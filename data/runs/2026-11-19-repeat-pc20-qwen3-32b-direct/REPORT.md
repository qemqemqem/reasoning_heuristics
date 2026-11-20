# Run 2026-11-19-repeat-pc20-qwen3-32b-direct

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-32b`; returned `qwen/qwen3-32b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 2760}.
- **Condition:** `direct`; max_tokens 1024; reasoning `{'enabled': False}`; sampling `{'temperature': 0.7, 'top_p': 0.8, 'top_k': 20}`; system prompt: "Respond with only the final answer in the requested format. Do not explain or show your working.".
- **Items:** 1380 (data/items/pc20/C_E2_dev_s1.jsonl.gz, data/items/pc20/AH_E5_dev_s1.jsonl.gz, data/items/pc20/C_E1_dev_s1.jsonl.gz); skipped {'excluded_eval': 0, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 2760 responses, 0 failed calls, 1380 from cache.
- **Spend:** $0.0826 API-reported over 1 invocation(s) (last cap $0.30; dry-run estimate $0.17, worst case $0.75).
- **Code:** git `ff49489f63bf1d576da4aad6dda3632908945afb`; scorer `scorer-1.5.2` at `ff49489f63bf1d576da4aad6dda3632908945afb`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | truncated | Correct of ok |
|---|---|---|---|---|---|---|---|
| A/H | E5 | 680 | 669 | 10 | 1 | 0 | 36/669 (5%) |
| C | E1 | 480 | 472 | 6 | 0 | 2 | 12/472 (3%) |
| C | E2 | 1600 | 1598 | 0 | 2 | 0 | 7/1598 (0%) |
| **All** | | **2760** | **2739** | **16** | **3** | **2** | **55/2739 (2%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E5 | COL | 160 | 74 | 73 | 0 | 0 | 294 | 0 (0%) | 0 (0%) | 0.00004 |
| A/H | E5 | ENT | 160 | 26 | 25 | 0 | 0 | 219 | 0 (0%) | 0 (0%) | 0.00002 |
| A/H | E5 | KNAP | 160 | 19 | 18 | 0 | 0 | 242 | 0 (0%) | 0 (0%) | 0.00002 |
| A/H | E5 | SAT | 200 | 29 | 27 | 0 | 0 | 1,414 | 0 (0%) | 0 (0%) | 0.00010 |
| C | E1 | COL | 240 | 116 | 116 | 0 | 0 | 563 | 0 (0%) | 0 (0%) | 0.00006 |
| C | E1 | SAT | 240 | 103 | 102 | 0 | 0 | 1,303 | 2 (1%) | 0 (0%) | 0.00011 |
| C | E2 | COL | 600 | 116 | 116 | 0 | 0 | 572 | 0 (0%) | 0 (0%) | 0.00006 |
| C | E2 | KNAP | 600 | 8 | 9 | 0 | 0 | 208 | 0 (0%) | 0 (0%) | 0.00002 |
| C | E2 | SAT | 400 | 103 | 98 | 0 | 0 | 1,492 | 0 (0%) | 0 (0%) | 0.00012 |
| **All** | | | **2760** | **97** | **69** | **0** | **0** | | **2** | **0** | **0.00006** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 0, max 4; 0 responses (0%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `order_differs_from_requested` | 140 |
| `no_answer_marker` | 29 |
| `repeated_variable` | 6 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E2-5ae5a5fe63-COL_FF-vs-DSATUR_BASE` | partial | missing 1 vertex(s): v55 |
| `C-E2-6efffb290c-SAT_GREEDY-vs-POLARITY_PLACEBO` | partial | missing 1 variable(s): x94 |
| `AH-E5-1c8b9b665a-SAT-SAT_P` | parse_fail | 24 digits for 12 variables |
| `AH-E5-e6180eaf8a-SAT-SAT_T` | parse_fail | 24 digits for 12 variables |
| `AH-E5-30e355f86c-SAT-SAT_P` | parse_fail | 24 digits for 12 variables |
| `AH-E5-ded1e3e5dc-SAT-SAT_T` | partial | 15 digits for 16 variables |
| `AH-E5-4de14e5b09-SAT-SAT_I+R` | parse_fail | 24 digits for 12 variables |
| `AH-E5-4de14e5b09-SAT-SAT_P` | parse_fail | 23 digits for 12 variables |
| `AH-E5-807428cb05-SAT-SAT_I+R` | parse_fail | 24 digits for 12 variables |
| `AH-E5-807428cb05-SAT-SAT_P` | parse_fail | 24 digits for 12 variables |
| `AH-E5-19afc608cf-SAT-SAT_P` | parse_fail | 24 digits for 12 variables |
| `AH-E5-d2dc1fb011-SAT-SAT_P` | parse_fail | 24 digits for 12 variables |
| `AH-E5-be7b466562-ENT-ENT_T` | parse_fail | unrecognised fact(s): ['NOTHING'] |
| `C-E1-15ec0fc41c-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x10, x100, x11, x12, x13, x14, x15, x17, x18, x2 |
| `C-E1-15ec0fc41c-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x10, x100, x11, x12, x13, x14, x15, x17, x18, x2 |
| `C-E1-6919e3b400-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x100, x101, x102, x103, x104, x105, x106, x107, x108, x109 |
| `C-E1-6919e3b400-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x10, x100, x11, x13, x14, x15, x16, x17, x18, x19 |
| `C-E1-cbf51c7982-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x10, x11, x12, x13, x16, x17, x18, x21, x22, x23 |
| `C-E1-4ebeb9d55e-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x100, x12, x15, x16, x17, x18, x19, x2, x20 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E1 | SAT/c5-ANS-FREE | 2 |

