"""A small, instrumented RASP-L interpreter.

Semantics follow the RASP-L core of Zhou et al. 2024 (arXiv 2310.16028, Listing 2;
reference code: github.com/apple-aiml-research/ml-np-rasp, src/np_rasp/core.py):
every selector is causal (key index <= query index), `aggregate` reduces with
mean / max / min, mean is truncated to an integer, and `sel_width` counts selected keys.
This file re-implements those few lines (it does not vendor Apple's code) and adds:

* **counting**: every primitive call is tallied, so a program's length is measured by
  running it, not by hand;
* **depth**: every value carries the number of attention layers on its longest path;
* **types** (Zhou et al. App. E): int8 values; `indices` and each `sel_width` output are
  index-like types that admit only comparisons and +/-1.  Departures are not errors;
  they are recorded as *flags* so each program's report says which rule it bends.

Length convention (pre-registered for T2): one unit per call of `select`, `aggregate`,
`sel_width`, `tok_map`, `seq_map` (operators on SOps are `tok_map`/`seq_map` calls).
`tokens`, `indices`, `full` are free.  A select whose predicate conjoins two key/query
comparisons counts once (one attention head adds the two score terms).

Run with numpy installed.  Nothing here is fast; instances are small.
"""

from __future__ import annotations

import itertools
from collections import Counter
from dataclasses import dataclass, field

import numpy as np

INT8_MIN, INT8_MAX = -128, 127

# --------------------------------------------------------------------------- tracing


@dataclass
class Trace:
    counts: Counter = field(default_factory=Counter)
    flags: set = field(default_factory=set)
    max_layer: int = 0

    @property
    def length(self) -> int:
        return sum(self.counts.values())

    @property
    def heads(self) -> int:
        return self.counts["aggregate"] + self.counts["sel_width"]


_TRACE = Trace()


def reset_trace() -> Trace:
    global _TRACE
    _TRACE = Trace()
    return _TRACE


def _tick(kind: str, layer: int = 0) -> None:
    _TRACE.counts[kind] += 1
    _TRACE.max_layer = max(_TRACE.max_layer, layer)


def flag(name: str) -> None:
    _TRACE.flags.add(name)


_width_ids = itertools.count()

# --------------------------------------------------------------------------- values


class SOp:
    """A sequence value. kind: 'int8' | 'index' | ('width', id) | 'set'."""

    def __init__(self, val, kind="int8", layer=0):
        self.val = np.asarray(val) if kind != "set" else val
        self.kind = kind
        self.layer = layer
        if kind == "int8":
            self.val = self.val.astype(int)
            if self.val.size and (self.val.min() < INT8_MIN or self.val.max() > INT8_MAX):
                flag("int8_overflow")

    def __len__(self):
        return len(self.val)

    # Elementwise operators are maps (one primitive each).
    def _bin(self, other, f):
        return seq_map(self, other, f) if isinstance(other, SOp) else tok_map(self, lambda x: f(x, other))

    def __add__(self, o): return self._bin(o, lambda a, b: a + b)
    def __sub__(self, o): return self._bin(o, lambda a, b: a - b)
    def __mul__(self, o): return self._bin(o, lambda a, b: a * b)
    def __and__(self, o): return self._bin(o, lambda a, b: (a != 0) & (b != 0))
    def __or__(self, o): return self._bin(o, lambda a, b: (a != 0) | (b != 0))
    def __eq__(self, o): return self._bin(o, lambda a, b: a == b)
    def __ne__(self, o): return self._bin(o, lambda a, b: a != b)
    def __lt__(self, o): return self._bin(o, lambda a, b: a < b)
    def __le__(self, o): return self._bin(o, lambda a, b: a <= b)
    def __gt__(self, o): return self._bin(o, lambda a, b: a > b)
    def __ge__(self, o): return self._bin(o, lambda a, b: a >= b)
    def __invert__(self): return tok_map(self, lambda a: a == 0)
    def __neg__(self): return tok_map(self, lambda a: -a)
    __hash__ = None


class Selector:
    def __init__(self, mat, layer):
        self.mat = mat
        self.layer = layer


# --------------------------------------------------------------------------- core (free)


def tokens(seq) -> SOp:
    return SOp(np.asarray(seq, dtype=int))


def indices(x: SOp) -> SOp:
    return SOp(np.arange(len(x)), kind="index")


def full(x: SOp, c: int) -> SOp:
    return SOp(np.full(len(x), c))


# --------------------------------------------------------------------------- core (counted)


def _vec(f, *arrays):
    out = f(*arrays)
    return np.broadcast_to(np.asarray(out), arrays[0].shape)


def tok_map(x: SOp, f) -> SOp:
    _tick("tok_map", x.layer)
    if x.kind != "int8":
        flag("map_on_index")  # only +/-1 is RASP-L legal; use succ()/pred()
    return SOp(_vec(f, x.val).astype(int), "int8", x.layer)


def seq_map(x: SOp, y: SOp, f) -> SOp:
    layer = max(x.layer, y.layer)
    _tick("seq_map", layer)
    if x.kind != y.kind:
        if "set" in (x.kind, y.kind):
            flag("set_valued")
        elif x.kind == "int8" or y.kind == "int8":
            flag("index_int8_mix")
        else:
            flag("cross_width_compare")  # as in Zhou et al.'s own binary_mode listing
    elif x.kind != "int8":
        out = _vec(f, x.val, y.val)
        if out.dtype != bool:
            flag("index_arithmetic")
    return SOp(_vec(f, x.val, y.val).astype(int), "int8", layer)


def map_n(f, *xs: SOp) -> SOp:
    """An n-ary elementwise map, counted as n-1 binary maps (a tree of seq_maps).

    Flagged 'nary_map': the binary tree needs int8 intermediate codes, which exist only
    when the joint domain of the inputs is small enough.  The count is the convention.
    """
    layer = max(x.layer for x in xs)
    for _ in range(len(xs) - 1):
        _tick("seq_map", layer)
    flag("nary_map")
    return SOp(_vec(f, *[x.val for x in xs]).astype(int), "int8", layer)


def succ(x: SOp, k: int = 1) -> SOp:
    """Successor / predecessor on an index-like value: legal in RASP-L (counted as a map)."""
    _tick("tok_map", x.layer)
    if x.kind == "int8":
        return SOp(x.val + k, "int8", x.layer)
    if abs(k) > 3:
        flag("index_arithmetic")
    return SOp(x.val + k, x.kind, x.layer)


def _as_tuple(z):
    return z if isinstance(z, tuple) else (z,)


def select(k, q, pred) -> Selector:
    """Causal selector.  k, q are SOps or 2-tuples of SOps (conjunctive predicate).

    pred receives numpy arrays shaped (1, n) for keys and (n, 1) for queries
    (tuples in the same order) and must return a boolean (n, n) array.
    """
    ks, qs = _as_tuple(k), _as_tuple(q)
    layer = max(s.layer for s in ks + qs)
    _tick("select", layer)
    for a, b in zip(ks, qs):
        if a.kind != b.kind and "set" not in (a.kind, b.kind):
            flag("select_kind_mismatch")
        if "set" in (a.kind, b.kind):
            flag("set_valued")
    n = len(ks[0])
    if any(s.kind == "set" for s in ks + qs):
        kv = tuple(s.val for s in ks)
        qv = tuple(s.val for s in qs)
        mat = np.array([[bool(pred(*(x[j] for x in kv), *(x[i] for x in qv))) for j in range(n)]
                        for i in range(n)])
    else:
        kv = tuple(s.val[None, :] for s in ks)
        qv = tuple(s.val[:, None] for s in qs)
        mat = np.broadcast_to(pred(*kv, *qv), (n, n)).astype(bool)
    mat = mat & np.tril(np.ones((n, n), dtype=bool))  # causal: key index <= query index
    return Selector(mat, layer)


def aggregate(s: Selector, v: SOp, reduction: str = "mean", default: int = 0) -> SOp:
    layer = max(s.layer, v.layer) + 1
    _tick("aggregate", layer)
    if v.kind == "set":
        raise ValueError("use aggregate_set for set-valued data")
    if v.kind != "int8" and reduction == "mean":
        flag("index_arithmetic")
    out = np.full(len(v), default)
    width = s.mat.sum(axis=1)
    if reduction == "mean":
        tot = s.mat @ v.val
        nz = width > 0
        out[nz] = np.trunc(tot[nz] / width[nz]).astype(int)
    else:
        big = INT8_MIN - 1 if reduction == "max" else INT8_MAX + 1
        big = big if v.kind == "int8" else (-1 if reduction == "max" else 10**9)
        m = np.where(s.mat, v.val[None, :], big)
        red = m.max(axis=1) if reduction == "max" else m.min(axis=1)
        out = np.where(width > 0, red, default)
    return SOp(out, v.kind, layer)


def sel_width(s: Selector) -> SOp:
    layer = s.layer + 1
    _tick("sel_width", layer)
    return SOp(s.mat.sum(axis=1), ("width", next(_width_ids)), layer)


# --------------------------------------------------------------------------- extension (flagged)


def aggregate_set(s: Selector, v: SOp) -> SOp:
    """Set-valued aggregation (union of selected int8 values).

    NOT RASP-L: per-position state is a set of up to n values, i.e. a residual stream of
    width >= n.  Real transformers can hold such sets in superposition; RASP-L forbids it
    because the representation is length-dependent (non-uniform).  Flagged 'set_valued'.
    """
    layer = max(s.layer, v.layer) + 1
    _tick("aggregate", layer)
    flag("set_valued")
    vals = [frozenset(int(v.val[j]) for j in np.flatnonzero(s.mat[i])) for i in range(len(v))]
    return SOp(vals, "set", layer)


# --------------------------------------------------------------------------- library


def shift(x: SOp, n: int = 1, default: int = 0) -> SOp:
    """x[i - n] (the value n positions back).  3 primitives: succ, select, aggregate."""
    idx = indices(x)
    return aggregate(select(succ(idx, n), idx, lambda k, q: k == q), x, "max", default)


def where(cond: SOp, a, b) -> SOp:
    """One map when a, b are constants or one of them is; a seq_map chain otherwise."""
    if not isinstance(a, SOp) and not isinstance(b, SOp):
        return tok_map(cond, lambda c: np.where(c != 0, a, b))
    if isinstance(a, SOp) and not isinstance(b, SOp):
        return seq_map(cond, a, lambda c, x: np.where(c != 0, x, b))
    if not isinstance(a, SOp) and isinstance(b, SOp):
        return seq_map(cond, b, lambda c, y: np.where(c != 0, a, y))
    # three-input map = two maps (pack cond into a, then combine)
    packed = seq_map(cond, a, lambda c, x: np.where(c != 0, x, INT8_MIN))
    return seq_map(packed, b, lambda p, y: np.where(p != INT8_MIN, p, y))


def select_all(x: SOp) -> Selector:
    return select(full(x, 1), full(x, 1), lambda k, q: k == q)


def last(x: SOp) -> int:
    """Read the program's output at the final position (the answer slot)."""
    return int(x.val[-1])


@dataclass
class Report:
    name: str
    length: int
    counts: dict
    heads: int
    layers: int
    flags: tuple


def measure(name: str, program, example_input) -> Report:
    """Run `program` once and return its length / depth / flags.

    Programs are straight-line (Python loops only over constants such as k rounds), so
    one run gives the static count.
    """
    tr = reset_trace()
    program(example_input)
    return Report(name, tr.length, dict(tr.counts), tr.heads, tr.max_layer, tuple(sorted(tr.flags)))
