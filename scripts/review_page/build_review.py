"""Build the Stage 1 item-review page from the generators worktree's dev batches.

Picks four to six items per eval (PICKS: each domain and the main contrasts) and writes the page
to the path given (default review.html in the current directory). The published page keeps marks in
its artifact store: collection `reviews` (one document per item) and `generator_notes` (one per eval).
"""
import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
REPO_BLOB = "https://github.com/qemqemqem/reasoning_heuristics/blob/generators"

EVALS = OrderedDict([
    ("AH_E1", dict(name="Structure-blindness pairs", vertical="A/H baselines",
        tests="Each set is a pair of instances with the same surface statistics (size, clause density, "
              "polarity counts, token multiset). In critical pairs the true answer flips; in null pairs it "
              "stays. A model that reads only cues answers both members of a pair alike.",
        check=["The two members of a pair differ only in the edited literals or edges.",
               "Nothing in the prompt hints which member was edited.",
               "Prompt and answer format are clear."])),
    ("AH_E2", dict(name="Cue moves", vertical="A/H baselines",
        tests="Padding clauses over fresh pure variables move the density cue while the answer stays fixed: "
              "K raises clauses per variable to 4.78, J lowers it to 3.79, U declares unused variables.",
        check=["The padding reads like ordinary clauses.",
               "K and J differ only in how many fresh variables carry the padding.",
               "Nothing marks the padding as padding."])),
    ("AH_E5", dict(name="Rule inversion", vertical="A/H baselines",
        tests="One constraint list under the textbook rule (T), with a neutral preamble (N), with an inverted rule "
              "(I), with the inverted rule plus a reminder (I+R) and, for SAT, with half the clauses inverted (P). "
              "A model that applies the textbook rule anyway gives the textbook solution under I.",
        check=["The inverted rule cannot be misread.",
               "The neutral preamble adds no information.",
               "The textbook solution really violates the inverted rule."])),
    ("AH_E8", dict(name="Trace faithfulness specs", vertical="A/H baselines",
        tests="No prompts yet: each item is a spec for continuing the model's own response to an earlier item "
              "(cut it early, transplant another instance's trace, or insert a mistake) and then forcing an answer. "
              "The prompt shown is the host item's.",
        check=["The test fits its host item.",
               "For transplants, the donor's cue value differs from the host's.",
               "The forced-answer header is neutral."])),
    ("B4C4_E1", dict(name="Disjunction gadget", vertical="B4/C4 restriction and online update",
        tests="\"Either (a is A and a is B), or (b is C and b is D)\" plus a second premise, then: does a claim follow? "
              "ETR and mental-model members endorse the illusory \"a is B\" after \"a is A\". Factors: disjunct position, "
              "premise order, second-premise type, yes/no vs multiple choice.",
        check=["The sentences read naturally for the drawn lexicon.",
               "The correct answer is right.",
               "Multiple-choice options don't lead."])),
    ("B4C4_E2", dict(name="Conditional inferences", vertical="B4/C4 restriction and online update",
        tests="The four conditional inferences (MP, AC, DA, MT) × premise order × five forms (A→B, three negated forms, "
              "A↔B), plus an instruction cell (\"'if X, then Y' does not mean 'if Y, then X'\"). The readout is the "
              "endorsement profile, compared with each member's profile.",
        check=["Negated antecedents and consequents read naturally.",
               "The neutral note is neutral and about as long as the instruction.",
               "The correct answers are right (all four follow for ↔)."])),
    ("C_E1", dict(name="Order source", vertical="C constructive",
        tests="Six isomorphic copies of one instance: natural labels, relabelled, answer asked in label order, in a random "
              "order or in any order, and relisted. First-fit in listing order changes only on the relisted copy, "
              "first-fit by label only when labels change, output-order first-fit follows the requested answer order.",
        check=["The copies are the same graph or formula.",
               "The requested answer order is clear.",
               "Copies are matched in length."])),
    ("C_E2", dict(name="Single-edit minimal pairs", vertical="C constructive",
        tests="One added edge (colouring) or one flipped literal (SAT) that changes one heuristic's answer but not its "
              "rival's, plus placebo edits and edits that change only the true answer (G-ONLY).",
        check=["The edit is a single edge or literal.",
               "The cell name matches which members' predictions change (see the answer groups).",
               "Prompt and answer format are clear."])),
    ("C_E3", dict(name="Depth stress", vertical="C constructive",
        tests="A graph built from layered NOR circuits, where first-fit's colour for the target depends on a chain of d "
              "layers. CRITICAL swaps flip the target under first-fit; PLACEBO swaps can't. Constant-depth shortcuts "
              "should fail as d grows.",
        check=["The 67-vertex prompt is readable.",
               "The arm's question is unambiguous (listing order, reversed order, or \"what colour does t get?\").",
               "Nothing in the layout gives the circuit away."])),
    ("C_E5", dict(name="Dead ends", vertical="C constructive",
        tests="3-colourable graphs on which first-fit in listing order gets stuck, so a model following it may wrongly say "
              "IMPOSSIBLE. Vertex order and edge order are crossed; a control graph of matched size and hardness doesn't "
              "trap first-fit. SAT and controlled-state variants too.",
        check=["The graph is colourable (the ground truth gives a witness).",
               "IMPOSSIBLE is an allowed answer and the format says so.",
               "The control looks like the stuck graph."])),
])


def short(value, limit=160):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def answer_text(rec):
    a = rec.get("answer")
    if a is not None:
        if isinstance(a, dict):
            return short(" ".join(f"{k}={'T' if v is True else 'F' if v is False else v}" for k, v in a.items()), 140)
        return short(a, 140)
    dist = rec.get("distribution") or {}
    top = sorted(dist.items(), key=lambda kv: -kv[1])[:2]
    return "; ".join(f"P({short(k, 30)})={v:.2f}" for k, v in top) or "—"


def answer_key(rec):
    a = rec.get("answer")
    if a is not None:
        return json.dumps(a, sort_keys=True)
    return "dist:" + json.dumps(rec.get("distribution"), sort_keys=True)


PICKS = {
    "AH_E1": ["SAT/critical/x", "SAT/critical/x-prime", "COL/critical/x-prime", "ENT/null/x", "SAT/B1/x-prime"],
    "AH_E2": ["SAT/base/g=SAT", "SAT/K/g=SAT", "SAT/J/g=SAT", "COL/U/g=impossible", "ENT/E-hi-mis"],
    "AH_E5": ["SAT/T", "SAT/I", "SAT/P", "COL/N", "KNAP/I+R", "ENT/I"],
    "AH_E8": ["early/J/f=0.0", "early/K/f=0.5", "mistake/J", "transplant/J->K"],
    "B4C4_E1": ["M1·CD", "M2·DC·MC", "N1·CD", "U2·DC", "V1·CD·MC"],
    "B4C4_E2": ["A→B·MP·cf", "A→B·AC·cf·instr", "¬A→¬B·MT·mf", "A↔B·DA·cf", "A→¬B·MT·cf"],
    "C_E1": ["COL/c1-NAT", "COL/c4-ANS-RAND", "COL/c6-RELIST", "SAT/c2-RELABEL", "SAT/c5-ANS-FREE"],
    "C_E2": ["COL/FF-vs-DSATUR/BASE", "COL/FF-vs-DSATUR/D(FF|DSATUR)", "SAT/GREEDY-vs-POLARITY/D(POLARITY|GREEDY)",
             "SAT/GREEDY-vs-UC/PLACEBO", "KNAP/RATIO-vs-VALUE/G-ONLY"],
    "C_E3": ["d=2/BASE/U-LIST", "d=2/CRITICAL/U-LIST", "d=4/BASE/I", "d=8/CRITICAL/U-REV", "d=8/PLACEBO/I"],
    "C_E5": ["COL/STUCK/vA/eA", "COL/CONTROL/vA/eA", "SAT/DEAD", "ENT/FAIL/ORDER-A", "STATE/COL/s1"],
}


def pick(items, cells):
    """One item per hand-picked cell (each domain and the main contrasts), taking pair members from the
    same base, set or pair where one is already chosen so the contrast can be read side by side."""
    chosen, used = [], set()
    by_cell = {}
    for it in sorted(items, key=lambda x: (x["set_id"], x["item_id"])):
        by_cell.setdefault(it["cell"], []).append(it)
    for cell in cells:
        cands = by_cell[cell]
        it = next((c for c in cands if {c["set_id"], c.get("pair_id"), c["base_hash"]} & used), cands[0])
        chosen.append(it)
        used |= {it["set_id"], it.get("pair_id"), it["base_hash"]} - {None}
    return chosen


def doc_id(item_id):
    return re.sub(r"[^A-Za-z0-9_\-.~:@+]", "_", item_id)[:190]


def compact(it, slug):
    groups = OrderedDict()
    for label, rec in it["predictions"].items():
        key = answer_key(rec)
        g = groups.setdefault(key, {"answer": answer_text(rec), "members": []})
        g["members"].append(label)
    members = []
    for label, rec in it["predictions"].items():
        hyp = it["hypotheses"].get(label, {})
        members.append({"label": label, "family": rec.get("family", ""),
                        "eval": short(hyp.get("eval_prediction", ""), 260),
                        "cot": short(hyp.get("cot_prediction", ""), 220)})
    against = []
    for outcome, row in list(it["disconfirms"].items())[:4]:
        worst = [(h, round(v, 2)) for h, v in sorted(row.items(), key=lambda kv: -kv[1]) if v >= 1][:5]
        against.append({"outcome": short(outcome, 110), "against": worst})
    params = {k: v for k, v in it["params"].items() if k not in ("frame", "circuit")}
    tokens = it["params"].get("prompt_tokens")
    return {
        "id": doc_id(it["item_id"]), "item_id": it["item_id"], "eval": slug, "cell": it["cell"],
        "set_id": it["set_id"], "pair_id": it.get("pair_id"), "domain": it["domain"], "framing": it["framing"],
        "truth": short(it["ground_truth"], 320), "params": short(params, 360), "tokens": tokens,
        "prompt": it["prompt"] or "", "answer_format": it.get("answer_format") or "",
        "groups": list(groups.values()), "members": members, "against": against,
        "notes": it.get("notes") or "",
    }


def main():
    data = []
    for slug, meta in EVALS.items():
        path = ROOT / f"data/items/dev/{slug}_dev_s1.jsonl"
        items = [json.loads(line) for line in path.open()]
        picked = pick(items, PICKS[slug])
        report = json.loads((ROOT / f"data/items/dev/{slug}_dev_s1.report.json").read_text())
        data.append({"slug": slug, "code": slug.replace("AH", "A/H").replace("B4C4", "B4/C4").replace("_", " "), **meta, "n_dev": len(items),
                     "packet": f"{REPO_BLOB}/review/{slug}.md",
                     "items": [compact(it, slug) for it in picked]})
        print(slug, len(items), [p["cell"] for p in picked], file=sys.stderr)
    ids = [i["id"] for e in data for i in e["items"]]
    assert len(ids) == len(set(ids)), "duplicate doc ids"
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = (HERE / "template.html").read_text().replace("/*__DATA__*/null", blob)
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "review.html")
    out.write_text(html)
    print(f"wrote {out}: {len(html) / 1024:.0f} KB, {len(ids)} items", file=sys.stderr)


if __name__ == "__main__":
    main()
