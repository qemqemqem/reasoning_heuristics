# Run forced-2/all-k4096/2026-11-18-dev-qwen3-14b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-14b`; returned `qwen/qwen3-14b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 82}.
- **Condition:** `thinking-high-forced-k4096`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 82 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0453 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.04, worst case $0.11).
- **Code:** git `2c27e2b27f86f29699b08001a77d758bc9e977f4`; scorer `scorer-1.5.2` at `2c27e2b27f86f29699b08001a77d758bc9e977f4`.

## Forced final answers

The responses of `2026-11-18-dev-qwen3-14b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 4096 tokens by the model's tokenizer (`Qwen/Qwen3-32B/tokenizer.json`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 82 forced responses, 80 answered and 2 went back to reasoning and stopped at max_tokens again (`truncated` below). 80 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; the source run `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`.
- **Budget:** 33 of the selected traces were within budget and not sent: their natural answers stand. 82 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 63 prompt tokens as a raw prompt and 72 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 22 of the 81 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | truncated | Correct of ok |
|---|---|---|---|---|---|
| A/H | E1 | 10 | 10 | 0 | 7/10 (70%) |
| A/H | E2 | 9 | 7 | 2 | 4/7 (57%) |
| A/H | E5 | 13 | 13 | 0 | 5/13 (38%) |
| C | E1 | 10 | 10 | 0 | 1/10 (10%) |
| C | E2 | 15 | 15 | 0 | 4/15 (27%) |
| C | E3 | 5 | 5 | 0 | 1/5 (20%) |
| C | E5 | 20 | 20 | 0 | 5/20 (25%) |
| **All** | | **82** | **80** | **2** | **27/80 (34%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 5 | 11 | 56 | 0 | 0 | 4,468 | 0 (0%) | 0 (0%) | 0.00044 |
| A/H | E1 | SAT | 5 | 37 | 36 | 0 | 0 | 6,632 | 0 (0%) | 0 (0%) | 0.00064 |
| A/H | E2 | COL | 4 | 136 | 117 | 0 | 0 | 4,504 | 0 (0%) | 0 (0%) | 0.00045 |
| A/H | E2 | SAT | 5 | 45 | 1,662 | 0 | 0 | 6,802 | 2 (40%) | 0 (0%) | 0.00097 |
| A/H | E5 | COL | 3 | 72 | 59 | 0 | 0 | 4,382 | 0 (0%) | 0 (0%) | 0.00043 |
| A/H | E5 | KNAP | 5 | 22 | 20 | 0 | 0 | 4,333 | 0 (0%) | 0 (0%) | 0.00042 |
| A/H | E5 | SAT | 5 | 25 | 25 | 0 | 0 | 5,354 | 0 (0%) | 0 (0%) | 0.00052 |
| C | E1 | COL | 5 | 116 | 299 | 0 | 0 | 4,663 | 0 (0%) | 0 (0%) | 0.00050 |
| C | E1 | SAT | 5 | 103 | 103 | 0 | 0 | 5,307 | 0 (0%) | 0 (0%) | 0.00053 |
| C | E2 | COL | 5 | 116 | 247 | 0 | 0 | 4,658 | 0 (0%) | 0 (0%) | 0.00049 |
| C | E2 | KNAP | 5 | 11 | 297 | 0 | 0 | 4,301 | 0 (0%) | 0 (0%) | 0.00047 |
| C | E2 | SAT | 5 | 84 | 75 | 0 | 0 | 5,494 | 0 (0%) | 0 (0%) | 0.00054 |
| C | E3 | COL-I | 1 | 1,896 | 1,896 | 0 | 0 | 5,651 | 0 (0%) | 0 (0%) | 0.00091 |
| C | E3 | COL-U | 4 | 472 | 472 | 0 | 0 | 5,918 | 0 (0%) | 0 (0%) | 0.00066 |
| C | E5 | COL | 5 | 693 | 642 | 0 | 0 | 4,756 | 0 (0%) | 0 (0%) | 0.00058 |
| C | E5 | SAT | 5 | 104 | 109 | 0 | 0 | 5,839 | 0 (0%) | 0 (0%) | 0.00058 |
| C | E5 | STATE | 10 | 103 | 87 | 0 | 0 | 5,140 | 0 (0%) | 0 (0%) | 0.00051 |
| **All** | | | **82** | **103** | **282** | **0** | **0** | | **2** | **0** | **0.00055** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 191, max 4,097; 11 responses (13%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `order_differs_from_requested` | 3 |
| `no_answer_marker` | 2 |
| `answer_blocks_disagree` | 1 |
| `latex_unwrapped` | 1 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E2 | SAT/J/g=SAT | 1 |
| E2 | SAT/K/g=SAT | 1 |

