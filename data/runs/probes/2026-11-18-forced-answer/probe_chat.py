"""Probe: can a truncated thinking response be given a final chance to answer, through OpenRouter?

For a few truncated responses of a run, three ways of asking for the answer:
  reprompt  the partial reasoning as the assistant's previous (visible) turn, then a user turn saying the
            thinking budget is used up; a short second thinking span (effort low) and max_tokens 4096
  details   the same, but the partial reasoning goes back as reasoning_details on an empty assistant turn
            (OpenRouter's documented way to preserve reasoning); prompt_tokens shows whether it was used
  prefill   the partial reasoning plus "Final answer:" as a final assistant message (content prefill)
Prints a summary only. Run from a worktree with PYTHONPATH=src. Never prints the API key."""
import gzip, json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from reasoning_heuristics.evals.client import OpenRouterClient
from reasoning_heuristics.evals.scoring import ResponseView, score_response

RUN, OUT = Path(sys.argv[1]), Path(sys.argv[2])
UNITS = [tuple(u.split(":")) for u in sys.argv[3].split(",")]  # vertical:eval:domain
FORCE = ("You have reached your thinking budget. Stop working and give your final answer now, using your work so far, "
         "in the format the question asks for.")
items = {}
for p in json.loads((RUN / "manifest.json").read_text())["items"]["files"]:
    for line in gzip.open(p, "rt"):
        it = json.loads(line); items[it["item_id"]] = it
picked = {}
for line in gzip.open(RUN / "raw.jsonl.gz"):
    r = json.loads(line)
    ch = ((r.get("response") or {}).get("choices") or [{}])[0]
    it = items[r["item_id"]]
    u = (it["vertical"], it["eval_id"], it["domain"])
    if ch.get("finish_reason") == "length" and u in UNITS and u not in picked:
        picked[u] = r
SHORT = FORCE + " Do not start over: answer from the work you have done."
VARIANTS = sys.argv[4].split(",") if len(sys.argv) > 4 else ["reprompt", "short"]
jobs = []
for u, r in picked.items():
    req, msg = r["request"], r["response"]["choices"][0]["message"]
    base = {k: v for k, v in req.items() if k != "messages"}
    user = req["messages"]
    trace = msg.get("reasoning") or ""
    if "reprompt" in VARIANTS:
        jobs.append(("reprompt", u, r, {**base, "reasoning": {"effort": "low"}, "max_tokens": 4096,
                     "messages": user + [{"role": "assistant", "content": trace}, {"role": "user", "content": FORCE}]}))
    if "short" in VARIANTS:
        jobs.append(("short", u, r, {**base, "reasoning": {"effort": "low"}, "max_tokens": 1024,
                     "messages": user + [{"role": "assistant", "content": trace}, {"role": "user", "content": SHORT}]}))
client = OpenRouterClient(max_attempts=4, app_title="reasoning-heuristics forced-answer probe")
RAW = OUT.with_suffix(".raw.jsonl")
def call(job):
    variant, u, r, body = job
    res = client.chat(body)
    with RAW.open("a") as f:  # saved before anything else touches it
        f.write(json.dumps({"variant": variant, "item_id": r["item_id"], "request": body, "response": res.response,
                            "error": res.error}) + "\n")
    return variant, u, r, body, res
with ThreadPoolExecutor(6) as ex, OUT.open("w") as out:
    for variant, u, r, body, res in ex.map(call, jobs):
        data = res.response
        view = ResponseView.from_api(data, max_tokens=body["max_tokens"], error=None if data else res.error)
        try:
            s = score_response(items[r["item_id"]], view)
        except Exception as e:  # keep going: the raw response is already saved
            s = {"category": f"scoring error: {e!r}"}
        usage = (data or {}).get("usage") or {}
        out.write(json.dumps({"variant": variant, "item_id": r["item_id"], "request": body, "response": data,
                              "error": None if data else res.error, "score": s}) + "\n")
        content = (((data or {}).get("choices") or [{}])[0].get("message") or {}).get("content") or ""
        print(f"{variant:8s} {'/'.join(u):18s} prompt {usage.get('prompt_tokens')} completion {usage.get('completion_tokens')} "
              f"reasoning {((usage.get('completion_tokens_details') or {}).get('reasoning_tokens'))} finish {view.finish_reason} "
              f"cost {usage.get('cost')} | {s.get('category')} correct={s.get('correct')} members={(s.get('members_matched') or [])[:2]} "
              f"| content[:90]={content[:90]!r}")
