# Run forced-2/all-k8192/2026-11-18-dev-qwen3-32b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-32b`; returned `qwen/qwen3-32b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 70}.
- **Condition:** `thinking-high-forced-k8192`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 70 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0468 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.04, worst case $0.11).
- **Code:** git `95999b544d9e2d01e836b4ec922c091cdbb76b48`; scorer `scorer-1.5.2` at `95999b544d9e2d01e836b4ec922c091cdbb76b48`.

## Forced final answers

The responses of `2026-11-18-dev-qwen3-32b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 8192 tokens by the model's tokenizer (`Qwen/Qwen3-32B/tokenizer.json`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 70 forced responses, 69 answered and 1 went back to reasoning and stopped at max_tokens again (`truncated` below). 68 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; the source run `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`.
- **Budget:** 45 of the selected traces were within budget and not sent: their natural answers stand. 70 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 63 prompt tokens as a raw prompt and 72 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 23 of the 67 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | truncated | Correct of ok |
|---|---|---|---|---|---|---|
| A/H | E1 | 9 | 9 | 0 | 0 | 5/9 (56%) |
| A/H | E2 | 9 | 8 | 0 | 1 | 5/8 (62%) |
| A/H | E5 | 12 | 12 | 0 | 0 | 5/12 (42%) |
| C | E1 | 9 | 8 | 1 | 0 | 4/8 (50%) |
| C | E2 | 14 | 14 | 0 | 0 | 5/14 (36%) |
| C | E3 | 4 | 4 | 0 | 0 | 2/4 (50%) |
| C | E5 | 13 | 13 | 0 | 0 | 2/13 (15%) |
| **All** | | **70** | **68** | **1** | **1** | **28/68 (41%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 4 | 60 | 82 | 0 | 0 | 8,580 | 0 (0%) | 0 (0%) | 0.00057 |
| A/H | E1 | SAT | 5 | 37 | 36 | 0 | 0 | 10,727 | 0 (0%) | 0 (0%) | 0.00069 |
| A/H | E2 | COL | 4 | 168 | 166 | 0 | 0 | 8,647 | 0 (0%) | 0 (0%) | 0.00059 |
| A/H | E2 | SAT | 5 | 38 | 850 | 0 | 0 | 10,898 | 1 (20%) | 0 (0%) | 0.00089 |
| A/H | E5 | COL | 2 | 42 | 42 | 0 | 0 | 8,465 | 0 (0%) | 0 (0%) | 0.00055 |
| A/H | E5 | KNAP | 5 | 22 | 20 | 0 | 0 | 8,429 | 0 (0%) | 0 (0%) | 0.00054 |
| A/H | E5 | SAT | 5 | 25 | 25 | 0 | 0 | 9,450 | 0 (0%) | 0 (0%) | 0.00061 |
| C | E1 | COL | 4 | 510 | 459 | 0 | 0 | 8,756 | 0 (0%) | 0 (0%) | 0.00066 |
| C | E1 | SAT | 5 | 265 | 722 | 0 | 0 | 9,403 | 0 (0%) | 0 (0%) | 0.00076 |
| C | E2 | COL | 4 | 290 | 362 | 0 | 0 | 8,754 | 0 (0%) | 0 (0%) | 0.00064 |
| C | E2 | KNAP | 5 | 260 | 346 | 0 | 0 | 8,397 | 0 (0%) | 0 (0%) | 0.00061 |
| C | E2 | SAT | 5 | 267 | 360 | 0 | 0 | 9,591 | 0 (0%) | 0 (0%) | 0.00069 |
| C | E3 | COL-I | 1 | 344 | 344 | 0 | 0 | 9,748 | 0 (0%) | 0 (0%) | 0.00070 |
| C | E3 | COL-U | 3 | 473 | 473 | 0 | 0 | 10,014 | 0 (0%) | 0 (0%) | 0.00075 |
| C | E5 | COL | 5 | 171 | 227 | 0 | 0 | 8,852 | 0 (0%) | 0 (0%) | 0.00062 |
| C | E5 | SAT | 5 | 418 | 427 | 0 | 0 | 9,935 | 0 (0%) | 0 (0%) | 0.00073 |
| C | E5 | STATE | 3 | 378 | 305 | 0 | 0 | 9,638 | 0 (0%) | 0 (0%) | 0.00069 |
| **All** | | | **70** | **184** | **316** | **0** | **0** | | **1** | **0** | **0.00067** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 227, max 4,097; 32 responses (46%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `latex_unwrapped` | 3 |
| `witness_partial` | 2 |
| `positional_values` | 2 |
| `fenced_answer_no_marker` | 1 |
| `order_differs_from_requested` | 1 |
| `extra_text_in_block` | 1 |
| `no_answer_marker` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E1-15ec0fc41c-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x58 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E2 | SAT/J/g=SAT | 1 |

