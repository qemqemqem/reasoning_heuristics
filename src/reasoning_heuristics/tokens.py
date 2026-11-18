"""Tokenizer proxy for surface matching.

The real panel tokenizers (o200k for gpt-oss, Qwen3, DeepSeek-V3, Llama-3) are not
dependencies of this package. Surface matching uses a stated proxy instead:

    PROXY = "regex-digit-split-v1":
      - every digit is its own token (Qwen-style; the most fragmenting panel tokenizer),
      - a run of letters is one token,
      - every other non-space character is one token,
      - whitespace is free.

Equal proxy counts do not guarantee equal counts under every panel tokenizer. Of the
two edits the generators use most, permuting lines preserves the multiset of proxy
tokens, but swapping names drawn from a fixed-width pool preserves only their number:
the digits change (v37 -> v12), so a real tokenizer counts the copy the same only if
every label in the pool has the same token count in it (the check C §1.2 asks for).
Per-tokenizer checks against the real vocabularies belong to the runner, before a pilot.
"""

from __future__ import annotations

import re

PROXY_NAME = "regex-digit-split-v1"
_TOKEN = re.compile(r"\d|[^\W\d_]+|[^\w\s]|_")


def tokens(text: str) -> list[str]:
    return _TOKEN.findall(text)


def count(text: str) -> int:
    return len(tokens(text))


def multiset(text: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for t in tokens(text):
        out[t] = out.get(t, 0) + 1
    return out
