"""B4/C4 E2: the conditional four-inference profile x order x connective x negation.

Design (B4/C4 §2.5 E2), per frame: inference I in {MP, AC, DA, MT} x order O in {cf
(conditional first), mf (minor premise first)} x form in {A→B, A→¬B, ¬A→B, ¬A→¬B, A↔B}
= 40 cells, plus the instruction factor on the affirmative "if" (8 cells) = 48 cells.
A and B are atoms about two different subjects ("the box is red", "the jar is cold").

Minor premise and probe per inference, with the antecedent A* and consequent B* as stated
in the form: MP A* ⊢ B*; AC B* ⊢ A*; DA ¬A* ⊢ ¬B*; MT ¬B* ⊢ ¬A* (negations of negated
literals are rendered positive).

Readings of the doc (also in docs/GENERATORS.md):
- Note line. Every non-instruction cell carries a neutral note and instruction cells carry
  "'if X, then Y' does not mean 'if Y, then X'." The doc asks for notes within ±1 token;
  the library's neutral note ("consider every statement before you answer.") is 11 proxy
  tokens shorter than the instruction. The default `note_style="matched"` uses a neutral
  note with the instruction's proxy-token count ("read 'statement 1' and 'statement 2'
  carefully, and only then give your answer."); `note_style="library"` reproduces the
  library's wording exactly.
- "Non-causal predicate pairs only (judge prompt)": no judge is run (no model calls). The
  frames use the abstract object/property lexicon and the people/place lexicon, whose
  pairs are about different subjects and have no causal link by construction.
- BICOND-PRAG is the pragmatic variant the instruction factor tests: BICOND without the
  instruction, the stated reading with it.

Set = one frame x one form x one note level (8 cells: I x O); O pairs share the premise
multiset and are token-multiset permutations of each other (asserted).
"""

from __future__ import annotations

from typing import Any

from reasoning_heuristics import tokens
from reasoning_heuristics.counterfactual import surface
from reasoning_heuristics.generators import b4_common as B
from reasoning_heuristics.generators.common import GenStats, make_item, set_hash
from reasoning_heuristics.hashing import sha
from reasoning_heuristics.heuristics.tasks import EntailmentTask, load_task
from reasoning_heuristics.problems.entailment import formula as F
from reasoning_heuristics.seeds import TIERS, base_seed, rng_for
from reasoning_heuristics.validate.truth import truth

VERTICAL, EVAL_ID = "B4/C4", "E2"
LEXICON_PARTITIONED = True
FORMS = ("A→B", "A→¬B", "¬A→B", "¬A→¬B", "A↔B")
INFERENCES = ("MP", "AC", "DA", "MT")
ORDERS = ("cf", "mf")
INSTRUCTION = "'if X, then Y' does not mean 'if Y, then X'."
NEUTRAL = {
    "matched": "read 'statement 1' and 'statement 2' carefully, and only then give your answer.",
    "library": "consider every statement before you answer.",
}
VALID = {"MP": True, "AC": False, "DA": False, "MT": True}


def cells(params: dict[str, Any]) -> list[str]:
    out = [f"{form}·{i}·{o}" for form in FORMS for i in INFERENCES for o in ORDERS]
    return out + [f"A→B·{i}·{o}·instr" for i in INFERENCES for o in ORDERS]


def build_task(frame: B.Frame, form: str, inference: str, order: str) -> EntailmentTask:
    A = F.lit(frame.atom(0, 0), not form.startswith("¬A"))
    Bc = F.lit(frame.atom(1, 1), not form.endswith("¬B"))

    def flip(x):
        return F.lit(x[1], not x[2])

    rule = F.iff(A, Bc) if form == "A↔B" else F.cond(A, Bc)
    minor, probe = {"MP": (A, Bc), "AC": (Bc, A), "DA": (flip(A), flip(Bc)), "MT": (flip(Bc), flip(A))}[inference]
    premises = (rule, minor) if order == "cf" else (minor, rule)
    return EntailmentTask(premises, probe, "YN")


def specs(instruction: bool) -> list:
    return B.members("YN", with_conditionals=True) + [("BICOND-PRAG", "BICOND-PRAG", {"instruction": instruction})]


def generate(tier: str, seed: int, per_cell: int | None = None, themes: list[str] | None = None,
             note_style: str = "matched", repeat_prompt: bool = False) -> tuple[list, dict]:
    per_cell = per_cell or TIERS[tier].default_per_cell
    split = TIERS[tier].split
    themes = themes or list(B.THEMES)
    stats = GenStats()
    items = []
    attempt = 0
    while stats.accepted < per_cell:
        bseed = base_seed(tier, seed, attempt)
        attempt += 1
        stats.attempts += 1
        rng = rng_for(bseed, "B4-E2")
        theme = themes[stats.accepted % len(themes)]
        frame = B.draw_frame(rng, split, theme, 2, 2, [])
        frame_items = []
        for form in FORMS:
            for instr in ((False, True) if form == "A→B" else (False,)):
                note = INSTRUCTION if instr else NEUTRAL[note_style]
                set_id = f"{set_hash(bseed, form, instr)}-{'instr' if instr else 'neutral'}"
                for inference in INFERENCES:
                    pair = sha({"premises": B.premise_multiset(build_task(frame, form, inference, "cf")),
                                "frame": frame.to_json(), "form": form, "inference": inference})
                    for order in ORDERS:
                        task = build_task(frame, form, inference, order)
                        cell = f"{form}·{inference}·{order}" + ("·instr" if instr else "")
                        gt = truth(task)
                        prompt = B.render_prompt(task, note=note, repeat_prompt=repeat_prompt)
                        frame_items.append(make_item(
                            vertical=VERTICAL, eval_id=EVAL_ID, set_id=set_id, cell=cell, domain="entailment",
                            framing=theme, prompt=prompt, answer_format=B.YN_ANSWER, task=task, ground_truth=gt,
                            specs=specs(instr), channel=B.channel("YN"), seed=bseed, tier=tier, generator=__name__,
                            base_hash=pair, source_hash=None if order == "cf" else pair, pair_id=pair,
                            params={"form": form, "inference": inference, "O": order, "instruction": instr,
                                    "note": note, "note_style": note_style, "frame": frame.to_json(),
                                    "prompt_tokens": tokens.count(prompt), "tokenizer_proxy": tokens.PROXY_NAME,
                                    "repeat_prompt": repeat_prompt},
                            notes="Conditional inference profile. Every member recomputed on this cell; the O pair "
                                  "shares the premise multiset (pair_id).",
                            cell_note=f"Cell {cell}: the ground truth is {gt['answer']}.",
                        ))
        problems = [m for sid in {it.set_id for it in frame_items}
                    for m in check_set([it for it in frame_items if it.set_id == sid])]
        if note_style == "matched":
            problems += note_length_check(frame_items)
        if problems:
            stats.reject("set invariant failed: " + problems[0][:60])
            continue
        items += frame_items
        stats.accepted += 1
    return items, stats.to_json()


def note_length_check(items: list) -> list[str]:
    """Instruction and neutral notes within ±1 proxy token (B4/C4 §2.10 E2)."""
    neutral = {it.cell: it.prompt for it in items if it.params["form"] == "A→B" and not it.params["instruction"]}
    instr = {it.cell.replace("·instr", ""): it.prompt for it in items if it.params["instruction"]}
    return surface.token_delta_within(neutral, instr, 1)


def check_set(items: list) -> list[str]:
    errs = []
    form = items[0].params["form"]
    by_cell = {it.cell: it for it in items}
    for it in items:
        want = "YES" if form == "A↔B" or VALID[it.params["inference"]] else "NO"
        if it.ground_truth["answer"] != want:
            errs.append(f"{it.cell}: ground truth {it.ground_truth['answer']} differs from the design ({want})")
    for inference in INFERENCES:
        pair = [it for it in items if it.params["inference"] == inference]
        if len({repr(B.premise_multiset(load_task(it.instance))) for it in pair}) != 1:
            errs.append(f"{inference}: the O pair does not share the premise multiset")
        errs += surface.equal_token_multisets({it.cell: it.prompt for it in pair})
    # h-fixed, g-varying: BICOND endorses AC and DA under 'if' (g = NO) as under 'iff' (g = YES).
    if form == "A→B" and not items[0].params["instruction"]:
        for i in ("AC", "DA"):
            for o in ORDERS:
                if by_cell[f"A→B·{i}·{o}"].predictions["BICOND"]["answer"] != "YES":
                    errs.append(f"BICOND does not endorse {i}·{o}")
        mt = [by_cell[f"A→B·MT·{o}"].predictions["MM-G"]["answer"] for o in ORDERS]
        if mt != ["NO", "YES"]:
            errs.append(f"MM-G lacks the minor-first MT effect: {mt}")
    return errs
