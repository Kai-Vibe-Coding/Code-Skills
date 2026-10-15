---
name: secrets-and-key-management
description: Use when storing, rotating, or accessing application secrets and cryptographic keys so they never end up hardcoded or exposed in source control.
category: security
tags: [secrets, key-management, vault]
maturity: stable
updated: 2026-08-21
---

## Purpose

Hardcoded secrets in source control are one of the most common and easily preventable causes of breaches. This skill covers using a dedicated secret manager, rotating credentials, and structuring code so secrets are injected at runtime rather than embedded in code or config files committed to version control.

It applies to database connection strings, API keys, signing keys, and encryption keys alike.

## When to use / When NOT to use

**Use this skill when:**

- You are adding a new external integration that requires an API key or credential.
- You are configuring database connection strings, signing keys, or encryption keys for a service.
- You discover a secret was accidentally committed to source control and need to remediate it.

**Do NOT use this skill when:**

- The value isn't actually sensitive (e.g. a public API base URL) — plain configuration is fine, see skills/30-backend/configuration-and-feature-flags/SKILL.md.
- You need to design the broader authentication flow that consumes these secrets — see skills/80-security/authn-authz-hardening/SKILL.md.

## Prerequisites

- skills/30-backend/configuration-and-feature-flags/SKILL.md for how configuration is layered and consumed by the application.
- Access to a secret manager (Azure Key Vault, AWS Secrets Manager, HashiCorp Vault) provisioned for the environment.

## Workflow

1. **Never commit secrets to source control, ever** - Use `.gitignore` for local secret files and pre-commit/CI secret scanning to catch accidental commits before merge.
2. **Store secrets in a dedicated secret manager** - Use Azure Key Vault, AWS Secrets Manager, or HashiCorp Vault rather than environment variables baked into container images.
3. **Inject secrets at runtime, not build time** - Application containers pull secrets from the secret manager at startup or via a sidecar, never baked into an image layer.
4. **Scope access to secrets narrowly** - Grant each service/identity access only to the specific secrets it needs, using managed identities rather than shared credentials.
5. **Rotate secrets on a schedule and on suspected exposure** - Define a rotation cadence for long-lived credentials, and rotate immediately if exposure is suspected.
6. **Use short-lived, dynamically generated credentials where possible** - Prefer a secret manager's dynamic database credential feature over a single long-lived connection string.
7. **Audit secret access** - Enable access logging on the secret manager so unusual access patterns can be detected and investigated.
8. **Remediate any historical exposure by rotation, not just deletion** - If a secret was ever committed to git history, treat it as compromised and rotate it — removing it from history alone is insufficient.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A new API integration requires an API key | Store it in the secret manager and reference it by name from application configuration; never hardcode it. |
| A secret is discovered committed in git history | Rotate the secret immediately, then clean git history as a secondary step; rotation is the priority, not just history rewriting. |
| A service needs to connect to a database | Prefer a managed identity or dynamically generated short-lived credential over a static connection string where the platform supports it. |
| Local development needs a secret value | Use a local secret store (e.g. `dotnet user-secrets`) or a dev-tier secret manager entry, never a checked-in `.env` file with real values. |
| A CI/CD pipeline needs to deploy using a cloud credential | Use short-lived, workload-identity-federated credentials rather than a long-lived static service principal secret where supported. |

## Reference implementation

Loading a secret from Azure Key Vault at application startup rather than hardcoding it:

```csharp
var builder = WebApplication.CreateBuilder(args);

if (!builder.Environment.IsDevelopment())
{
    var keyVaultUri = new Uri(builder.Configuration["KeyVault:Uri"]!);
    builder.Configuration.AddAzureKeyVault(
        keyVaultUri,
        new DefaultAzureCredential()); // managed identity, no secret stored in code
}

var app = builder.Build();

// Consumed later via standard configuration binding - the connection string itself
// is never present in source control or the container image.
var connectionString = builder.Configuration.GetConnectionString("OrdersDb");
```

- DefaultAzureCredential uses the hosting environment's managed identity, so no client secret is needed at all in production.
- Local development falls back to `dotnet user-secrets` or a dev Key Vault entry, never a real production secret in a local file.

### A CI secret-scanning guard as part of pre-merge checks (YAML)

Catching accidentally committed secrets before they merge:

```yaml
name: secret-scan
on: [pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Scan for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          extra_args: --only-verified
```

## Checklist

- [ ] No secret values are hardcoded in source, config files, or container images checked into version control.
- [ ] Secrets are stored in a dedicated secret manager and injected at runtime.
- [ ] Each service/identity has narrowly scoped access to only the secrets it needs.
- [ ] A rotation cadence exists for long-lived credentials, with immediate rotation on suspected exposure.
- [ ] CI includes automated secret scanning on every pull request.
- [ ] Any historically exposed secret has been rotated, not just removed from the latest commit.

## Anti-patterns

- **Hardcoded connection strings** - Embedding a database connection string or API key directly in source code or `appsettings.json` committed to git.
- **Secrets baked into container images** - Building a Docker image with secrets set as build-time ARGs or COPYed files, leaving them recoverable from image layers.
- **Shared long-lived credentials** - Using the same static API key or database credential across all environments and services indefinitely.
- **Deleting instead of rotating** - Believing a secret is safe after removing it from the latest commit, without rotating the actual credential value.
- **No access auditing** - Storing secrets in a vault but never reviewing access logs to detect anomalous or unauthorized retrieval.

## Verification

- A repository scan (e.g. TruffleHog, gitleaks) confirms no verified secrets exist in the current codebase or history.
- Application startup successfully retrieves required secrets from the secret manager in each environment.
- A rotation of a test secret completes without requiring an application code change or redeploy.
- Access logs for the secret manager show scoped, expected access patterns per service identity.

## References

- skills/30-backend/configuration-and-feature-flags/SKILL.md
- skills/80-security/authn-authz-hardening/SKILL.md
- OWASP Secrets Management Cheat Sheet.
