"""The response record: one model response to one item, as the identification engine reads it.

A runner/scorer (`reasoning_heuristics.evals`, built separately) emits these as JSON lines.
The record is deliberately small; every field is documented here and nowhere else.

| Field | Meaning |
|---|---|
| `item_id` | The item answered. Unique within an item set. |
| `content_hash` | The item's `content_hash` at run time. The join checks it, so a response is never scored against an item whose logical content changed under the same id. |
| `presentation_hash` | Optional: the item's `presentation_hash` (the exact prompt). Checked when given. |
| `model` | Provider model id (e.g. `openai/gpt-oss-20b`). |
| `condition` | The run condition, an opaque fit key alongside model and eval: the run manifest's condition label (`thinking-high`, `thinking-low`, `direct`, ...). |
| `category` | `ok`, `parse_fail`, `refusal`, `declared_impossible`, `partial` or `truncated` (DESIGN §5 rule 5). |
| `answer` | The parsed answer, in the representation the item's members use: a colouring `{vertex: colour}`, an assignment `{var: bool}`, a list of item names or of literal strings, or a token (`"UNSAT"`, `"IMPOSSIBLE"`, `"YES"`, `"NO"`, `"X"`, `"NOTHING"`, an option letter, a colour number). `None` unless the category carries an answer (`ok`; `truncated` with a forced answer; `partial`). |
| `answer_key` | Optional canonical key of `answer` (`heuristics.answers.answer_key`). The engine recomputes it from `answer` on the item's scoring channel and checks it when both are given. |
| `reasoning_tokens` | Reasoning tokens the API reported (`None` if not reported). |
| `pre_answer_tokens` | Optional: visible output tokens before the answer (direct condition: flags responses that reason in the visible output). |
| `sample` | Repeat index for repeated samples of one (item, model, condition), from 0. |

**From the scorer.** `from_scored(path)` reads the scorer's `scored.jsonl.gz` records
(`evals.scoring`, docs/RUNNER.md) into Responses; it is the only code that knows that schema.

**Joining responses to items.** `content_hash` alone is *not* a unique item key: it is
invariant to presentation by design, and several evals present the same content in several
cells (C E1 copies that differ only in the requested answer order, B4/C4 YN vs MC formats,
C E3 listing arms, A/H E5 framings). Two such items have different member predictions, so
responses are joined on `item_id` and the join asserts that `content_hash` (and
`presentation_hash`, when given) match the item. `join()` raises on any mismatch or unknown item.
"""

from __future__ import annotations

import gzip
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

CATEGORIES = ("ok", "parse_fail", "refusal", "declared_impossible", "partial", "truncated")


@dataclass(frozen=True)
class Response:
    item_id: str
    content_hash: str
    model: str
    category: str
    answer: Any = None
    answer_key: str | None = None
    reasoning_tokens: int | None = None
    condition: str = "thinking"
    presentation_hash: str | None = None
    pre_answer_tokens: int | None = None
    sample: int = 0
    extra: dict[str, Any] = field(default_factory=dict, compare=False, hash=False)

    def __post_init__(self) -> None:
        if self.category not in CATEGORIES:
            raise ValueError(f"unknown response category {self.category!r}; expected one of {CATEGORIES}")
        if not self.condition:
            raise ValueError("condition must be a non-empty string")
        if self.category in ("parse_fail", "refusal") and self.answer is not None:
            raise ValueError(f"a {self.category} response carries no answer (item {self.item_id})")

    def to_json(self) -> dict[str, Any]:
        out = asdict(self)
        if not out["extra"]:
            out.pop("extra")
        return out

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Response":
        known = {f for f in cls.__dataclass_fields__}
        unknown = set(data) - known
        if unknown:
            raise ValueError(f"unknown response fields {sorted(unknown)}")
        return cls(**data)


def read_responses(path: str | Path) -> list[Response]:
    p = Path(path)
    opener = gzip.open if p.suffix == ".gz" else open
    with opener(p, "rt", encoding="utf-8") as f:
        return [Response.from_json(json.loads(line)) for line in f if line.strip()]


def write_responses(responses: Iterable[Response], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if p.suffix == ".gz" else open
    with opener(p, "wt", encoding="utf-8") as f:
        for r in responses:
            f.write(json.dumps(r.to_json(), ensure_ascii=False, sort_keys=True) + "\n")


# scorer fields kept in Response.extra (docs/RUNNER.md, "The scored record")
SCORED_EXTRA = ("run_id", "model", "provider", "cell", "channel", "parse_status", "parse_detail", "flags", "channel_value",
                "outcome_class", "members_matched", "answer_key_matches", "correct", "valid", "optimal", "witness",
                "finish_reason", "truncated", "completion_tokens", "prompt_tokens", "cost_usd", "reasoning_returned",
                "from_cache", "scorer_version", "scorer_git_sha", "scorer_git_dirty")


def from_scored(source: str | Path | Iterable[dict[str, Any]]) -> tuple[list[Response], dict[str, int]]:
    """Responses from the scorer's records (`evals.scoring.score_response`; `scored.jsonl.gz`).

    This is the one place that knows the scorer's schema: `parsed` becomes `answer` (it is null
    outside `ok`; the parser's view of truncated or partial answers stays in `parse_status`, kept in
    `extra`), `model_requested` (else the served `model`) is the model, `condition` is used as-is
    (an opaque fit key such as `thinking-high`, `thinking-low`, `direct`), and `api_error` rows (calls
    that never returned) are dropped and counted. Returns (responses, dropped counts by category)."""
    if isinstance(source, (str, Path)):
        p = Path(source)
        opener = gzip.open if p.suffix == ".gz" else open
        with opener(p, "rt", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]
    else:
        records = list(source)
    out: list[Response] = []
    dropped: dict[str, int] = {}
    for rec in records:
        cat = rec["category"]
        if cat == "api_error":
            dropped["api_error"] = dropped.get("api_error", 0) + 1
            continue
        out.append(Response(
            item_id=rec["item_id"], content_hash=rec["content_hash"],
            model=rec.get("model_requested") or rec["model"], category=cat,
            answer=rec.get("parsed") if cat == "ok" else None,
            answer_key=rec.get("answer_key") if cat == "ok" else None,
            reasoning_tokens=rec.get("reasoning_tokens"), condition=rec["condition"],
            presentation_hash=rec.get("presentation_hash"), pre_answer_tokens=rec.get("pre_answer_tokens"),
            sample=rec.get("sample", 0), extra={k: rec[k] for k in SCORED_EXTRA if k in rec}))
    return out, dropped


def join(responses: Iterable[Response], items: Iterable[dict[str, Any]]) -> list[tuple[Response, dict[str, Any]]]:
    """Pair every response with its item (by item_id), checking the hashes. Raises on any mismatch."""
    by_id: dict[str, dict[str, Any]] = {}
    for it in items:
        if it["item_id"] in by_id:
            raise ValueError(f"duplicate item_id {it['item_id']} in the item sets")
        by_id[it["item_id"]] = it
    out = []
    for r in responses:
        it = by_id.get(r.item_id)
        if it is None:
            raise KeyError(f"response for unknown item {r.item_id}")
        if it["content_hash"] != r.content_hash:
            raise ValueError(f"content_hash mismatch for {r.item_id}: response {r.content_hash}, item {it['content_hash']}")
        if r.presentation_hash is not None and it["presentation_hash"] != r.presentation_hash:
            raise ValueError(f"presentation_hash mismatch for {r.item_id}")
        out.append((r, it))
    return out


def fit_key(r: Response, item: dict[str, Any]) -> tuple[str, str, str, str]:
    """(model, condition, eval, domain): one mixture fit per key."""
    from reasoning_heuristics.identify.units import eval_name

    return (r.model, r.condition, eval_name(item), item["domain"])
