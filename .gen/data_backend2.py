SKILLS = [
    dict(
        dir="30-backend", slug="repository-unit-of-work-specification", category="backend",
        tags=["repository", "unit-of-work", "specification-pattern"],
        desc="Use when your application layer needs to query and persist aggregates without depending on EF Core or a specific ORM directly.",
        purpose=[
            "Coupling the Application layer directly to an ORM's DbContext leaks infrastructure concerns "
            "into business logic and makes unit testing without a real database difficult. The Repository "
            "and Unit of Work patterns, combined with a Specification pattern for composable queries, give "
            "the Application layer a persistence-ignorant contract for loading and saving aggregates.",
            "This skill defines when repositories add real value versus when they become a needless "
            "abstraction over an ORM that already implements those patterns internally.",
        ],
        when_use=[
            "The Application layer needs to remain testable without a real database.",
            "You may need to swap or add a persistence technology later (e.g. adding a cache-backed repository).",
            "Aggregate loading involves consistent, reusable query logic (specifications) across multiple use cases.",
        ],
        when_not=[
            "The application is small, uses EF Core exclusively, and DbContext-as-repository is well understood by the team.",
            "You need highly tuned, one-off read queries — use skills/30-backend/dapper-and-raw-sql/SKILL.md for those instead of forcing them through a repository abstraction.",
        ],
        prereqs=[
            "skills/20-architecture/domain-driven-design/SKILL.md for aggregate boundaries the repository operates on.",
            "skills/30-backend/ef-core-data-access/SKILL.md if EF Core is the underlying implementation.",
            "Understanding of the Unit of Work pattern for transaction boundaries.",
        ],
        workflow=[
            ("Define one repository interface per aggregate root", "IOrderRepository, not a generic IRepository<T> for every entity — repositories operate at the aggregate boundary."),
            ("Keep repository methods aggregate-oriented", "AddAsync, GetByIdAsync, and methods returning whole aggregates, not arbitrary partial projections."),
            ("Introduce specifications for reusable query logic", "Encapsulate criteria like 'orders pending fulfillment older than 3 days' as a named Specification<Order> class."),
            ("Define IUnitOfWork for transaction boundaries", "A single SaveChangesAsync call commits everything a use case changed, keeping the transaction boundary explicit."),
            ("Implement repositories in Infrastructure", "Concrete EF Core (or Dapper) implementations live in Infrastructure and are injected via DI."),
            ("Use in-memory fakes for Application-layer unit tests", "Test handlers against a simple in-memory implementation of the repository interface, not a real database."),
            ("Reserve read-only projections for query handlers", "Queries that only need a DTO shape can bypass repositories and use a dedicated read model or Dapper query."),
        ],
        decision=[
            ("Aggregate load-and-save is straightforward", "Use a plain repository interface with GetByIdAsync/AddAsync/Update methods."),
            ("Query criteria is reused across several use cases", "Extract it into a named Specification class rather than duplicating LINQ expressions."),
            ("A read query just needs a flat DTO for a UI list", "Skip the repository and aggregate entirely; use a dedicated query handler with Dapper or EF Core projection."),
            ("Team already trusts DbContext as the Unit of Work", "It's acceptable to inject DbContext directly as IUnitOfWork rather than build a redundant wrapper."),
            ("Generic IRepository<T> for every entity is tempting", "Resist it — it leaks CRUD-on-anything semantics that erode aggregate boundaries; scope repositories to aggregate roots only."),
        ],
        code_lang="csharp",
        code_intro="An aggregate-scoped repository interface with a specification-based query method:",
        code=(
            "public interface IOrderRepository\n"
            "{\n"
            "    Task<Order?> GetByIdAsync(Guid id, CancellationToken ct = default);\n"
            "    Task<IReadOnlyList<Order>> FindAsync(ISpecification<Order> spec, CancellationToken ct = default);\n"
            "    Task AddAsync(Order order, CancellationToken ct = default);\n"
            "    void Remove(Order order);\n"
            "}\n"
            "\n"
            "public interface ISpecification<T>\n"
            "{\n"
            "    Expression<Func<T, bool>> Criteria { get; }\n"
            "    List<Expression<Func<T, object>>> Includes { get; }\n"
            "}\n"
            "\n"
            "public class PendingFulfillmentSpec : ISpecification<Order>\n"
            "{\n"
            "    public Expression<Func<Order, bool>> Criteria { get; }\n"
            "    public List<Expression<Func<Order, object>>> Includes { get; } = new() { o => o.Lines };\n"
            "\n"
            "    public PendingFulfillmentSpec(TimeSpan olderThan)\n"
            "    {\n"
            "        var cutoff = DateTime.UtcNow - olderThan;\n"
            "        Criteria = o => o.Status == OrderStatus.Submitted && o.SubmittedAt < cutoff;\n"
            "    }\n"
            "}\n"
        ),
        code_notes=[
            "Includes lets a specification declare its own eager-loading needs without leaking EF Core details to callers.",
            "The interface itself has zero EF Core or Dapper references, keeping the Application layer persistence-ignorant.",
        ],
        code2_heading="Unit of Work committing changes across repositories (C#)",
        code2=("csharp",
            "A single commit point per use case, regardless of how many repositories were touched:",
            "public interface IUnitOfWork\n"
            "{\n"
            "    Task<int> SaveChangesAsync(CancellationToken ct = default);\n"
            "}\n"
            "\n"
            "public class EfUnitOfWork : IUnitOfWork\n"
            "{\n"
            "    private readonly AppDbContext _db;\n"
            "    public EfUnitOfWork(AppDbContext db) => _db = db;\n"
            "\n"
            "    public Task<int> SaveChangesAsync(CancellationToken ct = default) =>\n"
            "        _db.SaveChangesAsync(ct);\n"
            "}\n"
            "\n"
            "// In a handler:\n"
            "await _orders.AddAsync(order, ct);\n"
            "await _unitOfWork.SaveChangesAsync(ct); // one commit for the whole use case\n"
        ),
        checklist=[
            "Repository interfaces are scoped to aggregate roots, not one per table.",
            "No generic IRepository<T> is used for arbitrary entities across bounded contexts.",
            "Reusable query criteria are captured in named Specification classes.",
            "A single Unit of Work commit point exists per use case/transaction.",
            "Application-layer handler tests run against an in-memory fake repository, without a real database.",
            "Flat read queries bypass the repository/aggregate pattern entirely.",
        ],
        antipatterns=[
            ("Generic CRUD repository", "IRepository<T> with Get/Add/Update/Delete for every entity, encouraging cross-aggregate mutation that violates consistency boundaries."),
            ("Repository leaking IQueryable", "Exposing IQueryable<Order> from the repository interface, letting callers build arbitrary EF-specific queries and defeating the abstraction's purpose."),
            ("One SaveChanges per repository call", "Calling SaveChangesAsync inside every repository method instead of once per use case, fragmenting the transaction boundary."),
            ("Repositories for pure read DTOs", "Forcing list/report queries through aggregate-oriented repositories instead of a lightweight query handler."),
            ("Duplicated query criteria", "Copy-pasting the same LINQ filter across multiple handlers instead of extracting a Specification."),
        ],
        verification=[
            "Every repository interface maps 1:1 to an aggregate root, verified during code review.",
            "Application-layer unit tests pass using in-memory fake repositories with no database connection.",
            "A single SaveChangesAsync/commit call exists per use case in each command handler.",
            "No repository interface exposes IQueryable or leaks ORM-specific types to the Application layer.",
        ],
        references=[
            "skills/20-architecture/domain-driven-design/SKILL.md",
            "skills/30-backend/ef-core-data-access/SKILL.md",
            "Martin Fowler — Repository and Unit of Work patterns (Patterns of Enterprise Application Architecture).",
        ],
    ),
    dict(
        dir="30-backend", slug="ef-core-data-access", category="backend",
        tags=["ef-core", "orm", "data-access"],
        desc="Use when implementing the persistence layer for a .NET service with Entity Framework Core and you need entity configuration, migrations, and query performance handled correctly.",
        purpose=[
            "EF Core is powerful but easy to misuse in ways that cause N+1 queries, leaky domain models, or "
            "fragile migrations. This skill covers configuring EF Core so it maps a rich domain model "
            "faithfully, keeps entity configuration out of domain classes, and produces efficient, "
            "predictable SQL.",
            "It also covers the migration workflow needed to evolve the schema safely alongside the domain "
            "model as the application grows.",
        ],
        when_use=[
            "You are implementing the Infrastructure-layer persistence for aggregates defined in the Domain layer.",
            "You need to configure relationships, value objects, or owned types without polluting domain entities with ORM attributes.",
            "Query performance issues (N+1, over-fetching) need to be diagnosed and fixed.",
        ],
        when_not=[
            "The query is a complex reporting query better served by raw SQL — see skills/30-backend/dapper-and-raw-sql/SKILL.md.",
            "The project deliberately uses a different ORM or micro-ORM; don't force EF Core conventions onto it.",
        ],
        prereqs=[
            "skills/20-architecture/domain-driven-design/SKILL.md for the entity/value-object/aggregate shapes being mapped.",
            "skills/50-database/relational-data-modeling/SKILL.md for the underlying schema design.",
            "EF Core 8 package referenced in the Infrastructure project only, never Domain.",
        ],
        workflow=[
            ("Configure entities with Fluent API, not attributes", "Use IEntityTypeConfiguration<T> classes in Infrastructure so Domain classes stay free of EF attributes."),
            ("Map value objects as owned types or conversions", "Use OwnsOne for owned value objects, or ValueConverters for simple wrapper types like Money or Email."),
            ("Keep navigation properties private where possible", "Expose read-only collections from aggregates; use backing fields so EF Core can still populate them."),
            ("Use explicit Include for known access patterns", "Load related data with .Include() intentionally in repository methods, not implicitly via lazy loading."),
            ("Disable lazy loading proxies", "Avoid runtime surprises and hidden N+1 queries by not enabling lazy loading by default."),
            ("Generate migrations per meaningful schema change", "dotnet ef migrations add <Name> after each domain/schema change, reviewed like any other code change."),
            ("Review generated SQL for hot paths", "Use logging or EF Core's query tags to inspect generated SQL for frequently executed queries."),
            ("Apply migrations via a controlled pipeline step", "Run dotnet ef database update (or migration bundle) as an explicit deployment step, not automatically on app startup in production."),
        ],
        decision=[
            ("Entity has a value object like Money or Address", "Map it with OwnsOne (owned entity) or a ValueConverter for simple immutable wrappers."),
            ("A screen just needs a few columns from several tables", "Use .Select() projection to a DTO instead of loading full entity graphs."),
            ("Query needs to filter to a tenant or soft-deleted rows globally", "Use EF Core global query filters instead of repeating the filter in every query."),
            ("Migration touches a large, heavily used table", "Review it against skills/50-database/migrations-and-zero-downtime-schema-change/SKILL.md before applying in production."),
            ("Reporting query has multiple complex joins/aggregations", "Prefer skills/30-backend/dapper-and-raw-sql/SKILL.md over forcing it through LINQ-to-Entities."),
        ],
        code_lang="csharp",
        code_intro="Fluent API configuration keeping the domain entity free of ORM concerns:",
        code=(
            "public class OrderConfiguration : IEntityTypeConfiguration<Order>\n"
            "{\n"
            "    public void Configure(EntityTypeBuilder<Order> builder)\n"
            "    {\n"
            "        builder.ToTable(\"Orders\");\n"
            "        builder.HasKey(o => o.Id);\n"
            "        builder.Property(o => o.Status).HasConversion<string>().HasMaxLength(20);\n"
            "\n"
            "        builder.OwnsOne(o => o.ShippingAddress, a =>\n"
            "        {\n"
            "            a.Property(p => p.Street).HasColumnName(\"ShippingStreet\");\n"
            "            a.Property(p => p.City).HasColumnName(\"ShippingCity\");\n"
            "        });\n"
            "\n"
            "        builder.HasMany(o => o.Lines)\n"
            "            .WithOne()\n"
            "            .HasForeignKey(\"OrderId\")\n"
            "            .OnDelete(DeleteBehavior.Cascade);\n"
            "\n"
            "        builder.Metadata.FindNavigation(nameof(Order.Lines))!\n"
            "            .SetPropertyAccessMode(PropertyAccessMode.Field);\n"
            "\n"
            "        builder.HasQueryFilter(o => !o.IsDeleted);\n"
            "    }\n"
            "}\n"
        ),
        code_notes=[
            "PropertyAccessMode.Field lets EF Core populate a private backing field for Lines while the domain exposes only IReadOnlyList<OrderLine>.",
            "HasQueryFilter applies a global soft-delete filter automatically to every query against Order.",
        ],
        code2_heading="Projecting to a DTO to avoid over-fetching (C#)",
        code2=("csharp",
            "Avoid loading full aggregates for read-only list views:",
            "var summaries = await db.Orders\n"
            "    .Where(o => o.CustomerId == customerId)\n"
            "    .Select(o => new OrderSummaryDto\n"
            "    {\n"
            "        Id = o.Id,\n"
            "        Status = o.Status.ToString(),\n"
            "        Total = o.Lines.Sum(l => l.UnitPrice * l.Quantity)\n"
            "    })\n"
            "    .AsNoTracking()\n"
            "    .ToListAsync(ct);\n"
        ),
        checklist=[
            "Domain entities contain no EF Core attributes or references; all mapping is Fluent API in Infrastructure.",
            "Value objects are mapped as owned types or value converters, not flattened primitives on the entity.",
            "Lazy loading proxies are disabled; related data is loaded via explicit Include or projection.",
            "Read-only queries use AsNoTracking() and project to DTOs where full aggregates aren't needed.",
            "Migrations are generated per schema change and reviewed before merging.",
            "Migration application is an explicit pipeline step, not automatic on every app startup in production.",
        ],
        antipatterns=[
            ("Data annotations on domain entities", "Sprinkling [Required], [Column] attributes on Domain classes, coupling the domain model to EF Core."),
            ("Lazy loading left enabled", "Allowing implicit lazy loading, causing invisible N+1 queries that only surface under load."),
            ("Loading full graphs for list views", "Fetching entire aggregates with all navigation properties just to render a summary list."),
            ("Auto-migrate on startup in production", "Calling Database.Migrate() in Program.cs for a production service, risking uncontrolled schema changes on every deploy."),
            ("Public setters on collection navigation properties", "Exposing List<T> setters publicly, letting callers replace an aggregate's child collection and break invariants."),
        ],
        verification=[
            "SQL logging or a profiler shows no unexpected N+1 query patterns for common list/detail screens.",
            "`dotnet ef migrations add` produces a clean, reviewable diff matching the intended domain change.",
            "Domain project has zero EF Core package references (verified via project reference check).",
            "Read-heavy endpoints use AsNoTracking projections, confirmed by code review or query plan inspection.",
        ],
        references=[
            "skills/20-architecture/domain-driven-design/SKILL.md",
            "skills/50-database/relational-data-modeling/SKILL.md",
            "skills/50-database/migrations-and-zero-downtime-schema-change/SKILL.md",
            "Microsoft Learn — EF Core documentation.",
        ],
    ),
]
