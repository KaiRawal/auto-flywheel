# Mode registry — flywheel skill

| Mode | Trigger | Agent (all `primary`) + skill | Question tool |
|------|---------|-------------------------------|---------------|
| `autonomous` | `/flywheel-run problems/<name>` | `orchestrate` + `orchestrate-autonomous` | never |
| `interactive` | `/flywheel-run problems/<name> --interactive` or `/flywheel-run-interactive` | `orchestrate-interactive` + `orchestrate-interactive` | on ambiguous gate fail, researcher tie, planner commit-split |
| `new` | `/flywheel-new` | `build` + `problem-architect` | always (or defaults+log in autonomous) |
| `plan` | Tab-cycle to `plan` | `plan` | as needed for scoping |
| `build` | Tab-cycle to `build` | `build` | as needed for execution |
| `ask` | `/ask [question]` or Tab-cycle to `ask` | `ask` (+ optional `flywheel-status` skill for runs) | always welcome, never required — read-only, outside the loop |

Lifecycle: `new` (setup interview, once) → `autonomous`/`interactive` (long run, hours) → repeat. `ask` answers from repo map + git history, and (with the `flywheel-status` skill, full install only) run provenance. `plan` scopes before `build`/`orchestrate` execute.
