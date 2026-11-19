"""Answer spaces: what a response can be on an item's scoring channel, the distance between two
answers, the near-miss slip kernel, and the reference ("none of the above") distribution q.

Every answer is handled as its canonical **key**, the string `heuristics.answers.answer_key`
gives (or the generator's channel key: a decision, a target bit, an option letter). The key
functions here mirror the generators' channels (`generators/common.py`, `c_e3.py`), so a
response and a member that give the same answer get the same key.

Spaces
------
- `FiniteSpace`: decisions (SAT/UNSAT, POSSIBLE/IMPOSSIBLE, YES/NO), MC option letters,
  C E3's target bit and target colour. A slip is any other value, uniformly (for two values, a
  flip). q is uniform over the values. **C E3's bit channel is {same, different, IMPOSSIBLE}**, with
  q uniform over the three: the U-arm format admits IMPOSSIBLE and FF-OUT and LF predict it (on
  every U-REV item), so it is a point prediction here. The items' stored outcome classes and the
  scorer's `outcome_class` lump IMPOSSIBLE with "other" on that channel.
- `BitSpace`: SAT assignments (Hamming distance = variables flipped), knapsack item sets and
  A/H E5's "what follows" literal sets (symmetric difference), plus special tokens (UNSAT; X).
- `PartitionSpace`: colourings, compared up to renaming of colours, plus IMPOSSIBLE on
  k-colour tasks. The distance is the number of vertices recoloured.

The near-miss slip kernel (normalised over the answer space)
------------------------------------------------------------
A slip from an intended structured answer a: draw D ~ truncated geometric on {1..DMAX},
P(D = d) = g_d(rho) = (1-rho) rho^(d-1) / (1 - rho^DMAX) (D is capped at n); pick D distinct
positions uniformly; give each a uniformly random *different* value. For assignments and item
sets that is P(y | a) = g_d / C(n, d) at Hamming distance d. For colourings the value set is the
palette of a's colours plus one new colour (C = b_a + 1), and the observed answer is a partition,
so P(y | a) sums over every injective colour naming of y's blocks:
P(y | a) = sum_sigma g_{d(sigma)} / (C(n, d) (C - 1)^d), d(sigma) = vertices whose colour differs.
These are exact probability mass functions over the space (tests check that they sum to 1). A
special token (UNSAT, IMPOSSIBLE, X) has no near misses: the kernels refuse one as the intended
answer, and the likelihood does not slip predictions of one (`likelihood.py`). Slips from
structured answers stay structured.

`slip(y, a)` returns (b0, c) with P_slip(y | a; rho) = b0 + sum_d c[d] g_d(rho): the rho-free part
and the coefficients of g, so the slip shape rho can be estimated without recomputing kernels.

The reference distribution q
----------------------------
q(y | x): with probability tau = s/(1+s) (s = number of special tokens) a uniformly chosen special
token, otherwise a uniformly random structured answer (assignments and sets: uniform over 2^n;
colourings: a uniformly random colour vector with n colours, read as a partition, so q gives
every partition positive mass). On finite spaces q is uniform. The `RANDOM (H)` member's
"uniform over k^n colourings" is `log_uniform` (palette k, or n on fewest-colour tasks, where it
coincides with q's structured part).

Options of the noise model (`noise.py`; the defaults above are unchanged)
-------------------------------------------------------------------------
- **Size strata** (`q="strata"`): `q_stratum` gives an answer's stratum (colour blocks of a
  partition, set positions of a bit vector), `log_stratum_size` how many answers share it (a
  Stirling number of the second kind, or a binomial coefficient), `default_strata` the default
  q's mass on each stratum, and `sample_stratum` a uniform answer from one.
- **Free kernels** (`kernel="free"`): the same distance cells as the geometric kernel, so `slip`
  serves; `sample_slip_g` draws D from a given kernel vector g instead of g(rho).
- **Adds and drops** (`kernel="swap"`, bit spaces): `slip_ad`, `slip_set_ad` and `sample_slip_ad`
  are the kernel over the (adds, drops) cells `AD_CELLS`: a slip draws a cell, then that many
  positions to set among a's clear ones and to clear among its set ones, uniformly (a cell asking
  for more than there are is clipped, as D is clipped at n), so P(y | a) = sum over the cells that
  clip to y's (adds, drops) of g_cell / (C(n - k, adds) C(k, drops)), k = |a|. A one-for-one swap
  is the cell (1, 1).
"""

from __future__ import annotations

import ast
import itertools
import math
from functools import lru_cache
from typing import Any, Callable

import numpy as np

from reasoning_heuristics.heuristics.answers import assignment_key, colouring_key

DMAX = 6  # largest number of positions one slip changes (rho = 0.3 leaves 0.07% of mass beyond it)

DECISION_VALUES = {"sat_task": ("SAT", "UNSAT"), "coloring_task": ("POSSIBLE", "IMPOSSIBLE"),
                   "entailment_task": ("YES", "NO")}


def trunc_geom(rho: Any, dmax: int = DMAX) -> np.ndarray:
    """g[..., d] = P(D = d) for d = 0..dmax (g[..., 0] = 0), truncated geometric with parameter rho."""
    rho = np.asarray(rho, dtype=float)
    d = np.arange(dmax + 1)
    g = (1 - rho[..., None]) * rho[..., None] ** np.maximum(d - 1, 0)
    g = g / (1 - rho[..., None] ** dmax)
    g[..., 0] = 0.0
    return g


def sample_d(rho: float, rng: np.random.Generator, dmax: int = DMAX) -> int:
    g = trunc_geom(rho, dmax)
    return int(rng.choice(dmax + 1, p=g / g.sum()))


@lru_cache(maxsize=None)
def _perms(C: int, b: int) -> np.ndarray:
    """All injective maps {0..b-1} -> {0..C-1}, as rows."""
    return np.array(list(itertools.permutations(range(C), b)), dtype=np.int64).reshape(-1, b)


@lru_cache(maxsize=None)
def _log_bell(n: int) -> float:
    row = [1]
    for _ in range(n - 1):
        new = [row[-1]]
        for x in row:
            new.append(new[-1] + x)
        row = new
    return math.log(row[-1]) if n > 0 else 0.0


# (adds, drops) cells of the swap kernel; index 0 is unused, as d = 0 is in the distance kernel
AD_CELLS: tuple[tuple[int, int], ...] = ((0, 0),) + tuple((a, r) for a in range(DMAX + 1) for r in range(DMAX + 1)
                                                         if 0 < a + r <= DMAX)


@lru_cache(maxsize=None)
def _stirling2(n: int) -> tuple[tuple[int, ...], ...]:
    """S[m][j]: partitions of m elements into j blocks, exact, for m, j = 0..n."""
    S = [[0] * (n + 1) for _ in range(n + 1)]
    S[0][0] = 1
    for m in range(1, n + 1):
        for j in range(1, m + 1):
            S[m][j] = S[m - 1][j - 1] + j * S[m - 1][j]
    return tuple(tuple(r) for r in S)


def _log_int(x: int) -> float:
    return math.log(x) if x < 2 ** 1000 else math.log(x >> 900) + 900 * math.log(2)


def sample_partition_rgs(n: int, b: int, rng: np.random.Generator) -> np.ndarray:
    """A uniformly random partition of n elements into exactly b blocks, as a restricted-growth string.

    Element m is a singleton with probability S(m-1, b-1) / S(m, b), else it joins one of the b blocks
    of a partition of the first m-1 (S(m, b) = S(m-1, b-1) + b S(m-1, b)); the choices are drawn from
    m = n down, then the blocks are built from m = 1 up."""
    if not 1 <= b <= n:
        raise ValueError(f"no partition of {n} elements into {b} blocks")
    S = _stirling2(n)
    steps = []
    j = b
    for m in range(n, 0, -1):
        single = j >= 1 and (S[m - 1][j - 1] == S[m][j] or rng.random() < S[m - 1][j - 1] / S[m][j])
        steps.append(single)
        j -= single
    out = np.empty(n, dtype=np.int64)
    blocks = 0
    for m, single in enumerate(reversed(steps)):
        if single:
            out[m] = blocks
            blocks += 1
        else:
            out[m] = int(rng.integers(blocks))
    return PartitionSpace.canon(out)


class Space:
    """Base class. Subclasses define keys, q, the uniform member, slips and sampling."""

    kind = "space"
    specials: tuple[str, ...] = ()

    # --- keys -------------------------------------------------------------------------------
    def key(self, answer: Any) -> str | None:  # pragma: no cover - abstract
        raise NotImplementedError

    def valid(self, key: str | None) -> bool:  # pragma: no cover - abstract
        raise NotImplementedError

    def is_special(self, key: str) -> bool:
        return key in self.specials

    # --- distributions ----------------------------------------------------------------------
    def log_q(self, key: str) -> float:  # pragma: no cover - abstract
        raise NotImplementedError

    def log_uniform(self, key: str) -> float:  # pragma: no cover - abstract
        raise NotImplementedError

    def log_size(self) -> float:  # pragma: no cover - abstract
        raise NotImplementedError

    def slip(self, y: str, a: str) -> tuple[float, np.ndarray]:  # pragma: no cover - abstract
        raise NotImplementedError

    def slip_set(self, y: str, S: Any) -> np.ndarray:  # pragma: no cover - abstract
        raise NotImplementedError

    def distance(self, y: str, a: str) -> int:  # pragma: no cover - abstract
        raise NotImplementedError

    # --- sampling ---------------------------------------------------------------------------
    def sample_q(self, rng: np.random.Generator) -> str:  # pragma: no cover - abstract
        raise NotImplementedError

    def sample_uniform(self, rng: np.random.Generator) -> str:  # pragma: no cover - abstract
        raise NotImplementedError

    def sample_slip(self, a: str, rho: float, rng: np.random.Generator) -> str:  # pragma: no cover - abstract
        raise NotImplementedError

    def sample_uniform_slip(self, a: str, rng: np.random.Generator) -> str:
        """A slip to a uniformly random answer other than a (the coarse 'any other answer' slip)."""
        while True:
            y = self.sample_q(rng)
            if y != a:
                return y

    def signature(self) -> tuple:
        """Two items whose spaces have equal signatures accept the same answers (for permutation baselines)."""
        return (self.kind,)

    # --- noise-model options (noise.py) -----------------------------------------------------
    def q_stratum(self, key: str) -> int | None:
        """The size stratum of a structured answer (None for a special token or a finite space)."""
        return None

    def log_stratum_size(self, s: int) -> float:  # pragma: no cover - abstract
        raise NotImplementedError

    def default_strata(self) -> np.ndarray:  # pragma: no cover - abstract
        """The default q's mass on each stratum 0..n, given a structured answer."""
        raise NotImplementedError

    def sample_stratum(self, s: int, rng: np.random.Generator) -> str:  # pragma: no cover - abstract
        raise NotImplementedError

    def sample_slip_g(self, a: str, g: np.ndarray, rng: np.random.Generator) -> str:  # pragma: no cover - abstract
        """A near-miss slip with D drawn from the kernel vector g over distances 0..DMAX."""
        raise NotImplementedError

    def ball_fraction(self, r: int, palette: int | None = None) -> float:  # pragma: no cover - abstract
        """The share of the structured answers within distance r of a given one (an upper bound for partitions)."""
        raise NotImplementedError


def _no_special(space: Space, a: str) -> None:
    if a in space.specials:
        raise ValueError(f"special token {a!r} has no near misses; predictions of it do not slip")


def _tau(specials: tuple[str, ...]) -> float:
    s = len(specials)
    return s / (1 + s)


# =============================================================================================
# Finite spaces
# =============================================================================================


class FiniteSpace(Space):
    kind = "finite"

    def __init__(self, values: list[str], key_fn: Callable[[Any], str | None]):
        if len(set(values)) != len(values) or len(values) < 2:
            raise ValueError(f"finite space needs >= 2 distinct values, got {values}")
        self.values = list(values)
        self._key = key_fn
        self._set = set(values)
        self.dmax = 1

    def key(self, answer: Any) -> str | None:
        return self._key(answer)

    def valid(self, key: str | None) -> bool:
        return key in self._set

    def log_q(self, key: str) -> float:
        return -math.log(len(self.values)) if key in self._set else -math.inf

    def log_uniform(self, key: str) -> float:
        return self.log_q(key)

    def log_size(self) -> float:
        return math.log(len(self.values))

    def slip(self, y: str, a: str) -> tuple[float, np.ndarray]:
        b0 = 0.0 if y == a or y not in self._set else 1.0 / (len(self.values) - 1)
        return b0, np.zeros(DMAX + 1)

    def slip_set(self, y: str, S: Any) -> np.ndarray:
        raise TypeError("finite spaces have no set-valued members")

    def distance(self, y: str, a: str) -> int:
        return 0 if y == a else 1

    def sample_q(self, rng: np.random.Generator) -> str:
        return self.values[int(rng.integers(len(self.values)))]

    def sample_uniform(self, rng: np.random.Generator) -> str:
        return self.sample_q(rng)

    def sample_slip(self, a: str, rho: float, rng: np.random.Generator) -> str:
        others = [v for v in self.values if v != a]
        return others[int(rng.integers(len(others)))]

    def sample_slip_g(self, a: str, g: np.ndarray, rng: np.random.Generator) -> str:
        return self.sample_slip(a, 0.0, rng)

    def signature(self) -> tuple:
        return (self.kind, tuple(self.values))


# =============================================================================================
# Bit-vector spaces: assignments, item sets, literal sets
# =============================================================================================


class _SatCodec:
    def __init__(self, names: list[str]):
        self.names = list(names)
        self.pos = {v: i for i, v in enumerate(self.names)}

    def key(self, answer: Any) -> str | None:
        if answer is None:
            return None
        if isinstance(answer, str):
            return answer
        return assignment_key(answer)

    def parse(self, key: str) -> np.ndarray:
        vec = np.zeros(len(self.names), dtype=bool)
        seen = 0
        for kv in key.split(","):
            name, _, val = kv.partition("=")
            if name not in self.pos or val not in ("T", "F"):
                raise ValueError(f"not an assignment over this item's variables: {key[:60]!r}")
            vec[self.pos[name]] = val == "T"
            seen += 1
        if seen != len(self.names):
            raise ValueError(f"assignment covers {seen} of {len(self.names)} variables")
        return vec

    def encode(self, vec: np.ndarray) -> str:
        return assignment_key({n: bool(b) for n, b in zip(self.names, vec)})


class _SubsetCodec:
    def __init__(self, names: list[str]):
        self.names = list(names)
        self.pos = {v: i for i, v in enumerate(self.names)}

    def key(self, answer: Any) -> str | None:
        if answer is None:
            return None
        if isinstance(answer, str):
            return answer
        return ",".join(sorted(answer))

    def parse(self, key: str) -> np.ndarray:
        vec = np.zeros(len(self.names), dtype=bool)
        if key == "":
            return vec
        for name in key.split(","):
            if name not in self.pos or vec[self.pos[name]]:
                raise ValueError(f"not a set of this item's elements: {key[:60]!r}")
            vec[self.pos[name]] = True
        return vec

    def encode(self, vec: np.ndarray) -> str:
        return ",".join(sorted(n for n, b in zip(self.names, vec) if b))


class _LiteralSetCodec:
    """A/H E5 'what follows': a sorted list of literal strings, or NOTHING for the empty set."""

    def __init__(self, universe: list[str]):
        self.names = sorted(universe)
        self.pos = {v: i for i, v in enumerate(self.names)}

    def key(self, answer: Any) -> str | None:
        if answer is None:
            return None
        if isinstance(answer, str):
            return answer
        lits = sorted(answer)
        return str(lits) if lits else "NOTHING"

    def parse(self, key: str) -> np.ndarray:
        vec = np.zeros(len(self.names), dtype=bool)
        if key == "NOTHING":
            return vec
        try:
            lits = ast.literal_eval(key)
        except (ValueError, SyntaxError):
            raise ValueError(f"not a literal list: {key[:60]!r}") from None
        if not isinstance(lits, list):
            raise ValueError(f"not a literal list: {key[:60]!r}")
        for lit in lits:
            if lit not in self.pos or vec[self.pos[lit]]:
                raise ValueError(f"literal outside this item's universe: {lit!r}")
            vec[self.pos[lit]] = True
        return vec

    def encode(self, vec: np.ndarray) -> str:
        lits = [n for n, b in zip(self.names, vec) if b]
        return str(sorted(lits)) if lits else "NOTHING"


class BitSpace(Space):
    kind = "bits"

    def __init__(self, codec: Any, specials: tuple[str, ...] = ()):
        self.codec = codec
        self.n = len(codec.names)
        if self.n == 0:
            raise ValueError("empty bit space")
        self.specials = tuple(specials)
        self.tau = _tau(self.specials)
        self._parse_cache: dict[str, np.ndarray | None] = {}
        self._comb = np.array([math.comb(self.n, d) for d in range(self.n + 1)], dtype=float)

    def key(self, answer: Any) -> str | None:
        return self.codec.key(answer)

    def parse(self, key: str) -> np.ndarray | None:
        if key not in self._parse_cache:
            try:
                self._parse_cache[key] = self.codec.parse(key)
            except ValueError:
                self._parse_cache[key] = None
        return self._parse_cache[key]

    def encode(self, vec: np.ndarray) -> str:
        return self.codec.encode(vec)

    def valid(self, key: str | None) -> bool:
        return key is not None and (key in self.specials or self.parse(key) is not None)

    def log_q(self, key: str) -> float:
        if key in self.specials:
            return math.log(self.tau / len(self.specials))
        if self.parse(key) is None:
            return -math.inf
        return math.log1p(-self.tau) - self.n * math.log(2)

    def log_uniform(self, key: str) -> float:
        if key in self.specials or self.parse(key) is None:
            return -math.inf
        return -self.n * math.log(2)

    def log_size(self) -> float:
        return math.log(2.0 ** self.n + len(self.specials)) if self.n < 1000 else self.n * math.log(2)

    def _coeffs_from_hist(self, hist: np.ndarray, weight: float = 1.0) -> np.ndarray:
        """hist[d] = number of (path) pairs at distance d -> coefficients of g, with D capped at n."""
        c = np.zeros(DMAX + 1)
        for d in range(1, min(self.n, DMAX) + 1):
            c[d] = hist[d] / self._comb[d] * weight
        if self.n < DMAX:  # D >= n is clipped to n: P(D = n) absorbs the tail
            c[self.n + 1:] = c[self.n]
        return c

    def slip(self, y: str, a: str) -> tuple[float, np.ndarray]:
        _no_special(self, a)
        if y in self.specials:
            return 0.0, np.zeros(DMAX + 1)
        vy, va = self.parse(y), self.parse(a)
        d = int((vy != va).sum())
        hist = np.zeros(self.n + 1)
        hist[d] = 1
        return 0.0, self._coeffs_from_hist(hist)

    def slip_set(self, y: str, S: np.ndarray) -> np.ndarray:
        if y in self.specials:
            return np.zeros(DMAX + 1)
        vy = self.parse(y)
        d = (S != vy[None, :]).sum(1)
        hist = np.bincount(d, minlength=self.n + 1).astype(float)
        return self._coeffs_from_hist(hist, 1.0 / len(S))

    def set_array(self, keys: list[str]) -> np.ndarray:
        return np.array([self.parse(k) for k in keys], dtype=bool).reshape(len(keys), self.n)

    def distance(self, y: str, a: str) -> int:
        if y in self.specials or a in self.specials:
            return 0 if y == a else self.n
        return int((self.parse(y) != self.parse(a)).sum())

    def sample_q(self, rng: np.random.Generator) -> str:
        if self.specials and rng.random() < self.tau:
            return self.specials[int(rng.integers(len(self.specials)))]
        return self.sample_uniform(rng)

    def sample_uniform(self, rng: np.random.Generator) -> str:
        return self.encode(rng.random(self.n) < 0.5)

    def sample_slip(self, a: str, rho: float, rng: np.random.Generator) -> str:
        _no_special(self, a)
        d = min(sample_d(rho, rng), self.n)
        vec = self.parse(a).copy()
        flip = rng.choice(self.n, size=d, replace=False)
        vec[flip] = ~vec[flip]
        return self.encode(vec)

    def signature(self) -> tuple:
        return (self.kind, tuple(self.codec.names), self.specials)

    # --- noise-model options -----------------------------------------------------------------
    def q_stratum(self, key: str) -> int | None:
        if key in self.specials:
            return None
        v = self.parse(key)
        return None if v is None else int(v.sum())

    def log_stratum_size(self, s: int) -> float:
        return math.log(self._comb[s])

    def default_strata(self) -> np.ndarray:
        return self._comb / self._comb.sum()

    def ball_fraction(self, r: int, palette: int | None = None) -> float:
        return float(self._comb[: min(r, self.n) + 1].sum() / self._comb.sum())

    def sample_stratum(self, s: int, rng: np.random.Generator) -> str:
        vec = np.zeros(self.n, dtype=bool)
        vec[rng.choice(self.n, size=s, replace=False)] = True
        return self.encode(vec)

    def sample_slip_g(self, a: str, g: np.ndarray, rng: np.random.Generator) -> str:
        _no_special(self, a)
        g = np.asarray(g, dtype=float)
        d = min(int(rng.choice(len(g), p=g / g.sum())), self.n)
        vec = self.parse(a).copy()
        flip = rng.choice(self.n, size=d, replace=False)
        vec[flip] = ~vec[flip]
        return self.encode(vec)

    def _ad_coeffs(self, adds: np.ndarray, drops: np.ndarray, k: np.ndarray) -> np.ndarray:
        """(m, len(AD_CELLS)) coefficients for m (adds, drops, |a|) triples."""
        n = self.n
        c = np.zeros((len(adds), len(AD_CELLS)))
        inv = 1.0 / np.array([math.comb(int(n - kk), int(aa)) * math.comb(int(kk), int(rr))
                              for aa, rr, kk in zip(adds, drops, k)], dtype=float)
        for j, (A, R) in enumerate(AD_CELLS[1:], start=1):
            hit = (np.minimum(A, n - k) == adds) & (np.minimum(R, k) == drops)
            c[hit, j] = inv[hit]
        return c

    def slip_ad(self, y: str, a: str) -> tuple[float, np.ndarray]:
        """(b0, c) of the adds-and-drops kernel: P_slip(y | a) = sum_cells c[cell] g[cell]."""
        _no_special(self, a)
        if y in self.specials:
            return 0.0, np.zeros(len(AD_CELLS))
        vy, va = self.parse(y), self.parse(a)
        adds, drops, k = int((vy & ~va).sum()), int((~vy & va).sum()), int(va.sum())
        return 0.0, self._ad_coeffs(np.array([adds]), np.array([drops]), np.array([k]))[0]

    def slip_set_ad(self, y: str, S: np.ndarray) -> np.ndarray:
        if y in self.specials:
            return np.zeros(len(AD_CELLS))
        vy = self.parse(y)
        adds = (vy[None, :] & ~S).sum(1)
        drops = (~vy[None, :] & S).sum(1)
        k = S.sum(1)
        trip, counts = np.unique(np.stack([adds, drops, k], 1), axis=0, return_counts=True)
        c = self._ad_coeffs(trip[:, 0], trip[:, 1], trip[:, 2])
        return (c * counts[:, None]).sum(0) / len(S)

    def sample_slip_ad(self, a: str, g: np.ndarray, rng: np.random.Generator) -> str:
        _no_special(self, a)
        g = np.asarray(g, dtype=float)
        A, R = AD_CELLS[int(rng.choice(len(g), p=g / g.sum()))]
        vec = self.parse(a).copy()
        ones, zeros = np.flatnonzero(vec), np.flatnonzero(~vec)
        add = rng.choice(zeros, size=min(A, len(zeros)), replace=False)
        drop = rng.choice(ones, size=min(R, len(ones)), replace=False)
        vec[add] = True
        vec[drop] = False
        return self.encode(vec)


# =============================================================================================
# Partitions (colourings up to renaming)
# =============================================================================================


class PartitionSpace(Space):
    kind = "partition"

    def __init__(self, vertices: list[str], k_task: int | None, specials: tuple[str, ...] = ()):
        self.vertices = list(vertices)
        self.n = len(self.vertices)
        self.pos = {v: i for i, v in enumerate(self.vertices)}
        self.k_uniform = k_task or self.n
        self.specials = tuple(specials)
        self.tau = _tau(self.specials)
        self._parse_cache: dict[str, np.ndarray | None] = {}
        self._comb = np.array([math.comb(self.n, d) for d in range(self.n + 1)], dtype=float)

    def key(self, answer: Any) -> str | None:
        if answer is None:
            return None
        return answer if isinstance(answer, str) else colouring_key(answer)

    def parse(self, key: str) -> np.ndarray | None:
        """Restricted-growth string: block id of each vertex, blocks numbered by first vertex."""
        if key in self._parse_cache:
            return self._parse_cache[key]
        out = None
        if key not in self.specials and key:
            blocks = [b.split(",") for b in key.split("|")]
            label = np.full(self.n, -1, dtype=np.int64)
            ok = True
            for j, blk in enumerate(blocks):
                for v in blk:
                    i = self.pos.get(v)
                    if i is None or label[i] != -1:
                        ok = False
                        break
                    label[i] = j
                if not ok:
                    break
            if ok and (label >= 0).all():
                remap: dict[int, int] = {}
                out = np.array([remap.setdefault(int(x), len(remap)) for x in label], dtype=np.int64)
        self._parse_cache[key] = out
        return out

    def encode(self, rgs: np.ndarray) -> str:
        return colouring_key({v: int(c) + 1 for v, c in zip(self.vertices, rgs)})

    @staticmethod
    def canon(colours: np.ndarray) -> np.ndarray:
        remap: dict[int, int] = {}
        return np.array([remap.setdefault(int(x), len(remap)) for x in colours], dtype=np.int64)

    def valid(self, key: str | None) -> bool:
        return key is not None and (key in self.specials or self.parse(key) is not None)

    @staticmethod
    def _log_falling(C: int, b: int) -> float:
        return math.lgamma(C + 1) - math.lgamma(C - b + 1)

    def log_q(self, key: str) -> float:
        if key in self.specials:
            return math.log(self.tau / len(self.specials))
        r = self.parse(key)
        if r is None:
            return -math.inf
        b = int(r.max()) + 1
        return math.log1p(-self.tau) + self._log_falling(self.n, b) - self.n * math.log(self.n)

    def log_uniform(self, key: str) -> float:
        if key in self.specials:
            return -math.inf
        r = self.parse(key)
        if r is None:
            return -math.inf
        b = int(r.max()) + 1
        k = self.k_uniform
        if b > k:
            return -math.inf
        return self._log_falling(k, b) - self.n * math.log(k)

    def log_size(self) -> float:
        lb = _log_bell(self.n)
        return lb if not self.specials else lb + math.log1p(len(self.specials) / math.exp(min(lb, 700)))

    def _coeffs(self, hist: np.ndarray, C: int, weight: float = 1.0) -> np.ndarray:
        c = np.zeros(DMAX + 1)
        for d in range(1, min(self.n, DMAX) + 1):
            c[d] = hist[d] / (self._comb[d] * (C - 1) ** d) * weight
        if self.n < DMAX:
            c[self.n + 1:] = c[self.n]
        return c

    def slip(self, y: str, a: str) -> tuple[float, np.ndarray]:
        _no_special(self, a)
        if y in self.specials:
            return 0.0, np.zeros(DMAX + 1)
        ry, ra = self.parse(y), self.parse(a)
        by, ba = int(ry.max()) + 1, int(ra.max()) + 1
        C = ba + 1
        if by > C:
            return 0.0, np.zeros(DMAX + 1)
        O = np.bincount(ry * C + ra, minlength=by * C).reshape(by, C)
        P = _perms(C, by)
        match = O[np.arange(by)[None, :], P].sum(1)
        hist = np.bincount(self.n - match, minlength=self.n + 1).astype(float)
        return 0.0, self._coeffs(hist, C)

    def set_array(self, keys: list[str]) -> np.ndarray:
        return np.array([self.parse(k) for k in keys], dtype=np.int64).reshape(len(keys), self.n)

    def slip_set(self, y: str, S: np.ndarray) -> np.ndarray:
        """Average slip coefficients over the rows of S (RGS array), grouped by block count."""
        c = np.zeros(DMAX + 1)
        if y in self.specials:
            return c
        ry = self.parse(y)
        by = int(ry.max()) + 1
        blocks = S.max(1) + 1
        for bs in np.unique(blocks):
            C = int(bs) + 1
            if by > C:
                continue
            P = _perms(C, by)
            rows = S[blocks == bs]
            hist = np.zeros(self.n + 1)
            reach = min(self.n, DMAX)
            for start in range(0, len(rows), 4096):
                Sg = rows[start:start + 4096]
                G = len(Sg)
                flat = (np.arange(G)[:, None] * (by * C) + ry[None, :] * C + Sg).ravel()
                O = np.bincount(flat, minlength=G * by * C).reshape(G, by, C)
                # every naming is at least n - sum_j max_c O[j, c] away: skip solutions beyond a slip's reach
                near = self.n - O.max(2).sum(1) <= reach
                if not near.any():
                    continue
                O = O[near]
                match = O[:, np.arange(by)[None, :], P].sum(-1)  # G' x |P|
                hist += np.bincount((self.n - match).ravel(), minlength=self.n + 1)
            c += self._coeffs(hist, C)
        return c / len(S)

    def distance(self, y: str, a: str) -> int:
        """Vertices to recolour to turn y into a, up to renaming (partition distance)."""
        if y in self.specials or a in self.specials:
            return 0 if y == a else self.n
        from scipy.optimize import linear_sum_assignment

        ry, ra = self.parse(y), self.parse(a)
        by, ba = int(ry.max()) + 1, int(ra.max()) + 1
        O = np.bincount(ry * ba + ra, minlength=by * ba).reshape(by, ba)
        r, c = linear_sum_assignment(-O)
        return int(self.n - O[r, c].sum())

    def sample_q(self, rng: np.random.Generator) -> str:
        if self.specials and rng.random() < self.tau:
            return self.specials[int(rng.integers(len(self.specials)))]
        return self.encode(self.canon(rng.integers(self.n, size=self.n)))

    def sample_uniform(self, rng: np.random.Generator) -> str:
        return self.encode(self.canon(rng.integers(self.k_uniform, size=self.n)))

    def sample_slip(self, a: str, rho: float, rng: np.random.Generator) -> str:
        _no_special(self, a)
        ra = self.parse(a).copy()
        C = int(ra.max()) + 2
        d = min(sample_d(rho, rng), self.n)
        for v in rng.choice(self.n, size=d, replace=False):
            new = int(rng.integers(C - 1))
            ra[v] = new if new < ra[v] else new + 1
        return self.encode(self.canon(ra))

    def signature(self) -> tuple:
        return (self.kind, tuple(self.vertices), self.k_uniform, self.specials)

    # --- noise-model options -----------------------------------------------------------------
    def q_stratum(self, key: str) -> int | None:
        if key in self.specials:
            return None
        r = self.parse(key)
        return None if r is None else int(r.max()) + 1

    def log_stratum_size(self, s: int) -> float:
        return _log_int(_stirling2(self.n)[self.n][s])

    def default_strata(self) -> np.ndarray:
        """q's structured part draws n colours uniformly: P(b blocks) = S(n, b) n! / (n - b)! / n^n."""
        S = _stirling2(self.n)[self.n]
        logs = np.array([(_log_int(S[b]) + self._log_falling(self.n, b) - self.n * math.log(self.n)) if S[b] else -np.inf
                         for b in range(self.n + 1)])
        p = np.exp(logs - logs.max())
        return p / p.sum()

    def sample_stratum(self, s: int, rng: np.random.Generator) -> str:
        return self.encode(sample_partition_rgs(self.n, s, rng))

    def ball_fraction(self, r: int, palette: int | None = None) -> float:
        """At most sum_d C(n, d) (C - 1)^d of the Bell(n) partitions are within r recolourings of a
        partition whose slips use C = palette colours (its blocks plus one new colour)."""
        C = palette if palette is not None else self.n
        ball = sum(math.comb(self.n, d) * (C - 1) ** d for d in range(min(r, self.n) + 1))
        return min(1.0, ball / math.exp(_log_bell(self.n)))

    def sample_slip_g(self, a: str, g: np.ndarray, rng: np.random.Generator) -> str:
        _no_special(self, a)
        g = np.asarray(g, dtype=float)
        ra = self.parse(a).copy()
        C = int(ra.max()) + 2
        d = min(int(rng.choice(len(g), p=g / g.sum())), self.n)
        for v in rng.choice(self.n, size=d, replace=False):
            new = int(rng.integers(C - 1))
            ra[v] = new if new < ra[v] else new + 1
        return self.encode(self.canon(ra))


# =============================================================================================
# Item -> channel key and space
# =============================================================================================


def channel_of(item: dict[str, Any]) -> str:
    return item["extra"]["channel"]


def space_for(item: dict[str, Any]) -> Space:
    """The answer space of an item's scoring channel (raises on combinations not built yet)."""
    channel = channel_of(item)
    inst = item["instance"]
    kind = inst["kind"]
    if channel == "decision":
        pos, neg = DECISION_VALUES[kind]

        def dec_key(a: Any, pos: str = pos, neg: str = neg) -> str | None:
            if a is None:
                return None
            if isinstance(a, str):
                return {"X": neg}.get(a, a)
            return pos

        return FiniteSpace([pos, neg], dec_key)
    if channel == "target-bit":
        target, ref = item["params"]["target"], item["params"]["reference_vertex"]

        def bit_key(a: Any) -> str | None:
            if isinstance(a, dict):
                return "same" if a[target] == a[ref] else "different"
            return a if a in ("same", "different", "IMPOSSIBLE") else None

        # the U arms' answer format admits IMPOSSIBLE, and some members (FF-OUT, LF) answer it
        return FiniteSpace(["same", "different", "IMPOSSIBLE"], bit_key)
    if channel == "target-colour":
        target = item["params"]["target"]
        top = max([3] + [max(p["answer"].values()) for p in item["predictions"].values() if isinstance(p["answer"], dict)])

        def colour_key(a: Any) -> str | None:
            if isinstance(a, dict):
                return str(a[target])
            if isinstance(a, (int, np.integer)) and not isinstance(a, bool):
                return str(int(a))
            if isinstance(a, str) and a.strip().isdigit():
                return str(int(a))
            return None

        return FiniteSpace([str(c) for c in range(1, top + 2)], colour_key)
    if channel != "answer":
        raise NotImplementedError(f"channel {channel!r}")
    if kind == "coloring_task":
        k = inst["k"]
        return PartitionSpace(inst["graph"]["vertices"], k, ("IMPOSSIBLE",) if k is not None else ())
    if kind == "sat_task":
        names = inst["declared"] if inst.get("declared") else inst["cnf"]["var_names"]
        return BitSpace(_SatCodec(names), ("UNSAT",))
    if kind == "knapsack_task":
        return BitSpace(_SubsetCodec(inst["knapsack"]["names"]))
    if kind == "entailment_task":
        if inst["fmt"] == "MC":
            letters = [chr(ord("A") + i) for i in range(len(inst["options"]) + 1)]
            return FiniteSpace(letters, lambda a: a if isinstance(a, str) else None)
        if inst["fmt"] == "OPEN":
            from reasoning_heuristics.heuristics.tasks import load_task
            from reasoning_heuristics.problems.entailment import formula as F

            task = load_task(inst)
            atoms = F.atoms_of(task.premises)
            universe = [F.render_lit(a, pol) for a in atoms for pol in (True, False)]
            return BitSpace(_LiteralSetCodec(universe), ("X",))
    raise NotImplementedError(f"answer channel for {kind} / {inst.get('fmt')}")
