# AGENTS.md — auto-flywheel

Instructions for AI coding agents in this lab.

## Environment rules

- **`.venv` only** — never `pip install` outside the problem's `.venv` at its root. No `brew`/`apt`/`npm`.
- Run from the problem root (or lab root with `workdir`): `.venv/bin/python -m pytest`, `.venv/bin/python -m ruff check .`, `.venv/bin/jupyter nbconvert ...`.
- **Guards before every heavy step**:
  - `df -h / | tail -1` — abort if < `constraints.disk_gb` free
  - `vm_stat | head` / `ps aux -m | head` — stay < `constraints.mem_gb` (20GB default hard ceiling)
  - Wrap with GNU `timeout` where appropriate: `timeout 600 .venv/bin/python train.py`
- **Heavy jobs in background** — `nohup .venv/bin/python train.py > runs/<p>/<ts>/logs/X.log 2>&1 &` then poll with `while pgrep -f "train.py" >/dev/null; do sleep 10; done` so lint/docs/tests can run in parallel. Never `sleep 590` polling.
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
- [ ] Disk/memory guards never tripped; `.venv` is the only install target
