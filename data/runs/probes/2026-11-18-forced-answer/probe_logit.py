"""Probe: do the pinned providers honour logit_bias and return logprobs on POST /completions?

For each model, a short raw prompt asking for a one-word answer, sent twice:
  plain   max_tokens 40, logprobs + top_logprobs 5
  banned  the same, with the end-of-message token(s) banned via logit_bias (-100): if honoured, the model
          cannot stop, so it runs to max_tokens (finish_reason length) instead of stopping.
Saves every raw response before touching it. Never prints the API key."""
import json
import os
import sys
import urllib.request
from pathlib import Path

OUT = Path(sys.argv[1])
GPT_OSS = ("<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.\nKnowledge cutoff: 2024-06\n\n"
           "Reasoning: low\n\n# Valid channels: analysis, commentary, final. Channel must be included for every message.<|end|>"
           "<|start|>user<|message|>Is 17 a prime number? Answer with one word, YES or NO.<|end|>"
           "<|start|>assistant<|channel|>analysis<|message|>17 has no divisors other than 1 and itself.<|end|>"
           "<|start|>assistant<|channel|>final<|message|>")
QWEN = ("<|im_start|>user\nIs 17 a prime number? Answer with one word, YES or NO.<|im_end|>\n<|im_start|>assistant\n"
        "<think>\n17 has no divisors other than 1 and itself.\n</think>\n\n")
CASES = [
    ("openai/gpt-oss-20b", {"order": ["dekallm/bf16"], "allow_fallbacks": False, "require_parameters": True, "quantizations": ["bf16"]},
     GPT_OSS, {"200002": -100, "200007": -100, "200012": -100}),          # <|return|>, <|end|>, <|call|>
    ("openai/gpt-oss-120b", {"order": ["dekallm/bf16"], "allow_fallbacks": False, "require_parameters": True, "quantizations": ["bf16"]},
     GPT_OSS, {"200002": -100, "200007": -100, "200012": -100}),
    ("qwen/qwen3-32b", {"order": ["deepinfra/fp8/flex"], "allow_fallbacks": False, "require_parameters": True, "quantizations": ["fp8"]},
     QWEN, {"151645": -100, "151643": -100}),                              # <|im_end|>, <|endoftext|>
]


def post(body):
    req = urllib.request.Request("https://openrouter.ai/api/v1/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
                                          "Content-Type": "application/json", "X-Title": "reasoning-heuristics logit probe"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=300)), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read()[:400]!r}"
    except Exception as e:
        return None, repr(e)[:300]


with OUT.open("a") as f:
    for model, provider, prompt, ban in CASES:
        for variant in ("plain", "banned"):
            body = {"model": model, "provider": provider, "prompt": prompt, "max_tokens": 40, "temperature": 0.0,
                    "logprobs": True, "top_logprobs": 5}
            if variant == "banned":
                body["logit_bias"] = ban
            data, err = post(body)
            f.write(json.dumps({"model": model, "variant": variant, "request": body, "response": data, "error": err}) + "\n")
            f.flush()
            ch = ((data or {}).get("choices") or [{}])[0]
            lp = ch.get("logprobs")
            lp_note = "none" if not lp else (f"keys {sorted(lp.keys())[:4]}" if isinstance(lp, dict) else type(lp).__name__)
            print(f"{model:20s} {variant:6s} finish {ch.get('finish_reason')} tokens {((data or {}).get('usage') or {}).get('completion_tokens')} "
                  f"text {(ch.get('text') or '')[:60]!r} | logprobs {lp_note} | err {err}")
