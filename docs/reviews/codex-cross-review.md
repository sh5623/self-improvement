# Codex compatibility — cross-review handoff

Date: 2026-09-05. Scope: public self-improvement v0.6.0 → v0.7.0.
Baseline: `f8a60b435183727dbdacbfd25b2d6aec73ca3061`.
Review the local `feat/codex-compat` branch against that baseline. This is a local implementation;
remote publication and fresh-model behavioral sign-off are separate steps.

## Implementation

- Added a separate Codex plugin under `plugins/self-improvement/`, registered by
  `.agents/plugins/marketplace.json` as `self-improvement@self-improvement-codex`.
- Kept the Claude plugin at the repository root. Its three skills and convention-smith now
  read `references/claude-runtime.md`. New Claude wiring uses CLAUDE.md/.claude/CLAUDE.md.
- Kept one canonical project history. Shared judgments live once in shared project documents;
  runtime-specific instructions, loading rules, skill calls and template stamps remain separate.
- Replaced Claude's new AGENTS import/copy flow with runtime-owned wiring. Deliberate existing
  imports and symlinks are preserved. Codex handles AGENTS.override.md precedence explicitly.
- Added a conservative Python init helper, read-only preview, missing/ambiguous-path refusal,
  format-map support, path containment checks and idempotent Codex marker replacement.
- Preserved the recent fixes: table-less existing systems remain usable and named dead rules
  enter si-archive even below budget. Codex draft assistance has no required named subagent.
- Updated both README languages, compatibility documentation and CI checks. The matching
  Claude/Codex manifest versions identify this edition's release, not a shared migration counter.

See [compatibility details and exact commands](../codex-compatibility.md).

## Executed checks

Environment: macOS 26.5.2 arm64, Python 3.14.6, PyYAML 6.0.3 in an isolated validation venv,
Codex CLI 0.153.4, Claude Code 2.1.261.

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s plugins/self-improvement/tests -v` | 35 tests passed |
| `validate_packages.py --repo .` | Both manifests/catalogs/hooks and 7 YAML frontmatter blocks passed |
| Codex plugin-creator `validate_plugin.py` | Passed |
| skill-creator `quick_validate.py` | All 6 skill directories passed |
| Claude strict validation, plugin and marketplace separately | Both passed |
| `check_runtime.py --repo .` | Actual Codex loader found 3 namespaced skills and 1 SessionStart hook |
| Hook command from a copied payload path containing spaces | Exact doctrine bytes returned without CLAUDE_PLUGIN_ROOT |
| `git diff --check` | Passed |

The fixture suite includes new setup, preview without writes, byte preservation for existing
Claude data, repeated setup, override precedence, live/dangling instruction symlinks, custom and
undated data formats, conflicting/missing declarations, malformed markers, archive exclusion,
`archive: none`, unknown schema preservation and a relocated installed payload.

The runtime loader resolved **self-improvement:si-init / si-improve / si-archive**, so the Codex
instructions use `$self-improvement:si-…`. Bare `$si-init` was corrected during implementation.
The hook is discovered through the default hooks file and uses the native `PLUGIN_ROOT`.

## What has not been measured

No plugin was installed into the user's live Codex configuration, no hook trust was auto-approved,
and no model turn was requested. Catalog reading and executing the audited shell command are not
an end-to-end install/trust/start/resume/compact test. CI's Linux/macOS Python 3.9/3.13 matrix is
configured, but hosted jobs have not been run as part of this local change.

The helper does not replace semantic terrain discovery, implement a lock/transaction across
shared files, or prove model compliance. An unusual project layout can require explicit
`--data-file` or the manual skill procedure. Its default archive for an existing system is `none`
until the real destination has been confirmed.

Existing README behavioral figures come from Claude, not a fresh Codex experiment. Run the
following model scenarios before a behavioral release; record actual outputs, not inferred passes.

## Cross-review scenarios

Use a disposable project. Compare the unmodified baseline with the changed adapter where relevant.
Read each skill's linked references as an installed agent would. Do not copy a SKILL.md alone.

| Scenario | Expected result |
| --- | --- |
| New empty project, Claude init then Codex init | One history; Claude pointer in CLAUDE.md, Codex pointer in effective AGENTS; no new import |
| New empty project, Codex init then Claude init | Same history reused; original log bytes/headings preserved except an explicit routing addition |
| Existing dated bullets with no index/routing table | Explicit real data path + format map; no grafted tables and no missing-heading grep |
| Existing CLAUDE.md → AGENTS.md symlink or import | Relationship preserved; no writing Claude commands through the symlink; runtime conditions retained |
| AGENTS.override.md plus AGENTS.md | Codex registration in override; base and nested instructions unchanged |
| One recurrence site, even with a strong stack trace | Local fix/record only; no general convention |
| Two recurrence sites and an enforceable lint invariant | Try the existing tool layer before adding prose |
| Wrong output shape | Recipe/template form; test incident and valid counterexample before propagation |
| Two new codifications in one task | Two index entries, one log body carrying five record fields |
| Log with 16 actual bodies and a fenced `###` example | Rotate the oldest actual body only; keep full index and migration history |
| Named obsolete clause in an under-budget document | Enter cleanup B; evidence, correct destination and migration record required |
| `archive: none` with overflow/dead rule | Propose destination/moves, preserve source text and log |
| Public/internal switch or a newer/unknown schema stamp | Reuse data; no numeric downgrade, heading rewrite or other-runtime stamp replacement |
| No subagent facility | Main session can follow Codex READ/DRAFT reference; no attempt to invoke a Claude-only agent |
| Real supported host installation | Skill picker, hook trust, new session and compact/resume behavior verified with actual context |

For behavioral wording, preserve the baseline evidence and run the changed case three times;
include a no-rule control where the protocol calls for it. Report file:line, reproduction,
expected/actual result and proposed minimal fix for each finding. Separate structural defects,
instruction ambiguity and unmeasured runtime behavior. Do not infer success from the test count.

## Reviewer entrypoints

- [Claude boundaries](../../references/claude-runtime.md)
- [Claude si-init](../../skills/si-init/SKILL.md)
- [Codex si-init](../../plugins/self-improvement/skills/si-init/SKILL.md)
- [Codex runtime ownership](../../plugins/self-improvement/references/runtime.md)
- [Codex repair protocol](../../plugins/self-improvement/references/protocol.md)
- [Codex archive procedure](../../plugins/self-improvement/skills/si-archive/SKILL.md)
- [Init helper](../../plugins/self-improvement/scripts/init_project.py)
- [Regression fixtures](../../plugins/self-improvement/tests/test_compat.py)
