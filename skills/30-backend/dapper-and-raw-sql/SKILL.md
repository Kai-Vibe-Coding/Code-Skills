---
name: dapper-and-raw-sql
description: Use when a query is performance-critical or too complex for clean LINQ expression and you need direct, well-parameterized SQL via a micro-ORM like Dapper.
category: backend
tags: [dapper, sql, performance]
maturity: stable
updated: 2026-08-21
---

## Purpose

Some queries — complex reports, bulk operations, or hot paths under heavy load — are clearer and faster written as raw, hand-tuned SQL than forced through an ORM's query translation. Dapper gives a thin, fast mapping layer between raw SQL and C# objects while still requiring discipline around parameterization and connection management.

This skill defines when to reach for Dapper instead of EF Core, and how to do so safely without reintroducing SQL injection or connection-leak risks.

## When to use / When NOT to use

**Use this skill when:**

- A reporting or analytics query involves multiple joins/aggregations that are unreadable or slow as LINQ.
- A hot-path query needs hand-tuned SQL (specific index hints, batched operations) for performance.
- Bulk read or write operations need to avoid EF Core's per-entity change tracking overhead.

**Do NOT use this skill when:**

- The query is a simple CRUD operation already well served by EF Core — don't bypass the ORM for its own sake.
- The team lacks SQL review discipline; raw SQL without careful review reintroduces injection and maintainability risk.

## Prerequisites

- skills/50-database/indexing-and-query-optimization/SKILL.md for tuning the underlying query.
- skills/80-security/input-validation-and-output-encoding/SKILL.md for parameterization discipline.
- A connection factory or scoped connection lifetime already established in Infrastructure.

## Workflow

1. **Identify the query that needs raw SQL** - Confirm via profiling or readability review that EF Core LINQ is the wrong tool for this specific query, not the whole layer.
2. **Write parameterized SQL only** - Always use Dapper's parameter objects; never string-concatenate user input into SQL text.
3. **Map results to purpose-built DTOs** - Query into a flat read-model class, not domain entities — Dapper queries are for reads, not aggregate reconstruction.
4. **Manage connections explicitly and briefly** - Open a connection per query/operation via a factory, and let `using` dispose it promptly.
5. **Use QueryMultiple for related result sets** - Fetch a parent and its children in a single round trip when the shape is well known, instead of N+1 separate calls.
6. **Wrap multi-statement writes in a transaction** - Use IDbTransaction explicitly when a raw-SQL write spans more than one statement that must succeed or fail together.
7. **Keep Dapper isolated to specific query handlers** - Confine raw-SQL usage to the handlers/repositories that need it; don't let it creep into general-purpose CRUD.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Read query is a straightforward filter/sort of one table | Use EF Core; Dapper adds no benefit here. |
| Read query aggregates across 5+ tables for a dashboard | Use Dapper with hand-written SQL and a flat result DTO. |
| Write operation must update thousands of rows efficiently | Use Dapper with a set-based UPDATE statement instead of loading and saving entities individually. |
| Query needs full-text search or database-specific functions | Use Dapper to call the database-specific SQL feature directly rather than fighting the ORM's LINQ translator. |
| Team is unsure whether raw SQL is warranted | Default to EF Core first; only switch to Dapper once profiling shows a concrete performance or readability problem. |

## Reference implementation

A parameterized Dapper query returning a flat DTO for a dashboard:

```csharp
public class OrderReportQueries : IOrderReportQueries
{
    private readonly IDbConnectionFactory _connectionFactory;
    public OrderReportQueries(IDbConnectionFactory connectionFactory) =>
        _connectionFactory = connectionFactory;

    public async Task<IReadOnlyList<CustomerSpendDto>> GetTopSpendersAsync(
        DateTime since, int take, CancellationToken ct)
    {
        const string sql = """
            SELECT c.Id AS CustomerId, c.Name,
                   SUM(ol.UnitPrice * ol.Quantity) AS TotalSpend
            FROM Orders o
            JOIN OrderLines ol ON ol.OrderId = o.Id
            JOIN Customers c ON c.Id = o.CustomerId
            WHERE o.SubmittedAt >= @Since
            GROUP BY c.Id, c.Name
            ORDER BY TotalSpend DESC
            LIMIT @Take
            """;

        using var conn = _connectionFactory.Create();
        var command = new CommandDefinition(sql, new { Since = since, Take = take },
            cancellationToken: ct);
        var rows = await conn.QueryAsync<CustomerSpendDto>(command);
        return rows.AsList();
    }
}
```

- @Since and @Take are bound parameters — never interpolate values directly into the sql string.
- CommandDefinition carries the CancellationToken through so long-running reports can be cancelled cleanly.

### A multi-statement write wrapped in an explicit transaction (C#)

Ensuring a batch update and audit insert succeed or fail together:

```csharp
using var conn = _connectionFactory.Create();
conn.Open();
using var tx = conn.BeginTransaction();
try
{
    await conn.ExecuteAsync(
        "UPDATE Orders SET Status = @Status WHERE Id = ANY(@Ids)",
        new { Status = "Archived", Ids = orderIds }, tx);
    await conn.ExecuteAsync(
        "INSERT INTO AuditLog (Action, Payload) VALUES (@Action, @Payload::jsonb)",
        new { Action = "BulkArchive", Payload = JsonSerializer.Serialize(orderIds) }, tx);
    tx.Commit();
}
catch { tx.Rollback(); throw; }
```

## Checklist

- [ ] Every Dapper query uses parameter objects; no string concatenation or interpolation of user input into SQL.
- [ ] Dapper queries return flat DTOs, not domain entities being reconstructed as aggregates.
- [ ] Connections are opened per operation and disposed promptly via `using`.
- [ ] Multi-statement writes use an explicit transaction with commit/rollback handling.
- [ ] Raw SQL usage is confined to specific, justified query handlers, not the default data-access approach.
- [ ] CancellationToken is passed through CommandDefinition for long-running queries.

## Anti-patterns

- **String-concatenated SQL** - Building SQL text by concatenating user input directly, reintroducing SQL injection risk that parameterized queries prevent.
- **Dapper for simple CRUD** - Using Dapper to replace all EF Core access 'for performance' without profiling data justifying the switch.
- **Long-lived shared connections** - Holding a single DbConnection open for the app's lifetime instead of opening/closing per operation, causing pool exhaustion.
- **Domain entities from raw SQL** - Populating full domain aggregates via Dapper and then calling repository.Add on them, bypassing invariant enforcement in constructors/factories.
- **Unversioned ad hoc SQL scattered in handlers** - Copy-pasting similar raw SQL across many handlers instead of centralizing shared report queries.

## Verification

- A security review or SAST scan confirms no raw string concatenation feeds into executed SQL.
- Profiling shows the target query's latency improved measurably versus the ORM-translated equivalent.
- Connections opened via Dapper are confirmed closed/disposed under load testing (no pool exhaustion).
- Code review confirms Dapper usage is limited to the specific queries that justified it.

## References

- Dapper documentation (StackExchange).
- skills/50-database/indexing-and-query-optimization/SKILL.md
- skills/80-security/input-validation-and-output-encoding/SKILL.md
- skills/30-backend/ef-core-data-access/SKILL.md
