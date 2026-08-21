SKILLS = [
    dict(
        dir="30-backend", slug="realtime-signalr-and-grpc", category="backend",
        tags=["signalr", "grpc", "realtime"],
        desc="Use when a feature needs server-push updates to clients or high-throughput internal service-to-service calls and you must choose between SignalR and gRPC.",
        purpose=[
            "REST over HTTP is poorly suited to two common needs: pushing live updates to browser clients, "
            "and high-throughput, strongly-typed internal service calls. SignalR provides real-time "
            "server-to-client messaging over WebSockets with fallback transports, while gRPC provides "
            "efficient, strongly-typed, bidirectional streaming for service-to-service communication.",
            "This skill covers choosing between them correctly and structuring each so they don't become "
            "brittle, hard-to-scale additions to the architecture.",
        ],
        when_use=[
            "A UI needs live updates (notifications, live dashboards, chat) without polling.",
            "Two internal services need high-throughput, low-latency, strongly-typed calls, potentially with streaming.",
            "You are deciding between REST, SignalR, and gRPC for a new communication requirement.",
        ],
        when_not=[
            "A simple request/response REST call would suffice — see skills/20-architecture/api-design-rest/SKILL.md instead.",
            "The client is a public third-party integrator that expects a standard REST/GraphQL contract, not gRPC or SignalR-specific protocols.",
        ],
        prereqs=[
            "skills/20-architecture/api-design-graphql-and-grpc/SKILL.md for gRPC contract design fundamentals.",
            "skills/20-architecture/resilience-patterns/SKILL.md for reconnect/backoff behavior.",
            "A load balancer/proxy that supports HTTP/2 and WebSockets if scaling beyond one instance.",
        ],
        workflow=[
            ("Identify the communication shape needed", "Server-push to many browser clients suggests SignalR; internal high-throughput RPC suggests gRPC."),
            ("For SignalR, design hubs around a small set of client-facing operations", "Keep hub methods thin, delegating real logic to the Application layer via MediatR."),
            ("Use groups for targeted broadcasting", "Add connections to groups (e.g. per-order, per-tenant) rather than broadcasting every update to every connected client."),
            ("Configure a backplane for multi-instance SignalR", "Use Redis or Azure SignalR Service as a backplane so messages reach clients connected to any instance."),
            ("For gRPC, define contracts in .proto files first", "Treat the .proto file as the source of truth, generating both client and server stubs from it."),
            ("Use gRPC streaming only when genuinely needed", "Prefer unary calls unless the use case truly needs client, server, or bidirectional streaming."),
            ("Plan reconnect and backoff on the client for both", "SignalR's automatic reconnect and gRPC client retry policies should be configured explicitly, not left at defaults."),
        ],
        decision=[
            ("Browser needs live order status updates", "Use SignalR with a per-order group, pushed from the Application layer after a domain event."),
            ("Two internal microservices need a low-latency RPC call", "Use gRPC with a well-defined .proto contract."),
            ("A public third-party API is being exposed", "Use REST/GraphQL, not gRPC or SignalR, for broad client compatibility."),
            ("SignalR needs to scale beyond one instance", "Add a backplane (Redis or Azure SignalR Service) before scaling out, or messages will only reach clients on the same instance."),
            ("A gRPC call needs a stream of continuously changing data", "Use server streaming; reserve bidirectional streaming for genuinely two-way continuous exchanges."),
        ],
        code_lang="csharp",
        code_intro="A thin SignalR hub delegating to the Application layer, broadcasting to a per-order group:",
        code=(
            "public class OrderStatusHub : Hub\n"
            "{\n"
            "    public async Task JoinOrderGroup(string orderId) =>\n"
            "        await Groups.AddToGroupAsync(Context.ConnectionId, $\"order-{orderId}\");\n"
            "}\n"
            "\n"
            "// Called from an Application-layer event handler after OrderStatusChanged:\n"
            "public class OrderStatusNotifier : INotificationHandler<OrderStatusChangedEvent>\n"
            "{\n"
            "    private readonly IHubContext<OrderStatusHub> _hub;\n"
            "    public OrderStatusNotifier(IHubContext<OrderStatusHub> hub) => _hub = hub;\n"
            "\n"
            "    public Task Handle(OrderStatusChangedEvent e, CancellationToken ct) =>\n"
            "        _hub.Clients.Group($\"order-{e.OrderId}\")\n"
            "            .SendAsync(\"orderStatusChanged\", new { e.OrderId, e.NewStatus }, ct);\n"
            "}\n"
        ),
        code_notes=[
            "The hub itself contains no business logic; notifications originate from domain event handlers in the Application layer.",
            "Group naming ($\"order-{orderId}\") ensures only clients watching that specific order receive the update.",
        ],
        code2_heading="A gRPC service contract and minimal implementation (proto + C#)",
        code2=("protobuf",
            "Contract-first gRPC definition, with the server implementation delegating to Application handlers:",
            "service InventoryService {\n"
            "  rpc ReserveStock (ReserveStockRequest) returns (ReserveStockReply);\n"
            "}\n"
            "message ReserveStockRequest { string product_id = 1; int32 quantity = 2; }\n"
            "message ReserveStockReply { bool reserved = 1; int32 remaining = 2; }\n"
            "\n"
            "// C# server implementation\n"
            "public override async Task<ReserveStockReply> ReserveStock(\n"
            "    ReserveStockRequest request, ServerCallContext context)\n"
            "{\n"
            "    var result = await _mediator.Send(new ReserveStockCommand(\n"
            "        request.ProductId, request.Quantity), context.CancellationToken);\n"
            "    return new ReserveStockReply { Reserved = result.Reserved, Remaining = result.Remaining };\n"
            "}\n"
        ),
        checklist=[
            "The communication shape (push vs RPC) was deliberately chosen, not defaulted to whatever was easiest.",
            "SignalR hubs are thin and delegate business logic to the Application layer.",
            "Broadcasts use targeted groups, not all-clients broadcast, where only a subset should receive updates.",
            "A backplane is configured for SignalR if the service scales to more than one instance.",
            "gRPC contracts are defined in .proto files as the source of truth for both client and server.",
            "Streaming is used only where the use case genuinely requires it, not as a default choice.",
        ],
        antipatterns=[
            ("Broadcasting to all clients", "Sending every update to every connected SignalR client instead of scoping via groups, wasting bandwidth and leaking data across tenants."),
            ("Business logic inside the hub", "Implementing domain rules directly in a SignalR Hub class instead of delegating to the Application layer."),
            ("No backplane at scale", "Deploying SignalR across multiple instances without a backplane, causing clients on different instances to miss messages."),
            ("gRPC for public third-party APIs", "Exposing gRPC as the only interface for external partner integrations that expect standard REST/GraphQL."),
            ("Streaming used unnecessarily", "Defaulting to bidirectional streaming for what is really a simple unary request/response, adding needless complexity."),
        ],
        verification=[
            "A load test with multiple instances confirms SignalR messages reach clients connected to any instance (backplane works).",
            "Hub methods contain no direct business logic, confirmed by code review.",
            "gRPC contract changes go through .proto review before server/client code is regenerated.",
            "Reconnect/backoff behavior is exercised in a test that simulates a dropped connection.",
        ],
        references=[
            "skills/20-architecture/api-design-graphql-and-grpc/SKILL.md",
            "skills/20-architecture/resilience-patterns/SKILL.md",
            "Microsoft Learn — ASP.NET Core SignalR and gRPC documentation.",
        ],
    ),
    dict(
        dir="30-backend", slug="object-mapping-and-dtos", category="backend",
        tags=["dto", "mapping", "api-contracts"],
        desc="Use when deciding how domain entities are translated to and from API request/response contracts without leaking internal model details.",
        purpose=[
            "Returning domain entities directly from API endpoints couples the wire contract to internal "
            "implementation details and risks leaking fields that were never meant to be public. This skill "
            "establishes explicit DTOs for every API boundary and a consistent, low-overhead mapping strategy "
            "between domain models and those DTOs.",
            "It also covers when to hand-write mapping versus using a mapping library, since generated mapping "
            "code can hide bugs when domain and DTO shapes diverge silently.",
        ],
        when_use=[
            "You are defining request/response contracts for a new API endpoint.",
            "Domain entities are currently being serialized directly as API responses.",
            "Mapping code between layers has become repetitive and error-prone.",
        ],
        when_not=[
            "The DTO and domain shapes are identical and trivial (e.g. a single value lookup) — a direct return may be acceptable if reviewed carefully.",
            "You're inside a single layer (e.g. Domain to Domain) where no contract boundary is being crossed.",
        ],
        prereqs=[
            "skills/20-architecture/clean-and-onion-architecture/SKILL.md for where DTOs live (Application/Api boundary).",
            "skills/20-architecture/api-design-rest/SKILL.md for the contract shape DTOs should follow.",
        ],
        workflow=[
            ("Define a DTO for every request and response shape", "Never serialize a domain entity or EF Core entity directly as an API response."),
            ("Keep DTOs flat and purpose-built per endpoint", "Avoid one giant shared DTO reused everywhere; a list view and a detail view usually need different shapes."),
            ("Map explicitly for anything with business logic in the translation", "Hand-write mapping code when field names differ meaningfully or computed values are involved."),
            ("Use a mapping library for simple, high-volume 1:1 mappings", "Mapperly or AutoMapper can reduce boilerplate for straightforward property-to-property mapping, with generated mappings reviewed."),
            ("Never map DTOs back into domain entities directly", "Reconstruct or mutate domain entities via factory methods/domain methods, not by assigning DTO fields onto them."),
            ("Version DTOs deliberately when contracts must change", "Add new fields as optional or introduce a new versioned DTO rather than silently changing meaning of existing fields."),
            ("Unit test mapping logic for anything non-trivial", "Any mapping involving computed fields or conditional logic gets a direct unit test."),
        ],
        decision=[
            ("Endpoint returns a simple 1:1 shape of an entity", "A source-generated mapper (e.g. Mapperly) is fine, keeping mapping code minimal."),
            ("Mapping involves computed or conditional fields", "Hand-write the mapping method explicitly so the logic is visible and testable, not hidden in library conventions."),
            ("Command input DTO needs to become a domain aggregate", "Use a domain factory method (Order.Create(...)) rather than assigning DTO properties onto a new entity instance directly."),
            ("Different clients need different views of the same entity", "Define separate DTOs per client need (e.g. OrderSummaryDto vs OrderDetailDto) instead of one bloated shared DTO."),
            ("A mapping library's generated code silently ignores a new domain field", "Treat this as a bug signal — add an explicit test asserting every expected field is mapped."),
        ],
        code_lang="csharp",
        code_intro="Explicit mapping from a domain aggregate to a response DTO:",
        code=(
            "public record OrderDetailDto(\n"
            "    Guid Id,\n"
            "    string Status,\n"
            "    decimal Total,\n"
            "    IReadOnlyList<OrderLineDto> Lines);\n"
            "\n"
            "public record OrderLineDto(string ProductName, int Quantity, decimal UnitPrice);\n"
            "\n"
            "public static class OrderMappingExtensions\n"
            "{\n"
            "    public static OrderDetailDto ToDetailDto(this Order order) => new(\n"
            "        order.Id,\n"
            "        order.Status.ToString(),\n"
            "        order.Lines.Sum(l => l.UnitPrice * l.Quantity),\n"
            "        order.Lines.Select(l => new OrderLineDto(\n"
            "            l.ProductName, l.Quantity, l.UnitPrice)).ToList());\n"
            "}\n"
        ),
        code_notes=[
            "Total is computed during mapping rather than stored redundantly on the entity, keeping the domain model the single source of truth.",
            "Extension methods keep mapping colocated with the DTO definitions, easy to find and test.",
        ],
        code2_heading="Source-generated mapping for simple 1:1 shapes (Mapperly, C#)",
        code2=("csharp",
            "Reducing boilerplate for straightforward property mapping, with compile-time-checked output:",
            "[Mapper]\n"
            "public partial class ProductMapper\n"
            "{\n"
            "    public partial ProductSummaryDto ToDto(Product product);\n"
            "}\n"
            "\n"
            "// Generated at compile time; a build warning surfaces if a Product property\n"
            "// has no corresponding DTO property, catching silent drift early.\n"
        ),
        checklist=[
            "No domain or EF Core entity is serialized directly as an API response.",
            "DTOs are purpose-built per endpoint rather than one shared bloated shape.",
            "Mapping involving computed or conditional logic is hand-written and unit tested.",
            "Domain entities are constructed/mutated via factory or domain methods, never by direct DTO field assignment.",
            "Mapping libraries used for simple cases have generated output reviewed, or compile-time warnings enabled for unmapped fields.",
            "DTO contract changes are additive or explicitly versioned, not silently breaking.",
        ],
        antipatterns=[
            ("Serializing entities directly", "Returning an EF Core tracked entity directly from a controller action, leaking navigation properties and internal fields."),
            ("God DTO", "One giant DTO reused across list, detail, and edit endpoints, forcing clients to handle irrelevant null fields."),
            ("DTO fields assigned onto domain entities", "Bypassing domain factory/methods by setting entity properties directly from an incoming DTO, skipping invariant checks."),
            ("Silent mapping drift", "A mapping library silently ignoring a newly added domain field with no build warning or test catching the gap."),
            ("Breaking DTO changes without versioning", "Renaming or repurposing an existing response field in place, breaking existing API consumers without notice."),
        ],
        verification=[
            "A code search confirms no controller/endpoint returns a domain or EF Core entity type directly.",
            "Unit tests exist for every mapping method containing computed or conditional logic.",
            "Adding a new domain field either produces a build warning (generated mapping) or requires an explicit DTO/mapping update (hand-written).",
            "API contract changes are reviewed against skills/20-architecture/api-design-rest/SKILL.md versioning guidance before merging.",
        ],
        references=[
            "skills/20-architecture/api-design-rest/SKILL.md",
            "skills/20-architecture/clean-and-onion-architecture/SKILL.md",
            "Mapperly / AutoMapper documentation.",
        ],
    ),
    dict(
        dir="30-backend", slug="configuration-and-feature-flags", category="backend",
        tags=["configuration", "feature-flags", "options-pattern"],
        desc="Use when a service needs environment-specific configuration or the ability to toggle features safely without a full redeploy.",
        purpose=[
            "Hardcoded configuration values and ad hoc environment checks scattered through code make services "
            "fragile to deploy and risky to change behavior in production. This skill establishes the .NET "
            "Options pattern for strongly-typed, validated configuration, plus a feature flag strategy for "
            "toggling behavior safely without redeploying.",
            "It distinguishes static configuration (connection strings, timeouts) from dynamic feature flags "
            "(gradual rollouts, kill switches), since they have different lifecycles and risk profiles.",
        ],
        when_use=[
            "A service needs configuration values that differ across environments (dev, staging, production).",
            "You need to roll out a new feature gradually or be able to disable it instantly without a deploy.",
            "Configuration values are currently read via raw IConfiguration string lookups scattered through the codebase.",
        ],
        when_not=[
            "The value never changes and is truly a compile-time constant (e.g. a fixed business rule threshold) — a flag adds needless indirection.",
            "You're storing secrets — use skills/80-security/secrets-and-key-management/SKILL.md instead of plain configuration.",
        ],
        prereqs=[
            "skills/80-security/secrets-and-key-management/SKILL.md for secret values that must never live in plain configuration.",
            "A feature flag provider selected (e.g. a hosted service or a simple database-backed flag store) if dynamic flags are needed.",
        ],
        workflow=[
            ("Define strongly-typed options classes", "One class per logical configuration section (e.g. EmailOptions), bound via IOptions<T>."),
            ("Validate configuration at startup", "Use IValidateOptions<T> or data annotations so missing/invalid configuration fails fast at startup, not at first use."),
            ("Never read raw configuration strings in business logic", "Inject IOptions<T> (or IOptionsSnapshot<T> for values that change without restart), not IConfiguration directly, into handlers."),
            ("Separate static config from dynamic feature flags", "Static settings live in appsettings/environment variables; flags that change at runtime live in a feature flag store."),
            ("Use feature flags for gradual rollout and kill switches", "Wrap new/risky functionality behind a flag so it can be disabled instantly without a redeploy."),
            ("Scope flags to the right audience", "Support percentage rollout, per-tenant, or per-user targeting rather than a single global on/off switch when a gradual rollout is needed."),
            ("Remove stale flags after full rollout", "Once a feature is fully rolled out and stable, delete the flag and the old code path to avoid permanent branching complexity."),
        ],
        decision=[
            ("A value differs only by environment (timeout, base URL)", "Use the Options pattern bound from appsettings.{Environment}.json or environment variables."),
            ("A new feature needs to be tested with a subset of users first", "Use a feature flag with percentage or per-tenant targeting."),
            ("A risky feature needs an instant kill switch in production", "Wrap it in a feature flag checked at the point of use, not just at startup."),
            ("A flag has been fully rolled out for months", "Remove the flag and the old code path; don't let flags accumulate indefinitely."),
            ("A configuration value is actually a secret", "Move it to skills/80-security/secrets-and-key-management/SKILL.md's secret store, never plain appsettings.json."),
        ],
        code_lang="csharp",
        code_intro="Strongly-typed, validated options bound and consumed via DI:",
        code=(
            "public class EmailOptions\n"
            "{\n"
            "    public const string SectionName = \"Email\";\n"
            "    [Required] public string SenderAddress { get; set; } = default!;\n"
            "    [Range(1, 300)] public int TimeoutSeconds { get; set; } = 30;\n"
            "}\n"
            "\n"
            "builder.Services.AddOptions<EmailOptions>()\n"
            "    .Bind(builder.Configuration.GetSection(EmailOptions.SectionName))\n"
            "    .ValidateDataAnnotations()\n"
            "    .ValidateOnStart();\n"
            "\n"
            "public class EmailSender\n"
            "{\n"
            "    private readonly EmailOptions _options;\n"
            "    public EmailSender(IOptions<EmailOptions> options) => _options = options.Value;\n"
            "\n"
            "    public Task SendAsync(string to, string subject) =>\n"
            "        SendViaSmtpAsync(_options.SenderAddress, to, subject, _options.TimeoutSeconds);\n"
            "}\n"
        ),
        code_notes=[
            "ValidateOnStart() makes a missing SenderAddress fail the app at startup instead of at the first email send attempt.",
            "IOptions<T> is a singleton snapshot; use IOptionsSnapshot<T> instead if the value must refresh without an app restart.",
        ],
        code2_heading="A feature flag guarding a risky new code path (C#)",
        code2=("csharp",
            "Checked at the point of use so it can be disabled instantly without a redeploy:",
            "public class CheckoutService\n"
            "{\n"
            "    private readonly IFeatureManager _features;\n"
            "\n"
            "    public async Task<CheckoutResult> CheckoutAsync(Cart cart, CancellationToken ct)\n"
            "    {\n"
            "        if (await _features.IsEnabledAsync(\"NewPricingEngine\", ct))\n"
            "            return await _newPricingEngine.CheckoutAsync(cart, ct);\n"
            "        return await _legacyPricingEngine.CheckoutAsync(cart, ct);\n"
            "    }\n"
            "}\n"
        ),
        checklist=[
            "Configuration is bound to strongly-typed options classes, not read via raw IConfiguration string keys in business logic.",
            "Required configuration is validated at startup with ValidateOnStart, failing fast rather than at first use.",
            "Secrets are never stored in plain appsettings.json, only in the designated secret store.",
            "Risky or gradually-rolled-out features are wrapped in a feature flag checked at the point of use.",
            "Flags support the targeting granularity actually needed (global, percentage, per-tenant).",
            "Fully rolled-out flags and their old code paths are removed rather than accumulating indefinitely.",
        ],
        antipatterns=[
            ("Raw IConfiguration everywhere", "Reading configuration.GetValue<string>(\"Email:SenderAddress\") scattered through business logic instead of one bound options class."),
            ("Secrets in appsettings.json", "Committing connection strings or API keys into source-controlled configuration files instead of a secret store."),
            ("Global-only flags", "Only supporting a single on/off flag with no targeting, forcing all-or-nothing rollouts for risky changes."),
            ("Flags that never get removed", "Leaving fully-rolled-out feature flags in code indefinitely, accumulating dead branches and testing burden."),
            ("Silent misconfiguration", "Letting a missing required configuration value fail deep inside business logic at runtime instead of at startup."),
        ],
        verification=[
            "Starting the app with a missing required configuration value fails immediately at startup with a clear error.",
            "A feature flag can be toggled off in a lower environment and the old code path is confirmed to activate.",
            "A secret-scanning check confirms no credentials exist in appsettings.json or committed configuration files.",
            "A periodic review confirms no feature flag has remained fully-rolled-out and unused for more than an agreed grace period.",
        ],
        references=[
            "skills/80-security/secrets-and-key-management/SKILL.md",
            "Microsoft Learn — Options pattern in ASP.NET Core.",
            "Microsoft.FeatureManagement documentation.",
        ],
    ),
]
