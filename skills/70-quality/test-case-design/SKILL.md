---
name: test-case-design
description: Use when designing the specific test cases for a piece of functionality to ensure meaningful coverage of behavior, edge cases, and failure modes.
category: quality
tags: [test-case-design, boundary-analysis, equivalence-partitioning]
maturity: stable
updated: 2026-08-21
---

## Purpose

Writing tests only for the 'happy path' leaves edge cases, boundary conditions, and error handling unverified, exactly where bugs tend to hide. This skill covers systematic test case design techniques — equivalence partitioning, boundary value analysis, and decision tables — that generate a compact but meaningful set of test cases rather than either too few or an unfocused excess.

It applies to unit, integration, and manual test case design alike, since the underlying technique for identifying what to test is the same regardless of the test level.

## When to use / When NOT to use

**Use this skill when:**

- You are writing tests for a new function, endpoint, or business rule.
- A bug was found in production that existing tests should have caught, indicating a coverage gap.
- You need to review whether a test suite for a piece of logic is actually comprehensive.

**Do NOT use this skill when:**

- You need overall strategy about test type/pyramid balance — see skills/70-quality/test-strategy/SKILL.md instead.
- The functionality is trivial (e.g. a pure pass-through) with no meaningful branching or edge cases to enumerate.

## Prerequisites

- skills/70-quality/test-strategy/SKILL.md for which test level (unit/integration/E2E) this case belongs in.
- A clear specification or acceptance criteria for the functionality being tested.

## Workflow

1. **Identify equivalence classes for each input** - Group inputs into classes expected to behave the same way (valid, invalid, boundary) to avoid redundant near-identical tests.
2. **Apply boundary value analysis at each class edge** - Test just inside, at, and just outside each boundary (e.g. quantity = 0, 1, max, max+1), since bugs cluster at boundaries.
3. **Cover both positive and negative cases** - Test that valid input succeeds and that invalid input is rejected with the correct error, not just the success path.
4. **Use a decision table for multiple interacting conditions** - When several boolean conditions combine to determine behavior, enumerate the combinations systematically rather than ad hoc.
5. **Include representative error and exception scenarios** - Network failure, timeout, and malformed input scenarios get explicit test cases, not just the well-formed case.
6. **Name tests to describe behavior, not implementation** - A test name should read as a specification: 'Should reject order when quantity is zero', not 'Test1'.
7. **Review test cases against the specification before writing code (TDD) or after (test-after)** - Confirm the enumerated cases actually map to the acceptance criteria, catching missed requirements early.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| An input has a numeric range (e.g. 1-100) | Test the boundaries: 0 (just below), 1 (min), 100 (max), 101 (just above), plus a mid-range valid value. |
| An input has several independent boolean flags affecting behavior | Build a decision table enumerating the meaningful flag combinations rather than guessing which matter. |
| Many inputs would exercise the same code path identically | Pick one representative value per equivalence class instead of testing every possible value. |
| A function can throw for multiple distinct reasons | Write a distinct test case per exception type/reason, asserting the specific error, not just 'an exception is thrown'. |
| A previous production bug slipped through testing | Add a regression test reproducing that exact scenario before considering the bug fully closed. |

## Reference implementation

Boundary value and equivalence-partition test cases for a discount rule:

```csharp
public class DiscountCalculatorTests
{
    [Theory]
    [InlineData(0, 0)]      // below minimum quantity: no discount
    [InlineData(1, 0)]      // boundary: minimum non-discount quantity
    [InlineData(10, 5)]     // boundary: exactly at discount threshold
    [InlineData(11, 5)]     // just above threshold: same discount tier
    [InlineData(100, 15)]   // upper tier boundary
    public void CalculatesDiscountPercentForQuantity(int quantity, int expectedPercent)
    {
        var result = DiscountCalculator.PercentFor(quantity);
        Assert.Equal(expectedPercent, result);
    }

    [Fact]
    public void ThrowsForNegativeQuantity()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() => DiscountCalculator.PercentFor(-1));
    }
}
```

- Each InlineData row targets a specific boundary or equivalence class, not an arbitrary or redundant value.
- The negative-quantity case is a distinct equivalence class (invalid input) tested separately from the valid-range boundaries.

### A decision table for a shipping-eligibility rule (Markdown)

Enumerating combinations of conditions systematically before writing test cases:

```markdown
| Is Member | Order Total > $50 | Region Supported | Result           |
|-----------|--------------------|------------------|-------------------|
| Yes        | Yes                | Yes              | Free shipping     |
| Yes        | No                 | Yes              | Standard shipping |
| No         | Yes                | Yes              | Standard shipping |
| No         | Yes                | No               | Rejected          |
```

## Checklist

- [ ] Test cases cover equivalence classes (valid, invalid, boundary) rather than redundant near-identical inputs.
- [ ] Boundary values are explicitly tested just inside, at, and just outside each meaningful threshold.
- [ ] Both positive (valid input succeeds) and negative (invalid input rejected correctly) cases are covered.
- [ ] Interacting conditions are enumerated via a decision table where more than one flag affects behavior.
- [ ] Test names describe expected behavior, readable as a specification.
- [ ] Every previously found production bug has a corresponding regression test case.

## Anti-patterns

- **Happy-path-only testing** - Writing tests only for well-formed, typical input, leaving edge cases and error handling completely unverified.
- **Redundant near-identical test cases** - Testing quantity=5, 6, 7, 8 when they're all in the same equivalence class, adding maintenance cost with no new coverage.
- **Untested boundaries** - Testing quantity=50 for a rule that changes behavior at quantity=50, but never testing 49 or 51 directly at the edge.
- **Vague test names** - Naming tests Test1, Test2 or TestDiscount, giving no indication of what specific behavior is being verified when it fails.
- **Guessing at decision table combinations** - Testing only a couple of ad hoc combinations of interacting conditions instead of systematically enumerating the meaningful ones.

## Verification

- A code review confirms test cases explicitly cover each boundary of every meaningful numeric range or threshold.
- Both a valid and an invalid case exist for every distinct equivalence class identified in the specification.
- Test names alone (without reading the body) convey what specific behavior each test verifies.
- A previously reported production bug has an associated regression test that would fail without the fix.

## References

- skills/70-quality/test-strategy/SKILL.md
- skills/70-quality/unit-testing-dotnet/SKILL.md
- ISTQB — Equivalence Partitioning and Boundary Value Analysis.
