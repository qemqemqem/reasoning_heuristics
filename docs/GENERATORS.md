# Generators: how to run them, and the item schema

The Stage 1 generators (SCOPE §5) live in `src/reasoning_heuristics/`. They build A/H E1, E2, E5, E8; C E1, E2, E3, E5; and B4/C4 E1, E2 item sets, at smoke (1 item per design cell) and dev (5 per cell) tiers, from disjoint seeds. Every ground truth and every prediction is computed by code and recomputed by the validators.

## Running

```bash
python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'

# one eval, one tier
.venv/bin/python -m reasoning_heuristics.generate --vertical C --eval E1 --tier dev --seed 1
.venv/bin/python -m reasoning_heuristics.generate --vertical B4 --eval E1 --tier smoke --seed 1 --set themes='["people"]'

# everything: smoke + dev for every eval, a test batch for the leakage check, review packets, summary
.venv/bin/python -m reasoning_heuristics.review

# tests
.venv/bin/python -m pytest -q
```

- `--vertical` takes `A/H` (alias `AH`), `C` or `B4/C4` (alias `B4`). `--per-cell N` overrides the items per cell. `--set key=value` passes a generator parameter (JSON values), e.g. sizes (`n=24`), depths, framings, or the theory arms below.
- Output: `data/items/<tier>/<V>_<E>_<tier>_s<seed>.jsonl` plus a `.report.json` with selection statistics and the validator report. The CLI exits non-zero if any item or set fails validation; the items are still written so the failure can be inspected.
- The committed form of each set is the deterministic `.jsonl.gz` copy that `review` writes next to it. Generation is deterministic in (code, tier, seed, parameters), so `review` rebuilds identical files.
- `review/<V>_<E>.md` renders five representative dev items per eval for human review; `review/summary.md` has item counts, cell coverage, validator pass rates and any failures.
- `scripts/review_page/build_review.py` builds the interactive review page (50 hand-picked dev items, four to six per eval, with keep / fix / drop and comments). The published page keeps marks in its artifact store, in the collections `reviews` (one document per item) and `generator_notes` (one per eval). Rebuild it after a generator changes.

## Tiers, seeds and splits

| Tier | Split | Base seeds | Items per cell |
|---|---|---|---|
| smoke | dev | [0, 10⁵) | 1 |
| dev | dev | [10⁵, 10⁶) | 5 (configurable 5–10) |
| test | test | [10⁶, 2·10⁶) | set by the study |

Every item records the seed of its base; every variant of a base inherits the base's seed and split. The validators check the seed against its tier's range, not only its split's. Test batches are written to the gitignored `data/items/test/` and are used here only for the leakage check.

Random streams come from `seeds.rng_for(seed, salt)`, which keys a stream on the first 8 bytes of the salt only ("AH-E1-SAT-critical" and "AH-E1-SAT-null" both key "AH-E1-SA"). The truncation is kept so existing items regenerate identically; `rng_for` raises if one seed is asked for with two salts that agree in their first 8 bytes, since they would share a stream. Give a new salt its own 8-byte prefix.

## The item schema

`src/reasoning_heuristics/schema/item.py` (dataclass) and `item.schema.json` (JSON Schema; every written item is validated against it).

| Field | Meaning |
|---|---|
| `item_id`, `vertical`, `eval_id`, `set_id`, `pair_id`, `cell` | Identity and design position. A *set* is one counterfactual set (e.g. the six isomorphic copies of a base); `pair_id` links designed pairs. |
| `domain`, `framing`, `prompt`, `answer_format` | What the model sees and how it must answer. |
| `ground_truth` | Standard keys (`chromatic_number` or `k`/`colourable`; `satisfiable`; `answer`/`follows`; `optimum`; `optimal_length`) plus eval-specific readouts. |
| `predictions` | `{label: {member, family, params, answer, trace_features, distribution}}`: enough to recompute every prediction. |
| `trace_predictions`, `hypotheses` | The pre-registered trace signature of each member and its computed trace features; the per-member eval and CoT predictions. |
| `disconfirms` | Log10 likelihood ratios by observed outcome (sign convention below). |
| `instance` | The structured task (instance + question context), so validators never parse prompts. |
| `params`, `notes`, `likelihood_model` | Design parameters, notes, and the likelihood model behind `disconfirms`. |
| `content_hash` | Hash of the logical content (instance + question), invariant to presentation. Whatever changes the answer is content: C E3's instructed first-fit question includes the listing order and the target. |
| `presentation_hash` | Hash of the exact prompt. |
| `base_hash` | Content hash of the base item its lineage starts from; used for splits and leakage. See the lineage rule below. |
| `source_hash` | Content hash of the item this one was manipulated from (`null` for a base item). |
| `seed`, `split`, `tier`, `generator`, `generator_version` | Provenance. |
| `extra` | `outcome_classes` (row label → class key), `channel` (its name) and `channel_spec` (everything needed to rebuild the channel, including each set-valued member's membership rule and set size), `likelihood` (ε, K, each member's kind); for converted library items, every field that did not map. |

**Lineage rules** (`validate/checks.py`, `LINEAGE_RULES`). Every generator follows them, and `run_checks` fails any violation (`KNOWN_LINEAGE_GAPS` is empty).

- A *base item* has `source_hash = null` and `base_hash` = its own `content_hash`.
- A *derived item* has `source_hash` = the `content_hash` of the item it was manipulated from, an item of the same set, and `base_hash` = its source's `base_hash`. In Stage 1 every variant is derived directly from its set's base item. Two examples: in C E3, CRITICAL and PLACEBO come from the BASE item of the same arm, and BASE/U-REV and BASE/I from BASE/U-LIST; in A/H E2 ENT, the other seven conclusions come from the first.
- Every item of one base carries the base's seed, split and tier.
- A set can hold several lineages. A matched control is a base of its own (C E5), and so is each inference's `cf` item in B4/C4 E2.
- **Items built from another eval's items.** An A/H E8 spec poses its host E2 item's task, so its content hash is the host's. Its `source_hash` is that hash (`params.host_item_id` names the host), and its `base_hash` is the host's.

**Entailment ground truth** follows the prompts: a conclusion follows when it "must be true whenever all the statements are true", so inconsistent premises would entail everything. No design intends them, and the validators flag any item whose stated premises are inconsistent.

**Likelihood-ratio sign convention (one for the repo):** `disconfirms[o][h] = log10 max_h' P(o|h') − log10 P(o|h)`. Positive = evidence against theory *h*; 0 = *h* is among the best-fitting theories for outcome *o*.

**The table is a uniform-slip preview.** It shows what each item can tell apart. The identification engine (`identify/`) computes its own likelihoods from raw answers, with near-miss slips and a fitted slip rate (SCOPE §6 rule 3). It does not read `disconfirms`. The preview is built in `generators/common.py` (`likelihood_table`):

- *Outcome classes* on the scoring channel:
  - every channel value a deterministic member predicts;
  - the channel's declared answers: both decisions on a decision channel; UNSAT / IMPOSSIBLE where the format allows them; same / different on the C E3 bit;
  - the solution of any set-valued member whose set has one element (it is deterministic there);
  - on a witness channel, the *unlisted* members of each solution set, as their own class (key `_in:<members>`, one per combination of sets);
  - other: not listed, and in no solution set.

  So an invalid answer never shares a class with a valid answer that no member listed.
- *Set-valued members* (EXACT, A/H E5's TT, uniform fills) carry a membership rule, its parameters and the set size. The rules (`colouring`, `assignment`, `subset`) are in `common.RULES`, and the scorer uses the same rules to classify answers. Examples: "proper colouring with exactly χ classes" (optimal), "at most k colours, keeping the fixed colours", "satisfying assignment of the stated / textbook formula", "optimal under the stated / textbook objective". A listed answer in the set gets 1/size, and the unlisted class gets the rest. On a non-witness channel the set's class counts give the probabilities (C E3: EXACT's share of colourings with the target matching the reference, counted exactly). Two sets on one item declare their overlap (A/H E5: identical under T and N, disjoint under I and I+R, counted under P).
- *Distributional members* use their own distributions, with each answer key mapped to its class. `_exact` mass is spread like EXACT, and an untracked Monte Carlo remainder (`_other`) goes to other.
- *Slip:* P(o|h) = (1 − ε)·p_h(o) + ε/K over the item's K classes, with ε = 0.1. A deterministic member therefore puts 1 − ε + ε/K on its own class. The same lapse formula holds for every kind of member: a deterministic member is the point-mass case of a distributional one, so the two get identical rows when they agree. The hypothesis texts quote the per-item numbers.
- *Every listed member has a row.* An answer with no reading on the channel is other (IMPOSSIBLE on the C E3 bit). A member with no prediction at all, or a set spec naming a member that isn't listed, is an error. The validator's `discriminates` check requires two members to differ on the channel and the table to be non-degenerate.

**Example libraries.** `python -m reasoning_heuristics.schema.convert` maps all six `data/examples/*.jsonl` libraries into the schema (`data/library/`, gitignored) and writes `data/library/CONVERSION_REPORT.md`, which lists every field that did not map. The libraries used three LR sign conventions; the converter unifies them.

## Package layout

| Path | Contents |
|---|---|
| `problems/{sat,coloring,entailment,knapsack,tsp}` | Instances with presentation orders, exact solvers paired with independent validator-path solvers, renderers |
| `heuristics/` | The zoo: one interface, `member(task, params) -> Prediction(answer, trace_features)`, a registry, and the composite `SEARCH(b, order, value, default)` |
| `counterfactual/` | Isomorphic copies and re-orderings, the minimal-edit search engine, surface matching |
| `validate/` | Ground truth twice (`truth.py`: the generator path; `independent.py`: the validator's own instance reading, stated-rule transforms and solvers, CaDiCaL rather than MiniSat, plus the readouts behind the likelihood tables); item, set, hash-collision, lineage and leakage checks (`checks.py`) |
| `generators/` | One module per eval; `common.py` assembles items, LR tables and hypotheses |
| `generate.py`, `review.py` | The CLI and the review/summary builder |
| `tokens.py`, `lexicon.py`, `seeds.py`, `hashing.py` | Tokenizer proxy, naming, tiers and seeds, canonical hashes |

**Tokenizer proxy.** Surface matching uses `regex-digit-split-v1` (`tokens.py`): each digit, letter run and punctuation mark is one token. Checks against the real panel tokenizers belong to the runner, before a pilot.

## Options from the theory notes (docs/theory/README.md §5)

All are generator parameters, not defaults:

- **Sizes** are parameters everywhere (`n`, `alpha`, depths, ...), so SAT can be centred on each model's budget line n\*.
- **C E3 gadget depth** up to 16 (`depths=[...]`, `d_max=...`).
- **Prompt given twice** (`repeat_prompt=true`) in the colouring, SAT and entailment renderers.
- **Adjacency list vs shuffled edge list** for colouring (`serialisation="adjacency" | "edge_list_shuffled"`).
- **Composite search member** `SEARCH(b, order, value, default)` in the zoo (`heuristics/search.py`).

## The Stage 1 generators

Each module's docstring states its design and every reading of the vertical doc it had to choose; the review packets (`review/<V>_<E>.md`) reproduce the docstring above five rendered dev items. In brief:

| Eval | Module | Cells | What is built | Not built (and why) |
|---|---|---|---|---|
| A/H E1 | `ah_e1` | 14 | Invariance pairs (x, x′): SAT polarity-preserving sign swaps (critical SAT→UNSAT and null pairs, CNF and menu framings, a B1 UP-refutable stratum), COL double-edge swaps (degree sequence fixed), ENT negation moves stratified by C's propagation depth. Cues, POLARITY and token multisets asserted equal within a pair. | — |
| A/H E2 | `ah_e2` | 24 | Satisfiability-neutral padding base/K/J/U for SAT (core n = 24, m = 101) and COL (K₃,₃,₃ / 27-edge tree / isolated people); matched ENT conclusions g × FREQ × ATMOSPHERE. | ENT matching omits the perception-fragility κ and PyETR counterbalancing (the ETR prediction is recorded on every item) |
| A/H E5 | `ah_e5` | 17 | Rule inversion T / N / I / I+R for COL (friend groups, complement graph), SAT (inverted clause rule, F ∧ F̄ UNSAT), KNAP (covering) and ENT (NOR reading); P (partial inversion) for SAT. N and I preambles equal in words. | P cells for COL, KNAP and ENT (the task types cannot express a partial inversion yet) |
| A/H E8 | `ah_e8` | 12 | Trace-faithfulness *specs* built from the E2 SAT K/J sets: early answering at f ∈ {0, .25, .5, .75}, transplants K→J and J→K, mistake insertion. `materialise(spec, response)` builds the continuation prompt once a model has answered. | Specs from E1, E5 and E6 responses |
| C E1 | `c_e1` | 12 | Isomorphic copies c1–c6 (natural, relabel, label answer order, random answer order, free, relist) for COL (n = 16) and SAT (n = 20), with every §2.8 filter (partition enumeration capped at 200k). | KNAP and TSP copies; the re-themed 20% and names variants |
| C E2 | `c_e2` | 40 | Edit-search cells BASE, D(h1\|h2), D(h2\|h1), PLACEBO, G-ONLY for COL (FF/DSATUR/LF), SAT (GREEDY vs UC, GREEDY vs POLARITY) and KNAP (RATIO vs DIFF, RATIO vs VALUE, PREFIX vs SKIP). | E2-KT tie psychophysics; E2-TSP; POLARITY vs JW/MOMS on mixed 2+3-SAT |
| C E3 | `c_e3` | 54 | Two-circuit NOR gadgets: depths {1, 2, 3, 4, 6, 8} (up to 16 by parameter) × BASE / CRITICAL / PLACEBO (same labelled graph, one adjacent swap) × arms U-LIST, U-REV, I. The gadget lemma is checked on every item; target bits balanced per depth; LOCAL-t proxy accuracies audited. | E3-SAT (gated by the doc); E3-NN |
| C E5 | `c_e5` | 17 | COL stuck 2 × 2 (vertex order × edge order) + control matched on n, m ± 1 and degree-order backtracking nodes; SAT dead-end / permuted / control; controlled partial states s1–s3 (SAT) and s1, s3 (COL); GREEDY-CM entailment order pairs with ETR predictions. | E5-P (a runner condition, not an item set) |
| B4/C4 E1 | `b4_e1` | 28 | Disjunction gadget P × O × T × F per frame (16 YN + 12 MC), abstract and people themes, lexicon partitioned 20/80 dev/test. | MC for N cells (see below) |
| B4/C4 E2 | `b4_e2` | 48 | Four-inference profile × order × five forms, plus the instruction factor; length-matched neutral note. | The causal-pair judge (no model calls) |

### Readings of the vertical docs worth a reviewer's attention

The full list is in the module docstrings. The ones that change what an item is:

- **B4/C4 E1, MC cells.** MC is built for T ∈ {M, U, V}. With the shared option set, N cells have two incomparable entailed options, so "the strongest entailed option" is undefined there; the doc tabulates MC for M cells only and the library has M and V.
- **B4/C4 E1, MC option order.** The options rotate in a Latin square across frames (rotation (frame + T) mod 4, "None of these" last). Within every MC cell the correct letter therefore cycles through A–D, balanced to ±1. All cells of one set share the rotation, so the O and P contrasts are not confounded with letter position. The doc's A2 `POSITION` member is not in the zoo yet.
- **B4/C4 E2, the note line.** The doc asks for notes within ±1 token; the library's neutral note is 11 proxy tokens shorter than the instruction. The default note is length-matched; `note_style="library"` reproduces the library.
- **B4/C4 C1 GREEDY-MODEL on "iff".** The doc's prose says DA = MT = 0 in both orders; executing its own §1.1 definition gives DA = YES and MT = X (cf) / YES (mf). The generators use the computed values (SCOPE §6 rule 5).
- **B4/C4 CW-COMP.** Completion applies to atom heads only, as §1.1 defines it ("each atom E that is a rule consequent"), so "if A then not B" is left as stated; this is what the library computed.
- **A/H E2, K negations.** "14 of 28 fresh literals negated" cannot hold with 3 pure variables at 8–10 occurrences each; K negates one variable's 10 slots and J negates the same slots.
- **A/H E5, k = 4 only.** With planted friend cliques, k = 3 is infeasible at n ∈ {10, 14}. The N preamble adds "who are" so its word count equals I's (the library's pair differed by 2 words).
- **C E1, token matching.** Copies are checked for equal token counts, not equal token multisets, because relabelling changes which labels repeat in neighbour lists. FF-OUT is omitted on the FREE copy c5 (it depends on the emitted order).
- **C E2, SAT density.** α ∈ {3.5, 4.0} by default: at α = 3.0 none of 30 measured bases had a reachable G-ONLY cell.
- **C E3, gadget size.** This construction gives n = 67, m = 113 at width 3 and D_max = 8 (the doc quotes 68 / 114; the extra vertex and edge are not identifiable from its description). n and m are identical across depths, as the design requires.
- **C E3, depth.** The cell's depth d counts gate layers. LOCAL-t-LIST counts rounds. It colours a vertex in the round equal to its first-fit dependency depth and gives it colour 1 otherwise. The inputs take one round, and an input listed after its pendant takes a second, so the target sits at first-fit depth D = d + 2 (d + 1 when every input in its cone is "True"). Gadgets are kept only when D = d + 2 in all three versions, and every item records `target_ff_depth`. The doc's recovery gate "d\* for LOCAL-t-LIST = t" holds with depth measured as D; in gate layers, d\* = t − 2. The listed proxies are LOCAL-(D−1), one round short (it answers the default), and LOCAL-D (= FF-LIST on the target). The proxy audit enforces chance accuracy for every proxy that can't see the target or its inputs: t < D when leftovers get colour 1, and t < D − 2 when they get their smallest free colour. Those proxies are constant on the target by construction, so the audit checks the balance. LOCAL-(D−2) with the free default is reported in the stats but not enforced. It reads the target off whichever inputs are already coloured, and at d = 1 it decodes the target exactly: a True input is coloured in round 1, a False one isn't. That is a finding for the doc's audit design.
- **C E3, I-arm members.** The instructed procedure *is* FF-LIST, so EXACT, an optimal colouring whose colour names are arbitrary, is not listed on the I arm. RANDOM (H) is listed on every arm; its channel probabilities are exact. Where FF's target colour is 1 (half the I-arm items, by the balancing), FF and the constant proxies coincide by construction; those items separate them only within their triple.
- **E8 items are specs.** They carry the host prompt, the source items' hashes, the cue values and the predictions that don't depend on a response (A2 DENSITY, A1 ALWAYS-UNSAT, C0 POLARITY). The continuation prompt can only be built from a model's own response. So can the trace-driven and D∘DENSITY predictions, which `materialise` computes:
  - on a transplant, trace-driven is the donor response's final answer, and D∘DENSITY is that answer, or the host's cue if the donor gave up;
  - on early answering and mistake insertion, the point prediction needs the trace replayed, which isn't built, so `materialise` returns the response's final answer.
- **C E5 give-up members.** Every part lists the A1 constant: ALWAYS-IMPOSSIBLE, ALWAYS-UNSAT, or NONE (always NO). So an IMPOSSIBLE answer on a STUCK item is no longer credited only to the members that abort at the dead end. On ENT items NONE equals EXACT.
- **Selection on members' behaviour (a design question).** Some §2.8 filters select bases on a named member's success or failure:
  - C E1-SAT needs GREEDY to satisfy in all three orders;
  - C E1-COL needs FF to use χ + 1 colours in some order;
  - C E5 needs FF-3 stuck, GREEDY and UC to dead-end, and GREEDY-CM to miss the countermodel.

  SCOPE §6 rule 6 says never select on one heuristic's errors. The filters are kept as the docs specify, and recorded on every item (`params.filters`) so analyses can condition on them.

**Zoo members.** Where a vertical doc is silent or contradicts itself, the reference implementation (`heuristics/`) reads it as follows:

- **SEARCH on a fewest-colours task is given k = χ.** D/F's colouring `DPLL-b` is a k-colouring search, so on "use as few colours as possible" items it runs at the true chromatic number, an oracle no reader has.
- **SEARCH skips unconstrained variables.** D/F's orders (MENTION, INDEX, MOMS; LIST, DSATUR, …) branch only on variables that occur in some clause and vertices that have an edge. Declared-but-unused variables and isolated vertices are filled by the value rule once every constraint holds, so they never cost budget: A/H E2's level U (unused declared variables, isolated people) predicts no change for D.
- **ONLINE-FF reads the edge stream.** It follows B4/C4's `ONLINE-FIRST-FIT`: a vertex is coloured when it first appears in the edge list, against the neighbours seen so far. At its first appearance a vertex has seen only one neighbour, so it never uses colour 3. C §1.1 says online first-fit *is* FF-LIST (a vertex-arrival model); that member is FF-LIST itself.
- **CW-MIN uses subset-minimal models.** B4/C4 §1.1 says "subset-minimal models (fewest true atoms)"; circumscription minimises by subset, and the parenthesis could be read as cardinality-minimal. The two differ when minimal models have different sizes.
- **PRIMACY / RECENCY on MC follow B4/C4.** They pick the option with the most literal overlap with the first / last premise, not A/H's "option at position 1 / K".
- **MATCH-A matches against every categorical premise.** B4/C4 §1.1 says "same as MATCH-L, any j ≠ i (order-invariant)". With several categorical premises, "the first such j" would depend on order, so MATCH-A (and MATCH-atom) keep the disjuncts that share a literal with any of them. A disjunction rewritten to one disjunct is not a categorical premise for the others (for MATCH-L that cannot arise).
- **Distributional members (RO-FF, RO-GREEDY): ε = ½.** C §1.2 asks for 10⁴ runs with add-ε smoothing and names no ε. Every observed outcome is kept, with P(o) = (n_o + ε)/(N + ε(K + 1)), and `_other` (every outcome no run produced) gets ε/(N + ε(K + 1)).
- **SAT PERCEPTION-NOISE flips each literal occurrence with p_f = 0.01.** A/H §1.5 says "flip one literal's sign w.p. p_f" with no default; the rate per literal read matches the entailment member's default.
- **UP-k with clashing facts.** B1's pseudocode assumes consistent facts. A unit clause that clashes with an earlier fact (or a fixed value) is not applied, so round 1 finds its clause falsified: UP-0 says SAT, UP-1 UNSAT.
- **WALK checks the k-th flip.** D/F's `WALK-k` loop checks before each flip; a run whose k-th flip satisfies the formula counts as a success.
- **"X" is a heuristic answer, not ground truth.** Members that reason exactly about the premises they are given (EXACT, TT, NOISY-EXACT's exact answer, BICOND-PRAG under the instruction, PERCEPTION-NOISE on its misread instance) use the ground truth's reading: inconsistent premises entail everything (`exact_answer`). A member whose own rewrite of consistent premises contradicts itself (FIRST, MATCH-*, BICOND, CW-COMP, CW-MIN, GREEDY-MODEL, strict ONL) answers X, B4/C4 §1.1's output for "the member's state is contradictory"; X maps to NO in two-way formats.

### Reference implementations

`heuristics/` registers every member under (domain, name) with its family and a one-line pre-registered trace signature. ETR members wrap PyETR 1.0.0 (`ETR-default`: `default_procedure_does_it_follow` for yes/no and `default_inference_procedure` for MC; `ETR-1p`: one pass, no reversed retry; renderings R1 and R2); the MC `output` text is put in canonical order, so it does not depend on the hash seed. Mental models (`MM-S1`, `MM-G`) are the simplified form the B4/C4 doc specifies, with premises conjoined by the system-1 rules (an implicit model meets an explicit one as null when the explicit one mentions an atom its conditional represents); the doc marks them as provisional until checked against mSentential. `SEARCH` is D/F's `DPLL-b` (SAT) and FC-BT (colouring), with b counting nodes = decisions + flipped re-assignments. Tests reproduce the B4/C4 E1 and E2 prediction tables and the C library's computed predictions, and check each member against an independent implementation of its pseudocode (`tests/test_zoo_*.py`).
