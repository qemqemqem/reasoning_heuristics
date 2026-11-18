"""Canonical JSON and content hashes.

Every hash in the item store is a SHA-256 over canonical JSON (sorted keys, no
whitespace, tuples as lists). Hashes are shortened to 16 hex characters for
readability; collisions at that length are checked by the validators.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

HASH_LENGTH = 16


def to_jsonable(value: Any) -> Any:
    """Recursively convert tuples, sets and frozensets to lists, and keys to strings."""
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return sorted((to_jsonable(v) for v in value), key=canonical_json)
    if hasattr(value, "item") and callable(value.item):  # numpy scalars
        return value.item()
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(to_jsonable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(value: Any) -> str:
    """Short SHA-256 of a value's canonical JSON (strings are hashed as-is)."""
    text = value if isinstance(value, str) else canonical_json(value)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:HASH_LENGTH]
