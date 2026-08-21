---
name: incident-response-and-runbooks
description: Use when an on-call engineer needs a repeatable process for detecting, triaging, and resolving a production incident, backed by written runbooks for known failure modes.
category: devops
tags: [incident-response, runbooks, on-call]
maturity: stable
updated: 2026-08-21
---

## Purpose

Without a defined process, incidents are handled inconsistently — some resolved quickly by someone who happens to know the system, others dragging on because no one knows where to start. This skill establishes a repeatable incident response process (detect, triage, mitigate, resolve, review) and a runbook format for documenting known failure modes so any on-call engineer can act effectively.

It treats the post-incident review as equally important as the resolution itself, since recurring incidents without a blameless review process indicate a broken feedback loop.

## When to use / When NOT to use

**Use this skill when:**

- You are setting up or improving an on-call rotation and incident response process.
- A recent incident took longer to resolve than it should have because no runbook existed.
- You need to write a runbook for a known, previously-diagnosed failure mode.

**Do NOT use this skill when:**

- The issue is a routine, already-triaged bug fix with no active production impact — handle it through the normal engineering workflow instead.
- You're investigating a security breach specifically — see skills/80-security/security-incident-response/SKILL.md for that specialized process.

## Prerequisites

- skills/60-devops/observability/SKILL.md for the signals that trigger and inform incident detection.
- A defined on-call rotation and paging tool already in place.

## Workflow

1. **Detect via alerting, not customer reports** - Alerts fire from SLO burn rate or key health metrics before customers notice, per skills/60-devops/observability/SKILL.md.
2. **Declare the incident and assign an incident commander** - One clear owner coordinates the response; others investigate and execute under their direction.
3. **Triage severity and communicate status** - Classify impact (SEV1-3), and post regular status updates to a status page or stakeholder channel.
4. **Mitigate before root-causing** - Stop the bleeding first (rollback, feature-flag kill switch, scale up) even before fully understanding the root cause.
5. **Follow the relevant runbook if one exists** - A written runbook for a known failure mode gives step-by-step mitigation instructions, reducing time-to-mitigate.
6. **Resolve and confirm recovery** - Verify metrics have returned to normal and the mitigation is stable before declaring the incident resolved.
7. **Hold a blameless post-incident review** - Document a timeline, contributing factors, and follow-up action items, focusing on systemic causes, not individual blame.
8. **Write or update a runbook from what was learned** - Every incident without a prior runbook should produce one, or update an existing one, for next time.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| An alert fires for a known, previously-diagnosed failure mode | Follow its existing runbook directly rather than re-diagnosing from scratch. |
| An alert fires for a novel, undiagnosed issue | Declare an incident, assign a commander, and investigate live, documenting findings for a future runbook. |
| The fix requires understanding root cause before it's safe to mitigate | Still look for a safe stop-gap (traffic shed, circuit breaker, flag disable) while root-causing continues in parallel. |
| An incident recurs for the second time in a similar way | Treat this as a signal the post-incident action items from the first occurrence weren't actually completed or were ineffective. |
| A postmortem reveals an individual's mistake as a contributing factor | Focus on the process/system gap that allowed the mistake to cause impact, not on blaming the individual. |

## Reference implementation

A runbook entry for a known, previously-diagnosed failure mode:

```markdown
## Runbook: Order API returning 503s under high checkout volume

**Symptoms:** OrderApiFastBurn alert fires; 5xx rate on /checkout exceeds 2%.

**Likely cause:** Downstream payment provider latency spike causing thread-pool exhaustion.

**Mitigation steps:**
1. Check the payment provider status page and the `PaymentGatewayLatency` dashboard.
2. If provider latency is elevated, enable the `PaymentProviderCircuitBreaker` feature flag
   to fail fast and show a 'try again shortly' message instead of hanging requests.
3. Scale the order-api Deployment replicas from 3 to 6 to absorb queued retries.
4. Monitor error rate for 10 minutes; if it doesn't recover, escalate to the payments on-call.

**Resolution:** Once payment provider latency normalizes, disable the circuit breaker flag
and scale replicas back down.
```

- The runbook gives concrete, executable steps (flag names, dashboard names, exact scaling numbers), not vague advice like 'investigate payments'.
- It's written from a prior real incident, keeping it grounded in what actually happened rather than speculation.

### A blameless post-incident review template excerpt (Markdown)

Focused on timeline and systemic factors, not individual blame:

```markdown
## Incident Review: 2026-01-14 Checkout Outage

**Impact:** 18 minutes of elevated 5xx errors on checkout, ~4% of attempted orders failed.

**Timeline:** 14:02 alert fired -> 14:05 incident declared -> 14:11 mitigation applied -> 14:20 resolved.

**Contributing factors:** No circuit breaker existed for the payment provider dependency;
thread-pool exhaustion cascaded from one slow dependency to the whole checkout path.

**Action items:** Add a circuit breaker (owner: X, due: Y); create this runbook (done).
```

## Checklist

- [ ] Incidents are detected via automated alerting tied to SLOs, not primarily via customer reports.
- [ ] Every declared incident has a clear incident commander and severity classification.
- [ ] Mitigation is attempted before full root-cause analysis, prioritizing stopping user impact quickly.
- [ ] A runbook exists (or is created) for every recurring or previously-diagnosed failure mode.
- [ ] A blameless post-incident review happens after every significant incident, with concrete action items.
- [ ] Post-incident action items are tracked to completion, not left open indefinitely.

## Anti-patterns

- **Customer-reported detection** - Learning about an outage from customer support tickets before any internal alert fired, indicating a monitoring gap.
- **No incident commander** - Multiple engineers investigating in parallel with no clear coordination, duplicating effort or missing critical steps.
- **Root-cause-first response** - Refusing to apply any mitigation until the root cause is fully understood, prolonging user-facing impact unnecessarily.
- **Tribal-knowledge-only troubleshooting** - Only one specific engineer knows how to resolve a recurring issue, with no runbook capturing that knowledge.
- **Blame-focused postmortems** - Post-incident reviews that focus on which individual made a mistake instead of what systemic gap allowed it to cause impact.

## Verification

- A sample of recent incidents shows detection time close to alert-fire time, not customer-report time.
- Every SEV1/SEV2 incident in the last quarter has a completed, blameless post-incident review document.
- A runbook exists for each of the top recurring alert types, verified against the alert catalog.
- Action items from past reviews are tracked and show a completion rate, not an ever-growing backlog.

## References

- skills/60-devops/observability/SKILL.md
- skills/80-security/security-incident-response/SKILL.md
- Google SRE Book — Incident Response and Postmortems.
- templates/runbook.template.md
