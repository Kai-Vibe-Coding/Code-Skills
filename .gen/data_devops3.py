SKILLS = [
    dict(
        dir="60-devops", slug="observability", category="devops",
        tags=["observability", "logging", "metrics", "tracing"],
        desc="Use when a service needs structured logging, metrics, and distributed tracing so its behavior in production can be understood without guessing.",
        purpose=[
            "Without deliberate observability, diagnosing a production issue means guessing, adding ad hoc "
            "log statements, and redeploying — far too slow for anything urgent. This skill covers the three "
            "pillars of observability (structured logs, metrics, distributed traces) and how they connect via "
            "a shared correlation ID so an engineer can go from a single alert to the exact request that "
            "caused it.",
            "It emphasizes designing observability in from the start of a service, not retrofitting it after "
            "the first difficult incident.",
        ],
        when_use=[
            "You are building a new service and need to establish its logging/metrics/tracing baseline.",
            "An incident was hard to diagnose because logs lacked context or correlation across services.",
            "You need to define SLIs/SLOs and alerting for a service.",
        ],
        when_not=[
            "The system is a short-lived batch script with no ongoing operational lifecycle.",
            "You're debugging a specific already-reproducible local bug — a debugger is more effective than production observability tooling for that.",
        ],
        prereqs=[
            "skills/60-devops/incident-response-and-runbooks/SKILL.md for how observability data feeds incident response.",
            "A logging/metrics/tracing backend selected (e.g. OpenTelemetry exporting to a vendor or self-hosted stack).",
        ],
        workflow=[
            ("Emit structured logs, not free-text strings", "Use structured logging (key-value pairs / JSON) so logs are queryable, not just human-readable."),
            ("Propagate a correlation/trace ID through every request", "Generate or forward a trace ID at the edge and include it in every log line and downstream call for that request."),
            ("Instrument with OpenTelemetry for traces and metrics", "Use a vendor-neutral instrumentation library so the backend (Jaeger, Datadog, etc.) can be swapped without re-instrumenting code."),
            ("Define RED/USE metrics for each service", "Rate, Errors, Duration for request-driven services; Utilization, Saturation, Errors for resource-driven ones."),
            ("Set SLIs and SLOs, then alert on SLO burn rate", "Alert when the error budget is burning too fast, not on every individual transient error."),
            ("Avoid logging sensitive data", "Redact or omit PII/secrets from logs per skills/80-security/privacy-and-compliance-basics/SKILL.md."),
            ("Build dashboards around user-facing outcomes", "Dashboards answer 'is the service healthy for users' first, then drill into infrastructure-level detail."),
            ("Test observability during incident drills", "Confirm the on-call engineer can actually trace a synthetic failure end-to-end using only the observability tooling."),
        ],
        decision=[
            ("A request fails somewhere across three microservices", "Follow the shared trace ID through each service's logs/traces to find exactly where it failed."),
            ("You need to alert on service health without noisy false positives", "Alert on SLO error-budget burn rate over a window, not on every single error occurrence."),
            ("A log line risks including a customer's email or payment details", "Redact or hash the sensitive field before logging, per skills/80-security/privacy-and-compliance-basics/SKILL.md."),
            ("A dashboard has become a wall of infrastructure graphs no one checks", "Redesign it around user-facing outcomes (latency, error rate, availability) with infra detail one click deeper."),
            ("On-call engineers say they can't diagnose incidents from current tooling", "Run an incident drill to find the specific observability gap, then close it before the next real incident."),
        ],
        code_lang="csharp",
        code_intro="Structured logging with a correlation ID propagated through a request (C#/Serilog):",
        code=(
            "app.Use(async (context, next) =>\n"
            "{\n"
            "    var correlationId = context.Request.Headers[\"X-Correlation-Id\"].FirstOrDefault()\n"
            "        ?? Guid.NewGuid().ToString();\n"
            "    using (LogContext.PushProperty(\"CorrelationId\", correlationId))\n"
            "    {\n"
            "        context.Response.Headers[\"X-Correlation-Id\"] = correlationId;\n"
            "        await next();\n"
            "    }\n"
            "});\n"
            "\n"
            "// Every log call automatically includes CorrelationId as a structured field:\n"
            "logger.LogInformation(\"Order {OrderId} submitted by {CustomerId}\",\n"
            "    order.Id, order.CustomerId);\n"
            "// Emits: { \"CorrelationId\": \"...\", \"OrderId\": \"...\", \"CustomerId\": \"...\", \"@m\": \"Order ... submitted by ...\" }\n"
        ),
        code_notes=[
            "LogContext.PushProperty attaches CorrelationId to every log statement inside the request's scope automatically, no manual threading needed.",
            "The correlation ID is echoed back in the response header so client-side logs/support tickets can reference the same identifier.",
        ],
        code2_heading="An SLO-based alert on error-budget burn rate (YAML, Prometheus-style)",
        code2=("yaml",
            "Alerting on a sustained burn rate rather than any single transient error:",
            "groups:\n"
            "  - name: order-api-slo\n"
            "    rules:\n"
            "      - alert: OrderApiFastBurn\n"
            "        expr: |\n"
            "          (sum(rate(http_requests_total{job=\"order-api\",status=~\"5..\"}[5m]))\n"
            "           / sum(rate(http_requests_total{job=\"order-api\"}[5m]))) > 0.02\n"
            "        for: 5m\n"
            "        labels: { severity: page }\n"
        ),
        checklist=[
            "Logs are structured (key-value/JSON), not unstructured free text.",
            "A correlation/trace ID is propagated through every request and downstream call.",
            "Instrumentation uses a vendor-neutral standard (OpenTelemetry) rather than a proprietary lock-in SDK where feasible.",
            "SLIs/SLOs are defined, and alerts fire on error-budget burn rate, not raw transient error counts.",
            "No sensitive/PII data is written to logs unredacted.",
            "Dashboards are organized around user-facing outcomes, with infrastructure detail available on drill-down.",
        ],
        antipatterns=[
            ("Unstructured log strings", "Logging free-text strings like 'order failed' with no structured fields, making them nearly impossible to query at scale."),
            ("No correlation ID", "Losing the ability to trace one user's request across multiple services because no shared identifier connects the logs."),
            ("Alerting on every error", "Paging on-call for every single transient error instead of a sustained burn rate against an agreed error budget."),
            ("Logging sensitive data", "Writing full customer PII or payment details into logs in plaintext, creating a compliance and security risk."),
            ("Dashboards no one understands", "Building dashboards full of raw infrastructure metrics with no clear connection to user-facing health."),
        ],
        verification=[
            "A synthetic failure injected into one service can be traced end-to-end using only logs/traces and the correlation ID.",
            "An alert fires correctly when a simulated SLO burn rate exceeds the configured threshold, and stays quiet for isolated transient errors.",
            "A log/PII scan confirms no sensitive fields are emitted unredacted.",
            "An on-call engineer, during a drill, can diagnose a synthetic incident using only the observability stack within an agreed time budget.",
        ],
        references=[
            "skills/60-devops/incident-response-and-runbooks/SKILL.md",
            "skills/80-security/privacy-and-compliance-basics/SKILL.md",
            "Google SRE Book — SLIs, SLOs, and Error Budgets.",
            "OpenTelemetry documentation.",
        ],
    ),
    dict(
        dir="60-devops", slug="release-strategies", category="devops",
        tags=["release-strategies", "canary", "blue-green"],
        desc="Use when deciding how a new version of a service should be rolled out to production to minimize the blast radius of a bad release.",
        purpose=[
            "A big-bang deployment that switches all traffic to a new version at once maximizes the blast "
            "radius of any regression. This skill covers progressive release strategies — canary releases, "
            "blue-green deployment, and feature-flag-gated rollout — that limit exposure to a new version "
            "and enable fast, automated rollback when something goes wrong.",
            "It also covers the automated health checks and rollback triggers that make progressive delivery "
            "safe rather than just slower.",
        ],
        when_use=[
            "You are deploying a change to a production service with real user traffic.",
            "A past incident was caused or worsened by an all-at-once deployment with no gradual rollout.",
            "You need to decouple deploying code from releasing a feature to users.",
        ],
        when_not=[
            "The service has no production traffic yet (pre-launch) — a simpler direct deploy is fine until real users are involved.",
            "The change is a config-only, zero-risk update where progressive rollout overhead isn't justified.",
        ],
        prereqs=[
            "skills/60-devops/observability/SKILL.md for the health signals a canary/rollback decision depends on.",
            "skills/60-devops/kubernetes-deployment/SKILL.md (or equivalent platform) supporting traffic-splitting.",
        ],
        workflow=[
            ("Choose a release strategy matching the risk of the change", "Low-risk changes may use a standard rolling deploy; high-risk changes warrant canary or blue-green."),
            ("Deploy the new version alongside the old, receiving no traffic initially", "Blue-green: stand up the new environment fully before any traffic switch; canary: deploy alongside with a small traffic percentage."),
            ("Route a small percentage of traffic to the new version", "Canary releases start at 1-5% traffic, watched closely against key health metrics."),
            ("Define automated health checks and rollback triggers", "Error rate, latency, and business-metric thresholds that automatically halt/rollback the release if breached."),
            ("Gradually increase traffic on success", "Step up the canary percentage (5% -> 25% -> 50% -> 100%) only after each stage's health checks pass for a defined bake time."),
            ("Decouple deployment from release using feature flags", "Deploy the code dark (flag off) and separately enable the feature for users once deployment is confirmed healthy."),
            ("Automate rollback, don't rely on a human noticing first", "A failing canary should automatically revert traffic to the previous version without waiting for manual intervention."),
            ("Communicate release status to stakeholders", "Notify relevant channels when a progressive rollout starts, advances, or rolls back."),
        ],
        decision=[
            ("Change is a well-tested, low-risk bug fix", "A standard rolling deployment (skills/60-devops/kubernetes-deployment/SKILL.md) is likely sufficient."),
            ("Change touches a critical, high-traffic path", "Use a canary release with automated metric-based rollback, starting at a small traffic percentage."),
            ("You need to instantly revert if something goes wrong, with zero rebuild time", "Use blue-green deployment, keeping the old environment fully live and ready to receive traffic back instantly."),
            ("A feature needs to be tested with real users before a full launch", "Deploy the code normally but gate the feature behind a flag, enabling it for a targeted subset first."),
            ("A canary shows a metric regression during rollout", "Automatically halt and roll back the traffic shift rather than proceeding and hoping it stabilizes."),
        ],
        code_lang="yaml",
        code_intro="A canary rollout step configuration with automated analysis and rollback (Argo Rollouts style):",
        code=(
            "apiVersion: argoproj.io/v1alpha1\n"
            "kind: Rollout\n"
            "spec:\n"
            "  strategy:\n"
            "    canary:\n"
            "      steps:\n"
            "        - setWeight: 5\n"
            "        - pause: { duration: 5m }\n"
            "        - analysis:\n"
            "            templates:\n"
            "              - templateName: error-rate-check\n"
            "        - setWeight: 25\n"
            "        - pause: { duration: 10m }\n"
            "        - setWeight: 100\n"
            "  # error-rate-check analysis template queries the metrics backend and\n"
            "  # automatically aborts/rolls back the Rollout if error rate exceeds threshold.\n"
        ),
        code_notes=[
            "The analysis step queries live metrics (error rate, latency) and halts progression automatically if thresholds are breached, without waiting on a human.",
            "Pausing between weight increases gives enough bake time to catch regressions that only appear under sustained, real traffic.",
        ],
        code2_heading="Decoupling deploy from release using a feature flag (C#)",
        code2=("csharp",
            "Deploying new code dark, then enabling it for a targeted audience separately from the deploy:",
            "if (await _features.IsEnabledAsync(\"NewCheckoutFlow\", targetingContext: new(userId), ct))\n"
            "{\n"
            "    return await _newCheckout.ProcessAsync(cart, ct);\n"
            "}\n"
            "return await _legacyCheckout.ProcessAsync(cart, ct);\n"
            "// The flag can target a percentage or specific accounts, entirely independent\n"
            "// of when the code itself was deployed.\n"
        ),
        checklist=[
            "The release strategy chosen matches the risk profile of the change (rolling, canary, or blue-green).",
            "Automated health checks and rollback triggers are defined before a progressive rollout starts, not improvised mid-incident.",
            "Canary traffic percentage increases gradually with a defined bake time at each stage.",
            "A failing health check automatically halts/rolls back the release without requiring a human to notice first.",
            "High-risk features are deployed dark and enabled via a feature flag separately from the code deployment.",
            "Release status (start, progress, rollback) is communicated to relevant stakeholders.",
        ],
        antipatterns=[
            ("Big-bang deployment", "Switching 100% of traffic to a new version instantly with no gradual rollout, maximizing the blast radius of any regression."),
            ("Manual-only rollback", "Relying on an on-call engineer to notice a problem and manually trigger a rollback instead of automated metric-based triggers."),
            ("No bake time between canary steps", "Increasing traffic weight rapidly with no pause to observe real-world behavior at each stage."),
            ("Coupling deploy and release", "Only being able to test a risky feature by deploying it fully live to all users, instead of gating it behind a flag for controlled exposure."),
            ("Ignoring canary signals", "Proceeding with a rollout despite a canary showing early signs of regression, hoping it resolves itself."),
        ],
        verification=[
            "A simulated regression in the canary stage triggers an automatic halt/rollback within the expected time window.",
            "Traffic percentage increases only after each stage's defined bake time and health check pass, verified in rollout history.",
            "A risky feature can be enabled/disabled via its flag independently of a code deployment, verified in a lower environment.",
            "Stakeholders receive a notification at each major stage of a progressive rollout, confirmed via the notification channel's history.",
        ],
        references=[
            "skills/60-devops/observability/SKILL.md",
            "skills/60-devops/kubernetes-deployment/SKILL.md",
            "skills/30-backend/configuration-and-feature-flags/SKILL.md",
        ],
    ),
]
