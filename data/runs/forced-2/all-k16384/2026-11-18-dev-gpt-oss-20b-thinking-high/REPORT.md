# Run forced-2/all-k16384/2026-11-18-dev-gpt-oss-20b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-20b`; returned `openai/gpt-oss-20b`.
- **Provider:** routing `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DeepInfra': 67}.
- **Condition:** `thinking-high-forced-k16384`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 67 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0304 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.03, worst case $0.07).
- **Code:** git `95999b544d9e2d01e836b4ec922c091cdbb76b48`; scorer `scorer-1.5.2` at `95999b544d9e2d01e836b4ec922c091cdbb76b48`.

## Forced final answers

The responses of `2026-11-18-dev-gpt-oss-20b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 16384 tokens by the model's tokenizer (`o200k_harmony`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096, logit_bias `{'200005': -100, '200006': -100, '200007': -100}`): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 67 forced responses, 66 answered and 1 went back to reasoning and stopped at max_tokens again (`truncated` below). 62 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; the source run `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`.
- **Budget:** 48 of the selected traces were within budget and not sent: their natural answers stand. 67 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 93 prompt tokens as a raw prompt and 147 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 12 of the 22 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | truncated | Correct of ok |
|---|---|---|---|---|---|---|---|
| A/H | E1 | 10 | 10 | 0 | 0 | 0 | 8/10 (80%) |
| A/H | E2 | 10 | 10 | 0 | 0 | 0 | 7/10 (70%) |
| A/H | E5 | 10 | 8 | 1 | 1 | 0 | 4/8 (50%) |
| C | E1 | 9 | 9 | 0 | 0 | 0 | 6/9 (67%) |
| C | E2 | 11 | 10 | 1 | 0 | 0 | 0/10 (0%) |
| C | E3 | 4 | 3 | 0 | 1 | 0 | 0/3 (0%) |
| C | E5 | 13 | 12 | 0 | 0 | 1 | 2/12 (17%) |
| **All** | | **67** | **62** | **2** | **2** | **1** | **27/62 (44%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 5 | 11 | 72 | 0 | 0 | 16,779 | 0 (0%) | 0 (0%) | 0.00046 |
| A/H | E1 | SAT | 5 | 13 | 17 | 0 | 0 | 18,567 | 0 (0%) | 0 (0%) | 0.00047 |
| A/H | E2 | COL | 5 | 11 | 71 | 0 | 0 | 16,842 | 0 (0%) | 0 (0%) | 0.00044 |
| A/H | E2 | SAT | 5 | 23 | 20 | 0 | 0 | 18,652 | 0 (0%) | 0 (0%) | 0.00041 |
| A/H | E5 | COL | 3 | 72 | 71 | 0 | 0 | 16,701 | 0 (0%) | 0 (0%) | 0.00043 |
| A/H | E5 | KNAP | 3 | 65 | 78 | 0 | 0 | 16,626 | 0 (0%) | 0 (0%) | 0.00047 |
| A/H | E5 | SAT | 4 | 17 | 320 | 0 | 0 | 17,498 | 0 (0%) | 0 (0%) | 0.00043 |
| C | E1 | COL | 5 | 98 | 98 | 0 | 0 | 16,865 | 0 (0%) | 0 (0%) | 0.00041 |
| C | E1 | SAT | 4 | 210 | 303 | 0 | 0 | 17,378 | 0 (0%) | 0 (0%) | 0.00043 |
| C | E2 | COL | 1 | 98 | 98 | 0 | 0 | 16,861 | 0 (0%) | 0 (0%) | 0.00039 |
| C | E2 | KNAP | 5 | 80 | 56 | 0 | 0 | 16,598 | 0 (0%) | 0 (0%) | 0.00043 |
| C | E2 | SAT | 5 | 93 | 118 | 0 | 0 | 17,524 | 0 (0%) | 0 (0%) | 0.00043 |
| C | E3 | COL-U | 4 | 398 | 301 | 0 | 0 | 17,808 | 0 (0%) | 0 (0%) | 0.00047 |
| C | E5 | COL | 5 | 6 | 71 | 0 | 0 | 16,925 | 0 (0%) | 0 (0%) | 0.00044 |
| C | E5 | SAT | 5 | 5 | 47 | 0 | 0 | 17,792 | 0 (0%) | 0 (0%) | 0.00048 |
| C | E5 | STATE | 3 | 92 | 1,426 | 0 | 0 | 17,568 | 1 (33%) | 0 (0%) | 0.00073 |
| **All** | | | **67** | **72** | **170** | **0** | **0** | | **1** | **0** | **0.00045** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 70, max 1,448; 11 responses (16%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `fenced_answer_no_marker` | 3 |
| `witness_malformed` | 2 |
| `no_answer_marker` | 2 |
| `order_differs_from_requested` | 2 |
| `witness_partial` | 1 |
| `extra_text_in_block` | 1 |
| `latex_unwrapped` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E5-19256cba91-SAT-SAT_N` | partial | 11 digits for 12 variables |
| `AH-E5-7044bcf4a8-COL-COL_I` | parse_fail | unknown name(s): L |
| `C-E2-07ec51fc55-SAT_GREEDY-vs-UC_BASE` | parse_fail | no answer block |
| `C-E3-df0043fbca-d=1_CRITICAL_U-REV` | partial | missing 2 vertex(s): v43, v37 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E5 | STATE/SAT/s1 | 1 |

