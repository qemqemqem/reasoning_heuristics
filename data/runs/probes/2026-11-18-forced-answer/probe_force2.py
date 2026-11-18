"""Probe force-2 for gpt-oss: the force-1 harmony prompt, sent to a provider that honours raw prompts on
/completions (DeepInfra bf16; DekaLLM wraps the prompt as a chat user message), with and without logit_bias
banning the tokens that leave the final channel (<|channel|> 200005, <|start|> 200006, <|end|> 200007).

Two sets of source responses from one run:
  cut     the first response cut at the cap per unit (as in the force-1 probes)
  done    the first response that finished per unit: its whole trace, then the answer forced. A sound forcing
          method should give the model's own final answer here (agreement at f = 1).
Usage: probe_force2.py <run dir> <out.jsonl> <provider slug> [max_tokens]. Saves raw responses first; never prints the key."""
import gzip
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from reasoning_heuristics.evals.force import forced_prompt
from reasoning_heuristics.evals.scoring import ResponseView, score_response

RUN, OUT, SLUG = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
MAX_TOKENS = int(sys.argv[4]) if len(sys.argv) > 4 else 4096
BAN = {"200005": -100, "200006": -100, "200007": -100}
UNITS = [("C", "E2", "knapsack"), ("C", "E2", "3-SAT"), ("C", "E3", "colouring (gadget)"), ("A/H", "E2", "SAT"),
         ("C", "E5", "colouring (k=3)"), ("A/H", "E1", "SAT"), ("A/H", "E2", "COL"), ("C", "E2", "colouring")]
items = {}
for p in json.loads((RUN / "manifest.json").read_text())["items"]["files"]:
    for line in gzip.open(p, "rt"):
        it = json.loads(line)
        items[it["item_id"]] = it
cut, done = {}, {}
for line in gzip.open(RUN / "raw.jsonl.gz", "rt"):
    r = json.loads(line)
    ch = ((r.get("response") or {}).get("choices") or [{}])[0]
    it = items[r["item_id"]]
    u = (it["vertical"], it["eval_id"], it["domain"])
    if u not in UNITS or not ((ch.get("message") or {}).get("reasoning") or "").strip():
        continue
    if ch.get("finish_reason") == "length" and u not in cut:
        cut[u] = r
    if ch.get("finish_reason") == "stop" and (ch.get("message") or {}).get("content") and u not in done:
        done[u] = r
jobs = []
for kind, recs in (("cut", cut), ("done", done)):
    for u, r in recs.items():
        trace = r["response"]["choices"][0]["message"]["reasoning"]
        body = {"model": r["request"]["model"], "prompt": forced_prompt(r["request"], trace), "max_tokens": MAX_TOKENS,
                "temperature": r["request"]["temperature"], "top_p": r["request"]["top_p"],
                "provider": {"order": [SLUG], "allow_fallbacks": False, "require_parameters": True}}
        variants = (("plain", {}), ("ban", {"logit_bias": BAN})) if kind == "cut" else (("ban", {"logit_bias": BAN}),)
        for name, extra in variants:
            jobs.append((kind, name, u, r, {**body, **extra}))


def call(job):
    kind, name, u, r, body = job
    req = urllib.request.Request("https://openrouter.ai/api/v1/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
                                          "Content-Type": "application/json", "X-Title": "reasoning-heuristics force-2 probe"})
    data, err = None, None
    for attempt in range(4):
        try:
            data, err = json.load(urllib.request.urlopen(req, timeout=900)), None
            break
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}: {e.read()[:300]!r}"
            if e.code not in (429, 500, 502, 503, 504):
                break
        except Exception as e:
            err = repr(e)[:300]
        time.sleep(20 * (attempt + 1))
    with OUT.with_suffix(".raw.jsonl").open("a") as f:
        f.write(json.dumps({"kind": kind, "variant": name, "item_id": r["item_id"], "request": body, "response": data, "error": err}) + "\n")
    return job, data, err


with ThreadPoolExecutor(6) as ex:
    for (kind, name, u, r, body), data, err in ex.map(call, jobs):
        ch = ((data or {}).get("choices") or [{}])[0]
        view = ResponseView.from_api(data, max_tokens=MAX_TOKENS, error=err)
        try:
            s = score_response(items[r["item_id"]], view)
        except Exception as e:
            s = {"category": f"scoring error {e!r}"}
        nat = ""
        if kind == "done":
            nview = ResponseView.from_api(r["response"], max_tokens=r["request"]["max_tokens"])
            ns = score_response(items[r["item_id"]], nview)
            nat = f" | natural {ns.get('category')}/{ns.get('correct')} same_answer={ns.get('answer_key') == s.get('answer_key')}"
        u_ = (data or {}).get("usage") or {}
        print(f"{kind:4s} {name:5s} {'/'.join(u):24s} finish {ch.get('finish_reason')} tokens {u_.get('completion_tokens')} "
              f"reasoning {len(ch.get('reasoning') or '')}ch | {s.get('category')} correct={s.get('correct')}{nat} | "
              f"text {(ch.get('text') or '')[:50]!r} | err {err}")
