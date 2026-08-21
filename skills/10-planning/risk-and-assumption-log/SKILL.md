---
name: risk-and-assumption-log
description: Use when a plan or PRD depends on unverified assumptions or carries risks that could derail delivery, and those need to be tracked visibly rather than discovered later.
category: planning
tags: [risk-management, assumptions, planning]
maturity: stable
updated: 2026-08-21
---

## Purpose

Unstated assumptions and untracked risks are a leading cause of late-stage surprises in software delivery. This skill provides a lightweight log format for recording assumptions, risks, and their mitigations so they are visible to the whole team and revisited as new information arrives.

It is deliberately simple: a living table, not a heavyweight risk-management process, designed to be updated in minutes during planning meetings.

## When to use / When NOT to use

**Use this skill when:**

- A plan depends on something outside the team's control (a third-party API, another team's delivery).
- You are estimating work with significant technical or requirements uncertainty.
- A stakeholder decision is pending and work is proceeding on a best guess in the meantime.
- A previous project failed due to an unmanaged risk and you want to avoid repeating it.

**Do NOT use this skill when:**

- The task is small, fully understood, and has no external dependencies or open questions.

## Prerequisites

- A draft plan or PRD to anchor the assumptions and risks against.
- A shared, visible place to maintain the log (ticket, wiki page, or PRD appendix).

## Workflow

1. **Brainstorm assumptions** - List everything the plan takes for granted: technical, resourcing, third-party, and timing assumptions.
2. **Brainstorm risks separately** - List things that could go wrong even if assumptions hold, e.g. a dependency being late or scope growing.
3. **Rate likelihood and impact** - Score each risk on rough likelihood and impact (Low/Medium/High) to prioritize attention.
4. **Assign a mitigation or contingency** - For medium/high risks, define what you will do if the risk materializes, not just hope it doesn't.
5. **Assign an owner** - Every open risk and assumption needs a named owner responsible for monitoring and resolving it.
6. **Review on a cadence** - Revisit the log at each planning checkpoint, closing resolved items and adding new ones.
7. **Escalate blocking risks early** - If a high-impact risk is close to materializing, raise it to stakeholders before it becomes a crisis.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Assumption is easy to verify quickly | Verify it immediately rather than logging it as an ongoing risk. |
| Risk has low likelihood and low impact | Log it for visibility but do not invest mitigation effort — accept it explicitly. |
| Risk has high likelihood or high impact | Define and, if cheap, implement a concrete mitigation or contingency plan now. |
| Risk depends on another team's delivery | Get an explicit commitment or fallback plan from that team, not just an assumption it will land on time. |
| An assumption turns out to be false mid-project | Update the plan immediately and communicate the impact, rather than continuing silently. |
| Risk log grows very long | Focus active discussion on Medium/High items; keep Low items archived but visible. |

## Reference implementation

A lightweight risk and assumption log format:

```text
Risk & Assumption Log — Bulk Order Export
-------------------------------------------
Assumptions:
A1: Third-party email service supports attachments up to 25MB. [Owner: BE] [Unverified]
A2: Finance team's export volume stays under 100k rows for the next 12 months. [Owner: PM]

Risks:
| ID | Risk                                   | Likelihood | Impact | Mitigation                          | Owner |
|----|-----------------------------------------|-----------|--------|--------------------------------------|-------|
| R1 | Export job times out for very large sets| Medium    | High   | Add chunked processing + retry       | BE    |
| R2 | Email provider rate-limits large sends   | Low       | Medium | Fallback: in-app download link       | BE    |
| R3 | Finance needs Excel not CSV (scope risk) | Medium    | Medium | Confirm format explicitly in PRD     | PM    |

Review cadence: revisit at each sprint planning; close items once verified/resolved.
```

- Convert 'Unverified' assumptions to either 'Confirmed' or a tracked risk as soon as they are checked.
- Do not let the log become a graveyard — actively close items each review cycle.

### Escalating a materializing risk

Example escalation message when a logged risk is about to become real:

```text
Subject: Risk R1 (export timeout) is materializing - needs a decision

Status: Load testing shows the export job times out around 60k rows,
below our 100k target (see R1 in the risk log).

Options:
  1. Ship with a documented 60k row limit for v1, raise it in v1.1 (recommended)
  2. Delay launch by 1 week to implement chunked processing now

Requesting a decision from: Product Owner, Eng Lead, by EOD Thursday.
```

## Checklist

- [ ] Assumptions and risks are logged separately with distinct handling.
- [ ] Every Medium/High risk has a named owner and a concrete mitigation or contingency.
- [ ] Unverified assumptions are flagged as such, not silently treated as fact.
- [ ] The log is reviewed on a regular cadence, not written once and forgotten.
- [ ] High-impact risks close to materializing were escalated to stakeholders proactively.
- [ ] Resolved risks/assumptions are marked closed rather than left stale.

## Anti-patterns

- **Silent assumptions** - Proceeding on unverified assumptions without ever writing them down, so no one notices when they are wrong.
- **Risk theater** - Logging risks once during kickoff and never revisiting them for the rest of the project.
- **Ownerless risks** - Listing risks with no assigned owner, so nobody actually monitors or mitigates them.
- **Hope as a strategy** - Identifying a high-impact risk but defining no mitigation or contingency plan at all.
- **Late escalation** - Sitting on a materializing high-impact risk until it becomes an emergency instead of raising it early.

## Verification

- Every assumption has a status: Confirmed, Unverified, or Invalidated.
- Every Medium/High risk has an owner and a stated mitigation.
- The log's last-updated date is recent relative to the project timeline, not stale.
- At least one planning checkpoint explicitly reviewed the log as an agenda item.

## References

- skills/10-planning/prd-and-spec-writing/SKILL.md
- skills/10-planning/architecture-decision-records/SKILL.md
- PMI, 'Risk Management' guidance adapted for lightweight software delivery.
