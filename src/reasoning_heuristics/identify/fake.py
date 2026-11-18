"""Fake models: planted mixtures of zoo members that answer real items (DESIGN §3 O3 step 6).

A fake model is a `Scenario`: per item it picks a member (or q) from planted weights, renormalised
over the members available on that item, and draws the answer from that member's likelihood
(`UnitModel.sample`) under a generating slip model (near-miss or uniform-over-candidates). The
recovery harness then fits the responses and compares the estimates with the planted truth.

Scenario kinds (SCOPE §4 item 5):

- `single`: 100% one member (one scenario per tie group).
- `mix`: 0.6 / 0.3 / 0.1 on three members.
- `feature`: weights that depend on an item feature (two levels): 0.7 / 0.2 / 0.1 on one level,
  0.2 / 0.7 / 0.1 on the other; fitted with the softmax model.
- `null_q`: every answer from q ("none of the above").
- `null_always`: one fixed answer on every item (the first decision value, option A, UNSAT or
  IMPOSSIBLE, the empty set, one colour for every vertex), without slips. Its truth is the group that
  gives that answer on every item if there is one, otherwise q.
- `off_zoo`: 0.3 on a member that the generator has but the fit withholds, 0.7 on another member.
  The question is where the withheld 0.3 goes: to q, or onto zoo members.
- `clustered`: the `mix` weights, but the member is drawn once per cluster (every variant of a base
  answered by the same member), which is what the cluster bootstrap must cope with.
- `truncated`: the `mix` weights, with runs truncated (censored) at a rate that depends on the
  member: 0.4 for the 0.6 member, 0.05 otherwise. Fitted twice: with truncated runs excluded, and
  with the true truncation probabilities as the token model (the hook in `likelihood.py`).

On finite channels (decisions, options, bits) a slip is a mixture with q, so the slip rate is not
identified and the fit counts slips as unexplained mass (`Tensors.slip_identified`); fake models
there plant no slips, so the planted weights are the identifiable ones.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from reasoning_heuristics.identify.likelihood import Observation, UnitModel
from reasoning_heuristics.identify.records import Response
from reasoning_heuristics.identify.spaces import BitSpace, FiniteSpace, PartitionSpace


@dataclass
class Scenario:
    name: str
    kind: str
    weights: dict[str, float] = field(default_factory=dict)  # constant planted weights over member labels
    q: float = 0.0  # planted weight of q
    eps: float = 0.1
    rho: float = 0.3
    level_weights: dict[int, dict[str, float]] | None = None  # feature scenario: weights per level
    always: bool = False  # null_always: answer the fixed answer of `always_answer`
    withheld: list[str] = field(default_factory=list)  # off_zoo: labels removed from the fit
    clustered: bool = False
    truncation: dict[str, float] | None = None  # member label -> P(truncated); others `trunc_default`
    trunc_default: float = 0.05

    def weights_on(self, level: int | None) -> dict[str, float]:
        if self.level_weights is not None:
            return self.level_weights[level]
        return self.weights


def always_answer(um: UnitModel, i: int) -> str:
    """The fixed answer of the ALWAYS responder on item i."""
    space = um.items[i].space
    if isinstance(space, FiniteSpace):
        return space.values[0]
    if space.specials:
        return space.specials[0]
    if isinstance(space, PartitionSpace):
        return space.encode(np.zeros(space.n, dtype=np.int64))
    if isinstance(space, BitSpace):
        return space.encode(np.zeros(space.n, dtype=bool))
    raise TypeError(type(space))


def simulate(um: UnitModel, sc: Scenario, rng: np.random.Generator, levels: np.ndarray | None = None) -> list[Observation]:
    """One fake model's responses to every item of the unit (censored rows for truncated runs).

    `um` is the generating unit model: its slip model is the generating slip model, and it must
    contain every planted member (including withheld ones)."""
    obs: list[Observation] = []
    chosen: dict[int, str | None] = {}
    for i in range(len(um.items)):
        if sc.always:
            obs.append(Observation(i, always_answer(um, i)))
            continue
        w = sc.weights_on(None if levels is None else int(levels[i]))
        avail = [l for l in w if um.pred(i, l).available and w[l] > 0]
        probs = np.array([w[l] for l in avail] + [sc.q], dtype=float)
        if probs.sum() <= 0:
            raise ValueError(f"no planted member is available on item {um.unit.items[i]['item_id']}")
        c = int(um.unit.cluster[i])
        if sc.clustered and c in chosen and (chosen[c] is None or chosen[c] in avail):
            label = chosen[c]
        else:
            j = int(rng.choice(len(probs), p=probs / probs.sum()))
            label = None if j == len(avail) else avail[j]
            chosen[c] = label
        finite = isinstance(um.items[i].space, FiniteSpace)
        eps = 0.0 if finite else sc.eps
        if sc.truncation is not None:
            p_cut = sc.truncation.get(label, sc.trunc_default) if label is not None else sc.trunc_default
            if rng.random() < p_cut:
                obs.append(Observation(i, None))
                continue
        y = um.sample_q(i, rng) if label is None else um.sample(i, label, eps, sc.rho, rng)
        obs.append(Observation(i, y))
    return obs


def to_responses(um: UnitModel, obs: list[Observation], model: str = "fake", condition: str = "thinking") -> list[Response]:
    """Response records for simulated observations (censored rows become `truncated`)."""
    out = []
    for k, ob in enumerate(obs):
        it = um.unit.items[ob.item]
        if ob.censored:
            out.append(Response(it["item_id"], it["content_hash"], model, "truncated", condition=condition, sample=k))
        else:
            out.append(Response(it["item_id"], it["content_hash"], model, "ok", answer_key=ob.key, condition=condition, sample=k))
    return out


def truth_vector(um_fit: UnitModel, weights: dict[str, float], q: float) -> np.ndarray:
    """Planted weights mapped onto the fit's column groups (+ q last); withheld members map nowhere."""
    t = np.zeros(len(um_fit.columns) + 1)
    t[-1] = q
    for label, w in weights.items():
        if label not in um_fit.labels:
            continue  # withheld from the fit
        j = um_fit.column_of(label)
        if j is None:
            t[-1] += w
        else:
            t[j] += w
    return t
