"""Periodic learnings loop: capture, synthesize, reuse — goals immutable.

Pins the harness contract with stdlib only:
- reviewer returns structured learnings per iteration (scoring unchanged)
- researcher leads with baseline diagnosis from all logs + learnings.md
- planner carries Learnings / Baseline / Do-not-retry into plan.md verbatim
- orchestrators own run-scoped learnings.md and inject it into next steps
- problem.yaml goal/gates stay immutable everywhere
"""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AGENT = REPO / ".opencode" / "agent"
REVIEWER = AGENT / "sandbox-reviewer.md"
RESEARCHER = AGENT / "researcher.md"
PLANNER = AGENT / "planner.md"
ORCH = AGENT / "flywheel-orchestrator.md"
ORCH_INT = AGENT / "flywheel-orchestrator-interactive.md"
SANDBOX = AGENT / "sandbox-executor.md"
FLYWHEEL = AGENT / "flywheel-executor.md"
SKILL = REPO / ".opencode" / "skills" / "flywheel" / "SKILL.md"
CONTRACT = REPO / "shared" / "gate-contract.md"
SCHEMA = REPO / "shared" / "event-schema.md"
COMMAND = REPO / ".opencode" / "command" / "flywheel-run.md"

GOAL_FILES = (REVIEWER, RESEARCHER, PLANNER, ORCH, ORCH_INT, SANDBOX, FLYWHEEL)


def test_goals_immutable_everywhere():
    for path in GOAL_FILES:
        text = path.read_text(encoding="utf-8")
        assert "immutable" in text.lower(), f"{path.name} missing immutability rule"
        assert "problem.yaml" in text, f"{path.name} must name problem.yaml scope"


def test_reviewer_returns_structured_learnings():
    text = REVIEWER.read_text(encoding="utf-8")
    for token in ("Learning", "Do-not-retry", "Next hypothesis",
                  "baseline_delta", "best-so-far", "Failure modes",
                  "learnings.md", "gate_score"):
        assert token in text, f"reviewer missing {token}"
    assert "hints-blind" in text


def test_researcher_diagnoses_baseline_from_all_logs():
    text = RESEARCHER.read_text(encoding="utf-8")
    for token in ("learnings.md", "baseline diagnosis", "kill-criterion",
                  "do-not-try", "max 3"):
        assert token in text, f"researcher missing {token}"
    assert "Naively throwing bigger models" in text or "last resort" in text


def test_planner_carries_learnings_verbatim_thresholds():
    text = PLANNER.read_text(encoding="utf-8")
    for token in ("Learnings", "Baseline diagnosis", "Do-not-retry",
                  "verbatim copy", "Rejected with a reason", "learnings.md"):
        assert token in text, f"planner missing {token}"
    assert "researcher-suggested adjustments" not in text


def test_orchestrators_own_learnings_loop():
    for path in (ORCH, ORCH_INT):
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for token in ("learnings.md", "every 3 iterations or on plateau",
                      "nudge", "future steps only"):
            assert token in lowered, f"{path.name} missing {token}"
    assert "next `sandbox-executor` prompt" in ORCH.read_text(encoding="utf-8")


def test_executors_honor_learnings():
    sandbox = SANDBOX.read_text(encoding="utf-8")
    assert "do-not-retry" in sandbox
    assert "which prior learning this variant tests" in sandbox
    flywheel = FLYWHEEL.read_text(encoding="utf-8")
    assert "Do-not-retry" in flywheel
    assert "which carried-forward learning paid off" in flywheel


def test_skill_contract_and_command():
    skill = SKILL.read_text(encoding="utf-8")
    assert "learnings.md" in skill
    assert "immutable" in skill
    assert "why the good baseline still wins" in skill
    command = COMMAND.read_text(encoding="utf-8")
    assert "learnings.md" in command
    assert "immutable" in command


def test_shared_docs_document_loop_without_schema_change():
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "learnings.md" in contract
    assert "immutable" in contract
    schema = SCHEMA.read_text(encoding="utf-8")
    assert "learnings.md" in schema
    assert "no schema change" in schema.lower() or "No schema change" in schema
