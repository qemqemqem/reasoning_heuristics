# Run 2026-11-19-repeat-pc20-gpt-oss-120b-thinking-low

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-120b`; returned `openai/gpt-oss-120b`.
- **Provider:** routing `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DekaLLM': 2760}.
- **Condition:** `thinking-low`; max_tokens 32768; reasoning `{'effort': 'low'}`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 1380 (data/items/pc20/C_E2_dev_s1.jsonl.gz, data/items/pc20/AH_E5_dev_s1.jsonl.gz, data/items/pc20/C_E1_dev_s1.jsonl.gz); skipped {'excluded_eval': 0, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 2760 responses, 0 failed calls, 1380 from cache.
- **Spend:** $0.3884 API-reported over 1 invocation(s) (last cap $0.71; dry-run estimate $3.92, worst case $16.33).
- **Code:** git `ff49489f63bf1d576da4aad6dda3632908945afb`; scorer `scorer-1.5.2` at `ff49489f63bf1d576da4aad6dda3632908945afb`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | Correct of ok |
|---|---|---|---|---|---|---|
| A/H | E5 | 680 | 678 | 2 | 0 | 328/678 (48%) |
| C | E1 | 480 | 454 | 16 | 10 | 189/454 (42%) |
| C | E2 | 1600 | 1600 | 0 | 0 | 576/1600 (36%) |
| **All** | | **2760** | **2732** | **18** | **10** | **1093/2732 (40%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E5 | COL | 160 | 341 | 556 | 322 | 512 | 319 | 0 (0%) | 160 (100%) | 0.00011 |
| A/H | E5 | ENT | 160 | 776 | 799 | 716 | 735 | 250 | 0 (0%) | 160 (100%) | 0.00015 |
| A/H | E5 | KNAP | 160 | 988 | 1,089 | 960 | 1,052 | 259 | 0 (0%) | 160 (100%) | 0.00020 |
| A/H | E5 | SAT | 200 | 3,268 | 3,071 | 3,142 | 2,930 | 1,260 | 0 (0%) | 200 (100%) | 0.00059 |
| C | E1 | COL | 240 | 1,136 | 1,186 | 1,036 | 1,081 | 477 | 0 (0%) | 240 (100%) | 0.00023 |
| C | E1 | SAT | 240 | 2,234 | 2,154 | 2,124 | 2,031 | 1,066 | 0 (0%) | 240 (100%) | 0.00042 |
| C | E2 | COL | 600 | 921 | 1,045 | 816 | 940 | 484 | 0 (0%) | 600 (100%) | 0.00020 |
| C | E2 | KNAP | 600 | 821 | 840 | 800 | 821 | 216 | 0 (0%) | 600 (100%) | 0.00016 |
| C | E2 | SAT | 400 | 2,730 | 2,713 | 2,644 | 2,622 | 1,212 | 0 (0%) | 400 (100%) | 0.00052 |
| **All** | | | **2760** | **990** | **1,458** | **931** | **1,379** | | **0** | **2760** | **0.00028** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 1, max 174; 44 responses (2%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `order_differs_from_requested` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E5-1c8b9b665a-SAT-SAT_N` | parse_fail | 13 digits for 12 variables |
| `AH-E5-807428cb05-SAT-SAT_P` | parse_fail | 13 digits for 12 variables |
| `C-E1-15ec0fc41c-SAT_c5-ANS-FREE` | partial | missing 10 variable(s): x52, x86, x47, x42, x38, x16, x63, x76, x43, x19 |
| `C-E1-15ec0fc41c-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x10, x11, x12, x13, x14, x15, x17, x18, x2 |
| `C-E1-6919e3b400-SAT_c5-ANS-FREE` | parse_fail | variable x83 given two values (False, True) |
| `C-E1-72ee36a5d2-SAT_c5-ANS-FREE` | partial | missing 6 variable(s): x99, x84, x63, x90, x64, x59 |
| `C-E1-72ee36a5d2-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x30, x31, x32, x35, x37, x38, x39, x40, x42, x43 |
| `C-E1-7bf589398d-SAT_c5-ANS-FREE` | partial | missing 9 variable(s): x42, x65, x35, x95, x83, x21, x20, x44, x71 |
| `C-E1-7bf589398d-SAT_c5-ANS-FREE` | partial | missing 12 variable(s): x42, x80, x65, x35, x95, x83, x11, x81, x63, x67 |
| `C-E1-1cd5a6cceb-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x10, x11, x12, x13, x14, x15, x16, x17, x18 |
| `C-E1-1cd5a6cceb-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x10, x11, x12, x13, x14, x15, x16, x17, x18 |
| `C-E1-3f36aaa52d-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x100, x28, x29, x31, x33, x34, x40, x41, x42, x43 |
| `C-E1-e92c328151-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x12, x13, x14, x15, x16, x17, x18, x19, x2 |
| `C-E1-e92c328151-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x12, x13, x14, x15, x16, x17, x18, x19, x2 |
| `C-E1-0211b4f1e0-SAT_c5-ANS-FREE` | partial | missing 2 variable(s): x63, x43 |
| `C-E1-348719fa81-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x10, x11, x12, x13, x14, x15, x16, x19, x2 |
| `C-E1-a1dc3b409d-SAT_c5-ANS-FREE` | partial | missing 11 variable(s): x56, x88, x62, x10, x74, x40, x77, x57, x23, x98 |
| `C-E1-1eb3f1047e-SAT_c5-ANS-FREE` | partial | missing 14 variable(s): x14, x42, x72, x32, x61, x19, x49, x81, x79, x63 |
| `C-E1-1eb3f1047e-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x10, x11, x12, x13, x15, x16, x17, x18, x2 |
| `C-E1-5df7b5ecb5-SAT_c5-ANS-FREE` | partial | missing 12 variable(s): x53, x61, x86, x85, x29, x91, x65, x67, x63, x62 |
| `C-E1-4ebeb9d55e-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x100, x12, x15, x16, x17, x18, x19, x2, x20 |
| `C-E1-4ebeb9d55e-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x100, x12, x15, x16, x17, x18, x19, x2, x20 |
| `C-E1-c044fa8953-SAT_c5-ANS-FREE` | partial | missing 1 variable(s): x96 |
| `C-E1-c044fa8953-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x100, x68, x69, x70, x71, x72, x73, x75, x77, x78 |
| `C-E1-425688c73a-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x10, x12, x13, x14, x15, x16, x18, x19, x2 |

