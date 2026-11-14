"""Shared pieces of the C-vertical generators: label conventions, renderers that reproduce the
C library's prompts, structure maps for comparing answers across copies, and channels.

Conventions (C §1.2): vertex labels v10-v99 and variable labels x10-x99 (two digits, so
every label has the same proxy token count); the natural format c1 has labels ascending
along the listing order; answers follow `ANSWER:`.

A *structure map* sends each label of a copy to the index of the underlying base
vertex / variable, so partitions and assignments can be compared across isomorphic copies.
"""

from __future__ import annotations

from typing import Any, Callable

from reasoning_heuristics.generators.common import Channel, witness_channel
from reasoning_heuristics.heuristics.answers import answer_key
from reasoning_heuristics.problems.coloring.graph import Graph, label_key
from reasoning_heuristics.problems.coloring.render import render_edge_list, render_neighbours
from reasoning_heuristics.problems.sat.cnf import CNF, satisfies

COLOUR_FEWEST_FORMAT = "After the line ANSWER:, one line `vertex: colour` per vertex"
COLOUR_K_FORMAT = "After the line ANSWER:, IMPOSSIBLE or one line `vertex: colour` per vertex"
SAT_FORMAT = "After the line ANSWER:, UNSAT or `x=T` / `x=F` values"


def guard(attempt: int, params: dict, stats, what: str) -> None:
    """Fail loudly instead of looping forever when a design cell cannot be filled."""
    if attempt > params.get("max_attempts", 50_000):
        raise RuntimeError(f"{what}: no acceptance after {attempt - 1} attempts; rejections {stats.rejections}")


# --- labels -----------------------------------------------------------------------------------


def labels_for(n: int, prefix: str, rng) -> list[str]:
    """n distinct labels, sorted ascending. Two digits (10-99) when n <= 90, else three digits."""
    import numpy as np

    if n <= 90:
        nums = rng.choice(np.arange(10, 100), size=n, replace=False)
    else:
        nums = rng.choice(np.arange(100, 1000), size=n, replace=False)
    return sorted((f"{prefix}{int(x)}" for x in nums), key=label_key)


# --- colouring --------------------------------------------------------------------------------


def render_colouring(g: Graph, task: str, answer_order: list[str] | None, k: int | None = None,
                     serialisation: str = "adjacency", repeat_prompt: bool = False) -> str:
    """`serialisation`: "adjacency" (neighbour lines, the default) or "edge_list_shuffled"
    (the instance's edge order, which the generator shuffles once per base: theory §5 arm)."""
    if serialisation == "adjacency":
        return render_neighbours(g, task, answer_order, k, repeat_prompt)
    if serialisation == "edge_list_shuffled":
        return render_edge_list(g, task, answer_order, k, repeat_prompt)
    raise ValueError(serialisation)


def parse_partition_key(key: str) -> list[list[str]] | None:
    if key in ("IMPOSSIBLE", "") or "=" in key:
        return None
    return [c.split(",") for c in key.split("|")]


def optimal_partition_test(g: Graph, chi: int) -> Callable[[str], bool]:
    """Is an answer class a proper colouring with exactly chi colours?"""

    def test(key: str) -> bool:
        classes = parse_partition_key(key)
        if classes is None or len(classes) != chi or sorted(v for c in classes for v in c) != sorted(g.vertices):
            return False
        return all(not g.has_edge(u, v) for c in classes for i, u in enumerate(c) for v in c[i + 1:])

    return test


def colouring_channel(g: Graph, chi: int, n_optimal: int) -> Channel:
    return witness_channel("coloring", {"EXACT": (optimal_partition_test(g, chi), n_optimal),
                                        "RANDOM": (lambda key: False, 1)})


def structural_partition(col: Any, structure: dict[str, int]) -> frozenset | str:
    """A colouring as a partition of base-vertex indices (or the string answer itself)."""
    if isinstance(col, str):
        return col
    classes: dict[int, set[int]] = {}
    for v, c in col.items():
        if not v.startswith("_"):
            classes.setdefault(c, set()).add(structure[v])
    return frozenset(frozenset(s) for s in classes.values())


def structural_edges(g: Graph, structure: dict[str, int]) -> frozenset:
    return frozenset(frozenset((structure[u], structure[v])) for u, v in g.edges)


# --- SAT ----------------------------------------------------------------------------------------


def solution_test(cnf: CNF, fixed: dict[str, bool] | None = None) -> Callable[[str], bool]:
    def test(key: str) -> bool:
        if "=" not in key:
            return False
        a = {kv.split("=")[0]: kv.split("=")[1] == "T" for kv in key.split(",")}
        if any(a.get(k) != v for k, v in (fixed or {}).items()):
            return False
        return set(a) == set(cnf.var_names) and satisfies(cnf, a)

    return test


def sat_channel(cnf: CNF, n_solutions: int, fixed: dict[str, bool] | None = None) -> Channel:
    """EXACT is set-valued (uniform over the solutions) only when solutions exist; on an
    UNSAT item it answers UNSAT deterministically."""
    sv = {"RANDOM": (lambda key: False, 1)}
    if n_solutions > 0:
        sv["EXACT"] = (solution_test(cnf, fixed), n_solutions)
    return witness_channel("sat", sv)


def count_models(cnf: CNF, fixed: dict[str, bool] | None = None) -> int:
    """Exact model count over all declared variables: DPLL with unit propagation that
    multiplies by 2^free when every clause is satisfied (fast at the sizes used here)."""
    clauses = [frozenset(c) for c in cnf.clauses]
    start = {cnf.index(k): v for k, v in (fixed or {}).items()}

    def simplify(cls, lit):
        out = []
        for c in cls:
            if lit in c:
                continue
            if -lit in c:
                c = c - {-lit}
                if not c:
                    return None
            out.append(c)
        return out

    def rec(cls, assigned: int) -> int:
        while True:
            unit = next((c for c in cls if len(c) == 1), None)
            if unit is None:
                break
            (lit,) = unit
            cls = simplify(cls, lit)
            assigned += 1
            if cls is None:
                return 0
        if not cls:
            return 2 ** (cnf.n - assigned)
        v = abs(next(iter(cls[0])))
        total = 0
        for lit in (v, -v):
            sub = simplify(cls, lit)
            if sub is not None:
                total += rec(sub, assigned + 1)
        return total

    cls = clauses
    for v, val in start.items():
        cls = simplify(cls, v if val else -v)
        if cls is None:
            return 0
    return rec(cls, len(start))


def structural_assignment(a: Any, structure: dict[str, int]) -> tuple | str:
    if isinstance(a, str):
        return a
    return tuple(sorted((structure[k], v) for k, v in a.items() if not k.startswith("_")))


def hamming(a: dict[str, bool], b: dict[str, bool]) -> int:
    return sum(1 for k in a if a[k] != b[k])


def key_of(domain: str, answer: Any) -> str | None:
    return answer_key(domain, answer) if answer is not None else None
