"""Task objects: an instance plus its question context, JSON round-trippable.

`load_task(json)` rebuilds any task from an item's `instance` field, which is how the
validators recompute predictions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from reasoning_heuristics.problems.coloring.graph import Graph
from reasoning_heuristics.problems.entailment import formula as F
from reasoning_heuristics.problems.knapsack.knapsack import Knapsack
from reasoning_heuristics.problems.sat.cnf import CNF
from reasoning_heuristics.problems.tsp.tsp import TSP


@dataclass(frozen=True)
class ColouringTask:
    graph: Graph
    k: int | None = None  # None: "use as few colours as possible"
    fixed: tuple[tuple[str, int], ...] = ()  # pre-coloured vertices (E5-STATE)
    answer_order: tuple[str, ...] | None = None  # None: FREE
    complement: bool = False  # A/H E5 inverted rule: colour the complement graph

    domain = "coloring"

    def fixed_dict(self) -> dict[str, int]:
        return dict(self.fixed)

    def to_json(self) -> dict[str, Any]:
        return {"kind": "coloring_task", "graph": self.graph.to_json(), "k": self.k,
                "fixed": [list(x) for x in self.fixed],
                "answer_order": list(self.answer_order) if self.answer_order is not None else None,
                "complement": self.complement}

    def content_key(self) -> dict[str, Any]:
        return {"graph": self.graph.content_key(), "k": self.k, "fixed": sorted(self.fixed), "complement": self.complement}


@dataclass(frozen=True)
class SatTask:
    cnf: CNF
    fixed: tuple[tuple[str, bool], ...] = ()
    answer_order: tuple[str, ...] | None = None
    declared: tuple[str, ...] | None = None  # declared variables (A/H E2 padding level U)
    inverted: bool = False  # A/H E5: "a rule holds when at least one condition is false"

    domain = "sat"

    def fixed_dict(self) -> dict[str, bool]:
        return dict(self.fixed)

    def to_json(self) -> dict[str, Any]:
        return {"kind": "sat_task", "cnf": self.cnf.to_json(), "fixed": [list(x) for x in self.fixed],
                "answer_order": list(self.answer_order) if self.answer_order is not None else None,
                "declared": list(self.declared) if self.declared is not None else None,
                "inverted": self.inverted}

    def content_key(self) -> dict[str, Any]:
        return {"cnf": self.cnf.content_key(), "fixed": sorted(self.fixed),
                "declared": sorted(self.declared) if self.declared else None, "inverted": self.inverted}


@dataclass(frozen=True)
class EntailmentTask:
    premises: tuple[F.Formula, ...]
    probe: F.Formula | None  # YN: "does it follow that <probe>?"
    fmt: str = "YN"  # "YN" | "MC" | "OPEN"
    options: tuple[F.Formula, ...] = ()  # MC options, in display order (None-of-these is implicit)
    reading: str = "standard"  # "standard" | "nor" (A/H E5 inverted "either...or")

    domain = "entailment"

    def to_json(self) -> dict[str, Any]:
        return {"kind": "entailment_task", "premises": [F.to_json(p) for p in self.premises],
                "probe": F.to_json(self.probe) if self.probe is not None else None,
                "fmt": self.fmt, "options": [F.to_json(o) for o in self.options], "reading": self.reading}

    def content_key(self) -> dict[str, Any]:
        return {"premises": sorted((F.canonical(p) for p in self.premises), key=repr),
                "probe": F.canonical(self.probe) if self.probe is not None else None,
                "fmt": self.fmt, "options": sorted((F.canonical(o) for o in self.options), key=repr),
                "reading": self.reading}


@dataclass(frozen=True)
class KnapsackTask:
    knapsack: Knapsack
    covering: bool = False  # A/H E5 inverted: weight >= capacity, minimise value
    answer_order: tuple[str, ...] | None = None

    domain = "knapsack"

    def to_json(self) -> dict[str, Any]:
        return {"kind": "knapsack_task", "knapsack": self.knapsack.to_json(), "covering": self.covering,
                "answer_order": list(self.answer_order) if self.answer_order is not None else None}

    def content_key(self) -> dict[str, Any]:
        return {"knapsack": self.knapsack.content_key(), "covering": self.covering}


@dataclass(frozen=True)
class TspTask:
    tsp: TSP
    start: str | None = None  # None: first-listed city

    domain = "tsp"

    def to_json(self) -> dict[str, Any]:
        return {"kind": "tsp_task", "tsp": self.tsp.to_json(), "start": self.start}

    def content_key(self) -> dict[str, Any]:
        return {"tsp": self.tsp.content_key(), "start": self.start}


def load_task(data: dict[str, Any]):
    kind = data["kind"]
    if kind == "coloring_task":
        return ColouringTask(Graph.from_json(data["graph"]), data["k"], tuple((v, c) for v, c in data["fixed"]),
                             tuple(data["answer_order"]) if data["answer_order"] is not None else None,
                             data.get("complement", False))
    if kind == "sat_task":
        return SatTask(CNF.from_json(data["cnf"]), tuple((v, b) for v, b in data["fixed"]),
                       tuple(data["answer_order"]) if data["answer_order"] is not None else None,
                       tuple(data["declared"]) if data.get("declared") is not None else None,
                       data.get("inverted", False))
    if kind == "entailment_task":
        return EntailmentTask(tuple(F.from_json(p) for p in data["premises"]),
                              F.from_json(data["probe"]) if data["probe"] is not None else None,
                              data["fmt"], tuple(F.from_json(o) for o in data["options"]), data.get("reading", "standard"))
    if kind == "knapsack_task":
        return KnapsackTask(Knapsack.from_json(data["knapsack"]), data["covering"],
                            tuple(data["answer_order"]) if data.get("answer_order") is not None else None)
    if kind == "tsp_task":
        return TspTask(TSP.from_json(data["tsp"]), data.get("start"))
    raise ValueError(f"unknown task kind {kind}")
