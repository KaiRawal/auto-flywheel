"""Ask mode stays read-only, generic, and wired up.

Parses the ask agent/command frontmatter with stdlib only (no yaml
dependency) and asserts the read-only posture plus registration.

Ask is flywheel-free by design (so the lite install ships it verbatim):
the only flywheel-adjacent token allowed in the agent body is the single
`flywheel-status` skill hook line. Run-provenance knowledge lives in
.skills/flywheel-status/SKILL.md (full install only).
"""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AGENT = REPO / ".opencode" / "agent" / "ask.md"
COMMAND = REPO / ".opencode" / "command" / "ask.md"

# Flywheel tokens that must not appear in ask (agent or command), except via
# the single `flywheel-status` hook line in the agent body.
BANNED_TOKENS = (
    "events.jsonl",
    "decisions.md",
    "flywheel-state.json",
    "observe.py",
    "problem.yaml",
    "flywheel-run",
    "orchestrate",
    "sandbox",
    "researcher",
    "planner",
    "problem-architect",
    "gate-contract",
    "event-schema",
    "decision-log",
    "metrics.json",
    "learnings.md",
    ".flywheel",
    "problems/",
    "runs/",
    "artifacts/",
    "blackbox",
    "flywheel/",
)


def frontmatter(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0].strip() == "---", f"{path} missing frontmatter"
    end = lines.index("---", 1)
    return [line.strip() for line in lines[1:end]]


def agent_body_without_hook() -> str:
    lines = AGENT.read_text(encoding="utf-8").splitlines()
    kept = [line for line in lines if "flywheel-status" not in line]
    return "\n".join(kept)


def test_ask_agent_exists_and_is_primary():
    assert AGENT.exists()
    fm = frontmatter(AGENT)
    assert "mode: primary" in fm


def test_ask_agent_is_read_only():
    fm = frontmatter(AGENT)
    assert "edit: deny" in fm
    assert "todowrite: deny" in fm
    # bash default-deny with a generic git-only allowlist; last match wins in
    # opencode, so the wildcard deny must come first.
    bash_start = fm.index("bash:")
    star = next(i for i in range(bash_start, len(fm)) if '"*": deny' in fm[i])
    allows = [line for line in fm[bash_start:] if ": allow" in line]
    assert star < fm.index(allows[0])
    joined = "\n".join(fm)
    for cmd in ("git log*", "git show*", "git diff*", "git status*", "git branch*"):
        assert cmd in joined, f"ask bash allowlist missing {cmd}"
    assert "observe.py" not in joined, "ask must not allow observe.py queries"
    assert "question: allow" in fm
    assert "webfetch: allow" in fm
    assert "websearch: allow" in fm


def test_ask_agent_knows_git_and_hook():
    body = AGENT.read_text(encoding="utf-8")
    assert "flywheel-status" in body, "ask missing the optional status-skill hook"
    for ref in ("git log", "git show", "git diff"):
        assert ref in body, f"ask prompt missing {ref}"


def test_ask_agent_is_flywheel_free():
    body = agent_body_without_hook()
    lowered = body.lower()
    for token in BANNED_TOKENS:
        assert token.lower() not in lowered, f"ask body contains flywheel token {token}"
    assert "flywheel" not in lowered, "ask body references flywheel outside the hook line"


def test_ask_agent_knows_its_mode():
    body = AGENT.read_text(encoding="utf-8")
    assert "ASK mode" in body
    assert "overrides all other instructions" in body
    assert "Tab-switch" in body and "build" in body
    assert "one redirect, then stop" in body


def test_ask_command_routes_to_ask_agent():
    assert COMMAND.exists()
    fm = frontmatter(COMMAND)
    assert "agent: ask" in fm
    body = COMMAND.read_text(encoding="utf-8")
    assert "read-only" in body.lower()
    lowered = body.lower()
    for token in BANNED_TOKENS:
        assert token.lower() not in lowered, f"ask command contains flywheel token {token}"
    assert "flywheel" not in lowered, "ask command references flywheel"


def test_ask_agent_ends_with_sources_footer():
    body = AGENT.read_text(encoding="utf-8")
    assert "Sources:" in body
    assert "next-steps" in body  # only as a prohibition, never as an offering
    assert "suggested next steps as commands" not in body


def test_ask_registered_in_mode_tables():
    registry = (REPO / "MODE_REGISTRY.md").read_text(encoding="utf-8")
    assert "`ask`" in registry and "/ask" in registry
    skill = (REPO / ".opencode" / "skills" / "flywheel" / "SKILL.md").read_text(
        encoding="utf-8")
    assert "`ask`" in skill
