---
name: repository-unit-of-work-specification
description: Use when your application layer needs to query and persist aggregates without depending on EF Core or a specific ORM directly.
category: backend
tags: [repository, unit-of-work, specification-pattern]
maturity: stable
updated: 2026-08-21
---

## Purpose

Coupling the Application layer directly to an ORM's DbContext leaks infrastructure concerns into business logic and makes unit testing without a real database difficult. The Repository and Unit of Work patterns, combined with a Specification pattern for composable queries, give the Application layer a persistence-ignorant contract for loading and saving aggregates.

This skill defines when repositories add real value versus when they become a needless abstraction over an ORM that already implements those patterns internally.

## When to use / When NOT to use

**Use this skill when:**

- The Application layer needs to remain testable without a real database.
- You may need to swap or add a persistence technology later (e.g. adding a cache-backed repository).
- Aggregate loading involves consistent, reusable query logic (specifications) across multiple use cases.

**Do NOT use this skill when:**

- The application is small, uses EF Core exclusively, and DbContext-as-repository is well understood by the team.
- You need highly tuned, one-off read queries — use skills/30-backend/dapper-and-raw-sql/SKILL.md for those instead of forcing them through a repository abstraction.

## Prerequisites

- skills/20-architecture/domain-driven-design/SKILL.md for aggregate boundaries the repository operates on.
- skills/30-backend/ef-core-data-access/SKILL.md if EF Core is the underlying implementation.
- Understanding of the Unit of Work pattern for transaction boundaries.

## Workflow

1. **Define one repository interface per aggregate root** - IOrderRepository, not a generic IRepository<T> for every entity — repositories operate at the aggregate boundary.
2. **Keep repository methods aggregate-oriented** - AddAsync, GetByIdAsync, and methods returning whole aggregates, not arbitrary partial projections.
3. **Introduce specifications for reusable query logic** - Encapsulate criteria like 'orders pending fulfillment older than 3 days' as a named Specification<Order> class.
4. **Define IUnitOfWork for transaction boundaries** - A single SaveChangesAsync call commits everything a use case changed, keeping the transaction boundary explicit.
5. **Implement repositories in Infrastructure** - Concrete EF Core (or Dapper) implementations live in Infrastructure and are injected via DI.
6. **Use in-memory fakes for Application-layer unit tests** - Test handlers against a simple in-memory implementation of the repository interface, not a real database.
7. **Reserve read-only projections for query handlers** - Queries that only need a DTO shape can bypass repositories and use a dedicated read model or Dapper query.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Aggregate load-and-save is straightforward | Use a plain repository interface with GetByIdAsync/AddAsync/Update methods. |
| Query criteria is reused across several use cases | Extract it into a named Specification class rather than duplicating LINQ expressions. |
| A read query just needs a flat DTO for a UI list | Skip the repository and aggregate entirely; use a dedicated query handler with Dapper or EF Core projection. |
| Team already trusts DbContext as the Unit of Work | It's acceptable to inject DbContext directly as IUnitOfWork rather than build a redundant wrapper. |
| Generic IRepository<T> for every entity is tempting | Resist it — it leaks CRUD-on-anything semantics that erode aggregate boundaries; scope repositories to aggregate roots only. |

## Reference implementation

An aggregate-scoped repository interface with a specification-based query method:

```csharp
public interface IOrderRepository
{
    Task<Order?> GetByIdAsync(Guid id, CancellationToken ct = default);
    Task<IReadOnlyList<Order>> FindAsync(ISpecification<Order> spec, CancellationToken ct = default);
    Task AddAsync(Order order, CancellationToken ct = default);
    void Remove(Order order);
}

public interface ISpecification<T>
{
    Expression<Func<T, bool>> Criteria { get; }
    List<Expression<Func<T, object>>> Includes { get; }
}

public class PendingFulfillmentSpec : ISpecification<Order>
{
    public Expression<Func<Order, bool>> Criteria { get; }
    public List<Expression<Func<Order, object>>> Includes { get; } = new() { o => o.Lines };

    public PendingFulfillmentSpec(TimeSpan olderThan)
    {
        var cutoff = DateTime.UtcNow - olderThan;
        Criteria = o => o.Status == OrderStatus.Submitted && o.SubmittedAt < cutoff;
    }
}
```

- Includes lets a specification declare its own eager-loading needs without leaking EF Core details to callers.
- The interface itself has zero EF Core or Dapper references, keeping the Application layer persistence-ignorant.

### Unit of Work committing changes across repositories (C#)

A single commit point per use case, regardless of how many repositories were touched:

```csharp
public interface IUnitOfWork
{
    Task<int> SaveChangesAsync(CancellationToken ct = default);
}

public class EfUnitOfWork : IUnitOfWork
{
    private readonly AppDbContext _db;
    public EfUnitOfWork(AppDbContext db) => _db = db;

    public Task<int> SaveChangesAsync(CancellationToken ct = default) =>
        _db.SaveChangesAsync(ct);
}

// In a handler:
await _orders.AddAsync(order, ct);
await _unitOfWork.SaveChangesAsync(ct); // one commit for the whole use case
```

## Checklist

- [ ] Repository interfaces are scoped to aggregate roots, not one per table.
- [ ] No generic IRepository<T> is used for arbitrary entities across bounded contexts.
- [ ] Reusable query criteria are captured in named Specification classes.
- [ ] A single Unit of Work commit point exists per use case/transaction.
- [ ] Application-layer handler tests run against an in-memory fake repository, without a real database.
- [ ] Flat read queries bypass the repository/aggregate pattern entirely.

## Anti-patterns

- **Generic CRUD repository** - IRepository<T> with Get/Add/Update/Delete for every entity, encouraging cross-aggregate mutation that violates consistency boundaries.
- **Repository leaking IQueryable** - Exposing IQueryable<Order> from the repository interface, letting callers build arbitrary EF-specific queries and defeating the abstraction's purpose.
- **One SaveChanges per repository call** - Calling SaveChangesAsync inside every repository method instead of once per use case, fragmenting the transaction boundary.
- **Repositories for pure read DTOs** - Forcing list/report queries through aggregate-oriented repositories instead of a lightweight query handler.
- **Duplicated query criteria** - Copy-pasting the same LINQ filter across multiple handlers instead of extracting a Specification.

## Verification

- Every repository interface maps 1:1 to an aggregate root, verified during code review.
- Application-layer unit tests pass using in-memory fake repositories with no database connection.
- A single SaveChangesAsync/commit call exists per use case in each command handler.
- No repository interface exposes IQueryable or leaks ORM-specific types to the Application layer.

## References

- skills/20-architecture/domain-driven-design/SKILL.md
- skills/30-backend/ef-core-data-access/SKILL.md
- Martin Fowler — Repository and Unit of Work patterns (Patterns of Enterprise Application Architecture).
