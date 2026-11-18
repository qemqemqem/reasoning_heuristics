"""Token counts (o200k_base, the gpt-oss family tokenizer base) of sample trace lines used in
docs/theory/T1_expressivity.md section 3. Run: uv run --no-project --with tiktoken python trace_tokens.py
"""
import tiktoken
e = tiktoken.get_encoding("o200k_base")
T = lambda s: len(e.encode(s))
samples = {
 # SAT / DPLL
 "clause_cnf": "(x12 ∨ ¬x5 ∨ x33)",
 "clause_plain": "(x12 or not x5 or x33)",
 "clause_nl": "Either the lamp is on, or the door is not locked, or the fan is running.",
 "dec_terse": " x14=T;",
 "prop_terse": " c23→x3=T;",
 "conf_terse": " c41✗ ⇒ backtrack x14=F;",
 "dec_verbose": "Let's try setting x14 = True. ",
 "prop_verbose": "Clause 23 is (¬x14 ∨ x3 ∨ ¬x8): x14 is True and x8 is True, so x3 must be True. ",
 "conf_verbose": "But clause 41 is (¬x3 ∨ ¬x22 ∨ x8): x3 is True, x22 is True and x8 is False, so it is violated. Contradiction, so we backtrack and set x14 = False instead. ",
 "clause_check_line": "C17 (x4 ∨ ¬x9 ∨ x21): x4=F, x9=T, x21=T ✓\n",
 "state_line_per_var": " x14=T",
 # colouring
 "col_step_terse": " v7:B;",
 "col_step_verbose": "Vertex 7 is adjacent to 2 (Red), 5 (Green) and 11 (uncoloured), so give it Blue. ",
 "edge_check": "7-11: Blue vs Red ✓\n",
 # BP message
 "bp_msg": "C12 (lamp ∨ cat ∨ ¬door): cat leans False (0.3), door leans True (0.7), so this clause pushes lamp toward True (+0.8). ",
 "wp_msg": "C12: cat→F, door→T, so lamp must be T. ",
 # walk
 "flip_terse": " flip x9 (c17); now unsat: c3,c40;",
 "flip_verbose": "Clause 17 is violated. Flipping x9 would break clauses 3 and 40; flipping x21 breaks only clause 8, so flip x21 to True. Now the violated clauses are 8 and 52. ",
 # truth table row for entailment
 "tt_row_6atoms": "A=T B=F C=T D=T E=F F=F: P1 ✓ P2 ✓ P3 ✗ → skip\n",
 # ETR / premise update
 "premise_update": "After premise 3 (if the lamp is on then the fan is running), the remaining possibilities are {lamp, fan, ¬door} and {¬lamp, door}. ",
}
for k, s in samples.items():
    print(f"{k:22s} {T(s):4d}")
