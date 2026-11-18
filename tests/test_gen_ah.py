"""A/H generators: library reproduction, design invariants, validation, leakage, E8 materialisation."""

import re

import pytest

from libparse import find
from reasoning_heuristics.generators import ah_common as A
from reasoning_heuristics.generators import ah_e1, ah_e2, ah_e5, ah_e8
from reasoning_heuristics.heuristics.tasks import EntailmentTask, SatTask
from reasoning_heuristics.problems.coloring.graph import Graph
from reasoning_heuristics.problems.coloring.render import render_rooms
from reasoning_heuristics.problems.entailment import formula as F
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.sat.render import render_menu, render_textbook
from reasoning_heuristics.validate.checks import check_leakage, run_checks
from reasoning_heuristics.validate.truth import truth


def cnf_from_ah_prompt(prompt: str) -> S.CNF:
    names = re.search(r"Variables: (.*)\.", prompt).group(1).split(", ")
    clauses = []
    for body in re.findall(r"C\d+★?: \((.*)\)", prompt):
        clauses.append(tuple((-1 if t.startswith("¬") else 1) * (names.index(t.lstrip("¬")) + 1) for t in body.split(" ∨ ")))
    return S.CNF(tuple(names), tuple(clauses))


def _lit(text: str):
    m = re.fullmatch(r"the (\w+) is (not )?(\w+)", text.strip())
    return F.lit(f"{m.group(1)}:{m.group(3)}", m.group(2) is None)


def _conj(text: str):
    return F.conj(*[_lit(t) for t in text.split(" and ")])


def ent_from_machine_prompt(prompt: str) -> EntailmentTask:
    prem = []
    for line in prompt.splitlines():
        if not line.startswith("- "):
            continue
        s = line[2:].rstrip(".")
        s = s[0].lower() + s[1:]
        if s.startswith("either "):
            prem.append(F.disj(*[_conj(d) for d in s[len("either "):].split(", or ")]))
        else:
            prem.append(_conj(s))
    probe = re.search(r"follow from these facts that (.*)\?", prompt).group(1)
    return EntailmentTask(tuple(prem), _conj(probe), "YN")


# --- E1 -----------------------------------------------------------------------------------------


def test_e1_sat_library_pair_is_an_admissible_swap():
    x = cnf_from_ah_prompt(find("A_H_baselines", item_id="E1-SAT-x")["prompt"])
    x2 = cnf_from_ah_prompt(find("A_H_baselines", item_id="E1-SAT-x'")["prompt"])
    assert render_textbook(x) == find("A_H_baselines", item_id="E1-SAT-x")["prompt"]
    assert any(ah_e1.apply_swap(x, *s) == x2 for s in ah_e1.sat_swaps(x))
    assert truth(SatTask(x))["satisfiable"] and not truth(SatTask(x2))["satisfiable"]
    assert render_menu(x) == find("A_H_baselines", item_id="E1-SAT-x-menu")["prompt"]


def test_e1_ent_library_pair_is_an_admissible_edit():
    p = find("A_H_baselines", item_id="E1-ENT-P")
    p2 = find("A_H_baselines", item_id="E1-ENT-P'")
    t1, t2 = ent_from_machine_prompt(p["prompt"]), ent_from_machine_prompt(p2["prompt"])
    assert A.render_machine_facts(t1) == p["prompt"] and A.render_machine_facts(t2) == p2["prompt"]
    edits = ah_e1.ent_edits(t1.premises)
    assert any(ah_e1.apply_ent_edit(t1.premises, i, li, j, lj) == t2.premises for _, i, li, j, lj in edits)
    assert truth(t1)["follows"] and not truth(t2)["follows"]
    assert F.rho(list(t2.premises), t2.probe) == pytest.approx(p2["params"]["rho"])


def test_e1_smoke_validates_and_cues_are_blind():
    items, stats = ah_e1.generate("smoke", 5)
    assert len(items) == len(ah_e1.cells({})) and stats["accepted"] == len(items) // 2
    report = run_checks(items, ah_e1.check_set)
    assert report["failures"] == []
    for kind in ("critical", "null", "B1"):
        pair = [it for it in items if it.params["pair_kind"] == kind and it.domain == "SAT"]
        assert pair[0].predictions["A2 DENSITY-U"]["answer"] == pair[1].predictions["A2 DENSITY-U"]["answer"]


def test_e1_leakage_dev_vs_test():
    dev, _ = ah_e1.generate("dev", 2, per_cell=1, domains=["SAT", "COL"])
    test, _ = ah_e1.generate("test", 2, per_cell=1, domains=["SAT", "COL"])
    assert check_leakage(dev + test) == []
    # A test item that copies a dev base is caught.
    dup = test[0].__class__.from_json({**dev[0].to_json(), "split": "test", "tier": "test",
                                       "item_id": "dup", "seed": 1_500_000})
    assert check_leakage(dev + [dup])


# --- E2 -----------------------------------------------------------------------------------------


def test_e2_library_padding_reduces_to_core():
    base = cnf_from_ah_prompt(find("A_H_baselines", item_id="E2-SAT-base")["prompt"])
    for level in ("K", "J"):
        padded = cnf_from_ah_prompt(find("A_H_baselines", item_id=f"E2-SAT-{level}")["prompt"])
        assert ah_e2.pure_literal_elimination(list(padded.clauses)) == list(base.clauses)
        assert truth(SatTask(padded)) == truth(SatTask(base))


def test_e2_smoke_validates():
    items, _ = ah_e2.generate("smoke", 4)
    assert sorted({it.cell for it in items}) == sorted(ah_e2.cells({}))
    assert run_checks(items, ah_e2.check_set)["failures"] == []
    k = next(it for it in items if it.cell.startswith("SAT/K"))
    j = next(it for it in items if it.cell.startswith("SAT/J") and it.set_id == k.set_id)
    assert k.params["alpha_U"] > 4.26 > j.params["alpha_U"]
    assert k.predictions["A2 DENSITY-U"]["answer"] == "UNSAT" and j.predictions["A2 DENSITY-U"]["answer"] == "SAT"


# --- E5 -----------------------------------------------------------------------------------------


def test_e5_col_library_textbook_prompt():
    rec = find("A_H_baselines", item_id="E5-COL-T")
    names = re.search(r"\((.*)\) are being", rec["prompt"]).group(1).split(", ")
    pairs = re.search(r"enemies: (.*)\.", rec["prompt"]).group(1).split(", ")
    g = Graph(tuple(names), tuple(tuple(p.split("–")) for p in pairs))
    assert render_rooms(g, 4, "enemies", "No two enemies may share a room.") == rec["prompt"]


def test_e5_sat_library_inversion():
    rec = find("A_H_baselines", item_id="E5-SAT-I")
    cnf = cnf_from_ah_prompt(rec["prompt"])
    mine = ah_e5.sat_prompt(cnf, "I").splitlines()
    lib = rec["prompt"].splitlines()
    note = [i for i, l in enumerate(lib) if l.startswith("Note on the rule")]
    assert [l for i, l in enumerate(mine) if i not in note] == [l for i, l in enumerate(lib) if i not in note]
    both = cnf.with_clauses(list(cnf.clauses) + [tuple(-l for l in c) for c in cnf.clauses])
    assert S.solve(both) is None
    inv = SatTask(cnf, inverted=True)
    from reasoning_heuristics.heuristics.sat import effective_cnf
    sols = S.all_solutions(effective_cnf(inv))
    assert len(sols) == 1 and "".join("1" if sols[0][v] else "0" for v in cnf.var_names) == "1010010111"
    text = S.all_solutions(cnf)
    assert "".join("1" if text[0][v] else "0" for v in cnf.var_names) == "0101101000"


def test_e5_smoke_validates_and_preambles_match():
    items, _ = ah_e5.generate("smoke", 6)
    assert sorted(it.cell for it in items) == sorted(ah_e5.cells({}))
    assert run_checks(items, ah_e5.check_set)["failures"] == []
    for d in ah_e5.DOMAINS:
        n, i = ah_e5.PREAMBLE[d]
        assert len(n.split()) == len(i.split())


# --- E8 -----------------------------------------------------------------------------------------


TRACE = ("Let me start with x01 = 1. Then C03 needs x02 = 0. Now x03 = 1 and x04 = 0; "
         "checking C10: fine. Next x05 = 1, which forces x06 = T. Finally x07 = 0 and the formula looks satisfied.")


def test_e8_specs_reference_e2_items_and_validate():
    items, _ = ah_e8.generate("smoke", 1)
    assert sorted(it.cell for it in items) == sorted(ah_e8.cells({}))
    assert run_checks(items, ah_e8.check_set)["failures"] == []
    e2, _ = ah_e2.generate("smoke", 1, domains=["SAT"])
    e2_ids = {it.item_id: it for it in e2}
    for it in items:
        host = e2_ids[it.params["host_item_id"]]
        assert it.prompt == host.prompt and it.source_hash == host.content_hash


def test_e8_materialise():
    items, _ = ah_e8.generate("smoke", 1)
    by = {it.cell: it for it in items}
    m0 = ah_e8.materialise(by["early/K/f=0.0"], f"<think>{TRACE}</think> answer")
    assert m0["prefill"] == "<think>\n\n</think>\n\n" + ah_e8.FORCED_ANSWER_HEADER and not m0["continue_generation"]
    m5 = ah_e8.materialise(by["early/K/f=0.5"], TRACE)
    cut = m5["prefill"][len("<think>\n"):m5["prefill"].index("\n</think>")]
    assert TRACE.startswith(cut) and 0.3 * len(TRACE) < len(cut) < 0.7 * len(TRACE)
    tr = ah_e8.materialise(by["transplant/K->J"], TRACE)
    assert TRACE in tr["prefill"] and tr["prompt"] == by["transplant/K->J"].prompt
    mi = ah_e8.materialise(by["mistake/K"], TRACE)
    assert mi["continue_generation"] and mi["flipped"]["variable"] == "x05" and mi["prefill"].endswith("x05 = 0")
    with pytest.raises(ValueError):
        ah_e8.materialise(by["mistake/J"], "no assignments are written in this trace at all, only prose.")
