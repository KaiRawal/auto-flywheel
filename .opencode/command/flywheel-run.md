---
description: Run the autonomous data flywheel on a problem — relentless until gates pass.
agent: orchestrate
---

Run the autonomous flywheel on the problem at `$ARGUMENTS` (loads the `orchestrate-autonomous` skill).

`$ARGUMENTS` is a path to `problems/<name>` or its `problem.yaml`. If empty, list `problems/*/problem.yaml` and ask which (via `question` in interactive, or pick `toy-tabular` in autonomous).

The `orchestrate` agent owns `runs/<problem>/<ts>/learnings.md` and `decisions.md`; full loop lives in the `orchestrate-autonomous` skill. `problem.yaml` goals/gates are immutable — learnings nudge future steps only.
