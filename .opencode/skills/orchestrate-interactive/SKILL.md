---
name: orchestrate-interactive
description: Use for interactive flywheel runs — same loop as orchestrate-autonomous but asks via question tool at decision points. Triggered by /flywheel-run-interactive or --interactive.
---

# Orchestrate-interactive skill

Load `orchestrate-autonomous` first — same state, loop, dispatch order, provenance, guards. Delta below is the only difference.

## When to call `question`

- Ambiguous gate failure (reviewer `fail` but margin is close)
- Researcher tie (two equally good candidate metrics/backbones)
- Planner commit-split choice
- Unclear `problem.yaml` field
- Resource conflict (host drifted below `problem.yaml: constraints` — halt and propose abort/downscale instead of reinterpreting silently)

Log every `Q:`/`A:` alongside `Decision:`/`Rationale:` blocks via `shared/observe.py append` (dual-writes `events.jsonl` + `decisions.md`; never hand-append).

If the user does not answer, proceed with the planner's default and log it.
