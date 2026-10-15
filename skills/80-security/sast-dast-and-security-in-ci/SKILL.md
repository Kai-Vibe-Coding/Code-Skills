---
name: sast-dast-and-security-in-ci
description: Use when integrating automated security scanning into the CI/CD pipeline so vulnerabilities are caught before merge or release rather than after deployment.
category: security
tags: [sast, dast, ci-cd, shift-left]
maturity: stable
updated: 2026-08-21
---

## Purpose

Manual, periodic security reviews miss issues introduced between reviews. This skill covers embedding Static Application Security Testing (SAST), Dynamic Application Security Testing (DAST), and dependency scanning directly into the CI/CD pipeline so every change is automatically checked, shifting security feedback as early as possible.

It is about pipeline integration and triage process, not about performing manual penetration testing — see skills/80-security/authorized-penetration-testing/SKILL.md for that.

## When to use / When NOT to use

**Use this skill when:**

- You are setting up or extending CI/CD for a project and want automated security gates.
- You need to decide which class of scanning (SAST vs DAST vs dependency) applies to a given risk.
- A security scanning tool is producing findings and you need a triage process for them.

**Do NOT use this skill when:**

- You need dependency-specific scanning details — see skills/80-security/dependency-and-supply-chain-security/SKILL.md.
- You need manual, authorized exploitation testing beyond what automated tools find — see skills/80-security/authorized-penetration-testing/SKILL.md.

## Prerequisites

- skills/60-devops/ci-cd-pipelines/SKILL.md for the pipeline structure scanning steps are added to.
- skills/80-security/dependency-and-supply-chain-security/SKILL.md for dependency scanning specifics.

## Workflow

1. **Add SAST scanning on every pull request** - Run a static analyzer (e.g. CodeQL, SonarQube) against the codebase on every PR to catch insecure patterns before merge.
2. **Add DAST scanning against a running test environment** - Run a dynamic scanner (e.g. OWASP ZAP) against a deployed staging environment to catch runtime-only issues like misconfigured headers.
3. **Gate merges on critical/high findings, not all findings** - Block merge for critical/high severity new findings; route lower severity findings to a tracked backlog to avoid alert fatigue.
4. **Baseline existing findings before enabling hard gates** - When first introducing a scanner to an existing codebase, baseline current findings so the gate only blocks *new* issues, avoiding an unworkable wall of pre-existing debt.
5. **Triage findings promptly with a defined SLA** - Assign an owner and remediation timeframe by severity, mirroring the approach in skills/80-security/dependency-and-supply-chain-security/SKILL.md.
6. **Keep scan configuration and suppressions in version control** - Any suppressed finding is documented with a reason and reviewed periodically, not silently ignored forever.
7. **Run scans early and often, not just before release** - Integrate into the standard PR pipeline so feedback arrives in minutes, not right before a release cutoff.
8. **Combine automated scanning with periodic manual review** - Automated tools catch known patterns; complement with periodic manual code review and, where warranted, authorized penetration testing.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Choosing between SAST and DAST for a given check | Use SAST for code-level issues detectable from source (injection patterns, hardcoded secrets); use DAST for runtime-only issues (missing security headers, live misconfigurations). |
| A new SAST finding is Critical severity on a PR | Block the merge until it's fixed or explicitly triaged as a false positive with documented justification. |
| Introducing a scanner to a legacy codebase with many existing findings | Baseline current findings first so the gate only enforces against new issues going forward. |
| A finding is a false positive | Suppress it with an inline, reviewed justification comment, not a blanket rule disabling that entire check category. |
| Choosing where DAST scans should target | Run against a representative staging/test environment, never against production without explicit authorization and safeguards. |

## Reference implementation

A CI pipeline stage running CodeQL SAST analysis on every pull request:

```yaml
name: codeql-analysis
on:
  pull_request:
  push:
    branches: [main]
jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: csharp
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3
        with:
          category: sast
```

- Findings surface as code scanning alerts on the PR, giving reviewers visibility before merge.
- `security-events: write` permission is scoped narrowly to this job, following least privilege for CI credentials.

### A DAST scan stage against a staging environment (YAML)

Running OWASP ZAP baseline scan post-deployment to staging:

```yaml
- name: DAST baseline scan
  uses: zaproxy/action-baseline@v0.12.0
  with:
    target: 'https://staging.example.internal'
    fail_action: true
    cmd_options: '-a'
```

## Checklist

- [ ] SAST scanning runs automatically on every pull request against the target branch.
- [ ] DAST scanning runs against a representative staging environment, never unauthorized against production.
- [ ] Merges are gated on new critical/high findings, with lower severities tracked in a backlog.
- [ ] Existing findings were baselined before enabling hard gates on a legacy codebase.
- [ ] Suppressions are documented in version control with a reviewed justification, not silently disabled.
- [ ] Findings are triaged with an owner and remediation SLA by severity.

## Anti-patterns

- **Scanning only before release** - Running security scans only right before a release cutoff instead of on every pull request, surfacing issues too late to fix cheaply.
- **Blocking on every finding regardless of severity** - Gating merges on any finding at all, including informational/low severity ones, causing alert fatigue and pressure to disable the gate entirely.
- **Silent suppressions** - Disabling a scanner rule or suppressing a finding without a documented, reviewed justification.
- **DAST against production without authorization** - Running dynamic scans against a live production environment without explicit authorization and safeguards, risking outages or data corruption.
- **No baseline on legacy codebases** - Introducing a hard gate to an existing codebase with hundreds of pre-existing findings, making the gate immediately unworkable and likely to be bypassed.

## Verification

- A CI run shows the SAST job executes and reports results on a sample pull request.
- A test PR introducing a known-bad pattern (e.g. hardcoded credential) is flagged and blocks merge.
- A DAST scan report exists for the most recent staging deployment.
- The suppression list in version control shows a documented reason for every currently suppressed finding.

## References

- skills/60-devops/ci-cd-pipelines/SKILL.md
- skills/80-security/dependency-and-supply-chain-security/SKILL.md
- OWASP DevSecOps guideline documentation.
