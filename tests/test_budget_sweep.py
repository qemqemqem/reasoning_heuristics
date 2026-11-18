"""analysis/budget_sweep.py: the committed outputs match a fresh run (trivially, while no budget pass is committed), and
on passes made here with the HTTP layer mocked and a fake tokenizer, each item counts once: its natural answer when
its trace fit within the budget, else its forced answer, an unparsed one as not correct."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

from test_evals_force import SECRET, SOURCE, Transport, force, read_gz, source_run

REPO = Path(__file__).resolve().parent.parent


def load_script():
    spec = importlib.util.spec_from_file_location("budget_sweep", REPO / "analysis" / "budget_sweep.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_budget_sweep_matches_the_committed_files():
    r = subprocess.run([sys.executable, str(REPO / "analysis" / "budget_sweep.py"), "--check"], capture_output=True,
                       text=True, cwd=REPO)
    assert r.returncode == 0, r.stdout + r.stderr


def test_each_item_counts_once_natural_within_budget_else_forced(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", SECRET)
    t = Transport()
    src = source_run(tmp_path, t)
    for extra in (("--select", "all", "--truncate-at", "30"), ("--select", "all", "--truncate-frac", "0"),
                  ("--select", "cut"), ("--select", "all")):  # the last two have no budget: not read
        assert force(src, t, *extra) == 0
    bs = load_script()
    runs = tmp_path / "runs"
    assert [(s, label) for s, label, _ in bs.pass_dirs(runs)] == [("all", "f0"), ("all", "k30")]
    res = bs.compute(runs)
    assert set(res["passes"]) == {f"all-k30/{SOURCE}", f"all-f0/{SOURCE}"}
    [group] = res["groups"]
    assert (group["model"], group["source_run_id"], group["select"]) == ("openai/gpt-oss-20b", SOURCE, "all")
    rows = {(r["unit"], r["budget"]): r for r in group["rows"]}
    assert list(rows) == [("all units", "k30"), ("all units", "f0"), ("B4/C4 E1 entailment", "k30"), ("B4/C4 E1 entailment", "f0")]

    natural = {r["item_id"]: r for r in read_gz(src / "scored.jsonl.gz")}
    ids = [r["item_id"] for r in read_gz(src / "raw.jsonl.gz")]
    good = lambda r: r["category"] == "ok" and r["correct"] is True  # noqa: E731
    at_k = {r["item_id"]: r for r in read_gz(runs / "forced-2" / "all-k30" / SOURCE / "scored.jsonl.gz")}
    at_0 = {r["item_id"]: r for r in read_gz(runs / "forced-2" / "all-f0" / SOURCE / "scored.jsonl.gz")}
    selected = [ids[i] for i in (0, 1, 2, 4, 5)]  # item 3 stopped at the cap without a trace
    # k30: items 0-2 (47-token traces) were cut and forced, items 4-5 (27 tokens) kept their natural answers;
    # item 2's forced call went back to reasoning (Transport): not parsed, not correct
    want_k = sum(good(at_k[i]) for i in selected[:3]) + sum(good(natural[i]) for i in selected[3:])
    assert {k: rows[("all units", "k30")][k] for k in ("items", "within_budget", "forced", "answered", "parsed", "correct",
                                                       "no_room", "missing", "natural_correct")} == {
        "items": 5, "within_budget": 2, "forced": 3, "answered": 2, "parsed": 2, "correct": want_k, "no_room": 0, "missing": 0,
        "natural_correct": sum(good(natural[i]) for i in selected)}
    assert rows[("all units", "k30")]["accuracy"] == round(want_k / 5, 4)
    # f0: every trace emptied and forced, item 2's included
    want_0 = sum(good(at_0[i]) for i in selected)
    assert (rows[("all units", "f0")]["within_budget"], rows[("all units", "f0")]["forced"],
            rows[("all units", "f0")]["parsed"], rows[("all units", "f0")]["correct"]) == (0, 5, 5, want_0)
    assert rows[("B4/C4 E1 entailment", "k30")] == {**rows[("all units", "k30")], "unit": "B4/C4 E1 entailment"}
    md = bs.table(res)
    assert f"## openai/gpt-oss-20b: `{SOURCE}`, select all" in md and "| all units | k30 | 5 | 2 | 3 | 2 | 2 |" in md


def test_with_no_budget_pass_the_sweep_is_empty(tmp_path):
    bs = load_script()
    res = bs.compute(tmp_path)
    assert (res["passes"], res["groups"]) == ({}, []) and "No budget-forcing passes are committed yet." in bs.table(res)
