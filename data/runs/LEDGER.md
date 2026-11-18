# Inference ledger

One row per live run or probe batch. Costs are API-reported (`usage.cost`, summed); dry runs cost nothing and are not listed.

| Date (UTC) | Run id | Model | Condition | Items | API cost (USD) | Budget tag | Notes |
|---|---|---|---|---|---|---|---|
| 2026-11-18 | probes/2026-11-17 | openai/gpt-oss-20b, openai/gpt-oss-120b, qwen/qwen3-32b, qwen/qwen3-14b, qwen/qwen3-30b-a3b, deepseek/deepseek-r1-0528, qwen/qwen3-235b-a22b-thinking-2507 | probe | 62 | 0.005539 | runner-agent | provider probes (calls in the Items column) |
| 2026-11-18 | 2026-11-18-smoke-qwen3-32b-direct | qwen/qwen3-32b | direct | 254 | 0.019379 | runner-agent | acceptance run (c) status=complete |
