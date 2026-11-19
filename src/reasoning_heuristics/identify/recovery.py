"""The recovery harness (SCOPE §4 item 5; the Stage 0 gate): fake models with planted mixtures are
fitted, and the estimates are compared with the planted weights.

    python -m reasoning_heuristics.identify.recovery run --items data/items/dev --out data/recovery/dev.json
    python -m reasoning_heuristics.identify.recovery run --items <dir with larger sets> --label pc20 --scenarios mix,null_q
    python -m reasoning_heuristics.identify.recovery table data/recovery/dev.json [more.json ...]
    python -m reasoning_heuristics.identify.recovery report data/recovery/dev.json [sweep.json ...]
    python -m reasoning_heuristics.identify.recovery merge data/recovery/dev.json rerun.json

`run` fits every scenario of `fake.py` on every fit unit (eval x domain) of the item sets it is
given and writes one JSON file, with the git SHA and the sha256 of every item file it read;
`table` prints the gate tables in Markdown. Rerun it on regenerated item sets with the same
command: nothing in it is tuned to the current items. Workers are processes, so run it with
`OMP_NUM_THREADS=1` (numpy's BLAS threads only oversubscribe the cores here).

**Gates** (SCOPE §4 item 5), per unit and scenario, over replicates:

- bias: |mean(pi_hat) - pi_true| <= 0.05 for every reported quantity (every tie group and the
  unexplained mass, planted or absent);
- coverage: the 95% interval contains the planted value in >= 90% of replicates, for every planted
  quantity (pi_true > 0);
- width: the median 95% interval width over planted quantities and replicates is <= 0.2.

**The planted triple** for `mix`, `feature`, `clustered`, `truncated` and `off_zoo` is chosen by a
rule, not by hand: h1 (0.6) is the first deterministic group of the largest family; h2 (0.3) is h1's
nearest competitor (the group with the fewest separating items, > 0); h3 (0.1) is the group of
another family that is most separated from both. Only groups available on every item are planted,
and members of a linear dependency (identified only in combination) are avoided when three
others remain.

**Feature levels** (`feature`): the first factor of the cell label that takes exactly two values
in the unit (cells split on "/" and "·"); if there is none, the cells are split into two halves in
sorted order.

**Noise-model options** (`--noise`, docs/NOISE_MODEL.md): the fake models still answer with the
pre-registered noise (geometric slips at eps = 0.1, rho = 0.3, uniform q), which every option
nests, and the near-miss fits use the given noise model instead. That asks whether a more
flexible noise model still recovers the planted weights, or absorbs them into noise.
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

from reasoning_heuristics.identify.engine import design_rank, identifiability, separations
from reasoning_heuristics.identify.fake import Scenario, always_answer, simulate, truth_vector
from reasoning_heuristics.identify.likelihood import NEAR_MISS, UNIFORM, TruncationTable, UnitModel
from reasoning_heuristics.identify.mixture import UNEXPLAINED, bca_interval, em, fit, fit_features
from reasoning_heuristics.identify.noise import NoiseModel
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


def choose_triple(um: UnitModel, sep: dict[str, dict[str, int]], exclude: set[str] | None = None) -> list[str] | None:
    """h1, h2 from deterministic groups when there are enough (procedures, not noise models), h3 any group.
    Groups in `exclude` (members of a linear dependency, which no data can recover on their own) are
    left out when at least three others remain."""
    cols = um.columns
    full = full_columns(um)
    if exclude:
        kept = [j for j in full if cols[j].name not in exclude]
        full = kept if len(kept) >= 3 else full
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


def diagnostics_least_separated(sep: dict[str, dict[str, int]], k: int = 6) -> list[dict[str, Any]]:
    pairs = sorted({tuple(sorted((a, b))): n for a, row in sep.items() for b, n in row.items()}.items(), key=lambda kv: kv[1])
    return [{"pair": list(p), "separating_items": n} for p, n in pairs[:k]]


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
    return fit(T, n_boot=n_boot, rng=rng, jackknife=True)


def run_unit(unit: Unit, cfg: dict[str, Any]) -> dict[str, Any]:
    t0 = time.time()
    rng = np.random.default_rng(cfg["seed"])
    gen = {NEAR_MISS: UnitModel(unit, NEAR_MISS), UNIFORM: UnitModel(unit, UNIFORM)}
    fitm = gen  # the full zoo is both generator and fit, except off_zoo
    noise = NoiseModel.parse(cfg.get("noise"))
    if not noise.is_default:  # fit the near-miss scenarios with another noise model (the generator stays)
        fitm = {NEAR_MISS: UnitModel(unit, NEAR_MISS, noise=noise), UNIFORM: gen[UNIFORM]}
    um = gen[NEAR_MISS]
    sep = separations(um)
    labels = [g.name for g in um.columns] + [UNEXPLAINED]
    finite = all(type(im.space).__name__ == "FiniteSpace" for im in um.items)
    out: dict[str, Any] = {"unit": unit.name, "n_items": len(unit.items), "n_clusters": unit.n_clusters,
                           "n_cells": len(set(unit.cells)), "items_per_cell": round(len(unit.items) / len(set(unit.cells)), 2),
                           "finite_channel": finite, "groups": [g.members for g in um.columns], "folded_into_q": um.q_members,
                           "scenarios": {}}
    # Gates are checked on identified quantities only (engine.identifiability): members of a linear
    # dependency are identified only in combination, and the planted triple avoids them when it can.
    ident = {NEAR_MISS: identifiability(um, rng=rng)}
    ident[UNIFORM] = ident[NEAR_MISS] if finite else identifiability(gen[UNIFORM], rng=rng)
    triple = choose_triple(um, sep, exclude=set(ident[NEAR_MISS]["involved"]))
    out["triple"] = triple
    out["design"] = design_rank(um)
    out["least_separated"] = diagnostics_least_separated(sep)
    out["identifiability"] = {m: {k: v for k, v in d.items() if k not in ("transform", "null_basis")} for m, d in ident.items()}
    R, B = cfg["reps"], cfg["boot"]
    scen = cfg["scenarios"]

    def testability(model: str, truth: np.ndarray) -> tuple[bool, str | None]:
        """Testable only if every planted weight is identified on its own: a member in a linear
        dependency (whichever one the pivot is) is identified only in combination."""
        d = ident[model]
        bad = [l for l in d["involved"] if truth[d["columns"].index(l)] > 0]
        if bad:
            deps = [x["statement"] for x in d["dependencies"] if set(x["members"]) & set(bad)]
            return False, f"planted weight on {', '.join(bad)}, identified only in combination: " + "; ".join(deps)
        return True, None

    def replicate(sc: Scenario, gen_model: str, fit_model: str, reps: int, boot: int, token=False, levels=None):
        Tid = ident[fit_model]["transform"]
        truths, ests, los, his, blo, bhi = [], [], [], [], [], []
        tv = truth_vector(fitm[fit_model], sc.weights, sc.q)
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
            tb = res.boot @ Tid.T
            truths.append(Tid @ tv)
            ests.append(Tid @ res.pi)
            los.append(np.percentile(tb, 2.5, 0))
            his.append(np.percentile(tb, 97.5, 0))
            bl, bh = bca_interval(tb, Tid @ res.pi, res.jack @ Tid.T)
            blo.append(bl)
            bhi.append(bh)
        idl = ident[fit_model]["identified"]
        out_s = summarise(np.array(truths), np.array(ests), np.array(los), np.array(his), idl)
        # the BCa alternative, on the same fits (same estimates, so the same bias)
        b = summarise(np.array(truths), np.array(ests), np.array(blo), np.array(bhi), idl)
        out_s["bca"] = {k: b[k] for k in ("min_coverage", "worst_coverage_quantity", "median_width", "gates", "pass")}
        out_s["bca"]["coverage"] = {q: v["coverage"] for q, v in b["quantities"].items()}
        out_s["bca"]["median_width_by_quantity"] = {q: v["median_width"] for q, v in b["quantities"].items()}
        ok, why = testability(fit_model, tv)
        if not ok:
            out_s.update({"testable": False, "not_testable": why, "pass": None})
            out_s["bca"]["pass"] = None
        return out_s

    if "single" in scen:
        rows = {}
        for j, g in enumerate(um.columns):
            full = j in full_columns(um)
            sc = Scenario(f"single:{g.name}", "single", {g.members[0]: 1.0 if full else 0.95}, q=0.0 if full else 0.05)
            ok, why = testability(NEAR_MISS, truth_vector(um, sc.weights, sc.q))
            rows[g.name] = replicate(sc, NEAR_MISS, NEAR_MISS, cfg["single_reps"], B) if ok else \
                {"testable": False, "not_testable": why, "pass": None}
        tested = {k: r for k, r in rows.items() if r.get("testable", True)}
        out["scenarios"]["single"] = {"by_group": rows, "pass": all(r["pass"] for r in tested.values()) if tested else None,
                                      "failing": [k for k, r in tested.items() if not r["pass"]],
                                      "not_testable": [k for k, r in rows.items() if not r.get("testable", True)]}
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
            Tid = ident[NEAR_MISS]["transform"]
            idl = ident[NEAR_MISS]["identified"]
            truths, ests, los, his = [], [], [], []
            if not noise.is_default:
                raise NotImplementedError("the feature scenario is fitted with the default noise model only")
            for _ in range(cfg["feature_reps"]):
                obs = simulate(um, sc, rng, levels)
                T = um.tensors(obs)
                X = np.stack([np.ones(T.n), levels[T.item]], 1).astype(float)
                fr = fit_features(T, X, np.array([[1.0, 0.0], [1.0, 1.0]]), n_boot=cfg["feature_boot"], rng=rng)
                # one quantity per (level, identified combination), so opposite biases cannot cancel
                truths.append(np.concatenate([Tid @ truth_vector(um, lw[lev], 0.0) for lev in (0, 1)]))
                ests.append(np.concatenate([Tid @ fr["pi"][lev] for lev in (0, 1)]))
                los.append(np.concatenate([np.percentile(fr["boot"][:, lev] @ Tid.T, 2.5, 0) for lev in (0, 1)]))
                his.append(np.concatenate([np.percentile(fr["boot"][:, lev] @ Tid.T, 97.5, 0) for lev in (0, 1)]))
            res = summarise(np.array(truths), np.array(ests), np.array(los), np.array(his),
                            [f"level 0: {l}" for l in idl] + [f"level 1: {l}" for l in idl])
            res["feature"] = desc
            ok, why = testability(NEAR_MISS, truth_vector(um, lw[0], 0.0) + truth_vector(um, lw[1], 0.0))
            if not ok:
                res.update({"testable": False, "not_testable": why, "pass": None})
            out["scenarios"]["feature"] = res
        if "off_zoo" in scen:
            rows = {}
            for g in um.columns:
                if triple[0] in g.members:
                    continue
                if not all(um.pred(i, g.members[0]).available for i in range(len(um.items))):
                    continue
                keep = [l for l in um.labels if l not in g.members]
                um_fit = UnitModel(unit, NEAR_MISS, labels=keep, noise=noise)
                fl = [c.name for c in um_fit.columns] + [UNEXPLAINED]
                q_identified = True
                if finite:
                    q_identified = "q" not in identifiability(um_fit, rng=rng)["not_identified"]
                sc = Scenario(f"off_zoo:{g.name}", "off_zoo", {triple[0]: 0.7, g.members[0]: 0.3}, withheld=g.members)
                ests = []
                for _ in range(cfg["offzoo_reps"]):
                    obs = simulate(um, sc, rng)
                    ests.append(em(um_fit.tensors(obs)).pi[0])
                ests = np.array(ests).mean(0)
                j1 = um_fit.column_of(triple[0])
                others = [(fl[j], float(ests[j])) for j in range(len(fl) - 1) if j != j1]
                top = max(others, key=lambda kv: kv[1]) if others else (None, 0.0)
                rows[g.name] = {"q_identified": q_identified, "to_q": round(float(ests[-1]), 3), "to_h1_excess": round(float(ests[j1] - 0.7), 3) if j1 is not None else None,
                                "to_other_members": round(sum(v for _, v in others), 3),
                                "largest_single_member": top[0], "largest_single_share": round(top[1], 3),
                                "share_of_withheld_on_one_member": round(max(top[1], float(ests[j1] - 0.7) if j1 is not None else 0) / 0.3, 3)}
            judged = {k: r for k, r in rows.items() if r["q_identified"]}
            out["scenarios"]["off_zoo"] = {"by_withheld_group": rows,
                                           "criterion": "< 0.2 of the withheld 0.3 on any single zoo member (A/H §5.3 P6); "
                                                        "not testable where q is not identified in the reduced zoo",
                                           "pass": all(r["share_of_withheld_on_one_member"] < 0.2 for r in judged.values()) if judged else None,
                                           "failing": [k for k, r in judged.items() if r["share_of_withheld_on_one_member"] >= 0.2],
                                           "not_testable": [k for k, r in rows.items() if not r["q_identified"]]}
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
    gated = [v["pass"] for k, v in out["scenarios"].items() if k in GATED and v.get("pass") is not None]
    out["all_gates_pass"] = bool(gated) and all(gated)
    out["not_testable"] = [k for k, v in out["scenarios"].items() if k in GATED and v.get("pass") is None]
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
    ap.add_argument("--units", default=None,
                    help="unit names (eval/domain) separated by ';' (names can contain commas)")
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
    ap.add_argument("--noise", default=None,
                    help="fit with this noise model (a name in noise.CANDIDATES, or 'kernel=free,eps_max=1,q=strata'); "
                         "default: the pre-registered one")
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
    if a.noise:
        cfg["noise"] = a.noise
        cfg["noise_model"] = NoiseModel.parse(a.noise).to_json()
    wanted = [u.strip() for u in a.units.split(";") if u.strip()] if a.units else None
    tasks, found = [], set()
    for ev, ps in sorted(by_eval.items()):
        for name in make_units(load_items(ps)):
            found.add(name)
            if wanted and name not in wanted:
                continue
            tasks.append((ps, name, cfg))
    missing = sorted(set(wanted or ()) - found)
    if missing:
        print(f"no unit named {missing} in these item sets; units are: {sorted(found)}", file=sys.stderr)
        return 2
    # longest first, so the pool is not left waiting on one big unit at the end
    tasks.sort(key=lambda t: -sum(p.stat().st_size for p in t[0]))
    prov = provenance(paths)  # before the run, so later edits to the tree cannot leak in
    t0 = time.time()
    results = []
    with mp.get_context("fork").Pool(a.workers) as pool:
        for r in pool.imap_unordered(_worker, tasks):
            results.append(r)
            status = "ERROR " + r["error"] if "error" in r else ("PASS" if r.get("all_gates_pass") else "fail")
            print(f"[{time.time() - t0:7.0f}s] {r['unit']}: {status} ({r.get('seconds', '?')}s)", flush=True)
    results.sort(key=lambda r: r["unit"])
    doc = {"label": a.label or Path(a.items).name, "items": str(a.items), "config": cfg, "gates": GATES,
           "generated": time.strftime("%Y-%m-%d %H:%M"), "provenance": prov,
           "command": "python -m reasoning_heuristics.identify.recovery run " + " ".join(argv), "units": results}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(doc, indent=1, ensure_ascii=False))
    print(f"wrote {a.out}")
    return 0


# =============================================================================================
# Tables
# =============================================================================================


def _single_mark(single: dict[str, Any] | None) -> str:
    if not single:
        return "–"
    nt = len(single.get("not_testable", []))
    tested = len(single["by_group"]) - nt
    if single["pass"] is None:
        return f"not testable ({nt})"
    tag = "PASS" if single["pass"] else f"fail {len(single['failing'])}/{tested}"
    return tag + (f", {nt} not testable" if nt else "")


def _mark(res: dict[str, Any] | None) -> str:
    if res is None:
        return "–"
    if res.get("testable") is False:
        return "not testable"
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
            sm = _single_mark(s.get("single"))
            mix = s.get("mix")
            lines.append(f"| {u['unit']} | {u['items_per_cell']} | {sm} | {_mark(mix)} | {_mark(s.get('feature'))} | "
                         f"{_mark(s.get('null_q'))} | {_mark(s.get('null_always'))} | {_mark(s.get('clustered'))} | "
                         f"{mix['max_abs_bias'] if mix else '–'} | {mix['min_coverage'] if mix else '–'} | {mix['median_width'] if mix else '–'} |")
        lines.append("")
    return "\n".join(lines)


def _f(x: Any) -> str:
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else (f"{x:.3f}" if isinstance(x, float) else str(x))


def report(dev_path: str, sweep_paths: list[str]) -> str:
    """The Markdown sections of docs/RECOVERY.md: gates at dev size, details, misspecification,
    off-zoo leakage, checks, and the items-per-cell sweep."""
    dev = json.loads(Path(dev_path).read_text())
    units = [u for u in dev["units"] if "error" not in u]
    def _sha(p: dict[str, Any]) -> str:
        return f"{(p.get('git_sha') or '?')[:10]}{' (dirty)' if p.get('git_dirty') else ''}"

    merged = "".join(f"; {', '.join(m['units'])} rerun at git {_sha(m['provenance'])}" for m in dev.get("merged", []))
    out = [f"Item set `{dev['items']}`, git {_sha(dev['provenance'])}{merged}; {dev['config']['reps']} replicates × "
           f"{dev['config']['boot']} bootstrap draws"
           + (f" ({dev['config']['single_reps']} per single member)" if "single" in dev["config"]["scenarios"] else "") + ".\n"]
    out.append("| Unit | items | clusters | single | mix | mix, uniform slips | feature | null q | null ALWAYS | all |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for u in units:
        s = u["scenarios"]
        sm = _single_mark(s.get("single"))
        out.append(f"| {u['unit']} | {u['n_items']} | {u['n_clusters']} | {sm} | {_mark(s.get('mix'))} | "
                   f"{_mark(s.get('mix_uniform_slips')) if not u['finite_channel'] else 'n/a (finite)'} | "
                   f"{_mark(s.get('feature'))} | {_mark(s.get('null_q'))} | {_mark(s.get('null_always'))} | "
                   f"{'PASS' if u['all_gates_pass'] else 'fail'}{' (' + str(len(u.get('not_testable', []))) + ' not testable)' if u.get('not_testable') else ''} |")
    out.append("\n**The 60/30/10 mixture in detail** (worst quantity for each gate):\n")
    out.append("| Unit | triple (0.6 / 0.3 / 0.1) | max \\|bias\\| | on | min coverage | on | median width | BCa: min coverage / median width |")
    out.append("|---|---|---|---|---|---|---|---|")
    for u in units:
        m = u["scenarios"].get("mix")
        if not m:
            out.append(f"| {u['unit']} | (no triple) ||||||")
            continue
        if m.get("testable") is False:
            out.append(f"| {u['unit']} | {' / '.join(u['triple'])} | not testable: {m['not_testable']} ||||||")
            continue
        bc = m.get("bca") or {}
        out.append(f"| {u['unit']} | {' / '.join(u['triple'])} | {_f(m['max_abs_bias'])} | {m['worst_bias_quantity']} | "
                   f"{_f(m['min_coverage'])} | {m['worst_coverage_quantity']} | {_f(m['median_width'])} | "
                   f"{_f(bc.get('min_coverage'))} / {_f(bc.get('median_width'))} |")
    out.append("\n**Single members that fail** (the first gate each fails on, and its worst quantity):\n")
    for u in units:
        single = u["scenarios"].get("single")
        if not single or single["pass"] is not False:
            continue
        bits = []
        for g in single["failing"]:
            r = single["by_group"][g]
            if r.get("testable") is False:
                continue
            why = [k for k in ("bias", "coverage", "width") if not r["gates"][k]]
            bits.append(f"{g} ({', '.join(why)}; bias {r['max_abs_bias']:.2f} on {r['worst_bias_quantity']})")
        out.append(f"- **{u['unit']}**: " + "; ".join(bits))
    out.append("\n**Linear dependencies** (`engine.identifiability`: rank of the (item, outcome) × (groups + q) "
               "matrix; witness channels on sampled outcomes). Every member of a dependency is identified only in "
               "combination; the fits report the identified combinations shown (one basis of them):\n")
    for u in units:
        d = (u.get("identifiability") or {}).get("near-miss")
        if not d or not d["deficiency"]:
            continue
        combos = [c for c in d["identified"] if " + " in c]
        deps = d.get("dependencies") or [{"statement": x} for x in d["null_directions"]]
        out.append(f"- **{u['unit']}** (rank {d['rank']} of {len(d['columns'])}): " + "; ".join(f"`{x['statement']}`" for x in deps)
                   + ". Not identified on their own: " + ", ".join(d.get("involved", d["not_identified"]))
                   + (". Identified combinations reported: " + "; ".join(f"`{c}`" for c in combos) if combos else "") + ".")
    full = [u["unit"] for u in units if not ((u.get("identifiability") or {}).get("near-miss") or {}).get("deficiency")]
    out.append(f"- Full rank: {', '.join(full)}.")
    out.append("\n**Identifiability diagnostics** (finite channels: rank of the (item, value) × (groups + q) "
               "design; A/H §5.3 asks for σ_min/σ_max ≥ 0.05) and the least-separated pairs:\n")
    out.append("| Unit | rank / columns | σ ratio | weakest direction | least-separated pair (items) |")
    out.append("|---|---|---|---|---|")
    for u in units:
        d = u.get("design")
        ls = u.get("least_separated") or []
        pair = f"{ls[0]['pair'][0]} vs {ls[0]['pair'][1]} ({ls[0]['separating_items']})" if ls else "–"
        if d:
            out.append(f"| {u['unit']} | {d['rank']} / {d['columns']} | {d['sigma_ratio']} | {', '.join(d['weakest_direction'][:4])} | {pair} |")
        else:
            out.append(f"| {u['unit']} | (witness channel) | | | {pair} |")
    sections = {"dev": "\n".join(out)}

    mis = ["| Unit | near-miss fit: max \\|bias\\| / min coverage | uniform fit on near-miss data | on | near-miss fit on uniform data | on |",
           "|---|---|---|---|---|---|"]
    for u in units:
        s = u["scenarios"]
        a, b, c = s.get("mix"), s.get("misspec_uniform_fit_on_near_miss"), s.get("misspec_near_miss_fit_on_uniform")
        if not b:
            continue
        mis.append(f"| {u['unit']} | {_f(a['max_abs_bias'])} / {_f(a['min_coverage'])} | {_f(b['max_abs_bias'])} / {_f(b['min_coverage'])} | "
                   f"{b['worst_bias_quantity']} | {_f(c['max_abs_bias'])} / {_f(c['min_coverage'])} | {c['worst_bias_quantity']} |")
    sections["misspec"] = "\n".join(mis)

    oz = ["| Unit | withheld groups | to q (mean) | onto h1 (mean excess) | onto other members (mean) | groups with ≥ 0.2 of the withheld 0.3 on one member |",
          "|---|---|---|---|---|---|"]
    for u in units:
        o = u["scenarios"].get("off_zoo")
        if not o or not o["by_withheld_group"]:
            continue
        rows = list(o["by_withheld_group"].values())
        to_q = np.mean([r["to_q"] for r in rows])
        h1 = np.mean([r["to_h1_excess"] for r in rows if r["to_h1_excess"] is not None])
        oth = np.mean([r["to_other_members"] for r in rows])
        oz.append(f"| {u['unit']} | {len(rows)} | {to_q:.3f} | {h1:+.3f} | {oth:.3f} | {len(o['failing'])} of {len(rows)} |")
    sections["offzoo"] = "\n".join(oz)

    ck = ["| Unit | clustered: max \\|bias\\| / min coverage / width | truncated, excluded: bias on h1 | truncated, token model: bias on h1 |",
          "|---|---|---|---|"]
    for u in units:
        s = u["scenarios"]
        cl, te, tt = s.get("clustered"), s.get("truncated_excluded"), s.get("truncated_token_model")
        if not cl:
            continue
        if cl.get("testable") is False:  # the triple has weight on a member identified only in combination
            ck.append(f"| {u['unit']} | not testable | not testable | not testable |")
            continue
        h1 = u["triple"][0]
        h1g = next((g for g in te["quantities"] if h1 in g.split(" = ")), None) if te else None
        b_ex = te["quantities"][h1g]["bias"] if h1g else None
        b_tm = tt["quantities"][h1g]["bias"] if h1g and h1g in tt["quantities"] else None
        ck.append(f"| {u['unit']} | {_f(cl['max_abs_bias'])} / {_f(cl['min_coverage'])} / {_f(cl['median_width'])} | {_f(b_ex)} | {_f(b_tm)} |")
    sections["checks"] = "\n".join(ck)

    if sweep_paths:
        docs = [json.loads(Path(p).read_text()) for p in sweep_paths]
        sizes = {"dev": dev}
        for d in docs:
            sizes[d["label"]] = d
        names = sorted({u["unit"] for d in sizes.values() for u in d["units"] if "error" not in u})
        labels = list(sizes)
        sw = ["| Unit | " + " | ".join(f"{l} (items/cell)" for l in labels) + " |", "|---" * (len(labels) + 1) + "|"]
        for n in names:
            cells = []
            for l in labels:
                u = next((x for x in sizes[l]["units"] if x["unit"] == n and "error" not in x), None)
                if u is None:
                    cells.append("–")
                    continue
                m, q = u["scenarios"].get("mix"), u["scenarios"].get("null_q")
                if not m:
                    tag = "mix –"
                elif m.get("testable") is False:
                    tag = "mix not testable"
                else:
                    bc = m.get("bca") or {}
                    tag = "mix " + ("PASS" if m["pass"] else "fail") + f" (b {_f(m['max_abs_bias'])}, c {_f(m['min_coverage'])}, w {_f(m['median_width'])}" \
                        + (f"; BCa c {_f(bc.get('min_coverage'))}, w {_f(bc.get('median_width'))}" if bc else "") + ")"
                tag += "; q " + ("not testable" if q and q.get("testable") is False else ("PASS" if q and q["pass"] else "fail"))
                cells.append(f"{u['items_per_cell']:g}: {tag}")
            sw.append(f"| {n} | " + " | ".join(cells) + " |")
        sections["sweep"] = "\n".join(sw)
        # the smallest size at which the 60/30/10 mixture passes bias + width, and all three gates
        need = ["| Unit | bias and width pass from (items/cell) | all three gates pass at (percentile) | ... with BCa intervals |",
                "|---|---|---|---|"]
        for n in names:
            bw, allg, allb = None, [], []
            for l in labels:
                u = next((x for x in sizes[l]["units"] if x["unit"] == n and "error" not in x), None)
                m = u["scenarios"].get("mix") if u else None
                if not m or m.get("testable") is False:
                    continue
                if bw is None and m["gates"]["bias"] and m["gates"]["width"]:
                    bw = f"{u['items_per_cell']:g}"
                if m["pass"]:
                    allg.append(f"{u['items_per_cell']:g}")
                if (m.get("bca") or {}).get("pass"):
                    allb.append(f"{u['items_per_cell']:g}")
            mixes = [((next((x for x in sizes[l]["units"] if x["unit"] == n and "error" not in x), {}) or {})
                      .get("scenarios", {}).get("mix")) for l in labels]
            mixes = [m for m in mixes if m]
            if not mixes:
                status = "no planted triple (fewer than 3 members on every item)"
            elif all(m.get("testable") is False for m in mixes):
                status = "not testable"
            else:
                status = bw if bw is not None else "not reached"
            need.append(f"| {n} | {status} | {', '.join(allg) if allg else '–'} | {', '.join(allb) if allb else '–'} |")
        sections["needed"] = "\n".join(need)
        sections["where"] = _where_table(names, sizes, labels)
    return "\n\n".join(f"<!-- {k} -->\n{v}" for k, v in sections.items())


def _verdict(s: dict[str, Any] | None) -> str | None:
    if s is None:
        return None
    if s.get("testable") is False:
        return "not testable"
    return "pass" if s["pass"] else "fail"


def _by_size(pairs: list[tuple[str, str]]) -> str:
    """[(size, verdict)] -> "pass at 5, 10; fail at 20" (a single verdict: "pass at every size (5–40)")."""
    kinds = list(dict.fromkeys(v for _, v in pairs))
    if not kinds:
        return "–"
    if len(kinds) == 1:
        return f"{kinds[0]} at every size ({pairs[0][0]}–{pairs[-1][0]})" if len(pairs) > 1 else f"{kinds[0]} at {pairs[0][0]}"
    return "; ".join(f"{k} at {', '.join(s for s, v in pairs if v == k)}" for k in kinds)


def _where_table(names: list[str], sizes: dict[str, dict[str, Any]], labels: list[str]) -> str:
    """Per unit: the sizes (items per cell) at which the 60/30/10 mixture passes all three gates, with
    percentile and with BCa intervals; the two null scenarios by size; and the sizes at which the
    mixture (percentile) and both nulls pass together."""
    rows = ["| Unit | mixture passes at (percentile) | mixture passes at (BCa) | null q | null ALWAYS | mixture and both nulls pass at |",
            "|---|---|---|---|---|---|"]
    for n in names:
        per = []
        for l in labels:
            u = next((x for x in sizes[l]["units"] if x["unit"] == n and "error" not in x), None)
            if u is not None:
                per.append((f"{u['items_per_cell']:g}", u["scenarios"]))
        mixes = [(z, s["mix"]) for z, s in per if s.get("mix")]
        if not mixes:
            pct = bca = "no planted triple"
        elif all(m.get("testable") is False for _, m in mixes):
            pct = bca = "not testable"
        else:
            p = [z for z, m in mixes if m.get("pass")]
            b = [z for z, m in mixes if (m.get("bca") or {}).get("pass")]
            run = f"{mixes[0][0]}–{mixes[-1][0]}" if len(mixes) > 1 else mixes[0][0]
            pct = ", ".join(p) if p else f"none ({run})"
            bca = ", ".join(b) if b else f"none ({run})"
        nq = _by_size([(z, v) for z, s in per if (v := _verdict(s.get("null_q")))])
        na = _by_size([(z, v) for z, s in per if (v := _verdict(s.get("null_always")))])
        together = [z for z, s in per if _verdict(s.get("mix")) == "pass"
                    and _verdict(s.get("null_q")) == "pass" and _verdict(s.get("null_always")) == "pass"]
        rows.append(f"| {n} | {pct} | {bca} | {nq} | {na} | {', '.join(together) if together else '–'} |")
    return "\n".join(rows)


def merge(base_path: str, patch_path: str) -> None:
    """Overwrite, unit by unit, the scenarios of `base` that `patch` reran (e.g. after a rule change),
    with the patch's planted triple, and keep both runs' provenance."""
    base = json.loads(Path(base_path).read_text())
    patch = json.loads(Path(patch_path).read_text())
    by_name = {u["unit"]: u for u in base["units"]}
    names = set()
    for pu in patch["units"]:
        names.add(pu["unit"])
        bu = by_name.get(pu["unit"])
        if bu is None or "error" in bu or "error" in pu:
            by_name[pu["unit"]] = pu
            continue
        for k, v in pu.items():
            if k != "scenarios":
                bu[k] = v
        bu["scenarios"].update(pu["scenarios"])
        gated = [v["pass"] for k, v in bu["scenarios"].items() if k in GATED and v.get("pass") is not None]
        bu["all_gates_pass"] = bool(gated) and all(gated)
        bu["not_testable"] = [k for k, v in bu["scenarios"].items() if k in GATED and v.get("pass") is None]
    base["units"] = sorted(by_name.values(), key=lambda u: u["unit"])
    base.setdefault("merged", []).append({"units": sorted(names), "provenance": patch["provenance"],
                                           "command": patch.get("command"), "generated": patch.get("generated")})
    Path(base_path).write_text(json.dumps(base, indent=1, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in ("run", "table", "report", "merge"):
        print(__doc__)
        return 2
    if argv[0] == "run":
        return run(argv[1:])
    if argv[0] == "merge":
        merge(argv[1], argv[2])
        return 0
    if argv[0] == "report":
        print(report(argv[1], argv[2:]))
        return 0
    print(table(argv[1:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
