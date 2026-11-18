# Theoretical priors: which heuristics does theory support?

*Written 2026-11-13, before any project data. This page combines three theory notes, each scoring every family in [PAPER_SKELETON.md](../PAPER_SKELETON.md) Table 4 from −2 to +2:*

| Note | Question it asks | Method |
|---|---|---|
| [T1_expressivity.md](T1_expressivity.md) | **Can** a transformer compute this cheaply, in one pass or with ~32k tokens of thinking? | Circuit-complexity and CoT theorems; simulated search costs and dependency depths ([scripts/theory/expressivity/](../../scripts/theory/expressivity/)) |
| [T2_rasp_learnability.md](T2_rasp_learnability.md) | **Would training select it**: is it a short RASP-L program on the accuracy-vs-length frontier? | RASP-L programs run and tested against reference implementations; two-part MDL; sensitivity ([scripts/theory/rasp/](../../scripts/theory/rasp/)) |
| [T3_llm_precedent.md](T3_llm_precedent.md) | **Do LLMs already do it**, by mechanistic or behavioural evidence, and which way does training push? | Literature, citations checked |

The three lenses ask different questions, so they are not summed. T1 is a gate: a member that can't be computed cheaply in a regime isn't available there. Among available members, T2 (would it be learned) and T3 (is it observed) give the support.

**Verdict rule.**

- **Not available:** T1 ≤ −1 in that regime.
- **Strong:** T2 and T3 both ≥ +1.
- **Supported:** one of T2/T3 ≥ +1 and the other ≥ 0 or not scored.
- **Contested:** one ≥ +1 and the other ≤ −1.
- **Weak:** both ≤ 0.
- If both T2 and T3 rate their score low-confidence, the verdict drops one level.

**Regimes.** *Direct* = a single-token answer with thinking off (1P), or a structured answer written out with thinking off (DS) where marked. *Thinking* = best effort, ~32k tokens, mainly below the budget line n\*.

---

## 1. Combined table

Scores are T1 / T2 / T3; "—" = not scored by that lens.

| Family · member | Direct | Verdict | Thinking | Verdict |
|---|---|---|---|---|
| **A1** constant default (`ALWAYS-SAT`, "no") | +2 / +1 / +2 | **Strong** | +2 / −1 / +1 | Contested: all agree it appears as search's default answer at the cap |
| **A2** density cue (`DENSITY`) | +2 / +2 / +1 | **Strong** (random 3-SAT; 0 on puzzle CNF) | +2 / −1 / 0 | Weak |
| **A2** position (`PRIMACY`, `RECENCY`) | +2 / −1 / +2 | Contested | +2 / −1 / +1 | Contested |
| **A3** `TEXTBOOK-TRANSFER` | +1 / — / +2 | Supported | +1 / — / +1 | Supported |
| **B1** `UP-k`, k ≤ 3 | +1 / +2 / +1 | **Strong** | +2 / +1 / 0 | Supported, as a subroutine of search |
| **B1** `PREMISE-SUBSET`, `DROP-CONSTRAINT` | +2 / — / +1 | Supported (low confidence; not yet separable from misreading) | +2 / — / 0 | Weak |
| **B3** `LP-ROUND` | −2 / −2 / 0 | Not available | −1 / −1 / 0 | Not available |
| **B4** surface restriction (`FIRST`, `BICOND`, `MATCH`) | +2 / −1 / +1 | Contested | +2 / −1 / 0 | Weak |
| **B4/C4** `MM`, `ETR` | +1 / −1 / +1 | Contested (≤ ~5 premises in one pass) | +2 / −1 / 0 | Weak |
| **B4** `ADD-CONSTRAINT` (phantom constraint) | +2 / — / +1 | Supported (low) | +2 / — / +1 | Supported: structured vs random is unknown |
| **B5** `EXPECTED-COST` | +1 / 0 / 0 | Weak | +1 / 0 / 0 | Weak |
| **C0** `POLARITY` (one-shot scoring) | +2 / +2 / +1 | **Strong** | +2 / 0 / +1 | Supported, as the value ordering inside search |
| **C1** greedy, single-token query | −1 to −2 / 0 / −1 | Not available | | |
| **C1** greedy, answer written out (DS) | +2 / 0 / +2 | Supported | +2 / +1 / +1 | **Strong**, as the first candidate inside search |
| **C2** `DSATUR` (adaptive order) | −2 / −2 / 0 | Not available | +2 / +1 / +1 | Supported (both low confidence) |
| **C2** `UC` as a decision procedure | −2 / −2 / 0 | Not available | +2 / −1 / +1 | Contested |
| **C3** random-order greedy | 0 / −1 / −1 | Weak | +1 / 0 / −1 | Weak |
| **C4** `ONLINE-STATE(k)` | +1 / −1 / +1 | Contested | +2 / 0 / 0 | Weak |
| **D** truncated search (`DPLL-b`) | −2 / −2 / −2 | Not available | +2 / +2 / +2 (family), +1 (systematic `DPLL-b`) | **Strong** |
| **D** `BEAM-w`, `BACKDOOR-k` | −2 / — / −1 | Not available | 0 to +1 / — / 0 | Weak |
| **E** `BP-t`, `WP-t`, `LOCAL-t` | +1 / −1 / +1 | Contested | −1 explicit, +2 implicit / −1 / 0 | Not available written out; Weak implicitly |
| **F** `MIN-CONFLICTS`, `WALK-k`, `2OPT-k` | −2 / −2 / −1 | Not available | +1 / +1 (`MIN-CONFLICTS`), 0 (`WALK`) / +1 | Supported (both low confidence) |
| **G** `DP-EXACT` | −1 / — / −1 | Not available | +1 / — / +1 | Supported (small knapsacks only) |
| **G** `IGNORE-CROSSLINKS` | +1 / 0 / 0 | Weak | +2 / 0 / +1 | Weak (both lenses low confidence) |
| **H** `RANDOM` | +2 / — / +1 | Supported (low) | +2 / — / 0 | Weak |
| **H** `SAMPLE-m` / `PROBE-m` | +1 / −1 SAT, +1 ENT / 0 | Weak on SAT; Supported on entailment | +2 / 0 / +1 | Supported, as "check a few cases" |
| **I** strategy selection | +2 / 0 / +1 | Supported | +2 / 0 / +1 | Supported |
| *Nuisance* `NOISY-EXACT` | — / −2 / +1 | Contested | — / +2 / +2 | **Strong** |
| *Nuisance* `PERCEPTION-NOISE` | — / — / +1 | Supported | — / — / +2 | Supported |

---

## 2. What the table says

**1. The regimes split cleanly, and all three lenses agree on the split.**

- *Direct answers* are best explained by short, shallow programs: constant defaults, the density cue, a few rounds of unit propagation, and one-shot scoring. Search, repair and adaptive greedy aren't available in one pass.
- *Thinking* flips the ranking toward truncated exact search (D). T1: it fits the budget below n\*. T2: its per-step program is about as long as greedy's and far more accurate on training-size items, so two-part MDL prefers it. T3: R1-style traces build and navigate a search tree, and output length tracks solver conflicts.

**2. In thinking models, theory predicts one composite procedure, not rival families.** Search (D) opens with a greedy candidate (C1/C2), orders values by a one-shot score (C0), propagates units inside (B1), answers with a default when it hits the cap (A1), and makes slips and misreadings (nuisance). The mixture model treats families as rivals. So for thinking runs the zoo needs **composite members** such as `DPLL-b(order = DSATUR | listing, value = POLARITY, default = UNSAT)`. Their parameters, not a family label, are what the evals should identify. [SCOPE.md](../SCOPE.md) already plans parameterised members (`SEARCH(b, …)`, `PRIORITY(order, score, rule)`).

**3. Restriction (B4, including ETR and mental models) is the most informative contested family.**

- It is computable (T1 +2) and observed in non-thinking models (T3 +1).
- Simplicity gives it no advantage: `FIRST∘UP-k` and `BICOND∘UP-k` are exactly as long as `UP-k` and less accurate under validity labels (T2).
- So if B4 carries weight, training data put it there, because human text endorses those readings. That makes three joint predictions:
  - B4 weight is higher in natural-language framings than in formal ones.
  - It doesn't grow with instance size at fixed framing.
  - It falls with thinking, with interpretive members (`BICOND`, `CLOSED-WORLD`) falling least.
- This is the cleanest test of H6, and the ETR thread of the project lives here.

**4. Position effects come from the architecture, not a learned program.** T2 finds `PRIMACY` off the frontier, yet T3's evidence for position bias is among the strongest in the table. The resolution is the causal mask (Wu et al. 2025): position effects are a property of how attention reaches the input, not a heuristic the model learned. Prediction (T3 P3/P5): under thinking they shrink as accuracy effects but survive as which correct solution is returned, and they grow with trace length.

**5. Message passing (E) is contested in one pass and unlikely as written reasoning.** It fits inside a pass, and attention resembles it (T1), but `BP-2` is 81 primitives and no more accurate than the 9-primitive `POLARITY` on training-like items (T2). Written out, one round costs 9–22k tokens at n = 40 (T1). The E vertical's second-order and calibration items (E2, E5) decide it.

**6. The biggest threat is to the premise, not to any family.**

- **Compute forces heuristics only on large SAT.** T1's simulations put exact search's 32k budget line at n\* ≈ 30–50 for unsatisfiable 3-SAT and ≈ 70–80 for satisfiable 3-SAT. Our colouring (≤ 40 nodes) and entailment (3–12 premises) items sit below the line for any sensible exact method.
- **Misreading may outweigh every heuristic.** T3 finds the best-documented reasoning-model errors on constraint problems are misreading the instance and slips during long execution. Its prediction P10 is that this noise mass exceeds any single heuristic family's above n\*.
- What to do about it:
  - Make SAT sizes straddle each model's n\*. The budget line itself is a measurement: its value fingerprints the branching rule (T1 P6), and it rises with the log of the budget (T1 P7).
  - Treat colouring and entailment errors at best effort as *chosen* shortcuts, a different and still interesting claim. Say so in the paper's §3 argument.
  - Make the nuisance terms first-class rows with sharp signatures. T1 §3.6: `NOISY-EXACT` errors grow with the work done, not with work relative to budget. T3 P9: phantom edges are uniform (noise) or concentrated on co-mentioned pairs (B4).

**7. Two findings worth a paper section on their own.**

- **Out-of-distribution shadows (T2).** With a fixed atom vocabulary, the MDL-optimal direct entailment program is a 3-layer parallel truth table. It is exact on training-size items and becomes a fixed-probe sampler, 56% commission, on larger ones. A "heuristic" seen on hard items can be the OOD behaviour of a program that was exact in training. Toy-model test: Table 16.
- **Trace style is predicted (T2 P7).** Terse greedy with state isn't RASP-L. Verbose "restate the neighbours' colours, then decide" is a strict 3-layer step. So traces should be copy-then-evaluate, and their token counts should scale with Σdeg or with m per decision.

---

## 3. Where the lenses disagree

| Topic | Disagreement | Resolution or test |
|---|---|---|
| Position cues | Observed (T3 +2), off the frontier (T2 −1) | Architectural bias, not a program (§2.4). C E1 fingerprints; A_H E4 × budget |
| B4 restriction | Observed in direct mode (T3), no simplicity advantage (T2) | Data inheritance (§2.3). B4 E1 format arm; B4 E2 |
| Message passing | Cheap in a pass (T1), not selected (T2), analogy only (T3) | E E2, E5: BP-1 vs `POLARITY` on 2-lift and second-order items |
| Constant default under thinking | T2: only as search's default at the cap. T3: "too complex, so UNSAT" answers | Same thing seen from two sides. T3 P1 predicts the default flips direction with mode: SAT-biased direct, UNSAT-biased thinking |
| Does effort track hardness? | ZebraLogic and SMTrap say yes; Verma 2026 says no once length is controlled (T3 §5) | T3 P2 at matched length; a null shifts weight from D to `NOISY-EXACT` |
| Systematic vs wandering search | T2 favours systematic `DPLL-b`; T3 finds reasoning models "wanderers", stopping early | Fitted b well below the cap (T3 P16); strategy-switch counts in wrong answers |

---

## 4. Pre-registered predictions (selected)

Full lists: T1 §4 (P1–P14), T2 §6 (P1–P10), T3 §4 (P1–P16). These are the ones where the lenses converge or where a result would most change the paper.

| # | Prediction | Source | Eval |
|---|---|---|---|
| 1 | Direct (1P) weight concentrates on A, C0, B1 (k ≤ 3); C2, D (b > 0) and F (k > 0) each get π ≲ 0.05 | T1 P1, T2 P1–P2 | A_H E1–E2; B1 E1; C E3 |
| 2 | Thinking below n\*: truncated exact search plus noise, not C1 or F; trap-pair failures rise only above n\* | T2 P6, T3 P4 | D_F E1, E4; C E5 |
| 3 | n\* fingerprints the branching rule: ≈ 22–44 in listing order, ≈ 42–80 most-constrained-first; each ×4 of budget adds ≈ 11–31 variables | T1 P6–P7 | D_F E1 |
| 4 | The default flips with mode: SAT-biased direct, UNSAT-biased thinking above n\* | T3 P1 | D_F E1, E5; C E5; A_H E1–E2 |
| 5 | B4 weight follows framing, not size, and falls with thinking; `BICOND`/`CLOSED-WORLD` fall least | T2 P4, T3 P7, T1 P9 | B4 E1, E2, E5 |
| 6 | Position effects survive thinking as solution fingerprints and grow with trace length | T3 P3, P5 | A_H E4; C E1 |
| 7 | One-pass reach orders by global-attention depth, not capability: gpt-oss-120b below Qwen3-14B on long-range items | T1 P2–P3, T2 P3 | B1 E1; E E1; C E3 |
| 8 | Traces are copy-then-evaluate; tokens scale with Σdeg or m per decision | T2 P7 | Trace codes in C, D_F |
| 9 | Nuisance mass ≥ the largest heuristic family above n\* | T3 P10 | All mixture fits |
| 10 | Phantom colouring edges concentrate on co-mentioned pairs | T3 P9 | B4 E6a; D_F E6 |

**Results that would embarrass the theory as a whole:** thinking-mode errors below n\* that look greedy (C1) on items where search is exact within budget (T2); one-pass weight on an off-frontier member exceeding the frontier member's at equal accuracy (T2); B4 commission growing with size at fixed framing (T2 P4).

---

## 5. Changes this implies for the design (proposed, not yet made)

1. **Composite members for thinking runs:** search with order, value and default parameters (§2.2). Affects every vertical's member list and the mixture model in PAPER_SKELETON §6.
2. **Re-centre SAT sizes on each model's n\*** and treat colouring and entailment at best effort as the "chosen shortcut" regime. Affects SCOPE §5 (size calibration) and PAPER_SKELETON §3.
3. **Extend depth ranges to about 12–16** in C E3 gadgets and the B1/E radius ladders, or Qwen3-32B's one-pass ceiling is censored (T1 P2).
4. **Two cheap arms:** prompt given twice (T1 P4; B1 E3, E E1); adjacency lists vs shuffled edge lists, to test gpt-oss's 128-token sliding windows (T1 P3).
5. **Fill PAPER_SKELETON Table 15** from T2 §8, and freeze it before the first run.
6. **Literature fix (done):** slice A's citation of Heyman & Zylberberg 2025a is marked withdrawn. Its authors report the correlation is "not causally significant" because it tracked edge count (arXiv 2505.12151 v3, §1 and App. A.1).
