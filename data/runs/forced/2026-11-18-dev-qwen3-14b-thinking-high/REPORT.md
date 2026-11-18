# Run forced/2026-11-18-dev-qwen3-14b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-14b`; returned `qwen/qwen3-14b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 28}.
- **Condition:** `thinking-high-forced`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 28 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_room': 0}.
- **Status:** complete; 28 responses, 0 failed calls, 2 from cache.
- **Spend:** $0.0901 API-reported over 2 invocation(s) (last cap $0.20; dry-run estimate $0.09, worst case $0.12).
- **Code:** git `7d32556690649dcbcff0cffd5ae6d66f2c8cadda`; scorer `scorer-1.5.2` at `7d32556690649dcbcff0cffd5ae6d66f2c8cadda`.

## Forced final answers

The responses of `2026-11-18-dev-qwen3-14b-thinking-high` that stopped at the cap with a reasoning trace, replayed with the thinking closed (template `force-1`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 28 selected; 0 stopped at the cap without a trace and were skipped. Of 28 forced responses, 25 answered and 3 went back to reasoning and stopped at max_tokens again (`truncated` below).

These records are a stratum of their own. The source run's records stay `truncated` (censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | truncated | Correct of ok |
|---|---|---|---|---|---|
| A/H | E1 | 5 | 4 | 1 | 3/4 (75%) |
| A/H | E2 | 7 | 5 | 2 | 4/5 (80%) |
| A/H | E5 | 2 | 2 | 0 | 0/2 (0%) |
| C | E2 | 6 | 6 | 0 | 1/6 (17%) |
| C | E3 | 7 | 7 | 0 | 5/7 (71%) |
| C | E5 | 1 | 1 | 0 | 0/1 (0%) |
| **All** | | **28** | **25** | **3** | **13/25 (52%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | SAT | 5 | 29 | 844 | 0 | 0 | 35,069 | 1 (20%) | 0 (0%) | 0.00353 |
| A/H | E2 | COL | 1 | 11 | 11 | 0 | 0 | 33,293 | 0 (0%) | 0 (0%) | 0.00320 |
| A/H | E2 | SAT | 6 | 63 | 1,401 | 0 | 0 | 35,686 | 2 (33%) | 0 (0%) | 0.00369 |
| A/H | E5 | SAT | 2 | 27 | 27 | 0 | 0 | 34,172 | 0 (0%) | 0 (0%) | 0.00329 |
| C | E2 | KNAP | 1 | 561 | 561 | 0 | 0 | 32,972 | 0 (0%) | 0 (0%) | 0.00327 |
| C | E2 | SAT | 5 | 103 | 164 | 0 | 0 | 34,194 | 0 (0%) | 0 (0%) | 0.00331 |
| C | E3 | COL-U | 7 | 472 | 488 | 0 | 0 | 34,589 | 0 (0%) | 0 (0%) | 0.00341 |
| C | E5 | SAT | 1 | 128 | 128 | 0 | 0 | 34,513 | 0 (0%) | 0 (0%) | 0.00334 |
| **All** | | | **28** | **116** | **629** | **0** | **0** | | **3** | **0** | **0.00345** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 479, max 4,097; 7 responses (25%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `witness_malformed` | 4 |
| `latex_unwrapped` | 1 |
| `order_differs_from_requested` | 1 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E1 | SAT/critical/x | 1 |
| E2 | SAT/K/g=SAT | 1 |
| E2 | SAT/K/g=UNSAT | 1 |

