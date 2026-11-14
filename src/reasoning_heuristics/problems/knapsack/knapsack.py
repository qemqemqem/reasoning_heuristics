"""0/1 knapsack instances, exact solvers and renderers.

Items keep their listing order π_L; names are letters (A, B, ...) or labelled objects.
Generator path: dynamic programming over capacity (`solve_dp`). Validator path:
vectorised enumeration of all subsets (`solve_brute`, n <= 22).

`covering=True` is A/H E5's inverted problem: choose items with total weight at least
L, minimising total value.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Knapsack:
    names: tuple[str, ...]
    values: tuple[int, ...]
    weights: tuple[int, ...]
    capacity: int

    def __post_init__(self) -> None:
        assert len(self.names) == len(self.values) == len(self.weights)
        assert len(set(self.names)) == len(self.names)

    @property
    def n(self) -> int:
        return len(self.names)

    def to_json(self) -> dict:
        return {"kind": "knapsack", "names": list(self.names), "values": list(self.values),
                "weights": list(self.weights), "capacity": self.capacity}

    @classmethod
    def from_json(cls, d: dict) -> "Knapsack":
        assert d["kind"] == "knapsack"
        return cls(tuple(d["names"]), tuple(d["values"]), tuple(d["weights"]), d["capacity"])

    def content_key(self) -> dict:
        return {"kind": "knapsack", "capacity": self.capacity,
                "items": sorted(zip(self.names, self.values, self.weights))}

    def relisted(self, order: list[str]) -> "Knapsack":
        idx = [self.names.index(x) for x in order]
        return Knapsack(tuple(order), tuple(self.values[i] for i in idx), tuple(self.weights[i] for i in idx), self.capacity)

    def with_item(self, name: str, value: int | None = None, weight: int | None = None) -> "Knapsack":
        i = self.names.index(name)
        vals, ws = list(self.values), list(self.weights)
        if value is not None:
            vals[i] = value
        if weight is not None:
            ws[i] = weight
        return Knapsack(self.names, tuple(vals), tuple(ws), self.capacity)

    def value_of(self, chosen: list[str]) -> int:
        return sum(self.values[self.names.index(x)] for x in chosen)

    def weight_of(self, chosen: list[str]) -> int:
        return sum(self.weights[self.names.index(x)] for x in chosen)

    def feasible(self, chosen: list[str], covering: bool = False) -> bool:
        w = self.weight_of(chosen)
        return w >= self.capacity if covering else w <= self.capacity


def solve_dp(k: Knapsack) -> tuple[int, list[str]]:
    """Optimal packing value and one optimal subset (ties: lexicographically earliest in π_L)."""
    W = k.capacity
    best = [[0] * (W + 1) for _ in range(k.n + 1)]
    for i in range(k.n - 1, -1, -1):
        v, w = k.values[i], k.weights[i]
        for c in range(W + 1):
            best[i][c] = best[i + 1][c]
            if w <= c and v + best[i + 1][c - w] > best[i][c]:
                best[i][c] = v + best[i + 1][c - w]
    chosen, c = [], W
    for i in range(k.n):
        w = k.weights[i]
        if w <= c and k.values[i] + best[i + 1][c - w] == best[i][c]:
            chosen.append(k.names[i])
            c -= w
    return best[0][W], chosen


def solve_brute(k: Knapsack, covering: bool = False) -> tuple[int, list[list[str]]]:
    """Optimum and every optimal subset by enumeration (validator path; n <= 22)."""
    if k.n > 22:
        raise ValueError("brute force limited to n <= 22")
    idx = np.arange(2**k.n, dtype=np.int64)
    bits = (idx[:, None] >> np.arange(k.n)) & 1
    vals = bits @ np.array(k.values)
    ws = bits @ np.array(k.weights)
    if covering:
        ok = ws >= k.capacity
        if not ok.any():
            raise ValueError("covering instance infeasible")
        opt = vals[ok].min()
    else:
        ok = ws <= k.capacity
        opt = vals[ok].max()
    rows = np.nonzero(ok & (vals == opt))[0]
    subsets = [[k.names[i] for i in range(k.n) if r >> i & 1] for r in rows]
    return int(opt), subsets


def solve_covering_dp(k: Knapsack) -> tuple[int, list[str]]:
    """Min total value subject to total weight >= capacity (complement of a packing)."""
    total_w = sum(k.weights)
    comp = Knapsack(k.names, k.values, k.weights, total_w - k.capacity)
    v, keep_out = solve_dp(comp)
    chosen = [x for x in k.names if x not in keep_out]
    return sum(k.values) - v, chosen


def render(k: Knapsack, answer_note: str = "", unit: str = "kg") -> str:
    lines = [f"You can carry at most {k.capacity} {unit}. Items (value, weight):"]
    for name, v, w in zip(k.names, k.values, k.weights):
        lines.append(f"{name}: value {v}, weight {w} {unit}")
    lines += ["", "Choose items to maximise the total value without exceeding the weight limit.",
              "After the line ANSWER:, write the letters of the chosen items, comma-separated" + (f", {answer_note}" if answer_note else "") + "."]
    return "\n".join(lines)
