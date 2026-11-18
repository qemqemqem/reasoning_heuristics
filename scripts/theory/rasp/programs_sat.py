"""RASP-L programs for CNF tasks, each paired with a plain-Python reference.

SAT-DEC: decide SAT/UNSAT; the answer (1 = SAT) is read at the final Q position.
SAT-VAL: given a satisfiable formula and a target variable v (token after Q), output a
         value for v (1 = true) that some satisfying assignment shares.

Every program is causal: a position sees only earlier tokens.  Several members are
therefore the *causal* variant of the textbook heuristic (information flows from earlier
clauses to later ones only).  The reference functions implement exactly that variant,
and `test_equivalence()` checks program == reference on random instances.
"""

from __future__ import annotations

import random

import numpy as np

import instances as I
from rasp import (SOp, aggregate, full, indices, last, measure, select, select_all,
                  sel_width, seq_map, shift, tok_map, tokens)

# ============================================================================ shared setup


def is_literal(t):
    return (np.abs(t) >= 1) & (np.abs(t) <= 30)


def cnf_setup(tok: SOp) -> dict:
    """7 primitives: lit flag, var, sign, open/close flags, clause id, same-clause selector."""
    lit = tok_map(tok, is_literal)
    var = tok_map(tok, lambda t: np.where(is_literal(t), np.abs(t), 0))
    sgn = tok_map(tok, lambda t: np.where(is_literal(t), np.sign(t), 0))
    is_close = tok == I.CLOSE
    opens = tok == I.OPEN
    cid = sel_width(select(opens, opens, lambda k, q: k == 1))   # clauses opened so far
    same_clause = select(cid, cid, lambda k, q: k == q)
    return dict(lit=lit, var=var, sgn=sgn, close=is_close, same_clause=same_clause)


# ============================================================================ SAT-DEC

def always_sat(seq):
    tok = tokens(seq)
    return tok_map(tok, lambda t: 1)


def density(seq, theta=6):
    """SAT iff (#distinct variables / #tokens) * 127 >= theta, i.e. low clause density."""
    tok = tokens(seq)
    var = tok_map(tok, lambda t: np.where(is_literal(t), np.abs(t), 0))
    first_idx = aggregate(select(var, var, lambda k, q: k == q), indices(tok), "min")
    is_first = seq_map(first_idx, indices(tok), lambda a, b: a == b)          # index == index
    new_var = seq_map(is_first, var, lambda f, v: np.where((f != 0) & (v > 0), 127, 0))
    frac = aggregate(select_all(tok), new_var, "mean")
    return tok_map(frac, lambda f: f >= theta)


def up_causal(seq, k=2):
    """k rounds of causal unit propagation; UNSAT iff a conflict is found.

    Derived literals live at clause-close positions; a literal looks up its variable among
    derived literals of *earlier* clauses (previous round).  A clause whose non-false
    literals collapse to one token (max == min) and which has no true literal is unit.
    """
    tok = tokens(seq)
    s = cnf_setup(tok)
    d = full(tok, 0)            # derived signed literal at close positions
    conflict = full(tok, 0)
    for _ in range(k):
        dvar = tok_map(d, np.abs)
        dsgn = tok_map(d, np.sign)
        look = select(dvar, s["var"], lambda kk, q: (kk == q) & (q > 0))
        vmax = aggregate(look, dsgn, "max")
        vmin = aggregate(look, dsgn, "min")
        packed = seq_map(vmax, vmin, lambda a, b: 3 * a + b)              # in {-4,..,4}
        # status: 0 unassigned, 1 false, 2 true, 3 both (contradiction); per literal
        status = seq_map(packed, s["sgn"], _status)
        hi_val = seq_map(status, tok, lambda st, t: np.where(is_literal(t) & (st != 1), t, -128))
        lo_val = seq_map(status, tok, lambda st, t: np.where(is_literal(t) & (st != 1), t, 127))
        true_v = tok_map(status, lambda st: st >= 2)
        sat = aggregate(s["same_clause"], true_v, "max")
        hi = aggregate(s["same_clause"], hi_val, "max")
        lo = aggregate(s["same_clause"], lo_val, "min")
        open_c = seq_map(sat, s["close"], lambda a, c: (c != 0) & (a == 0))  # unsatisfied close
        unit = seq_map(hi, lo, lambda h, l: np.where(h == -128, -128, np.where(h == l, h, 0)))
        # unit: the single free literal; -128: no free literal (all false); 0: otherwise
        new = seq_map(unit, open_c, lambda u, o: np.where(o != 0, u, 0))
        conflict = seq_map(conflict, new, lambda c, n: (c != 0) | (n == -128))
        bad_lit = tok_map(status, lambda st: st == 3)
        conflict = conflict | bad_lit
        d = seq_map(d, new, lambda old, n: np.where(old != 0, old, np.where(n == -128, 0, n)))
    any_conflict = aggregate(select_all(tok), conflict, "max")
    return ~any_conflict


def _status(packed, sgn):
    # decode packed = 3*vmax + vmin with vmax, vmin in {-1, 0, 1}
    table = {}
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            table[3 * a + b] = (a, b)
    pv = np.vectorize(lambda p: table[int(p)][0])(packed)
    nv = np.vectorize(lambda p: table[int(p)][1])(packed)
    has_pos = (pv == 1) | (nv == 1)
    has_neg = (pv == -1) | (nv == -1)
    agrees = np.where(sgn > 0, has_pos, has_neg)
    disagrees = np.where(sgn > 0, has_neg, has_pos)
    return np.where(agrees & disagrees, 3, np.where(agrees, 2, np.where(disagrees, 1, 0)))


def probe(seq, m=2):
    """FIXED-PROBE-m: SAT iff one of m fixed assignments satisfies every clause, else UNSAT.

    Probes: all-true, all-false, odd-true, even-true (the deterministic stand-in for SAMPLE-m).
    """
    probes = [lambda v: v > 0, lambda v: v < 0,
              lambda v: (v > 0) == (np.abs(v) % 2 == 1), lambda v: (v > 0) == (np.abs(v) % 2 == 0)]
    tok = tokens(seq)
    s = cnf_setup(tok)
    alls = select_all(tok)
    ok = full(tok, 0)
    for p in probes[:m]:
        lt = tok_map(tok, lambda t, p=p: is_literal(t) & p(t))
        sat = aggregate(s["same_clause"], lt, "max")
        bad = seq_map(sat, s["close"], lambda a, c: (c != 0) & (a == 0))
        any_bad = aggregate(alls, bad, "max")
        ok = seq_map(ok, any_bad, lambda o, b: (o != 0) | (b == 0))
    return ok


# ---------------------------------------------------------------------------- references


def ref_density(clauses, n, theta=6):
    T = 2 + 5 * len(clauses)
    nvars = len({abs(l) for c in clauses for l in c})
    return int(127 * nvars // T >= theta)


def ref_up_causal(clauses, k=2):
    m = len(clauses)
    d = [0] * m
    conflict = False
    for _ in range(k):
        new_d = list(d)
        for j, c in enumerate(clauses):
            signs = {}
            for i in range(j):
                if d[i]:
                    signs.setdefault(abs(d[i]), set()).add(1 if d[i] > 0 else -1)
            sat, free = False, []
            for lit in c:
                s = signs.get(abs(lit), set())
                agree, disagree = (1 if lit > 0 else -1) in s, (-1 if lit > 0 else 1) in s
                if agree and disagree:
                    conflict = True
                if agree:
                    sat = True
                if agree or not disagree:
                    free.append(lit)
            if not sat:
                if not free:
                    conflict = True
                elif len(set(free)) == 1 and d[j] == 0:
                    new_d[j] = free[0]
        d = new_d
    return int(not conflict)


def ref_up_full(clauses, n, k=None):
    """Non-causal unit propagation (k rounds, None = fixpoint); UNSAT iff conflict."""
    assign = {}
    rounds = 0
    while k is None or rounds < k:
        rounds += 1
        new = {}
        for c in clauses:
            free, sat = [], False
            for lit in c:
                if abs(lit) in assign:
                    sat |= assign[abs(lit)] == (lit > 0)
                else:
                    free.append(lit)
            if sat:
                continue
            if not free:
                return 0
            if len(free) == 1:
                v, val = abs(free[0]), free[0] > 0
                if new.get(v, val) != val:
                    return 0
                new[v] = val
        if not new:
            break
        assign.update(new)
    return 1


def ref_probe(clauses, m=2):
    probes = [lambda v: v > 0, lambda v: v < 0,
              lambda v: (v > 0) == (abs(v) % 2 == 1), lambda v: (v > 0) == (abs(v) % 2 == 0)]
    return int(any(all(any(p(l) for l in c) for c in clauses) for p in probes[:m]))


# ============================================================================ SAT-VAL

LOGQ = {}  # int8 log-probability table: P(literal false) from a polarity mean in [-100, 100]


def _p_false(pol, sgn):
    """P(literal false) in percent, from the variable's mean polarity (x100)."""
    p_true_var = (pol + 100) / 2           # 0..100
    p_true_lit = np.where(sgn > 0, p_true_var, 100 - p_true_var)
    return np.clip(100 - p_true_lit, 1, 99)


def prompt_mask(tok):
    """1 before the query marker Q, 0 from Q on (4 primitives)."""
    return ~aggregate(select_all(tok), tok == I.Q, "max")


def polarity(seq):
    """BP-0: value = sign of the target variable's mean polarity (ties -> true)."""
    tok = tokens(seq)
    var = seq_map(tok, prompt_mask(tok), lambda t, m: np.where(is_literal(t) & (m != 0), np.abs(t), 0))
    sgn100 = tok_map(tok, lambda t: np.where(is_literal(t), 100 * np.sign(t), 0))
    pol = aggregate(select(var, tok, lambda k, q: (k == q) & (k > 0)), sgn100, "mean")
    return tok_map(pol, lambda p: p >= 0)


def bp_causal(seq, t=1):
    """BP-t (causal, int8, mean-field): t rounds of clause->variable messages on 3-CNF.

    Round 0 belief of a literal's variable = mean polarity of its earlier occurrences.
    A clause (at its close) sends to each of its 3 slots the 'need' = product of the
    other two literals' P(false) (in percent).  A literal position updates its variable's
    belief with the mean signed need from earlier clauses (one head per slot), and the
    query position reads the same quantity for the target variable over the whole prompt.
    """
    tok = tokens(seq)
    s = cnf_setup(tok)
    s["var"] = seq_map(s["var"], prompt_mask(tok), lambda v, m: v * (m != 0))
    s["sgn"] = seq_map(s["sgn"], s["var"], lambda g, v: g * (v != 0))
    sgn100 = tok_map(s["sgn"], lambda x: 100 * x)
    pol = aggregate(select(s["var"], s["var"], lambda k, q: (k == q) & (k > 0)), sgn100, "mean")
    belief = pol                                            # in [-100, 100]
    idx = indices(tok)
    back = [select(_succ_free(idx, j), idx, lambda k, q: k == q) for j in (1, 2, 3)]
    slot_var = [aggregate(b, s["var"], "max") for b in back]   # var of literal j back
    slot_sgn = [aggregate(b, s["sgn"], "max") for b in back]
    slot_var = [seq_map(v, s["close"], lambda a, c: np.where(c != 0, a, 0)) for v in slot_var]
    for _ in range(t):
        pf = seq_map(belief, s["sgn"], lambda b, g: np.where(g != 0, _p_false(b, g), 0))
        slot_pf = [aggregate(b, pf, "max") for b in back]
        # need for slot j = product of the other two P(false), percent
        need = [seq_map(slot_pf[(j + 1) % 3], slot_pf[(j + 2) % 3], lambda a, b: a * b // 100)
                for j in range(3)]
        signed = [seq_map(need[j], slot_sgn[j], lambda a, g: a * g) for j in range(3)]
        msgs = [aggregate(select(slot_var[j], s["var"], lambda k, q: (k == q) & (q > 0)),
                          signed[j], "mean") for j in range(3)]
        summ = seq_map(seq_map(msgs[0], msgs[1], lambda a, b: a + b), msgs[2],
                       lambda a, b: np.clip(a + b, -127, 127))
        belief = seq_map(pol, summ, lambda p, m_: np.clip(p // 2 + m_, -100, 100))
    # read out at the query position (token = target variable)
    final = [aggregate(select(slot_var[j], tok, lambda k, q: (k == q) & (k > 0)),
                       signed[j], "mean") for j in range(3)] if t > 0 else []
    qpol = aggregate(select(s["var"], tok, lambda k, q: (k == q) & (k > 0)), sgn100, "mean")
    if not final:
        return tok_map(qpol, lambda p: p >= 0)
    tot = seq_map(seq_map(final[0], final[1], lambda a, b: a + b), final[2],
                  lambda a, b: np.clip(a + b, -127, 127))
    return seq_map(qpol, tot, lambda p, m_: (p // 2 + m_) >= 0)


def _succ_free(idx, j):
    from rasp import succ
    return succ(idx, j)


def ref_polarity(clauses, v):
    occ = [np.sign(l) for c in clauses for l in c if abs(l) == v]
    return int(np.trunc(100 * sum(occ) / len(occ)) >= 0) if occ else 1


def ref_bp(clauses, v, t=1):
    """Non-causal BP-t with the same message form (exact sums, floats) for comparison."""
    vars_ = {abs(l) for c in clauses for l in c}
    pol = {u: np.mean([np.sign(l) for c in clauses for l in c if abs(l) == u]) for u in vars_}
    belief = dict(pol)
    for _ in range(t):
        def pf(l):
            pt = (belief[abs(l)] + 1) / 2
            return float(np.clip(1 - (pt if l > 0 else 1 - pt), 0.01, 0.99))
        msg = {u: 0.0 for u in vars_}
        for c in clauses:
            for j, l in enumerate(c):
                need = np.prod([pf(o) for i, o in enumerate(c) if i != j])
                msg[abs(l)] += np.sign(l) * need
        belief = {u: float(np.tanh(pol[u] / 2 + msg[u])) for u in vars_}
    return int(belief.get(v, 0) >= 0)


# ============================================================================ checks


def test_equivalence(n_trials=200, seed=0):
    rng = random.Random(seed)
    bad = 0
    for _ in range(n_trials):
        n = rng.randint(4, 9)
        clauses = mixed_cnf(n, rng.randint(3, 4 * n), rng)
        seq = I.cnf_tokens(clauses)
        for k in (1, 2, 3):
            bad += last(up_causal(seq, k)) != ref_up_causal(clauses, k)
        for m in (2, 4):
            bad += last(probe(seq, m)) != ref_probe(clauses, m)
        bad += last(density(seq)) != ref_density(clauses, n)
        cl3 = I.random_ksat(n, rng.randint(2, 4 * n), 3, rng)
        v = rng.randint(1, n)
        if any(abs(l) == v for c in cl3 for l in c):
            bad += last(polarity(I.cnf_tokens(cl3, v))) != ref_polarity(cl3, v)
    return bad


def mixed_cnf(n, m, rng=random, widths=(1, 2, 3), weights=(0.15, 0.35, 0.5)):
    """Puzzle-like CNF: some given facts (units), binary and ternary constraints."""
    out = []
    for _ in range(m):
        w = min(rng.choices(widths, weights)[0], n)
        out.append(tuple(v if rng.random() < 0.5 else -v for v in rng.sample(range(1, n + 1), w)))
    return out


if __name__ == "__main__":
    print("equivalence failures:", test_equivalence())
    ex = I.cnf_tokens(I.random_ksat(6, 10, 3), 3)
    for name, prog in [("ALWAYS-SAT", always_sat), ("DENSITY", density),
                       ("UP-1c", lambda s: up_causal(s, 1)), ("UP-2c", lambda s: up_causal(s, 2)),
                       ("UP-3c", lambda s: up_causal(s, 3)), ("PROBE-2", lambda s: probe(s, 2)),
                       ("PROBE-4", lambda s: probe(s, 4)), ("POLARITY", polarity),
                       ("BP-1c", lambda s: bp_causal(s, 1)), ("BP-2c", lambda s: bp_causal(s, 2))]:
        print(measure(name, prog, ex))
