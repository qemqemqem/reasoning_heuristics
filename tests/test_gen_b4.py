"""B4/C4 generators reproduce the library items and pass their validators."""

import pytest

from libparse import library
from reasoning_heuristics.generators import b4_common as B
from reasoning_heuristics.generators import b4_e1
from reasoning_heuristics.generators.common import predict_all
from reasoning_heuristics.validate.checks import check_leakage, run_checks

LIB_FRAME = B.Frame("abstract", ("box", "jar", "cup"), ("red", "heavy", "blue", "cold", "green"))
SAME_NAMES = ["FIRST", "MATCH-L", "MATCH-A", "ETR-default", "ETR-1p", "MM-S1", "MM-elim", "BICOND", "CW-MIN",
              "CW-COMP", "ONL(1)", "ONL(2)", "ONL(4)", "PRIMACY", "RECENCY", "AFFIRM", "ALWAYS-YES", "NONE", "UP-1",
              "C1-GREEDY", "EXACT"]


def _lib_e1():
    return [r for r in library("B4_C4_restrict_online") if r["eval_id"] == "E1" and r["framing"] == "abstract"]


@pytest.mark.parametrize("rec", _lib_e1(), ids=lambda r: r["cell"])
def test_e1_reproduces_library(rec):
    p = rec["params"]
    task = b4_e1.build_task(LIB_FRAME, p["T"], p["P"], p["O"], p["F"])
    assert B.render_prompt(task) == rec["prompt"]
    preds = predict_all(task, B.members(p["F"], False))
    for name in SAME_NAMES:
        lib = rec["predictions"].get(name)
        if lib in (None, "n/a"):
            continue
        ours = preds[name]["answer"]
        assert ours == lib, (rec["cell"], name, ours, lib)


def test_e1_smoke_and_dev_validate():
    items, stats = b4_e1.generate("smoke", 3)
    assert stats["accepted"] == 1 and len(items) == len(b4_e1.cells({}))
    report = run_checks(items, b4_e1.check_set)
    assert report["failures"] == []
    dev, _ = b4_e1.generate("dev", 3, per_cell=2)
    test, _ = b4_e1.generate("test", 3, per_cell=1)
    assert check_leakage(items + dev + test, lexicon_partitioned=True) == []


from reasoning_heuristics.generators import b4_e2  # noqa: E402

LIB_FRAME_E2 = B.Frame("abstract", ("box", "jar"), ("red", "cold"))
E2_NAMES = SAME_NAMES + ["MM-G", "ETR-default-R2", "ETR-1p-R2", "BICOND-PRAG", "SAMPLE-3"]


def _lib_e2():
    return [r for r in library("B4_C4_restrict_online") if r["eval_id"] == "E2" and r["framing"] == "abstract"]


@pytest.mark.parametrize("rec", _lib_e2(), ids=lambda r: r["cell"])
def test_e2_reproduces_library(rec):
    p = rec["params"]
    task = b4_e2.build_task(LIB_FRAME_E2, p["form"], p["inference"], p["O"])
    note = b4_e2.INSTRUCTION if p["instruction"] else b4_e2.NEUTRAL["library"]
    assert B.render_prompt(task, note=note) == rec["prompt"]
    preds = predict_all(task, b4_e2.specs(p["instruction"]))
    for name in E2_NAMES:
        lib = rec["predictions"].get(name)
        if lib in (None, "n/a"):
            continue
        ours = preds[name]["answer"]
        if name == "SAMPLE-3":
            assert preds[name]["distribution"]["YES"] == pytest.approx(lib, abs=0.01)
            continue
        assert ours == lib or ({"X": "NO"}.get(ours) == lib), (rec["cell"], name, ours, lib)


def test_e2_smoke_validates():
    items, stats = b4_e2.generate("smoke", 5)
    assert len(items) == len(b4_e2.cells({})) == 48
    assert run_checks(items, b4_e2.check_set)["failures"] == []
