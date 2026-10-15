---
name: requirements-to-code-traceability
description: Use when you need to prove that every requirement, ticket, or acceptance criterion is actually implemented and tested somewhere in the codebase.
category: core
tags: [traceability, requirements, compliance]
maturity: stable
updated: 2026-08-21
---

## Purpose

Untraceable requirements silently disappear during implementation, causing missed acceptance criteria that surface only in production or during an audit.

This skill provides a lightweight way to link requirements to the code and tests that satisfy them, so gaps are visible before release rather than after, and so audits can be answered with evidence instead of memory.

## When to use / When NOT to use

**Use this skill when:**

- You are implementing a feature with multiple discrete acceptance criteria.
- The project is subject to audit, compliance, or contractual sign-off requirements.
- A PR needs to demonstrate which ticket items are actually addressed.
- A large feature is being built incrementally across several PRs and coverage must be tracked.

**Do NOT use this skill when:**

- The change is a trivial, single-criterion bug fix with no formal requirement document.
- The team has no requirement-tracking system at all and adding one is out of scope for this task.

## Prerequisites

- A source of requirements (ticket, PRD, or acceptance criteria list).
- skills/10-planning/prd-and-spec-writing/SKILL.md if the PRD itself still needs to be written.
- A test framework capable of naming/tagging individual test cases.

## Workflow

1. **List atomic requirements** - Break the PRD or ticket into individually testable statements, each with a stable ID (e.g. REQ-1).
2. **Map each requirement to code** - Identify the file(s)/class(es) that implement each requirement as you build it.
3. **Map each requirement to a test** - Ensure at least one automated test asserts the requirement's observable behavior.
4. **Maintain a traceability matrix** - Keep a simple table of requirement ID -> code location -> test ID, updated as work progresses.
5. **Flag orphans** - Any requirement with no code/test mapping, or any test with no requirement mapping, is a gap to resolve before release.
6. **Review the matrix before sign-off** - Walk the matrix with a reviewer or stakeholder to confirm every row is actually 'Done', not just claimed.
7. **Attach the matrix to the PR** - Include or link the traceability matrix so reviewers can confirm coverage without re-reading the whole diff.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Small bug fix, single criterion | Use an informal one-line trace in the PR description instead of a full matrix. |
| Regulated or contractual feature | Maintain a persistent traceability matrix file reviewed as part of sign-off. |
| Requirement changes mid-implementation | Update the requirement ID's description and re-verify its code/test mapping, do not silently drop it. |
| A requirement has no feasible automated test | Document the manual verification procedure explicitly in the matrix instead of leaving it blank. |
| Feature spans multiple PRs | Carry the matrix forward in the tracking issue and update it per PR rather than recreating it each time. |

## Reference implementation

A minimal traceability matrix that can live in a PR description or a docs file:

```text
| Req ID | Requirement                          | Code                         | Test                    | Status |
|--------|---------------------------------------|------------------------------|--------------------------|--------|
| REQ-1  | User can reset password via email     | AuthController.RequestReset   | AuthControllerTests.T1   | Done   |
| REQ-2  | Reset link expires after 30 minutes   | PasswordResetToken.IsExpired  | PasswordResetTokenTests  | Done   |
| REQ-3  | Rate limit reset requests per account | ResetRateLimiter              | ResetRateLimiterTests    | Gap    |
| REQ-4  | Reset events are audit logged         | AuditLogger.LogPasswordReset  | AuditLoggerTests         | Done   |

REQ-3 has code but no automated test yet - blocking release sign-off.

Sign-off note (attach to PR):
  4 of 4 requirements have code. 3 of 4 have passing automated tests.
  REQ-3 tracked as follow-up ticket JIRA-4821 before this feature can be marked done.
```

- Store the matrix in the PR description for small features, or a linked docs/traceability/<feature>.md for larger ones.
- Treat 'Gap' rows as release blockers unless explicitly and visibly waived by a decision-maker.

### Escalating an unresolved gap

Example note attached to a release sign-off request when a gap cannot be closed in time:

```text
Release sign-off request for v2.4.0:
  Coverage: 12/13 requirements have code + passing tests.
  Open gap: REQ-9 (bulk export rate limiting) has code but no automated test;
  manual test performed 2026-08-19 by QA, see JIRA-5102 for the automation follow-up.
  Requesting explicit waiver from: Release Owner, QA Lead.
  Waiver granted by: <name>, <date>. Follow-up ticket due: <sprint>.
```

## Checklist

- [ ] Every acceptance criterion has a stable requirement ID.
- [ ] Each requirement ID maps to at least one code location and one test.
- [ ] No requirement is marked 'done' without a corresponding passing test or documented manual check.
- [ ] The traceability matrix is attached to or linked from the PR.
- [ ] Any requirement that changed scope mid-implementation is reflected in the matrix.
- [ ] Gaps are tracked as follow-up tickets, not silently dropped.
- [ ] Any waived gap names an explicit approver and a due date for the follow-up.
- [ ] The matrix's requirement IDs match the IDs used in the originating ticket or PRD.

## Anti-patterns

- **Implicit coverage** - Assuming a requirement is covered because 'the tests probably exercise it' without an explicit mapping.
- **Matrix drift** - Writing the matrix once at the start and never updating it as implementation details change.
- **Test without requirement** - Adding tests for behavior that traces back to no stated requirement, inflating scope silently.
- **Requirement without test** - Marking a requirement 'done' purely because code was written, without proving the behavior via a test.
- **Silent gap waiving** - Shipping with an unresolved 'Gap' row without any stakeholder sign-off or tracked follow-up.

## Verification

- Every row in the traceability matrix has a non-empty code and test column, or an explicit documented exception.
- Running the mapped tests actually exercises the described requirement (spot-check a sample).
- A reviewer can answer 'is REQ-N done?' by reading the matrix alone.
- Any waived gap has a linked follow-up ticket and a named approver.

## References

- skills/10-planning/prd-and-spec-writing/SKILL.md
- skills/70-quality/test-case-design/SKILL.md
- ISO/IEC/IEEE 29148 — Requirements engineering traceability practices.
- skills/90-delivery/shipping-checklist/SKILL.md
