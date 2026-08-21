---
name: configuration-and-feature-flags
description: Use when a service needs environment-specific configuration or the ability to toggle features safely without a full redeploy.
category: backend
tags: [configuration, feature-flags, options-pattern]
maturity: stable
updated: 2026-08-21
---

## Purpose

Hardcoded configuration values and ad hoc environment checks scattered through code make services fragile to deploy and risky to change behavior in production. This skill establishes the .NET Options pattern for strongly-typed, validated configuration, plus a feature flag strategy for toggling behavior safely without redeploying.

It distinguishes static configuration (connection strings, timeouts) from dynamic feature flags (gradual rollouts, kill switches), since they have different lifecycles and risk profiles.

## When to use / When NOT to use

**Use this skill when:**

- A service needs configuration values that differ across environments (dev, staging, production).
- You need to roll out a new feature gradually or be able to disable it instantly without a deploy.
- Configuration values are currently read via raw IConfiguration string lookups scattered through the codebase.

**Do NOT use this skill when:**

- The value never changes and is truly a compile-time constant (e.g. a fixed business rule threshold) — a flag adds needless indirection.
- You're storing secrets — use skills/80-security/secrets-and-key-management/SKILL.md instead of plain configuration.

## Prerequisites

- skills/80-security/secrets-and-key-management/SKILL.md for secret values that must never live in plain configuration.
- A feature flag provider selected (e.g. a hosted service or a simple database-backed flag store) if dynamic flags are needed.

## Workflow

1. **Define strongly-typed options classes** - One class per logical configuration section (e.g. EmailOptions), bound via IOptions<T>.
2. **Validate configuration at startup** - Use IValidateOptions<T> or data annotations so missing/invalid configuration fails fast at startup, not at first use.
3. **Never read raw configuration strings in business logic** - Inject IOptions<T> (or IOptionsSnapshot<T> for values that change without restart), not IConfiguration directly, into handlers.
4. **Separate static config from dynamic feature flags** - Static settings live in appsettings/environment variables; flags that change at runtime live in a feature flag store.
5. **Use feature flags for gradual rollout and kill switches** - Wrap new/risky functionality behind a flag so it can be disabled instantly without a redeploy.
6. **Scope flags to the right audience** - Support percentage rollout, per-tenant, or per-user targeting rather than a single global on/off switch when a gradual rollout is needed.
7. **Remove stale flags after full rollout** - Once a feature is fully rolled out and stable, delete the flag and the old code path to avoid permanent branching complexity.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A value differs only by environment (timeout, base URL) | Use the Options pattern bound from appsettings.{Environment}.json or environment variables. |
| A new feature needs to be tested with a subset of users first | Use a feature flag with percentage or per-tenant targeting. |
| A risky feature needs an instant kill switch in production | Wrap it in a feature flag checked at the point of use, not just at startup. |
| A flag has been fully rolled out for months | Remove the flag and the old code path; don't let flags accumulate indefinitely. |
| A configuration value is actually a secret | Move it to skills/80-security/secrets-and-key-management/SKILL.md's secret store, never plain appsettings.json. |

## Reference implementation

Strongly-typed, validated options bound and consumed via DI:

```csharp
public class EmailOptions
{
    public const string SectionName = "Email";
    [Required] public string SenderAddress { get; set; } = default!;
    [Range(1, 300)] public int TimeoutSeconds { get; set; } = 30;
}

builder.Services.AddOptions<EmailOptions>()
    .Bind(builder.Configuration.GetSection(EmailOptions.SectionName))
    .ValidateDataAnnotations()
    .ValidateOnStart();

public class EmailSender
{
    private readonly EmailOptions _options;
    public EmailSender(IOptions<EmailOptions> options) => _options = options.Value;

    public Task SendAsync(string to, string subject) =>
        SendViaSmtpAsync(_options.SenderAddress, to, subject, _options.TimeoutSeconds);
}
```

- ValidateOnStart() makes a missing SenderAddress fail the app at startup instead of at the first email send attempt.
- IOptions<T> is a singleton snapshot; use IOptionsSnapshot<T> instead if the value must refresh without an app restart.

### A feature flag guarding a risky new code path (C#)

Checked at the point of use so it can be disabled instantly without a redeploy:

```csharp
public class CheckoutService
{
    private readonly IFeatureManager _features;

    public async Task<CheckoutResult> CheckoutAsync(Cart cart, CancellationToken ct)
    {
        if (await _features.IsEnabledAsync("NewPricingEngine", ct))
            return await _newPricingEngine.CheckoutAsync(cart, ct);
        return await _legacyPricingEngine.CheckoutAsync(cart, ct);
    }
}
```

## Checklist

- [ ] Configuration is bound to strongly-typed options classes, not read via raw IConfiguration string keys in business logic.
- [ ] Required configuration is validated at startup with ValidateOnStart, failing fast rather than at first use.
- [ ] Secrets are never stored in plain appsettings.json, only in the designated secret store.
- [ ] Risky or gradually-rolled-out features are wrapped in a feature flag checked at the point of use.
- [ ] Flags support the targeting granularity actually needed (global, percentage, per-tenant).
- [ ] Fully rolled-out flags and their old code paths are removed rather than accumulating indefinitely.

## Anti-patterns

- **Raw IConfiguration everywhere** - Reading configuration.GetValue<string>("Email:SenderAddress") scattered through business logic instead of one bound options class.
- **Secrets in appsettings.json** - Committing connection strings or API keys into source-controlled configuration files instead of a secret store.
- **Global-only flags** - Only supporting a single on/off flag with no targeting, forcing all-or-nothing rollouts for risky changes.
- **Flags that never get removed** - Leaving fully-rolled-out feature flags in code indefinitely, accumulating dead branches and testing burden.
- **Silent misconfiguration** - Letting a missing required configuration value fail deep inside business logic at runtime instead of at startup.

## Verification

- Starting the app with a missing required configuration value fails immediately at startup with a clear error.
- A feature flag can be toggled off in a lower environment and the old code path is confirmed to activate.
- A secret-scanning check confirms no credentials exist in appsettings.json or committed configuration files.
- A periodic review confirms no feature flag has remained fully-rolled-out and unused for more than an agreed grace period.

## References

- skills/80-security/secrets-and-key-management/SKILL.md
- Microsoft Learn — Options pattern in ASP.NET Core.
- Microsoft.FeatureManagement documentation.
