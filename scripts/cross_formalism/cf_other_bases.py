"""Non-colouring base types for the cross-formalism vertical.

E7 (reverse direction): a random 3-SAT base rendered as
    C        CNF over x1..xn
    L-SW     'At least one of these is true: switch 3 is on, switch 5 is off, switch 7 is on.'
    G-GROUP  a graph: one group of three vertices per clause, an edge between every two vertices whose
             literals are complementary; 'pick exactly one vertex from each group, no two picked adjacent'
             (Karp's SAT -> independent set reduction without the triangle edges). Here the graph
             rendering is the LONGER one, which reverses the length confound of the colouring sets.

E8 (logic-native gadget): the B4/C4 E1 disjunction gadget (DC order, matched disjunct first) rendered as
    L-DNF    'Either the box is red and the box is heavy, or the jar is blue and the jar is cold.'
    L-CNF    the same premise as four English clauses ('The box is red or the jar is blue.' ...)
    C        the four clauses as symbolic CNF
"""
from __future__ import annotations

import itertools
import random

from cf_members import IMP, clause_status, mention_order, unit_propagate

# ============================================================================================
# E7: SAT-native bases
# ============================================================================================


def random_3sat(n, m, seed):
    rng = random.Random(seed)
    clauses = []
    while len(clauses) < m:
        vs = rng.sample(range(1, n + 1), 3)
        cl = [v if rng.random() < 0.5 else -v for v in vs]
        if sorted(cl) not in [sorted(c) for c in clauses]:
            clauses.append(cl)
    return clauses


def sat_models(clauses, n):
    out = []
    for bits in itertools.product([False, True], repeat=n):
        A = {i + 1: bits[i] for i in range(n)}
        if all(any(A[abs(l)] == (l > 0) for l in cl) for cl in clauses):
            out.append(A)
    return out


class _CNFView:
    """Minimal CNF object so the C-family members of cf_members run on plain clause lists."""
    def __init__(self, clauses, n):
        self.clauses, self.nvars = clauses, n
        self.kinds = ['CL'] * len(clauses)


def group_graph(clauses):
    """Vertices (clause i, position j) in listing order; edges between complementary occurrences."""
    verts = [(i, j) for i in range(len(clauses)) for j in range(3)]
    lit = {(i, j): clauses[i][j] for (i, j) in verts}
    edges = [(a, b) for a, b in itertools.combinations(verts, 2) if lit[a] == -lit[b]]
    return verts, edges, lit


def pick_first(clauses, score=None):
    """Group-native C1: groups in listed order; pick the first (or lowest-score) vertex not adjacent
    to an already picked vertex. In SAT terms: for each clause in order, make true its first literal
    not contradicting the literals chosen so far. ABORT if a group has no compatible vertex."""
    chosen = set()
    for cl in clauses:
        cands = [l for l in cl if -l not in chosen]
        if not cands:
            return IMP
        if score is not None:
            cands = sorted(cands, key=lambda l: (score(l), cl.index(l)))
        chosen.add(cands[0])
    return ('LITS', frozenset(chosen))


def pick_mindeg(clauses):
    """Group-native static score: pick the compatible vertex with the fewest edges (fewest
    complementary occurrences overall). Ties: first in the group."""
    occ = {}
    for cl in clauses:
        for l in cl:
            occ[l] = occ.get(l, 0) + 1
    return pick_first(clauses, score=lambda l: occ.get(-l, 0))


def most_constrained_group(clauses):
    """Group-native C2 (DSATUR-like): repeatedly take the group with the fewest compatible vertices
    (ties: listed order) and pick its first compatible vertex. ABORT when a group has none."""
    chosen = set()
    left = list(range(len(clauses)))
    while left:
        def ncomp(i):
            return sum(1 for l in clauses[i] if -l not in chosen)
        i = min(left, key=lambda i: (ncomp(i), i))
        cands = [l for l in clauses[i] if -l not in chosen]
        if not cands:
            return IMP
        chosen.add(cands[0])
        left.remove(i)
    return ('LITS', frozenset(chosen))


def lits_valid(clauses, lits):
    if any(-l in lits for l in lits):
        return False
    return all(any(l in lits for l in cl) for cl in clauses)


def render_sat_C(clauses, n):
    lines = [f"CNF formula over {n} Boolean variables (x1 to x{n}) with {len(clauses)} clauses (in this order):"]
    lines += ["(" + " ∨ ".join(("¬" if l < 0 else "") + f"x{abs(l)}" for l in cl) + ")" for cl in clauses]
    lines.append("Find an assignment of true/false to the variables that makes every clause true.")
    fmt = ("Think it through as carefully as you need. If no such assignment exists, finish with the line \"ANSWER: UNSAT\". "
           "Otherwise finish with the line \"ANSWER:\" followed by the variables you set to true, separated by spaces "
           "(every other variable is false).")
    return "\n".join(lines) + "\n\n" + fmt, fmt


def render_sat_L(clauses, n):
    sw = lambda l: f"switch {abs(l)} is {'on' if l > 0 else 'off'}"
    lines = [f"A panel has {n} switches, numbered 1 to {n}; each switch is either on or off. Here are some rules:"]
    for i, cl in enumerate(clauses, 1):
        lines.append(f"{i}. At least one of these is true: " + ", ".join(sw(l) for l in cl) + ".")
    lines.append("Question: Can all of the rules hold at the same time? If they can, give a setting of the switches that satisfies every rule.")
    fmt = ("Think it through as carefully as you need. If the rules cannot all hold, finish with the line \"ANSWER: NO\". "
           "Otherwise finish with the line \"ANSWER:\" followed by the numbers of the switches that are on, separated by "
           "spaces (every other switch is off).")
    return "\n".join(lines) + "\n\n" + fmt, fmt


def render_sat_G(clauses, n, seed):
    verts, edges, lit = group_graph(clauses)
    rng = random.Random(seed)
    labs = rng.sample(range(100, 1000), len(verts))   # three-digit labels: 3m can exceed 90
    lab = {v: f"u{labs[k]}" for k, v in enumerate(verts)}
    lines = [f"A graph has {len(verts)} vertices in {len(clauses)} groups of three and {len(edges)} edges.",
             "Groups (in this order):"]
    for i in range(len(clauses)):
        lines.append(f"Group {i + 1}: " + ", ".join(lab[(i, j)] for j in range(3)))
    lines.append("Edges (in this order):")
    lines += [f"{lab[a]} - {lab[b]}" for a, b in edges]
    lines.append("Pick exactly one vertex from each group so that no two picked vertices are joined by an edge.")
    fmt = ("Think it through as carefully as you need. If this is impossible, finish with the line \"ANSWER: IMPOSSIBLE\". "
           "Otherwise finish with the line \"ANSWER:\" followed by one line `group: vertex` per group, in group order.")
    return "\n".join(lines) + "\n\n" + fmt, fmt, len(edges)


# ============================================================================================
# E8: the B4/C4 E1 disjunction gadget in three logical forms
# ============================================================================================

GADGET_ATOMS = {1: ("the box", "red"), 2: ("the box", "heavy"), 3: ("the jar", "blue"), 4: ("the jar", "cold"), 5: ("the cup", "green")}
GADGET_CELLS = {
    # second premise, probe literal ; DNF premise is (A and B) or (C and D) with A..E = 1..5
    'M': ([[1]], 2),          # 'The box is red.'           probe: the box is heavy   g = NO
    'N': ([[-1]], 4),         # 'The box is not red.'       probe: the jar is cold    g = YES
    'U': ([[5]], 2),          # 'The cup is green.'         probe: the box is heavy   g = NO
    'V': ([[1, 5]], 2),       # 'The box is red, or the cup is green.'  probe heavy   g = NO
}
DNF = [[1, 2], [3, 4]]                     # disjunction of conjunctions
CNF_OF_DNF = [[1, 3], [1, 4], [2, 3], [2, 4]]


def g_text(l):
    s, p = GADGET_ATOMS[abs(l)]
    return f"{s} is {'not ' if l < 0 else ''}{p}"


def g_cap(s):
    return s[0].upper() + s[1:]


def render_gadget(cell, enc):
    second, probe = GADGET_CELLS[cell]
    sec = second[0]
    sec_txt = g_cap(g_text(sec[0])) + "." if len(sec) == 1 else g_cap(g_text(sec[0])) + ", or " + g_text(sec[1]) + "."
    if enc == 'L-DNF':
        prem = [f"Either {g_text(1)} and {g_text(2)}, or {g_text(3)} and {g_text(4)}.", sec_txt]
    elif enc == 'L-CNF':
        prem = [g_cap(g_text(a)) + " or " + g_text(b) + "." for a, b in CNF_OF_DNF] + [sec_txt]
    if enc in ('L-DNF', 'L-CNF'):
        lines = ["Here are some statements:"] + [f"{i}. {p}" for i, p in enumerate(prem, 1)]
        lines += [f"Question: Does it follow that {g_text(probe)}?",
                  "A conclusion follows only if it must be true whenever all of the statements are true."]
    else:
        cls = CNF_OF_DNF + second
        lines = ["CNF formula over 5 Boolean variables (x1 to x5) with %d clauses (in this order):" % len(cls)]
        lines += ["(" + " ∨ ".join(("¬" if l < 0 else "") + f"x{abs(l)}" for l in cl) + ")" for cl in cls]
        lines.append(f"Question: Is x{probe} true in every assignment that makes every clause true?")
    fmt = "Think it through as carefully as you need. Finish with a final line that is exactly \"ANSWER: YES\" or \"ANSWER: NO\"."
    return "\n".join(lines) + "\n\n" + fmt, fmt


def entails(clauses, lit, n=5):
    for A in sat_models(clauses, n):
        if A[abs(lit)] != (lit > 0):
            return False
    return True


def consistent(clauses, n=5):
    return len(sat_models(clauses, n)) > 0


def gadget_premises(cell, enc):
    """Premises as (kind, payload) in surface order. kinds: 'DNF' (list of conjunctions), 'CL' (clause)."""
    second, _ = GADGET_CELLS[cell]
    if enc == 'L-DNF':
        return [('DNF', DNF), ('CL', second[0])]
    return [('CL', c) for c in CNF_OF_DNF] + [('CL', second[0])]


def premises_to_cnf(prem):
    out = []
    for kind, p in prem:
        if kind == 'DNF':
            out += [list(x) for x in itertools.product(*p)]
        else:
            out.append(list(p))
    return out


def g_first(prem, probe):
    """B4 FIRST: each disjunctive premise read as its first disjunct; exact; X -> NO."""
    cl = []
    for kind, p in prem:
        if kind == 'DNF':
            cl += [[l] for l in p[0]]
        elif len(p) > 1:
            cl.append([p[0]])
        else:
            cl.append(list(p))
    if not consistent(cl):
        return 'NO'
    return 'YES' if entails(cl, probe) else 'NO'


def g_match(prem, probe, later_only=True):
    """B4 MATCH-L / MATCH-A (polarity-aware): a disjunctive premise is cut to the disjuncts sharing a
    literal with a categorical premise (later one for -L, any other for -A), if that keeps 0 < |S| < |P|."""
    cats = [(i, set(p)) for i, (kind, p) in enumerate(prem) if kind == 'CL' and len(p) == 1]
    out = []
    for i, (kind, p) in enumerate(prem):
        disj = [set(d) for d in p] if kind == 'DNF' else ([{l} for l in p] if len(p) > 1 else None)
        if disj is not None:
            for j, cat in cats:
                if (later_only and j <= i) or j == i:
                    continue
                S = [d for d in disj if d & cat]
                if 0 < len(S) < len(disj):
                    disj = S
                break
            out.append(('DNF', [sorted(d) for d in disj]))
        else:
            out.append((kind, p))
    cl = premises_to_cnf(out)
    return 'YES' if entails(cl, probe) else 'NO'


def g_alts(kind, p):
    if kind == 'DNF':
        return [frozenset(d) for d in p]
    return [frozenset([l]) for l in p]


def g_onl(prem, probe, k, mode='reset'):
    S = [frozenset()]
    for kind, p in prem:
        alts = g_alts(kind, p)
        S2 = []
        for s in S:
            for a in alts:
                u = s | a
                if any(-l in u for l in u) or u in S2:
                    continue
                S2.append(u)
        S2 = S2[:k]
        if not S2:
            if mode == 'strict':
                return 'NO'
            S2 = alts[:k]
        S = S2
    return 'YES' if all(probe in s for s in S) else 'NO'


def g_up1(prem, probe):
    cl = premises_to_cnf(prem)
    A = {}
    for c in cl:
        if len(c) == 1:
            A[abs(c[0])] = c[0] > 0
    new = {}
    for c in cl:
        st = clause_status(c, A)
        if st not in ('SAT', 'FALSE') and len(st[1]) == 1:
            new[abs(st[1][0])] = st[1][0] > 0
    A.update(new)
    return 'YES' if A.get(abs(probe)) == (probe > 0) else 'NO'


def g_primacy(prem, probe, last=False):
    kind, p = prem[-1] if last else prem[0]
    lits = {l for d in p for l in d} if kind == 'DNF' else set(p)
    return 'YES' if probe in lits else 'NO'


def g_sample(prem, probe, m=3):
    cl = premises_to_cnf(prem)
    mods = sat_models(cl, 5)
    rho = sum(1 for A in mods if A[abs(probe)] != (probe > 0)) / len(mods)
    return (1 - rho) ** m


def g_greedy_cm(prem, probe):
    """C1 GREEDY-CM: CNF(P and not C), premise order, GREEDY-MENTION; a model found -> NO, else YES."""
    cl = premises_to_cnf(prem) + [[-probe]]
    view = _CNFView(cl, 5)
    order = mention_order(view)
    A = {}
    for v in order:
        p = q = 0
        for c in cl:
            if clause_status(c, A) == 'SAT':
                continue
            p += v in c
            q += -v in c
        A[v] = p >= q
    ok = all(clause_status(c, A) == 'SAT' for c in cl)
    return 'NO' if ok else 'YES'


def g_etr(prem, probe):
    """ETR-dif via PyETR 1.0.0 (default_procedure_does_it_follow), no issue marks."""
    from pyetr import View
    from pyetr.inference import default_procedure_does_it_follow
    def atom(l):
        s, p = GADGET_ATOMS[abs(l)]
        a = f"{p.capitalize()}({s.split()[1]}())"
        return ("~" if l < 0 else "") + a
    views = []
    for kind, p in prem:
        if kind == 'DNF':
            views.append("{" + ",".join(" ".join(atom(l) for l in d) for d in p) + "}")
        else:
            views.append("{" + ",".join(atom(l) for l in p) + "}")
    r = default_procedure_does_it_follow([View.from_str(v) for v in views], View.from_str("{" + atom(probe) + "}"))
    return 'YES' if r else 'NO'
