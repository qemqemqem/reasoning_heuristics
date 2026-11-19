# Run forced-2/cut/2026-11-18-budget-dev-gpt-oss-20b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-20b`; returned `openai/gpt-oss-20b`.
- **Provider:** routing `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DeepInfra': 198}.
- **Condition:** `thinking-high+budget-forced`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 198 (data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_room': 0}.
- **Status:** complete; 198 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.2020 API-reported over 1 invocation(s) (last cap $0.40; dry-run estimate $0.20, worst case $0.31).
- **Code:** git `2937a238d2026e6571eb4a5d8b60d032a3916046`; scorer `scorer-1.5.2` at `2937a238d2026e6571eb4a5d8b60d032a3916046`.

## Forced final answers

The responses of `2026-11-18-budget-dev-gpt-oss-20b-thinking-high` that stopped at the cap with a reasoning trace, replayed with the thinking closed (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096, logit_bias `{'200005': -100, '200006': -100, '200007': -100}`): 198 selected; 0 skipped (no trace); 0 skipped (no room). Of 198 forced responses, 198 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below). 194 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; the source run `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`.
- **Raw-prompt check:** the same text gave 93 prompt tokens as a raw prompt and 147 as a chat user message, so the provider passed the raw prompt through.

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | Correct of ok |
|---|---|---|---|---|---|---|
| A/H | E2 | 71 | 70 | 1 | 0 | 40/70 (57%) |
| C | E2 | 127 | 124 | 2 | 1 | 67/124 (54%) |
| **All** | | **198** | **194** | **3** | **1** | **107/194 (55%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E2 | COL | 31 | 11 | 138 | 0 | 0 | 33,302 | 0 (0%) | 0 (0%) | 0.00102 |
| A/H | E2 | SAT | 40 | 23 | 38 | 0 | 0 | 35,116 | 0 (0%) | 0 (0%) | 0.00106 |
| C | E2 | COL | 18 | 104 | 228 | 0 | 0 | 33,294 | 0 (0%) | 0 (0%) | 0.00103 |
| C | E2 | KNAP | 67 | 9 | 21 | 0 | 0 | 33,021 | 0 (0%) | 0 (0%) | 0.00099 |
| C | E2 | SAT | 42 | 89 | 70 | 0 | 0 | 34,034 | 0 (0%) | 0 (0%) | 0.00103 |
| **All** | | | **198** | **14** | **72** | **0** | **0** | | **0** | **0** | **0.00102** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 29, max 2,090; 14 responses (7%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `witness_malformed` | 19 |
| `order_differs_from_requested` | 16 |
| `no_answer_marker` | 11 |
| `extra_text_in_block` | 8 |
| `witness_partial` | 5 |
| `fenced_answer_no_marker` | 2 |
| `text_after_answer` | 2 |
| `latex_unwrapped` | 1 |
| `repeated_item` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E2-5b9e32dcea-SAT_GREEDY-vs-POLARITY_G-ONLY` | partial | missing 18 variable(s): x55, x34, x52, x14, x23, x85, x70, x92, x68, x69 |
| `C-E2-effa8ba7e3-SAT_GREEDY-vs-UC_PLACEBO` | parse_fail | no answer block |
| `C-E2-68929de3b8-KNAP_RATIO-vs-VALUE_D(RATIO_VALUE)` | parse_fail | no answer block |
| `AH-E2-beae284e57-SAT-SAT-SAT_J_g=SAT` | parse_fail | no answer block |

