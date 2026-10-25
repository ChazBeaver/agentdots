# agentdots

Portable AI agent rules and skills, installed by symlink into every agent CLI on the
machine. Sibling of `appdots` (app configs) and `hyprdots` (Hyprland), using
the same installer contract: declarative, idempotent, safe to rerun.

One skill folder in this repo shows up identically in Claude Code, Codex, and
OpenCode. Omarchy's bundled skills live alongside in the same target
directories and are never touched.

## Quick start

```bash
mkdir -p ~/Projects/home
git clone <repo-url> ~/Projects/home/agentdots
cd ~/Projects/home/agentdots
./sync.sh
```

After a `git pull`, or after adding or renaming a skill:

```bash
./sync.sh
```

To check for drift without changing anything:

```bash
./doctor.sh
```

`sync.sh` also writes `AGENT_DOTS_DIR` and an `agentdots` alias (cd into the
repo) into `~/.dotfiles-env.sh`, next to the appdots and hyprdots entries.

Personal repositories live at `~/Projects/home/<repo>` on every machine.
Create the parent before cloning as shown above; successful sync also creates
it if missing. Sync creates the environment file as needed, repairs this
repo's export and alias, removes duplicates for those keys, and preserves
other repos' entries. It registers the current checkout without moving it.
This registry supplies appdots' `home-status`, `home-pull`, `home-sync`, and
`home-doctor`. Run `bash tests/env.sh` for isolated registration checks.

## Use the skills

Ask for a skill by name in the agent client while working in the repository
that owns the change. These examples are ordinary requests, not client-specific
slash commands:

| Skill | Purpose | Example request |
| --- | --- | --- |
| [plan-change](skills/plan-change/SKILL.md) | Resolve design questions and preserve the agreed requirements in a task brief. | "Use plan-change to plan the package cleanup and put the brief in my existing project plan." |
| [review-changes](skills/review-changes/SKILL.md) | Check working changes against the original requirements and repository standards, with evidence for each verdict. | "Use review-changes against this task brief, including staged, unstaged, and relevant untracked files." |
| [git-conventions](skills/git-conventions/SKILL.md) | Conventional Commit messages, branch names, and explicitly requested Herdr worktrees. | "Suggest a commit message for these changes." |

The [plan, build, and review guide](docs/workflows/plan-build-review.md) shows
how to hand a brief to a builder and then a separate reviewer. The new planning
and review packages adapt Matt Pocock's approach with pinned source references
and MIT notices in each package's `UPSTREAM.md`. They are self-contained and
use only the portable `name` and `description` metadata.

The [evaluation scenarios](evals/plan-review/scenarios.md) define expected
behavior for future trials. A passing package validator and successful install
establish structure and links; model behavior needs a separate trial.

## Manual operation

Run these commands in a terminal; no agent CLI needs to be running. You need
Bash, Git, Python 3, and the usual Unix file utilities. The validator uses
only Python's standard library; no Python packages need installing.
Examples assume this checkout:

```bash
cd ~/Projects/home/agentdots
git status --short
git pull --ff-only           # stop and resolve divergence if this fails
./sync.sh                   # backs up, links instructions/skills, prunes stale links
source ~/.dotfiles-env.sh    # load the repaired path and alias in this shell
./doctor.sh                 # success ends with "All checks passed."
agentdots                   # return here from another directory
```

Individual entrypoints take no arguments:

| Example | Effect |
| --- | --- |
| `./backup.sh` | Copy conflicting real skills and instruction files into `backups/<timestamp>/`; leave originals in place. Sync calls this automatically. |
| `./sync.sh` | Validate active skills and check collisions, then apply the repo to all targets, including tools not installed yet. |
| `./doctor.sh` | Run both checks below; exit nonzero on drift. |
| `./test.sh` | Run all isolated regression suites; continue after a failed suite and return nonzero if any fail. |
| `bash doctor/env.sh` | Check the persisted repo path and alias. |
| `bash doctor/symlinks.sh` | Validate skill packages; check installed skills, instructions, retired links, and foreign links. |

These entrypoints do not implement a dry run or argument parser; do not use
`--help` to preview a sync. Files in `lib/` are sourced implementation helpers,
not standalone commands.

The included `git-conventions` skill is also readable without an agent:
see its [commit format](skills/git-conventions/references/commits.md),
[branch naming](skills/git-conventions/references/branches.md), and
[Herdr worktree procedure](skills/git-conventions/references/worktrees.md).
For example, when you intentionally want a new worktree, run this inside a
Herdr session from the target repository (it creates a branch and workspace):

```bash
herdr worktree create --cwd "$PWD" --branch chore/manual-usage --no-focus
```

It uses the current branch as the base; supply `--base main` only when you
want an existing main branch instead. Read the returned path/workspace ID;
do not guess its location. This is an optional workflow, not a sync step.

### Edit, add, rename, or retire a skill

Edit an existing skill and its references directly, then check it:

```bash
cd ~/Projects/home/agentdots
nvim skills/git-conventions/SKILL.md
./sync.sh
./doctor.sh
```

To add a skill, choose a name unused in the client targets. This example creates a small
portable skill that you can expand before installing:

```bash
mkdir skills/repo-review
cat > skills/repo-review/SKILL.md <<'EOF'
---
name: repo-review
description: Review a repository's working changes and report findings.
---

Read AGENTS.md, inspect git diff, and report actionable findings with file paths.
EOF
./sync.sh
./doctor.sh
```

To rename that example, move its folder, update `name:` and any references,
and sync. Links for the old name are pruned automatically:

```bash
mv skills/repo-review skills/change-review
nvim skills/change-review/SKILL.md
./sync.sh
./doctor.sh
```

To retire it without throwing away the source, move it outside `skills/`:

```bash
mkdir -p ~/Backups/retired-agent-skills
mv skills/change-review ~/Backups/retired-agent-skills/
./sync.sh
./doctor.sh
```

To edit the global rules, run `nvim instructions/global.md`, then `./doctor.sh`;
existing symlinks expose the edit immediately. The root `AGENTS.md` and its
relative `CLAUDE.md` link contain instructions for developing Agentdots itself.
After updating an older installation that linked clients to the root file,
run `./sync.sh` to migrate those links to `instructions/global.md`.
To add another tool, edit both the
target lists and labels in `lib/targets.sh`, then run `./sync.sh` and
`./doctor.sh`. Removing a target from that file stops future management; it
does **not** remove links already installed in the former target directory.

### Inspect and recover a replaced file

```bash
find backups -mindepth 1 -maxdepth 4 -print
readlink ~/.codex/AGENTS.md
```

For example, to restore a previous Codex instruction file, set `saved` to the
actual backup path printed above. First verify the destination is still the
agentdots link, then unlink it and copy the saved file:

```bash
saved='backups/REPLACE_WITH_TIMESTAMP/instructions/.codex-AGENTS.md'
test -f "$saved" && test -L ~/.codex/AGENTS.md &&
  test "$(readlink ~/.codex/AGENTS.md)" = "$PWD/instructions/global.md" &&
  unlink ~/.codex/AGENTS.md && cp -a "$saved" ~/.codex/AGENTS.md
```

This intentionally creates drift; the next sync will manage the path again.
Backups are local recovery data, not files to commit. After moving the whole
checkout, run its `./sync.sh` and reload `~/.dotfiles-env.sh`. Sync reads the
previous `AGENT_DOTS_DIR` export without executing the environment file, so
links from the recorded old checkout remain identifiable as owned. It updates
that export only after convergence succeeds. Keep the old export until sync
has repaired the links; links from any other checkout require an explicit
ownership decision.

## Layout

| Path | Purpose |
|:--|:--|
| `skills/<name>/` | Active skill packages; every directory must have a valid `SKILL.md`. Keep drafts outside this directory. |
| `instructions/global.md` | Shared policy installed into global client instruction paths. |
| `AGENTS.md`, `CLAUDE.md` | Repository development instructions and their relative symlink; never exported globally. |
| `lib/targets.sh` | Shared instruction source and client target lists. Edit here to add or drop a tool. |
| `lib/link.sh` | Skill preflight, ownership checks, link installation, and retirement pruning. |
| `scripts/validate-skills.py` | Read-only metadata and bundled-reference validation; prints active skill paths only when all packages pass. |
| `lib/env.sh` | Persists `AGENT_DOTS_DIR` and the alias. |
| `lib/log.sh`, `lib/detect.sh` | Verbatim from appdots. |
| `sync.sh` | Backup, link every skill into every target, prune stale links. |
| `backup.sh` | Copies any real (non-symlink) directory sync would replace into `backups/<timestamp>/`. Runs inside sync. |
| `doctor.sh`, `doctor/*.sh` | Read-only drift checks. Non-zero exit on drift. |
| `test.sh`, `tests/` | Regression entrypoint and temporary fixtures; no live client installation. |
| `skills/plan-change/templates/task-brief.md` | Canonical outcome, scope, acceptance, and evidence template; `docs/templates/task-brief.md` links to it. |
| `docs/workflows/plan-build-review.md` | Manual handoff procedure and example prompts for one builder and a separate reviewer. |
| `evals/plan-review/scenarios.md` | Curated planning/review prompts and expected outcomes; raw trial output stays local. |

## Where skills are linked

| Target | Tool |
|:--|:--|
| `~/.claude/skills/<name>` | Claude Code |
| `~/.codex/skills/<name>` | Codex |
| `~/.agents/skills/<name>` | Shared cross-agent location (also read by Codex) |
| `~/.config/opencode/skills/<name>` | OpenCode (directory created on first sync) |

## Global instructions

`instructions/global.md` holds the machine-wide rules every agent should
follow. `sync.sh` links it to each harness's global instruction path:

| Target | Tool |
|:--|:--|
| `~/.claude/CLAUDE.md` | Claude Code |
| `~/.codex/AGENTS.md` | Codex |
| `~/.config/opencode/AGENTS.md` | OpenCode |

Keep it harness-agnostic and short. Rules that only apply inside one
repository belong in that repository's own `AGENTS.md` (with `CLAUDE.md` as
a symlink to it) and its `.agents/skills/`; agentdots never reaches into other
checkouts. A real file already at a target path is copied to `backups/`
before it is replaced.

`./test.sh` checks global instruction migration, package validation, foreign
collisions, real-file backups, repeated installation, renames, retirement,
checkout moves and retries, and the aggregate runner's failure handling. The
fixtures route client paths into temporary directories without changing `HOME`.
The real installer and doctor are exercised with those isolated targets.

For a substantive change, use [the task brief](docs/templates/task-brief.md)
in the existing issue or plan. Keep domain vocabulary in the owning repo's
glossary, architectural tradeoffs in its decision records, and acceptance
criteria in the brief. These documents capture intent; session logs stay local.

## Adding a skill

1. Create `skills/<name>/SKILL.md` with YAML frontmatter containing only
   `name` and `description`. Keep it tool-agnostic: no Claude-only keys, no
   `$ARGUMENTS`, no slash-command assumptions.
2. Put detail in supporting files next to it (`workflows/`, `references/`,
   `templates/`, `scripts/`) and reference them by relative path from
   `SKILL.md`. Scripts should be stdlib-only and optional.
3. Run `./sync.sh`.

Renaming or deleting a skill folder and re-running `./sync.sh` removes the old
link from every tool. Removing only `SKILL.md` leaves an invalid active package;
doctor reports it and sync stops. Restore the file or move the whole draft
outside `skills/` before retrying.

### Portable package checks

Sync and doctor use the same validator. To run it without changing clients:

```bash
python3 -B scripts/validate-skills.py skills
```

The header begins and ends with `---` and has exactly two nonempty string
fields: `name` and `description`. The name matches its directory and uses
lowercase letters, digits, and single hyphens, at most 64 characters. Supported
values are plain text, YAML single-quoted strings, JSON double-quoted strings,
and indented literal (`|`) or folded (`>`) blocks, optionally with `+` or `-`.
Quote punctuation such as `: ` or ` #`, numeric text, and words interpreted
as booleans by YAML readers. This is a documented YAML subset, not a general
YAML parser: collections, tags, aliases, extra keys, and other scalar syntax
must be rewritten into this portable format before installation.

Instructions must follow the header. Local Markdown links and reference
definitions must resolve inside the skill folder, including through linked
Markdown documents. Percent-encoded paths and symlinks are resolved before
checking that boundary. Fenced examples, inline code, and HTML comments are
excluded. External links are not fetched, and fragment names are not checked.
Use Markdown links for required supporting files; plain text mentions and
runtime calls to other skills are not dependency declarations this check can
verify. Packaging checks do not establish correct agent behavior or triggering.

### Skill ownership collisions

Before backups, environment changes, or client link changes, sync validates
all active packages and checks their names across every skill target. A
same-named symlink into another source, including a dangling foreign link,
stops installation and stays intact. Choose another skill name, or deliberately
move the existing link aside after deciding to replace it. There is no
automatic adoption of foreign skill links.

## Behaviour notes

- Skill installation repairs links owned by this checkout or the previous
  checkout recorded in the environment file. Non-colliding foreign skill
  links remain informational and are left alone.
- Real files and directories at managed targets retain the existing recovery
  workflow: `backup.sh` copies them aside before sync replaces them. Global
  instruction links retain their existing replacement behavior.
- Sync manages `<target>/<skill-name>`, the global instruction paths listed
  above, and its entries in `~/.dotfiles-env.sh`.
- Pruning removes owned links that no longer match an active skill and target
  name, even if their old source still exists. An incomplete active package
  fails validation before pruning; it is not treated as a retirement.
