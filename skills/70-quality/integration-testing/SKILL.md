---
name: integration-testing
description: Use when verifying that a service correctly integrates with a real dependency such as a database, message broker, or HTTP API, beyond what a unit test with mocks can confirm.
category: quality
tags: [integration-testing, testcontainers, webapplicationfactory]
maturity: stable
updated: 2026-08-21
---

## Purpose

Unit tests with mocked dependencies can't catch real integration bugs — a subtly wrong SQL query, a serialization mismatch, or an incorrect HTTP status code mapping. This skill covers writing integration tests that exercise real infrastructure (via Testcontainers or an in-process test server) to verify these boundaries actually work, while keeping the tests fast and reliable enough to run routinely in CI.

It emphasizes using ephemeral, code-provisioned infrastructure rather than a shared persistent test environment, so tests are isolated and reproducible.

## When to use / When NOT to use

**Use this skill when:**

- You need to verify a repository's queries actually work against a real database engine.
- You need to verify an API endpoint's full request/response pipeline (routing, auth, serialization).
- A unit test with mocks wouldn't catch the specific class of bug you're worried about (e.g. a wrong column mapping).

**Do NOT use this skill when:**

- The logic being tested has no real external dependency — a unit test is faster and sufficient.
- You need to test a full user journey across multiple services/UI — see skills/70-quality/e2e-and-contract-testing/SKILL.md instead.

## Prerequisites

- skills/70-quality/unit-testing-dotnet/SKILL.md for the base testing conventions this builds on.
- Docker available in the CI environment for Testcontainers-based database/broker instances.

## Workflow

1. **Use Testcontainers for real, ephemeral infrastructure** - Spin up a real Postgres/SQL Server/RabbitMQ container per test run rather than mocking the driver or using a shared environment.
2. **Use WebApplicationFactory for full-pipeline API tests** - Boot the actual ASP.NET Core app in-process, testing routing, middleware, and serialization together.
3. **Reset state between tests** - Truncate tables or use a fresh container/schema per test class so tests don't leak state into each other.
4. **Test real query/mapping correctness** - Verify EF Core/Dapper queries against the real database engine, catching SQL dialect or mapping issues mocks would hide.
5. **Verify the full HTTP contract for key endpoints** - Assert status codes, response shape, and headers, not just that a handler method was called.
6. **Keep the suite reasonably fast via parallelization and reuse** - Run independent test classes in parallel and reuse a container across tests within a class where safe, respecting state isolation.
7. **Run integration tests on every PR, not just nightly** - They're not free, but they're valuable enough to run before merge, distinct from a slower full E2E suite.
8. **Isolate integration tests from unit tests in the pipeline** - Separate test projects/categories so CI can report and gate on them distinctly from fast unit tests.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Verifying a repository's EF Core query logic | Use a Testcontainers-provisioned real database instance, not an in-memory EF provider that behaves differently from production SQL. |
| Verifying an API endpoint's full request pipeline | Use WebApplicationFactory to boot the app in-process and send real HTTP requests to it. |
| A test needs a message broker to verify publish/consume behavior | Use a Testcontainers RabbitMQ/Kafka instance rather than mocking the broker client. |
| Tests are slow because each spins up its own container | Share one container across a test class's tests where test data isolation still holds, resetting state between tests. |
| You're tempted to use EF Core's in-memory provider for a 'quick' integration test | Avoid it — it doesn't enforce real constraints or SQL translation, hiding bugs a real database would catch. |

## Reference implementation

A Testcontainers-backed integration test for a repository against a real PostgreSQL instance:

```csharp
public class OrderRepositoryTests : IClassFixture<PostgresFixture>
{
    private readonly PostgresFixture _fixture;
    public OrderRepositoryTests(PostgresFixture fixture) => _fixture = fixture;

    [Fact]
    public async Task AddAsync_PersistsOrderWithLines()
    {
        await using var db = _fixture.CreateDbContext();
        var repository = new EfOrderRepository(db);
        var order = Order.Create(Guid.NewGuid());
        order.AddLine(new ProductRef(Guid.NewGuid(), "Widget"), quantity: 3);

        await repository.AddAsync(order);
        await db.SaveChangesAsync();

        await using var verifyDb = _fixture.CreateDbContext();
        var reloaded = await verifyDb.Orders.Include(o => o.Lines)
            .FirstAsync(o => o.Id == order.Id);
        Assert.Single(reloaded.Lines);
    }
}

public class PostgresFixture : IAsyncLifetime
{
    private readonly PostgreSqlContainer _container = new PostgreSqlBuilder().Build();
    public async Task InitializeAsync() => await _container.StartAsync();
    public Task DisposeAsync() => _container.DisposeAsync().AsTask();
    public AppDbContext CreateDbContext() => new(new DbContextOptionsBuilder<AppDbContext>()
        .UseNpgsql(_container.GetConnectionString()).Options);
}
```

- A fresh Postgres container starts per test class run, giving a real database with no shared-environment state leakage between test runs.
- Reloading via a second, separate DbContext instance confirms data was actually persisted, not just held in the first context's change tracker.

### An in-process API test using WebApplicationFactory (C#)

Testing the full HTTP pipeline including routing, auth, and serialization:

```csharp
public class OrdersApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;
    public OrdersApiTests(WebApplicationFactory<Program> factory) => _client = factory.CreateClient();

    [Fact]
    public async Task GetOrder_NotFound_Returns404WithProblemDetails()
    {
        var response = await _client.GetAsync($"/orders/{Guid.NewGuid()}");
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
        var problem = await response.Content.ReadFromJsonAsync<ProblemDetails>();
        Assert.Equal(404, problem!.Status);
    }
}
```

## Checklist

- [ ] Integration tests use real, ephemeral infrastructure (Testcontainers) rather than in-memory fakes that behave differently from production.
- [ ] API integration tests boot the actual app in-process via WebApplicationFactory, exercising the full pipeline.
- [ ] Test state is reset between tests/classes to prevent leakage and flaky ordering dependencies.
- [ ] Integration tests run on every PR, in a distinct, separately reported CI stage from unit tests.
- [ ] EF Core's in-memory provider is avoided for integration tests that need to verify real SQL/constraint behavior.
- [ ] The suite's total runtime is kept reasonable via parallelization and safe container reuse.

## Anti-patterns

- **EF Core in-memory provider as an integration test** - Using UseInMemoryDatabase for an 'integration' test, which silently ignores real SQL constraints and dialect differences.
- **Shared persistent test environment** - Running integration tests against one long-lived shared database, causing state leakage and non-reproducible failures between runs.
- **No state reset between tests** - Letting data from one test bleed into the next, causing order-dependent, flaky test results.
- **Mixing unit and integration tests in one project/run** - Failing to separate fast unit tests from slower integration tests, making it impossible for CI to gate on them differently.
- **Testing only the happy path via HTTP** - Only verifying a 200 response for valid input, never asserting the correct status/shape for 404/400/409 cases.

## Verification

- Integration tests pass consistently across multiple consecutive CI runs, with no observed ordering-dependent flakiness.
- A schema/constraint violation introduced deliberately causes the relevant integration test to fail, confirming it exercises real database behavior.
- CI reports unit and integration test results as distinct stages/categories.
- API integration tests cover at least one success and one representative failure status code per key endpoint.

## References

- skills/70-quality/unit-testing-dotnet/SKILL.md
- skills/70-quality/e2e-and-contract-testing/SKILL.md
- Testcontainers for .NET documentation.
- Microsoft Learn — WebApplicationFactory integration testing.
