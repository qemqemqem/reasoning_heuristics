# Run forced-2/all-k8192/2026-11-18-dev-gpt-oss-20b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-20b`; returned `openai/gpt-oss-20b`.
- **Provider:** routing `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DeepInfra': 83}.
- **Condition:** `thinking-high-forced-k8192`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 83 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0192 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.02, worst case $0.07).
- **Code:** git `95999b544d9e2d01e836b4ec922c091cdbb76b48`; scorer `scorer-1.5.2` at `95999b544d9e2d01e836b4ec922c091cdbb76b48`.

## Forced final answers

The responses of `2026-11-18-dev-gpt-oss-20b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 8192 tokens by the model's tokenizer (`o200k_harmony`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096, logit_bias `{'200005': -100, '200006': -100, '200007': -100}`): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 83 forced responses, 83 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below). 81 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; the source run `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`.
- **Budget:** 32 of the selected traces were within budget and not sent: their natural answers stand. 83 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 93 prompt tokens as a raw prompt and 147 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 13 of the 38 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | Correct of ok |
|---|---|---|---|---|---|---|
| A/H | E1 | 10 | 10 | 0 | 0 | 2/10 (20%) |
| A/H | E2 | 10 | 10 | 0 | 0 | 3/10 (30%) |
| A/H | E5 | 16 | 15 | 0 | 1 | 8/15 (53%) |
| C | E1 | 10 | 10 | 0 | 0 | 4/10 (40%) |
| C | E2 | 15 | 14 | 1 | 0 | 3/14 (21%) |
| C | E3 | 5 | 5 | 0 | 0 | 1/5 (20%) |
| C | E5 | 17 | 17 | 0 | 0 | 5/17 (29%) |
| **All** | | **83** | **81** | **1** | **1** | **26/81 (32%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 5 | 11 | 60 | 0 | 0 | 8,587 | 0 (0%) | 0 (0%) | 0.00020 |
| A/H | E1 | SAT | 5 | 13 | 31 | 0 | 0 | 10,375 | 0 (0%) | 0 (0%) | 0.00022 |
| A/H | E2 | COL | 5 | 11 | 11 | 0 | 0 | 8,650 | 0 (0%) | 0 (0%) | 0.00019 |
| A/H | E2 | SAT | 5 | 13 | 15 | 0 | 0 | 10,460 | 0 (0%) | 0 (0%) | 0.00022 |
| A/H | E5 | COL | 3 | 73 | 60 | 0 | 0 | 8,509 | 0 (0%) | 0 (0%) | 0.00020 |
| A/H | E5 | ENT | 3 | 33 | 26 | 0 | 0 | 8,438 | 0 (0%) | 0 (0%) | 0.00023 |
| A/H | E5 | KNAP | 5 | 23 | 23 | 0 | 0 | 8,444 | 0 (0%) | 0 (0%) | 0.00019 |
| A/H | E5 | SAT | 5 | 17 | 16 | 0 | 0 | 9,310 | 0 (0%) | 0 (0%) | 0.00020 |
| C | E1 | COL | 5 | 98 | 103 | 0 | 0 | 8,673 | 0 (0%) | 0 (0%) | 0.00023 |
| C | E1 | SAT | 5 | 5 | 24 | 0 | 0 | 9,188 | 0 (0%) | 0 (0%) | 0.00025 |
| C | E2 | COL | 5 | 98 | 98 | 0 | 0 | 8,669 | 0 (0%) | 0 (0%) | 0.00023 |
| C | E2 | KNAP | 5 | 12 | 12 | 0 | 0 | 8,406 | 0 (0%) | 0 (0%) | 0.00025 |
| C | E2 | SAT | 5 | 5 | 24 | 0 | 0 | 9,332 | 0 (0%) | 0 (0%) | 0.00025 |
| C | E3 | COL-I | 1 | 5 | 5 | 0 | 0 | 9,416 | 0 (0%) | 0 (0%) | 0.00027 |
| C | E3 | COL-U | 4 | 405 | 308 | 0 | 0 | 9,616 | 0 (0%) | 0 (0%) | 0.00029 |
| C | E5 | COL | 5 | 606 | 497 | 0 | 0 | 8,733 | 0 (0%) | 0 (0%) | 0.00029 |
| C | E5 | SAT | 5 | 5 | 27 | 0 | 0 | 9,600 | 0 (0%) | 0 (0%) | 0.00024 |
| C | E5 | STATE | 7 | 89 | 67 | 0 | 0 | 9,103 | 0 (0%) | 0 (0%) | 0.00024 |
| **All** | | | **83** | **17** | **80** | **0** | **0** | | **0** | **0** | **0.00023** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 24, max 711; 5 responses (6%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `no_answer_marker` | 3 |
| `fenced_answer_no_marker` | 2 |
| `text_after_answer` | 1 |
| `latex_unwrapped` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E5-7044bcf4a8-COL-COL_I` | partial | missing 1: Gil |
| `C-E2-25a935fa9d-KNAP_RATIO-vs-VALUE_PLACEBO` | parse_fail | no answer block |

