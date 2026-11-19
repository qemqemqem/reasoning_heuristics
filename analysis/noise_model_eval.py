"""Noise-model evaluation (docs/NOISE_MODEL.md): the candidate noise models of `identify/noise.py` on
the 24 gated fits of analysis/prelim_2026_11_18.py, with that script's settings.

    # data-level diagnosis and a point-fit likelihood ladder over every candidate (minutes)
    OMP_NUM_THREADS=1 python analysis/noise_model_eval.py diagnose --out analysis/out/noise_model/diagnosis.json
    # one candidate: fits with 2000 cluster-bootstrap draws (percentile and BCa), then 100 fake data sets
    # drawn from each fit, refitted with 200 draws each (recovery at the estimate, and the four
    # predictive checks of the prelim script, computed on the same fake data)
    OMP_NUM_THREADS=1 python analysis/noise_model_eval.py fits --noise KEQ --workers 3 --out analysis/out/noise_model/fits_KEQ.json
    # the Stage 0 harness (planted 60/30/10 and both nulls) fitted with a candidate
    OMP_NUM_THREADS=1 python -m reasoning_heuristics.identify.recovery run --items data/items/pc20 --label pc20 \\
        --units 'C_E2/colouring;C_E2/knapsack;AH_E5/SAT' --scenarios mix,null_q,null_always --reps 100 --boot 100 \\
        --noise KEQ --workers 3 --out analysis/out/noise_model/stage0_pc20_KEQ.json
    # the tables of docs/NOISE_MODEL.md
    python analysis/noise_model_eval.py table --dir analysis/out/noise_model

The committed analysis (analysis/out/prelim_2026_11_18.json) is the pre-registered model, M0; it is
read, not recomputed. `fits --noise M0` reproduces its numbers (same seeds, same code path), which
is how this script is checked. Settings are the prelim script's defaults (`--n-boot 2000`,
`--recovery-reps 100`, `--recovery-boot 200`), except that no permutation baselines are computed:
they do not bear on the noise model, and they cost as much as the rest.

**A fit passes the predictive checks** as in the prelim script's table: the observed share of
answers equal to a slipping member's answer, beyond every slipping member's reach, and special
tokens each inside the 5-95% range of the fake data sets, and the distance-profile check's p >= 0.05.
"""

from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
import json
import math
import multiprocessing as mp
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prelim_2026_11_18 as P  # noqa: E402

from reasoning_heuristics.identify import agreement  # noqa: E402
from reasoning_heuristics.identify.engine import identifiability, weight_ranges  # noqa: E402
from reasoning_heuristics.identify.fake import Scenario, simulate, truth_vector  # noqa: E402
from reasoning_heuristics.identify.likelihood import UnitModel  # noqa: E402
from reasoning_heuristics.identify.mixture import (UNEXPLAINED, _GeneralStepper, bca_interval, em, fit,  # noqa: E402
                                                   noise_params)
from reasoning_heuristics.identify.noise import CANDIDATES, NoiseModel  # noqa: E402
from reasoning_heuristics.identify.spaces import AD_CELLS, BitSpace, PartitionSpace, trunc_geom  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "analysis" / "out" / "noise_model"
CHECKS = ("exact", "beyond_reach", "special")


# =============================================================================================
# Shared
# =============================================================================================


def load(runs_root: Path) -> list[tuple[str, str, str]]:
    """Every pilot run (pc20, pc40) and the gated units fitted on it, as the prelim script does."""
    found, _ = P.discover_runs(runs_root)
    sets: dict[str, Any] = {}
    runs = {rid: P.load_run(runs_root, rid, sets) for rid in found if "-dev-" not in rid}
    P._CTX.update(sets=sets, runs=runs)
    return [(runs[rid]["item_set"], name, rid) for rid in sorted(runs) for name in P.GATED.get(runs[rid]["item_set"], [])]


def unit_model(set_name: str, name: str, noise: NoiseModel) -> UnitModel:
    um = UnitModel(P._unit(set_name, name), noise=noise)
    P.check_ties(set_name, name, um)
    return um


def responses(name: str, run_id: str) -> list:
    return [r for r, it in P._CTX["runs"][run_id]["pairs"] if P.unit_name(it) == name]


def state_of(res, T) -> dict[str, np.ndarray]:
    """Every fitted parameter as a one-replicate state (the default model's eps and rho included)."""
    if "state" in res.extra:
        return {k: np.atleast_2d(np.asarray(v, dtype=float)) if k not in ("tau", "rho") else np.atleast_1d(np.asarray(v, dtype=float))
                for k, v in res.extra["state"].items()}
    return {"pi": res.pi[None], "eps": np.array([[res.eps]]), "g": trunc_geom(res.rho)[None], "rho": np.array([res.rho])}


def mass_shares(T, st: dict[str, np.ndarray]) -> dict[str, float]:
    """Where the fitted model puts the observed answers (posterior shares over rows): a member's exact
    output (no slip), a member's slip, a member that does not slip (a stored distribution: RO-FF,
    NOISY-EXACT), or q. 'noise' is slips + q."""
    step = _GeneralStepper(T, np.ones((1, T.n)), None)
    S, L, num, numq, tot, _ = step.terms(st)
    tot = np.maximum(tot[0], 1e-300)
    e = st["eps"][0][None, :]
    A, slips = T.A, T.slips
    pi = st["pi"][0]
    G = A.shape[1]
    w = pi[None, :G] * T.avail
    exact = (w * (1 - e) * A)[:, slips].sum(1) / tot
    slip = (w * e * S[0])[:, slips].sum(1) / tot
    other = num[0][:, ~slips].sum(1) / tot
    q = numq[0] / tot
    out = {"exact": float(exact.mean()), "slip": float(slip.mean()), "nonslipping_members": float(other.mean()),
           "q": float(q.mean())}
    out["noise"] = out["slip"] + out["q"]
    return out


def n_params(um: UnitModel, T, noise: NoiseModel) -> int:
    """Free parameters: the weights (columns + q, less one), the slip rate(s), the kernel, the q strata and tau."""
    G = len(um.columns)
    k = G
    if T.slip_identified:
        k += int(T.slips.sum()) if noise.eps == "member" else 1
        k += 1 if noise.kernel == "geometric" else (len(AD_CELLS) - 2 if noise.cells == "adds-drops" else 5)
    if noise.q == "strata" and T.qs is not None:
        groups = Counter(T.qs.group.tolist())
        k += sum(sum(1 for j, g in enumerate(T.qs.group) if g == grp and T.qs.p0[j] > 0) - 1 for grp in groups)
        k += int(T.qs.tau_free and T.qs.has_special.any())
    return k


# =============================================================================================
# fits: one candidate on every gated fit, with recovery and predictive checks at the estimate
# =============================================================================================


def fit_job(args: tuple) -> dict[str, Any]:
    set_name, name, run_id, cand, n_boot = args
    noise = NoiseModel.parse(cand)
    um = unit_model(set_name, name, noise)
    seed = P.job_seed("fit", name, run_id)
    rng = np.random.default_rng(seed)
    obs, exc = um.observations(responses(name, run_id))
    T = um.tensors(obs)
    t0 = time.time()
    res = fit(T, n_boot=n_boot, rng=rng, jackknife=True)
    blo, bhi = bca_interval(res.boot, res.pi, res.jack)
    ident = identifiability(um, rng=rng)
    weights = {lab: {"pi": float(p), "lo": float(a), "hi": float(b), "bca": [float(c), float(d)]}
               for lab, p, a, b, c, d in zip(res.labels, res.pi, res.lo, res.hi, blo, bhi)}
    names = [g.name for g in um.columns] + [res.labels[-1]]
    if ident["deficiency"]:
        lo_r, hi_r = weight_ranges(res.pi, ident["null_basis"])
        for lab in ident["involved"]:
            c = ident["columns"].index(lab)
            weights[names[c]] = {"pi": "not identified", "range": [float(lo_r[c]), float(hi_r[c])]}
    st = state_of(res, T)
    eps_cols = st["eps"][0]
    slipping = [g.name for g, s in zip(um.columns, T.slips) if s]
    rep = {"unit": name, "run_id": run_id, "item_set": set_name, "noise": noise.to_json(), "seed": seed,
           "fit": {"weights": weights, "eps": res.eps, "eps_ci": list(res.eps_ci), "rho": res.rho, "rho_ci": list(res.rho_ci),
                   "loglik": res.loglik, "n_rows": res.n_rows, "n_clusters": res.n_clusters, "converged": res.converged,
                   "n_params": n_params(um, T, noise), "slip_identified": T.slip_identified,
                   "kernel": st["g"][0].tolist(), "kernel_cells": noise.cells,
                   "eps_by_group": ({g.name: float(e) for g, e in zip(um.columns, eps_cols)} if len(eps_cols) > 1 else None),
                   "eps_at_cap": bool(T.slip_identified and res.eps >= noise.eps_max - 1e-6),
                   "slipping_groups": slipping, "state": {k: v[0].tolist() if v.ndim > 1 else float(v[0]) for k, v in st.items()},
                   "state_ci": res.extra.get("state_ci"), "data_ties": res.extra["data_ties"]},
           "groups": [g.members for g in um.columns], "mass": mass_shares(T, st), "excluded": exc.to_json(),
           "near": P.nearest_distances(um, obs), "reach": P.reach_stats(um, obs, T), "seconds_fit": round(time.time() - t0, 1)}
    if noise.q == "strata" and T.qs is not None:
        rep["fit"]["tau_free"] = T.qs.tau_free
        rep["fit"]["always_token_columns"] = um.always_token_columns()
    return P.to_jsonable(rep)


def planted_of(rep: dict[str, Any]) -> tuple[dict[str, float], float]:
    """The fitted weights as a fake model, rounded to 4 decimals first as the prelim script's JSON round trip does."""
    w = {k: {"pi": round(v["pi"], 4) if isinstance(v["pi"], float) else v["pi"]} for k, v in rep["fit"]["weights"].items()}
    return P.planted_from_fit({"fit": {"weights": w}}, rep["groups"])


def recovery_job(args: tuple) -> dict[str, Any]:
    """Fake models answering the unit's items from one fitted mixture (its noise parameters too), refitted;
    one chunk of replicates. For M0 this is the prelim script's `recovery_job` exactly."""
    set_name, name, run_id, cand, planted, q, state, reps, n_boot, chunk = args
    noise = NoiseModel.parse(cand)
    um = unit_model(set_name, name, noise)
    obs_real, _ = um.observations(responses(name, run_id))
    keep = Counter(ob.item for ob in obs_real)
    if noise.is_default:
        # rounded as in the prelim script, which plants the JSON's eps and rho
        sc = Scenario("at-estimate", "mix", weights=planted, q=q, eps=round(float(state["eps"][0]), 4),
                      rho=round(float(state["rho"]), 4))
    else:
        keys = [g.members[0] for g in um.columns]
        st = {k: np.asarray(v) for k, v in state.items()}
        prm = noise_params(st, noise, keys, um.strata_index()[0] if noise.q == "strata" else None)
        sc = Scenario("at-estimate", "mix", weights=planted, q=q, params=prm)
    truth = truth_vector(um, planted, q)
    rng = np.random.default_rng(P.job_seed("recovery", name, run_id, str(chunk)))
    out = []
    for _ in range(reps):
        sim = [ob for ob in simulate(um, sc, rng) if keep.get(ob.item)]
        T = um.tensors(sim)
        if n_boot == 0:  # predictive checks only: no refit
            out.append({"reach": P.reach_stats(um, sim, T), "near": P.near_shares(um, sim)})
            continue
        res = fit(T, n_boot=n_boot, rng=rng, jackknife=True)
        blo, bhi = bca_interval(res.boot, res.pi, res.jack)
        out.append({"pi": res.pi.tolist(), "lo": res.lo.tolist(), "hi": res.hi.tolist(), "bca_lo": blo.tolist(),
                    "bca_hi": bhi.tolist(), "eps": res.eps, "rho": res.rho, "reach": P.reach_stats(um, sim, T),
                    "near": P.near_shares(um, sim)})
    return {"unit": name, "run_id": run_id, "chunk": chunk, "truth": truth.tolist(),
            "labels": [g.name for g in um.columns] + [UNEXPLAINED], "replicates": out}


def checks_only(chunks: list[dict[str, Any]], observed_near: dict[str, Any]) -> dict[str, Any]:
    """The predictive checks' summary from fake data sets that were not refitted (`--recovery-boot 0`)."""
    reps = [r for c in sorted(chunks, key=lambda c: c["chunk"]) for r in c["replicates"]]
    return {"replicates": len(reps), "refitted": False,
            "distance_check": P.distance_check(observed_near, np.array([r["near"] for r in reps])),
            "simulated": {k: {"mean": float(np.mean([r["reach"][k] for r in reps])),
                              "p05_p95": [float(np.percentile([r["reach"][k] for r in reps], p)) for p in (5, 95)]}
                          for k in CHECKS}}


def ppc_verdict(rep: dict[str, Any], rec: dict[str, Any]) -> dict[str, Any]:
    fails = []
    for k in CHECKS:
        lo, hi = rec["simulated"][k]["p05_p95"]
        if not lo - 1e-9 <= rep["reach"][k] <= hi + 1e-9:
            fails.append(k)
    dc = rec.get("distance_check")
    if dc and dc["p_value"] < 0.05:
        fails.append("distance")
    return {"fails": fails, "pass": not fails}


def cmd_fits(a: argparse.Namespace) -> int:
    t0 = time.time()
    targets = load(a.runs_root)
    if a.only:
        targets = [t for t in targets if any(o in f"{t[1]} {t[2]}" for o in a.only.split(";"))]
    noise = NoiseModel.parse(a.noise)
    if noise.cells == "adds-drops":
        targets = [t for t in targets if "colouring" not in t[1]]
    ctx = mp.get_context("fork")
    with ctx.Pool(a.workers) as pool:
        fitted = pool.map(fit_job, [(s, n, r, a.noise, a.n_boot) for s, n, r in targets], chunksize=1)
        print(f"[{time.time() - t0:6.0f}s] {len(fitted)} fits", flush=True)
        by = {(f["unit"], f["run_id"]): f for f in fitted}
        jobs = []
        n_chunks = max(1, min(10, a.recovery_reps // 10))
        per = [a.recovery_reps // n_chunks + (1 if k < a.recovery_reps % n_chunks else 0) for k in range(n_chunks)]
        for s, n, r in targets:
            rep = by[(n, r)]
            planted, q = planted_of(rep)
            rep["planted"] = {"weights": planted, "q": q}
            jobs += [(s, n, r, a.noise, planted, q, rep["fit"]["state"], per[k], a.recovery_boot, k) for k in range(n_chunks) if per[k]]
        chunks = []
        if a.recovery_reps:
            for c in pool.imap_unordered(recovery_job, jobs, chunksize=1):
                chunks.append(c)
                if len(chunks) % 10 == 0:
                    print(f"[{time.time() - t0:6.0f}s] {len(chunks)} / {len(jobs)} recovery chunks", flush=True)
    grouped: dict[tuple[str, str], list] = defaultdict(list)
    for c in chunks:
        grouped[(c["unit"], c["run_id"])].append(c)
    out: dict[str, dict[str, Any]] = defaultdict(dict)
    for (n, r), rep in by.items():
        if (n, r) in grouped:
            rec = (P.summarise_recovery(grouped[(n, r)], rep["near"]) if a.recovery_boot
                   else checks_only(grouped[(n, r)], rep["near"]))
            rep["recovery"] = rec
            rep["ppc"] = ppc_verdict(rep, rec)
        out[n][r] = rep
    doc = {"noise": a.noise, "noise_model": noise.to_json(), "command": " ".join(sys.argv),
           "settings": {"n_boot": a.n_boot, "recovery_reps": a.recovery_reps, "recovery_boot": a.recovery_boot,
                        "n_perm": 0, "plant_min": P.PLANT_MIN},
           "git": P.git_state(), "seconds": round(time.time() - t0), "fits": out}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(P.to_jsonable(doc), indent=1, sort_keys=True) + "\n")
    print(f"wrote {a.out} ({round(time.time() - t0)} s)")
    return 0


# =============================================================================================
# diagnose: what the wrong answers look like, and a point-fit likelihood ladder
# =============================================================================================


def nearest_member(um: UnitModel, i: int, y: str) -> tuple[int | None, str | None, np.ndarray | None]:
    """Distance to the nearest deterministic or set-valued member, the member, and its answer as a vector."""
    im = um.items[i]
    sp = im.space
    best: tuple[int | None, str | None, np.ndarray | None] = (None, None, None)
    vy = sp.parse(y) if not sp.is_special(y) else None
    if vy is None:
        return best
    for g in um.columns:
        p = um.pred(i, g.members[0])
        if p.kind == "det" and not sp.is_special(p.key):
            d = sp.distance(y, p.key)
            if best[0] is None or d < best[0]:
                best = (d, g.name, sp.parse(p.key))
        elif p.kind == "set" and isinstance(sp, BitSpace):
            S = p.sol.array(sp)
            ds = (S != vy[None]).sum(1)
            j = int(ds.argmin())
            if best[0] is None or ds[j] < best[0]:
                best = (int(ds[j]), g.name, S[j])
        elif p.kind == "set":
            d = P.set_distance(sp, y, p.sol, bound=best[0])
            if best[0] is None or d < best[0]:
                best = (d, g.name, None)
    return best


def describe_answers(um: UnitModel, obs: list) -> dict[str, Any]:
    """Shares of correct, exact-member, wrong-and-exact answers; for wrong answers that match no member,
    their distance to the nearest one; bit spaces: (adds, drops) against the nearest member; partitions:
    colour blocks of the answers and of the members' answers, and how many answers are proper colourings."""
    n = len(obs)
    special = sum(1 for ob in obs if um.items[ob.item].space.is_special(ob.key))
    correct = [agreement.is_correct(um, ob.item, ob.key) for ob in obs]
    exact = []
    for ob in obs:
        hit = False
        for g in um.columns:
            p = um.pred(ob.item, g.members[0])
            if p.kind == "det" and p.key == ob.key or p.kind == "set" and p.sol.contains(ob.key):
                hit = True
                break
        exact.append(hit)
    wrong = [k for k in range(n) if not correct[k]]
    out: dict[str, Any] = {"n": n, "special": special, "correct": sum(correct), "exact_member": sum(exact),
                           "wrong": len(wrong), "wrong_exact_member": sum(1 for k in wrong if exact[k])}
    ad, dist, blocks, mblocks, popfrac = Counter(), Counter(), Counter(), Counter(), Counter()
    for k in wrong:
        ob = obs[k]
        sp = um.items[ob.item].space
        if sp.is_special(ob.key):
            continue
        d, _, va = nearest_member(um, ob.item, ob.key)
        if d is not None and not exact[k]:
            dist[str(d) if d <= 6 else ">6"] += 1
        if isinstance(sp, BitSpace) and va is not None and d is not None and 1 <= d <= 3:
            vy = sp.parse(ob.key)
            ad[f"{int((vy & ~va).sum())},{int((~vy & va).sum())}"] += 1
        if isinstance(sp, BitSpace):
            popfrac[round(float(sp.parse(ob.key).mean()), 1)] += 1
        if isinstance(sp, PartitionSpace):
            blocks[int(sp.parse(ob.key).max()) + 1] += 1
    for ob in obs:
        sp = um.items[ob.item].space
        if isinstance(sp, PartitionSpace):
            for g in um.columns:
                p = um.pred(ob.item, g.members[0])
                if p.kind == "det" and not sp.is_special(p.key):
                    mblocks[int(sp.parse(p.key).max()) + 1] += 1
    out["wrong_nonexact_distance"] = dict(sorted(dist.items()))
    if ad:
        out["near_wrong_adds_drops"] = dict(sorted(ad.items()))
    if popfrac:
        out["wrong_set_fraction"] = {str(k): v for k, v in sorted(popfrac.items())}
    if blocks:
        out["wrong_blocks"] = dict(sorted(blocks.items()))
        tot = sum(mblocks.values())
        out["member_blocks_share"] = {b: round(v / tot, 3) for b, v in sorted(mblocks.items())}
    return out


def diagnose_job(args: tuple) -> dict[str, Any]:
    set_name, name, run_ids, cands = args
    out: dict[str, Any] = {}
    base = UnitModel(P._unit(set_name, name))
    for rid in run_ids:
        obs, _ = base.observations(responses(name, rid))
        out[rid] = {"answers": describe_answers(base, obs), "ladder": {}}
    for cand in cands:
        noise = NoiseModel.parse(cand)
        if noise.cells == "adds-drops" and "colouring" in name:
            continue
        um = base if noise.is_default else UnitModel(P._unit(set_name, name), noise=noise)
        for rid in run_ids:
            obs, _ = um.observations(responses(name, rid))
            T = um.tensors(obs)
            r = em(T)
            st = r.state if r.state is not None else {"pi": r.pi, "eps": r.eps[:, None], "g": trunc_geom(r.rho), "rho": r.rho}
            st1 = {k: v[:1] for k, v in st.items()}
            row = {"loglik": float(r.loglik[0]), "n_params": n_params(um, T, noise), "pi0": float(r.pi[0, -1]),
                   "eps": float(r.eps[0]), "kernel": np.round(st1["g"][0], 3).tolist(), "mass": mass_shares(T, st1),
                   "top": sorted(((round(float(p), 3), lab) for p, lab in zip(r.pi[0, :-1], T.labels)), reverse=True)[:4]}
            if "tau" in st1:
                row["tau"] = float(st1["tau"][0])
            if st1["eps"].shape[1] > 1:
                row["eps_by_group"] = {lab: round(float(e), 3) for lab, e in zip(T.labels, st1["eps"][0])}
            out[rid]["ladder"][cand] = row
    return {"unit": name, "runs": P.to_jsonable(out)}


def cmd_diagnose(a: argparse.Namespace) -> int:
    t0 = time.time()
    targets = load(a.runs_root)
    by_unit: dict[tuple[str, str], list[str]] = defaultdict(list)
    for s, n, r in targets:
        by_unit[(s, n)].append(r)
    cands = list(CANDIDATES)
    with mp.get_context("fork").Pool(a.workers) as pool:
        res = pool.map(diagnose_job, [(s, n, rs, cands) for (s, n), rs in by_unit.items()], chunksize=1)
    doc = {"command": " ".join(sys.argv), "git": P.git_state(), "candidates": {k: v.to_json() for k, v in CANDIDATES.items()},
           "units": {r["unit"]: r["runs"] for r in res}, "seconds": round(time.time() - t0)}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    print(f"wrote {a.out} ({round(time.time() - t0)} s)")
    return 0


# =============================================================================================
# recurrence: does the fitted model repeat wrong answers as often as the model does?
# =============================================================================================

# the runs redrawn with --samples 2 (PR #51): sample 0 is the 2026-11-18 response, sample 1 a new draw
REPEAT_RUNS = [f"2026-11-18-{s}-{m}" for s in ("pc20", "pc40") for m in
               ("qwen3-14b-direct", "qwen3-32b-direct", "gpt-oss-20b-thinking-low", "gpt-oss-120b-thinking-low")]


def answer_class(um: UnitModel, i: int, y: str) -> str:
    """'special' (a special token), 'member' (a deterministic member's answer or in a set member's solutions),
    else 'unmatched'."""
    if um.items[i].space.is_special(y):
        return "special"
    for g in um.columns:
        p = um.pred(i, g.members[0])
        if p.kind == "det" and p.key == y or p.kind == "set" and p.sol.contains(y):
            return "member"
    return "unmatched"


def fitted_scenario(um: UnitModel, cand: str, rep: dict[str, Any]) -> Scenario:
    planted, q = planted_of(rep)
    noise = NoiseModel.parse(cand)
    st = rep["fit"]["state"]
    if noise.is_default:
        return Scenario("fit", "mix", weights=planted, q=q, eps=round(float(st["eps"][0]), 4), rho=round(float(st["rho"]), 4))
    prm = noise_params({k: np.asarray(v) for k, v in st.items()}, noise, [g.members[0] for g in um.columns],
                       um.strata_index()[0] if noise.q == "strata" else None)
    return Scenario("fit", "mix", weights=planted, q=q, params=prm)


def recurrence_job(args: tuple) -> dict[str, Any]:
    """Per item: the fitted model's probability that two independent draws are the same wrong answer, by the
    first draw's class (Monte Carlo over `pairs` pairs of whole data sets)."""
    set_name, name, run_id, cand, rep, pairs = args
    um = unit_model(set_name, name, NoiseModel.parse(cand))
    sc = fitted_scenario(um, cand, rep)
    rng = np.random.default_rng(P.job_seed("recurrence", name, run_id, cand))
    n = len(um.items)
    hits = {c: np.zeros(n) for c in ("special", "member", "unmatched")}
    cls_cache: dict[tuple[int, str], tuple[bool, str]] = {}
    for _ in range(pairs):
        a, b = simulate(um, sc, rng), simulate(um, sc, rng)
        for oa, ob in zip(a, b):
            if oa.key != ob.key:
                continue
            k = (oa.item, oa.key)
            if k not in cls_cache:
                cls_cache[k] = (agreement.is_correct(um, oa.item, oa.key), answer_class(um, oa.item, oa.key))
            right, c = cls_cache[k]
            if not right:
                hits[c][oa.item] += 1
    ids = [it["item_id"] for it in um.unit.items]
    return {"unit": name, "run_id": run_id, "items": ids, "pairs": pairs,
            "p_same_wrong": {c: (h / pairs).tolist() for c, h in hits.items()}}


def cmd_recurrence(a: argparse.Namespace) -> int:
    t0 = time.time()
    targets = [t for t in load(a.runs_root) if t[2] in REPEAT_RUNS]
    jobs = []
    for cand in a.noise.split(","):
        if cand == "M0":
            fits = load_m0_fits()
        else:
            fits = json.loads((OUT_DIR / f"fits_{cand}.json").read_text())["fits"]
        for s, n, r in targets:
            if n in fits and r in fits[n]:
                jobs.append((s, n, r, cand, fits[n][r], a.pairs))
    with mp.get_context("fork").Pool(a.workers) as pool:
        res = pool.map(recurrence_job, jobs, chunksize=1)
        observed = pool.map(observed_job, [(s, n, r, str(a.repeats)) for s, n, r in targets], chunksize=1) if a.repeats else []
    out: dict[str, Any] = defaultdict(lambda: defaultdict(dict))
    for (s, n, r, cand, _, _), x in zip(jobs, res):
        out[cand][n][r] = x
    obs_out: dict[str, Any] = defaultdict(dict)
    for (s, n, r), x in zip(targets, observed):
        obs_out[n][r] = x
    doc = {"command": " ".join(sys.argv), "git": P.git_state(), "pairs": a.pairs, "predicted": out,
           "observed": obs_out, "seconds": round(time.time() - t0)}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(P.to_jsonable(doc), indent=1, sort_keys=True) + "\n")
    print(f"wrote {a.out} ({round(time.time() - t0)} s)")
    return 0


def load_m0_fits() -> dict[str, dict[str, Any]]:
    """The committed (M0) fits in this script's layout: weights, eps, rho and the groups."""
    ref = json.loads((REPO / "analysis" / "out" / "prelim_2026_11_18.json").read_text())
    out: dict[str, dict[str, Any]] = defaultdict(dict)
    for n, runs in ref["fits"].items():
        for r, rep in runs.items():
            out[n][r] = {"fit": {"weights": rep["fit"]["weights"], "state": {"eps": [rep["fit"]["eps"]], "rho": rep["fit"]["rho"]}},
                         "groups": rep["diagnostics"]["groups"]}
    return out


def observed_recurrence(repeat_root: Path, name: str, run_id: str, um: UnitModel) -> dict[str, Any]:
    """From a repeat run: per item answered ok (on the channel) in both samples, whether both are wrong and
    equal, by sample 0's class."""
    from reasoning_heuristics.identify.records import from_scored

    rid = run_id.replace("2026-11-18-", "2026-11-19-repeat-")
    resp, _ = from_scored(repeat_root / rid / "scored.jsonl.gz")
    by: dict[str, dict[int, Any]] = defaultdict(dict)
    for r in resp:
        if r.item_id in um.unit.index:
            by[r.item_id][r.sample] = r
    out = {}
    for iid, d in by.items():
        if 0 not in d or 1 not in d:
            continue
        obs, _ = um.observations([d[0], d[1]])
        if len(obs) != 2:
            continue
        i, y0, y1 = obs[0].item, obs[0].key, obs[1].key
        w0, w1 = not agreement.is_correct(um, i, y0), not agreement.is_correct(um, i, y1)
        out[iid] = {"both_wrong": w0 and w1, "same_wrong": w0 and w1 and y0 == y1, "class": answer_class(um, i, y0)}
    return out


def observed_job(args: tuple) -> dict[str, Any]:
    set_name, name, run_id, root = args
    return observed_recurrence(Path(root), name, run_id, UnitModel(P._unit(set_name, name)))


def recurrence_table(paths: list[Path]) -> str:
    """Observed against predicted recurrence of wrong answers, per fit with repeats, by sample 0's class: the
    number of items answered twice whose two answers are the same wrong answer, observed, and expected under
    each fitted model (the sum over those items of its probability)."""
    preds: dict[str, Any] = {}
    observed: dict[str, Any] = {}
    for p in paths:
        doc = json.loads(p.read_text())
        preds.update(doc["predicted"])
        for n, runs in doc.get("observed", {}).items():
            observed.setdefault(n, {}).update(runs)
    cands = [c for c in ("M0", "KEQ", "KEQ-r", "SEQ-r") if c in preds]
    rows = []
    for name in ("C_E2/colouring", "C_E2/knapsack", "AH_E5/SAT", "C_E5/3-SAT (partial assignment given)"):
        for run_id in REPEAT_RUNS:
            ob = observed.get(name, {}).get(run_id)
            if ob is None:
                continue
            items = list(ob)
            n = len(items)
            row = [name, run_label_short(run_id), n]
            for c in ("unmatched", "member", "special"):
                k = sum(1 for iid in items if ob[iid]["same_wrong"] and ob[iid]["class"] == c)
                cells = [f"{k}"]
                for cand in cands:
                    x = preds[cand].get(name, {}).get(run_id)
                    if x is None:
                        cells.append("–")
                        continue
                    idx = {iid: j for j, iid in enumerate(x["items"])}
                    cells.append(f"{sum(x['p_same_wrong'][c][idx[iid]] for iid in items):.1f}")
                row.append(" / ".join(cells))
            rows.append(row)
            continue
            items = [iid for iid in ob]
            n = len(items)
            row = [name, run_id.split("-", 4)[-1], n]
            for c in ("unmatched", "member", "special"):
                k = sum(1 for iid in items if ob[iid]["same_wrong"] and ob[iid]["class"] == c)
                cells = [f"{k}"]
                for cand in cands:
                    x = preds[cand].get(name, {}).get(run_id)
                    if x is None:
                        cells.append("–")
                        continue
                    idx = {iid: j for j, iid in enumerate(x["items"])}
                    e = sum(x["p_same_wrong"][c][idx[iid]] for iid in items)
                    cells.append(f"{e:.1f}")
                row.append(" / ".join(cells))
            rows.append(row)
    head = " / ".join(["observed"] + cands)
    return md_table(["Unit", "Run", "Items answered twice"] + [f"{c}: {head}" for c in ("unmatched", "member's answer", "special token")], rows)


def run_label_short(run_id: str) -> str:
    rest = run_id.split("-", 4)[-1]
    return (rest.replace("qwen3-14b", "Qwen3-14B").replace("qwen3-32b", "Qwen3-32B").replace("-thinking-low", " low effort")
            .replace("-direct", " direct"))


def md_table(header: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    return "\n".join(out + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


# =============================================================================================
# main
# =============================================================================================


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fits")
    f.add_argument("--noise", required=True, help="a name in noise.CANDIDATES or an option string")
    f.add_argument("--runs-root", type=Path, default=REPO / "data" / "runs")
    f.add_argument("--n-boot", type=int, default=2000)
    f.add_argument("--recovery-reps", type=int, default=100)
    f.add_argument("--recovery-boot", type=int, default=200,
                   help="bootstrap draws per refit of a fake data set; 0: no refits, the predictive checks only")
    f.add_argument("--workers", type=int, default=3)
    f.add_argument("--only", default=None, help="';'-separated substrings of 'unit run_id' to keep (for timing)")
    f.add_argument("--out", type=Path, required=True)
    d = sub.add_parser("diagnose")
    d.add_argument("--runs-root", type=Path, default=REPO / "data" / "runs")
    d.add_argument("--workers", type=int, default=3)
    d.add_argument("--out", type=Path, default=OUT_DIR / "diagnosis.json")
    t = sub.add_parser("table")
    t.add_argument("--dir", type=Path, default=OUT_DIR)
    rc = sub.add_parser("recurrence", help="predicted recurrence of wrong answers under fitted models (the box)")
    rc.add_argument("--noise", default="M0", help="','-separated candidates (M0, or ones with fits_<name>.json)")
    rc.add_argument("--runs-root", type=Path, default=REPO / "data" / "runs")
    rc.add_argument("--pairs", type=int, default=400)
    rc.add_argument("--workers", type=int, default=3)
    rc.add_argument("--out", type=Path, default=OUT_DIR / "recurrence.json")
    rc.add_argument("--repeats", type=Path, default=None,
                    help="a directory holding 2026-11-19-repeat-*/scored.jsonl.gz (PR #51): also the observed recurrence")
    rt = sub.add_parser("recurrence-table", help="observed against predicted (from `recurrence` outputs)")
    rt.add_argument("paths", type=Path, nargs="+")
    a = ap.parse_args(argv)
    if a.cmd == "recurrence":
        return cmd_recurrence(a)
    if a.cmd == "recurrence-table":
        print(recurrence_table(a.paths))
        return 0
    if a.cmd == "fits":
        return cmd_fits(a)
    if a.cmd == "diagnose":
        return cmd_diagnose(a)
    from noise_model_tables import main as tables  # noqa: E402

    return tables(a.dir)


if __name__ == "__main__":
    raise SystemExit(main())
