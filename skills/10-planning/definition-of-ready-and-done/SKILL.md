---
name: definition-of-ready-and-done
description: Use when a team needs explicit, shared criteria for when a work item is ready to start and when it is truly finished, to avoid starting underspecified work or shipping incomplete features.
category: planning
tags: [dor, dod, agile, quality-gates]
maturity: stable
updated: 2026-08-21
---

## Purpose

Teams without an explicit Definition of Ready (DoR) start work on underspecified tickets, causing mid-sprint churn. Teams without an explicit Definition of Done (DoD) ship features that are 'code complete' but missing tests, docs, or monitoring. This skill defines both gates concretely and shows how to apply them consistently.

DoR and DoD are team-level contracts: once agreed, they should be enforced the same way for every ticket, not applied selectively based on deadline pressure.

## When to use / When NOT to use

**Use this skill when:**

- A team is repeatedly starting work that turns out to be underspecified mid-sprint.
- Features are marked 'done' but later found missing tests, docs, or monitoring.
- A new team is being formed and needs a shared quality bar from day one.
- You are reviewing whether a ticket can move into the next stage of a workflow (backlog -> sprint -> done).

**Do NOT use this skill when:**

- The team already has a documented, working DoR/DoD and this ticket simply needs to be checked against it.
- The work is a single-person spike explicitly exempted from normal DoD (e.g. throwaway prototype).

## Prerequisites

- Team agreement on what belongs in DoR and DoD (this is a one-time setup cost).
- A ticketing system or checklist mechanism to attach these criteria to work items.

## Workflow

1. **Draft the Definition of Ready** - List the minimum information a ticket must have before it can be pulled into a sprint (acceptance criteria, estimate, dependencies known).
2. **Draft the Definition of Done** - List everything required beyond 'code compiles': tests, docs, code review, monitoring, deployed and verified.
3. **Socialize and agree as a team** - Review both definitions with the whole team and adjust until everyone will actually honor them.
4. **Attach the checklist to the workflow** - Add DoR as a gate before 'sprint start' and DoD as a gate before 'done' in the ticketing tool.
5. **Apply consistently** - Reject tickets that fail DoR back to refinement; reject 'done' claims that fail DoD back to in-progress.
6. **Revisit periodically** - Update DoR/DoD as the team matures — e.g. adding accessibility checks once that becomes a standing concern.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Ticket lacks clear acceptance criteria | Fails DoR — send back to refinement before it enters a sprint. |
| Feature works but has no automated test | Fails DoD — not shippable as 'done' regardless of deadline pressure. |
| A story is an exploratory spike | Apply a reduced DoD explicitly agreed in advance (e.g. 'no production code required'), not the full checklist. |
| Team is under deadline pressure to skip DoD items | Make the trade-off explicit and get a named approver to accept the risk, rather than silently lowering the bar. |
| DoR/DoD items feel irrelevant for a specific ticket type | Adjust the team-level definition explicitly rather than ignoring it case-by-case. |

## Reference implementation

Example Definition of Ready and Definition of Done for a backend team:

```text
Definition of Ready (before a ticket enters a sprint)
-------------------------------------------------------
[ ] Problem/goal stated in one sentence
[ ] Acceptance criteria are specific and testable
[ ] Dependencies (other teams, external services) identified
[ ] Rough size estimate agreed (see work-breakdown-and-estimation)
[ ] UX/API contract available if the ticket involves a user-facing or API change

Definition of Done (before a ticket is marked done)
-------------------------------------------------------
[ ] Code implements all stated acceptance criteria
[ ] Automated tests cover the acceptance criteria (unit + integration as applicable)
[ ] Code reviewed and approved by at least one other engineer
[ ] Documentation updated (README, API docs, or runbook as applicable)
[ ] Deployed to at least staging and manually verified
[ ] Monitoring/alerting in place for new failure modes introduced
[ ] No known regressions in existing automated test suite
```

- Keep both lists short (5-8 items); a checklist nobody reads provides no value.
- Print the DoD on the PR template so it is checked at the natural point of submission.

### Handling a DoD exception explicitly

Example of an explicit, tracked exception instead of silently lowering the bar:

```text
Ticket: ORD-482 Add order channel column to export

DoD exception requested: ship without a staging deploy due to environment outage.
Approved by: Eng Lead (2026-08-15).
Follow-up: verify in staging within 24h of environment restoration, tracked as
ORD-483, blocking the next release until confirmed.
```

## Checklist

- [ ] The team has an explicitly agreed, written DoR and DoD (not tribal knowledge).
- [ ] Tickets failing DoR are sent back to refinement rather than started anyway.
- [ ] Work claiming 'done' is checked against every DoD item, not just 'code compiles'.
- [ ] Any explicit exception (e.g. reduced DoD for a spike) is agreed in advance, not applied retroactively.
- [ ] DoR/DoD are revisited periodically as the team's standards evolve.

## Anti-patterns

- **Tribal knowledge DoD** - Relying on 'everyone knows what done means' instead of a written, agreed checklist.
- **Selective enforcement** - Applying DoD strictly for some tickets but waiving it silently under deadline pressure for others.
- **DoR as a formality** - Rubber-stamping tickets into a sprint without actually checking acceptance criteria are testable.
- **Done means merged** - Treating a merged PR as 'done' without deployment, verification, or monitoring in place.
- **Static definitions** - Never updating DoR/DoD even as the team learns painful lessons that should be codified.

## Verification

- A sample of recently started tickets shows each passed the team's DoR at start time.
- A sample of recently closed tickets shows each satisfies every DoD item.
- Any DoD exception applied has a recorded, explicit approval.

## References

- skills/10-planning/work-breakdown-and-estimation/SKILL.md
- skills/90-delivery/shipping-checklist/SKILL.md
- Scrum Guide — Definition of Done concept.
