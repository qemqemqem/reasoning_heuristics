"""Shared pieces of the A/H (baselines) generators: member lists per domain, the machine-facts
entailment template, and small instance helpers.

A/H scores on the decision channel (SAT / UNSAT, possible / impossible, follows / does not
follow). Every A2 threshold here is an illustrative default, recorded with the member's
params; the study fits thresholds out of sample (A/H §1.5).
"""

from __future__ import annotations

from typing import Any

from reasoning_heuristics.generators.common import decision_channel
from reasoning_heuristics.heuristics.tasks import EntailmentTask
from reasoning_heuristics.problems.entailment import formula as F

SAT_FORMAT = "sat_json"
COL_FORMAT = "col_json"
ENT_YN_FORMAT = "ent_yn_json"
ENT_OPEN_FORMAT = "ent_open_json"

SAT_CHANNEL = decision_channel("SAT", "UNSAT")
COL_CHANNEL = decision_channel("POSSIBLE", "IMPOSSIBLE")
ENT_CHANNEL = decision_channel("YES", "NO")


def sat_members(length_theta: int, budget: int = 8, walk_runs: int = 30) -> list[tuple[str, str, dict[str, Any]]]:
    return [
        ("exact", "EXACT", {}),
        ("A1 ALWAYS-SAT", "ALWAYS-SAT", {}),
        ("A1 ALWAYS-UNSAT", "ALWAYS-UNSAT", {}),
        ("A2 DENSITY-U", "DENSITY", {"variant": "U", "theta": 4.26}),
        ("A2 DENSITY-D", "DENSITY", {"variant": "D", "theta": 4.26}),
        ("A2 LENGTH-M", "LENGTH", {"variant": "M", "theta": length_theta}),
        ("H RANDOM-U", "RANDOM", {}),
        ("H SAMPLE-8", "SAMPLE-m", {"m": 8}),
        ("NOISY-EXACT-STEP", "NOISY-EXACT", {"variant": "STEP", "p": 0.02}),
        ("NOISY-EXACT-READ", "NOISY-EXACT", {"variant": "READ", "p": 0.01}),
        ("PERCEPTION-NOISE", "PERCEPTION-NOISE", {"p_d": 0.02, "runs": 200, "seed": 0}),
        ("C0 POLARITY", "POLARITY", {}),
        ("C1 GREEDY", "GREEDY", {"order": "MENTION", "mode": "ABORT"}),
        ("C2 UC", "UC", {}),
        ("B1 UP-3", "UP-k", {"k": 3}),
        ("D DPLL-b", "SEARCH", {"b": budget, "order": "MENTION", "value": "TRUE", "default": "UNSAT"}),
        ("D∘DENSITY", "SEARCH", {"b": budget, "order": "MENTION", "value": "TRUE", "default": "DENSITY", "theta": 4.26}),
        ("F WALK-200", "WALK", {"flips": 200, "runs": walk_runs, "seed": 0}),
    ]


def col_members(k: int, length_theta: int, budget: int = 20) -> list[tuple[str, str, dict[str, Any]]]:
    return [
        ("exact", "EXACT", {}),
        ("A1 ALWAYS-POSSIBLE", "ALWAYS-POSSIBLE", {}),
        ("A1 ALWAYS-IMPOSSIBLE", "ALWAYS-IMPOSSIBLE", {}),
        ("A2 DENSITY-U", "DENSITY", {"variant": "U", "theta": 4.69}),
        ("A2 DENSITY-D", "DENSITY", {"variant": "D", "theta": 4.69}),
        ("A2 LENGTH-M", "LENGTH", {"theta": length_theta}),
        ("H RANDOM-U", "RANDOM-DEC", {}),
        ("H SAMPLE-8", "SAMPLE-m", {"m": 8}),
        ("NOISY-EXACT", "NOISY-EXACT-DEC", {"p": 0.01}),
        ("PERCEPTION-NOISE", "PERCEPTION-NOISE", {"p_d": 0.02, "p_a": 0.05, "runs": 100, "seed": 0}),
        ("C1 FIRST-FIT", "FF", {"order": "LIST", "k": k, "mode": "ABORT"}),
        ("C2 DSATUR", "DSATUR", {"k": k, "mode": "ABORT"}),
        ("B1 DROP-CONSTRAINT(last 3)", "DROP-LAST", {"q": 3, "k": k}),
        ("B4 ADD-CONSTRAINT(adjacent)", "PHANTOM", {"pairs": "adjacent-listed", "k": k}),
        ("D DPLL-b", "SEARCH", {"b": budget, "order": "LIST", "default": "IMPOSSIBLE"}),
    ]


def ent_members(with_etr: bool = True) -> list[tuple[str, str, dict[str, Any]]]:
    specs = [
        ("exact", "EXACT", {}),
        ("A1 ALWAYS-YES", "ALWAYS-YES", {}),
        ("A1 NONE", "NONE", {}),
        ("A2 FREQ", "FREQ", {"theta": 2}),
        ("A2 ATMOSPHERE", "ATMOSPHERE", {}),
        ("A2 PRIMACY", "PRIMACY", {}),
        ("A2 RECENCY", "RECENCY", {}),
        ("A2 DENSITY", "DENSITY", {"theta": 1.0}),
        ("H RANDOM-U", "RANDOM", {}),
        ("H SAMPLE-8", "SAMPLE-m", {"m": 8}),
        ("NOISY-EXACT", "NOISY-EXACT", {"p": 0.01}),
        ("PERCEPTION-NOISE", "PERCEPTION-NOISE", {"p_d": 0.02, "p_f": 0.01}),
        ("B1 UP-1", "UP-k", {"k": 1}),
        ("B1 UP-2", "UP-k", {"k": 2}),
        ("B1 UP-3", "UP-k", {"k": 3}),
        ("B4 FIRST", "FIRST", {}),
        ("B4 MATCH", "MATCH-A", {}),
        ("D case-split (b = 4)", "CASE-SPLIT", {"b": 4}),
    ]
    if with_etr:
        specs.append(("B4 ETR", "ETR-default", {"rendering": "R1"}))
    return specs


def render_machine_facts(task: EntailmentTask, preamble: str | None = None, reminder: str | None = None) -> str:
    """A/H machine-facts template (library E1-ENT/E2-ENT). YN asks about the probe; OPEN asks what follows."""
    lines = ["Here are some facts about a machine.", ""]
    lines += [f"- {F.sentence(p)}" for p in task.premises]
    lines.append("")
    if preamble:
        lines.append(preamble)
    if reminder:
        lines.append(reminder)
    if preamble or reminder:
        lines.append("")
    if task.fmt == "YN":
        lines += [f"Question: Does it follow from these facts that {F.render(task.probe, False)}?",
                  'Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}']
    elif task.fmt == "OPEN":
        lines += ["Question: Which facts about single parts of the machine (a part being in a given state, or not being in it) must be true whenever all of these facts are true?",
                  'Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in one of these forms:',
                  '{"conclusion": ["<fact>", ...]} listing every such fact, or {"conclusion": "NOTHING"} if there are none']
    else:
        raise ValueError(task.fmt)
    return "\n".join(lines)


def up_depth(task: EntailmentTask, max_k: int = 8) -> int | None:
    """C's propagation depth: the smallest k for which UP-k derives the probe (None if no k <= max_k does)."""
    from reasoning_heuristics.heuristics.base import run

    for k in range(0, max_k + 1):
        if run("entailment", "UP-k", task, {"k": k}).answer == "YES":
            return k
    return None


def word_count(text: str) -> int:
    return len(text.split())


def discriminates(item) -> bool:
    """The validator's rule: at least two listed members give different (non-set-valued) answers."""
    from reasoning_heuristics.heuristics.answers import answer_key
    from reasoning_heuristics.heuristics.tasks import load_task

    domain = load_task(item.instance).domain
    keys = {answer_key(domain, r["answer"]) for r in item.predictions.values()
            if r["answer"] is not None and not r.get("trace_features", {}).get("set_valued")}
    return len(keys) >= 2
