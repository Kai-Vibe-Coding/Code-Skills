---
name: test-strategy
description: Use when defining what kinds of tests a project needs, in what proportion, and at which pipeline stage they should run.
category: quality
tags: [test-strategy, test-pyramid, quality]
maturity: stable
updated: 2026-08-21
---

## Purpose

Without a deliberate test strategy, teams either over-invest in slow, brittle E2E tests or under-invest in fast unit tests, producing a suite that's both slow and unreliable. This skill establishes the test pyramid as a guiding shape — many fast unit tests, fewer integration tests, fewest E2E tests — and maps each test type to the confidence and feedback speed it provides.

It also covers how a test strategy should be documented and revisited as the codebase evolves, rather than decided once and never reconsidered.

## When to use / When NOT to use

**Use this skill when:**

- You are starting a new project and need to establish its overall testing approach.
- An existing test suite is slow, flaky, or gives the team little confidence despite high coverage numbers.
- You are deciding what kind of test to write for a specific new piece of functionality.

**Do NOT use this skill when:**

- You need guidance on writing a specific unit test's structure — see skills/70-quality/unit-testing-dotnet/SKILL.md or skills/70-quality/test-case-design/SKILL.md instead.
- The question is about a specific test framework's syntax rather than overall strategy.

## Prerequisites

- skills/70-quality/test-case-design/SKILL.md for how individual test cases should be designed.
- skills/60-devops/ci-cd-pipelines/SKILL.md for where each test type runs in the pipeline.

## Workflow

1. **Shape the suite like a pyramid** - Many fast, isolated unit tests at the base; fewer integration tests; a small number of E2E tests at the top.
2. **Match test type to what needs verifying** - Unit tests verify logic in isolation; integration tests verify component boundaries (DB, HTTP); E2E tests verify critical user journeys end-to-end.
3. **Define what 'critical path' means for E2E coverage** - Only the handful of highest-value user journeys (checkout, login) warrant E2E tests; don't E2E-test every edge case.
4. **Run fast tests on every push, slow tests less frequently** - Unit tests on every commit; integration/E2E tests on PR merge or a scheduled cadence, per skills/60-devops/ci-cd-pipelines/SKILL.md.
5. **Track flaky tests as a first-class defect** - A flaky test undermines trust in the whole suite; quarantine and fix it promptly rather than ignoring reruns.
6. **Measure meaningful coverage, not just percentage** - Track coverage of critical logic paths and mutation-testing signal over raw line-coverage percentage chasing.
7. **Document the strategy and revisit it periodically** - Write down the intended test-type mix and reasoning; revisit it if the codebase's risk profile changes significantly.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Verifying a pure business rule/calculation | Write a unit test — fast, isolated, no I/O. |
| Verifying a repository correctly persists and retrieves data | Write an integration test against a real (or containerized) database. |
| Verifying the checkout flow works end-to-end across UI, API, and payment | Write one E2E test for the critical happy path, not exhaustive E2E coverage of every variation. |
| A test suite is slow and blocking CI feedback | Rebalance toward more unit tests and fewer, more targeted integration/E2E tests. |
| Coverage percentage is high but bugs still slip through | Review whether tests actually assert meaningful behavior, or investigate mutation testing to find weak assertions. |

## Reference implementation

The test pyramid shape and where each layer runs in the pipeline:

```text
        /\
       /E2E\        <- few, slow, highest confidence for critical user journeys
      /------\         runs on PR merge / nightly
     /Integr. \    <- moderate count, verifies component boundaries (DB, HTTP, queues)
    /----------\      runs on every PR
   /   Unit     \  <- many, fast, isolated logic verification
  /--------------\    runs on every push/commit

Guideline ratio (adjust per codebase): ~70% unit, ~20% integration, ~10% E2E.
```

- The ratio is a guideline, not a strict rule — a data-heavy service may lean more integration-test-heavy; the shape (fewer tests as you go up) should still hold.
- Running tests at different pipeline stages balances fast feedback against full-confidence coverage before deploy.

### A test-type decision recorded alongside a feature (Markdown note)

Documenting why a specific test type was chosen for a change:

```markdown
## Test approach: Order discount calculation
- Unit tests: all discount rule combinations (percentage, fixed, tiered) - fast, exhaustive.
- Integration test: one test confirming the discount is persisted correctly with the order.
- No E2E test added: covered by the existing checkout E2E happy-path test already.
```

## Checklist

- [ ] The test suite's overall shape resembles a pyramid: many unit tests, fewer integration, fewest E2E.
- [ ] Each new piece of functionality's test type is chosen deliberately based on what needs verifying.
- [ ] Fast tests run on every push; slower tests run at a less frequent, still regular cadence.
- [ ] Flaky tests are tracked and fixed promptly, not silently retried and ignored.
- [ ] Coverage is evaluated for meaningfulness (critical paths, mutation signal), not chased as a raw percentage target.
- [ ] The test strategy is documented and revisited as the project's risk profile evolves.

## Anti-patterns

- **Ice cream cone anti-pattern** - A test suite with mostly slow E2E tests and few unit tests, making the suite slow, flaky, and hard to maintain.
- **100% E2E coverage aspiration** - Attempting to E2E-test every edge case instead of pushing detailed logic verification down to unit tests.
- **Chasing coverage percentage** - Writing tests that execute code without meaningfully asserting behavior, just to inflate a coverage number.
- **Ignoring flaky tests** - Treating a flaky test as background noise to retry rather than a real defect undermining trust in the suite.
- **One-time strategy, never revisited** - Deciding on a test approach once at project start and never reconsidering it as the codebase and risk profile change.

## Verification

- A test-count report shows the suite's shape roughly follows the intended pyramid ratio.
- CI pipeline timing confirms fast tests provide feedback within a target time budget on every push.
- No test in the suite has an open, ignored flakiness ticket older than an agreed threshold.
- A mutation testing run (or targeted review) confirms critical logic paths have meaningful, not just present, test coverage.

## References

- skills/70-quality/test-case-design/SKILL.md
- skills/70-quality/unit-testing-dotnet/SKILL.md
- skills/70-quality/integration-testing/SKILL.md
- skills/70-quality/e2e-and-contract-testing/SKILL.md
- Martin Fowler — Test Pyramid.
