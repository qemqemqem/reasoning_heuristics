"""Ground truth, computed twice by unrelated code paths.

`truth(task)` is what generators store (DSATUR backtracking, python-sat, truth tables,
DP, Held-Karp). `independent_truth(task)` is what validators recompute it with (SAT
encodings, a plain DPLL, enumeration, branch and bound). The standard keys are:

- colouring: {"chromatic_number"} (fewest) or {"k", "colourable"};
- SAT: {"satisfiable"};
- entailment: {"answer"} (+ {"follows"} for yes/no);
- knapsack: {"optimum"}; TSP: {"optimal_length"}.
"""

from __future__ import annotations

import itertools
from typing import Any

from pysat.solvers import Minisat22

from reasoning_heuristics.heuristics.coloring import effective_graph
from reasoning_heuristics.heuristics.entailment import answer_from_premises, effective_premises, mc_letter
from reasoning_heuristics.heuristics.sat import effective_cnf
from reasoning_heuristics.heuristics.tasks import ColouringTask, EntailmentTask, KnapsackTask, SatTask, TspTask
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.entailment import formula as F
from reasoning_heuristics.problems.knapsack.knapsack import solve_brute, solve_covering_dp, solve_dp
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.tsp.tsp import solve_bnb, solve_held_karp


def truth(task: Any) -> dict[str, Any]:
    if isinstance(task, ColouringTask):
        g = effective_graph(task)
        if task.k is None:
            return {"chromatic_number": G.chromatic_number(g)}
        return {"k": task.k, "colourable": G.k_colour(g, task.k, task.fixed_dict()) is not None}
    if isinstance(task, SatTask):
        return {"satisfiable": S.solve(effective_cnf(task), task.fixed_dict()) is not None}
    if isinstance(task, EntailmentTask):
        ans = answer_from_premises(task, effective_premises(task))
        out = {"answer": ans}
        if task.fmt == "YN":
            out["follows"] = ans == "YES"
        return out
    if isinstance(task, KnapsackTask):
        opt = solve_covering_dp(task.knapsack)[0] if task.covering else solve_dp(task.knapsack)[0]
        return {"optimum": opt}
    if isinstance(task, TspTask):
        return {"optimal_length": solve_held_karp(task.tsp)[0]}
    raise TypeError(type(task))


def _k_colourable_sat_fixed(g: G.Graph, k: int, fixed: dict[str, int]) -> bool:
    idx = {v: i for i, v in enumerate(g.vertices)}

    def var(v, c):
        return idx[v] * k + c + 1

    clauses = [[var(v, c) for c in range(k)] for v in g.vertices]
    for v in g.vertices:
        for a, b in itertools.combinations(range(k), 2):
            clauses.append([-var(v, a), -var(v, b)])
    for u, v in g.edges:
        for c in range(k):
            clauses.append([-var(u, c), -var(v, c)])
    for v, c in fixed.items():
        if not 1 <= c <= k:
            return False
        clauses.append([var(v, c - 1)])
    with Minisat22(bootstrap_with=clauses) as s:
        return bool(s.solve())


def _mc_answer_sat(task: EntailmentTask, premises: list) -> str:
    ok = [i for i, o in enumerate(task.options) if F.entails_sat(premises, o)]
    if not ok:
        return mc_letter(task, None)
    maximal = [i for i in ok if all(F.entails_sat([task.options[i]], task.options[j]) for j in ok)]
    pool = maximal or ok
    canon = sorted(range(len(task.options)), key=lambda i: repr(F.canonical(task.options[i])))
    return mc_letter(task, min(pool, key=canon.index))


def independent_truth(task: Any) -> dict[str, Any]:
    if isinstance(task, ColouringTask):
        g = effective_graph(task)
        if task.k is None:
            return {"chromatic_number": G.chromatic_number_sat(g)}
        return {"k": task.k, "colourable": _k_colourable_sat_fixed(g, task.k, task.fixed_dict())}
    if isinstance(task, SatTask):
        return {"satisfiable": S.dpll_solve(effective_cnf(task), task.fixed_dict()) is not None}
    if isinstance(task, EntailmentTask):
        prem = effective_premises(task)
        atoms = F.atoms_of(list(prem) + ([task.probe] if task.probe is not None else []) + list(task.options))
        clauses = [c for p in prem for c in F.clauses_of(p)]
        idx = {a: i + 1 for i, a in enumerate(atoms)}
        with Minisat22(bootstrap_with=[[idx[a] if s else -idx[a] for a, s in c] for c in clauses]) as s:
            consistent = s.solve()
        if not consistent:
            return {"answer": "X", **({"follows": False} if task.fmt == "YN" else {})}
        if task.fmt == "YN":
            f = F.entails_sat(prem, task.probe)
            return {"answer": "YES" if f else "NO", "follows": f}
        if task.fmt == "MC":
            return {"answer": _mc_answer_sat(task, prem)}
        if task.fmt == "OPEN":
            lits = sorted(F.render_lit(a, pol) for a in F.atoms_of(task.premises) for pol in (True, False)
                          if F.entails_sat(prem, F.lit(a, pol)))
            return {"answer": lits or "NOTHING"}
        raise ValueError(task.fmt)
    if isinstance(task, KnapsackTask):
        return {"optimum": solve_brute(task.knapsack, covering=task.covering)[0]}
    if isinstance(task, TspTask):
        return {"optimal_length": solve_bnb(task.tsp)}
    raise TypeError(type(task))
