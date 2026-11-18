"""What each member predicts on an item, as a distribution over the item's answer space.

Built from the item's `predictions` and `instance` only. The engine computes its own
likelihoods (`likelihood`, with a fitted slip rate) and never reads the items' `disconfirms`
tables or outcome classes, which are a uniform-slip preview with ε fixed at 0.1
(docs/GENERATORS.md).

Every `predictions[label]` record becomes a `Pred` of one of five kinds:

- `det`: one answer (its channel key). Slips with the fitted slip model.
- `set`: uniform over a solution set S, rebuilt **by validity** from the instance (below).
  Slips like a member that first draws a solution from S.
- `uniform`: `RANDOM (H)` on colourings: uniform over k^n colourings (`Space.log_uniform`).
- `dist`: a distributional member (C3, H, nuisance): its stored distribution, taken as complete
  (it is a noise model already, so no slips are added). Stored entries map to answers; `_other`
  (a Monte Carlo tail) to q; `_exact` to EXACT's solution set (or answer); a decision placeholder
  on a witness channel (RANDOM's "SAT") to a uniformly random structured answer.
- `na`: no prediction on this channel (e.g. EXACT's colour number on C E3's I arm, which colour
  names do not define). The mixture renormalises over the members available on each item.

**Set-valued members, by validity.** On witness channels (colouring, SAT, knapsack answers):

| Member | S |
|---|---|
| `EXACT` (registry name) | every valid solution of the stated instance: proper colourings of the effective graph with <= k classes (k-colour tasks, consistent with any fixed colours up to renaming) or exactly chi classes (fewest-colour tasks); satisfying assignments of the effective CNF that keep the fixed values; optimal item sets of the effective knapsack (packing or covering) |
| `TT` with inner EXACT (A/H E5's `A3 TT[exact]`) | the same, under the textbook rule (the un-inverted graph, CNF or packing problem) |

When S is empty the member answers the stored impossibility token (UNSAT, IMPOSSIBLE) as `det`.
On C E3's target-bit channel EXACT is the projection of S onto the bit (a `dist` over
same/different), when S can be enumerated (up to `MAX_SOLUTIONS`); otherwise `na`.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np

from reasoning_heuristics.identify.spaces import BitSpace, FiniteSpace, PartitionSpace, Space, channel_of

STRUCTURED = (BitSpace, PartitionSpace)
MAX_SOLUTIONS = 2_000_000


@dataclass
class SolutionSet:
    rule: str
    ident: str
    enum: Callable[[], list[str]]
    _keys: list[str] | None = field(default=None, repr=False)
    _set: set | None = field(default=None, repr=False)
    _array: Any = field(default=None, repr=False)

    def keys(self) -> list[str]:
        if self._keys is None:
            self._keys = sorted(set(self.enum()))
            self._set = set(self._keys)
        return self._keys

    @property
    def size(self) -> int:
        return len(self.keys())

    def contains(self, key: str) -> bool:
        self.keys()
        return key in self._set

    def array(self, space: Space) -> np.ndarray:
        if self._array is None:
            self._array = space.set_array(self.keys())
        return self._array


@dataclass
class Pred:
    kind: str  # det | set | uniform | dist | na
    key: str | None = None
    sol: SolutionSet | None = None
    dist: dict[str, float] | None = None  # keys: answers, "_other" (q), "_uniform", "_exact"
    exact: "Pred | None" = None  # EXACT's prediction, when dist uses "_exact"
    note: str = ""

    @property
    def available(self) -> bool:
        return self.kind != "na"

    @property
    def slips(self) -> bool:
        """Whether the likelihood adds slips to this member."""
        return self.kind in ("det", "set")


def _ident(*parts: Any) -> str:
    return hashlib.sha1(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:16]


# --- validity-based solution sets ---------------------------------------------------------------


def _partitions(g: Any, kmax: int, keep: Callable[[list[int]], bool]) -> list[str]:
    from reasoning_heuristics.heuristics.answers import colouring_key
    from reasoning_heuristics.problems.coloring import graph as G

    masks = G.enumerate_partitions(g, kmax, MAX_SOLUTIONS)
    if masks is None:
        raise OverflowError(f"more than {MAX_SOLUTIONS} colourings")
    return [colouring_key(G.masks_to_colouring(g, m)) for m in masks if keep(m)]


def _fixed_ok(g: Any, fixed: dict[str, int]) -> Callable[[list[int]], bool]:
    """Class masks consistent with the fixed colours up to renaming (an injective class -> colour map)."""
    pos = {v: i for i, v in enumerate(g.vertices)}

    def ok(masks: list[int]) -> bool:
        colour_of_class: dict[int, int] = {}
        for v, c in fixed.items():
            cls = next(j for j, m in enumerate(masks) if m >> pos[v] & 1)
            if colour_of_class.setdefault(cls, c) != c:
                return False
        return len(set(colour_of_class.values())) == len(colour_of_class)

    return ok


def colouring_solutions(g: Any, k: int | None, fixed: dict[str, int], chi: int | None = None) -> tuple[str, Callable[[], list[str]]]:
    from reasoning_heuristics.problems.coloring import graph as G

    if k is None:
        def enum() -> list[str]:
            c = chi if chi is not None else G.chromatic_number(g)
            return _partitions(g, c, lambda m: len(m) == c)

        return "optimal colourings (exactly chi classes)", enum
    keep = _fixed_ok(g, fixed) if fixed else (lambda m: True)
    return f"proper colourings with <= {k} classes" + (" consistent with the fixed colours" if fixed else ""), \
        lambda: _partitions(g, k, keep)


def sat_solutions(cnf: Any, names: list[str], fixed: dict[str, bool]) -> Callable[[], list[str]]:
    from reasoning_heuristics.heuristics.answers import assignment_key
    from reasoning_heuristics.problems.sat import cnf as S

    def enum() -> list[str]:
        used = {cnf.name(v) for v in cnf.used_vars()}
        free = [v for v in names if v not in used]
        out = []
        for sol in S.all_solutions(cnf, limit=MAX_SOLUTIONS):
            if any(k in sol and sol[k] != v for k, v in fixed.items()):
                continue
            for bits in itertools.product((False, True), repeat=len(free)):
                a = {**sol, **dict(zip(free, bits))}
                if all(a[k] == v for k, v in fixed.items()):
                    out.append(assignment_key(a))
        return out

    return enum


def knapsack_solutions(names: list[str], values: list[int], weights: list[int], capacity: int, covering: bool) -> list[str]:
    n = len(names)
    if n > 22:
        raise OverflowError("knapsack too large for brute force")
    best, sols = None, []
    for mask in range(1 << n):
        w = sum(weights[i] for i in range(n) if mask >> i & 1)
        if (w < capacity) if covering else (w > capacity):
            continue
        v = sum(values[i] for i in range(n) if mask >> i & 1)
        better = best is None or (v < best if covering else v > best)
        if better:
            best, sols = v, [mask]
        elif v == best:
            sols.append(mask)
    return [",".join(sorted(names[i] for i in range(n) if m >> i & 1)) for m in sols]


def solution_set(item: dict[str, Any], textbook: bool) -> SolutionSet | None:
    """S for EXACT (stated rule) or TT[exact] (textbook rule); None if the instance has no solution."""
    from reasoning_heuristics.heuristics.coloring import effective_graph
    from reasoning_heuristics.heuristics.sat import effective_cnf
    from reasoning_heuristics.heuristics.tasks import load_task
    from reasoning_heuristics.problems.coloring import graph as G
    from reasoning_heuristics.problems.sat import cnf as S

    inst = item["instance"]
    task = load_task(inst)
    kind = inst["kind"]
    if kind == "coloring_task":
        g = task.graph if textbook else effective_graph(task)
        fixed = task.fixed_dict()
        if task.k is not None and not G.k_colour(g, task.k, fixed or None):
            return None
        chi = item["ground_truth"].get("chromatic_number") if (task.k is None and not textbook and not task.complement) else None
        rule, enum = colouring_solutions(g, task.k, fixed, chi)
        return SolutionSet(("textbook " if textbook else "") + rule, _ident("col", g.to_json(), task.k, sorted(fixed.items())), enum)
    if kind == "sat_task":
        cnf = task.cnf if textbook else effective_cnf(task)
        fixed = task.fixed_dict()
        if S.solve(cnf, fixed or None) is None:
            return None
        names = list(task.declared) if task.declared else list(cnf.var_names)
        return SolutionSet(("textbook " if textbook else "") + "satisfying assignments" + (" keeping the fixed values" if fixed else ""),
                           _ident("sat", cnf.to_json(), sorted(fixed.items()), names), sat_solutions(cnf, names, fixed))
    if kind == "knapsack_task":
        k = inst["knapsack"]
        covering = bool(task.covering) and not textbook
        sols = knapsack_solutions(k["names"], k["values"], k["weights"], k["capacity"], covering)
        if not sols:
            return None
        return SolutionSet(("covering" if covering else "packing") + " optima",
                           _ident("knap", k, covering), lambda: list(sols))
    raise NotImplementedError(kind)


# --- predictions -----------------------------------------------------------------------------------


def _set_valued_kind(rec: dict[str, Any]) -> str | None:
    """'stated' for EXACT, 'textbook' for TT with the exact inner solver, else None."""
    if rec["member"] == "EXACT":
        return "stated"
    if rec["member"] == "TT" and (rec.get("params") or {}).get("inner", "EXACT") == "EXACT":
        return "textbook"
    return None


def log_count_colourings(vertices: list[str], edges: list[tuple[str, str]], k: int,
                         evidence: dict[str, int] | None = None) -> float:
    """log of the number of proper colourings with colours 0..k-1 (vertices in `evidence` fixed),
    by variable elimination in min-degree order (exact; fast on the sparse gadget graphs)."""
    neq = 1.0 - np.eye(k)
    factors: list[tuple[tuple[str, ...], np.ndarray]] = [((u, v), neq) for u, v in edges]
    for v, c in (evidence or {}).items():
        e = np.zeros(k)
        e[c] = 1.0
        factors.append(((v,), e))
    adj: dict[str, set[str]] = {v: set() for v in vertices}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    remaining = set(vertices)
    log_total = 0.0
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    while remaining:
        x = min(remaining, key=lambda v: (len(adj[v] & remaining), v))
        involved = [f for f in factors if x in f[0]]
        factors = [f for f in factors if x not in f[0]]
        remaining.discard(x)
        if not involved:
            log_total += np.log(k)
            continue
        scope = sorted(set().union(*[set(f[0]) for f in involved]) - {x})
        if len(scope) + 1 > len(letters):
            raise OverflowError("elimination width too large")
        lab = {v: letters[i] for i, v in enumerate([x] + scope)}
        expr = ",".join("".join(lab[v] for v in f[0]) for f in involved) + "->" + "".join(lab[v] for v in scope)
        new = np.einsum(expr, *[f[1] for f in involved])
        s = float(new.max())
        if s <= 0:
            return -np.inf
        log_total += np.log(s)
        factors.append((tuple(scope), new / s))
        for a in scope:
            adj[a] |= set(scope) - {a}
    for _, arr in factors:
        val = float(arr)
        if val <= 0:
            return -np.inf
        log_total += np.log(val)
    return log_total


def _bit_projection(item: dict[str, Any], space: FiniteSpace) -> "Pred":
    """EXACT on C E3's target bit: the share of valid colourings in which target and reference agree
    (a proper colouring of a 3-chromatic gadget uses all 3 colours, so colour vectors and partitions
    give the same share)."""
    from reasoning_heuristics.heuristics.tasks import load_task

    task = load_task(item["instance"])
    g = task.graph
    if task.k is None:
        return Pred("na", note="fewest-colour task: colour numbers are not defined by EXACT")
    t, r = item["params"]["target"], item["params"]["reference_vertex"]
    edges = [tuple(e) for e in g.edges]
    total = log_count_colourings(list(g.vertices), edges, task.k)
    if total == -np.inf:
        return Pred("det", key="IMPOSSIBLE") if space.valid("IMPOSSIBLE") else Pred("na", note="no colouring")
    same = np.log(task.k) + log_count_colourings(list(g.vertices), edges, task.k, {t: 0, r: 0})
    p = float(np.exp(same - total)) if same > -np.inf else 0.0
    return Pred("dist", dist={k: v for k, v in (("same", p), ("different", 1 - p)) if v > 0},
                note="projection of the valid colourings onto the target bit")


def item_preds(item: dict[str, Any], space: Space) -> dict[str, Pred]:
    """Every member's prediction on this item (raises on a record it cannot interpret)."""
    out: dict[str, Pred] = {}
    exact_label = None
    sets: dict[str, SolutionSet | None] = {}
    witness = isinstance(space, STRUCTURED) and channel_of(item) == "answer" \
        and item["instance"]["kind"] in ("coloring_task", "sat_task", "knapsack_task")
    for label, rec in item["predictions"].items():
        ans, dist = rec["answer"], rec.get("distribution")
        sv = _set_valued_kind(rec)
        if rec["member"] == "EXACT":
            exact_label = label
        if isinstance(space, FiniteSpace):
            key = space.key(ans) if ans is not None else None
            if sv == "stated" and channel_of(item) == "target-bit":
                out[label] = _bit_projection(item, space)
            elif key is not None and space.valid(key):
                out[label] = Pred("det", key=key)
            elif dist:
                mapped: dict[str, float] = {}
                for k, v in dist.items():
                    kk = space.key(k)
                    if kk is None or not space.valid(kk):
                        raise ValueError(f"{item['item_id']} {label}: distribution key {k!r} is not on the channel")
                    mapped[kk] = mapped.get(kk, 0.0) + v
                out[label] = Pred("dist", dist=mapped)
            elif ans is not None and key is not None:
                raise ValueError(f"{item['item_id']} {label}: answer {ans!r} is not on the channel")
            else:
                out[label] = Pred("na", note="no prediction on this channel")
            continue
        if witness and sv is not None:
            if sv not in sets:
                sets[sv] = solution_set(item, textbook=(sv == "textbook"))
            sol = sets[sv]
            if sol is not None:
                out[label] = Pred("set", sol=sol)
                continue
        if rec["member"] == "RANDOM" and ans is None and not dist:
            out[label] = Pred("uniform")
            continue
        key = space.key(ans) if ans is not None else None
        if key is not None and space.valid(key):
            out[label] = Pred("det", key=key)
            continue
        if dist:
            mapped = {}
            for k, v in dist.items():
                if k in ("_other", "_exact") or space.valid(k):
                    kk = k
                elif k in ("SAT", "POSSIBLE") or k.startswith("CHI="):
                    kk = "_uniform"  # RANDOM's "a witness" outcome: a uniformly random structured answer
                else:
                    raise ValueError(f"{item['item_id']} {label}: distribution key {k[:40]!r} is not an answer")
                mapped[kk] = mapped.get(kk, 0.0) + v
            out[label] = Pred("dist", dist=mapped)
            continue
        if ans is not None:
            raise ValueError(f"{item['item_id']} {label}: answer {str(ans)[:40]!r} is not an answer on this channel")
        out[label] = Pred("na", note="no prediction")
    for p in out.values():
        if p.kind == "dist" and "_exact" in p.dist:
            if exact_label is None:
                raise ValueError(f"{item['item_id']}: a distribution uses _exact but the item has no EXACT member")
            p.exact = out[exact_label]
    return out


# --- normal forms (for tie detection) -----------------------------------------------------------


def normal_form(p: Pred, space: Space) -> tuple:
    """A hashable form of the predicted distribution: equal forms give equal likelihoods for every
    slip rate and shape. Returns ("na",) for an unavailable member."""
    if p.kind == "na":
        return ("na",)
    if p.kind == "det":
        return ("slips", (("key", p.key, 1.0),))
    if p.kind == "set":
        return ("slips", (("set", p.sol.ident, 1.0),))
    atoms: dict[tuple, float] = {}

    def add(atom: tuple, w: float) -> None:
        atoms[atom] = atoms.get(atom, 0.0) + w

    def add_q(w: float) -> None:
        if isinstance(space, FiniteSpace):
            for v in space.values:
                add(("key", v), w / len(space.values))
            return
        for s in space.specials:
            add(("key", s), w * space.tau / len(space.specials))
        # q's structured part equals the uniform member except on k-colour tasks (palette n vs k)
        same = not isinstance(space, PartitionSpace) or space.k_uniform == space.n
        add(("U",) if same else ("Q-struct",), w * (1 - space.tau))

    if p.kind == "uniform":
        add(("U",), 1.0)
    else:
        for k, v in p.dist.items():
            if k == "_other":
                add_q(v)
            elif k == "_uniform":
                add(("U",), v)
            elif k == "_exact":
                ex = p.exact
                add(("set", ex.sol.ident) if ex.kind == "set" else ("key", ex.key), v)
            else:
                add(("key", k), v)
    return ("noslip", tuple(sorted((a + (round(w, 12),)) for a, w in atoms.items() if w > 0)))


def q_normal_form(space: Space) -> tuple:
    """The normal form of q itself, so members identical to q can be merged with it."""
    return normal_form(Pred("dist", dist={"_other": 1.0}), space)
