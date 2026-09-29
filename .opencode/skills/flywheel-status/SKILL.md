---
name: flywheel-status
description: Use when asked about flywheel runs — teaches the ask agent to interrogate run provenance (events.jsonl, decisions.md, flywheel-state.json) via shared/observe.py. Only installed with the full harness, never with lite.
---

# Flywheel-status skill

Load this when asked about runs in a repo with a `.flywheel/` directory.
If no `.flywheel/runs/` entries exist, say so and fall back to git history.

## Run layout

`problems/<name>/problem.yaml` is the only problem-specific file (spec:
datasets, blackbox, surrogate variants, gates, deliverables, constraints).
`runs/<problem>/<ts>/` is gitignored scratch per run (`events.jsonl`,
`decisions.md`, `flywheel-state.json`, `logs/`, `sandbox/`).
`artifacts/` holds committed keepers (hashes in `manifest.json`).
`shared/observe.py` is the provenance logger (stdlib only);
`shared/event-schema.md`, `shared/gate-contract.md`, `shared/decision-log.md`
are its contracts.

In scaffolded repos `problems/<name>` → `.flywheel`, `runs/<problem>/<ts>`
→ `.flywheel/runs/<ts>`, and `shared/` → `.flywheel/shared/`.

## Provenance recipes

Every run dual-writes `events.jsonl` (machine-readable) + `decisions.md`
(human render) via `observe.py`; live state in `flywheel-state.json`.
Interrogate with:
`.venv/bin/python shared/observe.py query <run-dir> [--phase ..] [--event ..]
[--gate ..] [--failed-only]` (filters AND; use `.flywheel/shared/observe.py`
in scaffolded repos), or raw `jq` over `events.jsonl`
(e.g. `jq -c 'select(.gates.fidelity.pass==false)' <run-dir>/events.jsonl`).
`decisions.md` blocks look like `## <ts> — <phase> — <agent>` with
Decision / Rationale / Gate-delta.

## Attribution rules

Actions taken by the flywheel are traceable in `events.jsonl` +
`decisions.md` (phase/agent/event per entry) and in delivery branches named
`flywheel/<problem>-<ts>`. Everything else is ordinary git history:
`git log --oneline -15`, `git show <sha> --stat`,
`git diff main...flywheel/<branch>`. When asked "what did opencode change",
check both: provenance logs for flywheel-attributed work, git for the rest.
If the two disagree, say so explicitly and trust the evidence.
