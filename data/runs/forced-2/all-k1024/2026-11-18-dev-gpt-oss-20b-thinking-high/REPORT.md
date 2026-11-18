# Run forced-2/all-k1024/2026-11-18-dev-gpt-oss-20b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-20b`; returned `openai/gpt-oss-20b`.
- **Provider:** routing `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DeepInfra': 108}.
- **Condition:** `thinking-high-forced-k1024`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 108 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0114 API-reported over 3 invocation(s) (last cap $0.05; dry-run estimate $0.01, worst case $0.07).
- **Code:** git `95999b544d9e2d01e836b4ec922c091cdbb76b48`; scorer `scorer-1.5.2` at `95999b544d9e2d01e836b4ec922c091cdbb76b48`.

## Forced final answers

The responses of `2026-11-18-dev-gpt-oss-20b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 1024 tokens by the model's tokenizer (`o200k_harmony`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096, logit_bias `{'200005': -100, '200006': -100, '200007': -100}`): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 108 forced responses, 104 answered and 4 went back to reasoning and stopped at max_tokens again (`truncated` below). 94 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; the source run `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`.
- **Budget:** 7 of the selected traces were within budget and not sent: their natural answers stand. 108 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 93 prompt tokens as a raw prompt and 147 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 21 of the 63 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | truncated | Correct of ok |
|---|---|---|---|---|---|---|---|
| A/H | E1 | 15 | 13 | 1 | 0 | 1 | 8/13 (62%) |
| A/H | E2 | 15 | 13 | 1 | 0 | 1 | 6/13 (46%) |
| A/H | E5 | 20 | 17 | 2 | 1 | 0 | 2/17 (12%) |
| B4/C4 | E1 | 4 | 4 | 0 | 0 | 0 | 4/4 (100%) |
| B4/C4 | E2 | 1 | 1 | 0 | 0 | 0 | 1/1 (100%) |
| C | E1 | 10 | 9 | 1 | 0 | 0 | 0/9 (0%) |
| C | E2 | 15 | 14 | 1 | 0 | 0 | 2/14 (14%) |
| C | E3 | 5 | 5 | 0 | 0 | 0 | 0/5 (0%) |
| C | E5 | 23 | 18 | 1 | 2 | 2 | 6/18 (33%) |
| **All** | | **108** | **94** | **7** | **3** | **4** | **29/94 (31%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 5 | 11 | 54 | 0 | 0 | 1,419 | 0 (0%) | 0 (0%) | 0.00004 |
| A/H | E1 | ENT | 5 | 7 | 523 | 0 | 0 | 1,288 | 0 (0%) | 0 (0%) | 0.00011 |
| A/H | E1 | SAT | 5 | 23 | 862 | 0 | 0 | 3,207 | 1 (20%) | 0 (0%) | 0.00021 |
| A/H | E2 | COL | 5 | 53 | 875 | 0 | 0 | 1,482 | 1 (20%) | 0 (0%) | 0.00017 |
| A/H | E2 | ENT | 5 | 7 | 7 | 0 | 0 | 1,286 | 0 (0%) | 0 (0%) | 0.00004 |
| A/H | E2 | SAT | 5 | 13 | 57 | 0 | 0 | 3,292 | 0 (0%) | 0 (0%) | 0.00011 |
| A/H | E5 | COL | 5 | 11 | 10 | 0 | 0 | 1,327 | 0 (0%) | 0 (0%) | 0.00004 |
| A/H | E5 | ENT | 5 | 1,013 | 1,042 | 0 | 0 | 1,268 | 0 (0%) | 0 (0%) | 0.00018 |
| A/H | E5 | KNAP | 5 | 48 | 464 | 0 | 0 | 1,276 | 0 (0%) | 0 (0%) | 0.00010 |
| A/H | E5 | SAT | 5 | 17 | 48 | 0 | 0 | 2,142 | 0 (0%) | 0 (0%) | 0.00007 |
| B4/C4 | E1 | ENT | 4 | 11 | 87 | 0 | 0 | 1,189 | 0 (0%) | 0 (0%) | 0.00005 |
| B4/C4 | E2 | ENT | 1 | 4 | 4 | 0 | 0 | 1,196 | 0 (0%) | 0 (0%) | 0.00004 |
| C | E1 | COL | 5 | 154 | 327 | 0 | 0 | 1,505 | 0 (0%) | 0 (0%) | 0.00009 |
| C | E1 | SAT | 5 | 5 | 30 | 0 | 0 | 2,020 | 0 (0%) | 0 (0%) | 0.00006 |
| C | E2 | COL | 5 | 288 | 347 | 0 | 0 | 1,501 | 0 (0%) | 0 (0%) | 0.00009 |
| C | E2 | KNAP | 5 | 48 | 81 | 0 | 0 | 1,238 | 0 (0%) | 0 (0%) | 0.00005 |
| C | E2 | SAT | 5 | 127 | 212 | 0 | 0 | 2,164 | 0 (0%) | 0 (0%) | 0.00009 |
| C | E3 | COL-I | 1 | 5 | 5 | 0 | 0 | 2,248 | 0 (0%) | 0 (0%) | 0.00005 |
| C | E3 | COL-U | 4 | 480 | 495 | 0 | 0 | 2,448 | 0 (0%) | 0 (0%) | 0.00014 |
| C | E5 | COL | 5 | 170 | 491 | 0 | 0 | 1,565 | 0 (0%) | 0 (0%) | 0.00011 |
| C | E5 | ENT | 3 | 4 | 4 | 0 | 0 | 1,153 | 0 (0%) | 0 (0%) | 0.00003 |
| C | E5 | SAT | 5 | 11 | 33 | 0 | 0 | 2,431 | 0 (0%) | 0 (0%) | 0.00008 |
| C | E5 | STATE | 10 | 118 | 1,265 | 0 | 0 | 1,890 | 2 (20%) | 0 (0%) | 0.00023 |
| **All** | | | **108** | **26** | **392** | **0** | **0** | | **4** | **0** | **0.00011** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 358, max 5,067; 40 responses (37%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `extra_text_in_block` | 9 |
| `latex_unwrapped` | 6 |
| `order_differs_from_requested` | 3 |
| `text_after_answer` | 2 |
| `fenced_answer_no_marker` | 2 |
| `missing_only_fixed` | 2 |
| `witness_partial` | 1 |
| `repeated_vertex` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E1-76e49f9803-SAT-critical-SAT_critical_x-prime` | parse_fail | no answer block |
| `AH-E2-19256cba91-SAT-SAT-SAT_U_g=SAT` | parse_fail | no answer block |
| `AH-E5-7044bcf4a8-COL-COL_I` | partial | no rooms |
| `AH-E5-c0cbfc3e6e-ENT-ENT_I+R` | parse_fail | unrecognised fact(s): ['door is closed', 'motor is stopped'] |
| `AH-E5-9e5f62b0b9-ENT-ENT_T` | parse_fail | unrecognised fact(s): ['!S'] |
| `C-E1-15ec0fc41c-SAT_c2-RELABEL` | parse_fail | no answer block |
| `C-E2-25a935fa9d-KNAP_RATIO-vs-VALUE_BASE` | parse_fail | no answer block |
| `C-E5-ae33489378-COL_STUCK_vB_eA` | partial | missing 1 vertex(s): v60 |
| `C-E5-cff1984132-SAT_DEAD-PERM` | parse_fail | no answer block |
| `C-E5-79b30b5957-STATE_SAT_s2` | partial | missing 6 variable(s): x14, x16, x11, x18, x31, x33 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E1 | SAT/critical/x-prime | 1 |
| E2 | COL/base/g=possible | 1 |
| E5 | STATE/SAT/s1 | 1 |
| E5 | STATE/SAT/s2 | 1 |

