"""Monte-Carlo estimates for the distributional members (C §1.2: "estimated from 10⁴
Monte-Carlo runs with add-ε smoothing").

A member draws `samples` random orders with `random_orders`, counts the outcome of each run,
and returns `smoothed(counts, eps)`: every observed outcome is kept (no truncation), and one
`_other` class stands for all outcomes no run produced:

    P(o) = (n_o + ε) / (N + ε·(K + 1))   for each of the K observed outcomes,
    P(_other) = ε / (N + ε·(K + 1)),

which sums to 1. ε = ½ (the Krichevsky–Trofimov estimator) unless the member is given
another `smoothing_eps`; the C doc names no value.
"""

from __future__ import annotations

import numpy as np

SAMPLES = 10_000
SMOOTHING_EPS = 0.5


def random_orders(rng: np.random.Generator, n: int, samples: int) -> np.ndarray:
    """`samples` uniformly random permutations of range(n), one per row (int array)."""
    return rng.permuted(np.tile(np.arange(n), (samples, 1)), axis=1)


def smoothed(counts: dict[str, int], eps: float = SMOOTHING_EPS) -> dict[str, float]:
    """Add-ε smoothing over the observed outcomes plus `_other`; ordered by count, then key."""
    total = sum(counts.values())
    denom = total + eps * (len(counts) + 1)
    dist = {k: (c + eps) / denom for k, c in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))}
    dist["_other"] = eps / denom
    return dist
