---
name: dotnet-solution-bootstrap
description: Use when starting a new .NET 8 backend service and you need a consistent solution layout, project references, and baseline tooling before writing feature code.
category: backend
tags: [dotnet, solution-structure, bootstrap]
maturity: stable
updated: 2026-08-21
---

## Purpose

Inconsistent solution structures across services make it harder for engineers to move between projects and for tooling (CI, analyzers, architecture tests) to apply uniformly. This skill defines a standard .NET 8 solution layout aligned with Clean/Onion Architecture, plus the baseline tooling (analyzers, EditorConfig, central package management) every new service should start with.

Getting this right at bootstrap time avoids expensive structural rework once a service has significant business logic already in place.

## When to use / When NOT to use

**Use this skill when:**

- You are starting a brand-new .NET 8 backend service from scratch.
- An existing service's structure has drifted and needs to be realigned with the team standard.
- You are setting up shared tooling (analyzers, formatting) for a new solution.

**Do NOT use this skill when:**

- You are adding a feature to an already-bootstrapped, well-structured solution — just follow its existing conventions.
- The project is a small throwaway script or prototype with no expectation of long-term maintenance.

## Prerequisites

- .NET 8 SDK installed.
- skills/20-architecture/clean-and-onion-architecture/SKILL.md understood, since the layout implements it.
- Team agreement on shared analyzer/style rules if this is a multi-service organization.

## Workflow

1. **Create the solution and layered projects** - dotnet new sln, then Domain, Application, Infrastructure, and Api class library/web projects.
2. **Set project references per the dependency rule** - Application -> Domain; Infrastructure -> Application, Domain; Api -> Application, Infrastructure.
3. **Add central package management** - Use Directory.Packages.props to pin package versions once across the whole solution.
4. **Add a Directory.Build.props for shared settings** - Centralize TargetFramework, Nullable, ImplicitUsings, and analyzer settings across all projects.
5. **Configure nullable reference types and analyzers** - Enable <Nullable>enable</Nullable> and treat key analyzer warnings as errors from day one, not retrofitted later.
6. **Set up the test project structure** - One test project per layer (Domain.Tests, Application.Tests) plus an Api.IntegrationTests project.
7. **Add baseline CI** - Wire dotnet build, dotnet test, and dotnet format --verify-no-changes into CI immediately.
8. **Commit a working 'hello world' vertical slice** - Prove the layering works end-to-end with one trivial endpoint before building real features.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Solution will have many similar services (a platform) | Extract Directory.Build.props/Directory.Packages.props conventions into a shared template repo. |
| Team is small and domain is simple | Still use the layered structure, but keep the Application layer thin rather than skipping layering entirely. |
| Service needs both a public API and background workers | Add a separate Worker project referencing Application/Infrastructure, rather than cramming worker code into the Api project. |
| Analyzer warnings are noisy on day one | Enable them as warnings first, fix or explicitly suppress with justification, then escalate to errors — do not disable them permanently. |
| Package versions drift across projects | Centralize via Directory.Packages.props immediately rather than pinning per-project. |

## Reference implementation

Standard .NET 8 solution layout produced by the bootstrap workflow:

```text
OrderPlatform.sln
Directory.Build.props
Directory.Packages.props
.editorconfig
src/
  OrderPlatform.Domain/            (no project references)
  OrderPlatform.Application/        -> Domain
  OrderPlatform.Infrastructure/     -> Application, Domain
  OrderPlatform.Api/                -> Application, Infrastructure (composition root)
  OrderPlatform.Worker/             -> Application, Infrastructure
tests/
  OrderPlatform.Domain.Tests/
  OrderPlatform.Application.Tests/
  OrderPlatform.Api.IntegrationTests/

# Bootstrap commands
dotnet new sln -n OrderPlatform
dotnet new classlib -n OrderPlatform.Domain -o src/OrderPlatform.Domain
dotnet new classlib -n OrderPlatform.Application -o src/OrderPlatform.Application
dotnet new classlib -n OrderPlatform.Infrastructure -o src/OrderPlatform.Infrastructure
dotnet new webapi -n OrderPlatform.Api -o src/OrderPlatform.Api
dotnet sln add src/**/*.csproj tests/**/*.csproj
```

- Add project references immediately after creation so the dependency rule is enforced from commit one.
- Keep the Api project's Program.cs as the only place concrete infrastructure types are registered (the composition root).

### Directory.Build.props baseline settings

Shared settings applied to every project in the solution:

```xml
<Project>
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <AnalysisLevel>latest</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
  </PropertyGroup>
</Project>
```

## Checklist

- [ ] Projects are split by layer (Domain, Application, Infrastructure, Api) with correct references.
- [ ] Domain project has zero references to Infrastructure or any framework package.
- [ ] Directory.Build.props and Directory.Packages.props centralize shared settings and versions.
- [ ] Nullable reference types are enabled solution-wide from the start.
- [ ] A test project exists per layer, plus an integration test project for the Api.
- [ ] CI runs build, test, and format-verification on every push from day one.
- [ ] A trivial end-to-end vertical slice proves the layering works before real features are built.

## Anti-patterns

- **Single flat project** - Putting controllers, business logic, and EF Core entities all in one project, making later layering a painful retrofit.
- **Per-project package versions** - Letting each project pin its own package versions, causing version drift and conflicting transitive dependencies.
- **Deferred nullable enablement** - Starting with Nullable disabled 'to move fast' and enabling it later, when it requires touching every file.
- **No tests from day one** - Deferring test project setup until 'there's something worth testing', losing the habit of testing as you go.
- **CI added as an afterthought** - Writing weeks of code before wiring up any CI pipeline, missing early regressions.

## Verification

- `dotnet build` succeeds with zero warnings on a fresh clone.
- An architecture test (or manual check) confirms Domain has no outward project references.
- `dotnet test` runs at least one passing test per layer, including the integration test project.
- CI is green on the initial bootstrap commit before any feature work begins.

## References

- skills/20-architecture/clean-and-onion-architecture/SKILL.md
- Microsoft Learn — .NET solution and project structure guidance.
- skills/60-devops/ci-cd-pipelines/SKILL.md
