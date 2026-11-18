"""(Re-)score a run from its raw outputs on disk (DESIGN §5 rule 3: when the scorer changes,
everything is re-scored from raw outputs).

    python -m reasoning_heuristics.evals.score data/runs/<run_id> [data/runs/<other> ...]

Reads manifest.json (which item files, with their SHA-256) and raw.jsonl.gz; writes
scored.jsonl.gz, scoring.json (scorer version, git SHA, counts) and REPORT.md. The item files
must still hash to what the manifest recorded, unless --allow-item-drift is given.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from reasoning_heuristics.evals.manifest import REPO, git_info, sha256_file, utc_now, versions, write_json
from reasoning_heuristics.evals.report import build_report
from reasoning_heuristics.evals.scoring import SCORER_VERSION, ItemContext, ResponseView, score_response

SCORED = "scored.jsonl.gz"


def load_run_items(manifest: dict[str, Any], allow_item_drift: bool = False) -> dict[str, dict[str, Any]]:
    items: dict[str, dict[str, Any]] = {}
    for rel, digest in manifest["items"]["files"].items():
        path = Path(rel) if Path(rel).is_absolute() else REPO / rel
        actual = sha256_file(path)
        if actual != digest and not allow_item_drift:
            raise SystemExit(f"{rel} changed since the run (sha256 {actual[:12]} != {digest[:12]}); "
                             "re-score with --allow-item-drift only if the change is understood")
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            for line in fh:
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


def score_raw(manifest: dict[str, Any], raw: list[dict[str, Any]], items: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    git = git_info()
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
        out.append(rec)
    return out


def score_run(run_dir: Path, allow_item_drift: bool = False) -> dict[str, Any]:
    run_dir = Path(run_dir)
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    items = load_run_items(manifest, allow_item_drift)
    raw = read_jsonl_gz(run_dir / "raw.jsonl.gz")
    scored = score_raw(manifest, raw, items)
    write_jsonl_gz(run_dir / SCORED, scored)
    summary = {"scorer_version": SCORER_VERSION, "git": git_info(), "versions": versions(), "scored_at": utc_now(),
               "records": len(scored), "categories": dict(Counter(r["category"] for r in scored))}
    write_json(run_dir / "scoring.json", summary)
    (run_dir / "REPORT.md").write_text(build_report(manifest, scored), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m reasoning_heuristics.evals.score", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+", help="run directories (data/runs/<run_id>)")
    ap.add_argument("--allow-item-drift", action="store_true")
    a = ap.parse_args(argv)
    for run in a.runs:
        s = score_run(Path(run), a.allow_item_drift)
        print(f"{run}: {s['records']} records, {s['categories']} ({s['scorer_version']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
