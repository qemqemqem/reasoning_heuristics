"""Member predictions, likelihood rows, ties, exclusions and censoring."""

import math
from pathlib import Path

import numpy as np
import pytest
from identify_helpers import decision_item, plant

from reasoning_heuristics.identify.likelihood import NEAR_MISS, UNIFORM, Observation, TruncationTable, UnitModel
from reasoning_heuristics.identify.members import log_count_colourings
from reasoning_heuristics.identify.mixture import fit
from reasoning_heuristics.identify.records import Response
from reasoning_heuristics.identify.units import Unit, load_items, make_units

ROOT = Path(__file__).resolve().parents[1]
SMOKE = sorted((ROOT / "data/items/smoke").glob("*.jsonl.gz"))


def unit_of(items):
    return Unit("T_E0", "SAT", items)


@pytest.fixture(scope="module")
def smoke_units():
    return make_units(load_items(SMOKE))


def test_every_smoke_unit_builds_and_samples(smoke_units):
    """Every member's prediction is interpretable, and every answer a member can produce has positive
    likelihood under that member (both slip models)."""
    rng = np.random.default_rng(0)
    assert smoke_units and not any("E8" in name for name in smoke_units)
    for name, unit in smoke_units.items():
        for model in (NEAR_MISS, UNIFORM):
            um = UnitModel(unit, model)
            for i in range(len(unit.items)):
                for g in um.columns:
                    if not um.pred(i, g.members[0]).available:
                        continue
                    y = um.sample(i, g.members[0], 0.3, 0.4, rng)
                    assert um.items[i].space.valid(y), (name, g.name, y)
                    A, B0, C, Q, avail = um.row(i, y)
                    j = um.columns.index(g)
                    assert avail[j] and (A[j] > 0 or B0[j] > 0 or C[j].any()), (name, g.name, y)


def test_solution_sets_rebuilt_by_validity():
    items = load_items(ROOT / "data/items/dev/C_E1_dev_s1.jsonl.gz")
    units = make_units(items)
    for name, field in (("C_E1/colouring", "n_optimal_partitions"), ("C_E1/3-SAT", "n_solutions")):
        um = UnitModel(units[name])
        for i, it in enumerate(um.unit.items[:6]):
            p = um.pred(i, "EXACT")
            assert p.kind == "set" and p.sol.size == it["ground_truth"][field]
    um = UnitModel(units["C_E1/colouring"])
    space = um.items[0].space
    chi = um.unit.items[0]["ground_truth"]["chromatic_number"]
    for key in um.pred(0, "EXACT").sol.keys()[:50]:
        assert int(space.parse(key).max()) + 1 == chi


def test_colouring_counter_matches_brute_force():
    import itertools

    rng = np.random.default_rng(3)
    V = [f"v{i}" for i in range(6)]
    E = [(V[i], V[j]) for i in range(6) for j in range(i + 1, 6) if rng.random() < 0.4]
    for k in (2, 3):
        brute = sum(1 for c in itertools.product(range(k), repeat=6) if all(c[int(u[1:])] != c[int(v[1:])] for u, v in E))
        got = log_count_colourings(V, E, k)
        assert (brute == 0 and got == -math.inf) or abs(math.exp(got) - brute) < 1e-6


def test_rows_for_a_deterministic_member():
    items = [decision_item(0, {"A": "SAT", "B": "UNSAT"})]
    um = UnitModel(unit_of(items), NEAR_MISS)
    cols = [g.name for g in um.columns]
    A, B0, C, Q, avail = um.row(0, "SAT")
    assert A[cols.index("A = EXACT")] == 1 and B0[cols.index("A = EXACT")] == 0 and B0[cols.index("B")] == 1
    assert Q == 0.5 and avail.all()


def test_uniform_candidate_slip_is_normalised():
    items = load_items(ROOT / "data/items/dev/C_E2_dev_s1.jsonl.gz")
    unit = make_units(items)["C_E2/knapsack"]
    um = UnitModel(unit, UNIFORM)
    im = um.items[0]
    a = im.candidates[0]
    on_cands = sum(um._candidate_slip(im, c, a) for c in im.candidates)
    K = len(im.candidates) - 1 + 1
    # the non-candidates share 1/K in proportion to q
    assert abs(on_cands + 1.0 / K - 1) < 1e-12


def test_ties_are_merged_and_random_is_folded_into_q():
    items = [decision_item(i, {"A": "SAT", "A2": "SAT", "B": "UNSAT" if i % 2 else "SAT"},
                           dists={"RANDOM": {"SAT": 0.5, "UNSAT": 0.5}}) for i in range(6)]
    um = UnitModel(unit_of(items))
    names = [g.name for g in um.columns]
    assert "A = A2 = EXACT" in names and "B" in names
    assert um.q_members == ["RANDOM"]
    assert UnitModel(unit_of(items), merge_ties=False).columns[0].name == "A"


def test_exclusions_declared_impossible_and_censoring():
    items = [decision_item(i, {"A": "SAT", "B": "UNSAT"}, cell=f"c{i % 2}") for i in range(4)]
    um = UnitModel(unit_of(items))
    rs = [Response("T-0", "h0", "m", "ok", answer="SAT"),
          Response("T-1", "h1", "m", "declared_impossible"),
          Response("T-2", "h2", "m", "parse_fail"),
          Response("T-3", "h3", "m", "truncated", reasoning_tokens=32000),
          Response("T-0", "h0", "m", "refusal")]
    obs, exc = um.observations(rs)
    assert [o.key for o in obs] == ["SAT"]  # give-ups are not answers by default
    assert exc.counts["c0"] == {"parse_fail": 1, "refusal": 1}
    assert exc.counts["c1"] == {"truncated": 1, "declared_impossible": 1}
    assert abs(exc.rates()["c1"]["truncated"] - 0.5) < 1e-12
    obs2, _ = um.observations(rs, declared_impossible="as-token")
    assert [o.key for o in obs2] == ["SAT", "UNSAT"]  # the sensitivity option reads them as UNSAT
    tm = TruncationTable({("T-3", "A"): 0.8, ("T-3", "B"): 0.1}, default=0.2)
    obs3, exc3 = um.observations(rs, token_model=tm)
    assert obs3[-1].censored and "truncated" not in exc3.counts["c1"]
    T = um.tensors(obs3, tm)
    cols = T.labels
    row = T.A[-1] * np.exp(T.log_scale[-1])
    assert abs(row[cols.index("A = EXACT")] - 0.8) < 1e-12 and abs(row[cols.index("B")] - 0.1) < 1e-12
    with pytest.raises(ValueError):
        um.observations([Response("T-0", "WRONG", "m", "ok", answer="SAT")])


def test_off_channel_answers_are_counted():
    items = load_items(ROOT / "data/items/smoke/C_E3_smoke_s1.jsonl.gz")
    unit = make_units(items)["C_E3/colouring (gadget)"]
    um = UnitModel(unit)
    it = [x for x in unit.items if x["extra"]["channel"] == "target-colour"][0]
    obs, exc = um.observations([Response(it["item_id"], it["content_hash"], "m", "ok", answer="IMPOSSIBLE")])
    assert not obs and exc.counts[it["cell"]]["off_channel"] == 1


def test_planted_member_has_the_highest_likelihood_on_its_own_answers(smoke_units):
    rng = np.random.default_rng(5)
    unit = smoke_units["C_E2/colouring"]
    um = UnitModel(unit, NEAR_MISS)
    g = next(c for c in um.columns if all(um.pred(i, c.members[0]).kind == "det" for i in range(len(unit.items))))
    obs = plant(um, {g.members[0]: 1.0}, eps=0.0, rho=0.3, rng=rng)
    T = um.tensors(obs)
    j = T.labels.index(g.name)
    for n in range(T.n):
        assert T.A[n, j] == T.A[n].max()


def test_special_token_predictions_do_not_slip():
    """A deterministic prediction of a special token (UNSAT, IMPOSSIBLE, X) has no near misses, so it
    does not slip: P(token | h) = 1 at any eps, under both slip models. If it slipped to "q without the
    token", a member that predicts the token on every item (ALWAYS-UNSAT) would equal q at
    eps = 1 - q(token) = 0.5 (one special token: the eps cap), and pure noise would load on it."""
    unit = make_units(load_items(ROOT / "data/items/dev/C_E5_dev_s1.jsonl.gz"))["C_E5/3-SAT (partial assignment given)"]
    rng = np.random.default_rng(0)
    au = "ALWAYS-UNSAT (A1 give-up)"
    for model in (NEAR_MISS, UNIFORM):
        um = UnitModel(unit, model)
        j = [g.name for g in um.columns].index(au)
        for i in range(len(um.items)):
            assert um.sample(i, au, 0.5, 0.3, rng) == "UNSAT"
            A, B0, C, _, _ = um.row(i, "UNSAT")
            assert A[j] == B0[j] == 1 and not C[j].any()
            A, B0, C, _, _ = um.row(i, um.items[i].space.sample_uniform(rng))
            assert A[j] == B0[j] == 0 and not C[j].any()
    # pure noise keeps its weight on q (with slips, ALWAYS-UNSAT took 0.36-0.41 of it on the C E5 pc20 set)
    um = UnitModel(unit, NEAR_MISS)
    T = um.tensors([Observation(i, um.sample_q(i, rng)) for i in range(len(um.items)) for _ in range(20)])
    assert not T.slips[T.labels.index(au)]
    res = fit(T, n_boot=0)
    assert res.weight(au) < 0.1 and res.pi[-1] > 0.85, dict(zip(res.labels, res.pi.round(3)))
