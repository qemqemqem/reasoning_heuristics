"""Build the example library for the cross-formalism vertical (I_cross_formalism).

    python build_library.py OUT.jsonl SUMMARY.json

Needs: numpy, python-sat, tiktoken (o200k_base), pyetr==1.0.0 (E8 only).

Every ground truth is computed twice (backtracking enumeration and a SAT solver) and asserted equal.
Every member's prediction is computed on every encoding: natively where the member is defined on that
surface, otherwise by translating through the reduction ('transported'), flagged per cell.

Sign convention for likelihood ratios: positive log10 LR = evidence AGAINST that theory, relative to the
theory (member, or hypothesis H-*) that predicts the observation best.
"""
from __future__ import annotations

import json
import math
import random
import sys
from collections import Counter

from cf_core import (K, Instance, random_instance, colourings, canon, is_proper, cnf_encode, decode,
                     pysat_colourable, render_G, render_S, render_C, render_L, render_X, render_DIMACS,
                     pad_label, C_HINT, C_NEUTRAL, L_HINT, L_NEUTRAL, count_tokens, exam_names, vlabel)
import cf_members as M
import cf_other_bases as O

EPS = 0.10          # slip rate used for the library's illustrative likelihoods (deterministic members)
LR_REPORT = 0.3     # report log10 LR entries >= this (about 2:1)

# --------------------------------------------------------------------------------------------
# Member catalogue: name -> (family, home formalism)
# --------------------------------------------------------------------------------------------
FAMILY = {
    'FF-LIST': ('C1', 'graph'), 'FF-LIST-INFEAS': ('C1', 'graph'), 'FF-LABEL': ('C1', 'graph'), 'LF': ('C1', 'graph'),
    'DSATUR': ('C2', 'graph'), 'RO-FF': ('C3', 'graph'), 'DPLL-LIST': ('D', 'graph'), 'DPLL-DSATUR': ('D', 'graph'),
    'DPLL-LIST-b12': ('D', 'graph'), 'MIN-CONFLICTS': ('F', 'graph'), 'DROP-LAST-1': ('B1', 'graph'),
    'POLARITY': ('C0', 'cnf'), 'GREEDY-MENTION': ('C1', 'cnf'), 'UC-DET': ('C2', 'cnf'), 'UC-DET-INDEX': ('C2', 'cnf'),
    'GUC-DET': ('C2', 'cnf'), 'DPLL-MENTION': ('D', 'cnf'), 'DPLL-INDEX': ('D', 'cnf'), 'DPLL-OCC': ('D', 'cnf'),
    'DPLL-MENTION-b24': ('D', 'cnf'), 'WALK': ('F', 'cnf'),
    'FIRST': ('B4', 'logic'), 'BICOND': ('B4', 'logic'), 'ONL(1)': ('C4', 'logic'), 'ONL(64)': ('C4', 'logic'),
    'ETR': ('B4/C4', 'logic'),
    'EXACT': ('null', 'any'), 'ALWAYS-NO': ('A1', 'any'), 'ALWAYS-YES': ('A1', 'any'), 'RANDOM': ('H', 'any'),
    'PERCEPTION-NOISE': ('nuisance', 'any'),
    # MUST
    'WP-1': ('E/B1', 'graph'), 'WP-2': ('E/B1', 'graph'), 'WP-inf': ('E/B1', 'graph'),
    'UP-2': ('B1', 'cnf'), 'UP-3': ('B1', 'cnf'), 'UP-4': ('B1', 'cnf'), 'UP-inf': ('B1', 'cnf'),
    'FF-LIST-READ': ('C1', 'graph'), 'DSATUR-READ': ('C2', 'graph'), 'FF-CM': ('C1', 'graph'),
    'UC-READ': ('C2', 'cnf'), 'UC-CM': ('C2', 'cnf'), 'GREEDY-CM': ('C1', 'cnf'), 'SAMPLE-3': ('H', 'any'),
    'ONL(1)-reset': ('C4', 'logic'), 'ONL(8)-reset': ('C4', 'logic'),
}
GRAPH_TYPE = {'G', 'S', 'G-PAD'}
L_TYPE = {'L', 'L-HINT', 'L-NEUTRAL', 'L-XORD'}
C_TYPE = {'C', 'C-DIMACS', 'C-SCRAMBLE', 'C-HINT', 'C-NEUTRAL', 'X', 'C-XORD'}


def formalism_of(enc):
    return 'graph' if enc in GRAPH_TYPE else ('logic' if enc in L_TYPE else 'cnf')


def how(member, enc):
    home = FAMILY[member][1]
    if home == 'any':
        return 'native'
    f = formalism_of(enc)
    if home == f:
        return 'native'
    if home == 'cnf' and f == 'logic':
        return 'native'        # L is the clause list in English: clause-level members read it directly
    if home == 'logic' and f == 'cnf' and member in ('FIRST', 'ONL(1)', 'ONL(64)', 'ONL(1)-reset', 'ONL(8)-reset'):
        return 'native (clause form)'   # every CNF clause is a disjunction: computed on the C surface
    return 'transported'


# --------------------------------------------------------------------------------------------
# Reference profiles (pre-registered for ILLUSTRATION of item-level evidence only; the real test
# is the fitted mixture). Profiles are per formalism; hypotheses combine them (see doc §2.2).
# --------------------------------------------------------------------------------------------
PROF_FIND = {
    'graph': {'FF-LIST': .15, 'FF-LIST-INFEAS': .05, 'DPLL-LIST': .15, 'FF-LABEL': .05, 'DSATUR': .15, 'LF': .05,
              'MIN-CONFLICTS': .05, 'EXACT': .20, 'UC-DET': .03, 'GUC-DET': .02, 'DPLL-OCC': .02, 'POLARITY': .01,
              'FIRST': .01, 'RANDOM': .03, 'DROP-LAST-1': .03},
    'cnf': {'UC-DET': .15, 'GUC-DET': .10, 'DPLL-OCC': .05, 'DPLL-INDEX': .05, 'DPLL-MENTION': .15, 'WALK': .05,
            'POLARITY': .05, 'GREEDY-MENTION': .05, 'EXACT': .20, 'FF-LIST': .03, 'DSATUR': .03, 'LF': .02,
            'RANDOM': .03, 'DROP-LAST-1': .02, 'FF-LABEL': .02},
    'logic': {'UC-DET': .12, 'GUC-DET': .08, 'DPLL-OCC': .05, 'DPLL-INDEX': .05, 'DPLL-MENTION': .15, 'WALK': .05,
              'FIRST': .05, 'BICOND': .05, 'ONL(1)': .05, 'EXACT': .20, 'FF-LIST': .03, 'DSATUR': .03, 'LF': .02,
              'RANDOM': .03, 'DROP-LAST-1': .02, 'FF-LABEL': .02},
}
PROF_MUST = {
    'graph': {'EXACT': .40, 'WP-inf': .15, 'WP-1': .05, 'FF-LIST-READ': .12, 'DSATUR-READ': .05, 'FF-CM': .05,
              'SAMPLE-3': .08, 'ALWAYS-YES': .04, 'ALWAYS-NO': .03, 'FIRST': .03},
    'cnf': {'EXACT': .35, 'UP-inf': .20, 'UP-2': .05, 'UC-READ': .10, 'UC-CM': .05, 'GREEDY-CM': .07, 'SAMPLE-3': .05,
            'ALWAYS-YES': .03, 'ALWAYS-NO': .03, 'FIRST': .05, 'FF-LIST-READ': .02},
    'logic': {'EXACT': .35, 'UP-inf': .15, 'UP-2': .05, 'UC-READ': .08, 'ONL(1)-reset': .07, 'GREEDY-CM': .05,
              'SAMPLE-3': .08, 'ALWAYS-YES': .04, 'ALWAYS-NO': .03, 'FIRST': .04, 'BICOND': .04, 'FF-LIST-READ': .02},
}
TAU = {'C': .6, 'L': .6, 'X': .9, 'C-DIMACS': .6, 'C-SCRAMBLE': .3, 'C-NEUTRAL': .6, 'C-HINT': .95,
       'L-HINT': .95, 'L-NEUTRAL': .6, 'C-XORD': .6, 'L-XORD': .6}
SURFACE = {'G': 'sym', 'C': 'sym', 'X': 'sym', 'G-PAD': 'sym', 'C-DIMACS': 'sym', 'C-SCRAMBLE': 'sym', 'C-HINT': 'sym',
           'C-NEUTRAL': 'sym', 'C-XORD': 'sym', 'S': 'nl', 'L': 'nl', 'L-HINT': 'nl', 'L-NEUTRAL': 'nl', 'L-XORD': 'nl'}


def mix(a, b, w):
    keys = set(a) | set(b)
    return {k: w * a.get(k, 0) + (1 - w) * b.get(k, 0) for k in keys}


def h_profiles(enc, prof, tok_ratio):
    """Return {H: (profile, slip)} for an encoding. tok_ratio = tokens(enc) / tokens(G of the same instance)."""
    f = formalism_of(enc)
    out = {
        'H-structure': (prof['graph'], EPS),
        'H-formalism': (prof[f], EPS),
        'H-translate': (prof['graph'] if f == 'graph' else mix(prof['graph'], prof[f], TAU.get(enc, .6)), EPS),
        'H-length': (prof['graph'], min(0.4, EPS * tok_ratio)),
        'H-surface': (prof['graph'] if SURFACE.get(enc, 'sym') == 'sym' else prof['logic'], EPS),
    }
    return out


# --------------------------------------------------------------------------------------------
# Rendering per encoding
# --------------------------------------------------------------------------------------------

def encoding_cnf(inst, enc, xord=None, perm=None):
    if enc in ('C-XORD', 'L-XORD'):
        pos = {v: i for i, v in enumerate(xord)}
        eo = sorted(inst.edges, key=lambda e: tuple(sorted((pos[e[0]], pos[e[1]]))))
        return cnf_encode(inst, vertex_order=xord, edge_order=eo)
    if enc == 'C-SCRAMBLE':
        return cnf_encode(inst, index_perm=perm)
    return cnf_encode(inst)


def render(inst, enc, task, query=None, cnf=None, pad_words=None):
    if enc == 'G':
        return render_G(inst, task, query)
    if enc == 'G-PAD':
        return render_G(inst, task, query, labels=[pad_label(inst, v, pad_words) for v in range(inst.n)])
    if enc == 'S':
        return render_S(inst, task, query)
    if enc in ('C', 'C-SCRAMBLE', 'C-XORD'):
        return render_C(inst, task, query, cnf=cnf)
    if enc == 'C-HINT':
        return render_C(inst, task, query, cnf=cnf, header=C_HINT)
    if enc == 'C-NEUTRAL':
        return render_C(inst, task, query, cnf=cnf, header=C_NEUTRAL)
    if enc == 'C-DIMACS':
        return render_DIMACS(inst, task, query, cnf=cnf)
    if enc == 'X':
        return render_X(inst, task, query, cnf=cnf)
    if enc in ('L', 'L-XORD'):
        return render_L(inst, task, query, cnf=cnf)
    if enc == 'L-HINT':
        return render_L(inst, task, query, cnf=cnf, header=L_HINT)
    if enc == 'L-NEUTRAL':
        return render_L(inst, task, query, cnf=cnf, header=L_NEUTRAL)
    raise ValueError(enc)


def n_statements(inst, enc, cnf):
    return len(inst.edges) + len(inst.pre) if enc in GRAPH_TYPE else len(cnf.clauses)


def answer_text(inst, enc, col, cnf):
    """The expected answer block in the encoding's own format (for a canonical colouring)."""
    if col is None:
        return {'G': 'IMPOSSIBLE', 'G-PAD': 'IMPOSSIBLE', 'S': 'IMPOSSIBLE'}.get(enc, 'NO' if enc in L_TYPE else 'UNSAT')
    if enc in ('G', 'G-PAD'):
        return "; ".join(f"{vlabel(inst, v)}: {col[v]}" for v in range(inst.n))
    if enc in ('S',) or enc in L_TYPE:
        ex = exam_names(inst)
        return "; ".join(f"{ex[v]}: {col[v]}" for v in range(inst.n))
    tv = sorted(cnf.var_of[(v, col[v])] for v in range(inst.n))
    if enc == 'X':
        return " ".join(f"{vlabel(inst, cnf.vc_of[i][0])}.{cnf.vc_of[i][1]}" for i in tv)
    if enc == 'C-DIMACS':
        return " ".join(str(i) for i in tv)
    w = 2 if cnf.nvars < 100 else 3
    return " ".join(f"x{i:0{w}d}" for i in tv)


# --------------------------------------------------------------------------------------------
# Colouring members: predictions per encoding (canonical answers)
# --------------------------------------------------------------------------------------------

def canon_of(inst, cnf, ans):
    """Member answer -> canonical: 'IMPOSSIBLE' | ('VALID', partition) | ('INVALID', colouring)."""
    if ans[0] == 'IMP':
        return 'IMPOSSIBLE'
    if ans[0] == 'COL':
        col = ans[1]
    else:
        col, _ = decode(cnf, inst, ans[1])
    if is_proper(inst, col):
        return ('VALID', canon(col) if not inst.pre else col)
    return ('INVALID', col)


def find_predictions(inst, enc, cnf_e, dist_cache, xord=None):
    """All FIND/DECIDE members on one encoding. cnf_e = this encoding's CNF (its clause order /
    variable names); graph-native members use the encoding's induced vertex order."""
    canon_cnf = cnf_encode(inst)
    lst = xord if (enc in ('C-XORD', 'L-XORD')) else inst.listing_order()
    lab = inst.label_order()
    native_cnf = cnf_e if enc not in GRAPH_TYPE else canon_cnf
    form = 'C' if enc in C_TYPE else 'L'
    mo = M.mention_order(native_cnf)
    idx_order = sorted(native_cnf.vc_of)
    P = {}
    P['FF-LIST'] = M.ff(inst, lst, 'ABORT')
    P['FF-LIST-INFEAS'] = M.ff(inst, lst, 'INFEAS')
    P['FF-LABEL'] = M.ff(inst, lab, 'ABORT')
    P['LF'] = M.ff(inst, M.lf_order(inst), 'ABORT')
    P['DSATUR'] = M.dsatur(inst, 'ABORT')
    sub = Instance(inst.n, inst.edges, inst.labels, inst.pre, inst.seed)
    if lst != inst.listing_order():   # DPLL-LIST in the encoding's own vertex order
        P['DPLL-LIST'] = _dpll_order(inst, lst)
        P['DPLL-LIST-b12'] = _dpll_order(inst, lst, budget=12)
    else:
        P['DPLL-LIST'] = M.dpll_graph(sub, 'list')[0]
        P['DPLL-LIST-b12'] = M.dpll_graph(sub, 'list', budget=12)[0]
    P['DPLL-DSATUR'] = M.dpll_graph(sub, 'dsatur')[0]
    if lst != inst.listing_order():   # crossed order: the last statement is the last edge in this encoding's order
        pos = {v: i for i, v in enumerate(lst)}
        eo = sorted(inst.edges, key=lambda e: tuple(sorted((pos[e[0]], pos[e[1]]))))
        P['DROP-LAST-1'] = _dpll_order(Instance(inst.n, eo[:-1], inst.labels, inst.pre, inst.seed), lst)
    else:
        P['DROP-LAST-1'] = M.drop_last_edges(inst, 1)
    P['POLARITY'] = M.polarity(native_cnf)
    P['GREEDY-MENTION'] = M.greedy(native_cnf, mo)
    P['UC-DET'] = M.uc_det(native_cnf, mo)
    P['UC-DET-INDEX'] = M.uc_det(native_cnf, idx_order)
    P['GUC-DET'] = M.guc_det(native_cnf)
    P['DPLL-MENTION'] = M.dpll_cnf(native_cnf, 'MENTION')[0]
    P['DPLL-INDEX'] = M.dpll_cnf(native_cnf, 'INDEX')[0]
    P['DPLL-OCC'] = M.dpll_cnf(native_cnf, 'OCC')[0]
    P['DPLL-MENTION-b24'] = M.dpll_cnf(native_cnf, 'MENTION', budget=24)[0]
    lcnf = native_cnf
    P['FIRST'] = M.first_member(lcnf, form=('C' if enc in C_TYPE else 'L'))
    P['BICOND'] = M.bicond_member(cnf_e if enc in L_TYPE else (cnf_encode(inst, vertex_order=lst) if enc in C_TYPE else canon_cnf))
    P['ONL(1)'] = M.onl_answer_find(lcnf, inst, 1, 'strict', form=form)
    P['ONL(64)'] = M.onl_answer_find(lcnf, inst, 64, 'strict', form=form)
    out = {}
    for name, ans in P.items():
        cnf_for_decode = native_cnf if FAMILY[name][1] in ('cnf', 'logic') else canon_cnf
        if name == 'BICOND':
            cnf_for_decode = cnf_e if enc in L_TYPE else (cnf_encode(inst, vertex_order=lst) if enc in C_TYPE else canon_cnf)
        out[name] = canon_of(inst, cnf_for_decode, ans)
    out['ETR'] = 'n/c'
    if enc == 'C-SCRAMBLE':
        out['FF-LABEL'] = 'n.a.'   # no label order on this surface: variable numbers are permuted
    out['ALWAYS-NO'] = 'IMPOSSIBLE'
    out['EXACT'] = 'UNIFORM-VALID'
    out['RANDOM'] = 'UNIFORM'
    for k in ('RO-FF', 'MIN-CONFLICTS', 'WALK'):
        out[k] = 'DIST'
    return out


def _dpll_order(inst, order, budget=None):
    """DPLL-LIST in an arbitrary vertex order: relabel vertices so `order` becomes 0..n-1."""
    pos = {v: i for i, v in enumerate(order)}
    edges = sorted(tuple(sorted((pos[u], pos[v]))) for u, v in inst.edges)
    sub = Instance(inst.n, edges, [inst.labels[v] for v in order], {pos[v]: c for v, c in inst.pre.items()}, inst.seed)
    ans, _ = M.dpll_graph(sub, 'list', budget=budget)
    if ans[0] == 'IMP':
        return ans
    col = [0] * inst.n
    for v in range(inst.n):
        col[v] = ans[1][pos[v]]
    return ('COL', tuple(col))


def distributions(inst, cnf):
    return {'RO-FF': M.ro_ff_dist(inst, runs=2000, seed=inst.seed),
            'MIN-CONFLICTS': M.min_conflicts_dist(inst, runs=300, seed=inst.seed),
            'WALK': M.walk_dist(cnf, inst, runs=200, seed=inst.seed)}


# --------------------------------------------------------------------------------------------
# Observation classes and likelihoods (FIND: partition-level; DECIDE: decision-level)
# --------------------------------------------------------------------------------------------

def label_count(part):
    j = len(set(part))
    return math.perm(K, j)


def find_classes(inst, preds, sols):
    parts = sorted({canon(s) for s in sols})
    named = []
    for name, p in preds.items():
        if isinstance(p, tuple) and p[0] == 'VALID' and p[1] not in named:
            named.append(p[1])
    return parts, named


def classify(inst, col, named, colourable):
    if col == 'IMPOSSIBLE':
        return 'IMPOSSIBLE'
    if is_proper(inst, col):
        c = canon(col)
        return ('FP', named.index(c)) if c in named else 'OTHER-VALID'
    return 'INVALID'


def kernel(inst, col, named, colourable):
    out = Counter()
    nb = [(v, c) for v in range(inst.n) if v not in inst.pre for c in range(1, K + 1) if c != col[v]]
    for v, c in nb:
        new = list(col)
        new[v] = c
        out[classify(inst, tuple(new), named, colourable)] += 1 / len(nb)
    return out


def member_probs_find(inst, preds, sols, dists, named, parts, eps=EPS):
    colourable = bool(sols)
    sol_by_part = {}
    for s in sols:
        sol_by_part.setdefault(canon(s), s)
    def valid_uniform():
        c = Counter()
        for p in parts:
            c[('FP', named.index(p)) if p in named else 'OTHER-VALID'] += 1 / len(parts)
        return c
    imp_slip = valid_uniform() if colourable else Counter({'INVALID': 1.0})
    exact_slip = Counter()
    for p in parts:
        for k2, v in kernel(inst, sol_by_part[p], named, colourable).items():
            exact_slip[k2] += v / len(parts)
    probs = {}
    for name, p in preds.items():
        c = Counter()
        if p in ('n/c', 'n.a.'):
            continue
        if p == 'IMPOSSIBLE':
            c['IMPOSSIBLE'] += 1 - eps
            for k2, v in imp_slip.items():
                c[k2] += eps * v
        elif p == 'UNIFORM-VALID':
            if colourable:
                for k2, v in valid_uniform().items():
                    c[k2] += (1 - eps) * v
                for k2, v in exact_slip.items():
                    c[k2] += eps * v
            else:
                c['IMPOSSIBLE'] += 1 - eps
                c['INVALID'] += eps
        elif p == 'UNIFORM':
            c['IMPOSSIBLE'] += 0.5
            tot = 3 ** inst.n
            nvalid_lab = len(sols)
            for i, part in enumerate(named):
                c[('FP', i)] += 0.5 * label_count(part) / tot
            c['OTHER-VALID'] += 0.5 * (nvalid_lab - sum(label_count(q) for q in named)) / tot
            c['INVALID'] += 0.5 * (1 - nvalid_lab / tot)
        elif p == 'DIST':
            d = dists[name]
            for key, v in d.items():
                if key == ('IMP',):
                    c['IMPOSSIBLE'] += v
                elif key == ('INVALID',):
                    c['INVALID'] += v
                else:
                    c[('FP', named.index(key)) if key in named else 'OTHER-VALID'] += v
        else:
            kind, col = p
            if kind == 'VALID':
                own = ('FP', named.index(col)) if col in named else 'OTHER-VALID'
                rep = sol_by_part.get(col, col)
            else:
                own, rep = 'INVALID', col
            c[own] += 1 - eps
            for k2, v in kernel(inst, rep, named, colourable).items():
                c[k2] += eps * v
        probs[name] = c
    return probs


def to_decision(c):
    out = Counter()
    for k2, v in c.items():
        out['IMPOSSIBLE' if k2 == 'IMPOSSIBLE' else ('INVALID' if k2 == 'INVALID' else 'VALID')] += v
    return out


def lr_table(obs_classes, member_probs, h_probs):
    """disconfirms: obs -> {theory: log10 LR}, positive = evidence against the theory."""
    out = {}
    for o in obs_classes:
        row = {}
        pm = {h: max(p.get(o, 0), 1e-6) for h, p in member_probs.items()}
        best = max(pm.values())
        for h, v in sorted(pm.items(), key=lambda kv: kv[1]):
            lr = math.log10(best / v)
            if lr >= LR_REPORT:
                row[h] = round(lr, 2)
        ph = {h: max(p.get(o, 0), 1e-6) for h, p in h_probs.items()}
        bh = max(ph.values())
        for h, v in ph.items():
            row[h] = round(math.log10(bh / v), 2)
        out[o] = row
    return out


def h_class_probs(member_probs, prof_by_enc, enc, tok_ratio, item_probs_fn):
    out = {}
    for H, (prof, slip) in h_profiles(enc, prof_by_enc, tok_ratio).items():
        mp = item_probs_fn(slip) if slip != EPS else member_probs
        tot = Counter()
        z = sum(w for h, w in prof.items() if h in mp)
        for h, w in prof.items():
            if h in mp:
                for k2, v in mp[h].items():
                    tot[k2] += w / z * v
        out[H] = tot
    return out


def obs_name(o, named_desc=None):
    if isinstance(o, tuple) and o[0] == 'FP':
        return f"answer = fingerprint #{o[1]}" + (f" ({named_desc[o[1]]})" if named_desc else "")
    return {'IMPOSSIBLE': 'IMPOSSIBLE / UNSAT / NO', 'OTHER-VALID': 'another valid colouring (no member predicts it)',
            'INVALID': 'an invalid colouring', 'VALID': 'a valid colouring', 'YES': 'YES', 'NO': 'NO'}.get(o, str(o))


# --------------------------------------------------------------------------------------------
# Trace and hypothesis text
# --------------------------------------------------------------------------------------------
TRACE_FIND = {
    'FF-LIST': "K1 commits vertices in the encoding's listing / first-mention order; colour = smallest not used by an earlier neighbour; 0 revisions; K5 dead end -> IMPOSSIBLE without revision",
    'FF-LABEL': "K1 commit order follows label order (numeric labels in G; alphabetical exam names in S/L; variable index in C)",
    'LF': "K3 degree mentions; commit order = degree descending",
    'DSATUR': "K3 'most constrained' / 'fewest options left' mentions; next vertex = max saturation given the trace state",
    'DPLL-LIST': "K1 in listing order plus chronological backtracking (K4) at dead ends; K10 case splits",
    'UC-DET': "Forced moves first ('x07 must be false because clause 31', 'Botany can only be slot 3'), otherwise next variable in mention order set true; 0 revisions",
    'GUC-DET': "Picks the shortest open clause / statement next and satisfies its first literal; no backtracking",
    'DPLL-OCC': "Branches first on the most frequent variable (highest-degree vertex), with propagation and backtracking",
    'POLARITY': "Counts positive vs negative occurrences per variable; sets almost every variable false; reports UNSAT",
    'GREEDY-MENTION': "Variable-by-variable counts of open clauses; sets variables false; reports UNSAT at a falsified 'at least one' clause",
    'FIRST': "K3 COMMIT: reads 'in slot 1, slot 2 or slot 3' as slot 1 for every exam; then finds a contradiction",
    'BICOND': "K5 CONVERSE: uses 'if A is not in slot c then B is' (the converse of a conflict rule)",
    'ONL(1)': "K7 premise-by-premise in presentation order with one scenario kept; K9 contradiction at the first conflict rule",
    'EXACT': "Systematic search or propagation with backtracking; answer is any valid colouring",
    'MIN-CONFLICTS': "A full guess first, then repeated local repairs anywhere",
    'WALK': "A full assignment first, then repeated variable flips in falsified clauses",
}
TRACE_H = {
    'H-structure': "Trace content tracks the constraint structure; commitment pattern (mapped to the canonical instance) is the same member's as in the other encodings of this set; no particular vocabulary required.",
    'H-formalism': "Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).",
    'H-translate': "TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back.",
    'H-length': "No translation needed; K11 misquoted or dropped constraints rise with prompt length at the same per-statement rate in every encoding.",
    'H-surface': "Same trace profile for the two natural-language encodings (S, L) and for the two symbolic ones (G, C), whatever the formalism.",
}


def h_blocks(eval_id, enc, extra=None):
    """Item-level statements of every hypothesis: output, eval-level pre-registered threshold, CoT."""
    f = formalism_of(enc)
    pre = PREREG[eval_id]
    out = {}
    for H in ('H-structure', 'H-formalism', 'H-translate', 'H-length', 'H-surface'):
        out[H] = {'output': (extra or {}).get(H, OUTPUT_H[H].format(f=f, enc=enc, tau=TAU.get(enc, 'n/a'))),
                  'eval_prediction': pre[H],
                  'cot_prediction': TRACE_H[H]}
    return out


OUTPUT_H = {
    'H-structure': "Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.",
    'H-formalism': "Answer distribution = the {f} reference profile's: members whose home formalism is '{f}' carry extra weight here.",
    'H-translate': "Answer distribution = tau * graph profile + (1 - tau) * {f} profile, tau = {tau} for {enc} (translation rate; measured from traces in the real run).",
    'H-length': "Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).",
    'H-surface': "Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.",
}

PREREG = {
    'E1': {
        'H-structure': "Pooled over E1: every |Δπ_h(e, G)| 90% interval within ±0.05 (TOST); omnibus shared-π vs encoding-specific-π: ΔELPD < 2 SE and parametric-bootstrap LRT p > .05; cross-encoding / retest agreement ratio R >= 0.9.",
        'H-formalism': "Home-advantage index HAI >= 0.10 (lower 95% > 0.05), using only components identifiable on E1 items: graph-home DSATUR (= DPLL-DSATUR) and LF weight higher on G/S than C/L; CNF/logic-home GUC-DET, DPLL-OCC and the collapse members (POLARITY, GREEDY, FIRST, BICOND, ONL; answer IMPOSSIBLE) higher on C/L than G/S; R <= 0.8.",
        'H-translate': "Translation rate tau_C, tau_L >= 0.5 (κ-corrected); weight on graph-home members in translated C/L traces exceeds untranslated ones by >= 0.20; π on C/L lies on the segment between the C/L-home and G profiles.",
        'H-length': "Valid-answer fingerprint distributions equal across encodings (total-variation distance <= 0.05); accuracy differences fully absorbed by length-dependent slip (see E2).",
        'H-surface': "Δπ(S − G) and Δπ(L − C) equal and non-zero (>= 0.10); Δπ(C − G) and Δπ(L − S) within ±0.05.",
    },
    'E2': {
        'H-structure': "G-PAD, X and C-DIMACS have the same π as G and C (all |Δπ| within ±0.05).",
        'H-formalism': "Δπ(G → G-PAD) within ±0.05 (tokens alone change nothing); Δπ(G → X) >= 0.10 toward CNF-home members; Δπ(X → C) within ±0.05.",
        'H-translate': "X behaves like G (transparent atoms are translated: tau_X >= 0.8); C-DIMACS like C.",
        'H-length': "Δπ and accuracy change G → G-PAD >= 80% of the G → C change; C-DIMACS (fewer tokens) is closer to G than C is.",
        'H-surface': "All five encodings here are symbolic: no differences beyond ±0.05.",
    },
    'E3': {
        'H-structure': "No dial effect: π on C-SCRAMBLE, C-NEUTRAL, C-HINT, L-NEUTRAL, L-HINT all within ±0.05 of G.",
        'H-formalism': "No dial effect, but all C/L arms differ from G by HAI >= 0.10; HINT − NEUTRAL within ±0.05.",
        'H-translate': "Monotone dial: graph-home weight SCRAMBLE < NEUTRAL < HINT, with Δπ(HINT − SCRAMBLE) >= 0.10 and the change in tau predicting the change in π (slope 0.5–2 of the predicted).",
        'H-length': "HINT and NEUTRAL (token-matched) equal; SCRAMBLE equal to C (same tokens).",
        'H-surface': "C-arms and L-arms differ by the same surface shift as in E1; no dial effect.",
    },
    'E4': {
        'H-structure': "Cell contrasts (a1 − b), (a2 − a1), (c-twin − b) and the collapse rate in cell b equal across encodings (each Δ within ±0.05) once every member's native prediction is applied.",
        'H-formalism': "Collapse rate (false IMPOSSIBLE in cell b, where no constructive member fails) >= 0.10 on C/L and <= 0.03 on G/S; the first-fit dead-end contrast (a1 − b) larger on G/S than on C/L by >= 0.10 (first-fit is graph-home; unit propagation rescues a1 on C/L).",
        'H-translate': "C/L cell pattern = tau·(G/S pattern) + (1 − tau)·(C/L-home pattern), tau from traces; collapse answers come from untranslated traces (odds ratio >= 2).",
        'H-length': "Error rates rise with tokens in every cell by the same amount: no cell × encoding interaction beyond PERCEPTION-NOISE's computed one (cell c: false 'possible' 0.09 on G/S vs 0.34 on C/L at a 3% per-statement drop rate).",
        'H-surface': "Cell pattern shared within {S, L} and within {G, C}.",
    },
    'E5': {
        'H-structure': "Omission share (propagation only: NO on F-CASE) and commission share (single-model or counter-model construction: YES on NF-READ and F-CASE-twin) equal across encodings (±0.05); fitted propagation depth equal in graph hops (WP-t on G/S matches UP-2t on C/L).",
        'H-formalism': "Omission share higher on L and C than on G/S by >= 0.10 (deriving consequences is the home move in logic); commission share higher on G/S by >= 0.10 (building a colouring is the home move for graphs); fitted propagation depth equal in statement rounds (UP-k on C/L with k ≈ t on G/S, i.e. half the graph depth).",
        'H-translate': "C/L traces that translate (TR1/TR2) show the G/S split; untranslated ones show the C/L-home split.",
        'H-length': "Accuracy falls with tokens through symmetric slips; the omission / commission split is unchanged.",
        'H-surface': "Split shared within {S, L} and within {G, C}.",
    },
    'E6': {
        'H-structure': "Cross-encoding agreement drops from E1's matched-order level by exactly the predicted amount Σ_h π_h·(1 − agreement of h across the two orders) (95% interval of observed − predicted includes 0).",
        'H-formalism': "As H-structure for order-dependent members (order is read from each encoding's own surface); a larger drop indicates more weight moving between members.",
        'H-translate': "Translated traces rebuild the graph in the encoding's own first-mention order (π'); fingerprints follow π', not G's π_L.",
        'H-length': "Same as matched order: crossing order changes no length feature.",
        'H-surface': "No specific prediction.",
    },
    'E7': {
        'H-structure': "PICK-FIRST, UC-DET and GREEDY weights equal across C, L-SW and G-GROUP (±0.05).",
        'H-formalism': "Graph rendering raises PICK-FIRST / MCG weight (false NO in r1) and lowers UC-DET / GREEDY weight (false NO in r2) by >= 0.10 each.",
        'H-translate': "If the canonical target is graph: C/L-SW traces translate to the group graph (unlikely); if it is SAT: G-GROUP traces translate to clauses (TR1 'one literal per clause'), and G-GROUP π moves to the C profile.",
        'H-length': "G-GROUP is the longest encoding here, so it should be the least accurate; if formalism (not length) drove E1, G-GROUP should instead look like G in E1.",
        'H-surface': "L-SW (NL) differs from C and G-GROUP (symbolic) by the E1 surface shift.",
    },
    'E8': {
        'H-structure': "L-CNF and C (identical member predictions, computed) give the same answers within ±0.05 per cell; the L-DNF → L-CNF change equals Σ_h π_h·Δ_h from the computed member changes (MATCH-L/A, PRIMACY, ETR and ONL(2) are representation-bound here; FIRST is not).",
        'H-formalism': "Weights equal on L-DNF and L-CNF (both English logic); B4 weights (FIRST, MATCH, ETR, ONL) lower on C than on L-CNF by >= 0.10, a pure weight shift. A form-bound variant (the logical form selects) instead predicts a FIRST-pattern drop already from L-DNF to L-CNF.",
        'H-translate': "C traces re-express the clauses as cases or as English statements (TR1) and then follow the L-CNF profile.",
        'H-length': "Tokens differ little here (92–122); no difference predicted beyond slips.",
        'H-surface': "Same prediction as H-formalism on this set (L-DNF, L-CNF English; C symbolic): E8 does not separate them; the E1 2 × 2 does.",
    },
}


# --------------------------------------------------------------------------------------------
# Item assembly helpers
# --------------------------------------------------------------------------------------------

def tok_info(prompt):
    return count_tokens(prompt)


def pred_record(inst, enc, name, can, cnf_e):
    rec = {'family': FAMILY[name][0], 'home': FAMILY[name][1],
           'how': {'n/c': 'n/c (PyETR times out at n >= 6)', 'n.a.': 'n.a. (no label order on this surface)'}.get(can, how(name, enc)) if isinstance(can, str) else how(name, enc)}
    if isinstance(can, tuple):
        kind, col = can
        rec['canonical'] = {'kind': kind, 'colouring': list(col)}
        if kind == 'VALID':
            rec['answer_text'] = answer_text(inst, enc, _labelled(inst, col), cnf_e)
    else:
        rec['canonical'] = can
    return rec


def _labelled(inst, part):
    return tuple(part)


def jsonable_key(o):
    if isinstance(o, tuple):
        return f"fingerprint#{o[1]}"
    return o


# --------------------------------------------------------------------------------------------
# E1 / E2 / E3 / E6: FIND sets on colouring bases
# --------------------------------------------------------------------------------------------

def find_e1_bases(count, n=12, m=18, seed0=20000, require_ff=True):
    bases = []
    seed = seed0
    while len(bases) < count:
        seed += 1
        inst = random_instance(n, m, seed)
        sols = colourings(inst)
        if not sols or len({canon(s) for s in sols}) < 20:
            continue
        cnf = cnf_encode(inst)
        dec = lambda a: canon_of(inst, cnf, a)
        fp = {'LIST': dec(M.dpll_graph(inst, 'list')[0]), 'LABEL': dec(M.dpll_cnf(cnf, 'INDEX')[0]),
              'DSATUR': dec(M.dsatur(inst)), 'LF': dec(M.ff(inst, M.lf_order(inst))), 'GUC': dec(M.guc_det(cnf)),
              'OCC': dec(M.dpll_cnf(cnf, 'OCC')[0])}
        vals = list(fp.values())
        if not all(isinstance(v, tuple) and v[0] == 'VALID' for v in vals) or len({v[1] for v in vals}) != 6:
            continue
        if require_ff and (M.ff(inst, range(n))[0] == 'IMP' or M.ff(inst, inst.label_order())[0] == 'IMP'
                           or M.uc_det(cnf, M.mention_order(cnf))[0] == 'IMP'):
            continue
        bases.append((inst, sols, seed - seed0))
    return bases


def verify_colouring_truth(inst, sols):
    ok, col = pysat_colourable(inst)
    assert ok == bool(sols), 'solver disagreement'
    if ok:
        assert is_proper(inst, col)
    return {'colourable': ok, 'n_colourings': len(sols), 'n_partitions': len({canon(s) for s in sols}) if not inst.pre else len(sols),
            'verified_by': ['backtracking enumeration of all colourings', 'PySAT Glucose4 on the direct CNF encoding'],
            'check': 'any proper 3-colouring is correct' if ok else 'IMPOSSIBLE is correct'}


def build_find_items(eval_id, set_id, pair_id, inst, sols, encs, cell, extra_params=None, xord=None, perm=None, task='FIND'):
    items = []
    cnf0 = cnf_encode(inst)
    gprompt, _ = render(inst, 'G', task)
    tok_G = tok_info(gprompt)
    ctok = tok_info(render(inst, 'C', task)[0])
    pad_words = min(range(1, 14), key=lambda w: abs(tok_info(render(inst, 'G-PAD', task, pad_words=w)[0]) - ctok))
    dists = distributions(inst, cnf0)
    truth = verify_colouring_truth(inst, sols)
    parts = sorted({canon(s) for s in sols})
    for enc in encs:
        cnf_e = encoding_cnf(inst, enc, xord=xord, perm=perm) if enc not in GRAPH_TYPE else cnf0
        prompt, fmt = render(inst, enc, task, cnf=cnf_e, pad_words=pad_words)
        tok = tok_info(prompt)
        preds = find_predictions(inst, enc, cnf_e, dists, xord=xord)
        _, named = find_classes(inst, preds, sols)
        mprobs = member_probs_find(inst, preds, sols, dists, named, parts)
        fn = lambda slip: member_probs_find(inst, preds, sols, dists, named, parts, eps=slip)
        hprobs = h_class_probs(mprobs, PROF_FIND, enc, tok / tok_G, fn)
        if task == 'DECIDE':
            mprobs_d = {h: to_decision(c) for h, c in mprobs.items()}
            hprobs_d = {h: to_decision(c) for h, c in hprobs.items()}
            obs = ['VALID', 'INVALID', 'IMPOSSIBLE']
            disc = lr_table(obs, mprobs_d, hprobs_d)
        else:
            obs = [('FP', i) for i in range(len(named))] + ['OTHER-VALID', 'INVALID', 'IMPOSSIBLE']
            disc = lr_table(obs, mprobs, hprobs)
        fp_members = {i: sorted(n for n, p in preds.items() if isinstance(p, tuple) and p[0] == 'VALID' and p[1] == part)
                      for i, part in enumerate(named)}
        predictions = {name: pred_record(inst, enc, name, can, cnf_e) for name, can in preds.items()}
        trace = {name: TRACE_FIND[name] for name in TRACE_FIND}
        params = {'n': inst.n, 'm': len(inst.edges), 'k': K, 'seed': inst.seed, 'labels': inst.labels,
                  'edges': inst.edges, 'precolouring': inst.pre, 'encoding_formalism': formalism_of(enc),
                  'surface': SURFACE.get(enc), 'prompt_tokens_o200k': tok, 'tokens_ratio_to_G': round(tok / tok_G, 2),
                  'n_statements': n_statements(inst, enc, cnf_e), 'n_atoms': inst.n if enc in GRAPH_TYPE else cnf_e.nvars,
                  'fingerprints': {f"#{i}": {'colouring': list(named[i]), 'members': fp_members[i]} for i in range(len(named))},
                  'order': 'crossed (pi_L\')' if enc in ('C-XORD', 'L-XORD') else 'matched (pi_L, lambda)'}
        if enc == 'G-PAD':
            params['pad_words_per_label'] = pad_words
        if extra_params:
            params.update(extra_params)
        hyp = h_blocks(eval_id, enc)
        hyp['members_diagnostic_here'] = {f"#{i}": fp_members[i] for i in fp_members}
        items.append({
            'eval_id': eval_id, 'set_id': set_id, 'pair_id': pair_id, 'cell': cell, 'encoding': enc,
            'domain': 'colouring (k = 3)', 'framing': {'G': 'textbook graph', 'S': 'story: exam timetable', 'G-PAD': 'textbook graph, long labels'}.get(enc, 'logic (exam/slot atoms)' if enc in L_TYPE else 'CNF'),
            'prompt': prompt, 'answer_format': fmt, 'ground_truth': truth, 'predictions': predictions,
            'trace_predictions': {'members': trace, 'hypotheses': TRACE_H},
            'params': params, 'hypotheses': hyp,
            'disconfirms': {obs_name(o, None) if not isinstance(o, tuple) else f"answer = fingerprint #{o[1]} ({', '.join(fp_members[o[1]][:4])}{'…' if len(fp_members[o[1]]) > 4 else ''})": v for o, v in disc.items()},
            '_hprobs': {H: {jsonable_key(k2): round(v, 4) for k2, v in (to_decision(c) if task == 'DECIDE' else c).items()} for H, c in hprobs.items()},
            'notes': '',
        })
    return items


# --------------------------------------------------------------------------------------------
# E4: DECIDE cells
# --------------------------------------------------------------------------------------------

def find_e4_cells(n=12, seed0=50000):
    want = {'a1': None, 'a2': None, 'b': None, 'c': None}
    seed = seed0
    while any(v is None for v in want.values()):
        seed += 1
        m = random.Random(seed).choice([22, 24, 26])
        inst = random_instance(n, m, seed)
        sols = colourings(inst)
        cnf = cnf_encode(inst)
        mo = M.mention_order(cnf)
        if sols:
            f = M.ff(inst, range(n))[0] != 'IMP'
            u = M.uc_det(cnf, mo)[0] != 'IMP'
            d = M.dsatur(inst)[0] != 'IMP'
            if not f and u and d and want['a1'] is None:
                want['a1'] = (inst, sols)
            elif not f and not u and d and want['a2'] is None:
                want['a2'] = (inst, sols)
            elif f and u and d and want['b'] is None and len(sols) >= 6:
                want['b'] = (inst, sols)
        elif want['c'] is None:
            relaxed = Instance(n, inst.edges[:-1], inst.labels, {}, inst.seed)
            rs = colourings(relaxed)
            if rs:
                want['c'] = (inst, sols)
                want['c-twin'] = (relaxed, rs)
    return want


def perception_noise_decide(inst, enc, cnf, p=0.03, runs=1500, seed=0):
    """Nuisance PERCEPTION-NOISE: each statement dropped w.p. p, then exact. P(answer 'possible')."""
    rng = random.Random(seed)
    yes = 0
    from pysat.solvers import Solver
    for _ in range(runs):
        if enc in GRAPH_TYPE:
            edges = [e for e in inst.edges if rng.random() >= p]
            ok = bool(colourings(Instance(inst.n, edges, inst.labels, inst.pre, inst.seed), limit=1))
        else:
            cl = [c for c in cnf.clauses if rng.random() >= p]
            with Solver(name='g4', bootstrap_with=cl) as s:
                ok = s.solve()
        yes += ok
    return yes / runs


# --------------------------------------------------------------------------------------------
# E5: MUST cells
# --------------------------------------------------------------------------------------------

def must_predictions(inst, enc, cnf_e, w, c, sols):
    canon_cnf = cnf_encode(inst)
    native = cnf_e if enc not in GRAPH_TYPE else canon_cnf
    form = 'C' if enc in C_TYPE else 'L'
    q = native.var_of[(w, c)]
    P = {}
    truth = all(s[w] == c for s in sols)
    P['EXACT'] = truth
    for t in (1, 2):
        dom, _ = M.wp_colouring(inst, t)
        P[f'WP-{t}'] = dom[w] == {c}
    dom, _ = M.wp_colouring(inst, 50)
    P['WP-inf'] = dom[w] == {c}
    for k in (2, 3, 4, None):
        A, _, conf = M.up_k(native.clauses, k, native.nvars)
        P['UP-inf' if k is None else f'UP-{k}'] = A.get(q) is True
    P['FF-LIST-READ'] = M.ff(inst, range(inst.n), 'INFEAS')[1][w] == c
    P['DSATUR-READ'] = M.dsatur(inst, 'INFEAS')[1][w] == c
    P['FF-CM'] = M.ff(inst, range(inst.n), 'ABORT', extra_forbid={w: {c}})[0] == 'IMP'
    mo = M.mention_order(native)
    uc = M.uc_det(native, mo, abort=False)
    P['UC-READ'] = q in uc[1]
    P['UC-CM'] = M.uc_det(native, mo, abort=True, extra_clauses=[[-q]])[0] == 'IMP'
    cl_cm = native.clauses + [[-q]]
    class _V: pass
    v = _V(); v.clauses = cl_cm; v.nvars = native.nvars
    g = M.greedy(v, M.mention_order(v), abort=True)
    P['GREEDY-CM'] = g[0] == 'IMP'
    fr = M.first_member(native, form=form, extra=[[-q]])
    fr0 = M.first_member(native, form=form)
    P['FIRST'] = (fr0[0] != 'IMP') and fr[0] == 'IMP'
    bc0 = M.bicond_member(native)
    P['BICOND'] = (bc0[0] != 'IMP') and M.bicond_member(native, extra=[[-q]])[0] == 'IMP'
    P['ONL(1)-reset'] = M.onl_answer_must(native, 1, q, form=form) == ('YES',)
    P['ONL(8)-reset'] = M.onl_answer_must(native, 8, q, form=form) == ('YES',)
    P['ALWAYS-YES'] = True
    P['ALWAYS-NO'] = False
    out = {k2: ('YES' if v2 else 'NO') for k2, v2 in P.items()}
    out['SAMPLE-3'] = round(M.sample_m_must(sols, w, c, 3), 3)
    out['ETR'] = 'n/c'
    return out, truth


def must_probs(preds, eps=EPS):
    out = {}
    for h, p in preds.items():
        if p == 'n/c':
            continue
        if isinstance(p, float):
            out[h] = Counter({'YES': p, 'NO': 1 - p})
        else:
            out[h] = Counter({p: 1 - eps, ('NO' if p == 'YES' else 'YES'): eps})
    return out


def find_e5_cells(n=10, seed0=90000):
    want = {'F-UP': None, 'F-CASE': None, 'NF-READ': None}
    seed = seed0
    while any(v is None for v in want.values()):
        seed += 1
        rng = random.Random(seed)
        inst = random_instance(n, rng.choice([14, 15, 16]), seed)
        a, b = rng.sample(range(n), 2)
        inst.pre = {a: 1, b: 2}
        sols = colourings(inst)
        if len(sols) < 4:
            continue
        cnf = cnf_encode(inst)
        A, _, _ = M.up_k(cnf.clauses, None, cnf.nvars)
        for w in range(n):
            if w in inst.pre:
                continue
            vals = {s[w] for s in sols}
            for c in (1, 2, 3):
                forced = vals == {c}
                derived = A.get(cnf.var_of[(w, c)]) is True
                dom1, _ = M.wp_colouring(inst, 1)
                dom2, _ = M.wp_colouring(inst, 2)
                if forced and derived and dom1[w] != {c} and dom2[w] == {c} and want['F-UP'] is None:
                    want['F-UP'] = (inst, sols, w, c)
                elif forced and not derived and want['F-CASE'] is None:
                    # twin: remove one edge so the query is no longer forced
                    for e in inst.edges:
                        tw = Instance(n, [x for x in inst.edges if x != e], inst.labels, dict(inst.pre), inst.seed)
                        ts = colourings(tw)
                        if ts and {s[w] for s in ts} != {c} and c in {s[w] for s in ts}:
                            want['F-CASE'] = (inst, sols, w, c)
                            want['F-CASE-twin'] = (tw, ts, w, c, e)
                            break
                elif (not forced) and c in vals and want['NF-READ'] is None:
                    if M.ff(inst, range(n), 'INFEAS')[1][w] == c and M.dsatur(inst, 'INFEAS')[1][w] != c:
                        want['NF-READ'] = (inst, sols, w, c)
    return want


def build_must_items(eval_id, set_id, pair_id, inst, sols, w, c, cell, encs, extra_note=''):
    items = []
    tok_G = tok_info(render(inst, 'G', 'MUST', (w, c))[0])
    from pysat.solvers import Solver
    cnf0 = cnf_encode(inst)
    with Solver(name='g4', bootstrap_with=cnf0.clauses) as s:
        follows = not s.solve(assumptions=[-cnf0.var_of[(w, c)]])
    for enc in encs:
        cnf_e = encoding_cnf(inst, enc) if enc not in GRAPH_TYPE else cnf0
        prompt, fmt = render(inst, enc, 'MUST', (w, c), cnf=cnf_e)
        tok = tok_info(prompt)
        preds, truth = must_predictions(inst, enc, cnf_e, w, c, sols)
        assert truth == follows, 'MUST ground truth disagreement'
        mp = must_probs(preds)
        fn = lambda slip: must_probs(preds, eps=slip)
        hp = h_class_probs(mp, PROF_MUST, enc, tok / tok_G, fn)
        disc = lr_table(['YES', 'NO'], mp, hp)
        predictions = {k2: {'answer': v2, 'family': FAMILY[k2][0], 'home': FAMILY[k2][1],
                            'how': how(k2, enc) if v2 != 'n/c' else 'n/c (PyETR times out at n >= 6)'} for k2, v2 in preds.items()}
        share = sum(1 for s in sols if s[w] == c) / len(sols)
        items.append({
            'eval_id': eval_id, 'set_id': set_id, 'pair_id': pair_id, 'cell': cell, 'encoding': enc,
            'domain': 'colouring backbone (k = 3, precoloured)', 'framing': {'G': 'textbook graph', 'S': 'story: exam timetable'}.get(enc, 'logic: does it follow' if enc in L_TYPE else 'CNF'),
            'prompt': prompt, 'answer_format': fmt,
            'ground_truth': {'answer': 'YES' if follows else 'NO', 'n_models': len(sols), 'share_of_models_with_query_true': round(share, 3),
                             'verified_by': ['enumeration of all colourings extending the precolouring', 'PySAT: CNF plus the negated query is UNSAT iff YES']},
            'predictions': predictions,
            'trace_predictions': {'members': TRACE_MUST, 'hypotheses': TRACE_H},
            'params': {'n': inst.n, 'm': len(inst.edges), 'seed': inst.seed, 'edges': inst.edges, 'labels': inst.labels,
                       'precolouring': inst.pre, 'query': {'vertex': w, 'colour': c}, 'prompt_tokens_o200k': tok,
                       'tokens_ratio_to_G': round(tok / tok_G, 2), 'encoding_formalism': formalism_of(enc), 'surface': SURFACE.get(enc),
                       'n_statements': n_statements(inst, enc, cnf_e)},
            'hypotheses': h_blocks(eval_id, enc),
            'disconfirms': {f"answer {o}": v for o, v in disc.items()},
            '_hprobs': {H: {k2: round(v, 4) for k2, v in c2.items()} for H, c2 in hp.items()},
            'notes': extra_note,
        })
    return items


TRACE_MUST = {
    'WP-t / UP-k': "Forward propagation from the fixed exams / unit facts: 'v12 is 1 so its neighbours are not 1' (graph) or 'x07 is false by clause 40' (CNF); stops when nothing new follows; answers NO if the query was not derived (omission).",
    'FF-LIST-READ / UC-READ': "Builds one complete colouring / scenario and reads the query off it; no check that another colouring exists (commission when the query holds in that one model).",
    'FF-CM / UC-CM / GREEDY-CM': "Tries to build a counter-example (query false) greedily; answers YES when that construction fails (commission).",
    'SAMPLE-3': "Checks two or three example colourings / scenarios, no exhaustiveness claim.",
    'ONL(k)': "Statement-by-statement in order, keeping k scenarios; resets on contradiction.",
    'FIRST / BICOND': "K3 COMMIT to the first listed slot, or K5 CONVERSE of a conditional; contradictory state -> NO.",
    'EXACT': "Case analysis that covers every colouring of the relevant vertices (K10), or a refutation of the negated query.",
}


# --------------------------------------------------------------------------------------------
# E7 and E8
# --------------------------------------------------------------------------------------------

def find_e7_cells(n=8, seed0=70000):
    want = {'r1': None, 'r2': None}
    seed = seed0
    while any(v is None for v in want.values()):
        seed += 1
        m = random.Random(seed).choice([24, 26, 28])
        cls = O.random_3sat(n, m, seed)
        mods = O.sat_models(cls, n)
        if not mods:
            continue
        view = O._CNFView(cls, n)
        mo = M.mention_order(view)
        pf = O.pick_first(cls)[0] != 'IMP'
        uc = M.uc_det(view, mo)[0] != 'IMP'
        gr = M.greedy(view, mo)[0] != 'IMP'
        if not pf and uc and gr and want['r1'] is None:
            want['r1'] = (cls, mods, seed)
        if pf and not uc and not gr and want['r2'] is None:
            want['r2'] = (cls, mods, seed)
    return want


def e7_predictions(cls, n):
    view = O._CNFView(cls, n)
    mo = M.mention_order(view)
    def tv(a):
        if a[0] == 'IMP':
            return 'NO'
        A = {v: (v in a[1]) for v in range(1, n + 1)}
        return 'YES-valid' if all(any(A[abs(l)] == (l > 0) for l in c) for c in cls) else 'YES-invalid'
    def lits(a):
        if a[0] == 'IMP':
            return 'NO'
        return 'YES-valid' if O.lits_valid(cls, a[1]) else 'YES-invalid'
    P = {'POLARITY': tv(M.polarity(view)), 'GREEDY-MENTION': tv(M.greedy(view, mo)), 'UC-DET': tv(M.uc_det(view, mo)),
         'GUC-DET': tv(M.guc_det(view)), 'PICK-FIRST': lits(O.pick_first(cls)), 'PICK-MINDEG': lits(O.pick_mindeg(cls)),
         'MCG': lits(O.most_constrained_group(cls)), 'EXACT': 'YES-valid' if O.sat_models(cls, n) else 'NO',
         'ALWAYS-NO': 'NO'}
    return P


E7_PROF = {   # CNF home: variable-driven construction; graph home: group (clause)-driven construction
    'cnf': {'UC-DET': .2, 'GREEDY-MENTION': .1, 'POLARITY': .05, 'GUC-DET': .1, 'EXACT': .35, 'PICK-FIRST': .05, 'MCG': .03, 'PICK-MINDEG': .02, 'ALWAYS-NO': .1},
    'graph': {'PICK-FIRST': .2, 'PICK-MINDEG': .1, 'MCG': .1, 'EXACT': .35, 'UC-DET': .02, 'GREEDY-MENTION': .02, 'GUC-DET': .06, 'POLARITY': .0, 'ALWAYS-NO': .15},
}
E7_PROF['logic'] = E7_PROF['cnf']


def e7_probs(P, eps=EPS):
    out = {}
    for h, p in P.items():
        c = Counter({p: 1 - eps})
        others = [x for x in ('YES-valid', 'YES-invalid', 'NO') if x != p]
        for x in others:
            c[x] += eps / 2
        out[h] = c
    return out


def build_e7_items(cell, cls, mods, seed, n):
    items = []
    P = e7_predictions(cls, n)
    renders = {'C': O.render_sat_C(cls, n), 'L-SW': O.render_sat_L(cls, n)}
    gp, gf, ne = O.render_sat_G(cls, n, seed)
    renders['G-GROUP'] = (gp, gf)
    toks = {e: tok_info(r[0]) for e, r in renders.items()}
    from pysat.solvers import Solver
    with Solver(name='g4', bootstrap_with=cls) as s:
        assert s.solve() == bool(mods)
    for enc, (prompt, fmt) in renders.items():
        f = {'C': 'cnf', 'L-SW': 'logic', 'G-GROUP': 'graph'}[enc]
        mp = e7_probs(P)
        hp = {}
        tr = toks[enc] / toks['C']
        Hs = {'H-structure': (E7_PROF['cnf'], EPS), 'H-formalism': (E7_PROF[f], EPS),
              'H-translate': (E7_PROF['cnf'] if f != 'graph' else mix(E7_PROF['cnf'], E7_PROF['graph'], 0.5), EPS),
              'H-length': (E7_PROF['cnf'], min(0.4, EPS * tr)),
              'H-surface': (E7_PROF['cnf'], EPS)}
        for H, (prof, slip) in Hs.items():
            m2 = e7_probs(P, slip)
            tot = Counter()
            for h, wgt in prof.items():
                for k2, v in m2[h].items():
                    tot[k2] += wgt * v
            hp[H] = tot
        disc = lr_table(['YES-valid', 'YES-invalid', 'NO'], mp, hp)
        how7 = lambda h: 'native' if (h in ('PICK-FIRST', 'PICK-MINDEG', 'MCG')) == (f == 'graph') or h in ('EXACT', 'ALWAYS-NO') else 'transported'
        items.append({
            'eval_id': 'E7', 'set_id': f'I-E7-{cell}', 'pair_id': 'I-E7', 'cell': cell, 'encoding': enc,
            'domain': 'SAT-native (random 3-SAT)', 'framing': {'C': 'CNF', 'L-SW': 'logic: switch rules', 'G-GROUP': 'textbook graph: one vertex per group'}[enc],
            'prompt': prompt, 'answer_format': fmt,
            'ground_truth': {'satisfiable': bool(mods), 'n_models': len(mods), 'verified_by': ['truth-table enumeration', 'PySAT Glucose4']},
            'predictions': {h: {'answer': p, 'how': how7(h), 'family': {'PICK-FIRST': 'C1', 'PICK-MINDEG': 'C1', 'MCG': 'C2', 'POLARITY': 'C0', 'GREEDY-MENTION': 'C1', 'UC-DET': 'C2', 'GUC-DET': 'C2', 'EXACT': 'null', 'ALWAYS-NO': 'A1'}[h]} for h, p in P.items()},
            'trace_predictions': {'members': {'PICK-FIRST': 'Goes group by group / clause by clause in order, choosing the first option that does not clash with earlier choices; no revisions', 'MCG': 'Chooses the group with the fewest remaining options next', 'UC-DET': 'Forced literals first, then variables in mention order set true', 'GREEDY-MENTION': 'Variable-by-variable majority over open clauses'}, 'hypotheses': TRACE_H},
            'params': {'n_vars': n, 'm_clauses': len(cls), 'clauses': cls, 'seed': seed, 'prompt_tokens_o200k': toks[enc],
                       'tokens_ratio_to_C': round(toks[enc] / toks['C'], 2), 'n_statements': len(cls) if enc != 'G-GROUP' else 3 * len(cls) + ne,
                       'encoding_formalism': f},
            'hypotheses': h_blocks('E7', enc, extra={'H-structure': 'Same member weights as on C (CNF profile used as the invariant reference here).'}),
            'disconfirms': {f"answer {o}": v for o, v in disc.items()},
            '_hprobs': {H: {k2: round(v, 4) for k2, v in c2.items()} for H, c2 in hp.items()},
            'notes': 'Reverse direction: here the graph rendering is the longest (statements and tokens), so length and formalism are crossed relative to E1–E6.',
        })
    return items


E8_PROF = {
    'logic': {'EXACT': .5, 'FIRST': .08, 'MATCH-L': .08, 'MATCH-A': .05, 'ETR': .10, 'ONL(1)': .04, 'PRIMACY': .03, 'RECENCY': .02,
              'SAMPLE-3': .05, 'ALWAYS-YES': .03, 'UP-1': .02},
    'cnf': {'EXACT': .6, 'UP-1': .15, 'GREEDY-CM': .05, 'SAMPLE-3': .05, 'FIRST': .03, 'MATCH-L': .02, 'ETR': .03, 'ALWAYS-YES': .04, 'PRIMACY': .03},
}


def build_e8_items():
    items = []
    for cell in ('M', 'N', 'U', 'V'):
        second, probe = O.GADGET_CELLS[cell]
        toks = {}
        renders = {e: O.render_gadget(cell, e) for e in ('L-DNF', 'L-CNF', 'C')}
        for e, r in renders.items():
            toks[e] = tok_info(r[0])
        for enc, (prompt, fmt) in renders.items():
            prem = O.gadget_premises(cell, enc)
            cl = O.premises_to_cnf(prem)
            g = 'YES' if O.entails(cl, probe) else 'NO'
            P = {'EXACT': g, 'FIRST': O.g_first(prem, probe), 'MATCH-L': O.g_match(prem, probe, True),
                 'MATCH-A': O.g_match(prem, probe, False), 'ONL(1)': O.g_onl(prem, probe, 1), 'ONL(2)': O.g_onl(prem, probe, 2),
                 'UP-1': O.g_up1(prem, probe), 'PRIMACY': O.g_primacy(prem, probe), 'RECENCY': O.g_primacy(prem, probe, last=True),
                 'GREEDY-CM': O.g_greedy_cm(prem, probe), 'ALWAYS-YES': 'YES'}
            try:
                P['ETR'] = O.g_etr(prem, probe)
            except Exception as ex:   # noqa: BLE001 - record failure, do not hide it
                P['ETR'] = f'n/c ({type(ex).__name__})'
            P['SAMPLE-3'] = round(O.g_sample(prem, probe), 3)
            mp = must_probs({k: v for k, v in P.items() if not str(v).startswith('n/c')})
            f = 'cnf' if enc == 'C' else 'logic'
            hp = {}
            Hs = {'H-structure': E8_PROF['logic'], 'H-formalism': E8_PROF[f],
                  'H-translate': E8_PROF['logic'] if f == 'logic' else mix(E8_PROF['logic'], E8_PROF['cnf'], .5),
                  'H-length': E8_PROF['logic'], 'H-surface': E8_PROF['logic'] if enc != 'C' else E8_PROF['cnf']}
            for H, prof in Hs.items():
                tot = Counter()
                z = sum(w for h, w in prof.items() if h in mp)
                for h, wgt in prof.items():
                    if h in mp:
                        for k2, v in mp[h].items():
                            tot[k2] += wgt / z * v
                hp[H] = tot
            disc = lr_table(['YES', 'NO'], mp, hp)
            rep_bound = []
            items.append({
                'eval_id': 'E8', 'set_id': f'I-E8-{cell}', 'pair_id': 'I-E8', 'cell': f'{cell}1·DC', 'encoding': enc,
                'domain': 'propositional entailment (B4/C4 E1 gadget)', 'framing': {'L-DNF': 'logic, disjunction of conjunctions (home form)', 'L-CNF': 'logic, the same premise as four English clauses', 'C': 'symbolic CNF'}[enc],
                'prompt': prompt, 'answer_format': fmt,
                'ground_truth': {'answer': g, 'verified_by': ['truth table over 5 atoms; the three forms are checked to be logically equivalent']},
                'predictions': {h: {'answer': p} for h, p in P.items()},
                'trace_predictions': {'members': {'FIRST': 'K3 COMMIT to the first disjunct / first literal of each clause', 'MATCH-L': 'K4 SELECT-BY-MATCH: keeps the case that shares a literal with the later categorical', 'ETR': 'K7 in-order processing with overlap filtering (PyETR 1.0.0)', 'UP-1': 'One round of unit propagation from the categorical', 'EXACT': 'K2 counter-model {box red, box not heavy, jar blue, jar cold} considered (M, U, V cells)'}, 'hypotheses': TRACE_H},
                'params': {'cell': cell, 'order': 'DC', 'premises_clausal': cl, 'probe_literal': probe, 'prompt_tokens_o200k': toks[enc]},
                'hypotheses': h_blocks('E8', enc),
                'disconfirms': {f"answer {o}": v for o, v in disc.items()},
                '_hprobs': {H: {k2: round(v, 4) for k2, v in c2.items()} for H, c2 in hp.items()},
                'notes': '',
            })
        # equivalence check across forms
        cls = [O.premises_to_cnf(O.gadget_premises(cell, e)) for e in ('L-DNF', 'L-CNF', 'C')]
        mods = [{tuple(sorted(A.items())) for A in O.sat_models(c, 5)} for c in cls]
        assert mods[0] == mods[1] == mods[2]
    return items


# --------------------------------------------------------------------------------------------
# Set-level evidence: joint outcome patterns across the encodings of one instance
# (independent responses given the hypothesis, i.e. the strategy is drawn per response; see doc §2.5)
# --------------------------------------------------------------------------------------------
SET_PATTERNS = {
    'E1': {'LIST-family fingerprint in G, S, C and L': {'G': 'm:DPLL-LIST', 'S': 'm:DPLL-LIST', 'C': 'm:DPLL-LIST', 'L': 'm:DPLL-LIST'},
           'DSATUR in G and S; GUC-DET in C and L': {'G': 'm:DSATUR', 'S': 'm:DSATUR', 'C': 'm:GUC-DET', 'L': 'm:GUC-DET'},
           'DSATUR in all four': {'G': 'm:DSATUR', 'S': 'm:DSATUR', 'C': 'm:DSATUR', 'L': 'm:DSATUR'},
           'valid in G and S; IMPOSSIBLE in C and L': {'G': 'm:DPLL-LIST', 'S': 'm:DPLL-LIST', 'C': 'IMPOSSIBLE', 'L': 'IMPOSSIBLE'},
           'LIST in G and C; DSATUR in S and L': {'G': 'm:DPLL-LIST', 'C': 'm:DPLL-LIST', 'S': 'm:DSATUR', 'L': 'm:DSATUR'}},
    'E4': {'IMPOSSIBLE in G and S; valid in C and L': {'G': 'IMPOSSIBLE', 'S': 'IMPOSSIBLE', 'C': 'VALID', 'L': 'VALID'},
           'valid in G and S; IMPOSSIBLE in C and L': {'G': 'VALID', 'S': 'VALID', 'C': 'IMPOSSIBLE', 'L': 'IMPOSSIBLE'},
           'IMPOSSIBLE in all four': {e: 'IMPOSSIBLE' for e in 'GSCL'},
           'valid in all four': {e: 'VALID' for e in 'GSCL'},
           'invalid colouring in all four': {e: 'INVALID' for e in 'GSCL'}},
    'E5': {'YES in all four': {e: 'YES' for e in 'GSCL'}, 'NO in all four': {e: 'NO' for e in 'GSCL'},
           'YES in G and S; NO in C and L': {'G': 'YES', 'S': 'YES', 'C': 'NO', 'L': 'NO'},
           'NO in G and S; YES in C and L': {'G': 'NO', 'S': 'NO', 'C': 'YES', 'L': 'YES'}},
    'E7': {'NO in G-GROUP only': {'C': 'YES-valid', 'L-SW': 'YES-valid', 'G-GROUP': 'NO'},
           'NO in C and L-SW only': {'C': 'NO', 'L-SW': 'NO', 'G-GROUP': 'YES-valid'},
           'valid in all three': {'C': 'YES-valid', 'L-SW': 'YES-valid', 'G-GROUP': 'YES-valid'}},
    'E8': {'YES in L-DNF only': {'L-DNF': 'YES', 'L-CNF': 'NO', 'C': 'NO'},
           'YES in all three': {'L-DNF': 'YES', 'L-CNF': 'YES', 'C': 'YES'},
           'NO in all three': {'L-DNF': 'NO', 'L-CNF': 'NO', 'C': 'NO'},
           'YES in L-DNF and L-CNF; NO in C': {'L-DNF': 'YES', 'L-CNF': 'YES', 'C': 'NO'}},
}


def add_set_disconfirms(items):
    groups = {}
    for it in items:
        if it['eval_id'] in SET_PATTERNS:
            groups.setdefault((it['eval_id'], it['set_id']), {})[it['encoding']] = it
    for (ev, sid), by_enc in groups.items():
        res = {}
        for pname, spec in SET_PATTERNS[ev].items():
            if not all(e in by_enc for e in spec):
                continue
            logp = {}
            for H in ('H-structure', 'H-formalism', 'H-translate', 'H-length', 'H-surface'):
                tot = 0.0
                for e, key in spec.items():
                    it = by_enc[e]
                    if key.startswith('m:'):
                        fp = [k for k, v in it['params']['fingerprints'].items() if key[2:] in v['members']]
                        key = 'fingerprint' + fp[0] if fp else 'OTHER-VALID'
                    tot += math.log10(max(it['_hprobs'][H].get(key, 0.0), 1e-9))
                logp[H] = tot
            best = max(logp.values())
            res[pname] = {H: round(best - v, 2) for H, v in logp.items()}
        for it in by_enc.values():
            it['set_disconfirms'] = res


# --------------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------------

def main(out_jsonl, out_summary):
    items = []
    summary = {}
    # ---------------- E1 ----------------
    e1 = find_e1_bases(3)
    summary['E1_yield_note'] = 'E1 bases: all six fingerprints (LIST, LABEL, DSATUR, LF, GUC, OCC) valid and pairwise distinct, FF-LIST, FF-LABEL and UC-DET succeed, >= 20 partitions.'
    for i, (inst, sols, tries) in enumerate(e1, 1):
        items += build_find_items('E1', f'I-E1-B{i}', f'I-E1-B{i}', inst, sols, ['G', 'S', 'C', 'L'], cell=f'base {i}')
        summary[f'E1-B{i}_tries'] = tries
    # ---------------- E2 (length ladder on E1 bases 1, 2) ----------------
    for i in (1, 2):
        inst, sols, _ = e1[i - 1]
        items += build_find_items('E2', f'I-E1-B{i}', f'I-E2-B{i}', inst, sols, ['G-PAD', 'X', 'C-DIMACS'], cell=f'base {i}')
    # ---------------- E3 (translation dial on E1 base 1) ----------------
    inst, sols, _ = e1[0]
    rng = random.Random(4242)
    perm_vals = list(range(1, inst.n * K + 1))
    rng.shuffle(perm_vals)
    perm = {i + 1: perm_vals[i] for i in range(inst.n * K)}
    items += build_find_items('E3', 'I-E1-B1', 'I-E3-B1', inst, sols, ['C-SCRAMBLE'], cell='dial: scrambled', perm=perm)
    items += build_find_items('E3', 'I-E1-B1', 'I-E3-B1', inst, sols, ['C-NEUTRAL', 'C-HINT', 'L-NEUTRAL', 'L-HINT'], cell='dial')
    # ---------------- E6 (crossed order on E1 bases 2, 3) ----------------
    for i in (2, 3):
        inst, sols, _ = e1[i - 1]
        r = random.Random(777 + i)
        base_list = canon_of(inst, cnf_encode(inst), M.dpll_graph(inst, 'list')[0])
        while True:
            xord = list(range(inst.n))
            r.shuffle(xord)
            if _dpll_order(inst, xord)[0] == 'COL' and canon(_dpll_order(inst, xord)[1]) != base_list[1]:
                break
        items += build_find_items('E6', f'I-E1-B{i}', f'I-E6-B{i}', inst, sols, ['C-XORD', 'L-XORD'], cell='crossed order', xord=xord,
                                  extra_params={'xord': xord})
    # ---------------- E4 ----------------
    e4 = find_e4_cells()
    for cell in ('a1', 'a2', 'b', 'c', 'c-twin'):
        inst, sols = e4[cell]
        new = build_find_items('E4', f'I-E4-{cell}', 'I-E4-c' if cell.startswith('c') else f'I-E4-{cell}', inst, sols,
                               ['G', 'S', 'C', 'L'], cell=cell, task='DECIDE')
        for it in new:
            cnf_e = encoding_cnf(inst, it['encoding']) if it['encoding'] not in GRAPH_TYPE else cnf_encode(inst)
            pn = perception_noise_decide(inst, it['encoding'], cnf_e, seed=inst.seed)
            it['predictions']['PERCEPTION-NOISE'] = {'family': 'nuisance', 'home': 'any', 'how': 'native (drops each statement w.p. 0.03)',
                                                      'canonical': f'P(answer possible) = {pn:.3f}'}
            it['notes'] = {'a1': 'Colourable. FF-LIST dead-ends; UC-DET (unit propagation first) and DSATUR succeed.',
                           'a2': 'Colourable. FF-LIST and UC-DET both dead-end; DSATUR succeeds.',
                           'b': 'Colourable. FF-LIST, UC-DET and DSATUR all succeed: only collapse members (POLARITY, GREEDY, FIRST, BICOND, ONL) and cues say IMPOSSIBLE.',
                           'c': 'Not colourable; removing the last-listed edge makes it colourable (B1 DROP-LAST-1 says possible). Truth twin of c-twin.',
                           'c-twin': 'Twin of c with the last edge removed: colourable. Same encodings; the truth flips with one edge.'}[cell]
        items += new
    # ---------------- E5 ----------------
    e5 = find_e5_cells()
    for cell in ('F-UP', 'F-CASE', 'NF-READ'):
        inst, sols, w, c = e5[cell]
        items += build_must_items('E5', f'I-E5-{cell}', 'I-E5-FCASE' if cell == 'F-CASE' else f'I-E5-{cell}', inst, sols, w, c, cell, ['G', 'S', 'C', 'L'],
                                  extra_note={'F-UP': 'Forced, derivable by propagation: WP-2 (two graph hops) = UP-4; WP-1 = UP-2 do not reach it.',
                                              'F-CASE': 'Forced only by case analysis: UP to fixpoint (= WP to fixpoint) does not derive it (B1 omission).',
                                              'NF-READ': 'Not forced; the first-fit model has the query true (single-model commission), DSATUR\'s model does not.'}[cell])
    tw, ts, w, c, e = e5['F-CASE-twin']
    items += build_must_items('E5', 'I-E5-F-CASE-twin', 'I-E5-FCASE', tw, ts, w, c, 'F-CASE-twin', ['G', 'S', 'C', 'L'],
                              extra_note=f'Twin of F-CASE with edge {e} removed: the query is no longer forced (truth flips, encodings fixed).')
    # ---------------- E7 ----------------
    e7 = find_e7_cells()
    for cell in ('r1', 'r2'):
        cls, mods, seed = e7[cell]
        items += build_e7_items(cell, cls, mods, seed, 8)
    # ---------------- E8 ----------------
    items += build_e8_items()
    add_set_disconfirms(items)
    # ---------------- write ----------------
    with open(out_jsonl, 'w') as f:
        for it in items:
            it2 = {k: v for k, v in it.items() if not k.startswith('_')}
            f.write(json.dumps(it2, ensure_ascii=False) + '\n')
    summary['n_items'] = len(items)
    summary['by_eval_encoding'] = Counter(f"{it['eval_id']}:{it['encoding']}" for it in items)
    summary['hprobs'] = [{'eval_id': it['eval_id'], 'set_id': it['set_id'], 'cell': it['cell'], 'encoding': it['encoding'],
                          'hprobs': it['_hprobs']} for it in items]
    with open(out_summary, 'w') as f:
        json.dump(summary, f, indent=1, default=str)
    print('items', len(items))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
