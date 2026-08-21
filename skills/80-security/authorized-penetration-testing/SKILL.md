---
name: authorized-penetration-testing
description: Use when planning or scoping a penetration test to ensure explicit written authorization, defined scope, and safe engagement rules are in place before any testing begins.
category: security
tags: [penetration-testing, authorization, scoping]
maturity: stable
updated: 2026-08-21
---

## Purpose

Penetration testing without explicit authorization is illegal and unethical, regardless of intent. This skill covers the governance process for scoping, authorizing, and safely conducting a penetration test — rules of engagement, scope definition, and responsible disclosure of findings — rather than any specific attack technique.

This skill deliberately does not include exploit code or step-by-step attack instructions; it focuses entirely on the authorization, scoping, and process controls that make testing legal, safe, and useful.

## When to use / When NOT to use

**Use this skill when:**

- You are planning a penetration test engagement (internal team or external vendor) against a system you own or are explicitly authorized to test.
- You need to define rules of engagement, scope boundaries, and success criteria before testing begins.
- You've received a penetration test report and need a process for triaging and remediating findings.

**Do NOT use this skill when:**

- You do not have explicit, written authorization from the system owner to test it — do not proceed under any circumstances; unauthorized testing is illegal.
- You want general defensive coding guidance instead — see skills/80-security/secure-coding-owasp-top-10/SKILL.md.

## Prerequisites

- Written, signed authorization from the system owner covering scope, dates, and methods.
- skills/80-security/threat-modeling-stride/SKILL.md output, useful for prioritizing what to test.

## Workflow

1. **Obtain explicit written authorization before any testing** - A signed rules-of-engagement document from the system owner is a prerequisite, not a formality — never test without it.
2. **Define scope precisely** - List exactly which systems, IP ranges, environments, and time windows are in scope, and explicitly what is out of scope.
3. **Agree on rules of engagement** - Define permitted techniques, prohibited actions (e.g. no destructive testing against production data), and an emergency stop/contact procedure.
4. **Use a non-production environment where possible** - Prefer testing a staging/pre-production replica over live production to avoid customer impact, unless production testing is specifically required and authorized.
5. **Maintain a communication channel during the engagement** - Establish a point of contact on the defending side who can be reached if testing causes unexpected impact.
6. **Document findings with reproducible evidence, not raw exploit payloads** - Reports describe the vulnerability class, impact, and remediation guidance without including a ready-to-run weaponized exploit.
7. **Follow responsible disclosure and remediation timelines** - Share findings only with authorized stakeholders, and track remediation with agreed timeframes by severity.
8. **Conduct a retest after remediation** - Verify fixes actually close the reported gap before considering a finding resolved.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A test target is not explicitly listed in the signed scope document | Do not test it, even if it appears related; get an explicit scope amendment first. |
| Testing is more convenient against production than staging | Prefer staging/pre-production unless the engagement specifically authorizes production testing with appropriate safeguards. |
| A test action risks being destructive (e.g. deleting data) | Confirm explicit authorization for that specific action exists in the rules of engagement before proceeding, or avoid it. |
| A critical vulnerability is discovered mid-engagement | Report it immediately through the agreed emergency contact channel rather than waiting for the final report. |
| A finding needs to be documented in the report | Describe the vulnerability class, evidence, and business impact without including a fully weaponized, ready-to-run exploit script. |

## Reference implementation

A rules-of-engagement excerpt establishing authorization boundaries:

```markdown
## Rules of Engagement: Q3 External Web Application Assessment

**Authorized by:** VP Engineering, [Company] (signed 2026-07-01)
**Testing window:** 2026-07-15 to 2026-07-26, business hours only

**In scope:**
- staging.example.com (full application, all endpoints)
- Authenticated testing using provided non-production test accounts

**Out of scope:**
- Production environment (example.com) - explicitly excluded
- Third-party payment processor endpoints
- Denial-of-service style testing (volumetric load testing excluded)

**Emergency contact:** security-oncall@example.com, +1-555-0100 (24/7 during window)

**Reporting:** Findings shared only via the encrypted client portal; no findings in email.
```

- Explicit exclusions (production, third-party endpoints, DoS-style testing) prevent scope creep and accidental unauthorized activity.
- An emergency contact channel ensures any unexpected impact can be addressed immediately during the engagement window.

### A findings triage and remediation tracking table (Markdown)

Tracking authorized-test findings through to verified remediation:

```markdown
| Finding                          | Severity | Owner        | Remediation Due | Status       |
|-----------------------------------|----------|--------------|-------------------|-------------|
| Missing rate limiting on login     | Medium   | Platform Team | 2026-08-15        | In Progress |
| Verbose error messages in staging   | Low      | Web Team      | 2026-09-01        | Open        |
| Session cookie missing Secure flag  | High     | Platform Team | 2026-07-30        | Remediated  |
```

## Checklist

- [ ] Written, signed authorization from the system owner exists before any testing begins.
- [ ] Scope is precisely defined, including explicit exclusions, and testing never exceeds it.
- [ ] Rules of engagement define permitted techniques, prohibited actions, and an emergency contact.
- [ ] Testing prefers a non-production environment unless production is specifically authorized.
- [ ] Findings are documented with reproducible evidence and impact, not weaponized exploit scripts.
- [ ] A retest is conducted after remediation to confirm each finding is actually resolved.

## Anti-patterns

- **Testing without written authorization** - Conducting any penetration testing activity without an explicit, signed authorization from the system owner — this is illegal regardless of intent.
- **Scope creep during testing** - Testing systems or techniques not explicitly listed in the agreed scope document, even if they seem related.
- **No emergency contact procedure** - Running an engagement with no way to reach the defending team if testing causes unexpected production impact.
- **Weaponized exploits in reports** - Including a fully working, ready-to-run exploit script in a findings report instead of a description sufficient for remediation.
- **Skipping retest** - Marking a finding as resolved based on a fix being deployed without actually verifying the vulnerability is closed.

## Verification

- A signed rules-of-engagement document exists and is referenced before the testing window opens.
- A post-engagement review confirms no testing activity occurred outside the agreed scope or window.
- Every Critical/High finding has a documented remediation date and a verified retest result.
- The final report is confirmed shared only through the agreed secure channel with authorized recipients.

## References

- skills/80-security/threat-modeling-stride/SKILL.md
- skills/80-security/security-incident-response/SKILL.md
- PTES (Penetration Testing Execution Standard) - process guidance.
