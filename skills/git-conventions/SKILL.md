---
name: git-conventions
description: Generate Conventional Commit messages and Conventional Branch names, and create Herdr worktrees on explicit request. Use when the user asks for a commit message, asks to commit changes, requests a branch name, asks to create a branch or worktree, or wants guidance on Git naming.
---

# Git Conventions

Generate names and messages from the actual work or, before edits exist, from
the active task. Keep suggestions separate from Git mutations.

## Gather context

When a Git worktree is available, inspect all current work: staged changes,
unstaged changes, and untracked files. Read enough of the changes to identify
their purpose and whether they form one logical unit. Do not prefer staged
changes merely because they are staged.

If the worktree contains unrelated changes, recommend separate commits or
branches and group the work clearly. If no changes exist, use the current task
and conversation. State an assumption only when the intent remains ambiguous.

## Preserve the action boundary

- A request for a commit message or branch name is advisory. Return text only;
  do not stage, commit, create, rename, or switch branches.
- Perform a Git mutation only when the user explicitly asks for that action,
  such as “commit these changes” or “create the branch.”
- An explicit request to create a worktree authorizes creating the one
  Conventional Branch required for that worktree. Do not create a branch merely
  because a worktree could be useful.
- An explicit action authorizes only that action and its stated scope. If an
  explicit commit request contains unrelated work that would require multiple
  commits, present the proposed grouping and get direction before proceeding.

## Route the request

- For commit messages or commit actions, read
  [references/commits.md](references/commits.md).
- For branch names or branch-creation actions, read
  [references/branches.md](references/branches.md).
- For a worktree request or when considering a worktree recommendation, read
  [references/worktrees.md](references/worktrees.md).
- Read both only when the request genuinely involves both.

## Present suggestions

Return one copy-ready suggestion when one logical answer is clear. Add a brief
note only when an assumption, ambiguity, or recommended split matters. Do not
offer a menu of alternatives unless the user asks for one.
