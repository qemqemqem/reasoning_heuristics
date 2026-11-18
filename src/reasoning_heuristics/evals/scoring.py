"""The one versioned scorer (DESIGN §5 rules 3-5): a model response -> an answer in the members'
representation, a response category, validity and correctness, and the item's outcome class.

No LLM is involved; everything here is deterministic and reads the item's own structured
instance (`instance`, `ground_truth`, `predictions`, `extra.outcome_classes`), never the prompt.

Pipeline for one response
-------------------------
1. **Visible text.** The message `content`, with any inline `<think>...</think>` removed (some
   providers inline the reasoning). The reasoning channel is never parsed for the answer.
2. **Gates.** `truncated` if the provider stopped for length (finish_reason "length", or the
   completion reached `max_tokens`); `refusal` if finish_reason is "content_filter" or the
   message carries a `refusal`. Truncation is censoring (SCOPE §6 rule 2), so it wins even when a
   partial answer happens to parse; the parse is still recorded in `parse_status` / `parsed`.
3. **Parse by answer format.** The last answer block wins: the last line-initial `ANSWER:` marker
   for the `ANSWER:` formats, the last JSON object carrying the format's key for the JSON formats.
   Code fences, markdown emphasis, whitespace and case are tolerated; missing or unknown vertices
   / variables / items are not: a witness with missing elements is `partial`, unknown or
   conflicting elements are `parse_fail`. Nothing is ever filled in.
4. **Categories** (exactly one per response): ok, parse_fail, refusal, declared_impossible,
   partial, truncated (plus `api_error` for a call that never returned a response).
   `declared_impossible` is a give-up ("cannot be determined", "too complex", "unknown",
   "contradictory") or an IMPOSSIBLE / UNSAT where the format offers no such answer. Where the
   format does offer it (k-colouring, SAT, {"possible": false}), IMPOSSIBLE / UNSAT is an
   ordinary answer (category ok): several members predict it.
5. **Decision vs witness channels.** On a decision channel (A/H E1/E2, C E5 entailment, B4/C4
   YES/NO) the scored answer is the decision; a positive claim's witness is checked
   (`valid`) and its problems are flags (`witness_partial`, ...), not a category. On every other
   channel the witness is the answer, so its problems set the category.
6. **Outcome class** (only for category ok): the item's channel (reconstructed with the same
   generator functions that built `extra.outcome_classes`) maps the parsed answer to a class key;
   the record carries the class label as written in `extra.outcome_classes` / `disconfirms`
   ("answer = other" when no deterministic member predicted it).
7. **Correctness** (only for category ok), with the repo's problem code: proper colouring and
   colour count (k, fixed colours, the stated rule's effective graph), the assignment satisfies
   the stated CNF and the fixed values, knapsack feasibility and optimality, the entailment
   answer, the instructed first-fit colour.

Bump SCORER_VERSION on any change in behaviour; every scored record carries it, and the scoring
manifest records the git SHA (DESIGN §5 rule 3). Re-score everything from raw outputs after a
bump (`python -m reasoning_heuristics.evals.score`).
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

from reasoning_heuristics import tokens
from reasoning_heuristics.generators.c_e3 import bit_channel, colour_channel
from reasoning_heuristics.generators.common import Channel, decision_channel, witness_channel
from reasoning_heuristics.heuristics.answers import answer_key
from reasoning_heuristics.heuristics.coloring import effective_graph
from reasoning_heuristics.heuristics.sat import effective_cnf
from reasoning_heuristics.heuristics.tasks import ColouringTask, EntailmentTask, KnapsackTask, SatTask, load_task
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.entailment import formula as F
from reasoning_heuristics.problems.sat import cnf as S

SCORER_VERSION = "scorer-1.3.0"
# 1.1.0: a reply that is nothing but the answer, without the ANSWER: marker, is parsed (flag no_answer_marker).
# 1.1.1: answer_only_in_reasoning is not set on truncated replies (their reasoning often quotes the format).
# 1.2.0: LaTeX answer decoration (\\boxed{..}, \\text{..}, $$ ... $$) is unwrapped before the ANSWER: formats are parsed.
# 1.3.0: C SAT / colouring values given without their names (or with the format's placeholder, `x=T`) are read in
#        the requested order when the count is exact (flags positional_values, placeholder_names).

CATEGORIES = ("ok", "parse_fail", "refusal", "declared_impossible", "partial", "truncated", "api_error")

# --- answer formats -----------------------------------------------------------------------------

JSON_FORMATS = {
    "sat_json": "json_sat",
    "col_json": "json_col",
    "ent_yn_json": "json_ent_yn",
    "ent_open_json": "json_ent_open",
    'JSON {"items": [...]}': "json_knap",
}
JSON_KEYS = {"json_sat": "satisfiable", "json_col": "possible", "json_ent_yn": "follows",
             "json_ent_open": "conclusion", "json_knap": "items"}


class UnsupportedItem(ValueError):
    """An item the runner cannot send as a plain prompt (A/H E8 specs)."""


@dataclass(frozen=True)
class AnswerFormat:
    kind: str
    allow_impossible: bool = False  # IMPOSSIBLE / UNSAT is a legal answer in this format
    target: str | None = None  # the single-vertex format's vertex


def answer_format(item: dict[str, Any]) -> AnswerFormat:
    """The parser for an item's `answer_format` string. Unknown formats raise (fail fast)."""
    fmt = item["answer_format"]
    if fmt in JSON_FORMATS:
        kind = JSON_FORMATS[fmt]
        return AnswerFormat(kind, allow_impossible=kind in ("json_sat", "json_col"))
    if fmt.startswith("sat_json (forced"):
        raise UnsupportedItem(f"{item['item_id']}: an E8 spec; it needs the model's earlier response (ah_e8.materialise)")
    if fmt.startswith("After the line ANSWER:"):
        m = re.search(r"only the colour number of (\S+)$", fmt)
        if m:
            return AnswerFormat("ans_single_colour", target=m.group(1))
        if "`vertex: colour`" in fmt:
            return AnswerFormat("ans_col", allow_impossible="IMPOSSIBLE or" in fmt)
        if "UNSAT or `x=T`" in fmt:
            return AnswerFormat("ans_sat", allow_impossible=True)
        if "letters of the chosen items" in fmt:
            return AnswerFormat("ans_knap")
        if fmt.endswith("YES or NO"):
            return AnswerFormat("ans_yn")
    if fmt == 'final line "ANSWER: YES" or "ANSWER: NO"':
        return AnswerFormat("ans_yn")
    if fmt == 'final line "ANSWER: <letter>"':
        return AnswerFormat("ans_letter")
    raise ValueError(f"{item['item_id']}: unknown answer format {fmt!r}")


# --- the response as the scorer sees it ---------------------------------------------------------


@dataclass
class ResponseView:
    """The fields the scorer reads, always re-derived from the stored raw API response."""

    content: str | None
    reasoning: str | None
    finish_reason: str | None
    native_finish_reason: str | None = None
    refusal: str | None = None
    completion_tokens: int | None = None
    reasoning_tokens: int | None = None
    prompt_tokens: int | None = None
    cost: float | None = None
    model: str | None = None
    provider: str | None = None
    generation_id: str | None = None
    max_tokens: int | None = None
    error: str | None = None

    @classmethod
    def from_api(cls, response: dict[str, Any] | None, max_tokens: int | None = None, error: str | None = None) -> "ResponseView":
        if response is None:
            return cls(None, None, None, max_tokens=max_tokens, error=error or "no response")
        choice = (response.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        usage = response.get("usage") or {}
        details = usage.get("completion_tokens_details") or {}
        reasoning = msg.get("reasoning")
        if not reasoning and msg.get("reasoning_details"):
            reasoning = "".join(d.get("text") or d.get("summary") or "" for d in msg["reasoning_details"] if isinstance(d, dict)) or None
        content = msg.get("content")
        if isinstance(content, list):  # content parts
            content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
        choice_error = choice.get("error")
        if error is None and isinstance(choice_error, dict):
            error = choice_error.get("message") or json.dumps(choice_error)
        if error is None and choice.get("finish_reason") == "error":
            error = "finish_reason error"
        return cls(
            content=content,
            reasoning=reasoning,
            finish_reason=choice.get("finish_reason"),
            native_finish_reason=choice.get("native_finish_reason"),
            refusal=msg.get("refusal"),
            completion_tokens=usage.get("completion_tokens"),
            reasoning_tokens=details.get("reasoning_tokens"),
            prompt_tokens=usage.get("prompt_tokens"),
            cost=usage.get("cost"),
            model=response.get("model"),
            provider=served_provider(response),
            generation_id=response.get("id"),
            max_tokens=max_tokens,
            error=error,
        )


def served_provider(response: dict[str, Any]) -> str | None:
    """The provider that served a response: the top-level `provider` field, else the selected
    endpoint in `openrouter_metadata`."""
    if response.get("provider"):
        return response["provider"]
    meta = response.get("openrouter_metadata") or {}
    for ep in meta.get("endpoints") or []:
        if isinstance(ep, dict) and ep.get("selected"):
            return ep.get("provider")
    return None


_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.S | re.I)


def visible_text(content: str | None) -> tuple[str, list[str]]:
    """The content with inline reasoning removed, and flags saying what was removed."""
    if not content:
        return "", []
    flags: list[str] = []
    text = content
    if re.search(r"<think>", text, re.I):
        flags.append("think_in_content")
        text = _THINK_BLOCK.sub("", text)
        if re.search(r"<think>", text, re.I):  # unclosed: the rest is reasoning
            flags.append("unclosed_think_in_content")
            text = re.split(r"<think>", text, flags=re.I)[0]
    if re.search(r"</think>", text, re.I):  # closing tag only: the template opened it in the prompt
        flags.append("think_close_in_content")
        text = re.split(r"</think>", text, flags=re.I)[-1]
    return text, flags


# --- phrase lists (deterministic, versioned with the scorer) -------------------------------------

_GIVEUP = re.compile(
    r"\b(cannot be (?:determined|solved|decided|answered)|can(?:no|')t (?:be )?(?:determined?|decided?|solved?|tell|say)"
    r"|unable to (?:determine|solve|decide|answer)|undetermin(?:ed|able)|indeterminate|undecidable|unknown"
    r"|too (?:complex|hard|large|difficult|long)|not enough information|insufficient information"
    r"|contradictory|inconsistent|neither)\b", re.I)
_NEGATIVE = re.compile(r"\b(impossible|unsat(?:isfiable)?|uncolou?rable|not (?:possible|colou?rable|satisfiable)"
                       r"|no (?:valid |possible |such |proper )?(?:solution|colou?ring|assignment))\b", re.I)
_REFUSAL = re.compile(
    r"(I(?:'m| am) sorry,? but I (?:can(?:no|')t|won't|am unable|will not)|I can(?:no|')t (?:help|assist|comply|do that|provide|answer)"
    r"|I(?:'m| am) (?:not able|unable) to (?:help|assist|comply|provide)|I won't (?:help|assist|provide)|cannot comply"
    r"|against (?:my|the) (?:policy|policies|guidelines))", re.I)

# Line-initial ANSWER markers ("ANSWER:", "**ANSWER:**", "### Final answer:", "ANSWER" alone on a line);
# an inline "ANSWER:" (upper case) only counts when no line-initial marker exists.
_MARK_LINE = re.compile(r"(?im)^[ \t>*_#`~|-]*(?:final[ \t]+)?answer[ \t*_`]*[:：]")
_MARK_HEAD = re.compile(r"(?im)^[ \t>*_#`~|-]*(?:final[ \t]+)?answer[ \t*_`]*$")
_MARK_INLINE = re.compile(r"ANSWER[ \t*_`]*[:：]")


def answer_markers(text: str) -> tuple[list[tuple[int, int]], bool]:
    """(start, end) of every answer marker in order, and whether they are inline-only."""
    marks = sorted({(m.start(), m.end()) for rx in (_MARK_LINE, _MARK_HEAD) for m in rx.finditer(text)})
    if marks:
        return marks, False
    return [(m.start(), m.end()) for m in _MARK_INLINE.finditer(text)], True


def clean_block(text: str) -> str:
    """An answer block with fence lines, markdown emphasis and backticks removed."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if re.fullmatch(r"(`{3,}|~{3,})[\w+-]*", s):
            continue
        s = s.replace("**", "").replace("__", "").replace("`", "").strip()
        s = re.sub(r"^(?:[-*•>]|\d+[.)])\s+", "", s)  # list bullets / numbering
        out.append(s)
    return "\n".join(out).strip()


def json_objects(text: str) -> list[tuple[int, int, dict[str, Any]]]:
    """Every JSON object that parses at some '{' (outermost first), as (start, end, value)."""
    dec = json.JSONDecoder()
    out = []
    i = text.find("{")
    while i != -1:
        try:
            val, end = dec.raw_decode(text, i)
        except json.JSONDecodeError:
            i = text.find("{", i + 1)
            continue
        if isinstance(val, dict):
            out.append((i, end, val))
            i = text.find("{", end)
        else:
            i = text.find("{", i + 1)
    return out


_LOOSE_OBJ = re.compile(r"\{(?:[^{}]|\{[^{}]*\})*\}")


def loose_objects(text: str) -> list[tuple[int, int, dict[str, Any]]]:
    """Python-literal style objects ({'follows': True}), tried only when no JSON object fits."""
    out = []
    for m in _LOOSE_OBJ.finditer(text):
        src = re.sub(r"\btrue\b", "True", re.sub(r"\bfalse\b", "False", re.sub(r"\bnull\b", "None", m.group(0))))
        try:
            val = ast.literal_eval(src)
        except (ValueError, SyntaxError, MemoryError, RecursionError):
            continue
        if isinstance(val, dict):
            out.append((m.start(), m.end(), val))
    return out


def _norm_key(k: Any) -> str:
    return re.sub(r"[\s_-]", "", str(k)).lower()


def _get(obj: dict[str, Any], *names: str) -> tuple[Any, bool, str | None]:
    """Case- and separator-insensitive key lookup: (value, found, the key actually used)."""
    want = {_norm_key(n): n for n in names}
    for k, v in obj.items():
        if _norm_key(k) in want:
            return v, True, k
    return None, False, None


def _as_bool(v: Any, flags: list[str]) -> bool | None:
    if isinstance(v, bool):
        return v
    if isinstance(v, str) and v.strip().lower() in ("true", "yes"):
        flags.append("boolean_as_string")
        return True
    if isinstance(v, str) and v.strip().lower() in ("false", "no"):
        flags.append("boolean_as_string")
        return False
    if isinstance(v, int) and v in (0, 1):
        flags.append("boolean_as_number")
        return bool(v)
    return None


# --- parse results ----------------------------------------------------------------------------------


@dataclass
class Parse:
    status: str  # ok | parse_fail | partial | declared_impossible
    answer: Any = None  # the members' representation (status ok)
    detail: str = ""
    flags: list[str] = field(default_factory=list)
    answer_start: int | None = None  # offset in the visible text where the final answer block starts
    n_blocks: int = 0
    witness: str | None = None  # decision channels: complete | partial | malformed | missing | None


class ItemContext:
    """Everything the scorer derives from one item, computed once."""

    def __init__(self, item: dict[str, Any]):
        self.item = item
        self.fmt = answer_format(item)
        self.task = load_task(item["instance"])
        self.domain = self.task.domain
        self.channel_name = item["extra"].get("channel")
        self.channel = channel_for(item, self.domain)
        self.decision = self.channel_name == "decision"

    @cached_property
    def names(self) -> list[str]:
        t = self.task
        if isinstance(t, ColouringTask):
            return list(t.graph.vertices)
        if isinstance(t, SatTask):
            return list(t.cnf.var_names)
        if isinstance(t, KnapsackTask):
            return list(t.knapsack.names)
        return []

    @cached_property
    def name_map(self) -> dict[str, str]:
        return {n.lower(): n for n in self.names}

    @cached_property
    def name_pattern(self) -> str:
        """A regex for the instance's naming scheme: `v\\d+` style labels, else the literal names."""
        ms = [re.fullmatch(r"([A-Za-z]+)(\d+)", n) for n in self.names]
        if ms and all(ms) and len({m.group(1).lower() for m in ms}) == 1:
            return rf"{re.escape(ms[0].group(1))}\d+"
        return "|".join(re.escape(n) for n in sorted(self.names, key=len, reverse=True))

    @cached_property
    def open_vocabulary(self) -> dict[str, str]:
        """Normalised fact text -> canonical literal, for the ent_open format."""
        out: dict[str, str] = {}
        for a in F.atoms_of(self.task.premises):
            for pol in (True, False):
                canon = F.render_lit(a, pol)
                for variant in _fact_variants(canon):
                    out.setdefault(variant, canon)
        return out

    @cached_property
    def letters(self) -> list[str]:
        return [chr(ord("A") + i) for i in range(len(self.task.options) + 1)]


def channel_for(item: dict[str, Any], domain: str) -> Channel:
    """The item's scoring channel, rebuilt with the generator functions that produced its outcome classes."""
    name = item["extra"].get("channel")
    if name == "decision":
        pos, neg = {"sat": ("SAT", "UNSAT"), "coloring": ("POSSIBLE", "IMPOSSIBLE"), "entailment": ("YES", "NO")}[domain]
        return decision_channel(pos, neg)
    if name == "answer":
        return witness_channel(domain)
    if name == "target-bit":
        return bit_channel(item["params"]["target"], item["params"]["reference_vertex"])
    if name == "target-colour":
        return colour_channel(item["params"]["target"])
    raise ValueError(f"{item['item_id']}: unknown channel {name!r}")


def _fact_norm(s: str) -> str:
    s = s.strip().strip("\"'“”‘’").strip()
    s = re.sub(r"[.;,!]+$", "", s).strip()
    s = s.lower().replace("’", "'")
    s = re.sub(r"\bisn't\b", "is not", s)
    s = re.sub(r"\s+", " ", s)
    return s


def _fact_variants(canon: str) -> list[str]:
    s = _fact_norm(canon)
    return [s, s[4:]] if s.startswith("the ") else [s]


# --- the parsers ------------------------------------------------------------------------------------


_LATEX_WRAP = re.compile(r"\\(?:boxed|text|textbf|textit|texttt|mathrm|mathbf|mathtt)\s*\{([^{}]*)\}")


def unlatex(text: str) -> str:
    """Unwrap LaTeX answer decoration (seen live: `$$\\text{ANSWER: C}$$`, `$$\\boxed{C}$$`): wrappers such
    as \\boxed{..} and \\text{..} are replaced by their contents, and math delimiters by line breaks."""
    prev = None
    while prev != text:  # nested: \boxed{\text{C}}
        prev, text = text, _LATEX_WRAP.sub(r"\1", text)
    text = re.sub(r"\$\$|\\\[|\\\]|\\\(|\\\)", "\n", text)
    return re.sub(r"(?<!\\)\$", "", text)


def parse(ctx: ItemContext, text: str) -> Parse | None:
    """Parse the visible text by the item's format. None means no answer block was found."""
    if ctx.fmt.kind.startswith("json_"):
        return _parse_json(ctx, text)
    marks, inline = answer_markers(text)
    if not marks:
        return _bare_answer(ctx, text)
    results = []
    for i, (start, end) in enumerate(marks):
        stop = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        block = clean_block(text[end:stop]) if i + 1 < len(marks) else clean_block(text[end:])
        results.append(_parse_block(ctx, block))
    final = results[-1]
    final.answer_start = marks[-1][0]
    final.n_blocks = len(marks)
    if inline:
        final.flags.append("inline_answer_marker")
    if len({json.dumps(r.answer, sort_keys=True, default=str) for r in results if r.status == "ok"}) > 1:
        final.flags.append("answer_blocks_disagree")
    return final


def _first_line(block: str) -> str:
    return next((ln for ln in block.splitlines() if ln.strip()), "")


def _bare_answer(ctx: ItemContext, text: str) -> Parse | None:
    """No ANSWER marker at all: accept the visible text only if it is nothing but an answer in the
    format (the direct condition's "respond with only the final answer" often drops the marker).
    Any other text means no answer block. Flagged `no_answer_marker`."""
    block = clean_block(text)
    lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
    if not lines:
        return None
    kind = ctx.fmt.kind
    one = lines[0].rstrip(".")
    if kind == "ans_yn":
        pure = len(lines) == 1 and re.fullmatch(r"(?i)yes|no", one)
    elif kind == "ans_letter":
        pure = len(lines) == 1 and re.fullmatch(r"\(?[A-Za-z]\)?", one)
    elif kind == "ans_single_colour":
        pure = len(lines) == 1 and re.fullmatch(rf"(?i)(?:{re.escape(ctx.fmt.target)}\s*[:=]\s*)?-?\d+", one)
    elif kind == "ans_knap":
        pure = len(lines) == 1 and re.fullmatch(rf"(?i)(?:none|(?:(?:{ctx.name_pattern})(?:\s*[,;]\s*|\s+|$))+)", one)
    elif kind in ("ans_col", "ans_sat"):
        word, ph, value = ("IMPOSSIBLE", "vertex", r"-?\d+") if kind == "ans_col" else ("UNSAT", "x", r"(?:TRUE|FALSE|T|F|1|0)")
        pure = (len(lines) == 1 and one.upper() == word) or all(
            re.fullmatch(rf"(?i)(?:(?:{ctx.name_pattern})\s*[:=]\s*\S+?\s*[,;]?\s*)+", ln) for ln in lines) or all(
            re.fullmatch(rf"(?i)(?:(?:{ph}\s*[:=]\s*)?{value}(?:\s*[,;]\s*|\s+|$))+", ln.rstrip(".")) for ln in lines)
    else:
        pure = False
    if not pure:
        return None
    res = _parse_block(ctx, block)
    res.flags.append("no_answer_marker")
    res.answer_start, res.n_blocks = 0, 1
    return res


def _declared_or_fail(ctx: ItemContext, snippet: str, what: str) -> Parse:
    if _GIVEUP.search(snippet) or (_NEGATIVE.search(snippet) and not ctx.fmt.allow_impossible):
        return Parse("declared_impossible", detail=snippet[:200])
    return Parse("parse_fail", detail=f"{what}: {snippet[:200]!r}")


def _parse_block(ctx: ItemContext, block: str) -> Parse:
    kind = ctx.fmt.kind
    first = _first_line(block)
    if kind == "ans_yn":
        m = re.match(r"^[\W_]*([A-Za-z]+)", first)
        word = m.group(1).upper() if m else ""
        if word in ("YES", "NO"):
            return Parse("ok", word)
        return _declared_or_fail(ctx, first, "not YES or NO")
    if kind == "ans_letter":
        m = re.match(r"^[\W_]*\(?([A-Za-z])\)?(?![A-Za-z])", first)
        if m and m.group(1).upper() in ctx.letters:
            return Parse("ok", m.group(1).upper())
        if re.match(r"^[\W_]*none of (?:these|the above)", first, re.I):
            return Parse("ok", ctx.letters[-1], flags=["none_of_these_as_text"])
        if m:
            return Parse("parse_fail", detail=f"letter {m.group(1)!r} is not an option ({''.join(ctx.letters)})")
        return _declared_or_fail(ctx, first, "no option letter")
    if kind == "ans_single_colour":
        target = ctx.fmt.target
        rest = re.sub(rf"(?<![\w]){re.escape(target)}(?![\w])", " ", first, flags=re.I)
        nums = re.findall(r"(?<![\w.])(-?\d+)(?!\w)(?!\.\d)", rest)  # "2" and "2." but not "1.5"
        if not nums:
            return _declared_or_fail(ctx, first, "no colour number")
        flags = ["several_numbers"] if len(set(nums)) > 1 else []
        return Parse("ok", {target: int(nums[0])}, flags=flags)
    if kind == "ans_col":
        return _parse_pairs(ctx, block, value_rx=r"-?\d+", convert=int, negative_word="IMPOSSIBLE", what="vertex")
    if kind == "ans_sat":
        return _parse_pairs(ctx, block, value_rx=r"(?:TRUE|FALSE|T|F|1|0)",
                            convert=lambda s: s.upper() in ("T", "TRUE", "1"), negative_word="UNSAT", what="variable")
    if kind == "ans_knap":
        return _parse_knap_line(ctx, first)
    raise AssertionError(kind)


def _parse_pairs(ctx: ItemContext, block: str, value_rx: str, convert, negative_word: str, what: str) -> Parse:
    first = _first_line(block)
    head = re.sub(r"[^A-Za-z ]", " ", first).strip().upper()
    if head.startswith(negative_word):
        if ctx.fmt.allow_impossible:
            return Parse("ok", negative_word)
        return Parse("declared_impossible", detail=first[:200])
    pair = re.compile(rf"(?<![\w])({ctx.name_pattern})\s*(?:[:=]|->|→|is|gets)\s*({value_rx})(?!\w)(?!\.\d)", re.I)
    pairs: list[tuple[str, str]] = []
    extra_lines = 0
    for line in block.splitlines():
        found = pair.findall(line)
        if found:
            pairs += found
        elif line.strip():
            extra_lines += 1
    if not pairs:
        if _NEGATIVE.search(first) and ctx.fmt.allow_impossible:
            return Parse("ok", negative_word, flags=[f"{negative_word.lower()}_as_phrase"])
        positional = _positional(ctx, block, value_rx, convert, what)
        if positional is not None:
            return positional
        return _declared_or_fail(ctx, first, f"no `{what}: value` pairs")
    flags = ["extra_text_in_block"] if extra_lines else []
    values: dict[str, Any] = {}
    unknown = []
    for raw_name, raw_val in pairs:
        name = ctx.name_map.get(raw_name.lower())
        if name is None:
            unknown.append(raw_name)
            continue
        val = convert(raw_val)
        if name in values and values[name] != val:
            return Parse("parse_fail", detail=f"{what} {name} given two values ({values[name]!r}, {val!r})")
        if name in values:
            flags.append("repeated_" + what)
        values[name] = val
    if unknown:
        return Parse("parse_fail", detail=f"unknown {what}(s): {', '.join(sorted(set(unknown))[:10])}")
    order = list(ctx.task.answer_order) if getattr(ctx.task, "answer_order", None) else None
    if order and [n for n in (ctx.name_map[p[0].lower()] for p in pairs)] != order:
        flags.append("order_differs_from_requested")
    return _complete_or_partial(ctx, values, flags, what)


PLACEHOLDER = {"variable": "x", "vertex": "vertex"}  # the generic names in the C formats' `x=T` / `vertex: colour`


def _positional(ctx: ItemContext, block: str, value_rx: str, convert, what: str) -> Parse | None:
    """Values without their names, in the requested order (seen live: "ANSWER: T, T, F, ..." and the
    format's own placeholder taken literally, "ANSWER: x=T, x=T, x=F, ..."). Read positionally only when
    the item states an answer order and the block holds exactly one value per name; otherwise None."""
    order = list(ctx.task.answer_order) if getattr(ctx.task, "answer_order", None) else None
    if not order:
        return None
    ph = PLACEHOLDER[what]
    item = rf"(?:{ph}\s*[:=]\s*)?({value_rx})"
    line_rx = re.compile(rf"(?i)^(?:{item}(?:\s*[,;]\s*|\s+|$))+$")
    lines = [ln.strip().rstrip(".") for ln in block.splitlines() if ln.strip()]
    if not lines or not all(line_rx.match(ln) for ln in lines):
        return None
    vals = [m.group(1) for ln in lines for m in re.finditer(rf"(?i)(?<![\w]){item}(?![\w])", ln)]
    if len(vals) != len(order):
        return Parse("parse_fail", detail=f"{len(vals)} values without names for {len(order)} {what}s")
    flags = ["positional_values"] + (["placeholder_names"] if re.search(rf"(?i)\b{ph}\s*[:=]", block) else [])
    return _complete_or_partial(ctx, {n: convert(v) for n, v in zip(order, vals)}, flags, what)


def _complete_or_partial(ctx: ItemContext, values: dict[str, Any], flags: list[str], what: str) -> Parse:
    missing = [n for n in ctx.names if n not in values]
    if missing:
        fixed = {v for v, _ in getattr(ctx.task, "fixed", ())}
        if fixed and set(missing) <= fixed:
            flags.append("missing_only_fixed")
        return Parse("partial", detail=f"missing {len(missing)} {what}(s): {', '.join(missing[:10])}", flags=flags)
    return Parse("ok", {n: values[n] for n in ctx.names}, flags=flags)


def _parse_knap_line(ctx: ItemContext, line: str) -> Parse:
    stripped = line.strip(" .*_`")
    if re.fullmatch(r"(?i)(none|nothing|no items|\(none\)|∅|-|—|\{\}|\[\])", stripped):
        return Parse("ok", [], flags=["empty_selection"])
    single = all(len(n) == 1 for n in ctx.names)
    if single:
        found = re.findall(r"(?<![A-Za-z])([A-Za-z])(?![A-Za-z])", line)
    else:
        found = re.findall(rf"(?<![\w])({ctx.name_pattern})(?![\w])", line, flags=re.I)
    if not found:
        return _declared_or_fail(ctx, line, "no item names")
    res = _items_answer(ctx, found)
    if res.status == "ok" and [ctx.name_map[f.lower()] for f in found] != sorted(res.answer):
        res.flags.append("order_differs_from_requested")  # the C format asks for alphabetical order
    return res


def _items_answer(ctx: ItemContext, names: list[str], flags: list[str] | None = None) -> Parse:
    flags = list(flags or [])
    chosen, unknown = [], []
    for raw in names:
        n = ctx.name_map.get(str(raw).strip().lower())
        (unknown if n is None else chosen).append(raw if n is None else n)
    if unknown:
        return Parse("parse_fail", detail=f"unknown item(s): {', '.join(map(str, unknown[:10]))}")
    if len(set(chosen)) != len(chosen):
        flags.append("repeated_item")
    return Parse("ok", sorted(set(chosen)), flags=flags)


def _parse_json(ctx: ItemContext, text: str) -> Parse | None:
    key = JSON_KEYS[ctx.fmt.kind]
    objs = [o for o in json_objects(text) if _get(o[2], key)[1]]
    flags: list[str] = []
    if not objs:
        objs = [o for o in loose_objects(text) if _get(o[2], key)[1]]
        if objs:
            flags.append("loose_json")
    if not objs:
        return None
    start, end, obj = objs[-1]
    tail = re.sub(r"[`~\s]", "", text[end:])
    if tail:
        flags.append("text_after_answer")
    res = _interpret_json(ctx, obj, flags)
    res.answer_start = start
    res.n_blocks = len(objs)
    if len({json.dumps(o[2], sort_keys=True, default=str) for o in objs}) > 1:
        res.flags.append("answer_blocks_disagree")
    return res


def _interpret_json(ctx: ItemContext, obj: dict[str, Any], flags: list[str]) -> Parse:
    kind = ctx.fmt.kind
    key = JSON_KEYS[kind]
    value, _, _ = _get(obj, key)
    if kind in ("json_sat", "json_col", "json_ent_yn"):
        b = _as_bool(value, flags)
        if b is None:
            return _declared_or_fail(ctx, str(value), f"{key!r} is not a boolean")
        if kind == "json_ent_yn":
            return Parse("ok", "YES" if b else "NO", flags=flags)
        positive, negative = ("SAT", "UNSAT") if kind == "json_sat" else ("POSSIBLE", "IMPOSSIBLE")
        wkey = ("assignment",) if kind == "json_sat" else ("rooms", "colouring", "coloring", "assignment")
        witness, has_w, used = _get(obj, *wkey)
        if used is not None and _norm_key(used) != _norm_key(wkey[0]):
            flags.append(f"witness_key_{used}")
        if not b:
            if witness not in (None, "", [], {}):
                flags.append("witness_given_with_negative_answer")
            return Parse("ok", negative, flags=flags)
        values, status, detail = (_sat_witness if kind == "json_sat" else _col_witness)(ctx, witness, flags)
        if ctx.decision:
            if status != "complete":
                flags.append(f"witness_{status}")
            return Parse("ok", values if status == "complete" else positive, detail=detail, flags=flags, witness=status)
        if status == "complete":
            return Parse("ok", values, flags=flags)
        return Parse("partial" if status in ("partial", "missing") else "parse_fail", detail=detail, flags=flags)
    if kind == "json_ent_open":
        if isinstance(value, str):
            if _fact_norm(value) in ("nothing", "none", "nothing follows"):
                return Parse("ok", "NOTHING", flags=flags)
            if re.search(r"\b(contradictory|inconsistent|contradiction)\b", value, re.I):
                # the members' "X" (no state satisfies the facts); the format has no other way to say it
                return Parse("ok", "X", flags=flags + ["contradiction_as_X"])
            flags.append("single_fact_as_string")
            value = [value]
        if not isinstance(value, list):
            return Parse("parse_fail", detail=f"conclusion is {type(value).__name__}", flags=flags)
        if not value:
            flags.append("empty_list_as_nothing")
            return Parse("ok", "NOTHING", flags=flags)
        facts, unknown = [], []
        for v in value:
            canon = ctx.open_vocabulary.get(_fact_norm(str(v)))
            (unknown if canon is None else facts).append(str(v) if canon is None else canon)
        if unknown:
            return Parse("parse_fail", detail=f"unrecognised fact(s): {unknown[:5]}", flags=flags)
        if len(set(facts)) != len(facts):
            flags.append("repeated_fact")
        return Parse("ok", sorted(set(facts)), flags=flags)
    if kind == "json_knap":
        if isinstance(value, str):
            flags.append("items_as_string")
            value = [v for v in re.split(r"[\s,;]+", value) if v]
        if not isinstance(value, list):
            return Parse("parse_fail", detail=f"items is {type(value).__name__}", flags=flags)
        if not value:
            flags.append("empty_selection")
            return Parse("ok", [], flags=flags)
        return _items_answer(ctx, [str(v) for v in value], flags)
    raise AssertionError(kind)


def _sat_witness(ctx: ItemContext, a: Any, flags: list[str]) -> tuple[dict[str, bool] | None, str, str]:
    names = ctx.names
    if a is None or a == "":
        return None, "missing", "no assignment"
    if isinstance(a, list) and all(x in (0, 1, True, False, "0", "1") for x in a):
        flags.append("assignment_as_list")
        a = "".join("1" if x in (1, True, "1") else "0" for x in a)
    if isinstance(a, str):
        digits = re.sub(r"[\s,;|]", "", a)
        if re.fullmatch(r"[01]+", digits):
            if len(digits) == len(names):
                return {n: d == "1" for n, d in zip(names, digits)}, "complete", ""
            status = "partial" if len(digits) < len(names) else "malformed"
            return None, status, f"{len(digits)} digits for {len(names)} variables"
        pairs = re.findall(rf"(?<![\w])({ctx.name_pattern})\s*[:=]\s*(TRUE|FALSE|T|F|1|0)(?![\w])", a, flags=re.I)
        if pairs:
            flags.append("assignment_as_pairs")
            return _named_values(ctx, [(n, v.upper() in ("1", "T", "TRUE")) for n, v in pairs])
        return None, "malformed", f"assignment {a[:60]!r} is not a digit string"
    if isinstance(a, dict):
        flags.append("assignment_as_object")
        vals = []
        for k, v in a.items():
            b = _as_bool(v, flags) if not isinstance(v, str) or v.upper() not in ("T", "F") else v.upper() == "T"
            if b is None:
                return None, "malformed", f"value {v!r} for {k}"
            vals.append((str(k), b))
        return _named_values(ctx, vals)
    return None, "malformed", f"assignment is {type(a).__name__}"


def _col_witness(ctx: ItemContext, rooms: Any, flags: list[str]) -> tuple[dict[str, int] | None, str, str]:
    if rooms is None or rooms == {}:
        return None, "missing", "no rooms"
    if not isinstance(rooms, dict):
        return None, "malformed", f"rooms is {type(rooms).__name__}"
    vals = []
    for k, v in rooms.items():
        if isinstance(v, bool):
            return None, "malformed", f"room {v!r} for {k}"
        if isinstance(v, str) and re.fullmatch(r"\s*-?\d+\s*", v):
            flags.append("room_as_string")
            v = int(v)
        if isinstance(v, float) and v.is_integer():
            v = int(v)
        if not isinstance(v, int):
            return None, "malformed", f"room {v!r} for {k}"
        vals.append((str(k), v))
    return _named_values(ctx, vals)


def _named_values(ctx: ItemContext, pairs: list[tuple[str, Any]]) -> tuple[dict[str, Any] | None, str, str]:
    out: dict[str, Any] = {}
    unknown = []
    for raw, v in pairs:
        n = ctx.name_map.get(raw.strip().lower())
        if n is None:
            unknown.append(raw)
            continue
        if n in out and out[n] != v:
            return None, "malformed", f"{n} given two values"
        out[n] = v
    if unknown:
        return None, "malformed", f"unknown name(s): {', '.join(unknown[:10])}"
    missing = [n for n in ctx.names if n not in out]
    if missing:
        return None, "partial", f"missing {len(missing)}: {', '.join(missing[:10])}"
    return {n: out[n] for n in ctx.names}, "complete", ""


# --- validity and correctness ---------------------------------------------------------------------


def judge(ctx: ItemContext, ans: Any) -> tuple[bool | None, bool | None, bool | None]:
    """(correct, valid, optimal) of a parsed answer against the item's ground truth."""
    t, gt = ctx.task, ctx.item["ground_truth"]
    if isinstance(t, ColouringTask):
        if ans == "IMPOSSIBLE":
            return gt.get("colourable") is False, None, None
        if ans == "POSSIBLE":
            return gt.get("colourable") is True, None, None
        if ctx.fmt.kind == "ans_single_colour":
            return ans[ctx.fmt.target] == gt["answer"], None, None
        g = effective_graph(t)
        in_range = all(isinstance(c, int) and c >= 1 and (t.k is None or c <= t.k) for c in ans.values())
        fixed_ok = all(ans.get(v) == c for v, c in t.fixed)
        valid = in_range and fixed_ok and G.is_proper(g, ans)
        if ctx.decision:
            return gt["colourable"] is True, valid, None
        if t.k is None:
            optimal = valid and G.n_colours(ans) == gt["chromatic_number"]
            return optimal, valid, optimal
        return valid, valid, None
    if isinstance(t, SatTask):
        if ans == "UNSAT":
            return gt["satisfiable"] is False, None, None
        if ans == "SAT":
            return gt["satisfiable"] is True, None, None
        fixed_ok = all(ans.get(v) == b for v, b in t.fixed)
        valid = fixed_ok and S.satisfies(effective_cnf(t), ans)
        if ctx.decision:
            return gt["satisfiable"] is True, valid, None
        return valid, valid, None
    if isinstance(t, KnapsackTask):
        kn = t.knapsack
        valid = kn.feasible(ans, covering=t.covering)
        optimal = valid and kn.value_of(ans) == gt["optimum"]
        return optimal, valid, optimal
    if isinstance(t, EntailmentTask):
        want = gt["answer"]
        if isinstance(want, list):
            want = sorted(want)
        return ans == want, None, None
    raise TypeError(type(t))


# --- the scored record ----------------------------------------------------------------------------------


def _set_valued(rec: dict[str, Any]) -> bool:
    return bool((rec.get("trace_features") or {}).get("set_valued"))


def outcome(ctx: ItemContext, ans: Any) -> tuple[str | None, str, list[str], list[str]]:
    """(channel value, outcome-class label, members matching on the channel, members with the same answer key)."""
    classes = ctx.item["extra"]["outcome_classes"]
    by_key = {v: k for k, v in classes.items()}
    other = by_key.get("_other", "answer = other")
    value = ctx.channel.key(ans) if ans is not None else None
    label = by_key.get(value, other) if value is not None else other
    mine = answer_key(ctx.domain, ans)
    on_channel, same_key = [], []
    for lbl, rec in ctx.item["predictions"].items():
        if rec.get("answer") is None or _set_valued(rec):
            continue
        try:
            if value is not None and ctx.channel.key(rec["answer"]) == value:
                on_channel.append(lbl)
        except (KeyError, TypeError):  # a member answer the channel cannot read (e.g. a string on a bit channel)
            pass
        if mine is not None and answer_key(ctx.domain, rec["answer"]) == mine:
            same_key.append(lbl)
    return value, label, on_channel, same_key


def score_response(item: dict[str, Any], view: ResponseView, ctx: ItemContext | None = None) -> dict[str, Any]:
    """Score one response to one item. Returns the per-response record (see docs/RUNNER.md)."""
    ctx = ctx or ItemContext(item)
    text, flags = visible_text(view.content)
    if not ctx.fmt.kind.startswith("json_"):
        plain = unlatex(text)
        if plain != text:
            text = plain
            flags.append("latex_unwrapped")
    truncated = view.finish_reason == "length" or view.native_finish_reason in ("length", "max_tokens", "MAX_TOKENS") or (
        view.max_tokens is not None and view.completion_tokens is not None and view.completion_tokens >= view.max_tokens)
    rec: dict[str, Any] = {
        "scorer_version": SCORER_VERSION,
        "item_id": item["item_id"], "content_hash": item["content_hash"], "presentation_hash": item["presentation_hash"],
        "base_hash": item["base_hash"], "source_hash": item.get("source_hash"), "set_id": item["set_id"],
        "pair_id": item.get("pair_id"), "vertical": item["vertical"], "eval_id": item["eval_id"], "cell": item["cell"],
        "domain": ctx.domain, "item_domain": item["domain"], "answer_format": item["answer_format"], "channel": ctx.channel_name,
        "model": view.model, "provider": view.provider, "generation_id": view.generation_id,
        "finish_reason": view.finish_reason, "native_finish_reason": view.native_finish_reason, "truncated": bool(truncated),
        "prompt_tokens": view.prompt_tokens, "completion_tokens": view.completion_tokens, "reasoning_tokens": view.reasoning_tokens,
        "cost_usd": view.cost, "reasoning_returned": bool(view.reasoning), "reasoning_chars": len(view.reasoning or ""),
        "content_chars": len(view.content or ""),
    }
    result: Parse | None = None
    if view.error is not None:
        category = "api_error"
        detail = view.error
    else:
        result = parse(ctx, text)
        if result is None:
            tail = text[-600:]
            if not text.strip():
                result = Parse("parse_fail", detail="empty content")
                # only for a finished reply: a reasoning trace cut at the cap often just quotes the
                # prompt's answer format, which is not an answer
                if not truncated and view.reasoning and parse(ctx, visible_text(view.reasoning)[0]) is not None:
                    result.flags.append("answer_only_in_reasoning")
            elif _GIVEUP.search(tail):
                result = Parse("declared_impossible", detail="no answer block; " + _GIVEUP.search(tail).group(0))
            else:
                result = Parse("parse_fail", detail="no answer block")
        category, detail = result.status, result.detail
        if truncated:
            category = "truncated"
        elif view.finish_reason == "content_filter" or view.refusal:
            category = "refusal"
            detail = view.refusal or "finish_reason content_filter"
        elif category == "parse_fail" and _REFUSAL.search(text):
            category = "refusal"
            detail = _REFUSAL.search(text).group(0)
    parsed = result.answer if result is not None and result.status == "ok" else None
    rec.update({
        "category": category, "parse_status": result.status if result else None, "parse_detail": detail,
        "flags": sorted(set(flags + (result.flags if result else []))),
        "parsed": parsed, "answer_key": answer_key(ctx.domain, parsed) if parsed is not None else None,
        "witness": result.witness if result else None,
        "n_answer_blocks": result.n_blocks if result else 0,
        "pre_answer_tokens": tokens.count(text[: result.answer_start] if result and result.answer_start is not None else text),
        "channel_value": None, "outcome_class": None, "members_matched": [], "answer_key_matches": [],
        "correct": None, "valid": None, "optimal": None,
    })
    if category == "ok":
        value, label, on_channel, same_key = outcome(ctx, parsed)
        correct, valid, optimal = judge(ctx, parsed)
        rec.update({"channel_value": value, "outcome_class": label, "members_matched": on_channel,
                    "answer_key_matches": same_key, "correct": correct, "valid": valid, "optimal": optimal})
    return rec
