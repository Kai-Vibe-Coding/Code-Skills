---
name: ci-cd-pipelines
description: Use when designing or reviewing a build/test/deploy pipeline to ensure fast feedback, reliable gates, and safe automated deployment.
category: devops
tags: [ci-cd, pipelines, automation]
maturity: stable
updated: 2026-08-21
---

## Purpose

A slow or unreliable CI/CD pipeline erodes trust in automation and encourages engineers to skip or ignore its results. This skill covers structuring pipelines into fast, parallelized stages with clear quality gates (build, test, scan, deploy), and progressive deployment automation that reduces the risk of any single change.

It emphasizes making the pipeline itself a first-class piece of engineering, versioned and reviewed like any other code, not an afterthought bolted on once a project already exists.

## When to use / When NOT to use

**Use this skill when:**

- You are setting up CI/CD for a new service or repository.
- An existing pipeline is slow, flaky, or missing key quality gates (tests, security scans).
- You are moving from manual deployment to automated, gated deployment.

**Do NOT use this skill when:**

- The project is an experimental prototype not headed to production — a full pipeline may be premature.
- You're debugging one specific flaky test rather than the pipeline's overall structure — fix that test directly first.

## Prerequisites

- skills/70-quality/test-strategy/SKILL.md for what tests should run at which pipeline stage.
- skills/80-security/sast-dast-and-security-in-ci/SKILL.md for the security scanning gates to include.
- skills/60-devops/release-strategies/SKILL.md for how the pipeline's deploy stage should behave.

## Workflow

1. **Trigger CI on every push and pull request** - Fast feedback on every change, not just on merge to main.
2. **Run fast checks first, in parallel where possible** - Lint, unit tests, and build run in parallel jobs before slower integration/E2E tests.
3. **Fail fast on the cheapest checks** - Static analysis and unit tests should fail the pipeline in seconds/minutes, before expensive integration tests even start.
4. **Cache dependencies between runs** - Cache package manager downloads (NuGet, npm) keyed by lockfile hash to avoid re-downloading on every run.
5. **Build once, deploy the same artifact everywhere** - Produce one versioned build artifact/image and promote it through environments, never rebuilding per environment.
6. **Gate deployment on required checks** - Merges to main and deploys are blocked unless build, tests, and security scans all pass.
7. **Automate progressive deployment** - Deploy to staging automatically, then to production via a controlled strategy (canary/blue-green) per skills/60-devops/release-strategies/SKILL.md.
8. **Version and review pipeline configuration like code** - Pipeline YAML changes go through the same PR review as application code.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A test suite is slow and blocking fast feedback | Split into fast unit tests (run on every push) and slower integration/E2E tests (run on PR or a separate stage), not one monolithic suite. |
| Different environments need different configuration | Inject environment-specific config at deploy time into one built artifact, rather than rebuilding per environment. |
| A security scan finding blocks a release | Fail the pipeline for critical/high findings per skills/80-security/sast-dast-and-security-in-ci/SKILL.md policy, don't silently ignore it. |
| Deployment to production needs to be safer | Add a canary or blue-green stage with automated rollback triggers rather than a single big-bang deploy. |
| Pipeline runs are flaky and inconsistent | Treat flaky tests/steps as a bug to fix immediately, not something to retry indefinitely and ignore. |

## Reference implementation

A staged GitHub Actions pipeline with parallel fast checks and a gated deploy:

```yaml
name: CI
on: [push, pull_request]
jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: '8.0.x' }
      - run: dotnet format --verify-no-changes
      - run: dotnet test --logger trx --results-directory TestResults

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: trivy fs --exit-code 1 --severity CRITICAL,HIGH .

  deploy-staging:
    needs: [lint-and-test, security-scan]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/deploy.sh staging ${{ github.sha }}
```

- deploy-staging only runs after both lint-and-test and security-scan succeed, and only on main, keeping the deploy gate explicit.
- The same commit SHA is used as the deploy artifact version, ensuring what's tested is exactly what's deployed.

### Caching dependencies keyed by lockfile hash (YAML)

Avoiding redundant downloads on every pipeline run:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.nuget/packages
    key: nuget-${{ hashFiles('**/packages.lock.json') }}
    restore-keys: nuget-
```

## Checklist

- [ ] CI triggers on every push and pull request, not only on merge to main.
- [ ] Fast checks (lint, unit tests) run before and gate slower integration/E2E tests.
- [ ] Dependencies are cached between runs, keyed by a lockfile hash.
- [ ] One versioned build artifact is promoted through environments rather than rebuilt per environment.
- [ ] Merges and deploys are blocked unless all required checks (build, test, security scan) pass.
- [ ] Pipeline configuration changes go through code review like any other change.

## Anti-patterns

- **Monolithic slow pipeline** - Running every test (unit, integration, E2E) sequentially in one long job, delaying feedback on simple mistakes by tens of minutes.
- **Rebuild per environment** - Building a separate artifact for staging and production instead of promoting one tested artifact, risking untested differences between them.
- **Optional security scans** - Running a SAST/dependency scan but not failing the build on critical findings, making the scan purely informational and easy to ignore.
- **Manual, undocumented deploy steps** - Relying on an engineer running commands from memory to deploy instead of a scripted, versioned pipeline step.
- **Ignoring flaky tests** - Retrying a known-flaky test indefinitely instead of fixing or quarantining it, eroding trust in the whole pipeline's signal.

## Verification

- A trivial one-line change reaches a pass/fail CI result within a target time budget (e.g. under 10 minutes for fast checks).
- The exact artifact deployed to production is confirmed to be the same one that passed staging tests (by version/SHA).
- A critical security finding is confirmed to block the pipeline in a test run.
- Pipeline YAML changes are visible in PR history with the same review requirements as application code.

## References

- skills/70-quality/test-strategy/SKILL.md
- skills/80-security/sast-dast-and-security-in-ci/SKILL.md
- skills/60-devops/release-strategies/SKILL.md
