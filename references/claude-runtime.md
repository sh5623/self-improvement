# Claude runtime boundary

Read this before using the Claude skills or convention-smith. These are Claude Code
instructions. The separate Codex package has its own entrypoints and doctrine.

- Claude-owned wiring goes in CLAUDE.md or an existing .claude/CLAUDE.md, not AGENTS.md.
  New installs do not create an AGENTS.md import. Preserve intentional legacy imports and
  symlinks; do not follow a symlink to inject Claude commands into a Codex instruction file.
  With a symlinked root CLAUDE.md, use a separate .claude/CLAUDE.md when safe, or report the
  ownership conflict and propose a minimal separation.
- Codex owns AGENTS.md / AGENTS.override.md, nested AGENTS.md and .agents/skills. It does
  not load Claude paths-glob rules or @file imports as Codex instructions.
- Shared judgments live once in existing shared project docs. Claude paths-scoped rules
  may point to that canonical content. Runtime-specific entrypoints contain pointers and
  runtime conditions, not mirrored copies of the shared rule body.
- Read the Claude self-improvement declaration first. An existing AGENTS declaration can
  supply data/protocol/archive paths and its format map; do not adopt Codex tool commands.
  Reuse that real data file. Never create one changelog per runtime.
- Treat English and Korean section names and both Format:/형식: declarations as equivalent
  labels, using actual headings. Missing tables remain valid via the format map.
- si-plugin stamps are Claude template metadata; si-codex-template stamps are Codex
  metadata; si-schema: v1 identifies the neutral data layout. Preserve stamps you do not
  own. Public/internal release numbers are not a shared migration counter. A newer stamp,
  a different edition, or an unknown schema requires inspection rather than a downgrade.
- Before modifying a shared record, reread the current section. An additive edit/new file
  does not by itself prevent concurrent edits from being lost.

For si-init, always verify the active runtime's pointer even when data already exists.
Retain a legacy working shared pointer; add only missing Claude-specific wiring. Do not
rewrite project-owned history or force missing tables into registered systems.
