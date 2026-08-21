SKILLS = [
    dict(
        dir="20-architecture", slug="scalability-and-capacity-planning", category="architecture",
        tags=["scalability", "capacity-planning", "performance"],
        desc="Use when a system needs to handle growing load and you need to plan capacity, identify bottlenecks, and choose between scaling strategies before performance becomes a production incident.",
        purpose=[
            "Scaling problems discovered in production during a traffic spike are far more expensive to fix "
            "than ones planned for in advance. This skill provides a process for estimating expected load, "
            "identifying the likely first bottleneck, and choosing between vertical scaling, horizontal "
            "scaling, and architectural changes before they are urgently needed.",
            "It treats capacity planning as an ongoing practice tied to measured data, not a one-time "
            "estimate made at launch and never revisited.",
        ],
        when_use=[
            "You are launching a feature expected to see significant or rapidly growing traffic.",
            "A system is approaching known resource limits (CPU, memory, connections, DB IOPS).",
            "You need to justify an infrastructure investment or a scaling architecture change.",
            "A traffic spike (marketing campaign, seasonal event) is planned and capacity needs confirming.",
        ],
        when_not=[
            "Current and projected load is far below any known system limit with no growth signal.",
            "The system has no production traffic yet and no reasonable load estimate can be made — focus on launching first, then measure.",
        ],
        prereqs=[
            "Current or projected traffic numbers (requests/sec, data volume, concurrent users).",
            "Observability in place (skills/60-devops/observability/SKILL.md) to measure actual resource usage.",
            "Known limits of each component in the current architecture (DB connections, thread pools, etc.).",
        ],
        workflow=[
            ("Establish the load model", "Define expected requests/sec, data growth rate, and peak-to-average traffic ratio, based on real or comparable data."),
            ("Identify the first bottleneck", "Load test or model each tier (app, DB, cache, network) to find which one will saturate first at target load."),
            ("Choose scale-up vs scale-out for that bottleneck", "Vertical scaling for quick wins on stateful components; horizontal scaling for stateless components that can add instances."),
            ("Remove architectural bottlenecks if scaling alone won't work", "e.g. introduce caching, read replicas, or async processing if the bottleneck cannot be solved by adding more of the same resource."),
            ("Load test against the target, not just current load", "Test at 2-3x expected peak to leave headroom for unexpected spikes and future growth."),
            ("Plan for graceful degradation", "Define what happens when capacity is exceeded (queueing, load shedding, rate limiting) rather than an uncontrolled failure."),
            ("Set up autoscaling where applicable", "Configure autoscaling rules based on the metric that actually predicts saturation (not always CPU)."),
            ("Revisit capacity plans on a cadence", "Re-run the load model as real traffic data accumulates, not just once before launch."),
        ],
        decision=[
            ("Bottleneck is a stateless application tier", "Scale out horizontally with an autoscaling group behind a load balancer."),
            ("Bottleneck is a single relational database", "Scale up first for headroom; consider read replicas for read-heavy load or sharding as a last resort for write-heavy load."),
            ("Traffic is highly spiky (e.g. flash sales)", "Add a queue in front of the bottleneck to smooth bursts rather than sizing permanently for peak."),
            ("Autoscaling reacts too slowly to sudden spikes", "Pre-warm capacity ahead of known events (scheduled scale-out) rather than relying purely on reactive autoscaling."),
            ("A single component cannot scale further no matter what", "Consider skills/20-architecture/modular-monolith-vs-microservices/SKILL.md to isolate it for independent scaling."),
            ("The system approaches capacity but a full redesign is too slow", "Apply load shedding and graceful degradation as a stopgap while a longer-term fix is built."),
        ],
        code_lang="mermaid",
        code_intro="A capacity planning flow identifying the bottleneck before choosing a scaling strategy:",
        code=(
            "flowchart TD\n"
            "    Load[Estimate target load: req/s, data volume, peak ratio]\n"
            "    Load --> Test[Load test each tier at 2-3x target]\n"
            "    Test --> Bottleneck{First tier to saturate?}\n"
            "    Bottleneck -->|App tier| ScaleOut[Horizontal autoscaling]\n"
            "    Bottleneck -->|Database| DBPlan{Read or write heavy?}\n"
            "    DBPlan -->|Read heavy| ReadReplica[Add read replicas + caching]\n"
            "    DBPlan -->|Write heavy| Shard[Consider sharding / scale up]\n"
            "    Bottleneck -->|Network/3rd party| Queue[Add a buffering queue]\n"
        ),
        code_notes=[
            "Always re-run this flow after major traffic pattern shifts, not just once at launch.",
            "Load test at 2-3x expected peak to leave room for unplanned spikes and future growth.",
        ],
        code2_heading="A capacity worksheet example",
        code2=("text",
            "A simple worksheet used to justify a scaling decision with real numbers:",
            "Feature: Checkout API\n"
            "  Current peak: 150 req/s, DB CPU at 55% during peak\n"
            "  Projected peak in 6 months (30% MoM growth): ~550 req/s\n"
            "  Load test result at 550 req/s: DB CPU saturates at 95%, p95 latency 1.2s (SLO: 300ms)\n"
            "  Bottleneck: Database CPU, primarily from unindexed order-history query\n"
            "  Decision: add covering index (see indexing-and-query-optimization) + 1 read replica\n"
            "  Re-test result: DB CPU at 60% at 550 req/s, p95 latency 210ms — meets SLO with headroom\n"
        ),
        checklist=[
            "A concrete load model (req/s, data volume, peak ratio) exists, not a vague estimate.",
            "Load testing identified the specific first bottleneck, not a generic guess.",
            "The chosen scaling strategy matches the bottleneck type (stateless vs stateful, read vs write heavy).",
            "The system was tested at 2-3x expected peak, not just at current or exactly-projected load.",
            "Graceful degradation (queueing, load shedding, rate limiting) is defined for beyond-capacity scenarios.",
            "Autoscaling rules (if used) trigger on the metric that actually predicts saturation.",
            "The capacity plan is revisited periodically against real traffic data, not treated as one-time.",
        ],
        antipatterns=[
            ("Guessing instead of measuring", "Choosing a scaling strategy based on intuition rather than load testing and real traffic data."),
            ("Scaling the wrong tier", "Adding application servers when the database is the actual bottleneck, wasting cost with no improvement."),
            ("CPU-only autoscaling", "Scaling purely on CPU when the real constraint is connection pool exhaustion, queue depth, or memory."),
            ("No headroom", "Sizing exactly for today's projected peak with zero margin for estimation error or unplanned spikes."),
            ("Uncontrolled overload failure", "Having no load shedding or rate limiting, so exceeding capacity causes a cascading full outage instead of a controlled degradation."),
            ("One-time planning", "Doing a capacity plan once at launch and never revisiting it as real usage patterns diverge from the original estimate."),
        ],
        verification=[
            "A load test report exists showing measured behavior at 2-3x target load, with the bottleneck identified.",
            "The chosen scaling strategy was validated to resolve the measured bottleneck (re-test after the fix).",
            "A documented plan exists for behavior beyond capacity (what gets shed or queued first).",
            "Autoscaling (if configured) was tested to trigger correctly under a simulated load spike.",
        ],
        references=[
            "skills/50-database/indexing-and-query-optimization/SKILL.md",
            "skills/70-quality/performance-and-load-testing/SKILL.md",
            "skills/60-devops/cost-and-resource-optimization/SKILL.md",
            "Google SRE Book — capacity planning chapter.",
        ],
    ),
    dict(
        dir="20-architecture", slug="resilience-patterns", category="architecture",
        tags=["resilience", "fault-tolerance", "reliability"],
        desc="Use when a system depends on other services or resources that can fail or become slow, and you need to prevent those failures from cascading into a full outage.",
        purpose=[
            "In a distributed system, every network call is a potential failure point, and a naive "
            "implementation lets one slow or failing dependency cascade into an outage of the entire system. "
            "This skill covers the core resilience patterns — timeouts, retries, circuit breakers, "
            "bulkheads, and fallbacks — and when to apply each.",
            "The goal is graceful degradation: a partial failure should cause a partial, contained impact, "
            "not a total outage.",
        ],
        when_use=[
            "A service calls another service, database, or third-party API over the network.",
            "A dependency has occasionally been slow, flaky, or unavailable in the past.",
            "You need to protect a system from cascading failure when one dependency degrades.",
            "You are designing SLOs and need to define acceptable degraded-mode behavior.",
        ],
        when_not=[
            "The call is to a fully in-process, in-memory component with no network or I/O involved.",
            "Adding resilience patterns to a genuinely non-critical, best-effort call adds more complexity than value.",
        ],
        prereqs=[
            "A resilience library available for the stack (e.g. Polly for .NET).",
            "Known SLAs/SLOs for the calling service and its dependencies.",
            "skills/60-devops/observability/SKILL.md to detect when patterns are actually triggering.",
        ],
        workflow=[
            ("Set explicit timeouts on every external call", "Never rely on default/infinite timeouts; choose a value based on the caller's own latency budget."),
            ("Add retries with backoff for transient failures", "Retry only on errors known to be transient (timeouts, 5xx, connection resets), with exponential backoff and jitter."),
            ("Add a circuit breaker for repeated failures", "Stop calling a consistently failing dependency for a cool-down period instead of retrying into an outage."),
            ("Isolate failures with bulkheads", "Use separate connection pools/thread pools per dependency so one slow dependency cannot exhaust resources needed by others."),
            ("Define a fallback for degraded mode", "Decide what to return when a dependency is unavailable: cached data, a default value, or an explicit degraded response."),
            ("Make retries idempotent-safe", "Confirm the operation being retried is safe to execute more than once, or use an idempotency key."),
            ("Combine patterns deliberately", "Layer timeout, retry, and circuit breaker together (timeout inside retry inside circuit breaker) rather than picking just one."),
            ("Observe and alert on pattern activation", "Track circuit breaker trips, retry counts, and fallback usage as signals of dependency health."),
        ],
        decision=[
            ("Dependency call fails with a client error (4xx)", "Do not retry — it will fail identically; treat as a non-transient failure."),
            ("Dependency call times out or returns 5xx", "Retry a bounded number of times with exponential backoff and jitter."),
            ("Dependency has been failing repeatedly for the last N requests", "Open the circuit breaker to fail fast and give the dependency time to recover."),
            ("A slow dependency risks exhausting a shared thread/connection pool", "Isolate it in its own bulkhead so other calls are unaffected."),
            ("A degraded dependency has no safe fallback value", "Return an explicit, clearly-labeled degraded response rather than pretending the request succeeded fully."),
            ("An operation is not naturally idempotent", "Add an idempotency key before enabling retries, or do not retry it."),
        ],
        code_lang="mermaid",
        code_intro="Layered resilience patterns applied to a single outbound call:",
        code=(
            "flowchart LR\n"
            "    Caller[Caller] --> CB{Circuit Breaker}\n"
            "    CB -->|closed| Retry[Retry w/ backoff]\n"
            "    CB -->|open| Fallback[Return cached/default response]\n"
            "    Retry --> Timeout[Timeout-bounded call]\n"
            "    Timeout --> Dep[(Downstream Dependency)]\n"
            "    Dep -->|success| Caller\n"
            "    Dep -->|repeated failure| CB\n"
        ),
        code_notes=[
            "The circuit breaker wraps the retry policy, not the other way around — otherwise retries can keep the circuit artificially 'closed' by masking failures.",
            "Fallback responses should be clearly distinguishable (e.g. a flag in the response) so consumers know they got degraded data.",
        ],
        code2_heading="Combined timeout, retry, and circuit breaker with Polly (C#)",
        code2=("csharp",
            "A realistic resilience pipeline for an HttpClient call to a downstream service:",
            "var retryPolicy = Policy\n"
            "    .Handle<HttpRequestException>()\n"
            "    .OrResult<HttpResponseMessage>(r => (int)r.StatusCode >= 500)\n"
            "    .WaitAndRetryAsync(3, attempt =>\n"
            "        TimeSpan.FromMilliseconds(200 * Math.Pow(2, attempt)) +\n"
            "        TimeSpan.FromMilliseconds(Random.Shared.Next(0, 100)));\n"
            "\n"
            "var circuitBreaker = Policy\n"
            "    .Handle<HttpRequestException>()\n"
            "    .CircuitBreakerAsync(handledEventsAllowedBeforeBreaking: 5,\n"
            "        durationOfBreak: TimeSpan.FromSeconds(30));\n"
            "\n"
            "var timeout = Policy.TimeoutAsync(TimeSpan.FromSeconds(2));\n"
            "\n"
            "var pipeline = Policy.WrapAsync(circuitBreaker, retryPolicy, timeout);\n"
            "\n"
            "var response = await pipeline.ExecuteAsync(() => httpClient.GetAsync(\"/pricing\"));\n"
        ),
        checklist=[
            "Every external call has an explicit, deliberately chosen timeout.",
            "Retries only apply to genuinely transient failures, with exponential backoff and jitter.",
            "A circuit breaker protects against repeatedly calling a consistently failing dependency.",
            "Bulkheads isolate resource pools so one slow dependency cannot starve unrelated calls.",
            "A defined fallback exists for degraded mode, clearly distinguishable from a full success.",
            "Retried operations are confirmed idempotent or protected with an idempotency key.",
            "Circuit breaker trips and fallback usage are visible on dashboards with alerting.",
        ],
        antipatterns=[
            ("No timeout", "Making a network call with no timeout, letting a hung dependency exhaust the caller's own resources indefinitely."),
            ("Retrying non-transient errors", "Retrying 4xx client errors or business validation failures that will fail identically every time."),
            ("Retry storms", "Retrying without backoff/jitter, causing synchronized retry spikes that make a struggling dependency's outage worse."),
            ("No circuit breaker", "Continuing to hammer a known-down dependency with new requests instead of failing fast during an outage."),
            ("Shared resource pools across dependencies", "One slow dependency exhausting a shared connection/thread pool, taking down calls to unrelated, healthy dependencies."),
            ("Silent degraded responses", "Returning stale/fallback data without any indication to the caller that it is not the full, live result."),
        ],
        verification=[
            "A simulated dependency timeout confirms the caller fails fast at the configured timeout, not indefinitely.",
            "A simulated string of failures confirms the circuit breaker opens and stops calling the dependency.",
            "A load test with one dependency artificially slowed confirms other dependencies remain unaffected (bulkhead isolation).",
            "Retried write operations were confirmed idempotent via a test that executes them twice.",
        ],
        references=[
            "Michael Nygard, 'Release It!' — circuit breaker and bulkhead patterns.",
            "Polly documentation (.NET resilience library).",
            "skills/60-devops/observability/SKILL.md",
            "skills/20-architecture/scalability-and-capacity-planning/SKILL.md",
        ],
    ),
    dict(
        dir="20-architecture", slug="multi-tenancy-design", category="architecture",
        tags=["multi-tenancy", "isolation", "saas"],
        desc="Use when building a SaaS system that serves multiple customers (tenants) from shared infrastructure and you need to choose a tenancy model that balances isolation, cost, and operational complexity.",
        purpose=[
            "Multi-tenant systems must balance per-tenant data isolation, cost efficiency of shared "
            "infrastructure, and the operational burden of managing many tenants. Choosing the wrong "
            "tenancy model early is expensive to change later, especially once customer data is commingled "
            "or contractually isolated tenants need separating out.",
            "This skill covers the three common tenancy models — shared schema, schema-per-tenant, and "
            "database-per-tenant — and how to enforce tenant isolation correctly regardless of which is "
            "chosen.",
        ],
        when_use=[
            "You are designing a new SaaS product that will serve multiple customer organizations.",
            "An existing single-tenant system needs to become multi-tenant.",
            "A customer requires contractual data isolation (dedicated infrastructure) beyond the platform default.",
            "You are debugging a tenant data isolation or cross-tenant leakage concern.",
        ],
        when_not=[
            "The system will only ever serve a single customer/organization.",
            "Tenants are so few and so large that dedicated infrastructure per tenant is clearly simpler and required anyway.",
        ],
        prereqs=[
            "Confirmed tenant model: how tenants are identified (subdomain, header, claim) at request time.",
            "skills/30-backend/authentication-and-authorization/SKILL.md for tenant-aware authorization.",
            "Compliance/contractual requirements for tenant isolation, if any.",
        ],
        workflow=[
            ("Choose the tenancy model deliberately", "Shared schema (row-level tenant ID) for cost efficiency at scale; schema/database-per-tenant for stronger isolation or compliance needs."),
            ("Establish tenant context early in the request pipeline", "Resolve the tenant ID from the request (subdomain, header, JWT claim) in middleware, before any business logic runs."),
            ("Enforce tenant isolation at the data layer", "Apply a mandatory tenant filter on every query — ideally enforced structurally, not left to each query author's discipline."),
            ("Isolate noisy-neighbor resource usage", "Apply per-tenant rate limits or resource quotas so one tenant cannot degrade service for others."),
            ("Plan for tenant-specific configuration", "Support per-tenant feature flags, branding, or limits without duplicating core application logic."),
            ("Support tenant lifecycle operations", "Design explicit provisioning, offboarding, and data export/deletion flows per tenant from the start."),
            ("Test cross-tenant isolation explicitly", "Write automated tests that assert tenant A can never see or modify tenant B's data."),
        ],
        decision=[
            ("Many small tenants, cost efficiency matters most", "Use a shared schema with a mandatory tenant_id column and row-level enforcement."),
            ("Few large tenants with strict compliance/isolation needs", "Use database-per-tenant (or schema-per-tenant) for stronger physical isolation."),
            ("A specific enterprise customer contractually requires dedicated infrastructure", "Provision database-per-tenant just for that tenant while others remain on shared schema."),
            ("Tenant ID is only checked in application code, not enforced at the data layer", "Add a structural enforcement mechanism (e.g. row-level security, or a base repository that always injects the filter) instead of relying on every developer remembering."),
            ("A tenant needs to be fully offboarded and data deleted", "Ensure the tenancy model supports clean, verifiable deletion of exactly that tenant's data."),
            ("One tenant's usage spikes and affects others", "Apply per-tenant rate limiting/quotas rather than a single global limit."),
        ],
        code_lang="mermaid",
        code_intro="Tenant context resolution and enforcement flow for a shared-schema model:",
        code=(
            "flowchart TB\n"
            "    Req[Incoming Request] --> MW[Tenant Resolution Middleware]\n"
            "    MW -->|resolves TenantId from subdomain/JWT| Ctx[(ITenantContext)]\n"
            "    Ctx --> Repo[Base Repository]\n"
            "    Repo -->|auto-applies WHERE tenant_id = @TenantId| DB[(Shared Database)]\n"
            "    Ctx --> RateLimit[Per-tenant rate limiter]\n"
        ),
        code_notes=[
            "Resolving tenant context in middleware ensures no code path can accidentally run without a known tenant.",
            "Auto-applying the tenant filter at the repository base class removes reliance on every query author remembering it.",
        ],
        code2_heading="Enforcing tenant isolation at the EF Core query level (C#)",
        code2=("csharp",
            "A global query filter that makes forgetting the tenant_id filter structurally impossible:",
            "public class AppDbContext : DbContext\n"
            "{\n"
            "    private readonly ITenantContext _tenant;\n"
            "    public AppDbContext(DbContextOptions options, ITenantContext tenant)\n"
            "        : base(options) => _tenant = tenant;\n"
            "\n"
            "    public DbSet<Order> Orders => Set<Order>();\n"
            "\n"
            "    protected override void OnModelCreating(ModelBuilder modelBuilder)\n"
            "    {\n"
            "        modelBuilder.Entity<Order>()\n"
            "            .HasQueryFilter(o => o.TenantId == _tenant.TenantId);\n"
            "    }\n"
            "\n"
            "    public override int SaveChanges()\n"
            "    {\n"
            "        foreach (var entry in ChangeTracker.Entries<ITenantScoped>()\n"
            "                     .Where(e => e.State == EntityState.Added))\n"
            "            entry.Entity.TenantId = _tenant.TenantId;\n"
            "        return base.SaveChanges();\n"
            "    }\n"
            "}\n"
        ),
        checklist=[
            "A tenancy model was chosen deliberately based on isolation, cost, and compliance needs.",
            "Tenant context is resolved once, early in the request pipeline, not re-derived ad hoc in each handler.",
            "Tenant isolation is enforced structurally at the data layer, not left to per-query discipline.",
            "Per-tenant rate limits or quotas prevent one tenant from degrading others (noisy neighbor).",
            "Tenant provisioning, offboarding, and data export/deletion flows are explicitly designed.",
            "Automated tests assert that one tenant cannot read or write another tenant's data.",
            "A path exists to move a specific tenant to dedicated infrastructure if contractually required.",
        ],
        antipatterns=[
            ("Manual tenant filtering", "Relying on every developer to remember to add WHERE tenant_id = ... to every query, guaranteeing an eventual leak."),
            ("Tenant ID from an unverified source", "Trusting a tenant ID passed in a request body or unsigned header instead of deriving it from an authenticated identity/claim."),
            ("No noisy-neighbor protection", "Letting one tenant's traffic spike degrade performance for all other tenants with no per-tenant limits."),
            ("No offboarding plan", "Building a multi-tenant system with no way to cleanly and verifiably delete a single tenant's data on request."),
            ("Untested isolation", "Never writing an automated test that actively tries to access another tenant's data and confirms it fails."),
            ("One-size-fits-all infrastructure", "Refusing to ever support dedicated infrastructure for a tenant, even when a contract requires it, forcing an awkward workaround."),
        ],
        verification=[
            "An automated test using tenant A's credentials attempting to access tenant B's data fails as expected.",
            "A code review or static check confirms every tenant-scoped table has structural (not just conventional) tenant filtering.",
            "A per-tenant load test confirms one tenant's spike does not measurably degrade another tenant's latency.",
            "A tenant offboarding run in a test environment confirms all of that tenant's data is fully and verifiably removed.",
        ],
        references=[
            "skills/30-backend/authentication-and-authorization/SKILL.md",
            "skills/50-database/relational-data-modeling/SKILL.md",
            "Microsoft Azure Architecture Center — multi-tenant SaaS patterns.",
            "skills/80-security/privacy-and-compliance-basics/SKILL.md",
        ],
    ),
]
