# Run forced-2/all-k8192/2026-11-18-dev-qwen3-14b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-14b`; returned `qwen/qwen3-14b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 69}.
- **Condition:** `thinking-high-forced-k8192`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 69 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0645 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.06, worst case $0.12).
- **Code:** git `2c27e2b27f86f29699b08001a77d758bc9e977f4`; scorer `scorer-1.5.2` at `2c27e2b27f86f29699b08001a77d758bc9e977f4`.

## Forced final answers

The responses of `2026-11-18-dev-qwen3-14b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 8192 tokens by the model's tokenizer (`Qwen/Qwen3-32B/tokenizer.json`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 69 forced responses, 69 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below). 69 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; the source run `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`.
- **Budget:** 46 of the selected traces were within budget and not sent: their natural answers stand. 69 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 63 prompt tokens as a raw prompt and 72 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 23 of the 68 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | Correct of ok |
|---|---|---|---|---|
| A/H | E1 | 10 | 10 | 6/10 (60%) |
| A/H | E2 | 8 | 8 | 7/8 (88%) |
| A/H | E5 | 10 | 10 | 6/10 (60%) |
| C | E1 | 9 | 9 | 5/9 (56%) |
| C | E2 | 13 | 13 | 3/13 (23%) |
| C | E3 | 5 | 5 | 3/5 (60%) |
| C | E5 | 14 | 14 | 1/14 (7%) |
| **All** | | **69** | **69** | **31/69 (45%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 5 | 11 | 401 | 0 | 0 | 8,565 | 0 (0%) | 0 (0%) | 0.00090 |
| A/H | E1 | SAT | 5 | 37 | 36 | 0 | 0 | 10,728 | 0 (0%) | 0 (0%) | 0.00104 |
| A/H | E2 | COL | 3 | 134 | 110 | 0 | 0 | 8,565 | 0 (0%) | 0 (0%) | 0.00084 |
| A/H | E2 | SAT | 5 | 41 | 42 | 0 | 0 | 10,898 | 0 (0%) | 0 (0%) | 0.00105 |
| A/H | E5 | COL | 1 | 11 | 11 | 0 | 0 | 8,456 | 0 (0%) | 0 (0%) | 0.00081 |
| A/H | E5 | KNAP | 4 | 18 | 18 | 0 | 0 | 8,427 | 0 (0%) | 0 (0%) | 0.00081 |
| A/H | E5 | SAT | 5 | 25 | 25 | 0 | 0 | 9,450 | 0 (0%) | 0 (0%) | 0.00091 |
| C | E1 | COL | 4 | 116 | 175 | 0 | 0 | 8,756 | 0 (0%) | 0 (0%) | 0.00087 |
| C | E1 | SAT | 5 | 103 | 159 | 0 | 0 | 9,403 | 0 (0%) | 0 (0%) | 0.00093 |
| C | E2 | COL | 3 | 116 | 166 | 0 | 0 | 8,753 | 0 (0%) | 0 (0%) | 0.00087 |
| C | E2 | KNAP | 5 | 364 | 340 | 0 | 0 | 8,397 | 0 (0%) | 0 (0%) | 0.00087 |
| C | E2 | SAT | 5 | 103 | 163 | 0 | 0 | 9,590 | 0 (0%) | 0 (0%) | 0.00095 |
| C | E3 | COL-I | 1 | 233 | 233 | 0 | 0 | 9,748 | 0 (0%) | 0 (0%) | 0.00098 |
| C | E3 | COL-U | 4 | 472 | 472 | 0 | 0 | 10,014 | 0 (0%) | 0 (0%) | 0.00105 |
| C | E5 | COL | 5 | 172 | 270 | 0 | 0 | 8,852 | 0 (0%) | 0 (0%) | 0.00090 |
| C | E5 | SAT | 5 | 128 | 128 | 0 | 0 | 9,936 | 0 (0%) | 0 (0%) | 0.00098 |
| C | E5 | STATE | 4 | 103 | 237 | 0 | 0 | 9,636 | 0 (0%) | 0 (0%) | 0.00097 |
| **All** | | | **69** | **103** | **181** | **0** | **0** | | **0** | **0** | **0.00093** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 82, max 1,706; 14 responses (20%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `latex_unwrapped` | 3 |
| `witness_malformed` | 2 |
| `answer_blocks_disagree` | 1 |
| `order_differs_from_requested` | 1 |

