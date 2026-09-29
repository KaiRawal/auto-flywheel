---
name: flywheel
description: Flywheel index — points to the architect/orchestrate skills and the plan/build/ask/orchestrate agents. Triggered by /flywheel-new or /flywheel-run.
---

# Flywheel skill (index)

A problem-agnostic harness for iteratively building ML systems, predictors, or software features.

## Modes

| Mode | Agent (all `primary`) | Skill | Question tool |
|------|------------------------|-------|---------------|
| `autonomous` | `orchestrate` | `orchestrate-autonomous` | never — log to `decisions.md` |
| `interactive` | `orchestrate-interactive` | `orchestrate-interactive` (+ `orchestrate-autonomous`) | on ambiguous gate fail, researcher tie, commit-split |
| `new` | `build` | `problem-architect` | always — Socratic YAML builder (or defaults+log in autonomous) |
| `ask` | `ask` | — (read-only observer, `/ask`; loads `flywheel-status` for runs) | always welcome, never required |
| `plan` | `plan` | — (planning, no execution) | as needed for scoping |

Lifecycle: `new` (setup interview, once) → `autonomous`/`interactive` (long run) → repeat. `ask` sits outside the loop. `plan` scopes work before `build`/`orchestrate` execute.

Subagents (dispatched by `orchestrate` via `task`, unchanged): `sandbox-executor`, `sandbox-reviewer`, `researcher`, `planner`, `flywheel-executor`. See each agent file plus `shared/gate-contract.md` for gate syntax and `shared/event-schema.md` for provenance.

## Problem file

`problems/<name>/problem.yaml` — the only problem-specific file. See `shared/gate-contract.md` for gate syntax.
