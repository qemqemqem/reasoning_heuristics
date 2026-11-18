"""Probe: force the final answer after a truncated thinking trace, through OpenRouter's raw completions endpoint.

We write the chat template ourselves and end the thinking:
  gpt-oss (harmony): ...<|start|>assistant<|channel|>analysis<|message|>{trace}<|end|><|start|>assistant<|channel|>final<|message|>
  Qwen3:             ...<|im_start|>assistant\n<think>\n{trace}\n\n{QWEN_STOP}\n</think>\n\n
and let the model write only the answer (max_tokens small). Saves every raw response before touching it.
Usage: probe_raw.py <run dir> <out.jsonl> <units vertical:eval:domain,...> [max_tokens]
Run from a worktree with PYTHONPATH=src. Never prints the API key."""
import gzip
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from reasoning_heuristics.evals.scoring import ResponseView, score_response

RUN, OUT = Path(sys.argv[1]), Path(sys.argv[2])
UNITS = [tuple(u.split(":")) for u in sys.argv[3].split(",")]
MAX_TOKENS = int(sys.argv[4]) if len(sys.argv) > 4 else 1024
QWEN_STOP = "Considering the limited time by the user, I have to give the solution based on the thinking directly now."
GPT_OSS_STOP = "I have run out of time to think, so I must give my final answer now, based on the work above."
GPT_OSS_SYSTEM = ("You are ChatGPT, a large language model trained by OpenAI.\nKnowledge cutoff: 2024-06\n\n"
                  "Reasoning: {effort}\n\n# Valid channels: analysis, commentary, final. Channel must be included for every message.")

items = {}
for p in json.loads((RUN / "manifest.json").read_text())["items"]["files"]:
    for line in gzip.open(p, "rt"):
        it = json.loads(line)
        items[it["item_id"]] = it
picked = {}
for line in gzip.open(RUN / "raw.jsonl.gz"):
    r = json.loads(line)
    ch = ((r.get("response") or {}).get("choices") or [{}])[0]
    it = items[r["item_id"]]
    u = (it["vertical"], it["eval_id"], it["domain"])
    if ch.get("finish_reason") == "length" and u in UNITS and u not in picked:
        picked[u] = r


WRAP = os.environ.get("WRAP", "1") == "1"
PREFIX = os.environ.get("PREFIX", "0") == "1"


def answer_prefix(item: dict) -> str:
    return ('{"' if item["vertical"] == "A/H" else "ANSWER:") if PREFIX else ""


def raw_prompt(req: dict, trace: str, prefix: str = "") -> str:
    user = req["messages"][-1]["content"]
    system = [m["content"] for m in req["messages"] if m["role"] == "system"]
    if req["model"].startswith("openai/gpt-oss"):
        effort = (req.get("reasoning") or {}).get("effort", "medium")
        sys_msg = GPT_OSS_SYSTEM.format(effort=effort)
        dev = f"<|start|>developer<|message|># Instructions\n\n{system[0]}<|end|>" if system else ""
        return (f"<|start|>system<|message|>{sys_msg}<|end|>{dev}<|start|>user<|message|>{user}<|end|>"
                f"<|start|>assistant<|channel|>analysis<|message|>{trace.rstrip()}{chr(10) * 2 + GPT_OSS_STOP if WRAP else ''}<|end|>"
                f"<|start|>assistant<|channel|>final<|message|>{prefix}")
    sys_part = f"<|im_start|>system\n{system[0]}<|im_end|>\n" if system else ""
    return (f"{sys_part}<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n<think>\n{trace.rstrip()}\n\n"
            f"{QWEN_STOP}\n</think>\n\n{prefix}")


def call(job):
    u, r = job
    req = r["request"]
    trace = r["response"]["choices"][0]["message"].get("reasoning") or ""
    prefix = answer_prefix(items[r["item_id"]])
    body = {"model": req["model"], "provider": req["provider"], "prompt": raw_prompt(req, trace, prefix),
            "max_tokens": MAX_TOKENS, "temperature": req.get("temperature", 1.0), "top_p": req.get("top_p", 1.0),
            **({"top_k": req["top_k"]} if "top_k" in req else {})}
    hreq = urllib.request.Request("https://openrouter.ai/api/v1/completions", data=json.dumps(body).encode(),
                                  headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
                                           "Content-Type": "application/json",
                                           "X-Title": "reasoning-heuristics forced-answer probe"})
    for attempt in range(5):
        try:
            data, err = json.load(urllib.request.urlopen(hreq, timeout=900)), None
            break
        except urllib.error.HTTPError as e:
            data, err = None, f"HTTP {e.code}: {e.read()[:300]!r}"
            if e.code not in (429, 500, 502, 503, 504):
                break
        except Exception as e:
            data, err = None, repr(e)[:300]
        time.sleep(30 * (attempt + 1))
    with OUT.with_suffix(".raw.jsonl").open("a") as f:
        f.write(json.dumps({"item_id": r["item_id"], "request": body, "response": data, "error": err}) + "\n")
    return u, r, body, data, err


with ThreadPoolExecutor(6) as ex, OUT.open("w") as out:
    for u, r, body, data, err in ex.map(call, list(picked.items())):
        choice = ((data or {}).get("choices") or [{}])[0]
        text = choice.get("text")
        if text is None:
            text = (choice.get("message") or {}).get("content")
        text = answer_prefix(items[r["item_id"]]) + (text or "")
        chat_like = None if data is None else {**data, "choices": [{"message": {"content": text, "reasoning": None},
                                                                     "finish_reason": choice.get("finish_reason")}]}
        view = ResponseView.from_api(chat_like, max_tokens=MAX_TOKENS, error=err)
        try:
            s = score_response(items[r["item_id"]], view)
        except Exception as e:
            s = {"category": f"scoring error: {e!r}"}
        usage = (data or {}).get("usage") or {}
        out.write(json.dumps({"item_id": r["item_id"], "unit": u, "score": s, "text": text}) + "\n")
        print(f"{'/'.join(u):24s} prompt {usage.get('prompt_tokens')} completion {usage.get('completion_tokens')} "
              f"finish {choice.get('finish_reason')} cost {usage.get('cost')} | {s.get('category')} correct={s.get('correct')} "
              f"members={(s.get('members_matched') or [])[:3]} | err={err} | text[:100]={(text or '')[:100]!r}")
