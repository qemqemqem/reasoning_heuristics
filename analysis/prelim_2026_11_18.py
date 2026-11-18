"""Preliminary results of 2026-11-18: every number in docs/results/2026-11-18-preliminary.md.

    OMP_NUM_THREADS=1 python analysis/prelim_2026_11_18.py --runs-root data/runs
    OMP_NUM_THREADS=1 python analysis/prelim_2026_11_18.py --runs-root data/runs --check   # regenerate, compare, write nothing
    python analysis/prelim_2026_11_18.py --render-only --check     # seconds: do the doc's tables match the JSON?

The recovery check at the estimate is the slow part (C E2 colouring: about an hour of CPU per
fit); `--recovery-reps 0` skips it, and `--no-doc` writes only the JSON.

Discovers every run under --runs-root named `2026-11-18-{dev,pc20,pc40}-*` that has scored
records, reads the committed item set each one's manifest names (data/items/<set>), and writes
`analysis/out/prelim_2026_11_18.json` and the doc's generated tables (the blocks between
`<!-- BEGIN prelim:NAME -->` and `<!-- END prelim:NAME -->`; the prose around them is written by
hand). DESIGN §5 rule 6: every number in the doc comes from this command. The JSON holds every
discovered run, so a page can be built from it alone (`SCHEMA` below, also written into it); the
doc's tables show only the runs the doc describes (`DOC_PILOT`, `DOC_DEV`).

What it computes:

1. **Joins.** Every scored record is read with `identify.records.from_scored` and joined to the
   current item files by item_id with the content hash checked (`identify.records.join`, which
   raises on any mismatch). The first runs were scored before #22 added the A1 give-up member to the
   C E1 and C E2 SAT items; the join is what makes that drift safe (ids, prompts and content hashes
   are unchanged), and the per-run drift of item-file hashes against each manifest is recorded.
2. **Descriptive statistics for every run and unit** from the scorer's own fields: categories,
   `correct` and `valid` among ok answers, `members_matched` and `sets_matched`.
3. **Mixture fits only where the recovery gates pass at the item set's size** (DESIGN §5 rule 12;
   `GATED`): C E2 colouring, C E2 knapsack and A/H E5 SAT at 20 per cell, and C E5 SAT with a given
   partial assignment at 40, on every run of those sets, with `identify.engine.fit_unit` (near-miss
   slips, percentile cluster-bootstrap intervals), plus BCa intervals from the same bootstrap draws
   (`mixture.bca_interval`, #24). Members tied on every item share one weight (`MUST_TIE` checks
   the one tie a gate depends on). Each fit also reports how far the answers are from the nearest
   member, and which members predict a special token.
4. **Recovery at the estimate**: fake models that answer the same items from each fitted mixture
   (its weights, slip rate and slip shape) are refitted, to check bias, coverage and width at the
   operating point the real data put the fit in, which the Stage 0 gates did not test (they plant
   0.6 / 0.3 / 0.1 with eps = 0.1, rho = 0.3), with both interval methods.

Every random draw is seeded; a rerun reproduces the JSON and the tables exactly.
"""

from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")  # before numpy: workers are processes

import argparse
import gzip
import hashlib
import json
import math
import multiprocessing as mp
import platform
import subprocess
import sys
import time
import zlib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from reasoning_heuristics.identify import agreement
from reasoning_heuristics.identify.engine import fit_unit
from reasoning_heuristics.identify.fake import Scenario, simulate, truth_vector
from reasoning_heuristics.identify.likelihood import UnitModel
from reasoning_heuristics.identify.mixture import EPS_MAX, RHO_GRID, UNEXPLAINED, bca_interval, fit
from reasoning_heuristics.identify.records import from_scored, join
from reasoning_heuristics.identify.units import Unit, eval_name, is_answer_item, load_items

REPO = Path(__file__).resolve().parent.parent
OUT_JSON = REPO / "analysis" / "out" / "prelim_2026_11_18.json"
DOC = REPO / "docs" / "results" / "2026-11-18-preliminary.md"

# Runs are discovered under --runs-root: every directory matching one of these patterns that has
# scored records. A run still in progress has none; it is listed under `skipped_runs` and left out.
RUN_PATTERNS = ("2026-11-18-dev-*", "2026-11-18-pc20-*", "2026-11-18-pc40-*")

# Per item set (the directory under data/items/ a run's manifest names), the units whose recovery
# gates pass at that set's size on the regenerated items (RECOVERY.md, "Regenerated items:
# candidate units", #24). Nothing else is fitted (DESIGN §5 rule 12).
GATED = {
    "pc20": ["C_E2/colouring", "C_E2/knapsack", "AH_E5/SAT"],
    "pc40": ["C_E5/3-SAT (partial assignment given)"],
}
# Members that are tied on every item of a gated unit, so that only their sum is identified: the
# engine merges them into one group, and the script stops if it ever does not (RECOVERY.md: on C E5
# SAT with a given state at 40 per cell the pass covers the pair's sum, never either one alone)
MUST_TIE = {("pc40", "C_E5/3-SAT (partial assignment given)"): ("GUC-DET from state (C2)", "SC-DET from state (C2)")}

# The runs the doc describes. Its tables are rendered for these runs only, so the doc stays what its
# prose says when more runs land; the JSON holds every discovered run, for a page built from it.
DOC_PILOT = ["2026-11-18-pc20-qwen3-32b-direct", "2026-11-18-pc20-gpt-oss-20b-thinking-low"]
DOC_DEV = ["2026-11-18-dev-qwen3-32b-direct", "2026-11-18-dev-qwen3-14b-direct", "2026-11-18-dev-gpt-oss-20b-thinking-low"]
DOC_FIT_UNITS = GATED["pc20"]

# Why every other unit gets descriptive statistics only. RECOVERY.md "Regenerated items: candidate
# units" (#24) where a unit was rerun on the regenerated items, else its pre-regeneration "Where the
# gates pass" and sweep tables; dev units are at 5 per cell, where no unit passes ("Bottom line").
NOT_FITTED = {
    "AH_E1": "fails by design: q is not identified on a two-valued channel (q = ½ always-positive + ½ always-negative), and the noise models are near-mixtures of the procedures",
    "AH_E2": "fails by design: as A/H E1",
    "AH_E5/COL": "not reached by 40 (pre-regeneration): the 0.1 weight's coverage is 0.84 at 40 (100 replicates); at 20, coverage 0.83 and width 0.24",
    "AH_E5/ENT": "not reached by 40 on the regenerated items: coverage 0.81 at 20 and 0.87 at 40 (B4 FIRST); BCa 0.88 at both",
    "AH_E5/KNAP": "no mixture test (pre-regeneration): fewer than three members on every item; null q fails at 20",
    "B4C4_E1": "fails by design: NOISY-EXACT is nearly the EXACT group (σ_min/σ_max = 0.0004)",
    "B4C4_E2": "fails by design: five linear dependencies, one of them among procedures (the H6 gap)",
    "C_E1/3-SAT": "fails at 20 on the regenerated items: percentile coverage 0.86 (ALWAYS-UNSAT; BCa 0.92 passes), and null q fails (coverage 0.78)",
    "C_E1/colouring": "not reached by 40 (pre-regeneration): coverage 0.88 ± 0.03 at 40 (100 replicates); 0.77 at 20",
    "C_E2/3-SAT": "fails at 20 on the regenerated items: median width 0.28 > 0.2, and null q fails (coverage 0.89)",
    "C_E3": "fails by design: FF-LIST (= DPLL-LIST) leaks 0.14–0.31 of its weight to the LOCAL-t proxies at every size",
    "C_E5/3-SAT": "not reached by 40: width 0.23",
    "C_E5/3-SAT (partial assignment given)": "passes only at 40 per cell (regenerated items); null q fails below 40",
    "C_E5/colouring (k=3)": "fails by design at these sizes: a near-tie (FF-3-EDGE-MENTION-ABORT vs PHANTOM-ADJACENT); widths stay at 0.4",
    "C_E5/colouring (k=3, partial colouring given)": "not reached by 40: bias 0.07, width 0.24",
    "C_E5/propositional entailment": "fails by design: q and NOISY-EXACT are combinations of other members, and EXACT answers NO on every item",
}

SCHEMA = {
    "runs": "one entry per discovered run: run_id, label, item_set, model, condition, effort, reasoning, max_tokens, "
            "providers_served, n_records, from_cache, spent_usd (API-reported), scorer, run and scorer git SHAs, scored_sha256, "
            "item_drift (per item file: the manifest's sha256 and the current file's)",
    "skipped_runs": "directories matching the run patterns that have no scored records yet (in progress)",
    "descriptive": "run_id -> unit -> categories, ok, correct, accuracy_of_ok, valid / valid_defined, members_matched and "
                   "sets_matched ([{members, answers, share_of_ok}], members matching the same answers merged), "
                   "wrong_member_match, special_answers, token medians, truncated_by_cell",
    "fits": "unit -> run_id -> fit_unit's report (fit.weights: pi with percentile lo/hi, or 'not identified' with a range; "
            "eps, rho with intervals; identifiability; diagnostics; excluded; error_agreement and weight_lift with "
            "permutation baselines) plus bca ({group: [lo, hi]}), ea_counts, q_exact_chance, near, reach, lumps, "
            "unit_facts, special_check, seed, item_set",
    "recovery_at_estimate": "unit -> run_id -> fake models planted at the fitted mixture: per-quantity truth, mean, bias, "
                            "coverage and width (percentile and BCa), gate verdicts, and the simulated reach statistics",
    "gated_units": "item set -> the units fitted at that size; every other unit is descriptive only (not_fitted gives why)",
}

CATS = ("ok", "parse_fail", "partial", "truncated", "refusal", "declared_impossible", "api_error")
SPECIALS = ("UNSAT", "IMPOSSIBLE", "X")
PLANT_MIN = 0.01  # recovery at the estimate: fitted weights below this are planted as 0


# =============================================================================================
# Inputs
# =============================================================================================


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_state() -> dict[str, Any]:
    def run(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()

    return {"sha": run("rev-parse", "HEAD"),
            "dirty_src": bool(run("status", "--porcelain", "--", "src", "pyproject.toml", "analysis/prelim_2026_11_18.py"))}


def unit_name(item: dict[str, Any]) -> str:
    return f"{eval_name(item)}/{item['domain']}"


def not_fitted_reason(name: str, item_set: str) -> str:
    if item_set == "dev":
        return "dev size (5 per cell): no unit passes the gates there (RECOVERY.md, Bottom line)"
    if name in NOT_FITTED:
        return NOT_FITTED[name]
    return NOT_FITTED[name.split("/")[0]]


def discover_runs(runs_root: Path) -> tuple[list[str], list[str]]:
    """Run directories matching RUN_PATTERNS: those with scored records, and those without."""
    found, skipped = [], []
    for pat in RUN_PATTERNS:
        for d in sorted(runs_root.glob(pat)):
            if d.is_dir():
                (found if (d / "scored.jsonl.gz").exists() else skipped).append(d.name)
    if not found:
        raise FileNotFoundError(f"no scored run matching {RUN_PATTERNS} under {runs_root}")
    return found, skipped


def run_label(manifest: dict[str, Any]) -> str:
    """'Qwen3-32B direct', 'gpt-oss-20b thinking-low', ... from the manifest."""
    model = manifest["model_requested"].split("/")[-1]
    if model.startswith("qwen"):
        model = "Qwen" + model[4:].upper()
    return f"{model} {manifest['condition']['label']}"


def item_set_of(manifest: dict[str, Any]) -> str:
    """The item set a run answered: the one directory under data/items/ that its manifest's files are in."""
    dirs = {Path(p).parent for p in manifest["items"]["files"]}
    if len(dirs) != 1 or next(iter(dirs)).parent != Path("data/items"):
        raise ValueError(f"run {manifest['run_id']}: item files are not in one directory of data/items: {sorted(map(str, dirs))}")
    return next(iter(dirs)).name


def load_set(name: str) -> dict[str, Any]:
    """Every item file of data/items/<name>, as committed now."""
    paths = sorted(str(p.relative_to(REPO)) for p in (REPO / "data" / "items" / name).glob("*.jsonl.gz"))
    if not paths:
        raise FileNotFoundError(f"no item files in data/items/{name}")
    items = load_items([REPO / p for p in paths])
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for it in items:
        if is_answer_item(it):
            groups[unit_name(it)].append(it)
    return {"paths": paths, "sha256": {p: sha256(REPO / p) for p in paths}, "items": items,
            "by_id": {it["item_id"]: it for it in items}, "groups": dict(groups)}


def read_records(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_run(runs_root: Path, run_id: str, sets: dict[str, dict[str, Any]]) -> dict[str, Any]:
    d = runs_root / run_id
    scored = d / "scored.jsonl.gz"
    manifest = json.loads((d / "manifest.json").read_text())
    scoring = json.loads((d / "scoring.json").read_text())
    set_name = item_set_of(manifest)
    if set_name not in sets:
        sets[set_name] = load_set(set_name)
    item_set = sets[set_name]
    missing = set(manifest["items"]["files"]) - set(item_set["paths"])
    if missing:
        raise FileNotFoundError(f"run {run_id} answered item files that are not committed: {sorted(missing)}")
    records = read_records(scored)
    responses, dropped = from_scored(scored)
    pairs = join(responses, item_set["items"])  # raises on an unknown item or a content-hash mismatch
    if len(pairs) != len(responses):
        raise AssertionError("join lost responses")
    drift = {}
    for p, h in manifest["items"]["files"].items():
        cur = item_set["sha256"].get(p)
        drift[p] = {"manifest": h, "current": cur, "same": h == cur}
    return {"run_id": run_id, "dir": str(d), "item_set": set_name, "scored_sha256": sha256(scored), "manifest": manifest,
            "scoring": scoring, "records": records, "responses": responses, "dropped": dropped, "pairs": pairs, "drift": drift}


def run_meta(run: dict[str, Any]) -> dict[str, Any]:
    m = run["manifest"]
    recs = run["records"]
    return {"run_id": run["run_id"], "label": run_label(m), "item_set": run["item_set"], "model": m["model_requested"],
            "models_returned": m.get("models_returned"), "condition": m["condition"]["label"],
            "effort": m["condition"].get("effort"),
            "reasoning": m["condition"]["reasoning"], "max_tokens": m["condition"]["max_tokens"],
            "system_prompt": m["condition"]["system_prompt"], "sampling": m["condition"]["sampling"],
            "providers_served": m.get("providers_served"), "provider_routing": m.get("provider_routing"),
            "status": m["status"], "n_items": m["items"]["n_items"], "n_records": len(recs),
            "from_cache": sum(1 for r in recs if r.get("from_cache")), "spent_usd": m["spend"]["spent_usd"],
            "max_pre_answer_tokens": max((r.get("pre_answer_tokens") or 0 for r in recs), default=0),
            "pre_answer_over_20": sum(1 for r in recs if (r.get("pre_answer_tokens") or 0) > 20),
            "run_git_sha": m["git"]["sha"], "scorer_version": run["scoring"]["scorer_version"],
            "scorer_git_sha": run["scoring"]["git"]["sha"], "scored_sha256": run["scored_sha256"],
            "dropped_by_from_scored": run["dropped"], "item_drift": run["drift"]}


# =============================================================================================
# Descriptive statistics (the scorer's own fields)
# =============================================================================================


def match_groups(recs: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    """Members by how many ok answers they match (and that count's share of the ok answers); members
    that match exactly the same answers are merged ("A = B")."""
    hits: dict[str, set[int]] = defaultdict(set)
    for k, r in enumerate(recs):
        for m in r.get(field) or []:
            hits[m].add(k)
    merged: dict[frozenset, list[str]] = defaultdict(list)
    for m, s in hits.items():
        merged[frozenset(s)].append(m)
    out = [{"members": " = ".join(ms), "answers": len(s), "share_of_ok": len(s) / len(recs)} for s, ms in merged.items()]
    return sorted(out, key=lambda x: (-x["answers"], x["members"]))


def median_or_none(xs: list) -> float | None:
    xs = [x for x in xs if x is not None]
    return float(np.median(xs)) if xs else None


def describe(run: dict[str, Any], item_set: dict[str, Any]) -> dict[str, Any]:
    by_unit: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in run["records"]:
        by_unit[unit_name(item_set["by_id"][r["item_id"]])].append(r)
    out = {}
    for name, recs in sorted(by_unit.items()):
        cats = Counter(r["category"] for r in recs)
        unknown = set(cats) - set(CATS)
        if unknown:
            raise ValueError(f"unknown categories {unknown}")
        ok = [r for r in recs if r["category"] == "ok"]
        valid = [r["valid"] for r in ok if r.get("valid") is not None]
        special = Counter(r["parsed"] for r in ok if isinstance(r.get("parsed"), str) and r["parsed"] in SPECIALS)
        n_correct = sum(1 for r in ok if r["correct"])
        out[name] = {
            "n": len(recs), "categories": {c: cats.get(c, 0) for c in CATS},
            "ok": len(ok), "correct": n_correct, "accuracy_of_ok": n_correct / len(ok) if ok else None,
            "valid": sum(1 for v in valid if v), "valid_defined": len(valid),
            "any_member_match": sum(1 for r in ok if r.get("members_matched")),
            "wrong": sum(1 for r in ok if r["correct"] is False),
            "wrong_member_match": sum(1 for r in ok if r["correct"] is False and r.get("members_matched")),
            "any_set_match": sum(1 for r in ok if r.get("sets_matched")),
            "members_matched": match_groups(ok, "members_matched"),
            "sets_matched": match_groups(ok, "sets_matched"),
            "special_answers": dict(special),
            "truncated_by_cell": dict(Counter(r["cell"] for r in recs if r["category"] == "truncated")),
            "median_reasoning_tokens": median_or_none([r.get("reasoning_tokens") for r in recs]),
            "median_completion_tokens": median_or_none([r.get("completion_tokens") for r in recs]),
            "max_pre_answer_tokens": max((r.get("pre_answer_tokens") or 0 for r in recs), default=0),
            "pre_answer_over_20": sum(1 for r in recs if (r.get("pre_answer_tokens") or 0) > 20),
            "scorer_git_sha": sorted({r["scorer_git_sha"] for r in recs}),
        }
    return out


# =============================================================================================
# Fits
# =============================================================================================


def to_jsonable(x: Any) -> Any:
    if isinstance(x, dict):
        return {str(k): to_jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [to_jsonable(v) for v in x]
    if isinstance(x, (np.floating, float)):
        v = float(x)
        return None if math.isnan(v) else round(v, 6)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, np.ndarray):
        return to_jsonable(x.tolist())
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def job_seed(*parts: str) -> int:
    return zlib.crc32("|".join(parts).encode())


_CTX: dict[str, Any] = {}


def _unit(item_set: str, name: str) -> Unit:
    groups = _CTX["sets"][item_set]["groups"]
    ev, dom = name.split("/", 1)
    return Unit(ev, dom, groups[name])


def special_check(um: UnitModel) -> dict[str, Any]:
    """Does any member predict a special token? The pending fix changes only such predictions."""
    det, dist = Counter(), Counter()
    specials = set()
    for i, im in enumerate(um.items):
        specials |= set(im.space.specials)
        for lbl, p in im.preds.items():
            if p.kind == "det" and im.space.is_special(p.key):
                det[lbl] += 1
            if p.kind == "dist" and any(k in im.space.specials for k in p.dist):
                dist[lbl] += 1
    return {"space_specials": sorted(specials), "det_special_predictions": dict(det),
            "dist_members_with_special_mass": dict(dist), "n_items": len(um.items)}


def set_distance(space: Any, y: str, sol: Any) -> int:
    """Exact distance from answer y to the nearest member of a solution set (`space.distance` on the
    best one). Bit spaces: Hamming distance, vectorised. Partitions: a lower bound for every
    solution first (n minus the best overlap of each of y's blocks, injectivity dropped), then the
    exact distance on solutions in lower-bound order until the bound exceeds the best found."""
    S = sol.array(space)
    vy = space.parse(y)
    if S.dtype == bool:
        return int((S != vy[None, :]).sum(1).min())
    keys = sol.keys()
    by = int(vy.max()) + 1
    C = int(S.max()) + 1
    flat = (np.arange(len(S))[:, None] * (by * C) + vy[None, :] * C + S).ravel()
    O = np.bincount(flat, minlength=len(S) * by * C).reshape(len(S), by, C)
    lb = space.n - O.max(2).sum(1)
    best = None
    for k in np.argsort(lb, kind="stable"):
        if best is not None and lb[k] >= best:
            break
        d = space.distance(y, keys[int(k)])
        best = d if best is None else min(best, d)
    return int(best)


def nearest_distances(um: UnitModel, obs: list) -> dict[str, Any]:
    """For each answer: the distance to the nearest deterministic or set-valued member (vertices
    recoloured up to renaming, variables flipped, items toggled)."""
    bins = Counter()
    sizes = []
    for ob in obs:
        i, y = ob.item, ob.key
        im = um.items[i]
        if im.space.is_special(y):
            bins["special token"] += 1
            continue
        best = None
        for g in um.columns:
            p = um.pred(i, g.members[0])
            if p.kind == "det" and not im.space.is_special(p.key):
                d = im.space.distance(y, p.key)
            elif p.kind == "set":
                sizes.append(p.sol.size)
                d = set_distance(im.space, y, p.sol)
            else:
                continue
            best = d if best is None else min(best, d)
        if best is None:
            bins["no member"] += 1
        elif best <= 3:
            bins[str(best)] += 1
        elif best <= 6:
            bins["4-6"] += 1
        else:
            bins[">6"] += 1
    n_positions = sorted({um.items[ob.item].space.n for ob in obs})
    return {"bins": dict(bins), "n": len(obs), "set_sizes_max": max(sizes) if sizes else None,
            "positions_per_item": n_positions}


def reach_stats(um: UnitModel, obs: list, T) -> dict[str, float]:
    """Share of answers equal to some slipping member's answer (a deterministic member's answer, or
    one of a set-valued member's solutions); share beyond every slipping member's reach (only q, or a
    stored noise model's lump, gives them positive probability); share that are a special token."""
    s = T.slips
    exact = (T.A[:, s] > 0).any(1)
    reach = ((T.A[:, s] + T.B0[:, s] + T.C[:, s].sum(2)) > 0).any(1)
    special = np.array([um.items[ob.item].space.is_special(ob.key) for ob in obs])
    return {"exact": float(exact.mean()), "beyond_reach": float((~reach).mean()), "special": float(special.mean())}


def unit_facts(um: UnitModel) -> dict[str, Any]:
    """Facts about the unit's items that the doc quotes: ground truth, solution-set sizes, positions
    per item, and the stored distributions' sizes."""
    gts = [it["ground_truth"] for it in um.unit.items]
    out: dict[str, Any] = {"n_items": len(um.items), "n_cells": len(set(um.unit.cells)), "n_clusters": um.unit.n_clusters,
                           "positions_per_item": sorted({im.space.n for im in um.items if hasattr(im.space, "n")})}
    if all("satisfiable" in g for g in gts):
        out["satisfiable_items"] = sum(1 for g in gts if g["satisfiable"])
    if all("chromatic_number" in g for g in gts):
        out["chromatic_numbers"] = sorted({g["chromatic_number"] for g in gts})
    sizes: dict[str, list[int]] = defaultdict(list)
    dists: dict[str, list[tuple[int, float]]] = defaultdict(list)
    for im in um.items:
        for lbl, p in im.preds.items():
            if p.kind == "set":
                sizes[lbl].append(p.sol.size)
            elif p.kind == "dist":
                dists[lbl].append((len([k for k in p.dist if not k.startswith("_")]), p.dist.get("_other", 0.0)))
    out["set_sizes"] = {l: {"min": min(v), "median": float(np.median(v)), "max": max(v)} for l, v in sizes.items()}
    out["stored_distributions"] = {l: {"outcomes_min": min(n for n, _ in v), "outcomes_max": max(n for n, _ in v),
                                       "other_mass_max": max(o for _, o in v)} for l, v in dists.items()}
    return out


def lump_shares(um: UnitModel, obs: list, T, fitj: dict[str, Any]) -> dict[str, Any]:
    """Stored-distribution members (RO-FF, NOISY-EXACT) keep a Monte Carlo tail, `_other`, that the
    likelihood spreads exactly like q. For each such group: its mean `_other` mass per item, and the
    share of its fitted responsibility (posterior weight summed over answers) that arrives through
    that lump rather than through its listed outcomes."""
    from reasoning_heuristics.identify.spaces import trunc_geom

    labels = [g.name for g in um.columns]
    w = fitj["weights"]
    pi = np.array([w[l]["pi"] if isinstance(w[l]["pi"], (int, float)) else np.nan for l in labels] + [w[UNEXPLAINED]["pi"]])
    if np.isnan(pi).any():
        return {}
    eps, rho = fitj["eps"], fitj["rho"]
    S = T.B0 + T.C @ trunc_geom(rho)
    L = (1 - eps) * T.A + eps * S
    L = np.where(T.slips[None, :], L, T.A)  # stored distributions do not slip
    tot = (pi[None, :-1] * L * T.avail).sum(1) + pi[-1] * T.Q
    out = {}
    for j, g in enumerate(um.columns):
        if T.slips[j]:
            continue
        other = np.array([(um.pred(ob.item, g.members[0]).dist or {}).get("_other", 0.0) for ob in obs])
        resp = pi[j] * L[:, j] / tot
        resp_other = pi[j] * other * T.Q / tot
        out[g.name] = {"mean_other_mass": float(other.mean()), "responsibility": float(resp.sum()),
                       "responsibility_via_other": float(resp_other.sum()),
                       "share_via_other": float(resp_other.sum() / resp.sum()) if resp.sum() > 0 else None}
    return out


def check_ties(set_name: str, name: str, um: UnitModel) -> None:
    """Members that must share one weight on this unit (MUST_TIE) are one tie group, or we stop."""
    tied = MUST_TIE.get((set_name, name))
    if tied and not any(set(tied) <= set(g.members) for g in um.columns):
        raise AssertionError(f"{set_name} {name}: {tied} are not one tie group on these items; the gate covers only their sum")


def fit_job(args: tuple) -> dict[str, Any]:
    set_name, name, run_id, n_boot, n_perm = args
    run = _CTX["runs"][run_id]
    unit = _unit(set_name, name)
    um = UnitModel(unit)
    check_ties(set_name, name, um)
    rs = [r for r, it in run["pairs"] if unit_name(it) == name]
    seed = job_seed("fit", name, run_id)
    rep = fit_unit(um, rs, n_boot=n_boot, seed=seed, n_perm=n_perm)
    obs, _ = um.observations(rs)
    T = um.tensors(obs)
    # BCa next to the percentile intervals, from the same bootstrap draws: fit_unit's first use of its
    # rng is this same fit, so seeding alike reproduces its replicates (asserted), and the jackknife
    # (leave one cluster out) draws nothing
    res = fit(T, n_boot=n_boot, rng=np.random.default_rng(seed), jackknife=True)
    w = rep["fit"]["weights"]
    for j, lab in enumerate(res.labels):
        if isinstance(w[lab]["pi"], (int, float)) and not (abs(w[lab]["lo"] - res.lo[j]) < 1e-3 and abs(w[lab]["hi"] - res.hi[j]) < 1e-3):
            raise AssertionError(f"{name} {run_id} {lab}: the refit's bootstrap differs from fit_unit's")
    blo, bhi = bca_interval(res.boot, res.pi, res.jack)
    rep["bca"] = {lab: [float(a), float(b)] for lab, a, b in zip(res.labels, blo, bhi)}
    counts = agreement.error_agreement(um, obs, ties="include")
    rep["ea_counts"] = {g: {"n": v.n, "agree": v.agree, "n_h_wrong": v.n_h_wrong,
                            "co_agree": (v.co_error or 0.0) * v.n_h_wrong} for g, v in counts.items()}
    # the chance that a q draw ("none of the above") is exactly a deterministic member's answer
    qx: dict[str, list[float]] = defaultdict(list)
    for ob in obs:
        im = um.items[ob.item]
        for g in um.columns:
            p = um.pred(ob.item, g.members[0])
            if p.kind == "det":
                qx[g.name].append(math.exp(im.space.log_q(p.key)))
    rep["q_exact_chance"] = {g: max(v) for g, v in qx.items()}
    rep["near"] = nearest_distances(um, obs)
    rep["reach"] = reach_stats(um, obs, T)
    rep["lumps"] = lump_shares(um, obs, T, rep["fit"])
    rep["unit_facts"] = unit_facts(um)
    rep["special_check"] = special_check(um)
    rep["seed"] = seed
    rep["item_set"] = set_name
    return {"unit": name, "run_id": run_id, "report": to_jsonable(rep)}


def recovery_job(args: tuple) -> dict[str, Any]:
    """Fake models answering the unit's items from a fitted mixture, refitted; one chunk of replicates."""
    set_name, name, run_id, planted, q, eps, rho, reps, n_boot, chunk = args
    run = _CTX["runs"][run_id]
    unit = _unit(set_name, name)
    um = UnitModel(unit)
    rs = [r for r, it in run["pairs"] if unit_name(it) == name]
    obs_real, _ = um.observations(rs)
    keep = Counter(ob.item for ob in obs_real)  # the real design: the items that have an answer
    sc = Scenario("at-estimate", "mix", weights=planted, q=q, eps=eps, rho=rho)
    truth = truth_vector(um, planted, q)
    rng = np.random.default_rng(job_seed("recovery", name, run_id, str(chunk)))
    out = []
    for _ in range(reps):
        sim = [ob for ob in simulate(um, sc, rng) if keep.get(ob.item)]
        T = um.tensors(sim)
        res = fit(T, n_boot=n_boot, rng=rng, jackknife=True)
        blo, bhi = bca_interval(res.boot, res.pi, res.jack)
        out.append({"pi": res.pi.tolist(), "lo": res.lo.tolist(), "hi": res.hi.tolist(), "bca_lo": blo.tolist(),
                    "bca_hi": bhi.tolist(), "eps": res.eps, "rho": res.rho, "reach": reach_stats(um, sim, T)})
    return {"unit": name, "run_id": run_id, "chunk": chunk, "truth": truth.tolist(), "labels": [g.name for g in um.columns] + [UNEXPLAINED],
            "replicates": out}


def summarise_recovery(chunks: list[dict[str, Any]]) -> dict[str, Any]:
    labels, truth = chunks[0]["labels"], np.array(chunks[0]["truth"])
    reps = [r for c in sorted(chunks, key=lambda c: c["chunk"]) for r in c["replicates"]]
    pi = np.array([r["pi"] for r in reps])
    planted = [j for j in range(len(labels)) if truth[j] > 0]
    by_method = {}
    for method, (klo, khi) in (("percentile", ("lo", "hi")), ("bca", ("bca_lo", "bca_hi"))):
        lo = np.array([r[klo] for r in reps])
        hi = np.array([r[khi] for r in reps])
        cover = (lo <= truth[None, :] + 1e-12) & (truth[None, :] - 1e-12 <= hi)
        width = hi - lo
        by_method[method] = {"coverage": cover.mean(0), "median_width": np.median(width, 0),
                             "planted_median_width": float(np.median(width[:, planted]))}
    q = {}
    for j, lab in enumerate(labels):
        q[lab] = {"truth": float(truth[j]), "mean": float(pi[:, j].mean()), "bias": float(pi[:, j].mean() - truth[j]),
                  "coverage": float(by_method["percentile"]["coverage"][j]),
                  "median_width": float(by_method["percentile"]["median_width"][j]),
                  "coverage_bca": float(by_method["bca"]["coverage"][j]),
                  "median_width_bca": float(by_method["bca"]["median_width"][j])}
    bias_ok = max(abs(v["bias"]) for v in q.values()) <= 0.05
    verdicts = {}
    for method, bm in by_method.items():
        cov = bm["coverage"]
        gates = {"bias": bias_ok, "coverage": float(min(cov[j] for j in planted)) >= 0.9, "width": bm["planted_median_width"] <= 0.2}
        verdicts[method] = {"gates": gates, "pass": all(gates.values()), "min_coverage": float(min(cov[j] for j in planted)),
                            "worst_coverage_quantity": labels[min(planted, key=lambda j: cov[j])],
                            "median_width": bm["planted_median_width"]}
    pv = verdicts["percentile"]
    return {"replicates": len(reps), "quantities": q,
            "max_abs_bias": max(abs(v["bias"]) for v in q.values()),
            "worst_bias_quantity": max(q, key=lambda k: abs(q[k]["bias"])),
            "min_coverage": pv["min_coverage"], "worst_coverage_quantity": pv["worst_coverage_quantity"],
            "median_width": pv["median_width"], "gates": pv["gates"], "pass": pv["pass"], "bca": verdicts["bca"],
            "eps_mean": float(np.mean([r["eps"] for r in reps])), "rho_mean": float(np.mean([r["rho"] for r in reps])),
            "simulated": {k: {"mean": float(np.mean([r["reach"][k] for r in reps])),
                              "p05_p95": [float(np.percentile([r["reach"][k] for r in reps], p)) for p in (5, 95)]}
                          for k in ("exact", "beyond_reach", "special")}}


def planted_from_fit(rep: dict[str, Any], um_groups: list[list[str]]) -> tuple[dict[str, float], float]:
    """The fitted weights as a fake model: every group's weight on its first member, weights below
    PLANT_MIN set to 0, renormalised with q."""
    w = rep["fit"]["weights"]
    raw = {}
    for members in um_groups:
        g = " = ".join(members) if len(members) > 1 else members[0]
        if g in w and isinstance(w[g]["pi"], (int, float)):
            raw[members[0]] = float(w[g]["pi"])
    q = float(w[UNEXPLAINED]["pi"])
    raw = {k: (v if v >= PLANT_MIN else 0.0) for k, v in raw.items()}
    q = q if q >= PLANT_MIN else 0.0
    tot = sum(raw.values()) + q
    return {k: v / tot for k, v in raw.items() if v > 0}, q / tot


# =============================================================================================
# Tables
# =============================================================================================


def f3(x: float | None) -> str:
    return "–" if x is None else f"{x:.3f}"


def f2(x: float | None) -> str:
    return "–" if x is None else f"{x:.2f}"


def pct(a: int, b: int) -> str:
    return "–" if not b else f"{a}/{b} ({100 * a / b:.0f}%)"


def pval(p: float | None) -> str:
    if p is None:
        return "–"
    return f"{p:.3f}"


def md_table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(h.replace("|", "\\|") for h in header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |" for r in rows]
    return "\n".join(out)


_LABELS: dict[str, str] = {}  # run id -> label, set by render() from the JSON


def label_of(run_id: str) -> str:
    return _LABELS[run_id]


def doc_pilot() -> list[tuple[str, str]]:
    return [(rid, label_of(rid)) for rid in DOC_PILOT]


def table_runs(meta: list[dict[str, Any]]) -> str:
    rows = []
    for m in meta:
        prov = ", ".join(f"{k} ({v})" for k, v in (m["providers_served"] or {}).items())
        drift = [p.split("/")[-1].split("_dev")[0] for p, d in m["item_drift"].items() if not d["same"]]
        ct = m.get("cache_twin")
        cache = f"{m['from_cache']}" + (f" ({ct['cached_same_generation_as_dev_run']} are the dev run's own responses)" if ct else "")
        rows.append([f"`{m['run_id']}`", m["model"], m["condition"], f"{m['max_tokens']:,}", prov, m["n_records"],
                     cache, f"{m['max_pre_answer_tokens']} ({m['pre_answer_over_20']} over 20)",
                     f"${m['spent_usd']:.4f}", m["scorer_version"], ", ".join(sorted(drift)) if drift else "none"])
    return md_table(["Run", "Model", "Condition", "max_tokens", "Served by", "Responses", "From the response cache",
                     "Visible working: max pre_answer_tokens", "API cost", "Scorer", "Item files changed since the run"], rows)


def table_units(special: dict[str, dict[str, Any]], unit_items: dict[str, int]) -> str:
    rows = []
    for name in sorted(unit_items):
        sc = special[name]
        tok = "; ".join(f"{k} ({v})" for k, v in sorted(sc["det_special_predictions"].items())) or "none"
        if sc["dist_members_with_special_mass"]:
            tok += "; stored distributions: " + ", ".join(sorted(sc["dist_members_with_special_mass"]))
        if name in DOC_FIT_UNITS:
            rows.append([name, unit_items[name], "**fitted**", "the mixture passes the three gates at 20 per cell on the regenerated items (see the text)", tok])
        else:
            rows.append([name, unit_items[name], "descriptive only", not_fitted_reason(name, "pc20"), tok])
    return md_table(["Unit (20 per cell)", "Items", "Here", "Why (docs/RECOVERY.md)",
                     "Members predicting UNSAT / IMPOSSIBLE / X (items)"], rows)


def table_dev_units(unit_items: dict[str, int]) -> str:
    rows = []
    for name in sorted(unit_items):
        by_design = NOT_FITTED.get(name) or NOT_FITTED.get(name.split("/")[0], "")
        rows.append([name, unit_items[name], by_design])
    return md_table(["Unit (5 per cell)", "Items", "Gate status at larger sizes (docs/RECOVERY.md)"], rows)


def weights_table(name: str, fits: dict[str, dict[str, Any]]) -> str:
    runs = list(DOC_PILOT)
    labels = list(fits[runs[0]]["fit"]["weights"].keys())
    rows = []
    for lab in labels:
        row = [lab if lab != UNEXPLAINED else "**unexplained mass π₀ (q)**"]
        for rid in runs:
            w = fits[rid]["fit"]["weights"][lab]
            if isinstance(w["pi"], str):
                row += [f"not identified, range [{w['range'][0]:.3f}, {w['range'][1]:.3f}]", "–"]
            else:
                b = fits[rid]["bca"][lab]
                row += [f"{w['pi']:.3f} [{w['lo']:.3f}, {w['hi']:.3f}]", f"[{b[0]:.3f}, {b[1]:.3f}]"]
        rows.append(row)
    for key, fmt in (("eps", "ε (slip rate; cap 0.5)"), ("rho", "ρ (slip shape; grid 0.02–0.9)")):
        row = [fmt]
        for rid in runs:
            f = fits[rid]["fit"]
            ci = f[f"{key}_ci"]
            row += [f"{f[key]:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]", "–"]
        rows.append(row)
    rows.append(["answers fitted (rows) / clusters"] + [x for r in runs for x in (f"{fits[r]['fit']['n_rows']} / {fits[r]['fit']['n_clusters']}", "")])
    rows.append(["log-likelihood"] + [x for r in runs for x in (f"{fits[r]['fit']['loglik']:.1f}", "")])
    header = ["Weight"] + [x for r in runs for x in (f"{label_of(r)}: π [95% percentile]", "BCa")]
    return md_table(header, rows)


def ident_table(name: str, fits: dict[str, dict[str, Any]]) -> str:
    rid = DOC_PILOT[0]
    rep = fits[rid]
    idf = rep["identifiability"]
    diag = rep["diagnostics"]
    ties = [" = ".join(g) for g in diag["groups"] if len(g) > 1]
    pairs, seen = [], set()
    for d in diag["least_separated"]:
        key = frozenset((d["group"], d["nearest"]))
        if key not in seen:
            seen.add(key)
            pairs.append(f"{d['group']} vs {d['nearest']}: {d['separating_items']} of {diag['n_items']} items")
    dt = sorted({" = ".join(t) for r in fits.values() for t in r["fit"].get("data_ties", [])})
    sc = rep["special_check"]
    special = ", ".join(f"{k} ({v} items)" for k, v in sc["det_special_predictions"].items()) or "none"
    special += f"; stored distributions with special-token mass: {', '.join(sc['dist_members_with_special_mass']) or 'none'}"
    special += f"; special tokens in the answer space: {', '.join(sc['space_specials']) or 'none'}"
    same = all(fits[r]["identifiability"]["rank"] == idf["rank"] for r in fits)
    rows = [["rank / columns (groups + q)", f"{idf['rank']} / {len(idf['columns'])}" + ("" if same else " (differs between the runs' draws)")],
            ["σ_min / σ_max of the design (columns scaled)", f"{idf['sigma_ratio']:.3f}"],
            ["linear dependencies", "; ".join(d["statement"] for d in idf["dependencies"]) or "none"],
            ["weights reported as not identified (with ranges)", ", ".join(idf["not_identified"]) or "none"],
            ["tie groups (identical predictions on every item; one weight)", "; ".join(ties) or "none"],
            ["members folded into q (identical to q on every item)", ", ".join(diag["folded_into_q"]) or "none"],
            ["least-separated pairs", "; ".join(pairs[:3])],
            ["data ties in either fit (identical likelihood on every answered row)", "; ".join(dt) or "none"],
            ["members that predict UNSAT / IMPOSSIBLE / X", special]]
    return md_table(["Identifiability: " + name, ""], rows)


def near_table(fits_by_unit: dict[str, dict[str, dict[str, Any]]]) -> str:
    order = ["0", "1", "2", "3", "4-6", ">6", "special token"]
    rows = []
    for name in DOC_FIT_UNITS:
        for rid, lab in doc_pilot():
            rep = fits_by_unit[name][rid]
            nb = rep["near"]
            n = nb["n"]
            cells = [f"{nb['bins'].get(k, 0)} ({100 * nb['bins'].get(k, 0) / n:.0f}%)" if nb["bins"].get(k, 0) else "0" for k in order]
            rows.append([name, lab, n, "/".join(map(str, nb["positions_per_item"]))] + cells)
    return md_table(["Unit", "Run", "Answers", "Positions per item"] + [f"d = {k}" if k[0].isdigit() or k[0] == ">" else k for k in order], rows)


def lumps_table(fits_by_unit: dict[str, dict[str, dict[str, Any]]]) -> str:
    rows = []
    for name in DOC_FIT_UNITS:
        for rid, lab in doc_pilot():
            rep = fits_by_unit[name][rid]
            for g, v in rep.get("lumps", {}).items():
                w = rep["fit"]["weights"][g]["pi"]
                rows.append([name, lab, g, f"{v['mean_other_mass']:.2f}", f"{w:.3f}",
                             "–" if v["share_via_other"] is None else f"{v['share_via_other']:.2f}"])
    if not rows:
        return "No stored-distribution member on the fitted units."
    return md_table(["Unit", "Run", "Stored-distribution member", "Mean `_other` mass per item", "Fitted π",
                     "Share of its fitted responsibility that comes through `_other` (q-shaped)"], rows)


def recovery_table(fits_by_unit: dict[str, dict[str, dict[str, Any]]], rec: dict[str, dict[str, dict[str, Any]]]) -> str:
    rows = []
    for name in DOC_FIT_UNITS:
        for rid, lab in doc_pilot():
            r = rec[name][rid]
            g = r["gates"]
            pl = r["planted"]
            verdict = "PASS" if r["pass"] else "fail (" + ", ".join(k for k, v in g.items() if not v) + ")"
            bv = r["bca"]
            bverdict = "PASS" if bv["pass"] else "fail (" + ", ".join(k for k, v in bv["gates"].items() if not v) + ")"
            rows.append([name, lab, f"{pl['eps']:.2f} / {pl['rho']:.2f}", r["replicates"],
                         f"{r['max_abs_bias']:.3f} ({r['worst_bias_quantity']})",
                         verdict, f"{r['min_coverage']:.2f} ({r['worst_coverage_quantity']})", f"{r['median_width']:.3f}",
                         bverdict, f"{bv['min_coverage']:.2f} ({bv['worst_coverage_quantity']})", f"{bv['median_width']:.3f}"])
    return md_table(["Unit", "Run whose fit is planted", "planted ε / ρ", "Replicates", "max |bias|",
                     "Percentile: gates", "min coverage", "median width", "BCa: gates", "min coverage", "median width"], rows)


def ppc_table(fits_by_unit: dict[str, dict[str, dict[str, Any]]], rec: dict[str, dict[str, dict[str, Any]]]) -> str:
    """Observed statistics against the same statistics of fake data drawn from the fitted mixture."""
    rows = []
    for name in DOC_FIT_UNITS:
        for rid, lab in doc_pilot():
            obs = fits_by_unit[name][rid]["reach"]
            sim = rec[name][rid]["simulated"]
            cells = []
            for k in ("exact", "beyond_reach", "special"):
                lo, hi = sim[k]["p05_p95"]
                flag = "" if lo - 1e-9 <= obs[k] <= hi + 1e-9 else " **outside**"
                cells.append(f"{obs[k]:.2f} vs {sim[k]['mean']:.2f} [{lo:.2f}, {hi:.2f}]{flag}")
            rows.append([name, lab] + cells)
    return md_table(["Unit", "Run", "Answers equal to a member's answer: observed vs fitted model [5–95%]",
                     "Answers beyond every member's slip reach", "Special-token answers (UNSAT)"], rows)


def recovery_detail_table(rec: dict[str, dict[str, dict[str, Any]]]) -> str:
    rows = []
    for name in DOC_FIT_UNITS:
        for rid, lab in doc_pilot():
            for q, v in rec[name][rid]["quantities"].items():
                if v["truth"] <= 0 and abs(v["bias"]) < 0.02:
                    continue
                planted = v["truth"] > 0
                rows.append([name, lab, q, f"{v['truth']:.3f}", f"{v['mean']:.3f}", f"{v['bias']:+.3f}",
                             f"{v['coverage']:.2f}" if planted else "–", f"{v['coverage_bca']:.2f}" if planted else "–",
                             f"{v['median_width']:.3f}"])
    return md_table(["Unit", "Run", "Quantity", "Planted", "Mean estimate", "Bias", "Coverage, percentile", "Coverage, BCa",
                     "Median width (percentile)"], rows)


def agreement_table(name: str, fits: dict[str, dict[str, Any]]) -> str:
    """EA, co-error and the weight, each with its within-cell permutation baseline ('chance'), lift
    and one-sided p-value. EA's denominator (items where the answer and the member are both wrong)
    and co-error's (items where the member is wrong) are given with the counts."""
    rows = []
    for rid, lab in doc_pilot():
        rep = fits[rid]
        ea = rep["error_agreement"]
        wl = rep.get("weight_lift", {})
        exch = ea["exchangeable"]
        dens = rep.get("ea_counts", {})
        for g in list(ea["ea"]) + [UNEXPLAINED]:
            v = ea["ea"].get(g, {})
            co = ea["co_error"].get(g, {})
            w = (wl.get("by_group") or {}).get(g, {})
            n = dens.get(g, {})
            rows.append([lab, g, f"{exch:.2f}",
                         f3(v.get("observed")) + (f" ({n['agree']:.0f}/{n['n']:.0f})" if n.get("n") else ""),
                         f3(v.get("baseline")), f3(v.get("lift")), pval(v.get("p_value")),
                         f3(co.get("observed")) + (f" ({n['co_agree']:.0f}/{n['n_h_wrong']:.0f})" if n.get("n_h_wrong") else ""),
                         f3(co.get("baseline")), f3(co.get("lift")), pval(co.get("p_value")),
                         f3(w.get("observed")), f3(w.get("baseline")), f3(w.get("lift")), pval(w.get("p_value"))])
    return md_table(["Run", "Member group", "Exchangeable share", "EA (agree / both wrong)", "chance", "lift", "p",
                     "co-error (agree / member wrong)", "chance", "lift", "p", "π", "chance", "lift", "p"], rows)


def denominators_table(fits_by_unit: dict[str, dict[str, dict[str, Any]]], desc_pc20: dict[str, dict[str, Any]]) -> str:
    """How many answers are wrong, and how many items each member gets wrong (EA's denominators)."""
    rows = []
    for name in DOC_FIT_UNITS:
        for rid, lab in doc_pilot():
            d = desc_pc20[rid][name]
            rows.append([name, lab, d["ok"], d["ok"] - d["correct"], d["correct"]])
    return md_table(["Unit", "Run", "ok answers", "wrong", "correct"], rows)


def excluded_table(fits_by_unit: dict[str, dict[str, dict[str, Any]]]) -> str:
    rows = []
    for name in DOC_FIT_UNITS:
        for rid, lab in doc_pilot():
            ex = fits_by_unit[name][rid]["excluded"]
            total = sum(ex["responses_by_cell"].values())
            if not ex["by_cell"]:
                rows.append([name, lab, "–", "none", f"0 of {total}"])
                continue
            for cell, cats in ex["by_cell"].items():
                n = ex["responses_by_cell"][cell]
                rows.append([name, lab, cell, ", ".join(f"{c} {k}" for c, k in sorted(cats.items())), f"{sum(cats.values())} of {n}"])
    return md_table(["Unit", "Run", "Cell", "Excluded (category count)", "Of the cell's responses"], rows)


def descriptive_table(desc: dict[str, dict[str, Any]], run_ids: list[str], fitted: set[str]) -> str:
    rows = []
    names = sorted({u for rid in run_ids for u in desc[rid]})
    for name in names:
        for rid in run_ids:
            d = desc[rid].get(name)
            if d is None:
                continue
            c = d["categories"]
            other = ", ".join(f"{k} {v}" for k, v in c.items() if k != "ok" and v)
            top = "; ".join(f"{m['members']} {m['answers']}" for m in d["members_matched"][:3]) or "–"
            sets = "; ".join(f"{m['members']} {m['answers']}" for m in d["sets_matched"][:2]) or "–"
            spec = ", ".join(f"{k} {v}" for k, v in sorted(d["special_answers"].items()))
            mr = d["median_reasoning_tokens"]
            toks = f"{mr:,.0f} / {d['median_completion_tokens']:,.0f}" if mr is not None else "–"
            rows.append([name + (" (fitted)" if name in fitted else ""), label_of(rid), d["n"], d["ok"], other or "–",
                         pct(d["correct"], d["ok"]),
                         pct(d["valid"], d["valid_defined"]) if d["valid_defined"] else "–",
                         pct(d["any_member_match"], d["ok"]), pct(d["wrong_member_match"], d["wrong"]), top, sets,
                         spec or "–", toks])
    return md_table(["Unit", "Run", "Responses", "ok", "Not ok", "Correct of ok", "Valid of ok",
                     "Match ≥1 member (of ok)", "Wrong answers matching ≥1 member", "Members matched most (answers)",
                     "Sets matched (answers)", "Special-token answers", "Median tokens: reasoning / completion"], rows)


def render(results: dict[str, Any]) -> dict[str, str]:
    """The doc's tables, for the doc's runs (DOC_PILOT, DOC_DEV) and units (DOC_FIT_UNITS) only."""
    _LABELS.clear()
    _LABELS.update({m["run_id"]: m["label"] for m in results["runs"]})
    missing = [r for r in DOC_PILOT + DOC_DEV if r not in _LABELS]
    if missing:
        raise KeyError(f"the doc's runs are not in the results: {missing}")
    fits = results["fits"]
    rec = results["recovery_at_estimate"]
    by_id = {m["run_id"]: m for m in results["runs"]}
    t = {"runs": table_runs([by_id[r] for r in DOC_PILOT + DOC_DEV]),
         "units": table_units(results["special_tokens"]["pc20"], results["unit_items"]["pc20"]),
         "dev_units": table_dev_units(results["unit_items"]["dev"])}
    for name in DOC_FIT_UNITS:
        key = name.replace("/", "_").replace(" ", "_")
        t[f"weights_{key}"] = weights_table(name, fits[name])
        t[f"ident_{key}"] = ident_table(name, fits[name])
        t[f"agreement_{key}"] = agreement_table(name, fits[name])
    t["near"] = near_table(fits)
    t["lumps"] = lumps_table(fits)
    t["recovery"] = recovery_table(fits, rec)
    t["ppc"] = ppc_table(fits, rec)
    t["recovery_detail"] = recovery_detail_table(rec)
    t["excluded"] = excluded_table(fits)
    t["wrong"] = denominators_table(fits, results["descriptive"])
    t["desc_pilot"] = descriptive_table(results["descriptive"], DOC_PILOT, set(DOC_FIT_UNITS))
    t["desc_dev"] = descriptive_table(results["descriptive"], DOC_DEV, set())
    return t


def splice(doc: str, tables: dict[str, str]) -> str:
    for name, body in tables.items():
        begin, end = f"<!-- BEGIN prelim:{name} -->", f"<!-- END prelim:{name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise ValueError(f"the doc must contain exactly one {begin} ... {end} block")
        a = doc.index(begin) + len(begin)
        b = doc.index(end)
        doc = doc[:a] + "\n" + body + "\n" + doc[b:]
    return doc


# =============================================================================================
# Main
# =============================================================================================


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--runs-root", type=Path, default=REPO / "data" / "runs", help="directory holding the run directories")
    ap.add_argument("--n-boot", type=int, default=2000, help="cluster-bootstrap draws per fit")
    ap.add_argument("--n-perm", type=int, default=2000, help="within-cell permutations per baseline")
    ap.add_argument("--recovery-reps", type=int, default=100, help="fake-model replicates per fit for recovery at the estimate")
    ap.add_argument("--recovery-boot", type=int, default=200, help="bootstrap draws per recovery replicate")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", type=Path, default=OUT_JSON)
    ap.add_argument("--doc", type=Path, default=DOC)
    ap.add_argument("--check", action="store_true", help="regenerate and compare the doc's tables; write nothing")
    ap.add_argument("--render-only", action="store_true",
                    help="rewrite the doc's tables from the existing --out JSON without recomputing; with --check, "
                         "only compare (a fast check that the doc's tables match the committed numbers)")
    ap.add_argument("--no-doc", action="store_true", help="write the JSON only; leave the doc alone")
    args = ap.parse_args(argv)
    t0 = time.time()

    if args.render_only:  # tables from the JSON alone: no item set or run is read
        results = json.loads(args.out.read_text())
        doc = args.doc.read_text()
        new_doc = splice(doc, render(results))
        if args.check:
            if new_doc != doc:
                print(f"the doc's tables differ from those rendered from {args.out}", file=sys.stderr)
                return 1
            print("doc tables match the JSON")
            return 0
        args.doc.write_text(new_doc)
        print(f"re-rendered the tables in {args.doc} from {args.out}")
        return 0

    found, skipped = discover_runs(args.runs_root)
    sets: dict[str, dict[str, Any]] = {}
    runs = {rid: load_run(args.runs_root, rid, sets) for rid in found}
    _CTX.update(sets=sets, runs=runs)
    meta = [run_meta(runs[rid]) for rid in found]
    for m in meta:  # a cached response is the earlier run's own response to the same prompt
        if m["item_set"] == "dev" or "dev" not in sets:
            continue
        twins = [o for o in meta if o["item_set"] == "dev" and o["model"] == m["model"] and o["condition"] == m["condition"]]
        if not twins:
            continue
        twin = twins[0]["run_id"]
        gens = {r.get("generation_id") for r in runs[twin]["records"]}
        cached = [r for r in runs[m["run_id"]]["records"] if r.get("from_cache")]
        own = sets[m["item_set"]]["by_id"]
        m["cache_twin"] = {"dev_run": twin, "cached": len(cached),
                           "cached_same_generation_as_dev_run": sum(1 for r in cached if r.get("generation_id") in gens),
                           "items_shared_with_dev_set": len(set(own) & set(sets["dev"]["by_id"])),
                           "cached_by_unit": dict(Counter(unit_name(own[r["item_id"]]) for r in cached))}
    descriptive = {rid: describe(runs[rid], sets[runs[rid]["item_set"]]) for rid in found}
    special_tokens = {s: {name: special_check(UnitModel(_unit(s, name))) for name in sorted(v["groups"])}
                      for s, v in sorted(sets.items()) if s != "dev"}

    fit_targets = [(runs[rid]["item_set"], name, rid) for rid in found for name in GATED.get(runs[rid]["item_set"], [])
                   if name in descriptive[rid]]
    ctx = mp.get_context("fork")
    with ctx.Pool(args.workers) as pool:
        jobs = [(s, name, rid, args.n_boot, args.n_perm) for s, name, rid in fit_targets]
        fitted = pool.map(fit_job, jobs, chunksize=1)
        fits: dict[str, dict[str, Any]] = defaultdict(dict)
        for f in fitted:
            fits[f["unit"]][f["run_id"]] = f["report"]
        rjobs = []
        planted_by: dict[tuple[str, str], Any] = {}
        for s, name, rid in fit_targets:
            rep = fits[name][rid]
            planted, q = planted_from_fit(rep, rep["diagnostics"]["groups"])
            eps, rho = rep["fit"]["eps"], rep["fit"]["rho"]
            planted_by[(name, rid)] = {"weights": planted, "q": q, "eps": eps, "rho": rho}
            n_chunks = max(1, min(10, args.recovery_reps // 10))
            per = [args.recovery_reps // n_chunks + (1 if k < args.recovery_reps % n_chunks else 0) for k in range(n_chunks)]
            rjobs += [(s, name, rid, planted, q, eps, rho, per[k], args.recovery_boot, k) for k in range(n_chunks) if per[k]]
        chunks = pool.map(recovery_job, rjobs, chunksize=1) if args.recovery_reps else []
    by_fit: dict[tuple[str, str], list] = defaultdict(list)
    for c in chunks:
        by_fit[(c["unit"], c["run_id"])].append(c)
    recovery: dict[str, dict[str, Any]] = defaultdict(dict)
    for (name, rid), cs in by_fit.items():
        recovery[name][rid] = {**summarise_recovery(cs), "planted": planted_by[(name, rid)]}

    results = {
        "description": "Preliminary results 2026-11-18 (dev split); see docs/results/2026-11-18-preliminary.md",
        "command": " ".join([Path(sys.argv[0]).name] + (argv if argv is not None else sys.argv[1:])),
        "git": git_state(), "python": platform.python_version(), "numpy": np.__version__,
        "settings": {"n_boot": args.n_boot, "n_perm": args.n_perm, "recovery_reps": args.recovery_reps,
                     "recovery_boot": args.recovery_boot, "plant_min": PLANT_MIN, "eps_max": EPS_MAX,
                     "rho_grid": [float(RHO_GRID[0]), float(RHO_GRID[-1])], "intervals": "percentile cluster bootstrap (primary) and BCa from the same draws"},
        "schema": SCHEMA,
        "item_sets": {k: {"paths": v["paths"], "sha256": v["sha256"], "n_items": len(v["items"])} for k, v in sorted(sets.items())},
        "unit_items": {k: {name: len(its) for name, its in sorted(v["groups"].items())} for k, v in sorted(sets.items())},
        "runs": meta, "skipped_runs": skipped, "gated_units": GATED,
        "must_tie": [{"item_set": s, "unit": u, "members": list(m)} for (s, u), m in MUST_TIE.items()],
        "not_fitted": {s: {name: not_fitted_reason(name, s) for name in sorted(v["groups"]) if name not in GATED.get(s, [])}
                       for s, v in sorted(sets.items())},
        "doc_runs": {"pilot": DOC_PILOT, "dev": DOC_DEV, "fit_units": DOC_FIT_UNITS},
        "descriptive": descriptive, "special_tokens": special_tokens, "fits": fits, "recovery_at_estimate": recovery,
    }
    results = to_jsonable(results)
    if not args.check:  # the numbers first, so a table-format failure never costs the computation
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(results, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    if args.no_doc:
        print(f"wrote {args.out} ({len(found)} runs, {len(fit_targets)} fits; {round(time.time() - t0)} s)")
        return 0
    tables = render(results)
    doc = args.doc.read_text()
    new_doc = splice(doc, tables)
    if args.check:
        if new_doc != doc:
            print("the doc's generated tables differ from what the script computes; rerun without --check", file=sys.stderr)
            return 1
        print("doc tables up to date")
        return 0
    args.doc.write_text(new_doc)
    print(f"wrote {args.out} and {len(tables)} tables in {args.doc} ({round(time.time() - t0)} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
