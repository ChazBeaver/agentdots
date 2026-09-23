# Global agent instructions

These rules apply on every machine and in every directory, for any coding
agent. They are installed by agentdots and are deliberately harness-agnostic.
A repository's own `AGENTS.md` adds to them and wins on conflict.

## Read the repository's instructions first

Every personal repository carries an `AGENTS.md` at its root (with `CLAUDE.md`
as a symlink to it) and may carry repository-scoped skills under
`.agents/skills/`. Read the root file before changing anything in that
repository, and prefer a repository skill over improvising a procedure.

## Where things live

Repository locations are exported in `~/.dotfiles-env.sh` as `APP_DOTS_DIR`,
`HYPR_DOTS_DIR`, and `AGENT_DOTS_DIR`.

| Concern | Repository |
| --- | --- |
| Application configs, shell, packages for Linux and macOS | appdots |
| Hyprland, Omarchy shell, pinned Omarchy plugins and themes | hyprdots |
| Agent skills and this file | agentdots |
| Recipes, meal plans, pantry (for the cooking skill) | kitchen, linked at `~/kitchen` |

Put a file in the repository that owns its concern. Skills never go in appdots
or hyprdots' global scope; a procedure that only makes sense inside one
repository goes in that repository's `.agents/skills/`. If ownership is
unclear, ask.

## Persist intent, never state

Version what was decided: configs, instructions, skills, pinned sources.
Never commit credentials, tokens, session or history files, caches, or
anything a tool generated about itself. If a tool rewrites a file you want to
persist, persist the intended keys with a merge step rather than the file.

## Git

- Use Conventional Commits and Conventional Branch names.
- Do not commit, push, or create branches unless asked. Leave changes in the
  working tree and offer a message.
- Report test and doctor results exactly; if something failed, say so first.

## Skills and schemas

- A skill is portable: `SKILL.md` frontmatter holds only `name` and
  `description`, with no tool-specific keys, `$ARGUMENTS`, or slash-command
  assumptions. Detail lives in files beside it, referenced by relative path.
- Prefer the smallest schema that answers the real queries. One tagged field
  with an enforced vocabulary beats many optional fields, and searchable data
  is derived from content rather than maintained twice.

## Omarchy machines

- Never modify anything under `/usr/share/omarchy/`; reading it is encouraged.
- Prefer the `omarchy` CLI over hand-editing what it manages, and validate
  Hyprland changes with `hyprctl reload` followed by `hyprctl configerrors`.

## Working style

- Verify with the repository's own `doctor.sh` and tests before reporting done.
- Make the smallest change that fully solves the request; do not widen scope.
- When a repository already has a mechanism for something, extend it instead
  of adding a parallel one.
