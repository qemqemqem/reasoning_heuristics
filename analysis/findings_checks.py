"""Checks behind the hand-written claims in docs/results/findings.html that the main analysis does not compute.

    python analysis/findings_checks.py            # writes analysis/out/findings_checks.json (about a minute)

It reads the committed item sets and the scored pilot runs (data/runs/2026-11-18-{pc20,pc40}-*), nothing else.
Each check answers a question a sceptical reader asked of the first draft (2026-11-18):

1. knapsack_near_optimality (pc20 C E2 knapsack). Is the agreement of wrong packings with greedy rules more than
   near-optimal answers would give? On these items the greedy rules are wrong by design, so their packings are
   often the runner-up by value. For each run: the value rank of every wrong ok answer among the feasible packings
   (dense, 1 = optimal); the wrong answers equal to some greedy member's packing; the number a null predicts
   that keeps the run's own distribution of ranks but ignores which packings are greedy; and the runner-up
   contrast (how often a wrong answer is the runner-up when the runner-up is a greedy packing, and when not).
2. colouring_ro_ff_chance (pc20 C E2 colouring). A structure-matched chance level for the colouring agreement:
   the probability that a random-order first fit (the stored RO-FF distribution, 10,000 samples per item) gives
   each deterministic member's wrong colouring, summed over the items where the model and the member are both
   wrong, next to the observed count.
3. impossible_by_cell (pc40 C E5). IMPOSSIBLE answers on the 3-colouring CONTROL graphs (where list-order greedy
   succeeds) against the STUCK graphs; UNSAT answers on the 3-SAT cells likewise.
4. textbook_paired (pc20 A/H E5). Per run and domain, textbook answers under I against I+R, paired by base
   instance, with an exact McNemar test.
5. size_paired (pc20 and pc40). gpt-oss-120b against gpt-oss-20b at low effort, per unit, correctness paired by
   item (both ok), with an exact McNemar test.
"""

from __future__ import annotations

import argparse
import gzip
import itertools
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from reasoning_heuristics.heuristics.answers import answer_key
from reasoning_heuristics.heuristics.tasks import load_task

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "analysis" / "out" / "findings_checks.json"
COLOUR_MEMBERS = ("FF-LIST", "FF-LABEL", "LF", "DSATUR", "DSATUR-LABEL")


def load_items(item_set: str) -> dict[str, dict[str, Any]]:
    out = {}
    for p in sorted((REPO / "data" / "items" / item_set).glob("*.jsonl.gz")):
        for line in gzip.open(p, "rt", encoding="utf-8"):
            if line.strip():
                it = json.loads(line)
                out[it["item_id"]] = it
    return out


def load_runs(item_set: str, runs_root: Path) -> dict[str, list[dict[str, Any]]]:
    out = {}
    for d in sorted(runs_root.glob(f"2026-11-18-{item_set}-*")):
        f = d / "scored.jsonl.gz"
        if f.exists():
            out[d.name.replace("2026-11-18-", "")] = [json.loads(l) for l in gzip.open(f, "rt", encoding="utf-8") if l.strip()]
    return out


def mcnemar(b: int, c: int) -> float:
    """Exact two-sided McNemar p-value for b and c discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def is_textbook(r: dict[str, Any]) -> bool:
    return any(m.startswith("A3") for m in (r.get("members_matched") or []) + (r.get("sets_matched") or []))


# --- 1. knapsack -------------------------------------------------------------------------------


def knapsack_table(it: dict[str, Any]) -> dict[str, Any]:
    """Every feasible packing of an item with its dense value rank, and the greedy members' packings."""
    kn = load_task(it["instance"]).knapsack
    names = list(kn.names)
    vals = dict(zip(names, kn.values))
    wts = dict(zip(names, kn.weights))
    feas = {}
    for k in range(len(names) + 1):
        for combo in itertools.combinations(names, k):
            if sum(wts[n] for n in combo) <= kn.capacity:
                feas[frozenset(combo)] = sum(vals[n] for n in combo)
    distinct = sorted(set(feas.values()), reverse=True)
    rank_of_value = {v: i + 1 for i, v in enumerate(distinct)}
    rank = {s: rank_of_value[v] for s, v in feas.items()}
    greedy = {frozenset(p["answer"]) for m, p in it["predictions"].items()
              if m != "EXACT" and isinstance(p.get("answer"), list)}
    members = {frozenset(p["answer"]) for p in it["predictions"].values() if isinstance(p.get("answer"), list)}
    by_rank: dict[int, list[frozenset]] = defaultdict(list)
    for s, r in rank.items():
        by_rank[r].append(s)
    return {"rank": rank, "greedy": greedy, "members": members, "by_rank": by_rank}


def swap_of_nearest(t: dict[str, Any], s: frozenset) -> tuple[int, bool]:
    """Distance (items toggled) to the nearest member's packing, and whether a distance-2 answer is a one-for-one swap
    of some nearest member's packing (one item out, one in) rather than two items added or dropped."""
    d = min(len(s ^ m) for m in t["members"])
    swap = d == 2 and any(len(s ^ m) == 2 and len(s - m) == 1 and len(m - s) == 1 for m in t["members"])
    return d, swap


def knapsack_near_optimality(items: dict[str, dict[str, Any]], runs: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    tables = {iid: knapsack_table(it) for iid, it in items.items() if it["domain"] == "knapsack" and it["eval_id"] == "E2"}
    out = {}
    for run, recs in runs.items():
        wrong = [r for r in recs if r["item_id"] in tables and r["category"] == "ok" and r["correct"] is False]
        ranks, greedy_hits, rows, d2 = Counter(), 0, [], Counter()
        for r in wrong:
            t = tables[r["item_id"]]
            s = frozenset(r["parsed"])
            rk = t["rank"].get(s)  # None: infeasible
            ranks[rk if rk is not None else "infeasible"] += 1
            hit = s in t["greedy"]
            greedy_hits += hit
            rows.append((t, rk))
            d, swap = swap_of_nearest(t, s)
            if d == 2:
                d2["distance_2"] += 1
                d2["one_for_one_swap"] += swap
        n = len(wrong)
        p = {k: v / n for k, v in ranks.items()} if n else {}
        expected = 0.0
        for t, _ in rows:
            for rk, pr in p.items():
                if rk == "infeasible" or rk not in t["by_rank"]:
                    continue
                packs = t["by_rank"][rk]
                expected += pr * sum(s in t["greedy"] for s in packs) / len(packs)
        ru = {"runner_up_greedy": Counter(), "runner_up_not_greedy": Counter()}
        for t, rk in rows:
            key = "runner_up_greedy" if any(s in t["greedy"] for s in t["by_rank"].get(2, [])) else "runner_up_not_greedy"
            ru[key]["wrong"] += 1
            ru[key]["answer_is_runner_up"] += rk == 2
        out[run] = {"wrong": n, "equal_to_a_greedy_packing": greedy_hits, "expected_under_rank_null": round(expected, 2),
                    "answer_is_runner_up": ranks.get(2, 0), "infeasible": ranks.get("infeasible", 0),
                    "rank_counts": {str(k): v for k, v in sorted(ranks.items(), key=lambda kv: (isinstance(kv[0], str), kv[0]))},
                    "runner_up_contrast": {k: dict(v) for k, v in ru.items()}, "nearest_member_distance_2": dict(d2)}
    return out


# --- 2. colouring chance from RO-FF -------------------------------------------------------------


def colouring_ro_ff_chance(items: dict[str, dict[str, Any]], runs: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    col = {iid: it for iid, it in items.items() if it["domain"] == "colouring" and it["eval_id"] == "E2"}
    info = {}
    for iid, it in col.items():
        chi = it["ground_truth"].get("chromatic_number")
        dist = it["predictions"]["RO-FF (C3)"]["distribution"]
        mem = {}
        for m in COLOUR_MEMBERS:
            ans = it["predictions"][m]["answer"]
            key = answer_key("coloring", ans)
            mem[m] = {"key": key, "wrong": len(set(ans.values())) > chi, "p_ro_ff": dist.get(key, 0.0)}
        info[iid] = mem
    out = {}
    for run, recs in runs.items():
        res = {m: {"both_wrong": 0, "observed": 0, "expected_ro_ff": 0.0} for m in COLOUR_MEMBERS}
        for r in recs:
            if r["item_id"] not in info or r["category"] != "ok" or r["correct"] is not False:
                continue
            akey = answer_key("coloring", r["parsed"]) if isinstance(r["parsed"], dict) else None
            for m, x in info[r["item_id"]].items():
                if not x["wrong"]:
                    continue
                res[m]["both_wrong"] += 1
                res[m]["observed"] += akey == x["key"]
                res[m]["expected_ro_ff"] += x["p_ro_ff"]
        out[run] = {m: {**v, "expected_ro_ff": round(v["expected_ro_ff"], 2)} for m, v in res.items()}
    return out


# --- 3. impossible by cell ----------------------------------------------------------------------


def impossible_by_cell(runs: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    out = {}
    for run, recs in runs.items():
        c = defaultdict(Counter)
        for r in recs:
            if r["category"] != "ok" or r["item_domain"] not in ("colouring (k=3)", "3-SAT"):
                continue
            kind = r["cell"].split("/")[1]
            key = f"{r['item_domain']} / {kind}"
            c[key]["ok"] += 1
            c[key]["special"] += r["parsed"] in ("IMPOSSIBLE", "UNSAT")
        out[run] = {k: dict(v) for k, v in sorted(c.items())}
    return out


# --- 4. textbook answers, I against I+R ---------------------------------------------------------


def textbook_paired(items: dict[str, dict[str, Any]], runs: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    out = {}
    for run, recs in runs.items():
        by = defaultdict(dict)
        for r in recs:
            it = items.get(r["item_id"])
            if it is None or it["vertical"] != "A/H" or it["eval_id"] != "E5" or r["category"] != "ok":
                continue
            dom, fr = r["cell"].split("/")
            if fr in ("I", "I+R"):
                by[(dom, it["base_hash"])][fr] = is_textbook(r)
        res = {}
        for dom in sorted({d for d, _ in by}):
            pairs = [v for (d, _), v in by.items() if d == dom and len(v) == 2]
            b = sum(1 for v in pairs if v["I"] and not v["I+R"])
            c = sum(1 for v in pairs if not v["I"] and v["I+R"])
            res[dom] = {"pairs": len(pairs), "textbook_I_only": b, "textbook_IR_only": c,
                        "textbook_both": sum(1 for v in pairs if v["I"] and v["I+R"]), "mcnemar_p": float(f"{mcnemar(b, c):.3g}")}
        out[run] = res
    return out


# --- 5. gpt-oss sizes ---------------------------------------------------------------------------


def size_paired(items: dict[str, dict[str, Any]], runs: dict[str, list[dict[str, Any]]], big: str, small: str) -> dict[str, Any]:
    if big not in runs or small not in runs:
        return {}
    def unit(it):
        return f"{'AH' if it['vertical'] == 'A/H' else it['vertical'].replace('/', '')}_{it['eval_id']}/{it['domain']}"
    a = {r["item_id"]: r for r in runs[big] if r["category"] == "ok"}
    b = {r["item_id"]: r for r in runs[small] if r["category"] == "ok"}
    res = defaultdict(Counter)
    for iid in set(a) & set(b):
        u = unit(items[iid])
        ca, cb = bool(a[iid]["correct"]), bool(b[iid]["correct"])
        res[u]["pairs"] += 1
        res[u]["big_correct"] += ca
        res[u]["small_correct"] += cb
        res[u]["big_only"] += ca and not cb
        res[u]["small_only"] += cb and not ca
    return {u: {**dict(v), "mcnemar_p": float(f"{mcnemar(v['big_only'], v['small_only']):.3g}")} for u, v in sorted(res.items())}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--runs-root", type=Path, default=REPO / "data" / "runs")
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--check", action="store_true", help="recompute and compare with --out; write nothing")
    args = ap.parse_args(argv)
    pc20, pc40 = load_items("pc20"), load_items("pc40")
    r20, r40 = load_runs("pc20", args.runs_root), load_runs("pc40", args.runs_root)
    res = {
        "description": "Checks behind docs/results/findings.html; see the docstring of analysis/findings_checks.py",
        "runs": {"pc20": sorted(r20), "pc40": sorted(r40)},
        "knapsack_near_optimality": knapsack_near_optimality(pc20, r20),
        "colouring_ro_ff_chance": colouring_ro_ff_chance(pc20, r20),
        "impossible_by_cell": impossible_by_cell(r40),
        "textbook_paired": textbook_paired(pc20, r20),
        "size_paired": {"pc20": size_paired(pc20, r20, "pc20-gpt-oss-120b-thinking-low", "pc20-gpt-oss-20b-thinking-low"),
                        "pc40": size_paired(pc40, r40, "pc40-gpt-oss-120b-thinking-low", "pc40-gpt-oss-20b-thinking-low")},
    }
    text = json.dumps(res, indent=1, sort_keys=True) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text() != text:
            print(f"{args.out} differs from a fresh run of analysis/findings_checks.py", file=sys.stderr)
            return 1
        print("findings checks match the committed JSON")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
