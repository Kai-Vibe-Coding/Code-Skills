---
name: object-mapping-and-dtos
description: Use when deciding how domain entities are translated to and from API request/response contracts without leaking internal model details.
category: backend
tags: [dto, mapping, api-contracts]
maturity: stable
updated: 2026-08-21
---

## Purpose

Returning domain entities directly from API endpoints couples the wire contract to internal implementation details and risks leaking fields that were never meant to be public. This skill establishes explicit DTOs for every API boundary and a consistent, low-overhead mapping strategy between domain models and those DTOs.

It also covers when to hand-write mapping versus using a mapping library, since generated mapping code can hide bugs when domain and DTO shapes diverge silently.

## When to use / When NOT to use

**Use this skill when:**

- You are defining request/response contracts for a new API endpoint.
- Domain entities are currently being serialized directly as API responses.
- Mapping code between layers has become repetitive and error-prone.

**Do NOT use this skill when:**

- The DTO and domain shapes are identical and trivial (e.g. a single value lookup) — a direct return may be acceptable if reviewed carefully.
- You're inside a single layer (e.g. Domain to Domain) where no contract boundary is being crossed.

## Prerequisites

- skills/20-architecture/clean-and-onion-architecture/SKILL.md for where DTOs live (Application/Api boundary).
- skills/20-architecture/api-design-rest/SKILL.md for the contract shape DTOs should follow.

## Workflow

1. **Define a DTO for every request and response shape** - Never serialize a domain entity or EF Core entity directly as an API response.
2. **Keep DTOs flat and purpose-built per endpoint** - Avoid one giant shared DTO reused everywhere; a list view and a detail view usually need different shapes.
3. **Map explicitly for anything with business logic in the translation** - Hand-write mapping code when field names differ meaningfully or computed values are involved.
4. **Use a mapping library for simple, high-volume 1:1 mappings** - Mapperly or AutoMapper can reduce boilerplate for straightforward property-to-property mapping, with generated mappings reviewed.
5. **Never map DTOs back into domain entities directly** - Reconstruct or mutate domain entities via factory methods/domain methods, not by assigning DTO fields onto them.
6. **Version DTOs deliberately when contracts must change** - Add new fields as optional or introduce a new versioned DTO rather than silently changing meaning of existing fields.
7. **Unit test mapping logic for anything non-trivial** - Any mapping involving computed fields or conditional logic gets a direct unit test.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Endpoint returns a simple 1:1 shape of an entity | A source-generated mapper (e.g. Mapperly) is fine, keeping mapping code minimal. |
| Mapping involves computed or conditional fields | Hand-write the mapping method explicitly so the logic is visible and testable, not hidden in library conventions. |
| Command input DTO needs to become a domain aggregate | Use a domain factory method (Order.Create(...)) rather than assigning DTO properties onto a new entity instance directly. |
| Different clients need different views of the same entity | Define separate DTOs per client need (e.g. OrderSummaryDto vs OrderDetailDto) instead of one bloated shared DTO. |
| A mapping library's generated code silently ignores a new domain field | Treat this as a bug signal — add an explicit test asserting every expected field is mapped. |

## Reference implementation

Explicit mapping from a domain aggregate to a response DTO:

```csharp
public record OrderDetailDto(
    Guid Id,
    string Status,
    decimal Total,
    IReadOnlyList<OrderLineDto> Lines);

public record OrderLineDto(string ProductName, int Quantity, decimal UnitPrice);

public static class OrderMappingExtensions
{
    public static OrderDetailDto ToDetailDto(this Order order) => new(
        order.Id,
        order.Status.ToString(),
        order.Lines.Sum(l => l.UnitPrice * l.Quantity),
        order.Lines.Select(l => new OrderLineDto(
            l.ProductName, l.Quantity, l.UnitPrice)).ToList());
}
```

- Total is computed during mapping rather than stored redundantly on the entity, keeping the domain model the single source of truth.
- Extension methods keep mapping colocated with the DTO definitions, easy to find and test.

### Source-generated mapping for simple 1:1 shapes (Mapperly, C#)

Reducing boilerplate for straightforward property mapping, with compile-time-checked output:

```csharp
[Mapper]
public partial class ProductMapper
{
    public partial ProductSummaryDto ToDto(Product product);
}

// Generated at compile time; a build warning surfaces if a Product property
// has no corresponding DTO property, catching silent drift early.
```

## Checklist

- [ ] No domain or EF Core entity is serialized directly as an API response.
- [ ] DTOs are purpose-built per endpoint rather than one shared bloated shape.
- [ ] Mapping involving computed or conditional logic is hand-written and unit tested.
- [ ] Domain entities are constructed/mutated via factory or domain methods, never by direct DTO field assignment.
- [ ] Mapping libraries used for simple cases have generated output reviewed, or compile-time warnings enabled for unmapped fields.
- [ ] DTO contract changes are additive or explicitly versioned, not silently breaking.

## Anti-patterns

- **Serializing entities directly** - Returning an EF Core tracked entity directly from a controller action, leaking navigation properties and internal fields.
- **God DTO** - One giant DTO reused across list, detail, and edit endpoints, forcing clients to handle irrelevant null fields.
- **DTO fields assigned onto domain entities** - Bypassing domain factory/methods by setting entity properties directly from an incoming DTO, skipping invariant checks.
- **Silent mapping drift** - A mapping library silently ignoring a newly added domain field with no build warning or test catching the gap.
- **Breaking DTO changes without versioning** - Renaming or repurposing an existing response field in place, breaking existing API consumers without notice.

## Verification

- A code search confirms no controller/endpoint returns a domain or EF Core entity type directly.
- Unit tests exist for every mapping method containing computed or conditional logic.
- Adding a new domain field either produces a build warning (generated mapping) or requires an explicit DTO/mapping update (hand-written).
- API contract changes are reviewed against skills/20-architecture/api-design-rest/SKILL.md versioning guidance before merging.

## References

- skills/20-architecture/api-design-rest/SKILL.md
- skills/20-architecture/clean-and-onion-architecture/SKILL.md
- Mapperly / AutoMapper documentation.
