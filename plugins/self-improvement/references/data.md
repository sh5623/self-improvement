# Resolve the project data once

1. Read the self-improvement declaration in the effective Codex instruction document
   (AGENTS.override.md before AGENTS.md). A declared real path is authoritative.
2. If no Codex declaration exists, inspect a legacy declaration in CLAUDE.md or
   .claude/CLAUDE.md only to recover data/protocol/archive paths and its format map.
   This is data discovery, not adoption of Claude instructions.
3. Check docs/conventions/CHANGELOG.md.
4. Search existing project docs for CONVENTIONS-CHANGELOG, self-improvement, or 자가개선.
   Inspect candidates. Exclude archives, installed plugin/skill source, and explanatory
   READMEs with no actual convention records. Dated bullets or clauses are valid records;
   tables and stamps are not required. Multiple credible systems need a canonical choice.
5. No system: run $self-improvement:si-init within the authorized task before codifying.

Resolve `datafile`, `archive`, and the format map to real paths. Confirm file existence
before counting or searching: missing files are not evidence of zero duplicates.
Never substitute the plugin's default path after resolving a custom registration.

For generated layout v1, use §routing, §index, §migration table and §log. For a registered
system, use its declared map; a missing field means `none`, not an invented heading:

English/Korean labels are equivalent (for example §index/§색인, §routing/§라우팅,
§migration table/§이관표, §log/§로그, Format:/형식:). Use the actual heading and preserve
its language; do not rename existing sections just to match this package's template.

- index none: skim actual record headings/bullets plus keyword search; a short record title
  doubles as an index entry.
- routing none: apply runtime.md's layer order, record the actual destination, and propose
  a routing table only if useful; do not graft one onto the project.
- log unit not `### dated blocks`: use the file's own record unit. Count that unit, not all
  Markdown headings. Preserve the five record fields as content.
- archive none: report overflow and propose a destination; do not rotate or remove source
  clauses until the project has adopted an archive destination.
- migration table absent: use an existing equivalent record or propose a migration record
  in the system's own format; never write into an imagined table.

The log holds one block per unit of work, with N improvements grouped in it. Index entries
are one per codification, newest first. Record trigger/evidence, change, destination,
verification, and commit/PR (`uncommitted (working tree)` when appropriate). The canonical
rule owns the rule text; the log owns its rationale and evidence. Reusing a shared changelog
does not authorize mirroring the rule itself.

Default budgets: root instructions 200 lines, scoped instructions 150 lines each, task docs
400 lines suggested, log body 15 work blocks. Project values take precedence. Count only
actual log bodies with the fence-aware command below (also shipped as
`scripts/count_log_blocks.sh <datafile> [unit] [section]`, resolved relative to this package).
`unit` is the record regex the format map names (`^### ` for the generated layout, `^- ` for
dated bullets); `sec` matches the log section's `## ` heading (`''` counts a file with no `## `
headings). A fence is CommonMark's: up to 3 spaces of indentation, then 3 or more backticks or
tildes, closed only by the same character at the same length or longer with nothing but spaces
after. Headings inside a fence, a shorter or different inner fence, and headings in other
sections are not counted; plain `grep -c '^### '` over-counts all of those. Keep the index
and migration history in the head file when rotating oldest bodies.

````sh
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

Before writing a shared data file, reread the affected section to incorporate another
session's changes. A new file or additive edit does not eliminate concurrency conflicts.
