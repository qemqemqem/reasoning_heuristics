"""Shared machinery for every generator: run the members, build the likelihood-ratio table and
hypothesis blocks, and assemble schema items.

Likelihood model (stated on every item, `Item.likelihood_model`):

- outcome classes are the distinct answers of the deterministic members on the item's
  scoring channel, plus "other";
- a deterministic member puts 1 - eps on its own answer and spreads eps over the other
  classes (eps = 0.1, the slip floor);
- a distributional member uses its own distribution (mass on answers outside the listed
  classes goes to "other"), mixed with the same slip floor;
- a set-valued member (EXACT on witness tasks; uniform fills) spreads 1 - eps uniformly
  over its solution set, using the set size the generator passes in;
- disconfirms[o][h] = log10 max_h' P(o|h') - log10 P(o|h): positive = evidence against h.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any, Callable

from reasoning_heuristics.hashing import sha, to_jsonable
from reasoning_heuristics.heuristics.answers import answer_key
from reasoning_heuristics.heuristics.base import get, run
from reasoning_heuristics.schema.item import Item
from reasoning_heuristics.seeds import TIERS

EPS = 0.1

MemberSpec = tuple[str, str, dict[str, Any]]  # (label shown on the item, registry name, params)


def predict_all(task: Any, specs: list[MemberSpec]) -> dict[str, dict[str, Any]]:
    out = {}
    for label, name, params in specs:
        m = get(task.domain, name)
        pred = run(task.domain, name, task, params)
        out[label] = {
            "member": name,
            "family": m.family,
            "params": to_jsonable(params),
            "answer": to_jsonable(pred.answer),
            "trace_features": to_jsonable(pred.trace_features),
            "distribution": to_jsonable(pred.distribution) if pred.distribution is not None else None,
        }
    return out


@dataclass
class Channel:
    """How answers are compared for likelihoods: `key(answer) -> class or None`."""

    name: str
    key: Callable[[Any], str | None]
    set_valued: dict[str, tuple[Callable[[str], bool], int]] = field(default_factory=dict)  # label -> (is_member, size)


def witness_channel(domain: str, set_valued: dict | None = None) -> Channel:
    return Channel("answer", lambda a: answer_key(domain, a) if a is not None else None, set_valued or {})


def decision_channel(positive: str, negative: str, set_valued: dict | None = None) -> Channel:
    """Map witness answers to the decision they claim (e.g. any assignment -> SAT)."""

    def key(a: Any) -> str | None:
        if a is None:
            return None
        if isinstance(a, str):
            return {"X": negative}.get(a, a)
        return positive

    return Channel("decision", key, set_valued or {})


def disconfirms(preds: dict[str, dict[str, Any]], channel: Channel, eps: float = EPS) -> tuple[dict[str, dict[str, float]], dict[str, str]]:
    """The item's log10-LR table (positive = against) and a map outcome label -> answer class."""
    classes: dict[str, list[str]] = {}
    for label, rec in preds.items():
        if label in channel.set_valued:
            continue
        k = channel.key(rec["answer"])
        if k is not None:
            classes.setdefault(k, []).append(label)
    keys = list(classes) + ["_other"]
    K = len(keys)
    probs: dict[str, dict[str, float]] = {}
    for label, rec in preds.items():
        p = {k: 0.0 for k in keys}
        if label in channel.set_valued:
            is_member, size = channel.set_valued[label]
            listed = [k for k in keys[:-1] if is_member(k)]
            for k in listed:
                p[k] = 1.0 / size
            p["_other"] = max(0.0, 1.0 - len(listed) / size)
        elif channel.key(rec["answer"]) is not None:
            p[channel.key(rec["answer"])] = 1.0
        elif rec.get("distribution"):
            for k, v in rec["distribution"].items():
                if k == "_exact" and "EXACT" in channel.set_valued:
                    # slip models: the "_exact" mass is spread like EXACT's solution set
                    is_member, size = channel.set_valued["EXACT"]
                    listed = [c for c in keys[:-1] if is_member(c)]
                    for c in listed:
                        p[c] += v / size
                    p["_other"] += v * max(0.0, 1.0 - len(listed) / size)
                    continue
                kk = k if k in p else "_other"
                p[kk] += v
        else:
            continue  # no prediction on this channel (e.g. a member that is n/a here)
        probs[label] = {k: (1 - eps) * v + eps / K for k, v in p.items()}
    table: dict[str, dict[str, float]] = {}
    outcome_of: dict[str, str] = {}
    for k in keys:
        label = "answer = other" if k == "_other" else f"answer = {' / '.join(classes[k])}'s prediction"
        if k != "_other" and len(k) <= 12:
            label = f"answer = {k}"
        best = max(pr[k] for pr in probs.values())
        table[label] = {h: round(math.log10(best) - math.log10(pr[k]), 2) for h, pr in probs.items()}
        outcome_of[label] = k
    return table, outcome_of


def render_answer(domain: str, answer: Any) -> str:
    if answer is None:
        return "distribution (see predictions)"
    if isinstance(answer, str):
        return answer
    if domain == "coloring":
        return answer_key(domain, answer).replace("|", " | ").replace(",", " ")
    if domain == "sat":
        return " ".join(f"{k}={'T' if v else 'F'}" for k, v in answer.items())
    return str(answer)


def hypotheses(domain: str, preds: dict[str, dict[str, Any]], roles: dict[str, str], cell_note: str) -> dict[str, Any]:
    out = {}
    for label, rec in preds.items():
        m = get(domain, rec["member"])
        dist = rec.get("distribution")
        output = render_answer(domain, rec["answer"])
        if rec["answer"] is None and dist:
            top = sorted(dist.items(), key=lambda kv: -kv[1])[:3]
            output = "; ".join(f"P({k[:40]}) = {v:.2f}" for k, v in top)
        if rec["answer"] is not None:
            rate = f"p_h(answer = its prediction) = {1 - EPS:.2f} with slip eps = {EPS}"
        elif dist:
            rate = "p_h(outcome) = its distribution, mixed with slip eps = " + str(EPS)
        else:
            rate = "set-valued: uniform over its solution set"
        out[label] = {
            "family": rec["family"],
            "output": output,
            "eval_prediction": " ".join(x for x in (roles.get(label, ""), rate + "; the cell rate is Σ_h π_h·p_h.", cell_note) if x),
            "cot_prediction": m.cot,
        }
    return out


def trace_predictions(domain: str, preds: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {label: {"signature": get(domain, rec["member"]).cot, **rec["trace_features"]} for label, rec in preds.items()}


def distinct_answers(preds: dict[str, dict[str, Any]], channel: Channel) -> int:
    return len({channel.key(r["answer"]) for lbl, r in preds.items() if lbl not in channel.set_valued and channel.key(r["answer"]) is not None})


def item_id(vertical: str, eval_id: str, set_id: str, cell: str) -> str:
    v = vertical.replace("/", "")
    c = re.sub(r"[\s/|]+", "_", cell).strip("_")  # keep symbols such as ·, ′, →, ¬: they distinguish cells
    return f"{v}-{eval_id}-{set_id}-{c}"


def make_item(*, vertical: str, eval_id: str, set_id: str, cell: str, domain: str, framing: str, prompt: str,
              answer_format: str, task: Any, ground_truth: dict[str, Any], specs: list[MemberSpec],
              channel: Channel, seed: int, tier: str, generator: str, base_hash: str,
              source_hash: str | None = None, pair_id: str | None = None, params: dict[str, Any] | None = None,
              notes: str = "", roles: dict[str, str] | None = None, cell_note: str = "",
              extra: dict[str, Any] | None = None) -> Item:
    preds = predict_all(task, specs)
    table, outcomes = disconfirms(preds, channel)
    it = Item(
        item_id=item_id(vertical, eval_id, set_id, cell),
        vertical=vertical,
        eval_id=eval_id,
        set_id=set_id,
        pair_id=pair_id,
        cell=cell,
        domain=domain,
        framing=framing,
        prompt=prompt,
        answer_format=answer_format,
        ground_truth=to_jsonable(ground_truth),
        predictions=preds,
        instance=task.to_json(),
        params=to_jsonable(params or {}),
        trace_predictions=trace_predictions(task.domain, preds),
        hypotheses=hypotheses(task.domain, preds, roles or {}, cell_note),
        disconfirms=table,
        notes=notes,
        likelihood_model=(f"channel={channel.name}; outcome classes = distinct deterministic answers + other; "
                          f"slip eps={EPS}; disconfirms[o][h] = log10 max_h' P(o|h') - log10 P(o|h), positive = against h"),
        base_hash=base_hash,
        source_hash=source_hash,
        seed=seed,
        split=TIERS[tier].split,
        tier=tier,
        generator=generator,
        extra={"outcome_classes": outcomes, "channel": channel.name, **(extra or {})},
    )
    it.finalise_hashes(task.content_key())
    return it


@dataclass
class GenStats:
    attempts: int = 0
    accepted: int = 0
    rejections: dict[str, int] = field(default_factory=dict)

    def reject(self, reason: str) -> None:
        self.rejections[reason] = self.rejections.get(reason, 0) + 1

    def to_json(self) -> dict[str, Any]:
        return {"attempts": self.attempts, "accepted": self.accepted, "rejections": dict(sorted(self.rejections.items()))}


def short(h: str) -> str:
    return h[:8]


def set_hash(*parts: Any) -> str:
    return sha(list(parts))[:10]
