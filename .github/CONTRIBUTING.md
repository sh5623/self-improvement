# Contributing to self-improvement

Thanks for considering a contribution. `self-improvement` is a Claude Code plugin — a set
of instructions a model reads, not an application that runs. There is no build step and no
runtime: everything here is Markdown plus three small JSON files (two manifests and one hook config). What that means in
practice is that **the text is the product**, and a sloppy sentence is a bug that ships to
every project that installs the plugin.

## Before you start

- Read [`README.md`](../README.md) for the layer model and the three principles, then read
  [`hooks/doctrine.md`](../hooks/doctrine.md). The doctrine is the contract — every skill in
  this repo is an elaboration of one of its six clauses.
- Check open issues and PRs first to avoid duplicate work.
- For anything non-trivial (a new skill, a change to the doctrine, a new layer in the
  routing model), open an issue to discuss the approach before writing.

**A note on language.** English is canonical everywhere: the doctrine, the skills, the
agent, and `README.md`. `README.ko.md` is a mirror that points back at the English. Keep
edits in English, and do not create a second copy of anything in another language, because
two copies drift and the drift is silent. The one deliberate exception is the legacy Korean
term inside the data-file detection greps, which is there so installations predating v0.5.0
are still found rather than duplicated.

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

Three checks are expected on every PR. The first runs in CI (`.github/workflows/validate.yml`,
on every push and pull request); the other two are yours to run and paste.

**1. Manifest validation and frontmatter parse** — must pass clean:

```bash
claude plugin validate . --strict
for f in skills/*/SKILL.md agents/*.md; do
  ruby -ryaml -e 'YAML.safe_load(File.read(ARGV[0])[/\A---\n(.*?)\n---\n/m,1]) && puts "ok #{ARGV[0]}"' "$f"
done
```

The frontmatter parse exists because a sibling plugin shipped a `description:` containing an
unquoted `word:` — invalid YAML that Claude Code tolerates by loading the body with empty metadata,
which silently removes the description that triggers the skill. Keep multi-sentence descriptions in
a `>-` block scalar, as every skill here already does.

**2. An application test.** This is the one that actually catches problems. Give a *fresh*
agent nothing but the changed skill text and a scenario **from a stack you did not have in
mind while writing** — if you edited with a backend case in your head, test it on a
frontend one. Ask it to produce the routing decision, the gate verdict, and the changelog
entry, and then to list every point where it had to invent something the text did not
specify. That last list is the deliverable: it is how the current wording was hardened, and
it is what you should paste into the PR.

Watch for three specific failures:

- The agent **routes a rule into prose that a linter or CI could enforce.** The layer model
  says tool config wins; if the text let prose win, the text is wrong.
- The agent **codifies a one-off.** The gate exists to reject gaps that recur nowhere else.
  If a one-off got through, the gate wording leaks.
- The agent **picks a form that fights the failure** — a prohibition where the output had the
  wrong shape, or an inline "unless…" clause that reopens the rule for negotiation. §4 has a
  table for this; if the agent skipped it, the wording did not make the choice load-bearing.

**3. A baseline, when you change rule wording.** Adding a rule or rewording an existing one
needs the run *before* the change, not only after. Give a fresh agent the **unchanged** text
and the same scenario first. If the baseline does not reproduce the failure you are fixing,
stop — there is nothing to fix, and the rule you were about to add would cost budget for
nothing. Two candidate rules were dropped exactly this way (see the README). Then run the
changed text **three times** and read all three outputs: they should land on the same shape.
Three different interpretations means the wording is not binding yet, and the fix is a
different form rather than more words.

If you add an automated check, wire it into this section **and** into the workflow in the same PR.

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
  ones in `si-improve` §4: match the form to the failure type you classified in §2 (a
  prohibition aimed at a wrong-shape failure backfires — write the recipe instead), no
  unconditional assertions **in judgment or detection rules** (state the conditions and
  exceptions), no inline "unless…" clause in a behavioral instruction (scope it by structure
  and put a genuine exception on its own line as a condition), evidence when you *narrow* a
  rule's scope and not only when you widen it, and any cap or budget must be wired into the
  procedure step that executes it — never left in a header.
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

## Editing the diagrams

The SVGs in `docs/assets/` are hand-authored, and SVG `<text>` does not wrap. A line that outgrows
its container is not an error: it renders clipped at the viewBox edge and looks fine in a diff.

**Render before you commit a diagram change.** Do not estimate the width, and do not trust a preview
that scales the image, because that is how a clipped line survived review here once already:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --hide-scrollbars \
  --window-size=920,348 \
  --screenshot=/tmp/out.png \
  "file://$PWD/docs/assets/does-it-work.svg"
```

Match `--window-size` to that file's `viewBox`, then look at the PNG. If a line does not fit, split
it into two `<text>` elements and grow the container plus the `viewBox` height to match. Keep about
8px of clearance from the right edge.


## Codex adapter checks

For a runtime adapter change, run the commands in [compatibility validation](../docs/codex-compatibility.md#validation).
The Python fixture suite and both packages' YAML/JSON checks are wired into validate.yml.
The optional check_runtime.py reads the real installed Codex loader without installing a plugin
or requesting a model turn. Record the CLI version and separate structural results from model
application-test results. The fresh-agent scenarios remain required for a behavioral release;
use [the cross-review cases](../docs/reviews/codex-cross-review.md) to review this adapter.

Keep the same-edition Claude and Codex manifest versions aligned for a release. Shared invariants
belong in both adapters' procedures; runtime tool names, instruction ownership and hooks stay
separate. Never copy Claude agent registration into the Codex payload. Both README languages must
show the same installed skill names. Editing one distribution does not update another automatically.
