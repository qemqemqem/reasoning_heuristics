"""Regression tests for the generator and likelihood-table defects found in the 2026-11-17 review
(docs/reviews/2026-11-17-project-review.md, G1-G8, V1-V3, V8). Each test reproduces the defect on
the generators' own output."""

import json
from collections import Counter, defaultdict
from functools import lru_cache

import numpy as np
import pytest

from reasoning_heuristics.generators import ah_e2, ah_e5, ah_e8, b4_e1, b4_e2, c_e1, c_e3, c_e5
from reasoning_heuristics.generators.common import EPS, decision_channel, make_item
from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.tasks import ColouringTask, SatTask, load_task
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.validate.checks import KNOWN_LINEAGE_GAPS, check_item, check_lineage
from reasoning_heuristics.validate.independent import recheck_readouts


@lru_cache(maxsize=None)
def c_e1_col():
    return tuple(c_e1.generate("smoke", 5, domains=["COL"])[0])


@lru_cache(maxsize=None)
def c_e1_sat():
    return tuple(c_e1.generate("smoke", 5, domains=["SAT"])[0])


@lru_cache(maxsize=None)
def c_e3_small():
    return c_e3.generate("smoke", 4, D_max=4, depths=[1, 2, 4])


def label_of(item, key):
    return next(lbl for lbl, k in item.extra["outcome_classes"].items() if k == key)


# --- G1: honest outcome classes ----------------------------------------------------------------------


def test_invalid_colourings_are_evidence_against_exact():
    """C E1-COL: an invalid answer (e.g. every vertex colour 1) used to share "other" with EXACT's
    unlisted optimal colourings, so it counted for EXACT and against FF/DSATUR/DPLL."""
    for it in c_e1_col():
        assert it.disconfirms[label_of(it, "_other")]["EXACT"] > 0.5, it.item_id
        unlisted = [k for k in it.extra["outcome_classes"].values() if k.startswith("_in:")]
        assert unlisted == ["_in:EXACT"], it.item_id
        assert it.disconfirms[label_of(it, "_in:EXACT")]["EXACT"] == 0.0


def test_unsat_answers_are_evidence_against_exact_on_satisfiable_items():
    for it in c_e1_sat():
        assert "answer = UNSAT" in it.disconfirms, it.item_id
        assert it.disconfirms["answer = UNSAT"]["EXACT"] > 0.5, it.item_id


def test_unique_but_different_optima_make_the_knapsack_inversion_tables_discriminate():
    items, _ = ah_e5.generate("smoke", 6, domains=["KNAP"])
    for it in items:
        if it.params["framing"] in ("I", "I+R"):
            spread = max(max(r.values()) - min(r.values()) for r in it.disconfirms.values())
            assert spread > 1.0, it.item_id
            assert [r["exact"] for r in it.disconfirms.values()] != [r["A3 TT[exact]"] for r in it.disconfirms.values()]


def test_set_membership_is_serialised():
    it = c_e1_col()[0]
    spec = it.extra["channel_spec"]["set_valued"]["EXACT"]
    assert spec["rule"] == "colouring" and spec["size"] == it.ground_truth["n_optimal_partitions"]
    assert spec["params"] == {"graph": "stated", "colours": it.ground_truth["chromatic_number"], "exactly": True}


# --- G4: one slip model, stated consistently ---------------------------------------------------------


def test_slip_text_matches_the_table():
    it = c_e1_col()[0]
    K = len(it.extra["outcome_classes"])
    assert f"{1 - EPS + EPS / K:.3f}" in it.hypotheses["FF-LIST"]["eval_prediction"]
    assert "0.90" not in it.hypotheses["EXACT"]["eval_prediction"]
    assert "set-valued" in it.hypotheses["EXACT"]["eval_prediction"]
    assert "preview" in it.likelihood_model and it.extra["likelihood"]["K"] == K


# --- G2: every listed member has a row ---------------------------------------------------------------


def test_every_listed_member_has_a_row():
    items = list(c_e1_col()) + c_e3_small()[0]
    for it in items:
        for outcome, row in it.disconfirms.items():
            assert set(row) == set(it.predictions), (it.item_id, outcome, set(it.predictions) - set(row))


# --- V3: discrimination on the scoring channel -------------------------------------------------------


def _greedy_polarity_cnf():
    rng = np.random.default_rng(0)
    for _ in range(500):
        cnf = S.random_ksat(8, 12, 3, rng, tuple(f"x{i}" for i in range(10, 18)))
        t = SatTask(cnf)
        g = run("sat", "GREEDY", t, {"order": "MENTION"}).answer
        p = run("sat", "POLARITY", t).answer
        if isinstance(g, dict) and S.satisfies(cnf, g) and S.satisfies(cnf, p) and g != p:
            return t
    raise AssertionError("no instance found")


def test_discriminates_judges_the_scoring_channel():
    """Two different satisfying assignments are the same answer on a decision channel."""
    task = _greedy_polarity_cnf()
    it = make_item(vertical="A/H", eval_id="TEST", set_id="s", cell="c", domain="SAT", framing="x", prompt="p",
                   answer_format="sat_json", task=task, ground_truth={"satisfiable": True},
                   specs=[("GREEDY", "GREEDY", {"order": "MENTION"}), ("POLARITY", "POLARITY", {})],
                   channel=decision_channel("SAT", "UNSAT"), seed=100_001, tier="dev", generator="test", base_hash="")
    assert [f.message for f in check_item(it) if f.check == "discriminates"]


def test_c_e3_items_discriminate():
    items, _ = c_e3_small()
    assert not [f for it in items for f in check_item(it) if f.check == "discriminates"]


# --- V1, V2: the C E3 instructed question is part of the task ----------------------------------------


def test_c_e3_instructed_questions_have_their_own_content_hash():
    items, _ = c_e3_small()
    by_set = defaultdict(list)
    for it in items:
        if it.params["arm"] == "I":
            by_set[it.set_id].append(it)
            task = load_task(it.instance)
            assert task.target == it.params["target"] == it.instance["target"]
            assert recheck_readouts(it.instance, it.ground_truth, it.params) == []  # the independent first-fit
    for sid, group in by_set.items():
        assert len({it.content_hash for it in group}) == 3, sid
    t = load_task(items[0].instance)
    other = ColouringTask(t.graph.relisted(list(reversed(t.graph.vertices))), t.k)
    assert ColouringTask(t.graph, t.k).content_key() == other.content_key()  # no target: listing is presentation


# --- V8: lineage --------------------------------------------------------------------------------------


def lineage_failures(items):
    failures, gaps = check_lineage(list(items), known=set())
    return [f.message for f in failures + gaps]


def test_no_lineage_gaps_are_tolerated():
    assert KNOWN_LINEAGE_GAPS == set()


def test_lineage_of_c_and_b4_sets():
    assert lineage_failures(c_e1_col()) == []
    assert lineage_failures(c_e1_sat()) == []
    assert lineage_failures(c_e3_small()[0]) == []
    assert lineage_failures(b4_e1.generate("smoke", 3)[0]) == []
    assert lineage_failures(b4_e2.generate("smoke", 5)[0]) == []


def test_lineage_of_a_h_sets():
    assert lineage_failures(ah_e5.generate("smoke", 6)[0]) == []
    ent, _ = ah_e2.generate("smoke", 4, domains=["ENT"])
    assert lineage_failures(ent) == []


# --- G3: B4/C4 E1 option order -----------------------------------------------------------------------


def test_b4_e1_correct_letters_are_balanced_within_cells():
    items, _ = b4_e1.generate("dev", 3, per_cell=4)
    letters = defaultdict(Counter)
    for it in items:
        if it.params["F"] == "MC":
            letters[it.cell][it.ground_truth["answer"]] += 1
            assert it.ground_truth["answer"] == it.params["mc_correct_letter"]
    assert letters and all(sorted(c) == ["A", "B", "C", "D"] for c in letters.values()), dict(letters)


# --- G5: E8 predictions that depend on a response ----------------------------------------------------


def test_e8_specs_store_no_response_dependent_prediction():
    items, _ = ah_e8.generate("smoke", 1)
    assert all(ah_e8.TRACE_DRIVEN not in it.predictions and ah_e8.D_DENSITY not in it.predictions for it in items)
    spec = next(it for it in items if it.cell == "transplant/K->J")
    for decision in (True, False):
        donor = '<think>x25 = 1, then ...</think>\n' + json.dumps({"satisfiable": decision, "assignment": None})
        m = ah_e8.materialise(spec, donor)
        want = "SAT" if decision else "UNSAT"
        assert m["response_predictions"][ah_e8.TRACE_DRIVEN]["answer"] == want
        assert m["disconfirms"][f"answer = {want}"][ah_e8.TRACE_DRIVEN] == 0.0
    gave_up = ah_e8.materialise(spec, "<think>too many clauses</think> I cannot decide.")
    assert gave_up["response_predictions"][ah_e8.D_DENSITY]["answer"] == spec.predictions[ah_e8.CUE]["answer"]
    assert "disconfirms" not in gave_up


# --- G6: C E3 depth accounting -------------------------------------------------------------------------


def test_c_e3_local_proxies_bracket_the_targets_first_fit_depth():
    items, stats = c_e3_small()
    for it in items:
        d, D = it.params["target_depth"], it.params["target_ff_depth"]
        assert D == d + 2 == c_e3.ff_depth(load_task(it.instance).graph, it.params["target"])
        t = it.params["target"]
        ff = it.predictions["FF-LIST (C1 seq)"]["answer"]
        short = it.predictions[f"LOCAL-{D - 1}-LIST (const proxy, one round short)"]["answer"]
        reach = it.predictions[f"LOCAL-{D}-LIST (const proxy, reaches the target)"]["answer"]
        if isinstance(ff, dict):
            assert short[t] == 1 and reach[t] == ff[t], it.item_id
    for d, row in stats["audit"].items():
        D = row["target_ff_depth"]
        assert f"LOCAL-{D - 1}-LIST/one" in row["proxy_accuracy"] and f"LOCAL-{D - 1}-LIST/free" not in row["proxy_accuracy"]


# --- G7: C E5 give-up members -------------------------------------------------------------------------


def test_c_e5_lists_a_give_up_member():
    items, _ = c_e5.generate("smoke", 2, parts=["COL", "SAT"])
    for it in items:
        give_up = [lbl for lbl in it.predictions if "A1 give-up" in lbl]
        assert len(give_up) == 1, it.item_id
        if it.cell.startswith("COL/STUCK"):
            assert it.disconfirms["answer = IMPOSSIBLE"][give_up[0]] == 0.0


def test_selection_filters_are_recorded():
    assert all(it.params["filters"] for it in c_e1_col() + c_e1_sat())
    items, _ = c_e5.generate("smoke", 2, parts=["COL"])
    assert all(any("selects on FF" in f for f in it.params["filters"]) for it in items)


# --- G8: review --reuse on a fresh clone ---------------------------------------------------------------


def test_review_reuse_reads_the_committed_gz(tmp_path, monkeypatch):
    from reasoning_heuristics import review
    from reasoning_heuristics.generate import output_path
    from reasoning_heuristics.schema.item import compress, write_jsonl

    items, _ = b4_e1.generate("smoke", 11)
    for tier in ("smoke", "dev", "test"):
        path = output_path(tmp_path, "B4/C4", "E1", tier, 1)
        write_jsonl(items, path)
        if tier != "test":
            compress(path)
            path.unlink()  # a fresh clone has only the committed .jsonl.gz
        report = {"generation": {"accepted": 1, "attempts": 1}, "generation_seconds": 1.0, "path": str(path),
                  "validation": {"items": len(items), "items_passed": len(items), "pass_rate": 1.0, "failures": []}}
        path.with_suffix(".report.json").write_text(json.dumps(report))
    monkeypatch.setattr(review, "ITEMS", tmp_path)
    monkeypatch.setattr(review, "REVIEW", tmp_path / "review")
    rows = review.build([("B4/C4", "E1")], 1, reuse=True, dev_per_cell=None)
    assert rows[0]["tiers"]["dev"]["items"] == len(items)
