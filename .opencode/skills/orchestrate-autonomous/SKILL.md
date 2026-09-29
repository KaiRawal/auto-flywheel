---
name: orchestrate-autonomous
description: Use for autonomous flywheel runs — gate-driven sandbox loop, learnings, research/plan/relentless execution with mandatory provenance. Triggered by /flywheel-run.
---

# Orchestrate-autonomous skill

Run the autonomous data flywheel on `problems/<name>/problem.yaml` until gates pass. Never call `question` — log and proceed.

## State you own

`runs/<problem>/<ts>/flywheel-state.json` ( sole writer), `runs/<problem>/<ts>/learnings.md` (append-only), `events.jsonl` + `decisions.md` via `shared/observe.py` (see `shared/event-schema.md`). Never hand-append `decisions.md`. Granularity is phase + gate deltas only.

Provenance: `init` once per run (`.venv/bin/python shared/observe.py init --run-dir runs/<p>/<ts> --problem <p>`), then `append` one event per phase transition / reviewer score / nudge (`--phase sandbox-loop|research|plan|flywheel|done --event phase_transition|gate_score|decision|nudge --gates '{...}'`). Subagents return `gates` maps; you log.

## Setup

Read `problems/<name>/problem.yaml` (or `$ARGUMENTS` path). If missing, run the `problem-architect` skill in autonomous defaults mode.

Resource confirm once at run start: `df -h / | tail -1` + (`vm_stat | head` / `free -h`) + `nproc`, compare against `constraints.disk_gb`/`mem_gb` (measured at setup). On drift below promised, abort or downscale variants and log via `observe.py`. Do not re-measure mid-run.

## Loop (dispatch via `task`, subagents unchanged)

1. **Sandbox loop** — `sandbox-executor` + `sandbox-reviewer`, gate-driven, up to 3 iterations / nudges or until `pass`. Parallel light variants only; `heavy_bg` or peak-RAM variants serially, one job → one log. Inject accumulated learnings + do-not-retry + baseline note from `learnings.md` into each next `sandbox-executor` prompt.
2. **Learnings** — after every reviewer score, append its Learning/Do-not-retry lines to `learnings.md` and log a `nudge` summary (full text stays in `learnings.md`). Every 3 iterations or on plateau, consolidate Confirmed / Contradicted / Open + ranked hypotheses + baseline diagnosis for researcher/planner.
3. **Research → Plan → Flywheel** — on plateau dispatch `researcher` (reads all `logs/` + `learnings.md`; leads with why the good baseline still wins), then `planner` (writes `runs/<p>/<ts>/plan.md` with commit split), then `flywheel-executor` (relentless BG execution, picks winners by gate margin).
4. **Heavy jobs** — `nohup {constraints.venv}/bin/python train.py > runs/.../logs/X.log 2>&1 &`, poll `while pgrep -f train.py >/dev/null; do sleep 10; done`. Memory-light work (`ruff`, `pytest --collect-only`, docs) may run in parallel. Never two peak-RAM phases at once. Use `timeout` per `constraints`.

## Guards

- Goals immutable: never edit `problems/<name>/problem.yaml` `goal`/`gates`/thresholds — learnings nudge future steps only.
- Environment: `.venv`-only installs, global caches (`~/.cache/huggingface`, `~/.cache/torch`), `timeout` per `constraints`.
- `models:` in `problem.yaml` overrides `opencode.json` — forward `model=` through `task` calls.
- After gates pass, commit per `plan.md` split and verify `pytest/ruff/nbconvert` under `timeout`.
