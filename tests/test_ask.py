"""Ask mode stays read-only and wired up.

Parses the ask agent/command frontmatter with stdlib only (no yaml
dependency) and asserts the read-only posture plus registration.
"""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AGENT = REPO / ".opencode" / "agent" / "ask.md"
COMMAND = REPO / ".opencode" / "command" / "ask.md"


def frontmatter(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0].strip() == "---", f"{path} missing frontmatter"
    end = lines.index("---", 1)
    return [line.strip() for line in lines[1:end]]


def test_ask_agent_exists_and_is_primary():
    assert AGENT.exists()
    fm = frontmatter(AGENT)
    assert "mode: primary" in fm


def test_ask_agent_is_read_only():
    fm = frontmatter(AGENT)
    assert "edit: deny" in fm
    assert "todowrite: deny" in fm
    # bash default-deny with a read-only allowlist; last match wins in
    # opencode, so the wildcard deny must come first.
    bash_start = fm.index("bash:")
    star = next(i for i in range(bash_start, len(fm)) if '"*": deny' in fm[i])
    allows = [line for line in fm[bash_start:] if ": allow" in line]
    assert star < fm.index(allows[0])
    joined = "\n".join(fm)
    for cmd in ("git log*", "git show*", "git diff*", "observe.py query*"):
        assert cmd in joined, f"ask bash allowlist missing {cmd}"
    assert "question: allow" in fm
    assert "webfetch: allow" in fm
    assert "websearch: allow" in fm


def test_ask_agent_knows_provenance():
    body = AGENT.read_text(encoding="utf-8")
    for ref in ("event-schema.md", "gate-contract.md", "events.jsonl",
                "decisions.md", "flywheel-state.json", "observe.py query"):
        assert ref in body, f"ask prompt missing {ref}"


def test_ask_command_routes_to_ask_agent():
    assert COMMAND.exists()
    fm = frontmatter(COMMAND)
    assert "agent: ask" in fm
    body = COMMAND.read_text(encoding="utf-8")
    assert "read-only" in body.lower()


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
