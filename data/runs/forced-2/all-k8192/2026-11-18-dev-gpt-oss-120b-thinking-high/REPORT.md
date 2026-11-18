# Run forced-2/all-k8192/2026-11-18-dev-gpt-oss-120b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-120b`; returned `openai/gpt-oss-120b`.
- **Provider:** routing `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DeepInfra': 76}.
- **Condition:** `thinking-high-forced-k8192`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 76 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0272 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.03, worst case $0.08).
- **Code:** git `2c27e2b27f86f29699b08001a77d758bc9e977f4`; scorer `scorer-1.5.2` at `2c27e2b27f86f29699b08001a77d758bc9e977f4`.

## Forced final answers

The responses of `2026-11-18-dev-gpt-oss-120b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 8192 tokens by the model's tokenizer (`o200k_harmony`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096, logit_bias `{'200005': -100, '200006': -100, '200007': -100}`): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 76 forced responses, 76 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below). 75 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; the source run `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`.
- **Budget:** 39 of the selected traces were within budget and not sent: their natural answers stand. 76 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 93 prompt tokens as a raw prompt and 147 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 13 of the 50 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | partial | Correct of ok |
|---|---|---|---|---|---|
| A/H | E1 | 10 | 10 | 0 | 7/10 (70%) |
| A/H | E2 | 10 | 10 | 0 | 5/10 (50%) |
| A/H | E5 | 13 | 13 | 0 | 6/13 (46%) |
| C | E1 | 10 | 10 | 0 | 2/10 (20%) |
| C | E2 | 14 | 14 | 0 | 5/14 (36%) |
| C | E3 | 5 | 4 | 1 | 1/4 (25%) |
| C | E5 | 14 | 14 | 0 | 2/14 (14%) |
| **All** | | **76** | **75** | **1** | **28/75 (37%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 5 | 133 | 141 | 0 | 0 | 8,587 | 0 (0%) | 0 (0%) | 0.00034 |
| A/H | E1 | SAT | 5 | 23 | 23 | 0 | 0 | 10,375 | 0 (0%) | 0 (0%) | 0.00039 |
| A/H | E2 | COL | 5 | 186 | 197 | 0 | 0 | 8,650 | 0 (0%) | 0 (0%) | 0.00035 |
| A/H | E2 | SAT | 5 | 25 | 84 | 0 | 0 | 10,460 | 0 (0%) | 0 (0%) | 0.00040 |
| A/H | E5 | COL | 3 | 116 | 482 | 0 | 0 | 8,509 | 0 (0%) | 0 (0%) | 0.00039 |
| A/H | E5 | ENT | 1 | 36 | 36 | 0 | 0 | 8,446 | 0 (0%) | 0 (0%) | 0.00032 |
| A/H | E5 | KNAP | 4 | 190 | 288 | 0 | 0 | 8,442 | 0 (0%) | 0 (0%) | 0.00036 |
| A/H | E5 | SAT | 5 | 21 | 63 | 0 | 0 | 9,310 | 0 (0%) | 0 (0%) | 0.00035 |
| C | E1 | COL | 5 | 100 | 100 | 0 | 0 | 8,673 | 0 (0%) | 0 (0%) | 0.00033 |
| C | E1 | SAT | 5 | 99 | 107 | 0 | 0 | 9,188 | 0 (0%) | 0 (0%) | 0.00035 |
| C | E2 | COL | 4 | 100 | 100 | 0 | 0 | 8,668 | 0 (0%) | 0 (0%) | 0.00034 |
| C | E2 | KNAP | 5 | 15 | 15 | 0 | 0 | 8,406 | 0 (0%) | 0 (0%) | 0.00031 |
| C | E2 | SAT | 5 | 100 | 98 | 0 | 0 | 9,332 | 0 (0%) | 0 (0%) | 0.00036 |
| C | E3 | COL-I | 1 | 2 | 2 | 0 | 0 | 9,416 | 0 (0%) | 0 (0%) | 0.00033 |
| C | E3 | COL-U | 4 | 406 | 404 | 0 | 0 | 9,616 | 0 (0%) | 0 (0%) | 0.00042 |
| C | E5 | COL | 5 | 148 | 92 | 0 | 0 | 8,733 | 0 (0%) | 0 (0%) | 0.00034 |
| C | E5 | SAT | 5 | 109 | 114 | 0 | 0 | 9,600 | 0 (0%) | 0 (0%) | 0.00037 |
| C | E5 | STATE | 4 | 90 | 70 | 0 | 0 | 9,375 | 0 (0%) | 0 (0%) | 0.00035 |
| **All** | | | **76** | **100** | **133** | **0** | **0** | | **0** | **0** | **0.00036** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 37, max 1,194; 10 responses (13%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `witness_partial` | 4 |
| `text_after_answer` | 1 |
| `witness_malformed` | 1 |
| `no_answer_marker` | 1 |
| `order_differs_from_requested` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E3-df0043fbca-d=1_CRITICAL_U-REV` | partial | missing 1 vertex(s): v43 |

