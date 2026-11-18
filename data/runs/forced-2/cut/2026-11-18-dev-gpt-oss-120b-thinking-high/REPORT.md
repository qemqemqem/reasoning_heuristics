# Run forced-2/cut/2026-11-18-dev-gpt-oss-120b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-120b`; returned `openai/gpt-oss-120b`.
- **Provider:** routing `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DeepInfra': 284}.
- **Condition:** `thinking-high-forced`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 284 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_room': 0}.
- **Status:** complete; 284 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.3696 API-reported over 2 invocation(s) (last cap $0.10; dry-run estimate $0.36, worst case $0.56).
- **Code:** git `c30616bc9159d4af81b231aef1079c2107f48800`; scorer `scorer-1.5.2` at `c30616bc9159d4af81b231aef1079c2107f48800`.

## Forced final answers

The responses of `2026-11-18-dev-gpt-oss-120b-thinking-high` that stopped at the cap with a reasoning trace, replayed with the thinking closed (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096, logit_bias `{'200005': -100, '200006': -100, '200007': -100}`): 284 selected; 0 skipped (no trace); 0 skipped (no room). Of 284 forced responses, 284 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below). 270 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; the source run `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`.
- **Raw-prompt check:** the same text gave 93 prompt tokens as a raw prompt and 147 as a chat user message, so the provider passed the raw prompt through.

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | Correct of ok |
|---|---|---|---|---|---|---|
| A/H | E1 | 15 | 14 | 1 | 0 | 7/14 (50%) |
| A/H | E2 | 47 | 40 | 7 | 0 | 23/40 (58%) |
| A/H | E5 | 17 | 17 | 0 | 0 | 6/17 (35%) |
| C | E1 | 5 | 4 | 1 | 0 | 3/4 (75%) |
| C | E2 | 44 | 42 | 1 | 1 | 16/42 (38%) |
| C | E3 | 143 | 140 | 0 | 3 | 23/140 (16%) |
| C | E5 | 13 | 13 | 0 | 0 | 3/13 (23%) |
| **All** | | **284** | **270** | **10** | **4** | **81/270 (30%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | SAT | 15 | 25 | 74 | 0 | 0 | 35,110 | 0 (0%) | 0 (0%) | 0.00131 |
| A/H | E2 | COL | 9 | 164 | 155 | 0 | 0 | 33,230 | 0 (0%) | 0 (0%) | 0.00125 |
| A/H | E2 | SAT | 38 | 29 | 50 | 0 | 0 | 35,084 | 0 (0%) | 0 (0%) | 0.00130 |
| A/H | E5 | COL | 1 | 288 | 288 | 0 | 0 | 33,138 | 0 (0%) | 0 (0%) | 0.00127 |
| A/H | E5 | KNAP | 3 | 25 | 267 | 0 | 0 | 33,021 | 0 (0%) | 0 (0%) | 0.00127 |
| A/H | E5 | SAT | 13 | 37 | 107 | 0 | 0 | 34,006 | 0 (0%) | 0 (0%) | 0.00127 |
| C | E1 | COL | 2 | 114 | 114 | 0 | 0 | 33,243 | 0 (0%) | 0 (0%) | 0.00125 |
| C | E1 | SAT | 3 | 95 | 95 | 0 | 0 | 33,895 | 0 (0%) | 0 (0%) | 0.00127 |
| C | E2 | COL | 1 | 136 | 136 | 0 | 0 | 33,237 | 0 (0%) | 0 (0%) | 0.00125 |
| C | E2 | KNAP | 14 | 13 | 64 | 0 | 0 | 32,978 | 0 (0%) | 0 (0%) | 0.00123 |
| C | E2 | SAT | 29 | 93 | 87 | 0 | 0 | 33,974 | 0 (0%) | 0 (0%) | 0.00127 |
| C | E3 | COL-U | 143 | 404 | 374 | 0 | 0 | 34,189 | 0 (0%) | 0 (0%) | 0.00132 |
| C | E5 | COL | 2 | 146 | 146 | 0 | 0 | 33,304 | 0 (0%) | 0 (0%) | 0.00126 |
| C | E5 | SAT | 11 | 116 | 123 | 0 | 0 | 34,168 | 0 (0%) | 0 (0%) | 0.00128 |
| **All** | | | **284** | **250** | **233** | **0** | **0** | | **0** | **0** | **0.00130** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 18, max 752; 32 responses (11%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `witness_partial` | 10 |
| `no_answer_marker` | 10 |
| `witness_malformed` | 6 |
| `order_differs_from_requested` | 5 |
| `text_after_answer` | 2 |
| `extra_text_in_block` | 1 |
| `latex_unwrapped` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E1-f822e2bd74-SAT-null-SAT_null_x-prime` | parse_fail | no answer block |
| `AH-E2-19256cba91-SAT-SAT-SAT_base_g=SAT` | parse_fail | no answer block |
| `AH-E2-1c8b9b665a-SAT-UNSAT-SAT_U_g=UNSAT` | parse_fail | no answer block |
| `AH-E2-24d476e87e-SAT-SAT-SAT_K_g=SAT` | parse_fail | no answer block |
| `AH-E2-30e355f86c-SAT-UNSAT-SAT_K_g=UNSAT` | parse_fail | no answer block |
| `AH-E2-30e355f86c-SAT-UNSAT-SAT_J_g=UNSAT` | parse_fail | no answer block |
| `AH-E2-643ef3947c-SAT-UNSAT-SAT_base_g=UNSAT` | parse_fail | no answer block |
| `AH-E2-a616e788ae-SAT-UNSAT-SAT_base_g=UNSAT` | parse_fail | no answer block |
| `C-E1-cbf51c7982-SAT_c5-ANS-FREE` | parse_fail | no `variable: value` pairs: 'A=F,\u202fB=F,\u202fC=F,\u202fD=T,\u202fE=F,\u202fF=T,\u202fG=F,\u202fH=T,\u202fI=F,\u202fJ=F,\u202fK=T,\u202fL |
| `C-E2-fcc6ef350c-SAT_GREEDY-vs-POLARITY_D(POLARITY_GREEDY)` | partial | missing 9 variable(s): x91, x73, x90, x81, x92, x67, x58, x54, x52 |
| `C-E2-fcf800eb48-SAT_GREEDY-vs-UC_PLACEBO` | parse_fail | no `variable: value` pairs: 'a=T, b=T, c=T, d=F, e=T, f=T, g=T, h=T, i=F, j=T, k=T, l=F, m=T, n=T, o=T, p=F, q=F, r=F, s=F, t=F' |
| `C-E3-d8b624d603-d=2_BASE_U-LIST` | partial | missing 6 vertex(s): v60, v70, v99, v64, v33, v89 |
| `C-E3-9a0cd44b4d-d=3_BASE_U-REV` | partial | missing 1 vertex(s): v34 |
| `C-E3-5403d40fe4-d=3_BASE_U-REV` | partial | missing 1 vertex(s): v50 |

