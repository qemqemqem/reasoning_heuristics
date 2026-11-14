"""Graphs for colouring: presentation-aware instances, exact solvers, partition enumeration.

A `Graph` keeps two presentation orders as part of the instance:

- `vertices` is the listing order π_L (the vertex header line);
- `edges` is the edge-list order π_E, each edge in the orientation it is written.

Label order λ is derived from the vertex names (numeric part for v37-style labels,
alphabetical otherwise). Content keys ignore both presentation orders.

Generator path for ground truth: `chromatic_number` / `k_colour` (DSATUR-ordered
backtracking). Validator path: `k_colourable_sat` (python-sat encoding).
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass
from functools import cached_property

import networkx as nx
import numpy as np
from pysat.solvers import Minisat22

Colouring = dict[str, int]


def label_key(name: str) -> tuple:
    m = re.fullmatch(r"([A-Za-z]*)(\d+)", name)
    return (0, m.group(1), int(m.group(2))) if m else (1, name, 0)


@dataclass(frozen=True)
class Graph:
    vertices: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        vs = set(self.vertices)
        if len(vs) != len(self.vertices):
            raise ValueError("duplicate vertex")
        seen = set()
        for u, v in self.edges:
            if u == v or u not in vs or v not in vs:
                raise ValueError(f"bad edge {u}-{v}")
            key = frozenset((u, v))
            if key in seen:
                raise ValueError(f"duplicate edge {u}-{v}")
            seen.add(key)

    @property
    def n(self) -> int:
        return len(self.vertices)

    @property
    def m(self) -> int:
        return len(self.edges)

    @cached_property
    def position(self) -> dict[str, int]:
        return {v: i for i, v in enumerate(self.vertices)}

    @cached_property
    def adj(self) -> dict[str, frozenset[str]]:
        out: dict[str, set[str]] = {v: set() for v in self.vertices}
        for u, v in self.edges:
            out[u].add(v)
            out[v].add(u)
        return {v: frozenset(s) for v, s in out.items()}

    def neighbours_listed(self, v: str) -> list[str]:
        """Neighbours of v in listing order."""
        return sorted(self.adj[v], key=self.position.__getitem__)

    def degree(self, v: str) -> int:
        return len(self.adj[v])

    def has_edge(self, u: str, v: str) -> bool:
        return v in self.adj[u]

    def label_order(self) -> list[str]:
        return sorted(self.vertices, key=label_key)

    def edge_mention_order(self) -> list[str]:
        """Vertices by first mention in the edge list (isolated vertices last, in listing order)."""
        seen: dict[str, None] = {}
        for u, v in self.edges:
            seen.setdefault(u, None)
            seen.setdefault(v, None)
        rest = [v for v in self.vertices if v not in seen]
        return list(seen) + rest

    # --- derived instances -----------------------------------------------------------

    def relisted(self, order: list[str]) -> "Graph":
        assert sorted(order) == sorted(self.vertices)
        return Graph(tuple(order), self.edges)

    def renamed(self, mapping: dict[str, str]) -> "Graph":
        return Graph(tuple(mapping[v] for v in self.vertices), tuple((mapping[u], mapping[v]) for u, v in self.edges))

    def with_edge(self, u: str, v: str) -> "Graph":
        assert not self.has_edge(u, v)
        return Graph(self.vertices, self.edges + ((u, v),))

    def without_edge(self, u: str, v: str) -> "Graph":
        key = frozenset((u, v))
        return Graph(self.vertices, tuple(e for e in self.edges if frozenset(e) != key))

    def with_edges_in_order(self, edges: list[tuple[str, str]]) -> "Graph":
        assert {frozenset(e) for e in edges} == {frozenset(e) for e in self.edges}
        return Graph(self.vertices, tuple(edges))

    def to_json(self) -> dict:
        return {"kind": "graph", "vertices": list(self.vertices), "edges": [list(e) for e in self.edges]}

    @classmethod
    def from_json(cls, data: dict) -> "Graph":
        assert data["kind"] == "graph"
        return cls(tuple(data["vertices"]), tuple((u, v) for u, v in data["edges"]))

    def content_key(self) -> dict:
        return {"kind": "graph", "vertices": sorted(self.vertices), "edges": sorted(sorted(e) for e in self.edges)}

    def nx(self) -> nx.Graph:
        g = nx.Graph()
        g.add_nodes_from(self.vertices)
        g.add_edges_from(self.edges)
        return g


# --- checks ----------------------------------------------------------------------------


def conflicts(g: Graph, col: Colouring) -> list[tuple[str, str]]:
    """Edges (in edge-list order) whose ends share a colour."""
    return [(u, v) for u, v in g.edges if col.get(u) is not None and col.get(u) == col.get(v)]


def is_proper(g: Graph, col: Colouring) -> bool:
    return set(col) == set(g.vertices) and not conflicts(g, col)


def n_colours(col: Colouring) -> int:
    return len(set(col.values()))


def partition_of(col: Colouring) -> frozenset[frozenset[str]]:
    classes: dict[int, set[str]] = {}
    for v, c in col.items():
        classes.setdefault(c, set()).add(v)
    return frozenset(frozenset(s) for s in classes.values())


def partition_json(col: Colouring, order: list[str]) -> list[list[str]]:
    """Partition as lists in a stable order (classes by first member in `order`)."""
    pos = {v: i for i, v in enumerate(order)}
    classes = [sorted(c, key=pos.__getitem__) for c in partition_of(col)]
    return sorted(classes, key=lambda c: pos[c[0]])


# --- exact colouring (generator path) --------------------------------------------------


def k_colour(g: Graph, k: int, fixed: Colouring | None = None) -> Colouring | None:
    """A proper colouring with colours 1..k extending `fixed`, or None. DSATUR-ordered backtracking."""
    col: Colouring = dict(fixed or {})
    if conflicts(g, col):
        return None
    adj = g.adj

    def choose() -> str | None:
        best, best_key = None, None
        for v in g.vertices:
            if v in col:
                continue
            sat = len({col[u] for u in adj[v] if u in col})
            key = (sat, len(adj[v]))
            if best_key is None or key > best_key:
                best, best_key = v, key
        return best

    def rec() -> bool:
        v = choose()
        if v is None:
            return True
        used = {col[u] for u in adj[v] if u in col}
        max_used = max(col.values(), default=0)
        for c in range(1, k + 1):
            if c in used:
                continue
            if c > max_used + 1 and not fixed:  # symmetry: new colours in order
                break
            col[v] = c
            if rec():
                return True
            del col[v]
        return False

    return dict(col) if rec() else None


def chromatic_number(g: Graph) -> int:
    if g.m == 0:
        return 1 if g.n else 0
    k = 2
    while k_colour(g, k) is None:
        k += 1
    return k


# --- exact colouring (validator path) --------------------------------------------------


def k_colourable_sat(g: Graph, k: int) -> bool:
    """Independent check via a SAT encoding (one-hot colours, edge exclusions)."""
    idx = {v: i for i, v in enumerate(g.vertices)}

    def var(v: str, c: int) -> int:
        return idx[v] * k + c + 1

    clauses = [[var(v, c) for c in range(k)] for v in g.vertices]
    for v in g.vertices:
        for a, b in itertools.combinations(range(k), 2):
            clauses.append([-var(v, a), -var(v, b)])
    for u, v in g.edges:
        for c in range(k):
            clauses.append([-var(u, c), -var(v, c)])
    with Minisat22(bootstrap_with=clauses) as s:
        return bool(s.solve())


def chromatic_number_sat(g: Graph) -> int:
    k = 1
    while not k_colourable_sat(g, k):
        k += 1
    return k


# --- enumeration of optimal partitions and the Grundy property -------------------------


def enumerate_partitions(g: Graph, k: int, limit: int) -> list[list[int]] | None:
    """All partitions of V into at most k independent sets, as class-mask lists.

    Returns None if there are more than `limit` (the caller rejects such bases).
    Vertices are processed in degree-descending order; a vertex may open colour
    c only if colours 1..c-1 are open, so each partition is produced once.
    """
    order = sorted(g.vertices, key=lambda v: (-g.degree(v), g.position[v]))
    bit = {v: 1 << i for i, v in enumerate(g.vertices)}
    nbr = [sum(bit[u] for u in g.adj[v]) for v in order]
    vb = [bit[v] for v in order]
    out: list[list[int]] = []
    classes = [0] * k
    n = len(order)

    def rec(i: int, opened: int) -> bool:
        if i == n:
            out.append(list(classes[:opened]))
            return len(out) <= limit
        for c in range(min(opened + 1, k)):
            if classes[c] & nbr[i]:
                continue
            classes[c] |= vb[i]
            ok = rec(i + 1, max(opened, c + 1))
            classes[c] &= ~vb[i]
            if not ok:
                return False
        return True

    return out if rec(0, 0) else None


def masks_to_colouring(g: Graph, masks: list[int]) -> Colouring:
    col = {}
    for c, mask in enumerate(masks, 1):
        for i, v in enumerate(g.vertices):
            if mask >> i & 1:
                col[v] = c
    return col


def is_grundy_masks(g: Graph, masks: list[int]) -> bool:
    """Lemma L1: the partition is a first-fit output for some vertex order iff some ordering of
    its classes gives every vertex of class j a neighbour in each class 1..j-1."""
    bit = {v: i for i, v in enumerate(g.vertices)}
    nbr = {i: sum(1 << bit[u] for u in g.adj[v]) for v, i in bit.items()}
    members = [[i for i in range(g.n) if m >> i & 1] for m in masks]
    for perm in itertools.permutations(range(len(masks))):
        ok = True
        for j, cj in enumerate(perm):
            for i in members[cj]:
                if any(not (nbr[i] & masks[perm[p]]) for p in range(j)):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return True
    return False


def is_grundy(g: Graph, col: Colouring) -> bool:
    bit = {v: i for i, v in enumerate(g.vertices)}
    masks: dict[int, int] = {}
    for v, c in col.items():
        masks[c] = masks.get(c, 0) | (1 << bit[v])
    return is_grundy_masks(g, list(masks.values()))


# --- random graphs and isomorphism --------------------------------------------------------


def random_gnp(names: list[str], p: float, rng: np.random.Generator) -> Graph:
    edges = []
    for i, j in itertools.combinations(range(len(names)), 2):
        if rng.random() < p:
            edges.append((names[i], names[j]))
    return Graph(tuple(names), tuple(edges))


def random_gnm(names: list[str], m: int, rng: np.random.Generator) -> Graph:
    pairs = list(itertools.combinations(range(len(names)), 2))
    chosen = sorted(rng.choice(len(pairs), size=m, replace=False))
    return Graph(tuple(names), tuple((names[pairs[c][0]], names[pairs[c][1]]) for c in chosen))


def iso_invariant(g: Graph) -> str:
    return nx.weisfeiler_lehman_graph_hash(g.nx(), iterations=4)


def isomorphic(a: Graph, b: Graph) -> bool:
    return a.n == b.n and a.m == b.m and nx.is_isomorphic(a.nx(), b.nx())
