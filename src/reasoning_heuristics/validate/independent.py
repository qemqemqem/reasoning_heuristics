"""The validator's own reading of an item: the stated problem, exact solvers and the
ground-truth readouts, sharing no code with the generator path.

The generator path (`validate.truth.truth`, the generators and the zoo) reads an instance through
`heuristics.tasks.load_task`, rewrites it with the zoo's `effective_graph` / `effective_cnf` /
`effective_premises`, and solves it with MiniSat 2.2, DSATUR backtracking, truth tables, dynamic
programming and Held-Karp. A validator that reused any of those would repeat its bugs, so this
module:

- parses the raw `instance` JSON itself and applies its own reading of the stated rule (the
  complement graph, inverted or marked clauses, the NOR reading of "either ... or");
- decides colourability, satisfiability, consistency and entailment with CaDiCaL 1.5.3
  (`SAT_BACKEND`, python-sat's other backend), entailment through its own Tseitin encoding;
- counts models, partitions and completions, and enumerates knapsack subsets, with its own
  enumerators; renders literals and letters options itself.

It imports nothing from `heuristics/`, `generators/` or the problem modules, except the TSP
branch and bound, which `problems/tsp` already keeps apart from the generator's Held-Karp.

Semantics follow the prompts. A conclusion "follows" when it "must be true whenever all the
statements are true", so inconsistent premises entail everything (vacuously); `check_item` flags
such items separately, since no design intends them. An MC item must have one strongest entailed
option: the validator reports a tie instead of breaking it the way the generator does.
"""

from __future__ import annotations

import itertools
from typing import Any

from pysat.solvers import Solver

from reasoning_heuristics.problems.tsp.tsp import TSP, solve_bnb

SAT_BACKEND = "cadical153"

# Ground-truth keys, beyond the standard ones, that `recheck_readouts` recomputes.
READOUTS: dict[str, tuple[str, ...]] = {
    "coloring_task": ("n_optimal_partitions", "n_colourings_up_to_renaming", "n_partitions_stated",
                      "n_partitions_textbook", "n_completions", "example", "answer"),
    "sat_task": ("n_solutions", "n_completions", "n_solutions_stated", "n_solutions_textbook"),
    "entailment_task": ("countermodels", "entailed_under_or", "entailed_under_nor"),
    "knapsack_task": ("optimal_set", "optimal_subsets", "packing_optimal_subsets"),
}


def _solve(clauses: list[list[int]], assumptions: list[int] = ()) -> bool:
    if any(not c for c in clauses):
        return False
    with Solver(name=SAT_BACKEND, bootstrap_with=clauses) as s:
        return bool(s.solve(assumptions=list(assumptions)))


# --- colouring ----------------------------------------------------------------------------------


def _graph(inst: dict[str, Any], stated: bool = True) -> tuple[list[str], set[frozenset[str]]]:
    """Vertices in listing order and the edges of the stated problem ("only friends may share a
    room" lists friendships: the conflicts are the complement)."""
    vertices = list(inst["graph"]["vertices"])
    names = set(vertices)
    if len(names) != len(vertices):
        raise ValueError("duplicate vertex")
    listed: set[frozenset[str]] = set()
    for u, v in inst["graph"]["edges"]:
        if u == v or u not in names or v not in names:
            raise ValueError(f"bad edge {u}-{v}")
        listed.add(frozenset((u, v)))
    if stated and inst.get("complement"):
        return vertices, {frozenset(p) for p in itertools.combinations(vertices, 2)} - listed
    return vertices, listed


def _neighbours(vertices: list[str], edges: set[frozenset[str]]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {v: set() for v in vertices}
    for e in edges:
        u, v = tuple(e)
        out[u].add(v)
        out[v].add(u)
    return out


def _fixed_colours(inst: dict[str, Any], vertices: list[str], k: int | None) -> dict[str, int]:
    fixed: dict[str, int] = {}
    for v, c in inst.get("fixed") or ():
        if v not in set(vertices):
            raise ValueError(f"fixed vertex {v!r} is not in the graph")
        if k is None:
            raise ValueError("fixed colours on a fewest-colours task")
        if isinstance(c, bool) or not isinstance(c, int) or not 1 <= c <= k:
            raise ValueError(f"fixed colour {c!r} of {v} is outside 1..{k}")
        if fixed.setdefault(v, c) != c:
            raise ValueError(f"vertex {v} is fixed to two colours")
    return fixed


def _colourable(vertices: list[str], edges: set[frozenset[str]], k: int, fixed: dict[str, int]) -> bool:
    if k < 1:
        return not vertices
    idx = {v: i for i, v in enumerate(vertices)}

    def x(v: str, c: int) -> int:  # c in 1..k
        return idx[v] * k + c

    clauses = [[x(v, c) for c in range(1, k + 1)] for v in vertices]
    for e in edges:
        u, v = tuple(e)
        clauses += [[-x(u, c), -x(v, c)] for c in range(1, k + 1)]
    clauses += [[x(v, c)] for v, c in fixed.items()]
    return _solve(clauses)


def _chromatic(vertices: list[str], edges: set[frozenset[str]]) -> int:
    if not vertices:
        return 0
    k = 1
    while not _colourable(vertices, edges, k, {}):
        k += 1
    return k


def _count_partitions(vertices: list[str], edges: set[frozenset[str]], k: int) -> int:
    """Partitions of the vertices into at most k independent sets (colourings up to renaming)."""
    nb = _neighbours(vertices, edges)
    order = sorted(vertices, key=lambda v: -len(nb[v]))
    bit = {v: 1 << i for i, v in enumerate(order)}
    mask = [sum(bit[u] for u in nb[v]) for v in order]
    classes: list[int] = []

    def rec(i: int) -> int:
        if i == len(order):
            return 1
        total = 0
        for j, cls in enumerate(classes):
            if not cls & mask[i]:
                classes[j] = cls | 1 << i
                total += rec(i + 1)
                classes[j] = cls
        if len(classes) < k:  # open a class: classes are ordered by first member, so each partition is counted once
            classes.append(1 << i)
            total += rec(i + 1)
            classes.pop()
        return total

    return rec(0)


def _count_completions(vertices: list[str], edges: set[frozenset[str]], k: int, fixed: dict[str, int]) -> int:
    """Proper colourings with colours 1..k that extend `fixed` (labelled colourings)."""
    nb = _neighbours(vertices, edges)
    if any(fixed.get(u) == c for v, c in fixed.items() for u in nb[v]):
        return 0
    free = sorted((v for v in vertices if v not in fixed), key=lambda v: -len(nb[v]))
    col = dict(fixed)

    def rec(i: int) -> int:
        if i == len(free):
            return 1
        v = free[i]
        used = {col[u] for u in nb[v] if u in col}
        total = 0
        for c in range(1, k + 1):
            if c not in used:
                col[v] = c
                total += rec(i + 1)
                del col[v]
        return total

    return rec(0)


def _first_fit(vertices: list[str], edges: set[frozenset[str]]) -> dict[str, int]:
    """The smallest free colour for each vertex in turn, in listing order."""
    nb = _neighbours(vertices, edges)
    col: dict[str, int] = {}
    for v in vertices:
        used = {col[u] for u in nb[v] if u in col}
        col[v] = next(c for c in itertools.count(1) if c not in used)
    return col


# --- CNF ----------------------------------------------------------------------------------------


def _cnf(inst: dict[str, Any]) -> tuple[int, list[list[int]], list[list[int]], list[int]]:
    """(number of variables, clauses as written, clauses of the stated rule, fixed literals).

    The inverted rule ("a clause holds when at least one condition is false") flips every literal;
    marked clauses (A/H E5 P) flip only those."""
    names = list(inst["cnf"]["var_names"])
    n = len(names)
    if len(set(names)) != n:
        raise ValueError("duplicate variable names")
    written = [list(c) for c in inst["cnf"]["clauses"]]
    for c in written:
        if any(isinstance(l, bool) or not isinstance(l, int) or l == 0 or abs(l) > n for l in c):
            raise ValueError(f"bad clause {c} for {n} variables")
    marked = set(inst.get("inverted_clauses") or ())
    if inst.get("inverted") and marked:
        raise ValueError("both the inverted rule and marked clauses")
    if any(not 0 <= i < len(written) for i in marked):
        raise ValueError(f"marked clause outside 0..{len(written) - 1}")
    stated = [[-l for l in c] if inst.get("inverted") or i in marked else c for i, c in enumerate(written)]
    pos = {name: i + 1 for i, name in enumerate(names)}
    fixed = []
    for name, value in inst.get("fixed") or ():
        if name not in pos:
            raise ValueError(f"fixed variable {name!r} is not declared")
        fixed.append(pos[name] if value else -pos[name])
    return n, written, stated, fixed


def _count_models(n: int, clauses: list[list[int]], fixed: list[int] = ()) -> int:
    """Assignments to variables 1..n that satisfy every clause and the fixed literals (DPLL with
    unit propagation; a branch whose clauses are all satisfied contributes 2^free)."""

    def assign(cls: list[frozenset[int]], lit: int) -> list[frozenset[int]] | None:
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

    cls: list[frozenset[int]] | None = [frozenset(c) for c in clauses]
    if any(not c for c in cls):
        return 0
    values: dict[int, bool] = {}
    for lit in fixed:
        if values.setdefault(abs(lit), lit > 0) != (lit > 0):
            return 0
        cls = assign(cls, lit)
        if cls is None:
            return 0

    def rec(cls: list[frozenset[int]], assigned: int) -> int:
        while True:
            unit = next((c for c in cls if len(c) == 1), None)
            if unit is None:
                break
            (lit,) = unit
            cls = assign(cls, lit)
            if cls is None:
                return 0
            assigned += 1
        if not cls:
            return 2 ** (n - assigned)
        v = abs(next(iter(min(cls, key=len))))
        total = 0
        for lit in (v, -v):
            sub = assign(cls, lit)
            if sub is not None:
                total += rec(sub, assigned + 1)
        return total

    return rec(cls, len(values))


# --- entailment ---------------------------------------------------------------------------------


def _formula(data: Any) -> tuple:
    op = data[0]
    if op == "lit":
        return ("lit", str(data[1]), bool(data[2]))
    if op in ("and", "or", "nand", "nor"):
        return (op, tuple(_formula(g) for g in data[1]))
    if op in ("if", "iff"):
        return (op, _formula(data[1]), _formula(data[2]))
    raise ValueError(f"unknown operator {op!r}")


def _premises(inst: dict[str, Any], reading: str | None = None) -> list[tuple]:
    """Premises as the stated rule reads them: under the NOR reading every "either ... or"
    premise (a top-level disjunction) means "neither ... nor"."""
    prem = [_formula(p) for p in inst["premises"]]
    reading = reading or inst.get("reading", "standard")
    if reading == "nor":
        return [("nor", p[1]) if p[0] == "or" else p for p in prem]
    if reading != "standard":
        raise ValueError(f"unknown reading {reading!r}")
    return prem


def _atoms(formulas: list[tuple]) -> list[str]:
    """Atoms in order of first mention."""
    out: dict[str, None] = {}

    def walk(f: tuple) -> None:
        if f[0] == "lit":
            out.setdefault(f[1], None)
        elif f[0] in ("if", "iff"):
            walk(f[1])
            walk(f[2])
        else:
            for g in f[1]:
                walk(g)

    for f in formulas:
        walk(f)
    return list(out)


def render_literal(atom: str, positive: bool) -> str:
    """How the prompts write a literal ("the door is not open", "Ann is tall", "not p")."""
    if "@" in atom:
        name, phrase = atom.split("@", 1)
        return f"{name} is {'' if positive else 'not '}{phrase}"
    if ":" in atom:
        subject, predicate = atom.split(":", 1)
        return f"the {subject} is {'' if positive else 'not '}{predicate}"
    return atom if positive else f"not {atom}"


def _letter(index: int) -> str:
    return chr(ord("A") + index)


class _Tseitin:
    """Definitional CNF: every subformula gets a literal t with t <-> subformula, so a formula
    holds under an assumption on its literal; the definitions alone constrain no atom."""

    def __init__(self) -> None:
        self.atom: dict[str, int] = {}
        self.top = 0
        self.clauses: list[list[int]] = []
        self._memo: dict[tuple, int] = {}

    def _fresh(self) -> int:
        self.top += 1
        return self.top

    def lit(self, f: tuple) -> int:
        if f in self._memo:
            return self._memo[f]
        op = f[0]
        if op == "lit":
            if f[1] not in self.atom:
                self.atom[f[1]] = self._fresh()
            out = self.atom[f[1]] if f[2] else -self.atom[f[1]]
        elif op in ("and", "nand", "or", "nor"):
            kids = [self.lit(g) for g in f[1]]
            t = self._fresh()
            if op in ("and", "nand"):
                self.clauses += [[-t, k] for k in kids] + [[t] + [-k for k in kids]]
            else:
                self.clauses += [[t, -k] for k in kids] + [[-t] + kids]
            out = t if op in ("and", "or") else -t
        elif op == "if":
            a, b = self.lit(f[1]), self.lit(f[2])
            out = self._fresh()
            self.clauses += [[-out, -a, b], [out, a], [out, -b]]
        elif op == "iff":
            a, b = self.lit(f[1]), self.lit(f[2])
            out = self._fresh()
            self.clauses += [[-out, -a, b], [-out, a, -b], [out, a, b], [out, -a, -b]]
        else:
            raise ValueError(f"unknown operator {op!r}")
        self._memo[f] = out
        return out


def _entailment(inst: dict[str, Any], reading: str | None = None) -> dict[str, Any]:
    """Consistency, the standard answer, and the entailed literals of one premise reading."""
    prem = _premises(inst, reading)
    probe = _formula(inst["probe"]) if inst.get("probe") is not None else None
    options = [_formula(o) for o in inst.get("options") or ()]
    enc = _Tseitin()
    p = [enc.lit(f) for f in prem]
    q = enc.lit(probe) if probe is not None else None
    o = [enc.lit(f) for f in options]
    written_atoms = _atoms([_formula(f) for f in inst["premises"]])
    for a in written_atoms:
        enc.lit(("lit", a, True))
    out: dict[str, Any] = {}
    with Solver(name=SAT_BACKEND, bootstrap_with=enc.clauses) as s:

        def holds(*lits: int) -> bool:
            return bool(s.solve(assumptions=list(lits)))

        def follows(lit: int) -> bool:  # true whenever all the premises are true
            return not holds(*p, -lit)

        out["consistent"] = holds(*p)
        if q is not None:
            out["follows"] = follows(q)
        out["entailed"] = sorted(render_literal(a, pol) for a in written_atoms for pol in (True, False)
                                 if follows(enc.atom[a] if pol else -enc.atom[a]))
        if options:
            entailed = [i for i in range(len(options)) if follows(o[i])]
            strongest = [i for i in entailed if all(not holds(o[i], -o[j]) for j in entailed)]
            out["mc"] = (entailed, strongest)
    return out


def _countermodels(inst: dict[str, Any]) -> int:
    """Assignments to the atoms of the premises and probe under which every premise holds and
    the probe fails."""
    prem = _premises(inst)
    probe = _formula(inst["probe"])
    enc = _Tseitin()
    hard = [[enc.lit(f)] for f in prem] + [[-enc.lit(probe)]]
    counted = [enc.atom[a] for a in _atoms(prem + [probe])]
    if not counted:
        return int(_solve(enc.clauses + hard))
    n = 0
    with Solver(name=SAT_BACKEND, bootstrap_with=enc.clauses + hard) as s:
        while s.solve():
            model = {abs(l): l > 0 for l in s.get_model()}
            s.add_clause([-v if model.get(v, False) else v for v in counted])
            n += 1
    return n


def _entailment_answer(inst: dict[str, Any]) -> dict[str, Any]:
    fmt = inst["fmt"]
    ent = _entailment(inst)
    if fmt == "YN":
        return {"answer": "YES" if ent["follows"] else "NO", "follows": ent["follows"]}
    if fmt == "MC":
        entailed, strongest = ent["mc"]
        if not entailed:
            return {"answer": _letter(len(inst["options"]))}  # "None of these"
        if len(strongest) != 1:
            raise ValueError(f"MC item has no single strongest entailed option (entailed: "
                             f"{[_letter(i) for i in entailed]}, strongest: {[_letter(i) for i in strongest]})")
        return {"answer": _letter(strongest[0])}
    if fmt == "OPEN":
        return {"answer": ent["entailed"] or "NOTHING"}
    raise ValueError(f"unknown format {fmt!r}")


def premises_consistent(instance: dict[str, Any]) -> bool:
    """Whether the stated premises of an entailment instance can all be true at once."""
    return _entailment(instance)["consistent"]


# --- knapsack and TSP ---------------------------------------------------------------------------


def _knapsack(inst: dict[str, Any]) -> tuple[list[str], list[int], list[int], int]:
    k = inst["knapsack"]
    names, values, weights = list(k["names"]), list(k["values"]), list(k["weights"])
    if not len(names) == len(values) == len(weights) or len(set(names)) != len(names):
        raise ValueError("malformed knapsack")
    return names, values, weights, k["capacity"]


def _optimal_subsets(inst: dict[str, Any], covering: bool) -> tuple[int, list[list[str]]]:
    """The optimum and every optimal subset (each sorted), by enumerating all subsets. Packing:
    total weight <= capacity, maximise value; covering: weight >= capacity, minimise value."""
    names, values, weights, cap = _knapsack(inst)
    n = len(names)
    if n > 22:
        raise ValueError("subset enumeration limited to 22 items")
    w, v = [0] * (1 << n), [0] * (1 << n)
    for mask in range(1, 1 << n):
        low = mask & -mask
        i = low.bit_length() - 1
        w[mask], v[mask] = w[mask ^ low] + weights[i], v[mask ^ low] + values[i]
    feasible = [m for m in range(1 << n) if (w[m] >= cap if covering else w[m] <= cap)]
    if not feasible:
        raise ValueError("no feasible subset")
    best = (min if covering else max)(v[m] for m in feasible)
    return best, sorted(sorted(names[i] for i in range(n) if m >> i & 1) for m in feasible if v[m] == best)


def _tsp(inst: dict[str, Any]) -> TSP:
    t = inst["tsp"]
    return TSP(tuple(t["names"]), tuple(tuple(c) for c in t["coords"]))


# --- the standard keys and the readouts ---------------------------------------------------------


def independent_truth(instance: dict[str, Any]) -> dict[str, Any]:
    """The standard ground-truth keys of an item's `instance` JSON (see `validate.truth`)."""
    kind = instance["kind"]
    if kind == "coloring_task":
        vertices, edges = _graph(instance)
        k = instance["k"]
        fixed = _fixed_colours(instance, vertices, k)
        if k is None:
            return {"chromatic_number": _chromatic(vertices, edges)}
        return {"k": k, "colourable": _colourable(vertices, edges, k, fixed)}
    if kind == "sat_task":
        _, _, stated, fixed = _cnf(instance)
        return {"satisfiable": _solve(stated, fixed)}
    if kind == "entailment_task":
        return _entailment_answer(instance)
    if kind == "knapsack_task":
        return {"optimum": _optimal_subsets(instance, instance["covering"])[0]}
    if kind == "tsp_task":
        return {"optimal_length": solve_bnb(_tsp(instance))}
    raise ValueError(f"unknown instance kind {kind!r}")


def _example_problem(example: Any, vertices: list[str], edges: set[frozenset[str]], k: int, fixed: dict[str, int]) -> str | None:
    if example is None:
        return "null, but the graph is k-colourable" if _colourable(vertices, edges, k, fixed) else None
    if not isinstance(example, dict) or set(example) != set(vertices):
        return "does not colour exactly the graph's vertices"
    if any(isinstance(c, bool) or not isinstance(c, int) or not 1 <= c <= k for c in example.values()):
        return f"uses a colour outside 1..{k}"
    if any(example[v] != c for v, c in fixed.items()):
        return "changes a fixed colour"
    bad = sorted(sorted(e) for e in edges if len({example[u] for u in e}) == 1)
    return f"is not proper: {bad[:3]}" if bad else None


def recheck_readouts(instance: dict[str, Any], ground_truth: Any, params: dict[str, Any] | None = None) -> list[str]:
    """Recompute every readout in `READOUTS` that the ground truth carries (the solution and
    completion counts, optimal-partition counts and optimal sets that feed the likelihood tables,
    the C E3 asked answer, ...). Returns one message per mismatch."""
    kind = instance["kind"]
    keys = [k for k in READOUTS.get(kind, ()) if isinstance(ground_truth, dict) and k in ground_truth]
    out: list[str] = []

    def compare(key: str, got: Any) -> None:
        if got != ground_truth[key]:
            out.append(f"{key}: stored {ground_truth[key]!r} != independent {got!r}")

    if kind == "coloring_task" and keys:
        vertices, edges = _graph(instance)
        k = instance["k"]
        fixed = _fixed_colours(instance, vertices, k)
        for key in keys:
            if key == "n_optimal_partitions":
                compare(key, _count_partitions(vertices, edges, _chromatic(vertices, edges)))
            elif k is None and key != "answer":
                out.append(f"{key}: needs a colour count k")
            elif key in ("n_colourings_up_to_renaming", "n_partitions_stated"):
                compare(key, _count_partitions(vertices, edges, k))
            elif key == "n_partitions_textbook":
                compare(key, _count_partitions(*_graph(instance, stated=False), k))
            elif key == "n_completions":
                compare(key, _count_completions(vertices, edges, k, fixed))
            elif key == "example":
                problem = _example_problem(ground_truth[key], vertices, edges, k, fixed)
                if problem:
                    out.append(f"example: {problem}")
            elif key == "answer":  # C E3: the colour first fit gives the target, in listing order
                target = instance.get("target", (params or {}).get("target"))
                if target not in set(vertices):
                    out.append(f"answer: no target vertex recorded (got {target!r})")
                else:
                    compare(key, _first_fit(vertices, edges)[target])
    elif kind == "sat_task" and keys:
        n, written, stated, fixed = _cnf(instance)
        for key in keys:
            if key == "n_completions":
                compare(key, _count_models(n, stated, fixed))
            elif key == "n_solutions_textbook":
                compare(key, _count_models(n, written))
            else:  # n_solutions, n_solutions_stated: the stated formula, no fixed values
                compare(key, _count_models(n, stated))
    elif kind == "entailment_task" and keys:
        for key in keys:
            if key == "countermodels":
                compare(key, _countermodels(instance))
            else:
                compare(key, _entailment(instance, reading="standard" if key == "entailed_under_or" else "nor")["entailed"])
    elif kind == "knapsack_task" and keys:
        for key in keys:
            covering = instance["covering"] and key != "packing_optimal_subsets"
            _, subsets = _optimal_subsets(instance, covering)
            stored = ground_truth[key]
            if key == "optimal_set":
                if len(subsets) != 1:
                    out.append(f"optimal_set: the optimum is reached by {len(subsets)} subsets, not one")
                elif sorted(stored) != subsets[0]:
                    out.append(f"optimal_set: stored {stored!r} != independent {subsets[0]!r}")
            elif sorted(sorted(s) for s in stored) != subsets:
                out.append(f"{key}: stored {stored!r} != independent {subsets!r}")
    return out


# --- the stated problem in canonical form (leakage) ---------------------------------------------


def _canonical(f: tuple) -> tuple:
    """Order-free form: juncts and the sides of a biconditional sorted, conditionals kept directed."""
    op = f[0]
    if op == "lit":
        return f
    if op in ("if", "iff"):
        a, b = _canonical(f[1]), _canonical(f[2])
        return (op, a, b) if op == "if" else (op, *sorted((a, b), key=repr))
    return (op, tuple(sorted({_canonical(g) for g in f[1]}, key=repr)))


def effective_problem(instance: dict[str, Any]) -> tuple[str, Any]:
    """(kind, hashable canonical form) of the stated problem, for the dev-vs-test leakage check.

    graph: the vertex set and the stated conflict edges (complement applied); cnf: the stated
    clauses as literal sets, duplicates and tautologies dropped; formula: the set of stated
    premises (canonical, so duplicates drop) and the probe; knapsack: the packing capacity and the
    multiset of (weight, value), a covering instance mapped to its complement packing (capacity
    W - L); tsp: the distance matrix."""
    kind = instance["kind"]
    if kind == "coloring_task":
        vertices, edges = _graph(instance)
        return "graph", (tuple(sorted(vertices)), frozenset(edges))
    if kind == "sat_task":
        _, _, stated, _ = _cnf(instance)
        clauses = {frozenset(c) for c in stated}
        return "cnf", frozenset(c for c in clauses if not any(-l in c for l in c))
    if kind == "entailment_task":
        probe = _canonical(_formula(instance["probe"])) if instance.get("probe") is not None else None
        return "formula", (frozenset(_canonical(p) for p in _premises(instance)), probe)
    if kind == "knapsack_task":
        _, values, weights, cap = _knapsack(instance)
        if instance["covering"]:
            cap = sum(weights) - cap  # min value with weight >= L  <=>  max value left out with weight <= W - L
        return "knapsack", (cap, tuple(sorted(zip(weights, values))))
    if kind == "tsp_task":
        return "tsp", tuple(tuple(row) for row in _tsp(instance).dist)
    raise ValueError(f"unknown instance kind {kind!r}")
