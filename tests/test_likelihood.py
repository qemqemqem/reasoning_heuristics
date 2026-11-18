"""Direct tests of the likelihood machinery in generators/common.py: outcome classes, the slip
model, set-valued members and the serialised channel."""

import math

import pytest

from reasoning_heuristics.generators import common as C
from reasoning_heuristics.generators.common import OTHER, SetSpec
from reasoning_heuristics.heuristics.answers import answer_key
from reasoning_heuristics.heuristics.tasks import ColouringTask, KnapsackTask, SatTask
from reasoning_heuristics.problems.coloring.graph import Graph
from reasoning_heuristics.problems.knapsack.knapsack import Knapsack
from reasoning_heuristics.problems.sat import cnf as S

# Three disjoint edges: chi = 2 and four optimal partitions.
G3 = Graph(("v10", "v11", "v12", "v13", "v14", "v15"), (("v10", "v11"), ("v12", "v13"), ("v14", "v15")))
TASK = ColouringTask(G3, None, (), tuple(G3.vertices))
FF = {"v10": 1, "v11": 2, "v12": 1, "v13": 2, "v14": 1, "v15": 2}  # {v10,v12,v14} | {v11,v13,v15}
SUBOPT = {"v10": 1, "v11": 2, "v12": 3, "v13": 1, "v14": 1, "v15": 2}  # proper, 3 colours
UNLISTED_OPT = {"v10": 1, "v11": 2, "v12": 2, "v13": 1, "v14": 1, "v15": 2}  # optimal, nobody predicts it
ALL_ONE = {v: 1 for v in G3.vertices}  # invalid


def rec(member, answer=None, distribution=None, trace=None):
    return {"member": member, "family": "x", "params": {}, "answer": answer, "trace_features": trace or {},
            "distribution": distribution}


def col_preds():
    return {
        "FF-LIST": rec("FF", FF),
        "GREEDY+REPAIR": rec("GREEDY+REPAIR", SUBOPT),
        "EXACT": rec("EXACT", "CHI=2", trace={"set_valued": True}),
        "RANDOM (H)": rec("RANDOM", None, trace={"set_valued": True}),
        "NOISY-EXACT": rec("NOISY-EXACT", None, {"_exact": 0.7, "_other": 0.3}),
    }


def col_channel():
    return C.witness_channel("coloring", {
        "EXACT": SetSpec("colouring", {"graph": "stated", "colours": 2, "exactly": True}, 4, "optimal colouring"),
        "RANDOM (H)": C.uniform_fill("uniform over 6^6 colourings", 6, 6),
    }, task=TASK)


def key_of(col):
    return answer_key("coloring", col)


def test_invalid_answers_are_kept_apart_from_unlisted_solutions():
    ch = col_channel()
    lt = C.likelihood_table(col_preds(), ch)
    region = C.REGION + "EXACT"
    assert lt.keys == [key_of(FF), key_of(SUBOPT), region, OTHER]
    assert C.classify_answer(ch, lt.keys, ALL_ONE) == OTHER
    assert C.classify_answer(ch, lt.keys, UNLISTED_OPT) == region
    assert C.classify_answer(ch, lt.keys, FF) == key_of(FF)
    table, classes = C.disconfirms(col_preds(), ch)
    other = next(lbl for lbl, k in classes.items() if k == OTHER)
    unlisted = next(lbl for lbl, k in classes.items() if k == region)
    # An invalid answer is evidence against EXACT (it only slips there) ...
    assert table[other]["EXACT"] > 1.0 and table[other]["RANDOM (H)"] == 0.0
    # ... and an unlisted optimal colouring is evidence for it, against FF.
    assert table[unlisted]["EXACT"] == 0.0 and table[unlisted]["FF-LIST"] > 1.0
    # EXACT's mass: 1/4 on FF's (optimal) answer, 3/4 on its unlisted solutions, nothing on the suboptimal one.
    K = lt.K
    assert lt.probs["EXACT"][key_of(FF)] == pytest.approx(0.9 * 0.25 + 0.1 / K)
    assert lt.probs["EXACT"][region] == pytest.approx(0.9 * 0.75 + 0.1 / K)
    assert lt.probs["EXACT"][key_of(SUBOPT)] == pytest.approx(0.1 / K)
    # NOISY-EXACT's "_exact" mass is spread like EXACT, its slips are invalid answers.
    assert lt.probs["NOISY-EXACT"][region] == pytest.approx(0.9 * 0.7 * 0.75 + 0.1 / K)
    assert lt.probs["NOISY-EXACT"][OTHER] == pytest.approx(0.9 * 0.3 + 0.1 / K)


def test_slip_is_one_lapse_formula_for_every_member():
    lt = C.likelihood_table(col_preds(), col_channel())
    K = lt.K
    for label, p in lt.probs.items():
        assert sum(p.values()) == pytest.approx(1.0), label
    assert lt.probs["FF-LIST"][key_of(FF)] == pytest.approx(1 - C.EPS + C.EPS / K)
    assert lt.probs["FF-LIST"][key_of(SUBOPT)] == pytest.approx(C.EPS / K)
    # a distributional member with a point mass gets the deterministic member's row
    preds = {**col_preds(), "POINT": rec("RO-FF", None, {key_of(FF): 1.0})}
    lt2 = C.likelihood_table(preds, col_channel())
    assert lt2.probs["POINT"] == pytest.approx(lt2.probs["FF-LIST"])


def test_hypothesis_texts_match_the_slip_model():
    preds = col_preds()
    ch = col_channel()
    lt = C.likelihood_table(preds, ch)
    hyp = C.hypotheses("coloring", preds, {}, "", lt, ch)
    own = 1 - C.EPS + C.EPS / lt.K
    assert f"{own:.3f}" in hyp["FF-LIST"]["eval_prediction"]
    assert "0.90 " not in hyp["EXACT"]["eval_prediction"] and "set-valued" in hyp["EXACT"]["eval_prediction"]
    assert "4 solutions" in hyp["EXACT"]["output"]


def test_unique_solutions_are_deterministic_classes():
    """A/H E5 KNAP I: exact (covering) and TT (packing) have unique, different optima."""
    k = Knapsack(tuple("ABCD"), (6, 3, 3, 1), (4, 3, 2, 1), 5)
    task = KnapsackTask(k, covering=True)
    assert C.rule_subset(task, "B,C") and C.rule_subset(task, "A,D", objective="textbook")
    preds = {"exact": rec("EXACT", ["B", "C"]), "A3 TT[exact]": rec("TT", ["A", "D"])}
    ch = C.witness_channel("knapsack", {
        "exact": SetSpec("subset", {"objective": "stated"}, 1, "covering optimum", solution="B,C"),
        "A3 TT[exact]": SetSpec("subset", {"objective": "textbook"}, 1, "packing optimum", solution="A,D"),
    }, task=task, overlaps={("exact", "A3 TT[exact]"): 0})
    table, classes = C.disconfirms(preds, ch)
    assert set(classes.values()) == {"A,D", "B,C", OTHER}
    assert table["answer = B,C"]["A3 TT[exact]"] > 1.0 and table["answer = B,C"]["exact"] == 0.0
    assert table["answer = A,D"]["exact"] > 1.0
    assert C.distinct_answers(preds, ch) == 2


def test_a_member_without_a_row_fails_loudly():
    preds = col_preds()
    with pytest.raises(ValueError, match="not listed"):  # the "RANDOM" vs "RANDOM (H)" label mismatch
        C.likelihood_table(preds, C.witness_channel("coloring", {"RANDOM": C.uniform_fill("x", 6, 6)}, task=TASK))
    with pytest.raises(ValueError, match="needs a row"):  # RANDOM (H) with no spec has no prediction at all
        C.likelihood_table(preds, C.witness_channel("coloring", {
            "EXACT": SetSpec("colouring", {"graph": "stated", "colours": 2, "exactly": True}, 4, "optimal")}, task=TASK))


def test_answers_without_a_reading_are_class_other():
    """C E3: FF-OUT's IMPOSSIBLE on the target-bit channel is an outcome (other), not a missing row."""
    preds = {"FF-LIST": rec("FF", FF), "FF-OUT": rec("FF", "IMPOSSIBLE"),
             "EXACT": rec("EXACT", "POSSIBLE", trace={"set_valued": True})}
    ch = C.target_bit_channel("v14", "v10", {"EXACT": SetSpec("colouring", {"graph": "stated", "colours": 2}, 4, "2-colourings",
                                                               class_counts={"same": 2, "different": 2})})
    lt = C.likelihood_table(preds, ch)
    assert lt.keys == ["same", "different", OTHER]
    assert lt.probs["FF-OUT"][OTHER] == pytest.approx(1 - C.EPS + C.EPS / 3)
    assert lt.probs["EXACT"]["different"] == pytest.approx(0.9 * 0.5 + 0.1 / 3)


def test_unsat_is_always_a_class_on_sat_witness_channels():
    """C E1-SAT: an UNSAT answer to a satisfiable formula must not be explained by EXACT."""
    cnf = S.CNF(("x10", "x11", "x12"), ((1, 2), (-1, 3)))
    task = SatTask(cnf)
    n = S.count_solutions(cnf)
    greedy = {"x10": True, "x11": True, "x12": True}
    preds = {"GREEDY": rec("GREEDY", greedy), "EXACT": rec("EXACT", "SAT", trace={"set_valued": True}),
             "RO-GREEDY": rec("RO-GREEDY", None, {answer_key("sat", greedy): 0.5, "UNSAT": 0.5})}
    ch = C.witness_channel("sat", {"EXACT": SetSpec("assignment", {"cnf": "stated"}, n, "satisfying assignment")},
                           task=task, values=("UNSAT",))
    table, classes = C.disconfirms(preds, ch)
    assert table["answer = UNSAT"]["EXACT"] > 1.0 and table["answer = UNSAT"]["RO-GREEDY"] == 0.0
    assert C.classify_answer(ch, list(classes.values()), "UNSAT") == "UNSAT"


def test_overlapping_solution_sets():
    """A/H E5: exact (stated rule) and TT (textbook rule) - identical sets merge, disjoint sets split."""
    task = ColouringTask(G3, 2)
    spec = SetSpec("colouring", {"graph": "stated", "colours": 2}, 4, "valid 2-colouring")
    tt = SetSpec("colouring", {"graph": "textbook", "colours": 2}, 4, "valid 2-colouring, textbook")
    preds = {"FF": rec("FF", FF), "exact": rec("EXACT", "POSSIBLE"), "A3 TT[exact]": rec("TT", UNLISTED_OPT)}
    same = C.likelihood_table(preds, C.witness_channel("coloring", {"exact": spec, "A3 TT[exact]": tt}, task=task,
                                                       overlaps={("exact", "A3 TT[exact]"): 4}))
    assert [k for k in same.keys if k.startswith(C.REGION)] == [C.REGION + "A3 TT[exact]+exact"]
    assert same.probs["exact"] == pytest.approx(same.probs["A3 TT[exact]"])
    with pytest.raises(ValueError, match="declared overlap"):
        C.likelihood_table(preds, C.witness_channel("coloring", {"exact": spec, "A3 TT[exact]": tt}, task=task))
    with pytest.raises(ValueError, match="exceed the declared size"):  # identical sets declared disjoint
        C.likelihood_table(preds, C.witness_channel("coloring", {"exact": spec, "A3 TT[exact]": tt}, task=task,
                                                    overlaps={("exact", "A3 TT[exact]"): 0}))


def test_channel_round_trip_rebuilds_the_same_table():
    ch = col_channel()
    again = C.channel_from_json(ch.to_json(), TASK)
    assert C.disconfirms(col_preds(), again) == C.disconfirms(col_preds(), ch)
    assert math.isclose(C.likelihood_table(col_preds(), again).probs["EXACT"][OTHER],
                        C.likelihood_table(col_preds(), ch).probs["EXACT"][OTHER])


def test_membership_rules():
    assert C.rule_colouring(TASK, key_of(UNLISTED_OPT), colours=2, exactly=True)
    assert not C.rule_colouring(TASK, key_of(SUBOPT), colours=2, exactly=True)
    assert not C.rule_colouring(TASK, key_of(ALL_ONE), colours=6)
    fixed = ColouringTask(G3, 2, (("v10", 2), ("v12", 1)))
    assert C.rule_colouring(fixed, key_of(UNLISTED_OPT), colours=2)  # v10, v12 in different classes
    assert not C.rule_colouring(fixed, key_of(FF), colours=2)  # v10 and v12 share a class but not a colour
    cnf = S.CNF(("x10", "x11"), ((1, 2),))
    assert C.rule_assignment(SatTask(cnf), "x10=T,x11=F")
    assert not C.rule_assignment(SatTask(cnf, (("x10", False),)), "x10=T,x11=F")
    assert C.rule_assignment(SatTask(cnf, inverted=True), "x10=F,x11=T") and not C.rule_assignment(
        SatTask(cnf, inverted=True), "x10=T,x11=T")
    k = Knapsack(tuple("ABC"), (3, 2, 2), (2, 1, 1), 2)
    assert C.rule_subset(KnapsackTask(k), "B,C") and not C.rule_subset(KnapsackTask(k), "A")
