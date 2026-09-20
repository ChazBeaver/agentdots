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
- Only paths of the form `<target>/<skill-name>` are ever written. Nothing else
  under `~/.claude`, `~/.codex`, `~/.agents`, or `~/.config/opencode` is read
  or modified.
- Pruning only removes symlinks whose destination is inside this repo and no
  longer exists. Links to anywhere else are reported by `doctor.sh` as
  "foreign" and left alone.
