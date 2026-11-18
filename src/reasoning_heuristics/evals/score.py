"""(Re-)score a run from its raw outputs on disk (DESIGN §5 rule 3: when the scorer changes,
everything is re-scored from raw outputs).

    python -m reasoning_heuristics.evals.score data/runs/<run_id> [data/runs/<other> ...]
    python -m reasoning_heuristics.evals.score data/runs/forced-2/<select>/<source_run_id>    (a forced-answer pass;
        a budget pass's are in forced-2/<select>-k<K>/ or <select>-f<F>/, force-1's in data/runs/forced/<source_run_id>)

Reads manifest.json (which item files, with their SHA-256) and raw.jsonl.gz; writes
scored.jsonl.gz, scoring.json (scorer version, git SHA, counts) and REPORT.md. The item files
must still hash to what the manifest recorded. After the item sets are regenerated, score
against the files as they were with --items-at-run-sha (`git show <run sha>:<path>`, checked
against the manifest's SHA-256), or knowingly against today's files with --allow-item-drift.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from reasoning_heuristics.evals.manifest import REPO, git_info, sha256_file, utc_now, versions, write_json
from reasoning_heuristics.evals.report import build_report
from reasoning_heuristics.evals.scoring import SCORER_VERSION, ItemContext, ResponseView, score_response

SCORED = "scored.jsonl.gz"
# a budget pass's fields (force.py --truncate-at, --truncate-frac), carried from each raw record to its scored one
BUDGET_FIELDS = ("trace_tokens", "cut_tokens", "budget_k", "budget_frac", "provider_reasoning_tokens")


def git_show(ref: str, rel: str) -> bytes:
    """The bytes of a committed file at a git ref (`git show <ref>:<path>`)."""
    try:
        return subprocess.run(["git", "show", f"{ref}:{rel}"], cwd=REPO, capture_output=True, check=True).stdout
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"git show {ref[:12]}:{rel} failed: {e.stderr.decode(errors='replace').strip()[:300]}") from e


def load_run_items(manifest: dict[str, Any], allow_item_drift: bool = False,
                   items_ref: str | None = None) -> dict[str, dict[str, Any]]:
    """The run's items, by id. Read from the working tree (must still hash to the manifest), or with
    `items_ref` from git at that ref (e.g. the run's own SHA, after the item sets were regenerated);
    the bytes read from git must hash to the manifest too."""
    items: dict[str, dict[str, Any]] = {}
    for rel, digest in manifest["items"]["files"].items():
        if items_ref is not None:
            data = git_show(items_ref, rel)
            actual = hashlib.sha256(data).hexdigest()
            if actual != digest:
                raise SystemExit(f"{rel} at {items_ref[:12]} has sha256 {actual[:12]}, not the run's {digest[:12]}; "
                                 "the items the run used were not committed at that ref")
        else:
            path = Path(rel) if Path(rel).is_absolute() else REPO / rel
            actual = sha256_file(path)
            if actual != digest and not allow_item_drift:
                raise SystemExit(f"{rel} changed since the run (sha256 {actual[:12]} != {digest[:12]}); re-score against the "
                                 "items as they were with --items-at-run-sha, or with --allow-item-drift if the change is understood")
            data = path.read_bytes()
        for line in gzip.decompress(data).decode("utf-8").splitlines():
            if line.strip():
                it = json.loads(line)
                items[it["item_id"]] = it
    return items


def read_jsonl_gz(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def write_jsonl_gz(path: Path, recs: list[dict[str, Any]]) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
        for r in recs:
            gz.write((json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
    tmp.replace(path)


def score_raw(manifest: dict[str, Any], raw: list[dict[str, Any]], items: dict[str, dict[str, Any]],
              git: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    git = git or git_info()
    ctxs: dict[str, ItemContext] = {}
    out = []
    for r in raw:
        it = items[r["item_id"]]
        ctx = ctxs.setdefault(it["item_id"], ItemContext(it))
        resp = r.get("response")
        view = ResponseView.from_api(resp, max_tokens=(r.get("request") or {}).get("max_tokens"),
                                     error=None if resp is not None else (r.get("error") or "no response"))
        rec = score_response(it, view, ctx)
        rec.update({"run_id": manifest["run_id"], "model_requested": manifest["model_requested"],
                    "condition": manifest["condition"]["label"], "sample": r.get("sample", 0),
                    "from_cache": bool(r.get("from_cache")), "scorer_git_sha": git.get("sha"),
                    "scorer_git_dirty": git.get("dirty")})
        if r.get("forced_template"):  # a forced final answer (force.py): a stratum of its own, never the source's
            rec.update({"forced": True, "forced_template": r["forced_template"], "source_run_id": r["source_run_id"]})
            rec.update({k: r[k] for k in ("forced_select", "forced_sample", "source_sample", *BUDGET_FIELDS) if k in r})
            if r.get("natural_response") is not None:  # --select done: the source response's own answer
                rec.update(natural_scoring(it, r, ctx, rec))
        out.append(rec)
    return out


def natural_scoring(item: dict[str, Any], raw: dict[str, Any], ctx: ItemContext, forced: dict[str, Any]) -> dict[str, Any]:
    """The source response's own scoring, beside a forced answer to the same trace (force.py --select done), and
    whether the two agree: `same_as_natural` is the same answer key with both ok."""
    nat = score_response(item, ResponseView.from_api(raw["natural_response"], max_tokens=raw.get("natural_max_tokens")), ctx)
    return {"natural_category": nat["category"], "natural_correct": nat["correct"], "natural_answer_key": nat["answer_key"],
            "same_as_natural": nat["category"] == "ok" and forced["category"] == "ok" and nat["answer_key"] == forced["answer_key"]}


def score_run(run_dir: Path, allow_item_drift: bool = False, items_at_run_sha: bool = False,
              items_ref: str | None = None) -> dict[str, Any]:
    run_dir = Path(run_dir)
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if items_at_run_sha:
        items_ref = (manifest.get("git") or {}).get("sha")
        if not items_ref:
            raise SystemExit(f"{run_dir}: the manifest records no git SHA")
    items = load_run_items(manifest, allow_item_drift, items_ref)
    raw = read_jsonl_gz(run_dir / "raw.jsonl.gz")
    git = git_info()  # before anything is written
    scored = score_raw(manifest, raw, items, git)
    write_jsonl_gz(run_dir / SCORED, scored)
    summary = {"scorer_version": SCORER_VERSION, "git": git, "versions": versions(), "scored_at": utc_now(),
               "items_source": f"git {items_ref}" if items_ref else "working tree",
               "records": len(scored), "categories": dict(Counter(r["category"] for r in scored))}
    write_json(run_dir / "scoring.json", summary)
    (run_dir / "REPORT.md").write_text(build_report(manifest, scored), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m reasoning_heuristics.evals.score", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+", help="run directories (data/runs/<run_id>)")
    ap.add_argument("--allow-item-drift", action="store_true", help="score against the current item files even if they changed")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--items-at-run-sha", action="store_true",
                     help="read the item files from git at each run's recorded SHA (git show), checked against the manifest's sha256")
    src.add_argument("--items-ref", help="read the item files from git at this ref instead")
    a = ap.parse_args(argv)
    for run in a.runs:
        s = score_run(Path(run), a.allow_item_drift, a.items_at_run_sha, a.items_ref)
        print(f"{run}: {s['records']} records, {s['categories']} ({s['scorer_version']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
