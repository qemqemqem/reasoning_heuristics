# Vertical: A (cue / substitution), H (guess / sample), nuisance models, I (strategy selection): the baselines

*One file for four groups, because together they make up the **null**: "the model isn't reasoning about this instance; it is answering from surface cues, from a constant, by guessing, or by running an exact procedure badly." Every other vertical has to beat what this file defines. Layout follows [TEMPLATE.md](TEMPLATE.md), expanded as the brief asked.*

- **Status:** designed (v0.2). Not piloted.
- **Owner:** [TODO]
- **Scope (Phase 1, per Andrew, 2026-11-13).**
  - Phase 1 is **behavioural only**.
  - **Primary condition:** open-weight reasoning models at best effort: high reasoning effort, thinking budget up to 32k tokens (`BE-32k`).
  - Direct-answer and non-thinking runs (`NT`) are diagnostic only.
  - Thinking budget (`B-4k`) is an experimental factor, not the default.
  - Interpretability (§3) is **Phase 2, and only if the behavioural evidence warrants it**.
- **Readout convention: graded weights** (per Andrew, 2026-11-13). Heuristics may be partly used, so nothing in this file is read as "used / not used". Every result is a quantity with an interval:
  - the mixture weight π_h (posterior mean and 95% interval);
  - the share of errors explained above chance (lift over the cue-stratified permutation baseline);
  - the log-likelihood gain or Bayes factor over the null B\* and over the nearest competitor;
  - for traces, the share matching h's signature, weighted by measured faithfulness r̂.

  Weights may depend on item features and on the model; that is family I (§5).

  An eval does not "support" or "refute" a member. It **moves weight** (Δπ), **bounds** a weight (e.g. π_competitor ≤ 0.1, upper 95%), or has **power** to detect a weight (π_h ≥ 0.15 at 80% power). "Disconfirming" a competitor means pushing its weight toward zero with a stated bound.

  The per-set likelihood ratios and weight resolutions are computed in [A_H_baselines_questions.md](A_H_baselines_questions.md). The coverage matrix is §2.9.
- **Sources.** Citations come from the repo's literature reports ([LITERATURE.md](../LITERATURE.md), [literature/](../literature/)) or were verified by fetching the arXiv abstract page this session; those are marked **[v]**. Numbers quoted only in agent reports are treated as leads.

---

## 0. What this vertical gives the other verticals

### 0.1 The baseline contract

Let **B\*** be the best-fitting mixture, with feature-dependent weights (§5), over A ∪ H ∪ nuisance ∪ {q}, where q is the "none of the above" model. Every other vertical's family claim must report three things, on the same items:

1. **Held-out log-likelihood gain over B\*.**
   - Measured per item, on the items where the family's best member and B\* disagree.
   - Uses a paired bootstrap over items.
   - The threshold δ is pre-registered (proposal: 0.02 nats/item).
2. **Error-agreement (EA) lift over a cue-stratified permutation baseline.**
   - DESIGN's permutation baseline permutes a heuristic's predictions across items "matched on item structure".
   - We make the matching explicit: permute within strata of the pre-registered cue vector ψ(x) (§1.4), so each stratum has the same cue values.
   - A structural heuristic whose predictions merely correlate with a cue then gets no lift.
3. **Consistency with E1.**
   - On minimal pairs where the model is shown to be structure-blind (E1), no structural family may claim the model's errors.

### 0.2 Channel-matched likelihoods

Many members here predict only a **projection** of the answer, called its *channel* κ_h(y). Examples:
- the decision bit (`DENSITY`);
- the conclusion's mood (`ATMOSPHERE`);
- the option position (`PRIMACY`).

Structural heuristics predict whole witnesses. Comparing a channel predictor with a witness predictor on full answers is biased one way or the other, depending on how the unpredicted part is filled. The rule:

- **Full-answer likelihood:** P(y | h, x) = P(κ_h(y) | h, x) · q_fill(y | κ_h(y), x).
  - q_fill is a shared reference fill: uniform over the witnesses consistent with the channel value.
  - For open entailment answers, q_fill is uniform over literal sets of the same size.
- **Every comparison is reported twice:**
  - (a) on the **decision channel alone**, since every family induces a decision;
  - (b) on **full answers** with q_fill.
- A claim such as "family X beats cue use" must hold under both.

### 0.3 Partial-input surrogate

S_ψ is a cross-validated (multinomial) logistic regression from the cue vector ψ(x) to **the model's answer**, not to g(x). It is the upper bound on what any combination of the listed cues explains. This is a hypothesis-only baseline in the sense of Poliak et al. 2018 **[v]**.

**Caveat** (Feng, Wallace & Boyd-Graber 2019 **[v]**): when a partial-input baseline does poorly, that does not show the cues are absent, because cues outside ψ remain possible. That is why E1 uses *invariance-defined* pairs. They neutralise every cue that is a function of the preserved statistics, listed or not.

---

## 1. The class

### 1.1 Defining ideas

- **A. Cue / substitution.** The answer is f(φ(x)) for an accessible, low-dimensional attribute φ: Kahneman & Frederick's attribute substitution (report F, [S]).
  - **A1:** f is constant.
  - **A2:** f is a threshold on a scalar φ.
  - **A3:** the answer is s(T(x)), where T substitutes a canonical (textbook) problem and s is an inner solver.
- **H. Guess / sample.** The answer is drawn from a simple distribution, optionally checked against the instance.
- **Nuisance.** An exact procedure corrupted by execution slips (`NOISY-EXACT`) or by misreading the input (`PERCEPTION-NOISE`). These are not heuristics. They are in the zoo so their errors are not credited to one (DESIGN O3; Sinha et al. 2025 on noisy execution).
- **I. Strategy selection.** Rice's algorithm selection (report F, [S]): mixture weights π_h(φ(x)) that depend on item features.

### 1.2 Taxonomy position and boundaries

Rows A, H, I and nuisance in PAPER_SKELETON Table 4. These boundaries are fixed now so that no behaviour is claimed twice:

| Behaviour | Owned by | Why it isn't ours |
|---|---|---|
| Positional selection of a premise, then exact inference on it | B1 `PREMISE-SUBSET(sel)` | Inference over the selected premises is a relaxation. `PRIMACY` here selects an *answer candidate* without inference. |
| Positional selection in constructive domains (take items or vertices in listed order) | C1 `INPUT-ORDER` / `FIRST-FIT` | Sequential construction |
| `FREQ` on the SAT witness (majority sign per variable) | C0 `POLARITY` | Same statistic. We use `FREQ` only on entailment and abduction answers. |
| Deterministic misreading by a selector rule (drop late edges; phantom edges between co-mentioned nodes) | B1 `DROP-CONSTRAINT` / B4 `ADD-CONSTRAINT` | Systematic. `PERCEPTION-NOISE` is random. E7 tells them apart by sample-to-sample and across-rendering consistency. |
| The default answer that `DPLL-b` gives when its budget runs out | D, composed with an A member | `DPLL-b`'s default *is* an A1 or A2 rule. We call this `D∘A`. E2 identifies the default, including on runs forced to answer at the 32k cap. |

### 1.3 Answer formats

These are shared with the other verticals. The final answer is JSON after the thinking trace.

| Domain | Format | Decision channel |
|---|---|---|
| SAT (3-SAT) | `{"satisfiable": true/false, "assignment": "0110…"}`. The assignment is over fixed-width names `x01…xNN`, and only when satisfiable is true. | satisfiable |
| COL (k-colouring decision; k given) | `{"possible": true/false, "colouring": {"Ann": 1, …}}` | possible |
| ENT-YN | `{"follows": true/false}` | follows |
| ENT-MC (K = 4) | `{"choice": "<label>"}` | — |
| ENT-OPEN | `{"conclusion": [literal, …]}` or `{"conclusion": "NOTHING"}`. It is the strongest conjunction of literals the model asserts follows; g(x) is the set of entailed literals (the backbone). | non-empty |
| KNAP | `{"items": [id, …]}` | — |
| ROUTE, ABD (secondary) | `{"tour": […]}` / `{"explanation": [h, …]}` or `"NONE"` | — |

**Response strata.** Every response is classed by how it ended:

- `COMPLETE`: the trace reaches its own verdict before the cap.
- `GIVEUP`: the trace stops of its own accord without completing a procedure (coded; §2.5).
- `CAPPED`: generation hit 32k. We then append `</think>` and the answer header, and decode at most 64 tokens. These are *forced* answers.
- `PARSE-FAIL`, `REFUSAL`, `DECLARED-IMPOSSIBLE` (DESIGN §5.5).

**Primary analyses use all responses, forced ones included.** Analyses that exclude capped runs (treated as censored) are sensitivity analyses.

Stratum-conditional analyses are descriptive only. Capping is a post-treatment variable, and its rate differs across counterfactual cells, so conditioning on it biases between-cell comparisons.

### 1.4 The pre-registered cue vector ψ(x)

ψ(x) is used for A2, for stratifying the permutation baseline, for the surrogate S_ψ, and as features for I.

- **SAT:**
  - n_decl, n_used, m;
  - α_U = m/n_used and α_D = m/n_decl;
  - prompt tokens;
  - number of negated literals;
  - maximum and minimum variable occurrence;
  - polarity skew Σ_v |pos_v − neg_v|;
  - number of pure variables;
  - clause negation-count histogram;
  - framing (CNF / natural language).
- **COL:**
  - |V_decl|, |V_used| (non-isolated vertices), |E|;
  - mean and maximum degree; k;
  - prompt tokens;
  - number of times each name is mentioned;
  - number of isolated vertices;
  - framing.
- **ENT:**
  - premise count, atom count, prompt tokens;
  - number of negations;
  - counts of `or` / `if` / `and`;
  - position of the categorical premise;
  - FREQ c(ℓ) for each signed literal.
  - For the conclusion C: token length, mood (form, polarity), maximum FREQ of its literals, and atom overlap with the first, last and categorical premises.
- **MC options:**
  - position and label;
  - token length;
  - FREQ score;
  - mood match;
  - overlap with the first and last premises.
- **KNAP:** n, capacity / total weight, prompt tokens.

### 1.5 Members, defined per problem model

**Conventions.**

- **Ties** are broken by earliest position in the input, then by lexicographic name. Options are ordered by displayed position.
- **"Positive"** means SAT / possible / follows.
- **Every A2 member is a soft threshold:** P(positive | x) = σ(s_h · (θ_h − φ_h(x))). The sign is chosen so that a larger cue means the negative answer: UNSAT / impossible / doesn't follow.
  - θ_h and s_h are fitted out of sample, per model × domain × condition: SAT/COL on the E3 sweep, ENT on a 50% calibration split.
  - The deterministic member is the limit s_h → ∞; at φ = θ it answers negative.
  - We also report the parameter-free **ecological** member θ\*_h = argmax_θ (accuracy on the generator distribution).
- **Witness fill.** A decision-only member that must output a witness fills it from q_fill (§0.2). This is the same fill `RANDOM` uses.

| Member | SAT | COL | ENT | KNAP / ROUTE / ABD | Channel |
|---|---|---|---|---|---|
| `ALWAYS-SAT` (A1) | SAT + fill | possible + fill | YN: follows (`ALWAYS-YES`) | — | decision |
| `ALWAYS-UNSAT` (A1; "give-up", Hazra's "UNSAT because complex") | UNSAT | impossible | YN: ≡ `NONE` | ROUTE: "infeasible" | decision |
| `NONE` (A1) | ≡ `ALWAYS-UNSAT` | ≡ `ALWAYS-UNSAT` | YN: doesn't follow; OPEN: NOTHING; MC: the "nothing follows" option if shown, else n/a | ABD: NONE | decision / full |
| `ECHO` (A1) | n/a | n/a | OPEN: the literal conjuncts of the categorical premise (the last one if several; premise 1 if none). YN: n/a, since our C is never a premise. | n/a | full |
| `DENSITY` (A2) | φ = α_U (`DENSITY-U`) or α_D (`DENSITY-D`) | φ = 2\|E\|/\|V_used\| (`-U`) or /\|V_decl\| (`-D`); θ depends on k | YN: φ = premises/atoms, and "follows" iff φ > θ (low prior) | n/a | decision |
| `LENGTH-PRIOR` (A2) | φ = m (`LENGTH-M`) or prompt tokens (`LENGTH-T`) | φ = \|E\| or tokens | YN: "follows" iff tokens(C) < θ. MC: choose the longest (`-LONG`) or shortest (`-SHORT`) option. | ROUTE: infeasible iff many stops | decision / option |
| `FREQ` (A2) | n/a (= C0 `POLARITY`) | n/a (= C1 `LARGEST-FIRST`) | c(ℓ) = occurrences of signed literal ℓ. OPEN: argmax_ℓ c(ℓ), all ties included; if ℓ and ¬ℓ are both maximal, keep the first mentioned. YN: follows iff min_{ℓ∈C} c(ℓ) ≥ θ (max for a disjunctive C). MC: argmax of the mean c over the option's literals. | ABD: the most-mentioned hypothesis | full / decision / option |
| `ATMOSPHERE` (A2) | n/a | n/a | atm(P) = (form, polarity). Form is the majority premise form in {conj, disj, cond}, ties → disj. Polarity is negative iff ≥ ½ of literal occurrences are negated. Monadic fragment: the classic rule (a negative premise gives a negative conclusion; a particular premise gives a particular one). YN: follows iff mood(C) = atm(P). MC: the option matching atm, else the fewest mismatches. | n/a | mood / decision / option |
| `PRIMACY` / `RECENCY` (A2) | n/a (→ C1) | n/a (→ C1) | MC: option at position 1 / K. YN: follows iff every literal of C occurs with the same sign in premise 1 / the last premise. OPEN: literal conjuncts of premise 1 / the last premise. | KNAP: n/a (→ C1). ABD: the first / last listed hypothesis. | option / decision / full |
| `LABEL-A` (nuisance-like token prior; Zheng et al. 2024 **[v]**) | — | — | MC: the option labelled "A" | — | option |
| `TEXTBOOK-TRANSFER` (A3) `TT[T, s]` | T: read the inverted clause rule as standard CNF | T: read "only friends may share" as "enemies may not share" (G instead of Ḡ) | T: read the redefined "either…or" (NOR) as inclusive OR | KNAP: covering → packing. ROUTE: longest → shortest tour. ABD: n/a. | full |
| `RANDOM-U` (H) | Bernoulli(½); assignment uniform on {0,1}ⁿ | uniform over k-colourings | YN: Bernoulli(½); MC: 1/K | uniform over subsets / tours | full |
| `RANDOM-B` (H; probability matching) | Bernoulli(p̂_m), where p̂_m is the model's marginal positive rate | same | same | — | decision |
| `SAMPLE-m` (H) | Draw m uniform assignments. SAT + the first satisfying one if any, else UNSAT. P(SAT) = 1 − (1 − s/2ⁿ)^m, with s = number of solutions. | same, over colourings | Draw m models of P uniformly from Mod(P). YN: follows iff C holds in all m, so P(follows) = (1 − ρ)^m, where ρ = \|Mod(P ∧ ¬C)\|/\|Mod(P)\|. OPEN: literals true in all m. MC: the option true in all m (ties → earliest). m is fitted as an integer, 1–64. | KNAP: best of m random feasible subsets | full |
| `NOISY-EXACT` (nuisance) | Decision: P(wrong) = ½(1 − (1 − p)^{L(x)}), with L = m (`-READ`) or instrumented MiniSat-style DPLL decisions + propagations (`-STEP`). Witness: P(y) ∝ max_{a∈Sol} p^{d(y,a)}(1 − p)^{n−d(y,a)}, with d_min computed by MaxSAT. | same; Hamming distance over colourings | YN: the same flip model. OPEN: drop each entailed literal w.p. p and add each non-entailed literal w.p. p (**symmetric**; contrast B1, omission only, and B4, commission only). | same | full |
| `PERCEPTION-NOISE` (nuisance) | x̃ ~ Π(x): drop each clause w.p. p_d; flip one literal's sign w.p. p_f; then y = g(x̃). `-POS`: p_d is U-shaped in position (cf. Liu et al. 2024 **[v]**). | drop each edge w.p. p_d; add a random non-edge w.p. p_a | drop a premise or flip a literal, then exact | drop or misread an item | full |

**Pseudocode for the members whose likelihood is non-trivial.**

```text
DENSITY-U(x):                           # SAT; COL is analogous with mean degree
    phi = m(x) / n_used(x)
    p_unsat = sigmoid(s * (phi - theta))     # theta, s fitted out of sample (E3)
    return {decision: UNSAT w.p. p_unsat; witness ~ q_fill if SAT}

SAMPLE-m(P, C):                         # ENT-YN; exact likelihood, no simulation needed
    rho = |Mod(P & ~C)| / |Mod(P)|           # enumeration (<= 10 atoms)
    return {follows: w.p. (1 - rho)^m}

TT[T, s](x):                            # A3; s defaults to exact, any zoo member allowed
    return s(T(x))                           # T is a fixed rewrite of the rule text's semantics

NOISY-EXACT-STEP(x):
    L = instrumented_dpll(x).steps
    return {decision: g(x) w.p. 1 - eps; flipped w.p. eps}, eps = 0.5 * (1 - (1-p)^L)

PERCEPTION-NOISE(x):                    # Monte-Carlo likelihood, 10^3 draws, plus exact
    x_tilde ~ Pi_{p_d, p_f, p_a}(x)          #   enumeration of 1-2 edits for small x
    return uniform over Sol(x_tilde), or UNSAT if Sol(x_tilde) is empty
```

**ROUTE and ABD.** Only definitions are given for now. Evals wait until those generators exist.

### 1.6 Expressibility (depth class)

- **A1:** constant.
- **A2:**
  - Counts, ratios and thresholds are majority-type, so constant-depth threshold circuits (TC⁰). Whether they are also in AC⁰ under constant precision is unverified (report F, Unverified).
  - `PRIMACY` / `RECENCY` / `LABEL-A` are positional selection: constant depth.
- **A3:** the rewrite T is a constant-depth relabelling, so the depth of `TT[s]` is the depth of s.
- **H:**
  - One `RANDOM` sample is constant depth.
  - `SAMPLE-m` checks m assignments against all constraints, which is m parallel AND-of-ORs: constant depth for fixed m.
  - Written out in a chain of thought, `SAMPLE-m` is sequential, with O(m · |constraints|) steps.
- **Nuisance:** inherits the depth of the exact procedure.
- **I:** the selector is constant depth (features → choice).

### 1.7 RASP-L sketch (pre-registered before any LLM data)

Lengths are my estimates in RASP-L primitives. The RASP vertical fixes the length measure (DESIGN O6) and will finalise these.

| Member | Program outline | Primitives / layers (estimate) |
|---|---|---|
| `ALWAYS-*` | constant map | 1 / 1 |
| `PRIMACY` (MC) | select the option-1 span, copy its label | 2 / 1 |
| `LENGTH-M` | indicator on clause-close tokens, then numeric aggregate (count), then threshold | 3 / 2 |
| `DENSITY-U` | clause count; first-occurrence indicator per variable (select same token earlier); aggregate (distinct count); ratio and compare in the MLP | 7 / 3 |
| `FREQ` (OPEN) | select same signed literal, aggregate (count), select-max, output | 5 / 3 |
| `ATMOSPHERE` | negation fraction (aggregate); form majority (3 aggregates); compare | 6 / 2 |
| `SAMPLE-m` | RASP-L is deterministic, so the counterpart is `FIXED-PROBE-m`: check m fixed assignments (all-true, all-false, alternating, …) | 4 + 2m / 3 |

**Prediction for O6** (to be tested by the RASP vertical): among class-C programs, `LENGTH-M` and `ALWAYS-*` are the shortest, but `DENSITY-U` is more accurate near threshold on natural random-3-SAT distributions. So `DENSITY-U` should sit on the length–error frontier for non-thinking runs.

---

## 2. Behavioural evidence (evals)

### 2.1 Models and conditions

**Primary models** (open weights, best effort; 12 models; **no tiny models**, so the smallest is 7–8B):

1. **gpt-oss-20b at high reasoning effort comes first.**
   - Every dev batch (§7) and the pilot run on it before any other model.
   - Its tokenizer is the first one the cue-matching checks (§2.6, E1 confound control) must pass.
   - Its `NT` diagnostic is low reasoning effort.
2. Then: gpt-oss-120b (high effort); Qwen3-14B, Qwen3-32B and Qwen3-30B-A3B in thinking mode; Qwen3-235B-A22B-Thinking; DeepSeek-R1; R1-Distill-Qwen-7B / 14B / 32B; R1-Distill-Llama-8B / 70B.

There are no sub-7B models, and no ladder extension below the 7B distills.

| Condition | Definition | Role | Models |
|---|---|---|---|
| `BE-32k` | High effort, thinking capped at 32k tokens, then a forced answer. Sampling at each model's recommended settings. | **Primary** | all |
| `B-4k` | Thinking budget forced at 4k (budget forcing, or gpt-oss low effort) | Budget factor, 30% subsets of E1–E3 | all |
| `NT` | Non-thinking: Qwen3 `/no_think`, gpt-oss minimal effort | Diagnostic, 30% subsets | Qwen3, gpt-oss only (R1 and the distills cannot turn thinking off) |

**Why the A/H nulls still matter at best effort.**

- A thinking model may search genuinely, fail, and then answer from a cue. `D∘A` predicts that.
- It may also answer from a cue and write a search-like trace afterwards. That is post-hoc rationalisation (Arcuschin et al. 2025; Cox et al. 2026, report C).
- Both put an A-family member in the answer channel above the budget line. Neither is visible in accuracy.

### 2.2 Predicted error signatures

| Member | Omission / commission | Feasibility of witness | Where it breaks |
|---|---|---|---|
| A1 | Wrong on the minority class, always. One-sided. | `ALWAYS-SAT`: random fill, so ≈ m/8 violated clauses | Nowhere specific: error rate = minority-class rate |
| A2 count cues | Wrong exactly where cue and truth disagree: SAT items at high α, UNSAT items at low α | random fill | A step at θ in cue coordinates, **fixed across n** (E3) |
| A2 positional | Wrong whenever the correct option is not at the favoured position | — | Position-only |
| A3 | Wrong on inverted items, with the textbook answer | Valid for T(x), invalid for x | Inverted framings only |
| `RANDOM` | Chance, two-sided | ≈ 1/8 of clauses violated (the 7/8 diagnostic; Håstad 2001, report F) | — |
| `SAMPLE-m` | Commission on items with rare counter-models (small ρ); false UNSAT on SAT items with few solutions | When it fails, its outputs look random | Knee where the solution density falls below 1/m, which moves to **lower α as n grows** |
| `NOISY-EXACT` | Two-sided, **symmetric** | Near-misses: few violations, located at random | Smooth growth with L(x), towards 0.5 |
| `PERCEPTION-NOISE` | One-sided under drops: UNSAT → SAT, not → possible | Valid for a perturbed instance; violations at misread constraints | Grows with m; positional if `-POS` |

### 2.3 Two design principles for discriminating items

**P1. Invariance pairs** (E1): g changes, every cue in an invariance class stays fixed.

- Edit x into x′ with an edit from a group G that preserves a large set of statistics. For SAT, the group is same-variable sign swaps between clauses whose negation counts differ by one.
- Every function of ψ is then equal on the pair, and so is **every unlisted cue that is a function of the preserved statistics**: per-variable polarity counts, the clause sign-pattern histogram, variable positions, token counts.
- The only things that differ are joint (clause, sign) structure, and therefore g.
- This is a contrast-set design (Gardner et al. 2020 **[v]**) made exact by construction, in the spirit of HANS (McCoy, Pavlick & Linzen 2019 **[v]**) and Zhang, Chen & Chen 2026's matched SAT/UNSAT pairs (report A).

**P2. Hardness-neutral cue moves** (E2): the cue moves; g and every structural competitor's prediction stay fixed.

- In natural random instances, α is confounded with every structural heuristic's hardness. Greedy, WalkSAT and `SAMPLE-m` all fail more often at high α.
- So a bare α effect cannot be credited to `DENSITY` (see also Verma 2026 on α being confounded with length; report A).
- We move α by adding **satisfiability-neutral padding**: clauses that contain a pure literal of a fresh variable.
  - After pure-literal elimination, every padded instance reduces to its own core.
  - The decision is unchanged, and so is the hardness for any solver that handles pure literals.

### 2.4 Manipulation signatures (template table)

Notation: = no change; ↑ / ↓ direction of the error or answer rate; ↕ the answer moves with the manipulated item; ✓ applies.

| Manipulation | A1 | A2 count cues | A2 positional | A3 `TT` | `RANDOM` | `SAMPLE-m` | `NOISY-EXACT` | `PERCEPTION-NOISE` | Nearest competitors |
|---|---|---|---|---|---|---|---|---|---|
| Premise / constraint order reversed | = | = | ↕ | = | = | = | = | = (↕ if `-POS`) | C1, C4, B4-ETR ↕; D = |
| Re-themed / renamed (token-matched) | = | = | = | ↕ (the further from textbook, the less `TT`) | = | = | = | = | all = |
| Rule inverted | = | = | = | **↑, with the textbook answer** | = | = (it checks the stated rule) | slight ↑ (longer prompt) | ↑ only if the rule is misread | exact = |
| Irrelevant constraint added (satisfiability-neutral padding) | = | **moves with φ** (E2) | ↕ if the padding sits at an end | = | = | ↓ SAT rate (more variables to guess) | `-READ` ↑ symmetric; `-STEP` = | slight ↑ | pure-literal-aware D / B1 / C0: = |
| Size / density ↑ | = | knee fixed at θ in φ | = | = | = | knee drifts to lower α | smooth ↑ towards 0.5 | ↑ with m | C: knee near the algorithmic threshold (UC ≈ 8/3, myopic 3.26; report F); D: ↑ above n\* |
| Thinking budget ↑ | = | = if fixed; ↓ weight if selection is adaptive (I) | = | = or ↓ | = | m ↑, so the ρ-curve steepens | `-STEP`: error ↓ only if p falls | = | D: b ↑; F: k ↑ |

### 2.5 Trace protocol (used by every eval)

The thinking trace is a second channel. We treat it as **unreliable evidence**:

- Hint use is verbalised only about 25% of the time in Claude 3.7 Sonnet and 39% in R1 (Chen et al. 2025).
- Answers are often decodable before the chain of thought, and steering them yields confabulated traces (Cox et al. 2026).
- Both are in report C.

Trace evidence therefore **never establishes a member on its own** (§2.5.5).

#### 2.5.1 Codebook

This codebook should be shared across verticals; we list the full event inventory, because competitor predictions need it. Each code is an **event** with a character span.

| Code | Meaning | Main family | Extraction |
|---|---|---|---|
| `CUE-DENS` | Cites ratio, density, "many constraints per variable", "over-constrained" as a reason | A2 `DENSITY` | lexicon + LLM |
| `CUE-SIZE` | Cites size or complexity ("too many rules", "large") as a reason | A2 `LENGTH` | lexicon + LLM |
| `CUE-FREQ` | Cites how often a literal or name appears as a reason | A2 `FREQ` | LLM |
| `CUE-POS` | Cites position ("the first option", "the last statement") as a reason | A2 `PRIMACY`/`RECENCY` | lexicon + LLM |
| `CUE-MOOD` | Matches the conclusion's form or polarity to the premises without a derivation | A2 `ATMOSPHERE` | LLM |
| `ECHO` | The conclusion restates a premise | A1 `ECHO` | automatic (string/logic match) |
| `GIVEUP` | Stops without finishing a procedure, then asserts a verdict with hedging ("likely", "probably") | A1 / `D∘A` | LLM + automatic (no closed refutation) |
| `REFRAME` | Paraphrases the rule; sub-code `textbook` / `as-stated` / `absent` | A3 | LLM + automatic check of constraint-check semantics |
| `SAMPLE(k)` | Tests k specific cases, non-exhaustively, and generalises | H `SAMPLE-m` | automatic (parse the cases) + LLM |
| `ASSIGN` | Assigns a variable or colour | C/D/F | automatic parser |
| `PROP` | Derives a forced value ("so x07 must be 0") | B1/D/E | automatic + replay check |
| `BRANCH` | Case split or supposition | D | lexicon + LLM |
| `CONTRA` | Detects a contradiction | D/B1 | lexicon + replay |
| `BACKTRACK` | Revises an earlier assignment after a contradiction | D | automatic (assignment reversal after `CONTRA`) |
| `REPAIR` | Proposes a full candidate, lists violations, flips | F | automatic + LLM |
| `COMMIT-DISJ` | Picks one disjunct and never revisits it | B4 `FIRST` | LLM |
| `TRUE-ONLY` | Lists only the true cases of each premise | B4 `MM` | LLM |
| `VERIFY(c)` | Checks a candidate against c constraints | all | automatic |
| `DECOMP` | Splits the instance into independent parts | G | LLM |
| `MISQUOTE` | A quoted constraint ≠ the instance (sign, pair or premise) | `PERCEPTION-NOISE` | **automatic** (quote extraction + diff) |
| `EVALSLIP` | Evaluates a constraint wrongly under the trace's own stated assignment | `NOISY-EXACT` | **automatic** (replay) |
| `OPT-EVAL(order, stop)` | The order in which MC options are evaluated, and where evaluation stops | A2 positional | automatic |

#### 2.5.2 Automatic parsers

Implemented first, and validated against the hand-labelled subset (precision and recall per code reported). They cover:

1. **Assignment and colour events.** Grammar over `x07 = 1 | true | T`, "Ann → room 2", and so on.
2. **Quoted constraints.** Clause, edge and premise regexes, then a diff against the instance, which gives `MISQUOTE`.
3. **Replay.** Re-execute the trace's stated assignments and claimed evaluations against the instance. This gives `EVALSLIP` and `PROP` validity, and tells whether a refutation is closed.
4. **Option-evaluation order** in MC, giving `OPT-EVAL`.
5. **Keyword lexicons**, pre-registered per code.
6. **Final committed state**: the last full assignment, the derived-literal set, or the accepted option, plus the answer that state implies.

#### 2.5.3 LLM-assisted coding

The coder is a fixed open-weight model, run non-thinking, with a frozen codebook prompt and a pinned version.

**What the coder sees:**
- **Blinded:** it sees the trace and the vocabulary. It does *not* see g(x), the counterfactual cell, the pair partner, or the model's identity. This follows DESIGN §5.4's rule that a translator never sees premises.
- **Chunked:** traces are coded in 4k-token windows with 512-token overlap, and events are merged.
- **Spans checked:** each event must cite a span. Spans that don't exist verbatim are dropped (no hallucinated quotes).

**Coverage:** 100% of traces get automatic parsing. 25% of `BE` traces, stratified by model × eval cell, get LLM coding, plus 100% of the traces in E1 critical pairs and E5.

**Hand-labelled validation:**

- **Sample:** 150 traces per domain (SAT, COL, ENT), stratified by model and cell.
- **Procedure:**
  - Two human coders work independently, blind as above.
  - Each codes a random 2k-token window plus the final 1k tokens of each trace, since full 20k traces are too costly to code.
  - Disagreements are adjudicated.
- **Statistics:** Cohen's κ per code for human–human and for LLM–adjudicated.
- **Acceptance rule:** a code is used from the LLM coder only if both hold:
  - κ(LLM, adjudicated) ≥ 0.70, and no lower than the human–human κ minus 0.10;
  - **differential error** across counterfactual cells is ≤ 5 pp. Otherwise coder error could manufacture a between-cell effect.

  Codes that fail are reported from the human-coded subset only.

#### 2.5.4 Faithfulness tests

These are E8. They give a per-model × domain faithfulness index r̂ ∈ [0, 1] from:

1. **Trace–answer consistency.** Does the answer implied by the trace's final committed state equal the final answer?
2. **Early answering** (Lanham et al. 2023, report C). Truncate the trace at fraction f and force an answer.
3. **Mistake insertion** (Lanham et al. 2023). Corrupt one derived fact and continue the generation.
4. **Trace transplant.** Splice the trace from one version of an item into the prompt of its cue-shifted twin, then force an answer.

#### 2.5.5 How trace and answer evidence combine (pre-registered)

- **Answer evidence is primary.** It is machine-scored and enters the evidence table.
- **Trace evidence is a second likelihood,** down-weighted by reliability. This follows Glöckner's multiple-measure method (report B) with an explicit unfaithful component:
  - P(codes | h) = r̂ · P(codes | h, faithful) + (1 − r̂) · P(codes | generic),
  - and the joint fit is L(h) = Π_x P(y_x | h) · P(t_x | h)^{r̂}.
  - Answer-only and joint fits are both reported.

Both channels give graded quantities:

- the answer-channel weight **π_h^ans** (posterior mean, 95% interval) from the I-model on answers;
- the trace share **s_h** = (traces coded with h's signature) / (traces), corrected for the coder's false-positive rate and divided by r̂. That gives the trace-implied weight **π_h^tr ≈ (s_h − fp_h) / r̂**.

The reported weight is the answer-channel weight, with the joint-fit weight next to it.

| Answer channel | Trace channel | r̂ | What is reported |
|---|---|---|---|
| π_h^ans interval excludes 0 | π_h^tr inside π_h^ans's interval | any | π_h^ans with the joint-fit interval, which is narrower; "the channels converge" |
| π_h^ans interval excludes 0 | π_h^tr ≈ 0 (another procedure is described) | ≥ 0.7 | **Conflict.** Report both. Then run E8 on the items carrying h's weight. If the answer is insensitive to trace edits there and predictable at f = 0, report "π_h^ans, with a decorative trace". If it is sensitive, the described procedure coincides with h on those items, so report h and that procedure as a merged composite (not separately identified). |
| π_h^ans interval excludes 0 | anything | < 0.7 | π_h^ans only; the trace channel gets weight r̂ in the joint fit and is reported as uninformative |
| π_h^ans upper 95% ≤ 0.05 | π_h^tr large (e.g. density talk) | any | π_h bounded ≤ 0.05; the cue talk is reported as a rationalisation rate (s_h), not as weight |
| interval wide (includes 0 and ≥ 0.2) | π_h^tr large | ≥ 0.7 | The joint fit may narrow the interval. The weight is reported only if the pre-registered joint log-likelihood gain is met. |

---

### 2.6 The evals

The table after E9 summarises them. Each eval runs under `BE-32k`, unless a subset is stated, and on every primary model.

---

#### E1. Structure-blindness minimal pairs (g flips; every cue in an invariance class fixed)

**Question.**

> On near-threshold items, are the model's decisions **blind to the structural difference that decides g**, once every surface statistic is held fixed?

Quantity estimated, per model × domain × size: the null-corrected directed discordance D̂ − D̂_null, which lower-bounds the total weight on structure-reading families (B1 with derivations, C, D, E, F, exact).

If the estimate is near 0, with upper 95% ≤ 0.075, almost all weight on those items sits on blind members: A, H, C0, and B1 on random instances. E2–E7 then apportion it.

**Design.**

For each domain, pairs (x, x′) are built with an edit from the invariance group:

- **SAT** (n ∈ {16, 24, 36}, α ∈ {4.0, 4.26, 4.5}):
  - Choose a variable v, a clause i where v occurs positively and a clause j where v occurs negatively, with neg(j) = neg(i) + 1. Flip both occurrences.
  - Preserved exactly:
    - n, m, α, prompt tokens;
    - each variable's polarity counts, so `FREQ`, `POLARITY`, `MOMS` and `PURE-LITERAL` are unchanged;
    - the clause negation-count histogram, so the validity of the all-true and all-false assignments is unchanged;
    - the positions of all variables.
  - **Critical pairs:** g(x) = SAT, g(x′) = UNSAT.
  - **Null pairs:** the same kind of edit with g unchanged (SAT→SAT and UNSAT→UNSAT).
- **COL** (n ∈ {15, 20, 30}, k = 3, mean degree ≈ 4.4):
  - A double-edge swap (a,b),(c,d) → (a,d),(c,b), made in place in the edge list.
  - Preserved: the degree sequence, |E|, the vertex-list order (and with it `FIRST-FIT` order), tokens, and how often each name is mentioned.
  - Critical: G is 3-colourable and G′ is not. Null: colourability unchanged.
- **ENT** (6 / 8 / 10 atoms; 4–7 premises; question "Does it follow that C?"):
  - Swap a negation between two occurrences of the same atom v ∉ atoms(C), in two different premises, with the same negation-count condition as SAT.
  - Preserved: signed-literal FREQ, the negation count, connective counts, premise positions, and C's atom overlap with every premise.
  - Critical: P ⊨ C and P′ ⊭ C.
  - The pairs are stratified by two quantities:
    - C's propagation depth in P, counted in unit-propagation steps beyond the stated facts (1, 2, ≥ 3, or not UP-derivable). `UP-k` derives C iff the depth is ≤ k;
    - ρ′ = the counter-model fraction of C in P′.

  This stratification is what separates B1 and `SAMPLE-m` from exact.

**Statistic.**
- D = P(y = pos, y′ = neg) − P(y = neg, y′ = pos), computed on critical pairs in the g direction. This is McNemar's (b − c)/N.
- The total discordance on critical pairs is compared with null pairs and with test–retest (a second sample on 25% of items).

**Answer predictions** (D on critical pairs). "item" means computed per pair by running the reference implementation; the table gives the expected value.

| Family / member | SAT | COL | ENT |
|---|---|---|---|
| A1 (all) | 0 | 0 | 0 |
| A2 (`DENSITY`, `LENGTH`, `FREQ`, `ATMOSPHERE`, `PRIMACY`/`RECENCY`) | 0: equal by construction | 0 | 0 |
| A3 `TT` | 0 (textbook framing) | 0 | 0 |
| H `RANDOM` | 0 | 0 | 0 |
| H `SAMPLE-m` | ≈ m·s(x)/2ⁿ ≈ 0 for n ≥ 16 | ≈ 0 | 1 − (1 − ρ′)^m: small in the ρ′ ≤ 1/8 stratum, large at ρ′ ≥ ½ |
| `NOISY-EXACT` | 1 − ε(x) − ε(x′): large below n\*, → 0 as L grows | same | same |
| `PERCEPTION-NOISE` | P(x′ stays UNSAT under drops) ≈ (1 − p_d)^{\|N(x′)\|}, where N = clauses in every MUS | same, with critical edges | P(misread P′ still ⊭ C) |
| B1 `UP-k` / `2SAT-CORE` | ≈ 0 (no units or binaries in random 3-SAT) | n/a | **> 0 only in the UP-depth ≤ k strata** |
| B1 `DROP-CONSTRAINT(sel)` | — | 0 on pairs where the selector drops the swapped-in edge; otherwise item (edited positions are balanced across early/middle/late) | — |
| B4 (polarity-restrict; `ADD-CONSTRAINT`; `FIRST`, `MATCH`, `ETR`, `MM`) | small, item | item (phantom edges can make both members impossible, giving 0) | item (PyETR for `ETR`) |
| C (`GREEDY`, `UC`; `FIRST-FIT`, `DSATUR`) | P(greedy solves x), item | P(greedy 3-colours G), item | — |
| D `DPLL-b` | ≈ P(both members within b nodes): rises with budget | same | same (exhaustive case split) |
| E `WP-t`/`BP-t`; `LOCAL-t` | item | item | item (on the SAT encoding) |
| F `WALK-k` / `MIN-CONFLICTS` (default "no") | P(it finds a solution of x within k), item | same | — |
| G | n/a (random instances don't decompose) | n/a | n/a |
| Exact | 1 | 1 | 1 |

**Trace predictions** (per pair, comparing x with x′).

| Family | Trace content | Divergence between the x and x′ traces |
|---|---|---|
| A1 / A2 | `CUE-*` and `GIVEUP` equally often in both; the UNSAT member contains no closed refutation | No more than test–retest; nothing local to clauses i, j |
| H `SAMPLE-m` | `SAMPLE(k)` with the same k in both; "none of these work" leads to UNSAT | ≈ test–retest |
| `NOISY-EXACT` | Systematic search in both; an `EVALSLIP` at a random step decides the error | Divergence at i, j (structure is read) |
| `PERCEPTION-NOISE` | In an erring x′, a `MISQUOTE` of a clause in N(x′) | At the misquoted clause |
| B1 | `PROP` only; ENT: a derivation chain to C in P, which stops in P′ | At the swapped literal, in the propagation chain |
| B4 | `COMMIT-DISJ` / `TRUE-ONLY`; no revisits | Only where the committed disjunct contains v |
| C | One pass of `ASSIGN`, no `BACKTRACK`; in x′, a dead end then `GIVEUP` or an invalid answer | At the first clause, i or j, that the pass reaches |
| D | `BRANCH`, `CONTRA`, `BACKTRACK`; the x′ trace is longer and ends in a closed refutation or the cap | At a `CONTRA` involving clause i or j |
| F | `REPAIR` loops; in x′ they never converge, giving a long trace and the cap | Repeated violations of i or j |

Measures: (i) whether either trace mentions the literals of clauses i and j (automatic); (ii) whether their evaluation differs (replay); (iii) the token difference within the pair, compared with null pairs.

**Confound control.**

- **Tokens:** identical by construction. The negation is one fixed token sequence, and fixed-width names (`x07`, single-token people's names, checked against each tokenizer: Qwen3, gpt-oss, DeepSeek, Llama) keep per-name tokens constant. Qwen splits digits, so `x9` and `x12` would differ.
- **Entity names:** identical within a pair.
- **Positions:** identical (in-place edits).
- **Answer format:** identical.
- **Framing:** CNF for half the base items, natural language (Hazra et al.'s "Menu"-style; report A) for the other half. Framing is a between-item factor and an I feature.

**Generator recipe.**

1. Sample a random 3-SAT base (or G(n, p) graph, or ENT premise set from a v1-style generator over 6–10 atoms).
2. Enumerate admissible edits (SAT: about 200 per formula).
3. Solve x′ with PySAT, or z3 for ENT.
4. Keep the edit if it is critical or null as required.
5. **Assert** that every A member and every C0 member gives the same prediction on both members (feature-vector equality plus reference-implementation runs). Reject the pair otherwise.
6. ENT only: reject if C is a premise, or if v ∈ atoms(C).
7. Balance the critical pairs across sizes and the ENT strata. At most one pair per base, to avoid dependence.

**Format, metric, criteria.**
- Formats as in §1.3, on the decision channel.
- Metrics: D and its CI; McNemar exact test; TOST.
- Sizes, framing and models are pooled in a mixed logistic model: y ~ member × pairtype × size + (1 | pair) + (1 | model).
- **Weight readout.**
  - E[D] = Σ_h π_h D_h. Structure-blind members (A1, A2, H, C0, and B1 on random 3-SAT) have D_h = 0; exact has D_h = 1; the others have D_h computed per pair (table above). So the null-corrected D̂ − D̂_null is a **lower bound on the total weight of structure-reading families**: π_struct ≥ D̂ − D̂_null, since D_h ≤ 1.
  - The I-model apportions that weight among members using the pair-level predictions and the error side:
    - SAT-side errors: C, F, D with a default of "UNSAT";
    - UNSAT-side errors: `PERCEPTION-NOISE`, B1, `ALWAYS-SAT`;
    - symmetric errors: `NOISY-EXACT`.
  - The witness channel on x separates `C0 POLARITY` and C/D, which give their own witnesses, from fill-based members. The UP-refutable stratum separates B1.
- **Resolution at the planned N** (400 critical pairs; computed in the question library):
  - SE(D̂) ≈ 0.025, so π_struct ≥ 0.07 is detected with 80% power.
  - Under a structure-blind model, the bound is π_struct ≤ 0.075 (upper 95%).
  - Within the blind group, the decision channel gives no resolution among `ALWAYS-SAT`, `DENSITY`, `LENGTH`, `POLARITY` and UP on random 3-SAT, because their pair distributions are identical. The witness channel and E2/E3 provide it.
  - Per-member resolution in the dev library (E1-SAT, detectable π vs the nearest competitor):
    - `C0 POLARITY` 0.01, through its own witness;
    - `ALWAYS-SAT`, `DENSITY` and B1 UP-3 0.09, through the UP-refutable stratum;
    - D 0.09; `NOISY-EXACT` 0.13; `PERCEPTION-NOISE` 0.17;
    - C1, F and exact ≈ 0.24–0.27, because at n = 12 greedy and WalkSAT rarely fail. They separate better at the study sizes.
- Weights are reported per model × size. A model may put most of its weight on blind members at n = 36 and on exact at n = 16. That is the budget line expressed as weights, and I models it with log n as a feature.

**Power.**
- McNemar for D, with expected total discordance p_d ≈ 0.25: n ≈ [z_{α/2}√p_d + z_β√(p_d − D²)]² / D².
  - D = 0.07, α = 0.05, power 0.8 gives n ≈ 400 critical pairs.
- The same 400 pairs give a TOST equivalence bound of (1.645 + 1.28)·√(0.25/400) ≈ 0.073.
- So each domain has 400 critical + 200 null pairs = **1,200 items**, per model, at a single condition.
- Per-size estimates (≈ 133 critical pairs each) detect D ≈ 0.12.

**Threats to validity.**

1. **The edit preserves cues outside our list, but not every conceivable cue.** A model could react to local co-occurrence, e.g. "v appears negated next to x12".
   - Mitigation: null pairs use the same edit type, so any edit-sensitivity that is not about g shows up as symmetric discordance and is subtracted.
2. **Ceiling at small n.** At n = 16, best-effort models may solve both members, so D ≈ 1. That isn't a threat; it locates n\*. The A-family claim is made only at sizes where D is small.
3. **Capping differs between members.** UNSAT members are capped more, and their answers are forced.
   - Primary analysis keeps forced answers. A sensitivity analysis treats capped runs as censored.
   - A difference in capping rate is itself structure sensitivity (it's a process-channel D).
4. **Pair dependence through base items.** At most one pair per base.

---

#### E2. Hardness-neutral cue moves (the cue moves; g and structural competitors fixed)

**Question.**

> Does moving a cue φ, while holding g and every pure-literal-aware structural prediction fixed, move the answer in the direction and by the amount the cue model fitted on E3 predicts?

Example: is "unsatisfiable" said more often when α rises at fixed clause count m and fixed hardness? This test separates `DENSITY` from `LENGTH`, from `SAMPLE-m`, and from noise.

**Design (SAT).**

- Base core: n = 24, α = 4.2, m = 101 (300 bases; 150 SAT, 150 UNSAT).
- Four padding levels:

| Level | Construction | n_used / n_decl | m | α_U | α_D |
|---|---|---|---|---|---|
| base | core | 24 / 24 | 101 | 4.21 | 4.21 |
| **K** | +28 clauses (fresh literal, core literal, core literal). Fresh literals come from **3** fresh pure variables (≈ 9 clauses each). | 27 / 27 | 129 | 4.78 | 4.78 |
| **J** | The **same** 28 clauses with the **same** core literals in the same positions. Fresh literals come from **10** fresh pure variables (≈ 2.8 clauses each). | 34 / 34 | 129 | 3.79 | 3.79 |
| **U** | core + 8 declared but unused variables | 24 / 32 | 101 | 4.21 | 3.16 |

- In both K and J, 14 of the 28 fresh literals are negated. Fresh variables are pure with planted signs, so the padding is satisfiable whatever the core's assignment.
- K versus J is the key contrast. It moves α by about 1 at fixed m, with the same core-literal noise and the same positions, and both reduce to the same core after pure-literal elimination.

**Design (COL).**
- Base: n = 20, |E| = 44, mean degree 4.4.
- K: add K_{3,3,3}, giving |E| = 71, n = 29, mean degree 4.9.
- J: add a 27-edge tree on 28 new vertices, listed in BFS order. This gives |E| = 71, n = 48, mean degree 2.96.
- U: add 8 isolated declared people.
- New edges are interleaved at the same positions in K and J; only the endpoints differ. New names are interleaved in the people list.
- The decision is unchanged, since the added component is disconnected and 3-colourable.

**Design (ENT): matched conclusion sets.**
- For each premise set (200 sets, 6–8 atoms), choose 8 conclusions in a 2 (g) × 2 (`FREQ` high / low) × 2 (`ATMOSPHERE` match / mismatch) design.
- `FREQ` high means f(C) ≥ 3 and low means f(C) ≤ 1, where f(C) is the minimum count c(ℓ) over a conjunction's literals and the maximum over a disjunction's. That is the statistic `FREQ` thresholds, so the cells straddle any θ in (1, 3).
- The conclusions must be matched on:
  - token length (±1 token);
  - overlap with the first, last and categorical premises;
  - UP-depth (for entailed C);
  - ρ and the perception fragility κ (for non-entailed C; see E6);
  - the PyETR prediction, which must be equal within each g level, or else counterbalanced across sets.
- So the cues vary **within one premise set**, and premise-level confounds cancel.

**Answer predictions** (SAT; sign of Δ P(UNSAT) relative to base, on both SAT and UNSAT bases).

| Member | K | J | U | K − J |
|---|---|---|---|---|
| `DENSITY-U` | + | − | 0 | **+** |
| `DENSITY-D` | + | − | − | **+** |
| `LENGTH-M` | + | + | 0 | **0** |
| `LENGTH-T` | + | + (+28 tokens of declarations) | small + | ≈ 0 (J slightly more) |
| A1, `RANDOM` | 0 | 0 | 0 | 0 |
| `SAMPLE-m` | + (3 fresh variables to guess) | ++ (10 to guess) | 0 | **−** |
| `NOISY-EXACT-READ` | ± symmetric: errors ↑ on both base types | ± symmetric | 0 | 0 |
| `NOISY-EXACT-STEP`, exact, pure-literal-aware D / B1 / C0 `POLARITY` | 0 | 0 | 0 | 0 |
| `PERCEPTION-NOISE` | ≈ 0 (dropping padding clauses is harmless) | ≈ 0 | 0 | 0 |
| C1 `GREEDY` (mention order), C2 `UC` | ≈ 0, item | ≈ 0, item | 0 | ≈ 0 |
| F `WALK-k` | ≈ 0 (a single flip fixes a fresh variable) | small + | 0 | small − |
| D `DPLL-b` without pure-literal elimination | +, item (more nodes) | +, item | 0 | item |
| E `WP-t` | ≈ 0 (pure literals send no warnings) | ≈ 0 | 0 | 0 |
| `D∘A` (default at the cap) | default = A1: 0; default = `DENSITY`: + | default = A1: 0; default = `DENSITY`: − | | identifies the default |

**Crossover signature.**
- A cue shifts the *answer rate* in the same direction on SAT and UNSAT bases, so the *error rate* moves in opposite directions on the two.
- Noise (`NOISY-EXACT-READ`) moves the error rate in the same direction on both.
- That one interaction separates cue from noise with no fitted parameters.

COL predictions are analogous. ENT predictions: `FREQ` gives a main effect of FREQ; `ATMOSPHERE` gives a main effect of mood match; exact gives g only; B1, `SAMPLE-m`, `NOISY-EXACT` and `PERCEPTION-NOISE` are flat, because their drivers are matched; B4 / `ETR` / `MM` are item-level and counterbalanced.

**Out-of-sample magnitude.**
- The `DENSITY` / `LENGTH` curves fitted on E3 (θ, s per model) *predict* the size of each E2 shift.
- The test is the ratio of observed to predicted shift. If it is ≈ 1 under a single cue, that is a pure cue user; π_cue is estimated as that ratio.

**Trace predictions.**

| Family | K vs J traces |
|---|---|
| `DENSITY` | `CUE-DENS` more often in K; padding variables not treated specially |
| `LENGTH` | `CUE-SIZE` equally often in K and J |
| Structural (pure-literal-aware) | Explicit handling, e.g. "x25 appears only un-negated; set it to 1". Similar token counts in K and J after that step. |
| `SAMPLE-m` | `SAMPLE(k)`; its failures are blamed on padding clauses more in J |
| `NOISY-EXACT-READ` | `EVALSLIP` rate rises with m, equally in K and J |

**Confound control.**
- Tokens are equal in K and J, except for 7 declared names (+28 tokens, ≈ 1.5%). U isolates the declaration effect.
- Same core literals and positions; fixed-width names; same negation counts.
- **Fresh-variable atypicality**: purity, and very low occurrence counts in J. This is measured with ψ (number of pure variables, minimum occurrence) and modelled as a covariate. It is also the subject of the transplant test in E8.

**Generator recipe.**
1. Core: rejection-sample random 3-SAT with n = 24, m = 101 until the target g. Record nodes, |MUS| and the greedy / WalkSAT outcomes.
2. Choose 48 core literals uniformly; this choice is shared by K and J.
3. Assign the fresh literals to clauses, with K occurrence counts in [8, 10] and J in [2, 4].
4. Assert:
   - the padded formula is satisfiable iff the core is;
   - pure-literal elimination yields the core;
   - `POLARITY` gives the same core assignment.
5. COL: assert that `FIRST-FIT` and `DSATUR` use ≤ 3 colours on the added component in the presented order, so the greedy prediction is unchanged.
6. ENT: search the candidate conclusions (literals and 2-literal conjunctions or disjunctions, about 300 per set) for an 8-tuple satisfying the matching constraints. Reject the premise set if none exists.

**Format, metric, criteria.**
- Decision channel.
- A mixed logistic model, P(neg) ~ level × g_base + (1 | base) + (1 | model), with pre-registered contrasts K − base, J − base, U − base and K − J.
- Each member's predicted contrast vector, scaled by its E3-fitted curve, is matched by likelihood, with one free scale π ∈ [0, 1].
- **Weight readout.** Each contrast is c = Σ_h π_h c_h. The members' signature vectors over (K − J, K − base, J − base, U − base, crossover) are linearly independent, so the contrast vector identifies weights jointly. Fisher-information rank was checked in the library:
  - `DENSITY-U`: K − J > 0, U = 0;
  - `DENSITY-D`: K − J > 0, U < 0;
  - `LENGTH`: K − J = 0, K − base > 0;
  - `SAMPLE-m`: K − J < 0;
  - `NOISY-EXACT-READ`: errors rise symmetrically, with no crossover;
  - structural members: 0.

  Point estimate: π̂_DENSITY = (observed K − J) / (E3-fitted c_DENSITY). Because c_DENSITY is fitted on E3, this is an out-of-sample weight.
- **Resolution at the planned N** (300 bases): in the dev library every cue member (`DENSITY-U`, `DENSITY-D`, `LENGTH`, `SAMPLE-m`, `ALWAYS-*`) has detectable π ≈ 0.05, with an upper 95% bound of 0.03, when its signature is deterministic (c = 1). With a soft fitted cue, the general values are 0.05 / c and 0.03 / c. `NOISY-EXACT-READ` resolves at 0.14 and `PERCEPTION-NOISE` at 0.24. `DENSITY-U` and `D∘A` coincide here and are separated by E8.
- **What the readout means.** The evidence moves weight from `LENGTH` to `DENSITY` in proportion to K − J. A negative K − J moves weight toward `SAMPLE-m`. A missing crossover moves weight from cues to `NOISY-EXACT-READ`.

**Power.**
- Paired within-base comparisons at p_d ≈ 0.25, with 3 contrasts Holm-adjusted (α = 0.0167): a 10 pp shift needs ≈ 258 bases. We use 300 bases × 4 levels = **1,200 items** per domain.
- ENT: 200 sets × 8 = 1,600 items; a 10 pp within-set cue effect needs ≈ 200 sets.

**Threats to validity.**
1. **Padding is detectable.** Pure variables are atypical, so a model might treat padded instances differently for reasons we haven't modelled.
   - Mitigations: K and J are equally atypical in purity; occurrence atypicality goes the opposite way to α; trace codes show whether padding is noticed.
2. **Hardness neutrality holds only for pure-literal-aware procedures.** For the others we compute item-level predictions rather than assume neutrality.
3. **The capped-run share differs between K and J.** Primary analysis includes forced answers.
4. **ENT matching may be infeasible for some premise sets.** That causes selection on premise-set type. We report the rejection rate and compare the kept and rejected sets on ψ.

---

#### E3. Knee location under finite-size scaling (the shared α × n sweep)

**Question.**

> Does the model's P(UNSAT | α, n) curve have its knee at a fixed α\* across n (`DENSITY`), at a fixed m\* (`LENGTH`, so α\* ∝ 1/n), at an α\* that falls with n (`SAMPLE-m`), at an algorithmic threshold (C, F), or does it track the true transition and sharpen with n (exact)?

Separately: **conditional independence**. Given α and n, does g still predict the answer?

**Design.**
- This **rides on the shared budget-line sweep** and adds no items of our own.
- SAT: α ∈ {3.0, 3.4, 3.8, 4.0, 4.26, 4.5, 4.8, 5.2, 6.0} × n ∈ {10, 15, 20, 30, 40} × 40 items = 1,800.
- COL: mean degree ∈ 9 levels around the 3-colouring transition × the same n values × 40 = 1,800.
- **Recommendation to the budget-line vertical:** add n = 50 for best-effort thinking models.

**Analysis.**
- Fit per model × condition × n: logit P(neg) = a_n + b_n·φ + c·g + Σ_j γ_j z_j(x), where z_j are competitor predictions computed per item (greedy success, WalkSAT success probability, DPLL nodes, solution density).
- Knee location: α\*(n) = −a_n / b_n, with sharpness b_n.
- Compare the trajectory {α\*(n), b_n} with each member's **simulated** trajectory on the same items.

**Predictions.**

| Member | α\*(n) | b_n | c (effect of g given α) |
|---|---|---|---|
| `DENSITY` | constant (= θ) | constant | 0 |
| `LENGTH-M` | m\*/n (falls ∝ 1/n) | ∝ n | 0 |
| `SAMPLE-m` | falls with n (solution density 2^{−n(1 − H(α))} drops below 1/m at lower α) | rises | small (via s) |
| A1 / `RANDOM` | none (flat) | 0 | 0 |
| Exact | → 4.26 with finite-size shift (measured on our generator) | rises with n | large |
| `NOISY-EXACT` | ≈ exact | falls with n (curve flattens towards 0.5) | large, but shrinking with n |
| C `UC` / greedy | algorithmic threshold (≈ 8/3 for UC; report F) | rises with n | errors only on the SAT side |
| D `DPLL-b` | exact for n < n\*; above n\* the curve flattens to the default answer | — | large below n\*, ≈ 0 above |
| F `WALK-k` | WalkSAT's empirical threshold (simulated) | rises | errors only on the SAT side |

**Trace predictions.**
- `CUE-DENS` / `CUE-SIZE` rates as a function of α and n.
- `DENSITY` predicts `CUE-DENS` peaking near θ, where the model "needs" the cue. `LENGTH` predicts `CUE-SIZE` rising with m.
- D predicts the `BACKTRACK` count tracking solver nodes, with the cap and then `GIVEUP` at high n.

**Confound control.** Within an n level, α and m are collinear. That is why the trajectory across n, and E2, do the dissociating.

**Weight readout.**
- The observed curve is fitted as the mixture P(neg | α, n) = Σ_h π_h(n) · P_h(neg | α, n), with every P_h simulated on the same items and π_h allowed to vary with n (that is I).
- The knee trajectory then becomes a weight trajectory: how π_DENSITY, π_LENGTH and π_exact change with n.
- The coefficient c bounds the cue weight: c > 0 requires weight on structure-reading members.
- **Resolution:** with 360 items per n, α\* is resolved to ±0.09. The weights separate `DENSITY` from `LENGTH` with almost no confusion, since their α\*(15)/α\*(40) ratios are 1 versus 2.67. In the four-cell dev set, `DENSITY` resolves at π ≈ 0.07 and `LENGTH` at 0.12; the full sweep is sharper (§5.3 simulations).

**Power.**
- 360 items per n. The logistic location has SE ≈ 1/(b·√(N·p(1 − p))) ≈ 0.045 at b ≈ 3 / unit α, so α\* is resolved to ±0.09.
- `LENGTH` predicts α\*(15)/α\*(40) = 2.67, and `DENSITY` predicts 1, so the two are trivially separable.
- Sharpening by a factor of ≈ 1.9 between n = 15 and 40 (exact) is detectable at ≈ 15% SE on b_n.

**Threats to validity.**
1. **Broad curves at small n** mimic a soft cue. Answer: the c test, not curve shape alone.
2. **Mixtures change across n** (that is I). Fit per n, then feed into I.
3. **Capping concentrates at high n.** Forced answers are included, plus censored sensitivity analyses.

---

#### E4. Position and order counterbalancing (`PRIMACY`, `RECENCY`, `LABEL-A`, `LENGTH-OPTION`, `ECHO`)

**Question.**

> When a thinking model picks among options, or among premises to rely on, is the choice driven by **surface position**, or by **option-ID tokens**, rather than by content? And do order effects follow surface position or the order in which premises are used in the proof (the Chen et al. 2024 effect; report B)?

**Design: MC (ENT, K = 4).**
- 200 items. The options are:
  - the correct conclusion;
  - the `ETR` prediction (PyETR);
  - a cue-maximising distractor (highest `FREQ`, mood-matched, shortest);
  - a B4/B1 competitor (`MATCH` or `FIRST`, or a weaker sound conclusion).
- In half the items the correct option is also the cue-maximising one (with the cue distractor then mood-mismatched), so cues and truth are decorrelated across items.
- Each item is shown in **4 cyclic rotations × 2 label schemes** = 8 renderings:
  - labels A–D in order;
  - labels D–A in order, so that position 1 carries label "D".
- Position and label are therefore orthogonal to content and to each other.

**Design: premise order (ENT-YN).**
- 150 items with three premises: a fact F and chained rules R1, R2, with C reachable only via F → R1 → R2.
- All **6 permutations** are shown.
- The fact's position (1 / 2 / 3) is partly decorrelated from proof-order alignment τ, the Kendall τ between surface order and proof order:
  - fact first: τ ∈ {1, ⅓};
  - fact in the middle: τ ∈ {⅓, −⅓};
  - fact last: τ ∈ {−⅓, −1}.

**Answer predictions (MC).** A conditional logit, with β_pos for position, β_label for label, and content terms.

| Member | β_pos | β_label | Content terms |
|---|---|---|---|
| `PRIMACY` / `RECENCY` | position 1 / 4 ↑ under both label schemes | 0 | 0 |
| `LABEL-A` | 0 | "A" ↑ (position 1 under A–D, position 4 under D–A) | 0 |
| `LENGTH-SHORT` / `-LONG` | 0 | 0 | β_len < 0 / > 0 |
| `FREQ`, `ATMOSPHERE` | 0 | 0 | β_freq, β_atm > 0 |
| `RANDOM` | 0 | 0 | 0 |
| `SAMPLE-m` | 0 | 0 | prefers options with small ρ |
| Exact | 0 | 0 | β_truth ≫ 0 |
| B4 `ETR` / `MATCH` | 0 | 0 | β_ETR / β_MATCH > 0 |
| C4 / sequential evaluation with early stopping | **position 1 ↑ via satisficing**, the size of the effect growing with distractor plausibility | 0 | interaction position × plausibility |

**Answer predictions (premise order)**, computed per permutation:
- `PRIMACY-YN`: follows iff C's literals occur in premise 1.
- `RECENCY-YN`: the same, for the last premise.
- `ETR` and C4 `ONLINE-STATE`: PyETR / simulation.
- B1 `PREMISE-SUBSET(last j)`: computed.
- Exact and D: order-invariant.
- "Proof-order alignment" (the forward-chaining process) predicts a monotone effect of τ.

**Trace predictions.**
- `OPT-EVAL(order, stop)`:
  - Satisficing predicts that options are evaluated in displayed order and evaluation stops at the first acceptable one. The chosen option is then the first that passes the trace's own (possibly flawed) check.
  - Content-based families predict that the conclusion is derived first and then matched to an option, or that all options are evaluated.
  - `PRIMACY` as a bare cue predicts choosing position 1 with `CUE-POS` or no evaluation at all.
- Premise order: which premise the trace processes first, and premise mention coverage:
  - `ETR` / C4 process in displayed order;
  - B1 `PREMISE-SUBSET` never mentions some premises;
  - exact uses premises in proof order whatever the display order.

**Confound control.**
- The Latin square balances position within item.
- Label tokens are single tokens in every tokenizer.
- Option lengths are recorded as covariates.
- Option-ID priors are estimated the PriDe way: permute contents on a held-out 10% (Zheng et al. 2024 **[v]**).

**Generator recipe.**
- Options from zoo outputs. Reject an item if two options are logically equivalent or if more than one is entailed.
- Premise-order items are chains built with z3, with 6–8 atoms. Reject an item if fewer than 3 zoo members differ across permutations.

**Weight readout.**
- The conditional logit maps onto weights, because a π-mixture of "choose position 1" with content-based choice gives a position-1 share of π_PRIMACY + (1 − π_PRIMACY)·(content share). So:
  - π̂_PRIMACY = (position-1 share − content-predicted share) / (1 − content-predicted share);
  - π_LABEL-A is the analogous excess for label "A";
  - the content weights π_exact, π_ETR, π_FIRST, π_cue come from which content is chosen.
- Satisficing is a separate weight. Its signature is the position × plausibility interaction.
- Premise order: separate weights for surface position (`PRIMACY` / `RECENCY`), order-sensitive updating (`ETR` / C4), and order invariance (exact, UP).
- **Resolution at the planned N** (200 items × 8 renderings): position, label, length and content weights are detectable at π ≈ 0.02–0.04 (question library). The two-way tie for the shortest option keeps `LENGTH-SHORT` separate from the role that owns the shortest text.

**Power.**
- MC: 200 items × 8 renderings = 1,600. A 5 pp position-share shift needs ≈ 590 renderings at α = 0.05; 1,600 detect ≈ 3 pp.
- Premise order: 150 items × 6 = **900**. A fact-first versus fact-last 10 pp effect, within item, at p_d ≈ 0.3 needs ≈ 240 comparisons; we have about 600.

**Threats to validity.**
1. **Thinking models rarely show position effects when they evaluate every option.** A null is informative here; it is not a failure.
2. **Satisficing versus cue** is separated only by the plausibility interaction. Distractor plausibility is pre-registered as the share of zoo members that endorse the option.
3. **Label-scheme D–A is itself unusual**, which may raise caution. The analysis includes a label-scheme main effect.

---

#### E5. Rule inversion with length-matched preamble controls (`TEXTBOOK-TRANSFER`)

**Question.**

> When a familiar problem is stated with an inverted rule, does the model answer with **the textbook problem's answer**, rather than make unstructured errors?

Quantity estimated: π_TT. It is the excess, over the coincidence rate, of inverted-item answers that are valid under the textbook reading and invalid under the stated one, normalised by textbook competence. It is cross-checked by the rate at which the answer is **identical** to the model's own answer to the neutral version, relative to test–retest identity.

**Design.** Each base instance is shown in 4 framings, plus a partial-inversion set:

| Framing | Content | Correct answer | `TT` answer |
|---|---|---|---|
| T | Textbook rule, no preamble | Sol(x) | Sol(x) |
| N | T plus a **neutral** preamble restating the standard meaning (length-matched to I, ±3 tokens) | Sol(x) | Sol(x) |
| I | The same constraint list plus an **inverting** preamble | Sol(x_inv) | Sol(x): the same answer as under N |
| I+R | I plus a one-line restatement of the rule just before the question | Sol(x_inv) | Sol(x) if substitution is a prior; ↓ if it is a retention failure |
| P (partial) | Only the constraints marked ★ (half of them) use the inverted meaning | Sol(x_P) | Violations concentrated on ★ constraints |

**Inversions per domain** (each chosen so that `TT` and the correct answer are disjoint by construction):

- **SAT** (n ∈ {12, 16}, α ∈ [3.8, 4.3], SAT).
  - Rule: "a rule holds when at least one of its listed conditions is **false**", so x_inv = F̄, the formula with every literal flipped.
  - Sol(F̄) = ¬Sol(F), so the *decision* can't discriminate; the witness can.
  - Reject the item unless F ∧ F̄ is UNSAT, so that no textbook solution is valid under inversion.
  - Half the items have a unique textbook solution. For those, `TT` detection doesn't depend on the inner solver.
- **COL** (n ∈ {10, 14}, k ∈ {3, 4}).
  - Rule: "the listed pairs are **friends**; *only* friends may share a room; at most k rooms". That is a proper colouring of Ḡ, a partition into ≤ k cliques of G.
  - The textbook reading is: the listed pairs are enemies, enemies may not share.
  - G is planted as k cliques of size 3–4 plus random edges (p ≈ 0.15). Require G and Ḡ both k-colourable. They are disjoint for n > k.
- **ENT** (5–6 atoms, 2–3 "either…or" premises).
  - Preamble: "here 'either A or B' means that **neither** A nor B is true" (NOR; a counterfactual-task design, Wu et al. 2024, report B).
  - Require the entailed-literal sets under NOR and under OR to differ and both be non-empty. B4 `FIRST`/`ETR` are computed under both readings.
- **KNAP** (n = 10).
  - Rule: "choose items whose total weight is **at least** L, minimising total value", with L at the capacity position (EHOP-style inversion; report B).
  - The textbook optimum (≤ L, maximising value) is infeasible here.

**Answer predictions** (inverted cells; ± means item-computed under the stated rule).

| Family | I: answer | I vs N identity | I+R vs I | P: where violations fall |
|---|---|---|---|---|
| A3 `TT` | ∈ Sol(T(x)) \ Sol(x) | **ID_IN ≈ ID_NN** (the test–retest identity under N) | = (prior) or ↓ (retention) | concentrated on ★ |
| Exact | ∈ Sol(x_inv) | ≈ 0 (the solution sets are disjoint) | = | none |
| A1 / A2 cues | decision as under N (inversion doesn't move cues); witness from fill | ≈ 0 | = | uniform |
| `RANDOM` | chance; ≈ 1/8 violations under both readings | 0 | = | uniform |
| `SAMPLE-m` | checks the stated rule: no `TT` | 0 | = | — |
| `NOISY-EXACT` | near Sol(x_inv): few inverted-reading violations | 0 | = | uniform over constraints |
| `PERCEPTION-NOISE` (misreads the rule w.p. p_r) | `TT`-like w.p. p_r | ≈ p_r · ID_NN | ↓ | **uniform** (misreads individual constraints, not the ★ class) |
| B1 `DROP-CONSTRAINT` (selector: non-standard constraints) | violates the ★ / inverted constraints | ≈ 0 | = | on ★, like `TT` (the stated overlap, see threats) |
| B4 / C / D / F | run under the rule they *read*: under the stated rule, ± computed; composed with `TT`, as `TT[s]` | `TT[s]` ⇒ ID_IN ≈ ID_NN | — | — |

**Violation profile.**
- 2-D: (violations under the textbook reading, violations under the stated reading).
- `TT`: (0, ≈ 1/7 of SAT clauses). Correct: (≈ 1/7, 0). `RANDOM`: (1/8, 1/8). Noisy variants lie near the respective axes.

**Trace predictions.**

| Family | Trace |
|---|---|
| `TT` | `REFRAME = textbook` (the rule is restated in standard form) or `absent`. Constraint checks use textbook semantics ("Ann and Bob are friends, so different rooms"). **Rule drift**: an as-stated paraphrase early, textbook checks later. Drift means substitution at solving time, not at reading. |
| Exact | `REFRAME = as-stated`; every check uses the stated semantics |
| `PERCEPTION-NOISE` | One `MISQUOTE` of the rule; checks consistent with the misquote; fixed by R |
| B1 `DROP-CONSTRAINT` | ★ constraints never mentioned (coverage) |

Check semantics are classified automatically from parsed check statements, using the instance's constraint list, plus LLM `REFRAME` coding.

**Confound control.**
- N controls for the preamble's length, the presence of a definition, and the attention a definition demands. I versus N is the inversion effect; T versus N is the preamble effect.
- Constraint lists are identical across T / N / I. P marks are single-token "★".

**Metrics and criteria.**
- TT rate = P(y_I ∈ Sol(T(x)) \ Sol(x)).
- Identity ratio = ID_IN / ID_NN, where ID_NN comes from the second N sample.
- Partial-inversion concentration ratio CR = (★ violations / ★ count) / (non-★ violations / non-★ count).
- **Weight readout.**
  - π̂_TT = (TT rate − coincidence rate) / (textbook competence). Textbook competence is the model's accuracy under N, so π_TT is the share of the model's textbook competence that gets carried, unchanged, into the inverted problem.
  - The coincidence rate is |Sol(T(x))|/|answer space|: ≈ 0 for SAT/COL; for ENT, the share of OR-reading answers among random literal sets.
  - The identity ratio (ID_IN / ID_NN) gives an inner-solver-free estimate of the same weight.
  - The I+R − I difference splits that weight into a *prior* part (persists with the reminder) and a *retention* part (removed by it). The second is credited to `PERCEPTION-NOISE`.
  - The concentration ratio CR on P moves weight between TT / B1 (★-concentrated) and noise (uniform).
- **Resolution at the planned N** (200 bases): π_TT is detectable at 0.015–0.03 (COL and SAT), with upper 95% bounds of 0.01–0.02, because coincidence is ≈ 0. `PERCEPTION-NOISE` (rule misreading) resolves at 0.05. TT[s] and B1 `DROP-CONSTRAINT(★)` are separated only by the I framing.

**Power.**
- Coincidence is ≈ 0, so detecting π_TT ≥ 0.05 needs only ≈ 100 items.
- The real targets are the **moderators**: direct versus `BE` and I versus I+R, paired, a 10 pp difference at p_d ≈ 0.2, ≈ 150 bases. We use **200 bases × 4 framings + 100 partial** per domain (KNAP: 200 × 4).

**Threats to validity.**
1. **NOR and "only friends" are hard to state naturally.** Low accuracy under I could be comprehension failure. The I+R and P cells and the paraphrase coding separate comprehension (the rule is misquoted) from substitution (the rule is quoted correctly, but textbook checks follow).
2. **`TT` and B1 `DROP-CONSTRAINT` with a "non-standard" selector are observationally close in the P cell.** We pre-register that P concentration is credited to `TT` only when ID_IN ≈ ID_NN also holds on full inversions.
3. **Sizes are below n\*,** so textbook answers exist. Results therefore don't speak to `TT` above the budget line.

---

#### E6. Rarity dose-response (`SAMPLE-m` versus D-search versus perception)

**Question.**

> Does endorsing a non-entailed conclusion fall with its counter-model fraction ρ along the curve (1 − ρ)^m, holding cues, the perception fragility κ and the systematic-search cost η fixed?

Separately: when the trace samples k cases, is endorsement ≈ (1 − ρ)^k?

**Design (ENT).**
- 200 premise sets over 7 atoms, with |Mod(P)| ∈ {16, 32}.
- Each set has 6 conclusions at ρ ∈ {0 (entailed), 1/16, 1/8, ¼, ½, ¾}, matched within the set on ψ-cues.
- Across the set of items, ρ is decorrelated (|r| < 0.1) from:
  - κ: the fraction of single-literal sign flips of P under which P̃ ⊨ C (the `PERCEPTION-NOISE` driver);
  - η: DPLL nodes to the first counter-model, with fixed atom order and true first (the D driver);
  - the PyETR and `MM` predictions.
- Plus a 2 × 2 subset: ρ ∈ {1/16, ½} × κ ∈ {low, high}, 100 sets × 4.
- SAT secondary: 300 SAT items at n = 20, α = 4.0, spread over log s (exact solution counts by enumeration). `SAMPLE-m` predicts P(SAT) rising with s/2ⁿ; `DENSITY` predicts flat. WalkSAT's success, simulated per item, is a covariate, and the assignment channel separates the two (E7).

**Answer predictions** (P(follows) as a function of the drivers).

| Member | ρ | κ | η |
|---|---|---|---|
| `SAMPLE-m` | (1 − ρ)^m: decreasing, convex | 0 | 0 |
| A1 / A2 (cues matched) | flat | flat | flat |
| `RANDOM` | flat | flat | flat |
| Exact | 1 at ρ = 0, 0 for ρ > 0 | 0 | 0 |
| `NOISY-EXACT` | flat at ε for ρ > 0 | 0 | 0 |
| `PERCEPTION-NOISE` | weak | **increasing** | 0 |
| D `DPLL-b` | weak | 0 | **increasing** (fails to find a counter-model within b) |
| B1 (sound) | 0 for ρ > 0 | 0 | 0 |
| B4 `MM` / `ETR` | item: endorses iff the counter-models lie outside the explicit models | 0 | 0 |

**Trace predictions.**

| Family | Trace |
|---|---|
| `SAMPLE-m` | `SAMPLE(k)` with a small, non-exhaustive k; endorses iff no sampled case is a counter-model. **Quantitative law:** among `SAMPLE(k)` traces, P(follows) ≈ (1 − ρ)^k. |
| D | Exhaustive `BRANCH` structure; stops at the first counter-model, at a trace position ∝ η |
| B4 `MM` | `TRUE-ONLY` enumeration; omits the false-component cases that contain the counter-models |
| `PERCEPTION-NOISE` | A `MISQUOTE` that makes C entailed |
| A2 | No case analysis; `CUE-*` |
| **Faithfulness check** | If a sampled case *is* a counter-model and the answer is still "follows", the trace is unfaithful or there is a slip (an `EVALSLIP` in that case) |

**Weight readout.**
- P(follows | x) = Σ_h π_h · P_h(follows | x), where P_SAMPLE = (1 − ρ)^m, P_PERCEPTION ∝ κ, P_D falls with η, and exact gives a step.
- Because ρ, κ and η are decorrelated by design, π_SAMPLE, π_PERCEPTION and π_D are separately identified, with m as a free parameter.
- The trace law gives a second, faithfulness-weighted estimate: among `SAMPLE(k)` traces, compare P(follows) with (1 − ρ)^k.
- **Resolution at the planned N** (200 sets × 6 conclusions):
  - The dev library (one premise set, m = 8) resolves π_SAMPLE at 0.07 against `NOISY-EXACT`, with an upper 95% bound of 0.05. The analytic power for the full design is π_SAMPLE ≈ 0.12 at m = 4.
  - `PERCEPTION-NOISE` is almost unresolved on a single premise set (0.94), because κ is not decorrelated from ρ there. That is why the study's design decorrelates ρ, κ and η across 200 sets.

**Power.**
- Within-set contrast at ρ = 1/16 versus ½: π_SAMPLE = 0.1 at m = 4 gives Δ = 0.07; at p_d ≈ 0.2 that needs ≈ 317 sets.
- 200 sets detect π ≈ 0.12.
- Totals: ENT 200 × 6 + 100 × 4 = **1,600**; SAT 300.

**Threats to validity.**
1. **ρ, κ and η are correlated in natural items.** Decorrelation by design selection may pick unusual premise sets; we report ψ distributions.
2. **Thinking models may enumerate exhaustively at 7 atoms (128 rows),** collapsing everything to exact. Then the null is the finding, and sizes would grow to 9–10 atoms in a follow-up.
3. **`SAMPLE(k)` coding depends on parsing cases.** We validate it on the hand-labelled subset.

---

#### E7. Error systematicity, perception and noise (`NOISY-EXACT`, `PERCEPTION-NOISE`, `RANDOM`)

**Question.**

> Are a model's errors **systematic** (determined by the item and invariant across renderings that preserve the relevant cue), or **exchangeable noise** given size?

Separately: are invalid witnesses explained by **misreading** (aligned with what the echo shows was misread) or by **execution slips**?

**Design.**
- 150 base items per domain near n\*: SAT n = 20–24 at α ≈ 4.2; COL n = 20; ENT-OPEN with 8 atoms.
- Each in 4 renderings:
  - R0: original;
  - R1: renamed (a random permutation of variable indices or person names, token-count-preserving);
  - R2: shuffled (clause, edge and premise order permuted, and literal order within clauses);
  - R3: renamed and shuffled.
- Samples: 2 for R0 and R3, 1 for R1 and R2.
- **Echo condition:** 150 items per domain (SAT at n = 16). The prompt asks the model to restate the constraints as JSON first, then answer.

**Analyses.**
1. **Variance components** of correctness: logit P(err) = f(size, hardness) + u_item + v_{item×shuffle} + w_{item×rename} + residual.
2. **Wrong-answer concentration:** the entropy of the wrong witnesses, mapped back through the renaming, across samples and renderings.
3. **Violation profile:** the count, position and type of violated constraints; involvement of high-degree vertices.
4. **Echo alignment:**
   - P(answer valid for the echoed instance | echo ≠ instance);
   - the overlap between the answer's violations and the echo's errors.
5. **`RANDOM` diagnostic:** the share of clauses satisfied versus 7/8; the share of edges violated versus 1/k.

**Predictions.**

| Member | σ²_u (item) after size covariates | σ²_v (shuffle) | σ²_w (rename) | Wrong-answer entropy | Violations | Echo alignment |
|---|---|---|---|---|---|---|
| A1, A2 count cues | **large** | ≈ 0 | ≈ 0 | low (determined) | random fill | none |
| A2 positional | large | **large** | ≈ 0 | low | — | none |
| A3 | n/a (textbook framing) | | | | | |
| `RANDOM` | ≈ 0 | ≈ 0 | ≈ 0 | **maximal** | ≈ m/8; ≈ \|E\|/k | none |
| `SAMPLE-m` | small (via s) | ≈ 0 | ≈ 0 | high (a random solution or non-solution) | ≈ m/8 when it fails | none |
| `NOISY-EXACT` | **≈ 0** (errors exchangeable at fixed L) | ≈ 0 | ≈ 0 | high, but near-misses (1–3 violations) | few, uniform in position, at clauses containing the flipped variables | none |
| `PERCEPTION-NOISE` | ≈ 0 | ≈ 0 (`-POS`: > 0) | ≈ 0 | moderate | few, **exactly the misread constraints** | **high** |
| C1 (input order); D with lexicographic branching | large | large | **> 0** (renaming permutes index order) | low | C: a dead-end pattern; D: none, or the default | none |
| F `WALK-k` | moderate | ≈ 0 | ≈ 0 | moderate (local minima) | 1–3, concentrated at local minima | none |
| B1 / B4 systematic misreading | large | large if position-based | ≈ 0 | low | on the selector-defined class, the **same across samples** | aligned only if the echo shows the same selector |

**Trace predictions.**
- `NOISY-EXACT`: an `EVALSLIP` precedes the first violation, at the step involving that constraint.
- `PERCEPTION-NOISE`: a `MISQUOTE` (in the echo, or in quotes within the trace) of exactly the violated constraint.
- B1/B4 systematic: the selector-class constraints are never mentioned.

**Weight readout.**
- The systematic share of error variance, σ²_u / (σ²_u + π²/3), estimates 1 − π_noise among errors. Here π_noise = π_NOISY + π_PERCEPTION, and π²/3 is the logistic residual variance.
- Echo alignment splits π_noise: the share of invalid witnesses whose violations coincide with echo errors estimates π_PERCEPTION / π_noise, against a permutation baseline.
- The shuffle and rename components measure weight on order-sensitive (C1, positional) and index-sensitive members.
- **Resolution at the planned N** (150 items × 4 renderings): a systematic share of ≥ 0.15 is detected. `NOISY-EXACT` is the hardest family in the whole library to resolve: 0.46 in E7 at dev size, 0.13 at best (E1-SAT, from its symmetric errors). Its bound therefore relies most on the study-size N and on E2's crossover test. Echo alignment of ≥ 0.3 versus a chance alignment of ≈ 0.1 is detected with 15–45 misread items per model, pooled hierarchically.

**Power.**
- Within-item versus between-matched-item concordance of error: 150 items × 6 within-item rendering pairs, with matched-size random pairs. SE ≈ 0.025 after clustering, so a concordance difference of 0.07 is detectable.
- Echo: 150 items per domain, with an expected echo-error rate of 10–30%. That gives 15–45 misread items per domain per model, enough to detect alignment ≥ 0.5 versus chance ≈ 0.1. Pooling across models is via the hierarchical model.

**Threats to validity.**
1. **Echo changes the computation** (it acts as a scratchpad). Causal claims about perception are restricted to the echo condition, and its error distribution is compared with R0's.
2. **Renaming changes the tokenisation of names.** We use fixed-width indices and a single-token name pool checked against each tokenizer.
3. **"Systematic" errors could come from a structural heuristic, not a cue.** σ²_u alone doesn't identify A; it only bounds the weight on exchangeable noise. A's weight comes from E1/E2.

---

#### E8. Trace faithfulness and answer commitment (behavioural; no activations)

**Question.**

> Is the final answer **determined by the procedure the trace describes**, or is it fixed before the trace (as by a cue) and carried through regardless?

Quantities estimated, per model × domain: π_post-hoc (the answer is fixed before the trace and matches the cue), π_trace (the answer is produced by the traced procedure) and π_D∘A. They are estimated from the commitment curve c(f), the transplant outcomes and mistake insertion, stratified by how the response ended.

**Items.** Subsets of `BE` responses, with no new prompts:
- 250 from E1 critical pairs;
- 200 from E2 K/J pairs;
- 150 from E5;
- 150 from E6.

**Tests.**

1. **Early answering** (Lanham et al. 2023).
   - Truncate the trace at f ∈ {0, 0.25, 0.5, 0.75}, append `</think>` and the answer header, and decode the answer greedily.
   - Commitment curve c(f) = P(answer at f = final answer).
   - Also record P(answer at f = cue prediction).
2. **Trace transplant** (cue-conflict). Splice the complete trace from the K version into the J prompt, and vice versa (the fresh variables x25–x27 exist in both), then force the answer.
   - If the answer follows the trace's conclusion, the trace is sufficient.
   - If it follows the host prompt's α, the cue is read from the prompt and overrides the trace.
3. **Mistake insertion** (Lanham et al. 2023).
   - In traces coded as D, C or F, flip one derived fact at the midpoint (`x07 = 1` → `0`) and continue generating.
   - If the answer moves as the corrupted procedure implies, the trace is causally used.
4. **Trace–answer consistency.** The answer implied by the final committed state (parsed and replayed) versus the final answer. Inconsistent responses are classed:
   - (i) the procedure found X, the answer is ¬X: an override;
   - (ii) the procedure was inconclusive, the answer is confident: `GIVEUP` / cue;
   - (iii) the procedure is wrong because of a slip: `NOISY-EXACT`.

**Predictions.**

| Family | c(0) | Answer at f = 0 vs cue | Transplant follows | Mistake insertion moves answer | Consistency |
|---|---|---|---|---|---|
| A2 cue, post-hoc trace | **high** | = cue | **host prompt's cue** | no | type (ii) inconsistency common |
| A1 | high | = constant | either (constant) | no | (ii) |
| `D∘A` (search, then cue default) | low on `COMPLETE`, high on `GIVEUP`/`CAPPED` | = cue on `GIVEUP` | the trace when it completed; the cue when it gave up | yes on `COMPLETE` | high on `COMPLETE` |
| `SAMPLE-m` | low; steps up at each sampled case | — | the trace | yes (corrupt a case) | high |
| Exact / D / C / F | low, rising late | ≠ cue | **the trace** | **yes** | high; slips are type (iii) |
| `NOISY-EXACT` | like exact | | the trace | yes | type (iii) |

**Output.** The faithfulness index r̂ per model × domain is the pre-registered mean of:
- 1 − c(0) on items where the trace's procedure is coded non-cue;
- the transplant follows-trace rate;
- the mistake-insertion sensitivity;
- the consistency rate.

r̂ is used in §2.5.5.

**Weight readout.**
- Three weights: π_post-hoc (the cue fixes the answer and the trace is decorative), π_trace (the answer follows the trace), and π_D∘A (trace-driven when the trace completes, cue-driven otherwise).
- They are estimated from the stratified early-answer and transplant outcomes: the cue-following share in COMPLETE versus GIVEUP/CAPPED responses.
- r̂ = 1 − π_post-hoc, restricted to the procedure-coded traces.
- **Resolution at the planned N** (750 early answers, 200 transplants): detectable π ≈ 0.06–0.09 for the three weights (question library, E8 table).

**Power.** 200 K/J transplants. Detecting a follows-host rate of 0.6 versus 0.5 needs ≈ 200 (one-sided, power 0.8). Early answering on 750 responses × 4 truncation points.

**Threats to validity.**
1. **Forced early answers are out of distribution.** A model may answer "UNSAT" by default when cut off, which mimics A1. Control: at f = 0 under `NT`, compare with the model's own non-thinking answer.
2. **Transplanted traces mention instance details that conflict with the host prompt.** K and J share the core, the positions and the x25–x27 names, so conflicts are limited to the fresh-variable occurrence counts.
3. **Mistake insertion needs traces with explicit derived facts.** A-family traces rarely have them, so the sensitivity estimate is conditional on procedure-coded traces. This is pre-registered as such.

---

#### E9. Environment shift in context (I: is cue reliance adaptive?) — exploratory

**Question.**

> Does a model's `DENSITY` reliance (the E2 contrast K − J) change with how valid the cue is in **in-context examples**?

Rational strategy selection (Lieder & Griffiths 2017, report F) predicts that it does. A fixed prior predicts that it does not.

**Design.**
- 8 solved examples (n = 12; decision plus witness) before an E2 K or J test item, from one of three environments:
  - **V:** natural random instances, where α predicts g (`DENSITY` with θ = 4.26 is ≈ 85% accurate, measured on the generator).
  - **N:** matched pairs, so α carries no information.
  - **R:** high-α SAT and low-α UNSAT, chosen so that the α *marginal* equals V's.
- 200 test items × 3 environments = 600.

**Predictions.**

| Member | K − J in V | in N | in R |
|---|---|---|---|
| Adaptive `DENSITY` (I) | + | ≈ 0 | − (reversed cue learned in context) |
| Fixed `DENSITY` prior | + | + | + |
| Exact / structural | 0 | 0 | 0 |
| `LENGTH` | 0 | 0 | 0 |

**Trace.** References to the examples' sizes or densities ("like example 3, which had many clauses and was unsatisfiable").

**Confound control.** The environments are matched on example prompt lengths, n, m and the α marginal; only the (α, g) relation differs.

**Power.** About 100 K and 100 J per environment give a contrast SE ≈ 0.07, so only differences ≥ 0.2 across environments are detectable. Hence **exploratory**.

**Threats to validity.** Long prompts (≈ 7k tokens) change the attention context. In-context examples may also prime the model to verify more, which reduces cue use in every environment. That is a main effect, not an interaction, so the interaction test survives it.

---

### 2.7 Eval design summary (template table)

| ID | Item generator | Answer format | Metric | Weight readout (what moves π) | Resolution at planned N (the question library has per-theory values) |
|---|---|---|---|---|---|
| E1 | Invariance pairs: SAT polarity-preserving swaps; COL double-edge swaps; ENT sign swaps. 400 critical + 200 null pairs per domain, plus a 50-pair UP-refutable stratum. | decision + witness | Directed discordance D; the witness class on x; trace divergence at the edited constraints | D̂ − D̂_null lower-bounds π_struct. The error side splits it among C/F/D, `PERCEPTION-NOISE` / B1, and `NOISY-EXACT`. The witness class separates C0/C1/D from fill-based members. | π_struct ≥ 0.07 detectable; π_struct ≤ 0.075 (upper 95%) under a blind model |
| E2 | Satisfiability-neutral padding K/J/U (SAT, COL); matched conclusions g × FREQ × ATMOSPHERE (ENT) | decision | Contrast vector versus member signature vectors; the crossover | π̂_DENSITY = (K − J)/c_DENSITY; the U contrast splits `DENSITY-D` from `-U`; K − base with K ≈ J moves weight to `LENGTH`; K − J < 0 to `SAMPLE-m`; no crossover to noise | Cue weights ≈ 0.05/c_cue detectable (library: 0.05) |
| E3 | Shared α × n sweep | decision | Mixture fit of simulated curves, per n | Weight trajectories π_DENSITY(n), π_LENGTH(n), π_exact(n) | α\* ±0.09 per n; `DENSITY` vs `LENGTH` almost unconfusable |
| E4 | MC Latin square × 2 label schemes; 6 premise permutations | option / YN | Conditional logit; order-specific weights | Excess position-1 share gives π_PRIMACY; excess "A" gives π_LABEL-A; the chosen content gives the content weights; surface-position versus updating weights from the orders | Position, label, length and content weights 0.02–0.04 |
| E5 | T / N / I / I+R / P framings; disjointness-checked inversions | witness | TT rate; identity ratio; concentration ratio CR | π̂_TT = (TT rate − coincidence) / textbook competence, split into prior and retention parts by I+R; CR splits TT/B1 from noise | π_TT 0.015–0.03 detectable |
| E6 | ρ-graded conclusions, decorrelated from κ and η | YN | Mixture dose-response with free m; trace law | Separate weights π_SAMPLE, π_PERCEPTION, π_D via ρ, κ, η | π_SAMPLE 0.07 (library) to 0.12 (analytic, m = 4) |
| E7 | 4 renderings × samples; echo condition | witness | Variance components; wrong-answer entropy; echo alignment | The systematic share gives 1 − π_noise; echo alignment splits π_noise into `PERCEPTION` vs `NOISY` | Systematic share ≥ 0.15 detected; `NOISY-EXACT` the hardest family (0.13–0.46) |
| E8 | Subsets of E1/E2/E5/E6 responses | forced answer | Stratified early answering, transplant, mistake insertion | π_post-hoc, π_trace, π_D∘A; r̂ = 1 − π_post-hoc | 0.06–0.09 |
| E9 | 3 in-context environments × E2 K/J test items | decision | K − J by environment | Δπ_DENSITY across environments: the slope of the I selector on cue validity | Δπ ≥ 0.2 (exploratory) |

### 2.8 Generator specifications

Worked instances of every eval, with verified ground truths and per-theory predictions, are in [A_H_baselines_questions.md](A_H_baselines_questions.md) and [`data/examples/A_H_baselines.jsonl`](../../data/examples/A_H_baselines.jsonl). Yields below were **measured** with throwaway scripts (z3 / brute force), not guessed, except where marked *est.*

**Common to every generator.**

- **Hashes** (DESIGN §5.1). Each item stores three:
  - a *presentation hash* of the exact prompt;
  - a *logical hash* of the canonical content (sorted clauses with sorted literals; sorted premises), which is invariant to clause and literal order but not to renaming;
  - a *family hash* of its base item, inherited by every variant.

  Analyses join on these hashes.
- **Dev/test disjointness.**
  - Dev bases draw seeds from [0, 10⁶) and test bases from [10⁶, 2·10⁶). Every variant inherits its base's split.
  - A dedup pass rejects any test base whose logical hash matches a dev base or a library item.
  - For n ≤ 24 it also rejects test bases isomorphic to one: when cheap invariants collide (degree and sign-pattern histograms), it runs a VF2 isomorphism test (networkx) on the signed clause–variable incidence graph.
  - The example-library items are on a blocklist for both splits. In-context example pools (E9) are a third, separate pool.
- **Rendering.**
  - Fixed-width variable names (`x01`…).
  - People's names come from a pool that is single-token in all four tokenizer families (gpt-oss o200k, Qwen3, DeepSeek-V3, Llama-3); the generator checks this.
  - Atoms use the form "the ⟨noun⟩ is ⟨adjective⟩", so negation is always exactly the one token " not" or "¬".
  - The generator asserts, per tokenizer, the token-count difference that each design promises: 0 within E1 pairs, the declaration line only between E2 K and J, ±3 between E5 preambles.
- **Recorded with every item:**
  - all zoo members' predictions, from every vertical;
  - hardness covariates: DPLL decisions with and without the pure-literal rule, solution count, necessary clauses, WalkSAT success over 30 seeds, greedy outcome, UP depth, ρ, κ, η;
  - the list of assertions passed.

**E1. Invariance pairs.**

| | SAT | COL | ENT |
|---|---|---|---|
| Template | §1.3 CNF, or the menu story (½ each, between bases) | rooms; "the following pairs are enemies"; k = 3 | "facts about a machine" plus "Does it follow that C?" |
| Parameters | n ∈ {16, 24, 36} (⅓ each); α ∈ {4.0, 4.26, 4.5}; m = round(αn); 3 distinct variables per clause, signs Bernoulli(½) | n ∈ {15, 20, 30}; G(n, p) with mean degree U[4.2, 4.6]; random list order | atoms ∈ {6, 8, 10}; 4–7 premises: one categorical (a conjunction of 1–2 literals, at a random position), the rest "either…or" with 2–3 disjuncts of 1–2 literals |
| Variant derivation | Enumerate admissible swaps (v, i, j): v positive in C_i, negative in C_j, neg(C_j) = neg(C_i) + 1; flip both. Critical if g flips, null if not. One swap per base. | Double-edge swap (a,b),(c,d) → (a,d),(c,b), done in place; a, b, c, d distinct and the new edges absent | Move a negation on atom v ∉ atoms(C) from premise j to premise i, with neg(j) = neg(i) + 1 |
| Rejection / assertions | The base needs ≥ 1 critical swap. Assert equal: per-variable polarity counts, the clause negation multiset, the `POLARITY` assignment, tokens. Null pairs: half SAT→SAT, half UNSAT→UNSAT, from different bases. | Degree sequence equal; the list positions of the edited edges balanced across terciles; FIRST-FIT order is the people-list order | P and P′ consistent; C not a premise; P′ ⊭ C. Assert equal: FREQ, atmosphere, `PRIMACY`/`RECENCY`, the per-premise negation multiset, total words and tokens. Stratify by C's propagation depth (steps beyond the facts) ∈ {1, 2, ≥ 3, none} and record ρ′. A conclusion that is itself a stated fact cannot be broken by a swap on another atom, so there is no depth-0 stratum. |
| B1 stratum | 50 extra pairs: formulas with 2 unit clauses ("facts") and 15% binary clauses, where UP-3 refutes F′ but not F | — | the depth strata |
| Yield (measured) | P(SAT base) at α = 4.26: 0.82 (n = 12), 0.52 (n = 16), 0.42 (n = 24). Admissible swaps per base ≈ 180–370, of which 5–10% are critical. ≈ 60–70% of SAT bases have a critical swap. So about 2 random formulas per critical pair. | *est.* similar to SAT: 1 colourable base in ~2 near the threshold, with several % of swaps critical | ≈ 15 premise sets tried per accepted pair (6 atoms, depth ≥ 1 step beyond the facts; measured) |

**E2. Satisfiability-neutral padding.**

| | SAT | COL | ENT (matched conclusions) |
|---|---|---|---|
| Template | §1.3 CNF, with the declaration line listing all declared variables | rooms, k = 3 | as E1, one conclusion per item |
| Base | Core n = 24, m = 101 (α = 4.21), rejection-sampled to the target g: 150 SAT, 150 UNSAT | G(20, p), mean degree 4.4, to the target colourability | 6–8 atoms, 4–6 premises |
| Variant derivation | 28 padding clauses, each = (fresh literal, two core literals from distinct core variables, signs ½), at 28 uniformly chosen slots of 129. **The same core literals and slots in K and J.** K: fresh variables x25–x27, each in 9–10 clauses. J: x25–x34, each in 2–3 clauses. 14 of 28 fresh literals are negated, in the same slots in both. U: core + 8 declared, unused variables. | K: + K_{3,3,3} on 9 new people (27 edges). J: + a random tree on 28 new people (27 edges, BFS order). U: + 8 isolated people. New edges sit at the same list positions in K and J; K's new names are a prefix-aligned subset of J's insertion positions. | Search ≈ 300 candidate conclusions (literals and two-literal conjunctions or disjunctions) for an 8-tuple filling g × FREQ (f(C) ≥ 3 vs ≤ 1, as defined in E2) × ATMOSPHERE (match vs mismatch) |
| Rejection / assertions | (The dev library uses a core at α = 4.5, so that the deterministic θ = 4.26 falls between U's α_D and α_U.) Fresh variables pure. Padded formula SAT iff the core is. Pure-literal elimination returns the core exactly. The K and J prompts differ only in fresh-variable identities and the declaration line. | Colourability unchanged. FIRST-FIT and DSATUR colour the new component with ≤ 3 colours in presented order. | Within the tuple: words ±1; equal overlap with the first, last and categorical premises; for entailed C, equal UP depth; for non-entailed C, ρ within ±1/16 and κ within ±0.05. PyETR predictions counterbalanced across sets. Reject the set if no tuple exists. |
| Split | — | — | 50% of premise sets are a calibration split for the A2 thresholds |
| Yield | Core acceptance = P(target g): P(SAT) = 0.71 at n = 24, m = 101 (measured), so ≈ 1.4 draws per SAT core and ≈ 3.4 per UNSAT core. Padding never rejects. | *est.* ~0.5 per target class near the threshold | *est.* The dev search (5 atoms, 5 premises, with no conclusion overlapping the first or last premise) succeeds within minutes; to be measured in the pilot. |

**E3.** The shared sweep (budget-line vertical): random 3-SAT, α grid × n grid × 40, **no rejection**, so the natural distribution is kept; g is stored. COL is analogous on a mean-degree grid. Yield 1.

**E4.**

- **MC.**
  - 3–4 premises over 5–7 atoms: two or three "either…or" and one categorical.
  - **Options:**
    - **correct:** an entailed formula that is not a premise, preferably with a mood that does not match the atmosphere;
    - **ETR:** non-entailed, but endorsed by PyETR;
    - **FIRST:** non-entailed, entailed under the first-disjunct restriction, not endorsed by ETR;
    - **cue:** non-entailed, endorsed by neither, mood = atmosphere, with mean FREQ strictly above every other option's.
  - Exactly one option is entailed (asserted).
  - In half the items, roles are swapped so that the correct option is also the cue-maximising one.
  - 4 cyclic rotations × 2 label schemes.
  - Option word counts are recorded as covariates, not matched.
  - Yield *est.*: the dev search needs thousands of premise sets once a two-way tie for the shortest option is required (so `LENGTH-SHORT` alternates across rotations and stays identified); to be measured in the pilot.
- **Premise order.**
  - A chain: a fact f; R1 = "either ¬f, or g"; R2 = "either ¬g, or c". Plus 1–2 distractor disjunctions on other atoms. All 6 permutations.
  - Reject unless ≥ 3 zoo members differ across the permutations: PyETR, `PREMISE-SUBSET(last 2)`, `PRIMACY-YN`, `RECENCY-YN`.

**E5.**

- **SAT.**
  - n ∈ {12, 16}, α ∈ [3.8, 4.3].
  - Keep a formula only if it is SAT and F ∧ F̄ is UNSAT. Half the kept items must also have a unique solution.
  - Measured at n = 10, α = 4.0: 0.85 of random formulas are SAT with F ∧ F̄ UNSAT; 0.11 also have a unique solution.
- **COL.**
  - n ∈ {10, 14}, k ∈ {3, 4}.
  - Plant k friend groups (sizes as equal as possible), add cross-group pairs with p = 0.2, and shuffle the pair list.
  - Require: G k-colourable (textbook answer exists); Ḡ k-colourable (inverted answer exists; true by planting); FIRST-FIT on G fits in k rooms.
  - Disjointness holds automatically for n > k (asserted).
  - About 1 in 2 draws accepted at n = 10 (*est.*, from the example build).
- **ENT.**
  - 5–6 atoms, 2–3 "either…or" premises.
  - Require the entailed-literal sets under the NOR and OR readings to differ and both be non-empty.
- **KNAP.**
  - n = 10, weights U{1..20}, values U{1..30}, capacity = 0.5 × total weight.
  - Require the packing optimum ≠ the covering optimum.
- **Preambles.** N and I are written as a pair, with word count ±0 and tokens ±3 per tokenizer (asserted). I+R adds one sentence. For P, half the constraints are chosen uniformly and marked ★.

**E6.**

- 7 atoms, 4–5 premises, |Mod(P)| ∈ {16, 32}.
- Conclusions are two-literal disjunctions with exactly one negated literal, which keeps form, polarity and length constant.
- Six conclusions per set, at ρ ∈ {0, 1/16, 1/8, 1/4, 1/2}, plus the largest available ρ ≥ 5/8 (an exact 3/4 is often unavailable).
- **Selection:** draw a pool 5× the target size, then select greedily so that |corr(ρ, κ)|, |corr(ρ, η)| and |corr(ρ, ETR)| are each < 0.1.
- 2 × 2 subset: ρ ∈ {1/16, ½} × κ ∈ {≤ 0.05, ≥ 0.20}.
- Measured at 5 atoms and |Mod| = 16: 1.6% of premise sets accepted at 6 atoms, 3 premises (2–3 disjuncts each), |Mod| = 16; 0 of 76k at 5 atoms / 2 premises. The study's 7-atom version needs a pilot measurement..

**E7.**
- Bases come from the E3 generator in the cells nearest each model's n\*.
- R1: a random permutation of variable indices (fixed-width names keep token counts). R2: random clause order and random literal order within clauses. R3: both.
- Echo variant: the copy instruction is inserted before the question. Yield 1.

**E8.**
- No generator. Continuations are built from each model's own `BE` responses.
- Truncation at token positions ⌊f·L⌋.
- Transplants only between E2 K and J of the same base.
- Mistake insertion: take the first parsed `ASSIGN`/`PROP` event after 0.5·L, flip its value, and resume generation.

**E9.**
- Example pools (study: n = 12; dev: n = 6) at α ∈ {3.0, 6.0}.
- **Environments:**
  - V: 4 low-α SAT + 4 high-α UNSAT;
  - N: 2 of each (α, g) combination;
  - R: 4 low-α UNSAT + 4 high-α SAT.
- The order is shuffled with a seed per prompt. The test item is E2 K or J.
- Rejection sampling for the rare classes. Measured at n = 6: P(UNSAT | n = 6, α = 3) = 0.007 (≈ 140 draws per example); P(SAT | n = 6, α = 6) = 0.36. At n = 12 the low-α UNSAT class is rarer still, so it is drawn from a large pre-generated pool.

### 2.9 Coverage: question sets × competing theories

Each cell is the **smallest weight detectable with 80% power** at the planned N, for the best-resolved member of that family, against its nearest competitor in that set. The nearest competitor is the theory with the most similar predictions (smallest KL divergence); the detectable weight comes from the Fisher information of a two-component mixture at π = 0, with a slip floor of 0.05. It is computed from the verified library items in [A_H_baselines_questions.md](A_H_baselines_questions.md).

A blank cell means the family is not among the set's theories. *n.i.* means it is present but has identical predictions to some other theory there, so the set gives it no resolution. "> 1" means the set cannot resolve that family's weight at the planned N.

Smaller numbers mean sharper evidence. A value ≤ 0.10 means the set can push that family's weight to within about 0.1 of zero (upper 95% bound ≈ 0.66 × the cell value).

| Set | exact | NOISY-EXACT | PERCEPTION-NOISE | RANDOM | SAMPLE-m | A1 constant | A2 DENSITY | A2 LENGTH | A2 FREQ / ATMOSPHERE | A2 PRIMACY / RECENCY | LABEL-A | A3 TT | B1 | B4 | C0 | C1 | D | F | D∘A | I adaptive |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E1-SAT | 0.26 | 0.13 | 0.17 | 0.04 | 0.26 | 0.09 | 0.09 | 0.26 |  |  |  |  | 0.09 |  | 0.01 | 0.27 | 0.09 | 0.24 |  |  |
| E1-ENT | > 1 | 0.93 | > 1 | 0.10 | > 1 | 0.17 |  |  | 0.17 | 0.17 |  |  | > 1 | 0.17 |  |  | 0.17 |  |  |  |
| E2-SAT | 0.30 | 0.14 | 0.24 | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 |  |  |  |  |  |  | 0.05 | 0.05 | 0.30 | 0.28 | 0.05 |  |
| E2-ENT | > 1 | 0.25 | > 1 | < 0.01 | 0.16 | 0.02 |  |  | 0.02 | 0.02 |  |  | 0.02 | 0.02 |  |  | 0.04 |  |  |  |
| E3 | 0.74 | 0.49 |  | 0.02 | 0.33 | 0.61 | 0.07 | 0.12 |  |  |  |  |  |  |  | 0.61 | 0.09 | 0.74 |  |  |
| E4 | 0.04 |  |  | 0.02 | 0.04 |  |  | 0.02 | 0.04 | 0.02 | 0.04 |  |  | 0.04 |  |  |  |  |  |  |
| E4-order | 0.48 | 0.34 | 0.22 | 0.06 | 0.48 | 0.04 |  |  | 0.04 | 0.04 |  |  | 0.04 | 0.04 |  |  | 0.48 |  |  |  |
| E5-COL | 0.05 |  | 0.05 | 0.03 |  | 0.10 |  |  |  |  |  | 0.01 | 0.02 |  |  | 0.10 |  |  |  |  |
| E5-SAT | 0.03 |  |  | > 1 |  | > 1 |  |  |  |  |  | 0.03 |  |  |  |  |  |  |  |  |
| E6 | > 1 | 0.32 | 0.94 | < 0.01 | 0.07 | 0.03 |  |  | 0.03 | 0.06 |  |  | 0.06 | 0.06 |  |  | 0.04 |  |  |  |
| E7 | 0.64 | 0.46 |  | 0.02 |  | 0.07 | 0.07 | 0.07 |  |  |  |  |  |  | 0.64 | 0.07 | 0.07 | 0.64 |  |  |
| E8 |  |  |  |  |  |  | 0.09 |  |  |  |  |  |  |  |  |  |  |  | 0.08 |  |
| E9 | 0.04 |  |  |  |  |  | 0.01 | 0.04 |  |  |  |  |  |  |  |  |  |  |  | 0.04 |
| **best in library** | **0.03** | **0.13** | **0.05** | **< 0.01** | **0.04** | **0.02** | **0.01** | **0.02** | **0.02** | **0.02** | **0.04** | **0.01** | **0.02** | **0.02** | **0.01** | **0.05** | **0.04** | **0.24** | **0.05** | **0.04** |

**Pairs never separated anywhere in the library** (identical predictions in every set where both appear):

- none: every pair of theories that appears together in some set is separated by at least one set.

**Not covered by this library, by design.** These families are not competitors on these item types:

- **E (message passing)** predictions are computed per item in the study (`WP-t`, `BP-t`), but are not part of this dev library. Its separating sets belong to the E vertical.
- **G (decompose)** reduces to its inner solver on the connected random instances used here.
- **B4-internal distinctions** (`FIRST` vs `MATCH` vs `ETR` vs `MM`) are resolved where they differ in E1-ENT / E2-ENT / E4-order. Their full resolution is the B4 vertical's job.


---

## 3. Mechanistic evidence: Phase 2 (only if behavioural evidence)

Run only if Phase 1 finds an A-family member whose π has a lower 95% bound ≥ 0.10 in some model × condition. For thinking models, A-family evidence would come mainly from E1 blindness above n\* together with E2 cue moves or E8 silent cue use.

- **State variables.**
  - For `DENSITY`: a linearly decodable α. It must be decodable *beyond* the best linear function of separately decoded m and n, which tests whether the ratio is actually computed. The read-out positions are the end of the prompt and the pre-think position.
  - For `PRIMACY`: option position bound to its content.
  - For `TT`: whether the rule semantics is represented at the constraint positions.
- **Probes.** Linear probes, each with:
  - Hewitt & Liang control tasks (labels permuted across items);
  - format residualisation for m, tokens and premise count (Sahoo et al. 2026);
  - a random-init baseline of the same architecture (Sutter et al. 2025);
  - a **g probe** as the reverse control: it should be near chance in blind models.

  All are in report C.
- **Interventions.**
  - DAS / interchange on the α subspace between E2 K and J items. Prediction: the answer moves toward the source's `DENSITY` prediction, more than under the same intervention on competitor variables (unit-propagation contradiction, solution-density, a DPLL node-count proxy) and more than under norm-matched orthogonal steering (Cox et al. 2026).
  - LEACE erasure of α at the probe layers (Belrose et al. 2023 **[v]**). Prediction: the E2 contrast collapses while any g-dependence remains, and an erasure of equal rank on a control concept does nothing.
  - For thinking models: steer at the pre-think position and test whether the final post-think answer still moves.
- **Positive controls.**
  1. A 4-layer toy trained on 3-SAT with label = 1[α_U > 4.26] and variable n. It must use α by construction.
  2. A matched-pair-trained toy, where α carries no information (negative control).
  3. The Ye et al. 2025 capacity toy: beyond capacity, its degree heuristic is a known A2-like cue.
  4. A DENSITY rule planted by SIIT (InterpBench style) into weights with a realistic distribution.

  The pipeline must find α causally in toys 1, 3 and 4, and not in toy 2.
- **Models** (no tiny models; the toys in the positive controls are training controls, not subjects):
  - gpt-oss-20b first, since it is the Phase 1 lead model and has a CLT in circuit-tracer (report C).
  - Qwen3-8B and Qwen3-14B: transcoders exist up to 14B, and thinking and non-thinking modes share a checkpoint. The 8B → 14B → 32B step (32B by probes only, no transcoders) tests whether the cue is *represented but unused* at larger scale.
  - R1-Distill-Llama-8B versus Llama-3.1-8B: the effect of reasoning tuning.

| ID | Model | Method | Prediction | Quantity reported (with 95% CI) | Evidence that moves weight away |
|---|---|---|---|---|---|
| M1 | gpt-oss-20b; Qwen3-8B / 14B / 32B; NT and pre-think | α / m / n / g probes with controls | α decodable beyond m and n; g at chance in blind models | Probe selectivity (pp over control); R² of α beyond the best linear function of decoded m and n | Selectivity CI including 0, or α explained by linear m, n |
| M2 | gpt-oss-20b; Qwen3-8B / 14B; R1-Distill-Llama-8B | DAS on the α subspace (E2 pairs); LEACE; steering versus norm-matched baselines | Answer moves as `DENSITY` predicts, more than for competitor variables; random-init fails | Interchange-intervention accuracy (IIA) minus the competitor's IIA; the share of the E2 contrast removed by LEACE erasure (≈ the mechanistic share of π_DENSITY) | Competitor or random-init IIA within 5 pp |
| M3 | Toys 1–4 | The same pipeline | Recovers the known use | Recovered versus planted cue reliance, with bias and CI | Bias > 0.1 on any toy |

---

## 4. Evidence-table row

| Behavioural lift over baseline | Mixture weight | Signatures matched | Process match | Probe selectivity | Intervention vs competitor | Control recovered | RASP-L length / class |
|---|---|---|---|---|---|---|---|
| B\*'s held-out log-likelihood gain over q and over constant π (nats/item, 95% CI); error lift of each member over the cue-stratified permutation baseline (pp, 95% CI) | π_h posterior mean and 95% interval per member × model × condition; π_h(φ) curves where feature-dependent (§5) | Per eval, the shift in weight Δπ the set produces and the bound it achieves (e.g. π_struct ≤ 0.075) | Trace-implied weight π_h^tr = (s_h − fp_h)/r̂ next to π_h^ans; r̂ from E8 | Phase 2 | Phase 2 | Phase 2 | §1.7 (const) |

---

## 5. Weight bounds, and how I is fitted and validated

### 5.1 What drives each family's weight toward zero, and how tightly

Nothing is "falsified" as a whole. A family's weight is pushed toward zero with a stated bound. The bounds are at the planned N, under the assumption that the model's remaining weight sits on the nearest competitor (the most similar predictions; question library, weight-resolution tables).

| Family / member | Evidence that moves weight away from it | Bound achievable at planned N: upper 95% on π if its weight is truly 0 (best set; computed in the library) |
|---|---|---|
| A1 (constants) | Answers move with structure (E1 D̂ > 0) or with cues (E2 contrasts ≠ 0); test–retest identity | 0.011 (E2-ENT) |
| A2 `DENSITY` | E2 K − J ≈ 0 while K − base > 0, which moves weight to `LENGTH`; E3 knee tracking n or g; E9 reversal, which moves weight to adaptive I | 0.009 (E9); 0.03 (E2-SAT) |
| A2 `LENGTH` | E2 K ≠ J at equal m; the E3 equal-m cells differing; E4 length tie | 0.011 (E4); 0.03 (E2-SAT) |
| A2 `FREQ` / `ATMOSPHERE` | No FREQ / mood contrast within matched conclusion sets (E2-ENT) | 0.011 (E2-ENT) |
| A2 `PRIMACY` / `RECENCY` / `LABEL-A` | Choices following content across rotations and label schemes (E4); order invariance (E4-order) | 0.011 (E2-ENT, E4); `LABEL-A` 0.025 (E4) |
| A3 `TT` | No textbook answers on I beyond coincidence; identity ratio ≈ 0 (E5) | 0.010 (E5-COL); 0.02 (E5-SAT) |
| H `RANDOM` | Test–retest agreement; predictability from cues or structure | 0.002 (E2-ENT) |
| H `SAMPLE-m` | A flat ρ curve with κ and η controlled (E6); SAMPLE(k) traces disagreeing with (1 − ρ)^k | 0.025 (E4); 0.05 (E6) |
| `NOISY-EXACT` | Systematic error variance σ²_u (E7); a directional crossover under padding (E2); asymmetric errors on pairs (E1) | 0.086 (E1-SAT): the weakest bound among our families |
| `PERCEPTION-NOISE` | Echo errors not aligned with violations (E7-echo); P-framing violations concentrated on ★ (E5); no UNSAT-side error excess (E1) | 0.034 (E5-COL) |
| I (selection) | Constant π fitting as well as feature-dependent π; dependence absorbed by size-dependent noise (§5.3) | adaptive-versus-fixed `DENSITY` weight resolved at 0.04 (E9, exploratory) |

These are dev-library values at the study N. They assume deterministic signatures and a slip floor of 0.05. With soft (fitted) cue curves they scale as 1/c.

Families outside this group (B1, B4, C0, C1, D, F, D∘A) appear here only as competitors. The weight resolution this library gives them is in the coverage matrix (§2.9); their own verticals carry the sets that resolve them fully.

### 5.2 The I model

**The mixture.** P(y | x, model, cond) = Σ_h π_h(x) · P(y | h, x, λ_h) + π_0 · q(y | x).

**Components.**
- The component set is *every* zoo member across all verticals, plus q.
- Component likelihoods are precomputed and channel-matched (§0.2), with a slip parameter λ_h ~ Beta prior restricted to ≤ 0.3.
- `NOISY-EXACT`'s size dependence lives **inside** its component, through ε(L(x)), not in the selector.

**The selector.** π_h(x) = softmax_h(β_{h0} + β_h · φ_sel(x) + u_{h, model}).
- Pre-registered φ_sel:
  - domain and framing (textbook / costumed / inverted);
  - a natural-cubic-spline basis in log n (3 knots);
  - the standardised hardness parameter (α, mean degree, or the number of disjunctive premises), and m;
  - condition (`BE` / `B-4k` / `NT`);
  - key-premise position and answer format;
  - log solution density;
  - model random effects, with a log-parameter-count slope within families.
- A regularised-horseshoe prior on β gives sparsity.

**Fitting.** NUTS in numpyro, on per-item × component likelihood tables. Family weights are sums over members.

**Two stochastic specifications** (Davis-Stober & Brown 2011, report B), compared by held-out log-likelihood on the 25% of items with repeat samples:
- S1: the strategy is fixed per item, so all samples of x come from one h.
- S2: the strategy is drawn per response.

**Trace channel** (optional): the joint likelihood of §2.5.5. Within-trace switching ("first heuristic, then rational"; Aoki et al. 2024, report B) is described with a segment-level hidden Markov model over code sequences. It is **descriptive only** in Phase 1.

### 5.3 Identifiability and validation

**Identifiability.** The components are known functions of x, up to λ_h. So the weights at a feature value are identified exactly when the components' answer distributions are linearly independent over the items near that value. In practice: for every pair (h, h′), there must be items **in that feature region** where h(x) ≠ h′(x).

The finite-mixture theory in Allman, Matias & Rhodes 2009 **[v]** bears on the latent-class case, but known components make the condition this simple rank condition. Diagnostics:

1. **Per feature bin** (log n tercile × domain × framing × condition), form the item × component prediction matrix M_bin.
   - Require σ_min/σ_max ≥ 0.05 (pre-registered).
   - Where a bin fails, the members that are not separable there are **merged** into a composite for reporting. For example, at high α on natural instances, `ALWAYS-UNSAT`, `DENSITY`, `D∘A` and `SAMPLE-m` coincide. E2 padding items exist to fill exactly these bins.
2. **Posterior correlations** with |corr(π_h, π_h′)| > 0.7 are reported as "not separately identified at this design".
3. **The λ–π trade-off.** A component with λ near 1 − 1/|Y| is `RANDOM`. Cap λ, fit `RANDOM` explicitly, and report sensitivity to the cap.
4. **Selection versus noise.** Fit (a) the full model and (b) constant π with size-dependent noise only. Feature dependence is claimed only if (a) beats (b) on held-out log-likelihood by ≥ 0.01 nats/item, *and* E7 shows systematic (σ²_u > 0) errors in the regions where selection shifts.

**Validation by recovering planted agents** (run before any LLM data; DESIGN §5.12).

- 200 synthetic agents are simulated on **the exact item sets and sample counts** used for the LLMs, including forced-at-cap strata (simulated by truncating `DPLL-b`).
- **Planted agents use graded mixtures**, not single heuristics:
  - **P1 (single members, as a sanity check):** each A/H/nuisance member alone, with 10% slips.
  - **P2 (three-way constant mixtures):** `DENSITY` / exact / `NOISY-EXACT` at 0.6 / 0.3 / 0.1, 0.3 / 0.6 / 0.1 and 0.1 / 0.3 / 0.6; `ALWAYS-UNSAT` / C1 / exact at 0.2 / 0.5 / 0.3; `TT` / exact / `PERCEPTION-NOISE` at 0.5 / 0.4 / 0.1.
  - **P3 (feature-dependent):** π_DENSITY(n) = 0.7 · σ(5 · (log n − log 24)), with π_exact = 1 − π_DENSITY − 0.1 and π_NOISY = 0.1. This is a planted budget line with a smooth knee; splines in log n approximate it.
  - **P4 (framing-dependent):** π_TT = 0.5 in inverted framings and 0 elsewhere, with the rest split 0.8 / 0.2 between exact and C1.
  - **P5 (the noise confound):** `NOISY-EXACT` with ε rising in n and *constant* weights 0.5 / 0.5 with exact. This must **not** be recovered as feature-dependent selection.
  - **P6 (withheld member):** 30% weight on `MOMS`, or on a 10-cue logistic "bag of cues" agent fitted to pilot data, the rest on exact. The withheld mass must go to q or spread out, with < 0.2 of it on any single zoo member.
  - **P7 (`D∘A`):** `DPLL-b` with a `DENSITY` default at the cap, at 0.7, plus exact at 0.3.
  - **P8 (random sparse selectors from the prior):** 1–3 active families, base weights drawn from Dirichlet(1, 1, 1), and feature slopes of 0.5–2 logit/SD.
- **Reported per planted weight** (not top-1 accuracy):
  - the bias E[π̂_h − π_h];
  - the RMSE;
  - the 95% interval width;
  - the 95% interval coverage;
  - for feature-dependent weights, the same quantities for π_h(φ) at the 10th, 50th and 90th percentiles of φ.
- **Pre-registered pass criteria at the planned N:**
  - |bias| ≤ 0.03 for every planted weight ≥ 0.1;
  - median 95% interval width ≤ 0.15;
  - coverage in [0.90, 0.97];
  - RMSE of π_h(φ) ≤ 0.08 across items;
  - in P5, the false-positive rate for feature dependence ≤ 5%;
  - in P6, misattribution < 0.2 of the withheld mass to any single member;
  - in P7, the default identified in ≥ 80% of agents.
- **If a criterion fails for a weight,** that weight is reported only as a composite with the members it is confused with. The interval widths from this study are the resolution limits quoted in the paper.

**Weight statements for I.**
- The feature-dependent model's held-out gain over the best constant-π mixture, in nats/item with a 95% bootstrap interval, is reported as the strength of selection.
- Each selector slope β_h is reported with its interval, and as the change in π_h across the observed range of the feature (Δπ_h, 95% interval).
- I carries explanatory weight to the extent that this gain is positive after the selection-versus-noise comparison (4 above), and that the Δπ_h agree across the models of a family ladder (reported as the between-model SD of β_h).

---

## 6. Build scope

**Shared infrastructure this vertical depends on.** These should be built once, not here:

- content-hashed item store (DESIGN §5.1);
- runner: vLLM, reasoning-effort and budget control, forced answer at the cap, logprobs, prefix caching for E8;
- exact solvers with instrumentation: PySAT/MiniSat node counts, colouring via PySAT, z3/PySMT, PyETR;
- MaxSAT (RC2) for d_min;
- model counting by enumeration (≤ 10 atoms, n ≤ 24);
- zoo registry and base class;
- the core mixture engine (`identify/`);
- the α × n sweep (budget-line vertical);
- **the trace codebook, parsers, LLM coder and hand-labelling.** These should be shared, because every vertical needs the same event inventory. They are listed below because A/H/nuisance codes are defined here.

| Component | Person-days | Shared? |
|---|---|---|
| Reference implementations: A1/A2/A3 for every domain, with soft-threshold fitting | 3.0 | — |
| H: `RANDOM-U/B`, `SAMPLE-m` with exact likelihoods | 2.0 | — |
| Nuisance: `NOISY-EXACT` (MaxSAT d_min, instrumented L), `PERCEPTION-NOISE` (Monte Carlo likelihood) | 3.0 | — |
| E1 invariance-pair generators (three domains), feature-equality assertions, null pairs | 4.0 | — |
| E2 padding generators (SAT K/J/U, COL components); ENT matched conclusion search | 4.0 | — |
| E4 MC builder from zoo outputs, Latin squares, label schemes, permutations | 2.0 | — |
| E5 inversion maps, disjointness rejection, length-matched preambles, partial inversion | 4.0 | — |
| E6 ρ/κ/η computation and decorrelated design selection | 3.0 | — |
| E7 tokenizer-checked renaming, shuffles, echo prompts and echo parser | 2.0 | — |
| E9 environment builder | 1.0 | — |
| Trace parsers: assignments, quotes, replay, option evaluation, lexicons, final state | 5.0 | **should be shared** |
| LLM coder: prompt, span verification, κ and differential-error harness | 3.0 | **should be shared** |
| Hand-labelling: 450 traces × 2 coders, windowed, plus adjudication | 13.0 (coder-days) | **should be shared** |
| E8 continuation harness: early answering, transplant, mistake insertion | 3.0 | — |
| Analysis: E1 (McNemar, TOST, GLMM, trace divergence) | 2.0 | — |
| Analysis: E2 signature matching (out of sample from E3) | 1.5 | — |
| Analysis: E3 knee trajectories versus simulated | 2.0 | — |
| Analysis: E4 conditional logit | 1.5 | — |
| Analysis: E5 TT rate, identity, violation profiles | 1.5 | — |
| Analysis: E6 dose-response and the trace law | 1.5 | — |
| Analysis: E7 variance components, entropy, echo alignment | 2.5 | — |
| Analysis: E9 | 0.5 | — |
| I: feature-dependent mixture, channel matching, identifiability diagnostics, planted-agent simulator and recovery study | 7.0 | Core engine shared; the extension is here |
| B\* contract and cue-stratified permutation baseline (delivered to all verticals) | 1.5 | Delivered here |
| Pilot: tokenizer cue matching (4 tokenizer families), truncation calibration | 2.5 | — |
| **Total, Phase 1** | **≈ 76** (of which ≈ 21 should be shared trace infrastructure) | |
| Phase 2: probes and controls, DAS / LEACE / steering, 4 toys | ≈ 15 | — |

---

## 7. Compute budget

**Conditions:**
- `BE` = best effort, 32k thinking cap, forced answer at the cap.
- `B-4k` = thinking forced to 4k, on 30% subsets.
- `NT` = non-thinking, on 30% subsets, Qwen3 and gpt-oss only.

Samples/item of 1.25 means a second sample on 25% of items. Output tokens are thinking plus answer.

**Dev batches.** Each eval has a **Dev batch** row: the smallest item set that still fills every cell of its counterfactual design, at 5–10 items per cell. Dev batches run on **gpt-oss-20b (high effort) under `BE-32k` only**. They exist to iterate quickly on generators, prompts, parsers and analysis code. Their results never enter the pre-registered analyses. The cells each dev batch covers:

- **E1:** per domain, 3 sizes × {critical, null SAT→SAT, null UNSAT→UNSAT} × 5 pairs = 45 pairs (90 items). For ENT, the 15 critical pairs are spread over the 4 propagation-depth strata, ≥ 3 per stratum. Framing alternates CNF / natural language.
- **E2:** SAT and COL: 4 levels × 2 g × 8 bases = 64 items. ENT: 8 premise sets × 8 conclusions (the full 2 × 2 × 2) = 64.
- **E3:** 9 α (or degree) levels × 3 n values {10, 20, 40} × 5 items = 135 per domain.
- **E4:** MC: 10 items (5 where the correct option is also the cue-maximising one, 5 where it isn't) × 8 renderings = 80. Premise order: 8 items × 6 permutations = 48.
- **E5:** per domain, 8 bases (4 with a unique textbook solution, 4 with several) × 4 framings + 8 partial-inversion items = 40.
- **E6:** ENT: 8 premise sets × 6 ρ levels + 5 sets × the 2 × 2 (ρ × κ) = 68. SAT: 5 log-s bins × 6 = 30.
- **E7:** per domain, 10 items × 4 renderings = 40, plus 8 echo items.
- **E8:** 10 responses from each of E1 / E2 / E5 / E6 dev runs, giving 160 early-answer, 20 transplant and 10 mistake-insertion continuations.
- **E9:** 3 environments × {K, J} × 8 = 48.

All dev batches together come to ≈ 1,310 items, ≈ 16.5M output tokens and 2.9M prompt tokens on gpt-oss-20b. That is under 2 hours of decode on one node at the throughput assumed below, and less on a model of gpt-oss-20b's size. They are **estimates to be calibrated by the pilot**, informed by two findings in report A: Verma 2026, where random UNSAT items hit a 16k budget; and Hazra et al. 2025, where R1's token use stays high on over-constrained items.

| Eval ID | Domain | # items | Conditions (e.g. direct, CoT-1k, CoT-4k) | Samples/item | Avg prompt tokens | Avg output tokens per condition | Needs activations? (Y/N) |
|---|---|---|---|---|---|---|---|
| E1 | SAT (n 16/24/36, α ≈ 4.26) | 1,200 | BE-32k; B-4k (30%); NT (30%) | 1.25 | 1,700 | BE 18,000 · B-4k 4,100 · NT 80 | N |
| E1 | COL (n 15/20/30, k = 3) | 1,200 | BE-32k; B-4k (30%); NT (30%) | 1.25 | 500 | BE 14,000 · B-4k 4,100 · NT 70 | N |
| E1 | ENT-YN (6/8/10 atoms) | 1,200 | BE-32k; B-4k (30%); NT (30%) | 1.25 | 420 | BE 7,000 · B-4k 4,100 · NT 5 | N |
| E1 Dev batch | SAT / COL / ENT (3 sizes × 3 pair types × 5 pairs per domain) | 270 (90 per domain) | BE-32k, gpt-oss-20b only | 1.2 | 1,700 / 500 / 420 | BE 18,000 / 14,000 / 7,000 | N |
| E2 | SAT (core n = 24 + K/J/U) | 1,200 | BE-32k; B-4k (30%); NT (30%) | 1.25 | 1,800 | BE 16,000 · B-4k 4,100 · NT 80 | N |
| E2 | COL (n 20 + components) | 1,200 | BE-32k; B-4k (30%); NT (30%) | 1.25 | 650 | BE 12,000 · B-4k 4,100 · NT 80 | N |
| E2 | ENT-YN (matched conclusions) | 1,600 | BE-32k; B-4k (30%); NT (30%) | 1.25 | 450 | BE 7,000 · B-4k 4,100 · NT 5 | N |
| E2 Dev batch | SAT / COL (4 levels × 2 g × 8 bases); ENT (8 sets × 8 conclusions) | 192 (64 per domain) | BE-32k, gpt-oss-20b only | 1 | 1,800 / 650 / 450 | BE 16,000 / 12,000 / 7,000 | N |
| E3 (shared sweep) | SAT (α 3–6 × n 10–40) | 1,800 | BE-32k; B-4k (30%); NT (30%) | 1 | 1,450 | BE 15,000 · B-4k 4,100 · NT 80 | N |
| E3 (shared sweep) | COL (9 degrees × n 10–40) | 1,800 | BE-32k; B-4k (30%); NT (30%) | 1 | 520 | BE 12,000 · B-4k 4,100 · NT 70 | N |
| E3 Dev batch | SAT / COL (9 levels × n {10, 20, 40} × 5) | 270 (135 per domain) | BE-32k, gpt-oss-20b only | 1 | 1,450 / 520 | BE 15,000 / 12,000 | N |
| E4 | ENT-MC (200 × 8 renderings) | 1,600 | BE-32k; NT (30%) | 1 | 500 | BE 8,000 · NT 5 | N |
| E4 | ENT-YN premise order (150 × 6) | 900 | BE-32k; NT (30%) | 1 | 420 | BE 6,000 · NT 5 | N |
| E4 Dev batch | ENT-MC (10 items × 8 renderings); ENT-YN (8 × 6 permutations) | 128 | BE-32k, gpt-oss-20b only | 1 | 500 / 420 | BE 8,000 / 6,000 | N |
| E5 | SAT (n 12/16) | 900 | BE-32k; NT (30%) | 1.25 | 1,250 | BE 10,000 · NT 60 | N |
| E5 | COL (n 10/14) | 900 | BE-32k; NT (30%) | 1.25 | 480 | BE 7,000 · NT 60 | N |
| E5 | ENT-OPEN (5–6 atoms) | 900 | BE-32k; NT (30%) | 1.25 | 480 | BE 7,000 · NT 30 | N |
| E5 | KNAP (n = 10) | 800 | BE-32k; NT (30%) | 1.25 | 420 | BE 6,000 · NT 30 | N |
| E5 Dev batch | SAT / COL / ENT / KNAP (8 bases × 4 framings + 8 partial per domain) | 160 (40 per domain) | BE-32k, gpt-oss-20b only | 1.2 | 1,250 / 480 / 480 / 420 | BE 10,000 / 7,000 / 7,000 / 6,000 | N |
| E6 | ENT-YN (7 atoms) | 1,600 | BE-32k | 1.25 | 480 | BE 7,000 | N |
| E6 | SAT (n = 20, α = 4.0) | 300 | BE-32k | 1 | 1,500 | BE 12,000 | N |
| E6 Dev batch | ENT (8 sets × 6 ρ + 5 sets × 2 × 2); SAT (5 log-s bins × 6) | 98 | BE-32k, gpt-oss-20b only | 1 | 480 / 1,500 | BE 7,000 / 12,000 | N |
| E7 | SAT (150 × 4 renderings) | 600 | BE-32k | 1.5 | 1,700 | BE 16,000 | N |
| E7 | COL (150 × 4) | 600 | BE-32k | 1.5 | 560 | BE 12,000 | N |
| E7 | ENT-OPEN (150 × 4) | 600 | BE-32k | 1.5 | 420 | BE 8,000 | N |
| E7-echo | SAT (n 16) / COL / ENT | 450 | BE-32k, echo-first prompt | 1 | 750 | BE 11,000 (including ≈ 1k echo) | N |
| E7 Dev batch | SAT / COL / ENT (10 items × 4 renderings) + 8 echo items per domain | 144 | BE-32k, gpt-oss-20b only | 1.5 (renderings); 1 (echo) | 1,700 / 560 / 420; echo 750 | BE 16,000 / 12,000 / 8,000; echo 11,000 | N |
| E8 | Continuations of 750 E1/E2/E5/E6 responses: 3,000 early-answer, 200 × 2 transplant, 200 mistake-insertion | 3,600 continuations | Forced answer after a truncated, spliced or edited trace | 1 | 6,000 (prompt + trace prefix; mostly prefix-cached) · transplant 15,000 · insertion 8,000 | forced 30 · insertion 6,000 | N |
| E8 Dev batch | 40 dev responses (10 each from E1/E2/E5/E6 dev): 160 early-answer, 20 transplant, 10 mistake-insertion | 190 continuations | Forced answer, gpt-oss-20b only | 1 | 6,000 · transplant 15,000 · insertion 8,000 | forced 30 · insertion 6,000 | N |
| E9 | SAT (E2 K/J test items) | 600 | BE-32k | 1 | 7,000 (8 in-context examples + item) | BE 15,000 | N |
| E9 Dev batch | 3 environments × {K, J} × 8 | 48 | BE-32k, gpt-oss-20b only | 1 | 7,000 | BE 15,000 | N |
| TC | Trace coding (25% of BE traces, plus 100% of E1-critical and E5) | ≈ 6,500 traces per model | Coder LLM, non-thinking | 1 | 12,500 (trace + codebook) | 400 | N |
| TC Dev batch | Codebook iteration: 30 dev traces per domain, hand-coded and LLM-coded | 90 traces | Coder LLM, non-thinking | 1 | 12,500 | 400 | N |
| M1 (Phase 2) | Probes: E1 / E2 / E3-SAT subsets | 5,000 | NT forward pass + pre-think position | 1 | 1,100 | 0 | Y |
| M2 (Phase 2) | DAS / LEACE / steering on E2 pairs | 1,200 | NT and BE (steered pre-think) | 1 | 1,800 | NT 80 · BE 16,000 (300 items) | Y |
| M3 (Phase 2) | Toys 1–4 | 20,000 synthetic | Training + evaluation | — | 400 | — | Y |

**Totals.**

- **Items:** ≈ 21,950. That is 18,350 new items for this vertical plus the 3,600-item shared sweep.
- **Per model:** ≈ 278M `BE` output tokens, 14M `B-4k` output, 24M prompt, 1.3M E8 output.
- **Across the 12 primary models:**
  - ≈ **3.5B output tokens** and 0.65B prompt tokens;
  - ≈ 0.69B of the output comes from the shared sweep;
  - trace coding adds ≈ 0.85B coder input tokens.
- **Throughput:** at an assumed 2.5k tokens/s aggregate decode per 8-GPU node, that is ≈ 400 node-hours. This is a rough figure; the pilot will measure it.

**Core tier, if the budget is tight:** E1 + E2 + E5 + E8, plus the shared E3. That is ≈ 150M output tokens per model, or ≈ 1.8B for 12 models. A second option is to run the full set on 6 anchor models (Qwen3-32B, Qwen3-235B-A22B-Thinking, gpt-oss-20b, gpt-oss-120b, DeepSeek-R1, R1-Distill-Qwen-14B) and only the core on the rest.

**Expected truncation at 32k** (pre-registered guesses, to be calibrated in the pilot):

| Item class | Share expected capped |
|---|---|
| SAT UNSAT, n = 36, near threshold (E1) | 70–90% |
| SAT UNSAT, n = 24 (E1; E2 bases; E9 test items) | 30–60% |
| SAT SAT, n = 36 | 20–40% |
| E3 SAT, n ≥ 30, α ∈ [3.8, 4.8] | 40–80% |
| SAT, n ≤ 16 (E1 small; E5; E7-echo) | < 10% |
| COL uncolourable, n = 30 / n = 20 | 50–80% / 20–40% |
| COL colourable, n ≤ 20 | < 10% |
| ENT, 10 atoms / ≤ 8 atoms | 5–15% / < 3% |
| E5 (deliberately below n\*), KNAP | < 5% |

Capped runs are the stratum where A and `D∘A` predictions matter most. They are kept, with forced answers, in the primary analyses (§1.3).

---

## 8. Threats that cut across evals, and open questions

1. **Prompt-format sensitivity.** CNF versus natural language, and the wording of the answer schema, are experimental factors (DESIGN §5.10). Framing enters I as a feature.
2. **The generator's own statistics** (Zhang et al. 2023, report B: models exploit generator features). Before any LLM run, train a small classifier on ψ(x) to predict g(x) on each generator, and report its accuracy. If cues predict g, our items reward cue use, and that has to be stated.
3. **Multiple comparisons.** There are 9 evals × 3 domains × 12 models × 3 conditions. Cross-model claims come from the hierarchical model, not from counting significant tests (DESIGN §5.7). Per-eval primary tests are Holm-adjusted within the eval.
4. **Open question for Andrew: the ENT size.** Is 6–10 atoms enough to put best-effort thinking models above n\*? If not, E1/E2-ENT become ceiling-bound, and E6 moves to 9–10 atoms.
5. **Open question for Andrew: the coder.** Which model codes traces? Proposal: Qwen3-32B in non-thinking mode, self-hosted and pinned, so that coding is reproducible and free of API drift.

---

## References used in this file

**From the repo's literature reports** (see those reports for links and verification tags):
- Report A: Zhang, Chen & Chen 2026; Hazra et al. 2025; Verma 2026; Heyman & Zylberberg 2025.
- Report B: EHOP (Duchnowski, Pavlick & Koller 2025); Chen et al. 2024 (premise order); McCoy et al. 2024 (embers of autoregression); Wu et al. 2024; Zhang et al. 2023 (paradox of learning to reason); Bertolazzi et al. 2024; Eisape et al. 2024; Aoki et al. 2024; Bröder & Schiffer 2003; Glöckner 2009; Davis-Stober & Brown 2011; Myung & Pitt 2009.
- Report C: Chen et al. 2025 (reasoning models don't always say what they think); Lanham et al. 2023; Cox et al. 2026; Arcuschin et al. 2025; Hewitt & Liang 2019; Sutter et al. 2025; Méloux et al. 2025; Sahoo et al. 2026; Ye et al. 2025; Gupta et al. 2024 (InterpBench).
- Report F: Kahneman & Frederick 2002; Rice 1976; Lieder & Griffiths 2017, 2020; Håstad 2001; Pearl 1983; algorithmic thresholds (Achlioptas 2001; Achlioptas & Sorkin 2000).
- DESIGN.md: Sinha et al. 2025.

**Verified this session [v]** (arXiv abstract pages):
- Belrose et al. 2023, *LEACE: Perfect linear concept erasure in closed form*, arXiv 2306.03819.
- McCoy, Pavlick & Linzen 2019, *Right for the Wrong Reasons* (HANS), ACL 2019, arXiv 1902.01007.
- Feng, Wallace & Boyd-Graber 2019, *Misleading Failures of Partial-input Baselines*, ACL 2019, arXiv 1905.05778.
- Poliak et al. 2018, *Hypothesis Only Baselines in Natural Language Inference*, \*SEM 2018, arXiv 1805.01042.
- Gardner et al. 2020, *Evaluating Models' Local Decision Boundaries via Contrast Sets*, arXiv 2004.02709.
- Allman, Matias & Rhodes 2009, *Identifiability of parameters in latent structure models with many observed variables*, Annals of Statistics 37(6A), arXiv 0809.5032.
- Zheng et al. 2024, *Large Language Models Are Not Robust Multiple Choice Selectors*, ICLR 2024, arXiv 2309.03882.
- Liu et al. 2024, *Lost in the Middle: How Language Models Use Long Contexts*, TACL, arXiv 2307.03172.
