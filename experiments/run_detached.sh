#!/bin/sh
# Runs rounds 9 and 10 from start to finish on a remote machine: collect, retry, judge, retry, score. Needs OPENROUTER_API_KEY in the environment.
cd "$(dirname "$0")/.."
for r in v9_gap v10_report; do
  python3 experiments/run_$r.py --max-spend 30 > detached_$r.log 2>&1
  python3 experiments/run_$r.py --max-spend 30 >> detached_$r.log 2>&1
  python3 experiments/run_$r.py --max-spend 30 >> detached_$r.log 2>&1
  python3 experiments/run_$r.py --judge --max-spend 8 >> detached_$r.log 2>&1
  python3 experiments/run_$r.py --judge --max-spend 8 >> detached_$r.log 2>&1
  python3 experiments/analyze_$r.py > detached_$r.summary 2>&1
  echo "$r done $(date -u)" >> detached.done
done
echo ALL_DONE >> detached.done
