---
name: si-improve
description: >-
  Use when a convention, document, or procedure was missing, wrong, or ambiguous and it cost you
  time during the work, and that gap looks likely to recur in other files, features, or tasks.
  Also use when the end-of-work check ("of what bit me, what will recur?") surfaces a gap, and on
  requests like "self-improvement", "fix the convention", "we have a convention gap". Do NOT load
  for: one-off mistakes, fixing the code bug itself, trimming bloated convention docs (si-archive
  owns that), or first-time setup in a project without the system (si-init owns that).
---

# si-improve — the self-improvement protocol: detect → classify → verify → codify → propagate → record

Read [Claude runtime boundaries](../../references/claude-runtime.md) before this procedure.

## Principles

- **Conventions are not frozen.** Do not route around the spot that bit you — fix the convention,
  on your own, inside the same unit of work.
- Editing convention docs needs no user approval. Commits follow the project's git rules.
- This procedure does not know your domain — it is identical in frontend, backend, scripting, and
  documentation projects. The examples below are examples, not part of the procedure.

## 0. Find the data file

The first of these that matches is the data file:

1. **The path declared in the self-improvement section of the always-loaded doc** (`CLAUDE.md` / `.claude/CLAUDE.md`; legacy AGENTS pointers supply data only) — if present, that declaration is authoritative (si-init §4 wires it; for projects
   with a pre-existing system registered, it is the only channel that carries it forward).
2. `docs/conventions/CHANGELOG.md`.
3. Fallback grep:
   `grep -ril "CONVENTIONS-CHANGELOG\|self-improvement\|자가개선" --include="*.md" docs .claude . 2>/dev/null | grep -v node_modules | head`
   — with several candidates, pick **the file that has an §index table**, and exclude any file with
   `archive`/`ARCHIVE` in its name or path (writing there stacks new blocks on top of old logs).
   READMEs and protocol descriptions are not data files. (The pattern includes the legacy Korean
   term on purpose — installations predating v0.5.0 wrote it into their always-loaded docs.)
4. All of them fail → **STOP: run `/self-improvement:si-init` first** (if a similar system exists,
   init registers and wires it).

**Substitute these two values into every command below** — typing the default paths verbatim reads
files that do not exist in a project with a registered pre-existing system (a grep against a missing
file returns 0 hits and passes silently → a duplicate convention lands, and the rotation check
measures nothing):

- `<datafile>` = the file you found above.
- `<archive>` = the archive path from declaration 1 if it names one, otherwise `archive/` in the
  directory holding `<datafile>` (created on the first rotation).
- **The format map** (registered systems only — the `Format:` line of declaration 1, written by
  si-init §4). A generated data file has this plugin's shape and needs no map. A registered system
  may lack every table, and si-init forbids grafting them on, so each step below that names a
  §index, §routing table, `### ` block, or §migration table uses the stand-in the map names. A slot
  that says `none` — or a registered system with no map at all — means:
  - `index: none` → the duplication check in §3 is `grep -n "^#" <datafile>` over the headings plus
    the keyword grep, and the log heading doubles as the index line (keep it ≤120 chars).
  - `routing: none` → route by §4's default layer order and write the actual home into the log
    entry; propose the table once (si-init §1), do not add it.
  - a log unit other than `### ` blocks → record in §6 in the file's own unit, keeping the five
    fields as content; the `grep -c '^### '` rotation check applies only to `### ` blocks, so count
    by the map's unit or leave the count to si-archive.
  - `archive: none` → nothing rotates; an over-cap log is reported, not moved.

## 1. Detect — is it worth codifying? (the gate)

Codify only when **both** are true:

- **Generality**: you can **name two or more** recurrence sites (files, features, tasks). If you
  cannot → record it in that task's local doc (spec, module README) and stop. If no local doc exists
  yet, create one **following the documentation pattern already used next to that target** — do not
  invent a new one.
- **Evidence**: at least one of a measurement, an execution log, a source `file:line`, or a
  reproduction. Without it → verify first, or park it as `needs verification`. **Never codify a guess.**

| Codify (global) | Local (that task's doc only) |
|---|---|
| "Judge external API performance with a cache key that has never been used" — recurs in every integration | "This list defaults to sort by created-at desc" — this feature's policy |
| "A test losing its handle and switching to a workaround path is a defect signal" — recurs in every refactor | "This batch job is pinned to 04:00" — this job's quirk |

## 2. Classify — the type of gap

New / **correction** of an existing rule / **clarification** of an existing rule (narrowing scope,
adding a conditional) / **removal of a dead rule** (→ follow the si-archive procedure) / **a
repeatable analysis or verification task** (→ create `.claude/agents/<name>.md`; note in the record
that a new agent is recognized from the next session onward).

**Classify the failure type as well** — it decides the sentence form in §4. The form that works on
one type measurably backfires on another.

| Failure type | What happened |
|---|---|
| Discipline violation | They knew the rule and skipped it under pressure (time, sunk cost, authority) |
| Wrong output shape | The rule was followed but the output came out wrong — bloated, out of order, the point buried |
| Missing element | One slot was left out of something they already produce |
| Should be conditional | Behavior should depend on the situation but is frozen into one branch |

## 3. Verify — prove it before you write it

- **Duplication**: skim **the §index only** (never read the whole file — the index covers the entire
  history; in a registered system without one, skim the stand-in the format map names — §0). Then
  grep keywords across head and archive together:
  `grep -n "<keyword>" <datafile> <archive>/*.md 2>/dev/null` (substituted per §0 — confirm the file
  exists with `ls <datafile>` first, so "0 hits because the file is missing" is distinguishable from
  a real 0). Already there → reclassify as a reinforcement or clarification, or stop.
- **Contradiction**: grep the neighbouring rules in each home listed in the routing table. On a
  conflict, **do not add a new rule** — reconcile both in a single edit.
- **Tools first**: if a linter, formatter, type checker, test, or CI can enforce it, it goes in
  **tool config**, not a document (frontend: biome/eslint, tsc; backend: checkstyle/ktlint/ruff/mypy/
  ArchUnit; either: a CI gate). Document conventions carry only the judgment a tool cannot make. When
  enforceability is uncertain, decide it with **one draft-rule proof of concept** — if it detects the
  existing violations, the tool layer is confirmed; if it cannot be expressed, drop to the next layer
  and note `tool-enforcement candidate` alongside. If a tool catches part of it, the caught part goes
  to the tool and only the remaining judgment to the document (never state the same thing twice).
- **Frozen gate**: if the project declared that value or artifact frozen, do not codify — escalate
  (report only).
- **Two traps in evidence** (both observed):
  - **Warming and cache bias** — a number that improved across repeated runs is a lower bound, not
    the truth. Judge performance and "it's fixed" from the first, cold run, and record *when you
    measured and which run it was* alongside the number. Apply the same to the other side's "we
    fixed it" reply.
  - **Declared ≠ applied** — presence in a spec, document, or config does not mean it runs. One real
    measurement can flip the verdict (check the real thing once before wiring).

## 4. Codify — minimally, in the right home, in a verifiable sentence

For a judgment used by both runtimes, keep the rule body once in a shared project doc;
Claude scope files point to it. The following Claude instruction destinations apply to
Claude-only content. Do not modify Codex-owned instructions while applying this adapter.

Landing priority — **the first layer from the top that fits** (each project's actual locations are
owned by the §routing table in the data file; using a home not in the table means updating the table
too. A registered system whose format map says `routing: none` uses this default order as-is and
names the actual home in the log entry — §0):

1. **Tool config** (decided in §3)
2. **Path-scoped rule** — `.claude/rules/<topic>.md` with `paths:` frontmatter (loads only when a
   matching file is touched). No fitting scope → **a new file** (a new file means no parallel-edit
   conflict)
3. **Task or domain doc** — the document someone reads while running that procedure (playbook, spec,
   README)
4. **Claude always-loaded doc** (`CLAUDE.md` / `.claude/CLAUDE.md`) — only when the answer to "is this true in every
   session, for every file?" is yes. Over budget → run si-archive first

Make **the smallest edit**, matching the target file's voice and language, and prefer an **addition**
(a new bullet, a new section) to avoid parallel conflicts.

**Match the form to the failure type from §2:**

| Failure type | Form to use | Form to avoid |
|---|---|---|
| Discipline violation | Prohibition + rationalization table + red-flag list | "prefer", "where possible", "consider" |
| Wrong output shape | **A recipe** — what the output consists of, in what order | Prohibitions ("do not …") |
| Missing element | A **required slot** in the template or checklist | Prose warnings next to the template |
| Should be conditional | A conditional on an observable predicate ("if X, then Y") | An unconditional rule plus exemption clauses |

**Four sentence-quality rules** (all of them came out of real incidents):

- **No unconditional assertions in a detection or judgment rule** — state the conditions and
  exceptions. (An assertion that "the total is always 100" produced false positives on 13 valid
  cases → it was rewritten split in two: "exceeding is always a defect / matching only when every
  item is stated". Grep for one counter-example before writing the rule.)
- **Never put an exception clause inside an instruction sentence** — "do X, except when Y" opens a
  negotiation that disarms the rule (in wording tests a single appended exception clause dropped
  consistent compliance to erratic). Limit applicability **structurally** (the `paths:` of a
  path-scoped rule, the choice of landing document), and write a genuine exception as **a separate
  conditional line**. Exemption clauses do not scope — if part of an output must be exempt, change
  the layout so the rule cannot reach it.
- **Narrowing scope also needs evidence** — "this only applies to our case" is itself a judgment
  that needs a measurement (grep to confirm the other places really are unaffected). Narrowing
  wrongly has caused a real incident.
- **Wire a rule into the procedure step that executes it** — caps and obligations written only in a
  header or preamble are triggered by nobody (a cap that lived only in a header let a log grow to 42
  blocks and 949 lines). When you write a rule, insert "when and by whom is this run" into the
  matching step of that procedure document.

**Effectiveness check before finalizing — does the wording change behavior?** (Do this **before**
§5 propagation — if the check changes the sentence, propagation has to be redone. §3's "declared ≠
applied" applies to convention sentences too.)

- **Always**: re-judge this incident's violations with the new sentence — every violation must be
  caught and the valid cases must not be. If even one case comes out ambiguous, fix the sentence
  before finalizing.
- **For an expensive or contested convention**: 3+ subagent runs of the same scenario, plus **one
  control run with no convention**. If the control does not reproduce the failure, the convention is
  unnecessary — do not write it. If the three outputs disagree in shape, the wording is not binding
  — change the form before adding words (see the form matching above).

## 5. Propagate — fixing only the rule leaves the existing artifacts stale

- **Grep for existing violations of the new or corrected rule** — if you can fix and verify them
  inside this unit of work, do so; otherwise report "N not retrofitted + the list" explicitly (no
  silent neglect — the criterion is not the count, it is whether verification fits in this unit).
- If you changed a template, generator, or scaffold, derivatives do not update themselves —
  propagate with an **idempotent (marker-guarded) script** and compare the edit count against what
  you expected.
- If the project has checklists, definitions of done, or gates, **wire the new rule into those too**
  (the pass verdict comes from the checklist, not from prose).

## 6. Record — one log block per unit of work + one index line per improvement + a check

- At the **top** of §log (newest first), **one block per unit of work**: `### YYYY-MM-DD — title`
  plus **Trigger** (what bit you) / **Change** / **Where** / **Verification** / **Commit·PR**. Several
  improvements from the same unit of work become items inside that one block. With no commit yet,
  write `uncommitted (working tree)` in the commit field (no obligation to backfill the hash — git
  owns history). In a registered system, write the block in **the file's own record unit** (the
  format map's `log unit`, §0) — the five fields are the content, the heading shape is the file's.
- The block body carries **what is not in the landing document** (trigger, evidence, how it came
  about, verification) — the convention sentence itself is owned by the landing document. "It is
  already in the landing doc" is not a reason to skip the body (a real case left the index growing
  with zero bodies).
- §index gets **one line per improvement** (**newest first here too**):
  `| date | what bit you (≤120 chars, one line — evidence and background belong in the body) | landed |`.
  If the data file's header still declares an older format ("1 improvement = 1 index line + 1 log
  block"), update that line as well — repairing plugin version drift in general belongs to a re-run
  of `/self-improvement:si-init`.
- **Check it on the spot**: `grep -c '^### ' <datafile>` — over 15, run the rotation in
  `/self-improvement:si-archive` immediately (index and migration table stay in the head; only
  bodies move). That count is meaningful only for `### ` blocks; with another log unit, count by
  the format map's unit, and with `archive: none` report the overflow instead of moving it (§0).

## Reporting (required at the end of a unit of work)

One line in the final report: **"self-improvement: N items + where"** or **"self-improvement: none"**.
A report without that line skipped the check. (A project that has declared its own marker string
keeps it — the requirement is the line, not the language.)
N counts **only codifications** (tool config or global docs) — items that failed the gate and were
handled locally are not counted (mention them in parentheses if useful).

## When not to — red flags

| Signal | Action |
|---|---|
| Cannot name the recurrence sites | Do not globalize — local doc |
| Writing "probably" or "it should be" | Verify first, or mark `needs verification` |
| Already in the §index | Do not add — reinforce, or stop |
| Conflicts with an existing rule | Do not add — reconcile in one edit |
| A value or artifact declared frozen | Escalate only |
| The landing document is over budget | Run si-archive first |
| About to append "except when …" to an instruction | Scope structurally; write the exception as a separate conditional |
| About to finalize without checking the wording | Re-judge the violations first (§4 effectiveness check) |

When the routing, the draft, or the gate verdict is unclear, **delegate to the `convention-smith`
agent** (READ+DRAFT — you get a draft back and this session applies it).

## Meta

This protocol, the routing table, and this plugin are themselves subject to self-improvement. Feed
plugin defects back into the marketplace repo through the same loop and bump `version` in
`plugin.json`.
