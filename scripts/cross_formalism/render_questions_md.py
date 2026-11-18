"""Render the cross-formalism question library (markdown) from the JSONL built by build_library.py.

    python render_questions_md.py LIB.jsonl OUT.md
"""
from __future__ import annotations

import json
import sys
from collections import Counter, OrderedDict

ENC_NAMES = OrderedDict([
    ('G', 'graph colouring, symbolic labels'), ('S', 'story: exam timetable'), ('C', 'CNF, opaque variables'),
    ('L', 'English premises, clause for clause'), ('G-PAD', 'G with long labels (tokens ≈ C)'),
    ('X', 'CNF with named atoms v37.1 (statements of C, labels of G)'), ('C-DIMACS', 'C in DIMACS notation (fewer tokens)'),
    ('C-SCRAMBLE', 'C with variable numbers permuted'), ('C-NEUTRAL', 'C + neutral header (token control)'),
    ('C-HINT', 'C + legend naming the reduction'), ('L-NEUTRAL', 'L + neutral header'), ('L-HINT', 'L + legend'),
    ('C-XORD', 'C, vertices in a different order'), ('L-XORD', 'L, vertices in a different order'),
    ('L-SW', 'switch rules in English'), ('G-GROUP', 'graph: one vertex per group, no two adjacent'),
    ('L-DNF', 'English, disjunction of conjunctions'), ('L-CNF', 'English, four clauses'),
])

EVAL_TEXT = {
    'E1': ("Witness fingerprints across four formalisms",
           "When a model solves the same 3-colouring instance as a graph, a timetable story, a CNF formula and a list of English premises, does *which* valid answer it returns (the fingerprint of the procedure) stay the same? Fingerprints are read among valid answers, so the comparison does not depend on accuracy.",
           "Encoding: G, S, C, L (same instance, same listing order and label order).",
           "Ground truth (colourable, ≥ 20 partitions); vertex listing order = first-mention order; label order = variable-index order = alphabetical order of exam names; colours 1, 2, 3 everywhere; answer format (a witness or IMPOSSIBLE)."),
    'E2': ("Length ladder",
           "Is the G → C difference a length effect (tokens or statement count) or a formalism effect? G-PAD adds tokens only; X expands every edge into per-colour clauses but keeps G's labels; C-DIMACS removes tokens from C.",
           "Encoding: G-PAD, X, C-DIMACS (G and C of the same instance are in E1).",
           "Instance, orders, answer format."),
    'E3': ("Translation dial",
           "Does making the reduction visible move the weights toward the graph profile (H-translate), or do the weights follow the surface formalism whatever the model is told (H-formalism)?",
           "Header: none (E1's C and L) / neutral / legend; variable numbering: natural / scrambled.",
           "Clauses and clause order; legend and neutral header within ±1.3% tokens of each other."),
    'E4': ("Feasibility near the threshold: dead ends and collapse",
           "Where do false IMPOSSIBLE answers come from in each formalism: first-fit dead ends (C1), unit-propagation dead ends (C2), collapse members that read the surface (POLARITY, GREEDY, FIRST, BICOND, ONL), or truncated search (D)? Does B1's drop-the-last-constraint error (false 'possible') depend on formalism?",
           "Cell (a1: FF dead end rescued by UC-DET; a2: FF and UC-DET dead ends; b: no constructive member fails; c: not colourable, last edge critical; c-twin: c minus its last edge) × encoding (G, S, C, L).",
           "Within a cell set, the instance; between c and c-twin, the encoding (truth flips with one edge)."),
    'E5': ("Backbone entailment: omission vs commission",
           "Asked whether a vertex must take a colour, does the model under-conclude (propagation only: B1 UP-k / E WP-t), over-conclude from one model (C1/C2 READ, counter-model search), or solve exactly — and does the split depend on formalism? Does the fitted propagation depth count graph hops or statement rounds?",
           "Cell (F-UP: forced, two hops of propagation; F-CASE: forced only by case analysis; F-CASE-twin: one edge removed, not forced; NF-READ: not forced, first-fit's model says yes) × encoding.",
           "Within a cell set, the instance and query; between F-CASE and its twin, the encoding."),
    'E6': ("Crossed order",
           "E1 matches vertex order across encodings. Here C and L list the vertices in a different order. Order-dependent members then predict a different canonical answer from G's; order-free members do not. The predicted drop in cross-encoding agreement checks that E1's agreement is not produced by order matching alone.",
           "Encoding: C-XORD, L-XORD (G of the same instance is in E1).",
           "Instance, label order, answer format."),
    'E7': ("Reverse direction: a SAT-native base",
           "With a random 3-SAT base, the graph rendering (pick one vertex per group, no two adjacent) is the longest encoding, reversing E1's length confound. Do variable-driven members (UC-DET, GREEDY, POLARITY; CNF-home) and group-driven members (PICK-FIRST, MCG; graph-home) trade weight by formalism?",
           "Cell (r1: group-driven members dead-end, variable-driven succeed; r2: the reverse) × encoding (C, L-SW, G-GROUP).",
           "Instance and clause order."),
    'E8': ("A logic-native gadget in three logical forms",
           "The B4/C4 E1 disjunction gadget, written as a disjunction of conjunctions (its home form), as four English clauses, and as symbolic CNF. English clauses and symbolic CNF have identical member predictions (computed), so any change between them is a pure weight shift. Between the disjunctive and clausal English forms, several members' own predictions change (MATCH, PRIMACY, ETR, ONL(2)) while FIRST's does not.",
           "Cell (M, N, U, V; DC order) × form (L-DNF, L-CNF, C).",
           "Logical content (the three forms have the same models, checked)."),
}

FP_ALIAS = [('DPLL-LIST', 'LIST'), ('DPLL-INDEX', 'LABEL'), ('DSATUR', 'DSATUR'), ('LF', 'LF'), ('GUC-DET', 'GUC'),
            ('DPLL-OCC', 'OCC'), ('UC-DET', 'UC'), ('DROP-LAST-1', 'DROP'), ('UC-DET-INDEX', 'UC-INDEX')]


def fp_label(members):
    tags = [a for m, a in FP_ALIAS if m in members]
    return "=".join(tags) if tags else members[0]


def abridge(prompt, keep_head=14, keep_tail=4):
    lines = prompt.split("\n")
    if len(lines) <= keep_head + keep_tail + 6:
        return prompt
    body_end = len(lines) - 3  # question and format lines
    head = lines[:keep_head]
    tail = lines[body_end - keep_tail:]
    return "\n".join(head + [f"… ({body_end - keep_tail - keep_head} lines omitted; full prompt in the JSONL) …"] + tail)


def canon_cell(it, rec):
    c = rec.get('canonical', rec.get('answer'))
    if isinstance(c, dict):
        if c['kind'] == 'VALID':
            for k, v in it['params']['fingerprints'].items():
                if v['colouring'] == c['colouring']:
                    return fp_label(v['members'])
            return 'valid'
        return 'invalid'
    if c == 'IMPOSSIBLE':
        return 'IMP'
    if c in ('UNIFORM-VALID',):
        return 'uniform over valid'
    if c in ('UNIFORM', 'DIST'):
        return {'UNIFORM': 'uniform', 'DIST': 'distribution'}[c]
    return str(c)


def how_mark(rec):
    h = rec.get('how', '')
    return '' if h.startswith('native') else (' ᵗ' if h == 'transported' else ' ⁿ')


def member_table(items, members):
    encs = [it['encoding'] for it in items]
    out = ["| Member (family, home) | " + " | ".join(encs) + " |", "|---|" + "---|" * len(encs)]
    for m in members:
        if m not in items[0]['predictions']:
            continue
        r0 = items[0]['predictions'][m]
        fam = f"{r0.get('family', '')}, {r0.get('home', '')}" if r0.get('family') else ''
        cells = [canon_cell(it, it['predictions'][m]) + how_mark(it['predictions'][m]) for it in items]
        out.append(f"| `{m}` ({fam}) | " + " | ".join(cells) + " |")
    return "\n".join(out)


def lr_rows(it, top=6):
    rows = []
    for obs, d in it['disconfirms'].items():
        mem = sorted(((k, v) for k, v in d.items() if not k.startswith('H-')), key=lambda kv: -kv[1])[:top]
        hs = " · ".join(f"{k} {v:+.2f}" for k, v in d.items() if k.startswith('H-'))
        rows.append(f"| {obs} | " + (", ".join(f"`{k}` {v:.1f}" for k, v in mem) or "—") + f" | {hs} |")
    return "\n".join(["| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |", "|---|---|---|"] + rows)


def set_table(it):
    sd = it.get('set_disconfirms')
    if not sd:
        return ""
    Hs = ['H-structure', 'H-formalism', 'H-translate', 'H-length', 'H-surface']
    out = ["| Joint outcome over the set | " + " | ".join(Hs) + " |", "|---|" + "---|" * len(Hs)]
    for p, d in sd.items():
        out.append(f"| {p} | " + " | ".join(f"{d[H]:.2f}" for H in Hs) + " |")
    return "\n".join(out)


MEMBERS_FIND = ['FF-LIST', 'FF-LIST-INFEAS', 'FF-LABEL', 'LF', 'DSATUR', 'DPLL-LIST', 'DPLL-LIST-b12', 'DPLL-DSATUR', 'DROP-LAST-1',
                'POLARITY', 'GREEDY-MENTION', 'UC-DET', 'UC-DET-INDEX', 'GUC-DET', 'DPLL-MENTION', 'DPLL-INDEX', 'DPLL-OCC',
                'DPLL-MENTION-b24', 'FIRST', 'BICOND', 'ONL(1)', 'ONL(64)', 'ETR', 'EXACT', 'RO-FF', 'MIN-CONFLICTS', 'WALK',
                'ALWAYS-NO', 'RANDOM', 'PERCEPTION-NOISE']
MEMBERS_MUST = ['EXACT', 'WP-1', 'WP-2', 'WP-inf', 'UP-2', 'UP-3', 'UP-4', 'UP-inf', 'FF-LIST-READ', 'DSATUR-READ', 'FF-CM', 'UC-READ',
                'UC-CM', 'GREEDY-CM', 'FIRST', 'BICOND', 'ONL(1)-reset', 'ONL(8)-reset', 'SAMPLE-3', 'ALWAYS-YES', 'ALWAYS-NO', 'ETR']


def simple_table(items, members):
    encs = [it['encoding'] for it in items]
    out = ["| Member | " + " | ".join(encs) + " |", "|---|" + "---|" * len(encs)]
    for m in members:
        if m not in items[0]['predictions']:
            continue
        cells = []
        for it in items:
            r = it['predictions'][m]
            a = r.get('answer', r.get('canonical'))
            cells.append(str(a) + how_mark(r))
        out.append(f"| `{m}` | " + " | ".join(cells) + " |")
    return "\n".join(out)


def main(lib, out):
    items = [json.loads(l) for l in open(lib)]
    by_eval = OrderedDict()
    for it in items:
        by_eval.setdefault(it['eval_id'], []).append(it)
    cnt = Counter(it['encoding'] for it in items)
    L = []
    L.append("# I — Cross-formalism question library\n")
    L.append("*Companion to [I_cross_formalism.md](I_cross_formalism.md). Machine-readable copy: "
             "[`data/examples/I_cross_formalism.jsonl`](../../data/examples/I_cross_formalism.jsonl). Built by "
             "[`scripts/cross_formalism/build_library.py`](../../scripts/cross_formalism/build_library.py) and rendered by "
             "`render_questions_md.py` in the same folder.*\n")
    L.append("## How to read this library\n")
    L.append(f"- **What is here.** {len(items)} items in {len(by_eval)} question sets (E1–E8). Every item is one encoding of one instance. "
             "`set_id` links the encodings of one instance (same ground truth); `pair_id` links counterfactual partners (truth twins, "
             "length-ladder and dial arms of a base); `encoding` names the rendering.")
    L.append("- **Items by encoding:** " + ", ".join(f"{e} {cnt[e]}" for e in ENC_NAMES if cnt[e]) + ".")
    L.append("- **Encodings.** " + "; ".join(f"**{e}** = {d}" for e, d in ENC_NAMES.items()) + ".")
    L.append("- **How everything was computed.** No value here was worked out by hand.")
    L.append("  - Colouring ground truth: enumeration of every colouring by backtracking, checked against PySAT (Glucose 4) on the direct CNF encoding. Backbone (E5) truth: enumeration, checked by PySAT with the negated query as an assumption. SAT-native truth (E7): truth table and PySAT. Gadget truth (E8): truth table, with the three logical forms checked to have the same models.")
    L.append("  - Members: reference implementations in `scripts/cross_formalism/cf_members.py` (definitions from the owning verticals). ETR: PyETR 1.0.0, computed on E8 only; on colouring-derived logic it times out from n = 6 (n = 5 took 18 s), so ETR is `n/c` there.")
    L.append("  - Tokens: o200k_base (the gpt-oss tokenizer family).")
    L.append("- **Prediction cells.** Each member's answer on each encoding, mapped to the canonical space (a colouring of the underlying graph, IMP = IMPOSSIBLE/UNSAT/NO, or YES/NO). Valid colourings are named by the members that produce them: LIST = the lexicographically first colouring in listing order (FF-LIST, UC-DET, DPLL-LIST and DPLL-MENTION when they succeed); LABEL = the same in label order; DSATUR, LF, GUC (GUC-DET), OCC (DPLL-OCC). `ᵗ` = transported (the member is not defined on this surface; its prediction is computed by translating through the reduction, which is what H-translate says the model does). Unmarked = native.")
    L.append("- **Readout is graded.** The response distribution on encoding e is Σ_h π_{h,e}·p_h(y | x_e) plus a none-of-the-above term. Hypotheses are statements about how π_{h,e} depends on e (vertical §2.2).")
    L.append("- **Sign convention.** Every likelihood ratio is a **log10 LR, positive = evidence against that theory**, relative to the theory (member, or hypothesis) that predicts the observation best. Member LRs use a 10% near-miss slip (one vertex recoloured) for deterministic members. Hypothesis LRs use the **reference profiles** of `build_library.py` (illustrative weights, not estimates) and are per single response; set-level LRs add the log-probabilities of the responses across the encodings of one instance, assuming independent responses given the hypothesis.")
    L.append("- **Hypothesis blocks.** Every item carries, for each of H-structure, H-formalism, H-translate, H-length and H-surface: (a) the predicted output on this item, (b) the pre-registered eval-level threshold, (c) the chain-of-thought prediction. Trace codes TR1–TR4 are defined in vertical §2.5; member codes K… are those of the owning verticals.\n")

    for ev in sorted(by_eval):
        its = by_eval[ev]
        title, q, varied, controlled = EVAL_TEXT[ev]
        L.append(f"## {ev}. {title}\n")
        L.append(f"- **Reasoning question.** {q}")
        L.append(f"- **Varied:** {varied}")
        L.append(f"- **Controlled:** {controlled}")
        L.append(f"- **Pre-registered eval-level predictions** (from the hypothesis blocks):")
        for H, block in its[0]['hypotheses'].items():
            if H.startswith('H-'):
                L.append(f"  - **{H}:** {block['eval_prediction']}")
        L.append("")
        sets = OrderedDict()
        for it in its:
            sets.setdefault(it['set_id'] + '|' + it['cell'], []).append(it)
        first = True
        for key, sit in sets.items():
            sid, cell = key.split('|')
            L.append(f"### {ev} · {sid} · {cell}\n")
            gt = sit[0]['ground_truth']
            gtxt = ", ".join(f"{k} = {v}" for k, v in gt.items() if k not in ('verified_by', 'check'))
            L.append(f"**Ground truth:** {gtxt} (verified by {', '.join(gt.get('verified_by', []))}).\n")
            if sit[0].get('notes'):
                L.append(f"*{sit[0]['notes']}*\n")
            toks = " · ".join(f"{it['encoding']}: {it['params'].get('prompt_tokens_o200k')} tokens, {it['params'].get('n_statements', '—')} statements" for it in sit)
            L.append(f"**Length per encoding:** {toks}.\n")
            if first:
                for it in sit:
                    L.append(f"**Prompt, {it['encoding']}** ({ENC_NAMES.get(it['encoding'], '')}):\n")
                    L.append("```\n" + abridge(it['prompt']) + "\n```\n")
                first = False
            if ev in ('E1', 'E2', 'E3', 'E4', 'E6'):
                L.append("**Predictions per encoding** (canonical answer):\n")
                L.append(member_table(sit, MEMBERS_FIND) + "\n")
            else:
                L.append("**Predictions per encoding:**\n")
                L.append(simple_table(sit, MEMBERS_MUST if ev == 'E5' else list(sit[0]['predictions'])) + "\n")
            L.append("**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):\n")
            for H in ('H-structure', 'H-formalism', 'H-translate', 'H-length', 'H-surface'):
                outs = {it['encoding']: it['hypotheses'][H]['output'] for it in sit}
                uniq = list(OrderedDict.fromkeys(outs.values()))
                if len(uniq) == 1:
                    L.append(f"- **{H}:** {uniq[0]}")
                else:
                    L.append(f"- **{H}:** " + " / ".join(f"{e}: {o}" for e, o in outs.items()))
            L.append(f"- **CoT predictions:** H-translate: {sit[0]['hypotheses']['H-translate']['cot_prediction']} H-formalism: {sit[0]['hypotheses']['H-formalism']['cot_prediction']}\n")
            st = set_table(sit[0])
            if st:
                L.append("**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):\n")
                L.append(st + "\n")
            nonref = [it for it in sit if it['encoding'] not in ('G', 'S', 'L-DNF')]
            show = (nonref or sit)[:1] if ev not in ('E4', 'E5', 'E8') else [sit[0]] + (nonref or sit[1:])[:1]
            for it in show:
                L.append(f"**Item-level evidence, {it['encoding']}** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):\n")
                L.append(lr_rows(it) + "\n")
    open(out, 'w').write("\n".join(L) + "\n")
    print('wrote', out, len(L), 'lines')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
