"""Colouring members against their specs: GREEDY+REPAIR (C §1.3 with D/F §1.3 MIN-CONFLICTS moves)
and RO-FF (C §1.2 distributional members: 10^4 runs, add-ε smoothing, the whole distribution)."""

import subprocess
import sys
import time

import numpy as np
import pytest

from reasoning_heuristics.heuristics import coloring as COL
from reasoning_heuristics.heuristics.answers import colouring_key
from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.montecarlo import random_orders
from reasoning_heuristics.heuristics.tasks import ColouringTask
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.coloring.graph import Graph

K4 = Graph(("v11", "v12", "v13", "v14"),
           (("v11", "v12"), ("v11", "v13"), ("v11", "v14"), ("v12", "v13"), ("v12", "v14"), ("v13", "v14")))


def test_repair_keeps_the_current_colour_when_it_is_among_the_minima():
    # FF-3-LIST-INFEAS on K4: v11..v13 get 1, 2, 3 and v14 gets 1 (one conflict with v11). Every
    # colour has one conflict for v11, so a min-conflicts move keeps it: no oscillation.
    task = ColouringTask(K4, 3)
    infeas = run("coloring", "FF", task, {"order": "LIST", "mode": "INFEAS"}).answer
    answers = [run("coloring", "GREEDY+REPAIR", task, {"order": "LIST", "max_steps": s}) for s in (39, 40, 41)]
    assert all(a.answer == infeas for a in answers)
    assert answers[0].trace_features["repaired_vertices"] == []


def test_repair_moves_are_min_conflicts():
    rng = np.random.default_rng(3)
    for _ in range(40):
        g = G.random_gnp([f"v{i}" for i in range(10, 30)], 0.3, rng)
        task = ColouringTask(g, 3)
        a = run("coloring", "GREEDY+REPAIR", task, {"order": "LIST"})
        b = run("coloring", "GREEDY+REPAIR", task, {"order": "LIST", "max_steps": 10 * g.n + 1})
        assert colouring_key(a.answer) == colouring_key(b.answer)  # no dependence on step parity
        before = run("coloring", "FF", task, {"order": "LIST", "mode": "INFEAS"}).answer
        assert len(G.conflicts(g, a.answer)) <= len(G.conflicts(g, before))


def test_repair_on_a_fewest_colours_task_stops_when_a_fixed_vertex_holds_the_top_colour():
    code = ("from reasoning_heuristics.heuristics.base import run\n"
            "from reasoning_heuristics.heuristics.tasks import ColouringTask\n"
            "from reasoning_heuristics.problems.coloring.graph import Graph\n"
            "g = Graph(('v11', 'v12', 'v13'), (('v11', 'v12'),))\n"
            "p = run('coloring', 'GREEDY+REPAIR', ColouringTask(g, None, (('v12', 2),)), {'order': 'LIST'})\n"
            "print(sorted(p.answer.items()))\n")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "[('v11', 1), ('v12', 2), ('v13', 1)]"


# --- RO-FF -----------------------------------------------------------------------------------------------


def test_ro_ff_distribution_is_complete_and_smoothed():
    rng = np.random.default_rng(1)
    g = G.random_gnp([f"v{i}" for i in rng.choice(np.arange(10, 100), 16, replace=False)], 0.3, rng)
    task = ColouringTask(g)
    t0 = time.time()
    pred = run("coloring", "RO-FF", task, {"seed": 0})
    assert time.time() - t0 < 10
    d, tf = pred.distribution, pred.trace_features
    N, eps, K = tf["samples"], tf["smoothing_eps"], tf["distinct_outcomes"]
    assert N == 10_000 and len(d) == K + 1
    assert sum(d.values()) == pytest.approx(1.0, abs=1e-12)
    assert d["_other"] == pytest.approx(eps / (N + eps * (K + 1)))
    # Listed answers of deterministic members are never truncated away when RO-FF can produce them.
    ff = colouring_key(run("coloring", "FF", task, {"order": "LIST"}).answer)
    assert ff in d


@pytest.mark.parametrize("k,mode", [(None, "ABORT"), (3, "ABORT"), (3, "INFEAS")])
def test_ro_ff_counts_equal_first_fit_on_the_same_orders(k, mode):
    rng = np.random.default_rng(5)
    g = G.random_gnp([f"v{i}" for i in range(10, 24)], 0.3, rng)
    task = ColouringTask(g, k, (("v12", 2),) if k else ())
    free = [v for v in g.vertices if v not in task.fixed_dict()]
    orders = random_orders(np.random.default_rng(0), len(free), 300)
    got = COL.ro_ff_counts(task, g, free, orders, k, mode)
    want = {}
    for row in orders:
        key = colouring_key(COL.first_fit(task, g, [free[i] for i in row], k, mode).answer)
        want[key] = want.get(key, 0) + 1
    assert got == want
