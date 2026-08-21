---
name: privacy-and-compliance-basics
description: Use when a system handles personal data and you need to apply baseline privacy-by-design and regulatory compliance practices such as data minimization and consent management.
category: security
tags: [privacy, compliance, gdpr, data-protection]
maturity: stable
updated: 2026-08-21
---

## Purpose

Handling personal data carries legal obligations (GDPR, CCPA, and similar regimes) independent of technical security. This skill covers baseline privacy-by-design practices — data minimization, purpose limitation, consent management, and data subject rights — that apply broadly across most regulatory regimes, without attempting to give jurisdiction-specific legal advice.

This is engineering guidance for building compliant systems, not a substitute for legal counsel on specific regulatory obligations.

## When to use / When NOT to use

**Use this skill when:**

- You are designing a system or feature that collects, stores, or processes personal data.
- You need to implement a data subject access, deletion, or export request.
- A design review needs a checklist for privacy-by-design considerations.

**Do NOT use this skill when:**

- You need definitive legal interpretation of a specific regulation for your jurisdiction — consult legal counsel, this skill is engineering guidance only.
- The data being handled is not personal/identifying data at all.

## Prerequisites

- skills/80-security/secrets-and-key-management/SKILL.md and skills/80-security/secure-coding-owasp-top-10/SKILL.md for the security controls protecting personal data at rest and in transit.
- Organizational legal/compliance guidance on which regulatory regimes apply to your users.

## Workflow

1. **Apply data minimization from the start** - Collect only the personal data actually necessary for the feature's purpose, not data that might be useful someday.
2. **Define and document the purpose for each data element** - Personal data collected for one purpose (e.g. shipping) should not be silently repurposed (e.g. marketing) without fresh consent.
3. **Obtain and record explicit consent where required** - Track what a user consented to, when, and for what purpose, with an accessible mechanism to withdraw consent.
4. **Implement data subject rights: access, rectification, deletion, export** - Build supportable mechanisms for a user to view, correct, delete, or export their personal data, not just a manual/ad hoc process.
5. **Encrypt personal data at rest and in transit** - Apply the encryption practices from skills/80-security/secrets-and-key-management/SKILL.md to any personal data store.
6. **Set data retention limits and enforce automated deletion** - Define how long each category of personal data is retained and automate its deletion when the retention period expires.
7. **Maintain a record of processing activities** - Document what personal data is processed, why, where it's stored, and who has access, to support compliance audits.
8. **Assess third-party processors for compliance** - Any vendor that processes personal data on your behalf needs an appropriate data processing agreement and compliance posture.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A new feature wants to collect an optional data field 'just in case' | Don't collect it unless there's a defined current purpose; add it later if a genuine need arises. |
| A user requests deletion of their account data | Execute a supportable deletion workflow that removes/anonymizes personal data across all systems, not just the primary database. |
| Data collected for one purpose is being considered for a new use (e.g. analytics) | Obtain fresh, explicit consent for the new purpose rather than silently repurposing existing consent. |
| A third-party vendor will process user personal data | Confirm a data processing agreement is in place and their compliance posture is assessed before integration. |
| Retention period for a data category is undefined | Default to the minimum retention necessary for the stated purpose and document it explicitly, rather than retaining indefinitely by default. |

## Reference implementation

A data subject deletion request handler that cascades across relevant tables:

```csharp
public async Task<DeletionResult> ExecuteDeletionRequestAsync(Guid userId, CancellationToken ct)
{
    // Anonymize rather than hard-delete records that must be retained for legal/financial
    // reasons (e.g. completed order history), per the documented retention policy.
    await _orderStore.AnonymizeCustomerReferencesAsync(userId, ct);

    // Hard-delete data with no retention obligation.
    await _profileStore.DeleteAsync(userId, ct);
    await _marketingPreferencesStore.DeleteAsync(userId, ct);
    await _sessionStore.RevokeAllForUserAsync(userId, ct);

    await _auditLog.RecordAsync(new DeletionAudit(userId, DateTimeOffset.UtcNow), ct);

    return DeletionResult.Completed;
}
```

- Records with an independent legal retention requirement (e.g. financial records) are anonymized rather than deleted, balancing deletion rights against other obligations.
- An audit record of the deletion itself is kept, supporting compliance verification without retaining the deleted personal data.

### A consent record schema tracking purpose-specific consent (SQL)

Recording what a user consented to, when, and for what specific purpose:

```sql
CREATE TABLE consent_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    purpose VARCHAR(100) NOT NULL, -- e.g. 'marketing_email', 'analytics'
    granted BOOLEAN NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    withdrawal_at TIMESTAMPTZ NULL
);
```

## Checklist

- [ ] Only personal data with a defined, current purpose is collected; no speculative 'just in case' fields.
- [ ] Consent is tracked per-purpose with an accessible withdrawal mechanism, not a single blanket checkbox.
- [ ] Data subject access, deletion, and export requests are supportable via a defined workflow, not manual ad hoc handling.
- [ ] Personal data is encrypted at rest and in transit per skills/80-security/secrets-and-key-management/SKILL.md.
- [ ] Retention periods are defined per data category with automated enforcement/deletion.
- [ ] A record of processing activities exists documenting what data is processed, why, and by whom.

## Anti-patterns

- **Speculative data collection** - Collecting personal data fields with no defined current purpose, on the assumption they might be useful later.
- **Silent purpose repurposing** - Using data collected for one purpose (e.g. order fulfillment) for an unrelated purpose (e.g. marketing) without fresh consent.
- **Manual-only deletion process** - Handling data subject deletion requests through an ad hoc manual process with no defined, auditable workflow.
- **Indefinite retention by default** - Keeping personal data forever with no defined retention period or deletion mechanism, simply because deleting it was never prioritized.
- **Treating this as purely a legal problem** - Assuming compliance is entirely legal's responsibility with no engineering practices supporting it, resulting in unsupportable requests when they arrive.

## Verification

- A data subject deletion request executed end-to-end confirms personal data is removed/anonymized across all relevant systems.
- Consent records show purpose-specific granularity with a working withdrawal mechanism.
- An automated job confirms data past its retention period is deleted without manual intervention.
- A record of processing activities is current and reviewed as part of a regular compliance cadence.

## References

- skills/80-security/secrets-and-key-management/SKILL.md
- skills/80-security/secure-coding-owasp-top-10/SKILL.md
- GDPR Articles 5, 15-20 (data minimization and data subject rights) - consult legal counsel for jurisdiction-specific obligations.
