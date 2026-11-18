# Scope and Cost: Phase 1 (behavioural evals)

*Written 2026-11-13 from the six eval-design verticals in [verticals/](verticals/). Prices are OpenRouter list prices fetched the same day.*

## Bottom line

- **Phase 1 is behavioural only.** It runs on open-weight thinking models at best effort (high reasoning effort, 32k-token cap), starting with gpt-oss-20b, mostly through OpenRouter. Mechanistic interpretability is Phase 2, only for families that get behavioural weight.
- **Iteration is cheap:**
  - one dev pass over all seven verticals on gpt-oss-20b costs about **$8** (the cross-formalism vertical adds $0.29);
  - a pilot at 10% of full size on gpt-oss-20b plus Qwen3-32B costs about **$45**.
- **The full study as the verticals specify it is expensive.** About 1.03B output tokens per model; running every model of the ladder costs about **$7,800**. The recommended plan is **~$2,300**: full study on four cheap core models and the core tier on the two large ones. A lean version, with items cut to pilot-based power, is **~$1,200**. Running only gpt-oss-20b is **~$120**.
- **The engineering is the real cost.** The design agents' human-equivalent estimate is about **350 person-days**: ~35 shared infrastructure, ~255 vertical-specific, ~60 trace annotation. AI agents can write most of the generators and reference implementations. Human time goes into review, decisions and hand-labelling traces. Staging (below) gets a first result from about a third of that.

## Budget target: real results for under $100

Andrew's target (2026-11-13): preliminary results for well under $100, real results for $100 or less, and more spending only if those look good.

| Stage | What | Cost |
|-------|------|------|
| **Preliminary** | Dev batches for all six verticals on gpt-oss-20b (~5,700 items, 58M output tokens; ~$8 per pass), a second pass after fixes, and optionally the first three verticals' dev batches on gpt-oss-120b (batch, ~$5) | **≈ $15–20** |
| **Real results** | Core evals of the six original verticals: gpt-oss-20b (batch) at ~40% of the full design (~$48), gpt-oss-120b (batch) on the same items at ~25% (~$36); the cross-formalism core on gpt-oss-20b (~$6); LLM trace coding of a 20% sample (~$5) | **≈ $95** |
| If good | Cross-formalism core on gpt-oss-120b (~$7); Qwen3-32B and Qwen3-14B (cross-family check; ~$70 each at 25%), then R1 and Qwen3-235B on the core sets, up to the recommended plan below (~$2,300) | $300+ |

**Knobs that make $95 enough:**
- best-effort condition only (budget-sweep arms only where a design needs them);
- one sample per item, with repeats on a 10% subset;
- batch endpoints;
- item counts set by the pilot's effect sizes rather than worst-case power.

**What this costs in precision.** At ~40% of the specified items, weight intervals are about 1.5× wider than the full design. Detection limits move from roughly 0.03–0.06 to roughly 0.05–0.09. (The 20b share was cut from ~45% to make room for the cross-formalism vertical; its core tier detects a home-advantage shift of 0.05 with 85% power.) That is enough to see a standout family. The result is an evidence table for two sizes of one model family (20B vs 120B).

Recovery tests on fake models are free and run first.

---

## 1. Models and conditions

**Primary condition:** open-weight thinking models at best effort (high reasoning effort, 32k cap). Direct-answer and low-budget runs are diagnostic only, used where a design needs them (the depth-stress gadgets, single-pass locality tests). No tiny models.

| Model (OpenRouter) | $/M in | $/M out | Role |
|--------------------|--------|---------|------|
| gpt-oss-20b, high effort | 0.03 (batch 0.024) | 0.13 (batch 0.112) | **First model**; dev, pilot and full |
| Qwen3-14B, thinking | 0.12 | 0.24 | Core (Qwen3 size ladder) |
| Qwen3-32B, thinking | 0.08 | 0.28 | Core (Qwen3 size ladder); pilot partner |
| gpt-oss-120b, high effort | 0.15 (batch 0.03) | 0.60 (batch 0.136) | Core (gpt-oss size ladder) |
| Qwen3-30B-A3B, thinking | 0.12 | 0.50 | Optional (mixture-of-experts contrast) |
| DeepSeek-R1-0528 | 0.50 | 2.15 | Large; core tier only |
| Qwen3-235B-A22B-thinking | 0.45 | 3.50 | Large; core tier only |

**Before any pilot:**

- **Check that each model and provider actually returns the reasoning text.** Trace hypotheses are useless without it.
- **Pin the provider and precision** (OpenRouter provider routing). Quantised serving could change behaviour relative to the weights we would inspect in Phase 2.

---

## 2. Run tiers

| Tier | What | Models | Output tokens | Cost |
|------|------|--------|---------------|------|
| 0. Smoke | 1 item per design cell, per eval | gpt-oss-20b | ~1M | < $1 |
| 1. Dev batch | 5–10 items per cell, per eval; all six verticals ≈ 5,700 items | gpt-oss-20b | ~58M | **~$8 per full pass** |
| 2. Pilot | ~10% of full size | gpt-oss-20b + Qwen3-32B | ~100M each | **~$45** |
| 3. Full study | Pre-registered sizes | Plan below | ~1.03B per model | see §3 |

The infrastructure that keeps iteration cheap and honest:

- a response cache keyed on (model, provider, parameters, prompt hash);
- a cost estimate and hard cap before every run;
- batch endpoints for Tiers 2–3;
- dev and test items from disjoint seeds, so prompts are never tuned on the test items.

---

## 3. Full-study cost

**Volumes as specified by the verticals**, best effort, per model:

| Vertical | Items per model | Output tokens per model | Dev-batch tokens | Person-days (vertical-specific) | Phase 2 (if triggered) |
|----------|-----------------|-------------------------|------------------|----------------------------------|------------------------|
| A, H, nuisance, I: baselines | ~18,350 (+3,600 shared sweep) | ~290M | 16.5M | ~55 | ~15 |
| B1, G: relax / decompose | ~7,570 | ~175M | 4.9M | ~38 | ~20 |
| C: constructive / greedy | ~10,960 | ~159M | 13M | ~40 | ~19 |
| B4, C4: restrict / online (ETR) | ~12,400 | ~133M | 4M | ~53 | [TODO] |
| D, F: truncated and local search | ~3,500 | ~144M | 6.5M | ~37 | [TODO] |
| E: message passing | ~15,700 | ~125M | 13M | ~32 | ~25 |
| **Total (six original verticals)** | **~68,000** | **~1.03B** | **~58M** | **~255** | **~80–100** |
| I: cross-formalism (added later) | ~11,500 (core ~5,740) | ~104M (core ~52M) | 2.8M | ~19 (incl. 4 annotation) | ~10 |
| **Total, all seven** | **~79,500** | **~1.13B** | **~61M** | **~274** | **~90–110** |

Prompt tokens are taken as about 15% of output tokens, which matches the B1/G vertical's estimate.

**Cost per model** (full study / core tier ≈ 50% of tokens; six original verticals. The cross-formalism vertical adds $12 / $6 on gpt-oss-20b and $14.6 / $7.3 on gpt-oss-120b, and about 10% for the other models):

| Model | Full study | Core tier only |
|-------|------------|----------------|
| gpt-oss-20b (batch) | $119 | $60 |
| gpt-oss-120b (batch) | $144 | $73 |
| Qwen3-14B | $265 | $134 |
| Qwen3-32B | $300 | $151 |
| Qwen3-30B-A3B | $531 | $268 |
| DeepSeek-R1-0528 | $2,283 | $1,153 |
| Qwen3-235B-A22B-thinking | $3,660 | $1,848 |

**Plans.**

| Plan | Models | Cost |
|------|--------|------|
| Everything | All 7 models, full study, list prices | ~$7,800 |
| **Recommended** | Full study on gpt-oss-20b, gpt-oss-120b (batch), Qwen3-14B and Qwen3-32B; R1 and Qwen3-235B on half the core tier | **~$2,300** |
| Lean | As recommended, with item counts halved by pilot-based power analysis | ~$1,200 |
| Start small | gpt-oss-20b only, full study | ~$120 |

**Trace coding.** An LLM coder reads the traces. For the four core models that is about 1B input tokens: about $30 with gpt-oss-120b (batch), about $140 with Qwen3-235B-instruct. Coder validation against hand labels is human time; see §4.

**Why the full study is large.** Every vertical sized its evals to detect small weights, π ≈ 0.03–0.15, with worst-case power. The pilot's effect sizes will tell us how much of that is needed. Halving the item counts is a reasonable prior.

---

## 4. Engineering scope

**Shared infrastructure, built once (~35 person-days).**

1. **Runner:**
   - an OpenRouter client with reasoning parameters, provider pinning and batch support;
   - the response cache and cost guard;
   - run manifests.
2. **Item schema:**
   - one JSONL schema for all verticals, plus a converter for the six example libraries, whose extra fields currently differ;
   - content hashes, with each manipulated item storing its source hash;
   - split management.
3. **Heuristic framework:** reference implementations behind one interface (instance → answer plus trace features). Family members are parameterised (`PRIORITY(order, score, rule)`, `SEARCH(b, …)`, …) as report F suggests.
4. **Identification engine:**
   - likelihoods with a near-miss slip model;
   - the mixture with feature-dependent weights;
   - permutation baselines;
   - the hierarchical fit;
   - censoring for capped runs.
5. **Recovery harness.** Fake models plant graded mixtures (100%, 60/30/10, feature-dependent, nulls, an off-zoo procedure). It must pass three gates before any LLM fit: |bias| ≤ 0.05, 95% coverage ≥ 0.9, median interval width ≤ 0.2.
6. **Trace pipeline:**
   - a shared codebook;
   - automatic parsers (assignment order, decisions and backtracks, repairs, disjunct commitments);
   - an LLM coder;
   - a hand-labelling tool, with agreement gates (κ ≥ 0.7);
   - faithfulness probes (early answering, trace edits) whose results set how much weight trace evidence gets.
7. **Counterfactual tooling:**
   - edit search (find a single edit that changes one heuristic's output but not its rival's);
   - order and isomorphic-copy machinery;
   - surface matching (length, names, tokenisation).
8. **Shared sweeps:** the α × n random 3-SAT sweep used by the baselines and search verticals.

**Per vertical.** Each needs generators that implement its spec, reference implementations of its members, its eval-specific analysis, and its dev-batch calibration. About 255 person-days in total (table above).

**Trace annotation.** About 60 annotator-days across the verticals. A shared codebook should cut that.

**What AI agents can and can't do here.** Agents can write most of the generators, reference implementations and analysis code. During design they already wrote verifiers that caught several errors in hand reasoning. Human time goes into:

- reviewing designs and pre-registrations;
- hand-labelling traces for coder validation;
- judging ETR variants with the v1 co-authors;
- the go / no-go decisions.

---

## 5. Recommended build order

| Stage | Scope | Gate to continue |
|-------|-------|------------------|
| **0. Shared infra** | Runner, schema, heuristic framework, identification engine, recovery harness, trace pipeline (§4, items 1–6) | Recovery gates pass on fake models |
| **1. First verticals** | Baselines core tier (A/H: E1, E2, E5, E8), C greedy (E1–E3, E5), B4/C4 E1–E2 | Smoke → dev on gpt-oss-20b → size calibration → pilot (gpt-oss-20b + Qwen3-32B) → power analysis |
| **2. Remaining verticals** | B1/G, D/F, E, and I cross-formalism (reuses C and B4/C4 members and renderers; its E1 and E4 dev batches, ≈ $0.15, can run in Stage 1): dev → pilot | Same |
| **3. Full study** | Pre-registered; recommended or lean plan | Pre-registration committed before data |
| **Phase 2 gate** | Interpretability for families whose π lower bound ≥ [TODO, e.g. 0.15] on ≥ 2 models | — |

Stage 1 gives a first evidence table, covering baselines, greedy and cognitive restriction, for about a third of the engineering and well under $100 of inference.

---

## 6. Rules for every vertical

These came up independently in several verticals; adopt them everywhere.

1. **Size calibration.** Best-effort models may sit at ceiling. Calibrate instance sizes on the dev split so gpt-oss-20b scores 40–80% on the hardest cell, then freeze. Re-centre per model only by a pre-registered rule.
2. **Truncation is censoring.** At the 32k cap, expect 20–60% of runs on hard cells to be cut off (estimates from the C, D/F and E verticals). Model them as censored observations and report the truncation rate per cell.
3. **The noise model is pre-registered.** In the C vertical's recovery simulation, a uniform slip model biased the weights of diffuse theories (exact solver, local search) by up to 0.13, and their intervals under-covered. Near-miss slips with a separately estimated slip rate fixed most of this.
4. **Traces are down-weighted evidence:**
   - validated coding (κ ≥ 0.7);
   - faithfulness measured per model by early answering and trace edits, and used as the weight on trace evidence;
   - an answer-only analysis always reported alongside.
5. **Compute everything.** Every ground truth and heuristic prediction is computed by code. Hand reasoning was wrong several times during design:
   - backdoors of size ≥ 3 can't be planted in pure 3-CNF;
   - BP over-amplifies along chains of 2-clause equivalences;
   - E6's original specification accepted no items in 200k tries;
   - and others.
6. **Identification hygiene:**
   - content hashes, with manipulated items joined to their sources on hashes;
   - dev and test splits from disjoint seeds;
   - items selected on disagreement among all members, never on one heuristic's errors.
7. **ETR is several procedures.** The yes/no and what-follows modes, the conditional renderings and the issue-structure mapping are separate pre-registered members. Ask the v1 co-authors which ones represent the theory.
8. **Compute predictions per encoding.** Every member's prediction is computed on every encoding of an item; predictions transported through a reduction are flagged; slip rates are estimated per encoding.

---

## 7. Known weak separations

| Pair | What separates them | Risk |
|------|---------------------|------|
| Greedy (C) vs backtracking search (D) | Dead-end items (C E5, D E4); traces | Identical wherever greedy succeeds |
| `DPLL-b` vs `NOISY-EXACT` | Budget interactions (D E1–E3) | Only works if forced caps act like real budgets |
| Exact solver vs local search | C E4/E5, D E6/E7, traces | Up to ~0.15 of weight can sit on the wrong one |
| Message passing (E) vs `UP-k` (B1) | Soft-signal sets (E E2, E5), E6b | Hard-propagation items can't separate them |
| `FIRST` / `MATCH` / `ETR` | B4/C4 E1 permutation pairs | Some pairs tied within a set |
| C1 SAT greedy vs "always impossible" | C-vertical SAT items | Identical on B4/C4's SAT instances |
| Density cue vs real hardness | A/H E2 padding only | Padding variables are atypical; models may notice |
| `NOISY-EXACT` (weakest-resolved overall) | A/H E7, D E1 | Smallest detectable weight ≈ 0.13 (local search ≈ 0.24) |
| H-structure vs H-translate (cross-formalism) | I E3 translation dial; traces | Identical in answers if the model always translates |
| B4 collapse vs `ALWAYS-NO` on colouring rendered as logic | Traces only | The logic-native restrictions say "inconsistent" on every colourable graph |
| First-fit vs unit-propagation-first vs DPLL in listing order | I E4 dead-end cells; traces | Same first colouring wherever they succeed |

---

## 8. Phase 2 (only if behavioural evidence)

**Effort:** ~80–100 person-days if every family qualified, much less in practice.

**Compute:** self-hosted open models (Qwen3-14B, Llama-3.1-8B, Gemma 3, gpt-oss-20b) on rented GPUs. RunPod H100 on demand costs $2.69–4.39/hr. A rough envelope is 200–600 H100-hours per model family: ~$600–$2,600. To be refined from the verticals' Phase 2 sections once the families are known.

## 9. Decisions for Andrew

1. Recommended (~$2.3k) vs lean (~$1.2k) full-study plan. This can be decided after the pilot.
2. Stage 1 verticals as proposed: baselines, greedy, ETR / restriction?
3. The Phase 2 gate threshold: the π lower bound, and on how many models.
4. Who hand-labels traces, and whether to involve the v1 co-authors for the ETR variants.
