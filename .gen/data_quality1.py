SKILLS = [
    dict(
        dir="70-quality", slug="test-strategy", category="quality",
        tags=["test-strategy", "test-pyramid", "quality"],
        desc="Use when defining what kinds of tests a project needs, in what proportion, and at which pipeline stage they should run.",
        purpose=[
            "Without a deliberate test strategy, teams either over-invest in slow, brittle E2E tests or "
            "under-invest in fast unit tests, producing a suite that's both slow and unreliable. This skill "
            "establishes the test pyramid as a guiding shape — many fast unit tests, fewer integration tests, "
            "fewest E2E tests — and maps each test type to the confidence and feedback speed it provides.",
            "It also covers how a test strategy should be documented and revisited as the codebase evolves, "
            "rather than decided once and never reconsidered.",
        ],
        when_use=[
            "You are starting a new project and need to establish its overall testing approach.",
            "An existing test suite is slow, flaky, or gives the team little confidence despite high coverage numbers.",
            "You are deciding what kind of test to write for a specific new piece of functionality.",
        ],
        when_not=[
            "You need guidance on writing a specific unit test's structure — see skills/70-quality/unit-testing-dotnet/SKILL.md or skills/70-quality/test-case-design/SKILL.md instead.",
            "The question is about a specific test framework's syntax rather than overall strategy.",
        ],
        prereqs=[
            "skills/70-quality/test-case-design/SKILL.md for how individual test cases should be designed.",
            "skills/60-devops/ci-cd-pipelines/SKILL.md for where each test type runs in the pipeline.",
        ],
        workflow=[
            ("Shape the suite like a pyramid", "Many fast, isolated unit tests at the base; fewer integration tests; a small number of E2E tests at the top."),
            ("Match test type to what needs verifying", "Unit tests verify logic in isolation; integration tests verify component boundaries (DB, HTTP); E2E tests verify critical user journeys end-to-end."),
            ("Define what 'critical path' means for E2E coverage", "Only the handful of highest-value user journeys (checkout, login) warrant E2E tests; don't E2E-test every edge case."),
            ("Run fast tests on every push, slow tests less frequently", "Unit tests on every commit; integration/E2E tests on PR merge or a scheduled cadence, per skills/60-devops/ci-cd-pipelines/SKILL.md."),
            ("Track flaky tests as a first-class defect", "A flaky test undermines trust in the whole suite; quarantine and fix it promptly rather than ignoring reruns."),
            ("Measure meaningful coverage, not just percentage", "Track coverage of critical logic paths and mutation-testing signal over raw line-coverage percentage chasing."),
            ("Document the strategy and revisit it periodically", "Write down the intended test-type mix and reasoning; revisit it if the codebase's risk profile changes significantly."),
        ],
        decision=[
            ("Verifying a pure business rule/calculation", "Write a unit test — fast, isolated, no I/O."),
            ("Verifying a repository correctly persists and retrieves data", "Write an integration test against a real (or containerized) database."),
            ("Verifying the checkout flow works end-to-end across UI, API, and payment", "Write one E2E test for the critical happy path, not exhaustive E2E coverage of every variation."),
            ("A test suite is slow and blocking CI feedback", "Rebalance toward more unit tests and fewer, more targeted integration/E2E tests."),
            ("Coverage percentage is high but bugs still slip through", "Review whether tests actually assert meaningful behavior, or investigate mutation testing to find weak assertions."),
        ],
        code_lang="text",
        code_intro="The test pyramid shape and where each layer runs in the pipeline:",
        code=(
            "        /\\\n"
            "       /E2E\\        <- few, slow, highest confidence for critical user journeys\n"
            "      /------\\         runs on PR merge / nightly\n"
            "     /Integr. \\    <- moderate count, verifies component boundaries (DB, HTTP, queues)\n"
            "    /----------\\      runs on every PR\n"
            "   /   Unit     \\  <- many, fast, isolated logic verification\n"
            "  /--------------\\    runs on every push/commit\n"
            "\n"
            "Guideline ratio (adjust per codebase): ~70% unit, ~20% integration, ~10% E2E.\n"
        ),
        code_notes=[
            "The ratio is a guideline, not a strict rule — a data-heavy service may lean more integration-test-heavy; the shape (fewer tests as you go up) should still hold.",
            "Running tests at different pipeline stages balances fast feedback against full-confidence coverage before deploy.",
        ],
        code2_heading="A test-type decision recorded alongside a feature (Markdown note)",
        code2=("markdown",
            "Documenting why a specific test type was chosen for a change:",
            "## Test approach: Order discount calculation\n"
            "- Unit tests: all discount rule combinations (percentage, fixed, tiered) - fast, exhaustive.\n"
            "- Integration test: one test confirming the discount is persisted correctly with the order.\n"
            "- No E2E test added: covered by the existing checkout E2E happy-path test already.\n"
        ),
        checklist=[
            "The test suite's overall shape resembles a pyramid: many unit tests, fewer integration, fewest E2E.",
            "Each new piece of functionality's test type is chosen deliberately based on what needs verifying.",
            "Fast tests run on every push; slower tests run at a less frequent, still regular cadence.",
            "Flaky tests are tracked and fixed promptly, not silently retried and ignored.",
            "Coverage is evaluated for meaningfulness (critical paths, mutation signal), not chased as a raw percentage target.",
            "The test strategy is documented and revisited as the project's risk profile evolves.",
        ],
        antipatterns=[
            ("Ice cream cone anti-pattern", "A test suite with mostly slow E2E tests and few unit tests, making the suite slow, flaky, and hard to maintain."),
            ("100% E2E coverage aspiration", "Attempting to E2E-test every edge case instead of pushing detailed logic verification down to unit tests."),
            ("Chasing coverage percentage", "Writing tests that execute code without meaningfully asserting behavior, just to inflate a coverage number."),
            ("Ignoring flaky tests", "Treating a flaky test as background noise to retry rather than a real defect undermining trust in the suite."),
            ("One-time strategy, never revisited", "Deciding on a test approach once at project start and never reconsidering it as the codebase and risk profile change."),
        ],
        verification=[
            "A test-count report shows the suite's shape roughly follows the intended pyramid ratio.",
            "CI pipeline timing confirms fast tests provide feedback within a target time budget on every push.",
            "No test in the suite has an open, ignored flakiness ticket older than an agreed threshold.",
            "A mutation testing run (or targeted review) confirms critical logic paths have meaningful, not just present, test coverage.",
        ],
        references=[
            "skills/70-quality/test-case-design/SKILL.md",
            "skills/70-quality/unit-testing-dotnet/SKILL.md",
            "skills/70-quality/integration-testing/SKILL.md",
            "skills/70-quality/e2e-and-contract-testing/SKILL.md",
            "Martin Fowler — Test Pyramid.",
        ],
    ),
    dict(
        dir="70-quality", slug="test-case-design", category="quality",
        tags=["test-case-design", "boundary-analysis", "equivalence-partitioning"],
        desc="Use when designing the specific test cases for a piece of functionality to ensure meaningful coverage of behavior, edge cases, and failure modes.",
        purpose=[
            "Writing tests only for the 'happy path' leaves edge cases, boundary conditions, and error "
            "handling unverified, exactly where bugs tend to hide. This skill covers systematic test case "
            "design techniques — equivalence partitioning, boundary value analysis, and decision tables — "
            "that generate a compact but meaningful set of test cases rather than either too few or an "
            "unfocused excess.",
            "It applies to unit, integration, and manual test case design alike, since the underlying "
            "technique for identifying what to test is the same regardless of the test level.",
        ],
        when_use=[
            "You are writing tests for a new function, endpoint, or business rule.",
            "A bug was found in production that existing tests should have caught, indicating a coverage gap.",
            "You need to review whether a test suite for a piece of logic is actually comprehensive.",
        ],
        when_not=[
            "You need overall strategy about test type/pyramid balance — see skills/70-quality/test-strategy/SKILL.md instead.",
            "The functionality is trivial (e.g. a pure pass-through) with no meaningful branching or edge cases to enumerate.",
        ],
        prereqs=[
            "skills/70-quality/test-strategy/SKILL.md for which test level (unit/integration/E2E) this case belongs in.",
            "A clear specification or acceptance criteria for the functionality being tested.",
        ],
        workflow=[
            ("Identify equivalence classes for each input", "Group inputs into classes expected to behave the same way (valid, invalid, boundary) to avoid redundant near-identical tests."),
            ("Apply boundary value analysis at each class edge", "Test just inside, at, and just outside each boundary (e.g. quantity = 0, 1, max, max+1), since bugs cluster at boundaries."),
            ("Cover both positive and negative cases", "Test that valid input succeeds and that invalid input is rejected with the correct error, not just the success path."),
            ("Use a decision table for multiple interacting conditions", "When several boolean conditions combine to determine behavior, enumerate the combinations systematically rather than ad hoc."),
            ("Include representative error and exception scenarios", "Network failure, timeout, and malformed input scenarios get explicit test cases, not just the well-formed case."),
            ("Name tests to describe behavior, not implementation", "A test name should read as a specification: 'Should reject order when quantity is zero', not 'Test1'."),
            ("Review test cases against the specification before writing code (TDD) or after (test-after)", "Confirm the enumerated cases actually map to the acceptance criteria, catching missed requirements early."),
        ],
        decision=[
            ("An input has a numeric range (e.g. 1-100)", "Test the boundaries: 0 (just below), 1 (min), 100 (max), 101 (just above), plus a mid-range valid value."),
            ("An input has several independent boolean flags affecting behavior", "Build a decision table enumerating the meaningful flag combinations rather than guessing which matter."),
            ("Many inputs would exercise the same code path identically", "Pick one representative value per equivalence class instead of testing every possible value."),
            ("A function can throw for multiple distinct reasons", "Write a distinct test case per exception type/reason, asserting the specific error, not just 'an exception is thrown'."),
            ("A previous production bug slipped through testing", "Add a regression test reproducing that exact scenario before considering the bug fully closed."),
        ],
        code_lang="csharp",
        code_intro="Boundary value and equivalence-partition test cases for a discount rule:",
        code=(
            "public class DiscountCalculatorTests\n"
            "{\n"
            "    [Theory]\n"
            "    [InlineData(0, 0)]      // below minimum quantity: no discount\n"
            "    [InlineData(1, 0)]      // boundary: minimum non-discount quantity\n"
            "    [InlineData(10, 5)]     // boundary: exactly at discount threshold\n"
            "    [InlineData(11, 5)]     // just above threshold: same discount tier\n"
            "    [InlineData(100, 15)]   // upper tier boundary\n"
            "    public void CalculatesDiscountPercentForQuantity(int quantity, int expectedPercent)\n"
            "    {\n"
            "        var result = DiscountCalculator.PercentFor(quantity);\n"
            "        Assert.Equal(expectedPercent, result);\n"
            "    }\n"
            "\n"
            "    [Fact]\n"
            "    public void ThrowsForNegativeQuantity()\n"
            "    {\n"
            "        Assert.Throws<ArgumentOutOfRangeException>(() => DiscountCalculator.PercentFor(-1));\n"
            "    }\n"
            "}\n"
        ),
        code_notes=[
            "Each InlineData row targets a specific boundary or equivalence class, not an arbitrary or redundant value.",
            "The negative-quantity case is a distinct equivalence class (invalid input) tested separately from the valid-range boundaries.",
        ],
        code2_heading="A decision table for a shipping-eligibility rule (Markdown)",
        code2=("markdown",
            "Enumerating combinations of conditions systematically before writing test cases:",
            "| Is Member | Order Total > $50 | Region Supported | Result           |\n"
            "|-----------|--------------------|------------------|-------------------|\n"
            "| Yes        | Yes                | Yes              | Free shipping     |\n"
            "| Yes        | No                 | Yes              | Standard shipping |\n"
            "| No         | Yes                | Yes              | Standard shipping |\n"
            "| No         | Yes                | No               | Rejected          |\n"
        ),
        checklist=[
            "Test cases cover equivalence classes (valid, invalid, boundary) rather than redundant near-identical inputs.",
            "Boundary values are explicitly tested just inside, at, and just outside each meaningful threshold.",
            "Both positive (valid input succeeds) and negative (invalid input rejected correctly) cases are covered.",
            "Interacting conditions are enumerated via a decision table where more than one flag affects behavior.",
            "Test names describe expected behavior, readable as a specification.",
            "Every previously found production bug has a corresponding regression test case.",
        ],
        antipatterns=[
            ("Happy-path-only testing", "Writing tests only for well-formed, typical input, leaving edge cases and error handling completely unverified."),
            ("Redundant near-identical test cases", "Testing quantity=5, 6, 7, 8 when they're all in the same equivalence class, adding maintenance cost with no new coverage."),
            ("Untested boundaries", "Testing quantity=50 for a rule that changes behavior at quantity=50, but never testing 49 or 51 directly at the edge."),
            ("Vague test names", "Naming tests Test1, Test2 or TestDiscount, giving no indication of what specific behavior is being verified when it fails."),
            ("Guessing at decision table combinations", "Testing only a couple of ad hoc combinations of interacting conditions instead of systematically enumerating the meaningful ones."),
        ],
        verification=[
            "A code review confirms test cases explicitly cover each boundary of every meaningful numeric range or threshold.",
            "Both a valid and an invalid case exist for every distinct equivalence class identified in the specification.",
            "Test names alone (without reading the body) convey what specific behavior each test verifies.",
            "A previously reported production bug has an associated regression test that would fail without the fix.",
        ],
        references=[
            "skills/70-quality/test-strategy/SKILL.md",
            "skills/70-quality/unit-testing-dotnet/SKILL.md",
            "ISTQB — Equivalence Partitioning and Boundary Value Analysis.",
        ],
    ),
]
