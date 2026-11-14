"""C-vertical generators: reproduce the C library, and validate generated sets."""

import re

import numpy as np
import pytest

from libparse import cnf_from_c_prompt, find, graph_from_edge_list, graph_from_neighbours, library
from reasoning_heuristics.counterfactual import edits as E
from reasoning_heuristics.generators import c_e1, c_e2, c_e3, c_e5
from reasoning_heuristics.generators.common import predict_all
from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.tasks import ColouringTask, EntailmentTask, KnapsackTask, SatTask
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.coloring.render import render_neighbours
from reasoning_heuristics.problems.entailment import formula as F
from reasoning_heuristics.problems.knapsack.knapsack import Knapsack
from reasoning_heuristics.problems.sat.render import render_c
from reasoning_heuristics.validate.checks import check_leakage, run_checks

C_LIB = library("C_constructive")


def answer_order(prompt: str):
    m = re.search(r"in this order: (.*)\.$", prompt, flags=re.M)
    return m.group(1).split(", ") if m else None


# --- library reproduction ---------------------------------------------------------------------------


@pytest.mark.parametrize("rec", [r for r in C_LIB if r["pair_id"] == "E1-COL-A" and "theme" not in r["cell"]], ids=lambda r: r["cell"])
def test_e1_col_copies_match_library(rec):
    g = graph_from_neighbours(rec["prompt"])
    order = answer_order(rec["prompt"])
    task = ColouringTask(g, None, (), tuple(order) if order else None)
    assert render_neighbours(g, "fewest", order) == rec["prompt"]
    copy = rec["cell"]
    preds = predict_all(task, c_e1.col_members(copy))
    lib = rec["predictions"]
    for ours, theirs in [("FF-LIST", "FF-LIST"), ("FF-LABEL", "FF-LABEL"), ("LF", "LF"), ("DSATUR", "DSATUR"),
                         ("DPLL-LIST (D)", "DPLL-LIST (D, k=3)"), ("DPLL-LABEL (D)", "DPLL-LABEL (D, k=3)"),
                         ("FF-OUT (AR)", "FF-OUT (AR)")]:
        if ours not in preds or not isinstance(lib.get(theirs), dict):
            continue
        assert preds[ours]["answer"] == lib[theirs], (copy, ours)
    assert "FF-OUT (AR)" not in preds or copy != "c5-ANS-FREE"


@pytest.mark.parametrize("rec", [r for r in C_LIB if r["pair_id"] == "E1-SAT-A"], ids=lambda r: r["cell"])
def test_e1_sat_copies_match_library(rec):
    cnf = cnf_from_c_prompt(rec["prompt"])
    order = answer_order(rec["prompt"])
    assert render_c(cnf, order) == rec["prompt"]
    preds = predict_all(SatTask(cnf, (), tuple(order)), c_e1.sat_members(rec["cell"]))

    def lib_assignment(d):
        return {k: v == "T" for k, v in d.items() if not k.startswith("_")}

    for ours, theirs in [("GREEDY-MENTION", "GREEDY-MENTION"), ("GREEDY-INDEX", "GREEDY-INDEX"),
                         ("POLARITY (C0)", "POLARITY (C0)"), ("DPLL-MENTION (D, T first)", "DPLL-MENTION (D, T first)")]:
        assert preds[ours]["answer"] == lib_assignment(rec["predictions"][theirs]), (rec["cell"], ours)


def _knap_from_prompt(prompt):
    cap = int(re.search(r"at most (\d+) kg", prompt).group(1))
    rows = re.findall(r"^([A-Z]): value (\d+), weight (\d+)$", prompt, flags=re.M)
    return Knapsack(tuple(r[0] for r in rows), tuple(int(r[1]) for r in rows), tuple(int(r[2]) for r in rows), cap)


@pytest.mark.parametrize("rec", [r for r in C_LIB if r["pair_id"] == "E2-KNAP-A"], ids=lambda r: r["cell"])
def test_e2_knap_matches_library(rec):
    k = _knap_from_prompt(rec["prompt"])
    assert c_e2.knap_prompt(k) == rec["prompt"]
    preds = predict_all(KnapsackTask(k), c_e2.item_members("KNAP"))
    for name in ("INPUT-FIT", "RATIO-SKIP", "RATIO-PREFIX", "VALUE", "LARGEST-FIT", "DIFF", "RATIO+BEST-SINGLE"):
        assert preds[name]["answer"] == rec["predictions"][name], (rec["cell"], name)
    assert preds["EXACT"]["answer"] == rec["predictions"]["DP-EXACT"]


def test_e2_col_library_edits_have_their_signatures():
    base = find("C_constructive", pair_id="E2-COL-A", cell="BASE")
    g = graph_from_neighbours(base["prompt"])
    task = ColouringTask(g, None, (), tuple(g.vertices))
    sigs = {e.text: s for e, _, s in E.search(task, c_e2.SIGNATURE["COL"], lambda t: G.chromatic_number(t.graph),
                                               lambda s: True, edits=E.colouring_edits(task, ("add_edge",)))}

    def sig(u, v):
        return sigs.get(f"add edge {u}-{v}") or sigs[f"add edge {v}-{u}"]

    s = sig("v39", "v58")  # the library's D(FF|DSATUR) edit
    assert s["FF"] and not s["DSATUR"] and not s["TRUTH"]
    s = sig("v58", "v64")  # the library's G-ONLY edit
    assert s["TRUTH"]


def test_e3_library_gadget_prompts_and_lemma():
    base_u = find("C_constructive", pair_id="E3-COL-A", cell="d=2/BASE/U-LIST")
    base_i = find("C_constructive", pair_id="E3-COL-A", cell="d=2/BASE/I")
    crit_i = find("C_constructive", pair_id="E3-COL-A", cell="d=2/CRITICAL/I")
    g = graph_from_neighbours(base_u["prompt"])
    assert c_e3.u_prompt(g, list(g.vertices)) == base_u["prompt"]
    assert c_e3.i_prompt(g, "v29") == base_i["prompt"]
    ff = run("coloring", "FF", ColouringTask(g), {"order": "LIST"}).answer
    assert ff["v29"] == base_i["ground_truth"]["answer"]
    gc = graph_from_neighbours(crit_i["prompt"])
    assert run("coloring", "FF", ColouringTask(gc), {"order": "LIST"}).answer["v29"] == crit_i["ground_truth"]["answer"]


def test_e5_library_prompts_and_states():
    stuck = find("C_constructive", pair_id="E5-COL-A", cell="STUCK/vertexA/edgeA")
    assert c_e5.col_edge_prompt(graph_from_edge_list(stuck["prompt"])) == stuck["prompt"]
    for cell, want in (("STATE-s1: POLARITY vs GREEDY", "s1"), ("STATE-s2: UC vs GREEDY", "s2")):
        rec = find("C_constructive", pair_id="E5-SAT-STATE-A", cell=cell)
        cnf = cnf_from_c_prompt(rec["prompt"])
        fixed = {k: v == "T" for k, v in rec["params"]["fixed"].items()}
        assert render_c(cnf, list(cnf.var_names), fixed) == rec["prompt"]
        assert c_e5.sat_state_classes(cnf, fixed) == want
    L = F.lit
    for cell, prem in (("ORDER-A", (F.nand(L("E"), L("C")), F.disj(L("B"), L("C")), F.nand(L("B"), L("A")), F.disj(L("E"), L("A")))),):
        rec = find("C_constructive", pair_id="E5-ENT-A", cell=cell)
        a = EntailmentTask(prem, L("D"), "YN")
        b = EntailmentTask(tuple(reversed(prem)), L("D"), "YN")
        assert c_e5.ent_prompt(a) == rec["prompt"]
        assert c_e5.ent_prompt(b) == find("C_constructive", pair_id="E5-ENT-A", cell="ORDER-B (premises reversed)")["prompt"]
        assert (c_e5.greedy_cm(a), c_e5.greedy_cm(b)) == ("YES", "NO")


# --- gadget properties ------------------------------------------------------------------------------


@pytest.mark.parametrize("seed", range(6))
def test_gadget_lemma_and_constant_size(seed):
    rng = np.random.default_rng(seed)
    sizes = set()
    for d in (1, 3, 5):
        gad = c_e3.build_gadget(rng, 3, 6, d, 0.5, 3)
        vals = c_e3.nor_values(gad, gad["orient"])
        g = G.Graph(tuple(gad["listing"]), tuple(gad["edges"]))
        ff = run("coloring", "FF", ColouringTask(g), {"order": "LIST"}).answer
        assert all((ff[x] == 1) == v for x, v in vals.items())
        assert len(set(ff.values())) == 3 == G.chromatic_number(g)
        sizes.add((g.n, g.m))
    assert len(sizes) == 1


def test_gadget_deep_three_digit_labels():
    items, stats = c_e3.generate("smoke", 2, depths=[14], D_max=14)
    assert items and all(len(v) == 4 for v in c_e3.load_task(items[0].instance).graph.vertices)
    assert run_checks(items, c_e3.check_set)["failures"] == []


# --- generated sets validate ---------------------------------------------------------------------------


def test_e1_smoke_validates_and_no_leakage():
    items, stats = c_e1.generate("smoke", 5)
    assert len(items) == len(c_e1.cells({}))
    assert run_checks(items, c_e1.check_set)["failures"] == []
    test_items, _ = c_e1.generate("test", 5, per_cell=1)
    assert check_leakage(items + test_items) == []


def test_e1_edge_list_and_repeat_arms():
    items, _ = c_e1.generate("smoke", 6, domains=["COL"], serialisation="edge_list_shuffled", repeat_prompt=True)
    assert all("Edges: " in it.prompt and "repeated verbatim" in it.prompt for it in items)
    assert run_checks(items, c_e1.check_set)["failures"] == []


def test_e2_smoke_small_validates():
    items, stats = c_e2.generate("smoke", 3, n_col=12, n_sat=14, n_knap=8)
    assert {it.cell for it in items} == set(c_e2.cells({}))
    assert run_checks(items, c_e2.check_set)["failures"] == []


def test_e3_smoke_small_validates():
    items, stats = c_e3.generate("smoke", 4, D_max=4, depths=[1, 2, 4])
    assert len(items) == 27
    assert run_checks(items, c_e3.check_set)["failures"] == []
    assert stats["audit"]["d=4"]["N"] == 1


def test_e5_smoke_validates():
    items, stats = c_e5.generate("smoke", 2)
    assert {it.cell for it in items} == set(c_e5.cells({}))
    assert run_checks(items, c_e5.check_set)["failures"] == []
