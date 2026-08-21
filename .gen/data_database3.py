SKILLS = [
    dict(
        dir="50-database", slug="nosql-and-polyglot-persistence", category="database",
        tags=["nosql", "polyglot-persistence", "document-db"],
        desc="Use when deciding whether a relational database is the right fit for a given data access pattern or whether a document, key-value, or wide-column store would serve it better.",
        purpose=[
            "Defaulting to a single relational database for every workload ignores cases where a document "
            "store, key-value cache, or wide-column database is a much better fit for the actual access "
            "pattern. This skill provides a decision framework for polyglot persistence: matching each "
            "workload's read/write pattern and consistency needs to the storage technology best suited for it.",
            "It also covers the operational cost of running multiple storage technologies, since polyglot "
            "persistence trades data-model fit for increased operational complexity and must be justified.",
        ],
        when_use=[
            "A workload's data shape or access pattern doesn't map well to a relational schema (e.g. deeply nested, schema-variable documents).",
            "You need extremely low-latency key-value lookups at a scale a relational database struggles with.",
            "You are evaluating whether to introduce a second storage technology alongside an existing relational database.",
        ],
        when_not=[
            "The data is naturally tabular with clear relationships and needs strong transactional guarantees — a relational database remains the better default.",
            "The team has no operational experience running the proposed NoSQL technology and there's no strong justification for the added complexity.",
        ],
        prereqs=[
            "skills/50-database/relational-data-modeling/SKILL.md to have ruled out (or confirmed) a relational fit first.",
            "skills/20-architecture/caching-strategy/SKILL.md if the motivation is caching rather than primary storage.",
        ],
        workflow=[
            ("Characterize the workload's access pattern", "Is it read-heavy key-value lookups, complex relational joins, full-text search, or time-series writes?"),
            ("Match the pattern to a storage category", "Document stores for schema-variable nested data; key-value for simple fast lookups; wide-column for massive write-heavy time-series; relational for transactional, joined data."),
            ("Evaluate consistency requirements honestly", "Many NoSQL stores offer eventual consistency by default; confirm the use case can tolerate that before adopting one for correctness-critical data."),
            ("Keep the system of record singular per entity", "Even in a polyglot architecture, one store should be the authoritative source of truth for a given entity, with others as derived/cache copies."),
            ("Synchronize derived stores via events, not dual writes from every caller", "Use skills/20-architecture/event-driven-architecture/SKILL.md patterns to keep a search index or cache in sync with the system of record."),
            ("Assess operational cost before adopting a new store", "Factor in on-call familiarity, backup/restore tooling, and monitoring maturity for the new technology, not just its data-model fit."),
            ("Start with the simplest viable option", "Prefer using the relational database's JSONB/document column support for lightly schema-flexible data before introducing an entirely separate NoSQL store."),
        ],
        decision=[
            ("Need extremely fast key-based lookups (session data, feature flags)", "Use a key-value store (e.g. Redis) rather than a relational table for this specific access pattern."),
            ("Data is deeply nested and schema varies significantly per record", "Use a document store (e.g. MongoDB), or a JSONB column in the existing relational database if the rest of the data is relational."),
            ("Workload is massive-scale time-series writes (metrics, IoT)", "Use a wide-column or time-series-optimized store rather than a general relational database."),
            ("Search needs to be full-text and faceted across large text fields", "Use a dedicated search engine (e.g. Elasticsearch) as a derived index, kept in sync via events, not as the system of record."),
            ("Data is transactional with strong relational integrity needs", "Stay with the relational database; don't introduce NoSQL purely for perceived 'scale' without a measured need."),
        ],
        code_lang="text",
        code_intro="A polyglot architecture with a single system of record and derived, event-synced stores:",
        code=(
            "                     ┌────────────────────┐\n"
            "                     │  PostgreSQL (SoR)  │  <- authoritative Order/Customer data\n"
            "                     └─────────┬──────────┘\n"
            "                               │ OrderPlaced / OrderUpdated events\n"
            "                 ┌─────────────┼─────────────────┐\n"
            "                 ▼                                 ▼\n"
            "        ┌────────────────┐               ┌──────────────────────┐\n"
            "        │ Elasticsearch   │               │ Redis (cache)         │\n"
            "        │ (search index)  │               │ per-customer summary  │\n"
            "        └────────────────┘               └──────────────────────┘\n"
            "\n"
            "Rule: PostgreSQL is always the source of truth. Elasticsearch and Redis are rebuildable\n"
            "projections that can be dropped and repopulated from events without data loss.\n"
        ),
        code_notes=[
            "If Elasticsearch or Redis is lost entirely, it can be fully rebuilt by replaying events from the system of record — this is the key test for whether a derived store is safe to add.",
            "No caller writes directly to Elasticsearch/Redis; they're only updated via the event stream, avoiding split-brain inconsistency.",
        ],
        code2_heading="Using JSONB in a relational database before reaching for a separate document store (SQL)",
        code2=("sql",
            "A pragmatic middle ground for lightly schema-variable data within an otherwise relational schema:",
            "CREATE TABLE product_attributes (\n"
            "    product_id UUID PRIMARY KEY REFERENCES products(id),\n"
            "    attributes JSONB NOT NULL DEFAULT '{}'\n"
            ");\n"
            "\n"
            "-- Query into the JSONB column without needing a separate NoSQL database:\n"
            "SELECT product_id FROM product_attributes\n"
            "WHERE attributes @> '{\"color\": \"red\"}';\n"
            "\n"
            "CREATE INDEX idx_product_attributes_gin ON product_attributes USING GIN (attributes);\n"
        ),
        checklist=[
            "Each storage technology choice is justified by a specific, characterized workload pattern, not general preference.",
            "One system of record is designated per entity; other stores are explicitly derived/rebuildable projections.",
            "Derived stores are kept in sync via events, not ad hoc dual writes scattered across the codebase.",
            "Consistency requirements (strong vs eventual) were evaluated honestly against the chosen store's guarantees.",
            "Operational readiness (monitoring, backup, on-call familiarity) was assessed before adopting a new storage technology.",
            "Simpler options (e.g. JSONB in the existing relational database) were considered before introducing a wholly separate NoSQL store.",
        ],
        antipatterns=[
            ("NoSQL for its own sake", "Adopting a document or key-value store because it's trendy, without a workload characteristic that actually benefits from it."),
            ("Multiple systems of record for the same entity", "Allowing both the relational database and a document store to be independently writable sources of truth for the same entity, causing data drift."),
            ("Dual writes from every caller", "Writing directly to both the primary store and a derived cache/search index from application code everywhere, rather than syncing via events centrally."),
            ("Ignoring consistency guarantees", "Storing correctness-critical financial data in an eventually-consistent store without accounting for read-your-writes issues."),
            ("Adopting a new store with no operational plan", "Introducing a new database technology with no backup strategy, monitoring, or on-call runbook in place."),
        ],
        verification=[
            "For each non-relational store in use, a specific workload characteristic justifying it is documented.",
            "Deleting and rebuilding a derived store from its event stream restores it to a correct state, verified by a drill.",
            "No application code writes directly to more than one store for the same logical write operation.",
            "On-call runbooks and monitoring exist for every storage technology in production use.",
        ],
        references=[
            "skills/50-database/relational-data-modeling/SKILL.md",
            "skills/20-architecture/event-driven-architecture/SKILL.md",
            "skills/20-architecture/caching-strategy/SKILL.md",
            "Martin Fowler — Polyglot Persistence.",
        ],
    ),
]
