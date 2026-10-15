---
name: cqrs-with-mediatr
description: Use when an application's use cases are becoming tangled in large service classes and you need a consistent, discoverable pattern for commands, queries, and their handlers.
category: backend
tags: [cqrs, mediatr, application-layer]
maturity: stable
updated: 2026-08-21
---

## Purpose

As an application layer grows, large service classes with many methods become hard to navigate and test in isolation. CQRS (Command Query Responsibility Segregation) with a mediator library like MediatR gives each use case its own small, independently testable handler, discoverable by convention rather than buried in a large class.

This skill covers applying CQRS pragmatically within a single data store (not necessarily separate read/write databases) using MediatR as the in-process mediator.

## When to use / When NOT to use

**Use this skill when:**

- The application layer has many distinct use cases that would benefit from isolation.
- You want cross-cutting concerns (logging, validation, transactions) applied consistently via pipeline behaviors.
- Multiple engineers work on different use cases concurrently and merge conflicts in large service classes are frequent.

**Do NOT use this skill when:**

- The application has only a handful of simple CRUD operations — plain service/repository methods are simpler.
- The team is unfamiliar with mediator patterns and the indirection would slow onboarding for a small project.

## Prerequisites

- skills/20-architecture/clean-and-onion-architecture/SKILL.md applied, since commands/queries live in the Application layer.
- MediatR (or equivalent) package referenced in the Application layer.
- skills/30-backend/validation-and-error-handling/SKILL.md for validation pipeline behavior.

## Workflow

1. **Define a command or query per use case** - One class per use case (PlaceOrderCommand, GetOrderByIdQuery) with only the data it needs.
2. **Write one handler per command/query** - Each handler implements IRequestHandler<TRequest, TResponse> and contains only that use case's orchestration logic.
3. **Keep handlers thin and focused** - Handlers orchestrate domain objects and repositories; business rules live in domain entities, not handlers.
4. **Add pipeline behaviors for cross-cutting concerns** - Validation, logging, and transaction wrapping applied uniformly via IPipelineBehavior, not duplicated per handler.
5. **Separate commands from queries clearly** - Commands mutate state and return minimal data (e.g. an ID); queries never mutate state.
6. **Register handlers via assembly scanning** - Use MediatR's service registration to auto-discover handlers instead of manually wiring each one.
7. **Test handlers in isolation** - Unit test each handler with mocked repositories/dependencies, independent of HTTP or the database.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Use case only reads data with no business logic | Model it as a query handler returning a DTO directly from a read-optimized query, not through domain entities. |
| Use case mutates state and enforces business rules | Model it as a command handler that loads an aggregate, calls domain methods, and persists changes. |
| Same validation logic needed across every command | Implement it once as a MediatR pipeline behavior (e.g. using FluentValidation) rather than per-handler. |
| A handler grows to orchestrate many unrelated steps | Split it into a domain service called by a leaner handler, or reconsider whether it is really one use case. |
| Read-heavy reporting query with complex joins | Consider Dapper (skills/30-backend/dapper-and-raw-sql/SKILL.md) for that specific query handler instead of forcing it through EF Core entities. |

## Reference implementation

A command and its handler following CQRS conventions:

```csharp
public record PlaceOrderCommand(Guid CustomerId, List<OrderLineDto> Lines)
    : IRequest<PlaceOrderResult>;

public class PlaceOrderCommandHandler : IRequestHandler<PlaceOrderCommand, PlaceOrderResult>
{
    private readonly IOrderRepository _orders;
    private readonly ICatalogQueries _catalog;

    public PlaceOrderCommandHandler(IOrderRepository orders, ICatalogQueries catalog)
    {
        _orders = orders;
        _catalog = catalog;
    }

    public async Task<PlaceOrderResult> Handle(PlaceOrderCommand request, CancellationToken ct)
    {
        var order = Order.Create(request.CustomerId);
        foreach (var line in request.Lines)
        {
            var product = await _catalog.GetProductAsync(line.ProductId)
                ?? throw new NotFoundException(nameof(Product), line.ProductId);
            order.AddLine(product.ToRef(), line.Quantity);
        }
        order.Submit();
        await _orders.AddAsync(order, ct);
        return new PlaceOrderResult(order.Id);
    }
}
```

- The handler orchestrates; AddLine and Submit enforce invariants inside the Order aggregate, not here.
- Register handlers with services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(typeof(PlaceOrderCommand).Assembly)).

### A validation pipeline behavior applied to every command (C#)

Cross-cutting validation without repeating logic in every handler:

```csharp
public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly IEnumerable<IValidator<TRequest>> _validators;
    public ValidationBehavior(IEnumerable<IValidator<TRequest>> validators) => _validators = validators;

    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next,
        CancellationToken ct)
    {
        var failures = _validators
            .Select(v => v.Validate(request))
            .SelectMany(r => r.Errors)
            .Where(e => e != null)
            .ToList();
        if (failures.Count != 0)
            throw new ValidationException(failures);
        return await next();
    }
}
```

## Checklist

- [ ] Each use case has its own command/query and handler, not a shared multi-method service class.
- [ ] Commands mutate state and return minimal data; queries never mutate state.
- [ ] Business rules live inside domain entities, not scattered across handler logic.
- [ ] Cross-cutting concerns (validation, logging, transactions) are pipeline behaviors, not duplicated per handler.
- [ ] Handlers are unit tested in isolation with mocked dependencies.
- [ ] Handler registration uses assembly scanning rather than manual per-handler wiring.

## Anti-patterns

- **Fat handlers** - Cramming business rules directly into a handler instead of delegating to domain entities, recreating an anemic-model problem inside MediatR.
- **CQRS as ceremony** - Introducing MediatR and command/query classes for a trivial CRUD app with no real benefit, adding indirection for its own sake.
- **Commands returning full entities** - Returning entire aggregate graphs from a command handler instead of the minimal result the caller actually needs.
- **Duplicated cross-cutting logic** - Re-implementing logging or validation inside every handler instead of a shared pipeline behavior.
- **Queries that mutate state** - Sneaking a side effect (like an audit log write) into a query handler, blurring the CQRS separation and surprising callers.

## Verification

- A new engineer can find the handler for any given use case by its command/query name alone.
- Unit tests exist for each handler's core logic without requiring a database or HTTP server.
- Validation, logging, and transaction behavior are demonstrably applied uniformly across handlers via pipeline tests.
- No query handler is found to mutate persisted state during code review.

## References

- MediatR documentation (Jimmy Bogard).
- skills/20-architecture/clean-and-onion-architecture/SKILL.md
- skills/30-backend/validation-and-error-handling/SKILL.md
- skills/20-architecture/domain-driven-design/SKILL.md
