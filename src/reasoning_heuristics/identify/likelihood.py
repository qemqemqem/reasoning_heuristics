"""Likelihoods P(y | h, x) for every member of a fit unit, and the tensors the mixture fit reads.

Computed from each item's `predictions`, its `instance` and the raw answer (`members.py`,
`spaces.py`); the items' `disconfirms` tables are not used.

A member that slips (deterministic and set-valued members) gives its intended answer with
probability 1 - eps and otherwise slips; distributional members are complete noise models and are
used as stored. Two slip models:

- `near-miss` (the pre-registered noise model, SCOPE §6 rule 3): a slip is a near miss of the
  intended answer under the domain kernel of `spaces.py` (vertices recoloured, variables
  flipped, items or literals added or dropped, another decision or option). The slip rate eps
  and the slip shape rho are estimated in the fit, not fixed.
- `uniform` (the coarse alternative, used for the misspecification check): a slip goes uniformly
  to one of the item's other candidate answers, i.e. another deterministic member's answer or
  "anything else" (one alternative, spread uniformly over the remaining answer space). This is
  the "slips uniform over candidate answers" model the C vertical's first recovery run used, with
  three fixes over the items' tables: the slip never lands on the member's own answer;
  set-valued members put their no-slip mass on valid solutions only; and no member is dropped.
  It still depends on which members are in the zoo, by construction.

Both share q, the "none of the above" distribution (`Space.log_q`), and both are written as
P(y | h, x) = (1 - eps) A[h] + eps (B0[h] + sum_d C[h, d] g_d(rho)) with rows rescaled so the
largest entry is 1 (`log_scale` keeps the factor), so one EM serves both.

Responses that are not `ok` (DESIGN §5 rule 5):

- `parse_fail`, `refusal`, `partial`: excluded from the answer likelihood; counted per cell.
- `declared_impossible`: by default read as the item's impossibility token when the channel has
  one (UNSAT, IMPOSSIBLE, or the decision's negative value on SAT and colouring decisions);
  otherwise excluded and counted. `declared_impossible="exclude"` excludes them all.
- `truncated` (SCOPE §6 rule 2, censoring): excluded and counted per cell, unless a `TokenModel`
  is given. **Token-model hook:** with `token_model`, a truncated run becomes a censored row with
  likelihood P(run hits the cap | h, x) for each member and for q, and every answered row is
  multiplied by the survival probability 1 - P(cap | h, x). Without one, truncation that depends
  on the member biases the weights toward members that finish.
- An `ok` answer that is not on the item's scoring channel (e.g. a colouring with too many
  vertices) is excluded and counted as `off_channel`.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Iterable, Protocol

import numpy as np

from reasoning_heuristics.identify.members import Pred, item_preds, normal_form, q_normal_form
from reasoning_heuristics.identify.records import Response
from reasoning_heuristics.identify.spaces import DMAX, FiniteSpace, Space, space_for
from reasoning_heuristics.identify.units import Unit

NEAR_MISS = "near-miss"
UNIFORM = "uniform"
MODELS = (NEAR_MISS, UNIFORM)
IMPOSSIBILITY_TOKENS = ("UNSAT", "IMPOSSIBLE")


class TokenModel(Protocol):
    """Hook for a reasoning-token model (SCOPE §6 rule 2): P(the run hits the token cap | h, x).

    `label` is a member label, or None for q. A real implementation would map each member's step
    count on the item to tokens with a fitted per-model rate; none is fitted yet.
    """

    def p_truncated(self, item: dict[str, Any], label: str | None) -> float: ...


@dataclass
class TruncationTable:
    """The simplest token model: a fixed truncation probability per (item_id, label), else `default`
    (q uses label None)."""

    table: dict[tuple[str, str | None], float]
    default: float = 0.0

    def p_truncated(self, item: dict[str, Any], label: str | None) -> float:
        return self.table.get((item["item_id"], label), self.default)


@dataclass
class ItemModel:
    item: dict[str, Any]
    space: Space
    preds: dict[str, Pred]
    candidates: list[str]  # distinct answers of the available deterministic members

    @classmethod
    def build(cls, item: dict[str, Any]) -> "ItemModel":
        space = space_for(item)
        preds = item_preds(item, space)
        cands: list[str] = []
        for p in preds.values():
            if p.kind == "det" and p.key not in cands:
                cands.append(p.key)
        return cls(item, space, preds, cands)

    def q_other_mass(self) -> float:
        """q's mass on the answers that are not candidates (the 'anything else' alternative)."""
        if not hasattr(self, "_q_other"):
            self._q_other = max(0.0, 1.0 - sum(math.exp(self.space.log_q(c)) for c in self.candidates))
        return self._q_other


@dataclass
class Observation:
    item: int  # index into the unit's items
    key: str | None  # None for a censored (truncated) row
    response: Response | None = None

    @property
    def censored(self) -> bool:
        return self.key is None


@dataclass
class Exclusions:
    """Responses kept out of the answer likelihood, by cell and category."""

    counts: dict[str, Counter] = field(default_factory=lambda: defaultdict(Counter))
    totals: Counter = field(default_factory=Counter)

    def add(self, cell: str, category: str) -> None:
        self.counts[cell][category] += 1

    def count_total(self, cell: str) -> None:
        self.totals[cell] += 1

    def rates(self) -> dict[str, dict[str, float]]:
        return {cell: {cat: n / self.totals[cell] for cat, n in sorted(c.items())} for cell, c in sorted(self.counts.items())}

    def to_json(self) -> dict[str, Any]:
        return {"by_cell": {cell: dict(c) for cell, c in sorted(self.counts.items())},
                "responses_by_cell": dict(sorted(self.totals.items())), "rates": self.rates()}


@dataclass
class Tensors:
    A: np.ndarray  # (N, G) no-slip probability
    B0: np.ndarray  # (N, G) rho-free slip probability
    C: np.ndarray  # (N, G, DMAX + 1) coefficients of g(rho)
    Q: np.ndarray  # (N,) q
    avail: np.ndarray  # (N, G) bool
    slips: np.ndarray  # (G,) bool: the column has slips
    log_scale: np.ndarray  # (N,)
    item: np.ndarray  # (N,) unit item index
    cluster: np.ndarray  # (N,)
    labels: list[str]  # column labels (group names)
    finite: np.ndarray | None = None  # (N,) bool: the row's channel is finite (decision, option, bit)

    @property
    def n(self) -> int:
        return self.A.shape[0]

    @property
    def slip_identified(self) -> bool:
        """False when every row is on a finite channel: there a slip to another value is a mixture with
        q (uniform over the values), so eps cannot be told apart from the unexplained mass. The fit then
        holds eps at 0 and pi_0 includes slips."""
        return self.finite is None or not bool(self.finite.all())

    @property
    def rho_free(self) -> bool:
        return not bool(self.C.any())

    def subset(self, rows: np.ndarray) -> "Tensors":
        return Tensors(self.A[rows], self.B0[rows], self.C[rows], self.Q[rows], self.avail[rows], self.slips,
                       self.log_scale[rows], self.item[rows], self.cluster[rows], self.labels,
                       None if self.finite is None else self.finite[rows])


@dataclass
class Group:
    name: str
    members: list[str]
    with_q: bool = False  # tied with q on every item: folded into the unexplained mass


class UnitModel:
    """A fit unit with its answer spaces, member predictions, tie groups and a likelihood cache.

    **Ties.** Members whose predicted distributions are identical on every item of the unit (same
    `normal_form` everywhere, unavailability included) cannot be separated by any data; they get
    one column and are reported as one group, named "A = B = ...". A group identical to q on every
    item (e.g. RANDOM (H) on a fewest-colour task) is folded into the unexplained mass.
    """

    def __init__(self, unit: Unit, model: str = NEAR_MISS, merge_ties: bool = True, labels: list[str] | None = None):
        if model not in MODELS:
            raise ValueError(f"likelihood model must be one of {MODELS}")
        self.unit = unit
        self.model = model
        self.items = [ItemModel.build(it) for it in unit.items]
        self.labels = labels if labels is not None else unit.labels()
        self.groups = self._groups(merge_ties)
        self._cache: dict[tuple[int, str], tuple] = {}

    # --- ties -------------------------------------------------------------------------------
    def signature(self, i: int, label: str) -> tuple:
        im = self.items[i]
        return normal_form(im.preds.get(label, Pred("na")), im.space)

    def _groups(self, merge: bool) -> list[Group]:
        n = len(self.items)
        sigs = {lbl: tuple(self.signature(i, lbl) for i in range(n)) for lbl in self.labels}
        qsig = tuple(q_normal_form(im.space) for im in self.items)
        groups: dict[tuple, list[str]] = {}
        for lbl in self.labels:
            groups.setdefault(sigs[lbl] if merge else (lbl,), []).append(lbl)
        return [Group(" = ".join(m) if len(m) > 1 else m[0], m, merge and key == qsig) for key, m in groups.items()]

    @property
    def columns(self) -> list[Group]:
        """The groups that get their own mixture weight (groups tied with q are folded into q)."""
        return [g for g in self.groups if not g.with_q]

    @property
    def q_members(self) -> list[str]:
        return [m for g in self.groups if g.with_q for m in g.members]

    def column_of(self, label: str) -> int | None:
        """Column index of a member's group (None if the member is folded into q)."""
        for j, g in enumerate(self.columns):
            if label in g.members:
                return j
        if label in self.q_members:
            return None
        raise KeyError(label)

    def pred(self, i: int, label: str) -> Pred:
        return self.items[i].preds.get(label, Pred("na"))

    # --- rows -------------------------------------------------------------------------------
    def row(self, i: int, y: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, np.ndarray]:
        """(A, B0, C, Q, avail) for observed answer key y on item i, one entry per column (unscaled)."""
        ck = (i, y)
        if ck in self._cache:
            return self._cache[ck]
        im = self.items[i]
        cols = self.columns
        G = len(cols)
        A, B0 = np.zeros(G), np.zeros(G)
        C = np.zeros((G, DMAX + 1))
        avail = np.zeros(G, dtype=bool)
        Q = math.exp(im.space.log_q(y))
        for g, grp in enumerate(cols):
            p = im.preds.get(grp.members[0], Pred("na"))
            if not p.available:
                continue
            avail[g] = True
            if p.kind == "det":
                A[g] = 1.0 if y == p.key else 0.0
                if self.model == NEAR_MISS:
                    B0[g], C[g] = im.space.slip(y, p.key)
                else:
                    B0[g] = self._candidate_slip(im, y, p.key)
            elif p.kind == "set":
                A[g] = 1.0 / p.sol.size if p.sol.contains(y) else 0.0
                if self.model == NEAR_MISS:
                    C[g] = im.space.slip_set(y, p.sol.array(im.space))
                else:
                    B0[g] = self._candidate_slip(im, y, None)
            else:
                A[g] = B0[g] = self._noslip_prob(im, p, y, Q)
        out = (A, B0, C, Q, avail)
        self._cache[ck] = out
        return out

    @staticmethod
    def _candidate_slip(im: ItemModel, y: str, a: str | None) -> float:
        """Uniform-over-candidates slip from intended answer a (None: a set-valued member): each other
        candidate answer, and 'anything else' (q restricted to the non-candidates), get 1/K each."""
        q_other = im.q_other_mass()
        alts = [c for c in im.candidates if c != a]
        K = len(alts) + (1 if q_other > 0 else 0)
        if y == a or K == 0:
            return 0.0
        if y in im.candidates:
            return 1.0 / K
        return math.exp(im.space.log_q(y)) / (K * q_other)

    # --- sampling (the generative side of the same model; fake models use it) ---------------
    def sample(self, i: int, label: str, eps: float, rho: float, rng: np.random.Generator) -> str:
        """Draw an answer key from P(y | h, x) under this unit's slip model."""
        im = self.items[i]
        p = self.pred(i, label)
        if p.kind == "na":
            raise ValueError(f"{label} has no prediction on item {im.item['item_id']}")
        if p.kind in ("det", "set"):
            a = p.key if p.kind == "det" else p.sol.keys()[int(rng.integers(p.sol.size))]
            if rng.random() >= eps:
                return a
            if self.model == NEAR_MISS:
                return im.space.sample_slip(a, rho, rng)
            return self._sample_candidate_slip(im, a if p.kind == "det" else None, rng)
        return self._sample_noslip(im, p, rng)

    @staticmethod
    def _sample_candidate_slip(im: ItemModel, a: str | None, rng: np.random.Generator) -> str:
        alts: list[str | None] = [c for c in im.candidates if c != a]
        if im.q_other_mass() > 0:
            alts.append(None)
        pick = alts[int(rng.integers(len(alts)))]
        if pick is not None:
            return pick
        cands = set(im.candidates)
        while True:
            y = im.space.sample_q(rng)
            if y not in cands:
                return y

    @staticmethod
    def _sample_noslip(im: ItemModel, p: Pred, rng: np.random.Generator) -> str:
        if p.kind == "uniform":
            return im.space.sample_uniform(rng)
        keys = list(p.dist)
        probs = np.array([p.dist[k] for k in keys], dtype=float)
        k = keys[int(rng.choice(len(keys), p=probs / probs.sum()))]
        if k == "_other":
            return im.space.sample_q(rng)
        if k == "_uniform":
            return im.space.sample_uniform(rng)
        if k == "_exact":
            ex = p.exact
            return ex.key if ex.kind == "det" else ex.sol.keys()[int(rng.integers(ex.sol.size))]
        return k

    def sample_q(self, i: int, rng: np.random.Generator) -> str:
        return self.items[i].space.sample_q(rng)

    @staticmethod
    def _noslip_prob(im: ItemModel, p: Pred, y: str, Q: float) -> float:
        if p.kind == "uniform":
            return math.exp(im.space.log_uniform(y))
        total = 0.0
        for k, v in p.dist.items():
            if k == "_other":
                total += v * Q
            elif k == "_uniform":
                total += v * math.exp(im.space.log_uniform(y))
            elif k == "_exact":
                ex = p.exact
                if ex.kind == "set":
                    total += v * (1.0 / ex.sol.size if ex.sol.contains(y) else 0.0)
                else:
                    total += v * (1.0 if y == ex.key else 0.0)
            elif k == y:
                total += v
        return total

    # --- observations -----------------------------------------------------------------------
    def observations(self, responses: Iterable[Response], token_model: TokenModel | None = None,
                     declared_impossible: str = "as-token") -> tuple[list[Observation], Exclusions]:
        """Turn responses into likelihood rows; everything else is counted in Exclusions."""
        obs: list[Observation] = []
        exc = Exclusions()
        for r in responses:
            i = self.unit.index.get(r.item_id)
            if i is None:
                raise KeyError(f"response for item {r.item_id} is not in unit {self.unit.name}")
            it = self.unit.items[i]
            if it["content_hash"] != r.content_hash:
                raise ValueError(f"content_hash mismatch for {r.item_id}")
            cell = it["cell"]
            exc.count_total(cell)
            space = self.items[i].space
            if r.category == "ok":
                key = space.key(r.answer) if r.answer is not None else r.answer_key
                if r.answer is not None and r.answer_key is not None and not isinstance(space, FiniteSpace) \
                        and r.answer_key != key:
                    raise ValueError(f"{r.item_id}: answer_key {r.answer_key!r} does not match the answer ({key!r})")
                if key is None or not space.valid(key):
                    exc.add(cell, "off_channel")
                    continue
                obs.append(Observation(i, key, r))
            elif r.category == "declared_impossible":
                tok = _impossibility_token(space) if declared_impossible == "as-token" else None
                if tok is None:
                    exc.add(cell, "declared_impossible")
                    continue
                obs.append(Observation(i, tok, r))
            elif r.category == "truncated" and token_model is not None:
                obs.append(Observation(i, None, r))
            else:
                exc.add(cell, r.category)
        return obs, exc

    def tensors(self, obs: list[Observation], token_model: TokenModel | None = None) -> Tensors:
        cols = self.columns
        G, N = len(cols), len(obs)
        A, B0 = np.zeros((N, G)), np.zeros((N, G))
        C = np.zeros((N, G, DMAX + 1))
        Q = np.zeros(N)
        avail = np.zeros((N, G), dtype=bool)
        for n, ob in enumerate(obs):
            it = self.unit.items[ob.item]
            if ob.censored:
                for g, grp in enumerate(cols):
                    if self.pred(ob.item, grp.members[0]).available:
                        avail[n, g] = True
                        A[n, g] = B0[n, g] = token_model.p_truncated(it, grp.members[0])
                Q[n] = token_model.p_truncated(it, None)
                continue
            a, b0, c, q, av = self.row(ob.item, ob.key)
            A[n], B0[n], C[n], Q[n], avail[n] = a, b0, c, q, av
            if token_model is not None:
                surv = np.array([1.0 - token_model.p_truncated(it, grp.members[0]) for grp in cols])
                A[n] *= surv
                B0[n] *= surv
                C[n] *= surv[:, None]
                Q[n] *= 1.0 - token_model.p_truncated(it, None)
        scale = np.maximum.reduce([A.max(1, initial=0.0), B0.max(1, initial=0.0), C.max((1, 2), initial=0.0), Q])
        if (scale <= 0).any():
            bad = [obs[n] for n in np.where(scale <= 0)[0][:3]]
            raise ValueError(f"{int((scale <= 0).sum())} rows have zero likelihood under every component: "
                             f"{[(self.unit.items[o.item]['item_id'], o.key) for o in bad]}")
        A /= scale[:, None]
        B0 /= scale[:, None]
        C /= scale[:, None, None]
        Q = Q / scale
        slips = np.array([any(self.pred(i, g.members[0]).slips for i in range(len(self.items))) for g in cols])
        items = np.array([o.item for o in obs], dtype=np.int64)
        finite = np.array([isinstance(self.items[o.item].space, FiniteSpace) for o in obs], dtype=bool)
        return Tensors(A, B0, C, Q, avail, slips, np.log(scale), items, self.unit.cluster[items], [g.name for g in cols],
                       finite)


def _impossibility_token(space: Space) -> str | None:
    if isinstance(space, FiniteSpace):
        neg = [v for v in space.values if v in IMPOSSIBILITY_TOKENS]
        return neg[0] if neg else None
    for t in IMPOSSIBILITY_TOKENS:
        if t in space.specials:
            return t
    return None
