"""Noise-model options for the mixture fit (docs/NOISE_MODEL.md).

The pre-registered noise model (SCOPE §6 rule 3) is the default, `NoiseModel()`: a slip from a
deterministic or set-valued member has rate eps (shared by every member, capped at 0.5) and a
truncated-geometric distance kernel with shape rho (`spaces.trunc_geom`), and q is uniform over
the answer space with half its mass on the special tokens. Every committed result uses it, and the
code path it takes is unchanged (`mixture.em` and `mixture.fit` dispatch on `NoiseModel.is_default`).

The options, each estimated by the same EM (`mixture._GeneralStepper`):

- `kernel`: the slip kernel's shape over the cells a slip can land in.
  - `geometric` (default): P(D = d) = g_d(rho), one parameter.
  - `free`: g_1..g_DMAX free (a nonparametric distance kernel), shared by the members of a fit
    unit; the M-step is closed form (expected slips per distance, normalised).
  - `swap` (bit spaces only: knapsack item sets, SAT assignments): a free kernel over
    (adds, drops) cells with adds + drops <= DMAX, so a one-for-one swap (1, 1) has its own mass
    instead of being a two-position slip. Adds are positions set (an item packed, a variable
    made true), drops positions cleared; a cell asks for more adds than the answer has zeros
    (or more drops than ones) is clipped to what there is, as the distance kernel clips D at n.
- `eps`: `shared` (default) or `member` (one slip rate per tie group).
- `eps_max`: the cap on eps (default 0.5; 1 lifts it).
- `reach`: the largest distance a slip can move (free and swap kernels; default 6 = `spaces.DMAX`).
  `auto` takes, per unit, the largest reach <= 6 whose ball around an answer covers at most
  `REACH_COVER` (a fifth) of the item's answer space (`spaces.Space.ball_fraction`), on every item.
  A member that always slips is then a cloud at least five times denser than q around its answer,
  not a stand-in for q: on knapsack (10 items) six moves reach 83% of all packings, so with the cap
  lifted, pure noise loads on members (docs/NOISE_MODEL.md, Stage 0).
- `q`: the reference distribution.
  - `uniform` (default): as `spaces.Space.log_q`.
  - `strata`: uniform within size strata, with the strata's probabilities estimated: the number of
    colour blocks of a colouring, the number of items packed or variables set true of a bit
    vector. One categorical per number of positions n in the unit (items of different sizes do not
    share strata). The special tokens' total mass tau is estimated too, except where a member
    predicts a special token on every item (ALWAYS-UNSAT and the like): tau and that member's
    weight would then be one ridge (pi_member + tau pi_0 is all the data identify), so tau is 0
    there and the member carries the constant token. Finite channels keep q uniform.

`NoiseParams` holds one fit's parameters in a form the fake models sample from
(`likelihood.UnitModel.sample_from`).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np

KERNELS = ("geometric", "free", "swap")
EPS_MODES = ("shared", "member")
Q_MODES = ("uniform", "strata")


@dataclass(frozen=True)
class NoiseModel:
    kernel: str = "geometric"
    eps: str = "shared"
    eps_max: float = 0.5
    q: str = "uniform"
    reach: int | str = 6

    def __post_init__(self) -> None:
        if self.kernel not in KERNELS:
            raise ValueError(f"kernel must be one of {KERNELS}, not {self.kernel!r}")
        if self.eps not in EPS_MODES:
            raise ValueError(f"eps must be one of {EPS_MODES}, not {self.eps!r}")
        if self.q not in Q_MODES:
            raise ValueError(f"q must be one of {Q_MODES}, not {self.q!r}")
        if not 0.0 < self.eps_max <= 1.0:
            raise ValueError(f"eps_max must be in (0, 1], not {self.eps_max}")
        if self.reach != "auto" and not (isinstance(self.reach, int) and 1 <= self.reach <= 6):
            raise ValueError(f"reach must be 1..6 or 'auto', not {self.reach!r}")
        if self.reach != 6 and self.kernel == "geometric":
            raise ValueError("reach applies to the free and swap kernels (the geometric kernel is defined up to 6)")

    @property
    def is_default(self) -> bool:
        return self == NoiseModel()

    @property
    def cells(self) -> str:
        """The kernel's cells: 'distance' (geometric, free) or 'adds-drops' (swap)."""
        return "adds-drops" if self.kernel == "swap" else "distance"

    def to_json(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def parse(cls, spec: str | None) -> "NoiseModel":
        """'kernel=free,eps_max=1,q=strata' -> NoiseModel; a name in CANDIDATES; '' or None -> default."""
        if not spec:
            return cls()
        if spec in CANDIDATES:
            return CANDIDATES[spec]
        kw: dict[str, Any] = {}
        for part in spec.split(","):
            k, _, v = part.partition("=")
            k = k.strip()
            if k not in ("kernel", "eps", "eps_max", "q", "reach"):
                raise ValueError(f"unknown noise option {k!r} in {spec!r}")
            v = v.strip()
            kw[k] = float(v) if k == "eps_max" else (int(v) if k == "reach" and v != "auto" else v)
        return cls(**kw)


# The candidates docs/NOISE_MODEL.md evaluates, nested from the pre-registered model.
CANDIDATES: dict[str, NoiseModel] = {
    "M0": NoiseModel(),
    "K": NoiseModel(kernel="free"),
    "KE": NoiseModel(kernel="free", eps_max=1.0),
    "KEQ": NoiseModel(kernel="free", eps_max=1.0, q="strata"),
    "KEQ-h": NoiseModel(kernel="free", eps="member", eps_max=1.0, q="strata"),
    "SEQ": NoiseModel(kernel="swap", eps_max=1.0, q="strata"),
    "KEQ-r": NoiseModel(kernel="free", eps_max=1.0, q="strata", reach="auto"),
    "SEQ-r": NoiseModel(kernel="swap", eps_max=1.0, q="strata", reach="auto"),
}
REACH_COVER = 0.2


@dataclass
class NoiseParams:
    """One fit's noise parameters, for sampling fake data from it.

    eps: one rate, or {member label: rate} (labels missing from the dict use `eps_default`);
    g: the kernel over the unit's cells (index 0 unused); tau: q's special-token mass (None: q is
    uniform); strata: {(space kind, n): probabilities over stratum sizes 0..n} (None: q is uniform)."""

    eps: float | dict[str, float]
    g: np.ndarray
    tau: float | None = None
    strata: dict[tuple[str, int], np.ndarray] | None = None
    eps_default: float = 0.0
    cells: str = "distance"
    extra: dict[str, Any] = field(default_factory=dict)

    def eps_for(self, label: str) -> float:
        if isinstance(self.eps, dict):
            return float(self.eps.get(label, self.eps_default))
        return float(self.eps)
