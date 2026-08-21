---
name: validation-and-error-handling
description: Use when designing how a backend service validates input and reports errors consistently across all endpoints and use cases.
category: backend
tags: [validation, error-handling, problem-details]
maturity: stable
updated: 2026-08-21
---

## Purpose

Inconsistent validation and error responses make an API frustrating to integrate with and hide real bugs behind generic 500 errors. This skill establishes a layered validation strategy (input shape, business rule, domain invariant) and a single, consistent error response format using RFC 7807 Problem Details.

It also defines how exceptions map to HTTP status codes so client applications get predictable, machine-readable errors rather than parsing free-text messages.

## When to use / When NOT to use

**Use this skill when:**

- You are designing or auditing how a .NET API validates requests and returns error responses.
- Client teams report unpredictable or inconsistent error shapes across different endpoints.
- You are adding a new command/query and need to know where each kind of validation belongs.

**Do NOT use this skill when:**

- The service is a purely internal batch job with no external API surface — simpler logging-based error handling may suffice.
- You're deep in a single bug fix; a full validation strategy overhaul isn't warranted for a one-line change.

## Prerequisites

- skills/30-backend/cqrs-with-mediatr/SKILL.md if using pipeline behaviors for validation.
- skills/80-security/input-validation-and-output-encoding/SKILL.md for security-relevant input handling.
- FluentValidation (or equivalent) package for declarative input validation.

## Workflow

1. **Validate input shape at the API boundary** - Use model binding plus FluentValidation validators to reject malformed requests before they reach the Application layer.
2. **Validate business rules in Application handlers** - Rules like 'customer must have an active subscription' belong in the handler or a domain service, not the controller.
3. **Enforce invariants inside domain entities** - Rules intrinsic to the entity (e.g. order total must be positive) throw domain exceptions from within the entity itself.
4. **Map exceptions to Problem Details centrally** - A single exception-handling middleware converts known exception types to RFC 7807 responses with correct status codes.
5. **Distinguish validation errors from not-found and conflict errors** - 400 for validation, 404 for missing resources, 409 for conflicts — never collapse all failures to 500.
6. **Never leak internal exception details to clients** - Log full exception details server-side; return a safe, generic message and a correlation ID to the client.
7. **Return structured field-level errors for validation failures** - Include an 'errors' dictionary keyed by field name so client forms can highlight the exact problem.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Request has malformed JSON or missing required fields | Return 400 with field-level Problem Details errors from the input validator. |
| Business rule fails (e.g. insufficient balance) | Throw a specific domain/application exception and map it to 409 Conflict or 422 Unprocessable Entity. |
| Referenced resource doesn't exist | Throw a NotFoundException mapped to 404, never a generic 400. |
| An unexpected, unhandled exception occurs | Map it to 500 with a generic message and a correlation ID; log the full stack trace server-side only. |
| Client needs to distinguish retryable vs non-retryable errors | Use distinct status codes/error codes (e.g. 429 vs 400) so clients can decide whether to retry. |

## Reference implementation

Centralized exception-to-Problem-Details mapping middleware:

```csharp
app.UseExceptionHandler(errApp => errApp.Run(async context =>
{
    var feature = context.Features.Get<IExceptionHandlerFeature>();
    var ex = feature?.Error;
    var (status, title) = ex switch
    {
        ValidationException => (StatusCodes.Status400BadRequest, "Validation failed"),
        NotFoundException => (StatusCodes.Status404NotFound, "Resource not found"),
        ConflictException => (StatusCodes.Status409Conflict, "Conflict"),
        _ => (StatusCodes.Status500InternalServerError, "An unexpected error occurred")
    };

    var problem = new ProblemDetails
    {
        Status = status,
        Title = title,
        Extensions = { ["correlationId"] = context.TraceIdentifier }
    };
    if (ex is ValidationException ve)
        problem.Extensions["errors"] = ve.Errors.GroupBy(e => e.PropertyName)
            .ToDictionary(g => g.Key, g => g.Select(e => e.ErrorMessage).ToArray());

    context.Response.StatusCode = status;
    await context.Response.WriteAsJsonAsync(problem);
}));
```

- context.TraceIdentifier gives support teams a correlation ID to find the matching server-side log entry.
- Only ValidationException field errors are exposed; unhandled exceptions never leak stack traces to the client.

### Declarative FluentValidation validator (C#)

Input-shape validation applied automatically via a MediatR pipeline behavior:

```csharp
public class PlaceOrderCommandValidator : AbstractValidator<PlaceOrderCommand>
{
    public PlaceOrderCommandValidator()
    {
        RuleFor(x => x.CustomerId).NotEmpty();
        RuleFor(x => x.Lines).NotEmpty()
            .WithMessage("Order must contain at least one line item.");
        RuleForEach(x => x.Lines).ChildRules(line =>
        {
            line.RuleFor(l => l.Quantity).GreaterThan(0);
        });
    }
}
```

## Checklist

- [ ] Input-shape validation happens at the API boundary using declarative validators.
- [ ] Business rules live in Application handlers or domain services, not controllers.
- [ ] Entity invariants throw domain exceptions from within the entity, never bypassed.
- [ ] A single centralized middleware maps exceptions to consistent Problem Details responses.
- [ ] 400/404/409/500 are used distinctly and never collapsed into a generic error shape.
- [ ] Unhandled exceptions never leak stack traces or internal details to the client.

## Anti-patterns

- **Try/catch in every controller action** - Duplicating exception-to-response mapping logic in each endpoint instead of one centralized middleware.
- **Everything returns 400** - Collapsing not-found, conflict, and validation errors all into 400 Bad Request, making client-side error handling impossible.
- **Leaking stack traces** - Returning ex.ToString() or ex.StackTrace in the API response body, exposing internal implementation details.
- **Validation scattered ad hoc** - Re-implementing the same null/empty checks manually in multiple handlers instead of one declarative validator per command.
- **Swallowing exceptions silently** - Catching an exception and returning a generic success response, hiding failures from both the client and logs.

## Verification

- Every distinct failure mode (validation, not-found, conflict, unexpected) maps to a distinct, correct HTTP status code.
- API responses never include a stack trace or exception type name in production.
- Field-level validation errors are returned as structured data, not a single free-text message.
- A correlation ID in the error response can be matched to a corresponding server-side log entry.

## References

- RFC 7807 — Problem Details for HTTP APIs.
- FluentValidation documentation.
- skills/30-backend/cqrs-with-mediatr/SKILL.md
- skills/80-security/input-validation-and-output-encoding/SKILL.md
