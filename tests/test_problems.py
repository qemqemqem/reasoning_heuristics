"""Exact solvers agree with their independent validator-path twins; renderers reproduce the library."""

import itertools
import json
import re
from pathlib import Path

import numpy as np
import pytest

from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.coloring.render import render_neighbours
from reasoning_heuristics.problems.entailment import formula as F
from reasoning_heuristics.problems.knapsack.knapsack import Knapsack, solve_brute, solve_covering_dp, solve_dp
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.sat.render import render_textbook
from reasoning_heuristics.problems.tsp.tsp import TSP, solve_bnb, solve_held_karp

ROOT = Path(__file__).resolve().parents[1]


def _lib(name):
    return [json.loads(l) for l in (ROOT / "data/examples" / f"{name}.jsonl").read_text().splitlines() if l.strip()]


@pytest.mark.parametrize("seed", range(12))
def test_sat_solvers_agree(seed):
    rng = np.random.default_rng(seed)
    n = 10
    cnf = S.random_ksat(n, int(4.3 * n), 3, rng, tuple(f"x{i:02d}" for i in range(1, n + 1)))
    a = S.solve(cnf)
    b = S.dpll_solve(cnf)
    assert (a is None) == (b is None)
    if a is not None:
        assert S.satisfies(cnf, a) and S.satisfies(cnf, b)
    assert S.count_solutions(cnf) == S.brute_force_count(cnf)
    fixed = {"x01": True, "x02": False}
    assert S.count_solutions(cnf, fixed=fixed) == S.brute_force_count(cnf, fixed=fixed)


def test_cnf_iso_invariant_under_renaming_and_polarity():
    rng = np.random.default_rng(3)
    names = tuple(f"x{i:02d}" for i in range(1, 9))
    cnf = S.random_ksat(8, 30, 3, rng, names)
    perm = list(rng.permutation(8) + 1)
    flipped = cnf.with_clauses([[(-1 if abs(l) == 3 else 1) * (perm[abs(l) - 1] if l > 0 else -perm[abs(l) - 1]) for l in c] for c in reversed(cnf.clauses)])
    assert S.iso_invariant(cnf) == S.iso_invariant(flipped)
    assert S.isomorphic(cnf, flipped)


@pytest.mark.parametrize("seed", range(10))
def test_colouring_paths_agree(seed):
    rng = np.random.default_rng(seed)
    g = G.random_gnp([f"v{i}" for i in range(10, 22)], 0.4, rng)
    chi = G.chromatic_number(g)
    assert chi == G.chromatic_number_sat(g)
    col = G.k_colour(g, chi)
    assert G.is_proper(g, col) and G.n_colours(col) == chi


def test_partition_enumeration_matches_brute_force():
    rng = np.random.default_rng(5)
    g = G.random_gnp([f"v{i}" for i in range(10, 18)], 0.35, rng)
    k = G.chromatic_number(g)
    parts = G.enumerate_partitions(g, k, limit=10**6)
    brute = set()
    for cols in itertools.product(range(k), repeat=g.n):
        col = dict(zip(g.vertices, cols))
        if G.is_proper(g, col):
            brute.add(G.partition_of(col))
    got = {G.partition_of(G.masks_to_colouring(g, m)) for m in parts}
    assert got == brute and len(parts) == len(brute)
    assert G.enumerate_partitions(g, k, limit=len(parts) - 1) is None


@pytest.mark.parametrize("seed", range(8))
def test_entailment_paths_agree(seed):
    rng = np.random.default_rng(seed)
    atoms = list("ABCDE")

    def rand_lit():
        return F.lit(str(rng.choice(atoms)), bool(rng.integers(2)))

    for _ in range(20):
        prem = [F.disj(rand_lit(), F.conj(rand_lit(), rand_lit())), F.cond(rand_lit(), rand_lit()),
                F.nand(rand_lit(), rand_lit()), F.iff(rand_lit(), rand_lit())]
        concl = rand_lit()
        if not F.models(prem):
            continue
        assert F.entails(prem, concl) == F.entails_sat(prem, concl)


@pytest.mark.parametrize("seed", range(6))
def test_knapsack_dp_matches_brute(seed):
    rng = np.random.default_rng(seed)
    n = 12
    w = rng.integers(10, 100, size=n)
    v = rng.integers(10, 100, size=n)
    k = Knapsack(tuple("ABCDEFGHIJKL"), tuple(int(x) for x in v), tuple(int(x) for x in w), int(0.45 * w.sum()))
    opt, chosen = solve_dp(k)
    bopt, subsets = solve_brute(k)
    assert opt == bopt and sorted(chosen) in [sorted(s) for s in subsets]
    copt, cchosen = solve_covering_dp(k)
    bcopt, _ = solve_brute(k, covering=True)
    assert copt == bcopt and k.feasible(cchosen, covering=True)


@pytest.mark.parametrize("seed", range(4))
def test_tsp_solvers_agree(seed):
    rng = np.random.default_rng(seed)
    t = TSP(tuple(f"c{i}" for i in range(9)), tuple((int(x), int(y)) for x, y in rng.integers(0, 100, size=(9, 2))))
    length, tour = solve_held_karp(t)
    assert length == solve_bnb(t) == t.tour_length(tour)


def test_render_textbook_reproduces_ah_library_prompt():
    rec = next(r for r in _lib("A_H_baselines") if r["item_id"] == "E1-SAT-x")
    names = re.search(r"Variables: (.*)\.", rec["prompt"]).group(1).split(", ")
    clauses = []
    for body in re.findall(r"C\d+: \((.*)\)", rec["prompt"]):
        clauses.append(tuple((-1 if t.startswith("¬") else 1) * (names.index(t.lstrip("¬")) + 1) for t in body.split(" ∨ ")))
    cnf = S.CNF(tuple(names), tuple(clauses))
    assert render_textbook(cnf) == rec["prompt"]


def test_render_neighbours_reproduces_c_library_prompt():
    rec = next(r for r in _lib("C_constructive") if r["pair_id"] == "E1-COL-A" and r["cell"] == "c1-NAT")
    lines = rec["prompt"].splitlines()
    vertices = lines[1].split(": ", 1)[1].split(", ")
    edges = []
    for line in lines[3:3 + len(vertices)]:
        v, rest = line.split(": ")
        for u in rest.split(", "):
            if vertices.index(u) > vertices.index(v):
                edges.append((v, u))
    g = G.Graph(tuple(vertices), tuple(edges))
    order = vertices
    assert render_neighbours(g, "fewest", order) == rec["prompt"]
