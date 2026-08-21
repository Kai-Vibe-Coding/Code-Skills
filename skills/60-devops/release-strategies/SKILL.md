---
name: release-strategies
description: Use when deciding how a new version of a service should be rolled out to production to minimize the blast radius of a bad release.
category: devops
tags: [release-strategies, canary, blue-green]
maturity: stable
updated: 2026-08-21
---

## Purpose

A big-bang deployment that switches all traffic to a new version at once maximizes the blast radius of any regression. This skill covers progressive release strategies — canary releases, blue-green deployment, and feature-flag-gated rollout — that limit exposure to a new version and enable fast, automated rollback when something goes wrong.

It also covers the automated health checks and rollback triggers that make progressive delivery safe rather than just slower.

## When to use / When NOT to use

**Use this skill when:**

- You are deploying a change to a production service with real user traffic.
- A past incident was caused or worsened by an all-at-once deployment with no gradual rollout.
- You need to decouple deploying code from releasing a feature to users.

**Do NOT use this skill when:**

- The service has no production traffic yet (pre-launch) — a simpler direct deploy is fine until real users are involved.
- The change is a config-only, zero-risk update where progressive rollout overhead isn't justified.

## Prerequisites

- skills/60-devops/observability/SKILL.md for the health signals a canary/rollback decision depends on.
- skills/60-devops/kubernetes-deployment/SKILL.md (or equivalent platform) supporting traffic-splitting.

## Workflow

1. **Choose a release strategy matching the risk of the change** - Low-risk changes may use a standard rolling deploy; high-risk changes warrant canary or blue-green.
2. **Deploy the new version alongside the old, receiving no traffic initially** - Blue-green: stand up the new environment fully before any traffic switch; canary: deploy alongside with a small traffic percentage.
3. **Route a small percentage of traffic to the new version** - Canary releases start at 1-5% traffic, watched closely against key health metrics.
4. **Define automated health checks and rollback triggers** - Error rate, latency, and business-metric thresholds that automatically halt/rollback the release if breached.
5. **Gradually increase traffic on success** - Step up the canary percentage (5% -> 25% -> 50% -> 100%) only after each stage's health checks pass for a defined bake time.
6. **Decouple deployment from release using feature flags** - Deploy the code dark (flag off) and separately enable the feature for users once deployment is confirmed healthy.
7. **Automate rollback, don't rely on a human noticing first** - A failing canary should automatically revert traffic to the previous version without waiting for manual intervention.
8. **Communicate release status to stakeholders** - Notify relevant channels when a progressive rollout starts, advances, or rolls back.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Change is a well-tested, low-risk bug fix | A standard rolling deployment (skills/60-devops/kubernetes-deployment/SKILL.md) is likely sufficient. |
| Change touches a critical, high-traffic path | Use a canary release with automated metric-based rollback, starting at a small traffic percentage. |
| You need to instantly revert if something goes wrong, with zero rebuild time | Use blue-green deployment, keeping the old environment fully live and ready to receive traffic back instantly. |
| A feature needs to be tested with real users before a full launch | Deploy the code normally but gate the feature behind a flag, enabling it for a targeted subset first. |
| A canary shows a metric regression during rollout | Automatically halt and roll back the traffic shift rather than proceeding and hoping it stabilizes. |

## Reference implementation

A canary rollout step configuration with automated analysis and rollback (Argo Rollouts style):

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
spec:
  strategy:
    canary:
      steps:
        - setWeight: 5
        - pause: { duration: 5m }
        - analysis:
            templates:
              - templateName: error-rate-check
        - setWeight: 25
        - pause: { duration: 10m }
        - setWeight: 100
  # error-rate-check analysis template queries the metrics backend and
  # automatically aborts/rolls back the Rollout if error rate exceeds threshold.
```

- The analysis step queries live metrics (error rate, latency) and halts progression automatically if thresholds are breached, without waiting on a human.
- Pausing between weight increases gives enough bake time to catch regressions that only appear under sustained, real traffic.

### Decoupling deploy from release using a feature flag (C#)

Deploying new code dark, then enabling it for a targeted audience separately from the deploy:

```csharp
if (await _features.IsEnabledAsync("NewCheckoutFlow", targetingContext: new(userId), ct))
{
    return await _newCheckout.ProcessAsync(cart, ct);
}
return await _legacyCheckout.ProcessAsync(cart, ct);
// The flag can target a percentage or specific accounts, entirely independent
// of when the code itself was deployed.
```

## Checklist

- [ ] The release strategy chosen matches the risk profile of the change (rolling, canary, or blue-green).
- [ ] Automated health checks and rollback triggers are defined before a progressive rollout starts, not improvised mid-incident.
- [ ] Canary traffic percentage increases gradually with a defined bake time at each stage.
- [ ] A failing health check automatically halts/rolls back the release without requiring a human to notice first.
- [ ] High-risk features are deployed dark and enabled via a feature flag separately from the code deployment.
- [ ] Release status (start, progress, rollback) is communicated to relevant stakeholders.

## Anti-patterns

- **Big-bang deployment** - Switching 100% of traffic to a new version instantly with no gradual rollout, maximizing the blast radius of any regression.
- **Manual-only rollback** - Relying on an on-call engineer to notice a problem and manually trigger a rollback instead of automated metric-based triggers.
- **No bake time between canary steps** - Increasing traffic weight rapidly with no pause to observe real-world behavior at each stage.
- **Coupling deploy and release** - Only being able to test a risky feature by deploying it fully live to all users, instead of gating it behind a flag for controlled exposure.
- **Ignoring canary signals** - Proceeding with a rollout despite a canary showing early signs of regression, hoping it resolves itself.

## Verification

- A simulated regression in the canary stage triggers an automatic halt/rollback within the expected time window.
- Traffic percentage increases only after each stage's defined bake time and health check pass, verified in rollout history.
- A risky feature can be enabled/disabled via its flag independently of a code deployment, verified in a lower environment.
- Stakeholders receive a notification at each major stage of a progressive rollout, confirmed via the notification channel's history.

## References

- skills/60-devops/observability/SKILL.md
- skills/60-devops/kubernetes-deployment/SKILL.md
- skills/30-backend/configuration-and-feature-flags/SKILL.md
