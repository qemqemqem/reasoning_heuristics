"""OpenRouter chat-completions client (and raw text completions): retries with backoff, long timeouts,
full response capture.

Fields follow OpenRouter's public API reference (openrouter.ai/docs, read 2026-11-17):

- request: `model`, `messages`, `max_tokens`, sampling (`temperature`, `top_p`, `top_k`, `seed`),
  `reasoning` ({"effort": ..., "enabled": ..., "max_tokens": ..., "exclude": ...}) and `provider`
  routing ({"order": [...], "allow_fallbacks": false, "quantizations": [...],
  "require_parameters": true, "data_collection": ...});
- response: `id` (generation id), `model`, `provider`, `choices[0].message.{content, reasoning,
  reasoning_details, refusal}`, `choices[0].finish_reason` (normalised: stop / length /
  content_filter / tool_calls / error) and `native_finish_reason`, and `usage` with
  `prompt_tokens`, `completion_tokens`, `completion_tokens_details.reasoning_tokens` and `cost`
  (always returned; the old `usage: {include: true}` flag is deprecated and has no effect);
- raw text completions (`POST /completions`, used by the forced-answer pass, evals/force.py): the
  request carries `prompt` (the chat template written by the caller) instead of `messages`, and the
  choice carries `text` instead of `message`, and `reasoning` for any analysis the model wrote. Not
  every provider passes the prompt through: DekaLLM wraps it as a chat user message (probes,
  2026-11-18), which force.py's raw-prompt check detects.

The whole response JSON is kept; nothing is dropped. The API key is read from the environment
(`OPENROUTER_API_KEY`) inside each request and never stored, returned, logged or written.
The HTTP layer is a plain callable (`Transport`), so tests replace it and nothing here can reach
the network unless the default transport is used.
"""

from __future__ import annotations

import http.client
import json
import os
import random
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable

API_BASE = "https://openrouter.ai/api/v1"
KEY_ENV = "OPENROUTER_API_KEY"
RETRY_STATUS = {408, 409, 425, 429, 500, 502, 503, 504, 520, 522, 524, 529}
FATAL_STATUS = {400, 401, 402, 403, 404, 413, 422}  # bad request, auth, no credits, not found, too large


@dataclass
class HttpResponse:
    status: int
    body: bytes
    headers: dict[str, str] = field(default_factory=dict)


Transport = Callable[[str, str, dict[str, str], bytes | None, float], HttpResponse]


def urllib_transport(method: str, url: str, headers: dict[str, str], body: bytes | None, timeout: float) -> HttpResponse:
    """The real network transport (stdlib only)."""
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return HttpResponse(resp.status, resp.read(), dict(resp.headers.items()))
    except urllib.error.HTTPError as e:
        return HttpResponse(e.code, e.read() or b"", dict(e.headers.items()) if e.headers else {})


class FatalAPIError(RuntimeError):
    """A response that retrying cannot fix (bad request, auth, no credits). Stops the run.
    `charged` is any cost the API reported on that response."""

    def __init__(self, message: str, charged: float = 0.0):
        super().__init__(message)
        self.charged = charged


def _reported_cost(data: Any) -> float:
    """`usage.cost` from a response body, or 0 when it carries none."""
    if isinstance(data, dict) and isinstance(data.get("usage"), dict):
        cost = data["usage"].get("cost")
        if isinstance(cost, (int, float)) and cost > 0:
            return float(cost)
    return 0.0


class MissingKeyError(RuntimeError):
    pass


@dataclass
class CallResult:
    """One chat-completion call: the raw response (or the last error) and how we got it."""

    response: dict[str, Any] | None
    status: int | None
    attempts: int
    latency_s: float
    error: str | None = None
    errors: list[str] = field(default_factory=list)  # one line per failed attempt
    failed_attempt_costs: list[float] = field(default_factory=list)  # API-reported cost of each failed attempt (0 if none)

    @property
    def ok(self) -> bool:
        return self.response is not None and self.error is None


def _key() -> str:
    key = os.environ.get(KEY_ENV)
    if not key:
        raise MissingKeyError(f"{KEY_ENV} is not set; live calls need it in the environment (never pass it on the command line)")
    return key


def _retryable_body(data: dict[str, Any]) -> str | None:
    """An error carried inside a 200 response (OpenRouter forwards provider failures that way)."""
    if isinstance(data.get("error"), dict):
        return f"error {data['error'].get('code')}: {str(data['error'].get('message'))[:200]}"
    choices = data.get("choices") or []
    if not choices:
        return "response has no choices"
    ch = choices[0]
    if ch.get("finish_reason") == "error" or isinstance(ch.get("error"), dict):
        return f"choice error: {json.dumps(ch.get('error'))[:200]}"
    if not data.get("usage") and not _visible_output(ch):
        # every real response carries usage (see the module docstring); an empty reply without it is a provider
        # failure, not an answer (9 of 284 forced gpt-oss-120b calls on DeepInfra, 2026-11-18)
        return "empty reply without usage"
    return None


def _visible_output(choice: dict[str, Any]) -> bool:
    """Whether a choice carries any output: content, a text completion's text, or reasoning."""
    msg = choice.get("message") or {}
    return any((v or "").strip() for v in (msg.get("content"), msg.get("reasoning"), choice.get("text"), choice.get("reasoning")))


def usable(response: dict[str, Any] | None) -> bool:
    """A stored response that counts as done: present, and not one the client would now retry (an error carried in a
    200, no choices, an empty reply without usage). Resumes and the response cache re-send anything else."""
    return response is not None and _retryable_body(response) is None


class OpenRouterClient:
    def __init__(self, transport: Transport | None = None, *, timeout_s: float = 1800.0, max_attempts: int = 6,
                 backoff_base_s: float = 4.0, backoff_max_s: float = 180.0, sleep: Callable[[float], None] = time.sleep,
                 rng: random.Random | None = None, app_title: str = "reasoning_heuristics evals"):
        self.transport = transport or urllib_transport
        self.timeout_s = timeout_s
        self.max_attempts = max_attempts
        self.backoff_base_s = backoff_base_s
        self.backoff_max_s = backoff_max_s
        self.sleep = sleep
        self.rng = rng or random.Random(0)
        self.app_title = app_title

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {_key()}", "Content-Type": "application/json", "X-Title": self.app_title}

    def _backoff(self, attempt: int, retry_after: str | None) -> float:
        if retry_after:
            try:
                return min(float(retry_after), self.backoff_max_s)
            except ValueError:
                pass
        base = min(self.backoff_base_s * 2 ** (attempt - 1), self.backoff_max_s)
        return base * (0.5 + 0.5 * self.rng.random())

    def chat(self, body: dict[str, Any], on_failed_attempt: Callable[[float], bool] | None = None) -> CallResult:
        """POST /chat/completions with retries. Raises FatalAPIError for unretryable failures.

        A failed attempt can still be charged (e.g. a 200 whose body carries an error after the
        provider generated). Its API-reported `usage.cost` (0 if none) is kept in
        `failed_attempt_costs` and passed to `on_failed_attempt`, which books it and returns whether
        another attempt is allowed (the cost guard says no when a retry could pass the cap).
        """
        return self._post("/chat/completions", body, on_failed_attempt)

    def complete(self, body: dict[str, Any], on_failed_attempt: Callable[[float], bool] | None = None) -> CallResult:
        """POST /completions (raw text completions: `prompt`, not `messages`) with exactly `chat`'s
        retries and cost booking."""
        return self._post("/completions", body, on_failed_attempt)

    def _post(self, path: str, body: dict[str, Any], on_failed_attempt: Callable[[float], bool] | None) -> CallResult:
        """The retry loop behind `chat` and `complete`."""
        payload = json.dumps(body).encode("utf-8")
        errors: list[str] = []
        failed_costs: list[float] = []
        t0 = time.monotonic()
        status = None
        for attempt in range(1, self.max_attempts + 1):
            retry_after = None
            charged = 0.0
            try:
                resp = self.transport("POST", f"{API_BASE}{path}", self._headers(), payload, self.timeout_s)
            except (urllib.error.URLError, http.client.HTTPException, TimeoutError, ConnectionError, OSError) as e:
                # HTTPException covers a body cut short (IncompleteRead) and a dropped connection
                errors.append(f"attempt {attempt}: network {type(e).__name__}: {str(e)[:200]}")
            else:
                status = resp.status
                retry_after = resp.headers.get("Retry-After") or resp.headers.get("retry-after")
                text = resp.body.decode("utf-8", errors="replace")
                data = None
                try:
                    data = json.loads(text) if text.strip() else {}
                except json.JSONDecodeError:
                    pass
                charged = _reported_cost(data)
                if resp.status in FATAL_STATUS:
                    raise FatalAPIError(f"HTTP {resp.status}: {text[:500]}", charged)
                if resp.status == 200:
                    if data is None:
                        errors.append(f"attempt {attempt}: unparseable 200 body ({len(text)} chars)")
                    else:
                        problem = _retryable_body(data)
                        if problem is None:
                            return CallResult(data, 200, attempt, time.monotonic() - t0, None, errors, failed_costs)
                        if isinstance(data.get("error"), dict) and data["error"].get("code") in FATAL_STATUS:
                            raise FatalAPIError(problem, charged)
                        errors.append(f"attempt {attempt}: {problem}")
                elif resp.status in RETRY_STATUS or resp.status >= 500:
                    errors.append(f"attempt {attempt}: HTTP {resp.status}: {text[:200]}")
                else:
                    raise FatalAPIError(f"HTTP {resp.status}: {text[:500]}", charged)
            failed_costs.append(charged)
            allowed = on_failed_attempt(charged) if on_failed_attempt is not None else True
            if not allowed:
                errors.append(f"attempt {attempt}: no retry (the cost guard refused one)")
                break
            if attempt < self.max_attempts:
                self.sleep(self._backoff(attempt, retry_after))
        return CallResult(None, status, len(failed_costs), time.monotonic() - t0, errors[-1] if errors else "failed",
                          errors, failed_costs)

    def get_json(self, path: str) -> dict[str, Any]:
        """GET an API path (model endpoint listings, generation stats). Free; needs the key."""
        resp = self.transport("GET", f"{API_BASE}{path}", self._headers(), None, 60.0)
        if resp.status != 200:
            raise FatalAPIError(f"GET {path}: HTTP {resp.status}: {resp.body[:300]!r}")
        return json.loads(resp.body.decode("utf-8"))

    def endpoints(self, model: str) -> dict[str, Any]:
        """GET /models/{author}/{slug}/endpoints: providers, quantization, prices, limits, parameters."""
        return self.get_json(f"/models/{model}/endpoints")

    def generation(self, generation_id: str) -> dict[str, Any]:
        """GET /generation?id=...: provider_name, native token counts, total_cost."""
        return self.get_json(f"/generation?id={generation_id}")

    def key_usage(self) -> dict[str, Any]:
        """The key's own usage counter (GET /key), as numbers only: never the key, its label or its hash.
        Other users of the same key move it too, so a before/after delta is an upper bound on a run."""
        try:
            data = self.get_json("/key").get("data") or {}
        except (FatalAPIError, OSError, ValueError) as e:
            return {"error": str(e)[:200]}
        return {k: data.get(k) for k in ("usage", "usage_daily", "limit", "limit_remaining") if k in data}
