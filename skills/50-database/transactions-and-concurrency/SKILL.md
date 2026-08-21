---
name: transactions-and-concurrency
description: Use when multiple concurrent operations read and write shared data and you need to choose the right transaction isolation level and locking strategy to prevent anomalies.
category: database
tags: [transactions, concurrency, isolation-levels]
maturity: stable
updated: 2026-08-21
---

## Purpose

Incorrect transaction boundaries or isolation levels cause subtle bugs like lost updates, dirty reads, or phantom rows that only appear under real concurrent load, long after a feature ships. This skill covers choosing an appropriate isolation level, applying optimistic or pessimistic concurrency control, and structuring transactions to avoid deadlocks.

It emphasizes reasoning about concurrent access explicitly during design, since these bugs are notoriously hard to reproduce and debug after the fact in production.

## When to use / When NOT to use

**Use this skill when:**

- Multiple users or processes can read and write the same row(s) concurrently.
- A 'lost update' or stale-data bug has been reported that only reproduces under load.
- You are designing a use case involving a check-then-act sequence (e.g. check inventory, then reserve it).

**Do NOT use this skill when:**

- The data is effectively single-writer (e.g. one background job is the only writer) — standard transactions suffice without special concurrency handling.
- You're optimizing raw query speed rather than correctness under concurrency — see skills/50-database/indexing-and-query-optimization/SKILL.md instead.

## Prerequisites

- skills/20-architecture/domain-driven-design/SKILL.md for aggregate boundaries, since a transaction typically should not span multiple aggregates.
- Understanding of the standard isolation levels (Read Committed, Repeatable Read, Serializable).

## Workflow

1. **Identify check-then-act sequences** - Any 'read a value, decide, then write' sequence is vulnerable to a race unless protected.
2. **Default to optimistic concurrency for low-contention scenarios** - Add a row version/RowVersion column, and fail the update if the version doesn't match what was read.
3. **Use pessimistic locking for high-contention hot rows** - SELECT ... FOR UPDATE (or equivalent) to lock a row for the duration of a transaction when conflicts are frequent and retries are expensive.
4. **Choose the isolation level deliberately per use case** - Read Committed is a reasonable default; escalate to Repeatable Read or Serializable only for specific operations that need stronger guarantees.
5. **Keep transactions short** - Do the minimum necessary work inside a transaction; avoid calling external services (HTTP, email) while holding a database transaction open.
6. **Order lock acquisition consistently to avoid deadlocks** - If a use case must lock multiple rows/tables, always acquire them in the same order across all code paths.
7. **Handle concurrency conflicts explicitly at the application layer** - Catch a version-mismatch/deadlock exception and retry or surface a clear 'someone else changed this' error to the user.
8. **Test concurrent scenarios directly** - Write a test that fires two concurrent updates at the same row and asserts one wins and the other detects the conflict.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Two users might edit the same record around the same time, rarely | Use optimistic concurrency (row version) — conflicts are rare and a retry/error message is acceptable. |
| Many concurrent processes reserve limited inventory for the same product | Use pessimistic row locking (SELECT FOR UPDATE) since contention is expected and frequent. |
| A report needs a consistent snapshot across several queries | Use a Repeatable Read (or Snapshot) isolation transaction, not the default Read Committed, for that specific report. |
| A financial transfer between two accounts must never lose money | Use Serializable isolation or explicit locking with a consistent lock order to prevent both lost updates and deadlocks. |
| A transaction is calling an external HTTP API mid-transaction | Move the external call outside the transaction boundary; never hold a DB transaction open across a network call to another system. |

## Reference implementation

Optimistic concurrency using a row version column with EF Core:

```csharp
public class Order
{
    public Guid Id { get; private set; }
    public OrderStatus Status { get; private set; }
    [Timestamp] public byte[] RowVersion { get; private set; } = default!;
}

try
{
    order.MarkShipped();
    await db.SaveChangesAsync(ct);
}
catch (DbUpdateConcurrencyException)
{
    // Another process changed this order since it was loaded.
    throw new ConflictException("Order was modified concurrently; please retry.");
}
```

- EF Core includes RowVersion in the WHERE clause of the UPDATE statement; a mismatch means zero rows affected, which EF surfaces as DbUpdateConcurrencyException.
- This approach requires no locks held between read and write, keeping throughput high for the common non-conflicting case.

### Pessimistic row locking for high-contention inventory reservation (SQL)

Locking the row for the duration of the transaction when conflicts are frequent:

```sql
BEGIN;
SELECT quantity_available FROM inventory
WHERE product_id = $1 FOR UPDATE;
-- Application checks quantity_available >= requested here
UPDATE inventory SET quantity_available = quantity_available - $2
WHERE product_id = $1;
COMMIT;
```

## Checklist

- [ ] Every check-then-act sequence against shared data is protected by optimistic or pessimistic concurrency control.
- [ ] Isolation level is chosen deliberately per use case, not left at whatever the driver defaults to without consideration.
- [ ] Transactions are kept short and never span an external network call (HTTP, email, message publish).
- [ ] Lock acquisition order is consistent across all code paths that lock multiple rows/tables, preventing deadlocks.
- [ ] Concurrency conflicts are caught explicitly and surfaced as a clear retry/conflict error, not an unhandled exception.
- [ ] A concurrent-access test exists for at least the highest-risk check-then-act use cases.

## Anti-patterns

- **No concurrency control at all** - Reading a value, deciding based on it, and writing back with no version check or lock, allowing silent lost updates.
- **Long-held transactions spanning external calls** - Keeping a database transaction open while waiting on an HTTP call to another service, holding locks far longer than necessary.
- **Inconsistent lock ordering** - Locking table A then B in one code path and B then A in another, creating a classic deadlock scenario.
- **Always using Serializable 'to be safe'** - Defaulting every transaction to Serializable isolation, adding unnecessary contention and abort rates for cases that didn't need it.
- **Swallowing concurrency exceptions** - Catching a DbUpdateConcurrencyException and silently retrying with stale data instead of re-reading and re-validating.

## Verification

- A test firing two concurrent updates at the same row confirms one succeeds and the other detects a conflict rather than silently overwriting.
- No transaction in the codebase holds open across an external network call, confirmed by code review.
- A deadlock-inducing concurrent test (locking two shared resources in different orders) either doesn't occur or is handled with a documented consistent lock order.
- Isolation level choices are documented for any use case that deviates from the default.

## References

- skills/20-architecture/domain-driven-design/SKILL.md
- skills/20-architecture/resilience-patterns/SKILL.md
- PostgreSQL / SQL Server documentation on transaction isolation levels.
