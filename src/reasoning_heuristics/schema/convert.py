"""Convert the six hand-built example libraries (data/examples/*.jsonl) into the item schema.

The libraries were written by different design agents and differ in their extra
fields and, importantly, in their likelihood-ratio sign conventions:

| Library | Source field(s) | Source convention | Mapping |
|---|---|---|---|
| A_H_baselines | `disconfirms`, `supports` | log10 LR, negative = against (disconfirms), positive = for (supports) | negate both, merge |
| B1_G_relax_decompose | `disconfirms` | log10 LR, positive = against | as is |
| B4_C4_restrict_online | `disconfirms` (numeric entries) | log10 LR, positive = against | as is; list-valued contrast entries are unmapped |
| C_constructive | `likelihood_ratios` | log10 LR relative to the best theory (<= 0) | negate |
| D_F_search | `outcome_likelihoods` (P(o given h)) | probabilities | log10 max_h' P - log10 P |
| E_message_passing | `disconfirms[o][h]["log10_LR"]` | positive = against | as is |

The target convention is `schema.item.LR_CONVENTION` (positive = evidence against).
Library items carry no structured `instance` (they were rendered by scratch scripts),
so they cannot be recomputed; their content hash is taken over the prompt and ground
truth, and the report says so.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from reasoning_heuristics.hashing import sha
from reasoning_heuristics.schema.item import Item, validate_against_schema

LIBRARIES = {
    "A_H_baselines": "A/H",
    "B1_G_relax_decompose": "B1/G",
    "B4_C4_restrict_online": "B4/C4",
    "C_constructive": "C",
    "D_F_search": "D/F",
    "E_message_passing": "E",
}

DIRECT_FIELDS = {
    "eval_id", "cell", "pair_id", "domain", "framing", "prompt", "answer_format",
    "ground_truth", "trace_predictions", "params", "notes", "hypotheses",
}
CONSUMED_FIELDS = DIRECT_FIELDS | {
    "item_id", "set_id", "predictions", "disconfirms", "supports", "likelihood_ratios",
    "outcome_likelihoods",
}


def _numeric_table(table: Any, sign: float, unmapped: dict[str, Any], field: str) -> dict[str, dict[str, float]]:
    """Map {outcome: {theory: number}} with a sign; non-numeric entries go to `unmapped`."""
    out: dict[str, dict[str, float]] = {}
    if not isinstance(table, dict):
        unmapped[field] = table
        return out
    for outcome, row in table.items():
        if isinstance(row, dict) and all(isinstance(v, (int, float)) for v in row.values()):
            out[outcome] = {h: round(sign * float(v), 4) + 0.0 for h, v in row.items()}
        elif isinstance(row, dict) and all(isinstance(v, dict) and "log10_LR" in v for v in row.values()):
            out[outcome] = {h: round(sign * float(v["log10_LR"]), 4) + 0.0 for h, v in row.items()}
        else:
            unmapped.setdefault(field, {})[outcome] = row
    return out


def _from_outcome_likelihoods(table: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    outcomes = sorted({o for row in table.values() for o in row})
    out: dict[str, dict[str, float]] = {}
    for o in outcomes:
        best = max(row.get(o, 0.0) for row in table.values())
        out[o] = {}
        for h, row in table.items():
            p = row.get(o, 0.0)
            out[o][h] = round(math.log10(best) - math.log10(p), 4) if p > 0 else math.inf
        out[o] = {h: v for h, v in out[o].items() if math.isfinite(v)}
    return out


def _disconfirms(lib: str, rec: dict[str, Any], unmapped: dict[str, Any]) -> dict[str, dict[str, float]]:
    if lib == "A_H_baselines":
        table = _numeric_table(rec.get("disconfirms", {}), -1.0, unmapped, "disconfirms")
        for o, row in _numeric_table(rec.get("supports", {}), -1.0, unmapped, "supports").items():
            table.setdefault(o, {}).update(row)
        return table
    if lib == "C_constructive":
        if "disconfirms" in rec:
            unmapped["disconfirms"] = rec["disconfirms"]
        if "supports" in rec:
            unmapped["supports"] = rec["supports"]
        return _numeric_table(rec.get("likelihood_ratios", {}), -1.0, unmapped, "likelihood_ratios")
    if lib == "D_F_search":
        if "disconfirms" in rec:
            unmapped["disconfirms"] = rec["disconfirms"]
        return _from_outcome_likelihoods(rec.get("outcome_likelihoods", {}))
    return _numeric_table(rec.get("disconfirms", {}), 1.0, unmapped, "disconfirms")


def convert_record(lib: str, rec: dict[str, Any], index: int) -> tuple[Item, dict[str, Any]]:
    unmapped: dict[str, Any] = {k: v for k, v in rec.items() if k not in CONSUMED_FIELDS}
    disconfirms = _disconfirms(lib, rec, unmapped)
    predictions = {
        name: {"member": name, "family": "", "params": {}, "answer": value}
        for name, value in (rec.get("predictions") or {}).items()
    }
    hypotheses = rec.get("hypotheses", {})
    if not isinstance(hypotheses, dict):
        unmapped["hypotheses"] = hypotheses
        hypotheses = {}
    notes = rec.get("notes", "")
    if not isinstance(notes, str):
        unmapped["notes"] = notes
        notes = ""
    set_id = rec.get("set_id") or rec.get("pair_id") or f"{lib}-{index}"
    item_id = rec.get("item_id") or f"{LIBRARIES[lib]}:{rec['eval_id']}:{rec.get('pair_id')}:{rec['cell']}"
    item = Item(
        item_id=f"library:{lib}:{index:03d}:{item_id}",
        vertical=LIBRARIES[lib],
        eval_id=rec["eval_id"],
        set_id=str(set_id),
        pair_id=rec.get("pair_id"),
        cell=str(rec["cell"]),
        domain=str(rec["domain"]),
        framing=str(rec.get("framing", "")),
        prompt=rec["prompt"],
        answer_format=str(rec.get("answer_format", "")),
        ground_truth=rec.get("ground_truth"),
        predictions=predictions,
        instance=None,
        params=rec.get("params") if isinstance(rec.get("params"), dict) else {"value": rec.get("params")},
        trace_predictions=rec.get("trace_predictions") or {},
        hypotheses=hypotheses,
        disconfirms=disconfirms,
        notes=notes,
        seed=None,
        split="library",
        tier="library",
        generator=f"library:{lib}",
        extra={"unmapped": unmapped} if unmapped else {},
    )
    item.finalise_hashes({"prompt": rec["prompt"], "ground_truth": rec.get("ground_truth")})
    item.base_hash = sha({"library": lib, "set": str(set_id)})
    return item, unmapped


def convert_library(path: Path) -> tuple[list[Item], dict[str, Any]]:
    lib = path.stem
    if lib not in LIBRARIES:
        raise ValueError(f"unknown library {lib}")
    items: list[Item] = []
    unmapped_counts: Counter[str] = Counter()
    with path.open(encoding="utf-8") as fh:
        records = [json.loads(line) for line in fh if line.strip()]
    for i, rec in enumerate(records):
        item, unmapped = convert_record(lib, rec, i)
        validate_against_schema(item.to_json())
        items.append(item)
        unmapped_counts.update(unmapped.keys())
    ids = Counter(it.item_id for it in items)
    duplicates = [k for k, v in ids.items() if v > 1]
    if duplicates:
        raise ValueError(f"{lib}: duplicate item ids after conversion: {duplicates[:3]}")
    report = {
        "library": lib,
        "items": len(items),
        "items_with_disconfirms": sum(1 for it in items if it.disconfirms),
        "unmapped_fields": dict(sorted(unmapped_counts.items())),
        "not_recomputable": "no structured instance in the library records; content_hash is over prompt + ground truth",
    }
    return items, report


def convert_all(examples_dir: Path, out_dir: Path) -> list[dict[str, Any]]:
    from reasoning_heuristics.schema.item import write_jsonl

    reports = []
    for lib in LIBRARIES:
        items, report = convert_library(examples_dir / f"{lib}.jsonl")
        write_jsonl(items, out_dir / f"{lib}.jsonl")
        reports.append(report)
    lines = [
        "# Example-library conversion report",
        "",
        "Generated by `python -m reasoning_heuristics.schema.convert`. Every record of the six",
        "libraries in `data/examples/` converts into the item schema and passes the JSON Schema.",
        "Fields listed below did not map onto a schema field; they are kept verbatim under",
        "`extra.unmapped` on each converted item.",
        "",
        "| Library | Items | With LR table | Unmapped fields (items) |",
        "|---|---|---|---|",
    ]
    for r in reports:
        unm = ", ".join(f"`{k}` ({v})" for k, v in r["unmapped_fields"].items()) or "none"
        lines.append(f"| {r['library']} | {r['items']} | {r['items_with_disconfirms']} | {unm} |")
    lines += [
        "",
        "Notes:",
        "",
        "- Sign conventions were unified to positive log10 LR = evidence against (see `convert.py`).",
        "- C's `supports`/`disconfirms` are lists of theory names per outcome; the numeric",
        "  `likelihood_ratios` table carries the same information and is the one mapped.",
        "- D/F's `disconfirms` summarises `outcome_likelihoods`; the full table is mapped instead.",
        "- B4/C4's list-valued `disconfirms` entries (observed contrast classes) are kept unmapped.",
        "- No library item carries a structured instance, so none can be recomputed by the validators;",
        "  the generators reproduce the designs instead (see docs/GENERATORS.md).",
        "",
    ]
    (out_dir / "CONVERSION_REPORT.md").write_text("\n".join(lines))
    return reports


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    for r in convert_all(root / "data" / "examples", root / "data" / "library"):
        print(r["library"], r["items"], r["unmapped_fields"])
