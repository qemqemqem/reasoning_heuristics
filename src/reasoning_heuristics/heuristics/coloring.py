"""Colouring members: C1 first-fit and static scores, C2 DSATUR, C3 random-order first-fit,
C->F greedy+repair, E LOCAL-t, C4 online first-fit, B4 phantom edges, B1 dropped edges,
A3 textbook transfer, H random, nuisance noisy-exact, and the exact solver.

Conventions (C §1.2): colours are 1..k; ties go to the earliest vertex in π_L (variant:
lowest label); dead ends run as -ABORT (answer IMPOSSIBLE at the first stuck vertex) or
-INFEAS (give the stuck vertex the colour with the fewest conflicts with earlier
neighbours, ties to the smallest, and continue).
"""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np

from reasoning_heuristics.heuristics.answers import colouring_key
from reasoning_heuristics.heuristics.base import Prediction, member
from reasoning_heuristics.heuristics.tasks import ColouringTask
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.coloring.graph import Graph, label_key

D = "coloring"


def effective_graph(task: ColouringTask) -> Graph:
    """The graph whose proper colourings answer the *stated* question."""
    g = task.graph
    if not task.complement:
        return g
    present = {frozenset(e) for e in g.edges}
    vs = g.vertices
    edges = tuple((vs[i], vs[j]) for i in range(len(vs)) for j in range(i + 1, len(vs)) if frozenset((vs[i], vs[j])) not in present)
    return Graph(vs, edges)


def resolve_order(task: ColouringTask, g: Graph, params: dict[str, Any]) -> list[str]:
    order = params.get("order", "LIST")
    if order == "LIST":
        return list(g.vertices)
    if order == "LABEL":
        return g.label_order()
    if order == "REV":
        return list(reversed(g.vertices))
    if order == "EDGE":
        return g.edge_mention_order()
    if order == "OUT":
        if task.answer_order is None:
            if "sequence" not in params:
                raise ValueError("FF-OUT under FREE needs the emitted order as params['sequence']")
            return list(params["sequence"])
        return list(task.answer_order)
    if order == "EXPLICIT":
        return list(params["sequence"])
    if order == "DEGREE":
        tie = params.get("tie", "LIST")
        key = (lambda v: g.position[v]) if tie == "LIST" else label_key
        return sorted(g.vertices, key=lambda v: (-g.degree(v), key(v)))
    raise ValueError(f"unknown order {order}")


def _assign(g: Graph, col: dict[str, int], v: str, k: int | None, mode: str, trace: dict) -> bool:
    """Give v its first-fit colour given the coloured neighbours. Returns False on ABORT."""
    used = {col[u] for u in g.adj[v] if u in col}
    c = 1
    while c in used:
        c += 1
    if k is None or c <= k:
        col[v] = c
        return True
    trace.setdefault("stuck_vertex", v)
    if mode == "ABORT":
        return False
    counts = Counter(col[u] for u in g.adj[v] if u in col)
    col[v] = min(range(1, k + 1), key=lambda x: (counts[x], x))
    return True


def first_fit(task: ColouringTask, g: Graph, sequence: list[str], k: int | None, mode: str) -> Prediction:
    col = task.fixed_dict()
    trace: dict[str, Any] = {"commit_order": [], "revisions": 0}
    for v in sequence:
        if v in col:
            continue
        if not _assign(g, col, v, k, mode, trace):
            trace["commit_order"].append(v)
            return Prediction("IMPOSSIBLE", trace)
        trace["commit_order"].append(v)
    trace["colours_used"] = len(set(col.values()))
    trace["conflicts"] = [f"{u}-{v}" for u, v in G.conflicts(g, col)]
    return Prediction(dict(col), trace)


@member("FF", "C1", D, "commits vertices in order σ; colour = smallest number not used by an earlier neighbour; no revisions")
def ff(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    g = effective_graph(task)
    k = params.get("k", task.k)
    return first_fit(task, g, resolve_order(task, g, params), k, params.get("mode", "ABORT"))


@member("LF", "C1", D, "commits vertices by degree, highest first; first-fit colour; cites degree")
def lf(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    g = effective_graph(task)
    seq = resolve_order(task, g, {"order": "DEGREE", "tie": params.get("tie", "LIST")})
    return first_fit(task, g, seq, params.get("k", task.k), params.get("mode", "ABORT"))


@member("DSATUR", "C2", D, "next vertex = most distinct colours among its neighbours ('most constrained'); first-fit colour")
def dsatur(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    g = effective_graph(task)
    k = params.get("k", task.k)
    mode = params.get("mode", "ABORT")
    tie_key = (lambda v: g.position[v]) if params.get("tie", "LIST") == "LIST" else label_key
    col = task.fixed_dict()
    trace: dict[str, Any] = {"commit_order": [], "revisions": 0}
    while len(col) < g.n:
        def score(v: str):
            sat = len({col[u] for u in g.adj[v] if u in col})
            deg_uncoloured = sum(1 for u in g.adj[v] if u not in col)
            return (-sat, -deg_uncoloured, tie_key(v))

        v = min((v for v in g.vertices if v not in col), key=score)
        trace["commit_order"].append(v)
        if not _assign(g, col, v, k, mode, trace):
            return Prediction("IMPOSSIBLE", trace)
    trace["colours_used"] = len(set(col.values()))
    return Prediction(dict(col), trace)


@member("RO-FF", "C3", D, "commit order uncorrelated with listing, label and answer order; first-fit colour; arbitrary-choice statements", deterministic=False)
def ro_ff(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    """Random-order first-fit, estimated by Monte Carlo (fixed seed, so recomputation is exact)."""
    g = effective_graph(task)
    k = params.get("k", task.k)
    samples = params.get("samples", 2000)
    rng = np.random.default_rng(params.get("seed", 0))
    counts: Counter[str] = Counter()
    free = [v for v in g.vertices if v not in task.fixed_dict()]
    for _ in range(samples):
        seq = [free[i] for i in rng.permutation(len(free))]
        pred = first_fit(task, g, seq, k, params.get("mode", "ABORT"))
        counts[colouring_key(pred.answer)] += 1
    top = counts.most_common(params.get("keep", 25))
    dist = {key: c / samples for key, c in top}
    rest = 1.0 - sum(dist.values())
    if rest > 1e-12:
        dist["_other"] = rest
    trace = {"samples": samples, "distinct_outcomes": len(counts), "modal_probability": top[0][1] / samples}
    return Prediction(None, trace, dist)


@member("GREEDY+REPAIR", "C->F", D, "a complete first-fit pass in order σ, then verification, then local recolouring confined to the top colour class or conflicted vertices")
def greedy_repair(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    g = effective_graph(task)
    seq = resolve_order(task, g, params)
    k = params.get("k", task.k)
    first = first_fit(task, g, seq, k, "INFEAS")
    col = dict(first.answer)
    repaired: list[str] = []
    fixed = task.fixed_dict()
    if k is None:
        while True:
            top = max(col.values())
            movable = [v for v in seq if col[v] == top and v not in fixed]
            trial = dict(col)
            ok = True
            for v in movable:
                used = {trial[u] for u in g.adj[v]}
                lower = [c for c in range(1, top) if c not in used]
                if not lower:
                    ok = False
                    break
                trial[v] = lower[0]
            if not ok or top == 1:
                break
            repaired += movable
            col = trial
    else:
        for _ in range(params.get("max_steps", 10 * g.n)):
            bad = {x for e in G.conflicts(g, col) for x in e} - set(fixed)
            if not bad:
                break
            v = next(x for x in seq if x in bad)
            counts = Counter(col[u] for u in g.adj[v])
            best = min((c for c in range(1, k + 1) if c != col[v]), key=lambda c: (counts[c], c))
            if counts[best] > counts[col[v]]:
                break  # local minimum: no improving move
            col[v] = best
            repaired.append(v)
    trace = {"commit_order": first.trace_features["commit_order"], "repaired_vertices": repaired,
             "revisions": len(repaired), "colours_used": len(set(col.values())),
             "conflicts": [f"{u}-{v}" for u, v in G.conflicts(g, col)]}
    return Prediction(col, trace)


@member("LOCAL-t", "E", D, "no sequential commitments; each vertex looks at its neighbours for t rounds", deterministic=True)
def local_t(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    """t rounds of ID-based local greedy. IDs = listing positions (LIST) or labels (LABEL).

    With t = infinity this is exactly first-fit in ID order (C §1.3).
    """
    g = effective_graph(task)
    ids = params.get("ids", "LIST")
    rank = {v: i for i, v in enumerate(g.vertices if ids == "LIST" else g.label_order())}
    t = params["t"]
    default = params.get("default", "one")
    col = task.fixed_dict()
    for _ in range(t):
        ready = [v for v in g.vertices if v not in col and all(rank[v] < rank[u] for u in g.adj[v] if u not in col)]
        if not ready:
            break
        new = {}
        for v in ready:
            used = {col[u] for u in g.adj[v] if u in col}
            c = 1
            while c in used:
                c += 1
            new[v] = c
        col.update(new)
    leftovers = [v for v in g.vertices if v not in col]
    if default == "one":
        for v in leftovers:
            col[v] = 1
    elif default == "free":
        snapshot = dict(col)
        for v in leftovers:
            used = {snapshot[u] for u in g.adj[v] if u in snapshot}
            c = 1
            while c in used:
                c += 1
            col[v] = c
    else:
        raise ValueError(default)
    trace = {"rounds": t, "leftovers": leftovers, "valid": G.is_proper(g, col)}
    return Prediction(col, trace)


@member("ONLINE-FF", "C4", D, "reads the edge list once in order; colours a vertex at first appearance; never recolours")
def online_ff(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    """C4 online first-fit: violations can only lie on closing edges (both ends already coloured)."""
    g = effective_graph(task)
    k = params.get("k", task.k)
    col = task.fixed_dict()
    seen: dict[str, set[str]] = {v: set() for v in g.vertices}
    closing_conflicts = []
    order = []
    for u, v in g.edges:
        seen[u].add(v)
        seen[v].add(u)
        for x in (u, v):
            if x not in col:
                used = {col[y] for y in seen[x] if y in col}
                c = 1
                while c in used:
                    c += 1
                if k is not None and c > k:
                    counts = Counter(col[y] for y in seen[x] if y in col)
                    c = min(range(1, k + 1), key=lambda z: (counts[z], z))
                col[x] = c
                order.append(x)
        if col[u] == col[v]:
            closing_conflicts.append(f"{u}-{v}")
    for v in g.vertices:
        if v not in col:
            col[v] = 1
            order.append(v)
    return Prediction(col, {"commit_order": order, "conflicts": closing_conflicts, "revisions": 0})


def _exact_on(task: ColouringTask, g: Graph, k: int | None) -> tuple[dict[str, int] | str, int]:
    if k is None:
        chi = G.chromatic_number(g) if not task.fixed else None
        if chi is None:
            raise ValueError("fixed vertices need a k task")
        return G.k_colour(g, chi), chi
    sol = G.k_colour(g, k, task.fixed_dict())
    return (sol if sol is not None else "IMPOSSIBLE"), k


@member("PHANTOM", "B4", D, "quotes constraints that are not in the instance (phantom edges); false IMPOSSIBLE")
def phantom(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    """ADD-CONSTRAINT: add phantom edges, then solve exactly. pairs = 'adjacent-listed' or explicit."""
    g = effective_graph(task)
    pairs = params.get("pairs", "adjacent-listed")
    extra = list(zip(g.vertices, g.vertices[1:])) if pairs == "adjacent-listed" else [tuple(p) for p in pairs]
    added = [e for e in extra if not g.has_edge(*e)]
    g2 = Graph(g.vertices, g.edges + tuple(added))
    sol, _ = _exact_on(task, g2, params.get("k", task.k))
    return Prediction(sol, {"phantom_edges": [f"{u}-{v}" for u, v in added]})


@member("DROP-LAST", "B1", D, "neighbourhoods quoted without the late edges; conflicts on dropped edges")
def drop_last(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    g = effective_graph(task)
    q = params["q"]
    kept = g.edges[: max(0, g.m - q)]
    sol, _ = _exact_on(task, Graph(g.vertices, kept), params.get("k", task.k))
    conflicts = [] if isinstance(sol, str) else [f"{u}-{v}" for u, v in G.conflicts(g, sol)]
    return Prediction(sol, {"dropped": [f"{u}-{v}" for u, v in g.edges[len(kept):]], "conflicts": conflicts})


@member("EXACT", "null", D, "a completed procedure: a checked witness, or a closed refutation")
def exact(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    """Set-valued: any valid (k task) or optimal (fewest task) colouring. The answer is the
    decision; `witness` is one solution."""
    g = effective_graph(task)
    sol, k = _exact_on(task, g, task.k)
    if isinstance(sol, str):
        return Prediction("IMPOSSIBLE", {"set_valued": False})
    decision = f"CHI={k}" if task.k is None else "POSSIBLE"
    return Prediction(decision, {"set_valued": True, "witness": sol})


@member("TT", "A3", D, "restates the rule in textbook form ('pairs need different rooms'); checks use textbook semantics")
def textbook_transfer(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    """TT[T, s]: answer the textbook (un-inverted) problem with inner solver s ∈ {EXACT, FF}."""
    textbook = ColouringTask(task.graph, task.k, task.fixed, task.answer_order, complement=False)
    inner = params.get("inner", "EXACT")
    if inner == "EXACT":
        sol = G.k_colour(textbook.graph, task.k) if task.k is not None else G.k_colour(textbook.graph, G.chromatic_number(textbook.graph))
        return Prediction(sol if sol is not None else "IMPOSSIBLE", {"inner": "EXACT"})
    if inner == "FF":
        return ff(textbook, {"order": params.get("order", "LIST"), "mode": "ABORT"})
    raise ValueError(inner)


@member("RANDOM", "H", D, "no procedure determines the answer; trace content and verdict unrelated", deterministic=False)
def random_colouring(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    """Uniform over colourings with colours 1..k (k = task k, or the number of vertices)."""
    k = task.k or task.graph.n
    return Prediction(None, {"set_valued": True, "uniform_over": f"{k}^{task.graph.n} colourings"})


@member("NOISY-EXACT", "nuisance", D, "correct procedure with sporadic violations of its own stated rule", deterministic=False)
def noisy_exact(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    """Slip model: the exact answer survives L steps with prob (1-p)^L, L = number of edges read."""
    g = effective_graph(task)
    p = params.get("p", 0.01)
    L = params.get("L", g.m)
    q = (1 - p) ** L
    return Prediction(None, {"p": p, "L": L, "P(exact)": round(q, 4)}, {"_exact": q, "_other": 1 - q})
