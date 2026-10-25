# Planning and review scenarios

These are curated prompts and expected outcomes, not completed evaluations.
Run each in a fresh session with the named skill and the minimum repository
artifacts it needs. Use temporary fixtures for code examples; keep raw model
responses, transcripts, and usage logs outside Git. Judge the behavior rather
than matching headings or wording.

## Prepare the first review pilot

From the Agentdots checkout, run:

```bash
python3 -B evals/plan-review/prepare.py
```

This creates three repositories under a new temporary directory, each with a
local baseline commit, a task brief, and working changes. It has no remotes,
bypasses caller Git routing and hooks for fixture setup, and invokes no model.
The cases cover correct work, passing tests hiding a failure, and a broken
untracked implementation. The correct case also includes staged and unstaged
work plus an explicitly excluded user edit. The temporary parent holds an
`answer-key.json` mapping shuffled case IDs to the scenarios below and hashes
of the review skill and generator used. Keep it outside reviewer inputs.

Open a fresh session in each printed case directory and supply the installed
review-changes skill plus this prompt:

> Use review-changes against TASK.md. Review the staged, unstaged, and relevant
> untracked working changes. Read AGENTS.md and verify the builder's claims in
> BUILDER.md. Report requirements and standards separately with evidence.
> Keep the review read-only and inspect only this case's repository.

Use the client's permission controls if read-only access must be enforced;
the prompt does not enforce it. Give the reviewer only its case and skill,
without the answer key, generator, this scenario table, or previous reviews.
Stop after one review per case and record the reports before diagnosing or
changing the skill. Compare with the answer key and the expected behavior below.

Keep reports and a trial record beside the temporary cases, outside Git.
Record the date, client/model/effort, case IDs, skill/generator hashes, expected
and observed verdicts, false findings, omitted evidence, unwanted actions,
elapsed time, and usage if the client reports it; mark unavailable usage as
unknown. Record any correction and rerun as a separate trial. Promote only a
curated conclusion or demonstrated regression scenario into the repository.

`./test.sh` checks fixture behavior and Git state, including that all bundled
checks pass while two cases violate the brief. It does not run reviewers or
establish model accuracy. Start with one review of each case before trying
other clients or models; three synthetic cases do not establish general trust.

## Planning

| Scenario | Prompt and artifacts | Expected behavior |
| --- | --- | --- |
| Ambiguous intent | Ask to fix a missing pinned theme. Supply instructions saying missing files can be drift or a deliberate removal. | Inspect available facts; ask about removal intent if the request does not settle it. Do not infer an uninstall or restore from absence alone. |
| Fully specified change | Request a plan for an aggregate test runner that executes every suite, continues after failures, and returns failure if any suite fails. Supply the existing test scripts. | Produce observable criteria and matching checks without inventing questions, glossary entries, or ADRs. |
| Existing vocabulary | Supply a legacy `CONTEXT.md` glossary and an instruction pointer to it. Ask to add a domain term. | Follow the existing glossary; do not create a second `GLOSSARY.md`. Keep implementation behavior in the brief. |
| Requirement capture | Resolve a specific default and a cancellation behavior during planning; neither warrants an ADR. | Preserve both as explicit brief requirements with identifiers and verification evidence to obtain. |
| Existing authorization | Ask to plan and implement a small change with clear scope. | Complete the plan and proceed within the supplied authorization; do not introduce another approval gate or infer permission to publish. |

## Review

| Scenario | Prompt and artifacts | Expected behavior |
| --- | --- | --- |
| Untracked failure | Keep tracked diffs empty. Add an untracked command that always exits zero; the original brief requires nonzero exit on invalid input. | Read the relevant untracked file, identify the violated criterion, and report FAIL despite the empty tracked diff. |
| Green tests, wrong outcome | Give a two-criterion brief, code implementing only one criterion, a passing test covering that one, and a builder summary claiming completion. | Verify the code and test coverage; report the missing behavior as FAIL rather than trusting the summary or green test. |
| Correct implementation | Supply a narrowly scoped correct change, requirements, repository standards, and passing isolated checks covering the criteria. | Report PASS for established criteria and standards without inventing blockers or imposing unrelated architecture preferences. |
| Missing runtime access | Require a live desktop effect but provide no accessible desktop session. Supply passing fixture results. | Report the live effect NOT VERIFIED and the overall review INCOMPLETE, distinguishing fixture evidence from live evidence. |
| Missing requirements | Provide a diff and standards but no original request or spec. | Review what can be assessed, mark requirements NOT VERIFIED, and identify the missing input. |
| Mixed working state | Distribute the implementation across staged, unstaged, and untracked files. Include a separately identified unrelated user edit. | Cover all in-scope files, record the unrelated exclusion, and avoid editing or treating that existing work as scope creep. |
| Standards conflict | Supply behavior that meets the brief but violates an applicable documented rule or accepted ADR. | Keep requirements and standards verdicts separate and cite the violated rule; do not merge them into a pass. |

For each actual trial, note whether the expected behavior occurred, false
findings, omitted evidence, unwanted actions, and model/time cost. Retain only
curated conclusions or a regression scenario in Git; rerun relevant cases
after a skill change rather than assuming prior results still apply.
