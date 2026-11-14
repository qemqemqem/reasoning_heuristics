"""Order and isomorphic-copy machinery (C §1.2, P1 "order-only counterfactuals").

A copy changes only presentation: the listing order, the labels (a permutation of the
same label multiset), or the requested answer order. Ground truth and every
order-invariant member are constant by construction; `assert_isomorphic_copy` checks it.
"""

from __future__ import annotations

import numpy as np

from reasoning_heuristics.problems.coloring.graph import Graph
from reasoning_heuristics.problems.sat.cnf import CNF


def permutation(items: list, rng: np.random.Generator) -> list:
    return [items[i] for i in rng.permutation(len(items))]


def label_permutation(labels: list[str], rng: np.random.Generator) -> dict[str, str]:
    """A random bijection of a label set onto itself (same multiset, new assignment)."""
    return dict(zip(labels, permutation(labels, rng)))


def relabel_graph(g: Graph, mapping: dict[str, str]) -> Graph:
    assert sorted(mapping) == sorted(mapping.values()) == sorted(g.vertices)
    return g.renamed(mapping)


def relist_graph(g: Graph, order: list[str]) -> Graph:
    return g.relisted(order)


def ascending_labels_along_listing(g: Graph, labels_sorted: list[str]) -> tuple[Graph, dict[str, str]]:
    """Rename so that labels ascend along π_L (the natural format, c1)."""
    mapping = dict(zip(g.vertices, labels_sorted))
    return g.renamed(mapping), mapping


def relabel_cnf(cnf: CNF, mapping: dict[str, str]) -> CNF:
    assert sorted(mapping) == sorted(mapping.values()) == sorted(cnf.var_names)
    return cnf.renamed(mapping)


def reorder_clauses(cnf: CNF, order: list[int], literal_orders: list[list[int]] | None = None) -> CNF:
    """Re-list clauses (and optionally literals within clauses); the formula is unchanged."""
    clauses = []
    for j, i in enumerate(order):
        c = cnf.clauses[i]
        if literal_orders is not None:
            c = tuple(c[x] for x in literal_orders[j])
        clauses.append(c)
    return cnf.with_clauses(clauses)


def assert_isomorphic_copy(a: Graph, b: Graph, mapping: dict[str, str] | None = None) -> None:
    """Fail loudly unless b is a copy of a: same vertex/label multiset, same edges through mapping."""
    if sorted(a.vertices) != sorted(b.vertices):
        raise AssertionError("label multisets differ")
    mapping = mapping or {v: v for v in a.vertices}
    ea = {frozenset((mapping[u], mapping[v])) for u, v in a.edges}
    eb = {frozenset(e) for e in b.edges}
    if ea != eb:
        raise AssertionError("edge sets differ under the mapping")


def assert_same_formula(a: CNF, b: CNF, mapping: dict[str, str] | None = None) -> None:
    mapping = mapping or {v: v for v in a.var_names}

    def key(cnf, ren):
        return sorted(sorted((ren(cnf.name(l)), l > 0) for l in c) for c in cnf.clauses)

    if key(a, mapping.__getitem__) != key(b, lambda x: x):
        raise AssertionError("formulas differ under the mapping")
