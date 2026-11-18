"""Python references for the sequential members (D, F, C2) on CNF, with step budgets.

These are the heuristics whose *per-step* program a thinking model would iterate.
Each returns (answer, steps_used).  RASP-L lengths for their steps are estimates
(see T2_rasp_learnability.md, section 3.4); only their accuracy is computed here.
"""

from __future__ import annotations

import random

from instances import _unit_propagate


def dpll_b(clauses, n, b, default=1):
    """DPLL with unit propagation, at most b decisions; then the default answer."""
    budget = [b]

    def rec(assign):
        assign, conflict = _unit_propagate(clauses, assign)
        if conflict:
            return 0
        free = [v for v in range(1, n + 1) if v not in assign]
        if not free:
            return 1
        if budget[0] <= 0:
            raise TimeoutError
        budget[0] -= 1
        v = free[0]
        for val in (True, False):
            if rec({**assign, v: val}):
                return 1
        return 0

    try:
        return rec({}), b - budget[0]
    except TimeoutError:
        return default, b


def walk_k(clauses, n, k, p=0.5, rng=random):
    """WalkSAT, k flips from a random start; never certifies UNSAT (answers 0 at budget)."""
    a = {v: rng.random() < 0.5 for v in range(1, n + 1)}
    for step in range(k + 1):
        unsat = [c for c in clauses if not any(a[abs(l)] == (l > 0) for l in c)]
        if not unsat:
            return 1, step
        if step == k:
            break
        c = rng.choice(unsat)
        if rng.random() < p:
            v = abs(rng.choice(c))
        else:
            def breaks(v):
                a[v] = not a[v]
                b = sum(1 for cc in clauses if not any(a[abs(l)] == (l > 0) for l in cc))
                a[v] = not a[v]
                return b
            v = min((abs(l) for l in c), key=breaks)
        a[v] = not a[v]
    return 0, k


def unit_clause(clauses, n, rng=random):
    """UC: satisfy a unit clause if one exists, else set a random free variable at random;
    never backtrack.  SAT iff it ends without conflict (false UNSAT otherwise)."""
    assign = {}
    for step in range(n):
        assign, conflict = _unit_propagate(clauses, assign)
        if conflict:
            return 0, step
        free = [v for v in range(1, n + 1) if v not in assign]
        if not free:
            return 1, step
        v = rng.choice(free)
        assign[v] = rng.random() < 0.5
    _, conflict = _unit_propagate(clauses, assign)
    return int(not conflict), n
