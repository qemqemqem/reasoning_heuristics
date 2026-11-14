"""Reference implementations of the zoo members used by the cross-formalism vertical.

Definitions follow the owning verticals (names reused, not redefined):
  C  (C_constructive.md):   FF-sigma, LF, DSATUR, RO-FF, POLARITY, GREEDY-sigma, UC-DET, GUC-DET, GREEDY-CM
  D  (D_F_search.md):       DPLL-b (graph: forward checking; CNF: unit propagation), first solution if b = inf
  F  (D_F_search.md):       MIN-CONFLICTS (graph), WALK-k (CNF)
  B1 (B1_G_relax_decompose.md): UP-k (Jacobi rounds), DROP-CONSTRAINT(LAST)
  E  (E_message_passing.md): WP-t colouring (singleton propagation)
  B4/C4 (B4_C4_restrict_online.md): FIRST, BICOND, ONL(k)
  H  (A_H_baselines.md):    SAMPLE-m, RANDOM

Every member returns an answer in its *own* encoding's terms; build_library.py decodes to the
canonical space (a colouring of the underlying graph, IMPOSSIBLE, or YES/NO).
Answers: ('IMP', None) | ('COL', colouring tuple, possibly invalid) | ('YES',) | ('NO',).
"""
from __future__ import annotations

import itertools
import random
from collections import Counter

from cf_core import K, CNF, Instance, colourings, decode, is_proper, canon

IMP = ('IMP', None)

# ============================================================================================
# Graph-native members (vertex order = listing positions 0..n-1 unless given)
# ============================================================================================


def ff(inst: Instance, order, mode='ABORT', k=K, extra_forbid=None):
    """First-fit in `order`; precoloured vertices are fixed first. mode ABORT -> IMP at a dead end;
    INFEAS -> stuck vertex takes the least-conflict colour (ties smallest)."""
    adj = inst.adj
    col = [0] * inst.n
    for v, c in inst.pre.items():
        col[v] = c
    forbid = extra_forbid or {}
    for v in order:
        if col[v]:
            continue
        used = {col[u] for u in adj[v] if col[u]}
        free = [c for c in range(1, k + 1) if c not in used and c not in forbid.get(v, ())]
        if free:
            col[v] = free[0]
        elif mode == 'ABORT':
            return IMP
        else:
            conf = {c: sum(1 for u in adj[v] if col[u] == c) for c in range(1, k + 1)}
            col[v] = min(range(1, k + 1), key=lambda c: (conf[c], c))
    return ('COL', tuple(col))


def lf_order(inst):
    adj = inst.adj
    return sorted(range(inst.n), key=lambda v: (-len(adj[v]), v))


def dsatur(inst: Instance, mode='ABORT', k=K, tie='list'):
    adj = inst.adj
    col = [0] * inst.n
    for v, c in inst.pre.items():
        col[v] = c
    key2 = (lambda v: v) if tie == 'list' else (lambda v: inst.labels[v])
    while True:
        unc = [v for v in range(inst.n) if not col[v]]
        if not unc:
            return ('COL', tuple(col))
        def score(v):
            sat = len({col[u] for u in adj[v] if col[u]})
            deg_unc = sum(1 for u in adj[v] if not col[u])
            return (-sat, -deg_unc, key2(v))
        v = min(unc, key=score)
        used = {col[u] for u in adj[v] if col[u]}
        free = [c for c in range(1, k + 1) if c not in used]
        if free:
            col[v] = free[0]
        elif mode == 'ABORT':
            return IMP
        else:
            conf = {c: sum(1 for u in adj[v] if col[u] == c) for c in range(1, k + 1)}
            col[v] = min(range(1, k + 1), key=lambda c: (conf[c], c))


def dpll_graph(inst: Instance, branch='list', k=K, budget=None, forbid=None):
    """Backtracking with forward checking (singleton domains assign and prune neighbours).
    branch: 'list' (first unassigned in listing order) | 'dsatur' (smallest domain; ties degree, listing).
    Returns (answer, nodes). answer IMP if exhausted (certified) or budget hit (default IMPOSSIBLE)."""
    adj = inst.adj
    dom0 = [set(range(1, k + 1)) for _ in range(inst.n)]
    for v, c in inst.pre.items():
        dom0[v] = {c}
    for v, cs in (forbid or {}).items():
        dom0[v] -= set(cs)
    nodes = [0]

    def propagate(dom, assigned):
        changed = True
        while changed:
            changed = False
            for v in range(inst.n):
                if not dom[v]:
                    return False
                if len(dom[v]) == 1 and v not in assigned:
                    c = next(iter(dom[v]))
                    assigned.add(v)
                    for u in adj[v]:
                        if c in dom[u]:
                            dom[u] = dom[u] - {c}
                            changed = True
                            if not dom[u]:
                                return False
        return True

    def rec(dom, assigned):
        if budget is not None and nodes[0] >= budget:
            return 'BUDGET'
        if len(assigned) == inst.n:
            return tuple(next(iter(dom[v])) for v in range(inst.n))
        unassigned = [v for v in range(inst.n) if v not in assigned]
        if branch == 'list':
            v = unassigned[0]
        else:
            v = min(unassigned, key=lambda x: (len(dom[x]), -sum(1 for u in adj[x] if u not in assigned), x))
        for c in sorted(dom[v]):
            nodes[0] += 1
            d2 = [set(s) for s in dom]
            d2[v] = {c}
            a2 = set(assigned)
            if propagate(d2, a2):
                r = rec(d2, a2)
                if r == 'BUDGET':
                    return 'BUDGET'
                if r is not None:
                    return r
        return None

    dom = [set(s) for s in dom0]
    assigned = set()
    if not propagate(dom, assigned):
        return IMP, nodes[0]
    r = rec(dom, assigned)
    if r is None or r == 'BUDGET':
        return IMP, nodes[0]
    return ('COL', r), nodes[0]


def wp_colouring(inst: Instance, t, k=K):
    """WP-t colouring = singleton propagation (forward checking) for t synchronous rounds.
    Returns (domains, conflict?)."""
    adj = inst.adj
    dom = [set(range(1, k + 1)) for _ in range(inst.n)]
    for v, c in inst.pre.items():
        dom[v] = {c}
    for _ in range(t):
        new = [set(s) for s in dom]
        for v in range(inst.n):
            for u in adj[v]:
                if len(dom[u]) == 1:
                    new[v] -= dom[u]
        if new == dom:
            break
        dom = new
        if any(not s for s in dom):
            return dom, True
    return dom, any(not s for s in dom)


def drop_last_edges(inst: Instance, q):
    """B1 DROP-CONSTRAINT(LAST, q) o EXACT_LEX: drop the last q edges of the edge list."""
    relaxed = Instance(inst.n, inst.edges[:len(inst.edges) - q], inst.labels, dict(inst.pre), inst.seed)
    ans, _ = dpll_graph(relaxed, 'list')
    return ans


def ro_ff_dist(inst, runs=3000, seed=0, mode='INFEAS'):
    rng = random.Random(seed)
    cnt = Counter()
    for _ in range(runs):
        order = list(range(inst.n))
        rng.shuffle(order)
        a = ff(inst, order, mode)
        cnt[('IMP',) if a[0] == 'IMP' else canon(a[1])] += 1
    return {kk: v / runs for kk, v in cnt.items()}


def min_conflicts_dist(inst, runs=600, steps=2000, seed=0, k=K):
    """F MIN-CONFLICTS, random init, random conflicted vertex; least-conflict colour (keep current if tied)."""
    rng = random.Random(seed)
    adj = inst.adj
    cnt = Counter()
    for _ in range(runs):
        col = [inst.pre.get(v, rng.randint(1, k)) for v in range(inst.n)]
        for _s in range(steps):
            confl = [v for v in range(inst.n) if v not in inst.pre and any(col[u] == col[v] for u in adj[v])]
            if not confl:
                break
            v = rng.choice(confl)
            cc = {c: sum(1 for u in adj[v] if col[u] == c) for c in range(1, k + 1)}
            best = min(cc.values())
            cands = [c for c in range(1, k + 1) if cc[c] == best]
            if col[v] not in cands:
                col[v] = rng.choice(cands)
        cnt[canon(tuple(col)) if is_proper(inst, tuple(col)) else ('INVALID',)] += 1
    return {kk: v / runs for kk, v in cnt.items()}


# ============================================================================================
# CNF-native members
# ============================================================================================


def mention_order(cnf: CNF):
    seen, out = set(), []
    for cl in cnf.clauses:
        for l in cl:
            if abs(l) not in seen:
                seen.add(abs(l))
                out.append(abs(l))
    return out


def clause_status(cl, A):
    """'SAT' | 'FALSE' | ('OPEN', unassigned literals)."""
    un = []
    for l in cl:
        v = abs(l)
        if v in A:
            if A[v] == (l > 0):
                return 'SAT'
        else:
            un.append(l)
    return 'FALSE' if not un else ('OPEN', un)


def cnf_result(cnf, A, abort):
    """Full assignment -> ('TV', set of true vars) or IMP if abort and some clause falsified."""
    falsified = any(clause_status(cl, A) == 'FALSE' for cl in cnf.clauses)
    if falsified and abort:
        return IMP
    return ('TV', frozenset(v for v, b in A.items() if b))


def polarity(cnf: CNF, abort=True):
    pos, neg = Counter(), Counter()
    for cl in cnf.clauses:
        for l in cl:
            (pos if l > 0 else neg)[abs(l)] += 1
    A = {v: pos[v] >= neg[v] for v in range(1, cnf.nvars + 1)}
    return cnf_result(cnf, A, abort)


def greedy(cnf: CNF, order, abort=True):
    A = {}
    for v in order:
        p = q = 0
        for cl in cnf.clauses:
            st = clause_status(cl, A)
            if st == 'SAT':
                continue
            if v in cl:
                p += 1
            if -v in cl:
                q += 1
        A[v] = p >= q
    return cnf_result(cnf, A, abort)


def unit_propagate(cnf_clauses, A, order_hint=None):
    """Sequential UP to fixpoint (lowest-index unit clause first). Returns (A, ok)."""
    A = dict(A)
    while True:
        unit = None
        for cl in cnf_clauses:
            st = clause_status(cl, A)
            if st == 'FALSE':
                return A, False
            if st != 'SAT' and len(st[1]) == 1:
                unit = st[1][0]
                break
        if unit is None:
            return A, True
        A[abs(unit)] = unit > 0


def uc_det(cnf: CNF, free_order, abort=True, extra_clauses=()):
    """UC-DET = UP + GUESS: unit clause (first in clause order) if any, else first unassigned
    variable in free_order set True. ABORT at a falsified clause."""
    clauses = list(extra_clauses) + cnf.clauses
    A = {}
    while True:
        unit = None
        for cl in clauses:
            st = clause_status(cl, A)
            if st == 'FALSE':
                if abort:
                    return IMP
                st = None
                continue
            if st != 'SAT' and len(st[1]) == 1:
                unit = st[1][0]
                break
        if unit is not None:
            A[abs(unit)] = unit > 0
            continue
        free = [v for v in free_order if v not in A]
        if not free:
            return cnf_result(cnf, A, abort)
        A[free[0]] = True


def guc_det(cnf: CNF, abort=True):
    """GUC-DET: pick the first open clause of minimum remaining length; make its first unassigned literal true."""
    A = {}
    while True:
        best = None
        for cl in cnf.clauses:
            st = clause_status(cl, A)
            if st == 'FALSE':
                if abort:
                    return IMP
                continue
            if st == 'SAT':
                continue
            if best is None or len(st[1]) < len(best):
                best = st[1]
        if best is None:
            for v in range(1, cnf.nvars + 1):
                A.setdefault(v, False)
            return cnf_result(cnf, A, abort)
        l = best[0]
        A[abs(l)] = l > 0


def dpll_cnf(cnf: CNF, branch='MENTION', budget=None, extra_clauses=()):
    """DPLL with UP, chronological backtracking, value True first. branch MENTION | INDEX | OCC.
    Returns (('TV', true vars) | IMP, nodes)."""
    clauses = list(extra_clauses) + cnf.clauses
    mo = mention_order(cnf)
    occ = Counter(abs(l) for cl in clauses for l in cl)
    nodes = [0]

    def pick(A):
        free = [v for v in (mo if branch != 'INDEX' else range(1, cnf.nvars + 1)) if v not in A]
        free += [v for v in range(1, cnf.nvars + 1) if v not in A and v not in free]
        if not free:
            return None
        if branch == 'OCC':
            def open_occ(v):
                return sum(1 for cl in clauses if clause_status(cl, A) != 'SAT' and (v in cl or -v in cl))
            return max(free, key=lambda v: (open_occ(v), -free.index(v)))
        return free[0]

    def rec(A):
        if budget is not None and nodes[0] >= budget:
            return 'BUDGET'
        A, ok = unit_propagate(clauses, A)
        if not ok:
            return None
        v = pick(A)
        if v is None:
            return A
        for val in (True, False):
            nodes[0] += 1
            r = rec({**A, v: val})
            if r == 'BUDGET':
                return 'BUDGET'
            if r is not None:
                return r
        return None

    r = rec({})
    if r is None or r == 'BUDGET':
        return IMP, nodes[0]
    return ('TV', frozenset(v for v, b in r.items() if b)), nodes[0]


def up_k(clauses, k, nvars):
    """B1 UP-k, Jacobi rounds (reads only round r-1 state). Returns (A, depth, conflict?)."""
    A, depth = {}, {}
    for cl in clauses:
        if len(cl) == 1:
            A[abs(cl[0])] = cl[0] > 0
            depth[abs(cl[0])] = 0
    for r in range(1, (k if k is not None else 10 ** 6) + 1):
        new = {}
        for cl in clauses:
            st = clause_status(cl, A)
            if st == 'SAT':
                continue
            if st == 'FALSE':
                return A, depth, True
            if len(st[1]) == 1:
                l = st[1][0]
                new.setdefault(abs(l), set()).add(l > 0)
        if not new:
            break
        if any(len(s) == 2 for s in new.values()):
            return A, depth, True
        for v, s in new.items():
            A[v] = s.pop()
            depth[v] = r
    return A, depth, False


def walk_dist(cnf: CNF, inst, runs=400, flips=4000, p=0.5, seed=0):
    """F WALK-k (WalkSAT/SKC), random init, random falsified clause. Distribution over canonical answers."""
    rng = random.Random(seed)
    occ = {v: [] for v in range(1, cnf.nvars + 1)}
    for i, cl in enumerate(cnf.clauses):
        for l in cl:
            occ[abs(l)].append(i)
    cnt = Counter()
    for _ in range(runs):
        A = {v: rng.random() < 0.5 for v in range(1, cnf.nvars + 1)}
        sat = lambda cl: any(A[abs(l)] == (l > 0) for l in cl)
        for _f in range(flips):
            fals = [cl for cl in cnf.clauses if not sat(cl)]
            if not fals:
                break
            cl = rng.choice(fals)

            def break_count(v):   # clauses satisfied now that flipping v would falsify
                before = [sat(cnf.clauses[i]) for i in occ[v]]
                A[v] = not A[v]
                after = [sat(cnf.clauses[i]) for i in occ[v]]
                A[v] = not A[v]
                return sum(1 for b0, b1 in zip(before, after) if b0 and not b1)
            bc = {abs(l): break_count(abs(l)) for l in cl}
            zero = [abs(l) for l in cl if bc[abs(l)] == 0]
            if zero:
                v = zero[0]
            elif rng.random() < p:
                v = abs(rng.choice(cl))
            else:
                v = min((abs(l) for l in cl), key=lambda x: bc[x])
            A[v] = not A[v]
        col, valid = decode(cnf, inst, {v for v, b in A.items() if b})
        cnt[canon(col) if valid else ('INVALID',)] += 1
    return {kk: v / runs for kk, v in cnt.items()}


# ============================================================================================
# Logic-native members (premises = the clause list with surface roles: ALO disjunction with
# disjuncts in written order; binary clause [-a, -b] written "if a then not b"; units as facts)
# ============================================================================================


def sat_check(clauses, nvars):
    from pysat.solvers import Solver
    with Solver(name='g4', bootstrap_with=clauses) as s:
        ok = s.solve()
        return ok, (s.get_model() if ok else None)


def first_member(cnf: CNF, form='L', extra=()):
    """B4 FIRST: every disjunctive premise read as its first disjunct; exact on the result.
    form 'L': only the ALO premises are disjunctions (binary clauses are written as conditionals);
    form 'C': every clause is a disjunction, so every clause is read as its first literal.
    Returns IMP (state contradictory, X) or ('TV', model)."""
    if form == 'L':
        cl2 = [[cl[0]] if kind == 'ALO' else cl for cl, kind in zip(cnf.clauses, cnf.kinds)]
    else:
        cl2 = [[cl[0]] for cl in cnf.clauses]
    cl2 = cl2 + [list(c) for c in extra]
    ok, model = sat_check(cl2, cnf.nvars)
    return ('TV', frozenset(x for x in model if x > 0)) if ok else IMP


def bicond_member(cnf: CNF, extra=()):
    """B4 BICOND: every conditional 'if a then not b' (clause [-a, -b]) read as 'a iff not b',
    i.e. adds the converse clause [a, b]. Exact on the result."""
    cl2 = list(cnf.clauses)
    for cl, kind in zip(cnf.clauses, cnf.kinds):
        if kind in ('AMO', 'CONF'):
            cl2.append([abs(cl[0]), abs(cl[1])])   # converse of 'if a then not b' is 'if b is false then a': (a or b)
    cl2 += [list(c) for c in extra]
    ok, model = sat_check(cl2, cnf.nvars)
    return ('TV', frozenset(x for x in model if x > 0)) if ok else IMP


def premise_alts(cl, kind, form='L'):
    """alts(P) in surface order (B4_C4 §1.1): disjunction -> its disjuncts; 'if a then not b' ->
    [{a, not b}, {not a}]; fact -> [{l}]. In form 'C' every clause is a disjunction of its literals."""
    if form == 'C':
        return [frozenset([l]) for l in cl]
    if kind == 'UNIT':
        return [frozenset([cl[0]])]
    if kind == 'ALO':
        return [frozenset([l]) for l in cl]
    a, b = -cl[0], cl[1]          # clause [-a, -b] rendered 'if a then not b'
    return [frozenset([a, b]), frozenset([-a])]


def onl(cnf: CNF, k, mode='reset', form='L'):
    """C4 ONLINE-STATE(k): premise-at-a-time, keep the first k consistent alternatives (primacy
    truncation), reset (default) or strict (X) on an empty state.
    Returns dict: states (final), x (strict contradiction hit), resets (count)."""
    S = [frozenset()]
    resets = 0
    for cl, kind in zip(cnf.clauses, cnf.kinds):
        alts = premise_alts(cl, kind, form)
        S2, seen = [], set()
        for s in S:
            for a in alts:
                u = s | a
                if any(-l in u for l in u):
                    continue
                if u not in seen:
                    seen.add(u)
                    S2.append(u)
                if len(S2) >= k:
                    break
            if len(S2) >= k:
                break
        if not S2:
            if mode == 'strict':
                return {'states': [], 'x': True, 'resets': resets}
            resets += 1
            S2 = alts[:k]
        S = S2
    return {'states': S, 'x': False, 'resets': resets}


def onl_answer_find(cnf, inst, k, mode, form='L'):
    r = onl(cnf, k, mode, form)
    if r['x']:
        return IMP
    s = r['states'][0]
    return ('TV', frozenset(l for l in s if l > 0))


def onl_answer_must(cnf, k, qvar, form='L'):
    r = onl(cnf, k, 'reset', form)
    if not r['states']:
        return ('NO',)
    return ('YES',) if all(qvar in s for s in r['states']) else ('NO',)


# ============================================================================================
# Counting helpers for H members
# ============================================================================================


def sample_m_must(sols, w, c, m=3):
    """H SAMPLE-m (entailment): P(YES) = (1 - rho)^m, rho = share of models where the query is false."""
    if not sols:
        return 1.0
    rho = sum(1 for s in sols if s[w] != c) / len(sols)
    return (1 - rho) ** m
