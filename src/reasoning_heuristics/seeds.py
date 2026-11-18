"""Run tiers, splits and seed ranges.

SCOPE §2: smoke = 1 item per design cell, dev = 5-10 per cell, and dev and test
items come from disjoint seeds. The ranges follow the verticals (C §2.8, A/H §2.8):
dev bases draw seeds from [0, 10^6), test bases from [10^6, 2*10^6). Smoke is a
separate sub-range of the dev split so smoke items are never re-used as dev items.

A base's seed is derived from (tier, user seed, base attempt) and stored on every
item derived from that base, so any item can be regenerated from its record.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Tier:
    name: str
    split: str
    seed_lo: int
    seed_hi: int
    default_per_cell: int


TIERS: dict[str, Tier] = {
    "smoke": Tier("smoke", "dev", 0, 100_000, 1),
    "dev": Tier("dev", "dev", 100_000, 1_000_000, 5),
    "test": Tier("test", "test", 1_000_000, 2_000_000, 50),
}

SPLIT_RANGES = {"dev": (0, 1_000_000), "test": (1_000_000, 2_000_000)}


def base_seed(tier: str, user_seed: int, attempt: int) -> int:
    """Deterministic seed of the attempt-th candidate base for this tier and user seed."""
    t = TIERS[tier]
    width = t.seed_hi - t.seed_lo
    value = t.seed_lo + (user_seed * 7919 * 104_729 + attempt * 7_919) % width
    assert t.seed_lo <= value < t.seed_hi
    return value


SALT_BYTES = 8

# (seed, salt key) -> the first salt that used it, for every stream handed out in this process.
_STREAM_OWNERS: dict[tuple[int, int], str] = {}


def rng_for(seed: int, salt: str) -> np.random.Generator:
    """A numpy Generator keyed on (seed, salt): different evals never share streams.

    Only the first SALT_BYTES (8) UTF-8 bytes of the salt key the stream: "AH-E1-SAT-critical",
    "AH-E1-SAT-null" and "AH-E1-SAT-B1" all key "AH-E1-SA". The truncation stays, so existing
    items regenerate identically. What it must never do is hand two different salts the same
    stream, so asking for a seed with a salt that agrees with an earlier one in its first 8 bytes
    raises AssertionError. Salts that differ only after byte 8 are therefore usable only with
    different seeds (A/H E1's kinds each draw their own base seeds). Give a new salt its own
    8-byte prefix.
    """
    salt_int = int.from_bytes(salt.encode("utf-8")[:SALT_BYTES].ljust(SALT_BYTES, b"\0"), "little")
    owner = _STREAM_OWNERS.setdefault((seed, salt_int), salt)
    if owner != salt:
        raise AssertionError(f"rng_for: salts {owner!r} and {salt!r} agree in their first {SALT_BYTES} bytes, "
                             f"so with seed {seed} they would share one random stream")
    return np.random.default_rng([seed, salt_int])


def split_of_seed(seed: int) -> str:
    for split, (lo, hi) in SPLIT_RANGES.items():
        if lo <= seed < hi:
            return split
    raise ValueError(f"seed {seed} is outside every split range")
