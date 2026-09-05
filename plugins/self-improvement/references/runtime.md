# Runtime boundaries

Read this before choosing a convention's destination. The active runtime is Codex.

| Content | Canonical home | Loading |
| --- | --- | --- |
| Enforceable invariant | Existing lint/type/test/CI configuration | Tool execution |
| Shared domain or workflow judgment | Existing shared docs, usually docs/conventions/ | Explicit Read by either runtime |
| Codex instruction for a directory | That directory's AGENTS.md, or its existing AGENTS.override.md | Codex instruction chain |
| Codex instruction for every task | Project-root AGENTS.md, or existing AGENTS.override.md | Codex instruction chain |
| Claude-only instruction | CLAUDE.md / .claude/CLAUDE.md / .claude/rules/ | Claude loading rules |
| Reusable Codex workflow | .agents/skills/<name>/SKILL.md | Skill discovery |
| Records and migration history | The single registered data file and archive | Explicit Read |

AGENTS.override.md takes precedence over AGENTS.md in the same directory. Instructions in
nested AGENTS files have directory scope; they are not Claude paths-glob rules. Codex does
not implement Claude's `@file` import syntax. Read a linked shared document explicitly.
Never translate a glob like `**/*.test.ts` into a claim that a directory AGENTS file matches
only tests: put the conditional in the instruction or in a task skill.

Do not copy CLAUDE.md, Claude tool names, or `.claude/rules` into AGENTS.md. A legacy
CLAUDE.md → AGENTS.md import/symlink may intentionally exist: preserve it and keep new
Codex sections explicitly conditional on "When running in Codex". Do not create a new
import or change the legacy relationship merely to install this plugin.

For a shared rule, keep its substantive text in one shared document. Runtime entry
documents contain pointers, not mirrored rule bodies. An existing project may deliberately
use AGENTS.md as shared truth; retain that choice and scope only runtime-specific additions.
If Claude-only source text is the only existing rule, propose extracting its shared part
with both consumers wired before removing anything. Do not silently move the rule to a
Codex-only destination and claim propagation to Claude.

One data file serves both runtimes. The data file's format map and project budgets win over
plugin defaults. Public and internal editions are alternative distributions: install one
Codex edition per environment, not both (the skill names are intentionally identical).

The Claude `si-plugin` stamp and Codex `si-codex-template` stamp have separate ownership.
Neither is a schema version or comparable across public/internal release sequences.
`si-schema: v1` identifies the neutral generated data layout. Never downgrade or replace
another runtime's stamp. A different/newer schema requires inspection, not regeneration.

Codex skills do not authorize committing, pushing, publishing, changing credentials, or
editing unrelated global configuration. Continue under the user's existing authorization.
State concrete environmental blockers; do not add redundant confirmation steps.
