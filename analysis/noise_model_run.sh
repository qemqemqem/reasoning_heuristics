# The noise-model evaluation (docs/NOISE_MODEL.md), one step after another: bash analysis/noise_model_run.sh <step> ...
#   diagnose | fits:<cand> | stage0:<cand> | m0check   (each step uses 3 worker processes, niced)
# e.g. remote-run start nm-eval -- bash analysis/noise_model_run.sh diagnose fits:KEQ stage0:KEQ
export OMP_NUM_THREADS=1 PYTHONPATH=src
OUT=analysis/out/noise_model
mkdir -p $OUT
for step in "$@"; do
  kind=${step%%:*}; cand=${step#*:}
  echo "=== $(date +%T) $step"
  case $kind in
    m0check) nice -n 10 python analysis/noise_model_eval.py fits --noise M0 --only "C_E2/knapsack 2026-11-18-pc20-gpt-oss-20b" \
      --workers 3 --out $OUT/m0_check.json ;;
    diagnose) nice -n 10 python analysis/noise_model_eval.py diagnose --workers 3 --out $OUT/diagnosis.json ;;
    fits) nice -n 10 python analysis/noise_model_eval.py fits --noise "$cand" --workers 3 --out $OUT/fits_$cand.json ;;
    # the reach variants differ from their base only where reach < 6: knapsack (3) and A/H E5 SAT (4)
    fitsbits) nice -n 10 python analysis/noise_model_eval.py fits --noise "$cand" --only "C_E2/knapsack;AH_E5/SAT" \
      --workers 3 --out $OUT/fits_$cand.json ;;
    stage0bits) nice -n 10 python -m reasoning_heuristics.identify.recovery run --items data/items/pc20 --label pc20 \
      --units 'C_E2/knapsack;AH_E5/SAT' --scenarios mix,null_q,null_always --reps 100 --boot 100 --noise "$cand" \
      --workers 3 --out $OUT/stage0_pc20_$cand.json ;;
    stage0)
      units20='C_E2/colouring;C_E2/knapsack;AH_E5/SAT'
      [ "$cand" = SEQ ] && units20='C_E2/knapsack;AH_E5/SAT'
      nice -n 10 python -m reasoning_heuristics.identify.recovery run --items data/items/pc20 --label pc20 --units "$units20" \
        --scenarios mix,null_q,null_always --reps 100 --boot 100 --noise "$cand" --workers 3 --out $OUT/stage0_pc20_$cand.json
      nice -n 10 python -m reasoning_heuristics.identify.recovery run --items data/items/pc40 --label pc40 \
        --units 'C_E5/3-SAT (partial assignment given)' --scenarios mix,null_q,null_always --reps 100 --boot 100 \
        --noise "$cand" --workers 3 --out $OUT/stage0_pc40_$cand.json ;;
  esac
  echo "=== $(date +%T) done $step (exit $?)"
done
