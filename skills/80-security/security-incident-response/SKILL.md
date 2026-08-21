---
name: security-incident-response
description: Use when responding to a suspected or confirmed security incident to contain impact, preserve evidence, and recover safely with a clear post-incident process.
category: security
tags: [incident-response, security, forensics]
maturity: stable
updated: 2026-08-21
---

## Purpose

A security incident (suspected breach, credential compromise, malware) is a distinct scenario from a routine operational outage: it requires containment and evidence preservation alongside recovery. This skill covers a structured incident response process — detection, containment, eradication, recovery, and post-incident review — building on the operational incident practices in skills/60-devops/incident-response-and-runbooks/SKILL.md with security-specific concerns.

## When to use / When NOT to use

**Use this skill when:**

- You suspect unauthorized access, data exfiltration, credential compromise, or malware in a system.
- A security scanning tool or user report indicates a possible active compromise.
- You need to establish a security incident response plan before an incident occurs.

**Do NOT use this skill when:**

- The event is a routine operational outage with no security dimension — see skills/60-devops/incident-response-and-runbooks/SKILL.md instead.
- You are planning authorized testing rather than responding to a real incident — see skills/80-security/authorized-penetration-testing/SKILL.md.

## Prerequisites

- skills/60-devops/incident-response-and-runbooks/SKILL.md for the baseline incident process this extends.
- A pre-defined security incident response plan with named roles, agreed before any incident occurs.

## Workflow

1. **Detect and triage the suspected incident** - Confirm whether the signal (alert, report) indicates a genuine security incident versus a false positive or benign anomaly.
2. **Declare the incident and assemble the response team** - Name an incident commander and pull in security, engineering, and legal/communications stakeholders as the severity warrants.
3. **Contain the incident without destroying evidence** - Isolate affected systems (e.g. revoke credentials, disable accounts, segment network access) while preserving logs and system state for later analysis.
4. **Preserve evidence before remediation actions** - Snapshot affected systems/logs before patching or rebuilding, so forensic analysis of root cause remains possible.
5. **Eradicate the root cause** - Remove the attacker's access path entirely (patch the vulnerability, rotate all potentially exposed credentials), not just the immediately visible symptom.
6. **Recover systems to normal operation carefully** - Restore from known-clean backups or rebuilt images, verifying integrity before returning to production traffic.
7. **Notify affected parties per legal/regulatory obligation** - Determine notification requirements (e.g. breach notification laws, contractual SLAs) with legal counsel promptly, not as an afterthought.
8. **Conduct a blameless post-incident review** - Document the timeline, root cause, and process gaps, mirroring skills/60-devops/incident-response-and-runbooks/SKILL.md's blameless postmortem approach.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A signal might indicate compromise but isn't confirmed | Triage first — investigate quickly and quietly rather than immediately declaring a full incident, but don't dismiss it either. |
| An affected system needs to be taken offline | Isolate/quarantine it rather than immediately wiping or rebuilding it, preserving evidence for forensic analysis first. |
| Credentials are suspected to be exposed | Rotate them immediately, following skills/80-security/secrets-and-key-management/SKILL.md's rotation guidance, without waiting for full root cause confirmation. |
| Customer data may have been accessed | Involve legal/compliance immediately to determine notification obligations; do not delay based on incomplete technical detail. |
| The root cause is identified but only partially fixed | Do not declare the incident closed until the full access path is eradicated, not just the immediately observed symptom. |

## Reference implementation

A security incident response timeline excerpt showing containment before eradication:

```markdown
## Security Incident #2026-0042: Suspected Credential Compromise

**Severity:** SEV-1 | **Incident Commander:** J. Alvarez

| Time (UTC)  | Action                                                        |
|-------------|----------------------------------------------------------------|
| 14:02        | Alert: anomalous login pattern for service-account `svc-orders` |
| 14:07        | Triaged as likely compromise; incident declared, IC assigned     |
| 14:12        | Snapshot taken of affected host logs and process state (evidence preservation) |
| 14:15        | svc-orders credentials rotated; account access suspended         |
| 14:40        | Root cause confirmed: leaked credential in a public gist          |
| 15:10        | Gist removed; all related secrets rotated; access path closed     |
| 15:30        | Legal notified to assess data-exposure notification obligations   |
```

- Evidence preservation (14:12) happens before credential rotation completes the containment step, so forensic analysis remains possible.
- Legal is looped in as soon as data exposure is plausible, not only after full technical root cause is confirmed.

### A blameless post-incident review outline (Markdown)

Structuring the review to focus on systemic gaps, not individual blame:

```markdown
## Post-Incident Review: #2026-0042

**What happened:** Brief factual timeline summary.
**Root cause:** Credential accidentally published in a public code snippet.
**What went well:** Detection alert fired within minutes of anomalous activity.
**What could improve:** No automated secret-scanning on public gists/pastes was in place.
**Action items:** Add secret-scanning webhook for public gist creation (owner, due date).
```

## Checklist

- [ ] A security incident response plan with named roles exists before any incident occurs.
- [ ] Detection signals are triaged promptly to confirm genuine incidents versus false positives.
- [ ] Containment actions preserve evidence (snapshots/logs) before remediation destroys system state.
- [ ] Root cause eradication closes the full access path, not just the immediately visible symptom.
- [ ] Legal/compliance is engaged promptly to assess notification obligations when data exposure is plausible.
- [ ] A blameless post-incident review documents timeline, root cause, and concrete action items.

## Anti-patterns

- **Wiping systems before evidence preservation** - Rebuilding or patching an affected system immediately without first preserving logs/state, losing the ability to determine root cause.
- **Declaring victory after symptom removal** - Closing an incident after removing the immediately visible symptom without confirming the full access path is eradicated.
- **Delaying legal involvement** - Waiting until full technical root cause is confirmed before looping in legal/compliance on notification obligations, risking missed regulatory deadlines.
- **Blame-focused reviews** - Conducting a post-incident review that focuses on which individual made a mistake rather than what systemic gap allowed the incident.
- **No pre-defined response plan** - Improvising incident response roles and process for the first time during an actual active incident.

## Verification

- A tabletop exercise confirms the response plan's roles and escalation paths are understood by the team.
- A sample incident timeline shows evidence preservation occurred before destructive remediation actions.
- Post-incident review documents exist for prior incidents with concrete, owned action items tracked to completion.
- Notification obligations were assessed and met within applicable regulatory timeframes for any incident involving data exposure.

## References

- skills/60-devops/incident-response-and-runbooks/SKILL.md
- skills/80-security/secrets-and-key-management/SKILL.md
- NIST SP 800-61: Computer Security Incident Handling Guide.
