"""Counterfactual tooling: SAT edits keep the task's rule marks; copy checks fail loudly."""

from types import SimpleNamespace

import pytest

from reasoning_heuristics.counterfactual import edits as E
from reasoning_heuristics.counterfactual.reorder import assert_isomorphic_copy
from reasoning_heuristics.heuristics.sat import effective_cnf
from reasoning_heuristics.heuristics.tasks import SatTask
from reasoning_heuristics.problems.coloring.graph import Graph
from reasoning_heuristics.problems.sat.cnf import CNF


def test_sat_edits_keep_inverted_clause_marks():
    cnf = CNF(("x1", "x2", "x3"), ((1, 2), (-1, 3), (2, -3), (1, -2)))
    task = SatTask(cnf, inverted_clauses=(1, 3))
    marked = sorted(cnf.clauses[i] for i in task.inverted_clauses)
    kinds = ("flip_sign", "replace_var", "delete_clause", "swap_clauses")
    seen = set()
    for edit, t in E.sat_edits(task, kinds):
        seen.add(edit.kind)
        if edit.kind in ("flip_sign", "replace_var"):
            assert t.inverted_clauses == (1, 3), edit.text
        elif edit.kind == "delete_clause":
            (i,) = edit.args
            assert t.inverted_clauses == tuple(j - (j > i) for j in (1, 3) if j != i), edit.text
        else:
            assert sorted(t.cnf.clauses[j] for j in t.inverted_clauses) == marked, edit.text
            assert t.inverted_clauses == tuple(sorted(t.inverted_clauses))
        # the edited task still reads its marked clauses with the inverted rule
        eff = effective_cnf(t).clauses
        assert all(eff[j] == tuple(-l for l in t.cnf.clauses[j]) for j in t.inverted_clauses), edit.text
    assert seen == set(kinds)


def test_assert_isomorphic_copy_checks_the_mapping_and_the_edge_count():
    a = Graph(("v1", "v2", "v3", "v4"), (("v1", "v2"), ("v1", "v3")))
    assert_isomorphic_copy(a, Graph(("v4", "v3", "v2", "v1"), (("v2", "v1"), ("v3", "v1"))))
    swap = {"v1": "v4", "v2": "v2", "v3": "v3", "v4": "v1"}
    assert_isomorphic_copy(a, Graph(a.vertices, (("v4", "v2"), ("v4", "v3"))), swap)
    collapse = {"v1": "v1", "v2": "v2", "v3": "v2", "v4": "v4"}  # v2 and v3 both go to v2
    with pytest.raises(AssertionError, match="bijection"):
        assert_isomorphic_copy(a, Graph(a.vertices, (("v1", "v2"),)), collapse)
    with pytest.raises(AssertionError, match="edge sets"):
        assert_isomorphic_copy(a, Graph(a.vertices, (("v1", "v2"), ("v2", "v3"))))
    # Same edge *set*, different edge count (a graph-like object listing one edge twice).
    doubled = SimpleNamespace(vertices=a.vertices, edges=(("v1", "v2"), ("v1", "v3"), ("v3", "v1")))
    with pytest.raises(AssertionError, match="edge counts"):
        assert_isomorphic_copy(a, doubled)
