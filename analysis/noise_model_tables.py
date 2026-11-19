"""The tables of docs/NOISE_MODEL.md, from analysis/out/noise_model/ and the committed analysis.

    python analysis/noise_model_tables.py [analysis/out/noise_model]

M0 (the pre-registered model) is read from analysis/out/prelim_2026_11_18.json and
data/recovery/pc{20,40}.json, which this evaluation does not recompute; every other candidate from
fits_<name>.json and stage0_pc{20,40}_<name>.json. The diagnosis tables come from diagnosis.json.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parent.parent
PRELIM = REPO / "analysis" / "out" / "prelim_2026_11_18.json"
RECOVERY = {"pc20": REPO / "data" / "recovery" / "pc20.json", "pc40": REPO / "data" / "recovery" / "pc40.json"}
ORDER = ["M0", "K", "KE", "KEQ", "KEQ-h", "SEQ"]
UNITS = ["C_E2/colouring", "C_E2/knapsack", "AH_E5/SAT", "C_E5/3-SAT (partial assignment given)"]
SHORT = {"C_E2/colouring": "C E2 colouring", "C_E2/knapsack": "C E2 knapsack", "AH_E5/SAT": "A/H E5 SAT",
         "C_E5/3-SAT (partial assignment given)": "C E5 SAT, state given"}
STAGE0_UNITS = {"pc20": ["C_E2/colouring", "C_E2/knapsack", "AH_E5/SAT"], "pc40": ["C_E5/3-SAT (partial assignment given)"]}
CHECKS = ("exact", "beyond_reach", "special")
Q = "unexplained (q)"


def run_label(rid: str) -> str:
    m = rid.split("-", 4)[-1]
    return (m.replace("qwen3-", "Qwen3-").replace("gpt-oss-", "gpt-oss-").replace("-thinking-high", " thinking")
            .replace("-thinking-low", " low").replace("-direct", " direct").replace("b ", "B ").replace("Qwen3-14B", "Qwen3-14B"))


def md(header: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def load(d: Path) -> dict[str, Any]:
    prelim = json.loads(PRELIM.read_text())
    fits = {"M0": m0_fits(prelim)}
    for name in ORDER[1:]:
        p = d / f"fits_{name}.json"
        if p.exists():
            fits[name] = json.loads(p.read_text())["fits"]
    stage0 = {"M0": {s: json.loads(p.read_text()) for s, p in RECOVERY.items() if p.exists()}}
    for name in ORDER[1:]:
        got = {s: json.loads((d / f"stage0_{s}_{name}.json").read_text()) for s in ("pc20", "pc40")
               if (d / f"stage0_{s}_{name}.json").exists()}
        if got:
            stage0[name] = got
    diag = json.loads((d / "diagnosis.json").read_text()) if (d / "diagnosis.json").exists() else None
    return {"prelim": prelim, "fits": fits, "stage0": stage0, "diag": diag}


def m0_fits(prelim: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """The committed fits in this evaluation's layout."""
    out: dict[str, dict[str, Any]] = {}
    for unit, runs in prelim["fits"].items():
        out[unit] = {}
        for rid, rep in runs.items():
            rec = prelim["recovery_at_estimate"][unit][rid]
            fails = [k for k in CHECKS if not rec["simulated"][k]["p05_p95"][0] - 1e-9 <= rep["reach"][k]
                     <= rec["simulated"][k]["p05_p95"][1] + 1e-9]
            if rec.get("distance_check", {}).get("p_value", 1) < 0.05:
                fails.append("distance")
            w = {k: dict(v, bca=rep["bca"].get(k)) for k, v in rep["fit"]["weights"].items()}
            out[unit][rid] = {"fit": {"weights": w, "eps": rep["fit"]["eps"], "eps_ci": rep["fit"]["eps_ci"],
                                      "rho": rep["fit"]["rho"], "eps_at_cap": rep["fit"]["eps"] >= 0.5 - 1e-6 and
                                      rep["fit"].get("slip_identified", True), "loglik": rep["fit"]["loglik"]},
                              "recovery": rec, "ppc": {"fails": fails, "pass": not fails}, "reach": rep["reach"], "near": rep["near"]}
    return out


def targets(fits: dict[str, Any]) -> list[tuple[str, str]]:
    return [(u, r) for u in UNITS for r in sorted(fits["M0"].get(u, {}))]


def weight(rep: dict[str, Any], prefix: str) -> tuple[float, float, float] | None:
    for k, v in rep["fit"]["weights"].items():
        if k.startswith(prefix) and isinstance(v["pi"], (int, float)):
            return v["pi"], v["lo"], v["hi"]
    return None


def fmt_w(w: tuple[float, float, float] | None) -> str:
    return "–" if w is None else f"{w[0]:.2f} [{w[1]:.2f}, {w[2]:.2f}]"


# =============================================================================================
# Diagnosis
# =============================================================================================


def table_profiles(data: dict[str, Any]) -> str:
    """Observed distance profile against the M0 fit's simulated mean, and the M0 checks that fail."""
    prelim = data["prelim"]
    bins = ("0", "1", "2", "3", "4-6", ">6", "special token")
    rows = []
    for u, r in targets(data["fits"]):
        dc = prelim["recovery_at_estimate"][u][r]["distance_check"]
        cell = []
        for b in bins:
            o, m = dc["observed"][b], dc["mean"][b]
            cell.append(f"{o:.2f} / {m:.2f}" + (" ↑" if o - m > 0.05 else " ↓" if m - o > 0.05 else ""))
        rep = data["fits"]["M0"][u][r]
        rows.append([SHORT[u], run_label(r), f"{rep['fit']['eps']:.2f}", f"{rep['fit']['rho']:.2f}"] + cell +
                    [", ".join(rep["ppc"]["fails"]) or "pass"])
    return md(["Unit", "Run", "ε", "ρ"] + [f"d = {b}" if b[0].isdigit() or b[0] == ">" else "special" for b in bins] +
              ["M0 checks failed"], rows)


def table_answers(data: dict[str, Any]) -> str:
    diag = data["diag"]
    rows = []
    for u, r in targets(data["fits"]):
        a = diag["units"][u][r]["answers"]
        wrong = a["wrong"]
        nonex = wrong - a["wrong_exact_member"]
        dist = a["wrong_nonexact_distance"]
        far = sum(v for k, v in dist.items() if k == ">6" or int(k) >= 4)
        sig = ""
        if "near_wrong_adds_drops" in a:
            ad = a["near_wrong_adds_drops"]
            tot = sum(ad.values())
            sig = f"swaps (1 in, 1 out) {ad.get('1,1', 0)}/{tot}; drops only {sum(v for k, v in ad.items() if k.startswith('0,'))}/{tot}"
            if "SAT" in u:
                frac = a.get("wrong_set_fraction", {})
                sig = f"all-false {frac.get('0.0', 0)}, all-true {frac.get('1.0', 0)}"
        if "wrong_blocks" in a:
            bl = a["wrong_blocks"]
            sig = "colours used: " + ", ".join(f"{k}: {v}" for k, v in bl.items() if v >= 5)
        rows.append([SHORT[u], run_label(r), a["n"], a["correct"], wrong, a["special"], f"{nonex} ({nonex / max(wrong, 1):.0%})",
                     f"{far}", sig])
    return md(["Unit", "Run", "Answers", "Correct", "Wrong", "Special token", "Wrong, no member's answer", "of them ≥ 4 away",
               "Signature"], rows)


def table_ladder(data: dict[str, Any]) -> str:
    diag = data["diag"]
    rows = []
    cands = [c for c in ORDER if c != "M0"]
    for u, r in targets(data["fits"]):
        lad = diag["units"][u][r]["ladder"]
        base = lad["M0"]
        cells = []
        for c in cands:
            if c not in lad:
                cells.append("–")
                continue
            d_ll = lad[c]["loglik"] - base["loglik"]
            d_k = lad[c]["n_params"] - base["n_params"]
            cells.append(f"{d_ll:+.0f} ({d_k:+d})")
        rows.append([SHORT[u], run_label(r)] + cells)
    return md(["Unit", "Run"] + [f"{c}: Δlog L (Δparams)" for c in cands], rows)


# =============================================================================================
# Evaluation
# =============================================================================================


def stage0_cell(doc: dict[str, Any], unit: str) -> str:
    for ur in doc["units"]:
        if ur["unit"] == unit:
            sc = ur["scenarios"]
            parts = []
            for k in ("mix", "null_q", "null_always"):
                s = sc.get(k)
                if s is None:
                    parts.append("–")
                elif s.get("pass") is None:
                    parts.append("n/t")
                else:
                    parts.append("✓" if s["pass"] else "✗")
            return " ".join(parts)
    return "–"


def stage0_counts(docs: dict[str, Any]) -> tuple[int, int, list[str]]:
    passed, total, fails = 0, 0, []
    for size, units in STAGE0_UNITS.items():
        doc = docs.get(size)
        if doc is None:
            continue
        for ur in doc["units"]:
            if ur["unit"] not in units:
                continue
            for k in ("mix", "null_q", "null_always"):
                s = ur["scenarios"].get(k)
                if s is None or s.get("pass") is None:
                    continue
                total += 1
                passed += bool(s["pass"])
                if not s["pass"]:
                    fails.append(f"{SHORT[ur['unit']]} {k} ({s['min_coverage']:.2f} cov, {s['max_abs_bias']:.3f} bias, "
                                 f"{s['median_width']:.2f} width)")
    return passed, total, fails


def table_summary(data: dict[str, Any]) -> str:
    rows = []
    tg = targets(data["fits"])
    for c in ORDER:
        fits = data["fits"].get(c)
        if fits is None:
            continue
        reps = [fits[u][r] for u, r in tg if u in fits and r in fits[u]]
        if not reps:
            continue
        n = len(reps)
        ppc = sum(1 for x in reps if x.get("ppc", {}).get("pass"))
        cap = sum(1 for x in reps if x["fit"].get("eps_at_cap"))
        rec = sum(1 for x in reps if x.get("recovery", {}).get("pass"))
        rec_b = sum(1 for x in reps if x.get("recovery", {}).get("bca", {}).get("pass"))
        s0p, s0t, _ = stage0_counts(data["stage0"].get(c, {}))
        qm = [x["fit"]["weights"][Q]["pi"] for x in reps]
        mass = [x["mass"] for x in reps if "mass" in x] or [data["diag"]["units"][u][r]["ladder"][c]["mass"]
                                                             for u, r in tg if data["diag"] and c in data["diag"]["units"][u][r]["ladder"]]
        noise = [m["noise"] for m in mass]
        rows.append([c, n, f"{ppc}", f"{cap}", f"{rec} / {rec_b}", f"{s0p} / {s0t}" if s0t else "–",
                     f"{np.median(qm):.2f} ({min(qm):.2f}–{max(qm):.2f})",
                     f"{np.median(noise):.2f} ({min(noise):.2f}–{max(noise):.2f})" if noise else "–"])
    return md(["Model", "Fits", "Pass every predictive check", "ε at its cap", "Recovery at the estimate passes (percentile / BCa)",
               "Stage 0 scenarios passed", "π₀ (q), median (range)", "Answers put on noise (slips + q), median (range)"], rows)


def table_ppc(data: dict[str, Any]) -> str:
    rows = []
    for u, r in targets(data["fits"]):
        cells = []
        for c in ORDER:
            f = data["fits"].get(c, {}).get(u, {}).get(r)
            if f is None or "ppc" not in f:
                cells.append("–")
                continue
            mark = "pass" if f["ppc"]["pass"] else ", ".join(f["ppc"]["fails"])
            cap = " (ε cap)" if f["fit"].get("eps_at_cap") else ""
            cells.append(mark + cap)
        rows.append([SHORT[u], run_label(r)] + cells)
    return md(["Unit", "Run"] + [c for c in ORDER if c in data["fits"]], rows)


def table_stage0(data: dict[str, Any]) -> str:
    rows = []
    for size, units in STAGE0_UNITS.items():
        for u in units:
            cells = [stage0_cell(data["stage0"][c][size], u) if c in data["stage0"] and size in data["stage0"][c] else "–"
                     for c in ORDER]
            rows.append([SHORT[u], size] + cells)
    return md(["Unit", "Items per cell"] + [f"{c}: mix, null q, null always" for c in ORDER], rows)


KEY_WEIGHTS = [("C_E2/colouring", "FF-LIST", "FF-LIST (C1, list order)"), ("C_E2/colouring", "RO-FF", "RO-FF (C3)"),
               ("C_E2/colouring", "EXACT", "EXACT"), ("C_E2/knapsack", "EXACT", "EXACT"),
               ("C_E2/knapsack", "RATIO+BEST", "RATIO+BEST-SINGLE (C1)"), ("AH_E5/SAT", "exact", "exact"),
               ("AH_E5/SAT", "A3 TT[exact]", "A3 TT[exact]"), ("AH_E5/SAT", "C0 POLARITY", "C0 POLARITY"),
               ("C_E5/3-SAT (partial assignment given)", "EXACT", "EXACT"),
               ("C_E5/3-SAT (partial assignment given)", "POLARITY", "POLARITY (C0)"),
               ("C_E5/3-SAT (partial assignment given)", "ALWAYS-UNSAT", "ALWAYS-UNSAT (A1)")]


def table_weights(data: dict[str, Any], cands: list[str]) -> str:
    rows = []
    for u, prefix, label in KEY_WEIGHTS:
        for r in sorted(data["fits"]["M0"].get(u, {})):
            cells = []
            for c in cands:
                f = data["fits"].get(c, {}).get(u, {}).get(r)
                cells.append(fmt_w(weight(f, prefix)) if f else "–")
            if all(x in ("–",) or x.startswith("0.00") or x.startswith("0.01") for x in cells):
                continue
            rows.append([SHORT[u], label, run_label(r)] + cells)
    return md(["Unit", "Member", "Run"] + cands, rows)


def table_noise_params(data: dict[str, Any], c: str) -> str:
    rows = []
    fits = data["fits"].get(c, {})
    for u, r in targets(data["fits"]):
        f = fits.get(u, {}).get(r)
        if f is None:
            continue
        g = f["fit"].get("kernel")
        kern = "–" if g is None else " ".join(f"{x:.2f}" for x in g[1:7]) if f["fit"].get("kernel_cells") == "distance" else "adds/drops"
        st = f["fit"].get("state", {})
        tau = st.get("tau")
        m = f.get("mass", {})
        rows.append([SHORT[u], run_label(r), f"{f['fit']['eps']:.2f} [{f['fit']['eps_ci'][0]:.2f}, {f['fit']['eps_ci'][1]:.2f}]",
                     kern, "–" if tau is None else f"{tau:.2f}", f"{f['fit']['weights'][Q]['pi']:.2f}",
                     f"{m.get('exact', float('nan')):.2f}", f"{m.get('slip', float('nan')):.2f}", f"{m.get('q', float('nan')):.2f}"])
    return md(["Unit", "Run", "ε [95%]", "kernel g₁…g₆", "τ", "π₀", "answers: exact", "slip", "q"], rows)


def main(d: Path | str | None = None) -> int:
    d = Path(d) if d else REPO / "analysis" / "out" / "noise_model"
    data = load(d)
    out = []
    if data["diag"]:
        out += ["## Diagnosis: distance profiles (observed / M0 fit)", table_profiles(data),
                "## Diagnosis: the answers", table_answers(data), "## Likelihood ladder (point fits)", table_ladder(data)]
    out += ["## Summary", table_summary(data), "## Predictive checks", table_ppc(data), "## Stage 0", table_stage0(data),
            "## Weights", table_weights(data, [c for c in ORDER if c in data["fits"]])]
    for c in ORDER[1:]:
        if c in data["fits"]:
            out += [f"## Noise parameters: {c}", table_noise_params(data, c)]
    print("\n\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else None))
