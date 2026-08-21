SKILLS = [
    dict(
        dir="50-database", slug="migrations-and-zero-downtime-schema-change", category="database",
        tags=["migrations", "zero-downtime", "schema-evolution"],
        desc="Use when a schema change must be deployed to a production database without taking the application offline or breaking currently running application instances.",
        purpose=[
            "A schema change that locks a large table or that the currently deployed application code can't "
            "tolerate causes downtime or errors during rolling deployments. This skill covers the "
            "expand-contract pattern for evolving schemas safely: adding new structures alongside old ones, "
            "migrating data, switching reads/writes over, and only then removing the old structure once "
            "nothing depends on it.",
            "It applies to any relational (and many document) database and assumes a rolling/blue-green "
            "deployment model where old and new application code briefly run simultaneously.",
        ],
        when_use=[
            "You need to add, rename, or remove a column/table on a production database with a rolling deployment model.",
            "A migration would lock a large, frequently accessed table for more than a brief moment.",
            "Old and new application versions must both work correctly against the database during a rollout.",
        ],
        when_not=[
            "The database is taken fully offline for maintenance windows and simple downtime is acceptable — a direct migration may be simpler.",
            "The table is small and the change (e.g. adding a nullable column) is inherently non-locking and backward compatible already.",
        ],
        prereqs=[
            "skills/30-backend/ef-core-data-access/SKILL.md or equivalent migration tooling for generating the migration itself.",
            "skills/60-devops/release-strategies/SKILL.md for the rolling/blue-green deployment model this pattern assumes.",
        ],
        workflow=[
            ("Classify the change as additive, destructive, or transformative", "Adding a nullable column is additive; dropping/renaming a column is destructive; changing a type is transformative."),
            ("Expand: add new structures without removing old ones", "Add the new column/table alongside the existing one; both old and new code can still run correctly."),
            ("Deploy application code that writes to both old and new structures", "Dual-write (or a trigger/backfill) so data stays consistent while both versions may be live."),
            ("Backfill historical data", "Run a batched, throttled backfill job to populate the new structure for existing rows without locking the table."),
            ("Deploy application code that reads from the new structure", "Switch reads over once the backfill is confirmed complete and consistent."),
            ("Contract: remove the old structure only after full cutover", "Only after no running code references the old column/table, drop it in a later migration."),
            ("Avoid long-held locks on large tables", "Use ALGORITHM=INPLACE/CONCURRENTLY-style options or add constraints as NOT VALID then VALIDATE separately to avoid full-table locks."),
            ("Test the migration against a production-sized dataset", "Verify timing and locking behavior on a realistic data volume before running in production."),
        ],
        decision=[
            ("Adding a new nullable column", "Usually safe as a single-step additive migration; no expand-contract needed."),
            ("Renaming a column", "Never rename directly; add the new column, dual-write, backfill, cut over reads, then drop the old column in a later release."),
            ("Changing a column's type incompatibly", "Add a new column with the new type, migrate data, cut over, then drop the old column — never ALTER TYPE directly on a large hot table."),
            ("Adding a NOT NULL constraint to an existing large table", "Add it as NOT VALID (or equivalent) first, backfill/validate, then enforce it, avoiding a full-table lock and scan in one step."),
            ("Removing a column no longer used by any code", "Confirm via deployment history that all instances of old code are fully retired before dropping it in a separate migration."),
        ],
        code_lang="sql",
        code_intro="Expand-contract steps for renaming a column without downtime (across 3 releases):",
        code=(
            "-- Release 1 (expand): add the new column, dual-write from application code\n"
            "ALTER TABLE customers ADD COLUMN full_name VARCHAR(200);\n"
            "\n"
            "-- Backfill in small batches to avoid long locks (run as a background job)\n"
            "UPDATE customers SET full_name = name\n"
            "WHERE full_name IS NULL AND id IN (\n"
            "    SELECT id FROM customers WHERE full_name IS NULL LIMIT 1000\n"
            ");\n"
            "\n"
            "-- Release 2 (cut over): application code reads/writes full_name only,\n"
            "-- old 'name' column still present but no longer written or read.\n"
            "\n"
            "-- Release 3 (contract): once release 2 is fully rolled out and stable\n"
            "ALTER TABLE customers DROP COLUMN name;\n"
        ),
        code_notes=[
            "Splitting across three releases ensures both old and new application versions always find a column they understand during a rolling deploy.",
            "Batched backfill (LIMIT 1000 loop) avoids locking the entire table for the duration of a large UPDATE.",
        ],
        code2_heading="Adding a NOT NULL constraint without a full-table lock (PostgreSQL)",
        code2=("sql",
            "Validating the constraint separately from adding it, avoiding a blocking full scan in one step:",
            "ALTER TABLE orders ADD CONSTRAINT chk_orders_status_not_null\n"
            "    CHECK (status IS NOT NULL) NOT VALID;\n"
            "\n"
            "-- Runs as a separate, non-blocking validation pass once backfill is complete:\n"
            "ALTER TABLE orders VALIDATE CONSTRAINT chk_orders_status_not_null;\n"
        ),
        checklist=[
            "Destructive or transformative changes (rename, type change) use the expand-contract pattern across multiple releases.",
            "Backfills run in small batches to avoid holding long locks on large tables.",
            "Both old and new application code can run correctly against the schema at every point during a rolling deploy.",
            "Large-table constraints are added as NOT VALID and validated separately rather than in one blocking step.",
            "The migration has been tested against a production-representative data volume for timing and locking behavior.",
            "Old structures are dropped only after confirming no running code references them.",
        ],
        antipatterns=[
            ("Rename in a single migration", "Renaming a column directly in one release, breaking any application instance still running the old code during a rolling deploy."),
            ("Unbatched backfill of a huge table", "Running a single UPDATE across millions of rows, holding locks and blocking other queries for the duration."),
            ("Adding NOT NULL directly on a large table", "ALTER COLUMN ... SET NOT NULL in one step on a huge table, causing a full-table scan and lock."),
            ("Dropping a column before confirming cutover", "Removing an old column while some deployed instances still read/write it, causing runtime errors."),
            ("No production-scale testing", "Testing a migration only against a tiny dev database, missing lock/timing issues that only appear at real data volume."),
        ],
        verification=[
            "A rolling deployment through the expand phase shows zero errors from either old or new application code.",
            "Migration execution time and lock duration were measured against a production-representative dataset before the production run.",
            "The contract (removal) step only ran after confirming, via deployment/monitoring history, that no code referenced the old structure.",
            "No migration step held a lock long enough to cause visible request timeouts in production.",
        ],
        references=[
            "skills/60-devops/release-strategies/SKILL.md",
            "skills/30-backend/ef-core-data-access/SKILL.md",
            "PostgreSQL documentation — ALTER TABLE and NOT VALID constraints.",
        ],
    ),
    dict(
        dir="50-database", slug="transactions-and-concurrency", category="database",
        tags=["transactions", "concurrency", "isolation-levels"],
        desc="Use when multiple concurrent operations read and write shared data and you need to choose the right transaction isolation level and locking strategy to prevent anomalies.",
        purpose=[
            "Incorrect transaction boundaries or isolation levels cause subtle bugs like lost updates, dirty "
            "reads, or phantom rows that only appear under real concurrent load, long after a feature ships. "
            "This skill covers choosing an appropriate isolation level, applying optimistic or pessimistic "
            "concurrency control, and structuring transactions to avoid deadlocks.",
            "It emphasizes reasoning about concurrent access explicitly during design, since these bugs are "
            "notoriously hard to reproduce and debug after the fact in production.",
        ],
        when_use=[
            "Multiple users or processes can read and write the same row(s) concurrently.",
            "A 'lost update' or stale-data bug has been reported that only reproduces under load.",
            "You are designing a use case involving a check-then-act sequence (e.g. check inventory, then reserve it).",
        ],
        when_not=[
            "The data is effectively single-writer (e.g. one background job is the only writer) — standard transactions suffice without special concurrency handling.",
            "You're optimizing raw query speed rather than correctness under concurrency — see skills/50-database/indexing-and-query-optimization/SKILL.md instead.",
        ],
        prereqs=[
            "skills/20-architecture/domain-driven-design/SKILL.md for aggregate boundaries, since a transaction typically should not span multiple aggregates.",
            "Understanding of the standard isolation levels (Read Committed, Repeatable Read, Serializable).",
        ],
        workflow=[
            ("Identify check-then-act sequences", "Any 'read a value, decide, then write' sequence is vulnerable to a race unless protected."),
            ("Default to optimistic concurrency for low-contention scenarios", "Add a row version/RowVersion column, and fail the update if the version doesn't match what was read."),
            ("Use pessimistic locking for high-contention hot rows", "SELECT ... FOR UPDATE (or equivalent) to lock a row for the duration of a transaction when conflicts are frequent and retries are expensive."),
            ("Choose the isolation level deliberately per use case", "Read Committed is a reasonable default; escalate to Repeatable Read or Serializable only for specific operations that need stronger guarantees."),
            ("Keep transactions short", "Do the minimum necessary work inside a transaction; avoid calling external services (HTTP, email) while holding a database transaction open."),
            ("Order lock acquisition consistently to avoid deadlocks", "If a use case must lock multiple rows/tables, always acquire them in the same order across all code paths."),
            ("Handle concurrency conflicts explicitly at the application layer", "Catch a version-mismatch/deadlock exception and retry or surface a clear 'someone else changed this' error to the user."),
            ("Test concurrent scenarios directly", "Write a test that fires two concurrent updates at the same row and asserts one wins and the other detects the conflict."),
        ],
        decision=[
            ("Two users might edit the same record around the same time, rarely", "Use optimistic concurrency (row version) — conflicts are rare and a retry/error message is acceptable."),
            ("Many concurrent processes reserve limited inventory for the same product", "Use pessimistic row locking (SELECT FOR UPDATE) since contention is expected and frequent."),
            ("A report needs a consistent snapshot across several queries", "Use a Repeatable Read (or Snapshot) isolation transaction, not the default Read Committed, for that specific report."),
            ("A financial transfer between two accounts must never lose money", "Use Serializable isolation or explicit locking with a consistent lock order to prevent both lost updates and deadlocks."),
            ("A transaction is calling an external HTTP API mid-transaction", "Move the external call outside the transaction boundary; never hold a DB transaction open across a network call to another system."),
        ],
        code_lang="csharp",
        code_intro="Optimistic concurrency using a row version column with EF Core:",
        code=(
            "public class Order\n"
            "{\n"
            "    public Guid Id { get; private set; }\n"
            "    public OrderStatus Status { get; private set; }\n"
            "    [Timestamp] public byte[] RowVersion { get; private set; } = default!;\n"
            "}\n"
            "\n"
            "try\n"
            "{\n"
            "    order.MarkShipped();\n"
            "    await db.SaveChangesAsync(ct);\n"
            "}\n"
            "catch (DbUpdateConcurrencyException)\n"
            "{\n"
            "    // Another process changed this order since it was loaded.\n"
            "    throw new ConflictException(\"Order was modified concurrently; please retry.\");\n"
            "}\n"
        ),
        code_notes=[
            "EF Core includes RowVersion in the WHERE clause of the UPDATE statement; a mismatch means zero rows affected, which EF surfaces as DbUpdateConcurrencyException.",
            "This approach requires no locks held between read and write, keeping throughput high for the common non-conflicting case.",
        ],
        code2_heading="Pessimistic row locking for high-contention inventory reservation (SQL)",
        code2=("sql",
            "Locking the row for the duration of the transaction when conflicts are frequent:",
            "BEGIN;\n"
            "SELECT quantity_available FROM inventory\n"
            "WHERE product_id = $1 FOR UPDATE;\n"
            "-- Application checks quantity_available >= requested here\n"
            "UPDATE inventory SET quantity_available = quantity_available - $2\n"
            "WHERE product_id = $1;\n"
            "COMMIT;\n"
        ),
        checklist=[
            "Every check-then-act sequence against shared data is protected by optimistic or pessimistic concurrency control.",
            "Isolation level is chosen deliberately per use case, not left at whatever the driver defaults to without consideration.",
            "Transactions are kept short and never span an external network call (HTTP, email, message publish).",
            "Lock acquisition order is consistent across all code paths that lock multiple rows/tables, preventing deadlocks.",
            "Concurrency conflicts are caught explicitly and surfaced as a clear retry/conflict error, not an unhandled exception.",
            "A concurrent-access test exists for at least the highest-risk check-then-act use cases.",
        ],
        antipatterns=[
            ("No concurrency control at all", "Reading a value, deciding based on it, and writing back with no version check or lock, allowing silent lost updates."),
            ("Long-held transactions spanning external calls", "Keeping a database transaction open while waiting on an HTTP call to another service, holding locks far longer than necessary."),
            ("Inconsistent lock ordering", "Locking table A then B in one code path and B then A in another, creating a classic deadlock scenario."),
            ("Always using Serializable 'to be safe'", "Defaulting every transaction to Serializable isolation, adding unnecessary contention and abort rates for cases that didn't need it."),
            ("Swallowing concurrency exceptions", "Catching a DbUpdateConcurrencyException and silently retrying with stale data instead of re-reading and re-validating."),
        ],
        verification=[
            "A test firing two concurrent updates at the same row confirms one succeeds and the other detects a conflict rather than silently overwriting.",
            "No transaction in the codebase holds open across an external network call, confirmed by code review.",
            "A deadlock-inducing concurrent test (locking two shared resources in different orders) either doesn't occur or is handled with a documented consistent lock order.",
            "Isolation level choices are documented for any use case that deviates from the default.",
        ],
        references=[
            "skills/20-architecture/domain-driven-design/SKILL.md",
            "skills/20-architecture/resilience-patterns/SKILL.md",
            "PostgreSQL / SQL Server documentation on transaction isolation levels.",
        ],
    ),
]
