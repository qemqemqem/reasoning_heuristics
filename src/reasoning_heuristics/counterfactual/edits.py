"""Minimal-edit search (SCOPE §4 item 7; C E2).

Enumerate single edits of a base task, run every listed member and the ground truth on
each edited task, and keep the edits whose *change signature* (which outputs changed)
matches a request, e.g. "FF changes, DSATUR does not, the truth does not" (a single
dissociation), "nothing changes" (placebo) or "only the truth changes" (G-ONLY).

Edit kinds per domain:
- colouring: add_edge, delete_edge
- SAT: flip_sign, replace_var, delete_clause, swap_clauses (order only)
- knapsack: value or weight +-1..6, staying two-digit
- TSP: move one city by 1-3 grid units
- entailment: flip_literal (negation of one literal occurrence)
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Any, Callable, Iterator

from reasoning_heuristics.heuristics.answers import answer_key
from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.tasks import ColouringTask, EntailmentTask, KnapsackTask, SatTask, TspTask
from reasoning_heuristics.problems.coloring.graph import Graph
from reasoning_heuristics.problems.entailment import formula as F


@dataclass(frozen=True)
class Edit:
    kind: str
    args: tuple
    text: str

    def to_json(self) -> dict[str, Any]:
        return {"kind": self.kind, "args": list(self.args), "text": self.text}


def colouring_edits(task: ColouringTask, kinds=("add_edge", "delete_edge")) -> Iterator[tuple[Edit, ColouringTask]]:
    g = task.graph
    if "add_edge" in kinds:
        for u, v in itertools.combinations(g.vertices, 2):
            if not g.has_edge(u, v):
                yield Edit("add_edge", (u, v), f"add edge {u}-{v}"), ColouringTask(g.with_edge(u, v), task.k, task.fixed, task.answer_order, task.complement)
    if "delete_edge" in kinds:
        for u, v in g.edges:
            yield Edit("delete_edge", (u, v), f"delete edge {u}-{v}"), ColouringTask(g.without_edge(u, v), task.k, task.fixed, task.answer_order, task.complement)


def sat_edits(task: SatTask, kinds=("flip_sign", "replace_var", "delete_clause")) -> Iterator[tuple[Edit, SatTask]]:
    cnf = task.cnf

    def with_clauses(cl):
        return SatTask(cnf.with_clauses(cl), task.fixed, task.answer_order, task.declared, task.inverted)

    for i, c in enumerate(cnf.clauses):
        for j, lit in enumerate(c):
            if "flip_sign" in kinds:
                new = list(cnf.clauses)
                new[i] = c[:j] + (-lit,) + c[j + 1:]
                yield Edit("flip_sign", (i, j), f"flip the sign of {cnf.name(lit)} in C{i + 1}"), with_clauses(new)
            if "replace_var" in kinds:
                for v in range(1, cnf.n + 1):
                    if v in {abs(x) for x in c}:
                        continue
                    new = list(cnf.clauses)
                    new[i] = c[:j] + ((v if lit > 0 else -v),) + c[j + 1:]
                    yield Edit("replace_var", (i, j, v), f"replace {cnf.name(lit)} by {cnf.var_names[v - 1]} in C{i + 1}"), with_clauses(new)
        if "delete_clause" in kinds:
            new = list(cnf.clauses[:i]) + list(cnf.clauses[i + 1:])
            yield Edit("delete_clause", (i,), f"delete C{i + 1}"), with_clauses(new)
    if "swap_clauses" in kinds:
        for i in range(cnf.m - 1):
            new = list(cnf.clauses)
            new[i], new[i + 1] = new[i + 1], new[i]
            yield Edit("swap_clauses", (i, i + 1), f"swap C{i + 1} and C{i + 2}"), with_clauses(new)


def knapsack_edits(task: KnapsackTask, deltas=range(1, 7)) -> Iterator[tuple[Edit, KnapsackTask]]:
    k = task.knapsack
    for name in k.names:
        i = k.names.index(name)
        for field in ("value", "weight"):
            base = k.values[i] if field == "value" else k.weights[i]
            for d in list(deltas) + [-x for x in deltas]:
                new = base + d
                if not 10 <= new <= 99:
                    continue
                k2 = k.with_item(name, **{field: new})
                yield Edit(f"{field}_delta", (name, d), f"{field} of {name} {base} -> {new}"), KnapsackTask(k2, task.covering, task.answer_order)


def tsp_edits(task: TspTask, max_step: int = 3, grid: int = 100) -> Iterator[tuple[Edit, TspTask]]:
    t = task.tsp
    for i, name in enumerate(t.names):
        x, y = t.coords[i]
        for dx in range(-max_step, max_step + 1):
            for dy in range(-max_step, max_step + 1):
                if (dx, dy) == (0, 0) or not (0 <= x + dx < grid and 0 <= y + dy < grid):
                    continue
                if (x + dx, y + dy) in t.coords:
                    continue
                yield Edit("move_city", (name, dx, dy), f"move {name} by ({dx}, {dy})"), TspTask(t.moved(name, (x + dx, y + dy)), task.start)


def entailment_edits(task: EntailmentTask) -> Iterator[tuple[Edit, EntailmentTask]]:
    from reasoning_heuristics.heuristics.entailment import _flip_nth

    for i, p in enumerate(task.premises):
        for j in range(len(F.literals(p))):
            prem = task.premises[:i] + (_flip_nth(p, j),) + task.premises[i + 1:]
            yield Edit("flip_literal", (i, j), f"flip literal {j + 1} of premise {i + 1}"), EntailmentTask(prem, task.probe, task.fmt, task.options, task.reading)


EDITORS: dict[str, Callable] = {
    "coloring": colouring_edits, "sat": sat_edits, "knapsack": knapsack_edits, "tsp": tsp_edits,
    "entailment": entailment_edits,
}

MemberSpec = tuple[str, str, dict[str, Any]]  # (label, registry name, params)


def outputs(task: Any, members: list[MemberSpec]) -> dict[str, str | None]:
    out = {}
    for label, name, params in members:
        pred = run(task.domain, name, task, params)
        out[label] = answer_key(task.domain, pred.answer) if pred.answer is not None else repr(sorted((pred.distribution or {}).items()))
    return out


def signature(before: dict[str, Any], after: dict[str, Any]) -> dict[str, bool]:
    return {k: before[k] != after[k] for k in before}


def search(task: Any, members: list[MemberSpec], truth: Callable[[Any], Any], wanted: Callable[[dict[str, bool]], bool],
           edits: Iterator[tuple[Edit, Any]] | None = None, limit: int | None = None) -> list[tuple[Edit, Any, dict[str, bool]]]:
    """Edits whose change signature (members plus key 'TRUTH') satisfies `wanted`."""
    base = outputs(task, members)
    base["TRUTH"] = truth(task)
    found = []
    for edit, new_task in (edits if edits is not None else EDITORS[task.domain](task)):
        after = outputs(new_task, members)
        after["TRUTH"] = truth(new_task)
        sig = signature(base, after)
        if wanted(sig):
            found.append((edit, new_task, sig))
            if limit is not None and len(found) >= limit:
                break
    return found


def flips_only(changed: set[str], fixed: set[str]) -> Callable[[dict[str, bool]], bool]:
    """Signature predicate: every key in `changed` changes and every key in `fixed` does not."""
    return lambda sig: all(sig[k] for k in changed) and not any(sig[k] for k in fixed)
