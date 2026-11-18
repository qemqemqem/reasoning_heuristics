# D/F example question library

*Companion to [D_F_search.md](D_F_search.md). Concrete counterfactual sets for every eval, built so that a generator can produce thousands of similar items (generator specs: D_F_search.md §2.9). Machine-readable copy: [`data/examples/D_F_search.jsonl`](../../data/examples/D_F_search.jsonl), one object per item.*

## How to read this

- **Sizes are dev-scale** (n = 12–38 variables) so the prompts stay readable. The study centres sizes on each model's budget line *n\** (D_F_search.md §2.7).
- **Everything below was computed, not worked out by hand.** Throwaway scripts (kept outside the repo):
  - brute-force enumeration (n ≤ 18) or z3 with blocking clauses for every ground truth and solution count;
  - the reference implementations of §1.3 for every member's prediction;
  - Monte Carlo for the stochastic members (100–300 runs each).
- **Verification caught several things hand-reasoning got wrong.** These changed the design in D_F_search.md:
  - In pure 3-CNF, UP and `FLP-1` are idle from the empty assignment: one assignment never creates a unit clause. So every weak UP-backdoor has size ≥ 2.
  - At α ≈ 4.26, planting a backdoor larger than 2 fails, because the random fill always creates a natural size-2 one. E3 therefore selects *k\** from natural formulas.
  - `BEAM-1` is not `C-UC`: it propagates both values and keeps the better one.
  - Putting the backdoor variables first in the text can make DPLL-MENTION *slower* (E3.3/E3.4: 92 vs 10 nodes). Presentation effects are computed per item, never assumed.
  - Single wrong answers from different sources can be identical (E6): WALK's modal failure equals C-UC/CONT's output on that item.
- **Theory names.**
  - `DPLL-b[H,V,CHR]` is DPLL with branching order *H*, value rule *V*, chronological backtracking, and budget *b* nodes. It needs *N* nodes and *W* clause visits to finish.
  - Δ = its default when *b < N*.
  - LM0 = a WalkSAT local minimum: no violated clause has a break-0 variable.
  - EXACT = "the model solves it exactly".
- **Readout is graded.** Heuristics may be partly used, so results are mixture weights π_h with intervals, lift, and log-likelihood gains (D_F_search.md §2.5), not used/not-used verdicts.
- **Every item carries a hypothesis block:** for each theory, (a) its *output* on the item, (b) the *eval result* as a weight statement (what moves π_h, the power to detect it, or the bound when the effect is null), and (c) its *chain-of-thought* signature.
- **Every item carries outcome likelihoods.** For each theory, a distribution over the item's outcome categories, with a 5% slip floor (JSONL `outcome_likelihoods`). The graded `disconfirms` field lists, for each outcome, the best-fitting theories and the theories whose likelihood ratio against the best is ≤ 0.2.
- **Every set carries two tables:** a direction table (which set-level outcomes move weight toward and away from which theories), and a computed likelihood-ratio table (modal-pattern log10 LRs). A set also says which competitor it cannot separate, and which set does. The coverage matrix across sets is D_F_search.md §2.10.

## Contents

- [E1: Budget line: matched SAT/UNSAT pair (+ themed rendering)](#e1) (4 items)
- [E2: D/F quadrants at fixed n and α](#e2) (4 items)
- [E3: Backdoor size × presentation salience](#e3) (6 items)
- [E4: Trap pairs: backtracking necessity](#e4) (8 items)
- [E5: Certificate pairs](#e5) (4 items)
- [E6: Violation profiles (answer library on the E2 'W low × F high' item, plus verification probes)](#e6) (2 items)
- [E7-SAT: Seeded candidates (SAT)](#e7-sat) (6 items)
- [E7-TSP: Seeded candidates (TSP, courier framing)](#e7-tsp) (4 items)
- [E8: Truncation and state corruption](#e8) (2 items)

**40 items in total.**

---

## E1

### Budget line: matched SAT/UNSAT pair (+ themed rendering)

| Item | Cell | Ground truth | Varied |
|------|------|--------------|--------|
| E1.1 | n=12 (dev level), SAT member, bare | SAT (2 solutions) | one literal sign (clause C32, position 1) decides SAT vs UNSAT |
| E1.2 | n=12 (dev level), UNSAT member, bare | UNSAT | one literal sign (clause C32, position 1) decides SAT vs UNSAT |
| E1.3 | n=12 (dev level), SAT member, theme: product configuration | SAT (2 solutions) | one literal sign (clause C32, position 1) decides SAT vs UNSAT |
| E1.4 | n=12 (dev level), UNSAT member, theme: product configuration | UNSAT | one literal sign (clause C32, position 1) decides SAT vs UNSAT |

**Direction table** (how each set-level outcome moves weight; the sizes are in the likelihood-ratio table below and in each item's hypothesis block):

| Observed outcome (set level) | Moves weight toward | Moves weight away from |
|------------------------------|---------------------|------------------------|
| Both members right at BE, and accuracy over the sweep falls only where W·τ_W exceeds the budget, with the threshold moving 2k→8k by the predicted Δn* | DPLL-b (β ≈ 1) | NOISY-EXACT (β = 0), C (flat in budget), A (ADR = 0), RANDOM, EXACT (if n*_obs is inside the sweep) |
| Errors above n* mostly in completed runs, with false VERIFY; same accuracy at 8k and 32k | NOISY-EXACT | DPLL-b, WALK-k (both predict exhausted-type errors) |
| UNSAT members answered UNSAT without a complete case tree, at a rate that does not depend on W_unsat | WALK-k / MIN-CONFLICTS with UNSAT default, or a DPLL-b default | EXACT, NOISY-EXACT; DPLL-b only if the certified rate also fails to fall with W_unsat |
| Identical answers on both twins (ADR ≈ 0) | A cues (ALWAYS-SAT, DENSITY), POLARITY | every search theory |
| Themed accuracy below bare, with n* shifted by the ratio of tokens per clause | any procedure applied to the structure (D, F, C) | TEXTBOOK-TRANSFER-type retrieval, if themed accuracy collapses beyond the token-cost shift |

**Likelihood-ratio table** (computed). Each row asks: if one response per item (E1.1, E1.2) matched theory *h*'s most likely outcome, how much less likely is that pattern under each competitor? Entries are log10 LR(competitor : h), with a 5% slip floor on every theory, so −1.0 means the pattern pushes that competitor's weight down 10× relative to *h*. A cell of N independent responses multiplies these by about N. The readout is the mixture posterior over π, not a verdict (D_F_search.md §2.5).

| If responses match the modal pattern of h = | Tied with h (0.0) | Weakly disfavoured (−1 < log10 LR < 0) | Pushed down ≥ 10× (log10 LR ≤ −1) |
|---------------------------------------------|-------------------|----------------------------------------|-----------------------------------|
| EXACT | DPLL-b (b >= N), PERCEPTION-NOISE | NOISY-EXACT (-0.1) | DPLL-b[MOMS, b=6, Δ=UNSAT] (-1.8), BEAM-2 (-1.8), BACKDOOR[k=2,OCC] (-1.8), WALK-k (k=60) (-1.8), MIN-CONFLICTS (k=60) (-2.2), C-UC/STOP (-1.8), C-UC/CONT (-1.8), C-GREEDY (-3.6), POLARITY / ALWAYS-SAT (-3.6), B1 (UP-k, FLP-1) (-3.6), RANDOM (-3.6) |
| DPLL-b (b >= N) | EXACT, PERCEPTION-NOISE | NOISY-EXACT (-0.1) | DPLL-b[MOMS, b=6, Δ=UNSAT] (-1.8), BEAM-2 (-1.8), BACKDOOR[k=2,OCC] (-1.8), WALK-k (k=60) (-1.8), MIN-CONFLICTS (k=60) (-2.2), C-UC/STOP (-1.8), C-UC/CONT (-1.8), C-GREEDY (-3.6), POLARITY / ALWAYS-SAT (-3.6), B1 (UP-k, FLP-1) (-3.6), RANDOM (-3.6) |
| DPLL-b[MOMS, b=6, Δ=UNSAT] | BEAM-2, BACKDOOR[k=2,OCC], C-UC/STOP | WALK-k (k=60) (-0.4), MIN-CONFLICTS (k=60) (-0.7) | EXACT (-1.8), DPLL-b (b >= N) (-1.8), C-UC/CONT (-1.8), C-GREEDY (-3.6), POLARITY / ALWAYS-SAT (-3.6), B1 (UP-k, FLP-1) (-1.9), NOISY-EXACT (-1.8), PERCEPTION-NOISE (-1.8), RANDOM (-3.6) |
| BEAM-2 | DPLL-b[MOMS, b=6, Δ=UNSAT], BACKDOOR[k=2,OCC], C-UC/STOP | WALK-k (k=60) (-0.4), MIN-CONFLICTS (k=60) (-0.7) | EXACT (-1.8), DPLL-b (b >= N) (-1.8), C-UC/CONT (-1.8), C-GREEDY (-3.6), POLARITY / ALWAYS-SAT (-3.6), B1 (UP-k, FLP-1) (-1.9), NOISY-EXACT (-1.8), PERCEPTION-NOISE (-1.8), RANDOM (-3.6) |
| BACKDOOR[k=2,OCC] | DPLL-b[MOMS, b=6, Δ=UNSAT], BEAM-2, C-UC/STOP | WALK-k (k=60) (-0.4), MIN-CONFLICTS (k=60) (-0.7) | EXACT (-1.8), DPLL-b (b >= N) (-1.8), C-UC/CONT (-1.8), C-GREEDY (-3.6), POLARITY / ALWAYS-SAT (-3.6), B1 (UP-k, FLP-1) (-1.9), NOISY-EXACT (-1.8), PERCEPTION-NOISE (-1.8), RANDOM (-3.6) |
| WALK-k (k=60) | — | MIN-CONFLICTS (k=60) (-0.3) | EXACT (-1.4), DPLL-b (b >= N) (-1.4), C-UC/CONT (-1.4), C-GREEDY (-3.3), POLARITY / ALWAYS-SAT (-3.3), B1 (UP-k, FLP-1) (-1.5), NOISY-EXACT (-1.4), PERCEPTION-NOISE (-1.4), RANDOM (-3.3) |
| MIN-CONFLICTS (k=60) | — | WALK-k (k=60) (-0.5) | EXACT (-3.2), DPLL-b (b >= N) (-3.2), DPLL-b[MOMS, b=6, Δ=UNSAT] (-1.4), BEAM-2 (-1.4), BACKDOOR[k=2,OCC] (-1.4), C-UC/STOP (-1.4), C-UC/CONT (-3.2), C-GREEDY (-1.3), POLARITY / ALWAYS-SAT (-3.2), B1 (UP-k, FLP-1) (-1.4), NOISY-EXACT (-2.6), PERCEPTION-NOISE (-2.5), RANDOM (-3.2) |
| C-UC/STOP | DPLL-b[MOMS, b=6, Δ=UNSAT], BEAM-2, BACKDOOR[k=2,OCC] | WALK-k (k=60) (-0.4), MIN-CONFLICTS (k=60) (-0.7) | EXACT (-1.8), DPLL-b (b >= N) (-1.8), C-UC/CONT (-1.8), C-GREEDY (-3.6), POLARITY / ALWAYS-SAT (-3.6), B1 (UP-k, FLP-1) (-1.9), NOISY-EXACT (-1.8), PERCEPTION-NOISE (-1.8), RANDOM (-3.6) |
| C-UC/CONT | — | WALK-k (k=60) (-0.4), MIN-CONFLICTS (k=60) (-0.7), NOISY-EXACT (-0.7) | EXACT (-1.8), DPLL-b (b >= N) (-1.8), DPLL-b[MOMS, b=6, Δ=UNSAT] (-1.8), BEAM-2 (-1.8), BACKDOOR[k=2,OCC] (-1.8), C-UC/STOP (-1.8), C-GREEDY (-1.9), POLARITY / ALWAYS-SAT (-1.9), B1 (UP-k, FLP-1) (-3.6), PERCEPTION-NOISE (-1.3), RANDOM (-1.9) |
| C-GREEDY | — | MIN-CONFLICTS (k=60) (-0.5) | EXACT (-3.6), DPLL-b (b >= N) (-3.6), DPLL-b[MOMS, b=6, Δ=UNSAT] (-3.6), BEAM-2 (-3.6), BACKDOOR[k=2,OCC] (-3.6), WALK-k (k=60) (-1.0), C-UC/STOP (-3.6), C-UC/CONT (-1.9), POLARITY / ALWAYS-SAT (-1.9), B1 (UP-k, FLP-1) (-3.6), NOISY-EXACT (-2.0), PERCEPTION-NOISE (-2.4), RANDOM (-1.9) |
| POLARITY / ALWAYS-SAT | RANDOM | — | EXACT (-3.6), DPLL-b (b >= N) (-3.6), DPLL-b[MOMS, b=6, Δ=UNSAT] (-3.6), BEAM-2 (-3.6), BACKDOOR[k=2,OCC] (-3.6), WALK-k (k=60) (-2.2), MIN-CONFLICTS (k=60) (-2.2), C-UC/STOP (-3.6), C-UC/CONT (-1.9), C-GREEDY (-1.9), B1 (UP-k, FLP-1) (-3.6), NOISY-EXACT (-2.0), PERCEPTION-NOISE (-3.1) |
| B1 (UP-k, FLP-1) | — | — | EXACT (-3.6), DPLL-b (b >= N) (-3.6), DPLL-b[MOMS, b=6, Δ=UNSAT] (-1.9), BEAM-2 (-1.9), BACKDOOR[k=2,OCC] (-1.9), WALK-k (k=60) (-2.2), MIN-CONFLICTS (k=60) (-2.2), C-UC/STOP (-1.9), C-UC/CONT (-3.6), C-GREEDY (-3.6), POLARITY / ALWAYS-SAT (-3.6), NOISY-EXACT (-3.6), PERCEPTION-NOISE (-3.6), RANDOM (-3.6) |
| NOISY-EXACT | — | — | DPLL-b[MOMS, b=6, Δ=UNSAT] (-1.6), BEAM-2 (-1.6), BACKDOOR[k=2,OCC] (-1.6), WALK-k (k=60) (-1.7), MIN-CONFLICTS (k=60) (-2.1), C-UC/STOP (-1.6), C-UC/CONT (-1.6), C-GREEDY (-3.5), POLARITY / ALWAYS-SAT (-3.5), B1 (UP-k, FLP-1) (-3.5), RANDOM (-3.5) |
| PERCEPTION-NOISE | EXACT, DPLL-b (b >= N) | NOISY-EXACT (-0.1) | DPLL-b[MOMS, b=6, Δ=UNSAT] (-1.7), BEAM-2 (-1.7), BACKDOOR[k=2,OCC] (-1.7), WALK-k (k=60) (-1.8), MIN-CONFLICTS (k=60) (-2.2), C-UC/STOP (-1.7), C-UC/CONT (-1.7), C-GREEDY (-3.6), POLARITY / ALWAYS-SAT (-3.6), B1 (UP-k, FLP-1) (-3.6), RANDOM (-3.6) |
| RANDOM | POLARITY / ALWAYS-SAT | — | EXACT (-3.6), DPLL-b (b >= N) (-3.6), DPLL-b[MOMS, b=6, Δ=UNSAT] (-3.6), BEAM-2 (-3.6), BACKDOOR[k=2,OCC] (-3.6), WALK-k (k=60) (-2.2), MIN-CONFLICTS (k=60) (-2.2), C-UC/STOP (-3.6), C-UC/CONT (-1.9), C-GREEDY (-1.9), B1 (UP-k, FLP-1) (-3.6), NOISY-EXACT (-2.0), PERCEPTION-NOISE (-3.1) |

**Not distinguished by this set:** DPLL-b vs WALK-k on the SAT twin alone: both solve it. Separated by E2 (quadrants), E5 (certificates) and E6/E7. BEAM-w vs DPLL-b: see E4. PERCEPTION-NOISE: see E6.

### E1.1: n=12 (dev level), SAT member, bare

- **Question tested:** Below or above the budget line: does the model search to completion, and on the UNSAT twin does it certify or default?
- **Controlled:** n = 12, m = 51 (α = 4.25); clause order and variable names identical across the pair; pure 3-CNF, no unit clauses; same prompt template and answer format
- **Varied:** one literal sign (clause C32, position 1) decides SAT vs UNSAT
- **Ground truth:** `{"answer": "SAT", "n_solutions": 2, "solutions": ["x1=0 x2=1 x3=1 x4=1 x5=1 x6=1 x7=0 x8=0 x9=1 x10=0 x11=0 x12=0", "x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=0 x8=0 x9=1 x10=0 x11=0 x12=0"]}`
- **Notes:** Dev-level size: at BE this pair sits far below every panel model's n*; the study sweep uses 9 grid levels centred on n*.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x12. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x4 OR NOT x11 OR NOT x12)
C2: (x1 OR x8 OR x9)
C3: (NOT x9 OR x11 OR NOT x12)
C4: (x2 OR NOT x4 OR x12)
C5: (x4 OR NOT x8 OR NOT x12)
C6: (x9 OR NOT x10 OR NOT x11)
C7: (NOT x2 OR NOT x4 OR NOT x11)
C8: (x2 OR x4 OR x12)
C9: (x5 OR x6 OR NOT x9)
C10: (NOT x1 OR NOT x2 OR x9)
C11: (x1 OR NOT x4 OR NOT x8)
C12: (NOT x3 OR x6 OR NOT x9)
C13: (NOT x8 OR NOT x9 OR x12)
C14: (NOT x2 OR x4 OR NOT x8)
C15: (NOT x3 OR x9 OR NOT x11)
C16: (NOT x7 OR NOT x10 OR x11)
C17: (x5 OR x9 OR x10)
C18: (x1 OR NOT x7 OR NOT x10)
C19: (x7 OR x9 OR x10)
C20: (x7 OR NOT x8 OR NOT x9)
C21: (x4 OR x8 OR NOT x11)
C22: (x6 OR x8 OR x9)
C23: (x1 OR x3 OR x5)
C24: (x5 OR x6 OR x11)
C25: (NOT x2 OR NOT x9 OR NOT x10)
C26: (NOT x1 OR NOT x7 OR NOT x12)
C27: (NOT x4 OR NOT x9 OR NOT x12)
C28: (NOT x3 OR x10 OR NOT x12)
C29: (x3 OR NOT x6 OR x10)
C30: (x2 OR x3 OR NOT x4)
C31: (x2 OR NOT x7 OR NOT x12)
C32: (x3 OR NOT x4 OR x7)
C33: (x6 OR NOT x10 OR NOT x11)
C34: (x6 OR NOT x9 OR NOT x11)
C35: (x2 OR NOT x8 OR NOT x12)
C36: (x3 OR x8 OR x10)
C37: (NOT x2 OR NOT x3 OR x5)
C38: (x2 OR x6 OR x12)
C39: (x4 OR NOT x6 OR NOT x10)
C40: (x3 OR x7 OR NOT x8)
C41: (NOT x2 OR x3 OR NOT x10)
C42: (NOT x7 OR x11 OR NOT x12)
C43: (NOT x5 OR NOT x6 OR NOT x11)
C44: (NOT x3 OR NOT x6 OR NOT x7)
C45: (NOT x3 OR x4 OR x7)
C46: (NOT x1 OR NOT x2 OR NOT x8)
C47: (NOT x1 OR NOT x4 OR x5)
C48: (x7 OR NOT x10 OR x11)
C49: (NOT x4 OR NOT x8 OR NOT x11)
C50: (x1 OR x2 OR x10)
C51: (x1 OR x4 OR NOT x9)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 2 solutions | π_EXACT = the share of above-n* items still solved; a collapse at n*_obs inside the sweep bounds π_EXACT ≤ 0.05 (upper 95%) there | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=0 x8=0 x9=1 x10=0 x11=0 x12=0 after N = 4 nodes (W = 765); MENTION,MAJ: N = 4. If b < N: the default (UNSAT, or FILL = violates [10, 44] at b = N/2). | π_DPLL (posterior mean, 95% CrI) per model × budget; pre-registered: Δπ_DPLL(2k→8k) > 0 with CrI excluding 0, and the collapse coefficient β ≈ 1 gives ΔLL(DPLL-b vs NOISY-EXACT) > 0 per item; power 0.8 to detect π_DPLL ≥ 0.15 against NE on above-n* errors | MOMS,MAJ reference: DEC = 3, BT = 1, CONF = 1, PROP = 10; first decisions (var, value) = [(4, 1), (2, 1), (9, 0)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: SAT; w=2: SAT; w=4: SAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: SAT; k=2,MENTION: UNSAT (default); k=2,INDEX: SAT; k=3,OCC: SAT; k=3,MENTION: UNSAT (default); k=3,INDEX: SAT | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=12) = 0.34, P(success / k=60) = 0.82, P(success / k=300) = 1.00; modal failure at k=12: violates [11], LM0=True, Hamming to nearest solution = 5 | π_F on SAT members estimated from near-miss errors (E6 profile); expected to rise with budget | FULL candidate, VIOL list, FLIP moves; DEC <= 1; #FLIP about the WalkSAT median of 29 |
| MIN-CONFLICTS | P(success / k=12) = 0.09, P(success / k=60) = 0.36, P(success / k=300) = 0.35 | π_F on SAT members estimated from near-miss errors (E6 profile); expected to rise with budget | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C30); MENTION,MAJ: SAT; MOMS,TRUE: SAT; MOMS,MAJ: UNSAT (dead end at C11) / CONT violates: MENTION,TRUE: [11, 30, 31, 35, 49, 50]; MENTION,MAJ: []; MOMS,TRUE: []; MOMS,MAJ: [11] | π_C = the budget-flat component that follows g(x); lift over the permutation baseline reported with its CI | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=1 x3=1 x4=1 x5=1 x6=0 x7=1 x8=0 x9=1 x10=0 x11=0 x12=0 (violates [12]) | π_C = the budget-flat component that follows g(x); lift over the permutation baseline reported with its CI | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=1 x8=0 x9=0 x10=0 x11=0 x12=0 (violates [10, 44]) | π_POLARITY bounded by the pair ADR: each pair answered right on both twins has LR ≈ 0.05 against it | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.926 (eps=1e-4) or 0.465 (eps=1e-3), W = 765; otherwise a slip (one missed clause, or a spurious conflict) | π_NE = the budget-independent, W-smooth component; if β̂ ∈ [0.5, 1.5], π_NE ≤ 0.2 (upper 95%) on above-n* errors | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| PERCEPTION-NOISE | exact answer to a misread formula; 17% of single sign misreads give a wrong answer here | π_PERCEPTION estimated in E6 (re-check, same-clause repeats); here only its budget-flat error rate | the trace quotes the violated clause with a sign or index error |
| RANDOM | uniform assignment; P(correct) = 0.0005 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the ADR: ADR >= 0.5 implies π_A ≤ 0.5 (upper 95%) with 270 pairs | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), DPLL-b[MENTION, b=6, Δ=UNSAT], DPLL-b[MOMS, b=6, Δ=UNSAT], BEAM-2, BACKDOOR[k=2,OCC], C-UC/STOP, C-UC/CONT; pushes down DPLL-b[INDEX, b=6, Δ=UNSAT] (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.014)
- *near-miss (infeasible, LM0, V<=3)*: best fit C-GREEDY; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=6, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=6, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=6, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=60) (LR 0.191), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.049), PERCEPTION-NOISE (LR 0.063), RANDOM (LR 0.013)
- *infeasible (other)*: best fit POLARITY / ALWAYS-SAT; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=6, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=6, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=6, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=60) (LR 0.013), MIN-CONFLICTS (k=60) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.049), PERCEPTION-NOISE (LR 0.013)
- *UNSAT/UNKNOWN*: best fit DPLL-b[INDEX, b=6, Δ=UNSAT], B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=6, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=6, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=60) (LR 0.013), MIN-CONFLICTS (k=60) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), PERCEPTION-NOISE (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=6, W=1173; MENTION,MAJ: N=4, W=663; INDEX,TRUE: N=2, W=663; INDEX,MAJ: N=7, W=1887; MOMS,TRUE: N=3, W=612; MOMS,MAJ: N=4, W=765. Every member's full output is in the JSONL `predictions` field.

### E1.2: n=12 (dev level), UNSAT member, bare

- **Question tested:** Below or above the budget line: does the model search to completion, and on the UNSAT twin does it certify or default?
- **Controlled:** n = 12, m = 51 (α = 4.25); clause order and variable names identical across the pair; pure 3-CNF, no unit clauses; same prompt template and answer format
- **Varied:** one literal sign (clause C32, position 1) decides SAT vs UNSAT
- **Ground truth:** `{"answer": "UNSAT"}`
- **Notes:** Dev-level size: at BE this pair sits far below every panel model's n*; the study sweep uses 9 grid levels centred on n*.
- **Differs from E1.1 only in:** C32: (x3 OR NOT x4 OR x7) → (NOT x3 OR NOT x4 OR x7)

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x12. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x4 OR NOT x11 OR NOT x12)
C2: (x1 OR x8 OR x9)
C3: (NOT x9 OR x11 OR NOT x12)
C4: (x2 OR NOT x4 OR x12)
C5: (x4 OR NOT x8 OR NOT x12)
C6: (x9 OR NOT x10 OR NOT x11)
C7: (NOT x2 OR NOT x4 OR NOT x11)
C8: (x2 OR x4 OR x12)
C9: (x5 OR x6 OR NOT x9)
C10: (NOT x1 OR NOT x2 OR x9)
C11: (x1 OR NOT x4 OR NOT x8)
C12: (NOT x3 OR x6 OR NOT x9)
C13: (NOT x8 OR NOT x9 OR x12)
C14: (NOT x2 OR x4 OR NOT x8)
C15: (NOT x3 OR x9 OR NOT x11)
C16: (NOT x7 OR NOT x10 OR x11)
C17: (x5 OR x9 OR x10)
C18: (x1 OR NOT x7 OR NOT x10)
C19: (x7 OR x9 OR x10)
C20: (x7 OR NOT x8 OR NOT x9)
C21: (x4 OR x8 OR NOT x11)
C22: (x6 OR x8 OR x9)
C23: (x1 OR x3 OR x5)
C24: (x5 OR x6 OR x11)
C25: (NOT x2 OR NOT x9 OR NOT x10)
C26: (NOT x1 OR NOT x7 OR NOT x12)
C27: (NOT x4 OR NOT x9 OR NOT x12)
C28: (NOT x3 OR x10 OR NOT x12)
C29: (x3 OR NOT x6 OR x10)
C30: (x2 OR x3 OR NOT x4)
C31: (x2 OR NOT x7 OR NOT x12)
C32: (NOT x3 OR NOT x4 OR x7)
C33: (x6 OR NOT x10 OR NOT x11)
C34: (x6 OR NOT x9 OR NOT x11)
C35: (x2 OR NOT x8 OR NOT x12)
C36: (x3 OR x8 OR x10)
C37: (NOT x2 OR NOT x3 OR x5)
C38: (x2 OR x6 OR x12)
C39: (x4 OR NOT x6 OR NOT x10)
C40: (x3 OR x7 OR NOT x8)
C41: (NOT x2 OR x3 OR NOT x10)
C42: (NOT x7 OR x11 OR NOT x12)
C43: (NOT x5 OR NOT x6 OR NOT x11)
C44: (NOT x3 OR NOT x6 OR NOT x7)
C45: (NOT x3 OR x4 OR x7)
C46: (NOT x1 OR NOT x2 OR NOT x8)
C47: (NOT x1 OR NOT x4 OR x5)
C48: (x7 OR NOT x10 OR x11)
C49: (NOT x4 OR NOT x8 OR NOT x11)
C50: (x1 OR x2 OR x10)
C51: (x1 OR x4 OR NOT x9)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | UNSAT | π_EXACT = the share of above-n* items still solved; a collapse at n*_obs inside the sweep bounds π_EXACT ≤ 0.05 (upper 95%) there | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: UNSAT after N = 10 nodes (W = 2193); MENTION,MAJ: N = 14. If b < N: the default (UNSAT, or FILL = violates [10, 29, 36] at b = N/2). | π_DPLL on UNSAT members tracks the certified rate, which should fall with W_unsat (pre-registered slope < 0); the token ratio UNSAT/SAT twin tracking W_unsat/W_sat adds ΔLL for DPLL-b over WALK-k | MOMS,MAJ reference: DEC = 5, BT = 5, CONF = 6, PROP = 32; first decisions (var, value) = [(4, 1), (2, 1), (9, 0)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: UNSAT; w=2: UNSAT; w=4: UNSAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: UNSAT (default) | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | never certifies UNSAT; ends in a near-miss: k=12: violates [12], LM0=True, Hamming to nearest solution = None | π_F on UNSAT members is bounded by certification: each FA6-certified UNSAT response has LR ≈ 0.05 against F; 30 certified responses bound π_F(UNSAT) ≤ 0.1 (upper 95%) | FULL candidate, VIOL list, FLIP moves; DEC <= 1; FLIP until cap or GIVEUP |
| MIN-CONFLICTS | P(success / k=12) = 0.00, P(success / k=60) = 0.00, P(success / k=300) = 0.00 | π_F on UNSAT members is bounded by certification: each FA6-certified UNSAT response has LR ≈ 0.05 against F; 30 certified responses bound π_F(UNSAT) ≤ 0.1 (upper 95%) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C30); MENTION,MAJ: UNSAT (dead end at C44); MOMS,TRUE: UNSAT (dead end at C44); MOMS,MAJ: UNSAT (dead end at C11) / CONT violates: MENTION,TRUE: [11, 30, 31, 35, 49, 50]; MENTION,MAJ: [44]; MOMS,TRUE: [44]; MOMS,MAJ: [11] | π_C = the budget-flat component that follows g(x); lift over the permutation baseline reported with its CI | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=1 x3=0 x4=1 x5=1 x6=0 x7=1 x8=0 x9=1 x10=0 x11=0 x12=0 (violates [36]) | π_C = the budget-flat component that follows g(x); lift over the permutation baseline reported with its CI | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=0 x4=1 x5=1 x6=1 x7=1 x8=0 x9=0 x10=0 x11=0 x12=0 (violates [10, 29, 36]) | π_POLARITY bounded by the pair ADR: each pair answered right on both twins has LR ≈ 0.05 against it | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.803 (eps=1e-4) or 0.111 (eps=1e-3), W = 2193; otherwise a slip (one missed clause, or a spurious conflict) | π_NE = the budget-independent, W-smooth component; if β̂ ∈ [0.5, 1.5], π_NE ≤ 0.2 (upper 95%) on above-n* errors | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| PERCEPTION-NOISE | exact answer to a misread formula; 14% of single sign misreads give a wrong answer here | π_PERCEPTION estimated in E6 (re-check, same-clause repeats); here only its budget-flat error rate | the trace quotes the violated clause with a sign or index error |
| RANDOM | uniform assignment; P(correct) = 0.0000 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the ADR: ADR >= 0.5 implies π_A ≤ 0.5 (upper 95%) with 270 pairs | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *UNSAT, certified*: best fit EXACT, DPLL-b (b >= N); pushes down DPLL-b[MOMS, b=6, Δ=UNSAT] (LR 0.017), BEAM-2 (LR 0.017), BACKDOOR[k=2,OCC] (LR 0.017), WALK-k (k=60) (LR 0.017), MIN-CONFLICTS (k=60) (LR 0.017), C-UC/STOP (LR 0.017), C-UC/CONT (LR 0.017), C-GREEDY (LR 0.017), POLARITY / ALWAYS-SAT (LR 0.017), B1 (UP-k, FLP-1) (LR 0.017), RANDOM (LR 0.017)
- *UNSAT, uncertified*: best fit DPLL-b[MOMS, b=6, Δ=UNSAT], BEAM-2, BACKDOOR[k=2,OCC], C-UC/STOP, B1 (UP-k, FLP-1); pushes down EXACT (LR 0.017), DPLL-b (b >= N) (LR 0.017), C-UC/CONT (LR 0.017), C-GREEDY (LR 0.017), POLARITY / ALWAYS-SAT (LR 0.017), NOISY-EXACT (LR 0.017), PERCEPTION-NOISE (LR 0.017), RANDOM (LR 0.017)
- *SAT claim (infeasible)*: best fit C-UC/CONT, C-GREEDY, POLARITY / ALWAYS-SAT, RANDOM; pushes down EXACT (LR 0.017), DPLL-b (b >= N) (LR 0.017), DPLL-b[MOMS, b=6, Δ=UNSAT] (LR 0.017), BEAM-2 (LR 0.017), BACKDOOR[k=2,OCC] (LR 0.017), C-UC/STOP (LR 0.017), B1 (UP-k, FLP-1) (LR 0.017), PERCEPTION-NOISE (LR 0.058)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=14, W=2805; MENTION,MAJ: N=14, W=2805; INDEX,TRUE: N=14, W=3213; INDEX,MAJ: N=14, W=3213; MOMS,TRUE: N=10, W=2193; MOMS,MAJ: N=10, W=2193. Every member's full output is in the JSONL `predictions` field.

### E1.3: n=12 (dev level), SAT member, theme: product configuration

- **Question tested:** Below or above the budget line: does the model search to completion, and on the UNSAT twin does it certify or default?
- **Controlled:** n = 12, m = 51 (α = 4.25); clause order and variable names identical across the pair; pure 3-CNF, no unit clauses; same prompt template and answer format
- **Varied:** one literal sign (clause C32, position 1) decides SAT vs UNSAT
- **Ground truth:** `{"answer": "SAT", "n_solutions": 2, "solutions": ["x1=0 x2=1 x3=1 x4=1 x5=1 x6=1 x7=0 x8=0 x9=1 x10=0 x11=0 x12=0", "x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=0 x8=0 x9=1 x10=0 x11=0 x12=0"]}`
- **Notes:** Dev-level size: at BE this pair sits far below every panel model's n*; the study sweep uses 9 grid levels centred on n*.

<details><summary>Exact prompt</summary>

```text
A customer is configuring a product with 12 optional features, F1, F2, ..., F12. Each feature is either included or excluded. The customer's requirements are listed below. Each requirement names three conditions, and at least one of the three must hold. It may be impossible to meet every requirement.

R1: F4 is included, or F11 is excluded, or F12 is excluded.
R2: F1 is included, or F8 is included, or F9 is included.
R3: F9 is excluded, or F11 is included, or F12 is excluded.
R4: F2 is included, or F4 is excluded, or F12 is included.
R5: F4 is included, or F8 is excluded, or F12 is excluded.
R6: F9 is included, or F10 is excluded, or F11 is excluded.
R7: F2 is excluded, or F4 is excluded, or F11 is excluded.
R8: F2 is included, or F4 is included, or F12 is included.
R9: F5 is included, or F6 is included, or F9 is excluded.
R10: F1 is excluded, or F2 is excluded, or F9 is included.
R11: F1 is included, or F4 is excluded, or F8 is excluded.
R12: F3 is excluded, or F6 is included, or F9 is excluded.
R13: F8 is excluded, or F9 is excluded, or F12 is included.
R14: F2 is excluded, or F4 is included, or F8 is excluded.
R15: F3 is excluded, or F9 is included, or F11 is excluded.
R16: F7 is excluded, or F10 is excluded, or F11 is included.
R17: F5 is included, or F9 is included, or F10 is included.
R18: F1 is included, or F7 is excluded, or F10 is excluded.
R19: F7 is included, or F9 is included, or F10 is included.
R20: F7 is included, or F8 is excluded, or F9 is excluded.
R21: F4 is included, or F8 is included, or F11 is excluded.
R22: F6 is included, or F8 is included, or F9 is included.
R23: F1 is included, or F3 is included, or F5 is included.
R24: F5 is included, or F6 is included, or F11 is included.
R25: F2 is excluded, or F9 is excluded, or F10 is excluded.
R26: F1 is excluded, or F7 is excluded, or F12 is excluded.
R27: F4 is excluded, or F9 is excluded, or F12 is excluded.
R28: F3 is excluded, or F10 is included, or F12 is excluded.
R29: F3 is included, or F6 is excluded, or F10 is included.
R30: F2 is included, or F3 is included, or F4 is excluded.
R31: F2 is included, or F7 is excluded, or F12 is excluded.
R32: F3 is included, or F4 is excluded, or F7 is included.
R33: F6 is included, or F10 is excluded, or F11 is excluded.
R34: F6 is included, or F9 is excluded, or F11 is excluded.
R35: F2 is included, or F8 is excluded, or F12 is excluded.
R36: F3 is included, or F8 is included, or F10 is included.
R37: F2 is excluded, or F3 is excluded, or F5 is included.
R38: F2 is included, or F6 is included, or F12 is included.
R39: F4 is included, or F6 is excluded, or F10 is excluded.
R40: F3 is included, or F7 is included, or F8 is excluded.
R41: F2 is excluded, or F3 is included, or F10 is excluded.
R42: F7 is excluded, or F11 is included, or F12 is excluded.
R43: F5 is excluded, or F6 is excluded, or F11 is excluded.
R44: F3 is excluded, or F6 is excluded, or F7 is excluded.
R45: F3 is excluded, or F4 is included, or F7 is included.
R46: F1 is excluded, or F2 is excluded, or F8 is excluded.
R47: F1 is excluded, or F4 is excluded, or F5 is included.
R48: F7 is included, or F10 is excluded, or F11 is included.
R49: F4 is excluded, or F8 is excluded, or F11 is excluded.
R50: F1 is included, or F2 is included, or F10 is included.
R51: F1 is included, or F4 is included, or F9 is excluded.

Is there a configuration that meets every requirement? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if a configuration exists: {"answer": "POSSIBLE", "configuration": "F1=in F2=out ... FN=in"} (list every feature)
- if no configuration exists: {"answer": "IMPOSSIBLE"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 2 solutions | π_EXACT = the share of above-n* items still solved; a collapse at n*_obs inside the sweep bounds π_EXACT ≤ 0.05 (upper 95%) there | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=0 x8=0 x9=1 x10=0 x11=0 x12=0 after N = 4 nodes (W = 765); MENTION,MAJ: N = 4. If b < N: the default (UNSAT, or FILL = violates [10, 44] at b = N/2). | π_DPLL (posterior mean, 95% CrI) per model × budget; pre-registered: Δπ_DPLL(2k→8k) > 0 with CrI excluding 0, and the collapse coefficient β ≈ 1 gives ΔLL(DPLL-b vs NOISY-EXACT) > 0 per item; power 0.8 to detect π_DPLL ≥ 0.15 against NE on above-n* errors | MOMS,MAJ reference: DEC = 3, BT = 1, CONF = 1, PROP = 10; first decisions (var, value) = [(4, 1), (2, 1), (9, 0)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: SAT; w=2: SAT; w=4: SAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: SAT; k=2,MENTION: UNSAT (default); k=2,INDEX: SAT; k=3,OCC: SAT; k=3,MENTION: UNSAT (default); k=3,INDEX: SAT | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=12) = 0.34, P(success / k=60) = 0.82, P(success / k=300) = 1.00; modal failure at k=12: violates [11], LM0=True, Hamming to nearest solution = 5 | π_F on SAT members estimated from near-miss errors (E6 profile); expected to rise with budget | FULL candidate, VIOL list, FLIP moves; DEC <= 1; #FLIP about the WalkSAT median of 29 |
| MIN-CONFLICTS | P(success / k=12) = 0.09, P(success / k=60) = 0.36, P(success / k=300) = 0.35 | π_F on SAT members estimated from near-miss errors (E6 profile); expected to rise with budget | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C30); MENTION,MAJ: SAT; MOMS,TRUE: SAT; MOMS,MAJ: UNSAT (dead end at C11) / CONT violates: MENTION,TRUE: [11, 30, 31, 35, 49, 50]; MENTION,MAJ: []; MOMS,TRUE: []; MOMS,MAJ: [11] | π_C = the budget-flat component that follows g(x); lift over the permutation baseline reported with its CI | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=1 x3=1 x4=1 x5=1 x6=0 x7=1 x8=0 x9=1 x10=0 x11=0 x12=0 (violates [12]) | π_C = the budget-flat component that follows g(x); lift over the permutation baseline reported with its CI | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=1 x8=0 x9=0 x10=0 x11=0 x12=0 (violates [10, 44]) | π_POLARITY bounded by the pair ADR: each pair answered right on both twins has LR ≈ 0.05 against it | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.926 (eps=1e-4) or 0.465 (eps=1e-3), W = 765; otherwise a slip (one missed clause, or a spurious conflict) | π_NE = the budget-independent, W-smooth component; if β̂ ∈ [0.5, 1.5], π_NE ≤ 0.2 (upper 95%) on above-n* errors | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| PERCEPTION-NOISE | exact answer to a misread formula; 17% of single sign misreads give a wrong answer here | π_PERCEPTION estimated in E6 (re-check, same-clause repeats); here only its budget-flat error rate | the trace quotes the violated clause with a sign or index error |
| RANDOM | uniform assignment; P(correct) = 0.0005 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the ADR: ADR >= 0.5 implies π_A ≤ 0.5 (upper 95%) with 270 pairs | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), DPLL-b[MENTION, b=6, Δ=UNSAT], DPLL-b[MOMS, b=6, Δ=UNSAT], BEAM-2, BACKDOOR[k=2,OCC], C-UC/STOP, C-UC/CONT; pushes down DPLL-b[INDEX, b=6, Δ=UNSAT] (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.014)
- *near-miss (infeasible, LM0, V<=3)*: best fit C-GREEDY; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=6, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=6, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=6, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=60) (LR 0.191), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.049), PERCEPTION-NOISE (LR 0.063), RANDOM (LR 0.013)
- *infeasible (other)*: best fit POLARITY / ALWAYS-SAT; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=6, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=6, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=6, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=60) (LR 0.013), MIN-CONFLICTS (k=60) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.049), PERCEPTION-NOISE (LR 0.013)
- *UNSAT/UNKNOWN*: best fit DPLL-b[INDEX, b=6, Δ=UNSAT], B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=6, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=6, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=60) (LR 0.013), MIN-CONFLICTS (k=60) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), PERCEPTION-NOISE (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=6, W=1173; MENTION,MAJ: N=4, W=663; INDEX,TRUE: N=2, W=663; INDEX,MAJ: N=7, W=1887; MOMS,TRUE: N=3, W=612; MOMS,MAJ: N=4, W=765. Every member's full output is in the JSONL `predictions` field.

### E1.4: n=12 (dev level), UNSAT member, theme: product configuration

- **Question tested:** Below or above the budget line: does the model search to completion, and on the UNSAT twin does it certify or default?
- **Controlled:** n = 12, m = 51 (α = 4.25); clause order and variable names identical across the pair; pure 3-CNF, no unit clauses; same prompt template and answer format
- **Varied:** one literal sign (clause C32, position 1) decides SAT vs UNSAT
- **Ground truth:** `{"answer": "UNSAT"}`
- **Notes:** Dev-level size: at BE this pair sits far below every panel model's n*; the study sweep uses 9 grid levels centred on n*.
- **Differs from E1.3 only in:** C32: (x3 OR NOT x4 OR x7) → (NOT x3 OR NOT x4 OR x7)

<details><summary>Exact prompt</summary>

```text
A customer is configuring a product with 12 optional features, F1, F2, ..., F12. Each feature is either included or excluded. The customer's requirements are listed below. Each requirement names three conditions, and at least one of the three must hold. It may be impossible to meet every requirement.

R1: F4 is included, or F11 is excluded, or F12 is excluded.
R2: F1 is included, or F8 is included, or F9 is included.
R3: F9 is excluded, or F11 is included, or F12 is excluded.
R4: F2 is included, or F4 is excluded, or F12 is included.
R5: F4 is included, or F8 is excluded, or F12 is excluded.
R6: F9 is included, or F10 is excluded, or F11 is excluded.
R7: F2 is excluded, or F4 is excluded, or F11 is excluded.
R8: F2 is included, or F4 is included, or F12 is included.
R9: F5 is included, or F6 is included, or F9 is excluded.
R10: F1 is excluded, or F2 is excluded, or F9 is included.
R11: F1 is included, or F4 is excluded, or F8 is excluded.
R12: F3 is excluded, or F6 is included, or F9 is excluded.
R13: F8 is excluded, or F9 is excluded, or F12 is included.
R14: F2 is excluded, or F4 is included, or F8 is excluded.
R15: F3 is excluded, or F9 is included, or F11 is excluded.
R16: F7 is excluded, or F10 is excluded, or F11 is included.
R17: F5 is included, or F9 is included, or F10 is included.
R18: F1 is included, or F7 is excluded, or F10 is excluded.
R19: F7 is included, or F9 is included, or F10 is included.
R20: F7 is included, or F8 is excluded, or F9 is excluded.
R21: F4 is included, or F8 is included, or F11 is excluded.
R22: F6 is included, or F8 is included, or F9 is included.
R23: F1 is included, or F3 is included, or F5 is included.
R24: F5 is included, or F6 is included, or F11 is included.
R25: F2 is excluded, or F9 is excluded, or F10 is excluded.
R26: F1 is excluded, or F7 is excluded, or F12 is excluded.
R27: F4 is excluded, or F9 is excluded, or F12 is excluded.
R28: F3 is excluded, or F10 is included, or F12 is excluded.
R29: F3 is included, or F6 is excluded, or F10 is included.
R30: F2 is included, or F3 is included, or F4 is excluded.
R31: F2 is included, or F7 is excluded, or F12 is excluded.
R32: F3 is excluded, or F4 is excluded, or F7 is included.
R33: F6 is included, or F10 is excluded, or F11 is excluded.
R34: F6 is included, or F9 is excluded, or F11 is excluded.
R35: F2 is included, or F8 is excluded, or F12 is excluded.
R36: F3 is included, or F8 is included, or F10 is included.
R37: F2 is excluded, or F3 is excluded, or F5 is included.
R38: F2 is included, or F6 is included, or F12 is included.
R39: F4 is included, or F6 is excluded, or F10 is excluded.
R40: F3 is included, or F7 is included, or F8 is excluded.
R41: F2 is excluded, or F3 is included, or F10 is excluded.
R42: F7 is excluded, or F11 is included, or F12 is excluded.
R43: F5 is excluded, or F6 is excluded, or F11 is excluded.
R44: F3 is excluded, or F6 is excluded, or F7 is excluded.
R45: F3 is excluded, or F4 is included, or F7 is included.
R46: F1 is excluded, or F2 is excluded, or F8 is excluded.
R47: F1 is excluded, or F4 is excluded, or F5 is included.
R48: F7 is included, or F10 is excluded, or F11 is included.
R49: F4 is excluded, or F8 is excluded, or F11 is excluded.
R50: F1 is included, or F2 is included, or F10 is included.
R51: F1 is included, or F4 is included, or F9 is excluded.

Is there a configuration that meets every requirement? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if a configuration exists: {"answer": "POSSIBLE", "configuration": "F1=in F2=out ... FN=in"} (list every feature)
- if no configuration exists: {"answer": "IMPOSSIBLE"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | UNSAT | π_EXACT = the share of above-n* items still solved; a collapse at n*_obs inside the sweep bounds π_EXACT ≤ 0.05 (upper 95%) there | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: UNSAT after N = 10 nodes (W = 2193); MENTION,MAJ: N = 14. If b < N: the default (UNSAT, or FILL = violates [10, 29, 36] at b = N/2). | π_DPLL on UNSAT members tracks the certified rate, which should fall with W_unsat (pre-registered slope < 0); the token ratio UNSAT/SAT twin tracking W_unsat/W_sat adds ΔLL for DPLL-b over WALK-k | MOMS,MAJ reference: DEC = 5, BT = 5, CONF = 6, PROP = 32; first decisions (var, value) = [(4, 1), (2, 1), (9, 0)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: UNSAT; w=2: UNSAT; w=4: UNSAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: UNSAT (default) | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | never certifies UNSAT; ends in a near-miss: k=12: violates [12], LM0=True, Hamming to nearest solution = None | π_F on UNSAT members is bounded by certification: each FA6-certified UNSAT response has LR ≈ 0.05 against F; 30 certified responses bound π_F(UNSAT) ≤ 0.1 (upper 95%) | FULL candidate, VIOL list, FLIP moves; DEC <= 1; FLIP until cap or GIVEUP |
| MIN-CONFLICTS | P(success / k=12) = 0.00, P(success / k=60) = 0.00, P(success / k=300) = 0.00 | π_F on UNSAT members is bounded by certification: each FA6-certified UNSAT response has LR ≈ 0.05 against F; 30 certified responses bound π_F(UNSAT) ≤ 0.1 (upper 95%) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C30); MENTION,MAJ: UNSAT (dead end at C44); MOMS,TRUE: UNSAT (dead end at C44); MOMS,MAJ: UNSAT (dead end at C11) / CONT violates: MENTION,TRUE: [11, 30, 31, 35, 49, 50]; MENTION,MAJ: [44]; MOMS,TRUE: [44]; MOMS,MAJ: [11] | π_C = the budget-flat component that follows g(x); lift over the permutation baseline reported with its CI | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=1 x3=0 x4=1 x5=1 x6=0 x7=1 x8=0 x9=1 x10=0 x11=0 x12=0 (violates [36]) | π_C = the budget-flat component that follows g(x); lift over the permutation baseline reported with its CI | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=0 x4=1 x5=1 x6=1 x7=1 x8=0 x9=0 x10=0 x11=0 x12=0 (violates [10, 29, 36]) | π_POLARITY bounded by the pair ADR: each pair answered right on both twins has LR ≈ 0.05 against it | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.803 (eps=1e-4) or 0.111 (eps=1e-3), W = 2193; otherwise a slip (one missed clause, or a spurious conflict) | π_NE = the budget-independent, W-smooth component; if β̂ ∈ [0.5, 1.5], π_NE ≤ 0.2 (upper 95%) on above-n* errors | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| PERCEPTION-NOISE | exact answer to a misread formula; 14% of single sign misreads give a wrong answer here | π_PERCEPTION estimated in E6 (re-check, same-clause repeats); here only its budget-flat error rate | the trace quotes the violated clause with a sign or index error |
| RANDOM | uniform assignment; P(correct) = 0.0000 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the ADR: ADR >= 0.5 implies π_A ≤ 0.5 (upper 95%) with 270 pairs | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *UNSAT, certified*: best fit EXACT, DPLL-b (b >= N); pushes down DPLL-b[MOMS, b=6, Δ=UNSAT] (LR 0.017), BEAM-2 (LR 0.017), BACKDOOR[k=2,OCC] (LR 0.017), WALK-k (k=60) (LR 0.017), MIN-CONFLICTS (k=60) (LR 0.017), C-UC/STOP (LR 0.017), C-UC/CONT (LR 0.017), C-GREEDY (LR 0.017), POLARITY / ALWAYS-SAT (LR 0.017), B1 (UP-k, FLP-1) (LR 0.017), RANDOM (LR 0.017)
- *UNSAT, uncertified*: best fit DPLL-b[MOMS, b=6, Δ=UNSAT], BEAM-2, BACKDOOR[k=2,OCC], C-UC/STOP, B1 (UP-k, FLP-1); pushes down EXACT (LR 0.017), DPLL-b (b >= N) (LR 0.017), C-UC/CONT (LR 0.017), C-GREEDY (LR 0.017), POLARITY / ALWAYS-SAT (LR 0.017), NOISY-EXACT (LR 0.017), PERCEPTION-NOISE (LR 0.017), RANDOM (LR 0.017)
- *SAT claim (infeasible)*: best fit C-UC/CONT, C-GREEDY, POLARITY / ALWAYS-SAT, RANDOM; pushes down EXACT (LR 0.017), DPLL-b (b >= N) (LR 0.017), DPLL-b[MOMS, b=6, Δ=UNSAT] (LR 0.017), BEAM-2 (LR 0.017), BACKDOOR[k=2,OCC] (LR 0.017), C-UC/STOP (LR 0.017), B1 (UP-k, FLP-1) (LR 0.017), PERCEPTION-NOISE (LR 0.058)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=14, W=2805; MENTION,MAJ: N=14, W=2805; INDEX,TRUE: N=14, W=3213; INDEX,MAJ: N=14, W=3213; MOMS,TRUE: N=10, W=2193; MOMS,MAJ: N=10, W=2193. Every member's full output is in the JSONL `predictions` field.

---

## E2

### D/F quadrants at fixed n and α

| Item | Cell | Ground truth | Varied |
|------|------|--------------|--------|
| E2.1 | W low × F low | SAT (4 solutions) | W low (median DPLL work over 6 variants = 1380); F low (WalkSAT median flips = 11) |
| E2.2 | W low × F high | SAT (4 solutions) | W low (median DPLL work over 6 variants = 1380); F high (WalkSAT median flips = 35) |
| E2.3 | W high × F low | SAT (3 solutions) | W high (median DPLL work over 6 variants = 2580); F low (WalkSAT median flips = 14) |
| E2.4 | W high × F high | SAT (3 solutions) | W high (median DPLL work over 6 variants = 4320); F high (WalkSAT median flips = 54) |

**Direction table** (how each set-level outcome moves weight; the sizes are in the likelihood-ratio table below and in each item's hypothesis block):

| Observed outcome (set level) | Moves weight toward | Moves weight away from |
|------------------------------|---------------------|------------------------|
| Accuracy lower in both W-high cells, equal across F | DPLL-b; NOISY-EXACT (ambiguous on this alone) | WALK-k, MIN-CONFLICTS, C, POLARITY, EXACT |
| Accuracy lower in both F-high cells, equal across W | WALK-k / MIN-CONFLICTS | DPLL-b, NOISY-EXACT, C, EXACT |
| W effect present and b̂ rises with budget (2k < 8k <= BE), with Δ-type errors at the cap | DPLL-b | NOISY-EXACT (b̂ = ∞, errors in completed runs) |
| W effect present but b̂ flat, errors are slips in completed runs | NOISY-EXACT | DPLL-b |
| No quadrant effects; accuracy near ceiling | EXACT | D and F as the operative procedure at this size (move the level up) |

**Likelihood-ratio table** (computed). Each row asks: if one response per item (E2.1, E2.2, E2.3, E2.4) matched theory *h*'s most likely outcome, how much less likely is that pattern under each competitor? Entries are log10 LR(competitor : h), with a 5% slip floor on every theory, so −1.0 means the pattern pushes that competitor's weight down 10× relative to *h*. A cell of N independent responses multiplies these by about N. The readout is the mixture posterior over π, not a verdict (D_F_search.md §2.5).

| If responses match the modal pattern of h = | Tied with h (0.0) | Weakly disfavoured (−1 < log10 LR < 0) | Pushed down ≥ 10× (log10 LR ≤ −1) |
|---------------------------------------------|-------------------|----------------------------------------|-----------------------------------|
| EXACT | DPLL-b (b >= N), DPLL-b[MOMS, b=10, Δ=UNSAT] | NOISY-EXACT (-0.2), PERCEPTION-NOISE (-0.1) | DPLL-b[MENTION, b=10, Δ=UNSAT] (-3.8), DPLL-b[INDEX, b=10, Δ=UNSAT] (-3.8), BEAM-2 (-1.9), BACKDOOR[k=2,OCC] (-5.7), WALK-k (k=14) (-1.7), MIN-CONFLICTS (k=14) (-3.9), C-UC/STOP (-5.7), C-UC/CONT (-5.7), C-GREEDY (-7.5), POLARITY / ALWAYS-SAT (-7.5), B1 (UP-k, FLP-1) (-7.5), RANDOM (-7.5) |
| DPLL-b (b >= N) | EXACT, DPLL-b[MOMS, b=10, Δ=UNSAT] | NOISY-EXACT (-0.2), PERCEPTION-NOISE (-0.1) | DPLL-b[MENTION, b=10, Δ=UNSAT] (-3.8), DPLL-b[INDEX, b=10, Δ=UNSAT] (-3.8), BEAM-2 (-1.9), BACKDOOR[k=2,OCC] (-5.7), WALK-k (k=14) (-1.7), MIN-CONFLICTS (k=14) (-3.9), C-UC/STOP (-5.7), C-UC/CONT (-5.7), C-GREEDY (-7.5), POLARITY / ALWAYS-SAT (-7.5), B1 (UP-k, FLP-1) (-7.5), RANDOM (-7.5) |
| DPLL-b[MENTION, b=10, Δ=UNSAT] | DPLL-b[INDEX, b=10, Δ=UNSAT] | — | EXACT (-3.8), DPLL-b (b >= N) (-3.8), DPLL-b[MOMS, b=10, Δ=UNSAT] (-3.8), BEAM-2 (-1.9), BACKDOOR[k=2,OCC] (-1.9), WALK-k (k=14) (-4.6), MIN-CONFLICTS (k=14) (-5.6), C-UC/STOP (-1.9), C-UC/CONT (-5.7), C-GREEDY (-7.5), POLARITY / ALWAYS-SAT (-7.5), B1 (UP-k, FLP-1) (-3.8), NOISY-EXACT (-3.9), PERCEPTION-NOISE (-3.8), RANDOM (-7.5) |
| DPLL-b[INDEX, b=10, Δ=UNSAT] | DPLL-b[MENTION, b=10, Δ=UNSAT] | — | EXACT (-3.8), DPLL-b (b >= N) (-3.8), DPLL-b[MOMS, b=10, Δ=UNSAT] (-3.8), BEAM-2 (-1.9), BACKDOOR[k=2,OCC] (-1.9), WALK-k (k=14) (-4.6), MIN-CONFLICTS (k=14) (-5.6), C-UC/STOP (-1.9), C-UC/CONT (-5.7), C-GREEDY (-7.5), POLARITY / ALWAYS-SAT (-7.5), B1 (UP-k, FLP-1) (-3.8), NOISY-EXACT (-3.9), PERCEPTION-NOISE (-3.8), RANDOM (-7.5) |
| DPLL-b[MOMS, b=10, Δ=UNSAT] | EXACT, DPLL-b (b >= N) | NOISY-EXACT (-0.2), PERCEPTION-NOISE (-0.1) | DPLL-b[MENTION, b=10, Δ=UNSAT] (-3.8), DPLL-b[INDEX, b=10, Δ=UNSAT] (-3.8), BEAM-2 (-1.9), BACKDOOR[k=2,OCC] (-5.7), WALK-k (k=14) (-1.7), MIN-CONFLICTS (k=14) (-3.9), C-UC/STOP (-5.7), C-UC/CONT (-5.7), C-GREEDY (-7.5), POLARITY / ALWAYS-SAT (-7.5), B1 (UP-k, FLP-1) (-7.5), RANDOM (-7.5) |
| BEAM-2 | — | — | EXACT (-1.9), DPLL-b (b >= N) (-1.9), DPLL-b[MENTION, b=10, Δ=UNSAT] (-1.9), DPLL-b[INDEX, b=10, Δ=UNSAT] (-1.9), DPLL-b[MOMS, b=10, Δ=UNSAT] (-1.9), BACKDOOR[k=2,OCC] (-3.8), WALK-k (k=14) (-3.1), MIN-CONFLICTS (k=14) (-4.7), C-UC/STOP (-3.8), C-UC/CONT (-5.7), C-GREEDY (-7.5), POLARITY / ALWAYS-SAT (-7.5), B1 (UP-k, FLP-1) (-5.7), NOISY-EXACT (-2.0), PERCEPTION-NOISE (-1.9), RANDOM (-7.5) |
| BACKDOOR[k=2,OCC] | C-UC/STOP | — | EXACT (-5.7), DPLL-b (b >= N) (-5.7), DPLL-b[MENTION, b=10, Δ=UNSAT] (-1.9), DPLL-b[INDEX, b=10, Δ=UNSAT] (-1.9), DPLL-b[MOMS, b=10, Δ=UNSAT] (-5.7), BEAM-2 (-3.8), WALK-k (k=14) (-5.9), MIN-CONFLICTS (k=14) (-6.5), C-UC/CONT (-5.7), C-GREEDY (-7.5), POLARITY / ALWAYS-SAT (-7.5), B1 (UP-k, FLP-1) (-1.9), NOISY-EXACT (-5.7), PERCEPTION-NOISE (-5.7), RANDOM (-7.5) |
| WALK-k (k=14) | — | MIN-CONFLICTS (k=14) (-0.2) | EXACT (-5.0), DPLL-b (b >= N) (-5.0), DPLL-b[MENTION, b=10, Δ=UNSAT] (-5.0), DPLL-b[INDEX, b=10, Δ=UNSAT] (-5.0), DPLL-b[MOMS, b=10, Δ=UNSAT] (-5.0), BEAM-2 (-5.0), BACKDOOR[k=2,OCC] (-5.0), C-UC/STOP (-5.0), C-GREEDY (-5.0), POLARITY / ALWAYS-SAT (-6.9), B1 (UP-k, FLP-1) (-6.9), NOISY-EXACT (-3.0), PERCEPTION-NOISE (-2.8), RANDOM (-6.9) |
| MIN-CONFLICTS (k=14) | — | WALK-k (k=14) (-0.7) | EXACT (-7.4), DPLL-b (b >= N) (-7.4), DPLL-b[MENTION, b=10, Δ=UNSAT] (-7.4), DPLL-b[INDEX, b=10, Δ=UNSAT] (-7.4), DPLL-b[MOMS, b=10, Δ=UNSAT] (-7.4), BEAM-2 (-7.4), BACKDOOR[k=2,OCC] (-7.4), C-UC/STOP (-7.4), C-UC/CONT (-1.7), C-GREEDY (-5.5), POLARITY / ALWAYS-SAT (-7.4), B1 (UP-k, FLP-1) (-7.4), NOISY-EXACT (-4.6), PERCEPTION-NOISE (-4.7), RANDOM (-7.4) |
| C-UC/STOP | BACKDOOR[k=2,OCC] | — | EXACT (-5.7), DPLL-b (b >= N) (-5.7), DPLL-b[MENTION, b=10, Δ=UNSAT] (-1.9), DPLL-b[INDEX, b=10, Δ=UNSAT] (-1.9), DPLL-b[MOMS, b=10, Δ=UNSAT] (-5.7), BEAM-2 (-3.8), WALK-k (k=14) (-5.9), MIN-CONFLICTS (k=14) (-6.5), C-UC/CONT (-5.7), C-GREEDY (-7.5), POLARITY / ALWAYS-SAT (-7.5), B1 (UP-k, FLP-1) (-1.9), NOISY-EXACT (-5.7), PERCEPTION-NOISE (-5.7), RANDOM (-7.5) |
| C-UC/CONT | — | WALK-k (k=14) (-0.7), MIN-CONFLICTS (k=14) (-0.9) | EXACT (-5.7), DPLL-b (b >= N) (-5.7), DPLL-b[MENTION, b=10, Δ=UNSAT] (-5.7), DPLL-b[INDEX, b=10, Δ=UNSAT] (-5.7), DPLL-b[MOMS, b=10, Δ=UNSAT] (-5.7), BEAM-2 (-5.7), BACKDOOR[k=2,OCC] (-5.7), C-UC/STOP (-5.7), C-GREEDY (-5.7), POLARITY / ALWAYS-SAT (-7.5), B1 (UP-k, FLP-1) (-7.5), NOISY-EXACT (-3.7), PERCEPTION-NOISE (-3.5), RANDOM (-7.5) |
| C-GREEDY | — | — | EXACT (-7.5), DPLL-b (b >= N) (-7.5), DPLL-b[MENTION, b=10, Δ=UNSAT] (-7.5), DPLL-b[INDEX, b=10, Δ=UNSAT] (-7.5), DPLL-b[MOMS, b=10, Δ=UNSAT] (-7.5), BEAM-2 (-7.5), BACKDOOR[k=2,OCC] (-7.5), WALK-k (k=14) (-5.8), MIN-CONFLICTS (k=14) (-5.7), C-UC/STOP (-7.5), C-UC/CONT (-5.7), POLARITY / ALWAYS-SAT (-1.9), B1 (UP-k, FLP-1) (-7.5), NOISY-EXACT (-4.8), PERCEPTION-NOISE (-6.8), RANDOM (-1.9) |
| POLARITY / ALWAYS-SAT | RANDOM | — | EXACT (-7.5), DPLL-b (b >= N) (-7.5), DPLL-b[MENTION, b=10, Δ=UNSAT] (-7.5), DPLL-b[INDEX, b=10, Δ=UNSAT] (-7.5), DPLL-b[MOMS, b=10, Δ=UNSAT] (-7.5), BEAM-2 (-7.5), BACKDOOR[k=2,OCC] (-7.5), WALK-k (k=14) (-7.5), MIN-CONFLICTS (k=14) (-7.5), C-UC/STOP (-7.5), C-UC/CONT (-7.5), C-GREEDY (-1.9), B1 (UP-k, FLP-1) (-7.5), NOISY-EXACT (-4.8), PERCEPTION-NOISE (-7.5) |
| B1 (UP-k, FLP-1) | — | — | EXACT (-7.5), DPLL-b (b >= N) (-7.5), DPLL-b[MENTION, b=10, Δ=UNSAT] (-3.8), DPLL-b[INDEX, b=10, Δ=UNSAT] (-3.8), DPLL-b[MOMS, b=10, Δ=UNSAT] (-7.5), BEAM-2 (-5.7), BACKDOOR[k=2,OCC] (-1.9), WALK-k (k=14) (-7.5), MIN-CONFLICTS (k=14) (-7.5), C-UC/STOP (-1.9), C-UC/CONT (-7.5), C-GREEDY (-7.5), POLARITY / ALWAYS-SAT (-7.5), NOISY-EXACT (-7.5), PERCEPTION-NOISE (-7.5), RANDOM (-7.5) |
| NOISY-EXACT | — | — | DPLL-b[MENTION, b=10, Δ=UNSAT] (-3.6), DPLL-b[INDEX, b=10, Δ=UNSAT] (-3.6), BEAM-2 (-1.7), BACKDOOR[k=2,OCC] (-5.5), WALK-k (k=14) (-1.5), MIN-CONFLICTS (k=14) (-3.7), C-UC/STOP (-5.5), C-UC/CONT (-5.5), C-GREEDY (-7.4), POLARITY / ALWAYS-SAT (-7.4), B1 (UP-k, FLP-1) (-7.4), RANDOM (-7.3) |
| PERCEPTION-NOISE | — | NOISY-EXACT (-0.1) | DPLL-b[MENTION, b=10, Δ=UNSAT] (-3.7), DPLL-b[INDEX, b=10, Δ=UNSAT] (-3.7), BEAM-2 (-1.8), BACKDOOR[k=2,OCC] (-5.6), WALK-k (k=14) (-1.6), MIN-CONFLICTS (k=14) (-3.8), C-UC/STOP (-5.6), C-UC/CONT (-5.6), C-GREEDY (-7.5), POLARITY / ALWAYS-SAT (-7.5), B1 (UP-k, FLP-1) (-7.5), RANDOM (-7.4) |
| RANDOM | POLARITY / ALWAYS-SAT | — | EXACT (-7.5), DPLL-b (b >= N) (-7.5), DPLL-b[MENTION, b=10, Δ=UNSAT] (-7.5), DPLL-b[INDEX, b=10, Δ=UNSAT] (-7.5), DPLL-b[MOMS, b=10, Δ=UNSAT] (-7.5), BEAM-2 (-7.5), BACKDOOR[k=2,OCC] (-7.5), WALK-k (k=14) (-7.5), MIN-CONFLICTS (k=14) (-7.5), C-UC/STOP (-7.5), C-UC/CONT (-7.5), C-GREEDY (-1.9), B1 (UP-k, FLP-1) (-7.5), NOISY-EXACT (-4.8), PERCEPTION-NOISE (-7.5) |

**Not distinguished by this set:** BACKDOOR-k vs DPLL-b: see E3. PERCEPTION-NOISE: see E6.

### E2.1: W low × F low

- **Question tested:** At fixed n and α, does failure follow DPLL work (D) or local-search difficulty (F)?
- **Controlled:** n = 14, m = 60; all SAT; #solutions near the pool median; same template
- **Varied:** W low (median DPLL work over 6 variants = 1380); F low (WalkSAT median flips = 11)
- **Ground truth:** `{"answer": "SAT", "n_solutions": 4, "solutions": ["x1=0 x2=1 x3=0 x4=1 x5=1 x6=0 x7=0 x8=1 x9=0 x10=0 x11=0 x12=0 x13=1 x14=0", "x1=1 x2=0 x3=0 x4=0 x5=1 x6=0 x7=1 x8=1 x9=0 x10=0 x11=0 x12=1 x13=0 x14=1", "..."]}`
- **Notes:** Dev-scale example; the study uses n_Q ≈ n*_BE with 100 items per quadrant, matched on the covariates listed in §2.7 E2.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x14. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (NOT x3 OR x9 OR NOT x12)
C2: (NOT x2 OR x4 OR NOT x13)
C3: (NOT x4 OR x11 OR NOT x12)
C4: (x5 OR NOT x10 OR x14)
C5: (x3 OR NOT x10 OR NOT x14)
C6: (x1 OR NOT x3 OR NOT x12)
C7: (NOT x4 OR NOT x6 OR x14)
C8: (x4 OR x12 OR x13)
C9: (x7 OR x10 OR NOT x11)
C10: (NOT x1 OR NOT x4 OR NOT x7)
C11: (NOT x5 OR x7 OR x13)
C12: (x7 OR x8 OR x14)
C13: (x6 OR x8 OR NOT x14)
C14: (NOT x3 OR NOT x12 OR NOT x14)
C15: (x3 OR NOT x5 OR x8)
C16: (x5 OR NOT x6 OR x14)
C17: (x3 OR x5 OR NOT x14)
C18: (x1 OR x3 OR NOT x11)
C19: (NOT x8 OR NOT x10 OR NOT x11)
C20: (NOT x6 OR NOT x9 OR x13)
C21: (x1 OR x2 OR x6)
C22: (NOT x1 OR NOT x7 OR NOT x13)
C23: (x8 OR x10 OR NOT x14)
C24: (NOT x5 OR NOT x10 OR x12)
C25: (NOT x2 OR NOT x11 OR x13)
C26: (x7 OR x13 OR x14)
C27: (NOT x2 OR NOT x7 OR NOT x12)
C28: (NOT x1 OR x5 OR x10)
C29: (NOT x1 OR x7 OR NOT x8)
C30: (x3 OR x6 OR NOT x11)
C31: (x1 OR NOT x3 OR x9)
C32: (NOT x1 OR x2 OR NOT x13)
C33: (x2 OR NOT x7 OR x14)
C34: (x1 OR NOT x3 OR NOT x4)
C35: (x2 OR NOT x4 OR x7)
C36: (x9 OR NOT x10 OR NOT x12)
C37: (x1 OR x2 OR x4)
C38: (NOT x1 OR x2 OR NOT x9)
C39: (NOT x6 OR x8 OR NOT x12)
C40: (x2 OR x6 OR x8)
C41: (x7 OR NOT x9 OR NOT x12)
C42: (NOT x2 OR NOT x3 OR x13)
C43: (x5 OR x10 OR NOT x11)
C44: (x3 OR NOT x11 OR x12)
C45: (x4 OR NOT x9 OR x11)
C46: (NOT x1 OR NOT x6 OR x11)
C47: (x1 OR NOT x2 OR NOT x3)
C48: (x2 OR x4 OR x5)
C49: (x10 OR NOT x11 OR NOT x14)
C50: (x3 OR NOT x4 OR NOT x9)
C51: (x1 OR NOT x4 OR NOT x7)
C52: (NOT x3 OR NOT x5 OR NOT x11)
C53: (x4 OR NOT x6 OR x7)
C54: (x3 OR x5 OR NOT x13)
C55: (NOT x3 OR x8 OR x11)
C56: (NOT x4 OR x6 OR NOT x14)
C57: (x4 OR NOT x10 OR NOT x12)
C58: (x2 OR x3 OR x8)
C59: (NOT x2 OR x8 OR x10)
C60: (NOT x4 OR x8 OR NOT x9)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 4 solutions | π_EXACT = ceiling share; near-ceiling accuracy in all four cells means the level should move up | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=1 x2=1 x3=1 x4=1 x5=0 x6=1 x7=0 x8=0 x9=0 x10=1 x11=1 x12=0 x13=1 x14=1 after N = 4 nodes (W = 1380); MENTION,MAJ: N = 3. If b < N: the default (UNSAT, or FILL = violates [2, 22, 24] at b = N/2). | cell W low: π_DPLL estimated jointly with π_F from the W and F_ref effects (feature-dependent weights π_h(log W, log F_ref)); power 0.9 to detect a 15 pp W effect, i.e. π_DPLL ≥ 0.2 at the W contrast; a null W effect bounds π_DPLL ≤ 0.15 (upper 95%) | MOMS,MAJ reference: DEC = 3, BT = 1, CONF = 1, PROP = 18; first decisions (var, value) = [(3, 1), (1, 1), (7, 1)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: SAT; w=2: SAT; w=4: SAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: SAT; k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: SAT; k=3,MENTION: UNSAT (default); k=3,INDEX: SAT | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=14) = 0.61, P(success / k=70) = 0.99, P(success / k=350) = 1.00; modal failure at k=14: violates [2], LM0=True, Hamming to nearest solution = 2 | cell F low: π_F from the F_ref effect at fixed W; same power; a null F_ref effect bounds π_F ≤ 0.15 (upper 95%) | FULL candidate, VIOL list, FLIP moves; DEC <= 1; #FLIP about the WalkSAT median of 11 |
| MIN-CONFLICTS | P(success / k=14) = 0.14, P(success / k=70) = 0.51, P(success / k=350) = 0.62 | cell F low: π_F from the F_ref effect at fixed W; same power; a null F_ref effect bounds π_F ≤ 0.15 (upper 95%) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C41); MENTION,MAJ: SAT; MOMS,TRUE: UNSAT (dead end at C33); MOMS,MAJ: UNSAT (dead end at C33) / CONT violates: MENTION,TRUE: [19, 29, 41, 52]; MENTION,MAJ: []; MOMS,TRUE: [33, 38, 52]; MOMS,MAJ: [33, 38, 52] | π_C from residual errors not explained by W or F_ref (g(x) is balanced across cells) | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=0 x2=1 x3=1 x4=0 x5=1 x6=1 x7=1 x8=1 x9=0 x10=1 x11=0 x12=0 x13=1 x14=1 (violates [2, 24, 31, 47]) | π_C from residual errors not explained by W or F_ref (g(x) is balanced across cells) | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=1 x4=0 x5=1 x6=0 x7=1 x8=1 x9=0 x10=1 x11=0 x12=0 x13=1 x14=0 (violates [2, 22, 24]) | π_POLARITY ≈ 0 expected (polarity agreement matched across cells) | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.871 (eps=1e-4) or 0.251 (eps=1e-3), W = 1380; otherwise a slip (one missed clause, or a spurious conflict) | π_NE vs π_DPLL decided by b̂ across budgets: NOISY-DPLL(b, ε) posterior on log b; b̂ flat across 2k/8k/BE moves weight from DPLL-b to NE | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| PERCEPTION-NOISE | exact answer to a misread formula; 8% of single sign misreads give a wrong answer here | π_PERCEPTION estimated in E6 (re-check, same-clause repeats); here only its budget-flat error rate | the trace quotes the violated clause with a sign or index error |
| RANDOM | uniform assignment; P(correct) = 0.0002 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), DPLL-b[MENTION, b=10, Δ=UNSAT], DPLL-b[INDEX, b=10, Δ=UNSAT], DPLL-b[MOMS, b=10, Δ=UNSAT], BEAM-2, BACKDOOR[k=2,OCC], C-UC/STOP, C-UC/CONT; pushes down MIN-CONFLICTS (k=14) (LR 0.156), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *near-miss (infeasible, LM0, V<=3)*: best fit MIN-CONFLICTS (k=14); pushes down EXACT (LR 0.015), DPLL-b (b >= N) (LR 0.015), DPLL-b[MENTION, b=10, Δ=UNSAT] (LR 0.015), DPLL-b[INDEX, b=10, Δ=UNSAT] (LR 0.015), DPLL-b[MOMS, b=10, Δ=UNSAT] (LR 0.015), BEAM-2 (LR 0.015), BACKDOOR[k=2,OCC] (LR 0.015), C-UC/STOP (LR 0.015), C-UC/CONT (LR 0.015), C-GREEDY (LR 0.015), POLARITY / ALWAYS-SAT (LR 0.015), B1 (UP-k, FLP-1) (LR 0.015), NOISY-EXACT (LR 0.089), PERCEPTION-NOISE (LR 0.047), RANDOM (LR 0.015)
- *infeasible (other)*: best fit C-GREEDY, POLARITY / ALWAYS-SAT; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=10, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=14) (LR 0.013), MIN-CONFLICTS (k=14) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.077), PERCEPTION-NOISE (LR 0.013)
- *UNSAT/UNKNOWN*: best fit B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=10, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=14) (LR 0.013), MIN-CONFLICTS (k=14) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), PERCEPTION-NOISE (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=8, W=1980; MENTION,MAJ: N=3, W=900; INDEX,TRUE: N=3, W=900; INDEX,MAJ: N=3, W=900; MOMS,TRUE: N=4, W=1380; MOMS,MAJ: N=4, W=1380. Every member's full output is in the JSONL `predictions` field.

### E2.2: W low × F high

- **Question tested:** At fixed n and α, does failure follow DPLL work (D) or local-search difficulty (F)?
- **Controlled:** n = 14, m = 60; all SAT; #solutions near the pool median; same template
- **Varied:** W low (median DPLL work over 6 variants = 1380); F high (WalkSAT median flips = 35)
- **Ground truth:** `{"answer": "SAT", "n_solutions": 4, "solutions": ["x1=0 x2=0 x3=0 x4=0 x5=1 x6=1 x7=0 x8=0 x9=1 x10=0 x11=1 x12=1 x13=0 x14=0", "x1=1 x2=0 x3=0 x4=0 x5=1 x6=1 x7=0 x8=0 x9=1 x10=0 x11=1 x12=1 x13=0 x14=0", "..."]}`
- **Notes:** Dev-scale example; the study uses n_Q ≈ n*_BE with 100 items per quadrant, matched on the covariates listed in §2.7 E2.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x14. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (NOT x5 OR NOT x7 OR x10)
C2: (NOT x3 OR x9 OR x11)
C3: (NOT x4 OR x9 OR NOT x12)
C4: (x7 OR x11 OR x14)
C5: (x7 OR x12 OR x13)
C6: (NOT x4 OR NOT x5 OR x7)
C7: (x1 OR NOT x10 OR x12)
C8: (x5 OR x6 OR NOT x8)
C9: (x1 OR NOT x5 OR x6)
C10: (NOT x3 OR x8 OR x9)
C11: (x1 OR NOT x2 OR NOT x14)
C12: (NOT x6 OR x7 OR x11)
C13: (NOT x1 OR x5 OR NOT x14)
C14: (x8 OR NOT x9 OR NOT x10)
C15: (x7 OR x9 OR x14)
C16: (x2 OR NOT x3 OR NOT x5)
C17: (x3 OR x9 OR NOT x11)
C18: (x3 OR x9 OR NOT x12)
C19: (NOT x4 OR NOT x5 OR x12)
C20: (NOT x6 OR x9 OR NOT x11)
C21: (NOT x8 OR NOT x11 OR NOT x12)
C22: (x9 OR NOT x10 OR x12)
C23: (x6 OR x8 OR NOT x13)
C24: (x7 OR NOT x11 OR NOT x14)
C25: (NOT x3 OR NOT x10 OR NOT x12)
C26: (NOT x2 OR x6 OR x13)
C27: (NOT x1 OR x9 OR x11)
C28: (x6 OR x10 OR NOT x14)
C29: (NOT x7 OR NOT x8 OR NOT x11)
C30: (x6 OR NOT x10 OR x14)
C31: (NOT x4 OR NOT x8 OR NOT x12)
C32: (x2 OR x6 OR NOT x9)
C33: (NOT x2 OR x4 OR NOT x12)
C34: (NOT x1 OR x11 OR NOT x13)
C35: (x4 OR x5 OR x14)
C36: (x3 OR x6 OR NOT x10)
C37: (NOT x2 OR NOT x5 OR NOT x10)
C38: (NOT x2 OR x8 OR x9)
C39: (NOT x3 OR x7 OR NOT x11)
C40: (NOT x8 OR x13 OR x14)
C41: (NOT x6 OR NOT x8 OR NOT x9)
C42: (x3 OR x11 OR x13)
C43: (x4 OR x6 OR x14)
C44: (x9 OR NOT x10 OR x13)
C45: (x5 OR NOT x6 OR x11)
C46: (NOT x3 OR NOT x6 OR NOT x11)
C47: (NOT x3 OR NOT x5 OR x13)
C48: (NOT x2 OR NOT x6 OR x8)
C49: (NOT x1 OR NOT x9 OR x12)
C50: (NOT x1 OR x3 OR NOT x7)
C51: (x2 OR NOT x4 OR x5)
C52: (NOT x1 OR x2 OR x5)
C53: (x5 OR x8 OR NOT x12)
C54: (NOT x6 OR x10 OR x12)
C55: (x1 OR x2 OR x9)
C56: (x3 OR NOT x4 OR x13)
C57: (NOT x3 OR NOT x7 OR NOT x13)
C58: (NOT x3 OR x5 OR NOT x10)
C59: (NOT x2 OR NOT x5 OR NOT x12)
C60: (x1 OR NOT x3 OR NOT x10)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 4 solutions | π_EXACT = ceiling share; near-ceiling accuracy in all four cells means the level should move up | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=0 x2=0 x3=0 x4=0 x5=1 x6=1 x7=0 x8=0 x9=1 x10=0 x11=1 x12=1 x13=1 x14=0 after N = 3 nodes (W = 780); MENTION,MAJ: N = 7. If b < N: the default (UNSAT, or FILL = violates [1, 29, 41, 54] at b = N/2). | cell W low: π_DPLL estimated jointly with π_F from the W and F_ref effects (feature-dependent weights π_h(log W, log F_ref)); power 0.9 to detect a 15 pp W effect, i.e. π_DPLL ≥ 0.2 at the W contrast; a null W effect bounds π_DPLL ≤ 0.15 (upper 95%) | MOMS,MAJ reference: DEC = 3, BT = 0, CONF = 0, PROP = 9; first decisions (var, value) = [(5, 1), (2, 0), (9, 1)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: SAT; w=2: SAT; w=4: SAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: SAT; k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: SAT | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=14) = 0.26, P(success / k=70) = 0.78, P(success / k=350) = 1.00; modal failure at k=14: violates [41], LM0=True, Hamming to nearest solution = 5 | cell F high: π_F from the F_ref effect at fixed W; same power; a null F_ref effect bounds π_F ≤ 0.15 (upper 95%) | FULL candidate, VIOL list, FLIP moves; DEC <= 1; #FLIP about the WalkSAT median of 35 |
| MIN-CONFLICTS | P(success / k=14) = 0.08, P(success / k=70) = 0.36, P(success / k=350) = 0.63 | cell F high: π_F from the F_ref effect at fixed W; same power; a null F_ref effect bounds π_F ≤ 0.15 (upper 95%) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C41); MENTION,MAJ: UNSAT (dead end at C41); MOMS,TRUE: UNSAT (dead end at C43); MOMS,MAJ: SAT / CONT violates: MENTION,TRUE: [41]; MENTION,MAJ: [41]; MOMS,TRUE: [43, 49]; MOMS,MAJ: [] | π_C from residual errors not explained by W or F_ref (g(x) is balanced across cells) | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=0 x3=0 x4=0 x5=1 x6=1 x7=1 x8=0 x9=1 x10=0 x11=1 x12=0 x13=1 x14=1 (violates [1, 49, 50, 54]) | π_C from residual errors not explained by W or F_ref (g(x) is balanced across cells) | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=0 x2=0 x3=0 x4=0 x5=1 x6=1 x7=1 x8=1 x9=1 x10=0 x11=1 x12=0 x13=1 x14=1 (violates [1, 29, 41, 54]) | π_POLARITY ≈ 0 expected (polarity agreement matched across cells) | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.925 (eps=1e-4) or 0.458 (eps=1e-3), W = 780; otherwise a slip (one missed clause, or a spurious conflict) | π_NE vs π_DPLL decided by b̂ across budgets: NOISY-DPLL(b, ε) posterior on log b; b̂ flat across 2k/8k/BE moves weight from DPLL-b to NE | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| PERCEPTION-NOISE | exact answer to a misread formula; 18% of single sign misreads give a wrong answer here | π_PERCEPTION estimated in E6 (re-check, same-clause repeats); here only its budget-flat error rate | the trace quotes the violated clause with a sign or index error |
| RANDOM | uniform assignment; P(correct) = 0.0002 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), DPLL-b[MENTION, b=10, Δ=UNSAT], DPLL-b[INDEX, b=10, Δ=UNSAT], DPLL-b[MOMS, b=10, Δ=UNSAT], BEAM-2; pushes down BACKDOOR[k=2,OCC] (LR 0.013), MIN-CONFLICTS (k=14) (LR 0.092), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *near-miss (infeasible, LM0, V<=3)*: best fit C-UC/CONT; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=10, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), C-UC/STOP (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.05), PERCEPTION-NOISE (LR 0.074), RANDOM (LR 0.013)
- *infeasible (other)*: best fit C-GREEDY, POLARITY / ALWAYS-SAT; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=10, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=14) (LR 0.013), MIN-CONFLICTS (k=14) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.05), PERCEPTION-NOISE (LR 0.013)
- *UNSAT/UNKNOWN*: best fit BACKDOOR[k=2,OCC], C-UC/STOP, B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=10, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), WALK-k (k=14) (LR 0.013), MIN-CONFLICTS (k=14) (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), PERCEPTION-NOISE (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=9, W=2220; MENTION,MAJ: N=7, W=1320; INDEX,TRUE: N=14, W=3120; INDEX,MAJ: N=2, W=840; MOMS,TRUE: N=4, W=1380; MOMS,MAJ: N=3, W=780. Every member's full output is in the JSONL `predictions` field.

### E2.3: W high × F low

- **Question tested:** At fixed n and α, does failure follow DPLL work (D) or local-search difficulty (F)?
- **Controlled:** n = 14, m = 60; all SAT; #solutions near the pool median; same template
- **Varied:** W high (median DPLL work over 6 variants = 2580); F low (WalkSAT median flips = 14)
- **Ground truth:** `{"answer": "SAT", "n_solutions": 3, "solutions": ["x1=1 x2=1 x3=0 x4=0 x5=1 x6=0 x7=1 x8=1 x9=0 x10=0 x11=0 x12=0 x13=0 x14=1", "x1=1 x2=1 x3=0 x4=0 x5=1 x6=0 x7=0 x8=1 x9=0 x10=0 x11=0 x12=0 x13=1 x14=1", "..."]}`
- **Notes:** Dev-scale example; the study uses n_Q ≈ n*_BE with 100 items per quadrant, matched on the covariates listed in §2.7 E2.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x14. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (NOT x2 OR NOT x11 OR x12)
C2: (NOT x4 OR NOT x8 OR x11)
C3: (x1 OR x3 OR NOT x7)
C4: (x2 OR x4 OR NOT x11)
C5: (x1 OR NOT x9 OR x13)
C6: (x8 OR NOT x9 OR NOT x13)
C7: (x10 OR NOT x11 OR x12)
C8: (x10 OR NOT x12 OR x13)
C9: (NOT x2 OR NOT x4 OR NOT x5)
C10: (x2 OR x4 OR NOT x5)
C11: (x7 OR x10 OR x13)
C12: (x6 OR NOT x9 OR x11)
C13: (x1 OR NOT x7 OR NOT x14)
C14: (NOT x6 OR x9 OR x13)
C15: (NOT x2 OR NOT x3 OR x13)
C16: (NOT x4 OR NOT x5 OR NOT x8)
C17: (NOT x2 OR NOT x13 OR x14)
C18: (NOT x2 OR NOT x3 OR x10)
C19: (x5 OR x6 OR NOT x9)
C20: (x5 OR NOT x7 OR x13)
C21: (x1 OR NOT x4 OR x14)
C22: (x2 OR x11 OR NOT x13)
C23: (x1 OR NOT x7 OR x13)
C24: (x1 OR NOT x5 OR NOT x11)
C25: (NOT x10 OR NOT x13 OR x14)
C26: (NOT x1 OR NOT x2 OR NOT x11)
C27: (NOT x5 OR NOT x6 OR NOT x14)
C28: (x5 OR x8 OR NOT x14)
C29: (NOT x6 OR NOT x13 OR NOT x14)
C30: (x4 OR NOT x5 OR x14)
C31: (x1 OR x8 OR NOT x11)
C32: (x2 OR NOT x8 OR NOT x13)
C33: (x4 OR NOT x10 OR x13)
C34: (x1 OR NOT x7 OR x10)
C35: (x1 OR x7 OR x11)
C36: (x5 OR NOT x8 OR x12)
C37: (x1 OR NOT x3 OR NOT x13)
C38: (NOT x3 OR NOT x7 OR x13)
C39: (NOT x4 OR x10 OR x13)
C40: (x1 OR x2 OR NOT x7)
C41: (x8 OR x12 OR x14)
C42: (NOT x9 OR NOT x10 OR x12)
C43: (x4 OR NOT x10 OR NOT x13)
C44: (NOT x1 OR x7 OR x8)
C45: (x4 OR x8 OR NOT x13)
C46: (NOT x1 OR NOT x9 OR x12)
C47: (x5 OR NOT x6 OR NOT x12)
C48: (x5 OR x9 OR NOT x10)
C49: (x7 OR NOT x10 OR x14)
C50: (NOT x2 OR NOT x10 OR x14)
C51: (NOT x1 OR x9 OR NOT x12)
C52: (x1 OR x5 OR NOT x14)
C53: (x3 OR NOT x7 OR NOT x9)
C54: (NOT x5 OR NOT x9 OR NOT x14)
C55: (x2 OR x8 OR x14)
C56: (x3 OR x4 OR x8)
C57: (NOT x1 OR NOT x11 OR NOT x12)
C58: (x4 OR x9 OR x14)
C59: (NOT x3 OR x5 OR NOT x11)
C60: (NOT x1 OR NOT x4 OR x8)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 3 solutions | π_EXACT = ceiling share; near-ceiling accuracy in all four cells means the level should move up | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=1 x2=1 x3=0 x4=0 x5=1 x6=0 x7=0 x8=1 x9=0 x10=0 x11=0 x12=0 x13=1 x14=1 after N = 5 nodes (W = 840); MENTION,MAJ: N = 26. If b < N: the default (UNSAT, or FILL = violates [2, 16, 22, 32, 51] at b = N/2). | cell W high: π_DPLL estimated jointly with π_F from the W and F_ref effects (feature-dependent weights π_h(log W, log F_ref)); power 0.9 to detect a 15 pp W effect, i.e. π_DPLL ≥ 0.2 at the W contrast; a null W effect bounds π_DPLL ≤ 0.15 (upper 95%) | MOMS,MAJ reference: DEC = 5, BT = 0, CONF = 0, PROP = 8; first decisions (var, value) = [(13, 1), (14, 1), (8, 1)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: SAT; w=2: SAT; w=4: SAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: UNSAT (default) | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=14) = 0.38, P(success / k=70) = 0.93, P(success / k=350) = 1.00; modal failure at k=14: violates [16], LM0=True, Hamming to nearest solution = 5 | cell F low: π_F from the F_ref effect at fixed W; same power; a null F_ref effect bounds π_F ≤ 0.15 (upper 95%) | FULL candidate, VIOL list, FLIP moves; DEC <= 1; #FLIP about the WalkSAT median of 14 |
| MIN-CONFLICTS | P(success / k=14) = 0.10, P(success / k=70) = 0.39, P(success / k=350) = 0.49 | cell F low: π_F from the F_ref effect at fixed W; same power; a null F_ref effect bounds π_F ≤ 0.15 (upper 95%) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C52); MENTION,MAJ: UNSAT (dead end at C35); MOMS,TRUE: SAT; MOMS,MAJ: SAT / CONT violates: MENTION,TRUE: [52]; MENTION,MAJ: [35]; MOMS,TRUE: []; MOMS,MAJ: [] | π_C from residual errors not explained by W or F_ref (g(x) is balanced across cells) | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=0 x3=1 x4=1 x5=0 x6=1 x7=1 x8=1 x9=1 x10=0 x11=0 x12=1 x13=1 x14=0 (violates [2, 22, 32, 47]) | π_C from residual errors not explained by W or F_ref (g(x) is balanced across cells) | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=0 x3=0 x4=1 x5=1 x6=0 x7=0 x8=1 x9=0 x10=0 x11=0 x12=1 x13=1 x14=1 (violates [2, 16, 22, 32, 51]) | π_POLARITY ≈ 0 expected (polarity agreement matched across cells) | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.919 (eps=1e-4) or 0.432 (eps=1e-3), W = 840; otherwise a slip (one missed clause, or a spurious conflict) | π_NE vs π_DPLL decided by b̂ across budgets: NOISY-DPLL(b, ε) posterior on log b; b̂ flat across 2k/8k/BE moves weight from DPLL-b to NE | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| PERCEPTION-NOISE | exact answer to a misread formula; 13% of single sign misreads give a wrong answer here | π_PERCEPTION estimated in E6 (re-check, same-clause repeats); here only its budget-flat error rate | the trace quotes the violated clause with a sign or index error |
| RANDOM | uniform assignment; P(correct) = 0.0002 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), DPLL-b[MOMS, b=10, Δ=UNSAT], BEAM-2; pushes down DPLL-b[MENTION, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=10, Δ=UNSAT] (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), MIN-CONFLICTS (k=14) (LR 0.107), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *near-miss (infeasible, LM0, V<=3)*: best fit C-UC/CONT; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=10, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), C-UC/STOP (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.053), PERCEPTION-NOISE (LR 0.057), RANDOM (LR 0.013)
- *infeasible (other)*: best fit C-GREEDY, POLARITY / ALWAYS-SAT; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=10, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=14) (LR 0.013), MIN-CONFLICTS (k=14) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.053), PERCEPTION-NOISE (LR 0.013)
- *UNSAT/UNKNOWN*: best fit DPLL-b[MENTION, b=10, Δ=UNSAT], DPLL-b[INDEX, b=10, Δ=UNSAT], BACKDOOR[k=2,OCC], C-UC/STOP, B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MOMS, b=10, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), WALK-k (k=14) (LR 0.013), MIN-CONFLICTS (k=14) (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), PERCEPTION-NOISE (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=19, W=3240; MENTION,MAJ: N=26, W=4860; INDEX,TRUE: N=10, W=1560; INDEX,MAJ: N=15, W=2580; MOMS,TRUE: N=5, W=840; MOMS,MAJ: N=5, W=840. Every member's full output is in the JSONL `predictions` field.

### E2.4: W high × F high

- **Question tested:** At fixed n and α, does failure follow DPLL work (D) or local-search difficulty (F)?
- **Controlled:** n = 14, m = 60; all SAT; #solutions near the pool median; same template
- **Varied:** W high (median DPLL work over 6 variants = 4320); F high (WalkSAT median flips = 54)
- **Ground truth:** `{"answer": "SAT", "n_solutions": 3, "solutions": ["x1=0 x2=1 x3=1 x4=0 x5=0 x6=0 x7=0 x8=0 x9=1 x10=1 x11=1 x12=0 x13=0 x14=1", "x1=0 x2=1 x3=1 x4=0 x5=0 x6=0 x7=0 x8=0 x9=1 x10=1 x11=1 x12=1 x13=0 x14=1", "..."]}`
- **Notes:** Dev-scale example; the study uses n_Q ≈ n*_BE with 100 items per quadrant, matched on the covariates listed in §2.7 E2.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x14. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x1 OR NOT x8 OR NOT x13)
C2: (NOT x3 OR NOT x4 OR NOT x11)
C3: (x3 OR x6 OR x14)
C4: (NOT x1 OR NOT x12 OR NOT x13)
C5: (NOT x1 OR NOT x3 OR x7)
C6: (x5 OR x8 OR x9)
C7: (x2 OR NOT x3 OR NOT x9)
C8: (x3 OR x8 OR x11)
C9: (NOT x6 OR x9 OR NOT x13)
C10: (x6 OR NOT x7 OR x13)
C11: (NOT x3 OR NOT x6 OR NOT x13)
C12: (x7 OR x8 OR x14)
C13: (NOT x2 OR NOT x6 OR x8)
C14: (NOT x2 OR x3 OR NOT x13)
C15: (x5 OR NOT x8 OR NOT x11)
C16: (x2 OR NOT x13 OR NOT x14)
C17: (x5 OR x9 OR NOT x11)
C18: (NOT x1 OR x7 OR NOT x12)
C19: (x1 OR x2 OR x14)
C20: (x4 OR NOT x5 OR NOT x14)
C21: (x1 OR NOT x5 OR NOT x10)
C22: (NOT x6 OR x7 OR x13)
C23: (x3 OR NOT x13 OR NOT x14)
C24: (x3 OR NOT x5 OR NOT x8)
C25: (NOT x1 OR x3 OR x6)
C26: (x8 OR x12 OR NOT x13)
C27: (NOT x3 OR x9 OR NOT x11)
C28: (x6 OR x8 OR x9)
C29: (x1 OR x11 OR NOT x14)
C30: (x1 OR NOT x13 OR x14)
C31: (x2 OR x10 OR x11)
C32: (NOT x1 OR x2 OR x10)
C33: (x3 OR x11 OR x14)
C34: (NOT x10 OR x11 OR NOT x14)
C35: (NOT x8 OR x10 OR NOT x13)
C36: (NOT x2 OR NOT x9 OR x10)
C37: (NOT x4 OR NOT x9 OR x14)
C38: (NOT x4 OR x9 OR x14)
C39: (NOT x4 OR NOT x7 OR x11)
C40: (NOT x5 OR x7 OR NOT x10)
C41: (x3 OR x5 OR x8)
C42: (NOT x7 OR NOT x8 OR x10)
C43: (NOT x1 OR NOT x3 OR NOT x4)
C44: (x1 OR x10 OR NOT x13)
C45: (NOT x7 OR NOT x8 OR NOT x14)
C46: (NOT x1 OR x3 OR NOT x13)
C47: (x5 OR NOT x7 OR x9)
C48: (NOT x3 OR NOT x5 OR x10)
C49: (NOT x4 OR x5 OR NOT x10)
C50: (x1 OR NOT x3 OR NOT x7)
C51: (x4 OR NOT x10 OR x11)
C52: (NOT x6 OR x8 OR x9)
C53: (x3 OR NOT x5 OR x14)
C54: (NOT x2 OR x11 OR x14)
C55: (NOT x1 OR NOT x9 OR NOT x11)
C56: (NOT x7 OR x9 OR x12)
C57: (x10 OR x12 OR x14)
C58: (x1 OR x2 OR x3)
C59: (x8 OR x9 OR x10)
C60: (x3 OR x6 OR NOT x11)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 3 solutions | π_EXACT = ceiling share; near-ceiling accuracy in all four cells means the level should move up | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=0 x2=1 x3=1 x4=0 x5=0 x6=0 x7=0 x8=0 x9=1 x10=1 x11=1 x12=1 x13=0 x14=1 after N = 7 nodes (W = 1560); MENTION,MAJ: N = 22. If b < N: the default (UNSAT, or FILL = violates [20, 45, 55] at b = N/2). | cell W high: π_DPLL estimated jointly with π_F from the W and F_ref effects (feature-dependent weights π_h(log W, log F_ref)); power 0.9 to detect a 15 pp W effect, i.e. π_DPLL ≥ 0.2 at the W contrast; a null W effect bounds π_DPLL ≤ 0.15 (upper 95%) | MOMS,MAJ reference: DEC = 5, BT = 2, CONF = 2, PROP = 18; first decisions (var, value) = [(3, 1), (1, 1), (9, 1)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: UNSAT; w=2: UNSAT; w=4: SAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: SAT; k=3,MENTION: SAT; k=3,INDEX: UNSAT (default) | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=14) = 0.29, P(success / k=70) = 0.70, P(success / k=350) = 0.97; modal failure at k=14: violates [27], LM0=True, Hamming to nearest solution = 8 | cell F high: π_F from the F_ref effect at fixed W; same power; a null F_ref effect bounds π_F ≤ 0.15 (upper 95%) | FULL candidate, VIOL list, FLIP moves; DEC <= 1; #FLIP about the WalkSAT median of 54 |
| MIN-CONFLICTS | P(success / k=14) = 0.08, P(success / k=70) = 0.32, P(success / k=350) = 0.34 | cell F high: π_F from the F_ref effect at fixed W; same power; a null F_ref effect bounds π_F ≤ 0.15 (upper 95%) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C55); MENTION,MAJ: UNSAT (dead end at C55); MOMS,TRUE: UNSAT (dead end at C55); MOMS,MAJ: UNSAT (dead end at C55) / CONT violates: MENTION,TRUE: [55]; MENTION,MAJ: [55]; MOMS,TRUE: [55]; MOMS,MAJ: [55] | π_C from residual errors not explained by W or F_ref (g(x) is balanced across cells) | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=1 x3=1 x4=0 x5=1 x6=1 x7=1 x8=1 x9=0 x10=1 x11=1 x12=1 x13=0 x14=0 (violates [27]) | π_C from residual errors not explained by W or F_ref (g(x) is balanced across cells) | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=1 x4=0 x5=1 x6=1 x7=0 x8=1 x9=1 x10=1 x11=1 x12=1 x13=0 x14=1 (violates [5, 18, 20, 22, 40, 55]) | π_POLARITY ≈ 0 expected (polarity agreement matched across cells) | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.856 (eps=1e-4) or 0.21 (eps=1e-3), W = 1560; otherwise a slip (one missed clause, or a spurious conflict) | π_NE vs π_DPLL decided by b̂ across budgets: NOISY-DPLL(b, ε) posterior on log b; b̂ flat across 2k/8k/BE moves weight from DPLL-b to NE | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| PERCEPTION-NOISE | exact answer to a misread formula; 17% of single sign misreads give a wrong answer here | π_PERCEPTION estimated in E6 (re-check, same-clause repeats); here only its budget-flat error rate | the trace quotes the violated clause with a sign or index error |
| RANDOM | uniform assignment; P(correct) = 0.0002 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), DPLL-b[MOMS, b=10, Δ=UNSAT]; pushes down DPLL-b[MENTION, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=10, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), MIN-CONFLICTS (k=14) (LR 0.092), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *near-miss (infeasible, LM0, V<=3)*: best fit C-UC/CONT, C-GREEDY; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=10, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), C-UC/STOP (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.084), PERCEPTION-NOISE (LR 0.072), RANDOM (LR 0.013)
- *infeasible (other)*: best fit POLARITY / ALWAYS-SAT; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=10, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=10, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=14) (LR 0.013), MIN-CONFLICTS (k=14) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.084), PERCEPTION-NOISE (LR 0.013)
- *UNSAT/UNKNOWN*: best fit DPLL-b[MENTION, b=10, Δ=UNSAT], DPLL-b[INDEX, b=10, Δ=UNSAT], BEAM-2, BACKDOOR[k=2,OCC], C-UC/STOP, B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MOMS, b=10, Δ=UNSAT] (LR 0.013), WALK-k (k=14) (LR 0.013), MIN-CONFLICTS (k=14) (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), PERCEPTION-NOISE (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=21, W=4980; MENTION,MAJ: N=22, W=4920; INDEX,TRUE: N=23, W=4320; INDEX,MAJ: N=20, W=3720; MOMS,TRUE: N=6, W=1620; MOMS,MAJ: N=7, W=1560. Every member's full output is in the JSONL `predictions` field.

---

## E3

### Backdoor size × presentation salience

| Item | Cell | Ground truth | Varied |
|------|------|--------------|--------|
| E3.1 | k* = 2, salience high | SAT (21 solutions) | k* = 2 (between items); presentation: backdoor variables [1, 2] named and mentioned first |
| E3.2 | k* = 2, salience low | SAT (21 solutions) | k* = 2 (between items); presentation: backdoor variables [27, 28] named and mentioned last |
| E3.3 | k* = 3, salience high | SAT (6 solutions) | k* = 3 (between items); presentation: backdoor variables [1, 2, 3] named and mentioned first |
| E3.4 | k* = 3, salience low | SAT (6 solutions) | k* = 3 (between items); presentation: backdoor variables [26, 27, 28] named and mentioned last |
| E3.5 | k* = 4, salience high | SAT (36 solutions) | k* = 4 (between items); presentation: backdoor variables [1, 2, 3, 4] named and mentioned first |
| E3.6 | k* = 4, salience low | SAT (36 solutions) | k* = 4 (between items); presentation: backdoor variables [25, 26, 27, 28] named and mentioned last |

**Direction table** (how each set-level outcome moves weight; the sizes are in the likelihood-ratio table below and in each item's hypothesis block):

| Observed outcome (set level) | Moves weight toward | Moves weight away from |
|------------------------------|---------------------|------------------------|
| k*_50 threshold moves +1 per doubling of the budget | DPLL-b, BACKDOOR-k | NOISY-EXACT, C, A, EXACT (no threshold within the range) |
| Accuracy ≈ 2^-k*, flat in budget | C | DPLL-b, BACKDOOR-k, EXACT |
| Large presentation effect (high > low) on the same formula | DPLL-b[MENTION/INDEX], BACKDOOR[MENTION] | DPLL-b[MOMS], BACKDOOR[OCC], WALK-k, NOISY-EXACT, EXACT |
| No presentation effect but a k* × budget interaction | DPLL-b[MOMS] or BACKDOOR[OCC] | order-following members |

**Likelihood-ratio table** (computed). Each row asks: if one response per item (E3.1, E3.2, E3.3, E3.4, E3.5, E3.6) matched theory *h*'s most likely outcome, how much less likely is that pattern under each competitor? Entries are log10 LR(competitor : h), with a 5% slip floor on every theory, so −1.0 means the pattern pushes that competitor's weight down 10× relative to *h*. A cell of N independent responses multiplies these by about N. The readout is the mixture posterior over π, not a verdict (D_F_search.md §2.5).

| If responses match the modal pattern of h = | Tied with h (0.0) | Weakly disfavoured (−1 < log10 LR < 0) | Pushed down ≥ 10× (log10 LR ≤ −1) |
|---------------------------------------------|-------------------|----------------------------------------|-----------------------------------|
| EXACT | DPLL-b (b >= N), DPLL-b[MOMS, b=20, Δ=UNSAT] | — | DPLL-b[MENTION, b=20, Δ=UNSAT] (-1.9), DPLL-b[INDEX, b=20, Δ=UNSAT] (-7.5), BEAM-2 (-3.8), BACKDOOR[k=k*,INDEX] (-5.7), BACKDOOR[k=k*,OCC] (-11.3), WALK-k (k=140) (-1.3), MIN-CONFLICTS (k=140) (-4.4), C-UC/STOP (-5.7), C-UC/CONT (-5.7), C-GREEDY (-11.3), POLARITY / ALWAYS-SAT (-11.3), B1 (UP-k, FLP-1) (-11.3), NOISY-EXACT (-1.9), RANDOM (-11.3) |
| DPLL-b (b >= N) | EXACT, DPLL-b[MOMS, b=20, Δ=UNSAT] | — | DPLL-b[MENTION, b=20, Δ=UNSAT] (-1.9), DPLL-b[INDEX, b=20, Δ=UNSAT] (-7.5), BEAM-2 (-3.8), BACKDOOR[k=k*,INDEX] (-5.7), BACKDOOR[k=k*,OCC] (-11.3), WALK-k (k=140) (-1.3), MIN-CONFLICTS (k=140) (-4.4), C-UC/STOP (-5.7), C-UC/CONT (-5.7), C-GREEDY (-11.3), POLARITY / ALWAYS-SAT (-11.3), B1 (UP-k, FLP-1) (-11.3), NOISY-EXACT (-1.9), RANDOM (-11.3) |
| DPLL-b[MENTION, b=20, Δ=UNSAT] | — | — | EXACT (-1.9), DPLL-b (b >= N) (-1.9), DPLL-b[INDEX, b=20, Δ=UNSAT] (-5.7), DPLL-b[MOMS, b=20, Δ=UNSAT] (-1.9), BEAM-2 (-5.7), BACKDOOR[k=k*,INDEX] (-7.5), BACKDOOR[k=k*,OCC] (-9.4), WALK-k (k=140) (-2.8), MIN-CONFLICTS (k=140) (-5.2), C-UC/STOP (-3.8), C-UC/CONT (-5.7), C-GREEDY (-11.3), POLARITY / ALWAYS-SAT (-11.3), B1 (UP-k, FLP-1) (-9.4), NOISY-EXACT (-3.6), RANDOM (-11.3) |
| DPLL-b[INDEX, b=20, Δ=UNSAT] | — | — | EXACT (-7.5), DPLL-b (b >= N) (-7.5), DPLL-b[MENTION, b=20, Δ=UNSAT] (-5.7), DPLL-b[MOMS, b=20, Δ=UNSAT] (-7.5), BEAM-2 (-11.3), BACKDOOR[k=k*,INDEX] (-5.7), BACKDOOR[k=k*,OCC] (-3.8), WALK-k (k=140) (-7.9), MIN-CONFLICTS (k=140) (-8.8), C-UC/STOP (-1.9), C-UC/CONT (-7.5), C-GREEDY (-11.3), POLARITY / ALWAYS-SAT (-11.3), B1 (UP-k, FLP-1) (-3.8), NOISY-EXACT (-8.2), RANDOM (-11.3) |
| DPLL-b[MOMS, b=20, Δ=UNSAT] | EXACT, DPLL-b (b >= N) | — | DPLL-b[MENTION, b=20, Δ=UNSAT] (-1.9), DPLL-b[INDEX, b=20, Δ=UNSAT] (-7.5), BEAM-2 (-3.8), BACKDOOR[k=k*,INDEX] (-5.7), BACKDOOR[k=k*,OCC] (-11.3), WALK-k (k=140) (-1.3), MIN-CONFLICTS (k=140) (-4.4), C-UC/STOP (-5.7), C-UC/CONT (-5.7), C-GREEDY (-11.3), POLARITY / ALWAYS-SAT (-11.3), B1 (UP-k, FLP-1) (-11.3), NOISY-EXACT (-1.9), RANDOM (-11.3) |
| BEAM-2 | — | — | EXACT (-3.8), DPLL-b (b >= N) (-3.8), DPLL-b[MENTION, b=20, Δ=UNSAT] (-5.7), DPLL-b[INDEX, b=20, Δ=UNSAT] (-11.3), DPLL-b[MOMS, b=20, Δ=UNSAT] (-3.8), BACKDOOR[k=k*,INDEX] (-5.7), BACKDOOR[k=k*,OCC] (-7.5), WALK-k (k=140) (-4.7), MIN-CONFLICTS (k=140) (-6.9), C-UC/STOP (-9.4), C-UC/CONT (-9.4), C-GREEDY (-11.3), POLARITY / ALWAYS-SAT (-11.3), B1 (UP-k, FLP-1) (-7.5), NOISY-EXACT (-5.1), RANDOM (-11.3) |
| BACKDOOR[k=k*,INDEX] | — | — | EXACT (-5.7), DPLL-b (b >= N) (-5.7), DPLL-b[MENTION, b=20, Δ=UNSAT] (-7.5), DPLL-b[INDEX, b=20, Δ=UNSAT] (-5.7), DPLL-b[MOMS, b=20, Δ=UNSAT] (-5.7), BEAM-2 (-5.7), BACKDOOR[k=k*,OCC] (-5.7), WALK-k (k=140) (-6.4), MIN-CONFLICTS (k=140) (-8.0), C-UC/STOP (-7.5), C-UC/CONT (-9.4), C-GREEDY (-11.3), POLARITY / ALWAYS-SAT (-11.3), B1 (UP-k, FLP-1) (-5.7), NOISY-EXACT (-6.6), RANDOM (-11.3) |
| BACKDOOR[k=k*,OCC] | B1 (UP-k, FLP-1) | — | EXACT (-11.3), DPLL-b (b >= N) (-11.3), DPLL-b[MENTION, b=20, Δ=UNSAT] (-9.4), DPLL-b[INDEX, b=20, Δ=UNSAT] (-3.8), DPLL-b[MOMS, b=20, Δ=UNSAT] (-11.3), BEAM-2 (-7.5), BACKDOOR[k=k*,INDEX] (-5.7), WALK-k (k=140) (-11.3), MIN-CONFLICTS (k=140) (-11.3), C-UC/STOP (-5.7), C-UC/CONT (-11.3), C-GREEDY (-11.3), POLARITY / ALWAYS-SAT (-11.3), NOISY-EXACT (-11.3), RANDOM (-11.3) |
| WALK-k (k=140) | — | EXACT (-0.8), DPLL-b (b >= N) (-0.8), DPLL-b[MENTION, b=20, Δ=UNSAT] (-0.8), DPLL-b[MOMS, b=20, Δ=UNSAT] (-0.8) | DPLL-b[INDEX, b=20, Δ=UNSAT] (-6.4), BEAM-2 (-4.5), BACKDOOR[k=k*,INDEX] (-6.4), BACKDOOR[k=k*,OCC] (-10.2), MIN-CONFLICTS (k=140) (-2.3), C-UC/STOP (-4.5), C-UC/CONT (-2.6), C-GREEDY (-10.2), POLARITY / ALWAYS-SAT (-10.2), B1 (UP-k, FLP-1) (-10.2), NOISY-EXACT (-1.1), RANDOM (-10.2) |
| MIN-CONFLICTS (k=140) | — | — | EXACT (-10.8), DPLL-b (b >= N) (-10.8), DPLL-b[MENTION, b=20, Δ=UNSAT] (-10.8), DPLL-b[INDEX, b=20, Δ=UNSAT] (-10.8), DPLL-b[MOMS, b=20, Δ=UNSAT] (-10.8), BEAM-2 (-10.8), BACKDOOR[k=k*,INDEX] (-10.8), BACKDOOR[k=k*,OCC] (-10.8), WALK-k (k=140) (-3.4), C-UC/STOP (-10.8), C-UC/CONT (-7.0), C-GREEDY (-10.8), POLARITY / ALWAYS-SAT (-10.8), B1 (UP-k, FLP-1) (-10.8), NOISY-EXACT (-2.8), RANDOM (-10.8) |
| C-UC/STOP | — | — | EXACT (-5.7), DPLL-b (b >= N) (-5.7), DPLL-b[MENTION, b=20, Δ=UNSAT] (-3.8), DPLL-b[INDEX, b=20, Δ=UNSAT] (-1.9), DPLL-b[MOMS, b=20, Δ=UNSAT] (-5.7), BEAM-2 (-9.4), BACKDOOR[k=k*,INDEX] (-7.5), BACKDOOR[k=k*,OCC] (-5.7), WALK-k (k=140) (-6.2), MIN-CONFLICTS (k=140) (-7.8), C-UC/CONT (-5.7), C-GREEDY (-11.3), POLARITY / ALWAYS-SAT (-11.3), B1 (UP-k, FLP-1) (-5.7), NOISY-EXACT (-6.6), RANDOM (-11.3) |
| C-UC/CONT | — | — | EXACT (-5.7), DPLL-b (b >= N) (-5.7), DPLL-b[MENTION, b=20, Δ=UNSAT] (-5.7), DPLL-b[INDEX, b=20, Δ=UNSAT] (-7.5), DPLL-b[MOMS, b=20, Δ=UNSAT] (-5.7), BEAM-2 (-9.4), BACKDOOR[k=k*,INDEX] (-9.4), BACKDOOR[k=k*,OCC] (-11.3), WALK-k (k=140) (-3.0), MIN-CONFLICTS (k=140) (-4.2), C-UC/STOP (-5.7), C-GREEDY (-9.4), POLARITY / ALWAYS-SAT (-9.4), B1 (UP-k, FLP-1) (-11.3), NOISY-EXACT (-2.6), RANDOM (-9.4) |
| C-GREEDY | POLARITY / ALWAYS-SAT, RANDOM | — | EXACT (-11.3), DPLL-b (b >= N) (-11.3), DPLL-b[MENTION, b=20, Δ=UNSAT] (-11.3), DPLL-b[INDEX, b=20, Δ=UNSAT] (-11.3), DPLL-b[MOMS, b=20, Δ=UNSAT] (-11.3), BEAM-2 (-11.3), BACKDOOR[k=k*,INDEX] (-11.3), BACKDOOR[k=k*,OCC] (-11.3), WALK-k (k=140) (-9.9), MIN-CONFLICTS (k=140) (-11.3), C-UC/STOP (-11.3), C-UC/CONT (-9.4), B1 (UP-k, FLP-1) (-11.3), NOISY-EXACT (-3.4) |
| POLARITY / ALWAYS-SAT | C-GREEDY, RANDOM | — | EXACT (-11.3), DPLL-b (b >= N) (-11.3), DPLL-b[MENTION, b=20, Δ=UNSAT] (-11.3), DPLL-b[INDEX, b=20, Δ=UNSAT] (-11.3), DPLL-b[MOMS, b=20, Δ=UNSAT] (-11.3), BEAM-2 (-11.3), BACKDOOR[k=k*,INDEX] (-11.3), BACKDOOR[k=k*,OCC] (-11.3), WALK-k (k=140) (-9.9), MIN-CONFLICTS (k=140) (-11.3), C-UC/STOP (-11.3), C-UC/CONT (-9.4), B1 (UP-k, FLP-1) (-11.3), NOISY-EXACT (-3.4) |
| B1 (UP-k, FLP-1) | BACKDOOR[k=k*,OCC] | — | EXACT (-11.3), DPLL-b (b >= N) (-11.3), DPLL-b[MENTION, b=20, Δ=UNSAT] (-9.4), DPLL-b[INDEX, b=20, Δ=UNSAT] (-3.8), DPLL-b[MOMS, b=20, Δ=UNSAT] (-11.3), BEAM-2 (-7.5), BACKDOOR[k=k*,INDEX] (-5.7), WALK-k (k=140) (-11.3), MIN-CONFLICTS (k=140) (-11.3), C-UC/STOP (-5.7), C-UC/CONT (-11.3), C-GREEDY (-11.3), POLARITY / ALWAYS-SAT (-11.3), NOISY-EXACT (-11.3), RANDOM (-11.3) |
| NOISY-EXACT | — | — | DPLL-b[INDEX, b=20, Δ=UNSAT] (-5.6), BEAM-2 (-1.8), BACKDOOR[k=k*,INDEX] (-3.7), BACKDOOR[k=k*,OCC] (-9.4), MIN-CONFLICTS (k=140) (-2.4), C-UC/STOP (-3.7), C-UC/CONT (-3.7), C-GREEDY (-9.4), POLARITY / ALWAYS-SAT (-9.4), B1 (UP-k, FLP-1) (-9.4), RANDOM (-9.4) |
| RANDOM | C-GREEDY, POLARITY / ALWAYS-SAT | — | EXACT (-11.3), DPLL-b (b >= N) (-11.3), DPLL-b[MENTION, b=20, Δ=UNSAT] (-11.3), DPLL-b[INDEX, b=20, Δ=UNSAT] (-11.3), DPLL-b[MOMS, b=20, Δ=UNSAT] (-11.3), BEAM-2 (-11.3), BACKDOOR[k=k*,INDEX] (-11.3), BACKDOOR[k=k*,OCC] (-11.3), WALK-k (k=140) (-9.9), MIN-CONFLICTS (k=140) (-11.3), C-UC/STOP (-11.3), C-UC/CONT (-9.4), B1 (UP-k, FLP-1) (-11.3), NOISY-EXACT (-3.4) |

**Not distinguished by this set:** DPLL-b[MOMS] vs BACKDOOR[OCC]: only through items where the top-OCC set is or is not a backdoor (an observational covariate; rare naturally, about 3% at n=28). WALK-k vs NOISY-EXACT: E2/E6.

### E3.1: k* = 2, salience high

- **Question tested:** Does accuracy at fixed n and α depend on the size of the smallest backdoor, and does the model choose branching variables by their position in the text?
- **Controlled:** the same logical formula in both presentations (isomorphic); n = 28, m = 119; #solutions, backbone
- **Varied:** k* = 2 (between items); presentation: backdoor variables [1, 2] named and mentioned first
- **Ground truth:** `{"answer": "SAT", "n_solutions": 21, "solutions": ["x1=0 x2=1 x3=0 x4=1 x5=0 x6=0 x7=1 x8=0 x9=1 x10=1 x11=1 x12=0 x13=0 x14=1 x15=1 x16=1 x17=1 x18=1 x19=1 x20=0 x21=1 x22=1 x23=0 x24=0 x25=0 x26=0 x27=0 x28=1", "x1=0 x2=1 x3=0 x4=1 x5=0 x6=0 x7=1 x8=0 x9=1 x10=1 x11=1 x12=0 x13=0 x14=1 x15=1 x16=1 x17=1 x18=1 x19=1 x20=0 x21=1 x22=1 x23=0 x24=1 x25=0 x26=0 x27=0 x28=1", "..."]}`
- **Notes:** Selection-based manipulation. Planting backdoors larger than 2 at α≈4.26 failed: the random fill always created a natural size-2 backdoor. MOMS ties are broken by mention order, so even MOMS can shift slightly between presentations.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x28. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (NOT x1 OR NOT x2 OR x20)
C2: (x2 OR x22 OR x26)
C3: (NOT x2 OR x21 OR x18)
C4: (NOT x1 OR NOT x12 OR NOT x11)
C5: (x1 OR NOT x12 OR NOT x26)
C6: (x2 OR x9 OR x16)
C7: (NOT x2 OR x9 OR NOT x3)
C8: (x1 OR x12 OR NOT x27)
C9: (x1 OR NOT x22 OR x4)
C10: (NOT x2 OR NOT x20 OR NOT x23)
C11: (NOT x2 OR x27 OR NOT x23)
C12: (NOT x1 OR x11 OR x18)
C13: (x2 OR NOT x10 OR x27)
C14: (x1 OR x16 OR x10)
C15: (x2 OR NOT x8 OR NOT x28)
C16: (x2 OR NOT x8 OR NOT x4)
C17: (NOT x1 OR x7 OR NOT x10)
C18: (NOT x2 OR NOT x6 OR NOT x4)
C19: (x1 OR x21 OR x8)
C20: (x2 OR x15 OR x5)
C21: (NOT x2 OR NOT x20 OR NOT x5)
C22: (NOT x2 OR x9 OR x19)
C23: (x1 OR NOT x28 OR NOT x5)
C24: (NOT x1 OR x27 OR x18)
C25: (NOT x1 OR x12 OR NOT x8)
C26: (x8 OR x26 OR x19)
C27: (NOT x11 OR NOT x25 OR x26)
C28: (x9 OR x6 OR x19)
C29: (NOT x14 OR x9 OR x8)
C30: (x12 OR NOT x3 OR NOT x18)
C31: (x14 OR NOT x16 OR x26)
C32: (x21 OR NOT x22 OR NOT x18)
C33: (x16 OR x6 OR NOT x4)
C34: (NOT x6 OR x18 OR x26)
C35: (x11 OR NOT x24 OR NOT x18)
C36: (NOT x8 OR NOT x4 OR NOT x19)
C37: (x15 OR NOT x9 OR NOT x5)
C38: (x10 OR x3 OR x18)
C39: (NOT x12 OR NOT x22 OR x6)
C40: (NOT x14 OR x9 OR x6)
C41: (x14 OR NOT x22 OR x17)
C42: (NOT x22 OR x27 OR x19)
C43: (x25 OR NOT x26 OR x19)
C44: (NOT x16 OR x22 OR x17)
C45: (x15 OR NOT x17 OR x13)
C46: (NOT x10 OR x3 OR NOT x13)
C47: (x15 OR NOT x17 OR NOT x26)
C48: (x14 OR x22 OR NOT x6)
C49: (x14 OR NOT x27 OR x17)
C50: (NOT x14 OR x6 OR NOT x26)
C51: (NOT x22 OR x5 OR NOT x26)
C52: (x11 OR NOT x5 OR x13)
C53: (x7 OR x22 OR NOT x13)
C54: (x28 OR NOT x16 OR NOT x19)
C55: (NOT x9 OR x21 OR x25)
C56: (x21 OR x6 OR NOT x3)
C57: (NOT x20 OR NOT x28 OR x13)
C58: (x28 OR NOT x11 OR x5)
C59: (x24 OR NOT x25 OR NOT x18)
C60: (x15 OR NOT x8 OR NOT x7)
C61: (x21 OR NOT x28 OR x6)
C62: (NOT x28 OR x11 OR x4)
C63: (x8 OR NOT x24 OR x17)
C64: (NOT x15 OR x21 OR NOT x8)
C65: (NOT x15 OR x9 OR x5)
C66: (x7 OR NOT x25 OR NOT x3)
C67: (x11 OR NOT x10 OR NOT x18)
C68: (x22 OR x24 OR x27)
C69: (NOT x9 OR NOT x8 OR x10)
C70: (NOT x28 OR x16 OR NOT x19)
C71: (x11 OR NOT x16 OR NOT x5)
C72: (NOT x17 OR x13 OR x19)
C73: (NOT x10 OR x17 OR x13)
C74: (NOT x14 OR x11 OR NOT x27)
C75: (x14 OR NOT x3 OR NOT x18)
C76: (x6 OR x27 OR NOT x23)
C77: (x11 OR x17 OR x26)
C78: (x12 OR x7 OR x17)
C79: (NOT x28 OR NOT x10 OR NOT x23)
C80: (x21 OR x28 OR x17)
C81: (x27 OR x25 OR NOT x13)
C82: (NOT x20 OR x24 OR x13)
C83: (x9 OR x21 OR NOT x25)
C84: (NOT x20 OR x21 OR x10)
C85: (x11 OR x17 OR NOT x13)
C86: (x7 OR NOT x6 OR NOT x19)
C87: (x10 OR x13 OR NOT x19)
C88: (NOT x9 OR NOT x17 OR x19)
C89: (x20 OR x8 OR x16)
C90: (NOT x20 OR NOT x11 OR x23)
C91: (x12 OR x22 OR x17)
C92: (NOT x7 OR x24 OR NOT x13)
C93: (x20 OR x14 OR x12)
C94: (x9 OR NOT x5 OR NOT x23)
C95: (NOT x13 OR NOT x23 OR x26)
C96: (x16 OR NOT x25 OR NOT x19)
C97: (NOT x20 OR NOT x4 OR NOT x13)
C98: (NOT x27 OR x13 OR x26)
C99: (x16 OR NOT x10 OR NOT x4)
C100: (NOT x14 OR NOT x12 OR NOT x18)
C101: (x16 OR x22 OR NOT x25)
C102: (NOT x15 OR NOT x22 OR x17)
C103: (NOT x20 OR NOT x8 OR x4)
C104: (NOT x15 OR NOT x3 OR NOT x19)
C105: (NOT x15 OR NOT x28 OR NOT x6)
C106: (x12 OR x22 OR NOT x18)
C107: (x5 OR NOT x18 OR NOT x26)
C108: (NOT x7 OR x22 OR x23)
C109: (NOT x14 OR x28 OR NOT x3)
C110: (x16 OR NOT x22 OR x18)
C111: (x15 OR x12 OR x5)
C112: (x4 OR NOT x3 OR x19)
C113: (x8 OR NOT x6 OR NOT x26)
C114: (NOT x15 OR x7 OR NOT x10)
C115: (x14 OR x9 OR NOT x13)
C116: (NOT x20 OR NOT x28 OR NOT x16)
C117: (x11 OR NOT x5 OR NOT x26)
C118: (x9 OR NOT x3 OR x13)
C119: (NOT x15 OR x8 OR x18)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 21 solutions | π_EXACT = the ceiling share across cells | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=1 x2=0 x3=0 x4=0 x5=0 x6=0 x7=0 x8=0 x9=1 x10=0 x11=1 x12=0 x13=1 x14=1 x15=1 x16=1 x17=1 x18=1 x19=1 x20=0 x21=1 x22=1 x23=0 x24=1 x25=0 x26=0 x27=1 x28=1 after N = 15 nodes (W = 8925); MENTION,MAJ: N = 15. If b < N: the default (UNSAT, or FILL = violates [20, 38, 54, 58, 111] at b = N/2). | π_DPLL from the k* × budget interaction (slope s ≈ 1 per doubling); power > 0.95 to detect s ≥ 0.5, so a null bounds the budget-scaling search component π_DPLL+BACKDOOR ≤ 0.1 (upper 95%). Presentation effect is computed, not assumed: on this formula MENTION,MAJ needs 15 (high) vs 12 (low) nodes, INDEX,MAJ 23 vs 24, MOMS,MAJ 15 vs 15 (high presentation needs MORE MENTION nodes than low) | MOMS,MAJ reference: DEC = 11, BT = 4, CONF = 4, PROP = 59; first decisions (var, value) = [(22, 1), (18, 0), (26, 1)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: UNSAT; w=2: SAT; w=4: SAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: SAT; k=2,INDEX: SAT; k=3,OCC: UNSAT (default); k=3,MENTION: SAT; k=3,INDEX: SAT | BACKDOOR[k=2,INDEX] (branch on the k lowest-numbered variables): high → SAT, low → UNSAT (default); BACKDOOR[OCC]: no presentation effect | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=28) = 0.17, P(success / k=140) = 0.61, P(success / k=700) = 0.99; modal failure at k=28: violates [4, 20, 38, 44, 58], LM0=False, Hamming to nearest solution = 13 | π_F: no presentation effect (same formula); weak dependence on k* | FULL candidate, VIOL list, FLIP moves; DEC <= 1; #FLIP about the WalkSAT median of 136 |
| MIN-CONFLICTS | P(success / k=28) = 0.02, P(success / k=140) = 0.26, P(success / k=700) = 0.29 | π_F: no presentation effect (same formula); weak dependence on k* | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: SAT; MENTION,MAJ: UNSAT (dead end at C113); MOMS,TRUE: UNSAT (dead end at C105); MOMS,MAJ: UNSAT (dead end at C119) / CONT violates: MENTION,TRUE: []; MENTION,MAJ: [105, 113]; MOMS,TRUE: [105, 113]; MOMS,MAJ: [104, 116, 119] | π_C = the budget-flat component with accuracy ≈ 2^-k* | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=0 x3=0 x4=0 x5=1 x6=1 x7=0 x8=1 x9=1 x10=0 x11=1 x12=1 x13=1 x14=1 x15=1 x16=1 x17=1 x18=0 x19=1 x20=0 x21=1 x22=1 x23=0 x24=1 x25=1 x26=1 x27=1 x28=1 (violates [4, 15, 38, 69, 86, 105]) | π_C = the budget-flat component with accuracy ≈ 2^-k* | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=0 x3=0 x4=0 x5=0 x6=1 x7=1 x8=0 x9=1 x10=0 x11=1 x12=1 x13=1 x14=1 x15=0 x16=1 x17=1 x18=0 x19=1 x20=0 x21=1 x22=1 x23=0 x24=1 x25=0 x26=1 x27=1 x28=0 (violates [4, 20, 38, 47, 51, 54, 58, 113]) | π_POLARITY: each correct answer where the polarity assignment is infeasible has LR ≈ 0.05 against it | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.41 (eps=1e-4) or 0.0 (eps=1e-3), W = 8925; otherwise a slip (one missed clause, or a spurious conflict) | π_NE = the W-smooth component without a T × k* interaction | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0000 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), DPLL-b[MENTION, b=20, Δ=UNSAT], DPLL-b[MOMS, b=20, Δ=UNSAT], BEAM-2, BACKDOOR[k=k*,INDEX]; pushes down DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.013), BACKDOOR[k=k*,OCC] (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *near-miss (infeasible, LM0, V<=3)*: best fit C-UC/CONT; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=k*,INDEX] (LR 0.013), BACKDOOR[k=k*,OCC] (LR 0.013), C-UC/STOP (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *infeasible (other)*: best fit C-GREEDY, POLARITY / ALWAYS-SAT, RANDOM; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=k*,INDEX] (LR 0.013), BACKDOOR[k=k*,OCC] (LR 0.013), WALK-k (k=140) (LR 0.013), MIN-CONFLICTS (k=140) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013)
- *UNSAT/UNKNOWN*: best fit DPLL-b[INDEX, b=20, Δ=UNSAT], BACKDOOR[k=k*,OCC], C-UC/STOP, B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=k*,INDEX] (LR 0.013), WALK-k (k=140) (LR 0.013), MIN-CONFLICTS (k=140) (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=2, W=3451; MENTION,MAJ: N=15, W=5712; INDEX,TRUE: N=2, W=3451; INDEX,MAJ: N=23, W=9877; MOMS,TRUE: N=12, W=6426; MOMS,MAJ: N=15, W=8925. Every member's full output is in the JSONL `predictions` field.

### E3.2: k* = 2, salience low

- **Question tested:** Does accuracy at fixed n and α depend on the size of the smallest backdoor, and does the model choose branching variables by their position in the text?
- **Controlled:** the same logical formula in both presentations (isomorphic); n = 28, m = 119; #solutions, backbone
- **Varied:** k* = 2 (between items); presentation: backdoor variables [27, 28] named and mentioned last
- **Ground truth:** `{"answer": "SAT", "n_solutions": 21, "solutions": ["x1=0 x2=0 x3=0 x4=0 x5=0 x6=0 x7=1 x8=0 x9=0 x10=0 x11=1 x12=0 x13=1 x14=0 x15=1 x16=1 x17=1 x18=1 x19=1 x20=1 x21=0 x22=0 x23=0 x24=0 x25=1 x26=0 x27=1 x28=0", "x1=0 x2=0 x3=1 x4=0 x5=0 x6=0 x7=1 x8=0 x9=0 x10=0 x11=1 x12=0 x13=1 x14=0 x15=1 x16=1 x17=1 x18=1 x19=1 x20=1 x21=0 x22=0 x23=0 x24=0 x25=1 x26=0 x27=1 x28=0", "..."]}`
- **Notes:** Selection-based manipulation. Planting backdoors larger than 2 at α≈4.26 failed: the random fill always created a natural size-2 backdoor. MOMS ties are broken by mention order, so even MOMS can shift slightly between presentations.
- **Same formula as E3.1**, under a renaming of the variables and a reordering of clauses and literals (an isomorphic presentation).

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x28. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x6 OR x24 OR x17)
C2: (NOT x9 OR NOT x23 OR x24)
C3: (x7 OR x4 OR x17)
C4: (NOT x12 OR x7 OR x6)
C5: (x10 OR NOT x1 OR NOT x16)
C6: (x12 OR NOT x14 OR x24)
C7: (x19 OR NOT x20 OR NOT x16)
C8: (x14 OR x4 OR NOT x2)
C9: (NOT x4 OR x16 OR x24)
C10: (x9 OR NOT x22 OR NOT x16)
C11: (NOT x6 OR NOT x2 OR NOT x17)
C12: (x13 OR NOT x7 OR NOT x3)
C13: (x8 OR x1 OR x16)
C14: (NOT x10 OR NOT x20 OR x4)
C15: (NOT x12 OR x7 OR x4)
C16: (x12 OR NOT x20 OR x15)
C17: (NOT x20 OR x25 OR x17)
C18: (x23 OR NOT x24 OR x17)
C19: (NOT x14 OR x20 OR x15)
C20: (x13 OR NOT x15 OR x11)
C21: (NOT x8 OR x1 OR NOT x11)
C22: (x13 OR NOT x15 OR NOT x24)
C23: (x12 OR x20 OR NOT x4)
C24: (x12 OR NOT x25 OR x15)
C25: (NOT x12 OR x4 OR NOT x24)
C26: (NOT x20 OR x3 OR NOT x24)
C27: (x9 OR NOT x3 OR x11)
C28: (x5 OR x20 OR NOT x11)
C29: (x26 OR NOT x14 OR NOT x17)
C30: (NOT x7 OR x19 OR x23)
C31: (x19 OR x4 OR NOT x1)
C32: (NOT x18 OR NOT x26 OR x11)
C33: (x26 OR NOT x9 OR x3)
C34: (x22 OR NOT x23 OR NOT x16)
C35: (x13 OR NOT x6 OR NOT x5)
C36: (x19 OR NOT x26 OR x4)
C37: (NOT x26 OR x9 OR x2)
C38: (x6 OR NOT x22 OR x15)
C39: (NOT x13 OR x19 OR NOT x6)
C40: (NOT x13 OR x7 OR x3)
C41: (x5 OR NOT x23 OR NOT x1)
C42: (x9 OR NOT x8 OR NOT x16)
C43: (x20 OR x22 OR x25)
C44: (NOT x7 OR NOT x6 OR x8)
C45: (NOT x26 OR x14 OR NOT x17)
C46: (x9 OR NOT x14 OR NOT x3)
C47: (NOT x15 OR x11 OR x17)
C48: (NOT x8 OR x15 OR x11)
C49: (NOT x12 OR x9 OR NOT x25)
C50: (x12 OR NOT x1 OR NOT x16)
C51: (x4 OR x25 OR NOT x21)
C52: (x9 OR x15 OR x24)
C53: (x10 OR x5 OR x15)
C54: (NOT x26 OR NOT x8 OR NOT x21)
C55: (x19 OR x26 OR x15)
C56: (x25 OR x23 OR NOT x11)
C57: (NOT x18 OR x22 OR x11)
C58: (x7 OR x19 OR NOT x23)
C59: (NOT x18 OR x19 OR x8)
C60: (x9 OR x15 OR NOT x11)
C61: (x5 OR NOT x4 OR NOT x17)
C62: (x8 OR x11 OR NOT x17)
C63: (NOT x7 OR NOT x15 OR x17)
C64: (x18 OR x6 OR x14)
C65: (NOT x18 OR NOT x9 OR x21)
C66: (x10 OR x20 OR x15)
C67: (NOT x5 OR x22 OR NOT x11)
C68: (x18 OR x12 OR x10)
C69: (x7 OR NOT x3 OR NOT x21)
C70: (NOT x11 OR NOT x21 OR x24)
C71: (x14 OR NOT x23 OR NOT x17)
C72: (NOT x18 OR NOT x2 OR NOT x11)
C73: (NOT x25 OR x11 OR x24)
C74: (x14 OR NOT x8 OR NOT x2)
C75: (NOT x12 OR NOT x10 OR NOT x16)
C76: (x14 OR x20 OR NOT x23)
C77: (NOT x13 OR NOT x20 OR x15)
C78: (NOT x18 OR NOT x6 OR x2)
C79: (NOT x13 OR NOT x1 OR NOT x17)
C80: (NOT x13 OR NOT x26 OR NOT x4)
C81: (x10 OR x20 OR NOT x16)
C82: (x3 OR NOT x16 OR NOT x24)
C83: (NOT x5 OR x20 OR x21)
C84: (NOT x12 OR x26 OR NOT x1)
C85: (x14 OR NOT x20 OR x16)
C86: (x13 OR x10 OR x3)
C87: (x2 OR NOT x1 OR x17)
C88: (x6 OR NOT x4 OR NOT x24)
C89: (NOT x13 OR x5 OR NOT x8)
C90: (x12 OR x7 OR NOT x11)
C91: (NOT x18 OR NOT x26 OR NOT x14)
C92: (x9 OR NOT x3 OR NOT x24)
C93: (x7 OR NOT x1 OR x11)
C94: (NOT x13 OR x6 OR x16)
C95: (x20 OR x24 OR x28)
C96: (x19 OR x16 OR NOT x28)
C97: (NOT x10 OR NOT x9 OR NOT x27)
C98: (NOT x10 OR NOT x24 OR x27)
C99: (x7 OR x14 OR x28)
C100: (x7 OR NOT x1 OR NOT x28)
C101: (x10 OR NOT x25 OR x27)
C102: (NOT x20 OR x2 OR x27)
C103: (NOT x18 OR NOT x21 OR NOT x28)
C104: (x25 OR NOT x21 OR NOT x28)
C105: (x9 OR x16 OR NOT x27)
C106: (NOT x8 OR x25 OR x28)
C107: (x14 OR x8 OR x27)
C108: (NOT x6 OR NOT x26 OR x28)
C109: (NOT x6 OR NOT x2 OR x28)
C110: (x5 OR NOT x8 OR NOT x27)
C111: (NOT x4 OR NOT x2 OR NOT x28)
C112: (x19 OR x6 OR x27)
C113: (x13 OR x3 OR x28)
C114: (NOT x18 OR NOT x3 OR NOT x28)
C115: (x7 OR x17 OR NOT x28)
C116: (x18 OR NOT x27 OR NOT x28)
C117: (NOT x26 OR NOT x3 OR x27)
C118: (x25 OR x16 OR NOT x27)
C119: (x10 OR NOT x6 OR NOT x27)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 21 solutions | π_EXACT = the ceiling share across cells | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=0 x2=0 x3=0 x4=0 x5=1 x6=0 x7=1 x8=0 x9=1 x10=0 x11=1 x12=1 x13=1 x14=1 x15=1 x16=1 x17=1 x18=0 x19=1 x20=1 x21=0 x22=1 x23=0 x24=0 x25=1 x26=1 x27=1 x28=0 after N = 15 nodes (W = 8925); MENTION,MAJ: N = 12. If b < N: the default (UNSAT, or FILL = violates [13, 29, 33, 86, 113] at b = N/2). | π_DPLL from the k* × budget interaction (slope s ≈ 1 per doubling); power > 0.95 to detect s ≥ 0.5, so a null bounds the budget-scaling search component π_DPLL+BACKDOOR ≤ 0.1 (upper 95%). Presentation effect is computed, not assumed: on this formula MENTION,MAJ needs 15 (high) vs 12 (low) nodes, INDEX,MAJ 23 vs 24, MOMS,MAJ 15 vs 15 (high presentation needs MORE MENTION nodes than low) | MOMS,MAJ reference: DEC = 11, BT = 4, CONF = 4, PROP = 59; first decisions (var, value) = [(20, 1), (16, 0), (24, 1)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: UNSAT; w=2: SAT; w=4: SAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: UNSAT (default) | BACKDOOR[k=2,INDEX] (branch on the k lowest-numbered variables): high → SAT, low → UNSAT (default); BACKDOOR[OCC]: no presentation effect | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=28) = 0.22, P(success / k=140) = 0.67, P(success / k=700) = 0.97; modal failure at k=28: violates [19, 48], LM0=False, Hamming to nearest solution = 9 | π_F: no presentation effect (same formula); weak dependence on k* | FULL candidate, VIOL list, FLIP moves; DEC <= 1; #FLIP about the WalkSAT median of 56 |
| MIN-CONFLICTS | P(success / k=28) = 0.03, P(success / k=140) = 0.23, P(success / k=700) = 0.31 | π_F: no presentation effect (same formula); weak dependence on k* | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C80); MENTION,MAJ: UNSAT (dead end at C98); MOMS,TRUE: UNSAT (dead end at C117); MOMS,MAJ: UNSAT (dead end at C94) / CONT violates: MENTION,TRUE: [80, 83]; MENTION,MAJ: [43, 45, 62, 64, 98, 107]; MOMS,TRUE: [117]; MOMS,MAJ: [79, 91, 94] | π_C = the budget-flat component with accuracy ≈ 2^-k* | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=0 x3=1 x4=1 x5=1 x6=0 x7=1 x8=0 x9=1 x10=1 x11=1 x12=1 x13=1 x14=1 x15=1 x16=1 x17=1 x18=0 x19=1 x20=1 x21=1 x22=1 x23=0 x24=1 x25=1 x26=0 x27=1 x28=0 (violates [29, 75, 79, 84, 88, 97]) | π_C = the budget-flat component with accuracy ≈ 2^-k* | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=0 x2=0 x3=0 x4=1 x5=1 x6=0 x7=1 x8=0 x9=1 x10=1 x11=1 x12=1 x13=0 x14=1 x15=1 x16=0 x17=1 x18=0 x19=1 x20=1 x21=0 x22=1 x23=0 x24=1 x25=1 x26=0 x27=1 x28=0 (violates [13, 22, 26, 29, 33, 88, 97, 113]) | π_POLARITY: each correct answer where the polarity assignment is infeasible has LR ≈ 0.05 against it | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.41 (eps=1e-4) or 0.0 (eps=1e-3), W = 8925; otherwise a slip (one missed clause, or a spurious conflict) | π_NE = the W-smooth component without a T × k* interaction | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0000 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), DPLL-b[MENTION, b=20, Δ=UNSAT], DPLL-b[MOMS, b=20, Δ=UNSAT], BEAM-2; pushes down DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.013), BACKDOOR[k=k*,INDEX] (LR 0.013), BACKDOOR[k=k*,OCC] (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *near-miss (infeasible, LM0, V<=3)*: best fit MIN-CONFLICTS (k=140); pushes down EXACT (LR 0.017), DPLL-b (b >= N) (LR 0.017), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.017), DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.017), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.017), BEAM-2 (LR 0.017), BACKDOOR[k=k*,INDEX] (LR 0.017), BACKDOOR[k=k*,OCC] (LR 0.017), C-UC/STOP (LR 0.017), C-UC/CONT (LR 0.017), C-GREEDY (LR 0.017), POLARITY / ALWAYS-SAT (LR 0.017), B1 (UP-k, FLP-1) (LR 0.017), RANDOM (LR 0.017)
- *infeasible (other)*: best fit C-UC/CONT, C-GREEDY, POLARITY / ALWAYS-SAT, RANDOM; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=k*,INDEX] (LR 0.013), BACKDOOR[k=k*,OCC] (LR 0.013), WALK-k (k=140) (LR 0.013), MIN-CONFLICTS (k=140) (LR 0.013), C-UC/STOP (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013)
- *UNSAT/UNKNOWN*: best fit DPLL-b[INDEX, b=20, Δ=UNSAT], BACKDOOR[k=k*,INDEX], BACKDOOR[k=k*,OCC], C-UC/STOP, B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), WALK-k (k=140) (LR 0.013), MIN-CONFLICTS (k=140) (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=66, W=47719; MENTION,MAJ: N=12, W=3927; INDEX,TRUE: N=68, W=43316; INDEX,MAJ: N=24, W=16303; MOMS,TRUE: N=12, W=6307; MOMS,MAJ: N=15, W=8925. Every member's full output is in the JSONL `predictions` field.

### E3.3: k* = 3, salience high

- **Question tested:** Does accuracy at fixed n and α depend on the size of the smallest backdoor, and does the model choose branching variables by their position in the text?
- **Controlled:** the same logical formula in both presentations (isomorphic); n = 28, m = 119; #solutions, backbone
- **Varied:** k* = 3 (between items); presentation: backdoor variables [1, 2, 3] named and mentioned first
- **Ground truth:** `{"answer": "SAT", "n_solutions": 6, "solutions": ["x1=0 x2=0 x3=0 x4=0 x5=1 x6=0 x7=1 x8=1 x9=1 x10=1 x11=0 x12=0 x13=0 x14=0 x15=0 x16=0 x17=0 x18=1 x19=1 x20=1 x21=1 x22=0 x23=1 x24=0 x25=0 x26=0 x27=0 x28=0", "x1=0 x2=0 x3=0 x4=0 x5=1 x6=0 x7=0 x8=1 x9=1 x10=1 x11=0 x12=0 x13=0 x14=0 x15=0 x16=0 x17=0 x18=1 x19=1 x20=1 x21=1 x22=0 x23=1 x24=0 x25=0 x26=0 x27=0 x28=0", "..."]}`
- **Notes:** Selection-based manipulation. Planting backdoors larger than 2 at α≈4.26 failed: the random fill always created a natural size-2 backdoor. MOMS ties are broken by mention order, so even MOMS can shift slightly between presentations.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x28. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x1 OR x2 OR NOT x16)
C2: (x2 OR x3 OR NOT x25)
C3: (x1 OR x2 OR x18)
C4: (NOT x2 OR NOT x3 OR x10)
C5: (NOT x2 OR NOT x3 OR NOT x27)
C6: (x3 OR NOT x11 OR x26)
C7: (NOT x3 OR NOT x25 OR NOT x21)
C8: (NOT x3 OR NOT x19 OR NOT x12)
C9: (NOT x1 OR NOT x19 OR NOT x21)
C10: (x1 OR x6 OR NOT x24)
C11: (NOT x1 OR x15 OR x28)
C12: (x2 OR x23 OR x25)
C13: (NOT x2 OR NOT x6 OR x21)
C14: (NOT x2 OR x22 OR NOT x4)
C15: (NOT x1 OR x20 OR NOT x27)
C16: (x2 OR NOT x15 OR x13)
C17: (NOT x2 OR NOT x17 OR x16)
C18: (NOT x2 OR x22 OR NOT x26)
C19: (x3 OR NOT x6 OR NOT x14)
C20: (NOT x2 OR x9 OR NOT x27)
C21: (x3 OR x24 OR x21)
C22: (x1 OR x19 OR NOT x26)
C23: (x1 OR x5 OR NOT x21)
C24: (NOT x2 OR NOT x7 OR NOT x21)
C25: (x1 OR NOT x15 OR x12)
C26: (x1 OR x11 OR x20)
C27: (NOT x3 OR NOT x8 OR x21)
C28: (NOT x1 OR x23 OR x22)
C29: (NOT x1 OR NOT x24 OR NOT x5)
C30: (NOT x3 OR x16 OR NOT x21)
C31: (x2 OR x23 OR NOT x13)
C32: (NOT x1 OR x28 OR x10)
C33: (NOT x2 OR x16 OR x4)
C34: (x1 OR x6 OR NOT x14)
C35: (NOT x1 OR x19 OR NOT x21)
C36: (x25 OR NOT x27 OR x12)
C37: (x9 OR NOT x15 OR NOT x22)
C38: (x23 OR NOT x14 OR NOT x28)
C39: (NOT x23 OR NOT x15 OR NOT x28)
C40: (NOT x11 OR x13 OR x12)
C41: (x23 OR x14 OR NOT x27)
C42: (x27 OR NOT x8 OR x10)
C43: (x27 OR x7 OR NOT x26)
C44: (NOT x27 OR x13 OR x7)
C45: (x23 OR NOT x18 OR NOT x22)
C46: (NOT x18 OR x19 OR NOT x8)
C47: (x6 OR NOT x22 OR x10)
C48: (x9 OR NOT x19 OR NOT x21)
C49: (NOT x11 OR NOT x27 OR NOT x16)
C50: (NOT x18 OR NOT x24 OR NOT x5)
C51: (NOT x20 OR x27 OR x8)
C52: (x9 OR NOT x15 OR NOT x12)
C53: (NOT x6 OR NOT x13 OR x4)
C54: (NOT x18 OR NOT x22 OR NOT x26)
C55: (NOT x22 OR NOT x27 OR NOT x7)
C56: (NOT x17 OR x20 OR x7)
C57: (NOT x25 OR NOT x14 OR NOT x26)
C58: (x27 OR x8 OR NOT x7)
C59: (x22 OR x8 OR x28)
C60: (NOT x17 OR x6 OR x16)
C61: (x23 OR NOT x14 OR x13)
C62: (NOT x11 OR NOT x19 OR x12)
C63: (x9 OR x6 OR NOT x4)
C64: (NOT x27 OR NOT x28 OR NOT x12)
C65: (NOT x11 OR x17 OR NOT x26)
C66: (x9 OR NOT x15 OR x16)
C67: (x22 OR NOT x27 OR NOT x26)
C68: (x27 OR x8 OR NOT x26)
C69: (x25 OR NOT x5 OR NOT x13)
C70: (NOT x24 OR NOT x10 OR x12)
C71: (x11 OR x20 OR NOT x12)
C72: (x15 OR NOT x12 OR NOT x26)
C73: (x23 OR x25 OR NOT x27)
C74: (x17 OR NOT x16 OR x4)
C75: (NOT x14 OR NOT x5 OR NOT x26)
C76: (x19 OR x4 OR NOT x26)
C77: (NOT x25 OR x20 OR NOT x5)
C78: (NOT x23 OR x15 OR NOT x13)
C79: (NOT x6 OR x24 OR x4)
C80: (x8 OR x10 OR x4)
C81: (NOT x24 OR NOT x10 OR x26)
C82: (NOT x6 OR NOT x8 OR x7)
C83: (NOT x11 OR x23 OR x16)
C84: (x15 OR x13 OR NOT x12)
C85: (x27 OR NOT x24 OR NOT x4)
C86: (x25 OR NOT x22 OR NOT x8)
C87: (NOT x9 OR NOT x25 OR NOT x26)
C88: (x11 OR x20 OR x28)
C89: (x9 OR NOT x22 OR NOT x5)
C90: (x15 OR x22 OR NOT x28)
C91: (NOT x25 OR x24 OR NOT x12)
C92: (x5 OR x28 OR NOT x12)
C93: (NOT x20 OR x16 OR NOT x26)
C94: (NOT x6 OR NOT x10 OR x12)
C95: (NOT x25 OR NOT x14 OR x13)
C96: (x6 OR NOT x27 OR x8)
C97: (NOT x15 OR NOT x22 OR x16)
C98: (x23 OR NOT x18 OR x8)
C99: (x23 OR x5 OR NOT x4)
C100: (NOT x17 OR x18 OR x27)
C101: (x18 OR NOT x19 OR NOT x21)
C102: (x22 OR NOT x16 OR NOT x12)
C103: (NOT x16 OR NOT x12 OR x26)
C104: (x17 OR NOT x6 OR x28)
C105: (NOT x14 OR x22 OR NOT x24)
C106: (x25 OR x13 OR NOT x16)
C107: (NOT x18 OR NOT x6 OR x16)
C108: (x27 OR x24 OR x8)
C109: (x17 OR x8 OR NOT x7)
C110: (NOT x15 OR x20 OR NOT x28)
C111: (x15 OR x13 OR x8)
C112: (NOT x24 OR x10 OR NOT x26)
C113: (NOT x13 OR NOT x28 OR NOT x21)
C114: (x14 OR NOT x20 OR NOT x4)
C115: (NOT x23 OR x27 OR NOT x28)
C116: (x25 OR x8 OR NOT x16)
C117: (NOT x17 OR x24 OR x21)
C118: (NOT x27 OR x13 OR NOT x26)
C119: (NOT x27 OR NOT x19 OR NOT x5)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 6 solutions | π_EXACT = the ceiling share across cells | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=0 x2=0 x3=0 x4=0 x5=1 x6=0 x7=1 x8=1 x9=1 x10=1 x11=0 x12=0 x13=0 x14=0 x15=0 x16=0 x17=0 x18=1 x19=1 x20=1 x21=1 x22=0 x23=1 x24=0 x25=0 x26=0 x27=0 x28=0 after N = 11 nodes (W = 6307); MENTION,MAJ: N = 92. If b < N: the default (UNSAT, or FILL = violates [2, 11, 35, 78, 114] at b = N/2). | π_DPLL from the k* × budget interaction (slope s ≈ 1 per doubling); power > 0.95 to detect s ≥ 0.5, so a null bounds the budget-scaling search component π_DPLL+BACKDOOR ≤ 0.1 (upper 95%). Presentation effect is computed, not assumed: on this formula MENTION,MAJ needs 92 (high) vs 10 (low) nodes, INDEX,MAJ 162 vs 383, MOMS,MAJ 11 vs 11 (high presentation needs MORE MENTION nodes than low) | MOMS,MAJ reference: DEC = 8, BT = 3, CONF = 3, PROP = 41; first decisions (var, value) = [(27, 0), (8, 1), (24, 0)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: UNSAT; w=2: SAT; w=4: SAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: SAT | BACKDOOR[k=3,INDEX] (branch on the k lowest-numbered variables): high → SAT, low → UNSAT (default); BACKDOOR[OCC]: no presentation effect | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=28) = 0.12, P(success / k=140) = 0.43, P(success / k=700) = 0.86; modal failure at k=28: violates [7, 25, 34], LM0=False, Hamming to nearest solution = 8 | π_F: no presentation effect (same formula); weak dependence on k* | FULL candidate, VIOL list, FLIP moves; DEC <= 1; #FLIP about the WalkSAT median of 244 |
| MIN-CONFLICTS | P(success / k=28) = 0.02, P(success / k=140) = 0.08, P(success / k=700) = 0.12 | π_F: no presentation effect (same formula); weak dependence on k* | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C108); MENTION,MAJ: UNSAT (dead end at C108); MOMS,TRUE: UNSAT (dead end at C87); MOMS,MAJ: UNSAT (dead end at C27) / CONT violates: MENTION,TRUE: [108]; MENTION,MAJ: [108]; MOMS,TRUE: [87, 92]; MOMS,MAJ: [27] | π_C = the budget-flat component with accuracy ≈ 2^-k* | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=0 x3=1 x4=0 x5=1 x6=0 x7=0 x8=1 x9=1 x10=1 x11=0 x12=0 x13=1 x14=1 x15=1 x16=1 x17=1 x18=0 x19=0 x20=1 x21=0 x22=0 x23=1 x24=0 x25=1 x26=0 x27=0 x28=0 (violates [27, 100, 117]) | π_C = the budget-flat component with accuracy ≈ 2^-k* | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=0 x3=0 x4=1 x5=0 x6=0 x7=1 x8=1 x9=1 x10=1 x11=0 x12=0 x13=1 x14=0 x15=0 x16=1 x17=0 x18=0 x19=0 x20=1 x21=0 x22=1 x23=1 x24=0 x25=1 x26=0 x27=0 x28=0 (violates [2, 11, 21, 78, 114]) | π_POLARITY: each correct answer where the polarity assignment is infeasible has LR ≈ 0.05 against it | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.532 (eps=1e-4) or 0.002 (eps=1e-3), W = 6307; otherwise a slip (one missed clause, or a spurious conflict) | π_NE = the W-smooth component without a T × k* interaction | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0000 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), DPLL-b[MOMS, b=20, Δ=UNSAT], BEAM-2, BACKDOOR[k=k*,INDEX]; pushes down DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.013), BACKDOOR[k=k*,OCC] (LR 0.013), MIN-CONFLICTS (k=140) (LR 0.092), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *near-miss (infeasible, LM0, V<=3)*: best fit C-UC/CONT; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=k*,INDEX] (LR 0.013), BACKDOOR[k=k*,OCC] (LR 0.013), C-UC/STOP (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *infeasible (other)*: best fit C-GREEDY, POLARITY / ALWAYS-SAT, RANDOM; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=k*,INDEX] (LR 0.013), BACKDOOR[k=k*,OCC] (LR 0.013), WALK-k (k=140) (LR 0.013), MIN-CONFLICTS (k=140) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013)
- *UNSAT/UNKNOWN*: best fit DPLL-b[MENTION, b=20, Δ=UNSAT], DPLL-b[INDEX, b=20, Δ=UNSAT], BACKDOOR[k=k*,OCC], C-UC/STOP, B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=k*,INDEX] (LR 0.013), WALK-k (k=140) (LR 0.013), MIN-CONFLICTS (k=140) (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=108, W=60809; MENTION,MAJ: N=92, W=56287; INDEX,TRUE: N=184, W=72947; INDEX,MAJ: N=162, W=63308; MOMS,TRUE: N=33, W=20230; MOMS,MAJ: N=11, W=6307. Every member's full output is in the JSONL `predictions` field.

### E3.4: k* = 3, salience low

- **Question tested:** Does accuracy at fixed n and α depend on the size of the smallest backdoor, and does the model choose branching variables by their position in the text?
- **Controlled:** the same logical formula in both presentations (isomorphic); n = 28, m = 119; #solutions, backbone
- **Varied:** k* = 3 (between items); presentation: backdoor variables [26, 27, 28] named and mentioned last
- **Ground truth:** `{"answer": "SAT", "n_solutions": 6, "solutions": ["x1=0 x2=1 x3=0 x4=0 x5=1 x6=1 x7=1 x8=0 x9=0 x10=0 x11=0 x12=0 x13=0 x14=0 x15=1 x16=1 x17=1 x18=1 x19=0 x20=1 x21=0 x22=0 x23=0 x24=0 x25=0 x26=0 x27=0 x28=0", "x1=0 x2=1 x3=0 x4=1 x5=1 x6=1 x7=1 x8=0 x9=0 x10=0 x11=0 x12=0 x13=0 x14=0 x15=1 x16=1 x17=1 x18=1 x19=0 x20=1 x21=0 x22=0 x23=0 x24=0 x25=0 x26=0 x27=0 x28=0", "..."]}`
- **Notes:** Selection-based manipulation. Planting backdoors larger than 2 at α≈4.26 failed: the random fill always created a natural size-2 backdoor. MOMS ties are broken by mention order, so even MOMS can shift slightly between presentations.
- **Same formula as E3.3**, under a renaming of the variables and a reordering of clauses and literals (an isomorphic presentation).

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x28. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x22 OR NOT x24 OR x9)
C2: (x6 OR NOT x12 OR NOT x19)
C3: (x20 OR NOT x11 OR NOT x25)
C4: (NOT x20 OR NOT x12 OR NOT x25)
C5: (NOT x8 OR x10 OR x9)
C6: (x20 OR x11 OR NOT x24)
C7: (x24 OR NOT x5 OR x7)
C8: (x24 OR x4 OR NOT x23)
C9: (NOT x24 OR x10 OR x4)
C10: (x20 OR NOT x15 OR NOT x19)
C11: (NOT x15 OR x16 OR NOT x5)
C12: (x3 OR NOT x19 OR x7)
C13: (x6 OR NOT x16 OR NOT x18)
C14: (NOT x8 OR NOT x24 OR NOT x13)
C15: (NOT x15 OR NOT x21 OR NOT x2)
C16: (NOT x17 OR x24 OR x5)
C17: (x6 OR NOT x12 OR NOT x9)
C18: (NOT x3 OR NOT x10 OR x1)
C19: (NOT x15 OR NOT x19 OR NOT x23)
C20: (NOT x19 OR NOT x24 OR NOT x4)
C21: (NOT x14 OR x17 OR x4)
C22: (NOT x22 OR NOT x11 OR NOT x23)
C23: (x24 OR x5 OR NOT x4)
C24: (x19 OR x5 OR x25)
C25: (NOT x14 OR x3 OR x13)
C26: (x20 OR NOT x11 OR x10)
C27: (NOT x8 OR NOT x16 OR x9)
C28: (x6 OR x3 OR NOT x1)
C29: (NOT x24 OR NOT x25 OR NOT x9)
C30: (NOT x8 OR x14 OR NOT x23)
C31: (x6 OR NOT x12 OR x13)
C32: (x19 OR NOT x24 OR NOT x23)
C33: (x24 OR x5 OR NOT x23)
C34: (x22 OR NOT x2 OR NOT x10)
C35: (NOT x21 OR NOT x7 OR x9)
C36: (x8 OR x17 OR NOT x9)
C37: (x12 OR NOT x9 OR NOT x23)
C38: (x20 OR x22 OR NOT x24)
C39: (x14 OR NOT x13 OR x1)
C40: (NOT x11 OR NOT x2 OR NOT x23)
C41: (x16 OR x1 OR NOT x23)
C42: (NOT x22 OR x17 OR NOT x2)
C43: (NOT x20 OR x12 OR NOT x10)
C44: (NOT x3 OR x21 OR x1)
C45: (x5 OR x7 OR x1)
C46: (NOT x21 OR NOT x7 OR x23)
C47: (NOT x3 OR NOT x5 OR x4)
C48: (NOT x8 OR x20 OR x13)
C49: (x12 OR x10 OR NOT x9)
C50: (x24 OR NOT x21 OR NOT x1)
C51: (x22 OR NOT x19 OR NOT x5)
C52: (NOT x6 OR NOT x22 OR NOT x23)
C53: (x8 OR x17 OR x25)
C54: (x6 OR NOT x19 OR NOT x2)
C55: (x12 OR x19 OR NOT x25)
C56: (NOT x22 OR x21 OR NOT x9)
C57: (x2 OR x25 OR NOT x9)
C58: (NOT x17 OR x13 OR NOT x23)
C59: (NOT x3 OR NOT x7 OR x9)
C60: (NOT x22 OR NOT x11 OR x10)
C61: (x3 OR NOT x24 OR x5)
C62: (NOT x12 OR NOT x19 OR x13)
C63: (x20 OR NOT x15 OR x5)
C64: (x20 OR x2 OR NOT x1)
C65: (NOT x14 OR x15 OR x24)
C66: (x15 OR NOT x16 OR NOT x18)
C67: (x19 OR NOT x13 OR NOT x9)
C68: (NOT x13 OR NOT x9 OR x23)
C69: (x14 OR NOT x3 OR x25)
C70: (NOT x11 OR x19 OR NOT x21)
C71: (x22 OR x10 OR NOT x13)
C72: (NOT x15 OR NOT x3 OR x13)
C73: (x24 OR x21 OR x5)
C74: (x14 OR x5 OR NOT x4)
C75: (NOT x12 OR x17 OR NOT x25)
C76: (x12 OR x10 OR x5)
C77: (NOT x21 OR x7 OR NOT x23)
C78: (NOT x10 OR NOT x25 OR NOT x18)
C79: (x11 OR NOT x17 OR NOT x1)
C80: (NOT x20 OR x24 OR NOT x25)
C81: (x22 OR x5 OR NOT x13)
C82: (NOT x14 OR x21 OR x18)
C83: (NOT x24 OR x10 OR NOT x23)
C84: (NOT x24 OR NOT x16 OR NOT x2)
C85: (NOT x8 OR x23 OR x28)
C86: (NOT x13 OR x26 OR x27)
C87: (NOT x22 OR NOT x18 OR NOT x28)
C88: (NOT x16 OR NOT x9 OR NOT x28)
C89: (NOT x16 OR NOT x18 OR NOT x26)
C90: (NOT x22 OR x27 OR x28)
C91: (x3 OR NOT x21 OR x26)
C92: (x12 OR x25 OR NOT x26)
C93: (x20 OR x22 OR x27)
C94: (NOT x3 OR x18 OR NOT x27)
C95: (x19 OR NOT x1 OR NOT x27)
C96: (x17 OR NOT x24 OR NOT x26)
C97: (NOT x12 OR x10 OR x27)
C98: (NOT x14 OR x13 OR NOT x27)
C99: (x19 OR NOT x23 OR NOT x27)
C100: (NOT x3 OR NOT x11 OR x28)
C101: (x15 OR x26 OR x27)
C102: (x6 OR NOT x24 OR NOT x27)
C103: (x21 OR x18 OR x28)
C104: (x16 OR NOT x23 OR x26)
C105: (x2 OR NOT x18 OR x26)
C106: (NOT x4 OR NOT x18 OR NOT x27)
C107: (x7 OR NOT x27 OR NOT x28)
C108: (NOT x12 OR x9 OR x26)
C109: (x8 OR x17 OR x26)
C110: (NOT x5 OR x18 OR NOT x28)
C111: (x20 OR x19 OR NOT x26)
C112: (NOT x21 OR NOT x2 OR NOT x26)
C113: (x13 OR NOT x18 OR NOT x28)
C114: (x20 OR NOT x10 OR x27)
C115: (x25 OR x7 OR NOT x26)
C116: (x13 OR x1 OR NOT x27)
C117: (x3 OR NOT x11 OR x26)
C118: (x16 OR NOT x18 OR NOT x26)
C119: (NOT x24 OR NOT x27 OR NOT x28)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 6 solutions | π_EXACT = the ceiling share across cells | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=0 x2=1 x3=0 x4=1 x5=1 x6=1 x7=1 x8=0 x9=0 x10=0 x11=0 x12=0 x13=0 x14=0 x15=1 x16=1 x17=1 x18=1 x19=0 x20=1 x21=0 x22=0 x23=0 x24=0 x25=0 x26=0 x27=0 x28=0 after N = 11 nodes (W = 6069); MENTION,MAJ: N = 10. If b < N: the default (UNSAT, or FILL = violates [43, 79, 90, 92, 118] at b = N/2). | π_DPLL from the k* × budget interaction (slope s ≈ 1 per doubling); power > 0.95 to detect s ≥ 0.5, so a null bounds the budget-scaling search component π_DPLL+BACKDOOR ≤ 0.1 (upper 95%). Presentation effect is computed, not assumed: on this formula MENTION,MAJ needs 92 (high) vs 10 (low) nodes, INDEX,MAJ 162 vs 383, MOMS,MAJ 11 vs 11 (high presentation needs MORE MENTION nodes than low) | MOMS,MAJ reference: DEC = 8, BT = 3, CONF = 3, PROP = 39; first decisions (var, value) = [(24, 0), (5, 1), (21, 0)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: UNSAT; w=2: SAT; w=4: SAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: UNSAT (default) | BACKDOOR[k=3,INDEX] (branch on the k lowest-numbered variables): high → SAT, low → UNSAT (default); BACKDOOR[OCC]: no presentation effect | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=28) = 0.16, P(success / k=140) = 0.67, P(success / k=700) = 1.00; modal failure at k=28: violates [24, 61], LM0=True, Hamming to nearest solution = 14 | π_F: no presentation effect (same formula); weak dependence on k* | FULL candidate, VIOL list, FLIP moves; DEC <= 1; #FLIP about the WalkSAT median of 121 |
| MIN-CONFLICTS | P(success / k=28) = 0.01, P(success / k=140) = 0.12, P(success / k=700) = 0.14 | π_F: no presentation effect (same formula); weak dependence on k* | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C68); MENTION,MAJ: SAT; MOMS,TRUE: UNSAT (dead end at C52); MOMS,MAJ: UNSAT (dead end at C110) / CONT violates: MENTION,TRUE: [68, 100]; MENTION,MAJ: []; MOMS,TRUE: [52, 79, 112]; MOMS,MAJ: [110] | π_C = the budget-flat component with accuracy ≈ 2^-k* | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=0 x3=0 x4=1 x5=1 x6=1 x7=1 x8=0 x9=0 x10=0 x11=0 x12=0 x13=1 x14=0 x15=1 x16=1 x17=1 x18=0 x19=1 x20=1 x21=0 x22=1 x23=0 x24=0 x25=1 x26=1 x27=1 x28=1 (violates [79, 80, 110]) | π_C = the budget-flat component with accuracy ≈ 2^-k* | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=0 x3=0 x4=1 x5=1 x6=1 x7=1 x8=0 x9=0 x10=1 x11=0 x12=0 x13=1 x14=0 x15=0 x16=0 x17=1 x18=0 x19=1 x20=1 x21=0 x22=1 x23=0 x24=0 x25=0 x26=1 x27=0 x28=0 (violates [43, 79, 90, 92, 103]) | π_POLARITY: each correct answer where the polarity assignment is infeasible has LR ≈ 0.05 against it | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.545 (eps=1e-4) or 0.002 (eps=1e-3), W = 6069; otherwise a slip (one missed clause, or a spurious conflict) | π_NE = the W-smooth component without a T × k* interaction | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0000 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), DPLL-b[MENTION, b=20, Δ=UNSAT], DPLL-b[MOMS, b=20, Δ=UNSAT], BEAM-2, C-UC/STOP, C-UC/CONT; pushes down DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.013), BACKDOOR[k=k*,INDEX] (LR 0.013), BACKDOOR[k=k*,OCC] (LR 0.013), MIN-CONFLICTS (k=140) (LR 0.131), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *near-miss (infeasible, LM0, V<=3)*: best fit MIN-CONFLICTS (k=140); pushes down EXACT (LR 0.015), DPLL-b (b >= N) (LR 0.015), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.015), DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.015), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.015), BEAM-2 (LR 0.015), BACKDOOR[k=k*,INDEX] (LR 0.015), BACKDOOR[k=k*,OCC] (LR 0.015), C-UC/STOP (LR 0.015), C-UC/CONT (LR 0.015), C-GREEDY (LR 0.015), POLARITY / ALWAYS-SAT (LR 0.015), B1 (UP-k, FLP-1) (LR 0.015), RANDOM (LR 0.015)
- *infeasible (other)*: best fit C-GREEDY, POLARITY / ALWAYS-SAT, RANDOM; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=k*,INDEX] (LR 0.013), BACKDOOR[k=k*,OCC] (LR 0.013), WALK-k (k=140) (LR 0.013), MIN-CONFLICTS (k=140) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013)
- *UNSAT/UNKNOWN*: best fit DPLL-b[INDEX, b=20, Δ=UNSAT], BACKDOOR[k=k*,INDEX], BACKDOOR[k=k*,OCC], B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), WALK-k (k=140) (LR 0.013), MIN-CONFLICTS (k=140) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=126, W=61523; MENTION,MAJ: N=10, W=3451; INDEX,TRUE: N=228, W=115192; INDEX,MAJ: N=383, W=199920; MOMS,TRUE: N=31, W=22967; MOMS,MAJ: N=11, W=6069. Every member's full output is in the JSONL `predictions` field.

### E3.5: k* = 4, salience high

- **Question tested:** Does accuracy at fixed n and α depend on the size of the smallest backdoor, and does the model choose branching variables by their position in the text?
- **Controlled:** the same logical formula in both presentations (isomorphic); n = 28, m = 119; #solutions, backbone
- **Varied:** k* = 4 (between items); presentation: backdoor variables [1, 2, 3, 4] named and mentioned first
- **Ground truth:** `{"answer": "SAT", "n_solutions": 36, "solutions": ["x1=1 x2=0 x3=1 x4=0 x5=0 x6=1 x7=1 x8=0 x9=0 x10=0 x11=1 x12=0 x13=1 x14=1 x15=1 x16=0 x17=0 x18=0 x19=1 x20=0 x21=0 x22=0 x23=1 x24=0 x25=0 x26=1 x27=1 x28=0", "x1=1 x2=0 x3=1 x4=0 x5=0 x6=1 x7=0 x8=0 x9=0 x10=0 x11=1 x12=0 x13=1 x14=0 x15=1 x16=0 x17=0 x18=0 x19=1 x20=0 x21=0 x22=0 x23=1 x24=0 x25=0 x26=1 x27=1 x28=0", "..."]}`
- **Notes:** Selection-based manipulation. Planting backdoors larger than 2 at α≈4.26 failed: the random fill always created a natural size-2 backdoor. MOMS ties are broken by mention order, so even MOMS can shift slightly between presentations.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x28. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x1 OR x3 OR NOT x12)
C2: (NOT x1 OR NOT x4 OR NOT x22)
C3: (x2 OR x3 OR NOT x10)
C4: (x1 OR NOT x3 OR x7)
C5: (x1 OR NOT x3 OR x19)
C6: (x1 OR x4 OR x6)
C7: (x3 OR NOT x4 OR NOT x5)
C8: (x4 OR x20 OR NOT x17)
C9: (NOT x3 OR x5 OR NOT x22)
C10: (x3 OR x6 OR x22)
C11: (NOT x4 OR NOT x25 OR NOT x15)
C12: (x2 OR NOT x25 OR NOT x18)
C13: (x1 OR NOT x6 OR x23)
C14: (NOT x4 OR x14 OR x21)
C15: (NOT x1 OR x25 OR NOT x17)
C16: (NOT x4 OR NOT x9 OR x20)
C17: (x1 OR x5 OR NOT x27)
C18: (NOT x1 OR x6 OR x12)
C19: (NOT x3 OR x26 OR x22)
C20: (x3 OR x26 OR x8)
C21: (NOT x3 OR NOT x9 OR NOT x21)
C22: (NOT x4 OR NOT x6 OR NOT x24)
C23: (NOT x2 OR NOT x12 OR NOT x8)
C24: (NOT x2 OR NOT x16 OR x27)
C25: (x2 OR NOT x7 OR NOT x17)
C26: (NOT x2 OR NOT x11 OR NOT x18)
C27: (x2 OR x13 OR x17)
C28: (x4 OR NOT x20 OR x8)
C29: (NOT x4 OR x20 OR NOT x21)
C30: (NOT x4 OR x20 OR NOT x18)
C31: (x3 OR x25 OR NOT x22)
C32: (x3 OR NOT x28 OR NOT x23)
C33: (x2 OR NOT x27 OR NOT x10)
C34: (NOT x4 OR NOT x26 OR NOT x8)
C35: (x3 OR x19 OR x25)
C36: (x1 OR x6 OR NOT x18)
C37: (NOT x4 OR x23 OR NOT x18)
C38: (NOT x4 OR x19 OR x25)
C39: (x3 OR x14 OR x22)
C40: (NOT x1 OR x14 OR x27)
C41: (NOT x2 OR x13 OR x24)
C42: (x2 OR NOT x14 OR NOT x17)
C43: (x1 OR NOT x9 OR x14)
C44: (x3 OR NOT x9 OR NOT x20)
C45: (NOT x3 OR NOT x5 OR x7)
C46: (NOT x3 OR NOT x26 OR NOT x22)
C47: (NOT x2 OR x9 OR x23)
C48: (x2 OR NOT x9 OR x8)
C49: (NOT x6 OR NOT x17 OR NOT x18)
C50: (x6 OR x7 OR x8)
C51: (x24 OR NOT x12 OR x8)
C52: (NOT x28 OR x11 OR NOT x10)
C53: (x9 OR NOT x28 OR x21)
C54: (x13 OR NOT x21 OR NOT x10)
C55: (NOT x6 OR NOT x24 OR x27)
C56: (NOT x15 OR NOT x8 OR x10)
C57: (x5 OR x27 OR x17)
C58: (NOT x6 OR NOT x11 OR NOT x25)
C59: (NOT x5 OR x9 OR x26)
C60: (x11 OR NOT x26 OR NOT x22)
C61: (x5 OR x11 OR NOT x22)
C62: (x6 OR x9 OR NOT x10)
C63: (NOT x6 OR NOT x15 OR NOT x17)
C64: (NOT x5 OR x18 OR x8)
C65: (x5 OR NOT x24 OR NOT x7)
C66: (NOT x13 OR NOT x8 OR x10)
C67: (NOT x19 OR x13 OR NOT x9)
C68: (NOT x24 OR NOT x27 OR NOT x17)
C69: (x19 OR NOT x12 OR x17)
C70: (x6 OR NOT x14 OR x23)
C71: (NOT x14 OR x16 OR NOT x21)
C72: (x26 OR NOT x16 OR NOT x17)
C73: (x20 OR x23 OR NOT x21)
C74: (x6 OR x28 OR NOT x17)
C75: (NOT x26 OR x15 OR x16)
C76: (NOT x19 OR NOT x7 OR NOT x8)
C77: (x13 OR NOT x24 OR x7)
C78: (x19 OR x26 OR NOT x25)
C79: (NOT x20 OR NOT x15 OR x16)
C80: (NOT x5 OR x9 OR NOT x28)
C81: (x5 OR NOT x23 OR NOT x17)
C82: (x11 OR x26 OR NOT x10)
C83: (NOT x16 OR NOT x7 OR NOT x21)
C84: (NOT x19 OR x12 OR NOT x25)
C85: (x13 OR x26 OR NOT x7)
C86: (NOT x6 OR x13 OR x7)
C87: (NOT x11 OR NOT x16 OR x22)
C88: (x19 OR NOT x12 OR NOT x8)
C89: (NOT x26 OR NOT x27 OR NOT x18)
C90: (x11 OR x16 OR NOT x8)
C91: (x19 OR NOT x5 OR x21)
C92: (NOT x6 OR x27 OR NOT x8)
C93: (NOT x5 OR x20 OR NOT x21)
C94: (x25 OR x7 OR NOT x8)
C95: (x9 OR x15 OR x7)
C96: (NOT x13 OR x20 OR NOT x18)
C97: (x23 OR x25 OR NOT x27)
C98: (x6 OR NOT x20 OR x7)
C99: (NOT x20 OR NOT x12 OR NOT x18)
C100: (NOT x13 OR x11 OR NOT x27)
C101: (x24 OR NOT x12 OR NOT x17)
C102: (x19 OR NOT x28 OR NOT x10)
C103: (x25 OR NOT x17 OR x10)
C104: (NOT x28 OR NOT x14 OR NOT x23)
C105: (x20 OR x15 OR x17)
C106: (x24 OR NOT x16 OR x8)
C107: (x11 OR NOT x23 OR NOT x17)
C108: (x12 OR x23 OR NOT x18)
C109: (NOT x28 OR x12 OR NOT x15)
C110: (NOT x28 OR NOT x15 OR x17)
C111: (x28 OR x27 OR x10)
C112: (x27 OR NOT x8 OR x21)
C113: (NOT x5 OR NOT x15 OR NOT x7)
C114: (x11 OR x12 OR NOT x10)
C115: (NOT x24 OR NOT x26 OR NOT x27)
C116: (NOT x24 OR x26 OR x8)
C117: (x19 OR x17 OR x21)
C118: (x19 OR NOT x23 OR x16)
C119: (NOT x6 OR NOT x9 OR x20)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 36 solutions | π_EXACT = the ceiling share across cells | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=1 x2=1 x3=1 x4=0 x5=0 x6=1 x7=1 x8=0 x9=0 x10=0 x11=1 x12=0 x13=1 x14=1 x15=1 x16=0 x17=0 x18=0 x19=1 x20=0 x21=0 x22=0 x23=1 x24=0 x25=0 x26=1 x27=1 x28=0 after N = 13 nodes (W = 7021); MENTION,MAJ: N = 9. If b < N: the default (UNSAT, or FILL = violates [58, 84, 87, 106] at b = N/2). | π_DPLL from the k* × budget interaction (slope s ≈ 1 per doubling); power > 0.95 to detect s ≥ 0.5, so a null bounds the budget-scaling search component π_DPLL+BACKDOOR ≤ 0.1 (upper 95%). Presentation effect is computed, not assumed: on this formula MENTION,MAJ needs 9 (high) vs 15 (low) nodes, INDEX,MAJ 10 vs 12, MOMS,MAJ 13 vs 13 (high presentation needs fewer MENTION nodes than low) | MOMS,MAJ reference: DEC = 11, BT = 2, CONF = 2, PROP = 45; first decisions (var, value) = [(17, 0), (19, 1), (13, 1)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: UNSAT; w=2: UNSAT; w=4: SAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: UNSAT (default); k=4,OCC: UNSAT (default); k=4,MENTION: SAT; k=4,INDEX: SAT | BACKDOOR[k=4,INDEX] (branch on the k lowest-numbered variables): high → SAT, low → UNSAT (default); BACKDOOR[OCC]: no presentation effect | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=28) = 0.26, P(success / k=140) = 0.64, P(success / k=700) = 0.97; modal failure at k=28: violates [41], LM0=True, Hamming to nearest solution = 11 | π_F: no presentation effect (same formula); weak dependence on k* | FULL candidate, VIOL list, FLIP moves; DEC <= 1; #FLIP about the WalkSAT median of 98 |
| MIN-CONFLICTS | P(success / k=28) = 0.02, P(success / k=140) = 0.19, P(success / k=700) = 0.26 | π_F: no presentation effect (same formula); weak dependence on k* | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C99); MENTION,MAJ: SAT; MOMS,TRUE: UNSAT (dead end at C68); MOMS,MAJ: SAT / CONT violates: MENTION,TRUE: [79, 99, 113]; MENTION,MAJ: []; MOMS,TRUE: [68, 76]; MOMS,MAJ: [111] | π_C = the budget-flat component with accuracy ≈ 2^-k* | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=1 x3=1 x4=0 x5=0 x6=0 x7=1 x8=0 x9=0 x10=0 x11=1 x12=0 x13=1 x14=0 x15=0 x16=0 x17=0 x18=0 x19=1 x20=1 x21=1 x22=0 x23=1 x24=1 x25=1 x26=1 x27=1 x28=1 (violates [18, 28, 65, 75, 84, 115]) | π_C = the budget-flat component with accuracy ≈ 2^-k* | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=1 x4=0 x5=0 x6=1 x7=1 x8=0 x9=0 x10=0 x11=1 x12=0 x13=1 x14=1 x15=0 x16=1 x17=0 x18=0 x19=1 x20=1 x21=0 x22=0 x23=1 x24=0 x25=1 x26=1 x27=1 x28=0 (violates [28, 58, 84, 87, 106]) | π_POLARITY: each correct answer where the polarity assignment is infeasible has LR ≈ 0.05 against it | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.496 (eps=1e-4) or 0.001 (eps=1e-3), W = 7021; otherwise a slip (one missed clause, or a spurious conflict) | π_NE = the W-smooth component without a T × k* interaction | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0000 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), DPLL-b[MENTION, b=20, Δ=UNSAT], DPLL-b[INDEX, b=20, Δ=UNSAT], DPLL-b[MOMS, b=20, Δ=UNSAT], BACKDOOR[k=k*,INDEX], C-UC/STOP, C-UC/CONT; pushes down BEAM-2 (LR 0.013), BACKDOOR[k=k*,OCC] (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *near-miss (infeasible, LM0, V<=3)*: best fit MIN-CONFLICTS (k=140); pushes down EXACT (LR 0.016), DPLL-b (b >= N) (LR 0.016), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.016), DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.016), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.016), BEAM-2 (LR 0.016), BACKDOOR[k=k*,INDEX] (LR 0.016), BACKDOOR[k=k*,OCC] (LR 0.016), WALK-k (k=140) (LR 0.016), C-UC/STOP (LR 0.016), C-UC/CONT (LR 0.016), C-GREEDY (LR 0.016), POLARITY / ALWAYS-SAT (LR 0.016), B1 (UP-k, FLP-1) (LR 0.016), RANDOM (LR 0.016)
- *infeasible (other)*: best fit C-GREEDY, POLARITY / ALWAYS-SAT, RANDOM; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=k*,INDEX] (LR 0.013), BACKDOOR[k=k*,OCC] (LR 0.013), MIN-CONFLICTS (k=140) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013)
- *UNSAT/UNKNOWN*: best fit BEAM-2, BACKDOOR[k=k*,OCC], B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.013), BACKDOOR[k=k*,INDEX] (LR 0.013), WALK-k (k=140) (LR 0.013), MIN-CONFLICTS (k=140) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=20, W=13685; MENTION,MAJ: N=9, W=3332; INDEX,TRUE: N=7, W=4522; INDEX,MAJ: N=10, W=4046; MOMS,TRUE: N=25, W=17136; MOMS,MAJ: N=13, W=7021. Every member's full output is in the JSONL `predictions` field.

### E3.6: k* = 4, salience low

- **Question tested:** Does accuracy at fixed n and α depend on the size of the smallest backdoor, and does the model choose branching variables by their position in the text?
- **Controlled:** the same logical formula in both presentations (isomorphic); n = 28, m = 119; #solutions, backbone
- **Varied:** k* = 4 (between items); presentation: backdoor variables [25, 26, 27, 28] named and mentioned last
- **Ground truth:** `{"answer": "SAT", "n_solutions": 36, "solutions": ["x1=0 x2=1 x3=0 x4=0 x5=0 x6=0 x7=1 x8=0 x9=1 x10=1 x11=1 x12=0 x13=0 x14=0 x15=1 x16=0 x17=0 x18=0 x19=1 x20=0 x21=0 x22=1 x23=1 x24=0 x25=1 x26=0 x27=1 x28=0", "x1=0 x2=1 x3=0 x4=0 x5=0 x6=0 x7=1 x8=0 x9=1 x10=0 x11=1 x12=0 x13=0 x14=0 x15=1 x16=0 x17=0 x18=0 x19=1 x20=0 x21=0 x22=1 x23=1 x24=0 x25=1 x26=0 x27=1 x28=0", "..."]}`
- **Notes:** Selection-based manipulation. Planting backdoors larger than 2 at α≈4.26 failed: the random fill always created a natural size-2 backdoor. MOMS ties are broken by mention order, so even MOMS can shift slightly between presentations.
- **Same formula as E3.5**, under a renaming of the variables and a reordering of clauses and literals (an isomorphic presentation).

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x28. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (NOT x2 OR NOT x13 OR NOT x14)
C2: (x2 OR x3 OR x4)
C3: (x20 OR NOT x8 OR x4)
C4: (NOT x24 OR x7 OR NOT x6)
C5: (x5 OR NOT x24 OR x17)
C6: (x9 OR NOT x17 OR NOT x6)
C7: (NOT x2 OR NOT x20 OR x23)
C8: (NOT x11 OR NOT x4 OR x6)
C9: (x1 OR x23 OR x13)
C10: (NOT x2 OR NOT x7 OR NOT x21)
C11: (NOT x1 OR x5 OR x22)
C12: (x7 OR NOT x22 OR NOT x18)
C13: (x1 OR x7 OR NOT x18)
C14: (x2 OR x5 OR NOT x6)
C15: (NOT x2 OR NOT x11 OR NOT x13)
C16: (NOT x1 OR x14 OR x4)
C17: (x1 OR NOT x20 OR NOT x3)
C18: (NOT x9 OR NOT x4 OR x6)
C19: (NOT x15 OR x9 OR NOT x5)
C20: (NOT x20 OR NOT x23 OR NOT x13)
C21: (x15 OR NOT x8 OR x13)
C22: (x2 OR NOT x10 OR x19)
C23: (NOT x10 OR x12 OR NOT x17)
C24: (x22 OR NOT x12 OR NOT x13)
C25: (x16 OR x19 OR NOT x17)
C26: (x2 OR x24 OR NOT x13)
C27: (NOT x22 OR x11 OR x12)
C28: (NOT x15 OR NOT x3 OR NOT x4)
C29: (x9 OR NOT x20 OR x3)
C30: (x15 OR x22 OR NOT x21)
C31: (NOT x16 OR NOT x11 OR x12)
C32: (NOT x1 OR x5 OR NOT x24)
C33: (x1 OR NOT x19 OR NOT x13)
C34: (x7 OR x22 OR NOT x6)
C35: (NOT x12 OR NOT x3 OR NOT x17)
C36: (NOT x15 OR x8 OR NOT x21)
C37: (x9 OR x22 OR NOT x3)
C38: (NOT x2 OR x9 OR x3)
C39: (NOT x7 OR NOT x12 OR x18)
C40: (x15 OR NOT x8 OR NOT x4)
C41: (NOT x22 OR NOT x23 OR NOT x14)
C42: (x7 OR x12 OR NOT x4)
C43: (x15 OR NOT x1 OR x17)
C44: (NOT x2 OR x23 OR NOT x4)
C45: (NOT x1 OR x16 OR NOT x17)
C46: (x21 OR x3 OR NOT x4)
C47: (x5 OR x11 OR x3)
C48: (NOT x9 OR x16 OR NOT x14)
C49: (x19 OR x21 OR NOT x23)
C50: (x2 OR NOT x16 OR x3)
C51: (NOT x16 OR NOT x8 OR NOT x14)
C52: (NOT x9 OR x7 OR NOT x23)
C53: (x20 OR NOT x8 OR NOT x13)
C54: (x15 OR NOT x24 OR NOT x6)
C55: (x21 OR NOT x13 OR x6)
C56: (NOT x24 OR NOT x10 OR NOT x19)
C57: (x16 OR x11 OR x13)
C58: (x20 OR NOT x12 OR x4)
C59: (x7 OR NOT x19 OR NOT x13)
C60: (x8 OR x19 OR NOT x14)
C61: (NOT x24 OR x8 OR NOT x11)
C62: (NOT x24 OR NOT x11 OR x13)
C63: (x24 OR x23 OR x6)
C64: (x23 OR NOT x4 OR x17)
C65: (NOT x1 OR NOT x11 OR NOT x3)
C66: (x7 OR x8 OR NOT x6)
C67: (NOT x20 OR NOT x22 OR NOT x23)
C68: (NOT x20 OR x22 OR x4)
C69: (x15 OR x13 OR x17)
C70: (x15 OR NOT x19 OR x12)
C71: (NOT x2 OR NOT x5 OR x16)
C72: (x16 OR NOT x13 OR x28)
C73: (x1 OR NOT x18 OR NOT x27)
C74: (x2 OR x18 OR x27)
C75: (NOT x21 OR NOT x11 OR NOT x28)
C76: (NOT x21 OR NOT x14 OR x26)
C77: (NOT x2 OR x19 OR x25)
C78: (x10 OR x17 OR NOT x28)
C79: (x21 OR NOT x13 OR NOT x25)
C80: (NOT x5 OR x16 OR NOT x28)
C81: (x1 OR NOT x23 OR x25)
C82: (x2 OR x8 OR NOT x25)
C83: (x22 OR x18 OR NOT x27)
C84: (x22 OR x4 OR x27)
C85: (NOT x5 OR NOT x17 OR NOT x27)
C86: (NOT x2 OR NOT x20 OR NOT x28)
C87: (NOT x8 OR NOT x4 OR NOT x26)
C88: (NOT x12 OR x23 OR NOT x26)
C89: (NOT x3 OR NOT x13 OR x26)
C90: (NOT x7 OR NOT x14 OR NOT x26)
C91: (x9 OR x13 OR x26)
C92: (NOT x16 OR x4 OR x28)
C93: (x16 OR NOT x17 OR NOT x28)
C94: (NOT x8 OR x25 OR x27)
C95: (x16 OR NOT x14 OR NOT x28)
C96: (x21 OR NOT x18 OR x27)
C97: (NOT x24 OR NOT x19 OR x27)
C98: (NOT x23 OR NOT x6 OR x26)
C99: (NOT x22 OR NOT x4 OR NOT x28)
C100: (NOT x18 OR NOT x25 OR NOT x28)
C101: (x15 OR x21 OR x27)
C102: (NOT x6 OR x26 OR x27)
C103: (x2 OR NOT x14 OR x25)
C104: (x19 OR NOT x14 OR NOT x28)
C105: (x15 OR x21 OR NOT x28)
C106: (x10 OR x18 OR x27)
C107: (x3 OR x25 OR NOT x27)
C108: (x15 OR x25 OR NOT x27)
C109: (x10 OR x23 OR NOT x25)
C110: (x9 OR x20 OR NOT x26)
C111: (NOT x10 OR NOT x13 OR x26)
C112: (NOT x5 OR x10 OR x25)
C113: (x2 OR x25 OR x28)
C114: (NOT x5 OR NOT x16 OR x27)
C115: (NOT x1 OR x27 OR NOT x28)
C116: (NOT x1 OR x3 OR NOT x27)
C117: (NOT x22 OR NOT x18 OR NOT x27)
C118: (x5 OR x19 OR NOT x26)
C119: (NOT x5 OR x4 OR x26)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 36 solutions | π_EXACT = the ceiling share across cells | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=0 x2=1 x3=1 x4=0 x5=0 x6=0 x7=1 x8=0 x9=1 x10=1 x11=1 x12=0 x13=0 x14=0 x15=1 x16=0 x17=0 x18=0 x19=1 x20=0 x21=0 x22=1 x23=1 x24=0 x25=1 x26=1 x27=1 x28=0 after N = 13 nodes (W = 8330); MENTION,MAJ: N = 15. If b < N: the default (UNSAT, or FILL = violates [10, 36, 39, 58] at b = N/2). | π_DPLL from the k* × budget interaction (slope s ≈ 1 per doubling); power > 0.95 to detect s ≥ 0.5, so a null bounds the budget-scaling search component π_DPLL+BACKDOOR ≤ 0.1 (upper 95%). Presentation effect is computed, not assumed: on this formula MENTION,MAJ needs 9 (high) vs 15 (low) nodes, INDEX,MAJ 10 vs 12, MOMS,MAJ 13 vs 13 (high presentation needs fewer MENTION nodes than low) | MOMS,MAJ reference: DEC = 11, BT = 2, CONF = 2, PROP = 56; first decisions (var, value) = [(13, 0), (15, 1), (9, 1)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: UNSAT; w=2: UNSAT; w=4: SAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: UNSAT (default); k=4,OCC: UNSAT (default); k=4,MENTION: UNSAT (default); k=4,INDEX: UNSAT (default) | BACKDOOR[k=4,INDEX] (branch on the k lowest-numbered variables): high → SAT, low → UNSAT (default); BACKDOOR[OCC]: no presentation effect | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=28) = 0.21, P(success / k=140) = 0.70, P(success / k=700) = 0.99; modal failure at k=28: violates [18, 50, 73], LM0=True, Hamming to nearest solution = 11 | π_F: no presentation effect (same formula); weak dependence on k* | FULL candidate, VIOL list, FLIP moves; DEC <= 1; #FLIP about the WalkSAT median of 81 |
| MIN-CONFLICTS | P(success / k=28) = 0.00, P(success / k=140) = 0.25, P(success / k=700) = 0.25 | π_F: no presentation effect (same formula); weak dependence on k* | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C70); MENTION,MAJ: SAT; MOMS,TRUE: UNSAT (dead end at C20); MOMS,MAJ: SAT / CONT violates: MENTION,TRUE: [70, 101, 106, 112, 114]; MENTION,MAJ: []; MOMS,TRUE: [20, 70, 101, 106, 112, 114]; MOMS,MAJ: [63] | π_C = the budget-flat component with accuracy ≈ 2^-k* | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=0 x2=1 x3=1 x4=0 x5=0 x6=0 x7=1 x8=1 x9=1 x10=1 x11=0 x12=0 x13=0 x14=0 x15=1 x16=1 x17=0 x18=0 x19=1 x20=0 x21=1 x22=1 x23=1 x24=0 x25=1 x26=1 x27=1 x28=1 (violates [3, 10, 27]) | π_C = the budget-flat component with accuracy ≈ 2^-k* | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=0 x2=1 x3=1 x4=0 x5=0 x6=0 x7=1 x8=0 x9=1 x10=1 x11=0 x12=1 x13=0 x14=0 x15=1 x16=1 x17=0 x18=0 x19=1 x20=0 x21=1 x22=1 x23=1 x24=0 x25=1 x26=1 x27=1 x28=0 (violates [10, 36, 39, 58, 92]) | π_POLARITY: each correct answer where the polarity assignment is infeasible has LR ≈ 0.05 against it | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.435 (eps=1e-4) or 0.0 (eps=1e-3), W = 8330; otherwise a slip (one missed clause, or a spurious conflict) | π_NE = the W-smooth component without a T × k* interaction | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0000 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), DPLL-b[MENTION, b=20, Δ=UNSAT], DPLL-b[INDEX, b=20, Δ=UNSAT], DPLL-b[MOMS, b=20, Δ=UNSAT], C-UC/STOP, C-UC/CONT; pushes down BEAM-2 (LR 0.013), BACKDOOR[k=k*,INDEX] (LR 0.013), BACKDOOR[k=k*,OCC] (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *near-miss (infeasible, LM0, V<=3)*: best fit MIN-CONFLICTS (k=140); pushes down EXACT (LR 0.017), DPLL-b (b >= N) (LR 0.017), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.017), DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.017), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.017), BEAM-2 (LR 0.017), BACKDOOR[k=k*,INDEX] (LR 0.017), BACKDOOR[k=k*,OCC] (LR 0.017), C-UC/STOP (LR 0.017), C-UC/CONT (LR 0.017), C-GREEDY (LR 0.017), POLARITY / ALWAYS-SAT (LR 0.017), B1 (UP-k, FLP-1) (LR 0.017), RANDOM (LR 0.017)
- *infeasible (other)*: best fit C-GREEDY, POLARITY / ALWAYS-SAT, RANDOM; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=k*,INDEX] (LR 0.013), BACKDOOR[k=k*,OCC] (LR 0.013), WALK-k (k=140) (LR 0.013), MIN-CONFLICTS (k=140) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013)
- *UNSAT/UNKNOWN*: best fit BEAM-2, BACKDOOR[k=k*,INDEX], BACKDOOR[k=k*,OCC], B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), DPLL-b[MENTION, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[INDEX, b=20, Δ=UNSAT] (LR 0.013), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.013), WALK-k (k=140) (LR 0.013), MIN-CONFLICTS (k=140) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=35, W=22253; MENTION,MAJ: N=15, W=3094; INDEX,TRUE: N=31, W=22253; INDEX,MAJ: N=12, W=3094; MOMS,TRUE: N=25, W=19873; MOMS,MAJ: N=13, W=8330. Every member's full output is in the JSONL `predictions` field.

---

## E4

### Trap pairs: backtracking necessity

| Item | Cell | Ground truth | Varied |
|------|------|--------------|--------|
| E4.1 | d = 2, t = 1, trap arm | SAT (48 solutions) | 2 literal signs per trap (clauses [26, 28]) swap which gadget is live; d = 2 (chain length); t = 1 (traps) |
| E4.2 | d = 2, t = 1, control arm | SAT (92 solutions) | 2 literal signs per trap (clauses [26, 28]) swap which gadget is live; d = 2 (chain length); t = 1 (traps) |
| E4.3 | d = 2, t = 2, trap arm | SAT (1280 solutions) | 2 literal signs per trap (clauses [4, 19, 27, 48]) swap which gadget is live; d = 2 (chain length); t = 2 (traps) |
| E4.4 | d = 2, t = 2, control arm | SAT (1536 solutions) | 2 literal signs per trap (clauses [4, 19, 27, 48]) swap which gadget is live; d = 2 (chain length); t = 2 (traps) |
| E4.5 | d = 4, t = 1, trap arm | SAT (1088 solutions) | 2 literal signs per trap (clauses [21, 47]) swap which gadget is live; d = 4 (chain length); t = 1 (traps) |
| E4.6 | d = 4, t = 1, control arm | SAT (1920 solutions) | 2 literal signs per trap (clauses [21, 47]) swap which gadget is live; d = 4 (chain length); t = 1 (traps) |
| E4.7 | d = 4, t = 2, trap arm | SAT (2000 solutions) | 2 literal signs per trap (clauses [12, 30, 73, 84]) swap which gadget is live; d = 4 (chain length); t = 2 (traps) |
| E4.8 | d = 4, t = 2, control arm | SAT (2000 solutions) | 2 literal signs per trap (clauses [12, 30, 73, 84]) swap which gadget is live; d = 4 (chain length); t = 2 (traps) |

**Direction table** (how each set-level outcome moves weight; the sizes are in the likelihood-ratio table below and in each item's hypothesis block):

| Observed outcome (set level) | Moves weight toward | Moves weight away from |
|------------------------------|---------------------|------------------------|
| Δ ≈ 0, with BT on the trap variable in the trap arm and none in the control arm | DPLL-b (and BEAM at t = 1) | C-UC, C-GREEDY, POLARITY (all fail the trap arm by construction) |
| Δ >= 0.15, trap-arm errors are dead ends with the trap variable = 1 | C | DPLL-b, NOISY-EXACT (Δ <= 0.02), EXACT |
| Trap arm lower, errors LM0 near-misses, falling with d at every budget | WALK-k / MIN-CONFLICTS | DPLL-b (fails the trap only via budget), C (dead ends are not LM0) |
| Deferred t=2 pairs: trap-arm failures with CASES traces and no BT | BEAM-w (w < 4) | DPLL-b |
| Δ ≈ 0 but no BT in any trace | unverbalised search or sound lookahead | C; and flags the trace as unfaithful (go to E8 / Phase 2) |

**Likelihood-ratio table** (computed). Each row asks: if one response per item (E4.1, E4.2, E4.3, E4.4, E4.5, E4.6, E4.7, E4.8) matched theory *h*'s most likely outcome, how much less likely is that pattern under each competitor? Entries are log10 LR(competitor : h), with a 5% slip floor on every theory, so −1.0 means the pattern pushes that competitor's weight down 10× relative to *h*. A cell of N independent responses multiplies these by about N. The readout is the mixture posterior over π, not a verdict (D_F_search.md §2.5).

| If responses match the modal pattern of h = | Tied with h (0.0) | Weakly disfavoured (−1 < log10 LR < 0) | Pushed down ≥ 10× (log10 LR ≤ −1) |
|---------------------------------------------|-------------------|----------------------------------------|-----------------------------------|
| EXACT | DPLL-b (b >= N) | NOISY-EXACT (-0.5) | BEAM-2 (-1.9), BACKDOOR[k=2,OCC] (-15.1), C-UC/STOP (-7.5), C-UC/CONT (-7.5), C-GREEDY (-11.3), POLARITY / ALWAYS-SAT (-15.1), B1 (UP-k, FLP-1) (-15.1), RANDOM (-14.9) |
| DPLL-b (b >= N) | EXACT | NOISY-EXACT (-0.5) | BEAM-2 (-1.9), BACKDOOR[k=2,OCC] (-15.1), C-UC/STOP (-7.5), C-UC/CONT (-7.5), C-GREEDY (-11.3), POLARITY / ALWAYS-SAT (-15.1), B1 (UP-k, FLP-1) (-15.1), RANDOM (-14.9) |
| BEAM-2 | — | — | EXACT (-1.9), DPLL-b (b >= N) (-1.9), BACKDOOR[k=2,OCC] (-13.2), C-UC/STOP (-9.4), C-UC/CONT (-9.4), C-GREEDY (-13.2), POLARITY / ALWAYS-SAT (-15.1), B1 (UP-k, FLP-1) (-13.2), NOISY-EXACT (-2.4), RANDOM (-14.9) |
| BACKDOOR[k=2,OCC] | B1 (UP-k, FLP-1) | — | EXACT (-15.1), DPLL-b (b >= N) (-15.1), BEAM-2 (-13.2), C-UC/STOP (-7.5), C-UC/CONT (-15.1), C-GREEDY (-15.1), POLARITY / ALWAYS-SAT (-15.1), NOISY-EXACT (-15.1), RANDOM (-15.1) |
| C-UC/STOP | — | — | EXACT (-7.5), DPLL-b (b >= N) (-7.5), BEAM-2 (-9.4), BACKDOOR[k=2,OCC] (-7.5), C-UC/CONT (-7.5), C-GREEDY (-11.3), POLARITY / ALWAYS-SAT (-15.1), B1 (UP-k, FLP-1) (-7.5), NOISY-EXACT (-7.7), RANDOM (-15.0) |
| C-UC/CONT | — | — | EXACT (-7.5), DPLL-b (b >= N) (-7.5), BEAM-2 (-9.4), BACKDOOR[k=2,OCC] (-15.1), C-UC/STOP (-7.5), C-GREEDY (-3.8), POLARITY / ALWAYS-SAT (-9.4), B1 (UP-k, FLP-1) (-15.1), NOISY-EXACT (-4.4), RANDOM (-9.3) |
| C-GREEDY | — | — | EXACT (-11.3), DPLL-b (b >= N) (-11.3), BEAM-2 (-13.2), BACKDOOR[k=2,OCC] (-15.1), C-UC/STOP (-11.3), C-UC/CONT (-3.8), POLARITY / ALWAYS-SAT (-7.5), B1 (UP-k, FLP-1) (-15.1), NOISY-EXACT (-6.5), RANDOM (-7.5) |
| POLARITY / ALWAYS-SAT | RANDOM | — | EXACT (-15.1), DPLL-b (b >= N) (-15.1), BEAM-2 (-15.1), BACKDOOR[k=2,OCC] (-15.1), C-UC/STOP (-15.1), C-UC/CONT (-9.4), C-GREEDY (-7.5), B1 (UP-k, FLP-1) (-15.1), NOISY-EXACT (-9.1) |
| B1 (UP-k, FLP-1) | BACKDOOR[k=2,OCC] | — | EXACT (-15.1), DPLL-b (b >= N) (-15.1), BEAM-2 (-13.2), C-UC/STOP (-7.5), C-UC/CONT (-15.1), C-GREEDY (-15.1), POLARITY / ALWAYS-SAT (-15.1), NOISY-EXACT (-15.1), RANDOM (-15.1) |
| NOISY-EXACT | — | — | BEAM-2 (-1.3), BACKDOOR[k=2,OCC] (-14.5), C-UC/STOP (-7.0), C-UC/CONT (-7.0), C-GREEDY (-10.8), POLARITY / ALWAYS-SAT (-14.5), B1 (UP-k, FLP-1) (-14.5), RANDOM (-14.4) |
| RANDOM | POLARITY / ALWAYS-SAT | — | EXACT (-15.1), DPLL-b (b >= N) (-15.1), BEAM-2 (-15.1), BACKDOOR[k=2,OCC] (-15.1), C-UC/STOP (-15.1), C-UC/CONT (-9.4), C-GREEDY (-7.5), B1 (UP-k, FLP-1) (-15.1), NOISY-EXACT (-9.1) |

**Not distinguished by this set:** DPLL-b vs NOISY-EXACT: both give Δ ≈ 0 here; separated by E1/E2/E3 budget interactions and E6 profiles.

### E4.1: d = 2, t = 1, trap arm

- **Question tested:** When the value every greedy rule picks first is a dead end revealed only after another decision, does the model backtrack?
- **Controlled:** the same variable names and clause order in both arms; the trap variable's polarity counts, occurrence and first mention; n, m, clause length 3; both arms SAT
- **Varied:** 2 literal signs per trap (clauses [26, 28]) swap which gadget is live; d = 2 (chain length); t = 1 (traps)
- **Ground truth:** `{"answer": "SAT", "n_solutions": 48, "solutions": ["x1=0 x2=1 x3=0 x4=1 x5=1 x6=1 x7=0 x8=1 x9=0 x10=1 x11=1 x12=1 x13=0 x14=0 x15=0", "x1=0 x2=1 x3=1 x4=1 x5=1 x6=1 x7=0 x8=1 x9=0 x10=1 x11=1 x12=1 x13=0 x14=0 x15=0", "..."]}`

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x15. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x1 OR x11 OR NOT x2)
C2: (x7 OR x5 OR x8)
C3: (NOT x7 OR x1 OR NOT x2)
C4: (NOT x8 OR NOT x15 OR x6)
C5: (x13 OR x1 OR x4)
C6: (x8 OR NOT x2 OR x14)
C7: (x9 OR NOT x7 OR NOT x8)
C8: (x2 OR NOT x8 OR x7)
C9: (x13 OR x2 OR x14)
C10: (x6 OR NOT x14 OR NOT x10)
C11: (x5 OR x1 OR x6)
C12: (x5 OR x7 OR x14)
C13: (x14 OR x11 OR NOT x6)
C14: (NOT x11 OR x7 OR x10)
C15: (NOT x10 OR NOT x8 OR x11)
C16: (x7 OR x8 OR NOT x6)
C17: (x1 OR x10 OR x6)
C18: (NOT x1 OR NOT x15 OR x9)
C19: (x10 OR x4 OR x2)
C20: (x2 OR NOT x5 OR NOT x14)
C21: (NOT x7 OR x8 OR x1)
C22: (x5 OR NOT x7 OR NOT x1)
C23: (NOT x10 OR x2 OR NOT x14)
C24: (NOT x7 OR x6 OR NOT x8)
C25: (x11 OR NOT x8 OR NOT x6)
C26: (x1 OR x4 OR NOT x12)
C27: (x2 OR NOT x6 OR x14)
C28: (NOT x1 OR NOT x15 OR NOT x9)
C29: (NOT x5 OR NOT x7 OR x6)
C30: (x3 OR NOT x7 OR x10)
C31: (NOT x7 OR NOT x11 OR NOT x14)
C32: (x6 OR NOT x1 OR NOT x10)
C33: (x5 OR NOT x11 OR NOT x7)
C34: (x2 OR x12 OR NOT x6)
C35: (x3 OR x15 OR NOT x1)
C36: (NOT x14 OR x10 OR x8)
C37: (x11 OR NOT x8 OR x5)
C38: (x1 OR x2 OR x8)
C39: (x6 OR NOT x11 OR NOT x10)
C40: (NOT x1 OR x15 OR NOT x3)
C41: (x1 OR x12 OR NOT x4)
C42: (x1 OR NOT x13 OR x4)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 48 solutions | π_EXACT = the ceiling share in both arms | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=0 x2=1 x3=1 x4=1 x5=1 x6=1 x7=0 x8=1 x9=1 x10=1 x11=1 x12=1 x13=1 x14=1 x15=0 after N = 7 nodes (W = 672); MENTION,MAJ: N = 34. If b < N: the default (UNSAT, or FILL = violates [16, 40] at b = N/2). | π_C ≈ Δ = acc(control) − acc(trap), estimated per model; power 0.9 to detect π_C ≥ 0.10 with 300 pairs; if Δ̂ ≈ 0 the set bounds π_C ≤ 0.07 (upper 95%) and the backtracking share of the remaining weight is read from BT-on-v traces weighted by R_m | trap arm: DEC x1=1, then a DEC on a core variable, CONF, BT, CONF, BT to x1=0 (reference BTs on trap vars per variant: {'MENTION,TRUE': 1, 'MENTION,MAJ': 1, 'INDEX,TRUE': 1, 'INDEX,MAJ': 1, 'MOMS,TRUE': 1, 'MOMS,MAJ': 1}); control arm: no BT on the trap variable |
| BEAM-w | w=1: UNSAT; w=2: SAT; w=4: SAT | BEAM-1/BEAM-2 predictions differ from DPLL-b on specific items (listed in its output); deferred-conflict cells were not produced by this generator | CASES carried in parallel; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: SAT; k=3,OCC: SAT; k=3,MENTION: SAT; k=3,INDEX: SAT | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=15) = 0.49, P(success / k=75) = 0.94, P(success / k=375) = 1.00; modal failure at k=15: violates [35], LM0=True, Hamming to nearest solution = 4 | π_F from LM0 near-miss trap errors, whose share should grow with d (barrier height) | x1 changes by FLIP inside a full candidate, never by BT |
| MIN-CONFLICTS | P(success / k=15) = 0.23, P(success / k=75) = 0.35, P(success / k=375) = 0.37 | π_F from LM0 near-miss trap errors, whose share should grow with d (barrier height) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C40); MENTION,MAJ: UNSAT (dead end at C28); MOMS,TRUE: UNSAT (dead end at C28); MOMS,MAJ: UNSAT (dead end at C40) / CONT violates: MENTION,TRUE: [40]; MENTION,MAJ: [28]; MOMS,TRUE: [28]; MOMS,MAJ: [40] | π_C ≈ Δ, with trap-arm errors dead-end-typed (x_v = 1); each dead-end trap error has LR ≈ 20 for C over DPLL-b | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=0 x8=1 x9=1 x10=1 x11=1 x12=1 x13=1 x14=1 x15=0 (violates [40]) | π_C ≈ Δ, with trap-arm errors dead-end-typed (x_v = 1); each dead-end trap error has LR ≈ 20 for C over DPLL-b | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=0 x8=0 x9=1 x10=1 x11=1 x12=1 x13=1 x14=1 x15=0 (violates [16, 40]) | π_POLARITY bounded by control-arm successes (POLARITY fails the control arm by construction) | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.935 (eps=1e-4) or 0.511 (eps=1e-3), W = 672; otherwise a slip (one missed clause, or a spurious conflict) | π_NE contributes Δ ≤ 0.02 (tiny extra work): not separable from DPLL-b here (see E1–E3) | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0015 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), BEAM-2; pushes down BACKDOOR[k=2,OCC] (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.014)
- *near-miss (infeasible, LM0, V<=3)*: best fit MIN-CONFLICTS (k=75); pushes down EXACT (LR 0.02), DPLL-b (b >= N) (LR 0.02), BEAM-2 (LR 0.02), BACKDOOR[k=2,OCC] (LR 0.02), WALK-k (k=75) (LR 0.11), C-UC/STOP (LR 0.02), C-UC/CONT (LR 0.02), C-GREEDY (LR 0.02), POLARITY / ALWAYS-SAT (LR 0.02), B1 (UP-k, FLP-1) (LR 0.02), NOISY-EXACT (LR 0.069), RANDOM (LR 0.02)
- *infeasible (other)*: best fit C-UC/CONT, C-GREEDY, POLARITY / ALWAYS-SAT; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=75) (LR 0.013), MIN-CONFLICTS (k=75) (LR 0.013), C-UC/STOP (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.045)
- *UNSAT/UNKNOWN*: best fit BACKDOOR[k=2,OCC], C-UC/STOP, B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), WALK-k (k=75) (LR 0.013), MIN-CONFLICTS (k=75) (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=34, W=3864; MENTION,MAJ: N=34, W=3864; INDEX,TRUE: N=11, W=1092; INDEX,MAJ: N=11, W=1092; MOMS,TRUE: N=7, W=672; MOMS,MAJ: N=7, W=672. Every member's full output is in the JSONL `predictions` field.

### E4.2: d = 2, t = 1, control arm

- **Question tested:** When the value every greedy rule picks first is a dead end revealed only after another decision, does the model backtrack?
- **Controlled:** the same variable names and clause order in both arms; the trap variable's polarity counts, occurrence and first mention; n, m, clause length 3; both arms SAT
- **Varied:** 2 literal signs per trap (clauses [26, 28]) swap which gadget is live; d = 2 (chain length); t = 1 (traps)
- **Ground truth:** `{"answer": "SAT", "n_solutions": 92, "solutions": ["x1=1 x2=1 x3=1 x4=0 x5=1 x6=1 x7=1 x8=1 x9=1 x10=0 x11=1 x12=0 x13=0 x14=0 x15=1", "x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=1 x8=1 x9=1 x10=0 x11=1 x12=0 x13=0 x14=0 x15=1", "..."]}`
- **Differs from E4.1 only in:** C26: (x1 OR x4 OR NOT x12) → (x1 OR NOT x4 OR NOT x12); C28: (NOT x1 OR NOT x15 OR NOT x9) → (NOT x1 OR x15 OR NOT x9)

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x15. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x1 OR x11 OR NOT x2)
C2: (x7 OR x5 OR x8)
C3: (NOT x7 OR x1 OR NOT x2)
C4: (NOT x8 OR NOT x15 OR x6)
C5: (x13 OR x1 OR x4)
C6: (x8 OR NOT x2 OR x14)
C7: (x9 OR NOT x7 OR NOT x8)
C8: (x2 OR NOT x8 OR x7)
C9: (x13 OR x2 OR x14)
C10: (x6 OR NOT x14 OR NOT x10)
C11: (x5 OR x1 OR x6)
C12: (x5 OR x7 OR x14)
C13: (x14 OR x11 OR NOT x6)
C14: (NOT x11 OR x7 OR x10)
C15: (NOT x10 OR NOT x8 OR x11)
C16: (x7 OR x8 OR NOT x6)
C17: (x1 OR x10 OR x6)
C18: (NOT x1 OR NOT x15 OR x9)
C19: (x10 OR x4 OR x2)
C20: (x2 OR NOT x5 OR NOT x14)
C21: (NOT x7 OR x8 OR x1)
C22: (x5 OR NOT x7 OR NOT x1)
C23: (NOT x10 OR x2 OR NOT x14)
C24: (NOT x7 OR x6 OR NOT x8)
C25: (x11 OR NOT x8 OR NOT x6)
C26: (x1 OR NOT x4 OR NOT x12)
C27: (x2 OR NOT x6 OR x14)
C28: (NOT x1 OR x15 OR NOT x9)
C29: (NOT x5 OR NOT x7 OR x6)
C30: (x3 OR NOT x7 OR x10)
C31: (NOT x7 OR NOT x11 OR NOT x14)
C32: (x6 OR NOT x1 OR NOT x10)
C33: (x5 OR NOT x11 OR NOT x7)
C34: (x2 OR x12 OR NOT x6)
C35: (x3 OR x15 OR NOT x1)
C36: (NOT x14 OR x10 OR x8)
C37: (x11 OR NOT x8 OR x5)
C38: (x1 OR x2 OR x8)
C39: (x6 OR NOT x11 OR NOT x10)
C40: (NOT x1 OR x15 OR NOT x3)
C41: (x1 OR x12 OR NOT x4)
C42: (x1 OR NOT x13 OR x4)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 92 solutions | π_EXACT = the ceiling share in both arms | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=1 x8=0 x9=1 x10=1 x11=0 x12=1 x13=1 x14=1 x15=1 after N = 5 nodes (W = 504); MENTION,MAJ: N = 6. If b < N: the default (UNSAT, or FILL = violates [16] at b = N/2). | π_C ≈ Δ = acc(control) − acc(trap), estimated per model; power 0.9 to detect π_C ≥ 0.10 with 300 pairs; if Δ̂ ≈ 0 the set bounds π_C ≤ 0.07 (upper 95%) and the backtracking share of the remaining weight is read from BT-on-v traces weighted by R_m | control arm: x1=1 is kept; reference BTs on trap vars per variant: {'MENTION,TRUE': 0, 'MENTION,MAJ': 0, 'INDEX,TRUE': 0, 'INDEX,MAJ': 0, 'MOMS,TRUE': 0, 'MOMS,MAJ': 0} (all 0) |
| BEAM-w | w=1: SAT; w=2: SAT; w=4: SAT | BEAM-1/BEAM-2 predictions differ from DPLL-b on specific items (listed in its output); deferred-conflict cells were not produced by this generator | CASES carried in parallel; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: SAT; k=3,MENTION: UNSAT (default); k=3,INDEX: UNSAT (default) | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=15) = 0.85, P(success / k=75) = 1.00, P(success / k=375) = 1.00; modal failure at k=15: violates [40], LM0=True, Hamming to nearest solution = 2 | π_F from LM0 near-miss trap errors, whose share should grow with d (barrier height) | x1 changes by FLIP inside a full candidate, never by BT |
| MIN-CONFLICTS | P(success / k=15) = 0.33, P(success / k=75) = 0.75, P(success / k=375) = 0.67 | π_F from LM0 near-miss trap errors, whose share should grow with d (barrier height) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: SAT; MENTION,MAJ: SAT; MOMS,TRUE: SAT; MOMS,MAJ: SAT / CONT violates: MENTION,TRUE: []; MENTION,MAJ: []; MOMS,TRUE: []; MOMS,MAJ: [] | π_C ≈ Δ, with trap-arm errors dead-end-typed (x_v = 1); each dead-end trap error has LR ≈ 20 for C over DPLL-b | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=0 x8=1 x9=1 x10=1 x11=1 x12=1 x13=1 x14=1 x15=1 (violates []) | π_C ≈ Δ, with trap-arm errors dead-end-typed (x_v = 1); each dead-end trap error has LR ≈ 20 for C over DPLL-b | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=0 x8=0 x9=1 x10=1 x11=1 x12=1 x13=1 x14=1 x15=1 (violates [16]) | π_POLARITY bounded by control-arm successes (POLARITY fails the control arm by construction) | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.951 (eps=1e-4) or 0.604 (eps=1e-3), W = 504; otherwise a slip (one missed clause, or a spurious conflict) | π_NE contributes Δ ≤ 0.02 (tiny extra work): not separable from DPLL-b here (see E1–E3) | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0028 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), BEAM-2, WALK-k (k=75), C-UC/STOP, C-UC/CONT, C-GREEDY; pushes down BACKDOOR[k=2,OCC] (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.016)
- *near-miss (infeasible, LM0, V<=3)*: best fit MIN-CONFLICTS (k=75); pushes down EXACT (LR 0.05), DPLL-b (b >= N) (LR 0.05), BEAM-2 (LR 0.05), BACKDOOR[k=2,OCC] (LR 0.05), WALK-k (k=75) (LR 0.05), C-UC/STOP (LR 0.05), C-UC/CONT (LR 0.05), C-GREEDY (LR 0.05), POLARITY / ALWAYS-SAT (LR 0.05), B1 (UP-k, FLP-1) (LR 0.05), NOISY-EXACT (LR 0.143), RANDOM (LR 0.05)
- *infeasible (other)*: best fit POLARITY / ALWAYS-SAT; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=75) (LR 0.013), MIN-CONFLICTS (k=75) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.037)
- *UNSAT/UNKNOWN*: best fit BACKDOOR[k=2,OCC], B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), WALK-k (k=75) (LR 0.013), MIN-CONFLICTS (k=75) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=5, W=504; MENTION,MAJ: N=6, W=462; INDEX,TRUE: N=7, W=504; INDEX,MAJ: N=7, W=504; MOMS,TRUE: N=5, W=504; MOMS,MAJ: N=5, W=504. Every member's full output is in the JSONL `predictions` field.

### E4.3: d = 2, t = 2, trap arm

- **Question tested:** When the value every greedy rule picks first is a dead end revealed only after another decision, does the model backtrack?
- **Controlled:** the same variable names and clause order in both arms; the trap variable's polarity counts, occurrence and first mention; n, m, clause length 3; both arms SAT
- **Varied:** 2 literal signs per trap (clauses [4, 19, 27, 48]) swap which gadget is live; d = 2 (chain length); t = 2 (traps)
- **Ground truth:** `{"answer": "SAT", "n_solutions": 1280, "solutions": ["x1=0 x2=0 x3=1 x4=0 x5=1 x6=1 x7=0 x8=1 x9=1 x10=1 x11=0 x12=1 x13=0 x14=1 x15=1 x16=1 x17=0 x18=0 x19=1 x20=0 x21=1 x22=0", "x1=0 x2=0 x3=0 x4=0 x5=1 x6=1 x7=1 x8=0 x9=1 x10=0 x11=0 x12=1 x13=0 x14=1 x15=1 x16=0 x17=0 x18=0 x19=1 x20=0 x21=1 x22=0", "..."]}`

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x22. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x1 OR x5 OR x7)
C2: (x2 OR x19 OR x4)
C3: (NOT x4 OR NOT x5 OR NOT x17)
C4: (x21 OR NOT x14 OR x1)
C5: (x16 OR NOT x19 OR NOT x4)
C6: (NOT x4 OR x10 OR NOT x17)
C7: (x5 OR x16 OR NOT x20)
C8: (x15 OR x2 OR NOT x6)
C9: (x5 OR NOT x17 OR x11)
C10: (x5 OR NOT x17 OR NOT x7)
C11: (x16 OR NOT x4 OR NOT x7)
C12: (NOT x1 OR NOT x17 OR x5)
C13: (x16 OR NOT x4 OR NOT x12)
C14: (NOT x10 OR NOT x1 OR x8)
C15: (x16 OR NOT x5 OR NOT x17)
C16: (x2 OR x7 OR x16)
C17: (x22 OR x2 OR x6)
C18: (NOT x17 OR NOT x16 OR x19)
C19: (NOT x2 OR NOT x18 OR NOT x13)
C20: (x1 OR NOT x21 OR x14)
C21: (x7 OR x19 OR NOT x8)
C22: (x2 OR x12 OR NOT x19)
C23: (NOT x5 OR x14 OR x16)
C24: (NOT x1 OR x12 OR x9)
C25: (x21 OR NOT x11 OR x1)
C26: (x5 OR x2 OR NOT x9)
C27: (NOT x15 OR x2 OR x6)
C28: (NOT x16 OR NOT x5 OR x9)
C29: (x5 OR NOT x4 OR x22)
C30: (x5 OR x4 OR x16)
C31: (x2 OR x19 OR NOT x17)
C32: (x12 OR x9 OR x13)
C33: (x16 OR NOT x9 OR x5)
C34: (NOT x12 OR x5 OR x7)
C35: (NOT x19 OR x9 OR x1)
C36: (x9 OR NOT x3 OR NOT x19)
C37: (NOT x20 OR x18 OR NOT x2)
C38: (NOT x9 OR x12 OR x7)
C39: (x19 OR NOT x16 OR NOT x5)
C40: (x1 OR x9 OR NOT x7)
C41: (NOT x22 OR x6 OR x2)
C42: (NOT x19 OR x16 OR x7)
C43: (NOT x16 OR x12 OR NOT x5)
C44: (x1 OR x19 OR NOT x17)
C45: (NOT x16 OR NOT x4 OR x7)
C46: (NOT x4 OR x15 OR x17)
C47: (x16 OR NOT x6 OR x7)
C48: (NOT x8 OR NOT x3 OR NOT x1)
C49: (NOT x17 OR x7 OR NOT x2)
C50: (NOT x21 OR x16 OR x5)
C51: (NOT x18 OR NOT x2 OR x13)
C52: (NOT x12 OR NOT x4 OR x19)
C53: (x2 OR x19 OR x16)
C54: (x19 OR NOT x4 OR x1)
C55: (NOT x7 OR NOT x4 OR x19)
C56: (x1 OR x11 OR x21)
C57: (NOT x5 OR x1 OR x9)
C58: (x17 OR NOT x2 OR x16)
C59: (x4 OR NOT x17 OR x18)
C60: (NOT x1 OR x8 OR x10)
C61: (NOT x1 OR x3 OR NOT x8)
C62: (NOT x2 OR x18 OR x20)
C63: (x4 OR x19 OR NOT x7)
C64: (x9 OR x4 OR x5)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 1280 solutions | π_EXACT = the ceiling share in both arms | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=0 x2=0 x3=0 x4=0 x5=1 x6=1 x7=1 x8=0 x9=1 x10=1 x11=1 x12=1 x13=1 x14=1 x15=1 x16=1 x17=0 x18=1 x19=1 x20=0 x21=1 x22=1 after N = 12 nodes (W = 1344); MENTION,MAJ: N = 83. If b < N: the default (UNSAT, or FILL = violates [14] at b = N/2). | π_C ≈ Δ = acc(control) − acc(trap), estimated per model; power 0.9 to detect π_C ≥ 0.10 with 300 pairs; if Δ̂ ≈ 0 the set bounds π_C ≤ 0.07 (upper 95%) and the backtracking share of the remaining weight is read from BT-on-v traces weighted by R_m | trap arm: DEC x1=1, then a DEC on a core variable, CONF, BT, CONF, BT to x1=0 (reference BTs on trap vars per variant: {'MENTION,TRUE': 5, 'MENTION,MAJ': 5, 'INDEX,TRUE': 3, 'INDEX,MAJ': 3, 'MOMS,TRUE': 2, 'MOMS,MAJ': 2}); control arm: no BT on the trap variable |
| BEAM-w | w=1: SAT; w=2: SAT; w=4: SAT | BEAM-1/BEAM-2 predictions differ from DPLL-b on specific items (listed in its output); deferred-conflict cells were not produced by this generator | CASES carried in parallel; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: SAT; k=3,OCC: SAT; k=3,MENTION: UNSAT (default); k=3,INDEX: SAT | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=22) = 0.72, P(success / k=110) = 1.00, P(success / k=550) = 1.00; modal failure at k=22: violates [24, 28, 37, 39, 43, 45, 60], LM0=False, Hamming to nearest solution = 8 | π_F from LM0 near-miss trap errors, whose share should grow with d (barrier height) | x1 changes by FLIP inside a full candidate, never by BT |
| MIN-CONFLICTS | P(success / k=22) = 0.11, P(success / k=110) = 0.31, P(success / k=550) = 0.51 | π_F from LM0 near-miss trap errors, whose share should grow with d (barrier height) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C61); MENTION,MAJ: UNSAT (dead end at C61); MOMS,TRUE: UNSAT (dead end at C51); MOMS,MAJ: UNSAT (dead end at C51) / CONT violates: MENTION,TRUE: [51, 61]; MENTION,MAJ: [51, 61]; MOMS,TRUE: [51, 61]; MOMS,MAJ: [51, 61] | π_C ≈ Δ, with trap-arm errors dead-end-typed (x_v = 1); each dead-end trap error has LR ≈ 20 for C over DPLL-b | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=1 x3=1 x4=0 x5=1 x6=1 x7=1 x8=0 x9=1 x10=1 x11=1 x12=1 x13=1 x14=1 x15=1 x16=0 x17=0 x18=0 x19=1 x20=1 x21=1 x22=1 (violates [14, 37, 58]) | π_C ≈ Δ, with trap-arm errors dead-end-typed (x_v = 1); each dead-end trap error has LR ≈ 20 for C over DPLL-b | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=0 x4=0 x5=1 x6=1 x7=1 x8=0 x9=1 x10=1 x11=1 x12=1 x13=1 x14=1 x15=1 x16=1 x17=0 x18=1 x19=1 x20=0 x21=1 x22=1 (violates [14, 19]) | π_POLARITY bounded by control-arm successes (POLARITY fails the control arm by construction) | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.874 (eps=1e-4) or 0.261 (eps=1e-3), W = 1344; otherwise a slip (one missed clause, or a spurious conflict) | π_NE contributes Δ ≤ 0.02 (tiny extra work): not separable from DPLL-b here (see E1–E3) | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0003 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), BEAM-2, WALK-k (k=110); pushes down BACKDOOR[k=2,OCC] (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *near-miss (infeasible, LM0, V<=3)*: best fit MIN-CONFLICTS (k=110); pushes down EXACT (LR 0.019), DPLL-b (b >= N) (LR 0.019), BEAM-2 (LR 0.019), BACKDOOR[k=2,OCC] (LR 0.019), WALK-k (k=110) (LR 0.019), C-UC/STOP (LR 0.019), C-UC/CONT (LR 0.019), C-GREEDY (LR 0.019), POLARITY / ALWAYS-SAT (LR 0.019), B1 (UP-k, FLP-1) (LR 0.019), NOISY-EXACT (LR 0.108), RANDOM (LR 0.019)
- *infeasible (other)*: best fit C-UC/CONT, C-GREEDY, POLARITY / ALWAYS-SAT; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=110) (LR 0.013), MIN-CONFLICTS (k=110) (LR 0.013), C-UC/STOP (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.075)
- *UNSAT/UNKNOWN*: best fit BACKDOOR[k=2,OCC], C-UC/STOP, B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), WALK-k (k=110) (LR 0.013), MIN-CONFLICTS (k=110) (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=81, W=14208; MENTION,MAJ: N=83, W=14144; INDEX,TRUE: N=139, W=25280; INDEX,MAJ: N=143, W=25280; MOMS,TRUE: N=12, W=1600; MOMS,MAJ: N=12, W=1344. Every member's full output is in the JSONL `predictions` field.

### E4.4: d = 2, t = 2, control arm

- **Question tested:** When the value every greedy rule picks first is a dead end revealed only after another decision, does the model backtrack?
- **Controlled:** the same variable names and clause order in both arms; the trap variable's polarity counts, occurrence and first mention; n, m, clause length 3; both arms SAT
- **Varied:** 2 literal signs per trap (clauses [4, 19, 27, 48]) swap which gadget is live; d = 2 (chain length); t = 2 (traps)
- **Ground truth:** `{"answer": "SAT", "n_solutions": 1536, "solutions": ["x1=1 x2=1 x3=1 x4=0 x5=1 x6=0 x7=0 x8=1 x9=1 x10=0 x11=0 x12=1 x13=1 x14=0 x15=0 x16=1 x17=0 x18=1 x19=1 x20=0 x21=0 x22=0", "x1=1 x2=1 x3=1 x4=0 x5=0 x6=0 x7=1 x8=1 x9=1 x10=0 x11=0 x12=1 x13=1 x14=0 x15=0 x16=1 x17=0 x18=1 x19=1 x20=0 x21=0 x22=0", "..."]}`
- **Differs from E4.3 only in:** C4: (x21 OR NOT x14 OR x1) → (NOT x21 OR NOT x14 OR x1); C19: (NOT x2 OR NOT x18 OR NOT x13) → (NOT x2 OR x18 OR NOT x13); C27: (NOT x15 OR x2 OR x6) → (NOT x15 OR x2 OR NOT x6); C48: (NOT x8 OR NOT x3 OR NOT x1) → (x8 OR NOT x3 OR NOT x1)

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x22. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x1 OR x5 OR x7)
C2: (x2 OR x19 OR x4)
C3: (NOT x4 OR NOT x5 OR NOT x17)
C4: (NOT x21 OR NOT x14 OR x1)
C5: (x16 OR NOT x19 OR NOT x4)
C6: (NOT x4 OR x10 OR NOT x17)
C7: (x5 OR x16 OR NOT x20)
C8: (x15 OR x2 OR NOT x6)
C9: (x5 OR NOT x17 OR x11)
C10: (x5 OR NOT x17 OR NOT x7)
C11: (x16 OR NOT x4 OR NOT x7)
C12: (NOT x1 OR NOT x17 OR x5)
C13: (x16 OR NOT x4 OR NOT x12)
C14: (NOT x10 OR NOT x1 OR x8)
C15: (x16 OR NOT x5 OR NOT x17)
C16: (x2 OR x7 OR x16)
C17: (x22 OR x2 OR x6)
C18: (NOT x17 OR NOT x16 OR x19)
C19: (NOT x2 OR x18 OR NOT x13)
C20: (x1 OR NOT x21 OR x14)
C21: (x7 OR x19 OR NOT x8)
C22: (x2 OR x12 OR NOT x19)
C23: (NOT x5 OR x14 OR x16)
C24: (NOT x1 OR x12 OR x9)
C25: (x21 OR NOT x11 OR x1)
C26: (x5 OR x2 OR NOT x9)
C27: (NOT x15 OR x2 OR NOT x6)
C28: (NOT x16 OR NOT x5 OR x9)
C29: (x5 OR NOT x4 OR x22)
C30: (x5 OR x4 OR x16)
C31: (x2 OR x19 OR NOT x17)
C32: (x12 OR x9 OR x13)
C33: (x16 OR NOT x9 OR x5)
C34: (NOT x12 OR x5 OR x7)
C35: (NOT x19 OR x9 OR x1)
C36: (x9 OR NOT x3 OR NOT x19)
C37: (NOT x20 OR x18 OR NOT x2)
C38: (NOT x9 OR x12 OR x7)
C39: (x19 OR NOT x16 OR NOT x5)
C40: (x1 OR x9 OR NOT x7)
C41: (NOT x22 OR x6 OR x2)
C42: (NOT x19 OR x16 OR x7)
C43: (NOT x16 OR x12 OR NOT x5)
C44: (x1 OR x19 OR NOT x17)
C45: (NOT x16 OR NOT x4 OR x7)
C46: (NOT x4 OR x15 OR x17)
C47: (x16 OR NOT x6 OR x7)
C48: (x8 OR NOT x3 OR NOT x1)
C49: (NOT x17 OR x7 OR NOT x2)
C50: (NOT x21 OR x16 OR x5)
C51: (NOT x18 OR NOT x2 OR x13)
C52: (NOT x12 OR NOT x4 OR x19)
C53: (x2 OR x19 OR x16)
C54: (x19 OR NOT x4 OR x1)
C55: (NOT x7 OR NOT x4 OR x19)
C56: (x1 OR x11 OR x21)
C57: (NOT x5 OR x1 OR x9)
C58: (x17 OR NOT x2 OR x16)
C59: (x4 OR NOT x17 OR x18)
C60: (NOT x1 OR x8 OR x10)
C61: (NOT x1 OR x3 OR NOT x8)
C62: (NOT x2 OR x18 OR x20)
C63: (x4 OR x19 OR NOT x7)
C64: (x9 OR x4 OR x5)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 1536 solutions | π_EXACT = the ceiling share in both arms | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=1 x2=1 x3=1 x4=0 x5=1 x6=0 x7=1 x8=1 x9=1 x10=1 x11=1 x12=1 x13=1 x14=1 x15=1 x16=1 x17=0 x18=1 x19=1 x20=0 x21=0 x22=1 after N = 8 nodes (W = 896); MENTION,MAJ: N = 9. If b < N: the default (UNSAT, or FILL = violates [61] at b = N/2). | π_C ≈ Δ = acc(control) − acc(trap), estimated per model; power 0.9 to detect π_C ≥ 0.10 with 300 pairs; if Δ̂ ≈ 0 the set bounds π_C ≤ 0.07 (upper 95%) and the backtracking share of the remaining weight is read from BT-on-v traces weighted by R_m | control arm: x1=1 is kept; reference BTs on trap vars per variant: {'MENTION,TRUE': 0, 'MENTION,MAJ': 0, 'INDEX,TRUE': 0, 'INDEX,MAJ': 0, 'MOMS,TRUE': 0, 'MOMS,MAJ': 0} (all 0) |
| BEAM-w | w=1: UNSAT; w=2: SAT; w=4: SAT | BEAM-1/BEAM-2 predictions differ from DPLL-b on specific items (listed in its output); deferred-conflict cells were not produced by this generator | CASES carried in parallel; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: SAT | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=22) = 0.73, P(success / k=110) = 1.00, P(success / k=550) = 1.00; modal failure at k=22: violates [17], LM0=True, Hamming to nearest solution = 3 | π_F from LM0 near-miss trap errors, whose share should grow with d (barrier height) | x1 changes by FLIP inside a full candidate, never by BT |
| MIN-CONFLICTS | P(success / k=22) = 0.34, P(success / k=110) = 0.68, P(success / k=550) = 0.68 | π_F from LM0 near-miss trap errors, whose share should grow with d (barrier height) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: SAT; MENTION,MAJ: SAT; MOMS,TRUE: SAT; MOMS,MAJ: SAT / CONT violates: MENTION,TRUE: []; MENTION,MAJ: []; MOMS,TRUE: []; MOMS,MAJ: [] | π_C ≈ Δ, with trap-arm errors dead-end-typed (x_v = 1); each dead-end trap error has LR ≈ 20 for C over DPLL-b | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=1 x3=1 x4=0 x5=1 x6=1 x7=1 x8=1 x9=1 x10=1 x11=1 x12=1 x13=1 x14=1 x15=1 x16=0 x17=0 x18=1 x19=1 x20=1 x21=1 x22=1 (violates [58]) | π_C ≈ Δ, with trap-arm errors dead-end-typed (x_v = 1); each dead-end trap error has LR ≈ 20 for C over DPLL-b | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=0 x4=0 x5=1 x6=0 x7=1 x8=1 x9=1 x10=1 x11=1 x12=1 x13=1 x14=1 x15=1 x16=1 x17=0 x18=1 x19=1 x20=0 x21=0 x22=1 (violates [61]) | π_POLARITY bounded by control-arm successes (POLARITY fails the control arm by construction) | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.914 (eps=1e-4) or 0.408 (eps=1e-3), W = 896; otherwise a slip (one missed clause, or a spurious conflict) | π_NE contributes Δ ≤ 0.02 (tiny extra work): not separable from DPLL-b here (see E1–E3) | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0004 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), BEAM-2, WALK-k (k=110), C-UC/STOP, C-UC/CONT; pushes down BACKDOOR[k=2,OCC] (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *near-miss (infeasible, LM0, V<=3)*: best fit MIN-CONFLICTS (k=110); pushes down EXACT (LR 0.039), DPLL-b (b >= N) (LR 0.039), BEAM-2 (LR 0.039), BACKDOOR[k=2,OCC] (LR 0.039), WALK-k (k=110) (LR 0.039), C-UC/STOP (LR 0.039), C-UC/CONT (LR 0.039), C-GREEDY (LR 0.039), POLARITY / ALWAYS-SAT (LR 0.039), B1 (UP-k, FLP-1) (LR 0.039), NOISY-EXACT (LR 0.168), RANDOM (LR 0.039)
- *infeasible (other)*: best fit C-GREEDY, POLARITY / ALWAYS-SAT; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=110) (LR 0.013), MIN-CONFLICTS (k=110) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.055)
- *UNSAT/UNKNOWN*: best fit BACKDOOR[k=2,OCC], B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), WALK-k (k=110) (LR 0.013), MIN-CONFLICTS (k=110) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=8, W=1152; MENTION,MAJ: N=9, W=1088; INDEX,TRUE: N=6, W=1024; INDEX,MAJ: N=12, W=1216; MOMS,TRUE: N=7, W=1024; MOMS,MAJ: N=8, W=896. Every member's full output is in the JSONL `predictions` field.

### E4.5: d = 4, t = 1, trap arm

- **Question tested:** When the value every greedy rule picks first is a dead end revealed only after another decision, does the model backtrack?
- **Controlled:** the same variable names and clause order in both arms; the trap variable's polarity counts, occurrence and first mention; n, m, clause length 3; both arms SAT
- **Varied:** 2 literal signs per trap (clauses [21, 47]) swap which gadget is live; d = 4 (chain length); t = 1 (traps)
- **Ground truth:** `{"answer": "SAT", "n_solutions": 1088, "solutions": ["x1=0 x2=1 x3=0 x4=0 x5=0 x6=0 x7=0 x8=0 x9=0 x10=1 x11=0 x12=0 x13=1 x14=1 x15=1 x16=0 x17=1 x18=0 x19=0 x20=1 x21=0 x22=1 x23=0", "x1=0 x2=1 x3=0 x4=0 x5=0 x6=0 x7=0 x8=0 x9=1 x10=1 x11=0 x12=0 x13=1 x14=1 x15=1 x16=0 x17=1 x18=0 x19=0 x20=1 x21=0 x22=1 x23=0", "..."]}`

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x23. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x1 OR x10 OR x4)
C2: (NOT x23 OR NOT x7 OR NOT x22)
C3: (x17 OR NOT x12 OR x1)
C4: (x22 OR x15 OR NOT x4)
C5: (x22 OR NOT x8 OR NOT x23)
C6: (x8 OR NOT x21 OR NOT x15)
C7: (x2 OR NOT x21 OR x16)
C8: (NOT x4 OR x2 OR x15)
C9: (x1 OR NOT x4 OR x22)
C10: (NOT x19 OR x9 OR NOT x1)
C11: (x4 OR x22 OR NOT x15)
C12: (NOT x21 OR x8 OR NOT x12)
C13: (x23 OR NOT x21 OR x1)
C14: (NOT x1 OR NOT x9 OR x16)
C15: (x15 OR x8 OR x21)
C16: (NOT x23 OR NOT x10 OR NOT x1)
C17: (x21 OR NOT x4 OR x10)
C18: (x21 OR NOT x5 OR x10)
C19: (NOT x6 OR x4 OR NOT x22)
C20: (x15 OR x22 OR x1)
C21: (NOT x20 OR x17 OR x1)
C22: (NOT x21 OR NOT x4 OR x1)
C23: (x2 OR NOT x4 OR NOT x21)
C24: (x14 OR x1 OR NOT x13)
C25: (x15 OR NOT x2 OR x23)
C26: (x1 OR x18 OR x17)
C27: (NOT x23 OR x8 OR NOT x10)
C28: (x10 OR x22 OR NOT x1)
C29: (x22 OR x2 OR NOT x9)
C30: (x4 OR x1 OR NOT x21)
C31: (x11 OR x1 OR NOT x18)
C32: (NOT x4 OR NOT x15 OR x2)
C33: (x18 OR x15 OR x2)
C34: (NOT x17 OR x13 OR x1)
C35: (x1 OR x12 OR NOT x11)
C36: (NOT x4 OR x10 OR NOT x15)
C37: (NOT x15 OR x2 OR NOT x4)
C38: (x2 OR x4 OR NOT x10)
C39: (NOT x21 OR NOT x8 OR NOT x11)
C40: (NOT x10 OR x17 OR x8)
C41: (x4 OR NOT x3 OR x21)
C42: (x22 OR x10 OR x14)
C43: (NOT x14 OR x1 OR x20)
C44: (NOT x1 OR x7 OR NOT x16)
C45: (NOT x23 OR NOT x13 OR x4)
C46: (x23 OR x4 OR NOT x8)
C47: (NOT x1 OR NOT x7 OR NOT x5)
C48: (NOT x3 OR NOT x1 OR x5)
C49: (NOT x4 OR x10 OR x22)
C50: (x2 OR x23 OR x4)
C51: (x21 OR NOT x8 OR x15)
C52: (x10 OR NOT x23 OR NOT x20)
C53: (x15 OR x23 OR NOT x2)
C54: (NOT x1 OR x7 OR x19)
C55: (NOT x6 OR NOT x1 OR x3)
C56: (NOT x22 OR x21 OR x2)
C57: (NOT x7 OR x6 OR NOT x1)
C58: (x21 OR x8 OR NOT x19)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 1088 solutions | π_EXACT = the ceiling share in both arms | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=0 x2=1 x3=0 x4=0 x5=0 x6=0 x7=0 x8=0 x9=0 x10=1 x11=1 x12=1 x13=1 x14=1 x15=1 x16=1 x17=1 x18=1 x19=0 x20=1 x21=0 x22=1 x23=0 after N = 8 nodes (W = 2262); MENTION,MAJ: N = 16. If b < N: the default (UNSAT, or FILL = violates [31, 34, 43, 46] at b = N/2). | π_C ≈ Δ = acc(control) − acc(trap), estimated per model; power 0.9 to detect π_C ≥ 0.10 with 300 pairs; if Δ̂ ≈ 0 the set bounds π_C ≤ 0.07 (upper 95%) and the backtracking share of the remaining weight is read from BT-on-v traces weighted by R_m | trap arm: DEC x1=1, then a DEC on a core variable, CONF, BT, CONF, BT to x1=0 (reference BTs on trap vars per variant: {'MENTION,TRUE': 1, 'MENTION,MAJ': 1, 'INDEX,TRUE': 1, 'INDEX,MAJ': 1, 'MOMS,TRUE': 1, 'MOMS,MAJ': 1}); control arm: no BT on the trap variable |
| BEAM-w | w=1: UNSAT; w=2: SAT; w=4: SAT | BEAM-1/BEAM-2 predictions differ from DPLL-b on specific items (listed in its output); deferred-conflict cells were not produced by this generator | CASES carried in parallel; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: UNSAT (default) | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=23) = 0.58, P(success / k=115) = 0.84, P(success / k=575) = 1.00; modal failure at k=23: violates [35], LM0=True, Hamming to nearest solution = 5 | π_F from LM0 near-miss trap errors, whose share should grow with d (barrier height) | x1 changes by FLIP inside a full candidate, never by BT |
| MIN-CONFLICTS | P(success / k=23) = 0.15, P(success / k=115) = 0.31, P(success / k=575) = 0.38 | π_F from LM0 near-miss trap errors, whose share should grow with d (barrier height) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C57); MENTION,MAJ: UNSAT (dead end at C57); MOMS,TRUE: UNSAT (dead end at C57); MOMS,MAJ: UNSAT (dead end at C54) / CONT violates: MENTION,TRUE: [57]; MENTION,MAJ: [57]; MOMS,TRUE: [57]; MOMS,MAJ: [54] | π_C ≈ Δ, with trap-arm errors dead-end-typed (x_v = 1); each dead-end trap error has LR ≈ 20 for C over DPLL-b | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=1 x8=1 x9=1 x10=1 x11=1 x12=0 x13=1 x14=1 x15=1 x16=1 x17=1 x18=1 x19=0 x20=1 x21=0 x22=1 x23=0 (violates [47]) | π_C ≈ Δ, with trap-arm errors dead-end-typed (x_v = 1); each dead-end trap error has LR ≈ 20 for C over DPLL-b | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=0 x4=0 x5=0 x6=0 x7=0 x8=1 x9=0 x10=1 x11=0 x12=0 x13=0 x14=1 x15=1 x16=1 x17=1 x18=1 x19=0 x20=0 x21=0 x22=1 x23=0 (violates [44, 46, 54]) | π_POLARITY bounded by control-arm successes (POLARITY fails the control arm by construction) | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.798 (eps=1e-4) or 0.104 (eps=1e-3), W = 2262; otherwise a slip (one missed clause, or a spurious conflict) | π_NE contributes Δ ≤ 0.02 (tiny extra work): not separable from DPLL-b here (see E1–E3) | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0001 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), BEAM-2; pushes down BACKDOOR[k=2,OCC] (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *near-miss (infeasible, LM0, V<=3)*: best fit C-UC/CONT, C-GREEDY; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=115) (LR 0.171), C-UC/STOP (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.113), RANDOM (LR 0.013)
- *infeasible (other)*: best fit POLARITY / ALWAYS-SAT; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=115) (LR 0.013), MIN-CONFLICTS (k=115) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.113)
- *UNSAT/UNKNOWN*: best fit BACKDOOR[k=2,OCC], C-UC/STOP, B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), WALK-k (k=115) (LR 0.013), MIN-CONFLICTS (k=115) (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=16, W=3480; MENTION,MAJ: N=16, W=3422; INDEX,TRUE: N=14, W=2726; INDEX,MAJ: N=14, W=2668; MOMS,TRUE: N=8, W=1508; MOMS,MAJ: N=8, W=2262. Every member's full output is in the JSONL `predictions` field.

### E4.6: d = 4, t = 1, control arm

- **Question tested:** When the value every greedy rule picks first is a dead end revealed only after another decision, does the model backtrack?
- **Controlled:** the same variable names and clause order in both arms; the trap variable's polarity counts, occurrence and first mention; n, m, clause length 3; both arms SAT
- **Varied:** 2 literal signs per trap (clauses [21, 47]) swap which gadget is live; d = 4 (chain length); t = 1 (traps)
- **Ground truth:** `{"answer": "SAT", "n_solutions": 1920, "solutions": ["x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=1 x8=1 x9=0 x10=1 x11=0 x12=1 x13=1 x14=0 x15=1 x16=0 x17=0 x18=0 x19=0 x20=1 x21=1 x22=1 x23=0", "x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=1 x8=1 x9=0 x10=1 x11=0 x12=0 x13=0 x14=0 x15=1 x16=0 x17=0 x18=0 x19=0 x20=0 x21=0 x22=0 x23=0", "..."]}`
- **Differs from E4.5 only in:** C21: (NOT x20 OR x17 OR x1) → (NOT x20 OR NOT x17 OR x1); C47: (NOT x1 OR NOT x7 OR NOT x5) → (NOT x1 OR x7 OR NOT x5)

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x23. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x1 OR x10 OR x4)
C2: (NOT x23 OR NOT x7 OR NOT x22)
C3: (x17 OR NOT x12 OR x1)
C4: (x22 OR x15 OR NOT x4)
C5: (x22 OR NOT x8 OR NOT x23)
C6: (x8 OR NOT x21 OR NOT x15)
C7: (x2 OR NOT x21 OR x16)
C8: (NOT x4 OR x2 OR x15)
C9: (x1 OR NOT x4 OR x22)
C10: (NOT x19 OR x9 OR NOT x1)
C11: (x4 OR x22 OR NOT x15)
C12: (NOT x21 OR x8 OR NOT x12)
C13: (x23 OR NOT x21 OR x1)
C14: (NOT x1 OR NOT x9 OR x16)
C15: (x15 OR x8 OR x21)
C16: (NOT x23 OR NOT x10 OR NOT x1)
C17: (x21 OR NOT x4 OR x10)
C18: (x21 OR NOT x5 OR x10)
C19: (NOT x6 OR x4 OR NOT x22)
C20: (x15 OR x22 OR x1)
C21: (NOT x20 OR NOT x17 OR x1)
C22: (NOT x21 OR NOT x4 OR x1)
C23: (x2 OR NOT x4 OR NOT x21)
C24: (x14 OR x1 OR NOT x13)
C25: (x15 OR NOT x2 OR x23)
C26: (x1 OR x18 OR x17)
C27: (NOT x23 OR x8 OR NOT x10)
C28: (x10 OR x22 OR NOT x1)
C29: (x22 OR x2 OR NOT x9)
C30: (x4 OR x1 OR NOT x21)
C31: (x11 OR x1 OR NOT x18)
C32: (NOT x4 OR NOT x15 OR x2)
C33: (x18 OR x15 OR x2)
C34: (NOT x17 OR x13 OR x1)
C35: (x1 OR x12 OR NOT x11)
C36: (NOT x4 OR x10 OR NOT x15)
C37: (NOT x15 OR x2 OR NOT x4)
C38: (x2 OR x4 OR NOT x10)
C39: (NOT x21 OR NOT x8 OR NOT x11)
C40: (NOT x10 OR x17 OR x8)
C41: (x4 OR NOT x3 OR x21)
C42: (x22 OR x10 OR x14)
C43: (NOT x14 OR x1 OR x20)
C44: (NOT x1 OR x7 OR NOT x16)
C45: (NOT x23 OR NOT x13 OR x4)
C46: (x23 OR x4 OR NOT x8)
C47: (NOT x1 OR x7 OR NOT x5)
C48: (NOT x3 OR NOT x1 OR x5)
C49: (NOT x4 OR x10 OR x22)
C50: (x2 OR x23 OR x4)
C51: (x21 OR NOT x8 OR x15)
C52: (x10 OR NOT x23 OR NOT x20)
C53: (x15 OR x23 OR NOT x2)
C54: (NOT x1 OR x7 OR x19)
C55: (NOT x6 OR NOT x1 OR x3)
C56: (NOT x22 OR x21 OR x2)
C57: (NOT x7 OR x6 OR NOT x1)
C58: (x21 OR x8 OR NOT x19)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 1920 solutions | π_EXACT = the ceiling share in both arms | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=1 x8=1 x9=1 x10=1 x11=0 x12=0 x13=0 x14=1 x15=1 x16=1 x17=1 x18=1 x19=0 x20=0 x21=0 x22=1 x23=0 after N = 8 nodes (W = 870); MENTION,MAJ: N = 12. If b < N: the default (UNSAT, or FILL = violates [] at b = N/2). | π_C ≈ Δ = acc(control) − acc(trap), estimated per model; power 0.9 to detect π_C ≥ 0.10 with 300 pairs; if Δ̂ ≈ 0 the set bounds π_C ≤ 0.07 (upper 95%) and the backtracking share of the remaining weight is read from BT-on-v traces weighted by R_m | control arm: x1=1 is kept; reference BTs on trap vars per variant: {'MENTION,TRUE': 0, 'MENTION,MAJ': 0, 'INDEX,TRUE': 0, 'INDEX,MAJ': 0, 'MOMS,TRUE': 0, 'MOMS,MAJ': 0} (all 0) |
| BEAM-w | w=1: SAT; w=2: UNSAT; w=4: SAT | BEAM-1/BEAM-2 predictions differ from DPLL-b on specific items (listed in its output); deferred-conflict cells were not produced by this generator | CASES carried in parallel; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: UNSAT (default) | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=23) = 0.33, P(success / k=115) = 0.50, P(success / k=575) = 0.79; modal failure at k=23: violates [24], LM0=True, Hamming to nearest solution = 5 | π_F from LM0 near-miss trap errors, whose share should grow with d (barrier height) | x1 changes by FLIP inside a full candidate, never by BT |
| MIN-CONFLICTS | P(success / k=23) = 0.16, P(success / k=115) = 0.35, P(success / k=575) = 0.37 | π_F from LM0 near-miss trap errors, whose share should grow with d (barrier height) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: SAT; MENTION,MAJ: SAT; MOMS,TRUE: SAT; MOMS,MAJ: SAT / CONT violates: MENTION,TRUE: []; MENTION,MAJ: []; MOMS,TRUE: []; MOMS,MAJ: [] | π_C ≈ Δ, with trap-arm errors dead-end-typed (x_v = 1); each dead-end trap error has LR ≈ 20 for C over DPLL-b | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=1 x3=1 x4=1 x5=1 x6=1 x7=1 x8=1 x9=1 x10=1 x11=1 x12=0 x13=1 x14=1 x15=1 x16=1 x17=1 x18=1 x19=0 x20=1 x21=0 x22=1 x23=0 (violates []) | π_C ≈ Δ, with trap-arm errors dead-end-typed (x_v = 1); each dead-end trap error has LR ≈ 20 for C over DPLL-b | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=0 x4=0 x5=0 x6=0 x7=1 x8=1 x9=0 x10=1 x11=0 x12=0 x13=0 x14=1 x15=1 x16=1 x17=1 x18=1 x19=0 x20=0 x21=0 x22=1 x23=0 (violates [46, 57]) | π_POLARITY bounded by control-arm successes (POLARITY fails the control arm by construction) | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.917 (eps=1e-4) or 0.419 (eps=1e-3), W = 870; otherwise a slip (one missed clause, or a spurious conflict) | π_NE contributes Δ ≤ 0.02 (tiny extra work): not separable from DPLL-b here (see E1–E3) | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0002 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), C-UC/STOP, C-UC/CONT, C-GREEDY; pushes down BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *near-miss (infeasible, LM0, V<=3)*: best fit MIN-CONFLICTS (k=115); pushes down EXACT (LR 0.02), DPLL-b (b >= N) (LR 0.02), BEAM-2 (LR 0.02), BACKDOOR[k=2,OCC] (LR 0.02), C-UC/STOP (LR 0.02), C-UC/CONT (LR 0.02), C-GREEDY (LR 0.02), POLARITY / ALWAYS-SAT (LR 0.02), B1 (UP-k, FLP-1) (LR 0.02), NOISY-EXACT (LR 0.083), RANDOM (LR 0.02)
- *infeasible (other)*: best fit POLARITY / ALWAYS-SAT; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=115) (LR 0.013), MIN-CONFLICTS (k=115) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.054)
- *UNSAT/UNKNOWN*: best fit BEAM-2, BACKDOOR[k=2,OCC], B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), WALK-k (k=115) (LR 0.013), MIN-CONFLICTS (k=115) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=12, W=1160; MENTION,MAJ: N=12, W=1044; INDEX,TRUE: N=8, W=928; INDEX,MAJ: N=9, W=1218; MOMS,TRUE: N=8, W=928; MOMS,MAJ: N=8, W=870. Every member's full output is in the JSONL `predictions` field.

### E4.7: d = 4, t = 2, trap arm

- **Question tested:** When the value every greedy rule picks first is a dead end revealed only after another decision, does the model backtrack?
- **Controlled:** the same variable names and clause order in both arms; the trap variable's polarity counts, occurrence and first mention; n, m, clause length 3; both arms SAT
- **Varied:** 2 literal signs per trap (clauses [12, 30, 73, 84]) swap which gadget is live; d = 4 (chain length); t = 2 (traps)
- **Ground truth:** `{"answer": "SAT", "n_solutions": 2000, "solutions": ["x1=0 x2=0 x3=0 x4=1 x5=1 x6=0 x7=0 x8=1 x9=1 x10=0 x11=0 x12=0 x13=0 x14=0 x15=1 x16=1 x17=0 x18=1 x19=0 x20=0 x21=0 x22=1 x23=0 x24=1 x25=1 x26=1 x27=1 x28=1 x29=0 x30=0 x31=1 x32=0 x33=1 x34=1 x35=1 x36=0 x37=1 x38=0", "x1=0 x2=0 x3=0 x4=0 x5=1 x6=0 x7=0 x8=0 x9=1 x10=0 x11=0 x12=0 x13=0 x14=0 x15=0 x16=1 x17=0 x18=1 x19=0 x20=0 x21=0 x22=1 x23=0 x24=0 x25=1 x26=1 x27=1 x28=0 x29=0 x30=0 x31=1 x32=0 x33=1 x34=0 x35=1 x36=0 x37=1 x38=0", "..."]}`

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x38. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x1 OR x37 OR x27)
C2: (x2 OR x16 OR NOT x27)
C3: (NOT x36 OR x3 OR x1)
C4: (NOT x16 OR x14 OR x25)
C5: (x1 OR x36 OR x5)
C6: (NOT x6 OR NOT x27 OR x14)
C7: (NOT x25 OR x16 OR NOT x33)
C8: (x25 OR NOT x3 OR x16)
C9: (NOT x1 OR x34 OR NOT x29)
C10: (x8 OR NOT x1 OR NOT x34)
C11: (NOT x14 OR x26 OR x27)
C12: (NOT x1 OR NOT x34 OR NOT x20)
C13: (x33 OR NOT x15 OR x2)
C14: (NOT x1 OR NOT x6 OR x14)
C15: (x17 OR NOT x21 OR NOT x2)
C16: (NOT x14 OR x25 OR NOT x24)
C17: (NOT x17 OR NOT x2 OR x10)
C18: (x1 OR x30 OR NOT x3)
C19: (x27 OR x37 OR x35)
C20: (x16 OR x19 OR x25)
C21: (NOT x33 OR x2 OR x31)
C22: (NOT x1 OR x11 OR x34)
C23: (NOT x10 OR x14 OR NOT x19)
C24: (NOT x38 OR x19 OR x25)
C25: (NOT x32 OR x25 OR x37)
C26: (x37 OR NOT x16 OR x25)
C27: (x12 OR NOT x16 OR x27)
C28: (x25 OR NOT x27 OR NOT x37)
C29: (x1 OR NOT x19 OR x6)
C30: (x1 OR NOT x35 OR x5)
C31: (NOT x37 OR x6 OR x27)
C32: (NOT x2 OR x37 OR x16)
C33: (x2 OR NOT x13 OR x16)
C34: (x1 OR NOT x18 OR x35)
C35: (x37 OR x2 OR x25)
C36: (x27 OR NOT x28 OR x16)
C37: (NOT x2 OR x12 OR NOT x10)
C38: (x18 OR x6 OR NOT x14)
C39: (NOT x13 OR NOT x19 OR x2)
C40: (x2 OR NOT x28 OR x4)
C41: (NOT x25 OR NOT x6 OR x13)
C42: (NOT x1 OR NOT x11 OR x7)
C43: (x1 OR x5 OR NOT x30)
C44: (x17 OR NOT x13 OR x25)
C45: (x10 OR x32 OR NOT x2)
C46: (NOT x13 OR x34 OR x27)
C47: (x2 OR x27 OR NOT x16)
C48: (x19 OR NOT x13 OR NOT x6)
C49: (NOT x7 OR x29 OR NOT x1)
C50: (x6 OR NOT x13 OR x14)
C51: (NOT x25 OR x20 OR x16)
C52: (NOT x19 OR NOT x37 OR x25)
C53: (x16 OR NOT x14 OR x2)
C54: (NOT x2 OR NOT x24 OR x23)
C55: (x16 OR NOT x1 OR NOT x27)
C56: (x16 OR NOT x19 OR NOT x11)
C57: (NOT x8 OR x38 OR NOT x1)
C58: (NOT x5 OR NOT x13 OR NOT x6)
C59: (x4 OR NOT x6 OR NOT x13)
C60: (NOT x13 OR NOT x31 OR NOT x16)
C61: (NOT x6 OR x1 OR x25)
C62: (x2 OR NOT x31 OR x22)
C63: (NOT x37 OR x19 OR NOT x13)
C64: (x29 OR x37 OR x16)
C65: (NOT x37 OR NOT x6 OR x19)
C66: (NOT x25 OR x19 OR x16)
C67: (NOT x14 OR x13 OR x1)
C68: (NOT x23 OR x27 OR NOT x6)
C69: (NOT x25 OR NOT x2 OR x16)
C70: (x22 OR x13 OR NOT x6)
C71: (x16 OR x13 OR x1)
C72: (NOT x7 OR NOT x6 OR NOT x13)
C73: (NOT x10 OR NOT x2 OR NOT x23)
C74: (x2 OR x28 OR x33)
C75: (x14 OR x25 OR x1)
C76: (x16 OR NOT x27 OR x9)
C77: (NOT x14 OR x6 OR x27)
C78: (NOT x21 OR NOT x14 OR x13)
C79: (x9 OR NOT x22 OR x2)
C80: (NOT x26 OR x18 OR x1)
C81: (x15 OR x27 OR x14)
C82: (NOT x37 OR x16 OR x6)
C83: (NOT x37 OR NOT x27 OR NOT x14)
C84: (NOT x9 OR x33 OR x2)
C85: (NOT x36 OR NOT x14 OR NOT x13)
C86: (NOT x19 OR NOT x6 OR x30)
C87: (NOT x25 OR NOT x6 OR x8)
C88: (x27 OR x13 OR NOT x16)
C89: (x19 OR NOT x6 OR NOT x16)
C90: (NOT x25 OR NOT x16 OR NOT x19)
C91: (x21 OR NOT x32 OR NOT x2)
C92: (NOT x4 OR x15 OR x2)
C93: (NOT x38 OR x20 OR NOT x1)
C94: (x24 OR NOT x12 OR NOT x2)
C95: (x1 OR NOT x5 OR x26)
C96: (x6 OR x37 OR NOT x25)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 2000 solutions | π_EXACT = the ceiling share in both arms | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=0 x2=0 x3=1 x4=1 x5=1 x6=0 x7=0 x8=1 x9=1 x10=0 x11=0 x12=1 x13=0 x14=0 x15=1 x16=1 x17=1 x18=1 x19=0 x20=1 x21=0 x22=1 x23=0 x24=0 x25=1 x26=1 x27=1 x28=0 x29=1 x30=1 x31=1 x32=0 x33=1 x34=1 x35=1 x36=0 x37=1 x38=0 after N = 14 nodes (W = 3936); MENTION,MAJ: N = 36. If b < N: the default (UNSAT, or FILL = violates [17, 45, 94] at b = N/2). | π_C ≈ Δ = acc(control) − acc(trap), estimated per model; power 0.9 to detect π_C ≥ 0.10 with 300 pairs; if Δ̂ ≈ 0 the set bounds π_C ≤ 0.07 (upper 95%) and the backtracking share of the remaining weight is read from BT-on-v traces weighted by R_m | trap arm: DEC x1=1, then a DEC on a core variable, CONF, BT, CONF, BT to x1=0 (reference BTs on trap vars per variant: {'MENTION,TRUE': 4, 'MENTION,MAJ': 4, 'INDEX,TRUE': 3, 'INDEX,MAJ': 3, 'MOMS,TRUE': 2, 'MOMS,MAJ': 2}); control arm: no BT on the trap variable |
| BEAM-w | w=1: UNSAT; w=2: SAT; w=4: SAT | BEAM-1/BEAM-2 predictions differ from DPLL-b on specific items (listed in its output); deferred-conflict cells were not produced by this generator | CASES carried in parallel; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: UNSAT (default) | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=38) = 0.17, P(success / k=190) = 0.59, P(success / k=950) = 0.95; modal failure at k=38: violates [10], LM0=True, Hamming to nearest solution = 7 | π_F from LM0 near-miss trap errors, whose share should grow with d (barrier height) | x1 changes by FLIP inside a full candidate, never by BT |
| MIN-CONFLICTS | P(success / k=38) = 0.06, P(success / k=190) = 0.13, P(success / k=950) = 0.21 | π_F from LM0 near-miss trap errors, whose share should grow with d (barrier height) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C93); MENTION,MAJ: UNSAT (dead end at C93); MOMS,TRUE: UNSAT (dead end at C93); MOMS,MAJ: UNSAT (dead end at C93) / CONT violates: MENTION,TRUE: [93, 94]; MENTION,MAJ: [93, 94]; MOMS,TRUE: [93, 94]; MOMS,MAJ: [93, 94] | π_C ≈ Δ, with trap-arm errors dead-end-typed (x_v = 1); each dead-end trap error has LR ≈ 20 for C over DPLL-b | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=1 x3=1 x4=1 x5=0 x6=0 x7=1 x8=1 x9=1 x10=1 x11=0 x12=1 x13=1 x14=1 x15=1 x16=1 x17=1 x18=1 x19=1 x20=1 x21=1 x22=1 x23=1 x24=1 x25=1 x26=1 x27=1 x28=1 x29=1 x30=1 x31=0 x32=1 x33=1 x34=1 x35=1 x36=0 x37=1 x38=1 (violates [12, 73, 83, 90]) | π_C ≈ Δ, with trap-arm errors dead-end-typed (x_v = 1); each dead-end trap error has LR ≈ 20 for C over DPLL-b | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=0 x4=1 x5=1 x6=0 x7=0 x8=1 x9=1 x10=0 x11=0 x12=1 x13=0 x14=0 x15=1 x16=1 x17=1 x18=1 x19=1 x20=1 x21=0 x22=1 x23=0 x24=0 x25=1 x26=1 x27=1 x28=0 x29=1 x30=1 x31=0 x32=0 x33=1 x34=1 x35=1 x36=0 x37=1 x38=0 (violates [12, 17, 45, 57, 90, 94]) | π_POLARITY bounded by control-arm successes (POLARITY fails the control arm by construction) | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.675 (eps=1e-4) or 0.019 (eps=1e-3), W = 3936; otherwise a slip (one missed clause, or a spurious conflict) | π_NE contributes Δ ≤ 0.02 (tiny extra work): not separable from DPLL-b here (see E1–E3) | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0000 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), BEAM-2; pushes down BACKDOOR[k=2,OCC] (LR 0.013), MIN-CONFLICTS (k=190) (LR 0.141), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *near-miss (infeasible, LM0, V<=3)*: best fit MIN-CONFLICTS (k=190); pushes down EXACT (LR 0.015), DPLL-b (b >= N) (LR 0.015), BEAM-2 (LR 0.015), BACKDOOR[k=2,OCC] (LR 0.015), C-UC/STOP (LR 0.015), C-UC/CONT (LR 0.015), C-GREEDY (LR 0.015), POLARITY / ALWAYS-SAT (LR 0.015), B1 (UP-k, FLP-1) (LR 0.015), NOISY-EXACT (LR 0.199), RANDOM (LR 0.015)
- *infeasible (other)*: best fit C-UC/CONT, C-GREEDY, POLARITY / ALWAYS-SAT, RANDOM; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=190) (LR 0.013), MIN-CONFLICTS (k=190) (LR 0.013), C-UC/STOP (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.174)
- *UNSAT/UNKNOWN*: best fit BACKDOOR[k=2,OCC], C-UC/STOP, B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), WALK-k (k=190) (LR 0.013), MIN-CONFLICTS (k=190) (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=36, W=14208; MENTION,MAJ: N=36, W=14112; INDEX,TRUE: N=147, W=52128; INDEX,MAJ: N=145, W=51648; MOMS,TRUE: N=14, W=3936; MOMS,MAJ: N=14, W=3936. Every member's full output is in the JSONL `predictions` field.

### E4.8: d = 4, t = 2, control arm

- **Question tested:** When the value every greedy rule picks first is a dead end revealed only after another decision, does the model backtrack?
- **Controlled:** the same variable names and clause order in both arms; the trap variable's polarity counts, occurrence and first mention; n, m, clause length 3; both arms SAT
- **Varied:** 2 literal signs per trap (clauses [12, 30, 73, 84]) swap which gadget is live; d = 4 (chain length); t = 2 (traps)
- **Ground truth:** `{"answer": "SAT", "n_solutions": 2000, "solutions": ["x1=1 x2=1 x3=0 x4=1 x5=1 x6=0 x7=1 x8=1 x9=0 x10=1 x11=0 x12=1 x13=0 x14=0 x15=1 x16=1 x17=0 x18=0 x19=0 x20=1 x21=0 x22=1 x23=1 x24=1 x25=1 x26=0 x27=1 x28=0 x29=1 x30=1 x31=0 x32=0 x33=1 x34=1 x35=1 x36=1 x37=1 x38=1", "x1=1 x2=1 x3=0 x4=0 x5=0 x6=0 x7=0 x8=1 x9=0 x10=1 x11=0 x12=1 x13=0 x14=0 x15=0 x16=1 x17=0 x18=0 x19=0 x20=1 x21=0 x22=0 x23=1 x24=1 x25=1 x26=0 x27=1 x28=0 x29=0 x30=0 x31=0 x32=0 x33=0 x34=1 x35=0 x36=0 x37=1 x38=1", "..."]}`
- **Differs from E4.7 only in:** C12: (NOT x1 OR NOT x34 OR NOT x20) → (NOT x1 OR x34 OR NOT x20); C30: (x1 OR NOT x35 OR x5) → (x1 OR NOT x35 OR NOT x5); C73: (NOT x10 OR NOT x2 OR NOT x23) → (x10 OR NOT x2 OR NOT x23); C84: (NOT x9 OR x33 OR x2) → (NOT x9 OR NOT x33 OR x2)

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x38. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x1 OR x37 OR x27)
C2: (x2 OR x16 OR NOT x27)
C3: (NOT x36 OR x3 OR x1)
C4: (NOT x16 OR x14 OR x25)
C5: (x1 OR x36 OR x5)
C6: (NOT x6 OR NOT x27 OR x14)
C7: (NOT x25 OR x16 OR NOT x33)
C8: (x25 OR NOT x3 OR x16)
C9: (NOT x1 OR x34 OR NOT x29)
C10: (x8 OR NOT x1 OR NOT x34)
C11: (NOT x14 OR x26 OR x27)
C12: (NOT x1 OR x34 OR NOT x20)
C13: (x33 OR NOT x15 OR x2)
C14: (NOT x1 OR NOT x6 OR x14)
C15: (x17 OR NOT x21 OR NOT x2)
C16: (NOT x14 OR x25 OR NOT x24)
C17: (NOT x17 OR NOT x2 OR x10)
C18: (x1 OR x30 OR NOT x3)
C19: (x27 OR x37 OR x35)
C20: (x16 OR x19 OR x25)
C21: (NOT x33 OR x2 OR x31)
C22: (NOT x1 OR x11 OR x34)
C23: (NOT x10 OR x14 OR NOT x19)
C24: (NOT x38 OR x19 OR x25)
C25: (NOT x32 OR x25 OR x37)
C26: (x37 OR NOT x16 OR x25)
C27: (x12 OR NOT x16 OR x27)
C28: (x25 OR NOT x27 OR NOT x37)
C29: (x1 OR NOT x19 OR x6)
C30: (x1 OR NOT x35 OR NOT x5)
C31: (NOT x37 OR x6 OR x27)
C32: (NOT x2 OR x37 OR x16)
C33: (x2 OR NOT x13 OR x16)
C34: (x1 OR NOT x18 OR x35)
C35: (x37 OR x2 OR x25)
C36: (x27 OR NOT x28 OR x16)
C37: (NOT x2 OR x12 OR NOT x10)
C38: (x18 OR x6 OR NOT x14)
C39: (NOT x13 OR NOT x19 OR x2)
C40: (x2 OR NOT x28 OR x4)
C41: (NOT x25 OR NOT x6 OR x13)
C42: (NOT x1 OR NOT x11 OR x7)
C43: (x1 OR x5 OR NOT x30)
C44: (x17 OR NOT x13 OR x25)
C45: (x10 OR x32 OR NOT x2)
C46: (NOT x13 OR x34 OR x27)
C47: (x2 OR x27 OR NOT x16)
C48: (x19 OR NOT x13 OR NOT x6)
C49: (NOT x7 OR x29 OR NOT x1)
C50: (x6 OR NOT x13 OR x14)
C51: (NOT x25 OR x20 OR x16)
C52: (NOT x19 OR NOT x37 OR x25)
C53: (x16 OR NOT x14 OR x2)
C54: (NOT x2 OR NOT x24 OR x23)
C55: (x16 OR NOT x1 OR NOT x27)
C56: (x16 OR NOT x19 OR NOT x11)
C57: (NOT x8 OR x38 OR NOT x1)
C58: (NOT x5 OR NOT x13 OR NOT x6)
C59: (x4 OR NOT x6 OR NOT x13)
C60: (NOT x13 OR NOT x31 OR NOT x16)
C61: (NOT x6 OR x1 OR x25)
C62: (x2 OR NOT x31 OR x22)
C63: (NOT x37 OR x19 OR NOT x13)
C64: (x29 OR x37 OR x16)
C65: (NOT x37 OR NOT x6 OR x19)
C66: (NOT x25 OR x19 OR x16)
C67: (NOT x14 OR x13 OR x1)
C68: (NOT x23 OR x27 OR NOT x6)
C69: (NOT x25 OR NOT x2 OR x16)
C70: (x22 OR x13 OR NOT x6)
C71: (x16 OR x13 OR x1)
C72: (NOT x7 OR NOT x6 OR NOT x13)
C73: (x10 OR NOT x2 OR NOT x23)
C74: (x2 OR x28 OR x33)
C75: (x14 OR x25 OR x1)
C76: (x16 OR NOT x27 OR x9)
C77: (NOT x14 OR x6 OR x27)
C78: (NOT x21 OR NOT x14 OR x13)
C79: (x9 OR NOT x22 OR x2)
C80: (NOT x26 OR x18 OR x1)
C81: (x15 OR x27 OR x14)
C82: (NOT x37 OR x16 OR x6)
C83: (NOT x37 OR NOT x27 OR NOT x14)
C84: (NOT x9 OR NOT x33 OR x2)
C85: (NOT x36 OR NOT x14 OR NOT x13)
C86: (NOT x19 OR NOT x6 OR x30)
C87: (NOT x25 OR NOT x6 OR x8)
C88: (x27 OR x13 OR NOT x16)
C89: (x19 OR NOT x6 OR NOT x16)
C90: (NOT x25 OR NOT x16 OR NOT x19)
C91: (x21 OR NOT x32 OR NOT x2)
C92: (NOT x4 OR x15 OR x2)
C93: (NOT x38 OR x20 OR NOT x1)
C94: (x24 OR NOT x12 OR NOT x2)
C95: (x1 OR NOT x5 OR x26)
C96: (x6 OR x37 OR NOT x25)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 2000 solutions | π_EXACT = the ceiling share in both arms | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=1 x2=1 x3=0 x4=1 x5=0 x6=0 x7=1 x8=1 x9=1 x10=1 x11=0 x12=1 x13=0 x14=0 x15=1 x16=1 x17=1 x18=1 x19=0 x20=1 x21=1 x22=1 x23=1 x24=1 x25=1 x26=1 x27=1 x28=0 x29=1 x30=1 x31=0 x32=0 x33=0 x34=1 x35=1 x36=0 x37=1 x38=1 after N = 8 nodes (W = 2208); MENTION,MAJ: N = 9. If b < N: the default (UNSAT, or FILL = violates [94] at b = N/2). | π_C ≈ Δ = acc(control) − acc(trap), estimated per model; power 0.9 to detect π_C ≥ 0.10 with 300 pairs; if Δ̂ ≈ 0 the set bounds π_C ≤ 0.07 (upper 95%) and the backtracking share of the remaining weight is read from BT-on-v traces weighted by R_m | control arm: x1=1 is kept; reference BTs on trap vars per variant: {'MENTION,TRUE': 0, 'MENTION,MAJ': 0, 'INDEX,TRUE': 0, 'INDEX,MAJ': 0, 'MOMS,TRUE': 0, 'MOMS,MAJ': 0} (all 0) |
| BEAM-w | w=1: SAT; w=2: SAT; w=4: SAT | BEAM-1/BEAM-2 predictions differ from DPLL-b on specific items (listed in its output); deferred-conflict cells were not produced by this generator | CASES carried in parallel; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: UNSAT (default) | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=38) = 0.36, P(success / k=190) = 0.92, P(success / k=950) = 1.00; modal failure at k=38: violates [22, 37], LM0=True, Hamming to nearest solution = 10 | π_F from LM0 near-miss trap errors, whose share should grow with d (barrier height) | x1 changes by FLIP inside a full candidate, never by BT |
| MIN-CONFLICTS | P(success / k=38) = 0.15, P(success / k=190) = 0.20, P(success / k=950) = 0.21 | π_F from LM0 near-miss trap errors, whose share should grow with d (barrier height) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: SAT; MENTION,MAJ: SAT; MOMS,TRUE: SAT; MOMS,MAJ: SAT / CONT violates: MENTION,TRUE: []; MENTION,MAJ: []; MOMS,TRUE: []; MOMS,MAJ: [] | π_C ≈ Δ, with trap-arm errors dead-end-typed (x_v = 1); each dead-end trap error has LR ≈ 20 for C over DPLL-b | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=1 x3=1 x4=1 x5=0 x6=0 x7=1 x8=1 x9=1 x10=1 x11=0 x12=1 x13=1 x14=1 x15=1 x16=1 x17=1 x18=1 x19=1 x20=1 x21=1 x22=1 x23=1 x24=1 x25=1 x26=1 x27=1 x28=1 x29=1 x30=1 x31=0 x32=1 x33=1 x34=1 x35=1 x36=0 x37=1 x38=1 (violates [83, 90]) | π_C ≈ Δ, with trap-arm errors dead-end-typed (x_v = 1); each dead-end trap error has LR ≈ 20 for C over DPLL-b | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=0 x4=1 x5=0 x6=0 x7=0 x8=1 x9=1 x10=1 x11=0 x12=1 x13=0 x14=0 x15=1 x16=1 x17=1 x18=1 x19=1 x20=1 x21=0 x22=1 x23=0 x24=0 x25=1 x26=1 x27=1 x28=0 x29=1 x30=1 x31=0 x32=0 x33=0 x34=1 x35=1 x36=0 x37=1 x38=0 (violates [23, 57, 90, 94]) | π_POLARITY bounded by control-arm successes (POLARITY fails the control arm by construction) | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.802 (eps=1e-4) or 0.11 (eps=1e-3), W = 2208; otherwise a slip (one missed clause, or a spurious conflict) | π_NE contributes Δ ≤ 0.02 (tiny extra work): not separable from DPLL-b here (see E1–E3) | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0000 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A bounded by the pair ADR (each pair right on both twins has LR ≈ 0.05 against it) | no search; refers to size or density |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), BEAM-2, C-UC/STOP, C-UC/CONT; pushes down BACKDOOR[k=2,OCC] (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), RANDOM (LR 0.013)
- *near-miss (infeasible, LM0, V<=3)*: best fit C-GREEDY; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=190) (LR 0.092), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.111), RANDOM (LR 0.013)
- *infeasible (other)*: best fit POLARITY / ALWAYS-SAT, RANDOM; pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), BACKDOOR[k=2,OCC] (LR 0.013), WALK-k (k=190) (LR 0.013), MIN-CONFLICTS (k=190) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), B1 (UP-k, FLP-1) (LR 0.013), NOISY-EXACT (LR 0.111)
- *UNSAT/UNKNOWN*: best fit BACKDOOR[k=2,OCC], B1 (UP-k, FLP-1); pushes down EXACT (LR 0.013), DPLL-b (b >= N) (LR 0.013), BEAM-2 (LR 0.013), WALK-k (k=190) (LR 0.013), MIN-CONFLICTS (k=190) (LR 0.013), C-UC/STOP (LR 0.013), C-UC/CONT (LR 0.013), C-GREEDY (LR 0.013), POLARITY / ALWAYS-SAT (LR 0.013), NOISY-EXACT (LR 0.013), RANDOM (LR 0.013)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=9, W=2304; MENTION,MAJ: N=9, W=2208; INDEX,TRUE: N=17, W=4896; INDEX,MAJ: N=14, W=2688; MOMS,TRUE: N=8, W=2208; MOMS,MAJ: N=8, W=2208. Every member's full output is in the JSONL `predictions` field.

---

## E5

### Certificate pairs

| Item | Cell | Ground truth | Varied |
|------|------|--------------|--------|
| E5.1 | L easy, UNSAT arm | UNSAT | one literal in cluster K1 (UNSAT vs SAT); L easy: WalkSAT median flips on the SAT arm = 23 |
| E5.2 | L easy, SAT arm | SAT (24 solutions) | one literal in cluster K1 (UNSAT vs SAT); L easy: WalkSAT median flips on the SAT arm = 23 |
| E5.3 | L hard, UNSAT arm | UNSAT | one literal in cluster K1 (UNSAT vs SAT); L hard: WalkSAT median flips on the SAT arm = 85 |
| E5.4 | L hard, SAT arm | SAT (2 solutions) | one literal in cluster K1 (UNSAT vs SAT); L hard: WalkSAT median flips on the SAT arm = 85 |

**Direction table** (how each set-level outcome moves weight; the sizes are in the likelihood-ratio table below and in each item's hypothesis block):

| Observed outcome (set level) | Moves weight toward | Moves weight away from |
|------------------------------|---------------------|------------------------|
| High sensitivity (valid cores, FA6-complete trees) and low false alarm in both L cells | DPLL-b (within budget), NOISY-EXACT, EXACT | WALK-k / MIN-CONFLICTS, C, A-CORE, ALWAYS-SAT |
| False alarm rises in L-hard, with 'stubborn cluster' cores | WALK-k / MIN-CONFLICTS with an UNSAT default | DPLL-b, EXACT |
| UNSAT on both arms, core a random cluster (≈ 1/3 valid) | A-CORE | every search theory |
| SAT on both arms (UNSAT arm with an infeasible assignment) | ALWAYS-SAT, POLARITY, or F without an UNSAT default | DPLL-b, EXACT |

**Likelihood-ratio table** (computed). Each row asks: if one response per item (E5.1, E5.2, E5.3, E5.4) matched theory *h*'s most likely outcome, how much less likely is that pattern under each competitor? Entries are log10 LR(competitor : h), with a 5% slip floor on every theory, so −1.0 means the pattern pushes that competitor's weight down 10× relative to *h*. A cell of N independent responses multiplies these by about N. The readout is the mixture posterior over π, not a verdict (D_F_search.md §2.5).

| If responses match the modal pattern of h = | Tied with h (0.0) | Weakly disfavoured (−1 < log10 LR < 0) | Pushed down ≥ 10× (log10 LR ≤ −1) |
|---------------------------------------------|-------------------|----------------------------------------|-----------------------------------|
| EXACT | DPLL-b (b >= N) | NOISY-EXACT (-0.8) | DPLL-b[MOMS, b=20, Δ=UNSAT] (-3.5), WALK-k / MIN-CONFLICTS (-3.7), C-UC/STOP (-7.1), A-CORE (-4.5), POLARITY / ALWAYS-SAT (-7.1), B1 (UP-k, FLP-1) (-7.1), RANDOM (-7.1) |
| DPLL-b (b >= N) | EXACT | NOISY-EXACT (-0.8) | DPLL-b[MOMS, b=20, Δ=UNSAT] (-3.5), WALK-k / MIN-CONFLICTS (-3.7), C-UC/STOP (-7.1), A-CORE (-4.5), POLARITY / ALWAYS-SAT (-7.1), B1 (UP-k, FLP-1) (-7.1), RANDOM (-7.1) |
| DPLL-b[MOMS, b=20, Δ=UNSAT] | — | WALK-k / MIN-CONFLICTS (-0.8) | EXACT (-3.5), DPLL-b (b >= N) (-3.5), C-UC/STOP (-3.5), A-CORE (-3.9), POLARITY / ALWAYS-SAT (-7.1), B1 (UP-k, FLP-1) (-3.5), NOISY-EXACT (-3.7), RANDOM (-7.1) |
| WALK-k / MIN-CONFLICTS | — | — | EXACT (-2.7), DPLL-b (b >= N) (-2.7), C-UC/STOP (-2.7), A-CORE (-3.1), POLARITY / ALWAYS-SAT (-6.2), B1 (UP-k, FLP-1) (-2.7), NOISY-EXACT (-2.9), RANDOM (-6.2) |
| C-UC/STOP | B1 (UP-k, FLP-1) | A-CORE (-0.3) | EXACT (-7.1), DPLL-b (b >= N) (-7.1), DPLL-b[MOMS, b=20, Δ=UNSAT] (-3.5), WALK-k / MIN-CONFLICTS (-2.6), POLARITY / ALWAYS-SAT (-7.1), NOISY-EXACT (-7.1), RANDOM (-7.1) |
| A-CORE | — | — | EXACT (-6.7), DPLL-b (b >= N) (-6.7), DPLL-b[MOMS, b=20, Δ=UNSAT] (-3.2), WALK-k / MIN-CONFLICTS (-2.2), POLARITY / ALWAYS-SAT (-6.7), NOISY-EXACT (-6.7), RANDOM (-6.7) |
| POLARITY / ALWAYS-SAT | RANDOM | — | EXACT (-7.1), DPLL-b (b >= N) (-7.1), DPLL-b[MOMS, b=20, Δ=UNSAT] (-7.1), WALK-k / MIN-CONFLICTS (-2.6), C-UC/STOP (-7.1), A-CORE (-7.1), B1 (UP-k, FLP-1) (-7.1), NOISY-EXACT (-1.9) |
| B1 (UP-k, FLP-1) | C-UC/STOP | A-CORE (-0.3) | EXACT (-7.1), DPLL-b (b >= N) (-7.1), DPLL-b[MOMS, b=20, Δ=UNSAT] (-3.5), WALK-k / MIN-CONFLICTS (-2.6), POLARITY / ALWAYS-SAT (-7.1), NOISY-EXACT (-7.1), RANDOM (-7.1) |
| NOISY-EXACT | — | — | EXACT (-1.0), DPLL-b (b >= N) (-1.0), DPLL-b[MOMS, b=20, Δ=UNSAT] (-2.8), WALK-k / MIN-CONFLICTS (-1.5), C-UC/STOP (-6.3), A-CORE (-5.0), POLARITY / ALWAYS-SAT (-4.6), B1 (UP-k, FLP-1) (-6.3), RANDOM (-4.6) |
| RANDOM | POLARITY / ALWAYS-SAT | — | EXACT (-7.1), DPLL-b (b >= N) (-7.1), DPLL-b[MOMS, b=20, Δ=UNSAT] (-7.1), WALK-k / MIN-CONFLICTS (-2.6), C-UC/STOP (-7.1), A-CORE (-7.1), B1 (UP-k, FLP-1) (-7.1), NOISY-EXACT (-1.9) |

**Not distinguished by this set:** DPLL-b vs NOISY-EXACT within budget: both certify; separated by E1/E2 budget interactions.

### E5.1: L easy, UNSAT arm

- **Question tested:** When the model says UNSAT, has it refuted the formula, or is UNSAT a default it would also give on the satisfiable twin?
- **Controlled:** the same clause order and names in both arms; three equally dense 5-variable clusters in both arms; n, m
- **Varied:** one literal in cluster K1 (UNSAT vs SAT); L easy: WalkSAT median flips on the SAT arm = 23
- **Ground truth:** `{"answer": "UNSAT", "core_example": [1, 6, 8, 16, 20, 28, 39, 40, 60, 70, 72, 76]}`

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x22. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x20 OR NOT x1 OR x5)
C2: (x6 OR x3 OR x18)
C3: (NOT x3 OR x18 OR NOT x22)
C4: (x13 OR x16 OR NOT x4)
C5: (x9 OR NOT x12 OR NOT x15)
C6: (NOT x20 OR x1 OR x5)
C7: (x9 OR NOT x19 OR x12)
C8: (NOT x14 OR NOT x20 OR NOT x5)
C9: (x3 OR x18 OR x22)
C10: (NOT x9 OR x19 OR NOT x15)
C11: (NOT x9 OR NOT x19 OR x8)
C12: (NOT x17 OR x3 OR x18)
C13: (x13 OR x3 OR x18)
C14: (x10 OR x6 OR NOT x17)
C15: (x3 OR x22 OR NOT x21)
C16: (x14 OR x7 OR x1)
C17: (NOT x8 OR x3 OR NOT x6)
C18: (NOT x19 OR NOT x12 OR x15)
C19: (x1 OR NOT x18 OR NOT x2)
C20: (NOT x14 OR NOT x20 OR x5)
C21: (NOT x2 OR NOT x18 OR x17)
C22: (x21 OR NOT x2 OR x3)
C23: (x11 OR x2 OR NOT x3)
C24: (NOT x9 OR NOT x19 OR x15)
C25: (NOT x15 OR x17 OR x3)
C26: (x6 OR NOT x18 OR NOT x2)
C27: (x9 OR x2 OR x17)
C28: (NOT x14 OR x20 OR NOT x5)
C29: (x16 OR NOT x11 OR NOT x10)
C30: (x9 OR x19 OR NOT x12)
C31: (x17 OR x3 OR NOT x2)
C32: (NOT x9 OR NOT x12 OR x15)
C33: (NOT x17 OR x2 OR NOT x22)
C34: (NOT x3 OR NOT x22 OR NOT x21)
C35: (x19 OR x8 OR x15)
C36: (NOT x16 OR NOT x11 OR NOT x4)
C37: (NOT x4 OR NOT x18 OR NOT x22)
C38: (NOT x5 OR x17 OR x21)
C39: (NOT x14 OR x1 OR x5)
C40: (NOT x7 OR NOT x1 OR x5)
C41: (NOT x17 OR x18 OR x6)
C42: (x16 OR x10 OR x4)
C43: (NOT x3 OR NOT x17 OR x2)
C44: (x22 OR NOT x3 OR x6)
C45: (x6 OR NOT x21 OR x17)
C46: (NOT x3 OR x2 OR x21)
C47: (NOT x20 OR x17 OR x22)
C48: (NOT x18 OR NOT x2 OR x17)
C49: (NOT x13 OR NOT x11 OR x10)
C50: (x3 OR x18 OR x21)
C51: (x16 OR x3 OR NOT x22)
C52: (x9 OR x8 OR x12)
C53: (x18 OR x21 OR x2)
C54: (NOT x9 OR x19 OR x12)
C55: (x3 OR NOT x22 OR NOT x17)
C56: (x17 OR NOT x3 OR NOT x21)
C57: (NOT x13 OR x10 OR x4)
C58: (x19 OR x8 OR NOT x15)
C59: (x12 OR NOT x22 OR x3)
C60: (x14 OR x7 OR NOT x20)
C61: (NOT x3 OR NOT x18 OR x17)
C62: (NOT x7 OR x2 OR x17)
C63: (NOT x17 OR x18 OR x3)
C64: (x14 OR NOT x22 OR x21)
C65: (x19 OR NOT x18 OR x21)
C66: (NOT x13 OR NOT x16 OR NOT x10)
C67: (x18 OR NOT x17 OR x3)
C68: (x13 OR NOT x16 OR x11)
C69: (NOT x19 OR NOT x8 OR NOT x15)
C70: (x7 OR x20 OR NOT x5)
C71: (x13 OR NOT x16 OR NOT x4)
C72: (x14 OR NOT x20 OR NOT x5)
C73: (NOT x13 OR x11 OR NOT x4)
C74: (NOT x3 OR x22 OR NOT x18)
C75: (x16 OR x11 OR x4)
C76: (x14 OR NOT x7 OR x20)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT", "core": [ ... ]} (the numbers of at most 24 clauses that cannot all be satisfied together)
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | UNSAT | π_EXACT = ADR ceiling | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: UNSAT after N = 32 nodes (W = 7752); MENTION,MAJ: N = 10. If b < N: the default (UNSAT, or FILL = violates [8, 66] at b = N/2). | π_certify (DPLL-b within budget + NE + EXACT) from valid-core sensitivity; each valid-core, FA6-complete UNSAT has LR ≈ 20 against WALK-k and C; 200 pairs give power 0.95 (pooled) to detect a 0.10 difference in false alarm between L cells, i.e. π_F ≥ 0.15 | MOMS,MAJ reference: DEC = 16, BT = 16, CONF = 17, PROP = 69; first decisions (var, value) = [(3, 1), (22, 0), (2, 1)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: UNSAT; w=2: UNSAT; w=4: UNSAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT; k=3,INDEX: UNSAT (default) | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | never certifies UNSAT; ends in a near-miss: k=22: violates [60], LM0=True, Hamming to nearest solution = None | π_F from the L-dependence of false alarms; a null bounds π_F ≤ 0.12 (upper 95%, pooled) | FULL candidate, VIOL list, FLIP moves; DEC <= 1; FLIP until cap or GIVEUP |
| MIN-CONFLICTS | P(success / k=22) = 0.00, P(success / k=110) = 0.00, P(success / k=550) = 0.00 | π_F from the L-dependence of false alarms; a null bounds π_F ≤ 0.12 (upper 95%, pooled) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C72); MENTION,MAJ: UNSAT (dead end at C76); MOMS,TRUE: UNSAT (dead end at C28); MOMS,MAJ: UNSAT (dead end at C69) / CONT violates: MENTION,TRUE: [64, 69, 72, 75]; MENTION,MAJ: [69, 76]; MOMS,TRUE: [28, 66, 69]; MOMS,MAJ: [69, 76] | π_C from dead-end false UNSATs on both arms | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=1 x3=1 x4=0 x5=0 x6=1 x7=0 x8=1 x9=1 x10=1 x11=1 x12=0 x13=0 x14=1 x15=0 x16=1 x17=1 x18=0 x19=1 x20=0 x21=1 x22=0 (violates [1, 24]) | π_C from dead-end false UNSATs on both arms | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=1 x4=0 x5=1 x6=1 x7=1 x8=1 x9=1 x10=1 x11=1 x12=1 x13=1 x14=1 x15=0 x16=1 x17=1 x18=1 x19=1 x20=0 x21=1 x22=0 (violates [18, 24, 28, 32, 66, 74]) | π_POLARITY: each correct answer where the polarity assignment is infeasible has LR ≈ 0.05 against it | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.461 (eps=1e-4) or 0.0 (eps=1e-3), W = 7752; otherwise a slip (one missed clause, or a spurious conflict) | inside π_certify; not separable from DPLL-b here | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0000 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A-CORE from cluster-random cores (valid ≈ 1/3) given on both arms | no search; refers to size or density |
| A-CORE (list the densest cluster) | UNSAT with one of the three clusters: K1 [1, 6, 8, 16, 20, 28, 39, 40, 60, 70, 72, 76] (valid here: True), K2 [4, 29, 36, 42, 49, 57, 66, 68, 71, 73, 75], K3 [5, 7, 10, 11, 18, 24, 30, 32, 35, 52, 54, 58, 69] (each picked with P = 1/3) | sensitivity ≈ 1/3; false alarm = its UNSAT rate on SAT arms (same as on UNSAT arms) | notices dense groups of clauses; no case analysis |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *UNSAT + valid core*: best fit EXACT, DPLL-b (b >= N); pushes down DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.017), WALK-k / MIN-CONFLICTS (LR 0.017), C-UC/STOP (LR 0.017), POLARITY / ALWAYS-SAT (LR 0.017), B1 (UP-k, FLP-1) (LR 0.017), RANDOM (LR 0.017)
- *UNSAT, no valid core*: best fit DPLL-b[MOMS, b=20, Δ=UNSAT], C-UC/STOP, B1 (UP-k, FLP-1); pushes down EXACT (LR 0.017), DPLL-b (b >= N) (LR 0.017), POLARITY / ALWAYS-SAT (LR 0.017), NOISY-EXACT (LR 0.017), RANDOM (LR 0.017)
- *SAT claim (infeasible)*: best fit POLARITY / ALWAYS-SAT, RANDOM; pushes down EXACT (LR 0.017), DPLL-b (b >= N) (LR 0.017), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.017), C-UC/STOP (LR 0.017), A-CORE (LR 0.017), B1 (UP-k, FLP-1) (LR 0.017)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=10, W=1748; MENTION,MAJ: N=10, W=1748; INDEX,TRUE: N=170, W=33136; INDEX,MAJ: N=170, W=33136; MOMS,TRUE: N=32, W=7752; MOMS,MAJ: N=32, W=7752. Every member's full output is in the JSONL `predictions` field.

### E5.2: L easy, SAT arm

- **Question tested:** When the model says UNSAT, has it refuted the formula, or is UNSAT a default it would also give on the satisfiable twin?
- **Controlled:** the same clause order and names in both arms; three equally dense 5-variable clusters in both arms; n, m
- **Varied:** one literal in cluster K1 (UNSAT vs SAT); L easy: WalkSAT median flips on the SAT arm = 23
- **Ground truth:** `{"answer": "SAT", "n_solutions": 24, "solutions": ["x1=1 x2=1 x3=1 x4=0 x5=0 x6=1 x7=0 x8=1 x9=0 x10=0 x11=1 x12=0 x13=0 x14=1 x15=1 x16=1 x17=1 x18=0 x19=0 x20=0 x21=1 x22=0", "x1=1 x2=1 x3=1 x4=0 x5=0 x6=1 x7=0 x8=1 x9=0 x10=0 x11=1 x12=0 x13=0 x14=0 x15=0 x16=1 x17=0 x18=0 x19=0 x20=0 x21=0 x22=0", "..."]}`
- **Differs from E5.1 only in:** C1: (x20 OR NOT x1 OR x5) → (x20 OR x1 OR x5)

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x22. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x20 OR x1 OR x5)
C2: (x6 OR x3 OR x18)
C3: (NOT x3 OR x18 OR NOT x22)
C4: (x13 OR x16 OR NOT x4)
C5: (x9 OR NOT x12 OR NOT x15)
C6: (NOT x20 OR x1 OR x5)
C7: (x9 OR NOT x19 OR x12)
C8: (NOT x14 OR NOT x20 OR NOT x5)
C9: (x3 OR x18 OR x22)
C10: (NOT x9 OR x19 OR NOT x15)
C11: (NOT x9 OR NOT x19 OR x8)
C12: (NOT x17 OR x3 OR x18)
C13: (x13 OR x3 OR x18)
C14: (x10 OR x6 OR NOT x17)
C15: (x3 OR x22 OR NOT x21)
C16: (x14 OR x7 OR x1)
C17: (NOT x8 OR x3 OR NOT x6)
C18: (NOT x19 OR NOT x12 OR x15)
C19: (x1 OR NOT x18 OR NOT x2)
C20: (NOT x14 OR NOT x20 OR x5)
C21: (NOT x2 OR NOT x18 OR x17)
C22: (x21 OR NOT x2 OR x3)
C23: (x11 OR x2 OR NOT x3)
C24: (NOT x9 OR NOT x19 OR x15)
C25: (NOT x15 OR x17 OR x3)
C26: (x6 OR NOT x18 OR NOT x2)
C27: (x9 OR x2 OR x17)
C28: (NOT x14 OR x20 OR NOT x5)
C29: (x16 OR NOT x11 OR NOT x10)
C30: (x9 OR x19 OR NOT x12)
C31: (x17 OR x3 OR NOT x2)
C32: (NOT x9 OR NOT x12 OR x15)
C33: (NOT x17 OR x2 OR NOT x22)
C34: (NOT x3 OR NOT x22 OR NOT x21)
C35: (x19 OR x8 OR x15)
C36: (NOT x16 OR NOT x11 OR NOT x4)
C37: (NOT x4 OR NOT x18 OR NOT x22)
C38: (NOT x5 OR x17 OR x21)
C39: (NOT x14 OR x1 OR x5)
C40: (NOT x7 OR NOT x1 OR x5)
C41: (NOT x17 OR x18 OR x6)
C42: (x16 OR x10 OR x4)
C43: (NOT x3 OR NOT x17 OR x2)
C44: (x22 OR NOT x3 OR x6)
C45: (x6 OR NOT x21 OR x17)
C46: (NOT x3 OR x2 OR x21)
C47: (NOT x20 OR x17 OR x22)
C48: (NOT x18 OR NOT x2 OR x17)
C49: (NOT x13 OR NOT x11 OR x10)
C50: (x3 OR x18 OR x21)
C51: (x16 OR x3 OR NOT x22)
C52: (x9 OR x8 OR x12)
C53: (x18 OR x21 OR x2)
C54: (NOT x9 OR x19 OR x12)
C55: (x3 OR NOT x22 OR NOT x17)
C56: (x17 OR NOT x3 OR NOT x21)
C57: (NOT x13 OR x10 OR x4)
C58: (x19 OR x8 OR NOT x15)
C59: (x12 OR NOT x22 OR x3)
C60: (x14 OR x7 OR NOT x20)
C61: (NOT x3 OR NOT x18 OR x17)
C62: (NOT x7 OR x2 OR x17)
C63: (NOT x17 OR x18 OR x3)
C64: (x14 OR NOT x22 OR x21)
C65: (x19 OR NOT x18 OR x21)
C66: (NOT x13 OR NOT x16 OR NOT x10)
C67: (x18 OR NOT x17 OR x3)
C68: (x13 OR NOT x16 OR x11)
C69: (NOT x19 OR NOT x8 OR NOT x15)
C70: (x7 OR x20 OR NOT x5)
C71: (x13 OR NOT x16 OR NOT x4)
C72: (x14 OR NOT x20 OR NOT x5)
C73: (NOT x13 OR x11 OR NOT x4)
C74: (NOT x3 OR x22 OR NOT x18)
C75: (x16 OR x11 OR x4)
C76: (x14 OR NOT x7 OR x20)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT", "core": [ ... ]} (the numbers of at most 24 clauses that cannot all be satisfied together)
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 24 solutions | π_EXACT = ADR ceiling | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=1 x2=1 x3=1 x4=0 x5=0 x6=1 x7=0 x8=1 x9=0 x10=1 x11=1 x12=0 x13=0 x14=1 x15=0 x16=1 x17=1 x18=0 x19=0 x20=0 x21=1 x22=0 after N = 15 nodes (W = 2432); MENTION,MAJ: N = 14. If b < N: the default (UNSAT, or FILL = violates [18, 24, 28, 32, 66] at b = N/2). | π_certify (DPLL-b within budget + NE + EXACT) from valid-core sensitivity; each valid-core, FA6-complete UNSAT has LR ≈ 20 against WALK-k and C; 200 pairs give power 0.95 (pooled) to detect a 0.10 difference in false alarm between L cells, i.e. π_F ≥ 0.15 | MOMS,MAJ reference: DEC = 11, BT = 4, CONF = 4, PROP = 16; first decisions (var, value) = [(3, 1), (22, 0), (2, 1)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: UNSAT; w=2: SAT; w=4: SAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: UNSAT (default) | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=22) = 0.34, P(success / k=110) = 0.92, P(success / k=550) = 1.00; modal failure at k=22: violates [5], LM0=True, Hamming to nearest solution = 3 | π_F from the L-dependence of false alarms; a null bounds π_F ≤ 0.12 (upper 95%, pooled) | FULL candidate, VIOL list, FLIP moves; DEC <= 1; #FLIP about the WalkSAT median of 23 |
| MIN-CONFLICTS | P(success / k=22) = 0.02, P(success / k=110) = 0.31, P(success / k=550) = 0.62 | π_F from the L-dependence of false alarms; a null bounds π_F ≤ 0.12 (upper 95%, pooled) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C72); MENTION,MAJ: UNSAT (dead end at C69); MOMS,TRUE: UNSAT (dead end at C28); MOMS,MAJ: UNSAT (dead end at C69) / CONT violates: MENTION,TRUE: [64, 69, 72, 75]; MENTION,MAJ: [69]; MOMS,TRUE: [28, 66, 69]; MOMS,MAJ: [69, 76] | π_C from dead-end false UNSATs on both arms | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=1 x2=1 x3=1 x4=0 x5=0 x6=1 x7=0 x8=1 x9=1 x10=1 x11=1 x12=0 x13=0 x14=1 x15=0 x16=1 x17=1 x18=0 x19=1 x20=0 x21=1 x22=0 (violates [24]) | π_C from dead-end false UNSATs on both arms | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=1 x2=1 x3=1 x4=0 x5=1 x6=1 x7=1 x8=1 x9=1 x10=1 x11=1 x12=1 x13=1 x14=1 x15=0 x16=1 x17=1 x18=1 x19=1 x20=0 x21=1 x22=0 (violates [18, 24, 28, 32, 66, 74]) | π_POLARITY: each correct answer where the polarity assignment is infeasible has LR ≈ 0.05 against it | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.784 (eps=1e-4) or 0.088 (eps=1e-3), W = 2432; otherwise a slip (one missed clause, or a spurious conflict) | inside π_certify; not separable from DPLL-b here | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0000 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A-CORE from cluster-random cores (valid ≈ 1/3) given on both arms | no search; refers to size or density |
| A-CORE (list the densest cluster) | UNSAT with one of the three clusters: K1 [1, 6, 8, 16, 20, 28, 39, 40, 60, 70, 72, 76] (valid here: False), K2 [4, 29, 36, 42, 49, 57, 66, 68, 71, 73, 75], K3 [5, 7, 10, 11, 18, 24, 30, 32, 35, 52, 54, 58, 69] (each picked with P = 1/3) | sensitivity ≈ 1/3; false alarm = its UNSAT rate on SAT arms (same as on UNSAT arms) | notices dense groups of clauses; no case analysis |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), DPLL-b[MOMS, b=20, Δ=UNSAT]; pushes down C-UC/STOP (LR 0.017), A-CORE (LR 0.017), POLARITY / ALWAYS-SAT (LR 0.017), B1 (UP-k, FLP-1) (LR 0.017), RANDOM (LR 0.017)
- *UNSAT (false alarm)*: best fit C-UC/STOP, A-CORE, B1 (UP-k, FLP-1); pushes down EXACT (LR 0.017), DPLL-b (b >= N) (LR 0.017), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.017), WALK-k / MIN-CONFLICTS (LR 0.057), POLARITY / ALWAYS-SAT (LR 0.017), NOISY-EXACT (LR 0.017), RANDOM (LR 0.017)
- *infeasible SAT*: best fit POLARITY / ALWAYS-SAT, RANDOM; pushes down EXACT (LR 0.017), DPLL-b (b >= N) (LR 0.017), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.017), WALK-k / MIN-CONFLICTS (LR 0.057), C-UC/STOP (LR 0.017), A-CORE (LR 0.017), B1 (UP-k, FLP-1) (LR 0.017)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=33, W=6156; MENTION,MAJ: N=14, W=2128; INDEX,TRUE: N=101, W=16188; INDEX,MAJ: N=14, W=1596; MOMS,TRUE: N=24, W=4864; MOMS,MAJ: N=15, W=2432. Every member's full output is in the JSONL `predictions` field.

### E5.3: L hard, UNSAT arm

- **Question tested:** When the model says UNSAT, has it refuted the formula, or is UNSAT a default it would also give on the satisfiable twin?
- **Controlled:** the same clause order and names in both arms; three equally dense 5-variable clusters in both arms; n, m
- **Varied:** one literal in cluster K1 (UNSAT vs SAT); L hard: WalkSAT median flips on the SAT arm = 85
- **Ground truth:** `{"answer": "UNSAT", "core_example": [10, 12, 13, 29, 30, 36, 39, 43, 44, 56, 69, 73]}`

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x22. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (NOT x20 OR x5 OR x9)
C2: (NOT x21 OR NOT x12 OR NOT x16)
C3: (NOT x19 OR NOT x2 OR NOT x12)
C4: (NOT x4 OR NOT x21 OR x13)
C5: (x19 OR NOT x5 OR NOT x9)
C6: (x19 OR NOT x15 OR NOT x9)
C7: (NOT x1 OR NOT x7 OR NOT x8)
C8: (NOT x5 OR x15 OR NOT x9)
C9: (x21 OR x16 OR NOT x22)
C10: (NOT x14 OR NOT x6 OR NOT x10)
C11: (x18 OR x8 OR x17)
C12: (NOT x14 OR NOT x6 OR x10)
C13: (x6 OR x3 OR x11)
C14: (x2 OR x13 OR NOT x4)
C15: (x6 OR x22 OR x12)
C16: (NOT x18 OR x8 OR NOT x17)
C17: (x22 OR x21 OR NOT x16)
C18: (x7 OR NOT x8 OR NOT x17)
C19: (x20 OR x21 OR NOT x12)
C20: (x9 OR x21 OR x16)
C21: (x1 OR NOT x12 OR x2)
C22: (x16 OR NOT x4 OR x12)
C23: (NOT x20 OR NOT x19 OR NOT x5)
C24: (NOT x16 OR x22 OR x12)
C25: (NOT x13 OR x2 OR x21)
C26: (NOT x18 OR x8 OR x17)
C27: (NOT x21 OR NOT x12 OR NOT x4)
C28: (x13 OR x12 OR NOT x2)
C29: (NOT x14 OR NOT x10 OR NOT x11)
C30: (x6 OR NOT x3 OR x11)
C31: (x7 OR NOT x8 OR x17)
C32: (NOT x20 OR x5 OR NOT x9)
C33: (x21 OR NOT x12 OR x4)
C34: (x18 OR NOT x1 OR NOT x17)
C35: (NOT x16 OR x13 OR NOT x4)
C36: (x14 OR NOT x6 OR x10)
C37: (x1 OR x7 OR NOT x17)
C38: (x12 OR NOT x2 OR NOT x4)
C39: (x14 OR NOT x6 OR x3)
C40: (NOT x18 OR NOT x1 OR NOT x7)
C41: (NOT x17 OR NOT x12 OR NOT x21)
C42: (x2 OR NOT x4 OR NOT x22)
C43: (x14 OR x6 OR NOT x3)
C44: (x14 OR NOT x6 OR NOT x11)
C45: (x5 OR x15 OR NOT x9)
C46: (x14 OR NOT x4 OR x13)
C47: (NOT x2 OR NOT x4 OR NOT x22)
C48: (x7 OR NOT x2 OR NOT x12)
C49: (NOT x21 OR x16 OR NOT x13)
C50: (x19 OR NOT x5 OR x9)
C51: (x13 OR x12 OR x21)
C52: (x16 OR NOT x13 OR x21)
C53: (x18 OR NOT x2 OR x12)
C54: (x3 OR NOT x12 OR NOT x4)
C55: (x18 OR NOT x7 OR NOT x8)
C56: (x6 OR x3 OR NOT x11)
C57: (NOT x21 OR NOT x16 OR NOT x12)
C58: (NOT x13 OR x21 OR NOT x4)
C59: (NOT x15 OR NOT x12 OR x21)
C60: (NOT x4 OR x12 OR x21)
C61: (x20 OR NOT x19 OR x9)
C62: (x5 OR NOT x4 OR NOT x21)
C63: (NOT x12 OR x21 OR x2)
C64: (NOT x22 OR x13 OR NOT x16)
C65: (x20 OR x5 OR NOT x15)
C66: (x16 OR NOT x13 OR x2)
C67: (NOT x11 OR x13 OR x21)
C68: (x5 OR x15 OR x9)
C69: (x10 OR NOT x3 OR NOT x11)
C70: (x18 OR NOT x7 OR NOT x17)
C71: (NOT x2 OR x12 OR NOT x16)
C72: (NOT x8 OR x16 OR x12)
C73: (NOT x10 OR NOT x3 OR x11)
C74: (NOT x10 OR NOT x4 OR x13)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT", "core": [ ... ]} (the numbers of at most 24 clauses that cannot all be satisfied together)
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | UNSAT | π_EXACT = ADR ceiling | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: UNSAT after N = 26 nodes (W = 6438); MENTION,MAJ: N = 90. If b < N: the default (UNSAT, or FILL = violates [12, 26, 32] at b = N/2). | π_certify (DPLL-b within budget + NE + EXACT) from valid-core sensitivity; each valid-core, FA6-complete UNSAT has LR ≈ 20 against WALK-k and C; 200 pairs give power 0.95 (pooled) to detect a 0.10 difference in false alarm between L cells, i.e. π_F ≥ 0.15 | MOMS,MAJ reference: DEC = 13, BT = 13, CONF = 14, PROP = 60; first decisions (var, value) = [(12, 0), (16, 1), (5, 1)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: UNSAT; w=2: UNSAT; w=4: UNSAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: UNSAT (default) | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | never certifies UNSAT; ends in a near-miss: k=22: violates [39], LM0=True, Hamming to nearest solution = None | π_F from the L-dependence of false alarms; a null bounds π_F ≤ 0.12 (upper 95%, pooled) | FULL candidate, VIOL list, FLIP moves; DEC <= 1; FLIP until cap or GIVEUP |
| MIN-CONFLICTS | P(success / k=22) = 0.00, P(success / k=110) = 0.00, P(success / k=550) = 0.00 | π_F from the L-dependence of false alarms; a null bounds π_F ≤ 0.12 (upper 95%, pooled) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C50); MENTION,MAJ: UNSAT (dead end at C50); MOMS,TRUE: UNSAT (dead end at C45); MOMS,MAJ: UNSAT (dead end at C61) / CONT violates: MENTION,TRUE: [12, 26, 40, 50]; MENTION,MAJ: [12, 50]; MOMS,TRUE: [12, 45]; MOMS,MAJ: [26, 56, 61] | π_C from dead-end false UNSATs on both arms | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=0 x2=1 x3=0 x4=0 x5=1 x6=1 x7=1 x8=1 x9=0 x10=0 x11=1 x12=1 x13=0 x14=1 x15=1 x16=0 x17=0 x18=1 x19=0 x20=1 x21=1 x22=1 (violates [12, 50]) | π_C from dead-end false UNSATs on both arms | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=0 x2=0 x3=1 x4=0 x5=1 x6=1 x7=1 x8=0 x9=1 x10=0 x11=0 x12=0 x13=1 x14=1 x15=1 x16=1 x17=0 x18=1 x19=1 x20=1 x21=1 x22=0 (violates [12, 23, 24, 26]) | π_POLARITY: each correct answer where the polarity assignment is infeasible has LR ≈ 0.05 against it | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.525 (eps=1e-4) or 0.002 (eps=1e-3), W = 6438; otherwise a slip (one missed clause, or a spurious conflict) | inside π_certify; not separable from DPLL-b here | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0000 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A-CORE from cluster-random cores (valid ≈ 1/3) given on both arms | no search; refers to size or density |
| A-CORE (list the densest cluster) | UNSAT with one of the three clusters: K1 [10, 12, 13, 29, 30, 36, 39, 43, 44, 56, 69, 73] (valid here: True), K2 [1, 5, 6, 8, 23, 32, 45, 50, 61, 65, 68], K3 [7, 11, 16, 18, 26, 31, 34, 37, 40, 55, 70] (each picked with P = 1/3) | sensitivity ≈ 1/3; false alarm = its UNSAT rate on SAT arms (same as on UNSAT arms) | notices dense groups of clauses; no case analysis |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *UNSAT + valid core*: best fit EXACT, DPLL-b (b >= N); pushes down DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.017), WALK-k / MIN-CONFLICTS (LR 0.017), C-UC/STOP (LR 0.017), POLARITY / ALWAYS-SAT (LR 0.017), B1 (UP-k, FLP-1) (LR 0.017), RANDOM (LR 0.017)
- *UNSAT, no valid core*: best fit DPLL-b[MOMS, b=20, Δ=UNSAT], C-UC/STOP, B1 (UP-k, FLP-1); pushes down EXACT (LR 0.017), DPLL-b (b >= N) (LR 0.017), POLARITY / ALWAYS-SAT (LR 0.017), NOISY-EXACT (LR 0.017), RANDOM (LR 0.017)
- *SAT claim (infeasible)*: best fit POLARITY / ALWAYS-SAT, RANDOM; pushes down EXACT (LR 0.017), DPLL-b (b >= N) (LR 0.017), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.017), C-UC/STOP (LR 0.017), A-CORE (LR 0.017), B1 (UP-k, FLP-1) (LR 0.017)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=90, W=14356; MENTION,MAJ: N=90, W=14356; INDEX,TRUE: N=132, W=24716; INDEX,MAJ: N=132, W=24716; MOMS,TRUE: N=26, W=6438; MOMS,MAJ: N=26, W=6438. Every member's full output is in the JSONL `predictions` field.

### E5.4: L hard, SAT arm

- **Question tested:** When the model says UNSAT, has it refuted the formula, or is UNSAT a default it would also give on the satisfiable twin?
- **Controlled:** the same clause order and names in both arms; three equally dense 5-variable clusters in both arms; n, m
- **Varied:** one literal in cluster K1 (UNSAT vs SAT); L hard: WalkSAT median flips on the SAT arm = 85
- **Ground truth:** `{"answer": "SAT", "n_solutions": 2, "solutions": ["x1=0 x2=0 x3=1 x4=0 x5=1 x6=1 x7=1 x8=1 x9=1 x10=1 x11=1 x12=0 x13=1 x14=0 x15=1 x16=1 x17=1 x18=1 x19=1 x20=0 x21=1 x22=1", "x1=0 x2=0 x3=1 x4=0 x5=1 x6=1 x7=1 x8=1 x9=1 x10=1 x11=1 x12=0 x13=1 x14=0 x15=1 x16=1 x17=0 x18=1 x19=1 x20=0 x21=1 x22=1"]}`
- **Differs from E5.3 only in:** C44: (x14 OR NOT x6 OR NOT x11) → (x14 OR x6 OR NOT x11)

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x22. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (NOT x20 OR x5 OR x9)
C2: (NOT x21 OR NOT x12 OR NOT x16)
C3: (NOT x19 OR NOT x2 OR NOT x12)
C4: (NOT x4 OR NOT x21 OR x13)
C5: (x19 OR NOT x5 OR NOT x9)
C6: (x19 OR NOT x15 OR NOT x9)
C7: (NOT x1 OR NOT x7 OR NOT x8)
C8: (NOT x5 OR x15 OR NOT x9)
C9: (x21 OR x16 OR NOT x22)
C10: (NOT x14 OR NOT x6 OR NOT x10)
C11: (x18 OR x8 OR x17)
C12: (NOT x14 OR NOT x6 OR x10)
C13: (x6 OR x3 OR x11)
C14: (x2 OR x13 OR NOT x4)
C15: (x6 OR x22 OR x12)
C16: (NOT x18 OR x8 OR NOT x17)
C17: (x22 OR x21 OR NOT x16)
C18: (x7 OR NOT x8 OR NOT x17)
C19: (x20 OR x21 OR NOT x12)
C20: (x9 OR x21 OR x16)
C21: (x1 OR NOT x12 OR x2)
C22: (x16 OR NOT x4 OR x12)
C23: (NOT x20 OR NOT x19 OR NOT x5)
C24: (NOT x16 OR x22 OR x12)
C25: (NOT x13 OR x2 OR x21)
C26: (NOT x18 OR x8 OR x17)
C27: (NOT x21 OR NOT x12 OR NOT x4)
C28: (x13 OR x12 OR NOT x2)
C29: (NOT x14 OR NOT x10 OR NOT x11)
C30: (x6 OR NOT x3 OR x11)
C31: (x7 OR NOT x8 OR x17)
C32: (NOT x20 OR x5 OR NOT x9)
C33: (x21 OR NOT x12 OR x4)
C34: (x18 OR NOT x1 OR NOT x17)
C35: (NOT x16 OR x13 OR NOT x4)
C36: (x14 OR NOT x6 OR x10)
C37: (x1 OR x7 OR NOT x17)
C38: (x12 OR NOT x2 OR NOT x4)
C39: (x14 OR NOT x6 OR x3)
C40: (NOT x18 OR NOT x1 OR NOT x7)
C41: (NOT x17 OR NOT x12 OR NOT x21)
C42: (x2 OR NOT x4 OR NOT x22)
C43: (x14 OR x6 OR NOT x3)
C44: (x14 OR x6 OR NOT x11)
C45: (x5 OR x15 OR NOT x9)
C46: (x14 OR NOT x4 OR x13)
C47: (NOT x2 OR NOT x4 OR NOT x22)
C48: (x7 OR NOT x2 OR NOT x12)
C49: (NOT x21 OR x16 OR NOT x13)
C50: (x19 OR NOT x5 OR x9)
C51: (x13 OR x12 OR x21)
C52: (x16 OR NOT x13 OR x21)
C53: (x18 OR NOT x2 OR x12)
C54: (x3 OR NOT x12 OR NOT x4)
C55: (x18 OR NOT x7 OR NOT x8)
C56: (x6 OR x3 OR NOT x11)
C57: (NOT x21 OR NOT x16 OR NOT x12)
C58: (NOT x13 OR x21 OR NOT x4)
C59: (NOT x15 OR NOT x12 OR x21)
C60: (NOT x4 OR x12 OR x21)
C61: (x20 OR NOT x19 OR x9)
C62: (x5 OR NOT x4 OR NOT x21)
C63: (NOT x12 OR x21 OR x2)
C64: (NOT x22 OR x13 OR NOT x16)
C65: (x20 OR x5 OR NOT x15)
C66: (x16 OR NOT x13 OR x2)
C67: (NOT x11 OR x13 OR x21)
C68: (x5 OR x15 OR x9)
C69: (x10 OR NOT x3 OR NOT x11)
C70: (x18 OR NOT x7 OR NOT x17)
C71: (NOT x2 OR x12 OR NOT x16)
C72: (NOT x8 OR x16 OR x12)
C73: (NOT x10 OR NOT x3 OR x11)
C74: (NOT x10 OR NOT x4 OR x13)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT", "core": [ ... ]} (the numbers of at most 24 clauses that cannot all be satisfied together)
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT (solves it exactly) | SAT with one of the 2 solutions | π_EXACT = ADR ceiling | a complete search or a sound derivation; no GIVEUP; FA1 = 1 |
| DPLL-b | MOMS,MAJ: SAT x1=0 x2=0 x3=1 x4=0 x5=1 x6=1 x7=1 x8=1 x9=1 x10=1 x11=1 x12=0 x13=1 x14=0 x15=1 x16=1 x17=0 x18=1 x19=1 x20=0 x21=1 x22=1 after N = 10 nodes (W = 2072); MENTION,MAJ: N = 24. If b < N: the default (UNSAT, or FILL = violates [12, 26] at b = N/2). | π_certify (DPLL-b within budget + NE + EXACT) from valid-core sensitivity; each valid-core, FA6-complete UNSAT has LR ≈ 20 against WALK-k and C; 200 pairs give power 0.95 (pooled) to detect a 0.10 difference in false alarm between L cells, i.e. π_F ≥ 0.15 | MOMS,MAJ reference: DEC = 8, BT = 2, CONF = 2, PROP = 17; first decisions (var, value) = [(12, 0), (16, 1), (5, 1)]; if over budget: cap or GIVEUP, then a Δ answer |
| BEAM-w | w=1: SAT; w=2: SAT; w=4: SAT (UNSAT from BEAM is never certified) | π_BEAM not separable from π_DPLL on this set (same outputs); see E4 | CASES with >= 2 live partial assignments; BT = 0 |
| BACKDOOR-k | k=2,OCC: UNSAT (default); k=2,MENTION: UNSAT (default); k=2,INDEX: UNSAT (default); k=3,OCC: UNSAT (default); k=3,MENTION: UNSAT (default); k=3,INDEX: UNSAT (default) | π_BACKDOOR not separable here; see E3 | enumerates all 2^k combinations of one fixed variable set chosen up front |
| WALK-k (and SA) | P(success / k=22) = 0.18, P(success / k=110) = 0.65, P(success / k=550) = 0.89; modal failure at k=22: violates [70], LM0=True, Hamming to nearest solution = 5 | π_F from the L-dependence of false alarms; a null bounds π_F ≤ 0.12 (upper 95%, pooled) | FULL candidate, VIOL list, FLIP moves; DEC <= 1; #FLIP about the WalkSAT median of 85 |
| MIN-CONFLICTS | P(success / k=22) = 0.00, P(success / k=110) = 0.16, P(success / k=550) = 0.52 | π_F from the L-dependence of false alarms; a null bounds π_F ≤ 0.12 (upper 95%, pooled) | as WALK-k, but moves pick a conflicted variable and its min-conflict value |
| C-UC (greedy + unit rule, no backtracking) | STOP: MENTION,TRUE: UNSAT (dead end at C50); MENTION,MAJ: UNSAT (dead end at C50); MOMS,TRUE: UNSAT (dead end at C45); MOMS,MAJ: UNSAT (dead end at C61) / CONT violates: MENTION,TRUE: [12, 26, 40, 50]; MENTION,MAJ: [12, 50]; MOMS,TRUE: [12, 45]; MOMS,MAJ: [26, 61] | π_C from dead-end false UNSATs on both arms | one pass, DEC about n, BT = 0; at a dead end: 'contradiction' then UNSAT (STOP) or continue (CONT) |
| C-GREEDY | x1=0 x2=1 x3=0 x4=0 x5=1 x6=1 x7=1 x8=1 x9=0 x10=0 x11=1 x12=1 x13=0 x14=1 x15=1 x16=0 x17=0 x18=1 x19=0 x20=1 x21=1 x22=1 (violates [12, 50]) | π_C from dead-end false UNSATs on both arms | assigns in mention order, never revises, no PROP |
| POLARITY (C0 / A2) | SAT x1=0 x2=0 x3=1 x4=0 x5=1 x6=1 x7=1 x8=0 x9=1 x10=0 x11=0 x12=0 x13=1 x14=1 x15=1 x16=1 x17=0 x18=1 x19=1 x20=1 x21=1 x22=0 (violates [12, 23, 24, 26]) | π_POLARITY: each correct answer where the polarity assignment is infeasible has LR ≈ 0.05 against it | little search: counts signs, writes the majority value of each variable |
| B1 (UP-k, FLP-1) | default: UP is idle (no unit clauses); FLP-1 is idle on pure 3-CNF (DEFAULT) | π_B1: each correct answer on unit-free 3-CNF has LR ≈ 0.05 against it (UP is idle) | PROP only; stalls immediately |
| NOISY-EXACT | the exact answer with P = 0.813 (eps=1e-4) or 0.126 (eps=1e-3), W = 2072; otherwise a slip (one missed clause, or a spurious conflict) | inside π_certify; not separable from DPLL-b here | completes the search (no cap, no GIVEUP); errors show as a false VERIFY (FA3) or an unsound PROP (FA5) |
| RANDOM | uniform assignment; P(correct) = 0.0000 | π_RANDOM: each correct answer has LR ≈ nsol/2^n against it | no search |
| A (ALWAYS-SAT / DENSITY) | SAT (ALWAYS-SAT); DENSITY gives the same answer as the matched twin | π_A-CORE from cluster-random cores (valid ≈ 1/3) given on both arms | no search; refers to size or density |
| A-CORE (list the densest cluster) | UNSAT with one of the three clusters: K1 [10, 12, 13, 29, 30, 36, 39, 43, 44, 56, 69, 73] (valid here: False), K2 [1, 5, 6, 8, 23, 32, 45, 50, 61, 65, 68], K3 [7, 11, 16, 18, 26, 31, 34, 37, 40, 55, 70] (each picked with P = 1/3) | sensitivity ≈ 1/3; false alarm = its UNSAT rate on SAT arms (same as on UNSAT arms) | notices dense groups of clauses; no case analysis |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit EXACT, DPLL-b (b >= N), DPLL-b[MOMS, b=20, Δ=UNSAT]; pushes down C-UC/STOP (LR 0.017), A-CORE (LR 0.017), POLARITY / ALWAYS-SAT (LR 0.017), B1 (UP-k, FLP-1) (LR 0.017), RANDOM (LR 0.017)
- *UNSAT (false alarm)*: best fit C-UC/STOP, A-CORE, B1 (UP-k, FLP-1); pushes down EXACT (LR 0.017), DPLL-b (b >= N) (LR 0.017), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.017), WALK-k / MIN-CONFLICTS (LR 0.189), POLARITY / ALWAYS-SAT (LR 0.017), NOISY-EXACT (LR 0.017), RANDOM (LR 0.017)
- *infeasible SAT*: best fit POLARITY / ALWAYS-SAT, RANDOM; pushes down EXACT (LR 0.017), DPLL-b (b >= N) (LR 0.017), DPLL-b[MOMS, b=20, Δ=UNSAT] (LR 0.017), WALK-k / MIN-CONFLICTS (LR 0.189), C-UC/STOP (LR 0.017), A-CORE (LR 0.017), B1 (UP-k, FLP-1) (LR 0.017)

*Reference numbers:* DPLL-b nodes and work per variant: MENTION,TRUE: N=41, W=6364; MENTION,MAJ: N=24, W=3922; INDEX,TRUE: N=113, W=20646; INDEX,MAJ: N=20, W=3182; MOMS,TRUE: N=16, W=4218; MOMS,MAJ: N=10, W=2072. Every member's full output is in the JSONL `predictions` field.

---

## E6

### Violation profiles (answer library on the E2 'W low × F high' item, plus verification probes)

| Item | Cell | Ground truth | Varied |
|------|------|--------------|--------|
| E6.1 | verification probe of a WALK-k near-miss | violated [41] | the assignment under test (by source) |
| E6.2 | verification probe of a PERCEPTION answer | violated [1] | the assignment under test (by source) |

**Direction table** (how each set-level outcome moves weight; the sizes are in the likelihood-ratio table below and in each item's hypothesis block):

| Observed outcome (set level) | Moves weight toward | Moves weight away from |
|------------------------------|---------------------|------------------------|
| Wrong answers mostly LM0 with frustration LLR > 0, V falling with budget, detected on re-check | WALK-k / MIN-CONFLICTS | NOISY-EXACT, PERCEPTION, DPLL-b default, C, POLARITY |
| Violations concentrated on late variables (tail), V shrinking with budget, cap/GIVEUP traces | DPLL-b FILL default | WALK-k, NOISY-EXACT |
| Single violated clause, not LM0 beyond the base rate, detected on re-check, different across samples | NOISY-EXACT | WALK-k, PERCEPTION |
| Same clause violated across samples, missed on re-check, misquoted in the trace | PERCEPTION-NOISE | WALK-k, NOISY-EXACT |

**Likelihood-ratio table** (computed). Each row asks: if one response per item (E6.1, E6.2) matched theory *h*'s most likely outcome, how much less likely is that pattern under each competitor? Entries are log10 LR(competitor : h), with a 5% slip floor on every theory, so −1.0 means the pattern pushes that competitor's weight down 10× relative to *h*. A cell of N independent responses multiplies these by about N. The readout is the mixture posterior over π, not a verdict (D_F_search.md §2.5).

| If responses match the modal pattern of h = | Tied with h (0.0) | Weakly disfavoured (−1 < log10 LR < 0) | Pushed down ≥ 10× (log10 LR ≤ −1) |
|---------------------------------------------|-------------------|----------------------------------------|-----------------------------------|
| source = WALK-k (procedural near-miss) | source = NOISY-EXACT (transient slip) | — | source = PERCEPTION-NOISE (persistent misreading) (-1.7) |
| source = NOISY-EXACT (transient slip) | source = WALK-k (procedural near-miss) | — | source = PERCEPTION-NOISE (persistent misreading) (-1.7) |
| source = PERCEPTION-NOISE (persistent misreading) | — | — | source = WALK-k (procedural near-miss) (-1.7), source = NOISY-EXACT (transient slip) (-1.7) |

**Not distinguished by this set:** EXACT and RANDOM are not tested here (they predict no or random infeasible answers); E1/E2 cover them.

**Answer library on the E2 item 'W low × F high'.** These are the wrong answers each source produces, with the statistics E6 classifies on:

| Source | Violated clauses | V | Hamming to nearest solution | LM0 | Share of violations on first-half variables | Frustration LLR |
|--------|------------------|---|-----------------------------|-----|---------------------------------------------|-----------------|
| WALK-k (modal failure, k = n) | [41] | 1 | 5 | True | 0.0 | 1.41 |
| DPLL-b FILL default (MOMS,MAJ, b = N/2) | [1, 29, 41, 54] | 4 | 4 | False | 0.25 | 1.01 |
| C-UC/CONT (MENTION,MAJ) | [41] | 1 | 5 | True | 0.0 | 1.41 |
| NOISY-EXACT slip (clause C14 overlooked) | [14] | 1 | 3 | True | 0.0 | 0.21 |
| PERCEPTION (sign of literal 1 in C1 misread) | [1] | 1 | 2 | True | 1.0 | 1.1 |
| POLARITY | [1, 29, 41, 54] | 4 | 4 | False | 0.25 | 1.01 |

**What this shows:**

- WALK's modal failure and C-UC/CONT's output are *the same assignment* here.
- The first overlooked-clause slip coincides with the first misreading. The NE slip listed above is the first one that differs.
- So no single answer separates WALK from C, or NE from PERCEPTION. The channels that do:
  - budget dependence: *V* falls with *T* under F only;
  - the re-check (E6-VER): PERCEPTION misses its own misread clause;
  - same-clause consistency across samples;
  - the trace: FLIP vs one pass; a misquoted clause.

### E6.1: verification probe of a WALK-k near-miss

- **Question tested:** Was the original infeasible answer a procedural near-miss (detectable on re-check) or a misreading (not detectable)?
- **Controlled:** the same formula as the E2 item; fresh context, CoT-2k
- **Varied:** the assignment under test (by source)
- **Ground truth:** `{"violated": [41]}`
- **Notes:** The study probes each model with its *own* wrong answers; here the assignments come from the reference implementations.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x14. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false.

C1: (NOT x5 OR NOT x7 OR x10)
C2: (NOT x3 OR x9 OR x11)
C3: (NOT x4 OR x9 OR NOT x12)
C4: (x7 OR x11 OR x14)
C5: (x7 OR x12 OR x13)
C6: (NOT x4 OR NOT x5 OR x7)
C7: (x1 OR NOT x10 OR x12)
C8: (x5 OR x6 OR NOT x8)
C9: (x1 OR NOT x5 OR x6)
C10: (NOT x3 OR x8 OR x9)
C11: (x1 OR NOT x2 OR NOT x14)
C12: (NOT x6 OR x7 OR x11)
C13: (NOT x1 OR x5 OR NOT x14)
C14: (x8 OR NOT x9 OR NOT x10)
C15: (x7 OR x9 OR x14)
C16: (x2 OR NOT x3 OR NOT x5)
C17: (x3 OR x9 OR NOT x11)
C18: (x3 OR x9 OR NOT x12)
C19: (NOT x4 OR NOT x5 OR x12)
C20: (NOT x6 OR x9 OR NOT x11)
C21: (NOT x8 OR NOT x11 OR NOT x12)
C22: (x9 OR NOT x10 OR x12)
C23: (x6 OR x8 OR NOT x13)
C24: (x7 OR NOT x11 OR NOT x14)
C25: (NOT x3 OR NOT x10 OR NOT x12)
C26: (NOT x2 OR x6 OR x13)
C27: (NOT x1 OR x9 OR x11)
C28: (x6 OR x10 OR NOT x14)
C29: (NOT x7 OR NOT x8 OR NOT x11)
C30: (x6 OR NOT x10 OR x14)
C31: (NOT x4 OR NOT x8 OR NOT x12)
C32: (x2 OR x6 OR NOT x9)
C33: (NOT x2 OR x4 OR NOT x12)
C34: (NOT x1 OR x11 OR NOT x13)
C35: (x4 OR x5 OR x14)
C36: (x3 OR x6 OR NOT x10)
C37: (NOT x2 OR NOT x5 OR NOT x10)
C38: (NOT x2 OR x8 OR x9)
C39: (NOT x3 OR x7 OR NOT x11)
C40: (NOT x8 OR x13 OR x14)
C41: (NOT x6 OR NOT x8 OR NOT x9)
C42: (x3 OR x11 OR x13)
C43: (x4 OR x6 OR x14)
C44: (x9 OR NOT x10 OR x13)
C45: (x5 OR NOT x6 OR x11)
C46: (NOT x3 OR NOT x6 OR NOT x11)
C47: (NOT x3 OR NOT x5 OR x13)
C48: (NOT x2 OR NOT x6 OR x8)
C49: (NOT x1 OR NOT x9 OR x12)
C50: (NOT x1 OR x3 OR NOT x7)
C51: (x2 OR NOT x4 OR x5)
C52: (NOT x1 OR x2 OR x5)
C53: (x5 OR x8 OR NOT x12)
C54: (NOT x6 OR x10 OR x12)
C55: (x1 OR x2 OR x9)
C56: (x3 OR NOT x4 OR x13)
C57: (NOT x3 OR NOT x7 OR NOT x13)
C58: (NOT x3 OR x5 OR NOT x10)
C59: (NOT x2 OR NOT x5 OR NOT x12)
C60: (x1 OR NOT x3 OR NOT x10)

Here is an assignment: x1=0 x2=0 x3=0 x4=0 x5=1 x6=1 x7=1 x8=1 x9=1 x10=1 x11=0 x12=1 x13=1 x14=1

Which clauses does this assignment fail to satisfy? Check every clause. Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
{"violated": [ ... ]} (the clause numbers; an empty list if every clause is satisfied)
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT verifier | [41] | the probe's own accuracy is estimated on feasible-assignment controls | checks every clause in turn |
| WALK-k as the source | [41] (the model finds its own residual violation) | raises π_F(source) for answers whose violation is detected (LR ≈ 9 over PERCEPTION per detected probe) | the original trace contains FULL/VIOL/FLIP |
| NOISY-EXACT as the source | detects the violated clause (slips are transient) | raises π_NE(source) for detected violations that vary across samples | the original trace contains a false VERIFY |
| PERCEPTION-NOISE as the source | n/a | raises π_PERCEPTION(source) for missed violations that recur across samples (LR ≈ 9 per missed probe) | the original trace misquotes the clause |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *detects the violated clause*: best fit source = WALK-k (procedural near-miss), source = NOISY-EXACT (transient slip); pushes down source = PERCEPTION-NOISE (persistent misreading) (LR 0.136)
- *misses it*: best fit source = PERCEPTION-NOISE (persistent misreading); pushes down source = WALK-k (procedural near-miss) (LR 0.136), source = NOISY-EXACT (transient slip) (LR 0.136)

### E6.2: verification probe of a PERCEPTION answer

- **Question tested:** Was the original infeasible answer a procedural near-miss (detectable on re-check) or a misreading (not detectable)?
- **Controlled:** the same formula as the E2 item; fresh context, CoT-2k
- **Varied:** the assignment under test (by source)
- **Ground truth:** `{"violated": [1]}`
- **Notes:** The study probes each model with its *own* wrong answers; here the assignments come from the reference implementations.
- **Same clauses as E6.1**; only the framing, seed line or prefill differs.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x14. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false.

C1: (NOT x5 OR NOT x7 OR x10)
C2: (NOT x3 OR x9 OR x11)
C3: (NOT x4 OR x9 OR NOT x12)
C4: (x7 OR x11 OR x14)
C5: (x7 OR x12 OR x13)
C6: (NOT x4 OR NOT x5 OR x7)
C7: (x1 OR NOT x10 OR x12)
C8: (x5 OR x6 OR NOT x8)
C9: (x1 OR NOT x5 OR x6)
C10: (NOT x3 OR x8 OR x9)
C11: (x1 OR NOT x2 OR NOT x14)
C12: (NOT x6 OR x7 OR x11)
C13: (NOT x1 OR x5 OR NOT x14)
C14: (x8 OR NOT x9 OR NOT x10)
C15: (x7 OR x9 OR x14)
C16: (x2 OR NOT x3 OR NOT x5)
C17: (x3 OR x9 OR NOT x11)
C18: (x3 OR x9 OR NOT x12)
C19: (NOT x4 OR NOT x5 OR x12)
C20: (NOT x6 OR x9 OR NOT x11)
C21: (NOT x8 OR NOT x11 OR NOT x12)
C22: (x9 OR NOT x10 OR x12)
C23: (x6 OR x8 OR NOT x13)
C24: (x7 OR NOT x11 OR NOT x14)
C25: (NOT x3 OR NOT x10 OR NOT x12)
C26: (NOT x2 OR x6 OR x13)
C27: (NOT x1 OR x9 OR x11)
C28: (x6 OR x10 OR NOT x14)
C29: (NOT x7 OR NOT x8 OR NOT x11)
C30: (x6 OR NOT x10 OR x14)
C31: (NOT x4 OR NOT x8 OR NOT x12)
C32: (x2 OR x6 OR NOT x9)
C33: (NOT x2 OR x4 OR NOT x12)
C34: (NOT x1 OR x11 OR NOT x13)
C35: (x4 OR x5 OR x14)
C36: (x3 OR x6 OR NOT x10)
C37: (NOT x2 OR NOT x5 OR NOT x10)
C38: (NOT x2 OR x8 OR x9)
C39: (NOT x3 OR x7 OR NOT x11)
C40: (NOT x8 OR x13 OR x14)
C41: (NOT x6 OR NOT x8 OR NOT x9)
C42: (x3 OR x11 OR x13)
C43: (x4 OR x6 OR x14)
C44: (x9 OR NOT x10 OR x13)
C45: (x5 OR NOT x6 OR x11)
C46: (NOT x3 OR NOT x6 OR NOT x11)
C47: (NOT x3 OR NOT x5 OR x13)
C48: (NOT x2 OR NOT x6 OR x8)
C49: (NOT x1 OR NOT x9 OR x12)
C50: (NOT x1 OR x3 OR NOT x7)
C51: (x2 OR NOT x4 OR x5)
C52: (NOT x1 OR x2 OR x5)
C53: (x5 OR x8 OR NOT x12)
C54: (NOT x6 OR x10 OR x12)
C55: (x1 OR x2 OR x9)
C56: (x3 OR NOT x4 OR x13)
C57: (NOT x3 OR NOT x7 OR NOT x13)
C58: (NOT x3 OR x5 OR NOT x10)
C59: (NOT x2 OR NOT x5 OR NOT x12)
C60: (x1 OR NOT x3 OR NOT x10)

Here is an assignment: x1=0 x2=0 x3=0 x4=0 x5=1 x6=1 x7=1 x8=0 x9=1 x10=0 x11=1 x12=1 x13=1 x14=1

Which clauses does this assignment fail to satisfy? Check every clause. Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
{"violated": [ ... ]} (the clause numbers; an empty list if every clause is satisfied)
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| EXACT verifier | [1] | the probe's own accuracy is estimated on feasible-assignment controls | checks every clause in turn |
| WALK-k as the source | n/a | raises π_F(source) for answers whose violation is detected (LR ≈ 9 over PERCEPTION per detected probe) | the original trace contains FULL/VIOL/FLIP |
| NOISY-EXACT as the source | detects the violated clause (slips are transient) | raises π_NE(source) for detected violations that vary across samples | the original trace contains a false VERIFY |
| PERCEPTION-NOISE as the source | misses C1 (reads it the same wrong way): reports [] | raises π_PERCEPTION(source) for missed violations that recur across samples (LR ≈ 9 per missed probe) | the original trace misquotes the clause |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *detects the violated clause*: best fit source = WALK-k (procedural near-miss), source = NOISY-EXACT (transient slip); pushes down source = PERCEPTION-NOISE (persistent misreading) (LR 0.136)
- *misses it*: best fit source = PERCEPTION-NOISE (persistent misreading); pushes down source = WALK-k (procedural near-miss) (LR 0.136), source = NOISY-EXACT (transient slip) (LR 0.136)

---

## E7-SAT

### Seeded candidates (SAT)

| Item | Cell | Ground truth | Varied |
|------|------|--------------|--------|
| E7-SAT.1 | SAT seed S0 | SAT (2 solutions) | seed condition S0 |
| E7-SAT.2 | SAT seed S2 | SAT (2 solutions) | seed condition S2 |
| E7-SAT.3 | SAT seed S4 | SAT (2 solutions) | seed condition S4 |
| E7-SAT.4 | SAT seed S8 | SAT (2 solutions) | seed condition S8 |
| E7-SAT.5 | SAT seed SD | SAT (2 solutions) | seed condition SD |
| E7-SAT.6 | SAT seed SR | SAT (2 solutions) | seed condition SR |

**Direction table** (how each set-level outcome moves weight; the sizes are in the likelihood-ratio table below and in each item's hypothesis block):

| Observed outcome (set level) | Moves weight toward | Moves weight away from |
|------------------------------|---------------------|------------------------|
| Success ordered S2 > S4 > S8 > S0 ≈ SR, and SD errors stick to the decoy | WALK-k / MIN-CONFLICTS | DPLL-b, NOISY-EXACT, EXACT, C (dead ends are not LM0) |
| No seed effect, and Δ-type errors | DPLL-b, NOISY-EXACT | WALK-k, ECHO |
| The infeasible seed echoed verbatim | ECHO | WALK-k (would repair), DPLL-b, EXACT |
| Follows the seed to a dead end (not LM0) | seeded C-UC | WALK-k |

**Likelihood-ratio table** (computed). Each row asks: if one response per item (E7-SAT.1, E7-SAT.2, E7-SAT.3, E7-SAT.4, E7-SAT.5, E7-SAT.6) matched theory *h*'s most likely outcome, how much less likely is that pattern under each competitor? Entries are log10 LR(competitor : h), with a 5% slip floor on every theory, so −1.0 means the pattern pushes that competitor's weight down 10× relative to *h*. A cell of N independent responses multiplies these by about N. The readout is the mixture posterior over π, not a verdict (D_F_search.md §2.5).

| If responses match the modal pattern of h = | Tied with h (0.0) | Weakly disfavoured (−1 < log10 LR < 0) | Pushed down ≥ 10× (log10 LR ≤ −1) |
|---------------------------------------------|-------------------|----------------------------------------|-----------------------------------|
| WALK-k | DPLL-b, NOISY-EXACT, EXACT | — | MIN-CONFLICTS (-2.9), C-UC (seeded) (-5.3), ECHO (-9.1), RANDOM (-10.4) |
| MIN-CONFLICTS | — | — | WALK-k (-2.0), DPLL-b (-2.7), NOISY-EXACT (-2.7), EXACT (-2.7), C-UC (seeded) (-4.5), ECHO (-6.5), RANDOM (-7.9) |
| DPLL-b | WALK-k, NOISY-EXACT, EXACT | — | MIN-CONFLICTS (-2.9), C-UC (seeded) (-5.3), ECHO (-9.1), RANDOM (-10.4) |
| NOISY-EXACT | WALK-k, DPLL-b, EXACT | — | MIN-CONFLICTS (-2.9), C-UC (seeded) (-5.3), ECHO (-9.1), RANDOM (-10.4) |
| EXACT | WALK-k, DPLL-b, NOISY-EXACT | — | MIN-CONFLICTS (-2.9), C-UC (seeded) (-5.3), ECHO (-9.1), RANDOM (-10.4) |
| C-UC (seeded) | — | — | WALK-k (-4.8), MIN-CONFLICTS (-3.3), DPLL-b (-5.3), NOISY-EXACT (-5.3), EXACT (-5.3), ECHO (-9.1), RANDOM (-5.1) |
| ECHO | — | — | WALK-k (-8.3), MIN-CONFLICTS (-6.1), DPLL-b (-8.5), NOISY-EXACT (-8.5), EXACT (-8.5), C-UC (seeded) (-8.5), RANDOM (-10.1) |
| RANDOM | — | — | WALK-k (-9.6), MIN-CONFLICTS (-4.1), DPLL-b (-10.4), NOISY-EXACT (-10.4), EXACT (-10.4), C-UC (seeded) (-5.1), ECHO (-9.1) |

**Not distinguished by this set:** At this dev size (n = 12), noisy WALK-k escapes even the decoy (P(success) = 0.98 at k = 5n from SD), so on modal patterns WALK-k ties with DPLL-b, NOISY-EXACT and EXACT; MIN-CONFLICTS does not escape (P = 0 from SD) and is pushed apart (log10 LR ≤ −2.0). The study's SD acceptance rule (median flips from the decoy ≥ 10× S8's) is what makes WALK-k separable; no n = 12 decoy met it, so E7-SAT needs n ≥ 20 for WALK-k. DPLL-b vs NOISY-EXACT: both seed-blind; see E1/E2.

### E7-SAT.1: SAT seed S0

- **Question tested:** Does the answer depend on the starting candidate the way local search predicts?
- **Controlled:** the same formula, template and position of the seed line in all six prompts; seed-line length (S0 has a placeholder line)
- **Varied:** seed condition S0
- **Ground truth:** `{"answer": "SAT", "n_solutions": 2, "solutions": ["x1=1 x2=1 x3=0 x4=1 x5=0 x6=0 x7=1 x8=0 x9=1 x10=1 x11=1 x12=0", "x1=1 x2=1 x3=0 x4=1 x5=0 x6=0 x7=0 x8=0 x9=1 x10=1 x11=1 x12=1"]}`

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x12. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x5 OR NOT x6 OR NOT x11)
C2: (x2 OR NOT x3 OR x8)
C3: (x5 OR NOT x6 OR x10)
C4: (NOT x3 OR x5 OR x11)
C5: (x2 OR NOT x7 OR NOT x9)
C6: (NOT x2 OR NOT x8 OR x10)
C7: (x1 OR x6 OR x8)
C8: (NOT x4 OR NOT x6 OR NOT x9)
C9: (NOT x1 OR x10 OR NOT x11)
C10: (x4 OR NOT x5 OR x9)
C11: (NOT x2 OR x9 OR NOT x12)
C12: (x2 OR x4 OR NOT x8)
C13: (x7 OR NOT x8 OR x10)
C14: (NOT x4 OR NOT x5 OR x9)
C15: (NOT x6 OR x8 OR x11)
C16: (x4 OR NOT x9 OR NOT x10)
C17: (x4 OR NOT x7 OR x11)
C18: (NOT x4 OR NOT x5 OR NOT x6)
C19: (x8 OR NOT x10 OR x11)
C20: (x3 OR x7 OR x11)
C21: (NOT x5 OR NOT x6 OR NOT x8)
C22: (NOT x3 OR x6 OR x8)
C23: (NOT x2 OR NOT x5 OR x12)
C24: (x1 OR x3 OR x5)
C25: (NOT x3 OR NOT x6 OR NOT x12)
C26: (NOT x3 OR NOT x8 OR NOT x11)
C27: (x1 OR x7 OR x11)
C28: (x2 OR NOT x5 OR NOT x6)
C29: (NOT x1 OR x2 OR x9)
C30: (NOT x5 OR x8 OR NOT x10)
C31: (NOT x2 OR NOT x6 OR NOT x8)
C32: (NOT x7 OR x11 OR NOT x12)
C33: (x1 OR x4 OR x10)
C34: (NOT x3 OR x9 OR NOT x10)
C35: (NOT x3 OR x9 OR x10)
C36: (x2 OR x9 OR NOT x12)
C37: (x5 OR NOT x7 OR NOT x12)
C38: (x1 OR x7 OR NOT x8)
C39: (x1 OR x11 OR NOT x12)
C40: (x2 OR NOT x9 OR NOT x10)
C41: (NOT x4 OR x7 OR x12)
C42: (NOT x5 OR x6 OR x11)
C43: (NOT x2 OR x4 OR NOT x6)
C44: (x2 OR x8 OR NOT x9)
C45: (x1 OR x10 OR NOT x11)
C46: (x9 OR NOT x11 OR NOT x12)
C47: (NOT x1 OR x7 OR NOT x8)
C48: (NOT x2 OR x5 OR x10)
C49: (NOT x4 OR NOT x7 OR x9)
C50: (x6 OR NOT x8 OR NOT x9)
C51: (NOT x1 OR x9 OR NOT x10)

No candidate assignment is available.

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| WALK-k / MIN-CONFLICTS | P(success, k=5n) = 0.99 | π_F from the seed-distance slope and decoy-proximal errors (null rate ≈ 0, so each decoy-proximal error has LR > 10 for F over D); power 0.8 to detect π_F ≥ 0.15; a null bounds π_F ≤ 0.08 (upper 95%) | random/polarity init, FLIPs |
| DPLL-b | SAT regardless of seed (MOMS,MAJ N = 4); with seed phases N = - | π_seed-blind (DPLL-b + NE + EXACT) = 1 − π_F − π_ECHO − π_C(seeded) | seed ignored or checked once, then DEC/PROP/BT from scratch |
| C-UC | ignores the seed, or follows it until a dead end | π_C(seeded) from seed-proximal dead ends (not LM0) | one pass, BT = 0 |
| ECHO | n/a | π_ECHO = the verbatim-echo rate of infeasible seeds | little or no checking |
| NOISY-EXACT | as DPLL-b | inside π_seed-blind | complete search |
| EXACT | SAT with a solution | inside π_seed-blind; ceiling accuracy | — |
| RANDOM | P(correct) = 0.0005 | π_RANDOM ≈ 0 expected | — |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit DPLL-b, NOISY-EXACT, EXACT, C-UC (seeded); pushes down RANDOM (LR 0.026)
- *error*: best fit RANDOM; pushes down WALK-k (LR 0.035), DPLL-b (LR 0.026), NOISY-EXACT (LR 0.026), EXACT (LR 0.026), C-UC (seeded) (LR 0.026)

### E7-SAT.2: SAT seed S2

- **Question tested:** Does the answer depend on the starting candidate the way local search predicts?
- **Controlled:** the same formula, template and position of the seed line in all six prompts; seed-line length (S0 has a placeholder line)
- **Varied:** seed condition S2
- **Ground truth:** `{"answer": "SAT", "n_solutions": 2, "solutions": ["x1=1 x2=1 x3=0 x4=1 x5=0 x6=0 x7=1 x8=0 x9=1 x10=1 x11=1 x12=0", "x1=1 x2=1 x3=0 x4=1 x5=0 x6=0 x7=0 x8=0 x9=1 x10=1 x11=1 x12=1"]}`
- **Same clauses as E7-SAT.1**; only the framing, seed line or prefill differs.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x12. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x5 OR NOT x6 OR NOT x11)
C2: (x2 OR NOT x3 OR x8)
C3: (x5 OR NOT x6 OR x10)
C4: (NOT x3 OR x5 OR x11)
C5: (x2 OR NOT x7 OR NOT x9)
C6: (NOT x2 OR NOT x8 OR x10)
C7: (x1 OR x6 OR x8)
C8: (NOT x4 OR NOT x6 OR NOT x9)
C9: (NOT x1 OR x10 OR NOT x11)
C10: (x4 OR NOT x5 OR x9)
C11: (NOT x2 OR x9 OR NOT x12)
C12: (x2 OR x4 OR NOT x8)
C13: (x7 OR NOT x8 OR x10)
C14: (NOT x4 OR NOT x5 OR x9)
C15: (NOT x6 OR x8 OR x11)
C16: (x4 OR NOT x9 OR NOT x10)
C17: (x4 OR NOT x7 OR x11)
C18: (NOT x4 OR NOT x5 OR NOT x6)
C19: (x8 OR NOT x10 OR x11)
C20: (x3 OR x7 OR x11)
C21: (NOT x5 OR NOT x6 OR NOT x8)
C22: (NOT x3 OR x6 OR x8)
C23: (NOT x2 OR NOT x5 OR x12)
C24: (x1 OR x3 OR x5)
C25: (NOT x3 OR NOT x6 OR NOT x12)
C26: (NOT x3 OR NOT x8 OR NOT x11)
C27: (x1 OR x7 OR x11)
C28: (x2 OR NOT x5 OR NOT x6)
C29: (NOT x1 OR x2 OR x9)
C30: (NOT x5 OR x8 OR NOT x10)
C31: (NOT x2 OR NOT x6 OR NOT x8)
C32: (NOT x7 OR x11 OR NOT x12)
C33: (x1 OR x4 OR x10)
C34: (NOT x3 OR x9 OR NOT x10)
C35: (NOT x3 OR x9 OR x10)
C36: (x2 OR x9 OR NOT x12)
C37: (x5 OR NOT x7 OR NOT x12)
C38: (x1 OR x7 OR NOT x8)
C39: (x1 OR x11 OR NOT x12)
C40: (x2 OR NOT x9 OR NOT x10)
C41: (NOT x4 OR x7 OR x12)
C42: (NOT x5 OR x6 OR x11)
C43: (NOT x2 OR x4 OR NOT x6)
C44: (x2 OR x8 OR NOT x9)
C45: (x1 OR x10 OR NOT x11)
C46: (x9 OR NOT x11 OR NOT x12)
C47: (NOT x1 OR x7 OR NOT x8)
C48: (NOT x2 OR x5 OR x10)
C49: (NOT x4 OR NOT x7 OR x9)
C50: (x6 OR NOT x8 OR NOT x9)
C51: (NOT x1 OR x9 OR NOT x10)

A candidate assignment (it may be wrong; you may use it or ignore it): x1=0 x2=1 x3=0 x4=0 x5=0 x6=0 x7=1 x8=0 x9=1 x10=1 x11=1 x12=0

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| WALK-k / MIN-CONFLICTS | P(success, k=5n) = 1.0; failures near the seed: 0.0 | π_F from the seed-distance slope and decoy-proximal errors (null rate ≈ 0, so each decoy-proximal error has LR > 10 for F over D); power 0.8 to detect π_F ≥ 0.15; a null bounds π_F ≤ 0.08 (upper 95%) | SEEDREF then VIOL then FLIPs; #FLIP ≈ Hamming(seed, answer) |
| DPLL-b | SAT regardless of seed (MOMS,MAJ N = 4); with seed phases N = 4 | π_seed-blind (DPLL-b + NE + EXACT) = 1 − π_F − π_ECHO − π_C(seeded) | seed ignored or checked once, then DEC/PROP/BT from scratch |
| C-UC | ignores the seed, or follows it until a dead end (seeded: feasible = True) | π_C(seeded) from seed-proximal dead ends (not LM0) | one pass, BT = 0 |
| ECHO | the seed verbatim | π_ECHO = the verbatim-echo rate of infeasible seeds | little or no checking |
| NOISY-EXACT | as DPLL-b | inside π_seed-blind | complete search |
| EXACT | SAT with a solution | inside π_seed-blind; ceiling accuracy | — |
| RANDOM | P(correct) = 0.0005 | π_RANDOM ≈ 0 expected | — |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit WALK-k, DPLL-b, NOISY-EXACT, EXACT, C-UC (seeded); pushes down ECHO (LR 0.017), RANDOM (LR 0.017)
- *error within Hamming 2 of the seed*: best fit ECHO; pushes down WALK-k (LR 0.017), MIN-CONFLICTS (LR 0.134), DPLL-b (LR 0.017), NOISY-EXACT (LR 0.017), EXACT (LR 0.017), C-UC (seeded) (LR 0.017), RANDOM (LR 0.017)
- *other error*: best fit RANDOM; pushes down WALK-k (LR 0.017), MIN-CONFLICTS (LR 0.166), DPLL-b (LR 0.017), NOISY-EXACT (LR 0.017), EXACT (LR 0.017), C-UC (seeded) (LR 0.017), ECHO (LR 0.017)

### E7-SAT.3: SAT seed S4

- **Question tested:** Does the answer depend on the starting candidate the way local search predicts?
- **Controlled:** the same formula, template and position of the seed line in all six prompts; seed-line length (S0 has a placeholder line)
- **Varied:** seed condition S4
- **Ground truth:** `{"answer": "SAT", "n_solutions": 2, "solutions": ["x1=1 x2=1 x3=0 x4=1 x5=0 x6=0 x7=1 x8=0 x9=1 x10=1 x11=1 x12=0", "x1=1 x2=1 x3=0 x4=1 x5=0 x6=0 x7=0 x8=0 x9=1 x10=1 x11=1 x12=1"]}`
- **Same clauses as E7-SAT.1**; only the framing, seed line or prefill differs.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x12. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x5 OR NOT x6 OR NOT x11)
C2: (x2 OR NOT x3 OR x8)
C3: (x5 OR NOT x6 OR x10)
C4: (NOT x3 OR x5 OR x11)
C5: (x2 OR NOT x7 OR NOT x9)
C6: (NOT x2 OR NOT x8 OR x10)
C7: (x1 OR x6 OR x8)
C8: (NOT x4 OR NOT x6 OR NOT x9)
C9: (NOT x1 OR x10 OR NOT x11)
C10: (x4 OR NOT x5 OR x9)
C11: (NOT x2 OR x9 OR NOT x12)
C12: (x2 OR x4 OR NOT x8)
C13: (x7 OR NOT x8 OR x10)
C14: (NOT x4 OR NOT x5 OR x9)
C15: (NOT x6 OR x8 OR x11)
C16: (x4 OR NOT x9 OR NOT x10)
C17: (x4 OR NOT x7 OR x11)
C18: (NOT x4 OR NOT x5 OR NOT x6)
C19: (x8 OR NOT x10 OR x11)
C20: (x3 OR x7 OR x11)
C21: (NOT x5 OR NOT x6 OR NOT x8)
C22: (NOT x3 OR x6 OR x8)
C23: (NOT x2 OR NOT x5 OR x12)
C24: (x1 OR x3 OR x5)
C25: (NOT x3 OR NOT x6 OR NOT x12)
C26: (NOT x3 OR NOT x8 OR NOT x11)
C27: (x1 OR x7 OR x11)
C28: (x2 OR NOT x5 OR NOT x6)
C29: (NOT x1 OR x2 OR x9)
C30: (NOT x5 OR x8 OR NOT x10)
C31: (NOT x2 OR NOT x6 OR NOT x8)
C32: (NOT x7 OR x11 OR NOT x12)
C33: (x1 OR x4 OR x10)
C34: (NOT x3 OR x9 OR NOT x10)
C35: (NOT x3 OR x9 OR x10)
C36: (x2 OR x9 OR NOT x12)
C37: (x5 OR NOT x7 OR NOT x12)
C38: (x1 OR x7 OR NOT x8)
C39: (x1 OR x11 OR NOT x12)
C40: (x2 OR NOT x9 OR NOT x10)
C41: (NOT x4 OR x7 OR x12)
C42: (NOT x5 OR x6 OR x11)
C43: (NOT x2 OR x4 OR NOT x6)
C44: (x2 OR x8 OR NOT x9)
C45: (x1 OR x10 OR NOT x11)
C46: (x9 OR NOT x11 OR NOT x12)
C47: (NOT x1 OR x7 OR NOT x8)
C48: (NOT x2 OR x5 OR x10)
C49: (NOT x4 OR NOT x7 OR x9)
C50: (x6 OR NOT x8 OR NOT x9)
C51: (NOT x1 OR x9 OR NOT x10)

A candidate assignment (it may be wrong; you may use it or ignore it): x1=1 x2=1 x3=0 x4=0 x5=1 x6=1 x7=1 x8=1 x9=1 x10=1 x11=1 x12=0

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| WALK-k / MIN-CONFLICTS | P(success, k=5n) = 0.995; failures near the seed: 0.0 | π_F from the seed-distance slope and decoy-proximal errors (null rate ≈ 0, so each decoy-proximal error has LR > 10 for F over D); power 0.8 to detect π_F ≥ 0.15; a null bounds π_F ≤ 0.08 (upper 95%) | SEEDREF then VIOL then FLIPs; #FLIP ≈ Hamming(seed, answer) |
| DPLL-b | SAT regardless of seed (MOMS,MAJ N = 4); with seed phases N = 10 | π_seed-blind (DPLL-b + NE + EXACT) = 1 − π_F − π_ECHO − π_C(seeded) | seed ignored or checked once, then DEC/PROP/BT from scratch |
| C-UC | ignores the seed, or follows it until a dead end (seeded: feasible = False) | π_C(seeded) from seed-proximal dead ends (not LM0) | one pass, BT = 0 |
| ECHO | the seed verbatim | π_ECHO = the verbatim-echo rate of infeasible seeds | little or no checking |
| NOISY-EXACT | as DPLL-b | inside π_seed-blind | complete search |
| EXACT | SAT with a solution | inside π_seed-blind; ceiling accuracy | — |
| RANDOM | P(correct) = 0.0005 | π_RANDOM ≈ 0 expected | — |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit DPLL-b, NOISY-EXACT, EXACT; pushes down C-UC (seeded) (LR 0.017), ECHO (LR 0.017), RANDOM (LR 0.017)
- *error within Hamming 2 of the seed*: best fit ECHO; pushes down WALK-k (LR 0.017), MIN-CONFLICTS (LR 0.017), DPLL-b (LR 0.017), NOISY-EXACT (LR 0.017), EXACT (LR 0.017), C-UC (seeded) (LR 0.017), RANDOM (LR 0.017)
- *other error*: best fit C-UC (seeded), RANDOM; pushes down WALK-k (LR 0.022), DPLL-b (LR 0.017), NOISY-EXACT (LR 0.017), EXACT (LR 0.017), ECHO (LR 0.017)

### E7-SAT.4: SAT seed S8

- **Question tested:** Does the answer depend on the starting candidate the way local search predicts?
- **Controlled:** the same formula, template and position of the seed line in all six prompts; seed-line length (S0 has a placeholder line)
- **Varied:** seed condition S8
- **Ground truth:** `{"answer": "SAT", "n_solutions": 2, "solutions": ["x1=1 x2=1 x3=0 x4=1 x5=0 x6=0 x7=1 x8=0 x9=1 x10=1 x11=1 x12=0", "x1=1 x2=1 x3=0 x4=1 x5=0 x6=0 x7=0 x8=0 x9=1 x10=1 x11=1 x12=1"]}`
- **Same clauses as E7-SAT.1**; only the framing, seed line or prefill differs.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x12. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x5 OR NOT x6 OR NOT x11)
C2: (x2 OR NOT x3 OR x8)
C3: (x5 OR NOT x6 OR x10)
C4: (NOT x3 OR x5 OR x11)
C5: (x2 OR NOT x7 OR NOT x9)
C6: (NOT x2 OR NOT x8 OR x10)
C7: (x1 OR x6 OR x8)
C8: (NOT x4 OR NOT x6 OR NOT x9)
C9: (NOT x1 OR x10 OR NOT x11)
C10: (x4 OR NOT x5 OR x9)
C11: (NOT x2 OR x9 OR NOT x12)
C12: (x2 OR x4 OR NOT x8)
C13: (x7 OR NOT x8 OR x10)
C14: (NOT x4 OR NOT x5 OR x9)
C15: (NOT x6 OR x8 OR x11)
C16: (x4 OR NOT x9 OR NOT x10)
C17: (x4 OR NOT x7 OR x11)
C18: (NOT x4 OR NOT x5 OR NOT x6)
C19: (x8 OR NOT x10 OR x11)
C20: (x3 OR x7 OR x11)
C21: (NOT x5 OR NOT x6 OR NOT x8)
C22: (NOT x3 OR x6 OR x8)
C23: (NOT x2 OR NOT x5 OR x12)
C24: (x1 OR x3 OR x5)
C25: (NOT x3 OR NOT x6 OR NOT x12)
C26: (NOT x3 OR NOT x8 OR NOT x11)
C27: (x1 OR x7 OR x11)
C28: (x2 OR NOT x5 OR NOT x6)
C29: (NOT x1 OR x2 OR x9)
C30: (NOT x5 OR x8 OR NOT x10)
C31: (NOT x2 OR NOT x6 OR NOT x8)
C32: (NOT x7 OR x11 OR NOT x12)
C33: (x1 OR x4 OR x10)
C34: (NOT x3 OR x9 OR NOT x10)
C35: (NOT x3 OR x9 OR x10)
C36: (x2 OR x9 OR NOT x12)
C37: (x5 OR NOT x7 OR NOT x12)
C38: (x1 OR x7 OR NOT x8)
C39: (x1 OR x11 OR NOT x12)
C40: (x2 OR NOT x9 OR NOT x10)
C41: (NOT x4 OR x7 OR x12)
C42: (NOT x5 OR x6 OR x11)
C43: (NOT x2 OR x4 OR NOT x6)
C44: (x2 OR x8 OR NOT x9)
C45: (x1 OR x10 OR NOT x11)
C46: (x9 OR NOT x11 OR NOT x12)
C47: (NOT x1 OR x7 OR NOT x8)
C48: (NOT x2 OR x5 OR x10)
C49: (NOT x4 OR NOT x7 OR x9)
C50: (x6 OR NOT x8 OR NOT x9)
C51: (NOT x1 OR x9 OR NOT x10)

A candidate assignment (it may be wrong; you may use it or ignore it): x1=0 x2=1 x3=0 x4=0 x5=1 x6=1 x7=0 x8=1 x9=0 x10=1 x11=0 x12=0

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| WALK-k / MIN-CONFLICTS | P(success, k=5n) = 0.97; failures near the seed: 0.0 | π_F from the seed-distance slope and decoy-proximal errors (null rate ≈ 0, so each decoy-proximal error has LR > 10 for F over D); power 0.8 to detect π_F ≥ 0.15; a null bounds π_F ≤ 0.08 (upper 95%) | SEEDREF then VIOL then FLIPs; #FLIP ≈ Hamming(seed, answer) |
| DPLL-b | SAT regardless of seed (MOMS,MAJ N = 4); with seed phases N = 11 | π_seed-blind (DPLL-b + NE + EXACT) = 1 − π_F − π_ECHO − π_C(seeded) | seed ignored or checked once, then DEC/PROP/BT from scratch |
| C-UC | ignores the seed, or follows it until a dead end (seeded: feasible = False) | π_C(seeded) from seed-proximal dead ends (not LM0) | one pass, BT = 0 |
| ECHO | the seed verbatim | π_ECHO = the verbatim-echo rate of infeasible seeds | little or no checking |
| NOISY-EXACT | as DPLL-b | inside π_seed-blind | complete search |
| EXACT | SAT with a solution | inside π_seed-blind; ceiling accuracy | — |
| RANDOM | P(correct) = 0.0005 | π_RANDOM ≈ 0 expected | — |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit DPLL-b, NOISY-EXACT, EXACT; pushes down C-UC (seeded) (LR 0.017), ECHO (LR 0.017), RANDOM (LR 0.017)
- *error within Hamming 2 of the seed*: best fit ECHO; pushes down WALK-k (LR 0.017), MIN-CONFLICTS (LR 0.017), DPLL-b (LR 0.017), NOISY-EXACT (LR 0.017), EXACT (LR 0.017), C-UC (seeded) (LR 0.017), RANDOM (LR 0.017)
- *other error*: best fit C-UC (seeded), RANDOM; pushes down WALK-k (LR 0.047), DPLL-b (LR 0.017), NOISY-EXACT (LR 0.017), EXACT (LR 0.017), ECHO (LR 0.017)

### E7-SAT.5: SAT seed SD

- **Question tested:** Does the answer depend on the starting candidate the way local search predicts?
- **Controlled:** the same formula, template and position of the seed line in all six prompts; seed-line length (S0 has a placeholder line)
- **Varied:** seed condition SD
- **Ground truth:** `{"answer": "SAT", "n_solutions": 2, "solutions": ["x1=1 x2=1 x3=0 x4=1 x5=0 x6=0 x7=1 x8=0 x9=1 x10=1 x11=1 x12=0", "x1=1 x2=1 x3=0 x4=1 x5=0 x6=0 x7=0 x8=0 x9=1 x10=1 x11=1 x12=1"]}`
- **Same clauses as E7-SAT.1**; only the framing, seed line or prefill differs.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x12. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x5 OR NOT x6 OR NOT x11)
C2: (x2 OR NOT x3 OR x8)
C3: (x5 OR NOT x6 OR x10)
C4: (NOT x3 OR x5 OR x11)
C5: (x2 OR NOT x7 OR NOT x9)
C6: (NOT x2 OR NOT x8 OR x10)
C7: (x1 OR x6 OR x8)
C8: (NOT x4 OR NOT x6 OR NOT x9)
C9: (NOT x1 OR x10 OR NOT x11)
C10: (x4 OR NOT x5 OR x9)
C11: (NOT x2 OR x9 OR NOT x12)
C12: (x2 OR x4 OR NOT x8)
C13: (x7 OR NOT x8 OR x10)
C14: (NOT x4 OR NOT x5 OR x9)
C15: (NOT x6 OR x8 OR x11)
C16: (x4 OR NOT x9 OR NOT x10)
C17: (x4 OR NOT x7 OR x11)
C18: (NOT x4 OR NOT x5 OR NOT x6)
C19: (x8 OR NOT x10 OR x11)
C20: (x3 OR x7 OR x11)
C21: (NOT x5 OR NOT x6 OR NOT x8)
C22: (NOT x3 OR x6 OR x8)
C23: (NOT x2 OR NOT x5 OR x12)
C24: (x1 OR x3 OR x5)
C25: (NOT x3 OR NOT x6 OR NOT x12)
C26: (NOT x3 OR NOT x8 OR NOT x11)
C27: (x1 OR x7 OR x11)
C28: (x2 OR NOT x5 OR NOT x6)
C29: (NOT x1 OR x2 OR x9)
C30: (NOT x5 OR x8 OR NOT x10)
C31: (NOT x2 OR NOT x6 OR NOT x8)
C32: (NOT x7 OR x11 OR NOT x12)
C33: (x1 OR x4 OR x10)
C34: (NOT x3 OR x9 OR NOT x10)
C35: (NOT x3 OR x9 OR x10)
C36: (x2 OR x9 OR NOT x12)
C37: (x5 OR NOT x7 OR NOT x12)
C38: (x1 OR x7 OR NOT x8)
C39: (x1 OR x11 OR NOT x12)
C40: (x2 OR NOT x9 OR NOT x10)
C41: (NOT x4 OR x7 OR x12)
C42: (NOT x5 OR x6 OR x11)
C43: (NOT x2 OR x4 OR NOT x6)
C44: (x2 OR x8 OR NOT x9)
C45: (x1 OR x10 OR NOT x11)
C46: (x9 OR NOT x11 OR NOT x12)
C47: (NOT x1 OR x7 OR NOT x8)
C48: (NOT x2 OR x5 OR x10)
C49: (NOT x4 OR NOT x7 OR x9)
C50: (x6 OR NOT x8 OR NOT x9)
C51: (NOT x1 OR x9 OR NOT x10)

A candidate assignment (it may be wrong; you may use it or ignore it): x1=0 x2=1 x3=0 x4=0 x5=0 x6=0 x7=1 x8=1 x9=0 x10=1 x11=1 x12=0

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| WALK-k / MIN-CONFLICTS | P(success, k=5n) = 0.98; failures near the seed: 0.75 | π_F from the seed-distance slope and decoy-proximal errors (null rate ≈ 0, so each decoy-proximal error has LR > 10 for F over D); power 0.8 to detect π_F ≥ 0.15; a null bounds π_F ≤ 0.08 (upper 95%) | SEEDREF then VIOL then FLIPs; #FLIP ≈ Hamming(seed, answer) |
| DPLL-b | SAT regardless of seed (MOMS,MAJ N = 4); with seed phases N = 9 | π_seed-blind (DPLL-b + NE + EXACT) = 1 − π_F − π_ECHO − π_C(seeded) | seed ignored or checked once, then DEC/PROP/BT from scratch |
| C-UC | ignores the seed, or follows it until a dead end (seeded: feasible = True) | π_C(seeded) from seed-proximal dead ends (not LM0) | one pass, BT = 0 |
| ECHO | the seed verbatim | π_ECHO = the verbatim-echo rate of infeasible seeds | little or no checking |
| NOISY-EXACT | as DPLL-b | inside π_seed-blind | complete search |
| EXACT | SAT with a solution | inside π_seed-blind; ceiling accuracy | — |
| RANDOM | P(correct) = 0.0005 | π_RANDOM ≈ 0 expected | — |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit DPLL-b, NOISY-EXACT, EXACT, C-UC (seeded); pushes down MIN-CONFLICTS (LR 0.017), ECHO (LR 0.017), RANDOM (LR 0.017)
- *error within Hamming 2 of the seed*: best fit MIN-CONFLICTS, ECHO; pushes down WALK-k (LR 0.032), DPLL-b (LR 0.017), NOISY-EXACT (LR 0.017), EXACT (LR 0.017), C-UC (seeded) (LR 0.017), RANDOM (LR 0.017)
- *other error*: best fit RANDOM; pushes down WALK-k (LR 0.022), MIN-CONFLICTS (LR 0.017), DPLL-b (LR 0.017), NOISY-EXACT (LR 0.017), EXACT (LR 0.017), C-UC (seeded) (LR 0.017), ECHO (LR 0.017)

### E7-SAT.6: SAT seed SR

- **Question tested:** Does the answer depend on the starting candidate the way local search predicts?
- **Controlled:** the same formula, template and position of the seed line in all six prompts; seed-line length (S0 has a placeholder line)
- **Varied:** seed condition SR
- **Ground truth:** `{"answer": "SAT", "n_solutions": 2, "solutions": ["x1=1 x2=1 x3=0 x4=1 x5=0 x6=0 x7=1 x8=0 x9=1 x10=1 x11=1 x12=0", "x1=1 x2=1 x3=0 x4=1 x5=0 x6=0 x7=0 x8=0 x9=1 x10=1 x11=1 x12=1"]}`
- **Same clauses as E7-SAT.1**; only the framing, seed line or prefill differs.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x12. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x5 OR NOT x6 OR NOT x11)
C2: (x2 OR NOT x3 OR x8)
C3: (x5 OR NOT x6 OR x10)
C4: (NOT x3 OR x5 OR x11)
C5: (x2 OR NOT x7 OR NOT x9)
C6: (NOT x2 OR NOT x8 OR x10)
C7: (x1 OR x6 OR x8)
C8: (NOT x4 OR NOT x6 OR NOT x9)
C9: (NOT x1 OR x10 OR NOT x11)
C10: (x4 OR NOT x5 OR x9)
C11: (NOT x2 OR x9 OR NOT x12)
C12: (x2 OR x4 OR NOT x8)
C13: (x7 OR NOT x8 OR x10)
C14: (NOT x4 OR NOT x5 OR x9)
C15: (NOT x6 OR x8 OR x11)
C16: (x4 OR NOT x9 OR NOT x10)
C17: (x4 OR NOT x7 OR x11)
C18: (NOT x4 OR NOT x5 OR NOT x6)
C19: (x8 OR NOT x10 OR x11)
C20: (x3 OR x7 OR x11)
C21: (NOT x5 OR NOT x6 OR NOT x8)
C22: (NOT x3 OR x6 OR x8)
C23: (NOT x2 OR NOT x5 OR x12)
C24: (x1 OR x3 OR x5)
C25: (NOT x3 OR NOT x6 OR NOT x12)
C26: (NOT x3 OR NOT x8 OR NOT x11)
C27: (x1 OR x7 OR x11)
C28: (x2 OR NOT x5 OR NOT x6)
C29: (NOT x1 OR x2 OR x9)
C30: (NOT x5 OR x8 OR NOT x10)
C31: (NOT x2 OR NOT x6 OR NOT x8)
C32: (NOT x7 OR x11 OR NOT x12)
C33: (x1 OR x4 OR x10)
C34: (NOT x3 OR x9 OR NOT x10)
C35: (NOT x3 OR x9 OR x10)
C36: (x2 OR x9 OR NOT x12)
C37: (x5 OR NOT x7 OR NOT x12)
C38: (x1 OR x7 OR NOT x8)
C39: (x1 OR x11 OR NOT x12)
C40: (x2 OR NOT x9 OR NOT x10)
C41: (NOT x4 OR x7 OR x12)
C42: (NOT x5 OR x6 OR x11)
C43: (NOT x2 OR x4 OR NOT x6)
C44: (x2 OR x8 OR NOT x9)
C45: (x1 OR x10 OR NOT x11)
C46: (x9 OR NOT x11 OR NOT x12)
C47: (NOT x1 OR x7 OR NOT x8)
C48: (NOT x2 OR x5 OR x10)
C49: (NOT x4 OR NOT x7 OR x9)
C50: (x6 OR NOT x8 OR NOT x9)
C51: (NOT x1 OR x9 OR NOT x10)

A candidate assignment (it may be wrong; you may use it or ignore it): x1=1 x2=1 x3=1 x4=0 x5=1 x6=0 x7=0 x8=1 x9=1 x10=1 x11=1 x12=0

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| WALK-k / MIN-CONFLICTS | P(success, k=5n) = 1.0; failures near the seed: 0.0 | π_F from the seed-distance slope and decoy-proximal errors (null rate ≈ 0, so each decoy-proximal error has LR > 10 for F over D); power 0.8 to detect π_F ≥ 0.15; a null bounds π_F ≤ 0.08 (upper 95%) | SEEDREF then VIOL then FLIPs; #FLIP ≈ Hamming(seed, answer) |
| DPLL-b | SAT regardless of seed (MOMS,MAJ N = 4); with seed phases N = 9 | π_seed-blind (DPLL-b + NE + EXACT) = 1 − π_F − π_ECHO − π_C(seeded) | seed ignored or checked once, then DEC/PROP/BT from scratch |
| C-UC | ignores the seed, or follows it until a dead end (seeded: feasible = False) | π_C(seeded) from seed-proximal dead ends (not LM0) | one pass, BT = 0 |
| ECHO | the seed verbatim | π_ECHO = the verbatim-echo rate of infeasible seeds | little or no checking |
| NOISY-EXACT | as DPLL-b | inside π_seed-blind | complete search |
| EXACT | SAT with a solution | inside π_seed-blind; ceiling accuracy | — |
| RANDOM | P(correct) = 0.0005 | π_RANDOM ≈ 0 expected | — |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *correct*: best fit WALK-k, DPLL-b, NOISY-EXACT, EXACT; pushes down C-UC (seeded) (LR 0.017), ECHO (LR 0.017), RANDOM (LR 0.017)
- *error within Hamming 2 of the seed*: best fit ECHO; pushes down WALK-k (LR 0.017), MIN-CONFLICTS (LR 0.017), DPLL-b (LR 0.017), NOISY-EXACT (LR 0.017), EXACT (LR 0.017), C-UC (seeded) (LR 0.017), RANDOM (LR 0.017)
- *other error*: best fit C-UC (seeded), RANDOM; pushes down WALK-k (LR 0.017), DPLL-b (LR 0.017), NOISY-EXACT (LR 0.017), EXACT (LR 0.017), ECHO (LR 0.017)

---

## E7-TSP

### Seeded candidates (TSP, courier framing)

| Item | Cell | Ground truth | Varied |
|------|------|--------------|--------|
| E7-TSP.1 | TSP seed S0 | tour length 134 | seed condition S0 |
| E7-TSP.2 | TSP seed S-2opt | tour length 134 | seed condition S-2opt |
| E7-TSP.3 | TSP seed S-cross | tour length 134 | seed condition S-cross |
| E7-TSP.4 | TSP seed SR | tour length 134 | seed condition SR |

**Direction table** (how each set-level outcome moves weight; the sizes are in the likelihood-ratio table below and in each item's hypothesis block):

| Observed outcome (set level) | Moves weight toward | Moves weight away from |
|------------------------------|---------------------|------------------------|
| S-2opt seed returned unchanged; S-cross seed returned as its 2-opt descent | 2OPT-k | EXACT, NN-from-0, ECHO (ECHO would also return the S-cross seed unchanged) |
| The same tour (NN) in every condition | NN-from-0 | 2OPT-k, ECHO |
| The optimum in every condition | EXACT | 2OPT-k (from S-2opt), NN-from-0 |
| Every seed echoed | ECHO | 2OPT-k (it repairs S-cross) |

**Likelihood-ratio table** (computed). Each row asks: if one response per item (E7-TSP.1, E7-TSP.2, E7-TSP.3, E7-TSP.4) matched theory *h*'s most likely outcome, how much less likely is that pattern under each competitor? Entries are log10 LR(competitor : h), with a 5% slip floor on every theory, so −1.0 means the pattern pushes that competitor's weight down 10× relative to *h*. A cell of N independent responses multiplies these by about N. The readout is the mixture posterior over π, not a verdict (D_F_search.md §2.5).

| If responses match the modal pattern of h = | Tied with h (0.0) | Weakly disfavoured (−1 < log10 LR < 0) | Pushed down ≥ 10× (log10 LR ≤ −1) |
|---------------------------------------------|-------------------|----------------------------------------|-----------------------------------|
| 2OPT-k[FIRST] | — | — | 2OPT-k[BEST] (-2.0), NN-from-0 (C) (-7.5), EXACT (-3.9), ECHO (-4.3), RANDOM (-7.5) |
| 2OPT-k[BEST] | — | — | 2OPT-k[FIRST] (-2.0), NN-from-0 (C) (-7.5), EXACT (-1.9), ECHO (-4.3), RANDOM (-7.5) |
| NN-from-0 (C) | — | — | 2OPT-k[FIRST] (-7.5), 2OPT-k[BEST] (-7.5), EXACT (-7.5), ECHO (-6.2), RANDOM (-7.5) |
| EXACT | — | — | 2OPT-k[FIRST] (-3.9), 2OPT-k[BEST] (-1.9), NN-from-0 (C) (-7.5), ECHO (-6.2), RANDOM (-7.5) |
| ECHO | — | — | 2OPT-k[FIRST] (-3.4), 2OPT-k[BEST] (-3.4), NN-from-0 (C) (-7.1), EXACT (-5.3), RANDOM (-7.0) |
| RANDOM | — | — | 2OPT-k[FIRST] (-7.5), 2OPT-k[BEST] (-7.5), NN-from-0 (C) (-7.5), EXACT (-7.5), ECHO (-6.2) |

**Not distinguished by this set:** 2OPT-k[FIRST] vs [BEST]: often the same local optimum; their tours are listed where they differ.

### E7-TSP.1: TSP seed S0

- **Question tested:** Does the route the model returns depend on the starting route, as 2-opt repair predicts?
- **Controlled:** the same distance table; seed-line position and wording
- **Varied:** seed condition S0
- **Ground truth:** `{"tour": [0, 2, 6, 3, 7, 1, 5, 4, 0], "length": 134}`
- **Notes:** Distances are given as a table, so no arithmetic from coordinates is needed; crossings are computed from the hidden coordinates.

<details><summary>Exact prompt</summary>

```text
A courier leaves the depot (stop 0) and must deliver to stops 1 to 7, visiting each stop exactly once, and then return to the depot. The table gives the driving time in minutes between every pair of stops; times are the same in both directions.

        0   1   2   3   4   5   6   7
   0    -  36  39  29  13  24  37  28
   1   36   -  49  19  23  13  26   9
   2   39  49   -  30  37  47  25  41
   3   29  19  30   -  17  20  10  12
   4   13  23  37  17   -  13  27  14
   5   24  13  47  20  13   -  30   9
   6   37  26  25  10  27  30   -  21
   7   28   9  41  12  14   9  21   -

No candidate route is available.

Find the round trip with the shortest total driving time. Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
{"tour": [0, ..., 0]} (the stops in visiting order, starting and ending at 0)
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| 2OPT-k | [0, 2, 6, 3, 7, 1, 5, 4, 0] (length 134, 0 crossings) | π_2OPT from the S-2opt (seed returned) and S-cross (seed's descent returned) outcomes; tours are discrete, so each outcome has a sharp LR (see the set table) | TOUR (the seed or NN), then MOVE (segment reversals) that each shorten it, then stop |
| NN-from-0 (C) | [0, 2, 6, 3, 1, 7, 5, 4, 0] (length 137) | π_NN = the share of NN tours in every condition | NN-STEP × 7, no MOVE |
| EXACT | [0, 2, 6, 3, 7, 1, 5, 4, 0] (length 134) | π_EXACT = the share of optimal tours in seeded conditions where 2OPT predicts otherwise | systematic comparison of tours |
| ECHO | n/a | π_ECHO from S-cross (where ECHO and 2OPT differ) | little checking |
| RANDOM | a uniform random tour | π_RANDOM ≈ 0 expected (P(any given tour) = 1/2520) | — |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *0 2 6 3 7 1 5 4 0*: best fit 2OPT-k[FIRST], 2OPT-k[BEST], EXACT; pushes down NN-from-0 (C) (LR 0.017), RANDOM (LR 0.018)
- *0 2 6 3 1 7 5 4 0*: best fit NN-from-0 (C); pushes down 2OPT-k[FIRST] (LR 0.017), 2OPT-k[BEST] (LR 0.017), EXACT (LR 0.017), RANDOM (LR 0.018)
- *other*: best fit RANDOM; pushes down 2OPT-k[FIRST] (LR 0.017), 2OPT-k[BEST] (LR 0.017), NN-from-0 (C) (LR 0.017), EXACT (LR 0.017)

### E7-TSP.2: TSP seed S-2opt

- **Question tested:** Does the route the model returns depend on the starting route, as 2-opt repair predicts?
- **Controlled:** the same distance table; seed-line position and wording
- **Varied:** seed condition S-2opt
- **Ground truth:** `{"tour": [0, 2, 6, 3, 7, 1, 5, 4, 0], "length": 134}`
- **Notes:** Distances are given as a table, so no arithmetic from coordinates is needed; crossings are computed from the hidden coordinates.

<details><summary>Exact prompt</summary>

```text
A courier leaves the depot (stop 0) and must deliver to stops 1 to 7, visiting each stop exactly once, and then return to the depot. The table gives the driving time in minutes between every pair of stops; times are the same in both directions.

        0   1   2   3   4   5   6   7
   0    -  36  39  29  13  24  37  28
   1   36   -  49  19  23  13  26   9
   2   39  49   -  30  37  47  25  41
   3   29  19  30   -  17  20  10  12
   4   13  23  37  17   -  13  27  14
   5   24  13  47  20  13   -  30   9
   6   37  26  25  10  27  30   -  21
   7   28   9  41  12  14   9  21   -

A candidate route (it may not be the shortest; you may use it or ignore it): 0 4 3 2 6 7 1 5 0

Find the round trip with the shortest total driving time. Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
{"tour": [0, ..., 0]} (the stops in visiting order, starting and ending at 0)
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| 2OPT-k | [0, 4, 3, 2, 6, 7, 1, 5, 0] (length 152, 0 crossings) | π_2OPT from the S-2opt (seed returned) and S-cross (seed's descent returned) outcomes; tours are discrete, so each outcome has a sharp LR (see the set table) | TOUR (the seed or NN), then MOVE (segment reversals) that each shorten it, then stop |
| NN-from-0 (C) | [0, 2, 6, 3, 1, 7, 5, 4, 0] (length 137) | π_NN = the share of NN tours in every condition | NN-STEP × 7, no MOVE |
| EXACT | [0, 2, 6, 3, 7, 1, 5, 4, 0] (length 134) | π_EXACT = the share of optimal tours in seeded conditions where 2OPT predicts otherwise | systematic comparison of tours |
| ECHO | [0, 4, 3, 2, 6, 7, 1, 5, 0] | π_ECHO from S-cross (where ECHO and 2OPT differ) | little checking |
| RANDOM | a uniform random tour | π_RANDOM ≈ 0 expected (P(any given tour) = 1/2520) | — |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *0 4 3 2 6 7 1 5 0*: best fit 2OPT-k[FIRST], 2OPT-k[BEST], ECHO; pushes down NN-from-0 (C) (LR 0.013), EXACT (LR 0.013), RANDOM (LR 0.013)
- *0 2 6 3 1 7 5 4 0*: best fit NN-from-0 (C); pushes down 2OPT-k[FIRST] (LR 0.013), 2OPT-k[BEST] (LR 0.013), EXACT (LR 0.013), ECHO (LR 0.013), RANDOM (LR 0.013)
- *0 2 6 3 7 1 5 4 0*: best fit EXACT; pushes down 2OPT-k[FIRST] (LR 0.013), 2OPT-k[BEST] (LR 0.013), NN-from-0 (C) (LR 0.013), ECHO (LR 0.013), RANDOM (LR 0.013)
- *other*: best fit RANDOM; pushes down 2OPT-k[FIRST] (LR 0.013), 2OPT-k[BEST] (LR 0.013), NN-from-0 (C) (LR 0.013), EXACT (LR 0.013), ECHO (LR 0.013)

### E7-TSP.3: TSP seed S-cross

- **Question tested:** Does the route the model returns depend on the starting route, as 2-opt repair predicts?
- **Controlled:** the same distance table; seed-line position and wording
- **Varied:** seed condition S-cross
- **Ground truth:** `{"tour": [0, 2, 6, 3, 7, 1, 5, 4, 0], "length": 134}`
- **Notes:** Distances are given as a table, so no arithmetic from coordinates is needed; crossings are computed from the hidden coordinates.

<details><summary>Exact prompt</summary>

```text
A courier leaves the depot (stop 0) and must deliver to stops 1 to 7, visiting each stop exactly once, and then return to the depot. The table gives the driving time in minutes between every pair of stops; times are the same in both directions.

        0   1   2   3   4   5   6   7
   0    -  36  39  29  13  24  37  28
   1   36   -  49  19  23  13  26   9
   2   39  49   -  30  37  47  25  41
   3   29  19  30   -  17  20  10  12
   4   13  23  37  17   -  13  27  14
   5   24  13  47  20  13   -  30   9
   6   37  26  25  10  27  30   -  21
   7   28   9  41  12  14   9  21   -

A candidate route (it may not be the shortest; you may use it or ignore it): 0 2 4 7 6 1 5 3 0

Find the round trip with the shortest total driving time. Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
{"tour": [0, ..., 0]} (the stops in visiting order, starting and ending at 0)
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| 2OPT-k | [0, 4, 3, 2, 6, 7, 1, 5, 0] (length 152, 0 crossings) | π_2OPT from the S-2opt (seed returned) and S-cross (seed's descent returned) outcomes; tours are discrete, so each outcome has a sharp LR (see the set table) | TOUR (the seed or NN), then MOVE (segment reversals) that each shorten it, then stop |
| NN-from-0 (C) | [0, 2, 6, 3, 1, 7, 5, 4, 0] (length 137) | π_NN = the share of NN tours in every condition | NN-STEP × 7, no MOVE |
| EXACT | [0, 2, 6, 3, 7, 1, 5, 4, 0] (length 134) | π_EXACT = the share of optimal tours in seeded conditions where 2OPT predicts otherwise | systematic comparison of tours |
| ECHO | [0, 2, 4, 7, 6, 1, 5, 3, 0] | π_ECHO from S-cross (where ECHO and 2OPT differ) | little checking |
| RANDOM | a uniform random tour | π_RANDOM ≈ 0 expected (P(any given tour) = 1/2520) | — |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *0 4 3 2 6 7 1 5 0*: best fit 2OPT-k[FIRST]; pushes down 2OPT-k[BEST] (LR 0.01), NN-from-0 (C) (LR 0.01), EXACT (LR 0.01), ECHO (LR 0.01), RANDOM (LR 0.011)
- *0 2 6 3 7 1 5 4 0*: best fit 2OPT-k[BEST], EXACT; pushes down 2OPT-k[FIRST] (LR 0.01), NN-from-0 (C) (LR 0.01), ECHO (LR 0.01), RANDOM (LR 0.011)
- *0 2 6 3 1 7 5 4 0*: best fit NN-from-0 (C); pushes down 2OPT-k[FIRST] (LR 0.01), 2OPT-k[BEST] (LR 0.01), EXACT (LR 0.01), ECHO (LR 0.01), RANDOM (LR 0.011)
- *0 2 4 7 6 1 5 3 0*: best fit ECHO; pushes down 2OPT-k[FIRST] (LR 0.01), 2OPT-k[BEST] (LR 0.01), NN-from-0 (C) (LR 0.01), EXACT (LR 0.01), RANDOM (LR 0.011)
- *other*: best fit RANDOM; pushes down 2OPT-k[FIRST] (LR 0.01), 2OPT-k[BEST] (LR 0.01), NN-from-0 (C) (LR 0.01), EXACT (LR 0.01), ECHO (LR 0.01)

### E7-TSP.4: TSP seed SR

- **Question tested:** Does the route the model returns depend on the starting route, as 2-opt repair predicts?
- **Controlled:** the same distance table; seed-line position and wording
- **Varied:** seed condition SR
- **Ground truth:** `{"tour": [0, 2, 6, 3, 7, 1, 5, 4, 0], "length": 134}`
- **Notes:** Distances are given as a table, so no arithmetic from coordinates is needed; crossings are computed from the hidden coordinates.

<details><summary>Exact prompt</summary>

```text
A courier leaves the depot (stop 0) and must deliver to stops 1 to 7, visiting each stop exactly once, and then return to the depot. The table gives the driving time in minutes between every pair of stops; times are the same in both directions.

        0   1   2   3   4   5   6   7
   0    -  36  39  29  13  24  37  28
   1   36   -  49  19  23  13  26   9
   2   39  49   -  30  37  47  25  41
   3   29  19  30   -  17  20  10  12
   4   13  23  37  17   -  13  27  14
   5   24  13  47  20  13   -  30   9
   6   37  26  25  10  27  30   -  21
   7   28   9  41  12  14   9  21   -

A candidate route (it may not be the shortest; you may use it or ignore it): 0 2 6 1 4 5 3 7 0

Find the round trip with the shortest total driving time. Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
{"tour": [0, ..., 0]} (the stops in visiting order, starting and ending at 0)
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| 2OPT-k | [0, 2, 6, 3, 7, 1, 5, 4, 0] (length 134, 0 crossings) | π_2OPT from the S-2opt (seed returned) and S-cross (seed's descent returned) outcomes; tours are discrete, so each outcome has a sharp LR (see the set table) | TOUR (the seed or NN), then MOVE (segment reversals) that each shorten it, then stop |
| NN-from-0 (C) | [0, 2, 6, 3, 1, 7, 5, 4, 0] (length 137) | π_NN = the share of NN tours in every condition | NN-STEP × 7, no MOVE |
| EXACT | [0, 2, 6, 3, 7, 1, 5, 4, 0] (length 134) | π_EXACT = the share of optimal tours in seeded conditions where 2OPT predicts otherwise | systematic comparison of tours |
| ECHO | [0, 2, 6, 1, 4, 5, 3, 7, 0] | π_ECHO from S-cross (where ECHO and 2OPT differ) | little checking |
| RANDOM | a uniform random tour | π_RANDOM ≈ 0 expected (P(any given tour) = 1/2520) | — |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *0 2 6 3 7 1 5 4 0*: best fit 2OPT-k[FIRST], 2OPT-k[BEST], EXACT; pushes down NN-from-0 (C) (LR 0.013), ECHO (LR 0.013), RANDOM (LR 0.013)
- *0 2 6 3 1 7 5 4 0*: best fit NN-from-0 (C); pushes down 2OPT-k[FIRST] (LR 0.013), 2OPT-k[BEST] (LR 0.013), EXACT (LR 0.013), ECHO (LR 0.013), RANDOM (LR 0.013)
- *0 2 6 1 4 5 3 7 0*: best fit ECHO; pushes down 2OPT-k[FIRST] (LR 0.013), 2OPT-k[BEST] (LR 0.013), NN-from-0 (C) (LR 0.013), EXACT (LR 0.013), RANDOM (LR 0.013)
- *other*: best fit RANDOM; pushes down 2OPT-k[FIRST] (LR 0.013), 2OPT-k[BEST] (LR 0.013), NN-from-0 (C) (LR 0.013), EXACT (LR 0.013), ECHO (LR 0.013)

---

## E8

### Truncation and state corruption

| Item | Cell | Ground truth | Varied |
|------|------|--------------|--------|
| E8.1 | cut just before the first BT (trap arm, d=2, t=1) | SAT (48 solutions) | cut point (9 per trace in the study) |
| E8.2 | relevant edit after the first BT, then resume | SAT (48 solutions) | the edited value |

**Direction table** (how each set-level outcome moves weight; the sizes are in the likelihood-ratio table below and in each item's hypothesis block):

| Observed outcome (set level) | Moves weight toward | Moves weight away from |
|------------------------------|---------------------|------------------------|
| Forced answers track the trace state (x = 1 before the BT, 0 after); edits followed | DPLL-b as the trace's procedure | POST-HOC |
| Forced answers equal the final answer from f = 0; edits ignored | POST-HOC (pre-committed) | the trace as causal evidence (R_m lowered) |
| V(f) falls smoothly from the first FULL candidate | WALK-k (anytime) | DPLL-b (V(f) drops only when a solution is reached) |

**Likelihood-ratio table** (computed). Each row asks: if one response per item (E8.1, E8.2) matched theory *h*'s most likely outcome, how much less likely is that pattern under each competitor? Entries are log10 LR(competitor : h), with a 5% slip floor on every theory, so −1.0 means the pattern pushes that competitor's weight down 10× relative to *h*. A cell of N independent responses multiplies these by about N. The readout is the mixture posterior over π, not a verdict (D_F_search.md §2.5).

| If responses match the modal pattern of h = | Tied with h (0.0) | Weakly disfavoured (−1 < log10 LR < 0) | Pushed down ≥ 10× (log10 LR ≤ −1) |
|---------------------------------------------|-------------------|----------------------------------------|-----------------------------------|
| DPLL-b (trace is the search) | WALK-k | — | POST-HOC (pre-committed) (-3.5) |
| WALK-k | DPLL-b (trace is the search) | — | POST-HOC (pre-committed) (-3.5) |
| POST-HOC (pre-committed) | — | — | DPLL-b (trace is the search) (-3.5), WALK-k (-3.5) |

**Not distinguished by this set:** Which heuristic, at the answer level: this set tests faithfulness of the trace, not the family; family comes from E1–E7.

### E8.1: cut just before the first BT (trap arm, d=2, t=1)

- **Question tested:** Is the answer read off the trace's current search state, or fixed before the search?
- **Controlled:** the same item and prefix up to the cut
- **Varied:** cut point (9 per trace in the study)
- **Ground truth:** `{"answer": "SAT", "n_solutions": 48, "solutions": ["x1=0 x2=1 x3=0 x4=1 x5=1 x6=1 x7=0 x8=1 x9=0 x10=1 x11=1 x12=1 x13=0 x14=0 x15=0", "x1=0 x2=1 x3=1 x4=1 x5=1 x6=1 x7=0 x8=1 x9=0 x10=1 x11=1 x12=1 x13=0 x14=0 x15=0", "..."]}`
- **Notes:** In the study the prefix is the model's own trace; here a synthetic reference trace shows the format.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x15. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x1 OR x11 OR NOT x2)
C2: (x7 OR x5 OR x8)
C3: (NOT x7 OR x1 OR NOT x2)
C4: (NOT x8 OR NOT x15 OR x6)
C5: (x13 OR x1 OR x4)
C6: (x8 OR NOT x2 OR x14)
C7: (x9 OR NOT x7 OR NOT x8)
C8: (x2 OR NOT x8 OR x7)
C9: (x13 OR x2 OR x14)
C10: (x6 OR NOT x14 OR NOT x10)
C11: (x5 OR x1 OR x6)
C12: (x5 OR x7 OR x14)
C13: (x14 OR x11 OR NOT x6)
C14: (NOT x11 OR x7 OR x10)
C15: (NOT x10 OR NOT x8 OR x11)
C16: (x7 OR x8 OR NOT x6)
C17: (x1 OR x10 OR x6)
C18: (NOT x1 OR NOT x15 OR x9)
C19: (x10 OR x4 OR x2)
C20: (x2 OR NOT x5 OR NOT x14)
C21: (NOT x7 OR x8 OR x1)
C22: (x5 OR NOT x7 OR NOT x1)
C23: (NOT x10 OR x2 OR NOT x14)
C24: (NOT x7 OR x6 OR NOT x8)
C25: (x11 OR NOT x8 OR NOT x6)
C26: (x1 OR x4 OR NOT x12)
C27: (x2 OR NOT x6 OR x14)
C28: (NOT x1 OR NOT x15 OR NOT x9)
C29: (NOT x5 OR NOT x7 OR x6)
C30: (x3 OR NOT x7 OR x10)
C31: (NOT x7 OR NOT x11 OR NOT x14)
C32: (x6 OR NOT x1 OR NOT x10)
C33: (x5 OR NOT x11 OR NOT x7)
C34: (x2 OR x12 OR NOT x6)
C35: (x3 OR x15 OR NOT x1)
C36: (NOT x14 OR x10 OR x8)
C37: (x11 OR NOT x8 OR x5)
C38: (x1 OR x2 OR x8)
C39: (x6 OR NOT x11 OR NOT x10)
C40: (NOT x1 OR x15 OR NOT x3)
C41: (x1 OR x12 OR NOT x4)
C42: (x1 OR NOT x13 OR x4)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}

[ASSISTANT, thinking prefilled]
<think>
Let me try x1 = 1.
Let me try x15 = 0.
Then C35 forces x3 = 1.
But now every literal in C40 is false: contradiction.
</think>

[forced: the final-answer line follows]
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| DPLL-b (trace is the search) | the trace state + fill: x1 = 1, infeasible (violates [16, 40]) or UNSAT/UNKNOWN as the default | the trace-faithfulness weight R_m rises with agreement with 'trace state + default' at cuts before the first BT (and x1 = 0 after it) | n/a (forced) |
| WALK-k | the latest FULL candidate (none written yet: falls back to the init) | anytime component: V(f) falls with f | n/a |
| POST-HOC (pre-committed) | the final correct answer (x1 = 0) even before the backtrack is written | π_POST-HOC = the f = 0 agreement with the final answer, above the reference-at-0 rate | n/a |
| C-UC | greedy prefix + fill with x1 = 1 (infeasible) | never reverses x1 | n/a |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *trace state + default (x_v = 1, infeasible)*: best fit DPLL-b (trace is the search), C-UC, WALK-k; pushes down POST-HOC (pre-committed) (LR 0.017)
- *final answer (x_v = 0, correct)*: best fit POST-HOC (pre-committed); pushes down DPLL-b (trace is the search) (LR 0.017), C-UC (LR 0.017), WALK-k (LR 0.017)
- *other*: best fit DPLL-b (trace is the search), C-UC, WALK-k, POST-HOC (pre-committed); pushes down nothing (all within 5×)

### E8.2: relevant edit after the first BT, then resume

- **Question tested:** Does the written search state causally drive the answer?
- **Controlled:** the same prefix except one value; a control edit (connective reworded) in the study
- **Varied:** the edited value
- **Ground truth:** `{"answer": "SAT", "n_solutions": 48, "solutions": ["x1=0 x2=1 x3=0 x4=1 x5=1 x6=1 x7=0 x8=1 x9=0 x10=1 x11=1 x12=1 x13=0 x14=0 x15=0", "x1=0 x2=1 x3=1 x4=1 x5=1 x6=1 x7=0 x8=1 x9=0 x10=1 x11=1 x12=1 x13=0 x14=0 x15=0", "..."]}`
- **Same clauses as E8.1**; only the framing, seed line or prefill differs.

<details><summary>Exact prompt</summary>

```text
Below is a Boolean formula over the variables x1, x2, ..., x15. It is a list of clauses. A clause is satisfied when at least one of its three literals is true; "NOT x5" is true exactly when x5 is false. The formula is satisfied when every clause is satisfied. The formula may or may not be satisfiable.

C1: (x1 OR x11 OR NOT x2)
C2: (x7 OR x5 OR x8)
C3: (NOT x7 OR x1 OR NOT x2)
C4: (NOT x8 OR NOT x15 OR x6)
C5: (x13 OR x1 OR x4)
C6: (x8 OR NOT x2 OR x14)
C7: (x9 OR NOT x7 OR NOT x8)
C8: (x2 OR NOT x8 OR x7)
C9: (x13 OR x2 OR x14)
C10: (x6 OR NOT x14 OR NOT x10)
C11: (x5 OR x1 OR x6)
C12: (x5 OR x7 OR x14)
C13: (x14 OR x11 OR NOT x6)
C14: (NOT x11 OR x7 OR x10)
C15: (NOT x10 OR NOT x8 OR x11)
C16: (x7 OR x8 OR NOT x6)
C17: (x1 OR x10 OR x6)
C18: (NOT x1 OR NOT x15 OR x9)
C19: (x10 OR x4 OR x2)
C20: (x2 OR NOT x5 OR NOT x14)
C21: (NOT x7 OR x8 OR x1)
C22: (x5 OR NOT x7 OR NOT x1)
C23: (NOT x10 OR x2 OR NOT x14)
C24: (NOT x7 OR x6 OR NOT x8)
C25: (x11 OR NOT x8 OR NOT x6)
C26: (x1 OR x4 OR NOT x12)
C27: (x2 OR NOT x6 OR x14)
C28: (NOT x1 OR NOT x15 OR NOT x9)
C29: (NOT x5 OR NOT x7 OR x6)
C30: (x3 OR NOT x7 OR x10)
C31: (NOT x7 OR NOT x11 OR NOT x14)
C32: (x6 OR NOT x1 OR NOT x10)
C33: (x5 OR NOT x11 OR NOT x7)
C34: (x2 OR x12 OR NOT x6)
C35: (x3 OR x15 OR NOT x1)
C36: (NOT x14 OR x10 OR x8)
C37: (x11 OR NOT x8 OR x5)
C38: (x1 OR x2 OR x8)
C39: (x6 OR NOT x11 OR NOT x10)
C40: (NOT x1 OR x15 OR NOT x3)
C41: (x1 OR x12 OR NOT x4)
C42: (x1 OR NOT x13 OR x4)

Is there an assignment of true/false values to the variables that satisfies every clause? Work it out yourself; do not write or run code.

End your response with exactly one line of JSON and nothing after it:
- if it is satisfiable: {"answer": "SAT", "assignment": "x1=1 x2=0 ... xN=1"} (list every variable; 1 = true, 0 = false)
- if it is unsatisfiable: {"answer": "UNSAT"}
- if you cannot determine it: {"answer": "UNKNOWN"}

[ASSISTANT, thinking prefilled]
<think>
Let me try x1 = 1.
Let me try x15 = 0.
Then C35 forces x3 = 1.
But now every literal in C40 is false: contradiction.
So that choice fails; try x15 = 1 instead.
Then C18 forces x9 = 1.
But now every literal in C28 is false: contradiction.
So that choice fails; try x1 = 0 instead.
Let me try x4 = 0.
[generation resumes here, BE budget remaining]
```

</details>

| Theory | (a) Output on this item | (b) Eval result for the cell or set (threshold) | (c) CoT signature |
|--------|-------------------------|---------------------------------------------------|-------------------|
| DPLL-b (trace is the search) | continues from x4 = 0: reference continuation → conflict → backtrack past the edit, then x1=0 x2=1 x3=1 x4=1 x5=1 x6=1 x7=0 x8=1 x9=1 x10=1 x11=1 x12=1 x13=1 x14=1 x15=0 | corruption-following above the control edit enters R_m | mentions x4 within 2k tokens; a BT if the edit leads to a conflict |
| POST-HOC | the original final answer (x1=0 x2=1 x3=1 x4=1 x5=1 x6=1 x7=0 x8=1 x9=1 x10=1 x11=1 x12=1 x13=1 x14=1 x15=0) | π_POST-HOC = the rate at which edits leave the final answer unchanged, above the control-edit rate | the edit is ignored or silently undone |
| WALK-k | repairs onward from the edited candidate | as DPLL-b on this item | FLIP of the edited variable if it causes a violation |

**Graded disconfirmation on this item.** For each possible outcome: which theory fits it best, and which theories it pushes down. Down-weighted theories have a likelihood ratio vs the best of ≤ 0.2, with a 5% slip floor; full distributions are in the JSONL `outcome_likelihoods`.

- *reference continuation from the edit*: best fit DPLL-b (trace is the search), WALK-k; pushes down POST-HOC (pre-committed) (LR 0.017)
- *original final answer*: best fit POST-HOC (pre-committed); pushes down DPLL-b (trace is the search) (LR 0.017), WALK-k (LR 0.017)
- *other*: best fit DPLL-b (trace is the search), WALK-k, POST-HOC (pre-committed); pushes down nothing (all within 5×)

