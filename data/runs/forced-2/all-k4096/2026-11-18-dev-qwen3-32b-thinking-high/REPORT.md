# Run forced-2/all-k4096/2026-11-18-dev-qwen3-32b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-32b`; returned `qwen/qwen3-32b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 83}.
- **Condition:** `thinking-high-forced-k4096`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 83 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0366 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.03, worst case $0.10).
- **Code:** git `95999b544d9e2d01e836b4ec922c091cdbb76b48`; scorer `scorer-1.5.2` at `95999b544d9e2d01e836b4ec922c091cdbb76b48`.

## Forced final answers

The responses of `2026-11-18-dev-qwen3-32b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 4096 tokens by the model's tokenizer (`Qwen/Qwen3-32B/tokenizer.json`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 83 forced responses, 81 answered and 2 went back to reasoning and stopped at max_tokens again (`truncated` below). 81 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; the source run `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`.
- **Budget:** 32 of the selected traces were within budget and not sent: their natural answers stand. 83 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 63 prompt tokens as a raw prompt and 72 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 21 of the 80 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | truncated | Correct of ok |
|---|---|---|---|---|---|
| A/H | E1 | 10 | 10 | 0 | 5/10 (50%) |
| A/H | E2 | 10 | 9 | 1 | 6/9 (67%) |
| A/H | E5 | 15 | 15 | 0 | 8/15 (53%) |
| C | E1 | 10 | 10 | 0 | 2/10 (20%) |
| C | E2 | 15 | 15 | 0 | 4/15 (27%) |
| C | E3 | 5 | 5 | 0 | 2/5 (40%) |
| C | E5 | 18 | 17 | 1 | 3/17 (18%) |
| **All** | | **83** | **81** | **2** | **30/81 (37%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 5 | 108 | 113 | 0 | 0 | 4,468 | 0 (0%) | 0 (0%) | 0.00031 |
| A/H | E1 | SAT | 5 | 37 | 37 | 0 | 0 | 6,632 | 0 (0%) | 0 (0%) | 0.00043 |
| A/H | E2 | COL | 5 | 186 | 199 | 0 | 0 | 4,533 | 0 (0%) | 0 (0%) | 0.00033 |
| A/H | E2 | SAT | 5 | 37 | 844 | 0 | 0 | 6,802 | 1 (20%) | 0 (0%) | 0.00062 |
| A/H | E5 | COL | 5 | 72 | 77 | 0 | 0 | 4,368 | 0 (0%) | 0 (0%) | 0.00030 |
| A/H | E5 | KNAP | 5 | 22 | 20 | 0 | 0 | 4,333 | 0 (0%) | 0 (0%) | 0.00028 |
| A/H | E5 | SAT | 5 | 25 | 25 | 0 | 0 | 5,354 | 0 (0%) | 0 (0%) | 0.00035 |
| C | E1 | COL | 5 | 252 | 335 | 0 | 0 | 4,663 | 0 (0%) | 0 (0%) | 0.00037 |
| C | E1 | SAT | 5 | 509 | 443 | 0 | 0 | 5,307 | 0 (0%) | 0 (0%) | 0.00044 |
| C | E2 | COL | 5 | 146 | 357 | 0 | 0 | 4,658 | 0 (0%) | 0 (0%) | 0.00038 |
| C | E2 | KNAP | 5 | 754 | 744 | 0 | 0 | 4,301 | 0 (0%) | 0 (0%) | 0.00044 |
| C | E2 | SAT | 5 | 508 | 561 | 0 | 0 | 5,494 | 0 (0%) | 0 (0%) | 0.00048 |
| C | E3 | COL-I | 1 | 1,069 | 1,069 | 0 | 0 | 5,652 | 0 (0%) | 0 (0%) | 0.00060 |
| C | E3 | COL-U | 4 | 472 | 472 | 0 | 0 | 5,918 | 0 (0%) | 0 (0%) | 0.00048 |
| C | E5 | COL | 5 | 171 | 434 | 0 | 0 | 4,756 | 0 (0%) | 0 (0%) | 0.00040 |
| C | E5 | SAT | 5 | 751 | 1,481 | 0 | 0 | 5,840 | 1 (20%) | 0 (0%) | 0.00071 |
| C | E5 | STATE | 8 | 1,157 | 1,188 | 0 | 0 | 5,241 | 0 (0%) | 0 (0%) | 0.00060 |
| **All** | | | **83** | **171** | **492** | **0** | **0** | | **2** | **0** | **0.00044** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 403, max 4,479; 34 responses (41%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `witness_partial` | 2 |
| `witness_malformed` | 1 |
| `fenced_answer_no_marker` | 1 |
| `repeated_variable` | 1 |
| `order_differs_from_requested` | 1 |
| `extra_text_in_block` | 1 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E2 | SAT/J/g=SAT | 1 |
| E5 | SAT/DEAD-PERM | 1 |

