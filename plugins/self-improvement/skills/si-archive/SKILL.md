---
name: si-archive
description: Demote, merge, or archive over-budget convention docs and specifically identified dead or duplicate rules in Codex. Use for log rotation or named cleanup even below budget; exclude new convention repair and initial setup.
---

# Archive conventions in Codex

Read [runtime boundaries](../../references/runtime.md) and
[data resolution and format maps](../../references/data.md).
Resolve actual paths before measuring; missing data is not a zero count.

## Two independent entry conditions

- A: a document or log exceeds its project budget. Measure only the routed documents;
  without a routing map, measure the effective instruction doc and actual log and report
  other layers as unmeasured. Count the real record unit, not headings in examples.
- B: the caller or repair protocol names a dead/duplicate clause. Inspect that clause even
  when every document is below budget. This does not authorize unrelated cleanup.

Neither: finish with no cleanup needed.

## Classify and move

For each triggered clause: demote to a narrower runtime-compatible home / merge into an
existing canonical rule / archive a dead rule / keep a universally applicable rule.
Support dead or exclusion judgments with actual references, removed targets, or replacing
tool rules. Do not archive a rule solely because Codex does not consume a Claude file.

Preserve the original text, date and reason at the destination before removing source text.
Shared rules remain in shared docs; Codex-only demotion uses an applicable directory AGENTS
file or explicit task document. Do not create Claude `paths:` files as Codex instructions.
Update the actual migration table or registered equivalent. If no equivalent exists,
propose a record in the existing system's format before moving; inventing a table name
does not create a migration record.

If `archive: none`, propose the archive and moves, report overflow, and preserve source
clauses and logs. Do not perform destructive half-migrations.

## Rotate and verify

For a configured archive and an over-cap log, move only the oldest overflowing work blocks
to the top of the archive log. Keep the complete index and migration history in the head.
Use the format map's real record unit and budget; default generated layout caps at 15.

Reread shared files before applying edits. Check citations of moved rule names/sections;
repair references or confirm the migration record resolves them. Remeasure affected files,
report any remaining excess or unmeasured layer, and distinguish completed moves from
proposals.

Report A / B / both, demoted/merged/dead counts, rotated body count, actual destinations and
verification. Use $self-improvement:si-improve if the cleanup exposed another recurring convention gap.
