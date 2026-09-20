# Conventional Branch Names

Follow [Conventional Branch 1.1.0](https://conventionalbranch.org/) for naming.
This convention governs names only; it does not impose a branching, review,
merge, rebase, release, or deletion lifecycle.

## Format and purpose

```text
<type>/<description>
```

Use the canonical purpose prefixes:

- `feature/`: new behavior or capability.
- `bugfix/`: an ordinary defect correction.
- `hotfix/`: an urgent correction to released or production behavior.
- `release/`: release preparation.
- `chore/`: maintenance, documentation, tests, refactors, or other supporting
  work.

`main`, `master`, and `develop` are valid unprefixed trunk names, but do not
introduce or prescribe any of them. Prefer the canonical `feature/` and
`bugfix/` forms rather than their `feat/` and `fix/` aliases.

## Description rules

- Use lowercase letters and numbers, with single hyphens between words.
- Use dots only for version numbers, as in `release/v1.2.0`.
- Do not use spaces, underscores, repeated separators, or extra slashes.
- Describe the purpose concisely and do not invent an issue identifier.
- Do not use agent-source prefixes such as `codex/` or `ai/`; these names are
  generated only at the user's direction and should describe the work.

Examples:

```text
feature/add-git-conventions
bugfix/preserve-foreign-skill-links
hotfix/restore-skill-discovery
release/v1.2.0
chore/update-installation-notes
```

If the requested work contains unrelated purposes, recommend separate
branches and provide one name for each proposed branch rather than hiding the
split in a generic description.
