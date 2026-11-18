"""Run a model over item sets: dry-run cost estimate, cached and capped live calls, raw outputs,
scoring, report, manifest and ledger.

    python -m reasoning_heuristics.evals.run --items data/items/smoke --model openai/gpt-oss-20b \\
        --effort high --cap-usd 2 --out data/runs/<run_id> [--dry-run] [--exclude-eval E8]

Outputs in --out (kept permanently; see docs/RUNNER.md):
    manifest.json      model, provider, parameters, item-set hashes, git SHA, versions, spend
    raw.jsonl.gz       one record per (item, sample): the exact request and the full API response
    scored.jsonl.gz    one scored record per response (re-made by `python -m reasoning_heuristics.evals.score`)
    REPORT.md          descriptive summary
Re-running into the same --out resumes: completed (item, sample) pairs are not sent again, and the
response cache means a request identical to one already answered is never paid for twice.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from reasoning_heuristics.evals import cost as C
from reasoning_heuristics.evals import ledger
from reasoning_heuristics.evals.cache import ResponseCache, cache_key, prompt_hash
from reasoning_heuristics.evals.client import KEY_ENV, FatalAPIError, MissingKeyError, OpenRouterClient
from reasoning_heuristics.evals.manifest import (REPO, file_hashes, git_info, item_files, load_items, utc_now, versions,
                                                 write_json)
from reasoning_heuristics.evals.models import Condition, ModelConfig, Pricing, condition, get_model, request_body
from reasoning_heuristics.evals.scoring import served_provider

RAW = "raw.jsonl.gz"
PARTIAL = "raw.partial.jsonl"


def routing(cfg: ModelConfig, provider: str | None, quantizations: list[str] | None, no_pin: bool) -> dict[str, Any] | None:
    if provider:
        out: dict[str, Any] = {"order": [provider], "allow_fallbacks": False, "require_parameters": True}
        if quantizations:
            out["quantizations"] = quantizations
        return out
    if cfg.provider:
        return dict(cfg.provider)
    if no_pin:
        return None
    raise SystemExit(f"{cfg.slug} has no pinned provider (SCOPE §1: pin provider and precision before any pilot). "
                     "Run the probes and pin one in evals/models.py, pass --provider, or pass --no-pin explicitly.")


def item_seed(base: int, item_id: str, sample: int) -> int:
    return (base + int(hashlib.sha256(f"{item_id}#{sample}".encode()).hexdigest()[:8], 16)) % (2 ** 31)


def read_raw(out: Path) -> list[dict[str, Any]]:
    recs = []
    if (out / RAW).exists():
        with gzip.open(out / RAW, "rt", encoding="utf-8") as fh:
            recs += [json.loads(line) for line in fh if line.strip()]
    if (out / PARTIAL).exists():
        for line in (out / PARTIAL).read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    recs.append(json.loads(line))
                except json.JSONDecodeError:  # a line cut by a crash: that call is simply redone
                    pass
    latest: dict[tuple[str, int], dict[str, Any]] = {}
    for r in recs:  # a later successful record replaces an earlier failed one
        k = (r["item_id"], r.get("sample", 0))
        if k not in latest or (latest[k].get("response") is None and r.get("response") is not None):
            latest[k] = r
    return list(latest.values())


def write_raw(out: Path, recs: list[dict[str, Any]], order: dict[str, int]) -> None:
    recs = sorted(recs, key=lambda r: (order.get(r["item_id"], 10 ** 9), r.get("sample", 0)))
    tmp = out / (RAW + ".tmp")
    with open(tmp, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
        for r in recs:
            gz.write((json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
    tmp.replace(out / RAW)
    (out / PARTIAL).unlink(missing_ok=True)


class Runner:
    """Sends the requests with bounded concurrency under a CostGuard, caching every completed response."""

    def __init__(self, client: OpenRouterClient, cache: ResponseCache | None, guard: C.CostGuard, out: Path,
                 run_id: str, concurrency: int = 8, progress_every: int = 10):
        self.client, self.cache, self.guard, self.out, self.run_id = client, cache, guard, out, run_id
        self.concurrency = concurrency
        self.progress_every = progress_every
        self._write_lock = threading.Lock()
        self.stop_reason: str | None = None
        self.done = 0
        self.cache_hits = 0
        self.failures = 0
        self.charged = 0.0

    def _append(self, rec: dict[str, Any]) -> None:
        with self._write_lock:
            with (self.out / PARTIAL).open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
            self.done += 1
            if self.progress_every and self.done % self.progress_every == 0:
                print(f"[{self.run_id}] {self.done} done, ${self.guard.spent:.4f} spent, {self.failures} failed", file=sys.stderr, flush=True)

    def _record(self, job: dict[str, Any], body: dict[str, Any], key: str, **kw: Any) -> dict[str, Any]:
        it = job["item"]
        rec = {"run_id": self.run_id, "item_id": it["item_id"], "content_hash": it["content_hash"],
               "presentation_hash": it["presentation_hash"], "vertical": it["vertical"], "eval_id": it["eval_id"],
               "sample": job["sample"], "cache_key": key, "prompt_hash": prompt_hash(body["messages"]),
               "request": body, "requested_at": utc_now()}
        rec.update(kw)
        return rec

    def run(self, jobs: list[dict[str, Any]]) -> None:
        slots = threading.BoundedSemaphore(self.concurrency)
        with ThreadPoolExecutor(max_workers=self.concurrency) as pool:
            for job in jobs:
                if self.stop_reason:
                    break
                body, key = job["body"], job["key"]
                cached = self.cache.get(key) if self.cache else None
                if cached is not None and cached.get("response") is not None:
                    self.cache_hits += 1
                    self._append(self._record(job, body, key, response=cached["response"], error=None, errors=[],
                                              attempts=0, status=200, latency_s=0.0, from_cache=True,
                                              cached_from=cached.get("source"), charged_usd=0.0,
                                              cost_usd=(cached["response"].get("usage") or {}).get("cost"),
                                              failed_attempt_costs=[]))
                    continue
                worst = self.guard.worst_case(json.dumps(body))
                slots.acquire()
                if self.stop_reason:
                    slots.release()
                    break
                if not self.guard.reserve(worst):
                    slots.release()
                    self.stop_reason = (f"cap: the next request's worst case ${worst:.4f} would take the running total "
                                        f"(${self.guard.spent:.4f} spent + ${self.guard.reserved:.4f} in flight) past ${self.guard.cap:.4f}")
                    break
                pool.submit(self._call, job, worst, slots)

    def _call(self, job: dict[str, Any], worst: float, slots: threading.BoundedSemaphore) -> None:
        body, key = job["body"], job["key"]
        try:
            try:
                # failed attempts that the API charged are booked as they happen, and a retry is
                # refused when it could take the spend past the cap
                res = self.client.chat(body, on_failed_attempt=self.guard.book_failed_attempt)
            except FatalAPIError as e:
                if e.charged:
                    self.guard.book_failed_attempt(e.charged)
                self.guard.release(worst)
                self.stop_reason = f"fatal API error: {e}"
                with self._write_lock:
                    self.failures += 1
                    self.charged += e.charged
                self._append(self._record(job, body, key, response=None, error=str(e), errors=[str(e)], attempts=1,
                                          status=None, latency_s=0.0, from_cache=False, cached_from=None,
                                          charged_usd=e.charged, cost_usd=None, failed_attempt_costs=[e.charged]))
                return
            except MissingKeyError as e:
                self.guard.release(worst)
                self.stop_reason = str(e)
                return
            usage = (res.response or {}).get("usage") if res.response else None
            failed = False
            if res.ok:
                try:
                    charged = self.guard.settle(worst, usage)
                except C.PriceMismatch as e:
                    charged = float((usage or {}).get("cost") or 0.0)
                    self.stop_reason = str(e)
            else:
                self.guard.release(worst)
                charged = 0.0
                failed = True
                if any(c > 0 for c in res.failed_attempt_costs) and self.guard.spent + self.guard.reserved > self.guard.cap:
                    self.stop_reason = (f"cap: a charged failed attempt took the running total to ${self.guard.spent:.4f} "
                                        f"of ${self.guard.cap:.4f}")
            charged += sum(res.failed_attempt_costs)  # already booked in the guard
            with self._write_lock:
                self.charged += charged
                self.failures += failed
            rec = self._record(job, body, key, response=res.response, error=res.error, errors=res.errors,
                               attempts=res.attempts, status=res.status, latency_s=round(res.latency_s, 2),
                               from_cache=False, cached_from=None, charged_usd=charged,
                               cost_usd=(usage or {}).get("cost"), failed_attempt_costs=res.failed_attempt_costs)
            if res.ok and self.cache is not None:
                self.cache.put(key, {"request": body, "response": res.response, "sample": job["sample"],
                                     "source": f"{self.run_id}"})
            self._append(rec)
        except Exception as e:  # never lose a paid response silently
            self.stop_reason = f"runner error: {type(e).__name__}: {e}"
            raise
        finally:
            slots.release()


def build_jobs(items: list[dict[str, Any]], cfg: ModelConfig, cond: Condition, provider: dict[str, Any] | None,
               samples: int, seed: int | None, done: set[tuple[str, int]]) -> list[dict[str, Any]]:
    jobs = []
    for it in items:
        for s in range(samples):
            if (it["item_id"], s) in done:
                continue
            body = request_body(cfg, cond, it["prompt"], provider, None if seed is None else item_seed(seed, it["item_id"], s))
            jobs.append({"item": it, "sample": s, "body": body, "key": cache_key(body, s)})
    return jobs


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(prog="python -m reasoning_heuristics.evals.run", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--items", nargs="+", required=True, help="item-set files or directories (data/items/smoke)")
    ap.add_argument("--model", required=True, help="OpenRouter model slug, e.g. openai/gpt-oss-20b")
    ap.add_argument("--condition", choices=["thinking", "direct"], default="thinking")
    ap.add_argument("--effort", default="high", help="reasoning effort for the thinking condition (default high)")
    ap.add_argument("--max-tokens", type=int, help="override the condition's max_tokens (32768 thinking, 1024 direct)")
    ap.add_argument("--cap-usd", type=float, help="hard cap on API-reported spend for this run (required for live runs)")
    ap.add_argument("--out", required=True, help="run directory, data/runs/<run_id>")
    ap.add_argument("--dry-run", action="store_true", help="print the cost estimate and exit; no network")
    ap.add_argument("--exclude-eval", action="append", default=[], help="eval to skip (E8, or AH-E8); repeatable")
    ap.add_argument("--include-eval", action="append", default=[], help="run only these evals; repeatable")
    ap.add_argument("--limit", type=int, help="only the first N items (after filters)")
    ap.add_argument("--samples", type=int, default=1, help="samples per item (repeats are separate cache keys)")
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--provider", help="pin this provider slug (order=[p], allow_fallbacks=false) instead of the configured pin")
    ap.add_argument("--quantization", action="append", help="with --provider: allowed quantizations; repeatable")
    ap.add_argument("--no-pin", action="store_true", help="allow an unpinned model (not for pilots)")
    ap.add_argument("--price", type=float, nargs=2, metavar=("PROMPT", "COMPLETION"),
                    help="USD per million tokens for the estimate and the cap (default: the pinned endpoint's, else SCOPE list price)")
    ap.add_argument("--seed", type=int, help="send a per-item seed derived from this base (only if the provider supports seed)")
    ap.add_argument("--cache-dir", default=str(REPO / "data" / "cache" / "openrouter"))
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--ledger", default=str(REPO / "data" / "runs" / "LEDGER.md"))
    ap.add_argument("--budget-tag", help="ledger tag whose running total counts against --budget-usd")
    ap.add_argument("--budget-usd", type=float, help="total budget for --budget-tag across runs and probes")
    ap.add_argument("--timeout", type=float, default=1800.0, help="per-request timeout in seconds")
    ap.add_argument("--notes", default="", help="free text for the manifest and the ledger row")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None, client: OpenRouterClient | None = None) -> int:
    a = parse_args(argv)
    out = Path(a.out)
    run_id = out.name
    cfg = get_model(a.model)
    cond = condition(cfg, a.condition, a.effort if a.condition == "thinking" else None, a.max_tokens)
    files = item_files(a.items)
    items, skipped = load_items(files, a.exclude_eval, a.include_eval)
    if a.limit:
        items = items[: a.limit]
    provider = routing(cfg, a.provider, a.quantization, a.no_pin or a.dry_run)
    if not a.provider and cfg.max_completion_tokens and cond.max_tokens > cfg.max_completion_tokens:
        raise SystemExit(f"{cfg.slug}: max_tokens {cond.max_tokens} is above the pinned endpoint's completion limit "
                         f"{cfg.max_completion_tokens}; the condition cannot run there ({cfg.notes})")
    price: Pricing = cfg.pinned_price if (cfg.pinned_price and not a.provider) else cfg.list_price
    if a.price:
        price = Pricing(a.price[0], a.price[1], "--price")
    est = C.estimate(items, cond, price, a.samples)
    print(C.format_estimate(est, f"Cost estimate: {run_id} ({cfg.slug}, {len(items)} items, skipped {skipped})"))
    if a.dry_run:
        return 0
    if a.cap_usd is None:
        raise SystemExit("--cap-usd is required for a live run")
    cap = a.cap_usd
    spent_before = None
    if a.budget_tag:
        if a.budget_usd is None:
            raise SystemExit("--budget-tag needs --budget-usd")
        spent_before = ledger.spent(Path(a.ledger), a.budget_tag)
        cap = min(cap, a.budget_usd - spent_before)
        print(f"budget {a.budget_tag}: ${spent_before:.4f} of ${a.budget_usd:.2f} already booked; this run's cap is ${cap:.4f}",
              file=sys.stderr)
    if client is None:
        import os
        if not os.environ.get(KEY_ENV):
            raise SystemExit(f"{KEY_ENV} is not set in the environment")
        client = OpenRouterClient(timeout_s=a.timeout)
    guard = C.CostGuard(cap, price, cond.max_tokens)
    out.mkdir(parents=True, exist_ok=True)
    previous = read_raw(out)
    done = {(r["item_id"], r.get("sample", 0)) for r in previous if r.get("response") is not None}
    jobs = build_jobs(items, cfg, cond, provider, a.samples, a.seed, done)
    manifest: dict[str, Any] = {
        "run_id": run_id, "status": "running", "started_at": utc_now(), "model_requested": cfg.slug,
        "condition": cond.to_json(), "provider_routing": provider, "price": price.__dict__,
        "model_notes": cfg.notes, "samples_per_item": a.samples, "seed_base": a.seed,
        "items": {"files": file_hashes(files), "n_items": len(items), "skipped": skipped,
                  "exclude_eval": a.exclude_eval, "include_eval": a.include_eval, "limit": a.limit},
        "estimate": {"cost_usd": est["cost_usd"], "worst_case_usd": est["worst_case_usd"],
                     "output_tokens": est["output_tokens"], "prompt_tokens_proxy": est["prompt_tokens"]},
        "cap_usd": cap, "cap_requested_usd": a.cap_usd, "budget_tag": a.budget_tag, "budget_usd": a.budget_usd,
        "budget_spent_before_usd": spent_before, "git": git_info(), "versions": versions(),
        "client": {"timeout_s": client.timeout_s, "max_attempts": client.max_attempts, "concurrency": a.concurrency},
        "notes": a.notes, "resumed_from": len(done),
    }
    write_json(out / "manifest.json", manifest)
    runner = Runner(client, None if a.no_cache else ResponseCache(a.cache_dir), guard, out, run_id, a.concurrency)
    key_before = client.key_usage() if jobs else {}
    t0 = time.monotonic()
    try:
        runner.run(jobs)
    finally:
        key_after = client.key_usage() if jobs else {}
        delta = None
        if isinstance(key_before.get("usage"), (int, float)) and isinstance(key_after.get("usage"), (int, float)):
            delta = round(key_after["usage"] - key_before["usage"], 6)
        manifest["key_usage"] = {"before": key_before, "after": key_after, "delta_usd": delta,
                                 "note": "the key's own usage counter (GET /key); other users of the key move it too"}
        recs = read_raw(out)
        write_raw(out, recs, {it["item_id"]: i for i, it in enumerate(items)})
        status = "complete" if runner.stop_reason is None and len([r for r in recs if r.get("response")]) == len(items) * a.samples else (
            "stopped" if runner.stop_reason else "incomplete")
        responses = [r["response"] for r in recs if r.get("response")]
        manifest.update({
            "status": status, "stop_reason": runner.stop_reason, "finished_at": utc_now(),
            "wall_s": round(time.monotonic() - t0, 1),
            "models_returned": sorted({str(r.get("model")) for r in responses}),
            "system_fingerprints": sorted({str(r.get("system_fingerprint")) for r in responses if r.get("system_fingerprint")}),
            "providers_served": _counts(served_provider(r) for r in responses),
            "responses": len(responses), "failed_calls": runner.failures, "cache_hits": runner.cache_hits,
            "spend": guard.to_json(), "charged_usd": round(runner.charged, 6),
            "api_reported_cost_usd_all_responses": round(sum(float((r.get("usage") or {}).get("cost") or 0) for r in responses), 6),
        })
        write_json(out / "manifest.json", manifest)
        if guard.calls or runner.failures:
            ledger.append(Path(a.ledger), date=utc_now()[:10], run_id=run_id, model=cfg.slug, condition=cond.label,
                          items=len({r["item_id"] for r in recs if r.get("response")}), cost_usd=runner.charged,
                          budget_tag=a.budget_tag or "-", notes=(a.notes + f" status={status}").strip())
    from reasoning_heuristics.evals.score import score_run
    score_run(out)
    print(f"[{run_id}] {status}: {manifest['responses']} responses, ${runner.charged:.4f} charged, "
          f"{runner.cache_hits} from cache" + (f"; stopped: {runner.stop_reason}" if runner.stop_reason else ""))
    return 0 if status == "complete" else 2


def _counts(values) -> dict[str, int]:
    out: dict[str, int] = {}
    for v in values:
        out[str(v)] = out.get(str(v), 0) + 1
    return dict(sorted(out.items()))


if __name__ == "__main__":
    sys.exit(main())
