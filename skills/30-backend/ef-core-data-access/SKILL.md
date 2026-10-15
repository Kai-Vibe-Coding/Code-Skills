---
name: ef-core-data-access
description: Use when implementing the persistence layer for a .NET service with Entity Framework Core and you need entity configuration, migrations, and query performance handled correctly.
category: backend
tags: [ef-core, orm, data-access]
maturity: stable
updated: 2026-08-21
---

## Purpose

EF Core is powerful but easy to misuse in ways that cause N+1 queries, leaky domain models, or fragile migrations. This skill covers configuring EF Core so it maps a rich domain model faithfully, keeps entity configuration out of domain classes, and produces efficient, predictable SQL.

It also covers the migration workflow needed to evolve the schema safely alongside the domain model as the application grows.

## When to use / When NOT to use

**Use this skill when:**

- You are implementing the Infrastructure-layer persistence for aggregates defined in the Domain layer.
- You need to configure relationships, value objects, or owned types without polluting domain entities with ORM attributes.
- Query performance issues (N+1, over-fetching) need to be diagnosed and fixed.

**Do NOT use this skill when:**

- The query is a complex reporting query better served by raw SQL — see skills/30-backend/dapper-and-raw-sql/SKILL.md.
- The project deliberately uses a different ORM or micro-ORM; don't force EF Core conventions onto it.

## Prerequisites

- skills/20-architecture/domain-driven-design/SKILL.md for the entity/value-object/aggregate shapes being mapped.
- skills/50-database/relational-data-modeling/SKILL.md for the underlying schema design.
- EF Core 8 package referenced in the Infrastructure project only, never Domain.

## Workflow

1. **Configure entities with Fluent API, not attributes** - Use IEntityTypeConfiguration<T> classes in Infrastructure so Domain classes stay free of EF attributes.
2. **Map value objects as owned types or conversions** - Use OwnsOne for owned value objects, or ValueConverters for simple wrapper types like Money or Email.
3. **Keep navigation properties private where possible** - Expose read-only collections from aggregates; use backing fields so EF Core can still populate them.
4. **Use explicit Include for known access patterns** - Load related data with .Include() intentionally in repository methods, not implicitly via lazy loading.
5. **Disable lazy loading proxies** - Avoid runtime surprises and hidden N+1 queries by not enabling lazy loading by default.
6. **Generate migrations per meaningful schema change** - dotnet ef migrations add <Name> after each domain/schema change, reviewed like any other code change.
7. **Review generated SQL for hot paths** - Use logging or EF Core's query tags to inspect generated SQL for frequently executed queries.
8. **Apply migrations via a controlled pipeline step** - Run dotnet ef database update (or migration bundle) as an explicit deployment step, not automatically on app startup in production.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Entity has a value object like Money or Address | Map it with OwnsOne (owned entity) or a ValueConverter for simple immutable wrappers. |
| A screen just needs a few columns from several tables | Use .Select() projection to a DTO instead of loading full entity graphs. |
| Query needs to filter to a tenant or soft-deleted rows globally | Use EF Core global query filters instead of repeating the filter in every query. |
| Migration touches a large, heavily used table | Review it against skills/50-database/migrations-and-zero-downtime-schema-change/SKILL.md before applying in production. |
| Reporting query has multiple complex joins/aggregations | Prefer skills/30-backend/dapper-and-raw-sql/SKILL.md over forcing it through LINQ-to-Entities. |

## Reference implementation

Fluent API configuration keeping the domain entity free of ORM concerns:

```csharp
public class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> builder)
    {
        builder.ToTable("Orders");
        builder.HasKey(o => o.Id);
        builder.Property(o => o.Status).HasConversion<string>().HasMaxLength(20);

        builder.OwnsOne(o => o.ShippingAddress, a =>
        {
            a.Property(p => p.Street).HasColumnName("ShippingStreet");
            a.Property(p => p.City).HasColumnName("ShippingCity");
        });

        builder.HasMany(o => o.Lines)
            .WithOne()
            .HasForeignKey("OrderId")
            .OnDelete(DeleteBehavior.Cascade);

        builder.Metadata.FindNavigation(nameof(Order.Lines))!
            .SetPropertyAccessMode(PropertyAccessMode.Field);

        builder.HasQueryFilter(o => !o.IsDeleted);
    }
}
```

- PropertyAccessMode.Field lets EF Core populate a private backing field for Lines while the domain exposes only IReadOnlyList<OrderLine>.
- HasQueryFilter applies a global soft-delete filter automatically to every query against Order.

### Projecting to a DTO to avoid over-fetching (C#)

Avoid loading full aggregates for read-only list views:

```csharp
var summaries = await db.Orders
    .Where(o => o.CustomerId == customerId)
    .Select(o => new OrderSummaryDto
    {
        Id = o.Id,
        Status = o.Status.ToString(),
        Total = o.Lines.Sum(l => l.UnitPrice * l.Quantity)
    })
    .AsNoTracking()
    .ToListAsync(ct);
```

## Checklist

- [ ] Domain entities contain no EF Core attributes or references; all mapping is Fluent API in Infrastructure.
- [ ] Value objects are mapped as owned types or value converters, not flattened primitives on the entity.
- [ ] Lazy loading proxies are disabled; related data is loaded via explicit Include or projection.
- [ ] Read-only queries use AsNoTracking() and project to DTOs where full aggregates aren't needed.
- [ ] Migrations are generated per schema change and reviewed before merging.
- [ ] Migration application is an explicit pipeline step, not automatic on every app startup in production.

## Anti-patterns

- **Data annotations on domain entities** - Sprinkling [Required], [Column] attributes on Domain classes, coupling the domain model to EF Core.
- **Lazy loading left enabled** - Allowing implicit lazy loading, causing invisible N+1 queries that only surface under load.
- **Loading full graphs for list views** - Fetching entire aggregates with all navigation properties just to render a summary list.
- **Auto-migrate on startup in production** - Calling Database.Migrate() in Program.cs for a production service, risking uncontrolled schema changes on every deploy.
- **Public setters on collection navigation properties** - Exposing List<T> setters publicly, letting callers replace an aggregate's child collection and break invariants.

## Verification

- SQL logging or a profiler shows no unexpected N+1 query patterns for common list/detail screens.
- `dotnet ef migrations add` produces a clean, reviewable diff matching the intended domain change.
- Domain project has zero EF Core package references (verified via project reference check).
- Read-heavy endpoints use AsNoTracking projections, confirmed by code review or query plan inspection.

## References

- skills/20-architecture/domain-driven-design/SKILL.md
- skills/50-database/relational-data-modeling/SKILL.md
- skills/50-database/migrations-and-zero-downtime-schema-change/SKILL.md
- Microsoft Learn — EF Core documentation.
