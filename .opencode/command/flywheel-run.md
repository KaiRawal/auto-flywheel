---
description: Run the autonomous data flywheel on a problem — relentless until gates pass.
agent: flywheel-orchestrator
---

Run the autonomous flywheel on the problem at `$ARGUMENTS`.

`$ARGUMENTS` is a path to `problems/<name>` or its `problem.yaml`. If empty, list `problems/*/problem.yaml` and ask which (via `question` in interactive, or pick `toy-tabular` in autonomous).

The orchestrator owns `runs/<problem>/<ts>/flywheel-state.json` and `decisions.md`, dispatches sandbox-executor/reviewer loops (gate-driven), then researcher/planner/flywheel-executor as needed. Heavy jobs run via `nohup` + `while pgrep ... sleep 10` so verification can proceed in parallel. All installs in `constraints.venv`, global caches, `df/vm_stat` guards, `timeout` where configured.
