"""Instance generators, serialisations and exact solvers for the T2 theory scripts.

Serialisations (all tokens are int8):

* CNF (tasks SAT-DEC, SAT-VAL): ``BOS ( l l l ) ( l l l ) ... Q [v]``.  A literal is
  +v or -v for variable v in 1..30; OPEN = 101, CLOSE = 102.  For SAT-VAL the query
  token Q is followed by the target variable v, and the answer is read there.
* Entailment (task ENT): premises in a fixed grammar, ``L .`` / ``L and L .`` /
  ``either L or L .`` / ``if L then L .`` with L = atom | ``not`` atom (atoms 1..6),
  then ``? L END``.  Connectives come first so a literal's role is known causally.
* Colouring (task COL): an edge list ``BOS a b , a b , ... ;`` then the answer
  ``v c v c ...`` in vertex order 1..n.
"""

from __future__ import annotations

import itertools
import random

# ----------------------------------------------------------------------------- tokens
BOS, OPEN, CLOSE, Q = 120, 101, 102, 103
NOT, AND, EITHER, OR, IF, THEN, DOT, QMARK, END = 20, 21, 22, 23, 24, 25, 26, 27, 28
COMMA, SEMI = 104, 105

# ----------------------------------------------------------------------------- CNF


def random_ksat(n: int, m: int, k: int = 3, rng=random) -> list[tuple[int, ...]]:
    return [tuple(v if rng.random() < 0.5 else -v for v in rng.sample(range(1, n + 1), k))
            for _ in range(m)]


def cnf_tokens(clauses, query_var: int | None = None) -> list[int]:
    toks = [BOS]
    for c in clauses:
        toks += [OPEN, *c, CLOSE]
    toks.append(Q)
    if query_var is not None:
        toks.append(query_var)
    return toks


def _unit_propagate(clauses, assign):
    """Return (assign, conflict) after unit propagation to fixpoint."""
    assign = dict(assign)
    changed = True
    while changed:
        changed = False
        for c in clauses:
            free, sat = [], False
            for lit in c:
                v = abs(lit)
                if v in assign:
                    if assign[v] == (lit > 0):
                        sat = True
                        break
                else:
                    free.append(lit)
            if sat:
                continue
            if not free:
                return assign, True
            if len(free) == 1:
                assign[abs(free[0])] = free[0] > 0
                changed = True
    return assign, False


def solve(clauses, n: int, assign=None):
    """Tiny DPLL. Returns a satisfying assignment dict or None."""
    assign, conflict = _unit_propagate(clauses, assign or {})
    if conflict:
        return None
    free = [v for v in range(1, n + 1) if v not in assign]
    if not free:
        return assign
    # branch on the most frequent free variable
    counts = {v: 0 for v in free}
    for c in clauses:
        for lit in c:
            if abs(lit) in counts:
                counts[abs(lit)] += 1
    v = max(free, key=lambda u: counts[u])
    for val in (True, False):
        res = solve(clauses, n, {**assign, v: val})
        if res is not None:
            return res
    return None


def satisfiable(clauses, n) -> bool:
    return solve(clauses, n) is not None


def value_ok(clauses, n, v, val: bool) -> bool:
    """Is there a satisfying assignment with x_v = val?"""
    return solve(clauses, n, {v: val}) is not None


# ----------------------------------------------------------------------------- entailment

# A premise is (kind, lits) with kind in {"fact", "and", "or", "if"}; a literal is +a / -a.


def random_premises(n_atoms: int, n_prem: int, rng=random):
    kinds = ["fact", "and", "or", "if"]
    weights = [0.25, 0.1, 0.3, 0.35]
    prem = []
    for _ in range(n_prem):
        kind = rng.choices(kinds, weights)[0]
        if kind == "fact":
            a = rng.randint(1, n_atoms)
            prem.append((kind, (a if rng.random() < 0.7 else -a,)))
        else:
            a, b = rng.sample(range(1, n_atoms + 1), 2)
            sa = a if rng.random() < 0.75 else -a
            sb = b if rng.random() < 0.75 else -b
            prem.append((kind, (sa, sb)))
    return prem


def premise_clauses(prem):
    out = []
    for kind, lits in prem:
        if kind == "fact":
            out.append((lits[0],))
        elif kind == "and":
            out += [(lits[0],), (lits[1],)]
        elif kind == "or":
            out.append((lits[0], lits[1]))
        elif kind == "if":
            out.append((-lits[0], lits[1]))
    return out


def models(clauses, n_atoms):
    for bits in itertools.product((False, True), repeat=n_atoms):
        if all(any(bits[abs(l) - 1] == (l > 0) for l in c) for c in clauses):
            yield bits


def entails(prem, concl: int, n_atoms: int) -> bool:
    cl = premise_clauses(prem)
    return all(bits[abs(concl) - 1] == (concl > 0) for bits in models(cl, n_atoms))


def consistent(prem, n_atoms) -> bool:
    return next(models(premise_clauses(prem), n_atoms), None) is not None


def random_entailment_item(rng=random, n_atoms_range=(3, 4), n_prem_range=(2, 4)):
    """Consistent premises; the conclusion's atom is mentioned in the premises."""
    while True:
        n_atoms = rng.randint(*n_atoms_range)
        prem = random_premises(n_atoms, rng.randint(*n_prem_range), rng)
        if not consistent(prem, n_atoms):
            continue
        mentioned = sorted({abs(l) for _, ls in prem for l in ls})
        a = rng.choice(mentioned)
        concl = a if rng.random() < 0.6 else -a
        return prem, concl, n_atoms


def lit_tokens(l: int) -> list[int]:
    return [l] if l > 0 else [NOT, -l]


def entailment_tokens(prem, concl) -> list[int]:
    toks = [BOS]
    for kind, ls in prem:
        if kind == "fact":
            toks += lit_tokens(ls[0])
        elif kind == "and":
            toks += lit_tokens(ls[0]) + [AND] + lit_tokens(ls[1])
        elif kind == "or":
            toks += [EITHER] + lit_tokens(ls[0]) + [OR] + lit_tokens(ls[1])
        elif kind == "if":
            toks += [IF] + lit_tokens(ls[0]) + [THEN] + lit_tokens(ls[1])
        toks.append(DOT)
    toks += [QMARK] + lit_tokens(concl) + [END]
    return toks


# ----------------------------------------------------------------------------- colouring


def planted_colourable(n: int, k: int, p: float, rng=random):
    col = [rng.randrange(k) for _ in range(n)]
    edges = [(u, v) for u in range(1, n + 1) for v in range(u + 1, n + 1)
             if col[u - 1] != col[v - 1] and rng.random() < p]
    rng.shuffle(edges)
    return edges


def colourable(n: int, edges, k: int) -> bool:
    adj = {v: set() for v in range(1, n + 1)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    order = sorted(adj, key=lambda v: -len(adj[v]))
    col = {}

    def bt(i):
        if i == len(order):
            return True
        v = order[i]
        used = {col[u] for u in adj[v] if u in col}
        for c in range(1, k + 1):
            if c not in used:
                col[v] = c
                if bt(i + 1):
                    return True
                del col[v]
        return False

    return bt(0)


def colour_prompt(edges) -> list[int]:
    toks = [BOS]
    for u, v in edges:
        toks += [u, v, COMMA]
    toks.append(SEMI)
    return toks


def proper(edges, col: dict) -> bool:
    return all(col.get(u) != col.get(v) for u, v in edges)
