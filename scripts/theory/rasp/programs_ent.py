"""RASP-L programs for propositional entailment (task ENT), plus Python-only members.

Input: ``BOS  premise .  premise .  ...  ? L END`` (see instances.py), answer at END:
1 = "follows", 0 = "does not follow".

Programs (all causal, one pass):
  ALWAYS-NO, MATCH, PRIMACY, UP-k (bidirectional causal propagation over 2-literal
  clauses), FIRST o UP-k, BICOND o UP-k.
FIRST and BICOND are *the same program* as UP-k with a different role table (FIRST) or
two extra lookups (BICOND): restriction heuristics are nearly free once a propagation
skeleton exists.  Python-only members: EXACT, MM (initial mental models), SAMPLE-m,
NOISY-EXACT.
"""

from __future__ import annotations

import random

import numpy as np

import instances as I
from rasp import (aggregate, full, indices, last, map_n, measure, select, select_all,
                  seq_map, succ, tok_map, tokens)

ROLE_NONE, ROLE_FACT, ROLE_D1, ROLE_D2, ROLE_ANTE, ROLE_CONS, ROLE_QUERY = range(7)
CTX_ROLE = {I.BOS: ROLE_FACT, I.DOT: ROLE_FACT, I.AND: ROLE_FACT, I.EITHER: ROLE_D1,
            I.OR: ROLE_D2, I.IF: ROLE_ANTE, I.THEN: ROLE_CONS, I.QMARK: ROLE_QUERY}


def _role_table(ctx, atom, first=False):
    out = np.zeros_like(ctx)
    for c, r in CTX_ROLE.items():
        if first and r == ROLE_D1:
            r = ROLE_FACT          # FIRST: "either A or B" read as A
        elif first and r == ROLE_D2:
            r = ROLE_NONE          # ... and B is dropped
        out = np.where(ctx == c, r, out)
    return np.where(atom != 0, out, ROLE_NONE)


def setup(tok, first=False):
    idx = indices(tok)
    back = {j: select(succ(idx, j), idx, lambda k, q: k == q) for j in (1, 2, 3)}
    atom = tok_map(tok, lambda t: (t >= 1) & (t <= 6))
    prev = aggregate(back[1], tok, "max")
    prev2 = aggregate(back[2], tok, "max")
    neg = tok_map(prev, lambda p: p == I.NOT)
    ctx = seq_map(prev, prev2, lambda p, p2: np.where(p == I.NOT, p2, p))
    lit = seq_map(tok, neg, lambda t, n: np.where((t >= 1) & (t <= 6), np.where(n != 0, -t, t), 0))
    role = seq_map(ctx, atom, lambda c, a: _role_table(c, a, first))
    return dict(tok=tok, idx=idx, back=back, atom=atom, prev=prev, prev2=prev2, neg=neg,
                lit=lit, role=role)


def query_literal(s):
    """At END: the conclusion literal (atom one back, NOT two back)."""
    return seq_map(s["prev"], s["prev2"], lambda p, p2: np.where(p2 == I.NOT, -p, p))


def _exists(slot, q):
    """1 if an earlier position holds literal q in this slot (select + aggregate)."""
    return aggregate(select(slot, q, lambda k, qq: (k == qq) & (qq != 0)),
                     full(slot, 1), "max")


# ============================================================================ members


def always_no(seq):
    return tok_map(tokens(seq), lambda t: 0)


def match(seq):
    """Follows iff the conclusion literal occurs (same sign) somewhere in the premises."""
    tok = tokens(seq)
    s = setup(tok)
    prem_lit = seq_map(s["lit"], s["role"], lambda l, r: np.where(r == ROLE_QUERY, 0, l))
    return _exists(prem_lit, query_literal(s))


def primacy(seq):
    """Follows iff the conclusion literal occurs in the first premise."""
    tok = tokens(seq)
    s = setup(tok)
    dots = aggregate(select_all(tok), tok == I.DOT, "max")          # a DOT seen already?
    first_lit = seq_map(s["lit"], dots, lambda l, d: np.where(d == 0, l, 0))
    return _exists(first_lit, query_literal(s))


def up(seq, k=2, first=False, bicond=False):
    """k rounds of causal propagation over facts and 2-literal clauses.

    Facts live in slot A (fact positions; clause positions receive forward derivations).
    A clause (cx v cy) is stored at its second literal.  Lookups are sign-carrying: a
    position fetches an earlier fact *on the same variable* and a decision table says
    what it licenses, so FIRST (role table) and BICOND (decision table) reuse the
    skeleton at the same length.
    Round r: (i) a clause derives cy if an earlier slot holds -cx (cx if -cy);
    (ii) a position holding fact z derives the other literal of an earlier clause on |z|
    into a fresh slot B_r.  k = 0: the conclusion must be a stated fact.
    """
    tok = tokens(seq)
    s = setup(tok, first)
    role, lit = s["role"], s["lit"]
    A = seq_map(lit, role, lambda l, r: np.where(r == ROLE_FACT, l, 0))
    slots_b, fvars = [], []
    if k > 0:
        l2 = aggregate(s["back"][2], lit, "max")
        l3 = aggregate(s["back"][3], lit, "max")
        partner = seq_map(l2, l3, lambda a, b: np.where(a != 0, a, b))     # previous literal
        cx = seq_map(partner, role, lambda p, r: np.where(r == ROLE_CONS, -p, np.where(r == ROLE_D2, p, 0)))
        cy = seq_map(lit, role, lambda l, r: np.where((r == ROLE_CONS) | (r == ROLE_D2), l, 0))
        iff = tok_map(role, lambda r: (r == ROLE_CONS) & bicond)               # BICOND table
        vx, vy = tok_map(cx, np.abs), tok_map(cy, np.abs)
    for r in range(k):
        facts = [A] + slots_b
        fvars = [tok_map(A, np.abs)] + fvars[1:]          # slot A changes every round
        newA = A
        for f, fv in zip(facts, fvars):
            fx = aggregate(select(fv, vx, lambda kk, q: (kk == q) & (q != 0)), f, "max")
            fy = aggregate(select(fv, vy, lambda kk, q: (kk == q) & (q != 0)), f, "max")
            d = map_n(_forward, fx, fy, cx, cy, iff)
            newA = seq_map(newA, d, lambda a, b: np.where(a != 0, a, b))
        z = A if not slots_b else seq_map(slots_b[-1], A, lambda b, a: np.where(b != 0, b, a))
        zv = tok_map(z, np.abs)
        hit_x = select(vx, zv, lambda kk, q: (kk == q) & (q != 0))
        hit_y = select(vy, zv, lambda kk, q: (kk == q) & (q != 0))
        x_cx, x_cy, x_iff = (aggregate(hit_x, v, "max") for v in (cx, cy, iff))
        y_cy, y_cx, y_iff = (aggregate(hit_y, v, "max") for v in (cy, cx, iff))
        derived = map_n(_backward, z, x_cx, x_cy, x_iff, y_cy, y_cx, y_iff)
        slots_b.append(derived)
        fvars = (fvars or [None]) + [tok_map(derived, np.abs)]
        A = newA
    c = query_literal(s)
    return _any([_exists(f, c) for f in [A] + slots_b])


def _forward(fx, fy, cx, cy, iff):
    """Clause (cx v cy) at this position; fx, fy = earlier facts on |cx|, |cy| (0 = none)."""
    out = np.where((fx != 0) & (fx == -cx), cy, 0)
    out = np.where((out == 0) & (fy != 0) & (fy == -cy), cx, out)
    out = np.where((out == 0) & (iff != 0) & (fy != 0) & (fy == cy), -cx, out)   # b => a
    out = np.where((out == 0) & (iff != 0) & (fx != 0) & (fx == cx), -cy, out)   # -a => -b
    return out


def _backward(z, x_cx, x_cy, x_iff, y_cy, y_cx, y_iff):
    """Fact z here; an earlier clause has cx (resp. cy) on |z|."""
    out = np.where((z != 0) & (x_cx == -z), x_cy, 0)
    out = np.where((out == 0) & (z != 0) & (y_cy == -z), y_cx, out)
    out = np.where((out == 0) & (z != 0) & (y_iff != 0) & (y_cy == z), -y_cx, out)
    out = np.where((out == 0) & (z != 0) & (x_iff != 0) & (x_cx == z), -x_cy, out)
    return out


def probe(seq, m=4):
    """FIXED-PROBE-m: look for a counter-model among m fixed assignments.

    Probe i makes atom a true iff bit (a-1) of i is set, so m = 2**a probes enumerate every
    assignment of atoms 1..a: EXACT on items with <= a atoms (a non-uniform, parallel truth
    table), and a deterministic SAMPLE-m on larger items (atoms > a are always false).
    "Follows" iff no probe satisfies every premise while falsifying the conclusion.
    """
    tok = tokens(seq)
    s = setup(tok)
    role, lit = s["role"], s["lit"]
    l2 = aggregate(s["back"][2], lit, "max")
    l3 = aggregate(s["back"][3], lit, "max")
    partner = seq_map(l2, l3, lambda a, b: np.where(a != 0, a, b))
    c = query_literal(s)
    alls = select_all(tok)
    counter = full(tok, 0)
    for i in range(m):
        def truth(l, i=i):
            a = np.abs(l)
            val = ((i >> np.maximum(a - 1, 0)) & 1) == 1
            return np.where(l == 0, 0, np.where(l > 0, val, ~val)).astype(int)
        t = tok_map(lit, truth)
        tp = tok_map(partner, truth)
        falsified = map_n(lambda r, a, b: ((r == ROLE_FACT) & (a == 0)) | ((r == ROLE_D2) & (a == 0) & (b == 0))
                          | ((r == ROLE_CONS) & (a == 0) & (b == 1)), role, t, tp)
        any_false = aggregate(alls, falsified, "max")
        cm = seq_map(any_false, tok_map(c, truth), lambda f, ct: (f == 0) & (ct == 0))
        counter = counter | cm
    return ~counter


def _any(xs):
    out = xs[0]
    for x in xs[1:]:
        out = out | x
    return out


# ============================================================================ Python-only


def ref_exact(prem, concl, n_atoms):
    return int(I.entails(prem, concl, n_atoms))


def ref_mm(prem, concl, n_atoms):
    """Initial mental models (principle of truth): or -> {a},{b},{a,b}; if -> {a,b};
    conjoin by product, drop contradictory models; follows iff every model contains concl."""
    sets = [frozenset()]
    for kind, ls in prem:
        if kind == "fact":
            alts = [{ls[0]}]
        elif kind == "and":
            alts = [{ls[0], ls[1]}]
        elif kind == "or":
            alts = [{ls[0]}, {ls[1]}, {ls[0], ls[1]}]
        else:
            alts = [{ls[0], ls[1]}]
        new = []
        for m in sets:
            for a in alts:
                u = m | a
                if not any(-x in u for x in u) and u not in new:
                    new.append(frozenset(u))
        sets = new
    return int(bool(sets) and all(concl in m for m in sets))


def ref_sample(prem, concl, n_atoms, m=4, rng=random):
    cl = I.premise_clauses(prem)
    for _ in range(m):
        bits = [rng.random() < 0.5 for _ in range(n_atoms)]
        if all(any(bits[abs(l) - 1] == (l > 0) for l in c) for c in cl):
            if bits[abs(concl) - 1] != (concl > 0):
                return 0
    return 1


def ref_noisy_exact(prem, concl, n_atoms, eps=0.02, rng=random):
    """Exact truth-table check with an independent slip per evaluated row."""
    cl = I.premise_clauses(prem)
    import itertools
    for bits in itertools.product((False, True), repeat=n_atoms):
        holds = all(any(bits[abs(l) - 1] == (l > 0) for l in c) for c in cl)
        if rng.random() < eps:
            holds = not holds
        if holds and bits[abs(concl) - 1] != (concl > 0):
            return 0
    return 1


# ============================================================================ checks

SCHEMAS = [  # (premises, conclusion, expected UP-2, expected FIRST, expected BICOND)
    ([("if", (1, 2)), ("fact", (1,))], 2, 1, 1, 1),            # MP, rule first
    ([("fact", (1,)), ("if", (1, 2))], 2, 1, 1, 1),            # MP, fact first
    ([("if", (1, 2)), ("fact", (-2,))], -1, 1, 1, 1),          # MT
    ([("or", (1, 2)), ("fact", (-1,))], 2, 1, 0, 1),           # DS (FIRST reads it as 1)
    ([("or", (1, 2))], 1, 0, 1, 0),                            # illusory: FIRST says 1 follows
    ([("if", (1, 2)), ("fact", (2,))], 1, 0, 0, 1),            # affirming the consequent
    ([("if", (1, 2)), ("fact", (-1,))], -2, 0, 0, 1),          # denying the antecedent
    ([("fact", (1,)), ("if", (1, 2)), ("if", (2, 3))], 3, 1, 1, 1),  # chain, forward
    ([("if", (2, 3)), ("if", (1, 2)), ("fact", (1,))], 3, 1, 1, 1),  # chain, backward
]


def test_schemas():
    fails = []
    for prem, c, e_up, e_first, e_bi in SCHEMAS:
        seq = I.entailment_tokens(prem, c)
        got = (last(up(seq, 2)), last(up(seq, 2, first=True)), last(up(seq, 2, bicond=True)))
        if got != (e_up, e_first, e_bi):
            fails.append((prem, c, got, (e_up, e_first, e_bi)))
    return fails


if __name__ == "__main__":
    print("schema failures:", test_schemas())
    seq = I.entailment_tokens([("or", (1, -2)), ("if", (1, 3)), ("fact", (-3,))], 2)
    for name, prog in [("ALWAYS-NO", always_no), ("MATCH", match), ("PRIMACY", primacy),
                       ("UP-1", lambda s: up(s, 1)), ("UP-2", lambda s: up(s, 2)),
                       ("FIRST.UP-1", lambda s: up(s, 1, first=True)),
                       ("FIRST.UP-2", lambda s: up(s, 2, first=True)),
                       ("BICOND.UP-2", lambda s: up(s, 2, bicond=True))]:
        print(measure(name, prog, seq))
