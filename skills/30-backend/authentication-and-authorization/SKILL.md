---
name: authentication-and-authorization
description: Use when implementing login, token validation, or access-control checks in a .NET API and you need a consistent pattern for authentication and fine-grained authorization.
category: backend
tags: [authn, authz, jwt, policies]
maturity: stable
updated: 2026-08-21
---

## Purpose

Authentication (who is the caller) and authorization (what can they do) are frequently conflated, leading to ad hoc role checks scattered through controllers. This skill establishes JWT-bearer authentication with ASP.NET Core and policy-based authorization so access rules are declared once, testable, and consistently enforced.

It also covers the difference between role-based and resource-based (ownership) authorization, since most real applications need both.

## When to use / When NOT to use

**Use this skill when:**

- You are implementing or reviewing login, token issuance, or endpoint protection in an ASP.NET Core API.
- Authorization rules are becoming complex (roles plus per-resource ownership plus feature flags).
- You need to add a new protected endpoint and want to apply the established pattern.

**Do NOT use this skill when:**

- You are designing the deeper cryptographic details of a custom identity provider — defer to a vetted identity platform instead of building one from scratch.
- The task is purely about penetration testing auth mechanisms — see skills/80-security/authorized-penetration-testing/SKILL.md instead.

## Prerequisites

- skills/80-security/authn-authz-hardening/SKILL.md for the security hardening checklist this pattern must satisfy.
- skills/80-security/secrets-and-key-management/SKILL.md for storing signing keys/secrets.
- An identity provider (e.g. OpenID Connect provider) issuing JWTs, or a plan to use one.

## Workflow

1. **Configure JWT bearer authentication** - Register AddAuthentication().AddJwtBearer with the issuer, audience, and signing key validation parameters.
2. **Never hand-roll token validation** - Rely on the Microsoft.IdentityModel libraries' TokenValidationParameters rather than parsing/verifying JWTs manually.
3. **Define authorization policies, not inline role checks** - Register named policies (e.g. 'CanManageOrders') combining role and claim requirements in one place.
4. **Apply [Authorize(Policy = ...)] on endpoints** - Reference policies by name on controllers/minimal API endpoints instead of checking User.IsInRole inline.
5. **Add resource-based authorization for ownership checks** - Use IAuthorizationHandler for rules like 'user can only edit their own order', evaluated against the loaded resource.
6. **Keep claims minimal and purposeful** - Only include claims actually needed for authorization decisions in the token; avoid embedding excessive PII.
7. **Test authorization policies in isolation** - Unit test each IAuthorizationHandler with different claim/resource combinations, independent of HTTP.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Access depends only on a fixed role | Use a simple policy requiring that role claim (e.g. RequireRole("Admin")) . |
| Access depends on ownership of a specific resource | Use a resource-based IAuthorizationHandler evaluated against the loaded entity, not just the token's claims. |
| Multiple endpoints share the same complex rule combination | Extract it into one named policy so the rule is defined once and reused. |
| Feature access varies by subscription tier | Combine a claim-based policy with skills/30-backend/configuration-and-feature-flags/SKILL.md rather than hardcoding tier checks. |
| Service-to-service calls need authorization | Use client-credentials tokens with scope claims, checked via policies, rather than shared static API keys. |

## Reference implementation

JWT bearer authentication and named authorization policies:

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = builder.Configuration["Auth:Authority"];
        options.Audience = builder.Configuration["Auth:Audience"];
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromMinutes(1)
        };
    });

builder.Services.AddAuthorizationBuilder()
    .AddPolicy("CanManageOrders", policy =>
        policy.RequireRole("OrderManager", "Admin"))
    .AddPolicy("CanViewOwnOrder", policy =>
        policy.Requirements.Add(new OwnsResourceRequirement()));

app.MapGet("/orders/{id}", GetOrder).RequireAuthorization("CanViewOwnOrder");
```

- ClockSkew is deliberately kept small (rather than the 5-minute default) to reduce the window an expired token remains accepted.
- Policies are named after the capability they grant ('CanManageOrders'), not the role, decoupling endpoint code from role names.

### Resource-based authorization handler for ownership checks (C#)

Enforcing that a user can only access their own order:

```csharp
public class OwnsResourceRequirement : IAuthorizationRequirement { }

public class OwnsOrderHandler : AuthorizationHandler<OwnsResourceRequirement, Order>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context, OwnsResourceRequirement requirement, Order resource)
    {
        var userId = context.User.FindFirstValue(ClaimTypes.NameIdentifier);
        if (resource.CustomerId.ToString() == userId || context.User.IsInRole("Admin"))
            context.Succeed(requirement);
        return Task.CompletedTask;
    }
}
```

## Checklist

- [ ] JWT validation uses the standard Microsoft.IdentityModel pipeline, not hand-rolled parsing.
- [ ] Authorization is expressed as named policies, not inline User.IsInRole checks scattered in controllers.
- [ ] Resource ownership is enforced via resource-based authorization handlers, not just role checks.
- [ ] Tokens include only the claims needed for authorization decisions.
- [ ] Authorization handlers are unit tested against multiple claim/resource combinations.
- [ ] Clock skew and token lifetime validation are explicitly configured, not left at insecure defaults.

## Anti-patterns

- **Role checks scattered in controllers** - if (User.IsInRole("Admin")) checks duplicated across many actions instead of one named policy.
- **Hand-rolled JWT parsing** - Manually decoding and verifying JWT signatures instead of relying on the vetted TokenValidationParameters pipeline.
- **Claims-only ownership checks** - Trusting a customerId claim in the token for ownership instead of comparing against the actual loaded resource, allowing stale/forged claims to bypass checks.
- **Static shared API keys for service-to-service auth** - Using one long-lived shared secret for all internal service calls instead of scoped, short-lived credentials.
- **Overloaded JWTs** - Cramming full user profile/PII into JWT claims instead of keeping tokens minimal and fetching detail server-side when needed.

## Verification

- Attempting to access another user's resource with a valid token for a different user returns 403, verified by an integration test.
- Expired or tampered tokens are rejected, verified by a negative test case.
- Every protected endpoint uses a named policy, confirmed by a code search for RequireAuthorization/[Authorize].
- Authorization handler unit tests cover both allow and deny paths for each policy.

## References

- skills/80-security/authn-authz-hardening/SKILL.md
- skills/80-security/secrets-and-key-management/SKILL.md
- Microsoft Learn — ASP.NET Core authorization policies.
