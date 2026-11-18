"""Batch 11, reconstructed from the two inline runs on 2026-11-18 (the first covered DekaLLM gpt-oss-20b and 120b;
the second the providers below). For each provider: the same text sent as a raw prompt (POST /completions) and as
a chat user message (POST /chat/completions). A provider that honours raw prompts reports fewer prompt tokens for
the raw call (no chat template added) and continues the prompt directly; equal counts mean it wrapped the prompt."""
import json
import os
import urllib.request

lines = [json.loads(l) for l in open("logit_probe.raw.jsonl")]  # batch 10's prompts
GPT = next(l for l in lines if l["model"].startswith("openai"))["request"]["prompt"]
QWEN = next(l for l in lines if l["model"].startswith("qwen"))["request"]["prompt"]
CASES = [("openai/gpt-oss-20b", "dekallm/bf16", GPT), ("openai/gpt-oss-120b", "dekallm/bf16", GPT),
         ("qwen/qwen3-32b", "deepinfra/fp8/flex", QWEN), ("qwen/qwen3-14b", "deepinfra/fp8/flex", QWEN),
         ("openai/gpt-oss-20b", "deepinfra/bf16", GPT), ("openai/gpt-oss-20b", "parasail/fp4", GPT),
         ("openai/gpt-oss-120b", "deepinfra/bf16", GPT), ("openai/gpt-oss-120b", "parasail/fp4", GPT),
         ("openai/gpt-oss-120b", "cerebras/fp16", GPT)]


def post(path, body):
    req = urllib.request.Request("https://openrouter.ai/api/v1" + path, data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"], "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=300))


with open("wrap_test.raw.jsonl", "a") as out:
    for model, slug, prompt in CASES:
        prov = {"order": [slug], "allow_fallbacks": False, "require_parameters": True}
        a = post("/completions", {"model": model, "provider": prov, "prompt": prompt, "max_tokens": 40, "temperature": 0})
        b = post("/chat/completions", {"model": model, "provider": prov, "messages": [{"role": "user", "content": prompt}],
                                       "max_tokens": 40, "temperature": 0})
        out.write(json.dumps({"model": model, "provider": slug, "completions": a, "chat_user_message": b}) + "\n")
