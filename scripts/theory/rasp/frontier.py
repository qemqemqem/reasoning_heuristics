"""Length vs accuracy for every member, the Pareto frontier, two-part MDL winners, and
average sensitivity.  Writes results.json and a figure next to the theory note.

    python frontier.py [--n 400] [--seed 0]

Training-like distributions (stated assumptions, see T2 section 4):
  SAT-DEC/puzzle  mixed-width CNF (15% units, 35% binary, 50% ternary), n 4-10, m/n 0.5-3
  SAT-DEC/bench   random 3-SAT, n 8-14, alpha 3.0-5.5 (benchmark-like, near threshold)
  SAT-VAL         satisfiable random 3-SAT, n 6-12, alpha 1.5-4.2; target = a mentioned var
  ENT             2-4 premises over 3-4 atoms, consistent, conclusion atom mentioned
  COL             planted 3-colourable G(n,p), n 6-12, p 0.3-0.6; success = proper, <= 3 colours
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time

import numpy as np

import instances as I
import programs_col as PC
import programs_ent as PE
import programs_sat as PS
import search_refs as SR
from rasp import last, measure

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.normpath(os.path.join(HERE, "../../../docs/theory"))
BITS_PER_PRIM = 16


def h2(p):
    p = min(max(p, 1e-9), 1 - 1e-9)
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


# ============================================================================ data


def gen_sat_puzzle(rng):
    n = rng.randint(4, 10)
    m = max(1, round(rng.uniform(0.5, 3.0) * n))
    cl = PS.mixed_cnf(n, m, rng)
    return cl, n, int(I.satisfiable(cl, n))


def gen_sat_bench(rng):
    n = rng.randint(8, 14)
    cl = I.random_ksat(n, round(rng.uniform(3.0, 5.5) * n), 3, rng)
    return cl, n, int(I.satisfiable(cl, n))


def gen_sat_val(rng):
    while True:
        n = rng.randint(6, 12)
        cl = I.random_ksat(n, max(2, round(rng.uniform(1.5, 4.2) * n)), 3, rng)
        if not I.satisfiable(cl, n):
            continue
        v = rng.choice(sorted({abs(l) for c in cl for l in c}))
        ok = (int(I.value_ok(cl, n, v, False)), int(I.value_ok(cl, n, v, True)))
        return cl, n, v, ok


def gen_col(rng):
    while True:
        n = rng.randint(6, 12)
        edges = I.planted_colourable(n, 3, rng.uniform(0.3, 0.6), rng)
        if edges:
            n = max(max(e) for e in edges)
            return n, edges


# ============================================================================ members

SAT_DEC_RASP = {
    "ALWAYS-SAT": PS.always_sat,
    "DENSITY": None,                      # theta tuned on the training set, set below
    "UP-1c": lambda s: PS.up_causal(s, 1),
    "UP-2c": lambda s: PS.up_causal(s, 2),
    "UP-3c": lambda s: PS.up_causal(s, 3),
    "PROBE-2": lambda s: PS.probe(s, 2),
    "PROBE-4": lambda s: PS.probe(s, 4),
}
SAT_VAL_RASP = {
    "CONST-TRUE": PS.always_sat,
    "POLARITY": PS.polarity,
    "BP-1c": lambda s: PS.bp_causal(s, 1),
    "BP-2c": lambda s: PS.bp_causal(s, 2),
}
ENT_RASP = {
    "ALWAYS-NO": PE.always_no,
    "MATCH": PE.match,
    "PRIMACY": PE.primacy,
    "UP-0 (ECHO)": lambda s: PE.up(s, 0),
    "UP-1": lambda s: PE.up(s, 1),
    "UP-2": lambda s: PE.up(s, 2),
    "FIRST-0": lambda s: PE.up(s, 0, first=True),
    "FIRST.UP-1": lambda s: PE.up(s, 1, first=True),
    "FIRST.UP-2": lambda s: PE.up(s, 2, first=True),
    "BICOND.UP-1": lambda s: PE.up(s, 1, bicond=True),
    "BICOND.UP-2": lambda s: PE.up(s, 2, bicond=True),
    "PROBE-4": lambda s: PE.probe(s, 4),
    "PROBE-16": lambda s: PE.probe(s, 16),
}

# Per-step (thinking) programs whose length is an ESTIMATE from measured components
# (verbose copy-evaluate traces; see T2 section 3.4).  FIRST-FIT (verbose) is measured.
PER_STEP_EST = {
    "COL": {"FIRST-FIT (verbose)": (53, "measured"), "DSATUR (verbose)": (90, "est"),
            "MIN-CONFLICTS-20 (FF + repair)": (80, "est"), "LOCAL-3 (in-prompt, direct)": (35, "est")},
    "SAT-DEC thinking, n=20": {"UC (no backtrack)": (65, "est"), "WALK-k": (85, "est"),
                               "DPLL-b (default UNSAT)": (80, "est"), "ALWAYS-SAT": (1, "measured")},
}


def tune_density(data):
    best = None
    for th in range(0, 41):
        acc = np.mean([PS.ref_density(cl, n, th) == y for cl, n, y in data])
        if best is None or acc > best[1]:
            best = (th, acc)
    return best[0]


# ============================================================================ evaluation


def eval_sat_dec(data, theta):
    progs = dict(SAT_DEC_RASP)
    progs["DENSITY"] = lambda s, th=theta: PS.density(s, th)
    acc = {}
    for name, prog in progs.items():
        acc[name] = float(np.mean([last(prog(I.cnf_tokens(cl))) == y for cl, n, y in data]))
    acc["UP-fix (non-causal)"] = float(np.mean([PS.ref_up_full(cl, n) == y for cl, n, y in data]))
    acc["EXACT"] = 1.0
    sat_rate = float(np.mean([y for _, _, y in data]))
    return acc, sat_rate


def eval_sat_val(data):
    acc = {}
    for name, prog in SAT_VAL_RASP.items():
        acc[name] = float(np.mean([ok[last(prog(I.cnf_tokens(cl, v)))] for cl, n, v, ok in data]))
    for t in (1, 2, 5):
        acc[f"BP-{t} (non-causal)"] = float(np.mean([ok[PS.ref_bp(cl, v, t)] for cl, n, v, ok in data]))
    acc["EXACT"] = 1.0
    return acc


def eval_ent(data, rng):
    acc = {}
    for name, prog in ENT_RASP.items():
        acc[name] = float(np.mean([last(prog(I.entailment_tokens(p, c))) == y for p, c, na, y in data]))
    acc["ALWAYS-YES"] = float(np.mean([y == 1 for *_, y in data]))
    acc["MM (initial models)"] = float(np.mean([PE.ref_mm(p, c, na) == y for p, c, na, y in data]))
    for m in (1, 2, 4, 8):
        acc[f"SAMPLE-{m}"] = float(np.mean([PE.ref_sample(p, c, na, m, rng) == y for p, c, na, y in data]))
    acc["FIRST.EXACT"] = float(np.mean([PE.ref_exact(_first(p), c, na) == y for p, c, na, y in data]))
    acc["BICOND.EXACT"] = float(np.mean([PE.ref_exact(_bicond(p), c, na) == y for p, c, na, y in data
                                         if I.consistent(_bicond(p), na)] or [0]))
    acc["NOISY-EXACT (2%/row)"] = float(np.mean([PE.ref_noisy_exact(p, c, na, 0.02, rng) == y for p, c, na, y in data]))
    acc["EXACT"] = 1.0
    return acc


def _first(prem):
    return [("fact", (ls[0],)) if k == "or" else (k, ls) for k, ls in prem]


def _bicond(prem):
    out = []
    for k, ls in prem:
        out.append((k, ls))
        if k == "if":
            out.append(("if", (ls[1], ls[0])))
    return out


def eval_col(data, rng, rasp_check=30):
    def ok(n, edges, col):
        return I.proper(edges, col) and max(col.values()) <= 3
    acc = {
        "RANDOM": np.mean([ok(n, e, PC.ref_random(n, e, 3, rng)) for n, e in data]),
        "FIRST-FIT": np.mean([ok(n, e, PC.ref_first_fit(n, e)) for n, e in data]),
        "RO-FIRST-FIT": np.mean([ok(n, e, PC.ref_random_order_ff(n, e, rng)) for n, e in data]),
        "DSATUR": np.mean([ok(n, e, PC.ref_dsatur(n, e)) for n, e in data]),
        "LOCAL-1": np.mean([ok(n, e, PC.ref_local(n, e, 1)) for n, e in data]),
        "LOCAL-2": np.mean([ok(n, e, PC.ref_local(n, e, 2)) for n, e in data]),
        "LOCAL-3": np.mean([ok(n, e, PC.ref_local(n, e, 3)) for n, e in data]),
        "MIN-CONFLICTS-20": np.mean([ok(n, e, PC.ref_min_conflicts(n, e, 3, 20, rng)) for n, e in data]),
        "MIN-CONFLICTS-100": np.mean([ok(n, e, PC.ref_min_conflicts(n, e, 3, 100, rng)) for n, e in data]),
        "EXACT": 1.0,
    }
    # spot-check that the RASP per-step programs reproduce FIRST-FIT on these instances
    mism = 0
    for n, e in data[:rasp_check]:
        ref = PC.ref_first_fit(n, e)
        mism += PC.decode_verbose(PC.run(PC.ff_verbose_step, I.colour_prompt(e))) != ref
        mism += PC.decode_terse(PC.run(PC.ff_terse_step, I.colour_prompt(e))) != ref
    return {k: float(v) for k, v in acc.items()}, mism


# ============================================================================ thinking regime


def eval_thinking(rng, sizes=(10, 20, 30, 40), per=40, budget_tokens=32000, tok_per_check=6):
    """SAT-DEC on random 3-SAT at alpha = 4.26 under a token budget.

    Token-cost assumptions (verbose copy-evaluate traces; see T2 section 5):
      DPLL decision + propagation  ~ tok_per_check * m tokens
      WalkSAT flip (re-check clauses of the flipped var + break counts) ~ tok_per_check * 9 * alpha
      UC assignment (update clauses of the var) ~ tok_per_check * 3 * alpha
    """
    rows = []
    for n in sizes:
        m = round(4.26 * n)
        b = budget_tokens // (tok_per_check * m)
        k = int(budget_tokens // (tok_per_check * 9 * 4.26))
        data = []
        while len(data) < per:
            cl = I.random_ksat(n, m, 3, rng)
            data.append((cl, int(I.satisfiable(cl, n))))
        sat_rate = np.mean([y for _, y in data])
        r = {"n": n, "m": m, "sat_rate": float(sat_rate), "dpll_decisions_in_budget": int(b),
             "walk_flips_in_budget": k,
             "DPLL-b (default SAT)": float(np.mean([SR.dpll_b(cl, n, b, 1)[0] == y for cl, y in data])),
             "DPLL-b (default UNSAT)": float(np.mean([SR.dpll_b(cl, n, b, 0)[0] == y for cl, y in data])),
             "WALK-k": float(np.mean([SR.walk_k(cl, n, k, rng=rng)[0] == y for cl, y in data])),
             "UC (no backtrack)": float(np.mean([SR.unit_clause(cl, n, rng)[0] == y for cl, y in data])),
             "ALWAYS-SAT": float(sat_rate),
             "UP-fix": float(np.mean([PS.ref_up_full(cl, n) == y for cl, y in data]))}
        rows.append(r)
    return rows


# ============================================================================ sensitivity


def sensitivity_sat(data, fns, k=12, rng=random):
    """Mean fraction of single-literal sign flips that change the answer."""
    out = {name: [] for name in fns}
    for cl, n, y in data:
        pos = [(i, j) for i, c in enumerate(cl) for j in range(len(c))]
        picks = rng.sample(pos, min(k, len(pos)))
        base = {name: f(cl, n) for name, f in fns.items()}
        flips = {name: 0 for name in fns}
        for i, j in picks:
            cl2 = [list(c) for c in cl]
            cl2[i][j] = -cl2[i][j]
            cl2 = [tuple(c) for c in cl2]
            for name, f in fns.items():
                flips[name] += f(cl2, n) != base[name]
        for name in fns:
            out[name].append(flips[name] / len(picks))
    return {name: float(np.mean(v)) for name, v in out.items()}


def sensitivity_ent(data, progs, rng=random, k=6):
    """Mean fraction of single negation toggles (one premise literal) that change the answer."""
    out = {name: [] for name in progs}
    for p, c, na, y in data:
        lits = [(i, j) for i, (kd, ls) in enumerate(p) for j in range(len(ls))]
        picks = rng.sample(lits, min(k, len(lits)))
        base = {name: f(p, c, na) for name, f in progs.items()}
        flips = {name: 0 for name in progs}
        for i, j in picks:
            p2 = [(kd, list(ls)) for kd, ls in p]
            p2[i][1][j] = -p2[i][1][j]
            p2 = [(kd, tuple(ls)) for kd, ls in p2]
            if not I.consistent(p2, na):
                continue
            for name, f in progs.items():
                flips[name] += f(p2, c, na) != base[name]
        for name in progs:
            out[name].append(flips[name] / len(picks))
    return {name: float(np.mean(v)) for name, v in out.items()}


# ============================================================================ frontier / MDL


def pareto(members):
    """members: list of (name, length, acc). Return names on the frontier (non-dominated)."""
    front = []
    for name, L, a in members:
        dominated = any((L2 <= L and a2 > a + 1e-9) or (L2 < L and a2 >= a - 1e-9)
                        for n2, L2, a2 in members if n2 != name)
        if not dominated:
            front.append(name)
    return front


def mdl_path(members, Ns=(10, 30, 100, 300, 1e3, 3e3, 1e4, 1e5, 1e6, 1e7)):
    path = []
    for N in Ns:
        best = min(members, key=lambda t: BITS_PER_PRIM * t[1] + N * h2(1 - t[2]))
        path.append((N, best[0]))
    return path


def capacity_path(members, base=1.5, Ns=(1e2, 1e3, 1e4, 1e5, 1e6, 1e8)):
    """Sample-complexity reading: a member is learnable from N examples iff base**heads <= N;
    pick the most accurate learnable one (heads = attention ops)."""
    path = []
    for N in Ns:
        ok = [t for t in members if base ** t[1] <= N]
        path.append((N, max(ok, key=lambda t: t[2])[0] if ok else None))
    return path


# ============================================================================ main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--no-think", action="store_true")
    args = ap.parse_args()
    rng = random.Random(args.seed)
    t0 = time.time()
    res = {"assumptions": __doc__}

    # ---- lengths
    ex_cnf = I.cnf_tokens(I.random_ksat(6, 10, 3, rng))
    ex_val = I.cnf_tokens(I.random_ksat(6, 10, 3, rng), 2)
    ex_ent = I.entailment_tokens([("or", (1, -2)), ("if", (1, 3)), ("fact", (-3,))], 2)
    lengths = {}
    for task, progs, ex in [("SAT-DEC", {**SAT_DEC_RASP, "DENSITY": PS.density}, ex_cnf),
                            ("SAT-VAL", SAT_VAL_RASP, ex_val), ("ENT", ENT_RASP, ex_ent)]:
        for name, prog in progs.items():
            r = measure(name, prog, ex)
            lengths[(task, name)] = r
    edges = I.planted_colourable(6, 3, 0.5, rng) or [(1, 2)]
    pr = I.colour_prompt(edges)
    lengths[("COL", "FIRST-FIT (terse, set ext.)")] = measure("FF-terse", PC.ff_terse_step, pr + [1])
    lengths[("COL", "FIRST-FIT (verbose)")] = measure("FF-verbose", PC.ff_verbose_step, pr + [1, PC.COLON])
    res["lengths"] = {f"{t}|{n}": vars(r) for (t, n), r in lengths.items()}
    print(f"[{time.time()-t0:.0f}s] lengths done", file=sys.stderr)

    # ---- data
    sat_p = [gen_sat_puzzle(rng) for _ in range(args.n)]
    sat_b = [gen_sat_bench(rng) for _ in range(args.n)]
    sat_v = [gen_sat_val(rng) for _ in range(args.n)]
    ent = []
    for _ in range(args.n):
        p, c, na = I.random_entailment_item(rng)
        ent.append((p, c, na, int(I.entails(p, c, na))))
    col = [gen_col(rng) for _ in range(args.n)]
    print(f"[{time.time()-t0:.0f}s] data done", file=sys.stderr)

    theta = tune_density(sat_p)
    theta_b = tune_density(sat_b)
    res["density_theta"] = {"puzzle": theta, "bench": theta_b}
    acc_p, rate_p = eval_sat_dec(sat_p, theta)
    acc_b, rate_b = eval_sat_dec(sat_b, theta_b)
    res["SAT-DEC/puzzle"] = {"acc": acc_p, "sat_rate": rate_p}
    res["SAT-DEC/bench"] = {"acc": acc_b, "sat_rate": rate_b}
    res["SAT-VAL"] = {"acc": eval_sat_val(sat_v),
                      "true_ok_rate": float(np.mean([ok[1] for *_, ok in sat_v]))}
    res["ENT"] = {"acc": eval_ent(ent, rng), "yes_rate": float(np.mean([y for *_, y in ent]))}
    col_acc, col_mism = eval_col(col, rng)
    res["COL"] = {"acc": col_acc, "rasp_ff_mismatches_on_30": col_mism}
    print(f"[{time.time()-t0:.0f}s] accuracies done", file=sys.stderr)

    # ---- sensitivity (answer flips under single local edits), on 150 items
    sfns = {"ALWAYS-SAT": lambda cl, n: 1, "DENSITY": lambda cl, n: PS.ref_density(cl, n, theta),
            "UP-1c": lambda cl, n: PS.ref_up_causal(cl, 1), "UP-2c": lambda cl, n: PS.ref_up_causal(cl, 2),
            "UP-3c": lambda cl, n: PS.ref_up_causal(cl, 3), "PROBE-2": lambda cl, n: PS.ref_probe(cl, 2),
            "PROBE-4": lambda cl, n: PS.ref_probe(cl, 4),
            "UP-fix (non-causal)": lambda cl, n: PS.ref_up_full(cl, n),
            "EXACT": lambda cl, n: int(I.satisfiable(cl, n))}
    res["sens_SAT-DEC/puzzle"] = sensitivity_sat(sat_p[:150], sfns, rng=rng)
    efns = {name: (lambda p, c, na, prog=prog: last(prog(I.entailment_tokens(p, c))))
            for name, prog in ENT_RASP.items()}
    efns["MM (initial models)"] = PE.ref_mm
    efns["EXACT"] = PE.ref_exact
    res["sens_ENT"] = sensitivity_ent(ent[:150], efns, rng=rng)
    print(f"[{time.time()-t0:.0f}s] sensitivity done", file=sys.stderr)

    # ---- frontier + MDL per task
    res["frontier"] = {}
    for task, key in [("SAT-DEC", "SAT-DEC/puzzle"), ("SAT-DEC", "SAT-DEC/bench"),
                      ("SAT-VAL", "SAT-VAL"), ("ENT", "ENT")]:
        mem = [(n, lengths[(task, n)].length, res[key]["acc"][n]) for (t, n) in lengths if t == task]
        memh = [(n, lengths[(task, n)].heads, res[key]["acc"][n]) for (t, n) in lengths if t == task]
        res["frontier"][key] = {"by_length": pareto(mem), "by_heads": pareto(memh),
                                "mdl_path": mdl_path(mem),
                                "capacity_path_b1.5": capacity_path(memh, 1.5),
                                "capacity_path_b2": capacity_path(memh, 2.0)}

    res["label_mixture_ENT"] = label_mixture(ent)
    if not args.no_think:
        res["thinking"] = eval_thinking(rng)
        print(f"[{time.time()-t0:.0f}s] thinking done", file=sys.stderr)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(res, f, indent=1, default=str)
    plot(res, lengths)
    print(f"[{time.time()-t0:.0f}s] wrote results.json and figure", file=sys.stderr)


def label_mixture(ent, qs=(0, .1, .2, .3, .4, .5, .6, .8, 1.0)):
    """If a share q of training labels follow a restricted reading R (FIRST, BICOND or MM)
    instead of validity, which equal-length member fits best?  Agreement with the mixed
    labels is (1-q)*acc_vs_exact + q*acc_vs_R."""
    readers = {"FIRST": lambda p, c, na: PE.ref_exact(_first(p), c, na),
               "BICOND": lambda p, c, na: (PE.ref_exact(_bicond(p), c, na)
                                           if I.consistent(_bicond(p), na) else 0),
               "MM": PE.ref_mm}
    progs = {"UP-2": lambda s: PE.up(s, 2), "FIRST.UP-2": lambda s: PE.up(s, 2, first=True),
             "BICOND.UP-2": lambda s: PE.up(s, 2, bicond=True), "MATCH": PE.match,
             "UP-0 (ECHO)": lambda s: PE.up(s, 0)}
    outs = {n: [last(f(I.entailment_tokens(p, c))) for p, c, na, y in ent] for n, f in progs.items()}
    res = {}
    for rname, rf in readers.items():
        lab = [rf(p, c, na) for p, c, na, y in ent]
        exact = [y for *_, y in ent]
        rows = []
        for q in qs:
            agree = {n: (1 - q) * np.mean(np.equal(o, exact)) + q * np.mean(np.equal(o, lab))
                     for n, o in outs.items()}
            rows.append((q, max(agree, key=agree.get), {n: round(float(a), 3) for n, a in agree.items()}))
        res[rname] = rows
    return res


def plot(res, lengths):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    panels = [("SAT-DEC", "SAT-DEC/puzzle"), ("SAT-DEC", "SAT-DEC/bench"), ("SAT-VAL", "SAT-VAL"), ("ENT", "ENT")]
    fig, axes = plt.subplots(1, 4, figsize=(17, 4.2))
    for ax, (task, key) in zip(axes, panels):
        mem = [(n, lengths[(task, n)].length, res[key]["acc"][n]) for (t, n) in lengths if t == task]
        front = set(res["frontier"][key]["by_length"])
        for n, L, a in mem:
            on = n in front
            ax.scatter(L, a, s=36, color="#1f5fbf" if on else "#9aa5b1", zorder=3)
            ax.annotate(n, (L, a), fontsize=7, xytext=(3, 3), textcoords="offset points")
        fr = sorted([(L, a) for n, L, a in mem if n in front])
        ax.step([p[0] for p in fr], [p[1] for p in fr], where="post", color="#1f5fbf", lw=1)
        ax.set_title(key, fontsize=10)
        ax.set_xlabel("RASP-L length (primitives)")
        ax.grid(alpha=.3)
    axes[0].set_ylabel("accuracy on training-like distribution")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "T2_frontier.png"), dpi=130)

    # per-step (thinking) panel: per-step program length vs iterated accuracy
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    think20 = next((r for r in res.get("thinking", []) if r["n"] == 20), None)
    for ax, (task, mem) in zip(axes, PER_STEP_EST.items()):
        for name, (L, kind) in mem.items():
            if task == "COL":
                key = name.split(" (")[0]
                key = {"MIN-CONFLICTS-20": "MIN-CONFLICTS-20", "LOCAL-3": "LOCAL-3"}.get(key, key)
                a = res["COL"]["acc"].get(key)
            else:
                a = think20.get(name) if think20 else None
            if a is None:
                continue
            ax.scatter(L, a, s=40, facecolors="#1f5fbf" if kind == "measured" else "none",
                       edgecolors="#1f5fbf")
            ax.annotate(name, (L, a), fontsize=7, xytext=(3, 3), textcoords="offset points")
        ax.set_title(task + " (hollow = estimated length)", fontsize=9)
        ax.set_xlabel("per-step program length (primitives)")
        ax.grid(alpha=.3)
    axes[0].set_ylabel("accuracy of the iterated heuristic")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "T2_perstep.png"), dpi=130)


if __name__ == "__main__":
    main()
