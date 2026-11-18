"""Acceptance tests of the forced-answer machinery (evals/force.py, template force-2), from the committed passes.

    python analysis/forcing_acceptance.py            # writes analysis/out/forcing_acceptance.json and prints a table
    python analysis/forcing_acceptance.py --check    # recompute and compare with the committed JSON

It reads data/runs/forced-2/{done,cut}/<source_run_id>/{scored,raw}.jsonl.gz, nothing else. Per model:

- f = 1 (`--select done`): finished traces replayed whole, the answer forced. `same_answer` is the forced answer's
  answer key equal to the model's own natural answer's (both ok); `same_correctness` is the forced answer ok with the
  same correctness as the natural one. Problems with many solutions (a colouring, a satisfying assignment) can give a
  different but equally correct answer, which `same_answer` counts against and `same_correctness` does not. The bar
  (docs/RUNNER.md) is 95% on `same_answer`.
- Repeatability (`--samples 2`): records whose two forced samples are both ok, and how many of those give the same
  answer key.
- Cut traces (`--select cut`): `answered` (stopped by itself with a non-empty reply), `parsed` (category ok),
  `still_writing` (stopped at max_tokens again), `renewed_reasoning` (the choice carries reasoning: should be 0),
  and `provider_empty` (an empty reply with no usage record: a provider failure, not the model's answer). The bars
  are 95% for answered and for parsed.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "analysis" / "out" / "forcing_acceptance.json"
ROOT = REPO / "data" / "runs" / "forced-2"


def read(p: Path) -> list[dict[str, Any]]:
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def model_of(run_id: str) -> str:
    for m in ("gpt-oss-120b", "gpt-oss-20b", "qwen3-32b", "qwen3-14b"):
        if f"-{m}-" in run_id:
            return m
    raise ValueError(run_id)


def pct(a: int, b: int) -> float | None:
    return round(100 * a / b, 1) if b else None


def done_stats(recs: list[dict[str, Any]]) -> dict[str, Any]:
    nat_ok = [r for r in recs if r.get("natural_category") == "ok"]
    same = sum(1 for r in nat_ok if r.get("same_as_natural"))
    same_corr = sum(1 for r in nat_ok if r["category"] == "ok" and r["correct"] == r.get("natural_correct"))
    pairs: dict[tuple[str, int], dict[int, dict[str, Any]]] = defaultdict(dict)
    for r in recs:
        pairs[(r["item_id"], r.get("source_sample", 0))][r.get("forced_sample", 0)] = r
    both = [v for v in pairs.values() if 0 in v and 1 in v and v[0]["category"] == "ok" and v[1]["category"] == "ok"]
    rep = sum(1 for v in both if v[0]["answer_key"] == v[1]["answer_key"])
    return {"forced": len(recs), "natural_ok": len(nat_ok), "same_answer": same, "same_answer_pct": pct(same, len(nat_ok)),
            "same_correctness": same_corr, "same_correctness_pct": pct(same_corr, len(nat_ok)),
            "parsed": sum(1 for r in recs if r["category"] == "ok"),
            "renewed_reasoning": sum(1 for r in recs if r.get("reasoning_returned")),
            "repeat_pairs_both_ok": len(both), "repeat_same_answer": rep, "repeat_pct": pct(rep, len(both))}


def cut_stats(recs: list[dict[str, Any]], raw: list[dict[str, Any]]) -> dict[str, int]:
    empty = 0
    for r in raw:
        resp = r.get("response") or {}
        ch = (resp.get("choices") or [{}])[0]
        if not (ch.get("text") or "").strip() and not resp.get("usage"):
            empty += 1
    return {"forced": len(recs),
            "answered": sum(1 for r in recs if not r["truncated"] and r["category"] != "api_error" and r["content_chars"]),
            "parsed": sum(1 for r in recs if r["category"] == "ok"),
            "still_writing": sum(1 for r in recs if r["truncated"]),
            "renewed_reasoning": sum(1 for r in recs if r.get("reasoning_returned")),
            "provider_empty": empty}


def compute(root: Path = ROOT) -> dict[str, Any]:
    out: dict[str, Any] = {"description": "Acceptance tests of force-2; see the docstring of analysis/forcing_acceptance.py",
                           "passes": {}, "by_model": {}}
    done_by: dict[str, list[dict[str, Any]]] = defaultdict(list)
    cut_by: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for sel in ("done", "cut"):
        for d in sorted((root / sel).iterdir()) if (root / sel).exists() else []:
            recs = read(d / "scored.jsonl.gz")
            m = model_of(d.name)
            if sel == "done":
                out["passes"][f"{sel}/{d.name}"] = done_stats(recs)
                done_by[m] += recs
            else:
                s = cut_stats(recs, read(d / "raw.jsonl.gz"))
                out["passes"][f"{sel}/{d.name}"] = s
                for k, v in s.items():
                    cut_by[m][k] += v
    for m in sorted(set(done_by) | set(cut_by)):
        c = dict(cut_by.get(m, {}))
        if c:
            c.update({"answered_pct": pct(c["answered"], c["forced"]), "parsed_pct": pct(c["parsed"], c["forced"]),
                      "parsed_pct_without_provider_empty": pct(c["parsed"], c["forced"] - c["provider_empty"])})
        out["by_model"][m] = {"done": done_stats(done_by[m]) if m in done_by else None, "cut": c or None}
    return out


def table(res: dict[str, Any]) -> str:
    L = ["| Model | f = 1: same answer | f = 1: same correctness | Repeatable | Cut: answered | Cut: parsed | Renewed reasoning |",
         "|---|---|---|---|---|---|---|"]
    for m, v in res["by_model"].items():
        d, c = v["done"] or {}, v["cut"] or {}
        L.append(f"| {m} | {d.get('same_answer')}/{d.get('natural_ok')} ({d.get('same_answer_pct')}%) "
                 f"| {d.get('same_correctness')}/{d.get('natural_ok')} ({d.get('same_correctness_pct')}%) "
                 f"| {d.get('repeat_same_answer')}/{d.get('repeat_pairs_both_ok')} "
                 f"| {c.get('answered')}/{c.get('forced')} ({c.get('answered_pct')}%) "
                 f"| {c.get('parsed')}/{c.get('forced')} ({c.get('parsed_pct')}%) "
                 f"| {d.get('renewed_reasoning', 0) + c.get('renewed_reasoning', 0)} |")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="recompute and compare with the committed JSON; write nothing")
    a = ap.parse_args(argv)
    res = compute()
    text = json.dumps(res, indent=1, sort_keys=True) + "\n"
    if a.check:
        if not OUT.exists() or OUT.read_text() != text:
            print(f"{OUT} differs from a fresh run of analysis/forcing_acceptance.py", file=sys.stderr)
            return 1
        print("forcing acceptance matches the committed JSON")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print(table(res))
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
