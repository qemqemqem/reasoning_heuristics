"""Accuracy under a thinking budget, from the committed budget-forcing passes (evals/force.py --truncate-at and
--truncate-frac; docs/RUNNER.md, "Budget forcing and early answering").

    python analysis/budget_sweep.py            # writes analysis/out/budget_sweep.json and budget_sweep.md, prints the table
    python analysis/budget_sweep.py --check    # recompute and compare with the committed files; writes nothing

It reads data/runs/forced-2/<select>-k<K>/<source>/ and <select>-f<F>/<source>/ (manifest.json, budget.jsonl.gz,
scored.jsonl.gz) and each pass's source run, data/runs/<source>/scored.jsonl.gz, nothing else. A pass is one model on
one item set (its source run) at one budget, so rows are kept apart by source run and selection, then per unit
(vertical, eval, item domain) and budget:

- items: the selected traces (budget.jsonl.gz), each item once;
- within_budget: traces of at most K tokens, which were not sent: the natural answer stands, as a finished
  response's would under that budget (a fraction below 1 always cuts, so an f-budget has none);
- forced: traces cut and sent; answered: forced answers that stopped by themselves with a reply; parsed: forced
  answers whose category is ok;
- correct: each item once, the natural answer if its trace fit within the budget, else the forced answer at it
  (forced sample 0). A forced answer that did not parse counts as not correct (forced - parsed of them), as does
  a natural answer that is not ok (a response cut at the source's cap has none) and a trace the pass skipped for
  want of room in the context (no_room) or whose call failed (missing);
- accuracy: correct / items; natural_correct: the same items' natural answers at the source run's own cap, for
  comparison.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "data" / "runs"
OUT_JSON = REPO / "analysis" / "out" / "budget_sweep.json"
OUT_MD = REPO / "analysis" / "out" / "budget_sweep.md"
PASS_DIR = re.compile(r"^(cut|done|all)-(k\d+|f\d+(?:\.\d+)?)$")  # force.py's <select>-<budget label>
COLUMNS = ("items", "within_budget", "forced", "answered", "parsed", "correct", "no_room", "missing", "natural_correct")


def read(p: Path) -> list[dict[str, Any]]:
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def budget_order(label: str) -> tuple[int, float]:
    """k-budgets by K, then f-budgets by F."""
    return (0 if label[0] == "k" else 1, float(label[1:]))


def ok_and_correct(r: dict[str, Any] | None) -> bool:
    return r is not None and r.get("category") == "ok" and r.get("correct") is True


def pass_dirs(runs: Path) -> list[tuple[str, str, Path]]:
    """(select, budget label, pass directory) of every committed budget pass, in order."""
    root, out = runs / "forced-2", []
    for d in sorted(root.iterdir()) if root.exists() else []:
        m = PASS_DIR.match(d.name)
        if m and d.is_dir():
            out += [(m.group(1), m.group(2), p) for p in sorted(d.iterdir()) if (p / "manifest.json").exists()]
    return out


def compute(runs: Path = RUNS) -> dict[str, Any]:
    res: dict[str, Any] = {"description": "Accuracy under a thinking budget; see the docstring of analysis/budget_sweep.py",
                           "passes": {}, "groups": []}
    sources: dict[str, dict[tuple[str, int], dict[str, Any]]] = {}
    groups: dict[tuple[str, str, str], dict[tuple[str, str], dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: dict.fromkeys(COLUMNS, 0)))
    for select, label, d in pass_dirs(runs):
        manifest = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
        source = manifest["source"]["run_id"]
        if source not in sources:
            sources[source] = {(r["item_id"], r.get("sample", 0)): r for r in read(runs / source / "scored.jsonl.gz")}
        natural = sources[source]
        forced = {(r["item_id"], r.get("source_sample", 0)): r for r in read(d / "scored.jsonl.gz")
                  if r.get("forced_sample", 0) == 0}
        rows = groups[(manifest["model_requested"], source, select)]
        for b in read(d / "budget.jsonl.gz"):
            key = (b["item_id"], b["source_sample"])
            nat, f = natural[key], forced.get(key)
            unit = " ".join((nat["vertical"], nat["eval_id"], nat["item_domain"]))
            for row in (rows[("all units", label)], rows[(unit, label)]):
                row["items"] += 1
                row["natural_correct"] += ok_and_correct(nat)
                if b["status"] == "within_budget":
                    row["within_budget"] += 1
                    row["correct"] += ok_and_correct(nat)
                elif b["status"] == "no_room":
                    row["no_room"] += 1
                elif f is None:  # sent, but no forced answer recorded: the pass is incomplete
                    row["forced"] += 1
                    row["missing"] += 1
                else:
                    row["forced"] += 1
                    row["answered"] += bool(not f["truncated"] and f["category"] != "api_error" and f["content_chars"])
                    row["parsed"] += f["category"] == "ok"
                    row["correct"] += ok_and_correct(f)
        res["passes"][f"{d.parent.name}/{d.name}"] = {"model": manifest["model_requested"], "status": manifest.get("status"),
                                                      "counts": {k: manifest["counts"].get(k) for k in (
                                                          "selected", "within_budget", "sent", "responses")}}
    for (model, source, select), rows in sorted(groups.items()):
        res["groups"].append({"model": model, "source_run_id": source, "select": select, "rows": [
            {"unit": unit, "budget": label, **row,
             "accuracy": round(row["correct"] / row["items"], 4) if row["items"] else None}
            for (unit, label), row in sorted(rows.items(), key=lambda kv: (kv[0][0] != "all units", kv[0][0],
                                                                         budget_order(kv[0][1])))]})
    return res


def table(res: dict[str, Any]) -> str:
    L = ["# Budget sweep", "",
         "Written by `analysis/budget_sweep.py` from the committed budget-forcing passes (docs/RUNNER.md, \"Budget forcing "
         "and early answering\"). Accuracy at a budget counts each item once: the natural answer if its trace fit within "
         "the budget, else the forced answer there. A forced answer that did not parse counts as not correct (forced − "
         "parsed). Natural correct is the same items at the source run's own cap.", ""]
    if not res["groups"]:
        return "\n".join(L + ["No budget-forcing passes are committed yet.", ""])
    for g in res["groups"]:
        L += [f"## {g['model']}: `{g['source_run_id']}`, select {g['select']}", "",
              "| Unit | Budget | Items | Within budget | Forced | Answered | Parsed | Correct | Accuracy | No room | Missing | Natural correct |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in g["rows"]:
            L.append(f"| {r['unit']} | {r['budget']} | {r['items']} | {r['within_budget']} | {r['forced']} | {r['answered']} | "
                     f"{r['parsed']} | {r['correct']} | {r['accuracy']:.3f} | {r['no_room']} | {r['missing']} | "
                     f"{r['natural_correct']} |")
        L.append("")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="recompute and compare with the committed files; write nothing")
    a = ap.parse_args(argv)
    res = compute()
    text, md = json.dumps(res, indent=1, sort_keys=True) + "\n", table(res)
    if a.check:
        if not res["passes"] and not OUT_JSON.exists() and not OUT_MD.exists():
            print("no budget-forcing passes are committed; nothing to check")
            return 0
        for path, want in ((OUT_JSON, text), (OUT_MD, md)):
            if not path.exists() or path.read_text(encoding="utf-8") != want:
                print(f"{path} differs from a fresh run of analysis/budget_sweep.py", file=sys.stderr)
                return 1
        print("the budget sweep matches the committed files")
        return 0
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(text, encoding="utf-8")
    OUT_MD.write_text(md, encoding="utf-8")
    print(md)
    print(f"wrote {OUT_JSON} and {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
