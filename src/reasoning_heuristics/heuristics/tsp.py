"""TSP members (C §1.3): nearest neighbour from several starts, input order, greedy edge,
farthest insertion, and the exact solver. Tours are returned canonicalised from the
start city (the first-listed city unless the task names one); ties go to π_L.
"""

from __future__ import annotations

from typing import Any

from reasoning_heuristics.heuristics.base import Prediction, member
from reasoning_heuristics.heuristics.tasks import TspTask
from reasoning_heuristics.problems.coloring.graph import label_key
from reasoning_heuristics.problems.tsp.tsp import TSP, canonical_tour, solve_held_karp

D = "tsp"


def nn_tour(t: TSP, start: int) -> list[int]:
    tour, left = [start], set(range(t.n)) - {start}
    while left:
        here = tour[-1]
        nxt = min(left, key=lambda j: (t.dist[here][j], j))
        tour.append(nxt)
        left.remove(nxt)
    return tour


def _pred(task: TspTask, tour_idx: list[int], trace: dict[str, Any]) -> Prediction:
    t = task.tsp
    names = [t.names[i] for i in tour_idx]
    tour = canonical_tour(t, names, task.start)
    return Prediction(tour, {**trace, "length": t.tour_length(tour), "visit_order": names})


@member("NN-FIRST", "C1", D, "starts at the first-listed city and always goes to the nearest unvisited city")
def nn_first(task: TspTask, params):
    return _pred(task, nn_tour(task.tsp, 0), {"start": task.tsp.names[0]})


@member("NN-LABEL0", "C1", D, "nearest neighbour from the city with the smallest label")
def nn_label0(task: TspTask, params):
    t = task.tsp
    s = min(range(t.n), key=lambda i: label_key(t.names[i]))
    return _pred(task, nn_tour(t, s), {"start": t.names[s]})


@member("NN-BEST", "C1", D, "nearest-neighbour tours from every start; keeps the shortest")
def nn_best(task: TspTask, params):
    t = task.tsp
    tours = [nn_tour(t, s) for s in range(t.n)]
    lengths = [t.tour_length([t.names[i] for i in tr]) for tr in tours]
    s = min(range(t.n), key=lambda i: (lengths[i], i))
    return _pred(task, tours[s], {"start": t.names[s]})


@member("INPUT-ORDER", "C1", D, "visits the cities in the listed order")
def input_order(task: TspTask, params):
    return _pred(task, list(range(task.tsp.n)), {})


@member("GREEDY-EDGE", "C2", D, "adds the shortest remaining edge unless it makes a degree-3 vertex or a short cycle")
def greedy_edge(task: TspTask, params):
    t = task.tsp
    n = t.n
    edges = sorted(((t.dist[i][j], i, j) for i in range(n) for j in range(i + 1, n)))
    deg = [0] * n
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    adj: list[list[int]] = [[] for _ in range(n)]
    added = 0
    for _, i, j in edges:
        if deg[i] == 2 or deg[j] == 2:
            continue
        if find(i) == find(j) and added < n - 1:
            continue
        parent[find(i)] = find(j)
        adj[i].append(j)
        adj[j].append(i)
        deg[i] += 1
        deg[j] += 1
        added += 1
        if added == n:
            break
    tour, prev = [0], None
    while len(tour) < n:
        here = tour[-1]
        nxt = next(x for x in adj[here] if x != prev and x not in tour)
        prev = here
        tour.append(nxt)
    return _pred(task, tour, {})


@member("FARTHEST-INSERTION", "C2", D, "starts from the first city and its farthest city; inserts the farthest remaining city at its cheapest point")
def farthest_insertion(task: TspTask, params):
    t = task.tsp
    D_ = t.dist
    far = max(range(1, t.n), key=lambda j: (D_[0][j], -j))
    tour = [0, far]
    left = set(range(t.n)) - set(tour)
    while left:
        c = max(left, key=lambda x: (min(D_[x][y] for y in tour), -x))
        best = min(range(len(tour)), key=lambda i: (D_[tour[i]][c] + D_[c][tour[(i + 1) % len(tour)]] - D_[tour[i]][tour[(i + 1) % len(tour)]], i))
        tour.insert(best + 1, c)
        left.remove(c)
    return _pred(task, tour, {})


@member("EXACT", "null", D, "an exhaustive or dynamic-programming search over tours")
def exact(task: TspTask, params):
    length, tour = solve_held_karp(task.tsp)
    return Prediction(canonical_tour(task.tsp, tour, task.start), {"length": length})
