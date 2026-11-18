"""The recovery harness (SCOPE §4 item 5; the Stage 0 gate): fake models with planted mixtures are
fitted, and the estimates are compared with the planted weights.

    python -m reasoning_heuristics.identify.recovery run --items data/items/dev --out data/recovery/dev.json
    python -m reasoning_heuristics.identify.recovery run --items <dir with larger sets> --label pc20 --scenarios mix,null_q
    python -m reasoning_heuristics.identify.recovery table data/recovery/dev.json [more.json ...]

`run` fits every scenario of `fake.py` on every fit unit (eval x domain) of the item sets it is
given and writes one JSON file; `table` prints the gate tables in Markdown. Rerun it on
regenerated item sets with the same command: nothing in it is tuned to the current items.

**Gates** (SCOPE §4 item 5), per unit and scenario, over replicates:

- bias: |mean(pi_hat) - pi_true| <= 0.05 for every reported quantity (every tie group and the
  unexplained mass, planted or absent);
- coverage: the 95% interval contains the planted value in >= 90% of replicates, for every planted
  quantity (pi_true > 0);
- width: the median 95% interval width over planted quantities and replicates is <= 0.2.

**The planted triple** for `mix`, `feature`, `clustered`, `truncated` and `off_zoo` is chosen by a
rule, not by hand: h1 (0.6) is the first group of the largest family; h2 (0.3) is h1's nearest
competitor (the group with the fewest separating items, > 0); h3 (0.1) is the group of another
family that is most separated from both. Only groups available on every item are planted.

**Feature levels** (`feature`): the first factor of the cell label that takes exactly two values
in the unit (cells split on "/" and "·"); if there is none, the cells are split into two halves in
sorted order.
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from reasoning_heuristics.identify.engine import separations
from reasoning_heuristics.identify.fake import Scenario, always_answer, simulate, truth_vector
from reasoning_heuristics.identify.likelihood import NEAR_MISS, UNIFORM, TruncationTable, UnitModel
from reasoning_heuristics.identify.mixture import UNEXPLAINED, em, fit, fit_features
from reasoning_heuristics.identify.units import Unit, load_items, make_units

GATES = {"bias": 0.05, "coverage": 0.90, "width": 0.20}
ALL_SCENARIOS = ("single", "mix", "feature", "null_q", "null_always", "off_zoo", "clustered", "truncated", "misspec")
# the scenarios SCOPE §4 item 5 gates (off_zoo has its own criterion; clustered, truncated and misspec are checks)
GATED = ("single", "mix", "mix_uniform_slips", "feature", "null_q", "null_always")


# =============================================================================================
# Planted members
# =============================================================================================


def full_columns(um: UnitModel) -> list[int]:
    return [j for j, g in enumerate(um.columns) if all(um.pred(i, g.members[0]).available for i in range(len(um.items)))]


def family_of(um: UnitModel, label: str) -> str:
    return um.unit.families().get(label, "?")


def choose_triple(um: UnitModel, sep: dict[str, dict[str, int]]) -> list[str] | None:
    """h1, h2 from deterministic groups when there are enough (procedures, not noise models), h3 any group."""
    cols = um.columns
    full = full_columns(um)
    if len(full) < 3:
        return None
    det = [j for j in full if all(um.pred(i, cols[j].members[0]).kind == "det" for i in range(len(um.items)))]
    pool = det if len(det) >= 2 else full
    fams = Counter(family_of(um, cols[j].members[0]) for j in pool)
    order = sorted(pool, key=lambda j: (-fams[family_of(um, cols[j].members[0])], j))
    h1 = order[0]
    rest = [j for j in pool if j != h1 and sep[cols[h1].name][cols[j].name] > 0]
    if not rest:
        return None
    h2 = min(rest, key=lambda j: (sep[cols[h1].name][cols[j].name], j))
    f12 = {family_of(um, cols[h1].members[0]), family_of(um, cols[h2].members[0])}
    others = [j for j in full if j not in (h1, h2)]
    if not others:
        return None
    cross = [j for j in others if family_of(um, cols[j].members[0]) not in f12] or others
    h3 = max(cross, key=lambda j: (min(sep[cols[h1].name][cols[j].name], sep[cols[h2].name][cols[j].name]), -j))
    return [cols[h1].members[0], cols[h2].members[0], cols[h3].members[0]]


def feature_levels(unit: Unit) -> tuple[np.ndarray, str]:
    import re

    cells = [it["cell"] for it in unit.items]
    parts = [re.split(r"[/·]", c) for c in cells]
    width = min(len(p) for p in parts)
    for k in range(width):
        vals = sorted({p[k] for p in parts})
        if len(vals) == 2:
            return np.array([vals.index(p[k]) for p in parts]), f"cell factor {k}: {vals[0]} (0) vs {vals[1]} (1)"
    uniq = sorted(set(cells))
    half = {c: int(i >= len(uniq) / 2) for i, c in enumerate(uniq)}
    return np.array([half[c] for c in cells]), "cells split in two halves (sorted)"


# =============================================================================================
# Metrics
# =============================================================================================


def summarise(truths: np.ndarray, ests: np.ndarray, los: np.ndarray, his: np.ndarray, labels: list[str]) -> dict[str, Any]:
    """Bias, coverage and width per quantity over replicates (rows), and the three gates."""
    truths, ests, los, his = map(np.asarray, (truths, ests, los, his))
    bias = (ests - truths).mean(0)
    cover = ((los <= truths + 1e-9) & (truths - 1e-9 <= his)).mean(0)
    width = his - los
    present = truths.mean(0) > 0
    per = {}
    for j, lab in enumerate(labels):
        if present[j] or abs(bias[j]) > 0.01 or his[:, j].mean() > 0.05:
            per[lab] = {"truth": round(float(truths[:, j].mean()), 3), "mean": round(float(ests[:, j].mean()), 3),
                        "bias": round(float(bias[j]), 3), "coverage": round(float(cover[j]), 3),
                        "median_width": round(float(np.median(width[:, j])), 3),
                        "mean_upper": round(float(his[:, j].mean()), 3)}
    worst_bias = float(np.abs(bias).max())
    min_cov = float(cover[present].min()) if present.any() else float("nan")
    med_width = float(np.median(width[:, present])) if present.any() else float("nan")
    gates = {"bias": worst_bias <= GATES["bias"], "coverage": min_cov >= GATES["coverage"],
             "width": med_width <= GATES["width"]}
    worst = labels[int(np.abs(bias).argmax())]
    worst_cov = labels[int(np.where(present)[0][np.argmin(cover[present])])] if present.any() else None
    return {"max_abs_bias": round(worst_bias, 3), "worst_bias_quantity": worst, "min_coverage": round(min_cov, 3),
            "worst_coverage_quantity": worst_cov, "median_width": round(med_width, 3), "gates": gates,
            "pass": all(gates.values()), "quantities": per, "replicates": int(truths.shape[0])}


def point_summary(truths: np.ndarray, ests: np.ndarray, labels: list[str]) -> dict[str, Any]:
    bias = (np.asarray(ests) - np.asarray(truths)).mean(0)
    return {"bias": {l: round(float(b), 3) for l, b in zip(labels, bias) if abs(b) > 0.005},
            "max_abs_bias": round(float(np.abs(bias).max()), 3)}


# =============================================================================================
# One unit
# =============================================================================================


def _fit(um_fit: UnitModel, obs, rng, n_boot, token_model=None):
    T = um_fit.tensors(obs, token_model)
    return fit(T, n_boot=n_boot, rng=rng)


def run_unit(unit: Unit, cfg: dict[str, Any]) -> dict[str, Any]:
    t0 = time.time()
    rng = np.random.default_rng(cfg["seed"])
    gen = {NEAR_MISS: UnitModel(unit, NEAR_MISS), UNIFORM: UnitModel(unit, UNIFORM)}
    fitm = gen  # the full zoo is both generator and fit, except off_zoo
    um = gen[NEAR_MISS]
    sep = separations(um)
    labels = [g.name for g in um.columns] + [UNEXPLAINED]
    finite = all(type(im.space).__name__ == "FiniteSpace" for im in um.items)
    out: dict[str, Any] = {"unit": unit.name, "n_items": len(unit.items), "n_clusters": unit.n_clusters,
                           "n_cells": len(set(unit.cells)), "items_per_cell": round(len(unit.items) / len(set(unit.cells)), 2),
                           "finite_channel": finite, "groups": [g.members for g in um.columns], "folded_into_q": um.q_members,
                           "scenarios": {}}
    triple = choose_triple(um, sep)
    out["triple"] = triple
    R, B = cfg["reps"], cfg["boot"]
    scen = cfg["scenarios"]

    def replicate(sc: Scenario, gen_model: str, fit_model: str, reps: int, boot: int, token=False, levels=None):
        truths, ests, los, his = [], [], [], []
        for _ in range(reps):
            obs = simulate(gen[gen_model], sc, rng, levels)
            tm = None
            if sc.truncation is not None and token:
                table = {}
                for i, it in enumerate(unit.items):
                    for g in fitm[fit_model].columns:
                        table[(it["item_id"], g.members[0])] = sc.truncation.get(g.members[0], sc.trunc_default)
                    table[(it["item_id"], None)] = sc.trunc_default
                tm = TruncationTable(table, sc.trunc_default)
            if sc.truncation is not None and not token:
                obs = [o for o in obs if not o.censored]
            res = _fit(fitm[fit_model], obs, rng, boot, tm)
            truths.append(truth_vector(fitm[fit_model], sc.weights, sc.q))
            ests.append(res.pi)
            los.append(res.lo)
            his.append(res.hi)
        return summarise(np.array(truths), np.array(ests), np.array(los), np.array(his), labels)

    if "single" in scen:
        rows = {}
        for j, g in enumerate(um.columns):
            full = j in full_columns(um)
            sc = Scenario(f"single:{g.name}", "single", {g.members[0]: 1.0 if full else 0.95}, q=0.0 if full else 0.05)
            rows[g.name] = replicate(sc, NEAR_MISS, NEAR_MISS, cfg["single_reps"], B)
        out["scenarios"]["single"] = {"by_group": rows, "pass": all(r["pass"] for r in rows.values()),
                                      "failing": [k for k, r in rows.items() if not r["pass"]]}
    if triple:
        w = dict(zip(triple, (0.6, 0.3, 0.1)))
        if "mix" in scen:
            out["scenarios"]["mix"] = replicate(Scenario("mix", "mix", w), NEAR_MISS, NEAR_MISS, R, B)
            if not finite:
                out["scenarios"]["mix_uniform_slips"] = replicate(Scenario("mix", "mix", w), UNIFORM, UNIFORM, R, B)
        if "misspec" in scen and not finite:
            out["scenarios"]["misspec_uniform_fit_on_near_miss"] = replicate(Scenario("mix", "mix", w), NEAR_MISS, UNIFORM, R, B)
            out["scenarios"]["misspec_near_miss_fit_on_uniform"] = replicate(Scenario("mix", "mix", w), UNIFORM, NEAR_MISS, R, B)
        if "clustered" in scen:
            out["scenarios"]["clustered"] = replicate(Scenario("clustered", "mix", w, clustered=True), NEAR_MISS, NEAR_MISS, R, B)
        if "truncated" in scen:
            trunc = {triple[0]: 0.4}
            sc = Scenario("truncated", "mix", w, truncation=trunc)
            out["scenarios"]["truncated_excluded"] = replicate(sc, NEAR_MISS, NEAR_MISS, R, B, token=False)
            out["scenarios"]["truncated_token_model"] = replicate(sc, NEAR_MISS, NEAR_MISS, R, B, token=True)
        if "feature" in scen:
            levels, desc = feature_levels(unit)
            lw = {0: dict(zip(triple, (0.7, 0.2, 0.1))), 1: dict(zip(triple, (0.2, 0.7, 0.1)))}
            sc = Scenario("feature", "feature", level_weights=lw)
            truths, ests, los, his = [], [], [], []
            for _ in range(cfg["feature_reps"]):
                obs = simulate(um, sc, rng, levels)
                T = um.tensors(obs)
                X = np.stack([np.ones(T.n), levels[T.item]], 1).astype(float)
                fr = fit_features(T, X, np.array([[1.0, 0.0], [1.0, 1.0]]), n_boot=cfg["feature_boot"], rng=rng)
                for lev in (0, 1):
                    truths.append(truth_vector(um, lw[lev], 0.0))
                    ests.append(fr["pi"][lev])
                    los.append(fr["lo"][lev])
                    his.append(fr["hi"][lev])
            res = summarise(np.array(truths), np.array(ests), np.array(los), np.array(his), labels)
            res["feature"] = desc
            out["scenarios"]["feature"] = res
        if "off_zoo" in scen:
            rows = {}
            for g in um.columns:
                if triple[0] in g.members:
                    continue
                if not all(um.pred(i, g.members[0]).available for i in range(len(um.items))):
                    continue
                keep = [l for l in um.labels if l not in g.members]
                um_fit = UnitModel(unit, NEAR_MISS, labels=keep)
                fl = [c.name for c in um_fit.columns] + [UNEXPLAINED]
                sc = Scenario(f"off_zoo:{g.name}", "off_zoo", {triple[0]: 0.7, g.members[0]: 0.3}, withheld=g.members)
                ests = []
                for _ in range(cfg["offzoo_reps"]):
                    obs = simulate(um, sc, rng)
                    ests.append(em(um_fit.tensors(obs)).pi[0])
                ests = np.array(ests).mean(0)
                j1 = um_fit.column_of(triple[0])
                others = [(fl[j], float(ests[j])) for j in range(len(fl) - 1) if j != j1]
                top = max(others, key=lambda kv: kv[1]) if others else (None, 0.0)
                rows[g.name] = {"to_q": round(float(ests[-1]), 3), "to_h1_excess": round(float(ests[j1] - 0.7), 3) if j1 is not None else None,
                                "to_other_members": round(sum(v for _, v in others), 3),
                                "largest_single_member": top[0], "largest_single_share": round(top[1], 3),
                                "share_of_withheld_on_one_member": round(max(top[1], float(ests[j1] - 0.7) if j1 is not None else 0) / 0.3, 3)}
            out["scenarios"]["off_zoo"] = {"by_withheld_group": rows,
                                           "criterion": "< 0.2 of the withheld 0.3 on any single zoo member (A/H §5.3 P6)",
                                           "pass": all(r["share_of_withheld_on_one_member"] < 0.2 for r in rows.values()),
                                           "failing": [k for k, r in rows.items() if r["share_of_withheld_on_one_member"] >= 0.2]}
    if "null_q" in scen:
        out["scenarios"]["null_q"] = replicate(Scenario("null_q", "null_q", {}, q=1.0), NEAR_MISS, NEAR_MISS, R, B)
    if "null_always" in scen:
        sc = Scenario("null_always", "null_always", always=True)
        target = None
        for j, g in enumerate(um.columns):
            if all(um.pred(i, g.members[0]).kind == "det" and um.pred(i, g.members[0]).key == always_answer(um, i)
                   for i in range(len(um.items))):
                target = g.members[0]
        sc.weights, sc.q = ({target: 1.0}, 0.0) if target else ({}, 1.0)
        res = replicate(sc, NEAR_MISS, NEAR_MISS, max(3, R // 10), B)
        res["truth_group"] = target or UNEXPLAINED
        out["scenarios"]["null_always"] = res
    gated = [v["pass"] for k, v in out["scenarios"].items() if k in GATED]
    out["all_gates_pass"] = bool(gated) and all(gated)
    out["seconds"] = round(time.time() - t0, 1)
    return out


def _worker(args):
    paths, unit_name, cfg = args
    units = make_units(load_items(paths))
    try:
        return run_unit(units[unit_name], cfg)
    except Exception as e:  # report, do not hide: the failure is part of the output
        import traceback

        return {"unit": unit_name, "error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()}


def provenance(paths: list[Path]) -> dict[str, Any]:
    """The code and the item files a result came from: git SHA (and whether the tree was dirty),
    and the sha256 of every item file read."""
    import hashlib
    import subprocess

    repo = Path(__file__).resolve().parents[3]

    def git(*args: str) -> str | None:
        try:
            return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return None

    status = git("status", "--porcelain", "--untracked-files=no")
    files = {}
    for p in paths:
        rel = str(p.resolve().relative_to(repo)) if p.resolve().is_relative_to(repo) else str(p)
        files[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return {"git_sha": git("rev-parse", "HEAD"), "git_dirty": bool(status) if status is not None else None,
            "item_files": files}


def item_paths(spec: str, evals: list[str] | None) -> list[Path]:
    p = Path(spec)
    paths = sorted(p.rglob("*.jsonl.gz")) if p.is_dir() else [p]
    if not paths and p.is_dir():
        paths = sorted(p.rglob("*.jsonl"))
    if evals:
        paths = [x for x in paths if any(x.name.startswith(e + "_") for e in evals)]
    return [x for x in paths if "_E8_" not in x.name]


def run(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="recovery run")
    ap.add_argument("--items", required=True, help="a directory of item sets (*.jsonl.gz or *.jsonl) or one file")
    ap.add_argument("--evals", default=None, help="comma-separated eval names, e.g. C_E1,AH_E2")
    ap.add_argument("--units", default=None, help="comma-separated unit names (eval/domain)")
    ap.add_argument("--scenarios", default=",".join(ALL_SCENARIOS))
    ap.add_argument("--reps", type=int, default=60)
    ap.add_argument("--boot", type=int, default=150)
    ap.add_argument("--single-reps", type=int, default=20)
    ap.add_argument("--feature-reps", type=int, default=20)
    ap.add_argument("--feature-boot", type=int, default=40)
    ap.add_argument("--offzoo-reps", type=int, default=10)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--workers", type=int, default=max(1, min(6, (os.cpu_count() or 2) - 2)))
    ap.add_argument("--label", default=None, help="a name for this item set (e.g. dev, pc20)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    evals = a.evals.split(",") if a.evals else None
    paths = item_paths(a.items, evals)
    if not paths:
        print("no item sets found", file=sys.stderr)
        return 2
    by_eval: dict[str, list[Path]] = {}
    for p in paths:
        by_eval.setdefault("_".join(p.name.split("_")[:2]), []).append(p)
    cfg = {"reps": a.reps, "boot": a.boot, "single_reps": a.single_reps, "feature_reps": a.feature_reps,
           "feature_boot": a.feature_boot, "offzoo_reps": a.offzoo_reps, "seed": a.seed,
           "scenarios": a.scenarios.split(",")}
    tasks = []
    for ev, ps in sorted(by_eval.items()):
        for name in make_units(load_items(ps)):
            if a.units and name not in a.units.split(","):
                continue
            tasks.append((ps, name, cfg))
    # longest first, so the pool is not left waiting on one big unit at the end
    tasks.sort(key=lambda t: -sum(p.stat().st_size for p in t[0]))
    t0 = time.time()
    results = []
    with mp.get_context("fork").Pool(a.workers) as pool:
        for r in pool.imap_unordered(_worker, tasks):
            results.append(r)
            status = "ERROR " + r["error"] if "error" in r else ("PASS" if r.get("all_gates_pass") else "fail")
            print(f"[{time.time() - t0:7.0f}s] {r['unit']}: {status} ({r.get('seconds', '?')}s)", flush=True)
    results.sort(key=lambda r: r["unit"])
    doc = {"label": a.label or Path(a.items).name, "items": str(a.items), "config": cfg, "gates": GATES,
           "generated": time.strftime("%Y-%m-%d %H:%M"), "provenance": provenance(paths),
           "command": "python -m reasoning_heuristics.identify.recovery run " + " ".join(argv), "units": results}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(doc, indent=1, ensure_ascii=False))
    print(f"wrote {a.out}")
    return 0


# =============================================================================================
# Tables
# =============================================================================================


def _mark(res: dict[str, Any] | None) -> str:
    if res is None:
        return "–"
    if "gates" not in res:
        return "PASS" if res.get("pass") else "fail"
    g = res["gates"]
    if res["pass"]:
        return "PASS"
    return "fail (" + ", ".join(k for k in ("bias", "coverage", "width") if not g[k]) + ")"


def table(paths: list[str]) -> str:
    lines = []
    for path in paths:
        doc = json.loads(Path(path).read_text())
        lines.append(f"### {doc['label']} ({doc['items']})\n")
        lines.append("| Unit | items/cell | single | mix 60/30/10 | feature | null q | null ALWAYS | clustered | max \\|bias\\| (mix) | coverage (mix) | width (mix) |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for u in doc["units"]:
            if "error" in u:
                lines.append(f"| {u['unit']} | error: {u['error'][:60]} |||||||||")
                continue
            s = u["scenarios"]
            single = s.get("single")
            sm = "PASS" if single and single["pass"] else (f"fail ({len(single['failing'])}/{len(single['by_group'])})" if single else "–")
            mix = s.get("mix")
            lines.append(f"| {u['unit']} | {u['items_per_cell']} | {sm} | {_mark(mix)} | {_mark(s.get('feature'))} | "
                         f"{_mark(s.get('null_q'))} | {_mark(s.get('null_always'))} | {_mark(s.get('clustered'))} | "
                         f"{mix['max_abs_bias'] if mix else '–'} | {mix['min_coverage'] if mix else '–'} | {mix['median_width'] if mix else '–'} |")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in ("run", "table"):
        print(__doc__)
        return 2
    if argv[0] == "run":
        return run(argv[1:])
    print(table(argv[1:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
