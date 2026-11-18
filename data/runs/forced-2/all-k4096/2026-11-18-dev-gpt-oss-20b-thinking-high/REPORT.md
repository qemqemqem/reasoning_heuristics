# Run forced-2/all-k4096/2026-11-18-dev-gpt-oss-20b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-20b`; returned `openai/gpt-oss-20b`.
- **Provider:** routing `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DeepInfra': 93}.
- **Condition:** `thinking-high-forced-k4096`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 93 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0163 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.01, worst case $0.07).
- **Code:** git `95999b544d9e2d01e836b4ec922c091cdbb76b48`; scorer `scorer-1.5.2` at `95999b544d9e2d01e836b4ec922c091cdbb76b48`.

## Forced final answers

The responses of `2026-11-18-dev-gpt-oss-20b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 4096 tokens by the model's tokenizer (`o200k_harmony`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096, logit_bias `{'200005': -100, '200006': -100, '200007': -100}`): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 93 forced responses, 92 answered and 1 went back to reasoning and stopped at max_tokens again (`truncated` below). 86 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; the source run `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`.
- **Budget:** 22 of the selected traces were within budget and not sent: their natural answers stand. 93 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 93 prompt tokens as a raw prompt and 147 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 16 of the 48 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | truncated | Correct of ok |
|---|---|---|---|---|---|---|
| A/H | E1 | 12 | 11 | 1 | 0 | 7/11 (64%) |
| A/H | E2 | 12 | 11 | 1 | 0 | 4/11 (36%) |
| A/H | E5 | 20 | 19 | 1 | 0 | 10/19 (53%) |
| C | E1 | 10 | 10 | 0 | 0 | 0/10 (0%) |
| C | E2 | 15 | 13 | 1 | 1 | 1/13 (8%) |
| C | E3 | 5 | 3 | 2 | 0 | 0/3 (0%) |
| C | E5 | 19 | 19 | 0 | 0 | 5/19 (26%) |
| **All** | | **93** | **86** | **6** | **1** | **27/86 (31%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 5 | 11 | 61 | 0 | 0 | 4,491 | 0 (0%) | 0 (0%) | 0.00014 |
| A/H | E1 | ENT | 2 | 7 | 7 | 0 | 0 | 4,369 | 0 (0%) | 0 (0%) | 0.00013 |
| A/H | E1 | SAT | 5 | 13 | 66 | 0 | 0 | 6,279 | 0 (0%) | 0 (0%) | 0.00019 |
| A/H | E2 | COL | 5 | 135 | 110 | 0 | 0 | 4,554 | 0 (0%) | 0 (0%) | 0.00015 |
| A/H | E2 | ENT | 2 | 7 | 7 | 0 | 0 | 4,359 | 0 (0%) | 0 (0%) | 0.00013 |
| A/H | E2 | SAT | 5 | 13 | 20 | 0 | 0 | 6,364 | 0 (0%) | 0 (0%) | 0.00019 |
| A/H | E5 | COL | 5 | 72 | 73 | 0 | 0 | 4,399 | 0 (0%) | 0 (0%) | 0.00014 |
| A/H | E5 | ENT | 5 | 26 | 24 | 0 | 0 | 4,340 | 0 (0%) | 0 (0%) | 0.00013 |
| A/H | E5 | KNAP | 5 | 62 | 119 | 0 | 0 | 4,348 | 0 (0%) | 0 (0%) | 0.00015 |
| A/H | E5 | SAT | 5 | 21 | 238 | 0 | 0 | 5,214 | 0 (0%) | 0 (0%) | 0.00019 |
| C | E1 | COL | 5 | 105 | 131 | 0 | 0 | 4,577 | 0 (0%) | 0 (0%) | 0.00015 |
| C | E1 | SAT | 5 | 101 | 740 | 0 | 0 | 5,092 | 0 (0%) | 0 (0%) | 0.00025 |
| C | E2 | COL | 5 | 179 | 194 | 0 | 0 | 4,573 | 0 (0%) | 0 (0%) | 0.00016 |
| C | E2 | KNAP | 5 | 67 | 857 | 0 | 0 | 4,310 | 1 (20%) | 0 (0%) | 0.00025 |
| C | E2 | SAT | 5 | 88 | 91 | 0 | 0 | 5,236 | 0 (0%) | 0 (0%) | 0.00017 |
| C | E3 | COL-I | 1 | 12 | 12 | 0 | 0 | 5,320 | 0 (0%) | 0 (0%) | 0.00014 |
| C | E3 | COL-U | 4 | 215 | 221 | 0 | 0 | 5,520 | 0 (0%) | 0 (0%) | 0.00019 |
| C | E5 | COL | 5 | 152 | 308 | 0 | 0 | 4,637 | 0 (0%) | 0 (0%) | 0.00018 |
| C | E5 | SAT | 5 | 142 | 504 | 0 | 0 | 5,504 | 0 (0%) | 0 (0%) | 0.00023 |
| C | E5 | STATE | 9 | 90 | 140 | 0 | 0 | 4,998 | 0 (0%) | 0 (0%) | 0.00016 |
| **All** | | | **93** | **62** | **214** | **0** | **0** | | **1** | **0** | **0.00018** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 173, max 4,828; 22 responses (24%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `extra_text_in_block` | 9 |
| `latex_unwrapped` | 7 |
| `no_answer_marker` | 4 |
| `order_differs_from_requested` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E1-57311b5fcd-SAT-critical-SAT_critical_x` | parse_fail | no answer block |
| `AH-E2-19256cba91-SAT-SAT-SAT_U_g=SAT` | parse_fail | no answer block |
| `AH-E5-c0cbfc3e6e-ENT-ENT_N` | parse_fail | unrecognised fact(s): ['lamps is not lit'] |
| `C-E2-25a935fa9d-KNAP_RATIO-vs-VALUE_D(VALUE_RATIO)` | parse_fail | no answer block |
| `C-E3-df0043fbca-d=1_BASE_I` | parse_fail | no answer block |
| `C-E3-df0043fbca-d=1_CRITICAL_U-REV` | parse_fail | no answer block |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E2 | KNAP/RATIO-vs-VALUE/BASE | 1 |

