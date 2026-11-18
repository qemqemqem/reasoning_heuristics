"""The scorer against real committed items: every answer format, every renderable member prediction
scored back to that member's outcome class, plus adversarial responses."""

from __future__ import annotations

import json
from collections import Counter

import pytest
from evals_helpers import api_response, committed_items, first_with, render, runnable

from reasoning_heuristics.evals.scoring import (CATEGORIES, SCORER_VERSION, ItemContext, ResponseView, UnsupportedItem,
                                                answer_format, score_response)
from reasoning_heuristics.heuristics.answers import answer_key
from reasoning_heuristics.heuristics.tasks import load_task
from reasoning_heuristics.problems.coloring import graph as G

FORMATS = ["json_sat", "json_col", "json_ent_yn", "json_ent_open", "json_knap", "ans_col", "ans_sat", "ans_knap",
           "ans_single_colour", "ans_yn", "ans_letter"]


def score_text(item, content, **kw):
    return score_response(item, ResponseView.from_api(api_response(content, **kw), max_tokens=kw.pop("max_tokens", 32768)))


def independent_class_key(item, answer):
    """The channel value of a member answer, written out per channel without the scorer's code."""
    ch = item["extra"]["channel"]
    if ch == "decision":
        if isinstance(answer, str):
            return {"X": "NO"}.get(answer, answer)
        return {"sat": "SAT", "coloring": "POSSIBLE", "entailment": "YES"}[load_task(item["instance"]).domain]
    if ch == "target-bit":
        if not isinstance(answer, dict):
            return None
        return "same" if answer[item["params"]["target"]] == answer[item["params"]["reference_vertex"]] else "different"
    if ch == "target-colour":
        return str(answer[item["params"]["target"]]) if isinstance(answer, dict) else None
    return answer_key(load_task(item["instance"]).domain, answer)


def test_smoke_items_cover_every_answer_format():
    kinds = Counter(answer_format(it).kind for it in runnable(committed_items("smoke")))
    assert sorted(kinds) == sorted(FORMATS)


def test_e8_specs_are_unsupported():
    e8 = [it for it in committed_items("smoke") if it["eval_id"] == "E8"]
    assert e8
    with pytest.raises(UnsupportedItem):
        answer_format(e8[0])


@pytest.mark.parametrize("kind", FORMATS)
def test_member_predictions_score_back_to_their_outcome_class(kind):
    """Each member's own prediction, written in the item's format, parses back to the same answer and
    lands in that member's outcome class (and the member is among `members_matched`)."""
    items = [it for it in runnable(committed_items("smoke")) if answer_format(it).kind == kind]
    checked = 0
    for it in items:
        classes = it["extra"]["outcome_classes"]
        for label, pred in it["predictions"].items():
            ans = pred["answer"]
            if ans is None or (pred.get("trace_features") or {}).get("set_valued"):
                continue
            text = render(it, ans)
            if text is None:
                continue
            rec = score_text(it, text)
            assert rec["category"] == "ok", (it["item_id"], label, rec["parse_detail"])
            assert rec["scorer_version"] == SCORER_VERSION
            want = independent_class_key(it, ans)
            assert rec["channel_value"] == want, (it["item_id"], label)
            if want in classes.values():
                got_label = rec["outcome_class"]
                assert classes[got_label] == want
                # the member's own class, unless the generator kept it out of the classes (set-valued on
                # this channel, e.g. "A3 TT[exact]") and its answer coincides with another member's
                assert (label in got_label or got_label == f"answer = {want}"
                        or not any(label in lbl for lbl in classes)), (got_label, label)
            else:
                assert rec["outcome_class"] == next(k for k, v in classes.items() if v == "_other")
            # no reading on the channel (IMPOSSIBLE on a bit channel): the match shows on the answer key only
            assert label in (rec["members_matched"] if want is not None else rec["answer_key_matches"])
            if kind != "ans_single_colour" and not (it["extra"]["channel"] == "decision" and isinstance(ans, str)
                                                    and rec["parsed"] != ans):
                assert rec["answer_key"] == answer_key(load_task(it["instance"]).domain, ans), (it["item_id"], label)
            checked += 1
    assert checked >= 3, f"only {checked} member answers checked for {kind}"


def test_channel_reconstruction_matches_every_committed_item():
    """For every runnable smoke and dev item, the rebuilt channel maps each deterministic member's
    answer onto one of the item's stored outcome classes (so outcome classes cannot drift)."""
    n = 0
    for tier in ("smoke", "dev"):
        for it in runnable(committed_items(tier)):
            ctx = ItemContext(it)
            values = set(it["extra"]["outcome_classes"].values())
            for label, pred in it["predictions"].items():
                if pred["answer"] is None or (pred.get("trace_features") or {}).get("set_valued"):
                    continue
                key = ctx.channel.key(pred["answer"])
                if key is None:  # the member has no reading on this channel (e.g. "POSSIBLE" on a bit channel)
                    continue
                assert key in values or label.lower().startswith(("exact", "a3 tt[exact]")), (it["item_id"], label, key)
                n += 1
    assert n > 5000


# --- correctness against ground truth ------------------------------------------------------------------


def test_fewest_colours_correct_iff_proper_and_optimal():
    it = first_with("ans_col", vertical="C", eval_id="E1")
    task = load_task(it["instance"])
    seen = set()
    for label, pred in it["predictions"].items():
        if isinstance(pred["answer"], dict):
            rec = score_text(it, render(it, pred["answer"]))
            proper = G.is_proper(task.graph, pred["answer"])
            assert rec["valid"] == proper
            assert rec["correct"] == (proper and G.n_colours(pred["answer"]) == it["ground_truth"]["chromatic_number"])
            seen.add(rec["correct"])
    assert seen == {True, False}


def test_sat_witness_validity_and_unsat_claim():
    it = next(i for i in runnable(committed_items("smoke")) if i["item_id"].endswith("SAT_DEAD"))
    recs = {label: score_text(it, render(it, p["answer"])) for label, p in it["predictions"].items()
            if p["answer"] is not None and render(it, p["answer"]) is not None}
    assert recs["GREEDY-MENTION-ABORT (C1)"]["parsed"] == "UNSAT"
    assert recs["GREEDY-MENTION-ABORT (C1)"]["correct"] is False  # the formula is satisfiable
    assert recs["GREEDY-MENTION-INFEAS (C1)"]["valid"] is False  # an assignment that falsifies a clause
    assert recs["DPLL-MENTION (D)"]["valid"] is True and recs["DPLL-MENTION (D)"]["correct"] is True


def test_partial_colouring_given_must_keep_fixed_colours():
    it = first_with("ans_col", domain="colouring (k=3, partial colouring given)")
    task = load_task(it["instance"])
    sol = G.k_colour(task.graph, 3, task.fixed_dict())
    assert score_text(it, render(it, sol))["correct"] is True
    # swap two colour names everywhere: still a proper 3-colouring, but the fixed colours change
    swapped = {v: {1: 2, 2: 1}.get(c, c) for v, c in sol.items()}
    rec = score_text(it, render(it, swapped))
    assert rec["category"] == "ok" and rec["valid"] is False and rec["correct"] is False


def test_knapsack_feasibility_and_optimality():
    it = first_with("ans_knap")
    names = load_task(it["instance"]).knapsack.names
    every = score_text(it, "ANSWER:\n" + ", ".join(names))
    assert every["category"] == "ok" and every["valid"] is False and every["correct"] is False
    opt = score_text(it, render(it, it["predictions"]["EXACT"]["answer"]))
    assert opt["valid"] and opt["optimal"] and opt["correct"]


def test_inverted_rule_items_are_judged_under_the_stated_rule():
    """A/H E5: A3 TT[exact] solves the *textbook* rule. Under the stated rule its answer is right only
    where the generator says so (`tt_answer_violations_under_stated`, the stated optimal subsets, the
    stated entailment)."""
    seen = Counter()
    for it in runnable(committed_items("smoke")):
        if it["eval_id"] != "E5" or it["vertical"] != "A/H":
            continue
        pred = it["predictions"].get("A3 TT[exact]")
        if pred is None or render(it, pred["answer"]) is None:
            continue
        rec = score_text(it, render(it, pred["answer"]))
        gt = it["ground_truth"]
        assert rec["category"] == "ok", it["item_id"]
        if "tt_answer_violations_under_stated" in gt:
            assert rec["valid"] == (gt["tt_answer_violations_under_stated"] == 0), it["item_id"]
        elif "optimal_subsets" in gt:
            assert rec["correct"] == (sorted(pred["answer"]) in [sorted(s) for s in gt["optimal_subsets"]]), it["item_id"]
        else:
            assert rec["correct"] == (pred["answer"] == gt["answer"]), it["item_id"]
        seen[rec["correct"]] += 1
    assert seen[True] and seen[False]  # the textbook answer is right in T cells and wrong in some inverted ones


def test_bare_answer_without_marker_only_when_it_is_nothing_but_the_answer():
    """Direct replies often drop the ANSWER: marker (seen live: Qwen3-32B direct wrote just "UNSAT", "NO")."""
    sat = first_with("ans_sat", vertical="C", eval_id="E1")
    rec = score_text(sat, "UNSAT")
    assert rec["category"] == "ok" and rec["parsed"] == "UNSAT" and "no_answer_marker" in rec["flags"]
    pred = next(p["answer"] for p in sat["predictions"].values() if isinstance(p["answer"], dict))
    assert score_text(sat, render(sat, pred).split("\n", 1)[1])["parsed"] == pred
    assert score_text(sat, "The formula is UNSAT.")["category"] == "parse_fail"
    yn = first_with("ans_yn", vertical="C")
    assert score_text(yn, "NO")["parsed"] == "NO" and score_text(yn, "no.")["parsed"] == "NO"
    assert score_text(yn, "I think NO")["category"] == "parse_fail"
    mc = first_with("ans_letter")
    assert score_text(mc, "(C)")["parsed"] == "C" and score_text(mc, "Probably C")["category"] == "parse_fail"
    one = first_with("ans_single_colour")
    assert score_text(one, "2")["parsed"] == {answer_format(one).target: 2}
    knap = first_with("ans_knap")
    assert score_text(knap, "A, C, H")["parsed"] == ["A", "C", "H"]
    col = first_with("ans_col", vertical="C", eval_id="E1")
    sol = col["predictions"]["DSATUR"]["answer"]
    lines = render(col, sol).split("\n", 1)[1]
    assert score_text(col, lines)["category"] == "ok"
    assert score_text(col, "Here is my colouring:\n" + lines)["category"] == "parse_fail"


def test_trailing_periods_after_values():
    it = first_with("ans_single_colour")
    want = it["ground_truth"]["answer"]
    assert score_text(it, f"ANSWER: {want}.")["parsed"] == {answer_format(it).target: want}
    assert score_text(it, "ANSWER: 1.5")["category"] == "parse_fail"
    sat = first_with("ans_sat", vertical="C", eval_id="E1")
    pred = next(p["answer"] for p in sat["predictions"].values() if isinstance(p["answer"], dict))
    assert score_text(sat, render(sat, pred) + ".")["category"] == "ok"


def test_single_colour_against_instructed_first_fit():
    it = first_with("ans_single_colour")
    target, want = answer_format(it).target, it["ground_truth"]["answer"]
    assert score_text(it, f"ANSWER:\n{want}")["correct"] is True
    rec = score_text(it, f"ANSWER: {target}: {want + 1}")  # the vertex label is not read as the colour
    assert rec["parsed"] == {target: want + 1} and rec["correct"] is False


# --- adversarial responses ------------------------------------------------------------------------------------


def test_last_answer_block_wins():
    it = first_with("ans_yn", vertical="B4/C4")
    rec = score_text(it, "ANSWER: YES\n\nWait, statement 2 rules that out.\n\nANSWER: NO")
    assert rec["parsed"] == "NO" and rec["n_answer_blocks"] == 2 and "answer_blocks_disagree" in rec["flags"]
    js = first_with("json_ent_yn")
    rec = score_text(js, 'First guess {"follows": true}\nOn reflection:\n{"follows": false}')
    assert rec["parsed"] == "NO" and "answer_blocks_disagree" in rec["flags"]


def test_code_fences_markdown_and_case_are_tolerated():
    it = first_with("ans_col", vertical="C", eval_id="E1")
    sol = it["predictions"]["DSATUR"]["answer"]
    body = render(it, sol).split("\n", 1)[1]
    rec = score_text(it, f"Here it is.\n\n**Answer:**\n```text\n{body}\n```\n")
    assert rec["category"] == "ok" and rec["parsed"] == {v: sol[v] for v in load_task(it["instance"]).graph.vertices}
    js = first_with("json_sat", eval_id="E1")
    rec = score_text(js, 'Done.\n```json\n{"Satisfiable": false, "assignment": null}\n```')
    assert rec["parsed"] == "UNSAT"
    yn = first_with("ans_yn", vertical="B4/C4")
    assert score_text(yn, "answer: **yes.**")["parsed"] == "YES"


def test_missing_vertex_is_partial_and_unknown_vertex_is_parse_fail():
    it = first_with("ans_col", vertical="C", eval_id="E1")
    sol = it["predictions"]["DSATUR"]["answer"]
    lines = render(it, sol).splitlines()
    rec = score_text(it, "\n".join(lines[:-1]))
    assert rec["category"] == "partial" and rec["parsed"] is None and rec["correct"] is None
    rec = score_text(it, "\n".join(lines) + "\nv999: 1")
    assert rec["category"] == "parse_fail" and "unknown vertex" in rec["parse_detail"]
    first_v = lines[1].split(":")[0]
    rec = score_text(it, "\n".join(lines) + f"\n{first_v}: 99")
    assert rec["category"] == "parse_fail" and "two values" in rec["parse_detail"]


def test_missing_variable_on_witness_and_decision_channels():
    wit = first_with("ans_sat", vertical="C", eval_id="E1")
    pred = next(p["answer"] for p in wit["predictions"].values() if isinstance(p["answer"], dict))
    text = render(wit, pred)
    assert score_text(wit, text.rsplit(",", 1)[0])["category"] == "partial"
    dec = first_with("json_sat", eval_id="E1")
    n = len(load_task(dec["instance"]).cnf.var_names)
    rec = score_text(dec, json.dumps({"satisfiable": True, "assignment": "1" * (n - 1)}))
    assert rec["category"] == "ok" and rec["parsed"] == "SAT" and "witness_partial" in rec["flags"]
    assert rec["outcome_class"] == "answer = SAT" and rec["valid"] is None
    e5 = first_with("json_sat", eval_id="E5")
    n5 = len(load_task(e5["instance"]).cnf.var_names)
    assert score_text(e5, json.dumps({"satisfiable": True, "assignment": "1" * (n5 - 1)}))["category"] == "partial"
    assert score_text(e5, json.dumps({"satisfiable": True, "assignment": "1" * (n5 + 1)}))["category"] == "parse_fail"


def test_extra_prose_around_the_answer():
    it = first_with("ans_knap")
    ans = it["predictions"]["EXACT"]["answer"]
    rec = score_text(it, "Let me weigh the options.\nANSWER:\n" + ", ".join(ans) + "\n\nThat uses most of the capacity.")
    assert rec["category"] == "ok" and rec["parsed"] == sorted(ans) and rec["pre_answer_tokens"] > 0
    js = first_with("json_knap")
    rec = score_text(js, json.dumps({"items": js["predictions"]["exact"]["answer"]}) + "\nHope this helps!")
    assert rec["category"] == "ok" and "text_after_answer" in rec["flags"]


def test_refusal_and_content_filter():
    it = first_with("ans_yn", vertical="B4/C4")
    assert score_text(it, "I'm sorry, but I can't help with that.")["category"] == "refusal"
    assert score_text(it, "", finish="content_filter")["category"] == "refusal"


def test_declared_impossible_versus_legal_impossible():
    fewest = first_with("ans_col", vertical="C", eval_id="E1")
    assert score_text(fewest, "ANSWER:\nIMPOSSIBLE")["category"] == "declared_impossible"
    kcol = first_with("ans_col", vertical="C", eval_id="E5")
    rec = score_text(kcol, "ANSWER:\nIMPOSSIBLE")
    assert rec["category"] == "ok" and rec["parsed"] == "IMPOSSIBLE" and rec["correct"] is (not rec["valid"] and
                                                                                             kcol["ground_truth"]["colourable"] is False)
    yn = first_with("ans_yn", vertical="B4/C4")
    assert score_text(yn, "ANSWER: CANNOT BE DETERMINED")["category"] == "declared_impossible"
    assert score_text(yn, "This is too complex to determine by hand.")["category"] == "declared_impossible"
    js = first_with("json_ent_yn")
    assert score_text(js, '{"follows": "unknown"}')["category"] == "declared_impossible"
    sat = first_with("ans_sat", vertical="C", eval_id="E1")
    rec = score_text(sat, "ANSWER:\nUNSAT")
    assert rec["category"] == "ok" and rec["parsed"] == "UNSAT"


def test_truncation_wins_and_is_censored():
    it = first_with("ans_yn", vertical="B4/C4")
    rec = score_text(it, "ANSWER: YES", finish="length")
    assert rec["category"] == "truncated" and rec["truncated"] and rec["parse_status"] == "ok"
    assert rec["outcome_class"] is None and rec["correct"] is None
    rec = score_text(it, None, finish="length", completion_tokens=32768)
    assert rec["category"] == "truncated"
    rec = score_response(it, ResponseView.from_api(api_response("ANSWER: NO", completion_tokens=1024), max_tokens=1024))
    assert rec["category"] == "truncated"


def test_empty_content_inline_think_and_loose_json():
    it = first_with("ans_yn", vertical="B4/C4")
    rec = score_text(it, "", reasoning="... so ANSWER: YES")
    assert rec["category"] == "parse_fail" and "answer_only_in_reasoning" in rec["flags"]
    # a trace cut at the cap that merely quotes the prompt's format is not "an answer in the reasoning"
    js = first_with("json_sat", eval_id="E1")
    rec = score_text(js, None, reasoning='The answer must look like {"satisfiable": true, "assignment": "0101"} ... C008: (x04',
                     finish="length", completion_tokens=32768)
    assert rec["category"] == "truncated" and "answer_only_in_reasoning" not in rec["flags"]
    rec = score_text(it, "<think>ANSWER: YES</think>\nANSWER: NO")
    assert rec["parsed"] == "NO" and "think_in_content" in rec["flags"] and rec["n_answer_blocks"] == 1
    js = first_with("json_ent_yn")
    rec = score_text(js, "{'follows': True}")
    assert rec["parsed"] == "YES" and "loose_json" in rec["flags"]


def test_mc_letters():
    it = first_with("ans_letter")
    assert score_text(it, "ANSWER: (C)")["parsed"] == "C"
    assert score_text(it, "ANSWER: c) the coin is dry")["parsed"] == "C"
    assert score_text(it, "ANSWER: None of these")["parsed"] == "E"
    assert score_text(it, "ANSWER: F")["category"] == "parse_fail"


def test_ent_open_facts_map_to_canonical_literals():
    it = first_with("json_ent_open")
    want = it["ground_truth"]["answer"]
    shouted = [f.upper() + "." for f in want] if isinstance(want, list) else want
    rec = score_text(it, json.dumps({"conclusion": shouted}))
    assert rec["category"] == "ok" and rec["parsed"] == want and rec["correct"] is True
    assert score_text(it, json.dumps({"conclusion": ["the moon is made of cheese"]}))["category"] == "parse_fail"
    assert score_text(it, json.dumps({"conclusion": []}))["parsed"] == "NOTHING"


def test_pre_answer_tokens_counts_visible_working():
    it = first_with("ans_yn", vertical="B4/C4")
    assert score_text(it, "ANSWER: YES")["pre_answer_tokens"] == 0
    assert score_text(it, "Statement 1 gives two cases.\nANSWER: YES")["pre_answer_tokens"] == 6  # 5 words + "."


def test_api_error_record():
    it = first_with("ans_yn", vertical="B4/C4")
    rec = score_response(it, ResponseView.from_api(None, error="HTTP 503 after 6 attempts"))
    assert rec["category"] == "api_error" and rec["parsed"] is None


def test_every_category_is_reachable():
    it = first_with("ans_col", vertical="C", eval_id="E1")
    sol = it["predictions"]["DSATUR"]["answer"]
    lines = render(it, sol).splitlines()
    cats = {
        score_text(it, "\n".join(lines))["category"],
        score_text(it, "no idea")["category"],
        score_text(it, "I cannot help with that request.")["category"],
        score_text(it, "ANSWER: IMPOSSIBLE")["category"],
        score_text(it, "\n".join(lines[:-2]))["category"],
        score_text(it, "\n".join(lines), finish="length")["category"],
        score_response(it, ResponseView.from_api(None, error="boom"))["category"],
    }
    assert cats == set(CATEGORIES)
