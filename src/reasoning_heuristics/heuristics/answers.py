"""Canonical answer keys, so answers from different members can be compared exactly.

- colouring: the partition into colour classes (colour names do not matter), or IMPOSSIBLE;
- SAT: the assignment over all variables, or UNSAT;
- entailment: YES / NO / X (contradictory state), or an option letter;
- knapsack: the chosen set; TSP: the canonical tour.

`answer_key(domain, answer)` returns a short string; members whose answers have the
same key are tied on that item.
"""

from __future__ import annotations

from typing import Any

from reasoning_heuristics.problems.coloring.graph import label_key, partition_of


def colouring_key(col: Any) -> str:
    if isinstance(col, str):
        return col
    classes = [sorted(c, key=label_key) for c in partition_of({k: v for k, v in col.items() if not k.startswith("_")})]
    classes.sort(key=lambda c: label_key(c[0]))
    return "|".join(",".join(c) for c in classes)


def assignment_key(a: Any) -> str:
    if isinstance(a, str):
        return a
    return ",".join(f"{k}={'T' if v else 'F'}" for k, v in sorted(a.items(), key=lambda kv: label_key(kv[0])) if not k.startswith("_"))


def answer_key(domain: str, answer: Any) -> str | None:
    if answer is None:
        return None
    if domain == "coloring":
        return colouring_key(answer)
    if domain == "sat":
        return assignment_key(answer)
    if domain in ("entailment", "decision"):
        return str(answer)
    if domain == "knapsack":
        return answer if isinstance(answer, str) else ",".join(sorted(answer))
    if domain == "tsp":
        return answer if isinstance(answer, str) else "-".join(answer)
    raise ValueError(domain)
