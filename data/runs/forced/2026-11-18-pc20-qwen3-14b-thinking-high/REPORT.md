# Run forced/2026-11-18-pc20-qwen3-14b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-14b`; returned `qwen/qwen3-14b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 21}.
- **Condition:** `thinking-high-forced`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 21 (data/items/pc20/C_E2_dev_s1.jsonl.gz, data/items/pc20/AH_E5_dev_s1.jsonl.gz, data/items/pc20/C_E1_dev_s1.jsonl.gz); skipped {'no_trace': 0}.
- **Status:** complete; 21 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0692 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.07, worst case $0.09).
- **Code:** git `3223682c25e56bc749b4ebed1cf3a1732b022c07`; scorer `scorer-1.5.2` at `3223682c25e56bc749b4ebed1cf3a1732b022c07`.

## Forced final answers

The responses of `2026-11-18-pc20-qwen3-14b-thinking-high` that stopped at the cap with a reasoning trace, replayed with the thinking closed (template `force-1`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 21 selected; 0 stopped at the cap without a trace and were skipped. Of 21 forced responses, 21 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below).

These records are a stratum of their own. The source run's records stay `truncated` (censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | Correct of ok |
|---|---|---|---|---|
| A/H | E5 | 7 | 7 | 0/7 (0%) |
| C | E1 | 2 | 2 | 0/2 (0%) |
| C | E2 | 12 | 12 | 1/12 (8%) |
| **All** | | **21** | **21** | **1/21 (5%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E5 | COL | 2 | 56 | 56 | 0 | 0 | 33,097 | 0 (0%) | 0 (0%) | 0.00319 |
| A/H | E5 | SAT | 5 | 29 | 25 | 0 | 0 | 34,299 | 0 (0%) | 0 (0%) | 0.00330 |
| C | E1 | SAT | 2 | 103 | 103 | 0 | 0 | 34,082 | 0 (0%) | 0 (0%) | 0.00329 |
| C | E2 | SAT | 12 | 103 | 112 | 0 | 0 | 34,290 | 0 (0%) | 0 (0%) | 0.00331 |
| **All** | | | **21** | **103** | **85** | **0** | **0** | | **0** | **0** | **0.00330** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 11, max 119; 2 responses (10%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

