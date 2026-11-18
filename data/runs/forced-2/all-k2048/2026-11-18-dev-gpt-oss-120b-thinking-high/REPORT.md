# Run forced-2/all-k2048/2026-11-18-dev-gpt-oss-120b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-120b`; returned `openai/gpt-oss-120b`.
- **Provider:** routing `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DeepInfra': 98}.
- **Condition:** `thinking-high-forced-k2048`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 98 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0126 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.01, worst case $0.08).
- **Code:** git `2c27e2b27f86f29699b08001a77d758bc9e977f4`; scorer `scorer-1.5.2` at `2c27e2b27f86f29699b08001a77d758bc9e977f4`.

## Forced final answers

The responses of `2026-11-18-dev-gpt-oss-120b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 2048 tokens by the model's tokenizer (`o200k_harmony`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096, logit_bias `{'200005': -100, '200006': -100, '200007': -100}`): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 98 forced responses, 98 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below). 97 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; the source run `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`.
- **Budget:** 17 of the selected traces were within budget and not sent: their natural answers stand. 98 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 93 prompt tokens as a raw prompt and 147 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 20 of the 72 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | partial | Correct of ok |
|---|---|---|---|---|---|
| A/H | E1 | 15 | 15 | 0 | 10/15 (67%) |
| A/H | E2 | 14 | 14 | 0 | 12/14 (86%) |
| A/H | E5 | 20 | 20 | 0 | 6/20 (30%) |
| C | E1 | 10 | 10 | 0 | 0/10 (0%) |
| C | E2 | 15 | 15 | 0 | 3/15 (20%) |
| C | E3 | 5 | 5 | 0 | 0/5 (0%) |
| C | E5 | 19 | 18 | 1 | 3/18 (17%) |
| **All** | | **98** | **97** | **1** | **34/97 (35%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 5 | 160 | 168 | 0 | 0 | 2,443 | 0 (0%) | 0 (0%) | 0.00012 |
| A/H | E1 | ENT | 5 | 397 | 343 | 0 | 0 | 2,312 | 0 (0%) | 0 (0%) | 0.00014 |
| A/H | E1 | SAT | 5 | 23 | 89 | 0 | 0 | 4,231 | 0 (0%) | 0 (0%) | 0.00017 |
| A/H | E2 | COL | 5 | 227 | 410 | 0 | 0 | 2,506 | 0 (0%) | 0 (0%) | 0.00016 |
| A/H | E2 | ENT | 4 | 88 | 116 | 0 | 0 | 2,310 | 0 (0%) | 0 (0%) | 0.00010 |
| A/H | E2 | SAT | 5 | 233 | 165 | 0 | 0 | 4,316 | 0 (0%) | 0 (0%) | 0.00019 |
| A/H | E5 | COL | 5 | 123 | 187 | 0 | 0 | 2,351 | 0 (0%) | 0 (0%) | 0.00012 |
| A/H | E5 | ENT | 5 | 40 | 47 | 0 | 0 | 2,292 | 0 (0%) | 0 (0%) | 0.00009 |
| A/H | E5 | KNAP | 5 | 76 | 189 | 0 | 0 | 2,300 | 0 (0%) | 0 (0%) | 0.00011 |
| A/H | E5 | SAT | 5 | 21 | 58 | 0 | 0 | 3,166 | 0 (0%) | 0 (0%) | 0.00012 |
| C | E1 | COL | 5 | 100 | 139 | 0 | 0 | 2,529 | 0 (0%) | 0 (0%) | 0.00011 |
| C | E1 | SAT | 5 | 103 | 112 | 0 | 0 | 3,044 | 0 (0%) | 0 (0%) | 0.00013 |
| C | E2 | COL | 5 | 100 | 100 | 0 | 0 | 2,525 | 0 (0%) | 0 (0%) | 0.00011 |
| C | E2 | KNAP | 5 | 15 | 15 | 0 | 0 | 2,262 | 0 (0%) | 0 (0%) | 0.00008 |
| C | E2 | SAT | 5 | 100 | 101 | 0 | 0 | 3,188 | 0 (0%) | 0 (0%) | 0.00013 |
| C | E3 | COL-I | 1 | 5 | 5 | 0 | 0 | 3,272 | 0 (0%) | 0 (0%) | 0.00010 |
| C | E3 | COL-U | 4 | 406 | 406 | 0 | 0 | 3,472 | 0 (0%) | 0 (0%) | 0.00019 |
| C | E5 | COL | 5 | 148 | 148 | 0 | 0 | 2,589 | 0 (0%) | 0 (0%) | 0.00012 |
| C | E5 | SAT | 5 | 123 | 120 | 0 | 0 | 3,456 | 0 (0%) | 0 (0%) | 0.00015 |
| C | E5 | STATE | 9 | 100 | 87 | 0 | 0 | 2,950 | 0 (0%) | 0 (0%) | 0.00012 |
| **All** | | | **98** | **102** | **151** | **0** | **0** | | **0** | **0** | **0.00013** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 56, max 667; 28 responses (29%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `witness_malformed` | 4 |
| `text_after_answer` | 4 |
| `order_differs_from_requested` | 3 |
| `missing_only_fixed` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E5-4f7ee728ed-STATE_SAT_s3` | partial | missing 6 variable(s): x16, x17, x42, x10, x36, x20 |

