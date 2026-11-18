# 40-per-cell item set (dev split): C E5

A larger version of C E5, for pilot-size model runs on the one C E5 unit whose recovery gates pass at this size: SAT with a given partial assignment (docs/RECOVERY.md, "Regenerated items: candidate units"). Same split and seed as the committed dev set (tier dev, seed 1); 40 items per design cell instead of 5:

```
python -m reasoning_heuristics.generate --vertical C --eval E5 --tier dev --seed 1 --per-cell 40 --out-dir DIR
```

- 680 items: colouring (k = 3) 200, 3-SAT 120, 3-SAT with a partial assignment given 120, colouring with a partial colouring given 80, propositional entailment 160. All from dev seeds, never the test split.
- The decompressed file is byte-identical to the file the recovery sweep validated at 40 per cell (sha256 `83377798967e038c…`, recorded in `data/recovery/pc40.json`). Regenerated from main's code at db57330 and compressed with `schema.item.compress`, as `review` does. The report's `path` field was set to the repo path.
- **What the gates allow.** On SAT with a given state, the mixture and both nulls pass at 40 per cell. But there GUC-DET from state and SC-DET from state predict the same answer on every item, so only their sum is identified, and the fit reports them as one group. The other C E5 units are descriptive only.
- Model runs on this set are in `data/runs/2026-11-18-pc40-*`.
- They are dev items: fine for preliminary results and calibration; the pre-registered study uses the test split.
