"""Shared machinery for every generator: run the members, build the likelihood-ratio table and
hypothesis blocks, and assemble schema items.

Likelihood model. The table is a *uniform-slip preview*: it shows what each item can tell
apart. The identification engine computes its own likelihoods (with near-miss slips and a
fitted slip rate, SCOPE §6 rule 3) from the raw answers, using the serialised channel below.

Outcome classes, on the item's scoring channel (`extra.outcome_classes`: label -> class key):

- every distinct channel value a deterministic member predicts, plus the channel's declared
  answers (both decisions on a decision channel; UNSAT / IMPOSSIBLE where the format allows
  them; same / different on the C E3 bit channel);
- a set-valued member whose solution set has one element is deterministic: that solution is a
  class of its own;
- on a witness channel, the *unlisted* members of the solution sets form their own classes,
  one per combination of sets they belong to (key "_in:<labels>"), so a valid answer no member
  listed is never pooled with an invalid one;
- "_other": an answer that is none of these (not listed, and in no solution set).

Probabilities before the slip, p_h(o):

- deterministic member: 1 on its class; an answer with no reading on the channel (IMPOSSIBLE
  on the C E3 bit channel) is "other";
- distributional member: its own distribution, each answer key sent to its class (listed, an
  unlisted-solution class by set membership, or other); "_exact" mass is spread like the exact
  solver's prediction, and an untracked remainder ("_other") goes to other;
- set-valued member (`SetSpec`: membership rule, parameters, set size): uniform over its set.
  A listed answer in the set gets 1/size and an unlisted-solution class gets its share of the
  set; on a non-witness channel the set's class counts give p_h directly. A uniform fill whose
  mass on every listed answer and solution set is negligible puts it all on other.

Slip: P(o|h) = (1 - eps)·p_h(o) + eps/K over the item's K outcome classes, eps = 0.1. So a
deterministic member puts 1 - eps + eps/K on its own class and eps/K on each other class. This
one lapse formula is used for every kind of member (a deterministic member is the point-mass
case of a distributional one, so the two get identical rows when they agree); the docs follow
the code.

disconfirms[o][h] = log10 max_h' P(o|h') - log10 P(o|h): positive = evidence against h.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from functools import lru_cache
from itertools import combinations
from typing import Any, Callable

from reasoning_heuristics.hashing import sha, to_jsonable
from reasoning_heuristics.heuristics.answers import answer_key
from reasoning_heuristics.heuristics.base import get, run
from reasoning_heuristics.schema.item import Item
from reasoning_heuristics.seeds import TIERS

EPS = 0.1
OTHER = "_other"
REGION = "_in:"  # prefix of an unlisted-solution class key
PREVIEW = ("uniform-slip preview: P(o|h) = (1 - eps)·p_h(o) + eps/K over the K outcome classes; the identification "
           "engine computes its own likelihoods (near-miss slips, fitted slip rate) from raw answers")

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


# --- solution sets: membership rules ---------------------------------------------------------------
#
# A rule decides whether an answer key belongs to a set-valued member's solution set. Rules are
# named and parameterised so that the scorer, the validators and the identification engine can
# rebuild the set from the item alone (`extra.channel_spec`).


@lru_cache(maxsize=256)
def _graph(task: Any, which: str):
    from reasoning_heuristics.heuristics.coloring import effective_graph

    return effective_graph(task) if which == "stated" else task.graph


@lru_cache(maxsize=256)
def _cnf(task: Any, which: str):
    from reasoning_heuristics.heuristics.sat import effective_cnf

    return effective_cnf(task) if which == "stated" else task.cnf


@lru_cache(maxsize=256)
def _knap_optimum(knapsack: Any, covering: bool) -> int:
    from reasoning_heuristics.problems.knapsack.knapsack import solve_covering_dp, solve_dp

    return (solve_covering_dp(knapsack) if covering else solve_dp(knapsack))[0]


def rule_colouring(task: Any, key: str, graph: str = "stated", colours: int = 0, exactly: bool = False) -> bool:
    """A proper colouring (as a partition key) of the stated or textbook graph with exactly /
    at most `colours` classes, consistent with the task's fixed colours up to renaming."""
    if not key or "=" in key:
        return False
    g = _graph(task, graph)
    classes = [c.split(",") for c in key.split("|")]
    flat = [v for c in classes for v in c]
    if len(flat) != len(set(flat)) or set(flat) != set(g.vertices):
        return False
    if (len(classes) != colours) if exactly else (len(classes) > colours):
        return False
    if any(g.has_edge(u, v) for c in classes for i, u in enumerate(c) for v in c[i + 1:]):
        return False
    cls_of = {v: i for i, c in enumerate(classes) for v in c}
    colour_of: dict[int, int] = {}
    for v, c in task.fixed:
        if colour_of.setdefault(cls_of[v], c) != c:
            return False
    return len(set(colour_of.values())) == len(colour_of)


def rule_assignment(task: Any, key: str, cnf: str = "stated") -> bool:
    """A complete assignment key satisfying the stated or textbook formula and the fixed values."""
    from reasoning_heuristics.problems.sat.cnf import satisfies

    if not key or "=" not in key:
        return False
    a = {}
    for kv in key.split(","):
        name, _, val = kv.partition("=")
        a[name] = val == "T"
    c = _cnf(task, cnf)
    if set(a) != set(c.var_names) or any(a[v] != b for v, b in task.fixed):
        return False
    return satisfies(c, a)


def rule_subset(task: Any, key: str, objective: str = "stated") -> bool:
    """An optimal subset under the stated objective (covering when the task inverts it) or the
    textbook one (packing)."""
    k = task.knapsack
    names = [x for x in key.split(",") if x] if key else []
    if len(set(names)) != len(names) or set(names) - set(k.names):
        return False
    covering = task.covering if objective == "stated" else False
    return k.feasible(names, covering=covering) and k.value_of(names) == _knap_optimum(k, covering)


RULES: dict[str, Callable[..., bool]] = {"colouring": rule_colouring, "assignment": rule_assignment, "subset": rule_subset}


@dataclass(frozen=True)
class SetSpec:
    """A set-valued member's prediction: uniform over a solution set.

    `rule` names a membership rule in RULES (or "fill" for a uniform fill), `params` are its
    arguments, `size` the number of distinct answer keys in the set. `solution` is the answer key
    when size == 1 (the member is then deterministic). `class_counts` gives, on a non-witness
    channel, how many set elements fall in each channel class (sums to `size`)."""

    rule: str
    params: dict[str, Any]
    size: int
    description: str
    solution: str | None = None
    class_counts: dict[str, int] | None = None

    def __post_init__(self) -> None:
        if self.size < 1:
            raise ValueError(f"empty solution set ({self.description}): the member is deterministic here")
        if self.rule not in RULES and self.class_counts is None:
            raise ValueError(f"unknown membership rule {self.rule!r}")
        if self.class_counts is not None and sum(self.class_counts.values()) != self.size:
            raise ValueError(f"class counts {self.class_counts} do not sum to the set size {self.size}")
        if self.class_counts is None and self.size == 1 and self.solution is None:
            raise ValueError(f"a one-element set needs its solution ({self.description})")

    def contains(self, task: Any, key: str) -> bool:
        return RULES[self.rule](task, key, **self.params)

    def to_json(self) -> dict[str, Any]:
        return to_jsonable({"rule": self.rule, "params": self.params, "size": self.size, "description": self.description,
                            "solution": self.solution, "class_counts": self.class_counts})

    @classmethod
    def from_json(cls, d: dict[str, Any]) -> "SetSpec":
        return cls(d["rule"], d["params"], d["size"], d["description"], d.get("solution"), d.get("class_counts"))


def uniform_fill(description: str, bound: float) -> SetSpec:
    """A member uniform over the whole answer space (RANDOM on a witness channel): its mass on
    every listed answer and solution set is below `bound`, so all of it is put on other."""
    return SetSpec("fill", {"mass_outside_other_below": bound}, 1, description, class_counts={OTHER: 1})


# --- channels ----------------------------------------------------------------------------------------


@dataclass
class Channel:
    """How answers are compared for likelihoods: `key(answer) -> class or None`.

    `set_valued` maps member labels to their solution sets; `values` are answers that are always
    outcome classes; `overlaps` gives |S_a ∩ S_b| for pairs of solution sets on one item (needed
    to size the unlisted-solution classes); `task` evaluates membership; `spec` holds what
    `channel_from_json` needs to rebuild the channel."""

    name: str
    key: Callable[[Any], str | None]
    set_valued: dict[str, SetSpec] = field(default_factory=dict)
    values: tuple[str, ...] = ()
    overlaps: dict[frozenset, int] = field(default_factory=dict)
    task: Any = None
    spec: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> dict[str, Any]:
        return to_jsonable({"name": self.name, **self.spec, "values": list(self.values),
                            "set_valued": {lbl: s.to_json() for lbl, s in self.set_valued.items()},
                            "overlaps": [[*sorted(pair), n] for pair, n in sorted(self.overlaps.items(), key=lambda kv: sorted(kv[0]))]})


def _sets_arg(set_valued: dict | None) -> dict[str, SetSpec]:
    out = {}
    for label, spec in (set_valued or {}).items():
        if not isinstance(spec, SetSpec):
            raise TypeError(f"{label}: set-valued members take a SetSpec (rule, params, size), not {type(spec).__name__}")
        out[label] = spec
    return out


def _overlaps_arg(overlaps: dict | None) -> dict[frozenset, int]:
    return {frozenset(pair): int(n) for pair, n in (overlaps or {}).items()}


def witness_channel(domain: str, set_valued: dict | None = None, task: Any = None, values: tuple[str, ...] = (),
                    overlaps: dict | None = None) -> Channel:
    sv = _sets_arg(set_valued)
    if task is None and any(s.class_counts is None and s.size > 1 for s in sv.values()):
        raise ValueError("a witness channel with solution sets needs the task (for set membership)")
    return Channel("answer", lambda a: answer_key(domain, a) if a is not None else None, sv, tuple(values),
                   _overlaps_arg(overlaps), task, {"domain": domain})


def decision_channel(positive: str, negative: str, set_valued: dict | None = None) -> Channel:
    """Map witness answers to the decision they claim (e.g. any assignment -> SAT)."""

    def key(a: Any) -> str | None:
        if a is None:
            return None
        if isinstance(a, str):
            return {"X": negative}.get(a, a)
        return positive

    return Channel("decision", key, _sets_arg(set_valued), (positive, negative), {}, None,
                   {"positive": positive, "negative": negative})


def target_bit_channel(target: str, ref: str, set_valued: dict | None = None) -> Channel:
    """C E3 U arms: does the target share a colour with the reference (first-listed) vertex?
    A non-colouring answer (IMPOSSIBLE) has no reading and is class other."""

    def key(a: Any) -> str | None:
        if not isinstance(a, dict):
            return None
        return "same" if a[target] == a[ref] else "different"

    return Channel("target-bit", key, _sets_arg(set_valued), ("same", "different"), {}, None,
                   {"target": target, "reference": ref})


def target_colour_channel(target: str, set_valued: dict | None = None) -> Channel:
    """C E3 I arm: the colour number given to the target."""
    return Channel("target-colour", lambda a: str(a[target]) if isinstance(a, dict) else None, _sets_arg(set_valued),
                   (), {}, None, {"target": target})


def channel_from_json(spec: dict[str, Any], task: Any) -> Channel:
    """Rebuild an item's channel from `extra.channel_spec` and its task."""
    sv = {lbl: SetSpec.from_json(s) for lbl, s in spec.get("set_valued", {}).items()}
    name = spec["name"]
    if name == "answer":
        return witness_channel(spec["domain"], sv, task, tuple(spec.get("values", ())),
                               {(a, b): n for a, b, n in spec.get("overlaps", [])})
    if name == "decision":
        return decision_channel(spec["positive"], spec["negative"], sv)
    if name == "target-bit":
        return target_bit_channel(spec["target"], spec["reference"], sv)
    if name == "target-colour":
        return target_colour_channel(spec["target"], sv)
    raise ValueError(f"unknown channel {name!r}")


DECISIONS = {"sat": ("SAT", "UNSAT"), "coloring": ("POSSIBLE", "IMPOSSIBLE"), "entailment": ("YES", "NO")}


def item_channel(item: dict[str, Any] | Item) -> Channel:
    """The scoring channel of a stored item: rebuilt from `extra.channel_spec`, or, for items
    written before it existed, from the channel name and params (no solution sets)."""
    from reasoning_heuristics.heuristics.tasks import load_task

    d = item.to_json() if isinstance(item, Item) else item
    task = load_task(d["instance"])
    extra = d.get("extra") or {}
    if "channel_spec" in extra:
        return channel_from_json(extra["channel_spec"], task)
    name = extra.get("channel")
    if name == "decision":
        return decision_channel(*DECISIONS[task.domain])
    if name == "answer":
        return witness_channel(task.domain)
    if name == "target-bit":
        return target_bit_channel(d["params"]["target"], d["params"]["reference_vertex"])
    if name == "target-colour":
        return target_colour_channel(d["params"]["target"])
    raise ValueError(f"{d.get('item_id')}: unknown channel {name!r}")


# --- outcome classes and the likelihood table ---------------------------------------------------------


@dataclass
class LikelihoodTable:
    keys: list[str]  # outcome class keys, in table order (OTHER last)
    labels: dict[str, str]  # key -> row label
    probs: dict[str, dict[str, float]]  # member label -> {key: P(o|h)} (after the slip)
    kinds: dict[str, str]  # member label -> deterministic | distribution | set | unique | counts | fill
    regions: dict[str, tuple[str, ...]]  # unlisted-solution class key -> the set labels it lies in
    eps: float

    @property
    def K(self) -> int:
        return len(self.keys)

    def table(self) -> dict[str, dict[str, float]]:
        out = {}
        for k in self.keys:
            best = max(pr[k] for pr in self.probs.values())
            out[self.labels[k]] = {h: round(math.log10(best) - math.log10(pr[k]), 2) for h, pr in self.probs.items()}
        return out

    def outcome_classes(self) -> dict[str, str]:
        return {self.labels[k]: k for k in self.keys}


class _Sets:
    """The distinct solution sets of one item's witness channel (identical sets merged)."""

    def __init__(self, channel: Channel):
        self.channel = channel
        real = {lbl: s for lbl, s in channel.set_valued.items() if s.class_counts is None and s.size > 1}
        groups: list[list[str]] = []
        for lbl in real:
            for g in groups:
                n = channel.overlaps.get(frozenset((lbl, g[0])))
                if n is not None and n == real[lbl].size == real[g[0]].size:
                    g.append(lbl)
                    break
            else:
                groups.append([lbl])
        if len(groups) > 2:
            raise ValueError("more than two distinct solution sets on one item: their region sizes need inclusion-exclusion "
                             "beyond pairwise overlaps")
        self.groups = [tuple(sorted(g)) for g in groups]
        self.size = {g: real[g[0]].size for g in self.groups}
        self.overlap = 0
        if len(self.groups) == 2:
            a, b = self.groups
            n = channel.overlaps.get(frozenset((a[0], b[0])))
            if n is None:
                raise ValueError(f"solution sets of {a[0]} and {b[0]} need a declared overlap (|S_a ∩ S_b|)")
            self.overlap = n
        self.group_of = {lbl: g for g in self.groups for lbl in g}
        self._memo: dict[str, tuple] = {}

    def signature(self, key: str) -> tuple:
        if key not in self._memo:
            spec = self.channel.set_valued
            self._memo[key] = tuple(g for g in self.groups if spec[g[0]].contains(self.channel.task, key))
        return self._memo[key]

    def region_sizes(self, listed: list[str]) -> dict[tuple, int]:
        """Unlisted elements per membership signature (non-empty signatures only)."""
        if len(self.groups) == 1:
            full = {(self.groups[0],): self.size[self.groups[0]]}
        elif len(self.groups) == 2:
            a, b = self.groups
            full = {(a,): self.size[a] - self.overlap, (b,): self.size[b] - self.overlap, (a, b): self.overlap}
        else:
            full = {}
        for k in listed:
            sig = self.signature(k)
            if sig:
                full[sig] -= 1
        for sig, n in full.items():
            if n < 0:
                raise ValueError(f"listed answers exceed the declared size of the set(s) {sig}: check the set sizes")
        return {sig: n for sig, n in full.items() if n > 0}


def region_key(sig: tuple) -> str:
    return REGION + "+".join(lbl for g in sig for lbl in g)


def _label_for(key: str, members: list[str]) -> str:
    if len(key) <= 12 or not members:
        return f"answer = {key}"
    return f"answer = {' / '.join(members)}'s prediction"


def _region_label(sig: tuple, channel: Channel) -> str:
    names = [" = ".join(g) for g in sig]
    desc = channel.set_valued[sig[0][0]].description if len(sig) == 1 else "in both sets"
    return f"answer = unlisted, in {' and '.join(names)}'s solution set ({desc})"


def likelihood_table(preds: dict[str, dict[str, Any]], channel: Channel, eps: float = EPS) -> LikelihoodTable:
    sv = channel.set_valued
    unknown = sorted(set(sv) - set(preds))
    if unknown:
        raise ValueError(f"set-valued specs for members that are not listed: {unknown} (labels must match the item's)")
    listed: dict[str, list[str]] = {}
    for label, rec in preds.items():
        if label in sv:
            s = sv[label]
            if s.class_counts is None and s.size == 1:
                listed.setdefault(s.solution, []).append(label)
            continue
        k = channel.key(rec["answer"]) if rec["answer"] is not None else None
        if k is not None:
            listed.setdefault(k, []).append(label)
    for v in channel.values:
        listed.setdefault(v, [])
    for s in sv.values():
        for c in s.class_counts or {}:
            if c != OTHER:
                listed.setdefault(c, [])
    sets = _Sets(channel) if channel.name == "answer" else None
    region_of: dict[tuple, int] = sets.region_sizes(list(listed)) if sets else {}
    keys = list(listed) + [region_key(sig) for sig in region_of] + [OTHER]
    labels = {k: _label_for(k, listed[k]) for k in listed}
    labels.update({region_key(sig): _region_label(sig, channel) for sig in region_of})
    labels[OTHER] = "answer = other"
    if len(set(labels.values())) != len(labels):
        labels = {k: (lbl if list(labels.values()).count(lbl) == 1 else f"{lbl} [{k}]") for k, lbl in labels.items()}

    def classify(answer_key_: str) -> str:
        if answer_key_ in listed:
            return answer_key_
        if sets is not None:
            sig = sets.signature(answer_key_)
            if sig in region_of:
                return region_key(sig)
            if sig:
                raise ValueError(f"answer {answer_key_[:40]!r} lies in solution set(s) {sig} with no unlisted element left: "
                                 "the declared set sizes are inconsistent")
        return OTHER

    def set_mass(label: str) -> dict[str, float]:
        s = sv[label]
        p = {k: 0.0 for k in keys}
        if s.class_counts is not None:
            for c, n in s.class_counts.items():
                p[c if c in p else OTHER] += n / s.size
        elif s.size == 1:
            p[s.solution] = 1.0
        else:
            g = sets.group_of[label]
            for k in listed:
                if g in sets.signature(k):
                    p[k] = 1.0 / s.size
            for sig, n in region_of.items():
                if g in sig:
                    p[region_key(sig)] = n / s.size
        return p

    exact = [lbl for lbl, rec in preds.items() if rec["member"] == "EXACT"]
    probs: dict[str, dict[str, float]] = {}
    kinds: dict[str, str] = {}
    for label, rec in preds.items():
        p = {k: 0.0 for k in keys}
        if label in sv:
            s = sv[label]
            p = set_mass(label)
            kinds[label] = ("fill" if set(s.class_counts) == {OTHER} else "counts") if s.class_counts is not None else (
                "unique" if s.size == 1 else "set")
        elif rec["answer"] is not None:
            k = channel.key(rec["answer"])
            p[k if k is not None else OTHER] = 1.0
            kinds[label] = "deterministic"
        elif rec.get("distribution"):
            for k, v in rec["distribution"].items():
                if k == "_exact":
                    if len(exact) != 1:
                        raise ValueError(f"{label}: '_exact' mass needs exactly one EXACT member on the item, found {exact}")
                    e = exact[0]
                    if e in sv:
                        for kk, vv in set_mass(e).items():
                            p[kk] += v * vv
                    else:
                        ek = channel.key(preds[e]["answer"])
                        p[ek if ek is not None else OTHER] += v
                elif k == OTHER:
                    p[OTHER] += v
                else:
                    ck = channel.key(k)
                    p[classify(ck) if ck is not None else OTHER] += v
            kinds[label] = "distribution"
        else:
            raise ValueError(f"member {label!r} has no prediction on the {channel.name} channel (no answer, distribution "
                             "or solution set): every listed member needs a row")
        total = sum(p.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"member {label!r}: probabilities sum to {total}, not 1")
        K = len(keys)
        probs[label] = {k: (1 - eps) * v + eps / K for k, v in p.items()}
    regions = {region_key(sig): tuple(lbl for g in sig for lbl in g) for sig in region_of}
    return LikelihoodTable(keys, labels, probs, kinds, regions, eps)


def disconfirms(preds: dict[str, dict[str, Any]], channel: Channel, eps: float = EPS) -> tuple[dict[str, dict[str, float]], dict[str, str]]:
    """The item's log10-LR table (positive = against) and a map outcome label -> class key."""
    lt = likelihood_table(preds, channel, eps)
    return lt.table(), lt.outcome_classes()


def classify_answer(channel: Channel, class_keys: set[str] | list[str], answer: Any) -> str:
    """The outcome-class key of a parsed answer on an item (the scorer's readout): its channel
    value when that is a class, else the unlisted-solution class of the sets that contain it,
    else other."""
    value = channel.key(answer) if answer is not None else None
    if value is None:
        return OTHER
    if value in class_keys:
        return value
    if channel.name == "answer" and any(k.startswith(REGION) for k in class_keys):
        sig = _Sets(channel).signature(value)
        if sig:
            rk = region_key(sig)
            if rk not in class_keys:
                raise ValueError(f"answer {value!r} lies in solution set(s) {sig} that have no unlisted class: "
                                 "the stored set sizes are inconsistent")
            return rk
    return OTHER


# --- hypotheses and traces -----------------------------------------------------------------------------


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


def _rate_text(lt: LikelihoodTable, label: str, channel: Channel) -> str:
    eps, K = lt.eps, lt.K
    own = 1 - eps + eps / K
    kind = lt.kinds[label]
    slip = f"uniform slip eps = {eps} over the K = {K} outcome classes"
    if kind == "deterministic":
        return f"p_h(its class) = 1 - eps + eps/K = {own:.3f}, eps/K = {eps / K:.3f} on each other class ({slip})"
    if kind == "unique":
        s = channel.set_valued[label]
        return f"set-valued with a unique solution ({s.description}): deterministic, p_h(its solution) = {own:.3f} ({slip})"
    if kind == "set":
        s = channel.set_valued[label]
        return (f"set-valued: uniform over its {s.size} solutions ({s.description}); a listed solution gets "
                f"(1 - eps)/{s.size} + eps/K, its unlisted solutions form their own class ({slip})")
    if kind == "counts":
        s = channel.set_valued[label]
        shares = ", ".join(f"{'other' if c == OTHER else c}: {n / s.size:.3f}" for c, n in s.class_counts.items())
        if s.rule == "fill":
            return f"uniform over all answers ({s.description}); on this channel {shares} ({slip})"
        return f"set-valued: uniform over its {s.size} solutions ({s.description}), which give {shares} ({slip})"
    if kind == "fill":
        s = channel.set_valued[label]
        return (f"uniform over all answers ({s.description}): mass on listed answers and solution sets "
                f"< {s.params['mass_outside_other_below']:.1e}, so p_h(other) = 1 ({slip})")
    return f"p_h(outcome) = (1 - eps)·its distribution + eps/K ({slip})"


def hypotheses(domain: str, preds: dict[str, dict[str, Any]], roles: dict[str, str], cell_note: str,
               lt: LikelihoodTable, channel: Channel) -> dict[str, Any]:
    out = {}
    for label, rec in preds.items():
        m = get(domain, rec["member"])
        dist = rec.get("distribution")
        output = render_answer(domain, rec["answer"])
        if label in channel.set_valued:
            s = channel.set_valued[label]
            if s.rule == "fill":
                output = s.description
            else:
                output = f"any of {s.size} solutions ({s.description})" if s.size > 1 else f"its unique solution ({s.solution})"
        elif rec["answer"] is None and dist:
            top = sorted(dist.items(), key=lambda kv: -kv[1])[:3]
            output = "; ".join(f"P({k[:40]}) = {v:.2f}" for k, v in top)
        rate = _rate_text(lt, label, channel)
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
    """Distinct deterministic classes on the channel (unique-solution set members included)."""
    return len({k for k, lbls in _listed(preds, channel).items() if lbls})


def _listed(preds: dict[str, dict[str, Any]], channel: Channel) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for lbl, r in preds.items():
        s = channel.set_valued.get(lbl)
        if s is not None:
            if s.class_counts is None and s.size == 1:
                out.setdefault(s.solution, []).append(lbl)
            continue
        k = channel.key(r["answer"]) if r["answer"] is not None else None
        if k is not None:
            out.setdefault(k, []).append(lbl)
    return out


def item_id(vertical: str, eval_id: str, set_id: str, cell: str) -> str:
    v = vertical.replace("/", "")
    c = re.sub(r"[\s/|]+", "_", cell).strip("_")  # keep symbols such as ·, ′, →, ¬: they distinguish cells
    return f"{v}-{eval_id}-{set_id}-{c}"


def content_hash(task: Any) -> str:
    """The content hash an item built on `task` gets (lineage fields reference these)."""
    return sha(task.content_key())


def make_item(*, vertical: str, eval_id: str, set_id: str, cell: str, domain: str, framing: str, prompt: str,
              answer_format: str, task: Any, ground_truth: dict[str, Any], specs: list[MemberSpec],
              channel: Channel, seed: int, tier: str, generator: str, base_hash: str,
              source_hash: str | None = None, pair_id: str | None = None, params: dict[str, Any] | None = None,
              notes: str = "", roles: dict[str, str] | None = None, cell_note: str = "",
              extra: dict[str, Any] | None = None) -> Item:
    preds = predict_all(task, specs)
    if channel.task is not None and channel.task != task:
        raise ValueError(f"{cell}: the channel was built for another task (its solution sets would be wrong)")
    lt = likelihood_table(preds, channel)
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
        hypotheses=hypotheses(task.domain, preds, roles or {}, cell_note, lt, channel),
        disconfirms=lt.table(),
        notes=notes,
        likelihood_model=(f"channel={channel.name}; outcome classes = deterministic answers, declared answers, unique "
                          f"solutions, unlisted solutions per solution set, and other; {PREVIEW}; eps={EPS}, K={lt.K}; "
                          f"disconfirms[o][h] = log10 max_h' P(o|h') - log10 P(o|h), positive = against h"),
        base_hash=base_hash,
        source_hash=source_hash,
        seed=seed,
        split=TIERS[tier].split,
        tier=tier,
        generator=generator,
        extra={"outcome_classes": lt.outcome_classes(), "channel": channel.name, "channel_spec": channel.to_json(),
               "likelihood": {"preview": PREVIEW, "eps": EPS, "K": lt.K, "member_kinds": lt.kinds}, **(extra or {})},
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
