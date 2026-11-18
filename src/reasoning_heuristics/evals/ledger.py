"""data/runs/LEDGER.md: one row per live run or probe batch, with its API-reported cost.

The ledger is also the running total behind `--budget-tag` / `--budget-usd`: a run's effective
cap is min(--cap-usd, budget − what the ledger already books under that tag), and a run whose
remaining budget is zero does not start.
"""

from __future__ import annotations

import re
from pathlib import Path

HEADER = """# Inference ledger

One row per live run or probe batch. Costs are API-reported (`usage.cost`, summed); dry runs cost nothing and are not listed.

| Date (UTC) | Run id | Model | Condition | Items | API cost (USD) | Budget tag | Notes |
|---|---|---|---|---|---|---|---|
"""


def append(path: Path, *, date: str, run_id: str, model: str, condition: str, items: int, cost_usd: float,
           budget_tag: str, notes: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(HEADER, encoding="utf-8")
    cells = [date, run_id, model, condition, str(items), f"{cost_usd:.6f}", budget_tag, notes.replace("|", "/")]
    with path.open("a", encoding="utf-8") as fh:
        fh.write("| " + " | ".join(cells) + " |\n")


def rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    out = []
    cols = ["date", "run_id", "model", "condition", "items", "cost_usd", "budget_tag", "notes"]
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith("| Date") or set(line) <= set("|- "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= len(cols) - 1:
            out.append(dict(zip(cols, cells + [""] * (len(cols) - len(cells)))))
    return out


def spent(path: Path, budget_tag: str) -> float:
    total = 0.0
    for r in rows(path):
        if r["budget_tag"] == budget_tag and re.fullmatch(r"\d+(\.\d+)?", r["cost_usd"]):
            total += float(r["cost_usd"])
    return total
