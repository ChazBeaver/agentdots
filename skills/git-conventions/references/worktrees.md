# Herdr Worktrees

Use this workflow only when the user explicitly asks to create a worktree, or
when deciding whether to suggest one.

## Naming and authorization

- Derive the worktree branch name from the active task using the Conventional
  Branch rules in [branches.md](branches.md).
- A request for a worktree name is advisory: provide the branch name only.
- A request to create a worktree authorizes creation of exactly that branch and
  its Herdr worktree. It does not authorize commits, pushes, or other Git
  changes.
- Use the requested base ref. Otherwise base the worktree on the target
  repository's currently checked-out branch.

## Creation process

1. Identify the target repository and inspect its Git state. If the task spans
   unrelated purposes, propose separate worktrees rather than flattening them
   into one generic branch.
2. Verify that Herdr is available and that `HERDR_ENV=1`. If not, explain that
   Herdr cannot be controlled from the current session; do not silently fall
   back to `git worktree`.
3. Read `herdr worktree` help when the installed command syntax is not already
   known. Treat the installed CLI as authoritative.
4. Create the worktree with `herdr worktree create`, passing the repository
   root via `--cwd` and the Conventional Branch name via `--branch`. Pass an
   explicit `--base` only when the user selected a base other than the current
   branch. Let Herdr select its default path unless the user requested one. Use
   `--no-focus` unless the user asks to switch to the new workspace.
5. Read Herdr's response and report the actual branch and path/workspace it
   created. Do not infer them from a naming pattern.

## When to suggest a worktree

You may ask whether the user wants a Herdr worktree when isolated work would
materially help—for example, parallel independent changes, a risky refactor,
or preserving an unrelated dirty working tree. A suggestion is never
authorization to create one.
