"""The heuristic zoo's single interface.

Every member is a function `member(task, params) -> Prediction(answer, trace_features)`.

- `task` is a domain task object (`ColouringTask`, `SatTask`, `EntailmentTask`,
  `KnapsackTask`, `TspTask`; see `tasks.py`). It carries the instance plus the
  question context (k, fixed values, the requested answer order, the probe, options).
- `params` are the member's own parameters, e.g. `{"order": "LIST", "mode": "ABORT"}`
  for first-fit. Parameterised families (`PRIORITY(order, score, rule)`,
  `SEARCH(b, order, value, default)`) are single registry entries whose parameters
  name the member, as SCOPE §4 asks.

`Prediction.answer` is the member's deterministic answer (a colouring, an assignment,
"YES"/"NO"/"X", an option letter, "UNSAT", "IMPOSSIBLE", ...). Distributional members
(C3, H, nuisance) put their outcome probabilities in `distribution` and may leave
`answer` as None. `trace_features` are the pre-registered trace signature quantities
(commit order, revisions, dead end, ...), computed, not described.

Members are registered with their family, domain and a one-line pre-registered trace
signature (`cot`), taken from the vertical docs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Prediction:
    answer: Any
    trace_features: dict[str, Any] = field(default_factory=dict)
    distribution: dict[str, float] | None = None


@dataclass(frozen=True)
class Member:
    name: str
    family: str
    domain: str
    fn: Callable[[Any, dict[str, Any]], Prediction]
    cot: str
    deterministic: bool = True


REGISTRY: dict[tuple[str, str], Member] = {}


def member(name: str, family: str, domain: str, cot: str, deterministic: bool = True):
    """Decorator registering a member function under (domain, name)."""

    def wrap(fn: Callable[[Any, dict[str, Any]], Prediction]):
        key = (domain, name)
        if key in REGISTRY:
            raise ValueError(f"member {key} registered twice")
        REGISTRY[key] = Member(name, family, domain, fn, cot, deterministic)
        return fn

    return wrap


def get(domain: str, name: str) -> Member:
    _ensure_loaded()
    try:
        return REGISTRY[(domain, name)]
    except KeyError:
        raise KeyError(f"no member {name!r} for domain {domain!r}") from None


def run(domain: str, name: str, task: Any, params: dict[str, Any] | None = None) -> Prediction:
    return get(domain, name).fn(task, dict(params or {}))


_LOADED = False


def _ensure_loaded() -> None:
    global _LOADED
    if _LOADED:
        return
    # Importing the modules registers their members.
    from reasoning_heuristics.heuristics import (  # noqa: F401
        coloring, entailment, etr, knapsack, sat, search, tsp,
    )
    from reasoning_heuristics.heuristics import baselines  # noqa: F401  (A/H cue and nuisance members)

    _LOADED = True


def members_for(domain: str) -> list[Member]:
    _ensure_loaded()
    return [m for (d, _), m in sorted(REGISTRY.items()) if d == domain]
