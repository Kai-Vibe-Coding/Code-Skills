---
name: indexing-and-query-optimization
description: Use when a database query is slow and you need to diagnose the cause using execution plans and apply the correct indexing or query rewrite.
category: database
tags: [indexing, query-optimization, performance]
maturity: stable
updated: 2026-08-21
---

## Purpose

Slow queries are one of the most common production performance issues, and guessing at fixes without reading an execution plan often makes things worse. This skill covers reading query execution plans, choosing the right index type and column order, and recognizing common query patterns (implicit conversions, leading wildcards, unindexed foreign keys) that defeat indexing.

It treats indexing as a targeted response to a measured problem, not something to apply speculatively to every column, since excessive indexing slows down writes and bloats storage.

## When to use / When NOT to use

**Use this skill when:**

- A specific query or endpoint has been identified as slow via monitoring or user reports.
- You are reviewing a new query pattern before it goes to production at scale.
- Database CPU/IO is high and you need to identify which queries are responsible.

**Do NOT use this skill when:**

- No query has been measured as slow — don't add speculative indexes without evidence.
- The bottleneck is actually network or application-layer serialization, not the database — profile the whole request path first.

## Prerequisites

- skills/50-database/relational-data-modeling/SKILL.md for the schema the query runs against.
- Access to EXPLAIN ANALYZE (or the database's equivalent) and a representative dataset size for testing.

## Workflow

1. **Reproduce the slow query with EXPLAIN ANALYZE** - Get the actual execution plan against production-representative data volume, not a tiny dev database.
2. **Identify sequential scans on large tables** - A Seq Scan on a large table in a selective WHERE clause usually indicates a missing or unused index.
3. **Check index column order for composite indexes** - Lead with the column(s) used in equality filters, then range filters, matching the query's actual predicates.
4. **Verify the index is actually being used** - A plan may show Seq Scan even with an index present if statistics are stale or the predicate defeats index usage (e.g. wrapping a column in a function).
5. **Avoid patterns that defeat indexes** - Leading wildcard LIKE '%x', implicit type conversions, and functions applied to indexed columns typically prevent index usage.
6. **Consider covering indexes for read-heavy hot paths** - Include all columns a query needs so the database can answer from the index alone without a table lookup.
7. **Re-run EXPLAIN ANALYZE after each change** - Confirm the plan actually improved and measure real latency, not just assume the fix worked.
8. **Update table statistics regularly** - Ensure the query planner has fresh statistics (ANALYZE) so it makes good decisions about index usage.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A WHERE clause filters on one column with high selectivity | Add a single-column B-tree index on that column. |
| A WHERE clause filters on two columns together frequently | Add a composite index with the equality-filtered column first. |
| A query needs full-text search | Use a dedicated full-text/GIN index rather than LIKE '%term%' on an unindexed column. |
| A read-heavy query only needs a few columns | Consider a covering index including those columns to avoid a table heap lookup. |
| An index exists but isn't being used | Check for stale statistics, a function wrapping the column, or a type mismatch before adding a redundant index. |

## Reference implementation

Diagnosing a slow query and adding a targeted composite index:

```sql
EXPLAIN ANALYZE
SELECT id, status, submitted_at
FROM orders
WHERE customer_id = '11111111-1111-1111-1111-111111111111'
  AND status = 'Submitted'
ORDER BY submitted_at DESC
LIMIT 20;
-- Plan shows: Seq Scan on orders (cost=... rows=500000) -- confirms missing index

CREATE INDEX idx_orders_customer_status_submitted
    ON orders (customer_id, status, submitted_at DESC);

-- Re-run EXPLAIN ANALYZE: plan should now show
-- Index Scan using idx_orders_customer_status_submitted (cost=... rows=12)
```

- Column order matches the query: equality filters (customer_id, status) first, then the sort column (submitted_at) last.
- Including submitted_at DESC in the index lets the database satisfy ORDER BY without a separate sort step.

### A pattern that silently defeats an existing index (SQL)

Wrapping an indexed column in a function prevents the planner from using a plain index on it:

```sql
-- Defeats an index on submitted_at:
SELECT * FROM orders WHERE DATE(submitted_at) = '2026-01-01';

-- Index-friendly rewrite using a range instead of a function on the column:
SELECT * FROM orders
WHERE submitted_at >= '2026-01-01' AND submitted_at < '2026-01-02';
```

## Checklist

- [ ] Every index added is backed by an EXPLAIN ANALYZE showing a measured problem, not a speculative guess.
- [ ] Composite index column order matches actual query predicates (equality first, then range/sort).
- [ ] Query patterns avoid wrapping indexed columns in functions or leading wildcards that defeat index usage.
- [ ] Table statistics are kept current so the query planner makes informed decisions.
- [ ] Each optimization is re-verified with EXPLAIN ANALYZE and real latency measurement after the change.
- [ ] Write-path impact (extra indexes slow inserts/updates) is considered before adding an index.

## Anti-patterns

- **Indexing every column speculatively** - Adding an index to every column 'just in case', bloating storage and slowing down every write.
- **Guessing without EXPLAIN ANALYZE** - Adding an index based on intuition alone without confirming the actual execution plan showed a problem.
- **Function-wrapped predicates on indexed columns** - Writing WHERE LOWER(email) = ... against a plain index on email, silently forcing a sequential scan.
- **Leading wildcard searches** - Using LIKE '%term' on a large table, which cannot use a standard B-tree index efficiently.
- **Stale statistics ignored** - Never running ANALYZE after bulk data loads, leaving the query planner with outdated row-count estimates.

## Verification

- EXPLAIN ANALYZE for the target query shows an Index Scan (or equivalent) instead of a Seq Scan on the large table.
- Measured query latency improves meaningfully after the index/rewrite, confirmed under representative data volume.
- Write-path latency (INSERT/UPDATE) on the affected table has not regressed unacceptably after adding the index.
- No new index duplicates the leading columns of an existing index unnecessarily.

## References

- skills/50-database/relational-data-modeling/SKILL.md
- Use The Index, Luke! (use-the-index-luke.com).
- PostgreSQL / SQL Server documentation on EXPLAIN and index types.
