"""Fake models and the recovery harness."""

from pathlib import Path

import numpy as np
import pytest
from identify_helpers import patterned_items

from reasoning_heuristics.identify.engine import separations
from reasoning_heuristics.identify.fake import Scenario, always_answer, simulate, to_responses, truth_vector
from reasoning_heuristics.identify.likelihood import NEAR_MISS, UnitModel
from reasoning_heuristics.identify.mixture import fit
from reasoning_heuristics.identify.recovery import choose_triple, feature_levels, main, run_unit, summarise, table
from reasoning_heuristics.identify.units import Unit, load_items, make_units

ROOT = Path(__file__).resolve().parents[1]


def test_simulate_plants_the_weights():
    rng = np.random.default_rng(0)
    um = UnitModel(Unit("T_E0", "SAT", patterned_items(2000, rng)))
    sc = Scenario("mix", "mix", {"B": 0.6, "C": 0.3, "D": 0.1}, eps=0.0)
    obs = simulate(um, sc, rng)
    r = fit(um.tensors(obs), n_boot=0)
    w = dict(zip(r.labels, r.pi))
    assert abs(w["B"] - 0.6) < 0.04 and abs(w["C"] - 0.3) < 0.04
    t = truth_vector(um, sc.weights, sc.q)
    assert abs(t.sum() - 1) < 1e-12
    rs = to_responses(um, obs)
    assert all(x.category == "ok" for x in rs)


def test_always_and_withheld_and_truncated():
    rng = np.random.default_rng(1)
    um = UnitModel(Unit("T_E0", "SAT", patterned_items(50, rng)))
    obs = simulate(um, Scenario("a", "null_always", always=True), rng)
    assert {o.key for o in obs} == {always_answer(um, 0)}
    sc = Scenario("t", "mix", {"B": 1.0}, eps=0.0, truncation={"B": 1.0})
    assert all(o.censored for o in simulate(um, sc, rng))
    keep = [l for l in um.labels if l != "C"]
    um_fit = UnitModel(um.unit, labels=keep)
    t = truth_vector(um_fit, {"B": 0.7, "C": 0.3}, 0.0)
    assert abs(t.sum() - 0.7) < 1e-12  # the withheld mass has no column


def test_rules_for_triple_and_feature_levels():
    items = load_items(ROOT / "data/items/smoke/C_E2_smoke_s1.jsonl.gz")
    unit = make_units(items)["C_E2/colouring"]
    um = UnitModel(unit)
    tri = choose_triple(um, separations(um))
    assert tri is not None and len(set(tri)) == 3
    lv, desc = feature_levels(unit)
    assert set(lv) == {0, 1}


def test_summarise_gates():
    truths = np.array([[0.6, 0.4, 0.0]] * 10)
    ests = truths + 0.01
    res = summarise(truths, ests, ests - 0.05, ests + 0.05, ["a", "b", "q"])
    assert res["pass"] and res["median_width"] == pytest.approx(0.1)
    res = summarise(truths, ests + 0.1, ests + 0.05, ests + 0.15, ["a", "b", "q"])
    assert not res["gates"]["bias"] and not res["gates"]["coverage"]


def test_run_unit_end_to_end_small(tmp_path):
    items = load_items(ROOT / "data/items/smoke/C_E2_smoke_s1.jsonl.gz")
    unit = make_units(items)["C_E2/knapsack"]
    cfg = {"reps": 3, "boot": 10, "single_reps": 2, "feature_reps": 2, "feature_boot": 3, "offzoo_reps": 2, "seed": 0,
           "scenarios": ["single", "mix", "feature", "null_q", "null_always", "off_zoo", "clustered", "truncated", "misspec"]}
    out = run_unit(unit, cfg)
    for k in ("single", "mix", "feature", "null_q", "null_always", "off_zoo", "clustered", "truncated_excluded",
              "truncated_token_model", "misspec_uniform_fit_on_near_miss"):
        assert k in out["scenarios"], k
    import json

    from reasoning_heuristics.identify.recovery import report

    doc = {"label": "t", "items": "x", "config": cfg, "provenance": {"git_sha": "0" * 40, "git_dirty": False},
           "units": [out]}
    path = tmp_path / "r.json"
    path.write_text(json.dumps(doc))
    assert "C_E2/knapsack" in table([str(path)])
    md = report(str(path), [str(path)])
    for section in ("<!-- dev -->", "<!-- misspec -->", "<!-- offzoo -->", "<!-- checks -->", "<!-- sweep -->",
                    "<!-- needed -->", "<!-- where -->"):
        assert section in md


def _always_items(n, rng):
    from identify_helpers import decision_item

    items = []
    for i in range(n):
        ans = {"POS": "SAT", "NEG": "UNSAT", "B": "SAT" if i % 2 else "UNSAT", "C": "SAT" if rng.random() < 0.5 else "UNSAT"}
        items.append(decision_item(i, ans, cell=f"c{i % 2}", exact="SAT" if rng.random() < 0.5 else "UNSAT"))
    return items


def test_identifiability_finds_q_as_a_combination():
    from reasoning_heuristics.identify.engine import identifiability

    rng = np.random.default_rng(0)
    um = UnitModel(Unit("T_E0", "SAT", _always_items(60, rng)))
    d = identifiability(um, rng=rng)
    assert d["deficiency"] == 1 and d["not_identified"] == ["q"]
    assert d["null_directions"] == ["q = 0.5 × POS + 0.5 × NEG"]
    assert "POS + 0.5 × q" in d["identified"] and "NEG + 0.5 × q" in d["identified"]
    # the transform maps weights to the identified combinations, orthogonal to the null direction
    T, cols = d["transform"], d["columns"]
    v = np.zeros(len(cols))
    v[cols.index("q")], v[cols.index("POS")], v[cols.index("NEG")] = 1.0, -0.5, -0.5
    assert np.allclose(T @ v, 0)
    d2 = identifiability(UnitModel(Unit("T_E0", "SAT", patterned_items(60, rng))), rng=rng)
    assert d2["deficiency"] == 0 and np.allclose(d2["transform"], np.eye(len(d2["columns"])))


def test_null_q_is_not_testable_where_q_is_not_identified():
    rng = np.random.default_rng(1)
    unit = Unit("T_E0", "SAT", _always_items(40, rng))
    cfg = {"reps": 2, "boot": 10, "single_reps": 2, "feature_reps": 2, "feature_boot": 3, "offzoo_reps": 1, "seed": 0,
           "scenarios": ["null_q", "single", "mix"]}
    out = run_unit(unit, cfg)
    assert out["scenarios"]["null_q"]["testable"] is False and out["scenarios"]["null_q"]["pass"] is None
    assert "null_q" in out["not_testable"]
    assert out["identifiability"]["near-miss"]["null_directions"] == ["q = 0.5 × POS + 0.5 × NEG"]
    involved = set(out["identifiability"]["near-miss"]["involved"])
    assert involved == {"POS", "NEG", "q"}
    mix = out["scenarios"]["mix"]
    assert mix.get("testable", True) == (not involved & set(out["triple"]))


def test_engine_marks_non_identified_weights():
    from identify_helpers import responses_from

    from reasoning_heuristics.identify.engine import fit_unit

    rng = np.random.default_rng(2)
    um = UnitModel(Unit("T_E0", "SAT", _always_items(80, rng)))
    obs = simulate(um, Scenario("m", "mix", {"POS": 0.5, "B": 0.5}), rng)
    rep = fit_unit(um, responses_from(um, obs), n_boot=20, n_perm=0)
    w = rep["fit"]["weights"]
    for lab in ("unexplained (q)", "POS", "NEG"):  # every member of the dependency, not just the pivot
        assert w[lab]["pi"] == "not identified" and 0 <= w[lab]["range"][0] <= w[lab]["range"][1] <= 1
    assert isinstance(w["B"]["pi"], float)
    assert abs(rep["fit"]["identified"]["POS + 0.5 × q"]["est"] - 0.5) < 0.15


def test_weight_ranges_follow_the_null_direction():
    from reasoning_heuristics.identify.engine import weight_ranges

    # columns A, B, q with q = 1/2 A + 1/2 B: the null vector (A, B, q) = (-1/2, -1/2, 1)
    lo, hi = weight_ranges(np.array([0.3, 0.3, 0.4]), np.array([[-0.5, -0.5, 1.0]]))
    assert np.allclose(lo, [0.0, 0.0, 0.0]) and np.allclose(hi, [0.5, 0.5, 1.0])
    lo, hi = weight_ranges(np.array([0.2, 0.8]), np.zeros((0, 2)))
    assert np.allclose(lo, [0.2, 0.8]) and np.allclose(hi, [0.2, 0.8])


@pytest.mark.slow
def test_cli_run_on_smoke(tmp_path, capsys):
    out = tmp_path / "smoke.json"
    rc = main(["run", "--items", str(ROOT / "data/items/smoke"), "--units", "C_E2/knapsack;AH_E1/SAT", "--reps", "4",
               "--boot", "20", "--single-reps", "2", "--feature-reps", "2", "--feature-boot", "4", "--offzoo-reps", "2",
               "--workers", "2", "--out", str(out)])
    assert rc == 0 and out.exists()


def test_cli_units_are_semicolon_separated_and_unknown_names_fail(tmp_path, capsys):
    """Unit names contain commas ("C_E5/colouring (k=3, partial colouring given)"), so --units takes a
    ';'-separated list, and a name that matches no unit stops the run instead of being skipped."""
    out = tmp_path / "none.json"
    rc = main(["run", "--items", str(ROOT / "data/items/smoke"), "--units", "C_E2/knapsack;C_E2/knapsack,AH_E1/SAT",
               "--out", str(out)])
    assert rc == 2 and not out.exists()
    assert "C_E2/knapsack,AH_E1/SAT" in capsys.readouterr().err
