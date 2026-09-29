"""flywheel-lite: ask agent + ask command only, nothing else.

Verbatim copies (no rewrites), idempotent, collision-abort, dry-run,
dirty-tree gate, and CLI entrypoints. Stdlib only.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from shared.scaffold import (
    LITE_AGENT_FILES,
    LITE_COMMAND_FILES,
    SKILL_FILES,
    lite_scaffold,
    lite_update,
)

REPO = Path(__file__).resolve().parent.parent
LITE_INIT = REPO / "scripts" / "flywheel-lite-init"
LITE_UPDATE = REPO / "scripts" / "flywheel-lite-update"
STATUS_SKILL = REPO / ".opencode" / "skills" / "flywheel-status" / "SKILL.md"


def test_lite_file_lists_are_ask_only():
    assert LITE_AGENT_FILES == ["ask.md"]
    assert LITE_COMMAND_FILES == ["ask.md"]


def test_flywheel_status_skill_ships_with_full_only():
    assert "flywheel-status/SKILL.md" in SKILL_FILES
    assert STATUS_SKILL.exists()
    body = STATUS_SKILL.read_text(encoding="utf-8")
    for token in ("events.jsonl", "decisions.md", "flywheel-state.json",
                  "observe.py query"):
        assert token in body, f"status skill missing {token}"


def test_lite_scaffold_installs_only_ask(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    counts = lite_scaffold(target)
    assert counts["wrote"] == 2
    agent = target / ".opencode" / "agent" / "ask.md"
    command = target / ".opencode" / "command" / "ask.md"
    assert agent.exists() and command.exists()
    assert agent.read_bytes() == (REPO / ".opencode" / "agent" / "ask.md").read_bytes()
    assert command.read_bytes() == (REPO / ".opencode" / "command" / "ask.md").read_bytes()
    assert not (target / ".flywheel").exists()
    assert not (target / ".opencode" / "skills").exists()
    assert sorted(p.name for p in (target / ".opencode" / "agent").iterdir()) == ["ask.md"]
    assert sorted(p.name for p in (target / ".opencode" / "command").iterdir()) == ["ask.md"]
    assert not (target / "AGENTS.md").exists()
    assert not (target / ".gitignore").exists()


def test_lite_scaffold_idempotent(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    first = lite_scaffold(target)
    assert first["wrote"] == 2
    second = lite_scaffold(target)
    assert second == {"wrote": 0, "same": 2}


def test_lite_collision_aborts(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    clash = target / ".opencode" / "agent"
    clash.mkdir(parents=True)
    (clash / "ask.md").write_text("user's own ask, do not touch")
    with pytest.raises(SystemExit, match="Refusing to overwrite"):
        lite_scaffold(target)
    assert (clash / "ask.md").read_text() == "user's own ask, do not touch"


def test_lite_update_dry_run_changes_nothing(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    counts = lite_update(target, dry_run=True)
    assert counts == {"wrote": 2, "same": 0}
    assert not (target / ".opencode" / "agent" / "ask.md").exists()


def _git(target: Path, *args: str) -> None:
    proc = subprocess.run(
        ["git", "-C", str(target), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr


def test_lite_update_refuses_dirty_tree(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    _git(target, "init", "-q")
    _git(target, "config", "user.email", "test@example.com")
    _git(target, "config", "user.name", "test")
    lite_scaffold(target)
    _git(target, "add", "-A")
    _git(target, "commit", "-qm", "init")
    (target / "scratch.txt").write_text("dirty\n")
    with pytest.raises(SystemExit, match="uncommitted changes"):
        lite_update(target)
    counts = lite_update(target, allow_dirty=True)
    assert counts == {"wrote": 0, "same": 2}


def test_lite_cli_entrypoints(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    proc = subprocess.run(
        [sys.executable, str(LITE_INIT), str(target)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert (target / ".opencode" / "agent" / "ask.md").exists()
    proc = subprocess.run(
        [sys.executable, str(LITE_UPDATE), str(target)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    proc = subprocess.run(
        [sys.executable, str(LITE_UPDATE), str(target), "--dry-run"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr


def test_lite_cli_rejects_missing_dir(tmp_path):
    for script in (LITE_INIT, LITE_UPDATE):
        proc = subprocess.run(
            [sys.executable, str(script), str(tmp_path / "nope")],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 2
