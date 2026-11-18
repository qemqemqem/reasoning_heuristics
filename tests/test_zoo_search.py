"""SEARCH(b, order, value, default) against D/F §1.2-1.3: DPLL-b for SAT and FC-BT for colouring.

The budget b counts nodes = decisions + flipped re-assignments (D/F §1.2), and the loop returns
SAT as soon as every clause is satisfied (D/F §1.3). Colouring DPLL-b is backtracking with
forward checking: a singleton domain assigns its vertex for free (the analogue of UP), an
empty domain is a conflict, and every colour tried at a vertex is a node.

The reference implementations below are written independently of `heuristics/search.py`,
straight from the doc's pseudocode.
"""

import itertools

import numpy as np
import pytest

from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.search import search_sat
from reasoning_heuristics.heuristics.tasks import ColouringTask, SatTask
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.coloring.graph import Graph
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.sat.cnf import CNF

# --- references ---------------------------------------------------------------------------------


def _lv(l, A):
    v = A.get(abs(l))
    return None if v is None else (v if l > 0 else not v)


def _up(cnf, A):
    """D/F §1.2 UP to fixpoint: (A, conflict?)."""
    A = dict(A)
    while True:
        if any(all(_lv(l, A) is False for l in c) for c in cnf.clauses):
            return A, True
        for c in cnf.clauses:
            vals = [_lv(l, A) for l in c]
            if True in vals:
                continue
            free = [l for l, x in zip(c, vals) if x is None]
            if len(free) == 1:
                A[abs(free[0])] = free[0] > 0
                break
        else:
            return A, False


def dpll_b_reference(cnf, b):
    """D/F §1.3 DPLL-b(MENTION, TRUE, UNSAT, CHR) with b counting nodes; 'SAT' / 'UNSAT' / 'Δ'."""
    mention = cnf.mention_order()
    A, conflict = _up(cnf, {})
    trail, nodes = [], 0  # entries (var, val, flipped, A before the decision)
    while True:
        if not conflict and all(any(_lv(l, A) is True for l in c) for c in cnf.clauses):
            return "SAT", nodes
        if b is not None and nodes >= b:
            return "Δ", nodes
        if conflict:
            while trail and trail[-1][2]:
                trail.pop()
            if not trail:
                return "UNSAT", nodes
            var, val, _, before = trail.pop()
            trail.append((var, not val, True, before))
            A, conflict = _up(cnf, {**before, var: not val})
        else:
            v = next(v for v in mention if v not in A)
            trail.append((v, True, False, dict(A)))
            A, conflict = _up(cnf, {**A, v: True})
        nodes += 1


class _Exhausted(Exception):
    pass


def fc_bt_reference(g, k, b):
    """D/F §1.3 colouring DPLL-b: forward checking, listing order, lowest colour first, every colour
    tried is a node. For graphs without isolated vertices ('every edge satisfied' = 'all coloured')."""
    nodes = [0]

    def propagate(col, dom):
        col, dom = dict(col), {v: set(d) for v, d in dom.items()}
        changed = True
        while changed:
            changed = False
            for v in g.vertices:
                if v in col:
                    continue
                if not dom[v]:
                    return None, None
                if len(dom[v]) == 1:
                    c = next(iter(dom[v]))
                    col[v] = c
                    for u in g.adj[v]:
                        if u not in col:
                            dom[u].discard(c)
                    changed = True
        return col, dom

    def rec(col, dom):
        free = [v for v in g.vertices if v not in col]
        if not free:
            return col
        v = free[0]
        for c in sorted(dom[v]):
            if b is not None and nodes[0] >= b:
                raise _Exhausted
            nodes[0] += 1
            col2 = dict(col)
            col2[v] = c
            dom2 = {x: set(d) for x, d in dom.items()}
            for u in g.adj[v]:
                if u not in col2:
                    dom2[u].discard(c)
            col2, dom2 = propagate(col2, dom2)
            if col2 is not None:
                r = rec(col2, dom2)
                if r is not None:
                    return r
        return None

    col0, dom0 = propagate({}, {v: set(range(1, k + 1)) for v in g.vertices})
    try:
        r = rec(col0, dom0) if col0 is not None else None
        return ("POSSIBLE" if r else "IMPOSSIBLE"), nodes[0]
    except _Exhausted:
        return "Δ", nodes[0]


def _min_b(answer_at, limit=400):
    for b in range(limit):
        if answer_at(b) not in ("UNSAT", "IMPOSSIBLE", "Δ"):
            return b
    raise AssertionError("no budget up to the limit succeeds")


def sat_answer(task, b, **params):
    a = run("sat", "SEARCH", task, {"b": b, "order": "MENTION", "value": "TRUE", "default": "UNSAT", **params}).answer
    return a if isinstance(a, str) else "SAT"


def col_answer(task, b, **params):
    a = run("coloring", "SEARCH", task, {"b": b, "order": "LIST", "default": "IMPOSSIBLE", **params}).answer
    return a if isinstance(a, str) else "POSSIBLE"


# --- SAT ------------------------------------------------------------------------------------------


@pytest.mark.parametrize("b", [1, 2])
def test_sat_search_stops_when_every_clause_is_satisfied(b):
    # D/F §1.3: "if A satisfies every clause: return SAT". One decision (x1 = T) satisfies (x1 v x2 v x3).
    task = SatTask(CNF(("x1", "x2", "x3"), ((1, 2, 3),)))
    pred = run("sat", "SEARCH", task, {"b": b, "order": "MENTION", "value": "TRUE", "default": "UNSAT"})
    assert pred.answer == {"x1": True, "x2": True, "x3": True}
    assert pred.trace_features["nodes"] == 1


def test_sat_search_budget_counts_flips():
    # x1 = T propagates x2 = T and falsifies (¬x1 v ¬x2); the flip x1 = F is the second node,
    # and (x2 v x3) needs a third. Nodes = decisions + flipped re-assignments (D/F §1.2).
    cnf = CNF(("x1", "x2", "x3"), ((-1, 2), (-1, -2), (2, 3)))
    task = SatTask(cnf)
    assert sat_answer(task, 2) == "UNSAT"
    pred = run("sat", "SEARCH", task, {"b": 3, "order": "MENTION", "value": "TRUE", "default": "UNSAT"})
    assert pred.answer == {"x1": False, "x2": True, "x3": True}
    t = pred.trace_features
    assert (t["nodes"], t["decisions"], t["flips"]) == (3, 2, 1)
    assert dpll_b_reference(cnf, None) == ("SAT", 3)


@pytest.mark.parametrize("seed", range(12))
def test_sat_search_matches_the_reference_on_random_3sat(seed):
    rng = np.random.default_rng(seed)
    cnf = S.random_ksat(12, int(rng.integers(40, 60)), 3, rng, tuple(f"x{i}" for i in rng.choice(np.arange(10, 100), 12, replace=False)))
    task = SatTask(cnf)
    ref_answer, ref_nodes = dpll_b_reference(cnf, None)
    full = run("sat", "SEARCH", task, {"order": "MENTION", "value": "TRUE"})
    assert (full.answer == "UNSAT") == (ref_answer == "UNSAT") == (S.solve(cnf) is None)
    assert full.trace_features["nodes"] == ref_nodes
    for b in sorted({0, 1, ref_nodes // 2, max(ref_nodes - 1, 0), ref_nodes, ref_nodes + 1}):
        want = dpll_b_reference(cnf, b)[0]
        assert sat_answer(task, b) == ("UNSAT" if want == "Δ" else want), b


@pytest.mark.parametrize("order", ["MENTION", "INDEX", "MOMS"])
def test_unused_declared_variables_do_not_change_the_minimum_budget(order):
    # A/H E2 level U: declared variables that no clause mentions. D's predicted U effect is 0.
    rng = np.random.default_rng(3)
    core = S.random_ksat(10, 38, 3, rng, tuple(f"x{i}" for i in (12, 17, 23, 31, 38, 44, 52, 67, 71, 85)))
    assert S.solve(core) is not None
    names = core.var_names + ("x10", "x20", "x40", "x60", "x90")  # unused, interleaved in label order
    padded = CNF(names, core.clauses)
    base_b = _min_b(lambda b: sat_answer(SatTask(core), b, order=order))
    pad_b = _min_b(lambda b: sat_answer(SatTask(padded, declared=names), b, order=order))
    assert base_b == pad_b
    a = run("sat", "SEARCH", SatTask(padded, declared=names), {"b": pad_b, "order": order, "value": "TRUE"}).answer
    assert S.satisfies(padded, a) and all(a[x] is True for x in names[10:])  # filled by V = TRUE


def test_sat_fill_default_completes_by_the_value_rule():
    cnf = CNF(("x1", "x2", "x3", "x4"), ((1, 2), (3, 4), (-1, -3)))
    pred = run("sat", "SEARCH", SatTask(cnf), {"b": 1, "order": "MENTION", "value": "FALSE", "default": "SAT-FILL"})
    # One decision x1 = F (V = FALSE) propagates x2 = T; the budget then runs out with x3, x4 open,
    # and FILL completes A* by V.
    assert pred.trace_features["exhausted"] is True
    assert pred.answer == {"x1": False, "x2": True, "x3": False, "x4": False}


def test_moms_ties_go_to_occ_then_mention():
    # Shortest open clauses (width 2) give x1..x4 one occurrence each: a MOMS tie. D/F §1.2: ties go
    # to OCC (occurrences in clauses not yet satisfied), which favours x4 (three occurrences).
    cnf = CNF(("x1", "x2", "x3", "x4", "x5", "x6"), ((1, 2), (3, 4), (4, 5, 6), (-4, 5, -6)))
    _, trace = search_sat(cnf, {}, {"order": "MOMS", "value": "TRUE"})
    assert trace["decision_order"][0] == "x4"
    # With no OCC tie either, MENTION decides: x1 and x2 tie on both counts.
    cnf2 = CNF(("x1", "x2"), ((1, 2), (-1, -2)))
    _, trace2 = search_sat(cnf2, {}, {"order": "MOMS", "value": "TRUE"})
    assert trace2["decision_order"][0] == "x1"


def test_search_without_budget_is_still_exact_from_a_state():
    rng = np.random.default_rng(11)
    for _ in range(10):
        cnf = S.random_ksat(10, 42, 3, rng, tuple(f"x{i}" for i in range(10, 20)))
        fixed = (("x10", True), ("x13", False))
        sol = S.solve(cnf, dict(fixed))
        for order in ("MENTION", "INDEX", "MOMS"):
            for value in ("TRUE", "FALSE", "POLARITY"):
                a = run("sat", "SEARCH", SatTask(cnf, fixed), {"order": order, "value": value}).answer
                assert (a == "UNSAT") == (sol is None)
                if sol is not None:
                    assert S.satisfies(cnf, a) and all(a[x] == v for x, v in fixed)


# --- colouring ------------------------------------------------------------------------------------


def path(n, start=10):
    vs = tuple(f"v{i}" for i in range(start, start + n))
    return Graph(vs, tuple(zip(vs, vs[1:])))


def complete_tripartite(order):
    parts = {"a": ("v11", "v12", "v13"), "b": ("v21", "v22", "v23"), "c": ("v31", "v32", "v33")}
    edges = [(u, w) for p, q in itertools.combinations("abc", 2) for u in parts[p] for w in parts[q]]
    return Graph(tuple(order), tuple(edges))


def test_colouring_search_forward_checking_makes_propagation_free():
    # k = 2 on a path: the first decision forces every other vertex. n = 25 > b = 1.
    g = path(25)
    pred = run("coloring", "SEARCH", ColouringTask(g, 2), {"b": 1, "order": "LIST", "default": "IMPOSSIBLE"})
    assert isinstance(pred.answer, dict) and G.is_proper(g, pred.answer)
    assert pred.trace_features["nodes"] == 1
    # K3,3,3 listed one vertex per part in turn: two decisions, the rest is forced.
    g = complete_tripartite(["v11", "v21", "v31", "v12", "v22", "v32", "v13", "v23", "v33"])
    pred = run("coloring", "SEARCH", ColouringTask(g, 3), {"b": 2, "order": "LIST", "default": "IMPOSSIBLE"})
    assert isinstance(pred.answer, dict) and G.is_proper(g, pred.answer)
    assert pred.trace_features["nodes"] == 2


def test_colouring_search_path_k3_needs_one_node_per_vertex():
    # The review's example: a 25-vertex path at k = 3 has a real choice at every vertex, so
    # even spec FC-BT needs 25 nodes, and b = 20 runs out (Δ = IMPOSSIBLE).
    g = path(25)
    assert fc_bt_reference(g, 3, None) == ("POSSIBLE", 25)
    assert col_answer(ColouringTask(g, 3), 20) == "IMPOSSIBLE"
    assert col_answer(ColouringTask(g, 3), 25) == "POSSIBLE"


@pytest.mark.parametrize("seed", range(12))
def test_colouring_search_matches_the_fc_bt_reference(seed):
    rng = np.random.default_rng(1000 + seed)
    while True:
        g = G.random_gnp([f"v{i}" for i in rng.choice(np.arange(10, 100), 12, replace=False)], 0.35, rng)
        if all(g.degree(v) for v in g.vertices):
            break
    for k in (3, 4):
        task = ColouringTask(g, k)
        ref, ref_nodes = fc_bt_reference(g, k, None)
        full = run("coloring", "SEARCH", task, {"order": "LIST"})
        assert (full.answer == "IMPOSSIBLE") == (ref == "IMPOSSIBLE") == (G.k_colour(g, k) is None)
        assert full.trace_features["nodes"] == ref_nodes
        for b in sorted({0, 1, ref_nodes // 2, max(ref_nodes - 1, 0), ref_nodes}):
            want = fc_bt_reference(g, k, b)[0]
            assert col_answer(task, b) == ("IMPOSSIBLE" if want == "Δ" else want), (k, b)


def test_isolated_vertices_do_not_change_the_minimum_budget():
    # A/H E2 level U for colouring: isolated people. Interleave them in the listing.
    g = complete_tripartite(["v11", "v21", "v31", "v12", "v22", "v32", "v13", "v23", "v33"])
    loners = ("v41", "v42", "v43", "v44")
    order = ["v11", "v41", "v21", "v42", "v31", "v12", "v43", "v22", "v32", "v13", "v44", "v23", "v33"]
    padded = Graph(tuple(order), g.edges)
    base_b = _min_b(lambda b: col_answer(ColouringTask(g, 3), b))
    pad_b = _min_b(lambda b: col_answer(ColouringTask(padded, 3), b))
    assert base_b == pad_b == 2
    col = run("coloring", "SEARCH", ColouringTask(padded, 3), {"b": 2, "order": "LIST"}).answer
    assert G.is_proper(padded, col) and all(col[v] == 1 for v in loners)  # filled with the smallest colour


def test_colouring_search_dsatur_order_and_fixed_vertices():
    rng = np.random.default_rng(5)
    for _ in range(8):
        g = G.random_gnp([f"v{i}" for i in range(10, 24)], 0.3, rng)
        chi = G.chromatic_number(g)
        for order in ("LIST", "LABEL", "DEGREE", "DSATUR"):
            col = run("coloring", "SEARCH", ColouringTask(g), {"order": order}).answer
            assert G.is_proper(g, col) and len(set(col.values())) == chi
        v = g.vertices[0]
        fixed = ((v, 2),)
        col = run("coloring", "SEARCH", ColouringTask(g, chi, fixed), {"order": "DSATUR"}).answer
        sol = G.k_colour(g, chi, dict(fixed))
        assert (col == "IMPOSSIBLE") == (sol is None)
        if sol is not None:
            assert G.is_proper(g, col) and col[v] == 2


def test_colouring_search_without_budget_agrees_with_first_fit_where_it_succeeds():
    # C §1.4: with b = None and the same order, DPLL-σ coincides with FF-σ wherever FF-k-σ succeeds.
    rng = np.random.default_rng(21)
    hits = 0
    for _ in range(30):
        g = G.random_gnp([f"v{i}" for i in range(10, 26)], 0.25, rng)
        ff = run("coloring", "FF", ColouringTask(g, 3), {"order": "LIST", "mode": "ABORT"}).answer
        if ff == "IMPOSSIBLE":
            continue
        hits += 1
        assert run("coloring", "SEARCH", ColouringTask(g, 3), {"order": "LIST"}).answer == ff
    assert hits >= 5
