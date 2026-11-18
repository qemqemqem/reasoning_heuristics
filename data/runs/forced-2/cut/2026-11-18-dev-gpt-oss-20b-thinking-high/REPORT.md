# Run forced-2/cut/2026-11-18-dev-gpt-oss-20b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-20b`; returned `openai/gpt-oss-20b`.
- **Provider:** routing `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DeepInfra': 462}.
- **Condition:** `thinking-high-forced`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 462 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_room': 0}.
- **Status:** complete; 462 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.4792 API-reported over 1 invocation(s) (last cap $1.00; dry-run estimate $0.47, worst case $0.73).
- **Code:** git `75fb55fb5ebeafb80486f7fb27a1954c03404897`; scorer `scorer-1.5.2` at `75fb55fb5ebeafb80486f7fb27a1954c03404897`.

## Forced final answers

The responses of `2026-11-18-dev-gpt-oss-20b-thinking-high` that stopped at the cap with a reasoning trace, replayed with the thinking closed (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096, logit_bias `{'200005': -100, '200006': -100, '200007': -100}`): 462 selected; 0 skipped (no trace); 0 skipped (no room). Of 462 forced responses, 461 answered and 1 went back to reasoning and stopped at max_tokens again (`truncated` below). 439 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; the source run `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`.
- **Raw-prompt check:** the same text gave 93 prompt tokens as a raw prompt and 147 as a chat user message, so the provider passed the raw prompt through.

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | declared_impossible | partial | truncated | Correct of ok |
|---|---|---|---|---|---|---|---|---|
| A/H | E1 | 27 | 26 | 1 | 0 | 0 | 0 | 17/26 (65%) |
| A/H | E2 | 68 | 66 | 2 | 0 | 0 | 0 | 39/66 (59%) |
| A/H | E5 | 30 | 28 | 1 | 0 | 1 | 0 | 14/28 (50%) |
| C | E1 | 14 | 14 | 0 | 0 | 0 | 0 | 6/14 (43%) |
| C | E2 | 129 | 121 | 7 | 0 | 0 | 1 | 62/121 (51%) |
| C | E3 | 174 | 165 | 3 | 1 | 5 | 0 | 10/165 (6%) |
| C | E5 | 20 | 19 | 1 | 0 | 0 | 0 | 4/19 (21%) |
| **All** | | **462** | **439** | **15** | **1** | **6** | **1** | **152/439 (35%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 8 | 11 | 40 | 0 | 0 | 33,162 | 0 (0%) | 0 (0%) | 0.00100 |
| A/H | E1 | SAT | 19 | 19 | 36 | 0 | 0 | 34,936 | 0 (0%) | 0 (0%) | 0.00105 |
| A/H | E2 | COL | 29 | 11 | 72 | 0 | 0 | 33,257 | 0 (0%) | 0 (0%) | 0.00101 |
| A/H | E2 | SAT | 39 | 21 | 32 | 0 | 0 | 35,078 | 0 (0%) | 0 (0%) | 0.00105 |
| A/H | E5 | COL | 1 | 72 | 72 | 0 | 0 | 33,054 | 0 (0%) | 0 (0%) | 0.00100 |
| A/H | E5 | KNAP | 11 | 161 | 193 | 0 | 0 | 33,016 | 0 (0%) | 0 (0%) | 0.00102 |
| A/H | E5 | SAT | 18 | 16 | 34 | 0 | 0 | 34,002 | 0 (0%) | 0 (0%) | 0.00102 |
| C | E1 | COL | 8 | 98 | 274 | 0 | 0 | 33,240 | 0 (0%) | 0 (0%) | 0.00103 |
| C | E1 | SAT | 6 | 90 | 93 | 0 | 0 | 33,869 | 0 (0%) | 0 (0%) | 0.00103 |
| C | E2 | COL | 18 | 98 | 355 | 0 | 0 | 33,250 | 1 (6%) | 0 (0%) | 0.00105 |
| C | E2 | KNAP | 69 | 10 | 39 | 0 | 0 | 32,975 | 0 (0%) | 0 (0%) | 0.00099 |
| C | E2 | SAT | 42 | 90 | 140 | 0 | 0 | 33,983 | 0 (0%) | 0 (0%) | 0.00104 |
| C | E3 | COL-U | 174 | 404 | 277 | 0 | 0 | 34,188 | 0 (0%) | 0 (0%) | 0.00106 |
| C | E5 | COL | 7 | 147 | 197 | 0 | 0 | 33,304 | 0 (0%) | 0 (0%) | 0.00103 |
| C | E5 | SAT | 13 | 121 | 120 | 0 | 0 | 34,170 | 0 (0%) | 0 (0%) | 0.00104 |
| **All** | | | **462** | **28** | **165** | **0** | **0** | | **1** | **0** | **0.00104** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 39, max 3,887; 64 responses (14%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `no_answer_marker` | 56 |
| `extra_text_in_block` | 36 |
| `order_differs_from_requested` | 31 |
| `witness_malformed` | 13 |
| `fenced_answer_no_marker` | 10 |
| `latex_unwrapped` | 9 |
| `witness_partial` | 3 |
| `repeated_vertex` | 2 |
| `impossible_as_phrase` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E1-562afb2107-SAT-null-SAT_null_x-prime` | parse_fail | no answer block |
| `AH-E2-1c8b9b665a-SAT-UNSAT-SAT_base_g=UNSAT` | parse_fail | no answer block |
| `AH-E2-4caac01863-COL-possible-COL_K_g=possible` | parse_fail | no answer block |
| `AH-E5-c329f0fa25-SAT-SAT_I+R` | parse_fail | no answer block |
| `AH-E5-1c8b9b665a-SAT-SAT_I+R` | partial | 10 digits for 12 variables |
| `C-E2-5b9e32dcea-SAT_GREEDY-vs-POLARITY_G-ONLY` | parse_fail | no `variable: value` pairs: 'a=T,b=T,c=F,d=T,e=T,f=F,g=T,h=F,i=T,j=F,k=F,l=F,m=T,n=F,o=T,p=T,q=F,r=F,s=F,t=F' |
| `C-E2-fefe1fab3f-SAT_GREEDY-vs-POLARITY_BASE` | parse_fail | no answer block |
| `C-E2-fcc6ef350c-SAT_GREEDY-vs-POLARITY_D(POLARITY_GREEDY)` | parse_fail | no answer block |
| `C-E2-fcc6ef350c-SAT_GREEDY-vs-POLARITY_G-ONLY` | parse_fail | no `variable: value` pairs: 'SATISFIABLE with the assignment above.' |
| `C-E2-41f5f64b4a-KNAP_RATIO-vs-DIFF_D(RATIO_DIFF)` | parse_fail | unknown item(s): M, N, O, P, Q, R, S, T, U, V |
| `C-E2-1ea790987a-KNAP_RATIO-vs-VALUE_D(VALUE_RATIO)` | parse_fail | no answer block |
| `C-E2-1ea790987a-KNAP_RATIO-vs-VALUE_G-ONLY` | parse_fail | unknown item(s): p |
| `C-E3-322e4cdfac-d=1_PLACEBO_U-REV` | parse_fail | no answer block |
| `C-E3-c88de4bdf9-d=1_PLACEBO_U-LIST` | parse_fail | no `vertex: value` pairs: 'The graph is 3‑colourable.' |
| `C-E3-2c67926033-d=2_PLACEBO_U-REV` | partial | missing 24 vertex(s): v71, v91, v42, v15, v47, v28, v94, v23, v73, v48 |
| `C-E3-5403d40fe4-d=3_CRITICAL_U-REV` | partial | missing 1 vertex(s): v65 |
| `C-E3-b32de5c997-d=4_CRITICAL_U-REV` | partial | missing 8 vertex(s): v62, v44, v39, v74, v69, v63, v48, v43 |
| `C-E3-f55f670046-d=4_PLACEBO_U-REV` | parse_fail | unknown vertex(s): v32, v62 |
| `C-E3-a93af8e839-d=4_BASE_U-REV` | partial | missing 1 vertex(s): v77 |
| `C-E3-501a4bdac5-d=6_CRITICAL_U-REV` | declared_impossible | no answer block; Cannot determine |
| `C-E3-d94132c512-d=8_BASE_U-REV` | partial | missing 1 vertex(s): v46 |
| `C-E5-2c2dfe9dad-COL_CONTROL_vA_eA` | parse_fail | no answer block |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E2 | COL/FF-vs-DSATUR/G-ONLY | 1 |

