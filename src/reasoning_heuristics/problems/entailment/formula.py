"""Propositional premises in a fixed grammar, exact entailment, and NL rendering.

Grammar (formulas are nested tuples, JSON-serialised as lists):

    ("lit", atom, positive)          an atom or its negation
    ("and", (f1, ..., fk))           conjunction
    ("or", (f1, ..., fk))            inclusive disjunction ("either ... or ...")
    ("if", antecedent, consequent)   material conditional
    ("iff", a, b)                    biconditional
    ("nand", (f1, ..., fk))          "not both"
    ("nor", (f1, ..., fk))           "neither ... nor" (A/H E5's inverted reading of "either ... or")

Atoms are strings. Atoms of the form "subject:predicate" render as "the subject is
predicate"; any other atom renders as itself (letters style, C E5).

Generator path: truth tables (`entails`, `models`). Validator path: `entails_sat`
(CNF expansion + python-sat), which shares no code with the truth table.
"""

from __future__ import annotations

import itertools
from typing import Any, Iterable

from pysat.solvers import Minisat22

Formula = tuple
World = dict[str, bool]


def lit(atom: str, positive: bool = True) -> Formula:
    return ("lit", atom, positive)


def conj(*fs: Formula) -> Formula:
    return fs[0] if len(fs) == 1 else ("and", tuple(fs))


def disj(*fs: Formula) -> Formula:
    return ("or", tuple(fs))


def cond(a: Formula, b: Formula) -> Formula:
    return ("if", a, b)


def iff(a: Formula, b: Formula) -> Formula:
    return ("iff", a, b)


def nand(*fs: Formula) -> Formula:
    return ("nand", tuple(fs))


# --- structure ---------------------------------------------------------------------------


def atoms(f: Formula) -> list[str]:
    """Atoms in order of first mention."""
    out: dict[str, None] = {}

    def walk(g: Formula) -> None:
        op = g[0]
        if op == "lit":
            out.setdefault(g[1], None)
        elif op in ("and", "or", "nand", "nor"):
            for h in g[1]:
                walk(h)
        elif op in ("if", "iff"):
            walk(g[1])
            walk(g[2])
        else:
            raise ValueError(f"unknown operator {op}")

    walk(f)
    return list(out)


def atoms_of(fs: Iterable[Formula]) -> list[str]:
    out: dict[str, None] = {}
    for f in fs:
        for a in atoms(f):
            out.setdefault(a, None)
    return list(out)


def literals(f: Formula) -> list[tuple[str, bool]]:
    """Signed literal occurrences in surface order (with repetition)."""
    op = f[0]
    if op == "lit":
        return [(f[1], f[2])]
    if op in ("and", "or", "nand", "nor"):
        return [l for g in f[1] for l in literals(g)]
    return literals(f[1]) + literals(f[2])


def evaluate(f: Formula, w: World) -> bool:
    op = f[0]
    if op == "lit":
        return w[f[1]] == f[2]
    if op == "and":
        return all(evaluate(g, w) for g in f[1])
    if op == "or":
        return any(evaluate(g, w) for g in f[1])
    if op == "nand":
        return not all(evaluate(g, w) for g in f[1])
    if op == "nor":
        return not any(evaluate(g, w) for g in f[1])
    if op == "if":
        return (not evaluate(f[1], w)) or evaluate(f[2], w)
    if op == "iff":
        return evaluate(f[1], w) == evaluate(f[2], w)
    raise ValueError(op)


def worlds(atom_list: list[str]) -> Iterable[World]:
    for bits in itertools.product((True, False), repeat=len(atom_list)):
        yield dict(zip(atom_list, bits))


def models(premises: list[Formula], atom_list: list[str] | None = None) -> list[World]:
    atom_list = atom_list if atom_list is not None else atoms_of(premises)
    return [w for w in worlds(atom_list) if all(evaluate(p, w) for p in premises)]


def entails(premises: list[Formula], conclusion: Formula) -> bool:
    """Truth-table entailment (generator path). Inconsistent premises entail everything."""
    atom_list = atoms_of(list(premises) + [conclusion])
    return all(evaluate(conclusion, w) for w in models(premises, atom_list))


def countermodels(premises: list[Formula], conclusion: Formula) -> list[World]:
    atom_list = atoms_of(list(premises) + [conclusion])
    return [w for w in models(premises, atom_list) if not evaluate(conclusion, w)]


def rho(premises: list[Formula], conclusion: Formula) -> float:
    """Counter-model fraction |Mod(P & ~C)| / |Mod(P)| over the joint atoms (A/H's ρ)."""
    atom_list = atoms_of(list(premises) + [conclusion])
    ms = models(premises, atom_list)
    if not ms:
        raise ValueError("inconsistent premises")
    return sum(1 for w in ms if not evaluate(conclusion, w)) / len(ms)


# --- CNF expansion and SAT-based entailment (validator path) -----------------------------


def nnf(f: Formula, negate: bool = False) -> Formula:
    op = f[0]
    if op == "lit":
        return ("lit", f[1], f[2] != negate)
    if op == "and":
        parts = tuple(nnf(g, negate) for g in f[1])
        return ("or", parts) if negate else ("and", parts)
    if op == "or":
        parts = tuple(nnf(g, negate) for g in f[1])
        return ("and", parts) if negate else ("or", parts)
    if op == "nand":
        return nnf(("and", f[1]), not negate)
    if op == "nor":
        return nnf(("or", f[1]), not negate)
    if op == "if":
        return nnf(("or", (nnf(f[1], True), f[2])), negate)
    if op == "iff":
        a, b = f[1], f[2]
        both = ("and", (a, b))
        neither = ("and", (nnf(a, True), nnf(b, True)))
        return nnf(("or", (both, neither)), negate)
    raise ValueError(op)


def clauses_of(f: Formula) -> list[frozenset[tuple[str, bool]]]:
    """CNF by distribution over an NNF formula (fine for the small premises used here)."""
    g = nnf(f)

    def rec(h: Formula) -> list[frozenset[tuple[str, bool]]]:
        if h[0] == "lit":
            return [frozenset({(h[1], h[2])})]
        if h[0] == "and":
            return [c for part in h[1] for c in rec(part)]
        if h[0] == "or":
            acc = [frozenset()]
            for part in h[1]:
                acc = [a | b for a in acc for b in rec(part)]
            return acc
        raise ValueError(h[0])

    out = []
    for c in rec(g):
        if not any((a, not s) in c for a, s in c):  # drop tautologies
            out.append(c)
    return out


def entails_sat(premises: list[Formula], conclusion: Formula) -> bool:
    atom_list = atoms_of(list(premises) + [conclusion])
    idx = {a: i + 1 for i, a in enumerate(atom_list)}
    clauses = [c for p in premises for c in clauses_of(p)] + clauses_of(nnf(conclusion, True))
    dimacs = [[idx[a] if s else -idx[a] for a, s in c] for c in clauses]
    if any(not c for c in dimacs):
        return True  # an empty clause: P & ~C trivially inconsistent
    with Minisat22(bootstrap_with=dimacs) as s:
        return not s.solve()


# --- JSON ---------------------------------------------------------------------------------


def to_json(f: Formula) -> Any:
    op = f[0]
    if op == "lit":
        return ["lit", f[1], f[2]]
    if op in ("and", "or", "nand", "nor"):
        return [op, [to_json(g) for g in f[1]]]
    return [op, to_json(f[1]), to_json(f[2])]


def from_json(data: Any) -> Formula:
    op = data[0]
    if op == "lit":
        return ("lit", data[1], bool(data[2]))
    if op in ("and", "or", "nand", "nor"):
        return (op, tuple(from_json(g) for g in data[1]))
    return (op, from_json(data[1]), from_json(data[2]))


def canonical(f: Formula) -> Any:
    """Order-free canonical form (sorted juncts) for content hashes."""
    op = f[0]
    if op == "lit":
        return ["lit", f[1], f[2]]
    if op in ("and", "or", "nand", "nor", "iff"):
        parts = [canonical(g) for g in (f[1] if op != "iff" else (f[1], f[2]))]
        return [op, sorted(parts, key=repr)]
    return [op, canonical(f[1]), canonical(f[2])]


# --- natural language -----------------------------------------------------------------------


def render_lit(atom: str, positive: bool) -> str:
    if ":" in atom:
        subject, predicate = atom.split(":", 1)
        return f"the {subject} is {'' if positive else 'not '}{predicate}"
    return atom if positive else f"not {atom}"


def render(f: Formula, top: bool = True) -> str:
    """English rendering; `top` adds sentence-level framing ("Either ...", "If ...")."""
    op = f[0]
    if op == "lit":
        return render_lit(f[1], f[2])
    if op == "and":
        return " and ".join(render(g, False) for g in f[1])
    if op == "or":
        parts = [render(g, False) for g in f[1]]
        return "either " + ", or ".join(parts) if top else ", or ".join(parts)
    if op == "nand":
        return "not both " + " and ".join(render(g, False) for g in f[1])
    if op == "nor":
        return "neither " + " nor ".join(render(g, False) for g in f[1])
    if op == "if":
        return f"if {render(f[1], False)}, then {render(f[2], False)}"
    if op == "iff":
        return f"{render(f[1], False)} if and only if {render(f[2], False)}"
    raise ValueError(op)


def sentence(f: Formula) -> str:
    text = render(f)
    return text[0].upper() + text[1:] + "."
