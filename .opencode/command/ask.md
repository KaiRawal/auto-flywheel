---
description: Ask questions about the repo and recent changes — read-only, never edits.
agent: ask
---

Ask the ask agent about `$ARGUMENTS` (a question, or empty for orientation).

With no arguments, orient the user: what this repo does, its layout, and
the most recent commits (`git log --oneline -10`). With a question, answer
it from the repo and git history. Read-only: never edit files, never run
training, tests, or installs — offer verification commands instead.
