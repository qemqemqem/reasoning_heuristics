# Run 2026-11-18-dev-qwen3-14b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-14b`; returned `qwen/qwen3-14b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 1270}.
- **Condition:** `thinking-high`; max_tokens 32768; reasoning `{'effort': 'high'}`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 1270 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'excluded_eval': 60, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 1270 responses, 0 failed calls, 0 from cache.
- **Spend:** $2.2878 API-reported over 3 invocation(s) (last cap $0.20; dry-run estimate $1.91, worst case $8.08).
- **Code:** git `62d8345a6eec0691e8eb0c36f085239c09d1f46e`; scorer `scorer-1.5.1` at `34f2a739e3b2b71721f4ec75aa792469f382b395`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | truncated | Correct of ok |
|---|---|---|---|---|---|---|---|
| A/H | E1 | 70 | 65 | 0 | 0 | 5 | 49/65 (75%) |
| A/H | E2 | 120 | 113 | 0 | 0 | 7 | 88/113 (78%) |
| A/H | E5 | 85 | 82 | 1 | 0 | 2 | 61/82 (74%) |
| B4/C4 | E1 | 140 | 140 | 0 | 0 | 0 | 140/140 (100%) |
| B4/C4 | E2 | 240 | 240 | 0 | 0 | 0 | 240/240 (100%) |
| C | E1 | 60 | 59 | 1 | 0 | 0 | 48/59 (81%) |
| C | E2 | 200 | 187 | 7 | 0 | 6 | 98/187 (52%) |
| C | E3 | 270 | 242 | 19 | 2 | 7 | 217/242 (90%) |
| C | E5 | 85 | 83 | 1 | 0 | 1 | 50/83 (60%) |
| **All** | | **1270** | **1211** | **29** | **2** | **28** | **991/1211 (82%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 20 | 12,993 | 12,466 | 10,634 | 10,158 | 347 | 0 (0%) | 20 (100%) | 0.00243 |
| A/H | E1 | ENT | 20 | 1,688 | 1,857 | 1,574 | 1,675 | 200 | 0 (0%) | 20 (100%) | 0.00038 |
| A/H | E1 | SAT | 30 | 20,720 | 20,092 | 12,398 | 12,638 | 2,132 | 5 (17%) | 30 (100%) | 0.00406 |
| A/H | E2 | COL | 40 | 12,246 | 10,975 | 10,232 | 8,938 | 438 | 1 (2%) | 40 (100%) | 0.00215 |
| A/H | E2 | ENT | 40 | 1,474 | 1,645 | 1,355 | 1,546 | 187 | 0 (0%) | 40 (100%) | 0.00033 |
| A/H | E2 | SAT | 40 | 26,340 | 26,600 | 16,256 | 16,450 | 2,741 | 6 (15%) | 40 (100%) | 0.00537 |
| A/H | E5 | COL | 20 | 4,621 | 6,502 | 3,980 | 5,565 | 255 | 0 (0%) | 20 (100%) | 0.00127 |
| A/H | E5 | ENT | 20 | 2,302 | 2,609 | 2,320 | 2,487 | 195 | 0 (0%) | 20 (100%) | 0.00052 |
| A/H | E5 | KNAP | 20 | 9,724 | 10,044 | 6,048 | 6,383 | 217 | 0 (0%) | 20 (100%) | 0.00195 |
| A/H | E5 | SAT | 25 | 18,767 | 19,516 | 12,558 | 12,701 | 1,340 | 2 (8%) | 25 (100%) | 0.00388 |
| B4/C4 | E1 | ENT | 140 | 941 | 1,476 | 918 | 1,189 | 121 | 0 (0%) | 140 (100%) | 0.00030 |
| B4/C4 | E2 | ENT | 240 | 498 | 510 | 508 | 512 | 118 | 0 (0%) | 240 (100%) | 0.00011 |
| C | E1 | COL | 30 | 9,898 | 9,716 | 6,375 | 6,119 | 536 | 0 (0%) | 30 (100%) | 0.00192 |
| C | E1 | SAT | 30 | 13,813 | 14,977 | 8,674 | 9,358 | 1,259 | 0 (0%) | 30 (100%) | 0.00300 |
| C | E2 | COL | 75 | 8,794 | 9,501 | 5,662 | 6,025 | 550 | 0 (0%) | 75 (100%) | 0.00188 |
| C | E2 | KNAP | 75 | 12,801 | 13,870 | 7,196 | 7,742 | 181 | 1 (1%) | 75 (100%) | 0.00268 |
| C | E2 | SAT | 50 | 21,548 | 21,837 | 12,944 | 13,627 | 1,467 | 5 (10%) | 50 (100%) | 0.00433 |
| C | E3 | COL-I | 90 | 9,298 | 9,461 | 5,662 | 5,715 | 1,532 | 0 (0%) | 90 (100%) | 0.00196 |
| C | E3 | COL-U | 180 | 14,352 | 15,302 | 8,043 | 8,628 | 1,798 | 7 (4%) | 180 (100%) | 0.00311 |
| C | E5 | COL | 25 | 16,718 | 17,043 | 9,597 | 10,084 | 637 | 0 (0%) | 25 (100%) | 0.00333 |
| C | E5 | ENT | 20 | 1,692 | 1,746 | 1,388 | 1,385 | 73 | 0 (0%) | 20 (100%) | 0.00034 |
| C | E5 | SAT | 15 | 20,475 | 20,692 | 12,889 | 13,398 | 1,716 | 1 (7%) | 15 (100%) | 0.00414 |
| C | E5 | STATE | 25 | 8,000 | 8,839 | 5,169 | 5,565 | 1,098 | 0 (0%) | 25 (100%) | 0.00180 |
| **All** | | | **1270** | **8,612** | **9,324** | **5,258** | **5,870** | | **28** | **1270** | **0.00187** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 115, max 2,446; 305 responses (24%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `latex_unwrapped` | 180 |
| `answer_after_lead_in` | 20 |
| `no_answer_marker` | 19 |
| `witness_malformed` | 5 |
| `witness_partial` | 5 |
| `extra_text_in_block` | 4 |
| `order_differs_from_requested` | 3 |
| `fenced_answer_no_marker` | 2 |
| `repeated_variable` | 1 |
| `positional_values` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E5-c0cbfc3e6e-ENT-ENT_I` | parse_fail | unrecognised fact(s): ['switch is down'] |
| `C-E1-cbf51c7982-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1 |
| `C-E2-fcc6ef350c-SAT_GREEDY-vs-POLARITY_PLACEBO` | parse_fail | no answer block |
| `C-E2-97afa78f7c-KNAP_RATIO-vs-VALUE_D(VALUE_RATIO)` | parse_fail | no answer block |
| `C-E2-97afa78f7c-KNAP_RATIO-vs-VALUE_PLACEBO` | parse_fail | no answer block |
| `C-E2-68929de3b8-KNAP_RATIO-vs-VALUE_G-ONLY` | parse_fail | no answer block |
| `C-E2-41f5f64b4a-KNAP_RATIO-vs-DIFF_D(RATIO_DIFF)` | parse_fail | no answer block |
| `C-E2-1198d97fa1-KNAP_RATIO-vs-VALUE_D(VALUE_RATIO)` | parse_fail | no answer block |
| `C-E2-b4404ec2bc-KNAP_PREFIX-vs-RATIO_D(RATIO_PREFIX)` | parse_fail | no answer block |
| `C-E3-322e4cdfac-d=1_CRITICAL_I` | parse_fail | no answer block |
| `C-E3-337e67cdbd-d=2_CRITICAL_I` | parse_fail | no answer block |
| `C-E3-337e67cdbd-d=2_PLACEBO_I` | parse_fail | no answer block |
| `C-E3-d8b624d603-d=2_CRITICAL_U-REV` | partial | missing 9 vertex(s): v46, v36, v31, v17, v21, v69, v77, v49, v16 |
| `C-E3-3b60d2f9bd-d=3_CRITICAL_I` | parse_fail | no answer block |
| `C-E3-9a0cd44b4d-d=3_CRITICAL_U-REV` | partial | missing 1 vertex(s): v40 |
| `C-E3-9a0cd44b4d-d=3_CRITICAL_I` | parse_fail | no answer block |
| `C-E3-9a0cd44b4d-d=3_PLACEBO_I` | parse_fail | no answer block |
| `C-E3-03f012ed51-d=4_PLACEBO_I` | parse_fail | no answer block |
| `C-E3-f55f670046-d=4_CRITICAL_I` | parse_fail | no answer block |
| `C-E3-725dfed728-d=4_BASE_I` | parse_fail | no answer block |
| `C-E3-725dfed728-d=4_PLACEBO_I` | parse_fail | no answer block |
| `C-E3-a93af8e839-d=4_BASE_I` | parse_fail | no answer block |
| `C-E3-a93af8e839-d=4_CRITICAL_U-REV` | parse_fail | no answer block |
| `C-E3-44103b792f-d=6_BASE_I` | parse_fail | no answer block |
| `C-E3-44103b792f-d=6_CRITICAL_I` | parse_fail | no answer block |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E1 | SAT/B1/x | 1 |
| E1 | SAT/critical/x | 1 |
| E1 | SAT/critical/x-prime | 1 |
| E1 | SAT/null/x | 1 |
| E1 | SAT/null/x-prime | 1 |
| E2 | COL/K/g=impossible | 1 |
| E2 | KNAP/PREFIX-vs-RATIO/D(PREFIX|RATIO) | 1 |
| E2 | SAT/GREEDY-vs-POLARITY/D(GREEDY|POLARITY) | 1 |
| E2 | SAT/GREEDY-vs-POLARITY/G-ONLY | 1 |
| E2 | SAT/GREEDY-vs-UC/D(UC|GREEDY) | 1 |
| E2 | SAT/GREEDY-vs-UC/G-ONLY | 1 |
| E2 | SAT/GREEDY-vs-UC/PLACEBO | 1 |
| E2 | SAT/J/g=SAT | 2 |
| E2 | SAT/K/g=SAT | 2 |
| E2 | SAT/K/g=UNSAT | 2 |
| E3 | d=1/CRITICAL/U-LIST | 1 |
| E3 | d=1/PLACEBO/U-LIST | 1 |
| E3 | d=3/BASE/U-LIST | 1 |
| E3 | d=3/PLACEBO/U-REV | 2 |
| E3 | d=4/BASE/U-REV | 1 |
| E3 | d=8/CRITICAL/U-REV | 1 |
| E5 | SAT/CONTROL | 1 |
| E5 | SAT/I | 1 |
| E5 | SAT/P | 1 |

