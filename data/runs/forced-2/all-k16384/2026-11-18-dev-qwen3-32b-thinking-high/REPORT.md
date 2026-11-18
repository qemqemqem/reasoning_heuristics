# Run forced-2/all-k16384/2026-11-18-dev-qwen3-32b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-32b`; returned `qwen/qwen3-32b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 31}.
- **Condition:** `thinking-high-forced-k16384`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 31 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0367 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.04, worst case $0.06).
- **Code:** git `95999b544d9e2d01e836b4ec922c091cdbb76b48`; scorer `scorer-1.5.2` at `95999b544d9e2d01e836b4ec922c091cdbb76b48`.

## Forced final answers

The responses of `2026-11-18-dev-qwen3-32b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 16384 tokens by the model's tokenizer (`Qwen/Qwen3-32B/tokenizer.json`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 31 forced responses, 31 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below). 31 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; the source run `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`.
- **Budget:** 84 of the selected traces were within budget and not sent: their natural answers stand. 31 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 63 prompt tokens as a raw prompt and 72 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 9 of the 29 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | Correct of ok |
|---|---|---|---|---|
| A/H | E1 | 7 | 7 | 4/7 (57%) |
| A/H | E2 | 7 | 7 | 5/7 (71%) |
| A/H | E5 | 3 | 3 | 0/3 (0%) |
| C | E1 | 1 | 1 | 1/1 (100%) |
| C | E2 | 5 | 5 | 0/5 (0%) |
| C | E5 | 8 | 8 | 2/8 (25%) |
| **All** | | **31** | **31** | **12/31 (39%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 2 | 168 | 168 | 0 | 0 | 16,815 | 0 (0%) | 0 (0%) | 0.00111 |
| A/H | E1 | SAT | 5 | 37 | 37 | 0 | 0 | 18,920 | 0 (0%) | 0 (0%) | 0.00122 |
| A/H | E2 | COL | 2 | 255 | 255 | 0 | 0 | 16,918 | 0 (0%) | 0 (0%) | 0.00114 |
| A/H | E2 | SAT | 5 | 37 | 33 | 0 | 0 | 19,090 | 0 (0%) | 0 (0%) | 0.00123 |
| A/H | E5 | SAT | 3 | 25 | 25 | 0 | 0 | 17,632 | 0 (0%) | 0 (0%) | 0.00113 |
| C | E1 | COL | 1 | 166 | 166 | 0 | 0 | 16,902 | 0 (0%) | 0 (0%) | 0.00112 |
| C | E2 | SAT | 5 | 207 | 278 | 0 | 0 | 17,783 | 0 (0%) | 0 (0%) | 0.00120 |
| C | E5 | COL | 4 | 172 | 131 | 0 | 0 | 17,044 | 0 (0%) | 0 (0%) | 0.00112 |
| C | E5 | SAT | 4 | 322 | 328 | 0 | 0 | 18,128 | 0 (0%) | 0 (0%) | 0.00123 |
| **All** | | | **31** | **103** | **150** | **0** | **0** | | **0** | **0** | **0.00118** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 66, max 651; 7 responses (23%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `witness_partial` | 2 |
| `witness_malformed` | 1 |
| `extra_text_in_block` | 1 |
| `order_differs_from_requested` | 1 |
| `repeated_variable` | 1 |
| `no_answer_marker` | 1 |

