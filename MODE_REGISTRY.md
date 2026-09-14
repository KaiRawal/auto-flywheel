# Mode registry — flywheel skill

| Mode | Trigger | Agent (all `primary`) | Question tool |
|------|---------|------------------------|---------------|
| `autonomous` | `/flywheel-run problems/<name>` | `flywheel-orchestrator` | never |
| `interactive` | `/flywheel-run problems/<name> --interactive` or `/flywheel-run-interactive` | `flywheel-orchestrator-interactive` | on ambiguous gate fail, researcher tie, planner commit-split |
| `new` | `/flywheel-new` | `problem-architect` | always (or defaults+log in autonomous) |

Lifecycle: `new` (setup interview, once) → `autonomous`/`interactive` (long run, hours) → repeat.
