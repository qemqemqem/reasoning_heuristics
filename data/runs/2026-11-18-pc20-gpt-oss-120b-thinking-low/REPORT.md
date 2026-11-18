# Run 2026-11-18-pc20-gpt-oss-120b-thinking-low

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-120b`; returned `openai/gpt-oss-120b`.
- **Provider:** routing `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DekaLLM': 1380}.
- **Condition:** `thinking-low`; max_tokens 32768; reasoning `{'effort': 'low'}`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 1380 (data/items/pc20/C_E2_dev_s1.jsonl.gz, data/items/pc20/AH_E5_dev_s1.jsonl.gz, data/items/pc20/C_E1_dev_s1.jsonl.gz); skipped {'excluded_eval': 0, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 1380 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.3856 API-reported over 1 invocation(s) (last cap $0.80; dry-run estimate $1.96, worst case $8.17).
- **Code:** git `9f33eaae34ec5c7affccdaf2744e5d74a4221624`; scorer `scorer-1.5.1` at `34f2a739e3b2b71721f4ec75aa792469f382b395`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | Correct of ok |
|---|---|---|---|---|---|---|
| A/H | E5 | 340 | 339 | 1 | 0 | 160/339 (47%) |
| C | E1 | 240 | 224 | 7 | 9 | 90/224 (40%) |
| C | E2 | 800 | 800 | 0 | 0 | 296/800 (37%) |
| **All** | | **1380** | **1363** | **8** | **9** | **546/1363 (40%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E5 | COL | 80 | 305 | 485 | 198 | 438 | 319 | 0 (0%) | 80 (100%) | 0.00010 |
| A/H | E5 | ENT | 80 | 798 | 808 | 727 | 744 | 250 | 0 (0%) | 80 (100%) | 0.00015 |
| A/H | E5 | KNAP | 80 | 1,002 | 1,053 | 967 | 1,015 | 259 | 0 (0%) | 80 (100%) | 0.00020 |
| A/H | E5 | SAT | 100 | 3,318 | 3,140 | 3,196 | 2,993 | 1,260 | 0 (0%) | 100 (100%) | 0.00060 |
| C | E1 | COL | 120 | 1,142 | 1,176 | 1,041 | 1,071 | 477 | 0 (0%) | 120 (100%) | 0.00023 |
| C | E1 | SAT | 120 | 2,074 | 2,072 | 1,996 | 1,951 | 1,066 | 0 (0%) | 120 (100%) | 0.00040 |
| C | E2 | COL | 300 | 921 | 1,036 | 816 | 931 | 484 | 0 (0%) | 300 (100%) | 0.00020 |
| C | E2 | KNAP | 300 | 821 | 830 | 800 | 811 | 216 | 0 (0%) | 300 (100%) | 0.00016 |
| C | E2 | SAT | 200 | 2,730 | 2,765 | 2,647 | 2,672 | 1,212 | 0 (0%) | 200 (100%) | 0.00053 |
| **All** | | | **1380** | **972** | **1,452** | **918** | **1,373** | | **0** | **1380** | **0.00028** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 1, max 174; 22 responses (2%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E5-807428cb05-SAT-SAT_P` | parse_fail | 13 digits for 12 variables |
| `C-E1-15ec0fc41c-SAT_c5-ANS-FREE` | partial | missing 10 variable(s): x52, x86, x47, x42, x38, x16, x63, x76, x43, x19 |
| `C-E1-6919e3b400-SAT_c5-ANS-FREE` | parse_fail | variable x83 given two values (False, True) |
| `C-E1-72ee36a5d2-SAT_c5-ANS-FREE` | partial | missing 6 variable(s): x99, x84, x63, x90, x64, x59 |
| `C-E1-7bf589398d-SAT_c5-ANS-FREE` | partial | missing 9 variable(s): x42, x65, x35, x95, x83, x21, x20, x44, x71 |
| `C-E1-1cd5a6cceb-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x10, x11, x12, x13, x14, x15, x16, x17, x18 |
| `C-E1-3f36aaa52d-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x100, x28, x29, x31, x33, x34, x40, x41, x42, x43 |
| `C-E1-e92c328151-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x12, x13, x14, x15, x16, x17, x18, x19, x2 |
| `C-E1-0211b4f1e0-SAT_c5-ANS-FREE` | partial | missing 2 variable(s): x63, x43 |
| `C-E1-348719fa81-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x10, x11, x12, x13, x14, x15, x16, x19, x2 |
| `C-E1-a1dc3b409d-SAT_c5-ANS-FREE` | partial | missing 11 variable(s): x56, x88, x62, x10, x74, x40, x77, x57, x23, x98 |
| `C-E1-1eb3f1047e-SAT_c5-ANS-FREE` | partial | missing 14 variable(s): x14, x42, x72, x32, x61, x19, x49, x81, x79, x63 |
| `C-E1-5df7b5ecb5-SAT_c5-ANS-FREE` | partial | missing 12 variable(s): x53, x61, x86, x85, x29, x91, x65, x67, x63, x62 |
| `C-E1-4ebeb9d55e-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x100, x12, x15, x16, x17, x18, x19, x2, x20 |
| `C-E1-c044fa8953-SAT_c5-ANS-FREE` | partial | missing 1 variable(s): x96 |
| `C-E1-28e2b6e625-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x10, x11, x12, x13, x16, x17, x18, x19, x2 |
| `C-E1-b55d8c825c-SAT_c5-ANS-FREE` | partial | missing 12 variable(s): x47, x50, x51, x24, x60, x61, x96, x19, x33, x83 |

