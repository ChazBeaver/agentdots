# agentdots

Portable AI agent skills, installed by symlink into every agent CLI on the
machine. Sibling of `appdots` (app configs) and `hyprdots` (Hyprland), using
the same installer contract: declarative, idempotent, safe to rerun.

One skill folder in this repo shows up identically in Claude Code, Codex, and
OpenCode. Omarchy's bundled skills live alongside in the same target
directories and are never touched.

## Quick start

```bash
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

## Manual operation

Run these commands in a terminal; no agent CLI needs to be running. You need
Bash, Git, and the usual Unix file utilities. Examples assume this checkout:

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
| `./sync.sh` | Apply the repo to all targets, including tools not installed yet. |
| `./doctor.sh` | Run both checks below; exit nonzero on drift. |
| `bash doctor/env.sh` | Check the persisted repo path and alias. |
| `bash doctor/symlinks.sh` | Check skills, instructions, stale links, and foreign links. |

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

To add a skill, choose a previously unused name. This example creates a small
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
and sync. The old dangling links are pruned automatically:

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

To edit the global rules, run `nvim AGENTS.md`, then `./doctor.sh`; existing
symlinks expose the edit immediately. To add another tool, edit both the
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
  test "$(readlink ~/.codex/AGENTS.md)" = "$PWD/AGENTS.md" &&
  unlink ~/.codex/AGENTS.md && cp -a "$saved" ~/.codex/AGENTS.md
```

This intentionally creates drift; the next sync will manage the path again.
Backups are local recovery data, not files to commit. After moving the whole
checkout, run its `./sync.sh` and reload `~/.dotfiles-env.sh`.

## Layout

| Path | Purpose |
|:--|:--|
| `skills/<name>/` | One skill per folder. Linked only if it contains `SKILL.md`. |
| `lib/targets.sh` | The list of tool directories every skill is linked into. Edit here to add or drop a tool. |
| `lib/link.sh` | `link_item` (copied from appdots), `install_skills`, `prune_stale_links`. |
| `lib/env.sh` | Persists `AGENT_DOTS_DIR` and the alias. |
| `lib/log.sh`, `lib/detect.sh` | Verbatim from appdots. |
| `sync.sh` | Backup, link every skill into every target, prune stale links. |
| `backup.sh` | Copies any real (non-symlink) directory sync would replace into `backups/<timestamp>/`. Runs inside sync. |
| `doctor.sh`, `doctor/*.sh` | Read-only drift checks. Non-zero exit on drift. |

## Where skills are linked

| Target | Tool |
|:--|:--|
| `~/.claude/skills/<name>` | Claude Code |
| `~/.codex/skills/<name>` | Codex |
| `~/.agents/skills/<name>` | Shared cross-agent location (also read by Codex) |
| `~/.config/opencode/skills/<name>` | OpenCode (directory created on first sync) |

## Global instructions

`AGENTS.md` at the repo root holds the machine-wide rules every agent should
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

## Adding a skill

1. Create `skills/<name>/SKILL.md` with YAML frontmatter containing only
   `name` and `description`. Keep it tool-agnostic: no Claude-only keys, no
   `$ARGUMENTS`, no slash-command assumptions.
2. Put detail in supporting files next to it (`workflows/`, `references/`,
   `templates/`, `scripts/`) and reference them by relative path from
   `SKILL.md`. Scripts should be stdlib-only and optional.
3. Run `./sync.sh`.

Renaming or deleting a skill folder and re-running `./sync.sh` removes the old
link from every tool.

## Behaviour notes

- `link_item` replaces a wrong symlink or a real directory at the target path.
  `backup.sh` copies real directories aside first; symlinks are not backed up.
- Sync manages `<target>/<skill-name>`, the global instruction paths listed
  above, and its entries in `~/.dotfiles-env.sh`.
- Pruning only removes symlinks whose destination is inside this repo and no
  longer exists. Links to anywhere else are reported by `doctor.sh` as
  "foreign" and left alone.
