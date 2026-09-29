"""flywheel-update: delete stale harness files, then install the latest.

Covers the pre-rename layout (flywheel-orchestrator*.md, problem-architect
agent) plus dry-run, collision-abort, dirty-tree, idempotency, and CLI.
Stdlib only.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from shared.scaffold import STALE_FILES, scaffold, update

REPO = Path(__file__).resolve().parent.parent
UPDATE = REPO / "scripts" / "flywheel-update"

STALE_CONTENTS = {
    ".opencode/agent/flywheel-orchestrator.md": "# old orchestrator\n",
    ".opencode/agent/flywheel-orchestrator-interactive.md": "# old interactive\n",
    ".opencode/agent/problem-architect.md": "# old architect\n",
}


def seed_stale(target: Path) -> None:
    for rel, content in STALE_CONTENTS.items():
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def test_stale_list_matches_known_renames():
    assert ".opencode/agent/flywheel-orchestrator.md" in STALE_FILES
    assert ".opencode/agent/flywheel-orchestrator-interactive.md" in STALE_FILES
    assert ".opencode/agent/problem-architect.md" in STALE_FILES


def test_update_removes_stale_and_installs_latest(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    seed_stale(target)
    counts = update(target, "x")
    for rel in STALE_FILES:
        assert not (target / rel).exists(), f"stale {rel} not removed"
    assert (target / ".opencode" / "agent" / "orchestrate.md").exists()
    assert (target / ".opencode" / "agent" / "build.md").exists()
    assert (target / ".opencode" / "agent" / "plan.md").exists()
    assert (target / ".opencode" / "skills" / "problem-architect" / "SKILL.md").exists()
    assert (target / ".flywheel" / "problem.yaml").exists()
    assert len(counts["removed"]) == len(STALE_FILES)
    assert counts["wrote"] > 0


def test_update_dry_run_changes_nothing(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    seed_stale(target)
    counts = update(target, "x", dry_run=True)
    for rel in STALE_FILES:
        assert (target / rel).exists(), f"dry-run removed {rel}"
    assert not (target / ".opencode" / "agent" / "orchestrate.md").exists()
    assert len(counts["removed"]) == len(STALE_FILES)


def test_update_aborts_on_user_modified_shipped_file(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    clash = target / ".opencode" / "agent"
    clash.mkdir(parents=True)
    (clash / "planner.md").write_text("user's own planner, do not touch")
    with pytest.raises(SystemExit, match="Refusing to overwrite"):
        update(target, "x")
    assert (clash / "planner.md").read_text() == "user's own planner, do not touch"


def _git(target: Path, *args: str) -> None:
    proc = subprocess.run(
        ["git", "-C", str(target), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr


def test_update_refuses_dirty_tree(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    _git(target, "init", "-q")
    _git(target, "config", "user.email", "test@example.com")
    _git(target, "config", "user.name", "test")
    scaffold(target, "x")
    _git(target, "add", "-A")
    _git(target, "commit", "-qm", "init")
    (target / ".flywheel" / "problem.yaml").write_text("dirty\n")
    with pytest.raises(SystemExit, match="uncommitted changes"):
        update(target, "x")
    counts = update(target, "x", allow_dirty=True)
    assert counts["wrote"] >= 0


def test_update_idempotent(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    seed_stale(target)
    first = update(target, "x")
    assert first["wrote"] > 0
    second = update(target, "x")
    assert second["wrote"] == 0
    assert second["removed"] == []


def test_cli_entrypoint(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    seed_stale(target)
    proc = subprocess.run(
        [sys.executable, str(UPDATE), str(target), "x"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    for rel in STALE_FILES:
        assert not (target / rel).exists()


def test_cli_dry_run_and_missing_dir(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    seed_stale(target)
    proc = subprocess.run(
        [sys.executable, str(UPDATE), str(target), "x", "--dry-run"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert (target / STALE_FILES[0]).exists()
    proc = subprocess.run(
        [sys.executable, str(UPDATE), str(tmp_path / "nope")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 2
