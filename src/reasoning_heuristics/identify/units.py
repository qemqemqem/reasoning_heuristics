"""Item sets and fit units.

A **fit unit** is the set of items one mixture is fitted on: one eval × one domain (the
items' `domain` field, e.g. "SAT", "colouring (k=3)"). Members are domain-specific, so an
eval that mixes domains (A/H E1 has SAT, colouring and entailment) gives one unit per domain;
the response side adds (model, condition), see `records.fit_key`.

Within a unit, items are not independent: the variants of a base, and the items of one
counterfactual set, share their instance. `clusters()` joins items that share a `set_id` or
a `base_hash` (union-find), and the bootstrap resamples these clusters.

A/H E8 items are trace-faithfulness *specs* (the continuation prompt is built from a model's
own response), not answer items; `is_answer_item` excludes them.
"""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import numpy as np


def load_items(paths: str | Path | Iterable[str | Path]) -> list[dict[str, Any]]:
    if isinstance(paths, (str, Path)):
        paths = [paths]
    out: list[dict[str, Any]] = []
    for path in paths:
        p = Path(path)
        opener = gzip.open if p.suffix == ".gz" else open
        with opener(p, "rt", encoding="utf-8") as f:
            out.extend(json.loads(line) for line in f if line.strip())
    return out


def eval_name(item: dict[str, Any]) -> str:
    return f"{item['vertical'].replace('/', '')}_{item['eval_id']}"


def is_answer_item(item: dict[str, Any]) -> bool:
    return not item["generator"].endswith(".ah_e8")


def clusters(items: list[dict[str, Any]]) -> np.ndarray:
    """Cluster id per item: connected components of 'shares a set_id or a base_hash'."""
    parent = list(range(len(items)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    first: dict[tuple[str, str], int] = {}
    for i, it in enumerate(items):
        for key in (("set", it["set_id"]), ("base", it["base_hash"])):
            j = first.setdefault(key, i)
            ri, rj = find(i), find(j)
            if ri != rj:
                parent[ri] = rj
    roots: dict[int, int] = {}
    return np.array([roots.setdefault(find(i), len(roots)) for i in range(len(items))], dtype=np.int64)


@dataclass
class Unit:
    eval: str
    domain: str
    items: list[dict[str, Any]]
    cluster: np.ndarray = field(init=False)
    index: dict[str, int] = field(init=False)

    def __post_init__(self) -> None:
        self.cluster = clusters(self.items)
        self.index = {it["item_id"]: i for i, it in enumerate(self.items)}
        if len(self.index) != len(self.items):
            raise ValueError(f"duplicate item ids in unit {self.name}")

    @property
    def name(self) -> str:
        return f"{self.eval}/{self.domain}"

    @property
    def cells(self) -> list[str]:
        return [it["cell"] for it in self.items]

    @property
    def n_clusters(self) -> int:
        return int(self.cluster.max()) + 1 if len(self.items) else 0

    def labels(self) -> list[str]:
        """Every member label that appears on any item of the unit, in first-seen order."""
        seen: dict[str, None] = {}
        for it in self.items:
            for lbl in it["predictions"]:
                seen.setdefault(lbl, None)
        return list(seen)

    def families(self) -> dict[str, str]:
        out: dict[str, str] = {}
        for it in self.items:
            for lbl, p in it["predictions"].items():
                out.setdefault(lbl, p["family"])
        return out


def make_units(items: Iterable[dict[str, Any]]) -> dict[str, Unit]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for it in items:
        if not is_answer_item(it):
            continue
        groups.setdefault((eval_name(it), it["domain"]), []).append(it)
    return {f"{e}/{d}": Unit(e, d, its) for (e, d), its in groups.items()}
