# auto-flywheel

A problem-agnostic **autonomous delivery harness for [opencode](https://opencode.ai)** — a relentless loop that turns an underspecified `problem.yaml` into verified artifacts, tests and notebooks, with a queryable audit trail of everything it did and why.

> **Overkill by design.** The included `toy-tabular` problem (breast-cancer prediction) is intentionally trivial — it proves the autonomous loop works end-to-end in <1 minute with no downloads.

## What this is

```
[sandbox executor × N  + reviewer] (gate-driven loop, up to 3 nudges)
        │
        ├──> researcher (outside perspective: docs, papers, other repos)
        │
        ├──> planner (logs + research -> gated plan with commit split)
        │
        └──> flywheel-executor (relentless: nohup + pgrep, picks winners, builds)
```

- **Executors + reviewers** loop until your gates pass — the "flywheel" that builds ML models (or software features) and improves them.
- **Researcher** brings a new perspective when the loop plateaus.
- **Planner** combines research + logs into a gated workflow with acceptance thresholds.
- **Flywheel-executor** runs that workflow to completion — firing long jobs in the background, multitasking lint/docs/tests while models train.
- **Provenance built in**: every phase transition and gate score is logged to `events.jsonl` (machine-readable) + `decisions.md` (human-readable) via `shared/observe.py`, so you can interrogate any run.

Three phases, one codebase: **setup** (`/flywheel-new` interview, once) → **autonomous** run (never asks, just logs) or **interactive** run (asks you at ambiguous failures) → repeat.

## Prerequisites

- Python 3.10+ with `venv`
- [opencode](https://opencode.ai/docs) installed and authenticated to at least one model provider
- ~2 GB free disk for the demo (more for real problems — each `problem.yaml` declares its budget)

## Install

```bash
git clone https://github.com/KaiRawal/auto-flywheel.git
cd auto-flywheel
python -m venv .venv
.venv/bin/pip install pytest scikit-learn joblib ruff jupyter
```

Then launch opencode from the repo root:

```bash
opencode
```

> **First launch:** after opencode starts, **quit and restart it once** so the bundled agents (`flywheel-orchestrator`, `flywheel-orchestrator-interactive`, `problem-architect`, …) and commands (`/flywheel-new`, `/flywheel-run`, …) register. (Opencode only picks up new agent/command files on startup.)

> **Permissions:** `opencode.json` pre-allows the checkout at `~/Oxford/Projects/auto-flywheel/**`. If you cloned elsewhere, update that path to your checkout (or leave the default `ask` behavior).

## 60-second proof (do this first)

Inside opencode:

```
/flywheel-run problems/toy-tabular
```

This runs the autonomous loop on the trivial demo: no questions asked, finishes in under a minute. Then inspect what happened:

```bash
ls runs/toy-tabular/*/          # events.jsonl, decisions.md, flywheel-state.json, logs/
cat runs/toy-tabular/*/decisions.md
.venv/bin/python shared/observe.py query runs/toy-tabular/* --failed-only
```

Interactive variant (asks you at ambiguous gate failures, researcher ties, commit splits):

```
/flywheel-run problems/toy-tabular --interactive
```

## Your first problem

```bash
# inside opencode:
/flywheel-new
```

The `problem-architect` interviews you (type, data, metric, gate threshold, deliverables, budgets) and writes `problems/<name>/problem.yaml`. Prefer files? Copy the template manually instead:

```bash
cp -r problems/_template problems/my-new-thing
# edit problems/my-new-thing/problem.yaml
```

### Writing gates

Gates are declarative expressions — no metric is hard-coded in the harness:

```yaml
gates:
  fidelity: "f1 >= 0.85"
  robustness: "accuracy_drop <= 0.05"
  budgets: { samples: 200 }
```

`toy-tabular` uses `f1`/`accuracy`; a feature problem might use `pass_rate == 1.0` and `latency_p95 <= 50` (see `problems/feature-flags`). The reviewer evaluates whatever you name (syntax: `shared/gate-contract.md`).

### Problem types

| Type | Goal | Deliverable example |
|------|------|---------------------|
| `ml-system` | train a model | `artifacts/model.joblib` |
| `prediction` | ship predictions | a prediction CSV |
| `feature` | add software | code + `tests_pass == true and latency_p95 <= 120` |

Same agents handle all three — only `problem.yaml` changes.

### Run it

```
/flywheel-run problems/my-new-thing
```

## Bring flywheel to your own repo

Single-problem repos use the flywheel where they are — no submodules, no pointing opencode elsewhere. Clone this repo anywhere (its location doesn't matter afterwards), then scaffold **copies** of the harness into your repo:

```bash
git clone https://github.com/KaiRawal/auto-flywheel.git   # anywhere; forgettable
./auto-flywheel/scripts/flywheel-init /path/to/myrepo my-feature
cd /path/to/myrepo && opencode   # restart once so agents/commands register
```

What you get in your repo (all paths below are relative to it):

```
.opencode/agent/flywheel-*.md, planner, researcher, sandbox-*, problem-architect
.opencode/command/flywheel-*.md   # /flywheel-run, /flywheel-new, /flywheel-status, ...
.opencode/skills/flywheel/        # skill definition
.flywheel/problem.yaml            # your spec (starter template, TODOs inside)
.flywheel/shared/                 # observe.py logger + gate/observability contracts
```

`flywheel-init` is copy-only and idempotent: re-running it refreshes the harness files, merges `.gitignore` (`.flywheel/runs/`, `.venv/`) and an `AGENTS.md` section without touching anything else, and refuses to overwrite files whose content differs. Updating is just `git pull` here + re-run there. Then, inside opencode in your repo:

```
/flywheel-new    # fills .flywheel/problem.yaml: scope, test command, gates
/flywheel-run .flywheel
```

Runs land in `.flywheel/runs/<ts>/` (gitignored); the winner is delivered on a `flywheel/<problem>-<ts>` branch in your repo for review. Everything under "Writing gates", "Problem types" and "Observability" below applies with `problems/<name>` → `.flywheel` and `shared/` → `.flywheel/shared/`.

## Observability: what was done and why

Every run dual-writes its audit trail to `runs/<problem>/<ts>/`:

- `events.jsonl` — one JSON object per line: `{ts, phase, agent, event, decision, rationale, gates: {<gate>: {pass, margin}}}`. Query it:
  ```bash
  .venv/bin/python shared/observe.py query runs/<problem>/<ts> --failed-only
  .venv/bin/python shared/observe.py query runs/<problem>/<ts> --phase research
  .venv/bin/python shared/observe.py query runs/<problem>/<ts> --event decision --gate fidelity
  jq -c 'select(.gates.fidelity.pass==false)' runs/<problem>/<ts>/events.jsonl
  ```
- `decisions.md` — human render of the same events (`## <ts> — <phase> — <agent>` + Decision/Rationale/Gate-delta).
- `flywheel-state.json` — live phase/iteration/pids/last-scores; read it with `/flywheel-status`, abort with `/flywheel-abort`.

Schema: `shared/event-schema.md`. Status commands: `/flywheel-status`, `/flywheel-abort`. For a live view while a run is going: `tail -f runs/<p>/<ts>/events.jsonl`.

## Repo map

```
problems/<name>/problem.yaml   # spec — the only problem-specific file (committed)
runs/<problem>/<ts>/           # scratch (gitignored): events.jsonl, decisions.md,
                               #   flywheel-state.json, logs/, sandbox/
artifacts/                     # committed keepers (hashes in manifest.json)
shared/observe.py              # provenance logger (stdlib only)
shared/event-schema.md         # event schema + query recipes
.opencode/agent/               # orchestrators (primary), problem-architect (primary setup), executors, reviewer, researcher, planner
.opencode/command/             # /flywheel-run, /flywheel-new, /flywheel-status, ...
.opencode/skills/flywheel/     # skill definition for the loop
```

## Swapping models (model-agnostic)

```yaml
# in problem.yaml or opencode.json
models:
  orchestrator: "anthropic/claude-sonnet-4-6"
  executor: "openai/gpt-5"
```

Or per-run: `/flywheel-run problems/toy-tabular --model openai/gpt-5`. The orchestrator forwards `model=` through its subagent calls; no files rewritten.

## Safety guards

- `.venv`-only installs — never system `pip`, `brew`, `apt`, or `npm`
- Resources measured once at setup (`/flywheel-new` proposes `constraints` from `df`/`vm_stat`/`free` minus headroom), confirmed once at run start (abort/downscale + log on drift); executors stay inside `problem.yaml: constraints` without re-measuring
- `timeout 600 ...` around heavy commands; long jobs run via `nohup … &` (one job → one log) and are polled with `pgrep` so verification proceeds in parallel; never two peak-RAM phases at once
- Global caches (`~/.cache/huggingface`, `~/.cache/torch`) are reused, never re-downloaded

Contributor rules for agents live in `AGENTS.md`.

## When to use vs overkill

`toy-tabular` fits a `LogisticRegression` in ~2s — deliberately trivial, just proving the loop. Real value is on underspecified problems where you need several sandbox iterations plus a researcher nudge before anyone knows what "good" means.
