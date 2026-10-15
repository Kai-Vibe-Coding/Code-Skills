---
name: relational-data-modeling
description: Use when designing a new relational schema or evaluating an existing one for normalization, key design, and referential integrity correctness.
category: database
tags: [data-modeling, normalization, schema-design]
maturity: stable
updated: 2026-08-21
---

## Purpose

A poorly modeled relational schema causes data anomalies, slow queries, and painful migrations later. This skill covers normalizing data to remove redundancy and update anomalies, choosing appropriate primary/foreign key strategies, and deliberately denormalizing only where a measured read pattern justifies it.

It treats normalization as a starting discipline, not a religion — the goal is a schema that protects data integrity while still serving the application's actual query patterns well.

## When to use / When NOT to use

**Use this skill when:**

- You are designing a new relational schema for a service or feature.
- An existing schema shows update anomalies (the same fact stored inconsistently in multiple places).
- You are deciding whether to denormalize a hot read path.

**Do NOT use this skill when:**

- The data is inherently document-shaped, hierarchical, or schema-flexible — see skills/50-database/nosql-and-polyglot-persistence/SKILL.md instead.
- You're optimizing an existing, correctly modeled schema purely for query speed — see skills/50-database/indexing-and-query-optimization/SKILL.md instead.

## Prerequisites

- skills/20-architecture/domain-driven-design/SKILL.md for the aggregate/entity boundaries the schema should reflect.
- Understanding of normal forms (1NF-3NF) as a baseline vocabulary.

## Workflow

1. **Identify entities and their natural keys** - Model each real-world concept (Customer, Order, Product) as a table with a clear identity.
2. **Normalize to at least third normal form initially** - Every non-key column depends on the whole key and nothing but the key, removing update anomalies.
3. **Choose surrogate keys for stability** - Use a generated ID (GUID or sequence) as the primary key rather than a mutable natural key like an email address.
4. **Model relationships with explicit foreign keys** - Enforce referential integrity at the database level with FK constraints, not just application-level checks.
5. **Choose appropriate data types and constraints** - Use the narrowest correct type (e.g. DATE not VARCHAR for dates) and NOT NULL/CHECK constraints to enforce invariants.
6. **Add unique constraints for business keys** - A business-meaningful uniqueness rule (e.g. one active subscription per customer) is enforced by a unique constraint, not just app logic.
7. **Denormalize only for a measured, justified read pattern** - Add a redundant column or summary table only after profiling shows normalized joins are a genuine bottleneck.
8. **Document the schema's intent** - Comments/ER diagrams capture why a design choice was made, especially for any deliberate denormalization.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A value is naturally repeated across many rows (e.g. category name) | Extract it to its own table with a foreign key reference, avoiding update anomalies. |
| A hot read path requires joining 5+ tables on every request | Consider a denormalized summary table or materialized view, refreshed on a known cadence, after profiling confirms the need. |
| An entity's natural key can change over time (email, username) | Use a surrogate key as the primary key; keep the natural key as a unique, updatable column. |
| A business rule requires uniqueness across a combination of columns | Add a composite unique constraint at the database level, not just a check in application code. |
| Data is optional and highly variable in shape per row | Consider whether a relational model is truly the best fit, or whether a JSONB column/NoSQL store fits better (skills/50-database/nosql-and-polyglot-persistence/SKILL.md). |

## Reference implementation

A normalized schema with surrogate keys, foreign keys, and business-key uniqueness:

```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(320) NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    CONSTRAINT uq_customers_email UNIQUE (email)
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    status VARCHAR(20) NOT NULL CHECK (status IN ('Draft','Submitted','Shipped','Cancelled')),
    submitted_at TIMESTAMPTZ,
    CONSTRAINT chk_orders_submitted_requires_status
        CHECK (submitted_at IS NULL OR status <> 'Draft')
);

CREATE TABLE order_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0)
);
```

- Foreign keys enforce that an order_line can never reference a non-existent order or product, even if application code has a bug.
- CHECK constraints encode simple invariants (positive quantity, valid status) directly in the schema as a last line of defense.

### A deliberate, justified denormalized summary table (SQL)

Added only after profiling showed the joined query was a bottleneck on the dashboard:

```sql
CREATE TABLE customer_spend_summary (
    customer_id UUID PRIMARY KEY REFERENCES customers(id),
    total_spend NUMERIC(14,2) NOT NULL DEFAULT 0,
    last_order_at TIMESTAMPTZ,
    refreshed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Refreshed by a scheduled job or trigger, documented as an intentional read-optimization,
-- with the normalized orders/order_lines tables remaining the source of truth.
```

## Checklist

- [ ] Every table has a clear primary key, generally a surrogate key rather than a mutable natural key.
- [ ] Relationships are enforced with explicit foreign key constraints at the database level.
- [ ] The schema is normalized to at least 3NF before any denormalization is considered.
- [ ] Business-meaningful uniqueness rules are enforced with database unique constraints, not just app logic.
- [ ] Data types and CHECK constraints enforce simple invariants directly in the schema.
- [ ] Any denormalized table/column is justified by a measured read pattern and documented as such.

## Anti-patterns

- **Natural keys as primary keys** - Using an email address or username as the primary key, causing cascading updates across every referencing table when it changes.
- **No foreign key constraints** - Relying solely on application code to maintain referential integrity, allowing orphaned rows when a bug slips through.
- **Premature denormalization** - Duplicating data across tables 'for performance' before any query has been shown to be slow.
- **One giant table for everything** - Cramming unrelated concerns into a single wide table instead of normalizing into properly related entities.
- **Stringly-typed everything** - Using VARCHAR for dates, numbers, and enums instead of proper types and CHECK constraints, losing validation at the database level.

## Verification

- A schema review confirms every table has a stable surrogate primary key and appropriate foreign keys.
- Attempting to insert a row referencing a non-existent parent fails due to a foreign key constraint, verified by a test.
- No update anomaly exists where the same fact must be changed in more than one place to stay consistent.
- Any denormalized structure has a documented justification tied to a measured query pattern.

## References

- skills/20-architecture/domain-driven-design/SKILL.md
- skills/50-database/indexing-and-query-optimization/SKILL.md
- C.J. Date — An Introduction to Database Systems (normalization theory).
