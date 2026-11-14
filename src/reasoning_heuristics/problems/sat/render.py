"""CNF renderers. Names are fixed by the instance; renderers never invent names.

Two house styles, both copied from the example libraries:

- **A/H style** (`render_textbook`, `render_menu`): fixed-width names x01..xNN, clauses
  "C01: (x08 ∨ ¬x02 ∨ x09)", JSON answer. Used by the baselines vertical.
- **C style** (`render_c`): random two-digit labels, clauses "C1: x57 or not x21 or x60",
  `ANSWER:` block with the values in a requested order. Used by the constructive vertical.
"""

from __future__ import annotations

from reasoning_heuristics.problems.sat.cnf import CNF

SAT_JSON_FORMAT = "sat_json"


def _lit_symbolic(cnf: CNF, lit: int) -> str:
    return cnf.name(lit) if lit > 0 else "¬" + cnf.name(lit)


def render_textbook(cnf: CNF, declared: list[str] | None = None) -> str:
    """A/H CNF framing. `declared` lists every declared variable (defaults to all, in index order)."""
    names = declared if declared is not None else list(cnf.var_names)
    width = len(str(cnf.m)) if cnf.m >= 10 else 2
    widths = {len(c) for c in cnf.clauses}
    k_text = {1: "one literal", 2: "two literals", 3: "three literals"}.get(next(iter(widths)), "literals") if len(widths) == 1 else "literals"
    lines = [
        "Here is a Boolean formula in conjunctive normal form.",
        "Variables: " + ", ".join(names) + ".",
        f'Each clause is a disjunction of {k_text} ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.',
        "",
    ]
    for i, c in enumerate(cnf.clauses, 1):
        lines.append(f"C{i:0{width}d}: (" + " ∨ ".join(_lit_symbolic(cnf, l) for l in c) + ")")
    lines += [
        "",
        "Is there an assignment of truth values to the variables that satisfies every clause?",
        "Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:",
        '{"satisfiable": true, "assignment": "<one digit per variable, ' + names[0] + ' first; 1 = true, 0 = false>"}',
        '{"satisfiable": false, "assignment": null}',
    ]
    return "\n".join(lines)


def render_menu(cnf: CNF) -> str:
    """A/H natural-language framing (Hazra et al.'s menu style). Variable x07 renders as dish D07."""
    dish = {v: "D" + v.lstrip("x") for v in cnf.var_names}
    width = len(str(cnf.m)) if cnf.m >= 10 else 2
    lines = [
        f"You are planning which dishes to serve at a dinner. There are {cnf.n} candidate dishes, "
        f"{dish[cnf.var_names[0]]} to {dish[cnf.var_names[-1]]}; each is either served or not served.",
        "Each guest has a request that is met if at least one of its three conditions holds.",
        "",
    ]
    for i, c in enumerate(cnf.clauses, 1):
        parts = [f"{dish[cnf.name(l)]} is {'served' if l > 0 else 'not served'}" for l in c]
        lines.append(f"Guest {i:0{width}d}: " + ", or ".join(parts) + ".")
    lines += [
        "",
        "Can you choose which dishes to serve so that every guest's request is met?",
        "Think as carefully as you need. Then end your reply with your final answer as JSON on its own line, in exactly one of these forms:",
        '{"satisfiable": true, "assignment": "<one digit per dish, ' + dish[cnf.var_names[0]] + ' first; 1 = served, 0 = not served>"}',
        '{"satisfiable": false, "assignment": null}',
    ]
    return "\n".join(lines)


def c_answer_instruction(order: list[str] | None) -> str:
    if order is None:
        return "After the line ANSWER:, write UNSAT or the values as `x=T` / `x=F`, comma-separated, one per variable, in any order you like."
    return "After the line ANSWER:, write UNSAT or the values as `x=T` / `x=F`, comma-separated, in this order: " + ", ".join(order) + "."


def render_c(cnf: CNF, answer_order: list[str] | None, fixed: dict[str, bool] | None = None) -> str:
    """C-vertical framing. `answer_order` None means FREE (the model chooses the order)."""
    lines = [f"A formula over {cnf.n} true/false variables. Every clause must contain at least one true literal."]
    for i, c in enumerate(cnf.clauses, 1):
        lines.append(f"C{i}: " + " or ".join(cnf.name(l) if l > 0 else "not " + cnf.name(l) for l in c))
    lines.append("")
    if fixed:
        vals = ", ".join(f"{k}={'T' if v else 'F'}" for k, v in fixed.items())
        lines += [f"These values are already fixed and must not be changed: {vals}.", ""]
        lines.append("Find values for all variables that make every clause true (keeping the fixed values), or say UNSAT if none exist.")
    else:
        lines.append("Find values for all variables that make every clause true, or say UNSAT if none exist.")
    lines.append(c_answer_instruction(answer_order))
    return "\n".join(lines)
