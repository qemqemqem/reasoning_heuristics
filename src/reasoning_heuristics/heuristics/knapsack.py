"""Knapsack members (C §1.3): fixed-order and score-order greedy, the pBT width-2 hybrid,
A3 textbook transfer for the covering inversion, and the exact DP.

All sorts are descending with ties to the earlier item in π_L. -SKIP members take every
item that still fits; RATIO-PREFIX stops at the first item that does not fit.
"""

from __future__ import annotations

from typing import Any

from reasoning_heuristics.heuristics.base import Prediction, member
from reasoning_heuristics.heuristics.tasks import KnapsackTask
from reasoning_heuristics.problems.knapsack.knapsack import Knapsack, solve_brute, solve_covering_dp, solve_dp

D = "knapsack"

SCORES = {
    "INPUT": None,
    "RATIO": lambda v, w: v / w,
    "VALUE": lambda v, w: v,
    "WEIGHT": lambda v, w: w,
    "DIFF": lambda v, w: v - w,
}


def sorted_items(k: Knapsack, score: str) -> list[int]:
    idx = list(range(k.n))
    if SCORES[score] is None:
        return idx
    f = SCORES[score]
    return sorted(idx, key=lambda i: (-f(k.values[i], k.weights[i]), i))


def greedy_take(k: Knapsack, order: list[int], stop_at_misfit: bool) -> tuple[list[str], dict[str, Any]]:
    chosen, load, skipped = [], 0, []
    for i in order:
        if load + k.weights[i] <= k.capacity:
            chosen.append(k.names[i])
            load += k.weights[i]
        else:
            skipped.append(k.names[i])
            if stop_at_misfit:
                break
    return chosen, {"consider_order": [k.names[i] for i in order], "skipped": skipped, "unused_capacity": k.capacity - load}


def _greedy(task: KnapsackTask, score: str, prefix: bool) -> Prediction:
    if task.covering:
        raise ValueError("greedy packing members are undefined on the covering inversion")
    chosen, trace = greedy_take(task.knapsack, sorted_items(task.knapsack, score), prefix)
    return Prediction(sorted(chosen), trace)


@member("INPUT-FIT", "C1", D, "takes items in listed order whenever they fit")
def input_fit(task, params):
    return _greedy(task, "INPUT", False)


@member("RATIO-SKIP", "C1", D, "sorts by value per unit weight; takes each item that fits; cites value per kg")
def ratio_skip(task, params):
    return _greedy(task, "RATIO", False)


@member("RATIO-PREFIX", "C1", D, "sorts by value per unit weight; stops at the first item that does not fit")
def ratio_prefix(task, params):
    return _greedy(task, "RATIO", True)


@member("VALUE", "C1", D, "takes the most valuable items first while they fit")
def value_first(task, params):
    return _greedy(task, "VALUE", False)


@member("LARGEST-FIT", "C1", D, "takes the heaviest items first while they fit")
def largest_fit(task, params):
    return _greedy(task, "WEIGHT", False)


@member("DIFF", "C1", D, "sorts by value minus weight (a no-division proxy); takes each item that fits")
def diff(task, params):
    return _greedy(task, "DIFF", False)


@member("RATIO+BEST-SINGLE", "pBT-2", D, "compares the ratio-greedy prefix with the best single item")
def ratio_best_single(task, params):
    k = task.knapsack
    prefix, trace = greedy_take(k, sorted_items(k, "RATIO"), True)
    single = max((i for i in range(k.n) if k.weights[i] <= k.capacity), key=lambda i: (k.values[i], -i))
    if k.values[single] > k.value_of(prefix):
        return Prediction([k.names[single]], {**trace, "chose": "single"})
    return Prediction(sorted(prefix), {**trace, "chose": "prefix"})


@member("EXACT", "null", D, "dynamic programming or exhaustive comparison of subsets")
def exact(task: KnapsackTask, params):
    k = task.knapsack
    if task.covering:
        opt, chosen = solve_covering_dp(k)
    else:
        opt, chosen = solve_dp(k)
    _, all_opt = solve_brute(k, covering=task.covering) if k.n <= 22 else (opt, [chosen])
    return Prediction(sorted(chosen), {"optimum": opt, "n_optimal": len(all_opt), "set_valued": len(all_opt) > 1})


@member("TT", "A3", D, "restates the covering task as ordinary packing; maximises value under the limit")
def textbook_transfer(task: KnapsackTask, params):
    opt, chosen = solve_dp(task.knapsack)
    return Prediction(sorted(chosen), {"inner": "EXACT", "packing_optimum": opt})
