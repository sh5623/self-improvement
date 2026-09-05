---
name: si-init
description: Bootstrap or register a project's convention repair system in Codex, preserving existing records and separating Codex instruction wiring from Claude. Use for initial setup or checking the setup after a plugin update.
---

# Initialize self-improvement in Codex

Read [runtime boundaries](../../references/runtime.md) and
[data discovery and format maps](../../references/data.md).

Identify the project root and the canonical existing system before creating a file. Existing
Claude registrations and table-less convention logs remain canonical. Do not copy a whole
CLAUDE.md into AGENTS.md, create a Claude import, or start a second log for Codex.

The bundled helper performs conservative, idempotent wiring:

~~~sh
python3 "<this-skill-directory>/../../scripts/init_project.py" --project "<project-root>" --check
python3 "<this-skill-directory>/../../scripts/init_project.py" --project "<project-root>"
~~~

Resolve the script relative to this installed SKILL.md, not to the shell cwd. Python 3.9+
is required only for the helper. Without it, perform the same inspection and minimal edits
directly; report that the helper was not run.

- The helper creates a neutral generated log only when no credible system exists. It
  registers existing data without modifying its bytes. Multiple candidates require an
  explicit canonical choice: `--data-file "docs/actual-log.md"`.
- Existing registered systems default to `archive: none` until their actual destination is
  confirmed. Preserve a legacy declared archive or pass `--archive "docs/actual-archive"`;
  this registers the path and does not move records.
- It writes only the marked Codex section in the effective AGENTS.override.md/AGENTS.md.
  Symlinked instruction files require inspecting their ownership first; do not bypass a
  refusal by writing through a link into CLAUDE.md.
- Inspect the reported format map and correct it to the real system's sections, log unit,
  budgets and archive. `none` is valid. Do not create missing tables just to satisfy defaults.

Inspect the actual document terrain: tool configs and scripts; nested Codex instruction
files; shared task/domain docs; Claude-only files as a separate runtime layer. On a new log,
fill §routing with existing locations or `none (create when needed)`. Add Codex destinations
to an existing routing system in its own format, without changing Claude's routing rows.

After a plugin update, compare the installed .codex-plugin/plugin.json version with the
Codex template stamp, if present. The helper intentionally preserves existing data. Inspect
stale wording and repair only Codex-owned fixed text when needed, preserving table values,
index, migration history, log bodies and all Claude stamps. A public/internal version
switch is not evidence that the data needs upgrading; inspect schema and content.

Report created / registered / unchanged / repaired, the real data path, effective Codex
instruction path, format map and any unmeasured or missing layer. Confirm Claude files
were not modified by Codex wiring. Next action: `$self-improvement:si-improve` when an evidenced gap recurs.
