"""The results page, docs/results/2026-11-18-results.html, built from the analysis JSON.

    python analysis/results_page.py           # write the page (seconds)
    python analysis/results_page.py --check   # exit 1 if the committed page differs from a fresh render

It reads two files and nothing else:

- analysis/out/prelim_2026_11_18.json, which analysis/prelim_2026_11_18.py writes (its `schema` key
  describes the fields);
- docs/results/findings.html, a hand-written fragment with the claims, shown verbatim under
  "What we can say so far".

Every other number on the page is read from the JSON, for whatever runs it holds. Nothing here
names a run: when more runs land, rerun both scripts and the page follows.

The page is one self-contained file: no network, no external script or style sheet, and every chart
is inline SVG drawn here. Colours are CSS custom properties on :root, with a dark theme under
prefers-color-scheme. The chart colours are the dataviz reference palette's, validated with its
script: categorical slots 1 and 2, a five-step ordinal ramp for the distance bins, the sequential
blue ramp for the heat tables, and the status colours, which always come with an icon and a word.

The verdict every fit carries:

- **ε at its cap**: the slip rate's estimate is at `settings.eps_max` (the engine's EPS_MAX).
- **Reproduces the data**: each of the three statistics in `fits[u][r]["reach"]` lies inside the
  5–95% range of the same statistic over the fake data sets drawn from the fitted mixture
  (`recovery_at_estimate[u][r]["simulated"]`).
- **Nearness, not use**: either of the two fails, or the check was not run. Such weights say whose
  answers the model's answers are near, not which procedures it runs.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parent.parent
JSON_IN = REPO / "analysis" / "out" / "prelim_2026_11_18.json"
FINDINGS = REPO / "docs" / "results" / "findings.html"
PAGE = REPO / "docs" / "results" / "2026-11-18-results.html"

UNEXPLAINED = "unexplained (q)"
TOL = 1e-9
DIST_ALPHA = 0.05  # the distance-profile check fails at a Monte Carlo p below this
STATS = (("exact", "Answers equal to a member's answer"),
         ("beyond_reach", "Answers beyond every member's slip reach"),
         ("special", "Special-token answers (UNSAT, IMPOSSIBLE, X)"))
SET_ORDER = ("pc20", "pc40", "dev")  # pilot sets (where fits live) first; others after, by name
COND_ORDER = ("direct", "thinking-low", "thinking-medium", "thinking-high")
SLIP_REACH = 6  # a near miss changes at most 6 positions (truncated geometric on 1-6)
# distance bins as the JSON stores them, and as the stacked bars show them (an ordinal ramp needs <= 5 steps)
NEAR_BINS = ("0", "1", "2", "3", "4-6", ">6", "special token", "no member")
NEAR_SHOWN = (("d = 0", ("0",)), ("d = 1", ("1",)), ("d = 2–3", ("2", "3")), ("d = 4–6", ("4-6",)),
              ("d > 6", (">6",)), ("special token", ("special token",)), ("no member", ("no member",)))

# The sequential blue ramp (steps 100-700) for the heat tables, and the ink each step takes
HEAT = ("#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6",
        "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b")
HEAT_WHITE_FROM = 7  # steps 450 and darker carry white text, lighter ones near-black


e = html.escape


# =============================================================================================
# Reading the JSON
# =============================================================================================


def per_cell(item_set: str) -> int | None:
    """Items per design cell of an item set: dev is 5, pcN is N."""
    if item_set == "dev":
        return 5
    m = re.fullmatch(r"pc(\d+)", item_set)
    return int(m.group(1)) if m else None


def set_label(item_set: str) -> str:
    n = per_cell(item_set)
    return f"{item_set} ({n} per cell)" if n else item_set


def set_rank(item_set: str) -> tuple[int, str]:
    return (SET_ORDER.index(item_set) if item_set in SET_ORDER else len(SET_ORDER), item_set)


def family_size(model: str) -> tuple[str, float | None]:
    """'qwen/qwen3-32b' -> ('qwen/qwen3', 32.0); 'openai/gpt-oss-120b' -> ('openai/gpt-oss', 120.0)."""
    m = re.fullmatch(r"(.*?)-(\d+(?:\.\d+)?)b", model)
    return (m.group(1), float(m.group(2))) if m else (model, None)


def model_name(run: dict[str, Any]) -> str:
    """The model part of the run's label ('Qwen3-32B direct' -> 'Qwen3-32B')."""
    lab, cond = run["label"], run["condition"]
    return lab[: -len(cond) - 1] if lab.endswith(" " + cond) else lab


def run_key(run: dict[str, Any]) -> tuple:
    fam, size = family_size(run["model"])
    cond = run["condition"]
    return (set_rank(run["item_set"]), fam, size or 0.0,
            COND_ORDER.index(cond) if cond in COND_ORDER else len(COND_ORDER), cond, run["run_id"])


@dataclass
class Fit:
    """One fit: a gated unit on one run, with its predictive-check verdict."""
    unit: str
    run: dict[str, Any]
    rep: dict[str, Any]
    rec: dict[str, Any] | None
    eps_max: float

    @property
    def rid(self) -> str:
        return self.run["run_id"]

    @property
    def eps(self) -> float:
        return self.rep["fit"]["eps"]

    @property
    def at_cap(self) -> bool:
        return self.eps >= self.eps_max - TOL

    @property
    def ppc(self) -> list[dict[str, Any]] | None:
        """The three statistics, observed against the fake data drawn from the fitted mixture."""
        if not self.rec or "simulated" not in self.rec:
            return None
        out = []
        for key, name in STATS:
            obs = self.rep["reach"][key]
            sim = self.rec["simulated"][key]
            lo, hi = sim["p05_p95"]
            out.append({"key": key, "name": name, "obs": obs, "mean": sim["mean"], "lo": lo, "hi": hi,
                        "inside": lo - TOL <= obs <= hi + TOL})
        return out

    @property
    def dist(self) -> dict[str, Any] | None:
        """The distance-profile check (JSONs from before it existed have none)."""
        return (self.rec or {}).get("distance_check")

    @property
    def dist_misfit(self) -> bool:
        return self.dist is not None and self.dist["p_value"] < DIST_ALPHA

    @property
    def n_checks(self) -> int:
        return len(STATS) + (1 if self.dist is not None else 0)

    @property
    def n_outside(self) -> int | None:
        """Checks the data fail: the three statistics outside their 5–95% ranges, plus the distance profile."""
        p = self.ppc
        return None if p is None else sum(not s["inside"] for s in p) + int(self.dist_misfit)

    @property
    def reproduces(self) -> bool:
        return self.n_outside == 0

    @property
    def nearness(self) -> bool:
        return self.at_cap or not self.reproduces

    def why_nearness(self) -> str:
        parts = []
        if self.at_cap:
            parts.append(f"ε is at its cap ({self.eps_max:g})")
        if self.n_outside is None:
            parts.append("the predictive check was not run")
        elif self.n_outside:
            parts.append(f"the fitted model fails {self.n_outside} of {self.n_checks} checks against the data")
        return " and ".join(parts)


class Data:
    """The JSON, with runs in display order and every fit as a Fit."""

    def __init__(self, results: dict[str, Any]):
        self.r = results
        self.runs = sorted(results["runs"], key=run_key)
        self.by_id = {m["run_id"]: m for m in self.runs}
        self.eps_max = float(results["settings"]["eps_max"])
        self.sets = sorted({m["item_set"] for m in self.runs}, key=set_rank)
        self.gated = {s: list(u) for s, u in results["gated_units"].items()}
        self.fits: list[Fit] = []
        rec = results.get("recovery_at_estimate", {})
        for s in sorted(self.gated, key=set_rank):
            for unit in self.gated[s]:
                for m in self.runs:
                    rep = results["fits"].get(unit, {}).get(m["run_id"])
                    if rep is not None and m["item_set"] == s:
                        self.fits.append(Fit(unit, m, rep, rec.get(unit, {}).get(m["run_id"]), self.eps_max))
        self.fit_units = list(dict.fromkeys(f.unit for f in self.fits))

    def runs_of(self, item_set: str) -> list[dict[str, Any]]:
        return [m for m in self.runs if m["item_set"] == item_set]

    def fits_of(self, unit: str) -> list[Fit]:
        return [f for f in self.fits if f.unit == unit]

    def is_gated(self, item_set: str, unit: str) -> bool:
        return unit in self.gated.get(item_set, [])

    def units_of(self, item_set: str) -> list[str]:
        return sorted(self.r["unit_items"].get(item_set, {}))


# =============================================================================================
# Formatting
# =============================================================================================


def f2(x: float | None) -> str:
    return "–" if x is None else f"{x:.2f}"


def f3(x: float | None) -> str:
    return "–" if x is None else f"{x:.3f}"


def pval(p: float | None) -> str:
    """As the doc prints them: with 2,000 permutations the floor is 1/2001 ≈ 0.0005."""
    if p is None:
        return "–"
    return f"{p:.4f}" if p < 0.01 else f"{p:.3f}"


def share(num: float, den: float) -> str:
    """A share as a whole percentage that never rounds a nonzero count to 0% or a shortfall to 100%."""
    if not den:
        return "–"
    v = num / den
    if 0 < v < 0.005:
        return "<1%"
    if 0.995 < v < 1:
        return ">99%"
    return f"{100 * v:.0f}%"


def count_share(num: float, den: float) -> str:
    return "–" if not den else f"{num:.0f}/{den:.0f} ({share(num, den)})"


def plural(n: int, one: str, many: str | None = None) -> str:
    return f"{n} {one if n == 1 else (many or one + 's')}"


def money(x: float) -> str:
    return f"${x:,.2f}" if x >= 1 else f"${x:.3f}"


# =============================================================================================
# Chart pieces: rows of HTML labels beside inline SVG bands drawn in percentages
# =============================================================================================
#
# Each chart row is a small grid: a label, a band (an SVG whose x positions are percentages of its
# own width, so marks keep their shape at any width) and a value column. A container query stacks
# the label above the band when the chart is narrow (phones). Every mark carries a <title>: the
# browser shows it on hover, and the small script at the end turns it into a styled tooltip that
# also works on touch. Every value is also in a table.


class Scale:
    def __init__(self, hi: float, ticks: list[float], lo: float = 0.0):
        self.lo, self.hi, self.ticks = lo, hi, ticks

    def __call__(self, v: float) -> float:
        v = min(max(v, self.lo), self.hi)
        return 100.0 * (v - self.lo) / (self.hi - self.lo)


UNIT_SCALE = Scale(1.0, [0.0, 0.25, 0.5, 0.75, 1.0])


def nice_scale(vmax: float) -> Scale:
    """0 to a round number at or above vmax, with four or five ticks."""
    for top, step in ((0.02, 0.005), (0.05, 0.01), (0.1, 0.025), (0.2, 0.05), (0.3, 0.1), (0.4, 0.1),
                      (0.5, 0.1), (0.6, 0.2), (0.8, 0.2), (1.0, 0.25)):
        if vmax <= top + TOL:
            n = round(top / step)
            return Scale(top, [round(k * step, 6) for k in range(n + 1)])
    return UNIT_SCALE


BAND_H = 22
MID = BAND_H / 2


def pc(x: float) -> str:
    return f"{x:.2f}%"


def band(scale: Scale, marks: list[str], h: int = BAND_H) -> str:
    grid = "".join(f'<line class="g" x1="{pc(scale(t))}" x2="{pc(scale(t))}" y1="0" y2="{h}"/>' for t in scale.ticks)
    return f'<svg class="band" height="{h}" aria-hidden="true">{grid}{"".join(marks)}</svg>'


def tip_group(tip: str, *shapes: str, hit_x: float | None = None) -> str:
    hit = f'<circle class="hit" cx="{pc(hit_x)}" cy="{MID}" r="12"/>' if hit_x is not None else ""
    return f'<g><title>{e(tip)}</title>{hit}{"".join(shapes)}</g>'


def dot(x: float, cls: str, r: float = 4.5, cy: float = MID) -> str:
    return f'<circle class="{cls}" cx="{pc(x)}" cy="{cy}" r="{r}"/>'


def square(x: float, cls: str, s: float = 9.0) -> str:
    return f'<rect class="{cls}" x="{pc(x)}" y="{MID - s / 2}" width="{s:g}" height="{s:g}" rx="1.5" transform="translate({-s / 2:g} 0)"/>'


def hline(x1: float, x2: float, cls: str, cy: float = MID) -> str:
    return f'<line class="{cls}" x1="{pc(x1)}" x2="{pc(x2)}" y1="{cy}" y2="{cy}"/>'


def vtick(x: float, cls: str, half: float = 7.0) -> str:
    return f'<line class="{cls}" x1="{pc(x)}" x2="{pc(x)}" y1="{MID - half}" y2="{MID + half}"/>'


def row(label: str, svg: str, value: str, cls: str = "") -> str:
    return (f'<div class="rc-row{(" " + cls) if cls else ""}"><div class="lab">{label}</div>'
            f'<div class="bw">{svg}</div><div class="val">{value}</div></div>')


def axis_row(scale: Scale, fmt: Callable[[float], str], title: str) -> str:
    texts = []
    for t in scale.ticks:
        p = scale(t)
        anchor = "start" if p <= TOL else ("end" if p >= 100 - TOL else "middle")
        texts.append(f'<text x="{pc(p)}" y="12" text-anchor="{anchor}">{e(fmt(t))}</text>')
    svg = f'<svg class="axis" height="16" aria-hidden="true">{"".join(texts)}</svg>'
    return (f'<div class="rc-row axis"><div class="lab"></div><div class="bw">{svg}'
            f'<div class="axis-title">{e(title)}</div></div><div class="val"></div></div>')


def rowchart(rows: list[str], label: str) -> str:
    return f'<div class="rc" role="group" aria-label="{e(label)}">{"".join(rows)}</div>'


def legend(items: list[tuple[str, str]]) -> str:
    """items: (swatch SVG markup, text)."""
    return '<ul class="legend">' + "".join(
        f'<li><svg width="18" height="14" aria-hidden="true">{sw}</svg>{e(t)}</li>' for sw, t in items) + "</ul>"


SW_DOT = '<circle class="dot" cx="9" cy="7" r="4.5"/>'
SW_WHISKER = '<line class="wh" x1="1" x2="17" y1="7" y2="7"/><circle class="dot" cx="9" cy="7" r="4.5"/>'
SW_PI0 = '<line class="wh0" x1="1" x2="17" y1="7" y2="7"/><rect class="pi0" x="4.5" y="2.5" width="9" height="9" rx="1.5"/>'
SW_CHANCE = '<circle class="chance" cx="9" cy="7" r="4"/>'
SW_SIM = '<rect class="sim" x="1" y="2" width="16" height="10" rx="2"/><line class="simmean" x1="9" x2="9" y1="0" y2="14"/>'
SW_OBS_IN = '<circle class="obs" cx="9" cy="7" r="4.5"/>'
SW_OBS_OUT = '<circle class="obs out" cx="9" cy="7" r="4.5"/>'
SW_RING = '<circle class="ring" cx="9" cy="7" r="4"/>'


def table(header: list[str], rows: list[list[str]], cls: str = "", head_html: str | None = None, fit: bool = False) -> str:
    """A table in its own horizontal scroller. Cells are HTML; numbers right-aligned by class."""
    th = head_html or "<tr>" + "".join(f"<th>{h}</th>" for h in header) + "</tr>"
    body = "".join("<tr>" + "".join(c if c.startswith("<td") else f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return (f'<div class="scroll{" fit" if fit else ""}"><table class="{cls}"><thead>{th}</thead>'
            f"<tbody>{body}</tbody></table></div>")


def num(x: str) -> str:
    return f'<td class="n">{x}</td>'


def details(summary: str, inner: str, open_: bool = False) -> str:
    return f'<details{" open" if open_ else ""}><summary>{summary}</summary>{inner}</details>'


def chip(kind: str, text: str) -> str:
    icon = {"good": "✓", "bad": "✗", "warn": "▲", "info": "●", "none": "○"}[kind]
    return f'<span class="chip {kind}"><span class="ic" aria-hidden="true">{icon}</span>{text}</span>'


def eps_chip(f: Fit) -> str:
    if f.at_cap:
        return chip("warn", f"ε at its cap ({f.eps_max:g})")
    return chip("none", f"ε = {f.eps:.2f}, below its cap")


def ppc_chip(f: Fit) -> str:
    n = f.n_outside
    if n is None:
        return chip("warn", "predictive check not run")
    if n == 0:
        return chip("good", f"reproduces the data ({f.n_checks} of {f.n_checks} checks)")
    return chip("bad", f"misses the data ({n} of {f.n_checks} checks failed)")


def reading_chip(f: Fit) -> str:
    return chip("bad", "nearness, not use") if f.nearness else chip("good", "weights describe the answers")


# =============================================================================================
# Sections
# =============================================================================================


def section_header(d: Data) -> str:
    pilot = [s for s in d.sets if s != "dev" and per_cell(s)]
    sizes = "; ".join(
        ([f"pilot size, {' and '.join(str(per_cell(s)) for s in pilot)} items per design cell ({', '.join(pilot)})"] if pilot else [])
        + (["dev size, 5 per cell (dev)"] if "dev" in d.sets else []))
    conds = sorted({m["condition"] for m in d.runs}, key=lambda c: COND_ORDER.index(c) if c in COND_ORDER else 99)
    one_sample = all(m["n_records"] == m["n_items"] for m in d.runs)
    fits = d.fits
    n, n_cap = len(fits), sum(f.at_cap for f in fits)
    n_miss = sum(f.n_outside is not None and f.n_outside > 0 for f in fits)
    n_unchecked = sum(f.n_outside is None for f in fits)
    good = [f for f in fits if not f.nearness]
    best_effort = any(m["condition"] == "thinking-high" for m in d.runs)

    banner = (
        '<div class="banner" role="note"><strong>Preliminary.</strong> '
        f"Dev-split items; {e(sizes)}; "
        + ("one sample per item; " if one_sample else "")
        + f"conditions {e(', '.join(conds))}. "
        + ("" if best_effort else "No run at best effort (thinking-high) is in yet. ")
        + "This is not the pre-registered study, and nothing here tests a hypothesis of DESIGN §4.</div>")

    good_list = "; ".join(f"{e(f.unit)} on {e(f.run['label'])} ({e(f.run['item_set'])} items)" for f in good)
    lead = (f'<p class="lead"><strong>Read this first.</strong> In {n_cap} of {n} fits the slip rate ε sits at its '
            f"cap ({d.eps_max:g}), and in {n_miss} of {n} the data simulated from the fitted model fail to reproduce "
            "simple features of the real answers"
            + (f" ({n_unchecked} not checked)" if n_unchecked else "") + ". "
            + (f"Only {plural(len(good), 'fit')} {'reproduces its' if len(good) == 1 else 'reproduce their'} data "
               f"with ε below its cap: {good_list}. " if good else "No fit reproduces its data with ε below its cap. ")
            + "Every other fit's weights mean <em>whose answers the model's answers are near</em>, not "
              "<em>procedures the model runs</em>; each is labelled <span class=\"tag-near\">nearness, not use</span> below.</p>")

    hero = (f'<div class="hero"><div class="hero-num">{len(good)} of {n}</div>'
            '<div class="hero-cap">fits reproduce their data with the slip rate below its cap</div></div>')

    rows = []
    for f in fits:
        rows.append([e(f.unit), e(f.run["label"]), e(f.run["item_set"]), eps_chip(f), ppc_chip(f), reading_chip(f)])
    board = table(["Unit", "Run", "Items", "Slip rate ε", "Predictive check", "Read the weights as"], rows, "board")

    nav = ('<nav class="toc" aria-label="Sections"><a href="#findings">Findings</a><a href="#runs">Runs</a>'
           '<a href="#accuracy">Accuracy</a><a href="#weights">Weights</a><a href="#ppc">Predictive check</a>'
           '<a href="#ea">Error agreement</a><a href="#distance">Distance</a><a href="#compare">Comparisons</a>'
           + ('<a href="#textbook">Textbook transfer</a>' if any(
               "by_framing" in x for units in d.r["descriptive"].values() for x in units.values()) else "")
           + '<a href="#descriptive">Not fitted</a><a href="#limits">Limits</a><a href="#reproduce">Reproduce</a></nav>')
    return (f'<header><p class="kicker">Heuristics Under Hardness · results page</p>'
            f'<h1>Which heuristics do LLMs use on NP-hard problems? Preliminary results</h1>{banner}'
            f'<div id="verdict">{hero}{lead}{board}</div>{nav}</header>')


def section_findings(findings_html: str) -> str:
    return ('<section id="findings"><h2>What we can say so far</h2>'
            '<p class="note">Hand-written claims (docs/results/findings.html). Strength labels: '
            '<span class="strength a">(a)</span> fitted, and the fitted model reproduces the data; '
            '<span class="strength b">(b)</span> fitted, but the model does not reproduce the data, so the weights read as nearness; '
            '<span class="strength c">(c)</span> a descriptive count.</p>'
            f'<div class="findings">{findings_html.strip()}</div></section>')


def section_runs(d: Data) -> str:
    rows = []
    for m in d.runs:
        ct = m.get("cache_twin")
        cache = str(m["from_cache"])
        if ct and ct.get("cached"):
            same = ct["cached_same_generation_as_dev_run"]
            cache += " (all the dev run's)" if same == ct["cached"] else f" ({same} the dev run's)"
        prov = m.get("providers_served") or {}
        served = ", ".join(prov) if len(prov) == 1 else ", ".join(f"{k} {v}" for k, v in prov.items())
        quant = ", ".join((m.get("provider_routing") or {}).get("quantizations") or [])
        status = "" if m["status"] == "complete" else f' <span class="pill">{e(m["status"])}</span>'
        rows.append([f"<code>{e(m['run_id'])}</code>{status}", e(model_name(m)), e(m["condition"]), e(m.get("effort") or "–"),
                     e(m["item_set"]), num(f"{m['n_records']:,}"), num(e(cache)), num(money(m["spent_usd"])),
                     e(served + (f", {quant}" if quant else ""))])
    total = sum(m["spent_usd"] for m in d.runs)
    rows.append(["<strong>Total</strong>", "", "", "", "", num(f"{sum(m['n_records'] for m in d.runs):,}"),
                 num(str(sum(m["from_cache"] for m in d.runs))), num(f"<strong>{money(total)}</strong>"), ""])
    skipped = d.r.get("skipped_runs") or []
    skip = (f'<p class="note">Found but not yet scored (left out): {", ".join(f"<code>{e(s)}</code>" for s in skipped)}.</p>'
            if skipped else "")
    sizes = "; ".join(f"{e(s)}: {per_cell(s)} items per design cell" for s in d.sets if per_cell(s))
    return ('<section id="runs"><h2>Runs</h2>'
            f"<p>{plural(len(d.runs), 'run')} on {plural(len(d.sets), 'item set')} ({sizes}), all dev-split items. API cost is "
            "as the provider reported it. A pilot run can take responses from the response cache: those are the paired dev "
            "run's own responses to the same prompts, on the items the two sets share, so the two runs are not independent "
            "samples there.</p>"
            + table(["Run", "Model", "Condition", "Effort", "Items", "Responses", "From the response cache", "API cost",
                     "Served by, precision"], rows, "runs") + skip + "</section>")


def heat_cell(numr: float, den: float, what: str) -> str:
    if not den:
        return '<td class="hc na">–</td>'
    v = numr / den
    k = min(len(HEAT) - 1, max(0, round(v * (len(HEAT) - 1))))
    return f'<td class="hc h{k}" title="{e(what)}: {numr:.0f} of {den:.0f}">{share(numr, den)}</td>'


def section_accuracy(d: Data) -> str:
    out = ['<section id="accuracy"><h2>Accuracy and answer validity</h2>'
           "<p>For every unit (eval × domain) and run: the share of <em>ok</em> answers that are correct, and the share that are "
           "valid (a proper colouring, a feasible packing, a satisfying assignment). Excluded responses (parse failures, truncation) "
           "are not in the denominators. Validity is not defined on decision and entailment units (–). "
           '<span class="pill">fitted</span> marks the units whose mixture fits pass the recovery gates at that size.</p>',
           heat_legend()]
    for s in d.sets:
        runs = d.runs_of(s)
        head = ('<tr><th rowspan="2" class="sticky">Unit</th>'
                + "".join(f'<th colspan="2" class="runh">{e(m["label"])}</th>' for m in runs) + "</tr><tr>"
                + "".join('<th class="sub">correct</th><th class="sub">valid</th>' for _ in runs) + "</tr>")
        rows = []
        for unit in d.units_of(s):
            cells = [f'<td class="sticky">{e(unit)}' + (' <span class="pill">fitted</span>' if d.is_gated(s, unit) else "") + "</td>"]
            for m in runs:
                desc = d.r["descriptive"].get(m["run_id"], {}).get(unit)
                if desc is None:
                    cells += ['<td class="hc na">–</td>'] * 2
                    continue
                cells.append(heat_cell(desc["correct"], desc["ok"], "correct of ok"))
                cells.append(heat_cell(desc["valid"], desc["valid_defined"], "valid of ok"))
            rows.append(cells)
        out.append(f"<h3>{e(set_label(s))}</h3>" + table([], rows, "heat", head, fit=True))
    out.append("</section>")
    return "".join(out)


def heat_legend() -> str:
    stops = "".join(f'<span class="hs h{k}"></span>' for k in range(len(HEAT)))
    return f'<div class="heat-legend" aria-hidden="true"><span>0%</span><span class="hs-row">{stops}</span><span>100%</span></div>'


def weights_panel(f: Fit, labels: list[str]) -> str:
    w = f.rep["fit"]["weights"]
    bca = f.rep.get("bca", {})
    fitj = f.rep["fit"]
    rows = []
    for lab in labels:
        if lab not in w:
            continue
        x = w[lab]
        is_q = lab == UNEXPLAINED
        name = "π₀ unexplained (q)" if is_q else lab
        if isinstance(x["pi"], str):
            lo, hi = x["range"]
            svg = band(UNIT_SCALE, [tip_group(f"{name}: not identified, range [{lo:.3f}, {hi:.3f}]",
                                              hline(UNIT_SCALE(lo), UNIT_SCALE(hi), "nid"))])
            rows.append(row(e(name), svg, f"not identified [{lo:.3f}, {hi:.3f}]", "q" if is_q else ""))
            continue
        b = bca.get(lab)
        tip = f"{name}: π = {x['pi']:.3f}, 95% percentile [{x['lo']:.3f}, {x['hi']:.3f}]" + (
            f", BCa [{b[0]:.3f}, {b[1]:.3f}]" if b else "")
        mark = square(UNIT_SCALE(x["pi"]), "pi0") if is_q else dot(UNIT_SCALE(x["pi"]), "dot")
        svg = band(UNIT_SCALE, [tip_group(tip, hline(UNIT_SCALE(x["lo"]), UNIT_SCALE(x["hi"]), "wh0" if is_q else "wh"), mark,
                                          hit_x=UNIT_SCALE(x["pi"]))])
        rows.append(row(e(name), svg, f"{x['pi']:.3f} [{x['lo']:.3f}, {x['hi']:.3f}]", "q" if is_q else ""))
    rows.append(axis_row(UNIT_SCALE, lambda t: f"{t:g}", "weight π (95% percentile interval)"))
    if f.nearness:
        read = (f'<p class="reading near"><strong>Nearness, not use:</strong> {e(f.why_nearness())}. '
                "These weights say whose answers this model's answers are near, not which procedures it runs.</p>")
    else:
        read = ('<p class="reading ok"><strong>Reproduces the data.</strong> ε is below its cap and the fitted model '
                f"passes all {f.n_checks} checks. That makes the weights a fair description of these answers; "
                "it does not show that the model runs these procedures.</p>")
    rec = f.rec
    if rec:
        bv = rec.get("bca", {})
        recl = (f"Recovery at the estimate ({rec['replicates']} fake data sets): max |bias| {rec['max_abs_bias']:.3f}; "
                f"smallest coverage {rec['min_coverage']:.2f} with percentile intervals ({'passes' if rec['pass'] else 'fails'} the gates)"
                + (f", {bv['min_coverage']:.2f} with BCa ({'passes' if bv['pass'] else 'fails'})" if bv else "") + ".")
    else:
        recl = "Recovery at the estimate: not run."
    meta = (f'<p class="meta">ε = {fitj["eps"]:.3f} [{fitj["eps_ci"][0]:.3f}, {fitj["eps_ci"][1]:.3f}], '
            f'ρ = {fitj["rho"]:.3f} [{fitj["rho_ci"][0]:.3f}, {fitj["rho_ci"][1]:.3f}]; '
            f'{fitj["n_rows"]} answers in {fitj["n_clusters"]} clusters; log-likelihood {fitj["loglik"]:.1f}. {e(recl)}</p>')
    return (f'<article class="panel{" is-near" if f.nearness else ""}"><h4>{e(f.run["label"])}</h4>'
            f'<div class="chips">{eps_chip(f)}{ppc_chip(f)}</div>{read}'
            f'{rowchart(rows, f"Fitted weights, {f.unit}, {f.run["label"]}")}{meta}</article>')


def weight_labels(fits: list[Fit]) -> list[str]:
    labels = list(dict.fromkeys(l for f in fits for l in f.rep["fit"]["weights"] if l != UNEXPLAINED))
    return labels + [UNEXPLAINED]


def unit_facts_line(f: Fit) -> str:
    uf = f.rep.get("unit_facts", {})
    pos = "/".join(map(str, uf.get("positions_per_item", [])))
    return (f"{uf.get('n_items', '?')} items in {uf.get('n_cells', '?')} cells ({uf.get('n_clusters', '?')} clusters)"
            + (f", {pos} positions per item" if pos else ""))


def section_weights(d: Data) -> str:
    out = ['<section id="weights"><h2>Fitted weights, per gated unit</h2>'
           "<p>The fit is P(y | x) = Σ<sub>h</sub> π<sub>h</sub> P(y | h, x) + π₀ q(y | x) per (model, condition, eval, domain). "
           "π<sub>h</sub> is the share of answers attributed to member h's answer <em>or a near miss of it</em> (up to "
           f"{SLIP_REACH} positions changed), ε the share of each member's answers that are near misses, and π₀ the unexplained mass "
           f"(q, a uniformly random answer). Intervals are 95% percentile intervals from {d.r['settings']['n_boot']:,} draws of the "
           "cluster bootstrap (a cluster is a base item with its variants). Weights are shown only for units whose fake-model "
           "recovery gates pass at the run's item size (DESIGN §5 rule 12).</p>",
           legend([(SW_WHISKER, "member weight π with its 95% interval"), (SW_PI0, "unexplained mass π₀ (q)")])]
    for unit in d.fit_units:
        fits = d.fits_of(unit)
        labels = weight_labels(fits)
        sets = ", ".join(dict.fromkeys(set_label(f.run["item_set"]) for f in fits))
        out.append(f'<h3>{e(unit)} <span class="sub">{e(sets)}; {e(unit_facts_line(fits[0]))}</span></h3>')
        out.append('<div class="panels">' + "".join(weights_panel(f, labels) for f in fits) + "</div>")
        out.append(details(f"Table: weights for {e(unit)}", weights_table(fits, labels)))
    out.append("</section>")
    return "".join(out)


def weights_table(fits: list[Fit], labels: list[str]) -> str:
    head = ("<tr><th>Weight</th>" + "".join(f'<th colspan="2">{e(f.run["label"])}</th>' for f in fits) + "</tr><tr><th></th>"
            + "".join('<th class="sub">π [95% percentile]</th><th class="sub">BCa</th>' for _ in fits) + "</tr>")
    rows = []
    for lab in labels:
        cells = [e("π₀ unexplained (q)" if lab == UNEXPLAINED else lab)]
        for f in fits:
            x = f.rep["fit"]["weights"].get(lab)
            if x is None:
                cells += ["–", "–"]
            elif isinstance(x["pi"], str):
                cells += [f"not identified, range [{x['range'][0]:.3f}, {x['range'][1]:.3f}]", "–"]
            else:
                b = f.rep.get("bca", {}).get(lab)
                cells += [num(f"{x['pi']:.3f} [{x['lo']:.3f}, {x['hi']:.3f}]"), num(f"[{b[0]:.3f}, {b[1]:.3f}]" if b else "–")]
        rows.append(cells)
    for key, name in (("eps", "ε (slip rate)"), ("rho", "ρ (slip shape)")):
        cells = [name]
        for f in fits:
            ci = f.rep["fit"][f"{key}_ci"]
            cells += [num(f"{f.rep['fit'][key]:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]"), "–"]
        rows.append(cells)
    rows.append(["Read as"] + [c for f in fits for c in ("nearness, not use" if f.nearness else "reproduces the data", "")])
    return table([], rows, "", head)


def section_ppc(d: Data) -> str:
    st = d.r["settings"]
    has_dist = any(f.dist is not None for f in d.fits)
    out = ['<section id="ppc"><h2>The predictive check: does the fitted model reproduce the data?</h2>'
           f"<p>{st['recovery_reps']} fake data sets are drawn from each fitted mixture (its weights, those below {st['plant_min']:g} "
           "set to 0, its ε and its ρ), on the same items with the same exclusions. Three simple statistics of the real answers are "
           "compared with the same statistics over the fake data sets: their mean and 5–95% range. An observed value outside that "
           "range means the fitted model does not generate answers like these."
           + (" The fourth check is the <strong>distance profile</strong>: the shares of answers at each distance from the nearest "
              "member (0, 1, 2, 3, 4–6, more than 6, a special token), against the same shares in the fake data sets. Its statistic "
              "is the total variation distance from the fake data sets' mean profile, and p is the share of fake data sets at least "
              f"as far from it as the real data. It fails at p &lt; {DIST_ALPHA:g}." if has_dist else "")
           + " A fit passes only if every check passes.</p>"
           + ("<p class=\"plain\"><strong>Why the fourth check.</strong> The first statistic can barely fail while ε is below its cap: "
              "the fit chooses ε so that the expected share of exact matches is close to the observed share. On C E2 knapsack the "
              "other two are 0 by construction (no special tokens, no answer out of reach), so the first three checks there amount "
              "to “ε is below its cap”. The distance profile tests the shape of the near misses, which no single parameter fits. "
              "Because the fake data come from parameters fitted to the real data, the real data sit closer to the fake data's "
              "mean than a fresh data set would: the check is conservative, so a failure is a real misfit, and a pass is weak "
              "support.</p>" if has_dist else ""),
           legend([(SW_SIM, "fake data from the fitted model: 5–95% range and mean"), (SW_OBS_IN, "observed, inside the range"),
                   (SW_OBS_OUT, "observed, outside the range")])]
    scale = UNIT_SCALE
    for unit in d.fit_units:
        out.append(f"<h3>{e(unit)}</h3>")
        blocks = []
        for f in d.fits_of(unit):
            rows = []
            ppc = f.ppc
            if ppc is None:
                blocks.append(f'<article class="panel"><h4>{e(f.run["label"])}</h4><div class="chips">{ppc_chip(f)}</div></article>')
                continue
            for s in ppc:
                verdict = "inside" if s["inside"] else "outside"
                tip = f"{s['name']}: observed {s['obs']:.3f}; fitted model {s['mean']:.3f} [{s['lo']:.3f}, {s['hi']:.3f}] ({verdict})"
                lo, hi = scale(s["lo"]), scale(s["hi"])
                marks = [f'<rect class="sim" x="{pc(lo)}" y="{MID - 6}" width="{pc(max(hi - lo, 0.0))}" height="12" rx="2"/>',
                         vtick(scale(s["mean"]), "simmean"), dot(scale(s["obs"]), "obs" + ("" if s["inside"] else " out"))]
                svg = band(scale, [tip_group(tip, *marks, hit_x=scale(s["obs"]))])
                val = (f"{s['obs']:.2f} vs {s['mean']:.2f} [{s['lo']:.2f}, {s['hi']:.2f}]"
                       + ("" if s["inside"] else ' <span class="out-word"><span aria-hidden="true">✗</span> outside</span>'))
                rows.append(row(e(s["name"]), svg, val))
            dc = f.dist
            if dc is not None:
                lo, hi = dc["tv_simulated_p05_p95"]
                bad = f.dist_misfit
                tip = (f"Distance profile: total variation from the fitted model's mean profile, observed {dc['tv_observed']:.3f}; "
                       f"fake data {dc['tv_simulated_mean']:.3f} [{lo:.3f}, {hi:.3f}]; p = {dc['p_value']:.3f}")
                marks = [f'<rect class="sim" x="{pc(scale(lo))}" y="{MID - 6}" width="{pc(max(scale(hi) - scale(lo), 0.0))}" '
                         'height="12" rx="2"/>', vtick(scale(dc["tv_simulated_mean"]), "simmean"),
                         dot(scale(dc["tv_observed"]), "obs" + (" out" if bad else ""))]
                val = (f"{dc['tv_observed']:.2f} vs {dc['tv_simulated_mean']:.2f} [{lo:.2f}, {hi:.2f}] "
                       f'<span class="nw">· p {dc["p_value"]:.2f}</span>'
                       + (' <span class="out-word"><span aria-hidden="true">✗</span> misfit</span>' if bad else ""))
                rows.append(row("Distance profile (total variation from the fitted model's)",
                                band(scale, [tip_group(tip, *marks, hit_x=scale(dc["tv_observed"]))]), val))
            rows.append(axis_row(scale, lambda t: f"{t:g}", "share of answers (distance profile: total variation)"))
            blocks.append(f'<article class="panel{" is-near" if f.nearness else ""}"><h4>{e(f.run["label"])}</h4>'
                          f'<div class="chips">{ppc_chip(f)}{eps_chip(f)}</div>'
                          f'{rowchart(rows, f"Predictive check, {unit}, {f.run["label"]}")}</article>')
        out.append('<div class="panels">' + "".join(blocks) + "</div>")
    rows = []
    for f in d.fits:
        ppc = f.ppc or []
        cells = [e(f.unit), e(f.run["label"])]
        for s in ppc:
            cells.append(num(f"{s['obs']:.3f} vs {s['mean']:.3f} [{s['lo']:.3f}, {s['hi']:.3f}]" + ("" if s["inside"] else " <strong>outside</strong>")))
        cells += ["not run"] * (len(STATS) - len(ppc))
        if has_dist:
            dc = f.dist
            cells.append(num(f"{dc['tv_observed']:.3f} vs {dc['tv_simulated_mean']:.3f} [{dc['tv_simulated_p05_p95'][0]:.3f}, "
                             f"{dc['tv_simulated_p05_p95'][1]:.3f}]; p {dc['p_value']:.3f}" + (" <strong>misfit</strong>" if f.dist_misfit else ""))
                         if dc else "not run")
        rows.append(cells)
    out.append(details("Table: the predictive check for every fit",
                       table(["Unit", "Run"] + [e(n) + ": observed vs fitted model [5–95%]" for _, n in STATS]
                             + (["Distance profile: total variation, observed vs fake data [5–95%]; p"] if has_dist else []), rows)))
    if has_dist:
        out.append(details("Table: the distance profile of every fit, bin by bin", dist_table(d.fits)))
    out.append("</section>")
    return "".join(out)


def dist_table(fits: list[Fit]) -> str:
    """Observed share of answers per distance bin against the fake data sets' mean [5–95%]."""
    bins = next(f.dist["bins"] for f in fits if f.dist)
    rows = []
    for f in fits:
        dc = f.dist
        if not dc:
            continue
        cells = [e(f.unit), e(f.run["label"])]
        for b in bins:
            o, m, (lo, hi) = dc["observed"][b], dc["mean"][b], dc["p05_p95"][b]
            flag = "" if lo - TOL <= o <= hi + TOL else " <strong>outside</strong>"
            cells.append(num(f"{o:.2f} vs {m:.2f} [{lo:.2f}, {hi:.2f}]{flag}"))
        rows.append(cells)
    head = [f"d = {b}" if b[0].isdigit() or b[0] == ">" else b for b in bins]
    return table(["Unit", "Run"] + head, rows)


def section_ea(d: Data) -> str:
    n_perm = d.r["settings"]["n_perm"]
    out = ['<section id="ea"><h2>Error agreement against chance</h2>'
           "<p><strong>EA</strong> (error agreement) is P(y = h(x) | y wrong, h(x) wrong): among items where both the answer and "
           "member h's answer are wrong, how often they are the same answer. It counts exact matches only, so it does not lean on "
           "the near-miss model. <strong>Chance</strong> is the engine's within-cell permutation baseline: answers shuffled "
           f"{n_perm:,} times among items of the same cell whose answer spaces match. p is the one-sided permutation p-value; its "
           f"floor is 1/{n_perm + 1:,} ≈ {1 / (n_perm + 1):.4f}. These p-values are per member and uncorrected.</p>",
           legend([(SW_DOT, "observed EA"), (SW_CHANCE, "permutation chance level")])]
    for unit in d.fit_units:
        fits = d.fits_of(unit)
        vmax = 0.0
        for f in fits:
            for g, v in f.rep["error_agreement"]["ea"].items():
                for k in ("observed", "baseline"):
                    if v.get(k) is not None:
                        vmax = max(vmax, v[k])
        scale = nice_scale(max(vmax, 0.02))
        out.append(f"<h3>{e(unit)}</h3>")
        no_base = [f for f in fits if all(v.get("baseline") is None for v in f.rep["error_agreement"]["ea"].values())]
        if no_base:
            exch = sorted({f2(f.rep["error_agreement"].get("exchangeable")) for f in no_base})
            out.append('<p class="plain"><strong>No permutation baseline on this unit'
                       + ("" if len(no_base) == len(fits) else f" for {', '.join(e(f.run['label']) for f in no_base)}")
                       + f".</strong> Its exchangeable share is {'/'.join(exch)}: no two items in a cell share their answer "
                       "space, so the within-cell shuffle cannot move any answer, and the engine reports no chance level, lift or "
                       "p-value. Below are the raw counts only, with nothing to compare them against.</p>")
        blocks = []
        for f in fits:
            ea = f.rep["error_agreement"]
            counts = f.rep.get("ea_counts", {})
            rows, undefined = [], []
            for g, v in ea["ea"].items():
                if v.get("observed") is None:
                    undefined.append(g)
                    continue
                c = counts.get(g, {})
                base = v.get("baseline")
                marks = []
                if base is not None:
                    marks += [hline(scale(base), scale(v["observed"]), "lift"), dot(scale(base), "chance", r=4)]
                marks.append(dot(scale(v["observed"]), "dot"))
                tip = (f"{g}: EA {c.get('agree', 0):.0f}/{c.get('n', 0):.0f} = {v['observed']:.3f}"
                       + (f"; chance {base:.3f}; p = {pval(v.get('p_value'))}" if base is not None else "; no chance level"))
                val = (f"{c.get('agree', 0):.0f}/{c.get('n', 0):.0f} = {v['observed']:.3f}"
                       + (f' <span class="nw">· chance {base:.3f}</span> <span class="nw">· p {pval(v.get("p_value"))}</span>'
                          if base is not None else ""))
                rows.append(row(e(g), band(scale, [tip_group(tip, *marks, hit_x=scale(v["observed"]))]), val))
            rows.append(axis_row(scale, lambda t: f"{t:g}", "EA: agree / both wrong"))
            note = (f'<p class="meta">No EA for {", ".join(e(g) for g in undefined)}: none gives a single wrong answer on these '
                    "items (set-valued members, stored distributions, or members that are never wrong here).</p>" if undefined else "")
            blocks.append(f'<article class="panel"><h4>{e(f.run["label"])}</h4>'
                          f'{rowchart(rows, f"Error agreement, {unit}, {f.run["label"]}")}{note}</article>')
        out.append('<div class="panels">' + "".join(blocks) + "</div>")
        out.append(details(f"Table: EA, co-error and the weights against chance, {e(unit)}", ea_table(fits)))
    out.append("</section>")
    return "".join(out)


def ea_table(fits: list[Fit]) -> str:
    rows = []
    for f in fits:
        ea = f.rep["error_agreement"]
        counts = f.rep.get("ea_counts", {})
        wl = (f.rep.get("weight_lift") or {}).get("by_group") or {}
        for g in list(ea["ea"]) + [UNEXPLAINED]:
            v, co, w, c = ea["ea"].get(g, {}), ea["co_error"].get(g, {}), wl.get(g, {}), counts.get(g, {})
            rows.append([e(f.run["label"]), e(g), num(f2(ea.get("exchangeable"))),
                         num(f3(v.get("observed")) + (f" ({c['agree']:.0f}/{c['n']:.0f})" if c.get("n") else "")),
                         num(f3(v.get("baseline"))), num(pval(v.get("p_value"))),
                         num(f3(co.get("observed")) + (f" ({c['co_agree']:.0f}/{c['n_h_wrong']:.0f})" if c.get("n_h_wrong") else "")),
                         num(f3(co.get("baseline"))), num(pval(co.get("p_value"))),
                         num(f3(w.get("observed"))), num(f3(w.get("baseline"))), num(pval(w.get("p_value")))])
    return table(["Run", "Member group", "Exchangeable share", "EA (agree / both wrong)", "chance", "p",
                  "co-error (agree / member wrong)", "chance", "p", "π", "chance", "p"], rows)


def section_distance(d: Data) -> str:
    out = ['<section id="distance"><h2>How far each answer is from the nearest member\'s answer</h2>'
           "<p>For each answer, the distance to the nearest member's answer (for a set-valued member, its nearest solution): "
           "vertices recoloured up to renaming, items toggled, variables flipped. d = 0 is an exact match. A near miss changes "
           f"at most {SLIP_REACH} positions, so an answer more than {SLIP_REACH} away from every member can only be explained by q "
           "(or a stored distribution's lump). Taking the nearest of a set's solutions favours set-valued members with many solutions.</p>",
           near_legend()]
    for unit in d.fit_units:
        fits = d.fits_of(unit)
        out.append(f'<h3>{e(unit)} <span class="sub">{e(unit_facts_line(fits[0]))}</span></h3>')
        rows = []
        for f in fits:
            nb = f.rep["near"]
            n = nb["n"]
            bins = nb["bins"]
            segs, seps, x = [], [], 0.0
            for k, (name, keys) in enumerate(NEAR_SHOWN):
                c = sum(bins.get(b, 0) for b in keys)
                if not c:
                    continue
                if segs:  # a 2px surface gap between touching segments
                    seps.append(f'<line class="sep" x1="{pc(x)}" x2="{pc(x)}" y1="{MID - 8}" y2="{MID + 8}"/>')
                w = 100.0 * c / n
                segs.append(f'<g><title>{e(name)}: {c} of {n} answers ({share(c, n)})</title>'
                            f'<rect class="nb{k}" x="{pc(x)}" y="{MID - 7}" width="{pc(w)}" height="14"/></g>')
                x += w
            cid = "c" + re.sub(r"[^a-z0-9]", "", (f.unit + f.rid).lower())
            svg = (f'<svg class="band" height="{BAND_H}" aria-hidden="true"><defs><clipPath id="{cid}">'
                   f'<rect x="0" y="{MID - 7}" width="100%" height="14" rx="4"/></clipPath></defs>'
                   f'<g clip-path="url(#{cid})">{"".join(segs)}{"".join(seps)}</g></svg>')
            d0 = bins.get("0", 0)
            far = bins.get(">6", 0)
            val = f"d = 0: {share(d0, n)} · d &gt; {SLIP_REACH}: {share(far, n)}"
            rows.append(row(e(f.run["label"]) + f' <span class="sub">({n} answers)</span>', svg, val))
        rows.append(axis_row(UNIT_SCALE, lambda t: f"{100 * t:.0f}%", "share of answers"))
        out.append(rowchart(rows, f"Distance to the nearest member, {unit}"))
        trows = []
        for f in fits:
            nb = f.rep["near"]
            trows.append([e(f.run["label"]), num(str(nb["n"]))] + [num(count_share(nb["bins"].get(b, 0), nb["n"])) for b in NEAR_BINS])
        out.append(details(f"Table: distance bins, {e(unit)}", table(["Run", "Answers"] + [f"d = {b}" if b[0].isdigit() or b[0] == ">" else b for b in NEAR_BINS], trows)))
    out.append("</section>")
    return "".join(out)


def near_legend() -> str:
    items = []
    for k, (name, _) in enumerate(NEAR_SHOWN):
        items.append((f'<rect class="nb{k}" x="1" y="2" width="16" height="10" rx="2"/>', name))
    return legend(items)


def cond_rank(cond: str) -> int:
    return COND_ORDER.index(cond) if cond in COND_ORDER else len(COND_ORDER)


def comparison_pairs(d: Data) -> tuple[list[tuple[dict, dict, str]], list[tuple[dict, dict, str]]]:
    """(condition within a model, size within a family): pairs of runs on the same item set. Condition pairs are
    every two conditions one model ran on the same items (direct → thinking, low → high effort), in COND_ORDER."""
    think, size = [], []
    by_model: dict[tuple[str, str], list[dict]] = defaultdict(list)
    by_family: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for m in d.runs:
        by_model[(m["model"], m["item_set"])].append(m)
        fam, sz = family_size(m["model"])
        if sz is not None:
            by_family[(fam, m["condition"], m["item_set"])].append(m)
    for (model, s), ms in by_model.items():
        ms = sorted(ms, key=lambda m: cond_rank(m["condition"]))
        for i, a in enumerate(ms):
            for b in ms[i + 1:]:
                if a["condition"] != b["condition"]:
                    think.append((a, b, f"{model_name(a)}: {a['condition']} → {b['condition']}, {set_label(s)}"))
    for (fam, cond, s), ms in by_family.items():
        ms = sorted(ms, key=lambda m: family_size(m["model"])[1])
        for a, b in zip(ms, ms[1:]):
            if family_size(a["model"])[1] != family_size(b["model"])[1]:
                size.append((a, b, f"{model_name(a)} → {model_name(b)}, {cond}, {set_label(s)}"))
    key = lambda p: (set_rank(p[0]["item_set"]), run_key(p[0]), run_key(p[1]))
    return sorted(think, key=key), sorted(size, key=key)


def dumbbell(d: Data, a: dict, b: dict, title: str) -> str:
    s = a["item_set"]
    rows = []
    trows = []
    for unit in d.units_of(s):
        da = d.r["descriptive"].get(a["run_id"], {}).get(unit)
        db = d.r["descriptive"].get(b["run_id"], {}).get(unit)
        if not da or not db or not da["ok"] or not db["ok"]:
            continue
        va, vb = da["correct"] / da["ok"], db["correct"] / db["ok"]
        xa, xb = UNIT_SCALE(va), UNIT_SCALE(vb)
        tip = (f"{unit}: {a['label']} {da['correct']}/{da['ok']} ({share(da['correct'], da['ok'])}) → "
               f"{b['label']} {db['correct']}/{db['ok']} ({share(db['correct'], db['ok'])})")
        marks = [hline(min(xa, xb), max(xa, xb), "conn"), dot(xa, "ring", r=4), dot(xb, "dot")]
        lab = e(unit) + (' <span class="pill">fitted</span>' if d.is_gated(s, unit) else "")
        rows.append(row(lab, band(UNIT_SCALE, [tip_group(tip, *marks, hit_x=xb)]),
                        f"{share(da['correct'], da['ok'])} → {share(db['correct'], db['ok'])}"))
        trows.append([e(unit), num(count_share(da["correct"], da["ok"])), num(count_share(db["correct"], db["ok"])),
                      num(count_share(da["valid"], da["valid_defined"])), num(count_share(db["valid"], db["valid_defined"])),
                      num(count_share(da["any_member_match"], da["ok"])), num(count_share(db["any_member_match"], db["ok"]))])
    rows.append(axis_row(UNIT_SCALE, lambda t: f"{100 * t:.0f}%", "correct, of ok answers"))
    la, lb = e(a["label"]), e(b["label"])
    tab = table(["Unit", f"Correct: {la}", f"Correct: {lb}", f"Valid: {la}", f"Valid: {lb}",
                 f"Matches ≥1 member: {la}", f"Matches ≥1 member: {lb}"], trows)
    return (f'<article class="panel wide"><h4>{e(title)} <span class="tag-desc">descriptive</span></h4>'
            + legend([(SW_RING, a["label"]), (SW_DOT, b["label"])])
            + rowchart(rows, f"Accuracy, {title}") + details("Table: correct, valid and member matches", tab) + "</article>")


def section_compare(d: Data) -> str:
    think, size = comparison_pairs(d)
    out = ['<section id="compare"><h2>Comparisons the design supports</h2>'
           '<p class="plain"><strong>Descriptive only.</strong> Each comparison sets two runs of one model family on the same items '
           "side by side: two conditions of one model (direct against thinking, or low against high reasoning effort), and size "
           "within one family and condition. They are counts, one sample per item, with no interval and no test. Cross-model "
           "claims need one hierarchical model (DESIGN §5 rule 7), and no cross-model fit exists. Across families, model and "
           "condition change together (only Qwen3 has a direct condition; gpt-oss always reasons), so no comparison between "
           "families is shown.</p>",
           "<h3>Condition, within one model</h3>"]
    if think:
        out += [dumbbell(d, a, b, t) for a, b, t in think]
    else:
        out.append('<p class="empty">No pair yet: no model has two conditions on the same item set in this JSON.</p>')
    out.append("<h3>Size, within one family and condition</h3>")
    if size:
        out += [dumbbell(d, a, b, t) for a, b, t in size]
    else:
        out.append('<p class="empty">No pair yet: no family has two sizes in the same condition on the same item set.</p>')
    out.append("</section>")
    return "".join(out)


FRAMINGS = (("T", "textbook rule"), ("N", "neutral preamble"), ("I", "inverted rule"),
            ("I+R", "inverted, rule restated"), ("P", "half the constraints inverted"))


def section_textbook(d: Data) -> str:
    """A/H E5 by framing: correct and textbook answers per run and domain (descriptive)."""
    blocks = []
    for s in d.sets:
        units = [u for u in d.units_of(s) if u.startswith("AH_E5/")]
        rows = []
        for unit in units:
            for m in d.runs_of(s):
                bf = (d.r["descriptive"].get(m["run_id"], {}).get(unit) or {}).get("by_framing")
                if not bf:
                    continue
                cells = [e(unit.split("/", 1)[1]), e(m["label"])]
                for fr, _ in FRAMINGS:
                    c = bf.get(fr)
                    cells.append(num(f"{c['correct']} · {c['textbook']} / {c['ok']}") if c and c["ok"] else '<td class="n">–</td>')
                rows.append(cells)
        if rows:
            head = "<tr><th>Domain</th><th>Run</th>" + "".join(
                f'<th class="n">{e(fr)}<br><span class="sub">{e(name)}</span></th>' for fr, name in FRAMINGS) + "</tr>"
            blocks.append(f"<h3>{e(set_label(s))}</h3>" + table([], rows, "tt", head))
    if not blocks:
        return ""
    return ('<section id="textbook"><h2>Textbook transfer under rule inversion (A/H E5)</h2>'
            "<p>A/H E5 asks whether a model, given a familiar problem with an inverted rule, answers <em>the textbook "
            "problem</em> instead. Each base instance appears in up to five framings: T (the textbook rule), N (a neutral "
            "preamble of the same length), I (a preamble that inverts the rule), I+R (I plus the rule restated just before "
            "the question) and P (SAT only: half the constraints inverted). Each cell reads <strong>correct · textbook / "
            "ok</strong>: answers correct under the stated rule, and answers equal to the textbook problem's answer (an A3 TT "
            "member's), out of the ok answers. Under T and N the textbook answer is the correct one, so the two counts mostly "
            "coincide; under I and I+R they are disjoint by construction, so a textbook answer there is the textbook-transfer "
            "error.</p>"
            '<p class="plain"><strong>Counts, not weights.</strong> One sample per item and about 20 items per framing; the '
            "recovery gates pass for none of these units at 20 per cell except SAT (see Limits).</p>"
            + "".join(blocks) + "</section>")


def section_descriptive(d: Data) -> str:
    out = ['<section id="descriptive"><h2>Descriptive patterns on the units that are not fitted</h2>'
           '<p class="plain"><strong>Counts, not weights.</strong> On these units the recovery gates do not pass at the run\'s '
           "item size, so no mixture weight is reported (the reason for each is under Limits). The counts below say which members' "
           "answers the model gave, from the scorer's own fields; they do not say which procedure produced them. Members that "
           "match exactly the same answers are merged (A = B), and a set-valued member counts as matched only where its set has "
           "one solution.</p>"]
    for s in d.sets:
        runs = d.runs_of(s)
        units = [u for u in d.units_of(s) if not d.is_gated(s, u)]
        if not units:
            continue
        rows = []
        for unit in units:
            for m in runs:
                x = d.r["descriptive"].get(m["run_id"], {}).get(unit)
                if not x:
                    continue
                notok = ", ".join(f"{k} {v}" for k, v in x["categories"].items() if k != "ok" and v) or "–"
                top = "; ".join(f"{e(g['members'])} {g['answers']}" for g in x["members_matched"][:3]) or "–"
                spec = ", ".join(f"{e(k)} {v}" for k, v in sorted(x["special_answers"].items())) or "–"
                rows.append([e(unit), e(m["label"]), num(f"{x['ok']}/{x['n']}"), e(notok), num(count_share(x["correct"], x["ok"])),
                             num(count_share(x["valid"], x["valid_defined"])), num(count_share(x["any_member_match"], x["ok"])),
                             num(count_share(x["wrong_member_match"], x["wrong"])), top, num(spec)])
        tab = table(["Unit", "Run", "ok / responses", "Not ok", "Correct of ok", "Valid of ok", "Matches ≥1 member (of ok)",
                     "Wrong answers matching ≥1 member", "Members matched most (answers)", "Special-token answers"], rows, "desc")
        n_units = len(units)
        out.append(details(f"{e(set_label(s))}: {plural(n_units, 'unit')} not fitted, {plural(len(runs), 'run')}", tab,
                           open_=s != "dev"))
    out.append("</section>")
    return "".join(out)


def section_limits(d: Data) -> str:
    fp8 = sorted({model_name(m) for m in d.runs if "fp8" in ((m.get("provider_routing") or {}).get("quantizations") or [])})
    shared = [m for m in d.runs if (m.get("cache_twin") or {}).get("cached")]
    n_cap = sum(f.at_cap for f in d.fits)
    n_near = sum(f.nearness for f in d.fits)
    shows = ["<li><strong>Which fits pass the predictive checks against their data</strong>, and which do not "
             f"({len(d.fits) - n_near} of {len(d.fits)} do, with ε below its cap). The checks are conservative: a failure is a "
             "real misfit, a pass is weak support.</li>",
             "<li><strong>How often each model's wrong answers equal a member's wrong answer</strong>, on the gated units, against "
             "a within-cell permutation chance level where one exists.</li>",
             "<li><strong>Accuracy, validity and member-match counts</strong> on every unit and run.</li>"]
    nots = ["<li><strong>Which procedure any model runs.</strong> These are agreements between answers. Identification also "
            "needs manipulation signatures, traces or process measures (DESIGN §3 O3), and none were analysed here.</li>",
            f"<li><strong>Rates of heuristic use</strong> wherever a fit is labelled nearness, not use ({n_near} of {len(d.fits)} fits).</li>",
            "<li><strong>Any difference between model families.</strong> Model and condition change together, and no cross-model "
            "fit or paired test has been run (DESIGN §5 rule 7).</li>",
            "<li><strong>That the zoo is complete.</strong> A small π₀ does not show it: in recovery, a withheld procedure's "
            "weight went mostly onto zoo members (RECOVERY.md, Off-zoo).</li>",
            "<li><strong>Anything about the units that are not fitted</strong> beyond their counts, or about the test split or "
            "other item sizes.</li>"]
    if not any(m["condition"] == "thinking-high" for m in d.runs):
        nots.insert(2, "<li><strong>Anything about thinking at best effort</strong>, the primary condition: no thinking-high run "
                       "is in this JSON.</li>")
    caveats = [
        "<li><strong>Dev split, not the pre-registered test split.</strong> Nothing here was pre-registered: not the units, the "
        "statistics or the thresholds.</li>",
        "<li><strong>One sample per item.</strong> Run-to-run variance is not measured (DESIGN §5 rule 8)."
        + (f" {plural(len(shared), 'pilot run')} reused the paired dev run's own responses from the cache on the items the sets "
           "share, so those runs are not independent samples there." if shared else "") + "</li>",
        "<li><strong>The gates were checked at one operating point</strong> (a planted 0.6 / 0.3 / 0.1 triple, ε = 0.1, ρ = 0.3), "
        "which the real fits do not share. The recovery check at each fit's own estimate is in its panel.</li>",
        f"<li><strong>The slip rate sits at its cap in {n_cap} of {len(d.fits)} fits.</strong> The near-miss model wants more slip "
        "mass than the engine allows (EPS_MAX), so the answers miss the members more often, or by more, than the model can produce.</li>",
        "<li><strong>A weight is not a count of exact matches.</strong> π<sub>h</sub> includes h's near misses. Where no answer "
        "equals any member's, every weight on a member is near misses.</li>",
        "<li><strong>Percentile intervals are primary</strong>; BCa intervals from the same draws are in the tables. Neither is "
        "reliable on the boundary of the simplex (RECOVERY.md, Limitations): with π₀ = 1 they under-cover on C E2 knapsack, and "
        "coverage for a weight that sits at 0 was not checked.</li>",
        "<li><strong>Selection.</strong> The items are built so that members disagree. The weights describe these items, not "
        "instances at large (RECOVERY.md, Limitations).</li>",
        "<li><strong>Truncated responses are censored and excluded</strong>; the fits have no token model to correct for that.</li>",
    ]
    if any(m["condition"] == "direct" for m in d.runs):
        caveats.append("<li><strong>The direct condition's instruction conflicts with the prompts</strong>: the system message "
                       "says to answer without working, the prompts say to think as carefully as needed (RUNNER.md, Open "
                       "questions).</li>")
    if fp8:
        caveats.append(f"<li><strong>Served at fp8:</strong> {e(', '.join(fp8))}. Quantised serving may change behaviour against "
                       "the released weights (RUNNER.md, provider pins).</li>")
    why = []
    for s in d.sets:
        rows, common = [], set()
        for unit in d.units_of(s):
            if d.is_gated(s, unit):
                rows.append([e(unit), chip("good", "fitted"),
                             f"the mixture passes the three gates at {per_cell(s) or 'this'} per cell on the regenerated items"])
                continue
            reason = (d.r.get("not_fitted", {}).get(s) or {}).get(unit, "–")
            head, sep, rest = reason.partition(". At larger sizes: ")
            if sep:  # dev: one reason for every unit, then the unit's own status at larger sizes
                common.add(head)
                reason = "at larger sizes: " + rest
            rows.append([e(unit), chip("none", "descriptive only"), e(reason)])
        lead = (f'<p class="note">{e(" ".join(sorted(common)))}.</p>' if common else "")
        why.append(f"<h4>{e(set_label(s))}</h4>{lead}" + table(["Unit", "Here", "Why (docs/RECOVERY.md)"], rows, "why"))
    return ('<section id="limits"><h2>What this does and does not show</h2>'
            '<div class="two"><div><h3>What the data show</h3><ul>' + "".join(shows) + "</ul></div>"
            '<div><h3>What they do not show</h3><ul>' + "".join(nots) + "</ul></div></div>"
            '<h3>Caveats</h3><ul>' + "".join(caveats) + "</ul>"
            "<h3>Why each unit is fitted or not</h3><p>DESIGN §5 rule 12 allows mixture weights only for units and item sizes where "
            "the fake-model recovery gates pass: |bias| ≤ 0.05, 95% coverage ≥ 0.9 and median interval width ≤ 0.2, for the "
            "60/30/10 mixture with percentile intervals (docs/RECOVERY.md, “Where the gates pass”).</p>"
            + "".join(why) + "</section>")


def section_reproduce(d: Data) -> str:
    g = d.r.get("git", {})
    settings = d.r.get("settings", {})
    sets = d.r.get("item_sets", {})
    rows = []
    for s in sorted(sets, key=set_rank):
        for p in sets[s]["paths"]:
            rows.append([e(s), f"<code>{e(p)}</code>", f'<code class="hash">{e(sets[s]["sha256"][p])}</code>'])
    files = table(["Item set", "File", "sha256"], rows, "hashes")
    rrows = [[f"<code>{e(m['run_id'])}</code>", f"<code>{e(m.get('run_git_sha', '')[:10])}</code>", e(m.get("scorer_version", "")),
              f'<code class="hash">{e(m.get("scored_sha256", ""))}</code>'] for m in d.runs]
    runs = table(["Run", "Run code SHA", "Scorer", "scored.jsonl.gz sha256"], rrows, "hashes")
    sett = ", ".join(f"{e(k)} {e(str(v))}" for k, v in settings.items())
    return ('<section id="reproduce"><h2>Reproduce</h2>'
            "<p>Every number on this page comes from the JSON, except the hand-written claims under What we can say so far. Every "
            "random draw in the analysis is seeded, so a rerun reproduces the JSON.</p>"
            '<pre><code># 1. Recompute the analysis JSON and the preliminary doc\'s tables (about an hour on 6 workers)\n'
            "OMP_NUM_THREADS=1 python analysis/prelim_2026_11_18.py --runs-root data/runs --workers 6\n"
            "# 2. Rebuild this page from the JSON and docs/results/findings.html (seconds)\n"
            "python analysis/results_page.py\n"
            "python analysis/results_page.py --check   # fails if the committed page differs (a test runs this)</code></pre>"
            f'<p>The JSON was computed at commit <code>{e(g.get("sha", "?"))}</code>'
            + (" with uncommitted changes to the code" if g.get("dirty_src") else " on a clean tree")
            + f', by <code>{e(d.r.get("command", "?"))}</code>, with Python {e(str(d.r.get("python", "?")))} and numpy '
            f'{e(str(d.r.get("numpy", "?")))}. Settings: {sett}.</p>'
            + details("Item files read, with their sha256", files)
            + details("Runs: code SHA, scorer and the sha256 of the scored records", runs) + "</section>")


# =============================================================================================
# The page
# =============================================================================================


def css() -> str:
    heat_light = "".join(f"--h{k}:{c};--hi{k}:{'#ffffff' if k >= HEAT_WHITE_FROM else '#0b0b0b'};" for k, c in enumerate(HEAT))
    rev = list(reversed(HEAT))
    heat_dark = "".join(f"--h{k}:{c};--hi{k}:{'#ffffff' if (len(HEAT) - 1 - k) >= HEAT_WHITE_FROM else '#0b0b0b'};"
                        for k, c in enumerate(rev))
    heat_cls = "".join(f".h{k}{{background:var(--h{k});color:var(--hi{k})}}" for k in range(len(HEAT)))
    return CSS.replace("/*HEAT_LIGHT*/", heat_light).replace("/*HEAT_DARK*/", heat_dark).replace("/*HEAT_CLASSES*/", heat_cls)


CSS = """
:root{color-scheme:light;
--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink-2:#52514e;--muted:#898781;
--grid:#e1e0d9;--axis:#c3c2b7;--border:rgba(11,11,11,0.10);--rule:#e1e0d9;
--s1:#2a78d6;--s2:#eb6834;--wash:rgba(42,120,214,0.14);
--good:#0ca30c;--warning:#fab219;--serious:#ec835a;--critical:#d03b3b;--good-ink:#006300;
--nb0:#0d366b;--nb1:#1c5cab;--nb2:#2a78d6;--nb3:#5598e7;--nb4:#86b6ef;--nb5:#eb6834;--nb6:#c3c2b7;
/*HEAT_LIGHT*/}
@media (prefers-color-scheme:dark){:root{color-scheme:dark;
--page:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;--ink-2:#c3c2b7;--muted:#898781;
--grid:#2c2c2a;--axis:#383835;--border:rgba(255,255,255,0.10);--rule:#2c2c2a;
--s1:#3987e5;--s2:#d95926;--wash:rgba(57,135,229,0.22);--good-ink:#0ca30c;
--nb0:#cde2fb;--nb1:#9ec5f4;--nb2:#5598e7;--nb3:#256abf;--nb4:#184f95;--nb5:#d95926;--nb6:#52514e;
/*HEAT_DARK*/}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--page);color:var(--ink);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:72rem;margin:0 auto;padding:0 16px 4rem}
h1{font-size:1.6rem;line-height:1.25;margin:.25rem 0 1rem}
h2{font-size:1.3rem;margin:0 0 .75rem;padding-top:.5rem;border-top:1px solid var(--rule)}
h3{font-size:1.05rem;margin:1.75rem 0 .5rem}
h4{font-size:.95rem;margin:0 0 .4rem}
h3 .sub,h4 .sub,.lab .sub{font-weight:400;color:var(--ink-2);font-size:.85rem}
section{margin:2.5rem 0}
p,li{max-width:52rem}
a{color:var(--s1)}
code{font:.85em ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;overflow-wrap:anywhere}
pre{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:.75rem;overflow-x:auto;font-size:.85rem}
.kicker{margin:1.5rem 0 0;color:var(--ink-2);font-size:.85rem;letter-spacing:.02em}
.banner{background:var(--surface);border:1px solid var(--border);border-left:4px solid var(--warning);border-radius:6px;padding:.75rem 1rem;margin:0 0 1rem}
.toc{display:flex;flex-wrap:wrap;gap:.25rem .9rem;font-size:.85rem;margin:1rem 0 0}
.hero{display:flex;flex-wrap:wrap;align-items:baseline;gap:.25rem 1rem;margin:1.5rem 0 .5rem}
.hero-num{font-size:3rem;font-weight:650;line-height:1}
.hero-cap{font-size:1.1rem;color:var(--ink-2)}
.lead{font-size:1.05rem;background:var(--surface);border:1px solid var(--border);border-left:4px solid var(--critical);border-radius:6px;padding:.75rem 1rem;max-width:none}
.tag-near{display:inline-block;padding:0 .4rem;border-radius:4px;border:1px solid var(--serious);font-size:.9em;white-space:nowrap}
.tag-desc{display:inline-block;padding:0 .4rem;border-radius:4px;border:1px solid var(--axis);font-size:.75rem;font-weight:500;color:var(--ink-2);vertical-align:middle}
.note,.meta{color:var(--ink-2);font-size:.85rem}
.plain{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:.6rem .9rem}
.empty{color:var(--ink-2);font-style:italic}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:.5rem 0 1rem;border:1px solid var(--border);border-radius:6px;background:var(--surface)}
.scroll.fit{width:fit-content;max-width:100%}
table{border-collapse:collapse;font-size:.82rem;width:100%}
th,td{padding:.35rem .55rem;border-bottom:1px solid var(--grid);text-align:left;vertical-align:top}
th{font-weight:600;background:var(--surface)}
th.sub{font-weight:500;color:var(--ink-2);font-size:.75rem}
td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
table.runs td{white-space:nowrap}
table.desc td{min-width:4.5rem}
table.desc td:nth-child(2){white-space:nowrap}
table.desc td:nth-child(9){min-width:17rem}
table.board td{vertical-align:middle}
table.board td:nth-child(2){white-space:nowrap}
@media (max-width:40rem){
table.board thead{display:none}
table.board tr{display:block;padding:.55rem .6rem;border-bottom:1px solid var(--grid)}
table.board td{display:inline;border:0;padding:0}
table.board td:nth-child(1){font-weight:600}
table.board td:nth-child(2)::before,table.board td:nth-child(3)::before{content:" · ";color:var(--muted)}
table.board td:nth-child(4)::before{content:"";display:block;height:.35rem}}
table.why td:nth-child(2){white-space:nowrap}
.nw{white-space:nowrap}
code.hash{font-size:.75rem;word-break:break-all}
.pill{display:inline-block;font-size:.7rem;font-weight:600;padding:0 .35rem;border-radius:999px;border:1px solid var(--s1);color:var(--ink);vertical-align:1px;white-space:nowrap}
.chip{display:inline-flex;align-items:center;gap:.3rem;font-size:.78rem;line-height:1.3;padding:.1rem .5rem;border:1px solid var(--border);border-radius:999px;background:var(--surface);margin:0 .3rem .3rem 0;white-space:nowrap}
.chip .ic{font-weight:700}
.chip.good .ic{color:var(--good)}.chip.bad .ic{color:var(--critical)}.chip.warn .ic{color:var(--warning)}.chip.none .ic{color:var(--muted)}
.chip.good{border-color:color-mix(in srgb,var(--good) 55%,transparent)}
.chip.bad{border-color:color-mix(in srgb,var(--critical) 55%,transparent)}
.chip.warn{border-color:color-mix(in srgb,var(--warning) 70%,transparent)}
.strength{font-weight:600}
.strength.a::before,.strength.b::before,.strength.c::before{content:"";display:inline-block;width:.6rem;height:.6rem;border-radius:2px;margin-right:.25rem;vertical-align:0}
.strength.a::before{background:var(--good)}.strength.b::before{background:var(--serious)}.strength.c::before{background:var(--muted)}
.findings ol{padding-left:1.4rem}
.findings li{margin:0 0 .9rem}
.findings .not-yet{color:var(--ink-2);font-size:.9rem}
.panels{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,30rem),1fr));gap:1rem}
.panel{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:.8rem .9rem;min-width:0}
.panel.wide{margin:0 0 1rem}
.panel.is-near{border-top:4px solid var(--serious)}
.reading{font-size:.85rem;margin:.25rem 0 .6rem;padding:.4rem .6rem;border-radius:4px;background:var(--page)}
.reading.near{border-left:3px solid var(--serious)}
.reading.ok{border-left:3px solid var(--good)}
.chips{margin:.1rem 0 .3rem}
.legend{list-style:none;padding:0;margin:.25rem 0 .75rem;display:flex;flex-wrap:wrap;gap:.25rem 1.1rem;font-size:.8rem;color:var(--ink-2)}
.legend li{display:flex;align-items:center;gap:.35rem}
.rc{container-type:inline-size;margin:.25rem 0}
.rc-row{display:grid;grid-template-columns:minmax(0,10rem) minmax(0,1fr) minmax(0,10.5rem);grid-template-areas:"lab band val";column-gap:.75rem;align-items:center;min-height:24px}
.rc-row .lab{grid-area:lab;font-size:.8rem;line-height:1.2;overflow-wrap:anywhere;padding:2px 0}
.rc-row .bw{grid-area:band;padding:0 7px;min-width:0}
.rc-row .val{grid-area:val;font-size:.75rem;color:var(--ink-2);font-variant-numeric:tabular-nums;line-height:1.2}
.rc-row.q{border-top:1px solid var(--axis);margin-top:3px;padding-top:2px}
.rc-row.q .lab{font-style:italic}
.rc-row.axis{min-height:0}
.axis-title{font-size:.72rem;color:var(--ink-2);text-align:center}
@container (max-width:34rem){
.rc-row{grid-template-columns:minmax(0,1fr) auto;grid-template-areas:"lab val" "band band";row-gap:0;padding-bottom:3px}
.rc-row .val{text-align:right;max-width:15rem}
.rc-row.axis{grid-template-areas:"band band"}
.rc-row.axis .lab,.rc-row.axis .val{display:none}}
svg.band,svg.axis{display:block;width:100%;overflow:visible}
svg.axis text{font-size:11px;fill:var(--muted);font-variant-numeric:tabular-nums}
.g{stroke:var(--grid);stroke-width:1}
.wh{stroke:var(--s1);stroke-width:2;stroke-linecap:round}
.wh0{stroke:var(--s2);stroke-width:2;stroke-linecap:round}
.dot{fill:var(--s1);stroke:var(--surface);stroke-width:2}
.pi0{fill:var(--s2);stroke:var(--surface);stroke-width:2}
.nid{stroke:var(--muted);stroke-width:6;stroke-linecap:round;opacity:.6}
.chance{fill:none;stroke:var(--muted);stroke-width:2}
.lift,.conn{stroke:var(--axis);stroke-width:2}
.ring{fill:var(--surface);stroke:var(--s1);stroke-width:2}
.sim{fill:var(--wash)}
.simmean{stroke:var(--s1);stroke-width:2}
.obs{fill:var(--ink);stroke:var(--surface);stroke-width:2}
.obs.out{fill:var(--critical)}
.out-word{color:var(--ink);font-weight:600;white-space:nowrap}
.out-word span{color:var(--critical)}
.hit{fill:transparent}
.sep{stroke:var(--surface);stroke-width:2}
.nb0{fill:var(--nb0)}.nb1{fill:var(--nb1)}.nb2{fill:var(--nb2)}.nb3{fill:var(--nb3)}.nb4{fill:var(--nb4)}.nb5{fill:var(--nb5)}.nb6{fill:var(--nb6)}
g:hover>circle.dot,g:hover>circle.obs,g:hover>rect{opacity:.8}
table.heat{width:auto}
table.heat th,table.heat td{text-align:center;white-space:nowrap}
table.heat th.runh{font-size:.75rem;white-space:normal;min-width:6.5rem}
table.heat td.hc{font-variant-numeric:tabular-nums;min-width:3.2rem;border-bottom:2px solid var(--surface);border-right:2px solid var(--surface)}
table.heat td.na{color:var(--muted)}
.sticky{position:sticky;left:0;background:var(--surface);text-align:left!important;z-index:1;white-space:nowrap}
/*HEAT_CLASSES*/
.heat-legend{display:flex;align-items:center;gap:.4rem;font-size:.75rem;color:var(--ink-2);margin:.25rem 0}
.hs-row{display:inline-flex}.hs{display:inline-block;width:14px;height:10px}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,22rem),1fr));gap:0 2rem}
details{margin:.4rem 0 1rem}
summary{cursor:pointer;font-size:.88rem;color:var(--ink-2)}
footer{max-width:72rem;margin:0 auto;padding:1rem 16px 2rem;border-top:1px solid var(--rule);color:var(--ink-2);font-size:.8rem}
.tip{position:fixed;z-index:10;max-width:22rem;padding:.4rem .55rem;border-radius:6px;background:var(--ink);color:var(--page);font-size:.78rem;line-height:1.3;pointer-events:none;box-shadow:0 2px 8px rgba(0,0,0,.2)}
"""

SCRIPT = """
(function(){
var tip=document.createElement("div");tip.className="tip";tip.hidden=true;document.body.appendChild(tip);
document.querySelectorAll("svg g > title").forEach(function(t){t.parentNode.setAttribute("data-tip",t.textContent);t.remove();});
function at(ev){var el=ev.target.closest&&ev.target.closest("[data-tip]");if(!el){tip.hidden=true;return;}
tip.textContent=el.getAttribute("data-tip");tip.hidden=false;
var w=tip.offsetWidth,h=tip.offsetHeight,x=ev.clientX+12,y=ev.clientY+16;
if(x+w>innerWidth-8)x=Math.max(8,innerWidth-w-8);if(y+h>innerHeight-8)y=Math.max(8,ev.clientY-h-12);
tip.style.left=x+"px";tip.style.top=y+"px";}
document.addEventListener("pointermove",at);document.addEventListener("pointerdown",at);
document.addEventListener("pointerleave",function(){tip.hidden=true;});
window.addEventListener("scroll",function(){tip.hidden=true;},{passive:true});
})();
"""


def render(results: dict[str, Any], findings_html: str) -> str:
    d = Data(results)
    body = "".join([
        section_header(d), section_findings(findings_html), section_runs(d), section_accuracy(d), section_weights(d),
        section_ppc(d), section_ea(d), section_distance(d), section_compare(d), section_textbook(d), section_descriptive(d),
        section_limits(d), section_reproduce(d),
    ])
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            "<title>Heuristics Under Hardness</title>\n"
            '<meta name="description" content="Preliminary results: which heuristics LLMs use on NP-hard problems, from the '
            'mixture fits and counts of the 2026-11-18 analysis.">\n'
            f"<style>{css()}</style>\n</head>\n<body>\n<main>\n{body}\n</main>\n"
            f'<footer><p>Built by analysis/results_page.py from analysis/out/prelim_2026_11_18.json (computed at commit '
            f'<code>{e(str(results.get("git", {}).get("sha", "?"))[:10])}</code>) and docs/results/findings.html. '
            "Do not edit this file by hand.</p></footer>\n"
            f"<script>{SCRIPT}</script>\n</body>\n</html>\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", type=Path, default=JSON_IN, help="the analysis JSON")
    ap.add_argument("--findings", type=Path, default=FINDINGS, help="the hand-written claims fragment")
    ap.add_argument("--out", type=Path, default=PAGE, help="the page to write")
    ap.add_argument("--check", action="store_true", help="compare a fresh render with --out; write nothing")
    args = ap.parse_args(argv)
    page = render(json.loads(args.json.read_text()), args.findings.read_text())
    if args.check:
        if not args.out.exists() or args.out.read_text() != page:
            print(f"{args.out} differs from a fresh render of {args.json} and {args.findings}; "
                  "run python analysis/results_page.py and commit the page", file=sys.stderr)
            return 1
        print("results page matches the JSON and the findings")
        return 0
    args.out.write_text(page)
    print(f"wrote {args.out} ({len(page):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
