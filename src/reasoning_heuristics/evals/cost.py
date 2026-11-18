"""Cost estimates before a run (`--dry-run`) and the hard cap during it (`--cap-usd`).

Estimate = Σ over items of (prompt tokens × prompt price + assumed output tokens × completion
price), where

- prompt tokens come from the repo's tokenizer proxy (`tokens.py`, regex-digit-split-v1) over the
  system instruction and the prompt, plus `TEMPLATE_TOKENS` for the chat template;
- output tokens (reasoning + answer) per item are the per-eval assumptions below, taken from the
  vertical docs' dev-batch tables (SCOPE §2-3 are built from the same figures). Replace them with
  measured medians once a run exists (`report.py` prints them per eval);
- prices are the pinned endpoint's prices when the model has been probed, else SCOPE §1 list prices.

The cap: every request reserves its worst case (prompt bytes as a token upper bound, plus the
full `max_tokens` of output, times a safety factor) before it is sent, and settles to the
API-reported `usage.cost` when it returns. A request whose reservation would take the running
total past the cap is not sent, so the API-reported spend cannot pass the cap unless a provider
charges more than the configured price, which stops the run as an error.
"""

from __future__ import annotations

import gzip
import json
import statistics
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from reasoning_heuristics import tokens
from reasoning_heuristics.evals.models import Condition, Pricing

TEMPLATE_TOKENS = 12

# (vertical, eval, kind) -> (thinking output tokens, direct output tokens) per item
OUTPUT_TOKENS: dict[tuple[str, str, str], tuple[int, int]] = {
    # docs/verticals/A_H_baselines.md §7, dev-batch rows (BE); direct: our assumption (JSON answer size)
    ("A/H", "E1", "SAT"): (18000, 60), ("A/H", "E1", "COL"): (14000, 150), ("A/H", "E1", "ENT"): (7000, 10),
    ("A/H", "E2", "SAT"): (16000, 60), ("A/H", "E2", "COL"): (12000, 150), ("A/H", "E2", "ENT"): (7000, 10),
    ("A/H", "E5", "SAT"): (10000, 60), ("A/H", "E5", "COL"): (7000, 150), ("A/H", "E5", "ENT"): (7000, 40),
    ("A/H", "E5", "KNAP"): (6000, 30),
    # docs/verticals/C_constructive.md cost table (BE; ND = no thinking)
    ("C", "E1", "COL"): (7000, 100), ("C", "E1", "SAT"): (10000, 100),
    ("C", "E2", "COL"): (7000, 100), ("C", "E2", "SAT"): (11000, 100), ("C", "E2", "KNAP"): (6000, 70),
    ("C", "E3", "COL-U"): (14000, 450), ("C", "E3", "COL-I"): (6000, 8),
    ("C", "E5", "COL"): (10000, 150), ("C", "E5", "SAT"): (18000, 160), ("C", "E5", "STATE"): (7000, 100),
    ("C", "E5", "ENT"): (3000, 5),
    # docs/verticals/B4_C4_restrict_online.md cost table (BE; direct)
    ("B4/C4", "E1", "ENT"): (1800, 15), ("B4/C4", "E2", "ENT"): (1400, 10),
}
SOURCES = {
    "A/H": "docs/verticals/A_H_baselines.md §7 (dev-batch rows, BE); direct sizes assumed from the JSON answer",
    "C": "docs/verticals/C_constructive.md cost table (BE and ND)",
    "B4/C4": "docs/verticals/B4_C4_restrict_online.md cost table (BE and direct)",
}


def kind_of(item: dict[str, Any]) -> str:
    d = item["domain"].lower()
    if item["vertical"] == "C" and item["eval_id"] == "E3":
        return "COL-I" if "only the colour number" in item["answer_format"] else "COL-U"
    if "partial" in d:
        return "STATE"
    if "entail" in d or d == "ent":
        return "ENT"
    if "sat" in d:
        return "SAT"
    if "col" in d:
        return "COL"
    if "knap" in d:
        return "KNAP"
    raise KeyError(f"{item['item_id']}: no output-token assumption for domain {item['domain']!r}")


def assumed_output_tokens(item: dict[str, Any], cond: Condition, measured: dict[tuple[str, str, str], float] | None = None) -> int:
    key = (item["vertical"], item["eval_id"], kind_of(item))
    if measured and key in measured:
        return min(round(measured[key]), cond.max_tokens)
    think, direct = OUTPUT_TOKENS[key]
    return min(direct if cond.name == "direct" else think, cond.max_tokens)


def measured_output_tokens(scored_path: str | Path) -> dict[tuple[str, str, str], float]:
    """Mean API-reported completion tokens per (vertical, eval, kind) in a run's scored records
    (truncated responses count at the cap), to replace the assumptions once a run exists."""
    sums: dict[tuple[str, str, str], list[int]] = {}
    with gzip.open(scored_path, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["category"] == "api_error" or r.get("completion_tokens") is None:
                continue
            key = (r["vertical"], r["eval_id"], kind_of({"vertical": r["vertical"], "eval_id": r["eval_id"],
                                                         "domain": r["item_domain"], "answer_format": r["answer_format"],
                                                         "item_id": r["item_id"]}))
            sums.setdefault(key, []).append(r["completion_tokens"])
    return {k: sum(v) / len(v) for k, v in sums.items()}


def prompt_tokens_proxy(item: dict[str, Any], cond: Condition) -> int:
    return tokens.count(item["prompt"] + cond.prompt_suffix) + tokens.count(cond.system_prompt or "") + TEMPLATE_TOKENS


@dataclass
class EvalEstimate:
    vertical: str
    eval_id: str
    items: int
    prompt_tokens: int
    output_tokens: int
    cost_usd: float
    worst_case_usd: float

    def to_json(self) -> dict[str, Any]:
        return self.__dict__ | {"cost_usd": round(self.cost_usd, 4), "worst_case_usd": round(self.worst_case_usd, 4)}


def estimate(items: list[dict[str, Any]], cond: Condition, price: Pricing, samples: int = 1,
             measured: dict[tuple[str, str, str], float] | None = None, measured_source: str | None = None) -> dict[str, Any]:
    by: dict[tuple[str, str], EvalEstimate] = {}
    for it in items:
        key = (it["vertical"], it["eval_id"])
        row = by.setdefault(key, EvalEstimate(it["vertical"], it["eval_id"], 0, 0, 0, 0.0, 0.0))
        p, o = prompt_tokens_proxy(it, cond) * samples, assumed_output_tokens(it, cond, measured) * samples
        row.items += samples
        row.prompt_tokens += p
        row.output_tokens += o
        row.cost_usd += price.cost(p, o)
        row.worst_case_usd += price.cost(p, cond.max_tokens * samples)
    rows = [by[k] for k in sorted(by)]
    return {
        "condition": cond.to_json(), "price": price.__dict__, "samples_per_item": samples,
        "per_eval": [r.to_json() for r in rows],
        "items": sum(r.items for r in rows),
        "prompt_tokens": sum(r.prompt_tokens for r in rows),
        "output_tokens": sum(r.output_tokens for r in rows),
        "cost_usd": round(sum(r.cost_usd for r in rows), 4),
        "worst_case_usd": round(sum(r.worst_case_usd for r in rows), 4),
        "assumptions": {"prompt_tokens": f"tokens.py proxy ({tokens.PROXY_NAME}) + {TEMPLATE_TOKENS} template tokens",
                        "output_tokens": (f"measured means per eval and kind from {measured_source} (vertical-doc "
                                          f"assumptions where it has none)") if measured else SOURCES,
                        "price": price.source},
    }


def format_estimate(est: dict[str, Any], title: str) -> str:
    out_label = "measured" if str(est["assumptions"]["output_tokens"]).startswith("measured") else "assumed"
    lines = [f"## {title}", "",
             f"Condition {est['condition']['label']}, max_tokens {est['condition']['max_tokens']}; "
             f"price ${est['price']['prompt']}/M prompt, ${est['price']['completion']}/M completion ({est['price']['source']}).", "",
             f"| Vertical | Eval | Items | Prompt tokens (proxy) | Output tokens ({out_label}) | Estimate (USD) | Worst case, all at max_tokens (USD) |",
             "|---|---|---|---|---|---|---|"]
    for r in est["per_eval"]:
        lines.append(f"| {r['vertical']} | {r['eval_id']} | {r['items']} | {r['prompt_tokens']:,} | {r['output_tokens']:,} | "
                     f"{r['cost_usd']:.3f} | {r['worst_case_usd']:.3f} |")
    lines.append(f"| **Total** | | **{est['items']}** | **{est['prompt_tokens']:,}** | **{est['output_tokens']:,}** | "
                 f"**{est['cost_usd']:.2f}** | **{est['worst_case_usd']:.2f}** |")
    return "\n".join(lines)


class CapReached(RuntimeError):
    pass


class PriceMismatch(RuntimeError):
    """A call cost more than its reserved worst case: the configured prices are wrong. Stop."""


class CostGuard:
    """Thread-safe running total of API-reported cost with worst-case reservations."""

    def __init__(self, cap_usd: float, price: Pricing, max_tokens: int, safety: float = 1.25):
        if cap_usd <= 0:
            raise CapReached(f"cap ${cap_usd:.4f} leaves nothing to spend")
        self.cap = cap_usd
        self.price = price
        self.max_tokens = max_tokens
        self.safety = safety
        self.spent = 0.0
        self.reserved = 0.0
        self.calls = 0
        self.refused = 0
        self.estimated_costs = 0  # calls whose usage carried no cost (settled at the configured price)
        self.failed_attempt_cost = 0.0  # API-reported cost of attempts that failed (e.g. an error body after generation)
        self.failed_attempts_charged = 0
        self._lock = threading.Lock()

    def worst_case(self, body_text: str) -> float:
        upper_prompt_tokens = len(body_text.encode("utf-8")) + 64  # a token is at least one byte
        return self.safety * self.price.cost(upper_prompt_tokens, self.max_tokens)

    def reserve(self, amount: float) -> bool:
        with self._lock:
            if self.spent + self.reserved + amount > self.cap:
                self.refused += 1
                return False
            self.reserved += amount
            return True

    def settle(self, reserved: float, usage: dict[str, Any] | None) -> float:
        """Release a reservation and book the call's API-reported cost. Returns the cost booked."""
        usage = usage or {}
        cost = usage.get("cost")
        with self._lock:
            self.reserved -= reserved
            if cost is None:
                self.estimated_costs += 1
                cost = self.price.cost(usage.get("prompt_tokens") or 0, usage.get("completion_tokens") or 0)
            self.spent += float(cost)
            self.calls += 1
        if float(cost) > reserved + 1e-9:
            raise PriceMismatch(f"a call cost ${float(cost):.6f}, more than its reserved worst case ${reserved:.6f}; "
                                f"check the configured price {self.price}")
        return float(cost)

    def release(self, reserved: float) -> None:
        with self._lock:
            self.reserved -= reserved

    def book_failed_attempt(self, cost: float) -> bool:
        """Book the API-reported cost of a failed attempt; return whether the call may retry.

        The call still holds its reservation, which covers its next attempt, so a retry is allowed
        only while spend (now including this attempt) plus every reservation stays within the cap."""
        with self._lock:
            if cost:
                self.spent += float(cost)
                self.failed_attempt_cost += float(cost)
                self.failed_attempts_charged += 1
            return self.spent + self.reserved <= self.cap

    def to_json(self) -> dict[str, Any]:
        return {"cap_usd": self.cap, "spent_usd": round(self.spent, 6), "calls": self.calls,
                "refused_reservations": self.refused, "calls_without_reported_cost": self.estimated_costs,
                "failed_attempt_cost_usd": round(self.failed_attempt_cost, 6),
                "failed_attempts_charged": self.failed_attempts_charged,
                "safety_factor": self.safety, "price": self.price.__dict__}


def token_stats(values: list[int]) -> dict[str, Any]:
    vals = [v for v in values if v is not None]
    if not vals:
        return {"n": 0, "median": None, "mean": None, "max": None}
    return {"n": len(vals), "median": statistics.median(vals), "mean": round(statistics.fmean(vals), 1), "max": max(vals)}
