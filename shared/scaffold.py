"""Copy-only installer: bring the flywheel to the repo where you are.

Usage:
    scripts/flywheel-init <target-dir> [problem-name]

Copies agents, commands, the flywheel skill, the provenance logger and a
starter `.flywheel/problem.yaml` into an existing repo. No network, no
symlinks, nothing that breaks if this checkout moves or is deleted.

Safe to re-run (idempotent). Never overwrites a file whose content differs;
it aborts and shows you the collision instead.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parent.parent


def _discover(relative_dir: str, *patterns: str, exclude: frozenset[str] = frozenset()) -> list[str]:
    """List shipped files in SOURCE_ROOT/<relative_dir> (sorted, auto-discovered).

    New agents/commands/skills/shared docs ship on next flywheel-init with no
    list to update. Callers pass exclude for lab-only files (e.g. scaffold.py).
    """
    base = SOURCE_ROOT / relative_dir
    found: set[str] = set()
    for pattern in patterns:
        for path in base.glob(pattern):
            if path.is_file() and path.name not in exclude:
                found.add(path.name)
    return sorted(found)


# Auto-discovered so flywheel-init always ships whatever is available,
# including ask.md. Lab-only files stay excluded (scaffold.py itself,
# problem.yaml/README.md lab templates — only problem.scaffold.yaml ships).
AGENT_FILES = _discover(".opencode/agent", "*.md")

COMMAND_FILES = _discover(".opencode/command", "*.md")

SKILL_FILES = _discover(".opencode/skills/flywheel", "*.md")

SHARED_FILES = _discover("shared", "*.py", "*.md", exclude=frozenset({"scaffold.py"}))

# Ordered (pattern, replacement). Specific rules first, generic path
# remaps after. Applied to copied prompt/config markdown only.
REWRITE_RULES: list[tuple[str, str]] = [
    (
        r"Copy `problems/_template/problem\.yaml` to `problems/<name>/problem\.yaml`",
        r"Fill in `.flywheel/problem.yaml` (scaffolded by `flywheel-init`)",
    ),
    (
        (
            r"If empty, list `problems/\*/problem\.yaml` and ask which "
            r"\(via `question` in interactive, or pick `toy-tabular` in autonomous\)\."
        ),
        r"If empty, use `.flywheel/problem.yaml`.",
    ),
    (
        r"or pick `toy-tabular` in autonomous",
        r"or use `.flywheel/problem.yaml` in autonomous",
    ),
    (
        r"Offer the `toy-tabular` example if they are unsure\.",
        r"Offer a minimal worked example if they are unsure.",
    ),
    (
        (
            r"pick sensible defaults \(e\.g\. `f1 >= 0\.8`, `type: prediction`, "
            r"`sklearn:datasets\.load_breast_cancer`\)"
        ),
        (
            r"pick sensible defaults (`type: feature`, gates from the repo's test "
            r"command, `target.scope` defaulting to the repo root)"
        ),
    ),
    (
        r"Never modify the committed `problems/` tree\.",
        r"Never modify `.flywheel/` config; edit only within the assigned scope.",
    ),
    (r"problems/<[^>]*>/problem\.yaml", r".flywheel/problem.yaml"),
    (r"problems/\*/problem\.yaml", r".flywheel/problem.yaml"),
    (r"problems/<[^>]*>", r".flywheel"),
    (r"problems/\*", r".flywheel"),
    (r"runs/<p>/<ts>", r".flywheel/runs/<ts>"),
    (r"runs/<problem>/<ts>", r".flywheel/runs/<ts>"),
    (r"runs/toy-tabular/<ts>", r".flywheel/runs/<ts>"),
    (r"runs/<problem>", r".flywheel/runs"),
    (r"runs/<p>", r".flywheel/runs"),
    (r"runs/\.\.\.", r".flywheel/runs/..."),
    (
        r"shared/(observe\.py|event-schema\.md|gate-contract\.md|decision-log\.md)",
        r".flywheel/shared/\1",
    ),
]

AGENTS_SECTION = """<!-- flywheel:start -->
## Flywheel (scaffolded by auto-flywheel)
- Flywheel home is `.flywheel/`: spec `.flywheel/problem.yaml`, scratch `.flywheel/runs/`, logger `.flywheel/shared/observe.py`.
- Work on scratch branch `flywheel/<problem>-<ts>`; deliver the winner there. Never push unless asked.
- Edit only within `target.scope` from `.flywheel/problem.yaml`. Never hand-edit `.flywheel/` mid-run.
- `.venv`-only installs; disk/mem guards + `timeout` per `constraints`.
- Commands: `/flywheel-new`, `/flywheel-run .flywheel`, `/flywheel-status`, `/flywheel-abort`.
<!-- flywheel:end -->
"""

GITIGNORE_LINES = [".flywheel/runs/", ".venv/"]


def rewrite_text(text: str) -> str:
    for pattern, repl in REWRITE_RULES:
        text = re.sub(pattern, repl, text)
    return text


def install_file(src: Path, dst: Path, collisions: list[str]) -> str:
    """Copy src to dst with rewrite. Returns 'wrote' | 'same' | 'collision'."""
    content = rewrite_text(src.read_text(encoding="utf-8"))
    if dst.exists():
        if dst.read_text(encoding="utf-8") == content:
            return "same"
        collisions.append(str(dst))
        return "collision"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")
    return "wrote"


def ensure_gitignore(target: Path) -> str:
    gi = target / ".gitignore"
    content = gi.read_text(encoding="utf-8") if gi.exists() else ""
    existing = content.splitlines()
    missing = [line for line in GITIGNORE_LINES if line not in existing]
    if not missing:
        return "same"
    with open(gi, "a", encoding="utf-8") as f:
        if content and not content.endswith("\n"):
            f.write("\n")
        f.writelines(line + "\n" for line in missing)
    return "wrote"


def ensure_agents_section(target: Path) -> str:
    path = target / "AGENTS.md"
    if path.exists():
        content = path.read_text(encoding="utf-8")
        if "<!-- flywheel:start -->" in content:
            return "same"
        if not content.endswith("\n"):
            content += "\n"
        path.write_text(content + "\n" + AGENTS_SECTION, encoding="utf-8")
        return "wrote"
    path.write_text("# AGENTS.md\n\n" + AGENTS_SECTION, encoding="utf-8")
    return "wrote"


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "flywheel-problem"


def scaffold(target: Path, problem: str) -> dict:
    """Run the scaffold. Returns counts dict. Raises SystemExit on collision."""
    collisions: list[str] = []
    counts = {"wrote": 0, "same": 0}

    def put(src: Path, dst: Path) -> None:
        outcome = install_file(src, dst, collisions)
        if outcome != "collision":
            counts[outcome] += 1

    for name in AGENT_FILES:
        put(SOURCE_ROOT / ".opencode" / "agent" / name, target / ".opencode" / "agent" / name)
    for name in COMMAND_FILES:
        put(
            SOURCE_ROOT / ".opencode" / "command" / name,
            target / ".opencode" / "command" / name,
        )
    for name in SKILL_FILES:
        put(
            SOURCE_ROOT / ".opencode" / "skills" / "flywheel" / name,
            target / ".opencode" / "skills" / "flywheel" / name,
        )
    for name in SHARED_FILES:
        src = SOURCE_ROOT / "shared" / name
        dst = target / ".flywheel" / "shared" / name
        if name.endswith(".py"):
            # Code ships byte-identical; only docs get path rewrites.
            if dst.exists() and dst.read_bytes() != src.read_bytes():
                collisions.append(str(dst))
            elif not dst.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
                counts["wrote"] += 1
            else:
                counts["same"] += 1
        else:
            put(src, dst)

    problem_yaml = target / ".flywheel" / "problem.yaml"
    if not problem_yaml.exists():
        template = (SOURCE_ROOT / "problems" / "_template" / "problem.scaffold.yaml").read_text(
            encoding="utf-8"
        )
        problem_yaml.parent.mkdir(parents=True, exist_ok=True)
        problem_yaml.write_text(
            template.replace("__PROBLEM_NAME__", problem), encoding="utf-8"
        )
        counts["wrote"] += 1
    else:
        counts["same"] += 1

    counts["gitignore"] = ensure_gitignore(target)
    counts["agents_md"] = ensure_agents_section(target)

    if collisions:
        raise SystemExit(
            "Refusing to overwrite files with different content:\n"
            + "\n".join(f"  - {c}" for c in collisions)
            + "\nDelete, move, or reconcile them, then re-run."
        )
    return counts


def self_check(target: Path) -> list[str]:
    warnings: list[str] = []
    if shutil.which("python3") is None:
        warnings.append("python3 not found on PATH (needed for .flywheel/shared/observe.py)")
    opencode = shutil.which("opencode")
    if opencode is None:
        warnings.append("opencode not found on PATH — install it, then re-run this check")
    else:
        try:
            proc = subprocess.run(
                [opencode, "agent", "list"],
                capture_output=True,
                text=True,
                check=False,
                cwd=target,
                timeout=60,
            )
            found = set()
            for line in proc.stdout.splitlines():
                match = re.match(r"^([a-z][a-z0-9-]*) \((?:primary|subagent)\)", line)
                if match:
                    found.add(match.group(1))
            expected = {Path(f).stem for f in AGENT_FILES}
            missing = sorted(expected - found)
            if missing:
                warnings.append(
                    "these agents are not registered: "
                    + ", ".join(missing)
                    + f" — quit and restart opencode in {target}, then run "
                    "`opencode agent list | grep -E 'ask|flywheel|planner|researcher|sandbox|architect'`"
                )
        except (subprocess.SubprocessError, OSError) as exc:
            warnings.append(f"could not run `opencode agent list`: {exc}")
    return warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bring the flywheel to the repo where you are (copy-only, idempotent)."
    )
    parser.add_argument("target", help="existing repo directory to scaffold into")
    parser.add_argument("problem", nargs="?", help="problem name (default: target dir name)")
    args = parser.parse_args(argv)

    target = Path(args.target).resolve()
    if not target.is_dir():
        print(f"error: target is not a directory: {target}", file=sys.stderr)
        return 2
    git_check = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        check=False,
    )
    if git_check.returncode != 0:
        print(
            f"warning: {target} is not a git repo — branch delivery "
            "needs git; continuing with patch-only delivery",
        )

    problem = slugify(args.problem or target.name)
    try:
        counts = scaffold(target, problem)
    except SystemExit as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"scaffolded '{problem}' into {target} ({counts['wrote']} wrote, {counts['same']} kept)")
    print("  .opencode/agent, .opencode/command, .opencode/skills/flywheel")
    print("  .flywheel/problem.yaml, .flywheel/shared/*")
    for warning in self_check(target):
        print(f"warning: {warning}")
    print(f"next: cd {target} && opencode   (restart once), then /flywheel-new")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
