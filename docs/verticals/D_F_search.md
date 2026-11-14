# Vertical: D (truncated systematic search) and F (local search / repair)

*One file covers both families. They share items, competitors and the trace-coding scheme, and each one's eval is the other's control. The file follows [TEMPLATE.md](TEMPLATE.md), expanded as the brief asks. Both families live mainly in the chain-of-thought condition.*

- **Status:** designed, v0.1 (2026-11-13). Nothing has been run.
- **Owner:** [TODO]
- **Phase:** Phase 1 is behavioural only (scope update from Andrew, 2026-11-13). §3 (interpretability) runs only if Phase 1 finds evidence for D or F.
- **Primary condition: best effort (BE).** Open-weight reasoning models at their highest reasoning effort, with a thinking cap of 32k tokens. Lower caps (2k, 8k) are an experimental factor, used to fit *b* in `DPLL-b` and to test H3. No tiny models. **The first model is gpt-oss-20b at high effort.**
- **Members.** D: `DPLL-b`, `BEAM-w`, `BACKDOOR-k`. F: `MIN-CONFLICTS`, `WALK-k`, `2OPT-k`, `SA`.
- **Competitors this vertical must beat:**
  - C (greedy, never revises);
  - B1 `UP-k`, plus stronger sound propagation (failed-literal probing, `2SAT-CORE`);
  - nuisance `NOISY-EXACT` and `PERCEPTION-NOISE`;
  - A cues (`ALWAYS-SAT`, `DENSITY`, `POLARITY`, `ECHO`);
  - H `RANDOM`.
- **Readout: graded weights, not verdicts.** Heuristics may be partly used. Every result is a mixture weight π_h (posterior mean, 95% interval), a lift over chance, a log-likelihood gain over the null and over the nearest competitor, and an R_m-weighted trace share (§2.5). Weights may depend on item features and on the model (family I, strategy selection).
- **Example library:** [D_F_search_questions.md](D_F_search_questions.md) has 40 computationally verified items covering every eval's cells, each with a per-theory hypothesis block and likelihoods. The machine-readable copy is [`data/examples/D_F_search.jsonl`](../../data/examples/D_F_search.jsonl). Generator specs are in §2.9 and the coverage matrix in §2.10.

---

## 0. At a glance

| ID | Question (falsifiable) | Key counterfactual | Main contrast |
|----|------------------------|--------------------|---------------|
| **E1** Budget line | With size, does accuracy fall along *search work ÷ budget* (D), along *work alone* (`NOISY-EXACT`), or along neither? | The same matched SAT/UNSAT pairs at caps of 2k, 8k and 32k, with a size sweep centred on each model's *n\** | D vs NE vs C vs A |
| **E2** Fitting *b* | Does one *b* per (model, budget) predict *which* items fail? Does failure follow DPLL work or local-search difficulty? | 2×2 quadrants at fixed *n* and α: DPLL work (low/high) × WalkSAT flips (low/high) | D vs F vs NE |
| **E3** Backdoor | At fixed *n* and α, does accuracy fall with backdoor size *k\**, at a threshold that moves +1 per doubling of budget? Does the model branch by text position? | Natural formulas selected on *k\** ∈ {2, 3, 4} × presentation (the same formula, with the backdoor named and mentioned first vs last) × budget | `DPLL-b` vs `BACKDOOR-k` vs NE vs C vs B1 |
| **E4** Trap pairs | Does the model backtrack? | Two literal signs per gadget decide whether the value every greedy rule picks first is a dead end | D vs C (and B1, `BEAM-w`) |
| **E5** Certificate pairs | Can the model *certify* UNSAT, or is UNSAT a default? | SAT/UNSAT pairs one literal apart, with a small core hidden among decoy clusters; UNSAT answers must name a core | D, NE vs F, C, A |
| **E6** Violation profiles | Is a wrong assignment a local-search near-miss, a default fill, a dead end, a slip, or a misreading? | Every infeasible answer compared with each member's simulated distribution; a verification probe; same-item repeats; edge echo for colouring | F vs NE vs PERCEPTION vs D-default vs C |
| **E7** Seeds | Does the answer depend on the starting candidate, as local search says it must? | The same item with no seed, a seed near a solution (*h* = 2, 4, 8), a decoy local minimum, or a random seed | F vs D vs C vs `ECHO` |
| **E8** Truncation | Is the trace's own search state what fixes the answer? Is that state "anytime"? | Prefill the trace to fraction *f* and force an answer; flip one written decision and let the model resume | F (anytime) vs D (state + default) vs post-hoc |

**Totals (full study).**

- **Items:** about 7,200 unique items. Each model sees about 3,500 items in about 16,500 calls.
- **Models:** 8 primary models.
- **Tokens:** about 1.15 B output tokens (about 125 M per model), and about 0.5 B prompt tokens, mostly prefix-cached.
- **Compute:** about 1,000 H100-hours. The dev batch (§5) runs on gpt-oss-20b in about 2 GPU-hours.
- **Build:** about 62 person-days, of which about 25 are shared infrastructure; plus about 24 annotator-days for trace labelling.

---

## 1. The class

### 1.1 Defining ideas and place in the taxonomy

- **D: systematic search, truncated.**
  - **Idea:** walk a tree of *partial* assignments with propagation. On a conflict, undo the latest open decision. Stop after a budget and return a default.
  - **Exact if the budget suffices.**
  - **Formal model:** pBT (Alekhnovich et al. 2011), which "encompasses DPLL in many situations" (report F).
  - **Taxonomy (PAPER_SKELETON Table 4; report F):** D2 budget-truncated (`DPLL-b`, `BEAM-w`) and D3 parameterised (`BACKDOOR-k`).
- **F: local search / repair.**
  - **Idea:** hold a *complete* candidate and change it to reduce violations. Stop on success or after *k* moves.
  - **Formal model:** PLS (Johnson, Papadimitriou & Yannakakis 1988).
  - **It cannot certify UNSAT.**
  - **Taxonomy:** F1 descent (`MIN-CONFLICTS`, `2OPT-k`) and F2 noisy or annealed (`WALK-k`, `SA`).
- **What the two share:** both are class S (sequential) and need chain of thought. Both stop with a default when the budget runs out. Their defaults look different, and that difference is what E6 and E8 test.

### 1.2 SAT notation and shared subroutines

**The formula.**

- A CNF formula *F* has clauses *C*₁…*C*ₘ in prompt order.
- Variables are named x1…xn.
- Generators randomise the names, so **INDEX order** (x1 < x2 < …) and **MENTION order** (order of first appearance) differ, and can be told apart.

**Unit propagation:**

```
UP(F, A):                                   # run to fixpoint; UP-k stops after k passes
  repeat
    W += m                                  # work: one pass reads every clause (the naive count a reader pays)
    if some clause is falsified under A: return (A, CONFLICT, that clause)
    U ← clauses with exactly one unassigned literal and all others false
    if U is empty: return (A, OK)
    c ← the lowest-index clause in U; make its free literal true; record reason(var) = c
```

**Work and nodes.**

- **Work** *W(x)* is the total number of clause visits. It is the primary unit for budgets and is pre-registered.
- **Nodes** *N(x)* = decisions + flipped re-assignments. This is the secondary unit, and is what "*b*" counts in `DPLL-b`.

**Branching orders *H*:**

- **INDEX:** the lowest-numbered unassigned variable.
- **MENTION:** the first unassigned variable in prompt order.
- **OCC:** the most occurrences in clauses not yet satisfied; ties go to MENTION.
- **MOMS:** the most occurrences in the shortest clauses not yet satisfied; ties go to OCC, then MENTION.

**Value rules *V*:**

- **TRUE:** try True first.
- **MAJ:** the sign with more occurrences in clauses not yet satisfied; ties go to True.
- **FIRST-SIGN:** the sign of the variable's first mention.

**Defaults Δ when the budget runs out.** *A\** is the last conflict-free state on the trail.

- **UNSAT:** answer UNSAT ("too complex, so impossible": the lazy UNSAT reported by Hazra et al. 2025, per report A).
- **FILL:** answer SAT with *A\** completed by *V*.
- **PARTIAL:** answer SAT with only *A\**'s variables. This is scored as its own category.
- **DECLARE:** answer UNKNOWN.

**Backtracking:**

- **CHR:** chronological.
- **CBJ:** conflict-directed backjumping, which undoes back to the most recent unflipped decision in the conflict's implication graph. Report A says Hazra et al. see backjumping in R1 traces; confirm this before citing.

**Pre-registered primary grid.** This keeps the family from fitting anything.

- *H* ∈ {MENTION, INDEX, MOMS} × *V* ∈ {TRUE, MAJ}, with CHR: **6 primary variants**.
- Δ is estimated from budget-exhausted runs (§2.5).
- OCC, FIRST-SIGN and CBJ are secondary. They are penalised in model comparison by cross-validated log-likelihood.

### 1.3 Members, in pseudocode

#### SAT (primary)

**`DPLL-b(H, V, Δ, bt)`.** The budget is *b* nodes, or *W*ₘₐₓ clause visits in the work-budget variant.

```
A ← UP(F, ∅); trail ← []; nodes ← 0
loop
  if A satisfies every clause:        return SAT, fill(A, V)
  if nodes ≥ b (or W ≥ W_max):         return Δ(A*)
  if A falsifies a clause c:
     e ← CHR: latest trail entry with flipped = no
         CBJ: latest unflipped decision in the implication graph of c
     if no such e:                      return UNSAT              # certified: every branch closed
     undo the trail back to e; set e.var = ¬e.val; e.flipped ← yes; A ← UP(F, A); nodes += 1
  else
     v ← H(F, A); val ← V(F, A, v); push (v, val, flipped = no); A ← UP(F, A ∪ {v = val}); nodes += 1
```

**`BEAM-w(H, V, b)`.** The budget is *b* child expansions.

```
beams ← [UP(F, ∅)] (dropped if in conflict)
while beams is non-empty:
  if some beam satisfies every clause: return SAT, fill(beam, V)
  if expansions ≥ b:                   return Δ(best beam)
  children ← []
  for B in beams, in rank order:
     v ← H(F, B)
     for val in V-order(v): C ← UP(F, B ∪ {v = val}); expansions += 1; keep C if conflict-free
  score(C) = (#satisfied clauses, #assigned vars), higher first; ties by parent rank, then V's preferred value
  beams ← the top w children
return UNSAT                            # NOT certified: the solution may have been pruned
```

`BEAM-1` is **not** `C-UC`. It propagates *both* values of the chosen variable and keeps the better-scoring child, so it is greedy with one-step value lookahead. On the E4 library items it fails trap arms where `C-UC` also fails, but it differs from `C-UC` elsewhere.

**`BACKDOOR-k(R, V, Δ)`.** The budget is the 2^k branches, so *k* sets the cost.

```
S ← the k variables ranked highest by a static rule R ∈ {OCC, MENTION}; ties go to MENTION
open ← []
for each assignment a of S, in V-preferred lexicographic order:
   (A, status) ← UP(F, a)
   if status = CONFLICT: continue
   if fill(A, V) satisfies F: return SAT, fill(A, V)
   open.append(A)
if open is empty: return UNSAT                         # certified, relative to UP
return Δ(the open A with the most satisfied clauses)
```

`BACKDOOR-k` differs from `DPLL-b` in one way: it never branches outside the fixed set *S*, which is chosen up front from surface statistics. `DPLL-b` re-chooses after every propagation.

**`MIN-CONFLICTS(init, k, pick)`.**

- *init* ∈ {POLARITY (MAJ on each variable), TRUE, RANDOM, SEED}.
- Hoos & Stützle 2004 is the reference for this and the next two.

```
A ← init
repeat k times
  if A satisfies F: return SAT, A
  X ← variables in falsified clauses; v ← pick(X) ∈ {RANDOM, FIRST (mention order)}
  δ ← #falsified after flipping v − #falsified now
  flip v if δ < 0; if δ = 0, flip with probability ½ (stochastic) or keep (deterministic)
return Δ_F(A),  where Δ_F ∈ {SAT-claim with A (near-miss), UNSAT, UNKNOWN}
```

**`WALK-k(init, p, k, pick)`** (WalkSAT/SKC).

```
A ← init
repeat k times
  if A satisfies F: return SAT, A
  c ← a falsified clause, by pick ∈ {RANDOM, FIRST (lowest index)}
  break(u) ← # clauses satisfied now that flipping u would falsify, for u in c
  if some u has break(u) = 0: flip the first such u
  else with probability p flip a uniformly random u ∈ c, otherwise flip argmin break (ties: first in c)
return Δ_F(A)
```

**`SA(init, T₀, γ, k)`.**

```
A ← init; T ← T₀
repeat k times
  if A satisfies F: return SAT, A
  u ← a uniform random variable; δ ← change in #falsified clauses if u is flipped
  flip u if δ ≤ 0, else flip with probability exp(−δ/T); T ← γT
return Δ_F(A)
```

*Pre-registered:* `SA` is told apart from `WALK-k` only by its trajectory. Its uphill-acceptance rate falls over the trace (§2.6). At the answer level the two are merged.

#### Graph colouring (secondary: E4, E6, E7)

The input is a graph G = (V, E) with *c* colours, vertices in mention order.

- **`DPLL-b`: backtracking with forward checking.**
  - Each vertex has a domain D(v). A singleton domain assigns the vertex and removes that colour from its neighbours; this is the analogue of UP.
  - A conflict is an empty domain.
  - *H* ∈ {DSATUR (smallest domain; ties by most uncoloured neighbours, then mention order), MENTION}. Colours are tried lowest first.
  - Δ ∈ {UNCOLOURABLE, FILL with `FIRST-FIT`}.
- **`BEAM-w`:** as for SAT, scored by (#coloured, −#domain wipe-outs).
- **`BACKDOOR-k`:** try all c^k colourings of the *k* highest-degree vertices, then run DSATUR greedy with forward checking and no backtracking. UNCOLOURABLE is certified only if every branch wipes out.
- **`MIN-CONFLICTS`:**
  - init ∈ {`FIRST-FIT` (mention order), RANDOM, SEED};
  - repeat *k* times: pick a conflicted vertex (RANDOM or FIRST); recolour it to the colour with the fewest conflicts. On ties, keep the current colour if it is among the minima, otherwise take the lowest.
- **`WALK-k`:** as `MIN-CONFLICTS`, but with probability *p* the picked vertex gets a random colour.

#### TSP (E7 only)

- **`2OPT-k(init, rule, k)`.**
  - init ∈ {`NN-from-0`, `INPUT-ORDER`, SEED, RANDOM}.
  - rule ∈ {FIRST (scan i < j in lexicographic order, apply the first improving reversal, restart), BEST (apply the best improving reversal)}.
  - Stop at a 2-opt local optimum or after *k* moves.
  - Tours are written in canonical form: start at city 0, heading toward its lower-index neighbour.
- D is not tested on TSP in Phase 1. Exact DP gives ground truth.

#### Entailment, knapsack, scheduling

- **Entailment** reduces to UNSAT of *premises ∧ ¬conclusion*.
  - D is a case-split refutation; its Δ = UNSAT means "follows".
  - F is a countermodel search, and its default when none is found is also "follows", so both err by commission.
  - v1-sized items sit below every panel model's budget line, so entailment appears only as an optional rendering of E5 items (§2.7, E5).
- **Knapsack and scheduling** (branch-and-bound-*b*, swap local search) are left out of Phase 1. Their answer formats are not yet shared with the SAT pipeline, and EHOP already covers greedy on them (report B).

### 1.4 Competitors, as implemented for this vertical

| ID | Family | Definition used here | Why it matters for D/F |
|----|--------|----------------------|------------------------|
| `C-GREEDY` | C1 | Assign in MENTION order using *V*. Never revise. Output the full assignment (C-CONT). | The "no backtracking" null. `POLARITY` is its one-shot (C0) relative |
| `C-UC/STOP`, `C-UC/CONT` | C2 | Unit-clause rule when there are unit clauses, otherwise the next variable by MENTION or MOMS with *V*. At a falsified clause, STOP answers UNSAT; CONT carries on and outputs. | Hazra et al.'s "greedy search without backtracking" for GPT-4o (report A) |
| `POLARITY` | C0 / A2 | x_i = MAJ over all clauses, in one shot | Breaks naive planting; E3–E5 neutralise it |
| `UP-k` | B1 | *k* passes of UP from ∅, then Δ | Idle on unit-free 3-CNF, so it predicts Δ everywhere. Stronger B1 members are the real competitors: |
| `FLP-1` | B1 / D boundary | Failed-literal probing: for each variable, try each value and run UP; if one value conflicts, fix the other; repeat | **Idle from the empty assignment on pure 3-CNF:** one assignment never creates a unit clause (checked on every library item). It acts only after a decision, where it is part of D. The live sound-lookahead competitor is 2-level probing, which is D with b ≈ 4 |
| `2SAT-CORE` | B1 | Solve the 2-clauses exactly | E4 and E5 use pure 3-CNF |
| `NOISY-EXACT` (NE) | nuisance | DPLL(MOMS, MAJ, CHR) run to completion (*b* = ∞), with each clause evaluation wrong with probability ε | Also predicts accuracy falling with size (Sinha et al. 2025) |
| `NOISY-DPLL(b, ε)` | D × nuisance | Both slips and a budget | **Nests `DPLL-b` (ε = 0) and NE (*b* = ∞).** The D-vs-NE question becomes a question about its parameters |
| `PERCEPTION-NOISE` | nuisance | Each literal's sign (or variable index) is misread once with probability ε_p, then the misread formula is solved exactly. The misreading persists within a run | Produces single-clause near-misses like F's |
| `ALWAYS-SAT`, `DENSITY` | A2 | SAT always; or UNSAT iff m/n > α₀ (α₀ fitted) | Matched pairs make their ADR 0 |
| `ECHO` | A1 | Output the seed verbatim | E7's null |
| `A-CORE` | A2 | Name the clauses of the densest variable cluster as the core | E5's surface null |
| `RANDOM` | H | A uniform assignment | Chance |

### 1.5 Nesting and identifiability

These nestings are deliberate. Claims are made about *where in the nested parameter space* the model sits, not only about member names.

- `DPLL-0` with FILL = `UP+GUESS` = the fill rule (`POLARITY` or `ALL-TRUE`), because random 3-CNF has no unit clauses. Report F already notes that `UP+GUESS` is the *b* = 0 member of SEARCH.
- `BEAM-1` = greedy with one-step value lookahead; it differs from `C-UC` only in its value rule. `BEAM-∞` = exhaustive breadth-first search.
- `BACKDOOR-0` = UP to fixpoint, then Δ.
- `WALK-0` and `MIN-CONFLICTS-0` = the init rule: `POLARITY`, `RANDOM`, or `ECHO` of a seed.
- `NOISY-DPLL(b, ε)` contains both `DPLL-b` and NE.
- **The free parameters are capped:** 6 primary DPLL variants; *b* on a log-2 grid; *k*, *p*, ε and λ on pre-registered grids. Planted-model recovery (§2.5) must succeed at the planned sample sizes before any LLM data are analysed.

### 1.6 Reference implementations

| Problem model | Member | Reference implementation |
|---------------|--------|--------------------------|
| SAT | `DPLL-b` (H, V, Δ, CHR/CBJ; node and work budgets) | `src/reasoning_heuristics/heuristics/search/dpll.py` |
| SAT | `BEAM-w` | `heuristics/search/beam.py` |
| SAT | `BACKDOOR-k` | `heuristics/search/backdoor.py` |
| SAT | `MIN-CONFLICTS`, `WALK-k`, `SA` | `heuristics/local/{minconflicts,walksat,anneal}.py` |
| SAT | `NOISY-DPLL(b, ε)`, `PERCEPTION-NOISE` | `heuristics/nuisance/{noisy_dpll,perception}.py` |
| Colouring | `DPLL-b` (FC-BT), `BEAM-w`, `BACKDOOR-k`, `MIN-CONFLICTS`, `WALK-k` | `heuristics/{search,local}/coloring_*.py` |
| TSP | `2OPT-k` | `heuristics/local/two_opt.py` |

Every implementation emits a **trace in the shared event schema** (§2.6). The schema serves three uses:

- synthetic-trace tests of the parsers;
- fake-model recovery;
- the Phase 2 toy models.

### 1.7 Expressibility

**One step is constant depth; the whole procedure is sequential.**

- One step of each member is constant depth: find a falsified or unit clause, pick a variable, assign or flip it. Each step is counting plus selection.
- A fixed transformer can therefore run *b* steps in O(b) chain-of-thought segments.
- Pan et al. 2025 build such a transformer for DPLL with unit propagation, deciding 3-SAT on p variables in at most p·2^(p+1) CoT steps (report A).
- So D and F are **class S** (depth label "seq").

**F's trajectory cannot be shortcut in general.**

- Finding some local optimum is PLS-complete in general.
- Finding *the* local optimum that standard local search reaches from a given start is PSPACE-complete for local max-cut (Schäffer & Yannakakis 1991; report F).

**`BEAM-w` with polynomial width cannot decide hard 3-SAT:** 3-SAT needs exponential width in fully adaptive pBT (Alekhnovich et al. 2011).

**Direct-answer mode (DIR)** allows only the degenerate members of §1.5: Δ, the fill rule, or the init. In DIR, D and F therefore predict *exactly* their degenerate members. E4's DIR arm tests this. If DIR still escapes the trap at depth *d* ≥ 3, the model has in-pass lookahead.

**Token cost:**

- `DPLL-b` writes Θ(W) tokens if it checks or propagates clauses explicitly.
- `WALK-k` writes Θ(k) tokens, or Θ(k·n) if it restates the full candidate after each move.

### 1.8 RASP-L sketch

*Provisional. The counting convention (primitives = select + aggregate + map) and the trace format are to be frozen in `rasp/` before any LLM data.*

**Assumed "state-line" trace format.** Each step writes the trail as tokens `x5=1d x7=0p …`, where d/p marks a decision or a propagated value, plus a flipped flag.

**`DPLL-STEP`** (INDEX order):

| Stage | Operation | Primitives |
|-------|-----------|------------|
| VAL | Each literal token looks up its variable in the last trail line | 1 select, 1 aggregate, 1 map for the sign |
| STATUS | Each clause counts its false and its unassigned literals | 1 select, 2 aggregates |
| CONFLICT | Is any clause fully false? | 1 select, 1 aggregate |
| UNIT | The lowest-index unit clause and its free literal | 2 selects, 2 aggregates, 1 map |
| NEXT | The first unassigned variable | 1 select, 1 aggregate |
| TARGET | The last unflipped decision on the trail | 1 select, 1 aggregate |
| BUDGET | Count of decision markers ≥ b | 1 select, 1 aggregate, 1 map |
| EMIT | Case analysis, then copy the trail line with one change | ≈ 5 maps; 1 select, 1 aggregate, 2 maps |

- **Total:** about 31 primitives, at a depth of about 5 attention layers (VAL → STATUS → {CONFLICT, UNIT, NEXT, TARGET} → EMIT → copy).
- MOMS order adds about 4.

**Comparison programs:**

| Program | How it differs from `DPLL-STEP` | Primitives | Depth |
|---------|--------------------------------|------------|-------|
| `GREEDY-UC-STEP` | Drop TARGET, BUDGET and the backtrack branch | ≈ 22 | ≈ 5 |
| `WALK-STEP` (p = 0, deterministic) | VAL; true-count per clause; first falsified clause; break counts for its 3 variables (sole-true-literal map, select by variable, count); argmin; copy with one flip; stop test | ≈ 20 | 5–6 |
| `MIN-CONFLICTS-STEP` | make − break over conflicted variables | ≈ 24 | — |
| `BEAM-w` | *w* trails per line, plus ranking of *w* candidates | ≈ 30 + 8w | — |
| `BACKDOOR-k` | DPLL restricted to a fixed top-*k* set | ≈ 30 + k | — |

**Caveat:** noise (*p* > 0) and `SA` need a randomness source, which RASP-L lacks. They exist only through sampling at decoding time.

**Pre-registered prediction for O6:**

- D is about 9 primitives longer than C; F is about the same length as C.
- So D should appear only where its accuracy gain pays for the length: in thinking-trained models, and on items below the budget line.

---

## 2. Behavioural evidence (Phase 1)

### 2.1 Predicted error signatures

| Member | Omission or commission | Infeasible or suboptimal | Certifies UNSAT? | Error follows | Budget ↑ | Initialisation |
|--------|------------------------|--------------------------|------------------|---------------|----------|----------------|
| `DPLL-b` | Both, from Δ: false UNSAT (Δ = UNSAT) or false SAT (FILL) | FILL is infeasible, with violations confined to the *tail* (unassigned variables); PARTIAL is incomplete | Yes, while within budget | Work *W*(x) under its order, relative to budget; threshold-like | *n\** ↑ and b̂ ↑ (H3) | No (at most a phase effect) |
| `BEAM-w` | False UNSAT (pruned) | Rarely infeasible | No (pruned) | Number of simultaneous deferred traps vs. log₂w; budget-independent beyond the minimum | Small effect | No |
| `BACKDOOR-k` | Δ outside the backdoor | As for `DPLL-b` | Yes, relative to UP over S | Whether the static top-*k* set contains a backdoor (salience) | *k* ↑ | No |
| `MIN-CONFLICTS`, `WALK-k`, `SA` | False SAT (near-miss) or default UNSAT | **Infeasible near-misses:** V = 1–3, a local minimum, few Hamming flips from a solution, violations in frustrated clauses | **Never** | WalkSAT difficulty (flips, basin depth); on UNSAT items, nothing | SAT success ↑, near-miss *V* ↓, UNSAT unchanged | **Yes** |
| `2OPT-k` | — | Feasible but suboptimal tour, with 0 crossings (a 2-opt optimum) | — | Basin of the init | Converges | **Yes** |
| C | False UNSAT (STOP) or infeasible (CONT) | Dead-end violation at the point of commitment | No (dead ends are not proofs) | Greedy success *g*(x); traps | Flat | Order-sensitive |
| B1 `UP-k`, `FLP-1` | Omission (Δ) | — | Only if UP- or FLP-refutable | Whether the item is UP- or FLP-solvable | Small effect (*k* saturates) | No |
| NE | Commission slips in *completed* runs | One missed clause; not a local minimum at the simulated base rate | Mostly yes | *W*, smoothly; no budget interaction | Flat once the budget suffices | No |
| PERCEPTION | Commission | Violates the misread clause(s); the same clause across samples | Yes (about the misread formula) | Number of literals; position | Flat | No |

### 2.2 Contrast map: which eval separates which pair

✓ = the eval's primary test of that pair · (✓) = secondary.

| Pair | E1 | E2 | E3 | E4 | E5 | E6 | E7 | E8 |
|------|----|----|----|----|----|----|----|----|
| D vs NE | ✓ budget × *W*, termination type | ✓ *b* fit vs ε fit | ✓ *T* × *k\** | | (✓) | ✓ profile | | (✓) |
| D vs F | (✓) UNSAT side | ✓ quadrants | | (✓) | ✓ certificate specificity | ✓ | ✓ | ✓ anytime |
| D vs C | (✓) | | ✓ 2^−k\* flat in *T* | ✓ traps | (✓) | (✓) | (✓) | (✓) |
| D vs B1 | (✓) | | ✓ (UP/FLP-1 idle) | ✓ (UP/FLP-1 idle) | ✓ (UP/FLP-1 idle) | | | |
| `DPLL-b` vs `BACKDOOR-k` | | (✓) | ✓ salience | | (✓) | | | |
| `DPLL-b` vs `BEAM-w` | | | ✓ (item-level) | (✓) item-level; deferred cells not yet produced | | | | (✓) |
| F vs NE vs PERCEPTION | | (✓) | | | | ✓ | (✓) | |
| F vs `ECHO` | | | | | | | ✓ | |
| D/F vs A | ✓ pairs | ✓ balanced cues | ✓ | ✓ | ✓ decoys | | ✓ | |
| Trace faithful vs post-hoc | | | | (✓) | | | | ✓ |

### 2.3 Manipulation signatures

| Manipulation | D (`DPLL-b`) | F (`WALK-k`, `MIN-CONFLICTS`) | Nearest competitors |
|--------------|--------------|------------------------------|---------------------|
| Clause order reversed | MENTION order: *which* items fail changes, the rate does not. MOMS: invariant up to ties | RANDOM pick: invariant. FIRST pick: trajectory changes, rate does not | C1: large changes. NE: invariant. A `PRIMACY`: changes |
| Re-themed (CNF → natural-language "menu" framing, as in Hazra et al.) | Same procedure, but more tokens per clause, so *n\** falls by the ratio of token costs | Same | `TEXTBOOK-TRANSFER` may change |
| Rule inverted ("at least one literal false per clause" = complement every literal) | Invariant up to renaming | Invariant | `TEXTBOOK-TRANSFER` errs |
| Irrelevant constraint (clauses over fresh variables) | *W* grows by the extra clauses per pass; *n\** shifts slightly | Negligible | A `DENSITY` shifts |
| Size ↑ (fixed α) | Sharp drop near *n\**; errors are Δ-type | SAT: near-misses; UNSAT: Δ always | NE: smooth drop, slips. C: earlier drop, dead ends |
| Density ↑ (fixed *n*) | Easy-hard-easy, peaking where *W* peaks on our generator | Failure rises with α on SAT; UNSAT is always Δ | C: knee near its simulated threshold (unit clause works below about 8/3 asymptotically; Achlioptas 2001, report F) |
| Thinking budget 2k → 8k → 32k | *n\** ↑ and b̂ ↑, roughly in proportion to tokens used | SAT success ↑, *V* ↓ | C, A: flat. NE: flat once the budget suffices |

### 2.4 Process measures

**Token use**, pre-registered for runs that complete:

| Member | Predicted tokens |
|--------|------------------|
| `DPLL-b` | log tokens ≈ a + log *W*, so slope ∈ [0.6, 1.2]. An UNSAT member uses more than its SAT twin, by a ratio that tracks *W*_unsat / *W*_sat |
| `BEAM-w` | ≈ *w* × the C cost; flat in *W* at fixed *n* |
| `BACKDOOR-k` | Step-wise in 2^k |
| F | ∝ flips on SAT items. UNSAT items hit the cap or end in GIVEUP *regardless of W_unsat* (key UNSAT-side test, E1-H3) |
| C | ∝ n; flat in *W* |
| NE | ∝ *W*; runs complete |
| A | Small and flat |

**Confidence (secondary).** The final JSON may include `"confidence": 0–100`.

- D and F predict lower confidence on Δ answers than on answers from completed search.
- NE predicts high confidence on its slips.
- A predicts confidence that does not depend on hardness.

### 2.5 Shared methods

**Models (Phase 1; open weights only; no tiny models).** The first model run, which also runs the dev batch, is **gpt-oss-20b at high effort**. The primary panel is:

1. gpt-oss-20b (high);
2. gpt-oss-120b (high);
3. Qwen3-14B (thinking);
4. Qwen3-32B (thinking);
5. Qwen3-30B-A3B (thinking);
6. Qwen3-235B-A22B-Thinking;
7. DeepSeek-R1;
8. DeepSeek-R1-Distill-Qwen-32B.

The size range (14B dense up to 671B MoE) supports a pre-registered scale covariate: π_D rises with scale. The run manifest records sampling parameters (model-card recommended), version strings and dates.

**Conditions.**

- **BE** (primary): highest effort, thinking cap 32,768 tokens, plus a separate 512-token answer reserve after thinking ends.
- **CoT-8k, CoT-2k** (budget factor).
  - Qwen3 uses its thinking-budget mechanism (Qwen3 Technical Report, arXiv 2505.09388, verified this session).
  - R1-family models are stopped s1-style by forcing an end-of-thinking (Muennighoff et al. 2025, arXiv 2501.19393, verified this session).
  - gpt-oss uses low and medium effort plus hard caps, and the tokens actually used are recorded.
- **DIR:** Qwen3 non-thinking mode, answer only, as a reference arm in E1 and E4. gpt-oss has no non-thinking mode.

**Prompts.**

- One fixed template per domain, published, the same across conditions apart from the manipulated lines.
- No algorithm is suggested, and tools are disabled.
- Every SAT prompt says "the formula may or may not be satisfiable".
- Clauses are written `C17: (x3 OR NOT x12 OR x40)`, with clause IDs so that violations and cores can be cited.

**Answer formats.** All are small and machine-checkable, the final line is JSON, and there is no LLM in the scoring path.

| Domain | Format |
|--------|--------|
| SAT | `{"answer":"SAT","assignment":"x1=1 x2=0 …"}`, or `{"answer":"UNSAT"}` (E5 adds `"core":[clause ids ≤ 24]`), or `{"answer":"UNKNOWN"}` |
| Colouring | `{"answer":"COLOURING","colours":"v1=2 v2=1 …"}` or `UNCOLOURABLE`. E6 adds `"edges":[…]` (an echo) after the answer |
| TSP | `{"tour":[0, …]}` |

Writing assignments with explicit names, not bit-strings, removes off-by-one confusion between output positions and variables.

**Scoring categories** (DESIGN §5.5):

- correct;
- infeasible SAT claim;
- false UNSAT;
- PARTIAL (variables missing);
- UNKNOWN (declared);
- parse failure;
- refusal;
- LOOP (≥ 3 near-identical repeated spans until the cap);
- **capped** (hit the 32k or forced cap). Capped is a stratum flag that sits on top of the other categories.

**Truncation and censoring.**

- A capped run is closed by forcing end-of-thinking, then the answer is requested.
- In token-vs-size models, capped runs are **censored** (DESIGN §3 O2; Verma 2026).
- In answer analyses, forced answers form their own stratum. For D they are informative, because `DPLL-b` predicts that the forced answer is Δ(current state).
- "Budget-exhausted" is pre-registered as any of:
  - capped;
  - a GIVEUP event in the trace (§2.6);
  - a self-terminated Δ-type answer whose trace search is incomplete (FA6, §2.6).

**Likelihoods.** These are how D and F enter the shared mixture (DESIGN O3).

- **Deterministic members:** P(y | h, x) ∝ exp(−λ · d(y, h(x))). Here *d* is Hamming distance for assignments, maximal for an answer of the wrong type, and Kendall distance for tours.
- **Stochastic members** (`WALK`, `SA`, `MIN-CONFLICTS`/RANDOM, and D with randomised tie-breaking to capture heavy-tailed runtimes; Gomes et al. 2000): 200 Monte Carlo runs per item, with a Hamming kernel over the runs.
- For infeasible answers, a **violation-profile term** (E6 statistics) multiplies the likelihood.
- Parameters (*b*, *k*, *p*, ε, λ) are fitted by 5-fold cross-validation across items.
- Δ is estimated from budget-exhausted runs only.

**Readout: graded weights, not verdicts.** Heuristics can be partly used, so every result is a quantity with an interval.

- **Mixture weight π_h.** Posterior mean and 95% credible interval from the mixture P(y | x) = Σ_h π_h · P(y | h, x) + π_none · q(y | x).
  - The prior is a Dirichlet over members.
  - The hierarchical model has model and item random effects.
  - A family's weight is the sum of its members' weights.
- **Lift.** The share of errors explained above chance: error agreement EA(h) minus its value under a permutation baseline matched on item structure (DESIGN O3), with a bootstrap CI.
- **Log-likelihood gain.** Cross-validated ΔLL per response, for h over the null and over the nearest competitor, plus a Bayes factor where the marginal likelihood is tractable. The null is A + RANDOM + none.
- **Trace share.** The share of traces carrying h's signature (§2.6 labels), weighted by the model's faithfulness R_m, with its interval.
- **Feature-dependent weights (family I, strategy selection).**
  - π_h(φ(x)) = softmax(w_h · φ(x)), with pre-registered features φ = (log W/T, log F_ref, n, truth, k\*, presentation, seed condition, budget).
  - H3 becomes a statement about w: D's weight rises with budget and falls with W/T.
  - Model-level random slopes let weights differ between models, including across scale.
- **How results are stated:**
  - moving weight: "this set moves weight from h to h′ by Δπ (interval)";
  - a bound: "this set bounds π_h′ ≤ x (upper 95%)";
  - power: "this set has power p to detect π_h ≥ x".

  The weight statements in §2.7 and the per-item hypothesis blocks in the question library use these forms. The per-item outcome likelihoods, with a 5% slip floor on every theory, are in the JSONL (`outcome_likelihoods`). The question library turns them into modal-pattern log-likelihood-ratio tables per set.

**Recovery tests with graded mixtures** (DESIGN §5.12; these must pass before any LLM data are analysed).

- **Planted fake models.** All use the same token mapping *T* = τ·*W* and the same scorer.
  - single members: every D and F member, C, B1, NE, PERCEPTION, A;
  - two-way mixtures, 80/20 and 50/50: e.g. `DPLL-b`/NE and `WALK-k`/`C-UC`;
  - **three-way mixtures, 60/30/10:** e.g. `DPLL-b` / `C-UC` / NE, and `WALK-k` / `DPLL-b`-FILL / PERCEPTION;
  - **feature-dependent mixtures:** π_DPLL = logistic(β · (log b − log W)) with β ∈ {1, 3}, the rest `C-UC` or NE; and π_F rising with budget.
- **Report, for every planted weight:**
  - bias (mean recovered − planted);
  - 95% interval width;
  - coverage of the 95% interval;
  - for feature-dependent plants, the recovered slope w with its interval.
- **Pass criteria at the planned sample size,** per eval and pooled:
  - |bias| ≤ 0.05 for every weight ≥ 0.1;
  - coverage ≥ 0.90;
  - interval width ≤ 0.20 for weights ≥ 0.3;
  - the NE vs `DPLL-b` and F vs PERCEPTION weights recovered within these bounds in the 60/30/10 plants.
- **If a weight cannot be recovered to these bounds,** its members are merged *before* the LLM analysis, and the merge is recorded.

**Statistics.**

- Mixed-effects logistic models with (1 | item) and (1 | model).
- Paired tests (McNemar, TOST) for paired designs.
- Holm correction across each eval's *primary* hypotheses. The CT hypotheses below are secondary (process evidence).
- Cross-model claims come from one hierarchical model.

**Repeats.** BE has 2 samples per item everywhere, plus a 3rd sample on a fixed 20% subset (DESIGN O4).

### 2.6 Trace evidence: coding, faithfulness, and how it combines with answers

**The trace is unreliable evidence.**

- Hints are verbalised in only about 25–39% of cases (Chen et al. 2025, report C).
- Answers can be decodable before the CoT starts (Cox et al. 2026).
- Models can claim checks they did not do (NPPC, report A).
- Explicit-search supervision can suppress implicit reasoning (Qin et al. 2025, arXiv 2504.07052, verified this session).

So every inference from the trace below is pre-registered as *process consistency*, weighted by a measured per-model reliability.

**Codebook.** A closed set of event types:

| Event | Definition | Typical cues (the parser uses these and more) |
|-------|------------|-----------------------------------------------|
| `DEC` | A hypothetical assignment | try, suppose, assume, case 1, let's set … and see |
| `PROP` | A forced assignment with a reason | must, forced, so, therefore, then (+ a clause ID or literal) |
| `ASG` | An unmarked assignment | Resolved later: if revised, retro-coded `DEC`; if never revised, a C-style commit |
| `CHK` | A clause evaluated under the current state | "C12 satisfied by x4" |
| `CONF` | A clause stated violated, or a contradiction | contradiction, violated, impossible, fails |
| `BT` | A previous `DEC`/`ASG` value reversed or abandoned, after a `CONF` | so x5 can't be 1, go back, other case |
| `BJ` | A `BT` whose target is not the most recent open decision | Derived from the state tracker |
| `CASES` | ≥ 2 partial assignments carried forward together (`BEAM`) | Case A … Case B …, both kept |
| `FULL` | A complete candidate: ≥ 0.8n variables valued in one span | — |
| `VIOL` | A violated-clause list or count for a candidate | — |
| `FLIP` | One variable changed in a `FULL` candidate to repair violations | flip, change x4 to |
| `RESTART` | Start over | — |
| `GIVEUP` | Search declared too long or hard, followed by a guess or default | too many possibilities, likely unsatisfiable, I'll guess |
| `VERIFY` | A claim that the final candidate satisfies everything | — |
| `SEEDREF` | A reference to the provided seed (E7) | — |
| `LOOP` | Detected automatically | — |

Colouring uses the same codes; `RECOLOR` is its `FLIP`. TSP uses `TOUR`, `MOVE` (a 2-opt reversal or swap), `COST` and `NN-STEP`.

**Pipeline.**

1. **Segmenting.** Each model family has its own segmenter:
   - `<think>` blocks for Qwen3 and R1;
   - the harmony *analysis* channel for gpt-oss;
   - split into sentences, and lines for lists.
2. **Rule-based extraction.** Grammar and regex pick out variable–value mentions, clause IDs and cue words.
3. **State tracker.** It rebuilds the trace's own partial assignment, decision stack and candidate after every event. From this it derives:
   - decision order;
   - depth;
   - which decision each backtrack targets;
   - the number of distinct variables that receive decisions;
   - tokens between `DEC v` and `BT v`.
4. **LLM-assisted coding** handles windows where the regex finds variable mentions but no unambiguous cue (expected to be 20–40% of segments).
   - **Coder:** Llama-3.3-70B-Instruct. It is outside the panel, run at temperature 0, with the version pinned.
   - **Input:** about 1.5k-token windows, the tracker's state summary at the window's start, and the codebook.
   - **Output:** JSON events, validated against the grammar (variable names must exist).
   - **Kept from the coder:** the formula's ground truth, the final answer, and any text after the window.
5. **Synthetic-trace control.** Traces from the reference implementations are rendered into natural language in 6 styles, with paraphrase noise, then parsed. Event F1 must be ≥ 0.95, which catches parser bugs cheaply.

**Validation and inter-rater agreement.**

- **Segment-level gold.** 2,400 segments (300 per model), stratified by event type, eval and correctness, are coded by 2 trained annotators.
  - Report Cohen's κ per event type, with **κ ≥ 0.70** required.
  - Disagreements are adjudicated into gold.
- **Trace-level gold.** 48 complete traces from E4 (the shortest BE traces, median about 7k tokens; 6 per model) are single-coded, and 16 more are double-coded.
  - Report ICC for counts of `DEC`, `BT` and `FLIP`, with **ICC ≥ 0.80** required.
- **The automated pipeline** (parser + coder) is scored against gold:
  - event F1 ≥ 0.80 for `DEC`, `BT`, `CONF`, `FLIP`, `FULL` and `GIVEUP`;
  - ICC ≥ 0.80 for the derived counts.
- **Failures and reporting.**
  - Event types that fail are dropped from the CT hypotheses *before* the main analysis, and the drop is recorded.
  - All numbers are reported per model, because trace styles differ a lot.

**Trace-family labels** (pre-registered rules, applied to each trace):

| Label | Rule |
|-------|------|
| D | ≥ 2 `DEC`, ≥ 1 `BT`, and ≤ 1 `FULL` before the answer |
| BEAM | ≥ 1 `CASES` with ≥ 2 live cases across ≥ 2 decisions, and `BT` = 0 |
| F | ≥ 1 `FULL`, ≥ 2 `FLIP`, and ≤ 1 `DEC` |
| C | ≥ n/2 `DEC` + `ASG`, with `BT` = 0 and `FLIP` = 0 |
| B1 | Only `PROP` before the answer |
| MIXED | Two labelled segments, recorded in order (e.g. D→F) |
| NONE | Otherwise |

**Trace–answer consistency (faithfulness) tests**, computed for every coded trace:

| ID | Test | What D, F and C predict, if the trace is faithful |
|----|------|---------------------------------------------------|
| FA1 | The final answer equals the trace's last complete state, or its state at the in-trace answer | ≥ 0.9 |
| FA2 | **Phantom backtrack:** the trace reverses v (`BT`), but the answer keeps the old value of v with no later re-reversal | ≤ 0.05 |
| FA3 | **False verification:** `VERIFY` is claimed, but the answer violates a clause | ≤ 0.05; NE and PERCEPTION are higher |
| FA4 | Conflict precision: each `CONF` names a clause that really is falsified under the trace's state | ≥ 0.9 |
| FA5 | Propagation soundness: each `PROP` really is implied (a unit) under the trace's state | ≥ 0.9; NE is lower |
| FA6 | **Refutation completeness:** for UNSAT claims, every branch of the trace's case tree ends in a valid `CONF` | D below budget: complete. Δ / F / C: incomplete |
| FA7 | Answer-before-search: the final answer is stated as a hypothesis in the first 10% of the trace, before any search events | Post-hoc: high |
| FA8 | Backtracks that never reach the answer: the fraction of `BT` targets whose final value is the pre-`BT` value | Pooled from FA2 per model |

**Per-model reliability R_m.** The mean of:

- FA1;
- 1 − FA2;
- 1 − FA3;
- FA4;
- FA5;
- E8's corruption-following above control, rescaled to [0, 1].

R_m bands, pre-registered:

- R_m ≥ 0.7: **the trace is usable as process evidence**;
- 0.4 ≤ R_m < 0.7: **weak**;
- R_m < 0.4: **decorative**, and no CT test is interpreted for that model.

**How trace and answer evidence combine** (pre-registered):

1. **Weights come from answers.** π_h, lift and ΔLL in the evidence table are answer-channel quantities.
2. **The trace channel is a second, reported quantity:**
   - the R_m-weighted share of traces carrying h's signature;
   - per item, the agreement (κ) between the answer posterior's modal family and the trace label.
3. **Joint model (secondary).** A two-channel latent-class model:
   - a latent procedure *z* per response;
   - the answer likelihood comes from §2.5;
   - the trace label has a confusion matrix whose diagonal has a Beta prior centred on R_m.

   The answer-only and joint posteriors on every π are both reported. The joint posterior may narrow an interval, but **it may not move a weight's posterior mean by more than the answer-only 95% half-width.** That is pre-registered, so an unreliable trace cannot overturn the answers.
4. **Reading a disagreement.** Both readings below are quantities, reported side by side, never discarded.

| Answer channel | Trace channel | Reading |
|----------------|---------------|---------|
| π_h high | h-share high, R_m ≥ 0.7 | h's weight, process-consistent |
| π_h high | h-share low | Unverbalised computation or a post-hoc trace; check E8 (FA7, *f* = 0 agreement) |
| π_h low | h-share high | A "decorative h-like trace", e.g. the phantom-backtrack rate |
| π_h low | h-share low | Both channels bound h |

5. **Systematic disagreement is a finding in its own right.** If κ between answer-classified and trace-labelled families is below 0.2 for a model, that is reported as a faithfulness result alongside Chen et al. 2025.

### 2.7 Evals

Each eval gives, in order:

1. the question as falsifiable hypotheses;
2. the counterfactual design, with answer (**A:**) and trace (**T:**) predictions per cell for each relevant family;
3. confound control;
4. the generator recipe;
5. the answer format and metric;
6. weight statements: which π each outcome moves, power, and the bound when the effect is null;
7. pre-registered chain-of-thought hypotheses (CT);
8. sample size and power;
9. threats.

---

#### E1. Budget-line sweep, with a density arm

**Hypotheses.**

- **E1-H1 (D, H3): data collapse.**
  - Accuracy is one function of z = log *W*(x) − β · log *T* for all budgets, with β ≈ 1.
  - NE predicts β = 0: accuracy depends on *W* only.
  - C predicts dependence on greedy success *g*(x), with no *T* effect.
  - A predicts accuracy at the level of the answered class at every *n*: per-item 0.5 and ADR 0 on the pairs.
- **E1-H2 (the D/F default).** Among budget-exhausted runs, the answer does not depend on truth within a matched pair. In those runs, the two members of a pair get the same answer.
- **E1-H3 (UNSAT side, D vs F).**
  - Under D, the rate of *trace-certified* UNSAT (FA6) on UNSAT members falls with *W*_unsat.
  - Under F it is ≈ 0 at every *W*_unsat, and UNSAT answers arrive only by default. F's cap/GIVEUP rate on UNSAT members does not depend on *W*_unsat.
- **E1-H4 (density arm).** At n ≈ *n\**_BE:
  - D predicts an easy-hard-easy error curve peaking where *W* peaks on our generator.
  - F predicts failure rising with α on SAT items and Δ on all UNSAT items.
  - C predicts a knee on SAT items at its own simulated threshold.
  - The model's knee is compared with each member's simulated curve (report F, threshold-knee signature).

**Design.**

- **Matched SAT/UNSAT pairs** one literal sign apart (Zhang, Chen & Chen 2026), at α = 4.26.
- **Global size grid:** n ∈ {8, 10, 12, 15, 18, 22, 26, 30, 36, 42, 50, 60, 72}, with 30 pairs per level.
- **Stage 0 (E0):** a pilot staircase, n ∈ {10, 20, 30, 45, 60} × 10 pairs, BE, 1 sample, gives *n\**_BE.
- **Per model:** 9 consecutive grid levels centred on *n\**_BE, run at BE (2 samples), CoT-8k (1), CoT-2k (1) and DIR (1, Qwen3 only).
- **Density arm:** at the grid level nearest *n\**_BE, α ∈ {3.0, 3.5, 3.9, 4.26, 4.6, 5.2, 6.0} × 40 unpaired items, BE, 2 samples.
- **Predicted *n\**.** τ_W is the median tokens per unit of *W*, measured in completed D-coded traces below *n\**. Then *n\**_pred(T) is the *n* at which the median *W*(n) · τ_W = T (DESIGN O2 design rule).

| Family | n ≪ n\* | n ≈ n\* | n ≫ n\*, SAT member | n ≫ n\*, UNSAT member | Budget 2k → 32k |
|--------|---------|---------|---------------------|-----------------------|-----------------|
| `DPLL-b` | **A:** ✓ ✓<br>**T:** `DEC`/`PROP`/`BT`; refutation complete | **A:** items with *W* > budget fail with Δ<br>**T:** cap or `GIVEUP` on failures | **A:** Δ (UNSAT / FILL / PARTIAL)<br>**T:** many `DEC`/`BT`, ending at cap or `GIVEUP` | **A:** Δ (if Δ = UNSAT, right for the wrong reason)<br>**T:** incomplete tree | *n\** ↑; the 2k → 8k shift equals the shift in *n\**_pred |
| F | **A:** SAT ✓; UNSAT Δ<br>**T:** `FULL` + `FLIP` | **A:** SAT near-misses<br>**T:** long `FLIP` runs | **A:** near-miss<br>**T:** `FLIP` until cap | **A:** Δ always<br>**T:** cap/`GIVEUP`, independent of *W*_unsat | SAT ↑; UNSAT unchanged |
| NE | **A:** ✓ minus ε·*W*<br>**T:** complete search | **A:** smooth decline<br>**T:** completes; slips at a `CHK`/`PROP` | **A:** slip answers (infeasible, or a false UNSAT from a spurious conflict)<br>**T:** completes, with false `VERIFY` | **A:** mostly ✓ | Flat beyond 2k |
| C | **A:** fails where *g*(x) is low<br>**T:** one pass, `BT` = 0 | **A:** dead ends | **A:** dead-end infeasible or false UNSAT | **A:** UNSAT (STOP) | Flat |
| A | **A:** one member of each pair right | Same | Same | Same | Flat |

**Confound control.**

- **Length:** *n* and *m* rise together. That is unavoidable in a size sweep, but E1-H1 is identified from *within-level* variation in *W*, which spans about one decade, with log *m* as a covariate.
- **Surface:** the two members of a pair are identical except for one sign.
- **Solvability:** every level is 50% SAT, which removes inflation from SAT bias (Zhang et al. 2026).
- **Output length:** answers are under 300 tokens, with a separate reserve.
- **Truncation:** censored, and stratified (§2.5).

**Generator.**

1. Sample *F* ~ random 3-SAT(n, m = round(4.26n)), with distinct variables within a clause and no repeated clauses.
2. Solve it with CaDiCaL via PySAT.
3. If it is UNSAT, try literal flips in random order until one makes it SAT; if it is SAT, look for a flip that makes it UNSAT. Keep the pair.
4. Rename variables at random, and shuffle clause order, the same way in both members.
5. **Store, for each item:**
   - *W* and *N* under the 6 primary DPLL variants, plus CBJ;
   - WalkSAT median flips (100 runs; p ∈ {0.2, 0.5});
   - *g*(x) for the C variants;
   - the outcomes of UP, FLP-1 and the B1 members;
   - the number of solutions (enumeration up to 10⁴, otherwise approximate);
   - backbone size;
   - the size of the minimal unsatisfiable subset (MUS) of the UNSAT member (MUSX, time-capped);
   - the content hash.

**Metrics.**

- Item accuracy.
- ADR, the rate at which both pair members are right.
- *n\**_obs: the *n* at which item accuracy = 0.75 on a logistic in log *n*. This is the midpoint between perfect and the pair chance level of 0.5.
- Termination type × correctness.
- Tokens.
- β, estimated from the hierarchical model correct ~ s(log *W* − β log *T*) + log *m* + truth + (1 | item).
  - **Primary:** the 2k ↔ 8k leg, where both caps bind.
  - **Secondary:** 8k ↔ 32k, which tests whether BE is limited by the cap or by the model itself.
- `NOISY-DPLL(b, ε)`, fitted per budget.

**Weight statements (pre-registered).** These are per model × budget, from the mixture posterior (§2.5), for items above *n\**_obs.

- **π_DPLL vs π_NE.** β and the termination-type split together set how much of the above-*n\** error mass goes to truncation vs slips.
  - For a D-dominant model the pre-registered expectation is π_DPLL ≥ 0.5, with β̂ ∈ [0.5, 1.5].
  - ΔLL(DPLL-b : NE) per response and the Bayes factor are reported.
- **Bounds:**
  - if β̂'s 95% interval includes 0 and excludes 0.5, the set bounds π_DPLL ≤ 0.15 (upper 95%) on above-*n\** errors;
  - if ≥ 60% of errors are budget-exhausted, it bounds π_NE ≤ 0.3.
- **The default component.** Among exhausted runs, pair-answer agreement ≥ 0.8 means the default does not depend on truth. Each discordant exhausted pair has LR ≈ 0.1 against a pure default.
- **The UNSAT side.** Each FA6-certified UNSAT response has LR ≈ 0.05 against F. With ≥ 30 certified responses, π_F(UNSAT members) ≤ 0.1 (upper 95%).
- **A cues.** The ADR bounds π_A ≲ 1 − ADR.
- **Power.** 540 items × 2 samples give power 0.8 to detect π_DPLL ≥ 0.15 against an NE-only model (planted-recovery estimate).
- **Feature dependence (family I).** π_h(log W/T, truth, n) is fitted as a secondary model. D's weight should rise with budget and fall with W/T.

**Pre-registered CoT hypotheses.**

- **CT1.1:** in D-labelled traces of completed searches, log #`DEC` against log *N*_ref has a slope γ ∈ [0.5, 1.2], with Spearman ρ ≥ 0.4. F predicts `DEC` ≈ 0, with #`FLIP` tracking WalkSAT flips. C predicts `DEC` ≈ n with `BT` = 0.
- **CT1.2:** #`BT` per trace rises with *N*_ref (ρ ≥ 0.3) for both SAT and UNSAT members.
- **CT1.3 (give up and default):**
  - ≥ 50% of self-terminated failures above *n\**_obs contain `GIVEUP`;
  - the `GIVEUP` rate rises with *W*/*T*;
  - ≥ 80% of `GIVEUP` traces end in a Δ-type answer.
- **CT1.4 (UNSAT premium):** within pairs, tokens(UNSAT) / tokens(SAT) correlates with *W*_unsat / *W*_sat (ρ ≥ 0.3) under D. Under F, the UNSAT member hits the cap or gives up regardless.
- **CT1.5:** the FA6-complete refutation rate falls with *W*_unsat, and is ≈ 0 above *n\**_obs.

**Power.**

- Per model: 540 items × 2 BE samples, plus 540 × 2 capped runs.
- *n\**_obs is estimated to about ±8% (logistic on 9 levels with about 120 responses per level).
- β uses within-item contrasts across budgets: the SE is about 0.12, assuming *W* spans about 2 decades across the sweep.
- The share of budget-exhausted errors is estimated to ±6% on about 300 errors.
- **Density arm:** 280 items × 2 samples. Detecting a peak shift of 0.4 in α between the D and F curves has power ≈ 0.8 (by simulation with planted models, to be confirmed in §2.5 recovery).

**Threats.**

- **CoT unfaithfulness:** CT1.x count only if R_m ≥ 0.4.
- **Caps:** forced truncation is not the model's own default, so self-terminated and forced Δ are analysed separately.
- **Non-monotone budget effects** (Gema et al. 2025; Ghosal et al. 2025) are allowed on the 8k → 32k leg.
  - Inverse scaling is diagnosed by **FOUND-THEN-LOST** traces: the trace contains a valid solution that the answer does not keep. These are counted separately, not as evidence against H3.
- **Solver-hard is not always model-hard** (Verma 2026). A null on *W* is a real result against D, and is not explained away.
- **Heavy-tailed runtimes** call for 2 samples and randomised tie-breaking in the references.
- **Memorisation:** negligible for random instances.

---

#### E2. Fitting *b*, and D/F dissociation quadrants

**Hypotheses.**

- **E2-H1:** `DPLL-b`, with one *b* per (model, budget) and one primary variant, predicts *which* held-out items fail better than NE, `WALK-k`, C, B1 and A.
- **E2-H2:** at fixed *n* and α, with all items SAT, failure follows DPLL work *W* (D) rather than WalkSAT difficulty *F*_ref (F).
- **E2-H3 (H3):** b̂(2k) < b̂(8k) ≤ b̂(BE), with b̂ roughly proportional to the tokens actually used.

**Design.**

- **Fitting set:** E1 items plus the quadrant set.
- **The quadrant set** is at n_Q, the grid level {15, 22, 30, 42} nearest *n\**_BE, with α = 4.26 and every item SAT.
- **Proposal ensembles:**
  - random 3-SAT, conditioned on SAT;
  - **q-hidden planted formulas** (Jia, Moore & Strain 2005, arXiv cs/0503044, verified this session), with *q* tuned on our generator so that each variable's MAJ agreement with the hidden assignment is 0.50 ± 0.02. This removes the polarity cue that makes naive planting easy.
- **Selection:**
  - compute *W* (median over the 6 primary variants) and *F*_ref (WalkSAT median flips);
  - take terciles within the n_Q pool;
  - keep 100 items per quadrant {W low, W high} × {F low, F high}.
- **Matching across quadrants:**
  - log #solutions;
  - backbone fraction;
  - *g*(x);
  - UP and FLP outcomes;
  - polarity agreement;
  - clause-length statistics;
  - backdoor size (recorded as a covariate).
- **If the natural off-diagonal cells are too thin,** fill them with constructions:
  - **(W high, F low):** 2-hidden formulas, which Jia et al. describe as hard for DPLL but solvable by WalkSAT in polynomial time;
  - **(W low, F high):** a planted size-2 weak backdoor inside deceptive q-hidden fill. Planting works for k = 2, but not for k ≥ 3 (§2.9).

  At least 50% of each quadrant must be natural items, and quadrant effects are also tested *within* each ensemble.

| Family | W low, F low | W low, F high | W high, F low | W high, F high |
|--------|--------------|---------------|---------------|----------------|
| `DPLL-b` | **A:** ✓<br>**T:** few `DEC`, `BT` ≈ 0–2 | **A:** ✓<br>**T:** as before | **A:** ✗, Δ<br>**T:** many `DEC`/`BT`; cap/`GIVEUP` | **A:** ✗, Δ<br>**T:** as before |
| `WALK-k` | **A:** ✓<br>**T:** few `FLIP` | **A:** ✗, near-miss<br>**T:** long `FLIP` runs; repeated `VIOL` on the same clauses | **A:** ✓<br>**T:** few `FLIP` | **A:** ✗, near-miss |
| NE | **A:** ✓ | **A:** ✓ | **A:** lower, smoothly with *W*; errors are slips | **A:** lower |
| C | **A:** set by *g*(x) (balanced across cells) | Same | Same | Same |
| B1 | **A:** Δ everywhere | Same | Same | Same |
| A | **A:** flat (cues balanced) | Same | Same | Same |

**Fitting.**

- Per model × budget:
  - *b* on the grid {2⁰ … 2¹²} nodes, and *W*ₘₐₓ on a matching grid;
  - the variant from the primary grid;
  - Δ from exhausted runs;
  - 5-fold cross-validation stratified by *n*.
- **Predicted failure probabilities p̂ᵢ:**
  - `DPLL-b`: 50 tie-randomised runs;
  - NE: 1 − (1 − ε)^Wᵢ;
  - `WALK-k`: the simulated failure rate at the fitted *k*;
  - C: 1 − *g*ᵢ;
  - A: logistic on (n, m, α, polarity).
- **Comparisons:** held-out log-likelihood, and AUC with the DeLong test.
- **H3:** b̂ per budget with a bootstrap over items.

**Weight statements (pre-registered).**

- **Joint estimate.** π_DPLL and π_F are estimated together, with feature-dependent weights π_h(log W, log F_ref). The W effect identifies D's component and the F_ref effect identifies F's.
- **Power:** 0.93 to detect a 15 pp effect, i.e. a component weight of about 0.2 at the tercile contrast.
- **Bounds:** a null W effect bounds π_DPLL ≤ 0.15 (upper 95%); a null F_ref effect bounds π_F ≤ 0.15.
- **Fit quality.** Held-out ΔLL per response for `DPLL-b` over the best competitor, with a bootstrap interval, per model. AUC is secondary.
- **H3.** The posterior over b̂(T) per budget. The pre-registered quantities are b̂(BE) / b̂(2k), expected ≥ 4, and b̂ / T̄_used.
- **Moving weight.** If b̂ is flat across budgets, weight moves from `DPLL-b` to NE by the Bayes factor of `NOISY-DPLL` with *b* free vs *b* = ∞.
- **Yield caveat.** Natural off-diagonal quadrants are rare: about 2–3% each at n = 14 (§2.9). The quadrant contrast leans on large pools or flagged constructions.

**Pre-registered CoT hypotheses.**

- **CT2.1 (search order):**
  - the trace's first 3 `DEC` variables match one primary order *H* at ≥ 2× chance, where chance is 1 / #unassigned at each step;
  - the trace-best *H* equals the *H* chosen by answer cross-validation in ≥ 60% of models.
- **CT2.2:** first-decision values match *V* (TRUE or MAJ) in ≥ 70% of decisions.
- **CT2.3:**
  - D-labelled traces show more `BT` and more caps in high-*W* cells;
  - F-labelled traces show longer `FLIP` runs and more `FULL` restatements in high-*F* cells.
- **CT2.4:** in capped D-labelled runs, #`DEC` + #`BT` at the cap ≈ b̂, within a factor of 2.

**Power.**

- **Quadrant main effects:** 200 vs 200 items × 2 samples, with ICC about 0.5, gives an effective n of about 267 per arm. A 15 pp difference at p ≈ 0.5 needs about 170 per arm, so power ≈ 0.93.
- **AUC:** with about 400 quadrant items plus about 540 E1 items per model, and predictors correlated at r ≈ 0.5, ΔAUC = 0.07 is detectable at 80% per model. ΔAUC = 0.04 is detectable pooled across the hierarchical model.

**Threats.**

- **Quadrants are defined by *our* reference costs,** and the model's cost may follow something else. Matching handles this, and the solution count is a covariate.
- **Construction ensembles are confounded with cells.** Handled by the ≥ 50% natural-item rule plus the within-ensemble tests.
- ***F*_ref depends on WalkSAT's parameters.** Two settings are used.
- **"Easy for WalkSAT in polynomial time" (2-hiding) is asymptotic.** Membership is decided on *measured* costs at our *n*, never on ensemble labels.

---

#### E3. Backdoor size × presentation salience × budget

**Hypotheses.**

- **E3-H1:** at fixed *n* and α, accuracy falls with *k\**, the size of the smallest weak UP-backdoor (Williams, Gomes & Selman 2003).
- **E3-H2 (D, H3):** the threshold *k\**₅₀(T) moves by about +1 per doubling of the budget (slope s ≈ 1). D and `BACKDOOR-k` predict this; NE and C predict s = 0.
- **E3-H3 (presentation).** Take the *same* formula in two presentations: "high" names the backdoor variables x1…xk and mentions them first; "low" names and mentions them last. This changes the predictions of order-following members only.
  - `BACKDOOR[INDEX]` (branch on the k lowest-numbered variables) succeeds in high and defaults in low.
  - `DPLL-b[MENTION/INDEX]` changes by a node count that is **computed per item, and can go either way.** In the library, DPLL-MENTION needs 15 vs 12, 92 vs 10, and 9 vs 15 nodes (high vs low) on the three formulas.
  - `DPLL-b[MOMS]`, `BACKDOOR[OCC]`, F, NE and EXACT are invariant, apart from MOMS tie-breaks.

**Two facts found while building the examples:**

1. In pure 3-CNF a single assignment never creates a unit clause. So every weak UP-backdoor has size ≥ 2, and UP and `FLP-1` are idle from the empty assignment.
2. Planting a backdoor of size ≥ 3 at α ≈ 4.26 failed in every attempt at n = 14: the random fill always created a natural size-2 backdoor.

So *k\** is **selected from natural formulas, not planted.**

**Design.**

- **Cells:** *k\** ∈ {2, 3, 4} × presentation {high, low} × budget {2k, 8k, BE}.
- **Items:** 60 formulas per *k\**, each shown in both presentations, gives 360 items per model. 2 samples.
- ***n* ∈ {24, 36}.** Natural *k\** = 4 needs n = 36; at n = 24 only *k\** ∈ {2, 3} are available.
- Each model runs the level where its pilot CoT-8k accuracy on *k\** = 2 items is 0.4–0.8.

**Generator.** Selection plus relabelling; the full spec is in §2.9.

1. Draw random 3-SAT(n, round(4.26n)), keeping SAT formulas with ≤ 300 solutions.
2. Compute the exact minimum weak UP-backdoor size *k\**, and one minimum set S, by subset enumeration with queue-based UP.
3. Bin the formulas by *k\**.
4. Make the two presentations by relabelling:
   - high: S → x1…xk, with S-containing clauses first (most S literals first) and S literals first in each clause;
   - low: S → x_{n−k+1}…x_n, with S-containing clauses last.
5. Record per presentation:
   - *N* and *W* for the 6 variants;
   - BACKDOOR outcomes under INDEX, MENTION and OCC;
   - whether the top-occurrence set is a backdoor (an observational covariate for `BACKDOOR[OCC]`).

| Family | k\* ↑ | T × k\* | Presentation (same formula) | Trace |
|--------|-------|---------|-----------------------------|-------|
| `DPLL-b` (MOMS/OCC) | Drops once *N* exceeds *b* | **s ≈ 1** | None (up to MOMS tie-breaks) | #`DEC` grows with *N* |
| `DPLL-b` (MENTION/INDEX) | Same | s ≈ 1 | **Computed per item; either sign** | First decisions follow mention or index order |
| `BACKDOOR[INDEX]` / `[MENTION]` | ✓ iff the selected set is a backdoor | s ≈ 1 (k grows with *T*) | **High ✓, low Δ** | Enumerates the combinations of x1…xk up front |
| `BACKDOOR[OCC]` | ✓ iff the top-occurrence set is a backdoor (rare: about 3% at n = 28) | s ≈ 1 | None | Enumerates the top-occurrence set |
| NE | Smooth decline with *W* | s = 0 | None | Complete searches |
| C | ≈ 2^−k\* | s = 0 | Small (order changes which values it guesses) | `BT` = 0 |
| B1 | Δ everywhere (idle on pure 3-CNF) | — | — | — |
| F | Per-item simulation; weak *k\** dependence | *T* ↑ helps | None | `FULL` + `FLIP` |
| A | Flat | — | — | — |

**Metric.** A mixed logistic model: correct ~ *k\** × log₂*T* × presentation + covariates (#solutions, backbone, *W*, *F*_ref) + (1 | formula). It gives *k\**₅₀(T) and s.

**Weight statements (pre-registered).**

- **The budget-scaling search component** (π_DPLL + π_BACKDOOR) is estimated from s. Planted-model power is > 0.95 to detect s ≥ 0.5, so a null bounds that component ≤ 0.1 (upper 95%).
- **Within that component,** the presentation contrast moves weight between order-following and structure-following members, by the per-item likelihood ratios. In the library, a "high right, low wrong" pair on E3.3/E3.4 has log10 LR ≤ −1.9 against `DPLL-b[MENTION]`.
- **π_C** is the budget-flat component with accuracy ≈ 2^−k\*.

**Pre-registered CoT hypotheses.**

- **CT3.1:** in successful traces, the median number of distinct `DEC` variables is ≤ *k\** + 1 under `BACKDOOR-k`, and grows with *N*_ref under `DPLL-b`.
- **CT3.2:** in order-following (index- or mention-coded) traces, the share of first `DEC`s on x1…xk is ≥ 30 pp higher in the high presentation than in the low one. In MOMS-coded traces it is the same in both.
- **CT3.3:** in completed D-labelled traces, the log₂ tokens slope per +1 *k\** is in [0.5, 1.2]. C-labelled traces are flat.

**Power.**

- 3 *k\** × 2 presentations × 60 formulas × 3 budgets × 2 samples = 2,160 responses per model.
- s = 0.5 vs 0: power > 0.95 (planted simulation).
- The presentation effect is paired by formula (60 per *k\**): a 15 pp effect has power ≈ 0.8 per *k\** level.

**Threats.**

- **Selection confounds *k\** with #solutions and backbone.** Both are covariates, and *k\** bins are matched on them where the yield allows.
- **High salience by occurrence is rare in natural formulas** (about 3–9%). So `BACKDOOR[OCC]` vs `DPLL-b[MOMS]` is only an observational contrast.
- **Cost of the backdoor search.** It is exact for *k\** ≤ 4 at n = 36: about 60k subsets × ≤ 300 solution projections, a few seconds per formula in compiled code.

---

#### E4. Trap pairs: backtracking necessity

**Hypotheses.**

- **E4-H1:** when the value every greedy rule picks first for a variable *v* is a dead end that shows up only after another decision and *d* propagations:
  - D recovers: the accuracy difference Δ = acc(control) − acc(trap) ≈ 0;
  - C commits: Δ is large.
- **E4-H2:** under DIR (no chain of thought), the trap arm fails at C's rate for d = 4. This is the depth bound of §1.7.
- **E4-H3 (`BEAM-w` vs `DPLL-b`).** BEAM-1 and BEAM-2 fail specific, computed items:
  - BEAM-1 fails trap arms;
  - BEAM-2 gives a false UNSAT on some control arms (library item E4.6).

  Deferred multi-trap pairs, which would separate `BEAM-w` systematically, were not produced by this gadget (item 9 below).

**Generator: a "conditional cycle" gadget, pure 3-CNF.** Verified on the example library; the full spec is in §2.9.

1. **The live residual.** For each trap variable *v*, build an UNSAT 2-CNF on 2d − 1 core variables. It has two implication chains:
   - chain A: p → y₁ → … → y_{d−1} → ¬p;
   - chain B: ¬p → z₁ → … → z_{d−1} → p.

   Refuting it takes one decision on p plus d propagations per branch.
2. **The dead residual.** Flip chain A's closing clause to (¬y_{d−1} ∨ p). The residual is then SAT, with p forced to 1. It is greedy-safe under both TRUE and MAJ, which both pick p = 1.
3. **Two gadgets per trap, on disjoint core sets.**
   - G_T: each residual clause gets ¬v, so it is active only when v = 1.
   - G_F: each residual clause gets v.
   - The cores must be disjoint. A shared core would put every residual clause in the formula twice, as (¬v ∨ c) and (v ∨ c). Those resolve to c, which is both a visual cue and a shortcut by resolution.
4. **Arms.**
   - Trap arm: G_T live, G_F dead.
   - Control arm: G_T dead, G_F live.
   - So the arms differ by 2 literal signs per trap, and have the same number of "NOT" tokens.
   - *v* appears 2d times positive and 2d times negative in the gadgets.
5. **Fill and bridging.**
   - Planted 2-hidden fill on the fill variables (20 clauses on 8 variables in the library).
   - Bridging clauses: every gadget variable appears in at least one clause that a fill literal satisfies.
   - *v* gets 6 positive and 2 negative bridge occurrences.
6. **Presentation.**
   - A positive-*v* bridge clause comes first.
   - Trap variables take the lowest indices; all other names are random.
   - Literal order is shuffled.
   - Acceptance is re-run on the final presentation.
7. **Acceptance:**
   - (i) every C variant (`C-UC` MENTION/MOMS × TRUE/MAJ, and `C-GREEDY`) and `POLARITY` fails the trap arm;
   - (ii) every `C-UC` variant solves the control arm, while `POLARITY` fails it;
   - (iii) every primary DPLL variant has ≥ 1 backtrack on a trap variable in the trap arm and 0 in the control arm;
   - (iv) UP and `FLP-1` are idle (automatic in pure 3-CNF);
   - (v) WalkSAT, MIN-CONFLICTS and BEAM-1/2/4 outcomes are recorded.
   - **Measured acceptance rates:** 27% (d = 2, t = 1), 24% (d = 4, t = 1), 12% (d = 2, t = 2), 10% (d = 4, t = 2).
8. **Cells:** d ∈ {2, 4} × t ∈ {1, 2}, with 75 pairs per cell (300 pairs). *n* is about 15–38, which puts the items far below *n\**_BE for strong models.
9. **Deferral was not achieved.** No generated t = 2 pair defers the conflict for BEAM-2. Under MOMS, the core 2-clauses become the shortest clauses as soon as *v* is set, so the conflict surfaces at once. Deferral needs an order that branches on both trap variables before any core variable; that construction is open (§8).
10. **Colouring version.** k = 3, near the measured 50%-colourability density.
    - The trap vertex's lowest available colour starts a forced chain that ends in a conflict after *d* steps.
    - The control is one degree-preserving double edge swap, which makes the chain end consistently.
    - Acceptance uses DSATUR-BT, `FIRST-FIT`, DSATUR greedy and `MIN-CONFLICTS` simulations.
    - 150 pairs, d ∈ {2, 4}.

| Family | Trap arm | Control arm |
|--------|----------|-------------|
| `DPLL-b` | **A:** ✓ (costs +2 nodes and about 2d propagations under MOMS; MENTION can cost far more, e.g. 34 vs 6 nodes on E4.1/E4.2)<br>**T:** `DEC v=1`, `DEC p`, `CONF`, `BT`, `CONF`, `BT` on *v* → v = 0 | **A:** ✓<br>**T:** no `BT` on *v* |
| `BEAM-w` | **A:** BEAM-1 ✗ (greedy with one-step lookahead); BEAM-2 ✓ on every generated trap arm<br>**T:** `CASES`, `BT` = 0 | **A:** computed per item: BEAM-2 gives a false UNSAT on E4.6 |
| `BACKDOOR-k` | **A:** ✓ if *v* and p are in S and k ≥ 2 (simulated) | **A:** ✓ |
| C (every variant) | **A:** ✗: a dead end (infeasible, violating a G_T clause) or a false UNSAT (STOP)<br>**T:** `DEC v=1` … `CONF` with no `BT`, or `CONF` → "unsatisfiable" | **A:** ✓<br>**T:** one pass |
| B1 (`UP-k`, `FLP-1`) | **A:** Δ (idle)<br>**T:** stalls | **A:** Δ |
| F (POLARITY / RANDOM init) | **A:** simulated per item (P(success, k = n) = 0.17–0.72 on the library trap arms); failures are near-misses<br>**T:** `FULL`, `VIOL`, `FLIP`; *v* changes by `FLIP`, not `BT` | **A:** simulated; can be *lower* than the trap arm (E4.6: 0.33 vs 0.58) |
| NE | **A:** ✓ minus slips (ΔW is small, so Δ ≤ 0.02) | **A:** ✓ |
| A `POLARITY` | **A:** ✗ | **A:** ✗ (by acceptance (ii)) |

**Metrics.**

- Pair correctness, and Δ.
- McNemar's test.
- A mixed logistic model: arm × d × t + (1 | pair).
- Trap-arm errors classified as dead end / false UNSAT / near-miss / Δ.
- The paired token difference between arms.

**Weight statements (pre-registered).**

- **π_C on the trap arm ≈ Δ** = acc(control) − acc(trap), because C fails the trap arm and solves the control arm by construction. It is estimated per model with a 95% interval.
  - Power 0.9 to detect π_C ≥ 0.10 (300 pairs, α = 0.01).
  - If Δ̂ ≈ 0, the set bounds π_C ≤ 0.07 (upper 95%).
- **Per-response evidence:**
  - each dead-end trap-arm error (x_v = 1, infeasible or false UNSAT) has LR ≈ 20 for C over `DPLL-b`;
  - each LM0 near-miss trap error has LR > 5 for F over C.
- **The backtracking share** of the non-C weight is read from the trace: the fraction of correct trap responses with a `BT` on *v*, weighted by R_m.
- **Not identified here: π_NE** (Δ ≤ 0.02 either way). See E1–E3.
- **The DIR arm:** π_C(DIR) at d = 4. π_C(DIR) − π_C(BE) is the weight moved from C to D by thinking.

**Pre-registered CoT hypotheses.**

- **CT4.1:** P(`BT` on *v* | trap, correct) ≥ 0.7 and P(`BT` on *v* | control) ≤ 0.1 (D). C predicts ≈ 0 in both arms. F predicts that *v* changes by `FLIP`.
- **CT4.2:** tokens between *v*'s first assignment and its reversal grow linearly in *d* (slope > 0, CI excluding 0).
- **CT4.3:** the phantom-backtrack rate (FA2) on *v* is ≤ 5% for D-classified models.
- **CT4.4:** trap-arm errors end with v = 1 and either a stated contradiction followed by UNSAT (`C-UC/STOP`) or no stated contradiction (`C-CONT`).

**Power.**

- 300 SAT pairs per model.
- **C weight:** with π_C = 0.10 plus 5% symmetric discordance, there are 60 discordant pairs split 45 : 15. Then z ≈ 3.9, and power ≈ 0.9 at α = 0.01.
- **Equivalence for D:** with true Δ = 0.02, SE ≈ 0.02, so the upper bound is 0.02 + 1.645 × 0.02 = 0.053 < 0.07, and power ≈ 0.8.
- **Per cell** (75 pairs): Δ = 0.2 is detectable at 0.9.
- **Colouring:** 150 pairs, Δ = 0.15 at 0.9.

**Threats.**

- **The model may spot the gadget** and reason structurally, which is sound lookahead. That still counts as "not C", and the trace shows which. Polarities are renamed and clauses interleaved.
- **The model's value rule may lie outside the four in acceptance (i).** Then the "trap" is not a trap for that model. CT2.2 estimates the model's value rule. Pairs where the model's first stated value for *v* was 0 are analysed separately: pre-registered, and treated as a manipulation check.
- **Items sit at about 0.6 *n\**_BE,** so BE caps are rare (< 6%).

---

#### E5. Certificate pairs: can the model certify UNSAT?

**Hypotheses.**

- **E5-H1:** below budget, D (and NE) answer UNSAT on the UNSAT arm with a *valid* core, and answer SAT on the SAT arm.
- **E5-H2:** F's "UNSAT"/core claims do not depend on the arm. F names the stubborn cluster on *both* arms, and more often when the SAT arm is hard for local search.
- **E5-H3:** neither B1 (the core is not UP- or FLP-refutable) nor `A-CORE` (decoys) does better than its simulated rate.

**Generator.**

1. **Three dense 5-variable clusters**, each with 12–16 3-clauses:
   - **K_live:** minimally unsatisfiable. Not UP- or FLP-1-refutable; refutation needs ≥ 2 decisions under every primary variant; it never contains all 8 sign patterns of one triple, which would be a visual signature.
   - **K_d1, K_d2:** satisfiable decoys, each one literal flip away from a minimally unsatisfiable set.
2. **Fill:** about 15 further variables, with polarity-balanced planted fill at α_f = 3.5.
3. **Bridging clauses:** each contains a cluster variable and a non-cluster literal that is true under the fill assignment. This connects the variable–clause graph without constraining the clusters.
4. **Arms:**
   - **UNSAT arm:** K₁ = K_live.
   - **SAT arm:** one literal of K₁ flipped, giving a satisfiable K₁′ with few solutions.
   - So the arms are **one literal apart**.
   - Which cluster is live, and where the clusters sit in the clause order, are both randomised.
5. **Factor L, local-search hardness of the SAT arm** (WalkSAT median flips, top vs bottom tercile): 100 pairs each.
6. **Size:** n ≈ 30, m ≈ 100.
7. **Acceptance:**
   - K_live is the only unsatisfiable subset with ≤ 24 clauses (MUS enumeration);
   - *N*_CHR and *N*_CBJ are recorded. Chronological backtracking may re-refute K_live once for every decoy branch, so this is a measured predictor that separates CHR from CBJ;
   - `A-CORE` is valid in about 1/3 of items.

**Answer format:** `{"answer":"UNSAT","core":[≤ 24 clause IDs]}` or a SAT assignment.

**Metrics.**

- ADR.
- **Sensitivity:** P(UNSAT with a valid core | UNSAT arm). A core is valid if the solver finds the listed subset UNSAT.
- **False alarm:** P(UNSAT | SAT arm). Cores on the SAT arm are invalid by construction.
- **Core precision:** the share of listed clauses that are in K_live.

| Family | UNSAT arm | SAT arm, L easy | SAT arm, L hard |
|--------|-----------|-----------------|-----------------|
| `DPLL-b` (within budget) | **A:** UNSAT with a valid core, precision ≈ 1<br>**T:** a case tree over K₁'s variables, every branch closed (FA6); CHR re-visits decoy decisions, CBJ does not | **A:** ✓ | **A:** ✓ (32 combinations on K₁′) |
| `DPLL-b` (over budget) | **A:** Δ, with no valid core<br>**T:** cap/`GIVEUP` | **A:** ✓ / Δ | **A:** ✓ / Δ |
| NE | **A:** mostly valid cores; slips | **A:** ✓ | **A:** ✓ |
| F | **A:** a near-miss claimed SAT (violating 1 K₁ clause), or UNSAT with a "stubborn-cluster" core, which can be valid as a superset<br>**T:** repeated `FULL`/`VIOL` on K₁, never a complete tree | **A:** ✓ | **A:** **UNSAT claims rise** (core = K₁′, invalid) |
| C | **A:** false-UNSAT style; the core is the dead-end clause (invalid) | **A:** dead ends sometimes | **A:** dead ends sometimes |
| B1 | **A:** Δ (cannot refute) | **A:** Δ | **A:** Δ |
| `A-CORE` | **A:** UNSAT; valid ≈ 1/3 | **A:** UNSAT (false alarm) | **A:** UNSAT (false alarm) |

**Weight statements (pre-registered).**

- **π_certify** (`DPLL-b` within budget + NE + EXACT) comes from valid-core sensitivity. Each valid-core, FA6-complete UNSAT has LR ≈ 20 against F, C and `A-CORE`.
- **π_F** comes from the L-dependence of false alarms.
  - Power ≈ 0.95, pooled across models, to detect π_F ≥ 0.15.
  - A null bounds π_F ≤ 0.12 (upper 95%, pooled).
- **π_A-CORE** comes from UNSAT claims made on both arms with cluster-random cores (valid ≈ 1/3).
- **π_C** comes from dead-end false UNSATs.
- **Not identified here:** NE vs `DPLL-b` (both certify).

**Pre-registered CoT hypotheses.**

- **CT5.1:** among correct UNSAT-arm responses from D-labelled traces, ≥ 60% are FA6-complete. F-labelled UNSAT claims follow ≥ 2 `FULL` attempts that leave a K₁ clause violated.
- **CT5.2:** the listed core overlaps the clauses cited in `CONF` events by ≥ 80% (D). F's listed core is a subset of the clauses cited in `VIOL`.
- **CT5.3:** `GIVEUP` precedes ≥ 70% of UNSAT answers that lack a valid core.
- **CT5.4:** D-labelled traces revisit decoy decisions in proportion to *N*_CHR / *N*_CBJ: CHR if ρ > 0.3, CBJ if repeated refutations of K₁ are rare.

**Power.**

- 200 pairs per model.
- Sensitivity of 0.7 vs 0.33 is decisive (CI ±0.08 on about 150 UNSAT claims).
- A false-alarm difference of 0.10 between L cells (100 vs 100 pairs × 2 samples) has power ≈ 0.6 per model and ≈ 0.95 pooled.

**Optional rendering** (not in the budget): 60 pairs rendered as entailment. "Do these rules imply X? If so, list the rules needed; if not, give a counterexample." This tests whether the certification behaviour transfers.

**Threats.**

- **A valid core does not prove a refutation:** a superset guess by F can be valid. Hence the pair design (specificity) and FA6.
- **Decoys make the instances look unusual.** Both arms share them.
- **The core-listing instruction might itself prompt search.** It is the same in both arms; a pilot compares accuracy with and without the core field.

---

#### E6. Violation profiles: where wrong assignments come from

**Hypothesis (E6-H1).** The infeasible SAT answers from E1–E5 and E7 come from a mixture of identifiable sources:

- F near-misses;
- D FILL defaults;
- C dead ends;
- NE slips;
- PERCEPTION misreadings.

The shares are recovered by likelihood against each member's simulated distribution of the statistics below.

**Statistics for each wrong answer *y* on item *x*.**

- **V:** the number of violated clauses.
- **H:** Hamming distance to the nearest solution, exact by enumeration or by RC2 MaxSAT in PySAT.
- **LM0:** no violated clause has a break-0 variable, i.e. *y* is a WalkSAT local minimum.
- **Tail concentration:** under each primary order, the share of violated clauses whose variables all lie in the first half of the order. FILL predicts ≈ 0.
- **Frustration log-likelihood ratio:** the mean log of each violated clause's probability of being the leftover violated clause in 200 WalkSAT runs, against uniform.
- **Prompt position** of each violated clause.
- **Same-clause consistency** across the 2 samples.
- **Verification probe** (E6-VER): in a fresh context, at CoT-2k, the model is given its own assignment and asked which clauses it violates. Does it find the violated clause?
- **Misquote check:** does the trace restate the violated clause with a wrong sign or index (PERCEPTION)?
- **Colouring:** an edge echo after the answer. Is the violated edge missing from the echo (perception; Heyman & Zylberberg 2025b report hallucinated edges as a main source of colouring errors)?

**Dedicated set E6-COL.** 300 3-colouring items:

- n ∈ {20, 30}, at the measured 50%-colourability density;
- 70% colourable;
- answer, then edge echo.

| Statistic | F | D FILL | C dead end | NE slip | PERCEPTION | A `POLARITY` |
|-----------|---|--------|------------|---------|------------|--------------|
| V | 1–3 | ∝ size of the tail | 1 + whatever the fill breaks | 1 | Number of misreadings that matter (usually 1) | Large (simulated) |
| H | Small, except at decoys | ≈ tail / 2 | Variable | Variable | Small (a solution of a nearby formula) | Large |
| LM0 | **≈ 1** | Low | Low | Simulated base rate (expected 0.3–0.6) | Simulated base rate | Low |
| Tail concentration | None | **High** | High (in its own order) | None | None | None |
| Frustration LLR | **> 0** | ≈ 0 | ≈ 0 | ≈ 0 | ≈ 0 | ≈ 0 |
| Same clause across samples | Low | High | High | Low | **High** | High |
| Verification probe finds it | Yes | Yes | Yes | Yes | **No** | Yes |
| *V* vs budget | ↓ | ↓ (tail shrinks) | Flat | Flat | Flat | Flat |
| Trace | `FULL`/`VIOL`/`FLIP`; an honest leftover-violation statement | cap/`GIVEUP` | `CONF` without `BT` | False `VERIFY` (FA3) | Misquoted clause | Little search |

**Metric.** Each answer gets a posterior over sources from a kernel density over (V, H, LM0, tail, frustration), multiplied by the binary channels. The shares and their lift over a permutation baseline are reported. Planted-model recovery must pass first.

**Weight statements (pre-registered).**

- **Source shares.** Posterior mean and 95% interval over {F, D-FILL, C, NE, PERCEPTION, POLARITY, none}, with lift over a permutation baseline matched on *V*.
- **F is identified only by the joint pattern:**
  - an LM0 share above the NE/PERCEPTION base rate;
  - a frustration LLR > 0;
  - *V* falling with budget.

  Single answers do not separate F from C, or NE from PERCEPTION: the library has identical answers from different sources.
- **Per-probe evidence:**
  - a violation missed on re-check: LR ≈ 9 for PERCEPTION over F and NE;
  - the same clause violated across samples: LR ≈ 5 for PERCEPTION over NE.
- **Power.** About 1,000 infeasible answers per model give the LM0 share to ±3%, and power > 0.9 to detect an F share ≥ 0.15 above the NE base rate.

**Pre-registered CoT hypotheses.**

- **CT6.1:**
  - ≥ 60% of F-classified answers come from traces with `FULL` + `VIOL` + ≥ 2 `FLIP`;
  - D-FILL-classified answers come with cap/`GIVEUP`;
  - NE-classified answers come with a false `VERIFY`.
- **CT6.2:** in F-labelled traces, the last stated leftover-violation list matches the answer's actual violated clauses in ≥ 70% of cases (an "honest near-miss").
- **CT6.3:** ≥ 50% of PERCEPTION-classified errors whose clause the trace quotes are misquoted.

**Power.** Each model is expected to give 800–1,500 infeasible answers, so the LM0 rate is estimated to ±3%. With 300 colouring items × 2 samples, about 150 infeasible colourings are expected.

**Threats.**

- **The base rates depend on how the members are parameterised.** Use several settings (ε, p) and report the range.
- **The verification probe is a new context,** and may not show what the model perceived during its original run.

---

#### E7. Initialisation counterfactuals: seeded candidates

**Hypotheses.**

- **E7-H1 (F):** success rises as the seed moves closer to a solution, and errors stick to a decoy seed.
- **E7-H2 (D):** success does not depend on the seed.
- **E7-H3 (vs `ECHO`):** an infeasible seed is improved on, not copied.

**Design (within-item).**

- **SAT:** 80 items at about 0.8 *n\**_BE, with 1–4 solutions. Seed conditions:
  - **S0:** no seed. A placeholder line ("No candidate is available.") keeps the prompt length matched.
  - **S2, S4, S8:** Hamming distance *h* = 2, 4 or 8 from the nearest solution, inside its basin (WalkSAT from the seed reaches it in median ≤ 2h flips).
  - **SD:** a decoy. An LM0 local minimum with *V* = 1, at Hamming distance ≥ n/3 from every solution, where WalkSAT's median number of flips to a solution is ≥ 10× S8's.
  - **SR:** a random assignment.
- **Seed wording:** "A candidate assignment (it may be wrong; you may ignore it): …". Neutral, with no social framing.
- **Colouring:** 60 graphs. Conditions: S0; S-near (2 conflicts, inside the basin); SD (a 1-conflict local minimum far from every proper colouring); SR.
- **TSP:** 60 instances, n ∈ {10, 12, 14}, with an integer distance matrix (no arithmetic from coordinates). Conditions:
  - S0;
  - S-2opt: a 2-opt local optimum 8–15% above optimal;
  - S-cross: a tour with 2–3 crossings, whose 2-opt descent ends at a known non-global local optimum;
  - SR.

| Family | S2 / S4 / S8 | SD (decoy) | SR | TSP S-2opt |
|--------|--------------|------------|----|------------|
| F (`WALK-k`, `MIN-CONFLICTS`, `2OPT-k`) | **A:** success S2 > S4 > S8 > S0<br>**T:** `SEEDREF` → `VIOL` → `FLIP`s ≈ h | **A:** ✗; errors within Hamming 2 of the decoy<br>**T:** `FLIP`s around the decoy | **A:** ≈ S0 | **A:** **returns the seed unchanged** (already locally optimal)<br>**T:** `MOVE`s fail to improve |
| D | **A:** equal to S0 (a phase effect can cut nodes, changing results only under budget)<br>**T:** seed ignored, or checked once | **A:** equal to S0; errors are Δ-type, not near the decoy | **A:** = S0 | (not tested) |
| C | **A:** ignores the seed, or follows it until a dead end ("seeded greedy")<br>**T:** no `BT` | **A:** dead ends near the decoy, *not* LM0 | **A:** = S0 | **A:** NN tour |
| `ECHO` | **A:** the seed verbatim | **A:** the seed verbatim | **A:** the seed verbatim | **A:** the seed |
| NE | **A:** as D | **A:** as D | **A:** as D | — |

**Metrics.**

- A within-item logistic model on seed condition.
- **Decoy proximity:** the share of errors within Hamming 2 of the decoy.
- **Echo rate:** answer = seed, for infeasible seeds.
- d(answer, seed) vs. d(answer, nearest solution).
- **TSP:** crossings; Kendall distance to the seed; whether the answer equals the seed's 2-opt descent; optimality.

**Weight statements (pre-registered).**

- **π_F** comes from the seed-distance slope and from decoy-proximal errors. Decoy-proximal errors have a null rate ≈ 0, so each one has LR > 10 for F over D.
  - Power 0.8 to detect π_F ≥ 0.15.
  - A null bounds π_F ≤ 0.08 (upper 95%).
- **π_ECHO** is the verbatim-echo rate of infeasible seeds. **π_C(seeded)** is the rate of seed-proximal dead ends.
- **MIN-CONFLICTS vs WALK-k** are separated by the SD outcomes. In the library, starting from the decoy, MIN-CONFLICTS has P(success) = 0 and WALK-k has 0.98.
  - That decoy is too shallow for WALK-k: at dev size WALK-k ties with `DPLL-b`.
  - The SD acceptance rule (§2.9) is what makes WALK-k separable.
- **TSP.** Tours are discrete, so one S-2opt or S-cross outcome gives |log10 LR| ≥ 2 between `2OPT-k`, EXACT, `NN-from-0` and `ECHO` (library LR table).

**Pre-registered CoT hypotheses.**

- **CT7.1:** ≥ 50% of F-labelled seeded traces evaluate the seed first (`SEEDREF` + `VIOL`).
- **CT7.2:** #`FLIP` up to the answer ≈ Hamming(seed, answer), with Spearman ρ ≥ 0.5.
- **CT7.3:** D-labelled traces do not mention the seed after the first 10% of the trace.

**Power.**

- SAT: 80 items × 6 conditions × 2 samples. A within-item S2 vs S0 difference of 15 pp has power ≈ 0.8.
- Decoy proximity: F weight 0.05 is detectable (160 SD responses against a null near 0).
- Colouring and TSP: 60 items × 4 conditions, for large effects (≥ 20 pp).

**Threats.**

- **Anchoring and sycophancy toward any candidate.** Neutral wording, the "you may ignore it" clause, and `ECHO` as an explicit competitor.
- **The seed adds about n tokens.** Matched by the S0 placeholder.
- **A seed changes the problem the model sees**, so it is a demand cue. The SR condition controls for "a seed exists".

---

#### E8. Truncation, resumption and state corruption

This is behavioural: prefilled continuations on open models.

**Hypotheses.**

- **E8-H1:** the answer forced at point *f* of a trace equals the trace's *current* search state.
  - D: partial assignment + Δ.
  - F: the latest `FULL` candidate.
  - Post-hoc: the answer is fixed before search starts (Cox et al. 2026).
- **E8-H2:** editing a written decision changes the final answer in the direction the reference procedure, re-run from the edited state, predicts.
- **E8-H3 (F is anytime):** the violation count of the forced answer, *V*(f), falls roughly monotonically under F, but not under D.

**Design.**

- **Panel subset:** gpt-oss-20b, gpt-oss-120b, Qwen3-32B and Qwen3-30B-A3B. They are chosen because prefilling their raw thinking is well supported.
- **Source traces:** 300 BE traces from E2 and E4, balanced across D/F/C labels and correct/incorrect.
- **Cut points (sentence boundaries):**
  - f ∈ {0 (just after the thinking opens), 0.1, 0.25, 0.5, 0.75, 0.9};
  - just before the first `BT`; just after the first `BT`; just after the first `FULL`.
- **At each cut:** close the thinking and force the answer (Lanham et al. 2023 early answering). 2 samples.
- **Resumption** (200 traces, cut after ≥ 3 `DEC`/`FLIP`). Three edit conditions:
  - a **relevant edit:** flip the latest written value of a decided variable;
  - a **control edit:** reword one connective;
  - **no edit.**

  Generation then resumes to completion within the remaining BE budget (Lanham et al. mistake insertion). Thought-anchor-style resampling from each event boundary (Bogdan et al. 2025) is an optional add-on.

| Family | Forced answer at f | V(f) | Trap items: before / after the first `BT` | After a relevant edit |
|--------|--------------------|------|-------------------------------------------|----------------------|
| D | The trace state + Δ; ≥ 70% agreement with the reference "state + fill" | Not monotone; drops when the trace reaches a solution | v = 1 / v = 0 | Continues from the edit: detects a conflict and backtracks (more tokens), or the answer carries the edit. Agrees with reference DPLL from the edited state |
| F | The latest `FULL` | **Falls, ρ ≤ −0.3** | n/a | Repairs onward from the edited candidate |
| C | Greedy prefix + fill | Not monotone | v = 1 / v = 1 | Carries the edit, without backtracking |
| Post-hoc | ≈ the final answer even at f = 0 (agreement ≥ 0.8) | Flat | Final value / final value | **Edit ignored**: the final answer is unchanged ≥ 90% of the time |

**Metrics.**

- Agreement curves.
- Per-trace Spearman correlation of *V*(f).
- **Corruption-following:** P(the answer agrees with the reference re-run from the edited state) under the relevant edit, minus the same under the control edit.
- FA7.

**Weight statements (pre-registered).**

- **π_POST-HOC** is the *f* = 0 agreement with the final answer, above the reference-at-0 rate, with its 95% interval.
- **Corruption-following** above the control edit enters R_m (§2.6). Power > 0.99 for a 30 pp difference.
- **What this set re-weights.** It acts on the *trace channel*, not the families. A high π_POST-HOC lowers R_m, and with it the weight of every CT test for that model.

**Pre-registered CoT hypotheses.**

- **CT8.1:** after a relevant edit, the resumed trace mentions the edited variable within 2k tokens in ≥ 50% of cases.
- **CT8.2:** the rate of explicit self-correction ("that was a mistake, x5 should be 0") is reported. It shows the model reads its state, and it is neutral with respect to the answer.

**Power.**

- *V*(f) monotonicity: a sign test across about 100 F-labelled traces has power ≈ 0.9 for a median ρ of −0.3.
- Corruption-following: 200 traces × 2 samples gives power > 0.99 for a 30 pp difference, and ≈ 0.8 for 15 pp.

**Threats.**

- **Edits are off-policy text,** and models may notice tampering. Control edits and self-correction coding address this.
- **Cutting mid-reasoning** is done only at sentence boundaries.
- **gpt-oss** needs the harmony analysis channel to be prefilled exactly.

### 2.8 Eval designs (template table)

The template's "supported if / against if" columns are replaced by weight quantities (§2.5).

| ID | Item generator | Answer format | Weight quantity | Detectable (power) | Bound when the effect is null |
|----|----------------|---------------|-----------------|--------------------|-------------------------------|
| E1 | Random 3-SAT pairs one sign apart, α = 4.26, *n* on a grid centred on *n\**; density arm | Assignment / UNSAT / UNKNOWN | π_DPLL vs π_NE above *n\** (via β and termination type); π_F on UNSAT members (via certification); π_A (via ADR) | π_DPLL ≥ 0.15 vs NE at 0.8 | π_DPLL ≤ 0.15 if β ≈ 0; π_F(UNSAT) ≤ 0.1 with ≥ 30 certified |
| E2 | Random + q-hidden SAT, quadrants on *W* × *F*_ref at n_Q | Assignment | π_DPLL and π_F (feature-dependent, via the *W* and *F*_ref effects); b̂(T) | A component of about 0.2 at 0.93 | π_DPLL ≤ 0.15; π_F ≤ 0.15 |
| E3 | Natural formulas selected on *k\** ∈ {2, 3, 4}; two presentations | Assignment | Budget-scaling search component via s; order- vs structure-following via presentation | s ≥ 0.5 at > 0.95 | Component ≤ 0.1 |
| E4 | Conditional-cycle trap gadgets (SAT, colouring), 2 signs per trap | Assignment / colouring | π_C ≈ Δ; `BT`-on-*v* share × R_m | π_C ≥ 0.10 at 0.9 | π_C ≤ 0.07 |
| E5 | Live MU cluster + 2 decoys + fill; SAT twin 1 literal away; L factor | UNSAT + core / assignment | π_certify; π_F via L-dependence; π_A-CORE | π_F ≥ 0.15 at 0.95 (pooled) | π_F ≤ 0.12 (pooled) |
| E6 | Infeasible answers from E1–E5 and E7; 300 colouring items | — (plus probe and echo) | Source shares over F, D-FILL, C, NE, PERCEPTION | F share ≥ 0.15 above the NE base rate at > 0.9 | — |
| E7 | Seeds at h = 2/4/8, decoy, random; colouring and TSP analogues | Assignment / colouring / tour | π_F via the seed slope and decoy-proximal errors; π_ECHO; π_2OPT (TSP) | π_F ≥ 0.15 at 0.8 | π_F ≤ 0.08 |
| E8 | Prefix cuts and forced answers; edits + resumption | As source | π_POST-HOC; R_m | 30 pp corruption-following at > 0.99 | — |

### 2.9 Generator specifications

The example library ([D_F_search_questions.md](D_F_search_questions.md)) was produced by throwaway versions of these generators, kept outside the repo. Every ground truth and prediction there was computed by brute force or z3. Yields below were measured at dev scale this session unless marked "estimate".

**Rules shared by every generator.**

- **Rendering.** One fixed template per domain (§2.5): clauses `Cj: (x3 OR NOT x12 OR x7)`, variables x1…xn, and a final-line JSON answer.
- **Variants share everything except the manipulated literals or lines:**
  - the same names;
  - the same clause order and literal order;
  - the same template text.
- **Token matching.**
  - E1 and E5 twins differ by one "NOT", i.e. ±1–2 tokens.
  - E4 arms have the same "NOT" count: the live/dead flips cancel.
  - E3 presentations are isomorphic relabellings. Their token counts can differ slightly, because variable numbers have different lengths; this is recorded.
  - E7 seed conditions differ only in the seed line. S0 uses a placeholder of similar length.
- **Content hashing.** Each item stores:
  - the SHA-256 of its canonical clause multiset (sorted literals within clauses, sorted clauses);
  - an isomorphism-invariant hash: canonical labelling of the signed clause–variable incidence graph, via nauty or pynauty;
  - its source item's hash (DESIGN §5.1).
- **Keeping dev and test disjoint.**
  - Dev items are drawn from RNG seeds below 10⁶, test items from seeds of 10⁹ and above.
  - Every variant of a base item goes to the same split as the base.
  - E8 prefixes come from traces of same-split items.
  - A script asserts that no isomorphism hash appears in both splits before any analysis runs.
- **Rejection is always on computed predictions,** never on intuition. The member predictions that define a cell are re-run on the *final rendered* item.

**Per-eval specifications.**

| Eval | Template and parameters | Constraints and rejection rules | How variants are derived | Yield |
|------|-------------------------|---------------------------------|--------------------------|-------|
| E1 | Random 3-SAT: *n* on the grid {8, 10, …, 72}; m = round(4.26n); 3 distinct variables per clause; uniform signs; no duplicate clauses. Density arm: α ∈ {3.0, …, 6.0} at *n\**_BE | Draw until UNSAT, then search literal flips (random order) for a SAT twin with 1–4 solutions. Above n = 40, use incremental CaDiCaL for the flip search (≤ 3m calls) | SAT twin = that one flip. Themed twin = the same clauses rendered as product-configuration requirements | n = 12: P(UNSAT) = 0.24, and 98% of UNSAT draws have a qualifying flip, so about 4 draws per pair. Near the threshold at larger *n*, P(UNSAT) approaches 0.5 (estimate) |
| E2 | Random 3-SAT conditioned on SAT with ≤ 30 solutions at n_Q, plus q-hidden proposals with *q* tuned so the per-variable MAJ agreement with the hidden assignment is 0.50 ± 0.02 | *W* = the upper median over the 6 variants' work. *F*_ref = WalkSAT median flips (60 runs, p = 0.5, cap 3,000). Quadrants are tercile splits within the pool. Per quadrant, keep the items whose log #solutions is nearest the pool median, and match backbone, *g*(x) and polarity agreement | None (between-item cells) | n = 14, 220 SAT draws: 51 / 47 on the diagonal, but only **5 (W high, F low) and 7 (W low, F high)**, i.e. 2–3% each. For 100 per off-diagonal cell, draw about 4,000 natural formulas per *n*, or fill up to 50% of the cell with flagged constructions |
| E3 | Random 3-SAT, n ∈ {24, 36}, α = 4.26 | Keep SAT formulas with ≤ 300 solutions. Compute the exact minimum weak UP-backdoor size *k\** ≤ 4 and a minimum set S. Bin by *k\**, and match the bins on #solutions and backbone | **Presentation pair:** high = S renamed x1…xk, S-clauses first (most S literals first), S literals first; low = S renamed x_{n−k+1}…x_n, S-clauses last. Same formula | Natural *k\**: n = 20: 2 (80%), 3 (20%); n = 28: 2 (40%), 3 (57%), 4 (2%); n = 36: 2 (9%), 3 (74%), 4 (17%). About 350 SAT draws give 60 formulas with *k\** = 4 at n = 36. Top-occurrence set is a backdoor in about 3% (n = 28) to 9% (n = 36) of formulas. **Planting *k\** ≥ 3 failed: 0 of about 120 attempts at n = 14** |
| E4 | d ∈ {2, 4}, t ∈ {1, 2}, 8 fill variables with 20 planted 2-hidden fill clauses, bridging as in §2.7 E4 | Acceptance (i)–(v) of §2.7 E4, re-run after the final renaming and literal shuffle | Trap ↔ control = flip the closing sign of chain A in both gadgets (2 signs per trap) | Acceptance 27% / 24% / 12% / 10% for (2,1) / (4,1) / (2,2) / (4,2). Deferred-conflict pairs for BEAM: 0 found |
| E5 | Three 5-variable clusters with 11–16 clauses each, built by random accumulation from the 80 possible clauses until UNSAT, then deletion-based shrinking to minimally unsatisfiable. Plus 7 fill variables, 25 planted 2-hidden fill clauses, and 15 bridging clauses (one per cluster variable, satisfied by a fill literal). Variables randomly relabelled; clause order randomly permuted, the same in both arms | The UNSAT arm must be UNSAT with K_live an unsatisfiable subset; the SAT arm must be SAT. Each decoy is a twin with ≤ 3 cluster solutions. The L factor = WalkSAT median flips on the SAT arm (60 runs); keep the top and bottom terciles | SAT twin = the first literal flip inside K_live that leaves 1–3 cluster solutions | 100% of clusters gave a valid twin (40/40). 10 pairs in 10 attempts. L spread 23–85 flips |
| E6 | Probes: the item's clauses + "Here is an assignment: …" (the model's own wrong answer) + list the violated clauses. Colouring: random graphs at the measured 50%-colourability density, c = 3, n ∈ {20, 30}, with an edge echo after the answer | Probe only infeasible answers. Controls: feasible assignments, whose correct answer is [] | — | One probe per wrong answer (about 1,500 per model) |
| E7 | SAT: random 3-SAT at about 0.8 *n\**_BE with 1–4 solutions. TSP: n ∈ {10, 12, 14} cities on an integer grid 0–60, rounded Euclidean distances given as a table | **S_h:** flip h variables of a solution s₀. Accept if the nearest solution is at distance h and WalkSAT from the seed reaches s₀ in ≥ 50% of 60 runs, with a median ≤ 2h flips. **SD:** greedy descent (WalkSAT, p = 0) from 3,000 random starts; keep V = 1, LM0 endpoints at Hamming ≥ n/3 from every solution; take the one with the largest median flips to a solution; **accept only if that median is ≥ 10× S8's.** **SR:** V ∈ [m/10, m/6]. **TSP S-2opt:** a FIRST-improvement 2-opt optimum 6–18% above optimal. **TSP S-cross:** 2–3 crossings, with a FIRST descent ending at a non-global optimum | The same prompt with the seed line swapped | n = 12: the deepest decoy had a median of 12 flips, so **no n = 12 decoy passes the SD rule**. WALK-k escapes 98% of the time, while MIN-CONFLICTS stays stuck (0%). Use n ≥ 20; yield to be measured. TSP (n = 8): a valid S-2opt / S-cross set at the 19th instance |
| E8 | Source traces: BE traces of same-split E2/E4 items, balanced across D/F/C labels and correctness | Cuts only at sentence boundaries. Relevant edit = flip the last written value of the most recent decided variable. Control edit = reword one connective | Prefix + forced answer; prefix + edit + resume within the remaining budget | — |

### 2.10 Coverage: which sets can push which theory's weight down

● = the set has an outcome pattern with log10 LR ≤ −1 against the theory relative to its nearest rival, computed in the library's LR tables or by the design's power analysis; at the planned *N* this gives a bound on π.
◐ = only weak (−1 < log10 LR < 0), or only on specific items, or only in combination with another set.
— = not tested.

| Set | EXACT | DPLL-b | BEAM-w | BACKDOOR-k | WALK-k | MIN-CONF | SA | 2OPT-k | C (UC, GREEDY) | NN | POLARITY / A | B1 | NOISY-EXACT | PERCEPTION | RANDOM | ECHO | A-CORE | POST-HOC |
|-----|-------|--------|--------|------------|--------|----------|----|--------|----------------|----|--------------|----|-------------|------------|--------|------|--------|----------|
| E1 | ● | ● | ◐ | ◐ | ● | ● | ◐ | — | ● | — | ● | ● | ● | ◐ | ● | — | — | — |
| E2 | ◐ | ● | ◐ | ◐ | ● | ● | ◐ | — | ● | — | ● | ● | ● | ◐ | ● | — | — | — |
| E3 | ◐ | ● | ● | ● | ◐ | ● | ◐ | — | ● | — | ● | ● | ● | — | ● | — | — | — |
| E4 | ● | ● | ● | ● | ◐ | ● | ◐ | — | ● | — | ● | ● | — | — | ● | — | — | — |
| E5 | ● | ● | ◐ | ◐ | ● | ● | ◐ | — | ● | — | ● | ● | ◐ | — | ● | — | ● | — |
| E6 | — | ◐ | — | — | ● | ◐ | ◐ | — | ◐ | — | ◐ | — | ● | ● | — | — | — | — |
| E7-SAT | ◐ | ● | — | — | ◐ (● at n ≥ 20) | ● | ◐ | — | ● | — | — | — | ● | — | ● | ● | — | — |
| E7-TSP | ● | — | — | — | — | — | — | ● | — | ● | — | — | — | — | ● | ● | — | — |
| E8 | — | ●† | — | — | ●† | — | ◐† | — | ◐† | — | — | — | — | — | — | — | — | ● |

† As a *trace* procedure: E8 weights the trace channel, not the families.

**Reading the matrix.**

- **Every theory has at least one ●.**
- **The nulls:**
  - EXACT: E1 (a collapse inside the sweep), E4, E5, E7-TSP.
  - NOISY-EXACT: E1/E2 (budget interaction, termination type), E3 (s), E6 (re-check plus variability), E7.
  - PERCEPTION-NOISE: E6 (missed re-checks, same-clause repeats).
  - RANDOM: every answer-level set.
- **The weak spots:**
  - **`SA`** is not separable from `WALK-k` at the answer level; that merge is pre-registered. Only its trajectory (uphill acceptance falling over the trace) is testable, so it is ◐ everywhere.
  - **`BEAM-w` vs `DPLL-b`** rests on item-specific failures (E3, E4), because the deferred-conflict construction is still open.
  - **`WALK-k` in E7-SAT** needs n ≥ 20 decoys.
  - **NOISY-EXACT in E4** ties with `DPLL-b`, by design. E1–E3 carry that contrast.

## 3. Mechanistic evidence: Phase 2 (only if behavioural evidence)

*This runs only if Phase 1 finds a non-negligible weight for D or F (a lower 95% bound on π_D or π_F ≥ 0.1) for at least one model. Kept short on purpose.*

**State variables.** What D and F say the model must hold, at step boundaries in the chain of thought:

1. **Each variable's value in the current partial assignment** (3-way). This is mostly readable from the text, so it serves as a sanity check.
2. **Literals implied but not yet written,** i.e. ones UP would derive now that the model writes later.
3. **A conflict flag, before the conflict is written down.**
4. **Decision depth,** the number of open alternatives.
5. **For F:** the set of violated clauses for the current candidate.

**Probes.**

- Linear probes at every layer, at event-boundary positions.
- **Controls:**
  - Hewitt & Liang (2019) control tasks;
  - residualising on surface format (*n*, *m*, position, trace length; Sahoo et al. 2026);
  - **prefix-matched, formula-differing pairs.** The same written trace prefix is prefilled into two formulas that differ by one literal, so the true label (implied literal, conflict) differs while the text is identical.
- A probe that reads only the text fails this control. Behaviourally, the pair also tests whether the next `CONF`/`BT` depends on the clauses.

**Interventions.**

- **Suppress the backtracking direction** (difference of means before backtracking sentences; Venhoff et al. 2025; reused from base models per Ward et al. 2025) on E4 pairs.
  - Prediction: mixture weight shifts **from D to C**. Trap-arm accuracy falls to C's level, errors become dead ends, and control-arm accuracy stays within 5 pp.
  - Controls: a norm-matched random direction (Cox et al. 2026), and the "uncertainty" direction as a competitor.
- **Amplifying** the direction should add backtracks on control arms without changing accuracy there.
- Linear maps only (Sutter et al. 2025).

**Pre-CoT commitment.**

- Probe at the last prompt token for the *final* value of the trap variable *v* on E4. D predicts chance, or a decoding of the greedy value 1. Post-hoc predicts the correct final value.
- Pre-CoT steering (Cox et al. 2026): D predicts that answers resist steering below budget but are steerable above it, where the default comes from priors.

**Competitor and random-init controls.**

- The same probes, aimed at F's variables, run on D items, and the reverse.
- Random-init models of the same architecture.

**Positive controls.**

- Small transformers (6–8 layers) trained from scratch on reference-implementation traces (n ≤ 12):
  - DPLL;
  - `DPLL-b` + Δ;
  - `WALK-k`;
  - `C-UC`.

  Pan et al. 2025 show that trace-trained models learn DPLL within the sizes they were trained on.
- The whole Phase 1 + Phase 2 pipeline must recover each one. Suppressing the toy DPLL model's backtrack direction must make the behavioural pipeline label it C.
- Shah et al. 2024 decode Sudoku candidate sets in a model trained on solver steps, a precedent.

**Models and why.**

- **gpt-oss-20b**, the first behavioural model. It is MoE with about 3.6B active parameters, so activations are affordable, and circuit-tracer has a CLT for it (report C).
- **Qwen3-14B:** thinking mode, with transcoders up to 14B (report C).
- **Optional methods check:** R1-Distill-Llama-8B, where a backtracking direction has already been published.
- **Cost control.** Long BE chains make activation work expensive. Cache only about 200 event-boundary positions × 8 layers per trace (about 10 MB per trace), not every token. Restrict to E4 items at n ≤ 20, whose BE traces have a median of about 7–9k tokens.

| ID | Model | Method | Prediction | Quantity reported | Null reading |
|----|-------|--------|------------|-------------------|--------------|
| M1 | gpt-oss-20b, Qwen3-14B | Probes for implied-unwritten literals and the conflict flag, with prefix-matched controls | Above control; tracks the formula, not the text | Selectivity (pp, with CI); prefix-pair accuracy | Selectivity CI includes 0 |
| M2 | Same | Suppress the backtracking direction on E4 | Weight moves from D to C on the trap arm only | Δπ_C(trap) vs random direction, with interval; control-arm Δ | Both arms degrade equally |
| M3 | Same | Pre-CoT probe and steering | Final *v* not decodable before the CoT | AUC with CI on the trap arm | AUC ≥ 0.85 (pre-committed) |
| M4 | Toy DPLL / WALK / C-UC | Full pipeline | Recovers the trained procedure and the planted mixture weights | Bias and interval width of the recovered π | Bias > 0.05 or coverage < 0.9 |

---

## 4. Build scope

S = shared infrastructure, which other verticals also need. V = specific to this vertical.

| # | Component | S/V | Person-days |
|---|-----------|-----|-------------|
| 1 | SAT core: random generator, matched-pair builder, solver wrappers (PySAT), content hashing | S | 3 |
| 2 | Instrumented DPLL (H, V, Δ, CHR/CBJ; node and work counters; event-schema traces), `BEAM-w`, `BACKDOOR-k`, `NOISY-DPLL`, `PERCEPTION` | S (C and B1 reuse it) | 4 |
| 3 | Local search: `WALK`, `MIN-CONFLICTS`, `SA` for SAT and colouring; `2OPT-k`; seeded Monte Carlo sampling | V / S | 3 |
| 4 | Covariates: solution enumeration, backbone, min-Hamming (RC2), MUS (MUSX), exact weak-UP and FLP backdoors (numba/Rust), WalkSAT difficulty, greedy success | S | 4 |
| 5 | Generators with acceptance filters and unit tests (§2.9): E3 backdoor selection and presentation relabelling; E4 SAT and colouring traps; E5 certificate pairs with decoys; E2 quadrant selection (+ q-hidden); E7 seeds (basin labelling, decoys, TSP 2-opt optima); isomorphism hashing and split checks | V | 10 |
| 6 | Colouring and TSP generators and exact solvers | S | 2 |
| 7 | Runner: best-effort configs per model; thinking-budget and forced-end caps; gpt-oss effort levels; prefill, cut, resume and edit; capped/LOOP flags | S (prefill parts are V) | 4 |
| 8 | Answer parsing and scoring (assignments, cores, colourings, tours, edge echo, UNKNOWN, PARTIAL), violation profiles | S | 2 |
| 9 | Trace coding: codebook, per-family segmenters, regex parser, state tracker, FA1–FA8, LLM-coder pipeline, synthetic-trace control | V (reusable) | 8 |
| 10 | Hand labelling: 2,400 segments × 2 coders, 64 full traces, adjudication, inter-rater agreement | V (annotators) | 24 annotator-days, not counted below |
| 11 | Analysis: censored token models, collapse fit, *b* fitting and CV, `NOISY-DPLL` likelihood, mixed models, McNemar/TOST, E6 classifier, E7/E8 metrics; one script per figure | V | 8 |
| 12 | Recovery tests with graded mixtures (60/30/10, feature-dependent): bias, interval width and coverage per weight, plus fake traces | S framework, V members | 4 |
| 13 | Dev batch and pilot on gpt-oss-20b, re-sizing, pre-registration write-up | V | 4 |
| | **Total** | | **≈ 62 person-days** (≈ 25 shared) + 24 annotator-days |

Phase 2, if triggered, adds about 25 person-days: activation caching at event positions, probes and controls, steering, toy-model training.

---

## 5. Compute budget

**How to read the table.**

- "# items" is per model, unless stated otherwise.
- The full study runs the 8 primary models.
- E8 runs 4 of them.
- **Dev batch rows** run **gpt-oss-20b (high) only**, with 1 sample, and touch every cell of that eval's design.
- Output tokens include thinking.
- The averages are best-effort estimates for items *near each model's budget line*. Hard items often run 15–30k. They are to be re-estimated after the dev batch.

| Eval ID | Domain | # items | Conditions (e.g. direct, CoT-1k, CoT-4k, CoT-16k) | Samples/item | Avg prompt tokens | Avg output tokens per condition | Needs activations? (Y/N) |
|---|---|---|---|---|---|---|---|
| E0 (pilot) | 3-SAT pairs, staircase n ∈ {10…60} | 100 | BE-32k | 1 | 2.0k | BE 18k | N |
| E0 dev | Same | 20 (5 levels × 2 pairs) | BE-32k | 1 | 2.0k | BE 18k | N |
| E1 | 3-SAT pairs, α = 4.26, 9 levels around *n\** | 540 (780 in pool) | BE-32k; CoT-8k; CoT-2k; direct (Qwen3 only) | 2 / 1 / 1 / 1 | 2.1k | BE 16k; 8k 7.3k; 2k 2.0k; direct 60 | N |
| E1 dev | Same | 30 (5 levels × 3 pairs) | BE-32k; CoT-8k; CoT-2k | 1 | 2.1k | BE 16k; 8k 7.3k; 2k 2.0k | N |
| E1-dens | 3-SAT, α ∈ {3.0…6.0} at *n\**_BE | 280 | BE-32k | 2 | 2.2k | BE 15k | N |
| E1-dens dev | Same | 35 (7 α × 5) | BE-32k | 1 | 2.2k | BE 15k | N |
| E2 | 3-SAT quadrants (all SAT) at n_Q | 400 (1,600 in pool) | BE-32k; CoT-8k | 2 / 1 | 2.0k | BE 14k; 8k 7.0k | N |
| E2 dev | Same | 32 (4 quadrants × 8) | BE-32k; CoT-8k | 1 | 2.0k | BE 14k; 8k 7.0k | N |
| E3 | 3-SAT, natural formulas selected on *k\** ∈ {2, 3, 4}, two presentations each | 360 (60 formulas × 3 *k\** × 2 presentations; 1,080 in pool) | BE-32k; CoT-8k; CoT-2k | 2 / 2 / 2 | 2.0k | BE 12k; 8k 6.8k; 2k 2.0k | N |
| E3 dev | Same | 30 (3 *k\** × 2 presentations × 5 formulas) | BE-32k; CoT-8k; CoT-2k | 1 | 2.0k | BE 12k; 8k 6.8k; 2k 2.0k | N |
| E4-SAT | 3-SAT trap pairs, d ∈ {2, 4} × t ∈ {1, 2} | 600 (300 pairs, 75 per cell) | BE-32k; CoT-8k; direct (Qwen3 only) | 2 / 1 / 1 | 1.3k | BE 9k; 8k 5.5k; direct 60 | N |
| E4-SAT dev | Same | 40 (4 cells × 5 pairs) | BE-32k; CoT-8k | 1 | 1.3k | BE 9k; 8k 5.5k | N |
| E4-COL | 3-colouring trap pairs | 300 (150 pairs) | BE-32k | 2 | 0.9k | BE 8k | N |
| E4-COL dev | Same | 20 (2 depths × 5 pairs) | BE-32k | 1 | 0.9k | BE 8k | N |
| E5 | 3-SAT certificate pairs, L factor | 400 (200 pairs) | BE-32k | 2 | 1.8k | BE 17k (UNSAT arm ≈ 23k, SAT arm ≈ 11k) | N |
| E5 dev | Same | 32 (2 L × 8 pairs) | BE-32k | 1 | 1.8k | BE 17k | N |
| E6-VER | Verification probes on the model's own wrong SAT answers | ≈ 1,500 | CoT-2k | 1 | 2.1k | 2k 1.5k | N |
| E6-VER dev | Same | 50 | CoT-2k | 1 | 2.1k | 2k 1.5k | N |
| E6-COL | 3-colouring near-miss + edge echo | 300 | BE-32k | 2 | 1.0k | BE 12k (+0.2k echo) | N |
| E6-COL dev | Same | 30 (2 sizes × colourable/not, ≈ 8 each) | BE-32k | 1 | 1.0k | BE 12k | N |
| E7-SAT | SAT seeds, 80 items × 6 conditions | 480 prompts | BE-32k; CoT-8k | 2 / 1 | 2.0k | BE 10k; 8k 6.0k | N |
| E7-SAT dev | Same | 48 prompts (8 items × 6) | BE-32k; CoT-8k | 1 | 2.0k | BE 10k; 8k 6.0k | N |
| E7-COL | Colouring seeds, 60 × 4 | 240 prompts | BE-32k | 2 | 1.0k | BE 7k | N |
| E7-COL dev | Same | 24 (6 × 4) | BE-32k | 1 | 1.0k | BE 7k | N |
| E7-TSP | TSP seeds, n 10–14, 60 × 4 | 240 prompts | BE-32k | 2 | 0.8k | BE 9k | N |
| E7-TSP dev | Same | 24 (6 × 4) | BE-32k | 1 | 0.8k | BE 9k | N |
| E8-TR | Cuts + forced answer (4 open models) | 300 traces × 9 cut points | Prefill prefix + forced answer | 2 | 9k (prefix-cached) | 80 | N |
| E8-TR dev | Same (gpt-oss-20b) | 20 traces × 9 | Same | 1 | 9k | 80 | N |
| E8-RES | Edit + resume (4 open models) | 200 traces × 3 edit conditions | BE-32k (remaining budget) | 2 | 10k (prefix-cached) | 10k | N |
| E8-RES dev | Same | 15 traces × 3 | Same | 1 | 10k | 10k | N |
| TC | Trace coding by LLM on ambiguous windows (Llama-3.3-70B coder) | ≈ 100k windows of 1.5k tokens (all models) | Coder, non-thinking | 1 | 2.5k | 0.3k | N |
| TC dev | Same | ≈ 300 windows (20 traces) | Same | 1 | 2.5k | 0.3k | N |
| P2-M1 (Phase 2) | Probes on E4/E2 BE traces | 1,500 traces per model (2 models) | Forward pass over existing traces | 1 | ≈ 9k (prompt + trace) | 0 (no generation) | Y |
| P2-M1b (Phase 2) | Prefix-matched formula-differing pairs | 400 pairs | Prefill + continue 512 | 2 | 6k | 0.5k | Y |
| P2-M2 (Phase 2) | Backtracking steering on E4 pairs | 300 pairs × 5 steering conditions | BE, capped at 16k for cost | 2 | 1.9k | 8k | Y |
| P2-M3 (Phase 2) | Pre-CoT probes (+ steering) | 2,000 probe prompts; 400 × 3 steering | Prompt only; BE (16k cap) for steering | 1 / 2 | 1.9k | 0 / 8k | Y |
| P2-M4 (Phase 2) | Toy transformers on DPLL/WALK/greedy traces | 4 toys × 200k training traces (n ≤ 12) | Train + eval | — | 0.6k | 1.5k (trace) | Y |

**Totals.**

| Scope | Output tokens | Prompt tokens | Notes |
|-------|---------------|---------------|-------|
| Per primary model, E0–E7 | ≈ 124 M | ≈ 31 M | E1 31 M, E2 14 M, E3 15 M, E4 19 M, E5 13.6 M, E6 9.6 M, E7 20 M, E0 1.8 M |
| 8 models, E0–E7 | ≈ 0.99 B | ≈ 250 M | Plus ≈ 8% for the 20% third-sample subset → ≈ 1.07 B |
| E8 (4 models) | ≈ 50 M | ≈ 240 M (mostly cached) | |
| TC | ≈ 30 M | ≈ 250 M | |
| **Phase 1 total** | **≈ 1.15 B** | ≈ 0.75 B | |
| Dev batch (gpt-oss-20b) | ≈ 6.5 M | ≈ 1.4 M | ≈ 2 H100-hours |

**GPU-hours.** These are planning assumptions (vLLM, H100-80GB, long-context decoding); they are to be calibrated on the dev batch.

| Model | GPUs | Assumed tok/s | H100-hours |
|-------|------|---------------|------------|
| gpt-oss-20b | 1 | ≈ 5k | ≈ 7 |
| gpt-oss-120b | 1 | ≈ 2.5k | ≈ 14 |
| Qwen3-14B | 1 | ≈ 2.5k | ≈ 14 |
| Qwen3-30B-A3B | 1–2 | ≈ 5k | ≈ 14 |
| Qwen3-32B | 2 | ≈ 2k | ≈ 35 |
| R1-Distill-Qwen-32B | 2 | ≈ 2k | ≈ 35 |
| Qwen3-235B-A22B-Thinking | 8 (FP8) | ≈ 3k | ≈ 95 |
| DeepSeek-R1 | 16 | ≈ 2.5k | ≈ 230 |

The sum is about 450 H100-hours. With ×2 for slower long-context decoding and reruns, plus E8 and TC, the planning figure is **about 1,000 H100-hours**. DeepSeek-R1 is half of that: drop it to the end of the queue, or serve it through a hosted endpoint for the same open weights.

**Expected truncation at 32k.** These are estimated shares of BE runs that hit the cap, for a strong D-like model. gpt-oss at high effort should sit at the low end; DeepSeek-R1 and Qwen3-Thinking at the high end. LOOP runs are counted separately.

| Eval / cell | % capped at 32k | Why |
|-------------|-----------------|-----|
| E1, n ≤ 0.7 *n\** | < 3% | Within budget |
| E1, 0.7–1.4 *n\** | 10–30% | Near the line |
| E1, ≥ 1.4 *n\** | 35–65% (UNSAT about 1.5× SAT) | Refutation needs the whole tree |
| E1-dens, α ≈ 4.26 | 20–35% | Peak *W* |
| E1-dens, α ≤ 3.5 | < 5% | Easy SAT |
| E1-dens, α ≥ 5.2 | 10–25% | UNSAT refutations |
| E2, high-*W* quadrants | 25–40% | By construction |
| E2, low-*W* quadrants | 3–10% | |
| E3, *k\** = 4 at BE | 20–45% | Node counts grow with *k\** |
| E3, *k\** ≤ 2 | < 5% | |
| E4 (both arms) | 2–6% | Items at about 0.6 *n\**; trap arm slightly higher |
| E5, UNSAT arm | 20–35% | CHR re-refutation across decoys |
| E5, SAT arm | 5–10% | |
| E6-COL, colourable | 5–10% | |
| E6-COL, uncolourable | 20–40% | |
| E7-SAT, decoy or random seed | 8–15% | |
| E7-SAT, near seed | < 5% | |
| E7-TSP | 5–10% | Exhaustive checking |

Capped runs are kept: censored for token models, and a separate stratum for answers (§2.5).

---

## 6. What would push the weights of D, F and H3 toward zero

Heuristics can be partly used, so this section states bounds, not verdicts. All quantities are pre-registered, per model at BE, from the mixture posterior (§2.5).

**D's weight is pushed toward zero** (π_DPLL + π_BEAM + π_BACKDOOR ≤ 0.1, upper 95%) if all of these hold:

1. **E4:** Δ̂ ≥ 0.15, with dead-end errors. That puts weight on C instead of the backtracking members.
2. **E1/E2:** the `NOISY-DPLL` posterior puts *b* at ∞ (β's 95% interval includes 0 and excludes 0.5), and the error mass sits in completed runs. That moves weight from `DPLL-b` to NE.
3. **E3:** s's 95% interval includes 0, at power > 0.95 for s = 0.5.
4. **E5:** valid-core sensitivity is no higher than `A-CORE`'s (about 1/3), even well below *n\**.

Partial outcomes are the expected case. They are reported as such, e.g. "π_DPLL = 0.4 (0.3–0.5) on above-*n\** errors, rising with budget with slope w = …".

**The trace channel can lower D's *process* weight without touching its answer weight.** Suppose E8 shows post-hoc traces (π_POST-HOC high; edits ignored). Then the procedure is "search-equivalent at the answer level, but not run in the visible chain of thought". R_m falls, and the case becomes a Phase 2 target.

**F's weight is pushed toward zero** (π_WALK + π_MIN-CONFLICTS + π_2OPT ≤ 0.1, upper 95%) if all of these hold:

1. **E6:** the LM0 share of infeasible answers is at the NE/PERCEPTION base rate, and the frustration LLR's interval includes 0.
2. **E7:** no seed slope, and decoy-proximal errors at the null rate. This bounds π_F ≤ 0.08.
3. **E8:** *V*(f) does not fall.
4. **E2:** the *F*_ref effect is null. This bounds π_F ≤ 0.15.
5. **E5:** false alarms do not depend on L. This bounds π_F ≤ 0.12, pooled.

**H3's weight is pushed toward zero if:**

- for models with π_DPLL ≥ 0.3, the posterior ratio b̂(BE) / b̂(2k) has a 95% interval that includes 1;
- **or** the budget feature's weight on π_DPLL in π_h(φ) has an interval that includes 0;
- **or** E3's s and E1's β (2k ↔ 8k) both have intervals that include 0, at adequate power;
- **or**, above *n\**_BE, ΔLL(`DPLL-b` + Δ : A) and ΔLL(`DPLL-b` + Δ : NE) both have intervals that include 0. This is DESIGN's H3 falsifier, restated as a likelihood gain.

**Non-monotone effects of the thinking budget** (Gema et al. 2025; Ghosal et al. 2025) are pre-registered as allowed on the 8k → 32k leg. They show up as a budget weight that changes sign at high budget. They count against H3 only if b̂ itself falls. FOUND-THEN-LOST traces are reported as a separate component.

---

## 7. Evidence-table row

To fill in as results arrive. Two rows, D and F.

| Family | Lift over baseline [CI]; ΔLL vs null and nearest competitor | Mixture weight π (95% CrI); feature slopes | Signatures matched | Trace share × R_m | Probe selectivity | Intervention vs competitor | Recovery (bias, width) | RASP-L length / class |
|---|---|---|---|---|---|---|---|---|
| D | +XX pp [XX, XX]; ΔLL X.X vs NE | 0.XX (0.XX–0.XX); budget slope X.X | X/7 (§2.3) | 0.XX (CT1–CT5) | Phase 2 | Phase 2 (M2) | bias ±0.0X, width 0.XX | ≈ 31 (provisional) / S |
| F | +XX pp [XX, XX]; ΔLL X.X vs NE | 0.XX (0.XX–0.XX) | X/7 | 0.XX (CT6–CT8) | Phase 2 | — | bias ±0.0X, width 0.XX | ≈ 20 / S |

---

## 8. Biggest rigour risks and open questions

**The three biggest risks.**

1. **D vs `NOISY-EXACT` vs implicit search is the weakest separation.** All three predict accuracy falling with size. The separation rests on budget interactions (β, s) and termination type. Those are valid only if:
   - forced caps act like real budgets, although a forced answer is not the model's own default;
   - the budget unit (work vs nodes) is right;
   - BE is not self-limited below 32k. If it is, the 8k → 32k leg says nothing.

   Mitigations: the nested `NOISY-DPLL` fit, the 2k ↔ 8k leg as primary, and graded-mixture recovery tests before any data. In the library's E4 LR table, `DPLL-b` and NE tie by design, so the separation must come from E1–E3. Residual risk: a model running noisy *truncated* search sits in the interior of the parameter space, and gets wide, overlapping intervals on π_DPLL and π_NE.
2. **Constructed items are off-distribution, and "trap" is defined only relative to our grid of rules.**
   - E3–E5 and E7 use planted or gadget structure. A model may detect it, or switch strategy (family I).
   - Acceptance filters guarantee the cell predictions only for the *pre-registered* branching and value rules. If the model's rule lies outside them, the cell does not test what it claims to.

   Mitigations: multi-rule acceptance, matched surface statistics, natural-item anchors (E1, E2), and trace checks of the model's actual order (CT2.1/2.2), with off-rule pairs analysed separately.
3. **Trace coding of long chains of thought may fail validation, and traces may be unfaithful.**
   - Free-form 10–30k-token traces differ a lot between families: gpt-oss's terse analysis channel vs R1's verbose style.
   - Phantom backtracks or post-hoc traces would make the CT tests uninterpretable.
   - E8 relies on off-policy prefills.

   Mitigations: the pre-registered κ/F1 gates, the R_m bands, answer-first combination rules, and synthetic-trace parser controls. If the gates fail, Phase 1 falls back to answer-only identification, which stays valid.

**Open questions.**

- Primary budget unit: *W* (clause visits) or *N* (nodes)? Pre-registered as *W*, with *N* secondary. Is that the right call?
- Should DeepSeek-R1 (half the compute) be kept, or replaced by a second R1-distill?
- E5 core format: does asking for a core change search behaviour? The pilot compares runs with and without the core field.
- Is the q-hidden tuning stable at n ≤ 42? It has to be measured on our generator.
- Should `SA` be dropped entirely? It is not identifiable from answers (§1.3).
- **A deferred-conflict construction for `BEAM-w`** (§2.7 E4, item 9). Without it, `BEAM-w` vs `DPLL-b` rests on item-specific failures.
- **E7 decoy depth:** no n = 12 decoy passes the SD rule. Measure the yield at n ≥ 20 before the main run.
- **E2 off-diagonal yield** is 2–3% per quadrant naturally. Decide between a large natural pool and flagged constructions.

**To verify before citing.**

- Report-level claims not yet re-checked: Hazra et al.'s trace details (backjumping, MOMS); Pan et al.'s step bound and venue; Gomes et al. 2000 (title-level only).
- Classic sources I did not fetch, and so do not cite here: Minton et al. 1992 (min-conflicts); Selman, Kautz & Cohen 1994 (WalkSAT noise); Kilby et al. 2005 (backbones and backdoors); the original Achlioptas–Jia–Moore 2-hiding paper (cited here only through Jia, Moore & Strain's own description of it).

---

## 9. References

Cited from the repo's literature reports (`docs/literature/`) unless marked *verified this session*.

- Achlioptas (2001). *Lower bounds for random 3-SAT via differential equations.* TCS. doi 10.1016/s0304-3975(01)00159-1 (report F).
- Alekhnovich, Borodin, Buresh-Oppenheim, Impagliazzo, Magen & Pitassi (2011). *Toward a Model for Backtracking and Dynamic Programming.* Computational Complexity 20 (report F).
- Bogdan, Macar, Nanda & Conmy (2025). *Thought Anchors.* arXiv 2506.19143 (report C).
- Chen et al. (2025). *Reasoning Models Don't Always Say What They Think.* arXiv 2505.05410 (report C).
- Cox, Kianersi & Garriga-Alonso (2026). *Post-Hoc Reasoning in Chain of Thought.* arXiv 2603.01437 (report C).
- Gema et al. (2025). *Inverse Scaling in Test-Time Compute.* TMLR. arXiv 2507.14417 (report A).
- Ghosal et al. (2025). *Does Thinking More always Help?* NeurIPS. arXiv 2506.04210 (report A).
- Gomes, Selman, Crato & Kautz (2000). Heavy-tailed phenomena in SAT/CSP. JAR. doi 10.1023/a:1006314320276 (report F, title-level).
- Hazra, Venturato, Zuidberg Dos Martires & De Raedt (2025). *Have LLMs Learned to Reason? A Characterization via 3-SAT Phase Transition.* arXiv 2504.03930 (report A).
- Hewitt & Liang (2019). *Designing and Interpreting Probes with Control Tasks.* arXiv 1909.03368 (report C).
- Heyman & Zylberberg (2025b). *Reasoning LLM Errors Arise from Hallucinating Critical Problem Features.* arXiv 2505.12151 (report A).
- Hoos & Stützle (2004). *Stochastic Local Search: Foundations and Applications.* Morgan Kaufmann (report F).
- **Jia, Moore & Strain (2005).** *Generating Hard Satisfiable Formulas by Hiding Solutions Deceptively.* arXiv cs/0503044. *Verified this session.* Per the abstract: naive planting is easy because literals point to the hidden assignment; hiding it together with its complement gives formulas that are hard for DPLL but solvable by WalkSAT in polynomial time; *q*-weighting removes the bias.
- Johnson, Papadimitriou & Yannakakis (1988). *How easy is local search?* JCSS (report F).
- Lanham et al. (2023). *Measuring Faithfulness in Chain-of-Thought Reasoning.* arXiv 2307.13702 (report C).
- **Muennighoff et al. (2025).** *s1: Simple test-time scaling.* arXiv 2501.19393. *Verified this session* (budget forcing).
- Pan, Ganesh, Abernethy, Esposo & Lee (2025). *Can Transformers Reason Logically? A Study in SAT Solving.* arXiv 2410.07432 (reports A, D).
- **Qin, Alvarez-Melis, Jelassi & Malach (2025).** *To Backtrack or Not to Backtrack: When Sequential Search Limits Model Reasoning.* COLM. arXiv 2504.07052. *Verified this session.*
- **Qwen Team (Yang et al.) (2025).** *Qwen3 Technical Report.* arXiv 2505.09388. *Verified this session* (thinking and non-thinking modes; thinking-budget mechanism).
- Sahoo, Jain, Chadha & Chaudhary (2026). *Linear Probes Detect Task Format, Not Reasoning Mode.* arXiv 2606.02907 (report C).
- Schäffer & Yannakakis (1991). *Simple Local Search Problems that are Hard to Solve.* SIAM J. Comput. (report F).
- Shah, Dikkala, Wang & Panigrahy (2024). *Causal Language Modeling Can Elicit Search and Reasoning Capabilities on Logic Puzzles.* arXiv 2409.10502 (report C).
- Sinha, Arun, Goel, Staab & Geiping (2025). *The Illusion of Diminishing Returns.* arXiv 2509.09677 (report A).
- Sutter, Minder, Hofmann & Pimentel (2025). *The Non-Linear Representation Dilemma.* arXiv 2507.08802 (report C).
- Venhoff, Arcuschin, Torr, Conmy & Nanda (2025). *Understanding Reasoning in Thinking Language Models via Steering Vectors.* arXiv 2506.18167 (report C).
- Verma (2026). *Solver-Hard Is Not Model-Hard.* arXiv 2607.17047 (report A).
- Ward, Lin, Venhoff & Nanda (2025). *Reasoning-Finetuning Repurposes Latent Representations in Base Models.* arXiv 2507.12638 (report C).
- Williams, Gomes & Selman (2003). *Backdoors To Typical Case Complexity.* IJCAI (report A).
- Yang et al. (2025). *NPPC.* arXiv 2504.11239 (report A).
- Zhang, Chen & Chen (2026). *Satisfiability Solving with LLMs: A Matched-Pair Evaluation of Reasoning Capability.* FSE. arXiv 2605.28602 (report A).
