---
name: si-init
description: >-
  Use to bootstrap a project once, when it has no self-improvement data file (convention changelog
  and routing table). Triggers include "set up self-improvement", "si-init", and si-improve /
  si-archive / convention-smith failing to find the data file. Also re-run it right after a plugin
  update — it compares the data file's version stamp and repairs stale template wording (project
  data is never touched). Re-running is safe and idempotent: when it detects an existing system it
  registers and repairs rather than overwriting.
---

# si-init — project bootstrap (idempotent)

The plugin is the **tool**. In your project it leaves **one data file**
(`docs/conventions/CHANGELOG.md`) and a three-line pointer in the always-loaded doc. Frontend,
backend, scripting, documentation: it makes no difference, because detection reads the terrain and
the table records it.

## 1. Detect an existing system — never overwrite

```bash
ls docs/conventions/CHANGELOG.md 2>/dev/null
grep -ril "CONVENTIONS-CHANGELOG\|self-improvement\|자가개선" --include="*.md" docs .claude . 2>/dev/null | grep -v node_modules | head
```

(The pattern includes the legacy Korean term deliberately: installations predating v0.5.0 wrote it
into their always-loaded docs, and dropping it would make this skill create a second system next to
a working one.)

**Judging the candidates — that grep catches things that are not data files.** Observed: a README.md
containing only the phrase "self-improvement" came back as the first candidate. For each candidate:

```bash
grep -n "^#\+ .*[Ii]ndex\|^#\+ .*[Rr]outing\|^#\+ .*색인\|^#\+ .*라우팅\|si-plugin:\|^### 20[0-9][0-9]-" <candidate>
```

- **A data file in this plugin's format**: has an §index/§routing table, or a `<!-- si-plugin: v` stamp.
- **An existing system in another shape**: no such table, but **it genuinely holds convention
  records** (dated log blocks, a list of clauses). Missing tables, budgets, or a migration table are
  not grounds for exclusion. Recognize it as canonical and register it, merely *propose* the
  missing pieces per the third bullet below, and **write its format map** (§4) so that si-improve,
  si-archive, and convention-smith know what to read in place of the tables they would otherwise
  assume.
- **Not a candidate**: a document that only **describes** the system (a README, a plugin
  introduction, zero records), or any file with `archive`/`ARCHIVE` in its name or path (new blocks
  would stack on top of old logs).

Treatment by verdict:

- **A data file in this plugin's format already exists**: verify and repair only that the §routing
  table matches the current terrain (confirm each layer's location really exists), then stop.
- **An existing system in another shape** (its own convention changelog or protocol doc, e.g.
  `docs/**/CONVENTIONS-CHANGELOG.md`): **do not create a new one. The existing system is canonical.**
  Run §4's wiring **with its real paths substituted in**, and do not stop at reporting. A report dies
  with the session, and the next session re-runs the same fallback grep and picks the README or the
  archive again. If that system lacks something (routing table, budgets, rotation, migration table),
  raise it **as a proposal only**. Never graft it on by force. What makes a table-less system
  *usable* afterwards is not the graft but the **format map** in the §4 declaration: the three
  skills and the agent read that map and substitute the file's own parts for the tables. (Before
  the map existed, registration succeeded and the very next si-improve stalled on "skim the
  §index" of a file that had none.)
- **Zero candidates remain, so there is no existing system**: go to §2 and create one. Finishing here
  with a mistaken registration means no data file gets created, and the next session's si-improve §0
  picks up the same README again.

**Version drift repair — the main reason to re-run.** When the plugin updates, the skills and agent
(the tools) become current while the project's data file keeps **the old template wording** (the
price of separating tool from data). Compare the `<!-- si-plugin: vX.Y.Z -->` stamp at the top of the
data file against the current plugin version
(`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`):

- **Stamp lower than the current version**: update only the **fixed text** from
  `templates/CHANGELOG.template.md` (format lines, §log headings, budget and rotation wording) and
  raise the stamp. **Project data is immutable** — the routing table's values, §index, §log, and
  §migration table are not touched.
- **No stamp** (a registered pre-existing system): do not auto-update. That document belongs to the
  project. Report only the declarations that **contradict** the current procedure. (Observed: a
  header saying "1 improvement = 1 block" while the procedure said "1 unit of work = 1 block", which
  would make the next session follow the header and drop the log body.)
- **Stamp equal to the current version**: nothing to repair.

## 2. Detect the document terrain — raw material for the routing table

| Layer | What to find | Example command (finding only what exists is fine; an empty result is valid) |
|---|---|---|
| Tool config | linter, formatter, type check, tests, CI | `ls biome.json eslint.config.* .eslintrc* .prettierrc* tsconfig.json pyproject.toml ruff.toml setup.cfg build.gradle* pom.xml Makefile 2>/dev/null; ls .github/workflows 2>/dev/null` plus package-manager scripts (`package.json` scripts and similar) |
| Path-scoped rules | rule files with `paths:` frontmatter | `ls .claude/rules/ 2>/dev/null` |
| Task and domain docs | playbooks, spec directories | `ls docs/ 2>/dev/null` |
| Always-loaded docs | AGENTS.md / CLAUDE.md and their import relationship | `ls AGENTS.md CLAUDE.md .claude/CLAUDE.md 2>/dev/null; grep -n '@AGENTS\.md' CLAUDE.md 2>/dev/null` (the presence of the import decides §4's branch) |

An empty layer is not a failure. Record it in the table as `none (create when needed)`. It gets
created the first time a self-improvement needs that layer.

## 3. Create the data file

Copy `templates/CHANGELOG.template.md` from this skill's folder to `docs/conventions/CHANGELOG.md`
and substitute:

- `{{DATE}}` → today (YYYY-MM-DD) · `{{VERSION}}` → the current plugin version (`version` in
  `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`) · `{{TOOLS}}`/`{{RULES}}`/`{{DOCS}}`/`{{ALWAYS}}`
  → the §2 detection results (**using this project's real filenames**) · `{{ANCHOR_DOC}}` → the
  document you wire in §4.
- The default budgets (always-loaded ≤200 lines, path rules ≤150 lines, log body ≤15 blocks) are in
  the template. Projects may adjust them, but "unlimited" is forbidden.

## 4. Wire the always-loaded doc — a three-line, tool-agnostic pointer

**Which file**: if `AGENTS.md` exists, use it (the cross-tool standard, so colleagues and tools
without this plugin see it too). If only `CLAUDE.md` exists, use that. If neither exists, create
`AGENTS.md`.

**If you wrote to AGENTS.md, wire the CLAUDE.md import in the same step.** Claude Code reads
`CLAUDE.md` and does not read `AGENTS.md` (official docs: "Claude Code reads `CLAUDE.md`, not
`AGENTS.md`" — https://code.claude.com/docs/en/memory). Without the import, the pointer you wrote in
AGENTS.md **never loads** in a Claude session: you are left with a report claiming it was wired, and
the next session falls back to the grep.

```bash
ls -l CLAUDE.md 2>/dev/null; grep -n '@AGENTS\.md' CLAUDE.md 2>/dev/null
```

- **What counts as a valid import**: a line containing `@AGENTS.md` **outside** backticks and code
  fences. Claude Code's import parser skips code spans and fences, so a wrapped mention like
  `` `@AGENTS.md` `` is not an import (the grep above catches those too, so read the matched line and
  judge it).
- `CLAUDE.md` missing: create a stub containing only the `@AGENTS.md` line.
- Present but with no valid import: add `@AGENTS.md` at the **top** of the file, without backticks
  (existing content unchanged).
- A valid import already exists, or `CLAUDE.md` is a symlink to `AGENTS.md` (check with `ls -l`):
  skip. Idempotent.
- Verification: the grep above shows at least one `@AGENTS.md` outside backticks. Whether CLAUDE.md
  appears under **Memory files** in `/context` is confirmed in the next session.

If a self-improvement section already exists, skip (idempotent). What goes in is the three lines
below, and not the whole doctrine, since plugin users already get it injected by the SessionStart
hook. These three lines are the anchor for people and tools without the plugin:

```markdown
## Self-improvement
When a convention or document is missing or wrong and it costs you, do not just fix that one spot;
fix the convention itself (when it is general and evidenced, inside the same unit of work).
Procedure, routing, and records: the header of `docs/conventions/CHANGELOG.md`. State
"self-improvement: N items / none" in your work report.
```

If you arrived here from an existing-system registration (§1), substitute that system's **real
files** into those three lines, naming each one separately when the data file, protocol doc, and
archive are split apart. The next session's si-improve §0 reads this declaration **first**, so this
wiring is the only channel that carries the existing system forward.

**For a registered system, add a fourth line — the format map.** si-improve, si-archive, and
convention-smith are written against this plugin's shape (§routing table, §index, `### ` log
blocks, §migration table). A registered system may have none of those, and §1 forbids grafting them
on, so declare what stands in for each. Later sessions read this line instead of assuming:

```markdown
Format: data file `<path>` (own format) · index: <§section, or "none — grep the log headings"> · log unit: <"### YYYY-MM-DD blocks" | "dated bullets" | …> · routing: <§section or file, or "none — default layer order"> · archive: <path, or "none — propose before rotating">
```

Every slot may say `none`. A missing slot, or a registered system with no `Format:` line at all, is
read as `none` everywhere (si-improve §0, si-archive §0, convention-smith §0). Do not invent a
value to fill a slot: `none` routes those procedures to their fallback branch, an invented section
name sends them to grep a heading that does not exist and pass silently.

## 5. Report

- Where the pointer was wired, plus **the Claude load path**: `<file>` and
  `CLAUDE.md import: present / added / not applicable (the pointer is in CLAUDE.md itself)`. Finishing
  with the pointer only in AGENTS.md and no import is a wiring failure.
- Result: `created` / `registered existing` (path, **plus the format map exactly as written into
  the declaration**) / `repaired N` (write version drift repairs as `vX.Y.Z → vA.B.C, N lines of
  wording`) / `contradictions N` (unstamped existing system: proposals only).
- Show the full routing table, so the user can correct a detection error immediately.
- One next action: "when something bites you, run `/self-improvement:si-improve`".
