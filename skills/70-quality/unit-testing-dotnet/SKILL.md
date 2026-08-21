---
name: unit-testing-dotnet
description: Use when writing unit tests for .NET code and you need a consistent structure, mocking approach, and naming convention that keeps tests fast, isolated, and maintainable.
category: quality
tags: [unit-testing, xunit, mocking]
maturity: stable
updated: 2026-08-21
---

## Purpose

Unit tests that reach into real databases, sleep on timers, or depend on execution order aren't really unit tests — they're slow, flaky integration tests in disguise. This skill establishes xUnit conventions for .NET: the Arrange-Act-Assert structure, using test doubles for dependencies, and keeping each test isolated and deterministic.

It also covers when to use a real mocking library versus a simple hand-written fake, since over-mocking can couple tests tightly to implementation details rather than behavior.

## When to use / When NOT to use

**Use this skill when:**

- You are writing unit tests for a class or method in a .NET codebase.
- An existing test suite is slow, flaky, or tightly coupled to implementation internals.
- You need to decide how to isolate a class under test from its dependencies.

**Do NOT use this skill when:**

- You are testing the actual integration with a database or external service — see skills/70-quality/integration-testing/SKILL.md instead.
- You need guidance on which specific cases to write, rather than how to structure the test — see skills/70-quality/test-case-design/SKILL.md.

## Prerequisites

- skills/70-quality/test-case-design/SKILL.md for identifying which cases to write.
- xUnit and a mocking library (e.g. NSubstitute or Moq) referenced in the test project.

## Workflow

1. **Structure every test as Arrange-Act-Assert** - Set up inputs and dependencies, invoke the behavior under test, then assert the outcome — in that clear order.
2. **Test one logical behavior per test method** - Each test asserts one thing; multiple unrelated assertions in one test make failures ambiguous.
3. **Depend on abstractions, inject test doubles** - Classes under test take interfaces via constructor injection, allowing a fake/mock to stand in for real dependencies.
4. **Prefer state-based assertions over over-verifying interactions** - Assert on the resulting state/output first; use mock.Verify() only for genuinely important side effects (e.g. 'an email was sent').
5. **Use a hand-written fake for simple, stable dependencies** - A small in-memory fake repository is often clearer and more maintainable than a heavily configured mock for straightforward cases.
6. **Keep tests deterministic** - No reliance on real system time, random values, thread timing, or external network calls; inject a clock/random abstraction instead.
7. **Name tests to describe behavior clearly** - MethodName_Scenario_ExpectedBehavior or a plain English sentence — either way, readable without opening the test body.
8. **Keep test data setup minimal and obvious** - Build only the specific data needed for the scenario, using clear builder/factory helpers rather than large opaque fixture files.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A dependency has complex behavior needed for the test | Use a mocking library (NSubstitute/Moq) to configure exactly the behavior the scenario needs. |
| A dependency is simple and used across many tests | Write a small hand-rolled in-memory fake once, reused across tests, often clearer than repeated mock setup. |
| The test needs to verify a side effect occurred (e.g. event published) | Use mock.Received()/Verify() specifically for that side effect, not for every interaction. |
| A class depends on DateTime.Now or Guid.NewGuid directly | Inject an IClock/IGuidGenerator abstraction so tests can control time/identity deterministically. |
| A test needs a real database to be meaningful | It's not a unit test — move it to skills/70-quality/integration-testing/SKILL.md's approach instead. |

## Reference implementation

An Arrange-Act-Assert unit test using a mocking library for an injected dependency:

```csharp
public class PlaceOrderCommandHandlerTests
{
    [Fact]
    public async Task Handle_ValidOrder_AddsOrderAndReturnsId()
    {
        // Arrange
        var catalog = Substitute.For<ICatalogQueries>();
        catalog.GetProductAsync(Arg.Any<Guid>())
            .Returns(new ProductDto(Guid.NewGuid(), "Widget", 9.99m));
        var repository = Substitute.For<IOrderRepository>();
        var handler = new PlaceOrderCommandHandler(repository, catalog);
        var command = new PlaceOrderCommand(Guid.NewGuid(),
            new List<OrderLineDto> { new(Guid.NewGuid(), 2) });

        // Act
        var result = await handler.Handle(command, CancellationToken.None);

        // Assert
        Assert.NotEqual(Guid.Empty, result.OrderId);
        await repository.Received(1).AddAsync(Arg.Any<Order>(), Arg.Any<CancellationToken>());
    }
}
```

- The test asserts both the returned result (state) and that AddAsync was called once (a genuinely important side effect), not every incidental interaction.
- Substitute.For<T>() creates a lightweight mock scoped just to what this scenario needs, keeping setup minimal and readable.

### A hand-written in-memory fake repository for simpler, reused test setup (C#)

Often clearer than repeated mock configuration when the same fake is reused across many tests:

```csharp
public class InMemoryOrderRepository : IOrderRepository
{
    public List<Order> Orders { get; } = new();
    public Task<Order?> GetByIdAsync(Guid id, CancellationToken ct = default) =>
        Task.FromResult(Orders.FirstOrDefault(o => o.Id == id));
    public Task AddAsync(Order order, CancellationToken ct = default)
    {
        Orders.Add(order);
        return Task.CompletedTask;
    }
}
```

## Checklist

- [ ] Every unit test follows a clear Arrange-Act-Assert structure.
- [ ] Each test verifies one logical behavior, not several unrelated assertions bundled together.
- [ ] Dependencies are injected as abstractions, allowing test doubles to replace real implementations.
- [ ] Tests assert on resulting state/output primarily, using interaction verification only for genuinely important side effects.
- [ ] Non-deterministic sources (time, randomness, real I/O) are abstracted and controlled in tests.
- [ ] Test names clearly describe the scenario and expected behavior without needing to read the test body.

## Anti-patterns

- **Multiple unrelated assertions per test** - Asserting five unrelated things in one test method, making it unclear which behavior actually broke when it fails.
- **Over-mocking every dependency interaction** - Verifying every single method call on every mock, coupling tests tightly to implementation details rather than observable behavior.
- **Real time/randomness in tests** - Calling DateTime.Now or Guid.NewGuid directly inside code under test, making tests flaky or impossible to assert deterministically.
- **Giant shared fixture files** - A single huge, opaque test-data fixture reused (and mutated) across many unrelated tests, causing hidden coupling between them.
- **Testing implementation, not behavior** - Asserting on private internal state or exact call order that has nothing to do with the observable outcome, breaking on harmless refactors.

## Verification

- The full unit test suite runs in seconds, not minutes, with no real database or network dependency.
- Running tests in a different order or in parallel produces the same pass/fail results every time.
- A test failure's name and assertion message alone are enough to understand which behavior broke.
- Refactoring an implementation detail without changing observable behavior does not break existing unit tests.

## References

- skills/70-quality/test-case-design/SKILL.md
- skills/70-quality/integration-testing/SKILL.md
- xUnit and NSubstitute documentation.
