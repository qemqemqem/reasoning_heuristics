# B4 / C4 question library (Restrict + Online)

*Companion to [B4_C4_restrict_online.md](B4_C4_restrict_online.md). Machine-readable copy: [`data/examples/B4_C4_restrict_online.jsonl`](../../data/examples/B4_C4_restrict_online.jsonl). Generated 2026-11-13.*

## How to read this library

- **What is here.** 215 items in 9 question sets, one per eval arm. Each set is a complete counterfactual set: a base item plus every cell of its design.
  - This file prints about 30 full prompts and tabulates all cells.
  - The JSONL holds every item in full: prompt, answer format, ground truth, predictions, trace predictions, hypothesis block, the `disconfirms` map, parameters.
  - `disconfirms` gives, for each possible observation, the theories whose weight it pushes toward zero. For a single sample it also gives the log-likelihood ratio against each (nats, relative to the theory that predicts that observation best).
  - Two sets (E1L, E6) use one or two base instances; the generators (vertical §2.10) produce thousands.
- **How everything was computed.** Every ground truth and prediction was computed, none by hand:
  - brute force or z3 for entailment and CSP ground truth;
  - PyETR 1.0.0 (`etr_case_generator` venv) for ETR;
  - scratch reference implementations for the other members (definitions in vertical §1.1).
  - `MM-S1` / `MM-G` are a provisional port of mental-model initial models, to be replaced by mSentential.
  - `n/c` = PyETR timed out on that cell, which is then excluded from that theory's tests.
- **Readout is graded, not binary.** A model's response distribution in a cell is P(y | cell) = Σ_h π_h · p_h(y | cell), plus residual mass.
  - Each hypothesis is a statement about the **mixture weights π_h**, which may depend on item features and on the model (strategy selection, family I).
  - p_h is h's prediction executed with a 10% slip. Rate theories (`SAMPLE-3`, `NOISY-EXACT`, `PERCEPTION-NOISE`, `RANDOM`, `HALLUC-CONSTRAINT`, `A2-ADDED-SENTENCE`) give their probability directly.
- **Every item carries a hypothesis block, per theory:**
  - **(a) output:** h's answer.
  - **(b) eval prediction:** p_h, the theory's predicted rate of the scored response in this cell (its contribution to the mixture rate is π_h·p_h), plus its predicted value Δ_h of every pre-registered contrast the cell enters, in pp, with an outcome class.
    - Outcome classes: POS ≥ +10 pp; NEG ≤ −10 pp; ZERO = within ±5 pp (TOST); WEAK otherwise.
    - Under a mixture, a contrast's expected value is Σ_h π_h Δ_h. Observed contrasts therefore constrain linear combinations of weights.
  - **(c) CoT:** the trace features predicted if h generates the trace. Codes K1–K16 are in vertical §2.6.
  - Trace evidence enters as the share of traces matching h's signature, weighted by that model's measured faithfulness.
- **Discrimination is stated as likelihood.**
  - Each set reports the expected log-likelihood ratio (nats) per replicate of the cell set: one sample per cell, for each theory against its nearest rival. Per replicate, ln 10 ≈ 2.3 nats is a 10:1 Bayes factor.
  - Each set also reports how many replicates (frames) are needed to detect π_h ≥ 0.15 against exact solving, and to bound π_h ≤ 0.10 (one-sided upper 95%) when h is absent. These come from the Fisher information for π in a two-component mixture.
  - "Disconfirming" a theory means driving its weight toward 0 with a stated bound.
- **Abbreviations:** `FST`=FIRST, `ML`=MATCH-L, `MA`=MATCH-A, `ETR`=ETR-default, `E1p`=ETR-1p, `MM`=MM-S1, `MMG`=MM-G, `MMe`=MM-elim, `BIC`=BICOND, `CWm`=CW-MIN, `CWc`=CW-COMP, `O1`=ONL(1), `O2`=ONL(2), `O4`=ONL(4), `O8`=ONL(8), `O32`=ONL(32), `O128`=ONL(128), `PRI`=PRIMACY, `REC`=RECENCY, `AFF`=AFFIRM, `YES*`=ALWAYS-YES, `NO*`=NONE, `UP1`=UP-1, `C1`=C1-GREEDY, `S3`=SAMPLE-3, `EX`=EXACT, `NX`=NOISY-EXACT, `PN`=PERCEPTION-NOISE, `RND`=RANDOM, `ETR·R1`=ETR-default-R1, `E1p·R1`=ETR-1p-R1, `ETR·R2`=ETR-default-R2, `E1p·R2`=ETR-1p-R2, `BICp`=BICOND-PRAG, `ETR0`=ETR-noissue, `MQ`=MATCH-Q, `CWd`=CW-DCA, `ADD`=ADD-CONSTRAINT, `HAL`=HALLUC-CONSTRAINT, `DROP`=DROP-LAST, `FF`=FIRST-FIT, `DSAT`=DSATUR, `OFF`=ONLINE-FIRST-FIT, `A2+`=A2-ADDED-SENTENCE, `IMP*`=ALWAYS-IMPOSSIBLE, `BICs`=BICOND-SAT, `OCL`=ONLINE-CLAUSE, `C1s`=C1-GREEDY-SAT, `UPd`=UP+DEFAULT.

## E1. Disjunction gadget: disjunct position × premise order × second-premise type × format

- **Reasoning question.** When a model endorses an illusory conclusion from a disjunction, does it select a disjunct by position (FIRST), by literal match with a categorical (MATCH), by overlap with any later premise applied premise-by-premise (ETR), or does it keep a bounded set of alternatives (ONL)? Are order effects present only where PyETR predicts them (what-follows format, not yes/no)?
- **Target members (this vertical).** FIRST, MATCH-L, MATCH-A, ETR-default, ETR-1p, MM-S1, ONL(1).
- **Competitors (other families) and nulls.** PRIMACY, RECENCY, AFFIRM, ALWAYS-YES, NONE, UP-1, C1-GREEDY, SAMPLE-3; EXACT, NOISY-EXACT, PERCEPTION-NOISE, RANDOM.
- **Varied:** P (matched disjunct first/second, by swapping disjuncts), O (disjunction first / categorical first), T (M: categorical matches; N: categorical negates; U: unrelated; V: disjunctive premise overlapping one disjunct), F (YN / MC).
- **Controlled:** token multiset identical within P and O pairs; same lexicon and probe word across T; ground truth invariant to an exclusive reading of 'or' (checked); neutral, non-causal predicates.

### Full prompts (selected cells)

**E1 / M1·DC**: ground truth: **NO**

```
Here are some statements:
1. Either the box is red and the box is heavy, or the jar is blue and the jar is cold.
2. The box is red.

Question: Does it follow that the box is heavy?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E1 / M1·CD**: ground truth: **NO**

```
Here are some statements:
1. The box is red.
2. Either the box is red and the box is heavy, or the jar is blue and the jar is cold.

Question: Does it follow that the box is heavy?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E1 / M2·DC**: ground truth: **NO**

```
Here are some statements:
1. Either the jar is blue and the jar is cold, or the box is red and the box is heavy.
2. The box is red.

Question: Does it follow that the box is heavy?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E1 / V1·DC**: ground truth: **NO**

```
Here are some statements:
1. Either the box is red and the box is heavy, or the jar is blue and the jar is cold.
2. Either the box is red, or the cup is green.

Question: Does it follow that the box is heavy?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E1 / N1·DC**: ground truth: **YES**

```
Here are some statements:
1. Either the box is red and the box is heavy, or the jar is blue and the jar is cold.
2. The box is not red.

Question: Does it follow that the jar is cold?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E1 / M1·DC·MC**: ground truth: **C**

```
Here are some statements:
1. Either the box is red and the box is heavy, or the jar is blue and the jar is cold.
2. The box is red.

Question: Which ONE of the following must be true whenever all of the statements are true?
(A) the box is heavy
(B) the jar is cold
(C) the box is heavy, or the jar is blue and the jar is cold
(D) the box is not heavy
(E) None of these

Think it through as carefully as you need. Finish with a final line of the form "ANSWER: <letter>".
```

**E1 / M1·DC·people**: ground truth: **NO**

```
Here are some statements:
1. Either Ana is at the front desk and Ana is on the phone, or Ben is in the garden and Ben is wearing gloves.
2. Ana is at the front desk.

Question: Does it follow that Ana is on the phone?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

### (a) Output hypotheses: every cell

| cell | g | FST | ML | MA | ETR | E1p | MM | MMe | MMG | BIC | CWm | CWc | O1 | O2 | O4 | PRI | REC | AFF | YES* | NO* | UP1 | C1 | S3 | EX | NX | PN | RND | ETR0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M1·DC | NO | Y | Y | Y | Y | Y | N | Y | N | N | N | N | Y | N | N | Y | N | Y | Y | N | N | Y | 0.51 | N | 0.07 | 0.00 | 0.50 | Y |
| M1·DC·MC | C | A | A | A | A | A | C | A | C | C | C | C | A | C | C | C | E | n/a | n/a | E | E | A | 0.51 | C | 0.07 | 0.03 | 0.20 | A |
| M1·CD | NO | Y | N | Y | Y | N | N | Y | N | N | N | N | Y | N | N | N | Y | Y | Y | N | N | Y | 0.51 | N | 0.07 | 0.00 | 0.50 | Y |
| M1·CD·MC | C | A | C | A | C | C | C | A | C | C | C | C | A | C | C | E | C | n/a | n/a | E | E | A | 0.51 | C | 0.07 | 0.03 | 0.20 | C |
| N1·DC | YES | X | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y |
| N1·CD | YES | X | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y |
| U1·DC | NO | Y | N | N | N | N | N | N | N | N | N | N | Y | N | N | Y | N | Y | Y | N | N | Y | 0.36 | N | 0.07 | 0.00 | 0.50 | N |
| U1·CD | NO | Y | N | N | N | N | N | N | N | N | N | N | Y | N | N | N | Y | Y | Y | N | N | Y | 0.36 | N | 0.07 | 0.00 | 0.50 | N |
| V1·DC | NO | Y | N | N | Y | Y | N | N | N | N | N | N | Y | Y | N | Y | N | Y | Y | N | N | Y | 0.42 | N | 0.07 | 0.00 | 0.50 | Y |
| V1·DC·MC | C | A | C | C | A | A | C | C | C | C | C | C | A | A | C | C | E | n/a | n/a | E | E | A | 0.42 | C | 0.07 | 0.03 | 0.20 | A |
| V1·CD | NO | Y | N | N | Y | N | N | N | N | N | N | N | Y | N | N | N | Y | Y | Y | N | N | Y | 0.42 | N | 0.07 | 0.00 | 0.50 | Y |
| V1·CD·MC | C | A | C | C | E | E | C | C | C | C | C | C | A | C | C | E | C | n/a | n/a | E | E | A | 0.42 | C | 0.07 | 0.03 | 0.20 | E |
| M2·DC | NO | N | Y | Y | Y | Y | N | Y | N | N | N | N | N | N | N | Y | N | Y | Y | N | N | Y | 0.51 | N | 0.07 | 0.00 | 0.50 | Y |
| M2·CD | NO | N | N | Y | Y | N | N | Y | N | N | N | N | N | N | N | N | Y | Y | Y | N | N | Y | 0.51 | N | 0.07 | 0.00 | 0.50 | Y |
| N2·DC | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y |
| N2·CD | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y |
| U2·DC | NO | N | N | N | N | N | N | N | N | N | N | N | N | N | N | Y | N | Y | Y | N | N | Y | 0.36 | N | 0.07 | 0.00 | 0.50 | N |
| U2·CD | NO | N | N | N | N | N | N | N | N | N | N | N | N | N | N | N | Y | Y | Y | N | N | Y | 0.36 | N | 0.07 | 0.00 | 0.50 | N |
| V2·DC | NO | N | N | N | Y | Y | N | N | N | N | N | N | N | N | N | Y | N | Y | Y | N | N | Y | 0.42 | N | 0.07 | 0.00 | 0.50 | Y |
| V2·CD | NO | N | N | N | Y | N | N | N | N | N | N | N | N | N | N | N | Y | Y | Y | N | N | Y | 0.42 | N | 0.07 | 0.00 | 0.50 | Y |
| M1·DC·people | NO | Y | Y | Y | Y | Y | N | Y | N | N | N | N | Y | N | N | Y | N | Y | Y | N | N | Y | 0.51 | N | 0.07 | 0.00 | 0.50 | Y |
| M1·CD·people | NO | Y | N | Y | Y | N | N | Y | N | N | N | N | Y | N | N | N | Y | Y | Y | N | N | Y | 0.51 | N | 0.07 | 0.00 | 0.50 | Y |
| N1·DC·people | YES | X | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y |
| V1·DC·people | NO | Y | N | N | Y | Y | N | N | N | N | N | N | Y | Y | N | Y | N | Y | Y | N | N | Y | 0.42 | N | 0.07 | 0.00 | 0.50 | Y |

MC cells: the entries are option letters. The target (scored) response is option A, the illusory conclusion. Option C is the valid strongest conclusion. E = None of these.

### (b) Eval hypotheses: pre-registered contrasts (Δ under π_h = 1, in pp)

| contrast | definition | FST | ML | MA | ETR | E1p | MM | MMe | MMG | BIC | CWm | CWc | O1 | O2 | O4 | PRI | REC | AFF | YES* | NO* | UP1 | C1 | S3 | EX | NX | PN | RND | ETR0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E1-C1 | disjunct position: mean(M1,U1) − mean(M2,U2), YN | +80 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +80 | +0 | +0 | -0 | -0 | +0 | +0 | +0 | +0 | +0 | -0 | +0 | +0 | +0 | +0 | +0 |
| E1-C2 | premise order in M cells, YN: DC − CD | -0 | +80 | +0 | +0 | +80 | +0 | +0 | +0 | +0 | +0 | +0 | -0 | +0 | +0 | +80 | -80 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 |
| E1-C3 | format × order in M1: (MC: DC − CD) − (YN: DC − CD); target = illusory option A / YES | +0 | +0 | +0 | +80 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | -80 | +80 | n/c | n/c | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +80 |
| E1-C4 | disjunctive overlap: mean(V) − mean(U), YN | +0 | +0 | +0 | +80 | +40 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +20 | +0 | -0 | -0 | +0 | +0 | +0 | +0 | +0 | +6 | +0 | +0 | +0 | +0 | +80 |
| E1-C5 | validity tracking: mean(N) − mean(M), YN (N is valid, M is not) | +0 | +40 | +0 | +0 | +40 | +80 | +0 | +80 | +80 | +80 | +80 | +20 | +80 | +80 | -0 | -0 | +0 | +0 | +0 | +80 | +0 | +49 | +80 | +86 | +94 | +0 | +0 |
| E1-C6 | order in unrelated cells U: DC − CD (surface position cue) | -0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | -0 | +0 | +0 | +80 | -80 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 |
| E1-C7 | order in N1 (disjunctive syllogism): CD − DC | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +80 | +0 | +0 | -80 | +80 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 |

**Weight sensitivity per theory.**

- Replicates of this cell set (frames × samples) needed to detect π_h ≥ 0.15 against EXACT (lower 95% bound > 0).
- Replicates needed to bound π_h ≤ 0.10 (upper 95%) if h is absent.
- The nearest rival, with the expected log-LR per replicate favouring h over it if h is true.

| theory | family | reps to detect π≥0.15 | reps to bound π≤0.10 | nearest rival (nats/rep) |
|---|---|---|---|---|
| FST | B4 | 3 | 3 | O1 (1.76) |
| ML | B4 | 12 | 10 | S3 (5.85) |
| MA | B4 | 6 | 5 | MMe (0.00) |
| ETR | B4/C4 | 4 | 3 | ETR0 (0.00) |
| E1p | B4/C4 | 6 | 5 | S3 (6.88) |
| MM | B4 | ∞ (= EXACT here) | ∞ | MMG (0.00) |
| MMe | B4 | 6 | 5 | MA (0.00) |
| MMG | B4 | ∞ (= EXACT here) | ∞ | MM (0.00) |
| BIC | B4 | ∞ (= EXACT here) | ∞ | MM (0.00) |
| CWm | B4 | ∞ (= EXACT here) | ∞ | MM (0.00) |
| CWc | B4 | ∞ (= EXACT here) | ∞ | MM (0.00) |
| O1 | C4 | 4 | 3 | FST (1.76) |
| O2 | C4 | 16 | 13 | MM (5.27) |
| O4 | C4 | ∞ (= EXACT here) | ∞ | MM (0.00) |
| PRI | A2 | 5 | 4 | RND (7.51) |
| REC | A2 | 5 | 4 | RND (7.51) |
| AFF | A2 | 4 | 3 | YES* (0.00) |
| YES* | A1 | 4 | 3 | AFF (0.00) |
| NO* | A1 | 10 | 8 | RND (7.51) |
| UP1 | B1 | ∞ (= EXACT here) | ∞ | MM (0.00) |
| C1 | C1 | 3 | 3 | AFF (0.00) |
| S3 | H | 10 | 11 | RND (3.92) |
| EX | null (exact; = D DPLL-b, E BP-t at these sizes) | — | — | MM (0.00) |
| NX | null | 683 | 1128 | MM (0.13) |
| PN | null | 79 | 142 | NX (0.46) |
| RND | null (H RANDOM) | 8 | 8 | S3 (7.22) |
| ETR0 | B4/C4 | 4 | 3 | ETR (0.00) |

### (c) CoT hypotheses (trace signature per theory)

- **FST** (FIRST, B4): K3 COMMIT to first-listed disjunct 'the box is red and the box is heavy'; second disjunct never developed; K2 absent
- **ML** (MATCH-L, B4): K4 SELECT-BY-MATCH: keeps 'the box is red and the box is heavy' because a categorical premise repeats its literal; other disjunct dropped; K2 absent
- **MA** (MATCH-A, B4): K4 SELECT-BY-MATCH: keeps 'the box is red and the box is heavy' because a categorical premise repeats its literal; other disjunct dropped; K2 absent
- **ETR** (ETR-default, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; if the first pass is inconclusive, K13 second pass from the last premise
- **E1p** (ETR-1p, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; single pass, no K13; K2 absent
- **MM** (MM-S1, B4): K1 lists only the possibilities in which the clauses are true (K12 negative-literal share ≈ 0); conditionals get one explicit case plus 'other cases' left implicit; no fully explicit truth table
- **MMe** (MM-elim, B4): as MM-S1 plus: possibilities not mentioning the categorical's literal are deleted (K4-like)
- **MMG** (MM-G, B4): as MM-S1, but a categorical premise read BEFORE a conditional makes the trace build the conditional's cases consistent with it (e.g. not-B first → builds 'not-A and not-B')
- **BIC** (BICOND, B4): no conditional; reasons as EXACT
- **CWm** (CW-MIN, B4): K6 ABSENCE→FALSE: atoms not forced true are taken to be false ('nothing says X, so X is false')
- **CWc** (CW-COMP, B4): no rules to complete; reasons as EXACT
- **O1** (ONL(1), C4): K7 strict presentation order, no back-references; K8 ≤ 1 cases kept (after 1: 2 cand. →truncated to 1; after 2: 1 cand.)
- **O2** (ONL(2), C4): K7 strict presentation order, no back-references; K8 ≤ 2 cases kept (after 1: 2 cand.; after 2: 2 cand.)
- **O4** (ONL(4), C4): K7 strict presentation order, no back-references; K8 ≤ 4 cases kept (after 1: 2 cand.; after 2: 2 cand.)
- **PRI** (PRIMACY, A2): short trace; justification quotes statement 1 only; no case enumeration
- **REC** (RECENCY, A2): short trace; justification quotes statement 2 only; no case enumeration
- **AFF** (AFFIRM, A2): no case analysis tied to the premises; answer tracks whether the conclusion is affirmative
- **YES*** (ALWAYS-YES, A1): no structure-dependent reasoning; YES regardless
- **NO*** (NONE, A1): no structure-dependent reasoning; 'cannot be determined' regardless
- **UP1** (UP-1, B1): derives only single facts by one-step propagation; no case split; NO phrased as 'cannot be determined'
- **C1** (C1-GREEDY, C1): builds ONE scenario, assigning atoms in first-mention order (true unless a statement forbids it), never backtracks; reads the answer off that scenario
- **S3** (SAMPLE-3, H): tries 1-3 example scenarios ('for instance…'), no exhaustiveness claim; YES if the examples agree
- **EX** (EXACT, null (exact; = D DPLL-b, E BP-t at these sizes)): K10 VERIFY; K2 counter-model stated (e.g. the box is red; the box is not heavy; the jar is blue; the jar is cold); answer NO
- **NX** (NOISY-EXACT, null): EXACT-style trace with one unsystematic slip (a mis-copied literal or a skipped case) at a position unrelated to disjunct order or premise order
- **PN** (PERCEPTION-NOISE, null): restatement of the premises contains a misread literal (polarity flip or swapped name), then correct reasoning on the misread problem
- **RND** (RANDOM, null (H RANDOM)): no relation between trace and answer
- **ETR0** (ETR-noissue, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; K2 absent

Cell-specific trace predictions (e.g. which disjunct is committed to, the state sizes of `ONL(k)`, the counter-model to look for) are in the JSONL `trace_predictions` field.

### Discrimination as likelihood

Theories are grouped by their predicted outcome pattern over this set's contrasts. Observing a group's pattern moves weight toward that group.

- The last column gives the smallest expected log-LR per replicate between a group member and any theory outside the group (larger = faster discrimination).
- Theories inside a group differ only at cell level, if at all; cell-level separation is in the nearest-rival column above.

| observed pattern | weight moves toward | min log-LR/rep vs outside (pair) |
|---|---|---|
| C1:POS C2:ZERO C3:ZERO C4:ZERO C5:ZERO C6:ZERO C7:ZERO | FST | 1.76 (FST vs O1) |
| C1:ZERO C2:POS C3:ZERO C4:ZERO C5:POS C6:ZERO C7:ZERO | ML | 5.85 (ML vs S3) |
| C1:ZERO C2:ZERO C3:ZERO C4:ZERO C5:ZERO C6:ZERO C7:ZERO | MA, MMe, NO*, C1, RND | 0.00 (C1 vs AFF) |
| C1:ZERO C2:ZERO C3:POS C4:POS C5:ZERO C6:ZERO C7:ZERO | ETR, ETR0 | 7.03 (ETR vs AFF) |
| C1:ZERO C2:POS C3:ZERO C4:POS C5:POS C6:ZERO C7:ZERO | E1p | 6.88 (E1p vs S3) |
| C1:ZERO C2:ZERO C3:ZERO C4:ZERO C5:POS C6:ZERO C7:ZERO | MM, MMG, BIC, CWm, CWc, O4, UP1, EX, NX, PN | 5.27 (BIC vs O2) |
| C1:POS C2:ZERO C3:ZERO C4:ZERO C5:POS C6:ZERO C7:POS | O1 | 1.76 (O1 vs FST) |
| C1:ZERO C2:ZERO C3:ZERO C4:POS C5:POS C6:ZERO C7:ZERO | O2 | 5.27 (O2 vs BIC) |
| C1:ZERO C2:POS C3:NEG C4:ZERO C5:ZERO C6:POS C7:NEG | PRI | 7.51 (PRI vs RND) |
| C1:ZERO C2:NEG C3:POS C4:ZERO C5:ZERO C6:NEG C7:POS | REC | 7.51 (REC vs RND) |
| C1:ZERO C2:ZERO C3:n/c C4:ZERO C5:ZERO C6:ZERO C7:ZERO | AFF, YES* | 0.00 (AFF vs C1) |
| C1:ZERO C2:ZERO C3:ZERO C4:WEAK C5:POS C6:ZERO C7:ZERO | S3 | 3.92 (S3 vs RND) |

Any other pattern is unexplained by a single strategy. It is fitted as a mixture: each contrast constrains Σ_h π_h Δ_h. Residual mass goes to the 'none of the above' component.

**Nearest-competitor separation (required pairs).**

For each target member: its two nearest rivals in this set, the expected log-LR per replicate, and, if that is < 0.2 nats, the sets that do separate the pair.

| target | rival | log-LR/rep here | separated in (log-LR/rep) |
|---|---|---|---|
| FST | O1 | 1.76 |  |
| FST | RND | 11.94 |  |
| ML | S3 | 5.85 |  |
| ML | MA | 7.03 |  |
| MA | MMe | 0.00 | E2 (42.2), E5 (12.3) |
| MA | S3 | 5.72 |  |
| ETR | ETR0 | 0.00 | E4 (7.0) |
| ETR | AFF | 7.03 |  |
| E1p | S3 | 6.88 |  |
| E1p | ML | 7.03 |  |
| MM | MMG | 0.00 | E2 (10.6) |
| MM | BIC | 0.00 | E1L (7.0), E2 (38.7), E5 (31.6) |
| O1 | FST | 1.76 |  |
| O1 | RND | 11.94 |  |

## E1L. Loaded entailment with a planted unique counter-model: permutation variants and a g-twin

- **Reasoning question.** On items with exactly one counter-model, is a YES (commission) predicted by whether the counter-model lies in a member's blind spot, and do permutation variants move the answer the way that member predicts?
- **Target members (this vertical).** MATCH-L, MATCH-A, ETR-default, ETR-1p, ONL(1), ONL(2), FIRST, MM-S1.
- **Competitors (other families) and nulls.** SAMPLE-3, UP-1, PRIMACY, RECENCY, C1-GREEDY, CW-MIN; EXACT, NOISY-EXACT, PERCEPTION-NOISE, RANDOM.
- **Varied:** disjunct order of every 2x2 disjunction (swap), categorical premises late vs early (early), both, and a g-twin (one literal added to a critical disjunct so the counter-model disappears and the conclusion becomes valid).
- **Controlled:** permutation variants have identical token multisets; the g-twin differs by one literal; same lexicon.

### Full prompts (selected cells)

**E1L / base1·base**: ground truth: **NO**

```
Here are some statements:
1. Either the cup is not green and the bag is wet, or the box is not red and the cup is round.
2. Either the cup is not round, or the jar is cold.
3. Either the bag is wet and the cup is round, or the jar is blue and the bag is soft.
4. Either the box is heavy and the bag is wet, or the jar is not cold and the box is red.
5. If the bag is wet, then the box is heavy.
6. The box is not red.

Question: Does it follow that the jar is cold?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E1L / base1·early**: ground truth: **NO**

```
Here are some statements:
1. The box is not red.
2. Either the cup is not green and the bag is wet, or the box is not red and the cup is round.
3. Either the cup is not round, or the jar is cold.
4. Either the bag is wet and the cup is round, or the jar is blue and the bag is soft.
5. Either the box is heavy and the bag is wet, or the jar is not cold and the box is red.
6. If the bag is wet, then the box is heavy.

Question: Does it follow that the jar is cold?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E1L / base1·swap**: ground truth: **NO**

```
Here are some statements:
1. Either the box is not red and the cup is round, or the cup is not green and the bag is wet.
2. Either the cup is not round, or the jar is cold.
3. Either the jar is blue and the bag is soft, or the bag is wet and the cup is round.
4. Either the jar is not cold and the box is red, or the box is heavy and the bag is wet.
5. If the bag is wet, then the box is heavy.
6. The box is not red.

Question: Does it follow that the jar is cold?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E1L / base1·g-twin**: ground truth: **YES**

```
Here are some statements:
1. Either the cup is not green and the bag is wet and the box is not heavy, or the box is not red and the cup is round.
2. Either the cup is not round, or the jar is cold.
3. Either the bag is wet and the cup is round, or the jar is blue and the bag is soft.
4. Either the box is heavy and the bag is wet, or the jar is not cold and the box is red.
5. If the bag is wet, then the box is heavy.
6. The box is not red.

Question: Does it follow that the jar is cold?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

### (a) Output hypotheses: every cell

| cell | g | FST | ML | MA | ETR | E1p | MM | MMG | BIC | CWm | CWc | O1 | O2 | O4 | PRI | REC | AFF | YES* | NO* | UP1 | C1 | S3 | EX | NX | PN | RND | O8 | ETR0 | MMe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base1·base | NO | X | Y | Y | Y | Y | N | N | N | N | N | N | N | N | N | N | Y | Y | N | N | Y | 0.73 | N | 0.11 | 0.05 | 0.50 | N | Y | Y |
| base1·swap | NO | X | Y | Y | Y | Y | N | N | N | N | N | Y | Y | N | N | N | Y | Y | N | N | Y | 0.73 | N | 0.11 | 0.05 | 0.50 | N | Y | Y |
| base1·early | NO | X | N | Y | Y | N | N | N | N | N | N | N | N | N | N | N | Y | Y | N | N | Y | 0.73 | N | 0.11 | 0.05 | 0.50 | N | Y | Y |
| base1·swap+early | NO | X | N | Y | Y | N | N | N | N | N | N | Y | Y | N | N | N | Y | Y | N | N | Y | 0.73 | N | 0.11 | 0.05 | 0.50 | N | Y | Y |
| base1·g-twin | YES | X | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | N | Y | N | N | Y | Y | N | N | Y | 1.00 | Y | 0.89 | 0.86 | 0.50 | Y | Y | Y |
| base5·base | NO | X | Y | Y | Y | Y | N | N | Y | Y | N | N | N | N | N | N | N | Y | N | N | Y | 0.63 | N | 0.11 | 0.05 | 0.50 | N | Y | Y |
| base5·swap | NO | Y | Y | Y | Y | Y | N | N | Y | Y | N | N | N | Y | N | N | N | Y | N | N | N | 0.63 | N | 0.11 | 0.05 | 0.50 | N | Y | Y |
| base5·early | NO | X | N | Y | Y | N | N | N | Y | Y | N | N | N | N | N | N | N | Y | N | N | Y | 0.63 | N | 0.11 | 0.05 | 0.50 | N | Y | Y |
| base5·swap+early | NO | Y | N | Y | Y | N | N | N | Y | Y | N | N | N | Y | N | N | N | Y | N | N | N | 0.63 | N | 0.11 | 0.05 | 0.50 | N | Y | Y |
| base5·g-twin | YES | X | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | N | N | Y | N | N | Y | 1.00 | Y | 0.89 | 0.92 | 0.50 | Y | Y | Y |

### (b) Eval hypotheses: pre-registered contrasts (Δ under π_h = 1, in pp)

| contrast | definition | FST | ML | MA | ETR | E1p | MM | MMG | BIC | CWm | CWc | O1 | O2 | O4 | PRI | REC | AFF | YES* | NO* | UP1 | C1 | S3 | EX | NX | PN | RND | O8 | ETR0 | MMe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E1L-C1 | disjunct swap: mean(swap, swap+early) − mean(base, early) | +40 | -0 | +0 | +0 | -0 | +0 | +0 | -0 | -0 | +0 | +40 | +40 | +40 | +0 | +0 | +0 | +0 | +0 | +0 | -40 | -0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 |
| E1L-C2 | categoricals early: mean(early, swap+early) − mean(base, swap) | +0 | -80 | +0 | +0 | -80 | +0 | +0 | -0 | -0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | -0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 |
| E1L-C3 | validity twin: g-twin − base (g flips NO → YES) | +0 | +0 | +0 | +0 | +0 | +80 | +80 | +40 | +40 | +80 | +40 | +40 | +80 | +0 | +0 | -0 | +0 | +0 | +0 | +0 | +32 | +80 | +78 | +84 | +0 | +80 | +0 | +0 |

**Weight sensitivity per theory.**

- Replicates of this cell set (frames × samples) needed to detect π_h ≥ 0.15 against EXACT (lower 95% bound > 0).
- Replicates needed to bound π_h ≤ 0.10 (upper 95%) if h is absent.
- The nearest rival, with the expected log-LR per replicate favouring h over it if h is true.

| theory | family | reps to detect π≥0.15 | reps to bound π≤0.10 | nearest rival (nats/rep) |
|---|---|---|---|---|
| FST | B4 | 12 | 10 | O4 (3.52) |
| ML | B4 | 12 | 10 | E1p (0.00) |
| MA | B4 | 6 | 5 | ETR (0.00) |
| ETR | B4/C4 | 6 | 5 | MA (0.00) |
| E1p | B4/C4 | 12 | 10 | ML (0.00) |
| MM | B4 | ∞ (= EXACT here) | ∞ | MMG (0.00) |
| MMG | B4 | ∞ (= EXACT here) | ∞ | MM (0.00) |
| BIC | B4 | 12 | 10 | CWm (0.00) |
| CWm | B4 | 12 | 10 | BIC (0.00) |
| CWc | B4 | ∞ (= EXACT here) | ∞ | MM (0.00) |
| O1 | C4 | 16 | 13 | O2 (0.00) |
| O2 | C4 | 16 | 13 | O1 (0.00) |
| O4 | C4 | 23 | 20 | NX (3.35) |
| PRI | A2 | 23 | 20 | REC (0.00) |
| REC | A2 | 23 | 20 | PRI (0.00) |
| AFF | A2 | 10 | 8 | RND (3.68) |
| YES* | A1 | 6 | 5 | MA (0.00) |
| NO* | A1 | 23 | 20 | PRI (0.00) |
| UP1 | B1 | 23 | 20 | PRI (0.00) |
| C1 | C1 | 8 | 7 | S3 (2.14) |
| S3 | H | 10 | 9 | MA (1.60) |
| EX | null (exact; = D DPLL-b, E BP-t at these sizes) | — | — | MM (0.00) |
| NX | null | 15571 | 24355 | MM (0.01) |
| PN | null | 690 | 1162 | MM (0.14) |
| RND | null (H RANDOM) | 15 | 16 | S3 (3.16) |
| O8 | C4 | ∞ (= EXACT here) | ∞ | MM (0.00) |
| ETR0 | B4/C4 | 6 | 5 | MA (0.00) |
| MMe | B4 | 6 | 5 | MA (0.00) |

### (c) CoT hypotheses (trace signature per theory)

- **FST** (FIRST, B4): K3 COMMIT to first-listed disjunct 'the cup is not green and the bag is wet', 'the cup is not round', 'the bag is wet and the cup is round', 'the box is heavy and the bag is wet'; second disjunct never developed; K2 absent; meets contradiction (K9/X)
- **ML** (MATCH-L, B4): K4 SELECT-BY-MATCH: keeps 'the box is not red and the cup is round' because a categorical premise repeats its literal; other disjunct dropped; K2 absent
- **MA** (MATCH-A, B4): K4 SELECT-BY-MATCH: keeps 'the box is not red and the cup is round' because a categorical premise repeats its literal; other disjunct dropped; K2 absent
- **ETR** (ETR-default, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; if the first pass is inconclusive, K13 second pass from the last premise; conditional read as antecedent-and-consequent given antecedent
- **E1p** (ETR-1p, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; single pass, no K13; conditional read as antecedent-and-consequent given antecedent; K2 absent
- **MM** (MM-S1, B4): K1 lists only the possibilities in which the clauses are true (K12 negative-literal share ≈ 0); conditionals get one explicit case plus 'other cases' left implicit; no fully explicit truth table; answers 'nothing follows' (NO) when only implicit cases remain
- **MMG** (MM-G, B4): as MM-S1, but a categorical premise read BEFORE a conditional makes the trace build the conditional's cases consistent with it (e.g. not-B first → builds 'not-A and not-B')
- **BIC** (BICOND, B4): K5 CONVERSE stated or used: 'if the box is heavy, then the bag is wet'
- **CWm** (CW-MIN, B4): K6 ABSENCE→FALSE: atoms not forced true are taken to be false ('nothing says X, so X is false')
- **CWc** (CW-COMP, B4): K6: listed antecedents treated as the only possible causes ('E can only come from the listed causes')
- **O1** (ONL(1), C4): K7 strict presentation order, no back-references; K8 ≤ 1 cases kept (after 1: 2 cand. →truncated to 1; after 2: 2 cand. →truncated to 1; after 3: 1 cand.; after 4: 2 cand. →truncated to 1; after 5: 1 cand.; after 6: 1 cand.)
- **O2** (ONL(2), C4): K7 strict presentation order, no back-references; K8 ≤ 2 cases kept (after 1: 2 cand.; after 2: 3 cand. →truncated to 2; after 3: 3 cand. →truncated to 2; after 4: 3 cand. →truncated to 2; after 5: 2 cand.; after 6: 1 cand.)
- **O4** (ONL(4), C4): K7 strict presentation order, no back-references; K8 ≤ 4 cases kept (after 1: 2 cand.; after 2: 3 cand.; after 3: 5 cand. →truncated to 4; after 4: 5 cand. →truncated to 4; after 5: 4 cand.; after 6: 3 cand.)
- **PRI** (PRIMACY, A2): short trace; justification quotes statement 1 only; no case enumeration
- **REC** (RECENCY, A2): short trace; justification quotes statement 6 only; no case enumeration
- **AFF** (AFFIRM, A2): no case analysis tied to the premises; answer tracks whether the conclusion is affirmative
- **YES*** (ALWAYS-YES, A1): no structure-dependent reasoning; YES regardless
- **NO*** (NONE, A1): no structure-dependent reasoning; 'cannot be determined' regardless
- **UP1** (UP-1, B1): derives only single facts by one-step propagation; no case split; NO phrased as 'cannot be determined'
- **C1** (C1-GREEDY, C1): builds ONE scenario, assigning atoms in first-mention order (true unless a statement forbids it), never backtracks; reads the answer off that scenario
- **S3** (SAMPLE-3, H): tries 1-3 example scenarios ('for instance…'), no exhaustiveness claim; YES if the examples agree
- **EX** (EXACT, null (exact; = D DPLL-b, E BP-t at these sizes)): K10 VERIFY; K2 counter-model stated (e.g. the cup is not green; the bag is wet; the box is not red; the cup is not round; the jar is not cold; the jar is blue; the bag is soft; the box is heavy); answer NO
- **NX** (NOISY-EXACT, null): EXACT-style trace with one unsystematic slip (a mis-copied literal or a skipped case) at a position unrelated to disjunct order or premise order
- **PN** (PERCEPTION-NOISE, null): restatement of the premises contains a misread literal (polarity flip or swapped name), then correct reasoning on the misread problem
- **RND** (RANDOM, null (H RANDOM)): no relation between trace and answer
- **O8** (ONL(8), C4): K7 strict presentation order, no back-references; K8 ≤ 8 cases kept (after 1: 2 cand.; after 2: 3 cand.; after 3: 5 cand.; after 4: 6 cand.; after 5: 6 cand.; after 6: 5 cand.)
- **ETR0** (ETR-noissue, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; conditional read as antecedent-and-consequent given antecedent; K2 absent
- **MMe** (MM-elim, B4): as MM-S1 plus: possibilities not mentioning the categorical's literal are deleted (K4-like)

Cell-specific trace predictions (e.g. which disjunct is committed to, the state sizes of `ONL(k)`, the counter-model to look for) are in the JSONL `trace_predictions` field.

### Discrimination as likelihood

Theories are grouped by their predicted outcome pattern over this set's contrasts. Observing a group's pattern moves weight toward that group.

- The last column gives the smallest expected log-LR per replicate between a group member and any theory outside the group (larger = faster discrimination).
- Theories inside a group differ only at cell level, if at all; cell-level separation is in the nearest-rival column above.

| observed pattern | weight moves toward | min log-LR/rep vs outside (pair) |
|---|---|---|
| C1:POS C2:ZERO C3:ZERO | FST | 3.52 (FST vs NO*) |
| C1:ZERO C2:NEG C3:ZERO | ML, E1p | 3.68 (E1p vs RND) |
| C1:ZERO C2:ZERO C3:ZERO | MA, ETR, PRI, REC, AFF, YES*, NO*, UP1, RND, ETR0, MMe | 1.29 (YES* vs S3) |
| C1:ZERO C2:ZERO C3:POS | MM, MMG, BIC, CWm, CWc, S3, EX, NX, PN, O8 | 1.60 (S3 vs YES*) |
| C1:POS C2:ZERO C3:POS | O1, O2, O4 | 3.35 (O4 vs NX) |
| C1:NEG C2:ZERO C3:ZERO | C1 | 2.14 (C1 vs S3) |

Any other pattern is unexplained by a single strategy. It is fitted as a mixture: each contrast constrains Σ_h π_h Δ_h. Residual mass goes to the 'none of the above' component.

**Nearest-competitor separation (required pairs).**

For each target member: its two nearest rivals in this set, the expected log-LR per replicate, and, if that is < 0.2 nats, the sets that do separate the pair.

| target | rival | log-LR/rep here | separated in (log-LR/rep) |
|---|---|---|---|
| ML | E1p | 0.00 | E1 (7.0), E2 (10.6), E3 (84.4) |
| ML | RND | 3.68 |  |
| MA | ETR | 0.00 | E1 (12.3), E3 (52.7), E4 (7.0) |
| MA | YES* | 0.00 | E1 (15.8), E2 (38.7), E4 (7.0), E5 (58.0) |
| ETR | MA | 0.00 | E1 (12.3), E3 (52.7), E4 (7.0) |
| ETR | YES* | 0.00 | E1 (7.0), E2 (38.7), E3 (52.7), E4 (14.1), E5 (58.0) |
| E1p | ML | 0.00 | E1 (7.0), E2 (10.6), E3 (84.4) |
| E1p | RND | 3.68 |  |
| O1 | O2 | 0.00 | E1 (21.1), E2 (35.2), E3 (17.6), E5 (17.6) |
| O1 | RND | 3.68 |  |
| O2 | O1 | 0.00 | E1 (21.1), E2 (35.2), E3 (17.6), E5 (17.6) |
| O2 | RND | 3.68 |  |
| FST | O4 | 3.52 |  |
| FST | PRI | 3.52 |  |
| MM | MMG | 0.00 | E2 (10.6) |
| MM | CWc | 0.00 | E2 (38.7) |

## E2. Conditional four-inference profile × premise order × conditional form × instruction

- **Reasoning question.** Do models read 'if' as 'iff', build only initial models, show the human premise-order effect on modus tollens (minor premise first helps), follow PyETR under either conditional rendering, or follow polarity cues?
- **Target members (this vertical).** BICOND, MM-S1, MM-G, ETR-default, ETR-1p, ETR-default-R2, ETR-1p-R2, ONL(1), CW-MIN, BICOND-PRAG.
- **Competitors (other families) and nulls.** AFFIRM, PRIMACY, RECENCY, C1-GREEDY, UP-1, SAMPLE-3; EXACT, NOISY-EXACT, PERCEPTION-NOISE, RANDOM.
- **Varied:** inference (MP, AC, DA, MT), order (conditional first / minor premise first), form (A→B, A→¬B, ¬A→B, ¬A→¬B, A↔B), instruction ('if X then Y' does not mean 'if Y then X' vs a length-matched neutral note).
- **Controlled:** same two atoms and the same word 'not' in every form; categorical premises length-matched; abstract non-causal content; neutral note in every non-instruction cell.

### Full prompts (selected cells)

**E2 / A→B·MT·cf**: ground truth: **YES**

```
Here are some statements:
1. If the box is red, then the jar is cold.
2. The jar is not cold.

Note: consider every statement before you answer.

Question: Does it follow that the box is not red?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E2 / A→B·MT·mf**: ground truth: **YES**

```
Here are some statements:
1. The jar is not cold.
2. If the box is red, then the jar is cold.

Note: consider every statement before you answer.

Question: Does it follow that the box is not red?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E2 / A↔B·MT·cf**: ground truth: **YES**

```
Here are some statements:
1. The box is red if and only if the jar is cold.
2. The jar is not cold.

Note: consider every statement before you answer.

Question: Does it follow that the box is not red?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E2 / A→B·AC·cf·instr**: ground truth: **NO**

```
Here are some statements:
1. If the box is red, then the jar is cold.
2. The jar is cold.

Note: 'if X, then Y' does not mean 'if Y, then X'.

Question: Does it follow that the box is red?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E2 / A→B·AC·cf·people**: ground truth: **NO**

```
Here are some statements:
1. If Ana is at the front desk, then Ben is in the garden.
2. Ben is in the garden.

Note: consider every statement before you answer.

Question: Does it follow that Ana is at the front desk?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

### (a) Output hypotheses: every cell

| cell | g | FST | ML | MA | MM | MMG | BIC | CWm | CWc | O1 | O2 | O4 | PRI | REC | AFF | YES* | NO* | UP1 | C1 | S3 | EX | NX | PN | RND | ETR | E1p | ETR·R2 | E1p·R2 | BICp | ETR0 | MMe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A→B·MP·cf | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y | Y | Y | Y | Y | Y |
| A→B·MP·mf | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y | Y | Y | Y | Y | Y |
| A→B·AC·cf | NO | N | N | N | Y | Y | Y | N | Y | Y | N | N | Y | N | Y | Y | N | N | Y | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | Y | Y | Y | N | Y |
| A→B·AC·mf | NO | N | N | N | Y | Y | Y | N | Y | Y | N | N | N | Y | Y | Y | N | N | Y | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | Y | N | Y | N | Y |
| A→B·DA·cf | NO | N | N | N | N | N | Y | Y | Y | N | N | N | N | N | N | Y | N | N | N | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | N | N | Y | N | N |
| A→B·DA·mf | NO | N | N | N | N | N | Y | Y | Y | N | N | N | N | N | N | Y | N | N | N | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | N | N | Y | N | N |
| A→B·MT·cf | YES | Y | Y | Y | N | N | Y | Y | Y | N | Y | Y | N | N | N | Y | N | Y | X | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y | Y | Y | Y | Y | N |
| A→B·MT·mf | YES | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | N | N | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | N | Y | N | Y | Y | N |
| A→¬B·MP·cf | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | N | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y | Y | Y | Y | Y | Y |
| A→¬B·MP·mf | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | N | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y | Y | Y | Y | Y | Y |
| A→¬B·AC·cf | NO | N | N | N | Y | Y | Y | N | N | Y | N | N | Y | N | Y | Y | N | N | Y | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | Y | Y | Y | N | Y |
| A→¬B·AC·mf | NO | N | N | N | Y | Y | Y | N | N | Y | N | N | N | Y | Y | Y | N | N | Y | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | Y | N | Y | N | Y |
| A→¬B·DA·cf | NO | N | N | N | N | N | Y | N | N | N | N | N | N | N | Y | Y | N | N | Y | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | N | N | Y | N | N |
| A→¬B·DA·mf | NO | N | N | N | N | N | Y | N | N | N | N | N | N | N | Y | Y | N | N | Y | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | N | N | Y | N | N |
| A→¬B·MT·cf | YES | Y | Y | Y | N | N | Y | Y | Y | N | Y | Y | N | N | N | Y | N | Y | X | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y | Y | Y | Y | Y | N |
| A→¬B·MT·mf | YES | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | N | N | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | N | Y | N | Y | Y | N |
| ¬A→B·MP·cf | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y | Y | Y | Y | Y | Y |
| ¬A→B·MP·mf | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y | Y | Y | Y | Y | Y |
| ¬A→B·AC·cf | NO | N | N | N | Y | Y | Y | Y | Y | Y | N | N | Y | N | N | Y | N | N | N | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | Y | Y | Y | N | Y |
| ¬A→B·AC·mf | NO | N | N | N | Y | Y | Y | Y | Y | Y | N | N | N | Y | N | Y | N | N | N | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | Y | N | Y | N | Y |
| ¬A→B·DA·cf | NO | N | N | N | N | N | Y | Y | Y | N | N | N | N | N | N | Y | N | N | N | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | N | N | Y | N | N |
| ¬A→B·DA·mf | NO | N | N | N | N | N | Y | Y | Y | N | N | N | N | N | N | Y | N | N | N | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | N | N | Y | N | N |
| ¬A→B·MT·cf | YES | Y | Y | Y | N | N | Y | Y | Y | N | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y | Y | Y | Y | Y | N |
| ¬A→B·MT·mf | YES | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | N | Y | N | Y | Y | N |
| ¬A→¬B·MP·cf | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | N | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y | Y | Y | Y | Y | Y |
| ¬A→¬B·MP·mf | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | N | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y | Y | Y | Y | Y | Y |
| ¬A→¬B·AC·cf | NO | N | N | N | Y | Y | Y | Y | N | Y | N | N | Y | N | N | Y | N | N | N | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | Y | Y | Y | N | Y |
| ¬A→¬B·AC·mf | NO | N | N | N | Y | Y | Y | Y | N | Y | N | N | N | Y | N | Y | N | N | N | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | Y | N | Y | N | Y |
| ¬A→¬B·DA·cf | NO | N | N | N | N | N | Y | N | N | N | N | N | N | N | Y | Y | N | N | Y | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | N | N | Y | N | N |
| ¬A→¬B·DA·mf | NO | N | N | N | N | N | Y | N | N | N | N | N | N | N | Y | Y | N | N | Y | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | N | N | Y | N | N |
| ¬A→¬B·MT·cf | YES | Y | Y | Y | N | N | Y | Y | Y | N | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y | Y | Y | Y | Y | N |
| ¬A→¬B·MT·mf | YES | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | N | Y | N | Y | Y | N |
| A↔B·MP·cf | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y |  |  | Y | Y | Y |
| A↔B·MP·mf | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y |  |  | Y | Y | Y |
| A↔B·AC·cf | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y |  |  | Y | Y | Y |
| A↔B·AC·mf | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y |  |  | Y | Y | Y |
| A↔B·DA·cf | YES | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | N | N | N | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y |  |  | Y | Y | Y |
| A↔B·DA·mf | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | N | N | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y |  |  | Y | Y | Y |
| A↔B·MT·cf | YES | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | N | N | N | Y | N | Y | X | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y |  |  | Y | Y | Y |
| A↔B·MT·mf | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | N | N | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y |  |  | Y | Y | Y |
| A→B·MP·cf·instr | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y | Y | Y | Y | Y | Y |
| A→B·MP·mf·instr | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y | Y | Y | Y | Y | Y |
| A→B·AC·cf·instr | NO | N | N | N | Y | Y | Y | N | Y | Y | N | N | Y | N | Y | Y | N | N | Y | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | Y | Y | N | N | Y |
| A→B·AC·mf·instr | NO | N | N | N | Y | Y | Y | N | Y | Y | N | N | N | Y | Y | Y | N | N | Y | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | Y | N | N | N | Y |
| A→B·DA·cf·instr | NO | N | N | N | N | N | Y | Y | Y | N | N | N | N | N | N | Y | N | N | N | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | N | N | N | N | N |
| A→B·DA·mf·instr | NO | N | N | N | N | N | Y | Y | Y | N | N | N | N | N | N | Y | N | N | N | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | N | N | N | N | N |
| A→B·MT·cf·instr | YES | Y | Y | Y | N | N | Y | Y | Y | N | Y | Y | N | N | N | Y | N | Y | X | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y | Y | Y | Y | Y | N |
| A→B·MT·mf·instr | YES | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | N | N | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | N | Y | N | Y | Y | N |
| A→B·AC·cf·people | NO | N | N | N | Y | Y | Y | N | Y | Y | N | N | Y | N | Y | Y | N | N | Y | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | Y | Y | Y | N | Y |
| A→B·AC·mf·people | NO | N | N | N | Y | Y | Y | N | Y | Y | N | N | N | Y | Y | Y | N | N | Y | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | Y | N | Y | N | Y |
| A→B·MT·cf·people | YES | Y | Y | Y | N | N | Y | Y | Y | N | Y | Y | N | N | N | Y | N | Y | X | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | Y | Y | Y | Y | Y | N |
| A→B·MT·mf·people | YES | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | N | N | Y | N | Y | Y | 1.00 | Y | 0.93 | 0.94 | 0.50 | Y | N | Y | N | Y | Y | N |

### (b) Eval hypotheses: pre-registered contrasts (Δ under π_h = 1, in pp)

| contrast | definition | FST | ML | MA | MM | MMG | BIC | CWm | CWc | O1 | O2 | O4 | PRI | REC | AFF | YES* | NO* | UP1 | C1 | S3 | EX | NX | PN | RND | ETR | E1p | ETR·R2 | E1p·R2 | BICp | ETR0 | MMe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E2-C1 | MT order: mean over the four "if" forms of MT·mf − MT·cf | +0 | +0 | +0 | +0 | +80 | +0 | +0 | +0 | +80 | +0 | +0 | +0 | +0 | -0 | +0 | +0 | +0 | +40 | +0 | +0 | +0 | -0 | +0 | +0 | -80 | +0 | -80 | +0 | +0 | +0 |
| E2-C2 | "iff" order on DA and MT: mf − cf | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +80 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +40 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | n/c | n/c | +0 | +0 | +0 |
| E2-C3 | AC − DA over the four "if" forms, both orders | +0 | +0 | +0 | +80 | +80 | +0 | +0 | +0 | +80 | +0 | +0 | +40 | +40 | -0 | +0 | +0 | +0 | -0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +80 | +40 | +0 | +0 | +80 |
| E2-C4 | fallacy polarity: AC/DA cells with an affirmative probe − with a negated probe | +0 | +0 | +0 | -0 | -0 | +0 | -80 | -40 | -0 | +0 | +0 | -0 | +0 | +80 | +0 | +0 | +0 | +80 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | -0 | -0 | +0 | +0 | -0 |
| E2-C5 | "iff" − "if" on AC and DA (A→B) | +80 | +80 | +80 | +40 | +40 | +0 | +40 | +0 | +20 | +80 | +80 | +0 | +0 | +0 | +0 | +0 | +80 | +40 | +88 | +80 | +86 | +94 | +0 | +80 | +80 | n/c | n/c | +0 | +80 | +40 |
| E2-C6 | instruction effect on AC and DA (A→B): instruction − neutral note | +0 | +0 | +0 | +0 | +0 | +0 | -0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | -80 | +0 | +0 |
| E2-C7 | MT − MP, "if" forms, conditional first | +0 | +0 | +0 | -80 | -80 | +0 | +0 | +0 | -80 | +0 | +0 | -80 | +0 | -0 | +0 | +0 | +0 | -40 | +0 | +0 | +0 | -0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | -80 |

**Weight sensitivity per theory.**

- Replicates of this cell set (frames × samples) needed to detect π_h ≥ 0.15 against EXACT (lower 95% bound > 0).
- Replicates needed to bound π_h ≤ 0.10 (upper 95%) if h is absent.
- The nearest rival, with the expected log-LR per replicate favouring h over it if h is true.

| theory | family | reps to detect π≥0.15 | reps to bound π≤0.10 | nearest rival (nats/rep) |
|---|---|---|---|---|
| FST | B4 | ∞ (= EXACT here) | ∞ | ML (0.00) |
| ML | B4 | ∞ (= EXACT here) | ∞ | FST (0.00) |
| MA | B4 | ∞ (= EXACT here) | ∞ | FST (0.00) |
| MM | B4 | 2 | 2 | MMe (0.00) |
| MMG | B4 | 3 | 3 | O1 (3.52) |
| BIC | B4 | 3 | 2 | YES* (0.00) |
| CWm | B4 | 5 | 4 | CWc (14.06) |
| CWc | B4 | 4 | 3 | BIC (14.06) |
| O1 | C4 | 3 | 2 | MMG (3.52) |
| O2 | C4 | ∞ (= EXACT here) | ∞ | FST (0.00) |
| O4 | C4 | ∞ (= EXACT here) | ∞ | FST (0.00) |
| PRI | A2 | 2 | 2 | RND (19.14) |
| REC | A2 | 2 | 2 | RND (19.14) |
| AFF | A2 | 2 | 2 | RND (19.14) |
| YES* | A1 | 3 | 2 | BIC (0.00) |
| NO* | A1 | 2 | 2 | RND (19.14) |
| UP1 | B1 | ∞ (= EXACT here) | ∞ | FST (0.00) |
| C1 | C1 | 3 | 3 | RND (19.14) |
| S3 | H | 44 | 79 | NX (1.14) |
| EX | null (exact; = D DPLL-b, E BP-t at these sizes) | — | — | FST (0.00) |
| NX | null | 316 | 521 | FST (0.29) |
| PN | null | 51 | 91 | NX (0.61) |
| RND | null (H RANDOM) | 3 | 3 | ETR·R2 (22.48) |
| ETR | B4/C4 | ∞ (= EXACT here) | ∞ | FST (0.00) |
| E1p | B4/C4 | 8 | 7 | FST (10.55) |
| ETR·R2 | B4/C4 | 4 | 4 | MMG (10.55) |
| E1p·R2 | B4/C4 | 4 | 4 | E1p (10.55) |
| BICp | B4 | 3 | 3 | BIC (7.03) |
| ETR0 | B4/C4 | ∞ (= EXACT here) | ∞ | FST (0.00) |
| MMe | B4 | 2 | 2 | MM (0.00) |

### (c) CoT hypotheses (trace signature per theory)

- **FST** (FIRST, B4): no disjunction to commit on; reasons as EXACT
- **ML** (MATCH-L, B4): no disjunct selected (no categorical premise later than a disjunction); reasons as EXACT
- **MA** (MATCH-A, B4): no disjunct selected (no categorical premise sharing a literal with a disjunction); reasons as EXACT
- **MM** (MM-S1, B4): K1 lists only the possibilities in which the clauses are true (K12 negative-literal share ≈ 0); conditionals get one explicit case plus 'other cases' left implicit; no fully explicit truth table; answers 'nothing follows' (NO) when only implicit cases remain
- **MMG** (MM-G, B4): as MM-S1, but a categorical premise read BEFORE a conditional makes the trace build the conditional's cases consistent with it (e.g. not-B first → builds 'not-A and not-B')
- **BIC** (BICOND, B4): K5 CONVERSE stated or used: 'if the jar is cold, then the box is red'
- **CWm** (CW-MIN, B4): K6 ABSENCE→FALSE: atoms not forced true are taken to be false ('nothing says X, so X is false')
- **CWc** (CW-COMP, B4): K6: listed antecedents treated as the only possible causes ('E can only come from the listed causes')
- **O1** (ONL(1), C4): K7 strict presentation order, no back-references; K8 ≤ 1 cases kept (after 1: 2 cand. →truncated to 1; after 2: 1 cand. →RESET)
- **O2** (ONL(2), C4): K7 strict presentation order, no back-references; K8 ≤ 2 cases kept (after 1: 2 cand.; after 2: 1 cand.)
- **O4** (ONL(4), C4): K7 strict presentation order, no back-references; K8 ≤ 4 cases kept (after 1: 2 cand.; after 2: 1 cand.)
- **PRI** (PRIMACY, A2): short trace; justification quotes statement 1 only; no case enumeration
- **REC** (RECENCY, A2): short trace; justification quotes statement 2 only; no case enumeration
- **AFF** (AFFIRM, A2): no case analysis tied to the premises; answer tracks whether the conclusion is affirmative
- **YES*** (ALWAYS-YES, A1): no structure-dependent reasoning; YES regardless
- **NO*** (NONE, A1): no structure-dependent reasoning; 'cannot be determined' regardless
- **UP1** (UP-1, B1): derives only single facts by one-step propagation; no case split; NO phrased as 'cannot be determined'
- **C1** (C1-GREEDY, C1): builds ONE scenario, assigning atoms in first-mention order (true unless a statement forbids it), never backtracks; reads the answer off that scenario
- **S3** (SAMPLE-3, H): tries 1-3 example scenarios ('for instance…'), no exhaustiveness claim; YES if the examples agree
- **EX** (EXACT, null (exact; = D DPLL-b, E BP-t at these sizes)): K10 VERIFY; every case considered; no counter-model exists; answer YES
- **NX** (NOISY-EXACT, null): EXACT-style trace with one unsystematic slip (a mis-copied literal or a skipped case) at a position unrelated to disjunct order or premise order
- **PN** (PERCEPTION-NOISE, null): restatement of the premises contains a misread literal (polarity flip or swapped name), then correct reasoning on the misread problem
- **RND** (RANDOM, null (H RANDOM)): no relation between trace and answer
- **ETR** (ETR-default, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; if the first pass is inconclusive, K13 second pass from the last premise; conditional read as antecedent-and-consequent given antecedent
- **E1p** (ETR-1p, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; single pass, no K13; conditional read as antecedent-and-consequent given antecedent
- **ETR·R2** (ETR-default-R2, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; if the first pass is inconclusive, K13 second pass from the last premise; conditional read as antecedent-and-consequent given antecedent
- **E1p·R2** (ETR-1p-R2, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; single pass, no K13; conditional read as antecedent-and-consequent given antecedent
- **BICp** (BICOND-PRAG, B4): K11 READING: 'if' taken as 'if and only if' by default; with the explicit instruction, reasons as EXACT
- **ETR0** (ETR-noissue, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; conditional read as antecedent-and-consequent given antecedent
- **MMe** (MM-elim, B4): as MM-S1 plus: possibilities not mentioning the categorical's literal are deleted (K4-like)

Cell-specific trace predictions (e.g. which disjunct is committed to, the state sizes of `ONL(k)`, the counter-model to look for) are in the JSONL `trace_predictions` field.

### Discrimination as likelihood

Theories are grouped by their predicted outcome pattern over this set's contrasts. Observing a group's pattern moves weight toward that group.

- The last column gives the smallest expected log-LR per replicate between a group member and any theory outside the group (larger = faster discrimination).
- Theories inside a group differ only at cell level, if at all; cell-level separation is in the nearest-rival column above.

| observed pattern | weight moves toward | min log-LR/rep vs outside (pair) |
|---|---|---|
| C1:ZERO C2:ZERO C3:ZERO C4:ZERO C5:POS C6:ZERO C7:ZERO | FST, ML, MA, O2, O4, UP1, S3, EX, NX, PN, ETR, ETR0 | 10.55 (ETR vs E1p) |
| C1:ZERO C2:ZERO C3:POS C4:ZERO C5:POS C6:ZERO C7:NEG | MM, MMe | 10.55 (MM vs MMG) |
| C1:POS C2:ZERO C3:POS C4:ZERO C5:POS C6:ZERO C7:NEG | MMG | 3.52 (MMG vs O1) |
| C1:ZERO C2:ZERO C3:ZERO C4:ZERO C5:ZERO C6:ZERO C7:ZERO | BIC, YES*, NO*, RND | 7.03 (YES* vs BICp) |
| C1:ZERO C2:ZERO C3:ZERO C4:NEG C5:POS C6:ZERO C7:ZERO | CWm | 14.06 (CWm vs CWc) |
| C1:ZERO C2:ZERO C3:ZERO C4:NEG C5:ZERO C6:ZERO C7:ZERO | CWc | 14.06 (CWc vs YES*) |
| C1:POS C2:POS C3:POS C4:ZERO C5:POS C6:ZERO C7:NEG | O1 | 3.52 (O1 vs MMG) |
| C1:ZERO C2:ZERO C3:POS C4:ZERO C5:ZERO C6:ZERO C7:NEG | PRI | 19.14 (PRI vs RND) |
| C1:ZERO C2:ZERO C3:POS C4:ZERO C5:ZERO C6:ZERO C7:ZERO | REC | 19.14 (REC vs RND) |
| C1:ZERO C2:ZERO C3:ZERO C4:POS C5:ZERO C6:ZERO C7:ZERO | AFF | 19.14 (AFF vs RND) |
| C1:POS C2:POS C3:ZERO C4:POS C5:POS C6:ZERO C7:NEG | C1 | 19.14 (C1 vs RND) |
| C1:NEG C2:ZERO C3:ZERO C4:ZERO C5:POS C6:ZERO C7:ZERO | E1p | 10.55 (E1p vs E1p·R2) |
| C1:ZERO C2:n/c C3:POS C4:ZERO C5:n/c C6:ZERO C7:ZERO | ETR·R2 | 10.55 (ETR·R2 vs MMG) |
| C1:NEG C2:n/c C3:POS C4:ZERO C5:n/c C6:ZERO C7:ZERO | E1p·R2 | 10.55 (E1p·R2 vs E1p) |
| C1:ZERO C2:ZERO C3:ZERO C4:ZERO C5:ZERO C6:NEG C7:ZERO | BICp | 7.03 (BICp vs YES*) |

Any other pattern is unexplained by a single strategy. It is fitted as a mixture: each contrast constrains Σ_h π_h Δ_h. Residual mass goes to the 'none of the above' component.

**Nearest-competitor separation (required pairs).**

For each target member: its two nearest rivals in this set, the expected log-LR per replicate, and, if that is < 0.2 nats, the sets that do separate the pair.

| target | rival | log-LR/rep here | separated in (log-LR/rep) |
|---|---|---|---|
| BIC | YES* | 0.00 | E1 (26.4), E1L (7.0), E5 (14.1) |
| BIC | BICp | 7.03 |  |
| MM | MMe | 0.00 | E1 (14.1), E1L (14.1) |
| MM | MMG | 10.55 |  |
| MMG | O1 | 3.52 |  |
| MMG | MM | 10.55 |  |
| ETR | FST | 0.00 | E1 (19.3), E1L (14.1), E3 (31.6), E5 (8.8) |
| ETR | ML | 0.00 | E1 (15.8), E1L (7.0), E3 (52.7) |
| E1p | FST | 10.55 |  |
| E1p | ML | 10.55 |  |
| ETR·R2 | MMG | 10.55 |  |
| ETR·R2 | O1 | 10.55 |  |
| E1p·R2 | E1p | 10.55 |  |
| E1p·R2 | RND | 16.19 |  |
| O1 | MMG | 3.52 |  |
| O1 | ETR·R2 | 10.55 |  |
| CWm | CWc | 14.06 |  |
| CWm | FST | 17.58 |  |
| BICp | BIC | 7.03 |  |
| BICp | YES* | 7.03 |  |

## E3. Online capacity: anchored disjunction chains (width × order × probe side × size)

- **Reasoning question.** Does the model keep a bounded set of alternatives while reading premises in order? Accuracy should fall with chain width (inclusive chains) only when the anchors come late, and not for exclusive chains of the same length.
- **Target members (this vertical).** ONL(1), ONL(2), ONL(8), ONL(32), ONL(128), ETR-default, ETR-1p.
- **Competitors (other families) and nulls.** PRIMACY, RECENCY, UP-1, MM-S1, C1-GREEDY, FIRST; EXACT, NOISY-EXACT, PERCEPTION-NOISE, RANDOM.
- **Varied:** m (3,5,8,12,16 links), W (inclusive 'at least one' = width Fib(m+2); exclusive 'exactly one' = width 2), O (anchors late / early / just-in-time), probe side (near / far end).
- **Controlled:** inclusive and exclusive premises differ by one word; the same anchors and probe in every W and O cell; propagation depth from anchor to probe is 1 in every cell; lamp names, no digits.

### Full prompts (selected cells)

**E3 / m8·incl·late·far**: ground truth: **YES**

```
Here are some statements:
1. At least one of these lamps is on: the Alder lamp, the Birch lamp.
2. At least one of these lamps is on: the Birch lamp, the Cedar lamp.
3. At least one of these lamps is on: the Cedar lamp, the Elm lamp.
4. At least one of these lamps is on: the Elm lamp, the Fir lamp.
5. At least one of these lamps is on: the Fir lamp, the Hazel lamp.
6. At least one of these lamps is on: the Hazel lamp, the Juniper lamp.
7. At least one of these lamps is on: the Juniper lamp, the Larch lamp.
8. At least one of these lamps is on: the Larch lamp, the Maple lamp.
9. The Alder lamp is not on.
10. The Cedar lamp is not on.
11. The Fir lamp is not on.
12. The Juniper lamp is not on.
13. The Maple lamp is not on.

Question: Does it follow that the Larch lamp is on?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. If the statements contradict each other, finish with "ANSWER: CONTRADICTORY". Otherwise finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E3 / m8·excl·late·far**: ground truth: **YES**

```
Here are some statements:
1. Exactly one of these lamps is on: the Alder lamp, the Birch lamp.
2. Exactly one of these lamps is on: the Birch lamp, the Cedar lamp.
3. Exactly one of these lamps is on: the Cedar lamp, the Elm lamp.
4. Exactly one of these lamps is on: the Elm lamp, the Fir lamp.
5. Exactly one of these lamps is on: the Fir lamp, the Hazel lamp.
6. Exactly one of these lamps is on: the Hazel lamp, the Juniper lamp.
7. Exactly one of these lamps is on: the Juniper lamp, the Larch lamp.
8. Exactly one of these lamps is on: the Larch lamp, the Maple lamp.
9. The Alder lamp is not on.
10. The Cedar lamp is not on.
11. The Fir lamp is not on.
12. The Juniper lamp is not on.
13. The Maple lamp is not on.

Question: Does it follow that the Larch lamp is on?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. If the statements contradict each other, finish with "ANSWER: CONTRADICTORY". Otherwise finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E3 / m8·incl·early·far**: ground truth: **YES**

```
Here are some statements:
1. The Alder lamp is not on.
2. The Cedar lamp is not on.
3. The Fir lamp is not on.
4. The Juniper lamp is not on.
5. The Maple lamp is not on.
6. At least one of these lamps is on: the Alder lamp, the Birch lamp.
7. At least one of these lamps is on: the Birch lamp, the Cedar lamp.
8. At least one of these lamps is on: the Cedar lamp, the Elm lamp.
9. At least one of these lamps is on: the Elm lamp, the Fir lamp.
10. At least one of these lamps is on: the Fir lamp, the Hazel lamp.
11. At least one of these lamps is on: the Hazel lamp, the Juniper lamp.
12. At least one of these lamps is on: the Juniper lamp, the Larch lamp.
13. At least one of these lamps is on: the Larch lamp, the Maple lamp.

Question: Does it follow that the Larch lamp is on?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. If the statements contradict each other, finish with "ANSWER: CONTRADICTORY". Otherwise finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

### (a) Output hypotheses: every cell

| cell | g | FST | ML | MA | ETR | E1p | MM | MMG | BIC | CWm | CWc | O1 | O2 | PRI | REC | AFF | YES* | NO* | UP1 | C1 | S3 | EX | NX | PN | RND | O8 | O32 | O128 | ETR0 | MMe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| m3·incl·late·near | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | N | N | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.90 | 0.96 | 0.50 | Y | Y | Y | N | Y |
| m3·incl·late·far | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | N | N | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.90 | 0.91 | 0.50 | Y | Y | Y | N | Y |
| m3·incl·early·near | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.90 | 0.96 | 0.50 | Y | Y | Y | N | Y |
| m3·incl·early·far | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.90 | 0.91 | 0.50 | Y | Y | Y | N | Y |
| m3·incl·jit·near | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.90 | 0.96 | 0.50 | Y | Y | Y | N | Y |
| m3·incl·jit·far | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.90 | 0.91 | 0.50 | Y | Y | Y | N | Y |
| m3·excl·late·near | YES | X | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.90 | 0.88 | 0.50 | Y | Y | Y | Y | Y |
| m3·excl·late·far | YES | X | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.90 | 0.85 | 0.50 | Y | Y | Y | Y | Y |
| m3·excl·early·near | YES | X | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.90 | 0.88 | 0.50 | Y | Y | Y | Y | Y |
| m3·excl·early·far | YES | X | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.90 | 0.85 | 0.50 | Y | Y | Y | Y | Y |
| m3·excl·jit·near | YES | X | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.90 | 0.88 | 0.50 | Y | Y | Y | Y | Y |
| m3·excl·jit·far | YES | X | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.90 | 0.85 | 0.50 | Y | Y | Y | Y | Y |
| m5·incl·late·near | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | N | N | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.87 | 0.92 | 0.50 | N | Y | Y | N | Y |
| m5·incl·late·far | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | N | N | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.87 | 0.88 | 0.50 | N | Y | Y | N | Y |
| m5·incl·early·near | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.87 | 0.92 | 0.50 | Y | Y | Y | N | Y |
| m5·incl·early·far | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.87 | 0.88 | 0.50 | Y | Y | Y | N | Y |
| m5·incl·jit·near | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.87 | 0.92 | 0.50 | Y | Y | Y | N | Y |
| m5·incl·jit·far | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.87 | 0.88 | 0.50 | Y | Y | Y | N | Y |
| m5·excl·late·near | YES | X | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.87 | 0.81 | 0.50 | Y | Y | Y | Y | Y |
| m5·excl·late·far | YES | X | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.87 | 0.78 | 0.50 | Y | Y | Y | Y | Y |
| m5·excl·early·near | YES | X | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.87 | 0.81 | 0.50 | Y | Y | Y | Y | Y |
| m5·excl·early·far | YES | X | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.87 | 0.78 | 0.50 | Y | Y | Y | Y | Y |
| m5·excl·jit·near | YES | X | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.87 | 0.81 | 0.50 | Y | Y | Y | Y | Y |
| m5·excl·jit·far | YES | X | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.87 | 0.78 | 0.50 | Y | Y | Y | Y | Y |
| m8·incl·late·near | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | N | N | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.82 | 0.86 | 0.50 | N | N | Y | N | Y |
| m8·incl·late·far | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | N | N | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.82 | 0.86 | 0.50 | N | N | Y | N | Y |
| m8·incl·early·near | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.82 | 0.86 | 0.50 | Y | Y | Y | N | Y |
| m8·incl·early·far | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.82 | 0.86 | 0.50 | Y | Y | Y | N | Y |
| m8·incl·jit·near | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.82 | 0.86 | 0.50 | Y | Y | Y | N | Y |
| m8·incl·jit·far | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.82 | 0.86 | 0.50 | Y | Y | Y | N | Y |
| m8·excl·late·near | YES | X | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.82 | 0.71 | 0.50 | Y | Y | Y | Y | Y |
| m8·excl·late·far | YES | X | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.82 | 0.71 | 0.50 | Y | Y | Y | Y | Y |
| m8·excl·early·near | YES | X | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.82 | 0.71 | 0.50 | Y | Y | Y | Y | Y |
| m8·excl·early·far | YES | X | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.82 | 0.71 | 0.50 | Y | Y | Y | Y | Y |
| m8·excl·jit·near | YES | X | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.82 | 0.71 | 0.50 | Y | Y | Y | Y | Y |
| m8·excl·jit·far | YES | X | Y | Y | Y | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.82 | 0.71 | 0.50 | Y | Y | Y | Y | Y |
| m12·incl·late·near | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | N | N | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.76 | 0.81 | 0.50 | N | N | N | N | Y |
| m12·incl·late·far | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | N | N | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.76 | 0.81 | 0.50 | N | N | N | N | Y |
| m12·incl·early·near | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.76 | 0.81 | 0.50 | Y | Y | Y | N | Y |
| m12·incl·early·far | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.76 | 0.81 | 0.50 | Y | Y | Y | N | Y |
| m12·incl·jit·near | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.76 | 0.81 | 0.50 | Y | Y | Y | N | Y |
| m12·incl·jit·far | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.76 | 0.81 | 0.50 | Y | Y | Y | N | Y |
| m12·excl·late·near | YES | X | Y | Y | n/c | n/c | Y | Y | Y | Y | Y | N | Y | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.76 | 0.64 | 0.50 | Y | Y | Y | n/c | Y |
| m12·excl·late·far | YES | X | Y | Y | n/c | n/c | Y | Y | Y | Y | Y | N | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.76 | 0.64 | 0.50 | Y | Y | Y | n/c | Y |
| m12·excl·early·near | YES | X | Y | Y | n/c | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.76 | 0.64 | 0.50 | Y | Y | Y | n/c | Y |
| m12·excl·early·far | YES | X | Y | Y | n/c | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.76 | 0.64 | 0.50 | Y | Y | Y | n/c | Y |
| m12·excl·jit·near | YES | X | Y | Y | n/c | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.76 | 0.64 | 0.50 | Y | Y | Y | n/c | Y |
| m12·excl·jit·far | YES | X | Y | Y | n/c | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.76 | 0.64 | 0.50 | Y | Y | Y | n/c | Y |
| m16·incl·late·near | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | N | N | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.70 | 0.76 | 0.50 | N | N | N | N | Y |
| m16·incl·late·far | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | N | N | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.70 | 0.76 | 0.50 | N | N | N | N | Y |
| m16·incl·early·near | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.70 | 0.76 | 0.50 | Y | Y | Y | N | Y |
| m16·incl·early·far | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.70 | 0.76 | 0.50 | Y | Y | Y | N | Y |
| m16·incl·jit·near | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.70 | 0.76 | 0.50 | Y | Y | Y | N | Y |
| m16·incl·jit·far | YES | X | Y | Y | N | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.70 | 0.76 | 0.50 | Y | Y | Y | N | Y |
| m16·excl·late·near | YES | X | Y | Y | n/c | n/c | Y | Y | Y | Y | Y | N | Y | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.70 | 0.59 | 0.50 | Y | Y | Y | n/c | Y |
| m16·excl·late·far | YES | X | Y | Y | n/c | n/c | Y | Y | Y | Y | Y | N | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.70 | 0.59 | 0.50 | Y | Y | Y | n/c | Y |
| m16·excl·early·near | YES | X | Y | Y | n/c | N | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.70 | 0.59 | 0.50 | Y | Y | Y | n/c | Y |
| m16·excl·early·far | YES | X | Y | Y | n/c | N | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.70 | 0.59 | 0.50 | Y | Y | Y | n/c | Y |
| m16·excl·jit·near | YES | X | Y | Y | n/c | n/c | Y | Y | Y | Y | Y | Y | Y | N | N | Y | Y | N | Y | Y | 1.00 | Y | 0.70 | 0.59 | 0.50 | Y | Y | Y | n/c | Y |
| m16·excl·jit·far | YES | X | Y | Y | n/c | n/c | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.70 | 0.59 | 0.50 | Y | Y | Y | n/c | Y |

### (b) Eval hypotheses: pre-registered contrasts (Δ under π_h = 1, in pp)

| contrast | definition | FST | ML | MA | ETR | E1p | MM | MMG | BIC | CWm | CWc | O1 | O2 | PRI | REC | AFF | YES* | NO* | UP1 | C1 | S3 | EX | NX | PN | RND | O8 | O32 | O128 | ETR0 | MMe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E3-C1 | W × O at m ∈ {12,16}: (incl·early − incl·late) − (excl·early − excl·late) | -0 | +0 | +0 | n/c | n/c | +0 | +0 | +0 | +0 | +0 | -0 | +80 | -0 | -0 | +0 | +0 | -0 | +0 | +0 | +0 | +0 | -0 | +0 | +0 | +80 | +80 | +80 | n/c | +0 |
| E3-C2 | W × O at m ∈ {3,5} | -0 | +0 | +0 | -0 | +80 | +0 | +0 | +0 | +0 | +0 | -0 | +80 | -0 | -0 | +0 | +0 | -0 | +0 | +0 | +0 | +0 | -0 | -0 | +0 | +40 | +0 | +0 | -0 | +0 |
| E3-C3 | W main effect in early order, m ≤ 8: excl·early − incl·early | +0 | -0 | -0 | +80 | +0 | -0 | -0 | -0 | -0 | -0 | -0 | -0 | +0 | +0 | -0 | -0 | +0 | -0 | -0 | +0 | -0 | -0 | -11 | +0 | -0 | -0 | -0 | +80 | -0 |
| E3-C4 | near probe, exclusive chains: late − early (first-premise cue) | +0 | -0 | -0 | n/c | n/c | -0 | -0 | -0 | -0 | -0 | -80 | -0 | +80 | +0 | -0 | -0 | +0 | -0 | -0 | +0 | -0 | -0 | +0 | +0 | -0 | -0 | -0 | n/c | -0 |
| E3-C5 | far probe, exclusive chains: early − late (last-premise cue) | +0 | -0 | -0 | n/c | n/c | -0 | -0 | -0 | -0 | -0 | +80 | -0 | +0 | +80 | -0 | -0 | +0 | -0 | -0 | +0 | -0 | -0 | +0 | +0 | -0 | -0 | -0 | n/c | -0 |
| E3-C6 | size: exclusive·early m=16 − m=3 | +0 | +0 | +0 | n/c | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | -20 | -27 | +0 | +0 | +0 | +0 | n/c | +0 |

**Weight sensitivity per theory.**

- Replicates of this cell set (frames × samples) needed to detect π_h ≥ 0.15 against EXACT (lower 95% bound > 0).
- Replicates needed to bound π_h ≤ 0.10 (upper 95%) if h is absent.
- The nearest rival, with the expected log-LR per replicate favouring h over it if h is true.

| theory | family | reps to detect π≥0.15 | reps to bound π≤0.10 | nearest rival (nats/rep) |
|---|---|---|---|---|
| FST | B4 | 1 | 1 | NO* (0.00) |
| ML | B4 | ∞ (= EXACT here) | ∞ | MA (0.00) |
| MA | B4 | ∞ (= EXACT here) | ∞ | ML (0.00) |
| ETR | B4/C4 | 2 | 2 | ETR0 (0.00) |
| E1p | B4/C4 | 1 | 1 | FST (10.55) |
| MM | B4 | ∞ (= EXACT here) | ∞ | ML (0.00) |
| MMG | B4 | ∞ (= EXACT here) | ∞ | ML (0.00) |
| BIC | B4 | ∞ (= EXACT here) | ∞ | ML (0.00) |
| CWm | B4 | ∞ (= EXACT here) | ∞ | ML (0.00) |
| CWc | B4 | ∞ (= EXACT here) | ∞ | ML (0.00) |
| O1 | C4 | 3 | 2 | O2 (17.58) |
| O2 | C4 | 5 | 4 | O8 (3.52) |
| PRI | A2 | 1 | 1 | E1p (14.06) |
| REC | A2 | 2 | 1 | RND (22.08) |
| AFF | A2 | ∞ (= EXACT here) | ∞ | ML (0.00) |
| YES* | A1 | ∞ (= EXACT here) | ∞ | ML (0.00) |
| NO* | A1 | 1 | 1 | FST (0.00) |
| UP1 | B1 | ∞ (= EXACT here) | ∞ | ML (0.00) |
| C1 | C1 | ∞ (= EXACT here) | ∞ | ML (0.00) |
| S3 | H | 23 | 41 | ML (3.08) |
| EX | null (exact; = D DPLL-b, E BP-t at these sizes) | — | — | ML (0.00) |
| NX | null | 24 | 31 | PN (0.98) |
| PN | null | 14 | 17 | NX (1.00) |
| RND | null (H RANDOM) | 3 | 3 | PN (16.65) |
| O8 | C4 | 6 | 5 | O2 (3.52) |
| O32 | C4 | 8 | 7 | O8 (3.52) |
| O128 | C4 | 12 | 10 | O32 (3.52) |
| ETR0 | B4/C4 | 2 | 2 | ETR (0.00) |
| MMe | B4 | ∞ (= EXACT here) | ∞ | ML (0.00) |

### (c) CoT hypotheses (trace signature per theory)

- **FST** (FIRST, B4): K3 COMMIT to first-listed disjunct 'the Alder lamp is on', 'the Birch lamp is on', 'the Cedar lamp is on', 'the Elm lamp is on', 'the Fir lamp is on', 'the Hazel lamp is on', 'the Juniper lamp is on', 'the Larch lamp is on'; second disjunct never developed; K2 absent; meets contradiction (K9/X)
- **ML** (MATCH-L, B4): no disjunct selected (no categorical premise later than a disjunction); reasons as EXACT
- **MA** (MATCH-A, B4): no disjunct selected (no categorical premise sharing a literal with a disjunction); reasons as EXACT
- **ETR** (ETR-default, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; if the first pass is inconclusive, K13 second pass from the last premise
- **E1p** (ETR-1p, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; single pass, no K13
- **MM** (MM-S1, B4): K1 lists only the possibilities in which the clauses are true (K12 negative-literal share ≈ 0); conditionals get one explicit case plus 'other cases' left implicit; no fully explicit truth table
- **MMG** (MM-G, B4): as MM-S1, but a categorical premise read BEFORE a conditional makes the trace build the conditional's cases consistent with it (e.g. not-B first → builds 'not-A and not-B')
- **BIC** (BICOND, B4): no conditional; reasons as EXACT
- **CWm** (CW-MIN, B4): K6 ABSENCE→FALSE: atoms not forced true are taken to be false ('nothing says X, so X is false')
- **CWc** (CW-COMP, B4): no rules to complete; reasons as EXACT
- **O1** (ONL(1), C4): K7 strict presentation order, no back-references; K8 ≤ 1 cases kept (after 1: 2 cand. →truncated to 1; after 2: 2 cand. →truncated to 1; after 3: 2 cand. →truncated to 1; after 4: 2 cand. →truncated to 1; after 5: 2 cand. →truncated to 1; after 6: 2 cand. →truncated to 1; after 7: 2 cand. →truncated to 1; after 8: 2 cand. →truncated to 1; after 9: 1 cand. →RESET; after 10: 1 cand.; after 11: 1 cand.; after 12: 1 cand.; after 13: 1 cand.)
- **O2** (ONL(2), C4): K7 strict presentation order, no back-references; K8 ≤ 2 cases kept (after 1: 2 cand.; after 2: 4 cand. →truncated to 2; after 3: 4 cand. →truncated to 2; after 4: 4 cand. →truncated to 2; after 5: 4 cand. →truncated to 2; after 6: 4 cand. →truncated to 2; after 7: 4 cand. →truncated to 2; after 8: 4 cand. →truncated to 2; after 9: 1 cand. →RESET; after 10: 1 cand.; after 11: 1 cand.; after 12: 1 cand.; after 13: 1 cand.)
- **PRI** (PRIMACY, A2): short trace; justification quotes statement 1 only; no case enumeration
- **REC** (RECENCY, A2): short trace; justification quotes statement 13 only; no case enumeration
- **AFF** (AFFIRM, A2): no case analysis tied to the premises; answer tracks whether the conclusion is affirmative
- **YES*** (ALWAYS-YES, A1): no structure-dependent reasoning; YES regardless
- **NO*** (NONE, A1): no structure-dependent reasoning; 'cannot be determined' regardless
- **UP1** (UP-1, B1): derives only single facts by one-step propagation; no case split; NO phrased as 'cannot be determined'
- **C1** (C1-GREEDY, C1): builds ONE scenario, assigning atoms in first-mention order (true unless a statement forbids it), never backtracks; reads the answer off that scenario
- **S3** (SAMPLE-3, H): tries 1-3 example scenarios ('for instance…'), no exhaustiveness claim; YES if the examples agree
- **EX** (EXACT, null (exact; = D DPLL-b, E BP-t at these sizes)): K10 VERIFY; every case considered; no counter-model exists; answer YES
- **NX** (NOISY-EXACT, null): EXACT-style trace with one unsystematic slip (a mis-copied literal or a skipped case) at a position unrelated to disjunct order or premise order
- **PN** (PERCEPTION-NOISE, null): restatement of the premises contains a misread literal (polarity flip or swapped name), then correct reasoning on the misread problem
- **RND** (RANDOM, null (H RANDOM)): no relation between trace and answer
- **O8** (ONL(8), C4): K7 strict presentation order, no back-references; K8 ≤ 8 cases kept (after 1: 2 cand.; after 2: 4 cand.; after 3: 7 cand.; after 4: 12 cand. →truncated to 8; after 5: 14 cand. →truncated to 8; after 6: 14 cand. →truncated to 8; after 7: 14 cand. →truncated to 8; after 8: 14 cand. →truncated to 8; after 9: 1 cand. →RESET; after 10: 1 cand.; after 11: 1 cand.; after 12: 1 cand.; after 13: 1 cand.)
- **O32** (ONL(32), C4): K7 strict presentation order, no back-references; K8 ≤ 32 cases kept (after 1: 2 cand.; after 2: 4 cand.; after 3: 7 cand.; after 4: 12 cand.; after 5: 20 cand.; after 6: 33 cand. →truncated to 32; after 7: 53 cand. →truncated to 32; after 8: 53 cand. →truncated to 32; after 9: 1 cand. →RESET; after 10: 1 cand.; after 11: 1 cand.; after 12: 1 cand.; after 13: 1 cand.)
- **O128** (ONL(128), C4): K7 strict presentation order, no back-references; K8 ≤ 128 cases kept (after 1: 2 cand.; after 2: 4 cand.; after 3: 7 cand.; after 4: 12 cand.; after 5: 20 cand.; after 6: 33 cand.; after 7: 54 cand.; after 8: 88 cand.; after 9: 34 cand.; after 10: 13 cand.; after 11: 5 cand.; after 12: 2 cand.; after 13: 1 cand.)
- **ETR0** (ETR-noissue, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end
- **MMe** (MM-elim, B4): as MM-S1 plus: possibilities not mentioning the categorical's literal are deleted (K4-like)

Cell-specific trace predictions (e.g. which disjunct is committed to, the state sizes of `ONL(k)`, the counter-model to look for) are in the JSONL `trace_predictions` field.

### Discrimination as likelihood

Theories are grouped by their predicted outcome pattern over this set's contrasts. Observing a group's pattern moves weight toward that group.

- The last column gives the smallest expected log-LR per replicate between a group member and any theory outside the group (larger = faster discrimination).
- Theories inside a group differ only at cell level, if at all; cell-level separation is in the nearest-rival column above.

| observed pattern | weight moves toward | min log-LR/rep vs outside (pair) |
|---|---|---|
| C1:ZERO C2:ZERO C3:ZERO C4:ZERO C5:ZERO C6:ZERO | FST, ML, MA, MM, MMG, BIC, CWm, CWc, AFF, YES*, NO*, UP1, C1, S3, EX, RND, MMe | 2.52 (AFF vs NX) |
| C1:n/c C2:ZERO C3:POS C4:n/c C5:n/c C6:n/c | ETR, ETR0 | 17.67 (ETR vs RND) |
| C1:n/c C2:POS C3:ZERO C4:n/c C5:n/c C6:ZERO | E1p | 10.55 (E1p vs FST) |
| C1:ZERO C2:ZERO C3:ZERO C4:NEG C5:POS C6:ZERO | O1 | 17.58 (O1 vs O2) |
| C1:POS C2:POS C3:ZERO C4:ZERO C5:ZERO C6:ZERO | O2, O8 | 3.52 (O8 vs O32) |
| C1:ZERO C2:ZERO C3:ZERO C4:POS C5:ZERO C6:ZERO | PRI | 14.06 (PRI vs E1p) |
| C1:ZERO C2:ZERO C3:ZERO C4:ZERO C5:POS C6:ZERO | REC | 22.08 (REC vs RND) |
| C1:ZERO C2:ZERO C3:ZERO C4:ZERO C5:ZERO C6:NEG | NX | 0.98 (NX vs PN) |
| C1:ZERO C2:ZERO C3:NEG C4:ZERO C5:ZERO C6:NEG | PN | 1.00 (PN vs NX) |
| C1:POS C2:ZERO C3:ZERO C4:ZERO C5:ZERO C6:ZERO | O32, O128 | 3.52 (O32 vs O8) |

Any other pattern is unexplained by a single strategy. It is fitted as a mixture: each contrast constrains Σ_h π_h Δ_h. Residual mass goes to the 'none of the above' component.

**Nearest-competitor separation (required pairs).**

For each target member: its two nearest rivals in this set, the expected log-LR per replicate, and, if that is < 0.2 nats, the sets that do separate the pair.

| target | rival | log-LR/rep here | separated in (log-LR/rep) |
|---|---|---|---|
| O1 | O2 | 17.58 |  |
| O1 | O8 | 21.09 |  |
| O2 | O8 | 3.52 |  |
| O2 | O32 | 7.03 |  |
| O8 | O2 | 3.52 |  |
| O8 | O32 | 3.52 |  |
| O32 | O8 | 3.52 |  |
| O32 | O128 | 3.52 |  |
| O128 | O32 | 3.52 |  |
| O128 | NX | 5.72 |  |
| ETR | ETR0 | 0.00 | E4 (7.0) |
| ETR | RND | 17.67 |  |
| E1p | FST | 10.55 |  |
| E1p | NO* | 10.55 |  |

## E4. Issue-structure minimal pairs: 'Some A are B' vs 'Some B are A'

- **Reasoning question.** Does an illusory instantiation of an existential depend on which predicate is 'at issue' (the restrictor of the 'some' sentence), as ETR predicts, when the two quantified sentences are logically equivalent?
- **Target members (this vertical).** ETR-default, ETR-1p, MATCH-A, CW-MIN.
- **Competitors (other families) and nulls.** PRIMACY, RECENCY, AFFIRM, SAMPLE-3, ETR-noissue; EXACT, NOISY-EXACT, PERCEPTION-NOISE, RANDOM.
- **Varied:** quantified sentence (Some painters are sculptors / Some sculptors are painters / control: there is a painter and there is a sculptor), categorical predicate (painter / sculptor), order (quantified first / categorical first).
- **Controlled:** the two 'some' sentences are logically equivalent and use the same words; probe = the predicate not in the categorical; nouns usable both as subject and complement.

### Full prompts (selected cells)

**E4 / SomePS·catP·Qf**: ground truth: **NO**

```
Here are some statements:
1. Some of the painters in the club are sculptors.
2. Mara is one of the painters in the club.

Question: Does it follow that Mara is a sculptor?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E4 / SomeSP·catP·Qf**: ground truth: **NO**

```
Here are some statements:
1. Some of the sculptors in the club are painters.
2. Mara is one of the painters in the club.

Question: Does it follow that Mara is a sculptor?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E4 / Ctrl·catP·Qf**: ground truth: **NO**

```
Here are some statements:
1. There is a painter in the club, and there is a sculptor in the club.
2. Mara is one of the painters in the club.

Question: Does it follow that Mara is a sculptor?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

### (a) Output hypotheses: every cell

| cell | g | ETR | E1p | ETR0 | MA | CWm | PRI | REC | AFF | YES* | NO* | S3 | EX | NX | PN | RND |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SomePS·catP·Qf | NO | Y | Y | N | Y | Y | Y | N | Y | Y | N | 0.58 | N | 0.07 | 0.02 | 0.50 |
| SomePS·catP·cf | NO | Y | N | N | Y | Y | N | Y | Y | Y | N | 0.58 | N | 0.07 | 0.02 | 0.50 |
| SomePS·catS·Qf | NO | N | N | N | Y | Y | Y | N | Y | Y | N | 0.58 | N | 0.07 | 0.02 | 0.50 |
| SomePS·catS·cf | NO | N | N | N | Y | Y | N | Y | Y | Y | N | 0.58 | N | 0.07 | 0.02 | 0.50 |
| SomeSP·catP·Qf | NO | N | N | N | Y | Y | Y | N | Y | Y | N | 0.58 | N | 0.07 | 0.02 | 0.50 |
| SomeSP·catP·cf | NO | N | N | N | Y | Y | N | Y | Y | Y | N | 0.58 | N | 0.07 | 0.02 | 0.50 |
| SomeSP·catS·Qf | NO | Y | Y | N | Y | Y | Y | N | Y | Y | N | 0.58 | N | 0.07 | 0.02 | 0.50 |
| SomeSP·catS·cf | NO | Y | N | N | Y | Y | N | Y | Y | Y | N | 0.58 | N | 0.07 | 0.02 | 0.50 |
| Ctrl·catP·Qf | NO | N | N | N | N | Y | Y | N | Y | Y | N | 0.36 | N | 0.07 | 0.02 | 0.50 |
| Ctrl·catP·cf | NO | N | N | N | N | Y | N | Y | Y | Y | N | 0.36 | N | 0.07 | 0.02 | 0.50 |
| Ctrl·catS·Qf | NO | N | N | N | N | Y | Y | N | Y | Y | N | 0.36 | N | 0.07 | 0.02 | 0.50 |
| Ctrl·catS·cf | NO | N | N | N | N | Y | N | Y | Y | Y | N | 0.36 | N | 0.07 | 0.02 | 0.50 |

### (b) Eval hypotheses: pre-registered contrasts (Δ under π_h = 1, in pp)

| contrast | definition | ETR | E1p | ETR0 | MA | CWm | PRI | REC | AFF | YES* | NO* | S3 | EX | NX | PN | RND |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E4-C1 | issue asymmetry: mean(categorical = restrictor) − mean(categorical = predicate) | +80 | +40 | +0 | +0 | +0 | -0 | -0 | +0 | +0 | +0 | -0 | +0 | +0 | -0 | +0 |
| E4-C2 | order in issue-matched cells: Q-first − cat-first | +0 | +80 | +0 | +0 | +0 | +80 | -80 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 |
| E4-C3 | "some" − control sentence | +40 | +20 | -0 | +80 | +0 | -0 | -0 | +0 | +0 | -0 | +22 | -0 | +0 | -0 | +0 |
| E4-C4 | order in issue-mismatched cells: Q-first − cat-first | +0 | +0 | +0 | +0 | +0 | +80 | -80 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 |

**Weight sensitivity per theory.**

- Replicates of this cell set (frames × samples) needed to detect π_h ≥ 0.15 against EXACT (lower 95% bound > 0).
- Replicates needed to bound π_h ≤ 0.10 (upper 95%) if h is absent.
- The nearest rival, with the expected log-LR per replicate favouring h over it if h is true.

| theory | family | reps to detect π≥0.15 | reps to bound π≤0.10 | nearest rival (nats/rep) |
|---|---|---|---|---|
| ETR | B4/C4 | 12 | 10 | E1p (3.52) |
| E1p | B4/C4 | 23 | 20 | ETR (3.52) |
| ETR0 | B4/C4 | ∞ (= EXACT here) | ∞ | NO* (0.00) |
| MA | B4 | 6 | 5 | S3 (2.73) |
| CWm | B4 | 4 | 4 | AFF (0.00) |
| PRI | A2 | 8 | 7 | RND (4.42) |
| REC | A2 | 8 | 7 | RND (4.42) |
| AFF | A2 | 4 | 4 | CWm (0.00) |
| YES* | A1 | 4 | 4 | CWm (0.00) |
| NO* | A1 | ∞ (= EXACT here) | ∞ | ETR0 (0.00) |
| S3 | H | 12 | 12 | RND (0.26) |
| EX | null (exact; = D DPLL-b, E BP-t at these sizes) | — | — | ETR0 (0.00) |
| NX | null | 1366 | 2256 | ETR0 (0.07) |
| PN | null | 179 | 318 | NX (0.32) |
| RND | null (H RANDOM) | 12 | 13 | S3 (0.27) |

### (c) CoT hypotheses (trace signature per theory)

- **ETR** (ETR-default, B4/C4): K15 WITNESS-ID only when Mara's predicate is the restrictor of the 'some' sentence ('Mara is one of the painters, and some painters are sculptors, so Mara is one of them')
- **E1p** (ETR-1p, B4/C4): K15 WITNESS-ID only when Mara's predicate is the restrictor of the 'some' sentence ('Mara is one of the painters, and some painters are sculptors, so Mara is one of them'); single pass: only when the 'some' sentence is read first
- **ETR0** (ETR-noissue, B4/C4): no witness identification; as EXACT
- **MA** (MATCH-A, B4): —
- **CWm** (CW-MIN, B4): —
- **PRI** (PRIMACY, A2): short trace; justification quotes statement 1 only; no case enumeration
- **REC** (RECENCY, A2): short trace; justification quotes statement 0 only; no case enumeration
- **AFF** (AFFIRM, A2): no case analysis tied to the premises; answer tracks whether the conclusion is affirmative
- **YES*** (ALWAYS-YES, A1): no structure-dependent reasoning; YES regardless
- **NO*** (NONE, A1): no structure-dependent reasoning; 'cannot be determined' regardless
- **S3** (SAMPLE-3, H): tries 1-3 example scenarios ('for instance…'), no exhaustiveness claim; YES if the examples agree
- **EX** (EXACT, null (exact; = D DPLL-b, E BP-t at these sizes)): K2: notes the 'some' witness could be someone other than Mara (counter-model: Mara is a painter but not the other; someone else is both); K10
- **NX** (NOISY-EXACT, null): EXACT-style trace with one unsystematic slip (a mis-copied literal or a skipped case) at a position unrelated to disjunct order or premise order
- **PN** (PERCEPTION-NOISE, null): restatement of the premises contains a misread literal (polarity flip or swapped name), then correct reasoning on the misread problem
- **RND** (RANDOM, null (H RANDOM)): no relation between trace and answer

Cell-specific trace predictions (e.g. which disjunct is committed to, the state sizes of `ONL(k)`, the counter-model to look for) are in the JSONL `trace_predictions` field.

### Discrimination as likelihood

Theories are grouped by their predicted outcome pattern over this set's contrasts. Observing a group's pattern moves weight toward that group.

- The last column gives the smallest expected log-LR per replicate between a group member and any theory outside the group (larger = faster discrimination).
- Theories inside a group differ only at cell level, if at all; cell-level separation is in the nearest-rival column above.

| observed pattern | weight moves toward | min log-LR/rep vs outside (pair) |
|---|---|---|
| C1:POS C2:ZERO C3:POS C4:ZERO | ETR | 3.52 (ETR vs E1p) |
| C1:POS C2:POS C3:POS C4:ZERO | E1p | 3.52 (E1p vs ETR) |
| C1:ZERO C2:ZERO C3:ZERO C4:ZERO | ETR0, CWm, AFF, YES*, NO*, EX, NX, PN, RND | 0.27 (RND vs S3) |
| C1:ZERO C2:ZERO C3:POS C4:ZERO | MA, S3 | 0.26 (S3 vs RND) |
| C1:ZERO C2:POS C3:ZERO C4:POS | PRI | 4.42 (PRI vs RND) |
| C1:ZERO C2:NEG C3:ZERO C4:NEG | REC | 4.42 (REC vs RND) |

Any other pattern is unexplained by a single strategy. It is fitted as a mixture: each contrast constrains Σ_h π_h Δ_h. Residual mass goes to the 'none of the above' component.

**Nearest-competitor separation (required pairs).**

For each target member: its two nearest rivals in this set, the expected log-LR per replicate, and, if that is < 0.2 nats, the sets that do separate the pair.

| target | rival | log-LR/rep here | separated in (log-LR/rep) |
|---|---|---|---|
| ETR | E1p | 3.52 |  |
| ETR | S3 | 3.76 |  |
| E1p | ETR | 3.52 |  |
| E1p | ETR0 | 3.52 |  |
| MA | S3 | 2.73 |  |
| MA | RND | 4.42 |  |
| CWm | AFF | 0.00 | E1 (26.4), E1L (15.8), E2 (66.8), E5 (51.0) |
| CWm | YES* | 0.00 | E1 (26.4), E1L (7.0), E2 (21.1), E5 (51.0) |

## E5. Abduction / diagnosis: alternative causes, rule order, observation position, closure

- **Reasoning question.** When explaining an observation, do models read each rule as 'iff', assume the listed causes are the only causes, build initial models (and so show suppression by an alternative cause), or commit to the first-listed cause?
- **Target members (this vertical).** BICOND, CW-COMP, CW-MIN, MM-S1, ETR-default-R2, ETR-1p-R2, ONL(1), ONL(2).
- **Competitors (other families) and nulls.** PRIMACY, RECENCY, C1-GREEDY, UP-1, SAMPLE-3, ETR-default; EXACT, NOISY-EXACT, PERCEPTION-NOISE, RANDOM.
- **Varied:** number of rules (1/2), rule order (blue first / red first), observation position (last / first), closure premise ('the bell is ringing only if a lever is pulled'), probe (blue, red, blue-or-red, not-red).
- **Controlled:** fictional mechanism; rule sentences identical in form; closure adds one sentence and flips validity only for the blue-or-red probe (2 rules) or the blue probe (1 rule).

### Full prompts (selected cells)

**E5 / 1r·A·obs-last·open·A**: ground truth: **NO**

```
Here are some statements:
1. If the blue lever is pulled, then the bell is ringing.
2. The bell is ringing.

Question: Does it follow that the blue lever is pulled?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E5 / 2r·AB·obs-last·open·A**: ground truth: **NO**

```
Here are some statements:
1. If the blue lever is pulled, then the bell is ringing.
2. If the red lever is pulled, then the bell is ringing.
3. The bell is ringing.

Question: Does it follow that the blue lever is pulled?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E5 / 2r·AB·obs-last·closure·AorB**: ground truth: **YES**

```
Here are some statements:
1. If the blue lever is pulled, then the bell is ringing.
2. If the red lever is pulled, then the bell is ringing.
3. The bell is ringing only if the blue lever is pulled or the red lever is pulled.
4. The bell is ringing.

Question: Does it follow that the blue lever is pulled or the red lever is pulled (or both)?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**E5 / 2r·AB·obs-last·open·A·alarm**: ground truth: **NO**

```
Here are some statements:
1. If the back door is open, then the alarm is sounding.
2. If the kitchen window is broken, then the alarm is sounding.
3. The alarm is sounding.

Question: Does it follow that the back door is open?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

### (a) Output hypotheses: every cell

| cell | g | FST | ML | MA | MM | MMG | BIC | CWm | CWc | O1 | O2 | O4 | PRI | REC | AFF | YES* | NO* | UP1 | C1 | S3 | EX | NX | PN | RND | ETR | E1p | ETR·R2 | E1p·R2 | ETR0 | MMe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1r·A·obs-last·open·A | NO | N | N | N | Y | Y | Y | N | Y | Y | N | N | Y | N | Y | Y | N | N | Y | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | Y | Y | N | Y |
| 1r·A·obs-last·closure·A | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | N | Y | Y | 1.00 | Y | 0.92 | 0.92 | 0.50 | Y | Y | Y | Y | Y | Y |
| 1r·A·obs-first·open·A | NO | N | N | N | Y | Y | Y | N | Y | Y | N | N | N | Y | Y | Y | N | N | Y | 0.12 | N | 0.07 | 0.00 | 0.50 | N | N | Y | N | N | Y |
| 1r·A·obs-first·closure·A | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | Y | Y | 1.00 | Y | 0.92 | 0.92 | 0.50 | Y | Y | Y | Y | Y | Y |
| 2r·AB·obs-last·open·A | NO | N | N | N | N | N | Y | N | N | Y | Y | N | Y | N | Y | Y | N | N | Y | 0.12 | N | 0.08 | 0.00 | 0.50 | N | N | Y | Y | N | N |
| 2r·AB·obs-last·open·B | NO | N | N | N | N | N | Y | N | N | Y | N | N | N | N | Y | Y | N | N | Y | 0.12 | N | 0.08 | 0.00 | 0.50 | N | N | N | N | N | N |
| 2r·AB·obs-last·open·AorB | NO | N | N | N | Y | Y | Y | N | Y | Y | Y | N | Y | N | Y | Y | N | N | Y | 0.42 | N | 0.08 | 0.00 | 0.50 | N | N | N | N | N | Y |
| 2r·AB·obs-last·open·notB | NO | N | N | N | N | N | N | Y | N | N | N | N | N | N | N | Y | N | N | N | 0.12 | N | 0.08 | 0.04 | 0.50 | N | N | N | N | N | N |
| 2r·AB·obs-last·closure·A | NO | Y | N | N | N | N | Y | N | N | Y | Y | N | Y | N | Y | Y | N | N | Y | 0.30 | N | 0.09 | 0.02 | 0.50 | N | N | Y | Y | N | N |
| 2r·AB·obs-last·closure·B | NO | N | N | N | N | N | Y | N | N | Y | N | N | N | N | Y | Y | N | N | Y | 0.30 | N | 0.09 | 0.02 | 0.50 | N | N | N | N | N | N |
| 2r·AB·obs-last·closure·AorB | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | N | N | Y | 1.00 | Y | 0.91 | 0.93 | 0.50 | Y | Y | Y | Y | Y | Y |
| 2r·AB·obs-last·closure·notB | NO | N | N | N | N | N | N | N | N | N | N | N | N | N | N | Y | N | N | N | 0.04 | N | 0.09 | 0.04 | 0.50 | N | N | N | N | N | N |
| 2r·AB·obs-first·open·A | NO | N | N | N | N | N | Y | N | N | Y | Y | N | N | N | Y | Y | N | N | Y | 0.12 | N | 0.08 | 0.00 | 0.50 | N | N | N | N | N | N |
| 2r·AB·obs-first·open·B | NO | N | N | N | N | N | Y | N | N | Y | N | N | N | Y | Y | Y | N | N | Y | 0.12 | N | 0.08 | 0.00 | 0.50 | N | N | Y | N | N | N |
| 2r·AB·obs-first·open·AorB | NO | N | N | N | Y | Y | Y | N | Y | Y | Y | N | N | Y | Y | Y | N | N | Y | 0.42 | N | 0.08 | 0.00 | 0.50 | N | N | N | N | N | Y |
| 2r·AB·obs-first·open·notB | NO | N | N | N | N | N | N | Y | N | N | N | N | N | N | N | Y | N | N | N | 0.12 | N | 0.08 | 0.04 | 0.50 | N | N | N | N | N | N |
| 2r·AB·obs-first·closure·A | NO | Y | N | N | N | N | Y | N | N | Y | Y | N | N | Y | Y | Y | N | N | Y | 0.30 | N | 0.09 | 0.02 | 0.50 | N | N | N | N | N | N |
| 2r·AB·obs-first·closure·B | NO | N | N | N | N | N | Y | N | N | Y | N | N | N | Y | Y | Y | N | N | Y | 0.30 | N | 0.09 | 0.02 | 0.50 | N | N | N | N | N | N |
| 2r·AB·obs-first·closure·AorB | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | N | Y | 1.00 | Y | 0.91 | 0.93 | 0.50 | Y | Y | Y | Y | Y | Y |
| 2r·AB·obs-first·closure·notB | NO | N | N | N | N | N | N | N | N | N | N | N | N | N | N | Y | N | N | N | 0.04 | N | 0.09 | 0.04 | 0.50 | N | N | N | N | N | N |
| 2r·BA·obs-last·open·A | NO | N | N | N | N | N | Y | N | N | Y | N | N | N | N | Y | Y | N | N | Y | 0.12 | N | 0.08 | 0.00 | 0.50 | N | N | N | N | N | N |
| 2r·BA·obs-last·open·B | NO | N | N | N | N | N | Y | N | N | Y | Y | N | Y | N | Y | Y | N | N | Y | 0.12 | N | 0.08 | 0.00 | 0.50 | N | N | Y | Y | N | N |
| 2r·BA·obs-last·open·AorB | NO | N | N | N | Y | Y | Y | N | Y | Y | Y | N | Y | N | Y | Y | N | N | Y | 0.42 | N | 0.08 | 0.00 | 0.50 | N | N | N | N | N | Y |
| 2r·BA·obs-last·open·notB | NO | N | N | N | N | N | N | Y | N | N | N | N | N | N | N | Y | N | N | N | 0.12 | N | 0.08 | 0.04 | 0.50 | N | N | N | N | N | N |
| 2r·BA·obs-last·closure·A | NO | Y | N | N | N | N | Y | N | N | Y | N | N | N | N | Y | Y | N | N | Y | 0.30 | N | 0.09 | 0.02 | 0.50 | N | N | N | N | N | N |
| 2r·BA·obs-last·closure·B | NO | N | N | N | N | N | Y | N | N | Y | Y | N | Y | N | Y | Y | N | N | Y | 0.30 | N | 0.09 | 0.02 | 0.50 | N | N | Y | Y | N | N |
| 2r·BA·obs-last·closure·AorB | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | N | N | Y | 1.00 | Y | 0.91 | 0.93 | 0.50 | Y | Y | Y | Y | Y | Y |
| 2r·BA·obs-last·closure·notB | NO | N | N | N | N | N | N | N | N | N | N | N | N | N | N | Y | N | N | N | 0.04 | N | 0.09 | 0.04 | 0.50 | N | N | N | N | N | N |
| 2r·BA·obs-first·open·A | NO | N | N | N | N | N | Y | N | N | Y | N | N | N | Y | Y | Y | N | N | Y | 0.12 | N | 0.08 | 0.00 | 0.50 | N | N | Y | N | N | N |
| 2r·BA·obs-first·open·B | NO | N | N | N | N | N | Y | N | N | Y | Y | N | N | N | Y | Y | N | N | Y | 0.12 | N | 0.08 | 0.00 | 0.50 | N | N | N | N | N | N |
| 2r·BA·obs-first·open·AorB | NO | N | N | N | Y | Y | Y | N | Y | Y | Y | N | N | Y | Y | Y | N | N | Y | 0.42 | N | 0.08 | 0.00 | 0.50 | N | N | N | N | N | Y |
| 2r·BA·obs-first·open·notB | NO | N | N | N | N | N | N | Y | N | N | N | N | N | N | N | Y | N | N | N | 0.12 | N | 0.08 | 0.04 | 0.50 | N | N | N | N | N | N |
| 2r·BA·obs-first·closure·A | NO | Y | N | N | N | N | Y | N | N | Y | N | N | N | Y | Y | Y | N | N | Y | 0.30 | N | 0.09 | 0.02 | 0.50 | N | N | N | N | N | N |
| 2r·BA·obs-first·closure·B | NO | N | N | N | N | N | Y | N | N | Y | Y | N | N | Y | Y | Y | N | N | Y | 0.30 | N | 0.09 | 0.02 | 0.50 | N | N | N | N | N | N |
| 2r·BA·obs-first·closure·AorB | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | Y | N | N | Y | 1.00 | Y | 0.91 | 0.93 | 0.50 | Y | Y | Y | Y | Y | Y |
| 2r·BA·obs-first·closure·notB | NO | N | N | N | N | N | N | N | N | N | N | N | N | N | N | Y | N | N | N | 0.04 | N | 0.09 | 0.04 | 0.50 | N | N | N | N | N | N |
| 2r·AB·obs-last·open·A·alarm | NO | N | N | N | N | N | Y | N | N | Y | Y | N | Y | N | Y | Y | N | N | Y | 0.12 | N | 0.08 | 0.00 | 0.50 | N | N | Y | Y | N | N |
| 2r·AB·obs-last·open·AorB·alarm | NO | N | N | N | Y | Y | Y | N | Y | Y | Y | N | Y | N | Y | Y | N | N | Y | 0.42 | N | 0.08 | 0.00 | 0.50 | N | N | N | N | N | Y |
| 2r·AB·obs-last·closure·A·alarm | NO | Y | N | N | N | N | Y | N | N | Y | Y | N | Y | N | Y | Y | N | N | Y | 0.30 | N | 0.09 | 0.02 | 0.50 | N | N | Y | Y | N | N |
| 2r·AB·obs-last·closure·AorB·alarm | YES | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | N | Y | Y | N | N | Y | 1.00 | Y | 0.91 | 0.93 | 0.50 | Y | Y | Y | Y | Y | Y |

### (b) Eval hypotheses: pre-registered contrasts (Δ under π_h = 1, in pp)

| contrast | definition | FST | ML | MA | MM | MMG | BIC | CWm | CWc | O1 | O2 | O4 | PRI | REC | AFF | YES* | NO* | UP1 | C1 | S3 | EX | NX | PN | RND | ETR | E1p | ETR·R2 | E1p·R2 | ETR0 | MMe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E5-C1 | suppression: 1 rule (AC on blue) − 2 rules (blue rule first), observation last, no closure | +0 | +0 | +0 | +80 | +80 | +0 | +0 | +80 | +0 | -80 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | -1 | -0 | +0 | +0 | +0 | +0 | +0 | +0 | +80 |
| E5-C2 | first-listed cause, observation last: first-listed probe − second-listed probe | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +80 | +0 | +80 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +80 | +80 | +0 | +0 |
| E5-C3 | first-listed cause, observation first | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +80 | +0 | +0 | -80 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | -80 | +0 | +0 | +0 |
| E5-C4 | closure on "blue or red": closure − no closure (2 rules) | +80 | +80 | +80 | +0 | +0 | +0 | +80 | +0 | +0 | +0 | +80 | -0 | -0 | +0 | +0 | +0 | +0 | +0 | +58 | +80 | +83 | +92 | +0 | +80 | +80 | +80 | +80 | +80 | +0 |
| E5-C5 | "blue or red" − "blue" (2 rules, no closure) | +0 | +0 | +0 | +80 | +80 | +0 | +0 | +80 | +0 | +40 | +0 | +20 | +20 | +0 | +0 | +0 | +0 | +0 | +30 | +0 | -0 | +0 | +0 | +0 | +0 | -40 | -20 | +0 | +80 |
| E5-C6 | "not red" − "red" (2 rules, no closure) | +0 | +0 | +0 | +0 | +0 | -80 | +80 | +0 | -80 | -40 | +0 | -20 | -20 | -80 | +0 | +0 | +0 | -80 | +0 | +0 | -0 | +4 | +0 | +0 | +0 | -40 | -20 | +0 | +0 |

**Weight sensitivity per theory.**

- Replicates of this cell set (frames × samples) needed to detect π_h ≥ 0.15 against EXACT (lower 95% bound > 0).
- Replicates needed to bound π_h ≤ 0.10 (upper 95%) if h is absent.
- The nearest rival, with the expected log-LR per replicate favouring h over it if h is true.

| theory | family | reps to detect π≥0.15 | reps to bound π≤0.10 | nearest rival (nats/rep) |
|---|---|---|---|---|
| FST | B4 | 10 | 8 | S3 (6.45) |
| ML | B4 | ∞ (= EXACT here) | ∞ | MA (0.00) |
| MA | B4 | ∞ (= EXACT here) | ∞ | ML (0.00) |
| MM | B4 | 7 | 6 | MMG (0.00) |
| MMG | B4 | 7 | 6 | MM (0.00) |
| BIC | B4 | 2 | 2 | O1 (0.00) |
| CWm | B4 | 12 | 10 | ML (7.03) |
| CWc | B4 | 7 | 6 | MM (0.00) |
| O1 | C4 | 2 | 2 | BIC (0.00) |
| O2 | C4 | 4 | 3 | RND (14.72) |
| O4 | C4 | ∞ (= EXACT here) | ∞ | ML (0.00) |
| PRI | A2 | 4 | 3 | E1p·R2 (10.55) |
| REC | A2 | 4 | 3 | RND (14.72) |
| AFF | A2 | 2 | 2 | BIC (0.00) |
| YES* | A1 | 2 | 2 | BIC (14.06) |
| NO* | A1 | 7 | 6 | UP1 (3.52) |
| UP1 | B1 | 10 | 8 | NO* (3.52) |
| C1 | C1 | 2 | 2 | BIC (0.00) |
| S3 | H | 21 | 26 | ML (3.61) |
| EX | null (exact; = D DPLL-b, E BP-t at these sizes) | — | — | ML (0.00) |
| NX | null | 1290 | 2100 | ML (0.07) |
| PN | null | 57 | 102 | NX (1.01) |
| RND | null (H RANDOM) | 4 | 4 | S3 (19.97) |
| ETR | B4/C4 | ∞ (= EXACT here) | ∞ | ML (0.00) |
| E1p | B4/C4 | ∞ (= EXACT here) | ∞ | ML (0.00) |
| ETR·R2 | B4/C4 | 5 | 4 | E1p·R2 (5.27) |
| E1p·R2 | B4/C4 | 7 | 6 | ETR·R2 (5.27) |
| ETR0 | B4/C4 | ∞ (= EXACT here) | ∞ | ML (0.00) |
| MMe | B4 | 7 | 6 | MM (0.00) |

### (c) CoT hypotheses (trace signature per theory)

- **FST** (FIRST, B4): no disjunction to commit on; reasons as EXACT
- **ML** (MATCH-L, B4): no disjunct selected (no categorical premise later than a disjunction); reasons as EXACT
- **MA** (MATCH-A, B4): no disjunct selected (no categorical premise sharing a literal with a disjunction); reasons as EXACT
- **MM** (MM-S1, B4): K1 lists only the possibilities in which the clauses are true (K12 negative-literal share ≈ 0); conditionals get one explicit case plus 'other cases' left implicit; no fully explicit truth table; answers 'nothing follows' (NO) when only implicit cases remain
- **MMG** (MM-G, B4): as MM-S1, but a categorical premise read BEFORE a conditional makes the trace build the conditional's cases consistent with it (e.g. not-B first → builds 'not-A and not-B')
- **BIC** (BICOND, B4): K5 CONVERSE stated or used: 'if the bell is ringing, then the blue lever is pulled'
- **CWm** (CW-MIN, B4): K6 ABSENCE→FALSE: atoms not forced true are taken to be false ('nothing says X, so X is false')
- **CWc** (CW-COMP, B4): K6: listed antecedents treated as the only possible causes ('E can only come from the listed causes')
- **O1** (ONL(1), C4): K7 strict presentation order, no back-references; K8 ≤ 1 cases kept (after 1: 2 cand. →truncated to 1; after 2: 1 cand.)
- **O2** (ONL(2), C4): K7 strict presentation order, no back-references; K8 ≤ 2 cases kept (after 1: 2 cand.; after 2: 2 cand.)
- **O4** (ONL(4), C4): K7 strict presentation order, no back-references; K8 ≤ 4 cases kept (after 1: 2 cand.; after 2: 2 cand.)
- **PRI** (PRIMACY, A2): short trace; justification quotes statement 1 only; no case enumeration
- **REC** (RECENCY, A2): short trace; justification quotes statement 2 only; no case enumeration
- **AFF** (AFFIRM, A2): no case analysis tied to the premises; answer tracks whether the conclusion is affirmative
- **YES*** (ALWAYS-YES, A1): no structure-dependent reasoning; YES regardless
- **NO*** (NONE, A1): no structure-dependent reasoning; 'cannot be determined' regardless
- **UP1** (UP-1, B1): derives only single facts by one-step propagation; no case split; NO phrased as 'cannot be determined'
- **C1** (C1-GREEDY, C1): builds ONE scenario, assigning atoms in first-mention order (true unless a statement forbids it), never backtracks; reads the answer off that scenario
- **S3** (SAMPLE-3, H): tries 1-3 example scenarios ('for instance…'), no exhaustiveness claim; YES if the examples agree
- **EX** (EXACT, null (exact; = D DPLL-b, E BP-t at these sizes)): K10 VERIFY; K2 counter-model stated (e.g. the blue lever is not pulled; the bell is ringing); answer NO
- **NX** (NOISY-EXACT, null): EXACT-style trace with one unsystematic slip (a mis-copied literal or a skipped case) at a position unrelated to disjunct order or premise order
- **PN** (PERCEPTION-NOISE, null): restatement of the premises contains a misread literal (polarity flip or swapped name), then correct reasoning on the misread problem
- **RND** (RANDOM, null (H RANDOM)): no relation between trace and answer
- **ETR** (ETR-default, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; if the first pass is inconclusive, K13 second pass from the last premise; conditional read as antecedent-and-consequent given antecedent
- **E1p** (ETR-1p, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; single pass, no K13; conditional read as antecedent-and-consequent given antecedent
- **ETR·R2** (ETR-default-R2, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; if the first pass is inconclusive, K13 second pass from the last premise; conditional read as antecedent-and-consequent given antecedent
- **E1p·R2** (ETR-1p-R2, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; single pass, no K13; conditional read as antecedent-and-consequent given antecedent; K2 absent
- **ETR0** (ETR-noissue, B4/C4): K7 premise-by-premise processing; at each premise keeps only the cases that share the most literals with it (K4, also for disjunctive premises); contradicted cases kept until the end; conditional read as antecedent-and-consequent given antecedent
- **MMe** (MM-elim, B4): as MM-S1 plus: possibilities not mentioning the categorical's literal are deleted (K4-like)

Cell-specific trace predictions (e.g. which disjunct is committed to, the state sizes of `ONL(k)`, the counter-model to look for) are in the JSONL `trace_predictions` field.

### Discrimination as likelihood

Theories are grouped by their predicted outcome pattern over this set's contrasts. Observing a group's pattern moves weight toward that group.

- The last column gives the smallest expected log-LR per replicate between a group member and any theory outside the group (larger = faster discrimination).
- Theories inside a group differ only at cell level, if at all; cell-level separation is in the nearest-rival column above.

| observed pattern | weight moves toward | min log-LR/rep vs outside (pair) |
|---|---|---|
| C1:ZERO C2:ZERO C3:ZERO C4:POS C5:ZERO C6:ZERO | FST, ML, MA, O4, EX, NX, PN, ETR, E1p, ETR0 | 3.06 (E1p vs S3) |
| C1:POS C2:ZERO C3:ZERO C4:ZERO C5:POS C6:ZERO | MM, MMG, CWc, MMe | 7.54 (CWc vs S3) |
| C1:ZERO C2:ZERO C3:ZERO C4:ZERO C5:ZERO C6:NEG | BIC, O1, AFF, C1 | 14.06 (AFF vs YES*) |
| C1:ZERO C2:ZERO C3:ZERO C4:POS C5:ZERO C6:POS | CWm | 7.03 (CWm vs E1p) |
| C1:NEG C2:POS C3:POS C4:ZERO C5:POS C6:NEG | O2 | 14.72 (O2 vs RND) |
| C1:ZERO C2:POS C3:ZERO C4:ZERO C5:POS C6:NEG | PRI | 10.55 (PRI vs E1p·R2) |
| C1:ZERO C2:ZERO C3:NEG C4:ZERO C5:POS C6:NEG | REC | 14.72 (REC vs RND) |
| C1:ZERO C2:ZERO C3:ZERO C4:ZERO C5:ZERO C6:ZERO | YES*, NO*, UP1, RND | 8.79 (UP1 vs E1p) |
| C1:ZERO C2:ZERO C3:ZERO C4:POS C5:POS C6:ZERO | S3 | 3.61 (S3 vs E1p) |
| C1:ZERO C2:POS C3:NEG C4:POS C5:NEG C6:NEG | ETR·R2 | 5.27 (ETR·R2 vs E1p·R2) |
| C1:ZERO C2:POS C3:ZERO C4:POS C5:NEG C6:NEG | E1p·R2 | 5.27 (E1p·R2 vs ETR·R2) |

Any other pattern is unexplained by a single strategy. It is fitted as a mixture: each contrast constrains Σ_h π_h Δ_h. Residual mass goes to the 'none of the above' component.

**Nearest-competitor separation (required pairs).**

For each target member: its two nearest rivals in this set, the expected log-LR per replicate, and, if that is < 0.2 nats, the sets that do separate the pair.

| target | rival | log-LR/rep here | separated in (log-LR/rep) |
|---|---|---|---|
| BIC | O1 | 0.00 | E1 (26.4), E1L (12.3), E2 (31.6), E3 (35.2) |
| BIC | AFF | 0.00 | E1 (26.4), E1L (15.8), E2 (45.7) |
| CWc | MM | 0.00 | E2 (38.7) |
| CWc | MMG | 0.00 | E2 (28.1) |
| CWm | ML | 7.03 |  |
| CWm | MA | 7.03 |  |
| MM | MMG | 0.00 | E2 (10.6) |
| MM | CWc | 0.00 | E2 (38.7) |
| ETR·R2 | E1p·R2 | 5.27 |  |
| ETR·R2 | RND | 14.72 |  |
| E1p·R2 | ETR·R2 | 5.27 |  |
| E1p·R2 | PRI | 10.55 |  |
| O1 | BIC | 0.00 | E1 (26.4), E1L (12.3), E2 (31.6), E3 (35.2) |
| O1 | AFF | 0.00 | E1 (14.1), E1L (7.0), E2 (35.2), E3 (35.2) |
| O2 | RND | 14.72 |  |
| O2 | S3 | 15.71 |  |

## E6a. Phantom constraints: irrelevant co-mention of a forced-equal pair vs a free pair (exam scheduling)

- **Reasoning question.** Does an irrelevant sentence that co-mentions two exams make the model treat them as conflicting, causing errors only when those two exams must share a day?
- **Target members (this vertical).** ADD-CONSTRAINT.
- **Competitors (other families) and nulls.** HALLUC-CONSTRAINT, DROP-LAST, FIRST-FIT, DSATUR, ONLINE-FIRST-FIT, A2-ADDED-SENTENCE, ALWAYS-IMPOSSIBLE; EXACT, NOISY-EXACT, PERCEPTION-NOISE, RANDOM.
- **Varied:** co-mention sentence: none / forced-equal pair (u,v) / free pair (u,w); position early / late.
- **Controlled:** same graph and conflict list in every variant; the (u,v) and (u,w) sentences have the same template and length; g = feasible in every variant.

### Full prompts (selected cells)

**E6a / E6a·uv-early**: ground truth: **feasible (any proper 3-day schedule), e.g. {Algebra:Mon, Biology:Tue, Chemistry:Wed, Drama:Wed, Economics:Mon, French:Tue, Geography:Mon, History:Wed} proper**

```
A school must schedule 8 exams (Algebra, Biology, Chemistry, Drama, Economics, French, Geography, History) into 3 days: Monday, Tuesday, Wednesday. Two exams that share a student cannot be on the same day.
Chemistry and Drama were both written by Dr. Okafor.
These pairs of exams share a student:
- Drama and Biology
- Biology and History
- Economics and History
- Biology and Economics
- Chemistry and Biology
- Drama and Algebra
- French and Geography
- Algebra and Biology
- Chemistry and Algebra
- Drama and Economics
- Economics and French

Assign each exam to a day so that no two exams sharing a student are on the same day, or say that it is impossible.
Think it through as carefully as you need. Finish with one line of JSON: either {"schedule": {"<exam>": "<day>", ...}} or {"impossible": true}.
```

**E6a / E6a·uw-early**: ground truth: **feasible (any proper 3-day schedule), e.g. {Algebra:Mon, Biology:Tue, Chemistry:Wed, Drama:Wed, Economics:Mon, French:Tue, Geography:Mon, History:Wed} proper**

```
A school must schedule 8 exams (Algebra, Biology, Chemistry, Drama, Economics, French, Geography, History) into 3 days: Monday, Tuesday, Wednesday. Two exams that share a student cannot be on the same day.
Chemistry and Economics were both written by Dr. Okafor.
These pairs of exams share a student:
- Drama and Biology
- Biology and History
- Economics and History
- Biology and Economics
- Chemistry and Biology
- Drama and Algebra
- French and Geography
- Algebra and Biology
- Chemistry and Algebra
- Drama and Economics
- Economics and French

Assign each exam to a day so that no two exams sharing a student are on the same day, or say that it is impossible.
Think it through as carefully as you need. Finish with one line of JSON: either {"schedule": {"<exam>": "<day>", ...}} or {"impossible": true}.
```

**E6a / E6a·uv-early·graph**: ground truth: **feasible (any proper 3-day schedule), e.g. {Algebra:Mon, Biology:Tue, Chemistry:Wed, Drama:Wed, Economics:Mon, French:Tue, Geography:Mon, History:Wed} proper**

```
Colour the vertices Algebra, Biology, Chemistry, Drama, Economics, French, Geography, History of a graph with at most 3 colours (1-3) so that the two ends of every edge get different colours.
Note: Chemistry and Drama were both added to the graph on the same day.
Edges:
- Drama – Biology
- Biology – History
- Economics – History
- Biology – Economics
- Chemistry – Biology
- Drama – Algebra
- French – Geography
- Algebra – Biology
- Chemistry – Algebra
- Drama – Economics
- Economics – French

Think it through as carefully as you need. Finish with one line of JSON: either {"colours": {"<vertex>": <colour>, ...}} or {"impossible": true}.
```

### (a) Output hypotheses: every cell

| cell | g | ADD | HAL | DROP | FF | DSAT | OFF | A2+ | IMP* | EX | NX | PN | RND |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E6a·none | feasible | ok | 0.15 | ERR | ok | ok | ERR | 0.10 | IMP | ok | 0.16 | 0.14 | 1.00 |
| E6a·uv-early | feasible | IMP | 0.15 | ERR | ok | ok | ERR | 0.30 | IMP | ok | 0.16 | 0.14 | 1.00 |
| E6a·uv-late | feasible | IMP | 0.15 | ERR | ok | ok | ERR | 0.30 | IMP | ok | 0.16 | 0.14 | 1.00 |
| E6a·uw-early | feasible | ok | 0.15 | ERR | ok | ok | ERR | 0.30 | IMP | ok | 0.16 | 0.14 | 1.00 |
| E6a·uw-late | feasible | ok | 0.15 | ERR | ok | ok | ERR | 0.30 | IMP | ok | 0.16 | 0.14 | 1.00 |
| E6a·none·graph | feasible | ok | 0.15 | ERR | ok | ok | ERR | 0.10 | IMP | ok | 0.16 | 0.14 | 1.00 |
| E6a·uv-early·graph | feasible | IMP | 0.15 | ERR | ok | ok | ERR | 0.30 | IMP | ok | 0.16 | 0.14 | 1.00 |
| E6a·uw-early·graph | feasible | ok | 0.15 | ERR | ok | ok | ERR | 0.30 | IMP | ok | 0.16 | 0.14 | 1.00 |

CSP entries: `ok` = valid answer, `ERR` = invalid schedule or assignment, `IMP` = declared impossible (an error, since every item is feasible), decimals = P(error).

### (b) Eval hypotheses: pre-registered contrasts (Δ under π_h = 1, in pp)

| contrast | definition | ADD | HAL | DROP | FF | DSAT | OFF | A2+ | IMP* | EX | NX | PN | RND |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E6a-C1 | error rate: mean(uv) − mean(uw) | +80 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 | +0 |
| E6a-C2 | error rate: mean(uw) − none | +0 | +0 | +0 | +0 | +0 | +0 | +20 | +0 | +0 | +0 | +0 | +0 |

**Weight sensitivity per theory.**

- Replicates of this cell set (frames × samples) needed to detect π_h ≥ 0.15 against EXACT (lower 95% bound > 0).
- Replicates needed to bound π_h ≤ 0.10 (upper 95%) if h is absent.
- The nearest rival, with the expected log-LR per replicate favouring h over it if h is true.

| theory | family | reps to detect π≥0.15 | reps to bound π≤0.10 | nearest rival (nats/rep) |
|---|---|---|---|---|
| ADD | B4 | 16 | 13 | FF (24.82) |
| HAL | nuisance | 924 | 1379 | PN (0.00) |
| DROP | B1 | 6 | 5 | RND (47.79) |
| FF | C1 | ∞ (= EXACT here) | ∞ | DSAT (0.00) |
| DSAT | C2 | ∞ (= EXACT here) | ∞ | FF (0.00) |
| OFF | C4 | 6 | 5 | RND (47.79) |
| A2+ | A2 | 81 | 102 | NX (0.40) |
| IMP* | A1 | 6 | 5 | ADD (41.37) |
| EX | null (exact; = D DPLL-b, E BP-t at these sizes) | — | — | PN (0.06) |
| NX | null | 576 | 846 | HAL (0.01) |
| PN | null | 1329 | 2002 | HAL (0.00) |
| RND | null (H RANDOM) | 5 | 4 | A2+ (11.60) |

### (c) CoT hypotheses (trace signature per theory)

- **ADD** (ADD-CONSTRAINT, B4): K16 PHANTOM-EDGE: treats Chemistry and Drama as conflicting (restates them among the conflicts or requires different days)
- **HAL** (HALLUC-CONSTRAINT, nuisance): occasionally restates a conflict that is not in the list, unrelated to the co-mention sentence
- **DROP** (DROP-LAST, B1): never uses the last-listed conflict (omitted when conflicts are restated)
- **FF** (FIRST-FIT, C1): K7 assigns exams in the order of the exam list, earliest free day, never revisits
- **DSAT** (DSATUR, C2): repeatedly picks the exam with the most distinct days already used by its conflicts
- **OFF** (ONLINE-FIRST-FIT, C4): K7 assigns each exam the first time it appears in the conflict list, using only conflicts read so far, never revisits
- **A2+** (A2-ADDED-SENTENCE, A2): no specific mention of the co-mentioned pair; more errors whenever any extra sentence is present
- **IMP*** (ALWAYS-IMPOSSIBLE, A1): declares the schedule impossible without a constructed attempt
- **EX** (EXACT, null (exact; = D DPLL-b, E BP-t at these sizes)): systematic assignment with backtracking or constraint propagation; checks every conflict at the end; ignores the co-mention sentence
- **NX** (NOISY-EXACT, null): systematic search with one unsystematic slip (a mis-copied constraint) at a random point
- **PN** (PERCEPTION-NOISE, null): restates one constraint wrongly (dropped conflict or flipped switch) and solves the misread problem
- **RND** (RANDOM, null (H RANDOM)): no systematic construction

Cell-specific trace predictions (e.g. which disjunct is committed to, the state sizes of `ONL(k)`, the counter-model to look for) are in the JSONL `trace_predictions` field.

### Discrimination as likelihood

Theories are grouped by their predicted outcome pattern over this set's contrasts. Observing a group's pattern moves weight toward that group.

- The last column gives the smallest expected log-LR per replicate between a group member and any theory outside the group (larger = faster discrimination).
- Theories inside a group differ only at cell level, if at all; cell-level separation is in the nearest-rival column above.

| observed pattern | weight moves toward | min log-LR/rep vs outside (pair) |
|---|---|---|
| C1:POS C2:ZERO | ADD | 24.82 (ADD vs DSAT) |
| C1:ZERO C2:ZERO | HAL, DROP, FF, DSAT, OFF, IMP*, EX, NX, PN, RND | 0.35 (NX vs A2+) |
| C1:ZERO C2:POS | A2+ | 0.40 (A2+ vs NX) |

Any other pattern is unexplained by a single strategy. It is fitted as a mixture: each contrast constrains Σ_h π_h Δ_h. Residual mass goes to the 'none of the above' component.

**Nearest-competitor separation (required pairs).**

For each target member: its two nearest rivals in this set, the expected log-LR per replicate, and, if that is < 0.2 nats, the sets that do separate the pair.

| target | rival | log-LR/rep here | separated in (log-LR/rep) |
|---|---|---|---|
| ADD | FF | 24.82 |  |
| ADD | DSAT | 24.82 |  |

## E6b. Online edge order: same graph, conflicts listed in two orders

- **Reasoning question.** Does the model colour exams as their conflicts are read, never revisiting, so that the listed order of the same conflicts changes feasibility?
- **Target members (this vertical).** ONLINE-FIRST-FIT.
- **Competitors (other families) and nulls.** FIRST-FIT, DSATUR, DROP-LAST, HALLUC-CONSTRAINT, ADD-CONSTRAINT; EXACT, NOISY-EXACT, PERCEPTION-NOISE, RANDOM.
- **Varied:** order of the conflict list (closing-late vs closing-early, found by search).
- **Controlled:** identical vertex list, identical conflict multiset, same prompt otherwise.

### Full prompts (selected cells)

**E6b / E6b·closing-late**: ground truth: **feasible (any proper 3-day schedule), e.g. {Algebra:Mon, Biology:Mon, Chemistry:Mon, Drama:Tue, Economics:Tue, French:Tue, Geography:Wed, History:Mon} proper**

```
A school must schedule 8 exams (Algebra, Biology, Chemistry, Drama, Economics, French, Geography, History) into 3 days: Monday, Tuesday, Wednesday. Two exams that share a student cannot be on the same day.
These pairs of exams share a student:
- Chemistry and French
- Chemistry and Drama
- Algebra and Geography
- Chemistry and Economics
- Economics and Geography
- Biology and French
- Biology and Economics
- French and History
- French and Geography

Assign each exam to a day so that no two exams sharing a student are on the same day, or say that it is impossible.
Think it through as carefully as you need. Finish with one line of JSON: either {"schedule": {"<exam>": "<day>", ...}} or {"impossible": true}.
```

**E6b / E6b·closing-early**: ground truth: **feasible (any proper 3-day schedule), e.g. {Algebra:Mon, Biology:Mon, Chemistry:Mon, Drama:Tue, Economics:Tue, French:Tue, Geography:Wed, History:Mon} proper**

```
A school must schedule 8 exams (Algebra, Biology, Chemistry, Drama, Economics, French, Geography, History) into 3 days: Monday, Tuesday, Wednesday. Two exams that share a student cannot be on the same day.
These pairs of exams share a student:
- Chemistry and French
- French and Geography
- Algebra and Geography
- French and History
- Biology and Economics
- Biology and French
- Chemistry and Economics
- Chemistry and Drama
- Economics and Geography

Assign each exam to a day so that no two exams sharing a student are on the same day, or say that it is impossible.
Think it through as carefully as you need. Finish with one line of JSON: either {"schedule": {"<exam>": "<day>", ...}} or {"impossible": true}.
```

### (a) Output hypotheses: every cell

| cell | g | ADD | HAL | DROP | FF | DSAT | OFF | A2+ | IMP* | EX | NX | PN | RND |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E6b·closing-late | feasible | ok | 0.10 | ok | ok | ok | ERR | 0.10 | IMP | ok | 0.14 | 0.03 | 0.96 |
| E6b·closing-early | feasible | ok | 0.10 | ok | ok | ok | ok | 0.10 | IMP | ok | 0.14 | 0.03 | 0.96 |

CSP entries: `ok` = valid answer, `ERR` = invalid schedule or assignment, `IMP` = declared impossible (an error, since every item is feasible), decimals = P(error).

### (b) Eval hypotheses: pre-registered contrasts (Δ under π_h = 1, in pp)

| contrast | definition | ADD | HAL | DROP | FF | DSAT | OFF | A2+ | IMP* | EX | NX | PN | RND |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E6b-C1 | error rate: closing-late − closing-early | +0 | +0 | +0 | +0 | +0 | +80 | +0 | +0 | +0 | +0 | +0 | +0 |

**Weight sensitivity per theory.**

- Replicates of this cell set (frames × samples) needed to detect π_h ≥ 0.15 against EXACT (lower 95% bound > 0).
- Replicates needed to bound π_h ≤ 0.10 (upper 95%) if h is absent.
- The nearest rival, with the expected log-LR per replicate favouring h over it if h is true.

| theory | family | reps to detect π≥0.15 | reps to bound π≤0.10 | nearest rival (nats/rep) |
|---|---|---|---|---|
| ADD | B4 | ∞ (= EXACT here) | ∞ | DROP (0.00) |
| HAL | nuisance | ∞ (= EXACT here) | ∞ | A2+ (0.00) |
| DROP | B1 | ∞ (= EXACT here) | ∞ | ADD (0.00) |
| FF | C1 | ∞ (= EXACT here) | ∞ | ADD (0.00) |
| DSAT | C2 | ∞ (= EXACT here) | ∞ | HAL (6.59) |
| OFF | C4 | 46 | 39 | DSAT (8.27) |
| A2+ | A2 | ∞ (= EXACT here) | ∞ | HAL (0.00) |
| IMP* | A1 | 23 | 20 | RND (11.95) |
| EX | null (exact; = D DPLL-b, E BP-t at these sizes) | — | — | HAL (0.00) |
| NX | null | 5057 | 7611 | HAL (0.02) |
| PN | null | 1263 | 2224 | HAL (0.08) |
| RND | null (H RANDOM) | 21 | 17 | NX (3.49) |

### (c) CoT hypotheses (trace signature per theory)

- **ADD** (ADD-CONSTRAINT, B4): no co-mention sentence; as EXACT
- **HAL** (HALLUC-CONSTRAINT, nuisance): occasionally restates a conflict that is not in the list, unrelated to the co-mention sentence
- **DROP** (DROP-LAST, B1): never uses the last-listed conflict (omitted when conflicts are restated)
- **FF** (FIRST-FIT, C1): K7 assigns exams in the order of the exam list, earliest free day, never revisits
- **DSAT** (DSATUR, C2): repeatedly picks the exam with the most distinct days already used by its conflicts
- **OFF** (ONLINE-FIRST-FIT, C4): K7 assigns each exam the first time it appears in the conflict list, using only conflicts read so far, never revisits; predicted clash on [['Economics', 'Geography'], ['French', 'Geography']]
- **A2+** (A2-ADDED-SENTENCE, A2): no specific mention of the co-mentioned pair; more errors whenever any extra sentence is present
- **IMP*** (ALWAYS-IMPOSSIBLE, A1): declares the schedule impossible without a constructed attempt
- **EX** (EXACT, null (exact; = D DPLL-b, E BP-t at these sizes)): systematic assignment with backtracking or constraint propagation; checks every conflict at the end; ignores the co-mention sentence
- **NX** (NOISY-EXACT, null): systematic search with one unsystematic slip (a mis-copied constraint) at a random point
- **PN** (PERCEPTION-NOISE, null): restates one constraint wrongly (dropped conflict or flipped switch) and solves the misread problem
- **RND** (RANDOM, null (H RANDOM)): no systematic construction

Cell-specific trace predictions (e.g. which disjunct is committed to, the state sizes of `ONL(k)`, the counter-model to look for) are in the JSONL `trace_predictions` field.

### Discrimination as likelihood

Theories are grouped by their predicted outcome pattern over this set's contrasts. Observing a group's pattern moves weight toward that group.

- The last column gives the smallest expected log-LR per replicate between a group member and any theory outside the group (larger = faster discrimination).
- Theories inside a group differ only at cell level, if at all; cell-level separation is in the nearest-rival column above.

| observed pattern | weight moves toward | min log-LR/rep vs outside (pair) |
|---|---|---|
| C1:ZERO | ADD, HAL, DROP, FF, DSAT, A2+, IMP*, EX, NX, PN, RND | 4.59 (RND vs OFF) |
| C1:POS | OFF | 8.27 (OFF vs DSAT) |

Any other pattern is unexplained by a single strategy. It is fitted as a mixture: each contrast constrains Σ_h π_h Δ_h. Residual mass goes to the 'none of the above' component.

**Nearest-competitor separation (required pairs).**

For each target member: its two nearest rivals in this set, the expected log-LR per replicate, and, if that is < 0.2 nats, the sets that do separate the pair.

| target | rival | log-LR/rep here | separated in (log-LR/rep) |
|---|---|---|---|
| OFF | DSAT | 8.27 |  |
| OFF | NX | 11.19 |  |

## E6c. Converse constraints in SAT: implication-rendered rules, converse-UNSAT vs converse-SAT twins × clause order

- **Reasoning question.** Does the model read 'if switch X is on then switch Y is on' as 'iff', so that it declares a satisfiable panel impossible exactly when the converse-strengthened rules are unsatisfiable? Does listed rule order change the answer (online clause-by-clause commitment)?
- **Target members (this vertical).** BICOND-SAT, ONLINE-CLAUSE.
- **Competitors (other families) and nulls.** C1-GREEDY-SAT, UP+DEFAULT, ALWAYS-IMPOSSIBLE; EXACT, NOISY-EXACT, PERCEPTION-NOISE, RANDOM.
- **Varied:** twin A (converse closure UNSAT) vs twin B (one rule's target changed: converse closure SAT); two rule orders.
- **Controlled:** both twins satisfiable; the twins differ in one switch name in one rule; order variants have identical rule multisets.

### Full prompts (selected cells)

**E6c / E6c·A·order1**: ground truth: **satisfiable, e.g. on=['Dune', 'Frost', 'Garnet'] satisfies all rules**

```
A control panel has eight switches: Amber, Brass, Cobalt, Dune, Ember, Frost, Garnet, Hazel. These rules must all hold:
1. If the Hazel switch is on, then the Garnet switch is on.
2. If the Amber switch is on, then the Brass switch is on.
3. The Brass switch is off.
4. At least one of the Dune, Ember and Hazel switches is on.
5. If the Frost switch is on, then the Garnet switch is on.
6. If the Ember switch is on, then the Frost switch is on.
7. At least one of the Brass, Cobalt and Dune switches is on.
8. If the Amber switch is on, then the Garnet switch is on.
9. If the Dune switch is on, then the Frost switch is on.

Find a setting of the switches (each on or off) that satisfies every rule, or say that it is impossible.
Think it through as carefully as you need. Finish with one line of JSON: either {"on": ["<switch>", ...]} or {"impossible": true}.
```

**E6c / E6c·B·order1**: ground truth: **satisfiable, e.g. on=['Dune', 'Frost', 'Garnet'] satisfies all rules**

```
A control panel has eight switches: Amber, Brass, Cobalt, Dune, Ember, Frost, Garnet, Hazel. These rules must all hold:
1. If the Hazel switch is on, then the Garnet switch is on.
2. If the Amber switch is on, then the Brass switch is on.
3. The Brass switch is off.
4. At least one of the Dune, Ember and Hazel switches is on.
5. If the Frost switch is on, then the Garnet switch is on.
6. If the Ember switch is on, then the Cobalt switch is on.
7. At least one of the Brass, Cobalt and Dune switches is on.
8. If the Amber switch is on, then the Garnet switch is on.
9. If the Dune switch is on, then the Frost switch is on.

Find a setting of the switches (each on or off) that satisfies every rule, or say that it is impossible.
Think it through as carefully as you need. Finish with one line of JSON: either {"on": ["<switch>", ...]} or {"impossible": true}.
```

### (a) Output hypotheses: every cell

| cell | g | BICs | OCL | C1s | UPd | IMP* | EX | NX | PN | RND |
|---|---|---|---|---|---|---|---|---|---|---|
| E6c·A·order1 | SAT | IMP | ERR | IMP | ERR | IMP | ok | 0.14 | 0.15 | 0.95 |
| E6c·A·order2 | SAT | IMP | ok | IMP | ERR | IMP | ok | 0.14 | 0.15 | 0.95 |
| E6c·B·order1 | SAT | ok | ERR | IMP | ERR | IMP | ok | 0.14 | 0.17 | 0.95 |
| E6c·B·order2 | SAT | ok | ok | IMP | ERR | IMP | ok | 0.14 | 0.17 | 0.95 |

CSP entries: `ok` = valid answer, `ERR` = invalid schedule or assignment, `IMP` = declared impossible (an error, since every item is feasible), decimals = P(error).

### (b) Eval hypotheses: pre-registered contrasts (Δ under π_h = 1, in pp)

| contrast | definition | BICs | OCL | C1s | UPd | IMP* | EX | NX | PN | RND |
|---|---|---|---|---|---|---|---|---|---|---|
| E6c-C1 | error rate: twin A − twin B | +80 | -0 | +0 | +0 | +0 | +0 | +0 | -2 | +0 |
| E6c-C2 | error rate: order 1 − order 2 | -0 | +80 | +0 | +0 | +0 | +0 | +0 | +0 | +0 |

**Weight sensitivity per theory.**

- Replicates of this cell set (frames × samples) needed to detect π_h ≥ 0.15 against EXACT (lower 95% bound > 0).
- Replicates needed to bound π_h ≤ 0.10 (upper 95%) if h is absent.
- The nearest rival, with the expected log-LR per replicate favouring h over it if h is true.

| theory | family | reps to detect π≥0.15 | reps to bound π≤0.10 | nearest rival (nats/rep) |
|---|---|---|---|---|
| BICs | B4 | 23 | 20 | C1s (13.93) |
| OCL | C4 | 23 | 20 | PN (17.40) |
| C1s | C1 | 12 | 10 | IMP* (0.00) |
| UPd | B1 | 12 | 10 | RND (18.68) |
| IMP* | A1 | 12 | 10 | C1s (0.00) |
| EX | null (exact; = D DPLL-b, E BP-t at these sizes) | — | — | NX (0.03) |
| NX | null | 2529 | 3806 | PN (0.01) |
| PN | null | 1161 | 1701 | NX (0.01) |
| RND | null (H RANDOM) | 11 | 9 | PN (6.26) |

### (c) CoT hypotheses (trace signature per theory)

- **BICs** (BICOND-SAT, B4): K5 CONVERSE: treats 'if X is on then Y is on' as also 'if Y is on then X is on'; derives a contradiction from the converses
- **OCL** (ONLINE-CLAUSE, C4): K7 goes through the rules in listed order, satisfying each unsatisfied rule by switching on/off its first unassigned switch, never revisits
- **C1s** (C1-GREEDY-SAT, C1): assigns switches in panel order (Amber…Hazel), trying 'on' first, no backtracking; gives up at the first dead end
- **UPd** (UP+DEFAULT, B1): propagates forced settings (e.g. 'X is off' → consequences), then sets every remaining switch off
- **IMP*** (ALWAYS-IMPOSSIBLE, A1): declares the schedule impossible without a constructed attempt
- **EX** (EXACT, null (exact; = D DPLL-b, E BP-t at these sizes)): systematic assignment with backtracking or constraint propagation; checks every conflict at the end; ignores the co-mention sentence
- **NX** (NOISY-EXACT, null): systematic search with one unsystematic slip (a mis-copied constraint) at a random point
- **PN** (PERCEPTION-NOISE, null): restates one constraint wrongly (dropped conflict or flipped switch) and solves the misread problem
- **RND** (RANDOM, null (H RANDOM)): no systematic construction

Cell-specific trace predictions (e.g. which disjunct is committed to, the state sizes of `ONL(k)`, the counter-model to look for) are in the JSONL `trace_predictions` field.

### Discrimination as likelihood

Theories are grouped by their predicted outcome pattern over this set's contrasts. Observing a group's pattern moves weight toward that group.

- The last column gives the smallest expected log-LR per replicate between a group member and any theory outside the group (larger = faster discrimination).
- Theories inside a group differ only at cell level, if at all; cell-level separation is in the nearest-rival column above.

| observed pattern | weight moves toward | min log-LR/rep vs outside (pair) |
|---|---|---|
| C1:POS C2:ZERO | BICs | 13.93 (BICs vs IMP*) |
| C1:ZERO C2:POS | OCL | 17.40 (OCL vs PN) |
| C1:ZERO C2:ZERO | C1s, UPd, IMP*, EX, NX, PN, RND | 9.07 (RND vs BICs) |

Any other pattern is unexplained by a single strategy. It is fitted as a mixture: each contrast constrains Σ_h π_h Δ_h. Residual mass goes to the 'none of the above' component.

**Nearest-competitor separation (required pairs).**

For each target member: its two nearest rivals in this set, the expected log-LR per replicate, and, if that is < 0.2 nats, the sets that do separate the pair.

| target | rival | log-LR/rep here | separated in (log-LR/rep) |
|---|---|---|---|
| BICs | C1s | 13.93 |  |
| BICs | IMP* | 13.93 |  |
| OCL | PN | 17.40 |  |
| OCL | NX | 17.63 |  |

## E7. Trace interventions (instrument; templates)

**What E7 is.** E7 re-uses erred cells from E1L, E2, E3 and E5. The model's *own* thinking prefix, up to the point where it first processes the critical premise, is prefilled. One of four length-matched inserts is appended, and generation continues.

- So the exact prompt contains the model's trace, which does not exist yet.
- Below is the template applied to E1L / base1·base. The illustrative prefix is written by us and is marked as such.

**What it measures.** Whether the absence of the dropped alternative is causally implicated in the error: the dropped-alternative flip rate minus the control flip rate, paired by item.

**Weight readout.** A paired flip difference δ_E7 enters as evidence on the share of errors caused by a missing alternative.

- That share is a lower bound on π_restriction + π_SAMPLE among erring items.
- δ_E7 ≈ 0 with post-hoc early-exit curves bounds that share at the upper 95% limit of δ_E7.

```
Here are some statements:
1. Either the cup is not green and the bag is wet, or the box is not red and the cup is round.
2. Either the cup is not round, or the jar is cold.
3. Either the bag is wet and the cup is round, or the jar is blue and the bag is soft.
4. Either the box is heavy and the bag is wet, or the jar is not cold and the box is red.
5. If the bag is wet, then the box is heavy.
6. The box is not red.

Question: Does it follow that the jar is cold?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
<think>
[ILLUSTRATIVE PREFIX — in the study this is the model's own trace up to its first use of statement 5] Statement 5 says the cup is not green. In statement 2 the second option needs the cup to be not green and the jar to be cold, so let me see which option of statement 2 holds…
{INSERT}
```

| insert | text (unique counter-model filled in) | predicted effect by source of the error |
|---|---|---|
| dropped-alternative | Wait, I should check one more case: the box is not red; the box is heavy; the jar is blue; the jar is not cold; the cup is not green; the cup is not round; the bag is soft; the bag is wet. Does that case satisfy every statement? | MATCH-L: flip to NO (P ≥ .5); MATCH-A: flip to NO (P ≥ .5); ETR-default: flip to NO (P ≥ .5); FIRST: flip to NO (P ≥ .5); SAMPLE-3: flip to NO (P ≥ .5): a supplied counterexample also defeats sampling; NOISY-EXACT: flip ≈ control rate (re-checking prompt); post-hoc (answer fixed before trace): no flip (≤ control + 5 pp) |
| control | Wait, I should check one more case: the box is red; the box is heavy; the jar is blue; the jar is not cold; the cup is not green; the cup is round; the bag is soft; the bag is not wet. Does that case satisfy every statement? | MATCH-L: flip ≤ .10; MATCH-A: flip ≤ .10; ETR-default: flip ≤ .10; FIRST: flip ≤ .10; SAMPLE-3: flip ≤ .10; NOISY-EXACT: flip ≈ dropped-alternative rate; post-hoc (answer fixed before trace): no flip |
| commitment | So the first option in statement 1 is the one that holds. | FIRST: already committed: no change; MATCH-L: small increase in YES on items where the first disjunct is not the matched one; EXACT: little effect (verifies anyway); post-hoc (answer fixed before trace): no change |
| early-exit | </think>
ANSWER: | restriction members: answer at 25% / 50% / 75% = final answer only after the critical premise has been processed; post-hoc (answer fixed before trace): final answer already decodable at 25%; EXACT: answer stabilises only after the counter-model search |

The control insert is a scenario consistent with the premises in which the probe is *true*, so it is matched in length and content type. The JSONL carries these three templates as `eval_id = E7` items.

## Library coverage: which sets can push which theories' weights toward zero

**What an entry means.** The expected log-LR per replicate of that set (one sample per cell), favouring the theory over the *closest null*, if the theory is true.

- The nulls are: exact solving, NOISY-EXACT, PERCEPTION-NOISE and RANDOM. For a null's own row, the comparison is with the closest *other* null.
- ● ≥ 1.0 nats (the set drives π toward 0 quickly when the model is not using the theory); ◐ 0.2–1.0; · < 0.2 (the set cannot separate it from the nulls); blank = not defined in this domain.
- **†** = tied (< 0.01 nats) in this set with at least one *non-null* rival. Ties are listed below the table, and every tie is broken in another set (see the pair check).

| theory | E1 | E1L | E2 | E3 | E4 | E5 | E6a | E6b | E6c |
|---|---|---|---|---|---|---|---|---|---|
| FST (B4) | ● | ● | ·† | ●† |  | ● |  |  |  |
| ML (B4) | ● | ●† | ·† | ·† |  | ·† |  |  |  |
| MA (B4) | ●† | ●† | ·† | ·† | ● | ·† |  |  |  |
| ETR (B4/C4) | ●† | ●† | ·† | ●† | ● | ·† |  |  |  |
| E1p (B4/C4) | ● | ●† | ● | ● | ● | ·† |  |  |  |
| MM (B4) | ·† | ·† | ●† | ·† |  | ●† |  |  |  |
| MMe (B4) | ●† | ●† | ●† | ·† |  | ●† |  |  |  |
| MMG (B4) | ·† | ·† | ● | ·† |  | ●† |  |  |  |
| BIC (B4) | ·† | ●† | ●† | ·† |  | ●† |  |  |  |
| CWm (B4) | ·† | ●† | ● | ·† | ●† | ● |  |  |  |
| CWc (B4) | ·† | ·† | ● | ·† |  | ●† |  |  |  |
| O1 (C4) | ● | ●† | ● | ● |  | ●† |  |  |  |
| O2 (C4) | ● | ●† | ·† | ● |  | ● |  |  |  |
| O4 (C4) | ·† | ● | ·† |  |  | ·† |  |  |  |
| PRI (A2) | ● | ●† | ● | ● | ● | ● |  |  |  |
| REC (A2) | ● | ●† | ● | ● | ● | ● |  |  |  |
| AFF (A2) | ●† | ● | ● | ·† | ●† | ●† |  |  |  |
| YES* (A1) | ●† | ●† | ●† | ·† | ●† | ● |  |  |  |
| NO* (A1) | ● | ●† | ● | ●† | ·† | ● |  |  |  |
| UP1 (B1) | ·† | ●† | ·† | ·† |  | ● |  |  |  |
| C1 (C1) | ●† | ● | ● | ·† |  | ●† |  |  |  |
| S3 (H) | ● | ● | ● | ● | ◐ | ● |  |  |  |
| EX (null (exact; = D DPLL-b, E BP-t at these sizes)) | · | · | ◐ | ● | · | · | · | · | · |
| NX (null) | · | · | ◐ | ◐ | · | · | · | · | · |
| PN (null) | ◐ | · | ◐ | ● | ◐ | ● | · | · | · |
| RND (null (H RANDOM)) | ● | ● | ● | ● | ● | ● | ● | ● | ● |
| ETR0 (B4/C4) | ●† | ●† | ·† | ●† | ·† | ·† |  |  |  |
| O8 (C4) |  | ·† |  | ● |  |  |  |  |  |
| ETR·R2 (B4/C4) |  |  | ● |  |  | ● |  |  |  |
| E1p·R2 (B4/C4) |  |  | ● |  |  | ● |  |  |  |
| BICp (B4) |  |  | ● |  |  |  |  |  |  |
| O32 (C4) |  |  |  | ● |  |  |  |  |  |
| O128 (C4) |  |  |  | ● |  |  |  |  |  |
| ADD (B4) |  |  |  |  |  |  | ● | ●† |  |
| HAL (nuisance) |  |  |  |  |  |  | · | ·† |  |
| DROP (B1) |  |  |  |  |  |  | ● | ●† |  |
| FF (C1) |  |  |  |  |  |  | ●† | ●† |  |
| DSAT (C2) |  |  |  |  |  |  | ●† | ● |  |
| OFF (C4) |  |  |  |  |  |  | ● | ● |  |
| A2+ (A2) |  |  |  |  |  |  | ◐ | ·† |  |
| IMP* (A1) |  |  |  |  |  |  | ● | ● | ●† |
| BICs (B4) |  |  |  |  |  |  |  |  | ● |
| OCL (C4) |  |  |  |  |  |  |  |  | ● |
| C1s (C1) |  |  |  |  |  |  |  |  | ●† |
| UPd (B1) |  |  |  |  |  |  |  |  | ● |

**Ties within sets** (identical predictions on every cell of that set):

- E2: {MM, MMe}; {YES*, BIC}; {ETR, ETR0, FST, MA, ML, O2, O4, UP1}
- E3: {FST, NO*}; {AFF, YES*, BIC, C1, CWc, CWm, MA, ML, MMG, MM, MMe, UP1}; {ETR, ETR0}
- E1L: {BIC, CWm}; {CWc, MMG, MM, O8}; {E1p, ML}; {NO*, PRI, REC, UP1}; {O1, O2}; {YES*, ETR, ETR0, MA, MMe}
- E5: {CWc, MMG, MM, MMe}; {E1p, ETR, ETR0, MA, ML, O4}; {AFF, BIC, C1, O1}
- E1: {BIC, CWc, CWm, MMG, MM, O4, UP1}; {MA, MMe}; {AFF, YES*, C1}; {ETR, ETR0}
- E4: {ETR0, NO*}; {AFF, YES*, CWm}
- E6b: {A2+, HAL}; {ADD, DROP, FF}
- E6a: {DSAT, FF}
- E6c: {IMP*, C1s}

**Pairs not separated anywhere in the library** (expected log-LR per replicate < 0.01 in every shared set, i.e. identical predictions):

- ALWAYS-IMPOSSIBLE vs C1-GREEDY-SAT (shared sets: E6c)

This tie is expected. On these instances, panel-order greedy without backtracking dead-ends and gives up, so it says IMPOSSIBLE just like the constant cue.
Separating C1 greedy from 'always impossible' needs SAT instances where greedy succeeds, which is the C-family SAT vertical's job. Here both serve only as false-IMPOSSIBLE competitors to BICOND-SAT, which differs from both on twin B.

Every other pair of theories is separated (expected log-LR ≥ 0.01 nats/replicate) in at least one set. A theory can be tied with *different* rivals in different sets; what matters is that each pair is separated somewhere. The table below lists, for each theory, the three rivals that are hardest to separate across the whole library (the best set for each, with its log-LR per replicate). Rivals with < 0.2 nats/replicate in their best set need many frames; the per-set weight-sensitivity tables give the numbers.

| theory | hardest rival 1 | hardest rival 2 | hardest rival 3 |
|---|---|---|---|
| FST (B4) | E1p: 21.09 in E1 | E1p·R2: 21.09 in E2 | ETR·R2: 21.09 in E2 |
| ML (B4) | S3: 5.85 in E1 | EX: 7.03 in E1 | MA: 7.03 in E1 |
| MA (B4) | S3: 5.72 in E1 | ML: 7.03 in E1 | O128: 7.03 in E3 |
| ETR (B4/C4) | ETR0: 7.03 in E4 | RND: 19.14 in E2 | E1p: 21.09 in E3 |
| E1p (B4/C4) | E1p·R2: 12.30 in E5 | O4: 14.06 in E1 | RND: 19.88 in E3 |
| MM (B4) | O128: 7.03 in E3 | MMG: 10.55 in E2 | O32: 10.55 in E3 |
| MMe (B4) | O128: 7.03 in E3 | O32: 10.55 in E3 | MMG: 14.06 in E1 |
| MMG (B4) | O128: 7.03 in E3 | MM: 10.55 in E2 | O32: 10.55 in E3 |
| BIC (B4) | BICp: 7.03 in E2 | O128: 7.03 in E3 | O32: 10.55 in E3 |
| CWm (B4) | O128: 7.03 in E3 | O32: 10.55 in E3 | O8: 14.06 in E3 |
| CWc (B4) | O128: 7.03 in E3 | O32: 10.55 in E3 | O8: 14.06 in E3 |
| O1 (C4) | O8: 21.09 in E3 | RND: 22.08 in E3 | O32: 24.61 in E3 |
| O2 (C4) | O8: 5.27 in E1L | O32: 7.03 in E3 | O128: 10.55 in E3 |
| O4 (C4) | NX: 3.35 in E1L | EX: 3.52 in E1L | O8: 3.52 in E1L |
| PRI (A2) | E1p·R2: 19.34 in E2 | RND: 22.08 in E3 | NO*: 24.61 in E5 |
| REC (A2) | RND: 22.08 in E3 | NO*: 35.16 in E3 | O1: 36.91 in E2 |
| AFF (A2) | O128: 7.03 in E3 | O32: 10.55 in E3 | O8: 14.06 in E3 |
| YES* (A1) | BICp: 7.03 in E2 | O128: 7.03 in E3 | O32: 10.55 in E3 |
| NO* (A1) | RND: 22.08 in E3 | PRI: 24.61 in E5 | REC: 35.16 in E3 |
| UP1 (B1) | O128: 7.03 in E3 | EX: 8.79 in E5 | O4: 8.79 in E5 |
| C1 (C1) | O128: 7.03 in E3 | O32: 10.55 in E3 | O8: 14.06 in E3 |
| S3 (H) | MA: 7.58 in E1 | ML: 7.75 in E1 | EX: 7.93 in E1 |
| EX (null (exact; = D DPLL-b, E BP-t at these sizes)) | HAL: 0.08 in E6a | A2+: 0.70 in E6a | NX: 2.52 in E3 |
| NX (null) | HAL: 0.02 in E6b | A2+: 0.35 in E6a | PN: 1.51 in E5 |
| PN (null) | HAL: 0.08 in E6b | A2+: 0.44 in E6a | NX: 1.01 in E5 |
| RND (null (H RANDOM)) | BICs: 9.07 in E6c | C1s: 9.07 in E6c | OCL: 9.07 in E6c |
| ETR0 (B4/C4) | ETR: 7.03 in E4 | RND: 19.14 in E2 | E1p: 21.09 in E3 |
| O8 (C4) | O32: 3.52 in E3 | O4: 3.52 in E1L | O2: 5.27 in E1L |
| ETR·R2 (B4/C4) | RND: 16.19 in E2 | BICp: 17.58 in E2 | S3: 21.03 in E2 |
| E1p·R2 (B4/C4) | E1p: 12.30 in E5 | RND: 16.19 in E2 | PRI: 19.34 in E2 |
| BICp (B4) | YES*: 7.03 in E2 | BIC: 7.03 in E2 | ETR·R2: 17.58 in E2 |
| O32 (C4) | O128: 3.52 in E3 | O8: 3.52 in E3 | O2: 7.03 in E3 |
| O128 (C4) | O32: 3.52 in E3 | NX: 5.72 in E3 | AFF: 7.03 in E3 |
| ADD (B4) | DSAT: 24.82 in E6a | FF: 24.82 in E6a | A2+: 28.09 in E6a |
| HAL (nuisance) | NX: 0.01 in E6a | EX: 0.09 in E6a | PN: 0.13 in E6b |
| DROP (B1) | RND: 47.79 in E6a | A2+: 59.57 in E6a | NX: 62.40 in E6a |
| FF (C1) | EX: 9.96 in E6a | PN: 10.02 in E6a | HAL: 10.04 in E6a |
| DSAT (C2) | EX: 9.96 in E6a | PN: 10.02 in E6a | HAL: 10.04 in E6a |
| OFF (C4) | RND: 47.79 in E6a | A2+: 59.57 in E6a | NX: 62.40 in E6a |
| A2+ (A2) | NX: 0.40 in E6a | HAL: 0.47 in E6a | PN: 0.53 in E6a |
| IMP* (A1) | C1s: 0.00 in E6c | BICs: 13.93 in E6c | OCL: 27.86 in E6c |
| BICs (B4) | IMP*: 13.93 in E6c | C1s: 13.93 in E6c | PN: 17.61 in E6c |
| OCL (C4) | PN: 17.40 in E6c | NX: 17.63 in E6c | EX: 18.28 in E6c |
| C1s (C1) | IMP*: 0.00 in E6c | BICs: 13.93 in E6c | RND: 18.68 in E6c |
| UPd (B1) | RND: 18.68 in E6c | PN: 25.75 in E6c | NX: 26.25 in E6c |
