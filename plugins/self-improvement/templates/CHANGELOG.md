# Convention changelog and routing (self-improvement)

This is the project's shared data file, not an instruction file for one runtime.
Use si-init, si-improve and si-archive through the active runtime's installed skills.
Runtime invocation and loading instructions belong in its own entry document.

<!-- si-schema: v1 -->
<!-- si-codex-template: v{{VERSION}} -->

One unit of work = one log body containing N improvements. One improvement = one index
entry. Both are newest first. Log bodies contain trigger/evidence, change, destination,
verification and commit/PR. The rule text remains in its canonical document.

## §routing

| Layer | Actual location | Consumer / loading | Budget |
| --- | --- | --- | --- |
| Tools | none (detect project configs and scripts) | Shared / execution | — |
| Shared conventions and task docs | docs/conventions/ | Both / explicit Read | 400 lines suggested |
| Codex root instructions | {{ANCHOR}} | Codex / instruction chain | 200 lines |
| Codex scoped instructions | none (create a directory AGENTS.md when needed) | Codex / directory scope | 150 lines |
| Claude instructions | none (register existing CLAUDE.md and .claude/rules separately) | Claude / its own loading rules | 200 root / 150 scoped |
| Archive | {{ARCHIVE}} | Both / explicit historical lookup | — |

## §budgets and rotation

Measure the routed instruction docs before adding rules. Keep at most 15 actual work
blocks in §log; count only this section, ignoring code-fenced headings. On overflow,
si-archive moves the oldest bodies to the registered archive's CHANGELOG-ARCHIVE.md. If the
archive is none, propose a destination before moving records. The full index and migration
history stay here. Existing project budgets can override these defaults.

## §migration table

| Date | Original location | New location | Reason |
| --- | --- | --- | --- |

## §index

| Date | What bit you (one line, ≤120 chars) | Landed |
| --- | --- | --- |
| {{DATE}} | Registered the shared convention system for Codex | {{ANCHOR}} |

## §log

### {{DATE}} — Initialize self-improvement in Codex

- Trigger: no existing convention data file was found.
- Change: created a shared record and a runtime-scoped Codex pointer.
- Where: docs/conventions/CHANGELOG.md · {{ANCHOR}}
- Verification: initializer resolved the destination; routing terrain still needs inspection.
- Commit/PR: uncommitted (working tree)
