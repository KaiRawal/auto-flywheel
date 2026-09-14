---
description: Abort a running flywheel — kills pids in flywheel-state.json and cleans runs/<problem>/<ts>/sandbox.
agent: flywheel-orchestrator
---

Abort the run at `$ARGUMENTS`.

Read `runs/<problem>/<ts>/flywheel-state.json`, `kill` each pid, `rm -rf runs/<p>/<ts>/sandbox`, then log an `abort` event via `.venv/bin/python shared/observe.py append --run-dir <run-dir> --phase aborted --agent orchestrator --event abort --decision "run aborted" --rationale "<why>"` (dual-writes `events.jsonl` + `decisions.md`; never hand-append).
