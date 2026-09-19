"""User search hints nudge order, never gates.

Pins the optional free-text `hints:` section: present in both templates,
asked/written/logged by the interview, consumed by executor + planner,
invisible to the reviewer, documented in the contract. Stdlib only.
"""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "problems" / "_template" / "problem.yaml"
SCAFFOLD_TEMPLATE = REPO / "problems" / "_template" / "problem.scaffold.yaml"
ARCHITECT = REPO / ".opencode" / "agent" / "problem-architect.md"
EXECUTOR = REPO / ".opencode" / "agent" / "sandbox-executor.md"
PLANNER = REPO / ".opencode" / "agent" / "planner.md"
REVIEWER = REPO / ".opencode" / "agent" / "sandbox-reviewer.md"
CONTRACT = REPO / "shared" / "gate-contract.md"


def test_templates_have_empty_hints_block():
    for path in (TEMPLATE, SCAFFOLD_TEMPLATE):
        text = path.read_text(encoding="utf-8")
        assert 'hints: ""' in text, f"{path} missing empty hints default"
        assert "never" in text and "gates" in text, f"{path} missing hints semantics"


def test_interview_asks_writes_and_logs_hints():
    text = ARCHITECT.read_text(encoding="utf-8")
    assert "search hints" in text, "architect never asks for hints"
    assert "`hints:` verbatim" in text, "architect must write hints verbatim"
    assert "search hints given" in text, "architect must log hints"


def test_executor_and_planner_consume_hints():
    executor = EXECUTOR.read_text(encoding="utf-8")
    assert "problem.yaml: hints" in executor
    assert "before open search" in executor
    planner = PLANNER.read_text(encoding="utf-8")
    assert "problem.yaml: hints" in planner
    assert "never override" in planner


def test_reviewer_scores_hints_blind_but_diagnoses_freely():
    text = REVIEWER.read_text(encoding="utf-8")
    assert "hints-blind" in text, "reviewer must score gates hints-blind"
    assert "may cite" in text, "reviewer diagnosis may cite hints/learnings"


def test_contract_documents_hint_semantics():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "hints-blind" in text
    assert "biases search" in text
