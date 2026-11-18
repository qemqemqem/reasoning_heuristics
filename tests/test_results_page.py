"""The results page shows the committed numbers, and labels every fit honestly.

docs/results/2026-11-18-results.html must be exactly what analysis/results_page.py renders from
analysis/out/prelim_2026_11_18.json and docs/results/findings.html, so the page is never edited by
hand or left behind when the numbers or the claims change (DESIGN §5 rule 6). The check reads only
those three files and takes seconds.
"""

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "results" / "2026-11-18-results.html"


def _page_module():
    spec = importlib.util.spec_from_file_location("results_page", REPO / "analysis" / "results_page.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclasses look their module up while the class is built
    spec.loader.exec_module(mod)
    return mod


def test_results_page_matches_the_committed_numbers():
    r = subprocess.run([sys.executable, str(REPO / "analysis" / "results_page.py"), "--check"],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, r.stdout + r.stderr


def test_results_page_loads_nothing_from_outside():
    page = PAGE.read_text()
    assert not re.search(r"<script[^>]*\bsrc=", page), "a script is loaded from a file"
    assert not re.search(r"<link\b", page), "a style sheet or other resource is linked"
    assert not re.search(r"\bsrc=[\"']?(https?:)?//", page), "an element loads a remote resource"
    assert not re.search(r"@import|url\(\s*[\"']?(https?:)?//", page), "CSS loads a remote resource"


def _fit(mod, eps, observed, sim_range, with_check=True):
    rep = {"fit": {"eps": eps}, "reach": dict(zip(("exact", "beyond_reach", "special"), observed))}
    rec = ({"simulated": {k: {"mean": (lo + hi) / 2, "p05_p95": [lo, hi]}
                          for k, (lo, hi) in zip(("exact", "beyond_reach", "special"), sim_range)}}
           if with_check else None)
    return mod.Fit("U/x", {"run_id": "r", "label": "R"}, rep, rec, 0.5)


def test_a_fit_reads_as_use_only_below_the_cap_and_inside_every_range():
    mod = _page_module()
    inside = [(0.6, 0.8), (0.0, 0.1), (0.0, 0.0)]
    ok = _fit(mod, 0.29, (0.7, 0.0, 0.0), inside)
    assert ok.reproduces and not ok.at_cap and not ok.nearness

    at_cap = _fit(mod, 0.5, (0.7, 0.0, 0.0), inside)  # reproduces the data, but ε sits at its cap
    assert at_cap.reproduces and at_cap.at_cap and at_cap.nearness

    misses = _fit(mod, 0.29, (0.2, 0.0, 0.0), inside)  # one statistic outside its 5-95% range
    assert misses.n_outside == 1 and not misses.reproduces and misses.nearness

    unchecked = _fit(mod, 0.29, (0.7, 0.0, 0.0), inside, with_check=False)  # no check run: not "use"
    assert unchecked.n_outside is None and unchecked.nearness

    shape = _fit(mod, 0.29, (0.7, 0.0, 0.0), inside)  # every statistic inside, but the distance profile misfits
    shape.rec["distance_check"] = {"p_value": 0.01}
    assert shape.n_checks == 4 and shape.n_outside == 1 and not shape.reproduces and shape.nearness
    shape.rec["distance_check"] = {"p_value": 0.2}
    assert shape.n_outside == 0 and shape.reproduces and not shape.nearness


def test_condition_pairs_cover_effort_as_well_as_thinking():
    mod = _page_module()
    runs = [{"run_id": f"r-{c}", "model": "openai/gpt-oss-20b", "condition": c, "item_set": "dev", "label": f"gpt-oss-20b {c}"}
            for c in ("thinking-high", "thinking-low")]
    runs += [{"run_id": f"q-{c}", "model": "qwen/qwen3-32b", "condition": c, "item_set": "dev", "label": f"Qwen3-32B {c}"}
             for c in ("direct", "thinking-high")]
    d = mod.Data({"runs": runs, "settings": {"eps_max": 0.5}, "gated_units": {}, "fits": {}})
    think, _ = mod.comparison_pairs(d)
    assert [(a["condition"], b["condition"]) for a, b, _ in think] == [("thinking-low", "thinking-high"), ("direct", "thinking-high")]


def test_textbook_section_shows_each_framing():
    mod = _page_module()
    runs = [{"run_id": "r", "model": "openai/gpt-oss-120b", "condition": "thinking-low", "item_set": "pc20",
             "label": "gpt-oss-120b thinking-low"}]
    bf = {"I": {"n": 20, "ok": 20, "correct": 0, "textbook": 16, "textbook_wrong": 16},
          "I+R": {"n": 20, "ok": 20, "correct": 16, "textbook": 3, "textbook_wrong": 3}}
    d = mod.Data({"runs": runs, "settings": {"eps_max": 0.5}, "gated_units": {}, "fits": {},
                  "unit_items": {"pc20": {"AH_E5/ENT": 80}}, "descriptive": {"r": {"AH_E5/ENT": {"by_framing": bf}}}})
    html = mod.section_textbook(d)
    assert "0 · 16 / 20" in html and "16 · 3 / 20" in html and html.count('<td class="n">–</td>') == 3


def test_findings_checks_match_the_committed_json():
    """The numbers the hand-written claims take from analysis/findings_checks.py are what it computes today."""
    r = subprocess.run([sys.executable, str(REPO / "analysis" / "findings_checks.py"), "--check"],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, r.stdout + r.stderr
