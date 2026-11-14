# Vertical: `<heuristic class>`

*One file per heuristic class. A vertical collects everything needed to get evidence for or against "LLMs use this class of heuristic": the definition, the evals, the interpretability tests, and its row in the evidence table ([DESIGN.md §6](../DESIGN.md)).*

- **Status:** idea / designed / pilot run / full run
- **Owner:**

## 1. The class

- **Defining idea:** the mathematical principle, e.g. "commit to the locally best choice, never revise".
- **Taxonomy position:** where it sits in DESIGN.md §3 (Step 2).
- **Members:** the concrete heuristics in the zoo, per problem model.

| Problem model | Member heuristic | Reference implementation |
|---------------|------------------|--------------------------|
| | | `src/reasoning_heuristics/heuristics/...` |

- **Expressibility:** class C (constant depth: possible in one forward pass) or class S (sequential: needs chain of thought), with the argument or citation.
- **RASP-L sketch:** program outline and its length under the pre-registered measure. **Write this before any LLM data**, so Step 6 can test it rather than only explain it.

## 2. Behavioural evidence (evals)

**Predicted error signature.**

- Omission or commission?
- Infeasible, or feasible but suboptimal?
- Where on the hardness axis does it break: threshold behaviour on random instances?

**Discriminating items.** What separates this class from its nearest competitors? Name the competitors, and give the generator recipe for items where they disagree.

**Manipulation signatures.**

| Manipulation | Predicted change if the model uses this class | Predicted change under the nearest competitor |
|--------------|-----------------------------------------------|-----------------------------------------------|
| Premise / constraint order reversed | | |
| Re-themed / renamed | | |
| Rule inverted | | |
| Irrelevant constraint added | | |
| Size / density increased | | |
| Thinking budget increased | | |

**Process measures.** Predicted reasoning-token counts and confidence patterns.

**Eval designs.**

| ID | Item generator | Answer format | Metric | Supported if | Against if |
|----|----------------|---------------|--------|--------------|------------|
| E1 | | | | | |

## 3. Mechanistic evidence (interpretability)

- **State variables:** what the class says the model must represent (e.g. "the current partial assignment", "the surviving alternatives").
- **Probes:** where we expect each variable (layer and position) and the control task for selectivity.
- **Interventions:** what to patch or steer, and the predicted effect on the answer. Compare against the same intervention on the nearest competitor's variables, and on a random-init model.
- **Positive control:** a toy model known to implement this class (SIIT / ALTA / capacity toy). The pipeline must recover it.

| ID | Model | Method | Prediction | Supported if | Against if |
|----|-------|--------|------------|--------------|------------|
| M1 | | | | | |

## 4. Evidence-table row

What this vertical contributes to the table in DESIGN.md §6. Fill it in as results arrive.

| Behavioural lift over baseline | Mixture weight | Signatures matched | Process match | Probe selectivity | Intervention vs competitor | Control recovered | RASP-L length / class |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

## 5. Open questions
