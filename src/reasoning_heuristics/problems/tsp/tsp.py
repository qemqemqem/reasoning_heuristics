"""Euclidean TSP on an integer grid with integer (rounded) distances.

Generator path: Held-Karp dynamic programming (`solve_held_karp`, n <= 14).
Validator path: depth-first branch and bound (`solve_bnb`), a separate implementation.
Tours are closed and start at the first-listed city; direction is canonicalised so the
second city precedes the last in listing order.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from functools import cached_property


@dataclass(frozen=True)
class TSP:
    names: tuple[str, ...]
    coords: tuple[tuple[int, int], ...]

    @property
    def n(self) -> int:
        return len(self.names)

    @cached_property
    def dist(self) -> list[list[int]]:
        return [[int(round(math.hypot(a[0] - b[0], a[1] - b[1]))) for b in self.coords] for a in self.coords]

    def d(self, a: str, b: str) -> int:
        return self.dist[self.names.index(a)][self.names.index(b)]

    def tour_length(self, tour: list[str]) -> int:
        return sum(self.d(tour[i], tour[(i + 1) % len(tour)]) for i in range(len(tour)))

    def to_json(self) -> dict:
        return {"kind": "tsp", "names": list(self.names), "coords": [list(c) for c in self.coords]}

    @classmethod
    def from_json(cls, d: dict) -> "TSP":
        assert d["kind"] == "tsp"
        return cls(tuple(d["names"]), tuple(tuple(c) for c in d["coords"]))

    def content_key(self) -> dict:
        return {"kind": "tsp", "cities": sorted(zip(self.names, self.coords))}

    def relisted(self, order: list[str]) -> "TSP":
        idx = [self.names.index(x) for x in order]
        return TSP(tuple(order), tuple(self.coords[i] for i in idx))

    def moved(self, name: str, xy: tuple[int, int]) -> "TSP":
        i = self.names.index(name)
        coords = list(self.coords)
        coords[i] = xy
        return TSP(self.names, tuple(coords))


def canonical_tour(t: TSP, tour: list[str], start: str | None = None) -> list[str]:
    start = start or t.names[0]
    i = tour.index(start)
    tour = tour[i:] + tour[:i]
    if len(tour) > 2 and t.names.index(tour[1]) > t.names.index(tour[-1]):
        tour = [tour[0]] + tour[1:][::-1]
    return tour


def solve_held_karp(t: TSP) -> tuple[int, list[str]]:
    n = t.n
    if n > 14:
        raise ValueError("Held-Karp limited to n <= 14")
    D = t.dist
    best: dict[tuple[int, int], tuple[int, int]] = {}
    for j in range(1, n):
        best[(1 << j, j)] = (D[0][j], 0)
    for size in range(2, n):
        for subset in itertools.combinations(range(1, n), size):
            mask = sum(1 << j for j in subset)
            for j in subset:
                prev = mask & ~(1 << j)
                best[(mask, j)] = min((best[(prev, k)][0] + D[k][j], k) for k in subset if k != j)
    full = sum(1 << j for j in range(1, n))
    length, last = min((best[(full, j)][0] + D[j][0], j) for j in range(1, n))
    tour, mask, j = [], full, last
    while j != 0:
        tour.append(j)
        _, k = best[(mask, j)]
        mask &= ~(1 << j)
        j = k
    order = [0] + tour[::-1]
    return length, canonical_tour(t, [t.names[i] for i in order])


def solve_bnb(t: TSP) -> int:
    """Optimal tour length by depth-first branch and bound (validator path)."""
    n, D = t.n, t.dist
    best = [sum(D[i][(i + 1) % n] for i in range(n))]
    min_out = [min(D[i][j] for j in range(n) if j != i) for i in range(n)]

    def rec(path: list[int], used: int, length: int) -> None:
        if len(path) == n:
            best[0] = min(best[0], length + D[path[-1]][0])
            return
        bound = length + sum(min_out[i] for i in range(n) if not used >> i & 1)
        if bound >= best[0]:
            return
        for j in sorted(range(n), key=lambda j: D[path[-1]][j]):
            if not used >> j & 1:
                rec(path + [j], used | 1 << j, length + D[path[-1]][j])

    rec([0], 1, 0)
    return best[0]
