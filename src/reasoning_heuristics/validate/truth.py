"""Ground truth, computed twice by unrelated code paths.

`truth(task)` is what generators store: DSATUR backtracking, python-sat's MiniSat, truth tables,
DP and Held-Karp, on the zoo's reading of the stated rule (`effective_graph`, `effective_cnf`,
`effective_premises`). `independent_truth(instance)` is what validators recompute it with: it
lives in `validate.independent`, parses the raw instance JSON itself, applies its own reading of
the stated rule and decides everything with CaDiCaL, sharing no code with this path. The standard
keys are:

- colouring: {"chromatic_number"} (fewest) or {"k", "colourable"}; plus {"answer"}, the
  target's colour, for an instructed first-fit question (C E3 I arm, `task.target`);
- SAT: {"satisfiable"};
- entailment: {"answer"} (+ {"follows"} for yes/no);
- knapsack: {"optimum"}; TSP: {"optimal_length"}.

Entailment follows the prompts' definition: a conclusion follows when it "must be true whenever
all the statements are true". Inconsistent premises therefore entail everything (vacuously): YES,
every MC option (the strongest is chosen as usual), every literal. That is the zoo's
`exact_answer` (`vacuous_answer` when the premises are inconsistent), which the exact members use
too. No design intends such items, and `check_item` flags them.
"""

from __future__ import annotations

from typing import Any

from reasoning_heuristics.heuristics.coloring import effective_graph, first_fit
from reasoning_heuristics.heuristics.entailment import effective_premises, exact_answer
from reasoning_heuristics.heuristics.sat import effective_cnf
from reasoning_heuristics.heuristics.tasks import ColouringTask, EntailmentTask, KnapsackTask, SatTask, TspTask
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.knapsack.knapsack import solve_covering_dp, solve_dp
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.tsp.tsp import solve_held_karp
from reasoning_heuristics.validate.independent import independent_truth  # noqa: F401  (the validator path)


def truth(task: Any) -> dict[str, Any]:
    if isinstance(task, ColouringTask):
        g = effective_graph(task)
        if task.target is not None:
            ff = first_fit(task, g, list(g.vertices), None, "ABORT").answer
            return {"chromatic_number": G.chromatic_number(g), "answer": ff[task.target]}
        if task.k is None:
            return {"chromatic_number": G.chromatic_number(g)}
        return {"k": task.k, "colourable": G.k_colour(g, task.k, task.fixed_dict()) is not None}
    if isinstance(task, SatTask):
        return {"satisfiable": S.solve(effective_cnf(task), task.fixed_dict()) is not None}
    if isinstance(task, EntailmentTask):
        ans = exact_answer(task, effective_premises(task))
        out = {"answer": ans}
        if task.fmt == "YN":
            out["follows"] = ans == "YES"
        return out
    if isinstance(task, KnapsackTask):
        opt = solve_covering_dp(task.knapsack)[0] if task.covering else solve_dp(task.knapsack)[0]
        return {"optimum": opt}
    if isinstance(task, TspTask):
        return {"optimal_length": solve_held_karp(task.tsp)[0]}
    raise TypeError(type(task))
