"""Probe: an answer-format header at the start of the forced answer (force-2 plus a header), on a provider that
passes raw prompts through. Re-sends force-2 requests from committed passes with the header appended to the
prompt, so the model's first tokens continue the answer in the required format:
  C and B4/C4 items: "ANSWER:"        A/H items (JSON answers): '{"'
Sets: `fail` = every forced answer in a cut pass that is not ok (unparsed, partial, runaway); `done` = the first
N records of a done pass (f = 1 control: does the header change the model's own answer?).
Usage: probe_header.py <forced-2 pass dir> <fail|done> <out.jsonl> [N]. Saves raw responses first; never prints the key."""
import gzip
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from reasoning_heuristics.evals.client import OpenRouterClient
from reasoning_heuristics.evals.score import load_run_items
from reasoning_heuristics.evals.scoring import ResponseView, score_response

PASS, SET, OUT = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
N = int(sys.argv[4]) if len(sys.argv) > 4 else 20
manifest = json.loads((PASS / "manifest.json").read_text())
items = load_run_items(manifest, True, None)
scored = {(r["item_id"], r.get("sample", 0)): r for r in map(json.loads, gzip.open(PASS / "scored.jsonl.gz", "rt"))}
raw = [json.loads(l) for l in gzip.open(PASS / "raw.jsonl.gz", "rt")]


def header(item):
    return '{"' if item["vertical"] == "A/H" else "ANSWER:"


picked = []
for r in raw:
    s = scored[(r["item_id"], r.get("sample", 0))]
    if SET == "fail" and s["category"] != "ok":
        resp = r.get("response") or {}
        ch = (resp.get("choices") or [{}])[0]
        if not (ch.get("text") or "").strip() and not resp.get("usage"):
            continue  # provider-empty: retried by the client now, not a format problem
        picked.append(r)
    elif SET == "done" and r.get("sample", 0) == 0 and s.get("natural_category") == "ok":
        picked.append(r)
picked = picked[:N] if SET == "done" else picked
client = OpenRouterClient(max_attempts=4, app_title="reasoning-heuristics header probe")


def call(r):
    h = header(items[r["item_id"]])
    body = {**r["request"], "prompt": r["request"]["prompt"] + h}
    res = client.complete(body)
    with OUT.with_suffix(".raw.jsonl").open("a") as f:
        f.write(json.dumps({"item_id": r["item_id"], "header": h, "request": body, "response": res.response, "error": res.error,
                            "before": scored[(r["item_id"], r.get("sample", 0))]["category"]}) + "\n")
    return r, h, res


rows = []
with ThreadPoolExecutor(6) as ex:
    for r, h, res in ex.map(call, picked):
        data = res.response
        ch = ((data or {}).get("choices") or [{}])[0]
        chat_like = None if data is None else {**data, "choices": [{"message": {"content": h + (ch.get("text") or ""), "reasoning": ch.get("reasoning")},
                                                                     "finish_reason": ch.get("finish_reason")}]}
        s = score_response(items[r["item_id"]], ResponseView.from_api(chat_like, max_tokens=r["request"]["max_tokens"], error=res.error))
        before = scored[(r["item_id"], r.get("sample", 0))]
        same = (s["category"] == "ok" and s.get("answer_key") == before.get("natural_answer_key")) if SET == "done" else None
        rows.append((before["category"], s["category"], s.get("correct"), same, before.get("natural_correct")))
        print(f"{items[r['item_id']]['vertical']:5s} {items[r['item_id']]['domain']:20s} before {before['category']:12s} -> {s['category']:12s} "
              f"correct={s.get('correct')} {'same_as_natural=' + str(same) if SET == 'done' else ''} | {(h + (ch.get('text') or ''))[:70]!r}")
ok = sum(1 for b, a, *_ in rows if a == "ok")
print(f"\n{SET}: {len(rows)} calls; ok with the header {ok}" + (f"; same as natural {sum(1 for *_, same, _n in rows if same)}" if SET == "done" else ""))
