---
name: architecture-decision-records
description: Use when making a significant, hard-to-reverse technical decision that future engineers will need context on, such as choosing a database, framework, or integration pattern.
category: planning
tags: [adr, documentation, decision-making]
maturity: stable
updated: 2026-08-21
---

## Purpose

Significant technical decisions made verbally or in chat are forgotten within months, causing teams to relitigate the same debate or misunderstand why a system looks the way it does. This skill defines when and how to write an Architecture Decision Record (ADR) that captures the context, the decision, and the trade-offs at the time it was made.

ADRs are lightweight by design: they are meant to be written in under an hour and read in under five minutes, not to be exhaustive design documents.

## When to use / When NOT to use

**Use this skill when:**

- You are choosing between two or more viable technical approaches with real trade-offs.
- The decision is expensive or slow to reverse once implemented (e.g. database choice, API contract).
- The decision affects multiple teams or will outlive the original author's context.
- A past decision is being revisited and its original rationale is unclear or undocumented.

**Do NOT use this skill when:**

- The decision is easily reversible and low-impact (e.g. naming a single internal variable).
- There is only one reasonable option with no real trade-off to record.

## Prerequisites

- templates/adr.template.md as the starting structure.
- A short list of the realistic options actually considered.
- Enough context (see skills/00-core/context-gathering/SKILL.md) to describe constraints accurately.

## Workflow

1. **Number and title the ADR** - Use a sequential ID (ADR-0001) and a short, specific title describing the decision, not the problem.
2. **Write the context section first** - Describe the forces at play (technical, business, team) neutrally, before naming a preferred option.
3. **List the options genuinely considered** - Include the rejected options with brief reasoning, not just the chosen one.
4. **State the decision plainly** - Write the decision in one or two sentences in active voice: 'We will use PostgreSQL for...'
5. **Document consequences honestly** - List both positive outcomes and real trade-offs/costs accepted by making this choice.
6. **Set the status** - Mark it Proposed until reviewed, then Accepted; mark old ADRs Superseded rather than deleting them.
7. **Store it durably and discoverably** - Keep ADRs in a consistent location (e.g. docs/adr/) referenced from related code or READMEs.
8. **Link forward and backward** - When superseding a decision, link the new ADR to the old one and vice versa.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Decision is easily reversible | Skip the ADR; a code comment or PR description is sufficient. |
| Decision is contentious among the team | Write the ADR to force explicit trade-off comparison rather than resolving it informally in chat. |
| A prior ADR's assumptions have changed | Write a new ADR that explicitly supersedes the old one instead of editing history silently. |
| Decision spans multiple related choices | Write one ADR per independently reversible decision rather than one giant ADR. |
| No real alternative was considered | Skip the ADR, or note explicitly 'no viable alternative existed' rather than inventing false options. |
| Decision needs executive/stakeholder sign-off | Route the ADR through the same approval path as skills/10-planning/prd-and-spec-writing/SKILL.md. |

## Reference implementation

Filled example following templates/adr.template.md:

```markdown
# ADR-0007: Use PostgreSQL as the primary datastore for the Orders service

- Status: Accepted
- Date: 2026-08-10
- Deciders: Backend Guild

## Context
Orders service needs strong consistency for inventory decrement and supports
up to 5k orders/minute at peak. Team has strong SQL experience; NoSQL options
were considered for horizontal write scale that we do not currently need.

## Decision
We will use PostgreSQL (managed, single primary with read replicas) as the
primary datastore for the Orders service.

## Considered Options
1. PostgreSQL - strong consistency, team familiarity, mature tooling.
2. DynamoDB - higher write scale, but eventual consistency complicates inventory.
3. MongoDB - flexible schema, but weaker transactional guarantees for this use case.

## Consequences
Positive: strong consistency simplifies inventory logic; team can move fast.
Negative: horizontal write scaling requires future sharding work if volume 10x's.
```

- Keep the 'Considered Options' section honest — including the ones rejected is what makes an ADR useful later.
- Revisit ADRs during major re-architecture work rather than assuming they are still valid forever.

### Superseding an old ADR

How to link a new decision back to the one it replaces:

```markdown
# ADR-0014: Migrate Orders service from PostgreSQL to CockroachDB

- Status: Accepted
- Supersedes: ADR-0007

## Context
Order volume grew 12x since ADR-0007; single-primary PostgreSQL write
throughput is now the top scaling bottleneck.

## Decision
We will migrate to CockroachDB for horizontally scalable writes.

(ADR-0007 updated to add: "Status: Superseded by ADR-0014".)
```

## Checklist

- [ ] The ADR has a sequential ID and a decision-focused title.
- [ ] Context is described neutrally before the decision is stated.
- [ ] At least one genuinely rejected alternative is documented with reasoning.
- [ ] The decision itself is a single clear, active-voice statement.
- [ ] Both positive and negative consequences are documented honestly.
- [ ] The ADR's status (Proposed/Accepted/Superseded) is current.
- [ ] Superseding ADRs link to the ADRs they replace, and vice versa.

## Anti-patterns

- **Decision-only ADRs** - Recording only the chosen option with no context or rejected alternatives, making the record useless for future reconsideration.
- **Editing history** - Modifying an old ADR to reflect a new decision instead of writing a new one that supersedes it.
- **Sales-pitch ADRs** - Listing only positive consequences and omitting real trade-offs or costs accepted.
- **ADR sprawl** - Writing an ADR for every trivial, reversible choice, diluting the signal of the ones that actually matter.
- **Orphaned ADRs** - Storing ADRs somewhere no one will find them, disconnected from the code or docs they explain.

## Verification

- A new engineer reading the ADR alone can understand why the decision was made without asking anyone.
- The ADR's status reflects reality (not stuck as 'Proposed' long after implementation).
- Any decision it supersedes is explicitly linked and marked Superseded.

## References

- templates/adr.template.md
- Michael Nygard, 'Documenting Architecture Decisions' (original ADR concept).
- skills/20-architecture/system-design-process/SKILL.md
