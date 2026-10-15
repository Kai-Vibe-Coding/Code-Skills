---
name: dependency-and-supply-chain-security
description: Use when adding, updating, or auditing third-party dependencies to reduce the risk of known vulnerabilities or malicious packages entering the software supply chain.
category: security
tags: [supply-chain, dependencies, sbom]
maturity: stable
updated: 2026-08-21
---

## Purpose

Modern applications depend on hundreds of transitive third-party packages, any of which can introduce a known vulnerability or, in rarer cases, malicious code. This skill covers scanning dependencies for known vulnerabilities, pinning versions, generating a software bill of materials (SBOM), and evaluating new dependencies before adoption.

It applies across the entire dependency lifecycle: initial adoption, ongoing monitoring, and incident response when a vulnerability is disclosed.

## When to use / When NOT to use

**Use this skill when:**

- You are considering adding a new third-party package to the project.
- You are setting up or maintaining CI to continuously scan for vulnerable dependencies.
- A CVE is disclosed in a dependency your project uses and you need to assess and remediate impact.

**Do NOT use this skill when:**

- You are evaluating your own first-party code for vulnerabilities — see skills/80-security/secure-coding-owasp-top-10/SKILL.md instead.
- You need the broader CI security pipeline context — see skills/80-security/sast-dast-and-security-in-ci/SKILL.md.

## Prerequisites

- A dependency manifest and lockfile for the ecosystem in use (e.g. `.csproj`/`packages.lock.json`, `package.json`/`package-lock.json`).
- skills/60-devops/ci-cd-pipelines/SKILL.md for where scanning steps are integrated.

## Workflow

1. **Evaluate a new dependency before adoption** - Check its maintenance activity, download counts, license compatibility, and any known vulnerability history before adding it.
2. **Pin dependency versions with a lockfile** - Commit the lockfile so builds are reproducible and a compromised registry can't silently substitute a different version.
3. **Run automated vulnerability scanning in CI** - Use tools like `dotnet list package --vulnerable`, `npm audit`, or GitHub Dependabot/CodeQL to scan on every build.
4. **Generate and retain a software bill of materials (SBOM)** - Produce an SBOM (e.g. CycloneDX or SPDX format) per release so the full dependency tree is auditable later.
5. **Establish a remediation SLA by severity** - Define target timeframes for patching critical/high vulnerabilities (e.g. critical within days, medium within weeks).
6. **Prefer well-maintained, minimal-dependency packages** - Fewer, more actively maintained dependencies reduce both attack surface and the ongoing patching burden.
7. **Verify package integrity where supported** - Use package signing/checksum verification features of the ecosystem (e.g. NuGet package signing, npm provenance) where available.
8. **Automate dependency update PRs with review** - Use Dependabot or Renovate to open update PRs automatically, reviewed and merged on a regular cadence rather than ad hoc.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A new package is being considered for a core code path | Prefer an actively maintained package with a healthy release history over an abandoned or single-maintainer package with no recent updates. |
| A CVE is disclosed for a transitive dependency | Check the remediation SLA by severity; patch immediately for critical/high, schedule for lower severities. |
| A dependency has no patched version available yet | Assess whether the vulnerable code path is actually reachable in your usage; if so, consider a temporary mitigation or pinning away from the affected version. |
| Choosing between two packages with similar functionality | All else equal, prefer the one with fewer transitive dependencies and a clearer security disclosure process. |
| A build needs to be audited after the fact | Use the retained SBOM for that release to determine exactly what was included, without needing to reconstruct the dependency tree. |

## Reference implementation

A CI job scanning for vulnerable NuGet and npm dependencies on every push:

```yaml
name: dependency-scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'
      - name: Check for vulnerable NuGet packages
        run: dotnet list package --vulnerable --include-transitive | tee vuln-report.txt
      - name: Fail if any vulnerabilities found
        run: |
          if grep -q "has the following vulnerable packages" vuln-report.txt; then
            echo "Vulnerable packages detected"; exit 1
          fi
```

- `--include-transitive` ensures indirect dependencies are scanned, not just top-level references.
- The same pattern applies to `npm audit --audit-level=high` for a Node.js/TypeScript frontend.

### Generating a CycloneDX SBOM as part of the release pipeline (YAML)

Producing an auditable record of exactly what shipped in a release:

```yaml
- name: Generate SBOM
  run: |
    dotnet tool install --global CycloneDX
    dotnet CycloneDX ./src/OrderService.csproj -o ./sbom -j
- name: Upload SBOM artifact
  uses: actions/upload-artifact@v4
  with:
    name: sbom
    path: ./sbom/bom.json
```

## Checklist

- [ ] A lockfile is committed and enforced so dependency versions are reproducible across builds.
- [ ] CI runs an automated vulnerability scan on every push/PR against direct and transitive dependencies.
- [ ] An SBOM is generated and retained for every release.
- [ ] A remediation SLA by severity is defined and followed for disclosed vulnerabilities.
- [ ] New dependencies are evaluated for maintenance activity and necessity before adoption.
- [ ] Automated dependency update PRs (Dependabot/Renovate) are reviewed and merged on a regular cadence.

## Anti-patterns

- **No lockfile committed** - Allowing dependency versions to float on every build, risking a compromised registry silently substituting a malicious version.
- **Manual, occasional vulnerability checks** - Only checking for vulnerable dependencies sporadically instead of running automated scans on every build.
- **Ignoring transitive dependencies** - Auditing only directly referenced packages while ignoring the much larger transitive dependency tree.
- **No remediation SLA** - Leaving disclosed critical vulnerabilities unpatched indefinitely with no defined timeframe for action.
- **Adding dependencies without evaluation** - Pulling in a new package for a trivial utility function without checking its maintenance status or necessity.

## Verification

- A CI run confirms the vulnerability scan step fails the build when a known-vulnerable package is introduced.
- An SBOM artifact is present and retrievable for the most recent release.
- A sample disclosed CVE affecting a used dependency was remediated within the defined SLA window.
- Dependency update PRs show a consistent cadence of review and merge, not a large accumulated backlog.

## References

- skills/60-devops/ci-cd-pipelines/SKILL.md
- skills/80-security/sast-dast-and-security-in-ci/SKILL.md
- OWASP Dependency-Check and CycloneDX documentation.
