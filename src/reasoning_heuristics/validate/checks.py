"""Validators run on every generated item and set.

Item checks:
  schema            the record matches item.schema.json
  hashes            presentation hash = hash(prompt); content hash = hash(task content key)
  seed              the seed lies in its split's range (dev < 10^6 <= test)
  ground_truth      every standard ground-truth key equals its independent recomputation
  predictions       every listed prediction is recomputed from (instance, member, params)
  discriminates     at least two listed members give different answers

Set checks are supplied by each generator (its designed invariants: truth fixed while a
heuristic flips, identical label multisets, surface matching within tolerance, ...).

Leakage: no base instance is shared, or isomorphic, across the dev and test splits; for
lexicon-partitioned verticals, every content word lies in its split's lexicon partition.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Callable

import jsonschema
import networkx as nx

from reasoning_heuristics.hashing import sha, to_jsonable
from reasoning_heuristics.heuristics.answers import answer_key
from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.tasks import ColouringTask, EntailmentTask, SatTask, load_task
from reasoning_heuristics.lexicon import partition_of_word
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.entailment import formula as F
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.schema.item import Item, validate_against_schema
from reasoning_heuristics.seeds import SPLIT_RANGES
from reasoning_heuristics.validate.truth import independent_truth


@dataclass
class Failure:
    item_id: str
    check: str
    message: str

    def to_json(self) -> dict[str, str]:
        return {"item_id": self.item_id, "check": self.check, "message": self.message}


def _close(a: Any, b: Any, tol: float = 1e-9) -> bool:
    if isinstance(a, float) or isinstance(b, float):
        return isinstance(a, (int, float)) and isinstance(b, (int, float)) and math.isclose(a, b, abs_tol=tol)
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_close(a[k], b[k], tol) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_close(x, y, tol) for x, y in zip(a, b))
    return a == b


def check_item(item: Item) -> list[Failure]:
    out: list[Failure] = []

    def fail(check: str, msg: str) -> None:
        out.append(Failure(item.item_id, check, msg))

    try:
        validate_against_schema(item.to_json())
    except jsonschema.ValidationError as exc:
        fail("schema", exc.message[:300])
    if item.presentation_hash != sha(item.prompt):
        fail("hashes", "presentation hash does not match the prompt")
    if item.instance is None:
        fail("predictions", "no structured instance: cannot recompute")
        return out
    task = load_task(item.instance)
    if item.content_hash != sha(task.content_key()):
        fail("hashes", "content hash does not match the instance")
    lo, hi = SPLIT_RANGES[item.split]
    if item.seed is None or not lo <= item.seed < hi:
        fail("seed", f"seed {item.seed} outside the {item.split} range [{lo}, {hi})")
    indep = independent_truth(task)
    gt = item.ground_truth if isinstance(item.ground_truth, dict) else {}
    for k, v in indep.items():
        if k not in gt:
            fail("ground_truth", f"standard key {k!r} missing")
        elif to_jsonable(v) != gt[k]:
            fail("ground_truth", f"{k}: stored {gt[k]!r} != independent {to_jsonable(v)!r}")
    for label, rec in item.predictions.items():
        try:
            pred = run(task.domain, rec["member"], task, rec["params"])
        except Exception as exc:  # a member that cannot run on its own record is a failure, loudly
            fail("predictions", f"{label}: recomputation raised {type(exc).__name__}: {exc}")
            continue
        if to_jsonable(pred.answer) != rec["answer"]:
            fail("predictions", f"{label}: stored answer differs from recomputed")
        dist = to_jsonable(pred.distribution) if pred.distribution is not None else None
        if not _close(dist, rec.get("distribution")):
            fail("predictions", f"{label}: stored distribution differs from recomputed")
        if not _close(to_jsonable(pred.trace_features), rec.get("trace_features", {})):
            fail("predictions", f"{label}: stored trace features differ from recomputed")
    keys = {answer_key(task.domain, r["answer"]) for r in item.predictions.values()
            if r["answer"] is not None and not r.get("trace_features", {}).get("set_valued")}
    if len(keys) < 2:
        fail("discriminates", f"only {len(keys)} distinct member answer(s)")
    return out


# --- leakage ------------------------------------------------------------------------------------


def _base_object(task: Any) -> tuple[str, Any] | None:
    if isinstance(task, ColouringTask):
        return "graph", task.graph
    if isinstance(task, SatTask):
        return "cnf", task.cnf
    if isinstance(task, EntailmentTask):
        return "formula", task
    return None


def formula_graph(task: EntailmentTask) -> nx.Graph:
    g = nx.Graph()
    counter = [0]

    def node(kind: str) -> int:
        counter[0] += 1
        g.add_node(counter[0], kind=kind)
        return counter[0]

    atoms: dict[str, int] = {}

    def walk(f) -> int:
        if f[0] == "lit":
            if f[1] not in atoms:
                atoms[f[1]] = node("atom")
            n = node("pos" if f[2] else "neg")
            g.add_edge(n, atoms[f[1]])
            return n
        n = node(f[0])
        for h in (f[1] if f[0] in ("and", "or", "nand", "nor") else (f[1], f[2])):
            g.add_edge(n, walk(h))
        return n

    for p in task.premises:
        g.add_edge(node("premise"), walk(p))
    if task.probe is not None:
        g.add_edge(node("probe"), walk(task.probe))
    return g


def _invariant(kind: str, obj: Any) -> str:
    if kind == "graph":
        return G.iso_invariant(obj)
    if kind == "cnf":
        return S.iso_invariant(obj)
    return nx.weisfeiler_lehman_graph_hash(formula_graph(obj), node_attr="kind", iterations=4)


def _isomorphic(kind: str, a: Any, b: Any) -> bool:
    if kind == "graph":
        return G.isomorphic(a, b)
    if kind == "cnf":
        return S.isomorphic(a, b)
    nm = nx.algorithms.isomorphism.categorical_node_match("kind", None)
    return nx.is_isomorphic(formula_graph(a), formula_graph(b), node_match=nm)


def check_leakage(items: list[Item], lexicon_partitioned: bool = False) -> list[Failure]:
    """Compare base instances across splits (pass items of both splits together)."""
    out: list[Failure] = []
    by_split: dict[str, list[Item]] = defaultdict(list)
    for it in items:
        by_split[it.split].append(it)
    if lexicon_partitioned:
        for it in items:
            task = load_task(it.instance)
            if isinstance(task, EntailmentTask):
                words = {w for a in F.atoms_of(list(task.premises) + ([task.probe] if task.probe else []) + list(task.options))
                         for w in re.split("[:@]", a)}
                bad = sorted(w for w in words if partition_of_word(w) != it.split)
                if bad:
                    out.append(Failure(it.item_id, "leakage", f"lexicon words outside the {it.split} partition: {bad}"))
    if len(by_split) < 2:
        return out
    dev_hashes = {it.base_hash for it in by_split.get("dev", [])}
    for it in by_split.get("test", []):
        if it.base_hash in dev_hashes:
            out.append(Failure(it.item_id, "leakage", "test item shares a base hash with a dev item"))
    if lexicon_partitioned:
        return out  # template structure is shared by design; disjoint lexicons are the guarantee
    bases: dict[str, dict[str, tuple[str, Any, str]]] = defaultdict(dict)
    for it in items:
        if it.source_hash is not None and it.base_hash in bases[it.split]:
            continue
        obj = _base_object(load_task(it.instance))
        if obj is None:
            continue
        bases[it.split].setdefault(it.base_hash, (obj[0], obj[1], it.item_id))
    index: dict[str, list[tuple[str, Any, str]]] = defaultdict(list)
    for kind, obj, iid in bases.get("dev", {}).values():
        index[kind + ":" + _invariant(kind, obj)].append((kind, obj, iid))
    for kind, obj, iid in bases.get("test", {}).values():
        for kind2, obj2, iid2 in index.get(kind + ":" + _invariant(kind, obj), []):
            if _isomorphic(kind, obj, obj2):
                out.append(Failure(iid, "leakage", f"base instance isomorphic to dev item {iid2}"))
    return out


def run_checks(items: list[Item], set_check: Callable[[list[Item]], list[str]] | None) -> dict[str, Any]:
    """All item checks plus the generator's set checks. Returns a JSON-able report."""
    failures: list[Failure] = []
    for item_id, n in Counter(it.item_id for it in items).items():
        if n > 1:
            failures.append(Failure(item_id, "unique_id", f"item id used by {n} items"))
    for it in items:
        failures += check_item(it)
    sets: dict[str, list[Item]] = defaultdict(list)
    for it in items:
        sets[it.set_id].append(it)
    if set_check is not None:
        for sid, members in sets.items():
            for msg in set_check(members):
                failures.append(Failure(f"set:{sid}", "set_invariant", msg))
    failed_items = {f.item_id for f in failures if not f.item_id.startswith("set:")}
    failed_sets = {f.item_id[4:] for f in failures if f.item_id.startswith("set:")}
    passed = [it for it in items if it.item_id not in failed_items and it.set_id not in failed_sets]
    return {
        "items": len(items),
        "sets": len(sets),
        "items_passed": len(passed),
        "pass_rate": round(len(passed) / len(items), 4) if items else 1.0,
        "failures": [f.to_json() for f in failures],
    }
