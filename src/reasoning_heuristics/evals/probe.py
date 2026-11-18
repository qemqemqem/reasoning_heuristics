"""Provider probes (SCOPE §1, "before any pilot"): which providers of each model return the
reasoning text, which honour thinking off, and at what precision, so a provider can be pinned.

    python -m reasoning_heuristics.evals.probe --model qwen/qwen3-32b --model openai/gpt-oss-20b \\
        --out data/runs/probes/2026-11-17 --cap-usd 0.25 [--budget-tag T --budget-usd 3]

For each model: GET /models/{slug}/endpoints (free) lists every provider endpoint with its
quantization, context, prices and supported parameters. Then, per endpoint (up to
--max-endpoints, full precision first), a few tiny chat calls pinned to that endpoint
(`order: [tag]`, `allow_fallbacks: false`):

- `on`:      reasoning on (the model's thinking setting);
- `off`:     reasoning {"enabled": false};
- `none`:    reasoning {"effort": "none"};
- `no_think`: no reasoning parameter, " /no_think" appended to the prompt (Qwen3's soft switch).

Thinking off is honoured when the response has no reasoning text, zero reasoning tokens and no
<think> block in the content. Every call is capped like a run (CostGuard) and the total is
booked in the ledger. Writes probes.json (listings and every raw response) and PROBES.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from reasoning_heuristics.evals import ledger
from reasoning_heuristics.evals.client import FatalAPIError, OpenRouterClient
from reasoning_heuristics.evals.cost import CapReached, CostGuard, PriceMismatch
from reasoning_heuristics.evals.manifest import REPO, git_info, utc_now, write_json
from reasoning_heuristics.evals.models import Pricing, get_model
from reasoning_heuristics.evals.scoring import served_provider

QUESTION = "What is 17 + 25? Reply with just the number."
PRECISION_RANK = {"bf16": 0, "fp16": 0, "fp32": 0, "fp8": 1, "mxfp8": 1, "mxfp4": 2, "fp4": 3, "nvfp4": 3, "fp6": 2,
                  "int8": 2, "int4": 4, "unknown": 5, None: 5}


def endpoint_slug(ep: dict[str, Any]) -> str:
    """The routing slug for `provider.order`: the endpoint tag if listed, else the provider name."""
    return ep.get("tag") or str(ep.get("provider_name", "")).lower()


def endpoint_price(ep: dict[str, Any]) -> Pricing:
    p = ep.get("pricing") or {}
    return Pricing(float(p.get("prompt") or 0) * 1e6, float(p.get("completion") or 0) * 1e6,
                   f"OpenRouter endpoint {endpoint_slug(ep)} ({utc_now()[:10]})")


def probe_variants(slug: str) -> list[tuple[str, dict[str, Any] | None, str]]:
    cfg = get_model(slug)
    on = dict(cfg.thinking_reasoning)
    return [("on", on, ""), ("off", {"enabled": False}, ""), ("none", {"effort": "none"}, ""), ("no_think", None, " /no_think")]


def summarise(resp: dict[str, Any] | None) -> dict[str, Any]:
    if resp is None:
        return {}
    ch = (resp.get("choices") or [{}])[0]
    msg = ch.get("message") or {}
    usage = resp.get("usage") or {}
    reasoning = msg.get("reasoning") or ""
    if not reasoning and msg.get("reasoning_details"):
        reasoning = "".join(d.get("text") or d.get("summary") or "" for d in msg["reasoning_details"] if isinstance(d, dict))
    content = msg.get("content") or ""
    rt = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")
    return {"provider": served_provider(resp), "model": resp.get("model"), "finish_reason": ch.get("finish_reason"),
            "content": content[:200], "reasoning_chars": len(reasoning), "reasoning_returned": bool(reasoning),
            "reasoning_tokens": rt, "completion_tokens": usage.get("completion_tokens"),
            "prompt_tokens": usage.get("prompt_tokens"), "cost": usage.get("cost"),
            "think_in_content": "<think>" in content or "</think>" in content,
            "thinking_off_honoured": not reasoning and not rt and "<think>" not in content and "</think>" not in content}


def run_probes(client: OpenRouterClient, models: list[str], guard: CostGuard, max_endpoints: int, max_tokens: int,
               variants: list[str] | None = None) -> dict[str, Any]:
    out: dict[str, Any] = {"started_at": utc_now(), "question": QUESTION, "max_tokens": max_tokens, "models": {}}
    for slug in models:
        listing = client.endpoints(slug)
        eps = (listing.get("data") or {}).get("endpoints") or []
        ranked = sorted(eps, key=lambda e: (PRECISION_RANK.get(e.get("quantization"), 5),
                                            float((e.get("pricing") or {}).get("completion") or 1)))
        rec: dict[str, Any] = {"listing": listing, "probed": []}
        for ep in ranked[:max_endpoints]:
            price = endpoint_price(ep)
            for name, reasoning, suffix in probe_variants(slug):
                if variants and name not in variants:
                    continue
                body: dict[str, Any] = {"model": slug, "messages": [{"role": "user", "content": QUESTION + suffix}],
                                        "max_tokens": max_tokens,
                                        "provider": {"order": [endpoint_slug(ep)], "allow_fallbacks": False}}
                if reasoning is not None:
                    body["reasoning"] = reasoning
                worst = 1.25 * price.cost(len(json.dumps(body)) + 64, max_tokens) + 1e-6
                entry: dict[str, Any] = {"endpoint": endpoint_slug(ep), "provider_name": ep.get("provider_name"),
                                         "quantization": ep.get("quantization"), "variant": name, "request": body}
                if not guard.reserve(worst):
                    entry["skipped"] = "probe cap reached"
                    rec["probed"].append(entry)
                    continue
                try:
                    res = client.chat(body)
                except FatalAPIError as e:
                    guard.release(worst)
                    entry.update({"error": str(e)[:500]})
                    rec["probed"].append(entry)
                    continue
                if res.ok:
                    try:
                        guard.settle(worst, (res.response or {}).get("usage"))
                    except PriceMismatch as e:  # booked anyway; record it and move on
                        entry["price_mismatch"] = str(e)
                else:
                    guard.release(worst)
                entry.update({"response": res.response, "error": res.error, "attempts": res.attempts,
                              "summary": summarise(res.response)})
                rec["probed"].append(entry)
                print(f"[probe] {slug} @ {entry['endpoint']} ({entry['quantization']}) {name}: "
                      f"{json.dumps(entry['summary']) if res.ok else res.error}", file=sys.stderr, flush=True)
        out["models"][slug] = rec
    out["finished_at"] = utc_now()
    out["spend"] = guard.to_json()
    return out


def report(results: dict[str, Any]) -> str:
    L = ["# Provider probes", "",
         f"Run {results['started_at']} to {results['finished_at']}. Question: \"{results['question']}\" (max_tokens {results['max_tokens']}). "
         f"API-reported spend ${results['spend']['spent_usd']:.4f}.", "",
         "Variants: `on` = the model's thinking setting; `off` = reasoning {enabled: false}; `none` = reasoning {effort: none}; "
         "`no_think` = no reasoning parameter and \" /no_think\" appended to the prompt. Thinking off is honoured when the response has "
         "no reasoning text, zero reasoning tokens and no <think> block.", ""]
    for slug, rec in results["models"].items():
        eps = (rec["listing"].get("data") or {}).get("endpoints") or []
        L += [f"## {slug}", "", "| Endpoint | Provider | Quantization | Context | Max completion | $/M in | $/M out | reasoning | seed | top_k | Status |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for ep in eps:
            sp = set(ep.get("supported_parameters") or [])
            pr = ep.get("pricing") or {}
            L.append(f"| `{endpoint_slug(ep)}` | {ep.get('provider_name')} | {ep.get('quantization')} | {ep.get('context_length')} | "
                     f"{ep.get('max_completion_tokens')} | {float(pr.get('prompt') or 0) * 1e6:.3f} | {float(pr.get('completion') or 0) * 1e6:.3f} | "
                     f"{'y' if 'reasoning' in sp else 'n'} | {'y' if 'seed' in sp else 'n'} | {'y' if 'top_k' in sp else 'n'} | {ep.get('status')} |")
        L += ["", "| Endpoint | Variant | Served by | Reasoning text | Reasoning tokens | Completion tokens | Content | Off honoured | Cost | Error |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for p in rec["probed"]:
            s = p.get("summary") or {}
            err = (p.get("error") or p.get("skipped") or "")[:80].replace("|", "/").replace("\n", " ")
            L.append(f"| `{p['endpoint']}` | {p['variant']} | {s.get('provider', '–')} | {s.get('reasoning_chars', '–')} chars | "
                     f"{s.get('reasoning_tokens', '–')} | {s.get('completion_tokens', '–')} | {str(s.get('content', '')).strip()[:30].replace('|', '/')!r} | "
                     f"{s.get('thinking_off_honoured', '–') if p['variant'] != 'on' else '–'} | {s.get('cost', '–')} | {err} |")
        L.append("")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None, client: OpenRouterClient | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m reasoning_heuristics.evals.probe", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cap-usd", type=float, required=True)
    ap.add_argument("--max-endpoints", type=int, default=6)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--variant", action="append", help="only these variants (on, off, none, no_think)")
    ap.add_argument("--ledger", default=str(REPO / "data" / "runs" / "LEDGER.md"))
    ap.add_argument("--budget-tag")
    ap.add_argument("--budget-usd", type=float)
    a = ap.parse_args(argv)
    cap = a.cap_usd
    if a.budget_tag:
        cap = min(cap, (a.budget_usd or 0) - ledger.spent(Path(a.ledger), a.budget_tag))
    if cap <= 0:
        raise CapReached("no budget left for probes")
    # every probe reserves its own endpoint's worst case; the guard's price is only a fallback
    guard = CostGuard(cap, Pricing(0, 0, "per-endpoint"), a.max_tokens)
    client = client or OpenRouterClient(timeout_s=300)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    results = run_probes(client, a.model, guard, a.max_endpoints, a.max_tokens, a.variant)
    results["git"] = git_info()
    write_json(out / "probes.json", results)
    (out / "PROBES.md").write_text(report(results), encoding="utf-8")
    if guard.calls:
        ledger.append(Path(a.ledger), date=utc_now()[:10], run_id=f"probes/{out.name}", model=", ".join(a.model),
                      condition="probe", items=guard.calls, cost_usd=guard.spent, budget_tag=a.budget_tag or "-",
                      notes="provider probes (calls in the Items column)")
    print(f"probes: {guard.calls} calls, ${guard.spent:.4f}; wrote {out / 'PROBES.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
