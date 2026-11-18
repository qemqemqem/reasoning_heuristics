"""Parse example-library prompts back into instances (test helper only)."""

import json
import re
from pathlib import Path

from reasoning_heuristics.problems.coloring.graph import Graph
from reasoning_heuristics.problems.sat.cnf import CNF

ROOT = Path(__file__).resolve().parents[1]


def library(name):
    return [json.loads(l) for l in (ROOT / "data/examples" / f"{name}.jsonl").read_text().splitlines() if l.strip()]


def find(name, **kw):
    return next(r for r in library(name) if all(r.get(k) == v for k, v in kw.items()))


def graph_from_neighbours(prompt: str) -> Graph:
    lines = prompt.splitlines()
    vertices = lines[1].split(": ", 1)[1].split(", ")
    edges = []
    for line in lines[3:3 + len(vertices)]:
        v, rest = line.split(": ")
        for u in rest.split(", "):
            if u != "(none)" and vertices.index(u) > vertices.index(v):
                edges.append((v, u))
    return Graph(tuple(vertices), tuple(edges))


def graph_from_edge_list(prompt: str) -> Graph:
    lines = prompt.splitlines()
    vertices = lines[1].split(": ", 1)[1].split(", ")
    edges = [tuple(e.split("-")) for e in lines[2].split(": ", 1)[1].split(", ")]
    return Graph(tuple(vertices), tuple(edges))


def cnf_from_c_prompt(prompt: str) -> CNF:
    clauses_text = re.findall(r"^C\d+: (.*)$", prompt, flags=re.M)
    order = re.search(r"in this order: (.*)\.$", prompt, flags=re.M).group(1).split(", ")
    clauses = []
    for body in clauses_text:
        lits = []
        for t in body.split(" or "):
            t = t.strip()
            neg = t.startswith("not ")
            name = t[4:].strip() if neg else t
            lits.append((-1 if neg else 1) * (order.index(name) + 1))
        clauses.append(tuple(lits))
    return CNF(tuple(order), tuple(clauses))
