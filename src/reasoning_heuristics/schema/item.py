"""The one item schema shared by every vertical.

An item is one prompt plus everything needed to score it and to audit it:

- **Design fields** (from the example libraries): `eval_id`, `cell`, `set_id`,
  `pair_id`, `domain`, `framing`, `prompt`, `answer_format`, `ground_truth`,
  `predictions`, `trace_predictions`, `hypotheses`, `disconfirms`, `params`, `notes`.
- **Identity and lineage**: `content_hash` (logical content: instance + question,
  invariant to presentation), `presentation_hash` (the exact prompt), `base_hash`
  (content hash of the base instance the counterfactual set was built from; shared by
  every variant and used for split assignment), `source_hash` (content hash of the
  item this one was manipulated from; `None` for a base item), `seed`, `split`,
  `tier`, `generator`, `generator_version`.
- **Recomputation**: `instance` holds the structured logical form, so validators can
  recompute the ground truth and every prediction without parsing the prompt.

Likelihood-ratio sign convention (one for the whole repo)
---------------------------------------------------------
`disconfirms[outcome][theory]` is a log10 likelihood ratio **against** the theory:

    disconfirms[o][h] = log10 max_h' P(o | h') - log10 P(o | h)

so **positive = evidence against h**, 0 = h is among the best-fitting theories for that
outcome, and (in converted libraries that also listed support) negative = evidence for h.
The example libraries used three different conventions; `convert.py` maps them all to
this one.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import jsonschema

from reasoning_heuristics import GENERATOR_VERSION
from reasoning_heuristics.hashing import sha, to_jsonable

LR_CONVENTION = (
    "disconfirms[o][h] = log10 max_h' P(o|h') - log10 P(o|h); positive = evidence against h"
)

SCHEMA_PATH = Path(__file__).with_name("item.schema.json")


@dataclass
class PredictionRecord:
    """One member's prediction on one item, with what is needed to recompute it."""

    member: str  # registry name, e.g. "FF"
    family: str  # e.g. "C1"
    params: dict[str, Any]  # member parameters (order, tie key, budget, ...)
    answer: Any  # deterministic answer, or None for a purely distributional member
    trace_features: dict[str, Any] = field(default_factory=dict)
    distribution: dict[str, float] | None = None  # outcome label -> probability

    def to_json(self) -> dict[str, Any]:
        return to_jsonable(asdict(self))


@dataclass
class Item:
    item_id: str
    vertical: str
    eval_id: str
    set_id: str
    cell: str
    domain: str
    framing: str
    prompt: str
    answer_format: str
    ground_truth: Any
    predictions: dict[str, dict[str, Any]]
    instance: dict[str, Any] | None
    params: dict[str, Any] = field(default_factory=dict)
    pair_id: str | None = None
    trace_predictions: dict[str, Any] = field(default_factory=dict)
    hypotheses: dict[str, Any] = field(default_factory=dict)
    disconfirms: dict[str, dict[str, float]] = field(default_factory=dict)
    notes: str = ""
    likelihood_model: str = LR_CONVENTION
    content_hash: str = ""
    presentation_hash: str = ""
    base_hash: str = ""
    source_hash: str | None = None
    seed: int | None = None
    split: str = "dev"
    tier: str = "dev"
    generator: str = ""
    generator_version: str = GENERATOR_VERSION
    extra: dict[str, Any] = field(default_factory=dict)

    def finalise_hashes(self, content: Any) -> None:
        """Set content and presentation hashes. `content` is the logical content key."""
        self.content_hash = sha(content)
        self.presentation_hash = sha(self.prompt)
        if not self.base_hash:
            self.base_hash = self.content_hash

    def to_json(self) -> dict[str, Any]:
        return to_jsonable(asdict(self))

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Item":
        return cls(**data)


_SCHEMA_CACHE: dict[str, Any] = {}


def json_schema() -> dict[str, Any]:
    if "schema" not in _SCHEMA_CACHE:
        _SCHEMA_CACHE["schema"] = json.loads(SCHEMA_PATH.read_text())
    return _SCHEMA_CACHE["schema"]


def validate_against_schema(record: dict[str, Any]) -> None:
    """Raise jsonschema.ValidationError if the record does not match the item schema."""
    jsonschema.validate(record, json_schema())


def write_jsonl(items: list[Item], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for item in items:
            record = item.to_json()
            validate_against_schema(record)
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[Item]:
    with path.open(encoding="utf-8") as fh:
        return [Item.from_json(json.loads(line)) for line in fh if line.strip()]
