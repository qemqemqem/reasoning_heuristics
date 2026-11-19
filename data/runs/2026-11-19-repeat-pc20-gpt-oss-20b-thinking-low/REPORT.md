# Run 2026-11-19-repeat-pc20-gpt-oss-20b-thinking-low

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-20b`; returned `openai/gpt-oss-20b`.
- **Provider:** routing `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DekaLLM': 2760}.
- **Condition:** `thinking-low`; max_tokens 32768; reasoning `{'effort': 'low'}`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 1380 (data/items/pc20/C_E2_dev_s1.jsonl.gz, data/items/pc20/AH_E5_dev_s1.jsonl.gz, data/items/pc20/C_E1_dev_s1.jsonl.gz); skipped {'excluded_eval': 0, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 2760 responses, 0 failed calls, 1380 from cache.
- **Spend:** $0.2740 API-reported over 1 invocation(s) (last cap $0.60; dry-run estimate $3.06, worst case $12.71).
- **Code:** git `ff49489f63bf1d576da4aad6dda3632908945afb`; scorer `scorer-1.5.2` at `ff49489f63bf1d576da4aad6dda3632908945afb`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | Correct of ok |
|---|---|---|---|---|---|---|
| A/H | E5 | 680 | 653 | 22 | 5 | 280/653 (43%) |
| C | E1 | 480 | 457 | 20 | 3 | 149/457 (33%) |
| C | E2 | 1600 | 1599 | 1 | 0 | 453/1599 (28%) |
| **All** | | **2760** | **2709** | **43** | **8** | **882/2709 (33%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E5 | COL | 160 | 875 | 918 | 798 | 868 | 319 | 0 (0%) | 160 (100%) | 0.00014 |
| A/H | E5 | ENT | 160 | 639 | 678 | 618 | 656 | 250 | 0 (0%) | 160 (100%) | 0.00010 |
| A/H | E5 | KNAP | 160 | 1,169 | 1,284 | 1,148 | 1,260 | 259 | 0 (0%) | 160 (100%) | 0.00019 |
| A/H | E5 | SAT | 200 | 1,962 | 2,299 | 1,942 | 2,277 | 1,260 | 0 (0%) | 200 (100%) | 0.00036 |
| C | E1 | COL | 240 | 1,323 | 1,391 | 1,220 | 1,288 | 477 | 0 (0%) | 240 (100%) | 0.00021 |
| C | E1 | SAT | 240 | 1,082 | 1,308 | 876 | 1,182 | 1,066 | 0 (0%) | 240 (100%) | 0.00021 |
| C | E2 | COL | 600 | 1,144 | 1,254 | 1,042 | 1,150 | 484 | 0 (0%) | 600 (100%) | 0.00019 |
| C | E2 | KNAP | 600 | 854 | 910 | 836 | 894 | 216 | 0 (0%) | 600 (100%) | 0.00013 |
| C | E2 | SAT | 400 | 1,447 | 1,633 | 1,436 | 1,576 | 1,212 | 0 (0%) | 400 (100%) | 0.00026 |
| **All** | | | **2760** | **1,024** | **1,275** | **970** | **1,214** | | **0** | **2760** | **0.00020** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 0, max 180; 4 responses (0%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `order_differs_from_requested` | 9 |
| `extra_text_in_block` | 1 |
| `repeated_item` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E2-d556fa2cc7-COL_FF-vs-DSATUR_G-ONLY` | parse_fail | no answer block |
| `AH-E5-4d7c112e87-SAT-SAT_N` | parse_fail | 17 digits for 16 variables |
| `AH-E5-24d476e87e-SAT-SAT_N` | partial | 15 digits for 16 variables |
| `AH-E5-ded1e3e5dc-SAT-SAT_N` | parse_fail | 17 digits for 16 variables |
| `AH-E5-ded1e3e5dc-SAT-SAT_I` | parse_fail | 20 digits for 16 variables |
| `AH-E5-ded1e3e5dc-SAT-SAT_I+R` | parse_fail | 17 digits for 16 variables |
| `AH-E5-643ef3947c-SAT-SAT_I+R` | partial | 11 digits for 12 variables |
| `AH-E5-a616e788ae-SAT-SAT_N` | partial | no assignment |
| `AH-E5-0eb1a2da47-COL-COL_I` | partial | missing 1: Oli |
| `AH-E5-28b3419632-COL-COL_T` | partial | missing 1: Pia |
| `AH-E5-c2854a89d6-COL-COL_T` | parse_fail | unknown name(s): Megan |
| `AH-E5-e3a97a6906-ENT-ENT_I+R` | parse_fail | unrecognised fact(s): ['motor running', 'sensor active', 'lever not down', 'buzzer not sounding', 'pump not running'] |
| `AH-E5-fea9ce5136-ENT-ENT_N` | parse_fail | unrecognised fact(s): ['dial not turned'] |
| `AH-E5-a3c3032647-ENT-ENT_N` | parse_fail | unrecognised fact(s): ['relay NOT CLOSED', 'alarm ARMED', 'gate NOT CLOSED'] |
| `AH-E5-a3c3032647-ENT-ENT_I` | parse_fail | unrecognised fact(s): ['gate closed', 'switch not up'] |
| `AH-E5-a3c3032647-ENT-ENT_I+R` | parse_fail | unrecognised fact(s): ['switch is down'] |
| `AH-E5-075fde5b6a-ENT-ENT_I` | parse_fail | unrecognised fact(s): ['G gauge is high', 'D door is not open', 'R relay is open', 'B bell is not ringing'] |
| `AH-E5-94a645090c-ENT-ENT_T` | parse_fail | unrecognised fact(s): ['motor not running', 'heater not on'] |
| `AH-E5-94a645090c-ENT-ENT_I+R` | parse_fail | unrecognised fact(s): ['pump running', 'door open'] |
| `AH-E5-3386a6bdc1-ENT-ENT_I+R` | parse_fail | unrecognised fact(s): ['bell ringing', 'relay closed', 'alarm armed', 'not (gauge high and valve open)'] |
| `AH-E5-76dd7b9f6b-ENT-ENT_T` | parse_fail | unrecognised fact(s): ['motor running', 'heater on', 'relay closed'] |
| `AH-E5-76dd7b9f6b-ENT-ENT_N` | parse_fail | unrecognised fact(s): ['motor running', 'heater on', 'relay closed'] |
| `AH-E5-76dd7b9f6b-ENT-ENT_I` | parse_fail | unrecognised fact(s): ['motor not running', 'heater on', 'relay not closed', 'gate closed', 'dial turned'] |
| `AH-E5-76dd7b9f6b-ENT-ENT_I+R` | parse_fail | unrecognised fact(s): ['motor not running', 'relay not closed', 'heater on', 'dial turned', 'gate closed'] |
| `AH-E5-be7b466562-ENT-ENT_T` | parse_fail | unrecognised fact(s): ['pump running'] |

