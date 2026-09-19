# Decision log pattern

Provenance is dual-written via `shared/observe.py` (schema: `shared/event-schema.md`):

- `runs/<problem>/<ts>/events.jsonl` — queryable audit trail (phase + gate deltas only). Filter with `shared/observe.py query <run-dir> [--phase ..] [--failed-only] [--gate ..]` or plain `jq`.
- `runs/<problem>/<ts>/decisions.md` — human render, one `## <timestamp> — <phase> — <agent>` block per event with Decision/Rationale/Gate delta.

- Autonomous mode: every iteration appends one event. No `question` calls.
- Interactive mode: same, plus interleaved `Q: ...` / `A: ...` blocks from the `question` tool.

The orchestrator is the only writer; subagents read and return `gates` maps for the orchestrator to log. Reviewers additionally return Learning/Do-not-retry lines; the orchestrator appends full text to run-scoped `learnings.md` and logs `nudge` summaries. `problem.yaml` goals/gates are immutable — learnings nudge future steps only.

## Flywheel state

`runs/<problem>/<ts>/flywheel-state.json`:

```json
{"phase":"sandbox-loop","iteration":2,"nudges":["try rbf"],"last_scores":{"f1":0.82},"pids":[12345]}
```

Polled via `while pgrep -f "train.py" >/dev/null; do sleep 10; done`.
