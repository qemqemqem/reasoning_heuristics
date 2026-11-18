"""Error agreement and permutation baselines (DESIGN §3 O3 step 3).

**Error agreement.** EA(h, m) = P(y ~ h(x) | y wrong, h(x) wrong): among items where member h's
answer is wrong and the model's answer is wrong, how often they agree (y ~ h(x): the same answer,
or within `near` of it under the domain distance). Members are taken as tie groups; set-valued and
distributional members have no single wrong answer and get no EA. "Wrong" is judged against the
item's EXACT member (its answer, or its solution set by validity). On a two-valued channel EA is 1
whenever it is defined (both wrong means both give the one wrong value), so the report also gives
co_error = P(y ~ h(x) | h(x) wrong), the rate at which the model makes h's errors.

**Tie handling** (explicit, `ties=`):

- `include`: every group whose wrong answer y matches gets the agreement, shared or not;
- `exclude`: only items where h's wrong answer is h's alone (no other group gives it) count,
  in the numerator and the denominator;
- `split`: an agreement shared by t groups counts 1/t for each.

**Permutation baseline matched on item structure.** Responses are shuffled within cell, among
items whose answer spaces accept the same answers (same decision values or options; same
vertices or variables), so the baseline keeps each cell's answer frequencies but breaks the link
to the item. Lift = observed - mean permuted, with a one-sided permutation p-value. On witness
channels items in a cell rarely share an answer space (each base has its own labels), so there
the baseline is mostly undefined; `exchangeable` reports the share of responses that could move,
and the lift is None when it is below `min_exchangeable`.

The same shuffle gives a baseline for the mixture weights (`permutation_weights`): refit on
permuted responses; lift_h = pi_h - mean permuted pi_h.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

import numpy as np

from reasoning_heuristics.identify.likelihood import Observation, UnitModel
from reasoning_heuristics.identify.mixture import em

TIES = ("include", "exclude", "split")


def _exact_label(item: dict[str, Any]) -> str:
    labels = [l for l, r in item["predictions"].items() if r["member"] == "EXACT"]
    if not labels:
        raise ValueError(f"{item['item_id']}: no EXACT member to judge correctness")
    return labels[0]


def is_correct(um: UnitModel, i: int, key: str) -> bool:
    p = um.pred(i, _exact_label(um.unit.items[i]))
    if p.kind == "det":
        return key == p.key
    if p.kind == "set":
        return p.sol.contains(key)
    if p.kind == "dist":  # e.g. EXACT's projection onto C E3's target bit: any bit a valid colouring has
        return p.dist.get(key, 0.0) > 0
    raise ValueError("EXACT has no prediction on this item")


@dataclass
class EA:
    group: str
    ea: float | None  # P(y ~ h(x) | y wrong, h(x) wrong); None when no item has both wrong
    n: float  # its denominator
    agree: float  # its numerator (fractional under 'split')
    co_error: float | None  # P(y ~ h(x) | h(x) wrong)
    n_h_wrong: float


def error_agreement(um: UnitModel, obs: list[Observation], ties: str = "include", near: int = 0) -> dict[str, EA]:
    """EA per column group, plus co_error = P(y ~ h(x) | h(x) wrong).

    On a two-valued channel (decisions, a bit) EA is 1 whenever it is defined: both wrong means both
    give the one wrong value. There co_error, the rate at which the model makes h's errors, is the
    informative quantity, and the permutation baseline is its chance level."""
    if ties not in TIES:
        raise ValueError(f"ties must be one of {TIES}")
    cols = um.columns
    num, den = defaultdict(float), defaultdict(float)
    co_num, co_den = defaultdict(float), defaultdict(float)
    correct_cache: dict[tuple[int, str], bool] = {}

    def correct(i: int, k: str) -> bool:
        if (i, k) not in correct_cache:
            correct_cache[(i, k)] = is_correct(um, i, k)
        return correct_cache[(i, k)]

    for ob in obs:
        if ob.censored:
            continue
        i, y = ob.item, ob.key
        y_wrong = not correct(i, y)
        space = um.items[i].space
        wrong = {}
        for g in cols:
            p = um.pred(i, g.members[0])
            if p.kind == "det" and not correct(i, p.key):
                wrong[g.name] = p.key
        by_answer = defaultdict(list)
        for name, k in wrong.items():
            by_answer[k].append(name)
        for name, k in wrong.items():
            shared = len(by_answer[k])
            if ties == "exclude" and shared > 1:
                continue
            match = (y == k) if near == 0 else (space.distance(y, k) <= near)
            credit = (1.0 / shared if ties == "split" else 1.0) if match else 0.0
            co_den[name] += 1
            co_num[name] += credit
            if y_wrong:
                den[name] += 1
                num[name] += credit
    return {g.name: EA(g.name, (num[g.name] / den[g.name]) if den[g.name] else None, den[g.name], num[g.name],
                       (co_num[g.name] / co_den[g.name]) if co_den[g.name] else None, co_den[g.name]) for g in cols}


def _exchange_classes(um: UnitModel, obs: list[Observation]) -> dict[tuple, list[int]]:
    classes: dict[tuple, list[int]] = defaultdict(list)
    for n, ob in enumerate(obs):
        it = um.unit.items[ob.item]
        classes[(it["cell"], um.items[ob.item].space.signature())].append(n)
    return classes


def permute_within_cell(um: UnitModel, obs: list[Observation], rng: np.random.Generator) -> tuple[list[Observation], float]:
    """A within-cell shuffle of the answers among items with the same answer space.
    Returns the permuted observations and the share of rows that could move."""
    out = list(obs)
    movable = 0
    for rows in _exchange_classes(um, obs).values():
        live = [n for n in rows if not obs[n].censored]
        if len(live) < 2:
            continue
        movable += len(live)
        keys = [obs[n].key for n in live]
        perm = rng.permutation(len(live))
        for n, j in zip(live, perm):
            out[n] = Observation(obs[n].item, keys[j], obs[n].response)
    return out, movable / max(len(obs), 1)


@dataclass
class Lift:
    name: str
    observed: float | None
    baseline: float | None
    lift: float | None
    p_value: float | None


def ea_lift(um: UnitModel, obs: list[Observation], n_perm: int = 500, rng: np.random.Generator | None = None,
            ties: str = "include", near: int = 0, min_exchangeable: float = 0.5, stat: str = "ea") -> tuple[dict[str, Lift], float]:
    """Lift of EA (`stat="ea"`) or of co_error (`stat="co_error"`) over the within-cell permutation baseline."""
    rng = rng or np.random.default_rng(0)
    observed = {k: getattr(v, stat) for k, v in error_agreement(um, obs, ties, near).items()}
    _, exch = permute_within_cell(um, obs, rng)
    if exch < min_exchangeable:
        return {k: Lift(k, v, None, None, None) for k, v in observed.items()}, exch
    null = defaultdict(list)
    for _ in range(n_perm):
        pobs, _ = permute_within_cell(um, obs, rng)
        for k, v in error_agreement(um, pobs, ties, near).items():
            if getattr(v, stat) is not None:
                null[k].append(getattr(v, stat))
    out = {}
    for k, v in observed.items():
        if v is None or not null[k]:
            out[k] = Lift(k, v, None, None, None)
            continue
        arr = np.array(null[k])
        out[k] = Lift(k, v, float(arr.mean()), float(v - arr.mean()), float((1 + (arr >= v).sum()) / (1 + len(arr))))
    return out, exch


def permutation_weights(um: UnitModel, obs: list[Observation], pi_hat: np.ndarray, n_perm: int = 100,
                        rng: np.random.Generator | None = None, min_exchangeable: float = 0.5) -> tuple[dict[str, Lift], float]:
    """Mixture-weight baseline: refit (point estimates) on within-cell shuffled answers."""
    rng = rng or np.random.default_rng(0)
    labels = [g.name for g in um.columns] + ["unexplained (q)"]
    _, exch = permute_within_cell(um, obs, rng)
    if exch < min_exchangeable:
        return {l: Lift(l, float(p), None, None, None) for l, p in zip(labels, pi_hat)}, exch
    perms = []
    for _ in range(n_perm):
        pobs, _ = permute_within_cell(um, obs, rng)
        perms.append(em(um.tensors(pobs)).pi[0])
    arr = np.array(perms)
    base = arr.mean(0)
    return {l: Lift(l, float(p), float(b), float(p - b), float((1 + (arr[:, j] >= p).sum()) / (1 + len(arr))))
            for j, (l, p, b) in enumerate(zip(labels, pi_hat, base))}, exch
