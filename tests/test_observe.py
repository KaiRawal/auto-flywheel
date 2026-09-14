import json
import subprocess
import sys
from pathlib import Path

import pytest

from shared.observe import append_event, init_run, query_events

OBSERVE = Path("shared/observe.py")


def test_init_creates_events_decisions_state(tmp_path):
    run = tmp_path / "runs" / "toy" / "ts1"
    e = init_run(run, "toy")
    assert e["phase"] == "sandbox-loop" and e["event"] == "init"
    assert (run / "events.jsonl").exists()
    assert (run / "decisions.md").exists()
    state = json.loads((run / "flywheel-state.json").read_text())
    assert state["phase"] == "sandbox-loop"


def test_append_dual_writes_decisions_block(tmp_path):
    run = tmp_path / "runs" / "p" / "t"
    init_run(run, "p")
    append_event(
        run,
        phase="sandbox-loop",
        agent="sandbox-reviewer",
        event="gate_score",
        iteration=1,
        decision="scored linear",
        rationale="first variant",
        gate_delta="f1 0.82 vs 0.85 (-0.03)",
        gates={"fidelity": {"pass": False, "margin": -0.03}},
    )
    lines = (run / "events.jsonl").read_text().strip().splitlines()
    assert len(lines) == 2
    last = json.loads(lines[-1])
    assert last["gates"]["fidelity"]["pass"] is False
    md = (run / "decisions.md").read_text()
    assert "## " in md and "- Decision: scored linear" in md
    assert "- Gate delta: f1 0.82 vs 0.85 (-0.03)" in md


def test_query_filters(tmp_path):
    run = tmp_path / "runs" / "p" / "t"
    init_run(run, "p")
    append_event(
        run, phase="sandbox-loop", agent="a", event="gate_score",
        iteration=1, gates={"fidelity": {"pass": False, "margin": -0.03}},
    )
    append_event(
        run, phase="research", agent="researcher", event="decision",
        decision="try rbf", gates={"fidelity": {"pass": True, "margin": 0.02}},
    )
    assert len(query_events(run, failed_only=True)) == 1
    assert len(query_events(run, phase="research")) == 1
    assert len(query_events(run, gate="fidelity")) == 2
    assert len(query_events(run, gate="nope")) == 0


def test_abort_event_and_nudge_state(tmp_path):
    run = tmp_path / "runs" / "p" / "t"
    init_run(run, "p")
    append_event(
        run, phase="sandbox-loop", agent="orchestrator", event="nudge",
        iteration=1, decision="try rbf",
    )
    append_event(
        run, phase="aborted", agent="orchestrator", event="abort",
        decision="run aborted", rationale="user asked",
    )
    state = json.loads((run / "flywheel-state.json").read_text())
    assert state["phase"] == "aborted"
    assert "try rbf" in state["nudges"]


def test_validation_rejects_bad_phase_gate(tmp_path):
    run = tmp_path / "runs" / "p" / "t"
    with pytest.raises(ValueError):
        append_event(run, phase="nope", agent="a", event="decision")
    with pytest.raises((ValueError, TypeError)):
        append_event(
            run, phase="plan", agent="a", event="decision",
            gates={"fidelity": {"pass": "yes"}},
        )


def test_cli_append_query_roundtrip(tmp_path):
    run = tmp_path / "runs" / "p" / "t"
    py = sys.executable
    r = subprocess.run(
        [py, str(OBSERVE), "init", "--run-dir", str(run), "--problem", "p"],
        capture_output=True, text=True, check=False,
    )
    assert r.returncode == 0, r.stderr
    r = subprocess.run(
        [py, str(OBSERVE), "append", "--run-dir", str(run),
         "--phase", "plan", "--agent", "orchestrator", "--event", "decision",
         "--decision", "picked rbf", "--gates", '{"fidelity":{"pass":true,"margin":0.05}}'],
        capture_output=True, text=True, check=False,
    )
    assert r.returncode == 0, r.stderr
    r = subprocess.run(
        [py, str(OBSERVE), "query", str(run), "--failed-only"],
        capture_output=True, text=True, check=False,
    )
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == ""  # no failures logged
    r = subprocess.run(
        [py, str(OBSERVE), "query", str(run), "--phase", "plan"],
        capture_output=True, text=True, check=False,
    )
    assert r.returncode == 0
    assert "picked rbf" in r.stdout
