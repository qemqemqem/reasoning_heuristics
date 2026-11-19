"""Noise-model options (identify/noise.py, docs/NOISE_MODEL.md): the kernels and the strata q are
probability mass functions, the samplers draw from them, the default model is unchanged, and the
general EM recovers what it is given."""

import itertools
import math
from collections import Counter
from pathlib import Path

import numpy as np
import pytest
from identify_helpers import patterned_items, plant

from reasoning_heuristics.identify.fake import Scenario, simulate
from reasoning_heuristics.identify.likelihood import Observation, UnitModel
from reasoning_heuristics.identify.mixture import default_kernel, em, em_general, fit, noise_params
from reasoning_heuristics.identify.noise import CANDIDATES, NoiseModel, NoiseParams
from reasoning_heuristics.identify.spaces import (AD_CELLS, DMAX, BitSpace, PartitionSpace, _SatCodec, _stirling2,
                                                  _SubsetCodec, sample_partition_rgs, trunc_geom)
from reasoning_heuristics.identify.units import Unit, load_items, make_units

ROOT = Path(__file__).resolve().parents[1]


def all_partition_keys(space: PartitionSpace) -> list[str]:
    return sorted({space.encode(space.canon(np.array(c))) for c in itertools.product(range(space.n), repeat=space.n)})


def all_bit_keys(space: BitSpace) -> list[str]:
    return [space.encode(np.array(b, dtype=bool)) for b in itertools.product((False, True), repeat=space.n)]


@pytest.fixture(scope="module")
def knapsack_unit():
    return make_units(load_items(ROOT / "data/items/dev/C_E2_dev_s1.jsonl.gz"))["C_E2/knapsack"]


# --- options ---------------------------------------------------------------------------------


def test_noise_model_parse_and_default():
    assert NoiseModel().is_default and CANDIDATES["M0"].is_default
    assert NoiseModel.parse(None).is_default and NoiseModel.parse("").is_default
    m = NoiseModel.parse("kernel=free,eps_max=1,q=strata")
    assert m == NoiseModel(kernel="free", eps_max=1.0, q="strata") == CANDIDATES["KEQ"]
    assert NoiseModel.parse("KEQ-h").eps == "member"
    with pytest.raises(ValueError):
        NoiseModel(kernel="gaussian")
    with pytest.raises(ValueError):
        NoiseModel.parse("rho=3")


# --- spaces ----------------------------------------------------------------------------------


def test_stirling_numbers():
    S = _stirling2(6)
    assert [S[6][b] for b in range(7)] == [0, 1, 31, 90, 65, 15, 1]
    assert sum(S[6]) == 203  # Bell(6)


@pytest.mark.parametrize("n", [4, 5])
def test_partition_strata_partition_the_space(n):
    space = PartitionSpace([f"v{i}" for i in range(n)], None)
    keys = all_partition_keys(space)
    sizes = Counter(space.q_stratum(k) for k in keys)
    for b, c in sizes.items():
        assert abs(math.exp(space.log_stratum_size(b)) - c) < 1e-9
    # the default q's mass per stratum
    d = space.default_strata()
    for b in range(1, n + 1):
        mass = sum(math.exp(space.log_q(k)) for k in keys if space.q_stratum(k) == b)
        assert abs(mass - d[b]) < 1e-12


def test_bit_strata_and_default():
    space = BitSpace(_SubsetCodec(list("ABCDE")))
    keys = all_bit_keys(space)
    d = space.default_strata()
    for k in range(6):
        ks = [y for y in keys if space.q_stratum(y) == k]
        assert abs(math.exp(space.log_stratum_size(k)) - len(ks)) < 1e-9
        assert abs(sum(math.exp(space.log_q(y)) for y in ks) - d[k]) < 1e-12


def test_partition_sampler_is_uniform_within_a_stratum():
    rng = np.random.default_rng(0)
    n, b = 5, 3
    draws = Counter(tuple(sample_partition_rgs(n, b, rng)) for _ in range(25000))
    assert len(draws) == 25  # S(5, 3)
    freqs = np.array(list(draws.values())) / 25000
    assert np.abs(freqs - 1 / 25).max() < 0.012
    space = PartitionSpace([f"v{i}" for i in range(6)], None)
    assert all(space.q_stratum(space.sample_stratum(4, rng)) == 4 for _ in range(50))


@pytest.mark.parametrize("codec,specials", [(_SatCodec([f"x{i}" for i in range(1, 6)]), ("UNSAT",)),
                                            (_SubsetCodec(list("ABCDEF")), ())])
def test_adds_drops_kernel_is_a_pmf(codec, specials):
    space = BitSpace(codec, specials)
    keys = all_bit_keys(space) + list(specials)
    rng = np.random.default_rng(1)
    g = rng.random(len(AD_CELLS))
    g[0] = 0.0
    g /= g.sum()
    for a in keys[:4] + keys[len(keys) - len(specials) - 3: len(keys) - len(specials)]:
        total = sum(float(space.slip_ad(y, a)[1] @ g) for y in keys)
        assert abs(total - 1) < 1e-9, (a, total)
    # a set member's coefficients are the average over its solutions
    S = space.set_array(keys[3:9])
    for y in keys[:6]:
        avg = np.mean([space.slip_ad(y, s)[1] for s in keys[3:9]], 0)
        assert np.allclose(space.slip_set_ad(y, S), avg)


def test_adds_drops_sampler_matches_pmf():
    space = BitSpace(_SubsetCodec(list("ABCDE")))
    keys = all_bit_keys(space)
    g = np.zeros(len(AD_CELLS))
    g[AD_CELLS.index((1, 1))] = 0.6
    g[AD_CELLS.index((0, 1))] = 0.3
    g[AD_CELLS.index((2, 0))] = 0.1
    a = space.encode(np.array([True, True, False, False, False]))
    rng = np.random.default_rng(2)
    draws = Counter(space.sample_slip_ad(a, g, rng) for _ in range(20000))
    tv = 0.5 * sum(abs(draws.get(y, 0) / 20000 - float(space.slip_ad(y, a)[1] @ g)) for y in keys)
    assert tv < 0.03
    assert space.slip_ad(space.encode(np.array([True, False, True, False, False])), a)[1][AD_CELLS.index((1, 1))] == \
        pytest.approx(1 / (3 * 2))  # one of 3 clear positions set, one of 2 set positions cleared


def test_free_kernel_sampler_matches_pmf():
    space = PartitionSpace([f"v{i}" for i in range(5)], None)
    keys = all_partition_keys(space)
    g = np.array([0.0, 0.1, 0.7, 0.2, 0.0, 0.0, 0.0])
    a = keys[17]
    rng = np.random.default_rng(3)
    draws = Counter(space.sample_slip_g(a, g, rng) for _ in range(30000))

    def pmf(y):
        b0, c = space.slip(y, a)
        return b0 + float(c @ g)

    assert abs(sum(pmf(y) for y in keys) - 1) < 1e-9
    tv = 0.5 * sum(abs(draws.get(y, 0) / 30000 - pmf(y)) for y in keys)
    assert tv < 0.03


def test_default_kernel_over_adds_drops_cells_is_the_geometric_by_distance():
    g = default_kernel("adds-drops", 0.4)
    d = trunc_geom(0.4)
    for dist in range(1, DMAX + 1):
        assert abs(sum(g[j] for j, (a, r) in enumerate(AD_CELLS) if a + r == dist) - d[dist]) < 1e-12


# --- likelihood and EM -----------------------------------------------------------------------


def test_default_rows_and_fit_are_unchanged(knapsack_unit):
    """A UnitModel without a noise model is the pre-registered one, and the general EM run on its tensors
    reproduces the default EM."""
    um = UnitModel(knapsack_unit)
    assert um.noise.is_default
    rng = np.random.default_rng(4)
    labels = [c.members[0] for c in um.columns if um.pred(0, c.members[0]).kind == "det"][:3]
    obs = plant(um, dict(zip(labels, (0.6, 0.3, 0.1))), eps=0.2, rho=0.4, rng=rng, q=0.05, reps=3)
    T = um.tensors(obs)
    assert T.noise.is_default and T.qs is None and T.C.shape[2] == DMAX + 1
    a, b = em(T), em_general(T)
    assert np.abs(a.pi - b.pi).max() < 1e-6 and abs(a.eps[0] - b.eps[0]) < 1e-6 and a.rho[0] == b.rho[0]


def test_strata_q_is_a_pmf_at_any_parameters():
    """q(y) from the tensors' strata data sums to 1 over every answer, for arbitrary stratum probabilities and tau."""
    from reasoning_heuristics.identify.mixture import _GeneralStepper

    items = load_items(ROOT / "data/items/smoke/AH_E5_smoke_s1.jsonl.gz")
    unit = make_units(items)["AH_E5/ENT"]  # literal sets over 8 literals, and the special token X
    um = UnitModel(unit, noise=NoiseModel(q="strata"))
    i = 0
    space = um.items[i].space
    assert space.n <= 10 and space.specials
    keys = all_bit_keys(space) + list(space.specials)
    obs = [Observation(i, y) for y in keys]
    T = um.tensors(obs)
    step = _GeneralStepper(T, np.ones((1, T.n)), None)
    st = step.init(1, None, 0.1)
    rng = np.random.default_rng(5)
    st["P"] = rng.random(st["P"].shape)
    grp = T.qs.group
    for gi in set(grp.tolist()):
        st["P"][0, grp == gi] /= st["P"][0, grp == gi].sum()
    st["tau"] = np.array([0.3 if T.qs.tau_free else 0.0])
    Q = step.q_rows(st)[0] * np.exp(T.log_scale)
    assert abs(Q.sum() - 1) < 1e-9


def test_always_token_member_sets_tau_to_zero():
    """With a member that answers UNSAT on every item, tau would be a ridge with its weight: tau is 0."""
    items = load_items(ROOT / "data/items/dev/C_E2_dev_s1.jsonl.gz")
    unit = make_units(items)["C_E2/3-SAT"]
    um = UnitModel(unit, noise=NoiseModel(q="strata"))
    assert um.always_token_columns(), "C E2 SAT lists ALWAYS-UNSAT (A1 give-up)"
    rng = np.random.default_rng(6)
    obs = [Observation(i, um.sample_q(i, rng)) for i in range(len(um.items))]
    T = um.tensors(obs)
    assert not T.qs.tau_free and T.qs.tau0 == 0.0


def test_free_kernel_and_member_eps_are_recovered(knapsack_unit):
    """Planted: two members with slip rates 0.1 and 0.7, a kernel peaked at distance 2; the general EM finds both."""
    um = UnitModel(knapsack_unit, noise=NoiseModel(kernel="free", eps="member", eps_max=1.0))
    dets = [c.members[0] for c in um.columns if all(um.pred(i, c.members[0]).kind == "det" for i in range(len(um.items)))]
    h1, h2 = dets[0], dets[-1]
    g = np.array([0.0, 0.2, 0.6, 0.2, 0.0, 0.0, 0.0])
    prm = NoiseParams({h1: 0.1, h2: 0.7}, g)
    sc = Scenario("t", "mix", {h1: 0.5, h2: 0.5}, params=prm)
    rng = np.random.default_rng(7)
    obs = [o for _ in range(30) for o in simulate(um, sc, rng)]
    r = em(um.tensors(obs))
    eps = dict(zip(um.tensors(obs[:5]).labels, r.state["eps"][0]))
    col = {m: c.name for c in um.columns for m in c.members}
    assert abs(eps[col[h1]] - 0.1) < 0.05 and abs(eps[col[h2]] - 0.7) < 0.08
    assert np.abs(r.state["g"][0] - g).max() < 0.06


def test_strata_q_is_recovered_and_round_trips_through_noise_params(knapsack_unit):
    """Pure q data from a strata q (small packings only): the fit puts the weight on q and finds the strata."""
    nm = NoiseModel(q="strata")
    um = UnitModel(knapsack_unit, noise=nm)
    keys, group, p0 = um.strata_index()
    P = np.zeros(len(keys))
    for j, (_, n, size) in enumerate(keys):
        P[j] = {1: 0.5, 2: 0.5}.get(size, 0.0)
    state = {"eps": [0.1], "g": trunc_geom(0.3), "P": P, "tau": 0.0}
    prm = noise_params(state, nm, [c.members[0] for c in um.columns], keys)
    sc = Scenario("q", "null_q", {}, q=1.0, params=prm)
    rng = np.random.default_rng(8)
    obs = [o for _ in range(10) for o in simulate(um, sc, rng)]
    assert {um.items[o.item].space.q_stratum(o.key) for o in obs} <= {1, 2}
    r = fit(um.tensors(obs), n_boot=0)
    assert r.pi[-1] > 0.9
    Pf = np.array(r.extra["state"]["P"])
    assert abs(Pf[[j for j, k in enumerate(keys) if k[2] == 1]].sum() - 0.5) < 0.1


def test_general_fit_bootstrap_and_jackknife(knapsack_unit):
    um = UnitModel(knapsack_unit, noise=CANDIDATES["KEQ"])
    rng = np.random.default_rng(9)
    labels = [c.members[0] for c in um.columns if um.pred(0, c.members[0]).kind == "det"][:2]
    obs = plant(um, dict(zip(labels, (0.7, 0.3))), eps=0.2, rho=0.4, rng=rng, reps=2)
    res = fit(um.tensors(obs), n_boot=30, rng=rng, jackknife=True)
    assert res.boot.shape == (30, len(res.labels)) and res.jack is not None
    assert (res.lo <= res.pi + 1e-9).all() and (res.pi <= res.hi + 1e-9).all()
    assert set(res.extra["state"]) >= {"pi", "eps", "g", "P", "tau"} and "state_ci" in res.extra
    assert np.isnan(res.rho)  # a free kernel has no rho


def test_swap_kernel_needs_a_bit_space():
    items = load_items(ROOT / "data/items/smoke/C_E2_smoke_s1.jsonl.gz")
    with pytest.raises(ValueError):
        UnitModel(make_units(items)["C_E2/colouring"], noise=NoiseModel(kernel="swap"))


def test_permutation_and_recovery_paths_use_the_units_noise_model():
    """em() on tensors that carry a non-default noise model takes the general path (state is returned)."""
    rng = np.random.default_rng(10)
    um = UnitModel(Unit("T_E0", "SAT", patterned_items(200, rng)), noise=NoiseModel(eps="member"))
    obs = plant(um, {"B": 0.6, "C": 0.4}, eps=0.0, rho=0.3, rng=rng)
    r = em(um.tensors(obs))
    assert r.state is not None and r.eps[0] == 0.0  # finite channel: eps held at 0
