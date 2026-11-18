"""Forced final answers: a thinking model's reasoning trace is replayed with the thinking closed, through
OpenRouter's raw text-completions endpoint, so that the model's next tokens are its final answer.

    python -m reasoning_heuristics.evals.force data/runs/<source_run_id> --cap-usd X [--template force-2|force-1]
        [--select cut|done|all] [--truncate-at K | --truncate-frac F] [--per-unit N] [--samples S] [--limit N]
        [--max-tokens 4096] [--dry-run] [--concurrency 4] [--budget-tag T --budget-usd B] [--ledger path]
        [--cache-dir ...] [--no-cache] [--allow-item-drift | --items-at-run-sha]

What it selects (--select), from the source run's raw records, in the source's order:
    cut   responses that stopped for length (finish_reason "length") with a non-empty reasoning trace
          (`choices[0].message.reasoning`): one more chance to answer at the cap. Those that stopped there
          without a trace (the direct condition's) are counted and skipped.
    done  responses that finished (finish_reason "stop") with a non-empty trace and non-empty content. The
          whole trace is replayed and the answer forced, which should give the model's own answer: the
          f = 1 acceptance test. Each scored record carries the source response's own scoring.
    all   both: every response with a trace that finished with content or stopped for length, for sweeps over
          all items. Records from finished responses carry the source response's own scoring, as under done.
--per-unit N keeps at most N records per unit (vertical, eval, item domain), --limit N the first N, and
--samples S sends S calls per record (sample indices 0..S-1: distinct cache keys and records).

Budget forcing and early answering (force-2 only; docs/RUNNER.md, "Budget forcing and early answering"):
    --truncate-at K    cut each selected trace to its first K tokens, by the model's own tokenizer
                       (evals/tokenizer.py), and force the answer there. A trace of at most K tokens is not sent: it
                       is counted within_budget, and its natural answer stands.
    --truncate-frac F  cut each trace to its first floor(F x n) of its n tokens, 0 <= F < 1 (F = 0: an empty trace).
Either takes a comma-separated list for a dry run, which then prints its estimate per value; a live pass takes one.
The cut trace is a prefix of a run without a budget: the model did not know the budget.

The prompt is the model's own chat template, written here: the source request's system message (if any)
and last user message, verbatim, then the trace as the model's thinking, then the thinking closed. gpt-oss
(harmony) gets its analysis message ended and a final-channel message opened. Qwen3 gets the stop sentence
of the Qwen3 technical report's thinking-budget mechanism before `</think>`. Any other model is refused.

Templates (--template):
    force-2  (default) that prompt, sent to the model's forcing route (FORCING_ROUTES: an endpoint that
             passes a raw prompt through untouched, which need not be the source run's pin). For gpt-oss,
             logit_bias bans the tokens that would leave the final channel. Before its first call, a live
             pass checks that the route passes a raw prompt through (`raw_check`) and refuses if not.
    force-1  the first version, kept to reproduce and re-score its passes: the source run's own pin, no
             logit_bias, --select cut only. Its gpt-oss passes are invalid: DekaLLM, gpt-oss's pin, wraps
             a raw prompt as a chat user message, so the model reasons afresh. Its live calls get the
             raw-prompt check too, so a gpt-oss force-1 pass that has calls to send is refused.
Why, and what the 2026-11-18 probes found: docs/RUNNER.md, "Forced final answers at the cap".

Outputs, beside the source run, where the analysis's run patterns do not look: force-2 writes
data/runs/forced-2/<select>/<source_run_id>/ (run id forced-2/<select>/<source_run_id>), or with a budget
data/runs/forced-2/<select>-k<K>/ or <select>-f<F>/ (e.g. all-k4096, done-f0.25), force-1
data/runs/forced/<source_run_id>/ (run id forced/<source_run_id>):
    manifest.json      the source run (id, routing, raw-file SHA-256), template, select, max_tokens,
                       endpoint, logit_bias, the budget and the tokenizer, the forced calls' routing and price,
                       the raw-prompt check, cap, git SHA, versions, spend, counts
    raw.jsonl.gz       one record per forced call, as run.py writes them (`request` holds the whole
                       prompt), plus source_run_id, source_cache_key and forced_template. force-2 adds
                       forced_select, forced_sample and source_sample; for a finished source response (done,
                       all) also natural_response (the source response without its reasoning, which the
                       prompt holds) and natural_max_tokens; with a budget trace_tokens, cut_tokens,
                       budget_k or budget_frac, and provider_reasoning_tokens
    scored.jsonl.gz    the standard scorer's records plus forced, forced_template and source_run_id
                       (force-2: forced_select, forced_sample, source_sample; from a finished source response:
                       natural_category, natural_correct, natural_answer_key, same_as_natural; with a budget,
                       its fields as in raw.jsonl.gz)
    budget.jsonl.gz    with a budget: one record per selected trace and what the budget did with it
                       (within_budget, sent, no_room), its token counts, and the source's finish_reason
    REPORT.md          report.py's summary, with the forced pass's counts
`python -m reasoning_heuristics.evals.score <output dir>` re-scores a pass, with the item flags the pass
used (`items` in its manifest; `--items-ref <source SHA>` for --items-at-run-sha). The source run's files
are never modified: its truncated records stay truncated (censored, SCOPE §6 rule 2), and the forced
answers are a stratum of their own. Re-running resumes like run.py: only the missing calls are sent, and
the response cache never pays twice.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import Counter
from dataclasses import dataclass
from decimal import ROUND_FLOOR, Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable

from reasoning_heuristics.evals import cost as C
from reasoning_heuristics.evals import ledger
from reasoning_heuristics.evals import tokenizer as T
from reasoning_heuristics.evals.cache import ResponseCache, cache_key
from reasoning_heuristics.evals.client import API_BASE, KEY_ENV, CallResult, FatalAPIError, OpenRouterClient, usable
from reasoning_heuristics.evals.manifest import REPO, git_info, sha256_file, utc_now, versions, write_json
from reasoning_heuristics.evals.models import ModelConfig, Pricing, get_model, pin
from reasoning_heuristics.evals.report import forced_outcomes
from reasoning_heuristics.evals.run import PARTIAL, RAW, Runner, read_raw, write_raw
from reasoning_heuristics.evals.score import SCORED, load_run_items, read_jsonl_gz, score_run, write_jsonl_gz
from reasoning_heuristics.evals.scoring import ResponseView, served_provider

TEMPLATES = ("force-2", "force-1")
SELECTS = ("cut", "done", "all")
BUDGET = "budget.jsonl.gz"  # a budget pass: one record per selected trace
ENDPOINT = f"{API_BASE}/completions"
FORCED_DIRS = {"force-1": "forced", "force-2": "forced-2"}  # data/runs/forced/<source>, data/runs/forced-2/<select>/<source>
GPT_OSS_SYSTEM = ("You are ChatGPT, a large language model trained by OpenAI.\nKnowledge cutoff: 2024-06\n\n"
                  "Reasoning: {effort}\n\n# Valid channels: analysis, commentary, final. Channel must be included for every message.")
QWEN3_STOP = "Considering the limited time by the user, I have to give the solution based on the thinking directly now."
SUPPORTED = ("openai/gpt-oss-", "qwen/qwen3-")
ITEM_FIELDS = ("item_id", "content_hash", "presentation_hash", "vertical", "eval_id")
# force-2, gpt-oss: <|channel|>, <|start|> and <|end|> in tiktoken's o200k_harmony, the tokens that would leave the
# final channel. <|return|> (200002), which ends the answer, stays allowed.
GPT_OSS_LOGIT_BIAS = {"200005": -100, "200006": -100, "200007": -100}


class UnsupportedModel(ValueError):
    """A model with no force-1 template."""


@dataclass(frozen=True)
class ForcingRoute:
    """Where a model's forced calls go, and their price. The endpoint must pass a raw prompt through untouched,
    which the source run's pin need not do: DekaLLM, gpt-oss's, wraps it as a chat user message."""

    provider: dict[str, Any]
    price: Pricing
    context_length: int | None
    notes: str = ""


DEEPINFRA_BF16 = "DeepInfra bf16 endpoint listing (OpenRouter, 2026-11-17: data/runs/probes/2026-11-17)"
GPT_OSS_ROUTE_NOTES = ("DeepInfra bf16 passes raw prompts through (93 prompt tokens raw, 147 as a chat message; "
                       "data/runs/probes/2026-11-18-forced-answer, batch 11) and supports logit_bias, not logprobs. "
                       "It serves the released weights upcast to bf16, as DekaLLM bf16 (the source pin) does.")


def _source_pin(slug: str) -> ForcingRoute:
    cfg = get_model(slug)
    return ForcingRoute(dict(cfg.provider), cfg.pinned_price, cfg.context_length,
                        "the source pin, DeepInfra fp8 flex, which passes raw prompts through (42 prompt tokens raw, "
                        "51 as a chat message; data/runs/probes/2026-11-18-forced-answer, batch 11)")


FORCING_ROUTES: dict[str, ForcingRoute] = {
    "openai/gpt-oss-20b": ForcingRoute(pin("deepinfra/bf16", "bf16"), Pricing(0.03, 0.14, DEEPINFRA_BF16), 131072,
                                       GPT_OSS_ROUTE_NOTES),
    "openai/gpt-oss-120b": ForcingRoute(pin("deepinfra/bf16", "bf16"), Pricing(0.037, 0.17, DEEPINFRA_BF16), 131072,
                                        GPT_OSS_ROUTE_NOTES),
    "qwen/qwen3-32b": _source_pin("qwen/qwen3-32b"),
    "qwen/qwen3-14b": _source_pin("qwen/qwen3-14b"),
}


def forcing_route(cfg: ModelConfig, template: str) -> ForcingRoute:
    """force-2: the model's forcing route. force-1: the source run's pin, where its calls always went."""
    if template == "force-1":
        return ForcingRoute(dict(cfg.provider), cfg.pinned_price, cfg.context_length, "force-1: the source run's pin")
    if cfg.slug not in FORCING_ROUTES:
        raise SystemExit(f"{cfg.slug}: no forcing route. Probe a provider that passes a raw prompt through "
                         "(docs/RUNNER.md, 'Forced final answers at the cap') and add it to FORCING_ROUTES")
    return FORCING_ROUTES[cfg.slug]


def logit_bias_for(template: str, model: str) -> dict[str, int] | None:
    """force-2 bans gpt-oss's tokens that would leave the final channel; Qwen3 gets none, force-1 none."""
    return dict(GPT_OSS_LOGIT_BIAS) if template == "force-2" and model.startswith("openai/gpt-oss-") else None


def check_supported(model: str) -> None:
    if not model.startswith(SUPPORTED):
        raise UnsupportedModel(f"{model}: no force-1 template (gpt-oss and Qwen3 only); its chat template "
                               "would have to be written here and probed first")


def forced_prompt(request: dict[str, Any], trace: str) -> str:
    """The force-1 prompt, which force-2 sends too: the source chat request in the model's own chat template,
    then `trace` (the source response's reasoning) as its thinking, closed, so that the next tokens are the
    final answer."""
    model = request["model"]
    check_supported(model)
    roles = [m["role"] for m in request["messages"]]
    if roles not in (["user"], ["system", "user"]):
        raise ValueError(f"force-1 replays one user message, after at most one system message; got {roles}")
    system = request["messages"][0]["content"] if roles[0] == "system" else None
    user = request["messages"][-1]["content"]
    if model.startswith("openai/gpt-oss-"):
        effort = (request.get("reasoning") or {}).get("effort")
        if not effort:
            raise ValueError(f"{model}: the source request names no reasoning effort for the harmony system message")
        developer = "" if system is None else f"<|start|>developer<|message|># Instructions\n\n{system}<|end|>"
        return (f"<|start|>system<|message|>{GPT_OSS_SYSTEM.format(effort=effort)}<|end|>{developer}"
                f"<|start|>user<|message|>{user}<|end|>"
                f"<|start|>assistant<|channel|>analysis<|message|>{trace.rstrip()}<|end|>"
                "<|start|>assistant<|channel|>final<|message|>")
    system_turn = "" if system is None else f"<|im_start|>system\n{system}<|im_end|>\n"
    return (f"{system_turn}<|im_start|>user\n{user}<|im_end|>\n"
            f"<|im_start|>assistant\n<think>\n{trace.rstrip()}\n\n{QWEN3_STOP}\n</think>\n\n")


def forced_body(request: dict[str, Any], trace: str, max_tokens: int, provider: dict[str, Any] | None = None,
                logit_bias: dict[str, int] | None = None) -> dict[str, Any]:
    """The /completions body: the source request's model and sampling, the force-1 prompt, `provider` (by default
    the source request's routing, where force-1 sends) and, for force-2's gpt-oss, `logit_bias`."""
    body = {"model": request["model"], "provider": request["provider"] if provider is None else provider,
            "prompt": forced_prompt(request, trace), "max_tokens": max_tokens,
            "temperature": request["temperature"], "top_p": request["top_p"]}
    if "top_k" in request:
        body["top_k"] = request["top_k"]
    if logit_bias:
        body["logit_bias"] = logit_bias
    return body


def _choice(rec: dict[str, Any]) -> dict[str, Any]:
    return ((rec.get("response") or {}).get("choices") or [{}])[0]


def trace_of(rec: dict[str, Any]) -> str:
    """The source response's reasoning trace ("" if none)."""
    return (_choice(rec).get("message") or {}).get("reasoning") or ""


def finished(rec: dict[str, Any]) -> bool:
    """Whether the source response finished by itself (finish_reason "stop") rather than at the cap."""
    return _choice(rec).get("finish_reason") == "stop"


def select(raw: list[dict[str, Any]], which: str = "cut") -> tuple[list[dict[str, Any]], dict[str, int]]:
    """The source records to force, in order, and how many that stopped the right way were skipped, by reason.
    cut: finish_reason "length" with a reasoning trace (else no_trace). done: finish_reason "stop" with a trace
    (else no_trace) and an answer (else no_content). all: either."""
    finishes = {"cut": ("length",), "done": ("stop",), "all": ("length", "stop")}[which]
    picked: list[dict[str, Any]] = []
    skipped = {"no_trace": 0} if which == "cut" else {"no_trace": 0, "no_content": 0}
    for r in raw:
        if _choice(r).get("finish_reason") not in finishes:
            continue
        if not trace_of(r).strip():
            skipped["no_trace"] += 1
        elif finished(r) and not (ResponseView.from_api(r["response"]).content or "").strip():
            skipped["no_content"] += 1
        else:
            picked.append(r)
    return picked, skipped


def unit_of(item: dict[str, Any]) -> tuple[str, str, str]:
    return item["vertical"], item["eval_id"], item["domain"]


def per_unit(picked: list[dict[str, Any]], items: dict[str, dict[str, Any]], n: int) -> list[dict[str, Any]]:
    """At most `n` records per unit (vertical, eval, item domain), in order: a stratified sample."""
    seen: Counter = Counter()
    out = []
    for r in picked:
        u = unit_of(items[r["item_id"]])
        if seen[u] < n:
            seen[u] += 1
            out.append(r)
    return out


def without_reasoning(response: dict[str, Any]) -> dict[str, Any]:
    """A copy of a chat response without its reasoning text (`reasoning`, `reasoning_details`). The forced prompt
    holds the trace, and the scorer reads a finished response's answer from its content."""
    out = json.loads(json.dumps(response))
    for ch in out.get("choices") or []:
        for k in ("reasoning", "reasoning_details"):
            (ch.get("message") or {}).pop(k, None)
    return out


def prompt_tokens_estimate(rec: dict[str, Any], cut_tokens: int | None = None) -> int:
    """A forced prompt's size: the source's prompt plus the trace it replays. A whole trace counts as all the source
    generated (for a finished response that includes its answer, which the prompt leaves out); in the 2026-11-18
    probes the API reported 1.0007-1.0033 times this for cut traces, and the cost guard's safety factor (1.25) covers
    the difference. A trace cut by a budget counts as its `cut_tokens`, by the model's tokenizer."""
    usage = rec["response"]["usage"]
    return usage["prompt_tokens"] + (usage["completion_tokens"] if cut_tokens is None else cut_tokens)


CONTEXT_MARGIN = 1.01  # on the estimate: the probes' forced prompts came to 1.0007-1.0033 times it
TEMPLATE_TOKENS = 64  # the template's own tokens, generously
MIN_ANSWER_TOKENS = 256  # below this a call is skipped (and counted) rather than sent


def call_max_tokens(rec: dict[str, Any], max_tokens: int, context_length: int | None, cut_tokens: int | None = None) -> int:
    """One forced call's max_tokens: the pass's, lowered so that prompt plus answer fits the forcing endpoint's
    context. DeepInfra serves Qwen3 with a 40,960-token context, which a 32,768-token trace, a long item and
    4,096 answer tokens can overflow: an HTTP 400, which stops the pass (2026-11-18, one dev item per Qwen3 run).
    The prompt is the estimate above: with a budget, the source's prompt plus the cut trace, not the whole one."""
    if not context_length:
        return max_tokens
    return min(max_tokens, context_length - math.ceil(CONTEXT_MARGIN * prompt_tokens_estimate(rec, cut_tokens))
               - TEMPLATE_TOKENS)


# --- budget forcing and early answering ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Budget:
    """A cut of each selected trace: its first `k` tokens (--truncate-at), or the first floor(frac x n) of its n tokens
    (--truncate-frac, 0 <= frac < 1), by the model's own tokenizer."""

    k: int | None = None
    frac: Decimal | None = None

    @property
    def label(self) -> str:
        """The output directory's suffix: k4096, f0.25, f0."""
        return f"k{self.k}" if self.k is not None else f"f{format(self.frac.normalize(), 'f')}"

    def keep(self, n: int) -> int | None:
        """How many of a trace's `n` tokens to keep, or None when it is within budget (at most k tokens) and is not
        sent. A fraction below 1 always cuts."""
        if self.k is not None:
            return None if n <= self.k else self.k
        return int((self.frac * n).to_integral_value(rounding=ROUND_FLOOR))

    def to_json(self) -> dict[str, Any]:
        return {"truncate_at": self.k} if self.k is not None else {"truncate_frac": float(self.frac)}

    def fields(self) -> dict[str, Any]:
        """The record field that names the budget."""
        return {"budget_k": self.k} if self.k is not None else {"budget_frac": float(self.frac)}


@dataclass(frozen=True)
class TraceCut:
    """What a budget does with one selected trace."""

    trace_tokens: int  # the whole trace, by the model's tokenizer
    cut_tokens: int | None  # None: within budget, so nothing is sent
    text: str | None = None  # the cut trace, kept for a live pass


def provider_reasoning_tokens(rec: dict[str, Any]) -> int | None:
    """The source usage's reasoning_tokens: the provider's count of the trace."""
    return ((rec["response"].get("usage") or {}).get("completion_tokens_details") or {}).get("reasoning_tokens")


def trace_token_counts(picked: list[dict[str, Any]], cuts: list[TraceCut]) -> dict[str, Any]:
    """The selected traces' tokens by the model's tokenizer, beside the provider's own counts: reasoning_tokens, where
    the source usage reports them, and completion_tokens, where the source response has no answer text, so that all
    it generated is the trace. The second is the better check of the tokenizer: DeepInfra's reasoning_tokens for
    Qwen3 are 0.30-1.14 of its completion tokens (dev, 2026-11-18), far from the trace's length."""
    def pair(rows: list[tuple[int, int]]) -> dict[str, Any]:
        ours, theirs = sum(t for t, _ in rows), sum(p for _, p in rows)
        return {"traces": len(rows), "trace_tokens": ours, "provider_tokens": theirs,
                "ratio": round(ours / theirs, 4) if theirs else None}

    reported = [(c.trace_tokens, provider_reasoning_tokens(r)) for r, c in zip(picked, cuts)]
    no_answer = [(c.trace_tokens, r["response"]["usage"]["completion_tokens"]) for r, c in zip(picked, cuts)
                 if not (ResponseView.from_api(r["response"]).content or "").strip()]
    return {"traces": len(cuts), "trace_tokens": sum(c.trace_tokens for c in cuts),
            "vs_reasoning_tokens": pair([(t, p) for t, p in reported if isinstance(p, int)]),
            "vs_completion_tokens_without_answer": pair(no_answer)}


def cut_traces(picked: list[dict[str, Any]], tok: T.Tokenizer, budgets: list[Budget],
               keep_text: bool) -> list[list[TraceCut]]:
    """Per budget, each selected trace's cut, in order. Each trace is encoded once, and the cut is decoded back to
    text (tokenizer.prefix), which a live pass sends (`keep_text`)."""
    out: list[list[TraceCut]] = [[] for _ in budgets]
    for r in picked:
        ids = tok.encode(trace_of(r))
        for cuts, b in zip(out, budgets):
            keep = b.keep(len(ids))
            if keep is None:
                cuts.append(TraceCut(len(ids), None))
            else:
                text, kept = T.prefix(tok, ids, keep)
                cuts.append(TraceCut(len(ids), kept, text if keep_text else None))
    return out


def plan_calls(picked: list[dict[str, Any]], cuts: list[TraceCut] | None, max_tokens: int,
               context_length: int | None) -> tuple[list[tuple[dict[str, Any], TraceCut | None, int]], list[str]]:
    """The records to send, each with its cut (None without a budget) and its max_tokens, and the fate of every
    selected record, in order: "sent", "within_budget" (not sent; its natural answer stands) or "no_room" (under
    MIN_ANSWER_TOKENS left in the context; skipped)."""
    send, fates = [], []
    for i, r in enumerate(picked):
        c = cuts[i] if cuts is not None else None
        if c is not None and c.cut_tokens is None:
            fates.append("within_budget")
            continue
        m = call_max_tokens(r, max_tokens, context_length, c.cut_tokens if c else None)
        if m < MIN_ANSWER_TOKENS:
            fates.append("no_room")
            continue
        fates.append("sent")
        send.append((r, c, m))
    return send, fates


def budget_record(rec: dict[str, Any], cut: TraceCut, budget: Budget, fate: str) -> dict[str, Any]:
    """budget.jsonl.gz: one selected trace and what the budget did with it (`status`: plan_calls's fate)."""
    return {"item_id": rec["item_id"], "source_sample": rec.get("sample", 0), "source_cache_key": rec["cache_key"],
            "source_finish_reason": _choice(rec).get("finish_reason"), "status": fate,
            "trace_tokens": cut.trace_tokens, "cut_tokens": cut.cut_tokens,
            "provider_reasoning_tokens": provider_reasoning_tokens(rec), **budget.fields()}


def parse_budgets(text: str, frac: bool) -> list[Budget]:
    """--truncate-at K[,K...] (whole tokens, K >= 0) or --truncate-frac F[,F...] (0 <= F < 1)."""
    out = []
    for v in (s.strip() for s in text.split(",")):
        try:
            b = Budget(frac=Decimal(v) + 0) if frac else Budget(k=int(v))  # + 0: -0 is 0
        except (ValueError, InvalidOperation) as e:
            raise argparse.ArgumentTypeError(f"{v!r} is not a {'fraction' if frac else 'whole number of tokens'}") from e
        if (frac and not (b.frac.is_finite() and 0 <= b.frac < 1)) or (not frac and b.k < 0):
            raise argparse.ArgumentTypeError(f"{v!r}: --truncate-frac takes 0 <= F < 1" if frac else
                                             f"{v!r}: --truncate-at takes K >= 0")
        out.append(b)
    if len({b.label for b in out}) != len(out):
        raise argparse.ArgumentTypeError(f"{text!r} names a value twice")
    return out


# --- the raw-prompt check -----------------------------------------------------------------------------------------

RAW_CHECK_QUESTION = "Is 17 a prime number? Answer with one word, YES or NO."
RAW_CHECK_TRACE = "17 has no divisors other than 1 and itself."
RAW_CHECK_MAX_TOKENS = 8


def raw_check_prompt(model: str) -> str:
    """The check's text: a one-word question in the force-1 template, with a short closed thinking (gpt-oss: the
    final channel opened, exactly the prompt of the 2026-11-18 probes' batches 10 and 11; Qwen3: a closed
    `<think>` block, with the template's stop sentence)."""
    return forced_prompt({"model": model, "messages": [{"role": "user", "content": RAW_CHECK_QUESTION}],
                          "reasoning": {"effort": "low"}}, RAW_CHECK_TRACE)


def _booked_call(send: Callable[..., CallResult], body: dict[str, Any], guard: C.CostGuard) -> tuple[dict[str, Any] | None, str | None]:
    """One call outside the Runner, reserved and booked in `guard` as the Runner books its calls:
    (the response, None) or (None, the error)."""
    worst = guard.safety * guard.price.cost(len(json.dumps(body).encode("utf-8")) + 64, body["max_tokens"])
    if not guard.reserve(worst):
        return None, f"cap: its worst case ${worst:.6f} would take the spend past ${guard.cap:.4f}"
    try:
        res = send(body, on_failed_attempt=guard.book_failed_attempt)
    except FatalAPIError as e:
        guard.release(worst)
        if e.charged:
            guard.book_failed_attempt(e.charged)
        return None, str(e)
    if not res.ok:
        guard.release(worst)
        return None, res.error or "failed"
    try:
        guard.settle(worst, res.response.get("usage"))
    except C.PriceMismatch as e:
        return None, str(e)
    return res.response, None


def raw_check(client: OpenRouterClient, guard: C.CostGuard, model: str, provider: dict[str, Any]) -> dict[str, Any]:
    """Does `provider` pass a raw prompt through? The check's text is sent as a raw prompt (POST /completions)
    and as a chat user message (POST /chat/completions), max_tokens 8, temperature 0, each call booked in
    `guard`. The chat call adds the chat template, so a provider that passes the raw prompt through reports fewer
    prompt tokens for it. Equal counts mean it wrapped the raw prompt as a user message, as DekaLLM does for
    gpt-oss (160 = 160, 2026-11-18). `passed` only when the raw call's prompt_tokens are strictly below the chat
    call's."""
    text = raw_check_prompt(model)
    common = {"model": model, "provider": provider, "max_tokens": RAW_CHECK_MAX_TOKENS, "temperature": 0}
    out: dict[str, Any] = {"passed": False, "routing": provider, "prompt": text, "max_tokens": RAW_CHECK_MAX_TOKENS,
                           "temperature": 0, "checked_at": utc_now()}
    spent = guard.spent
    for name, send, body in (("completions", client.complete, {**common, "prompt": text}),
                             ("chat", client.chat, {**common, "messages": [{"role": "user", "content": text}]})):
        response, error = _booked_call(send, body, guard)
        if response is None:
            out[name] = {"error": error}
            break
        v = ResponseView.from_api(response)
        out[name] = {"provider": v.provider, "prompt_tokens": v.prompt_tokens, "completion_tokens": v.completion_tokens,
                     "text": v.content, "reasoning": v.reasoning, "finish_reason": v.finish_reason, "cost_usd": v.cost,
                     "generation_id": v.generation_id}
    out["cost_usd"] = round(guard.spent - spent, 8)
    raw_tokens, chat_tokens = ((out.get(k) or {}).get("prompt_tokens") for k in ("completions", "chat"))
    out["passed"] = isinstance(raw_tokens, int) and isinstance(chat_tokens, int) and raw_tokens < chat_tokens
    return out


def raw_check_refusal(check: dict[str, Any]) -> str:
    """The error that stops a pass whose raw-prompt check did not pass. It names the provider."""
    raw, chat = check.get("completions") or {}, check.get("chat") or {}
    served = sorted({str(c["provider"]) for c in (raw, chat) if c.get("provider")})
    where = f"{(check['routing'] or {}).get('order')}" + (f" (served by {', '.join(served)})" if served else "")
    tokens = f"{raw.get('prompt_tokens')} (raw prompt) and {chat.get('prompt_tokens')} (chat user message)"
    if "error" in raw or "error" in chat:
        detail = f"could not run the raw-prompt check on {where}: {raw.get('error') or chat.get('error')}"
    elif not (isinstance(raw.get("prompt_tokens"), int) and isinstance(chat.get("prompt_tokens"), int)):
        detail = f"raw-prompt check inconclusive on {where}: prompt_tokens {tokens}"
    else:
        detail = (f"raw-prompt check failed on {where}: the same text reported {raw['prompt_tokens']} prompt tokens as a raw "
                  f"prompt (POST /completions, text {raw.get('text')!r}) and {chat['prompt_tokens']} as a chat user message "
                  f"(POST /chat/completions, text {chat.get('text')!r}). The provider does not pass a raw prompt through "
                  "untouched (DekaLLM wraps it in the chat template), so the model would reason afresh instead of answering")
    return (f"{detail}. No forced call was sent. Force through an endpoint that passes raw prompts through "
            "(FORCING_ROUTES in evals/force.py; docs/RUNNER.md, 'Forced final answers at the cap').")


class ForcedRunner(Runner):
    """run.py's Runner for forced calls: each call reserves a worst case priced from its source response's
    usage (not from the prompt's bytes), and its raw record says where its prompt came from."""

    def worst_case(self, job: dict[str, Any]) -> float:
        return job["worst"]

    def _record(self, job: dict[str, Any], body: dict[str, Any], key: str, **kw: Any) -> dict[str, Any]:
        return {**super()._record(job, body, key, **kw), **job["provenance"]}


def _from_cache(cache: ResponseCache | None, key: str) -> bool:
    """Whether the Runner will answer this call from the cache (its own test), so that nothing is sent."""
    entry = cache.get(key) if cache is not None else None
    return entry is not None and usable(entry.get("response"))


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(prog="python -m reasoning_heuristics.evals.force", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="the source run directory, data/runs/<source_run_id>")
    ap.add_argument("--template", choices=TEMPLATES, default="force-2",
                    help="force-2 (default), or force-1 to reproduce its passes (the source's pin, --select cut only)")
    ap.add_argument("--select", choices=SELECTS, default="cut",
                    help="cut (default): responses stopped at the cap; done: finished ones, the whole trace replayed (the f = 1 "
                         "test); all: both, for sweeps over all items")
    budget = ap.add_mutually_exclusive_group()
    budget.add_argument("--truncate-at", metavar="K[,K...]", type=lambda s: parse_budgets(s, frac=False),
                        help="force-2: cut each selected trace to its first K tokens (the model's own tokenizer) and force the "
                             "answer there; a trace of at most K tokens is not sent (within_budget). A list: a dry run's "
                             "estimate per value")
    budget.add_argument("--truncate-frac", metavar="F[,F...]", type=lambda s: parse_budgets(s, frac=True),
                        help="force-2: cut each selected trace to the first floor(F x n) of its n tokens, 0 <= F < 1 (F = 0: "
                             "an empty trace), and force the answer there. A list: a dry run's estimate per value")
    ap.add_argument("--per-unit", type=int, help="at most N selected records per unit (vertical, eval, item domain), in source order")
    ap.add_argument("--samples", type=int, default=1, help="forced calls per selected record (sample indices 0..S-1, distinct cache keys)")
    ap.add_argument("--cap-usd", type=float, help="hard cap on API-reported spend for this invocation (required for a live pass)")
    ap.add_argument("--max-tokens", type=int, default=4096, help="max_tokens of each forced call (default 4096)")
    ap.add_argument("--dry-run", action="store_true", help="print the count and the cost estimate and exit; no API call (a budget "
                    "pass first loads the model's tokenizer, which tiktoken or evals/tokenizer.py downloads on first use)")
    ap.add_argument("--limit", type=int, help="only the first N selected records")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--cache-dir", default=str(REPO / "data" / "cache" / "openrouter"))
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--ledger", default=str(REPO / "data" / "runs" / "LEDGER.md"))
    ap.add_argument("--budget-tag", help="ledger tag whose running total counts against --budget-usd")
    ap.add_argument("--budget-usd", type=float, help="total budget for --budget-tag across runs and probes")
    ap.add_argument("--notes", default="", help="free text for the manifest and the ledger row")
    ap.add_argument("--allow-item-drift", action="store_true",
                    help="score against the current item files even if they changed since the source run (as its own scoring may have)")
    ap.add_argument("--items-at-run-sha", action="store_true",
                    help="score against the item files at the source run's git SHA (git show), checked against its manifest's sha256")
    a = ap.parse_args(argv)
    a.budgets = a.truncate_at or a.truncate_frac or []
    if a.template == "force-1" and (a.select != "cut" or a.per_unit is not None or a.samples != 1 or a.budgets):
        ap.error("force-1 is kept to reproduce its passes as they ran: --select cut, no --per-unit, --samples 1, "
                 "no --truncate-at or --truncate-frac")
    if a.samples < 1 or (a.per_unit is not None and a.per_unit < 1):
        ap.error("--samples and --per-unit take a positive number")
    if len(a.budgets) > 1 and not a.dry_run:
        ap.error("a live pass takes one --truncate-at or --truncate-frac value (a list is for a dry run's estimates)")
    return a


def budget_row(budget: Budget, picked: list[dict[str, Any]], cuts: list[TraceCut], max_tokens: int,
               context_length: int | None, price: Pricing, samples: int) -> dict[str, Any]:
    """One sweep value's count and cost estimate: prompt tokens are each sent record's source prompt plus its cut."""
    send, fates = plan_calls(picked, cuts, max_tokens, context_length)
    prompt = samples * sum(prompt_tokens_estimate(r, c.cut_tokens) for r, c, _ in send)
    return {"budget": budget.label, "traces": len(picked), "within_budget": fates.count("within_budget"),
            "sent": len(send), "no_room": fates.count("no_room"), "calls": samples * len(send), "prompt_tokens": prompt,
            "cost_usd": round(price.cost(prompt, 0), 4),
            "worst_case_usd": round(price.cost(prompt, samples * sum(m for _, _, m in send)), 4)}


def main(argv: list[str] | None = None, client: OpenRouterClient | None = None,
         tokenizer: T.Tokenizer | None = None) -> int:
    """`tokenizer` replaces the model's own (tests); a model with none in evals/tokenizer.py is refused all the same."""
    a = parse_args(argv)
    src = Path(a.source)
    src_manifest = json.loads((src / "manifest.json").read_text(encoding="utf-8"))
    if src_manifest.get("forced"):
        raise SystemExit(f"{src} is a forced pass itself; force its source run")
    if (src / PARTIAL).exists():
        raise SystemExit(f"{src} holds records not yet merged into {RAW} ({PARTIAL}); resume that run to the end first")
    source_id = src_manifest["run_id"]
    budget = a.budgets[0] if a.budgets else None  # a live pass has one; a dry run may list several
    rel = FORCED_DIRS[a.template] if a.template == "force-1" else (
        f"{FORCED_DIRS[a.template]}/{a.select}" + (f"-{budget.label}" if budget else ""))
    run_id, out = f"{rel}/{source_id}", src.parent / rel / source_id
    cfg = get_model(src_manifest["model_requested"])
    src_routing = src_manifest["provider_routing"]
    if cfg.pinned_price is None or not src_routing or src_routing != cfg.provider:
        raise SystemExit(f"{cfg.slug}: the source run was routed {src_routing}, not to the configured pin {cfg.provider}; "
                         "only traces from the pinned endpoint are forced")
    try:
        check_supported(cfg.slug)
    except UnsupportedModel as e:
        raise SystemExit(str(e)) from e
    route = forcing_route(cfg, a.template)
    bias = logit_bias_for(a.template, cfg.slug)
    price, samples = route.price, a.samples
    tok: T.Tokenizer | None = None
    if a.budgets:  # the model's own tokenizer, before anything is read or sent
        try:
            T.spec_for(cfg.slug)
            tok = tokenizer or T.for_model(cfg.slug)
        except T.UnknownTokenizer as e:
            raise SystemExit(str(e)) from e
        except ImportError as e:
            raise SystemExit(f"{e}: a budget pass needs the model's tokenizer library (pip install -e '.[force]')") from e
    items_ref = (src_manifest.get("git") or {}).get("sha") if a.items_at_run_sha else None
    if a.items_at_run_sha and not items_ref:
        raise SystemExit(f"{src}: the source manifest records no git SHA")
    items = load_run_items(src_manifest, a.allow_item_drift, items_ref)  # the scorer's items, checked before anything is spent
    source_sha = sha256_file(src / RAW)
    picked, skipped = select(read_jsonl_gz(src / RAW), a.select)
    candidates = len(picked)
    if a.per_unit:
        picked = per_unit(picked, items, a.per_unit)
    if a.limit:
        picked = picked[: a.limit]
    what = {"cut": "stopped at the cap with a reasoning trace", "done": "finished with a reasoning trace and an answer",
            "all": "finished with a reasoning trace and an answer, or stopped at the cap with one"}[a.select]
    left_out = {"cut": f"{skipped['no_trace']} stopped there without a trace",
                "done": f"{skipped['no_trace']} finished without a trace and {skipped.get('no_content', 0)} without an answer",
                "all": f"{skipped['no_trace']} without a trace and {skipped.get('no_content', 0)} finished without an answer"}[a.select]
    head = (f"Forced calls go to {route.provider['order']} ({route.provider}); the source run went to {src_routing['order']}."
            + (f" logit_bias {bias}." if bias else "") + "\n"
            f"{candidates} responses {what}. Skipped: {left_out}.\n"
            + (f"--per-unit {a.per_unit} keeps at most {a.per_unit} per unit (vertical, eval, item domain).\n" if a.per_unit else "")
            + (f"--limit {a.limit} keeps the first {a.limit}.\n" if a.limit else ""))
    check_note = (f"A live pass first checks that {route.provider['order']} passes a raw prompt through (two calls of "
                  f"max_tokens {RAW_CHECK_MAX_TOKENS}); a dry run makes no call.")
    cuts: list[TraceCut] | None = None
    tokens: dict[str, Any] | None = None
    if a.budgets:
        all_cuts = cut_traces(picked, tok, a.budgets, keep_text=not a.dry_run)
        rows = [budget_row(b, picked, c, a.max_tokens, route.context_length, price, samples) for b, c in zip(a.budgets, all_cuts)]
        info = tok.info()
        tokens = trace_token_counts(picked, all_cuts[0])
        vr, vc = tokens["vs_reasoning_tokens"], tokens["vs_completion_tokens_without_answer"]
        print(f"## Forced final answers: {source_id} ({cfg.slug}, template {a.template}, select {a.select}, max_tokens "
              f"{a.max_tokens}, budget forcing)\n\n" + head +
              f"Tokenizer: {info['name']} ({info['library']} {info['version']}; {info['file']}, sha256 {info['sha256'][:12]}). "
              f"The {tokens['traces']} traces hold {tokens['trace_tokens']:,} tokens by it. Against the provider's counts: "
              f"the {vr['traces']} whose source usage reports reasoning_tokens, {vr['trace_tokens']:,} by it and "
              f"{vr['provider_tokens']:,} reported ({vr['ratio']} x); the {vc['traces']} with no answer text, whose "
              f"completion_tokens are the trace alone, {vc['trace_tokens']:,} by it and {vc['provider_tokens']:,} reported "
              f"({vc['ratio']} x).\n"
              f"Each sent call's prompt: its source's prompt tokens plus the cut trace's tokens. A trace within budget is not "
              f"sent. A call left under {MIN_ANSWER_TOKENS} tokens of the endpoint's context ({route.context_length}) is "
              f"skipped (no room). Samples per record: {samples}.\n"
              f"Estimate at ${price.prompt}/M prompt, ${price.completion}/M completion ({price.source}): from the prompt alone "
              "(every call answers at once) to every call at max_tokens.\n\n"
              "| Budget | Traces | Within budget | Sent | No room | Calls | Prompt tokens | USD, answers at once | USD, all at max_tokens |\n"
              "|---|---|---|---|---|---|---|---|---|\n"
              + "".join(f"| {r['budget']} | {r['traces']} | {r['within_budget']} | {r['sent']} | {r['no_room']} | {r['calls']} | "
                        f"{r['prompt_tokens']:,} | {r['cost_usd']:.4f} | {r['worst_case_usd']:.4f} |\n" for r in rows)
              + "\n" + check_note)
        if a.dry_run:
            return 0
        cuts = all_cuts[0]
    send, fates = plan_calls(picked, cuts, a.max_tokens, route.context_length)
    no_room, within = fates.count("no_room"), fates.count("within_budget")
    selected = [r for r, f in zip(picked, fates) if f != "no_room"]
    limits = [m for _, _, m in send]
    bodies = [forced_body(r["request"], c.text if c else trace_of(r), m, route.provider, bias) for r, c, m in send]
    units = len({unit_of(items[r["item_id"]]) for r in selected})
    prompt_tokens = samples * sum(prompt_tokens_estimate(r, c.cut_tokens if c else None) for r, c, _ in send)
    lowered = sum(1 for m in limits if m < a.max_tokens)
    est = {"calls": len(send) * samples, "prompt_tokens": prompt_tokens, "cost_usd": round(price.cost(prompt_tokens, 0), 4),
           "worst_case_usd": round(price.cost(prompt_tokens, samples * sum(limits)), 4),
           "assumptions": "prompt tokens: each source response's prompt plus completion tokens; cost_usd is the prompt "
                          "alone (every call answers at once), worst_case_usd has every call at its max_tokens"}
    if budget:
        est.update({"within_budget": within, "assumptions": "prompt tokens: each sent record's source prompt tokens plus its "
                    "cut trace's tokens (by the model's tokenizer); cost_usd is the prompt alone (every call answers at "
                    "once), worst_case_usd has every call at its max_tokens"})
    else:
        print(f"## Forced final answers: {source_id} ({cfg.slug}, template {a.template}, select {a.select}, max_tokens {a.max_tokens})\n\n"
              + head + f"{lowered} records get a lower max_tokens to fit the endpoint's context ({route.context_length}); "
              f"{no_room} would have under {MIN_ANSWER_TOKENS} tokens and are skipped.\n"
              f"{len(send)} records from {units} units x {samples} sample{'s' if samples > 1 else ''} = {len(send) * samples} calls.\n"
              f"Prompt tokens over all calls (each call: its source response's prompt plus completion tokens): {prompt_tokens:,}.\n"
              f"Estimate at ${price.prompt}/M prompt, ${price.completion}/M completion ({price.source}): "
              f"${est['cost_usd']:.4f} if every call answers at once; ${est['worst_case_usd']:.4f} if every call runs to max_tokens.\n"
              + check_note)
        if a.dry_run:
            return 0
    if a.cap_usd is None:
        raise SystemExit("--cap-usd is required for a live pass")
    cap, spent_before = a.cap_usd, None
    if a.budget_tag:
        if a.budget_usd is None:
            raise SystemExit("--budget-tag needs --budget-usd")
        spent_before = ledger.spent(Path(a.ledger), a.budget_tag)
        cap = min(cap, a.budget_usd - spent_before)
        print(f"budget {a.budget_tag}: ${spent_before:.4f} of ${a.budget_usd:.2f} already booked; this pass's cap is ${cap:.4f}",
              file=sys.stderr)
    if client is None:
        if not os.environ.get(KEY_ENV):
            raise SystemExit(f"{KEY_ENV} is not set in the environment")
        client = OpenRouterClient()
    guard = C.CostGuard(cap, price, a.max_tokens)
    forced = {"template": a.template, "endpoint": ENDPOINT, "max_tokens": a.max_tokens}
    if a.template == "force-2":  # force-1 keeps its old keys, so that its passes still resume
        forced.update({"select": a.select, "logit_bias": bias})
        if budget:  # a pass without a budget keeps force-2's keys as they were, so that its passes still resume
            forced.update({"budget": budget.to_json(), "tokenizer": T.identity(tok.info())})
    manifest_path = out / "manifest.json"
    old = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None
    if old is not None and (old["forced"] != forced or old["source"]["raw_sha256"] != source_sha
                            or old.get("provider_routing") != route.provider):
        raise SystemExit(f"{out}: resuming with a different template, max_tokens, select, logit_bias, budget, tokenizer, "
                         "routing or source raw file than the pass was started with")
    done = {(r["item_id"], r.get("sample", 0)) for r in read_raw(out) if usable(r.get("response"))}
    per_source = src_manifest.get("samples_per_item") or 1
    jobs, want = [], set()
    for (r, c, _), body in zip(send, bodies):
        source_sample = r.get("sample", 0)
        for s in range(samples):
            sample = s * per_source + source_sample  # one sample: the source's own index, as force-1 had it
            want.add((r["item_id"], sample))
            if (r["item_id"], sample) in done:
                continue
            provenance = {"source_run_id": source_id, "source_cache_key": r["cache_key"], "forced_template": a.template}
            if a.template == "force-2":
                provenance.update({"forced_select": a.select, "forced_sample": s, "source_sample": source_sample})
                if finished(r):  # done, or all: the source response's own answer, to compare
                    provenance.update({"natural_response": without_reasoning(r["response"]),
                                       "natural_max_tokens": r["request"].get("max_tokens")})
                if c is not None:
                    provenance.update({"trace_tokens": c.trace_tokens, "cut_tokens": c.cut_tokens, **budget.fields(),
                                       "provider_reasoning_tokens": provider_reasoning_tokens(r)})
            jobs.append({"item": {k: r[k] for k in ITEM_FIELDS}, "sample": sample, "body": body, "key": cache_key(body, sample),
                         "worst": guard.safety * price.cost(prompt_tokens_estimate(r, c.cut_tokens if c else None),
                                                            body["max_tokens"]),
                         "provenance": provenance})
    cache = None if a.no_cache else ResponseCache(a.cache_dir)
    to_send = sum(1 for j in jobs if not _from_cache(cache, j["key"]))
    check: dict[str, Any] = {"passed": None, "skipped": "nothing left to send" if not jobs else
                             "no call to send: every forced call is answered from the response cache"}
    label = f"{src_manifest['condition']['label']}-forced" + (f"-{budget.label}" if budget else "")
    if to_send:  # before the first forced call: does the route pass a raw prompt through?
        check = raw_check(client, guard, cfg.slug, route.provider)
        if not check["passed"]:
            ledger.append(Path(a.ledger), date=utc_now()[:10], run_id=run_id, model=cfg.slug, condition=label, items=0,
                          cost_usd=check["cost_usd"], budget_tag=a.budget_tag or "-",
                          notes=(a.notes + " status=refused: raw-prompt check failed").strip())
            raise SystemExit(raw_check_refusal(check))
    out.mkdir(parents=True, exist_ok=True)
    if budget:
        write_jsonl_gz(out / BUDGET, [budget_record(r, c, budget, f) for r, c, f in zip(picked, cuts, fates)])
    src_cond = src_manifest["condition"]
    manifest: dict[str, Any] = {
        "run_id": run_id, "status": "running", "started_at": utc_now(), "model_requested": cfg.slug,
        "source": {"run_id": source_id, "raw_sha256": source_sha, "condition": src_cond["label"], "git": src_manifest.get("git"),
                   "provider_routing": src_routing},
        "forced": forced,
        "condition": {"name": "forced", "label": label, "effort": src_cond.get("effort"),
                      "max_tokens": a.max_tokens, "system_prompt": src_cond.get("system_prompt"), "reasoning": None,
                      "sampling": src_cond.get("sampling"), "template": a.template},
        "provider_routing": route.provider, "price": price.__dict__, "context_length": route.context_length,
        "routing_notes": route.notes, "model_notes": cfg.notes, "raw_check": check,
        **({"tokenizer": tok.info(), "tokens": tokens} if budget else {}),
        "items": {"files": src_manifest["items"]["files"], "n_items": len(selected),
                  "skipped": {**skipped, "no_room": no_room}, "per_unit": a.per_unit, "limit": a.limit,
                  "samples": samples, "allow_item_drift": a.allow_item_drift, "items_ref": items_ref},
        "estimate": est, "cap_usd": cap, "cap_requested_usd": a.cap_usd, "budget_tag": a.budget_tag,
        "budget_usd": a.budget_usd, "budget_spent_before_usd": spent_before, "git": git_info(), "versions": versions(),
        "client": {"timeout_s": client.timeout_s, "max_attempts": client.max_attempts, "concurrency": a.concurrency},
        "notes": a.notes, "resumed_from": len(done),
        "counts": {"candidates": candidates, "selected": len(selected), "units": units, "samples": samples,
                   **({"within_budget": within, "sent": len(send)} if budget else {}),
                   "calls": len(send) * samples, **{f"skipped_{k}": v for k, v in skipped.items()},
                   "skipped_no_room": no_room, "max_tokens_lowered": lowered, "responses": None, "answered": None,
                   "parsed": None, "still_reasoning": None, "renewed_reasoning": None,
                   **({"natural_ok": None, "same_as_natural": None} if a.select != "cut" else {})},
    }
    if old is not None:  # a resumed pass keeps every earlier invocation's provenance
        keep = ("started_at", "finished_at", "status", "stop_reason", "git", "versions", "cap_usd", "charged_usd", "spend",
                "responses", "failed_calls", "resumed_from", "providers_served", "models_returned", "wall_s", "client", "notes",
                "raw_check")
        manifest["previous_invocations"] = old.get("previous_invocations", []) + [{k: old.get(k) for k in keep}]
    write_json(manifest_path, manifest)
    runner = ForcedRunner(client, cache, guard, out, run_id, a.concurrency, send=client.complete)
    t0 = time.monotonic()
    try:
        runner.run(jobs)
    finally:
        recs = read_raw(out)
        write_raw(out, recs, {r["item_id"]: i for i, r in enumerate(picked)})
        responses = [r["response"] for r in recs if r.get("response")]
        have = {(r["item_id"], r.get("sample", 0)) for r in recs if r.get("response")}
        status = "complete" if runner.stop_reason is None and want <= have else (
            "stopped" if runner.stop_reason else "incomplete")
        charged = runner.charged + (check.get("cost_usd") or 0.0)  # the raw-prompt check is booked with the pass
        manifest.update({
            "status": status, "stop_reason": runner.stop_reason, "finished_at": utc_now(),
            "wall_s": round(time.monotonic() - t0, 1),
            "models_returned": sorted({str(r.get("model")) for r in responses}),
            "providers_served": dict(sorted(Counter(str(served_provider(r)) for r in responses).items())),
            "responses": len(responses), "failed_calls": runner.failures, "cache_hits": runner.cache_hits,
            "spend": guard.to_json(), "charged_usd": round(charged, 6),
            "charged_usd_all_invocations": round(charged + sum((p.get("charged_usd") or 0) for p in manifest.get("previous_invocations", [])), 6),
            "api_reported_cost_usd_all_responses": round(sum(float((r.get("usage") or {}).get("cost") or 0) for r in responses), 6),
        })
        manifest["counts"]["responses"] = len(responses)
        write_json(manifest_path, manifest)
        if guard.calls or runner.failures:
            ledger.append(Path(a.ledger), date=utc_now()[:10], run_id=run_id, model=cfg.slug, condition=label,
                          items=len(responses) - len(done), cost_usd=charged, budget_tag=a.budget_tag or "-",
                          notes=(a.notes + f" status={status}").strip())
    score_run(out, a.allow_item_drift, items_ref=items_ref)
    manifest["counts"].update(forced_outcomes(read_jsonl_gz(out / SCORED)))
    if a.select != "cut":  # 0, not None, when no forced answer came from a finished response (e.g. all within budget)
        manifest["counts"].update({k: manifest["counts"][k] or 0 for k in ("natural_ok", "same_as_natural")})
    write_json(manifest_path, manifest)
    c = manifest["counts"]
    natural = f", {c['same_as_natural']} of {c['natural_ok']} as the natural answer" if c.get("natural_ok") else ""
    kept = f"; {c['within_budget']} within budget, not sent" if budget else ""
    print(f"[{run_id}] {status}: {c['responses']} responses ({c['answered']} answered, {c['parsed']} parsed, "
          f"{c['still_reasoning']} still reasoning, {c['renewed_reasoning']} with renewed reasoning{natural}){kept}, "
          f"${charged:.4f} charged, {runner.cache_hits} from cache" + (f"; stopped: {runner.stop_reason}" if runner.stop_reason else ""))
    return 0 if status == "complete" else 2


if __name__ == "__main__":
    sys.exit(main())
