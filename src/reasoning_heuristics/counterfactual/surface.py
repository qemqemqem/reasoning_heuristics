"""Surface matching checks across the items of a counterfactual set.

Token counts use the stated proxy tokenizer (`reasoning_heuristics.tokens`, PROXY_NAME).
Every check returns a list of failure messages (empty = pass) so validators can report
all of them.
"""

from __future__ import annotations

import re

from reasoning_heuristics import tokens


def token_counts(prompts: dict[str, str]) -> dict[str, int]:
    return {k: tokens.count(p) for k, p in prompts.items()}


def equal_token_counts(prompts: dict[str, str], tolerance: int = 0) -> list[str]:
    counts = token_counts(prompts)
    lo, hi = min(counts.values()), max(counts.values())
    if hi - lo > tolerance:
        return [f"token counts differ by {hi - lo} > {tolerance} ({tokens.PROXY_NAME}): {counts}"]
    return []


def equal_token_multisets(prompts: dict[str, str]) -> list[str]:
    sets = {k: tokens.multiset(p) for k, p in prompts.items()}
    first_key = next(iter(sets))
    bad = [k for k, s in sets.items() if s != sets[first_key]]
    return [f"token multisets differ from {first_key}: {bad}"] if bad else []


def equal_lengths(prompts: dict[str, str], tolerance: int = 0) -> list[str]:
    lens = {k: len(p) for k, p in prompts.items()}
    if max(lens.values()) - min(lens.values()) > tolerance:
        return [f"character lengths differ by more than {tolerance}: {lens}"]
    return []


LABEL = re.compile(r"\b[vx]\d{2}\b")


def same_label_multiset(prompts: dict[str, str], pattern: re.Pattern = LABEL) -> list[str]:
    sets = {k: sorted(set(pattern.findall(p))) for k, p in prompts.items()}
    first_key = next(iter(sets))
    bad = [k for k, s in sets.items() if s != sets[first_key]]
    return [f"label sets differ from {first_key}: {bad}"] if bad else []


def token_delta_within(prompts_a: dict[str, str], prompts_b: dict[str, str], tolerance: int) -> list[str]:
    """Pairwise: |tokens(a_k) - tokens(b_k)| <= tolerance for every shared key."""
    bad = []
    for k in prompts_a:
        d = abs(tokens.count(prompts_a[k]) - tokens.count(prompts_b[k]))
        if d > tolerance:
            bad.append(f"{k}: token delta {d} > {tolerance}")
    return bad
