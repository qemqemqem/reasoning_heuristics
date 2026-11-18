"""Per-step (next-token) programs for greedy graph colouring (task COL).

Prompt: ``BOS a b , a b , ... ;`` (edge list).  Two answer formats:

* TERSE   ``v c v c ... STOP``  (vertices in order 1..n).  The FIRST-FIT step needs the
  colours of v's already-coloured neighbours: a join between prompt structure (edges)
  and generated state (colours).  We could not write it with int8 scalar values; it is
  short with *set-valued* aggregation (`aggregate_set`, flagged non-RASP-L).
* VERBOSE ``v : u1 c1 u2 c2 ... -> c |`` per vertex, listing earlier neighbours with
  their colours.  Every token is then a strict RASP-L step (int8, index comparisons).

Both programs are run autoregressively (append the argmax token, re-run) and checked
against Python FIRST-FIT.  Python-only members: DSATUR, RANDOM-ORDER-FF, LOCAL-t, RANDOM.
"""

from __future__ import annotations

import random

import numpy as np

import instances as I
from rasp import (aggregate, aggregate_set, full, indices, last, map_n, measure, select,
                  select_all, seq_map, succ, tok_map, tokens)

COL0 = 60                       # colour c is token 60 + c
COLON, ARROW, LINE_END, STOP = 106, 107, 108, 109
K_MAX = 6


def is_vertex(t):
    return (t >= 1) & (t <= 30)


def is_colour(t):
    return (t > COL0) & (t <= COL0 + K_MAX)


def _prompt_parts(tok):
    idx = indices(tok)
    back1 = select(succ(idx, 1), idx, lambda k, q: k == q)
    prev = aggregate(back1, tok, "max")
    seen_semi = aggregate(select_all(tok), tok == I.SEMI, "max")
    # second endpoint of an edge "a b ,": a vertex whose predecessor is a vertex, in the prompt
    second = map_n(lambda t, p, s: is_vertex(t) & is_vertex(p) & (s == 0), tok, prev, seen_semi)
    partner = seq_map(prev, second, lambda p, s: np.where(s != 0, p, 0))
    ep = seq_map(tok, second, lambda t, s: np.where(s != 0, t, 0))
    nmax = aggregate(select_all(tok), seq_map(tok, seen_semi, lambda t, s: np.where(is_vertex(t) & (s == 0), t, 0)), "max")
    return idx, prev, seen_semi, partner, ep, nmax


# ============================================================================ terse (set ext.)


def ff_terse_step(seq):
    tok = tokens(seq)
    idx, prev, seen_semi, partner, ep, nmax = _prompt_parts(tok)
    # neighbour set of the vertex at each position (union over both edge directions)
    n1 = aggregate_set(select(partner, tok, lambda k, q: (k == q) & (q > 0)), ep)
    n2 = aggregate_set(select(ep, tok, lambda k, q: (k == q) & (q > 0)), partner)
    nset = seq_map(n1, n2, None) if False else _union(n1, n2)
    # colour tokens carry the vertex they colour (the previous token)
    cvert = seq_map(prev, tok, lambda p, t: np.where(is_colour(t), p, 0))
    used = aggregate_set(select(cvert, nset, lambda k, qs: k in qs and k > 0), tok)
    colour = _mex(used)
    nxt = map_n(_terse_next, tok, prev, nmax, colour)
    return nxt


def _union(a, b):
    from rasp import SOp, _tick, flag
    _tick("seq_map", max(a.layer, b.layer))
    flag("set_valued")
    return SOp([x | y for x, y in zip(a.val, b.val)], "set", max(a.layer, b.layer))


def _mex(used):
    from rasp import SOp, _tick
    _tick("tok_map", used.layer)
    vals = []
    for s in used.val:
        c = 1
        while COL0 + c in s:
            c += 1
        vals.append(COL0 + min(c, K_MAX))
    return SOp(np.array(vals), "int8", used.layer)


def _terse_next(t, p, n, colour):
    return np.where(t == I.SEMI, 1,
           np.where(is_colour(t), np.where(p >= n, STOP, p + 1),
           np.where(is_vertex(t), colour, STOP)))


# ============================================================================ verbose (strict)


def ff_verbose_step(seq, k=3):
    tok = tokens(seq)
    idx, prev, seen_semi, partner, ep, nmax = _prompt_parts(tok)
    boundary = tok_map(tok, lambda t: (t == I.SEMI) | (t == LINE_END))
    # index of the last boundary strictly before each position (start of the current line)
    lb = aggregate(select((idx, boundary), idx, lambda ki, kb, qi: (kb == 1) & (ki < qi)), idx, "max", default=-1)
    lb_here = aggregate(select((idx, boundary), idx, lambda ki, kb, qi: (kb == 1) & (ki <= qi)), idx, "max", default=-1)
    # the line's vertex = token just after the line start
    v = aggregate(select(idx, succ(lb_here, 1), lambda k_, q: k_ == q), tok, "max")
    v_at_end = aggregate(select(idx, succ(lb, 1), lambda k_, q: k_ == q), tok, "max")   # at LINE_END
    nbr = map_n(lambda t, p, s: is_vertex(t) & ((p == COLON) | is_colour(p)) & (s != 0), tok, prev, seen_semi)
    u_last = aggregate(select((idx, nbr), lb_here, lambda ki, kn, q: (kn == 1) & (ki > q)),
                       seq_map(tok, nbr, lambda t, n: t * (n != 0)), "max")
    # next earlier-coloured neighbour w of v with u_last < w < v (both edge directions)
    w1 = aggregate(select((partner, ep), (v, u_last), lambda kp, ke, qv, ql: (kp == qv) & (ke > ql) & (ke < qv) & (qv > 0)),
                   ep, "min", default=127)
    w2 = aggregate(select((ep, partner), (v, u_last), lambda ke, kp, qv, ql: (ke == qv) & (kp > ql) & (kp < qv) & (qv > 0)),
                   partner, "min", default=127)
    w = seq_map(w1, w2, np.minimum)
    # colour of a listed neighbour u: the colour token after ARROW in u's own line
    line_col = seq_map(prev, tok, lambda p, t: (p == ARROW) & is_colour(t))
    lv = seq_map(v, line_col, lambda a, c: np.where(c != 0, a, 0))
    col_of_tok = aggregate(select(lv, tok, lambda k_, q: (k_ == q) & (q > 0)), tok, "max")
    # mex of the colours listed in the current line
    present = [aggregate(select((idx, tok), lb_here, lambda ki, kt, q, c=c: (ki > q) & (kt == COL0 + c)),
                         full(tok, 1), "max") for c in range(1, k + 1)]
    mex = map_n(lambda *fs: COL0 + np.select([f == 0 for f in fs], list(range(1, k + 1)), k + 1), *present)
    return map_n(_verbose_next, tok, prev, v, v_at_end, nmax, w, col_of_tok, mex)


def _verbose_next(t, p, v, v_end, n, w, col, mex):
    in_list = (t == COLON) | (is_colour(t) & (p != ARROW))
    return np.where(t == I.SEMI, 1,
           np.where(t == LINE_END, np.where(v_end >= n, STOP, v_end + 1),
           np.where(is_vertex(t) & ((p == I.SEMI) | (p == LINE_END)), COLON,
           np.where(in_list, np.where(w < 127, w, ARROW),
           np.where(is_vertex(t), col,
           np.where(t == ARROW, mex,
           np.where(is_colour(t) & (p == ARROW), LINE_END, STOP)))))))


# ============================================================================ running


def run(step, prompt, max_new=400):
    seq = list(prompt)
    for _ in range(max_new):
        nxt = last(step(seq))
        seq.append(nxt)
        if nxt == STOP:
            break
    return seq[len(prompt):]


def decode_terse(out):
    return {out[i]: out[i + 1] - COL0 for i in range(0, len(out) - 1, 2) if is_vertex(out[i])}


def decode_verbose(out):
    col, cur = {}, None
    for i, t in enumerate(out):
        if is_vertex(t) and (i == 0 or out[i - 1] == LINE_END):
            cur = t
        if t == ARROW:
            col[cur] = out[i + 1] - COL0
    return col


# ---------------------------------------------------------------------------- Python members


def _adj(n, edges):
    adj = {v: set() for v in range(1, n + 1)}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def ref_first_fit(n, edges, order=None):
    adj, col = _adj(n, edges), {}
    for v in order or range(1, n + 1):
        used = {col[u] for u in adj[v] if u in col}
        c = 1
        while c in used:
            c += 1
        col[v] = c
    return col


def ref_random_order_ff(n, edges, rng=random):
    order = list(range(1, n + 1))
    rng.shuffle(order)
    return ref_first_fit(n, edges, order)


def ref_dsatur(n, edges):
    adj, col = _adj(n, edges), {}
    while len(col) < n:
        def key(v):
            return (len({col[u] for u in adj[v] if u in col}), len(adj[v]), -v)
        v = max((u for u in adj if u not in col), key=key)
        used = {col[u] for u in adj[v] if u in col}
        c = 1
        while c in used:
            c += 1
        col[v] = c
    return col


def ref_local(n, edges, t=2):
    """t synchronous rounds: every vertex takes the mex of its lower-id neighbours' colours.

    After t rounds this equals FIRST-FIT on vertices whose lower-id dependency chains are
    shorter than t (the depth-truncated, constant-depth version of FIRST-FIT)."""
    adj = _adj(n, edges)
    col = {v: 1 for v in adj}
    for _ in range(t):
        new = {}
        for v in adj:
            used = {col[u] for u in adj[v] if u < v}
            c = 1
            while c in used:
                c += 1
            new[v] = c
        col = new
    return col


def ref_random(n, edges, k=3, rng=random):
    return {v: rng.randint(1, k) for v in range(1, n + 1)}


def ref_min_conflicts(n, edges, k=3, steps=50, rng=random):
    adj = _adj(n, edges)
    col = ref_first_fit(n, edges)
    col = {v: min(c, k) for v, c in col.items()}
    for _ in range(steps):
        bad = [v for v in adj if any(col[u] == col[v] for u in adj[v])]
        if not bad:
            break
        v = rng.choice(bad)
        col[v] = min(range(1, k + 1), key=lambda c: (sum(col[u] == c for u in adj[v]), rng.random()))
    return col


def test_equivalence(trials=40, seed=1):
    rng = random.Random(seed)
    bad = 0
    for _ in range(trials):
        n = rng.randint(4, 9)
        edges = I.planted_colourable(n, 3, 0.5, rng)
        if not edges:
            continue
        prompt = I.colour_prompt(edges)
        n_eff = max((max(e) for e in edges), default=0)   # isolated top vertices are invisible
        ref = ref_first_fit(n_eff, edges)
        bad += decode_terse(run(ff_terse_step, prompt)) != ref
        bad += decode_verbose(run(ff_verbose_step, prompt)) != ref
    return bad


if __name__ == "__main__":
    print("FIRST-FIT equivalence failures:", test_equivalence())
    edges = I.planted_colourable(6, 3, 0.5, random.Random(3))
    prompt = I.colour_prompt(edges)
    out = run(ff_verbose_step, prompt)
    print("verbose trace:", out)
    print(measure("FF-terse-step (set ext.)", ff_terse_step, prompt + [1]))
    print(measure("FF-verbose-step", ff_verbose_step, prompt + [1, COLON]))
