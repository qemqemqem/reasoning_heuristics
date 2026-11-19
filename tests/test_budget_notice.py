"""analysis/budget_notice.py: the committed outputs match a fresh run; records pair on (item, sample); a truncated
response counts by its forced answer at the cap, a finished one by its own; the exact McNemar test is right."""

from __future__ import annotations

import gzip
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def load_script():
    spec = importlib.util.spec_from_file_location("budget_notice", REPO / "analysis" / "budget_notice.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write(p: Path, recs: list[dict]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(p, "wt", encoding="utf-8") as fh:
        fh.writelines(json.dumps(r) + "\n" for r in recs)


def rec(item: str, outcome: str, domain: str = "sat", tokens: int = 100) -> dict:
    """outcome: correct, wrong, or trunc (stopped at the cap, no answer)."""
    return {"item_id": item, "sample": 0, "vertical": "C", "domain": domain, "truncated": outcome == "trunc",
            "category": "truncated" if outcome == "trunc" else "ok", "correct": outcome == "correct" if outcome != "trunc" else None,
            "completion_tokens": tokens}


def forced(item: str, ok: bool, correct: bool) -> dict:
    return {"item_id": item, "source_sample": 0, "forced_sample": 0, "category": "ok" if ok else "parse_fail",
            "correct": correct if ok else None}


def test_the_budget_notice_matches_the_committed_files():
    r = subprocess.run([sys.executable, str(REPO / "analysis" / "budget_notice.py"), "--check"], capture_output=True,
                       text=True, cwd=REPO)
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.parametrize("b,c,p", [(0, 0, 1.0), (0, 5, 0.0625), (5, 0, 0.0625), (1, 1, 1.0), (2, 8, 0.109375)])
def test_mcnemar_exact(b, c, p):
    assert load_script().mcnemar_p(b, c) == pytest.approx(p)


def test_pairing_and_forced_composition(tmp_path):
    bn = load_script()
    runs = tmp_path / "runs"
    write(runs / "notice" / "scored.jsonl.gz", [rec("a", "trunc"), rec("b", "correct"), rec("c", "trunc"), rec("d", "wrong", "coloring"),
                                                rec("only-notice", "correct")])
    write(runs / "base" / "scored.jsonl.gz", [rec("a", "correct"), rec("b", "trunc"), rec("c", "trunc"), rec("d", "correct", "coloring")])
    res = bn.compare(runs, "notice", "base")
    assert res["paired"] == 4 and res["notice_records"] == 5 and not res["forced_passes"]
    allu = res["rows"][0]
    assert allu["unit"] == "all units" and allu["n"] == 4
    assert (allu["notice"]["truncated"], allu["notice"]["correct"], allu["notice"]["wrong"]) == (2, 1, 1)
    assert (allu["base"]["truncated"], allu["base"]["correct"], allu["base"]["wrong"]) == (2, 2, 0)
    assert allu["truncation_flips"] == [1, 1] and allu["correct_flips"] == [1, 2]
    assert allu["notice"]["correct_forced"] is None
    assert [r["unit"] for r in res["rows"]] == ["all units", "C coloring", "C sat"]

    # with forced passes for both: a truncated record counts by its forced answer, a finished one by its own
    write(runs / "forced-2" / "cut" / "notice" / "scored.jsonl.gz", [forced("a", True, True), forced("c", False, False)])
    write(runs / "forced-2" / "cut" / "base" / "scored.jsonl.gz", [forced("b", True, False), forced("c", True, True)])
    res = bn.compare(runs, "notice", "base")
    allu = res["rows"][0]
    assert res["forced_passes"]
    assert allu["notice"]["correct_forced"] == 2  # a (forced, correct), b (natural, correct); c forced unparsed; d wrong
    assert allu["base"]["correct_forced"] == 3  # a and d (natural, correct), c (forced, correct); b forced wrong
