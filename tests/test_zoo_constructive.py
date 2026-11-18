"""Colouring, SAT, knapsack and TSP members against the C library's computed predictions,
the two lemmas of C §1.3, and brute-force references."""

import itertools

import numpy as np
import pytest

from libparse import cnf_from_c_prompt, find, graph_from_edge_list, graph_from_neighbours
from reasoning_heuristics.heuristics.answers import colouring_key
from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.tasks import ColouringTask, KnapsackTask, SatTask, TspTask
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.knapsack.knapsack import Knapsack, solve_brute
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.tsp.tsp import TSP, solve_held_karp


def test_library_e1_col_predictions():
    rec = find("C_constructive", pair_id="E1-COL-A", cell="c1-NAT")
    g = graph_from_neighbours(rec["prompt"])
    task = ColouringTask(g, None, (), tuple(g.vertices))
    p = rec["predictions"]
    assert run("coloring", "FF", task, {"order": "LIST"}).answer == p["FF-LIST"]
    assert run("coloring", "FF", task, {"order": "LABEL"}).answer == p["FF-LABEL"]
    assert run("coloring", "LF", task).answer == p["LF"]
    assert run("coloring", "DSATUR", task).answer == p["DSATUR"]
    assert run("coloring", "SEARCH", task, {"order": "LIST"}).answer == p["DPLL-LIST (D, k=3)"]
    assert run("coloring", "GREEDY+REPAIR", task, {"order": "LIST"}).answer == p["GREEDY+REPAIR-LIST (C->F)"]
    local = run("coloring", "LOCAL-t", task, {"t": 2, "ids": "LABEL", "default": "one"})
    want = {k: v for k, v in p["LOCAL-2-ID (E)"].items() if not k.startswith("_")}
    assert local.answer == want and local.trace_features["valid"] is False


def test_library_e2_col_base():
    rec = find("C_constructive", pair_id="E2-COL-A", cell="BASE")
    g = graph_from_neighbours(rec["prompt"])
    task = ColouringTask(g, None, (), tuple(g.vertices))
    p = rec["predictions"]
    assert run("coloring", "FF", task, {"order": "LIST"}).answer == p["FF-LIST"]
    assert run("coloring", "DSATUR", task).answer == p["DSATUR"]
    assert run("coloring", "LF", task).answer == p["LF"]


def test_library_e5_col_stuck():
    rec = find("C_constructive", pair_id="E5-COL-A", cell="STUCK/vertexA/edgeA")
    g = graph_from_edge_list(rec["prompt"])
    task = ColouringTask(g, 3, (), tuple(g.vertices))
    p = rec["predictions"]
    assert run("coloring", "FF", task, {"order": "LIST", "mode": "ABORT"}).answer == "IMPOSSIBLE"
    infeas = run("coloring", "FF", task, {"order": "LIST", "mode": "INFEAS"})
    want = {k: v for k, v in p["FF-3-LIST-INFEAS (C1)"].items() if not k.startswith("_")}
    assert infeas.answer == want
    def edges(xs):
        return {frozenset(e.split("-")) for e in xs}

    assert edges(infeas.trace_features["conflicts"]) == edges(p["FF-3-LIST-INFEAS (C1)"]["_conflicts"])
    assert run("coloring", "FF", task, {"order": "EDGE", "mode": "ABORT"}).answer == p["FF-3-EDGE-MENTION-ABORT (C1 variant)"]


def test_library_e5_sat_state():
    rec = find("C_constructive", pair_id="E5-SAT-STATE-A", cell="STATE-s2: UC vs GREEDY")
    cnf = cnf_from_c_prompt(rec["prompt"])
    fixed = tuple(rec["params"]["fixed"].items())
    task = SatTask(cnf, tuple((k, v == "T") for k, v in fixed), tuple(cnf.var_names))
    p = rec["predictions"]

    def strip(d):
        return {k: v == "T" for k, v in d.items() if not k.startswith("_")}

    g = run("sat", "GREEDY", task, {"order": "MENTION", "mode": "INFEAS"})
    assert g.answer == strip(p["GREEDY-MENTION from state (C1)"])
    assert run("sat", "POLARITY", task).answer == strip(p["POLARITY (C0, ignores state)"])
    assert run("sat", "UC", task).answer == strip(p["UC-DET from state (C2)"])
    assert run("sat", "SEARCH", task, {"order": "MENTION"}).answer == strip(p["DPLL from state (D)"])


@pytest.mark.parametrize("seed", range(15))
def test_ff_output_is_grundy_and_lemma_l2(seed):
    rng = np.random.default_rng(seed)
    g = G.random_gnp([f"v{i}" for i in range(10, 24)], 0.3, rng)
    task = ColouringTask(g)
    col = run("coloring", "FF", task, {"order": "LIST"}).answer
    assert G.is_proper(g, col) and G.is_grundy(g, col)  # Lemma L1 (=>)
    # Lemma L2: an edge between two differently coloured FF vertices never changes FF.
    for u, v in itertools.combinations(g.vertices, 2):
        if not g.has_edge(u, v) and col[u] != col[v]:
            g2 = g.with_edge(u, v)
            assert run("coloring", "FF", ColouringTask(g2), {"order": "LIST"}).answer == col
            break


@pytest.mark.parametrize("seed", range(8))
def test_local_infinity_equals_ff_and_dpll_equals_ff_when_optimal(seed):
    rng = np.random.default_rng(100 + seed)
    g = G.random_gnp([f"v{i}" for i in range(10, 22)], 0.35, rng)
    task = ColouringTask(g)
    ff = run("coloring", "FF", task, {"order": "LIST"}).answer
    assert run("coloring", "LOCAL-t", task, {"t": 10**6, "ids": "LIST"}).answer == ff
    if len(set(ff.values())) == G.chromatic_number(g):
        assert run("coloring", "SEARCH", task, {"order": "LIST"}).answer == ff


@pytest.mark.parametrize("seed", range(10))
def test_sat_search_is_exact_without_budget(seed):
    rng = np.random.default_rng(seed)
    cnf = S.random_ksat(10, 43, 3, rng, tuple(f"x{i}" for i in range(10, 20)))
    task = SatTask(cnf)
    for order in ("MENTION", "INDEX", "MOMS"):
        for value in ("TRUE", "POLARITY"):
            ans = run("sat", "SEARCH", task, {"order": order, "value": value}).answer
            sat = S.solve(cnf) is not None
            assert (ans != "UNSAT") == sat
            if sat:
                assert S.satisfies(cnf, ans)
    capped = run("sat", "SEARCH", task, {"b": 0, "default": "UNSAT"})
    assert capped.answer == "UNSAT" or capped.trace_features["exhausted"] is False


def test_greedy_definition_on_toy():
    # (x1 v x2) (¬x1 v x2) (¬x2 v x3): mention order x1, x2, x3.
    cnf = S.CNF(("x1", "x2", "x3"), ((1, 2), (-1, 2), (-2, 3)))
    ans = run("sat", "GREEDY", SatTask(cnf), {"order": "MENTION"}).answer
    # x1: p=1 (C1), q=1 (C2) -> T; then x2: p=1 (C2 open), q=1 (C3) -> T; x3: p=1 -> T.
    assert ans == {"x1": True, "x2": True, "x3": True}
    assert run("sat", "POLARITY", SatTask(cnf)).answer == {"x1": True, "x2": True, "x3": True}
    uc = run("sat", "UC", SatTask(cnf, (("x2", False),)))
    # x2 fixed F: C1 unit x1 -> T, then C2 falsified -> UNSAT.
    assert uc.answer == "UNSAT"


def test_knapsack_members_toy():
    # Ratios: A 3.0, B 2.0, C 1.5. Capacity 50: RATIO-PREFIX takes A (w 20), B (w 20) then stops at C (w 20).
    k = Knapsack(("A", "B", "C", "D"), (60, 40, 30, 9), (20, 20, 20, 9), 50)
    t = KnapsackTask(k)
    assert run("knapsack", "RATIO-PREFIX", t).answer == ["A", "B"]
    assert run("knapsack", "RATIO-SKIP", t).answer == ["A", "B", "D"]
    assert run("knapsack", "VALUE", t).answer == ["A", "B", "D"]
    assert run("knapsack", "INPUT-FIT", t).answer == ["A", "B", "D"]
    opt, subsets = solve_brute(k)
    assert run("knapsack", "EXACT", t).answer in [sorted(s) for s in subsets]


@pytest.mark.parametrize("seed", range(5))
def test_tsp_members_valid_and_exact(seed):
    rng = np.random.default_rng(seed)
    t = TSP(tuple(f"c{i}" for i in range(8)), tuple((int(x), int(y)) for x, y in rng.integers(0, 100, size=(8, 2))))
    task = TspTask(t)
    opt, _ = solve_held_karp(t)
    for name in ("NN-FIRST", "NN-LABEL0", "NN-BEST", "INPUT-ORDER", "GREEDY-EDGE", "FARTHEST-INSERTION", "EXACT"):
        tour = run("tsp", name, task).answer
        assert sorted(tour) == sorted(t.names) and tour[0] == t.names[0]
        assert t.tour_length(tour) >= opt
    assert t.tour_length(run("tsp", "EXACT", task).answer) == opt
    assert t.tour_length(run("tsp", "NN-BEST", task).answer) <= t.tour_length(run("tsp", "NN-FIRST", task).answer)
