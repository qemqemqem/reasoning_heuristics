# The runner and the scorer

The runner sends items to models through OpenRouter and keeps every response. The scorer turns each response into an answer in the members' representation, with a category, validity, correctness and the item's outcome class. This is SCOPE §4 item 1 plus the scoring path (DESIGN §5 rules 3–5, 10, 11). The code is in `src/reasoning_heuristics/evals/`.

| Module | What it does |
|---|---|
| `run.py` | CLI: dry-run estimate, capped and cached live calls, raw outputs, then scoring, report, manifest and ledger |
| `score.py` | CLI: re-score runs from their raw outputs on disk |
| `scoring.py` | The one versioned scorer (`SCORER_VERSION`) |
| `client.py` | OpenRouter chat completions: retries with backoff, long timeouts, full response capture |
| `cache.py` | Response cache keyed on the request body (model, provider routing, parameters, messages) plus the sample index |
| `cost.py` | Dry-run estimates and the `CostGuard` hard cap |
| `models.py` | Model configs, the thinking and direct conditions, the exact request body |
| `manifest.py`, `ledger.py`, `report.py` | Run manifests, `data/runs/LEDGER.md`, `REPORT.md` |
| `probe.py` | Provider probes: reasoning text returned, thinking off honoured, quantization |

## Running

```bash
# cost estimate only: no network, writes nothing
python -m reasoning_heuristics.evals.run --items data/items/smoke --model openai/gpt-oss-20b --effort high \
    --out data/runs/<run_id> --exclude-eval E8 --dry-run

# live run (the key comes from the environment; never put it on the command line)
set -a; . ./keys.env; set +a          # keys.env holds OPENROUTER_API_KEY=...; it is gitignored
python -m reasoning_heuristics.evals.run --items data/items/smoke --model openai/gpt-oss-20b --effort high \
    --cap-usd 2 --out data/runs/<run_id> --exclude-eval E8 [--budget-tag T --budget-usd 3]

# direct condition (thinking off; Qwen3 hybrids only)
python -m reasoning_heuristics.evals.run --items data/items/smoke --model qwen/qwen3-32b --condition direct \
    --cap-usd 0.2 --out data/runs/<run_id> --exclude-eval E8

# re-score from raw outputs after any scorer change
python -m reasoning_heuristics.evals.score data/runs/*/

# provider probes (tiny calls; results under data/runs/probes/)
python -m reasoning_heuristics.evals.probe --model qwen/qwen3-32b --out data/runs/probes/<date> --cap-usd 0.25
```

- **The key** is read from `OPENROUTER_API_KEY` inside each request and is never stored, printed, logged or written. A test greps every output file for it.
- **Provider pinning.** A live run refuses a model with no pinned provider (SCOPE §1), unless you pass `--provider <slug>` (sent as `order: [slug]`, `allow_fallbacks: false`, `require_parameters: true`) or `--no-pin`. Pins and the pinned endpoint's prices live in `models.py`; they come from the probes.
- **Resuming.** Re-running into the same `--out` sends only the (item, sample) pairs that have no response yet.
- **The cache** (`data/cache/openrouter/`, gitignored) means an identical request is never paid for twice, across runs. Repeat samples are separate keys. The permanent copy is each run's `raw.jsonl.gz`; `ResponseCache.import_runs` rebuilds a cache from those.
- **Concurrency** defaults to 8. Timeouts are 30 minutes per request. Retries: 6 attempts with exponential backoff and jitter (honouring `Retry-After`) on network errors, 408/409/425/429/5xx and errors inside a 200 body. 400/401/402/403/404/413/422 stop the run at once.
- **E8 is skipped** (`--exclude-eval E8`; the loader also refuses E8 specs). See [E8](#e8-continuations-and-prefill) below.

## Conditions

Decision record: [decisions/2026-11-17-direct-answer-arm.md](decisions/2026-11-17-direct-answer-arm.md).

| | thinking (primary) | direct (secondary) |
|---|---|---|
| Reasoning | on: gpt-oss `{"effort": "high"}` (`--effort` changes it); Qwen3 / R1 `{"enabled": true}` | off: `{"enabled": false}` (what each provider honours is a probe result) |
| max_tokens | 32,768 (reasoning + answer) | 1,024 |
| Messages | the item prompt as the only user message | a system message, then the item prompt |
| System instruction | none | "Respond with only the final answer in the requested format. Do not explain or show your working." |
| Sampling | each model's recommended thinking settings (gpt-oss: temperature 1.0, top_p 1.0; Qwen3: 0.6 / 0.95 / top_k 20; R1: 0.6 / 0.95) | Qwen3 non-thinking settings: 0.7 / 0.8 / top_k 20 |

- **gpt-oss cannot turn reasoning off.** It has no direct condition; the runner refuses one. `--effort low` is a budget arm of the thinking condition, labelled `thinking-low`.
- **The system instruction is an experimental factor.** Its exact text is in every manifest (`condition.system_prompt`) and in every raw request.
- **`pre_answer_tokens`** (proxy tokens of visible text before the final answer block) is on every scored record, so direct responses that work in the visible output can be flagged or excluded.

## What a run writes

`data/runs/<run_id>/`, kept permanently and committed (`.gitignore` ignores only `data/items/**/*.jsonl` and the cache):

| File | Contents |
|---|---|
| `manifest.json` | run id; status and stop reason; start and finish times; model requested and `models_returned`; `system_fingerprints`; provider routing sent and `providers_served`; the full condition (reasoning, sampling, max_tokens, system prompt); prices; item files with SHA-256, item count, skipped items; the dry-run estimate; cap, budget and spend (`spend.spent_usd` is API-reported); git SHA, branch and dirty flag; Python, python-sat, PyETR, numpy, networkx, tokenizer-proxy and scorer versions; client settings |
| `raw.jsonl.gz` | one record per (item, sample): `item_id`, `content_hash`, `presentation_hash`, `sample`, `cache_key`, `prompt_hash`, the exact `request` body, the full API `response` (content, reasoning, reasoning_details, usage, provider, model, id, finish reasons), `error` / `errors`, `attempts`, `latency_s`, `from_cache`, `charged_usd` (0 for a cache hit) and `cost_usd` (API-reported) |
| `scored.jsonl.gz` | one scored record per raw record (below) |
| `scoring.json` | scorer version, git SHA, scoring time, category counts |
| `REPORT.md` | descriptive summary: categories and accuracy per eval, tokens per eval and kind, truncation by cell, parse flags, the responses that were not ok. No mixture fits and no claims about heuristics |

Every live run (and probe batch) appends a row to `data/runs/LEDGER.md` with its API-reported cost. With `--budget-tag T --budget-usd B`, a run's cap is min(`--cap-usd`, B − the ledger's total for T), so a budget holds across runs.

### The scored record

One JSON object per response, the record the identification engine joins on `content_hash` (or `item_id`):

| Field | Meaning |
|---|---|
| `item_id`, `content_hash`, `presentation_hash`, `base_hash`, `source_hash`, `set_id`, `pair_id`, `vertical`, `eval_id`, `cell` | The item, copied from the item record |
| `domain` / `item_domain`, `answer_format`, `channel` | Canonical domain (coloring, sat, entailment, knapsack); the item's own domain string; its answer format; its scoring channel (`decision`, `answer`, `target-bit`, `target-colour`) |
| `run_id`, `model`, `model_requested`, `provider`, `condition`, `sample`, `from_cache`, `generation_id` | Who answered, under which condition |
| `category` | One of `ok`, `parse_fail`, `refusal`, `declared_impossible`, `partial`, `truncated`, plus `api_error` for a call that never returned |
| `parse_status`, `parse_detail`, `flags`, `n_answer_blocks`, `witness` | What the parser found (kept for truncated responses too), why, and tolerated deviations |
| `parsed` | The answer in the members' representation: colouring dict, assignment dict, "UNSAT", "IMPOSSIBLE", "SAT" / "POSSIBLE" (a positive decision without a usable witness), "YES" / "NO", "X", option letter, sorted item list, sorted fact list or "NOTHING". `{target: colour}` for the single-vertex format. `null` unless `category` is ok |
| `answer_key` | `heuristics.answers.answer_key(domain, parsed)`, comparable with `answer_key(domain, predictions[label]["answer"])` |
| `channel_value`, `outcome_class` | The parsed answer on the item's channel, and the outcome-class label as written in `extra.outcome_classes` and `disconfirms` ("answer = other" when no deterministic member predicted it). Only for ok |
| `members_matched`, `answer_key_matches` | Member labels whose prediction has the same channel value / the same answer key. Set-valued members (EXACT on witness tasks) never appear; use `correct` |
| `correct`, `valid`, `optimal` | Only for ok; otherwise `null`. See below |
| `prompt_tokens`, `completion_tokens`, `reasoning_tokens`, `cost_usd` | API-reported usage |
| `finish_reason`, `native_finish_reason`, `truncated` | Truncated = finish_reason `length`, or the completion reached max_tokens |
| `reasoning_returned`, `reasoning_chars`, `content_chars`, `pre_answer_tokens` | Whether reasoning text came back, sizes, and visible working before the answer |
| `scorer_version`, `scorer_git_sha`, `scorer_git_dirty` | Which scorer made the record (DESIGN §5 rule 3) |

For the single-vertex format (C E3, arm I) the members' answers are full colourings, so `answer_key` never matches theirs; compare on `channel_value`.

## The scorer

Deterministic, no LLM (DESIGN §5 rule 4), and it reads the item's structured `instance`, never the prompt.

**Parsing.** The last answer block wins: the last line-initial `ANSWER:` marker (also `**ANSWER:**`, `Final answer:`, `ANSWER` alone on a line; an inline `ANSWER:` only when there is no line-initial one), or the last JSON object carrying the format's key. Code fences, markdown emphasis, list bullets, whitespace and case are tolerated, and so is inline `<think>…</think>` in the content (removed first). The reasoning channel is never parsed for the answer; an answer found only there is flagged `answer_only_in_reasoning` and stays a parse failure.

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

**Versioning.** `SCORER_VERSION` is on every record, with the git SHA of the scoring checkout. Bump it on any behavioural change and re-score every run (`python -m reasoning_heuristics.evals.score data/runs/*/`). The outcome classes are rebuilt with the generator's own channel functions (`decision_channel`, `witness_channel`, C E3's `bit_channel` / `colour_channel`); a test checks them against every committed item's stored classes.

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

**The cap.** Before a request is sent, it reserves its worst case: prompt bytes as a token upper bound plus the full max_tokens, at the configured price, times 1.25. The reservation is settled to the API-reported `usage.cost` when the call returns. A request whose reservation would take spend plus in-flight reservations past `--cap-usd` is not sent; the run stops cleanly with status `stopped`, keeps everything already returned, and scores it. A call that costs more than its reservation means the configured price is wrong, and it also stops the run.

## Before any pilot (SCOPE §1)

To do on the first approved live run; results go in `data/runs/probes/` and the pins in `models.py`:

- [ ] Each model and provider returns the reasoning text (`reasoning` or `reasoning_details` non-empty; `reasoning_returned` on every scored record).
- [ ] The provider and precision are pinned per model (`provider.order`, `allow_fallbacks: false`, quantization recorded), with the reason.
- [ ] Thinking off is honoured for the direct condition on the pinned Qwen3 providers (no reasoning text, zero reasoning tokens, no `<think>` in content).
- [ ] Reported reasoning tokens and max_tokens behave as configured (DESIGN §5 rule 11): truncated responses stop at 32,768 completion tokens.
- [ ] The proxy prompt-token counts are compared with API-reported `prompt_tokens`, and the real tokenizers' counts are checked for the surface-matched pairs (`tokens.py` docstring).
- [ ] The cost estimate is recalibrated from the smoke run's measured tokens before any dev run.

## E8: continuations and prefill

E8 items are specs: each continuation is built from the model's own earlier response (`generators/ah_e8.py`, `materialise`), as a user turn plus an assistant prefill: `<think>` + the truncated trace + `</think>` + a forced-answer header (early answering and transplants, 64 new tokens at most), or the trace up to a flipped assignment (mistake insertion, then free continuation). The runner skips E8 for now. What it would need, judged from OpenRouter's public docs (read 2026-11-17):

- **Assistant prefill exists.** The API overview says that to have a model complete a partial response you "include a message with `role: "assistant"` at the end of your messages array". That covers the visible-content channel only.
- **Prefilling the reasoning channel is not documented.** The reasoning-tokens page documents sending `reasoning` / `reasoning_details` back on earlier assistant turns to preserve reasoning across turns, and warns that `reasoning_details` blocks must be passed back unmodified and in order. It says nothing about a final assistant message whose reasoning the model should continue. For gpt-oss (harmony format: analysis and final channels) and Qwen3 (`<think>` in the template), a content prefill would most likely land in the final answer channel, which is not what E8 means by a truncated trace.
- **So E8 on OpenRouter needs a probe before it is built:** send a content prefill (`<think>…</think>` text plus the header) and an assistant message carrying `reasoning`, per pinned provider, and check whether the model continues the prefix or starts a new reply. If neither works, the options are a raw completions endpoint with the chat template applied by us (`/api/v1/completions`, if the pinned provider serves these models there), or self-hosted vLLM, where the prompt can end inside the analysis channel.
- **Runner changes then:** materialise each spec from the source run's raw output (`ah_e8.materialise`, with the model tokenizer's offsets for the truncation point, not the proxy), send it as a continuation with max_tokens 64 (or the condition's max for mistake insertion), and score with the `sat_json` parser on the continuation text. E8 raw records would carry the source run id and the source response's cache key.

## Open questions

- **The `direct` system instruction conflicts with the item prompts**, which say "Think as carefully as you need" (A/H) or "Think it through as carefully as you need" (B4/C4). The decision record keeps the prompts unchanged; the conflict is part of the condition and is recorded, but it may raise `pre_answer_tokens`.
- **Single-vertex items (C E3 arm I)** cannot be compared with members on `answer_key` (members predict full colourings); use `channel_value`.
- **C E5 partial colouring / assignment given:** a response that omits the already-fixed vertices is `partial` (flagged `missing_only_fixed`), because the prompt asks for every vertex. Relax this only by a scorer version bump.
- **A/H decision items with a malformed witness** stay `ok` on the decision channel, with a witness flag. If witness-invalid SAT claims ("infeasible SAT claim") should be a category of their own, that is a scorer change.
