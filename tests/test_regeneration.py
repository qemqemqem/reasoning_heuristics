"""Follow-ups to the review fixes (docs/reviews/2026-11-17-project-review.md), made with the one
regeneration of the item sets: C E5 matches on SEARCH's nodes, the distributional members run the
C doc's 10⁴ samples, and SAT PERCEPTION-NOISE records p_f."""

import json
from collections import defaultdict

from reasoning_heuristics.generators import ah_common, c_e1, c_e2, c_e5
from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.montecarlo import SAMPLES, SMOOTHING_EPS
from reasoning_heuristics.heuristics.tasks import ColouringTask, SatTask, load_task
from reasoning_heuristics.seeds import rng_for


def col_graph():
    return c_e5.col_graph(rng_for(100_001, "C-E5-COL"), 24, 4.2)  # 3-chromatic; degree-order search flips


def sat_cnf():
    return c_e5.labelled_cnf(rng_for(100_000, "C-E5-SAT"), 25, 3.5)


# --- C E5: controls are matched on SEARCH's budget unit, nodes = decisions + flips ---------------------


def test_c_e5_colouring_hardness_counts_search_nodes():
    g = col_graph()
    tf = run("coloring", "SEARCH", ColouringTask(g, 3), {"order": "DEGREE", "tie": "LABEL"}).trace_features
    assert tf["flips"] > 0  # so counting decisions alone would differ
    assert c_e5.order_free_nodes(g) == tf["nodes"] == tf["decisions"] + tf["flips"]


def test_c_e5_sat_hardness_counts_search_nodes():
    cnf = sat_cnf()
    tf = run("sat", "SEARCH", SatTask(cnf), {"order": "MOMS", "value": "POLARITY"}).trace_features
    assert tf["flips"] > 0
    assert c_e5.sat_nodes(cnf) == tf["nodes"] == tf["decisions"] + tf["flips"]


def test_c_e5_records_nodes_and_matches_controls_on_them():
    items, _ = c_e5.generate("smoke", 3, parts=["COL", "SAT"])
    for it in items:
        task = load_task(it.instance)
        if it.cell.startswith("COL/"):
            assert it.params["order_free_hardness_nodes"] == c_e5.order_free_nodes(task.graph)
            assert it.params["listing_dpll_nodes"] == run("coloring", "SEARCH", task, {"order": "LIST"}).trace_features["nodes"]
        else:
            assert it.params["order_free_dpll_nodes"] == c_e5.sat_nodes(task.cnf)
    sets = defaultdict(list)
    for it in items:
        sets[it.set_id].append(it)
    assert len(sets) == 2 and all(c_e5.check_set(members) == [] for members in sets.values())


# --- RO-FF / RO-GREEDY: the members' default, 10⁴ runs with add-ε smoothing (C §1.2) -------------------


def distributional_specs():
    specs = [s for copy in c_e1.COPIES for s in c_e1.col_members(copy) + c_e1.sat_members(copy)]
    specs += [s for d in ("COL", "SAT") for s in c_e2.item_members(d)] + c_e5.sat_members()
    return [s for s in specs if s[1] in ("RO-FF", "RO-GREEDY")]


def test_distributional_members_run_the_documented_sample_count():
    specs = distributional_specs()
    assert {name for _, name, _ in specs} == {"RO-FF", "RO-GREEDY"}
    assert all("samples" not in params for _, _, params in specs)
    assert SAMPLES == 10_000
    for name, params in {(name, json.dumps(params, sort_keys=True)): (name, params) for _, name, params in specs}.values():
        domain, task = ("coloring", ColouringTask(col_graph())) if name == "RO-FF" else ("sat", SatTask(sat_cnf()))
        tf = run(domain, name, task, params).trace_features
        assert (tf["samples"], tf["smoothing_eps"]) == (SAMPLES, SMOOTHING_EPS)


# --- SAT PERCEPTION-NOISE records its sign-flip rate --------------------------------------------------


def test_sat_perception_noise_records_p_f():
    params = next(p for _, name, p in ah_common.sat_members(8) if name == "PERCEPTION-NOISE")
    assert params["p_f"] == 0.01
    tf = run("sat", "PERCEPTION-NOISE", SatTask(sat_cnf()), params).trace_features
    assert tf["p_f"] == params["p_f"]
