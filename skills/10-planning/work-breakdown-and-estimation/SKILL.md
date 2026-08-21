---
name: work-breakdown-and-estimation
description: Use when a feature or PRD needs to be broken into implementable tasks with size estimates before sprint or milestone planning.
category: planning
tags: [estimation, planning, wbs]
maturity: stable
updated: 2026-08-21
---

## Purpose

Large, unestimated units of work hide risk and make progress invisible until it is too late to adjust. This skill describes how to decompose a feature into small, independently deliverable tasks and produce estimates that are useful for planning without pretending to be precise.

It emphasizes relative sizing and explicit uncertainty over false-precision, single-number estimates that create unrealistic commitments.

## When to use / When NOT to use

**Use this skill when:**

- A PRD or epic needs to be turned into a sprint/milestone plan.
- Stakeholders are asking 'how long will this take' and a rough but defensible answer is needed.
- A task feels too large to safely implement, review, or test as a single unit.
- You need to identify which parts of a feature can be built in parallel.

**Do NOT use this skill when:**

- The work is a single, well-understood task with no meaningful sub-parts.
- Precise time estimates are not needed (e.g. pure exploratory research spikes) — timebox instead.

## Prerequisites

- A reviewed PRD or clear requirement list (skills/10-planning/prd-and-spec-writing/SKILL.md).
- Team velocity history or comparable past task data, if available.

## Workflow

1. **Decompose by vertical slice** - Split work into end-to-end slices that each deliver observable value, not by technical layer alone.
2. **Target 1-2 day tasks** - Break down any task estimated larger than roughly two days of focused work.
3. **Separate must-have from nice-to-have** - Tag each task against the PRD's goals vs non-goals so scope cuts are easy under pressure.
4. **Estimate relatively** - Use relative sizing (t-shirt sizes or story points) rather than false-precision hour estimates for uncertain work.
5. **Call out unknowns explicitly** - Flag tasks with high uncertainty and consider a time-boxed spike before committing an estimate.
6. **Sequence by dependency** - Identify which tasks block others and which can run in parallel across engineers.
7. **Review as a team** - Have more than one engineer sanity-check estimates, especially for unfamiliar areas.
8. **Track actuals vs estimates** - Record actual effort after completion to improve future estimation calibration.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Task has high technical uncertainty | Timebox a short spike first, then re-estimate with that information instead of guessing. |
| Task naturally spans multiple layers (API + DB + UI) | Split by vertical slice per capability rather than by layer, so each slice is independently testable. |
| Estimate significantly exceeds available time | Cut scope (defer nice-to-haves) rather than compressing the estimate artificially. |
| Team has little history with the tech stack | Widen the estimate range and flag it as low-confidence rather than presenting false precision. |
| Multiple engineers could work on it | Break work into parallelizable tasks with clear interface contracts between them. |
| A task keeps ballooning during breakdown | Split it further; if it still cannot go below ~2 days, treat it as its own mini-epic. |
| Stakeholders want a single delivery date | Give a range with a stated confidence level, not a false-precision point estimate. |

## Reference implementation

A work breakdown table combining vertical slices, sizing, and dependencies:

```text
Feature: Bulk Order Export (from PRD REQ-1..REQ-6)

| Task                                        | Slice type | Size | Depends on | Confidence |
|----------------------------------------------|-----------|------|------------|------------|
| Export request API + validation (REQ-1)       | vertical  | M    | -          | High       |
| Async export job + CSV generation (REQ-2)     | vertical  | L    | Task 1     | Medium     |
| Email notification on completion (REQ-2)      | vertical  | S    | Task 2     | High       |
| Role-based access check (REQ non-func: sec.)  | vertical  | S    | Task 1     | High       |
| Load test for 100k row export (REQ non-func)  | spike     | M    | Task 2     | Low        |

Sizes: S = <1 day, M = 1-2 days, L = 3-5 days (split further if larger).
Load test task is Low confidence -> timebox a 1-day spike before committing a firm size.
```

- Keep the breakdown table linked back to the PRD's requirement IDs for traceability.
- Re-run this breakdown whenever the PRD's scope changes materially.

### Splitting an oversized task

Example of decomposing a task that was initially too large to estimate confidently:

```text
Before: "Build export job" (estimated L, ~5 days, low confidence)

After splitting by vertical concern:
  1. CSV generation from an existing in-memory result set (S, high confidence)
  2. Chunked/streamed generation for large result sets (M, medium confidence)
  3. Background job scheduling + status tracking (M, high confidence)
  4. Failure/retry handling for partial export failures (S, medium confidence)

Each sub-task is now independently reviewable, testable, and estimable.
```

## Checklist

- [ ] Every task traces back to a specific PRD requirement or explicit technical necessity.
- [ ] No task is estimated larger than roughly two days without being split further.
- [ ] High-uncertainty tasks are flagged and have a spike planned before firm estimation.
- [ ] Dependencies between tasks are identified so parallel work is possible.
- [ ] Estimates use relative sizing or ranges, not false-precision single numbers for uncertain work.
- [ ] Must-have vs nice-to-have tasks are explicitly tagged for scope-cut decisions.
- [ ] A team review (not a single person) validated the breakdown and estimates.

## Anti-patterns

- **Layer-based decomposition** - Splitting tasks purely by technical layer (all backend, then all frontend) so nothing is demoable until the very end.
- **False precision** - Giving a single-number hour estimate for a task with significant unknowns instead of a range with a stated confidence level.
- **Giant tasks** - Leaving multi-week tasks unbroken, hiding risk and making progress invisible until it's nearly due.
- **Estimating in isolation** - One person estimating everything alone without any peer sanity-check, especially for unfamiliar work.
- **Ignoring dependencies** - Planning tasks without identifying blocking relationships, causing engineers to be idle or blocked mid-sprint.
- **No calibration loop** - Never comparing actual effort against estimates, so estimation accuracy never improves over time.

## Verification

- Every task in the plan maps to a PRD requirement or a stated technical necessity.
- No single task in the current sprint/milestone exceeds the team's agreed size ceiling.
- Dependency order was checked so no engineer is blocked without a fallback task.
- Post-completion, actual effort was recorded against the original estimate for calibration.

## References

- skills/10-planning/prd-and-spec-writing/SKILL.md
- skills/10-planning/definition-of-ready-and-done/SKILL.md
- Mike Cohn, 'Agile Estimating and Planning'.
