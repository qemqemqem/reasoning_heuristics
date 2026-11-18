"""Command-line entry point for the Stage 1 generators.

    python -m reasoning_heuristics.generate --vertical C --eval E1 --tier dev --seed 1
    python -m reasoning_heuristics.generate --vertical B4 --eval E1 --tier smoke --seed 1 --set n_frames=2

Writes data/items/<tier>/<VERTICAL>_<EVAL>_<tier>_s<seed>.jsonl and a .report.json with the
generator's selection statistics and the validator report. Exits non-zero if any item or
set fails validation (the items are still written, so the failure can be inspected).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from reasoning_heuristics.generators import canonical_vertical, load
from reasoning_heuristics.schema.item import write_jsonl
from reasoning_heuristics.seeds import TIERS
from reasoning_heuristics.validate.checks import run_checks

ROOT = Path(__file__).resolve().parents[2]


def parse_set(values: list[str]) -> dict:
    out = {}
    for v in values:
        k, _, raw = v.partition("=")
        try:
            out[k] = json.loads(raw)
        except json.JSONDecodeError:
            out[k] = raw
    return out


def output_path(out_dir: Path, vertical: str, eval_id: str, tier: str, seed: int) -> Path:
    return out_dir / tier / f"{vertical.replace('/', '')}_{eval_id}_{tier}_s{seed}.jsonl"


def generate_and_validate(vertical: str, eval_id: str, tier: str, seed: int, per_cell: int | None,
                          params: dict, out_dir: Path, validate: bool = True) -> dict:
    mod = load(vertical, eval_id)
    t0 = time.time()
    items, stats = mod.generate(tier, seed, per_cell, **params)
    gen_seconds = time.time() - t0
    path = output_path(out_dir, mod.VERTICAL, mod.EVAL_ID, tier, seed)
    write_jsonl(items, path)
    report = {"vertical": mod.VERTICAL, "eval_id": mod.EVAL_ID, "tier": tier, "seed": seed,
              "per_cell": per_cell or TIERS[tier].default_per_cell, "params": params,
              "cells": mod.cells(params), "generation": stats, "generation_seconds": round(gen_seconds, 1),
              "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)}
    if validate:
        t1 = time.time()
        report["validation"] = run_checks(items, mod.check_set)
        report["validation_seconds"] = round(time.time() - t1, 1)
    path.with_suffix(".report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vertical", required=True, help="A/H, C or B4/C4 (aliases AH, B4)")
    ap.add_argument("--eval", required=True, dest="eval_id")
    ap.add_argument("--tier", required=True, choices=sorted(TIERS))
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--per-cell", type=int, default=None, help="items per design cell (smoke 1, dev 5 by default)")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="generator parameter (JSON value)")
    ap.add_argument("--out-dir", type=Path, default=ROOT / "data" / "items")
    ap.add_argument("--no-validate", action="store_true")
    args = ap.parse_args(argv)
    report = generate_and_validate(canonical_vertical(args.vertical), args.eval_id.upper(), args.tier, args.seed,
                                   args.per_cell, parse_set(args.set), args.out_dir, not args.no_validate)
    v = report.get("validation")
    print(f"{report['vertical']} {report['eval_id']} {args.tier}: {report['generation']['accepted']} sets, "
          f"{v['items'] if v else '?'} items -> {report['path']}")
    if v:
        print(f"validation: {v['items_passed']}/{v['items']} items pass ({len(v['failures'])} failures)")
        for f in v["failures"][:20]:
            print("  FAIL", f["item_id"], f["check"], f["message"])
        return 0 if not v["failures"] else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
