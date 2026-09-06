---
name: si-archive
description: >-
  Use when a convention document has gone over budget (line count or block count), or when dead and
  duplicated clauses have piled up. Triggers include "the convention doc is too long", "clean up the
  conventions", "do an archive pass", the si-improve section 6 check reporting the log cap (15
  blocks) exceeded, and an always-loaded doc growing large enough to weigh on session context. Do
  NOT load for: adding or correcting an individual rule (si-improve owns that), or first-time setup
  (si-init owns that).
---

# si-archive — the demotion and archiving system for bloated or dead conventions

Read [Claude runtime boundaries](../../references/claude-runtime.md) before this procedure.

## Principles

- **Movement is downward only**: always-loaded doc → path-scoped rule or task doc (scope demotion);
  dead → `<archive>` (never loaded). **Archiving is not deletion.** Preserve the original text, the
  reason, and the date, so "removed on purpose" stays distinguishable from "dropped by accident".
- **One move = one row in the §migration table.** Do not scatter individual pointers through the
  source document. If several clauses left, one line at the top of that document saying
  "migrations: `<datafile>` §migration table" is enough.
- **Never send the §index or the §migration table to the archive.** They stay in the head for the
  entire history. That is the premise behind si-improve §3's claim that a duplication check is one
  file skim.

## 0. Resolve the paths — the two values every command below substitutes

Read the Claude declaration first; legacy AGENTS declarations supply shared data paths only.
Measure and edit Claude-owned instructions or shared project docs, not Codex-owned instructions.


Find them with si-improve §0's search order (① the path declared in the always-loaded doc's
self-improvement section → ② `docs/conventions/CHANGELOG.md` → ③ fallback grep, picking **the file
that has an §index**, excluding `archive`/`ARCHIVE` and READMEs). Substitute the result into every
command below. **Do not type the default paths verbatim**: a project with a registered pre-existing
system has different paths, and measuring a file that does not exist reads as "within budget".

- `<datafile>` = the data file you found. Confirm it exists with `ls <datafile>` before proceeding.
- `<archive>` = the archive path from the declaration if it names one, otherwise `archive/` in the
  directory holding `<datafile>` (this skill creates it if missing — **unless** the format map says
  `archive: none`, in which case dead clauses and rotation are *proposed*, never moved).
- **The format map** (registered systems only — the `Format:` line of the declaration, si-init §4).
  `routing: none` → §1 measures the two documents every project has (the always-loaded doc and
  `<datafile>`) and lists the rest as "not measured — no routing table; propose one via si-init".
  A log unit other than `### ` blocks → count §1 and §4 by that unit. No map on a registered system
  → every slot is `none`.

## 1. Entry — two triggers, measured separately

**Trigger A — over budget.** For each document in `<datafile>`'s §routing table (or, with no table,
the always-loaded doc and `<datafile>` — §0):

````bash
wc -l <always-loaded doc> <path-scoped rule files…>   # compare against the budgets in the table
# log body blocks (cap 15): fence-aware, log section only. unit = the format map's record regex
# (^### for the generated layout, ^- for dated bullets); sec = the log section's ## heading ('' = whole file)
awk -v unit='^### ' -v sec='§(log|로그)' '
BEGIN { inlog = (sec == "") }
{ t = ""; if (match($0, /^ ? ? ?(```+|~~~+)/)) { t = substr($0, RSTART, RLENGTH); sub(/^ +/, "", t) } }
fence == "" && t != "" { fence = substr(t, 1, 1); flen = length(t); next }
fence != "" { if (t != "" && substr(t, 1, 1) == fence && length(t) >= flen && substr($0, RSTART + RLENGTH) ~ /^[ \t]*$/) fence = ""; next }
/^## / { inlog = (sec == "" || $0 ~ sec); next }
inlog && $0 ~ unit { n++ }
END { print n + 0 }
' <datafile>
````

The awk treats a fence the way CommonMark does (up to 3 spaces, then 3 or more backticks or tildes,
closed only by the same character at the same length or longer), so example headings inside fences, a
shorter or different inner fence, and headings in other sections are not counted. Plain
`grep -c '^### '` over-counts each of those. Over budget → that document goes to §2, and an over-cap
log goes to §4.

**Trigger B — a dead or duplicated clause was named.** The caller asked for a cleanup pass, si-improve
§2 classified a gap as "removal of a dead rule", or a specific clause was reported as living in two
places. **Budget does not gate this trigger**: a 100-line document can carry a rule for a feature
that no longer exists, and it should not have to reach 200 lines before that rule can be retired.
The named document (or clause) goes to §2 even when every measurement in trigger A is within budget.

If neither trigger fires, **stop**. "No cleanup needed" is a valid result, and forcing a migration is
not an improvement. Take to §2 only what a trigger named: trigger A does not license a sweep of
documents that are within budget, and trigger B does not license touching clauses nobody named.

## 2. Classify the clauses in the document a trigger named (clause by clause)

| Verdict | Criterion | Treatment |
|---|---|---|
| **Demote** | True only for certain paths or certain tasks | Move to a path-scoped rule (give it `paths:`) or a task doc |
| **Merge** | The same content lives in two or more places | Pick one canonical home, delete the rest, add a migration row |
| **Dead** | The target code or procedure is gone / zero references / a tool now enforces it | Move to `<archive>/YYYY-<slug>.md` with the reason |
| **Keep** | True in every session | Leave it |

**A dead verdict needs evidence too** (an exclusion is a judgment, same principle as si-improve §4):
confirm zero references with `grep -rn "<rule keyword>" .`, confirm the target file or procedure is
absent, confirm the replacing tool rule exists. "I don't think we use this" is not a verdict.

## 3. Execute

1. Move the clause to its new home, matching that file's voice. When creating a new path-scoped rule,
   give it `paths:` frontmatter.
2. Add one row to `<datafile>`'s §migration table:
   `| date | original location §clause | new location | reason (demote/merge/dead) |`.
3. Delete the clause from the source document (no scattered pointers, per the principles above).
4. **Citation integrity**: run `grep -rn "<old section or rule name>" --include="*.md" .` to find
   citations and either update them or confirm the migration table covers them. Never leave a
   dangling citation.

## 4. Changelog rotation — bodies only, the index stays

If log blocks > 15, move the oldest bodies (as many as the overflow) to the **top** of
`<archive>/CHANGELOG-ARCHIVE.md` (create it if missing). The §index rows and the §migration table
stay in the head file (`<datafile>`). Re-run the check afterwards to confirm ≤15. In a registered
system, count by the format map's log unit, and if the map says `archive: none`, report the
overflow with a proposed archive path instead of moving anything (§0).

## 5. Verify and report

- Re-measure (the §1 commands) and confirm every document is within budget.
- Final grep on the moved clauses' keywords to confirm zero dangling citations.
- Report: **trigger A / B / both · demoted N · merged N · dead N · rotated N blocks**, plus where
  the migration table is (or "proposed — archive: none"). If this pass surfaced a convention gap,
  handle it through si-improve and include the "self-improvement: N items / none" line.

## Why it has this shape — the incidents behind it

- A cap written only in a file header, wired into no procedure, let a log grow to **42 blocks and 949
  lines** before anyone noticed. That produced both si-improve §6's "whoever records it runs the
  check and the rotation on the spot" and the separation between that skill and this one.
- An always-loaded doc of **34 KB** was being loaded every session until it was reorganized into five
  path-scoped rules. That is why scope demotion is the first treatment to reach for. During the
  reorganization, documents citing the old locations were covered by **a single migration table**,
  which beats dozens of individual pointers.
- The entry condition once read "everything within budget → stop", while the description promised a
  dead-rule pass. The two contradicted each other: a rule for a deleted feature in a 100-line
  document could never reach §2. A cross-repo review (2026-09) caught it, and §1 now has two
  triggers, with the dead/duplicate one explicitly not gated on budget.
