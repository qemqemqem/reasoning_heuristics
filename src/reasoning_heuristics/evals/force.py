"""Forced final answers at the cap: a thinking model that stopped at its token cap gets one more chance
to answer. Its truncated reasoning is replayed with the thinking closed, through OpenRouter's raw
text-completions endpoint, so the model's next tokens are its final answer.

    python -m reasoning_heuristics.evals.force data/runs/<source_run_id> --cap-usd X [--max-tokens 4096]
        [--dry-run] [--limit N] [--concurrency 4] [--budget-tag T --budget-usd B] [--ledger path]
        [--cache-dir ...] [--no-cache] [--allow-item-drift | --items-at-run-sha]

Selection: the source run's raw records whose response stopped for length (finish_reason "length")
with a non-empty reasoning trace (`choices[0].message.reasoning`), in the source's order. Those that
stopped there without a trace (the direct condition's) are counted and skipped.

The prompt (template "force-1") is the model's own chat template, written here: the source request's
system message (if any) and last user message, verbatim, then the trace as the model's thinking, then
the thinking closed. gpt-oss (harmony) gets its analysis message ended and a final-channel message
opened. Qwen3 gets the stop sentence of the Qwen3 technical report's thinking-budget mechanism before
`</think>`. Any other model is refused. Why the chat API cannot do this, and what the 2026-11-18 probes
found: docs/RUNNER.md, "Forced final answers at the cap".

Outputs in data/runs/forced/<source_run_id>/ (beside the source run), which the analysis's run
patterns do not match:
    manifest.json      source run id and raw-file SHA-256, template, max_tokens, endpoint, provider
                       routing, price, cap, git SHA, versions, spend, counts
    raw.jsonl.gz       one record per forced call, as run.py writes them (`request` holds the whole
                       prompt), plus source_run_id, source_cache_key and forced_template
    scored.jsonl.gz    the standard scorer's records plus forced, forced_template and source_run_id
    REPORT.md          report.py's summary, with the forced pass's counts
`python -m reasoning_heuristics.evals.score data/runs/forced/<source_run_id>` re-scores it, with the item
flags the pass used (`items` in its manifest; `--items-ref <source SHA>` for --items-at-run-sha). The source
run's files are never modified: its truncated records stay truncated (censored, SCOPE §6 rule 2), and
the forced answers are a stratum of their own. Re-running resumes like run.py: only the missing calls
are sent, and the response cache never pays twice.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

from reasoning_heuristics.evals import cost as C
from reasoning_heuristics.evals import ledger
from reasoning_heuristics.evals.cache import ResponseCache, cache_key
from reasoning_heuristics.evals.client import API_BASE, KEY_ENV, OpenRouterClient
from reasoning_heuristics.evals.manifest import REPO, git_info, sha256_file, utc_now, versions, write_json
from reasoning_heuristics.evals.models import get_model
from reasoning_heuristics.evals.report import forced_outcomes
from reasoning_heuristics.evals.run import PARTIAL, RAW, Runner, read_raw, write_raw
from reasoning_heuristics.evals.score import SCORED, load_run_items, read_jsonl_gz, score_run
from reasoning_heuristics.evals.scoring import served_provider

TEMPLATE = "force-1"
ENDPOINT = f"{API_BASE}/completions"
FORCED_DIR = "forced"  # data/runs/forced/<source_run_id>
GPT_OSS_SYSTEM = ("You are ChatGPT, a large language model trained by OpenAI.\nKnowledge cutoff: 2024-06\n\n"
                  "Reasoning: {effort}\n\n# Valid channels: analysis, commentary, final. Channel must be included for every message.")
QWEN3_STOP = "Considering the limited time by the user, I have to give the solution based on the thinking directly now."
SUPPORTED = ("openai/gpt-oss-", "qwen/qwen3-")
ITEM_FIELDS = ("item_id", "content_hash", "presentation_hash", "vertical", "eval_id")


class UnsupportedModel(ValueError):
    """A model with no force-1 template."""


def forced_prompt(request: dict[str, Any], trace: str) -> str:
    """Template force-1: the source chat request in the model's own chat template, then `trace` (the source
    response's reasoning) as its thinking, closed, so that the next tokens are the final answer."""
    model = request["model"]
    if not model.startswith(SUPPORTED):
        raise UnsupportedModel(f"{model}: no {TEMPLATE} template (gpt-oss and Qwen3 only); its chat template "
                               "would have to be written here and probed first")
    roles = [m["role"] for m in request["messages"]]
    if roles not in (["user"], ["system", "user"]):
        raise ValueError(f"{TEMPLATE} replays one user message, after at most one system message; got {roles}")
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


def forced_body(request: dict[str, Any], trace: str, max_tokens: int) -> dict[str, Any]:
    """The /completions body: the source request's model, provider routing and sampling, and the force-1 prompt."""
    body = {"model": request["model"], "provider": request["provider"], "prompt": forced_prompt(request, trace),
            "max_tokens": max_tokens, "temperature": request["temperature"], "top_p": request["top_p"]}
    if "top_k" in request:
        body["top_k"] = request["top_k"]
    return body


def _choice(rec: dict[str, Any]) -> dict[str, Any]:
    return ((rec.get("response") or {}).get("choices") or [{}])[0]


def trace_of(rec: dict[str, Any]) -> str:
    """The source response's reasoning trace ("" if none)."""
    return (_choice(rec).get("message") or {}).get("reasoning") or ""


def select(raw: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """The source records that stopped at the cap (finish_reason "length") with a reasoning trace, in order,
    and the number that stopped there without one."""
    picked, no_trace = [], 0
    for r in raw:
        if _choice(r).get("finish_reason") == "length":
            if trace_of(r).strip():
                picked.append(r)
            else:
                no_trace += 1
    return picked, no_trace


def prompt_tokens_estimate(rec: dict[str, Any]) -> int:
    """A forced prompt's size: the source's prompt plus all it generated. In the 2026-11-18 probes the API
    reported 1.0007-1.0033 times this; the cost guard's safety factor (1.25) covers the difference."""
    usage = rec["response"]["usage"]
    return usage["prompt_tokens"] + usage["completion_tokens"]


class ForcedRunner(Runner):
    """run.py's Runner for forced calls: each call reserves a worst case priced from its source response's
    usage (not from the prompt's bytes), and its raw record says where its prompt came from."""

    def worst_case(self, job: dict[str, Any]) -> float:
        return job["worst"]

    def _record(self, job: dict[str, Any], body: dict[str, Any], key: str, **kw: Any) -> dict[str, Any]:
        return {**super()._record(job, body, key, **kw), **job["provenance"]}


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(prog="python -m reasoning_heuristics.evals.force", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="the source run directory, data/runs/<source_run_id>")
    ap.add_argument("--cap-usd", type=float, help="hard cap on API-reported spend for this invocation (required for a live pass)")
    ap.add_argument("--max-tokens", type=int, default=4096, help="max_tokens of each forced call (default 4096)")
    ap.add_argument("--dry-run", action="store_true", help="print the count and the cost estimate and exit; no network")
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
    return ap.parse_args(argv)


def main(argv: list[str] | None = None, client: OpenRouterClient | None = None) -> int:
    a = parse_args(argv)
    src = Path(a.source)
    src_manifest = json.loads((src / "manifest.json").read_text(encoding="utf-8"))
    if src_manifest.get("forced"):
        raise SystemExit(f"{src} is a forced pass itself; force its source run")
    if (src / PARTIAL).exists():
        raise SystemExit(f"{src} holds records not yet merged into {RAW} ({PARTIAL}); resume that run to the end first")
    source_id = src_manifest["run_id"]
    run_id, out = f"{FORCED_DIR}/{source_id}", src.parent / FORCED_DIR / source_id
    cfg = get_model(src_manifest["model_requested"])
    routing = src_manifest["provider_routing"]
    if cfg.pinned_price is None or not routing or routing != cfg.provider:
        raise SystemExit(f"{cfg.slug}: the source run was routed {routing}, not to the configured pin {cfg.provider}; "
                         "forced calls go to the source's provider and are priced at the pinned endpoint's price")
    price = cfg.pinned_price
    source_sha = sha256_file(src / RAW)
    picked, no_trace = select(read_jsonl_gz(src / RAW))
    if a.limit:
        picked = picked[: a.limit]
    if any(r["request"].get("provider") != routing for r in picked):
        raise SystemExit(f"{src}: some source requests were not routed {routing}")
    try:
        bodies = [forced_body(r["request"], trace_of(r), a.max_tokens) for r in picked]
    except UnsupportedModel as e:
        raise SystemExit(str(e)) from e
    items_ref = (src_manifest.get("git") or {}).get("sha") if a.items_at_run_sha else None
    if a.items_at_run_sha and not items_ref:
        raise SystemExit(f"{src}: the source manifest records no git SHA")
    load_run_items(src_manifest, a.allow_item_drift, items_ref)  # the scorer's items, checked before anything is spent
    prompt_tokens = sum(prompt_tokens_estimate(r) for r in picked)
    est = {"calls": len(picked), "prompt_tokens": prompt_tokens, "cost_usd": round(price.cost(prompt_tokens, 0), 4),
           "worst_case_usd": round(price.cost(prompt_tokens, a.max_tokens * len(picked)), 4),
           "assumptions": "prompt tokens: each source response's prompt plus completion tokens; cost_usd is the prompt "
                          "alone (every call answers at once), worst_case_usd has every call at max_tokens"}
    print(f"## Forced final answers: {source_id} ({cfg.slug}, template {TEMPLATE}, max_tokens {a.max_tokens})\n\n"
          f"{len(picked)} calls: the responses that stopped at the cap with a reasoning trace"
          f"{f' (the first {a.limit})' if a.limit else ''}. {no_trace} stopped there without a trace and are skipped.\n"
          f"Prompt tokens (each source response's prompt plus completion tokens): {prompt_tokens:,}.\n"
          f"Estimate at ${price.prompt}/M prompt, ${price.completion}/M completion ({price.source}): "
          f"${est['cost_usd']:.4f} if every call answers at once; ${est['worst_case_usd']:.4f} if every call runs to max_tokens.")
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
    out.mkdir(parents=True, exist_ok=True)
    done = {(r["item_id"], r.get("sample", 0)) for r in read_raw(out) if r.get("response") is not None}
    jobs = []
    for r, body in zip(picked, bodies):
        sample = r.get("sample", 0)
        if (r["item_id"], sample) not in done:
            jobs.append({"item": {k: r[k] for k in ITEM_FIELDS}, "sample": sample, "body": body, "key": cache_key(body, sample),
                         "worst": guard.safety * price.cost(prompt_tokens_estimate(r), a.max_tokens),
                         "provenance": {"source_run_id": source_id, "source_cache_key": r["cache_key"], "forced_template": TEMPLATE}})
    src_cond = src_manifest["condition"]
    manifest: dict[str, Any] = {
        "run_id": run_id, "status": "running", "started_at": utc_now(), "model_requested": cfg.slug,
        "source": {"run_id": source_id, "raw_sha256": source_sha, "condition": src_cond["label"], "git": src_manifest.get("git")},
        "forced": {"template": TEMPLATE, "endpoint": ENDPOINT, "max_tokens": a.max_tokens},
        "condition": {"name": "forced", "label": f"{src_cond['label']}-forced", "effort": src_cond.get("effort"),
                      "max_tokens": a.max_tokens, "system_prompt": src_cond.get("system_prompt"), "reasoning": None,
                      "sampling": src_cond.get("sampling"), "template": TEMPLATE},
        "provider_routing": routing, "price": price.__dict__, "model_notes": cfg.notes,
        "items": {"files": src_manifest["items"]["files"], "n_items": len(picked), "skipped": {"no_trace": no_trace},
                  "limit": a.limit, "allow_item_drift": a.allow_item_drift, "items_ref": items_ref},
        "estimate": est, "cap_usd": cap, "cap_requested_usd": a.cap_usd, "budget_tag": a.budget_tag,
        "budget_usd": a.budget_usd, "budget_spent_before_usd": spent_before, "git": git_info(), "versions": versions(),
        "client": {"timeout_s": client.timeout_s, "max_attempts": client.max_attempts, "concurrency": a.concurrency},
        "notes": a.notes, "resumed_from": len(done),
        "counts": {"selected": len(picked), "skipped_no_trace": no_trace, "responses": None, "answered": None,
                   "still_reasoning": None},
    }
    manifest_path = out / "manifest.json"
    if manifest_path.exists():  # a resumed pass keeps every earlier invocation's provenance
        old = json.loads(manifest_path.read_text(encoding="utf-8"))
        if old["forced"] != manifest["forced"] or old["source"]["raw_sha256"] != source_sha:
            raise SystemExit(f"{out}: resuming with a different template, max_tokens or source raw file than the pass was started with")
        keep = ("started_at", "finished_at", "status", "stop_reason", "git", "versions", "cap_usd", "charged_usd", "spend",
                "responses", "failed_calls", "resumed_from", "providers_served", "models_returned", "wall_s", "client", "notes")
        manifest["previous_invocations"] = old.get("previous_invocations", []) + [{k: old.get(k) for k in keep}]
    write_json(manifest_path, manifest)
    runner = ForcedRunner(client, None if a.no_cache else ResponseCache(a.cache_dir), guard, out, run_id, a.concurrency,
                          send=client.complete)
    t0 = time.monotonic()
    try:
        runner.run(jobs)
    finally:
        recs = read_raw(out)
        write_raw(out, recs, {r["item_id"]: i for i, r in enumerate(picked)})
        responses = [r["response"] for r in recs if r.get("response")]
        status = "complete" if runner.stop_reason is None and len(responses) == len(picked) else (
            "stopped" if runner.stop_reason else "incomplete")
        manifest.update({
            "status": status, "stop_reason": runner.stop_reason, "finished_at": utc_now(),
            "wall_s": round(time.monotonic() - t0, 1),
            "models_returned": sorted({str(r.get("model")) for r in responses}),
            "providers_served": dict(sorted(Counter(str(served_provider(r)) for r in responses).items())),
            "responses": len(responses), "failed_calls": runner.failures, "cache_hits": runner.cache_hits,
            "spend": guard.to_json(), "charged_usd": round(runner.charged, 6),
            "charged_usd_all_invocations": round(runner.charged + sum((p.get("charged_usd") or 0) for p in manifest.get("previous_invocations", [])), 6),
            "api_reported_cost_usd_all_responses": round(sum(float((r.get("usage") or {}).get("cost") or 0) for r in responses), 6),
        })
        manifest["counts"]["responses"] = len(responses)
        write_json(manifest_path, manifest)
        if guard.calls or runner.failures:
            ledger.append(Path(a.ledger), date=utc_now()[:10], run_id=run_id, model=cfg.slug, condition=manifest["condition"]["label"],
                          items=len(responses) - len(done), cost_usd=runner.charged, budget_tag=a.budget_tag or "-",
                          notes=(a.notes + f" status={status}").strip())
    score_run(out, a.allow_item_drift, items_ref=items_ref)
    manifest["counts"].update(forced_outcomes(read_jsonl_gz(out / SCORED)))
    write_json(manifest_path, manifest)
    c = manifest["counts"]
    print(f"[{run_id}] {status}: {c['responses']} responses ({c['answered']} answered, {c['still_reasoning']} still reasoning), "
          f"${runner.charged:.4f} charged, {runner.cache_hits} from cache" + (f"; stopped: {runner.stop_reason}" if runner.stop_reason else ""))
    return 0 if status == "complete" else 2


if __name__ == "__main__":
    sys.exit(main())
