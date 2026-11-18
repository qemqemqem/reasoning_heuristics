"""B4/C4 E1: the disjunction gadget, position x order x second-premise type x format.

Design (B4/C4 §2.5 E1), per frame:
    P_D = "Either (a is A and a is B), or (b is C and b is D)"
    P  matched-disjunct position 1 | 2 (swap the disjuncts of P_D)
    O  order DC (disjunction first) | CD
    T  second premise M "a is A" (probe a is B, g = NO) | N "a is not A" (probe b is D, g = YES)
       | U "c is E" (probe a is B, g = NO) | V "a is A, or c is E" (probe a is B, g = NO)
    F  YN | MC
A frame is a lexicon draw (from the split's lexicon partition) x theme.

Readings of the doc, where it is ambiguous (also in docs/GENERATORS.md):
- MC is built for T in {M, U, V}. The doc tabulates MC for M cells and the library has MC for
  M and V cells. With the shared option set (a is B / b is D / a is B or (b is C and b is D) /
  a is not B / None), N cells have two incomparable entailed options (b is D, and the
  disjunction), so "the strongest entailed option" is undefined there; N cells are YN only.
  That gives 16 YN + 12 MC = 28 cells per frame.
- MC display order is the canonical order above; the doc's Latin-square rotation is "across
  samples", i.e. a runner concern, so it is not baked into items.
- U and V premises are rendered as in the library ("The cup is green.", "Either the box is
  red, or the cup is green."). The doc's "padded with a neutral clause" is not applied (the
  library does not, and no neutral clause is specified); prompt token counts are recorded
  as a covariate instead, and O/P pairs are exact token-multiset permutations (asserted).

Set = one frame x one T level; every O, P and F variant shares the premise multiset
(`pair_id`), and every member is recomputed on every cell.
"""

from __future__ import annotations

from typing import Any

from reasoning_heuristics import tokens
from reasoning_heuristics.counterfactual import surface
from reasoning_heuristics.generators import b4_common as B
from reasoning_heuristics.generators.common import GenStats, make_item, set_hash
from reasoning_heuristics.hashing import sha
from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.tasks import EntailmentTask, load_task
from reasoning_heuristics.problems.entailment import formula as F
from reasoning_heuristics.seeds import TIERS, base_seed, rng_for
from reasoning_heuristics.validate.truth import truth

VERTICAL, EVAL_ID = "B4/C4", "E1"
LEXICON_PARTITIONED = True
EXPECTED_G = {"M": "NO", "N": "YES", "U": "NO", "V": "NO"}
MC_T = ("M", "U", "V")


def cells(params: dict[str, Any]) -> list[str]:
    out = []
    for T in "MNUV":
        for P in (1, 2):
            for O in ("DC", "CD"):
                out.append(f"{T}{P}·{O}")
                if T in MC_T:
                    out.append(f"{T}{P}·{O}·MC")
    return out


def build_task(frame: B.Frame, T: str, P: int, O: str, fmt: str) -> EntailmentTask:
    L = F.lit
    aA, aB, bC, bD, cE = frame.atom(0, 0), frame.atom(0, 1), frame.atom(1, 2), frame.atom(1, 3), frame.atom(2, 4)
    d1, d2 = F.conj(L(aA), L(aB)), F.conj(L(bC), L(bD))
    pd = F.disj(d1, d2) if P == 1 else F.disj(d2, d1)
    second = {"M": L(aA), "N": L(aA, False), "U": L(cE), "V": F.disj(L(aA), L(cE))}[T]
    premises = (pd, second) if O == "DC" else (second, pd)
    if fmt == "YN":
        return EntailmentTask(premises, L(bD) if T == "N" else L(aB), "YN")
    options = (L(aB), L(bD), F.disj(L(aB), F.conj(L(bC), L(bD))), L(aB, False))
    return EntailmentTask(premises, None, "MC", options)


def generate(tier: str, seed: int, per_cell: int | None = None, themes: list[str] | None = None,
             repeat_prompt: bool = False) -> tuple[list, dict]:
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
        rng = rng_for(bseed, "B4-E1")
        theme = themes[stats.accepted % len(themes)]
        frame = B.draw_frame(rng, split, theme, 3, 5, [(0, 1), (2, 3)])
        if frame is None:
            stats.reject("antonym pair on one subject")
            continue
        frame_items = []
        for T in "MNUV":
            base_task = build_task(frame, T, 1, "DC", "YN")
            pair = sha({"premises": B.premise_multiset(base_task), "T": T, "frame": frame.to_json()})
            set_id = f"{set_hash(bseed, T)}-{T}"
            for fmt in (("YN", "MC") if T in MC_T else ("YN",)):
                for P in (1, 2):
                    for O in ("DC", "CD"):
                        task = build_task(frame, T, P, O, fmt)
                        cell = f"{T}{P}·{O}" + ("·MC" if fmt == "MC" else "")
                        gt = truth(task)
                        prompt = B.render_prompt(task, repeat_prompt=repeat_prompt)
                        frame_items.append(make_item(
                            vertical=VERTICAL, eval_id=EVAL_ID, set_id=set_id, cell=cell, domain="entailment",
                            framing=theme, prompt=prompt, answer_format=B.YN_ANSWER if fmt == "YN" else B.MC_ANSWER,
                            task=task, ground_truth=gt, specs=B.members(fmt, with_conditionals=False),
                            channel=B.channel(fmt), seed=bseed, tier=tier, generator=__name__,
                            base_hash=pair, source_hash=None if (P, O, fmt) == (1, "DC", "YN") else pair,
                            pair_id=pair,
                            params={"T": T, "P": P, "O": O, "F": fmt, "frame": frame.to_json(),
                                    "prompt_tokens": tokens.count(prompt), "tokenizer_proxy": tokens.PROXY_NAME,
                                    "repeat_prompt": repeat_prompt},
                            notes="Disjunction gadget. Every member recomputed on this cell from the structured form; "
                                  "O, P and F variants share the premise multiset (pair_id).",
                            cell_note=f"Cell {cell}: the ground truth is {gt['answer']}.",
                        ))
        problems = [m for sid in {it.set_id for it in frame_items}
                    for m in check_set([it for it in frame_items if it.set_id == sid])]
        if problems:
            stats.reject("set invariant failed: " + problems[0][:60])
            continue
        items += frame_items
        stats.accepted += 1
    return items, stats.to_json()


def check_set(items: list) -> list[str]:
    """Designed invariants of one frame x T set."""
    errs = []
    tasks = {it.cell: load_task(it.instance) for it in items}
    T = items[0].params["T"]
    multisets = {repr(B.premise_multiset(t)) for t in tasks.values()}
    if len(multisets) != 1:
        errs.append("O/P/F variants do not share the premise multiset")
    for it in items:
        if it.ground_truth["answer"] != (EXPECTED_G[T] if it.params["F"] == "YN" else "C"):
            errs.append(f"{it.cell}: ground truth {it.ground_truth['answer']} differs from the design")
        t = tasks[it.cell]
        if it.params["F"] == "YN":
            xor = truth(B.exclusive_or_reading(t))["answer"]
            if xor != it.ground_truth["answer"]:
                errs.append(f"{it.cell}: g changes under an exclusive reading of 'or'")
        else:
            entailed = [o for o in t.options if F.entails(list(t.premises), o)]
            strongest = [o for o in entailed if all(F.entails([o], x) for x in entailed)]
            if len(strongest) != 1:
                errs.append(f"{it.cell}: no unique strongest entailed option")
    yn = {it.cell: it.prompt for it in items if it.params["F"] == "YN"}
    mc = {it.cell: it.prompt for it in items if it.params["F"] == "MC"}
    for group in (yn, mc):
        if group:
            errs += surface.equal_token_multisets(group)
    # Disjunct position (P) must move FIRST on M cells, and categorical-first order must move MATCH-L.
    if T == "M":
        ans = {it.cell: it.predictions for it in items}
        if ans["M1·DC"]["FIRST"]["answer"] == ans["M2·DC"]["FIRST"]["answer"]:
            errs.append("FIRST does not respond to disjunct position")
        if ans["M1·DC"]["MATCH-L"]["answer"] == ans["M1·CD"]["MATCH-L"]["answer"]:
            errs.append("MATCH-L does not respond to order")
        if ans["M1·DC·MC"]["ETR-default"]["answer"] == ans["M1·CD·MC"]["ETR-default"]["answer"]:
            errs.append("ETR-default shows no order effect in MC")
        if ans["M1·DC"]["ETR-default"]["answer"] != ans["M1·CD"]["ETR-default"]["answer"]:
            errs.append("ETR-default shows an order effect in YN")
    return errs
