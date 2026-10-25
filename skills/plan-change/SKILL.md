---
name: plan-change
description: Plan a substantive repository change by resolving design questions, recording domain language and architectural decisions, and producing a task brief. Use when asked to plan a change, clarify requirements, or prepare work for implementation.
---

# Plan a change

Produce a brief that a builder and a separate reviewer can use without
reconstructing the planning conversation. Preserve requirements that are too
specific for a glossary or too routine for an architectural decision record.

## Establish the scope

Read the owning repository's `AGENTS.md`, applicable nested instructions,
relevant code, and existing planning documents. Identify the requested outcome,
boundaries, and operations already authorized. Research facts the repository
can answer; ask the user for unresolved decisions.

Read repository-linked glossary entries for concepts the task touches and
ADRs governing the proposed changes. Honor existing glossary names and maps,
including legacy `CONTEXT.md` layouts; use a root `GLOSSARY.md` when the first
agreed term needs a home and the repository has no established glossary.
Missing documentation alone does not block planning or justify creating an
empty hierarchy.

## Resolve consequential questions

Work from decisions already settled to the questions they unblock. Ask the
smallest useful round of independent questions, with a recommended answer
and its tradeoff. Wait for answers needed by dependent work; continue useful
research elsewhere while waiting. Preserve prior answers and authorization.

Use judgment for routine implementation details. Ask when ambiguity materially
changes the requested behavior, scope, or consequences. Challenge overloaded
terms with concrete examples and check claims against the code. Surface an
ADR conflict before proposing a different design. Distinguish assumptions
from confirmed requirements; unresolved blocking assumptions remain questions.

## Capture intent as it settles

- Update agreed project vocabulary in the relevant glossary as terms resolve.
  Keep definitions brief and separate from implementation details.
- Record a decision in the repository's ADR location when it is costly to
  reverse, surprising without its reasoning, and a choice among real
  alternatives. Reuse existing numbering and format; otherwise use numbered
  Markdown under `docs/adr/` when repository conventions permit it. A short
  context, decision, and reason are enough. Mark unaccepted proposals as proposed;
  distinguish the date a past decision was recorded from when it was made.
- Keep other agreed behavior, ordering, defaults, failure cases, and exclusions
  in the task brief. These requirements must survive even when no ADR qualifies.

## Deliver the brief

Use [the task-brief template](templates/task-brief.md), adapting its size to
the change. Prefer the existing issue or plan in the owning repository; a
new file is useful only when there is no suitable durable home. Keep the
brief self-contained and readable without this skill package. Follow the
repository's naming, ownership, and privacy conventions.

Give each acceptance criterion an identifier and an observable result. Map it
to verification evidence, separating isolated tests, machine diagnostics, and
live activation. Retain the original request or spec reference, agreed scope,
authorized operations, assumptions, and remaining questions. Set completion
evidence to NOT VERIFIED until implementation and checks supply that evidence.

Finish when the brief covers the agreed outcome and decisions, and either
has no blocking questions or identifies exactly what remains unresolved.
Report the brief's location, domain documents changed, and blocking questions.

For planning-only requests, finish with the plan. When implementation is also
requested and its scope is settled, continue within the existing authorization;
this skill adds no extra approval gate. Creating or updating planning documents
does not itself authorize commits, pushes, publication, or unrelated changes.

Source and licensing information: [UPSTREAM.md](UPSTREAM.md).
