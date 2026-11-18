# The runner and the scorer

The runner sends items to models through OpenRouter and keeps every response. The scorer turns each response into an answer in the members' representation, with a category, validity, correctness and the item's outcome class. This is SCOPE §4 item 1 plus the scoring path (DESIGN §5 rules 3–5, 10, 11). The code is in `src/reasoning_heuristics/evals/`.

| Module | What it does |
|---|---|
| `run.py` | CLI: dry-run estimate, capped and cached live calls, raw outputs, then scoring, report, manifest and ledger |
| `score.py` | CLI: re-score runs from their raw outputs on disk |
| `force.py` | CLI: forced final answers for responses cut at the cap ([below](#forced-final-answers-at-the-cap)) |
| `scoring.py` | The one versioned scorer (`SCORER_VERSION`) |
| `client.py` | OpenRouter chat completions (and raw text completions for `force.py`): retries with backoff, long timeouts, full response capture |
| `cache.py` | Response cache keyed on the request body (model, provider routing, parameters, messages) plus the sample index |
| `cost.py` | Dry-run estimates and the `CostGuard` hard cap |
| `models.py` | Model configs, the thinking and direct conditions, the exact request body |
| `manifest.py`, `ledger.py`, `report.py` | Run manifests, `data/runs/LEDGER.md`, `REPORT.md` |
| `probe.py` | Provider probes: reasoning text returned, thinking off honoured, quantization |

## Running

```bash
# cost estimate only: no network, writes nothing (--tokens-from prices it from a run's measured tokens)
python -m reasoning_heuristics.evals.run --items data/items/smoke --model openai/gpt-oss-20b --effort high \
    --out data/runs/<run_id> --exclude-eval E8 --dry-run [--tokens-from data/runs/<earlier run>]

# live run (the key comes from the environment; never put it on the command line)
set -a; . ./keys.env; set +a          # keys.env holds OPENROUTER_API_KEY=...; it is gitignored
python -m reasoning_heuristics.evals.run --items data/items/smoke --model openai/gpt-oss-20b --effort high \
    --cap-usd 2 --out data/runs/<run_id> --exclude-eval E8 [--budget-tag T --budget-usd 3]

# direct condition (thinking off; Qwen3 hybrids only)
python -m reasoning_heuristics.evals.run --items data/items/smoke --model qwen/qwen3-32b --condition direct \
    --cap-usd 0.2 --out data/runs/<run_id> --exclude-eval E8

# re-score from raw outputs after any scorer change
python -m reasoning_heuristics.evals.score data/runs/*/

# after the item sets are regenerated: score against the item files as they were at each run's git SHA
python -m reasoning_heuristics.evals.score --items-at-run-sha data/runs/*/

# provider probes (tiny calls; results under data/runs/probes/)
python -m reasoning_heuristics.evals.probe --model qwen/qwen3-32b --out data/runs/probes/<date> --cap-usd 0.25
```

- **The key** is read from `OPENROUTER_API_KEY` inside each request and is never stored, printed, logged or written. A test greps every output file for it.
- **Provider pinning.** A live run refuses a model with no pinned provider (SCOPE §1), unless you pass `--provider <slug>` (sent as `order: [slug]`, `allow_fallbacks: false`, `require_parameters: true`) or `--no-pin`. Pins and the pinned endpoint's prices live in `models.py`; they come from the probes.
- **Resuming.** Re-running into the same `--out` sends only the (item, sample) pairs that have no response yet. The manifest keeps every earlier invocation (git SHA, times, status, spend) under `previous_invocations` and the total charge in `charged_usd_all_invocations`. It refuses a resume with a different condition or item set.
- **Re-scoring after the items change.** `score` refuses a run whose item files no longer hash to its manifest. `--items-at-run-sha` reads each file with `git show <run's SHA>:<path>` and checks it against the manifest's SHA-256 (`--items-ref <ref>` picks another ref). PRs merge with merge commits, so a run made at a pushed branch commit stays re-scorable after the merge.
- **The cache** (`data/cache/openrouter/`, gitignored) means an identical request is never paid for twice, across runs. Repeat samples are separate keys. The permanent copy is each run's `raw.jsonl.gz`; `ResponseCache.import_runs` rebuilds a cache from those.
- **Concurrency** defaults to 8. Timeouts are 30 minutes per request. Retries: 6 attempts with exponential backoff and jitter (honouring `Retry-After`). They cover network errors (including a dropped connection or a body cut short), 408/409/425/429/5xx, and errors inside a 200 body. 400/401/402/403/404/413/422 stop the run at once.
- **E8 is skipped** (`--exclude-eval E8`; the loader also refuses E8 specs). See [E8](#e8-continuations-and-prefill) below.

## Conditions

Decision record: [decisions/2026-11-17-direct-answer-arm.md](decisions/2026-11-17-direct-answer-arm.md).

| | thinking (primary) | direct (secondary) |
|---|---|---|
| Reasoning | on: `{"effort": "high"}` for every model (`--effort` changes it; `enabled: true` alone would mean medium effort) | off: `{"enabled": false}` (what each provider honours is a probe result) |
| max_tokens | 32,768 (reasoning + answer) | 1,024 |
| Messages | the item prompt as the only user message | a system message, then the item prompt |
| System instruction | none | "Respond with only the final answer in the requested format. Do not explain or show your working." |
| Sampling | each model's recommended thinking settings (gpt-oss: temperature 1.0, top_p 1.0; Qwen3: 0.6 / 0.95 / top_k 20; R1: 0.6 / 0.95) | Qwen3 non-thinking settings: 0.7 / 0.8 / top_k 20 |

- **gpt-oss cannot turn reasoning off.** It has no direct condition; the runner refuses one. `--effort low` is a budget arm of the thinking condition, labelled `thinking-low`.
- **The budget notice** (`--budget-notice`; Andrew's suggestion, 2026-11-18) is a variant of the thinking condition, labelled `thinking-<effort>+budget`. The user message ends with: "You have a budget of 32,768 tokens for your reasoning and your answer together. If you reach it before you have answered, your reasoning will be cut off and you will have to give your final answer straight away." That is `BUDGET_NOTICE` in evals/models.py, with the condition's max_tokens. Nothing else in the request changes.
  - Pair it with `force.py`, which gives the responses cut at the cap their final answer.
  - The analysis (`RUN_PATTERNS`) does not know the variant, so name such runs `2026-11-18-budget-<tier>-…` to keep them out.
- **The system instruction is an experimental factor.** Its exact text is in every manifest (`condition.system_prompt`) and in every raw request.
- **`pre_answer_tokens`** (proxy tokens of visible text before the final answer block) is on every scored record, so direct responses that work in the visible output can be flagged or excluded.

## What a run writes

`data/runs/<run_id>/`, kept permanently and committed (`.gitignore` ignores only `data/items/**/*.jsonl` and the cache):

| File | Contents |
|---|---|
| `manifest.json` | run id; status and stop reason; start and finish times; model requested and `models_returned`; `system_fingerprints`; provider routing sent and `providers_served`; the full condition (reasoning, sampling, max_tokens, system prompt); prices; item files with SHA-256, item count, skipped items; the dry-run estimate; cap, budget and spend (`spend.spent_usd` is API-reported, including `failed_attempt_cost_usd`); the key's own usage counter before and after (`key_usage`, numbers only; other users of the key move it too, so its delta is an upper bound, and it lags the API's own cost reports by minutes); git SHA, branch and a dirty flag (modified code under `src/` or `pyproject.toml`); Python, python-sat, PyETR, numpy, networkx, tokenizer-proxy and scorer versions; client settings; `previous_invocations` for a resumed run |
| `raw.jsonl.gz` | one record per (item, sample): `item_id`, `content_hash`, `presentation_hash`, `sample`, `cache_key`, `prompt_hash`, the exact `request` body, the full API `response` (content, reasoning, reasoning_details, usage, provider, model, id, finish reasons), `error` / `errors`, `attempts`, `requested_at` and `completed_at` (UTC), `latency_s`, `from_cache`, `failed_attempt_costs` (API-reported cost of each failed attempt, 0 if none), `charged_usd` (all attempts; 0 for a cache hit) and `cost_usd` (the returned response's) |
| `scored.jsonl.gz` | one scored record per raw record (below) |
| `scoring.json` | scorer version, git SHA, scoring time, category counts |
| `REPORT.md` | descriptive summary: categories and accuracy per eval, tokens per eval and kind, truncation by cell, parse flags, the responses that were not ok. No mixture fits and no claims about heuristics |

Every live run (and probe batch) appends a row to `data/runs/LEDGER.md` with its API-reported cost. With `--budget-tag T --budget-usd B`, a run's cap is min(`--cap-usd`, B − the ledger's total for T), so a budget holds across runs.

### The scored record

One JSON object per response. The identification engine joins it to its item on `item_id` and checks `content_hash`; `content_hash` alone is not unique, because several cells present the same content.

| Field | Meaning |
|---|---|
| `item_id`, `content_hash`, `presentation_hash`, `base_hash`, `source_hash`, `set_id`, `pair_id`, `vertical`, `eval_id`, `cell` | The item, copied from the item record |
| `domain` / `item_domain`, `answer_format`, `channel` | Canonical domain (coloring, sat, entailment, knapsack); the item's own domain string; its answer format; its scoring channel (`decision`, `answer`, `target-bit`, `target-colour`) |
| `run_id`, `model`, `model_requested`, `provider`, `condition`, `sample`, `from_cache`, `generation_id` | Who answered, under which condition |
| `category` | One of `ok`, `parse_fail`, `refusal`, `declared_impossible`, `partial`, `truncated`, plus `api_error` for a call that never returned |
| `parse_status`, `parse_detail`, `flags`, `n_answer_blocks`, `witness` | What the parser found (kept for truncated responses too), why, and tolerated deviations |
| `parsed` | The answer in the members' representation: colouring dict, assignment dict, "UNSAT", "IMPOSSIBLE", "SAT" / "POSSIBLE" (a positive decision without a usable witness), "YES" / "NO", "X", option letter, sorted item list, sorted fact list or "NOTHING". `{target: colour}` for the single-vertex format. `null` unless `category` is ok |
| `answer_key` | `heuristics.answers.answer_key(domain, parsed)`, comparable with `answer_key(domain, predictions[label]["answer"])` |
| `channel_value`, `outcome_class` | The parsed answer on the item's channel, and the outcome-class label as written in `extra.outcome_classes` and `disconfirms`. Since scorer-1.1.0 an answer no member listed goes to the unlisted-solution class of the solution sets that contain it (checked with the item's serialised membership rules), and to "answer = other" only when it is in none. Only for ok |
| `members_matched`, `answer_key_matches` | Member labels whose prediction has the same channel value / the same answer key. A set-valued member appears in `members_matched` only when its set has one solution and the answer is it |
| `sets_matched` | Set-valued members (EXACT, A/H E5's TT) whose solution set contains the answer. Empty for items written before `extra.channel_spec` existed. Only for ok |
| `correct`, `valid`, `optimal` | Only for ok; otherwise `null`. See below |
| `prompt_tokens`, `completion_tokens`, `reasoning_tokens`, `cost_usd` | API-reported usage |
| `finish_reason`, `native_finish_reason`, `truncated` | Truncated = finish_reason `length`, or the completion reached max_tokens |
| `reasoning_returned`, `reasoning_chars`, `content_chars`, `pre_answer_tokens` | Whether reasoning text came back, sizes, and visible working before the answer |
| `scorer_version`, `scorer_git_sha`, `scorer_git_dirty` | Which scorer made the record (DESIGN §5 rule 3) |
| `forced`, `forced_template`, `source_run_id` | Only on a forced final answer (`force.py`): `true`, the template, and the run whose response's trace it replays |
| `forced_select`, `forced_sample`, `source_sample` | force-2 only: `cut` or `done`, the forced sample index, and the source response's sample index |
| `natural_category`, `natural_correct`, `natural_answer_key`, `same_as_natural` | `--select done` only: the source response's own scoring, and whether the forced answer has the same answer key, both `ok` |

For the single-vertex format (C E3, arm I) the members' answers are full colourings, so `answer_key` never matches theirs; compare on `channel_value`.

## The scorer

Deterministic, no LLM (DESIGN §5 rule 4), and it reads the item's structured `instance`, never the prompt.

**Parsing.** The last answer block wins.

- **Markers:** the last line-initial `ANSWER:` marker, also `**ANSWER:**`, `Final answer:`, or `ANSWER` alone on a line, after any symbols (`### ✅ Final Answer`). An inline `ANSWER:` counts only when there is no line-initial one. For the JSON formats, the last JSON object carrying the format's key.
- **Tolerated and removed first:** code fences, markdown emphasis, list bullets, whitespace and case; inline `<think>…</think>` in the content; and, for the `ANSWER:` formats, LaTeX decoration (`$$\text{ANSWER: C}$$`, `\boxed{C}`; flag `latex_unwrapped`).
- **No marker at all:** a reply that is nothing but an answer in the format is parsed (flag `no_answer_marker`). This matters in the direct condition. So is a last fenced code block that holds nothing but an answer (flag `fenced_answer_no_marker`). Any other text without a marker is a parse failure.
- **The reasoning channel is never parsed for the answer.** A finished reply whose answer appears only there is flagged `answer_only_in_reasoning` and stays a parse failure.

| Answer format (items) | Parsed into |
|---|---|
| `sat_json` (A/H SAT) | `{"satisfiable": true, "assignment": "0110…"}` → assignment dict over `cnf.var_names` in order; `false` → "UNSAT" |
| `col_json` (A/H COL) | `{"possible": true, "rooms": {...}}` → colouring dict; `false` → "IMPOSSIBLE" |
| `ent_yn_json` (A/H ENT) | `{"follows": true/false}` → "YES" / "NO" |
| `ent_open_json` (A/H E5 ENT) | list of facts → sorted canonical literals (matched to the premises' vocabulary after case, whitespace, final period, "isn't" and a leading "the" are normalised); "NOTHING" or [] → "NOTHING"; "contradictory" → "X" |
| `JSON {"items": [...]}` (A/H E5 KNAP) | sorted item list |
| `ANSWER:` + `vertex: colour` lines, with or without IMPOSSIBLE (C colouring) | colouring dict; IMPOSSIBLE where the format allows it |
| `ANSWER:` + UNSAT or `x=T` / `x=F` (C SAT) | assignment dict or "UNSAT" |
| `ANSWER:` + item letters (C knapsack) | sorted item list ("none" → []) |
| `ANSWER:` + only the colour number of v (C E3 arm I) | `{v: colour}` (the vertex label itself is not read as the colour) |
| `ANSWER:` + YES or NO (C E5 entailment); final line `ANSWER: YES`/`NO` (B4/C4) | "YES" / "NO" |
| final line `ANSWER: <letter>` (B4/C4 MC) | the option letter (A–E; "None of these" → E) |

**Strictness.** Nothing is filled in. A witness with missing vertices, variables or digits is `partial`. An unknown vertex or variable, or one given two different values, is `parse_fail`. Extra prose, a different order from the requested one, repeated identical entries and booleans written as strings are tolerated and flagged.

**Decision and witness channels.** On a decision channel (A/H E1/E2, C E5 entailment, B4/C4 YES/NO) the scored answer is the decision. A positive claim's witness is checked (`valid`), and its problems are flags (`witness_partial`, `witness_malformed`, `witness_missing`), not a category; the parsed answer is then "SAT" / "POSSIBLE". On every other channel the witness is the answer, so its problems set the category.

**Categories.** Truncation wins over everything (censoring, SCOPE §6 rule 2): the parse is still recorded in `parse_status`, but `parsed`, `outcome_class` and `correct` stay null. Then refusal (finish_reason `content_filter`, a `refusal` field, or refusal wording with no parseable answer). `declared_impossible` is a give-up ("cannot be determined", "too complex", "unknown", "contradictory" on a YES/NO question), or IMPOSSIBLE / UNSAT where the format offers no such answer (the fewest-colours and single-colour formats, knapsack). Where the format does offer it, IMPOSSIBLE / UNSAT is an ordinary `ok` answer, because members such as ALWAYS-UNSAT and the abort variants predict it.

**Correctness**, with the repo's problem code (read-only):

| Task | `valid` | `correct` |
|---|---|---|
| Colouring, k given | proper on the stated rule's graph (`effective_graph`, so A/H E5 complements count), colours in 1..k, fixed colours kept | = valid; IMPOSSIBLE is correct iff not k-colourable |
| Colouring, fewest colours | proper, positive colours | valid and uses χ colours (`optimal`) |
| Colouring, single vertex (C E3 I) | – | the colour equals instructed first-fit's |
| SAT | satisfies the stated CNF (`effective_cnf`) and the fixed values | = valid; UNSAT is correct iff unsatisfiable |
| Decision items | the witness, as above | the decision matches the ground truth |
| Knapsack | weight ≤ capacity (≥ for the A/H E5 covering rule) | valid and the value equals the optimum (`optimal`) |
| Entailment | – | equals the ground-truth answer (YES/NO, letter, fact set) |

**Versioning.** `SCORER_VERSION` is on every record, with the git SHA of the scoring checkout. Bump it on any behavioural change and re-score every run (`python -m reasoning_heuristics.evals.score data/runs/*/`). The channel is rebuilt from the item's `extra.channel_spec` (`generators.common.item_channel`). Items written before it existed are rebuilt from the channel name with the generator's channel functions. A test checks them against every committed item's stored classes.

**Scorer versions.** This is the one changelog. Two lines of work used overlapping labels before they met: main's (PR #13) and the smoke-runs branch's (PR #15). The branch labels are written below as `runs-x.y.z`; on that branch they appeared in records as plain `scorer-x.y.z`, and every one of those records has since been re-scored with 1.5.0.

| Label | Where | What it added |
|---|---|---|
| scorer-1.0.0 | PR #8 | The first scorer |
| scorer-1.1.0 | main, PR #13 (fix-generators) | Reads `extra.channel_spec` and classifies answers with `generators.common.classify_answer`. An answer that no member predicted goes to the unlisted-solution class of the sets that contain it, or to other when it is in none. The record gains `sets_matched`. On items without a `channel_spec` (every set generated before this version) the outcome classes are unchanged |
| runs-1.1.0 | smoke-runs branch | A reply that is nothing but the answer, with no `ANSWER:` marker, is parsed (`no_answer_marker`) |
| runs-1.1.1 | smoke-runs branch | `answer_only_in_reasoning` is no longer set on truncated replies, whose reasoning often just quotes the format |
| runs-1.2.0 | smoke-runs branch | LaTeX answer decoration is unwrapped in the `ANSWER:` formats (`latex_unwrapped`) |
| runs-1.3.0, runs-1.3.1 | smoke-runs branch | C SAT and colouring values given without their names, or with the format's `x=T` placeholder, are read in the requested order when the item states one and the count is exact (`positional_values`, `placeholder_names`). Commentary after the values is tolerated |
| runs-1.4.0 | smoke-runs branch | A line-initial marker may follow any symbols (`### ✅ Final Answer`). With no marker at all, the last fenced block is read if it holds nothing but an answer (`fenced_answer_no_marker`) |
| runs-1.4.1 | smoke-runs branch | Positional values may use the placeholders the generators switched to (`<variable>=T`, PR #12) |
| scorer-1.5.0 | PR #15 | scorer-1.1.0 plus every runs-x.y.z change |
| scorer-1.5.1 | 2026-11-18 | A knapsack answer block that opens with a lead-in ending in a colon and naming no item ("The chosen items in alphabetical order are:") is read from its next line (`answer_after_lead_in`). Seen on Qwen3-14B with thinking: 98 of its 300 pc20 C E2 knapsack answers were parse failures under 1.5.0. Every committed run is re-scored with it |
| **scorer-1.5.2** | 2026-11-18 | Reads a text-completions choice (`POST /completions`, `force.py`): no `message` but a `text` means the content is the text and the reasoning is the choice's `reasoning`. Chat responses score exactly as under 1.5.1: re-scoring all 22 committed 2026-11-18 runs (22,012 records) changed no field but `scorer_version`, `scorer_git_sha` and `scorer_git_dirty`. Their committed files stay at 1.5.1 |

## Cost estimates (dry runs)

Estimate = items × (proxy prompt tokens × prompt price + assumed output tokens × completion price). Prompt tokens come from the tokenizer proxy (`tokens.py`, regex-digit-split-v1) plus 12 template tokens. Output tokens per item are the vertical docs' dev-batch figures, the same ones SCOPE §2–3 are built from: [A/H §7](verticals/A_H_baselines.md) (BE: SAT 10–18k, COL 7–14k, ENT 7k, KNAP 6k), [C's cost table](verticals/C_constructive.md) (BE 3–18k by eval; ND for direct) and [B4/C4's cost table](verticals/B4_C4_restrict_online.md) (BE 1.4–1.8k; direct 10–15). A/H gives no direct figures, so direct assumes the JSON answer's size (SAT 60, COL 150, ENT 10–40, KNAP 30 tokens). Prices are SCOPE §1 list prices until a model's provider is pinned. The worst case puts every item at max_tokens.

**Smoke, excluding E8, gpt-oss-20b, thinking-high** ($0.03 / $0.13 per M):

| Vertical | Eval | Items | Prompt tokens (proxy) | Output tokens (assumed) | Estimate (USD) | Worst case (USD) |
|---|---|---|---|---|---|---|
| A/H | E1 | 14 | 9,958 | 192,000 | 0.025 | 0.060 |
| A/H | E2 | 24 | 25,121 | 280,000 | 0.037 | 0.103 |
| A/H | E5 | 17 | 8,027 | 130,000 | 0.017 | 0.073 |
| B4/C4 | E1 | 28 | 3,384 | 50,400 | 0.007 | 0.119 |
| B4/C4 | E2 | 48 | 5,648 | 67,200 | 0.009 | 0.205 |
| C | E1 | 12 | 9,932 | 102,000 | 0.014 | 0.051 |
| C | E2 | 40 | 24,101 | 305,000 | 0.040 | 0.171 |
| C | E3 | 54 | 88,650 | 612,000 | 0.082 | 0.233 |
| C | E5 | 17 | 13,767 | 151,000 | 0.020 | 0.073 |
| **Total** | | **254** | **188,588** | **1,889,600** | **0.25** | **1.09** |

**Dev, excluding E8, gpt-oss-20b, thinking-high:**

| Vertical | Eval | Items | Prompt tokens (proxy) | Output tokens (assumed) | Estimate (USD) | Worst case (USD) |
|---|---|---|---|---|---|---|
| A/H | E1 | 70 | 71,334 | 960,000 | 0.127 | 0.300 |
| A/H | E2 | 120 | 124,933 | 1,400,000 | 0.186 | 0.515 |
| A/H | E5 | 85 | 44,155 | 650,000 | 0.086 | 0.363 |
| B4/C4 | E1 | 140 | 17,304 | 252,000 | 0.033 | 0.597 |
| B4/C4 | E2 | 240 | 28,528 | 336,000 | 0.044 | 1.023 |
| C | E1 | 60 | 51,538 | 510,000 | 0.068 | 0.257 |
| C | E2 | 200 | 121,280 | 1,525,000 | 0.202 | 0.856 |
| C | E3 | 270 | 443,250 | 3,060,000 | 0.411 | 1.163 |
| C | E5 | 85 | 69,263 | 755,000 | 0.100 | 0.364 |
| **Total** | | **1,270** | **971,585** | **9,448,000** | **1.26** | **5.44** |

**Totals for other models and conditions** (same items and assumptions, SCOPE §1 list prices):

| Model, condition | Smoke estimate | Smoke worst case | Dev estimate | Dev worst case |
|---|---|---|---|---|
| gpt-oss-20b, thinking-high | $0.25 | $1.09 | $1.26 | $5.44 |
| gpt-oss-120b, thinking-high | $1.16 | $5.02 | $5.81 | $25.11 |
| Qwen3-32B, thinking | $0.54 | $2.35 | $2.72 | $11.73 |
| Qwen3-32B, direct | $0.02 | $0.09 | $0.12 | $0.44 |
| Qwen3-14B, thinking | $0.48 | $2.02 | $2.38 | $10.10 |
| Qwen3-14B, direct | $0.03 | $0.09 | $0.15 | $0.43 |

These are assumptions until a smoke run measures them. Each run's `REPORT.md` gives measured completion tokens per eval and kind, and the dev projections should be redone from those.

**Dev projections from the smoke runs** (2026-11-18). These come from `run --dry-run --tokens-from data/runs/<run_id>` on the dev tier (1,270 items, E8 excluded), at the pinned prices:

| Model, condition | Dev, assumed tokens | Dev, measured tokens | Dev worst case |
|---|---|---|---|
| gpt-oss-20b, thinking-high | $1.35 | $3.08 | $5.85 |
| Qwen3-32B, thinking-high | $2.18 | $2.47 | $9.38 |
| Qwen3-32B, direct | $0.09 | $0.10 | $0.35 |

The measured projection counts each truncated response at the 32,768 cap. With a higher cap it would be a floor: 35% of gpt-oss-20b's smoke responses hit the cap.

**The cap.** Before a request is sent, it reserves its worst case: prompt bytes as a token upper bound plus the full max_tokens, at the configured price, times 1.25. The reservation is settled to the API-reported `usage.cost` when the call returns. A request whose reservation would take spend plus in-flight reservations past `--cap-usd` is not sent; the run stops cleanly with status `stopped`, keeps everything already returned, and scores it. A call that costs more than its reservation means the configured price is wrong, and it also stops the run. A failed attempt can still be charged (a 200 whose body carries an error after the provider generated): any `usage.cost` it reports is booked at once, and the call retries only while spend plus every reservation, its own included, stays within the cap.

## Provider probes and pins (2026-11-17)

Endpoint listings and 62 tiny calls ("What is 17 + 25?") over the SCOPE §1 models cost $0.0055: [data/runs/probes/2026-11-17/PROBES.md](../data/runs/probes/2026-11-17/PROBES.md). Every probed endpoint returned the reasoning text. The pins, and why each was chosen, are in `models.py`:

| Model | Pinned endpoint | Precision | $/M in / out | Max completion | Thinking off |
|---|---|---|---|---|---|
| gpt-oss-20b | `dekallm/bf16` | bf16 | 0.029 / 0.14 | 117,964 | rejected on every endpoint (HTTP 400 "Reasoning is mandatory") |
| gpt-oss-120b | `dekallm/bf16` | bf16 | 0.03 / 0.18 | 117,964 | rejected |
| Qwen3-32B | `deepinfra/fp8/flex` | fp8 (no bf16 endpoint exists) | 0.064 / 0.224 | 36,864 | honoured: `enabled: false` and `effort: none` give 0 reasoning tokens; `/no_think` leaves an empty think block |
| Qwen3-14B | `deepinfra/fp8/flex` | fp8 (or int4 elsewhere) | 0.096 / 0.192 | 36,864 | honoured |
| Qwen3-30B-A3B | `deepinfra/fp8/flex` | fp8 (only provider) | 0.096 / 0.40 | 36,864 | honoured |
| DeepSeek-R1-0528 | `siliconflow/fp8` | fp8 (its release precision) | 0.50 / 2.18 | 147,456 | rejected |
| Qwen3-235B-A22B-thinking | `venice/fp8` | fp8 (only endpoint) | 0.45 / 3.50 | **16,384** | rejected; `/no_think` ignored |

- **gpt-oss:** bf16 holds the released MXFP4 expert weights exactly. The endpoints not pinned were rejected for these reasons:
  - DeepInfra bf16 was rate-limited upstream (HTTP 429 on all 6 attempts);
  - AkashML fp4 reported 0 reasoning tokens alongside reasoning text;
  - the fp8 endpoints are a lossy re-quantisation.
- **Qwen3 hybrids are fp8-only on OpenRouter.** Phase 2 should use the official FP8 checkpoint or say how bf16 differs. DeepInfra's standard tier caps completions at 16,384 and Tenstorrent's context is 20,000, so the flex tier is pinned.
- **Qwen3-235B-thinking cannot run the 32k condition on OpenRouter today.** The runner refuses a max_tokens above the pinned endpoint's completion limit.

## First live runs (smoke, 2026-11-18)

Three acceptance runs, each on all 254 smoke items except A/H E8, on the pinned endpoints. They used the items as committed before the generator fixes of 2026-11-18. To re-score them, use `score --items-at-run-sha`. Each run's own `REPORT.md` has the details; all are scored with scorer-1.5.1 against the items at their recorded SHA.

| Run | Model, condition | Provider served | Responses | ok | Truncated | Other categories | Correct of ok | API cost | Wall time |
|---|---|---|---|---|---|---|---|---|---|
| `2026-11-18-smoke-gpt-oss-20b-thinking-high` | gpt-oss-20b, thinking-high | DekaLLM (254) | 254 | 165 | 89 | – | 160/165 (97%) | $0.6159 | 111 min (2 invocations) |
| `2026-11-18-smoke-qwen3-32b-thinking-high` | qwen3-32b, thinking-high | DeepInfra (254) | 254 | 248 | 6 | – | 188/248 (76%) | $0.4941 | 56 min |
| `2026-11-18-smoke-qwen3-32b-direct` | qwen3-32b, direct | DeepInfra (254) | 254 | 250 | 3 | parse_fail 1 | 93/250 (37%) | $0.0194 | 1 min |

**Measured completion tokens per item** (reasoning included, API-reported; truncated responses count at their cap), with the truncation rate at the cap and the actual API cost per item. Use these, not the assumptions above, to price dev runs (`run --dry-run --tokens-from data/runs/<run_id>`):

| Model | Condition | Vertical | Eval | n | Completion tokens, median | mean | Truncated at cap | $/item | Run cost |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | thinking-high | A/H | E1 | 14 | 15,271 | 18,379 | 5 (36%) | 0.00259 | 0.0363 |
| gpt-oss-20b | thinking-high | A/H | E2 | 24 | 31,099 | 21,655 | 11 (46%) | 0.00306 | 0.0735 |
| gpt-oss-20b | thinking-high | A/H | E5 | 17 | 13,409 | 16,479 | 4 (24%) | 0.00232 | 0.0395 |
| gpt-oss-20b | thinking-high | B4/C4 | E1 | 28 | 2,378 | 2,621 | 0 (0%) | 0.00037 | 0.0104 |
| gpt-oss-20b | thinking-high | B4/C4 | E2 | 48 | 642 | 684 | 0 (0%) | 0.00010 | 0.0048 |
| gpt-oss-20b | thinking-high | C | E1 | 12 | 22,545 | 21,770 | 1 (8%) | 0.00307 | 0.0368 |
| gpt-oss-20b | thinking-high | C | E2 | 40 | 32,768 | 28,699 | 27 (68%) | 0.00403 | 0.1614 |
| gpt-oss-20b | thinking-high | C | E3 | 54 | 32,768 | 28,065 | 36 (67%) | 0.00397 | 0.2143 |
| gpt-oss-20b | thinking-high | C | E5 | 17 | 16,135 | 16,197 | 5 (29%) | 0.00229 | 0.0389 |
| **gpt-oss-20b** | **thinking-high** | **all** | | **254** | **17,564** | **17,179** | **89 (35%)** | **0.00242** | **0.6159** |
| qwen3-32b | thinking-high | A/H | E1 | 14 | 11,656 | 10,896 | 0 (0%) | 0.00249 | 0.0349 |
| qwen3-32b | thinking-high | A/H | E2 | 24 | 12,036 | 13,508 | 4 (17%) | 0.00310 | 0.0744 |
| qwen3-32b | thinking-high | A/H | E5 | 17 | 9,140 | 10,154 | 0 (0%) | 0.00231 | 0.0392 |
| qwen3-32b | thinking-high | B4/C4 | E1 | 28 | 1,109 | 1,439 | 0 (0%) | 0.00033 | 0.0092 |
| qwen3-32b | thinking-high | B4/C4 | E2 | 48 | 466 | 507 | 0 (0%) | 0.00012 | 0.0058 |
| qwen3-32b | thinking-high | C | E1 | 12 | 12,824 | 11,380 | 0 (0%) | 0.00260 | 0.0313 |
| qwen3-32b | thinking-high | C | E2 | 40 | 11,536 | 13,293 | 0 (0%) | 0.00302 | 0.1207 |
| qwen3-32b | thinking-high | C | E3 | 54 | 8,960 | 10,743 | 1 (2%) | 0.00252 | 0.1359 |
| qwen3-32b | thinking-high | C | E5 | 17 | 10,100 | 10,999 | 1 (6%) | 0.00252 | 0.0428 |
| **qwen3-32b** | **thinking-high** | **all** | | **254** | **7,276** | **8,462** | **6 (2%)** | **0.00195** | **0.4941** |
| qwen3-32b | direct | A/H | E1 | 14 | 29 | 31 | 0 (0%) | 0.00006 | 0.0008 |
| qwen3-32b | direct | A/H | E2 | 24 | 38 | 208 | 3 (12%) | 0.00012 | 0.0029 |
| qwen3-32b | direct | A/H | E5 | 17 | 19 | 30 | 0 (0%) | 0.00004 | 0.0007 |
| qwen3-32b | direct | B4/C4 | E1 | 28 | 5 | 12 | 0 (0%) | 0.00001 | 0.0003 |
| qwen3-32b | direct | B4/C4 | E2 | 48 | 5 | 5 | 0 (0%) | 0.00001 | 0.0005 |
| qwen3-32b | direct | C | E1 | 12 | 110 | 93 | 0 (0%) | 0.00008 | 0.0009 |
| qwen3-32b | direct | C | E2 | 40 | 103 | 67 | 0 (0%) | 0.00006 | 0.0023 |
| qwen3-32b | direct | C | E3 | 54 | 472 | 317 | 0 (0%) | 0.00018 | 0.0098 |
| qwen3-32b | direct | C | E5 | 17 | 8 | 45 | 0 (0%) | 0.00006 | 0.0011 |
| **qwen3-32b** | **direct** | **all** | | **254** | **8** | **111** | **3 (1%)** | **0.00008** | **0.0194** |

What the runs showed:

- **gpt-oss-20b at high effort writes 2.3× the output tokens the vertical docs assume** (4.36M against 1.89M on smoke), even though 89 of its 254 responses (35%) stop at the 32,768 cap.
  - The truncation is concentrated in a few kinds of item:
    - every C E3 full-colouring response (arm U, 36 of 36);
    - every A/H E2 SAT and C E5 SAT response;
    - 14 of 15 C E2 knapsack and 7 of 10 C E2 SAT responses.
  - B4/C4 never truncates, and neither does C E3's single-vertex arm I.
  - The truncated traces are still working, not looping. Their last 20k characters compress like those of finished traces (gzip ratio about 0.3), and few lines repeat.
  - The responses that finish are nearly all right (160 of 165), so the censoring removes the hard items, not random ones.
  - Truncated responses are censored (SCOPE §6 rule 2) and carry no answer. Before a pilot, the item sizes need calibrating for this model (SCOPE §6 rule 1), or the cap needs raising. The pinned endpoint allows 117,964 completion tokens.
- **Qwen3-32B with thinking is shorter, and truncates less**: 1.14× the assumed tokens, and 6 of 254 responses truncated. It writes its answer in four ways the scorer did not expect, each now handled with a flag:
  - LaTeX (`$$\boxed{C}$$`; runs-1.2.0);
  - the C SAT values without their names, or with the format's placeholder `x=T` (runs-1.3.x);
  - a stray `---` and commentary after the values (runs-1.3.1);
  - `### ✅ Final Answer` headings, or a colouring in a code fence with no marker at all (runs-1.4.0).
- **Qwen3-32B direct.**
  - Thinking off held on all 254 responses.
  - Several replies drop the `ANSWER:` marker (runs-1.1.0).
  - Three A/H E2 SAT replies loop on the assignment string (`0101…`) until the 1,024 cap.
  - A few replies still work in the visible output: see `pre_answer_tokens` in its REPORT.md.
- **Providers.**
  - DekaLLM answered HTTP 429 to some first attempts at 16 concurrent requests; all were retried successfully. DeepInfra flex sent none.
  - One DekaLLM response broke off mid-body (`IncompleteRead`) and stopped run (a) at 188 of 254. The client now retries that error, and the run was resumed into the same directory.
  - Streams ran at a median of 52 tokens/s on gpt-oss-20b (DekaLLM; 10th–90th percentile 43–64) and 34 tokens/s on Qwen3-32B (DeepInfra flex; 30–38).
  - Run (a) took 111 minutes over its two invocations at 16 concurrent requests. Run (b) took 56 minutes at 24.
- **Prompt tokens** (API-reported against the proxy, chat template included):
  - Qwen3-32B: 1.06× (1.03–1.11 by eval); 1.07× in the direct condition, which adds a system prompt.
  - gpt-oss-20b: 0.93× overall, from 0.83× on C E3 to 1.64× on B4/C4. On B4/C4's short prompts it reports about 65 tokens per request more than the proxy, against about 10 for Qwen3-32B. That is most likely its chat template's system header. On the C prompts, which are full of vertex and variable numbers, it reports fewer tokens than the proxy: its tokenizer groups up to three digits, while the proxy splits every digit.
- **One prompt bug, since fixed in the generators.** The C SAT answer line "the values as `x=T` / `x=F`" used `x` as a placeholder, which collides with the variable names `x15`…. PR #12 changed it to `<variable>=T`. Items regenerated from main carry the new wording; the scorer reads both.

## Before any pilot (SCOPE §1)

Checked on the probes and the 2026-11-18 smoke runs:

- [x] **Each model and provider returns the reasoning text.**
  - Every probed endpoint of the seven models did, on the probe question.
  - Every thinking response in the smoke runs did (`reasoning_returned`).
  - One endpoint, AkashML fp4 for gpt-oss-20b, reported 0 reasoning tokens alongside reasoning text, so it is not pinned.
- [x] **The provider and precision are pinned per model, with the reason** (`models.py`; the table above).
- [x] **Thinking off is honoured for the direct condition on the pinned Qwen3 provider.**
  - In the probes, `{enabled: false}` and `{effort: none}` both gave 0 reasoning tokens.
  - In run (c), all 254 Qwen3-32B direct responses had no reasoning text and 0 reasoning tokens.
- [x] **max_tokens behaves as configured** (DESIGN §5 rule 11). Truncated responses stop at exactly max_tokens: 32,768 for thinking, 1,024 for direct. Reasoning tokens are reported on every response of the pinned endpoints.
- [ ] **Proxy and real prompt-token counts compared.**
  - Done for counts. API-reported prompt tokens are 1.06–1.07× the proxy count on Qwen3-32B (1.03–1.16 by eval and condition). On gpt-oss-20b they are 0.93× (0.83–1.64 by eval), chat template included; see the runs section.
  - Not done: the per-tokenizer check of the surface-matched pairs (`tokens.py` docstring) needs the tokenizers themselves.
- [x] **Measured tokens per eval are in the runs section below**, for recalibrating the dev-run estimate.

## Forced final answers at the cap

`force.py` gives a thinking model that stopped at its token cap one more chance to answer. It replays the truncated reasoning with the thinking closed, so the model writes only its final answer. This is the "`</think>` plus answer forcing" that [C's design](verticals/C_constructive.md) (§2.1) gives BE runs that reach the cap.

**Why.** A response cut at the cap carries no answer. It is `truncated`, and censored (SCOPE §6 rule 2). On the dev tier at high effort that is 462 of gpt-oss-20b's 1,270 responses and 284 of gpt-oss-120b's; the Qwen3 dev and pilot runs have 14–28 each. The censoring removes the hard items, not random ones, so what a model answers when stopped there is worth having, as a stratum of its own.

**Why not the chat API.** Probes on 2026-11-18, on the dev runs' truncated responses:

- The partial trace as a visible assistant turn, then a user turn saying the budget is used up and to answer now: gpt-oss-20b started over, and ran out of a 1,024- or 4,096-token second budget on 9 of 10.
- `reasoning_details` passed back on the assistant turn are dropped by the provider (`prompt_tokens` 256).
- A content prefill is not continued: the model starts new reasoning.

**What works: raw text completions**, `POST https://openrouter.ai/api/v1/completions`, on a provider that passes the prompt through. We write the model's chat template ourselves, with the trace as its thinking, and close the thinking. The body is `model`, `provider`, `prompt`, `max_tokens`, and the source request's `temperature`, `top_p` and, when it has one, `top_k`. The choice's `text` holds the answer, and `reasoning` any analysis the model writes again.

**DekaLLM wraps the raw prompt.** Not every provider passes it through. Sent the same text through `/completions` and as a chat user message through `/chat/completions`, a provider that passes the raw prompt through reports fewer prompt tokens for it, because the chat call adds the chat template. Equal counts mean the raw prompt was wrapped as a user message, and the model then reasons afresh ("The user asks…"). The probes (batch 11, `data/runs/probes/2026-11-18-forced-answer/`):

| Model | Provider | Raw / chat prompt_tokens | Passes the raw prompt through |
|---|---|---|---|
| gpt-oss-20b | DekaLLM bf16 (the source runs' pin) | 160 / 160 | no |
| gpt-oss-120b | DekaLLM bf16 (the source runs' pin) | 206 / 206 | no |
| gpt-oss-20b and gpt-oss-120b | DeepInfra bf16 | 93 / 147 | yes |
| gpt-oss-20b and gpt-oss-120b | Parasail fp4 | 93 / 206 | yes |
| gpt-oss-120b | Cerebras fp16 | 93 / 206 | yes (leaves `<\|return\|>` in the text) |
| Qwen3-32B and Qwen3-14B | DeepInfra fp8 flex (their pin) | 42 / 51 | yes |

So **force-1's gpt-oss passes are invalid**: `data/runs/forced/2026-11-18-dev-gpt-oss-*` measured a re-prompt with the trace as user text, not a forced answer. The gpt-oss probes sent to DekaLLM (batches 03, 04 and 06–09) are invalid for the same reason: their answer rates, and the effects of a wrap-up sentence and of an answer header, say nothing about forcing. Qwen3's force-1 passes are valid: DeepInfra passes the prompt through, and force-2 sends Qwen3 the same body.

**On a provider that passes the prompt through, forcing works** (batch 12, gpt-oss-20b on DeepInfra bf16, force-1's prompt):

- **Cut traces:** it answered 16 of 16 (8 traces, each sent plain and with force-2's `logit_bias`), and none went back to reasoning. One answer did not parse (`<v85>: 1`), and one wrote 2,325 tokens of visible working before it.
- **Finished traces:** replayed whole with the answer forced, 8 of 8 gave the model's own natural answer.

Qwen3-32B on DeepInfra (batch 05) answered 5 of 5 cut traces at max_tokens 1,024.

**Parameters** (`GET /api/v1/models/<slug>/endpoints`, batch 10): DeepInfra supports `logit_bias` but not `logprobs`, for gpt-oss and Qwen3. With `require_parameters: true`, a request with a parameter its endpoint does not support fails with "No endpoints found … Filter by Parameters".

**The prompt (force-1's, which force-2 sends too).** `trace` is the source response's `choices[0].message.reasoning`, with trailing whitespace removed. `user` and `system` are the source request's last user message and its system message, verbatim.

- **gpt-oss** (`openai/gpt-oss-*`). `effort` is the source request's `reasoning.effort`. The developer message is there only when the source request had a system message.

  ```
  <|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.
  Knowledge cutoff: 2024-06

  Reasoning: {effort}

  # Valid channels: analysis, commentary, final. Channel must be included for every message.<|end|><|start|>developer<|message|># Instructions

  {system}<|end|><|start|>user<|message|>{user}<|end|><|start|>assistant<|channel|>analysis<|message|>{trace}<|end|><|start|>assistant<|channel|>final<|message|>
  ```

- **Qwen3** (`qwen/qwen3-*`). The system turn is there only when the source request had one. The stop sentence is the Qwen3 technical report's thinking-budget mechanism. The prompt ends with a blank line after `</think>`.

  ```
  <|im_start|>system
  {system}<|im_end|>
  <|im_start|>user
  {user}<|im_end|>
  <|im_start|>assistant
  <think>
  {trace}

  Considering the limited time by the user, I have to give the solution based on the thinking directly now.
  </think>
  ```

- **Any other model** is refused.

**Template `force-2` (the default).** The prompt above, with two changes from force-1:

- **The forcing route.** Forced calls go to an endpoint that passes the raw prompt through, which need not be the source run's pin (`FORCING_ROUTES` in `evals/force.py`). Each route is `{"order": [slug], "allow_fallbacks": false, "require_parameters": true, "quantizations": [q]}`, priced at the endpoint's listed price. Both DekaLLM's gpt-oss bf16 and DeepInfra's bf16 serve the released weights upcast to bf16, so the forced call runs the weights that wrote the trace.

  | Model | Source runs' pin | Forcing route | USD/M prompt, completion | Context |
  |---|---|---|---|---|
  | gpt-oss-20b | `dekallm/bf16` | `deepinfra/bf16` | 0.03, 0.14 | 131,072 |
  | gpt-oss-120b | `dekallm/bf16` | `deepinfra/bf16` | 0.037, 0.17 | 131,072 |
  | Qwen3-32B | `deepinfra/fp8/flex` | the same | 0.064, 0.224 | 40,960 |
  | Qwen3-14B | `deepinfra/fp8/flex` | the same | 0.096, 0.192 | 40,960 |

- **gpt-oss may not leave the final channel.** Its body carries `logit_bias: {"200005": -100, "200006": -100, "200007": -100}`: `<|channel|>`, `<|start|>` and `<|end|>` in tiktoken's `o200k_harmony`. `<|return|>` (200002), which ends the answer, stays allowed. Qwen3 gets no `logit_bias`.

The manifest records both routings: `source.provider_routing` (the source run's) and `provider_routing` (the forced calls'). A source run not routed to its model's configured pin is refused: only traces from the pinned endpoint are forced.

**The raw-prompt check.** Before the first forced call of a live invocation, `force.py` checks that the forcing route passes a raw prompt through. It sends one text twice, to the forcing route, with max_tokens 8 and temperature 0: as `prompt` to `/completions`, and as the user message to `/chat/completions`. The text is the template above, filled with "Is 17 a prime number? Answer with one word, YES or NO." and a one-line thinking; for gpt-oss it is exactly the probes' prompt.

- **It passes only when the raw call's prompt_tokens are strictly below the chat call's.** Otherwise, or when either call fails, the pass stops with an error naming the provider, before any forced call. Nothing is written but the ledger row for the check's cost.
- **Both responses' prompt_tokens, texts, providers and costs** go into the manifest as `raw_check`.
- **The check costs about $0.00001.** It is booked in the cost guard and in the invocation's ledger row.
- **When it does not run:** in a dry run, which makes no calls at all, and when every call is answered from the response cache (`raw_check.skipped` says so).

**Template `force-1`** (`--template force-1`) is kept to reproduce and re-score its passes. It sends exactly what it sent before: the source run's pin, no `logit_bias`, `--select cut` only, no `--per-unit` or `--samples`. Its outputs stay in `data/runs/forced/<source_run_id>/`. Its live calls get the raw-prompt check too, so a gpt-oss force-1 pass with calls to send is refused (DekaLLM wraps). A pass answered wholly from the cache needs no check.

**What it selects** (`--select`), from the source's raw records, in the source's order:

- **`cut`** (the default): responses that stopped for length (finish_reason `length`) with a non-empty `reasoning`. Those that stopped there without a trace (the direct condition's) are counted (`skipped_no_trace`) and skipped.
- **`done`**: responses that finished (finish_reason `stop`) with a non-empty trace and non-empty content. The whole trace is replayed and the answer forced: the f = 1 acceptance test. Each forced raw record keeps the source response, its reasoning removed (`natural_response`), and each scored record adds the source response's own scoring: `natural_category`, `natural_correct`, `natural_answer_key`, and `same_as_natural` (the same answer key, both `ok`). Skipped: `skipped_no_trace`, `skipped_no_content`.
- **`--per-unit N`** keeps at most N records per unit (vertical, eval, item domain), in the source's order: a stratified acceptance sample. **`--limit N`** then keeps the first N.
- **`--samples S`** sends S forced calls per record. Sample indices 0..S−1 (`forced_sample`) give distinct cache keys and records.

**Where the outputs live.** Beside the source run: force-2 in `data/runs/forced-2/<select>/<source_run_id>/` (run id `forced-2/<select>/<source_run_id>`), force-1 in `data/runs/forced/<source_run_id>/`.

| File | Contents |
|---|---|
| `manifest.json` | `source` (run id, routing, the SHA-256 of its `raw.jsonl.gz`, condition, git); `forced` (template, endpoint, max_tokens; for force-2 also select and logit_bias); condition `<source label>-forced`; `provider_routing` and `price` of the forced calls; `raw_check`; the dry-run estimate; cap, budget and spend; git and versions; `items` (the source's item files, the item flags used, per_unit, limit, samples); `counts` (below) |
| `raw.jsonl.gz` | one record per forced call, as `run.py` writes them: the full request, prompt included, and response. Plus `source_run_id`, `source_cache_key` and `forced_template`; force-2 adds `forced_select`, `forced_sample` and `source_sample`, and for `done` `natural_response` and `natural_max_tokens`. `prompt_hash` is the first 16 hex digits of the prompt's SHA-256 |
| `scored.jsonl.gz` | the standard scorer's records (since scorer-1.5.2 it reads a text completion), plus `forced: true`, `forced_template` and `source_run_id`; force-2 adds `forced_select`, `forced_sample` and `source_sample`, and `done` the `natural_*` fields and `same_as_natural` |
| `scoring.json`, `REPORT.md` | as for any run; the report adds the pass's counts, routings and raw-prompt check |

**Counts** (`counts` in the manifest):

- **Selection:** `candidates`, `selected`, `units`, `samples`, `calls`, `skipped_*`, `max_tokens_lowered`.
- **Outcomes:** `responses`; `answered` (stopped by itself with a non-empty reply); `parsed` (category `ok`); `still_reasoning` (stopped at max_tokens again); and `renewed_reasoning`, the responses whose choice carries non-empty `reasoning`. That should be 0 under force-2; anything else means the provider or the model left the answer.
- **`done` adds** `natural_ok` (the source response's answer is `ok`) and `same_as_natural`.

**Acceptance tests,** before forced answers are analysed:

- **f = 1 agreement:** on `--select done` (a stratified sample, `--per-unit 3`), `same_as_natural / natural_ok` should be at least 95%.
- **Cut traces:** `answered` and `parsed` should each be at least 95% of the responses.
- **Repeatability** is measured with `--samples 2`: the share of records whose two samples give the same answer key (scored records grouped by `item_id` and `source_sample`).

**How they are kept apart.** The source run's files are never written. Its truncated records stay `truncated` (censored), and a forced answer never replaces one: it was written under a second budget the source condition did not have. Forced answers are analysed as their own stratum (`forced: true`, condition `…-forced`). The analysis reads only `data/runs/2026-11-18-{dev,pc20,pc40}-*` (`RUN_PATTERNS`), which `data/runs/forced/` and `data/runs/forced-2/` do not match.

**Running it.**

```bash
# count and cost estimate: no network, writes nothing
python -m reasoning_heuristics.evals.force data/runs/<source_run_id> --dry-run --allow-item-drift [--select done --per-unit 3]

# live (the key comes from the environment); re-running resumes, and the cache never pays twice
python -m reasoning_heuristics.evals.force data/runs/<source_run_id> --cap-usd 1 --allow-item-drift \
    [--select cut|done] [--per-unit N] [--samples S] [--max-tokens 4096] [--limit N] [--concurrency 4] \
    [--budget-tag T --budget-usd B]

# re-score after a scorer change, with the item flag the pass used
python -m reasoning_heuristics.evals.score --allow-item-drift data/runs/forced-2/<select>/<source_run_id>
```

- **Items.** The pass is scored against the source run's items. It refuses to start if they no longer hash to the source manifest, unless given the flag the source's own scoring used:
  - `--allow-item-drift` for the dev and pilot runs: their C E1 and C E2 files gained the A1 give-up member after the runs (data/items/pc20/README.md);
  - `--items-at-run-sha` for the smoke runs: the files at the source run's SHA. Re-score such a pass with `score --items-ref <SHA>` (`source.git.sha` in its manifest).
- **The cap.** Each call reserves 1.25 × (prompt + max_tokens) at the forcing route's price. The prompt is estimated as the source response's prompt plus completion tokens; the probes' forced prompts came to 1.0007–1.0033 times that. For a finished response the estimate includes its answer, which the prompt leaves out.
- **The context.** Each call's max_tokens is lowered when prompt plus answer would not fit the forcing endpoint's context: it becomes context − 1.01 × the prompt estimate − 64. A call left with under 256 tokens is skipped and counted (`skipped_no_room`); `max_tokens_lowered` counts the rest. DeepInfra serves Qwen3 with 40,960 tokens. On 2026-11-18 one dev item per Qwen3 run (estimate 36,889 tokens) overflowed it at 4,096 answer tokens, with an HTTP 400 that stopped the pass, before this rule existed.
- **Ledger.** Each live invocation that sends a call appends one row, the raw-prompt check included: run id `forced-2/<select>/<source_run_id>` (force-1: `forced/<source_run_id>`), condition `<source label>-forced`. A pass refused by the check books the check's cost in a row of its own (`status=refused`).
- **Dry-run estimates** for the 2026-11-18 thinking-high runs under force-2, at max_tokens 4,096: from the prompt alone (every call answers at once) to every call at max_tokens. The low-effort and direct runs have nothing to cut.

| Source run | `cut`: calls | `cut`: USD | `done --per-unit 3`: calls (units) | `done --per-unit 3`: USD |
|---|---|---|---|---|
| dev, gpt-oss-20b | 462 | 0.47–0.74 | 66 (23) | 0.03–0.07 |
| dev, gpt-oss-120b | 284 | 0.36–0.56 | 68 (23) | 0.04–0.08 |
| dev, Qwen3-32B / Qwen3-14B | 26 / 28 | 0.06–0.08 / 0.09–0.12 | 69 / 69 (23) | 0.05–0.11 / 0.07–0.13 |
| pc20, Qwen3-32B / Qwen3-14B | 14 / 21 | 0.03–0.04 / 0.07–0.09 | 27 / 27 (9) | 0.02–0.05 / 0.03–0.05 |
| pc40, Qwen3-32B / Qwen3-14B | 14 / 21 | 0.03–0.04 / 0.07–0.09 | 15 / 15 (5) | 0.01–0.03 / 0.02–0.03 |
| smoke, gpt-oss-20b / Qwen3-32B | 89 / 6 | 0.09–0.14 / 0.01–0.02 | 58 (21) / 67 (23) | 0.02–0.06 / 0.04–0.11 |

## E8: continuations and prefill

E8 items are specs: each continuation is built from the model's own earlier response (`generators/ah_e8.py`, `materialise`), as a user turn plus an assistant prefill: `<think>` + the truncated trace + `</think>` + a forced-answer header (early answering and transplants, 64 new tokens at most), or the trace up to a flipped assignment (mistake insertion, then free continuation). The runner skips E8 for now. What it would need, judged from OpenRouter's public docs (read 2026-11-17):

- **Assistant prefill exists.** The API overview says that to have a model complete a partial response you "include a message with `role: "assistant"` at the end of your messages array". That covers the visible-content channel only.
- **Prefilling the reasoning channel is not documented.** The reasoning-tokens page documents sending `reasoning` / `reasoning_details` back on earlier assistant turns to preserve reasoning across turns, and warns that `reasoning_details` blocks must be passed back unmodified and in order. It says nothing about a final assistant message whose reasoning the model should continue. For gpt-oss (harmony format: analysis and final channels) and Qwen3 (`<think>` in the template), a content prefill would most likely land in the final answer channel, which is not what E8 means by a truncated trace.
- **The 2026-11-18 forced-answer probes answered part of this** ([above](#forced-final-answers-at-the-cap)): a content prefill is not continued, `reasoning_details` passed back are dropped, and the raw completions endpoint takes our own chat template on DeepInfra (Qwen3's pin, and gpt-oss bf16). DekaLLM, gpt-oss's pin, wraps a raw prompt as a chat user message.
- **So E8 on OpenRouter needs a probe before it is built:** send a content prefill (`<think>…</think>` text plus the header) and an assistant message carrying `reasoning`, per pinned provider, and check whether the model continues the prefix or starts a new reply. If neither works, the options are a raw completions endpoint with the chat template applied by us (`/api/v1/completions`, if the pinned provider serves these models there), or self-hosted vLLM, where the prompt can end inside the analysis channel.
- **Runner changes then:** materialise each spec from the source run's raw output (`ah_e8.materialise`, with the model tokenizer's offsets for the truncation point, not the proxy), send it as a continuation with max_tokens 64 (or the condition's max for mistake insertion), and score with the `sat_json` parser on the continuation text. E8 raw records would carry the source run id and the source response's cache key.

## Open questions

- **The `direct` system instruction conflicts with the item prompts**, which say "Think as carefully as you need" (A/H) or "Think it through as carefully as you need" (B4/C4). The decision record keeps the prompts unchanged; the conflict is part of the condition and is recorded, but it may raise `pre_answer_tokens`.
- **Single-vertex items (C E3 arm I)** cannot be compared with members on `answer_key` (members predict full colourings); use `channel_value`.
- **C E5 partial colouring / assignment given:** a response that omits the already-fixed vertices is `partial` (flagged `missing_only_fixed`), because the prompt asks for every vertex. Relax this only by a scorer version bump.
- **A/H decision items with a malformed witness** stay `ok` on the decision channel, with a witness flag. If witness-invalid SAT claims ("infeasible SAT claim") should be a category of their own, that is a scorer change.
- **gpt-oss-20b at 32,768 tokens censors 35% of the smoke responses**, including all of C E3 arm U. The options are to shrink those items for every model, to raise the cap (the pinned endpoint allows 117,964), or to accept the censoring. That is a design decision (SCOPE §6 rules 1–2), not a runner one.
- **IMPOSSIBLE on C E3 target-bit items.** The stored outcome classes put it in `answer = other`, and so `channel_value` is null and `outcome_class` is other. The identification engine's bit space counts it as a value of its own. One of the two should change.
