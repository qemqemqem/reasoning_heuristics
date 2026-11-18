"""Entailment members reproduce the B4/C4 vertical's computed prediction tables (§2.5 E1, E2)."""

import pytest

from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.tasks import EntailmentTask
from reasoning_heuristics.problems.entailment import formula as F

L = F.lit
aA, aB, bC, bD, cE = "box:red", "box:heavy", "jar:blue", "jar:cold", "cup:green"


def e1_task(T: str, P: int, O: str, fmt: str = "YN") -> EntailmentTask:
    d1, d2 = F.conj(L(aA), L(aB)), F.conj(L(bC), L(bD))
    pd = F.disj(d1, d2) if P == 1 else F.disj(d2, d1)
    second = {"M": L(aA), "N": L(aA, False), "U": L(cE), "V": F.disj(L(aA), L(cE))}[T]
    probe = L(bD) if T == "N" else L(aB)
    prem = (pd, second) if O == "DC" else (second, pd)
    if fmt == "YN":
        return EntailmentTask(prem, probe, "YN")
    options = (L(aB), L(bD), F.disj(L(aB), F.conj(L(bC), L(bD))), L(aB, False))
    return EntailmentTask(prem, None, "MC", options)


CELLS = [(T, P, O) for T in "MNUV" for P in (1, 2) for O in ("DC", "CD")]
TABLE = {
    "g": "0000 1111 0000 0000",
    "FIRST": "1100 XX11 1100 1100",
    "MATCH-L": "1010 1111 0000 0000",
    "MATCH-A": "1111 1111 0000 0000",
    "ETR-default": "1111 1111 0000 1111",
    "ETR-1p": "1010 1111 0000 1010",
    "ONL1": "1100 0111 1100 1100",
    "ONL2": "0000 1111 0000 1000",
    "PRIMACY": "1010 1010 1010 1010",
    "RECENCY": "0101 0101 0101 0101",
    "ALL1": "1111 1111 1111 1111",
    "ALL0": "0000 0000 0000 0000",
}
MEMBERS = {
    "g": [("EXACT", {}), ("MM-S1", {"variant": "open"}), ("BICOND", {}), ("CW-MIN", {}), ("CW-COMP", {}),
          ("ONL", {"k": 4}), ("UP-k", {"k": 1})],
    "FIRST": [("FIRST", {})],
    "MATCH-L": [("MATCH-L", {})],
    "MATCH-A": [("MATCH-A", {}), ("MM-S1", {"variant": "elim"})],
    "ETR-default": [("ETR-default", {"rendering": "R1"}), ("ETR-default", {"rendering": "R2"})],
    "ETR-1p": [("ETR-1p", {})],
    "ONL1": [("ONL", {"k": 1})],
    "ONL2": [("ONL", {"k": 2})],
    "PRIMACY": [("PRIMACY", {})],
    "RECENCY": [("RECENCY", {})],
    "ALL1": [("ALWAYS-YES", {}), ("AFFIRM", {}), ("GREEDY-MODEL", {})],
    "ALL0": [("NONE", {}), ("UP-k", {"k": 0})],
}


def _expected(row: str, T: str, P: int, O: str) -> str:
    # The doc's column order is T-major, then P, then O (DC before CD).
    bits = row.replace(" ", "")
    idx = "MNUV".index(T) * 4 + (P - 1) * 2 + (0 if O == "DC" else 1)
    return {"1": "YES", "0": "NO", "X": "X"}[bits[idx]]


@pytest.mark.parametrize("row", list(TABLE))
def test_e1_yes_no_table(row):
    for name, params in MEMBERS[row]:
        for T, P, O in CELLS:
            got = run("entailment", name, e1_task(T, P, O), params).answer
            assert got == _expected(TABLE[row], T, P, O), (row, name, params, T, P, O, got)


def test_e1_sample3_values():
    expected = {"M": 0.512, "N": 1.0, "U": 0.36, "V": 0.42}
    for T, P, O in CELLS:
        dist = run("entailment", "SAMPLE-m", e1_task(T, P, O), {"m": 3}).distribution
        assert dist["YES"] == pytest.approx(expected[T], abs=0.01)


def test_e1_mc_table_m_cells():
    # (DC, CD) letters: a = A (illusory), c = C (valid and strongest).
    table = {
        ("ETR-default", ()): "AC", ("ETR-1p", ()): "AC", ("MATCH-L", ()): "AC", ("MATCH-A", ()): "AA",
        ("FIRST", ()): "AA", ("ONL", (("k", 1),)): "AA", ("MM-S1", (("variant", "open"),)): "CC",
        ("ONL", (("k", 2),)): "CC", ("EXACT", ()): "CC",
    }
    for (name, params), letters in table.items():
        for O, want in zip(("DC", "CD"), letters):
            got = run("entailment", name, e1_task("M", 1, O, "MC"), dict(params)).answer
            assert got == want, (name, params, O, got)


def e2_task(form: str, inference: str, order: str) -> EntailmentTask:
    neg_a = form.startswith("¬A")
    neg_b = form.endswith("¬B")
    A, B = L(aA, not neg_a), L(bD, not neg_b)  # antecedent and consequent as stated

    def flip(x):
        return L(x[1], not x[2])

    rule = F.iff(A, B) if form == "A↔B" else F.cond(A, B)
    minor, probe = {"MP": (A, B), "AC": (B, A), "DA": (flip(A), flip(B)), "MT": (flip(B), flip(A))}[inference]
    prem = (rule, minor) if order == "cf" else (minor, rule)
    return EntailmentTask(prem, probe, "YN")


E2_IF = {  # affirmative A→B; columns MP·cf MP·mf AC·cf AC·mf DA·cf DA·mf MT·cf MT·mf
    ("EXACT", ()): "11000011",
    ("BICOND", ()): "11111111",
    ("CW-COMP", ()): "11111111",
    ("CW-MIN", ()): "11001111",
    ("MM-S1", ()): "11110000",
    ("MM-G", ()): "11110001",
    ("ETR-default", (("rendering", "R1"),)): "11000011",
    ("ETR-1p", (("rendering", "R1"),)): "11000010",
    ("ETR-default", (("rendering", "R2"),)): "11110011",
    ("ETR-1p", (("rendering", "R2"),)): "11100010",
    ("ONL", (("k", 1),)): "11110001",
    ("ONL", (("k", 1), ("on_empty", "strict"))): "1111X0X1",
    ("ONL", (("k", 2),)): "11000011",
    ("GREEDY-MODEL", ()): "111100X1",
    ("PRIMACY", ()): "10100000",
    ("RECENCY", ()): "01010000",
    ("AFFIRM", ()): "11110000",
    ("UP-k", (("k", 1),)): "11000011",
}
COLS = [(i, o) for i in ("MP", "AC", "DA", "MT") for o in ("cf", "mf")]


@pytest.mark.parametrize("key", list(E2_IF))
def test_e2_affirmative_if_table(key):
    name, params = key
    for (inf, order), want in zip(COLS, E2_IF[key]):
        got = run("entailment", name, e2_task("A→B", inf, order), dict(params)).answer
        assert got == {"1": "YES", "0": "NO", "X": "X"}[want], (name, params, inf, order, got)


NEG_ROWS = {  # MP AC DA MT, both orders unless the member is order-sensitive (C1 handled below)
    "A→¬B": {"AFFIRM": "0110", "CW-MIN": "1001", "MM-S1": "1100"},
    "¬A→B": {"AFFIRM": "1001", "CW-MIN": "1111", "MM-S1": "1100", "GREEDY-MODEL": "1001"},
    "¬A→¬B": {"AFFIRM": "0011", "CW-MIN": "1101", "MM-S1": "1100", "GREEDY-MODEL": "1011"},
}


@pytest.mark.parametrize("form", list(NEG_ROWS))
def test_e2_negation_forms(form):
    for name, bits in NEG_ROWS[form].items():
        for inf, want in zip(("MP", "AC", "DA", "MT"), bits):
            for order in ("cf", "mf"):
                got = run("entailment", name, e2_task(form, inf, order), {}).answer
                assert got == {"1": "YES", "0": "NO"}[want], (form, name, inf, order, got)
    # C1 on A→¬B: "1 1 1 X/1" (MT is X in cf, 1 in mf).
    assert run("entailment", "GREEDY-MODEL", e2_task("A→¬B", "MT", "cf"), {}).answer == "X"
    assert run("entailment", "GREEDY-MODEL", e2_task("A→¬B", "MT", "mf"), {}).answer == "YES"


def test_e2_iff():
    for inf, order in COLS:
        t = e2_task("A↔B", inf, order)
        for name, params in [("EXACT", {}), ("BICOND", {}), ("CW-MIN", {}), ("MM-S1", {}), ("MM-G", {}),
                             ("ETR-default", {}), ("ETR-1p", {}), ("ONL", {"k": 2})]:
            assert run("entailment", name, t, params).answer == "YES", (name, inf, order)
        onl1 = run("entailment", "ONL", t, {"k": 1}).answer
        if inf in ("DA", "MT"):
            assert onl1 == ("NO" if order == "cf" else "YES")
    # The doc's prose says C1 GREEDY-MODEL gives DA = MT = 0 on "iff" in both orders. Executing
    # its own §1.1 definition gives DA = YES (both orders) and MT = X (cf) / YES (mf); the
    # generators use the computed values (SCOPE §6 rule 5), and this is noted in GENERATORS.md.
    got = {(i, o): run("entailment", "GREEDY-MODEL", e2_task("A↔B", i, o), {}).answer for i in ("DA", "MT") for o in ("cf", "mf")}
    assert got == {("DA", "cf"): "YES", ("DA", "mf"): "YES", ("MT", "cf"): "X", ("MT", "mf"): "YES"}


def test_sample3_on_ac():
    assert run("entailment", "SAMPLE-m", e2_task("A→B", "AC", "cf"), {"m": 3}).distribution["YES"] == pytest.approx(0.125)


def test_greedy_cm_library_item():
    # C E5-ENT ORDER-A: 1. Not both E and C. 2. B or C. 3. Not both B and A. 4. E or A. Conclusion D.
    prem = (F.nand(L("E"), L("C")), F.disj(L("B"), L("C")), F.nand(L("B"), L("A")), F.disj(L("E"), L("A")))
    t = EntailmentTask(prem, L("D"), "YN")
    assert run("entailment", "EXACT", t).answer == "NO"
    assert run("entailment", "GREEDY-CM", t).answer == "YES"  # library: GREEDY-CM-MENTION says YES
