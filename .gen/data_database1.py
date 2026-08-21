SKILLS = [
    dict(
        dir="50-database", slug="relational-data-modeling", category="database",
        tags=["data-modeling", "normalization", "schema-design"],
        desc="Use when designing a new relational schema or evaluating an existing one for normalization, key design, and referential integrity correctness.",
        purpose=[
            "A poorly modeled relational schema causes data anomalies, slow queries, and painful migrations "
            "later. This skill covers normalizing data to remove redundancy and update anomalies, choosing "
            "appropriate primary/foreign key strategies, and deliberately denormalizing only where a "
            "measured read pattern justifies it.",
            "It treats normalization as a starting discipline, not a religion — the goal is a schema that "
            "protects data integrity while still serving the application's actual query patterns well.",
        ],
        when_use=[
            "You are designing a new relational schema for a service or feature.",
            "An existing schema shows update anomalies (the same fact stored inconsistently in multiple places).",
            "You are deciding whether to denormalize a hot read path.",
        ],
        when_not=[
            "The data is inherently document-shaped, hierarchical, or schema-flexible — see skills/50-database/nosql-and-polyglot-persistence/SKILL.md instead.",
            "You're optimizing an existing, correctly modeled schema purely for query speed — see skills/50-database/indexing-and-query-optimization/SKILL.md instead.",
        ],
        prereqs=[
            "skills/20-architecture/domain-driven-design/SKILL.md for the aggregate/entity boundaries the schema should reflect.",
            "Understanding of normal forms (1NF-3NF) as a baseline vocabulary.",
        ],
        workflow=[
            ("Identify entities and their natural keys", "Model each real-world concept (Customer, Order, Product) as a table with a clear identity."),
            ("Normalize to at least third normal form initially", "Every non-key column depends on the whole key and nothing but the key, removing update anomalies."),
            ("Choose surrogate keys for stability", "Use a generated ID (GUID or sequence) as the primary key rather than a mutable natural key like an email address."),
            ("Model relationships with explicit foreign keys", "Enforce referential integrity at the database level with FK constraints, not just application-level checks."),
            ("Choose appropriate data types and constraints", "Use the narrowest correct type (e.g. DATE not VARCHAR for dates) and NOT NULL/CHECK constraints to enforce invariants."),
            ("Add unique constraints for business keys", "A business-meaningful uniqueness rule (e.g. one active subscription per customer) is enforced by a unique constraint, not just app logic."),
            ("Denormalize only for a measured, justified read pattern", "Add a redundant column or summary table only after profiling shows normalized joins are a genuine bottleneck."),
            ("Document the schema's intent", "Comments/ER diagrams capture why a design choice was made, especially for any deliberate denormalization."),
        ],
        decision=[
            ("A value is naturally repeated across many rows (e.g. category name)", "Extract it to its own table with a foreign key reference, avoiding update anomalies."),
            ("A hot read path requires joining 5+ tables on every request", "Consider a denormalized summary table or materialized view, refreshed on a known cadence, after profiling confirms the need."),
            ("An entity's natural key can change over time (email, username)", "Use a surrogate key as the primary key; keep the natural key as a unique, updatable column."),
            ("A business rule requires uniqueness across a combination of columns", "Add a composite unique constraint at the database level, not just a check in application code."),
            ("Data is optional and highly variable in shape per row", "Consider whether a relational model is truly the best fit, or whether a JSONB column/NoSQL store fits better (skills/50-database/nosql-and-polyglot-persistence/SKILL.md)."),
        ],
        code_lang="sql",
        code_intro="A normalized schema with surrogate keys, foreign keys, and business-key uniqueness:",
        code=(
            "CREATE TABLE customers (\n"
            "    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n"
            "    email VARCHAR(320) NOT NULL,\n"
            "    display_name VARCHAR(200) NOT NULL,\n"
            "    CONSTRAINT uq_customers_email UNIQUE (email)\n"
            ");\n"
            "\n"
            "CREATE TABLE orders (\n"
            "    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n"
            "    customer_id UUID NOT NULL REFERENCES customers(id),\n"
            "    status VARCHAR(20) NOT NULL CHECK (status IN ('Draft','Submitted','Shipped','Cancelled')),\n"
            "    submitted_at TIMESTAMPTZ,\n"
            "    CONSTRAINT chk_orders_submitted_requires_status\n"
            "        CHECK (submitted_at IS NULL OR status <> 'Draft')\n"
            ");\n"
            "\n"
            "CREATE TABLE order_lines (\n"
            "    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n"
            "    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,\n"
            "    product_id UUID NOT NULL REFERENCES products(id),\n"
            "    quantity INT NOT NULL CHECK (quantity > 0),\n"
            "    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0)\n"
            ");\n"
        ),
        code_notes=[
            "Foreign keys enforce that an order_line can never reference a non-existent order or product, even if application code has a bug.",
            "CHECK constraints encode simple invariants (positive quantity, valid status) directly in the schema as a last line of defense.",
        ],
        code2_heading="A deliberate, justified denormalized summary table (SQL)",
        code2=("sql",
            "Added only after profiling showed the joined query was a bottleneck on the dashboard:",
            "CREATE TABLE customer_spend_summary (\n"
            "    customer_id UUID PRIMARY KEY REFERENCES customers(id),\n"
            "    total_spend NUMERIC(14,2) NOT NULL DEFAULT 0,\n"
            "    last_order_at TIMESTAMPTZ,\n"
            "    refreshed_at TIMESTAMPTZ NOT NULL DEFAULT now()\n"
            ");\n"
            "-- Refreshed by a scheduled job or trigger, documented as an intentional read-optimization,\n"
            "-- with the normalized orders/order_lines tables remaining the source of truth.\n"
        ),
        checklist=[
            "Every table has a clear primary key, generally a surrogate key rather than a mutable natural key.",
            "Relationships are enforced with explicit foreign key constraints at the database level.",
            "The schema is normalized to at least 3NF before any denormalization is considered.",
            "Business-meaningful uniqueness rules are enforced with database unique constraints, not just app logic.",
            "Data types and CHECK constraints enforce simple invariants directly in the schema.",
            "Any denormalized table/column is justified by a measured read pattern and documented as such.",
        ],
        antipatterns=[
            ("Natural keys as primary keys", "Using an email address or username as the primary key, causing cascading updates across every referencing table when it changes."),
            ("No foreign key constraints", "Relying solely on application code to maintain referential integrity, allowing orphaned rows when a bug slips through."),
            ("Premature denormalization", "Duplicating data across tables 'for performance' before any query has been shown to be slow."),
            ("One giant table for everything", "Cramming unrelated concerns into a single wide table instead of normalizing into properly related entities."),
            ("Stringly-typed everything", "Using VARCHAR for dates, numbers, and enums instead of proper types and CHECK constraints, losing validation at the database level."),
        ],
        verification=[
            "A schema review confirms every table has a stable surrogate primary key and appropriate foreign keys.",
            "Attempting to insert a row referencing a non-existent parent fails due to a foreign key constraint, verified by a test.",
            "No update anomaly exists where the same fact must be changed in more than one place to stay consistent.",
            "Any denormalized structure has a documented justification tied to a measured query pattern.",
        ],
        references=[
            "skills/20-architecture/domain-driven-design/SKILL.md",
            "skills/50-database/indexing-and-query-optimization/SKILL.md",
            "C.J. Date — An Introduction to Database Systems (normalization theory).",
        ],
    ),
    dict(
        dir="50-database", slug="indexing-and-query-optimization", category="database",
        tags=["indexing", "query-optimization", "performance"],
        desc="Use when a database query is slow and you need to diagnose the cause using execution plans and apply the correct indexing or query rewrite.",
        purpose=[
            "Slow queries are one of the most common production performance issues, and guessing at fixes "
            "without reading an execution plan often makes things worse. This skill covers reading query "
            "execution plans, choosing the right index type and column order, and recognizing common query "
            "patterns (implicit conversions, leading wildcards, unindexed foreign keys) that defeat indexing.",
            "It treats indexing as a targeted response to a measured problem, not something to apply "
            "speculatively to every column, since excessive indexing slows down writes and bloats storage.",
        ],
        when_use=[
            "A specific query or endpoint has been identified as slow via monitoring or user reports.",
            "You are reviewing a new query pattern before it goes to production at scale.",
            "Database CPU/IO is high and you need to identify which queries are responsible.",
        ],
        when_not=[
            "No query has been measured as slow — don't add speculative indexes without evidence.",
            "The bottleneck is actually network or application-layer serialization, not the database — profile the whole request path first.",
        ],
        prereqs=[
            "skills/50-database/relational-data-modeling/SKILL.md for the schema the query runs against.",
            "Access to EXPLAIN ANALYZE (or the database's equivalent) and a representative dataset size for testing.",
        ],
        workflow=[
            ("Reproduce the slow query with EXPLAIN ANALYZE", "Get the actual execution plan against production-representative data volume, not a tiny dev database."),
            ("Identify sequential scans on large tables", "A Seq Scan on a large table in a selective WHERE clause usually indicates a missing or unused index."),
            ("Check index column order for composite indexes", "Lead with the column(s) used in equality filters, then range filters, matching the query's actual predicates."),
            ("Verify the index is actually being used", "A plan may show Seq Scan even with an index present if statistics are stale or the predicate defeats index usage (e.g. wrapping a column in a function)."),
            ("Avoid patterns that defeat indexes", "Leading wildcard LIKE '%x', implicit type conversions, and functions applied to indexed columns typically prevent index usage."),
            ("Consider covering indexes for read-heavy hot paths", "Include all columns a query needs so the database can answer from the index alone without a table lookup."),
            ("Re-run EXPLAIN ANALYZE after each change", "Confirm the plan actually improved and measure real latency, not just assume the fix worked."),
            ("Update table statistics regularly", "Ensure the query planner has fresh statistics (ANALYZE) so it makes good decisions about index usage."),
        ],
        decision=[
            ("A WHERE clause filters on one column with high selectivity", "Add a single-column B-tree index on that column."),
            ("A WHERE clause filters on two columns together frequently", "Add a composite index with the equality-filtered column first."),
            ("A query needs full-text search", "Use a dedicated full-text/GIN index rather than LIKE '%term%' on an unindexed column."),
            ("A read-heavy query only needs a few columns", "Consider a covering index including those columns to avoid a table heap lookup."),
            ("An index exists but isn't being used", "Check for stale statistics, a function wrapping the column, or a type mismatch before adding a redundant index."),
        ],
        code_lang="sql",
        code_intro="Diagnosing a slow query and adding a targeted composite index:",
        code=(
            "EXPLAIN ANALYZE\n"
            "SELECT id, status, submitted_at\n"
            "FROM orders\n"
            "WHERE customer_id = '11111111-1111-1111-1111-111111111111'\n"
            "  AND status = 'Submitted'\n"
            "ORDER BY submitted_at DESC\n"
            "LIMIT 20;\n"
            "-- Plan shows: Seq Scan on orders (cost=... rows=500000) -- confirms missing index\n"
            "\n"
            "CREATE INDEX idx_orders_customer_status_submitted\n"
            "    ON orders (customer_id, status, submitted_at DESC);\n"
            "\n"
            "-- Re-run EXPLAIN ANALYZE: plan should now show\n"
            "-- Index Scan using idx_orders_customer_status_submitted (cost=... rows=12)\n"
        ),
        code_notes=[
            "Column order matches the query: equality filters (customer_id, status) first, then the sort column (submitted_at) last.",
            "Including submitted_at DESC in the index lets the database satisfy ORDER BY without a separate sort step.",
        ],
        code2_heading="A pattern that silently defeats an existing index (SQL)",
        code2=("sql",
            "Wrapping an indexed column in a function prevents the planner from using a plain index on it:",
            "-- Defeats an index on submitted_at:\n"
            "SELECT * FROM orders WHERE DATE(submitted_at) = '2026-01-01';\n"
            "\n"
            "-- Index-friendly rewrite using a range instead of a function on the column:\n"
            "SELECT * FROM orders\n"
            "WHERE submitted_at >= '2026-01-01' AND submitted_at < '2026-01-02';\n"
        ),
        checklist=[
            "Every index added is backed by an EXPLAIN ANALYZE showing a measured problem, not a speculative guess.",
            "Composite index column order matches actual query predicates (equality first, then range/sort).",
            "Query patterns avoid wrapping indexed columns in functions or leading wildcards that defeat index usage.",
            "Table statistics are kept current so the query planner makes informed decisions.",
            "Each optimization is re-verified with EXPLAIN ANALYZE and real latency measurement after the change.",
            "Write-path impact (extra indexes slow inserts/updates) is considered before adding an index.",
        ],
        antipatterns=[
            ("Indexing every column speculatively", "Adding an index to every column 'just in case', bloating storage and slowing down every write."),
            ("Guessing without EXPLAIN ANALYZE", "Adding an index based on intuition alone without confirming the actual execution plan showed a problem."),
            ("Function-wrapped predicates on indexed columns", "Writing WHERE LOWER(email) = ... against a plain index on email, silently forcing a sequential scan."),
            ("Leading wildcard searches", "Using LIKE '%term' on a large table, which cannot use a standard B-tree index efficiently."),
            ("Stale statistics ignored", "Never running ANALYZE after bulk data loads, leaving the query planner with outdated row-count estimates."),
        ],
        verification=[
            "EXPLAIN ANALYZE for the target query shows an Index Scan (or equivalent) instead of a Seq Scan on the large table.",
            "Measured query latency improves meaningfully after the index/rewrite, confirmed under representative data volume.",
            "Write-path latency (INSERT/UPDATE) on the affected table has not regressed unacceptably after adding the index.",
            "No new index duplicates the leading columns of an existing index unnecessarily.",
        ],
        references=[
            "skills/50-database/relational-data-modeling/SKILL.md",
            "Use The Index, Luke! (use-the-index-luke.com).",
            "PostgreSQL / SQL Server documentation on EXPLAIN and index types.",
        ],
    ),
]
