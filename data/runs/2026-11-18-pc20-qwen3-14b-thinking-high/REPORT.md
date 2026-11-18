# Run 2026-11-18-pc20-qwen3-14b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-14b`; returned `qwen/qwen3-14b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 1380}.
- **Condition:** `thinking-high`; max_tokens 32768; reasoning `{'effort': 'high'}`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 1380 (data/items/pc20/C_E2_dev_s1.jsonl.gz, data/items/pc20/AH_E5_dev_s1.jsonl.gz, data/items/pc20/C_E1_dev_s1.jsonl.gz); skipped {'excluded_eval': 0, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 1380 responses, 0 failed calls, 160 from cache.
- **Spend:** $3.0230 API-reported over 1 invocation(s) (last cap $4.00; dry-run estimate $2.15, worst case $8.77).
- **Code:** git `9f33eaae34ec5c7affccdaf2744e5d74a4221624`; scorer `scorer-1.5.1` at `34f2a739e3b2b71721f4ec75aa792469f382b395`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | truncated | Correct of ok |
|---|---|---|---|---|---|---|
| A/H | E5 | 340 | 331 | 2 | 7 | 237/331 (72%) |
| C | E1 | 240 | 236 | 2 | 2 | 178/236 (75%) |
| C | E2 | 800 | 764 | 24 | 12 | 427/764 (56%) |
| **All** | | **1380** | **1331** | **28** | **21** | **842/1331 (63%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E5 | COL | 80 | 5,958 | 7,628 | 4,957 | 6,400 | 267 | 2 (2%) | 80 (100%) | 0.00149 |
| A/H | E5 | ENT | 80 | 2,720 | 2,935 | 2,554 | 2,788 | 192 | 0 (0%) | 80 (100%) | 0.00058 |
| A/H | E5 | KNAP | 80 | 9,466 | 9,550 | 6,082 | 6,226 | 215 | 0 (0%) | 80 (100%) | 0.00185 |
| A/H | E5 | SAT | 100 | 19,028 | 19,426 | 12,326 | 12,620 | 1,387 | 5 (5%) | 100 (100%) | 0.00386 |
| C | E1 | COL | 120 | 8,830 | 9,375 | 5,584 | 5,912 | 536 | 0 (0%) | 120 (100%) | 0.00185 |
| C | E1 | SAT | 120 | 14,746 | 15,908 | 9,204 | 9,926 | 1,276 | 2 (2%) | 120 (100%) | 0.00318 |
| C | E2 | COL | 300 | 8,441 | 8,909 | 5,326 | 5,646 | 545 | 0 (0%) | 300 (100%) | 0.00176 |
| C | E2 | KNAP | 300 | 12,650 | 13,145 | 7,016 | 7,340 | 181 | 0 (0%) | 300 (100%) | 0.00254 |
| C | E2 | SAT | 200 | 20,114 | 20,440 | 12,430 | 12,726 | 1,465 | 12 (6%) | 200 (100%) | 0.00407 |
| **All** | | | **1380** | **11,630** | **12,529** | **6,990** | **7,853** | | **21** | **1380** | **0.00247** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 140, max 879; 420 responses (30%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `latex_unwrapped` | 186 |
| `answer_after_lead_in` | 98 |
| `no_answer_marker` | 32 |
| `extra_text_in_block` | 19 |
| `fenced_answer_no_marker` | 4 |
| `order_differs_from_requested` | 3 |
| `repeated_variable` | 1 |
| `positional_values` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E2-17774e248d-COL_DSATUR-vs-LF_G-ONLY` | parse_fail | no answer block |
| `C-E2-14dd49ad87-SAT_GREEDY-vs-POLARITY_BASE` | parse_fail | no answer block |
| `C-E2-1b8cbaa480-KNAP_RATIO-vs-DIFF_PLACEBO` | parse_fail | no answer block |
| `C-E2-1b8cbaa480-KNAP_RATIO-vs-DIFF_G-ONLY` | parse_fail | no answer block |
| `C-E2-9b5e0c0481-KNAP_RATIO-vs-VALUE_D(VALUE_RATIO)` | parse_fail | no answer block |
| `C-E2-63789994a0-KNAP_RATIO-vs-DIFF_PLACEBO` | parse_fail | no answer block |
| `C-E2-4ee55ab373-KNAP_RATIO-vs-VALUE_D(VALUE_RATIO)` | parse_fail | no answer block |
| `C-E2-382814412c-KNAP_RATIO-vs-VALUE_BASE` | parse_fail | no answer block |
| `C-E2-382814412c-KNAP_RATIO-vs-VALUE_D(VALUE_RATIO)` | parse_fail | no answer block |
| `C-E2-382814412c-KNAP_RATIO-vs-VALUE_G-ONLY` | parse_fail | no answer block |
| `C-E2-7b3eb86931-KNAP_RATIO-vs-DIFF_PLACEBO` | parse_fail | no answer block |
| `C-E2-d71c196792-KNAP_PREFIX-vs-RATIO_G-ONLY` | parse_fail | no answer block |
| `C-E2-5438ab1d24-KNAP_RATIO-vs-DIFF_D(RATIO_DIFF)` | parse_fail | no answer block |
| `C-E2-cd5771888e-KNAP_RATIO-vs-VALUE_PLACEBO` | parse_fail | no answer block |
| `C-E2-2562f01ee9-KNAP_RATIO-vs-DIFF_G-ONLY` | parse_fail | no answer block |
| `C-E2-3ce4b01af8-KNAP_RATIO-vs-VALUE_PLACEBO` | parse_fail | no answer block |
| `C-E2-5317cd9eab-KNAP_RATIO-vs-DIFF_PLACEBO` | parse_fail | no answer block |
| `C-E2-87110f5f03-KNAP_RATIO-vs-DIFF_D(DIFF_RATIO)` | parse_fail | no answer block |
| `C-E2-fbe877a9ed-KNAP_PREFIX-vs-RATIO_G-ONLY` | parse_fail | no answer block |
| `C-E2-f27c9880a8-KNAP_PREFIX-vs-RATIO_PLACEBO` | parse_fail | no answer block |
| `C-E2-916a1826d0-KNAP_PREFIX-vs-RATIO_BASE` | parse_fail | no answer block |
| `C-E2-4299d82b5f-KNAP_PREFIX-vs-RATIO_D(PREFIX_RATIO)` | parse_fail | no answer block |
| `C-E2-5a4557445d-KNAP_PREFIX-vs-RATIO_BASE` | parse_fail | no answer block |
| `C-E2-e36a305251-KNAP_PREFIX-vs-RATIO_BASE` | parse_fail | no answer block |
| `AH-E5-28b3419632-COL-COL_N` | parse_fail | room None for Kim |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E1 | SAT/c1-NAT | 1 |
| E1 | SAT/c2-RELABEL | 1 |
| E2 | SAT/GREEDY-vs-POLARITY/BASE | 2 |
| E2 | SAT/GREEDY-vs-POLARITY/D(POLARITY|GREEDY) | 2 |
| E2 | SAT/GREEDY-vs-POLARITY/G-ONLY | 1 |
| E2 | SAT/GREEDY-vs-UC/BASE | 3 |
| E2 | SAT/GREEDY-vs-UC/D(GREEDY|UC) | 2 |
| E2 | SAT/GREEDY-vs-UC/PLACEBO | 2 |
| E5 | COL/I | 2 |
| E5 | SAT/I | 2 |
| E5 | SAT/N | 1 |
| E5 | SAT/P | 1 |
| E5 | SAT/T | 1 |

