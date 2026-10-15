---
name: requirements-elicitation
description: Use when a feature request is vague or comes from a single stakeholder and you need to uncover the real needs, constraints, and edge cases before design begins.
category: planning
tags: [requirements, stakeholders, discovery]
maturity: stable
updated: 2026-08-21
---

## Purpose

Vague requirements produce rework, scope disputes, and features that miss the actual user need. This skill provides a structured way to interview stakeholders, surface hidden assumptions, and convert ambiguous requests into concrete, testable requirements.

It focuses on asking the right questions early, when changes are cheap, rather than discovering gaps during implementation or after release when changes are expensive.

## When to use / When NOT to use

**Use this skill when:**

- A stakeholder describes a feature in business terms without technical detail.
- A ticket says 'make it faster/better/easier' without a measurable target.
- Two stakeholders describe the same feature differently.
- You are about to write a PRD or spec and need raw material to work from.
- The request conflicts with, or overlaps, an existing feature.
- You suspect there are unstated non-functional requirements (performance, security, compliance).

**Do NOT use this skill when:**

- The requirement is already fully specified with clear acceptance criteria.
- You are fixing a well-understood bug with an obvious, unambiguous correct behavior.
- The change is a pure internal refactor with no external behavior change.

## Prerequisites

- Access to the requesting stakeholder(s) or their proxy (product manager, support lead).
- Basic understanding of the existing product/system the request relates to.
- skills/00-core/context-gathering/SKILL.md applied to the current system first.
- A place to record findings (ticket, doc, or PRD draft).

## Workflow

1. **Identify all stakeholders** - List everyone affected: requester, end users, support, compliance, ops — not just the loudest voice.
2. **Ask 'why' before 'what'** - Uncover the underlying problem or goal before accepting a proposed solution at face value.
3. **Use concrete scenarios** - Ask for specific examples ('walk me through the last time this went wrong') instead of abstract descriptions.
4. **Probe edge cases explicitly** - Ask about empty states, error states, concurrent use, and scale — these are rarely volunteered.
5. **Surface non-functional requirements** - Explicitly ask about performance, availability, security, and compliance constraints.
6. **Restate and confirm** - Play back your understanding in plain language and get explicit stakeholder confirmation.
7. **Document open questions separately** - Track unresolved ambiguities visibly instead of quietly picking an answer.
8. **Hand off to spec writing** - Feed confirmed requirements into skills/10-planning/prd-and-spec-writing/SKILL.md.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Stakeholder gives a solution, not a problem | Ask 'what problem does this solve for you' before accepting the proposed solution. |
| Two stakeholders disagree | Surface the disagreement explicitly and get a decision-maker to resolve it, rather than silently picking one side. |
| Stakeholder is unavailable for clarification | Document your best-effort assumption and flag it as unconfirmed, do not block indefinitely. |
| Request implies a large, multi-quarter effort | Break elicitation into phases: confirm the MVP scope first, defer edge cases to a follow-up round. |
| Non-functional requirements are never mentioned | Proactively ask about scale, latency, and security expectations rather than assuming 'default' is fine. |
| Requirement conflicts with a known technical constraint | Surface the conflict immediately rather than silently designing around it. |
| Elicitation reveals the request duplicates an existing feature | Point this out before further design work is invested. |

## Reference implementation

A structured interview script covering the most commonly missed areas:

```text
Requirements Elicitation Interview Guide
-----------------------------------------
1. Problem framing
   - What problem are you trying to solve? Who is affected, and how often?
   - What happens today without this change? What is the workaround?
2. Success criteria
   - How will you know this worked? What metric moves, and by how much?
3. Scenarios
   - Walk me through the last time this went wrong, step by step.
   - Who are the different types of users, and does each need something different?
4. Edge cases (ask explicitly, do not wait for volunteering)
   - What should happen with zero results / the first-ever use / concurrent use?
   - What is the expected behavior on error, timeout, or partial failure?
5. Non-functional requirements
   - Expected volume/scale? Peak load? Response time expectations?
   - Any compliance, audit, or data residency constraints?
6. Boundaries
   - What is explicitly out of scope for this iteration?
   - What existing feature might this overlap with or replace?

Output: a list of REQ-N statements plus an 'Open Questions' list of anything
unresolved, both fed into the PRD.
```

- Timebox elicitation sessions (30-45 minutes) and follow up in writing rather than trying to resolve everything live.
- Always send a written summary back to stakeholders for explicit confirmation before design starts.

### Turning a vague request into confirmed requirements

Before-and-after showing how elicitation converts a vague ask into testable requirements:

```text
Before (raw request): "Can we make the order search better? It's kind of slow
and people can't find what they need."

After elicitation:
  REQ-1: Search must return results in under 1s for a 500k-row order table (p95).
  REQ-2: Users must be able to filter by date range, status, and customer name.
  REQ-3: Empty search results must suggest removing the most restrictive filter.
  Open question: should search include archived (soft-deleted) orders? [Owner: PM]
```

## Checklist

- [ ] Every named stakeholder group was consulted or explicitly represented by a proxy.
- [ ] The underlying problem, not just the proposed solution, was captured.
- [ ] At least one concrete scenario/example was gathered per major requirement.
- [ ] Edge cases (empty, error, concurrent, scale) were explicitly asked about.
- [ ] Non-functional requirements were explicitly discussed, not assumed.
- [ ] A written summary was played back and confirmed by the stakeholder.
- [ ] Open questions are tracked visibly rather than silently resolved by guessing.
- [ ] Overlap with existing features was checked and called out if found.

## Anti-patterns

- **Accepting the first solution offered** - Taking a stakeholder's proposed implementation at face value instead of uncovering the underlying problem it is meant to solve.
- **Single-source requirements** - Gathering requirements from only the loudest or most senior stakeholder, missing conflicting needs from other affected groups.
- **Silent tie-breaking** - Quietly picking one interpretation when stakeholders disagree instead of escalating for an explicit decision.
- **Assuming defaults for non-functional requirements** - Never asking about scale, latency, or compliance and hoping the 'obvious' assumption is correct.
- **Skipping written confirmation** - Proceeding to design purely from a verbal conversation with no documented, confirmed summary.
- **Elicitation without boundaries** - Gathering an ever-expanding wish list without ever confirming what is explicitly out of scope.

## Verification

- A written requirements summary exists and was explicitly confirmed by the stakeholder(s).
- Each requirement traces back to a stated problem, not just a requested feature.
- Edge cases and non-functional requirements appear in the summary, not just happy-path behavior.
- Open questions are listed with an owner and are not blocking silently.
- The summary was checked against existing features for overlap or duplication.

## References

- skills/10-planning/prd-and-spec-writing/SKILL.md
- skills/10-planning/risk-and-assumption-log/SKILL.md
- Karl Wiegers, 'Software Requirements' — structured elicitation techniques.
- skills/00-core/requirements-to-code-traceability/SKILL.md
