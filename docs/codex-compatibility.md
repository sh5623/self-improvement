# Claude Code and Codex compatibility

Public v0.7.0 adds a separate Codex adapter. The Claude adapter stays at the repository root;
the Codex payload is `plugins/self-improvement/`. Install from the repository root as described
in [README](../README.md). This document covers the architecture and upgrade contract.

## What is shared

Each project has one canonical convention system: its existing changelog/protocol and archive,
or `docs/conventions/CHANGELOG.md` on a new project. Either runtime reads the same records,
format map, budgets, index and migration history. Shared rule bodies remain in existing shared
project documents. Pointers may repeat; substantive rule text should not.

The gate remains two concrete recurrence sites plus evidence; tool enforcement takes priority
over prose. Record one work block per unit of work and one index entry per codification. The
default cap is 15 actual work blocks, excluding fenced examples. Named dead-rule cleanup is
independent of document budget. A registered `archive: none` permits proposals, not rotation.

## What is separate

| Responsibility | Claude Code | Codex |
| --- | --- | --- |
| Manifest | `.claude-plugin/plugin.json` | `plugins/self-improvement/.codex-plugin/plugin.json` |
| Catalog | `.claude-plugin/marketplace.json` | `.agents/plugins/marketplace.json` |
| Three skills | `skills/si-*/SKILL.md` | `plugins/self-improvement/skills/si-*/SKILL.md` |
| Invocation | `/self-improvement:si-init` etc. | `$self-improvement:si-init` etc. |
| Doctrine | `hooks/doctrine.md` | `plugins/self-improvement/hooks/doctrine.md` |
| Draft assistance | `agents/convention-smith.md` | Bundled `references/convention-smith.md`; no required agent registration |
| Project instruction owner | CLAUDE.md / .claude/CLAUDE.md | Effective AGENTS.override.md / AGENTS.md |
| Scope | `.claude/rules` path patterns | Directory instruction chain, with explicit conditions for narrower applicability |
| Template metadata | `si-plugin` | `si-codex-template` |

Claude does not need to be installed to use the Codex payload. Do not install just a copied
SKILL.md: its references, scripts and hook live beside the skill directories in the full payload.

Codex reads the default `hooks/hooks.json`; its command uses the native `PLUGIN_ROOT` variable
and quotes the path. The hook requires runtime trust, separately from plugin installation. Check
`/hooks` after installation or changes. Unsupported hosts or skipped/untrusted hooks cannot
promise automatic doctrine injection; an explicit skill invocation remains a separate action.
[Codex hooks](https://developers.openai.com/codex/hooks),
[plugin packaging](https://developers.openai.com/codex/plugins).

Codex AGENTS.override.md wins over AGENTS.md in the same directory; nested instruction files
have directory scope. They do not implement Claude `paths:` globs or `@file` imports. A shared
document must be explicitly read. Preserve the project's existing custom fallback configuration;
the helper covers the standard AGENTS names only.
[Codex instruction discovery](https://developers.openai.com/codex/guides/agents-md).

## Initialize and migrate

1. Run the installed si-init in each runtime. It reads that runtime's declaration first, then
   legacy declarations for data locations. Existing table-less systems are valid and retain
   their own format. English/Korean headings are interpreted without renaming them.
2. New Claude wiring goes to a real CLAUDE.md or .claude/CLAUDE.md. New Codex wiring goes to
   the effective AGENTS document. New installs do not add imports or mirror whole documents.
3. Keep deliberate legacy imports/symlinks. Codex additions are conditional on running in Codex.
   A symlinked effective Codex anchor is refused by the helper: inspect ownership and make a
   minimal manual separation, never write through it into Claude-only instructions.
4. Reuse the existing data and archive paths. Fill the actual format map; missing sections
   mean `none`, not fabricated table names. A missing declared target needs repair before init.
5. Updates replace tools. Re-running init verifies wiring even when history already exists.
   Existing data is read-only to the Codex helper; the skill separately inspects stale wording.

Generated layouts identify schema `si-schema: v1`. Claude/Codex template stamps have different
owners. Only confirmed same-edition, same-runtime stale fixed wording can be repaired; retain
project values, headings, index, migration history, log bodies and other-runtime stamps. Unknown
schema, newer stamp, or an edition switch requires content inspection, never a numeric downgrade.

Public and internal editions use different release sequences and catalogs, but the same skill
names. Choose one edition per runtime. To switch, remove the old plugin, register the new
marketplace, install its plugin, start a new session, review hook trust, and rerun si-init against
the existing data. Do not delete project history or recreate it to match a release number.

## Init helper boundaries

The installed Codex si-init resolves `../../scripts/init_project.py` relative to its SKILL.md.
From this repository, a preview is:

```sh
python3 plugins/self-improvement/scripts/init_project.py --project "/path/to/project" --check
```

Remove `--check` after inspecting the result to apply it. For a confirmed custom system, add
`--data-file "docs/actual-log.md" --archive "docs/actual-archive"` (or `--archive none`). All
paths are project-relative. Explicit selection is required when discovery is ambiguous. Undated
clause lists or other nonstandard documents need semantic inspection by the skill; the helper
does not claim to recognize every format. If nothing is canonical, the skill can create the
new file manually after inspection, then register it with `--data-file`.

The helper preserves existing data bytes, updates only its marked Codex section, handles spaces,
checks path containment, respects existing override files, preserves instruction mode, and checks
for a changed instruction file before replacement. It does not inspect tool configuration, populate
the full routing terrain, evaluate rule quality, or run a cross-file transaction/lock. Complete
terrain discovery through the skill. Concurrent sessions must coordinate shared record edits and
reread before writing. Do not run competing initializations in the same project.

Python 3.9+ is required only for the helper and tests. The skill documents manual initialization
when Python is unavailable. Normal usage has no PyYAML dependency.

## Validation

From the repository root:

```sh
python3 -m unittest discover -s plugins/self-improvement/tests -v
python3 -m venv /tmp/si-validation-env
/tmp/si-validation-env/bin/pip install PyYAML==6.0.3
/tmp/si-validation-env/bin/python plugins/self-improvement/scripts/validate_packages.py --repo .
claude plugin validate .claude-plugin/plugin.json --strict
claude plugin validate .claude-plugin/marketplace.json --strict
python3 plugins/self-improvement/scripts/check_runtime.py --repo .
```

The last command uses the installed Codex app-server's read-only `plugin/read` API. It checks
catalog resolution, the three namespaced skill names and SessionStart discovery without
installing the plugin, changing user trust, sending a model turn, or publishing anything.

Local validation used Codex CLI 0.153.4, Claude Code 2.1.261 and macOS. Automated fixtures cover
data preservation, fresh setup, reruns, custom formats, ambiguous/missing paths, symlinks,
override precedence, relocatable payloads, shell quoting and the fence-aware log count (indented fences, a different or shorter inner fence, headings outside the log section, and the documented copies matching `scripts/count_log_blocks.sh`). CI additionally configures these checks
on Linux/macOS with Python 3.9/3.13; configured coverage is not a claim those hosted jobs ran.

These are structural and deterministic checks. End-to-end install/trust/compact behavior in the
target host, and a fresh model's gate/routing/archive decisions, still need the cross-review
scenarios in [the review report](reviews/codex-cross-review.md). Historical Claude measurements
in the README are not Codex behavioral measurements.
