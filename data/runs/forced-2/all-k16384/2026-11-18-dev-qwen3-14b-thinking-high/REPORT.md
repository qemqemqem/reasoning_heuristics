# Run forced-2/all-k16384/2026-11-18-dev-qwen3-14b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-14b`; returned `qwen/qwen3-14b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 26}.
- **Condition:** `thinking-high-forced-k16384`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 26 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0473 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.04, worst case $0.07).
- **Code:** git `2c27e2b27f86f29699b08001a77d758bc9e977f4`; scorer `scorer-1.5.2` at `2c27e2b27f86f29699b08001a77d758bc9e977f4`.

## Forced final answers

The responses of `2026-11-18-dev-qwen3-14b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 16384 tokens by the model's tokenizer (`Qwen/Qwen3-32B/tokenizer.json`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 26 forced responses, 24 answered and 2 went back to reasoning and stopped at max_tokens again (`truncated` below). 24 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; the source run `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`.
- **Budget:** 89 of the selected traces were within budget and not sent: their natural answers stand. 26 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 63 prompt tokens as a raw prompt and 72 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 10 of the 25 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | truncated | Correct of ok |
|---|---|---|---|---|---|
| A/H | E1 | 4 | 3 | 1 | 1/3 (33%) |
| A/H | E2 | 5 | 4 | 1 | 3/4 (75%) |
| A/H | E5 | 2 | 2 | 0 | 1/2 (50%) |
| C | E1 | 1 | 1 | 0 | 0/1 (0%) |
| C | E2 | 3 | 3 | 0 | 1/3 (33%) |
| C | E3 | 2 | 2 | 0 | 1/2 (50%) |
| C | E5 | 9 | 9 | 0 | 0/9 (0%) |
| **All** | | **26** | **24** | **2** | **7/24 (29%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 1 | 11 | 11 | 0 | 0 | 16,760 | 0 (0%) | 0 (0%) | 0.00161 |
| A/H | E1 | SAT | 3 | 37 | 1,387 | 0 | 0 | 19,189 | 1 (33%) | 0 (0%) | 0.00211 |
| A/H | E2 | SAT | 5 | 45 | 852 | 0 | 0 | 19,090 | 1 (20%) | 0 (0%) | 0.00200 |
| A/H | E5 | KNAP | 1 | 25 | 25 | 0 | 0 | 16,603 | 0 (0%) | 0 (0%) | 0.00160 |
| A/H | E5 | SAT | 1 | 25 | 25 | 0 | 0 | 17,655 | 0 (0%) | 0 (0%) | 0.00170 |
| C | E1 | SAT | 1 | 103 | 103 | 0 | 0 | 17,610 | 0 (0%) | 0 (0%) | 0.00171 |
| C | E2 | KNAP | 1 | 642 | 642 | 0 | 0 | 16,589 | 0 (0%) | 0 (0%) | 0.00172 |
| C | E2 | SAT | 2 | 103 | 103 | 0 | 0 | 17,782 | 0 (0%) | 0 (0%) | 0.00173 |
| C | E3 | COL-U | 2 | 472 | 472 | 0 | 0 | 18,206 | 0 (0%) | 0 (0%) | 0.00184 |
| C | E5 | COL | 3 | 8 | 62 | 0 | 0 | 17,044 | 0 (0%) | 0 (0%) | 0.00165 |
| C | E5 | SAT | 5 | 128 | 128 | 0 | 0 | 18,127 | 0 (0%) | 0 (0%) | 0.00176 |
| C | E5 | STATE | 1 | 103 | 103 | 0 | 0 | 17,831 | 0 (0%) | 0 (0%) | 0.00173 |
| **All** | | | **26** | **103** | **435** | **0** | **0** | | **2** | **0** | **0.00182** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 340, max 4,097; 3 responses (12%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `witness_partial` | 1 |
| `latex_unwrapped` | 1 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E1 | SAT/critical/x | 1 |
| E2 | SAT/K/g=SAT | 1 |

