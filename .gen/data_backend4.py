SKILLS = [
    dict(
        dir="30-backend", slug="authentication-and-authorization", category="backend",
        tags=["authn", "authz", "jwt", "policies"],
        desc="Use when implementing login, token validation, or access-control checks in a .NET API and you need a consistent pattern for authentication and fine-grained authorization.",
        purpose=[
            "Authentication (who is the caller) and authorization (what can they do) are frequently conflated, "
            "leading to ad hoc role checks scattered through controllers. This skill establishes JWT-bearer "
            "authentication with ASP.NET Core and policy-based authorization so access rules are declared "
            "once, testable, and consistently enforced.",
            "It also covers the difference between role-based and resource-based (ownership) authorization, "
            "since most real applications need both.",
        ],
        when_use=[
            "You are implementing or reviewing login, token issuance, or endpoint protection in an ASP.NET Core API.",
            "Authorization rules are becoming complex (roles plus per-resource ownership plus feature flags).",
            "You need to add a new protected endpoint and want to apply the established pattern.",
        ],
        when_not=[
            "You are designing the deeper cryptographic details of a custom identity provider — defer to a vetted identity platform instead of building one from scratch.",
            "The task is purely about penetration testing auth mechanisms — see skills/80-security/authorized-penetration-testing/SKILL.md instead.",
        ],
        prereqs=[
            "skills/80-security/authn-authz-hardening/SKILL.md for the security hardening checklist this pattern must satisfy.",
            "skills/80-security/secrets-and-key-management/SKILL.md for storing signing keys/secrets.",
            "An identity provider (e.g. OpenID Connect provider) issuing JWTs, or a plan to use one.",
        ],
        workflow=[
            ("Configure JWT bearer authentication", "Register AddAuthentication().AddJwtBearer with the issuer, audience, and signing key validation parameters."),
            ("Never hand-roll token validation", "Rely on the Microsoft.IdentityModel libraries' TokenValidationParameters rather than parsing/verifying JWTs manually."),
            ("Define authorization policies, not inline role checks", "Register named policies (e.g. 'CanManageOrders') combining role and claim requirements in one place."),
            ("Apply [Authorize(Policy = ...)] on endpoints", "Reference policies by name on controllers/minimal API endpoints instead of checking User.IsInRole inline."),
            ("Add resource-based authorization for ownership checks", "Use IAuthorizationHandler for rules like 'user can only edit their own order', evaluated against the loaded resource."),
            ("Keep claims minimal and purposeful", "Only include claims actually needed for authorization decisions in the token; avoid embedding excessive PII."),
            ("Test authorization policies in isolation", "Unit test each IAuthorizationHandler with different claim/resource combinations, independent of HTTP."),
        ],
        decision=[
            ("Access depends only on a fixed role", "Use a simple policy requiring that role claim (e.g. RequireRole(\"Admin\")) ."),
            ("Access depends on ownership of a specific resource", "Use a resource-based IAuthorizationHandler evaluated against the loaded entity, not just the token's claims."),
            ("Multiple endpoints share the same complex rule combination", "Extract it into one named policy so the rule is defined once and reused."),
            ("Feature access varies by subscription tier", "Combine a claim-based policy with skills/30-backend/configuration-and-feature-flags/SKILL.md rather than hardcoding tier checks."),
            ("Service-to-service calls need authorization", "Use client-credentials tokens with scope claims, checked via policies, rather than shared static API keys."),
        ],
        code_lang="csharp",
        code_intro="JWT bearer authentication and named authorization policies:",
        code=(
            "builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)\n"
            "    .AddJwtBearer(options =>\n"
            "    {\n"
            "        options.Authority = builder.Configuration[\"Auth:Authority\"];\n"
            "        options.Audience = builder.Configuration[\"Auth:Audience\"];\n"
            "        options.TokenValidationParameters = new TokenValidationParameters\n"
            "        {\n"
            "            ValidateIssuer = true,\n"
            "            ValidateAudience = true,\n"
            "            ValidateLifetime = true,\n"
            "            ClockSkew = TimeSpan.FromMinutes(1)\n"
            "        };\n"
            "    });\n"
            "\n"
            "builder.Services.AddAuthorizationBuilder()\n"
            "    .AddPolicy(\"CanManageOrders\", policy =>\n"
            "        policy.RequireRole(\"OrderManager\", \"Admin\"))\n"
            "    .AddPolicy(\"CanViewOwnOrder\", policy =>\n"
            "        policy.Requirements.Add(new OwnsResourceRequirement()));\n"
            "\n"
            "app.MapGet(\"/orders/{id}\", GetOrder).RequireAuthorization(\"CanViewOwnOrder\");\n"
        ),
        code_notes=[
            "ClockSkew is deliberately kept small (rather than the 5-minute default) to reduce the window an expired token remains accepted.",
            "Policies are named after the capability they grant ('CanManageOrders'), not the role, decoupling endpoint code from role names.",
        ],
        code2_heading="Resource-based authorization handler for ownership checks (C#)",
        code2=("csharp",
            "Enforcing that a user can only access their own order:",
            "public class OwnsResourceRequirement : IAuthorizationRequirement { }\n"
            "\n"
            "public class OwnsOrderHandler : AuthorizationHandler<OwnsResourceRequirement, Order>\n"
            "{\n"
            "    protected override Task HandleRequirementAsync(\n"
            "        AuthorizationHandlerContext context, OwnsResourceRequirement requirement, Order resource)\n"
            "    {\n"
            "        var userId = context.User.FindFirstValue(ClaimTypes.NameIdentifier);\n"
            "        if (resource.CustomerId.ToString() == userId || context.User.IsInRole(\"Admin\"))\n"
            "            context.Succeed(requirement);\n"
            "        return Task.CompletedTask;\n"
            "    }\n"
            "}\n"
        ),
        checklist=[
            "JWT validation uses the standard Microsoft.IdentityModel pipeline, not hand-rolled parsing.",
            "Authorization is expressed as named policies, not inline User.IsInRole checks scattered in controllers.",
            "Resource ownership is enforced via resource-based authorization handlers, not just role checks.",
            "Tokens include only the claims needed for authorization decisions.",
            "Authorization handlers are unit tested against multiple claim/resource combinations.",
            "Clock skew and token lifetime validation are explicitly configured, not left at insecure defaults.",
        ],
        antipatterns=[
            ("Role checks scattered in controllers", "if (User.IsInRole(\"Admin\")) checks duplicated across many actions instead of one named policy."),
            ("Hand-rolled JWT parsing", "Manually decoding and verifying JWT signatures instead of relying on the vetted TokenValidationParameters pipeline."),
            ("Claims-only ownership checks", "Trusting a customerId claim in the token for ownership instead of comparing against the actual loaded resource, allowing stale/forged claims to bypass checks."),
            ("Static shared API keys for service-to-service auth", "Using one long-lived shared secret for all internal service calls instead of scoped, short-lived credentials."),
            ("Overloaded JWTs", "Cramming full user profile/PII into JWT claims instead of keeping tokens minimal and fetching detail server-side when needed."),
        ],
        verification=[
            "Attempting to access another user's resource with a valid token for a different user returns 403, verified by an integration test.",
            "Expired or tampered tokens are rejected, verified by a negative test case.",
            "Every protected endpoint uses a named policy, confirmed by a code search for RequireAuthorization/[Authorize].",
            "Authorization handler unit tests cover both allow and deny paths for each policy.",
        ],
        references=[
            "skills/80-security/authn-authz-hardening/SKILL.md",
            "skills/80-security/secrets-and-key-management/SKILL.md",
            "Microsoft Learn — ASP.NET Core authorization policies.",
        ],
    ),
    dict(
        dir="30-backend", slug="background-jobs-and-messaging", category="backend",
        tags=["background-jobs", "messaging", "queues"],
        desc="Use when work must run outside the request/response cycle, such as scheduled jobs, retries, or asynchronous processing triggered by messages on a queue.",
        purpose=[
            "Not all work belongs inside an HTTP request: long-running tasks, scheduled jobs, and "
            "cross-service communication need durable background processing that survives restarts and "
            "handles failures gracefully. This skill covers structuring background jobs and message-driven "
            "processing in .NET using hosted services, a job scheduler, and a message broker.",
            "It emphasizes idempotency and reliable delivery, since background work is retried far more "
            "often than request/response calls and must tolerate at-least-once delivery semantics.",
        ],
        when_use=[
            "A use case involves work that shouldn't block the HTTP response (sending emails, generating reports).",
            "Work must run on a schedule (nightly reconciliation, cleanup jobs).",
            "Services need to communicate asynchronously via events rather than synchronous calls.",
        ],
        when_not=[
            "The work is fast and must complete before responding to the caller — do it synchronously in the request instead.",
            "You're designing the event schema itself — see skills/20-architecture/event-driven-architecture/SKILL.md first.",
        ],
        prereqs=[
            "skills/20-architecture/event-driven-architecture/SKILL.md for the messaging patterns underlying this skill.",
            "skills/20-architecture/resilience-patterns/SKILL.md for retry/backoff behavior of job processing.",
            "A message broker (e.g. RabbitMQ, Azure Service Bus) or job scheduling library (Hangfire, Quartz.NET) selected.",
        ],
        workflow=[
            ("Classify the work as scheduled, queued, or fire-and-forget", "Scheduled jobs run on a timer; queued jobs process messages from a broker; fire-and-forget defers non-critical work briefly."),
            ("Implement scheduled jobs as hosted services", "Use IHostedService/BackgroundService with a timer, or a scheduler like Hangfire for cron-style recurring jobs."),
            ("Implement message consumers as durable subscribers", "A consumer reads from a durable queue and acknowledges only after successful processing (at-least-once delivery)."),
            ("Design every handler to be idempotent", "Use a processed-message-id table or natural idempotency keys so re-delivery doesn't cause duplicate side effects."),
            ("Apply retry with backoff and a dead-letter queue", "Failed messages retry with exponential backoff a bounded number of times, then move to a dead-letter queue for investigation."),
            ("Emit domain events transactionally via the outbox pattern", "Write the event to an outbox table in the same transaction as the state change, then publish it asynchronously."),
            ("Monitor queue depth and failure rate", "Wire dead-letter queue size and processing failure rate into skills/60-devops/observability/SKILL.md dashboards and alerts."),
        ],
        decision=[
            ("Work must run at a fixed time daily", "Use a scheduled hosted job (Hangfire recurring job or Quartz.NET trigger)."),
            ("Work is triggered by another service's event", "Use a durable message consumer subscribed to that event, not polling."),
            ("A handler must not process the same message twice", "Store processed message IDs and check/skip on redelivery — assume at-least-once delivery always."),
            ("A state change must reliably trigger an event", "Use the transactional outbox pattern instead of publishing directly inside the same transaction as the DB write."),
            ("A message fails repeatedly", "Route it to a dead-letter queue after a bounded retry count rather than retrying indefinitely and blocking the queue."),
        ],
        code_lang="csharp",
        code_intro="An idempotent message consumer using an outbox-published event:",
        code=(
            "public class OrderPlacedConsumer : IConsumer<OrderPlacedEvent>\n"
            "{\n"
            "    private readonly IProcessedMessageStore _processed;\n"
            "    private readonly IEmailSender _email;\n"
            "\n"
            "    public async Task Consume(ConsumeContext<OrderPlacedEvent> context)\n"
            "    {\n"
            "        var messageId = context.MessageId?.ToString() ?? context.Message.OrderId.ToString();\n"
            "        if (await _processed.WasProcessedAsync(messageId, context.CancellationToken))\n"
            "            return; // already handled this delivery, safe to skip\n"
            "\n"
            "        await _email.SendOrderConfirmationAsync(context.Message.OrderId, context.CancellationToken);\n"
            "        await _processed.MarkProcessedAsync(messageId, context.CancellationToken);\n"
            "    }\n"
            "}\n"
        ),
        code_notes=[
            "Checking WasProcessedAsync first makes the consumer safe under at-least-once delivery, where the broker may redeliver on ack failure.",
            "MarkProcessedAsync should be committed atomically with any other state change the handler makes, ideally in one transaction.",
        ],
        code2_heading="Transactional outbox write alongside a state change (C#)",
        code2=("csharp",
            "Guaranteeing the event is never lost even if publishing fails immediately after commit:",
            "await using var tx = await _db.Database.BeginTransactionAsync(ct);\n"
            "order.Submit();\n"
            "_db.Outbox.Add(new OutboxMessage\n"
            "{\n"
            "    Id = Guid.NewGuid(),\n"
            "    Type = nameof(OrderPlacedEvent),\n"
            "    Payload = JsonSerializer.Serialize(new OrderPlacedEvent(order.Id)),\n"
            "    OccurredAt = DateTime.UtcNow\n"
            "});\n"
            "await _db.SaveChangesAsync(ct);\n"
            "await tx.CommitAsync(ct);\n"
            "// A separate background poller reads unpublished Outbox rows and publishes them to the broker.\n"
        ),
        checklist=[
            "Every message consumer is idempotent against redelivery, verified with a repeated-delivery test.",
            "Scheduled work uses a hosted service or scheduler library, not an ad hoc Thread.Sleep loop.",
            "State changes that must emit events use the transactional outbox pattern, not direct in-transaction publish.",
            "Failed messages retry with bounded exponential backoff, then land in a dead-letter queue.",
            "Queue depth and dead-letter counts are monitored with alerts, not just logs.",
            "Background job failures are logged with enough context to diagnose without reproducing manually.",
        ],
        antipatterns=[
            ("Publish-then-commit", "Publishing an event before committing the database transaction, risking a published event for a change that then fails to commit."),
            ("Non-idempotent consumers", "Assuming exactly-once delivery and performing non-idempotent side effects (e.g. charging a card twice) on redelivery."),
            ("Infinite retry with no dead-letter queue", "Retrying a poison message forever, blocking the queue and hiding the real error from anyone."),
            ("Thread.Sleep-based scheduling", "Implementing 'scheduled' jobs with an infinite loop and Task.Delay instead of a proper scheduler with observability and skip-if-still-running semantics."),
            ("Silent failure swallowing", "Catching and ignoring exceptions in a background job so failures never surface in logs or alerts."),
        ],
        verification=[
            "Redelivering the same message to a consumer twice produces no duplicate side effects, verified by an idempotency test.",
            "Killing the process mid-transaction never results in a published event without a corresponding committed state change.",
            "Dead-letter queue depth and failure-rate alerts are configured and tested to fire.",
            "A scheduled job's execution history is visible via logs/dashboard, not just inferred from side effects.",
        ],
        references=[
            "skills/20-architecture/event-driven-architecture/SKILL.md",
            "skills/20-architecture/resilience-patterns/SKILL.md",
            "skills/60-devops/observability/SKILL.md",
            "MassTransit / Hangfire documentation.",
        ],
    ),
]
