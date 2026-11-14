"""Stage 1 generators (SCOPE §5). Each module exposes:

    VERTICAL, EVAL_ID              e.g. "C", "E1"
    LEXICON_PARTITIONED            True when dev/test disjointness is by lexicon (B4/C4)
    cells(params) -> list[str]     the design cells (coverage is counted against these)
    generate(tier, seed, per_cell=None, **params) -> (items, stats)
    check_set(items) -> list[str]  the designed invariants of one counterfactual set
"""

from __future__ import annotations

import importlib
from types import ModuleType

REGISTRY: dict[tuple[str, str], str] = {
    ("A/H", "E1"): "reasoning_heuristics.generators.ah_e1",
    ("A/H", "E2"): "reasoning_heuristics.generators.ah_e2",
    ("A/H", "E5"): "reasoning_heuristics.generators.ah_e5",
    ("A/H", "E8"): "reasoning_heuristics.generators.ah_e8",
    ("C", "E1"): "reasoning_heuristics.generators.c_e1",
    ("C", "E2"): "reasoning_heuristics.generators.c_e2",
    ("C", "E3"): "reasoning_heuristics.generators.c_e3",
    ("C", "E5"): "reasoning_heuristics.generators.c_e5",
    ("B4/C4", "E1"): "reasoning_heuristics.generators.b4_e1",
    ("B4/C4", "E2"): "reasoning_heuristics.generators.b4_e2",
}

ALIASES = {"AH": "A/H", "A_H": "A/H", "A": "A/H", "B4": "B4/C4", "C4": "B4/C4", "B4C4": "B4/C4", "B4_C4": "B4/C4"}


def canonical_vertical(v: str) -> str:
    return ALIASES.get(v.upper(), v.upper())


def load(vertical: str, eval_id: str) -> ModuleType:
    key = (canonical_vertical(vertical), eval_id.upper())
    if key not in REGISTRY:
        raise KeyError(f"no generator for {key}; available: {sorted(REGISTRY)}")
    return importlib.import_module(REGISTRY[key])
