"""Run manifests (DESIGN §5 rules 3, 8, 10, 11): what was asked, of whom, with which code and items."""

from __future__ import annotations

import gzip
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any, Iterable

from reasoning_heuristics import GENERATOR_VERSION
from reasoning_heuristics import tokens as token_proxy
from reasoning_heuristics.evals.scoring import SCORER_VERSION, UnsupportedItem, answer_format

REPO = Path(__file__).resolve().parents[3]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_info(repo: Path = REPO) -> dict[str, Any]:
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()

    try:
        sha = git("rev-parse", "HEAD")
        # the code, not data: a run or scoring pass writes tracked files under data/runs/ itself
        dirty = bool(git("status", "--porcelain", "--untracked-files=no", "--", "src", "pyproject.toml"))
        branch = git("rev-parse", "--abbrev-ref", "HEAD")
    except (OSError, subprocess.CalledProcessError) as e:
        return {"sha": None, "error": str(e)}
    return {"sha": sha, "dirty": dirty, "branch": branch}


def versions() -> dict[str, Any]:
    out: dict[str, Any] = {"python": sys.version.split()[0], "platform": platform.platform(),
                           "reasoning_heuristics": GENERATOR_VERSION, "scorer": SCORER_VERSION,
                           "tokenizer_proxy": token_proxy.PROXY_NAME}
    for dist in ("python-sat", "pyetr", "numpy", "networkx", "jsonschema"):
        try:
            out[dist] = metadata.version(dist)
        except metadata.PackageNotFoundError:
            out[dist] = None
    return out


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def item_files(paths: Iterable[str | Path]) -> list[Path]:
    """Expand directories to their committed `*.jsonl.gz` item sets."""
    out: list[Path] = []
    for p in (Path(x).resolve() for x in paths):
        if p.is_dir():
            out += sorted(p.glob("*.jsonl.gz"))
        elif p.exists():
            out.append(p)
        else:
            raise FileNotFoundError(p)
    if not out:
        raise FileNotFoundError(f"no item files under {list(map(str, paths))}")
    return out


def load_items(files: list[Path], exclude_evals: Iterable[str] = (), include_evals: Iterable[str] = ()) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Items to run, in file order, and what was left out and why."""
    exclude = {e.upper() for e in exclude_evals}
    include = {e.upper() for e in include_evals}
    items, skipped = [], {"excluded_eval": 0, "unsupported": 0, "not_included": 0}
    for f in files:
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                it = json.loads(line)
                tag = it["eval_id"].upper()
                full = f"{it['vertical'].replace('/', '')}-{tag}".upper()
                if tag in exclude or full in exclude:
                    skipped["excluded_eval"] += 1
                    continue
                if include and tag not in include and full not in include:
                    skipped["not_included"] += 1
                    continue
                try:
                    answer_format(it)
                except UnsupportedItem:
                    skipped["unsupported"] += 1
                    continue
                items.append(it)
    ids = [it["item_id"] for it in items]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate item ids across the item files")
    return items, skipped


def file_hashes(files: list[Path]) -> dict[str, str]:
    return {str(f.relative_to(REPO) if f.is_absolute() and REPO in f.parents else f): sha256_file(f) for f in files}


def write_json(path: Path, data: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8")
    tmp.replace(path)
