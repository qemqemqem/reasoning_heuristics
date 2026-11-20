"""Test-retest from the repeat-sample runs: two independent samples of the same prompt (Andrew, 2026-11-19: repeats in
the cheap conditions). A heuristic is a procedure, so a model that follows one should give the same wrong answer to
an item again; noise should not repeat. This measures how often answers repeat, and whether wrong answers that match
a listed heuristic repeat more often than those that match none.

    python analysis/repeat_samples.py            # writes analysis/out/repeat_samples.json and repeat_samples.md, prints the table
    python analysis/repeat_samples.py --check    # recompute and compare with the committed files; writes nothing

It reads data/runs/2026-11-19-repeat-*/scored.jsonl.gz, nothing else. In each run, sample 0 is the original run's
response (served from the cache warmed from data/runs/2026-11-18-<tier>-<condition>) and sample 1 is a new draw a day
later. Records pair on item_id. Per run: over all units, over the full-answer units only (channel == "answer"), and
per unit (vertical, eval, item domain, channel):

- pairs: items with both samples; both_ok: both parsed (category ok);
- correct_s0, correct_s1: ok and correct in each sample (counted over all pairs); mcnemar_p: exact two-sided test on
  the items correct in one sample only, a check that the provider did not drift between the two days;
- same_correctness, same_answer: among both_ok, the same correctness and the same answer_key;
- both_wrong: both ok and wrong; same_wrong: of those, the same answer_key (the same wrong answer);
- both_wrong split by sample 0's wrong answer (answer_kind, as in analysis/findings_checks.py), with how many of
  each repeat exactly (_same):
  - built_matched / built_unmatched: a full colouring, assignment or packing that equals a listed heuristic's answer
    (members_matched not empty) / that equals none. Two samples give the same construction by chance only rarely, so
    a construction that repeats is evidence of a procedure; colouring answer keys are vertex partitions, so a
    relabelling of the colours counts as the same answer;
  - give_up: IMPOSSIBLE or UNSAT, one value, so it repeats whenever the model gives up twice;
  - other: decisions and other short answers, which repeat easily for the same reason.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from collections import defaultdict
from math import comb
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "data" / "runs"
PATTERN = "2026-11-19-repeat-*"
OUT_JSON = REPO / "analysis" / "out" / "repeat_samples.json"
OUT_MD = REPO / "analysis" / "out" / "repeat_samples.md"


def read(p: Path) -> list[dict[str, Any]]:
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def ok(r: dict[str, Any]) -> bool:
    return r.get("category") == "ok"


def good(r: dict[str, Any]) -> bool:
    return ok(r) and r.get("correct") is True


def wrong(r: dict[str, Any]) -> bool:
    return ok(r) and r.get("correct") is False


def answer_kind(r: dict[str, Any]) -> str:
    """give_up: IMPOSSIBLE or UNSAT. built: a full colouring, assignment or packing. other: decisions, open
    entailment answers and single colour numbers. The same rule as analysis/findings_checks.py."""
    p = r.get("parsed")
    if p in ("IMPOSSIBLE", "UNSAT"):
        return "give_up"
    if r["domain"] in ("coloring", "sat", "knapsack") and isinstance(p, (dict, list)) \
            and "only the colour number" not in (r.get("answer_format") or ""):
        return "built"
    return "other"


def mcnemar_p(b: int, c: int) -> float:
    """Exact two-sided McNemar p-value for discordant counts b and c."""
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2**n)


def stats(pairs: list[tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, Any]:
    both_ok = [(a, b) for a, b in pairs if ok(a) and ok(b)]
    both_wrong = [(a, b) for a, b in both_ok if wrong(a) and wrong(b)]
    same = lambda xs: sum(1 for a, b in xs if a.get("answer_key") == b.get("answer_key"))  # noqa: E731
    kind = {k: [(a, b) for a, b in both_wrong if answer_kind(a) == k] for k in ("built", "give_up", "other")}
    built_m = [(a, b) for a, b in kind["built"] if a.get("members_matched")]
    built_u = [(a, b) for a, b in kind["built"] if not a.get("members_matched")]
    only0 = sum(1 for a, b in pairs if good(a) and not good(b))
    only1 = sum(1 for a, b in pairs if good(b) and not good(a))
    return {"pairs": len(pairs), "both_ok": len(both_ok),
            "correct_s0": sum(1 for a, _ in pairs if good(a)), "correct_s1": sum(1 for _, b in pairs if good(b)),
            "mcnemar_p": round(mcnemar_p(only0, only1), 4),
            "same_correctness": sum(1 for a, b in both_ok if good(a) == good(b)), "same_answer": same(both_ok),
            "both_wrong": len(both_wrong), "same_wrong": same(both_wrong),
            "built_matched": len(built_m), "built_matched_same": same(built_m),
            "built_unmatched": len(built_u), "built_unmatched_same": same(built_u),
            "give_up": len(kind["give_up"]), "give_up_same": same(kind["give_up"]),
            "other": len(kind["other"]), "other_same": same(kind["other"])}


def compute(runs: Path = RUNS) -> dict[str, Any]:
    out: dict[str, Any] = {"description": "Test-retest from the repeat-sample runs; see the docstring of analysis/repeat_samples.py",
                           "runs": {}}
    for d in sorted(runs.glob(PATTERN)):
        recs = read(d / "scored.jsonl.gz")
        by: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
        for r in recs:
            by[r["item_id"]][r.get("sample", 0)] = r
        pairs = [(v[0], v[1]) for _, v in sorted(by.items()) if 0 in v and 1 in v]
        units: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
        for a, b in pairs:
            units[f"{a['vertical']} {a['eval_id']} {a.get('domain')} ({a.get('channel')})"].append((a, b))
        out["runs"][d.name] = {"records": len(recs), "all": stats(pairs),
                               "full_answer": stats([(a, b) for a, b in pairs if a.get("channel") == "answer"]),
                               "units": {u: stats(ps) for u, ps in sorted(units.items())}}
    return out


def pct(a: int, b: int) -> str:
    return f"{a}/{b} ({100 * a / b:.0f}%)" if b else "-"


def table(res: dict[str, Any]) -> str:
    L = ["| Run | Unit | Pairs | Correct: s0, s1 (p) | Same correctness | Same answer | Same wrong answer "
         "| Same wrong construction, = a heuristic | Same wrong construction, = none | Same give-up | Same other |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for run, v in res["runs"].items():
        name = run.replace("2026-11-19-repeat-", "")
        for unit, s in [("all units", v["all"]), ("full-answer units", v["full_answer"])] + list(v["units"].items()):
            L.append(f"| {name} | {unit} | {s['pairs']} | {s['correct_s0']}, {s['correct_s1']} ({s['mcnemar_p']}) "
                     f"| {pct(s['same_correctness'], s['both_ok'])} | {pct(s['same_answer'], s['both_ok'])} "
                     f"| {pct(s['same_wrong'], s['both_wrong'])} | {pct(s['built_matched_same'], s['built_matched'])} "
                     f"| {pct(s['built_unmatched_same'], s['built_unmatched'])} | {pct(s['give_up_same'], s['give_up'])} "
                     f"| {pct(s['other_same'], s['other'])} |")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="recompute and compare with the committed files; write nothing")
    a = ap.parse_args(argv)
    res = compute()
    text, md = json.dumps(res, indent=1, sort_keys=True) + "\n", table(res)
    if a.check:
        if not OUT_JSON.exists() or OUT_JSON.read_text() != text or not OUT_MD.exists() or OUT_MD.read_text() != md:
            print(f"{OUT_JSON} or {OUT_MD} differs from a fresh run of analysis/repeat_samples.py", file=sys.stderr)
            return 1
        print("repeat samples match the committed files")
        return 0
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(text)
    OUT_MD.write_text(md)
    print(md)
    print(f"wrote {OUT_JSON} and {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
