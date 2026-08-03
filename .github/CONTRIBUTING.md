# Contributing to self-improvement

Thanks for considering a contribution. `self-improvement` is a Claude Code plugin — a set
of instructions a model reads, not an application that runs. There is no build step and no
runtime: everything here is Markdown plus two small JSON manifests. What that means in
practice is that **the text is the product**, and a sloppy sentence is a bug that ships to
every project that installs the plugin.

## Before you start

- Read [`README.md`](../README.md) for the layer model and the three principles, then read
  [`hooks/doctrine.md`](../hooks/doctrine.md). The doctrine is the contract — every skill in
  this repo is an elaboration of one of its six clauses.
- Check open issues and PRs first to avoid duplicate work.
- For anything non-trivial (a new skill, a change to the doctrine, a new layer in the
  routing model), open an issue to discuss the approach before writing.

**A note on language.** The doctrine, skills, and agent are written in Korean, because that
is the language the model is instructed in. Keep edits to those files in Korean so the
voice stays consistent. Documentation for humans (`README.md`, this file) is English-first,
with `README.ko.md` as the Korean mirror.

## Development setup

```bash
git clone https://github.com/sh5623/self-improvement
cd self-improvement
```

The fastest loop is to point Claude Code straight at your working copy — no install, no
marketplace, and edits are picked up on the next session:

```bash
claude --plugin-dir /path/to/your/local/self-improvement
```

To exercise the real install path instead:

```
/plugin marketplace add /path/to/your/local/self-improvement
/plugin install self-improvement@self-improvement
```

**Hooks only load at session start.** After editing `hooks/doctrine.md` or `hooks/hooks.json`,
restart the session — the running one still holds the old text.

## Testing your change

There is no automated suite yet. Two checks are expected on every PR.

**1. Manifest validation** — must pass clean:

```bash
claude plugin validate . --strict
```

**2. An application test.** This is the one that actually catches problems. Give a *fresh*
agent nothing but the changed skill text and a scenario **from a stack you did not have in
mind while writing** — if you edited with a backend case in your head, test it on a
frontend one. Ask it to produce the routing decision, the gate verdict, and the changelog
entry, and then to list every point where it had to invent something the text did not
specify. That last list is the deliverable: it is how the current wording was hardened, and
it is what you should paste into the PR.

Watch for two specific failures:

- The agent **routes a rule into prose that a linter or CI could enforce.** The layer model
  says tool config wins; if the text let prose win, the text is wrong.
- The agent **codifies a one-off.** The gate exists to reject gaps that recur nowhere else.
  If a one-off got through, the gate wording leaks.

If you add an automated check, wire it into this section in the same PR.

## Making changes

- **Skills** (`skills/*/SKILL.md`): the `description` states **triggering conditions only** —
  never a summary of the workflow. A description that summarizes the steps becomes a
  shortcut the agent follows *instead of* reading the skill body. Keep the `Do NOT load for:`
  clause accurate; it is what stops the three skills from firing over each other.
- **The doctrine** (`hooks/doctrine.md`): this is injected into **every session of every
  project** that installs the plugin. A line added here is paid for forever, by everyone.
  The bar is "true in every session, for every project" — anything narrower belongs in a
  skill. Adding a clause needs a justification in the PR body.
- **The agent** (`agents/convention-smith.md`): READ + DRAFT only. It must not gain `Write`
  or `Edit` — the caller applies the diff, which is what keeps parallel sessions from
  drifting shared rule files.
- **The plugin's own rules apply to its source.** When you write a rule here, follow the
  ones in `si-improve` §4: no unconditional assertions (state the conditions and exceptions),
  evidence when you *narrow* a rule's scope and not only when you widen it, and any cap or
  budget must be wired into the procedure step that executes it — never left in a header.
- **Docs**: `README.md` is canonical. `README.ko.md` must be updated in the **same PR**, not
  a follow-up; a mirror that lags is worse than no mirror.
- **Version**: bump `version` in `.claude-plugin/plugin.json` (semver) when behavior changes.
  Documentation-only changes do not need a bump.

## Commit / PR style

- Conventional prefixes (`feat:`, `fix:`, `docs:`, `chore:`) — follow `git log --oneline`
  for tone.
- Keep a PR to one concern. Don't bundle a doctrine change with a README rewrite.
- In the PR body, include the application-test output described above and say which stack
  you tested against.

## Reporting bugs / requesting features

Open an issue and include:

- Which skill or hook, and what you expected instead.
- Your Claude Code version and OS.
- **Whether the project already had a conventions system** before you ran `si-init` —
  behavior deliberately differs (it registers an existing system rather than overwriting it),
  and this is the most common source of "it didn't do what I expected".
- For a skill that misbehaved, the transcript excerpt showing the decision it made.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By participating you
agree to abide by it.
