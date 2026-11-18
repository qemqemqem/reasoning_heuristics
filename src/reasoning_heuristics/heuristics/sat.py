"""SAT members: C0 one-shot scores, C1 GREEDY-σ, C2 unit/shortest-clause rules, C3 random
order, B1 UP-k, A1/A2 cues, A3 textbook transfer, H guesses, F WalkSAT, nuisance models,
and the exact solver.

Definitions follow C §1.3 and A/H §1.5. A clause is *satisfied* if some literal is true,
*falsified* if all its literals are false, *open* otherwise. Polarity-count ties resolve
to T. Fixed values (E5-STATE) are kept by every member; C0 members ignore them when
scoring the other variables ("state-blind").
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

import numpy as np

from reasoning_heuristics.heuristics.answers import assignment_key
from reasoning_heuristics.heuristics.base import Prediction, member
from reasoning_heuristics.heuristics.tasks import SatTask
from reasoning_heuristics.problems.coloring.graph import label_key
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.sat.cnf import CNF

D = "sat"


def effective_cnf(task: SatTask) -> CNF:
    """The formula the *stated* rule describes. Inverted rule: every literal flipped (F̄);
    partial inversion (A/H E5 P): only the marked clauses flipped."""
    if task.inverted:
        return task.cnf.with_clauses([[-l for l in c] for c in task.cnf.clauses])
    if task.inverted_clauses:
        marked = set(task.inverted_clauses)
        return task.cnf.with_clauses([[-l for l in c] if i in marked else list(c) for i, c in enumerate(task.cnf.clauses)])
    return task.cnf


def clause_state(c: tuple[int, ...], values: dict[int, bool]) -> tuple[str, list[int]]:
    vals = [S.lit_value(l, values) for l in c]
    if True in vals:
        return "sat", []
    open_lits = [l for l, v in zip(c, vals) if v is None]
    return ("falsified", []) if not open_lits else ("open", open_lits)


def _finish(cnf: CNF, values: dict[int, bool], trace: dict[str, Any]) -> Prediction:
    for v in range(1, cnf.n + 1):
        values.setdefault(v, True)
    assignment = S.to_assignment(cnf, values)
    trace["falsified"] = [f"C{i + 1}" for i in S.falsified_clauses(cnf, assignment)]
    return Prediction(assignment, trace)


def _start(task: SatTask, cnf: CNF) -> dict[int, bool]:
    return {cnf.index(k): v for k, v in task.fixed}


def resolve_var_order(task: SatTask, cnf: CNF, params: dict[str, Any]) -> list[int]:
    order = params.get("order", "MENTION")
    if order == "MENTION":
        mentioned = cnf.mention_order()
        return mentioned + [v for v in range(1, cnf.n + 1) if v not in mentioned]
    if order == "INDEX":
        return sorted(range(1, cnf.n + 1), key=lambda v: label_key(cnf.var_names[v - 1]))
    if order == "OUT":
        if task.answer_order is None:
            return [cnf.index(x) for x in params["sequence"]]
        return [cnf.index(x) for x in task.answer_order]
    if order == "EXPLICIT":
        return [cnf.index(x) for x in params["sequence"]]
    raise ValueError(f"unknown variable order {order}")


# --- C0 ---------------------------------------------------------------------------------


def _polarity_values(cnf: CNF, weight) -> dict[int, bool]:
    pos, neg = Counter(), Counter()
    for c in cnf.clauses:
        for l in c:
            (pos if l > 0 else neg)[abs(l)] += weight(c)
    return {v: pos[v] >= neg[v] for v in range(1, cnf.n + 1)}


def _c0(task: SatTask, values: dict[int, bool], name: str) -> Prediction:
    cnf = effective_cnf(task)
    start = _start(task, cnf)
    merged = {**values, **start}
    return _finish(cnf, merged, {"rule": name, "state_blind": True, "revisions": 0})


@member("POLARITY", "C0", D, "value = static majority sign of each variable over all clauses; never refers to earlier commitments")
def polarity(task: SatTask, params: dict[str, Any]) -> Prediction:
    return _c0(task, _polarity_values(effective_cnf(task), lambda c: 1), "POLARITY")


@member("JW", "C0", D, "Jeroslow-Wang: occurrences weighted 2^-|clause|; static majority")
def jw(task: SatTask, params: dict[str, Any]) -> Prediction:
    return _c0(task, _polarity_values(effective_cnf(task), lambda c: 2.0 ** -len(c)), "JW")


@member("MOMS", "C0", D, "polarity counted over minimum-width clauses only")
def moms(task: SatTask, params: dict[str, Any]) -> Prediction:
    cnf = effective_cnf(task)
    w = min(len(c) for c in cnf.clauses)
    short = cnf.with_clauses([c for c in cnf.clauses if len(c) == w])
    vals = _polarity_values(short, lambda c: 1)
    fallback = _polarity_values(cnf, lambda c: 1)
    mentioned = {abs(l) for c in short.clauses for l in c}
    return _c0(task, {v: (vals[v] if v in mentioned else fallback[v]) for v in fallback}, "MOMS")


@member("PURE+DEFAULT", "C0", D, "pure variables get their only sign; every other variable is set true")
def pure_default(task: SatTask, params: dict[str, Any]) -> Prediction:
    cnf = effective_cnf(task)
    signs: dict[int, set[bool]] = {}
    for c in cnf.clauses:
        for l in c:
            signs.setdefault(abs(l), set()).add(l > 0)
    return _c0(task, {v: (next(iter(signs[v])) if len(signs.get(v, ())) == 1 else True) for v in range(1, cnf.n + 1)}, "PURE+DEFAULT")


# --- C1 GREEDY-σ --------------------------------------------------------------------------


def greedy_run(cnf: CNF, order: list[int], start: dict[int, bool], mode: str) -> tuple[dict[int, bool] | None, dict[str, Any]]:
    values = dict(start)
    trace: dict[str, Any] = {"commit_order": [], "revisions": 0}
    for v in order:
        if v in values:
            continue
        p = q = 0
        for c in cnf.clauses:
            state, open_lits = clause_state(c, values)
            if state != "open":
                continue
            if v in open_lits:
                p += 1
            if -v in open_lits:
                q += 1
        values[v] = p >= q
        trace["commit_order"].append(cnf.var_names[v - 1])
        dead = [i for i, c in enumerate(cnf.clauses) if clause_state(c, values)[0] == "falsified"]
        if dead and "dead_end" not in trace:
            trace["dead_end"] = {"variable": cnf.var_names[v - 1], "clause": f"C{dead[0] + 1}"}
            if mode == "ABORT":
                return None, trace
    return values, trace


@member("GREEDY", "C1", D, "commits variables in order σ; value = sign with more open clauses given earlier commitments; no revisions")
def greedy(task: SatTask, params: dict[str, Any]) -> Prediction:
    cnf = effective_cnf(task)
    values, trace = greedy_run(cnf, resolve_var_order(task, cnf, params), _start(task, cnf), params.get("mode", "ABORT"))
    if values is None:
        return Prediction("UNSAT", trace)
    return _finish(cnf, values, trace)


@member("RO-GREEDY", "C3", D, "GREEDY in a uniformly random order; the order varies across samples", deterministic=False)
def ro_greedy(task: SatTask, params: dict[str, Any]) -> Prediction:
    cnf = effective_cnf(task)
    rng = np.random.default_rng(params.get("seed", 0))
    samples = params.get("samples", 1000)
    counts: Counter[str] = Counter()
    start = _start(task, cnf)
    free = [v for v in range(1, cnf.n + 1) if v not in start]
    for _ in range(samples):
        order = [free[i] for i in rng.permutation(len(free))]
        values, _ = greedy_run(cnf, order, start, params.get("mode", "ABORT"))
        counts["UNSAT" if values is None else assignment_key(S.to_assignment(cnf, values))] += 1
    top = counts.most_common(params.get("keep", 25))
    dist = {k: c / samples for k, c in top}
    if sum(dist.values()) < 1:
        dist["_other"] = 1 - sum(dist.values())
    return Prediction(None, {"samples": samples, "P(UNSAT)": counts["UNSAT"] / samples}, dist)


# --- C2 unit / shortest clause ------------------------------------------------------------


def _unit_style(task: SatTask, params: dict[str, Any], rule: str) -> Prediction:
    cnf = effective_cnf(task)
    values = _start(task, cnf)
    listing = resolve_var_order(task, cnf, {"order": "MENTION"})
    trace: dict[str, Any] = {"commit_order": [], "forced": [], "revisions": 0}
    while len(values) < cnf.n:
        states = [clause_state(c, values) for c in cnf.clauses]
        if any(s == "falsified" for s, _ in states):
            i = next(i for i, (s, _) in enumerate(states) if s == "falsified")
            trace["dead_end"] = f"C{i + 1}"
            return Prediction("UNSAT", trace)
        open_clauses = [(i, lits) for i, (s, lits) in enumerate(states) if s == "open"]
        chosen = None
        if rule == "UC":
            units = [(i, lits) for i, lits in open_clauses if len(lits) == 1]
            if units:
                chosen = units[0]
        elif rule == "GUC":
            if open_clauses:
                w = min(len(lits) for _, lits in open_clauses)
                chosen = next((i, lits) for i, lits in open_clauses if len(lits) == w)
        elif rule == "SC":
            for w in (1, 2):
                short = [(i, lits) for i, lits in open_clauses if len(lits) == w]
                if short:
                    chosen = short[0]
                    break
        else:
            raise ValueError(rule)
        if chosen is not None:
            lit = chosen[1][0]
            values[abs(lit)] = lit > 0
            trace["forced"].append(f"C{chosen[0] + 1}")
            trace["commit_order"].append(cnf.var_names[abs(lit) - 1])
        else:
            v = next(v for v in listing if v not in values)
            values[v] = True
            trace["commit_order"].append(cnf.var_names[v - 1])
    return _finish(cnf, values, trace)


@member("UC", "C2", D, "next commitment comes from a unit clause given the state ('forced'); else the first free variable set true; UNSAT at the first falsified clause")
def uc_det(task: SatTask, params: dict[str, Any]) -> Prediction:
    return _unit_style(task, params, "UC")


@member("GUC", "C2", D, "satisfies a literal of a shortest open clause at every step")
def guc_det(task: SatTask, params: dict[str, Any]) -> Prediction:
    return _unit_style(task, params, "GUC")


@member("SC", "C2", D, "prefers unit, then 2-literal open clauses; otherwise the first free variable set true")
def sc_det(task: SatTask, params: dict[str, Any]) -> Prediction:
    return _unit_style(task, params, "SC")


# --- B1 UP-k --------------------------------------------------------------------------------


def unit_propagate(cnf: CNF, start: dict[int, bool], rounds: int | None) -> tuple[dict[int, bool], bool, int]:
    """Stated unit clauses are facts; then `rounds` rounds of parallel unit propagation.

    Returns (values, refuted, rounds used)."""
    values = dict(start)
    for c in cnf.clauses:
        if len(c) == 1:
            if values.get(abs(c[0]), c[0] > 0) != (c[0] > 0):
                return values, True, 0
            values[abs(c[0])] = c[0] > 0
    r = 0
    while rounds is None or r < rounds:
        new: dict[int, bool] = {}
        for c in cnf.clauses:
            state, lits = clause_state(c, values)
            if state == "falsified":
                return values, True, r
            if state == "open" and len(lits) == 1:
                lit = lits[0]
                if new.get(abs(lit), lit > 0) != (lit > 0):
                    return values, True, r + 1
                new[abs(lit)] = lit > 0
        if not new:
            break
        values.update(new)
        r += 1
    refuted = any(clause_state(c, values)[0] == "falsified" for c in cnf.clauses)
    return values, refuted, r


@member("UP-k", "B1", D, "propagation steps only; no case splits; UNSAT only from a propagation conflict, else SAT by default")
def up_k(task: SatTask, params: dict[str, Any]) -> Prediction:
    cnf = effective_cnf(task)
    values, refuted, r = unit_propagate(cnf, _start(task, cnf), params.get("k"))
    trace = {"derived": [cnf.var_names[v - 1] + ("=T" if b else "=F") for v, b in values.items()], "rounds": r}
    return Prediction("UNSAT" if refuted else "SAT", trace)


# --- A cues -----------------------------------------------------------------------------------


def _decision_fill(answer: str) -> Prediction:
    return Prediction(answer, {"witness": "uniform fill" if answer == "SAT" else None, "set_valued": answer == "SAT"})


@member("ALWAYS-SAT", "A1", D, "a witness proposed without checking every constraint; no refutation attempted")
def always_sat(task: SatTask, params: dict[str, Any]) -> Prediction:
    return _decision_fill("SAT")


@member("ALWAYS-UNSAT", "A1", D, "GIVEUP early ('too many constraints to check'); no witness attempted")
def always_unsat(task: SatTask, params: dict[str, Any]) -> Prediction:
    return Prediction("UNSAT", {})


def cue_values(task: SatTask) -> dict[str, float]:
    cnf = task.cnf
    n_used = len(cnf.used_vars())
    n_decl = len(task.declared) if task.declared is not None else cnf.n
    return {"m": cnf.m, "n_used": n_used, "n_decl": n_decl, "alpha_U": cnf.m / n_used, "alpha_D": cnf.m / n_decl}


@member("DENSITY", "A2", D, "cites the clause-to-variable ratio as the reason; no closed refutation")
def density(task: SatTask, params: dict[str, Any]) -> Prediction:
    """Deterministic limit of the soft threshold: UNSAT iff α >= θ. variant U (used vars) or D (declared)."""
    cues = cue_values(task)
    phi = cues["alpha_U"] if params.get("variant", "U") == "U" else cues["alpha_D"]
    return _decision_fill("UNSAT" if phi >= params.get("theta", 4.26) else "SAT")


@member("LENGTH", "A2", D, "cites the number of clauses ('with this many clauses it is very likely unsatisfiable')")
def length(task: SatTask, params: dict[str, Any]) -> Prediction:
    phi = task.cnf.m if params.get("variant", "M") == "M" else params["tokens"]
    return _decision_fill("UNSAT" if phi >= params["theta"] else "SAT")


# --- H ------------------------------------------------------------------------------------------


@member("RANDOM", "H", D, "no procedure determines the verdict", deterministic=False)
def random_sat(task: SatTask, params: dict[str, Any]) -> Prediction:
    return Prediction(None, {"set_valued": True}, {"SAT": 0.5, "UNSAT": 0.5})


@member("SAMPLE-m", "H", D, "a few complete example assignments checked; UNSAT when none of them works", deterministic=False)
def sample_m(task: SatTask, params: dict[str, Any]) -> Prediction:
    cnf = effective_cnf(task)
    m = params.get("m", 8)
    n_decl = len(task.declared) if task.declared is not None else cnf.n
    s = S.count_solutions(cnf) * 2 ** (n_decl - cnf.n)
    p_sat = 1 - (1 - s / 2**n_decl) ** m
    return Prediction(None, {"n_solutions": s, "m": m}, {"SAT": p_sat, "UNSAT": 1 - p_sat})


@member("WALK", "F", D, "a full candidate, then repeated local flips of variables in violated clauses; never certifies UNSAT", deterministic=False)
def walksat(task: SatTask, params: dict[str, Any]) -> Prediction:
    """WalkSAT (noise 0.5) with `flips` flips from a random start; success rate over `runs` seeds.
    Default answer when it fails: UNSAT."""
    cnf = effective_cnf(task)
    flips, runs = params.get("flips", 200), params.get("runs", 30)
    rng = np.random.default_rng(params.get("seed", 0))
    clauses = [list(c) for c in cnf.clauses]
    successes = 0
    for _ in range(runs):
        vals = {v: bool(rng.integers(2)) for v in range(1, cnf.n + 1)}
        for _ in range(flips):
            unsat = [c for c in clauses if not any(S.lit_value(l, vals) for l in c)]
            if not unsat:
                break
            c = unsat[rng.integers(len(unsat))]
            if rng.random() < 0.5:
                v = abs(c[rng.integers(len(c))])
            else:
                def breaks(v: int) -> int:
                    vals[v] = not vals[v]
                    b = sum(1 for d in clauses if not any(S.lit_value(l, vals) for l in d))
                    vals[v] = not vals[v]
                    return b
                v = min((abs(l) for l in c), key=breaks)
            vals[v] = not vals[v]
        if all(any(S.lit_value(l, vals) for l in c) for c in clauses):
            successes += 1
    rate = successes / runs
    return Prediction(None, {"flips": flips, "runs": runs, "success_rate": rate}, {"SAT": rate, "UNSAT": 1 - rate})


# --- nuisance -------------------------------------------------------------------------------------


def dpll_steps(cnf: CNF, pure_literal: bool = False) -> int:
    from reasoning_heuristics.heuristics.search import search_sat

    _, trace = search_sat(cnf, {}, {"order": "MENTION", "value": "TRUE", "b": None, "pure": pure_literal})
    return trace["decisions"] + trace["propagations"]


@member("NOISY-EXACT", "nuisance", D, "systematic search with sporadic evaluation slips; errors symmetric", deterministic=False)
def noisy_exact(task: SatTask, params: dict[str, Any]) -> Prediction:
    """Decision flips w.p. eps = (1 - (1-p)^L)/2; L = m (READ) or DPLL decisions + propagations (STEP)."""
    cnf = effective_cnf(task)
    variant = params.get("variant", "READ")
    p = params.get("p", 0.01 if variant == "READ" else 0.02)
    L = cnf.m if variant == "READ" else dpll_steps(cnf)
    eps = 0.5 * (1 - (1 - p) ** L)
    g = "SAT" if S.solve(cnf, task.fixed_dict()) is not None else "UNSAT"
    other = "UNSAT" if g == "SAT" else "SAT"
    return Prediction(None, {"variant": variant, "L": L, "eps": round(eps, 4)}, {g: 1 - eps, other: eps})


@member("PERCEPTION-NOISE", "nuisance", D, "a misquote of a clause that predicts where the answer goes wrong", deterministic=False)
def perception_noise(task: SatTask, params: dict[str, Any]) -> Prediction:
    """Exact on a misread instance: each clause dropped w.p. p_d (Monte Carlo, fixed seed)."""
    cnf = effective_cnf(task)
    p_d = params.get("p_d", 0.02)
    runs = params.get("runs", 200)
    rng = np.random.default_rng(params.get("seed", 0))
    sat = 0
    for _ in range(runs):
        kept = [c for c in cnf.clauses if rng.random() >= p_d]
        if not kept or S.solve(cnf.with_clauses(kept)) is not None:
            sat += 1
    return Prediction(None, {"p_d": p_d, "runs": runs}, {"SAT": sat / runs, "UNSAT": 1 - sat / runs})


@member("EXACT", "null", D, "a witness checked against every clause, or a closed refutation")
def exact(task: SatTask, params: dict[str, Any]) -> Prediction:
    cnf = effective_cnf(task)
    sol = S.solve(cnf, task.fixed_dict())
    if sol is None:
        return Prediction("UNSAT", {"set_valued": False})
    return Prediction("SAT", {"set_valued": True, "witness": sol})


@member("TT", "A3", D, "restates the rule in standard CNF form; checks use textbook semantics")
def textbook_transfer(task: SatTask, params: dict[str, Any]) -> Prediction:
    """A3: answers the textbook (un-inverted) formula with the exact inner solver."""
    sol = S.solve(task.cnf, task.fixed_dict())
    return Prediction("UNSAT" if sol is None else sol, {"inner": "EXACT"})


def unit_rounds_to_refute(cnf: CNF) -> int | None:
    _, refuted, r = unit_propagate(cnf, {}, None)
    return r if refuted else None


def log2_solutions(cnf: CNF) -> float:
    s = S.count_solutions(cnf)
    return math.log2(s) if s else float("-inf")
