"""Does stating the token budget change how a thinking model spends it? The budget-notice runs against their base runs
on the same items (evals/run.py --budget-notice; docs/RUNNER.md).

    python analysis/budget_notice.py            # writes analysis/out/budget_notice.json and budget_notice.md, prints the table
    python analysis/budget_notice.py --check    # recompute and compare with the committed files; writes nothing

It reads, for each pair in PAIRS, data/runs/<run>/scored.jsonl.gz of the notice run and of its base run, and, where
they exist, the forced-answer passes at the cap, data/runs/forced-2/cut/<run>/scored.jsonl.gz. Records are paired on
(item_id, sample). Per unit (vertical, item domain) and over all units:

- truncated: stopped at the cap (max_tokens) before answering;
- correct: the natural answer is ok and correct; wrong: ok and not correct;
- median_tokens: median completion tokens (reasoning included);
- correct_forced: each item once, the natural answer if the response finished, else the forced answer at the cap
  (forced sample 0; an unparsed or missing one counts as not correct). None when either run has no forced pass;
- truncation_flips: [truncated only with the notice, truncated only without it], and correct_flips likewise for
  correct; mcnemar_p_*: the exact two-sided McNemar test on those discordant pairs.
"""

from __future__ import annotations

import argparse
import gzip
import json
import statistics
import sys
from collections import defaultdict
from math import comb
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "data" / "runs"
OUT_JSON = REPO / "analysis" / "out" / "budget_notice.json"
OUT_MD = REPO / "analysis" / "out" / "budget_notice.md"
PAIRS = [("2026-11-18-budget-dev-gpt-oss-20b-thinking-high", "2026-11-18-dev-gpt-oss-20b-thinking-high")]

Key = tuple[str, int]


def read(p: Path) -> list[dict[str, Any]]:
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def by_key(recs: list[dict[str, Any]], sample_field: str = "sample") -> dict[Key, dict[str, Any]]:
    return {(r["item_id"], r.get(sample_field, 0)): r for r in recs}


def good(r: dict[str, Any] | None) -> bool:
    return r is not None and r.get("category") == "ok" and r.get("correct") is True


def mcnemar_p(b: int, c: int) -> float:
    """Exact two-sided McNemar p-value for discordant counts b and c (binomial, p = 1/2)."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(comb(n, i) for i in range(min(b, c) + 1)) / 2**n
    return min(1.0, 2 * tail)


def forced_answers(runs: Path, run_id: str) -> dict[Key, dict[str, Any]] | None:
    """The forced answers at the cap (forced sample 0), keyed on the source record, or None without a pass."""
    p = runs / "forced-2" / "cut" / run_id / "scored.jsonl.gz"
    if not p.exists():
        return None
    return {(r["item_id"], r.get("source_sample", 0)): r for r in read(p) if r.get("forced_sample", 0) == 0}


def side(recs: list[dict[str, Any]], forced: dict[Key, dict[str, Any]] | None) -> dict[str, Any]:
    out = {"truncated": sum(1 for r in recs if r["truncated"]), "correct": sum(1 for r in recs if good(r)),
           "wrong": sum(1 for r in recs if r.get("category") == "ok" and r.get("correct") is False),
           "median_tokens": statistics.median(r.get("completion_tokens") or 0 for r in recs) if recs else None}
    if forced is not None:
        out["correct_forced"] = sum(1 for r in recs
                                    if (good(forced.get((r["item_id"], r.get("sample", 0)))) if r["truncated"] else good(r)))
    else:
        out["correct_forced"] = None
    return out


def compare(runs: Path, notice_id: str, base_id: str) -> dict[str, Any]:
    notice, base = by_key(read(runs / notice_id / "scored.jsonl.gz")), by_key(read(runs / base_id / "scored.jsonl.gz"))
    f_notice, f_base = forced_answers(runs, notice_id), forced_answers(runs, base_id)
    if f_notice is None or f_base is None:
        f_notice = f_base = None  # compare forced accuracy only when both runs have a pass
    keys = sorted(set(notice) & set(base))
    if not keys:
        raise ValueError(f"{notice_id} and {base_id} share no (item, sample)")
    units: dict[str, list[Key]] = defaultdict(list)
    for k in keys:
        units[f"{notice[k]['vertical']} {notice[k].get('domain')}"].append(k)
    rows = []
    for unit, ks in [("all units", keys)] + sorted(units.items()):
        n_recs, b_recs = [notice[k] for k in ks], [base[k] for k in ks]
        t = [sum(1 for k in ks if notice[k]["truncated"] and not base[k]["truncated"]),
             sum(1 for k in ks if base[k]["truncated"] and not notice[k]["truncated"])]
        c = [sum(1 for k in ks if good(notice[k]) and not good(base[k])), sum(1 for k in ks if good(base[k]) and not good(notice[k]))]
        rows.append({"unit": unit, "n": len(ks), "notice": side(n_recs, f_notice), "base": side(b_recs, f_base),
                     "truncation_flips": t, "mcnemar_p_truncation": round(mcnemar_p(*t), 4),
                     "correct_flips": c, "mcnemar_p_correct": round(mcnemar_p(*c), 4)})
    return {"notice_run": notice_id, "base_run": base_id, "paired": len(keys), "notice_records": len(notice),
            "forced_passes": f_notice is not None, "rows": rows}


def compute(runs: Path = RUNS, pairs: list[tuple[str, str]] = PAIRS) -> dict[str, Any]:
    return {"description": "The budget notice against its base run; see the docstring of analysis/budget_notice.py",
            "pairs": [compare(runs, n, b) for n, b in pairs]}


def table(res: dict[str, Any]) -> str:
    L = []
    for p in res["pairs"]:
        L += [f"### {p['notice_run']} against {p['base_run']} ({p['paired']} paired records)", "",
              "| Unit | n | Truncated: base → notice | Correct: base → notice | Correct with forcing at the cap: base → notice "
              "| Median tokens: base → notice | Truncation flips (notice only / base only), p | Correct flips, p |",
              "|---|---|---|---|---|---|---|---|"]
        for r in p["rows"]:
            b, n = r["base"], r["notice"]
            forced = f"{b['correct_forced']} → {n['correct_forced']}" if b["correct_forced"] is not None else "-"
            L.append(f"| {r['unit']} | {r['n']} | {b['truncated']} → {n['truncated']} | {b['correct']} → {n['correct']} | {forced} "
                     f"| {b['median_tokens']:.0f} → {n['median_tokens']:.0f} "
                     f"| {r['truncation_flips'][0]} / {r['truncation_flips'][1]}, {r['mcnemar_p_truncation']} "
                     f"| {r['correct_flips'][0]} / {r['correct_flips'][1]}, {r['mcnemar_p_correct']} |")
        L.append("")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="recompute and compare with the committed files; write nothing")
    a = ap.parse_args(argv)
    res = compute()
    text, md = json.dumps(res, indent=1, sort_keys=True) + "\n", table(res)
    if a.check:
        if not OUT_JSON.exists() or OUT_JSON.read_text() != text or not OUT_MD.exists() or OUT_MD.read_text() != md:
            print(f"{OUT_JSON} or {OUT_MD} differs from a fresh run of analysis/budget_notice.py", file=sys.stderr)
            return 1
        print("budget notice matches the committed files")
        return 0
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(text)
    OUT_MD.write_text(md)
    print(md)
    print(f"wrote {OUT_JSON} and {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
