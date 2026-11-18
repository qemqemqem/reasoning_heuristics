# Run 2026-11-18-pc20-qwen3-32b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-32b`; returned `qwen/qwen3-32b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 1380}.
- **Condition:** `thinking-high`; max_tokens 32768; reasoning `{'effort': 'high'}`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 1380 (data/items/pc20/C_E2_dev_s1.jsonl.gz, data/items/pc20/AH_E5_dev_s1.jsonl.gz, data/items/pc20/C_E1_dev_s1.jsonl.gz); skipped {'excluded_eval': 0, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 1380 responses, 0 failed calls, 85 from cache.
- **Spend:** $3.5636 API-reported over 2 invocation(s) (last cap $4.44; dry-run estimate $2.46, worst case $10.19).
- **Code:** git `62d8345a6eec0691e8eb0c36f085239c09d1f46e`; scorer `scorer-1.5.1` at `34f2a739e3b2b71721f4ec75aa792469f382b395`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | truncated | Correct of ok |
|---|---|---|---|---|---|---|---|
| A/H | E5 | 340 | 333 | 2 | 0 | 5 | 239/333 (72%) |
| C | E1 | 240 | 236 | 1 | 1 | 2 | 179/236 (76%) |
| C | E2 | 800 | 778 | 15 | 0 | 7 | 429/778 (55%) |
| **All** | | **1380** | **1347** | **18** | **1** | **14** | **847/1347 (63%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E5 | COL | 80 | 5,390 | 6,785 | 4,446 | 5,709 | 267 | 0 (0%) | 80 (100%) | 0.00154 |
| A/H | E5 | ENT | 80 | 2,823 | 3,033 | 2,684 | 2,884 | 192 | 0 (0%) | 80 (100%) | 0.00069 |
| A/H | E5 | KNAP | 80 | 10,676 | 10,870 | 7,132 | 7,369 | 215 | 0 (0%) | 80 (100%) | 0.00245 |
| A/H | E5 | SAT | 100 | 17,255 | 18,520 | 11,766 | 12,376 | 1,387 | 5 (5%) | 100 (100%) | 0.00424 |
| C | E1 | COL | 120 | 8,553 | 9,065 | 5,546 | 5,795 | 536 | 0 (0%) | 120 (100%) | 0.00206 |
| C | E1 | SAT | 120 | 14,066 | 14,883 | 8,665 | 9,214 | 1,276 | 2 (2%) | 120 (100%) | 0.00342 |
| C | E2 | COL | 300 | 8,640 | 9,203 | 5,576 | 5,897 | 545 | 0 (0%) | 300 (100%) | 0.00210 |
| C | E2 | KNAP | 300 | 12,342 | 12,567 | 7,112 | 7,274 | 181 | 0 (0%) | 300 (100%) | 0.00283 |
| C | E2 | SAT | 200 | 18,828 | 19,695 | 11,566 | 12,163 | 1,465 | 7 (4%) | 200 (100%) | 0.00451 |
| **All** | | | **1380** | **11,614** | **12,211** | **7,092** | **7,753** | | **14** | **1380** | **0.00278** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 120, max 875; 480 responses (35%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `latex_unwrapped` | 76 |
| `positional_values` | 51 |
| `no_answer_marker` | 48 |
| `fenced_answer_no_marker` | 20 |
| `order_differs_from_requested` | 11 |
| `answer_blocks_disagree` | 5 |
| `answer_after_lead_in` | 3 |
| `extra_text_in_block` | 2 |
| `repeated_item` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E2-432f0c6987-COL_FF-vs-LF_BASE` | parse_fail | no answer block |
| `C-E2-dc5333aabd-COL_FF-vs-LF_G-ONLY` | parse_fail | no answer block |
| `C-E2-4d97257e50-COL_DSATUR-vs-LF_BASE` | parse_fail | no answer block |
| `C-E2-56961cfefb-COL_FF-vs-DSATUR_D(FF_DSATUR)` | parse_fail | no answer block |
| `C-E2-d390a4f3b2-COL_DSATUR-vs-LF_D(DSATUR_LF)` | parse_fail | no answer block |
| `C-E2-6a09f574e7-COL_DSATUR-vs-LF_PLACEBO` | parse_fail | no answer block |
| `C-E2-6a09f574e7-COL_DSATUR-vs-LF_G-ONLY` | parse_fail | no answer block |
| `C-E2-e8f03c7923-COL_FF-vs-DSATUR_PLACEBO` | parse_fail | no answer block |
| `C-E2-e8f03c7923-COL_FF-vs-DSATUR_G-ONLY` | parse_fail | no answer block |
| `C-E2-17774e248d-COL_DSATUR-vs-LF_G-ONLY` | parse_fail | no answer block |
| `C-E2-df6c957c1f-SAT_GREEDY-vs-POLARITY_D(POLARITY_GREEDY)` | parse_fail | no answer block |
| `C-E2-4ee55ab373-KNAP_RATIO-vs-VALUE_PLACEBO` | parse_fail | no answer block |
| `C-E2-7b3eb86931-KNAP_RATIO-vs-DIFF_D(RATIO_DIFF)` | parse_fail | no answer block |
| `C-E2-1d976cddea-KNAP_RATIO-vs-DIFF_D(DIFF_RATIO)` | parse_fail | no answer block |
| `C-E2-916a1826d0-KNAP_PREFIX-vs-RATIO_D(PREFIX_RATIO)` | parse_fail | no answer block |
| `AH-E5-075fde5b6a-ENT-ENT_T` | parse_fail | unrecognised fact(s): ['¬G'] |
| `AH-E5-be7b466562-ENT-ENT_I+R` | parse_fail | unrecognised fact(s): ['¬P'] |
| `C-E1-df910b4194-COL_c5-ANS-FREE` | parse_fail | no answer block |
| `C-E1-a1dc3b409d-SAT_c5-ANS-FREE` | partial | missing 1 variable(s): x23 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E1 | SAT/c1-NAT | 1 |
| E1 | SAT/c5-ANS-FREE | 1 |
| E2 | SAT/GREEDY-vs-POLARITY/BASE | 1 |
| E2 | SAT/GREEDY-vs-POLARITY/D(GREEDY|POLARITY) | 1 |
| E2 | SAT/GREEDY-vs-POLARITY/G-ONLY | 3 |
| E2 | SAT/GREEDY-vs-POLARITY/PLACEBO | 2 |
| E5 | SAT/I+R | 1 |
| E5 | SAT/N | 1 |
| E5 | SAT/P | 2 |
| E5 | SAT/T | 1 |

