import json
from pathlib import Path

import jsonschema
import pytest

from reasoning_heuristics.hashing import sha
from reasoning_heuristics.schema.convert import LIBRARIES, convert_library
from reasoning_heuristics.schema.item import Item, read_jsonl, validate_against_schema, write_jsonl

ROOT = Path(__file__).resolve().parents[1]


def _item(**kw):
    base = dict(
        item_id="t-1", vertical="C", eval_id="E1", set_id="s", cell="c1", domain="colouring",
        framing="textbook", prompt="Colour it.", answer_format="x", ground_truth={"chi": 3},
        predictions={"FF": {"member": "FF", "family": "C1", "params": {}, "answer": {"v1": 1}}},
        instance={"kind": "graph"},
    )
    base.update(kw)
    it = Item(**base)
    it.finalise_hashes({"graph": 1})
    return it


def test_roundtrip(tmp_path):
    it = _item()
    path = tmp_path / "x.jsonl"
    write_jsonl([it], path)
    back = read_jsonl(path)[0]
    assert back.to_json() == it.to_json()
    assert it.base_hash == it.content_hash == sha({"graph": 1})


def test_schema_rejects_unknown_field_and_bad_hash():
    rec = _item().to_json()
    rec["bogus"] = 1
    with pytest.raises(jsonschema.ValidationError):
        validate_against_schema(rec)
    rec = _item().to_json()
    rec["content_hash"] = "xyz"
    with pytest.raises(jsonschema.ValidationError):
        validate_against_schema(rec)


@pytest.mark.parametrize("lib", list(LIBRARIES))
def test_every_library_converts(lib):
    items, report = convert_library(ROOT / "data" / "examples" / f"{lib}.jsonl")
    raw = [json.loads(l) for l in (ROOT / "data" / "examples" / f"{lib}.jsonl").read_text().splitlines() if l.strip()]
    assert len(items) == len(raw) == report["items"]
    for it in items:
        validate_against_schema(it.to_json())


def test_sign_conventions_unified():
    # C: likelihood_ratios are <= 0 relative to the best; converted values must be >= 0.
    items, _ = convert_library(ROOT / "data" / "examples" / "C_constructive.jsonl")
    vals = [v for it in items for row in it.disconfirms.values() for v in row.values()]
    assert vals and min(vals) >= 0
    # A/H: 'disconfirms' entries were negative = against; after conversion they are positive.
    items, _ = convert_library(ROOT / "data" / "examples" / "A_H_baselines.jsonl")
    first = items[0]
    assert first.disconfirms["x: SAT, x′: SAT"]["A1 ALWAYS-UNSAT"] == pytest.approx(2.56)
    # ... and 'supports' (positive = for) become negative.
    assert first.disconfirms["x: SAT + POLARITY witness"]["C0 POLARITY"] == pytest.approx(-2.03)
    # B4: already positive = against.
    items, _ = convert_library(ROOT / "data" / "examples" / "B4_C4_restrict_online.jsonl")
    assert items[0].disconfirms["one sample = YES"]["EXACT"] == pytest.approx(2.2)
