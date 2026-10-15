---
name: shipping-checklist
description: Use when preparing to ship a feature or release to production to confirm testing, observability, rollback, and documentation are all in place before go-live.
category: delivery
tags: [release, shipping, checklist]
maturity: stable
updated: 2026-08-21
---

## Purpose

A feature that's functionally complete isn't necessarily ready to ship — observability, rollback plans, and documentation are just as critical to a safe release. This skill provides a structured pre-launch checklist tying together the testing, observability, and release practices covered across other skills into a single go/no-go gate.

## When to use / When NOT to use

**Use this skill when:**

- You are preparing to release a feature or deploy a change to production.
- You need a consistent go/no-go gate for a release readiness review.
- A retrospective on a past incident reveals a gap in the pre-launch process.

**Do NOT use this skill when:**

- You need the detailed mechanics of a specific release strategy (canary, blue-green) — see skills/60-devops/release-strategies/SKILL.md instead.
- The change is a trivial, low-risk internal fix with no user-facing impact and an established fast-track process.

## Prerequisites

- skills/60-devops/release-strategies/SKILL.md and skills/60-devops/observability/SKILL.md for the underlying mechanisms this checklist verifies are in place.
- skills/70-quality/test-strategy/SKILL.md for the testing coverage expected before release.

## Workflow

1. **Confirm test coverage matches the risk of the change** - Verify unit, integration, and any needed end-to-end tests exist and pass, per skills/70-quality/test-strategy/SKILL.md.
2. **Confirm observability is in place for the new behavior** - Ensure logs, metrics, and traces exist for the new code paths, and dashboards/alerts are updated per skills/60-devops/observability/SKILL.md.
3. **Confirm a rollback plan exists and is tested** - Verify the deployment can be rolled back quickly, and that any accompanying data migration is backward compatible during the transition.
4. **Confirm feature flags gate risky behavior where applicable** - New, higher-risk behavior ships behind a flag that can be disabled without a redeploy, per skills/30-backend/configuration-and-feature-flags/SKILL.md.
5. **Confirm documentation is updated** - README, runbooks, and API references reflect the new behavior, per skills/90-delivery/technical-documentation/SKILL.md.
6. **Confirm on-call/support readiness** - The on-call team knows the change is shipping, what to watch for, and how to respond to related alerts.
7. **Choose an appropriate release strategy for the risk level** - Select canary, blue-green, or a straightforward rolling deploy based on blast-radius considerations from skills/60-devops/release-strategies/SKILL.md.
8. **Verify capacity and performance impact is understood** - Confirm the change was load-tested if it affects a hot path, per skills/70-quality/performance-and-load-testing/SKILL.md.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A feature has no automated test coverage for its main path | Do not ship; add the missing coverage first per skills/70-quality/test-strategy/SKILL.md. |
| A change modifies a hot, high-traffic code path | Require load testing evidence per skills/70-quality/performance-and-load-testing/SKILL.md before shipping. |
| A change has genuinely no safe rollback path (e.g. an irreversible data migration) | Split the release into reversible steps (expand/contract pattern) per skills/50-database/migrations-and-zero-downtime-schema-change/SKILL.md rather than shipping an irreversible change directly. |
| A risky new behavior is ready but not fully validated | Ship it behind a feature flag defaulted off, enabling gradual rollout rather than an all-or-nothing launch. |
| The on-call team wasn't informed of an upcoming risky release | Delay the release until on-call is briefed, since undetected/unexplained alerts during the release window slow incident response. |

## Reference implementation

A release readiness checklist used as a pre-launch gate:

```markdown
## Shipping Checklist: Discount Code Feature

- [x] Unit and integration tests cover the discount calculation logic
- [x] Load test confirms no regression on the checkout hot path
- [x] New metrics (`discount_applied_total`, `discount_errors_total`) added to dashboard
- [x] Alert configured for elevated discount error rate
- [x] Feature flag `discount-codes-v2` defaults to off, enabling gradual rollout
- [x] Rollback verified: disabling the flag reverts behavior with no redeploy needed
- [x] README and API reference updated with new discount code endpoint
- [x] On-call briefed on the release window and what to watch for
```

- Every item ties to a concrete, verifiable artifact (a test run, a dashboard panel, a flag state) rather than a subjective judgment call.
- The feature flag item enables a fast, redeploy-free rollback path independent of the underlying code deployment.

### A go/no-go decision table for release readiness reviews (Markdown)

Structuring the final go/no-go decision explicitly:

```markdown
| Criterion              | Status | Blocking? |
|--------------------------|--------|-----------|
| Test coverage adequate    | Pass   | Yes       |
| Observability in place    | Pass   | Yes       |
| Rollback plan verified     | Pass   | Yes       |
| Documentation updated      | Pass   | No        |

**Decision:** GO - all blocking criteria pass; documentation gap tracked as fast-follow.
```

## Checklist

- [ ] Test coverage matches the risk of the change and all relevant tests pass.
- [ ] Observability (logs, metrics, traces, dashboards, alerts) is in place for the new behavior.
- [ ] A tested rollback plan exists, including handling for any accompanying data migration.
- [ ] Risky new behavior ships behind a feature flag where appropriate for gradual rollout.
- [ ] Documentation (README, runbooks, API references) reflects the new behavior.
- [ ] On-call/support is briefed on the release window and what to watch for.

## Anti-patterns

- **Shipping on 'it works on my machine'** - Releasing a change with no automated test evidence, relying solely on manual local verification.
- **No rollback plan** - Deploying a change with no verified way to revert it quickly if something goes wrong in production.
- **Blind spots in observability** - Shipping new behavior with no corresponding metrics or logs, making it impossible to detect issues after launch.
- **Silent on-call handoff** - Releasing a risky change without informing the on-call team, leaving them to diagnose unexplained alerts from a first-hand surprise.
- **Treating the checklist as a rubber stamp** - Checking every box without verifying the underlying evidence actually exists, turning the gate into theater.

## Verification

- A sample release shows every checklist item backed by a verifiable artifact (test run link, dashboard panel, flag configuration).
- A rollback drill for a recent release completed successfully within the expected time window.
- Post-release monitoring during the release window shows relevant new metrics reporting as expected.
- On-call handoff notes for recent releases show the team was briefed ahead of the deployment window.

## References

- skills/60-devops/release-strategies/SKILL.md
- skills/60-devops/observability/SKILL.md
- skills/70-quality/test-strategy/SKILL.md
- skills/90-delivery/technical-documentation/SKILL.md
