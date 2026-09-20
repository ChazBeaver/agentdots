# Conventional Commit Messages

Follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
with this deliberately small local vocabulary.

## Format

```text
<type>[optional scope][!]: <description>
```

Return the subject line only unless the user explicitly asks for a body or
footers.

## Types

- `feat`: adds a user-visible capability or meaningfully extends behavior.
- `fix`: corrects broken, incorrect, or unintended behavior.
- `chore`: maintenance that does not add or fix behavior, including ordinary
  documentation, tests, behavior-preserving refactors, build or CI work,
  dependency updates, and formatting.
- `revert`: only for an actual reversal of an earlier commit.

Classify the effect, not the file extension. A `SKILL.md` edit that teaches an
agent a new capability is `feat`; one that corrects agent behavior is `fix`.
An explanatory README-only change is normally `chore`.

## Scope and description

- Add a scope when one stable subsystem is obvious, such as `cooking` or
  `sync`. Use a lowercase, hyphen-separated noun. Omit the scope for broad or
  ambiguous changes.
- Write a concise, imperative description that starts lowercase and has no
  trailing period.
- Mark an incompatible behavior change with `!` immediately before the colon.
- Never invent an issue identifier or scope that the repository does not use.

Examples:

```text
feat(cooking): add pantry-aware meal filtering
fix(sync): preserve foreign skill links
chore: update installation notes
feat(sync)!: change the skill target layout
revert: restore previous target discovery
```

## Logical commits

Base the result on all current staged, unstaged, and untracked work. When the
changes represent multiple unrelated purposes, recommend one subject per
logical commit and briefly identify which changes belong together. Do not
force unrelated work under one vague subject.
