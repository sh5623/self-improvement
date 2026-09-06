# Convention changelog & routing (self-improvement)

> This file is the **single data file** for this project's self-improvement system (the plugin is the
> tool, this file is the data).
> Use si-improve / si-archive through the active runtime's installed skills; invocation and
> loading instructions belong in that runtime's entry document. Both runtimes share this history.
> Format: one unit of work = one §log block (holding N improvements) · one improvement = one §index
> line. **Newest on top** (never append at the bottom, or the file splits into two orderings).
> A log body carries **what is not in the landing document** (trigger, evidence, background,
> verification). The convention sentence itself is owned by the landing document, and "it is already
> in the landing doc" is not a reason to skip the body.

<!-- si-schema: v1 -->
<!-- si-plugin: v{{VERSION}} — Claude template version (separate from Codex metadata). Re-running `/self-improvement:si-init` compares this against the current version and repairs only the format wording above (project data is never touched). Do not delete. -->

## §routing — where conventions live in this project (narrowest scope first)

A new convention goes in **the first layer from the top that fits**. This table is canonical; if you
use a home that is not in it, update the table too.

| Layer | Actual location in this project | Loads / fires when | Budget |
| --- | --- | --- | --- |
| Tool config | {{TOOLS}} | Enforced automatically | — (always beats a document convention) |
| Claude path-scoped rules | {{RULES}} | Only when a matching file is touched | ≤150 lines per file |
| Task and domain docs | {{DOCS}} | Explicitly read during that task | Loose (≤400 lines per doc suggested) |
| Claude always-loaded docs | {{ALWAYS}} | Every session | **≤200 lines** — only what is true in every session, for every file |
| Archive | docs/conventions/archive/ | Never loaded | — (dead conventions and rotated logs) |

Shared rule bodies live once in task/domain docs. Runtime-specific rows describe their own
loading behavior; add Codex rows only after inspecting the actual AGENTS instruction chain.

## §budgets and rotation

- The budget numbers can be adjusted to suit the project, but "unlimited" is forbidden (a cap with no
  budget is a cap nobody keeps).
- This file's §log holds **at most 15 body blocks**. Whoever records an entry runs the check on the
  spot with si-improve §5's fence-aware count (`### ` blocks inside §log only; headings inside code
  fences or in other sections do not count). Move the overflow, oldest first, to the top
  of `archive/CHANGELOG-ARCHIVE.md` (**§index and §migration table stay in this file for the entire
  history**, which is what lets a duplication check finish in one file).
- Moves between layers and migrations to the archive follow the active runtime’s si-archive
  procedure and leave one row in the §migration table.
- Parallel safety: prefer **additive** convention edits (a new bullet, a new section), a new file
  where possible; reread the shared section before writing, and small single-purpose commits or PRs per rule in shared docs.

## §migration table (layer moves and archiving; citations of old locations are covered by this table)

| Date | Original location §clause | New location | Reason |
| --- | --- | --- | --- |

## §index (entire history · newest on top — a duplication check starts by skimming this table)

| Date | What bit you (≤120 chars, one line) | Landed |
| --- | --- | --- |
| {{DATE}} | Bootstrapped the self-improvement system: detected the document terrain, wrote the routing table | This file |

## §log (newest on top · one block = one unit of work · at most 15 bodies)

### {{DATE}} — si-init: bootstrapped the self-improvement system

- **Trigger**: this project had no place or procedure for feeding convention gaps back in.
- **Change**: created this file (the routing table is the detection result) and wired a three-line
  self-improvement section into the always-loaded doc.
- **Where**: `docs/conventions/CHANGELOG.md` · {{ANCHOR_DOC}}
- **Verification**: confirmed each location in the routing table exists (ls/grep).
- **Commit/PR**: (per the project's git rules)
