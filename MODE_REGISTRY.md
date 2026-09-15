# Mode registry — flywheel skill

| Mode | Trigger | Agent (all `primary`) | Question tool |
|------|---------|------------------------|---------------|
| `autonomous` | `/flywheel-run problems/<name>` | `flywheel-orchestrator` | never |
| `interactive` | `/flywheel-run problems/<name> --interactive` or `/flywheel-run-interactive` | `flywheel-orchestrator-interactive` | on ambiguous gate fail, researcher tie, planner commit-split |
| `new` | `/flywheel-new` | `problem-architect` | always (or defaults+log in autonomous) |
| `ask` | `/ask [question]` or Tab-cycle to `ask` | `ask` | always welcome, never required — read-only, outside the loop |

Lifecycle: `new` (setup interview, once) → `autonomous`/`interactive` (long run, hours) → repeat. `ask` observes any phase without mutating: repo map, git history, run provenance (`events.jsonl`/`decisions.md`), artifacts.
