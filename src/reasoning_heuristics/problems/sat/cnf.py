"""CNF instances, random generation and exact solving.

Literals are signed 1-based variable indices (DIMACS style); `var_names[i-1]` is the
display name of variable i. Clause order and literal order are presentation; the
content key sorts both away but keeps names (so it is not invariant to renaming).

Two independent exact procedures are provided so validators can recompute ground
truth without the generator's code path:

- `solve` / `count_solutions` use python-sat (MiniSat 2.2) — the generator path;
- `dpll_solve` is a plain recursive DPLL with unit propagation, and
  `brute_force_count` enumerates assignments — the validator path.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Iterable

import networkx as nx
import numpy as np
from pysat.solvers import Minisat22

Assignment = dict[str, bool]


@dataclass(frozen=True)
class CNF:
    var_names: tuple[str, ...]
    clauses: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        n = len(self.var_names)
        if len(set(self.var_names)) != n:
            raise ValueError("duplicate variable names")
        for c in self.clauses:
            if not c or any(lit == 0 or abs(lit) > n for lit in c):
                raise ValueError(f"bad clause {c} for {n} variables")

    @property
    def n(self) -> int:
        return len(self.var_names)

    @property
    def m(self) -> int:
        return len(self.clauses)

    def name(self, lit: int) -> str:
        return self.var_names[abs(lit) - 1]

    def index(self, name: str) -> int:
        return self.var_names.index(name) + 1

    def used_vars(self) -> list[int]:
        return sorted({abs(l) for c in self.clauses for l in c})

    def mention_order(self) -> list[int]:
        """Variables in order of first mention, scanning clauses in presentation order."""
        seen: dict[int, None] = {}
        for c in self.clauses:
            for lit in c:
                seen.setdefault(abs(lit), None)
        return list(seen)

    def to_json(self) -> dict:
        return {"kind": "cnf", "var_names": list(self.var_names), "clauses": [list(c) for c in self.clauses]}

    @classmethod
    def from_json(cls, data: dict) -> "CNF":
        assert data["kind"] == "cnf"
        return cls(tuple(data["var_names"]), tuple(tuple(c) for c in data["clauses"]))

    def content_key(self) -> dict:
        """Logical content: invariant to clause and literal order, not to renaming."""
        clauses = sorted(sorted((self.name(l), l > 0) for l in c) for c in self.clauses)
        return {"kind": "cnf", "vars": sorted(self.var_names), "clauses": clauses}

    def renamed(self, mapping: dict[str, str]) -> "CNF":
        return CNF(tuple(mapping[v] for v in self.var_names), self.clauses)

    def with_clauses(self, clauses: Iterable[Iterable[int]]) -> "CNF":
        return CNF(self.var_names, tuple(tuple(c) for c in clauses))


# --- evaluation -----------------------------------------------------------------------


def lit_value(lit: int, values: dict[int, bool]) -> bool | None:
    v = values.get(abs(lit))
    if v is None:
        return None
    return v if lit > 0 else not v


def falsified_clauses(cnf: CNF, assignment: Assignment) -> list[int]:
    """0-based indices of clauses with every literal false (assignment must be total on them)."""
    values = {cnf.index(k): v for k, v in assignment.items()}
    return [i for i, c in enumerate(cnf.clauses) if all(lit_value(l, values) is False for l in c)]


def satisfies(cnf: CNF, assignment: Assignment) -> bool:
    values = {cnf.index(k): v for k, v in assignment.items()}
    return all(any(lit_value(l, values) is True for l in c) for c in cnf.clauses)


def to_assignment(cnf: CNF, values: dict[int, bool]) -> Assignment:
    return {cnf.var_names[i - 1]: values[i] for i in sorted(values)}


# --- generator path: python-sat ------------------------------------------------------


def solve(cnf: CNF, fixed: Assignment | None = None) -> Assignment | None:
    """One satisfying assignment (unused variables set False), or None if UNSAT."""
    assumptions = [cnf.index(k) if v else -cnf.index(k) for k, v in (fixed or {}).items()]
    with Minisat22(bootstrap_with=[list(c) for c in cnf.clauses]) as s:
        if not s.solve(assumptions=assumptions):
            return None
        model = {abs(l): l > 0 for l in s.get_model()}
    return {name: model.get(i + 1, False) for i, name in enumerate(cnf.var_names)}


def count_solutions(cnf: CNF, limit: int | None = None, fixed: Assignment | None = None) -> int:
    """Number of satisfying total assignments (over all declared variables), up to `limit`."""
    used = set(cnf.used_vars())
    free_unused = cnf.n - len(used) - sum(1 for k in (fixed or {}) if cnf.index(k) not in used)
    assumptions = [cnf.index(k) if v else -cnf.index(k) for k, v in (fixed or {}).items()]
    count = 0
    with Minisat22(bootstrap_with=[list(c) for c in cnf.clauses]) as s:
        while s.solve(assumptions=assumptions):
            model = [l for l in s.get_model() if abs(l) in used]
            count += 1
            if limit is not None and count * 2**free_unused >= limit:
                return limit
            s.add_clause([-l for l in model])
    return count * 2**free_unused


def all_solutions(cnf: CNF, limit: int = 100_000) -> list[Assignment]:
    """Every satisfying assignment over the used variables (raises if more than `limit`)."""
    used = cnf.used_vars()
    out = []
    with Minisat22(bootstrap_with=[list(c) for c in cnf.clauses]) as s:
        while s.solve():
            model = [l for l in s.get_model() if abs(l) in set(used)]
            out.append({cnf.name(l): l > 0 for l in model})
            if len(out) > limit:
                raise RuntimeError(f"more than {limit} solutions")
            s.add_clause([-l for l in model])
    return out


# --- validator path: plain DPLL and brute force ----------------------------------------


def dpll_solve(cnf: CNF, fixed: Assignment | None = None) -> Assignment | None:
    """Independent recursive DPLL (unit propagation, first-unassigned branching)."""
    clauses = [list(c) for c in cnf.clauses]
    start = {cnf.index(k): v for k, v in (fixed or {}).items()}

    def propagate(values: dict[int, bool]) -> dict[int, bool] | None:
        values = dict(values)
        changed = True
        while changed:
            changed = False
            for c in clauses:
                vals = [lit_value(l, values) for l in c]
                if True in vals:
                    continue
                open_lits = [l for l, v in zip(c, vals) if v is None]
                if not open_lits:
                    return None
                if len(open_lits) == 1:
                    values[abs(open_lits[0])] = open_lits[0] > 0
                    changed = True
        return values

    def rec(values: dict[int, bool]) -> dict[int, bool] | None:
        values = propagate(values)
        if values is None:
            return None
        for v in range(1, cnf.n + 1):
            if v not in values:
                for val in (True, False):
                    res = rec({**values, v: val})
                    if res is not None:
                        return res
                return None
        return values

    res = rec(start)
    return None if res is None else to_assignment(cnf, res)


def brute_force_count(cnf: CNF, fixed: Assignment | None = None) -> int:
    """Count satisfying assignments over all declared variables by enumeration (n <= 24)."""
    n = cnf.n
    if n > 24:
        raise ValueError("brute force limited to n <= 24")
    # vectorised: rows = assignments
    idx = np.arange(2**n, dtype=np.int64)
    bits = ((idx[:, None] >> np.arange(n)) & 1).astype(bool)  # bits[:, i] = value of var i+1
    ok = np.ones(2**n, dtype=bool)
    for k, v in (fixed or {}).items():
        ok &= bits[:, cnf.index(k) - 1] == v
    for c in cnf.clauses:
        sat = np.zeros(2**n, dtype=bool)
        for lit in c:
            col = bits[:, abs(lit) - 1]
            sat |= col if lit > 0 else ~col
        ok &= sat
    return int(ok.sum())


# --- random instances -----------------------------------------------------------------


def random_ksat(n: int, m: int, k: int, rng: np.random.Generator, var_names: tuple[str, ...]) -> CNF:
    """Uniform random k-SAT: k distinct variables per clause, signs Bernoulli(1/2)."""
    assert len(var_names) == n
    clauses = []
    for _ in range(m):
        vs = rng.choice(n, size=k, replace=False) + 1
        signs = rng.integers(0, 2, size=k) * 2 - 1
        clauses.append(tuple(int(v * s) for v, s in zip(vs, signs)))
    return CNF(var_names, tuple(clauses))


# --- isomorphism (leakage checks) -----------------------------------------------------


def incidence_graph(cnf: CNF) -> nx.Graph:
    """Signed clause-variable incidence graph (literal nodes joined to their variable)."""
    g = nx.Graph()
    for v in cnf.used_vars():
        g.add_node(("v", v), kind="var")
        g.add_node(("p", v), kind="lit")
        g.add_node(("q", v), kind="lit")
        g.add_edge(("v", v), ("p", v))
        g.add_edge(("v", v), ("q", v))
    for i, c in enumerate(cnf.clauses):
        g.add_node(("c", i), kind="clause")
        for l in c:
            g.add_edge(("c", i), ("p", abs(l)) if l > 0 else ("q", abs(l)))
    return g


def iso_invariant(cnf: CNF) -> str:
    """Weisfeiler-Lehman hash, invariant to renaming, polarity flips and clause order."""
    return nx.weisfeiler_lehman_graph_hash(incidence_graph(cnf), node_attr="kind", iterations=4)


def isomorphic(a: CNF, b: CNF) -> bool:
    if a.m != b.m or len(a.used_vars()) != len(b.used_vars()):
        return False
    nm = nx.algorithms.isomorphism.categorical_node_match("kind", None)
    return nx.is_isomorphic(incidence_graph(a), incidence_graph(b), node_match=nm)


def all_assignments(names: list[str]) -> Iterable[Assignment]:
    for bits in itertools.product((False, True), repeat=len(names)):
        yield dict(zip(names, bits))
