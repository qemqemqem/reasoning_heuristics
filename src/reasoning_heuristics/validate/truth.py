"""Ground truth, computed twice by unrelated code paths.

`truth(task)` is what generators store: DSATUR backtracking, python-sat's MiniSat, truth tables,
DP and Held-Karp, on the zoo's reading of the stated rule (`effective_graph`, `effective_cnf`,
`effective_premises`). `independent_truth(instance)` is what validators recompute it with: it
lives in `validate.independent`, parses the raw instance JSON itself, applies its own reading of
the stated rule and decides everything with CaDiCaL, sharing no code with this path. The standard
keys are:

- colouring: {"chromatic_number"} (fewest) or {"k", "colourable"};
- SAT: {"satisfiable"};
- entailment: {"answer"} (+ {"follows"} for yes/no);
- knapsack: {"optimum"}; TSP: {"optimal_length"}.

Entailment follows the prompts' definition: a conclusion follows when it "must be true whenever
all the statements are true". Inconsistent premises therefore entail everything (vacuously): YES,
every MC option (the strongest is chosen as usual), every literal. No design intends such items,
and `check_item` flags them.
"""

from __future__ import annotations

from typing import Any

from reasoning_heuristics.heuristics.coloring import effective_graph
from reasoning_heuristics.heuristics.entailment import answer_from_premises, effective_premises, mc_choose
from reasoning_heuristics.heuristics.sat import effective_cnf
from reasoning_heuristics.heuristics.tasks import ColouringTask, EntailmentTask, KnapsackTask, SatTask, TspTask
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.entailment import formula as F
from reasoning_heuristics.problems.knapsack.knapsack import solve_covering_dp, solve_dp
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.tsp.tsp import solve_held_karp
from reasoning_heuristics.validate.independent import independent_truth  # noqa: F401  (the validator path)


def _vacuous_answer(task: EntailmentTask) -> str | list[str]:
    """Inconsistent premises: every conclusion must be true whenever all the premises are."""
    if task.fmt == "YN":
        return "YES"
    if task.fmt == "MC":
        return mc_choose(task, lambda option: True)
    if task.fmt == "OPEN":
        return sorted(F.render_lit(a, pol) for a in F.atoms_of(task.premises) for pol in (True, False)) or "NOTHING"
    raise ValueError(task.fmt)


def truth(task: Any) -> dict[str, Any]:
    if isinstance(task, ColouringTask):
        g = effective_graph(task)
        if task.k is None:
            return {"chromatic_number": G.chromatic_number(g)}
        return {"k": task.k, "colourable": G.k_colour(g, task.k, task.fixed_dict()) is not None}
    if isinstance(task, SatTask):
        return {"satisfiable": S.solve(effective_cnf(task), task.fixed_dict()) is not None}
    if isinstance(task, EntailmentTask):
        prem = effective_premises(task)
        atoms = F.atoms_of(list(prem) + ([task.probe] if task.probe is not None else []) + list(task.options))
        ans = answer_from_premises(task, prem) if F.models(prem, atoms) else _vacuous_answer(task)
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
