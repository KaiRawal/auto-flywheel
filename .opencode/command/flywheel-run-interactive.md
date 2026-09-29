---
description: Run the interactive flywheel variant — asks via question tool on ambiguous gate fail, researcher tie, commit-split, resource conflict.
agent: orchestrate-interactive
---

Run the interactive flywheel variant on `$ARGUMENTS` (loads the `orchestrate-interactive` skill on top of `orchestrate-autonomous`).

Use when you want human nudges at: gate-fail ambiguity, researcher tie, planner commit-split, unclear `problem.yaml` field, or resource conflict. Audit still lands in `runs/<p>/<ts>/decisions.md` interleaved with `Q:` blocks.
