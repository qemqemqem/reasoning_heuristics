"""REPORT.md for a run: descriptive only (categories, accuracy, tokens, truncation, parse checks).
No mixture fits and no claims about heuristics; those belong to the identification engine."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from reasoning_heuristics.evals.cost import kind_of, token_stats
from reasoning_heuristics.evals.scoring import CATEGORIES


def _pct(a: int, b: int) -> str:
    return f"{100 * a / b:.0f}%" if b else "–"


def _num(v: Any) -> str:
    if v is None:
        return "–"
    return f"{v:,.0f}" if isinstance(v, (int, float)) else str(v)


def build_report(manifest: dict[str, Any], scored: list[dict[str, Any]], items: dict[str, dict[str, Any]] | None = None) -> str:
    cond = manifest["condition"]
    spend = manifest.get("spend") or {}
    L = [f"# Run {manifest['run_id']}", "",
         "Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.", "",
         f"- **Model:** requested `{manifest['model_requested']}`; returned {', '.join(f'`{m}`' for m in manifest.get('models_returned', [])) or '–'}.",
         f"- **Provider:** routing `{manifest.get('provider_routing')}`; served {manifest.get('providers_served') or '–'}.",
         f"- **Condition:** `{cond['label']}`; max_tokens {cond['max_tokens']}; reasoning `{cond['reasoning']}`; sampling `{cond['sampling']}`"
         + (f"; system prompt: \"{cond['system_prompt']}\"" if cond.get("system_prompt") else "; no system prompt") + ".",
         f"- **Items:** {manifest['items']['n_items']} ({', '.join(manifest['items']['files'])}); skipped {manifest['items']['skipped']}.",
         f"- **Status:** {manifest.get('status')}" + (f" ({manifest['stop_reason']})" if manifest.get("stop_reason") else "") +
         f"; {manifest.get('responses', '–')} responses, {manifest.get('failed_calls', 0)} failed calls, {manifest.get('cache_hits', 0)} from cache.",
         f"- **Spend:** ${manifest.get('charged_usd_all_invocations', manifest.get('charged_usd', 0)):.4f} API-reported over {1 + len(manifest.get('previous_invocations', []))} invocation(s) (last cap ${manifest.get('cap_usd', 0):.2f}; dry-run estimate "
         f"${manifest.get('estimate', {}).get('cost_usd', 0):.2f}, worst case ${manifest.get('estimate', {}).get('worst_case_usd', 0):.2f})."
         + (f" {spend['calls_without_reported_cost']} calls carried no cost and were booked at the configured price." if spend.get("calls_without_reported_cost") else ""),
         f"- **Code:** git `{(manifest.get('git') or {}).get('sha')}`{' (dirty)' if (manifest.get('git') or {}).get('dirty') else ''}; "
         f"scorer `{scored[0]['scorer_version'] if scored else '–'}` at `{scored[0].get('scorer_git_sha') if scored else '–'}`.", ""]
    by_eval: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in scored:
        by_eval[(r["vertical"], r["eval_id"])].append(r)
    cats = [c for c in CATEGORIES if any(r["category"] == c for r in scored)] or ["ok"]
    L += ["## Response categories", "", "Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).", "",
          "| Vertical | Eval | Responses | " + " | ".join(cats) + " | Correct of ok |", "|---|---|---|" + "---|" * len(cats) + "---|"]
    for (v, e), rs in sorted(by_eval.items()):
        c = Counter(r["category"] for r in rs)
        ok = [r for r in rs if r["category"] == "ok"]
        right = sum(1 for r in ok if r["correct"])
        L.append(f"| {v} | {e} | {len(rs)} | " + " | ".join(str(c.get(k, 0)) for k in cats) + f" | {right}/{len(ok)} ({_pct(right, len(ok))}) |")
    tot = Counter(r["category"] for r in scored)
    ok_all = [r for r in scored if r["category"] == "ok"]
    right_all = sum(1 for r in ok_all if r["correct"])
    L.append(f"| **All** | | **{len(scored)}** | " + " | ".join(f"**{tot.get(k, 0)}**" for k in cats) +
             f" | **{right_all}/{len(ok_all)} ({_pct(right_all, len(ok_all))})** |")
    L += ["", "## Tokens per response", "", "API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.", "",
          "| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    by_kind: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in scored:
        by_kind[(r["vertical"], r["eval_id"], _kind(r))].append(r)
    for (v, e, k), rs in sorted(by_kind.items()):
        ct, rt = token_stats([r["completion_tokens"] for r in rs]), token_stats([r["reasoning_tokens"] for r in rs])
        pt = token_stats([r["prompt_tokens"] for r in rs])
        tr = sum(1 for r in rs if r["truncated"])
        rr = sum(1 for r in rs if r["reasoning_returned"])
        L.append(f"| {v} | {e} | {k} | {len(rs)} | {_num(ct['median'])} | {_num(ct['mean'])} | {_num(rt['median'])} | {_num(rt['mean'])} | "
                 f"{_num(pt['mean'])} | {tr} ({_pct(tr, len(rs))}) | {rr} ({_pct(rr, len(rs))}) | {_cost_per_item(rs)} |")
    ct, rt = token_stats([r["completion_tokens"] for r in scored]), token_stats([r["reasoning_tokens"] for r in scored])
    L.append(f"| **All** | | | **{len(scored)}** | **{_num(ct['median'])}** | **{_num(ct['mean'])}** | **{_num(rt['median'])}** | "
             f"**{_num(rt['mean'])}** | | **{sum(1 for r in scored if r['truncated'])}** | **{sum(1 for r in scored if r['reasoning_returned'])}** | "
             f"**{_cost_per_item(scored)}** |")
    pre = token_stats([r["pre_answer_tokens"] for r in scored])
    over = sum(1 for r in scored if (r["pre_answer_tokens"] or 0) > 20)
    L += ["", "## Visible text before the answer", "",
          f"`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median {_num(pre['median'])}, mean {_num(pre['mean'])}, "
          f"max {_num(pre['max'])}; {over} responses ({_pct(over, len(scored))}) have more than 20. In the direct condition these are responses that "
          "worked in the visible output and may need flagging or exclusion.", ""]
    flags = Counter(f for r in scored for f in r["flags"])
    if flags:
        L += ["## Parse flags", "", "| Flag | Responses |", "|---|---|"] + [f"| `{f}` | {n} |" for f, n in flags.most_common()] + [""]
    bad = [r for r in scored if r["category"] in ("parse_fail", "partial", "declared_impossible", "refusal", "api_error")]
    if bad:
        L += ["## Responses that are not ok (first 25, for checking the scorer)", "", "| Item | Category | Detail |", "|---|---|---|"]
        for r in bad[:25]:
            L.append(f"| `{r['item_id']}` | {r['category']} | {str(r['parse_detail'])[:140].replace('|', '/')} |")
        L.append("")
    trunc_cells = Counter((r["eval_id"], r["cell"]) for r in scored if r["truncated"])
    if trunc_cells:
        L += ["## Truncation by cell (censored, SCOPE §6 rule 2)", "", "| Eval | Cell | Truncated |", "|---|---|---|"]
        L += [f"| {e} | {c} | {n} |" for (e, c), n in sorted(trunc_cells.items())] + [""]
    return "\n".join(L) + "\n"


def _cost_per_item(rs: list[dict[str, Any]]) -> str:
    costs = [r["cost_usd"] for r in rs if r.get("cost_usd") is not None]
    return f"{sum(costs) / len(costs):.5f}" if costs else "–"


def _kind(r: dict[str, Any]) -> str:
    return kind_of({"vertical": r["vertical"], "eval_id": r["eval_id"], "domain": r["item_domain"],
                    "answer_format": r["answer_format"], "item_id": r["item_id"]})
