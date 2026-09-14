# Mode registry — flywheel skill

| Mode | Trigger | Orchestrator | Question tool |
|------|---------|--------------|---------------|
| `autonomous` | `/flywheel-run problems/<name>` | `flywheel-orchestrator` | never |
| `interactive` | `/flywheel-run problems/<name> --interactive` or `/flywheel-run-interactive` | `flywheel-orchestrator-interactive` | on ambiguous gate fail, researcher tie, planner commit-split |
| `new` | `/flywheel-new` | `problem-architect` | always (or defaults+log in autonomous) |
