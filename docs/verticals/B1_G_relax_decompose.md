# Vertical: B1 Relax and G Decompose / DP

*One file for family B1 (drop constraints, solve the rest exactly) and family G (split into parts, solve the parts, track or ignore the links). They share a file because G's heuristic member, `IGNORE-CROSSLINKS`, is a B1 relaxation with a structural selector (report F), and because both predict the same kind of error: an answer that is sound or feasible-looking except for exactly what was dropped.*

- **Status:** designed (no pilot data). Every number below is a design target, to be re-estimated after the pilot (DESIGN §8: size the main study on pilot effects).
- **Owner:** [TODO]
- **Members:** B1 `UP-k`, `RES-w`, `PREMISE-SUBSET`, `2SAT-CORE`, `MST-TOUR`, `DROP-CONSTRAINT`; G `DP-EXACT`, `IGNORE-CROSSLINKS`. Variants proposed here are marked `*`.
- **Scope (Phase 1 is behavioural only).**
  - **Primary condition:** open-weight reasoning models at best effort, i.e. high reasoning effort and thinking budgets up to 32k tokens.
    - The first model is **gpt-oss-20b at high effort**.
    - Then gpt-oss-120b (high), Qwen3-14B / 32B / 30B-A3B in thinking mode, Qwen3-235B-A22B-Thinking, DeepSeek-R1, and the R1-Distill-Qwen-14B / 32B models.
    - No models under 14B.
  - **Secondary / diagnostic:** direct answers (non-thinking mode or low effort), and the thinking budget as an experimental factor (2k / 8k / 32k) on subsets.
  - **Phase 2 (interpretability)** runs only if the behavioural evidence warrants it (§3).
- **Evals:** E1–E6. For each eval we give:
  - the hypothesis;
  - the counterfactual cells, with every relevant family's predicted **answer and trace**;
  - confound controls and the generator spec;
  - metric, criteria, power and threats.

  §2.4 sets out the shared trace-evidence framework: the coding scheme, faithfulness tests, and how trace and answer evidence combine.
- **Companion files:**
  - `docs/verticals/B1_G_relax_decompose_questions.md`: worked counterfactual item sets, with ground truths and predictions computed by script;
  - `data/examples/B1_G_relax_decompose.jsonl`: the same items, machine-readable.

**Contents.** §0 Conventions · §1 The class · §2 Behavioural evidence (Phase 1) · §3 Mechanistic evidence (Phase 2, only if behavioural evidence) · §4 Evidence-table row · §5 Build scope · §6 Compute budget · §7 What would falsify these families · §8 Open questions · Sources

---

## 0. Conventions used throughout

### 0.1 Answer formats

All primary answers are machine-checkable (DESIGN §5.4).

| Domain | Instance as rendered | Answer | Ground truth g |
|---|---|---|---|
| Entailment, single query | Premises P₁…P_N in presentation order, then a query atom q | Final line `ANSWER: TRUE` / `FALSE` / `UNDETERMINED`, where UNDETERMINED means "the premises do not settle it" | z3: P ⊨ q gives TRUE; P ⊨ ¬q gives FALSE; otherwise UNDETERMINED. P is always satisfiable. |
| Entailment, list | As above, plus the vocabulary V listed in a fixed random order | JSON list of literals `"X"` / `"not X"` over V that must hold, excluding restated premises | The set of entailed literals that are not premises |
| SAT / CSP | Variables introduced in a list, then constraints ("at least one of: A is on, B is off, C is on") | JSON `{var: true/false}` or `"IMPOSSIBLE"` | PySAT |
| Coloring | Vertices introduced in a list, then conflicts, then k slots | JSON `{vertex: slot in 1..k}` or `"IMPOSSIBLE"` | PySAT |
| Knapsack | Items with weight and value, and a capacity W | JSON list of item ids | DP |
| Routing | Cities and a distance table | JSON list of cities, starting at the first-listed city | OR-Tools (small n) |

### 0.2 Clause forms

E1 and E3 use only premise forms that are single clauses. So "premise" and "clause" coincide, and CNF conversion adds no variables:

| Surface form | Clause | Direction tag |
|---|---|---|
| `A.` / `A is not the case.` | (A) / (¬A) | fact |
| `If A, then B.` | (¬A ∨ B) | head B |
| `If A, then not B.` | (¬A ∨ ¬B) | head ¬B |
| `If A and B, then C.` | (¬A ∨ ¬B ∨ C) | head C |
| `A or B (or both).` | (A ∨ B) | none |
| `Either A is not the case, or B is.` | (¬A ∨ B) | none (the disjunctive phrasing of a conditional) |

The direction tag records the surface form. It is used by `UP-k/R` (§1.4).

E2 also uses multi-clause forms, such as exclusive "or else" and biconditionals. There a premise is the set of its clauses.

### 0.3 Atoms and canonical order

- **Atoms** are rendered as "the ⟨colour⟩ ⟨object⟩ is ⟨state⟩", drawn from closed pools. The content is kept neutral, because world-knowledge heads contaminate logic circuits (belief bias; Kim et al. 2025). Each atom maps to one string per item.
- **Canonical order (LEX).**
  - Atoms, variables and vertices are ordered by first introduction.
  - Colours are ordered 1 < … < k, and False < True.
  - Items keep their listed order.
- **`EXACT_LEX(I)`** is the first solution of instance I in lexicographic order of the value vector under LEX. It is computed by complete DFS with LEX value order, and returns `None` if I is infeasible.

Every member below is deterministic given LEX.

### 0.4 Pair types

- A **Type-H pair** (x, x′) has h(x) ≠ h(x′) but g(x) = g(x′). It isolates h's *sensitivity*.
- A **Type-G pair** has g(x) ≠ g(x′) but h(x) = h(x′). It isolates h's *blindness*.

Every eval below is built from such pairs, or from 2×2 designs made of them.

### 0.5 Competitors referenced

These members are owned by other verticals. We only need their reference implementations to compute predictions. `*` marks a competitor proposed here.

- **A:**
  - `NONE` (always UNDETERMINED);
  - `FREQ` / `ATMOSPHERE` (answer from q's surface polarity or frequency);
  - `DENSITY` (feasible iff density is below a threshold);
  - `CYCLIC`\* (in intro order, vertex i gets colour ((i−1) mod k)+1).
- **B4:**
  - `FIRST`, `BICONDITIONAL`, `CLOSED-WORLD`;
  - `MM`, with a model-count cap c;
  - `ETR` (PyETR);
  - `DROP-CONJUNCT`\*: read "if A and B then C" as "if A then C". This strengthens the premise, so it is a restriction and errs by commission.
  - `ADD-CONSTRAINT`.
- **C:**
  - `FIRST-FIT-cap` and `DSATUR-cap`, with k colours. At a stuck vertex they take the colour with fewest conflicts, ties going to the smaller colour.
  - `ONLINE-STATE` (C4): premise-at-a-time, storing derived literals only.
- **D:**
  - `DPLL-b`;
  - `BC-b`\*: depth-first backward chaining from q without memoisation, with node budget b. It answers UNDETERMINED when the budget is exhausted.
  - `FC-budget-b`\*: sequential forward chaining, one derived literal per step in BFS-then-LEX order, stopping after b steps.
- **E:** `WP-t` (hard warning propagation); `BP-t` (t rounds of BP, then a threshold τ = 0.8 on the marginal).
- **F:** `MIN-CONFLICTS-k` (random initial assignment, then k repair steps).
- **H:** `SAMPLE-m` (sample m uniform models of P; conclude q if it holds in all m).
- **Nuisance:**
  - `NOISY-EXACT`: exact derivation, where each rule application is independently omitted with probability ε_o or misapplied with probability ε_c.
  - `PERCEPTION-NOISE`: each constraint is lost independently with probability ρ, optionally rising with list position.

---

## 1. The class

### 1.1 Defining idea

**B1.** h(x) = S(R(x)). R deletes constraints (clauses, edges, premises, or inference rules), and S solves the relaxed instance exactly, or with a declared solver. Entailment is monotone, and the solutions of R(x) include all solutions of x. Two consequences follow.

- **In entailment, h never gives a determinate answer that contradicts g.** It errs only by answering UNDETERMINED when g is determinate, i.e. by **omission**. It is an *errorless heuristic* in Bogdanov & Trevisan's sense (report F), with UNDETERMINED playing the role of ⊥.
- **In search, h never answers IMPOSSIBLE wrongly.** It claims feasibility whenever R(x) is feasible, so it is biased toward SAT. Its answers satisfy every retained constraint and violate only deleted ones. This is Pearl's (1983) relaxation, read as an error signature, as report F suggests.

**G.** Split x into parts, solve the parts, combine.

- `DP-EXACT` tracks every interaction, so its outputs equal g.
- `IGNORE-CROSSLINKS` drops the constraints between parts and solves each part independently, with its own canonical labels. It is the B1 member whose selector is "constraints that cross a part boundary".

### 1.2 Taxonomy position

- **Pearl's simplified-model calculus** (report F, Theory 1): B1 is relaxation. B4, restriction, is the direct contrast: it errs by commission. B5 is the probabilistic model.
- **Paradigm templates** (Theory 2):
  - `UP-k` is the hard-message member of LOCAL(t), and coincides with E's `WP-t`.
  - Truncated proof search (`BC-b`) is a D member.
  - G sits beside D in report F's tree. Used as a heuristic, it reduces to B1.

### 1.3 Members by problem model

| Member | Entailment | SAT / CSP | Coloring | Knapsack | Routing / scheduling | Abduction | Reference implementation |
|---|---|---|---|---|---|---|---|
| `UP-k` (with variants `/R`\*, `-PASS-p`\*, `-REFUTE`\*) | **Primary** (E1–E3) | Applies only with given unit clauses (configuration items), or as an UNSAT detector. Vacuous on pure random 3-SAT, which has no unit clauses. | Only as forced-colour propagation on precoloured instances. Not used. | n/a | n/a | As the consistency check inside explanation search (not budgeted) | `heuristics/b1_relax/up.py` |
| `RES-w` | **Primary** (E2 width ladder) | UNSAT detector: answers IMPOSSIBLE iff a width-w refutation exists (E4 decision analysis) | n/a (only through a CNF encoding) | n/a | n/a | n/a | `heuristics/b1_relax/res.py` |
| `PREMISE-SUBSET` | **Primary** (E3) | Same object as `DROP-CONSTRAINT`, since clauses are the premises. Merged. | Same as `DROP-CONSTRAINT`. Merged. | n/a (a single capacity constraint) | n/a | Explain only some observations (not budgeted) | `heuristics/b1_relax/premise_subset.py` |
| `2SAT-CORE` | Same as `PS(SHORT, m=2)`. Merged. | Mixed-width (2+p)-SAT only (E4). On pure 3-SAT it degenerates to "SAT, all False", an A1 constant. | n/a (2-colouring is itself 2-SAT) | n/a | n/a | n/a | `heuristics/b1_relax/two_sat_core.py` |
| `MST-TOUR` | n/a | n/a | n/a | n/a | Routing only (an extension of E4, not budgeted) | n/a | `heuristics/b1_relax/mst_tour.py` |
| `DROP-CONSTRAINT` | = `PREMISE-SUBSET` | **Primary** (E4) | **Primary** (E4) | n/a | Scheduling: drop precedence, time-window or resource constraints (extension) | n/a | `heuristics/b1_relax/drop.py` |
| `DP-EXACT` (with `DP-LIST`\*, `DP-ROUND`\*) | n/a | Tree-decomposition DP is exact, so it is behaviourally identical to g | Same | **Primary** (E6) | Weighted interval scheduling (exact) | n/a | `heuristics/g_decompose/dp.py` |
| `IGNORE-CROSSLINKS` (with `-TEXT`\*, `-GRAPH`\*, `-ALIGN`\*) | **Primary** (E5 header-move pairs) | **Primary** (E5) | **Primary** (E5) | n/a | Cluster-first, route-second (extension) | n/a | `heuristics/g_decompose/ignore_crosslinks.py` |

### 1.4 Definitions

All functions are deterministic.

- Clauses are frozensets of signed integer literals.
- `A` is a partial assignment, mapping variables to bools.
- `presentation` is the list of premises in rendered order.

**`UP-k` (parallel / Jacobi rounds), with the variant `UP-k/R`\*.**
- R ⊆ {MP, MT, DS} is the set of firing types allowed:
  - MP: derive the head when the rest of the clause is falsified;
  - MT: derive the negation of a body literal when the head and the other body literals are known;
  - DS: fire an untagged disjunction.
- `UP-k` = `UP-k/{MP, MT, DS}`, i.e. plain clausal unit propagation.
- `FC-k`\* = `UP-k/{MP}`: forward chaining along rules as written.

```
def UP(clauses, k=inf, R={MP,MT,DS}):
    A, depth = {}, {}
    for C in clauses:                       # round 0 = facts
        if len(C) == 1: A[var(l)] = sign(l); depth[var(l)] = 0      # items are consistent: no clash
    for r in 1..k:
        new = {}
        for C in clauses:                   # reads only round r-1 state, so order-invariant
            if satisfied(C, A): continue
            open_ = [l for l in C if var(l) not in A]
            if len(open_) == 0: return CONFLICT
            if len(open_) == 1 and firing_type(C, open_[0]) in R:
                new.setdefault(var(open_[0]), set()).add(sign(open_[0]))
        if not new: break
        if any(len(s) == 2 for s in new.values()): return CONFLICT
        for v, s in new.items(): A[v] = s.pop(); depth[v] = r
    return A, depth
answer(q) = TRUE if A[q] is True, FALSE if A[q] is False, else UNDETERMINED
list answer = {literal(v, A[v]) : depth[v] >= 1}
```

**`UP-PASS-p`\*: Gauss–Seidel passes in presentation order.**
- It uses the same firing rule as `UP`, but scans `presentation` and updates A immediately.
- It makes p passes.
- In proof order one pass derives everything. In reverse proof order, deriving a depth-d literal needs d + 1 passes.

**`UP-REFUTE-k`\*: the reductio variant.**
- Run `UP(P ∪ {¬q}, k)`. A conflict means TRUE.
- Otherwise run `UP(P ∪ {q}, k)`. A conflict means FALSE.
- Otherwise answer UNDETERMINED.
- On a chain, propagation meets in the middle, so it mimics `UP-2k`.

**`RES-w,k`: width-bounded forward resolution.**
- Unit resolution is always allowed, so `RES-0,∞` = `UP-∞`.
- The cost is n^O(w). This is Ben-Sasson & Wigderson's width-based search.

```
def RES(clauses, w, k=inf):
    S = set(clauses)
    for r in 1..k:
        new = set()
        for C1, C2 in pairs(S) clashing on exactly one variable x:
            Rv = (C1 - {x}) | (C2 - {-x})
            if tautology(Rv): continue
            if (len(Rv) <= w or min(len(C1), len(C2)) == 1) and not subsumed(Rv, S | new): new.add(Rv)
        if not new: break
        S |= new
    return S
answer(q) = TRUE if {q} in S, FALSE if {-q} in S, else UNDETERMINED
```

Examples:
- `RES-2` derives the conclusion of a 2-way dilemma: (A∨B), (¬A∨C) ⊢ (B∨C), then (B∨C), (¬B∨C) ⊢ (C).
- An n-way dilemma needs w = n.
- On fan-in-1 chains, `RES-2` composes implications by path doubling, so it needs about log₂ d + 1 rounds. AND-rules give width-3 resolvents, so `RES-2` cannot shortcut them.

**`PREMISE-SUBSET(sel, j) ∘ S`** (`PS` for short).
- S defaults to `UP-∞`; `UP-k` and `EXACT` are variants.
- The answer is S's answer on the selected premises P′ = sel(P, q, j). It is sound because P′ ⊆ P.

| Selector | P′ | Ties |
|---|---|---|
| `RECENT` | The last j premises | — |
| `FIRST` | The first j premises | — |
| `SHORT(m)` | Premises with ≤ m literals | — |
| `TYPE(T)` | Drop every premise of surface type T ∈ {disjunction, AND-rule, negated fact} | — |
| `OVERLAP(j)` | The top j by the number of shared content lemmas with the query sentence | Earlier position first |
| `RADIUS(r)` | Premises within r premise-hops of q in the premise–atom graph | — |

**`2SAT-CORE` (SAT).**

```
F2 = [C for C in F if len(C) <= 2]
if not satisfiable_2sat(F2): return "IMPOSSIBLE"
A = {}
for v in LEX order of vars(F2):              # LEX-least model of F2, in polynomial time
    A[v] = False if satisfiable_2sat(F2 ∪ units(A) ∪ {¬v}) else True
for v not in vars(F2): A[v] = False
return A                                     # can violate only clauses of width >= 3
```

**`DROP-CONSTRAINT(sel, m) ∘ S`** (`DROP`; coloring and SAT).
- D = sel(I, m), and the relaxed instance is I′ = I ∖ D.
- The answer is S(I′) if it is feasible, else `IMPOSSIBLE`. S defaults to `EXACT_LEX`; `FIRST-FIT` and `DSATUR` are declared variants.

| Selector | Domain | Constraints dropped (D) |
|---|---|---|
| `LAST` / `FIRST` | Coloring and SAT | The last / first m constraints in list order |
| `LONG` | Coloring | The m edges with the largest \|intro(u) − intro(v)\|; ties go to the later-listed edge |
| `CROSS` | Coloring | Edges between rendered paragraphs |
| `ADDENDUM` | Coloring | Constraints in a trailing "Also, …" sentence |
| `WIDE` | SAT | Clauses of width ≥ 3. With S = 2-SAT, this is `2SAT-CORE`. |
| `NEG` | SAT | All-negative clauses |
| `RARE` | SAT | Clauses containing the least frequent variable |

**`IGNORE-CROSSLINKS(decomp, S, align)`** (`IC`).

```
parts = decomp(I)   # TEXT: rendered paragraphs/sections; GRAPH: planted clusters
sol = {}
for part in parts (intro order):
    sub = I restricted to part; drop every constraint touching two parts
    s = S(sub) with labels canonicalised per part (first vertex of a part gets colour 1; LEX-least solution)
    if s is None: return "IMPOSSIBLE"
    sol |= s
if align: sol = relabel each later part by the colour permutation / alternative part solution
               that minimises cross-violations (LEX tie-break)            # IC-ALIGN*
return sol
```

In entailment, `IC-TEXT` runs `UP-k` inside each section, and derived literals are not exported across sections. The variant `IC-FACTS`\* exports given facts only.

**`MST-TOUR`.**
- Build a Prim MST from the first-listed city; ties go by (distance, index).
- Take the preorder DFS, visiting children in order of (distance from parent, index), and append the root.
- `MST-WALK`\* is the full Euler walk without shortcuts. It is infeasible as a tour: it repeats cities at MST branch vertices.

**`DP-EXACT` / `DP-LIST`\* / `DP-ROUND(δ)`\* (knapsack).**

```
L = {0: (0, ())}                                   # weight -> (value, chosen ids); LEX tie-break
for item i in listed order:
    L = pareto_prune(L ∪ {w+wi: (v+vi, S+(i,)) for w,(v,S) in L if w+wi <= W})
return argmax value (ties: smaller weight, then LEX ids)
cost(DP-LIST) = Σ_i |L after item i|               # process prediction
DP-ROUND(δ): run on ⌊wi/δ⌋·δ                        # relaxation: overshoot ≤ Σ (wi mod δ)
```

### 1.5 Declared equivalences: what answers cannot separate

1. **`UP-k` ≡ `WP-t` (E) with t = k.** These are the same function on our items. They get one zoo entry, cross-listed under B1 and E.
2. **`UP-k` ≡ `BP-t` on determined Horn items.** Hard evidence propagates as hard messages. They differ only on undetermined items whose thresholded marginal is high (E2, cell T5).
3. **On single-query chains, `UP-k` ≡ `BC-k` ≡ `PS(RADIUS, k)` in answers.** They are separated by:
   - the cone shape (E1);
   - the list format;
   - putting the query first rather than last (E3-Q);
   - **traces**: forward chaining asserts literals that are not ancestors of q, while `BC` states goals first.
4. **`UP-REFUTE-k` ≈ `UP-2k` on single-query chains.** Separated by the list format and by traces ("suppose not q").
5. **`DROP(sel)∘EXACT_LEX` and `DROP(sel)∘FIRST-FIT` coincide** whenever `FIRST-FIT` succeeds on I′. The signature "violations ⊆ D" identifies the selector, not the solver.
6. **`DP-EXACT` outputs equal g.** Only process evidence (E6: trace cost and the states written) or `DP-ROUND` can identify it.
7. **`DROP(LAST)` vs `PERCEPTION-NOISE` with a recency gradient.** They put the same mean on where violations fall. They are separated by:
   - cross-sample consistency;
   - an echo call;
   - the pendant-at-end manipulation;
   - traces: whether the dropped constraint is ever mentioned.
8. **`IC` ≡ `DROP(CROSS)` with per-part canonical labelling.**
9. **`FC-k` and `PS(TYPE: disjunction)` coincide on E3-O items.** Separated by E2-T6 (DS items) and by traces (whether the disjunction is quoted).

### 1.6 Expressibility

The depth classes matter for the diagnostic direct-answer condition, and for the budget factor.

| Member | Depth class | Argument |
|---|---|---|
| `UP-k`, fixed k | const | k rounds of local clause–literal updates. LOCAL = GNN (Sato et al. 2019). §1.7 gives about 2 attention layers per round. |
| `UP` to fixpoint | seq | Unit resolution and Horn unit resolution are P-complete (Greenlaw–Hoover–Ruzzo compendium, via report F) |
| `UP` on fan-in-1 chains | polylog in principle | Derivability is reachability. Parallel path doubling: Saparov et al. 2025 (reachable-set expansion); Ye et al. 2025 (diameter 3^L with L layers). So E1's fan-in factor is a depth-class contrast. |
| `RES-w,k` | const for fixed w, k; seq at fixpoint | It contains UP. Cost n^O(w) (Ben-Sasson & Wigderson). |
| `PS(sel)∘S` | Selector const; overall that of S | Positions, counts and lexical overlaps |
| `2SAT-CORE` | polylog | 2-SAT is NL-complete (a standard result; citation to add) |
| `DROP(sel)∘S` | Selector const; overall that of S | — |
| `MST-TOUR` | polylog (provisional) | Borůvka needs ≤ log n phases, plus Euler-tour preorder by prefix sums. This is our argument; report F lists "MST ∈ NC" as unverified. |
| `DP-EXACT` | seq (n stages, as executed) | Its output is g |
| `IC` | Decomposition const (paragraph ids) or polylog (components); solving that of S on each part | — |

### 1.7 RASP-L sketch (pre-register before any data)

The input is clause-tokenised CNF in the bare rendering, e.g. `[C] -a b [C] -b -c d [C] a ... [Q] d`. The sketch is RASP-style; translate it to the project's canonical dialect (report D notes that Tracr's RASP is not RASP-L).

```
clause_id   = numerical(cumsum(tok == "[C]"))                    # 1 line, 1 attn
same_clause = select(clause_id, clause_id, ==)                   # 1
same_var    = select(var(tok), var(tok), ==)                     # 1
clause_len  = selector_width(same_clause & is_lit)               # 1 line, 1 attn
val         = aggregate(same_var & is_unit_lit, sign)            # 1 line, 1 attn   (round 0)
# --- one round (unrolled k times; ALTA: loop body) ---
lit_false = is_lit & (val == -sign);  lit_true = is_lit & (val == sign)        # 2 lines, MLP
n_false   = selector_width(same_clause & lit_false)                            # 1 line, attn
sat       = aggregate(same_clause & lit_true, 1) > 0                           # 1 line, same layer
fire      = is_lit & ~sat & (val == 0) & (n_false == clause_len - 1) & dir_ok  # 1 line, MLP
val       = val + aggregate(same_var & fire, sign)                             # 1 line, attn
readout   = aggregate(select(var, q_var, ==), val)                             # 1 line, attn
```

**Lengths.**

| Program | Lines | Attention depth | ALTA |
|---|---|---|---|
| `UP-k` | ≈ 6k + 7 | ≈ 2k + 3 | A 6-rule loop body run k times |
| `FC-k` (`dir_ok` = head tag) | +1 | +0 | — |
| `PS(RECENT, j)` | +3 (premise index, count, window mask) | +1 | — |
| `IC(TEXT)` | +2 (section id conjoined into the selectors) | +0 | — |
| `DROP(LAST)` | +2 | +1 | Plus the solver |
| `RES-2` path doubling on chains | ≈ 3 per round, ⌈log₂ d⌉ rounds | — | — |
| `DP-LIST` | No constant-depth program | — | A loop with set-valued state of size \|L\| |

**Pre-registered prior for the diagnostic direct-answer condition.** One round costs about 2 layers, and only about half the layers compose (Csordás et al. 2025). So k*_direct ≤ L/4. For our minimum sizes: Qwen3-14B (L = 40) gives ≤ 10, and Qwen3-32B (L = 64) gives ≤ 16. These are upper bounds; expect less.

Qwen3-14B and Qwen3-32B have the same width (5120) but 40 vs 64 layers (checked against the HF configs). This gives a natural depth contrast: if the forward pass is layer-limited, k*_direct(32B) > k*_direct(14B).

---

## 2. Behavioural evidence (Phase 1)

### 2.0 Conditions and what "best effort" changes

**Primary condition (`BE-32k`).**
- Reasoning models get high effort and a 32k-token thinking cap:
  - gpt-oss: `reasoning_effort=high`;
  - Qwen3: thinking mode;
  - R1 and the distills: native.
- Sampling follows each model card's recommended settings. Every run logs the thinking tokens actually used.
- **Truncation policy.** A run that hits 32k gets the end-of-thinking delimiter and `ANSWER:` appended, to force an answer. It is analysed as **censored** (DESIGN §5.11). The forced answer is scored, but kept out of the main fits.

**Secondary conditions.**
- `DIRECT` (diagnostic): non-thinking mode, or the lowest effort setting, with "answer immediately". For always-thinking models (R1, the distills), the thinking block is forced empty. This is flagged as possibly off-distribution.
- `BUDGET` (the experimental factor): thinking caps of {2k, 8k, 32k} on designated subsets, using budget forcing at the cap.

**Why the sizes are large.** At best effort, Horn propagation (in P) on small items will be at ceiling. So:
- E1 and E3 scale N and d until the trace budget binds;
- E2's centre of gravity moves to the NP-hard part of entailment, **case analysis** (the case-split ladder);
- E4–E6 use instances large enough that exhaustive checking does not fit in 32k tokens for a meaningful share of items.

Each eval reports its expected truncation share (§6).

### 2.1 Predicted error signature

**Entailment: omission only.**
- Wrong answers are UNDETERMINED. Under the known aversion to "nothing follows" (Eisape et al. 2024; Bertolazzi et al. 2024), they may instead be **chance-polarity guesses**. Either way they fall on items that need more than the member allows: depth k, width w, rule types R, or the selected premises.
- They are never systematically wrong determinate answers.
- At best effort, `UP-k` should be near fixpoint (k large). The B1 prediction then becomes **"propagation-complete, case-split-incomplete"**: everything derivable by UP or low-width resolution is found, and conclusions that need case analysis are omitted.

**Search.**
- Claims feasibility on infeasible items. This SAT bias is consistent with models over-predicting SAT (Zhang, Chen & Chen 2026).
- Answers violate only constraints of the dropped type, and satisfy every retained constraint.
- Never a false IMPOSSIBLE.
- On the optimisation version: too few colours plus violations. This is the opposite of greedy, which uses too many colours and stays feasible.

**G.** `IC` errs exactly when the canonical per-part solutions clash on cross-links, and never on intra-part constraints.

**Hardness axis.**
- `UP-k` breaks at derivation depth, independent of n and of cone size.
- `RES-w` breaks at derivation width. Note that Verma (2026) finds no proof-hard vs proof-easy gap at matched density: prior evidence against resolution width driving errors in those models.
- `DROP` breaks where the dropped constraint is critical.
- On pure random 3-SAT, `UP-k` and `2SAT-CORE` are vacuous, and B1 is indistinguishable from `ALWAYS-SAT`. B1's SAT evidence must therefore come from E4–E5 items.

### 2.2 Nearest competitors, and which items separate them

| Competitor | Where it collides with B1/G | Separated by |
|---|---|---|
| `NOISY-EXACT` (omission slips) | Also produces omissions | Depth × size (E1): `UP-k` depends on d, `NOISY` on cone size s. Cross-sample consistency. Traces: slips skip a cone literal mid-derivation, while `UP-k` stops at a round boundary. |
| D: `BC-b`, `FC-budget-b`, `DPLL-b` | Sound and budgeted, like B1 | Cone shape and fan-out (E1); the case-split ladder (E2, where `DPLL-b` does case analysis and `UP`/`RES-w` don't); stuck locations (E4). Traces: goals vs assertions; "Case 1 / Case 2". |
| E: `BP-t`, `WP-t` | `WP-t` is identical to `UP-t` | Probability ladder at g = U (E2-T5), where `BP` and `SAMPLE` commit and B1 stays flat |
| B4 restrictions | Opposite error sign | Catch siblings (E1); E2-T3/T4 commission cells; false IMPOSSIBLE on feasible siblings (E4) |
| A cues | Can mimic anything at the aggregate | Surface-matched siblings; chance-polarity analysis; density-matched cells |
| C greedy / online | Order effects; stuck vertices | Proof order (E3-P); vertex vs constraint order, crossed (E4); sequential clusters (E5) |
| H `SAMPLE-m` | Commission on probable conclusions | Depth-invariance on determined items (E1); probability ladder (E2-T5) |
| F local search | Near-miss infeasible answers | Violated-constraint identity and consistency (E4); the BD cell (E5) |

**Generic recipe.** Every generator over-produces candidates, runs the whole zoo (this vertical's members plus the competitors in §0.5), and keeps the items or pairs that realise the designated prediction pattern. This uses the shared minimal-edit counterfactual search (§5).

### 2.3 Manipulation signatures

| Manipulation | Predicted change under B1/G | Under the nearest competitor |
|---|---|---|
| Premise / constraint order reversed | `UP-k`, `RES-w`, `DROP(LONG)`, `IC-GRAPH`: no change (order-invariant). `PS(RECENT/FIRST)`, `DROP(LAST/FIRST)`, `UP-PASS`: change, computable per item. | C4 / ETR: order-sensitive, and can flip to commission. C1 `FIRST-FIT`: changes with vertex order, not with edge order. |
| Re-themed / renamed | No change for every member (structure only), unless re-theming changes the section structure (`IC-TEXT`) | A3 `TEXTBOOK-TRANSFER`: no change. Content effects (Kim et al. 2025): a confound, not a heuristic. |
| Rule inverted (coloring "must share a slot"; SAT "at most one of") | Computed on the inverted instance; still sound, still omission or dropped-type errors | A3: errors ↑ (answers the uninverted problem) |
| Irrelevant constraint added | `UP` / `RES`: no change. `PS(RECENT)`: ↓ if appended, no change if prepended. **`DROP(LAST)`: an appended irrelevant constraint absorbs the drop, so errors ↓ on critical items** (a unique prediction). | A `DENSITY`: the same for appended and prepended. B4: more commission. |
| Size / density ↑ at fixed derivation depth | `UP-k`: no change. `PS`: ↓. `DROP`: more violations. Relaxation keeps SAT-claims high past the threshold. | `NOISY-EXACT`: smooth ↓. `FC-budget`: ↓ in proportion to the derivable literals. |
| Thinking budget ↑ (2k → 8k → 32k) | k ↑, with k*(B) ≈ B / τ_step (τ_step measured from traces); w ↑ only if the model case-splits; j ↑ for `PS` | D: b ↑ in the same direction. Separated by *what* grows: rounds (`UP`), case branches (`DPLL`), or derivation steps (`FC`). |

### 2.4 Trace evidence: hypotheses, coding, faithfulness, combination (shared by E1–E6)

**Pre-registered trace signature of each member.** "Asserted" means the trace states a literal or value as established.

| Member | The trace should contain | The trace should not contain |
|---|---|---|
| `UP-k` (forward) | Assertions in non-decreasing UP depth (Kendall τ with depth ≥ 0.6). Assertions of derivable non-ancestors of q (fan-out). It stops after the depth-k frontier, or at the fixpoint without q, then says "cannot be determined". | Case splits ("suppose", "case 1"); assertions of non-entailed literals; goal statements before assertions |
| `FC-k` (`UP/{MP}`) | As `UP-k`, but every step cites a conditional in its stated direction | Contrapositive steps ("since not B, not A") |
| `UP-PASS-p` | Assertions in **text order** (τ with premise position ≥ 0.6). Re-scanning markers ("going through the premises again") | Jumps back to earlier premises within a pass |
| `UP-REFUTE-k` | "Suppose q is false…", then propagation from ¬q, then a contradiction | — |
| `RES-w` | Derived **disjunctions** ("so A or C"), followed by their resolution | Explicit case branches with separate continuations |
| `PS(sel)` | No mention (quoting, paraphrase or atom pair) of the premises outside the selection; everything else as `UP` | Use of an unselected premise |
| `2SAT-CORE` / `DROP(sel)` | Constraints of the dropped type are never mentioned or checked. If there is a final verification pass, it skips them. | Acknowledging a violated dropped constraint |
| `IC` | Parts solved in separate blocks, each starting its own labelling at colour 1 / the canonical value. **No reconciliation step**: cross-links are not checked after the parts are combined. | "Swap colours in part B so the cross-links work" (that is `IC-ALIGN`) |
| `DP-LIST` | Tables or lists of reachable (weight, value) pairs, growing item by item. The cost tracks \|L\|. | Enumerating subsets; ratio sorting |
| `MST-TOUR` | Building a spanning tree or minimum edges, then a walk | Nearest-unvisited-city steps |

Competitors' trace signatures, used in the per-cell tables:

| Competitor | Trace signature |
|---|---|
| `BC` | Goals first ("to get q we need b"), then confirmations |
| `DPLL-b` | Nested case branches with propagation inside each, and backtracking markers |
| `MM` / `ETR` | Enumerated possibilities ("possibility 1: A and C") |
| `FIRST` / `BICONDITIONAL` | Unconditional use of one disjunct, or of a converse |
| `SAMPLE-m` | Trying example assignments and checking them |
| `FIRST-FIT` / `DSATUR` | Vertex-by-vertex assignment in a fixed or adaptive order, then a forced conflict |
| `MIN-CONFLICTS` | A full initial assignment, then repairs |
| A cues | No derivation, or a derivation unrelated to the answer |

**Coding scheme.**

1. **L0, automatic parser** (primary for trace features).
   - Segment the trace into sentences.
   - Match vocabulary strings whole-word. Atom strings are fixed per item, so matching is exact.
   - Tag each mention by regex patterns into an event: ASSERT, HYPOTHESIZE, GOAL, CITE-RULE, CASE-OPEN / CASE-CLOSE, ASSIGN (`X: 2`, `A = true`), CHECK (`X–Y ok`), REVISE (`change`, `instead`, `backtrack`) or CONCLUDE.
   - Derived per-trace features:
     - the assertion sequence, and its τ with UP depth, text position and distance to the query;
     - trace-level commissions (asserted, not entailed);
     - case-split count and nesting depth;
     - the set of premises or constraints touched (matched by their atom pairs);
     - the constraints never mentioned;
     - assignment order and revision count;
     - whether a final check is present.
   - Validated on 200 hand-coded traces per domain. Event precision and recall must each be ≥ 0.9.
2. **L1, LLM-assisted codes** (secondary). They cover what regexes miss:
   - the strategy label: forward / backward / case analysis / possibility enumeration / trial assignments / greedy construction / repair / none;
   - the stopping reason: done / gave up / budget;
   - premises explicitly dismissed;
   - "parts solved separately; reconciled? y/n".

   Design rules:
   - The coder is a different model family from the one being evaluated.
   - It sees the premises and the trace, but is **blind to g, the cell and the hypotheses**.
   - It works on chunks of ≤ 8k tokens, with a running summary.
   - Validation: two human coders on 200 traces per domain, stratified by cell. Report Cohen's κ human–human and LLM–human.
   - A code is used only if LLM–human κ ≥ 0.7 and it is within 0.1 of the human–human κ. Otherwise it is dropped.
3. **Not used as evidence:** the model's own description of its strategy ("I'll use unit propagation"). It is recorded, but carries no weight.

**Faithfulness (trace–answer consistency) tests.** Each is run per model and condition.

- **F1, state–answer agreement.** Compute the answer implied by the trace's final state, e.g. q asserted, or the last full assignment written. Compare it with the final answer. φ₁ = the agreement rate.
- **F2, procedure replay.** Re-run the procedure the trace codes as using, on the premises or constraints it touched, e.g. `UP` on the touched premises or `EXACT` on the mentioned constraints. Does the answer equal the replay? φ₂ = the agreement rate.
- **F3, counterfactual co-variation.** On a Type-H pair, does the trace change where the heuristic says it should? Example: the relocated edge stops being mentioned when it is listed last.
- **F4, censored runs.** Compare the truncated trace's partial state with the forced answer. This is reported separately.

**Combining trace and answer evidence.** Answers are primary, and are scored with no LLM in the path. Traces are a second, *unreliable* channel, entering through a measurement model:

> P(y, t | h) = P(y | h) · [ φ · P(t | h) + (1 − φ) · P(t) ]

- y is the scored answer and t the L0/L1 trace code.
- P(t | h) is the trace likelihood under h's signature, with a slip kernel.
- P(t) is the marginal code distribution, which is uninformative.
- φ is estimated per model from F1/F2 on items where the trace fixes the answer. So unfaithful models' traces are automatically discounted (hints are verbalised only about 25–39% of the time: Chen et al. 2025; Arcuschin et al. 2025).

**Disagreement policy.** Pre-registered:

| Answer | Trace | Conclusion |
|---|---|---|
| Fits h | Fits h | Strongest claim: "uses h" |
| Fits h | Fits h′ | "Answer-level h"; the evidence-table Process cell is ✗; the item is flagged trace-discordant |
| Not h | Fits h | No support for h (the trace is narrative) |

- A cell where discordance is systematic is reported as post-hoc rationalisation. That is a finding, not noise.
- Traces never override the answer-level classification on their own.

### 2.5 Eval designs (summary)

| ID | Item generator | Answer format | Metric | Pro threshold (on the §2.5a readouts) | Contra threshold (on the §2.5a readouts) |
|---|---|---|---|---|---|
| E1 | Horn cones: chain / ladder / tree, × depth d, × fan-out, × N. Catch siblings. | 3-way query | Accuracy by d at matched s and u; omission share; chance-polarity index; trace assertion order; k*(budget) | Accuracy depends on d only. Errors are U or chance-polarity guesses. Traces are depth-ordered and stop at a round frontier. | Accuracy tracks s or u; systematic polarity; catch commissions |
| E2 | Minimal-pair battery: case-split ladder, illusory, converse/inverse baits, probability ladder, rule direction; list items | 3-way query and list | Bröder-style posterior over members; soundness index; recall by capability | Commission ≤ 10%; flat probability ladder; omissions where case analysis or width is needed; no case splits in traces | Commission ≥ 25% (B4); rising probability ladder (E/H) |
| E3 | Single-premise counterfactuals on fixed skeletons: position × proof order; form × overlap; query position | 3-way query | Paired main effects; premise-mention sets in traces | The selector's feature has an effect ≥ 10pp and the others ≤ 5pp. The trace never mentions the unselected premise. | All effects null (then `UP-k`), or the order effect grows with d (`UP-PASS` / C4) |
| E4 | Edge-critical graphs and MU formulas, × orthogonal orderings; feasible siblings; relocation and pendant cells | Colouring / assignment or IMPOSSIBLE | Feasibility claims; identity of the violated constraint (conditional logit); consistency; echo | Selector agreement ≥ chance + 15pp; consistency ≥ 0.6; relocation and pendant effects ≥ 15pp; the dropped constraint unmentioned in the trace | Violation identity unpredictable; stuck-vertex pattern (C) |
| E5 | Two planted parts × cross-links in the NC / SC / BD cells, × rendering; entailment header-move pairs | Colouring / assignment / 3-way | SC − NC; where BD violations fall; header-move effect; "reconciliation" trace code | SC − NC ≥ 15pp with cross-only violations; traces solve parts separately without reconciling them | SC ≈ NC; violations inside parts |
| E6 | Knapsack, reachable-sum dial R at matched greedy outputs; trace re-analysis of E1/E2 | Item list | Log trace tokens vs R; accuracy under the 8k budget; DP-table events | Tokens(high R) / tokens(low R) ≥ 2, with DP tables in the trace | Tokens invariant to R |

**Shared generator rules (all evals).**
- **Splits.** Dev/test splits are made at the *base-skeleton* level by content hash, so every variant of a skeleton lands in the same split.
- **Atom and name pools** are partitioned. Dev uses pool half A, test uses half B, so no string is shared between splits.
- **Graphs and formulas** are split by isomorphism-class hash where the classes are rich enough. Odd cycles and wheels are not; for them, only names and orderings differ across splits, and this is recorded.
- **Seeds** come from disjoint ranges.
- **Hardness band.** On the dev split, sizes are calibrated so that **gpt-oss-20b (high)** scores 40–80% on the hardest cell of each eval. The size parameters are then frozen and committed before any test-split run. This rule is pre-registered.
- **Tokenisation.** All length matching uses three tokenizers: gpt-oss (o200k_harmony), Qwen3 and DeepSeek-R1.

### 2.5a Scalar readouts: partial use, not pass/fail

A model may use a member on some items and not others. So every eval is read out as **quantities with intervals**, never as a binary verdict. The "pro / contra" criteria in §2.6–§2.11 are pre-registered thresholds on these quantities. Each one is restated as a weight statement in the table below.

**Model.** For each model and condition:

> P(yᵢ | xᵢ) = Σ_h π_h(φᵢ) · P(yᵢ | h, xᵢ) + π₀ · q(yᵢ | xᵢ)

- P(y | h, x) is the noisy-execution likelihood: lapse ε_h, or the distance kernel for structured answers.
- π_h(φ) = softmax(w_h · φ), where φ are item features (d, s, b\*, n, budget).
- π₀ is the unexplained mass, with the uninformative model q.
- Models are pooled hierarchically. Fits use HMC; ELPD uses PSIS-LOO, with folds split by skeleton.

**Readouts for every eval:**

1. **π_h**: posterior mean and 95% credible interval, for each B1/G member and for the eval's nearest competitors and nulls (`NOISY-EXACT`, `PERCEPTION-NOISE`, `RANDOM`, `EXACT`). The interval is on π_h(φ̄) at the cell-mix mean, plus the slope w_h where φ is manipulated: depth (E1), b\* (E2), n (E4) and budget.
2. **Lift_h** = EA_h − EA_h^perm. This is the share of errors that h explains, above a permutation baseline matched on item structure. It is computed on items where h is wrong, with a 95% bootstrap interval over skeletons.
3. **ΔELPD**, or log₁₀ BF via bridge sampling. Two comparisons:
   - (a) the full zoo vs the zoo without h (gain over the null);
   - (b) h vs its nearest competitor, swapping one for the other in the mixture.
4. **Trace match share** m_h = Σᵢ rᵢₕ · 1[tᵢ ∈ sig(h)] / Σᵢ rᵢₕ.
   - rᵢₕ is the posterior responsibility of h for response i.
   - The result is shrunk by the faithfulness estimate: m̃_h = φ̂ · m_h + (1 − φ̂) · m_h^base (§2.4).
   - We also report the **discordance share**: answers attributed to h whose trace matches another member.

**Weight statements** (these replace the binary pro/contra criteria; per model unless "pooled"):

| Eval | Pro statement (supports partial use) | Contra statement (bounds the competitor) | Power: minimum detectable π_h (80%, per model) |
|---|---|---|---|
| E1 | π_UP-k lower 95% ≥ 0.15, and log₁₀ BF(UP-k vs `NOISY` / `BC` / `FC-budget`) ≥ 1 on the depth–size cells | π_NOISY + π_BC + π_FC-budget ≤ 0.1 (upper 95%) when the depth ordering holds; π_B4 on catches ≤ 0.05 (upper 95%) | ≈ 0.04 (≈ 1,500 discriminating responses; baseline match ≈ 0.15) |
| E2 | π_(UP-∞ ∪ UP-REFUTE ∪ RES-w) lower 95% ≥ 0.15 and π_B4 ≤ 0.1 (upper 95%); the T5 slope of π_SAMPLE ∪ BP within ±0.05 | π_DPLL-b ≤ 0.1 (upper 95%) on T2 failures, using the φ-weighted case-branch share | ≈ 0.03 |
| E3 | π_PS(sel) lower 95% ≥ 0.1 for the named selector | π_UP-PASS + π_C4 ≤ 0.1 (upper 95%) when there is no order × depth slope | ≈ 0.04 |
| E4 | π_DROP(sel) lower 95% ≥ 0.15 on single-violation answers, with log₁₀ LR vs `FIRST-FIT` / `MIN-CONFLICTS` ≥ 1 | π_MIN-CONFLICTS + π_PERCEPTION ≤ 0.1 (upper 95%) | ≈ 0.04 at 300 single-violation answers (baseline 1/m ≈ 0.05); ≈ 0.06 at 150 |
| E5 | π_IC (TEXT or GRAPH) lower 95% ≥ 0.15 in the SC/BD cells | π_IC-ALIGN ≤ 0.1 (upper 95%) if IC is supported, or vice versa | ≈ 0.04 |
| E6 | π_DP-LIST lower 95% ≥ 0.2 on the process channel (the cost slope in log \|L\|) | π_ENUMERATION ≤ 0.1 (upper 95%) | ≈ 0.06 |

The minimum detectable π is MDπ ≈ 2.8·√(b(1−b)/n_d) / (1 − ε − b), where n_d is the number of discriminating responses and b the baseline match rate. This is an analytic approximation; the graded recovery tests below confirm it. Pooled over ≥ 6 models, the population-mean MDπ is roughly halved.

**Recovery tests with graded planted mixtures.** These run on the full-study item sets, with the same samples per item. There are 200 replicates per condition, and each must pass before any LLM fit (DESIGN §5.12).

| Planted | Example components (per eval) | What it tests |
|---|---|---|
| R1: 60 / 30 / 10 | E1: `UP-12` / `NOISY(ε = 0.03)` / `BC-40`. E2: `RES-2` / `DPLL-4` / `BICONDITIONAL`. E3: `PS(RECENT)` / `UP-PASS-1` / `UP-∞`. E4: `DROP(LAST)` / `FIRST-FIT-cap` / `MIN-CONFLICTS`. E5: `IC-GRAPH` / `IC-ALIGN` / `NOISY`. E6: `DP-LIST` / `ENUMERATION` / `RATIO`. | Bias and interval width at a dominant mixture |
| R2: 34 / 33 / 33, and 90 / 10 | The same components | Near-equal mixtures; the detection floor for a minor component |
| R3: feature-dependent | π_UP-k(d) falling from 0.9 to 0.1 across the depth ladder, the rest guessing; π_DROP(n) rising with n; k rising with budget | Recovery of the slope w_h |
| R4: pure nulls | 100% `NOISY-EXACT`, 100% `RANDOM`, 100% `EXACT` | False-positive weight on B1/G members |
| R5: misspecified | An off-zoo procedure, e.g. `UP` firing MT with probability 0.5 | Whether π₀ absorbs it rather than inflating a zoo member |

Lapse ε ∈ {0.05, 0.15} throughout.

Report, per component:
- bias (mean π̂ − π);
- RMSE;
- 95% interval coverage;
- median interval width;
- the bias of w_h in R3.

Pass criteria, per model at full n:
- \|bias\| ≤ 0.05;
- coverage ≥ 0.9;
- median width ≤ 0.2;
- in R4, the upper 95% bound on every B1/G member's π is ≤ 0.1 in ≥ 95% of replicates.

### 2.6 E1 — Propagation-depth ladder: depth × cone shape × fan-out (entailment)

**Question (H-B1.1).** When entailment needs only propagation, do models derive exactly the literals reachable within k parallel unit-propagation rounds? Specifically:
- they stay sound and order-free;
- the effective k grows with the thinking budget;
- at best effort they are near fixpoint, failing only at the largest d.

It is falsified if any of these holds:
- accuracy on determined items depends on cone size s, tree-unfolding size u, fan-out F or premise count N at matched d;
- errors beyond the frontier have systematic polarity;
- traces are not ordered by depth.

**Cone shapes.** Each item embeds one *cone*: the premises needed to derive the target.

| Shape | Structure | Fan-in | Cone size s | Unfolding u | Facts in cone |
|---|---|---|---|---|---|
| `chain(d)` | F → a₁ → … → a_d = q | 1 | d | d | 1 |
| `ladder(d)` | Two literals per level; each is derived by an AND-rule from both literals of the level below | 2 | 2d − 1 | 2^d − 1 | 2 |
| `tree(d)` | A complete binary AND-tree | 2 | 2^d − 1 | 2^d − 1 | 2^d |

**Cells (Tier L, N = 112 premises).**
- chain d ∈ {2, 4, 8, 16, 24, 32};
- ladder d ∈ {2, 4, 8, 12, 16};
- tree d ∈ {2, 3, 4, 5};
- fan-out block: chain d ∈ {8, 16} × F ∈ {0, 24} (the default is F = 12 derivable non-ancestor literals);
- Tier XL (N = 224): chain 8 and 16, ladder 8, tree 4.

That is 23 cells, with 50 skeletons per cell × 2 versions = **2,300 items**.

The design contains:
- **matched-d trios**: d = 2 and d = 4 (chain / ladder / tree at the same d);
- **matched-s triples**: s ≈ 15–16 (chain 16 / ladder 8 / tree 4) and s ≈ 31–32 (chain 32 / ladder 16 / tree 5).

**Versions.**
- *Determined* (g = TRUE or FALSE, balanced). FALSE targets end in "then not q".
- *Catch* (g = U):
  - for chains: half have one link reversed at a random position, and half have the start fact negated;
  - for fan-in 2: one antecedent of one cone rule is replaced by an underivable atom ("missing-antecedent").

**Predicted answers and traces per contrast.**

Column key: (a) matched d: chain / ladder / tree. (b) Matched s: tree (small d) / ladder / chain (large d). (c) Chain vs fan-in 2 at matched d. (d) Fan-out F 0 → 24. (e) N 112 → 224. (f) Catch items. (g) Error form beyond capacity. (h) Trace.

| Member | (a) | (b) | (c) | (d) | (e) | (f) | (g) | (h) |
|---|---|---|---|---|---|---|---|---|
| `UP-k` | = = = | tree > ladder > chain (by d) | = | = | = | U | U or chance-polarity guess | Assertions ordered by depth (τ_depth ≥ 0.6); fan-out literals asserted; stops at a round frontier |
| `RES-2` (parallel) | chain > ladder = tree | tree > chain ≈ ladder | chain ≫ fan-in 2 | = | = | U | U | Composed conditionals ("so if F then a₄"); no case splits |
| `PS(SHORT, 2)` | Fan-in-2 at U for every d, including d = 2 | — | chain ≫ fan-in 2 | = | = | U | U | AND-rules never quoted |
| `PS(RECENT, j)` | chain > ladder > tree (cone premise count) | ≈ | chain > fan-in 2 | = | ↓ | U | U | Early premises never mentioned |
| `UP-PASS-p` / C4 | Order-dependent (E1 randomises order with \|τ_proof\| ≤ 0.2) | ≈ | ≈ | = (C4: ↓) | = | U | U | Assertions follow text order (τ_text ≥ 0.6); re-scan markers |
| `BC-b` (no memo) | chain > ladder ≈ tree | chain ≈ tree > ladder | chain ≫ fan-in 2 | = | = | U | U | Goals first, then confirmations; no fan-out assertions |
| `FC-budget-b` | chain > ladder > tree (BFS index) | ≈ | chain > fan-in 2 | ↓ | = | U | U | Every derivable literal asserted in BFS order until the budget runs out |
| `NOISY-EXACT` | chain > ladder > tree, as (1−ε)^s | = | chain > fan-in 2 | = | = or ↓ | Mostly U; ε_c commissions | U plus a few commissions | A cone literal skipped mid-sequence, then propagation continues without it |
| `SAMPLE-m` | Flat (depth-invariant) | = | = | = | = | Commission with probability P(q)^m | none | Trial assignments checked against premises |
| `BICONDITIONAL` / `DROP-CONJUNCT` | Correct | = | = | = | = | **Commission** (TRUE on reversed-link; FALSE on negated-fact; TRUE on missing-antecedent) | none | Uses a converse, or fires an AND-rule on one antecedent |
| `NONE` | U at every d, including d = 2 | — | — | = | = | U | U | No derivation |
| `FREQ` / `ATMOSPHERE` | Flat | = | = | = | = | The sibling's answer (surface polarity matched) | Systematic polarity | Derivation unrelated to the answer |
| `WP-t` / `BP-t` | = `UP-t` | = | = | = | = | WP: U; BP: U (catches have P(q) ≈ 0.5) | U | — |

**Counterfactual pairs.**

| Pair | Type | What it isolates |
|---|---|---|
| Matched-s triple | Type-H for `UP-k` (UP differs, g and `NOISY` same) | Depth sensitivity |
| Matched-d trio | Type-H for `NOISY`, `BC` and `FC-budget` (they differ, UP same) | Size sensitivity |
| Determined vs catch at d > k | Type-G for `UP-k` (g differs, UP-k says U on both) | UP-k's blindness |
| Determined vs catch | Type-G for `BICONDITIONAL` (both determinate) | B4's blindness |

**Confound control.**
- **Premise-type quota fixed per tier.** Tier L: 36 facts, 40 one-antecedent rules, 36 AND-rules, and 12 negations placed by a fixed rule. So every item in a tier has the same counts of `if`, `and`, `not` and `or`.
- Atom strings come from token-count-matched pools. Mean tokens per cell must be within ±2% of the tier mean, and each determined/catch sibling pair within ±3 tokens, in all three tokenizers.
- q is mentioned exactly twice in every item: as the consequent of the cone's last rule, and in one dead distractor. Its mention polarity is the same across siblings.
- Proof-order correlation |τ_proof| ≤ 0.2. Mean cone-premise position is matched across cells (±2 positions).
- Fan-out is fixed (F = 12) outside the fan-out block, with fan-out literals spread over depths ≤ d.
- **Surface gate.** A logistic classifier on 15 surface features is trained on the full set: counts, positions, q-mention polarity, q-as-consequent, premise lengths. Its held-out AUC must be ≤ 0.60 for g and ≤ 0.60 for depth bucket. If not, the offending cells are regenerated. This guards against SimpleLogic-style shortcuts (Zhang et al. 2023).

**Generator spec.**
- **Template.** "Here are some facts and rules. … Question: is it true that ⟨q⟩? Answer TRUE if the premises guarantee it, FALSE if they guarantee it is false, or UNDETERMINED if they do not settle it. End with `ANSWER: …`."
- **Rendering.** Natural rendering (primary); a bare-logic rendering on 10% of skeletons ("P3. If P3 then P7."); and an optional realistic-theme rendering (v1 themes) on 10% in Phase 2.
- **Parameters.** shape, d (grid above), N ∈ {112, 224}, F ∈ {0, 12, 24}, target polarity ~ Bernoulli(0.5), catch type ~ uniform over the shape's types, reversed-link position ~ U{1..d}.
- **Construction.**
  1. Build the cone with fresh atoms.
  2. Add live distractors (antecedents derivable from distractor facts or cone literals) until there are F fan-out literals at depths ≤ d.
  3. Add dead distractors (antecedents drawn from "sink" atoms that are never derivable) until the type quota is met.
  4. Place 12 negations as polarity flips on distractor literals, plus cone literals when the polarity schedule needs them.
- **Rejection.**
  - z3 reports P inconsistent, or `UP` hits a conflict.
  - The target's UP depth is not exactly d. This also excludes shorter alternative derivations.
  - For fan-in-2 items: `RES-2` depth < d, i.e. an accidental binary-path shortcut.
  - For catches: z3 finds g ≠ U, or the designated B4 member does not commit.
  - Token-match or surface-gate failure.
- **Variant derivation.**
  - The catch is a single edit of the determined item: swap one rule's antecedent and consequent; negate the start fact; or replace one antecedent atom with a sink atom whose string has matched token length.
  - The Tier XL version of a skeleton adds 112 dead distractors with the same type proportions.
- **Yield.** Expected rejection is low (< 20%), since construction is direct. Most rejections should come from the token-match gate on XL items, and from accidental shortcuts in ladders. Measure on dev.

**Metric and analysis.**
- Accuracy per cell, the omission share, and the **chance-polarity index** P(correct polarity | determinate answer, determined item beyond the frontier).
- Catch commission.
- **Latent-step likelihood:**
  - for d ≤ k, y = g with probability 1 − λ;
  - for d > k, y = U with probability c, otherwise TRUE or FALSE with probability (1 − c)/2 each;
  - k is hierarchical per model × condition, with item-feature-dependent π_k(φ).
- Competitor likelihoods: `NOISY` (s), `BC` (u), `FC-budget` (BFS index), `RES-2` (log-depth), `SAMPLE-m`. They are compared by ELPD, with CV split by skeleton.
- Trace features: τ_depth, τ_text, fan-out-assertion rate, goal-first rate, skip-and-continue events.

**Pro thresholds** (levels on the §2.5a readouts π, lift, ΔELPD; restated as weight statements there) (pooled hierarchical fit; each model must pass a competence gate of ≥ 80% on d = 2):
1. `UP-k` (or `RES-2` / `UP-∞` with a frontier) beats `NOISY`, `BC`, `FC-budget` and `SAMPLE` by ΔELPD > 4.
2. At matched d, chain–tree and chain–ladder gaps are ≤ 10pp (TOST). At matched s, accuracy orders by d with gaps ≥ 10pp.
3. ≥ 70% of errors beyond the frontier are U or chance-polarity guesses (polarity accuracy 50 ± 8%).
4. Catch commission ≤ max(5%, 2 × lapse).
5. τ_depth ≥ 0.6 in ≥ 70% of coded traces, with fan-out assertions present.
6. Budget factor: k* rises from 2k → 8k → 32k.

**Contra thresholds** (bounding competitor weight; §2.5a) any of these:
- accuracy tracks s (NOISY) or u (BC);
- polarity is systematic;
- catch commission ≥ 15%;
- τ_text dominates (then E3 decides between `UP-PASS` and C4).

A strong chain ≫ fan-in-2 effect with a log-shaped chain curve *refines* B1 toward `RES-2` rather than falsifying it.

**Sample size.**
- Per cell, 50 determined items × 3 samples. With ICC ≈ 0.3, the effective n is ≈ 94. At p ≈ 0.85 the SE is ≈ 3.7pp, so a contrast has SE ≈ 5.2pp and a 15pp gap is detected with 80% power per model. Pooled over ≥ 6 models in the hierarchical model, the equivalence margin is ±5pp.
- `NOISY` calibrated to the chain slope predicts a chain–tree gap ≥ 20pp at d = 4 (s = 4 vs 15) whenever ε ≥ 0.02. Power > 0.95 per model.
- Step location: a step of ≥ 30pp between adjacent d levels is located to ±1 level with probability > 0.95. Confirm with the graded planted-mixture recovery tests (§2.5a: R1–R5, e.g. 60/30/10 over `UP-12` / `NOISY` / `BC-40`), reporting bias and interval width.

**Threats and fixes.**
1. **Anti-UNDETERMINED bias.** Fixed by the chance-polarity analysis and catch-calibrated criterion c.
2. **Ceiling at best effort.** Fixed by the dev-calibrated hardness band. If d = 32 is still at ceiling, extend to d = 64 and N = 384 before freezing.
3. **Depth leaking through the surface.** Fixed by the quotas and the surface gate.
4. **Shortcut statistics from the generator.** Fixed by the surface gate, and by holding out distractor templates between dev and test.
5. **Censoring.** Runs that hit the cap are analysed separately and never counted as omissions.
6. **Natural-language AND-rules parsed as two rules.** Fixed by the bare-logic arm.
7. **Item heterogeneity in k.** Fixed by π_k(φ(x)).
8. **Unfaithful traces.** Fixed by the φ-weighted combination (§2.4). The trace criteria are secondary.

### 2.7 E2 — Soundness profile: omission vs commission, and the case-split ladder (entailment)

**Question (H-B1.2).** Are entailment errors omissions (B1) rather than commissions (B4 restrictions, E soft propagation, H sampling, A cues)?
- At best effort, do models stay **propagation-complete but case-split-incomplete**? That means they find everything derivable by `UP` or low-width resolution, but omit conclusions that need b nested case splits beyond some b̂.
- Or do they case-split (D: `DPLL-b`), or enumerate possibilities (B4: `MM`)?

**Cells.** Each cell is a minimal pair, x and x′, differing by one edit of ≤ 3 tokens, found by counterfactual search. The size targets for the full study are given per cell.

| Cell | x (g) | x′ (g′) | Isolates | Pairs |
|---|---|---|---|---|
| T1 control | Depth-1 MP (TRUE) | An irrelevant fact replaces the antecedent fact (U) | Competence; response criterion | 50 |
| T2 case-split ladder | q entailed; forward `UP-∞` fails; b* = min DPLL depth, with UP at every node, refuting P ∧ ¬q, in {0..5}. b* = 0 means reductio propagation suffices (`UP-REFUTE`). Width w* recorded. (TRUE) | One literal edit making q undetermined, keeping b* and w* of the remaining structure (U) | `RES-w` vs `DPLL-b` vs `UP-∞` vs `MM`-cap vs `FIRST` | 5 × 60 |
| T3 illusory | ETR-predicted fallacy (PyETR; v1 items), e.g. "an ace and a queen, or else a king and a ten; a king; so a ten?" (U) | Control in which the ETR answer follows (TRUE) | B4 `ETR` / `MM` commission vs B1 | 100 |
| T4 baits | A quartet: AC (U), DA (U), MP (TRUE), MT (FALSE) | Within the quartet | `BICONDITIONAL` / `CLOSED-WORLD` commission; `FC` and `MM`-initial MT omission | 60 quartets |
| T5 probability ladder | g = U with P(q \| P) ∈ {0.5, 0.75, 0.9, 0.97} under the uniform measure over models | One edit making q entailed | `BP-t` / `SAMPLE-m` commission rising with P, vs B1 flat | 4 × 50 |
| T6 rule direction | DS "A or B; not A ⇒ B?" (TRUE); compound DS + MT (FALSE) | The FIRST-bait variant | `UP/R` direction set | 60 |
| List | 12-atom theories with determined non-fact literals tagged {MP-depth-1, MP-depth-3, MT, 2-way dilemma}, plus 2 probable-not-entailed literals and 1 converse bait | — | Precision / recall by type | 200 |

**Predictions.** Answer first, trace in brackets. ✓ means correct.

| Member | T2 x / x′ | T3 x / x′ | T4 AC, DA, MP, MT | T5 as P(q) rises | Trace |
|---|---|---|---|---|---|
| `UP-REFUTE-∞` | ✓ iff b* = 0 / U | U / ✓ | U, U, ✓, ✓ | Flat | "Suppose not q …", back-propagation, contradiction |
| `UP-∞` | U / U (invariant) | U / ✓ if `UP`-derivable | U, U, ✓, ✓ | Flat U | Propagation only; "cannot be determined"; no cases |
| `FC-k` | U / U | Same as `UP` | U, U, ✓, **U** | Flat | No contrapositives |
| `RES-w` | ✓ iff w* ≤ w / U | U / ✓ | U, U, ✓, ✓ | Flat | Derived disjunctions |
| `DPLL-b` (D) | ✓ iff b* ≤ b, else default / U | U / ✓ | U, U, ✓, ✓ | Flat | "Case 1 … Case 2 … in both cases" |
| `MM` (cap c) | ✓ if the model count ≤ c / U, or commission when capped | **C** / ✓ | **C** (AC), U or C, ✓, **U** | Flat | Lists possibilities |
| `ETR` (PyETR) | Computed per item | **C** / ✓ | U, U, ✓, ✓ (PyETR: AC and DA give "nothing follows"; MT gives ¬A) | Computed | Possibilities; supposition |
| `FIRST` | ✓ / **C** | C / ✓ | — | — | Takes the first disjunct |
| `BICONDITIONAL` / `CLOSED-WORLD` | — | — | **C**, **C**, ✓, ✓ | — | Converse used |
| `BP-t` (τ = 0.8) | ✓ / C if P ≥ τ | C if P ≥ τ | — | **Commission once P ≥ τ** | Probabilistic language |
| `SAMPLE-m` | ✓ / C with probability P^m | Same | — | **Rises as P^m** | Example assignments |
| `FREQ` | Polarity-driven / same | Same | Polarity-driven | Flat (polarity balanced) | — |
| `EXACT` | ✓ / U | U / ✓ | U, U, ✓, ✓ | Flat U | Any complete method |
| `NOISY-EXACT` | ✓ / U with slips | U / ✓ | Mostly ✓ | Flat | — |

Two separations to note:
- `EXACT` and `DPLL-b` with large b are separated from B1 *only* where b* exceeds the frontier. T2 provides that, and E1 does the same at large d.
- In traces, `DPLL` shows case branches where `UP-∞` shows none.

**Generator spec (T2).**
- **Sampling.** Draw random consistent CNF theories over n ∈ [8, 16] atoms: 2-clauses and 3-clauses at a ratio of 1:1, with m/n ∈ [1.5, 2.5], plus 0–2 facts. Draw q among the non-fact atoms.
- **Keep the item if:**
  - z3 shows P ⊨ q;
  - forward `UP-∞` does not derive q;
  - b* is computed by exhaustive search over DPLL trees, with `UP` at every node, refuting P ∧ ¬q;
  - w* = the minimal w for which forward `RES-w` derives q.
- **Binning.** Bin items by b*, and within each bin balance w* ∈ {2, 3, ≥ 4}, so that b* and w* are decorrelated across the cell (target \|r\| ≤ 0.3).
- **Sibling.** Search over single-literal flips or atom swaps for an edit that makes g = U and leaves the other clauses intact.
- **Rendering.** Clauses are rendered as "at least one of …", or as conditionals when they carry a direction tag.
- **Measured yield** (random draws, 7 atoms, 8–11 clauses, 4,000 draws): 105 were entailed but not UP-derivable. Of those, 90 had b* = 0 and 15 had b* = 1; none had b* ≥ 2.
- **So bins with b* ≥ 1 use constructive gadgets.**
  - A complete clause set over b + 1 variables entails its head with b* = b. Its atoms are renamed, it is chained into the query through Horn links, and it is interleaved with Horn distractors.
  - In the plain gadget b* = w*. We try to decorrelate them by composing gadgets, and measure the result on dev.
  - If \|r(b*, w*)\| ≤ 0.3 cannot be reached, T2 is reported by b*, and `RES-w` vs `DPLL-b` is separated only by traces (derived disjunctions vs case branches).

**Generator spec (other cells).**
- **T3:** v1 PyETR items, re-rendered with neutral atoms, with v1's control items as siblings.
- **T4:** quartet templates over fresh atoms, padded to equal length with 2 irrelevant facts.
- **T5:** U items whose exact P(q \| P) falls in each bin, counted by brute force; the q-mention polarity is balanced across bins.
- **Surface matching** follows E1: same atom pools, ±3 tokens within a pair, and positions preserved by the edit.

**Metric.** Bröder & Schiffer-style classification. Each member predicts a response vector over the battery; P(y | h) carries a lapse ε_h; we take the posterior over members per model × condition. Also reported:
- the soundness index S = 1 − P(determinate wrong | g = U);
- recall by capability (b*, w*, rule type).

**Pro thresholds** (levels on the §2.5a readouts π, lift, ΔELPD; restated as weight statements there) all of:
- S ≥ 0.9;
- the T5 slope is ≤ 5pp per bin;
- in T2, accuracy falls with b* and traces show no case splits on the failures;
- the posterior on B1 members is ≥ 0.9.

**Contra thresholds** (bounding competitor weight; §2.5a) any of:
- commission is ≥ 25% on T3 x or on T4 AC/DA (B4-like);
- the T5 slope is ≥ 15pp per bin (E/H-like);
- T2 failures carry case-split traces that branch correctly but are abandoned (then this is D, `DPLL-b`, not B1).

**Sample size.** ≥ 50 pairs per cell × 3 samples gives an SE of about 4pp per proportion, enough to separate 10% from 25% commission with power > 0.9 per model. For the T2 slope across 5 bins, an effect of 8pp per bin is detectable.

**Threats.**
- *Cells differ in surface form.* This is inherent, so only within-pair and within-cell contrasts are used.
- *B4 predictions depend on implementation parameters.* Sweep the B4 vertical's pre-registered grid: `MM` cap c ∈ {2, 3, 4}.
- *Anti-U bias.* Report the chance-polarity index on T2 x.
- *Shortfalls in the list format.* MP-depth-1 recall is the baseline. On 100 list items, each literal is re-asked as a single query (400 extra items, in the 1,860 total).

### 2.8 E3 — Premise-selection probes (entailment)

**Question (H-B1.3).** When models omit, is it because they reason over a *selected subset* of premises, or over a single left-to-right pass? The candidate selectors are recency, primacy, syntactic type, and lexical overlap with the query. The alternative is all premises with a depth limit.

**Skeleton.** A chain of depth d ∈ {4, 12} (P cells) or d = 8 (O and Q cells), embedded in N = 96 premises (quota: 20 facts, 40 one-antecedent rules, 36 AND-rules). The critical premise π\* is the middle link of the chain.

**Cells.** Every skeleton is rendered in all cells of its sub-design, so all contrasts are paired.

| Sub-design | Cells | What changes |
|---|---|---|
| P | {early, late} × {proof order, reverse proof order}; half the skeletons at d = 4, half at d = 12 | Cone premises occupy the first-third or last-third slots, in derivation order or reversed |
| O | {conditional, disjunctive phrasing of π\*} × {query overlaps π\*, query overlaps a dead distractor} | Overlap is produced by permuting atom strings among roles |
| Q | {query before the premises, query after} | — |

Every sub-design also gets catch siblings at 25%.

**Predictions** (✓ correct, U omission):

| Member | P: early-fwd, early-rev, late-fwd, late-rev | O: cond-hi, cond-lo, disj-hi, disj-lo | Q: first, last | Trace |
|---|---|---|---|---|
| `UP-k` (k ≥ d) | ✓ ✓ ✓ ✓ | ✓ ✓ ✓ ✓ | = | All cone premises cited, in depth order |
| `PS(RECENT, N/2)` | U U ✓ ✓ | = | = | Early premises never mentioned |
| `PS(FIRST, N/2)` | ✓ ✓ U U | = | = | Late premises never mentioned |
| `UP-PASS-p` (p < d + 1) | ✓ U ✓ U, with the penalty growing with d | = | = | Text-order assertions; re-scans |
| C4 `ONLINE-STATE` | ✓ U ✓ U, also ↓ with memory load | = | = | Premise-by-premise narration |
| `FC-k` / `PS(TYPE: disjunction)` | = | ✓ ✓ U U | = | The disjunction is never used |
| `PS(OVERLAP, j)` | = | ✓ U ✓ U | Query-first helps | Mentions the high-overlap distractor |
| `BC-b` | ✓ ✓ ✓ ✓ | = | Query-first helps (goal-directed reading) | Goals first |
| A `PRIMACY` / `RECENCY` (cue) | Constant answer (q-mention polarity is fixed), so no omission pattern | — | — | — |
| `NOISY` / `PERCEPTION-NOISE` | Flat, or a weak gradient | Flat | = | Random skips |
| `EXACT` | ✓ everywhere | ✓ | = | — |

**Generator spec.**
- **Position cells** are produced by swapping each cone premise with a *type- and token-length-matched* dead distractor, so the premise multiset and every non-cone position are identical across cells.
- **Disjunctive phrasing** uses 3 paraphrase templates, matched to ±1 token.
- **Overlap** is created by giving atom names shared head nouns. The same strings appear in every cell, in permuted roles.
- **Query-first** uses the same instruction text, moved.
- **Rejection:** if a swap creates an alternative derivation, or the token match fails.
- **Yield:** above 90%.

**Metric.** Paired mixed logit with skeleton random effects (main effects plus the order × depth interaction), and per-cell trace premise-mention sets. In the F3 test, the unmentioned premise should be exactly the predicted one.

**Pro thresholds** (levels on the §2.5a readouts π, lift, ΔELPD; restated as weight statements there) the selector's predicted main effect is ≥ 10pp, the others are ≤ 5pp (TOST), and traces in the failing cells do not mention the predicted premises.

**Weight on `UP-k`** is favoured if all effects are ≤ 5pp with high accuracy. If the order effect grows with d, the result moves to `UP-PASS` (B1) or C4, and the memory-load contrast from E1 decides between them.

**Sample size.** 60 skeletons per sub-design × 3 samples ≈ 110 effective pairs. That detects a 12pp main effect with 80% power (McNemar), and a 25pp interaction. Total **750 items**.

**Threats.**
- *Local coherence changes when premises move.* Fixed by the matched swaps.
- *Disjunctions are harder to read for every member.* Measured on E2-T6, and on dead-distractor disjunctions.
- *Atom associations under the overlap permutation.* Balanced across skeletons.

### 2.9 E4 — Critical-constraint localisation: violation profiles (coloring, SAT)

**Question (H-B1.4).** When models return infeasible solutions, is the violated constraint the one a systematic relaxation drops, with every other constraint satisfied? The candidates are last-listed, first-listed, long-range, wide clause, or all-negative clause. The alternatives are:
- a stuck vertex of a constructive order (C);
- a local-search residual (F);
- a search frontier (D);
- a cue procedure (A);
- random noise.

**Design.**
- **Every constraint is critical.** Instances are (k+1)-edge-critical graphs or minimally unsatisfiable (MU) formulas, so a single-violation answer names exactly one "dropped" constraint.
- **Orthogonal orderings.** Each base instance is rendered under 4 orderings. Each is a pair (vertex/variable introduction order, constraint list order), chosen by search so that:
  - the selectors' and competitors' predicted constraints are pairwise distinct;
  - list position, intro distance, endpoint intro index and degree are uncorrelated across constraints. This makes the design D-optimal for the edge-choice model.
- **Arms.**
  - Coloring k = 3: random 4-edge-critical graphs with n ∈ {12, 16, 20, 24}. Greedy edge deletion from random 4-chromatic graphs makes every remaining edge critical.
  - SAT: MU subformulas of random 3-SAT with n ∈ {12, 16, 20} at α ≈ 4.26, by deletion-based MUS extraction. Plus MU formulas from (2+p)-SAT with p ≈ 0.4 (Monasson et al. 1999, per report F) for `2SAT-CORE`.
  - A small k = 2 diagnostic arm: odd cycles. These are the only 3-critical graphs, and reasoning models will usually see the parity argument.
- **Feasible siblings.** One degree-preserving double-edge swap (coloring) or one literal flip (SAT) makes the instance feasible, with equal counts and widths.
- **Type-H sub-designs** on 40 graphs and 20 formulas:
  - (i) relocation: swap the last-listed constraint with a mid-list one;
  - (ii) pendant: an irrelevant constraint (a pendant edge to a new vertex, or a clause on a fresh variable) placed first vs last.

**Predictions.** On UNSAT critical items.

| Member | Claims feasible? | Violated constraint(s) | Moves under list reorder? | Moves under intro reorder? | Cross-sample consistency | On feasible siblings | Pendant last vs first | Trace |
|---|---|---|---|---|---|---|---|---|
| `DROP(LAST)` | Yes | Exactly the last-listed | Yes | No | High | Its lex-first colouring of G − e_last; may violate e_last | **Last → IMPOSSIBLE (correct)**; first → as before | e_last never mentioned or checked |
| `DROP(FIRST)` | Yes | The first-listed | Yes | No | High | Analogous | No change | e_first never mentioned |
| `DROP(LONG)` | Yes | Maximal intro-distance edge | No | Yes | High | Analogous | No change | That edge never mentioned |
| `2SAT-CORE` / `DROP(WIDE)` (2+p arm) | Yes | Only width-3 clauses | No | No | High | Only width-3 | — | 3-clauses not checked |
| `DROP(NEG)` | Yes | All-negative clauses | No | No | High | — | — | Negative clauses skipped |
| C `FIRST-FIT-cap` (intro order) | Yes, or stuck → IMPOSSIBLE | Edges at the first stuck vertex | No | Yes | High | Feasible, or stuck | No change | Vertex-by-vertex in intro order, then a forced conflict |
| C `DSATUR-cap` | Same | At the DSATUR stuck vertex | No | Partly (ties) | High | Same | No change | Most-constrained-first narration |
| D `DPLL-b` | Above budget, default | Near the last decision | No | Yes | Medium | Feasible within budget | No change | Branching and backtracking |
| F `MIN-CONFLICTS-k` | Yes (never certifies UNSAT) | One edge anywhere, varying across samples | No | No | **Low** (≈ Σp²) | Feasible | No change | Full assignment, then repairs |
| E `BP-t` + rounding | Yes | Several, scattered | No | No | Medium | — | — | — |
| A `CYCLIC` | Yes | Edges with intro(u) ≡ intro(v) mod k | No | Yes | High | Often infeasible | No change | No search |
| A `DENSITY` | Decision by density only (matched across siblings) | — | — | — | — | Same decision as on UNSAT | Equal first vs last | — |
| B4 `ADD-CONSTRAINT` | No | — | — | — | — | **False IMPOSSIBLE** | — | A phantom constraint stated |
| `PERCEPTION-NOISE` (recency) | Yes | Random, with a late-list gradient | Weakly | No | Low | Random violations | Weak, and both positions | The constraint is misquoted or omitted when restated |
| `NOISY-EXACT` | Sometimes | Uniform | No | No | Low | Random | No change | — |
| `EXACT` | No (IMPOSSIBLE) | — | — | — | — | ✓ | — | A proof of impossibility |

**Metric.**
1. P(claims feasible) on UNSAT items vs on feasible siblings. Relaxation predicts high claim rates on both.
2. For single-violation answers, a conditional logit P(violated = e) ∝ exp(β·φ(e)), with φ = [is-last, is-first, list rank, intro distance, max endpoint intro index, degree, clause width, all-negative].
3. Agreement with each selector, vs chance 1/m.
4. Cross-sample consistency κ.
5. Violations on siblings ⊆ D_sel.
6. **Echo recall** of the violated constraint. A separate low-effort call restates the constraint list.
7. Trace: is the violated constraint ever mentioned or checked?

**Pro thresholds** (levels on the §2.5a readouts π, lift, ΔELPD; restated as weight statements there) all of:
- agreement with a pre-registered selector is ≥ chance + 15pp, and ≥ the best competitor + 10pp;
- κ ≥ 0.6;
- relocation and pendant-last effects are ≥ 15pp (paired);
- echo recall of e\* is ≥ 90%, so the constraint was encoded but not used;
- the trace never checks e\* on ≥ 70% of violating runs.

**Contra thresholds** (bounding competitor weight; §2.5a) any of:
- all |β| on selector features are < 0.2, and κ ≈ noise;
- violations cluster at stuck vertices (C);
- answers have many scattered violations (F, E or noise).

**Generator spec.**
- **Critical graphs.** Draw G(n, p) until χ = 4. Delete edges greedily in random order while χ stays 4, using an exact colouring check. The result is 4-edge-critical: every remaining edge, when removed, makes χ = 3.
- **MU formulas.** Draw random 3-SAT at α = 4.26 until UNSAT, then delete clauses while the formula stays UNSAT.
- **Ordering search.** Sample 500 orderings; score them by distinctness of the predictions and decorrelation of φ; keep the best 4.
- **Rejection.**
  - Prediction ties between `DROP(LAST)`, `FIRST-FIT` and `DROP(LONG)`.
  - Instances that the hardness band (dev-calibrated on gpt-oss-20b) marks as too easy, i.e. IMPOSSIBLE proved in < 2k tokens on > 90% of samples.
- **Names.** Vertex names come from a token-matched pool; variables are rendered as named switches.
- **Yield.**
  - Critical-graph construction succeeds on about 1 in 3 G(n, p) draws at p ≈ 3.5/n.
  - MUS extraction always succeeds.
  - Ordering search keeps about 60% of instances.

**Size.** 60 graphs and 60 formulas × 4 orderings, plus siblings, plus 10 odd cycles × 4, plus the relocation and pendant cells: **1,220 items**, 3 samples each.

**Power.** Chance is 1/m ≈ 2–4%. Suppose 20% of 1,000 UNSAT responses per model are single-violation claims (about 200). Then the agreement SE is about 3pp, so a 15pp lift is detected with power > 0.99. Paired relocation and pendant contrasts (60 instances × 3 samples) detect 15pp with 80% power.

**Threats.**
- *Models mostly answer IMPOSSIBLE, or hit the cap.* The decision arm still tests SAT bias. The hardness band raises n.
- *Critical instances are atypical.* Run a secondary violation-profile analysis on random near-threshold instances from the shared domain runs.
- *Long-range is defined by intro distance.* This is pre-registered.
- *Truncation.* Forced answers are analysed separately (F4).

**Extension (routing; not budgeted).** On tours with repeats or skips, are the repeats at MST branch vertices (`MST-WALK`)? Feasible tours are compared by edit distance to `MST-TOUR`, `NN-from-0`, `GREEDY-EDGE` and `2OPT` (the precedent is AlgoTrace's NN-path measure).

### 2.10 E5 — Cross-link decomposition quads (G: `IGNORE-CROSSLINKS`)

**Question (H-G.1).** Do models solve weakly coupled instances part by part, label each part canonically, and never reconcile the cross-part constraints? If so, they err exactly when the canonical part solutions clash on cross-links. A second question: is "part" defined by text layout or by graph structure?

**Design.**
- Two planted parts, A and B, whose solutions are unique up to symmetry:
  - k = 2: trees on 6–10 vertices;
  - k = 3: 2-trees on 8–12 vertices, which are uniquely 3-colourable;
  - SAT: 8-variable parts with exactly 2 models.
- c cross-links: k = 2 uses c = 2; k = 3 uses c = 3, all from one A-vertex; SAT uses c = 2 binary clauses.
- Parts, intra-part constraints, list positions and cross-link endpoint degrees are held fixed. Only the cross-link endpoints change, to realise three cells:

| Cell | Canonical part solutions vs cross-links | g |
|---|---|---|
| **NC** (slack, no clash) | Already satisfy every cross-link | Feasible |
| **SC** (slack, clash) | Violate them, but a relabelling of B satisfies them | Feasible |
| **BD** (binding) | No relabelling satisfies them | Infeasible |

  - For k = 2, with canonical BFS colourings: NC has both cross-links differing; SC has both equal; BD has one of each, which creates an odd cycle.
  - For k = 3, the B-endpoint canonical colours relative to the A-vertex are (2, 3, 2) for NC, (1, 2, 1) for SC, and (1, 2, 3) for BD.
- Crossed with rendering: **clustered** (A's constraints, then B's, then an "Also, …" paragraph of cross-links) or **interleaved** (one shuffled list).
- **Entailment arm: header-move minimal pairs.** N = 96, with a depth-8 chain and two section headers.
  - x: the boundary splits the chain.
  - x′: the identical premise sequence, with the boundary moved so the chain sits inside one section.
  - Also: no-header controls, and a boundary placed before vs after a *fact* (`IC-FACTS`).

**Predictions.**

| Member | NC | SC | BD | Clustered vs interleaved | Trace |
|---|---|---|---|---|---|
| `EXACT` | ✓ | ✓ | IMPOSSIBLE | = | Global reasoning; a proof on BD |
| `IC-GRAPH` | ✓ | Violates exactly the clashing cross-links | Claims feasible; violates exactly the clashing cross-link(s) | = | Parts in separate blocks; each restarts at colour 1; **no cross-link check** |
| `IC-TEXT` | As `IC-GRAPH` when clustered | As `IC-GRAPH` when clustered | As `IC-GRAPH` when clustered | Interleaved: no decomposition (behaves as its solver) | Follows the paragraphs |
| `IC-ALIGN` | ✓ | ✓ | Claims feasible; one cross violation (min-violation alignment) | = | "Swap colours in B so the cross-links work" |
| C `FIRST-FIT` (A before B) | ✓ | Feasible or stuck at a B-vertex (computed); violations may be inside B | Stuck → violation at the stuck vertex, intra or cross | Via intro order | Vertex-by-vertex, cross-links checked as reached |
| F `MIN-CONFLICTS` | ✓ | ✓ | One violation anywhere on the odd cycle | = | Repairs |
| D `DPLL-b` | ✓ | ✓ | IMPOSSIBLE within budget, else default | = | Branching |
| A `DENSITY` / `CYCLIC` | Same decision in all cells (density matched) | — | — | — | — |
| B4 `ADD-CONSTRAINT` | Possible false IMPOSSIBLE | Same | IMPOSSIBLE | = | Phantom constraint |
| `NOISY` / `PERCEPTION-NOISE` | Rare random violations, equal across cells | — | — | — | — |

Entailment arm:
- x vs x′ — `IC-TEXT`: U / ✓. Every other member: =. This is Type-H for `IC-TEXT`.
- Fact-boundary variant — `IC-FACTS` succeeds only when the crossing literal is a given fact.

**Pair types.**
- SC − NC is Type-H for `IC`: IC changes and g doesn't.
- BD − SC is Type-G for `IC`: g changes and IC still claims feasible with only cross violations.

**Metric.** Per cell:
- correctness and the feasibility claim;
- violation location (cross vs intra), and agreement with IC's exact violation set;
- trace codes: separate part blocks; reconciliation present?

**Pro thresholds** (levels on the §2.5a readouts π, lift, ΔELPD; restated as weight statements there) all of:
- SC − NC infeasible-answer rate ≥ 15pp, with ≥ 80% of violations on cross-links;
- BD answers claim feasibility with cross-only violations;
- traces show part blocks without reconciliation in ≥ 60% of SC failures;
- header-move x′ − x ≥ 10pp.

The clustered-vs-interleaved contrast decides between `IC-TEXT` and `IC-GRAPH`.

**Contra thresholds** (bounding competitor weight; §2.5a) SC ≈ NC (≤ 5pp), BD violations are intra-part as often as cross, and header-move ≤ 5pp.

**Generator spec.**
- **Parts.**
  - k = 2: Prüfer trees with BFS intro order.
  - k = 3: 2-trees grown by attaching each new vertex to both ends of a random existing edge, with the canonical colouring in construction order.
  - SAT: random 2/3-clause formulas, rejection-sampled until exactly 2 models (brute force at n = 8).
- **Cells.** Enumerate the candidate cross-link endpoint sets with matched intra-degrees, classify them into NC/SC/BD with the solver, and sample one per cell.
- **Robustness arm.** 20% of instances use non-unique parts, scored only on violation location.
- **Rejection.** Degree mismatch, solver disagreement, or FIRST-FIT predictions that coincide with IC in SC.
- **Yield.** ≥ 50% of part pairs admit all three cells at k = 3 (estimate; measure on dev).

**Size.**
- k = 3: 60 part-pairs × 3 cells × 2 renderings = 360.
- k = 2: 30 × 3 × 2 = 180.
- SAT: 50 × 3 × 2 = 300.
- Entailment: 80 pairs + 40 catch + 20 no-header = 220.
- Robustness: 60.

Total **1,120 items**.

**Power.** Paired SC vs NC: 60 pairs × 2 renderings × 3 samples ≈ 200 effective pairs, so a 10pp effect is detected with 80% power.

**Threats.**
- *Unique-colouring parts are special.* Covered by the robustness arm.
- *The canonical-labelling assumption.* Fall back to `IC-ALIGN`, and to the label-free "cross-only violations" signature.
- *Section headers may read as "separate questions".* That is the mechanism under test. The no-header controls bound it.

### 2.11 E6 — Process measures and DP cost (G `DP-EXACT`; trace re-analysis for B1)

**Question (H-G.2 and H-B1.5).**
- (a) Does trace cost follow the procedure the answers identified? Candidates:
  - `UP` / `FC`: cost ∝ derivable literals up to depth d, including fan-out;
  - `BC`: ∝ u;
  - `UP-PASS`: ∝ passes × N;
  - `NOISY`: ∝ s.
- (b) On knapsack, does trace cost scale with the DP state count \|L\| (`DP-LIST`), rather than with 2^n (enumeration) or n (greedy)? This is tested at matched answers for every non-DP heuristic.

**Design (a).** No new items: E1 and E2 traces, under BE-32k and under the 2k/8k budget factor. Prediction: k*(B) ≈ B / τ_step, with τ_step measured per model.

**Design (b): the R-dial.**
- n ∈ {16, 24} items with two-digit weights, and capacity ≈ 40% of the total weight.
- **high-R:** generic weights.
- **low-R:** weights drawn from 3 distinct values, each repeated, so \|L\| is about 20–80 against about 500–5,000 for high-R.
- Matched within each pair:
  - n, W, digit lengths;
  - the ratio order;
  - the answers and values of `RATIO`, `VALUE` and `LARGEST-FIT`;
  - the optimal-vs-greedy gap (±1);
  - the size of the LEX-optimal subset.

**Predictions.**

| Member | Tokens, low-R vs high-R | Accuracy under the 8k budget | Trace |
|---|---|---|---|
| `DP-LIST` | High-R ≥ 3× low-R | Low-R > high-R | (weight, value) tables growing item by item |
| `DP-ROUND(10)` | Similar to `DP-LIST` | Overshoot answers ≤ Σ residues | Rounded weights stated |
| Enumeration / B&B (D) | Equal (∝ 2^n, bounds) | Equal | Subsets listed; pruning |
| C `RATIO` / `VALUE` | Equal (∝ n log n) | Equal (outputs matched) | Sorting by ratio |
| F local search | Equal | Equal | Swaps |
| `EXACT` (any method) | — | Ceiling | — |

**Metric.**
- Log thinking tokens ~ log \|L\| + n + pair, as a mixed model.
- Count of "partial-sum" events, by regex on numbers.
- Accuracy under the 8k budget factor.

**Pro thresholds** (levels on the §2.5a readouts π, lift, ΔELPD; restated as weight statements there) tokens(high) / tokens(low) ≥ 2 and DP tables are present in ≥ 50% of traces. **Contra thresholds** (bounding competitor weight; §2.5a) the ratio is ≤ 1.2 (then DP gets no weight).

**Size.** 80 pairs per n, i.e. **320 items**.

**Power.** With a log-token SD of about 0.5, paired differences of 0.15 log-units are detectable.

**Threats.**
- *Duplicate weights may prompt grouping.* Grouping is itself DP-like; what is measured is cost ∝ \|L\|.
- *Verbose traces.* Use event counts rather than raw tokens.

### 2.12 Coverage: which eval can disconfirm which theory

Key:
- ● designed to disconfirm: an answer-level Type-H or Type-G contrast with a pre-registered threshold.
- ○ disconfirms through traces or process measures only.
- – cannot.

The worked sets in the question library realise the ● cells at dev size. Its per-set discrimination tables show which theories each set separates.

**This vertical's members (B1 and G).**

| Theory | E1 | E2 | E3 | E4 | E5 | E6 | The observation that disconfirms it |
|---|---|---|---|---|---|---|---|
| `UP-k` (finite k) | ● | ● | ● | – | ● | ○ | Accuracy tracks s or u rather than d; no step; no k growth with budget |
| `UP-∞` (fixpoint) | ● | ● | ● | – | ● | – | Errors on UP-derivable items (E1 deep cells), or successes on b* ≥ 1 items without case-branch traces |
| `UP-REFUTE` | ○ | ● | – | – | – | – | T2: b* = 0 items fail, or b* ≥ 1 items succeed |
| `FC-k` (MP only) | – | ● | ● | – | – | – | MT and DS succeed (E2-T4, T6); disjunctive phrasing has no effect (E3-O) |
| `UP-PASS-p` | ○ | – | ● | – | – | – | No proof-order effect, or one that doesn't grow with d (E3-P) |
| `RES-w` | ● | ● | – | – | – | – | T2 accuracy tracks b*, not w*; no derived disjunctions in traces |
| `PS(RECENT / FIRST)` | ○ | – | ● | – | ○ | – | No position main effect; the "unselected" premise is cited in traces |
| `PS(TYPE)` / `PS(SHORT)` | ● | ● | ● | – | – | – | Fan-in-2 items solved at d = 2 (E1); disjunctive phrasing has no effect (E3-O) |
| `PS(OVERLAP)` / `RADIUS` | – | – | ● | – | – | – | No overlap effect; query-first has no effect (E3-O/Q) |
| `2SAT-CORE` / `DROP(WIDE)` | – | – | – | ● | – | – | Violations not confined to width-3 clauses in the (2+p) arm |
| `DROP(LAST / FIRST / LONG)` | – | – | – | ● | ● | – | Violated-edge identity not predicted by list position or intro distance; low consistency; no relocation or pendant effect |
| `IC-TEXT` / `IC-GRAPH` | – | – | – | ○ | ● | – | SC ≈ NC; header-move null; BD violations inside parts |
| `IC-ALIGN` | – | – | – | – | ● | – | Failures in SC (`IC-ALIGN` predicts ✓) |
| `DP-LIST` / `DP-EXACT` | – | – | – | – | – | ● | Token cost and DP-table events invariant to R |
| `MST-TOUR` | – | – | – | ○ | – | – | Deferred: the routing extension of E4 (not in Phase 1) |

**Competitors and nulls.**

| Theory | E1 | E2 | E3 | E4 | E5 | E6 | The observation that disconfirms it |
|---|---|---|---|---|---|---|---|
| D `BC-b` | ● | – | ● | – | – | – | Ladder ≈ tree ≈ chain at matched d (E1); query position null (E3-Q); fan-out assertions in traces |
| D `FC-budget-b` | ● | – | – | – | – | – | No fan-out effect (E1 fan-out block) |
| D `DPLL-b` / enumeration | ○ | ● | – | ● | ● | ● | No case-branch traces; failures at small b* (E2); token cost tracks R, not 2^n (E6) |
| E `WP-t` | (≡ `UP-t`; the same function — not a separate theory) | | | | | | Disconfirmed with `UP-k` |
| E `BP-t` | – | ● | – | ○ | – | – | Flat T5 probability ladder |
| H `SAMPLE-m` | ● | ● | – | – | – | – | Depth effects on determined items (E1); flat T5 |
| B4 `FIRST` | – | ● | – | – | – | – | T2 sibling and T5 commission absent |
| B4 `BICONDITIONAL` / `CLOSED-WORLD` | ● | ● | ● | – | – | – | Catch and bait commission ≤ 5% |
| B4 `DROP-CONJUNCT` | ● | – | – | – | – | – | Missing-antecedent catch commission ≤ 5% |
| B4 `ETR` / `MM` | – | ● | – | – | – | – | T3 illusory commission ≤ 10%; MT success (`MM`-initial omits MT) |
| B4 `ADD-CONSTRAINT` | – | – | – | ● | ● | – | No false IMPOSSIBLE on feasible siblings |
| C `FIRST-FIT` / `DSATUR` | – | – | – | ● | ● | – | Violations not at the stuck vertex; they move with list order |
| C4 `ONLINE-STATE` | ○ | – | ● | – | – | – | No order effect; no memory-load effect |
| C `RATIO` / `VALUE` | – | – | – | – | – | ● | Answers differ from the greedy set; cost tracks R |
| F `MIN-CONFLICTS` | – | – | – | ● | ● | – | Cross-sample consistency ≥ 0.6; violations at predicted positions |
| A `NONE` | ● | ● | ● | – | – | – | Correct determinate answers at small d |
| A `FREQ` / `ATMOSPHERE` | ● | ● | ● | – | – | – | Answers flip with g across surface-matched siblings |
| A `DENSITY` / `CYCLIC` | – | – | – | ● | ● | – | Different decisions on density-matched siblings; violations not at i ≡ j (mod k) |
| Null `NOISY-EXACT` | ● | ● | ● | ● | ● | – | Size-independence at matched d (E1); position-locked, consistent violations (E4); clash-dependence (E5) |
| Null `PERCEPTION-NOISE` | ○ | – | ● | ● | ● | – | Echo recall ≥ 90% with violations persisting; pendant-last effect; consistency ≥ 0.6 (E4) |
| Null `RANDOM` | ● | ● | ● | ● | ● | ● | Any cell departing from uniform by > 15pp |
| Null `EXACT` (solves it) | ● | ● | ● | ● | ● | ○ | Any error rate above lapse on E1 deep cells, E2 T2 or E4 critical items. Only process evidence (E6) separates `EXACT` from `DP-EXACT`. |

**No theory is left undisconfirmable.** `WP-t` is the same function as `UP-t`, and `MST-TOUR` is out of Phase 1 scope.

---

## 3. Mechanistic evidence (Phase 2, only if behavioural evidence)

**Gate.** Phase 2 runs only if either of these holds in ≥ 2 models, in the pre-registered fits:
- E1/E2 put posterior ≥ 0.9 on a B1 member;
- E4/E5 meet their supported-if criteria.

**State variables.**

| Member | State variable |
|---|---|
| `UP-k` | derived[a] ∈ {T, F, ⊥}, and the round index d(a), for every atom |
| `PS` | active[π], whether premise π is in the selection |
| `DROP` / `IC` | edge-active[e] at the positions where the answer is decided, and part[v] |

Competitor variables are probed alongside, for comparison: BP marginals, goal-relevance anc_q(a), mention statistics, and window membership.

**Probes.**
- Linear probes for each variable, per layer, at three positions: consequent-premise positions, the query position, and the answer position.
- Held-out atom names. Hewitt & Liang control tasks (type-level random labels). A surface-feature baseline, and format residualisation (Sahoo et al. 2026).
- For thinking models, also at the trace tokens where a literal is asserted. Look-ahead = the depth beyond the current assertion that is already decodable; it estimates rounds per step.
- Prediction: the first decodable layer L*(d) rises with d, with a ceiling.

**Interventions.**
- Linear interchange interventions (DAS, Geiger et al. 2023) on derived[a], at the consequent position of a broken chain.
- **Structure-contingent prediction:** the answer flips only if the base item contains the rules from a to q.
- Controls, each of which must do worse:
  - the answer direction at the final position, which is not structure-contingent;
  - the competitors' variables;
  - norm-matched random directions (Cox et al. 2026);
  - the same fit on a random-init model, which must fail (Sutter et al. 2025).
- H5c, holds where wrong: patch the penultimate literal on d = k\* + 1 items, where the model omits. Prediction: rescue (cf. back-patching, Biran et al. 2024).
- For `DROP` / `IC`: edge-presence probes at the colour-decision positions. Prediction: the dropped edge is encoded at its mention but absent at the decision ("encoded, not used").

**Positive and negative controls.** The pipeline must pass these before any LLM claim (DESIGN §5.12):
- an ALTA-compiled `UP-k` (Shaw et al. 2025);
- InterpBench-style SIIT models of `UP-k`, `PS(RECENT)∘UP` and `BC-b` (Gupta et al. 2024);
- a Ye et al.-style capacity toy;
- random-init twins of each.

Pass criteria:
- the L*(d) slope is recovered to within 0.5 layer per round;
- DAS IIA ≥ 0.9 on the planted variable and ≤ 0.3 on random-init models;
- no misattribution between `UP-k`, `PS` and `BC`.

**Models.**
- Qwen3-14B (40 layers) vs Qwen3-32B (64 layers), which have the same width (5120), give a depth contrast. Transcoders exist for 14B.
- gpt-oss-20b, to match the Phase 1 primary model.
- DeepSeek-R1-Distill-Qwen-14B vs Qwen3-14B, for the effect of reasoning tuning.
- No models under 14B, per scope.

**Estimate.** About 20 person-days, plus about 150 GPU-hours, if the gate opens.

---

## 4. Evidence-table row

| Behavioural lift over baseline | Mixture weight | Signatures matched | Process match | Probe selectivity | Intervention vs competitor | Control recovered | RASP-L length / class |
|---|---|---|---|---|---|---|---|
| E1–E5: EA of the best B1/G member above the permutation baseline (pooled) | Shared engine on E1–E5 items | Out of 8: (i) depth not size; (ii) chance-polarity omissions; (iii) flat probability ladder; (iv) selector-predicted violation; (v) relocation / pendant; (vi) SC clash; (vii) header move; (viii) k\*(budget) | E6 plus the §2.4 trace channel (φ-weighted; F1–F3) | Phase 2 | Phase 2 | Phase 2 | §1.7: `UP-k` ≈ 6k + 7 lines, attention depth 2k + 3 (const for fixed k; seq at fixpoint) |

---

## 5. Build scope

**Built in this vertical (Phase 1).** The dev-tier prototypes of most components already exist as throwaway scripts used to verify the question library. Porting them is included in these estimates.

| Component | Contents | Person-days |
|---|---|---|
| Reference implementations | `UP-k/R`, `UP-PASS`, `UP-REFUTE`, `RES-w,k`, `PS(sel)` (6 selectors), `2SAT-CORE`, `DROP(sel)` (coloring and SAT), `IC-TEXT/GRAPH/ALIGN`, `MST-TOUR/WALK`, `DP-LIST/ROUND`. Property tests: soundness against z3 on 10k random items; monotone in k and w; `UP-k` order-invariant. | 7 |
| Generators | **E1:** cones, quotas, fan-out, catches, tiers, surface gate. **E2:** b\* / w\* computation, gadgets, minimal-edit siblings, PyETR import, probability bins. **E3:** matched swaps and paraphrases. **E4:** critical graphs, MUS extraction, D-optimal ordering search, siblings, pendant cells. **E5:** trees, 2-trees, 2-model SAT parts, cell enumeration, header moves. **E6:** R-dial matching. **All:** hardness-band calibration hooks and dev/test hashing. | 18 |
| Scorers | 3-way and list scoring with capability tags; chance-polarity index; extraction of violated constraints and their features; consistency κ; knapsack feasibility and value | 3 |
| Trace L0 parser | Vocabulary matcher; event tagger (ASSERT / GOAL / CASE / ASSIGN / CHECK / REVISE); feature extraction (τ_depth, τ_text, touched premises, unmentioned constraints, case depth, DP-table events). Validated on 200 hand-coded traces per domain. | 4 |
| Trace L1 coding | Coder prompts, chunking, blinding; a κ harness against human codes | 3 |
| Human trace labelling | 2 coders × 200 traces × 4 domains | 6 |
| Analysis | Latent-step k\* model; depth/size/unfolding mixed logit; edge-choice conditional logit; quad contrasts; process regressions; faithfulness tests F1–F4; the joint answer–trace likelihood; Bröder classification; planted-heuristic recovery for every member in §1.4 | 8 |
| Question library → test fixtures | Freeze the 42 verified items as regression tests for generators and scorers | 1 |
| **Total (Phase 1)** | | **50** (44 engineering + 6 labelling) |

**Shared infrastructure, not built here.**
- The content-addressed item store and manifests.
- The NL renderer and theme port from v1, with three-tokenizer length matching.
- The **minimal-edit counterfactual search** (edits plus a prediction-pattern predicate), which every vertical needs.
- Solver wrappers: z3 / PySMT; PySAT (not installed in the v1 venv), including MUS extraction; OR-Tools.
- The runner:
  - effort and budget control for gpt-oss, Qwen3 and R1;
  - budget forcing and censoring;
  - multi-sample runs;
  - raw thinking-trace capture.
- The parse / refusal / "declared impossible" taxonomy.
- The zoo registry, with competitor members from other verticals: `BC-b`, `FC-budget-b`, C4, `SAMPLE-m`, `BP-t`, `FIRST-FIT/DSATUR-cap`, `MIN-CONFLICTS`, `CYCLIC`, `ETR`/`MM`, and the nuisance models. If these are not ready, stubbing them here costs about 4 person-days.
- The mixture / likelihood engine, with permutation baselines.
- The fake-model recovery harness.
- The LLM-coder service and its κ tooling, if other verticals also code traces.

---

## 6. Compute budget

**How to read the table.**
- Counts are **per model**.
- "Avg output tokens" = thinking plus answer, under best effort (BE-32k). They are realistic averages for gpt-oss-20b at high effort; R1 and Qwen3-235B run 1–1.5× longer.
- Prompt tokens are measured on the dev-tier renderings and scaled to full-study N.
- `Dev` rows are the smallest set that exercises every cell: 5 items per cell (8 for E6), 1 sample, run first on gpt-oss-20b (high).

| Eval ID | Domain | # items | Conditions (e.g. direct, CoT-1k, CoT-4k) | Samples/item | Avg prompt tokens | Avg output tokens per condition | Needs activations? (Y/N) |
|---|---|---|---|---|---|---|---|
| E1 | Entailment | 2,300 | BE-32k (primary) | 3 | 2,000 (Tier L 1,700; XL 3,300) | BE-32k ≈ 6,000 (determined 4–6k; catches 6–9k; XL 8–12k); ≈ 2% truncated at 32k (XL catches) | N |
| E1-Dev | Entailment | 230 (23 cells × 2 versions × 5) | BE-32k | 1 | 2,000 | ≈ 6,000 | N |
| E2 | Entailment | 1,860 | BE-32k | 3 | 300 (T2 gadgets up to 600) | BE-32k ≈ 4,500 (T1/T3/T4/T6 1–2k; T2 b\* ≤ 2: 3–6k; b\* = 4–5: 15–30k); ≈ 5% truncated, concentrated in b\* = 5 (≈ 25% of that bin) | N |
| E2-Dev | Entailment | 145 (29 cells × 5) | BE-32k | 1 | 300 | ≈ 4,500 | N |
| E3 | Entailment | 750 | BE-32k | 3 | 1,500 | BE-32k ≈ 5,000; < 1% truncated | N |
| E3-Dev | Entailment | 75 (15 cells × 5) | BE-32k | 1 | 1,500 | ≈ 5,000 | N |
| E4 | Coloring + SAT | 1,220 | BE-32k | 3 | 850 (coloring 650; SAT 1,100) | BE-32k ≈ 16,000 (feasible siblings 6–10k; UNSAT n ≤ 16: 12–20k; UNSAT n ≥ 20 and SAT n = 20: often 32k); ≈ 20% truncated overall, ≈ 35% of UNSAT items with n ≥ 20 | N |
| E4-Dev | Coloring + SAT | 80 (16 cells × 5) | BE-32k | 1 | 850 | ≈ 16,000 | N |
| E4-echo | Coloring | 300 | Low effort (restate the conflict list) | 1 | 650 | ≈ 400 | N |
| E5 | Coloring + SAT + entailment | 1,120 | BE-32k | 3 | 700 (coloring 550; SAT 600; entailment 1,500) | BE-32k ≈ 8,000 (NC/SC 4–8k; BD 10–20k); ≈ 5% truncated (BD, k = 3) | N |
| E5-Dev | Coloring + SAT + entailment | 110 (22 cells × 5) | BE-32k | 1 | 700 | ≈ 8,000 | N |
| E6 | Knapsack | 320 | BE-32k | 3 | 400 | BE-32k ≈ 12,000 (low-R 5–8k; high-R 10–25k); ≈ 10% truncated (high-R, n = 24) | N |
| E6-Dev | Knapsack | 32 (4 cells × 8) | BE-32k | 1 | 400 | ≈ 12,000 | N |
| BUDGET (secondary) | Entailment (E1 600 + E2-T2 300) | 900 | Thinking caps 2k, 8k (32k = primary) | 3 | 1,500 | 2k cap ≈ 1,900 (most censored); 8k cap ≈ 5,500 | N |
| DIRECT (diagnostic) | Entailment (E1–E3) | 4,910 | Non-thinking / lowest effort, "answer immediately" | 1 | 1,300 | ≈ 15 | N |
| M (Phase 2, gated) | Entailment and coloring subsets | 2,000 | Forward passes over prompt + trace; residuals cached | 1 | 2,000 (+ trace up to 8k for step probes) | 0 (teacher-forced) | Y |

**Totals per model.**
- **Full Phase 1, primary:** 7,570 items; about 23,000 generations; about 25M prompt tokens and **about 175M output tokens**. E4 accounts for 33% of the output and E1 for 24%.
- **Secondary:** about 20M output tokens.
- **Dev batch:** 672 items, about **4.9M output tokens**. That is about 1 H100-hour on gpt-oss-20b.

**Across the planned models** (gpt-oss-20b / 120b; Qwen3-14B / 32B / 30B-A3B / 235B-A22B-Thinking; DeepSeek-R1; R1-Distill-Qwen-14B / 32B): about 1.6B output tokens.
- Rough cost: 500–600 H100-hours. DeepSeek-R1 alone is about 300.
- Recommendation: run R1 on a 30% subset stratified by cell.

**Truncation policy.** Forced answers are scored, but kept out of the main fits (§2.0). The hardness band is calibrated on dev so that the hardest cell is at 40–80% accuracy, which also keeps truncation below about 35% in any cell.

---

## 7. What would falsify these families' role

"Falsified" means a bound on weight, not a binary verdict: the §2.5a readouts put **π ≤ 0.1 (upper 95%)** on the family's members, with ΔELPD (or log₁₀ BF) favouring the named competitor by ≥ 1. The conditions below are the item-level patterns that drive those bounds.

**B1 as an account of entailment errors.** Any one of the following, pre-registered and judged on the pooled hierarchical fit:
1. **Commission dominates.** Errors beyond the frontier have systematic polarity (polarity accuracy deviates from 0.5 by ≥ 0.15 in the cue- or B4-predicted direction), and catch / bait commission is ≥ 15%. The errors are then B4 or A.
2. **Size, not depth, at best effort.** At matched d, the chain–tree gap is ≥ 20pp, and at matched s there is no ordering by depth. Then `NOISY-EXACT`, `FC-budget` or `BC` wins, and "rounds" fails.
3. **Case analysis present but abandoned.** On E2-T2 failures, traces show correct case branches that are left unfinished. The procedure is then D (truncated search), not relaxation.
4. **Probability-driven answers.** The T5 slope is ≥ 15pp per bin (E/H).
5. **No budget coupling.** k\* (or b̂) does not rise from the 2k to the 32k cap.
6. **The trace channel contradicts.** φ-weighted trace evidence favours a non-B1 member in ≥ 2 models. Then at most "answer-level B1" is claimed (§2.4), and the Process cell is ✗.

**B1 in search.** Falsified if all of these hold:
- violated-constraint identity is unpredictable (all |β| < 0.2);
- κ ≈ noise;
- the relocation and pendant contrasts are null;
- no SAT bias (feasibility claims on UNSAT ≈ false IMPOSSIBLE on siblings).

**G.** `IGNORE-CROSSLINKS` is falsified if SC ≈ NC (≤ 5pp), BD violations are not concentrated on cross-links, and the header move is null. `DP-EXACT` (as a process) is falsified if token cost and DP-table events are invariant to R.

**Outcomes that refine rather than falsify:**
- chain ≫ fan-in 2, with a log-shaped chain curve: favours `RES-2` / parallel reachability;
- an order effect growing with d: favours `UP-PASS` (B1) or C4, decided by memory load;
- position main effects: favour `PS(RECENT / FIRST)`;
- success at b\* = 0 but not at b\* ≥ 1: favours `UP-REFUTE`.

---

## 8. Open questions

1. **Merge `UP-k` and `WP-t`** into one zoo entry cross-listed under B1 and E? Recommend yes.
2. **Keep UNDETERMINED in the answer set** despite the aversion to "nothing follows"? Recommend keeping it, and relying on the chance-polarity index.
3. **Can b\* and w\* be decorrelated** in T2 at dev sizes? If not, `RES-w` vs `DPLL-b` rests on traces.
4. **Is `DROP(IMPLICIT)`** (constraints stated by a rule, e.g. "everyone on team X conflicts") a B1 heuristic or perception? Not budgeted.
5. **Should `DP-EXACT` stay in the answer-level zoo** at all, or only as a process model with `DP-ROUND`?
6. **H4 across domains.** Does a model's entailment soundness index predict its relaxation share in E4? Pre-register a correlation across models.
7. **Direct mode for always-thinking models** (R1, distills), with forced empty thinking, may be off-distribution. Should it be a separate condition label?
8. **Which coder model** for L1 trace codes? It must be a different family from the model being evaluated, and its κ must be reported per domain.

---

## Sources

Tags: [F], [B], [C], [A], [D] = repo literature reports; [DESIGN] = DESIGN.md; [V] = verified this session from the abstract page.

- Arcuschin et al. 2025, CoT in the wild is not always faithful [C]
- Ben-Sasson & Wigderson 1999, *Short Proofs are Narrow — Resolution made Simple*, ECCC TR99-022 [V]
- Bertolazzi, Gatt & Bernardi 2024 [B]
- Biran et al. 2024, *Hopping Too Late* [C]
- Bogdanov & Trevisan 2006 [F]
- Bröder & Schiffer 2003 [B]
- Chen et al. 2025, *Reasoning Models Don't Always Say What They Think* [C]
- Clark, Tafjord & Richardson 2020, *Transformers as Soft Reasoners over Language*, IJCAI, arXiv 2002.05867 (a depth-stratified rule-reasoning precedent) [V]
- Cox, Kianersi & Garriga-Alonso 2026 [C]
- Csordás, Manning & Potts 2025 [C]
- Eisape et al. 2024 [B]
- Geiger et al. 2023 (DAS) [C]
- Greenlaw, Hoover & Ruzzo 1991 compendium (unit resolution and Horn unit resolution P-complete) [F]
- Gupta et al. 2024 (InterpBench) [C]
- Hewitt & Liang 2019 [C]
- Kim, Valentino & Freitas 2025 [C]
- Monasson et al. 1999 ((2+p)-SAT; title-level) [F]
- Pearl 1983 [F]
- Saparov et al. 2025 [C]
- Sahoo et al. 2026 [C]
- Sato, Yamada & Kashima 2019 [F]
- Shaw et al. 2025 (ALTA) [C/D]
- Sutter et al. 2025 [C]
- Tafjord, Dalvi Mishra & Clark 2021, *ProofWriter*, Findings of ACL, arXiv 2012.13048 (iterated one-step implication) [V]
- Verma 2026 [A / DESIGN]
- Ye, Fu, Jia & Sharan 2025 [C]
- Zhang, Chen & Chen 2026 (models over-predict SAT) [A]
- Zhang et al. 2023 (*Paradox of Learning to Reason from Data*) [B]
- AlgoTrace (Lippl et al.) [B]
- Qwen3-14B / 32B layer counts and hidden sizes: HF `config.json` [V]
