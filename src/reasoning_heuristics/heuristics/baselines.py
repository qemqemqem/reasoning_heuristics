"""Baseline members the A/H vertical needs that the per-domain modules do not define:
colouring A1/A2 cues, H SAMPLE-m, decision-level nuisance models, and entailment A2
DENSITY plus a budgeted case-split search (D).

Definitions follow A/H §1.5. Cue members answer on the decision channel only, so their
answers are plain decisions (no witness set). Cue members read the *stated* instance (the surface), so an
inverted rule (A/H E5) does not move them. Every A2 member is the deterministic limit of a
soft threshold: it answers the negative class (IMPOSSIBLE / does not follow) at phi >= theta
for colouring (as for SAT), and "follows" iff phi > theta for entailment (the doc's
"low prior" direction). Thresholds here are illustrative defaults; the study fits them
out of sample (E3 sweep / ENT calibration split).
"""

from __future__ import annotations

import itertools
from typing import Any

import numpy as np

from reasoning_heuristics.heuristics.base import Prediction, member
from reasoning_heuristics.heuristics.coloring import effective_graph
from reasoning_heuristics.heuristics.entailment import effective_premises
from reasoning_heuristics.heuristics.tasks import ColouringTask, EntailmentTask
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.coloring.graph import Graph
from reasoning_heuristics.problems.entailment import formula as F

# --- colouring ----------------------------------------------------------------------------


def _decision(task: ColouringTask) -> str:
    """k-colourability via the SAT encoding (robust on disconnected or misread graphs)."""
    g = effective_graph(task)
    if task.k is None or task.fixed:
        raise ValueError("decision members need a k task without fixed vertices")
    return "POSSIBLE" if G.k_colourable_sat(g, task.k) else "IMPOSSIBLE"


@member("ALWAYS-POSSIBLE", "A1", "coloring", "'possible' asserted with a quick, unchecked assignment")
def always_possible(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    return Prediction("POSSIBLE", {"witness": "uniform fill"})


@member("ALWAYS-IMPOSSIBLE", "A1", "coloring", "GIVEUP early ('too many constraints'); no assignment attempted")
def always_impossible(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    return Prediction("IMPOSSIBLE", {})


def colouring_cues(task: ColouringTask) -> dict[str, float]:
    g = task.graph
    used = sum(1 for v in g.vertices if g.degree(v) > 0)
    return {"m": g.m, "n_used": used, "n_decl": g.n, "degree_U": 2 * g.m / used, "degree_D": 2 * g.m / g.n}


@member("DENSITY", "A2", "coloring", "cites how many conflicts there are per person as the reason; no closed refutation")
def density_col(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    """IMPOSSIBLE iff mean degree >= theta. Variant U (non-isolated vertices) or D (declared)."""
    cues = colouring_cues(task)
    phi = cues["degree_U"] if params.get("variant", "U") == "U" else cues["degree_D"]
    impossible = phi >= params.get("theta", 4.69)
    return Prediction("IMPOSSIBLE" if impossible else "POSSIBLE", {"phi": round(phi, 3)})


@member("LENGTH", "A2", "coloring", "cites the number of conflict pairs ('with this many pairs it cannot work')")
def length_col(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    impossible = task.graph.m >= params["theta"]
    return Prediction("IMPOSSIBLE" if impossible else "POSSIBLE", {"m": task.graph.m})


def labelled_colourings(g: Graph, k: int, limit: int) -> int:
    """Number of proper colourings with colours 1..k: the product over connected components;
    trees use k(k-1)^(n-1), other components are counted from their partitions into <= k classes."""
    total = 1
    for comp in _components(g):
        sub = Graph(tuple(v for v in g.vertices if v in comp), tuple(e for e in g.edges if e[0] in comp))
        if sub.m == sub.n - 1:  # a tree (connected by construction)
            total *= k * (k - 1) ** (sub.n - 1)
            continue
        parts = G.enumerate_partitions(sub, k, limit)
        if parts is None:
            raise ValueError(f"more than {limit} partitions in a component; SAMPLE-m likelihood not computed")
        count = 0
        for p in parts:
            ways = 1
            for i in range(len(p)):
                ways *= k - i
            count += ways
        total *= count
    return total


def _components(g: Graph) -> list[set[str]]:
    import networkx as nx

    return [set(c) for c in nx.connected_components(g.nx())]


@member("SAMPLE-m", "H", "coloring", "a few complete example assignments checked; 'impossible' when none of them works", deterministic=False)
def sample_m_col(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    g = effective_graph(task)
    m = params.get("m", 8)
    s = labelled_colourings(g, task.k, params.get("limit", 2_000_000))
    p = 1 - (1 - s / task.k ** g.n) ** m
    return Prediction(None, {"n_colourings": s, "m": m}, {"POSSIBLE": p, "IMPOSSIBLE": 1 - p})


@member("RANDOM-DEC", "H", "coloring", "no procedure determines the verdict; trace content and verdict unrelated", deterministic=False)
def random_decision(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    """RANDOM-U on the decision channel: possible / impossible with probability 1/2 each."""
    return Prediction(None, {}, {"POSSIBLE": 0.5, "IMPOSSIBLE": 0.5})


@member("NOISY-EXACT-DEC", "nuisance", "coloring", "systematic search with sporadic slips; errors symmetric", deterministic=False)
def noisy_exact_decision(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    """Decision flips w.p. eps = (1 - (1-p)^L)/2, L = number of conflict pairs read."""
    p = params.get("p", 0.01)
    L = task.graph.m
    eps = 0.5 * (1 - (1 - p) ** L)
    g = _decision(task)
    other = "IMPOSSIBLE" if g == "POSSIBLE" else "POSSIBLE"
    return Prediction(None, {"L": L, "eps": round(eps, 4)}, {g: 1 - eps, other: eps})


@member("PERCEPTION-NOISE", "nuisance", "coloring", "a misquoted pair (dropped or invented) that predicts where the answer goes wrong", deterministic=False)
def perception_noise_col(task: ColouringTask, params: dict[str, Any]) -> Prediction:
    """Exact on a misread instance: each pair dropped w.p. p_d, one random non-pair added w.p. p_a
    (Monte Carlo with a fixed seed)."""
    g = effective_graph(task)
    p_d, p_a, runs = params.get("p_d", 0.02), params.get("p_a", 0.05), params.get("runs", 100)
    rng = np.random.default_rng(params.get("seed", 0))
    non_edges = [e for e in itertools.combinations(g.vertices, 2) if not g.has_edge(*e)]
    possible = 0
    for _ in range(runs):
        edges = [e for e in g.edges if rng.random() >= p_d]
        if non_edges and rng.random() < p_a:
            edges.append(non_edges[rng.integers(len(non_edges))])
        if G.k_colourable_sat(Graph(g.vertices, tuple(edges)), task.k):
            possible += 1
    return Prediction(None, {"p_d": p_d, "p_a": p_a, "runs": runs},
                      {"POSSIBLE": possible / runs, "IMPOSSIBLE": 1 - possible / runs})


# --- entailment ---------------------------------------------------------------------------------


@member("DENSITY", "A2", "entailment", "cites how many facts there are relative to the things they mention")
def density_ent(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    phi = len(task.premises) / len(F.atoms_of(task.premises))
    return Prediction("YES" if phi > params.get("theta", 1.0) else "NO", {"phi": round(phi, 3)})


@member("CASE-SPLIT", "D", "entailment", "an explicit case split over the atoms in mention order; stops at the first counter-example or at the budget")
def case_split(task: EntailmentTask, params: dict[str, Any]) -> Prediction:
    """Enumerate the premises' models in truth-table order over atoms in first-mention order
    (true before false). A counter-model among the first b models -> NO; otherwise the default
    (YES: 'follows' after checking b cases without a counter-example)."""
    prem = effective_premises(task)
    atoms = F.atoms_of(list(prem) + [task.probe])
    b = params.get("b", 4)
    checked = 0
    for w in F.worlds(atoms):
        if not all(F.evaluate(p, w) for p in prem):
            continue
        checked += 1
        if not F.evaluate(task.probe, w):
            return Prediction("NO", {"first_countermodel": checked, "exhausted": False})
        if checked >= b:
            return Prediction(params.get("default", "YES"), {"cases_checked": checked, "exhausted": True})
    return Prediction("YES", {"cases_checked": checked, "exhausted": False})
