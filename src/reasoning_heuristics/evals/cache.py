"""Response cache keyed on (model, provider routing, parameters, prompt hash, sample index).

The key is a SHA-256 over the canonical JSON of the request body (which holds the model, the
provider routing, every sampling and reasoning parameter and the exact messages) plus the sample
index, so a repeat sample of the same item is a different key and is paid for once, and nothing
else is ever paid for twice. Only completed responses are cached (never errors).

Layout: `<dir>/<key[:2]>/<key>.json.gz`, one gzip JSON per response. The cache directory is a
local convenience (gitignored); the permanent copy of every response is the run's raw output,
and `import_runs` rebuilds a cache from those.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

from reasoning_heuristics.evals.client import usable
from reasoning_heuristics.hashing import canonical_json

CACHE_KEY_VERSION = 1


def cache_key(body: dict[str, Any], sample: int = 0) -> str:
    """Full-length SHA-256 of the request (without secrets: the key lives in headers, not the body)."""
    material = {"v": CACHE_KEY_VERSION, "body": body, "sample": sample}
    return hashlib.sha256(canonical_json(material).encode("utf-8")).hexdigest()


def prompt_hash(messages: list[dict[str, Any]]) -> str:
    return hashlib.sha256(canonical_json(messages).encode("utf-8")).hexdigest()[:16]


class ResponseCache:
    def __init__(self, root: Path | str):
        self.root = Path(root)

    def _path(self, key: str) -> Path:
        return self.root / key[:2] / f"{key}.json.gz"

    def get(self, key: str) -> dict[str, Any] | None:
        p = self._path(key)
        if not p.exists():
            return None
        with gzip.open(p, "rt", encoding="utf-8") as fh:
            return json.load(fh)

    def put(self, key: str, entry: dict[str, Any]) -> None:
        """Atomic write (temp file + rename), so a crash never leaves a half-written entry."""
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=p.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz:
                gz.write(json.dumps(entry, ensure_ascii=False).encode("utf-8"))
            os.replace(tmp, p)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise

    def __contains__(self, key: str) -> bool:
        return self._path(key).exists()

    def import_runs(self, raw_files: Iterable[Path]) -> int:
        """Warm the cache from runs' raw outputs (data/runs/*/raw.jsonl.gz). Returns entries added."""
        added = 0
        for f in raw_files:
            with gzip.open(f, "rt", encoding="utf-8") as fh:
                for line in fh:
                    rec = json.loads(line)
                    if not usable(rec.get("response")) or rec.get("cache_key") is None or rec["cache_key"] in self:
                        continue
                    self.put(rec["cache_key"], {"request": rec["request"], "response": rec["response"],
                                                "sample": rec.get("sample", 0), "source": str(f)})
                    added += 1
        return added
