# Run 2026-11-18-dev-gpt-oss-20b-thinking-low

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-20b`; returned `openai/gpt-oss-20b`.
- **Provider:** routing `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DekaLLM': 1270}.
- **Condition:** `thinking-low`; max_tokens 32768; reasoning `{'effort': 'low'}`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 1270 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'excluded_eval': 60, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 1270 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.1710 API-reported over 1 invocation(s) (last cap $3.00; dry-run estimate $1.35, worst case $5.85).
- **Code:** git `802e453b03cea85774978ff8e7041986423ebba9`; scorer `scorer-1.5.1` at `34f2a739e3b2b71721f4ec75aa792469f382b395`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | declared_impossible | partial | Correct of ok |
|---|---|---|---|---|---|---|---|
| A/H | E1 | 70 | 70 | 0 | 0 | 0 | 46/70 (66%) |
| A/H | E2 | 120 | 120 | 0 | 0 | 0 | 77/120 (64%) |
| A/H | E5 | 85 | 80 | 4 | 0 | 1 | 32/80 (40%) |
| B4/C4 | E1 | 140 | 138 | 1 | 1 | 0 | 133/138 (96%) |
| B4/C4 | E2 | 240 | 240 | 0 | 0 | 0 | 237/240 (99%) |
| C | E1 | 60 | 56 | 3 | 0 | 1 | 15/56 (27%) |
| C | E2 | 200 | 200 | 0 | 0 | 0 | 49/200 (24%) |
| C | E3 | 270 | 269 | 0 | 0 | 1 | 92/269 (34%) |
| C | E5 | 85 | 85 | 0 | 0 | 0 | 35/85 (41%) |
| **All** | | **1270** | **1258** | **8** | **1** | **3** | **716/1258 (57%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 20 | 74 | 383 | 58 | 367 | 396 | 0 (0%) | 20 (100%) | 0.00007 |
| A/H | E1 | ENT | 20 | 511 | 570 | 499 | 558 | 258 | 0 (0%) | 20 (100%) | 0.00009 |
| A/H | E1 | SAT | 30 | 1,750 | 2,028 | 1,725 | 2,005 | 1,860 | 0 (0%) | 30 (100%) | 0.00034 |
| A/H | E2 | COL | 40 | 77 | 149 | 60 | 126 | 478 | 0 (0%) | 40 (100%) | 0.00003 |
| A/H | E2 | ENT | 40 | 558 | 580 | 546 | 568 | 245 | 0 (0%) | 40 (100%) | 0.00009 |
| A/H | E2 | SAT | 40 | 484 | 1,790 | 466 | 1,768 | 2,308 | 0 (0%) | 40 (100%) | 0.00032 |
| A/H | E5 | COL | 20 | 954 | 1,199 | 886 | 1,147 | 311 | 0 (0%) | 20 (100%) | 0.00018 |
| A/H | E5 | ENT | 20 | 601 | 675 | 574 | 650 | 253 | 0 (0%) | 20 (100%) | 0.00010 |
| A/H | E5 | KNAP | 20 | 1,036 | 1,112 | 1,010 | 1,088 | 259 | 0 (0%) | 20 (100%) | 0.00016 |
| A/H | E5 | SAT | 25 | 2,636 | 2,410 | 2,618 | 2,389 | 1,219 | 0 (0%) | 25 (100%) | 0.00037 |
| B4/C4 | E1 | ENT | 140 | 228 | 318 | 181 | 230 | 177 | 0 (0%) | 140 (100%) | 0.00005 |
| B4/C4 | E2 | ENT | 240 | 86 | 96 | 75 | 81 | 174 | 0 (0%) | 240 (100%) | 0.00002 |
| C | E1 | COL | 30 | 1,426 | 1,491 | 1,322 | 1,391 | 477 | 0 (0%) | 30 (100%) | 0.00022 |
| C | E1 | SAT | 30 | 421 | 915 | 333 | 826 | 1,054 | 0 (0%) | 30 (100%) | 0.00016 |
| C | E2 | COL | 75 | 977 | 1,146 | 874 | 1,044 | 488 | 0 (0%) | 75 (100%) | 0.00017 |
| C | E2 | KNAP | 75 | 812 | 884 | 793 | 868 | 216 | 0 (0%) | 75 (100%) | 0.00013 |
| C | E2 | SAT | 50 | 269 | 1,234 | 208 | 1,184 | 1,214 | 0 (0%) | 50 (100%) | 0.00021 |
| C | E3 | COL-I | 90 | 2,180 | 2,200 | 2,170 | 2,190 | 1,226 | 0 (0%) | 90 (100%) | 0.00034 |
| C | E3 | COL-U | 180 | 108 | 483 | 92 | 407 | 1,426 | 0 (0%) | 180 (100%) | 0.00011 |
| C | E5 | COL | 25 | 79 | 372 | 68 | 356 | 544 | 0 (0%) | 25 (100%) | 0.00007 |
| C | E5 | ENT | 20 | 170 | 169 | 160 | 160 | 131 | 0 (0%) | 20 (100%) | 0.00003 |
| C | E5 | SAT | 15 | 2,711 | 2,734 | 2,597 | 2,633 | 1,406 | 0 (0%) | 15 (100%) | 0.00042 |
| C | E5 | STATE | 25 | 1,361 | 1,760 | 1,258 | 1,705 | 931 | 0 (0%) | 25 (100%) | 0.00027 |
| **All** | | | **1270** | **292** | **816** | **226** | **772** | | **0** | **1270** | **0.00013** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 9, max 567; 81 responses (6%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `no_answer_marker` | 103 |
| `latex_unwrapped` | 32 |
| `witness_malformed` | 6 |
| `witness_partial` | 5 |
| `order_differs_from_requested` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E5-4d7c112e87-SAT-SAT_N` | parse_fail | 17 digits for 16 variables |
| `AH-E5-f09867fdd5-COL-COL_I+R` | partial | missing 2: Ben, Gil |
| `AH-E5-865e6d6257-ENT-ENT_N` | parse_fail | unrecognised fact(s): ['alarm armed', 'sensor active', 'dial turned', 'timer not set', 'lever not down'] |
| `AH-E5-865e6d6257-ENT-ENT_I` | parse_fail | unrecognised fact(s): ['alarm armed', 'sensor active', 'dial turned', 'timer not set', 'lever not down'] |
| `AH-E5-a6341e7a5d-ENT-ENT_T` | parse_fail | unrecognised fact(s): ['Gate not closed'] |
| `B4C4-E1-965e066915-M-M2·CD·MC` | parse_fail | no answer block |
| `B4C4-E1-df3d3da2eb-M-M2·CD·MC` | declared_impossible | no answer block; neither |
| `C-E1-af8320d06c-COL_c6-RELIST` | parse_fail | no answer block |
| `C-E1-15ec0fc41c-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x10, x11, x12, x13, x14, x15, x17, x18, x2 |
| `C-E1-72ee36a5d2-SAT_c5-ANS-FREE` | partial | missing 16 variable(s): x41, x61, x99, x36, x33, x67, x75, x63, x52, x85 |
| `C-E1-cbf51c7982-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x10, x11, x12, x13, x16, x17, x18, x2, x21 |
| `C-E3-725dfed728-d=4_BASE_U-REV` | partial | missing 5 vertex(s): v69, v84, v56, v94, v16 |

