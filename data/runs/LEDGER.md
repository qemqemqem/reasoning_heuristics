# Inference ledger

One row per live run or probe batch. Costs are API-reported (`usage.cost`, summed); dry runs cost nothing and are not listed.

| Date (UTC) | Run id | Model | Condition | Items | API cost (USD) | Budget tag | Notes |
|---|---|---|---|---|---|---|---|
| 2026-11-18 | probes/2026-11-17 | openai/gpt-oss-20b, openai/gpt-oss-120b, qwen/qwen3-32b, qwen/qwen3-14b, qwen/qwen3-30b-a3b, deepseek/deepseek-r1-0528, qwen/qwen3-235b-a22b-thinking-2507 | probe | 62 | 0.005539 | runner-agent | provider probes (calls in the Items column) |
| 2026-11-18 | 2026-11-18-smoke-qwen3-32b-direct | qwen/qwen3-32b | direct | 254 | 0.019379 | runner-agent | acceptance run (c) status=complete |
| 2026-11-18 | 2026-11-18-smoke-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high | 254 | 0.494084 | runner-agent | acceptance run (b) status=complete |
| 2026-11-18 | 2026-11-18-smoke-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high | 188 | 0.377519 | runner-agent | acceptance run (a) status=stopped |
| 2026-11-18 | 2026-11-18-smoke-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high | 66 | 0.238390 | runner-agent | acceptance run (a), resumed after IncompleteRead status=complete; Items corrected by hand from 254 to the 66 new responses (this process started before the ledger fix) |
| 2026-11-18 | 2026-11-18-dev-qwen3-32b-direct | qwen/qwen3-32b | direct | 1270 | 0.098578 | dev-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-dev-qwen3-14b-direct | qwen/qwen3-14b | direct | 1270 | 0.126604 | dev-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-dev-gpt-oss-120b-thinking-high | openai/gpt-oss-120b | thinking-high | 49 | 0.182745 | dev-2026-11-18 | status=incomplete |
| 2026-11-18 | 2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high | 29 | 0.113582 | dev-2026-11-18 | status=incomplete |
| 2026-11-18 | 2026-11-18-dev-gpt-oss-20b-thinking-low | openai/gpt-oss-20b | thinking-low | 1270 | 0.171011 | dev-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-dev-qwen3-14b-thinking-high | qwen/qwen3-14b | thinking-high | 22 | 0.101905 | dev-2026-11-18 | status=incomplete |
| 2026-11-18 | 2026-11-18-dev-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high | 24 | 0.135034 | dev-2026-11-18 | status=incomplete |
