SKILLS = [
    dict(
        dir="70-quality", slug="e2e-and-contract-testing", category="quality",
        tags=["e2e-testing", "contract-testing", "playwright"],
        desc="Use when verifying a complete user journey across a real UI and backend, or verifying that two independently deployed services agree on their API contract.",
        purpose=[
            "E2E tests give the highest confidence that a system works as a whole but are the slowest and "
            "most brittle test type, so they must be used sparingly and deliberately. Contract testing solves "
            "a related but distinct problem — verifying that a consumer and provider service agree on an API "
            "shape — without needing a full E2E environment for every combination of service versions.",
            "This skill covers both: selecting a small set of critical E2E user journeys, and using "
            "consumer-driven contract tests to catch breaking API changes between independently deployed "
            "services early.",
        ],
        when_use=[
            "You need confidence that a critical, high-value user journey works across the full stack (UI, API, database).",
            "Two services are developed and deployed independently and need to agree on an API contract without a shared E2E environment.",
            "An E2E suite has become slow/flaky and needs to be pruned to only the highest-value journeys.",
        ],
        when_not=[
            "The scenario can be verified at a lower test level (unit or integration) with equal confidence — prefer the cheaper option.",
            "You're testing internal implementation logic rather than a full user-facing journey or a cross-service contract.",
        ],
        prereqs=[
            "skills/70-quality/integration-testing/SKILL.md, since integration tests should cover most cross-boundary verification, leaving E2E for genuinely end-to-end concerns.",
            "skills/20-architecture/api-design-rest/SKILL.md for the API contracts being verified.",
        ],
        workflow=[
            ("Select only the highest-value critical user journeys for E2E coverage", "Login, checkout, core workflows — not every possible UI permutation."),
            ("Run E2E tests against a realistic, isolated environment", "A dedicated staging-like environment or ephemeral preview environment, not directly against shared production."),
            ("Use resilient selectors, not brittle CSS/XPath", "Target elements by accessible role/label/test-id, so tests survive unrelated styling changes."),
            ("Avoid hard-coded waits", "Use the test framework's built-in auto-waiting/retry-assertions instead of Thread.Sleep/setTimeout, reducing flakiness."),
            ("Keep E2E test data setup independent and idempotent", "Each test creates its own data via API calls or fixtures rather than depending on a specific pre-existing database state."),
            ("Use consumer-driven contract tests between independently deployed services", "The consumer defines its expectations of the provider's API; the provider verifies it still satisfies all known consumer contracts."),
            ("Run contract verification in each service's own pipeline", "The provider's CI verifies against all published consumer contracts before deploying, catching breaking changes before they reach production."),
            ("Quarantine and fix flaky E2E tests immediately", "A flaky E2E test erodes trust fast; fix or remove it rather than letting it linger as a permanent 'known flaky' retry."),
        ],
        decision=[
            ("A user journey spans UI, API, and database and is business-critical", "Write one focused E2E test for its happy path, using Playwright or an equivalent framework."),
            ("Two teams' services communicate via a REST/event API and deploy independently", "Use consumer-driven contract testing (e.g. Pact) instead of relying on a shared E2E environment to catch mismatches."),
            ("An E2E test is testing an edge case better covered by an integration test", "Move it down to integration/unit level; reserve E2E for genuinely full-stack, high-value journeys."),
            ("An E2E test fails intermittently with no code change", "Treat it as a flakiness bug: check for missing wait conditions or shared test data races, don't just add a retry."),
            ("A provider service wants to change its API shape", "Verify the change against all published consumer contracts in CI before merging, catching a breaking change before it ships."),
        ],
        code_lang="typescript",
        code_intro="A resilient Playwright E2E test for a critical checkout journey:",
        code=(
            "test('customer can complete checkout with a valid card', async ({ page }) => {\n"
            "  await page.goto('/cart');\n"
            "  await page.getByRole('button', { name: 'Checkout' }).click();\n"
            "\n"
            "  await page.getByLabel('Card number').fill('4242424242424242');\n"
            "  await page.getByLabel('Expiry').fill('12/30');\n"
            "  await page.getByRole('button', { name: 'Pay now' }).click();\n"
            "\n"
            "  await expect(page.getByRole('heading', { name: 'Order confirmed' }))\n"
            "    .toBeVisible();\n"
            "  await expect(page.getByTestId('order-id')).not.toBeEmpty();\n"
            "});\n"
        ),
        code_notes=[
            "getByRole/getByLabel select elements the same way a real user (and assistive technology) would identify them, surviving unrelated CSS refactors.",
            "Playwright's expect().toBeVisible() auto-retries/waits, avoiding brittle hard-coded sleep calls.",
        ],
        code2_heading="A consumer-driven contract test defining expectations of a provider API (TypeScript, Pact)",
        code2=("typescript",
            "The consumer defines the interaction it expects; the provider verifies it in its own CI:",
            "await provider.addInteraction({\n"
            "  state: 'an order with id 123 exists',\n"
            "  uponReceiving: 'a request for order 123',\n"
            "  withRequest: { method: 'GET', path: '/orders/123' },\n"
            "  willRespondWith: {\n"
            "    status: 200,\n"
            "    body: { id: '123', status: like('Submitted') },\n"
            "  },\n"
            "});\n"
            "// Generates a pact contract file the provider's pipeline verifies against.\n"
        ),
        checklist=[
            "E2E tests cover only a small, deliberately chosen set of critical, high-value user journeys.",
            "Selectors target accessible roles/labels/test-ids, not brittle CSS classes or XPath.",
            "Tests use built-in auto-waiting/retry assertions instead of hard-coded sleeps.",
            "Each E2E test creates its own isolated test data rather than depending on shared pre-existing state.",
            "Cross-service API contracts are verified via consumer-driven contract tests, not solely relied on a shared E2E environment.",
            "Flaky E2E tests are fixed or removed promptly, not left as permanently-retried 'known flaky' tests.",
        ],
        antipatterns=[
            ("E2E-testing everything", "Writing an E2E test for every possible input variation instead of pushing detailed coverage down to unit/integration tests."),
            ("Brittle CSS/XPath selectors", "Selecting elements by deep CSS class chains that break on any unrelated styling refactor."),
            ("Hard-coded sleep calls", "Using Thread.Sleep(2000) to 'wait' for an async UI update instead of an explicit wait condition, causing flaky timing-dependent failures."),
            ("Shared mutable test data", "Multiple E2E tests depending on and mutating the same pre-seeded database row, causing order-dependent failures."),
            ("No contract testing between independently deployed services", "Relying only on manual coordination or a shared staging environment to catch API breaking changes between services, discovering mismatches in production instead."),
        ],
        verification=[
            "The E2E suite covers a small, named list of critical user journeys, reviewed and kept intentionally short.",
            "Running the E2E suite repeatedly in CI produces consistent results with no unexplained intermittent failures.",
            "A provider service's CI verifies its API changes against all published consumer contracts before merge.",
            "A deliberately introduced breaking API change is caught by contract verification before reaching a shared environment.",
        ],
        references=[
            "skills/70-quality/integration-testing/SKILL.md",
            "skills/20-architecture/api-design-rest/SKILL.md",
            "Playwright and Pact documentation.",
        ],
    ),
    dict(
        dir="70-quality", slug="performance-and-load-testing", category="quality",
        tags=["load-testing", "performance-testing", "k6"],
        desc="Use when you need to verify a system meets its latency and throughput requirements under realistic and peak load before it reaches production.",
        purpose=[
            "Functional tests confirm correctness but say nothing about how a system behaves under real "
            "concurrent load — that's where capacity and latency problems actually surface. This skill "
            "covers designing load tests that reflect realistic traffic patterns, defining pass/fail "
            "thresholds tied to actual SLOs, and running different test types (load, stress, soak) for "
            "different questions.",
            "It emphasizes running performance tests continuously (or at least per significant release) "
            "rather than only once before a major launch, since performance regressions creep in gradually.",
        ],
        when_use=[
            "You need to validate a service meets its latency/throughput SLOs before a major launch or scaling event.",
            "You suspect a recent change introduced a performance regression.",
            "You need to determine a system's actual capacity limits ahead of an anticipated traffic spike.",
        ],
        when_not=[
            "You're diagnosing a single already-identified slow query — see skills/50-database/indexing-and-query-optimization/SKILL.md for a more targeted approach.",
            "The system has no meaningful concurrent user load (e.g. an internal single-user batch tool).",
        ],
        prereqs=[
            "skills/60-devops/observability/SKILL.md for the metrics load test results should be measured against.",
            "skills/20-architecture/scalability-and-capacity-planning/SKILL.md for the target load profile and SLOs being validated.",
        ],
        workflow=[
            ("Define pass/fail thresholds tied to real SLOs", "e.g. p95 latency under 300ms and error rate under 0.1% at target throughput — not just 'run it and see'."),
            ("Model realistic traffic patterns, not uniform load", "Reflect real usage: ramp-up, peak, and think-time between actions, not every virtual user hammering one endpoint simultaneously with zero pause."),
            ("Run a load test at expected peak traffic", "Confirm the system meets its SLOs at the traffic level actually expected in production."),
            ("Run a stress test to find the breaking point", "Increase load beyond expected peak until the system degrades, to know the actual headroom and failure mode."),
            ("Run a soak test for sustained-duration issues", "A multi-hour test at moderate load reveals memory leaks or resource exhaustion that a short test wouldn't surface."),
            ("Test against a production-representative environment", "Run against infrastructure sized and configured like production, not a scaled-down dev environment, or the results won't be meaningful."),
            ("Correlate load test results with backend observability", "Watch CPU, memory, DB connection pool, and queue depth during the test, not just client-observed latency."),
            ("Run performance tests as part of the regular release cadence", "Catch gradual regressions per release rather than only discovering them once at a big launch event."),
        ],
        decision=[
            ("You need to confirm the system meets its SLOs at expected peak traffic", "Run a load test at that specific target throughput with realistic traffic shape."),
            ("You need to know the system's actual maximum capacity", "Run a stress test that ramps load until failure, identifying the true bottleneck (CPU, DB connections, thread pool)."),
            ("You suspect a slow memory leak or resource exhaustion over time", "Run a soak test over several hours at moderate, sustained load."),
            ("A load test result looks fine at the client but the backend feels sluggish", "Correlate with backend metrics (DB pool, CPU) — the bottleneck may be masked by client-side retry/timeout behavior."),
            ("A load test passes in a scaled-down test environment", "Distrust the result until it's confirmed on a production-representative environment, since scaled-down infra often hides real bottlenecks."),
        ],
        code_lang="javascript",
        code_intro="A k6 load test modeling realistic traffic with think-time and SLO-based thresholds:",
        code=(
            "import http from 'k6/http';\n"
            "import { sleep, check } from 'k6';\n"
            "\n"
            "export const options = {\n"
            "  stages: [\n"
            "    { duration: '2m', target: 200 },   // ramp up to expected peak\n"
            "    { duration: '5m', target: 200 },   // sustain peak\n"
            "    { duration: '2m', target: 0 },     // ramp down\n"
            "  ],\n"
            "  thresholds: {\n"
            "    http_req_duration: ['p(95)<300'],  // SLO: p95 latency under 300ms\n"
            "    http_req_failed: ['rate<0.001'],   // SLO: error rate under 0.1%\n"
            "  },\n"
            "};\n"
            "\n"
            "export default function () {\n"
            "  const res = http.get('https://staging.example.com/api/orders');\n"
            "  check(res, { 'status is 200': (r) => r.status === 200 });\n"
            "  sleep(Math.random() * 3 + 1); // realistic think-time between requests\n"
            "}\n"
        ),
        code_notes=[
            "Thresholds are tied directly to SLOs (p95 latency, error rate), making the test result an automatic pass/fail rather than requiring manual interpretation.",
            "sleep() with randomized think-time better approximates real user behavior than firing requests back-to-back with zero pause.",
        ],
        code2_heading="A CI gate failing the pipeline on an SLO breach (YAML)",
        code2=("yaml",
            "Making performance regression a release-blocking signal, not just informational:",
            "- name: Run load test\n"
            "  run: k6 run --out json=results.json load-test.js\n"
            "- name: Fail on threshold breach\n"
            "  run: |\n"
            "    if grep -q '\"thresholds_failed\":true' results.json; then\n"
            "      echo 'Performance SLO breached'; exit 1;\n"
            "    fi\n"
        ),
        checklist=[
            "Pass/fail thresholds are tied to real SLOs, not left as an ambiguous 'run and eyeball it' result.",
            "Traffic patterns model realistic ramp-up, peak, and think-time rather than uniform zero-pause load.",
            "Load, stress, and soak tests are used for their distinct purposes rather than one generic test for everything.",
            "Tests run against a production-representative environment, not a significantly scaled-down one.",
            "Backend observability (CPU, DB pool, queue depth) is correlated with client-observed results during the test.",
            "Performance tests run as part of the regular release cadence, not only once before a major launch.",
        ],
        antipatterns=[
            ("No defined pass/fail criteria", "Running a load test and eyeballing 'it seems fine' instead of an explicit SLO-based threshold."),
            ("Unrealistic zero-think-time load", "Firing requests back-to-back with no pause between them, producing a load shape nothing like real user behavior."),
            ("Testing only in a scaled-down environment", "Running load tests against a tiny dev environment and assuming results transfer directly to production-scale infrastructure."),
            ("One-time pre-launch testing only", "Load testing once before a big launch and never again, missing gradual performance regressions introduced by later releases."),
            ("Ignoring backend metrics during the test", "Looking only at client-side latency/throughput numbers without correlating against server-side resource utilization to find the real bottleneck."),
        ],
        verification=[
            "A load test run reports an automatic pass/fail based on SLO thresholds, not manual interpretation.",
            "A stress test identifies the specific resource (CPU, DB connections, thread pool) that becomes the bottleneck at failure.",
            "A soak test of several hours shows stable memory/resource usage, not a steady upward trend indicating a leak.",
            "Load test results are confirmed consistent between the test environment and a production-representative environment.",
        ],
        references=[
            "skills/60-devops/observability/SKILL.md",
            "skills/20-architecture/scalability-and-capacity-planning/SKILL.md",
            "k6 documentation.",
        ],
    ),
]
