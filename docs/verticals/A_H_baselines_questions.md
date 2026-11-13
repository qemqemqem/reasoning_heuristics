# Example question library: A / H / nuisance / I baselines

*Companion to [A_H_baselines.md](A_H_baselines.md). Every eval E1–E9 has at least one complete counterfactual set: a base item plus every variant its design needs, side by side.*

**Readout convention.** Heuristics may be partly used, so every set is read as **graded weight**, not as used / not used:

- the mixture weight π_h (posterior mean and 95% interval), which may depend on item features and on the model (family I);
- error lift above chance;
- log-likelihood gain or Bayes factor over the null and over the nearest competitor;
- for traces, the share of traces matching h's signature, weighted by measured faithfulness r̂.

Each set below therefore gives three things:

1. A **hypothesis matrix**: per theory, (a) its output on each item; (b) its pure-theory value of the set's statistic and the weight resolution; (c) its predicted trace features.
2. A **likelihood-ratio table**: for each observable response pattern, how strongly it favours each theory over the best alternative, and which theories it pushes toward zero weight (log₁₀ LR ≤ −1).
3. A **weight-resolution table**, from the Fisher information of a two-component mixture at π = 0 at the study N. The nearest competitor is the theory whose predictions are closest to h's (smallest KL divergence over the set):
   - the smallest weight π_h detectable with 80% power (one-sided α = 0.05) against h's nearest competitor in the set;
   - the upper 95% bound on π_h if the model is purely that competitor;
   - the expected log₁₀ Bayes factor, pure h versus pure competitor;
   - a worst case: the detectable π if the rest of the model is the base that masks h most (usually RANDOM, whose ½ answers hide any mixed-in component).

A theory with *identical* predictions to another on every item of a set has no weight resolution there. The table says so and points to the set that separates them.

**Files and verification.**

- **Machine-readable copy:** [`data/examples/A_H_baselines.jsonl`](../../data/examples/A_H_baselines.jsonl). One object per item, with fields:
  - `prompt`, `ground_truth`, `predictions`, `trace_predictions`;
  - `hypotheses` (theory → {output, eval_prediction, cot_prediction});
  - `disconfirms` (pattern → theories pushed toward zero, with log₁₀ LR);
  - `supports` (pattern → favoured theories, with log₁₀ LR);
  - `weight_resolution`, `params`, `notes`.
- **Verification.** Every ground truth and every output was computed, not written by hand, by throwaway scripts kept outside the repo:
  - brute force for SAT (n ≤ 15), entailment (≤ 6 atoms) and colouring (10 people);
  - reference DPLL, WalkSAT, unit propagation, greedy and FIRST-FIT;
  - PyETR 1.0.0 for ETR;
  - assertions for every construction property (equal cue vectors within a pair, pure padding, disjoint solution sets, exactly one entailed MC option, a two-way tie for the shortest MC option).
- **Likelihood model.** Deterministic predictions are clipped to [0.05, 0.95] (a slip floor), and responses are independent given the theory.
- **Sizes are dev-size**, so prompts stay readable; the study uses the same templates at the vertical doc's sizes. Thresholds marked *illustrative* (θ_m, FREQ θ = 2, DPLL budget b = 8, D case-split b = 4, p_d, p_f, ε) only make outputs concrete; in the study they are fitted out of sample. `DENSITY` uses the ecological θ = 4.26.

## Contents

- [E1: SAT structure-blindness minimal pair (+ null pair, + menu framing)](#e1-sat)
- [E1: entailment structure-blindness minimal pair](#e1-ent)
- [E2: satisfiability-neutral padding (base / K / J / U × SAT / UNSAT core)](#e2-sat)
- [E2: matched conclusions on one premise set (g × FREQ × ATMOSPHERE)](#e2-ent)
- [E3: four cells of the shared α × n sweep (two share m = 42)](#e3)
- [E4: one MC item in 4 rotations × 2 label schemes](#e4)
- [E4: premise order (fact → rule → rule chain, all 6 orders)](#e4-order)
- [E5: inversion set, rooms theme (T / N / I / I+R / P)](#e5-col)
- [E5: inversion pair, SAT (N vs I)](#e5-sat)
- [E6: counter-model rarity (one premise set, six conclusions)](#e6)
- [E7: four renderings of one SAT item (+ echo condition)](#e7)
- [E8: faithfulness continuations on E2-SAT K/J](#e8)
- [E9: in-context environments V / N / R × test K / J](#e9)

<a id="e1-sat"></a>
## E1: SAT structure-blindness minimal pair (+ null pair, + menu framing)

**Reasoning question.** Are SAT/UNSAT decisions sensitive to a structural edit that flips g, with every surface statistic fixed?

**Design.** x and x′ differ only in the signs of two occurrences of one variable; the null pair is the same kind of edit with g unchanged; the menu item is x in a story framing.  *Study units:* critical pair (x, x′) × 400; x full response (decision + witness) × 400; B1 stratum pair × 50.

| Item | Cell | Ground truth | Controlled | Varied |
|---|---|---|---|---|
| `E1-SAT-x` | critical, SAT member (x) | SAT | n, m, α, tokens, every variable's polarity counts, the clause negation-count multiset, variable positions, names, framing | the signs of two occurrences of one variable — flips g |
| `E1-SAT-x'` | critical, UNSAT member (x′) | UNSAT | n, m, α, tokens, every variable's polarity counts, the clause negation-count multiset, variable positions, names, framing | the signs of two occurrences of one variable — flips g |
| `E1-SAT-null1` | null pair, member 1 | SAT | n, m, α, tokens, every variable's polarity counts, the clause negation-count multiset, variable positions, names, framing | the signs of two occurrences of one variable — g unchanged |
| `E1-SAT-null2` | null pair, member 2 | SAT | n, m, α, tokens, every variable's polarity counts, the clause negation-count multiset, variable positions, names, framing | the signs of two occurrences of one variable — g unchanged |
| `E1-SAT-x-menu` | framing variant of x (menu theme) | SAT | the logical content of x | framing: CNF → menu story |
| `E1-SAT-B1-x` | B1 stratum, SAT member | SAT | n, m, α, tokens, every variable's polarity counts, the clause negation-count multiset, variable positions, names, framing | the same edit type; the formula has 2 unit clauses and 8 binary clauses, so unit propagation can refute x′ |
| `E1-SAT-B1-x'` | B1 stratum, UNSAT member (UP-refutable) | UNSAT | n, m, α, tokens, every variable's polarity counts, the clause negation-count multiset, variable positions, names, framing | the same edit type; the formula has 2 unit clauses and 8 binary clauses, so unit propagation can refute x′ |

<details><summary>Prompt and computed outputs — <code>E1-SAT-x</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x08 ∨ x02 ∨ x09)
C02: (¬x02 ∨ ¬x09 ∨ ¬x08)
C03: (¬x08 ∨ ¬x06 ∨ x10)
C04: (¬x05 ∨ x08 ∨ ¬x09)
C05: (¬x12 ∨ ¬x09 ∨ x05)
C06: (x08 ∨ x03 ∨ x07)
C07: (x04 ∨ x07 ∨ x02)
C08: (x03 ∨ ¬x11 ∨ ¬x06)
C09: (¬x04 ∨ x02 ∨ ¬x07)
C10: (¬x04 ∨ x03 ∨ x07)
C11: (¬x06 ∨ x12 ∨ ¬x02)
C12: (x08 ∨ ¬x01 ∨ ¬x07)
C13: (¬x02 ∨ x12 ∨ x04)
C14: (¬x01 ∨ ¬x03 ∨ ¬x05)
C15: (x11 ∨ ¬x05 ∨ ¬x07)
C16: (x12 ∨ ¬x06 ∨ x02)
C17: (¬x02 ∨ ¬x05 ∨ x01)
C18: (¬x04 ∨ x02 ∨ x05)
C19: (¬x09 ∨ x07 ∨ ¬x05)
C20: (x02 ∨ x03 ∨ x05)
C21: (x05 ∨ ¬x09 ∨ x04)
C22: (x06 ∨ x01 ∨ ¬x05)
C23: (x04 ∨ x09 ∨ ¬x08)
C24: (¬x11 ∨ ¬x07 ∨ ¬x08)
C25: (x05 ∨ ¬x04 ∨ ¬x11)
C26: (¬x11 ∨ ¬x03 ∨ ¬x07)
C27: (x01 ∨ x02 ∨ ¬x05)
C28: (¬x07 ∨ ¬x09 ∨ x05)
C29: (x03 ∨ x12 ∨ ¬x05)
C30: (x09 ∨ ¬x06 ∨ x04)
C31: (x03 ∨ x01 ∨ ¬x06)
C32: (¬x04 ∨ x12 ∨ ¬x09)
C33: (x03 ∨ x07 ∨ x10)
C34: (¬x04 ∨ ¬x02 ∨ x10)
C35: (¬x12 ∨ ¬x10 ∨ x07)
C36: (x05 ∨ ¬x10 ∨ ¬x03)
C37: (x11 ∨ ¬x07 ∨ ¬x09)
C38: (¬x01 ∨ ¬x11 ∨ ¬x10)
C39: (x11 ∨ x04 ∨ x02)
C40: (¬x02 ∨ ¬x07 ∨ ¬x08)
C41: (x11 ∨ x04 ∨ x08)
C42: (¬x09 ∨ x12 ∨ ¬x02)
C43: (x05 ∨ ¬x02 ∨ x12)
C44: (¬x11 ∨ x08 ∨ ¬x12)
C45: (¬x05 ∨ x01 ∨ ¬x10)
C46: (¬x06 ∨ x05 ∨ x11)
C47: (¬x08 ∨ ¬x05 ∨ x02)
C48: (x09 ∨ ¬x05 ∨ ¬x08)
C49: (¬x09 ∨ ¬x04 ∨ x05)
C50: (¬x08 ∨ x02 ∨ x09)
C51: (¬x04 ∨ x12 ∨ ¬x02)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** SAT, e.g. 010100100101 (1 solution)
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 6.4 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** SAT (α_U = 4.25 vs θ = 4.26)
- **A2 DENSITY-D:** SAT (α_D = 4.25 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 51 vs illustrative θ_m = 50)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 6.4 clauses
- **H SAMPLE-8:** P(SAT) = 0.002 (1 solutions in 2^12)
- **NOISY-EXACT-STEP:** SAT w.p. 0.83 (L = 20 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** SAT w.p. 0.80 (L = m = 51, p = 0.01/clause)
- **PERCEPTION-NOISE:** SAT (dropped clauses cannot remove solutions)
- **C0 POLARITY:** SAT, witness 111000000001 (1 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 111110010011 violates 3)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** UNSAT by default (20 decisions > illustrative b = 8)
- **F WALK-200:** SAT in 83% of runs, else UNSAT by default
- **D∘DENSITY (b=4):** SAT (budget exceeded at 20 decisions → density default)
- *params:* `{"n_used": 12, "n_decl": 12, "m": 51, "alpha_U": 4.25, "alpha_D": 4.25, "n_solutions": 1, "dpll_decisions": 20, "dpll_decisions_pure_literal": 18, "polarity_witness": "111000000001", "polarity_violations": 1, "greedy_witness": "111110010011", "greedy_violations": 3, "dpll_witness": "010100100101", "edit": "swap the signs of x02 in C01 (+ → ¬) and C13 (¬ → +)"}`
- *notes:* Dev-size instance (n = 12, m = 51); the study uses n ∈ {16, 24, 36} with the same template and edit.

</details>

<details><summary>Prompt and computed outputs — <code>E1-SAT-x'</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x08 ∨ ¬x02 ∨ x09)
C02: (¬x02 ∨ ¬x09 ∨ ¬x08)
C03: (¬x08 ∨ ¬x06 ∨ x10)
C04: (¬x05 ∨ x08 ∨ ¬x09)
C05: (¬x12 ∨ ¬x09 ∨ x05)
C06: (x08 ∨ x03 ∨ x07)
C07: (x04 ∨ x07 ∨ x02)
C08: (x03 ∨ ¬x11 ∨ ¬x06)
C09: (¬x04 ∨ x02 ∨ ¬x07)
C10: (¬x04 ∨ x03 ∨ x07)
C11: (¬x06 ∨ x12 ∨ ¬x02)
C12: (x08 ∨ ¬x01 ∨ ¬x07)
C13: (x02 ∨ x12 ∨ x04)
C14: (¬x01 ∨ ¬x03 ∨ ¬x05)
C15: (x11 ∨ ¬x05 ∨ ¬x07)
C16: (x12 ∨ ¬x06 ∨ x02)
C17: (¬x02 ∨ ¬x05 ∨ x01)
C18: (¬x04 ∨ x02 ∨ x05)
C19: (¬x09 ∨ x07 ∨ ¬x05)
C20: (x02 ∨ x03 ∨ x05)
C21: (x05 ∨ ¬x09 ∨ x04)
C22: (x06 ∨ x01 ∨ ¬x05)
C23: (x04 ∨ x09 ∨ ¬x08)
C24: (¬x11 ∨ ¬x07 ∨ ¬x08)
C25: (x05 ∨ ¬x04 ∨ ¬x11)
C26: (¬x11 ∨ ¬x03 ∨ ¬x07)
C27: (x01 ∨ x02 ∨ ¬x05)
C28: (¬x07 ∨ ¬x09 ∨ x05)
C29: (x03 ∨ x12 ∨ ¬x05)
C30: (x09 ∨ ¬x06 ∨ x04)
C31: (x03 ∨ x01 ∨ ¬x06)
C32: (¬x04 ∨ x12 ∨ ¬x09)
C33: (x03 ∨ x07 ∨ x10)
C34: (¬x04 ∨ ¬x02 ∨ x10)
C35: (¬x12 ∨ ¬x10 ∨ x07)
C36: (x05 ∨ ¬x10 ∨ ¬x03)
C37: (x11 ∨ ¬x07 ∨ ¬x09)
C38: (¬x01 ∨ ¬x11 ∨ ¬x10)
C39: (x11 ∨ x04 ∨ x02)
C40: (¬x02 ∨ ¬x07 ∨ ¬x08)
C41: (x11 ∨ x04 ∨ x08)
C42: (¬x09 ∨ x12 ∨ ¬x02)
C43: (x05 ∨ ¬x02 ∨ x12)
C44: (¬x11 ∨ x08 ∨ ¬x12)
C45: (¬x05 ∨ x01 ∨ ¬x10)
C46: (¬x06 ∨ x05 ∨ x11)
C47: (¬x08 ∨ ¬x05 ∨ x02)
C48: (x09 ∨ ¬x05 ∨ ¬x08)
C49: (¬x09 ∨ ¬x04 ∨ x05)
C50: (¬x08 ∨ x02 ∨ x09)
C51: (¬x04 ∨ x12 ∨ ¬x02)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** UNSAT
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 6.4 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** SAT (α_U = 4.25 vs θ = 4.26)
- **A2 DENSITY-D:** SAT (α_D = 4.25 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 51 vs illustrative θ_m = 50)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 6.4 clauses
- **H SAMPLE-8:** P(SAT) = 0.000 (0 solutions in 2^12)
- **NOISY-EXACT-STEP:** UNSAT w.p. 0.85 (L = 18 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** UNSAT w.p. 0.80 (L = m = 51, p = 0.01/clause)
- **PERCEPTION-NOISE:** P(SAT) = 0.321 at p_d = 0.05 (7 necessary clauses)
- **C0 POLARITY:** SAT, witness 111000000001 (2 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 111010010011 violates 3)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** UNSAT by default (18 decisions > illustrative b = 8)
- **F WALK-200:** UNSAT by default (never certifies)
- **D∘DENSITY (b=4):** SAT (budget exceeded at 18 decisions → density default)
- *params:* `{"n_used": 12, "n_decl": 12, "m": 51, "alpha_U": 4.25, "alpha_D": 4.25, "n_solutions": 0, "dpll_decisions": 18, "dpll_decisions_pure_literal": 16, "polarity_witness": "111000000001", "polarity_violations": 2, "greedy_witness": "111010010011", "greedy_violations": 3, "dpll_witness": null, "edit": "swap the signs of x02 in C01 (+ → ¬) and C13 (¬ → +)"}`
- *notes:* Dev-size instance (n = 12, m = 51); the study uses n ∈ {16, 24, 36} with the same template and edit.

</details>

<details><summary>Prompt and computed outputs — <code>E1-SAT-null1</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x08 ∨ ¬x09 ∨ x12)
C02: (¬x09 ∨ x08 ∨ x10)
C03: (¬x02 ∨ x09 ∨ x01)
C04: (¬x12 ∨ ¬x10 ∨ x03)
C05: (¬x01 ∨ ¬x04 ∨ x11)
C06: (x10 ∨ x04 ∨ x09)
C07: (x02 ∨ ¬x08 ∨ ¬x05)
C08: (¬x02 ∨ ¬x05 ∨ x06)
C09: (x10 ∨ x02 ∨ x07)
C10: (x01 ∨ ¬x11 ∨ x12)
C11: (x07 ∨ ¬x12 ∨ ¬x11)
C12: (x05 ∨ x06 ∨ x02)
C13: (¬x02 ∨ x03 ∨ x04)
C14: (x08 ∨ ¬x03 ∨ ¬x09)
C15: (x03 ∨ x07 ∨ x11)
C16: (¬x05 ∨ x10 ∨ x12)
C17: (x10 ∨ ¬x11 ∨ x12)
C18: (x05 ∨ x01 ∨ x10)
C19: (¬x02 ∨ x04 ∨ x10)
C20: (¬x10 ∨ x08 ∨ ¬x03)
C21: (x07 ∨ x03 ∨ ¬x11)
C22: (¬x12 ∨ ¬x04 ∨ x03)
C23: (x07 ∨ x08 ∨ x10)
C24: (¬x09 ∨ x05 ∨ x04)
C25: (¬x10 ∨ ¬x08 ∨ ¬x05)
C26: (¬x03 ∨ ¬x04 ∨ ¬x08)
C27: (¬x05 ∨ x04 ∨ x11)
C28: (x04 ∨ x01 ∨ ¬x11)
C29: (x03 ∨ x02 ∨ x06)
C30: (¬x12 ∨ ¬x09 ∨ ¬x10)
C31: (¬x08 ∨ x06 ∨ ¬x05)
C32: (x08 ∨ ¬x02 ∨ x05)
C33: (¬x09 ∨ ¬x06 ∨ ¬x01)
C34: (¬x06 ∨ ¬x12 ∨ ¬x02)
C35: (¬x07 ∨ ¬x01 ∨ x08)
C36: (x10 ∨ x01 ∨ x12)
C37: (x05 ∨ ¬x07 ∨ ¬x06)
C38: (x08 ∨ ¬x12 ∨ x09)
C39: (x10 ∨ ¬x02 ∨ x08)
C40: (x10 ∨ x11 ∨ x08)
C41: (¬x11 ∨ ¬x10 ∨ x04)
C42: (x08 ∨ ¬x12 ∨ x04)
C43: (x07 ∨ ¬x04 ∨ x11)
C44: (x03 ∨ ¬x12 ∨ x08)
C45: (x02 ∨ x05 ∨ ¬x03)
C46: (x07 ∨ x12 ∨ ¬x09)
C47: (x10 ∨ x08 ∨ ¬x06)
C48: (¬x01 ∨ x11 ∨ ¬x05)
C49: (x01 ∨ x11 ∨ ¬x03)
C50: (¬x05 ∨ ¬x04 ∨ x03)
C51: (¬x02 ∨ ¬x11 ∨ ¬x09)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** SAT, e.g. 111000010100 (7 solutions)
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 6.4 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** SAT (α_U = 4.25 vs θ = 4.26)
- **A2 DENSITY-D:** SAT (α_D = 4.25 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 51 vs illustrative θ_m = 50)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 6.4 clauses
- **H SAMPLE-8:** P(SAT) = 0.014 (7 solutions in 2^12)
- **NOISY-EXACT-STEP:** SAT w.p. 0.94 (L = 6 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** SAT w.p. 0.80 (L = m = 51, p = 0.01/clause)
- **PERCEPTION-NOISE:** SAT (dropped clauses cannot remove solutions)
- **C0 POLARITY:** SAT, witness 101101110110 (3 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 101100110111 violates 3)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** SAT (exact: 6 decisions ≤ illustrative b = 8)
- **F WALK-200:** SAT in 100% of runs, else UNSAT by default
- **D∘DENSITY (b=4):** SAT (budget exceeded at 6 decisions → density default)
- *params:* `{"n_used": 12, "n_decl": 12, "m": 51, "alpha_U": 4.25, "alpha_D": 4.25, "n_solutions": 7, "dpll_decisions": 6, "dpll_decisions_pure_literal": 5, "polarity_witness": "101101110110", "polarity_violations": 3, "greedy_witness": "101100110111", "greedy_violations": 3, "dpll_witness": "111001010100", "edit": "swap the signs of x01 in C03 (+ → ¬) and C05 (¬ → +)"}`
- *notes:* Dev-size instance (n = 12, m = 51); the study uses n ∈ {16, 24, 36} with the same template and edit.

</details>

<details><summary>Prompt and computed outputs — <code>E1-SAT-null2</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x08 ∨ ¬x09 ∨ x12)
C02: (¬x09 ∨ x08 ∨ x10)
C03: (¬x02 ∨ x09 ∨ ¬x01)
C04: (¬x12 ∨ ¬x10 ∨ x03)
C05: (x01 ∨ ¬x04 ∨ x11)
C06: (x10 ∨ x04 ∨ x09)
C07: (x02 ∨ ¬x08 ∨ ¬x05)
C08: (¬x02 ∨ ¬x05 ∨ x06)
C09: (x10 ∨ x02 ∨ x07)
C10: (x01 ∨ ¬x11 ∨ x12)
C11: (x07 ∨ ¬x12 ∨ ¬x11)
C12: (x05 ∨ x06 ∨ x02)
C13: (¬x02 ∨ x03 ∨ x04)
C14: (x08 ∨ ¬x03 ∨ ¬x09)
C15: (x03 ∨ x07 ∨ x11)
C16: (¬x05 ∨ x10 ∨ x12)
C17: (x10 ∨ ¬x11 ∨ x12)
C18: (x05 ∨ x01 ∨ x10)
C19: (¬x02 ∨ x04 ∨ x10)
C20: (¬x10 ∨ x08 ∨ ¬x03)
C21: (x07 ∨ x03 ∨ ¬x11)
C22: (¬x12 ∨ ¬x04 ∨ x03)
C23: (x07 ∨ x08 ∨ x10)
C24: (¬x09 ∨ x05 ∨ x04)
C25: (¬x10 ∨ ¬x08 ∨ ¬x05)
C26: (¬x03 ∨ ¬x04 ∨ ¬x08)
C27: (¬x05 ∨ x04 ∨ x11)
C28: (x04 ∨ x01 ∨ ¬x11)
C29: (x03 ∨ x02 ∨ x06)
C30: (¬x12 ∨ ¬x09 ∨ ¬x10)
C31: (¬x08 ∨ x06 ∨ ¬x05)
C32: (x08 ∨ ¬x02 ∨ x05)
C33: (¬x09 ∨ ¬x06 ∨ ¬x01)
C34: (¬x06 ∨ ¬x12 ∨ ¬x02)
C35: (¬x07 ∨ ¬x01 ∨ x08)
C36: (x10 ∨ x01 ∨ x12)
C37: (x05 ∨ ¬x07 ∨ ¬x06)
C38: (x08 ∨ ¬x12 ∨ x09)
C39: (x10 ∨ ¬x02 ∨ x08)
C40: (x10 ∨ x11 ∨ x08)
C41: (¬x11 ∨ ¬x10 ∨ x04)
C42: (x08 ∨ ¬x12 ∨ x04)
C43: (x07 ∨ ¬x04 ∨ x11)
C44: (x03 ∨ ¬x12 ∨ x08)
C45: (x02 ∨ x05 ∨ ¬x03)
C46: (x07 ∨ x12 ∨ ¬x09)
C47: (x10 ∨ x08 ∨ ¬x06)
C48: (¬x01 ∨ x11 ∨ ¬x05)
C49: (x01 ∨ x11 ∨ ¬x03)
C50: (¬x05 ∨ ¬x04 ∨ x03)
C51: (¬x02 ∨ ¬x11 ∨ ¬x09)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** SAT, e.g. 110100111000 (2 solutions)
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 6.4 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** SAT (α_U = 4.25 vs θ = 4.26)
- **A2 DENSITY-D:** SAT (α_D = 4.25 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 51 vs illustrative θ_m = 50)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 6.4 clauses
- **H SAMPLE-8:** P(SAT) = 0.004 (2 solutions in 2^12)
- **NOISY-EXACT-STEP:** SAT w.p. 0.98 (L = 2 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** SAT w.p. 0.80 (L = m = 51, p = 0.01/clause)
- **PERCEPTION-NOISE:** SAT (dropped clauses cannot remove solutions)
- **C0 POLARITY:** SAT, witness 101101110110 (3 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 101100110111 violates 3)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** SAT (exact: 2 decisions ≤ illustrative b = 8)
- **F WALK-200:** SAT in 90% of runs, else UNSAT by default
- **D∘DENSITY (b=4):** SAT (search finishes in 2 ≤ 4 decisions)
- *params:* `{"n_used": 12, "n_decl": 12, "m": 51, "alpha_U": 4.25, "alpha_D": 4.25, "n_solutions": 2, "dpll_decisions": 2, "dpll_decisions_pure_literal": 2, "polarity_witness": "101101110110", "polarity_violations": 3, "greedy_witness": "101100110111", "greedy_violations": 3, "dpll_witness": "110100111100", "edit": "swap the signs of x01 in C03 (+ → ¬) and C05 (¬ → +)"}`
- *notes:* Dev-size instance (n = 12, m = 51); the study uses n ∈ {16, 24, 36} with the same template and edit.

</details>

<details><summary>Prompt and computed outputs — <code>E1-SAT-x-menu</code></summary>

```text
You are planning which dishes to serve at a dinner. There are 12 candidate dishes, D01 to D12; each is either served or not served.
Each guest has a request that is met if at least one of its three conditions holds.

Guest 01: D08 is served, or D02 is served, or D09 is served.
Guest 02: D02 is not served, or D09 is not served, or D08 is not served.
Guest 03: D08 is not served, or D06 is not served, or D10 is served.
Guest 04: D05 is not served, or D08 is served, or D09 is not served.
Guest 05: D12 is not served, or D09 is not served, or D05 is served.
Guest 06: D08 is served, or D03 is served, or D07 is served.
Guest 07: D04 is served, or D07 is served, or D02 is served.
Guest 08: D03 is served, or D11 is not served, or D06 is not served.
Guest 09: D04 is not served, or D02 is served, or D07 is not served.
Guest 10: D04 is not served, or D03 is served, or D07 is served.
Guest 11: D06 is not served, or D12 is served, or D02 is not served.
Guest 12: D08 is served, or D01 is not served, or D07 is not served.
Guest 13: D02 is not served, or D12 is served, or D04 is served.
Guest 14: D01 is not served, or D03 is not served, or D05 is not served.
Guest 15: D11 is served, or D05 is not served, or D07 is not served.
Guest 16: D12 is served, or D06 is not served, or D02 is served.
Guest 17: D02 is not served, or D05 is not served, or D01 is served.
Guest 18: D04 is not served, or D02 is served, or D05 is served.
Guest 19: D09 is not served, or D07 is served, or D05 is not served.
Guest 20: D02 is served, or D03 is served, or D05 is served.
Guest 21: D05 is served, or D09 is not served, or D04 is served.
Guest 22: D06 is served, or D01 is served, or D05 is not served.
Guest 23: D04 is served, or D09 is served, or D08 is not served.
Guest 24: D11 is not served, or D07 is not served, or D08 is not served.
Guest 25: D05 is served, or D04 is not served, or D11 is not served.
Guest 26: D11 is not served, or D03 is not served, or D07 is not served.
Guest 27: D01 is served, or D02 is served, or D05 is not served.
Guest 28: D07 is not served, or D09 is not served, or D05 is served.
Guest 29: D03 is served, or D12 is served, or D05 is not served.
Guest 30: D09 is served, or D06 is not served, or D04 is served.
Guest 31: D03 is served, or D01 is served, or D06 is not served.
Guest 32: D04 is not served, or D12 is served, or D09 is not served.
Guest 33: D03 is served, or D07 is served, or D10 is served.
Guest 34: D04 is not served, or D02 is not served, or D10 is served.
Guest 35: D12 is not served, or D10 is not served, or D07 is served.
Guest 36: D05 is served, or D10 is not served, or D03 is not served.
Guest 37: D11 is served, or D07 is not served, or D09 is not served.
Guest 38: D01 is not served, or D11 is not served, or D10 is not served.
Guest 39: D11 is served, or D04 is served, or D02 is served.
Guest 40: D02 is not served, or D07 is not served, or D08 is not served.
Guest 41: D11 is served, or D04 is served, or D08 is served.
Guest 42: D09 is not served, or D12 is served, or D02 is not served.
Guest 43: D05 is served, or D02 is not served, or D12 is served.
Guest 44: D11 is not served, or D08 is served, or D12 is not served.
Guest 45: D05 is not served, or D01 is served, or D10 is not served.
Guest 46: D06 is not served, or D05 is served, or D11 is served.
Guest 47: D08 is not served, or D05 is not served, or D02 is served.
Guest 48: D09 is served, or D05 is not served, or D08 is not served.
Guest 49: D09 is not served, or D04 is not served, or D05 is served.
Guest 50: D08 is not served, or D02 is served, or D09 is served.
Guest 51: D04 is not served, or D12 is served, or D02 is not served.

Can you choose which dishes to serve so that every guest's request is met?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per dish, D01 first; 1 = served, 0 = not served>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** SAT, e.g. 010100100101 (1 solution)
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 6.4 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** SAT (α_U = 4.25 vs θ = 4.26)
- **A2 DENSITY-D:** SAT (α_D = 4.25 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 51 vs illustrative θ_m = 50)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 6.4 clauses
- **H SAMPLE-8:** P(SAT) = 0.002 (1 solutions in 2^12)
- **NOISY-EXACT-STEP:** SAT w.p. 0.83 (L = 20 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** SAT w.p. 0.80 (L = m = 51, p = 0.01/clause)
- **PERCEPTION-NOISE:** SAT (dropped clauses cannot remove solutions)
- **C0 POLARITY:** SAT, witness 111000000001 (1 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 111110010011 violates 3)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** UNSAT by default (20 decisions > illustrative b = 8)
- **F WALK-200:** SAT in 83% of runs, else UNSAT by default
- **D∘DENSITY (b=4):** SAT (budget exceeded at 20 decisions → density default)
- *params:* `{"n_used": 12, "n_decl": 12, "m": 51, "alpha_U": 4.25, "alpha_D": 4.25, "n_solutions": 1, "dpll_decisions": 20, "dpll_decisions_pure_literal": 18, "polarity_witness": "111000000001", "polarity_violations": 1, "greedy_witness": "111110010011", "greedy_violations": 3, "dpll_witness": "010100100101"}`
- *notes:* Same formula as E1-SAT-x.

</details>

<details><summary>Prompt and computed outputs — <code>E1-SAT-B1-x</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x07 ∨ x04 ∨ ¬x01)
C02: (x10 ∨ x07 ∨ ¬x01)
C03: (¬x11 ∨ ¬x02)
C04: (x04 ∨ ¬x08 ∨ x11)
C05: (¬x07 ∨ x05 ∨ ¬x02)
C06: (x02 ∨ ¬x05 ∨ ¬x04)
C07: (x01 ∨ ¬x08 ∨ ¬x07)
C08: (¬x12 ∨ ¬x04)
C09: (¬x06)
C10: (¬x07 ∨ ¬x10 ∨ ¬x03)
C11: (x10 ∨ x01 ∨ ¬x11)
C12: (x01 ∨ ¬x07 ∨ x11)
C13: (x10 ∨ ¬x09)
C14: (x05 ∨ x03)
C15: (¬x12 ∨ x01 ∨ ¬x03)
C16: (¬x09 ∨ x04 ∨ x07)
C17: (x02 ∨ ¬x12 ∨ x10)
C18: (¬x06 ∨ x02 ∨ ¬x01)
C19: (x05 ∨ ¬x12 ∨ x04)
C20: (¬x09 ∨ ¬x08 ∨ ¬x03)
C21: (x08 ∨ x09 ∨ x03)
C22: (¬x04 ∨ x01 ∨ x12)
C23: (¬x02 ∨ ¬x12 ∨ ¬x03)
C24: (¬x09 ∨ x07 ∨ x03)
C25: (x07 ∨ ¬x01 ∨ x06)
C26: (¬x08 ∨ x09)
C27: (x12 ∨ x09)
C28: (¬x08 ∨ ¬x02 ∨ x12)
C29: (x03 ∨ ¬x04 ∨ ¬x02)
C30: (¬x02 ∨ x05 ∨ x03)
C31: (¬x02 ∨ x08 ∨ ¬x11)
C32: (x09 ∨ ¬x12 ∨ x11)
C33: (x10 ∨ ¬x07 ∨ ¬x02)
C34: (x08 ∨ ¬x11 ∨ ¬x06)
C35: (¬x06 ∨ ¬x07)
C36: (¬x08)
C37: (x12 ∨ x03 ∨ x10)
C38: (¬x09 ∨ x03 ∨ x02)
C39: (¬x04 ∨ ¬x05 ∨ x11)
C40: (x06 ∨ x03 ∨ x01)
C41: (x09 ∨ x03 ∨ x04)
C42: (x11 ∨ ¬x10 ∨ x07)
C43: (x05 ∨ x08 ∨ x01)
C44: (¬x07 ∨ ¬x10 ∨ x02)
C45: (x04 ∨ ¬x11 ∨ x08)
C46: (¬x06 ∨ ¬x12 ∨ x11)
C47: (¬x10 ∨ x09 ∨ ¬x01)
C48: (¬x02 ∨ x01)
C49: (¬x12 ∨ x08 ∨ ¬x09)
C50: (¬x10 ∨ x03 ∨ ¬x08)
C51: (¬x03 ∨ ¬x12 ∨ ¬x04)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** SAT, e.g. 110010101100 (1 solution)
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 6.4 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** SAT (α_U = 4.25 vs θ = 4.26)
- **A2 DENSITY-D:** SAT (α_D = 4.25 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 51 vs illustrative θ_m = 50)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 6.4 clauses
- **H SAMPLE-8:** P(SAT) = 0.002 (1 solutions in 2^12)
- **NOISY-EXACT-STEP:** SAT w.p. 0.98 (L = 2 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** SAT w.p. 0.80 (L = m = 51, p = 0.01/clause)
- **PERCEPTION-NOISE:** SAT (dropped clauses cannot remove solutions)
- **C0 POLARITY:** SAT, witness 101110001110 (2 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 101100101110 violates 2)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** SAT (exact: 2 decisions ≤ illustrative b = 8)
- **F WALK-200:** SAT in 73% of runs, else UNSAT by default
- **D∘DENSITY (b=4):** SAT (search finishes in 2 ≤ 4 decisions)
- *params:* `{"n_used": 12, "n_decl": 12, "m": 51, "alpha_U": 4.25, "alpha_D": 4.25, "n_solutions": 1, "dpll_decisions": 2, "dpll_decisions_pure_literal": 2, "polarity_witness": "101110001110", "polarity_violations": 2, "greedy_witness": "101100101110", "greedy_violations": 2, "dpll_witness": "110010101100", "edit": "swap the signs of x08 in C21 and C36"}`
- *notes:* B1 stratum: 50 pairs in the study.

</details>

<details><summary>Prompt and computed outputs — <code>E1-SAT-B1-x'</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x07 ∨ x04 ∨ ¬x01)
C02: (x10 ∨ x07 ∨ ¬x01)
C03: (¬x11 ∨ ¬x02)
C04: (x04 ∨ ¬x08 ∨ x11)
C05: (¬x07 ∨ x05 ∨ ¬x02)
C06: (x02 ∨ ¬x05 ∨ ¬x04)
C07: (x01 ∨ ¬x08 ∨ ¬x07)
C08: (¬x12 ∨ ¬x04)
C09: (¬x06)
C10: (¬x07 ∨ ¬x10 ∨ ¬x03)
C11: (x10 ∨ x01 ∨ ¬x11)
C12: (x01 ∨ ¬x07 ∨ x11)
C13: (x10 ∨ ¬x09)
C14: (x05 ∨ x03)
C15: (¬x12 ∨ x01 ∨ ¬x03)
C16: (¬x09 ∨ x04 ∨ x07)
C17: (x02 ∨ ¬x12 ∨ x10)
C18: (¬x06 ∨ x02 ∨ ¬x01)
C19: (x05 ∨ ¬x12 ∨ x04)
C20: (¬x09 ∨ ¬x08 ∨ ¬x03)
C21: (¬x08 ∨ x09 ∨ x03)
C22: (¬x04 ∨ x01 ∨ x12)
C23: (¬x02 ∨ ¬x12 ∨ ¬x03)
C24: (¬x09 ∨ x07 ∨ x03)
C25: (x07 ∨ ¬x01 ∨ x06)
C26: (¬x08 ∨ x09)
C27: (x12 ∨ x09)
C28: (¬x08 ∨ ¬x02 ∨ x12)
C29: (x03 ∨ ¬x04 ∨ ¬x02)
C30: (¬x02 ∨ x05 ∨ x03)
C31: (¬x02 ∨ x08 ∨ ¬x11)
C32: (x09 ∨ ¬x12 ∨ x11)
C33: (x10 ∨ ¬x07 ∨ ¬x02)
C34: (x08 ∨ ¬x11 ∨ ¬x06)
C35: (¬x06 ∨ ¬x07)
C36: (x08)
C37: (x12 ∨ x03 ∨ x10)
C38: (¬x09 ∨ x03 ∨ x02)
C39: (¬x04 ∨ ¬x05 ∨ x11)
C40: (x06 ∨ x03 ∨ x01)
C41: (x09 ∨ x03 ∨ x04)
C42: (x11 ∨ ¬x10 ∨ x07)
C43: (x05 ∨ x08 ∨ x01)
C44: (¬x07 ∨ ¬x10 ∨ x02)
C45: (x04 ∨ ¬x11 ∨ x08)
C46: (¬x06 ∨ ¬x12 ∨ x11)
C47: (¬x10 ∨ x09 ∨ ¬x01)
C48: (¬x02 ∨ x01)
C49: (¬x12 ∨ x08 ∨ ¬x09)
C50: (¬x10 ∨ x03 ∨ ¬x08)
C51: (¬x03 ∨ ¬x12 ∨ ¬x04)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** UNSAT
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 6.4 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** SAT (α_U = 4.25 vs θ = 4.26)
- **A2 DENSITY-D:** SAT (α_D = 4.25 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 51 vs illustrative θ_m = 50)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 6.4 clauses
- **H SAMPLE-8:** P(SAT) = 0.000 (0 solutions in 2^12)
- **NOISY-EXACT-STEP:** UNSAT w.p. 0.99 (L = 0 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** UNSAT w.p. 0.80 (L = m = 51, p = 0.01/clause)
- **PERCEPTION-NOISE:** P(SAT) = 0.081 at p_d = 0.05 (1 necessary clauses)
- **C0 POLARITY:** SAT, witness 101110001110 (3 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 101100111110 violates 3)
- **B1 UP-3:** UNSAT (refuted)
- **D DPLL-b:** UNSAT (exact: 0 decisions ≤ illustrative b = 8)
- **F WALK-200:** UNSAT by default (never certifies)
- **D∘DENSITY (b=4):** UNSAT (search finishes in 0 ≤ 4 decisions)
- *params:* `{"n_used": 12, "n_decl": 12, "m": 51, "alpha_U": 4.25, "alpha_D": 4.25, "n_solutions": 0, "dpll_decisions": 0, "dpll_decisions_pure_literal": 0, "polarity_witness": "101110001110", "polarity_violations": 3, "greedy_witness": "101100111110", "greedy_violations": 3, "dpll_witness": null, "edit": "swap the signs of x08 in C21 and C36"}`
- *notes:* B1 stratum: 50 pairs in the study.

</details>

**Hypothesis matrix**

| Theory | (a) `E1-SAT-x` | (a) `E1-SAT-x'` | (a) `E1-SAT-null1` | (a) `E1-SAT-null2` | (a) `E1-SAT-x-menu` | (a) `E1-SAT-B1-x` | (a) `E1-SAT-B1-x'` | (b) pure-theory statistic · weight resolution | (c) predicted trace |
|---|---|---|---|---|---|---|---|---|---|
| exact | SAT | UNSAT | SAT | SAT | SAT | SAT | UNSAT | D = P(SAT\|x) − P(SAT\|x′) = +1.00. Detectable π ≥ 0.26 vs F WALK-200 | A completed procedure: a witness checked against every constraint, or a closed refutation / exhaustive case split. No cue given as a reason. |
| A1 ALWAYS-SAT | SAT | SAT | SAT | SAT | SAT | SAT | SAT | D = P(SAT\|x) − P(SAT\|x′) = +0.00. Detectable π ≥ 0.09 vs B1 UP-3 | A witness proposed without checking every constraint; no attempt at refutation. |
| A1 ALWAYS-UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | D = P(SAT\|x) − P(SAT\|x′) = +0.00. Detectable π ≥ 0.26 vs C1 GREEDY | GIVEUP early ('too many constraints to check'); no witness attempted. |
| A2 DENSITY-U | SAT | SAT | SAT | SAT | SAT | SAT | SAT | D = P(SAT\|x) − P(SAT\|x′) = +0.00. Detectable π ≥ 0.09 vs B1 UP-3 | CUE-DENS as the reason ('about 4.3 clauses per variable is near the hard threshold'); no closed refutation; padding variables not treated specially. |
| A2 LENGTH-M | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | D = P(SAT\|x) − P(SAT\|x′) = +0.00. Detectable π ≥ 0.26 vs C1 GREEDY | CUE-SIZE as the reason ('with this many clauses it is very likely unsatisfiable'). |
| H RANDOM-U | SAT or UNSAT w.p. ½; a random witness violates ≈ 6.4 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 6.4 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 6.4 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 6.4 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 6.4 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 6.4 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 6.4 clauses | D = P(SAT\|x) − P(SAT\|x′) = +0.00. Detectable π ≥ 0.04 vs NOISY-EXACT-STEP | No procedure determines the verdict; trace content and verdict unrelated. |
| H SAMPLE-8 | P(SAT) = 0.002 | P(SAT) = 0.000 | P(SAT) = 0.014 | P(SAT) = 0.004 | P(SAT) = 0.002 | P(SAT) = 0.002 | P(SAT) = 0.000 | D = P(SAT\|x) − P(SAT\|x′) = +0.00. Detectable π ≥ 0.26 vs C1 GREEDY | SAMPLE(k): at most 8 concrete cases checked, then a universal conclusion; no exhaustive split. |
| NOISY-EXACT-STEP | SAT w.p. 0.83 | UNSAT w.p. 0.85 | SAT w.p. 0.94 | SAT w.p. 0.98 | SAT w.p. 0.83 | SAT w.p. 0.98 | UNSAT w.p. 0.99 | D = P(SAT\|x) − P(SAT\|x′) = +0.68. Detectable π ≥ 0.13 vs F WALK-200 | A systematic procedure; an EVALSLIP (a constraint evaluated wrongly under the trace's own assignment) precedes every error. |
| PERCEPTION-NOISE | SAT | P(SAT) = 0.321 | SAT | SAT | SAT | SAT | P(SAT) = 0.081 | D = P(SAT\|x) − P(SAT\|x′) = +0.68. Detectable π ≥ 0.17 vs NOISY-EXACT-STEP | A MISQUOTE of a constraint (a dropped ¬, a wrong pair, a missing clause); later reasoning consistent with the misquote. |
| C0 POLARITY | SAT | SAT | SAT | SAT | SAT | SAT | SAT | D = P(SAT\|x) − P(SAT\|x′) = +0.00. Detectable π ≥ 0.01 vs A1 ALWAYS-SAT | A witness built in one step from majority signs; no search. |
| C1 GREEDY | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | D = P(SAT\|x) − P(SAT\|x′) = +0.00. Detectable π ≥ 0.27 vs A1 ALWAYS-UNSAT | One ASSIGN pass in index order, no BACKTRACK; at a dead end, GIVEUP or an invalid witness. |
| B1 UP-3 | SAT | SAT | SAT | SAT | SAT | SAT | UNSAT | D = P(SAT\|x) − P(SAT\|x′) = +0.00. Detectable π ≥ 0.09 vs A1 ALWAYS-SAT | PROP only: derived literals listed; no case split; stops when nothing more is forced. |
| D DPLL-b | UNSAT | UNSAT | SAT | SAT | UNSAT | SAT | UNSAT | D = P(SAT\|x) − P(SAT\|x′) = +0.00. Detectable π ≥ 0.09 vs H SAMPLE-8 | BRANCH / CONTRA / BACKTRACK; ends in a witness, a closed refutation, or the cap. |
| F WALK-200 | SAT in 83% of runs | UNSAT | SAT in 100% of runs | SAT in 90% of runs | SAT in 83% of runs | SAT in 73% of runs | UNSAT | D = P(SAT\|x) − P(SAT\|x′) = +0.83. Detectable π ≥ 0.24 vs NOISY-EXACT-STEP | REPAIR loops: a full candidate, its violated clauses listed, flips; never a refutation. |

*(c) for every theory: the expected share of traces showing the signature ≈ π_h · r̂ (faithfulness, from E8), plus the coder's false-positive rate.*

**Likelihood ratios per observable pattern** (log₁₀ LR; one study unit)

| Pattern | Favours (log₁₀ LR vs the best theory outside the favoured group) | Pushes toward zero weight (log₁₀ LR vs the best theory) |
|---|---|---|
| x: SAT, x′: UNSAT (both right) | exact (+0.6), F WALK-200 (+0.5), NOISY-EXACT-STEP (+0.5), PERCEPTION-NOISE (+0.4) | A1 ALWAYS-SAT (-1.3), A1 ALWAYS-UNSAT (-1.3), A2 DENSITY-U (-1.3), A2 LENGTH-M (-1.3), H SAMPLE-8 (-1.3), C0 POLARITY (-1.3), C1 GREEDY (-1.3), B1 UP-3 (-1.3), D DPLL-b (-1.3) |
| x: SAT, x′: SAT | A1 ALWAYS-SAT (+0.5), A2 DENSITY-U (+0.5), C0 POLARITY (+0.5), B1 UP-3 (+0.5) | A1 ALWAYS-UNSAT (-2.6), A2 LENGTH-M (-2.6), H SAMPLE-8 (-2.6), C1 GREEDY (-2.6), D DPLL-b (-2.6), F WALK-200 (-1.3), exact (-1.3) |
| x: UNSAT, x′: UNSAT | A1 ALWAYS-UNSAT (+0.6), A2 LENGTH-M (+0.6), H SAMPLE-8 (+0.6), C1 GREEDY (+0.6), D DPLL-b (+0.6) | A1 ALWAYS-SAT (-2.6), A2 DENSITY-U (-2.6), C0 POLARITY (-2.6), B1 UP-3 (-2.6), PERCEPTION-NOISE (-1.4), exact (-1.3) |
| x: UNSAT, x′: SAT (both wrong) | H RANDOM-U (+0.7) | exact (-2.0), F WALK-200 (-1.5), PERCEPTION-NOISE (-1.2) |
| x: SAT + POLARITY witness | C0 POLARITY (+2.0) | exact (-2.0), A1 ALWAYS-SAT (-2.0), A1 ALWAYS-UNSAT (-2.0), A2 DENSITY-U (-2.0), A2 LENGTH-M (-2.0), H RANDOM-U (-2.0), H SAMPLE-8 (-2.0), PERCEPTION-NOISE (-2.0), C1 GREEDY (-2.0), B1 UP-3 (-2.0), D DPLL-b (-2.0), F WALK-200 (-2.0), NOISY-EXACT-STEP (-2.0) |
| x: SAT + GREEDY witness | C1 GREEDY (+0.8) | — |
| x: SAT + DPLL witness | exact (+1.3), PERCEPTION-NOISE (+1.3), F WALK-200 (+1.2), NOISY-EXACT-STEP (+1.2) | A1 ALWAYS-SAT (-2.1), A1 ALWAYS-UNSAT (-2.1), A2 DENSITY-U (-2.1), A2 LENGTH-M (-2.1), H RANDOM-U (-2.1), C1 GREEDY (-2.1), B1 UP-3 (-2.1), C0 POLARITY (-2.0), D DPLL-b (-1.3), H SAMPLE-8 (-1.3) |
| x: SAT + other valid witness | exact (+9.9), A1 ALWAYS-SAT (+9.9), A1 ALWAYS-UNSAT (+9.9), A2 DENSITY-U (+9.9), A2 LENGTH-M (+9.9), H RANDOM-U (+9.9), H SAMPLE-8 (+9.9), NOISY-EXACT-STEP (+9.9), PERCEPTION-NOISE (+9.9), C0 POLARITY (+9.9), C1 GREEDY (+9.9), B1 UP-3 (+9.9), D DPLL-b (+9.9), F WALK-200 (+9.9) | — |
| x: SAT + other invalid witness | A1 ALWAYS-SAT (+1.1), A2 DENSITY-U (+1.1), B1 UP-3 (+1.1), H RANDOM-U (+0.8) | exact (-2.1), H SAMPLE-8 (-2.1), PERCEPTION-NOISE (-2.1), C1 GREEDY (-2.1), D DPLL-b (-2.1), F WALK-200 (-2.1), C0 POLARITY (-1.3), A1 ALWAYS-UNSAT (-1.3), A2 LENGTH-M (-1.3), NOISY-EXACT-STEP (-1.1) |
| B1 stratum: x SAT, x′ UNSAT | exact (+0.6), NOISY-EXACT-STEP (+0.6), B1 UP-3 (+0.6), D DPLL-b (+0.6), PERCEPTION-NOISE (+0.5), F WALK-200 (+0.5) | A1 ALWAYS-SAT (-1.3), A1 ALWAYS-UNSAT (-1.3), A2 DENSITY-U (-1.3), A2 LENGTH-M (-1.3), H SAMPLE-8 (-1.3), C0 POLARITY (-1.3), C1 GREEDY (-1.3) |
| B1 stratum: both SAT | A1 ALWAYS-SAT (+0.6), A2 DENSITY-U (+0.6), C0 POLARITY (+0.6) | A1 ALWAYS-UNSAT (-2.6), A2 LENGTH-M (-2.6), H SAMPLE-8 (-2.6), C1 GREEDY (-2.6), F WALK-200 (-1.4), exact (-1.3), NOISY-EXACT-STEP (-1.3), B1 UP-3 (-1.3), D DPLL-b (-1.3), PERCEPTION-NOISE (-1.1) |

**Weight resolution at study N**

| Theory | Nearest competitor (smallest KL) | Detectable π vs it (80% power) | Upper 95% bound on π if pure competitor | E[log₁₀ BF] vs competitor | Detectable π if the rest is the hardest base (which) | Identical predictions here |
|---|---|---|---|---|---|---|
| exact | F WALK-200 | 0.263 | 0.174 | 25.5 | 0.263 (F WALK-200) | — |
| A1 ALWAYS-SAT | B1 UP-3 | 0.085 | 0.056 | 57.5 | 0.085 (B1 UP-3) | A2 DENSITY-U |
| A1 ALWAYS-UNSAT | C1 GREEDY | 0.258 | 0.171 | 12.2 | 0.258 (C1 GREEDY) | A2 LENGTH-M |
| A2 DENSITY-U | B1 UP-3 | 0.085 | 0.056 | 57.5 | 0.085 (B1 UP-3) | A1 ALWAYS-SAT |
| A2 LENGTH-M | C1 GREEDY | 0.258 | 0.171 | 12.2 | 0.258 (C1 GREEDY) | A1 ALWAYS-UNSAT |
| H RANDOM-U | NOISY-EXACT-STEP | 0.041 | 0.027 | 380.1 | 0.041 (NOISY-EXACT-STEP) | — |
| H SAMPLE-8 | C1 GREEDY | 0.258 | 0.171 | 12.2 | 0.258 (C1 GREEDY) | — |
| NOISY-EXACT-STEP | F WALK-200 | 0.129 | 0.086 | 36.8 | 0.129 (F WALK-200) | — |
| PERCEPTION-NOISE | NOISY-EXACT-STEP | 0.170 | 0.113 | 49.5 | 0.170 (NOISY-EXACT-STEP) | — |
| C0 POLARITY | A1 ALWAYS-SAT | 0.013 | 0.008 | 693.8 | 0.013 (A1 ALWAYS-SAT) | — |
| C1 GREEDY | A1 ALWAYS-UNSAT | 0.270 | 0.178 | 11.8 | 0.270 (A1 ALWAYS-UNSAT) | — |
| B1 UP-3 | A1 ALWAYS-SAT | 0.085 | 0.056 | 57.5 | 0.085 (A1 ALWAYS-SAT) | — |
| D DPLL-b | H SAMPLE-8 | 0.085 | 0.056 | 57.6 | 0.085 (H SAMPLE-8) | — |
| F WALK-200 | NOISY-EXACT-STEP | 0.236 | 0.156 | 24.8 | 0.236 (NOISY-EXACT-STEP) | — |

**Not separated here.** The decision channel alone cannot split the blind theories (ALWAYS-SAT, DENSITY-U, LENGTH-M, C0 POLARITY, B1 UP-3 all answer alike on x and x′). The witness channel on x separates C0 POLARITY (its own witness) and C1 / D (their own witnesses) from fill-based theories, and the UP-refutable stratum separates B1 UP-3. DENSITY vs LENGTH vs ALWAYS-SAT need E2 and E3. RANDOM is separated from the deterministic blind theories by test–retest (second sample).

<a id="e1-ent"></a>
## E1: entailment structure-blindness minimal pair

**Reasoning question.** Is 'follows' sensitive to a structural edit that is invisible to every A2 cue?

**Design.** P and P′ differ in which premise carries the negation of an atom not in C; C follows from P by one propagation step beyond the facts.  *Study units:* critical pair (P, P′), one-step propagation stratum × 100.

| Item | Cell | Ground truth | Controlled | Varied |
|---|---|---|---|---|
| `E1-ENT-P` | critical, entailed member (P) | follows | signed-literal FREQ, total and per-premise negation counts, connectives, premise positions and word counts, C's overlap with every premise | which premise carries the negation of an atom that is not in C (flips entailment) |
| `E1-ENT-P'` | critical, non-entailed member (P′) | does not follow | signed-literal FREQ, total and per-premise negation counts, connectives, premise positions and word counts, C's overlap with every premise | which premise carries the negation of an atom that is not in C (flips entailment) |

<details><summary>Prompt and computed outputs — <code>E1-ENT-P</code></summary>

```text
Here are some facts about a machine.

- Either the lamp is not lit, or the alarm is not armed.
- Either the alarm is not armed, or the lamp is lit and the bell is not ringing.
- Either the bell is not ringing and the lamp is lit, or the bell is ringing.
- The bell is not ringing.

Question: Does it follow from these facts that the lamp is lit?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** follows
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** follows (literal counts [2]; min vs illustrative θ = 2)
- **A2 ATMOSPHERE:** does not follow (atm(P) = disj/neg, mood(C) = conj/pos)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 1.000 (ρ = 0.000)
- **NOISY-EXACT:** follows w.p. 0.90
- **PERCEPTION-NOISE:** follows unless a misread breaks it: P(does not follow) = 0.067
- **B1 UP-1:** follows (1 propagation step(s) beyond the facts)
- **B1 UP-2:** follows (1 propagation step(s) beyond the facts)
- **B4 ETR:** follows (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** does not follow
- **B4 MATCH:** does not follow
- **D case-split (b = 4):** follows
- *params:* `{"atoms": 6, "rho": 0.0, "n_models": 8, "up_depth": 2, "kappa_follow": 0.556, "kappa_break": 0.333, "eta_first_counter": null, "etr_what_follows": "{a2()~a5()}", "edit": "the negation on 'the bell is ringing' moves from premise 2 to premise 3", "propagation_steps_beyond_facts": 1}`
- *notes:* one-step propagation stratum; the edited atom is not in C. A2 outputs asserted equal on P and P′.

</details>

<details><summary>Prompt and computed outputs — <code>E1-ENT-P'</code></summary>

```text
Here are some facts about a machine.

- Either the lamp is not lit, or the alarm is not armed.
- Either the alarm is not armed, or the lamp is lit and the bell is ringing.
- Either the bell is not ringing and the lamp is lit, or the bell is not ringing.
- The bell is not ringing.

Question: Does it follow from these facts that the lamp is lit?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** does not follow
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** follows (literal counts [2]; min vs illustrative θ = 2)
- **A2 ATMOSPHERE:** does not follow (atm(P) = disj/neg, mood(C) = conj/pos)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 0.004 (ρ = 0.500)
- **NOISY-EXACT:** does not follow w.p. 0.90
- **PERCEPTION-NOISE:** does not follow unless a misread makes it follow: P(follows) = 0.022
- **B1 UP-1:** does not follow (not UP-derivable)
- **B1 UP-2:** does not follow (not UP-derivable)
- **B4 ETR:** follows (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** does not follow
- **B4 MATCH:** does not follow
- **D case-split (b = 4):** follows (first counter-model is #5 of 16 in atom order; budget 4 cases)
- *params:* `{"atoms": 6, "rho": 0.5, "n_models": 16, "up_depth": null, "kappa_follow": 0.111, "kappa_break": 0.778, "eta_first_counter": 5, "etr_what_follows": "{a2()~a5()}", "edit": "the negation on 'the bell is ringing' moves from premise 2 to premise 3", "propagation_steps_beyond_facts": null}`
- *notes:* one-step propagation stratum; the edited atom is not in C. A2 outputs asserted equal on P and P′.

</details>

**Hypothesis matrix**

| Theory | (a) `E1-ENT-P` | (a) `E1-ENT-P'` | (b) pure-theory statistic · weight resolution | (c) predicted trace |
|---|---|---|---|---|
| exact | follows | does not follow | D = P(follows\|P) − P(follows\|P′) = +1.00. π unresolved here vs PERCEPTION-NOISE | A completed procedure: a witness checked against every constraint, or a closed refutation / exhaustive case split. No cue given as a reason. |
| A1 ALWAYS-YES | follows | follows | D = P(follows\|P) − P(follows\|P′) = +0.00. Detectable π ≥ 0.17 vs H RANDOM-U | The conclusion asserted with no derivation and no search for a counter-model. |
| A1 NONE | does not follow | does not follow | D = P(follows\|P) − P(follows\|P′) = +0.00. Detectable π ≥ 0.17 vs H RANDOM-U | 'Nothing definite follows', with no case analysis. |
| A2 FREQ | follows | follows | D = P(follows\|P) − P(follows\|P′) = +0.00. Detectable π ≥ 0.17 vs H RANDOM-U | CUE-FREQ ('the bell ringing comes up most often'). |
| A2 ATMOSPHERE | does not follow | does not follow | D = P(follows\|P) − P(follows\|P′) = +0.00. Detectable π ≥ 0.17 vs H RANDOM-U | CUE-MOOD: the conclusion's form or polarity matched to the premises without a derivation. |
| A2 PRIMACY | does not follow | does not follow | D = P(follows\|P) − P(follows\|P′) = +0.00. Detectable π ≥ 0.17 vs H RANDOM-U | CUE-POS on the first premise or option; other options not evaluated. |
| A2 RECENCY | does not follow | does not follow | D = P(follows\|P) − P(follows\|P′) = +0.00. Detectable π ≥ 0.17 vs H RANDOM-U | CUE-POS on the last premise or option. |
| H RANDOM-U | follows w.p. ½ | follows w.p. ½ | D = P(follows\|P) − P(follows\|P′) = +0.00. Detectable π ≥ 0.10 vs NOISY-EXACT | No procedure determines the verdict; trace content and verdict unrelated. |
| H SAMPLE-8 | follows w.p. 1.000 | follows w.p. 0.004 | D = P(follows\|P) − P(follows\|P′) = +1.00. π unresolved here vs PERCEPTION-NOISE | SAMPLE(k): at most 8 concrete cases checked, then a universal conclusion; no exhaustive split. |
| NOISY-EXACT | follows w.p. 0.90 | does not follow w.p. 0.90 | D = P(follows\|P) − P(follows\|P′) = +0.80. Detectable π ≥ 0.93 vs PERCEPTION-NOISE | A systematic procedure; an EVALSLIP precedes every error. |
| PERCEPTION-NOISE | follows | does not follow | D = P(follows\|P) − P(follows\|P′) = +0.91. π unresolved here vs exact | A MISQUOTE of a constraint (a dropped ¬, a wrong pair, a missing clause); later reasoning consistent with the misquote. |
| B1 UP-1 | follows | does not follow | D = P(follows\|P) − P(follows\|P′) = +1.00. π unresolved here vs PERCEPTION-NOISE | PROP only, one round. |
| B1 UP-2 | follows | does not follow | D = P(follows\|P) − P(follows\|P′) = +1.00. π unresolved here vs PERCEPTION-NOISE | PROP only, two rounds; no case split. |
| B4 ETR | follows | follows | D = P(follows\|P) − P(follows\|P′) = +0.00. Detectable π ≥ 0.17 vs H RANDOM-U | COMMIT-DISJ / TRUE-ONLY: the disjunct matching the categorical fact kept, the others dropped. |
| B4 FIRST | does not follow | does not follow | D = P(follows\|P) − P(follows\|P′) = +0.00. Detectable π ≥ 0.17 vs H RANDOM-U | COMMIT-DISJ on each first disjunct, never revisited. |
| B4 MATCH | does not follow | does not follow | D = P(follows\|P) − P(follows\|P′) = +0.00. Detectable π ≥ 0.17 vs H RANDOM-U | Picks the disjunct that shares atoms with the categorical fact. |
| D case-split (b = 4) | follows | follows | D = P(follows\|P) − P(follows\|P′) = +0.00. Detectable π ≥ 0.17 vs H RANDOM-U | A systematic case split abandoned after ≈ 4 cases; 'follows' if no counter-model was found. |

*(c) for every theory: the expected share of traces showing the signature ≈ π_h · r̂ (faithfulness, from E8), plus the coder's false-positive rate.*

**Likelihood ratios per observable pattern** (log₁₀ LR; one study unit)

| Pattern | Favours (log₁₀ LR vs the best theory outside the favoured group) | Pushes toward zero weight (log₁₀ LR vs the best theory) |
|---|---|---|
| P: follows, P′: not (both right) | exact (+0.6), H SAMPLE-8 (+0.6), B1 UP-1 (+0.6), B1 UP-2 (+0.6), PERCEPTION-NOISE (+0.6), NOISY-EXACT (+0.5) | A1 ALWAYS-YES (-1.3), A1 NONE (-1.3), A2 FREQ (-1.3), A2 ATMOSPHERE (-1.3), A2 PRIMACY (-1.3), A2 RECENCY (-1.3), B4 ETR (-1.3), B4 FIRST (-1.3), B4 MATCH (-1.3), D case-split (b = 4) (-1.3) |
| P: follows, P′: follows (commission on P′) | A1 ALWAYS-YES (+0.6), A2 FREQ (+0.6), B4 ETR (+0.6), D case-split (b = 4) (+0.6) | A1 NONE (-2.6), A2 ATMOSPHERE (-2.6), A2 PRIMACY (-2.6), A2 RECENCY (-2.6), B4 FIRST (-2.6), B4 MATCH (-2.6), PERCEPTION-NOISE (-1.3), exact (-1.3), H SAMPLE-8 (-1.3), B1 UP-1 (-1.3), B1 UP-2 (-1.3), NOISY-EXACT (-1.0) |
| P: not, P′: not (omission on P) | A1 NONE (+0.6), A2 ATMOSPHERE (+0.6), A2 PRIMACY (+0.6), A2 RECENCY (+0.6), B4 FIRST (+0.6), B4 MATCH (+0.6) | A1 ALWAYS-YES (-2.6), A2 FREQ (-2.6), B4 ETR (-2.6), D case-split (b = 4) (-2.6), exact (-1.3), H SAMPLE-8 (-1.3), B1 UP-1 (-1.3), B1 UP-2 (-1.3), PERCEPTION-NOISE (-1.1), NOISY-EXACT (-1.0) |
| P: not, P′: follows (both wrong) | H RANDOM-U (+0.7) | exact (-2.0), H SAMPLE-8 (-2.0), B1 UP-1 (-2.0), B1 UP-2 (-2.0), PERCEPTION-NOISE (-1.9), NOISY-EXACT (-1.4) |

**Weight resolution at study N**

| Theory | Nearest competitor (smallest KL) | Detectable π vs it (80% power) | Upper 95% bound on π if pure competitor | E[log₁₀ BF] vs competitor | Detectable π if the rest is the hardest base (which) | Identical predictions here |
|---|---|---|---|---|---|---|
| exact | PERCEPTION-NOISE | > 1 (unresolved at this N) | > 1 (unresolved at this N) | 0.1 | > 1 (unresolved at this N) (PERCEPTION-NOISE) | H SAMPLE-8, B1 UP-1, B1 UP-2 |
| A1 ALWAYS-YES | H RANDOM-U | 0.165 | 0.109 | 43.0 | 0.165 (H RANDOM-U) | A2 FREQ, B4 ETR, D case-split (b = 4) |
| A1 NONE | H RANDOM-U | 0.165 | 0.109 | 43.0 | 0.165 (H RANDOM-U) | A2 ATMOSPHERE, A2 PRIMACY, A2 RECENCY, B4 FIRST, B4 MATCH |
| A2 FREQ | H RANDOM-U | 0.165 | 0.109 | 43.0 | 0.165 (H RANDOM-U) | A1 ALWAYS-YES, B4 ETR, D case-split (b = 4) |
| A2 ATMOSPHERE | H RANDOM-U | 0.165 | 0.109 | 43.0 | 0.165 (H RANDOM-U) | A1 NONE, A2 PRIMACY, A2 RECENCY, B4 FIRST, B4 MATCH |
| A2 PRIMACY | H RANDOM-U | 0.165 | 0.109 | 43.0 | 0.165 (H RANDOM-U) | A1 NONE, A2 ATMOSPHERE, A2 RECENCY, B4 FIRST, B4 MATCH |
| A2 RECENCY | H RANDOM-U | 0.165 | 0.109 | 43.0 | 0.165 (H RANDOM-U) | A1 NONE, A2 ATMOSPHERE, A2 PRIMACY, B4 FIRST, B4 MATCH |
| H RANDOM-U | NOISY-EXACT | 0.096 | 0.063 | 44.4 | 0.096 (NOISY-EXACT) | — |
| H SAMPLE-8 | PERCEPTION-NOISE | > 1 (unresolved at this N) | > 1 (unresolved at this N) | 0.1 | > 1 (unresolved at this N) (PERCEPTION-NOISE) | exact, B1 UP-1, B1 UP-2 |
| NOISY-EXACT | PERCEPTION-NOISE | 0.930 | 0.616 | 1.2 | 0.930 (PERCEPTION-NOISE) | — |
| PERCEPTION-NOISE | exact | > 1 (unresolved at this N) | > 1 (unresolved at this N) | 0.1 | > 1 (unresolved at this N) (exact) | — |
| B1 UP-1 | PERCEPTION-NOISE | > 1 (unresolved at this N) | > 1 (unresolved at this N) | 0.1 | > 1 (unresolved at this N) (PERCEPTION-NOISE) | exact, H SAMPLE-8, B1 UP-2 |
| B1 UP-2 | PERCEPTION-NOISE | > 1 (unresolved at this N) | > 1 (unresolved at this N) | 0.1 | > 1 (unresolved at this N) (PERCEPTION-NOISE) | exact, H SAMPLE-8, B1 UP-1 |
| B4 ETR | H RANDOM-U | 0.165 | 0.109 | 43.0 | 0.165 (H RANDOM-U) | A1 ALWAYS-YES, A2 FREQ, D case-split (b = 4) |
| B4 FIRST | H RANDOM-U | 0.165 | 0.109 | 43.0 | 0.165 (H RANDOM-U) | A1 NONE, A2 ATMOSPHERE, A2 PRIMACY, A2 RECENCY, B4 MATCH |
| B4 MATCH | H RANDOM-U | 0.165 | 0.109 | 43.0 | 0.165 (H RANDOM-U) | A1 NONE, A2 ATMOSPHERE, A2 PRIMACY, A2 RECENCY, B4 FIRST |
| D case-split (b = 4) | H RANDOM-U | 0.165 | 0.109 | 43.0 | 0.165 (H RANDOM-U) | A1 ALWAYS-YES, A2 FREQ, B4 ETR |

**Not separated here.** The A2 cues, ALWAYS-* and RANDOM give each member the same answer by construction; E2-ENT (matched conclusions) and E4 separate the cues from one another. Only the one-step propagation stratum is shown (N = 100 of the study's 400 critical pairs); the study adds two-step, ≥ 3-step and 'not UP-derivable' strata. UP-1 vs UP-2 is separated in E4-order (two steps).

<a id="e2-sat"></a>
## E2: satisfiability-neutral padding (base / K / J / U × SAT / UNSAT core)

**Reasoning question.** Does α move the decision when g, m and pure-literal-reduced hardness are fixed?

**Design.** K and J add the same 14 clauses (same core literals, same positions); only the number of fresh pure variables differs (2 vs 7). U adds 4 declared, unused variables.  *Study units:* SAT base: (base, K, J, U) × 150; UNSAT base: (base, K, J, U) × 150.

| Item | Cell | Ground truth | Controlled | Varied |
|---|---|---|---|---|
| `E2-SAT-base` | base, g = SAT | SAT | core clauses and their positions; the padding clauses' core literals and positions are identical in K and J; 7 of 14 fresh literals negated in both; fixed-width names | core only |
| `E2-SAT-K` | K, g = SAT | SAT | core clauses and their positions; the padding clauses' core literals and positions are identical in K and J; 7 of 14 fresh literals negated in both; fixed-width names | +14 clauses carrying 2 fresh pure variables (α ↑, m ↑) |
| `E2-SAT-J` | J, g = SAT | SAT | core clauses and their positions; the padding clauses' core literals and positions are identical in K and J; 7 of 14 fresh literals negated in both; fixed-width names | the same 14 clauses carrying 7 fresh pure variables (α ↓, m ↑ by the same 14) |
| `E2-SAT-U` | U, g = SAT | SAT | core clauses and their positions; the padding clauses' core literals and positions are identical in K and J; 7 of 14 fresh literals negated in both; fixed-width names | +4 declared but unused variables (α_D ↓; m, α_U unchanged) |
| `E2-UNSAT-base` | base, g = UNSAT | UNSAT | core clauses and their positions; the padding clauses' core literals and positions are identical in K and J; 7 of 14 fresh literals negated in both; fixed-width names | core only |
| `E2-UNSAT-K` | K, g = UNSAT | UNSAT | core clauses and their positions; the padding clauses' core literals and positions are identical in K and J; 7 of 14 fresh literals negated in both; fixed-width names | +14 clauses carrying 2 fresh pure variables (α ↑, m ↑) |
| `E2-UNSAT-J` | J, g = UNSAT | UNSAT | core clauses and their positions; the padding clauses' core literals and positions are identical in K and J; 7 of 14 fresh literals negated in both; fixed-width names | the same 14 clauses carrying 7 fresh pure variables (α ↓, m ↑ by the same 14) |
| `E2-UNSAT-U` | U, g = UNSAT | UNSAT | core clauses and their positions; the padding clauses' core literals and positions are identical in K and J; 7 of 14 fresh literals negated in both; fixed-width names | +4 declared but unused variables (α_D ↓; m, α_U unchanged) |

<details><summary>Prompt and computed outputs — <code>E2-SAT-base</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x03 ∨ x04 ∨ ¬x06)
C02: (x08 ∨ ¬x07 ∨ ¬x05)
C03: (x01 ∨ x03 ∨ ¬x05)
C04: (x04 ∨ ¬x06 ∨ ¬x01)
C05: (x07 ∨ x05 ∨ x04)
C06: (x02 ∨ ¬x06 ∨ x03)
C07: (¬x01 ∨ x04 ∨ x02)
C08: (x03 ∨ ¬x06 ∨ x01)
C09: (¬x04 ∨ ¬x02 ∨ ¬x06)
C10: (x02 ∨ ¬x01 ∨ x05)
C11: (x03 ∨ ¬x05 ∨ ¬x04)
C12: (x06 ∨ ¬x04 ∨ x07)
C13: (x08 ∨ ¬x01 ∨ ¬x04)
C14: (x06 ∨ ¬x05 ∨ ¬x07)
C15: (¬x06 ∨ x03 ∨ x05)
C16: (x03 ∨ ¬x07 ∨ ¬x04)
C17: (¬x04 ∨ ¬x08 ∨ ¬x02)
C18: (¬x08 ∨ ¬x05 ∨ x04)
C19: (¬x02 ∨ x04 ∨ ¬x07)
C20: (¬x01 ∨ x07 ∨ x03)
C21: (¬x07 ∨ x01 ∨ x03)
C22: (x08 ∨ ¬x01 ∨ ¬x03)
C23: (¬x08 ∨ x01 ∨ x02)
C24: (x06 ∨ ¬x05 ∨ x04)
C25: (x03 ∨ ¬x05 ∨ x07)
C26: (x03 ∨ x06 ∨ x01)
C27: (x07 ∨ ¬x03 ∨ ¬x06)
C28: (x03 ∨ x02 ∨ ¬x01)
C29: (¬x03 ∨ x01 ∨ ¬x07)
C30: (¬x06 ∨ ¬x04 ∨ x07)
C31: (¬x07 ∨ ¬x02 ∨ ¬x06)
C32: (x01 ∨ ¬x07 ∨ x08)
C33: (x03 ∨ ¬x07 ∨ ¬x06)
C34: (x01 ∨ ¬x02 ∨ ¬x04)
C35: (¬x08 ∨ x05 ∨ ¬x01)
C36: (x06 ∨ ¬x05 ∨ ¬x03)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** SAT, e.g. 10111111 (1 solution)
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 4.5 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** UNSAT (α_U = 4.50 vs θ = 4.26)
- **A2 DENSITY-D:** UNSAT (α_D = 4.50 vs θ = 4.26)
- **A2 LENGTH-M:** SAT (m = 36 vs illustrative θ_m = 40)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 4.5 clauses
- **H SAMPLE-8:** P(SAT) = 0.031 (1 solutions in 2^8)
- **NOISY-EXACT-STEP:** SAT w.p. 0.95 (L = 5 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** SAT w.p. 0.85 (L = m = 36, p = 0.01/clause)
- **PERCEPTION-NOISE:** SAT (dropped clauses cannot remove solutions)
- **C0 POLARITY:** SAT, witness 11100001 (2 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 11110011 violates 2)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** SAT (exact: 5 decisions ≤ illustrative b = 8)
- **F WALK-200:** SAT in 83% of runs, else UNSAT by default
- **D∘DENSITY (b=4):** UNSAT (budget exceeded at 5 decisions → density default)
- *params:* `{"n_used": 8, "n_decl": 8, "m": 36, "alpha_U": 4.5, "alpha_D": 4.5, "n_solutions": 1, "dpll_decisions": 5, "dpll_decisions_pure_literal": 5, "polarity_witness": "11100001", "polarity_violations": 2, "greedy_witness": "11110011", "greedy_violations": 2, "dpll_witness": "10111111"}`
- *notes:* Dev-size core (n = 8, m = 36, α = 4.5, chosen so the deterministic θ = 4.26 falls between U's α_D and α_U). Study core: n = 24, m = 101, 28 padding clauses on 3 vs 10 fresh variables; θ is fitted there.

</details>

<details><summary>Prompt and computed outputs — <code>E2-SAT-K</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x03 ∨ x04 ∨ ¬x06)
C02: (x08 ∨ ¬x07 ∨ ¬x05)
C03: (x01 ∨ x03 ∨ ¬x05)
C04: (x04 ∨ ¬x06 ∨ ¬x01)
C05: (x07 ∨ x05 ∨ x04)
C06: (x09 ∨ ¬x04 ∨ x01)
C07: (x09 ∨ x04 ∨ ¬x03)
C08: (x02 ∨ ¬x06 ∨ x03)
C09: (¬x01 ∨ x04 ∨ x02)
C10: (x09 ∨ ¬x07 ∨ ¬x01)
C11: (¬x10 ∨ ¬x08 ∨ x05)
C12: (x09 ∨ ¬x08 ∨ x04)
C13: (x03 ∨ ¬x06 ∨ x01)
C14: (¬x04 ∨ ¬x02 ∨ ¬x06)
C15: (x02 ∨ ¬x01 ∨ x05)
C16: (x03 ∨ ¬x05 ∨ ¬x04)
C17: (x06 ∨ ¬x04 ∨ x07)
C18: (x08 ∨ ¬x01 ∨ ¬x04)
C19: (x06 ∨ ¬x05 ∨ ¬x07)
C20: (¬x10 ∨ x07 ∨ x01)
C21: (¬x06 ∨ x03 ∨ x05)
C22: (x03 ∨ ¬x07 ∨ ¬x04)
C23: (¬x04 ∨ ¬x08 ∨ ¬x02)
C24: (¬x08 ∨ ¬x05 ∨ x04)
C25: (¬x10 ∨ x07 ∨ ¬x01)
C26: (x09 ∨ x07 ∨ ¬x06)
C27: (¬x02 ∨ x04 ∨ ¬x07)
C28: (¬x01 ∨ x07 ∨ x03)
C29: (¬x07 ∨ x01 ∨ x03)
C30: (x09 ∨ x07 ∨ x04)
C31: (x08 ∨ ¬x01 ∨ ¬x03)
C32: (¬x08 ∨ x01 ∨ x02)
C33: (x06 ∨ ¬x05 ∨ x04)
C34: (¬x10 ∨ x02 ∨ x01)
C35: (x03 ∨ ¬x05 ∨ x07)
C36: (¬x10 ∨ x04 ∨ ¬x07)
C37: (x03 ∨ x06 ∨ x01)
C38: (x07 ∨ ¬x03 ∨ ¬x06)
C39: (x03 ∨ x02 ∨ ¬x01)
C40: (¬x10 ∨ x05 ∨ x02)
C41: (¬x03 ∨ x01 ∨ ¬x07)
C42: (¬x06 ∨ ¬x04 ∨ x07)
C43: (¬x07 ∨ ¬x02 ∨ ¬x06)
C44: (x01 ∨ ¬x07 ∨ x08)
C45: (x03 ∨ ¬x07 ∨ ¬x06)
C46: (x09 ∨ x05 ∨ ¬x08)
C47: (¬x10 ∨ x01 ∨ x02)
C48: (x01 ∨ ¬x02 ∨ ¬x04)
C49: (¬x08 ∨ x05 ∨ ¬x01)
C50: (x06 ∨ ¬x05 ∨ ¬x03)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** SAT, e.g. 1011111110 (2 solutions)
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 6.2 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** UNSAT (α_U = 5.00 vs θ = 4.26)
- **A2 DENSITY-D:** UNSAT (α_D = 5.00 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 50 vs illustrative θ_m = 40)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 6.2 clauses
- **H SAMPLE-8:** P(SAT) = 0.016 (2 solutions in 2^10)
- **NOISY-EXACT-STEP:** SAT w.p. 0.95 (L = 5 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** SAT w.p. 0.80 (L = m = 50, p = 0.01/clause)
- **PERCEPTION-NOISE:** SAT (dropped clauses cannot remove solutions)
- **C0 POLARITY:** SAT, witness 1111000010 (3 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 1111100110 violates 3)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** SAT (exact: 5 decisions ≤ illustrative b = 8)
- **F WALK-200:** SAT in 80% of runs, else UNSAT by default
- **D∘DENSITY (b=4):** UNSAT (budget exceeded at 5 decisions → density default)
- *params:* `{"n_used": 10, "n_decl": 10, "m": 50, "alpha_U": 5.0, "alpha_D": 5.0, "n_solutions": 2, "dpll_decisions": 5, "dpll_decisions_pure_literal": 5, "polarity_witness": "1111000010", "polarity_violations": 3, "greedy_witness": "1111100110", "greedy_violations": 3, "dpll_witness": "1011111111", "pure_literal_elimination_gives_core": true}`
- *notes:* Dev-size core (n = 8, m = 36, α = 4.5, chosen so the deterministic θ = 4.26 falls between U's α_D and α_U). Study core: n = 24, m = 101, 28 padding clauses on 3 vs 10 fresh variables; θ is fitted there.

</details>

<details><summary>Prompt and computed outputs — <code>E2-SAT-J</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12, x13, x14, x15.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x03 ∨ x04 ∨ ¬x06)
C02: (x08 ∨ ¬x07 ∨ ¬x05)
C03: (x01 ∨ x03 ∨ ¬x05)
C04: (x04 ∨ ¬x06 ∨ ¬x01)
C05: (x07 ∨ x05 ∨ x04)
C06: (x12 ∨ ¬x04 ∨ x01)
C07: (x12 ∨ x04 ∨ ¬x03)
C08: (x02 ∨ ¬x06 ∨ x03)
C09: (¬x01 ∨ x04 ∨ x02)
C10: (x13 ∨ ¬x07 ∨ ¬x01)
C11: (¬x09 ∨ ¬x08 ∨ x05)
C12: (x13 ∨ ¬x08 ∨ x04)
C13: (x03 ∨ ¬x06 ∨ x01)
C14: (¬x04 ∨ ¬x02 ∨ ¬x06)
C15: (x02 ∨ ¬x01 ∨ x05)
C16: (x03 ∨ ¬x05 ∨ ¬x04)
C17: (x06 ∨ ¬x04 ∨ x07)
C18: (x08 ∨ ¬x01 ∨ ¬x04)
C19: (x06 ∨ ¬x05 ∨ ¬x07)
C20: (¬x09 ∨ x07 ∨ x01)
C21: (¬x06 ∨ x03 ∨ x05)
C22: (x03 ∨ ¬x07 ∨ ¬x04)
C23: (¬x04 ∨ ¬x08 ∨ ¬x02)
C24: (¬x08 ∨ ¬x05 ∨ x04)
C25: (¬x09 ∨ x07 ∨ ¬x01)
C26: (x14 ∨ x07 ∨ ¬x06)
C27: (¬x02 ∨ x04 ∨ ¬x07)
C28: (¬x01 ∨ x07 ∨ x03)
C29: (¬x07 ∨ x01 ∨ x03)
C30: (x14 ∨ x07 ∨ x04)
C31: (x08 ∨ ¬x01 ∨ ¬x03)
C32: (¬x08 ∨ x01 ∨ x02)
C33: (x06 ∨ ¬x05 ∨ x04)
C34: (¬x10 ∨ x02 ∨ x01)
C35: (x03 ∨ ¬x05 ∨ x07)
C36: (¬x10 ∨ x04 ∨ ¬x07)
C37: (x03 ∨ x06 ∨ x01)
C38: (x07 ∨ ¬x03 ∨ ¬x06)
C39: (x03 ∨ x02 ∨ ¬x01)
C40: (¬x11 ∨ x05 ∨ x02)
C41: (¬x03 ∨ x01 ∨ ¬x07)
C42: (¬x06 ∨ ¬x04 ∨ x07)
C43: (¬x07 ∨ ¬x02 ∨ ¬x06)
C44: (x01 ∨ ¬x07 ∨ x08)
C45: (x03 ∨ ¬x07 ∨ ¬x06)
C46: (x15 ∨ x05 ∨ ¬x08)
C47: (¬x11 ∨ x01 ∨ x02)
C48: (x01 ∨ ¬x02 ∨ ¬x04)
C49: (¬x08 ∨ x05 ∨ ¬x01)
C50: (x06 ∨ ¬x05 ∨ ¬x03)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** SAT, e.g. 101111110000100 (64 solutions)
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 6.2 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** SAT (α_U = 3.33 vs θ = 4.26)
- **A2 DENSITY-D:** SAT (α_D = 3.33 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 50 vs illustrative θ_m = 40)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 6.2 clauses
- **H SAMPLE-8:** P(SAT) = 0.016 (64 solutions in 2^15)
- **NOISY-EXACT-STEP:** SAT w.p. 0.95 (L = 5 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** SAT w.p. 0.80 (L = m = 50, p = 0.01/clause)
- **PERCEPTION-NOISE:** SAT (dropped clauses cannot remove solutions)
- **C0 POLARITY:** SAT, witness 111100000001111 (3 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 111110010111111 violates 3)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** SAT (exact: 5 decisions ≤ illustrative b = 8)
- **F WALK-200:** SAT in 87% of runs, else UNSAT by default
- **D∘DENSITY (b=4):** SAT (budget exceeded at 5 decisions → density default)
- *params:* `{"n_used": 15, "n_decl": 15, "m": 50, "alpha_U": 3.333, "alpha_D": 3.333, "n_solutions": 64, "dpll_decisions": 5, "dpll_decisions_pure_literal": 5, "polarity_witness": "111100000001111", "polarity_violations": 3, "greedy_witness": "111110010111111", "greedy_violations": 3, "dpll_witness": "101111111111111", "pure_literal_elimination_gives_core": true}`
- *notes:* Dev-size core (n = 8, m = 36, α = 4.5, chosen so the deterministic θ = 4.26 falls between U's α_D and α_U). Study core: n = 24, m = 101, 28 padding clauses on 3 vs 10 fresh variables; θ is fitted there.

</details>

<details><summary>Prompt and computed outputs — <code>E2-SAT-U</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x03 ∨ x04 ∨ ¬x06)
C02: (x08 ∨ ¬x07 ∨ ¬x05)
C03: (x01 ∨ x03 ∨ ¬x05)
C04: (x04 ∨ ¬x06 ∨ ¬x01)
C05: (x07 ∨ x05 ∨ x04)
C06: (x02 ∨ ¬x06 ∨ x03)
C07: (¬x01 ∨ x04 ∨ x02)
C08: (x03 ∨ ¬x06 ∨ x01)
C09: (¬x04 ∨ ¬x02 ∨ ¬x06)
C10: (x02 ∨ ¬x01 ∨ x05)
C11: (x03 ∨ ¬x05 ∨ ¬x04)
C12: (x06 ∨ ¬x04 ∨ x07)
C13: (x08 ∨ ¬x01 ∨ ¬x04)
C14: (x06 ∨ ¬x05 ∨ ¬x07)
C15: (¬x06 ∨ x03 ∨ x05)
C16: (x03 ∨ ¬x07 ∨ ¬x04)
C17: (¬x04 ∨ ¬x08 ∨ ¬x02)
C18: (¬x08 ∨ ¬x05 ∨ x04)
C19: (¬x02 ∨ x04 ∨ ¬x07)
C20: (¬x01 ∨ x07 ∨ x03)
C21: (¬x07 ∨ x01 ∨ x03)
C22: (x08 ∨ ¬x01 ∨ ¬x03)
C23: (¬x08 ∨ x01 ∨ x02)
C24: (x06 ∨ ¬x05 ∨ x04)
C25: (x03 ∨ ¬x05 ∨ x07)
C26: (x03 ∨ x06 ∨ x01)
C27: (x07 ∨ ¬x03 ∨ ¬x06)
C28: (x03 ∨ x02 ∨ ¬x01)
C29: (¬x03 ∨ x01 ∨ ¬x07)
C30: (¬x06 ∨ ¬x04 ∨ x07)
C31: (¬x07 ∨ ¬x02 ∨ ¬x06)
C32: (x01 ∨ ¬x07 ∨ x08)
C33: (x03 ∨ ¬x07 ∨ ¬x06)
C34: (x01 ∨ ¬x02 ∨ ¬x04)
C35: (¬x08 ∨ x05 ∨ ¬x01)
C36: (x06 ∨ ¬x05 ∨ ¬x03)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** SAT, e.g. 10111111 (1 solution)
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 4.5 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** UNSAT (α_U = 4.50 vs θ = 4.26)
- **A2 DENSITY-D:** SAT (α_D = 3.00 vs θ = 4.26)
- **A2 LENGTH-M:** SAT (m = 36 vs illustrative θ_m = 40)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 4.5 clauses
- **H SAMPLE-8:** P(SAT) = 0.031 (16 solutions in 2^12)
- **NOISY-EXACT-STEP:** SAT w.p. 0.95 (L = 5 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** SAT w.p. 0.85 (L = m = 36, p = 0.01/clause)
- **PERCEPTION-NOISE:** SAT (dropped clauses cannot remove solutions)
- **C0 POLARITY:** SAT, witness 11100001 (2 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 11110011 violates 2)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** SAT (exact: 5 decisions ≤ illustrative b = 8)
- **F WALK-200:** SAT in 83% of runs, else UNSAT by default
- **D∘DENSITY (b=4):** UNSAT (budget exceeded at 5 decisions → density default)
- *params:* `{"n_used": 8, "n_decl": 12, "m": 36, "alpha_U": 4.5, "alpha_D": 3.0, "n_solutions": 1, "dpll_decisions": 5, "dpll_decisions_pure_literal": 5, "polarity_witness": "11100001", "polarity_violations": 2, "greedy_witness": "11110011", "greedy_violations": 2, "dpll_witness": "10111111"}`
- *notes:* Dev-size core (n = 8, m = 36, α = 4.5, chosen so the deterministic θ = 4.26 falls between U's α_D and α_U). Study core: n = 24, m = 101, 28 padding clauses on 3 vs 10 fresh variables; θ is fitted there.

</details>

<details><summary>Prompt and computed outputs — <code>E2-UNSAT-base</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (¬x01 ∨ x05 ∨ ¬x03)
C02: (¬x01 ∨ x07 ∨ x06)
C03: (x03 ∨ x08 ∨ ¬x05)
C04: (¬x06 ∨ ¬x03 ∨ ¬x08)
C05: (x06 ∨ x08 ∨ x03)
C06: (¬x06 ∨ x03 ∨ ¬x01)
C07: (x06 ∨ x02 ∨ x07)
C08: (¬x07 ∨ ¬x03 ∨ ¬x02)
C09: (¬x06 ∨ ¬x01 ∨ x04)
C10: (¬x03 ∨ ¬x07 ∨ x02)
C11: (x05 ∨ x02 ∨ ¬x07)
C12: (x07 ∨ x01 ∨ ¬x06)
C13: (¬x08 ∨ x04 ∨ x06)
C14: (x08 ∨ x03 ∨ x02)
C15: (¬x03 ∨ x07 ∨ ¬x04)
C16: (x05 ∨ ¬x06 ∨ ¬x02)
C17: (¬x05 ∨ x08 ∨ ¬x02)
C18: (¬x07 ∨ ¬x04 ∨ ¬x05)
C19: (x08 ∨ ¬x05 ∨ ¬x04)
C20: (x04 ∨ x06 ∨ x05)
C21: (x04 ∨ x05 ∨ ¬x07)
C22: (x02 ∨ x05 ∨ x06)
C23: (¬x03 ∨ x01 ∨ ¬x05)
C24: (¬x03 ∨ ¬x07 ∨ x06)
C25: (¬x02 ∨ x03 ∨ x05)
C26: (x08 ∨ ¬x07 ∨ ¬x03)
C27: (x03 ∨ x06 ∨ x01)
C28: (¬x02 ∨ ¬x06 ∨ ¬x05)
C29: (x06 ∨ ¬x08 ∨ ¬x05)
C30: (x01 ∨ x05 ∨ ¬x08)
C31: (¬x07 ∨ ¬x06 ∨ x03)
C32: (¬x07 ∨ ¬x03 ∨ x01)
C33: (x06 ∨ x04 ∨ x05)
C34: (¬x02 ∨ ¬x08 ∨ x04)
C35: (x07 ∨ x04 ∨ x01)
C36: (¬x04 ∨ ¬x03 ∨ x01)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** UNSAT
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 4.5 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** UNSAT (α_U = 4.50 vs θ = 4.26)
- **A2 DENSITY-D:** UNSAT (α_D = 4.50 vs θ = 4.26)
- **A2 LENGTH-M:** SAT (m = 36 vs illustrative θ_m = 40)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 4.5 clauses
- **H SAMPLE-8:** P(SAT) = 0.000 (0 solutions in 2^8)
- **NOISY-EXACT-STEP:** UNSAT w.p. 0.88 (L = 14 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** UNSAT w.p. 0.85 (L = m = 36, p = 0.01/clause)
- **PERCEPTION-NOISE:** P(SAT) = 0.248 at p_d = 0.05 (5 necessary clauses)
- **C0 POLARITY:** SAT, witness 10011101 (1 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 10010101 violates 1)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** UNSAT by default (14 decisions > illustrative b = 8)
- **F WALK-200:** UNSAT by default (never certifies)
- **D∘DENSITY (b=4):** UNSAT (budget exceeded at 14 decisions → density default)
- *params:* `{"n_used": 8, "n_decl": 8, "m": 36, "alpha_U": 4.5, "alpha_D": 4.5, "n_solutions": 0, "dpll_decisions": 14, "dpll_decisions_pure_literal": 14, "polarity_witness": "10011101", "polarity_violations": 1, "greedy_witness": "10010101", "greedy_violations": 1, "dpll_witness": null}`
- *notes:* Dev-size core (n = 8, m = 36, α = 4.5, chosen so the deterministic θ = 4.26 falls between U's α_D and α_U). Study core: n = 24, m = 101, 28 padding clauses on 3 vs 10 fresh variables; θ is fitted there.

</details>

<details><summary>Prompt and computed outputs — <code>E2-UNSAT-K</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (¬x01 ∨ x05 ∨ ¬x03)
C02: (¬x01 ∨ x07 ∨ x06)
C03: (x03 ∨ x08 ∨ ¬x05)
C04: (¬x06 ∨ ¬x03 ∨ ¬x08)
C05: (x06 ∨ x08 ∨ x03)
C06: (¬x06 ∨ x03 ∨ ¬x01)
C07: (x06 ∨ x02 ∨ x07)
C08: (x09 ∨ x05 ∨ x06)
C09: (¬x10 ∨ x04 ∨ x03)
C10: (¬x07 ∨ ¬x03 ∨ ¬x02)
C11: (¬x06 ∨ ¬x01 ∨ x04)
C12: (¬x03 ∨ ¬x07 ∨ x02)
C13: (x05 ∨ x02 ∨ ¬x07)
C14: (x07 ∨ x01 ∨ ¬x06)
C15: (¬x08 ∨ x04 ∨ x06)
C16: (x09 ∨ x04 ∨ ¬x02)
C17: (x09 ∨ x04 ∨ ¬x03)
C18: (x08 ∨ x03 ∨ x02)
C19: (¬x10 ∨ x08 ∨ ¬x06)
C20: (¬x03 ∨ x07 ∨ ¬x04)
C21: (x05 ∨ ¬x06 ∨ ¬x02)
C22: (¬x05 ∨ x08 ∨ ¬x02)
C23: (¬x10 ∨ x06 ∨ x08)
C24: (¬x07 ∨ ¬x04 ∨ ¬x05)
C25: (x08 ∨ ¬x05 ∨ ¬x04)
C26: (x04 ∨ x06 ∨ x05)
C27: (x04 ∨ x05 ∨ ¬x07)
C28: (¬x10 ∨ x08 ∨ x02)
C29: (x02 ∨ x05 ∨ x06)
C30: (¬x03 ∨ x01 ∨ ¬x05)
C31: (x09 ∨ ¬x03 ∨ ¬x01)
C32: (¬x03 ∨ ¬x07 ∨ x06)
C33: (¬x02 ∨ x03 ∨ x05)
C34: (x08 ∨ ¬x07 ∨ ¬x03)
C35: (x03 ∨ x06 ∨ x01)
C36: (¬x02 ∨ ¬x06 ∨ ¬x05)
C37: (x06 ∨ ¬x08 ∨ ¬x05)
C38: (x01 ∨ x05 ∨ ¬x08)
C39: (¬x07 ∨ ¬x06 ∨ x03)
C40: (x09 ∨ ¬x06 ∨ ¬x08)
C41: (¬x07 ∨ ¬x03 ∨ x01)
C42: (x06 ∨ x04 ∨ x05)
C43: (¬x10 ∨ ¬x08 ∨ ¬x05)
C44: (x09 ∨ x04 ∨ ¬x01)
C45: (¬x10 ∨ x01 ∨ x07)
C46: (¬x02 ∨ ¬x08 ∨ x04)
C47: (¬x10 ∨ x06 ∨ x02)
C48: (x07 ∨ x04 ∨ x01)
C49: (¬x04 ∨ ¬x03 ∨ x01)
C50: (x09 ∨ x06 ∨ x04)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** UNSAT
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 6.2 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** UNSAT (α_U = 5.00 vs θ = 4.26)
- **A2 DENSITY-D:** UNSAT (α_D = 5.00 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 50 vs illustrative θ_m = 40)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 6.2 clauses
- **H SAMPLE-8:** P(SAT) = 0.000 (0 solutions in 2^10)
- **NOISY-EXACT-STEP:** UNSAT w.p. 0.88 (L = 14 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** UNSAT w.p. 0.80 (L = m = 50, p = 0.01/clause)
- **PERCEPTION-NOISE:** P(SAT) = 0.248 at p_d = 0.05 (5 necessary clauses)
- **C0 POLARITY:** SAT, witness 1101110110 (2 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 1101001111 violates 1)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** UNSAT by default (14 decisions > illustrative b = 8)
- **F WALK-200:** UNSAT by default (never certifies)
- **D∘DENSITY (b=4):** UNSAT (budget exceeded at 14 decisions → density default)
- *params:* `{"n_used": 10, "n_decl": 10, "m": 50, "alpha_U": 5.0, "alpha_D": 5.0, "n_solutions": 0, "dpll_decisions": 14, "dpll_decisions_pure_literal": 14, "polarity_witness": "1101110110", "polarity_violations": 2, "greedy_witness": "1101001111", "greedy_violations": 1, "dpll_witness": null, "pure_literal_elimination_gives_core": true}`
- *notes:* Dev-size core (n = 8, m = 36, α = 4.5, chosen so the deterministic θ = 4.26 falls between U's α_D and α_U). Study core: n = 24, m = 101, 28 padding clauses on 3 vs 10 fresh variables; θ is fitted there.

</details>

<details><summary>Prompt and computed outputs — <code>E2-UNSAT-J</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12, x13, x14, x15.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (¬x01 ∨ x05 ∨ ¬x03)
C02: (¬x01 ∨ x07 ∨ x06)
C03: (x03 ∨ x08 ∨ ¬x05)
C04: (¬x06 ∨ ¬x03 ∨ ¬x08)
C05: (x06 ∨ x08 ∨ x03)
C06: (¬x06 ∨ x03 ∨ ¬x01)
C07: (x06 ∨ x02 ∨ x07)
C08: (x12 ∨ x05 ∨ x06)
C09: (¬x09 ∨ x04 ∨ x03)
C10: (¬x07 ∨ ¬x03 ∨ ¬x02)
C11: (¬x06 ∨ ¬x01 ∨ x04)
C12: (¬x03 ∨ ¬x07 ∨ x02)
C13: (x05 ∨ x02 ∨ ¬x07)
C14: (x07 ∨ x01 ∨ ¬x06)
C15: (¬x08 ∨ x04 ∨ x06)
C16: (x12 ∨ x04 ∨ ¬x02)
C17: (x13 ∨ x04 ∨ ¬x03)
C18: (x08 ∨ x03 ∨ x02)
C19: (¬x09 ∨ x08 ∨ ¬x06)
C20: (¬x03 ∨ x07 ∨ ¬x04)
C21: (x05 ∨ ¬x06 ∨ ¬x02)
C22: (¬x05 ∨ x08 ∨ ¬x02)
C23: (¬x09 ∨ x06 ∨ x08)
C24: (¬x07 ∨ ¬x04 ∨ ¬x05)
C25: (x08 ∨ ¬x05 ∨ ¬x04)
C26: (x04 ∨ x06 ∨ x05)
C27: (x04 ∨ x05 ∨ ¬x07)
C28: (¬x10 ∨ x08 ∨ x02)
C29: (x02 ∨ x05 ∨ x06)
C30: (¬x03 ∨ x01 ∨ ¬x05)
C31: (x13 ∨ ¬x03 ∨ ¬x01)
C32: (¬x03 ∨ ¬x07 ∨ x06)
C33: (¬x02 ∨ x03 ∨ x05)
C34: (x08 ∨ ¬x07 ∨ ¬x03)
C35: (x03 ∨ x06 ∨ x01)
C36: (¬x02 ∨ ¬x06 ∨ ¬x05)
C37: (x06 ∨ ¬x08 ∨ ¬x05)
C38: (x01 ∨ x05 ∨ ¬x08)
C39: (¬x07 ∨ ¬x06 ∨ x03)
C40: (x14 ∨ ¬x06 ∨ ¬x08)
C41: (¬x07 ∨ ¬x03 ∨ x01)
C42: (x06 ∨ x04 ∨ x05)
C43: (¬x10 ∨ ¬x08 ∨ ¬x05)
C44: (x14 ∨ x04 ∨ ¬x01)
C45: (¬x11 ∨ x01 ∨ x07)
C46: (¬x02 ∨ ¬x08 ∨ x04)
C47: (¬x11 ∨ x06 ∨ x02)
C48: (x07 ∨ x04 ∨ x01)
C49: (¬x04 ∨ ¬x03 ∨ x01)
C50: (x15 ∨ x06 ∨ x04)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** UNSAT
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 6.2 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** SAT (α_U = 3.33 vs θ = 4.26)
- **A2 DENSITY-D:** SAT (α_D = 3.33 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 50 vs illustrative θ_m = 40)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 6.2 clauses
- **H SAMPLE-8:** P(SAT) = 0.000 (0 solutions in 2^15)
- **NOISY-EXACT-STEP:** UNSAT w.p. 0.88 (L = 14 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** UNSAT w.p. 0.80 (L = m = 50, p = 0.01/clause)
- **PERCEPTION-NOISE:** P(SAT) = 0.248 at p_d = 0.05 (5 necessary clauses)
- **C0 POLARITY:** SAT, witness 110111010001111 (2 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 110100111111111 violates 1)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** UNSAT by default (14 decisions > illustrative b = 8)
- **F WALK-200:** UNSAT by default (never certifies)
- **D∘DENSITY (b=4):** SAT (budget exceeded at 14 decisions → density default)
- *params:* `{"n_used": 15, "n_decl": 15, "m": 50, "alpha_U": 3.333, "alpha_D": 3.333, "n_solutions": 0, "dpll_decisions": 14, "dpll_decisions_pure_literal": 14, "polarity_witness": "110111010001111", "polarity_violations": 2, "greedy_witness": "110100111111111", "greedy_violations": 1, "dpll_witness": null, "pure_literal_elimination_gives_core": true}`
- *notes:* Dev-size core (n = 8, m = 36, α = 4.5, chosen so the deterministic θ = 4.26 falls between U's α_D and α_U). Study core: n = 24, m = 101, 28 padding clauses on 3 vs 10 fresh variables; θ is fitted there.

</details>

<details><summary>Prompt and computed outputs — <code>E2-UNSAT-U</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (¬x01 ∨ x05 ∨ ¬x03)
C02: (¬x01 ∨ x07 ∨ x06)
C03: (x03 ∨ x08 ∨ ¬x05)
C04: (¬x06 ∨ ¬x03 ∨ ¬x08)
C05: (x06 ∨ x08 ∨ x03)
C06: (¬x06 ∨ x03 ∨ ¬x01)
C07: (x06 ∨ x02 ∨ x07)
C08: (¬x07 ∨ ¬x03 ∨ ¬x02)
C09: (¬x06 ∨ ¬x01 ∨ x04)
C10: (¬x03 ∨ ¬x07 ∨ x02)
C11: (x05 ∨ x02 ∨ ¬x07)
C12: (x07 ∨ x01 ∨ ¬x06)
C13: (¬x08 ∨ x04 ∨ x06)
C14: (x08 ∨ x03 ∨ x02)
C15: (¬x03 ∨ x07 ∨ ¬x04)
C16: (x05 ∨ ¬x06 ∨ ¬x02)
C17: (¬x05 ∨ x08 ∨ ¬x02)
C18: (¬x07 ∨ ¬x04 ∨ ¬x05)
C19: (x08 ∨ ¬x05 ∨ ¬x04)
C20: (x04 ∨ x06 ∨ x05)
C21: (x04 ∨ x05 ∨ ¬x07)
C22: (x02 ∨ x05 ∨ x06)
C23: (¬x03 ∨ x01 ∨ ¬x05)
C24: (¬x03 ∨ ¬x07 ∨ x06)
C25: (¬x02 ∨ x03 ∨ x05)
C26: (x08 ∨ ¬x07 ∨ ¬x03)
C27: (x03 ∨ x06 ∨ x01)
C28: (¬x02 ∨ ¬x06 ∨ ¬x05)
C29: (x06 ∨ ¬x08 ∨ ¬x05)
C30: (x01 ∨ x05 ∨ ¬x08)
C31: (¬x07 ∨ ¬x06 ∨ x03)
C32: (¬x07 ∨ ¬x03 ∨ x01)
C33: (x06 ∨ x04 ∨ x05)
C34: (¬x02 ∨ ¬x08 ∨ x04)
C35: (x07 ∨ x04 ∨ x01)
C36: (¬x04 ∨ ¬x03 ∨ x01)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** UNSAT
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 4.5 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** UNSAT (α_U = 4.50 vs θ = 4.26)
- **A2 DENSITY-D:** SAT (α_D = 3.00 vs θ = 4.26)
- **A2 LENGTH-M:** SAT (m = 36 vs illustrative θ_m = 40)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 4.5 clauses
- **H SAMPLE-8:** P(SAT) = 0.000 (0 solutions in 2^12)
- **NOISY-EXACT-STEP:** UNSAT w.p. 0.88 (L = 14 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** UNSAT w.p. 0.85 (L = m = 36, p = 0.01/clause)
- **PERCEPTION-NOISE:** P(SAT) = 0.248 at p_d = 0.05 (5 necessary clauses)
- **C0 POLARITY:** SAT, witness 10011101 (1 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 10010101 violates 1)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** UNSAT by default (14 decisions > illustrative b = 8)
- **F WALK-200:** UNSAT by default (never certifies)
- **D∘DENSITY (b=4):** UNSAT (budget exceeded at 14 decisions → density default)
- *params:* `{"n_used": 8, "n_decl": 12, "m": 36, "alpha_U": 4.5, "alpha_D": 3.0, "n_solutions": 0, "dpll_decisions": 14, "dpll_decisions_pure_literal": 14, "polarity_witness": "10011101", "polarity_violations": 1, "greedy_witness": "10010101", "greedy_violations": 1, "dpll_witness": null}`
- *notes:* Dev-size core (n = 8, m = 36, α = 4.5, chosen so the deterministic θ = 4.26 falls between U's α_D and α_U). Study core: n = 24, m = 101, 28 padding clauses on 3 vs 10 fresh variables; θ is fitted there.

</details>

**Hypothesis matrix**

| Theory | (a) `E2-SAT-base` | (a) `E2-SAT-K` | (a) `E2-SAT-J` | (a) `E2-SAT-U` | (a) `E2-UNSAT-base` | (a) `E2-UNSAT-K` | (a) `E2-UNSAT-J` | (a) `E2-UNSAT-U` | (b) pure-theory statistic · weight resolution | (c) predicted trace |
|---|---|---|---|---|---|---|---|---|---|---|
| exact | SAT | SAT | SAT | SAT | UNSAT | UNSAT | UNSAT | UNSAT | K − J in P(UNSAT), mean of the two bases = +0.00. Detectable π ≥ 0.30 vs F WALK-200 | A completed procedure: a witness checked against every constraint, or a closed refutation / exhaustive case split. No cue given as a reason. |
| A1 ALWAYS-SAT | SAT | SAT | SAT | SAT | SAT | SAT | SAT | SAT | K − J in P(UNSAT), mean of the two bases = +0.00. Detectable π ≥ 0.05 vs H RANDOM-U | A witness proposed without checking every constraint; no attempt at refutation. |
| A1 ALWAYS-UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | K − J in P(UNSAT), mean of the two bases = +0.00. Detectable π ≥ 0.05 vs H RANDOM-U | GIVEUP early ('too many constraints to check'); no witness attempted. |
| A2 DENSITY-U | UNSAT | UNSAT | SAT | UNSAT | UNSAT | UNSAT | SAT | UNSAT | K − J in P(UNSAT), mean of the two bases = +1.00. Detectable π ≥ 0.05 vs H RANDOM-U | CUE-DENS as the reason ('about 4.3 clauses per variable is near the hard threshold'); no closed refutation; padding variables not treated specially. |
| A2 DENSITY-D | UNSAT | UNSAT | SAT | SAT | UNSAT | UNSAT | SAT | SAT | K − J in P(UNSAT), mean of the two bases = +1.00. Detectable π ≥ 0.05 vs H RANDOM-U | CUE-DENS computed from the declared variable count. |
| A2 LENGTH-M | SAT | UNSAT | UNSAT | SAT | SAT | UNSAT | UNSAT | SAT | K − J in P(UNSAT), mean of the two bases = +0.00. Detectable π ≥ 0.05 vs H RANDOM-U | CUE-SIZE as the reason ('with this many clauses it is very likely unsatisfiable'). |
| H RANDOM-U | SAT or UNSAT w.p. ½; a random witness violates ≈ 4.5 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 6.2 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 6.2 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 4.5 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 4.5 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 6.2 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 6.2 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 4.5 clauses | K − J in P(UNSAT), mean of the two bases = +0.00. Detectable π ≥ 0.05 vs NOISY-EXACT-READ | No procedure determines the verdict; trace content and verdict unrelated. |
| H SAMPLE-8 | P(SAT) = 0.031 | P(SAT) = 0.016 | P(SAT) = 0.016 | P(SAT) = 0.031 | P(SAT) = 0.000 | P(SAT) = 0.000 | P(SAT) = 0.000 | P(SAT) = 0.000 | K − J in P(UNSAT), mean of the two bases = +0.00. Detectable π ≥ 0.05 vs H RANDOM-U | SAMPLE(k): at most 8 concrete cases checked, then a universal conclusion; no exhaustive split. |
| NOISY-EXACT-READ | SAT w.p. 0.85 | SAT w.p. 0.80 | SAT w.p. 0.80 | SAT w.p. 0.85 | UNSAT w.p. 0.85 | UNSAT w.p. 0.80 | UNSAT w.p. 0.80 | UNSAT w.p. 0.85 | K − J in P(UNSAT), mean of the two bases = +0.00. Detectable π ≥ 0.14 vs F WALK-200 | As NOISY-EXACT-STEP, with slips when reading clauses, more often in longer inputs. |
| PERCEPTION-NOISE | SAT | SAT | SAT | SAT | P(SAT) = 0.248 | P(SAT) = 0.248 | P(SAT) = 0.248 | P(SAT) = 0.248 | K − J in P(UNSAT), mean of the two bases = +0.00. Detectable π ≥ 0.24 vs NOISY-EXACT-READ | A MISQUOTE of a constraint (a dropped ¬, a wrong pair, a missing clause); later reasoning consistent with the misquote. |
| C0 POLARITY | SAT | SAT | SAT | SAT | SAT | SAT | SAT | SAT | K − J in P(UNSAT), mean of the two bases = +0.00. Detectable π ≥ 0.05 vs H RANDOM-U | A witness built in one step from majority signs; no search. |
| C1 GREEDY | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | K − J in P(UNSAT), mean of the two bases = +0.00. Detectable π ≥ 0.05 vs H RANDOM-U | One ASSIGN pass in index order, no BACKTRACK; at a dead end, GIVEUP or an invalid witness. |
| D DPLL-b | SAT | SAT | SAT | SAT | UNSAT | UNSAT | UNSAT | UNSAT | K − J in P(UNSAT), mean of the two bases = +0.00. Detectable π ≥ 0.30 vs F WALK-200 | BRANCH / CONTRA / BACKTRACK; ends in a witness, a closed refutation, or the cap. |
| F WALK-200 | SAT in 83% of runs | SAT in 80% of runs | SAT in 87% of runs | SAT in 83% of runs | UNSAT | UNSAT | UNSAT | UNSAT | K − J in P(UNSAT), mean of the two bases = +0.03. Detectable π ≥ 0.28 vs NOISY-EXACT-READ | REPAIR loops: a full candidate, its violated clauses listed, flips; never a refutation. |
| D∘DENSITY (b=4) | UNSAT | UNSAT | SAT | UNSAT | UNSAT | UNSAT | SAT | UNSAT | K − J in P(UNSAT), mean of the two bases = +1.00. Detectable π ≥ 0.05 vs H RANDOM-U | A real search, abandoned (GIVEUP or the cap), then a density-based verdict. |

*(c) for every theory: the expected share of traces showing the signature ≈ π_h · r̂ (faithfulness, from E8), plus the coder's false-positive rate.*

**Likelihood ratios per observable pattern** (log₁₀ LR; one study unit)

| Pattern | Favours (log₁₀ LR vs the best theory outside the favoured group) | Pushes toward zero weight (log₁₀ LR vs the best theory) |
|---|---|---|
| SAT base: K UNSAT, J SAT | A2 DENSITY-U (+0.6), A2 DENSITY-D (+0.6), D∘DENSITY (b=4) (+0.6) | exact (-1.3), A1 ALWAYS-SAT (-1.3), A1 ALWAYS-UNSAT (-1.3), A2 LENGTH-M (-1.3), H SAMPLE-8 (-1.3), PERCEPTION-NOISE (-1.3), C0 POLARITY (-1.3), C1 GREEDY (-1.3), D DPLL-b (-1.3) |
| SAT base: K SAT, J UNSAT | H RANDOM-U (+0.4), NOISY-EXACT-READ (+0.2) | A2 DENSITY-U (-2.0), A2 DENSITY-D (-2.0), D∘DENSITY (b=4) (-2.0) |
| SAT base: K and J both UNSAT, base SAT | A2 LENGTH-M (+0.8) | exact (-2.6), A1 ALWAYS-SAT (-2.6), A2 DENSITY-U (-2.6), A2 DENSITY-D (-2.6), PERCEPTION-NOISE (-2.6), C0 POLARITY (-2.6), D DPLL-b (-2.6), D∘DENSITY (b=4) (-2.6), F WALK-200 (-1.6), NOISY-EXACT-READ (-1.4), A1 ALWAYS-UNSAT (-1.3), H SAMPLE-8 (-1.3), C1 GREEDY (-1.3) |
| SAT base: all four alike | exact (+0.8), A1 ALWAYS-SAT (+0.8), A1 ALWAYS-UNSAT (+0.8), H SAMPLE-8 (+0.8), PERCEPTION-NOISE (+0.8), C0 POLARITY (+0.8), C1 GREEDY (+0.8), D DPLL-b (+0.8), F WALK-200 (+0.6), NOISY-EXACT-READ (+0.6) | A2 DENSITY-D (-2.3), A2 LENGTH-M (-2.3), A2 DENSITY-U (-1.3), D∘DENSITY (b=4) (-1.3) |
| SAT base: U UNSAT, base SAT | H RANDOM-U (+0.7), F WALK-200 (+0.5), NOISY-EXACT-READ (+0.4) | A2 DENSITY-D (-2.0) |
| UNSAT base: K UNSAT, J SAT | A2 DENSITY-U (+0.6), A2 DENSITY-D (+0.6), D∘DENSITY (b=4) (+0.6) | exact (-1.3), A1 ALWAYS-SAT (-1.3), A1 ALWAYS-UNSAT (-1.3), A2 LENGTH-M (-1.3), H SAMPLE-8 (-1.3), C0 POLARITY (-1.3), C1 GREEDY (-1.3), D DPLL-b (-1.3), F WALK-200 (-1.3) |
| UNSAT base: K SAT, J UNSAT | H RANDOM-U (+0.7), PERCEPTION-NOISE (+0.6), NOISY-EXACT-READ (+0.5) | A2 DENSITY-U (-2.0), A2 DENSITY-D (-2.0), D∘DENSITY (b=4) (-2.0) |
| UNSAT base: K and J both UNSAT, base SAT | A2 LENGTH-M (+0.8) | A1 ALWAYS-SAT (-2.6), A2 DENSITY-U (-2.6), A2 DENSITY-D (-2.6), C0 POLARITY (-2.6), D∘DENSITY (b=4) (-2.6), exact (-1.3), A1 ALWAYS-UNSAT (-1.3), H SAMPLE-8 (-1.3), C1 GREEDY (-1.3), D DPLL-b (-1.3), F WALK-200 (-1.3) |
| UNSAT base: all four alike | exact (+0.4), A1 ALWAYS-SAT (+0.4), A1 ALWAYS-UNSAT (+0.4), H SAMPLE-8 (+0.4), C0 POLARITY (+0.4), C1 GREEDY (+0.4), D DPLL-b (+0.4), F WALK-200 (+0.4), NOISY-EXACT-READ (+0.2) | A2 DENSITY-D (-2.3), A2 LENGTH-M (-2.3), A2 DENSITY-U (-1.3), D∘DENSITY (b=4) (-1.3) |
| UNSAT base: U UNSAT, base SAT | H RANDOM-U (+0.7), PERCEPTION-NOISE (+0.6), NOISY-EXACT-READ (+0.4) | A2 DENSITY-D (-2.0) |

**Weight resolution at study N**

| Theory | Nearest competitor (smallest KL) | Detectable π vs it (80% power) | Upper 95% bound on π if pure competitor | E[log₁₀ BF] vs competitor | Detectable π if the rest is the hardest base (which) | Identical predictions here |
|---|---|---|---|---|---|---|
| exact | F WALK-200 | 0.300 | 0.199 | 17.0 | 0.300 (F WALK-200) | D DPLL-b |
| A1 ALWAYS-SAT | H RANDOM-U | 0.046 | 0.030 | 257.8 | 0.046 (H RANDOM-U) | C0 POLARITY |
| A1 ALWAYS-UNSAT | H RANDOM-U | 0.046 | 0.030 | 257.8 | 0.046 (H RANDOM-U) | H SAMPLE-8, C1 GREEDY |
| A2 DENSITY-U | H RANDOM-U | 0.046 | 0.030 | 257.8 | 0.046 (H RANDOM-U) | D∘DENSITY (b=4) |
| A2 DENSITY-D | H RANDOM-U | 0.046 | 0.030 | 257.8 | 0.046 (H RANDOM-U) | — |
| A2 LENGTH-M | H RANDOM-U | 0.046 | 0.030 | 257.8 | 0.046 (H RANDOM-U) | — |
| H RANDOM-U | NOISY-EXACT-READ | 0.050 | 0.033 | 145.8 | 0.050 (NOISY-EXACT-READ) | — |
| H SAMPLE-8 | H RANDOM-U | 0.046 | 0.030 | 257.8 | 0.046 (H RANDOM-U) | A1 ALWAYS-UNSAT, C1 GREEDY |
| NOISY-EXACT-READ | F WALK-200 | 0.137 | 0.091 | 28.3 | 0.137 (F WALK-200) | — |
| PERCEPTION-NOISE | NOISY-EXACT-READ | 0.243 | 0.161 | 23.8 | 0.243 (NOISY-EXACT-READ) | — |
| C0 POLARITY | H RANDOM-U | 0.046 | 0.030 | 257.8 | 0.046 (H RANDOM-U) | A1 ALWAYS-SAT |
| C1 GREEDY | H RANDOM-U | 0.046 | 0.030 | 257.8 | 0.046 (H RANDOM-U) | A1 ALWAYS-UNSAT, H SAMPLE-8 |
| D DPLL-b | F WALK-200 | 0.300 | 0.199 | 17.0 | 0.300 (F WALK-200) | exact |
| F WALK-200 | NOISY-EXACT-READ | 0.276 | 0.183 | 19.8 | 0.276 (NOISY-EXACT-READ) | — |
| D∘DENSITY (b=4) | H RANDOM-U | 0.046 | 0.030 | 257.8 | 0.046 (H RANDOM-U) | A2 DENSITY-U |

**Not separated here.** D∘DENSITY gives the same answers as DENSITY-U whenever the search budget is exceeded. E8's stratified early answering separates them (COMPLETE vs GIVEUP/CAPPED). Exact, C0 POLARITY, PERCEPTION-NOISE and pure-literal-aware structural theories are flat here; E1 separates them.

<a id="e2-ent"></a>
## E2: matched conclusions on one premise set (g × FREQ × ATMOSPHERE)

**Reasoning question.** Within one premise set, do FREQ and ATMOSPHERE move 'follows' when entailment, UP depth and ρ are held fixed?

**Design.** Eight conclusions fill the 2 × 2 × 2; none overlaps the first or last premise, so PRIMACY/RECENCY are constant here.  *Study units:* eight conclusions × 200.

| Item | Cell | Ground truth | Controlled | Varied |
|---|---|---|---|---|
| `E2-ENT-E-hi-match` | g = follows, FREQ hi, ATMOSPHERE match | follows | premises; conclusion words within ±2; no conclusion overlaps premise 1 or the last premise; entailed conclusions share UP depth None; non-entailed ρ within 0.00 | the conclusion: FREQ statistic (hi ≥ 3 vs lo ≤ 1; min over a conjunction's literals, max over a disjunction's) × atmosphere match, within each g |
| `E2-ENT-E-hi-mis` | g = follows, FREQ hi, ATMOSPHERE mismatch | follows | premises; conclusion words within ±2; no conclusion overlaps premise 1 or the last premise; entailed conclusions share UP depth None; non-entailed ρ within 0.00 | the conclusion: FREQ statistic (hi ≥ 3 vs lo ≤ 1; min over a conjunction's literals, max over a disjunction's) × atmosphere match, within each g |
| `E2-ENT-E-lo-match` | g = follows, FREQ lo, ATMOSPHERE match | follows | premises; conclusion words within ±2; no conclusion overlaps premise 1 or the last premise; entailed conclusions share UP depth None; non-entailed ρ within 0.00 | the conclusion: FREQ statistic (hi ≥ 3 vs lo ≤ 1; min over a conjunction's literals, max over a disjunction's) × atmosphere match, within each g |
| `E2-ENT-E-lo-mis` | g = follows, FREQ lo, ATMOSPHERE mismatch | follows | premises; conclusion words within ±2; no conclusion overlaps premise 1 or the last premise; entailed conclusions share UP depth None; non-entailed ρ within 0.00 | the conclusion: FREQ statistic (hi ≥ 3 vs lo ≤ 1; min over a conjunction's literals, max over a disjunction's) × atmosphere match, within each g |
| `E2-ENT-N-hi-match` | g = not, FREQ hi, ATMOSPHERE match | does not follow | premises; conclusion words within ±2; no conclusion overlaps premise 1 or the last premise; entailed conclusions share UP depth None; non-entailed ρ within 0.00 | the conclusion: FREQ statistic (hi ≥ 3 vs lo ≤ 1; min over a conjunction's literals, max over a disjunction's) × atmosphere match, within each g |
| `E2-ENT-N-hi-mis` | g = not, FREQ hi, ATMOSPHERE mismatch | does not follow | premises; conclusion words within ±2; no conclusion overlaps premise 1 or the last premise; entailed conclusions share UP depth None; non-entailed ρ within 0.00 | the conclusion: FREQ statistic (hi ≥ 3 vs lo ≤ 1; min over a conjunction's literals, max over a disjunction's) × atmosphere match, within each g |
| `E2-ENT-N-lo-match` | g = not, FREQ lo, ATMOSPHERE match | does not follow | premises; conclusion words within ±2; no conclusion overlaps premise 1 or the last premise; entailed conclusions share UP depth None; non-entailed ρ within 0.00 | the conclusion: FREQ statistic (hi ≥ 3 vs lo ≤ 1; min over a conjunction's literals, max over a disjunction's) × atmosphere match, within each g |
| `E2-ENT-N-lo-mis` | g = not, FREQ lo, ATMOSPHERE mismatch | does not follow | premises; conclusion words within ±2; no conclusion overlaps premise 1 or the last premise; entailed conclusions share UP depth None; non-entailed ρ within 0.00 | the conclusion: FREQ statistic (hi ≥ 3 vs lo ≤ 1; min over a conjunction's literals, max over a disjunction's) × atmosphere match, within each g |

<details><summary>Prompt and computed outputs — <code>E2-ENT-E-hi-match</code></summary>

```text
Here are some facts about a machine.

- Either the bell is ringing, or the lamp is lit.
- The fan is running.
- Either the lamp is not lit and the bell is ringing, or the door is open.
- Either the gate is not locked and the door is open, or the door is open.
- Either the bell is ringing, or the door is open.

Question: Does it follow from these facts that the bell is ringing or the fan is running?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** follows
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** follows (literal counts [3, 1]; max vs illustrative θ = 2)
- **A2 ATMOSPHERE:** follows (atm(P) = disj/pos, mood(C) = disj/pos)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 1.000 (ρ = 0.000)
- **NOISY-EXACT:** follows w.p. 0.90
- **PERCEPTION-NOISE:** follows unless a misread breaks it: P(does not follow) = 0.018
- **B1 UP-1:** does not follow (not UP-derivable)
- **B1 UP-2:** does not follow (not UP-derivable)
- **B4 ETR:** follows (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** follows
- **B4 MATCH:** follows
- **D case-split (b = 4):** follows
- *params:* `{"atoms": 5, "rho": 0.0, "n_models": 6, "up_depth": null, "kappa_follow": 0.909, "kappa_break": 0.091, "eta_first_counter": null, "etr_what_follows": "{0,a0()a1()~a4()}", "freq_stat": 3, "freq_cell": "hi", "atmosphere_match": true, "words": 9, "propagation_steps_beyond_facts": null}`
- *notes:* Dev-size (5 atoms, 5 premises).

</details>

<details><summary>Prompt and computed outputs — <code>E2-ENT-E-hi-mis</code></summary>

```text
Here are some facts about a machine.

- Either the bell is ringing, or the lamp is lit.
- The fan is running.
- Either the lamp is not lit and the bell is ringing, or the door is open.
- Either the gate is not locked and the door is open, or the door is open.
- Either the bell is ringing, or the door is open.

Question: Does it follow from these facts that the bell is not ringing or the door is open?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** follows
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** follows (literal counts [0, 4]; max vs illustrative θ = 2)
- **A2 ATMOSPHERE:** does not follow (atm(P) = disj/pos, mood(C) = disj/neg)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 1.000 (ρ = 0.000)
- **NOISY-EXACT:** follows w.p. 0.90
- **PERCEPTION-NOISE:** follows unless a misread breaks it: P(does not follow) = 0.036
- **B1 UP-1:** does not follow (not UP-derivable)
- **B1 UP-2:** does not follow (not UP-derivable)
- **B4 ETR:** does not follow (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** follows
- **B4 MATCH:** follows
- **D case-split (b = 4):** follows
- *params:* `{"atoms": 5, "rho": 0.0, "n_models": 6, "up_depth": null, "kappa_follow": 0.818, "kappa_break": 0.182, "eta_first_counter": null, "etr_what_follows": "{0,a0()a1()~a4()}", "freq_stat": 4, "freq_cell": "hi", "atmosphere_match": false, "words": 10, "propagation_steps_beyond_facts": null}`
- *notes:* Dev-size (5 atoms, 5 premises).

</details>

<details><summary>Prompt and computed outputs — <code>E2-ENT-E-lo-match</code></summary>

```text
Here are some facts about a machine.

- Either the bell is ringing, or the lamp is lit.
- The fan is running.
- Either the lamp is not lit and the bell is ringing, or the door is open.
- Either the gate is not locked and the door is open, or the door is open.
- Either the bell is ringing, or the door is open.

Question: Does it follow from these facts that the lamp is lit or the fan is running?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** follows
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** does not follow (literal counts [1, 1]; max vs illustrative θ = 2)
- **A2 ATMOSPHERE:** follows (atm(P) = disj/pos, mood(C) = disj/pos)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 1.000 (ρ = 0.000)
- **NOISY-EXACT:** follows w.p. 0.90
- **PERCEPTION-NOISE:** follows unless a misread breaks it: P(does not follow) = 0.018
- **B1 UP-1:** does not follow (not UP-derivable)
- **B1 UP-2:** does not follow (not UP-derivable)
- **B4 ETR:** does not follow (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** follows
- **B4 MATCH:** follows
- **D case-split (b = 4):** follows
- *params:* `{"atoms": 5, "rho": 0.0, "n_models": 6, "up_depth": null, "kappa_follow": 0.909, "kappa_break": 0.091, "eta_first_counter": null, "etr_what_follows": "{0,a0()a1()~a4()}", "freq_stat": 1, "freq_cell": "lo", "atmosphere_match": true, "words": 9, "propagation_steps_beyond_facts": null}`
- *notes:* Dev-size (5 atoms, 5 premises).

</details>

<details><summary>Prompt and computed outputs — <code>E2-ENT-E-lo-mis</code></summary>

```text
Here are some facts about a machine.

- Either the bell is ringing, or the lamp is lit.
- The fan is running.
- Either the lamp is not lit and the bell is ringing, or the door is open.
- Either the gate is not locked and the door is open, or the door is open.
- Either the bell is ringing, or the door is open.

Question: Does it follow from these facts that the bell is not ringing or the fan is running?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** follows
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** does not follow (literal counts [0, 1]; max vs illustrative θ = 2)
- **A2 ATMOSPHERE:** does not follow (atm(P) = disj/pos, mood(C) = disj/neg)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 1.000 (ρ = 0.000)
- **NOISY-EXACT:** follows w.p. 0.90
- **PERCEPTION-NOISE:** follows unless a misread breaks it: P(does not follow) = 0.018
- **B1 UP-1:** does not follow (not UP-derivable)
- **B1 UP-2:** does not follow (not UP-derivable)
- **B4 ETR:** does not follow (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** follows
- **B4 MATCH:** follows
- **D case-split (b = 4):** follows
- *params:* `{"atoms": 5, "rho": 0.0, "n_models": 6, "up_depth": null, "kappa_follow": 0.909, "kappa_break": 0.091, "eta_first_counter": null, "etr_what_follows": "{0,a0()a1()~a4()}", "freq_stat": 1, "freq_cell": "lo", "atmosphere_match": false, "words": 10, "propagation_steps_beyond_facts": null}`
- *notes:* Dev-size (5 atoms, 5 premises).

</details>

<details><summary>Prompt and computed outputs — <code>E2-ENT-N-hi-match</code></summary>

```text
Here are some facts about a machine.

- Either the bell is ringing, or the lamp is lit.
- The fan is running.
- Either the lamp is not lit and the bell is ringing, or the door is open.
- Either the gate is not locked and the door is open, or the door is open.
- Either the bell is ringing, or the door is open.

Question: Does it follow from these facts that the bell is ringing or the gate is locked?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** does not follow
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** follows (literal counts [3, 0]; max vs illustrative θ = 2)
- **A2 ATMOSPHERE:** follows (atm(P) = disj/pos, mood(C) = disj/pos)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 0.233 (ρ = 0.167)
- **NOISY-EXACT:** does not follow w.p. 0.90
- **PERCEPTION-NOISE:** does not follow unless a misread makes it follow: P(follows) = 0.036
- **B1 UP-1:** does not follow (not UP-derivable)
- **B1 UP-2:** does not follow (not UP-derivable)
- **B4 ETR:** does not follow (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** follows
- **B4 MATCH:** follows
- **D case-split (b = 4):** follows (first counter-model is #6 of 6 in atom order; budget 4 cases)
- *params:* `{"atoms": 5, "rho": 0.1667, "n_models": 6, "up_depth": null, "kappa_follow": 0.182, "kappa_break": 0.818, "eta_first_counter": 6, "etr_what_follows": "{0,a0()a1()~a4()}", "freq_stat": 3, "freq_cell": "hi", "atmosphere_match": true, "words": 9, "propagation_steps_beyond_facts": null}`
- *notes:* Dev-size (5 atoms, 5 premises).

</details>

<details><summary>Prompt and computed outputs — <code>E2-ENT-N-hi-mis</code></summary>

```text
Here are some facts about a machine.

- Either the bell is ringing, or the lamp is lit.
- The fan is running.
- Either the lamp is not lit and the bell is ringing, or the door is open.
- Either the gate is not locked and the door is open, or the door is open.
- Either the bell is ringing, or the door is open.

Question: Does it follow from these facts that the bell is ringing or the gate is not locked?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** does not follow
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** follows (literal counts [3, 1]; max vs illustrative θ = 2)
- **A2 ATMOSPHERE:** does not follow (atm(P) = disj/pos, mood(C) = disj/neg)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 0.233 (ρ = 0.167)
- **NOISY-EXACT:** does not follow w.p. 0.90
- **PERCEPTION-NOISE:** does not follow unless a misread makes it follow: P(follows) = 0.055
- **B1 UP-1:** does not follow (not UP-derivable)
- **B1 UP-2:** does not follow (not UP-derivable)
- **B4 ETR:** follows (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** follows
- **B4 MATCH:** follows
- **D case-split (b = 4):** follows (first counter-model is #5 of 6 in atom order; budget 4 cases)
- *params:* `{"atoms": 5, "rho": 0.1667, "n_models": 6, "up_depth": null, "kappa_follow": 0.273, "kappa_break": 0.727, "eta_first_counter": 5, "etr_what_follows": "{0,a0()a1()~a4()}", "freq_stat": 3, "freq_cell": "hi", "atmosphere_match": false, "words": 10, "propagation_steps_beyond_facts": null}`
- *notes:* Dev-size (5 atoms, 5 premises).

</details>

<details><summary>Prompt and computed outputs — <code>E2-ENT-N-lo-match</code></summary>

```text
Here are some facts about a machine.

- Either the bell is ringing, or the lamp is lit.
- The fan is running.
- Either the lamp is not lit and the bell is ringing, or the door is open.
- Either the gate is not locked and the door is open, or the door is open.
- Either the bell is ringing, or the door is open.

Question: Does it follow from these facts that the lamp is lit or the gate is locked?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** does not follow
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** does not follow (literal counts [1, 0]; max vs illustrative θ = 2)
- **A2 ATMOSPHERE:** follows (atm(P) = disj/pos, mood(C) = disj/pos)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 0.233 (ρ = 0.167)
- **NOISY-EXACT:** does not follow w.p. 0.90
- **PERCEPTION-NOISE:** does not follow unless a misread makes it follow: P(follows) = 0.000
- **B1 UP-1:** does not follow (not UP-derivable)
- **B1 UP-2:** does not follow (not UP-derivable)
- **B4 ETR:** does not follow (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** does not follow
- **B4 MATCH:** does not follow
- **D case-split (b = 4):** does not follow (first counter-model is #4 of 6 in atom order; budget 4 cases)
- *params:* `{"atoms": 5, "rho": 0.1667, "n_models": 6, "up_depth": null, "kappa_follow": 0.0, "kappa_break": 1.0, "eta_first_counter": 4, "etr_what_follows": "{0,a0()a1()~a4()}", "freq_stat": 1, "freq_cell": "lo", "atmosphere_match": true, "words": 9, "propagation_steps_beyond_facts": null}`
- *notes:* Dev-size (5 atoms, 5 premises).

</details>

<details><summary>Prompt and computed outputs — <code>E2-ENT-N-lo-mis</code></summary>

```text
Here are some facts about a machine.

- Either the bell is ringing, or the lamp is lit.
- The fan is running.
- Either the lamp is not lit and the bell is ringing, or the door is open.
- Either the gate is not locked and the door is open, or the door is open.
- Either the bell is ringing, or the door is open.

Question: Does it follow from these facts that the lamp is lit or the gate is not locked?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** does not follow
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** does not follow (literal counts [1, 1]; max vs illustrative θ = 2)
- **A2 ATMOSPHERE:** does not follow (atm(P) = disj/pos, mood(C) = disj/neg)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 0.233 (ρ = 0.167)
- **NOISY-EXACT:** does not follow w.p. 0.90
- **PERCEPTION-NOISE:** does not follow unless a misread makes it follow: P(follows) = 0.000
- **B1 UP-1:** does not follow (not UP-derivable)
- **B1 UP-2:** does not follow (not UP-derivable)
- **B4 ETR:** does not follow (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** follows
- **B4 MATCH:** follows
- **D case-split (b = 4):** does not follow (first counter-model is #3 of 6 in atom order; budget 4 cases)
- *params:* `{"atoms": 5, "rho": 0.1667, "n_models": 6, "up_depth": null, "kappa_follow": 0.0, "kappa_break": 1.0, "eta_first_counter": 3, "etr_what_follows": "{0,a0()a1()~a4()}", "freq_stat": 1, "freq_cell": "lo", "atmosphere_match": false, "words": 10, "propagation_steps_beyond_facts": null}`
- *notes:* Dev-size (5 atoms, 5 premises).

</details>

**Hypothesis matrix**

| Theory | (a) `E2-ENT-E-hi-match` | (a) `E2-ENT-E-hi-mis` | (a) `E2-ENT-E-lo-match` | (a) `E2-ENT-E-lo-mis` | (a) `E2-ENT-N-hi-match` | (a) `E2-ENT-N-hi-mis` | (a) `E2-ENT-N-lo-match` | (a) `E2-ENT-N-lo-mis` | (b) pure-theory statistic · weight resolution | (c) predicted trace |
|---|---|---|---|---|---|---|---|---|---|---|
| exact | follows | follows | follows | follows | does not follow | does not follow | does not follow | does not follow | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +0.00. π unresolved here vs PERCEPTION-NOISE | A completed procedure: a witness checked against every constraint, or a closed refutation / exhaustive case split. No cue given as a reason. |
| A1 ALWAYS-YES | follows | follows | follows | follows | follows | follows | follows | follows | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +0.00. Detectable π ≥ 0.04 vs B4 FIRST | The conclusion asserted with no derivation and no search for a counter-model. |
| A1 NONE | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +0.00. Detectable π ≥ 0.02 vs H RANDOM-U | 'Nothing definite follows', with no case analysis. |
| A2 FREQ | follows | follows | does not follow | does not follow | follows | follows | does not follow | does not follow | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +1.00. Detectable π ≥ 0.02 vs H RANDOM-U | CUE-FREQ ('the bell ringing comes up most often'). |
| A2 ATMOSPHERE | follows | does not follow | follows | does not follow | follows | does not follow | follows | does not follow | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +0.00. Detectable π ≥ 0.02 vs H RANDOM-U | CUE-MOOD: the conclusion's form or polarity matched to the premises without a derivation. |
| A2 PRIMACY | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +0.00. Detectable π ≥ 0.02 vs H RANDOM-U | CUE-POS on the first premise or option; other options not evaluated. |
| A2 RECENCY | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +0.00. Detectable π ≥ 0.02 vs H RANDOM-U | CUE-POS on the last premise or option. |
| H RANDOM-U | follows w.p. ½ | follows w.p. ½ | follows w.p. ½ | follows w.p. ½ | follows w.p. ½ | follows w.p. ½ | follows w.p. ½ | follows w.p. ½ | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +0.00. Detectable π ≥ 0.00 vs H SAMPLE-8 | No procedure determines the verdict; trace content and verdict unrelated. |
| H SAMPLE-8 | follows w.p. 1.000 | follows w.p. 1.000 | follows w.p. 1.000 | follows w.p. 1.000 | follows w.p. 0.233 | follows w.p. 0.233 | follows w.p. 0.233 | follows w.p. 0.233 | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +0.00. Detectable π ≥ 0.16 vs NOISY-EXACT | SAMPLE(k): at most 8 concrete cases checked, then a universal conclusion; no exhaustive split. |
| NOISY-EXACT | follows w.p. 0.90 | follows w.p. 0.90 | follows w.p. 0.90 | follows w.p. 0.90 | does not follow w.p. 0.90 | does not follow w.p. 0.90 | does not follow w.p. 0.90 | does not follow w.p. 0.90 | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +0.00. Detectable π ≥ 0.25 vs PERCEPTION-NOISE | A systematic procedure; an EVALSLIP precedes every error. |
| PERCEPTION-NOISE | follows | follows | follows | follows | does not follow | does not follow | does not follow | does not follow | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +0.02. π unresolved here vs exact | A MISQUOTE of a constraint (a dropped ¬, a wrong pair, a missing clause); later reasoning consistent with the misquote. |
| B1 UP-1 | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +0.00. Detectable π ≥ 0.02 vs H RANDOM-U | PROP only, one round. |
| B1 UP-2 | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +0.00. Detectable π ≥ 0.02 vs H RANDOM-U | PROP only, two rounds; no case split. |
| B4 ETR | follows | does not follow | does not follow | does not follow | does not follow | follows | does not follow | does not follow | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +0.50. Detectable π ≥ 0.02 vs H RANDOM-U | COMMIT-DISJ / TRUE-ONLY: the disjunct matching the categorical fact kept, the others dropped. |
| B4 FIRST | follows | follows | follows | follows | follows | follows | does not follow | follows | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +0.25. Detectable π ≥ 0.04 vs A1 ALWAYS-YES | COMMIT-DISJ on each first disjunct, never revisited. |
| B4 MATCH | follows | follows | follows | follows | follows | follows | does not follow | follows | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +0.25. Detectable π ≥ 0.04 vs A1 ALWAYS-YES | Picks the disjunct that shares atoms with the categorical fact. |
| D case-split (b = 4) | follows | follows | follows | follows | follows | follows | does not follow | does not follow | P(follows \| FREQ hi) − P(follows \| FREQ lo) = +0.50. Detectable π ≥ 0.04 vs B4 FIRST | A systematic case split abandoned after ≈ 4 cases; 'follows' if no counter-model was found. |

*(c) for every theory: the expected share of traces showing the signature ≈ π_h · r̂ (faithfulness, from E8), plus the coder's false-positive rate.*

**Likelihood ratios per observable pattern** (log₁₀ LR; one study unit)

| Pattern | Favours (log₁₀ LR vs the best theory outside the favoured group) | Pushes toward zero weight (log₁₀ LR vs the best theory) |
|---|---|---|
| follows exactly on the 4 entailed conclusions | exact (+0.4), PERCEPTION-NOISE (+0.4), NOISY-EXACT (+0.2) | A1 ALWAYS-YES (-5.1), A1 NONE (-5.1), A2 FREQ (-5.1), A2 ATMOSPHERE (-5.1), A2 PRIMACY (-5.1), A2 RECENCY (-5.1), B1 UP-1 (-5.1), B1 UP-2 (-5.1), B4 ETR (-5.1), B4 FIRST (-3.8), B4 MATCH (-3.8), D case-split (b = 4) (-2.6), H RANDOM-U (-2.2) |
| follows exactly on the 4 FREQ-hi conclusions | A2 FREQ (+2.2) | exact (-5.1), A1 ALWAYS-YES (-5.1), A1 NONE (-5.1), A2 ATMOSPHERE (-5.1), A2 PRIMACY (-5.1), A2 RECENCY (-5.1), B1 UP-1 (-5.1), B1 UP-2 (-5.1), PERCEPTION-NOISE (-5.1), NOISY-EXACT (-4.0), H SAMPLE-8 (-4.0), B4 FIRST (-3.8), B4 MATCH (-3.8), B4 ETR (-2.6), D case-split (b = 4) (-2.6), H RANDOM-U (-2.2) |
| follows exactly on the 4 atmosphere-matched conclusions | A2 ATMOSPHERE (+2.2) | B4 FIRST (-6.4), B4 MATCH (-6.4), exact (-5.1), A1 ALWAYS-YES (-5.1), A1 NONE (-5.1), A2 FREQ (-5.1), A2 PRIMACY (-5.1), A2 RECENCY (-5.1), PERCEPTION-NOISE (-5.1), B1 UP-1 (-5.1), B1 UP-2 (-5.1), B4 ETR (-5.1), D case-split (b = 4) (-5.1), NOISY-EXACT (-4.0), H SAMPLE-8 (-4.0), H RANDOM-U (-2.2) |
| follows on none | A1 NONE (+2.2), A2 PRIMACY (+2.2), A2 RECENCY (+2.2), B1 UP-1 (+2.2), B1 UP-2 (+2.2) | A1 ALWAYS-YES (-10.2), B4 FIRST (-8.9), B4 MATCH (-8.9), D case-split (b = 4) (-7.7), H SAMPLE-8 (-5.5), exact (-5.1), A2 FREQ (-5.1), A2 ATMOSPHERE (-5.1), PERCEPTION-NOISE (-5.1), NOISY-EXACT (-4.0), B4 ETR (-2.6), H RANDOM-U (-2.2) |
| follows on all | A1 ALWAYS-YES (+1.3) | A1 NONE (-10.2), A2 PRIMACY (-10.2), A2 RECENCY (-10.2), B1 UP-1 (-10.2), B1 UP-2 (-10.2), B4 ETR (-7.7), exact (-5.1), A2 FREQ (-5.1), A2 ATMOSPHERE (-5.1), PERCEPTION-NOISE (-5.1), NOISY-EXACT (-4.0), D case-split (b = 4) (-2.6), H SAMPLE-8 (-2.4), H RANDOM-U (-2.2), B4 FIRST (-1.3), B4 MATCH (-1.3) |

**Weight resolution at study N**

| Theory | Nearest competitor (smallest KL) | Detectable π vs it (80% power) | Upper 95% bound on π if pure competitor | E[log₁₀ BF] vs competitor | Detectable π if the rest is the hardest base (which) | Identical predictions here |
|---|---|---|---|---|---|---|
| exact | PERCEPTION-NOISE | > 1 (unresolved at this N) | > 1 (unresolved at this N) | 0.0 | > 1 (unresolved at this N) (PERCEPTION-NOISE) | — |
| A1 ALWAYS-YES | B4 FIRST | 0.043 | 0.028 | 230.2 | 0.043 (B4 FIRST) | — |
| A1 NONE | H RANDOM-U | 0.016 | 0.011 | 343.7 | 0.016 (H RANDOM-U) | A2 PRIMACY, A2 RECENCY, B1 UP-1, B1 UP-2 |
| A2 FREQ | H RANDOM-U | 0.016 | 0.011 | 343.7 | 0.016 (H RANDOM-U) | — |
| A2 ATMOSPHERE | H RANDOM-U | 0.016 | 0.011 | 343.7 | 0.016 (H RANDOM-U) | — |
| A2 PRIMACY | H RANDOM-U | 0.016 | 0.011 | 343.7 | 0.016 (H RANDOM-U) | A1 NONE, A2 RECENCY, B1 UP-1, B1 UP-2 |
| A2 RECENCY | H RANDOM-U | 0.016 | 0.011 | 343.7 | 0.016 (H RANDOM-U) | A1 NONE, A2 PRIMACY, B1 UP-1, B1 UP-2 |
| H RANDOM-U | H SAMPLE-8 | 0.003 | 0.002 | 347.0 | 0.003 (H SAMPLE-8) | — |
| H SAMPLE-8 | NOISY-EXACT | 0.156 | 0.103 | 31.5 | 0.156 (NOISY-EXACT) | — |
| NOISY-EXACT | PERCEPTION-NOISE | 0.251 | 0.166 | 14.0 | 0.251 (PERCEPTION-NOISE) | — |
| PERCEPTION-NOISE | exact | > 1 (unresolved at this N) | > 1 (unresolved at this N) | 0.0 | > 1 (unresolved at this N) (exact) | — |
| B1 UP-1 | H RANDOM-U | 0.016 | 0.011 | 343.7 | 0.016 (H RANDOM-U) | A1 NONE, A2 PRIMACY, A2 RECENCY, B1 UP-2 |
| B1 UP-2 | H RANDOM-U | 0.016 | 0.011 | 343.7 | 0.016 (H RANDOM-U) | A1 NONE, A2 PRIMACY, A2 RECENCY, B1 UP-1 |
| B4 ETR | H RANDOM-U | 0.016 | 0.011 | 343.7 | 0.016 (H RANDOM-U) | — |
| B4 FIRST | A1 ALWAYS-YES | 0.043 | 0.028 | 230.2 | 0.043 (D case-split (b = 4)) | B4 MATCH |
| B4 MATCH | A1 ALWAYS-YES | 0.043 | 0.028 | 230.2 | 0.043 (D case-split (b = 4)) | B4 FIRST |
| D case-split (b = 4) | B4 FIRST | 0.043 | 0.028 | 230.2 | 0.043 (B4 FIRST) | — |

**Not separated here.** PRIMACY and RECENCY are constant by construction (no conclusion overlaps the first or last premise); the premise-order set E4-order separates them.

<a id="e3"></a>
## E3: four cells of the shared α × n sweep (two share m = 42)

**Reasoning question.** Is the decision knee fixed in α, fixed in m, or does it follow g?

**Design.** Two cells with equal m and different α, plus the low/high-α corners. N = 120 assumes 40 matched units in each of three n-pairs of the sweep.  *Study units:* four cells × 120.

| Item | Cell | Ground truth | Controlled | Varied |
|---|---|---|---|---|
| `E3-n8-a3.5` | n = 8, α = 3.50 (m = 28) | SAT | generator and framing | α and n; the two middle cells share m = 42 but differ in α |
| `E3-n8-a5.25` | n = 8, α = 5.25 (m = 42) | SAT | generator and framing | α and n; the two middle cells share m = 42 but differ in α |
| `E3-n12-a3.5` | n = 12, α = 3.50 (m = 42) | SAT | generator and framing | α and n; the two middle cells share m = 42 but differ in α |
| `E3-n12-a5.25` | n = 12, α = 5.25 (m = 63) | UNSAT | generator and framing | α and n; the two middle cells share m = 42 but differ in α |

<details><summary>Prompt and computed outputs — <code>E3-n8-a3.5</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (¬x01 ∨ x04 ∨ x08)
C02: (¬x02 ∨ x05 ∨ ¬x08)
C03: (x01 ∨ ¬x06 ∨ x08)
C04: (x07 ∨ x02 ∨ ¬x05)
C05: (x07 ∨ x03 ∨ ¬x02)
C06: (x04 ∨ ¬x02 ∨ ¬x06)
C07: (x01 ∨ x07 ∨ ¬x02)
C08: (¬x07 ∨ ¬x01 ∨ ¬x08)
C09: (¬x04 ∨ x02 ∨ ¬x08)
C10: (x04 ∨ x08 ∨ ¬x01)
C11: (¬x08 ∨ ¬x06 ∨ ¬x07)
C12: (¬x02 ∨ ¬x07 ∨ ¬x03)
C13: (x05 ∨ ¬x01 ∨ ¬x02)
C14: (x02 ∨ x06 ∨ ¬x04)
C15: (x04 ∨ x01 ∨ x08)
C16: (x01 ∨ x05 ∨ ¬x06)
C17: (x02 ∨ ¬x08 ∨ ¬x07)
C18: (¬x08 ∨ ¬x01 ∨ ¬x04)
C19: (x08 ∨ x06 ∨ x05)
C20: (x08 ∨ ¬x07 ∨ ¬x01)
C21: (x06 ∨ ¬x02 ∨ x01)
C22: (¬x01 ∨ ¬x02 ∨ ¬x08)
C23: (¬x04 ∨ ¬x07 ∨ ¬x02)
C24: (¬x08 ∨ ¬x05 ∨ ¬x06)
C25: (¬x04 ∨ x05 ∨ ¬x02)
C26: (x08 ∨ ¬x03 ∨ x02)
C27: (x04 ∨ ¬x03 ∨ x06)
C28: (x02 ∨ x06 ∨ ¬x04)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** SAT, e.g. 11111000 (7 solutions)
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 3.5 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** SAT (α_U = 3.50 vs θ = 4.26)
- **A2 DENSITY-D:** SAT (α_D = 3.50 vs θ = 4.26)
- **A2 LENGTH-M:** SAT (m = 28 vs illustrative θ_m = 40)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 3.5 clauses
- **H SAMPLE-8:** P(SAT) = 0.199 (7 solutions in 2^8)
- **NOISY-EXACT-STEP:** SAT w.p. 0.98 (L = 2 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** SAT w.p. 0.88 (L = m = 28, p = 0.01/clause)
- **PERCEPTION-NOISE:** SAT (dropped clauses cannot remove solutions)
- **C0 POLARITY:** SAT, witness 00001100 (3 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 00001011 violates 1)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** SAT (exact: 2 decisions ≤ illustrative b = 8)
- **F WALK-200:** SAT in 100% of runs, else UNSAT by default
- **D∘DENSITY (b=4):** SAT (search finishes in 2 ≤ 4 decisions)
- *params:* `{"n_used": 8, "n_decl": 8, "m": 28, "alpha_U": 3.5, "alpha_D": 3.5, "n_solutions": 7, "dpll_decisions": 2, "dpll_decisions_pure_literal": 2, "polarity_witness": "00001100", "polarity_violations": 3, "greedy_witness": "00001011", "greedy_violations": 1, "dpll_witness": "11111100"}`
- *notes:* Four cells of the shared sweep; (n = 8, α = 5.25) is a SAT item at high α, chosen so DENSITY errs.

</details>

<details><summary>Prompt and computed outputs — <code>E3-n8-a5.25</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x05 ∨ x07 ∨ x02)
C02: (x06 ∨ x05 ∨ x02)
C03: (¬x01 ∨ x03 ∨ x04)
C04: (x05 ∨ x02 ∨ x06)
C05: (¬x05 ∨ x07 ∨ x06)
C06: (¬x08 ∨ x07 ∨ ¬x03)
C07: (x03 ∨ ¬x08 ∨ ¬x06)
C08: (¬x01 ∨ ¬x02 ∨ x06)
C09: (x05 ∨ x06 ∨ x02)
C10: (¬x08 ∨ x06 ∨ x03)
C11: (¬x05 ∨ x04 ∨ x03)
C12: (¬x01 ∨ ¬x08 ∨ ¬x04)
C13: (¬x08 ∨ ¬x04 ∨ ¬x01)
C14: (¬x08 ∨ ¬x04 ∨ x05)
C15: (¬x01 ∨ x04 ∨ x03)
C16: (¬x04 ∨ x02 ∨ ¬x08)
C17: (¬x04 ∨ ¬x02 ∨ x05)
C18: (¬x01 ∨ ¬x03 ∨ x07)
C19: (x07 ∨ ¬x04 ∨ x01)
C20: (x08 ∨ x06 ∨ ¬x07)
C21: (¬x02 ∨ ¬x03 ∨ x07)
C22: (x03 ∨ x01 ∨ ¬x02)
C23: (¬x08 ∨ x01 ∨ x03)
C24: (x01 ∨ ¬x07 ∨ x05)
C25: (x04 ∨ ¬x02 ∨ x03)
C26: (x02 ∨ ¬x07 ∨ ¬x08)
C27: (¬x06 ∨ ¬x01 ∨ x03)
C28: (¬x03 ∨ x04 ∨ ¬x05)
C29: (¬x04 ∨ x05 ∨ x07)
C30: (x06 ∨ x05 ∨ x07)
C31: (¬x03 ∨ ¬x05 ∨ ¬x07)
C32: (x07 ∨ ¬x06 ∨ x05)
C33: (¬x05 ∨ x06 ∨ x08)
C34: (x07 ∨ x05 ∨ x01)
C35: (x04 ∨ ¬x01 ∨ ¬x08)
C36: (x04 ∨ ¬x06 ∨ ¬x03)
C37: (¬x07 ∨ ¬x04 ∨ x03)
C38: (¬x06 ∨ ¬x02 ∨ ¬x01)
C39: (¬x05 ∨ ¬x08 ∨ ¬x02)
C40: (¬x04 ∨ ¬x05 ∨ x08)
C41: (¬x05 ∨ ¬x07 ∨ ¬x03)
C42: (¬x05 ∨ x03 ∨ ¬x07)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** SAT, e.g. 10110110 (1 solution)
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 5.2 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** UNSAT (α_U = 5.25 vs θ = 4.26)
- **A2 DENSITY-D:** UNSAT (α_D = 5.25 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 42 vs illustrative θ_m = 40)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 5.2 clauses
- **H SAMPLE-8:** P(SAT) = 0.031 (1 solutions in 2^8)
- **NOISY-EXACT-STEP:** SAT w.p. 0.96 (L = 4 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** SAT w.p. 0.83 (L = m = 42, p = 0.01/clause)
- **PERCEPTION-NOISE:** SAT (dropped clauses cannot remove solutions)
- **C0 POLARITY:** SAT, witness 00101110 (4 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 01100111 violates 2)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** SAT (exact: 4 decisions ≤ illustrative b = 8)
- **F WALK-200:** SAT in 100% of runs, else UNSAT by default
- **D∘DENSITY (b=4):** SAT (search finishes in 4 ≤ 4 decisions)
- *params:* `{"n_used": 8, "n_decl": 8, "m": 42, "alpha_U": 5.25, "alpha_D": 5.25, "n_solutions": 1, "dpll_decisions": 4, "dpll_decisions_pure_literal": 4, "polarity_witness": "00101110", "polarity_violations": 4, "greedy_witness": "01100111", "greedy_violations": 2, "dpll_witness": "10110110"}`
- *notes:* Four cells of the shared sweep; (n = 8, α = 5.25) is a SAT item at high α, chosen so DENSITY errs.

</details>

<details><summary>Prompt and computed outputs — <code>E3-n12-a3.5</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (¬x11 ∨ ¬x10 ∨ ¬x12)
C02: (¬x06 ∨ x02 ∨ ¬x09)
C03: (¬x06 ∨ x07 ∨ ¬x01)
C04: (¬x01 ∨ x02 ∨ x10)
C05: (¬x12 ∨ ¬x08 ∨ ¬x07)
C06: (x02 ∨ x10 ∨ x01)
C07: (¬x02 ∨ ¬x07 ∨ ¬x10)
C08: (¬x09 ∨ x03 ∨ ¬x02)
C09: (¬x07 ∨ x11 ∨ x01)
C10: (¬x01 ∨ ¬x06 ∨ x10)
C11: (x09 ∨ x03 ∨ x10)
C12: (¬x01 ∨ ¬x11 ∨ x07)
C13: (¬x12 ∨ ¬x03 ∨ ¬x09)
C14: (x10 ∨ x05 ∨ x04)
C15: (¬x08 ∨ x09 ∨ ¬x06)
C16: (¬x09 ∨ x07 ∨ ¬x02)
C17: (x11 ∨ x08 ∨ ¬x01)
C18: (x12 ∨ x05 ∨ x11)
C19: (x11 ∨ ¬x04 ∨ ¬x01)
C20: (¬x04 ∨ ¬x11 ∨ x05)
C21: (x03 ∨ x05 ∨ ¬x08)
C22: (¬x04 ∨ ¬x12 ∨ ¬x06)
C23: (¬x05 ∨ ¬x12 ∨ ¬x09)
C24: (x01 ∨ ¬x05 ∨ x11)
C25: (x10 ∨ x08 ∨ ¬x01)
C26: (¬x04 ∨ x01 ∨ ¬x06)
C27: (x11 ∨ x07 ∨ x12)
C28: (x05 ∨ ¬x10 ∨ ¬x08)
C29: (¬x12 ∨ ¬x05 ∨ ¬x10)
C30: (x04 ∨ ¬x10 ∨ x08)
C31: (¬x05 ∨ x09 ∨ ¬x10)
C32: (¬x01 ∨ x08 ∨ ¬x11)
C33: (¬x12 ∨ x10 ∨ x05)
C34: (x04 ∨ ¬x06 ∨ ¬x07)
C35: (¬x05 ∨ ¬x01 ∨ ¬x07)
C36: (x11 ∨ ¬x06 ∨ x09)
C37: (x03 ∨ ¬x08 ∨ ¬x04)
C38: (¬x01 ∨ ¬x02 ∨ x07)
C39: (¬x02 ∨ x10 ∨ x07)
C40: (¬x05 ∨ x10 ∨ x09)
C41: (¬x04 ∨ ¬x01 ∨ ¬x07)
C42: (¬x09 ∨ ¬x08 ∨ x10)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** SAT, e.g. 011010101010 (17 solutions)
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 5.2 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** SAT (α_U = 3.50 vs θ = 4.26)
- **A2 DENSITY-D:** SAT (α_D = 3.50 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 42 vs illustrative θ_m = 40)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 5.2 clauses
- **H SAMPLE-8:** P(SAT) = 0.033 (17 solutions in 2^12)
- **NOISY-EXACT-STEP:** SAT w.p. 0.87 (L = 15 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** SAT w.p. 0.83 (L = m = 42, p = 0.01/clause)
- **PERCEPTION-NOISE:** SAT (dropped clauses cannot remove solutions)
- **C0 POLARITY:** SAT, witness 001010100110 (2 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 001100000110 violates 1)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** UNSAT by default (15 decisions > illustrative b = 8)
- **F WALK-200:** SAT in 100% of runs, else UNSAT by default
- **D∘DENSITY (b=4):** SAT (budget exceeded at 15 decisions → density default)
- *params:* `{"n_used": 12, "n_decl": 12, "m": 42, "alpha_U": 3.5, "alpha_D": 3.5, "n_solutions": 17, "dpll_decisions": 15, "dpll_decisions_pure_literal": 15, "polarity_witness": "001010100110", "polarity_violations": 2, "greedy_witness": "001100000110", "greedy_violations": 1, "dpll_witness": "011110101010"}`
- *notes:* Four cells of the shared sweep; (n = 8, α = 5.25) is a SAT item at high α, chosen so DENSITY errs.

</details>

<details><summary>Prompt and computed outputs — <code>E3-n12-a5.25</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x06 ∨ ¬x12 ∨ ¬x08)
C02: (¬x03 ∨ ¬x01 ∨ ¬x02)
C03: (x05 ∨ x06 ∨ x04)
C04: (¬x03 ∨ ¬x10 ∨ x12)
C05: (¬x02 ∨ x07 ∨ x04)
C06: (x11 ∨ x07 ∨ x03)
C07: (x01 ∨ ¬x09 ∨ x12)
C08: (x10 ∨ x11 ∨ ¬x02)
C09: (¬x04 ∨ ¬x10 ∨ ¬x08)
C10: (x03 ∨ x04 ∨ x06)
C11: (¬x10 ∨ x09 ∨ ¬x01)
C12: (¬x11 ∨ ¬x05 ∨ x04)
C13: (x06 ∨ ¬x10 ∨ ¬x05)
C14: (¬x03 ∨ x04 ∨ ¬x06)
C15: (¬x08 ∨ x02 ∨ ¬x01)
C16: (¬x10 ∨ x08 ∨ x11)
C17: (¬x06 ∨ x10 ∨ x07)
C18: (¬x09 ∨ ¬x12 ∨ ¬x11)
C19: (x05 ∨ x07 ∨ ¬x08)
C20: (¬x08 ∨ x01 ∨ ¬x03)
C21: (x12 ∨ ¬x01 ∨ x09)
C22: (x09 ∨ ¬x01 ∨ ¬x04)
C23: (x10 ∨ ¬x01 ∨ x03)
C24: (x01 ∨ ¬x04 ∨ ¬x10)
C25: (¬x04 ∨ x12 ∨ ¬x10)
C26: (x08 ∨ x12 ∨ x07)
C27: (x06 ∨ x11 ∨ x12)
C28: (x04 ∨ ¬x10 ∨ x08)
C29: (¬x09 ∨ ¬x05 ∨ x12)
C30: (¬x04 ∨ x10 ∨ ¬x02)
C31: (x09 ∨ ¬x12 ∨ x05)
C32: (x02 ∨ x08 ∨ x11)
C33: (¬x03 ∨ ¬x07 ∨ x08)
C34: (¬x09 ∨ ¬x03 ∨ ¬x01)
C35: (x09 ∨ x01 ∨ ¬x11)
C36: (¬x09 ∨ ¬x03 ∨ x11)
C37: (x11 ∨ ¬x08 ∨ ¬x05)
C38: (¬x09 ∨ x07 ∨ x05)
C39: (x05 ∨ x11 ∨ x03)
C40: (¬x05 ∨ ¬x11 ∨ x06)
C41: (x11 ∨ ¬x03 ∨ x01)
C42: (¬x03 ∨ ¬x06 ∨ x04)
C43: (¬x06 ∨ ¬x04 ∨ ¬x10)
C44: (¬x08 ∨ ¬x12 ∨ ¬x07)
C45: (¬x04 ∨ ¬x11 ∨ ¬x07)
C46: (¬x02 ∨ x05 ∨ x12)
C47: (¬x03 ∨ ¬x04 ∨ ¬x09)
C48: (x02 ∨ x08 ∨ x10)
C49: (x03 ∨ x02 ∨ ¬x12)
C50: (x04 ∨ x01 ∨ ¬x11)
C51: (x12 ∨ x06 ∨ x09)
C52: (x10 ∨ ¬x08 ∨ ¬x05)
C53: (x10 ∨ ¬x04 ∨ x05)
C54: (x06 ∨ x08 ∨ x07)
C55: (¬x12 ∨ ¬x01 ∨ ¬x10)
C56: (¬x02 ∨ ¬x06 ∨ x10)
C57: (x10 ∨ ¬x07 ∨ ¬x02)
C58: (¬x03 ∨ x09 ∨ x05)
C59: (¬x04 ∨ x06 ∨ ¬x09)
C60: (x04 ∨ ¬x09 ∨ x08)
C61: (x01 ∨ ¬x04 ∨ x06)
C62: (x12 ∨ x05 ∨ x11)
C63: (¬x11 ∨ ¬x06 ∨ x02)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** UNSAT
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 7.9 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** UNSAT (α_U = 5.25 vs θ = 4.26)
- **A2 DENSITY-D:** UNSAT (α_D = 5.25 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 63 vs illustrative θ_m = 40)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 7.9 clauses
- **H SAMPLE-8:** P(SAT) = 0.000 (0 solutions in 2^12)
- **NOISY-EXACT-STEP:** UNSAT w.p. 0.89 (L = 12 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** UNSAT w.p. 0.77 (L = m = 63, p = 0.01/clause)
- **PERCEPTION-NOISE:** P(SAT) = 0.112 at p_d = 0.05 (2 necessary clauses)
- **C0 POLARITY:** SAT, witness 000011110011 (7 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 000011110100 violates 1)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** UNSAT by default (12 decisions > illustrative b = 8)
- **F WALK-200:** UNSAT by default (never certifies)
- **D∘DENSITY (b=4):** UNSAT (budget exceeded at 12 decisions → density default)
- *params:* `{"n_used": 12, "n_decl": 12, "m": 63, "alpha_U": 5.25, "alpha_D": 5.25, "n_solutions": 0, "dpll_decisions": 12, "dpll_decisions_pure_literal": 12, "polarity_witness": "000011110011", "polarity_violations": 7, "greedy_witness": "000011110100", "greedy_violations": 1, "dpll_witness": null}`
- *notes:* Four cells of the shared sweep; (n = 8, α = 5.25) is a SAT item at high α, chosen so DENSITY errs.

</details>

**Hypothesis matrix**

| Theory | (a) `E3-n8-a3.5` | (a) `E3-n8-a5.25` | (a) `E3-n12-a3.5` | (a) `E3-n12-a5.25` | (b) pure-theory statistic · weight resolution | (c) predicted trace |
|---|---|---|---|---|---|---|
| exact | SAT | SAT | SAT | UNSAT | P(UNSAT \| n=8, α=5.25) − P(UNSAT \| n=12, α=3.5)  [equal m = 42] = +0.00. Detectable π ≥ 0.74 vs NOISY-EXACT-STEP | A completed procedure: a witness checked against every constraint, or a closed refutation / exhaustive case split. No cue given as a reason. |
| A1 ALWAYS-UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | P(UNSAT \| n=8, α=5.25) − P(UNSAT \| n=12, α=3.5)  [equal m = 42] = +0.00. Detectable π ≥ 0.61 vs H SAMPLE-8 | GIVEUP early ('too many constraints to check'); no witness attempted. |
| A2 DENSITY-U | SAT | UNSAT | SAT | UNSAT | P(UNSAT \| n=8, α=5.25) − P(UNSAT \| n=12, α=3.5)  [equal m = 42] = +1.00. Detectable π ≥ 0.07 vs H RANDOM-U | CUE-DENS as the reason ('about 4.3 clauses per variable is near the hard threshold'); no closed refutation; padding variables not treated specially. |
| A2 LENGTH-M | SAT | UNSAT | UNSAT | UNSAT | P(UNSAT \| n=8, α=5.25) − P(UNSAT \| n=12, α=3.5)  [equal m = 42] = +0.00. Detectable π ≥ 0.12 vs H SAMPLE-8 | CUE-SIZE as the reason ('with this many clauses it is very likely unsatisfiable'). |
| H RANDOM-U | SAT or UNSAT w.p. ½; a random witness violates ≈ 3.5 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 5.2 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 5.2 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 7.9 clauses | P(UNSAT \| n=8, α=5.25) − P(UNSAT \| n=12, α=3.5)  [equal m = 42] = +0.00. Detectable π ≥ 0.02 vs NOISY-EXACT-STEP | No procedure determines the verdict; trace content and verdict unrelated. |
| H SAMPLE-8 | P(SAT) = 0.199 | P(SAT) = 0.031 | P(SAT) = 0.033 | P(SAT) = 0.000 | P(UNSAT \| n=8, α=5.25) − P(UNSAT \| n=12, α=3.5)  [equal m = 42] = +0.00. Detectable π ≥ 0.33 vs A1 ALWAYS-UNSAT | SAMPLE(k): at most 8 concrete cases checked, then a universal conclusion; no exhaustive split. |
| NOISY-EXACT-STEP | SAT w.p. 0.98 | SAT w.p. 0.96 | SAT w.p. 0.87 | UNSAT w.p. 0.89 | P(UNSAT \| n=8, α=5.25) − P(UNSAT \| n=12, α=3.5)  [equal m = 42] = -0.09. Detectable π ≥ 0.49 vs exact | A systematic procedure; an EVALSLIP (a constraint evaluated wrongly under the trace's own assignment) precedes every error. |
| C1 GREEDY | UNSAT | UNSAT | UNSAT | UNSAT | P(UNSAT \| n=8, α=5.25) − P(UNSAT \| n=12, α=3.5)  [equal m = 42] = +0.00. Detectable π ≥ 0.61 vs H SAMPLE-8 | One ASSIGN pass in index order, no BACKTRACK; at a dead end, GIVEUP or an invalid witness. |
| D DPLL-b | SAT | SAT | UNSAT | UNSAT | P(UNSAT \| n=8, α=5.25) − P(UNSAT \| n=12, α=3.5)  [equal m = 42] = -1.00. Detectable π ≥ 0.09 vs NOISY-EXACT-STEP | BRANCH / CONTRA / BACKTRACK; ends in a witness, a closed refutation, or the cap. |
| F WALK-200 | SAT in 100% of runs | SAT in 100% of runs | SAT in 100% of runs | UNSAT | P(UNSAT \| n=8, α=5.25) − P(UNSAT \| n=12, α=3.5)  [equal m = 42] = +0.00. Detectable π ≥ 0.74 vs NOISY-EXACT-STEP | REPAIR loops: a full candidate, its violated clauses listed, flips; never a refutation. |

*(c) for every theory: the expected share of traces showing the signature ≈ π_h · r̂ (faithfulness, from E8), plus the coder's false-positive rate.*

**Likelihood ratios per observable pattern** (log₁₀ LR; one study unit)

| Pattern | Favours (log₁₀ LR vs the best theory outside the favoured group) | Pushes toward zero weight (log₁₀ LR vs the best theory) |
|---|---|---|
| m = 42 cells: (n=8, α=5.25) UNSAT, (n=12, α=3.5) SAT | A2 DENSITY-U (+0.6) | D DPLL-b (-2.6), NOISY-EXACT-STEP (-1.3), exact (-1.3), A1 ALWAYS-UNSAT (-1.3), A2 LENGTH-M (-1.3), H SAMPLE-8 (-1.3), C1 GREEDY (-1.3), F WALK-200 (-1.3) |
| m = 42 cells: both SAT | exact (+0.6), F WALK-200 (+0.6), NOISY-EXACT-STEP (+0.5) | A1 ALWAYS-UNSAT (-2.6), A2 LENGTH-M (-2.6), H SAMPLE-8 (-2.6), C1 GREEDY (-2.6), A2 DENSITY-U (-1.3), D DPLL-b (-1.3) |
| m = 42 cells: both UNSAT | A1 ALWAYS-UNSAT (+0.6), A2 LENGTH-M (+0.6), H SAMPLE-8 (+0.6), C1 GREEDY (+0.6) | exact (-2.6), F WALK-200 (-2.6), NOISY-EXACT-STEP (-2.1), A2 DENSITY-U (-1.3), D DPLL-b (-1.3) |
| all four answered as g (SAT, SAT, SAT, UNSAT) | exact (+1.1), F WALK-200 (+1.1), NOISY-EXACT-STEP (+1.1) | A1 ALWAYS-UNSAT (-3.8), C1 GREEDY (-3.8), H SAMPLE-8 (-3.2), A2 LENGTH-M (-2.6), A2 DENSITY-U (-1.3), D DPLL-b (-1.3), H RANDOM-U (-1.1) |

**Weight resolution at study N**

| Theory | Nearest competitor (smallest KL) | Detectable π vs it (80% power) | Upper 95% bound on π if pure competitor | E[log₁₀ BF] vs competitor | Detectable π if the rest is the hardest base (which) | Identical predictions here |
|---|---|---|---|---|---|---|
| exact | NOISY-EXACT-STEP | 0.741 | 0.490 | 3.0 | 0.741 (NOISY-EXACT-STEP) | F WALK-200 |
| A1 ALWAYS-UNSAT | H SAMPLE-8 | 0.608 | 0.403 | 4.8 | 0.608 (H SAMPLE-8) | C1 GREEDY |
| A2 DENSITY-U | H RANDOM-U | 0.073 | 0.048 | 103.1 | 0.073 (H RANDOM-U) | — |
| A2 LENGTH-M | H SAMPLE-8 | 0.121 | 0.080 | 70.2 | 0.121 (H SAMPLE-8) | — |
| H RANDOM-U | NOISY-EXACT-STEP | 0.018 | 0.012 | 132.0 | 0.018 (NOISY-EXACT-STEP) | — |
| H SAMPLE-8 | A1 ALWAYS-UNSAT | 0.332 | 0.220 | 7.2 | 0.332 (A1 ALWAYS-UNSAT) | — |
| NOISY-EXACT-STEP | exact | 0.488 | 0.323 | 3.9 | 0.488 (exact) | — |
| C1 GREEDY | H SAMPLE-8 | 0.608 | 0.403 | 4.8 | 0.608 (H SAMPLE-8) | A1 ALWAYS-UNSAT |
| D DPLL-b | NOISY-EXACT-STEP | 0.092 | 0.061 | 91.9 | 0.092 (NOISY-EXACT-STEP) | — |
| F WALK-200 | NOISY-EXACT-STEP | 0.741 | 0.490 | 3.0 | 0.741 (NOISY-EXACT-STEP) | exact |

**Not separated here.** Four items cannot estimate a knee; the full sweep fits {α*(n), b_n} (vertical doc E3). Theories exact on all four cells are not separated here.

<a id="e4"></a>
## E4: one MC item in 4 rotations × 2 label schemes

**Reasoning question.** Does the choice follow position, label token, cues, or content?

**Design.** Identical premises and options; only order and label scheme vary. N = 200 items × 8 renderings.  *Study units:* 8 renderings × 200.

| Item | Cell | Ground truth | Controlled | Varied |
|---|---|---|---|---|
| `E4-r0-AD` | rotation 0, labels A–D | A | premises and the four option texts (identical in all 8 renderings) | option position (4 cyclic rotations) × label scheme (A–D or D–A, top to bottom) |
| `E4-r1-AD` | rotation 1, labels A–D | D | premises and the four option texts (identical in all 8 renderings) | option position (4 cyclic rotations) × label scheme (A–D or D–A, top to bottom) |
| `E4-r2-AD` | rotation 2, labels A–D | C | premises and the four option texts (identical in all 8 renderings) | option position (4 cyclic rotations) × label scheme (A–D or D–A, top to bottom) |
| `E4-r3-AD` | rotation 3, labels A–D | B | premises and the four option texts (identical in all 8 renderings) | option position (4 cyclic rotations) × label scheme (A–D or D–A, top to bottom) |
| `E4-r0-DA` | rotation 0, labels D–A | D | premises and the four option texts (identical in all 8 renderings) | option position (4 cyclic rotations) × label scheme (A–D or D–A, top to bottom) |
| `E4-r1-DA` | rotation 1, labels D–A | A | premises and the four option texts (identical in all 8 renderings) | option position (4 cyclic rotations) × label scheme (A–D or D–A, top to bottom) |
| `E4-r2-DA` | rotation 2, labels D–A | B | premises and the four option texts (identical in all 8 renderings) | option position (4 cyclic rotations) × label scheme (A–D or D–A, top to bottom) |
| `E4-r3-DA` | rotation 3, labels D–A | C | premises and the four option texts (identical in all 8 renderings) | option position (4 cyclic rotations) × label scheme (A–D or D–A, top to bottom) |

<details><summary>Prompt and computed outputs — <code>E4-r0-AD</code></summary>

```text
Here are some facts about a machine.

- Either the bell is ringing and the fan is not running, or the fan is running and the door is open.
- Either the gate is locked, or the lamp is lit and the door is open.
- The fan is not running.

Which one of the following conclusions necessarily follows from these facts?
A. The bell is ringing.
B. The lamp is lit.
C. The gate is locked.
D. The door is open or the lamp is lit.
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"choice": "<letter>"}
```

- **exact:** A
- **A2 PRIMACY:** A
- **A2 RECENCY:** D
- **LABEL-A:** A
- **A2 FREQ / ATMOSPHERE:** D
- **A2 LENGTH-SHORT:** A
- **B4 ETR:** B
- **B4 FIRST:** C
- **H SAMPLE-8:** A
- **H RANDOM-U:** uniform
- **satisficing (C-type sequential check):** A if 'correct' passes its check
- *params:* `{"option_order_top_to_bottom": ["correct", "ETR", "FIRST", "cue"], "labels_top_to_bottom": ["A", "B", "C", "D"], "option_words": {"correct": 4, "ETR": 4, "FIRST": 4, "cue": 9}, "freq_score": {"correct": 1.0, "ETR": 1.0, "FIRST": 1.0, "cue": 1.5}, "mood": {"correct": "conj/pos", "ETR": "conj/pos", "FIRST": "conj/pos", "cue": "disj/pos"}, "atmosphere": "disj/pos"}`
- *notes:* Exactly one option is entailed (model enumeration); the ETR option is endorsed by PyETR; the FIRST option follows when each 'either' is read as its first disjunct.

</details>

<details><summary>Prompt and computed outputs — <code>E4-r1-AD</code></summary>

```text
Here are some facts about a machine.

- Either the bell is ringing and the fan is not running, or the fan is running and the door is open.
- Either the gate is locked, or the lamp is lit and the door is open.
- The fan is not running.

Which one of the following conclusions necessarily follows from these facts?
A. The lamp is lit.
B. The gate is locked.
C. The door is open or the lamp is lit.
D. The bell is ringing.
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"choice": "<letter>"}
```

- **exact:** D
- **A2 PRIMACY:** A
- **A2 RECENCY:** D
- **LABEL-A:** A
- **A2 FREQ / ATMOSPHERE:** C
- **A2 LENGTH-SHORT:** A
- **B4 ETR:** A
- **B4 FIRST:** B
- **H SAMPLE-8:** D
- **H RANDOM-U:** uniform
- **satisficing (C-type sequential check):** A if 'ETR' passes its check
- *params:* `{"option_order_top_to_bottom": ["ETR", "FIRST", "cue", "correct"], "labels_top_to_bottom": ["A", "B", "C", "D"], "option_words": {"correct": 4, "ETR": 4, "FIRST": 4, "cue": 9}, "freq_score": {"correct": 1.0, "ETR": 1.0, "FIRST": 1.0, "cue": 1.5}, "mood": {"correct": "conj/pos", "ETR": "conj/pos", "FIRST": "conj/pos", "cue": "disj/pos"}, "atmosphere": "disj/pos"}`
- *notes:* Exactly one option is entailed (model enumeration); the ETR option is endorsed by PyETR; the FIRST option follows when each 'either' is read as its first disjunct.

</details>

<details><summary>Prompt and computed outputs — <code>E4-r2-AD</code></summary>

```text
Here are some facts about a machine.

- Either the bell is ringing and the fan is not running, or the fan is running and the door is open.
- Either the gate is locked, or the lamp is lit and the door is open.
- The fan is not running.

Which one of the following conclusions necessarily follows from these facts?
A. The gate is locked.
B. The door is open or the lamp is lit.
C. The bell is ringing.
D. The lamp is lit.
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"choice": "<letter>"}
```

- **exact:** C
- **A2 PRIMACY:** A
- **A2 RECENCY:** D
- **LABEL-A:** A
- **A2 FREQ / ATMOSPHERE:** B
- **A2 LENGTH-SHORT:** A
- **B4 ETR:** D
- **B4 FIRST:** A
- **H SAMPLE-8:** C
- **H RANDOM-U:** uniform
- **satisficing (C-type sequential check):** A if 'FIRST' passes its check
- *params:* `{"option_order_top_to_bottom": ["FIRST", "cue", "correct", "ETR"], "labels_top_to_bottom": ["A", "B", "C", "D"], "option_words": {"correct": 4, "ETR": 4, "FIRST": 4, "cue": 9}, "freq_score": {"correct": 1.0, "ETR": 1.0, "FIRST": 1.0, "cue": 1.5}, "mood": {"correct": "conj/pos", "ETR": "conj/pos", "FIRST": "conj/pos", "cue": "disj/pos"}, "atmosphere": "disj/pos"}`
- *notes:* Exactly one option is entailed (model enumeration); the ETR option is endorsed by PyETR; the FIRST option follows when each 'either' is read as its first disjunct.

</details>

<details><summary>Prompt and computed outputs — <code>E4-r3-AD</code></summary>

```text
Here are some facts about a machine.

- Either the bell is ringing and the fan is not running, or the fan is running and the door is open.
- Either the gate is locked, or the lamp is lit and the door is open.
- The fan is not running.

Which one of the following conclusions necessarily follows from these facts?
A. The door is open or the lamp is lit.
B. The bell is ringing.
C. The lamp is lit.
D. The gate is locked.
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"choice": "<letter>"}
```

- **exact:** B
- **A2 PRIMACY:** A
- **A2 RECENCY:** D
- **LABEL-A:** A
- **A2 FREQ / ATMOSPHERE:** A
- **A2 LENGTH-SHORT:** B
- **B4 ETR:** C
- **B4 FIRST:** D
- **H SAMPLE-8:** B
- **H RANDOM-U:** uniform
- **satisficing (C-type sequential check):** A if 'cue' passes its check
- *params:* `{"option_order_top_to_bottom": ["cue", "correct", "ETR", "FIRST"], "labels_top_to_bottom": ["A", "B", "C", "D"], "option_words": {"correct": 4, "ETR": 4, "FIRST": 4, "cue": 9}, "freq_score": {"correct": 1.0, "ETR": 1.0, "FIRST": 1.0, "cue": 1.5}, "mood": {"correct": "conj/pos", "ETR": "conj/pos", "FIRST": "conj/pos", "cue": "disj/pos"}, "atmosphere": "disj/pos"}`
- *notes:* Exactly one option is entailed (model enumeration); the ETR option is endorsed by PyETR; the FIRST option follows when each 'either' is read as its first disjunct.

</details>

<details><summary>Prompt and computed outputs — <code>E4-r0-DA</code></summary>

```text
Here are some facts about a machine.

- Either the bell is ringing and the fan is not running, or the fan is running and the door is open.
- Either the gate is locked, or the lamp is lit and the door is open.
- The fan is not running.

Which one of the following conclusions necessarily follows from these facts?
D. The bell is ringing.
C. The lamp is lit.
B. The gate is locked.
A. The door is open or the lamp is lit.
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"choice": "<letter>"}
```

- **exact:** D
- **A2 PRIMACY:** D
- **A2 RECENCY:** A
- **LABEL-A:** A
- **A2 FREQ / ATMOSPHERE:** A
- **A2 LENGTH-SHORT:** D
- **B4 ETR:** C
- **B4 FIRST:** B
- **H SAMPLE-8:** D
- **H RANDOM-U:** uniform
- **satisficing (C-type sequential check):** D if 'correct' passes its check
- *params:* `{"option_order_top_to_bottom": ["correct", "ETR", "FIRST", "cue"], "labels_top_to_bottom": ["D", "C", "B", "A"], "option_words": {"correct": 4, "ETR": 4, "FIRST": 4, "cue": 9}, "freq_score": {"correct": 1.0, "ETR": 1.0, "FIRST": 1.0, "cue": 1.5}, "mood": {"correct": "conj/pos", "ETR": "conj/pos", "FIRST": "conj/pos", "cue": "disj/pos"}, "atmosphere": "disj/pos"}`
- *notes:* Exactly one option is entailed (model enumeration); the ETR option is endorsed by PyETR; the FIRST option follows when each 'either' is read as its first disjunct.

</details>

<details><summary>Prompt and computed outputs — <code>E4-r1-DA</code></summary>

```text
Here are some facts about a machine.

- Either the bell is ringing and the fan is not running, or the fan is running and the door is open.
- Either the gate is locked, or the lamp is lit and the door is open.
- The fan is not running.

Which one of the following conclusions necessarily follows from these facts?
D. The lamp is lit.
C. The gate is locked.
B. The door is open or the lamp is lit.
A. The bell is ringing.
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"choice": "<letter>"}
```

- **exact:** A
- **A2 PRIMACY:** D
- **A2 RECENCY:** A
- **LABEL-A:** A
- **A2 FREQ / ATMOSPHERE:** B
- **A2 LENGTH-SHORT:** D
- **B4 ETR:** D
- **B4 FIRST:** C
- **H SAMPLE-8:** A
- **H RANDOM-U:** uniform
- **satisficing (C-type sequential check):** D if 'ETR' passes its check
- *params:* `{"option_order_top_to_bottom": ["ETR", "FIRST", "cue", "correct"], "labels_top_to_bottom": ["D", "C", "B", "A"], "option_words": {"correct": 4, "ETR": 4, "FIRST": 4, "cue": 9}, "freq_score": {"correct": 1.0, "ETR": 1.0, "FIRST": 1.0, "cue": 1.5}, "mood": {"correct": "conj/pos", "ETR": "conj/pos", "FIRST": "conj/pos", "cue": "disj/pos"}, "atmosphere": "disj/pos"}`
- *notes:* Exactly one option is entailed (model enumeration); the ETR option is endorsed by PyETR; the FIRST option follows when each 'either' is read as its first disjunct.

</details>

<details><summary>Prompt and computed outputs — <code>E4-r2-DA</code></summary>

```text
Here are some facts about a machine.

- Either the bell is ringing and the fan is not running, or the fan is running and the door is open.
- Either the gate is locked, or the lamp is lit and the door is open.
- The fan is not running.

Which one of the following conclusions necessarily follows from these facts?
D. The gate is locked.
C. The door is open or the lamp is lit.
B. The bell is ringing.
A. The lamp is lit.
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"choice": "<letter>"}
```

- **exact:** B
- **A2 PRIMACY:** D
- **A2 RECENCY:** A
- **LABEL-A:** A
- **A2 FREQ / ATMOSPHERE:** C
- **A2 LENGTH-SHORT:** D
- **B4 ETR:** A
- **B4 FIRST:** D
- **H SAMPLE-8:** B
- **H RANDOM-U:** uniform
- **satisficing (C-type sequential check):** D if 'FIRST' passes its check
- *params:* `{"option_order_top_to_bottom": ["FIRST", "cue", "correct", "ETR"], "labels_top_to_bottom": ["D", "C", "B", "A"], "option_words": {"correct": 4, "ETR": 4, "FIRST": 4, "cue": 9}, "freq_score": {"correct": 1.0, "ETR": 1.0, "FIRST": 1.0, "cue": 1.5}, "mood": {"correct": "conj/pos", "ETR": "conj/pos", "FIRST": "conj/pos", "cue": "disj/pos"}, "atmosphere": "disj/pos"}`
- *notes:* Exactly one option is entailed (model enumeration); the ETR option is endorsed by PyETR; the FIRST option follows when each 'either' is read as its first disjunct.

</details>

<details><summary>Prompt and computed outputs — <code>E4-r3-DA</code></summary>

```text
Here are some facts about a machine.

- Either the bell is ringing and the fan is not running, or the fan is running and the door is open.
- Either the gate is locked, or the lamp is lit and the door is open.
- The fan is not running.

Which one of the following conclusions necessarily follows from these facts?
D. The door is open or the lamp is lit.
C. The bell is ringing.
B. The lamp is lit.
A. The gate is locked.
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"choice": "<letter>"}
```

- **exact:** C
- **A2 PRIMACY:** D
- **A2 RECENCY:** A
- **LABEL-A:** A
- **A2 FREQ / ATMOSPHERE:** D
- **A2 LENGTH-SHORT:** C
- **B4 ETR:** B
- **B4 FIRST:** A
- **H SAMPLE-8:** C
- **H RANDOM-U:** uniform
- **satisficing (C-type sequential check):** D if 'cue' passes its check
- *params:* `{"option_order_top_to_bottom": ["cue", "correct", "ETR", "FIRST"], "labels_top_to_bottom": ["D", "C", "B", "A"], "option_words": {"correct": 4, "ETR": 4, "FIRST": 4, "cue": 9}, "freq_score": {"correct": 1.0, "ETR": 1.0, "FIRST": 1.0, "cue": 1.5}, "mood": {"correct": "conj/pos", "ETR": "conj/pos", "FIRST": "conj/pos", "cue": "disj/pos"}, "atmosphere": "disj/pos"}`
- *notes:* Exactly one option is entailed (model enumeration); the ETR option is endorsed by PyETR; the FIRST option follows when each 'either' is read as its first disjunct.

</details>

**Hypothesis matrix**

| Theory | (a) `E4-r0-AD` | (a) `E4-r1-AD` | (a) `E4-r2-AD` | (a) `E4-r3-AD` | (a) `E4-r0-DA` | (a) `E4-r1-DA` | (a) `E4-r2-DA` | (a) `E4-r3-DA` | (b) pure-theory statistic · weight resolution | (c) predicted trace |
|---|---|---|---|---|---|---|---|---|---|---|
| exact | A | D | C | B | D | A | B | C | Detectable π ≥ 0.04 vs H RANDOM-U | A completed procedure: a witness checked against every constraint, or a closed refutation / exhaustive case split. No cue given as a reason. |
| A2 PRIMACY | A | A | A | A | D | D | D | D | Detectable π ≥ 0.02 vs A2 LENGTH-SHORT | CUE-POS on the first premise or option; other options not evaluated. |
| A2 RECENCY | D | D | D | D | A | A | A | A | Detectable π ≥ 0.04 vs H RANDOM-U | CUE-POS on the last premise or option. |
| LABEL-A | A | A | A | A | A | A | A | A | Detectable π ≥ 0.04 vs H RANDOM-U | No trace signature expected (a token-level prior); the trace may rationalise whichever option is labelled A. |
| A2 FREQ / ATMOSPHERE | D | C | B | A | A | B | C | D | Detectable π ≥ 0.04 vs H RANDOM-U | CUE-FREQ / CUE-MOOD: the option 'sounds like' the premises; no derivation. |
| A2 LENGTH-SHORT | A | A | A | B | D | D | D | C | Detectable π ≥ 0.02 vs A2 PRIMACY | The simplest-looking option preferred without being checked. |
| B4 ETR | B | A | D | C | C | D | A | B | Detectable π ≥ 0.04 vs H RANDOM-U | COMMIT-DISJ / TRUE-ONLY: the disjunct matching the categorical fact kept, the others dropped. |
| B4 FIRST | C | B | A | D | B | C | D | A | Detectable π ≥ 0.04 vs H RANDOM-U | COMMIT-DISJ on each first disjunct, never revisited. |
| H SAMPLE-8 | A | D | C | B | D | A | B | C | Detectable π ≥ 0.04 vs H RANDOM-U | SAMPLE(k): at most 8 concrete cases checked, then a universal conclusion; no exhaustive split. |
| H RANDOM-U | uniform | uniform | uniform | uniform | uniform | uniform | uniform | uniform | Detectable π ≥ 0.02 vs A2 RECENCY | No procedure determines the verdict; trace content and verdict unrelated. |

*(c) for every theory: the expected share of traces showing the signature ≈ π_h · r̂ (faithfulness, from E8), plus the coder's false-positive rate.*

**Likelihood ratios per observable pattern** (log₁₀ LR; one study unit)

| Pattern | Favours (log₁₀ LR vs the best theory outside the favoured group) | Pushes toward zero weight (log₁₀ LR vs the best theory) |
|---|---|---|
| the 'correct' option in all 8 renderings | exact (+4.6), H SAMPLE-8 (+4.6) | A2 FREQ / ATMOSPHERE (-14.0), B4 ETR (-14.0), B4 FIRST (-14.0), A2 PRIMACY (-10.5), A2 RECENCY (-10.5), LABEL-A (-10.5), A2 LENGTH-SHORT (-7.0), H RANDOM-U (-4.6) |
| the 'ETR' option in all 8 renderings | B4 ETR (+4.6) | exact (-14.0), A2 FREQ / ATMOSPHERE (-14.0), B4 FIRST (-14.0), H SAMPLE-8 (-14.0), A2 PRIMACY (-10.5), A2 RECENCY (-10.5), LABEL-A (-10.5), A2 LENGTH-SHORT (-10.5), H RANDOM-U (-4.6) |
| the 'FIRST' option in all 8 renderings | B4 FIRST (+4.6) | exact (-14.0), A2 FREQ / ATMOSPHERE (-14.0), B4 ETR (-14.0), H SAMPLE-8 (-14.0), A2 PRIMACY (-10.5), A2 RECENCY (-10.5), LABEL-A (-10.5), A2 LENGTH-SHORT (-10.5), H RANDOM-U (-4.6) |
| the 'cue' option in all 8 renderings | A2 FREQ / ATMOSPHERE (+4.6) | exact (-14.0), A2 LENGTH-SHORT (-14.0), B4 ETR (-14.0), B4 FIRST (-14.0), H SAMPLE-8 (-14.0), A2 PRIMACY (-10.5), A2 RECENCY (-10.5), LABEL-A (-10.5), H RANDOM-U (-4.6) |
| the top position in all 8 | A2 PRIMACY (+3.5) | A2 RECENCY (-14.0), exact (-10.5), A2 FREQ / ATMOSPHERE (-10.5), B4 ETR (-10.5), B4 FIRST (-10.5), H SAMPLE-8 (-10.5), LABEL-A (-7.0), H RANDOM-U (-4.6), A2 LENGTH-SHORT (-3.5) |
| the bottom position in all 8 | A2 RECENCY (+4.6) | A2 PRIMACY (-14.0), A2 LENGTH-SHORT (-14.0), exact (-10.5), A2 FREQ / ATMOSPHERE (-10.5), B4 ETR (-10.5), B4 FIRST (-10.5), H SAMPLE-8 (-10.5), LABEL-A (-7.0), H RANDOM-U (-4.6) |
| label 'A' in all 8 | LABEL-A (+4.6) | exact (-10.5), A2 FREQ / ATMOSPHERE (-10.5), B4 ETR (-10.5), B4 FIRST (-10.5), H SAMPLE-8 (-10.5), A2 LENGTH-SHORT (-8.8), A2 PRIMACY (-7.0), A2 RECENCY (-7.0), H RANDOM-U (-4.6) |

**Weight resolution at study N**

| Theory | Nearest competitor (smallest KL) | Detectable π vs it (80% power) | Upper 95% bound on π if pure competitor | E[log₁₀ BF] vs competitor | Detectable π if the rest is the hardest base (which) | Identical predictions here |
|---|---|---|---|---|---|---|
| exact | H RANDOM-U | 0.038 | 0.025 | 787.2 | 0.038 (H RANDOM-U) | H SAMPLE-8 |
| A2 PRIMACY | A2 LENGTH-SHORT | 0.017 | 0.011 | 655.5 | 0.038 (H RANDOM-U) | — |
| A2 RECENCY | H RANDOM-U | 0.038 | 0.025 | 787.2 | 0.038 (H RANDOM-U) | — |
| LABEL-A | H RANDOM-U | 0.038 | 0.025 | 787.2 | 0.038 (H RANDOM-U) | — |
| A2 FREQ / ATMOSPHERE | H RANDOM-U | 0.038 | 0.025 | 787.2 | 0.038 (H RANDOM-U) | — |
| A2 LENGTH-SHORT | A2 PRIMACY | 0.017 | 0.011 | 655.5 | 0.038 (H RANDOM-U) | — |
| B4 ETR | H RANDOM-U | 0.038 | 0.025 | 787.2 | 0.038 (H RANDOM-U) | — |
| B4 FIRST | H RANDOM-U | 0.038 | 0.025 | 787.2 | 0.038 (H RANDOM-U) | — |
| H SAMPLE-8 | H RANDOM-U | 0.038 | 0.025 | 787.2 | 0.038 (H RANDOM-U) | exact |
| H RANDOM-U | A2 RECENCY | 0.019 | 0.013 | 1179.4 | 0.019 (A2 RECENCY) | — |

**Not separated here.** Exact and SAMPLE-8 pick the same option here (E6 separates them). LENGTH-SHORT coincides with whichever theory owns the shortest option; across items, option length is decorrelated from role. Satisficing (a sequential check) predicts the top position only when the top option passes its check; it is separated from bare PRIMACY by the position × plausibility interaction across items.

<a id="e4-order"></a>
## E4: premise order (fact → rule → rule chain, all 6 orders)

**Reasoning question.** Does 'follows' depend on surface position, on order-sensitive updating, or on nothing?

**Design.** The same three premises in all six orders; C needs the whole chain (UP depth 3).  *Study units:* six orders × 150.

| Item | Cell | Ground truth | Controlled | Varied |
|---|---|---|---|---|
| `E4-order-FR1R2` | order F → R1 → R2 | follows | the three premises and the question | premise order (all 6 permutations) |
| `E4-order-FR2R1` | order F → R2 → R1 | follows | the three premises and the question | premise order (all 6 permutations) |
| `E4-order-R1FR2` | order R1 → F → R2 | follows | the three premises and the question | premise order (all 6 permutations) |
| `E4-order-R1R2F` | order R1 → R2 → F | follows | the three premises and the question | premise order (all 6 permutations) |
| `E4-order-R2FR1` | order R2 → F → R1 | follows | the three premises and the question | premise order (all 6 permutations) |
| `E4-order-R2R1F` | order R2 → R1 → F | follows | the three premises and the question | premise order (all 6 permutations) |

<details><summary>Prompt and computed outputs — <code>E4-order-FR1R2</code></summary>

```text
Here are some facts about a machine.

- The bell is ringing.
- Either the door is open, or the bell is not ringing.
- Either the lamp is lit, or the door is not open.

Question: Does it follow from these facts that the lamp is lit?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** follows
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** does not follow (literal counts [1]; min vs illustrative θ = 2)
- **A2 ATMOSPHERE:** does not follow (atm(P) = disj/pos, mood(C) = conj/pos)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** follows
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 1.000 (ρ = 0.000)
- **NOISY-EXACT:** follows w.p. 0.90
- **PERCEPTION-NOISE:** follows unless a misread breaks it: P(does not follow) = 0.200
- **B1 UP-1:** does not follow (2 propagation step(s) beyond the facts)
- **B1 UP-2:** follows (2 propagation step(s) beyond the facts)
- **B4 ETR:** follows (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** follows
- **B4 MATCH:** does not follow
- **D case-split (b = 4):** follows
- *params:* `{"atoms": 3, "rho": 0.0, "n_models": 1, "up_depth": 3, "kappa_follow": 0.0, "kappa_break": 1.0, "eta_first_counter": null, "etr_what_follows": "{a1()a2()}", "order": ["F", "R1", "R2"], "fact_position": 1, "kendall_tau_vs_proof_order": 1.0, "propagation_steps_beyond_facts": 2}`
- *notes:* Chain: bell ringing → door open → lamp lit; C = 'the lamp is lit' (two propagation steps beyond the fact).

</details>

<details><summary>Prompt and computed outputs — <code>E4-order-FR2R1</code></summary>

```text
Here are some facts about a machine.

- The bell is ringing.
- Either the lamp is lit, or the door is not open.
- Either the door is open, or the bell is not ringing.

Question: Does it follow from these facts that the lamp is lit?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** follows
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** does not follow (literal counts [1]; min vs illustrative θ = 2)
- **A2 ATMOSPHERE:** does not follow (atm(P) = disj/pos, mood(C) = conj/pos)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 1.000 (ρ = 0.000)
- **NOISY-EXACT:** follows w.p. 0.90
- **PERCEPTION-NOISE:** follows unless a misread breaks it: P(does not follow) = 0.200
- **B1 UP-1:** does not follow (2 propagation step(s) beyond the facts)
- **B1 UP-2:** follows (2 propagation step(s) beyond the facts)
- **B4 ETR:** follows (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** follows
- **B4 MATCH:** does not follow
- **D case-split (b = 4):** follows
- *params:* `{"atoms": 3, "rho": 0.0, "n_models": 1, "up_depth": 3, "kappa_follow": 0.0, "kappa_break": 1.0, "eta_first_counter": null, "etr_what_follows": "{a1()a2()}", "order": ["F", "R2", "R1"], "fact_position": 1, "kendall_tau_vs_proof_order": 0.33, "propagation_steps_beyond_facts": 2}`
- *notes:* Chain: bell ringing → door open → lamp lit; C = 'the lamp is lit' (two propagation steps beyond the fact).

</details>

<details><summary>Prompt and computed outputs — <code>E4-order-R1FR2</code></summary>

```text
Here are some facts about a machine.

- Either the door is open, or the bell is not ringing.
- The bell is ringing.
- Either the lamp is lit, or the door is not open.

Question: Does it follow from these facts that the lamp is lit?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** follows
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** does not follow (literal counts [1]; min vs illustrative θ = 2)
- **A2 ATMOSPHERE:** does not follow (atm(P) = disj/pos, mood(C) = conj/pos)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** follows
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 1.000 (ρ = 0.000)
- **NOISY-EXACT:** follows w.p. 0.90
- **PERCEPTION-NOISE:** follows unless a misread breaks it: P(does not follow) = 0.200
- **B1 UP-1:** does not follow (2 propagation step(s) beyond the facts)
- **B1 UP-2:** follows (2 propagation step(s) beyond the facts)
- **B4 ETR:** follows (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** follows
- **B4 MATCH:** does not follow
- **D case-split (b = 4):** follows
- *params:* `{"atoms": 3, "rho": 0.0, "n_models": 1, "up_depth": 3, "kappa_follow": 0.0, "kappa_break": 1.0, "eta_first_counter": null, "etr_what_follows": "{a1()a2()}", "order": ["R1", "F", "R2"], "fact_position": 2, "kendall_tau_vs_proof_order": 0.33, "propagation_steps_beyond_facts": 2}`
- *notes:* Chain: bell ringing → door open → lamp lit; C = 'the lamp is lit' (two propagation steps beyond the fact).

</details>

<details><summary>Prompt and computed outputs — <code>E4-order-R1R2F</code></summary>

```text
Here are some facts about a machine.

- Either the door is open, or the bell is not ringing.
- Either the lamp is lit, or the door is not open.
- The bell is ringing.

Question: Does it follow from these facts that the lamp is lit?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** follows
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** does not follow (literal counts [1]; min vs illustrative θ = 2)
- **A2 ATMOSPHERE:** does not follow (atm(P) = disj/pos, mood(C) = conj/pos)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 1.000 (ρ = 0.000)
- **NOISY-EXACT:** follows w.p. 0.90
- **PERCEPTION-NOISE:** follows unless a misread breaks it: P(does not follow) = 0.200
- **B1 UP-1:** does not follow (2 propagation step(s) beyond the facts)
- **B1 UP-2:** follows (2 propagation step(s) beyond the facts)
- **B4 ETR:** follows (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** follows
- **B4 MATCH:** does not follow
- **D case-split (b = 4):** follows
- *params:* `{"atoms": 3, "rho": 0.0, "n_models": 1, "up_depth": 3, "kappa_follow": 0.0, "kappa_break": 1.0, "eta_first_counter": null, "etr_what_follows": "{a1()a2()}", "order": ["R1", "R2", "F"], "fact_position": 3, "kendall_tau_vs_proof_order": -0.33, "propagation_steps_beyond_facts": 2}`
- *notes:* Chain: bell ringing → door open → lamp lit; C = 'the lamp is lit' (two propagation steps beyond the fact).

</details>

<details><summary>Prompt and computed outputs — <code>E4-order-R2FR1</code></summary>

```text
Here are some facts about a machine.

- Either the lamp is lit, or the door is not open.
- The bell is ringing.
- Either the door is open, or the bell is not ringing.

Question: Does it follow from these facts that the lamp is lit?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** follows
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** does not follow (literal counts [1]; min vs illustrative θ = 2)
- **A2 ATMOSPHERE:** does not follow (atm(P) = disj/pos, mood(C) = conj/pos)
- **A2 PRIMACY:** follows
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 1.000 (ρ = 0.000)
- **NOISY-EXACT:** follows w.p. 0.90
- **PERCEPTION-NOISE:** follows unless a misread breaks it: P(does not follow) = 0.200
- **B1 UP-1:** does not follow (2 propagation step(s) beyond the facts)
- **B1 UP-2:** follows (2 propagation step(s) beyond the facts)
- **B4 ETR:** follows (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** follows
- **B4 MATCH:** does not follow
- **D case-split (b = 4):** follows
- *params:* `{"atoms": 3, "rho": 0.0, "n_models": 1, "up_depth": 3, "kappa_follow": 0.0, "kappa_break": 1.0, "eta_first_counter": null, "etr_what_follows": "{a1()a2()}", "order": ["R2", "F", "R1"], "fact_position": 2, "kendall_tau_vs_proof_order": -0.33, "propagation_steps_beyond_facts": 2}`
- *notes:* Chain: bell ringing → door open → lamp lit; C = 'the lamp is lit' (two propagation steps beyond the fact).

</details>

<details><summary>Prompt and computed outputs — <code>E4-order-R2R1F</code></summary>

```text
Here are some facts about a machine.

- Either the lamp is lit, or the door is not open.
- Either the door is open, or the bell is not ringing.
- The bell is ringing.

Question: Does it follow from these facts that the lamp is lit?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** follows
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** does not follow (literal counts [1]; min vs illustrative θ = 2)
- **A2 ATMOSPHERE:** does not follow (atm(P) = disj/pos, mood(C) = conj/pos)
- **A2 PRIMACY:** follows
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 1.000 (ρ = 0.000)
- **NOISY-EXACT:** follows w.p. 0.90
- **PERCEPTION-NOISE:** follows unless a misread breaks it: P(does not follow) = 0.200
- **B1 UP-1:** does not follow (2 propagation step(s) beyond the facts)
- **B1 UP-2:** follows (2 propagation step(s) beyond the facts)
- **B4 ETR:** follows (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** follows
- **B4 MATCH:** does not follow
- **D case-split (b = 4):** follows
- *params:* `{"atoms": 3, "rho": 0.0, "n_models": 1, "up_depth": 3, "kappa_follow": 0.0, "kappa_break": 1.0, "eta_first_counter": null, "etr_what_follows": "{a1()a2()}", "order": ["R2", "R1", "F"], "fact_position": 3, "kendall_tau_vs_proof_order": -1.0, "propagation_steps_beyond_facts": 2}`
- *notes:* Chain: bell ringing → door open → lamp lit; C = 'the lamp is lit' (two propagation steps beyond the fact).

</details>

**Hypothesis matrix**

| Theory | (a) `E4-order-FR1R2` | (a) `E4-order-FR2R1` | (a) `E4-order-R1FR2` | (a) `E4-order-R1R2F` | (a) `E4-order-R2FR1` | (a) `E4-order-R2R1F` | (b) pure-theory statistic · weight resolution | (c) predicted trace |
|---|---|---|---|---|---|---|---|---|
| exact | follows | follows | follows | follows | follows | follows | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 1.00, 1.00, 1.00, 1.00, 1.00, 1.00. Detectable π ≥ 0.48 vs NOISY-EXACT | A completed procedure: a witness checked against every constraint, or a closed refutation / exhaustive case split. No cue given as a reason. |
| A1 ALWAYS-YES | follows | follows | follows | follows | follows | follows | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 1.00, 1.00, 1.00, 1.00, 1.00, 1.00. Detectable π ≥ 0.48 vs NOISY-EXACT | The conclusion asserted with no derivation and no search for a counter-model. |
| A1 NONE | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 0.00, 0.00, 0.00, 0.00, 0.00, 0.00. Detectable π ≥ 0.04 vs H RANDOM-U | 'Nothing definite follows', with no case analysis. |
| A2 FREQ | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 0.00, 0.00, 0.00, 0.00, 0.00, 0.00. Detectable π ≥ 0.04 vs H RANDOM-U | CUE-FREQ ('the bell ringing comes up most often'). |
| A2 ATMOSPHERE | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 0.00, 0.00, 0.00, 0.00, 0.00, 0.00. Detectable π ≥ 0.04 vs H RANDOM-U | CUE-MOOD: the conclusion's form or polarity matched to the premises without a derivation. |
| A2 PRIMACY | does not follow | does not follow | does not follow | does not follow | follows | follows | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 0.00, 0.00, 0.00, 0.00, 1.00, 1.00. Detectable π ≥ 0.04 vs H RANDOM-U | CUE-POS on the first premise or option; other options not evaluated. |
| A2 RECENCY | follows | does not follow | follows | does not follow | does not follow | does not follow | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 1.00, 0.00, 1.00, 0.00, 0.00, 0.00. Detectable π ≥ 0.04 vs H RANDOM-U | CUE-POS on the last premise or option. |
| H RANDOM-U | follows w.p. ½ | follows w.p. ½ | follows w.p. ½ | follows w.p. ½ | follows w.p. ½ | follows w.p. ½ | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 0.50, 0.50, 0.50, 0.50, 0.50, 0.50. Detectable π ≥ 0.06 vs PERCEPTION-NOISE | No procedure determines the verdict; trace content and verdict unrelated. |
| H SAMPLE-8 | follows w.p. 1.000 | follows w.p. 1.000 | follows w.p. 1.000 | follows w.p. 1.000 | follows w.p. 1.000 | follows w.p. 1.000 | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 1.00, 1.00, 1.00, 1.00, 1.00, 1.00. Detectable π ≥ 0.48 vs NOISY-EXACT | SAMPLE(k): at most 8 concrete cases checked, then a universal conclusion; no exhaustive split. |
| NOISY-EXACT | follows w.p. 0.90 | follows w.p. 0.90 | follows w.p. 0.90 | follows w.p. 0.90 | follows w.p. 0.90 | follows w.p. 0.90 | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 0.90, 0.90, 0.90, 0.90, 0.90, 0.90. Detectable π ≥ 0.34 vs exact | A systematic procedure; an EVALSLIP precedes every error. |
| PERCEPTION-NOISE | follows | follows | follows | follows | follows | follows | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 0.80, 0.80, 0.80, 0.80, 0.80, 0.80. Detectable π ≥ 0.22 vs NOISY-EXACT | A MISQUOTE of a constraint (a dropped ¬, a wrong pair, a missing clause); later reasoning consistent with the misquote. |
| B1 UP-1 | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 0.00, 0.00, 0.00, 0.00, 0.00, 0.00. Detectable π ≥ 0.04 vs H RANDOM-U | PROP only, one round. |
| B1 UP-2 | follows | follows | follows | follows | follows | follows | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 1.00, 1.00, 1.00, 1.00, 1.00, 1.00. Detectable π ≥ 0.48 vs NOISY-EXACT | PROP only, two rounds; no case split. |
| B4 ETR | follows | follows | follows | follows | follows | follows | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 1.00, 1.00, 1.00, 1.00, 1.00, 1.00. Detectable π ≥ 0.48 vs NOISY-EXACT | COMMIT-DISJ / TRUE-ONLY: the disjunct matching the categorical fact kept, the others dropped. |
| B4 FIRST | follows | follows | follows | follows | follows | follows | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 1.00, 1.00, 1.00, 1.00, 1.00, 1.00. Detectable π ≥ 0.48 vs NOISY-EXACT | COMMIT-DISJ on each first disjunct, never revisited. |
| B4 MATCH | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 0.00, 0.00, 0.00, 0.00, 0.00, 0.00. Detectable π ≥ 0.04 vs H RANDOM-U | Picks the disjunct that shares atoms with the categorical fact. |
| D case-split (b = 4) | follows | follows | follows | follows | follows | follows | P(follows) per order F→R1→R2, F→R2→R1, R1→F→R2, R1→R2→F, R2→F→R1, R2→R1→F = 1.00, 1.00, 1.00, 1.00, 1.00, 1.00. Detectable π ≥ 0.48 vs NOISY-EXACT | A systematic case split abandoned after ≈ 4 cases; 'follows' if no counter-model was found. |

*(c) for every theory: the expected share of traces showing the signature ≈ π_h · r̂ (faithfulness, from E8), plus the coder's false-positive rate.*

**Likelihood ratios per observable pattern** (log₁₀ LR; one study unit)

| Pattern | Favours (log₁₀ LR vs the best theory outside the favoured group) | Pushes toward zero weight (log₁₀ LR vs the best theory) |
|---|---|---|
| follows only when R2 is first | A2 PRIMACY (+1.7) | exact (-5.1), A1 ALWAYS-YES (-5.1), A2 RECENCY (-5.1), H SAMPLE-8 (-5.1), B1 UP-2 (-5.1), B4 ETR (-5.1), B4 FIRST (-5.1), D case-split (b = 4) (-5.1), NOISY-EXACT (-4.0), PERCEPTION-NOISE (-2.9), A1 NONE (-2.6), A2 FREQ (-2.6), A2 ATMOSPHERE (-2.6), B1 UP-1 (-2.6), B4 MATCH (-2.6), H RANDOM-U (-1.7) |
| follows only when R2 is last | A2 RECENCY (+1.7) | exact (-5.1), A1 ALWAYS-YES (-5.1), A2 PRIMACY (-5.1), H SAMPLE-8 (-5.1), B1 UP-2 (-5.1), B4 ETR (-5.1), B4 FIRST (-5.1), D case-split (b = 4) (-5.1), NOISY-EXACT (-4.0), PERCEPTION-NOISE (-2.9), A1 NONE (-2.6), A2 FREQ (-2.6), A2 ATMOSPHERE (-2.6), B1 UP-1 (-2.6), B4 MATCH (-2.6), H RANDOM-U (-1.7) |
| follows in all six orders | exact (+0.5), A1 ALWAYS-YES (+0.5), H SAMPLE-8 (+0.5), B1 UP-2 (+0.5), B4 ETR (+0.5), B4 FIRST (+0.5), D case-split (b = 4) (+0.5), NOISY-EXACT (+0.3) | A1 NONE (-7.7), A2 FREQ (-7.7), A2 ATMOSPHERE (-7.7), B1 UP-1 (-7.7), B4 MATCH (-7.7), A2 PRIMACY (-5.1), A2 RECENCY (-5.1), H RANDOM-U (-1.7) |
| follows in none | A1 NONE (+1.7), A2 FREQ (+1.7), A2 ATMOSPHERE (+1.7), B1 UP-1 (+1.7), B4 MATCH (+1.7) | exact (-7.7), A1 ALWAYS-YES (-7.7), H SAMPLE-8 (-7.7), B1 UP-2 (-7.7), B4 ETR (-7.7), B4 FIRST (-7.7), D case-split (b = 4) (-7.7), NOISY-EXACT (-5.9), PERCEPTION-NOISE (-4.1), A2 PRIMACY (-2.6), A2 RECENCY (-2.6), H RANDOM-U (-1.7) |

**Weight resolution at study N**

| Theory | Nearest competitor (smallest KL) | Detectable π vs it (80% power) | Upper 95% bound on π if pure competitor | E[log₁₀ BF] vs competitor | Detectable π if the rest is the hardest base (which) | Identical predictions here |
|---|---|---|---|---|---|---|
| exact | NOISY-EXACT | 0.480 | 0.318 | 6.5 | 0.480 (NOISY-EXACT) | A1 ALWAYS-YES, H SAMPLE-8, B1 UP-2, B4 ETR, B4 FIRST, D case-split (b = 4) |
| A1 ALWAYS-YES | NOISY-EXACT | 0.480 | 0.318 | 6.5 | 0.480 (NOISY-EXACT) | exact, H SAMPLE-8, B1 UP-2, B4 ETR, B4 FIRST, D case-split (b = 4) |
| A1 NONE | H RANDOM-U | 0.035 | 0.023 | 193.3 | 0.035 (H RANDOM-U) | A2 FREQ, A2 ATMOSPHERE, B1 UP-1, B4 MATCH |
| A2 FREQ | H RANDOM-U | 0.035 | 0.023 | 193.3 | 0.035 (H RANDOM-U) | A1 NONE, A2 ATMOSPHERE, B1 UP-1, B4 MATCH |
| A2 ATMOSPHERE | H RANDOM-U | 0.035 | 0.023 | 193.3 | 0.035 (H RANDOM-U) | A1 NONE, A2 FREQ, B1 UP-1, B4 MATCH |
| A2 PRIMACY | H RANDOM-U | 0.035 | 0.023 | 193.3 | 0.035 (H RANDOM-U) | — |
| A2 RECENCY | H RANDOM-U | 0.035 | 0.023 | 193.3 | 0.035 (H RANDOM-U) | — |
| H RANDOM-U | PERCEPTION-NOISE | 0.055 | 0.036 | 87.2 | 0.055 (PERCEPTION-NOISE) | — |
| H SAMPLE-8 | NOISY-EXACT | 0.480 | 0.318 | 6.5 | 0.480 (NOISY-EXACT) | exact, A1 ALWAYS-YES, B1 UP-2, B4 ETR, B4 FIRST, D case-split (b = 4) |
| NOISY-EXACT | exact | 0.338 | 0.224 | 8.1 | 0.338 (exact) | — |
| PERCEPTION-NOISE | NOISY-EXACT | 0.216 | 0.143 | 17.4 | 0.216 (NOISY-EXACT) | — |
| B1 UP-1 | H RANDOM-U | 0.035 | 0.023 | 193.3 | 0.035 (H RANDOM-U) | A1 NONE, A2 FREQ, A2 ATMOSPHERE, B4 MATCH |
| B1 UP-2 | NOISY-EXACT | 0.480 | 0.318 | 6.5 | 0.480 (NOISY-EXACT) | exact, A1 ALWAYS-YES, H SAMPLE-8, B4 ETR, B4 FIRST, D case-split (b = 4) |
| B4 ETR | NOISY-EXACT | 0.480 | 0.318 | 6.5 | 0.480 (NOISY-EXACT) | exact, A1 ALWAYS-YES, H SAMPLE-8, B1 UP-2, B4 FIRST, D case-split (b = 4) |
| B4 FIRST | NOISY-EXACT | 0.480 | 0.318 | 6.5 | 0.480 (NOISY-EXACT) | exact, A1 ALWAYS-YES, H SAMPLE-8, B1 UP-2, B4 ETR, D case-split (b = 4) |
| B4 MATCH | H RANDOM-U | 0.035 | 0.023 | 193.3 | 0.035 (H RANDOM-U) | A1 NONE, A2 FREQ, A2 ATMOSPHERE, B1 UP-1 |
| D case-split (b = 4) | NOISY-EXACT | 0.480 | 0.318 | 6.5 | 0.480 (NOISY-EXACT) | exact, A1 ALWAYS-YES, H SAMPLE-8, B1 UP-2, B4 ETR, B4 FIRST |

**Not separated here.** ATMOSPHERE, FREQ, NONE and the short UP chains all say 'does not follow' in every order here; E2-ENT separates ATMOSPHERE and FREQ from them.

<a id="e5-col"></a>
## E5: inversion set, rooms theme (T / N / I / I+R / P)

**Reasoning question.** Under an inverted rule, does the model give the textbook answer it gives under N?

**Design.** The same pair list under the textbook, neutral, inverted, inverted + reminder and partial-inversion rules. Class probabilities assume p_r = 0.3 (I) and 0.05 (I+R) for PERCEPTION-NOISE.  *Study units:* I answer × 200; I+R answer × 200; P answer × 200.

| Item | Cell | Ground truth | Controlled | Varied |
|---|---|---|---|---|
| `E5-COL-T` | T (textbook) | possible, e.g. Ann: 1, Ben: 1, Cal: 2, Dan: 2, Eve: 3, Fay: 3, Gus: 1, Hal: 1, Ivy: 2, Jay: 3 | people, pair list and its order, room count, answer format; preamble length (N vs I within ±3 words) | textbook rule, no preamble |
| `E5-COL-N` | N (textbook + neutral preamble) | possible, e.g. Ann: 1, Ben: 1, Cal: 2, Dan: 2, Eve: 3, Fay: 3, Gus: 1, Hal: 1, Ivy: 2, Jay: 3 | people, pair list and its order, room count, answer format; preamble length (N vs I within ±3 words) | textbook rule + length-matched neutral preamble |
| `E5-COL-I` | I (inverted) | possible, e.g. Ann: 1, Ben: 2, Cal: 3, Dan: 2, Eve: 3, Fay: 4, Gus: 4, Hal: 3, Ivy: 1, Jay: 1 | people, pair list and its order, room count, answer format; preamble length (N vs I within ±3 words) | inverted rule + inverting preamble; same pair list |
| `E5-COL-I+R` | I+R (inverted + reminder) | possible, e.g. Ann: 1, Ben: 2, Cal: 3, Dan: 2, Eve: 3, Fay: 4, Gus: 4, Hal: 3, Ivy: 1, Jay: 1 | people, pair list and its order, room count, answer format; preamble length (N vs I within ±3 words) | I + reminder just before the question |
| `E5-COL-P` | P (partial inversion) | possible, e.g. Ann: 1, Ben: 3, Cal: 2, Dan: 3, Eve: 2, Fay: 4, Gus: 4, Hal: 2, Ivy: 1, Jay: 1 | people and pair list as in T/N/I | only ★ pairs carry the inverted relation (must share) |

<details><summary>Prompt and computed outputs — <code>E5-COL-T</code></summary>

```text
Ten people (Ann, Ben, Cal, Dan, Eve, Fay, Gus, Hal, Ivy, Jay) are being assigned to rooms 1–4.
The following pairs are enemies: Eve–Ivy, Ben–Ivy, Cal–Hal, Hal–Ivy, Ben–Eve, Ann–Fay, Eve–Hal, Fay–Gus, Ann–Dan, Ivy–Jay, Ann–Ivy, Fay–Hal, Cal–Eve, Ben–Dan, Dan–Fay, Cal–Fay, Ann–Jay, Ben–Cal.
No two enemies may share a room.
Is there an assignment of people to rooms 1–4 that follows this rule?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"possible": true, "rooms": {"<name>": <room number>, ...}}
{"possible": false, "rooms": null}
```

- **exact:** Ann: 1, Ben: 1, Cal: 2, Dan: 2, Eve: 3, Fay: 3, Gus: 1, Hal: 1, Ivy: 2, Jay: 3
- **A3 TT[exact]:** Ann: 1, Ben: 1, Cal: 2, Dan: 2, Eve: 3, Fay: 3, Gus: 1, Hal: 1, Ivy: 2, Jay: 3
- **A3 TT[FIRST-FIT]:** Ann: 1, Ben: 1, Cal: 2, Dan: 2, Eve: 3, Fay: 3, Gus: 1, Hal: 1, Ivy: 2, Jay: 3
- **C1 FIRST-FIT (stated rule):** Ann: 1, Ben: 1, Cal: 2, Dan: 2, Eve: 3, Fay: 3, Gus: 1, Hal: 1, Ivy: 2, Jay: 3
- **A1 ALWAYS-POSSIBLE:** possible, rooms from the uniform fill
- **H RANDOM-U:** valid w.p. 0.0027
- **B1 DROP-CONSTRAINT(★):** n/a (no ★ pairs in this framing) → as exact
- **PERCEPTION-NOISE (rule misread):** the TT answer w.p. p_r, otherwise the exact answer
- *params:* `{"friend_groups_planted": [["Ann", "Jay", "Ivy"], ["Cal", "Eve", "Hal"], ["Ben", "Dan"], ["Fay", "Gus"]], "pairs": 18, "textbook_colourings": 2880, "inverted_colourings": 24, "preamble_words_N_I": [25, 27], "textbook_answer_violates_inverted": 12, "inverted_answer_violates_textbook": 8}`
- *notes:* Solution sets are disjoint (n = 10 > k = 4); verified by exhaustive colouring.

</details>

<details><summary>Prompt and computed outputs — <code>E5-COL-N</code></summary>

```text
Ten people (Ann, Ben, Cal, Dan, Eve, Fay, Gus, Hal, Ivy, Jay) are being assigned to rooms 1–4.
The following pairs are enemies: Eve–Ivy, Ben–Ivy, Cal–Hal, Hal–Ivy, Ben–Eve, Ann–Fay, Eve–Hal, Fay–Gus, Ann–Dan, Ivy–Jay, Ann–Ivy, Fay–Hal, Cal–Eve, Ben–Dan, Dan–Fay, Cal–Fay, Ann–Jay, Ben–Cal.
No two enemies may share a room.
Note on the rule: the two people in each listed pair must be put in different rooms; people not listed together may share or not.
Is there an assignment of people to rooms 1–4 that follows this rule?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"possible": true, "rooms": {"<name>": <room number>, ...}}
{"possible": false, "rooms": null}
```

- **exact:** Ann: 1, Ben: 1, Cal: 2, Dan: 2, Eve: 3, Fay: 3, Gus: 1, Hal: 1, Ivy: 2, Jay: 3
- **A3 TT[exact]:** Ann: 1, Ben: 1, Cal: 2, Dan: 2, Eve: 3, Fay: 3, Gus: 1, Hal: 1, Ivy: 2, Jay: 3
- **A3 TT[FIRST-FIT]:** Ann: 1, Ben: 1, Cal: 2, Dan: 2, Eve: 3, Fay: 3, Gus: 1, Hal: 1, Ivy: 2, Jay: 3
- **C1 FIRST-FIT (stated rule):** Ann: 1, Ben: 1, Cal: 2, Dan: 2, Eve: 3, Fay: 3, Gus: 1, Hal: 1, Ivy: 2, Jay: 3
- **A1 ALWAYS-POSSIBLE:** possible, rooms from the uniform fill
- **H RANDOM-U:** valid w.p. 0.0027
- **B1 DROP-CONSTRAINT(★):** n/a (no ★ pairs in this framing) → as exact
- **PERCEPTION-NOISE (rule misread):** the TT answer w.p. p_r, otherwise the exact answer
- *params:* `{"friend_groups_planted": [["Ann", "Jay", "Ivy"], ["Cal", "Eve", "Hal"], ["Ben", "Dan"], ["Fay", "Gus"]], "pairs": 18, "textbook_colourings": 2880, "inverted_colourings": 24, "preamble_words_N_I": [25, 27], "textbook_answer_violates_inverted": 12, "inverted_answer_violates_textbook": 8}`
- *notes:* Solution sets are disjoint (n = 10 > k = 4); verified by exhaustive colouring.

</details>

<details><summary>Prompt and computed outputs — <code>E5-COL-I</code></summary>

```text
Ten people (Ann, Ben, Cal, Dan, Eve, Fay, Gus, Hal, Ivy, Jay) are being assigned to rooms 1–4.
The following pairs are friends: Eve–Ivy, Ben–Ivy, Cal–Hal, Hal–Ivy, Ben–Eve, Ann–Fay, Eve–Hal, Fay–Gus, Ann–Dan, Ivy–Jay, Ann–Ivy, Fay–Hal, Cal–Eve, Ben–Dan, Dan–Fay, Cal–Fay, Ann–Jay, Ben–Cal.
Only friends may share a room.
Note on the rule: people in each listed pair may share or not; any two people who are not listed together must be put in different rooms.
Is there an assignment of people to rooms 1–4 that follows this rule?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"possible": true, "rooms": {"<name>": <room number>, ...}}
{"possible": false, "rooms": null}
```

- **exact:** Ann: 1, Ben: 2, Cal: 3, Dan: 2, Eve: 3, Fay: 4, Gus: 4, Hal: 3, Ivy: 1, Jay: 1
- **A3 TT[exact]:** Ann: 1, Ben: 1, Cal: 2, Dan: 2, Eve: 3, Fay: 3, Gus: 1, Hal: 1, Ivy: 2, Jay: 3
- **A3 TT[FIRST-FIT]:** Ann: 1, Ben: 1, Cal: 2, Dan: 2, Eve: 3, Fay: 3, Gus: 1, Hal: 1, Ivy: 2, Jay: 3
- **C1 FIRST-FIT (stated rule):** Ann: 1, Ben: 2, Cal: 2, Dan: 1, Eve: 2, Fay: 1, Gus: 3, Hal: 4, Ivy: 4, Jay: 5 (needs a 5th room → 'impossible')
- **A1 ALWAYS-POSSIBLE:** possible, rooms from the uniform fill
- **H RANDOM-U:** valid w.p. 0.0000
- **B1 DROP-CONSTRAINT(★):** n/a (no ★ pairs in this framing) → as exact
- **PERCEPTION-NOISE (rule misread):** the TT answer w.p. p_r, otherwise the exact answer
- *params:* `{"friend_groups_planted": [["Ann", "Jay", "Ivy"], ["Cal", "Eve", "Hal"], ["Ben", "Dan"], ["Fay", "Gus"]], "pairs": 18, "textbook_colourings": 2880, "inverted_colourings": 24, "preamble_words_N_I": [25, 27], "textbook_answer_violates_inverted": 12, "inverted_answer_violates_textbook": 8}`
- *notes:* Solution sets are disjoint (n = 10 > k = 4); verified by exhaustive colouring.

</details>

<details><summary>Prompt and computed outputs — <code>E5-COL-I+R</code></summary>

```text
Ten people (Ann, Ben, Cal, Dan, Eve, Fay, Gus, Hal, Ivy, Jay) are being assigned to rooms 1–4.
The following pairs are friends: Eve–Ivy, Ben–Ivy, Cal–Hal, Hal–Ivy, Ben–Eve, Ann–Fay, Eve–Hal, Fay–Gus, Ann–Dan, Ivy–Jay, Ann–Ivy, Fay–Hal, Cal–Eve, Ben–Dan, Dan–Fay, Cal–Fay, Ann–Jay, Ben–Cal.
Only friends may share a room.
Note on the rule: people in each listed pair may share or not; any two people who are not listed together must be put in different rooms.
Reminder: only listed friends may share a room; everyone else must be split up.
Is there an assignment of people to rooms 1–4 that follows this rule?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"possible": true, "rooms": {"<name>": <room number>, ...}}
{"possible": false, "rooms": null}
```

- **exact:** Ann: 1, Ben: 2, Cal: 3, Dan: 2, Eve: 3, Fay: 4, Gus: 4, Hal: 3, Ivy: 1, Jay: 1
- **A3 TT[exact]:** Ann: 1, Ben: 1, Cal: 2, Dan: 2, Eve: 3, Fay: 3, Gus: 1, Hal: 1, Ivy: 2, Jay: 3
- **A3 TT[FIRST-FIT]:** Ann: 1, Ben: 1, Cal: 2, Dan: 2, Eve: 3, Fay: 3, Gus: 1, Hal: 1, Ivy: 2, Jay: 3
- **C1 FIRST-FIT (stated rule):** Ann: 1, Ben: 2, Cal: 2, Dan: 1, Eve: 2, Fay: 1, Gus: 3, Hal: 4, Ivy: 4, Jay: 5 (needs a 5th room → 'impossible')
- **A1 ALWAYS-POSSIBLE:** possible, rooms from the uniform fill
- **H RANDOM-U:** valid w.p. 0.0000
- **B1 DROP-CONSTRAINT(★):** n/a (no ★ pairs in this framing) → as exact
- **PERCEPTION-NOISE (rule misread):** the TT answer w.p. p_r, otherwise the exact answer
- *params:* `{"friend_groups_planted": [["Ann", "Jay", "Ivy"], ["Cal", "Eve", "Hal"], ["Ben", "Dan"], ["Fay", "Gus"]], "pairs": 18, "textbook_colourings": 2880, "inverted_colourings": 24, "preamble_words_N_I": [25, 27], "textbook_answer_violates_inverted": 12, "inverted_answer_violates_textbook": 8}`
- *notes:* Solution sets are disjoint (n = 10 > k = 4); verified by exhaustive colouring.

</details>

<details><summary>Prompt and computed outputs — <code>E5-COL-P</code></summary>

```text
Ten people (Ann, Ben, Cal, Dan, Eve, Fay, Gus, Hal, Ivy, Jay) are being assigned to rooms 1–4.
The following pairs are linked: Eve–Ivy, Ben–Ivy, Cal★Hal, Hal–Ivy, Ben–Eve, Ann–Fay, Eve★Hal, Fay★Gus, Ann–Dan, Ivy★Jay, Ann★Ivy, Fay–Hal, Cal★Eve, Ben★Dan, Dan–Fay, Cal–Fay, Ann★Jay, Ben–Cal.
A pair written with ★ are partners and must share a room; every pair written with – are enemies and must be in different rooms.
Is there an assignment of people to rooms 1–4 that follows these rules?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"possible": true, "rooms": {"<name>": <room number>, ...}}
{"possible": false, "rooms": null}
```

- **exact:** Ann: 1, Ben: 3, Cal: 2, Dan: 3, Eve: 2, Fay: 4, Gus: 4, Hal: 2, Ivy: 1, Jay: 1
- **A3 TT[exact]:** Ann: 1, Ben: 1, Cal: 2, Dan: 2, Eve: 3, Fay: 3, Gus: 1, Hal: 1, Ivy: 2, Jay: 3 (violates all 8 ★ pairs and 0 – pairs)
- **A3 TT[FIRST-FIT]:** Ann: 1, Ben: 1, Cal: 2, Dan: 2, Eve: 3, Fay: 3, Gus: 1, Hal: 1, Ivy: 2, Jay: 3 (treats ★ as –)
- **C1 FIRST-FIT (stated rule):** n/a (equality constraints)
- **A1 ALWAYS-POSSIBLE:** possible, uniform fill
- **H RANDOM-U:** violations spread over both pair types
- **B1 DROP-CONSTRAINT(★):** ignores ★ pairs: ★ violations like TT, but no textbook identity on I
- **PERCEPTION-NOISE (rule misread):** violations spread uniformly over ★ and – pairs
- *params:* `{"star_pairs": 8, "dash_pairs": 10}`
- *notes:* For COL, partial inversion is per pair: must share vs must differ.

</details>

**Hypothesis matrix**

| Theory | (a) `E5-COL-T` | (a) `E5-COL-N` | (a) `E5-COL-I` | (a) `E5-COL-I+R` | (a) `E5-COL-P` | (b) pure-theory statistic · weight resolution | (c) predicted trace |
|---|---|---|---|---|---|---|---|
| exact | textbook-valid | textbook-valid | inverted-valid | inverted-valid | partial-valid | Detectable π ≥ 0.05 vs PERCEPTION-NOISE (rule misread) | A completed procedure: a witness checked against every constraint, or a closed refutation / exhaustive case split. No cue given as a reason. |
| A3 TT[exact] | textbook-valid | textbook-valid | textbook-valid | textbook-valid | ★-violating | Detectable π ≥ 0.02 vs PERCEPTION-NOISE (rule misread) | REFRAME = textbook ('so the two people in each pair need different rooms'); checks use textbook semantics, or rule drift. |
| A3 TT[FIRST-FIT] | textbook-valid | textbook-valid | textbook-valid | textbook-valid | ★-violating | Detectable π ≥ 0.01 vs B1 DROP-CONSTRAINT(★) | As TT[exact], with a single pass giving each person the lowest free room. |
| PERCEPTION-NOISE (rule misread) | mixture | mixture | mixture | mixture | uniform violations | Detectable π ≥ 0.05 vs exact | One MISQUOTE of the rule itself; repaired by the reminder (I+R). |
| B1 DROP-CONSTRAINT(★) | textbook-valid | textbook-valid | inverted-valid | inverted-valid | ★-violating | Detectable π ≥ 0.02 vs exact | ★ pairs never mentioned (coverage). |
| C1 FIRST-FIT (stated rule) | textbook-valid | textbook-valid | impossible | impossible | n/a | Detectable π ≥ 0.10 vs H RANDOM-U | One pass in name order under the stated rule. |
| A1 ALWAYS-POSSIBLE | neither (≈) | neither (≈) | neither (≈) | neither (≈) | uniform violations | Detectable π ≥ 0.10 vs H RANDOM-U | 'Possible' asserted; a quick, unchecked assignment. |
| H RANDOM-U | neither (≈) | neither (≈) | neither (≈) | neither (≈) | uniform violations | Detectable π ≥ 0.03 vs C1 FIRST-FIT (stated rule) | No procedure determines the verdict; trace content and verdict unrelated. |

*(c) for every theory: the expected share of traces showing the signature ≈ π_h · r̂ (faithfulness, from E8), plus the coder's false-positive rate.*

**Likelihood ratios per observable pattern** (log₁₀ LR; one study unit)

| Pattern | Favours (log₁₀ LR vs the best theory outside the favoured group) | Pushes toward zero weight (log₁₀ LR vs the best theory) |
|---|---|---|
| I: textbook-valid, equal to the FIRST-FIT colouring | A3 TT[FIRST-FIT] (+1.8) | PERCEPTION-NOISE (rule misread) (-4.0), A3 TT[exact] (-3.5), exact (-1.9), B1 DROP-CONSTRAINT(★) (-1.9), C1 FIRST-FIT (stated rule) (-1.9), A1 ALWAYS-POSSIBLE (-1.9), H RANDOM-U (-1.8) |
| I: textbook-valid, other colouring | A3 TT[exact] (+0.5) | exact (-1.9), A3 TT[FIRST-FIT] (-1.9), B1 DROP-CONSTRAINT(★) (-1.9), C1 FIRST-FIT (stated rule) (-1.9), A1 ALWAYS-POSSIBLE (-1.9), H RANDOM-U (-1.8) |
| I: inverted-valid | exact (+1.8), B1 DROP-CONSTRAINT(★) (+1.8), PERCEPTION-NOISE (rule misread) (+1.6) | A3 TT[FIRST-FIT] (-1.9), C1 FIRST-FIT (stated rule) (-1.9), A1 ALWAYS-POSSIBLE (-1.9), A3 TT[exact] (-1.8), H RANDOM-U (-1.8) |
| I: neither | A1 ALWAYS-POSSIBLE (+0.3) | exact (-1.9), A3 TT[FIRST-FIT] (-1.9), B1 DROP-CONSTRAINT(★) (-1.9), C1 FIRST-FIT (stated rule) (-1.9), A3 TT[exact] (-1.8), PERCEPTION-NOISE (rule misread) (-1.6) |
| I: declared impossible | C1 FIRST-FIT (stated rule) (+1.6), H RANDOM-U (+1.3) | exact (-1.9), A3 TT[FIRST-FIT] (-1.9), B1 DROP-CONSTRAINT(★) (-1.9), A1 ALWAYS-POSSIBLE (-1.9), A3 TT[exact] (-1.8), PERCEPTION-NOISE (rule misread) (-1.6) |
| I+R: inverted-valid | exact (+1.8), B1 DROP-CONSTRAINT(★) (+1.8), PERCEPTION-NOISE (rule misread) (+1.7) | A3 TT[FIRST-FIT] (-1.9), C1 FIRST-FIT (stated rule) (-1.9), A1 ALWAYS-POSSIBLE (-1.9), A3 TT[exact] (-1.8), H RANDOM-U (-1.8) |
| I+R: textbook-valid (other) | A3 TT[exact] (+1.3) | exact (-1.9), A3 TT[FIRST-FIT] (-1.9), B1 DROP-CONSTRAINT(★) (-1.9), C1 FIRST-FIT (stated rule) (-1.9), A1 ALWAYS-POSSIBLE (-1.9), H RANDOM-U (-1.8), PERCEPTION-NOISE (rule misread) (-1.3) |
| P: violations concentrated on ★ pairs | A3 TT[exact] (+1.6), A3 TT[FIRST-FIT] (+1.6), B1 DROP-CONSTRAINT(★) (+1.6) | exact (-1.8), C1 FIRST-FIT (stated rule) (-1.8), A1 ALWAYS-POSSIBLE (-1.8), PERCEPTION-NOISE (rule misread) (-1.6), H RANDOM-U (-1.6) |
| P: violations spread | C1 FIRST-FIT (stated rule) (+0.5), A1 ALWAYS-POSSIBLE (+0.5), H RANDOM-U (+0.2) | exact (-1.8), A3 TT[exact] (-1.8), A3 TT[FIRST-FIT] (-1.8), B1 DROP-CONSTRAINT(★) (-1.8) |
| P: valid | exact (+1.6), PERCEPTION-NOISE (rule misread) (+1.4) | A3 TT[exact] (-1.8), A3 TT[FIRST-FIT] (-1.8), B1 DROP-CONSTRAINT(★) (-1.8), C1 FIRST-FIT (stated rule) (-1.8), A1 ALWAYS-POSSIBLE (-1.8), H RANDOM-U (-1.6) |

**Weight resolution at study N**

| Theory | Nearest competitor (smallest KL) | Detectable π vs it (80% power) | Upper 95% bound on π if pure competitor | E[log₁₀ BF] vs competitor | Detectable π if the rest is the hardest base (which) | Identical predictions here |
|---|---|---|---|---|---|---|
| exact | PERCEPTION-NOISE (rule misread) | 0.052 | 0.035 | 66.1 | 0.052 (PERCEPTION-NOISE (rule misread)) | — |
| A3 TT[exact] | PERCEPTION-NOISE (rule misread) | 0.024 | 0.016 | 614.7 | 0.024 (PERCEPTION-NOISE (rule misread)) | — |
| A3 TT[FIRST-FIT] | B1 DROP-CONSTRAINT(★) | 0.015 | 0.010 | 705.3 | 0.015 (H RANDOM-U) | — |
| PERCEPTION-NOISE (rule misread) | exact | 0.051 | 0.034 | 124.8 | 0.051 (exact) | — |
| B1 DROP-CONSTRAINT(★) | exact | 0.024 | 0.016 | 327.8 | 0.026 (PERCEPTION-NOISE (rule misread)) | — |
| C1 FIRST-FIT (stated rule) | H RANDOM-U | 0.105 | 0.070 | 155.8 | 0.105 (H RANDOM-U) | — |
| A1 ALWAYS-POSSIBLE | H RANDOM-U | 0.105 | 0.070 | 155.8 | 0.105 (H RANDOM-U) | — |
| H RANDOM-U | C1 FIRST-FIT (stated rule) | 0.025 | 0.017 | 356.8 | 0.025 (A1 ALWAYS-POSSIBLE) | — |

**Not separated here.** TT and B1 DROP-CONSTRAINT(★) coincide on P; they are separated on I (B1 has no ★ to drop there). A1 ALWAYS-POSSIBLE and RANDOM are separated here only by the 'declared impossible' rate (0 vs ½).

<a id="e5-sat"></a>
## E5: inversion pair, SAT (N vs I)

**Reasoning question.** Under the literal-flipped rule, does the model output the textbook solution?

**Design.** The same clause list under the standard and inverted clause semantics; both solutions unique.  *Study units:* I witness × 200.

| Item | Cell | Ground truth | Controlled | Varied |
|---|---|---|---|---|
| `E5-SAT-N` | N (textbook + neutral preamble) | SAT, unique assignment 0101101000 | clause list and order; preamble word count | rule semantics: standard vs every literal flipped |
| `E5-SAT-I` | I (inverted) | SAT, unique assignment 1010010111 | clause list and order; preamble word count | rule semantics: standard vs every literal flipped |

<details><summary>Prompt and computed outputs — <code>E5-SAT-N</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.
Note on the rule: this is the usual reading; a clause fails only when every one of its three literals is false.

C01: (x08 ∨ ¬x06 ∨ ¬x01)
C02: (¬x01 ∨ x08 ∨ ¬x03)
C03: (¬x09 ∨ ¬x03 ∨ x05)
C04: (x10 ∨ ¬x02 ∨ ¬x08)
C05: (¬x06 ∨ ¬x02 ∨ ¬x09)
C06: (¬x06 ∨ x03 ∨ x04)
C07: (x07 ∨ ¬x02 ∨ x03)
C08: (¬x07 ∨ ¬x05 ∨ x02)
C09: (¬x07 ∨ ¬x08 ∨ x06)
C10: (x08 ∨ ¬x06 ∨ ¬x10)
C11: (¬x06 ∨ ¬x04 ∨ ¬x05)
C12: (x03 ∨ x09 ∨ ¬x10)
C13: (¬x03 ∨ x09 ∨ ¬x04)
C14: (x10 ∨ x04 ∨ ¬x02)
C15: (¬x01 ∨ x02 ∨ x04)
C16: (¬x04 ∨ x10 ∨ x05)
C17: (¬x08 ∨ x07 ∨ ¬x05)
C18: (¬x08 ∨ ¬x03 ∨ ¬x05)
C19: (¬x10 ∨ ¬x06 ∨ ¬x02)
C20: (¬x09 ∨ ¬x07 ∨ x01)
C21: (x04 ∨ x06 ∨ x02)
C22: (x05 ∨ ¬x07 ∨ x10)
C23: (¬x08 ∨ x05 ∨ ¬x07)
C24: (¬x08 ∨ x07 ∨ ¬x09)
C25: (¬x10 ∨ x03 ∨ ¬x05)
C26: (¬x09 ∨ ¬x07 ∨ x08)
C27: (¬x08 ∨ x09 ∨ x03)
C28: (x07 ∨ x05 ∨ ¬x06)
C29: (¬x10 ∨ ¬x06 ∨ ¬x02)
C30: (x04 ∨ x08 ∨ x05)
C31: (x02 ∨ x05 ∨ ¬x10)
C32: (¬x07 ∨ ¬x09 ∨ x02)
C33: (¬x02 ∨ x07 ∨ x06)
C34: (x09 ∨ ¬x05 ∨ ¬x06)
C35: (¬x07 ∨ ¬x02 ∨ ¬x06)
C36: (x06 ∨ ¬x05 ∨ ¬x01)
C37: (¬x05 ∨ ¬x04 ∨ x02)
C38: (x07 ∨ ¬x09 ∨ x04)
C39: (¬x04 ∨ ¬x03 ∨ x10)
C40: (¬x10 ∨ x06 ∨ x09)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** 0101101000
- **A3 TT[exact]:** 0101101000
- **A1/A2 decision cues:** SAT; witness from the fill (the decision is the same under both readings)
- **H RANDOM-U:** witness violates ≈ 1/8 of clauses under either reading
- *params:* `{"n": 10, "m": 40, "TT_answer_violations_under_stated_rule": 0}`
- *notes:* F ∧ F̄ checked UNSAT, so no textbook solution is valid when inverted; both solutions unique.

</details>

<details><summary>Prompt and computed outputs — <code>E5-SAT-I</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10.
Each clause lists three literals ("¬" means NOT). In this puzzle a clause is satisfied when at least one of its literals is FALSE. The formula is the conjunction of all clauses.
Note on the rule: this is not the usual reading; a clause fails only when every one of its three literals is true.

C01: (x08 ∨ ¬x06 ∨ ¬x01)
C02: (¬x01 ∨ x08 ∨ ¬x03)
C03: (¬x09 ∨ ¬x03 ∨ x05)
C04: (x10 ∨ ¬x02 ∨ ¬x08)
C05: (¬x06 ∨ ¬x02 ∨ ¬x09)
C06: (¬x06 ∨ x03 ∨ x04)
C07: (x07 ∨ ¬x02 ∨ x03)
C08: (¬x07 ∨ ¬x05 ∨ x02)
C09: (¬x07 ∨ ¬x08 ∨ x06)
C10: (x08 ∨ ¬x06 ∨ ¬x10)
C11: (¬x06 ∨ ¬x04 ∨ ¬x05)
C12: (x03 ∨ x09 ∨ ¬x10)
C13: (¬x03 ∨ x09 ∨ ¬x04)
C14: (x10 ∨ x04 ∨ ¬x02)
C15: (¬x01 ∨ x02 ∨ x04)
C16: (¬x04 ∨ x10 ∨ x05)
C17: (¬x08 ∨ x07 ∨ ¬x05)
C18: (¬x08 ∨ ¬x03 ∨ ¬x05)
C19: (¬x10 ∨ ¬x06 ∨ ¬x02)
C20: (¬x09 ∨ ¬x07 ∨ x01)
C21: (x04 ∨ x06 ∨ x02)
C22: (x05 ∨ ¬x07 ∨ x10)
C23: (¬x08 ∨ x05 ∨ ¬x07)
C24: (¬x08 ∨ x07 ∨ ¬x09)
C25: (¬x10 ∨ x03 ∨ ¬x05)
C26: (¬x09 ∨ ¬x07 ∨ x08)
C27: (¬x08 ∨ x09 ∨ x03)
C28: (x07 ∨ x05 ∨ ¬x06)
C29: (¬x10 ∨ ¬x06 ∨ ¬x02)
C30: (x04 ∨ x08 ∨ x05)
C31: (x02 ∨ x05 ∨ ¬x10)
C32: (¬x07 ∨ ¬x09 ∨ x02)
C33: (¬x02 ∨ x07 ∨ x06)
C34: (x09 ∨ ¬x05 ∨ ¬x06)
C35: (¬x07 ∨ ¬x02 ∨ ¬x06)
C36: (x06 ∨ ¬x05 ∨ ¬x01)
C37: (¬x05 ∨ ¬x04 ∨ x02)
C38: (x07 ∨ ¬x09 ∨ x04)
C39: (¬x04 ∨ ¬x03 ∨ x10)
C40: (¬x10 ∨ x06 ∨ x09)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** 1010010111
- **A3 TT[exact]:** 0101101000 — the textbook solution, identical to its N answer
- **A1/A2 decision cues:** SAT; witness from the fill (the decision is the same under both readings)
- **H RANDOM-U:** witness violates ≈ 1/8 of clauses under either reading
- *params:* `{"n": 10, "m": 40, "TT_answer_violations_under_stated_rule": 6}`
- *notes:* F ∧ F̄ checked UNSAT, so no textbook solution is valid when inverted; both solutions unique.

</details>

**Hypothesis matrix**

| Theory | (a) `E5-SAT-N` | (a) `E5-SAT-I` | (b) pure-theory statistic · weight resolution | (c) predicted trace |
|---|---|---|---|---|
| exact | 0101101000 | 1010010111 | Detectable π ≥ 0.03 vs A3 TT[exact] | A completed procedure: a witness checked against every constraint, or a closed refutation / exhaustive case split. No cue given as a reason. |
| A3 TT[exact] | 0101101000 | 0101101000 — the textbook solution, identical to | Detectable π ≥ 0.03 vs exact | REFRAME = textbook ('so the two people in each pair need different rooms'); checks use textbook semantics, or rule drift. |
| A1/A2 decision cues | SAT | SAT | π unresolved here vs H RANDOM-U | Decision from a cue; the witness is not derived. |
| H RANDOM-U | witness violates ≈ 1/8 of clauses under either r | witness violates ≈ 1/8 of clauses under either r | π unresolved here vs A1/A2 decision cues | No procedure determines the verdict; trace content and verdict unrelated. |

*(c) for every theory: the expected share of traces showing the signature ≈ π_h · r̂ (faithfulness, from E8), plus the coder's false-positive rate.*

**Likelihood ratios per observable pattern** (log₁₀ LR; one study unit)

| Pattern | Favours (log₁₀ LR vs the best theory outside the favoured group) | Pushes toward zero weight (log₁₀ LR vs the best theory) |
|---|---|---|
| I: the textbook solution | A3 TT[exact] (+1.6) | A1/A2 decision cues (-1.6), exact (-1.6), H RANDOM-U (-1.6) |
| I: the inverted solution | exact (+1.6) | A1/A2 decision cues (-1.6), A3 TT[exact] (-1.6), H RANDOM-U (-1.6) |
| I: neither | A1/A2 decision cues (+1.6), H RANDOM-U (+1.6) | exact (-1.6), A3 TT[exact] (-1.6) |

**Weight resolution at study N**

| Theory | Nearest competitor (smallest KL) | Detectable π vs it (80% power) | Upper 95% bound on π if pure competitor | E[log₁₀ BF] vs competitor | Detectable π if the rest is the hardest base (which) | Identical predictions here |
|---|---|---|---|---|---|---|
| exact | A3 TT[exact] | 0.030 | 0.020 | 292.3 | 0.030 (A3 TT[exact]) | — |
| A3 TT[exact] | exact | 0.030 | 0.020 | 292.3 | 0.030 (exact) | — |
| A1/A2 decision cues | H RANDOM-U | > 1 (unresolved at this N) | > 1 (unresolved at this N) | 0.0 | > 1 (unresolved at this N) (H RANDOM-U) | — |
| H RANDOM-U | A1/A2 decision cues | > 1 (unresolved at this N) | > 1 (unresolved at this N) | 0.0 | > 1 (unresolved at this N) (A1/A2 decision cues) | — |

**Not separated here.** The decision is identical under both readings, so only the witness discriminates. A1/A2 and RANDOM are separated elsewhere (E1–E3).

<a id="e6"></a>
## E6: counter-model rarity (one premise set, six conclusions)

**Reasoning question.** Does endorsement fall with ρ along (1 − ρ)^m?

**Design.** Fixed premises; six two-literal disjunctions chosen to set ρ ∈ {0, 1, 2, 4, 8, ≥ 10}/16.  *Study units:* six conclusions × 200.

| Item | Cell | Ground truth | Controlled | Varied |
|---|---|---|---|---|
| `E6-rho0` | ρ = 0/16 | follows | premises; conclusion form (two-literal disjunction, one literal negated) and word count | the conclusion, chosen to set the counter-model fraction ρ |
| `E6-rho1` | ρ = 1/16 | does not follow | premises; conclusion form (two-literal disjunction, one literal negated) and word count | the conclusion, chosen to set the counter-model fraction ρ |
| `E6-rho2` | ρ = 2/16 | does not follow | premises; conclusion form (two-literal disjunction, one literal negated) and word count | the conclusion, chosen to set the counter-model fraction ρ |
| `E6-rho3` | ρ = 4/16 | does not follow | premises; conclusion form (two-literal disjunction, one literal negated) and word count | the conclusion, chosen to set the counter-model fraction ρ |
| `E6-rho4` | ρ = 8/16 | does not follow | premises; conclusion form (two-literal disjunction, one literal negated) and word count | the conclusion, chosen to set the counter-model fraction ρ |
| `E6-rho5` | ρ = 12/16 | does not follow | premises; conclusion form (two-literal disjunction, one literal negated) and word count | the conclusion, chosen to set the counter-model fraction ρ |

<details><summary>Prompt and computed outputs — <code>E6-rho0</code></summary>

```text
Here are some facts about a machine.

- Either the fan is running and the lamp is lit, or the gate is locked.
- Either the gate is not locked and the door is open, or the door is not open, or the fan is not running and the door is not open.
- Either the fan is not running and the door is not open, or the alarm is not armed.

Question: Does it follow from these facts that the door is not open or the lamp is lit?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** follows
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** follows (literal counts [3, 1]; max vs illustrative θ = 2)
- **A2 ATMOSPHERE:** follows (atm(P) = disj/neg, mood(C) = disj/neg)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 1.000 (ρ = 0.000)
- **NOISY-EXACT:** follows w.p. 0.90
- **PERCEPTION-NOISE:** follows unless a misread breaks it: P(does not follow) = 0.091
- **B1 UP-1:** does not follow (not UP-derivable)
- **B1 UP-2:** does not follow (not UP-derivable)
- **B4 ETR:** does not follow (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** does not follow
- **B4 MATCH:** does not follow
- **D case-split (b = 4):** follows
- *params:* `{"atoms": 6, "rho": 0.0, "n_models": 16, "up_depth": null, "kappa_follow": 0.545, "kappa_break": 0.455, "eta_first_counter": null, "etr_what_follows": "{a4(),a4()~a1()~a3()~a5()}", "propagation_steps_beyond_facts": null}`
- *notes:* Dev-size (6 atoms, 3 premises, 16 models). The top level is the largest available ρ ≥ 10/16. Study: 7 atoms, with ρ decorrelated from κ, η and PyETR across items.

</details>

<details><summary>Prompt and computed outputs — <code>E6-rho1</code></summary>

```text
Here are some facts about a machine.

- Either the fan is running and the lamp is lit, or the gate is locked.
- Either the gate is not locked and the door is open, or the door is not open, or the fan is not running and the door is not open.
- Either the fan is not running and the door is not open, or the alarm is not armed.

Question: Does it follow from these facts that the bell is ringing or the door is not open?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** does not follow
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** follows (literal counts [0, 3]; max vs illustrative θ = 2)
- **A2 ATMOSPHERE:** follows (atm(P) = disj/neg, mood(C) = disj/neg)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 0.597 (ρ = 0.062)
- **NOISY-EXACT:** does not follow w.p. 0.90
- **PERCEPTION-NOISE:** does not follow unless a misread makes it follow: P(follows) = 0.018
- **B1 UP-1:** does not follow (not UP-derivable)
- **B1 UP-2:** does not follow (not UP-derivable)
- **B4 ETR:** does not follow (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** does not follow
- **B4 MATCH:** does not follow
- **D case-split (b = 4):** follows (first counter-model is #9 of 16 in atom order; budget 4 cases)
- *params:* `{"atoms": 6, "rho": 0.0625, "n_models": 16, "up_depth": null, "kappa_follow": 0.091, "kappa_break": 0.909, "eta_first_counter": 9, "etr_what_follows": "{a4(),a4()~a1()~a3()~a5()}", "propagation_steps_beyond_facts": null}`
- *notes:* Dev-size (6 atoms, 3 premises, 16 models). The top level is the largest available ρ ≥ 10/16. Study: 7 atoms, with ρ decorrelated from κ, η and PyETR across items.

</details>

<details><summary>Prompt and computed outputs — <code>E6-rho2</code></summary>

```text
Here are some facts about a machine.

- Either the fan is running and the lamp is lit, or the gate is locked.
- Either the gate is not locked and the door is open, or the door is not open, or the fan is not running and the door is not open.
- Either the fan is not running and the door is not open, or the alarm is not armed.

Question: Does it follow from these facts that the bell is not ringing or the gate is locked?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** does not follow
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** does not follow (literal counts [0, 1]; max vs illustrative θ = 2)
- **A2 ATMOSPHERE:** follows (atm(P) = disj/neg, mood(C) = disj/neg)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 0.344 (ρ = 0.125)
- **NOISY-EXACT:** does not follow w.p. 0.90
- **PERCEPTION-NOISE:** does not follow unless a misread makes it follow: P(follows) = 0.000
- **B1 UP-1:** does not follow (not UP-derivable)
- **B1 UP-2:** does not follow (not UP-derivable)
- **B4 ETR:** does not follow (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** does not follow
- **B4 MATCH:** does not follow
- **D case-split (b = 4):** does not follow (first counter-model is #1 of 16 in atom order; budget 4 cases)
- *params:* `{"atoms": 6, "rho": 0.125, "n_models": 16, "up_depth": null, "kappa_follow": 0.0, "kappa_break": 1.0, "eta_first_counter": 1, "etr_what_follows": "{a4(),a4()~a1()~a3()~a5()}", "propagation_steps_beyond_facts": null}`
- *notes:* Dev-size (6 atoms, 3 premises, 16 models). The top level is the largest available ρ ≥ 10/16. Study: 7 atoms, with ρ decorrelated from κ, η and PyETR across items.

</details>

<details><summary>Prompt and computed outputs — <code>E6-rho3</code></summary>

```text
Here are some facts about a machine.

- Either the fan is running and the lamp is lit, or the gate is locked.
- Either the gate is not locked and the door is open, or the door is not open, or the fan is not running and the door is not open.
- Either the fan is not running and the door is not open, or the alarm is not armed.

Question: Does it follow from these facts that the bell is ringing or the fan is not running?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** does not follow
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** follows (literal counts [0, 2]; max vs illustrative θ = 2)
- **A2 ATMOSPHERE:** follows (atm(P) = disj/neg, mood(C) = disj/neg)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 0.100 (ρ = 0.250)
- **NOISY-EXACT:** does not follow w.p. 0.90
- **PERCEPTION-NOISE:** does not follow unless a misread makes it follow: P(follows) = 0.000
- **B1 UP-1:** does not follow (not UP-derivable)
- **B1 UP-2:** does not follow (not UP-derivable)
- **B4 ETR:** does not follow (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** does not follow
- **B4 MATCH:** does not follow
- **D case-split (b = 4):** follows (first counter-model is #9 of 16 in atom order; budget 4 cases)
- *params:* `{"atoms": 6, "rho": 0.25, "n_models": 16, "up_depth": null, "kappa_follow": 0.0, "kappa_break": 1.0, "eta_first_counter": 9, "etr_what_follows": "{a4(),a4()~a1()~a3()~a5()}", "propagation_steps_beyond_facts": null}`
- *notes:* Dev-size (6 atoms, 3 premises, 16 models). The top level is the largest available ρ ≥ 10/16. Study: 7 atoms, with ρ decorrelated from κ, η and PyETR across items.

</details>

<details><summary>Prompt and computed outputs — <code>E6-rho4</code></summary>

```text
Here are some facts about a machine.

- Either the fan is running and the lamp is lit, or the gate is locked.
- Either the gate is not locked and the door is open, or the door is not open, or the fan is not running and the door is not open.
- Either the fan is not running and the door is not open, or the alarm is not armed.

Question: Does it follow from these facts that the door is open or the lamp is not lit?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** does not follow
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** does not follow (literal counts [1, 0]; max vs illustrative θ = 2)
- **A2 ATMOSPHERE:** follows (atm(P) = disj/neg, mood(C) = disj/neg)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 0.004 (ρ = 0.500)
- **NOISY-EXACT:** does not follow w.p. 0.90
- **PERCEPTION-NOISE:** does not follow unless a misread makes it follow: P(follows) = 0.000
- **B1 UP-1:** does not follow (not UP-derivable)
- **B1 UP-2:** does not follow (not UP-derivable)
- **B4 ETR:** does not follow (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** does not follow
- **B4 MATCH:** does not follow
- **D case-split (b = 4):** does not follow (first counter-model is #2 of 16 in atom order; budget 4 cases)
- *params:* `{"atoms": 6, "rho": 0.5, "n_models": 16, "up_depth": null, "kappa_follow": 0.0, "kappa_break": 1.0, "eta_first_counter": 2, "etr_what_follows": "{a4(),a4()~a1()~a3()~a5()}", "propagation_steps_beyond_facts": null}`
- *notes:* Dev-size (6 atoms, 3 premises, 16 models). The top level is the largest available ρ ≥ 10/16. Study: 7 atoms, with ρ decorrelated from κ, η and PyETR across items.

</details>

<details><summary>Prompt and computed outputs — <code>E6-rho5</code></summary>

```text
Here are some facts about a machine.

- Either the fan is running and the lamp is lit, or the gate is locked.
- Either the gate is not locked and the door is open, or the door is not open, or the fan is not running and the door is not open.
- Either the fan is not running and the door is not open, or the alarm is not armed.

Question: Does it follow from these facts that the door is open or the gate is not locked?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"follows": true} or {"follows": false}
```

- **exact:** does not follow
- **A1 ALWAYS-YES:** follows
- **A1 NONE:** does not follow
- **A2 FREQ:** does not follow (literal counts [1, 1]; max vs illustrative θ = 2)
- **A2 ATMOSPHERE:** follows (atm(P) = disj/neg, mood(C) = disj/neg)
- **A2 PRIMACY:** does not follow
- **A2 RECENCY:** does not follow
- **H RANDOM-U:** follows w.p. ½
- **H SAMPLE-8:** follows w.p. 0.000 (ρ = 0.750)
- **NOISY-EXACT:** does not follow w.p. 0.90
- **PERCEPTION-NOISE:** does not follow unless a misread makes it follow: P(follows) = 0.000
- **B1 UP-1:** does not follow (not UP-derivable)
- **B1 UP-2:** does not follow (not UP-derivable)
- **B4 ETR:** does not follow (PyETR default_procedure_does_it_follow)
- **B4 FIRST:** does not follow
- **B4 MATCH:** does not follow
- **D case-split (b = 4):** does not follow (first counter-model is #2 of 16 in atom order; budget 4 cases)
- *params:* `{"atoms": 6, "rho": 0.75, "n_models": 16, "up_depth": null, "kappa_follow": 0.0, "kappa_break": 1.0, "eta_first_counter": 2, "etr_what_follows": "{a4(),a4()~a1()~a3()~a5()}", "propagation_steps_beyond_facts": null}`
- *notes:* Dev-size (6 atoms, 3 premises, 16 models). The top level is the largest available ρ ≥ 10/16. Study: 7 atoms, with ρ decorrelated from κ, η and PyETR across items.

</details>

**Hypothesis matrix**

| Theory | (a) `E6-rho0` | (a) `E6-rho1` | (a) `E6-rho2` | (a) `E6-rho3` | (a) `E6-rho4` | (a) `E6-rho5` | (b) pure-theory statistic · weight resolution | (c) predicted trace |
|---|---|---|---|---|---|---|---|---|
| exact | follows | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows \| ρ = 1/16) − P(follows \| ρ = 8/16) = +0.00. π unresolved here vs PERCEPTION-NOISE | A completed procedure: a witness checked against every constraint, or a closed refutation / exhaustive case split. No cue given as a reason. |
| A1 ALWAYS-YES | follows | follows | follows | follows | follows | follows | P(follows \| ρ = 1/16) − P(follows \| ρ = 8/16) = +0.00. Detectable π ≥ 0.03 vs H RANDOM-U | The conclusion asserted with no derivation and no search for a counter-model. |
| A1 NONE | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows \| ρ = 1/16) − P(follows \| ρ = 8/16) = +0.00. Detectable π ≥ 0.06 vs NOISY-EXACT | 'Nothing definite follows', with no case analysis. |
| A2 FREQ | follows | follows | does not follow | follows | does not follow | does not follow | P(follows \| ρ = 1/16) − P(follows \| ρ = 8/16) = +1.00. Detectable π ≥ 0.04 vs H SAMPLE-8 | CUE-FREQ ('the bell ringing comes up most often'). |
| A2 ATMOSPHERE | follows | follows | follows | follows | follows | follows | P(follows \| ρ = 1/16) − P(follows \| ρ = 8/16) = +0.00. Detectable π ≥ 0.03 vs H RANDOM-U | CUE-MOOD: the conclusion's form or polarity matched to the premises without a derivation. |
| A2 PRIMACY | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows \| ρ = 1/16) − P(follows \| ρ = 8/16) = +0.00. Detectable π ≥ 0.06 vs NOISY-EXACT | CUE-POS on the first premise or option; other options not evaluated. |
| A2 RECENCY | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows \| ρ = 1/16) − P(follows \| ρ = 8/16) = +0.00. Detectable π ≥ 0.06 vs NOISY-EXACT | CUE-POS on the last premise or option. |
| H RANDOM-U | follows w.p. ½ | follows w.p. ½ | follows w.p. ½ | follows w.p. ½ | follows w.p. ½ | follows w.p. ½ | P(follows \| ρ = 1/16) − P(follows \| ρ = 8/16) = +0.00. Detectable π ≥ 0.01 vs NOISY-EXACT | No procedure determines the verdict; trace content and verdict unrelated. |
| H SAMPLE-8 | follows w.p. 1.000 | follows w.p. 0.597 | follows w.p. 0.344 | follows w.p. 0.100 | follows w.p. 0.004 | follows w.p. 0.000 | P(follows \| ρ = 1/16) − P(follows \| ρ = 8/16) = +0.59. Detectable π ≥ 0.07 vs NOISY-EXACT | SAMPLE(k): at most 8 concrete cases checked, then a universal conclusion; no exhaustive split. |
| NOISY-EXACT | follows w.p. 0.90 | does not follow w.p. 0.90 | does not follow w.p. 0.90 | does not follow w.p. 0.90 | does not follow w.p. 0.90 | does not follow w.p. 0.90 | P(follows \| ρ = 1/16) − P(follows \| ρ = 8/16) = +0.00. Detectable π ≥ 0.32 vs PERCEPTION-NOISE | A systematic procedure; an EVALSLIP precedes every error. |
| PERCEPTION-NOISE | follows | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows \| ρ = 1/16) − P(follows \| ρ = 8/16) = +0.02. Detectable π ≥ 0.94 vs exact | A MISQUOTE of a constraint (a dropped ¬, a wrong pair, a missing clause); later reasoning consistent with the misquote. |
| B1 UP-2 | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows \| ρ = 1/16) − P(follows \| ρ = 8/16) = +0.00. Detectable π ≥ 0.06 vs NOISY-EXACT | PROP only, two rounds; no case split. |
| B4 ETR | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows \| ρ = 1/16) − P(follows \| ρ = 8/16) = +0.00. Detectable π ≥ 0.06 vs NOISY-EXACT | COMMIT-DISJ / TRUE-ONLY: the disjunct matching the categorical fact kept, the others dropped. |
| B4 FIRST | does not follow | does not follow | does not follow | does not follow | does not follow | does not follow | P(follows \| ρ = 1/16) − P(follows \| ρ = 8/16) = +0.00. Detectable π ≥ 0.06 vs NOISY-EXACT | COMMIT-DISJ on each first disjunct, never revisited. |
| D case-split (b = 4) | follows | follows | does not follow | follows | does not follow | does not follow | P(follows \| ρ = 1/16) − P(follows \| ρ = 8/16) = +1.00. Detectable π ≥ 0.04 vs H SAMPLE-8 | A systematic case split abandoned after ≈ 4 cases; 'follows' if no counter-model was found. |

*(c) for every theory: the expected share of traces showing the signature ≈ π_h · r̂ (faithfulness, from E8), plus the coder's false-positive rate.*

**Likelihood ratios per observable pattern** (log₁₀ LR; one study unit)

| Pattern | Favours (log₁₀ LR vs the best theory outside the favoured group) | Pushes toward zero weight (log₁₀ LR vs the best theory) |
|---|---|---|
| ρ = 1/16: follows; ρ = 8/16: not | A2 FREQ (+0.6), D case-split (b = 4) (+0.6), H SAMPLE-8 (+0.4) | exact (-1.3), A1 ALWAYS-YES (-1.3), A1 NONE (-1.3), A2 ATMOSPHERE (-1.3), A2 PRIMACY (-1.3), A2 RECENCY (-1.3), PERCEPTION-NOISE (-1.3), B1 UP-2 (-1.3), B4 ETR (-1.3), B4 FIRST (-1.3), NOISY-EXACT (-1.0) |
| ρ = 1/16 and ρ = 8/16 both: follows | A1 ALWAYS-YES (+0.6), A2 ATMOSPHERE (+0.6) | exact (-2.6), A1 NONE (-2.6), A2 PRIMACY (-2.6), A2 RECENCY (-2.6), PERCEPTION-NOISE (-2.6), B1 UP-2 (-2.6), B4 ETR (-2.6), B4 FIRST (-2.6), NOISY-EXACT (-2.0), H SAMPLE-8 (-1.5), A2 FREQ (-1.3), D case-split (b = 4) (-1.3) |
| ρ = 1/16 and ρ = 8/16 both: not | exact (+0.4), A1 NONE (+0.4), A2 PRIMACY (+0.4), A2 RECENCY (+0.4), PERCEPTION-NOISE (+0.4), B1 UP-2 (+0.4), B4 ETR (+0.4), B4 FIRST (+0.4), NOISY-EXACT (+0.3) | A1 ALWAYS-YES (-2.6), A2 ATMOSPHERE (-2.6), A2 FREQ (-1.3), D case-split (b = 4) (-1.3) |
| exact pattern (only ρ = 0 follows) | exact (+0.6), PERCEPTION-NOISE (+0.5), NOISY-EXACT (+0.4) | A1 ALWAYS-YES (-6.4), A2 ATMOSPHERE (-6.4), A2 FREQ (-2.6), D case-split (b = 4) (-2.6), H RANDOM-U (-1.7), A1 NONE (-1.3), A2 PRIMACY (-1.3), A2 RECENCY (-1.3), B1 UP-2 (-1.3), B4 ETR (-1.3), B4 FIRST (-1.3) |

**Weight resolution at study N**

| Theory | Nearest competitor (smallest KL) | Detectable π vs it (80% power) | Upper 95% bound on π if pure competitor | E[log₁₀ BF] vs competitor | Detectable π if the rest is the hardest base (which) | Identical predictions here |
|---|---|---|---|---|---|---|
| exact | PERCEPTION-NOISE | > 1 (unresolved at this N) | 0.817 | 1.0 | > 1 (unresolved at this N) (PERCEPTION-NOISE) | — |
| A1 ALWAYS-YES | H RANDOM-U | 0.030 | 0.020 | 257.8 | 0.030 (H RANDOM-U) | A2 ATMOSPHERE |
| A1 NONE | NOISY-EXACT | 0.057 | 0.038 | 180.5 | 0.059 (PERCEPTION-NOISE) | A2 PRIMACY, A2 RECENCY, B1 UP-2, B4 ETR, B4 FIRST |
| A2 FREQ | H SAMPLE-8 | 0.042 | 0.027 | 224.6 | 0.042 (H SAMPLE-8) | D case-split (b = 4) |
| A2 ATMOSPHERE | H RANDOM-U | 0.030 | 0.020 | 257.8 | 0.030 (H RANDOM-U) | A1 ALWAYS-YES |
| A2 PRIMACY | NOISY-EXACT | 0.057 | 0.038 | 180.5 | 0.059 (PERCEPTION-NOISE) | A1 NONE, A2 RECENCY, B1 UP-2, B4 ETR, B4 FIRST |
| A2 RECENCY | NOISY-EXACT | 0.057 | 0.038 | 180.5 | 0.059 (PERCEPTION-NOISE) | A1 NONE, A2 PRIMACY, B1 UP-2, B4 ETR, B4 FIRST |
| H RANDOM-U | NOISY-EXACT | 0.008 | 0.005 | 266.2 | 0.008 (NOISY-EXACT) | — |
| H SAMPLE-8 | NOISY-EXACT | 0.073 | 0.049 | 87.7 | 0.073 (NOISY-EXACT) | — |
| NOISY-EXACT | PERCEPTION-NOISE | 0.324 | 0.215 | 9.0 | 0.324 (PERCEPTION-NOISE) | — |
| PERCEPTION-NOISE | exact | 0.937 | 0.620 | 1.2 | 0.937 (exact) | — |
| B1 UP-2 | NOISY-EXACT | 0.057 | 0.038 | 180.5 | 0.059 (PERCEPTION-NOISE) | A1 NONE, A2 PRIMACY, A2 RECENCY, B4 ETR, B4 FIRST |
| B4 ETR | NOISY-EXACT | 0.057 | 0.038 | 180.5 | 0.059 (PERCEPTION-NOISE) | A1 NONE, A2 PRIMACY, A2 RECENCY, B1 UP-2, B4 FIRST |
| B4 FIRST | NOISY-EXACT | 0.057 | 0.038 | 180.5 | 0.059 (PERCEPTION-NOISE) | A1 NONE, A2 PRIMACY, A2 RECENCY, B1 UP-2, B4 ETR |
| D case-split (b = 4) | H SAMPLE-8 | 0.042 | 0.027 | 224.6 | 0.042 (H SAMPLE-8) | A2 FREQ |

**Not separated here.** On one premise set, κ and η are not decorrelated from ρ, so PERCEPTION-NOISE and D case-split (b = 4) can mimic the ρ curve. The study decorrelates them across 200 sets, and the ρ × κ 2 × 2 subset separates SAMPLE-m from PERCEPTION-NOISE.

<a id="e7"></a>
## E7: four renderings of one SAT item (+ echo condition)

**Reasoning question.** Are errors systematic (item-determined) or exchangeable noise?

**Design.** R1 permutes variable indices; R2 permutes clause and literal order; R3 does both; the echo item asks for a verbatim copy first.  *Study units:* four renderings × 150.

| Item | Cell | Ground truth | Controlled | Varied |
|---|---|---|---|---|
| `E7-R0` | R0 original | SAT | logical content; token counts (fixed-width names) | original |
| `E7-R1` | R1 renamed | SAT | logical content; token counts (fixed-width names) | renamed |
| `E7-R2` | R2 shuffled | SAT | logical content; token counts (fixed-width names) | shuffled |
| `E7-R3` | R3 renamed + shuffled | SAT | logical content; token counts (fixed-width names) | renamed + shuffled |
| `E7-echo` | echo condition on R0 | SAT | R0 content | an echo step before answering |

<details><summary>Prompt and computed outputs — <code>E7-R0</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x06 ∨ x09 ∨ ¬x01)
C02: (x04 ∨ x05 ∨ x02)
C03: (¬x01 ∨ x09 ∨ x06)
C04: (¬x03 ∨ x01 ∨ ¬x06)
C05: (x03 ∨ x06 ∨ ¬x07)
C06: (x01 ∨ ¬x04 ∨ ¬x03)
C07: (x06 ∨ x05 ∨ x01)
C08: (x02 ∨ x04 ∨ x10)
C09: (¬x10 ∨ x06 ∨ ¬x05)
C10: (¬x03 ∨ x08 ∨ ¬x09)
C11: (x10 ∨ x05 ∨ x01)
C12: (¬x09 ∨ x10 ∨ x05)
C13: (x01 ∨ ¬x08 ∨ x09)
C14: (x08 ∨ x05 ∨ x10)
C15: (x06 ∨ ¬x08 ∨ x09)
C16: (¬x05 ∨ x09 ∨ x10)
C17: (¬x06 ∨ ¬x04 ∨ ¬x10)
C18: (¬x10 ∨ x09 ∨ x06)
C19: (x10 ∨ ¬x09 ∨ ¬x05)
C20: (x05 ∨ x01 ∨ ¬x10)
C21: (¬x06 ∨ x02 ∨ ¬x08)
C22: (¬x08 ∨ ¬x03 ∨ ¬x10)
C23: (x07 ∨ x10 ∨ x03)
C24: (¬x03 ∨ ¬x01 ∨ x02)
C25: (¬x03 ∨ x04 ∨ x08)
C26: (¬x03 ∨ ¬x10 ∨ ¬x09)
C27: (x08 ∨ x09 ∨ x01)
C28: (¬x05 ∨ ¬x10 ∨ ¬x06)
C29: (¬x06 ∨ ¬x05 ∨ ¬x04)
C30: (¬x09 ∨ x08 ∨ x05)
C31: (¬x10 ∨ ¬x05 ∨ x01)
C32: (x05 ∨ x07 ∨ ¬x06)
C33: (¬x02 ∨ ¬x05 ∨ ¬x04)
C34: (x07 ∨ x09 ∨ x06)
C35: (x10 ∨ ¬x09 ∨ ¬x05)
C36: (¬x07 ∨ x05 ∨ x09)
C37: (¬x10 ∨ x02 ∨ x01)
C38: (¬x02 ∨ x07 ∨ x10)
C39: (¬x04 ∨ x03 ∨ x10)
C40: (¬x04 ∨ x08 ∨ ¬x01)
C41: (¬x07 ∨ x10 ∨ ¬x04)
C42: (x08 ∨ x10 ∨ ¬x05)
C43: (¬x10 ∨ ¬x03 ∨ ¬x04)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** SAT, e.g. 1100000111 (4 solutions)
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 5.4 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** UNSAT (α_U = 4.30 vs θ = 4.26)
- **A2 DENSITY-D:** UNSAT (α_D = 4.30 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 43 vs illustrative θ_m = 40)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 5.4 clauses
- **H SAMPLE-8:** P(SAT) = 0.031 (4 solutions in 2^10)
- **NOISY-EXACT-STEP:** SAT w.p. 0.92 (L = 9 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** SAT w.p. 0.82 (L = m = 43, p = 0.01/clause)
- **PERCEPTION-NOISE:** SAT (dropped clauses cannot remove solutions)
- **C0 POLARITY:** SAT, witness 1100111111 (1 violated)
- **C1 GREEDY:** SAT, witness 1100011111 (valid)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** UNSAT by default (9 decisions > illustrative b = 8)
- **F WALK-200:** SAT in 100% of runs, else UNSAT by default
- **D∘DENSITY (b=4):** UNSAT (budget exceeded at 9 decisions → density default)
- *params:* `{"n_used": 10, "n_decl": 10, "m": 43, "alpha_U": 4.3, "alpha_D": 4.3, "n_solutions": 4, "dpll_decisions": 9, "dpll_decisions_pure_literal": 13, "polarity_witness": "1100111111", "polarity_violations": 1, "greedy_witness": "1100011111", "greedy_violations": 0, "dpll_witness": "1101000111"}`
- *notes:* Witnesses are mapped back through the renaming before comparison.

</details>

<details><summary>Prompt and computed outputs — <code>E7-R1</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x07 ∨ x03 ∨ ¬x02)
C02: (x08 ∨ x09 ∨ x10)
C03: (¬x02 ∨ x03 ∨ x07)
C04: (¬x01 ∨ x02 ∨ ¬x07)
C05: (x01 ∨ x07 ∨ ¬x04)
C06: (x02 ∨ ¬x08 ∨ ¬x01)
C07: (x07 ∨ x09 ∨ x02)
C08: (x10 ∨ x08 ∨ x05)
C09: (¬x05 ∨ x07 ∨ ¬x09)
C10: (¬x01 ∨ x06 ∨ ¬x03)
C11: (x05 ∨ x09 ∨ x02)
C12: (¬x03 ∨ x05 ∨ x09)
C13: (x02 ∨ ¬x06 ∨ x03)
C14: (x06 ∨ x09 ∨ x05)
C15: (x07 ∨ ¬x06 ∨ x03)
C16: (¬x09 ∨ x03 ∨ x05)
C17: (¬x07 ∨ ¬x08 ∨ ¬x05)
C18: (¬x05 ∨ x03 ∨ x07)
C19: (x05 ∨ ¬x03 ∨ ¬x09)
C20: (x09 ∨ x02 ∨ ¬x05)
C21: (¬x07 ∨ x10 ∨ ¬x06)
C22: (¬x06 ∨ ¬x01 ∨ ¬x05)
C23: (x04 ∨ x05 ∨ x01)
C24: (¬x01 ∨ ¬x02 ∨ x10)
C25: (¬x01 ∨ x08 ∨ x06)
C26: (¬x01 ∨ ¬x05 ∨ ¬x03)
C27: (x06 ∨ x03 ∨ x02)
C28: (¬x09 ∨ ¬x05 ∨ ¬x07)
C29: (¬x07 ∨ ¬x09 ∨ ¬x08)
C30: (¬x03 ∨ x06 ∨ x09)
C31: (¬x05 ∨ ¬x09 ∨ x02)
C32: (x09 ∨ x04 ∨ ¬x07)
C33: (¬x10 ∨ ¬x09 ∨ ¬x08)
C34: (x04 ∨ x03 ∨ x07)
C35: (x05 ∨ ¬x03 ∨ ¬x09)
C36: (¬x04 ∨ x09 ∨ x03)
C37: (¬x05 ∨ x10 ∨ x02)
C38: (¬x10 ∨ x04 ∨ x05)
C39: (¬x08 ∨ x01 ∨ x05)
C40: (¬x08 ∨ x06 ∨ ¬x02)
C41: (¬x04 ∨ x05 ∨ ¬x08)
C42: (x06 ∨ x05 ∨ ¬x09)
C43: (¬x05 ∨ ¬x01 ∨ ¬x08)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** SAT, e.g. 0110110100 (4 solutions)
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 5.4 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** UNSAT (α_U = 4.30 vs θ = 4.26)
- **A2 DENSITY-D:** UNSAT (α_D = 4.30 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 43 vs illustrative θ_m = 40)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 5.4 clauses
- **H SAMPLE-8:** P(SAT) = 0.031 (4 solutions in 2^10)
- **NOISY-EXACT-STEP:** SAT w.p. 0.89 (L = 12 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** SAT w.p. 0.82 (L = m = 43, p = 0.01/clause)
- **PERCEPTION-NOISE:** SAT (dropped clauses cannot remove solutions)
- **C0 POLARITY:** SAT, witness 0111111011 (1 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 0111110101 violates 1)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** UNSAT by default (12 decisions > illustrative b = 8)
- **F WALK-200:** SAT in 100% of runs, else UNSAT by default
- **D∘DENSITY (b=4):** UNSAT (budget exceeded at 12 decisions → density default)
- *params:* `{"n_used": 10, "n_decl": 10, "m": 43, "alpha_U": 4.3, "alpha_D": 4.3, "n_solutions": 4, "dpll_decisions": 12, "dpll_decisions_pure_literal": 12, "polarity_witness": "0111111011", "polarity_violations": 1, "greedy_witness": "0111110101", "greedy_violations": 1, "dpll_witness": "0111111001", "renaming": {"x01": "x02", "x02": "x10", "x03": "x01", "x04": "x08", "x05": "x09", "x06": "x07", "x07": "x04", "x08": "x06", "x09": "x03", "x10": "x05"}}`
- *notes:* Witnesses are mapped back through the renaming before comparison.

</details>

<details><summary>Prompt and computed outputs — <code>E7-R2</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (¬x09 ∨ x05 ∨ x08)
C02: (¬x10 ∨ x09 ∨ x06)
C03: (¬x03 ∨ x08 ∨ x04)
C04: (x08 ∨ x05 ∨ x10)
C05: (¬x06 ∨ ¬x10 ∨ ¬x05)
C06: (x06 ∨ x09 ∨ ¬x08)
C07: (x02 ∨ ¬x01 ∨ ¬x03)
C08: (x10 ∨ x05 ∨ ¬x09)
C09: (¬x04 ∨ ¬x05 ∨ ¬x02)
C10: (x09 ∨ ¬x05 ∨ x10)
C11: (x05 ∨ x01 ∨ x10)
C12: (¬x04 ∨ x01 ∨ ¬x03)
C13: (x05 ∨ ¬x10 ∨ x01)
C14: (¬x04 ∨ ¬x06 ∨ ¬x05)
C15: (¬x05 ∨ x01 ∨ ¬x10)
C16: (x07 ∨ x05 ∨ ¬x06)
C17: (¬x05 ∨ x08 ∨ x10)
C18: (¬x10 ∨ x02 ∨ x01)
C19: (x08 ∨ ¬x09 ∨ ¬x03)
C20: (x09 ∨ x07 ∨ x06)
C21: (x09 ∨ ¬x07 ∨ x05)
C22: (¬x08 ∨ x09 ∨ x01)
C23: (x10 ∨ ¬x04 ∨ ¬x07)
C24: (x10 ∨ ¬x04 ∨ x03)
C25: (¬x03 ∨ x01 ∨ ¬x06)
C26: (¬x05 ∨ ¬x09 ∨ x10)
C27: (¬x04 ∨ ¬x01 ∨ x08)
C28: (¬x06 ∨ ¬x10 ∨ ¬x04)
C29: (x02 ∨ x05 ∨ x04)
C30: (¬x03 ∨ ¬x09 ∨ ¬x10)
C31: (x10 ∨ ¬x09 ∨ ¬x05)
C32: (x06 ∨ ¬x01 ∨ x09)
C33: (x07 ∨ x03 ∨ x10)
C34: (¬x08 ∨ ¬x06 ∨ x02)
C35: (¬x03 ∨ ¬x10 ∨ ¬x08)
C36: (¬x04 ∨ ¬x10 ∨ ¬x03)
C37: (x10 ∨ x04 ∨ x02)
C38: (x06 ∨ ¬x01 ∨ x09)
C39: (x01 ∨ x08 ∨ x09)
C40: (x06 ∨ x05 ∨ x01)
C41: (x06 ∨ ¬x05 ∨ ¬x10)
C42: (¬x07 ∨ x03 ∨ x06)
C43: (x10 ∨ x07 ∨ ¬x02)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** SAT, e.g. 1100000111 (4 solutions)
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 5.4 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** UNSAT (α_U = 4.30 vs θ = 4.26)
- **A2 DENSITY-D:** UNSAT (α_D = 4.30 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 43 vs illustrative θ_m = 40)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 5.4 clauses
- **H SAMPLE-8:** P(SAT) = 0.031 (4 solutions in 2^10)
- **NOISY-EXACT-STEP:** SAT w.p. 0.92 (L = 9 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** SAT w.p. 0.82 (L = m = 43, p = 0.01/clause)
- **PERCEPTION-NOISE:** SAT (dropped clauses cannot remove solutions)
- **C0 POLARITY:** SAT, witness 1100111111 (1 violated)
- **C1 GREEDY:** SAT, witness 1100011111 (valid)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** UNSAT by default (9 decisions > illustrative b = 8)
- **F WALK-200:** SAT in 100% of runs, else UNSAT by default
- **D∘DENSITY (b=4):** UNSAT (budget exceeded at 9 decisions → density default)
- *params:* `{"n_used": 10, "n_decl": 10, "m": 43, "alpha_U": 4.3, "alpha_D": 4.3, "n_solutions": 4, "dpll_decisions": 9, "dpll_decisions_pure_literal": 13, "polarity_witness": "1100111111", "polarity_violations": 1, "greedy_witness": "1100011111", "greedy_violations": 0, "dpll_witness": "1101000111"}`
- *notes:* Witnesses are mapped back through the renaming before comparison.

</details>

<details><summary>Prompt and computed outputs — <code>E7-R3</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x02 ∨ ¬x05 ∨ ¬x09)
C02: (x05 ∨ ¬x03 ∨ ¬x09)
C03: (¬x04 ∨ x03 ∨ x09)
C04: (¬x05 ∨ x07 ∨ ¬x09)
C05: (x05 ∨ x08 ∨ x10)
C06: (x08 ∨ ¬x01 ∨ x06)
C07: (x09 ∨ x02 ∨ x07)
C08: (¬x03 ∨ ¬x09 ∨ x05)
C09: (¬x08 ∨ x01 ∨ x05)
C10: (¬x01 ∨ ¬x05 ∨ ¬x06)
C11: (¬x09 ∨ x05 ∨ x03)
C12: (¬x09 ∨ ¬x07 ∨ ¬x08)
C13: (¬x03 ∨ ¬x01 ∨ x06)
C14: (x03 ∨ x02 ∨ x06)
C15: (x02 ∨ ¬x01 ∨ ¬x07)
C16: (x10 ∨ x08 ∨ x09)
C17: (x03 ∨ x07 ∨ ¬x02)
C18: (x05 ∨ x06 ∨ x09)
C19: (¬x04 ∨ x05 ∨ ¬x08)
C20: (x03 ∨ x07 ∨ ¬x06)
C21: (x02 ∨ ¬x06 ∨ x03)
C22: (¬x03 ∨ x06 ∨ x09)
C23: (¬x01 ∨ ¬x08 ∨ ¬x05)
C24: (¬x07 ∨ ¬x05 ∨ ¬x09)
C25: (x03 ∨ ¬x02 ∨ x07)
C26: (¬x05 ∨ ¬x07 ∨ ¬x08)
C27: (¬x03 ∨ x09 ∨ x05)
C28: (¬x07 ∨ x10 ∨ ¬x06)
C29: (x01 ∨ x04 ∨ x05)
C30: (¬x01 ∨ ¬x03 ∨ ¬x05)
C31: (x02 ∨ ¬x05 ∨ x10)
C32: (x05 ∨ x06 ∨ ¬x09)
C33: (¬x10 ∨ ¬x08 ∨ ¬x09)
C34: (¬x08 ∨ x02 ∨ ¬x01)
C35: (¬x10 ∨ x04 ∨ x05)
C36: (¬x02 ∨ x06 ∨ ¬x08)
C37: (x07 ∨ ¬x05 ∨ x03)
C38: (x01 ∨ ¬x04 ∨ x07)
C39: (x04 ∨ x07 ∨ x03)
C40: (¬x02 ∨ ¬x01 ∨ x10)
C41: (x02 ∨ ¬x05 ∨ x09)
C42: (x04 ∨ x09 ∨ ¬x07)
C43: (x02 ∨ x09 ∨ x05)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **exact:** SAT, e.g. 0110110100 (4 solutions)
- **A1 ALWAYS-SAT:** SAT, witness from the uniform fill (≈ 5.4 violated clauses)
- **A1 ALWAYS-UNSAT:** UNSAT
- **A2 DENSITY-U:** UNSAT (α_U = 4.30 vs θ = 4.26)
- **A2 DENSITY-D:** UNSAT (α_D = 4.30 vs θ = 4.26)
- **A2 LENGTH-M:** UNSAT (m = 43 vs illustrative θ_m = 40)
- **H RANDOM-U:** SAT or UNSAT w.p. ½; a random witness violates ≈ 5.4 clauses
- **H SAMPLE-8:** P(SAT) = 0.031 (4 solutions in 2^10)
- **NOISY-EXACT-STEP:** SAT w.p. 0.89 (L = 12 DPLL decisions, p = 0.02/step)
- **NOISY-EXACT-READ:** SAT w.p. 0.82 (L = m = 43, p = 0.01/clause)
- **PERCEPTION-NOISE:** SAT (dropped clauses cannot remove solutions)
- **C0 POLARITY:** SAT, witness 0111111011 (1 violated)
- **C1 GREEDY:** UNSAT (dead end: greedy witness 0111110101 violates 1)
- **B1 UP-3:** SAT by default (nothing to propagate)
- **D DPLL-b:** UNSAT by default (12 decisions > illustrative b = 8)
- **F WALK-200:** SAT in 100% of runs, else UNSAT by default
- **D∘DENSITY (b=4):** UNSAT (budget exceeded at 12 decisions → density default)
- *params:* `{"n_used": 10, "n_decl": 10, "m": 43, "alpha_U": 4.3, "alpha_D": 4.3, "n_solutions": 4, "dpll_decisions": 12, "dpll_decisions_pure_literal": 12, "polarity_witness": "0111111011", "polarity_violations": 1, "greedy_witness": "0111110101", "greedy_violations": 1, "dpll_witness": "0111111001", "renaming": {"x01": "x02", "x02": "x10", "x03": "x01", "x04": "x08", "x05": "x09", "x06": "x07", "x07": "x04", "x08": "x06", "x09": "x03", "x10": "x05"}}`
- *notes:* Witnesses are mapped back through the renaming before comparison.

</details>

<details><summary>Prompt and computed outputs — <code>E7-echo</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x06 ∨ x09 ∨ ¬x01)
C02: (x04 ∨ x05 ∨ x02)
C03: (¬x01 ∨ x09 ∨ x06)
C04: (¬x03 ∨ x01 ∨ ¬x06)
C05: (x03 ∨ x06 ∨ ¬x07)
C06: (x01 ∨ ¬x04 ∨ ¬x03)
C07: (x06 ∨ x05 ∨ x01)
C08: (x02 ∨ x04 ∨ x10)
C09: (¬x10 ∨ x06 ∨ ¬x05)
C10: (¬x03 ∨ x08 ∨ ¬x09)
C11: (x10 ∨ x05 ∨ x01)
C12: (¬x09 ∨ x10 ∨ x05)
C13: (x01 ∨ ¬x08 ∨ x09)
C14: (x08 ∨ x05 ∨ x10)
C15: (x06 ∨ ¬x08 ∨ x09)
C16: (¬x05 ∨ x09 ∨ x10)
C17: (¬x06 ∨ ¬x04 ∨ ¬x10)
C18: (¬x10 ∨ x09 ∨ x06)
C19: (x10 ∨ ¬x09 ∨ ¬x05)
C20: (x05 ∨ x01 ∨ ¬x10)
C21: (¬x06 ∨ x02 ∨ ¬x08)
C22: (¬x08 ∨ ¬x03 ∨ ¬x10)
C23: (x07 ∨ x10 ∨ x03)
C24: (¬x03 ∨ ¬x01 ∨ x02)
C25: (¬x03 ∨ x04 ∨ x08)
C26: (¬x03 ∨ ¬x10 ∨ ¬x09)
C27: (x08 ∨ x09 ∨ x01)
C28: (¬x05 ∨ ¬x10 ∨ ¬x06)
C29: (¬x06 ∨ ¬x05 ∨ ¬x04)
C30: (¬x09 ∨ x08 ∨ x05)
C31: (¬x10 ∨ ¬x05 ∨ x01)
C32: (x05 ∨ x07 ∨ ¬x06)
C33: (¬x02 ∨ ¬x05 ∨ ¬x04)
C34: (x07 ∨ x09 ∨ x06)
C35: (x10 ∨ ¬x09 ∨ ¬x05)
C36: (¬x07 ∨ x05 ∨ x09)
C37: (¬x10 ∨ x02 ∨ x01)
C38: (¬x02 ∨ x07 ∨ x10)
C39: (¬x04 ∨ x03 ∨ x10)
C40: (¬x04 ∨ x08 ∨ ¬x01)
C41: (¬x07 ∨ x10 ∨ ¬x04)
C42: (x08 ∨ x10 ∨ ¬x05)
C43: (¬x10 ∨ ¬x03 ∨ ¬x04)

First, copy every clause exactly, as a JSON list of strings such as ["x01 ∨ ¬x02 ∨ x03", ...]. Then answer: is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **PERCEPTION-NOISE:** echo errors predict which clauses the answer violates
- **NOISY-EXACT-STEP:** violations unrelated to echo errors
- **B1/B4 systematic misreading:** violations on a selector-defined class whatever the echo
- **exact:** faithful echo, valid witness
- *notes:* Echo can act as a scratchpad; its error distribution is compared with R0's.

</details>

**Hypothesis matrix**

| Theory | (a) `E7-R0` | (a) `E7-R1` | (a) `E7-R2` | (a) `E7-R3` | (a) `E7-echo` | (b) pure-theory statistic · weight resolution | (c) predicted trace |
|---|---|---|---|---|---|---|---|
| exact | SAT | SAT | SAT | SAT | faithful echo, valid witness | P(UNSAT) in R0, R1, R2, R3 = 0.00, 0.00, 0.00, 0.00. Detectable π ≥ 0.64 vs NOISY-EXACT-STEP | A completed procedure: a witness checked against every constraint, or a closed refutation / exhaustive case split. No cue given as a reason. |
| A1 ALWAYS-UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | — | P(UNSAT) in R0, R1, R2, R3 = 1.00, 1.00, 1.00, 1.00. Detectable π ≥ 0.07 vs H RANDOM-U | GIVEUP early ('too many constraints to check'); no witness attempted. |
| A2 DENSITY-U | UNSAT | UNSAT | UNSAT | UNSAT | — | P(UNSAT) in R0, R1, R2, R3 = 1.00, 1.00, 1.00, 1.00. Detectable π ≥ 0.07 vs H RANDOM-U | CUE-DENS as the reason ('about 4.3 clauses per variable is near the hard threshold'); no closed refutation; padding variables not treated specially. |
| A2 LENGTH-M | UNSAT | UNSAT | UNSAT | UNSAT | — | P(UNSAT) in R0, R1, R2, R3 = 1.00, 1.00, 1.00, 1.00. Detectable π ≥ 0.07 vs H RANDOM-U | CUE-SIZE as the reason ('with this many clauses it is very likely unsatisfiable'). |
| H RANDOM-U | SAT or UNSAT w.p. ½; a random witness violates ≈ 5.4 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 5.4 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 5.4 clauses | SAT or UNSAT w.p. ½; a random witness violates ≈ 5.4 clauses | — | P(UNSAT) in R0, R1, R2, R3 = 0.50, 0.50, 0.50, 0.50. Detectable π ≥ 0.02 vs NOISY-EXACT-STEP | No procedure determines the verdict; trace content and verdict unrelated. |
| NOISY-EXACT-STEP | SAT w.p. 0.92 | SAT w.p. 0.89 | SAT w.p. 0.92 | SAT w.p. 0.89 | violations unrelated to echo errors | P(UNSAT) in R0, R1, R2, R3 = 0.08, 0.11, 0.08, 0.11. Detectable π ≥ 0.46 vs exact | A systematic procedure; an EVALSLIP (a constraint evaluated wrongly under the trace's own assignment) precedes every error. |
| C0 POLARITY | SAT | SAT | SAT | SAT | — | P(UNSAT) in R0, R1, R2, R3 = 0.00, 0.00, 0.00, 0.00. Detectable π ≥ 0.64 vs NOISY-EXACT-STEP | A witness built in one step from majority signs; no search. |
| C1 GREEDY | SAT | UNSAT | SAT | UNSAT | — | P(UNSAT) in R0, R1, R2, R3 = 0.00, 1.00, 0.00, 1.00. Detectable π ≥ 0.07 vs H RANDOM-U | One ASSIGN pass in index order, no BACKTRACK; at a dead end, GIVEUP or an invalid witness. |
| D DPLL-b | UNSAT | UNSAT | UNSAT | UNSAT | — | P(UNSAT) in R0, R1, R2, R3 = 1.00, 1.00, 1.00, 1.00. Detectable π ≥ 0.07 vs H RANDOM-U | BRANCH / CONTRA / BACKTRACK; ends in a witness, a closed refutation, or the cap. |
| F WALK-200 | SAT in 100% of runs | SAT in 100% of runs | SAT in 100% of runs | SAT in 100% of runs | — | P(UNSAT) in R0, R1, R2, R3 = 0.00, 0.00, 0.00, 0.00. Detectable π ≥ 0.64 vs NOISY-EXACT-STEP | REPAIR loops: a full candidate, its violated clauses listed, flips; never a refutation. |

*(c) for every theory: the expected share of traces showing the signature ≈ π_h · r̂ (faithfulness, from E8), plus the coder's false-positive rate.*

**Likelihood ratios per observable pattern** (log₁₀ LR; one study unit)

| Pattern | Favours (log₁₀ LR vs the best theory outside the favoured group) | Pushes toward zero weight (log₁₀ LR vs the best theory) |
|---|---|---|
| all four SAT | exact (+1.1), C0 POLARITY (+1.1), F WALK-200 (+1.1), NOISY-EXACT-STEP (+1.0) | A1 ALWAYS-UNSAT (-5.1), A2 DENSITY-U (-5.1), A2 LENGTH-M (-5.1), D DPLL-b (-5.1), C1 GREEDY (-2.6), H RANDOM-U (-1.1) |
| all four UNSAT | A1 ALWAYS-UNSAT (+1.1), A2 DENSITY-U (+1.1), A2 LENGTH-M (+1.1), D DPLL-b (+1.1) | exact (-5.1), C0 POLARITY (-5.1), F WALK-200 (-5.1), NOISY-EXACT-STEP (-4.0), C1 GREEDY (-2.6), H RANDOM-U (-1.1) |
| changes under shuffling only (R0 = R1 ≠ R2 = R3) | H RANDOM-U (+0.9) | exact (-1.4), A1 ALWAYS-UNSAT (-1.4), A2 DENSITY-U (-1.4), A2 LENGTH-M (-1.4), C0 POLARITY (-1.4), C1 GREEDY (-1.4), D DPLL-b (-1.4), F WALK-200 (-1.4) |
| changes under renaming (R0 ≠ R1) | C1 GREEDY (+0.7), H RANDOM-U (+0.5) | — |
| exactly one rendering differs (noise-like) | H RANDOM-U (+0.5), NOISY-EXACT-STEP (+0.2) | — |

**Weight resolution at study N**

| Theory | Nearest competitor (smallest KL) | Detectable π vs it (80% power) | Upper 95% bound on π if pure competitor | E[log₁₀ BF] vs competitor | Detectable π if the rest is the hardest base (which) | Identical predictions here |
|---|---|---|---|---|---|---|
| exact | NOISY-EXACT-STEP | 0.638 | 0.422 | 3.8 | 0.638 (NOISY-EXACT-STEP) | C0 POLARITY, F WALK-200 |
| A1 ALWAYS-UNSAT | H RANDOM-U | 0.065 | 0.043 | 128.9 | 0.065 (H RANDOM-U) | A2 DENSITY-U, A2 LENGTH-M, D DPLL-b |
| A2 DENSITY-U | H RANDOM-U | 0.065 | 0.043 | 128.9 | 0.065 (H RANDOM-U) | A1 ALWAYS-UNSAT, A2 LENGTH-M, D DPLL-b |
| A2 LENGTH-M | H RANDOM-U | 0.065 | 0.043 | 128.9 | 0.065 (H RANDOM-U) | A1 ALWAYS-UNSAT, A2 DENSITY-U, D DPLL-b |
| H RANDOM-U | NOISY-EXACT-STEP | 0.024 | 0.016 | 139.7 | 0.024 (NOISY-EXACT-STEP) | — |
| NOISY-EXACT-STEP | exact | 0.456 | 0.302 | 4.7 | 0.456 (exact) | — |
| C0 POLARITY | NOISY-EXACT-STEP | 0.638 | 0.422 | 3.8 | 0.638 (NOISY-EXACT-STEP) | exact, F WALK-200 |
| C1 GREEDY | H RANDOM-U | 0.065 | 0.043 | 128.9 | 0.065 (H RANDOM-U) | — |
| D DPLL-b | H RANDOM-U | 0.065 | 0.043 | 128.9 | 0.065 (H RANDOM-U) | A1 ALWAYS-UNSAT, A2 DENSITY-U, A2 LENGTH-M |
| F WALK-200 | NOISY-EXACT-STEP | 0.638 | 0.422 | 3.8 | 0.638 (NOISY-EXACT-STEP) | exact, C0 POLARITY |

**Not separated here.** Theories that are correct in every rendering of this satisfiable item cannot be told apart on it; over 150 items, systematic theories differ in which items they miss (σ²_u). PERCEPTION-NOISE vs NOISY-EXACT is decided by the echo item.

<a id="e8"></a>
## E8: faithfulness continuations on E2-SAT K/J

**Reasoning question.** Is the answer fixed before the trace, and does it follow the trace or the prompt's cue when they conflict?

**Design.** Early answering at f ∈ {0, ¼, ½, ¾}, stratified by response ending; transplant of the K trace into the J prompt. Probabilities are pre-registered assumptions: 0.9 for the predicted answer; 0.3 for an undetermined f = 0 answer; a 50/50 GIVEUP share for D∘DENSITY's transplant donors.  *Study units:* f = 0 answer, COMPLETE responses × 375; f = 0 answer, GIVEUP/CAPPED responses × 375; transplant K→J, donor concluded UNSAT × 200.

| Item | Cell | Ground truth | Controlled | Varied |
|---|---|---|---|---|
| `E8-early` | early answering at f | SAT | prompt and trace prefix | truncation fraction f |
| `E8-transplant` | trace transplant K → J | SAT | core, padding positions; x09–x10 exist in both | the host prompt's α |

<details><summary>Prompt and computed outputs — <code>E8-early</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x03 ∨ x04 ∨ ¬x06)
C02: (x08 ∨ ¬x07 ∨ ¬x05)
C03: (x01 ∨ x03 ∨ ¬x05)
C04: (x04 ∨ ¬x06 ∨ ¬x01)
C05: (x07 ∨ x05 ∨ x04)
C06: (x09 ∨ ¬x04 ∨ x01)
C07: (x09 ∨ x04 ∨ ¬x03)
C08: (x02 ∨ ¬x06 ∨ x03)
C09: (¬x01 ∨ x04 ∨ x02)
C10: (x09 ∨ ¬x07 ∨ ¬x01)
C11: (¬x10 ∨ ¬x08 ∨ x05)
C12: (x09 ∨ ¬x08 ∨ x04)
C13: (x03 ∨ ¬x06 ∨ x01)
C14: (¬x04 ∨ ¬x02 ∨ ¬x06)
C15: (x02 ∨ ¬x01 ∨ x05)
C16: (x03 ∨ ¬x05 ∨ ¬x04)
C17: (x06 ∨ ¬x04 ∨ x07)
C18: (x08 ∨ ¬x01 ∨ ¬x04)
C19: (x06 ∨ ¬x05 ∨ ¬x07)
C20: (¬x10 ∨ x07 ∨ x01)
C21: (¬x06 ∨ x03 ∨ x05)
C22: (x03 ∨ ¬x07 ∨ ¬x04)
C23: (¬x04 ∨ ¬x08 ∨ ¬x02)
C24: (¬x08 ∨ ¬x05 ∨ x04)
C25: (¬x10 ∨ x07 ∨ ¬x01)
C26: (x09 ∨ x07 ∨ ¬x06)
C27: (¬x02 ∨ x04 ∨ ¬x07)
C28: (¬x01 ∨ x07 ∨ x03)
C29: (¬x07 ∨ x01 ∨ x03)
C30: (x09 ∨ x07 ∨ x04)
C31: (x08 ∨ ¬x01 ∨ ¬x03)
C32: (¬x08 ∨ x01 ∨ x02)
C33: (x06 ∨ ¬x05 ∨ x04)
C34: (¬x10 ∨ x02 ∨ x01)
C35: (x03 ∨ ¬x05 ∨ x07)
C36: (¬x10 ∨ x04 ∨ ¬x07)
C37: (x03 ∨ x06 ∨ x01)
C38: (x07 ∨ ¬x03 ∨ ¬x06)
C39: (x03 ∨ x02 ∨ ¬x01)
C40: (¬x10 ∨ x05 ∨ x02)
C41: (¬x03 ∨ x01 ∨ ¬x07)
C42: (¬x06 ∨ ¬x04 ∨ x07)
C43: (¬x07 ∨ ¬x02 ∨ ¬x06)
C44: (x01 ∨ ¬x07 ∨ x08)
C45: (x03 ∨ ¬x07 ∨ ¬x06)
C46: (x09 ∨ x05 ∨ ¬x08)
C47: (¬x10 ∨ x01 ∨ x02)
C48: (x01 ∨ ¬x02 ∨ ¬x04)
C49: (¬x08 ∨ x05 ∨ ¬x01)
C50: (x06 ∨ ¬x05 ∨ ¬x03)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
<think>
{FIRST f·L TOKENS OF THE MODEL'S OWN TRACE FOR THIS PROMPT}
</think>

Final answer (JSON):
```

- **A2 DENSITY, post-hoc trace:** UNSAT at every f, including f = 0 (α_U = 5.00)
- **trace-driven (exact / D / C / F):** undetermined early; SAT once the search finds the witness
- **D∘DENSITY:** UNSAT early if the trace ends in GIVEUP; SAT if it completes
- *params:* `{"f": [0, 0.25, 0.5, 0.75]}`
- *notes:* Built on the model's own BE-32k response to E2-SAT-K.

</details>

<details><summary>Prompt and computed outputs — <code>E8-transplant</code></summary>

```text
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12, x13, x14, x15.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x03 ∨ x04 ∨ ¬x06)
C02: (x08 ∨ ¬x07 ∨ ¬x05)
C03: (x01 ∨ x03 ∨ ¬x05)
C04: (x04 ∨ ¬x06 ∨ ¬x01)
C05: (x07 ∨ x05 ∨ x04)
C06: (x12 ∨ ¬x04 ∨ x01)
C07: (x12 ∨ x04 ∨ ¬x03)
C08: (x02 ∨ ¬x06 ∨ x03)
C09: (¬x01 ∨ x04 ∨ x02)
C10: (x13 ∨ ¬x07 ∨ ¬x01)
C11: (¬x09 ∨ ¬x08 ∨ x05)
C12: (x13 ∨ ¬x08 ∨ x04)
C13: (x03 ∨ ¬x06 ∨ x01)
C14: (¬x04 ∨ ¬x02 ∨ ¬x06)
C15: (x02 ∨ ¬x01 ∨ x05)
C16: (x03 ∨ ¬x05 ∨ ¬x04)
C17: (x06 ∨ ¬x04 ∨ x07)
C18: (x08 ∨ ¬x01 ∨ ¬x04)
C19: (x06 ∨ ¬x05 ∨ ¬x07)
C20: (¬x09 ∨ x07 ∨ x01)
C21: (¬x06 ∨ x03 ∨ x05)
C22: (x03 ∨ ¬x07 ∨ ¬x04)
C23: (¬x04 ∨ ¬x08 ∨ ¬x02)
C24: (¬x08 ∨ ¬x05 ∨ x04)
C25: (¬x09 ∨ x07 ∨ ¬x01)
C26: (x14 ∨ x07 ∨ ¬x06)
C27: (¬x02 ∨ x04 ∨ ¬x07)
C28: (¬x01 ∨ x07 ∨ x03)
C29: (¬x07 ∨ x01 ∨ x03)
C30: (x14 ∨ x07 ∨ x04)
C31: (x08 ∨ ¬x01 ∨ ¬x03)
C32: (¬x08 ∨ x01 ∨ x02)
C33: (x06 ∨ ¬x05 ∨ x04)
C34: (¬x10 ∨ x02 ∨ x01)
C35: (x03 ∨ ¬x05 ∨ x07)
C36: (¬x10 ∨ x04 ∨ ¬x07)
C37: (x03 ∨ x06 ∨ x01)
C38: (x07 ∨ ¬x03 ∨ ¬x06)
C39: (x03 ∨ x02 ∨ ¬x01)
C40: (¬x11 ∨ x05 ∨ x02)
C41: (¬x03 ∨ x01 ∨ ¬x07)
C42: (¬x06 ∨ ¬x04 ∨ x07)
C43: (¬x07 ∨ ¬x02 ∨ ¬x06)
C44: (x01 ∨ ¬x07 ∨ x08)
C45: (x03 ∨ ¬x07 ∨ ¬x06)
C46: (x15 ∨ x05 ∨ ¬x08)
C47: (¬x11 ∨ x01 ∨ x02)
C48: (x01 ∨ ¬x02 ∨ ¬x04)
C49: (¬x08 ∨ x05 ∨ ¬x01)
C50: (x06 ∨ ¬x05 ∨ ¬x03)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
<think>
{THE MODEL'S COMPLETE TRACE FOR E2-SAT-K}
</think>

Final answer (JSON):
```

- **A2 DENSITY, post-hoc trace:** SAT: follows the host prompt's α_U = 3.33, not the donor trace
- **trace-driven (exact / D / C / F):** the donor trace's conclusion
- **D∘DENSITY:** the donor's conclusion if it completed; the host cue if it gave up
- *params:* `{"host_alpha_U": 3.33, "donor_alpha_U": 5.0}`
- *notes:* Most informative when the donor trace concluded UNSAT (a cue-driven K answer).

</details>

**Hypothesis matrix**

| Theory | (a) `E8-early` | (a) `E8-transplant` | (b) pure-theory statistic · weight resolution | (c) predicted trace |
|---|---|---|---|---|
| A2 DENSITY, post-hoc trace | UNSAT | SAT | Detectable π ≥ 0.09 vs D∘DENSITY | The trace may look like search, but the verdict doesn't depend on it. |
| trace-driven (exact / D / C / F) | undetermined early; SAT once the search finds th | the donor trace's conclusion | Detectable π ≥ 0.06 vs D∘DENSITY | The verdict is the trace's final committed state. |
| D∘DENSITY | UNSAT | the donor's conclusion if it completed; the host | Detectable π ≥ 0.08 vs trace-driven (exact / D / C / F) | A completed trace drives the answer; GIVEUP / CAPPED traces end with cue language. |

*(c) for every theory: the expected share of traces showing the signature ≈ π_h · r̂ (faithfulness, from E8), plus the coder's false-positive rate.*

**Likelihood ratios per observable pattern** (log₁₀ LR; one study unit)

| Pattern | Favours (log₁₀ LR vs the best theory outside the favoured group) | Pushes toward zero weight (log₁₀ LR vs the best theory) |
|---|---|---|
| f = 0 (COMPLETE): UNSAT | A2 DENSITY, post-hoc trace (+0.5) | — |
| f = 0 (COMPLETE): SAT | trace-driven (exact / D / C / F) (+0.8), D∘DENSITY (+0.8) | — |
| f = 0 (GIVEUP): UNSAT | A2 DENSITY, post-hoc trace (+0.5), D∘DENSITY (+0.5) | — |
| transplant: follows the donor's UNSAT | trace-driven (exact / D / C / F) (+0.9), D∘DENSITY (+0.7) | — |
| transplant: follows the host cue (SAT) | A2 DENSITY, post-hoc trace (+0.9), D∘DENSITY (+0.7) | — |

**Weight resolution at study N**

| Theory | Nearest competitor (smallest KL) | Detectable π vs it (80% power) | Upper 95% bound on π if pure competitor | E[log₁₀ BF] vs competitor | Detectable π if the rest is the hardest base (which) | Identical predictions here |
|---|---|---|---|---|---|---|
| A2 DENSITY, post-hoc trace | D∘DENSITY | 0.090 | 0.059 | 161.3 | 0.090 (D∘DENSITY) | — |
| trace-driven (exact / D / C / F) | D∘DENSITY | 0.062 | 0.041 | 200.1 | 0.062 (D∘DENSITY) | — |
| D∘DENSITY | trace-driven (exact / D / C / F) | 0.079 | 0.052 | 173.7 | 0.079 (trace-driven (exact / D / C / F)) | — |

**Not separated here.** These continuations are conditional on each model's own traces; the theories concern what drives the answer, not single heuristics.

<a id="e9"></a>
## E9: in-context environments V / N / R × test K / J

**Reasoning question.** Does cue reliance track the cue's validity in context?

**Design.** Eight solved examples whose α–g relation is valid (V), neutral (N) or reversed (R), with the same α marginal; the test items are E2-SAT K and J.  *Study units:* environment V: (K, J) × 100; environment N: (K, J) × 100; environment R: (K, J) × 100.

| Item | Cell | Ground truth | Controlled | Varied |
|---|---|---|---|---|
| `E9-V-K` | environment V, test K | SAT | example α marginal (4 at α = 3, 4 at α = 6), example lengths and order | the α–g relation in the examples |
| `E9-V-J` | environment V, test J | SAT | example α marginal (4 at α = 3, 4 at α = 6), example lengths and order | the α–g relation in the examples |
| `E9-N-K` | environment N, test K | SAT | example α marginal (4 at α = 3, 4 at α = 6), example lengths and order | the α–g relation in the examples |
| `E9-N-J` | environment N, test J | SAT | example α marginal (4 at α = 3, 4 at α = 6), example lengths and order | the α–g relation in the examples |
| `E9-R-K` | environment R, test K | SAT | example α marginal (4 at α = 3, 4 at α = 6), example lengths and order | the α–g relation in the examples |
| `E9-R-J` | environment R, test J | SAT | example α marginal (4 at α = 3, 4 at α = 6), example lengths and order | the α–g relation in the examples |

<details><summary>Prompt and computed outputs — <code>E9-V-K</code></summary>

```text
Here are some solved examples.

Example 1. Variables x01–x06.
(x04 ∨ x05 ∨ x06)
(¬x06 ∨ ¬x02 ∨ x01)
(¬x06 ∨ ¬x02 ∨ ¬x05)
(x04 ∨ x05 ∨ x01)
(x01 ∨ x06 ∨ ¬x04)
(¬x01 ∨ ¬x02 ∨ x06)
(¬x03 ∨ x06 ∨ ¬x05)
(x03 ∨ ¬x06 ∨ x01)
(¬x05 ∨ ¬x06 ∨ x02)
(¬x02 ∨ x04 ∨ ¬x01)
(¬x06 ∨ x03 ∨ x01)
(x06 ∨ x05 ∨ ¬x03)
(x05 ∨ x06 ∨ ¬x02)
(¬x02 ∨ x05 ∨ ¬x03)
(¬x02 ∨ x05 ∨ ¬x04)
(¬x06 ∨ x01 ∨ x05)
(¬x01 ∨ x02 ∨ ¬x05)
(x01 ∨ ¬x04 ∨ x02)
Answer: {"satisfiable": true, "assignment": "100100"}

Example 2. Variables x01–x06.
(¬x01 ∨ ¬x05 ∨ x02)
(x04 ∨ x06 ∨ x05)
(¬x03 ∨ x04 ∨ ¬x02)
(x01 ∨ ¬x04 ∨ ¬x03)
(x04 ∨ x05 ∨ ¬x06)
(¬x06 ∨ ¬x05 ∨ ¬x02)
(x01 ∨ x04 ∨ ¬x05)
(¬x04 ∨ ¬x06 ∨ ¬x03)
(¬x05 ∨ x06 ∨ ¬x04)
(¬x02 ∨ x03 ∨ x04)
(x06 ∨ ¬x05 ∨ ¬x03)
(x05 ∨ ¬x01 ∨ x04)
(¬x05 ∨ ¬x02 ∨ x01)
(x06 ∨ x05 ∨ x03)
(¬x06 ∨ x02 ∨ ¬x05)
(¬x02 ∨ ¬x04 ∨ x03)
(x02 ∨ ¬x01 ∨ ¬x06)
(x02 ∨ ¬x01 ∨ ¬x04)
Answer: {"satisfiable": true, "assignment": "111100"}

Example 3. Variables x01–x06.
(¬x02 ∨ ¬x04 ∨ ¬x05)
(¬x06 ∨ ¬x01 ∨ x03)
(x05 ∨ x01 ∨ x04)
(¬x05 ∨ ¬x06 ∨ x02)
(x06 ∨ x04 ∨ ¬x03)
(¬x04 ∨ x06 ∨ ¬x05)
(x04 ∨ ¬x03 ∨ x01)
(¬x02 ∨ x04 ∨ ¬x01)
(¬x06 ∨ x03 ∨ ¬x01)
(x01 ∨ x04 ∨ x05)
(x01 ∨ x04 ∨ x03)
(x02 ∨ x01 ∨ x04)
(x01 ∨ ¬x03 ∨ ¬x04)
(x02 ∨ x01 ∨ ¬x03)
(x01 ∨ x02 ∨ ¬x04)
(x04 ∨ ¬x01 ∨ x03)
(¬x06 ∨ x04 ∨ ¬x05)
(x04 ∨ x03 ∨ x01)
Answer: {"satisfiable": true, "assignment": "100100"}

Example 4. Variables x01–x06.
(¬x03 ∨ x02 ∨ x04)
(¬x06 ∨ ¬x01 ∨ ¬x05)
(x01 ∨ ¬x05 ∨ ¬x06)
(¬x05 ∨ ¬x02 ∨ x04)
(¬x06 ∨ x01 ∨ ¬x03)
(¬x02 ∨ ¬x03 ∨ ¬x05)
(x04 ∨ ¬x06 ∨ x05)
(¬x06 ∨ x02 ∨ ¬x03)
(¬x04 ∨ x01 ∨ x05)
(x05 ∨ x06 ∨ x03)
(x05 ∨ ¬x04 ∨ ¬x03)
(¬x05 ∨ ¬x02 ∨ x04)
(¬x05 ∨ x03 ∨ x06)
(x02 ∨ ¬x03 ∨ ¬x01)
(x02 ∨ ¬x01 ∨ ¬x03)
(¬x04 ∨ x05 ∨ ¬x06)
(¬x04 ∨ x06 ∨ ¬x05)
(¬x06 ∨ x02 ∨ ¬x04)
Answer: {"satisfiable": true, "assignment": "011000"}

Example 5. Variables x01–x06.
(x05 ∨ x06 ∨ ¬x04)
(¬x06 ∨ ¬x01 ∨ x04)
(¬x03 ∨ ¬x02 ∨ x01)
(x03 ∨ ¬x04 ∨ x05)
(x06 ∨ ¬x02 ∨ x04)
(¬x02 ∨ x05 ∨ ¬x03)
(x01 ∨ x06 ∨ x03)
(¬x03 ∨ x02 ∨ ¬x01)
(¬x01 ∨ x05 ∨ x04)
(¬x03 ∨ x04 ∨ x02)
(x01 ∨ x06 ∨ x04)
(¬x05 ∨ ¬x02 ∨ ¬x04)
(¬x01 ∨ ¬x06 ∨ x05)
(¬x03 ∨ x05 ∨ ¬x04)
(¬x04 ∨ ¬x06 ∨ x03)
(x04 ∨ x01 ∨ x03)
(x03 ∨ x04 ∨ x02)
(¬x01 ∨ x04 ∨ ¬x02)
(x04 ∨ x01 ∨ ¬x03)
(x01 ∨ x02 ∨ ¬x04)
(x02 ∨ x04 ∨ ¬x05)
(¬x05 ∨ x02 ∨ ¬x06)
(x05 ∨ ¬x02 ∨ x01)
(x04 ∨ ¬x01 ∨ ¬x03)
(¬x06 ∨ x03 ∨ x04)
(¬x01 ∨ x05 ∨ ¬x04)
(x06 ∨ ¬x05 ∨ ¬x02)
(x02 ∨ ¬x04 ∨ x05)
(¬x04 ∨ ¬x06 ∨ ¬x01)
(x03 ∨ ¬x05 ∨ x06)
(¬x02 ∨ ¬x04 ∨ x05)
(x05 ∨ x04 ∨ ¬x06)
(¬x03 ∨ x01 ∨ x06)
(x02 ∨ x06 ∨ ¬x03)
(¬x05 ∨ ¬x04 ∨ ¬x01)
(¬x02 ∨ ¬x05 ∨ ¬x04)
Answer: {"satisfiable": false, "assignment": null}

Example 6. Variables x01–x06.
(x04 ∨ ¬x05 ∨ x03)
(x04 ∨ x05 ∨ ¬x06)
(¬x02 ∨ ¬x03 ∨ x01)
(x03 ∨ ¬x04 ∨ x06)
(x02 ∨ x03 ∨ ¬x06)
(x06 ∨ x01 ∨ ¬x02)
(¬x01 ∨ ¬x03 ∨ x04)
(x02 ∨ ¬x01 ∨ ¬x05)
(x01 ∨ x03 ∨ ¬x05)
(¬x05 ∨ x06 ∨ ¬x04)
(x02 ∨ x05 ∨ x04)
(x02 ∨ x04 ∨ ¬x01)
(¬x03 ∨ x05 ∨ ¬x06)
(x01 ∨ x02 ∨ ¬x05)
(x01 ∨ ¬x04 ∨ x06)
(x05 ∨ x03 ∨ x06)
(x01 ∨ x06 ∨ x05)
(x04 ∨ x06 ∨ ¬x01)
(x04 ∨ x06 ∨ ¬x02)
(¬x01 ∨ ¬x04 ∨ x03)
(x05 ∨ x04 ∨ ¬x02)
(¬x06 ∨ ¬x01 ∨ ¬x05)
(x02 ∨ x05 ∨ x01)
(x04 ∨ ¬x05 ∨ ¬x06)
(¬x01 ∨ x04 ∨ x03)
(x01 ∨ x05 ∨ x06)
(¬x06 ∨ ¬x04 ∨ ¬x05)
(¬x04 ∨ x06 ∨ ¬x03)
(x05 ∨ x01 ∨ x04)
(¬x02 ∨ x01 ∨ x05)
(¬x02 ∨ ¬x01 ∨ ¬x03)
(¬x02 ∨ ¬x03 ∨ ¬x04)
(¬x03 ∨ x01 ∨ ¬x06)
(x01 ∨ x03 ∨ ¬x02)
(¬x04 ∨ ¬x06 ∨ x03)
(¬x02 ∨ ¬x05 ∨ ¬x03)
Answer: {"satisfiable": false, "assignment": null}

Example 7. Variables x01–x06.
(¬x05 ∨ ¬x06 ∨ x01)
(¬x04 ∨ x05 ∨ x01)
(x04 ∨ x06 ∨ x05)
(¬x04 ∨ ¬x06 ∨ x02)
(¬x05 ∨ ¬x03 ∨ x01)
(¬x02 ∨ ¬x01 ∨ ¬x04)
(¬x01 ∨ x03 ∨ ¬x05)
(¬x01 ∨ ¬x04 ∨ x03)
(¬x05 ∨ ¬x03 ∨ x02)
(¬x02 ∨ x06 ∨ x04)
(x03 ∨ ¬x02 ∨ ¬x06)
(¬x03 ∨ ¬x06 ∨ ¬x01)
(x03 ∨ ¬x04 ∨ x05)
(¬x01 ∨ x04 ∨ x06)
(x05 ∨ x04 ∨ ¬x01)
(¬x04 ∨ x01 ∨ x02)
(¬x06 ∨ ¬x01 ∨ x04)
(x05 ∨ ¬x04 ∨ x02)
(¬x04 ∨ x05 ∨ ¬x06)
(x03 ∨ x01 ∨ ¬x04)
(¬x03 ∨ ¬x04 ∨ ¬x02)
(x01 ∨ x03 ∨ x02)
(¬x05 ∨ ¬x06 ∨ x02)
(¬x05 ∨ x03 ∨ ¬x06)
(x01 ∨ ¬x02 ∨ x05)
(¬x01 ∨ x06 ∨ x02)
(x02 ∨ ¬x06 ∨ x05)
(x05 ∨ x02 ∨ ¬x03)
(¬x06 ∨ x01 ∨ x02)
(¬x04 ∨ x02 ∨ x03)
(¬x01 ∨ x03 ∨ ¬x05)
(x01 ∨ ¬x04 ∨ x02)
(¬x05 ∨ ¬x02 ∨ x04)
(¬x01 ∨ ¬x02 ∨ x03)
(x01 ∨ ¬x02 ∨ x04)
(x01 ∨ ¬x05 ∨ ¬x03)
Answer: {"satisfiable": false, "assignment": null}

Example 8. Variables x01–x06.
(x02 ∨ ¬x05 ∨ x06)
(x05 ∨ x04 ∨ ¬x03)
(¬x01 ∨ ¬x02 ∨ x06)
(¬x03 ∨ ¬x06 ∨ x04)
(¬x05 ∨ ¬x01 ∨ ¬x04)
(¬x01 ∨ ¬x06 ∨ ¬x03)
(¬x04 ∨ x02 ∨ ¬x06)
(x02 ∨ x04 ∨ x06)
(¬x03 ∨ ¬x04 ∨ ¬x05)
(¬x06 ∨ x01 ∨ ¬x03)
(¬x06 ∨ x03 ∨ ¬x05)
(¬x01 ∨ x03 ∨ x04)
(x03 ∨ ¬x01 ∨ ¬x02)
(x06 ∨ ¬x01 ∨ ¬x02)
(x06 ∨ x03 ∨ x05)
(x04 ∨ x03 ∨ x01)
(¬x02 ∨ x01 ∨ x04)
(¬x01 ∨ x05 ∨ x02)
(¬x02 ∨ ¬x05 ∨ x01)
(x03 ∨ x02 ∨ x06)
(x06 ∨ x05 ∨ ¬x01)
(x06 ∨ x04 ∨ x02)
(¬x03 ∨ x05 ∨ x06)
(¬x02 ∨ ¬x06 ∨ x01)
(¬x04 ∨ ¬x01 ∨ ¬x02)
(¬x03 ∨ ¬x05 ∨ x06)
(¬x05 ∨ ¬x04 ∨ ¬x01)
(x01 ∨ ¬x06 ∨ ¬x02)
(x03 ∨ x05 ∨ ¬x06)
(x05 ∨ ¬x03 ∨ x04)
(x05 ∨ ¬x03 ∨ ¬x04)
(¬x06 ∨ x03 ∨ x02)
(¬x01 ∨ ¬x05 ∨ ¬x02)
(¬x04 ∨ ¬x03 ∨ ¬x02)
(¬x05 ∨ ¬x01 ∨ ¬x02)
(¬x02 ∨ ¬x06 ∨ x04)
Answer: {"satisfiable": false, "assignment": null}

Now the problem to solve.
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x03 ∨ x04 ∨ ¬x06)
C02: (x08 ∨ ¬x07 ∨ ¬x05)
C03: (x01 ∨ x03 ∨ ¬x05)
C04: (x04 ∨ ¬x06 ∨ ¬x01)
C05: (x07 ∨ x05 ∨ x04)
C06: (x09 ∨ ¬x04 ∨ x01)
C07: (x09 ∨ x04 ∨ ¬x03)
C08: (x02 ∨ ¬x06 ∨ x03)
C09: (¬x01 ∨ x04 ∨ x02)
C10: (x09 ∨ ¬x07 ∨ ¬x01)
C11: (¬x10 ∨ ¬x08 ∨ x05)
C12: (x09 ∨ ¬x08 ∨ x04)
C13: (x03 ∨ ¬x06 ∨ x01)
C14: (¬x04 ∨ ¬x02 ∨ ¬x06)
C15: (x02 ∨ ¬x01 ∨ x05)
C16: (x03 ∨ ¬x05 ∨ ¬x04)
C17: (x06 ∨ ¬x04 ∨ x07)
C18: (x08 ∨ ¬x01 ∨ ¬x04)
C19: (x06 ∨ ¬x05 ∨ ¬x07)
C20: (¬x10 ∨ x07 ∨ x01)
C21: (¬x06 ∨ x03 ∨ x05)
C22: (x03 ∨ ¬x07 ∨ ¬x04)
C23: (¬x04 ∨ ¬x08 ∨ ¬x02)
C24: (¬x08 ∨ ¬x05 ∨ x04)
C25: (¬x10 ∨ x07 ∨ ¬x01)
C26: (x09 ∨ x07 ∨ ¬x06)
C27: (¬x02 ∨ x04 ∨ ¬x07)
C28: (¬x01 ∨ x07 ∨ x03)
C29: (¬x07 ∨ x01 ∨ x03)
C30: (x09 ∨ x07 ∨ x04)
C31: (x08 ∨ ¬x01 ∨ ¬x03)
C32: (¬x08 ∨ x01 ∨ x02)
C33: (x06 ∨ ¬x05 ∨ x04)
C34: (¬x10 ∨ x02 ∨ x01)
C35: (x03 ∨ ¬x05 ∨ x07)
C36: (¬x10 ∨ x04 ∨ ¬x07)
C37: (x03 ∨ x06 ∨ x01)
C38: (x07 ∨ ¬x03 ∨ ¬x06)
C39: (x03 ∨ x02 ∨ ¬x01)
C40: (¬x10 ∨ x05 ∨ x02)
C41: (¬x03 ∨ x01 ∨ ¬x07)
C42: (¬x06 ∨ ¬x04 ∨ x07)
C43: (¬x07 ∨ ¬x02 ∨ ¬x06)
C44: (x01 ∨ ¬x07 ∨ x08)
C45: (x03 ∨ ¬x07 ∨ ¬x06)
C46: (x09 ∨ x05 ∨ ¬x08)
C47: (¬x10 ∨ x01 ∨ x02)
C48: (x01 ∨ ¬x02 ∨ ¬x04)
C49: (¬x08 ∨ x05 ∨ ¬x01)
C50: (x06 ∨ ¬x05 ∨ ¬x03)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **I adaptive DENSITY:** UNSAT on K, SAT on J
- **A2 fixed DENSITY:** UNSAT on K, SAT on J (every environment)
- **exact:** SAT on both
- **A2 LENGTH-M:** the same on K and J
- *params:* `{"examples_alpha_g": [[3.0, true], [3.0, true], [3.0, true], [3.0, true], [6.0, false], [6.0, false], [6.0, false], [6.0, false]], "env": "V"}`
- *notes:* Dev-size examples (n = 6); test items are E2-SAT-K and E2-SAT-J.

</details>

<details><summary>Prompt and computed outputs — <code>E9-V-J</code></summary>

```text
Here are some solved examples.

Example 1. Variables x01–x06.
(x04 ∨ x05 ∨ x06)
(¬x06 ∨ ¬x02 ∨ x01)
(¬x06 ∨ ¬x02 ∨ ¬x05)
(x04 ∨ x05 ∨ x01)
(x01 ∨ x06 ∨ ¬x04)
(¬x01 ∨ ¬x02 ∨ x06)
(¬x03 ∨ x06 ∨ ¬x05)
(x03 ∨ ¬x06 ∨ x01)
(¬x05 ∨ ¬x06 ∨ x02)
(¬x02 ∨ x04 ∨ ¬x01)
(¬x06 ∨ x03 ∨ x01)
(x06 ∨ x05 ∨ ¬x03)
(x05 ∨ x06 ∨ ¬x02)
(¬x02 ∨ x05 ∨ ¬x03)
(¬x02 ∨ x05 ∨ ¬x04)
(¬x06 ∨ x01 ∨ x05)
(¬x01 ∨ x02 ∨ ¬x05)
(x01 ∨ ¬x04 ∨ x02)
Answer: {"satisfiable": true, "assignment": "100100"}

Example 2. Variables x01–x06.
(¬x01 ∨ ¬x05 ∨ x02)
(x04 ∨ x06 ∨ x05)
(¬x03 ∨ x04 ∨ ¬x02)
(x01 ∨ ¬x04 ∨ ¬x03)
(x04 ∨ x05 ∨ ¬x06)
(¬x06 ∨ ¬x05 ∨ ¬x02)
(x01 ∨ x04 ∨ ¬x05)
(¬x04 ∨ ¬x06 ∨ ¬x03)
(¬x05 ∨ x06 ∨ ¬x04)
(¬x02 ∨ x03 ∨ x04)
(x06 ∨ ¬x05 ∨ ¬x03)
(x05 ∨ ¬x01 ∨ x04)
(¬x05 ∨ ¬x02 ∨ x01)
(x06 ∨ x05 ∨ x03)
(¬x06 ∨ x02 ∨ ¬x05)
(¬x02 ∨ ¬x04 ∨ x03)
(x02 ∨ ¬x01 ∨ ¬x06)
(x02 ∨ ¬x01 ∨ ¬x04)
Answer: {"satisfiable": true, "assignment": "111100"}

Example 3. Variables x01–x06.
(¬x02 ∨ ¬x04 ∨ ¬x05)
(¬x06 ∨ ¬x01 ∨ x03)
(x05 ∨ x01 ∨ x04)
(¬x05 ∨ ¬x06 ∨ x02)
(x06 ∨ x04 ∨ ¬x03)
(¬x04 ∨ x06 ∨ ¬x05)
(x04 ∨ ¬x03 ∨ x01)
(¬x02 ∨ x04 ∨ ¬x01)
(¬x06 ∨ x03 ∨ ¬x01)
(x01 ∨ x04 ∨ x05)
(x01 ∨ x04 ∨ x03)
(x02 ∨ x01 ∨ x04)
(x01 ∨ ¬x03 ∨ ¬x04)
(x02 ∨ x01 ∨ ¬x03)
(x01 ∨ x02 ∨ ¬x04)
(x04 ∨ ¬x01 ∨ x03)
(¬x06 ∨ x04 ∨ ¬x05)
(x04 ∨ x03 ∨ x01)
Answer: {"satisfiable": true, "assignment": "100100"}

Example 4. Variables x01–x06.
(¬x03 ∨ x02 ∨ x04)
(¬x06 ∨ ¬x01 ∨ ¬x05)
(x01 ∨ ¬x05 ∨ ¬x06)
(¬x05 ∨ ¬x02 ∨ x04)
(¬x06 ∨ x01 ∨ ¬x03)
(¬x02 ∨ ¬x03 ∨ ¬x05)
(x04 ∨ ¬x06 ∨ x05)
(¬x06 ∨ x02 ∨ ¬x03)
(¬x04 ∨ x01 ∨ x05)
(x05 ∨ x06 ∨ x03)
(x05 ∨ ¬x04 ∨ ¬x03)
(¬x05 ∨ ¬x02 ∨ x04)
(¬x05 ∨ x03 ∨ x06)
(x02 ∨ ¬x03 ∨ ¬x01)
(x02 ∨ ¬x01 ∨ ¬x03)
(¬x04 ∨ x05 ∨ ¬x06)
(¬x04 ∨ x06 ∨ ¬x05)
(¬x06 ∨ x02 ∨ ¬x04)
Answer: {"satisfiable": true, "assignment": "011000"}

Example 5. Variables x01–x06.
(x05 ∨ x06 ∨ ¬x04)
(¬x06 ∨ ¬x01 ∨ x04)
(¬x03 ∨ ¬x02 ∨ x01)
(x03 ∨ ¬x04 ∨ x05)
(x06 ∨ ¬x02 ∨ x04)
(¬x02 ∨ x05 ∨ ¬x03)
(x01 ∨ x06 ∨ x03)
(¬x03 ∨ x02 ∨ ¬x01)
(¬x01 ∨ x05 ∨ x04)
(¬x03 ∨ x04 ∨ x02)
(x01 ∨ x06 ∨ x04)
(¬x05 ∨ ¬x02 ∨ ¬x04)
(¬x01 ∨ ¬x06 ∨ x05)
(¬x03 ∨ x05 ∨ ¬x04)
(¬x04 ∨ ¬x06 ∨ x03)
(x04 ∨ x01 ∨ x03)
(x03 ∨ x04 ∨ x02)
(¬x01 ∨ x04 ∨ ¬x02)
(x04 ∨ x01 ∨ ¬x03)
(x01 ∨ x02 ∨ ¬x04)
(x02 ∨ x04 ∨ ¬x05)
(¬x05 ∨ x02 ∨ ¬x06)
(x05 ∨ ¬x02 ∨ x01)
(x04 ∨ ¬x01 ∨ ¬x03)
(¬x06 ∨ x03 ∨ x04)
(¬x01 ∨ x05 ∨ ¬x04)
(x06 ∨ ¬x05 ∨ ¬x02)
(x02 ∨ ¬x04 ∨ x05)
(¬x04 ∨ ¬x06 ∨ ¬x01)
(x03 ∨ ¬x05 ∨ x06)
(¬x02 ∨ ¬x04 ∨ x05)
(x05 ∨ x04 ∨ ¬x06)
(¬x03 ∨ x01 ∨ x06)
(x02 ∨ x06 ∨ ¬x03)
(¬x05 ∨ ¬x04 ∨ ¬x01)
(¬x02 ∨ ¬x05 ∨ ¬x04)
Answer: {"satisfiable": false, "assignment": null}

Example 6. Variables x01–x06.
(x04 ∨ ¬x05 ∨ x03)
(x04 ∨ x05 ∨ ¬x06)
(¬x02 ∨ ¬x03 ∨ x01)
(x03 ∨ ¬x04 ∨ x06)
(x02 ∨ x03 ∨ ¬x06)
(x06 ∨ x01 ∨ ¬x02)
(¬x01 ∨ ¬x03 ∨ x04)
(x02 ∨ ¬x01 ∨ ¬x05)
(x01 ∨ x03 ∨ ¬x05)
(¬x05 ∨ x06 ∨ ¬x04)
(x02 ∨ x05 ∨ x04)
(x02 ∨ x04 ∨ ¬x01)
(¬x03 ∨ x05 ∨ ¬x06)
(x01 ∨ x02 ∨ ¬x05)
(x01 ∨ ¬x04 ∨ x06)
(x05 ∨ x03 ∨ x06)
(x01 ∨ x06 ∨ x05)
(x04 ∨ x06 ∨ ¬x01)
(x04 ∨ x06 ∨ ¬x02)
(¬x01 ∨ ¬x04 ∨ x03)
(x05 ∨ x04 ∨ ¬x02)
(¬x06 ∨ ¬x01 ∨ ¬x05)
(x02 ∨ x05 ∨ x01)
(x04 ∨ ¬x05 ∨ ¬x06)
(¬x01 ∨ x04 ∨ x03)
(x01 ∨ x05 ∨ x06)
(¬x06 ∨ ¬x04 ∨ ¬x05)
(¬x04 ∨ x06 ∨ ¬x03)
(x05 ∨ x01 ∨ x04)
(¬x02 ∨ x01 ∨ x05)
(¬x02 ∨ ¬x01 ∨ ¬x03)
(¬x02 ∨ ¬x03 ∨ ¬x04)
(¬x03 ∨ x01 ∨ ¬x06)
(x01 ∨ x03 ∨ ¬x02)
(¬x04 ∨ ¬x06 ∨ x03)
(¬x02 ∨ ¬x05 ∨ ¬x03)
Answer: {"satisfiable": false, "assignment": null}

Example 7. Variables x01–x06.
(¬x05 ∨ ¬x06 ∨ x01)
(¬x04 ∨ x05 ∨ x01)
(x04 ∨ x06 ∨ x05)
(¬x04 ∨ ¬x06 ∨ x02)
(¬x05 ∨ ¬x03 ∨ x01)
(¬x02 ∨ ¬x01 ∨ ¬x04)
(¬x01 ∨ x03 ∨ ¬x05)
(¬x01 ∨ ¬x04 ∨ x03)
(¬x05 ∨ ¬x03 ∨ x02)
(¬x02 ∨ x06 ∨ x04)
(x03 ∨ ¬x02 ∨ ¬x06)
(¬x03 ∨ ¬x06 ∨ ¬x01)
(x03 ∨ ¬x04 ∨ x05)
(¬x01 ∨ x04 ∨ x06)
(x05 ∨ x04 ∨ ¬x01)
(¬x04 ∨ x01 ∨ x02)
(¬x06 ∨ ¬x01 ∨ x04)
(x05 ∨ ¬x04 ∨ x02)
(¬x04 ∨ x05 ∨ ¬x06)
(x03 ∨ x01 ∨ ¬x04)
(¬x03 ∨ ¬x04 ∨ ¬x02)
(x01 ∨ x03 ∨ x02)
(¬x05 ∨ ¬x06 ∨ x02)
(¬x05 ∨ x03 ∨ ¬x06)
(x01 ∨ ¬x02 ∨ x05)
(¬x01 ∨ x06 ∨ x02)
(x02 ∨ ¬x06 ∨ x05)
(x05 ∨ x02 ∨ ¬x03)
(¬x06 ∨ x01 ∨ x02)
(¬x04 ∨ x02 ∨ x03)
(¬x01 ∨ x03 ∨ ¬x05)
(x01 ∨ ¬x04 ∨ x02)
(¬x05 ∨ ¬x02 ∨ x04)
(¬x01 ∨ ¬x02 ∨ x03)
(x01 ∨ ¬x02 ∨ x04)
(x01 ∨ ¬x05 ∨ ¬x03)
Answer: {"satisfiable": false, "assignment": null}

Example 8. Variables x01–x06.
(x02 ∨ ¬x05 ∨ x06)
(x05 ∨ x04 ∨ ¬x03)
(¬x01 ∨ ¬x02 ∨ x06)
(¬x03 ∨ ¬x06 ∨ x04)
(¬x05 ∨ ¬x01 ∨ ¬x04)
(¬x01 ∨ ¬x06 ∨ ¬x03)
(¬x04 ∨ x02 ∨ ¬x06)
(x02 ∨ x04 ∨ x06)
(¬x03 ∨ ¬x04 ∨ ¬x05)
(¬x06 ∨ x01 ∨ ¬x03)
(¬x06 ∨ x03 ∨ ¬x05)
(¬x01 ∨ x03 ∨ x04)
(x03 ∨ ¬x01 ∨ ¬x02)
(x06 ∨ ¬x01 ∨ ¬x02)
(x06 ∨ x03 ∨ x05)
(x04 ∨ x03 ∨ x01)
(¬x02 ∨ x01 ∨ x04)
(¬x01 ∨ x05 ∨ x02)
(¬x02 ∨ ¬x05 ∨ x01)
(x03 ∨ x02 ∨ x06)
(x06 ∨ x05 ∨ ¬x01)
(x06 ∨ x04 ∨ x02)
(¬x03 ∨ x05 ∨ x06)
(¬x02 ∨ ¬x06 ∨ x01)
(¬x04 ∨ ¬x01 ∨ ¬x02)
(¬x03 ∨ ¬x05 ∨ x06)
(¬x05 ∨ ¬x04 ∨ ¬x01)
(x01 ∨ ¬x06 ∨ ¬x02)
(x03 ∨ x05 ∨ ¬x06)
(x05 ∨ ¬x03 ∨ x04)
(x05 ∨ ¬x03 ∨ ¬x04)
(¬x06 ∨ x03 ∨ x02)
(¬x01 ∨ ¬x05 ∨ ¬x02)
(¬x04 ∨ ¬x03 ∨ ¬x02)
(¬x05 ∨ ¬x01 ∨ ¬x02)
(¬x02 ∨ ¬x06 ∨ x04)
Answer: {"satisfiable": false, "assignment": null}

Now the problem to solve.
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12, x13, x14, x15.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x03 ∨ x04 ∨ ¬x06)
C02: (x08 ∨ ¬x07 ∨ ¬x05)
C03: (x01 ∨ x03 ∨ ¬x05)
C04: (x04 ∨ ¬x06 ∨ ¬x01)
C05: (x07 ∨ x05 ∨ x04)
C06: (x12 ∨ ¬x04 ∨ x01)
C07: (x12 ∨ x04 ∨ ¬x03)
C08: (x02 ∨ ¬x06 ∨ x03)
C09: (¬x01 ∨ x04 ∨ x02)
C10: (x13 ∨ ¬x07 ∨ ¬x01)
C11: (¬x09 ∨ ¬x08 ∨ x05)
C12: (x13 ∨ ¬x08 ∨ x04)
C13: (x03 ∨ ¬x06 ∨ x01)
C14: (¬x04 ∨ ¬x02 ∨ ¬x06)
C15: (x02 ∨ ¬x01 ∨ x05)
C16: (x03 ∨ ¬x05 ∨ ¬x04)
C17: (x06 ∨ ¬x04 ∨ x07)
C18: (x08 ∨ ¬x01 ∨ ¬x04)
C19: (x06 ∨ ¬x05 ∨ ¬x07)
C20: (¬x09 ∨ x07 ∨ x01)
C21: (¬x06 ∨ x03 ∨ x05)
C22: (x03 ∨ ¬x07 ∨ ¬x04)
C23: (¬x04 ∨ ¬x08 ∨ ¬x02)
C24: (¬x08 ∨ ¬x05 ∨ x04)
C25: (¬x09 ∨ x07 ∨ ¬x01)
C26: (x14 ∨ x07 ∨ ¬x06)
C27: (¬x02 ∨ x04 ∨ ¬x07)
C28: (¬x01 ∨ x07 ∨ x03)
C29: (¬x07 ∨ x01 ∨ x03)
C30: (x14 ∨ x07 ∨ x04)
C31: (x08 ∨ ¬x01 ∨ ¬x03)
C32: (¬x08 ∨ x01 ∨ x02)
C33: (x06 ∨ ¬x05 ∨ x04)
C34: (¬x10 ∨ x02 ∨ x01)
C35: (x03 ∨ ¬x05 ∨ x07)
C36: (¬x10 ∨ x04 ∨ ¬x07)
C37: (x03 ∨ x06 ∨ x01)
C38: (x07 ∨ ¬x03 ∨ ¬x06)
C39: (x03 ∨ x02 ∨ ¬x01)
C40: (¬x11 ∨ x05 ∨ x02)
C41: (¬x03 ∨ x01 ∨ ¬x07)
C42: (¬x06 ∨ ¬x04 ∨ x07)
C43: (¬x07 ∨ ¬x02 ∨ ¬x06)
C44: (x01 ∨ ¬x07 ∨ x08)
C45: (x03 ∨ ¬x07 ∨ ¬x06)
C46: (x15 ∨ x05 ∨ ¬x08)
C47: (¬x11 ∨ x01 ∨ x02)
C48: (x01 ∨ ¬x02 ∨ ¬x04)
C49: (¬x08 ∨ x05 ∨ ¬x01)
C50: (x06 ∨ ¬x05 ∨ ¬x03)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **I adaptive DENSITY:** UNSAT on K, SAT on J
- **A2 fixed DENSITY:** UNSAT on K, SAT on J (every environment)
- **exact:** SAT on both
- **A2 LENGTH-M:** the same on K and J
- *params:* `{"examples_alpha_g": [[3.0, true], [3.0, true], [3.0, true], [3.0, true], [6.0, false], [6.0, false], [6.0, false], [6.0, false]], "env": "V"}`
- *notes:* Dev-size examples (n = 6); test items are E2-SAT-K and E2-SAT-J.

</details>

<details><summary>Prompt and computed outputs — <code>E9-N-K</code></summary>

```text
Here are some solved examples.

Example 1. Variables x01–x06.
(x04 ∨ x05 ∨ x06)
(¬x06 ∨ ¬x02 ∨ x01)
(¬x06 ∨ ¬x02 ∨ ¬x05)
(x04 ∨ x05 ∨ x01)
(x01 ∨ x06 ∨ ¬x04)
(¬x01 ∨ ¬x02 ∨ x06)
(¬x03 ∨ x06 ∨ ¬x05)
(x03 ∨ ¬x06 ∨ x01)
(¬x05 ∨ ¬x06 ∨ x02)
(¬x02 ∨ x04 ∨ ¬x01)
(¬x06 ∨ x03 ∨ x01)
(x06 ∨ x05 ∨ ¬x03)
(x05 ∨ x06 ∨ ¬x02)
(¬x02 ∨ x05 ∨ ¬x03)
(¬x02 ∨ x05 ∨ ¬x04)
(¬x06 ∨ x01 ∨ x05)
(¬x01 ∨ x02 ∨ ¬x05)
(x01 ∨ ¬x04 ∨ x02)
Answer: {"satisfiable": true, "assignment": "100100"}

Example 2. Variables x01–x06.
(¬x01 ∨ ¬x05 ∨ x02)
(x04 ∨ x06 ∨ x05)
(¬x03 ∨ x04 ∨ ¬x02)
(x01 ∨ ¬x04 ∨ ¬x03)
(x04 ∨ x05 ∨ ¬x06)
(¬x06 ∨ ¬x05 ∨ ¬x02)
(x01 ∨ x04 ∨ ¬x05)
(¬x04 ∨ ¬x06 ∨ ¬x03)
(¬x05 ∨ x06 ∨ ¬x04)
(¬x02 ∨ x03 ∨ x04)
(x06 ∨ ¬x05 ∨ ¬x03)
(x05 ∨ ¬x01 ∨ x04)
(¬x05 ∨ ¬x02 ∨ x01)
(x06 ∨ x05 ∨ x03)
(¬x06 ∨ x02 ∨ ¬x05)
(¬x02 ∨ ¬x04 ∨ x03)
(x02 ∨ ¬x01 ∨ ¬x06)
(x02 ∨ ¬x01 ∨ ¬x04)
Answer: {"satisfiable": true, "assignment": "111100"}

Example 3. Variables x01–x06.
(¬x06 ∨ x03 ∨ x02)
(¬x03 ∨ ¬x06 ∨ x01)
(x03 ∨ x02 ∨ x06)
(x06 ∨ x02 ∨ x01)
(x03 ∨ ¬x02 ∨ x04)
(x01 ∨ ¬x02 ∨ x05)
(¬x04 ∨ x03 ∨ ¬x02)
(¬x03 ∨ x04 ∨ ¬x02)
(x04 ∨ ¬x02 ∨ ¬x06)
(¬x05 ∨ ¬x04 ∨ ¬x01)
(¬x03 ∨ x02 ∨ ¬x01)
(x06 ∨ ¬x01 ∨ ¬x05)
(¬x02 ∨ x05 ∨ x04)
(¬x03 ∨ ¬x01 ∨ x05)
(¬x03 ∨ ¬x04 ∨ ¬x05)
(x01 ∨ ¬x02 ∨ ¬x03)
(¬x04 ∨ x02 ∨ x03)
(¬x01 ∨ ¬x02 ∨ x05)
Answer: {"satisfiable": false, "assignment": null}

Example 4. Variables x01–x06.
(¬x01 ∨ ¬x04 ∨ x02)
(x05 ∨ ¬x04 ∨ x03)
(¬x04 ∨ x06 ∨ ¬x05)
(x03 ∨ x02 ∨ ¬x05)
(x01 ∨ ¬x06 ∨ ¬x02)
(¬x01 ∨ ¬x02 ∨ ¬x05)
(x04 ∨ x06 ∨ ¬x01)
(x01 ∨ ¬x05 ∨ x02)
(x06 ∨ x04 ∨ x02)
(x01 ∨ x04 ∨ ¬x05)
(¬x01 ∨ x06 ∨ x05)
(x06 ∨ x05 ∨ ¬x04)
(x05 ∨ ¬x06 ∨ ¬x03)
(¬x06 ∨ ¬x03 ∨ ¬x01)
(x05 ∨ x04 ∨ x03)
(x02 ∨ ¬x03 ∨ x01)
(x06 ∨ x01 ∨ x04)
(¬x05 ∨ ¬x01 ∨ ¬x03)
Answer: {"satisfiable": false, "assignment": null}

Example 5. Variables x01–x06.
(x01 ∨ ¬x05 ∨ x06)
(¬x05 ∨ x06 ∨ ¬x03)
(¬x04 ∨ ¬x01 ∨ ¬x06)
(¬x05 ∨ ¬x01 ∨ x03)
(x05 ∨ x03 ∨ x04)
(x02 ∨ x03 ∨ ¬x05)
(x02 ∨ x06 ∨ x01)
(¬x04 ∨ x02 ∨ ¬x01)
(¬x03 ∨ x04 ∨ x01)
(¬x03 ∨ ¬x04 ∨ x06)
(¬x06 ∨ ¬x05 ∨ x04)
(x03 ∨ ¬x01 ∨ ¬x04)
(x06 ∨ ¬x05 ∨ ¬x04)
(¬x03 ∨ x06 ∨ ¬x05)
(x05 ∨ ¬x06 ∨ x02)
(¬x02 ∨ ¬x05 ∨ x01)
(x04 ∨ x06 ∨ ¬x02)
(¬x04 ∨ ¬x01 ∨ x03)
(x06 ∨ ¬x05 ∨ x03)
(x04 ∨ x01 ∨ ¬x06)
(x02 ∨ x03 ∨ ¬x04)
(¬x06 ∨ x01 ∨ ¬x02)
(¬x02 ∨ ¬x05 ∨ ¬x03)
(¬x02 ∨ x06 ∨ ¬x05)
(x01 ∨ x02 ∨ ¬x03)
(x01 ∨ x06 ∨ x03)
(x01 ∨ ¬x06 ∨ x03)
(x06 ∨ ¬x04 ∨ ¬x02)
(x04 ∨ x06 ∨ x05)
(x02 ∨ x04 ∨ x01)
(¬x02 ∨ ¬x04 ∨ x06)
(¬x04 ∨ ¬x01 ∨ ¬x05)
(¬x04 ∨ ¬x06 ∨ ¬x01)
(x01 ∨ x04 ∨ x02)
(x01 ∨ ¬x02 ∨ x03)
(x04 ∨ x05 ∨ x06)
Answer: {"satisfiable": true, "assignment": "111001"}

Example 6. Variables x01–x06.
(x05 ∨ x06 ∨ ¬x04)
(¬x06 ∨ ¬x01 ∨ x04)
(¬x03 ∨ ¬x02 ∨ x01)
(x03 ∨ ¬x04 ∨ x05)
(x06 ∨ ¬x02 ∨ x04)
(¬x02 ∨ x05 ∨ ¬x03)
(x01 ∨ x06 ∨ x03)
(¬x03 ∨ x02 ∨ ¬x01)
(¬x01 ∨ x05 ∨ x04)
(¬x03 ∨ x04 ∨ x02)
(x01 ∨ x06 ∨ x04)
(¬x05 ∨ ¬x02 ∨ ¬x04)
(¬x01 ∨ ¬x06 ∨ x05)
(¬x03 ∨ x05 ∨ ¬x04)
(¬x04 ∨ ¬x06 ∨ x03)
(x04 ∨ x01 ∨ x03)
(x03 ∨ x04 ∨ x02)
(¬x01 ∨ x04 ∨ ¬x02)
(x04 ∨ x01 ∨ ¬x03)
(x01 ∨ x02 ∨ ¬x04)
(x02 ∨ x04 ∨ ¬x05)
(¬x05 ∨ x02 ∨ ¬x06)
(x05 ∨ ¬x02 ∨ x01)
(x04 ∨ ¬x01 ∨ ¬x03)
(¬x06 ∨ x03 ∨ x04)
(¬x01 ∨ x05 ∨ ¬x04)
(x06 ∨ ¬x05 ∨ ¬x02)
(x02 ∨ ¬x04 ∨ x05)
(¬x04 ∨ ¬x06 ∨ ¬x01)
(x03 ∨ ¬x05 ∨ x06)
(¬x02 ∨ ¬x04 ∨ x05)
(x05 ∨ x04 ∨ ¬x06)
(¬x03 ∨ x01 ∨ x06)
(x02 ∨ x06 ∨ ¬x03)
(¬x05 ∨ ¬x04 ∨ ¬x01)
(¬x02 ∨ ¬x05 ∨ ¬x04)
Answer: {"satisfiable": false, "assignment": null}

Example 7. Variables x01–x06.
(¬x05 ∨ x01 ∨ ¬x04)
(x02 ∨ x05 ∨ x06)
(¬x01 ∨ ¬x03 ∨ ¬x02)
(¬x05 ∨ x02 ∨ x06)
(¬x03 ∨ ¬x06 ∨ x01)
(¬x04 ∨ x02 ∨ ¬x06)
(¬x01 ∨ x06 ∨ x02)
(¬x03 ∨ ¬x06 ∨ x04)
(x03 ∨ ¬x04 ∨ ¬x01)
(¬x04 ∨ ¬x03 ∨ ¬x05)
(¬x04 ∨ ¬x02 ∨ ¬x05)
(¬x03 ∨ x01 ∨ ¬x06)
(¬x03 ∨ ¬x05 ∨ ¬x02)
(¬x01 ∨ x02 ∨ x04)
(x02 ∨ x05 ∨ x03)
(x02 ∨ x01 ∨ ¬x06)
(x04 ∨ x06 ∨ ¬x05)
(x06 ∨ x05 ∨ x01)
(x03 ∨ ¬x06 ∨ ¬x05)
(¬x01 ∨ ¬x04 ∨ x05)
(x02 ∨ ¬x04 ∨ ¬x01)
(¬x04 ∨ ¬x03 ∨ ¬x02)
(¬x01 ∨ ¬x04 ∨ ¬x05)
(¬x01 ∨ ¬x03 ∨ x04)
(x05 ∨ ¬x03 ∨ ¬x06)
(¬x01 ∨ ¬x05 ∨ x02)
(¬x06 ∨ ¬x04 ∨ x01)
(x01 ∨ x03 ∨ ¬x02)
(¬x03 ∨ x04 ∨ ¬x02)
(¬x02 ∨ ¬x03 ∨ ¬x04)
(¬x04 ∨ ¬x06 ∨ x03)
(x04 ∨ x01 ∨ ¬x02)
(¬x05 ∨ x04 ∨ x01)
(x02 ∨ ¬x06 ∨ ¬x01)
(¬x03 ∨ x04 ∨ x01)
(¬x02 ∨ ¬x03 ∨ x04)
Answer: {"satisfiable": true, "assignment": "110000"}

Example 8. Variables x01–x06.
(¬x05 ∨ ¬x06 ∨ x01)
(¬x04 ∨ x05 ∨ x01)
(x04 ∨ x06 ∨ x05)
(¬x04 ∨ ¬x06 ∨ x02)
(¬x05 ∨ ¬x03 ∨ x01)
(¬x02 ∨ ¬x01 ∨ ¬x04)
(¬x01 ∨ x03 ∨ ¬x05)
(¬x01 ∨ ¬x04 ∨ x03)
(¬x05 ∨ ¬x03 ∨ x02)
(¬x02 ∨ x06 ∨ x04)
(x03 ∨ ¬x02 ∨ ¬x06)
(¬x03 ∨ ¬x06 ∨ ¬x01)
(x03 ∨ ¬x04 ∨ x05)
(¬x01 ∨ x04 ∨ x06)
(x05 ∨ x04 ∨ ¬x01)
(¬x04 ∨ x01 ∨ x02)
(¬x06 ∨ ¬x01 ∨ x04)
(x05 ∨ ¬x04 ∨ x02)
(¬x04 ∨ x05 ∨ ¬x06)
(x03 ∨ x01 ∨ ¬x04)
(¬x03 ∨ ¬x04 ∨ ¬x02)
(x01 ∨ x03 ∨ x02)
(¬x05 ∨ ¬x06 ∨ x02)
(¬x05 ∨ x03 ∨ ¬x06)
(x01 ∨ ¬x02 ∨ x05)
(¬x01 ∨ x06 ∨ x02)
(x02 ∨ ¬x06 ∨ x05)
(x05 ∨ x02 ∨ ¬x03)
(¬x06 ∨ x01 ∨ x02)
(¬x04 ∨ x02 ∨ x03)
(¬x01 ∨ x03 ∨ ¬x05)
(x01 ∨ ¬x04 ∨ x02)
(¬x05 ∨ ¬x02 ∨ x04)
(¬x01 ∨ ¬x02 ∨ x03)
(x01 ∨ ¬x02 ∨ x04)
(x01 ∨ ¬x05 ∨ ¬x03)
Answer: {"satisfiable": false, "assignment": null}

Now the problem to solve.
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x03 ∨ x04 ∨ ¬x06)
C02: (x08 ∨ ¬x07 ∨ ¬x05)
C03: (x01 ∨ x03 ∨ ¬x05)
C04: (x04 ∨ ¬x06 ∨ ¬x01)
C05: (x07 ∨ x05 ∨ x04)
C06: (x09 ∨ ¬x04 ∨ x01)
C07: (x09 ∨ x04 ∨ ¬x03)
C08: (x02 ∨ ¬x06 ∨ x03)
C09: (¬x01 ∨ x04 ∨ x02)
C10: (x09 ∨ ¬x07 ∨ ¬x01)
C11: (¬x10 ∨ ¬x08 ∨ x05)
C12: (x09 ∨ ¬x08 ∨ x04)
C13: (x03 ∨ ¬x06 ∨ x01)
C14: (¬x04 ∨ ¬x02 ∨ ¬x06)
C15: (x02 ∨ ¬x01 ∨ x05)
C16: (x03 ∨ ¬x05 ∨ ¬x04)
C17: (x06 ∨ ¬x04 ∨ x07)
C18: (x08 ∨ ¬x01 ∨ ¬x04)
C19: (x06 ∨ ¬x05 ∨ ¬x07)
C20: (¬x10 ∨ x07 ∨ x01)
C21: (¬x06 ∨ x03 ∨ x05)
C22: (x03 ∨ ¬x07 ∨ ¬x04)
C23: (¬x04 ∨ ¬x08 ∨ ¬x02)
C24: (¬x08 ∨ ¬x05 ∨ x04)
C25: (¬x10 ∨ x07 ∨ ¬x01)
C26: (x09 ∨ x07 ∨ ¬x06)
C27: (¬x02 ∨ x04 ∨ ¬x07)
C28: (¬x01 ∨ x07 ∨ x03)
C29: (¬x07 ∨ x01 ∨ x03)
C30: (x09 ∨ x07 ∨ x04)
C31: (x08 ∨ ¬x01 ∨ ¬x03)
C32: (¬x08 ∨ x01 ∨ x02)
C33: (x06 ∨ ¬x05 ∨ x04)
C34: (¬x10 ∨ x02 ∨ x01)
C35: (x03 ∨ ¬x05 ∨ x07)
C36: (¬x10 ∨ x04 ∨ ¬x07)
C37: (x03 ∨ x06 ∨ x01)
C38: (x07 ∨ ¬x03 ∨ ¬x06)
C39: (x03 ∨ x02 ∨ ¬x01)
C40: (¬x10 ∨ x05 ∨ x02)
C41: (¬x03 ∨ x01 ∨ ¬x07)
C42: (¬x06 ∨ ¬x04 ∨ x07)
C43: (¬x07 ∨ ¬x02 ∨ ¬x06)
C44: (x01 ∨ ¬x07 ∨ x08)
C45: (x03 ∨ ¬x07 ∨ ¬x06)
C46: (x09 ∨ x05 ∨ ¬x08)
C47: (¬x10 ∨ x01 ∨ x02)
C48: (x01 ∨ ¬x02 ∨ ¬x04)
C49: (¬x08 ∨ x05 ∨ ¬x01)
C50: (x06 ∨ ¬x05 ∨ ¬x03)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **I adaptive DENSITY:** K and J alike
- **A2 fixed DENSITY:** UNSAT on K, SAT on J (every environment)
- **exact:** SAT on both
- **A2 LENGTH-M:** the same on K and J
- *params:* `{"examples_alpha_g": [[3.0, true], [3.0, true], [3.0, false], [3.0, false], [6.0, true], [6.0, false], [6.0, true], [6.0, false]], "env": "N"}`
- *notes:* Dev-size examples (n = 6); test items are E2-SAT-K and E2-SAT-J.

</details>

<details><summary>Prompt and computed outputs — <code>E9-N-J</code></summary>

```text
Here are some solved examples.

Example 1. Variables x01–x06.
(x04 ∨ x05 ∨ x06)
(¬x06 ∨ ¬x02 ∨ x01)
(¬x06 ∨ ¬x02 ∨ ¬x05)
(x04 ∨ x05 ∨ x01)
(x01 ∨ x06 ∨ ¬x04)
(¬x01 ∨ ¬x02 ∨ x06)
(¬x03 ∨ x06 ∨ ¬x05)
(x03 ∨ ¬x06 ∨ x01)
(¬x05 ∨ ¬x06 ∨ x02)
(¬x02 ∨ x04 ∨ ¬x01)
(¬x06 ∨ x03 ∨ x01)
(x06 ∨ x05 ∨ ¬x03)
(x05 ∨ x06 ∨ ¬x02)
(¬x02 ∨ x05 ∨ ¬x03)
(¬x02 ∨ x05 ∨ ¬x04)
(¬x06 ∨ x01 ∨ x05)
(¬x01 ∨ x02 ∨ ¬x05)
(x01 ∨ ¬x04 ∨ x02)
Answer: {"satisfiable": true, "assignment": "100100"}

Example 2. Variables x01–x06.
(¬x01 ∨ ¬x05 ∨ x02)
(x04 ∨ x06 ∨ x05)
(¬x03 ∨ x04 ∨ ¬x02)
(x01 ∨ ¬x04 ∨ ¬x03)
(x04 ∨ x05 ∨ ¬x06)
(¬x06 ∨ ¬x05 ∨ ¬x02)
(x01 ∨ x04 ∨ ¬x05)
(¬x04 ∨ ¬x06 ∨ ¬x03)
(¬x05 ∨ x06 ∨ ¬x04)
(¬x02 ∨ x03 ∨ x04)
(x06 ∨ ¬x05 ∨ ¬x03)
(x05 ∨ ¬x01 ∨ x04)
(¬x05 ∨ ¬x02 ∨ x01)
(x06 ∨ x05 ∨ x03)
(¬x06 ∨ x02 ∨ ¬x05)
(¬x02 ∨ ¬x04 ∨ x03)
(x02 ∨ ¬x01 ∨ ¬x06)
(x02 ∨ ¬x01 ∨ ¬x04)
Answer: {"satisfiable": true, "assignment": "111100"}

Example 3. Variables x01–x06.
(¬x06 ∨ x03 ∨ x02)
(¬x03 ∨ ¬x06 ∨ x01)
(x03 ∨ x02 ∨ x06)
(x06 ∨ x02 ∨ x01)
(x03 ∨ ¬x02 ∨ x04)
(x01 ∨ ¬x02 ∨ x05)
(¬x04 ∨ x03 ∨ ¬x02)
(¬x03 ∨ x04 ∨ ¬x02)
(x04 ∨ ¬x02 ∨ ¬x06)
(¬x05 ∨ ¬x04 ∨ ¬x01)
(¬x03 ∨ x02 ∨ ¬x01)
(x06 ∨ ¬x01 ∨ ¬x05)
(¬x02 ∨ x05 ∨ x04)
(¬x03 ∨ ¬x01 ∨ x05)
(¬x03 ∨ ¬x04 ∨ ¬x05)
(x01 ∨ ¬x02 ∨ ¬x03)
(¬x04 ∨ x02 ∨ x03)
(¬x01 ∨ ¬x02 ∨ x05)
Answer: {"satisfiable": false, "assignment": null}

Example 4. Variables x01–x06.
(¬x01 ∨ ¬x04 ∨ x02)
(x05 ∨ ¬x04 ∨ x03)
(¬x04 ∨ x06 ∨ ¬x05)
(x03 ∨ x02 ∨ ¬x05)
(x01 ∨ ¬x06 ∨ ¬x02)
(¬x01 ∨ ¬x02 ∨ ¬x05)
(x04 ∨ x06 ∨ ¬x01)
(x01 ∨ ¬x05 ∨ x02)
(x06 ∨ x04 ∨ x02)
(x01 ∨ x04 ∨ ¬x05)
(¬x01 ∨ x06 ∨ x05)
(x06 ∨ x05 ∨ ¬x04)
(x05 ∨ ¬x06 ∨ ¬x03)
(¬x06 ∨ ¬x03 ∨ ¬x01)
(x05 ∨ x04 ∨ x03)
(x02 ∨ ¬x03 ∨ x01)
(x06 ∨ x01 ∨ x04)
(¬x05 ∨ ¬x01 ∨ ¬x03)
Answer: {"satisfiable": false, "assignment": null}

Example 5. Variables x01–x06.
(x01 ∨ ¬x05 ∨ x06)
(¬x05 ∨ x06 ∨ ¬x03)
(¬x04 ∨ ¬x01 ∨ ¬x06)
(¬x05 ∨ ¬x01 ∨ x03)
(x05 ∨ x03 ∨ x04)
(x02 ∨ x03 ∨ ¬x05)
(x02 ∨ x06 ∨ x01)
(¬x04 ∨ x02 ∨ ¬x01)
(¬x03 ∨ x04 ∨ x01)
(¬x03 ∨ ¬x04 ∨ x06)
(¬x06 ∨ ¬x05 ∨ x04)
(x03 ∨ ¬x01 ∨ ¬x04)
(x06 ∨ ¬x05 ∨ ¬x04)
(¬x03 ∨ x06 ∨ ¬x05)
(x05 ∨ ¬x06 ∨ x02)
(¬x02 ∨ ¬x05 ∨ x01)
(x04 ∨ x06 ∨ ¬x02)
(¬x04 ∨ ¬x01 ∨ x03)
(x06 ∨ ¬x05 ∨ x03)
(x04 ∨ x01 ∨ ¬x06)
(x02 ∨ x03 ∨ ¬x04)
(¬x06 ∨ x01 ∨ ¬x02)
(¬x02 ∨ ¬x05 ∨ ¬x03)
(¬x02 ∨ x06 ∨ ¬x05)
(x01 ∨ x02 ∨ ¬x03)
(x01 ∨ x06 ∨ x03)
(x01 ∨ ¬x06 ∨ x03)
(x06 ∨ ¬x04 ∨ ¬x02)
(x04 ∨ x06 ∨ x05)
(x02 ∨ x04 ∨ x01)
(¬x02 ∨ ¬x04 ∨ x06)
(¬x04 ∨ ¬x01 ∨ ¬x05)
(¬x04 ∨ ¬x06 ∨ ¬x01)
(x01 ∨ x04 ∨ x02)
(x01 ∨ ¬x02 ∨ x03)
(x04 ∨ x05 ∨ x06)
Answer: {"satisfiable": true, "assignment": "111001"}

Example 6. Variables x01–x06.
(x05 ∨ x06 ∨ ¬x04)
(¬x06 ∨ ¬x01 ∨ x04)
(¬x03 ∨ ¬x02 ∨ x01)
(x03 ∨ ¬x04 ∨ x05)
(x06 ∨ ¬x02 ∨ x04)
(¬x02 ∨ x05 ∨ ¬x03)
(x01 ∨ x06 ∨ x03)
(¬x03 ∨ x02 ∨ ¬x01)
(¬x01 ∨ x05 ∨ x04)
(¬x03 ∨ x04 ∨ x02)
(x01 ∨ x06 ∨ x04)
(¬x05 ∨ ¬x02 ∨ ¬x04)
(¬x01 ∨ ¬x06 ∨ x05)
(¬x03 ∨ x05 ∨ ¬x04)
(¬x04 ∨ ¬x06 ∨ x03)
(x04 ∨ x01 ∨ x03)
(x03 ∨ x04 ∨ x02)
(¬x01 ∨ x04 ∨ ¬x02)
(x04 ∨ x01 ∨ ¬x03)
(x01 ∨ x02 ∨ ¬x04)
(x02 ∨ x04 ∨ ¬x05)
(¬x05 ∨ x02 ∨ ¬x06)
(x05 ∨ ¬x02 ∨ x01)
(x04 ∨ ¬x01 ∨ ¬x03)
(¬x06 ∨ x03 ∨ x04)
(¬x01 ∨ x05 ∨ ¬x04)
(x06 ∨ ¬x05 ∨ ¬x02)
(x02 ∨ ¬x04 ∨ x05)
(¬x04 ∨ ¬x06 ∨ ¬x01)
(x03 ∨ ¬x05 ∨ x06)
(¬x02 ∨ ¬x04 ∨ x05)
(x05 ∨ x04 ∨ ¬x06)
(¬x03 ∨ x01 ∨ x06)
(x02 ∨ x06 ∨ ¬x03)
(¬x05 ∨ ¬x04 ∨ ¬x01)
(¬x02 ∨ ¬x05 ∨ ¬x04)
Answer: {"satisfiable": false, "assignment": null}

Example 7. Variables x01–x06.
(¬x05 ∨ x01 ∨ ¬x04)
(x02 ∨ x05 ∨ x06)
(¬x01 ∨ ¬x03 ∨ ¬x02)
(¬x05 ∨ x02 ∨ x06)
(¬x03 ∨ ¬x06 ∨ x01)
(¬x04 ∨ x02 ∨ ¬x06)
(¬x01 ∨ x06 ∨ x02)
(¬x03 ∨ ¬x06 ∨ x04)
(x03 ∨ ¬x04 ∨ ¬x01)
(¬x04 ∨ ¬x03 ∨ ¬x05)
(¬x04 ∨ ¬x02 ∨ ¬x05)
(¬x03 ∨ x01 ∨ ¬x06)
(¬x03 ∨ ¬x05 ∨ ¬x02)
(¬x01 ∨ x02 ∨ x04)
(x02 ∨ x05 ∨ x03)
(x02 ∨ x01 ∨ ¬x06)
(x04 ∨ x06 ∨ ¬x05)
(x06 ∨ x05 ∨ x01)
(x03 ∨ ¬x06 ∨ ¬x05)
(¬x01 ∨ ¬x04 ∨ x05)
(x02 ∨ ¬x04 ∨ ¬x01)
(¬x04 ∨ ¬x03 ∨ ¬x02)
(¬x01 ∨ ¬x04 ∨ ¬x05)
(¬x01 ∨ ¬x03 ∨ x04)
(x05 ∨ ¬x03 ∨ ¬x06)
(¬x01 ∨ ¬x05 ∨ x02)
(¬x06 ∨ ¬x04 ∨ x01)
(x01 ∨ x03 ∨ ¬x02)
(¬x03 ∨ x04 ∨ ¬x02)
(¬x02 ∨ ¬x03 ∨ ¬x04)
(¬x04 ∨ ¬x06 ∨ x03)
(x04 ∨ x01 ∨ ¬x02)
(¬x05 ∨ x04 ∨ x01)
(x02 ∨ ¬x06 ∨ ¬x01)
(¬x03 ∨ x04 ∨ x01)
(¬x02 ∨ ¬x03 ∨ x04)
Answer: {"satisfiable": true, "assignment": "110000"}

Example 8. Variables x01–x06.
(¬x05 ∨ ¬x06 ∨ x01)
(¬x04 ∨ x05 ∨ x01)
(x04 ∨ x06 ∨ x05)
(¬x04 ∨ ¬x06 ∨ x02)
(¬x05 ∨ ¬x03 ∨ x01)
(¬x02 ∨ ¬x01 ∨ ¬x04)
(¬x01 ∨ x03 ∨ ¬x05)
(¬x01 ∨ ¬x04 ∨ x03)
(¬x05 ∨ ¬x03 ∨ x02)
(¬x02 ∨ x06 ∨ x04)
(x03 ∨ ¬x02 ∨ ¬x06)
(¬x03 ∨ ¬x06 ∨ ¬x01)
(x03 ∨ ¬x04 ∨ x05)
(¬x01 ∨ x04 ∨ x06)
(x05 ∨ x04 ∨ ¬x01)
(¬x04 ∨ x01 ∨ x02)
(¬x06 ∨ ¬x01 ∨ x04)
(x05 ∨ ¬x04 ∨ x02)
(¬x04 ∨ x05 ∨ ¬x06)
(x03 ∨ x01 ∨ ¬x04)
(¬x03 ∨ ¬x04 ∨ ¬x02)
(x01 ∨ x03 ∨ x02)
(¬x05 ∨ ¬x06 ∨ x02)
(¬x05 ∨ x03 ∨ ¬x06)
(x01 ∨ ¬x02 ∨ x05)
(¬x01 ∨ x06 ∨ x02)
(x02 ∨ ¬x06 ∨ x05)
(x05 ∨ x02 ∨ ¬x03)
(¬x06 ∨ x01 ∨ x02)
(¬x04 ∨ x02 ∨ x03)
(¬x01 ∨ x03 ∨ ¬x05)
(x01 ∨ ¬x04 ∨ x02)
(¬x05 ∨ ¬x02 ∨ x04)
(¬x01 ∨ ¬x02 ∨ x03)
(x01 ∨ ¬x02 ∨ x04)
(x01 ∨ ¬x05 ∨ ¬x03)
Answer: {"satisfiable": false, "assignment": null}

Now the problem to solve.
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12, x13, x14, x15.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x03 ∨ x04 ∨ ¬x06)
C02: (x08 ∨ ¬x07 ∨ ¬x05)
C03: (x01 ∨ x03 ∨ ¬x05)
C04: (x04 ∨ ¬x06 ∨ ¬x01)
C05: (x07 ∨ x05 ∨ x04)
C06: (x12 ∨ ¬x04 ∨ x01)
C07: (x12 ∨ x04 ∨ ¬x03)
C08: (x02 ∨ ¬x06 ∨ x03)
C09: (¬x01 ∨ x04 ∨ x02)
C10: (x13 ∨ ¬x07 ∨ ¬x01)
C11: (¬x09 ∨ ¬x08 ∨ x05)
C12: (x13 ∨ ¬x08 ∨ x04)
C13: (x03 ∨ ¬x06 ∨ x01)
C14: (¬x04 ∨ ¬x02 ∨ ¬x06)
C15: (x02 ∨ ¬x01 ∨ x05)
C16: (x03 ∨ ¬x05 ∨ ¬x04)
C17: (x06 ∨ ¬x04 ∨ x07)
C18: (x08 ∨ ¬x01 ∨ ¬x04)
C19: (x06 ∨ ¬x05 ∨ ¬x07)
C20: (¬x09 ∨ x07 ∨ x01)
C21: (¬x06 ∨ x03 ∨ x05)
C22: (x03 ∨ ¬x07 ∨ ¬x04)
C23: (¬x04 ∨ ¬x08 ∨ ¬x02)
C24: (¬x08 ∨ ¬x05 ∨ x04)
C25: (¬x09 ∨ x07 ∨ ¬x01)
C26: (x14 ∨ x07 ∨ ¬x06)
C27: (¬x02 ∨ x04 ∨ ¬x07)
C28: (¬x01 ∨ x07 ∨ x03)
C29: (¬x07 ∨ x01 ∨ x03)
C30: (x14 ∨ x07 ∨ x04)
C31: (x08 ∨ ¬x01 ∨ ¬x03)
C32: (¬x08 ∨ x01 ∨ x02)
C33: (x06 ∨ ¬x05 ∨ x04)
C34: (¬x10 ∨ x02 ∨ x01)
C35: (x03 ∨ ¬x05 ∨ x07)
C36: (¬x10 ∨ x04 ∨ ¬x07)
C37: (x03 ∨ x06 ∨ x01)
C38: (x07 ∨ ¬x03 ∨ ¬x06)
C39: (x03 ∨ x02 ∨ ¬x01)
C40: (¬x11 ∨ x05 ∨ x02)
C41: (¬x03 ∨ x01 ∨ ¬x07)
C42: (¬x06 ∨ ¬x04 ∨ x07)
C43: (¬x07 ∨ ¬x02 ∨ ¬x06)
C44: (x01 ∨ ¬x07 ∨ x08)
C45: (x03 ∨ ¬x07 ∨ ¬x06)
C46: (x15 ∨ x05 ∨ ¬x08)
C47: (¬x11 ∨ x01 ∨ x02)
C48: (x01 ∨ ¬x02 ∨ ¬x04)
C49: (¬x08 ∨ x05 ∨ ¬x01)
C50: (x06 ∨ ¬x05 ∨ ¬x03)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **I adaptive DENSITY:** K and J alike
- **A2 fixed DENSITY:** UNSAT on K, SAT on J (every environment)
- **exact:** SAT on both
- **A2 LENGTH-M:** the same on K and J
- *params:* `{"examples_alpha_g": [[3.0, true], [3.0, true], [3.0, false], [3.0, false], [6.0, true], [6.0, false], [6.0, true], [6.0, false]], "env": "N"}`
- *notes:* Dev-size examples (n = 6); test items are E2-SAT-K and E2-SAT-J.

</details>

<details><summary>Prompt and computed outputs — <code>E9-R-K</code></summary>

```text
Here are some solved examples.

Example 1. Variables x01–x06.
(¬x06 ∨ x03 ∨ x02)
(¬x03 ∨ ¬x06 ∨ x01)
(x03 ∨ x02 ∨ x06)
(x06 ∨ x02 ∨ x01)
(x03 ∨ ¬x02 ∨ x04)
(x01 ∨ ¬x02 ∨ x05)
(¬x04 ∨ x03 ∨ ¬x02)
(¬x03 ∨ x04 ∨ ¬x02)
(x04 ∨ ¬x02 ∨ ¬x06)
(¬x05 ∨ ¬x04 ∨ ¬x01)
(¬x03 ∨ x02 ∨ ¬x01)
(x06 ∨ ¬x01 ∨ ¬x05)
(¬x02 ∨ x05 ∨ x04)
(¬x03 ∨ ¬x01 ∨ x05)
(¬x03 ∨ ¬x04 ∨ ¬x05)
(x01 ∨ ¬x02 ∨ ¬x03)
(¬x04 ∨ x02 ∨ x03)
(¬x01 ∨ ¬x02 ∨ x05)
Answer: {"satisfiable": false, "assignment": null}

Example 2. Variables x01–x06.
(¬x01 ∨ ¬x04 ∨ x02)
(x05 ∨ ¬x04 ∨ x03)
(¬x04 ∨ x06 ∨ ¬x05)
(x03 ∨ x02 ∨ ¬x05)
(x01 ∨ ¬x06 ∨ ¬x02)
(¬x01 ∨ ¬x02 ∨ ¬x05)
(x04 ∨ x06 ∨ ¬x01)
(x01 ∨ ¬x05 ∨ x02)
(x06 ∨ x04 ∨ x02)
(x01 ∨ x04 ∨ ¬x05)
(¬x01 ∨ x06 ∨ x05)
(x06 ∨ x05 ∨ ¬x04)
(x05 ∨ ¬x06 ∨ ¬x03)
(¬x06 ∨ ¬x03 ∨ ¬x01)
(x05 ∨ x04 ∨ x03)
(x02 ∨ ¬x03 ∨ x01)
(x06 ∨ x01 ∨ x04)
(¬x05 ∨ ¬x01 ∨ ¬x03)
Answer: {"satisfiable": false, "assignment": null}

Example 3. Variables x01–x06.
(¬x01 ∨ ¬x02 ∨ ¬x06)
(x05 ∨ ¬x03 ∨ x01)
(x01 ∨ ¬x02 ∨ ¬x05)
(x02 ∨ x01 ∨ x04)
(¬x04 ∨ x05 ∨ ¬x06)
(x05 ∨ x03 ∨ x06)
(¬x01 ∨ x03 ∨ ¬x02)
(¬x05 ∨ ¬x03 ∨ ¬x04)
(x05 ∨ ¬x06 ∨ x01)
(x05 ∨ x06 ∨ x02)
(x05 ∨ x06 ∨ ¬x01)
(x06 ∨ ¬x05 ∨ x02)
(x02 ∨ x03 ∨ x05)
(¬x06 ∨ ¬x05 ∨ ¬x01)
(¬x03 ∨ ¬x01 ∨ x04)
(x02 ∨ ¬x04 ∨ x01)
(¬x06 ∨ x01 ∨ x03)
(x06 ∨ ¬x01 ∨ x04)
Answer: {"satisfiable": false, "assignment": null}

Example 4. Variables x01–x06.
(¬x03 ∨ x02 ∨ ¬x01)
(x02 ∨ ¬x05 ∨ ¬x03)
(¬x05 ∨ ¬x03 ∨ ¬x02)
(x04 ∨ x06 ∨ x02)
(x06 ∨ x03 ∨ x04)
(¬x04 ∨ ¬x05 ∨ x06)
(¬x01 ∨ ¬x02 ∨ ¬x06)
(x03 ∨ ¬x02 ∨ ¬x04)
(x06 ∨ x02 ∨ ¬x03)
(x05 ∨ x02 ∨ ¬x03)
(¬x06 ∨ x04 ∨ x01)
(x03 ∨ x02 ∨ ¬x06)
(¬x02 ∨ x01 ∨ x05)
(¬x05 ∨ ¬x02 ∨ ¬x04)
(x06 ∨ ¬x03 ∨ ¬x05)
(¬x01 ∨ x05 ∨ ¬x04)
(x06 ∨ x02 ∨ x05)
(¬x03 ∨ x04 ∨ x05)
Answer: {"satisfiable": false, "assignment": null}

Example 5. Variables x01–x06.
(x01 ∨ ¬x05 ∨ x06)
(¬x05 ∨ x06 ∨ ¬x03)
(¬x04 ∨ ¬x01 ∨ ¬x06)
(¬x05 ∨ ¬x01 ∨ x03)
(x05 ∨ x03 ∨ x04)
(x02 ∨ x03 ∨ ¬x05)
(x02 ∨ x06 ∨ x01)
(¬x04 ∨ x02 ∨ ¬x01)
(¬x03 ∨ x04 ∨ x01)
(¬x03 ∨ ¬x04 ∨ x06)
(¬x06 ∨ ¬x05 ∨ x04)
(x03 ∨ ¬x01 ∨ ¬x04)
(x06 ∨ ¬x05 ∨ ¬x04)
(¬x03 ∨ x06 ∨ ¬x05)
(x05 ∨ ¬x06 ∨ x02)
(¬x02 ∨ ¬x05 ∨ x01)
(x04 ∨ x06 ∨ ¬x02)
(¬x04 ∨ ¬x01 ∨ x03)
(x06 ∨ ¬x05 ∨ x03)
(x04 ∨ x01 ∨ ¬x06)
(x02 ∨ x03 ∨ ¬x04)
(¬x06 ∨ x01 ∨ ¬x02)
(¬x02 ∨ ¬x05 ∨ ¬x03)
(¬x02 ∨ x06 ∨ ¬x05)
(x01 ∨ x02 ∨ ¬x03)
(x01 ∨ x06 ∨ x03)
(x01 ∨ ¬x06 ∨ x03)
(x06 ∨ ¬x04 ∨ ¬x02)
(x04 ∨ x06 ∨ x05)
(x02 ∨ x04 ∨ x01)
(¬x02 ∨ ¬x04 ∨ x06)
(¬x04 ∨ ¬x01 ∨ ¬x05)
(¬x04 ∨ ¬x06 ∨ ¬x01)
(x01 ∨ x04 ∨ x02)
(x01 ∨ ¬x02 ∨ x03)
(x04 ∨ x05 ∨ x06)
Answer: {"satisfiable": true, "assignment": "111001"}

Example 6. Variables x01–x06.
(¬x04 ∨ x05 ∨ ¬x03)
(¬x03 ∨ x01 ∨ x05)
(x04 ∨ ¬x03 ∨ x02)
(¬x04 ∨ x01 ∨ ¬x06)
(x05 ∨ ¬x04 ∨ x03)
(¬x01 ∨ x04 ∨ ¬x02)
(¬x03 ∨ ¬x02 ∨ ¬x01)
(¬x04 ∨ ¬x03 ∨ ¬x06)
(¬x01 ∨ x03 ∨ x04)
(x03 ∨ x05 ∨ x02)
(x01 ∨ x04 ∨ x05)
(¬x05 ∨ ¬x03 ∨ ¬x02)
(x04 ∨ ¬x03 ∨ x02)
(¬x02 ∨ x01 ∨ ¬x04)
(x04 ∨ ¬x03 ∨ ¬x05)
(¬x06 ∨ x04 ∨ ¬x05)
(¬x06 ∨ x02 ∨ x04)
(x05 ∨ ¬x06 ∨ ¬x02)
(¬x06 ∨ ¬x02 ∨ x04)
(x05 ∨ x03 ∨ ¬x04)
(x04 ∨ ¬x05 ∨ x01)
(¬x03 ∨ ¬x04 ∨ ¬x05)
(¬x04 ∨ x06 ∨ ¬x01)
(¬x06 ∨ ¬x03 ∨ x02)
(x04 ∨ ¬x06 ∨ x03)
(x01 ∨ x02 ∨ ¬x06)
(x05 ∨ ¬x02 ∨ ¬x04)
(x04 ∨ x03 ∨ ¬x06)
(x02 ∨ ¬x06 ∨ ¬x04)
(x02 ∨ ¬x03 ∨ ¬x01)
(x04 ∨ ¬x02 ∨ ¬x06)
(x05 ∨ x03 ∨ x06)
(x06 ∨ ¬x03 ∨ ¬x05)
(x05 ∨ x02 ∨ ¬x01)
(¬x05 ∨ ¬x02 ∨ ¬x01)
(x04 ∨ ¬x03 ∨ x06)
Answer: {"satisfiable": true, "assignment": "000110"}

Example 7. Variables x01–x06.
(¬x05 ∨ x01 ∨ ¬x04)
(x02 ∨ x05 ∨ x06)
(¬x01 ∨ ¬x03 ∨ ¬x02)
(¬x05 ∨ x02 ∨ x06)
(¬x03 ∨ ¬x06 ∨ x01)
(¬x04 ∨ x02 ∨ ¬x06)
(¬x01 ∨ x06 ∨ x02)
(¬x03 ∨ ¬x06 ∨ x04)
(x03 ∨ ¬x04 ∨ ¬x01)
(¬x04 ∨ ¬x03 ∨ ¬x05)
(¬x04 ∨ ¬x02 ∨ ¬x05)
(¬x03 ∨ x01 ∨ ¬x06)
(¬x03 ∨ ¬x05 ∨ ¬x02)
(¬x01 ∨ x02 ∨ x04)
(x02 ∨ x05 ∨ x03)
(x02 ∨ x01 ∨ ¬x06)
(x04 ∨ x06 ∨ ¬x05)
(x06 ∨ x05 ∨ x01)
(x03 ∨ ¬x06 ∨ ¬x05)
(¬x01 ∨ ¬x04 ∨ x05)
(x02 ∨ ¬x04 ∨ ¬x01)
(¬x04 ∨ ¬x03 ∨ ¬x02)
(¬x01 ∨ ¬x04 ∨ ¬x05)
(¬x01 ∨ ¬x03 ∨ x04)
(x05 ∨ ¬x03 ∨ ¬x06)
(¬x01 ∨ ¬x05 ∨ x02)
(¬x06 ∨ ¬x04 ∨ x01)
(x01 ∨ x03 ∨ ¬x02)
(¬x03 ∨ x04 ∨ ¬x02)
(¬x02 ∨ ¬x03 ∨ ¬x04)
(¬x04 ∨ ¬x06 ∨ x03)
(x04 ∨ x01 ∨ ¬x02)
(¬x05 ∨ x04 ∨ x01)
(x02 ∨ ¬x06 ∨ ¬x01)
(¬x03 ∨ x04 ∨ x01)
(¬x02 ∨ ¬x03 ∨ x04)
Answer: {"satisfiable": true, "assignment": "110000"}

Example 8. Variables x01–x06.
(x02 ∨ ¬x04 ∨ ¬x03)
(x06 ∨ ¬x05 ∨ x01)
(x02 ∨ ¬x01 ∨ x04)
(x03 ∨ ¬x02 ∨ x05)
(x01 ∨ ¬x03 ∨ ¬x05)
(¬x06 ∨ x03 ∨ x04)
(x06 ∨ x05 ∨ ¬x03)
(x01 ∨ x06 ∨ ¬x02)
(¬x05 ∨ ¬x01 ∨ x06)
(x04 ∨ ¬x02 ∨ x03)
(¬x05 ∨ ¬x04 ∨ x02)
(x01 ∨ x04 ∨ ¬x06)
(¬x03 ∨ x01 ∨ x05)
(x06 ∨ ¬x02 ∨ x04)
(¬x05 ∨ ¬x02 ∨ ¬x03)
(x04 ∨ x03 ∨ ¬x05)
(x06 ∨ x05 ∨ ¬x02)
(¬x05 ∨ ¬x02 ∨ ¬x03)
(x05 ∨ x04 ∨ x06)
(x06 ∨ x05 ∨ ¬x01)
(x04 ∨ x02 ∨ ¬x03)
(x04 ∨ x06 ∨ x01)
(¬x06 ∨ ¬x01 ∨ ¬x05)
(x02 ∨ ¬x05 ∨ x01)
(¬x03 ∨ x02 ∨ ¬x05)
(x04 ∨ x06 ∨ x05)
(x06 ∨ x05 ∨ ¬x04)
(x03 ∨ ¬x02 ∨ ¬x06)
(x01 ∨ x04 ∨ x02)
(x05 ∨ ¬x01 ∨ ¬x03)
(x02 ∨ x04 ∨ ¬x03)
(x05 ∨ x01 ∨ x03)
(x06 ∨ ¬x02 ∨ ¬x05)
(x03 ∨ x05 ∨ x04)
(¬x02 ∨ x06 ∨ x01)
(x05 ∨ x03 ∨ ¬x02)
Answer: {"satisfiable": true, "assignment": "100101"}

Now the problem to solve.
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x03 ∨ x04 ∨ ¬x06)
C02: (x08 ∨ ¬x07 ∨ ¬x05)
C03: (x01 ∨ x03 ∨ ¬x05)
C04: (x04 ∨ ¬x06 ∨ ¬x01)
C05: (x07 ∨ x05 ∨ x04)
C06: (x09 ∨ ¬x04 ∨ x01)
C07: (x09 ∨ x04 ∨ ¬x03)
C08: (x02 ∨ ¬x06 ∨ x03)
C09: (¬x01 ∨ x04 ∨ x02)
C10: (x09 ∨ ¬x07 ∨ ¬x01)
C11: (¬x10 ∨ ¬x08 ∨ x05)
C12: (x09 ∨ ¬x08 ∨ x04)
C13: (x03 ∨ ¬x06 ∨ x01)
C14: (¬x04 ∨ ¬x02 ∨ ¬x06)
C15: (x02 ∨ ¬x01 ∨ x05)
C16: (x03 ∨ ¬x05 ∨ ¬x04)
C17: (x06 ∨ ¬x04 ∨ x07)
C18: (x08 ∨ ¬x01 ∨ ¬x04)
C19: (x06 ∨ ¬x05 ∨ ¬x07)
C20: (¬x10 ∨ x07 ∨ x01)
C21: (¬x06 ∨ x03 ∨ x05)
C22: (x03 ∨ ¬x07 ∨ ¬x04)
C23: (¬x04 ∨ ¬x08 ∨ ¬x02)
C24: (¬x08 ∨ ¬x05 ∨ x04)
C25: (¬x10 ∨ x07 ∨ ¬x01)
C26: (x09 ∨ x07 ∨ ¬x06)
C27: (¬x02 ∨ x04 ∨ ¬x07)
C28: (¬x01 ∨ x07 ∨ x03)
C29: (¬x07 ∨ x01 ∨ x03)
C30: (x09 ∨ x07 ∨ x04)
C31: (x08 ∨ ¬x01 ∨ ¬x03)
C32: (¬x08 ∨ x01 ∨ x02)
C33: (x06 ∨ ¬x05 ∨ x04)
C34: (¬x10 ∨ x02 ∨ x01)
C35: (x03 ∨ ¬x05 ∨ x07)
C36: (¬x10 ∨ x04 ∨ ¬x07)
C37: (x03 ∨ x06 ∨ x01)
C38: (x07 ∨ ¬x03 ∨ ¬x06)
C39: (x03 ∨ x02 ∨ ¬x01)
C40: (¬x10 ∨ x05 ∨ x02)
C41: (¬x03 ∨ x01 ∨ ¬x07)
C42: (¬x06 ∨ ¬x04 ∨ x07)
C43: (¬x07 ∨ ¬x02 ∨ ¬x06)
C44: (x01 ∨ ¬x07 ∨ x08)
C45: (x03 ∨ ¬x07 ∨ ¬x06)
C46: (x09 ∨ x05 ∨ ¬x08)
C47: (¬x10 ∨ x01 ∨ x02)
C48: (x01 ∨ ¬x02 ∨ ¬x04)
C49: (¬x08 ∨ x05 ∨ ¬x01)
C50: (x06 ∨ ¬x05 ∨ ¬x03)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **I adaptive DENSITY:** SAT on K, UNSAT on J
- **A2 fixed DENSITY:** UNSAT on K, SAT on J (every environment)
- **exact:** SAT on both
- **A2 LENGTH-M:** the same on K and J
- *params:* `{"examples_alpha_g": [[3.0, false], [3.0, false], [3.0, false], [3.0, false], [6.0, true], [6.0, true], [6.0, true], [6.0, true]], "env": "R"}`
- *notes:* Dev-size examples (n = 6); test items are E2-SAT-K and E2-SAT-J.

</details>

<details><summary>Prompt and computed outputs — <code>E9-R-J</code></summary>

```text
Here are some solved examples.

Example 1. Variables x01–x06.
(¬x06 ∨ x03 ∨ x02)
(¬x03 ∨ ¬x06 ∨ x01)
(x03 ∨ x02 ∨ x06)
(x06 ∨ x02 ∨ x01)
(x03 ∨ ¬x02 ∨ x04)
(x01 ∨ ¬x02 ∨ x05)
(¬x04 ∨ x03 ∨ ¬x02)
(¬x03 ∨ x04 ∨ ¬x02)
(x04 ∨ ¬x02 ∨ ¬x06)
(¬x05 ∨ ¬x04 ∨ ¬x01)
(¬x03 ∨ x02 ∨ ¬x01)
(x06 ∨ ¬x01 ∨ ¬x05)
(¬x02 ∨ x05 ∨ x04)
(¬x03 ∨ ¬x01 ∨ x05)
(¬x03 ∨ ¬x04 ∨ ¬x05)
(x01 ∨ ¬x02 ∨ ¬x03)
(¬x04 ∨ x02 ∨ x03)
(¬x01 ∨ ¬x02 ∨ x05)
Answer: {"satisfiable": false, "assignment": null}

Example 2. Variables x01–x06.
(¬x01 ∨ ¬x04 ∨ x02)
(x05 ∨ ¬x04 ∨ x03)
(¬x04 ∨ x06 ∨ ¬x05)
(x03 ∨ x02 ∨ ¬x05)
(x01 ∨ ¬x06 ∨ ¬x02)
(¬x01 ∨ ¬x02 ∨ ¬x05)
(x04 ∨ x06 ∨ ¬x01)
(x01 ∨ ¬x05 ∨ x02)
(x06 ∨ x04 ∨ x02)
(x01 ∨ x04 ∨ ¬x05)
(¬x01 ∨ x06 ∨ x05)
(x06 ∨ x05 ∨ ¬x04)
(x05 ∨ ¬x06 ∨ ¬x03)
(¬x06 ∨ ¬x03 ∨ ¬x01)
(x05 ∨ x04 ∨ x03)
(x02 ∨ ¬x03 ∨ x01)
(x06 ∨ x01 ∨ x04)
(¬x05 ∨ ¬x01 ∨ ¬x03)
Answer: {"satisfiable": false, "assignment": null}

Example 3. Variables x01–x06.
(¬x01 ∨ ¬x02 ∨ ¬x06)
(x05 ∨ ¬x03 ∨ x01)
(x01 ∨ ¬x02 ∨ ¬x05)
(x02 ∨ x01 ∨ x04)
(¬x04 ∨ x05 ∨ ¬x06)
(x05 ∨ x03 ∨ x06)
(¬x01 ∨ x03 ∨ ¬x02)
(¬x05 ∨ ¬x03 ∨ ¬x04)
(x05 ∨ ¬x06 ∨ x01)
(x05 ∨ x06 ∨ x02)
(x05 ∨ x06 ∨ ¬x01)
(x06 ∨ ¬x05 ∨ x02)
(x02 ∨ x03 ∨ x05)
(¬x06 ∨ ¬x05 ∨ ¬x01)
(¬x03 ∨ ¬x01 ∨ x04)
(x02 ∨ ¬x04 ∨ x01)
(¬x06 ∨ x01 ∨ x03)
(x06 ∨ ¬x01 ∨ x04)
Answer: {"satisfiable": false, "assignment": null}

Example 4. Variables x01–x06.
(¬x03 ∨ x02 ∨ ¬x01)
(x02 ∨ ¬x05 ∨ ¬x03)
(¬x05 ∨ ¬x03 ∨ ¬x02)
(x04 ∨ x06 ∨ x02)
(x06 ∨ x03 ∨ x04)
(¬x04 ∨ ¬x05 ∨ x06)
(¬x01 ∨ ¬x02 ∨ ¬x06)
(x03 ∨ ¬x02 ∨ ¬x04)
(x06 ∨ x02 ∨ ¬x03)
(x05 ∨ x02 ∨ ¬x03)
(¬x06 ∨ x04 ∨ x01)
(x03 ∨ x02 ∨ ¬x06)
(¬x02 ∨ x01 ∨ x05)
(¬x05 ∨ ¬x02 ∨ ¬x04)
(x06 ∨ ¬x03 ∨ ¬x05)
(¬x01 ∨ x05 ∨ ¬x04)
(x06 ∨ x02 ∨ x05)
(¬x03 ∨ x04 ∨ x05)
Answer: {"satisfiable": false, "assignment": null}

Example 5. Variables x01–x06.
(x01 ∨ ¬x05 ∨ x06)
(¬x05 ∨ x06 ∨ ¬x03)
(¬x04 ∨ ¬x01 ∨ ¬x06)
(¬x05 ∨ ¬x01 ∨ x03)
(x05 ∨ x03 ∨ x04)
(x02 ∨ x03 ∨ ¬x05)
(x02 ∨ x06 ∨ x01)
(¬x04 ∨ x02 ∨ ¬x01)
(¬x03 ∨ x04 ∨ x01)
(¬x03 ∨ ¬x04 ∨ x06)
(¬x06 ∨ ¬x05 ∨ x04)
(x03 ∨ ¬x01 ∨ ¬x04)
(x06 ∨ ¬x05 ∨ ¬x04)
(¬x03 ∨ x06 ∨ ¬x05)
(x05 ∨ ¬x06 ∨ x02)
(¬x02 ∨ ¬x05 ∨ x01)
(x04 ∨ x06 ∨ ¬x02)
(¬x04 ∨ ¬x01 ∨ x03)
(x06 ∨ ¬x05 ∨ x03)
(x04 ∨ x01 ∨ ¬x06)
(x02 ∨ x03 ∨ ¬x04)
(¬x06 ∨ x01 ∨ ¬x02)
(¬x02 ∨ ¬x05 ∨ ¬x03)
(¬x02 ∨ x06 ∨ ¬x05)
(x01 ∨ x02 ∨ ¬x03)
(x01 ∨ x06 ∨ x03)
(x01 ∨ ¬x06 ∨ x03)
(x06 ∨ ¬x04 ∨ ¬x02)
(x04 ∨ x06 ∨ x05)
(x02 ∨ x04 ∨ x01)
(¬x02 ∨ ¬x04 ∨ x06)
(¬x04 ∨ ¬x01 ∨ ¬x05)
(¬x04 ∨ ¬x06 ∨ ¬x01)
(x01 ∨ x04 ∨ x02)
(x01 ∨ ¬x02 ∨ x03)
(x04 ∨ x05 ∨ x06)
Answer: {"satisfiable": true, "assignment": "111001"}

Example 6. Variables x01–x06.
(¬x04 ∨ x05 ∨ ¬x03)
(¬x03 ∨ x01 ∨ x05)
(x04 ∨ ¬x03 ∨ x02)
(¬x04 ∨ x01 ∨ ¬x06)
(x05 ∨ ¬x04 ∨ x03)
(¬x01 ∨ x04 ∨ ¬x02)
(¬x03 ∨ ¬x02 ∨ ¬x01)
(¬x04 ∨ ¬x03 ∨ ¬x06)
(¬x01 ∨ x03 ∨ x04)
(x03 ∨ x05 ∨ x02)
(x01 ∨ x04 ∨ x05)
(¬x05 ∨ ¬x03 ∨ ¬x02)
(x04 ∨ ¬x03 ∨ x02)
(¬x02 ∨ x01 ∨ ¬x04)
(x04 ∨ ¬x03 ∨ ¬x05)
(¬x06 ∨ x04 ∨ ¬x05)
(¬x06 ∨ x02 ∨ x04)
(x05 ∨ ¬x06 ∨ ¬x02)
(¬x06 ∨ ¬x02 ∨ x04)
(x05 ∨ x03 ∨ ¬x04)
(x04 ∨ ¬x05 ∨ x01)
(¬x03 ∨ ¬x04 ∨ ¬x05)
(¬x04 ∨ x06 ∨ ¬x01)
(¬x06 ∨ ¬x03 ∨ x02)
(x04 ∨ ¬x06 ∨ x03)
(x01 ∨ x02 ∨ ¬x06)
(x05 ∨ ¬x02 ∨ ¬x04)
(x04 ∨ x03 ∨ ¬x06)
(x02 ∨ ¬x06 ∨ ¬x04)
(x02 ∨ ¬x03 ∨ ¬x01)
(x04 ∨ ¬x02 ∨ ¬x06)
(x05 ∨ x03 ∨ x06)
(x06 ∨ ¬x03 ∨ ¬x05)
(x05 ∨ x02 ∨ ¬x01)
(¬x05 ∨ ¬x02 ∨ ¬x01)
(x04 ∨ ¬x03 ∨ x06)
Answer: {"satisfiable": true, "assignment": "000110"}

Example 7. Variables x01–x06.
(¬x05 ∨ x01 ∨ ¬x04)
(x02 ∨ x05 ∨ x06)
(¬x01 ∨ ¬x03 ∨ ¬x02)
(¬x05 ∨ x02 ∨ x06)
(¬x03 ∨ ¬x06 ∨ x01)
(¬x04 ∨ x02 ∨ ¬x06)
(¬x01 ∨ x06 ∨ x02)
(¬x03 ∨ ¬x06 ∨ x04)
(x03 ∨ ¬x04 ∨ ¬x01)
(¬x04 ∨ ¬x03 ∨ ¬x05)
(¬x04 ∨ ¬x02 ∨ ¬x05)
(¬x03 ∨ x01 ∨ ¬x06)
(¬x03 ∨ ¬x05 ∨ ¬x02)
(¬x01 ∨ x02 ∨ x04)
(x02 ∨ x05 ∨ x03)
(x02 ∨ x01 ∨ ¬x06)
(x04 ∨ x06 ∨ ¬x05)
(x06 ∨ x05 ∨ x01)
(x03 ∨ ¬x06 ∨ ¬x05)
(¬x01 ∨ ¬x04 ∨ x05)
(x02 ∨ ¬x04 ∨ ¬x01)
(¬x04 ∨ ¬x03 ∨ ¬x02)
(¬x01 ∨ ¬x04 ∨ ¬x05)
(¬x01 ∨ ¬x03 ∨ x04)
(x05 ∨ ¬x03 ∨ ¬x06)
(¬x01 ∨ ¬x05 ∨ x02)
(¬x06 ∨ ¬x04 ∨ x01)
(x01 ∨ x03 ∨ ¬x02)
(¬x03 ∨ x04 ∨ ¬x02)
(¬x02 ∨ ¬x03 ∨ ¬x04)
(¬x04 ∨ ¬x06 ∨ x03)
(x04 ∨ x01 ∨ ¬x02)
(¬x05 ∨ x04 ∨ x01)
(x02 ∨ ¬x06 ∨ ¬x01)
(¬x03 ∨ x04 ∨ x01)
(¬x02 ∨ ¬x03 ∨ x04)
Answer: {"satisfiable": true, "assignment": "110000"}

Example 8. Variables x01–x06.
(x02 ∨ ¬x04 ∨ ¬x03)
(x06 ∨ ¬x05 ∨ x01)
(x02 ∨ ¬x01 ∨ x04)
(x03 ∨ ¬x02 ∨ x05)
(x01 ∨ ¬x03 ∨ ¬x05)
(¬x06 ∨ x03 ∨ x04)
(x06 ∨ x05 ∨ ¬x03)
(x01 ∨ x06 ∨ ¬x02)
(¬x05 ∨ ¬x01 ∨ x06)
(x04 ∨ ¬x02 ∨ x03)
(¬x05 ∨ ¬x04 ∨ x02)
(x01 ∨ x04 ∨ ¬x06)
(¬x03 ∨ x01 ∨ x05)
(x06 ∨ ¬x02 ∨ x04)
(¬x05 ∨ ¬x02 ∨ ¬x03)
(x04 ∨ x03 ∨ ¬x05)
(x06 ∨ x05 ∨ ¬x02)
(¬x05 ∨ ¬x02 ∨ ¬x03)
(x05 ∨ x04 ∨ x06)
(x06 ∨ x05 ∨ ¬x01)
(x04 ∨ x02 ∨ ¬x03)
(x04 ∨ x06 ∨ x01)
(¬x06 ∨ ¬x01 ∨ ¬x05)
(x02 ∨ ¬x05 ∨ x01)
(¬x03 ∨ x02 ∨ ¬x05)
(x04 ∨ x06 ∨ x05)
(x06 ∨ x05 ∨ ¬x04)
(x03 ∨ ¬x02 ∨ ¬x06)
(x01 ∨ x04 ∨ x02)
(x05 ∨ ¬x01 ∨ ¬x03)
(x02 ∨ x04 ∨ ¬x03)
(x05 ∨ x01 ∨ x03)
(x06 ∨ ¬x02 ∨ ¬x05)
(x03 ∨ x05 ∨ x04)
(¬x02 ∨ x06 ∨ x01)
(x05 ∨ x03 ∨ ¬x02)
Answer: {"satisfiable": true, "assignment": "100101"}

Now the problem to solve.
Here is a Boolean formula in conjunctive normal form.
Variables: x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12, x13, x14, x15.
Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.

C01: (x03 ∨ x04 ∨ ¬x06)
C02: (x08 ∨ ¬x07 ∨ ¬x05)
C03: (x01 ∨ x03 ∨ ¬x05)
C04: (x04 ∨ ¬x06 ∨ ¬x01)
C05: (x07 ∨ x05 ∨ x04)
C06: (x12 ∨ ¬x04 ∨ x01)
C07: (x12 ∨ x04 ∨ ¬x03)
C08: (x02 ∨ ¬x06 ∨ x03)
C09: (¬x01 ∨ x04 ∨ x02)
C10: (x13 ∨ ¬x07 ∨ ¬x01)
C11: (¬x09 ∨ ¬x08 ∨ x05)
C12: (x13 ∨ ¬x08 ∨ x04)
C13: (x03 ∨ ¬x06 ∨ x01)
C14: (¬x04 ∨ ¬x02 ∨ ¬x06)
C15: (x02 ∨ ¬x01 ∨ x05)
C16: (x03 ∨ ¬x05 ∨ ¬x04)
C17: (x06 ∨ ¬x04 ∨ x07)
C18: (x08 ∨ ¬x01 ∨ ¬x04)
C19: (x06 ∨ ¬x05 ∨ ¬x07)
C20: (¬x09 ∨ x07 ∨ x01)
C21: (¬x06 ∨ x03 ∨ x05)
C22: (x03 ∨ ¬x07 ∨ ¬x04)
C23: (¬x04 ∨ ¬x08 ∨ ¬x02)
C24: (¬x08 ∨ ¬x05 ∨ x04)
C25: (¬x09 ∨ x07 ∨ ¬x01)
C26: (x14 ∨ x07 ∨ ¬x06)
C27: (¬x02 ∨ x04 ∨ ¬x07)
C28: (¬x01 ∨ x07 ∨ x03)
C29: (¬x07 ∨ x01 ∨ x03)
C30: (x14 ∨ x07 ∨ x04)
C31: (x08 ∨ ¬x01 ∨ ¬x03)
C32: (¬x08 ∨ x01 ∨ x02)
C33: (x06 ∨ ¬x05 ∨ x04)
C34: (¬x10 ∨ x02 ∨ x01)
C35: (x03 ∨ ¬x05 ∨ x07)
C36: (¬x10 ∨ x04 ∨ ¬x07)
C37: (x03 ∨ x06 ∨ x01)
C38: (x07 ∨ ¬x03 ∨ ¬x06)
C39: (x03 ∨ x02 ∨ ¬x01)
C40: (¬x11 ∨ x05 ∨ x02)
C41: (¬x03 ∨ x01 ∨ ¬x07)
C42: (¬x06 ∨ ¬x04 ∨ x07)
C43: (¬x07 ∨ ¬x02 ∨ ¬x06)
C44: (x01 ∨ ¬x07 ∨ x08)
C45: (x03 ∨ ¬x07 ∨ ¬x06)
C46: (x15 ∨ x05 ∨ ¬x08)
C47: (¬x11 ∨ x01 ∨ x02)
C48: (x01 ∨ ¬x02 ∨ ¬x04)
C49: (¬x08 ∨ x05 ∨ ¬x01)
C50: (x06 ∨ ¬x05 ∨ ¬x03)

Is there an assignment of truth values to the variables that satisfies every clause?
Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:
{"satisfiable": true, "assignment": "<one digit per variable, x01 first; 1 = true, 0 = false>"}
{"satisfiable": false, "assignment": null}
```

- **I adaptive DENSITY:** SAT on K, UNSAT on J
- **A2 fixed DENSITY:** UNSAT on K, SAT on J (every environment)
- **exact:** SAT on both
- **A2 LENGTH-M:** the same on K and J
- *params:* `{"examples_alpha_g": [[3.0, false], [3.0, false], [3.0, false], [3.0, false], [6.0, true], [6.0, true], [6.0, true], [6.0, true]], "env": "R"}`
- *notes:* Dev-size examples (n = 6); test items are E2-SAT-K and E2-SAT-J.

</details>

**Hypothesis matrix**

| Theory | (a) `E9-V-K` | (a) `E9-V-J` | (a) `E9-N-K` | (a) `E9-N-J` | (a) `E9-R-K` | (a) `E9-R-J` | (b) pure-theory statistic · weight resolution | (c) predicted trace |
|---|---|---|---|---|---|---|---|---|
| I adaptive DENSITY | UNSAT | UNSAT | K and J alike | K and J alike | SAT | SAT | Detectable π ≥ 0.04 vs exact | References to the examples' sizes or densities ('like example 3, which had many clauses and was unsatisfiable'). |
| A2 fixed DENSITY | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | Detectable π ≥ 0.01 vs I adaptive DENSITY | CUE-DENS without reference to the examples. |
| exact | SAT | SAT | SAT | SAT | SAT | SAT | Detectable π ≥ 0.04 vs I adaptive DENSITY | A completed procedure: a witness checked against every constraint, or a closed refutation / exhaustive case split. No cue given as a reason. |
| A2 LENGTH-M | the same on K and J | the same on K and J | the same on K and J | the same on K and J | the same on K and J | the same on K and J | Detectable π ≥ 0.04 vs A2 fixed DENSITY | CUE-SIZE as the reason ('with this many clauses it is very likely unsatisfiable'). |

*(c) for every theory: the expected share of traces showing the signature ≈ π_h · r̂ (faithfulness, from E8), plus the coder's false-positive rate.*

**Likelihood ratios per observable pattern** (log₁₀ LR; one study unit)

| Pattern | Favours (log₁₀ LR vs the best theory outside the favoured group) | Pushes toward zero weight (log₁₀ LR vs the best theory) |
|---|---|---|
| V: K UNSAT, J SAT | I adaptive DENSITY (+1.3), A2 fixed DENSITY (+1.3) | exact (-1.3), A2 LENGTH-M (-1.3) |
| V: K SAT, J UNSAT | exact (+1.3), A2 LENGTH-M (+1.3) | I adaptive DENSITY (-1.3), A2 fixed DENSITY (-1.3) |
| V: both SAT | exact (+1.3) | A2 LENGTH-M (-2.6), I adaptive DENSITY (-1.3), A2 fixed DENSITY (-1.3) |
| N: K UNSAT, J SAT | A2 fixed DENSITY (+1.3) | I adaptive DENSITY (-1.3), exact (-1.3), A2 LENGTH-M (-1.3) |
| N: K SAT, J UNSAT | I adaptive DENSITY (+1.3), exact (+1.3), A2 LENGTH-M (+1.3) | A2 fixed DENSITY (-1.3) |
| N: both SAT | I adaptive DENSITY (+1.3), exact (+1.3) | A2 LENGTH-M (-2.6), A2 fixed DENSITY (-1.3) |
| R: K UNSAT, J SAT | A2 fixed DENSITY (+1.3) | I adaptive DENSITY (-2.6), exact (-1.3), A2 LENGTH-M (-1.3) |
| R: K SAT, J UNSAT | I adaptive DENSITY (+1.3) | A2 fixed DENSITY (-2.6), exact (-1.3), A2 LENGTH-M (-1.3) |
| R: both SAT | exact (+1.3) | A2 LENGTH-M (-2.6), I adaptive DENSITY (-1.3), A2 fixed DENSITY (-1.3) |

**Weight resolution at study N**

| Theory | Nearest competitor (smallest KL) | Detectable π vs it (80% power) | Upper 95% bound on π if pure competitor | E[log₁₀ BF] vs competitor | Detectable π if the rest is the hardest base (which) | Identical predictions here |
|---|---|---|---|---|---|---|
| I adaptive DENSITY | exact | 0.043 | 0.028 | 230.2 | 0.043 (exact) | — |
| A2 fixed DENSITY | I adaptive DENSITY | 0.013 | 0.009 | 345.3 | 0.035 (A2 LENGTH-M) | — |
| exact | I adaptive DENSITY | 0.043 | 0.028 | 230.2 | 0.043 (I adaptive DENSITY) | — |
| A2 LENGTH-M | A2 fixed DENSITY | 0.035 | 0.023 | 345.3 | 0.035 (A2 fixed DENSITY) | — |

**Not separated here.** Exploratory; at the planned N only environment differences ≥ 0.2 are detectable.

