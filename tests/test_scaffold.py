import re
import subprocess
import sys
from pathlib import Path

import pytest

from shared.scaffold import AGENT_FILES, COMMAND_FILES, scaffold

REPO = Path(__file__).resolve().parent.parent
INIT = REPO / "scripts" / "flywheel-init"

STALE_PATTERNS = [
    r"problems/<",
    r"problems/\*",
    r"(?<!\.flywheel/)shared/observe\.py",
    r"(?<!\.flywheel/)shared/event-schema\.md",
    r"(?<!\.flywheel/)shared/gate-contract\.md",
    r"(?<!\.flywheel/)runs/<",
    r"(?<!\.flywheel/)runs/\.\.\.",
    # bare `--problem toy-tabular` in a command example is fine; these are not:
    r"pick `toy-tabular`",
    r"Offer the `toy-tabular` example",
]


def scaffolded_md_files(target: Path) -> list[Path]:
    return [
        *(target / ".opencode" / "agent" / f for f in AGENT_FILES),
        *(target / ".opencode" / "command" / f for f in COMMAND_FILES),
        target / ".opencode" / "skills" / "flywheel" / "SKILL.md",
        target / ".flywheel" / "shared" / "event-schema.md",
        target / ".flywheel" / "shared" / "gate-contract.md",
        target / ".flywheel" / "shared" / "decision-log.md",
    ]


def test_scaffold_layout_and_problem_name(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    counts = scaffold(target, "my-feature")
    assert counts["wrote"] > 0
    assert (target / ".flywheel" / "problem.yaml").exists()
    text = (target / ".flywheel" / "problem.yaml").read_text()
    assert "problem: my-feature" in text
    assert "__PROBLEM_NAME__" not in text
    assert (target / ".flywheel" / "shared" / "observe.py").exists()
    for path in scaffolded_md_files(target):
        assert path.exists(), f"missing {path}"


def test_no_stale_lab_paths(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    scaffold(target, "x")
    bad = []
    for path in scaffolded_md_files(target):
        content = path.read_text()
        for pattern in STALE_PATTERNS:
            if re.search(pattern, content):
                bad.append(f"{path.name}: {pattern}")
    assert bad == []


def test_rewritten_paths_point_at_flywheel_dir(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    scaffold(target, "x")
    orch = (target / ".opencode" / "agent" / "flywheel-orchestrator.md").read_text()
    assert ".flywheel/problem.yaml" in orch
    assert ".flywheel/shared/observe.py" in orch
    assert ".flywheel/runs/" in orch
    new = (target / ".opencode" / "command" / "flywheel-new.md").read_text()
    assert ".flywheel/problem.yaml" in new


def test_copied_observe_still_runs(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    scaffold(target, "x")
    run_dir = target / ".flywheel" / "runs" / "ts1"
    for args in (
        ["init", "--run-dir", str(run_dir), "--problem", "x"],
        [
            "append", "--run-dir", str(run_dir), "--phase", "plan",
            "--agent", "orchestrator", "--event", "decision",
            "--decision", "picked v1",
        ],
    ):
        proc = subprocess.run(
            [sys.executable, str(target / ".flywheel" / "shared" / "observe.py"), *args],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
    assert (run_dir / "events.jsonl").exists()


def test_idempotent_rerun(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    first = scaffold(target, "x")
    assert first["wrote"] > 0
    second = scaffold(target, "x")
    assert second["wrote"] == 0


def test_collision_aborts(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    clash = target / ".opencode" / "agent"
    clash.mkdir(parents=True)
    (clash / "planner.md").write_text("user's own planner, do not touch")
    with pytest.raises(SystemExit, match="Refusing to overwrite"):
        scaffold(target, "x")


def test_gitignore_and_agents_merge(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    (target / ".gitignore").write_text("node_modules/\n")
    (target / "AGENTS.md").write_text("# my repo rules\n")
    scaffold(target, "x")
    scaffold(target, "x")  # second run must not duplicate
    gi = (target / ".gitignore").read_text()
    assert ".flywheel/runs/" in gi and "node_modules/" in gi
    assert gi.count(".flywheel/runs/") == 1
    agents = (target / "AGENTS.md").read_text()
    assert "# my repo rules" in agents and "flywheel:start" in agents
    assert agents.count("flywheel:start") == 1


def test_cli_entrypoint(tmp_path):
    target = tmp_path / "myrepo"
    target.mkdir()
    proc = subprocess.run(
        [sys.executable, str(INIT), str(target), "My Feature!"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    text = (target / ".flywheel" / "problem.yaml").read_text()
    assert re.search(r"^problem: my-feature$", text, re.MULTILINE)


def test_cli_rejects_missing_dir(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(INIT), str(tmp_path / "nope")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 2
