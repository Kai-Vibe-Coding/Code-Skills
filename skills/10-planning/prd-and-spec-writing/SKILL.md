---
name: prd-and-spec-writing
description: Use when you have gathered requirements for a feature and need to turn them into a written product requirements document or technical spec before implementation begins.
category: planning
tags: [prd, specification, documentation]
maturity: stable
updated: 2026-08-21
---

## Purpose

A good PRD turns scattered conversations into a single source of truth that engineering, design, and stakeholders can align on before code is written. This skill defines a lightweight but complete PRD/spec structure and the process for writing and reviewing one.

It exists to prevent the two common failure modes: PRDs so vague they don't reduce ambiguity, and PRDs so heavyweight that nobody writes or reads them.

## When to use / When NOT to use

**Use this skill when:**

- A feature is complex enough to involve more than one engineer or more than a few days of work.
- Multiple teams or stakeholders need to agree on scope before implementation starts.
- The feature has non-trivial non-functional requirements (performance, security, compliance).
- You need a durable reference to check the shipped feature against later.

**Do NOT use this skill when:**

- The change is a small, single-owner bug fix or minor tweak.
- The team has already agreed on scope informally and formal documentation adds no value for a trivial change.

## Prerequisites

- Requirements gathered via skills/10-planning/requirements-elicitation/SKILL.md.
- templates/prd.template.md as the starting structure.
- Access to whoever needs to approve the PRD before implementation.

## Workflow

1. **Start from the template** - Copy templates/prd.template.md rather than inventing a new structure each time.
2. **Write the problem statement first** - State the user/business problem in 2-3 sentences before any solution details.
3. **Define goals and explicit non-goals** - List what this feature will and will not do, to bound scope early.
4. **Translate requirements into user stories** - Phrase functional needs as 'As a <persona>, I want <capability>, so that <benefit>'.
5. **Specify non-functional requirements with numbers** - Replace 'fast' and 'secure' with measurable targets like p95 latency or specific compliance standards.
6. **Define success metrics** - State how success will be measured after launch, with a baseline and target.
7. **Circulate for review** - Get explicit sign-off from engineering, design, and the requesting stakeholder before implementation starts.
8. **Keep it living but versioned** - Update the PRD as scope changes during implementation, noting what changed and why.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Feature is small and single-owner | Use a 1-page lightweight spec instead of the full PRD template. |
| Requirements are still shifting rapidly | Delay full PRD sign-off; use a short 'working draft' status until they stabilize. |
| Non-functional requirements are unclear | Escalate to skills/20-architecture/scalability-and-capacity-planning/SKILL.md before finalizing the PRD. |
| Stakeholders disagree on scope after the draft is shared | Resolve via an explicit decision recorded in the PRD, not by silently editing it later. |
| Feature touches compliance-sensitive data | Loop in skills/80-security/privacy-and-compliance-basics/SKILL.md before sign-off. |
| PRD keeps growing during review | Split it: keep the MVP scope in this PRD and move future ideas to a separate backlog doc. |
| Engineering feasibility is uncertain | Run a short technical spike before finalizing effort-sensitive requirements. |

## Reference implementation

Excerpt from a filled PRD following templates/prd.template.md:

```markdown
# PRD: Bulk Order Export

## Problem Statement
Finance manually exports orders one page at a time, costing ~4 hours/week and
causing errors during month-end close.

## Goals
- Export up to 100k orders to CSV in a single request.
- Reduce manual export time to under 5 minutes.

## Non-Goals
- Real-time export streaming (out of scope for v1).
- Export formats other than CSV.

## Requirements
### Functional
1. User can request an export for a date range and status filter.
2. Export runs asynchronously; user is notified via email when ready.

### Non-Functional
- Performance: export of 100k rows completes within 5 minutes.
- Security: only users with Finance.Export role may request exports.

## Success Metrics
| Metric | Baseline | Target |
|---|---|---|
| Manual export time | 4 hrs/week | < 30 min/week |
```

- Keep the functional requirement list numbered so it can be referenced directly in skills/00-core/requirements-to-code-traceability/SKILL.md.
- Non-functional requirements must have a number attached — 'fast' and 'secure' are not requirements.

### Lightweight one-page spec for a small feature

For small, single-owner work, use a trimmed-down alternative instead of the full PRD:

```markdown
# Spec: Add CSV column for order channel

Problem: Finance cannot distinguish web vs phone orders in exports.
Change: add an `order_channel` column to the existing CSV export.
Non-goals: no new filter UI in this iteration.
Acceptance: exported CSV includes `order_channel` with values web|phone|store.
Verified by: OrderExportTests.IncludesChannelColumn.
```

## Checklist

- [ ] The problem statement is written before any solution detail.
- [ ] Explicit non-goals are listed to bound scope.
- [ ] Every functional requirement is numbered and independently testable.
- [ ] Non-functional requirements have measurable targets, not vague adjectives.
- [ ] Success metrics have a stated baseline and target.
- [ ] The PRD was explicitly reviewed and approved by engineering and the requesting stakeholder.
- [ ] Open questions are listed rather than silently resolved.
- [ ] Scope changes during implementation are reflected back into the PRD with a changelog note.

## Anti-patterns

- **Solution-first PRDs** - Jumping straight to UI mockups or technical design without stating the underlying problem first.
- **Vague non-functional requirements** - Writing 'the system should be fast and secure' instead of measurable targets and standards.
- **Unbounded scope** - Omitting explicit non-goals, letting the feature quietly grow during implementation.
- **Write-once documents** - Treating the PRD as immutable after the kickoff meeting, letting it silently diverge from what is actually being built.
- **Sign-off theater** - Circulating a PRD for 'review' without any explicit approval step or recorded decision.
- **Requirement soup** - Mixing functional requirements, implementation details, and success metrics together with no clear structure.

## Verification

- A named approver for each key stakeholder group signed off on the PRD before implementation began.
- Every requirement can be traced to a code/test pair using skills/00-core/requirements-to-code-traceability/SKILL.md.
- Non-functional requirements are measurable and were actually tested against post-launch.
- Any scope change during implementation has a corresponding update in the PRD.

## References

- templates/prd.template.md
- skills/10-planning/requirements-elicitation/SKILL.md
- skills/10-planning/definition-of-ready-and-done/SKILL.md
- skills/00-core/requirements-to-code-traceability/SKILL.md
