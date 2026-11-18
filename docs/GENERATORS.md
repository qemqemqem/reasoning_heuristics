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

Every item records the seed of its base; every variant of a base inherits the base's seed and split. Test batches are written to the gitignored `data/items/test/` and are used here only for the leakage check.

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
| `content_hash` | Hash of the logical content (instance + question), invariant to presentation. |
| `presentation_hash` | Hash of the exact prompt. |
| `base_hash` | Content hash of the base the set was built from; shared by all its variants; used for splits and leakage. |
| `source_hash` | Content hash of the item this one was manipulated from (`null` for a base item). |
| `seed`, `split`, `tier`, `generator`, `generator_version` | Provenance. |
| `extra` | Outcome-class map for `disconfirms`, and (for converted library items) every field that did not map. |

**Likelihood-ratio sign convention (one for the repo):** `disconfirms[o][h] = log10 max_h' P(o|h') − log10 P(o|h)`. Positive = evidence against theory *h*; 0 = *h* is among the best-fitting theories for outcome *o*. Outcome classes are the distinct answers of the deterministic members on the item's scoring channel plus "other"; deterministic members slip with ε = 0.1; distributional members use their own distributions; set-valued members (the exact solver on witness tasks, uniform fills) spread their mass over their solution sets.

**Example libraries.** `python -m reasoning_heuristics.schema.convert` maps all six `data/examples/*.jsonl` libraries into the schema (`data/library/`, gitignored) and writes `data/library/CONVERSION_REPORT.md`, which lists every field that did not map. The libraries used three LR sign conventions; the converter unifies them.

## Package layout

| Path | Contents |
|---|---|
| `problems/{sat,coloring,entailment,knapsack,tsp}` | Instances with presentation orders, exact solvers paired with independent validator-path solvers, renderers |
| `heuristics/` | The zoo: one interface, `member(task, params) -> Prediction(answer, trace_features)`, a registry, and the composite `SEARCH(b, order, value, default)` |
| `counterfactual/` | Isomorphic copies and re-orderings, the minimal-edit search engine, surface matching |
| `validate/` | Independent ground truth; item, set and leakage checks |
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
- **B4/C4 E2, the note line.** The doc asks for notes within ±1 token; the library's neutral note is 11 proxy tokens shorter than the instruction. The default note is length-matched; `note_style="library"` reproduces the library.
- **B4/C4 C1 GREEDY-MODEL on "iff".** The doc's prose says DA = MT = 0 in both orders; executing its own §1.1 definition gives DA = YES and MT = X (cf) / YES (mf). The generators use the computed values (SCOPE §6 rule 5).
- **B4/C4 CW-COMP.** Completion applies to atom heads only, as §1.1 defines it ("each atom E that is a rule consequent"), so "if A then not B" is left as stated; this is what the library computed.
- **A/H E2, K negations.** "14 of 28 fresh literals negated" cannot hold with 3 pure variables at 8–10 occurrences each; K negates one variable's 10 slots and J negates the same slots.
- **A/H E5, k = 4 only.** With planted friend cliques, k = 3 is infeasible at n ∈ {10, 14}. The N preamble adds "who are" so its word count equals I's (the library's pair differed by 2 words).
- **C E1, token matching.** Copies are checked for equal token counts, not equal token multisets, because relabelling changes which labels repeat in neighbour lists. FF-OUT is omitted on the FREE copy c5 (it depends on the emitted order).
- **C E2, SAT density.** α ∈ {3.5, 4.0} by default: at α = 3.0 none of 30 measured bases had a reachable G-ONLY cell.
- **C E3, gadget size.** This construction gives n = 67, m = 113 at width 3 and D_max = 8 (the doc quotes 68 / 114; the extra vertex and edge are not identifiable from its description). n and m are identical across depths, as the design requires.
- **E8 items are specs.** They carry the host prompt, the source items' hashes, the cue values and the member predictions; the continuation prompt can only be built from a model's own response.

### Reference implementations

`heuristics/` registers every member under (domain, name) with its family and a one-line pre-registered trace signature. ETR members wrap PyETR 1.0.0 (`ETR-default`: `default_procedure_does_it_follow` for yes/no and `default_inference_procedure` for MC; `ETR-1p`: one pass, no reversed retry; renderings R1 and R2). Mental models (`MM-S1`, `MM-G`) are the simplified form the B4/C4 doc specifies, marked there as provisional until checked against mSentential. Tests reproduce the B4/C4 E1 and E2 prediction tables and the C library's computed predictions.
