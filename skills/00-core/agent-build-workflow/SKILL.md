---
name: agent-build-workflow
description: Use when a coding agent is executing a multi-step build, fix, or feature task and needs a repeatable loop for planning, acting, and verifying work.
category: core
tags: [agent-workflow, process, automation]
maturity: stable
updated: 2026-08-21
---

## Purpose

Coding agents produce more reliable results when they follow an explicit plan-act-verify loop instead of free-form editing. This skill defines that loop: understand the task, form a plan, make the smallest change that satisfies it, run verification, and report progress — repeating until the task is complete.

It reduces two common agent failure modes: silently drifting from the original request, and declaring success without actually proving the change works.

## When to use / When NOT to use

**Use this skill when:**

- An agent is given a coding task spanning more than a single trivial edit.
- The task requires touching multiple files or coordinating several changes.
- You need a consistent way to track partially completed multi-step work.
- The task has ambiguous scope and needs to be broken down before execution.
- Multiple sub-tasks depend on each other and must be sequenced correctly.

**Do NOT use this skill when:**

- The task is a single-line, unambiguous fix — just make the edit and verify directly.
- You are only answering a question with no code change involved.
- The task is already fully specified as a single atomic step with no sub-decisions.

## Prerequisites

- Read access to the target repository and its existing tests/build tooling.
- skills/00-core/context-gathering/SKILL.md applied to understand the codebase first.
- A clear statement of the requested outcome, even if some details need clarifying assumptions.

## Workflow

1. **Restate the task** - Summarize the requested outcome in your own words, including explicit and implicit acceptance criteria.
2. **Gather context** - Locate relevant files, existing conventions, and prior art before writing any code.
3. **Form a plan** - Break the task into an ordered list of small, independently verifiable steps.
4. **Track the plan explicitly** - Maintain a visible list of steps with status (pending/in_progress/done/blocked) as work proceeds.
5. **Execute the smallest next step** - Make one focused change at a time rather than editing many files speculatively.
6. **Verify immediately** - Run the build, tests, or linter scoped to the change just made, not just at the very end.
7. **Adjust the plan when reality disagrees** - If a step reveals the plan was wrong, revise it explicitly rather than silently improvising.
8. **Report and iterate** - Summarize what changed and what remains, then continue to the next step until the plan is complete.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Task is a single well-defined bug fix | Skip formal planning; fix, verify, and report directly. |
| Task spans multiple files or subsystems | Write an explicit step list before editing anything. |
| A step reveals the plan was wrong | Stop, revise the plan, and continue — do not silently improvise around it. |
| Verification tooling is missing or broken | Fix or note the gap explicitly rather than skipping verification silently. |
| A step is blocked by an external dependency | Mark it blocked, explain why, and continue with independent steps if any exist. |
| The user's request is ambiguous about scope | State the assumed scope in the plan before executing, so it can be corrected early. |

## Reference implementation

A minimal task-tracking format an agent can maintain across a multi-step task:

```text
Task: Add pagination to GET /orders

Restated acceptance criteria:
  - Endpoint accepts pageNumber/pageSize query params (default 1/20).
  - Response includes totalCount and totalPages.
  - Existing callers without query params keep working unchanged.

Plan:
1. [done]        Read existing OrdersController and repository for conventions
2. [done]        Add PageNumber/PageSize query params with validation
3. [in_progress] Update repository query to apply Skip/Take
4. [pending]     Add/adjust integration test for paginated response shape
5. [pending]     Run dotnet test --filter Orders and confirm green

Verification performed so far:
- dotnet build succeeded after step 2
- Manual curl against /orders?pageNumber=1&pageSize=5 returned expected shape

Next action: implement step 3, then rerun the targeted test in step 5.
```

- Persist this plan somewhere durable (PR description, issue comment, or scratch file) so progress survives interruptions.
- Update the status markers in real time, not retroactively at the end of the task.

### What silent plan drift looks like

A red-flag transcript pattern to recognize and avoid in agent output:

```text
Turn 1: "Plan: 1) add param 2) update query 3) add test"
Turn 2: *edits 6 unrelated files, renames 2 classes, upgrades a NuGet package*
Turn 3: "Done! Also cleaned up some other things while I was in there."

Why this fails: the plan was abandoned without acknowledgement, unrelated
changes were bundled in, and 'cleaned up' hides scope that a reviewer now has
to reverse-engineer instead of reviewing intentionally.

Corrected behavior: if extra cleanup seems valuable, stop and say so explicitly:
"I also noticed X is duplicated in 3 places — want me to extract it in a
follow-up, or is that out of scope for this task?"
```

## Checklist

- [ ] The task was restated with explicit acceptance criteria before any edit was made.
- [ ] Work was broken into small, independently verifiable steps.
- [ ] Each step was verified before moving to the next one.
- [ ] Any plan revision (due to new information) was made explicit, not silent.
- [ ] Blocked steps are labeled as such with a stated reason, not silently dropped.
- [ ] A final summary lists what changed and how it was verified.
- [ ] Any additional cleanup beyond the stated scope was proposed, not silently applied.
- [ ] The plan's status markers were kept current throughout, not reconstructed after the fact.

## Anti-patterns

- **Edit-everything-then-test-once** - Making sweeping changes across many files before running any verification, making it hard to isolate what broke.
- **Silent plan drift** - Quietly abandoning the stated plan mid-task without acknowledging the change, confusing anyone reviewing progress.
- **Verification theater** - Running an unrelated or trivial check and calling it 'verified' instead of the smallest test that would actually catch a regression.
- **Unbounded scope creep** - Using a bug fix task as an excuse to refactor unrelated modules without calling it out separately.
- **Invisible progress** - Doing multi-step work without ever externalizing the plan, so a reviewer cannot tell what is left.

## Verification

- A step-by-step log or plan exists showing what was done in what order.
- Each completed step has a corresponding verification action (test run, build, manual check).
- The final report distinguishes 'done', 'in progress', and 'blocked' items clearly.
- Re-reading the original task against the final summary confirms every acceptance criterion was addressed.

## References

- skills/00-core/context-gathering/SKILL.md
- skills/00-core/requirements-to-code-traceability/SKILL.md
- skills/70-quality/debugging-methodology/SKILL.md
- skills/10-planning/work-breakdown-and-estimation/SKILL.md
