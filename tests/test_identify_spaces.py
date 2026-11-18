"""Answer spaces: the near-miss kernels and q are probability mass functions over the space,
and the samplers draw from them."""

import itertools
import math
from collections import Counter

import numpy as np
import pytest

from reasoning_heuristics.identify.spaces import (DMAX, BitSpace, FiniteSpace, PartitionSpace, _SatCodec, _SubsetCodec,
                                                  trunc_geom)


def all_partition_keys(space: PartitionSpace) -> list[str]:
    keys = set()
    n = space.n
    for colours in itertools.product(range(n), repeat=n):
        keys.add(space.encode(space.canon(np.array(colours))))
    return sorted(keys)


def slip_prob(space, y, a, rho):
    b0, c = space.slip(y, a)
    return b0 + float(c @ trunc_geom(rho))


def test_trunc_geom_normalised():
    for rho in (0.02, 0.3, 0.7):
        g = trunc_geom(rho)
        assert g[0] == 0 and abs(g.sum() - 1) < 1e-12
    assert trunc_geom(np.array([0.1, 0.5])).shape == (2, DMAX + 1)


@pytest.mark.parametrize("n,k,specials", [(4, None, ()), (5, 3, ("IMPOSSIBLE",)), (6, None, ())])
def test_partition_kernels_are_pmfs(n, k, specials):
    space = PartitionSpace([f"v{i}" for i in range(n)], k, specials)
    keys = all_partition_keys(space) + list(specials)
    assert len(keys) - len(specials) == round(math.exp(space.log_size())) - len(specials)  # Bell(n)
    assert abs(sum(math.exp(space.log_q(y)) for y in keys) - 1) < 1e-9
    assert abs(sum(math.exp(space.log_uniform(y)) for y in keys) - 1) < 1e-9
    rng = np.random.default_rng(0)
    for a in rng.choice(keys[: len(keys) - len(specials)], size=4, replace=False):
        for rho in (0.1, 0.6):
            total = sum(slip_prob(space, y, a, rho) for y in keys)
            assert abs(total - 1) < 1e-9, (a, rho, total)
            assert slip_prob(space, a, a, rho) >= 0
    for s in specials:  # a special token has no near misses
        with pytest.raises(ValueError):
            space.slip(keys[0], s)
        with pytest.raises(ValueError):
            space.sample_slip(s, 0.3, rng)


@pytest.mark.parametrize("codec,specials", [(_SatCodec([f"x{i}" for i in range(1, 6)]), ("UNSAT",)),
                                            (_SubsetCodec(list("ABCDEFGH")), ())])
def test_bit_kernels_are_pmfs(codec, specials):
    space = BitSpace(codec, specials)
    keys = [space.encode(np.array(bits, dtype=bool)) for bits in itertools.product((False, True), repeat=space.n)]
    keys += list(specials)
    assert abs(sum(math.exp(space.log_q(y)) for y in keys) - 1) < 1e-9
    structured = keys[: len(keys) - len(specials)]
    for a in structured[:5] + structured[-3:]:
        for rho in (0.05, 0.5):
            assert abs(sum(slip_prob(space, y, a, rho) for y in keys) - 1) < 1e-9
    for s in specials:
        with pytest.raises(ValueError):
            space.slip(keys[0], s)


def test_finite_space():
    space = FiniteSpace(["SAT", "UNSAT"], lambda a: a)
    assert slip_prob(space, "UNSAT", "SAT", 0.3) == 1.0 and slip_prob(space, "SAT", "SAT", 0.3) == 0.0
    space3 = FiniteSpace(list("ABCDE"), lambda a: a)
    assert abs(sum(slip_prob(space3, y, "C", 0.3) for y in "ABCDE") - 1) < 1e-12
    assert abs(sum(math.exp(space3.log_q(y)) for y in "ABCDE") - 1) < 1e-12


def test_slip_set_is_the_average_over_the_set():
    space = PartitionSpace([f"v{i}" for i in range(6)], None)
    keys = all_partition_keys(space)
    rng = np.random.default_rng(1)
    S = list(rng.choice(keys, size=7, replace=False))
    arr = space.set_array(S)
    g = trunc_geom(0.4)
    for y in rng.choice(keys, size=10):
        avg = np.mean([slip_prob(space, y, s, 0.4) for s in S])
        assert abs(float(space.slip_set(y, arr) @ g) - avg) < 1e-12


def test_near_miss_sampler_matches_pmf():
    space = PartitionSpace([f"v{i}" for i in range(5)], None)
    keys = all_partition_keys(space)
    a = keys[17]
    rng = np.random.default_rng(2)
    draws = Counter(space.sample_slip(a, 0.4, rng) for _ in range(30000))
    tv = 0.5 * sum(abs(draws.get(y, 0) / 30000 - slip_prob(space, y, a, 0.4)) for y in keys)
    assert tv < 0.03
    bits = BitSpace(_SatCodec(["x1", "x2", "x3", "x4"]), ("UNSAT",))
    a = bits.encode(np.array([True, False, True, False]))
    draws = Counter(bits.sample_slip(a, 0.5, rng) for _ in range(20000))
    allk = [bits.encode(np.array(b, dtype=bool)) for b in itertools.product((False, True), repeat=4)] + ["UNSAT"]
    tv = 0.5 * sum(abs(draws.get(y, 0) / 20000 - slip_prob(bits, y, a, 0.5)) for y in allk)
    assert tv < 0.03


def test_partition_distance_and_keys():
    space = PartitionSpace(["a", "b", "c", "d"], 3, ("IMPOSSIBLE",))
    x = space.key({"a": 1, "b": 1, "c": 2, "d": 3})
    y = space.key({"a": 2, "b": 2, "c": 1, "d": 3})  # same partition, colours renamed
    assert x == y and space.distance(x, y) == 0
    z = space.key({"a": 1, "b": 2, "c": 2, "d": 3})
    assert space.distance(x, z) == 1
    assert space.valid("IMPOSSIBLE") and not space.valid("a,b|c")  # d missing
    assert space.log_uniform(space.key({"a": 1, "b": 2, "c": 3, "d": 4})) == -math.inf  # 4 colours > k
    assert space.log_q(space.key({"a": 1, "b": 2, "c": 3, "d": 4})) > -math.inf  # q covers every partition
