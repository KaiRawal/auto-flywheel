---
description: Run the interactive flywheel variant — asks via question tool on ambiguous gate fail, researcher tie, commit-split.
agent: flywheel-orchestrator-interactive
---

Run the interactive flywheel variant on `$ARGUMENTS` (same as `/flywheel-run` but with `question` enabled).

Use when you want human nudges at: gate-fail ambiguity, researcher tie, planner commit-split, or unclear `problem.yaml` field. Audit still lands in `runs/<p>/<ts>/decisions.md` interleaved with `Q:` blocks.
