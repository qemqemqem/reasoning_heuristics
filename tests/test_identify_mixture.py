"""The mixture fit: EM with availability, slip estimation, the cluster bootstrap, data ties and
feature-dependent weights."""

from pathlib import Path

import numpy as np
import pytest
from identify_helpers import decision_item, patterned_items, plant

from reasoning_heuristics.identify.likelihood import NEAR_MISS, UnitModel
from reasoning_heuristics.identify.mixture import cluster_bootstrap, data_ties, em, fit, fit_features, fit_softmax
from reasoning_heuristics.identify.units import Unit, load_items, make_units

ROOT = Path(__file__).resolve().parents[1]


def unit_of(items):
    return Unit("T_E0", "SAT", items)


def weights_by_label(T, pi):
    return dict(zip(T.labels + ["q"], pi))


def test_em_recovers_planted_weights():
    rng = np.random.default_rng(0)
    um = UnitModel(unit_of(patterned_items(3000, rng)))
    obs = plant(um, {"B": 0.5, "C": 0.3, "D": 0.1}, eps=0.0, rho=0.3, rng=rng, q=0.1)
    T = um.tensors(obs)
    w = weights_by_label(T, em(T).pi[0])
    assert abs(w["B"] - 0.5) < 0.04 and abs(w["C"] - 0.3) < 0.04 and abs(w["D"] - 0.1) < 0.04
    assert w["A = EXACT"] < 0.04 and abs(w["q"] - 0.1) < 0.04


def test_finite_channels_count_slips_as_unexplained():
    """On a two-valued channel a slip is a coin flip, i.e. a mixture with q: eps is held at 0 and the
    estimates are the slip-free equivalent pi_h (1 - 2 eps), pi_0 + 2 eps (1 - pi_0)."""
    rng = np.random.default_rng(10)
    um = UnitModel(unit_of(patterned_items(4000, rng)))
    obs = plant(um, {"B": 0.5, "C": 0.3, "D": 0.1}, eps=0.15, rho=0.3, rng=rng, q=0.1)
    T = um.tensors(obs)
    assert not T.slip_identified
    r = em(T)
    w = weights_by_label(T, r.pi[0])
    assert r.eps[0] == 0.0
    for h, p in (("B", 0.5), ("C", 0.3), ("D", 0.1)):
        assert abs(w[h] - p * 0.7) < 0.04
    assert abs(w["q"] - (0.1 + 0.3 * 0.9)) < 0.05


def test_availability_renormalises():
    """A member missing on half the items keeps its weight on the items where it exists."""
    rng = np.random.default_rng(1)
    items = patterned_items(3000, rng)
    for it in items[::2]:
        del it["predictions"]["C"]
    um = UnitModel(unit_of(items))
    obs = plant(um, {"B": 0.4, "C": 0.4, "D": 0.2}, eps=0.0, rho=0.3, rng=rng)
    T = um.tensors(obs)
    w = weights_by_label(T, em(T).pi[0])
    assert abs(w["C"] - 0.4) < 0.05 and abs(w["B"] - 0.4) < 0.05


def test_rho_is_estimated_on_witness_answers():
    items = load_items(ROOT / "data/items/dev/C_E2_dev_s1.jsonl.gz")
    um = UnitModel(make_units(items)["C_E2/knapsack"], NEAR_MISS)
    rng = np.random.default_rng(2)
    label = next(c.members[0] for c in um.columns if um.pred(0, c.members[0]).kind == "det")
    obs = plant(um, {label: 1.0}, eps=0.4, rho=0.5, rng=rng, reps=40)
    r = em(um.tensors(obs))
    assert abs(r.eps[0] - 0.4) < 0.05 and abs(r.rho[0] - 0.5) < 0.1


def test_bca_interval_and_jackknife():
    from reasoning_heuristics.identify.mixture import bca_interval

    rng = np.random.default_rng(7)
    boot = rng.normal(0.5, 0.05, size=(4000, 1))
    jack = 0.5 + rng.normal(0, 0.01, size=(30, 1))
    lo, hi = bca_interval(boot, np.array([0.5]), jack)
    plo, phi = np.percentile(boot, 2.5, 0), np.percentile(boot, 97.5, 0)
    assert abs(lo[0] - plo[0]) < 0.01 and abs(hi[0] - phi[0]) < 0.01  # symmetric and unbiased: BCa = percentile
    lo2, hi2 = bca_interval(boot, np.array([0.55]), jack)  # estimate above most draws: the interval shifts up
    assert lo2[0] > lo[0] and hi2[0] > hi[0]
    um = UnitModel(unit_of(patterned_items(200, rng)))
    T = um.tensors(plant(um, {"B": 0.6, "C": 0.4}, eps=0.0, rho=0.3, rng=rng))
    res = fit(T, n_boot=20, rng=rng, jackknife=True)
    assert res.jack.shape == (len(np.unique(T.cluster)), len(res.labels))


def test_cluster_bootstrap_resamples_whole_clusters():
    cluster = np.array([0, 0, 1, 1, 1, 2, 3, 3])
    W = cluster_bootstrap(cluster, 50, np.random.default_rng(0))
    assert W.shape == (50, 8)
    for row in W:
        for c in range(4):
            assert len(set(row[cluster == c])) == 1
        assert sum(row[cluster == c][0] for c in range(4)) == 4


def test_fit_interval_contains_truth_and_flags_data_ties():
    rng = np.random.default_rng(3)
    items = patterned_items(400, rng)
    for it in items:  # E duplicates C except on items no response separates: identical rows
        it["predictions"]["E"] = dict(it["predictions"]["C"], member="E")
    items[0]["predictions"]["E"]["answer"] = "UNSAT" if items[0]["predictions"]["C"]["answer"] == "SAT" else "SAT"
    um = UnitModel(unit_of(items[1:]))  # without the separating item: a design tie
    assert any(g.name == "C = E" for g in um.columns)
    um2 = UnitModel(unit_of(items))
    assert not any(g.name == "C = E" for g in um2.columns)
    obs = [o for o in plant(um2, {"B": 0.6, "C": 0.4}, eps=0.0, rho=0.3, rng=rng) if o.item != 0]
    T = um2.tensors(obs)
    assert ["C", "E"] in data_ties(T)
    res = fit(T, n_boot=100, rng=rng)
    j = res.labels.index("B")
    assert res.lo[j] <= 0.6 <= res.hi[j]
    jc, je = res.labels.index("C"), res.labels.index("E")
    assert abs(res.pi[jc] + res.pi[je] - 0.4) < 0.1
    assert res.extra["data_ties"] == [["C", "E"]]


def test_softmax_recovers_feature_dependent_weights():
    rng = np.random.default_rng(4)
    items = patterned_items(2400, rng)
    um = UnitModel(unit_of(items))
    x = np.array([i % 2 for i in range(len(items))], dtype=float)
    obs = []
    from reasoning_heuristics.identify.likelihood import Observation

    for i in range(len(items)):
        wB = 0.8 if x[i] == 0 else 0.2
        h = "B" if rng.random() < wB else "C"
        obs.append(Observation(i, um.sample(i, h, 0.0, 0.3, rng)))
    T = um.tensors(obs)
    X = np.stack([np.ones(len(obs)), x[T.item]], 1)
    sf = fit_softmax(T, X)
    w = sf.weights(np.array([[1.0, 0.0], [1.0, 1.0]]))
    jb, jc = T.labels.index("B"), T.labels.index("C")
    assert abs(w[0, jb] - 0.8) < 0.06 and abs(w[1, jb] - 0.2) < 0.06
    assert abs(w[0, jc] - 0.2) < 0.06 and abs(w[1, jc] - 0.8) < 0.06
    # the constant model is the special case X = 1, and agrees with EM
    sc = fit_softmax(T, np.ones((T.n, 1)))
    r = em(T)
    assert np.allclose(sc.weights(np.ones((1, 1)))[0], r.pi[0], atol=0.02)
    res = fit_features(T, X, np.array([[1.0, 0.0], [1.0, 1.0]]), n_boot=10, rng=rng)
    assert res["lo"].shape == (2, len(T.labels) + 1)


@pytest.mark.slow
def test_cluster_bootstrap_coverage_with_clustered_strategies():
    """When the strategy is fixed per base (all variants of a base answered by one member), the
    cluster bootstrap still covers: a check of the interval method itself."""
    rng = np.random.default_rng(6)
    hits, reps = 0, 40
    for _ in range(reps):
        items = patterned_items(300, rng)
        um = UnitModel(unit_of(items))
        from reasoning_heuristics.identify.likelihood import Observation

        obs, choice = [], {}
        for i, it in enumerate(items):
            b = it["base_hash"]
            if b not in choice:
                choice[b] = "B" if rng.random() < 0.6 else "C"
            obs.append(Observation(i, um.sample(i, choice[b], 0.0, 0.3, rng)))
        res = fit(um.tensors(obs), n_boot=200, rng=rng)
        j = res.labels.index("B")
        hits += res.lo[j] <= 0.6 <= res.hi[j]
    assert hits / reps >= 0.85
