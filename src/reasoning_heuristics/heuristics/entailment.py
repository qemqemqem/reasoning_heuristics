"""Entailment members: B4 restriction (FIRST, MATCH, BICOND, CLOSED-WORLD, mental models),
C4 ONLINE-STATE(k), C1 GREEDY-MODEL and GREEDY-CM, B1 UP-k, A1/A2 cues, A3 textbook
transfer, H guesses, nuisance models and the exact solver.

Definitions follow B4/C4 §1.1 (and A/H §1.5 for the cues). Output vocabulary:
YN -> "YES" / "NO" / "X" (the member's state is contradictory; X maps to NO in a two-way
format); MC -> the letter of the strongest displayed option entailed by the member's model
set (ties: first in canonical order; none: the "None of these" letter); OPEN -> the sorted
list of entailed literals, or "NOTHING".

Mental models (MM-S1, MM-G) are the simplified form the B4/C4 doc specifies (initial
models with the principle of truth, an implicit model for conditionals, Girotto fleshing);
the doc itself marks them as a provisional port, to be validated against mSentential.
"""

from __future__ import annotations

import itertools
from collections import Counter
from typing import Any, Callable

from reasoning_heuristics.heuristics.base import Prediction, member
from reasoning_heuristics.heuristics.tasks import EntailmentTask
from reasoning_heuristics.problems.entailment import formula as F

D = "entailment"
Lit = tuple[str, bool]
State = frozenset  # of Lit


# --- structure helpers ----------------------------------------------------------------------


def is_categorical(f: F.Formula) -> bool:
    return f[0] == "lit" or (f[0] == "and" and all(g[0] == "lit" for g in f[1]))


def cat_lits(f: F.Formula) -> list[Lit]:
    if f[0] == "lit":
        return [(f[1], f[2])]
    if f[0] == "and" and all(g[0] == "lit" for g in f[1]):
        return [(g[1], g[2]) for g in f[1]]
    raise ValueError(f"not categorical: {f}")


def neg(l: Lit) -> Lit:
    return (l[0], not l[1])


def consistent(s) -> bool:
    return not any(neg(l) in s for l in s)


def alts(p: F.Formula) -> list[State]:
    """Minimal alternatives of a premise, in surface order (B4/C4 §1.1 table)."""
    op = p[0]
    if is_categorical(p):
        return [frozenset(cat_lits(p))]
    if op == "or":
        return [frozenset(cat_lits(d)) for d in p[1]]
    if op == "if":
        a, b = cat_lits(p[1]), cat_lits(p[2])
        return [frozenset(a + b)] + [frozenset({neg(x)}) for x in a]
    if op == "iff":
        a, b = cat_lits(p[1]), cat_lits(p[2])
        if len(a) != 1 or len(b) != 1:
            raise ValueError("iff alternatives defined for literal sides only")
        return [frozenset(a + b), frozenset({neg(a[0]), neg(b[0])})]
    if op == "nand":
        return [frozenset({neg(x)}) for d in p[1] for x in cat_lits(d)]
    raise ValueError(f"no alternatives for {op}")


def holds_in_state(f: F.Formula, s) -> bool:
    """Membership semantics on a partial state (a set of literals)."""
    op = f[0]
    if op == "lit":
        return (f[1], f[2]) in s
    if op == "and":
        return all(holds_in_state(g, s) for g in f[1])
    if op == "or":
        return any(holds_in_state(g, s) for g in f[1])
    raise ValueError(f"membership semantics undefined for {op}")


def stronger_order(task: EntailmentTask) -> list[int]:
    return sorted(range(len(task.options)), key=lambda i: repr(F.canonical(task.options[i])))


def mc_letter(task: EntailmentTask, index: int | None) -> str:
    return chr(ord("A") + (len(task.options) if index is None else index))


def mc_choose(task: EntailmentTask, entailed: Callable[[F.Formula], bool]) -> str:
    """Strongest displayed option the member's model set entails; 'None of these' if none."""
    ok = [i for i in range(len(task.options)) if entailed(task.options[i])]
    if not ok:
        return mc_letter(task, None)
    maximal = [i for i in ok if all(F.entails([task.options[i]], task.options[j]) for j in ok)]
    pool = maximal or ok
    canon = stronger_order(task)
    best = min(pool, key=canon.index)
    return mc_letter(task, best)


def effective_premises(task: EntailmentTask) -> list[F.Formula]:
    """Premises as the stated rule reads them (A/H E5 'nor' reading of 'either ... or')."""
    if task.reading == "standard":
        return list(task.premises)
    if task.reading == "nor":
        return [("nor", p[1]) if p[0] == "or" else p for p in task.premises]
    raise ValueError(task.reading)


def entailed_literals(premises: list[F.Formula], atoms: list[str]) -> list[str]:
    ms = F.models(premises, atoms)
    out = []
    for a in atoms:
        for pol in (True, False):
            if ms and all(w[a] == pol for w in ms):
                out.append(F.render_lit(a, pol))
    return sorted(out)


def answer_from_premises(task: EntailmentTask, premises: list[F.Formula]) -> str | list[str]:
    """EXACT on a (possibly rewritten) premise list, in the task's format."""
    all_atoms = F.atoms_of(list(premises) + ([task.probe] if task.probe is not None else []) + list(task.options))
    if not F.models(premises, all_atoms):
        return "X"
    if task.fmt == "YN":
        return "YES" if F.entails(premises, task.probe) else "NO"
    if task.fmt == "MC":
        return mc_choose(task, lambda o: F.entails(premises, o))
    if task.fmt == "OPEN":
        lits = entailed_literals(premises, F.atoms_of(task.premises))
        return lits or "NOTHING"
    raise ValueError(task.fmt)


def answer_from_states(task: EntailmentTask, states: list, implicit: bool = False) -> str:
    """Membership-semantics answer from a list of partial states (ONL, MM)."""
    if not states:
        return "NO" if task.fmt == "YN" else mc_letter(task, None)
    if task.fmt == "YN":
        if implicit:
            return "NO"
        return "YES" if all(holds_in_state(task.probe, s) for s in states) else "NO"
    if task.fmt == "MC":
        if implicit:
            return mc_letter(task, None)
        return mc_choose(task, lambda o: all(holds_in_state(o, s) for s in states))
    raise ValueError(task.fmt)


def describe(states) -> list[list[str]]:
    return [sorted(F.render_lit(a, p) for a, p in s) for s in states]


# --- exact -------------------------------------------------------------------------------------


@member("EXACT", "null", D, "fully explicit cases or a truth table; the counter-model appears when the conclusion does not follow")
def exact(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    prem = effective_premises(task)
    trace = {}
    if task.probe is not None:
        trace["countermodels"] = len(F.countermodels(prem, task.probe))
    return Prediction(answer_from_premises(task, prem), trace)


# --- B4 restriction ------------------------------------------------------------------------------


@member("FIRST", "B4", D, "commits to the first-listed disjunct of each disjunction; the second disjunct is never developed")
def first(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    rewritten = [p[1][0] if p[0] == "or" else p for p in effective_premises(task)]
    return Prediction(answer_from_premises(task, rewritten), {"kept": [F.render(p) for p in rewritten]})


def _match(task: EntailmentTask, later_only: bool, polarity: bool) -> Prediction:
    prem = list(effective_premises(task))
    rewrites = []
    for i, p in enumerate(prem):
        if p[0] != "or":
            continue
        js = [j for j in range(len(prem)) if j != i and (j > i or not later_only) and is_categorical(prem[j])]
        for j in js:
            cat = cat_lits(prem[j])
            if polarity:
                share = [d for d in p[1] if set(cat_lits(d)) & set(cat)] if all(is_categorical(d) for d in p[1]) else []
            else:
                atoms_j = {a for a, _ in cat}
                share = [d for d in p[1] if {a for a, _ in cat_lits(d)} & atoms_j] if all(is_categorical(d) for d in p[1]) else []
            if 0 < len(share) < len(p[1]):
                prem[i] = share[0] if len(share) == 1 else ("or", tuple(share))
                rewrites.append({"premise": i + 1, "by": j + 1, "kept": F.render(prem[i])})
            break  # only the first categorical j is consulted
    return Prediction(answer_from_premises(task, prem), {"rewrites": rewrites})


@member("MATCH-L", "B4", D, "SELECT-BY-MATCH: keeps the disjunct that a later categorical premise repeats; other disjuncts dropped")
def match_l(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    return _match(task, later_only=True, polarity=True)


@member("MATCH-A", "B4", D, "SELECT-BY-MATCH with a categorical premise in either position")
def match_a(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    return _match(task, later_only=False, polarity=True)


@member("MATCH-atom", "B4", D, "SELECT-BY-MATCH on shared atoms, ignoring polarity (sensitivity variant)")
def match_atom(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    return _match(task, later_only=False, polarity=False)


@member("BICOND", "B4", D, "CONVERSE stated or used ('so if B then A', 'not A, so not B'), or 'if' read as 'if and only if'")
def bicond(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    rewritten = [("iff", p[1], p[2]) if p[0] == "if" else p for p in effective_premises(task)]
    return Prediction(answer_from_premises(task, rewritten), {"converses_added": sum(p[0] == "if" for p in task.premises)})


@member("BICOND-PRAG", "B4", D, "reads 'if' as 'iff' as a pragmatic default; the reading disappears once the prompt says 'if X, then Y' does not mean 'if Y, then X'")
def bicond_pragmatic(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    """B4/C4 E2's pragmatic variant: BICOND unless the item carries the anti-converse instruction
    (params["instruction"]), in which case the conditional is read as stated."""
    if params["instruction"]:
        return Prediction(answer_from_premises(task, effective_premises(task)), {"reading": "as stated (instructed)"})
    pred = bicond(task, {})
    return Prediction(pred.answer, {"reading": "biconditional", **pred.trace_features})


@member("CW-COMP", "B4", D, "listed antecedents treated as the only possible causes (Clark completion)")
def cw_comp(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    """Clark completion (B4/C4 §1.1): for each *atom* E that is a rule consequent, add
    E -> OR(antecedents of the rules for E). Negated consequents are not heads, so a rule
    "if A then not B" is left as stated. With one positive-headed rule this is BICOND."""
    prem = list(effective_premises(task))
    heads: dict[tuple, list] = {}
    for p in prem:
        if p[0] == "if" and p[2][0] == "lit" and p[2][2]:
            heads.setdefault(tuple(F.to_json(p[2])), []).append(p[1])
    for head, bodies in heads.items():
        body = bodies[0] if len(bodies) == 1 else ("or", tuple(bodies))
        prem.append(("if", F.from_json(list(head)), body))
    return Prediction(answer_from_premises(task, prem), {"completions": len(heads)})


@member("CW-MIN", "B4", D, "ABSENCE->FALSE: atoms not forced true are taken to be false ('nothing says X, so X is false')")
def cw_min(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    """Circumscription: the conclusion must hold in every subset-minimal model (minimal true atoms)."""
    prem = effective_premises(task)
    extra = ([task.probe] if task.probe is not None else []) + list(task.options)
    atoms = F.atoms_of(list(prem) + extra)
    ms = F.models(prem, atoms)
    if not ms:
        return Prediction("X", {})
    trues = [frozenset(a for a in atoms if w[a]) for w in ms]
    minimal = [w for w, t in zip(ms, trues) if not any(o < t for o in trues)]
    if task.fmt == "YN":
        ans = "YES" if all(F.evaluate(task.probe, w) for w in minimal) else "NO"
    else:
        ans = mc_choose(task, lambda o: all(F.evaluate(o, w) for w in minimal))
    return Prediction(ans, {"minimal_models": len(minimal)})


# --- mental models (simplified, per the B4/C4 doc) -----------------------------------------------

IMPLICIT = "..."


def mm_initial(p: F.Formula) -> tuple[list[State], bool]:
    """Initial models under the principle of truth, and whether an implicit model is present."""
    if is_categorical(p):
        return [frozenset(cat_lits(p))], False
    if p[0] == "or":
        ds = [frozenset(cat_lits(d)) for d in p[1]]
        both = [frozenset().union(*c) for r in range(2, len(ds) + 1) for c in itertools.combinations(ds, r)]
        return ds + [m for m in both if consistent(m)], False
    if p[0] == "if":
        return [frozenset(cat_lits(p[1]) + cat_lits(p[2]))], True
    if p[0] == "iff":
        a, b = cat_lits(p[1]), cat_lits(p[2])
        return [frozenset(a + b), frozenset([neg(a[0]), neg(b[0])])], False
    if p[0] == "nand":
        lits = [x for d in p[1] for x in cat_lits(d)]
        return [frozenset({neg(x)}) for x in lits], False
    raise ValueError(p[0])


def fully_explicit_if(p: F.Formula) -> list[State]:
    a, b = cat_lits(p[1]), cat_lits(p[2])
    atoms = [x[0] for x in a + b]
    out = []
    for bits in itertools.product((True, False), repeat=len(atoms)):
        w = dict(zip(atoms, bits))
        if F.evaluate(p, w):
            out.append(frozenset(w.items()))
    return out


def mental_models(task: EntailmentTask, variant: str) -> tuple[list[State], bool, dict]:
    """variant: 'open' (MM-S1 default), 'elim' (categoricals eliminate unmatched disjunction models),
    'girotto' (MM-G: a categorical read before a conditional fleshes it out)."""
    prem = effective_premises(task)
    per = [mm_initial(p) for p in prem]
    per = [(list(ms), imp) for ms, imp in per]
    if variant == "girotto":
        for j, p in enumerate(prem):
            if p[0] != "if":
                continue
            for i in range(j):
                if not is_categorical(prem[i]):
                    continue
                for l in cat_lits(prem[i]):
                    if not any(l in m for m in per[j][0]):
                        extra = [m for m in fully_explicit_if(p) if l in m and m not in per[j][0]]
                        per[j][0].extend(extra)
    if variant == "elim":
        cats = [l for p in prem if is_categorical(p) for l in cat_lits(p)]
        for j, p in enumerate(prem):
            if p[0] != "or":
                continue
            ms = per[j][0]
            for l in cats:
                survivors = [m for m in ms if neg(l) not in m]
                if any(l in m for m in survivors):
                    ms = [m for m in survivors if l in m]
            per[j] = (ms, per[j][1])
    states: list[State] = [frozenset()]
    implicit_alive = False
    for j, (ms, imp) in enumerate(per):
        nxt = []
        for s in states:
            for m in ms:
                u = s | m
                if consistent(u) and u not in nxt:
                    nxt.append(u)
        if imp:
            # The implicit model survives a categorical context only if nothing in the other
            # premises matches a literal of this conditional's explicit models.
            explicit_lits = set().union(*ms)
            others = [l for i, p in enumerate(prem) if i != j and is_categorical(p) for l in cat_lits(p)]
            if not any(l in explicit_lits for l in others):
                implicit_alive = True
        states = nxt
    return states, implicit_alive, {"models": describe(states), "implicit": implicit_alive}


@member("MM-S1", "B4", D, "lists only the possibilities in which the clauses are true (negative literals rare); conditionals get one explicit case plus 'other cases'")
def mm_s1(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    variant = params.get("variant", "open")
    states, implicit, trace = mental_models(task, variant)
    return Prediction(answer_from_states(task, states, implicit), trace)


@member("MM-G", "B4", D, "as MM-S1, but a categorical premise read before a conditional makes the trace build the conditional's matching cases")
def mm_g(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    states, implicit, trace = mental_models(task, "girotto")
    return Prediction(answer_from_states(task, states, implicit), trace)


# --- C4 online ------------------------------------------------------------------------------------


@member("ONL", "C4", D, "strict presentation order, no back-references; at most k cases kept; RESET when a premise contradicts every kept case")
def online_state(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    """ONLINE-STATE(k): truncation = primacy (keep the first k); on an empty state reset (default)
    or strict (answer X)."""
    k = params["k"]
    on_empty = params.get("on_empty", "reset")
    states: list[State] = [frozenset()]
    sizes, resets = [], 0
    for p in effective_premises(task):
        nxt: list[State] = []
        for s in states:
            for a in alts(p):
                u = s | a
                if consistent(u) and u not in nxt:
                    nxt.append(u)
        if not nxt:
            if on_empty == "strict":
                return Prediction("X", {"kept_after_each": sizes + [0]})
            nxt = list(alts(p))
            resets += 1
        states = nxt[:k]
        sizes.append(len(states))
    return Prediction(answer_from_states(task, states), {"kept_after_each": sizes, "resets": resets, "final": describe(states)})


# --- C1 ---------------------------------------------------------------------------------------------


def three_valued(f: F.Formula, w: dict[str, bool]) -> bool | None:
    """Kleene evaluation on a partial world."""
    op = f[0]
    if op == "lit":
        return None if f[1] not in w else (w[f[1]] == f[2])
    if op in ("and", "or", "nand", "nor"):
        vals = [three_valued(g, w) for g in f[1]]
        if op in ("and", "nand"):
            r = False if False in vals else (None if None in vals else True)
            return r if op == "and" else (None if r is None else not r)
        r = True if True in vals else (None if None in vals else False)
        return r if op == "or" else (None if r is None else not r)
    if op == "if":
        a, b = three_valued(f[1], w), three_valued(f[2], w)
        if a is False or b is True:
            return True
        if a is True and b is False:
            return False
        return None
    if op == "iff":
        a, b = three_valued(f[1], w), three_valued(f[2], w)
        return None if a is None or b is None else a == b
    raise ValueError(op)


@member("GREEDY-MODEL", "C1", D, "assigns atoms in mention order, true unless that falsifies a premise; answers from that single model")
def greedy_model(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    prem = effective_premises(task)
    extra = ([task.probe] if task.probe is not None else []) + list(task.options)
    w: dict[str, bool] = {}
    for a in F.atoms_of(list(prem) + extra):
        for val in (True, False):
            w[a] = val
            if all(three_valued(p, w) is not False for p in prem):
                break
        else:
            return Prediction("X", {"dead_end": a})
    if task.fmt == "YN":
        return Prediction("YES" if F.evaluate(task.probe, w) else "NO", {"model": w})
    return Prediction(mc_choose(task, lambda o: F.evaluate(o, w)), {"model": w})


def ordered_clauses(f: F.Formula) -> list[tuple[Lit, ...]]:
    """CNF by distribution, keeping surface order of clauses and literals."""
    g = F.nnf(f)

    def rec(h):
        if h[0] == "lit":
            return [((h[1], h[2]),)]
        if h[0] == "and":
            return [c for part in h[1] for c in rec(part)]
        if h[0] == "or":
            acc = [()]
            for part in h[1]:
                acc = [a + b for a in acc for b in rec(part)]
            return acc
        raise ValueError(h[0])

    out = []
    for c in rec(g):
        c = tuple(dict.fromkeys(c))
        if not any(neg(l) in c for l in c) and c not in out:
            out.append(c)
    return out


@member("GREEDY-CM", "C1", D, "builds one countermodel greedily in premise order; 'does not follow' only if the greedy assignment works")
def greedy_cm(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    """CNF(P1 & ... & Pk & ~C), ~C last (variant 'neg_first'), then GREEDY-MENTION. A satisfying
    assignment found -> NO; otherwise YES. Errs only by commission."""
    from reasoning_heuristics.heuristics.sat import greedy_run
    from reasoning_heuristics.problems.sat.cnf import CNF

    parts = list(effective_premises(task))
    negc = F.nnf(task.probe, True)
    parts = [negc] + parts if params.get("neg_first") else parts + [negc]
    clauses = [c for p in parts for c in ordered_clauses(p)]
    atoms = list(dict.fromkeys(a for c in clauses for a, _ in c))
    cnf = CNF(tuple(atoms), tuple(tuple((atoms.index(a) + 1) * (1 if s else -1) for a, s in c) for c in clauses))
    values, trace = greedy_run(cnf, cnf.mention_order(), {}, "ABORT")
    found = values is not None
    return Prediction("NO" if found else "YES", {"countermodel_found": found, **trace})


# --- B1 ----------------------------------------------------------------------------------------------


@member("UP-k", "B1", D, "a derivation chain by unit propagation; stops after k rounds; YES only if the probe is derived")
def up_k(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    k = params["k"]
    clauses = [c for p in effective_premises(task) for c in F.clauses_of(p)]
    known: dict[str, bool] = {}
    for c in clauses:
        if len(c) == 1:
            (a, s), = c
            known[a] = s
    for _ in range(k):
        new = {}
        for c in clauses:
            if any(known.get(a) == s for a, s in c):
                continue
            open_l = [(a, s) for a, s in c if a not in known]
            if len(open_l) == 1:
                new[open_l[0][0]] = open_l[0][1]
        if not new:
            break
        known.update(new)
    if task.fmt == "YN":
        probe = cat_lits(task.probe)
        return Prediction("YES" if all(known.get(a) == s for a, s in probe) else "NO", {"derived": len(known)})
    state = frozenset(known.items())
    return Prediction(mc_choose(task, lambda o: holds_in_state(o, state)), {"derived": len(known)})


# --- A cues ---------------------------------------------------------------------------------------------


def _probe_lits(f: F.Formula) -> list[Lit]:
    return F.literals(f)


@member("PRIMACY", "A2", D, "no cases or case lists; the justification quotes only the first premise")
def primacy(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    first_lits = set(F.literals(task.premises[0]))
    if task.fmt == "YN":
        return Prediction("YES" if all(l in first_lits for l in _probe_lits(task.probe)) else "NO", {})
    return Prediction(_overlap_choice(task, first_lits), {})


@member("RECENCY", "A2", D, "no cases or case lists; the justification quotes only the last premise")
def recency(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    last_lits = set(F.literals(task.premises[-1]))
    if task.fmt == "YN":
        return Prediction("YES" if all(l in last_lits for l in _probe_lits(task.probe)) else "NO", {})
    return Prediction(_overlap_choice(task, last_lits), {})


def _overlap_choice(task: EntailmentTask, lits: set) -> str:
    scores = [len(set(F.literals(o)) & lits) for o in task.options]
    best = max(scores, default=0)
    if best == 0:
        return mc_letter(task, None)
    return mc_letter(task, scores.index(best))


@member("AFFIRM", "A2", D, "endorses affirmative conclusions, rejects negated ones")
def affirm(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    if task.fmt != "YN":
        return Prediction(None, {"note": "n/a outside yes/no"})
    return Prediction("YES" if all(s for _, s in _probe_lits(task.probe)) else "NO", {})


@member("ALWAYS-YES", "A1", D, "'follows' asserted without a case analysis")
def always_yes(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    return Prediction("YES" if task.fmt == "YN" else None, {})


@member("NONE", "A1", D, "'nothing follows' / 'cannot tell' without a case analysis")
def none(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    if task.fmt == "YN":
        return Prediction("NO", {})
    if task.fmt == "OPEN":
        return Prediction("NOTHING", {})
    return Prediction(mc_letter(task, None), {})


def literal_counts(task: EntailmentTask) -> Counter:
    return Counter(l for p in task.premises for l in F.literals(p))


def freq_score(task: EntailmentTask, c: F.Formula) -> int:
    counts = literal_counts(task)
    lits = F.literals(c)
    vals = [counts[l] for l in lits]
    return max(vals) if c[0] == "or" else min(vals)


@member("FREQ", "A2", D, "cites how often the conclusion's terms are mentioned")
def freq(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    theta = params.get("theta", 2)
    return Prediction("YES" if freq_score(task, task.probe) >= theta else "NO", {"f(C)": freq_score(task, task.probe), "theta": theta})


def form_of(f: F.Formula) -> str:
    if is_categorical(f):
        return "conj"
    return {"or": "disj", "if": "cond", "iff": "cond", "nand": "disj"}.get(f[0], "disj")


def atmosphere_of(task: EntailmentTask) -> tuple[str, str]:
    forms = Counter(form_of(p) for p in task.premises)
    top = max(forms.values())
    leaders = [f for f in ("disj", "conj", "cond") if forms[f] == top]
    form = "disj" if "disj" in leaders else leaders[0]
    lits = [l for p in task.premises for l in F.literals(p)]
    polarity = "neg" if sum(1 for _, s in lits if not s) * 2 >= len(lits) else "pos"
    return form, polarity


def mood_of(c: F.Formula) -> tuple[str, str]:
    lits = F.literals(c)
    return form_of(c), ("neg" if any(not s for _, s in lits) and sum(not s for _, s in lits) * 2 >= len(lits) else "pos")


@member("ATMOSPHERE", "A2", D, "endorses conclusions whose form and polarity match the premises' overall mood")
def atmosphere(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    atm, mood = atmosphere_of(task), mood_of(task.probe)
    return Prediction("YES" if atm == mood else "NO", {"atmosphere": atm, "mood": mood})


@member("TT", "A3", D, "restates 'either ... or' in its textbook (inclusive) meaning; checks use textbook semantics")
def textbook_transfer(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    std = EntailmentTask(task.premises, task.probe, task.fmt, task.options, "standard")
    return Prediction(answer_from_premises(std, list(task.premises)), {"reading": "standard"})


# --- H and nuisance ----------------------------------------------------------------------------------------


@member("SAMPLE-m", "H", D, "one to three example scenarios with no exhaustiveness claim; YES after only confirming examples", deterministic=False)
def sample_m(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    m = params.get("m", 3)
    prem = effective_premises(task)
    r = F.rho(prem, task.probe)
    p_yes = (1 - r) ** m
    return Prediction(None, {"rho": r, "m": m}, {"YES": p_yes, "NO": 1 - p_yes})


@member("RANDOM", "H", D, "no procedure determines the verdict", deterministic=False)
def random_ent(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    if task.fmt == "YN":
        return Prediction(None, {}, {"YES": 0.5, "NO": 0.5})
    k = len(task.options) + 1
    return Prediction(None, {}, {mc_letter(task, i if i < k - 1 else None): 1 / k for i in range(k)})


@member("NOISY-EXACT", "nuisance", D, "the exact procedure with sporadic slips", deterministic=False)
def noisy_exact(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    """Answer flips w.p. eps = (1 - (1-p)^L)/2, L = number of literal occurrences read."""
    p = params.get("p", 0.01)
    L = sum(len(F.literals(x)) for x in task.premises)
    eps = 0.5 * (1 - (1 - p) ** L)
    g = answer_from_premises(task, effective_premises(task))
    if task.fmt == "YN":
        other = "NO" if g == "YES" else "YES"
        return Prediction(None, {"L": L, "eps": round(eps, 4)}, {g: 1 - eps, other: eps})
    k = len(task.options) + 1
    dist = {mc_letter(task, i if i < k - 1 else None): eps / (k - 1) for i in range(k)}
    dist[g] = 1 - eps
    return Prediction(None, {"L": L, "eps": round(eps, 4)}, dist)


@member("PERCEPTION-NOISE", "nuisance", D, "a misquoted premise that predicts the error", deterministic=False)
def perception_noise(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    """Exact on a misread instance: at most one event, either a dropped premise (p_d each) or a
    flipped literal occurrence (p_f each); probabilities renormalised over 0-1 events."""
    p_d, p_f = params.get("p_d", 0.02), params.get("p_f", 0.01)
    prem = list(effective_premises(task))
    events: list[tuple[float, list]] = []
    n_lits = sum(len(F.literals(p)) for p in prem)
    events.append(((1 - p_d) ** len(prem) * (1 - p_f) ** n_lits, prem))
    for i in range(len(prem)):
        events.append((p_d, prem[:i] + prem[i + 1:]))
    for i, p in enumerate(prem):
        for j in range(len(F.literals(p))):
            events.append((p_f, prem[:i] + [_flip_nth(p, j)] + prem[i + 1:]))
    total = sum(w for w, _ in events)
    dist: Counter = Counter()
    for w, ps in events:
        dist[answer_from_premises(task, ps) if ps else ("NO" if task.fmt == "YN" else mc_letter(task, None))] += w / total
    if "X" in dist:
        dist["NO" if task.fmt == "YN" else mc_letter(task, None)] += dist.pop("X")
    return Prediction(None, {"p_d": p_d, "p_f": p_f}, dict(dist))


def _flip_nth(f: F.Formula, n: int) -> F.Formula:
    counter = [0]

    def rec(g):
        if g[0] == "lit":
            hit = counter[0] == n
            counter[0] += 1
            return ("lit", g[1], (not g[2]) if hit else g[2])
        if g[0] in ("and", "or", "nand", "nor"):
            return (g[0], tuple(rec(h) for h in g[1]))
        return (g[0], rec(g[1]), rec(g[2]))

    return rec(f)
