"""The composite search member SEARCH(b, order, value, default) (theory §2.2 and §5.1).

Theory predicts that thinking models run one composite procedure rather than rival
families: truncated search (D) that orders its branching by a greedy order (C1/C2),
picks values by a one-shot score (C0), propagates units inside (B1), and answers with a
default (A1/A2) when it hits its budget. Here that is one parameterised member:

    SEARCH(b, order, value, default)
      b        node budget: decisions + flipped re-assignments (D/F §1.2); None = unbounded,
               i.e. a complete solver
      order    variable / vertex order: SAT MENTION | INDEX | MOMS (dynamic);
               colouring LIST | LABEL | DEGREE | DSATUR (dynamic), or any static order
               `resolve_order` knows
      value    SAT TRUE | FALSE | POLARITY; colouring: smallest colour first
      default  answer when the budget runs out: UNSAT / IMPOSSIBLE (A1), SAT-FILL
               (complete the last conflict-free state A* by the value rule; a SAT claim),
               DENSITY (A2 cue), or FF-INFEAS (colouring: finish A* by first-fit)
      up       unit propagation inside the search (SAT; default True)
      pure     pure-literal elimination inside the search (SAT; default False)

SAT is D/F §1.3 `DPLL-b(H, V, Δ, CHR)`: unit propagation to a fixpoint after every
assignment; SAT as soon as every clause is satisfied; on a falsified clause, flip the
latest unflipped decision; UNSAT only when no unflipped decision is left. Colouring is
D/F §1.3 `DPLL-b` with forward checking (FC-BT): each vertex keeps a domain, a singleton
domain assigns its vertex for free (the analogue of UP), an empty domain is a conflict,
colours are tried lowest first, and every colour tried at a vertex is a node.

Readings (docs/GENERATORS.md): the order only branches on variables that occur in a clause
and vertices that have an edge, so declared-but-unused variables and isolated vertices are
filled by the value rule once every constraint holds and never cost budget (A/H E2 level U
predicts no change for D); on a fewest-colours task the colouring search is given k = χ.

`DPLL-σ-b` (D) is SEARCH(b, σ, TRUE|SMALLEST, UNSAT|IMPOSSIBLE); with b = None and the
same σ it coincides with FF-σ wherever first-fit succeeds (C §1.4).
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from reasoning_heuristics.heuristics.base import Prediction, member
from reasoning_heuristics.heuristics.coloring import effective_graph, first_fit, resolve_order
from reasoning_heuristics.heuristics.tasks import ColouringTask, SatTask
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.coloring.graph import label_key
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.sat.cnf import CNF


class BudgetExhausted(Exception):
    """The node budget ran out. args = (A*, the last conflict-free state; the trace so far)."""


def _new_trace() -> dict[str, Any]:
    return {"nodes": 0, "decisions": 0, "flips": 0, "conflicts": 0, "propagations": 0, "decision_order": []}


def _clause_state(c, values):
    vals = [S.lit_value(l, values) for l in c]
    if True in vals:
        return "sat", []
    open_lits = [l for l, v in zip(c, vals) if v is None]
    return ("falsified", []) if not open_lits else ("open", open_lits)


# --- SAT ------------------------------------------------------------------------------------------


def _value_rule(cnf: CNF, value: str):
    """V(v): the value tried first, and the value FILL gives an unassigned variable."""
    pos, neg = Counter(), Counter()
    for c in cnf.clauses:
        for l in c:
            (pos if l > 0 else neg)[abs(l)] += 1
    if value == "TRUE":
        return lambda v: True
    if value == "FALSE":
        return lambda v: False
    if value == "POLARITY":
        return lambda v: pos[v] >= neg[v]
    raise ValueError(value)


def fill_sat(cnf: CNF, values: dict[int, bool], value: str) -> dict[int, bool]:
    """fill(A, V): complete a partial assignment by the value rule."""
    rule = _value_rule(cnf, value)
    return {v: values[v] if v in values else rule(v) for v in range(1, cnf.n + 1)}


def search_sat(cnf: CNF, start: dict[int, bool], params: dict[str, Any]) -> tuple[dict[int, bool] | None, dict[str, Any]]:
    """D/F §1.3 DPLL-b with chronological backtracking.

    Returns (a total assignment, trace), or (None, trace) after an exhaustive refutation.
    Raises BudgetExhausted(A*, trace) when the nodes reach b first."""
    order = params.get("order", "MENTION")
    value = params.get("value", "TRUE")
    b = params.get("b")
    use_up = params.get("up", True)
    pure = params.get("pure", False)
    trace = _new_trace()
    mention = cnf.mention_order()  # the variables that occur in some clause, by first mention
    mention_pos = {v: i for i, v in enumerate(mention)}
    index_order = sorted(mention, key=lambda v: label_key(cnf.var_names[v - 1]))
    first_value = _value_rule(cnf, value)

    def propagate(values: dict[int, bool]) -> tuple[dict[int, bool], bool]:
        """UP to a fixpoint (D/F §1.2), then pure literals if asked. Returns (values, conflict)."""
        values = dict(values)
        changed = True
        while changed:
            changed = False
            for c in cnf.clauses:
                state, lits = _clause_state(c, values)
                if state == "falsified":
                    return values, True
                if use_up and state == "open" and len(lits) == 1:
                    values[abs(lits[0])] = lits[0] > 0
                    trace["propagations"] += 1
                    changed = True
            if pure and not changed:
                signs: dict[int, set[bool]] = {}
                for c in cnf.clauses:
                    if _clause_state(c, values)[0] == "open":
                        for l in c:
                            if abs(l) not in values:
                                signs.setdefault(abs(l), set()).add(l > 0)
                for v, s in signs.items():
                    if len(s) == 1:
                        values[v] = next(iter(s))
                        changed = True
        return values, False

    def pick(values: dict[int, bool]) -> int:
        if order == "MENTION":
            return next(v for v in mention if v not in values)
        if order == "INDEX":
            return next(v for v in index_order if v not in values)
        if order == "MOMS":
            # most occurrences in the shortest open clauses; ties: OCC (occurrences in all open
            # clauses), then MENTION (D/F §1.2)
            open_c = [lits for c in cnf.clauses for st, lits in [_clause_state(c, values)] if st == "open"]
            w = min(len(lits) for lits in open_c)
            moms = Counter(abs(l) for lits in open_c if len(lits) == w for l in lits)
            occ = Counter(abs(l) for lits in open_c for l in lits)
            return max((v for v in mention if v not in values), key=lambda v: (moms[v], occ[v], -mention_pos[v]))
        raise ValueError(order)

    def all_satisfied(values: dict[int, bool]) -> bool:
        return all(any(S.lit_value(l, values) is True for l in c) for c in cnf.clauses)

    A, conflict = propagate(dict(start))
    best = dict(start) if conflict else A  # A*: the last conflict-free state
    trail: list[tuple[int, bool, bool, dict[int, bool]]] = []  # (var, value, flipped, state before)
    while True:
        if not conflict and all_satisfied(A):
            return fill_sat(cnf, A, value), trace
        if b is not None and trace["nodes"] >= b:
            raise BudgetExhausted(dict(best), trace)
        if conflict:
            trace["conflicts"] += 1
            while trail and trail[-1][2]:
                trail.pop()
            if not trail:
                return None, trace
            var, val, _, before = trail.pop()
            trail.append((var, not val, True, before))
            A, conflict = propagate({**before, var: not val})
            trace["flips"] += 1
        else:
            v = pick(A)
            val = first_value(v)
            trail.append((v, val, False, A))
            A, conflict = propagate({**A, v: val})
            trace["decisions"] += 1
            trace["decision_order"].append(cnf.var_names[v - 1])
        trace["nodes"] += 1
        if not conflict:
            best = A


@member("SEARCH", "D", "sat", "branch / contradiction / backtrack events in order σ; IMPOSSIBLE only after an exhaustive refutation, or the default after the budget")
def search_sat_member(task: SatTask, params: dict[str, Any]) -> Prediction:
    from reasoning_heuristics.heuristics.sat import cue_values, effective_cnf

    cnf = effective_cnf(task)
    start = {cnf.index(k): v for k, v in task.fixed}
    try:
        values, trace = search_sat(cnf, start, params)
    except BudgetExhausted as exc:
        partial, trace = exc.args
        default = params.get("default", "UNSAT")
        trace = {**trace, "exhausted": True}
        if default == "UNSAT":
            return Prediction("UNSAT", trace)
        if default == "SAT-FILL":
            return Prediction(S.to_assignment(cnf, fill_sat(cnf, partial, params.get("value", "TRUE"))), trace)
        if default == "DENSITY":
            alpha = cue_values(task)["alpha_U"]
            return Prediction("UNSAT" if alpha >= params.get("theta", 4.26) else "SAT", trace)
        raise ValueError(default)
    trace["exhausted"] = False
    if values is None:
        return Prediction("UNSAT", trace)
    return Prediction(S.to_assignment(cnf, values), trace)


# --- colouring ------------------------------------------------------------------------------------


def search_colouring(task: ColouringTask, k: int, params: dict[str, Any]) -> tuple[dict[str, int] | None, dict[str, Any]]:
    """D/F §1.3 colouring DPLL-b: backtracking with forward checking (FC-BT).

    Returns (a proper k-colouring, trace), or (None, trace) after an exhaustive refutation.
    Raises BudgetExhausted(A*, trace) when the nodes reach b first."""
    g = effective_graph(task)
    order = params.get("order", "LIST")
    b = params.get("b")
    trace = _new_trace()
    constrained = [v for v in g.vertices if g.degree(v) > 0]
    static = None
    if order != "DSATUR":
        static = [v for v in resolve_order(task, g, {"order": order, "tie": params.get("tie", "LIST")}) if g.degree(v) > 0]
    tie = (lambda v: g.position[v]) if params.get("tie", "LIST") == "LIST" else label_key
    fixed = task.fixed_dict()
    State = tuple[dict[str, int], dict[str, set[int]]]

    def propagate(col: dict[str, int], dom: dict[str, set[int]]) -> tuple[dict[str, int], dict[str, set[int]], bool]:
        """Forward checking to a fixpoint: a singleton domain assigns its vertex and removes its
        colour from the neighbours' domains; an empty domain is a conflict."""
        changed = True
        while changed:
            changed = False
            for v in g.vertices:
                if v in col:
                    continue
                if not dom[v]:
                    return col, dom, True
                if len(dom[v]) == 1:
                    (c,) = dom[v]
                    col[v] = c
                    trace["propagations"] += 1
                    for u in g.adj[v]:
                        if u not in col:
                            dom[u].discard(c)
                    changed = True
        return col, dom, False

    def assign(state: State, v: str, c: int):
        col, dom = dict(state[0]), {x: set(d) for x, d in state[1].items()}
        col[v] = c
        for u in g.adj[v]:
            if u not in col:
                dom[u].discard(c)
        return propagate(col, dom)

    def pick(col: dict[str, int], dom: dict[str, set[int]]) -> str:
        if static is not None:
            return next(v for v in static if v not in col)
        free = [v for v in constrained if v not in col]
        return min(free, key=lambda v: (len(dom[v]), -sum(1 for u in g.adj[v] if u not in col), tie(v)))

    def fill(col: dict[str, int]) -> dict[str, int]:
        return {v: col.get(v, 1) for v in g.vertices}  # only isolated vertices are left: smallest colour

    col0 = dict(fixed)
    dom0 = {v: set(range(1, k + 1)) - {fixed[u] for u in g.adj[v] if u in fixed} for v in g.vertices if v not in fixed}
    if any(u in fixed and v in fixed and fixed[u] == fixed[v] for u, v in g.edges):
        col, dom, conflict = col0, dom0, True
    else:
        col, dom, conflict = propagate(col0, dom0)
    best = dict(fixed) if conflict else col  # A*: the last conflict-free state
    trail: list[tuple[str, list[int], State]] = []  # (vertex, colours still to try, state before)
    while True:
        if not conflict and all(v in col for v in constrained):
            return fill(col), trace
        if b is not None and trace["nodes"] >= b:
            raise BudgetExhausted(dict(best), trace)
        if conflict:
            trace["conflicts"] += 1
            while trail and not trail[-1][1]:
                trail.pop()
            if not trail:
                return None, trace
            v, rest, before = trail[-1]
            col, dom, conflict = assign(before, v, rest.pop(0))
            trace["flips"] += 1
        else:
            v = pick(col, dom)
            colours = sorted(dom[v])
            trail.append((v, colours[1:], (col, dom)))
            col, dom, conflict = assign((col, dom), v, colours[0])
            trace["decisions"] += 1
            trace["decision_order"].append(v)
        trace["nodes"] += 1
        if not conflict:
            best = col


@member("SEARCH", "D", "coloring", "chronological backtracking with forward checking in order σ, smallest colour first; IMPOSSIBLE only after exhaustive refutation, or the default after the budget")
def search_colouring_member(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    g = effective_graph(task)
    k = task.k if task.k is not None else G.chromatic_number(g)
    try:
        col, trace = search_colouring(task, k, params)
    except BudgetExhausted as exc:
        partial, trace = exc.args
        default = params.get("default", "IMPOSSIBLE")
        trace = {**trace, "exhausted": True}
        if default == "IMPOSSIBLE":
            return Prediction("IMPOSSIBLE", trace)
        if default == "FF-INFEAS":
            rest = [v for v in resolve_order(task, g, {"order": params.get("order", "LIST") if params.get("order") != "DSATUR" else "LIST"}) if v not in partial]
            t2 = ColouringTask(task.graph, task.k, tuple(partial.items()), task.answer_order, task.complement)
            return first_fit(t2, g, rest, k, "INFEAS")
        raise ValueError(default)
    trace["exhausted"] = False
    trace["k"] = k
    return Prediction(col if col is not None else "IMPOSSIBLE", trace)
