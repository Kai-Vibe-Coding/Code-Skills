---
name: refactoring-and-legacy-code
description: Use when you need to safely change behavior or improve the structure of code that has little or no existing test coverage.
category: quality
tags: [refactoring, legacy-code, technical-debt]
maturity: stable
updated: 2026-08-21
---

## Purpose

Legacy code — code without adequate tests, not necessarily old code — is risky to change because there's no safety net to confirm a refactor didn't alter behavior. This skill covers safely characterizing existing behavior with tests before refactoring, making small reversible steps, and using established refactoring patterns rather than rewriting from scratch.

It treats 'add tests, then refactor' as the default approach to legacy code, reserving a full rewrite for the rare cases where the existing code is genuinely beyond safe incremental repair.

## When to use / When NOT to use

**Use this skill when:**

- You need to change or extend a piece of code with little or no existing test coverage.
- A codebase area is described as 'nobody wants to touch it' due to fear of breaking something.
- You are deciding between refactoring incrementally versus rewriting a component from scratch.

**Do NOT use this skill when:**

- The code already has solid test coverage — see skills/70-quality/test-strategy/SKILL.md's normal workflow instead, no special legacy-code caution needed.
- The change is a trivial, well-isolated addition with no risk to existing behavior.

## Prerequisites

- skills/70-quality/unit-testing-dotnet/SKILL.md and skills/70-quality/integration-testing/SKILL.md for the testing techniques used to add a safety net.
- Version control with the ability to make small, incremental, revertible commits.

## Workflow

1. **Write characterization tests before changing anything** - Capture the code's current actual behavior (bugs and all) in tests, giving a safety net for the refactor.
2. **Identify seams to break dependencies for testability** - Find a point where a dependency can be substituted (extract an interface, inject a parameter) without a large rewrite.
3. **Make the smallest possible refactoring steps** - Extract a method, rename a variable, or introduce a parameter object one step at a time, running tests after each.
4. **Never refactor and change behavior in the same commit** - Separate 'restructure without changing behavior' commits from 'add new behavior' commits, so each is independently reviewable and revertible.
5. **Apply established refactoring patterns by name** - Extract Method, Extract Class, Replace Conditional with Polymorphism — recognized patterns are safer and more communicable than ad hoc restructuring.
6. **Improve test coverage incrementally as you touch code** - Add tests for the specific area being modified rather than attempting a big-bang full-codebase test-writing effort.
7. **Reserve a rewrite for genuinely irreparable code** - Only consider a full rewrite when incremental refactoring is demonstrably infeasible, and even then scope it as narrowly as possible.
8. **Track and pay down technical debt deliberately** - Log significant known debt as a ticket with context, rather than leaving it as an unspoken, undocumented risk.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Code has zero tests and needs a bug fix | Write characterization tests capturing current behavior first, then fix the bug with tests as a safety net. |
| A class has a hard dependency preventing any testing (e.g. static call, `new` in constructor) | Introduce a seam (extract interface, inject dependency) as the very first small step before attempting further refactoring. |
| A large method mixes several responsibilities | Apply Extract Method repeatedly to separate them, verifying behavior is unchanged after each small step. |
| The team is tempted to 'just rewrite it' | Default to incremental refactoring first; a rewrite carries high risk of losing undocumented business rules embedded in the old code. |
| A refactor and a behavior change both seem needed at once | Split them into separate commits/PRs — refactor first (behavior-preserving), then change behavior as a distinct, reviewable step. |

## Reference implementation

Introducing a seam to make a previously untestable class testable:

```csharp
// Before: hard dependency on a static call, impossible to unit test
public class InvoiceService
{
    public decimal CalculateTotal(Invoice invoice)
    {
        var taxRate = TaxRateProvider.GetCurrentRate(); // static call, untestable
        return invoice.Subtotal * (1 + taxRate);
    }
}

// After: seam introduced via constructor injection, now testable in isolation
public class InvoiceService
{
    private readonly ITaxRateProvider _taxRateProvider;
    public InvoiceService(ITaxRateProvider taxRateProvider) => _taxRateProvider = taxRateProvider;

    public decimal CalculateTotal(Invoice invoice)
    {
        var taxRate = _taxRateProvider.GetCurrentRate();
        return invoice.Subtotal * (1 + taxRate);
    }
}
```

- This single small change (extract an interface, inject it) is the entire first commit — no other behavior changes bundled in.
- Once this seam exists, a unit test can substitute a fake ITaxRateProvider and safely verify CalculateTotal's logic.

### A characterization test capturing existing behavior before refactoring (C#)

Written to match what the code actually does today, bugs included, as a safety net for the refactor:

```csharp
[Fact]
public void CalculateTotal_MatchesCurrentObservedBehavior()
{
    var provider = Substitute.For<ITaxRateProvider>();
    provider.GetCurrentRate().Returns(0.08m);
    var service = new InvoiceService(provider);

    var result = service.CalculateTotal(new Invoice { Subtotal = 100m });

    Assert.Equal(108m, result); // captures current behavior before any refactor
}
```

## Checklist

- [ ] Characterization tests exist for the current behavior before any refactoring begins.
- [ ] Refactoring commits are kept separate from behavior-changing commits.
- [ ] Each refactoring step is small enough to verify immediately with a test run.
- [ ] Seams (interfaces, injected dependencies) are introduced deliberately to make previously untestable code testable.
- [ ] A full rewrite is only chosen after incremental refactoring is demonstrated to be infeasible.
- [ ] Known technical debt is tracked in a ticket with context, not left as silent, undocumented risk.

## Anti-patterns

- **Refactoring with no tests as a safety net** - Restructuring code with zero characterization tests first, with no way to confirm behavior wasn't accidentally changed.
- **Refactor and feature change bundled together** - Mixing a restructuring with new functionality in one commit, making it impossible to isolate which change caused a regression.
- **Big-bang rewrite as a default** - Reaching for a full rewrite as the first response to messy legacy code, discarding undocumented business logic embedded in it.
- **Giant refactoring steps** - Attempting to restructure an entire large class in one uninterrupted pass instead of small, independently verifiable steps.
- **Silent technical debt** - Leaving known-bad code unaddressed and undocumented, with no ticket or note explaining the risk for future engineers.

## Verification

- Characterization tests pass both before and immediately after each refactoring step, confirming behavior is unchanged.
- Git history shows refactoring commits are separate from behavior-changing commits.
- A previously untestable class now has passing unit tests after a seam was introduced.
- Any deferred technical debt has a corresponding tracked ticket with enough context to act on later.

## References

- skills/70-quality/unit-testing-dotnet/SKILL.md
- Michael Feathers — Working Effectively with Legacy Code.
- Martin Fowler — Refactoring: Improving the Design of Existing Code.
