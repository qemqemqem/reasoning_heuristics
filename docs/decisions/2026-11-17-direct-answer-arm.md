# 2026-11-17: a direct-answer arm alongside thinking

**Decision (Andrew, 2026-11-17).** Phase 1 stays mostly focused on thinking models at best effort. Every eval also runs in a **direct** condition, thinking off, on the same items. It is a secondary condition, not a diagnostic used only where one design needs it.

## Why

- **The theory notes already split the two regimes.** [theory/README.md](../theory/README.md) scores every family separately for direct answers and for thinking. Most of the Strong priors are direct-answer ones: constant defaults, the density cue, `UP-k` with k ≤ 3, and `POLARITY`. Under thinking, most of those drop to Weak or Contested.
- **Several predictions need both regimes:**
  - restriction (B4, including `ETR` and `MM`) should fall with thinking, the sharpest test of H6;
  - thinking should shift weight from class C to class S (O6 prediction 3, H3);
  - the paper skeleton's Figure 4 plots both regimes.
- **RASP-L's claim is sharpest without thinking.** One pass computes the answer, so the program is short and shallow. With thinking, the theory needs a per-step program that the trace repeats.
- **Phase 2 interpretability works on forward passes.** Attribution graphs are planned for no-CoT items only, so Phase 1 needs direct-mode evidence on the same checkpoints.
- **It is cheap.** Answers are about 10–200 output tokens, against about 10k with thinking: roughly 1% of the thinking cost.

## How

- **Models:**
  - the hybrid Qwen3 checkpoints (Qwen3-14B, Qwen3-32B) with thinking on and off, so that the contrast holds the weights fixed;
  - gpt-oss cannot turn reasoning off, so its `low` effort is a budget arm, not direct.
- **Prompt:** the item's prompt unchanged, plus a fixed system instruction to give only the final answer without working. The instruction is an experimental factor and is recorded in each run's manifest (DESIGN §5 rule 10).
- **Generation:** a small max_tokens (about 1,024). The scorer records `pre_answer_tokens`, so responses that reason in the visible output can be flagged or excluded.
- **Regimes:** a single-token answer is the 1P regime and a written-out structured answer is DS ([theory/README.md](../theory/README.md)).

## Open

- **Instance sizes.** Sizes calibrated for thinking (SCOPE §6 rule 1) may put direct answers at floor on witness tasks. Decision items are fine. A smaller-size cell for direct mode should be pre-registered before the study.
