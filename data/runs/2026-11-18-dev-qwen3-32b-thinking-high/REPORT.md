# Run 2026-11-18-dev-qwen3-32b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-32b`; returned `qwen/qwen3-32b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 1270}.
- **Condition:** `thinking-high`; max_tokens 32768; reasoning `{'effort': 'high'}`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 1270 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'excluded_eval': 60, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 1270 responses, 0 failed calls, 100 from cache.
- **Spend:** $2.2600 API-reported over 2 invocation(s) (last cap $5.86; dry-run estimate $2.18, worst case $9.38).
- **Code:** git `12095bc719ce00f4d3ff50c8e7f73dc16c37054a`; scorer `scorer-1.5.1` at `34f2a739e3b2b71721f4ec75aa792469f382b395`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | declared_impossible | partial | truncated | Correct of ok |
|---|---|---|---|---|---|---|---|---|
| A/H | E1 | 70 | 65 | 0 | 0 | 0 | 5 | 50/65 (77%) |
| A/H | E2 | 120 | 107 | 0 | 0 | 0 | 13 | 77/107 (72%) |
| A/H | E5 | 85 | 83 | 0 | 0 | 1 | 1 | 61/83 (73%) |
| B4/C4 | E1 | 140 | 138 | 2 | 0 | 0 | 0 | 138/138 (100%) |
| B4/C4 | E2 | 240 | 240 | 0 | 0 | 0 | 0 | 240/240 (100%) |
| C | E1 | 60 | 60 | 0 | 0 | 0 | 0 | 42/60 (70%) |
| C | E2 | 200 | 194 | 4 | 0 | 0 | 2 | 105/194 (54%) |
| C | E3 | 270 | 260 | 5 | 1 | 0 | 4 | 207/260 (80%) |
| C | E5 | 85 | 82 | 2 | 0 | 0 | 1 | 50/82 (61%) |
| **All** | | **1270** | **1229** | **13** | **1** | **1** | **26** | **970/1229 (79%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 20 | 13,674 | 13,485 | 11,078 | 10,847 | 347 | 0 (0%) | 20 (100%) | 0.00304 |
| A/H | E1 | ENT | 20 | 1,462 | 1,796 | 1,421 | 1,705 | 200 | 0 (0%) | 20 (100%) | 0.00042 |
| A/H | E1 | SAT | 30 | 23,383 | 21,568 | 14,726 | 14,002 | 2,132 | 5 (17%) | 30 (100%) | 0.00497 |
| A/H | E2 | COL | 40 | 12,866 | 13,048 | 10,646 | 10,585 | 438 | 1 (2%) | 40 (100%) | 0.00295 |
| A/H | E2 | ENT | 40 | 1,475 | 1,737 | 1,436 | 1,615 | 187 | 0 (0%) | 40 (100%) | 0.00040 |
| A/H | E2 | SAT | 40 | 26,110 | 26,050 | 15,142 | 15,374 | 2,741 | 12 (30%) | 40 (100%) | 0.00601 |
| A/H | E5 | COL | 20 | 5,487 | 5,858 | 4,488 | 5,017 | 255 | 0 (0%) | 20 (100%) | 0.00133 |
| A/H | E5 | ENT | 20 | 2,600 | 2,950 | 2,462 | 2,835 | 195 | 0 (0%) | 20 (100%) | 0.00067 |
| A/H | E5 | KNAP | 20 | 11,067 | 11,014 | 7,400 | 7,397 | 217 | 0 (0%) | 20 (100%) | 0.00248 |
| A/H | E5 | SAT | 25 | 17,308 | 19,189 | 12,067 | 12,840 | 1,340 | 1 (4%) | 25 (100%) | 0.00438 |
| B4/C4 | E1 | ENT | 140 | 1,168 | 1,385 | 858 | 1,004 | 121 | 0 (0%) | 140 (100%) | 0.00032 |
| B4/C4 | E2 | ENT | 240 | 464 | 512 | 416 | 438 | 118 | 0 (0%) | 240 (100%) | 0.00012 |
| C | E1 | COL | 30 | 8,198 | 9,160 | 5,352 | 5,847 | 536 | 0 (0%) | 30 (100%) | 0.00209 |
| C | E1 | SAT | 30 | 13,308 | 14,190 | 8,138 | 8,737 | 1,259 | 0 (0%) | 30 (100%) | 0.00326 |
| C | E2 | COL | 75 | 9,102 | 9,906 | 5,748 | 6,327 | 550 | 0 (0%) | 75 (100%) | 0.00225 |
| C | E2 | KNAP | 75 | 12,433 | 12,775 | 7,151 | 7,330 | 181 | 0 (0%) | 75 (100%) | 0.00287 |
| C | E2 | SAT | 50 | 19,773 | 20,587 | 12,468 | 12,544 | 1,467 | 2 (4%) | 50 (100%) | 0.00471 |
| C | E3 | COL-I | 90 | 7,294 | 8,125 | 4,522 | 4,816 | 1,532 | 1 (1%) | 90 (100%) | 0.00192 |
| C | E3 | COL-U | 180 | 9,653 | 11,565 | 5,489 | 6,540 | 1,798 | 3 (2%) | 180 (100%) | 0.00271 |
| C | E5 | COL | 25 | 15,719 | 16,375 | 9,807 | 9,970 | 637 | 1 (4%) | 25 (100%) | 0.00371 |
| C | E5 | ENT | 20 | 1,612 | 1,480 | 1,162 | 1,143 | 73 | 0 (0%) | 20 (100%) | 0.00034 |
| C | E5 | SAT | 15 | 19,360 | 20,590 | 12,415 | 12,647 | 1,716 | 0 (0%) | 15 (100%) | 0.00472 |
| C | E5 | STATE | 25 | 7,755 | 7,881 | 4,801 | 4,872 | 1,098 | 0 (0%) | 25 (100%) | 0.00184 |
| **All** | | | **1270** | **7,721** | **8,636** | **4,728** | **5,456** | | **26** | **1270** | **0.00199** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 151, max 15,449; 468 responses (37%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `latex_unwrapped` | 150 |
| `no_answer_marker` | 47 |
| `positional_values` | 16 |
| `witness_malformed` | 7 |
| `extra_text_in_block` | 7 |
| `fenced_answer_no_marker` | 4 |
| `witness_missing` | 3 |
| `answer_blocks_disagree` | 2 |
| `witness_partial` | 1 |
| `order_differs_from_requested` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E5-7044bcf4a8-COL-COL_I+R` | partial | missing 1: Gil |
| `B4C4-E1-df3d3da2eb-M-M2·CD·MC` | parse_fail | no answer block |
| `B4C4-E1-4c7763ff06-V-V1·CD·MC` | parse_fail | no answer block |
| `C-E2-4d97257e50-COL_DSATUR-vs-LF_BASE` | parse_fail | no answer block |
| `C-E2-d390a4f3b2-COL_DSATUR-vs-LF_D(DSATUR_LF)` | parse_fail | no answer block |
| `C-E2-1ea790987a-KNAP_RATIO-vs-VALUE_G-ONLY` | parse_fail | no answer block |
| `C-E2-f45cf49a26-KNAP_RATIO-vs-DIFF_D(RATIO_DIFF)` | parse_fail | no answer block |
| `C-E3-a27fc7978c-d=2_CRITICAL_I` | parse_fail | no answer block |
| `C-E3-337e67cdbd-d=2_PLACEBO_U-REV` | parse_fail | no answer block |
| `C-E3-8edbf52414-d=3_CRITICAL_I` | declared_impossible | no answer block; neither |
| `C-E3-9a0cd44b4d-d=3_BASE_I` | parse_fail | no answer block |
| `C-E3-9a0cd44b4d-d=3_PLACEBO_U-LIST` | parse_fail | no `vertex: value` pairs: 'All vertices have been successfully colored with one of three colors such that no two adjacent vertices share the |
| `C-E3-0d95f6520b-d=8_BASE_U-REV` | parse_fail | no answer block |
| `C-E5-5d2f33a016-STATE_SAT_s2` | parse_fail | no answer block |
| `C-E5-3d0c055cdd-ENT_FAIL_ORDER-A` | parse_fail | no answer block |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E1 | SAT/B1/x-prime | 2 |
| E1 | SAT/critical/x | 1 |
| E1 | SAT/null/x | 2 |
| E2 | COL/base/g=possible | 1 |
| E2 | SAT/GREEDY-vs-POLARITY/BASE | 1 |
| E2 | SAT/GREEDY-vs-POLARITY/G-ONLY | 1 |
| E2 | SAT/J/g=SAT | 2 |
| E2 | SAT/J/g=UNSAT | 3 |
| E2 | SAT/K/g=UNSAT | 1 |
| E2 | SAT/U/g=SAT | 1 |
| E2 | SAT/U/g=UNSAT | 3 |
| E2 | SAT/base/g=SAT | 1 |
| E2 | SAT/base/g=UNSAT | 1 |
| E3 | d=1/PLACEBO/U-REV | 1 |
| E3 | d=4/BASE/I | 1 |
| E3 | d=6/PLACEBO/U-REV | 1 |
| E3 | d=8/BASE/U-REV | 1 |
| E5 | COL/STUCK/vB/eA | 1 |
| E5 | SAT/N | 1 |

