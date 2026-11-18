"""Validators run on every generated item and set.

Item checks:
  schema            the record matches item.schema.json
  hashes            presentation hash = hash(prompt); content hash = hash(task content key)
  seed              the seed lies in its tier's range (smoke [0, 1e5), dev [1e5, 1e6), test [1e6, 2e6))
  ground_truth      every standard ground-truth key equals its independent recomputation
  readouts          the readouts behind the likelihood tables (solution, completion and
                    optimal-partition counts, optimal sets, ...) equal their independent recomputation
  premises          an entailment item's stated premises are consistent (no design intends otherwise)
  predictions       every listed prediction is recomputed from (instance, member, params)
  discriminates     at least two listed members give different answers

The ground truth and readouts are recomputed by `validate.independent`, which reads the raw
instance JSON with its own code and a different SAT backend from the generator path.

Run checks (`run_checks`) add, over the items of one generated set:
  unique_id         no item id is used twice
  hash_collision    no 16-hex content or presentation hash is shared by two different contents or prompts
  lineage           the counterfactual lineage holds (`LINEAGE_RULES`); the violations today's
                    generators are known to have (`KNOWN_LINEAGE_GAPS`) are reported, not failed
  set_invariant     each generator's designed invariants (truth fixed while a heuristic flips,
                    identical label multisets, surface matching within tolerance, ...)

Leakage: no base instance is shared across the dev and test splits, and no instance of the test
split (every item, not one per base) states a problem identical or isomorphic to one in the dev
split, comparing the stated problem (complement graphs, inverted clauses, the NOR reading) in
canonical form; for lexicon-partitioned verticals, every content word lies in its split's lexicon
partition.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Callable

import jsonschema
import networkx as nx

from reasoning_heuristics.hashing import canonical_json, sha, to_jsonable
from reasoning_heuristics.heuristics.answers import answer_key
from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.tasks import EntailmentTask, load_task
from reasoning_heuristics.lexicon import partition_of_word
from reasoning_heuristics.problems.entailment import formula as F
from reasoning_heuristics.schema.item import Item, validate_against_schema
from reasoning_heuristics.seeds import TIERS
from reasoning_heuristics.validate.independent import effective_problem, independent_truth, premises_consistent, recheck_readouts


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
    tier = TIERS.get(item.tier)
    if tier is None or tier.split != item.split:
        fail("seed", f"tier {item.tier!r} does not belong to the {item.split} split")
    elif item.seed is None or not tier.seed_lo <= item.seed < tier.seed_hi:
        fail("seed", f"seed {item.seed} outside the {item.tier} tier range [{tier.seed_lo}, {tier.seed_hi})")
    gt = item.ground_truth if isinstance(item.ground_truth, dict) else {}
    try:
        indep = independent_truth(item.instance)
    except Exception as exc:  # an instance the validator cannot read or solve fails, loudly
        fail("ground_truth", f"independent recomputation raised {type(exc).__name__}: {exc}")
        indep = {}
    for k, v in indep.items():
        if k not in gt:
            fail("ground_truth", f"standard key {k!r} missing")
        elif to_jsonable(v) != gt[k]:
            fail("ground_truth", f"{k}: stored {gt[k]!r} != independent {to_jsonable(v)!r}")
    try:
        for msg in recheck_readouts(item.instance, gt, item.params):
            fail("readouts", msg)
    except Exception as exc:
        fail("readouts", f"independent recomputation raised {type(exc).__name__}: {exc}")
    if isinstance(task, EntailmentTask):
        try:
            if not premises_consistent(item.instance):
                fail("premises", "the stated premises are inconsistent, so every conclusion follows vacuously")
        except Exception as exc:
            fail("premises", f"consistency check raised {type(exc).__name__}: {exc}")
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


# --- hash collisions ----------------------------------------------------------------------------


def check_hash_collisions(items: list[Item]) -> list[Failure]:
    """Hashes are 16 hex characters: fail any content hash shared by two different content keys,
    and any presentation hash shared by two different prompts."""
    contents: dict[str, dict[str, str]] = defaultdict(dict)
    prompts: dict[str, dict[str, str]] = defaultdict(dict)
    for it in items:
        if it.instance is not None:
            contents[it.content_hash].setdefault(canonical_json(load_task(it.instance).content_key()), it.item_id)
        prompts[it.presentation_hash].setdefault(it.prompt, it.item_id)
    out = []
    for what, groups in (("content", contents), ("presentation", prompts)):
        for h, seen in groups.items():
            if len(seen) > 1:
                ids = list(seen.values())
                out.append(Failure(ids[1], "hash_collision", f"{what} hash {h} is shared by {len(seen)} different "
                                                             f"{'contents' if what == 'content' else 'prompts'} (items {ids[:4]})"))
    return out


# --- lineage --------------------------------------------------------------------------------------

LINEAGE_RULES = {
    "source-resolves": "a variant's source_hash is the content hash of an item in the same collection",
    "root-is-base": "an item with no source is its own base: content_hash == base_hash",
    "source-same-base": "a variant shares the base_hash of the item it was made from",
    "base-provenance": "every item of one base carries the base's seed, split and tier",
}

# (generator, rule) violations that the generators had when the lineage check was written. They
# are reported (run_checks' "lineage_known_gaps", review/summary.md) instead of failing; any
# other violation fails. Delete an entry when its generator is fixed.
KNOWN_LINEAGE_GAPS: set[tuple[str, str]] = {
    ("reasoning_heuristics.generators.ah_e2", "root-is-base"),  # ENT sets: 8 roots, base = premises only
    ("reasoning_heuristics.generators.ah_e5", "root-is-base"),  # ENT: base hashes the premises only
    ("reasoning_heuristics.generators.ah_e5", "source-resolves"),
    ("reasoning_heuristics.generators.b4_e1", "root-is-base"),  # base = the pair id, not an item
    ("reasoning_heuristics.generators.b4_e1", "source-resolves"),
    ("reasoning_heuristics.generators.b4_e2", "root-is-base"),
    ("reasoning_heuristics.generators.b4_e2", "source-resolves"),
    ("reasoning_heuristics.generators.c_e1", "root-is-base"),  # base = c2's task, the root is c2-RELABEL
    ("reasoning_heuristics.generators.c_e1", "source-resolves"),
    ("reasoning_heuristics.generators.c_e3", "root-is-base"),  # base = the bare Graph, not a task
    ("reasoning_heuristics.generators.c_e3", "source-resolves"),
    ("reasoning_heuristics.generators.c_e5", "root-is-base"),  # COL/SAT/STATE bases hash the bare instance
    ("reasoning_heuristics.generators.c_e5", "source-resolves"),
}


def check_lineage(items: list[Item], known: set[tuple[str, str]] | None = None) -> tuple[list[Failure], list[Failure]]:
    """Check `LINEAGE_RULES` over a collection (one generated set, or everything). Returns
    (failures, known gaps): violations whose (generator, rule) is in `known` (default
    `KNOWN_LINEAGE_GAPS`) are returned separately, to be reported rather than failed."""
    known = KNOWN_LINEAGE_GAPS if known is None else known
    by_content: dict[str, list[Item]] = defaultdict(list)
    by_base: dict[str, list[Item]] = defaultdict(list)
    for it in items:
        by_content[it.content_hash].append(it)
        by_base[it.base_hash].append(it)
    found: list[tuple[Item, str, str]] = []
    for it in items:
        if it.source_hash is None:
            if it.content_hash != it.base_hash:
                found.append((it, "root-is-base", f"no source, but content hash {it.content_hash} != base hash {it.base_hash}"))
            continue
        sources = by_content.get(it.source_hash, [])
        if not sources:
            found.append((it, "source-resolves", f"source hash {it.source_hash} matches no item's content hash"))
        elif not any(s.base_hash == it.base_hash for s in sources):
            found.append((it, "source-same-base", f"source {sources[0].item_id} has base {sources[0].base_hash}, "
                                                  f"this item {it.base_hash}"))
    for base, group in by_base.items():
        provenance = sorted({(it.seed, it.split, it.tier) for it in group}, key=repr)
        if len(provenance) > 1:
            found += [(it, "base-provenance", f"base {base} carries {provenance}") for it in group]
    failures, gaps = [], []
    for it, rule, msg in found:
        (gaps if (it.generator, rule) in known else failures).append(Failure(it.item_id, "lineage", f"{rule}: {msg}"))
    return failures, gaps


# --- leakage ------------------------------------------------------------------------------------


def _leak_graph(kind: str, obj: Any) -> nx.Graph:
    """A labelled graph whose isomorphism class is the stated problem's (up to renaming and,
    for CNF, polarity flips and order)."""
    g = nx.Graph()
    if kind == "graph":
        g.add_nodes_from(obj[0])
        g.add_edges_from(tuple(e) for e in obj[1])
    elif kind == "cnf":
        for v in {abs(l) for c in obj for l in c}:
            g.add_node(("v", v), kind="var")
            g.add_node(("p", v), kind="lit")
            g.add_node(("q", v), kind="lit")
            g.add_edge(("v", v), ("p", v))
            g.add_edge(("v", v), ("q", v))
        for i, c in enumerate(sorted(obj, key=sorted)):
            g.add_node(("c", i), kind="clause")
            g.add_edges_from((("c", i), ("p", l) if l > 0 else ("q", -l)) for l in c)
    elif kind == "formula":
        premises, probe = obj
        counter = [0]

        def node(k: str) -> int:
            counter[0] += 1
            g.add_node(counter[0], kind=k)
            return counter[0]

        atoms: dict[str, int] = {}

        def walk(f: tuple) -> int:
            if f[0] == "lit":
                if f[1] not in atoms:
                    atoms[f[1]] = node("atom")
                n = node("pos" if f[2] else "neg")
                g.add_edge(n, atoms[f[1]])
                return n
            n = node(f[0])
            if f[0] == "if":  # keep antecedent and consequent apart
                for role, h in (("antecedent", f[1]), ("consequent", f[2])):
                    r = node(role)
                    g.add_edge(n, r)
                    g.add_edge(r, walk(h))
            else:
                for h in (f[1], f[2]) if f[0] == "iff" else f[1]:
                    g.add_edge(n, walk(h))
            return n

        for p in premises:
            g.add_edge(node("premise"), walk(p))
        if probe is not None:
            g.add_edge(node("probe"), walk(probe))
    elif kind == "tsp":
        n = len(obj)
        g.add_nodes_from(range(n))
        g.add_edges_from((i, j, {"d": obj[i][j]}) for i in range(n) for j in range(i + 1, n))
    return g


def _invariant(kind: str, obj: Any) -> str:
    if kind == "knapsack":
        return repr(obj)  # already canonical
    g = _leak_graph(kind, obj)
    if kind == "graph":
        return nx.weisfeiler_lehman_graph_hash(g, iterations=4)
    if kind == "tsp":
        return nx.weisfeiler_lehman_graph_hash(g, edge_attr="d", iterations=3)
    return nx.weisfeiler_lehman_graph_hash(g, node_attr="kind", iterations=4)


def _isomorphic(kind: str, a: Any, b: Any) -> bool:
    if kind == "knapsack":
        return a == b
    ga, gb = _leak_graph(kind, a), _leak_graph(kind, b)
    if kind == "graph":
        return nx.is_isomorphic(ga, gb)
    if kind == "tsp":
        return nx.is_isomorphic(ga, gb, edge_match=nx.algorithms.isomorphism.categorical_edge_match("d", None))
    return nx.is_isomorphic(ga, gb, node_match=nx.algorithms.isomorphism.categorical_node_match("kind", None))


def check_leakage(items: list[Item], lexicon_partitioned: bool = False) -> list[Failure]:
    """Compare instances across splits (pass items of both splits together)."""
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
    # Every instance of either split, as its stated problem in canonical form; identical forms are compared once.
    def problem(it: Item) -> tuple[str, Any] | None:
        try:
            return effective_problem(it.instance)
        except Exception as exc:
            out.append(Failure(it.item_id, "leakage", f"cannot read the stated problem: {type(exc).__name__}: {exc}"))
            return None

    dev: dict[tuple[str, Any], str] = {}
    for it in by_split.get("dev", []):
        if (p := problem(it)) is not None:
            dev.setdefault(p, it.item_id)
    test: dict[tuple[str, Any], list[str]] = defaultdict(list)
    for it in by_split.get("test", []):
        if (p := problem(it)) is not None:
            test[p].append(it.item_id)
    index: dict[tuple[str, str], list[tuple[Any, str]]] = defaultdict(list)
    test_kinds = {kind for kind, _ in test}
    for (kind, obj), iid in dev.items():
        if kind in test_kinds:
            index[(kind, _invariant(kind, obj))].append((obj, iid))
    for (kind, obj), test_ids in test.items():
        if (kind, obj) in dev:
            match = dev[(kind, obj)]
        else:
            match = next((iid for obj2, iid in index.get((kind, _invariant(kind, obj)), []) if _isomorphic(kind, obj, obj2)), None)
        if match is not None:
            out += [Failure(tid, "leakage", f"{kind} instance isomorphic to dev item {match}") for tid in test_ids]
    return out


# --- a generated set ------------------------------------------------------------------------------


def run_checks(items: list[Item], set_check: Callable[[list[Item]], list[str]] | None) -> dict[str, Any]:
    """All item checks, hash collisions, lineage and the generator's set checks. Returns a JSON-able report."""
    failures: list[Failure] = []
    for item_id, n in Counter(it.item_id for it in items).items():
        if n > 1:
            failures.append(Failure(item_id, "unique_id", f"item id used by {n} items"))
    for it in items:
        failures += check_item(it)
    failures += check_hash_collisions(items)
    lineage_failures, gaps = check_lineage(items)
    failures += lineage_failures
    generator = {it.item_id: it.generator for it in items}
    known: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for f in gaps:
        known[generator[f.item_id]][f.message.split(":")[0]] += 1
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
        "lineage_known_gaps": {g: dict(rules) for g, rules in sorted(known.items())},
    }
