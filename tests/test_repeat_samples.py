"""analysis/repeat_samples.py: the committed outputs match a fresh run; samples pair on item; the same wrong answer is
counted, and split by kind: constructions that match a listed heuristic, constructions that match none, give-ups."""

from __future__ import annotations

import gzip
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def load_script():
    spec = importlib.util.spec_from_file_location("repeat_samples", REPO / "analysis" / "repeat_samples.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rec(item: str, sample: int, outcome: str, key: str = "k", members: list[str] | None = None, parsed=None) -> dict:
    return {"item_id": item, "sample": sample, "vertical": "C", "eval_id": "E5", "domain": "coloring", "channel": "answer",
            "category": "parse_fail" if outcome == "fail" else "ok", "correct": outcome == "correct" if outcome != "fail" else None,
            "answer_key": None if outcome == "fail" else key, "members_matched": members or [],
            "parsed": {"v1": 1} if parsed is None else parsed, "answer_format": "a colouring"}


def test_the_repeat_samples_match_the_committed_files():
    r = subprocess.run([sys.executable, str(REPO / "analysis" / "repeat_samples.py"), "--check"], capture_output=True,
                       text=True, cwd=REPO)
    assert r.returncode == 0, r.stdout + r.stderr


def test_pairs_and_same_wrong_answers(tmp_path):
    rs = load_script()
    d = tmp_path / "2026-11-19-repeat-pc20-x"
    d.mkdir()
    recs = [rec("a", 0, "correct", "1"), rec("a", 1, "correct", "2"),             # both correct, different colourings
            rec("b", 0, "wrong", "w", ["FF-LIST"]), rec("b", 1, "wrong", "w"),    # the same wrong answer, matched
            rec("c", 0, "wrong", "x"), rec("c", 1, "wrong", "y"),                 # different wrong answers, unmatched
            rec("d", 0, "wrong", "z"), rec("d", 1, "correct", "ok"),              # correct in sample 1 only
            rec("e", 0, "fail"), rec("e", 1, "wrong", "q"),                       # not both ok
            rec("g", 0, "wrong", "IMP", ["ALWAYS-IMPOSSIBLE"], "IMPOSSIBLE"),     # the same give-up
            rec("g", 1, "wrong", "IMP", parsed="IMPOSSIBLE"),
            rec("f", 0, "correct", "1")]                                          # no second sample: not a pair
    with gzip.open(d / "scored.jsonl.gz", "wt") as fh:
        fh.writelines(json.dumps(r) + "\n" for r in recs)
    s = rs.compute(tmp_path)["runs"][d.name]["all"]
    assert (s["pairs"], s["both_ok"], s["correct_s0"], s["correct_s1"]) == (6, 5, 1, 2)
    assert (s["same_correctness"], s["same_answer"]) == (4, 2)
    assert (s["both_wrong"], s["same_wrong"]) == (3, 2)
    assert (s["built_matched"], s["built_matched_same"], s["built_unmatched"], s["built_unmatched_same"]) == (1, 1, 1, 0)
    assert (s["give_up"], s["give_up_same"], s["other"], s["other_same"]) == (1, 1, 0, 0)  # a give-up is not a construction
    assert s["mcnemar_p"] == 1.0  # one item correct in s1 only
    assert rs.compute(tmp_path)["runs"][d.name]["full_answer"] == s  # every record here is on a full-answer channel
