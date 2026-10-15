---
name: cost-and-resource-optimization
description: Use when cloud infrastructure spend needs to be understood, attributed, and reduced without compromising reliability or performance.
category: devops
tags: [finops, cost-optimization, cloud]
maturity: stable
updated: 2026-08-21
---

## Purpose

Cloud costs left unmanaged tend to grow through over-provisioning, orphaned resources, and lack of visibility into which team or feature is driving spend. This skill covers cost attribution via tagging, right-sizing resources based on actual usage, and applying cost-saving purchase options (reserved/spot capacity) without sacrificing the reliability guarantees the system needs.

It treats cost as a first-class non-functional requirement, reviewed alongside performance and reliability rather than as an afterthought handled only when a bill spikes unexpectedly.

## When to use / When NOT to use

**Use this skill when:**

- Cloud spend is growing faster than usage/traffic would justify.
- You need to attribute cost to specific teams, services, or features for accountability.
- You are reviewing whether a workload is over-provisioned relative to its actual utilization.

**Do NOT use this skill when:**

- The system is pre-launch or low-traffic and cost is genuinely negligible relative to engineering time spent optimizing it.
- The proposed cost-saving change (e.g. aggressive spot usage) would compromise a reliability guarantee more valuable than the savings.

## Prerequisites

- skills/60-devops/infrastructure-as-code/SKILL.md for consistent tagging enforced at provisioning time.
- skills/60-devops/observability/SKILL.md for the utilization metrics right-sizing decisions depend on.

## Workflow

1. **Tag every resource with owner and purpose** - Consistent team/service/environment tags enable cost attribution in billing reports, enforced via IaC policy.
2. **Review utilization against provisioned capacity regularly** - Compare actual CPU/memory/IO usage against requested/reserved capacity to find over-provisioned resources.
3. **Right-size based on measured usage, not guesswork** - Reduce instance size or replica count for consistently underutilized resources, informed by real metrics over a representative period.
4. **Use autoscaling to match capacity to real demand** - Scale down during low-traffic periods automatically rather than provisioning for peak load permanently.
5. **Apply committed-use discounts for stable, predictable workloads** - Reserved instances or savings plans for baseline capacity that's reliably running long-term.
6. **Use spot/preemptible capacity only for interruption-tolerant workloads** - Batch jobs and stateless, retriable workloads are good candidates; anything stateful or latency-critical is not.
7. **Clean up orphaned and unused resources** - Regularly identify and remove unattached volumes, idle load balancers, and unused snapshots that accrue cost with no benefit.
8. **Set budget alerts per team/project** - Automated alerts on spend anomalies catch runaway costs quickly, not at the end of a monthly billing cycle.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A resource consistently runs at 10% CPU utilization | Right-size it to a smaller instance type or reduce replica count, backed by the observed metric history. |
| Traffic has a predictable daily/weekly pattern with clear low-traffic periods | Use autoscaling (including scale-to-zero for non-critical workloads) rather than static peak-sized provisioning. |
| A workload runs continuously and predictably for a year or more | Purchase reserved capacity/savings plans for that baseline rather than paying full on-demand rates indefinitely. |
| A batch job can tolerate being interrupted and retried | Run it on spot/preemptible instances at a significant discount versus on-demand. |
| An orphaned resource (unattached disk, idle load balancer) is found | Confirm it's truly unused, then delete it; don't let 'just in case' resources accumulate cost indefinitely. |

## Reference implementation

Enforcing cost-attribution tags via a Terraform policy check:

```hcl
# Required tags enforced at plan time via a policy-as-code check (e.g. Sentinel/OPA)
resource "cloud_compute_instance" "api" {
  name          = "order-api"
  instance_type = "m5.large"
  tags = {
    team        = "orders"
    environment = "production"
    cost_center = "CC-4471"
  }
}

# Policy rule (conceptual): reject any resource lacking team/environment/cost_center tags
# so every line item in the cloud bill can be attributed to a specific owner.
```

- Enforcing tags at plan time (failing the pipeline on missing tags) is far more reliable than asking engineers to remember to tag resources manually.
- cost_center enables direct mapping from cloud billing exports to internal budget owners.

### A budget alert configuration to catch anomalous spend early (YAML, conceptual)

Alerting well before a monthly bill surprises anyone:

```yaml
budgets:
  - name: orders-team-monthly
    amount: 5000
    currency: USD
    filter: { tag: { team: orders } }
    alerts:
      - threshold_percent: 80
        notify: ["orders-team-slack"]
      - threshold_percent: 100
        notify: ["orders-team-slack", "finops-oncall"]
```

## Checklist

- [ ] Every provisioned resource carries owner/team/environment tags, enforced at plan/apply time.
- [ ] Resource sizing is reviewed against measured utilization, not left at original provisioning guesses indefinitely.
- [ ] Autoscaling matches capacity to real demand rather than permanently provisioning for peak load.
- [ ] Committed-use discounts are applied to stable, predictable baseline workloads.
- [ ] Spot/preemptible capacity is used only for genuinely interruption-tolerant workloads.
- [ ] Orphaned resources are identified and cleaned up on a regular cadence, and budget alerts catch spend anomalies early.

## Anti-patterns

- **Untagged resources** - Provisioning infrastructure with no owner/team tags, making it impossible to attribute cost or safely clean it up later.
- **Provision-for-peak-forever** - Sizing a service permanently for its highest-ever traffic spike instead of using autoscaling to match real, varying demand.
- **Spot instances for stateful critical workloads** - Running a primary database or stateful critical service on preemptible/spot capacity, risking data loss or downtime on reclaim.
- **Orphaned resource accumulation** - Leaving unattached disks, idle load balancers, and old snapshots running indefinitely because no one is responsible for cleaning them up.
- **Cost reviewed only after a billing surprise** - Treating cost optimization as a reactive fire-drill after an unexpectedly large invoice instead of an ongoing practice.

## Verification

- A billing report can attribute at least 95% of monthly spend to a specific team/service via tags.
- A right-sizing review identifies and resizes/removes resources running below an agreed utilization threshold for a sustained period.
- No stateful, critical workload is found running on spot/preemptible capacity during an infrastructure audit.
- Budget alerts fire correctly in a test scenario before spend reaches 100% of the configured threshold.

## References

- skills/60-devops/infrastructure-as-code/SKILL.md
- skills/60-devops/observability/SKILL.md
- FinOps Foundation — FinOps Framework.
