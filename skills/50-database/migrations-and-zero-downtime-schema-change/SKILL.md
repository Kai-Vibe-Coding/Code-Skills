---
name: migrations-and-zero-downtime-schema-change
description: Use when a schema change must be deployed to a production database without taking the application offline or breaking currently running application instances.
category: database
tags: [migrations, zero-downtime, schema-evolution]
maturity: stable
updated: 2026-08-21
---

## Purpose

A schema change that locks a large table or that the currently deployed application code can't tolerate causes downtime or errors during rolling deployments. This skill covers the expand-contract pattern for evolving schemas safely: adding new structures alongside old ones, migrating data, switching reads/writes over, and only then removing the old structure once nothing depends on it.

It applies to any relational (and many document) database and assumes a rolling/blue-green deployment model where old and new application code briefly run simultaneously.

## When to use / When NOT to use

**Use this skill when:**

- You need to add, rename, or remove a column/table on a production database with a rolling deployment model.
- A migration would lock a large, frequently accessed table for more than a brief moment.
- Old and new application versions must both work correctly against the database during a rollout.

**Do NOT use this skill when:**

- The database is taken fully offline for maintenance windows and simple downtime is acceptable — a direct migration may be simpler.
- The table is small and the change (e.g. adding a nullable column) is inherently non-locking and backward compatible already.

## Prerequisites

- skills/30-backend/ef-core-data-access/SKILL.md or equivalent migration tooling for generating the migration itself.
- skills/60-devops/release-strategies/SKILL.md for the rolling/blue-green deployment model this pattern assumes.

## Workflow

1. **Classify the change as additive, destructive, or transformative** - Adding a nullable column is additive; dropping/renaming a column is destructive; changing a type is transformative.
2. **Expand: add new structures without removing old ones** - Add the new column/table alongside the existing one; both old and new code can still run correctly.
3. **Deploy application code that writes to both old and new structures** - Dual-write (or a trigger/backfill) so data stays consistent while both versions may be live.
4. **Backfill historical data** - Run a batched, throttled backfill job to populate the new structure for existing rows without locking the table.
5. **Deploy application code that reads from the new structure** - Switch reads over once the backfill is confirmed complete and consistent.
6. **Contract: remove the old structure only after full cutover** - Only after no running code references the old column/table, drop it in a later migration.
7. **Avoid long-held locks on large tables** - Use ALGORITHM=INPLACE/CONCURRENTLY-style options or add constraints as NOT VALID then VALIDATE separately to avoid full-table locks.
8. **Test the migration against a production-sized dataset** - Verify timing and locking behavior on a realistic data volume before running in production.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Adding a new nullable column | Usually safe as a single-step additive migration; no expand-contract needed. |
| Renaming a column | Never rename directly; add the new column, dual-write, backfill, cut over reads, then drop the old column in a later release. |
| Changing a column's type incompatibly | Add a new column with the new type, migrate data, cut over, then drop the old column — never ALTER TYPE directly on a large hot table. |
| Adding a NOT NULL constraint to an existing large table | Add it as NOT VALID (or equivalent) first, backfill/validate, then enforce it, avoiding a full-table lock and scan in one step. |
| Removing a column no longer used by any code | Confirm via deployment history that all instances of old code are fully retired before dropping it in a separate migration. |

## Reference implementation

Expand-contract steps for renaming a column without downtime (across 3 releases):

```sql
-- Release 1 (expand): add the new column, dual-write from application code
ALTER TABLE customers ADD COLUMN full_name VARCHAR(200);

-- Backfill in small batches to avoid long locks (run as a background job)
UPDATE customers SET full_name = name
WHERE full_name IS NULL AND id IN (
    SELECT id FROM customers WHERE full_name IS NULL LIMIT 1000
);

-- Release 2 (cut over): application code reads/writes full_name only,
-- old 'name' column still present but no longer written or read.

-- Release 3 (contract): once release 2 is fully rolled out and stable
ALTER TABLE customers DROP COLUMN name;
```

- Splitting across three releases ensures both old and new application versions always find a column they understand during a rolling deploy.
- Batched backfill (LIMIT 1000 loop) avoids locking the entire table for the duration of a large UPDATE.

### Adding a NOT NULL constraint without a full-table lock (PostgreSQL)

Validating the constraint separately from adding it, avoiding a blocking full scan in one step:

```sql
ALTER TABLE orders ADD CONSTRAINT chk_orders_status_not_null
    CHECK (status IS NOT NULL) NOT VALID;

-- Runs as a separate, non-blocking validation pass once backfill is complete:
ALTER TABLE orders VALIDATE CONSTRAINT chk_orders_status_not_null;
```

## Checklist

- [ ] Destructive or transformative changes (rename, type change) use the expand-contract pattern across multiple releases.
- [ ] Backfills run in small batches to avoid holding long locks on large tables.
- [ ] Both old and new application code can run correctly against the schema at every point during a rolling deploy.
- [ ] Large-table constraints are added as NOT VALID and validated separately rather than in one blocking step.
- [ ] The migration has been tested against a production-representative data volume for timing and locking behavior.
- [ ] Old structures are dropped only after confirming no running code references them.

## Anti-patterns

- **Rename in a single migration** - Renaming a column directly in one release, breaking any application instance still running the old code during a rolling deploy.
- **Unbatched backfill of a huge table** - Running a single UPDATE across millions of rows, holding locks and blocking other queries for the duration.
- **Adding NOT NULL directly on a large table** - ALTER COLUMN ... SET NOT NULL in one step on a huge table, causing a full-table scan and lock.
- **Dropping a column before confirming cutover** - Removing an old column while some deployed instances still read/write it, causing runtime errors.
- **No production-scale testing** - Testing a migration only against a tiny dev database, missing lock/timing issues that only appear at real data volume.

## Verification

- A rolling deployment through the expand phase shows zero errors from either old or new application code.
- Migration execution time and lock duration were measured against a production-representative dataset before the production run.
- The contract (removal) step only ran after confirming, via deployment/monitoring history, that no code referenced the old structure.
- No migration step held a lock long enough to cause visible request timeouts in production.

## References

- skills/60-devops/release-strategies/SKILL.md
- skills/30-backend/ef-core-data-access/SKILL.md
- PostgreSQL documentation — ALTER TABLE and NOT VALID constraints.
