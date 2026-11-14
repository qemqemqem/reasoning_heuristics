"""The composite search member SEARCH(b, order, value, default) (theory §2.2 and §5.1).

Theory predicts that thinking models run one composite procedure rather than rival
families: truncated search (D) that orders its branching by a greedy order (C1/C2),
picks values by a one-shot score (C0), propagates units inside (B1), and answers with a
default (A1/A2) when it hits its budget. Here that is one parameterised member:

    SEARCH(b, order, value, default)
      b        decision budget (None = unbounded, i.e. a complete solver)
      order    variable / vertex order: SAT MENTION | INDEX | MOMS (dynamic);
               colouring LIST | LABEL | DEGREE | DSATUR (dynamic)
      value    SAT TRUE | FALSE | POLARITY; colouring SMALLEST
      default  answer when the budget runs out: UNSAT / IMPOSSIBLE (A1), SAT-FILL
               (complete the current partial state with T; a SAT claim), DENSITY (A2 cue),
               or FF-INFEAS (colouring: finish the current state by first-fit)
      up       unit propagation inside the search (SAT; default True)

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
    pass


def _clause_state(c, values):
    vals = [S.lit_value(l, values) for l in c]
    if True in vals:
        return "sat", []
    open_lits = [l for l, v in zip(c, vals) if v is None]
    return ("falsified", []) if not open_lits else ("open", open_lits)


def search_sat(cnf: CNF, start: dict[int, bool], params: dict[str, Any]) -> tuple[dict[int, bool] | None, dict[str, Any]]:
    """Chronological DPLL. Raises BudgetExhausted after b decisions."""
    order = params.get("order", "MENTION")
    value = params.get("value", "TRUE")
    b = params.get("b")
    use_up = params.get("up", True)
    pure = params.get("pure", False)
    trace = {"decisions": 0, "backtracks": 0, "propagations": 0, "decision_order": []}
    mention = cnf.mention_order() + [v for v in range(1, cnf.n + 1) if v not in cnf.mention_order()]
    index_order = sorted(range(1, cnf.n + 1), key=lambda v: label_key(cnf.var_names[v - 1]))
    pos, neg = Counter(), Counter()
    for c in cnf.clauses:
        for l in c:
            (pos if l > 0 else neg)[abs(l)] += 1

    def propagate(values):
        values = dict(values)
        changed = True
        while changed:
            changed = False
            for c in cnf.clauses:
                state, lits = _clause_state(c, values)
                if state == "falsified":
                    return None
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
        return values

    def pick(values):
        free = [v for v in range(1, cnf.n + 1) if v not in values]
        if not free:
            return None
        if order == "MENTION":
            return next(v for v in mention if v not in values)
        if order == "INDEX":
            return next(v for v in index_order if v not in values)
        if order == "MOMS":
            open_c = [lits for c in cnf.clauses for st, lits in [_clause_state(c, values)] if st == "open"]
            if not open_c:
                return next(v for v in mention if v not in values)
            w = min(len(l) for l in open_c)
            cnt = Counter(abs(l) for lits in open_c if len(lits) == w for l in lits)
            return max(free, key=lambda v: (cnt[v], -mention.index(v)))
        raise ValueError(order)

    def first_value(v):
        if value == "TRUE":
            return True
        if value == "FALSE":
            return False
        if value == "POLARITY":
            return pos[v] >= neg[v]
        raise ValueError(value)

    def rec(values):
        values = propagate(values)
        if values is None:
            return None
        v = pick(values)
        if v is None:
            return values
        if b is not None and trace["decisions"] >= b:
            raise BudgetExhausted(values)
        trace["decisions"] += 1
        trace["decision_order"].append(cnf.var_names[v - 1])
        first = first_value(v)
        for val in (first, not first):
            res = rec({**values, v: val})
            if res is not None:
                return res
            trace["backtracks"] += 1
        return None

    return rec(dict(start)), trace


@member("SEARCH", "D", "sat", "branch / contradiction / backtrack events in order σ; IMPOSSIBLE only after an exhaustive refutation, or the default after the budget")
def search_sat_member(task: SatTask, params: dict[str, Any]) -> Prediction:
    from reasoning_heuristics.heuristics.sat import cue_values, effective_cnf

    cnf = effective_cnf(task)
    start = {cnf.index(k): v for k, v in task.fixed}
    try:
        values, trace = search_sat(cnf, start, params)
    except BudgetExhausted as exc:
        partial = exc.args[0]
        default = params.get("default", "UNSAT")
        trace = {"exhausted": True, "decisions": params.get("b")}
        if default == "UNSAT":
            return Prediction("UNSAT", trace)
        if default == "SAT-FILL":
            filled = {v: partial.get(v, True) for v in range(1, cnf.n + 1)}
            return Prediction(S.to_assignment(cnf, filled), trace)
        if default == "DENSITY":
            alpha = cue_values(task)["alpha_U"]
            return Prediction("UNSAT" if alpha >= params.get("theta", 4.26) else "SAT", trace)
        raise ValueError(default)
    trace["exhausted"] = False
    if values is None:
        return Prediction("UNSAT", trace)
    full = {v: values.get(v, True) for v in range(1, cnf.n + 1)}
    return Prediction(S.to_assignment(cnf, full), trace)


def search_colouring(task: ColouringTask, k: int, params: dict[str, Any]) -> tuple[dict[str, int] | None, dict[str, Any]]:
    g = effective_graph(task)
    order = params.get("order", "LIST")
    b = params.get("b")
    trace = {"decisions": 0, "backtracks": 0, "decision_order": []}
    static = None if order == "DSATUR" else resolve_order(task, g, {"order": order, "tie": params.get("tie", "LIST")})
    tie = (lambda v: g.position[v]) if params.get("tie", "LIST") == "LIST" else label_key
    col = task.fixed_dict()

    def pick():
        free = [v for v in g.vertices if v not in col]
        if not free:
            return None
        if static is not None:
            return next(v for v in static if v not in col)
        return min(free, key=lambda v: (-len({col[u] for u in g.adj[v] if u in col}), -sum(1 for u in g.adj[v] if u not in col), tie(v)))

    def rec() -> bool:
        v = pick()
        if v is None:
            return True
        used = {col[u] for u in g.adj[v] if u in col}
        for c in range(1, k + 1):
            if c in used:
                continue
            if b is not None and trace["decisions"] >= b:
                raise BudgetExhausted(dict(col))
            trace["decisions"] += 1
            trace["decision_order"].append(v)
            col[v] = c
            if rec():
                return True
            del col[v]
            trace["backtracks"] += 1
        return False

    return (dict(col) if rec() else None), trace


@member("SEARCH", "D", "coloring", "chronological backtracking in order σ, smallest colour first; IMPOSSIBLE only after exhaustive refutation, or the default after the budget")
def search_colouring_member(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    g = effective_graph(task)
    k = task.k if task.k is not None else G.chromatic_number(g)
    try:
        col, trace = search_colouring(task, k, params)
    except BudgetExhausted as exc:
        partial = exc.args[0]
        default = params.get("default", "IMPOSSIBLE")
        trace = {"exhausted": True, "decisions": params.get("b")}
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
