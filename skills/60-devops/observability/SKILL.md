---
name: observability
description: Use when a service needs structured logging, metrics, and distributed tracing so its behavior in production can be understood without guessing.
category: devops
tags: [observability, logging, metrics, tracing]
maturity: stable
updated: 2026-08-21
---

## Purpose

Without deliberate observability, diagnosing a production issue means guessing, adding ad hoc log statements, and redeploying — far too slow for anything urgent. This skill covers the three pillars of observability (structured logs, metrics, distributed traces) and how they connect via a shared correlation ID so an engineer can go from a single alert to the exact request that caused it.

It emphasizes designing observability in from the start of a service, not retrofitting it after the first difficult incident.

## When to use / When NOT to use

**Use this skill when:**

- You are building a new service and need to establish its logging/metrics/tracing baseline.
- An incident was hard to diagnose because logs lacked context or correlation across services.
- You need to define SLIs/SLOs and alerting for a service.

**Do NOT use this skill when:**

- The system is a short-lived batch script with no ongoing operational lifecycle.
- You're debugging a specific already-reproducible local bug — a debugger is more effective than production observability tooling for that.

## Prerequisites

- skills/60-devops/incident-response-and-runbooks/SKILL.md for how observability data feeds incident response.
- A logging/metrics/tracing backend selected (e.g. OpenTelemetry exporting to a vendor or self-hosted stack).

## Workflow

1. **Emit structured logs, not free-text strings** - Use structured logging (key-value pairs / JSON) so logs are queryable, not just human-readable.
2. **Propagate a correlation/trace ID through every request** - Generate or forward a trace ID at the edge and include it in every log line and downstream call for that request.
3. **Instrument with OpenTelemetry for traces and metrics** - Use a vendor-neutral instrumentation library so the backend (Jaeger, Datadog, etc.) can be swapped without re-instrumenting code.
4. **Define RED/USE metrics for each service** - Rate, Errors, Duration for request-driven services; Utilization, Saturation, Errors for resource-driven ones.
5. **Set SLIs and SLOs, then alert on SLO burn rate** - Alert when the error budget is burning too fast, not on every individual transient error.
6. **Avoid logging sensitive data** - Redact or omit PII/secrets from logs per skills/80-security/privacy-and-compliance-basics/SKILL.md.
7. **Build dashboards around user-facing outcomes** - Dashboards answer 'is the service healthy for users' first, then drill into infrastructure-level detail.
8. **Test observability during incident drills** - Confirm the on-call engineer can actually trace a synthetic failure end-to-end using only the observability tooling.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A request fails somewhere across three microservices | Follow the shared trace ID through each service's logs/traces to find exactly where it failed. |
| You need to alert on service health without noisy false positives | Alert on SLO error-budget burn rate over a window, not on every single error occurrence. |
| A log line risks including a customer's email or payment details | Redact or hash the sensitive field before logging, per skills/80-security/privacy-and-compliance-basics/SKILL.md. |
| A dashboard has become a wall of infrastructure graphs no one checks | Redesign it around user-facing outcomes (latency, error rate, availability) with infra detail one click deeper. |
| On-call engineers say they can't diagnose incidents from current tooling | Run an incident drill to find the specific observability gap, then close it before the next real incident. |

## Reference implementation

Structured logging with a correlation ID propagated through a request (C#/Serilog):

```csharp
app.Use(async (context, next) =>
{
    var correlationId = context.Request.Headers["X-Correlation-Id"].FirstOrDefault()
        ?? Guid.NewGuid().ToString();
    using (LogContext.PushProperty("CorrelationId", correlationId))
    {
        context.Response.Headers["X-Correlation-Id"] = correlationId;
        await next();
    }
});

// Every log call automatically includes CorrelationId as a structured field:
logger.LogInformation("Order {OrderId} submitted by {CustomerId}",
    order.Id, order.CustomerId);
// Emits: { "CorrelationId": "...", "OrderId": "...", "CustomerId": "...", "@m": "Order ... submitted by ..." }
```

- LogContext.PushProperty attaches CorrelationId to every log statement inside the request's scope automatically, no manual threading needed.
- The correlation ID is echoed back in the response header so client-side logs/support tickets can reference the same identifier.

### An SLO-based alert on error-budget burn rate (YAML, Prometheus-style)

Alerting on a sustained burn rate rather than any single transient error:

```yaml
groups:
  - name: order-api-slo
    rules:
      - alert: OrderApiFastBurn
        expr: |
          (sum(rate(http_requests_total{job="order-api",status=~"5.."}[5m]))
           / sum(rate(http_requests_total{job="order-api"}[5m]))) > 0.02
        for: 5m
        labels: { severity: page }
```

## Checklist

- [ ] Logs are structured (key-value/JSON), not unstructured free text.
- [ ] A correlation/trace ID is propagated through every request and downstream call.
- [ ] Instrumentation uses a vendor-neutral standard (OpenTelemetry) rather than a proprietary lock-in SDK where feasible.
- [ ] SLIs/SLOs are defined, and alerts fire on error-budget burn rate, not raw transient error counts.
- [ ] No sensitive/PII data is written to logs unredacted.
- [ ] Dashboards are organized around user-facing outcomes, with infrastructure detail available on drill-down.

## Anti-patterns

- **Unstructured log strings** - Logging free-text strings like 'order failed' with no structured fields, making them nearly impossible to query at scale.
- **No correlation ID** - Losing the ability to trace one user's request across multiple services because no shared identifier connects the logs.
- **Alerting on every error** - Paging on-call for every single transient error instead of a sustained burn rate against an agreed error budget.
- **Logging sensitive data** - Writing full customer PII or payment details into logs in plaintext, creating a compliance and security risk.
- **Dashboards no one understands** - Building dashboards full of raw infrastructure metrics with no clear connection to user-facing health.

## Verification

- A synthetic failure injected into one service can be traced end-to-end using only logs/traces and the correlation ID.
- An alert fires correctly when a simulated SLO burn rate exceeds the configured threshold, and stays quiet for isolated transient errors.
- A log/PII scan confirms no sensitive fields are emitted unredacted.
- An on-call engineer, during a drill, can diagnose a synthetic incident using only the observability stack within an agreed time budget.

## References

- skills/60-devops/incident-response-and-runbooks/SKILL.md
- skills/80-security/privacy-and-compliance-basics/SKILL.md
- Google SRE Book — SLIs, SLOs, and Error Budgets.
- OpenTelemetry documentation.
