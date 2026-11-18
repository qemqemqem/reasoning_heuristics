"""Error agreement with explicit tie handling, and within-cell permutation baselines."""

import numpy as np
from identify_helpers import decision_item, patterned_items, plant

from reasoning_heuristics.identify.agreement import ea_lift, error_agreement, permutation_weights, permute_within_cell
from reasoning_heuristics.identify.likelihood import Observation, UnitModel
from reasoning_heuristics.identify.mixture import em
from reasoning_heuristics.identify.units import Unit


def unit_of(items):
    return Unit("T_E0", "SAT", items)


def test_tie_handling():
    # EXACT says SAT everywhere. On items 0-1, X and Y both (wrongly) say UNSAT; on items 2-3 only X does.
    items = [decision_item(0, {"X": "UNSAT", "Y": "UNSAT", "Z": "SAT"}),
             decision_item(1, {"X": "UNSAT", "Y": "UNSAT", "Z": "UNSAT"}),
             decision_item(2, {"X": "UNSAT", "Y": "SAT", "Z": "SAT"}),
             decision_item(3, {"X": "UNSAT", "Y": "SAT", "Z": "SAT"})]
    um = UnitModel(unit_of(items))
    obs = [Observation(i, "UNSAT") for i in range(4)]  # the model is wrong everywhere, always UNSAT
    inc = error_agreement(um, obs, "include")
    exc = error_agreement(um, obs, "exclude")
    spl = error_agreement(um, obs, "split")
    assert inc["X"].ea == 1.0 and inc["X"].n == 4
    assert inc["Y"].ea == 1.0 and inc["Y"].n == 2
    assert exc["X"].n == 2 and exc["X"].ea == 1.0  # only items 2-3, where X's error is its own
    assert exc["Y"].ea is None  # Y's errors are always shared
    # item 0: shared by X, Y (1/2 each); item 1: shared by X, Y, Z (1/3 each); items 2, 3: X alone
    assert abs(spl["X"].agree - (0.5 + 1 / 3 + 2)) < 1e-12 and abs(spl["Z"].agree - 1 / 3) < 1e-12


def test_permutation_baseline_is_null_for_an_unrelated_responder():
    rng = np.random.default_rng(0)
    um = UnitModel(unit_of(patterned_items(400, rng)))
    obs = [Observation(i, "SAT" if rng.random() < 0.5 else "UNSAT") for i in range(400)]
    lifts, exch = ea_lift(um, obs, n_perm=200, rng=rng, stat="co_error")
    assert exch == 1.0
    for name in ("B", "C", "D"):
        assert abs(lifts[name].lift) < 0.1


def test_permutation_lift_detects_a_planted_member():
    rng = np.random.default_rng(1)
    items = patterned_items(400, rng)
    for it in items:  # make EXACT's answer vary so members have errors to agree on
        it["predictions"]["EXACT"]["answer"] = "SAT" if rng.random() < 0.5 else "UNSAT"
    um = UnitModel(unit_of(items))
    obs = plant(um, {"C": 1.0}, eps=0.05, rho=0.3, rng=rng)
    ea = error_agreement(um, obs)
    assert ea["C"].ea == 1.0  # two-valued channel: EA is 1 by construction ...
    lifts, _ = ea_lift(um, obs, n_perm=200, rng=rng, stat="co_error")  # ... so co-error carries the signal
    assert lifts["C"].observed > 0.9 and lifts["C"].lift > 0.3 and lifts["C"].p_value < 0.01
    assert abs(lifts["B"].lift) < 0.15
    T = um.tensors(obs)
    pi = em(T).pi[0]
    wl, _ = permutation_weights(um, obs, pi, n_perm=20, rng=rng)
    assert wl["C"].lift > 0.5


def test_permutation_moves_answers_only_within_cell():
    rng = np.random.default_rng(2)
    items = patterned_items(40, rng, cells=4)
    um = UnitModel(unit_of(items))
    obs = [Observation(i, "SAT" if i < 20 else "UNSAT") for i in range(40)]
    pobs, exch = permute_within_cell(um, obs, rng)
    for o, p in zip(obs, pobs):
        assert o.item == p.item
    for cell in range(4):
        rows = [n for n in range(40) if items[n]["cell"] == f"c{cell}"]
        assert sorted(obs[n].key for n in rows) == sorted(pobs[n].key for n in rows)
