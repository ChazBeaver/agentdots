---
name: review-changes
description: Review staged, unstaged, and untracked repository changes against the task requirements and repository standards, with evidence for each verdict. Use when asked to review working changes or verify an implementation.
---

# Review changes

Check requirements and repository standards separately. A passing check on one
does not establish the other. Treat the builder's report as claims to verify
against the original request, files, and observed results.

## Establish the review inputs

Read the owning repository's instructions, applicable nested instructions,
relevant glossary and ADRs, and any documented standards. Obtain the original
request or task brief from the user or an identified issue/plan. Resolve
ambiguity from those sources rather than deriving requirements from the code
being reviewed. If no requirements are available, review what can be assessed
and mark requirements NOT VERIFIED; do not invent a spec or call that a pass.

Default to the current working changes. Inspect `git status --short
--untracked-files=all`, `git diff --cached`, and `git diff`, then read relevant
untracked files explicitly. Account for new files, deletions, renames, symlinks,
and file modes. Follow the task's scope and preserve unrelated existing work.
Identify excluded files and explain any coverage gaps.

If the user supplies a comparison ref, resolve it to a commit SHA once and
review its merge-base diff to `HEAD`, plus working changes unless the user
requested committed changes only. An invalid ref requires clarification.
An empty diff establishes only that no changes were found for that comparison;
it does not prove implementation completeness. Record the comparison used.

## Inspect and verify

Trace each criterion through the implementation, relevant callers, and tests.
Check important failure, cancellation, and boundary cases. Identify missing
behavior and demonstrated regressions. Compare in-scope changes with the
documented standards and accepted decisions; distinguish hard violations from
optional design suggestions.

Run appropriate isolated checks when permitted. Inspect unfamiliar entrypoints
before executing them: names such as test or doctor do not establish their
side effects. Keep the review phase free of source edits and live activation;
sync, bootstrap, deployment, publication, staging, and commits are separate
actions. Report when a live check or missing tool prevents verification.
If fixes were also requested, finish the review findings first, then handle
implementation and renewed verification as a distinct step under that request.

Preserve exact command outcomes. Distinguish checks you ran from results only
reported by the builder. Passing tests support only the behavior those tests
actually cover. Explain what static inspection establishes and what still
requires runtime observation. Record the reviewed `HEAD` and working-change
scope; concurrent changes that affect the result require a refreshed review.

## Report the result

Lead with actionable findings, most consequential first. For each, give its
location, violated criterion or documented rule, observed evidence, and effect.
Keep optional improvements separate from blockers; when none are found, say so.

Give every acceptance criterion one verdict:

| Verdict | Meaning |
| --- | --- |
| PASS | Direct inspection or an observed check establishes the criterion; cite the evidence and its scope. |
| FAIL | Observed evidence contradicts the criterion; explain the discrepancy. |
| NOT VERIFIED | Necessary evidence, access, or requirements are missing; explain what would resolve it. |

Report repository standards separately with the same verdicts. Include commands
run, relevant checks not run, and coverage limits. Declare the reviewed scope
READY only when every required criterion and applicable standard passes, with
no unresolved blocking findings or necessary verification gaps. Otherwise use
NOT READY for demonstrated blockers or INCOMPLETE for missing evidence.

Use one reviewer by default. An independent review needs the original brief
and artifacts in a separate session; this skill does not create or isolate
agents. A read-only instruction is guidance, not an enforced permission boundary.

Source and licensing information: [UPSTREAM.md](UPSTREAM.md).
