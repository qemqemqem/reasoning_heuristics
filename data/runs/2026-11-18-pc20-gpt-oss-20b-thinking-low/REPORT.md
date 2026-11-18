# Run 2026-11-18-pc20-gpt-oss-20b-thinking-low

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-20b`; returned `openai/gpt-oss-20b`.
- **Provider:** routing `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DekaLLM': 1380}.
- **Condition:** `thinking-low`; max_tokens 32768; reasoning `{'effort': 'low'}`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 1380 (data/items/pc20/C_E2_dev_s1.jsonl.gz, data/items/pc20/AH_E5_dev_s1.jsonl.gz, data/items/pc20/C_E1_dev_s1.jsonl.gz); skipped {'excluded_eval': 0, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 1380 responses, 0 failed calls, 160 from cache.
- **Spend:** $0.2330 API-reported over 1 invocation(s) (last cap $0.60; dry-run estimate $1.53, worst case $6.36).
- **Code:** git `9677076ddcc42f1649a601b502371ccf394584c5`; scorer `scorer-1.5.1` at `34f2a739e3b2b71721f4ec75aa792469f382b395`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | Correct of ok |
|---|---|---|---|---|---|---|
| A/H | E5 | 340 | 324 | 15 | 1 | 142/324 (44%) |
| C | E1 | 240 | 228 | 10 | 2 | 73/228 (32%) |
| C | E2 | 800 | 799 | 1 | 0 | 217/799 (27%) |
| **All** | | **1380** | **1351** | **26** | **3** | **432/1351 (32%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E5 | COL | 80 | 960 | 991 | 890 | 943 | 319 | 0 (0%) | 80 (100%) | 0.00015 |
| A/H | E5 | ENT | 80 | 648 | 664 | 626 | 642 | 250 | 0 (0%) | 80 (100%) | 0.00010 |
| A/H | E5 | KNAP | 80 | 1,178 | 1,311 | 1,157 | 1,287 | 259 | 0 (0%) | 80 (100%) | 0.00019 |
| A/H | E5 | SAT | 100 | 2,164 | 2,279 | 2,140 | 2,257 | 1,260 | 0 (0%) | 100 (100%) | 0.00036 |
| C | E1 | COL | 120 | 1,358 | 1,422 | 1,254 | 1,320 | 477 | 0 (0%) | 120 (100%) | 0.00021 |
| C | E1 | SAT | 120 | 486 | 1,136 | 386 | 1,033 | 1,066 | 0 (0%) | 120 (100%) | 0.00019 |
| C | E2 | COL | 300 | 1,110 | 1,200 | 1,007 | 1,098 | 484 | 0 (0%) | 300 (100%) | 0.00018 |
| C | E2 | KNAP | 300 | 844 | 906 | 828 | 890 | 216 | 0 (0%) | 300 (100%) | 0.00013 |
| C | E2 | SAT | 200 | 1,590 | 1,651 | 1,492 | 1,592 | 1,212 | 0 (0%) | 200 (100%) | 0.00027 |
| **All** | | | **1380** | **1,012** | **1,257** | **968** | **1,197** | | **0** | **1380** | **0.00019** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 0, max 140; 1 responses (0%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `order_differs_from_requested` | 4 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E2-d556fa2cc7-COL_FF-vs-DSATUR_G-ONLY` | parse_fail | no answer block |
| `AH-E5-4d7c112e87-SAT-SAT_N` | parse_fail | 17 digits for 16 variables |
| `AH-E5-ded1e3e5dc-SAT-SAT_N` | parse_fail | 17 digits for 16 variables |
| `AH-E5-ded1e3e5dc-SAT-SAT_I` | parse_fail | 20 digits for 16 variables |
| `AH-E5-28b3419632-COL-COL_T` | partial | missing 1: Pia |
| `AH-E5-c2854a89d6-COL-COL_T` | parse_fail | unknown name(s): Megan |
| `AH-E5-e3a97a6906-ENT-ENT_I+R` | parse_fail | unrecognised fact(s): ['motor running', 'sensor active', 'lever not down', 'buzzer not sounding', 'pump not running'] |
| `AH-E5-fea9ce5136-ENT-ENT_N` | parse_fail | unrecognised fact(s): ['dial not turned'] |
| `AH-E5-a3c3032647-ENT-ENT_N` | parse_fail | unrecognised fact(s): ['relay NOT CLOSED', 'alarm ARMED', 'gate NOT CLOSED'] |
| `AH-E5-075fde5b6a-ENT-ENT_I` | parse_fail | unrecognised fact(s): ['G gauge is high', 'D door is not open', 'R relay is open', 'B bell is not ringing'] |
| `AH-E5-94a645090c-ENT-ENT_I+R` | parse_fail | unrecognised fact(s): ['pump running', 'door open'] |
| `AH-E5-3386a6bdc1-ENT-ENT_I+R` | parse_fail | unrecognised fact(s): ['bell ringing', 'relay closed', 'alarm armed', 'not (gauge high and valve open)'] |
| `AH-E5-76dd7b9f6b-ENT-ENT_T` | parse_fail | unrecognised fact(s): ['motor running', 'heater on', 'relay closed'] |
| `AH-E5-76dd7b9f6b-ENT-ENT_N` | parse_fail | unrecognised fact(s): ['motor running', 'heater on', 'relay closed'] |
| `AH-E5-76dd7b9f6b-ENT-ENT_I` | parse_fail | unrecognised fact(s): ['motor not running', 'heater on', 'relay not closed', 'gate closed', 'dial turned'] |
| `AH-E5-be7b466562-ENT-ENT_T` | parse_fail | unrecognised fact(s): ['pump running'] |
| `AH-E5-8c37e01b54-ENT-ENT_N` | parse_fail | no answer block |
| `C-E1-af8320d06c-COL_c6-RELIST` | parse_fail | no answer block |
| `C-E1-c2854a89d6-COL_c1-NAT` | parse_fail | no answer block |
| `C-E1-15ec0fc41c-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x10, x11, x12, x13, x14, x15, x17, x18, x2 |
| `C-E1-72ee36a5d2-SAT_c5-ANS-FREE` | partial | missing 16 variable(s): x41, x61, x99, x36, x33, x67, x75, x63, x52, x85 |
| `C-E1-cbf51c7982-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x10, x11, x12, x13, x16, x17, x18, x2, x21 |
| `C-E1-3f36aaa52d-SAT_c5-ANS-FREE` | parse_fail | no `variable: value` pairs: '1=T,2=T,3=T,4=T,5=T,6=T,7=T,8=T,9=T,10=T,11=T,12=T,13=T,14=T,15=T,16=T,17=T,18=F,19=T,20=T,21=T,22=T,23=T,24=T, |
| `C-E1-348719fa81-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x10, x11, x12, x13, x14, x15, x16, x19, x2 |
| `C-E1-a1dc3b409d-SAT_c5-ANS-FREE` | parse_fail | variable x37 given two values (True, False) |

