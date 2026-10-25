# Plan, build, and review

Use a short task brief to connect planning, implementation, and review. Start
with one builder and one reviewer. Both skills are portable Markdown packages;
they need no external skill dependencies or issue-tracker setup.

## Plan

In the repository that owns the change, ask:

> Use plan-change to plan <change>. Read the existing code and instructions,
> resolve the decisions that need my input, and put the brief in <existing plan>.

Planning records agreed vocabulary in the repository's glossary and qualifying
architectural choices in ADRs. Other requirements stay in the brief. A small,
clear request may need no interview, new glossary, or ADR. If implementation
was already requested, a settled plan lets the agent continue under that scope.

The canonical [task-brief template](../../skills/plan-change/templates/task-brief.md)
ships inside plan-change. The original `docs/templates/task-brief.md` path is
a relative symlink to it, so there is one maintained template.

## Build

Give the builder the agreed brief:

> Implement the task brief at <path>. Preserve its scope and authorization.
> Verify each acceptance criterion and report the evidence and any gaps.

Retain criterion identifiers when requirements change. Update the brief when
the user changes the requested behavior; keep the original reasoning or
reference available. Tests, machine diagnostics, and live activation establish
different things, so report which checks actually ran.

## Review

For an independent review, open a separate session in the same repository
after the builder has reached a stopping point:

> Use review-changes against the original task brief at <path>. Review the
> staged, unstaged, and relevant untracked changes. Report requirements and
> repository standards separately, with evidence. Keep the review read-only.

Name any existing work excluded from the task. For a committed comparison,
supply the base commit, branch, or tag and say whether working changes should
also be reviewed. The default needs no commit or branch creation.

A reviewer reads the brief and actual artifacts rather than relying on the
builder's summary. A green test suite can coexist with a missing requirement.
Missing runtime access produces NOT VERIFIED, not a passing result.

## Resolve findings

Return demonstrated findings to the builder, then review the resulting changes
and the affected checks. Bring unresolved requirements or scope decisions back
to the user. Start with manual handoffs before adding automatic retry loops.

These instructions provide a workflow, not agent orchestration or enforced
isolation. Use the client's actual permission controls when a reviewer must
be technically prevented from editing. Commit and publication remain governed
by the repository's existing authorization rules.

Use [the evaluation scenarios](../../evals/plan-review/scenarios.md) to trial
the skills against expected outcomes. Packaging tests and installed symlink
checks do not establish model behavior; record actual trial results separately.
