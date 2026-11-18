"""Instances, exact solvers and encodings for the cross-formalism vertical (I_cross_formalism).

One canonical instance (a graph with k = 3 colours, optional precolouring) is rendered in several
formalisms with the ground truth fixed:

    G       graph colouring, symbolic labels (v37), edge list
    S       story: exam timetabling (exams, slots, clashing pairs)
    C       CNF over opaque variables x01..x3n (direct encoding: ALO + AMO + conflict clauses)
    L       propositional premises in English, clause for clause with C, exam/slot atoms
    G-PAD   G with long labels (tokens matched to C; same statements)
    X       C with named atoms v37.1 ("v37 has colour 1"): statements of C, labels of G
    C-DIMACS  C in DIMACS notation (fewer tokens, same clauses)
    C-SCRAMBLE  C with variable numbers permuted (grouping into triples hidden)
    C-HINT / C-NEUTRAL, L-HINT / L-NEUTRAL  legend header vs a token-matched neutral header

Orders are matched across encodings by construction:
    listing order pi_L  = vertex order in G/S = order of first mention in C/L/X
    label order  lambda = numeric label order in G = variable-index order in C = alphabetical in S/L
Crossed-order variants pass a different vertex order to the propositional renderers.

Run with numpy, python-sat, tiktoken installed (see build_library.py).
"""
from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field

K = 3  # colours / slots

# --------------------------------------------------------------------------------------------
# Instances
# --------------------------------------------------------------------------------------------


@dataclass
class Instance:
    n: int
    edges: list            # (u, v) with u < v in listing positions; list order = edge-list order
    labels: list           # labels[v] = two-digit int, distinct; lambda order = sorted labels
    pre: dict = field(default_factory=dict)  # precolouring {v: colour}
    seed: int = 0

    @property
    def adj(self):
        a = [set() for _ in range(self.n)]
        for u, v in self.edges:
            a[u].add(v)
            a[v].add(u)
        return a

    def label_order(self):
        return sorted(range(self.n), key=lambda v: self.labels[v])

    def listing_order(self):
        return list(range(self.n))


def random_instance(n, m, seed, label_pool=range(10, 100)):
    rng = random.Random(seed)
    pairs = list(itertools.combinations(range(n), 2))
    rng.shuffle(pairs)
    edges = sorted(pairs[:m])  # edge-list order: lexicographic in listing positions
    labels = rng.sample(list(label_pool), n)
    return Instance(n=n, edges=edges, labels=labels, seed=seed)


def colourings(inst: Instance, k=K, limit=None, extra_neq=()):
    """All proper k-colourings (tuples, colours 1..k) extending inst.pre, by backtracking.
    extra_neq: list of (vertex, colour) pairs that are forbidden (used for counter-model checks)."""
    n, adj = inst.n, inst.adj
    forb = {}
    for v, c in extra_neq:
        forb.setdefault(v, set()).add(c)
    col = [0] * n
    out = []
    order = list(range(n))

    def rec(i):
        if limit is not None and len(out) >= limit:
            return
        if i == n:
            out.append(tuple(col))
            return
        v = order[i]
        choices = [inst.pre[v]] if v in inst.pre else range(1, k + 1)
        for c in choices:
            if c in forb.get(v, ()):
                continue
            if all(col[u] != c for u in adj[v] if col[u]):
                col[v] = c
                rec(i + 1)
                col[v] = 0

    rec(0)
    return out


def is_proper(inst, col, k=K):
    if col is None or len(col) != inst.n:
        return False
    if any(c not in range(1, k + 1) for c in col):
        return False
    if any(col[v] != c for v, c in inst.pre.items()):
        return False
    return all(col[u] != col[v] for u, v in inst.edges)


def canon(col, order=None):
    """Partition canonical form: rename colours by first appearance in listing order.
    Returns a tuple; invalid / partial colourings keep 0 for uncoloured vertices."""
    if col is None:
        return None
    order = order or range(len(col))
    ren, nxt = {}, 1
    out = list(col)
    for v in order:
        c = col[v]
        if c == 0:
            continue
        if c not in ren:
            ren[c] = nxt
            nxt += 1
        out[v] = ren[c]
    return tuple(out)


def partition_distance(a, b):
    """Minimum number of vertices to recolour to turn colouring a into b up to renaming colours."""
    best = None
    for perm in itertools.permutations(range(1, K + 1)):
        m = {i + 1: perm[i] for i in range(K)}
        d = sum(1 for x, y in zip(a, b) if m.get(x, 0) != y)
        best = d if best is None else min(best, d)
    return best


# --------------------------------------------------------------------------------------------
# CNF (direct encoding) and the solver cross-check
# --------------------------------------------------------------------------------------------


@dataclass
class CNF:
    clauses: list          # list of lists of signed ints, in clause order
    kinds: list            # 'UNIT' | 'ALO' | 'AMO' | 'CONF' per clause
    var_of: dict           # (v, c) -> var index (1-based)
    vc_of: dict            # var index -> (v, c)
    nvars: int


def cnf_encode(inst: Instance, vertex_order=None, edge_order=None, index_perm=None, k=K):
    """Direct encoding. Clause order: precolour units, ALO block, AMO block, conflict block.
    Variable index = rank of v in label order * k + c (so index order = label order x colour).
    vertex_order sets the order of the ALO/AMO blocks (default pi_L); edge_order the conflict block.
    index_perm (optional) renames variables (C-SCRAMBLE): new = index_perm[old]."""
    vo = vertex_order if vertex_order is not None else inst.listing_order()
    eo = edge_order if edge_order is not None else inst.edges
    lam_rank = {v: r for r, v in enumerate(inst.label_order())}
    var_of = {}
    for v in range(inst.n):
        for c in range(1, k + 1):
            idx = lam_rank[v] * k + c
            if index_perm is not None:
                idx = index_perm[idx]
            var_of[(v, c)] = idx
    vc_of = {i: vc for vc, i in var_of.items()}
    clauses, kinds = [], []
    for v in vo:
        if v in inst.pre:
            clauses.append([var_of[(v, inst.pre[v])]])
            kinds.append('UNIT')
    for v in vo:
        clauses.append([var_of[(v, c)] for c in range(1, k + 1)])
        kinds.append('ALO')
    for v in vo:
        for c1, c2 in itertools.combinations(range(1, k + 1), 2):
            clauses.append([-var_of[(v, c1)], -var_of[(v, c2)]])
            kinds.append('AMO')
    pos = {v: i for i, v in enumerate(vo)}
    for (u, v) in eo:
        a, b = (u, v) if pos[u] < pos[v] else (v, u)  # earlier-mentioned endpoint first
        for c in range(1, k + 1):
            clauses.append([-var_of[(a, c)], -var_of[(b, c)]])
            kinds.append('CONF')
    return CNF(clauses, kinds, var_of, vc_of, inst.n * k)


def decode(cnf: CNF, inst: Instance, true_vars):
    """Assignment (set of true variable indices) -> colouring tuple; a vertex with 0 or >1 true
    colours gets 0 (invalid). Returns (colouring, valid?)."""
    col = []
    for v in range(inst.n):
        cs = [c for c in range(1, K + 1) if cnf.var_of[(v, c)] in true_vars]
        col.append(cs[0] if len(cs) == 1 else 0)
    col = tuple(col)
    return col, (0 not in col) and is_proper(inst, col)


def encode_assignment(cnf: CNF, col):
    return {cnf.var_of[(v, c)] for v, c in enumerate(col) if c}


def pysat_colourable(inst: Instance, extra_units=()):
    """Independent check with a SAT solver (python-sat, CaDiCaL/Glucose)."""
    from pysat.solvers import Solver
    cnf = cnf_encode(inst)
    with Solver(name='g4', bootstrap_with=cnf.clauses) as s:
        ok = s.solve(assumptions=list(extra_units))
        model = s.get_model() if ok else None
    if not ok:
        return False, None
    tv = {x for x in model if x > 0}
    col, valid = decode(cnf, inst, tv)
    assert valid
    return True, col


# --------------------------------------------------------------------------------------------
# Renderers
# --------------------------------------------------------------------------------------------

EXAM_POOL = [
    "Algebra", "Botany", "Ceramics", "Dance", "Ecology", "Finance", "Geology", "Harmony",
    "Italian", "Journalism", "Kinetics", "Latin", "Mechanics", "Nutrition", "Optics", "Poetry",
    "Quilting", "Rhetoric", "Statistics", "Tectonics", "Urdu", "Virology", "Welding", "Zoology",
]
PAD_WORDS = ["amber", "basil", "cedar", "dune", "ember", "fjord", "garnet", "harbor", "indigo",
             "juniper", "kelp", "lumen", "maple", "nectar", "onyx", "pumice", "quartz", "russet"]


def exam_names(inst: Instance):
    """Exam names whose alphabetical order equals the label order (lambda matched)."""
    rng = random.Random(inst.seed * 7 + 3)
    names = sorted(rng.sample(EXAM_POOL, inst.n))
    out = [None] * inst.n
    for r, v in enumerate(inst.label_order()):
        out[v] = names[r]
    return out


def vlabel(inst, v):
    return f"v{inst.labels[v]}"


def pad_label(inst, v, nwords):
    rng = random.Random(inst.labels[v] * 101 + nwords)
    return f"v{inst.labels[v]}-" + "-".join(rng.sample(PAD_WORDS, nwords))


def answer_order_text(names):
    return ", ".join(names)


def render_G(inst, task, query=None, labels=None):
    lab = labels or [vlabel(inst, v) for v in range(inst.n)]
    lines = [f"Graph with {inst.n} vertices and {len(inst.edges)} edges.",
             "Vertices (in this order): " + ", ".join(lab[v] for v in range(inst.n)),
             "Edges (in this order):"]
    lines += [f"{lab[u]} - {lab[v]}" for u, v in inst.edges]
    if inst.pre:
        lines.append("Already coloured: " + ", ".join(f"{lab[v]} has colour {c}" for v, c in sorted(inst.pre.items())) + ".")
    if task in ("FIND", "DECIDE"):
        lines.append("Colour every vertex with one of the colours 1, 2, 3 so that the two ends of every edge get different colours.")
        fmt = ("Think it through as carefully as you need. If no such colouring exists, finish with the line "
               "\"ANSWER: IMPOSSIBLE\". Otherwise finish with the line \"ANSWER:\" followed by one line "
               f"`vertex: colour` per vertex, in this order: {answer_order_text(lab)}.")
    else:
        w, c = query
        lines.append("Consider every way of colouring all vertices with the colours 1, 2, 3 so that the two ends of every edge get different colours and the already-coloured vertices keep their colours.")
        lines.append(f"Question: In every such colouring, does {lab[w]} have colour {c}?")
        fmt = "Think it through as carefully as you need. Finish with a final line that is exactly \"ANSWER: YES\" or \"ANSWER: NO\"."
    return "\n".join(lines) + "\n\n" + fmt, fmt


def render_S(inst, task, query=None):
    ex = exam_names(inst)
    lines = [f"A school must timetable {inst.n} exams into three slots: slot 1, slot 2 and slot 3.",
             "Exams (in this order): " + ", ".join(ex),
             "Some pairs of exams share a student, so the two exams in each pair must be in different slots. The pairs are (in this order):"]
    lines += [f"{ex[u]} and {ex[v]}" for u, v in inst.edges]
    if inst.pre:
        lines.append("Already fixed: " + ", ".join(f"{ex[v]} is in slot {c}" for v, c in sorted(inst.pre.items())) + ".")
    if task in ("FIND", "DECIDE"):
        lines.append("Put every exam in one of the three slots so that no student has two exams in the same slot.")
        fmt = ("Think it through as carefully as you need. If no such timetable exists, finish with the line "
               "\"ANSWER: IMPOSSIBLE\". Otherwise finish with the line \"ANSWER:\" followed by one line "
               f"`exam: slot` per exam, in this order: {answer_order_text(ex)}.")
    else:
        w, c = query
        lines.append("Consider every timetable that puts each exam in one of the three slots, keeps the fixed exams where they are, and never puts two exams that share a student in the same slot.")
        lines.append(f"Question: In every such timetable, is {ex[w]} in slot {c}?")
        fmt = "Think it through as carefully as you need. Finish with a final line that is exactly \"ANSWER: YES\" or \"ANSWER: NO\"."
    return "\n".join(lines) + "\n\n" + fmt, fmt


def xname(i, width=2):
    return f"x{i:0{width}d}"


def lit_text(l, width=2):
    return ("¬" if l < 0 else "") + xname(abs(l), width)


def render_C(inst, task, query=None, cnf=None, header=None, atom_names=None):
    cnf = cnf or cnf_encode(inst)
    width = 2 if cnf.nvars < 100 else 3
    name = atom_names or (lambda i: xname(i, width))
    lt = lambda l: ("¬" if l < 0 else "") + name(abs(l))
    lines = []
    if header:
        lines.append(header)
    vars_sorted = sorted(cnf.vc_of)
    lines.append(f"CNF formula over {cnf.nvars} Boolean variables ({name(vars_sorted[0])} to {name(vars_sorted[-1])}) with {len(cnf.clauses)} clauses (in this order):")
    lines += ["(" + " ∨ ".join(lt(l) for l in cl) + ")" for cl in cnf.clauses]
    if task in ("FIND", "DECIDE"):
        lines.append("Find an assignment of true/false to the variables that makes every clause true.")
        fmt = ("Think it through as carefully as you need. If no such assignment exists, finish with the line "
               "\"ANSWER: UNSAT\". Otherwise finish with the line \"ANSWER:\" followed by the variables you set to true, "
               "separated by spaces (every other variable is false).")
    else:
        w, c = query
        lines.append(f"Question: Is {name(cnf.var_of[(w, c)])} true in every assignment that makes every clause true?")
        fmt = "Think it through as carefully as you need. Finish with a final line that is exactly \"ANSWER: YES\" or \"ANSWER: NO\"."
    return "\n".join(lines) + "\n\n" + fmt, fmt


def render_X(inst, task, query=None, cnf=None):
    """C with named atoms: v37.1 means 'vertex v37 has colour 1'. Same clauses, same order."""
    cnf = cnf or cnf_encode(inst)
    atom = lambda i: f"{vlabel(inst, cnf.vc_of[i][0])}.{cnf.vc_of[i][1]}"
    header = ("Atoms: for each vertex v of a graph and each colour c in 1, 2, 3, the atom v.c means "
              "\"vertex v has colour c\" (so v37.2 means vertex v37 has colour 2).")
    p, _ = render_C(inst, task, query, cnf=cnf, header=header, atom_names=atom)
    p = p.replace(f"CNF formula over {cnf.nvars} Boolean variables", f"CNF formula over {cnf.nvars} atoms")
    p = p.replace("Find an assignment of true/false to the variables", "Find an assignment of true/false to the atoms")
    p = p.replace("followed by the variables you set to true", "followed by the atoms you set to true")
    p = p.replace("(every other variable is false)", "(every other atom is false)")
    fmt = p.split("\n\n")[-1]
    return p, fmt


def render_DIMACS(inst, task, query=None, cnf=None):
    cnf = cnf or cnf_encode(inst)
    lines = ["A CNF formula in DIMACS format. Each line after the header is one clause: the literals in the clause, ending in 0. "
             "A positive number i means variable i is true; a negative number -i means variable i is false.",
             f"p cnf {cnf.nvars} {len(cnf.clauses)}"]
    lines += [" ".join(str(l) for l in cl) + " 0" for cl in cnf.clauses]
    if task in ("FIND", "DECIDE"):
        lines.append("Find an assignment of true/false to the variables that makes every clause true.")
        fmt = ("Think it through as carefully as you need. If no such assignment exists, finish with the line "
               "\"ANSWER: UNSAT\". Otherwise finish with the line \"ANSWER:\" followed by the numbers of the variables "
               "you set to true, separated by spaces (every other variable is false).")
    else:
        w, c = query
        lines.append(f"Question: Is variable {cnf.var_of[(w, c)]} true in every assignment that makes every clause true?")
        fmt = "Think it through as carefully as you need. Finish with a final line that is exactly \"ANSWER: YES\" or \"ANSWER: NO\"."
    return "\n".join(lines) + "\n\n" + fmt, fmt


def render_L(inst, task, query=None, cnf=None, header=None):
    """Clause-for-clause English rendering of the direct encoding, exam/slot atoms.
    ALO: 'The X exam is in slot 1, slot 2 or slot 3.'  AMO and conflicts: conditionals with the
    earlier-mentioned atom as antecedent ('If the X exam is in slot 1, then the X exam is not in slot 2.')."""
    cnf = cnf or cnf_encode(inst)
    ex = exam_names(inst)
    at = lambda v, c: f"the {ex[v]} exam is in slot {c}"
    lines = []
    if header:
        lines.append(header)
    lines.append("Here are some statements:")
    for i, (cl, kind) in enumerate(zip(cnf.clauses, cnf.kinds), 1):
        if kind == 'UNIT':
            v, c = cnf.vc_of[cl[0]]
            s = at(v, c)
        elif kind == 'ALO':
            v = cnf.vc_of[cl[0]][0]
            s = f"the {ex[v]} exam is in slot " + ", slot ".join(str(cnf.vc_of[l][1]) for l in cl[:-1]) + f" or slot {cnf.vc_of[cl[-1]][1]}"
        else:
            (v1, c1), (v2, c2) = cnf.vc_of[-cl[0]], cnf.vc_of[-cl[1]]
            s = f"if {at(v1, c1)}, then the {ex[v2]} exam is not in slot {c2}"
        lines.append(f"{i}. {s[0].upper()}{s[1:]}.")
    if task in ("FIND", "DECIDE"):
        lines.append("Question: Can all of these statements be true at the same time? If they can, describe a situation in which they are all true.")
        fmt = ("Think it through as carefully as you need. If they cannot all be true, finish with the line \"ANSWER: NO\". "
               "Otherwise finish with the line \"ANSWER:\" followed by one line `exam: slot` per exam, in this order: "
               f"{answer_order_text(ex)}.")
    else:
        w, c = query
        lines.append(f"Question: Does it follow that the {ex[w]} exam is in slot {c}?")
        lines.append("A conclusion follows only if it must be true whenever all of the statements are true.")
        fmt = "Think it through as carefully as you need. Finish with a final line that is exactly \"ANSWER: YES\" or \"ANSWER: NO\"."
    return "\n".join(lines) + "\n\n" + fmt, fmt


C_HINT = ("This formula encodes the colouring of a graph with three colours. For each vertex v and each colour c there is "
          "one variable meaning \"vertex v has colour c\". The first group of clauses says each vertex gets at least one "
          "colour, the second group says it gets at most one, and the remaining clauses say that two vertices joined by "
          "an edge do not get the same colour.")
C_NEUTRAL = ("This formula was produced by a generator program for a test of satisfiability checking. The clauses are printed "
             "in the order in which the program wrote them out, and the variables are numbered in the order the program "
             "created them. Nothing about how the formula was made is needed to answer the question below.")
L_HINT = ("These statements describe an exam timetable with three slots. Each exam is in exactly one slot, and every "
          "statement of the form \"If the A exam is in slot c, then the B exam is not in slot c\" with two different exams "
          "means that exams A and B share a student and must be in different slots.")
L_NEUTRAL = ("These statements were copied from the school office's records in the order in which they were filed. Some "
             "of them repeat information in a different form, and none of them is more important than another. Read "
             "them all before answering the question below.")


def count_tokens(text):
    import tiktoken
    enc = tiktoken.get_encoding("o200k_base")
    return len(enc.encode(text))
