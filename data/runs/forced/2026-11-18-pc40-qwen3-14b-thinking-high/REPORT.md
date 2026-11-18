# Run forced/2026-11-18-pc40-qwen3-14b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-14b`; returned `qwen/qwen3-14b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 21}.
- **Condition:** `thinking-high-forced`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 21 (data/items/pc40/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0}.
- **Status:** complete; 21 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0699 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.07, worst case $0.09).
- **Code:** git `3223682c25e56bc749b4ebed1cf3a1732b022c07`; scorer `scorer-1.5.2` at `3223682c25e56bc749b4ebed1cf3a1732b022c07`.

## Forced final answers

The responses of `2026-11-18-pc40-qwen3-14b-thinking-high` that stopped at the cap with a reasoning trace, replayed with the thinking closed (template `force-1`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 21 selected; 0 stopped at the cap without a trace and were skipped. Of 21 forced responses, 21 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below).

These records are a stratum of their own. The source run's records stay `truncated` (censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | Correct of ok |
|---|---|---|---|---|---|
| C | E5 | 21 | 20 | 1 | 3/20 (15%) |
| **All** | | **21** | **20** | **1** | **3/20 (15%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C | E5 | COL | 5 | 176 | 367 | 0 | 0 | 33,424 | 0 (0%) | 0 (0%) | 0.00328 |
| C | E5 | SAT | 14 | 128 | 191 | 0 | 0 | 34,503 | 0 (0%) | 0 (0%) | 0.00335 |
| C | E5 | STATE | 2 | 103 | 103 | 0 | 0 | 34,216 | 0 (0%) | 0 (0%) | 0.00330 |
| **All** | | | **21** | **171** | **224** | **0** | **0** | | **0** | **0** | **0.00333** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 99, max 463; 9 responses (43%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E5-17cca6f8a5-COL_STUCK_vA_eA` | parse_fail | no answer block |

