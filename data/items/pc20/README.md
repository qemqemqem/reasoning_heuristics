# 20-per-cell item sets (dev split)

Larger versions of three Stage 1 evals, for the pilot-size model runs that the recovery harness's gates allow (docs/RECOVERY.md, "Where the gates pass"). Same split and seed as the committed dev sets (tier dev, seed 1); 20 items per design cell instead of 5:

```
python -m reasoning_heuristics.generate --vertical C  --eval E2 --tier dev --seed 1 --per-cell 20 --out-dir DIR
python -m reasoning_heuristics.generate --vertical AH --eval E5 --tier dev --seed 1 --per-cell 20 --out-dir DIR
python -m reasoning_heuristics.generate --vertical C  --eval E1 --tier dev --seed 1 --per-cell 20 --out-dir DIR
```

- C E2: 800 items. A/H E5: 340. C E1: 240. All from dev seeds, never the test split.
- These are the exact files the recovery sweep at 20 per cell validated (its result files record their sha256). Model runs on them are in `data/runs/2026-11-18-pc20-*`.
- Only C E1 and C E2 share a prefix with the committed dev sets: C E1 contains all 60 dev items, C E2 75 of 200. A/H E5's base sequence depends on the per-cell count.
- They are dev items: fine for preliminary results and calibration; the pre-registered study uses the test split.
