# Invalid as forced answers

These calls went to DekaLLM, gpt-oss's configured pin. DekaLLM wraps a raw `/completions` prompt as a chat user message. Its `/completions` and `/chat/completions` calls with the same text report the same prompt_tokens: 160 = 160 for gpt-oss-20b, 206 = 206 for gpt-oss-120b.

So the model read its own truncated trace, with the harmony markup, as text from the user, and reasoned afresh. These responses are not continuations of its thinking, and are not forced answers.

They are kept because they were paid for and the ledger rows name them. The evidence is in `data/runs/probes/2026-11-18-forced-answer/PROBES.md` (batches 10–12). Forced answers that count are force-2's, which go to a provider that honours raw prompts (docs/RUNNER.md).
