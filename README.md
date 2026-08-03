# self-improvement — conventions that fix themselves

<div align="right">
  <a href="README.ko.md"><img src="https://img.shields.io/badge/lang-한국어-lightgrey?style=flat-square" alt="한국어"/></a>
  <a href="README.md"><img src="https://img.shields.io/badge/lang-English-blue?style=flat-square" alt="English"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT License"/></a>
</div>

A Claude Code plugin that turns "I just got bitten by a missing or wrong convention" into a fix of **the convention itself**, inside the same unit of work — instead of a workaround that only helps the file you happened to be in.

It is stack-agnostic. Frontend, backend, scripts, docs — the loop knows nothing about your domain, and the shape of your project's documentation is detected at setup time rather than assumed.

> **Language note.** The doctrine, skills, and agent are written in **Korean**, because that is the language the model is instructed in. Claude reads and follows them regardless of the language you write in, and this README documents everything they do — but if you plan to *edit* the rules, expect Korean source text.

Three principles:

1. **Conventions are not frozen.** The session that hits the gap fixes it, in the same unit of work, without waiting to be asked.
2. **No evidence, no rule.** A gap is codified only if it is *general* (you can name two or more places it recurs) **and** *evidenced* (a measurement, a log, a `file:line`). Otherwise it stays local, or it waits for verification.
3. **Documents have a budget.** Rules go in the narrowest scope that covers them, and when a document overflows, the overflow is demoted or archived. A rule doc that grows forever is a rule doc nobody reads.

## Install

```
/plugin marketplace add sh5623/self-improvement
/plugin install self-improvement@self-improvement
/reload-plugins
```

Installs at **user scope** by default, so it applies to every session in every project. Use `--scope project` to limit it to one repo, or drop it from that project's `.claude/settings.json` → `enabledPlugins` to turn it off. Update with `/plugin marketplace update self-improvement` → `/reload-plugins`.

![How a convention gap is gated and routed into the narrowest layer that fits](docs/assets/loop.svg)

## What it looks like

You don't invoke anything. You are working on something else, and the session stops to fix the rule on its way out:

```
$ claude
> the transferStock partial-commit bug — please fix it

  ✔ src/orders/OrderService.java:88 — the second repository write was running
    outside the transaction boundary.

  Before finishing — does this recur anywhere else?
    · PaymentService.java:141, SettlementService.java:52 — same shape (grep)
    · evidence: production log + file:line          → gate passed
    · a linter can enforce this, so it is not prose → tool config layer

  + src/test/java/arch/TransactionBoundaryTest.java   ArchUnit rule
  + docs/conventions/CHANGELOG.md                     index row + log block

자가개선: 1건 — ArchUnit rule (tool config layer) + changelog
```

That last line — *self-improvement: 1 item* — is the observable signal. It is a literal Korean marker specified by the doctrine, so you will see it verbatim whatever language you work in. **If it is missing, the end-of-work check was skipped**, and you can ask for it.

## What you get

| Component | Role |
|---|---|
| **SessionStart hook** (`hooks/doctrine.md`) | Injects a 6-clause doctrine into **every session** — fix the rule, not just your file · the evidence gate · the end-of-work self-check · the reporting duty. It is re-injected after a compaction, so long sessions don't lose it. |
| `/self-improvement:si-improve` | The protocol itself: detect → classify → verify → codify → propagate → record. |
| `/self-improvement:si-init` | Per-project bootstrap (idempotent): detect the documentation landscape → create the data file → wire a 3-line pointer into the always-loaded doc. |
| `/self-improvement:si-archive` | Bloat and dead-rule migration: measure against budgets → demote / merge / retire → migration table → changelog rotation. |
| `convention-smith` agent | Delegate here when routing or drafting is unclear. READ + DRAFT only — it returns a gate verdict and a minimal diff; the caller applies it. |

**Tool vs. data.** The plugin is the versioned *tool*. What lands in your project is **one data file** (`docs/conventions/CHANGELOG.md` — routing table, budgets, migration table, index, log) plus three lines of pointer. Updating the plugin never touches the history your project has accumulated.

## How it works

### Rules live in layers, and only move downward

A new rule goes into **the first layer from the top that fits** (`si-improve` §4). When a layer overflows or a rule dies, it moves **down only** (`si-archive`).

| Layer | When it loads | Notes |
|---|---|---|
| Tool config (lint · format · types · tests · CI) | Enforced automatically | If a tool can catch it, **it must not be prose**. Prose rules carry judgment calls only. |
| Path-scoped rules (`.claude/rules/*.md` with `paths:`) | Only when a matching file is touched | The default home. A new file means zero conflicts for parallel work. |
| Task / domain docs (`docs/**`) | Read explicitly when doing that task | Playbooks, specs. |
| Always-loaded doc (`AGENTS.md` / `CLAUDE.md`) | Every session | **≤200 lines.** Only what is true in every session, for every file. |
| Archive (`docs/conventions/archive/`) | Never loaded | Retired rules and rotated log entries. Preserved, not deleted — so "deliberately removed" stays distinguishable from "lost". |

### Three devices keep it from bloating

- **Log rotation** — the changelog holds at most 15 body blocks. Whoever records an entry checks it on the spot (`grep -c '^### '`) and rotates the overflow into the archive. The index and migration tables stay in the head file for the full history, which is what makes duplicate-checking a single-file scan.
- **Migration table** — one row per demotion or retirement. Old citations resolve through that one table instead of scattering pointers across the documents they left.
- **Caps are wired into the procedure that executes them** — never only into a document header. This one is not theoretical: a cap that lived only in a file header went untriggered until that log had grown to 42 blocks and 949 lines.

## Quick start

```
# 1) Once per project. If a similar system already exists, it registers that one and stops —
#    it does not overwrite what you already have.
/self-improvement:si-init

# 2) When a convention bites you (or when the doctrine makes the session do it unprompted)
/self-improvement:si-improve  <what bit you + the evidence>

# 3) When the rule docs have grown
/self-improvement:si-archive
```

From then on, every work report should end with **`자가개선: N건 + 위치`** (N improvements + where) or **`자가개선: 해당 없음`** (none applicable). That line is the signal that the loop ran.

> **What is and isn't guaranteed.** The hook injection is deterministic — the doctrine is in context, every session. What follows is instruction-following, not enforcement: nothing blocks a session that ignores it. That is exactly why the reporting line exists. If the line is missing, the end-of-work self-check was skipped, and you can ask for it.

## Where it came from

This is not a design exercise. It generalizes rules that were paid for on a real project (a legacy migration plus API integration work, with roughly forty logged convention changes). Each row below is an actual incident and the rule it produced.

| What went wrong | The rule it produced |
|---|---|
| Convention repair was treated as a separate task the user had to request, so most of it was never done | Self-initiated + a reporting duty — a report without that line means the self-check was skipped |
| A size cap existed only in a file header, so nothing ever triggered it; the log reached 42 blocks / 949 lines | A rule must be wired into the procedure step that executes it |
| An unconditional assertion ("the total is always 100") flagged 13 correct cases as defects | No unconditional assertions — state the conditions and exceptions, and grep for counterexamples before writing the rule |
| Narrowing a rule's scope to "our case only" missed a counterexample in another area | Narrowing a scope needs evidence too, not just widening it |
| A performance verdict read off a warmed cache was published, then retracted the same day | Measure cold; a warmed number is a floor, not the truth — and apply the same standard to "we fixed it" from the other side |
| An always-loaded rule doc reached 34 KB and was paid for on every single session | The layer model, scope demotion, and the migration table |

## Prerequisites

Claude Code. That is the whole list — there is no build step, no runtime, and no dependency to install. The plugin is Markdown plus two JSON manifests, and the one data file it creates in your project is Markdown too.

## This plugin is subject to its own loop

If a skill, the doctrine, or the agent falls short, it gets fixed the same way — edit this repo and bump `version` in `.claude-plugin/plugin.json`. The meta-conventions aren't frozen either.

Issues and PRs welcome — see [CONTRIBUTING](.github/CONTRIBUTING.md) for how changes here are tested, and [CODE_OF_CONDUCT](.github/CODE_OF_CONDUCT.md).

## License

[MIT](LICENSE) © 2026 Seungho
