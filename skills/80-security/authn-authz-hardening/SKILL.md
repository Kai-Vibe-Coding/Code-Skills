---
name: authn-authz-hardening
description: Use when hardening authentication and authorization flows to reduce risk of account takeover, session hijacking, and privilege escalation.
category: security
tags: [authentication, authorization, identity]
maturity: stable
updated: 2026-08-21
---

## Purpose

Authentication and authorization defects are among the most common and severe classes of vulnerability, since they directly control who can act as whom and what they can do. This skill covers hardening practices for these flows beyond the baseline covered in skills/30-backend/authentication-and-authorization/SKILL.md — focusing on defense-in-depth measures like MFA, session hardening, and token lifecycle management.

It is entirely defensive: it describes how to strengthen your own systems, not how to attack someone else's authentication mechanism.

## When to use / When NOT to use

**Use this skill when:**

- You are implementing or reviewing login, session management, or token issuance/validation logic.
- A security review flagged a weakness in session handling, password policy, or token expiry.
- You are adding multi-factor authentication or single sign-on to an existing system.

**Do NOT use this skill when:**

- You are implementing the initial, baseline authentication/authorization flow — start with skills/30-backend/authentication-and-authorization/SKILL.md and return here to harden it.
- You need to test whether an authentication bypass is exploitable on a live authorized target — see skills/80-security/authorized-penetration-testing/SKILL.md.

## Prerequisites

- skills/30-backend/authentication-and-authorization/SKILL.md for the baseline JWT/claims-based flow being hardened.
- skills/80-security/secrets-and-key-management/SKILL.md for how signing keys and secrets are stored securely.

## Workflow

1. **Enforce strong password policy and breached-password checks** - Require minimum length and complexity, and reject passwords found in known-breach databases (e.g. via HaveIBeenPwned's k-anonymity API).
2. **Support and encourage multi-factor authentication** - Offer TOTP or WebAuthn-based MFA and require it for privileged accounts and sensitive operations.
3. **Set short-lived access tokens with refresh token rotation** - Access tokens expire in minutes; refresh tokens are rotated on each use and revoked if reuse is detected.
4. **Bind sessions to context where feasible** - Detect anomalies like a session's IP or user agent changing abruptly, and re-authenticate or alert accordingly.
5. **Rate-limit and lock out after repeated failed login attempts** - Apply exponential backoff or temporary lockout after a threshold of failed attempts, while avoiding permanent denial-of-service against legitimate users.
6. **Invalidate all sessions on password change or suspected compromise** - A password reset must revoke existing refresh tokens and active sessions, not just change the credential going forward.
7. **Apply the principle of least privilege to authorization scopes** - Tokens carry the minimum scope/claims needed for the current operation, not blanket admin-equivalent access.
8. **Log authentication events for detection, without logging secrets** - Successful/failed logins, MFA challenges, and token revocations are logged with enough context to detect abuse.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A user account is flagged as privileged (admin, finance) | Require MFA enforcement for that account, not just optional availability. |
| A refresh token is presented that was already used once before | Treat this as a reuse/compromise signal, revoke the entire token family immediately. |
| A user changes their password | Revoke all existing sessions and refresh tokens for that user immediately, forcing re-authentication everywhere. |
| An API needs to act on behalf of a service rather than a user | Use a scoped service-to-service credential (e.g. client credentials grant) rather than reusing a user's token. |
| Login attempts fail repeatedly from the same account | Apply progressive backoff/lockout, while ensuring the mechanism cannot itself be abused to lock out a legitimate user indefinitely. |

## Reference implementation

Refresh token rotation with reuse detection in ASP.NET Core:

```csharp
public async Task<TokenResult> RefreshAsync(string presentedRefreshToken, CancellationToken ct)
{
    var stored = await _tokenStore.FindByHashAsync(Hash(presentedRefreshToken), ct);

    if (stored is null)
        throw new SecurityTokenException("Unknown refresh token.");

    if (stored.WasUsed)
    {
        // Reuse of an already-rotated token signals possible theft - revoke the whole family.
        await _tokenStore.RevokeFamilyAsync(stored.FamilyId, ct);
        throw new SecurityTokenException("Refresh token reuse detected; session revoked.");
    }

    await _tokenStore.MarkUsedAsync(stored.Id, ct);
    var newRefreshToken = await _tokenStore.IssueAsync(stored.UserId, stored.FamilyId, ct);
    var newAccessToken = _jwtIssuer.IssueAccessToken(stored.UserId, lifetime: TimeSpan.FromMinutes(10));

    return new TokenResult(newAccessToken, newRefreshToken);
}
```

- FamilyId groups all refresh tokens descending from a single original login, allowing a full family revocation on reuse detection.
- Access tokens are kept short-lived (10 minutes) so a leaked access token has a small usable window.

### Revoking all sessions on password change (C#)

A credential change must invalidate everything issued before it:

```csharp
public async Task ChangePasswordAsync(Guid userId, string newPassword, CancellationToken ct)
{
    await _userStore.SetPasswordHashAsync(userId, _hasher.Hash(newPassword), ct);

    // Revoke every active refresh token family for this user, forcing re-login everywhere.
    await _tokenStore.RevokeAllForUserAsync(userId, ct);
}
```

## Checklist

- [ ] Access tokens are short-lived; refresh tokens rotate on use and detect reuse.
- [ ] MFA is enforced for privileged accounts and available to all users.
- [ ] Password changes and suspected compromise revoke all existing sessions/tokens for that user.
- [ ] Failed login attempts are rate-limited/backed off without enabling a denial-of-service against legitimate users.
- [ ] Tokens carry least-privilege scopes/claims for the operation at hand, not blanket access.
- [ ] Authentication events are logged for detection without logging secrets or full tokens.

## Anti-patterns

- **Long-lived, non-rotating refresh tokens** - Issuing a refresh token that never expires or rotates, giving an attacker who steals it indefinite access.
- **No reuse detection** - Accepting a rotated-away refresh token without treating its reuse as a compromise signal.
- **Password change without session revocation** - Letting existing sessions/tokens remain valid after a user changes their password due to a suspected compromise.
- **MFA as optional for admins** - Allowing privileged accounts to operate without MFA enforcement, leaving the most sensitive accounts least protected.
- **Unbounded login attempts** - Allowing unlimited password guesses against an account with no rate limiting or lockout.

## Verification

- A test confirms that reusing a rotated-away refresh token revokes the entire token family.
- A test confirms all sessions are invalidated immediately after a password change.
- MFA enforcement is confirmed active for all accounts flagged as privileged.
- A login rate-limit test confirms lockout/backoff triggers after a defined threshold of failed attempts.

## References

- skills/30-backend/authentication-and-authorization/SKILL.md
- skills/80-security/secrets-and-key-management/SKILL.md
- OWASP Authentication Cheat Sheet.
