# AGENTS.md — auto-flywheel

Instructions for AI coding agents in this lab.

## Environment rules

- **`.venv` only** — never `pip install` outside the problem's `.venv` at its root. No `brew`/`apt`/`npm`.
- Run from the problem root (or lab root with `workdir`): `.venv/bin/python -m pytest`, `.venv/bin/python -m ruff check .`, `.venv/bin/jupyter nbconvert ...`.
- **Resources: measured once, not hardcoded**:
  - `/flywheel-new` (`problem-architect`) measures the host once (`df -h /`, `vm_stat`/`free`, `nproc`) and writes `constraints.disk_gb`/`mem_gb`/`heavy_bg` as measured free minus headroom (keep several GB disk + a few GB RAM free). Never invent limits.
  - The orchestrator confirms once at run start; on drift it aborts/downscales and logs. Executors just stay inside `problem.yaml` limits — no re-measuring.
  - Wrap with GNU `timeout` where appropriate: `timeout 600 .venv/bin/python train.py`
- **Heavy jobs in background** — one job → one log: `nohup .venv/bin/python train.py > runs/<p>/<ts>/logs/X.log 2>&1 &` then poll with `while pgrep -f "train.py" >/dev/null; do sleep 10; done` so lint/docs/tests can run in parallel. Never run two peak-RAM phases at once. Never `sleep 590` polling.
- **Global caches** — reuse `~/.cache/huggingface`, `~/.cache/torch` etc. Copy, don't re-download.
- Never modify code outside the problem directory. Never bump versions unless asked.
- After editing `opencode.json`/agent/skill/command files: tell the user to quit and restart opencode.

## Lab layout

- `problems/<name>/problem.yaml` — the only place problem knowledge lives (datasets, gates, deliverables)
- `runs/<problem>/<ts>/` — gitignored scratch: `flywheel-state.json`, `decisions.md`, `logs/`, `sandbox/`
- `artifacts/` or `problems/<name>/artifacts/` — committed keepers (hashes in `manifest.json`)

## Definition of done

- [ ] Gates in `problem.yaml` pass with margin (not knife-edge)
- [ ] `pytest` green, `ruff check .` clean inside `.venv`
- [ ] Deliverables in `problem.yaml: deliverables` exist and are committed where required
- [ ] `decisions.md` + `events.jsonl` audit trail exists (via `shared/observe.py`); no `question` calls in autonomous mode
- [ ] Resource limits (measured at setup, confirmed at run start) never exceeded; `.venv` is the only install target
