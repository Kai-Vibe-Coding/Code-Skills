---
name: e2e-and-contract-testing
description: Use when verifying a complete user journey across a real UI and backend, or verifying that two independently deployed services agree on their API contract.
category: quality
tags: [e2e-testing, contract-testing, playwright]
maturity: stable
updated: 2026-08-21
---

## Purpose

E2E tests give the highest confidence that a system works as a whole but are the slowest and most brittle test type, so they must be used sparingly and deliberately. Contract testing solves a related but distinct problem — verifying that a consumer and provider service agree on an API shape — without needing a full E2E environment for every combination of service versions.

This skill covers both: selecting a small set of critical E2E user journeys, and using consumer-driven contract tests to catch breaking API changes between independently deployed services early.

## When to use / When NOT to use

**Use this skill when:**

- You need confidence that a critical, high-value user journey works across the full stack (UI, API, database).
- Two services are developed and deployed independently and need to agree on an API contract without a shared E2E environment.
- An E2E suite has become slow/flaky and needs to be pruned to only the highest-value journeys.

**Do NOT use this skill when:**

- The scenario can be verified at a lower test level (unit or integration) with equal confidence — prefer the cheaper option.
- You're testing internal implementation logic rather than a full user-facing journey or a cross-service contract.

## Prerequisites

- skills/70-quality/integration-testing/SKILL.md, since integration tests should cover most cross-boundary verification, leaving E2E for genuinely end-to-end concerns.
- skills/20-architecture/api-design-rest/SKILL.md for the API contracts being verified.

## Workflow

1. **Select only the highest-value critical user journeys for E2E coverage** - Login, checkout, core workflows — not every possible UI permutation.
2. **Run E2E tests against a realistic, isolated environment** - A dedicated staging-like environment or ephemeral preview environment, not directly against shared production.
3. **Use resilient selectors, not brittle CSS/XPath** - Target elements by accessible role/label/test-id, so tests survive unrelated styling changes.
4. **Avoid hard-coded waits** - Use the test framework's built-in auto-waiting/retry-assertions instead of Thread.Sleep/setTimeout, reducing flakiness.
5. **Keep E2E test data setup independent and idempotent** - Each test creates its own data via API calls or fixtures rather than depending on a specific pre-existing database state.
6. **Use consumer-driven contract tests between independently deployed services** - The consumer defines its expectations of the provider's API; the provider verifies it still satisfies all known consumer contracts.
7. **Run contract verification in each service's own pipeline** - The provider's CI verifies against all published consumer contracts before deploying, catching breaking changes before they reach production.
8. **Quarantine and fix flaky E2E tests immediately** - A flaky E2E test erodes trust fast; fix or remove it rather than letting it linger as a permanent 'known flaky' retry.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A user journey spans UI, API, and database and is business-critical | Write one focused E2E test for its happy path, using Playwright or an equivalent framework. |
| Two teams' services communicate via a REST/event API and deploy independently | Use consumer-driven contract testing (e.g. Pact) instead of relying on a shared E2E environment to catch mismatches. |
| An E2E test is testing an edge case better covered by an integration test | Move it down to integration/unit level; reserve E2E for genuinely full-stack, high-value journeys. |
| An E2E test fails intermittently with no code change | Treat it as a flakiness bug: check for missing wait conditions or shared test data races, don't just add a retry. |
| A provider service wants to change its API shape | Verify the change against all published consumer contracts in CI before merging, catching a breaking change before it ships. |

## Reference implementation

A resilient Playwright E2E test for a critical checkout journey:

```typescript
test('customer can complete checkout with a valid card', async ({ page }) => {
  await page.goto('/cart');
  await page.getByRole('button', { name: 'Checkout' }).click();

  await page.getByLabel('Card number').fill('4242424242424242');
  await page.getByLabel('Expiry').fill('12/30');
  await page.getByRole('button', { name: 'Pay now' }).click();

  await expect(page.getByRole('heading', { name: 'Order confirmed' }))
    .toBeVisible();
  await expect(page.getByTestId('order-id')).not.toBeEmpty();
});
```

- getByRole/getByLabel select elements the same way a real user (and assistive technology) would identify them, surviving unrelated CSS refactors.
- Playwright's expect().toBeVisible() auto-retries/waits, avoiding brittle hard-coded sleep calls.

### A consumer-driven contract test defining expectations of a provider API (TypeScript, Pact)

The consumer defines the interaction it expects; the provider verifies it in its own CI:

```typescript
await provider.addInteraction({
  state: 'an order with id 123 exists',
  uponReceiving: 'a request for order 123',
  withRequest: { method: 'GET', path: '/orders/123' },
  willRespondWith: {
    status: 200,
    body: { id: '123', status: like('Submitted') },
  },
});
// Generates a pact contract file the provider's pipeline verifies against.
```

## Checklist

- [ ] E2E tests cover only a small, deliberately chosen set of critical, high-value user journeys.
- [ ] Selectors target accessible roles/labels/test-ids, not brittle CSS classes or XPath.
- [ ] Tests use built-in auto-waiting/retry assertions instead of hard-coded sleeps.
- [ ] Each E2E test creates its own isolated test data rather than depending on shared pre-existing state.
- [ ] Cross-service API contracts are verified via consumer-driven contract tests, not solely relied on a shared E2E environment.
- [ ] Flaky E2E tests are fixed or removed promptly, not left as permanently-retried 'known flaky' tests.

## Anti-patterns

- **E2E-testing everything** - Writing an E2E test for every possible input variation instead of pushing detailed coverage down to unit/integration tests.
- **Brittle CSS/XPath selectors** - Selecting elements by deep CSS class chains that break on any unrelated styling refactor.
- **Hard-coded sleep calls** - Using Thread.Sleep(2000) to 'wait' for an async UI update instead of an explicit wait condition, causing flaky timing-dependent failures.
- **Shared mutable test data** - Multiple E2E tests depending on and mutating the same pre-seeded database row, causing order-dependent failures.
- **No contract testing between independently deployed services** - Relying only on manual coordination or a shared staging environment to catch API breaking changes between services, discovering mismatches in production instead.

## Verification

- The E2E suite covers a small, named list of critical user journeys, reviewed and kept intentionally short.
- Running the E2E suite repeatedly in CI produces consistent results with no unexplained intermittent failures.
- A provider service's CI verifies its API changes against all published consumer contracts before merge.
- A deliberately introduced breaking API change is caught by contract verification before reaching a shared environment.

## References

- skills/70-quality/integration-testing/SKILL.md
- skills/20-architecture/api-design-rest/SKILL.md
- Playwright and Pact documentation.
