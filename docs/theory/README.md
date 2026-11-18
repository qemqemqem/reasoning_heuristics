# Theoretical priors: which heuristics does theory support?

*Written 2026-11-13, before any project data. This page combines three theory notes, each scoring every family in [PAPER_SKELETON.md](../PAPER_SKELETON.md) Table 4 from −2 to +2:*

| Note | Question it asks | Method |
|---|---|---|
| [T1_expressivity.md](T1_expressivity.md) | **Can** a transformer compute this cheaply, in one pass or with ~32k tokens of thinking? | Circuit-complexity and CoT theorems; simulated search costs and dependency depths ([scripts/theory/expressivity/](../../scripts/theory/expressivity/)) |
| [T2_rasp_learnability.md](T2_rasp_learnability.md) | **Would training select it**: is it a short RASP-L program on the accuracy-vs-length frontier? | RASP-L programs run and tested against reference implementations; two-part MDL; sensitivity ([scripts/theory/rasp/](../../scripts/theory/rasp/)) |
| [T3_llm_precedent.md](T3_llm_precedent.md) | **Do LLMs already do it**, by mechanistic or behavioural evidence, and which way does training push? | Literature, citations checked |

The three lenses ask different questions, so they are not summed. T1 is a gate: a member that can't be computed cheaply in a regime isn't available there. Among available members, T2 (would it be learned) and T3 (is it observed) give the support.

## Corrections (2026-11-17, made before any LLM data was analysed)

A reproducibility audit reran every theory script and found the mismatches below. The priors were corrected on 2026-11-17, before any model output was analysed (smoke runs existed that day but nobody had looked at them). **No verdict in the §1 table or in PAPER_SKELETON Table 4a changes**: every correction either leaves the evidence behind a score unchanged or strengthens it, and the verdict rule was re-applied row by row. The two scores resting on the most fragile evidence are `PROBE-m` on entailment (T2 +1 holds only under linear MDL; the capacity reading puts `PROBE-16` at N = 10⁸) and D in thinking (T2's per-step lengths are estimates); both keep their score.

**Code and results**

- `scripts/theory/rasp/frontier.py`: default `--n` is now 600, which is what the committed `results.json` and PNGs were made with (the default was 400, so the documented command did not reproduce them).
- `scripts/theory/rasp/programs_ent.py`: `up()` built the BICOND lookups (`iff`, two extra lookups per round, wider maps) even when `bicond=False`. Plain `UP-k` is now 48 / 81 / 122 primitives (was 54 / 93 / 141); behaviour is unchanged (0 differences on 300 random items × k × variant). `BICOND∘UP-k` stays 54 / 93 / 141, so it is 12.5% / 14.8% / 15.6% longer than `UP-k`. `FIRST∘UP-k` equals `UP-k` in length only under the table-swap convention. The B4 conclusion (no simplicity advantage) survives, more strongly for `BICOND`; the label-mixture crossovers (q ≈ 0.5 for `FIRST`, 0.6–0.8 for `BICOND`) did not move.
- `scripts/theory/rasp/programs_sat.py`: `up_causal(k)` did k − 1 propagation rounds, so `UP-1c` could never find a conflict and was identical to `ALWAYS-SAT`. It now seeds unit clauses and then runs k rounds, as T1 and this README define `UP-k` (the old `UP-k` is the new `UP-(k−1)`). Puzzle-CNF accuracy at k = 1 / 2 / 3 is 0.865 / 0.893 / 0.908 (was 0.718 / 0.865 / 0.893); lengths 37 / 57 / 77 (was 31 / 51 / 71). `UP-1c` joins the frontier, the MDL winner at N ≈ 3·10³ becomes `UP-1c`, and the capacity path (β = 2) for entailment reaches `UP-1` at N = 10⁴ instead of 10⁵.
- `scripts/theory/rasp/results.json`, `ood.json`, `docs/theory/T2_frontier.png`: regenerated. `T2_perstep.png`, all entailment and colouring accuracies, the thinking table and `PROBE-16` (1.000 in distribution, 0.61 and 56% commission out) are unchanged.
- `pyproject.toml`: optional extra `theory = ["matplotlib", "tiktoken"]`.

**T1 (`T1_expressivity.md`)**

- Added the exact command, output and measured runtime for every script.
- SAT-side n\*: ≈ 70–80 holds only for Jeroslow–Wang (JW) branching; listing order gives ≈ 40. The SAT/UNSAT gap is about +10 for listing order, +20–30 for JW.
- Budget elasticity: ×4 of budget adds +7 to +14 variables under listing order (not "about +12", not "+11 to +31") and +16 to +31 under JW. Also in P7.
- Sample sizes: UNSAT cells hold 9–21 formulas, not "30–40".
- JW is described as a MOMS-like global score, not "most-constrained-first"; P6 and P7 reworded.
- Colouring and entailment are "below the line" only for DSATUR-ordered search and truth tables up to ≈ 9 atoms, with the listing-order, random-graph and 20-atom caveats stated in the summary.

**T2 (`T2_rasp_learnability.md`)**

- Added the command, runtime and the `--n 600` note; stated that per-step lengths for `UC`, `DPLL-b`, `WALK`, `DSATUR`, `MIN-CONFLICTS`, `NN` are estimates.
- Every `UP-k` number (SAT lengths, accuracies, sensitivities, frontier, MDL and capacity paths, Table 15, the P2 order effect) updated to the corrected programs.
- "`FIRST`/`BICOND` +0 primitives / identical length" replaced as above.
- `DPLL-b` "1.00 / exact at n ≤ 20" corrected to 0.975–1.0 at n = 20 (40 items per cell); the n\* ≈ 30 agreement with T1 is noted as not independent (different token-cost models); `WALK` is dominated only at n = 20.
- "Strict RASP-L" for the verbose first-fit step qualified by the `nary_map` convention; the terse-step claim restated as "no program found, counting argument, not a proof".

**This README and `docs/PAPER_SKELETON.md` (§3 budget lines, Table 3a, §5.2, §10 summary, Table 15)**

- §2.1: "all three lenses agree" softened; T3's +1 for systematic `DPLL-b`, T2's own caveat on the thinking column, and the open status of "output length tracks conflicts" stated.
- §2.3: B4 length claim updated. §2.5: the BP comparison scoped to the causal int8 program. §2.6: "heuristics only on large SAT" replaced by T1's list (SAT, TSP, large knapsack) with the colouring and entailment conditions. §2.7: the truth-table finding stated as conditional on linear MDL, a ≤ 4-atom vocabulary and an untested toy model; the terse/verbose RASP-L claim qualified.
- §4 #3, Table 3a and the n\* paragraph: SAT n\* and elasticity ranges as in T1.

---

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

**1. The regimes split, and the lenses mostly agree on the split.**

- *Direct answers* are best explained by short, shallow programs: constant defaults, the density cue, a few rounds of unit propagation, and one-shot scoring. Search, repair and adaptive greedy aren't available in one pass.
- *Thinking* flips the ranking toward truncated exact search (D). T1: it fits the budget below n\*. T2: its per-step program is estimated (not measured) to be about as long as greedy's, and it is more accurate on training-size items (`DPLL-b` 0.975–1.0 vs `WALK` 0.875 at n = 20), so two-part MDL prefers it; T2 itself calls the TH column weaker evidence, since one generic interpreter would make per-step length irrelevant (T2 §5.3). T3: R1-style traces build and navigate a search tree (family score +2), but T3 scores systematic `DPLL-b` only +1 (models look like "wanderers"), and whether output length tracks solver conflicts is an open prediction (T3 P2: ZebraLogic and SMTrap say yes, Verma 2026 says no once length is controlled).

**2. In thinking models, theory predicts one composite procedure, not rival families.** Search (D) opens with a greedy candidate (C1/C2), orders values by a one-shot score (C0), propagates units inside (B1), answers with a default when it hits the cap (A1), and makes slips and misreadings (nuisance). The mixture model treats families as rivals. So for thinking runs the zoo needs **composite members** such as `DPLL-b(order = DSATUR | listing, value = POLARITY, default = UNSAT)`. Their parameters, not a family label, are what the evals should identify. [SCOPE.md](../SCOPE.md) already plans parameterised members (`SEARCH(b, …)`, `PRIORITY(order, score, rule)`).

**3. Restriction (B4, including ETR and mental models) is the most informative contested family.**

- It is computable (T1 +2) and observed in non-thinking models (T3 +1).
- Simplicity gives it no advantage: `FIRST∘UP-k` is the same length as `UP-k` (only under the convention that a table swap costs nothing), `BICOND∘UP-k` is 12–16% longer, and both are less accurate under validity labels (T2).
- So if B4 carries weight, training data put it there, because human text endorses those readings. That makes three joint predictions:
  - B4 weight is higher in natural-language framings than in formal ones.
  - It doesn't grow with instance size at fixed framing.
  - It falls with thinking, with interpretive members (`BICOND`, `CLOSED-WORLD`) falling least.
- This is the cleanest test of H6, and the ETR thread of the project lives here.

**4. Position effects come from the architecture, not a learned program.** T2 finds `PRIMACY` off the frontier, yet T3's evidence for position bias is among the strongest in the table. The resolution is the causal mask (Wu et al. 2025): position effects are a property of how attention reaches the input, not a heuristic the model learned. Prediction (T3 P3/P5): under thinking they shrink as accuracy effects but survive as which correct solution is returned, and they grow with trace length.

**5. Message passing (E) is contested in one pass and unlikely as written reasoning.** It fits inside a pass, and attention resembles it (T1), but causal int8 `BP-2` is 81 primitives and no more accurate than the 9-primitive `POLARITY` on training-like items (0.958 vs 0.960; T2). Non-causal float BP is more accurate (BP-2 0.978, BP-5 0.985), and T2's BP program is a hand-written upper bound on length, so this scores the causal int8 program, not message passing in general. Written out, one round costs 9–22k tokens at n = 40 (T1). The E vertical's second-order and calibration items (E2, E5) decide it.

**6. The biggest threat is to the premise, not to any family.**

- **Compute forces heuristics on large SAT, TSP and large-capacity knapsack; colouring and entailment are below the line only for a well-ordered exact method.** T1's simulations put exact search's 32k budget line at n\* ≈ 30–50 for unsatisfiable 3-SAT, and for satisfiable 3-SAT at ≈ 40 with listing-order branching and ≈ 70–80 with Jeroslow–Wang branching (a MOMS-like global score; the only global score simulated). Our colouring items (≤ 40 nodes) sit below the line for DSATUR-ordered search, but listing-order search crosses at n ≈ 20–25, and the random graphs simulated may be easier than the filtered project items (T1 §3.3, §5). Entailment (3–12 premises) is below the line for truth tables up to about 9 atoms; the 20-atom E1L items are not. TSP (10–14 cities) and large-capacity knapsack are above it (T1 §3.3).
- **Misreading may outweigh every heuristic.** T3 finds the best-documented reasoning-model errors on constraint problems are misreading the instance and slips during long execution. Its prediction P10 is that this noise mass exceeds any single heuristic family's above n\*.
- What to do about it:
  - Make SAT sizes straddle each model's n\*. The budget line itself is a measurement: its value fingerprints the branching rule (T1 P6), and it rises with the log of the budget (T1 P7).
  - Treat colouring and entailment errors at best effort as *chosen* shortcuts, a different and still interesting claim. Say so in the paper's §3 argument.
  - Make the nuisance terms first-class rows with sharp signatures. T1 §3.6: `NOISY-EXACT` errors grow with the work done, not with work relative to budget. T3 P9: phantom edges are uniform (noise) or concentrated on co-mentioned pairs (B4).

**7. Two findings worth a paper section on their own.**

- **Out-of-distribution shadows (T2).** With a fixed atom vocabulary (≤ 4 atoms, so 16 probes cover every assignment by construction), the MDL-optimal direct entailment program under *linear* two-part MDL at N ≳ 10⁴ is a 3-layer parallel truth table. It is exact on training-size items and becomes a fixed-probe sampler, 56% commission, on larger ones. This is conditional: T2's capacity reading (β = 2) delays `PROBE-16` to N = 10⁸, and T2 notes that linear MDL makes length nearly irrelevant at LLM scale. A "heuristic" seen on hard items *can* be the OOD behaviour of a program that was exact in training; whether LLMs do this is untested until the toy-model test (Table 16) runs.
- **Trace style is predicted (T2 P7).** We found no int8 RASP-L program for a terse greedy step with state (T2 §3.3 gives a counting argument, not a proof). Verbose "restate the neighbours' colours, then decide" is a 3-layer step under the n-ary-map counting convention (an 8-input arbitrary map counted as 7 binary maps). So traces should be copy-then-evaluate, and their token counts should scale with Σdeg or with m per decision.

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
| 3 | n\* fingerprints the branching rule: ≈ 22–44 in listing order, ≈ 42–80 with Jeroslow–Wang (MOMS-like) branching; each ×4 of budget adds ≈ 7–14 variables (listing order) or 16–31 (JW) | T1 P6–P7 | D_F E1 |
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
