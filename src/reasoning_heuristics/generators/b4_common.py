"""Shared pieces of the B4/C4 generators: frames (lexicon draws), the prompt template, the
member list, and channels.

The prompt template is the example library's (B4/C4 §2.4): a numbered premise list, the
question, the definition of "follows", and a final ANSWER line. There is no "answer
immediately" instruction. An optional note line sits before the question (E2's neutral
note or instruction), and the theory §5 "prompt given twice" arm repeats the statements.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from reasoning_heuristics.generators.common import Channel, decision_channel, witness_channel
from reasoning_heuristics.heuristics.entailment import mc_letter
from reasoning_heuristics.heuristics.tasks import EntailmentTask
from reasoning_heuristics.lexicon import lexicon
from reasoning_heuristics.problems.entailment import formula as F

THEMES = ("abstract", "people")
ANTONYMS = {frozenset(p) for p in [("wet", "dry"), ("full", "empty"), ("wide", "narrow"), ("open", "shut"),
                                   ("hot", "cold"), ("old", "new"), ("clean", "dirty"), ("soft", "hard"),
                                   ("big", "small"), ("light", "heavy"), ("light", "dark"), ("loud", "quiet"),
                                   ("thin", "thick"), ("smooth", "rough"), ("tall", "short"), ("long", "short"),
                                   ("plain", "fancy"), ("cold", "warm")]}

YN_ANSWER = 'final line "ANSWER: YES" or "ANSWER: NO"'
MC_ANSWER = 'final line "ANSWER: <letter>"'


@dataclass(frozen=True)
class Frame:
    theme: str
    subjects: tuple[str, ...]
    predicates: tuple[str, ...]

    def atom(self, s: int, p: int) -> str:
        subj, pred = self.subjects[s], self.predicates[p]
        return f"{subj}@{pred}" if self.theme == "people" else f"{subj}:{pred}"

    def words(self) -> list[str]:
        return list(self.subjects) + list(self.predicates)

    def to_json(self) -> dict[str, Any]:
        return {"theme": self.theme, "subjects": list(self.subjects), "predicates": list(self.predicates)}


def draw_frame(rng: np.random.Generator, split: str, theme: str, n_subjects: int, n_predicates: int,
               same_subject_pairs: list[tuple[int, int]]) -> Frame | None:
    """Draw distinct subjects and predicates from the split's lexicon partition.

    Returns None if a predicate pair used on one subject is an antonym pair (a world-knowledge link)."""
    subj_pool = lexicon("names" if theme == "people" else "objects", split)
    pred_pool = lexicon("phrases" if theme == "people" else "properties", split)
    if len(subj_pool) < n_subjects or len(pred_pool) < n_predicates:
        raise ValueError(f"lexicon partition {split} too small for theme {theme}")
    subjects = tuple(subj_pool[i] for i in rng.choice(len(subj_pool), n_subjects, replace=False))
    predicates = tuple(pred_pool[i] for i in rng.choice(len(pred_pool), n_predicates, replace=False))
    for a, b in same_subject_pairs:
        if frozenset((predicates[a], predicates[b])) in ANTONYMS:
            return None
    return Frame(theme, subjects, predicates)


def render_prompt(task: EntailmentTask, note: str | None = None, repeat_prompt: bool = False) -> str:
    statements = "\n".join(f"{i}. {F.sentence(p)}" for i, p in enumerate(task.premises, 1))
    head = "Here are some statements:\n" + statements + "\n\n"
    if repeat_prompt:
        head += "Here are the same statements again:\n" + statements + "\n\n"
    if note:
        head += f"Note: {note}\n\n"
    if task.fmt == "YN":
        q = (f"Question: Does it follow that {F.render(task.probe, False)}?\n"
             "A conclusion follows only if it must be true whenever all of the statements are true.\n\n"
             'Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".')
    elif task.fmt == "MC":
        opts = "\n".join(f"({mc_letter(task, i)}) {F.render(o, False)}" for i, o in enumerate(task.options))
        q = ("Question: Which ONE of the following must be true whenever all of the statements are true?\n"
             + opts + f"\n({mc_letter(task, None)}) None of these\n\n"
             'Think it through as carefully as you need. Finish with a final line of the form "ANSWER: <letter>".')
    else:
        raise ValueError(task.fmt)
    return head + q


def members(fmt: str, with_conditionals: bool) -> list[tuple[str, str, dict[str, Any]]]:
    """The prediction rows of the B4/C4 tables (every family appears)."""
    specs = [
        ("EXACT", "EXACT", {}),
        ("FIRST", "FIRST", {}),
        ("MATCH-L", "MATCH-L", {}),
        ("MATCH-A", "MATCH-A", {}),
        ("ETR-default", "ETR-default", {"rendering": "R1"}),
        ("ETR-1p", "ETR-1p", {"rendering": "R1"}),
    ]
    if with_conditionals:
        specs += [("ETR-default-R2", "ETR-default", {"rendering": "R2"}), ("ETR-1p-R2", "ETR-1p", {"rendering": "R2"})]
    specs += [
        ("MM-S1", "MM-S1", {"variant": "open"}),
        ("MM-elim", "MM-S1", {"variant": "elim"}),
        ("MM-G", "MM-G", {}),
        ("BICOND", "BICOND", {}),
        ("CW-MIN", "CW-MIN", {}),
        ("CW-COMP", "CW-COMP", {}),
        ("ONL(1)", "ONL", {"k": 1}),
        ("ONL(1)-strict", "ONL", {"k": 1, "on_empty": "strict"}),
        ("ONL(2)", "ONL", {"k": 2}),
        ("ONL(4)", "ONL", {"k": 4}),
        ("PRIMACY", "PRIMACY", {}),
        ("RECENCY", "RECENCY", {}),
        ("NONE", "NONE", {}),
        ("UP-1", "UP-k", {"k": 1}),
        ("C1-GREEDY", "GREEDY-MODEL", {}),
        ("NOISY-EXACT", "NOISY-EXACT", {"p": 0.01}),
        ("PERCEPTION-NOISE", "PERCEPTION-NOISE", {"p_d": 0.02, "p_f": 0.01}),
        ("RANDOM", "RANDOM", {}),
    ]
    if fmt == "YN":
        specs += [("AFFIRM", "AFFIRM", {}), ("ALWAYS-YES", "ALWAYS-YES", {}), ("SAMPLE-3", "SAMPLE-m", {"m": 3})]
    return specs


def channel(fmt: str) -> Channel:
    return decision_channel("YES", "NO") if fmt == "YN" else witness_channel("entailment")


def exclusive_or_reading(task: EntailmentTask) -> EntailmentTask:
    """Every "or" read as exclusive: (d1 or d2) and not both."""
    def xor(p):
        if p[0] == "or":
            return ("and", (p, ("nand", p[1])))
        return p
    return EntailmentTask(tuple(xor(p) for p in task.premises), task.probe, task.fmt, task.options, task.reading)


def premise_multiset(task: EntailmentTask) -> list:
    return sorted((F.canonical(p) for p in task.premises), key=repr)
