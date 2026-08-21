SKILLS = [
    dict(
        dir="70-quality", slug="unit-testing-dotnet", category="quality",
        tags=["unit-testing", "xunit", "mocking"],
        desc="Use when writing unit tests for .NET code and you need a consistent structure, mocking approach, and naming convention that keeps tests fast, isolated, and maintainable.",
        purpose=[
            "Unit tests that reach into real databases, sleep on timers, or depend on execution order aren't "
            "really unit tests — they're slow, flaky integration tests in disguise. This skill establishes "
            "xUnit conventions for .NET: the Arrange-Act-Assert structure, using test doubles for "
            "dependencies, and keeping each test isolated and deterministic.",
            "It also covers when to use a real mocking library versus a simple hand-written fake, since "
            "over-mocking can couple tests tightly to implementation details rather than behavior.",
        ],
        when_use=[
            "You are writing unit tests for a class or method in a .NET codebase.",
            "An existing test suite is slow, flaky, or tightly coupled to implementation internals.",
            "You need to decide how to isolate a class under test from its dependencies.",
        ],
        when_not=[
            "You are testing the actual integration with a database or external service — see skills/70-quality/integration-testing/SKILL.md instead.",
            "You need guidance on which specific cases to write, rather than how to structure the test — see skills/70-quality/test-case-design/SKILL.md.",
        ],
        prereqs=[
            "skills/70-quality/test-case-design/SKILL.md for identifying which cases to write.",
            "xUnit and a mocking library (e.g. NSubstitute or Moq) referenced in the test project.",
        ],
        workflow=[
            ("Structure every test as Arrange-Act-Assert", "Set up inputs and dependencies, invoke the behavior under test, then assert the outcome — in that clear order."),
            ("Test one logical behavior per test method", "Each test asserts one thing; multiple unrelated assertions in one test make failures ambiguous."),
            ("Depend on abstractions, inject test doubles", "Classes under test take interfaces via constructor injection, allowing a fake/mock to stand in for real dependencies."),
            ("Prefer state-based assertions over over-verifying interactions", "Assert on the resulting state/output first; use mock.Verify() only for genuinely important side effects (e.g. 'an email was sent')."),
            ("Use a hand-written fake for simple, stable dependencies", "A small in-memory fake repository is often clearer and more maintainable than a heavily configured mock for straightforward cases."),
            ("Keep tests deterministic", "No reliance on real system time, random values, thread timing, or external network calls; inject a clock/random abstraction instead."),
            ("Name tests to describe behavior clearly", "MethodName_Scenario_ExpectedBehavior or a plain English sentence — either way, readable without opening the test body."),
            ("Keep test data setup minimal and obvious", "Build only the specific data needed for the scenario, using clear builder/factory helpers rather than large opaque fixture files."),
        ],
        decision=[
            ("A dependency has complex behavior needed for the test", "Use a mocking library (NSubstitute/Moq) to configure exactly the behavior the scenario needs."),
            ("A dependency is simple and used across many tests", "Write a small hand-rolled in-memory fake once, reused across tests, often clearer than repeated mock setup."),
            ("The test needs to verify a side effect occurred (e.g. event published)", "Use mock.Received()/Verify() specifically for that side effect, not for every interaction."),
            ("A class depends on DateTime.Now or Guid.NewGuid directly", "Inject an IClock/IGuidGenerator abstraction so tests can control time/identity deterministically."),
            ("A test needs a real database to be meaningful", "It's not a unit test — move it to skills/70-quality/integration-testing/SKILL.md's approach instead."),
        ],
        code_lang="csharp",
        code_intro="An Arrange-Act-Assert unit test using a mocking library for an injected dependency:",
        code=(
            "public class PlaceOrderCommandHandlerTests\n"
            "{\n"
            "    [Fact]\n"
            "    public async Task Handle_ValidOrder_AddsOrderAndReturnsId()\n"
            "    {\n"
            "        // Arrange\n"
            "        var catalog = Substitute.For<ICatalogQueries>();\n"
            "        catalog.GetProductAsync(Arg.Any<Guid>())\n"
            "            .Returns(new ProductDto(Guid.NewGuid(), \"Widget\", 9.99m));\n"
            "        var repository = Substitute.For<IOrderRepository>();\n"
            "        var handler = new PlaceOrderCommandHandler(repository, catalog);\n"
            "        var command = new PlaceOrderCommand(Guid.NewGuid(),\n"
            "            new List<OrderLineDto> { new(Guid.NewGuid(), 2) });\n"
            "\n"
            "        // Act\n"
            "        var result = await handler.Handle(command, CancellationToken.None);\n"
            "\n"
            "        // Assert\n"
            "        Assert.NotEqual(Guid.Empty, result.OrderId);\n"
            "        await repository.Received(1).AddAsync(Arg.Any<Order>(), Arg.Any<CancellationToken>());\n"
            "    }\n"
            "}\n"
        ),
        code_notes=[
            "The test asserts both the returned result (state) and that AddAsync was called once (a genuinely important side effect), not every incidental interaction.",
            "Substitute.For<T>() creates a lightweight mock scoped just to what this scenario needs, keeping setup minimal and readable.",
        ],
        code2_heading="A hand-written in-memory fake repository for simpler, reused test setup (C#)",
        code2=("csharp",
            "Often clearer than repeated mock configuration when the same fake is reused across many tests:",
            "public class InMemoryOrderRepository : IOrderRepository\n"
            "{\n"
            "    public List<Order> Orders { get; } = new();\n"
            "    public Task<Order?> GetByIdAsync(Guid id, CancellationToken ct = default) =>\n"
            "        Task.FromResult(Orders.FirstOrDefault(o => o.Id == id));\n"
            "    public Task AddAsync(Order order, CancellationToken ct = default)\n"
            "    {\n"
            "        Orders.Add(order);\n"
            "        return Task.CompletedTask;\n"
            "    }\n"
            "}\n"
        ),
        checklist=[
            "Every unit test follows a clear Arrange-Act-Assert structure.",
            "Each test verifies one logical behavior, not several unrelated assertions bundled together.",
            "Dependencies are injected as abstractions, allowing test doubles to replace real implementations.",
            "Tests assert on resulting state/output primarily, using interaction verification only for genuinely important side effects.",
            "Non-deterministic sources (time, randomness, real I/O) are abstracted and controlled in tests.",
            "Test names clearly describe the scenario and expected behavior without needing to read the test body.",
        ],
        antipatterns=[
            ("Multiple unrelated assertions per test", "Asserting five unrelated things in one test method, making it unclear which behavior actually broke when it fails."),
            ("Over-mocking every dependency interaction", "Verifying every single method call on every mock, coupling tests tightly to implementation details rather than observable behavior."),
            ("Real time/randomness in tests", "Calling DateTime.Now or Guid.NewGuid directly inside code under test, making tests flaky or impossible to assert deterministically."),
            ("Giant shared fixture files", "A single huge, opaque test-data fixture reused (and mutated) across many unrelated tests, causing hidden coupling between them."),
            ("Testing implementation, not behavior", "Asserting on private internal state or exact call order that has nothing to do with the observable outcome, breaking on harmless refactors."),
        ],
        verification=[
            "The full unit test suite runs in seconds, not minutes, with no real database or network dependency.",
            "Running tests in a different order or in parallel produces the same pass/fail results every time.",
            "A test failure's name and assertion message alone are enough to understand which behavior broke.",
            "Refactoring an implementation detail without changing observable behavior does not break existing unit tests.",
        ],
        references=[
            "skills/70-quality/test-case-design/SKILL.md",
            "skills/70-quality/integration-testing/SKILL.md",
            "xUnit and NSubstitute documentation.",
        ],
    ),
    dict(
        dir="70-quality", slug="integration-testing", category="quality",
        tags=["integration-testing", "testcontainers", "webapplicationfactory"],
        desc="Use when verifying that a service correctly integrates with a real dependency such as a database, message broker, or HTTP API, beyond what a unit test with mocks can confirm.",
        purpose=[
            "Unit tests with mocked dependencies can't catch real integration bugs — a subtly wrong SQL "
            "query, a serialization mismatch, or an incorrect HTTP status code mapping. This skill covers "
            "writing integration tests that exercise real infrastructure (via Testcontainers or an in-process "
            "test server) to verify these boundaries actually work, while keeping the tests fast and "
            "reliable enough to run routinely in CI.",
            "It emphasizes using ephemeral, code-provisioned infrastructure rather than a shared persistent "
            "test environment, so tests are isolated and reproducible.",
        ],
        when_use=[
            "You need to verify a repository's queries actually work against a real database engine.",
            "You need to verify an API endpoint's full request/response pipeline (routing, auth, serialization).",
            "A unit test with mocks wouldn't catch the specific class of bug you're worried about (e.g. a wrong column mapping).",
        ],
        when_not=[
            "The logic being tested has no real external dependency — a unit test is faster and sufficient.",
            "You need to test a full user journey across multiple services/UI — see skills/70-quality/e2e-and-contract-testing/SKILL.md instead.",
        ],
        prereqs=[
            "skills/70-quality/unit-testing-dotnet/SKILL.md for the base testing conventions this builds on.",
            "Docker available in the CI environment for Testcontainers-based database/broker instances.",
        ],
        workflow=[
            ("Use Testcontainers for real, ephemeral infrastructure", "Spin up a real Postgres/SQL Server/RabbitMQ container per test run rather than mocking the driver or using a shared environment."),
            ("Use WebApplicationFactory for full-pipeline API tests", "Boot the actual ASP.NET Core app in-process, testing routing, middleware, and serialization together."),
            ("Reset state between tests", "Truncate tables or use a fresh container/schema per test class so tests don't leak state into each other."),
            ("Test real query/mapping correctness", "Verify EF Core/Dapper queries against the real database engine, catching SQL dialect or mapping issues mocks would hide."),
            ("Verify the full HTTP contract for key endpoints", "Assert status codes, response shape, and headers, not just that a handler method was called."),
            ("Keep the suite reasonably fast via parallelization and reuse", "Run independent test classes in parallel and reuse a container across tests within a class where safe, respecting state isolation."),
            ("Run integration tests on every PR, not just nightly", "They're not free, but they're valuable enough to run before merge, distinct from a slower full E2E suite."),
            ("Isolate integration tests from unit tests in the pipeline", "Separate test projects/categories so CI can report and gate on them distinctly from fast unit tests."),
        ],
        decision=[
            ("Verifying a repository's EF Core query logic", "Use a Testcontainers-provisioned real database instance, not an in-memory EF provider that behaves differently from production SQL."),
            ("Verifying an API endpoint's full request pipeline", "Use WebApplicationFactory to boot the app in-process and send real HTTP requests to it."),
            ("A test needs a message broker to verify publish/consume behavior", "Use a Testcontainers RabbitMQ/Kafka instance rather than mocking the broker client."),
            ("Tests are slow because each spins up its own container", "Share one container across a test class's tests where test data isolation still holds, resetting state between tests."),
            ("You're tempted to use EF Core's in-memory provider for a 'quick' integration test", "Avoid it — it doesn't enforce real constraints or SQL translation, hiding bugs a real database would catch."),
        ],
        code_lang="csharp",
        code_intro="A Testcontainers-backed integration test for a repository against a real PostgreSQL instance:",
        code=(
            "public class OrderRepositoryTests : IClassFixture<PostgresFixture>\n"
            "{\n"
            "    private readonly PostgresFixture _fixture;\n"
            "    public OrderRepositoryTests(PostgresFixture fixture) => _fixture = fixture;\n"
            "\n"
            "    [Fact]\n"
            "    public async Task AddAsync_PersistsOrderWithLines()\n"
            "    {\n"
            "        await using var db = _fixture.CreateDbContext();\n"
            "        var repository = new EfOrderRepository(db);\n"
            "        var order = Order.Create(Guid.NewGuid());\n"
            "        order.AddLine(new ProductRef(Guid.NewGuid(), \"Widget\"), quantity: 3);\n"
            "\n"
            "        await repository.AddAsync(order);\n"
            "        await db.SaveChangesAsync();\n"
            "\n"
            "        await using var verifyDb = _fixture.CreateDbContext();\n"
            "        var reloaded = await verifyDb.Orders.Include(o => o.Lines)\n"
            "            .FirstAsync(o => o.Id == order.Id);\n"
            "        Assert.Single(reloaded.Lines);\n"
            "    }\n"
            "}\n"
            "\n"
            "public class PostgresFixture : IAsyncLifetime\n"
            "{\n"
            "    private readonly PostgreSqlContainer _container = new PostgreSqlBuilder().Build();\n"
            "    public async Task InitializeAsync() => await _container.StartAsync();\n"
            "    public Task DisposeAsync() => _container.DisposeAsync().AsTask();\n"
            "    public AppDbContext CreateDbContext() => new(new DbContextOptionsBuilder<AppDbContext>()\n"
            "        .UseNpgsql(_container.GetConnectionString()).Options);\n"
            "}\n"
        ),
        code_notes=[
            "A fresh Postgres container starts per test class run, giving a real database with no shared-environment state leakage between test runs.",
            "Reloading via a second, separate DbContext instance confirms data was actually persisted, not just held in the first context's change tracker.",
        ],
        code2_heading="An in-process API test using WebApplicationFactory (C#)",
        code2=("csharp",
            "Testing the full HTTP pipeline including routing, auth, and serialization:",
            "public class OrdersApiTests : IClassFixture<WebApplicationFactory<Program>>\n"
            "{\n"
            "    private readonly HttpClient _client;\n"
            "    public OrdersApiTests(WebApplicationFactory<Program> factory) => _client = factory.CreateClient();\n"
            "\n"
            "    [Fact]\n"
            "    public async Task GetOrder_NotFound_Returns404WithProblemDetails()\n"
            "    {\n"
            "        var response = await _client.GetAsync($\"/orders/{Guid.NewGuid()}\");\n"
            "        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);\n"
            "        var problem = await response.Content.ReadFromJsonAsync<ProblemDetails>();\n"
            "        Assert.Equal(404, problem!.Status);\n"
            "    }\n"
            "}\n"
        ),
        checklist=[
            "Integration tests use real, ephemeral infrastructure (Testcontainers) rather than in-memory fakes that behave differently from production.",
            "API integration tests boot the actual app in-process via WebApplicationFactory, exercising the full pipeline.",
            "Test state is reset between tests/classes to prevent leakage and flaky ordering dependencies.",
            "Integration tests run on every PR, in a distinct, separately reported CI stage from unit tests.",
            "EF Core's in-memory provider is avoided for integration tests that need to verify real SQL/constraint behavior.",
            "The suite's total runtime is kept reasonable via parallelization and safe container reuse.",
        ],
        antipatterns=[
            ("EF Core in-memory provider as an integration test", "Using UseInMemoryDatabase for an 'integration' test, which silently ignores real SQL constraints and dialect differences."),
            ("Shared persistent test environment", "Running integration tests against one long-lived shared database, causing state leakage and non-reproducible failures between runs."),
            ("No state reset between tests", "Letting data from one test bleed into the next, causing order-dependent, flaky test results."),
            ("Mixing unit and integration tests in one project/run", "Failing to separate fast unit tests from slower integration tests, making it impossible for CI to gate on them differently."),
            ("Testing only the happy path via HTTP", "Only verifying a 200 response for valid input, never asserting the correct status/shape for 404/400/409 cases."),
        ],
        verification=[
            "Integration tests pass consistently across multiple consecutive CI runs, with no observed ordering-dependent flakiness.",
            "A schema/constraint violation introduced deliberately causes the relevant integration test to fail, confirming it exercises real database behavior.",
            "CI reports unit and integration test results as distinct stages/categories.",
            "API integration tests cover at least one success and one representative failure status code per key endpoint.",
        ],
        references=[
            "skills/70-quality/unit-testing-dotnet/SKILL.md",
            "skills/70-quality/e2e-and-contract-testing/SKILL.md",
            "Testcontainers for .NET documentation.",
            "Microsoft Learn — WebApplicationFactory integration testing.",
        ],
    ),
]
