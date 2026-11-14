"""Colouring renderers.

- `render_neighbours` (C style, the default serialisation): vertex header line in
  listing order, then one neighbour line per vertex, neighbours in listing order.
- `render_edge_list` (C E5 style and the theory §5 arm): vertex line, then the edge list
  in the instance's edge order (pass a shuffled-edge instance for the shuffled arm).
- `render_rooms` (A/H style): people, enemy (or friend) pairs, JSON answer.

`task` selects the question: "fewest" (minimise colours), or "k" (colour with 1..k or say
IMPOSSIBLE). `answer_order` None means FREE (the model chooses the output order).
"""

from __future__ import annotations

from reasoning_heuristics.problems.coloring.graph import Graph

NUMBER_WORDS = {
    5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve",
    13: "Thirteen", 14: "Fourteen", 15: "Fifteen", 16: "Sixteen", 17: "Seventeen", 18: "Eighteen",
    19: "Nineteen", 20: "Twenty",
}


def _question(task: str, k: int | None, edge_phrase: str) -> str:
    if task == "fewest":
        return f"Colour every vertex with a positive integer so that {edge_phrase} get different colours, using as few colours as possible."
    if task == "k":
        return f"Colour every vertex with one of the colours 1, 2, ..., {k} so that {edge_phrase} get different colours. If this is impossible, say IMPOSSIBLE."
    raise ValueError(task)


def answer_instruction(answer_order: list[str] | None, allow_impossible: bool) -> str:
    head = "After the line ANSWER:, write " + ("IMPOSSIBLE or " if allow_impossible else "")
    if answer_order is None:
        return head + "one line `vertex: colour` per vertex, in any order you like."
    return head + "one line `vertex: colour` per vertex, in this order: " + ", ".join(answer_order) + "."


def render_neighbours(g: Graph, task: str, answer_order: list[str] | None, k: int | None = None,
                      repeat_prompt: bool = False) -> str:
    lines = [
        f"Graph with {g.n} vertices.",
        "Vertices (in this order): " + ", ".join(g.vertices),
        "Neighbours (one line per vertex, same order):",
    ]
    for v in g.vertices:
        nbrs = g.neighbours_listed(v)
        lines.append(f"{v}: " + (", ".join(nbrs) if nbrs else "(none)"))
    lines += ["", _question(task, k, "neighbours"), answer_instruction(answer_order, task == "k")]
    return _maybe_twice("\n".join(lines), repeat_prompt)


def render_edge_list(g: Graph, task: str, answer_order: list[str] | None, k: int | None = None,
                     repeat_prompt: bool = False) -> str:
    lines = [
        f"Graph with {g.n} vertices and {g.m} edges.",
        "Vertices (in this order): " + ", ".join(g.vertices),
        "Edges: " + ", ".join(f"{u}-{v}" for u, v in g.edges),
        "",
        _question(task, k, "the two ends of every edge"),
        answer_instruction(answer_order, task == "k"),
    ]
    return _maybe_twice("\n".join(lines), repeat_prompt)


def render_rooms(g: Graph, k: int, relation: str = "enemies", rule: str | None = None,
                 preamble: str | None = None, reminder: str | None = None,
                 marked: set[frozenset[str]] | None = None) -> str:
    """A/H rooms framing. `relation` names the listed pairs; `rule` is the rule sentence.

    `marked` pairs get a "★" (A/H E5 partial inversion).
    """
    count = NUMBER_WORDS.get(g.n, str(g.n))
    pairs = []
    for u, v in g.edges:
        star = "★" if marked and frozenset((u, v)) in marked else ""
        pairs.append(f"{u}–{v}{star}")
    lines = [
        f"{count} people ({', '.join(g.vertices)}) are being assigned to rooms 1–{k}.",
        f"The following pairs are {relation}: " + ", ".join(pairs) + ".",
        rule if rule is not None else "Enemies may not share a room.",
    ]
    if preamble:
        lines.append(preamble)
    if reminder:
        lines.append(reminder)
    lines += [
        f"Is there an assignment of people to rooms 1–{k} that follows this rule?",
        "Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:",
        '{"possible": true, "rooms": {"<name>": <room number>, ...}}',
        '{"possible": false, "rooms": null}',
    ]
    return "\n".join(lines)


def _maybe_twice(text: str, repeat: bool) -> str:
    """Theory §5 'prompt given twice' arm: the whole problem statement repeated verbatim."""
    if not repeat:
        return text
    return text + "\n\nHere is the same problem again, repeated verbatim:\n\n" + text
