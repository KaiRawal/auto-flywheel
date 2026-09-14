#!/bin/bash
# Demo: background training + pgrep polling so lint/tests run in parallel (your ask #5).
set -e
LAB="$(cd "$(dirname "$0")/.." && pwd)"
echo "=== pgrep concurrency demo ($LAB) ==="
echo "disk:" && df -h / | tail -1
echo "mem:" && vm_stat | head -2
cd "$LAB"

# Fire two toy trainings in background (simulating long ML jobs)
nohup .venv/bin/python "$LAB/problems/toy-tabular/train.py" --out /tmp/pgrep_demo1.joblib > /tmp/pgrep_demo1.log 2>&1 &
PID1=$!
nohup .venv/bin/python "$LAB/problems/toy-tabular/train.py" --out /tmp/pgrep_demo2.joblib > /tmp/pgrep_demo2.log 2>&1 &
PID2=$!
echo "pids $PID1 $PID2 — polling via pgrep while running ruff in parallel"

# Do useful work while they train
timeout 60 .venv/bin/python -m ruff check . && echo "ruff done while training"

# Poll (not sleep 590) — the flywheel-executor pattern
while kill -0 $PID1 2>/dev/null || kill -0 $PID2 2>/dev/null; do sleep 1; done

echo "both trainings done:"
cat /tmp/pgrep_demo1.log | tail -1
cat /tmp/pgrep_demo2.log | tail -1
rm /tmp/pgrep_demo1.joblib /tmp/pgrep_demo2.joblib /tmp/pgrep_demo1.log /tmp/pgrep_demo2.log
echo "demo ok"
