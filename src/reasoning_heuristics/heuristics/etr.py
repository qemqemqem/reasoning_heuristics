"""ETR members, wrapping PyETR 1.0.0 (pinned in pyproject.toml).

    ETR-default  dif for yes/no: pyetr.inference.default_procedure_does_it_follow
                 dip for MC: pyetr.inference.default_inference_procedure, mapped to the
              MC option that is logically equivalent to PyETR's output ("None of these"
              if no option is)
    ETR-1p    one pass only: yes/no = step (1) of dif with no reversed retry; MC = step (1)
              of dip with no retry

Views (B4/C4 §1.1): atoms "subject:predicate" become unary predicates over constants,
`predicate(subject())`; other atoms become nullary predicates. No issue marks (nothing
in the English marks issue). Conditionals use rendering R1 `{B}^{A}` or R2 `{A B}^{A}`
(params["rendering"]); "iff" is `{A B, ~A ~B}`.
"""

from __future__ import annotations

import re
from typing import Any

from pyetr import View
from pyetr.inference import basic_step, default_inference_procedure, default_procedure_does_it_follow
from pyetr.stateset import SetOfStates, State

from reasoning_heuristics.heuristics.base import Prediction, member
from reasoning_heuristics.heuristics.entailment import cat_lits, is_categorical, mc_letter
from reasoning_heuristics.heuristics.tasks import EntailmentTask
from reasoning_heuristics.problems.entailment import formula as F

D = "entailment"
_IDENT = re.compile(r"^[a-z][a-z0-9]*$")


def atom_text(atom: str, positive: bool) -> str:
    if ":" in atom:
        subj, pred = atom.split(":", 1)
        assert _IDENT.match(subj) and _IDENT.match(pred), atom
        core = f"{pred}({subj}())"
    else:
        core = f"p{atom}()"
    return core if positive else "~" + core


def _state(lits) -> str:
    return "".join(atom_text(a, s) for a, s in lits)


def view_text(f: F.Formula, rendering: str) -> str:
    if is_categorical(f):
        return "{" + _state(cat_lits(f)) + "}"
    op = f[0]
    if op == "or":
        return "{" + ",".join(_state(cat_lits(d)) for d in f[1]) + "}"
    if op == "if":
        a, b = cat_lits(f[1]), cat_lits(f[2])
        if rendering == "R1":
            return "{" + _state(b) + "}^{" + _state(a) + "}"
        if rendering == "R2":
            return "{" + _state(a + b) + "}^{" + _state(a) + "}"
        raise ValueError(rendering)
    if op == "iff":
        a, b = cat_lits(f[1]), cat_lits(f[2])
        return "{" + _state(a + b) + "," + _state([(x, not s) for x, s in a + b]) + "}"
    if op == "nand":
        return "{" + ",".join(_state([(x, not s)]) for d in f[1] for x, s in cat_lits(d)) + "}"
    raise ValueError(f"no ETR view for {op}")


def views(task: EntailmentTask, rendering: str) -> list[View]:
    return [View.from_str(view_text(p, rendering)) for p in task.premises]


def view_to_formula(v: View, atom_names: dict[str, str]) -> F.Formula | None:
    """A view's stage as a DNF formula over our atoms (None for verum/falsum)."""
    if v.is_verum or v.is_falsum:
        return None
    disjuncts = []
    for state in v.stage:
        lits = []
        for a in state:
            key = f"{a.predicate.name}({','.join(str(t) for t in a.terms)})"
            lits.append(F.lit(atom_names[key], bool(a.predicate.verifier)))
        disjuncts.append(F.conj(*lits) if lits else None)
    if any(d is None for d in disjuncts):
        return None
    return disjuncts[0] if len(disjuncts) == 1 else F.disj(*disjuncts)


def _atom_names(task: EntailmentTask) -> dict[str, str]:
    names = {}
    for a in F.atoms_of(list(task.premises) + ([task.probe] if task.probe else []) + list(task.options)):
        text = atom_text(a, True)
        m = re.match(r"(\w+)\((\w*)\(?\)?\)", text)
        pred, subj = m.group(1), m.group(2)
        names[f"{pred}({subj})" if subj else f"{pred}()"] = a
    return names


def _one_pass_yn(vs: list[View], target: View) -> bool:
    g = basic_step(vs)
    out = g.suppose(
        View.with_restriction(stage=target.supposition, supposition=SetOfStates({State({})}),
                              dependency_relation=target.dependency_relation,
                              issue_structure=target.issue_structure, weights=None)
    ).query(target)
    return out == target


def _one_pass_dip(vs: list[View]) -> View:
    g = basic_step(vs)
    for i, v in enumerate(vs):
        g = g.factor(v.depose() if i == 0 else v)
    return View.get_verum() if (g.is_verum or g.is_falsum) else g


def _mc_from_view(task: EntailmentTask, out: View) -> tuple[str, str]:
    f = view_to_formula(out, _atom_names(task))
    if f is None:
        return mc_letter(task, None), "verum"
    for i, o in enumerate(task.options):
        if F.entails([f], o) and F.entails([o], f):
            return mc_letter(task, i), F.render(f)
    return mc_letter(task, None), F.render(f)


@member("ETR-default", "B4/C4", D, "premise-by-premise processing; keeps the cases sharing most literals with each premise; contradicted cases kept until the end; a second pass from the other end if the first is inconclusive")
def etr_default(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    """The default PyETR procedure for the task's format (dif for YN, dip for MC)."""
    rendering = params.get("rendering", "R1")
    vs = views(task, rendering)
    if task.fmt == "YN":
        ok = default_procedure_does_it_follow(vs, View.from_str(view_text(task.probe, rendering)))
        return Prediction("YES" if ok else "NO", {"procedure": "default_procedure_does_it_follow", "rendering": rendering})
    if task.fmt == "MC":
        letter, text = _mc_from_view(task, default_inference_procedure(vs))
        return Prediction(letter, {"procedure": "default_inference_procedure", "output": text, "rendering": rendering})
    raise ValueError(task.fmt)


@member("ETR-1p", "B4/C4", D, "premise-by-premise processing in a single pass; no second pass")
def etr_one_pass(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    rendering = params.get("rendering", "R1")
    vs = views(task, rendering)
    if task.fmt == "YN":
        ok = _one_pass_yn(vs, View.from_str(view_text(task.probe, rendering)))
        return Prediction("YES" if ok else "NO", {"procedure": "one pass", "rendering": rendering})
    if task.fmt == "MC":
        letter, text = _mc_from_view(task, _one_pass_dip(vs))
        return Prediction(letter, {"procedure": "one pass", "output": text, "rendering": rendering})
    raise ValueError(task.fmt)
