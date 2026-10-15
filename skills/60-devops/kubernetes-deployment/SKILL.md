---
name: kubernetes-deployment
description: Use when deploying a containerized service to Kubernetes and you need correct resource requests, health probes, and rollout configuration for reliable operation.
category: devops
tags: [kubernetes, deployment, helm]
maturity: stable
updated: 2026-08-21
---

## Purpose

A Kubernetes Deployment with no resource limits, missing probes, or default rollout settings can starve the cluster, get killed at the wrong time, or roll out badly during a bad deploy. This skill covers the essential Deployment/Service manifest configuration — resource requests/limits, liveness/readiness probes, and rolling update strategy — needed for a service to run reliably.

It treats Helm charts (or Kustomize) as the standard packaging mechanism for reusable, parameterized manifests across environments.

## When to use / When NOT to use

**Use this skill when:**

- You are deploying a new service to Kubernetes for the first time.
- An existing deployment shows OOMKills, failed rollouts, or traffic sent to not-yet-ready pods.
- You are configuring autoscaling or multi-environment deployment via Helm values.

**Do NOT use this skill when:**

- The workload runs on a simpler platform (e.g. a PaaS or serverless container service) with no direct Kubernetes manifests involved.
- You're debugging the container image itself rather than its Kubernetes deployment configuration — see skills/60-devops/docker-containerization/SKILL.md instead.

## Prerequisites

- skills/60-devops/docker-containerization/SKILL.md for the image being deployed, including its health check endpoint.
- skills/60-devops/observability/SKILL.md for the metrics/logging the deployment should expose.

## Workflow

1. **Define resource requests and limits** - Set CPU/memory requests based on measured usage, and limits to prevent one pod from starving the node.
2. **Add liveness and readiness probes** - Liveness restarts a stuck pod; readiness removes a not-yet-ready pod from load balancing without restarting it.
3. **Configure a safe rolling update strategy** - maxUnavailable and maxSurge tuned so capacity never drops below what's needed during a rollout.
4. **Externalize configuration via ConfigMaps and Secrets** - Environment-specific values and sensitive values are never baked into the image.
5. **Package manifests with Helm for reuse across environments** - One chart with environment-specific values.yaml files, not copy-pasted YAML per environment.
6. **Set PodDisruptionBudgets for critical services** - Ensure voluntary disruptions (node drains, cluster upgrades) don't take down all replicas simultaneously.
7. **Configure autoscaling based on real metrics** - Use HorizontalPodAutoscaler targeting CPU or custom metrics reflecting actual load, not guesswork.
8. **Verify rollouts before considering them complete** - Watch rollout status and readiness in CI/CD, automatically rolling back on failure rather than leaving a broken deploy live.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A pod's liveness probe is failing due to a slow-starting dependency | Add a startupProbe with a longer grace period rather than loosening the liveness probe's own timing. |
| A rollout must never drop below full capacity | Set maxUnavailable: 0 and maxSurge: 1 (or higher) so new pods come up before old ones terminate. |
| A service handles bursty traffic | Configure an HPA scaling on CPU or a custom request-rate metric, with sensible min/max replica bounds. |
| Multiple replicas exist for high availability | Add a PodDisruptionBudget ensuring at least N replicas stay available during voluntary disruptions. |
| Configuration differs across dev/staging/production | Use one Helm chart with per-environment values.yaml files, not separate copy-pasted manifest sets. |

## Reference implementation

A Deployment manifest with resource limits, probes, and a safe rollout strategy:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxUnavailable: 0, maxSurge: 1 }
  template:
    spec:
      containers:
        - name: order-api
          image: registry.example.com/order-api:1.4.2
          resources:
            requests: { cpu: "250m", memory: "256Mi" }
            limits: { cpu: "500m", memory: "512Mi" }
          readinessProbe:
            httpGet: { path: /health/ready, port: 8080 }
            initialDelaySeconds: 5
          livenessProbe:
            httpGet: { path: /health/live, port: 8080 }
            initialDelaySeconds: 15
            periodSeconds: 20
```

- maxUnavailable: 0 with maxSurge: 1 guarantees full capacity is maintained throughout the rollout, at the cost of briefly running one extra pod.
- Separate readiness and liveness endpoints let a pod be marked not-ready (e.g. warming a cache) without being killed by the liveness probe.

### A PodDisruptionBudget protecting availability during node maintenance (YAML)

Ensuring at least 2 replicas remain available even during a voluntary cluster disruption:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: order-api-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels: { app: order-api }
```

## Checklist

- [ ] Every container has resource requests and limits set based on measured usage.
- [ ] Liveness and readiness probes are defined separately with appropriate initial delays.
- [ ] Rolling update strategy guarantees the required minimum capacity throughout a deploy.
- [ ] Configuration and secrets are externalized via ConfigMaps/Secrets, never baked into the image.
- [ ] A PodDisruptionBudget protects availability for services with more than one replica.
- [ ] Manifests are packaged via Helm (or Kustomize) with per-environment values, not duplicated YAML.

## Anti-patterns

- **No resource limits** - Deploying a pod with no memory limit, allowing it to consume node resources unbounded and cause node-wide instability.
- **Single combined health endpoint** - Using the same endpoint for both liveness and readiness, causing a slow-warming pod to be killed and restarted in a crash loop instead of just marked not-ready.
- **maxUnavailable defaulting to 25%** - Accepting the default rolling update settings without considering whether a capacity dip during rollout is acceptable for this service.
- **Secrets baked into the image or plain manifests** - Committing a database password directly into a ConfigMap or Docker image instead of a proper Secret/secret manager.
- **Copy-pasted manifests per environment** - Maintaining separate near-duplicate YAML files per environment instead of one parameterized Helm chart.

## Verification

- A load test confirms the pod is OOMKilled or throttled appropriately only when actually exceeding its set limits, not prematurely.
- A rolling deploy under load shows zero dropped requests, confirmed via a synthetic traffic test during rollout.
- Draining a node hosting one replica does not take the service below its PodDisruptionBudget's minAvailable.
- No Secret value appears in a ConfigMap, Deployment manifest, or image layer, confirmed by a manifest/image scan.

## References

- skills/60-devops/docker-containerization/SKILL.md
- skills/60-devops/observability/SKILL.md
- Kubernetes documentation — Deployments, Probes, and PodDisruptionBudgets.
