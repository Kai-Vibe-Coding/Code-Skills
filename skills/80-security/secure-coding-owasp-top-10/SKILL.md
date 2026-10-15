---
name: secure-coding-owasp-top-10
description: Use when writing or reviewing application code to defensively guard against the most common and impactful vulnerability classes described in the OWASP Top 10.
category: security
tags: [owasp, secure-coding, vulnerabilities]
maturity: stable
updated: 2026-08-21
---

## Purpose

Most real-world application vulnerabilities fall into a well-known, recurring set of categories that the OWASP Top 10 catalogs. This skill covers defensive coding practices addressing the most relevant categories for typical web applications — injection, broken access control, cryptographic failures, and insecure design — with concrete, non-exploit-focused mitigations.

It is strictly defensive: it describes how to prevent and detect these issues in code you own, not how to exploit them in systems you don't have authorization to test.

## When to use / When NOT to use

**Use this skill when:**

- You are writing code that accepts user input, handles authentication, or manages sensitive data.
- You are reviewing a PR and want a checklist of common vulnerability classes to check for.
- A security scan flagged a finding and you need to understand the underlying defensive principle.

**Do NOT use this skill when:**

- You need to actually test whether a vulnerability is exploitable in an authorized target — see skills/80-security/authorized-penetration-testing/SKILL.md, which requires explicit authorization.
- You're investigating a live suspected compromise — see skills/80-security/security-incident-response/SKILL.md instead.

## Prerequisites

- skills/80-security/input-validation-and-output-encoding/SKILL.md for the injection-prevention details this skill references.
- skills/80-security/authn-authz-hardening/SKILL.md for the access-control details this skill references.

## Workflow

1. **Prevent injection with parameterization, never string concatenation** - SQL, command, and LDAP queries always use parameterized APIs; never build queries by concatenating untrusted input.
2. **Enforce access control on every request, server-side** - Never rely on hiding a UI button; check authorization server-side for every sensitive action, per skills/30-backend/authentication-and-authorization/SKILL.md.
3. **Use strong, standard cryptography, never home-grown** - Use vetted libraries and current algorithms (e.g. bcrypt/Argon2 for passwords, AES-GCM for encryption); never invent your own cipher or hashing scheme.
4. **Validate and constrain all input at trust boundaries** - Reject malformed input by allow-list wherever possible, per skills/80-security/input-validation-and-output-encoding/SKILL.md.
5. **Apply secure defaults and fail closed** - A misconfigured or failed authorization check should deny access by default, not silently allow it.
6. **Keep dependencies patched and monitored** - Track known-vulnerable dependencies continuously, per skills/80-security/dependency-and-supply-chain-security/SKILL.md.
7. **Log security-relevant events without logging secrets** - Authentication attempts and access-control denials are logged for detection, while passwords/tokens are never logged.
8. **Design for least privilege from the start** - Services, database accounts, and users get the minimum permissions needed, not broad default access 'to be safe'.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Building a query with user-supplied input | Always use parameterized queries/prepared statements; never string-concatenate input into SQL. |
| Storing user passwords | Use a vetted password hashing algorithm (bcrypt/Argon2) with a proper work factor; never store plaintext or use a fast general-purpose hash like MD5/SHA1. |
| An endpoint performs a sensitive action based on a resource ID in the URL | Always verify server-side that the authenticated user is authorized for that specific resource, not just that they're logged in. |
| A dependency has a known critical CVE | Patch or mitigate it promptly per skills/80-security/dependency-and-supply-chain-security/SKILL.md, don't defer indefinitely. |
| An error occurs during an authorization check | Fail closed (deny access) by default; never fail open due to an exception being swallowed. |

## Reference implementation

Defensive coding against injection and broken access control in a single endpoint:

```csharp
[HttpGet("/orders/{orderId}")]
[Authorize]
public async Task<IActionResult> GetOrder(Guid orderId, CancellationToken ct)
{
    var order = await _mediator.Send(new GetOrderQuery(orderId), ct);
    if (order is null) return NotFound();

    // Server-side authorization check, never trust that the UI only shows this button
    // to authorized users - this must be enforced here regardless of client behavior.
    var authResult = await _authorizationService.AuthorizeAsync(User, order, "CanViewOwnOrder");
    if (!authResult.Succeeded) return Forbid();

    return Ok(order.ToDetailDto());
}

// Underlying query uses parameterized access via EF Core/Dapper - never raw string SQL:
// SELECT * FROM orders WHERE id = @orderId  (parameter, not concatenated)
```

- AuthorizeAsync is checked explicitly against the loaded resource, not inferred from the URL or client-side state.
- Returning NotFound before Forbid where appropriate avoids leaking the existence of resources to unauthorized users, depending on the sensitivity of the data.

### Storing passwords with a vetted hashing algorithm (C#)

Never store plaintext or use a fast general-purpose hash for passwords:

```csharp
public string HashPassword(string password) =>
    BCrypt.Net.BCrypt.HashPassword(password, workFactor: 12);

public bool VerifyPassword(string password, string storedHash) =>
    BCrypt.Net.BCrypt.Verify(password, storedHash);
```

## Checklist

- [ ] All database/command queries use parameterized APIs; no string concatenation of user input into queries.
- [ ] Authorization is enforced server-side on every sensitive action, never inferred from client-side UI state alone.
- [ ] Passwords are hashed with a vetted, purpose-built algorithm (bcrypt/Argon2), never plaintext or a fast general hash.
- [ ] Input is validated against an allow-list at every trust boundary.
- [ ] Authorization and cryptographic failures fail closed (deny) by default.
- [ ] Dependencies are monitored and patched for known vulnerabilities on an ongoing basis.

## Anti-patterns

- **String-concatenated queries** - Building a SQL/command string by concatenating untrusted input, opening the door to injection attacks.
- **Client-side-only access control** - Hiding a delete button in the UI for unauthorized users but not checking authorization server-side, allowing direct API calls to bypass it.
- **Home-grown cryptography** - Inventing a custom encryption or hashing scheme instead of using a vetted, standard, peer-reviewed library.
- **Failing open** - Swallowing an exception in an authorization check and defaulting to allowing access rather than denying it.
- **Logging secrets** - Writing passwords, tokens, or API keys into application logs in plaintext for debugging convenience.

## Verification

- A static analysis (SAST) scan finds no string-concatenated SQL/command construction in the codebase.
- An authorization test confirms a request for another user's resource is denied server-side, even with a valid token.
- Password storage uses a hashing algorithm confirmed to include salting and an appropriate work factor.
- A dependency scan shows no unpatched critical/high vulnerabilities in production dependencies.

## References

- OWASP Top 10 (owasp.org).
- skills/80-security/input-validation-and-output-encoding/SKILL.md
- skills/80-security/authn-authz-hardening/SKILL.md
- skills/80-security/dependency-and-supply-chain-security/SKILL.md
