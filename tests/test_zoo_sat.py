"""SAT members against their specs: C2 UC/GUC/SC (C §1.3), B1 UP-k (B1 §1.3 pseudocode), F WALK
(D/F §1.3 WalkSAT/SKC), C3 RO-GREEDY (C §1.2 distributional members) and PERCEPTION-NOISE (A/H §1.5)."""

import time

import numpy as np
import pytest

from reasoning_heuristics.heuristics import sat as SAT
from reasoning_heuristics.heuristics.answers import assignment_key
from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.montecarlo import random_orders
from reasoning_heuristics.heuristics.tasks import SatTask
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.sat.cnf import CNF


def names(n, start=10):
    return tuple(f"x{i}" for i in range(start, start + n))


# --- C2: UC / GUC / SC check the final assignment ---------------------------------------------


def uc_reference(cnf):
    """C §1.3 UC-DET: falsified clause -> UNSAT; else the first unit clause; else the first free
    variable in listing order set T; the loop ends only when no variable is free."""
    vals = {}
    listing = cnf.mention_order() + [v for v in range(1, cnf.n + 1) if v not in cnf.mention_order()]
    while True:
        open_, falsified = [], False
        for c in cnf.clauses:
            lv = [S.lit_value(l, vals) for l in c]
            if True in lv:
                continue
            free = [l for l, x in zip(c, lv) if x is None]
            if not free:
                falsified = True
            open_.append(free)
        if falsified:
            return "UNSAT"
        if len(vals) == cnf.n:
            return S.to_assignment(cnf, vals)
        units = [f for f in open_ if len(f) == 1]
        if units:
            vals[abs(units[0][0])] = units[0][0] > 0
        else:
            vals[next(v for v in listing if v not in vals)] = True


@pytest.mark.parametrize("rule", ["UC", "GUC", "SC"])
def test_unit_rules_answer_unsat_on_a_conflict_at_the_last_step(rule):
    # (x1), (¬x1): x1 = T from the first unit clause falsifies the second clause.
    task = SatTask(CNF(("x1",), ((1,), (-1,))))
    assert run("sat", rule, task).answer == "UNSAT"
    # Every variable fixed up front, one clause falsified: no step is taken at all.
    task = SatTask(CNF(("a", "b"), ((1, 2), (-1, -2))), (("a", True), ("b", True)))
    assert run("sat", rule, task).answer == "UNSAT"


def test_uc_matches_the_reference_and_unit_rules_never_return_a_violating_assignment():
    rng = np.random.default_rng(1)
    for _ in range(400):
        cnf = S.random_ksat(12, int(round(rng.choice([3.5, 4.0, 4.26, 5.0]) * 12)), 3, rng, names(12))
        task = SatTask(cnf)
        assert run("sat", "UC", task).answer == uc_reference(cnf)
        for rule in ("UC", "GUC", "SC"):
            a = run("sat", rule, task).answer
            assert a == "UNSAT" or S.satisfies(cnf, a), rule


# --- B1: UP-k follows the B1 pseudocode -----------------------------------------------------------


def up_reference(cnf, k):
    """B1 §1.3, literally: facts are round 0; round r reads only round r-1 state; a clause with no
    open literal, or two opposite derivations in one round, is a CONFLICT found in that round."""
    A = {}
    for C in cnf.clauses:
        if len(C) == 1:
            A.setdefault(abs(C[0]), C[0] > 0)
    r = 0
    while k is None or r < k:
        r += 1
        new = {}
        for C in cnf.clauses:
            if any(S.lit_value(l, A) is True for l in C):
                continue
            open_ = [l for l in C if abs(l) not in A]
            if not open_:
                return "UNSAT"
            if len(open_) == 1:
                new.setdefault(abs(open_[0]), set()).add(open_[0] > 0)
        if not new:
            break
        if any(len(s) == 2 for s in new.values()):
            return "UNSAT"
        for v, s in new.items():
            A[v] = s.pop()
    return "SAT"


def up(cnf, k):
    return run("sat", "UP-k", SatTask(cnf), {"k": k}).answer


def test_up_k_finds_a_falsified_clause_only_in_a_round():
    # a; ¬a ∨ b; ¬a ∨ c; ¬b ∨ ¬c: round 1 derives b and c, round 2 reads the falsified clause.
    cnf = CNF(("a", "b", "c"), ((1,), (-1, 2), (-1, 3), (-2, -3)))
    assert [up(cnf, k) for k in (0, 1, 2)] == ["SAT", "SAT", "UNSAT"]
    # a; b; ¬a ∨ ¬b: no round has run at k = 0.
    cnf = CNF(("a", "b"), ((1,), (2,), (-1, -2)))
    assert [up(cnf, k) for k in (0, 1)] == ["SAT", "UNSAT"]
    # Round 1 already propagates: a; ¬a ∨ b; ¬a ∨ ¬b clash inside round 1.
    cnf = CNF(("a", "b"), ((1,), (-1, 2), (-1, -2)))
    assert [up(cnf, k) for k in (0, 1)] == ["SAT", "UNSAT"]
    assert SAT.unit_propagate(cnf, {}, None)[1:] == (True, 1)


def test_up_k_matches_the_pseudocode_on_random_horn_like_formulas():
    rng = np.random.default_rng(7)
    for _ in range(300):
        n = 8
        clauses = [(int(v) * int(rng.choice([-1, 1])),) for v in rng.choice(np.arange(1, n + 1), 2, replace=False)]
        for _ in range(int(rng.integers(6, 14))):
            w = int(rng.choice([2, 3]))
            vs = rng.choice(np.arange(1, n + 1), w, replace=False)
            clauses.append(tuple(int(v) * int(rng.choice([-1, 1])) for v in vs))
        cnf = CNF(names(n), tuple(clauses))
        for k in (0, 1, 2, 3, None):
            assert up(cnf, k) == up_reference(cnf, k), (clauses, k)


# --- F: WALK is WalkSAT/SKC ----------------------------------------------------------------------------


def test_walk_takes_the_freebie_move_whatever_the_noise():
    # All false: C1 (x1 v x2) is falsified. break(x1) = 1 (C2), break(x2) = 0 (C3 keeps ¬x4).
    cnf = CNF(names(4, 1), ((1, 2), (-1, 3), (-2, -4)))
    vals = {1: False, 2: False, 3: False, 4: False}
    out, trace = SAT.walk_run(cnf, vals, flips=1, p=1.0, pick="FIRST", rng=np.random.default_rng(0))
    assert trace["flipped"] == ["x2"] and trace["moves"] == ["freebie"]
    assert S.satisfies(cnf, S.to_assignment(cnf, out))


def test_walk_greedy_move_minimises_break_count_not_total_unsatisfied():
    # All false. C1 = (x1 v x2) is the first falsified clause. Flipping x1 fixes C1-C3 (make 3) but
    # breaks C4, C5 (break 2); flipping x2 fixes C1 (make 1) and breaks C6 (break 1). Total unsatisfied
    # after the flip prefers x1 (3 -> 2 vs 3 -> 3); SKC flips argmin break = x2.
    cnf = CNF(names(7, 1), ((1, 2), (1, 3), (1, 4), (-1, 5), (-1, 6), (-2, 7)))
    vals = {v: False for v in range(1, 8)}
    _, trace = SAT.walk_run(cnf, vals, flips=1, p=0.0, pick="FIRST", rng=np.random.default_rng(0))
    assert trace["flipped"] == ["x2"] and trace["moves"] == ["greedy"]


def test_walk_member_rates():
    rng = np.random.default_rng(2)
    easy = S.random_ksat(12, 30, 3, rng, names(12))
    assert S.solve(easy) is not None
    pred = run("sat", "WALK", SatTask(easy), {"flips": 200, "runs": 30, "seed": 0})
    assert pred.distribution["SAT"] > 0.9 and pred.trace_features["p"] == 0.5
    unsat = CNF(("a", "b"), ((1, 2), (1, -2), (-1, 2), (-1, -2)))
    assert run("sat", "WALK", SatTask(unsat), {"flips": 50, "runs": 10}).distribution["SAT"] == 0.0


# --- C3: RO-GREEDY keeps its whole distribution ------------------------------------------------------


def test_ro_greedy_distribution_is_complete_and_smoothed():
    rng = np.random.default_rng(4)
    cnf = S.random_ksat(14, 56, 3, rng, names(14))
    task = SatTask(cnf)
    t0 = time.time()
    pred = run("sat", "RO-GREEDY", task, {"seed": 0})
    assert time.time() - t0 < 10
    d, tf = pred.distribution, pred.trace_features
    N, eps, K = tf["samples"], tf["smoothing_eps"], tf["distinct_outcomes"]
    assert N == 10_000  # C §1.2: 10^4 Monte-Carlo runs
    assert len(d) == K + 1 and "_other" in d  # every observed outcome is kept
    assert sum(d.values()) == pytest.approx(1.0, abs=1e-12)
    assert d["_other"] == pytest.approx(eps / (N + eps * (K + 1)))
    assert min(v for k, v in d.items() if k != "_other") >= (1 + eps) / (N + eps * (K + 1)) - 1e-15


def test_ro_greedy_counts_equal_greedy_on_the_same_orders():
    rng = np.random.default_rng(9)
    for mode in ("ABORT", "INFEAS"):
        cnf = S.random_ksat(10, 40, 3, rng, names(10))
        start = {3: True}
        free = [v for v in range(1, cnf.n + 1) if v not in start]
        orders = random_orders(np.random.default_rng(0), len(free), 300)
        got = SAT.ro_greedy_counts(cnf, free, orders, start, mode)
        want = {}
        for row in orders:
            values, _ = SAT.greedy_run(cnf, [free[i] for i in row], start, mode)
            key = "UNSAT" if values is None else assignment_key(S.to_assignment(cnf, values))
            want[key] = want.get(key, 0) + 1
        assert got == want


# --- nuisance: PERCEPTION-NOISE misreads signs too ----------------------------------------------------


def test_sat_perception_noise_flips_literal_signs():
    # (x1), (¬x1) is UNSAT; with no drops, only sign flips can make it satisfiable (half the runs).
    task = SatTask(CNF(("x1",), ((1,), (-1,))))
    pred = run("sat", "PERCEPTION-NOISE", task, {"p_d": 0.0, "p_f": 0.5, "runs": 400, "seed": 0})
    assert 0.4 < pred.distribution["SAT"] < 0.6
    assert pred.trace_features["p_f"] == 0.5
    assert run("sat", "PERCEPTION-NOISE", task, {"p_d": 0.0, "p_f": 0.0, "runs": 50}).distribution["SAT"] == 0.0
