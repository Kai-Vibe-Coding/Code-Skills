SKILLS = [
    dict(
        dir="20-architecture", slug="api-design-rest", category="architecture",
        tags=["rest", "api-design", "http"],
        desc="Use when designing a new HTTP API or reviewing an existing one and you need consistent resource modeling, status codes, versioning, and pagination conventions.",
        purpose=[
            "Inconsistent REST APIs — mismatched status codes, ad hoc pagination, breaking changes without "
            "versioning — create integration pain for every consumer. This skill defines a consistent set "
            "of REST conventions covering resource modeling, HTTP verbs, status codes, error shapes, "
            "pagination, and versioning.",
            "It is meant to be applied uniformly across a service's endpoints so that consumers can predict "
            "behavior for any new endpoint without reading its docs.",
        ],
        when_use=[
            "You are designing a new HTTP API or a new set of endpoints on an existing one.",
            "You are reviewing an API design PR for consistency with the rest of the platform.",
            "Consumers report unpredictable error shapes or inconsistent pagination across endpoints.",
            "You need to introduce a breaking change and must decide how to version it.",
        ],
        when_not=[
            "The interface is internal-only, high-frequency, and better served by gRPC — see skills/20-architecture/api-design-graphql-and-grpc/SKILL.md.",
            "Consumers need flexible, client-specified queries across many resource types — consider GraphQL instead.",
        ],
        prereqs=[
            "Confirmed resource model (skills/20-architecture/domain-driven-design/SKILL.md if the domain is complex).",
            "Agreement on the API's versioning strategy before the first endpoint ships.",
            "skills/30-backend/validation-and-error-handling/SKILL.md for the error response shape.",
        ],
        workflow=[
            ("Model resources as nouns", "Design URLs around resources (/orders/{id}) not actions (/getOrder); use HTTP verbs for actions."),
            ("Choose verbs and status codes consistently", "GET=200, POST=201 with Location header, PUT/PATCH=200/204, DELETE=204; 4xx for client errors, 5xx for server errors."),
            ("Define a standard error shape", "Use one consistent JSON error envelope (code, message, details) across every endpoint, including validation failures."),
            ("Design pagination up front", "Use cursor or offset pagination consistently, with total count and next-page links, for every list endpoint."),
            ("Version from day one", "Include a version in the URL or header (/v1/orders) even for the first release, so breaking changes have a clear path."),
            ("Support partial responses / filtering deliberately", "Decide explicitly which endpoints support field selection or filtering, and document the query parameter convention."),
            ("Document with an OpenAPI spec", "Generate or hand-write an OpenAPI document as the source of truth, kept in sync with the implementation."),
            ("Review against existing endpoints", "Check new endpoints against existing ones in the same API for naming, status code, and error consistency."),
        ],
        decision=[
            ("Deciding a resource's identifier format", "Use opaque, stable IDs (GUID or ULID) rather than exposing internal database auto-increment integers."),
            ("An operation doesn't fit CRUD naturally (e.g. 'cancel order')", "Model it as a sub-resource action: POST /orders/{id}/cancel rather than a verb in the path."),
            ("A breaking change is required", "Introduce a new version (/v2/...) and support both versions during a deprecation window rather than breaking v1 consumers."),
            ("Client needs to fetch a large, deeply nested object graph", "Consider a dedicated aggregate endpoint or move that consumer to GraphQL rather than over-nesting REST responses."),
            ("List endpoint result set can grow unbounded", "Use cursor-based pagination instead of offset-based to avoid skipped/duplicated results under concurrent writes."),
            ("An error can have multiple causes (e.g. multiple invalid fields)", "Return all validation errors in one response, not just the first one encountered."),
            ("A partner consumer requires stability guarantees", "Document a deprecation policy and minimum notice period in the API contract."),
        ],
        code_lang="mermaid",
        code_intro="Standard request/response flow for a resource collection endpoint with pagination and errors:",
        code=(
            "sequenceDiagram\n"
            "    participant C as Client\n"
            "    participant A as Orders API\n"
            "    C->>A: GET /v1/orders?status=pending&cursor=abc123\n"
            "    alt valid request\n"
            "        A-->>C: 200 OK { data: [...], nextCursor: \"xyz789\" }\n"
            "    else invalid query parameter\n"
            "        A-->>C: 400 Bad Request { code: \"INVALID_PARAM\", message, details }\n"
            "    else not authorized\n"
            "        A-->>C: 403 Forbidden { code: \"FORBIDDEN\", message }\n"
            "    end\n"
        ),
        code_notes=[
            "Keep the error envelope shape identical across 400/403/404/409/500 — only the code and message content differ.",
            "cursor-based pagination avoids the duplicate/skip problem offset pagination has under concurrent inserts/deletes.",
        ],
        code2_heading="Minimal ASP.NET Core controller following these conventions (C#)",
        code2=("csharp",
            "A list endpoint with cursor pagination and a consistent error envelope:",
            "[ApiController]\n"
            "[Route(\"v1/orders\")]\n"
            "public class OrdersController : ControllerBase\n"
            "{\n"
            "    private readonly IOrderQueryService _queries;\n"
            "    public OrdersController(IOrderQueryService queries) => _queries = queries;\n"
            "\n"
            "    [HttpGet]\n"
            "    public async Task<ActionResult<PagedResult<OrderSummary>>> List(\n"
            "        [FromQuery] string? status, [FromQuery] string? cursor, [FromQuery] int pageSize = 20)\n"
            "    {\n"
            "        if (pageSize is < 1 or > 100)\n"
            "            return BadRequest(ApiError.From(\"INVALID_PARAM\", \"pageSize must be 1-100.\"));\n"
            "\n"
            "        var result = await _queries.ListAsync(status, cursor, pageSize);\n"
            "        return Ok(result); // { data, nextCursor, totalCount }\n"
            "    }\n"
            "\n"
            "    [HttpPost(\"{id:guid}/cancel\")]\n"
            "    public async Task<IActionResult> Cancel(Guid id)\n"
            "    {\n"
            "        await _queries.CancelAsync(id);\n"
            "        return NoContent(); // 204\n"
            "    }\n"
            "}\n"
        ),
        checklist=[
            "URLs are resource-oriented nouns; actions that don't fit CRUD use a sub-resource verb path.",
            "Status codes and verbs are used consistently across every endpoint in the API.",
            "Every error response uses the same envelope shape, including validation errors.",
            "Every list endpoint uses the same pagination approach with a documented convention.",
            "The API is versioned from its first release.",
            "An OpenAPI spec exists and is kept in sync with the implementation.",
            "IDs exposed to clients are opaque and stable, not internal auto-increment integers.",
            "A deprecation policy exists for any breaking change across versions.",
        ],
        antipatterns=[
            ("Verb-based URLs", "Endpoints like /getOrder or /createOrder instead of resource nouns with proper HTTP verbs."),
            ("Inconsistent error shapes", "Different endpoints returning different JSON structures for errors, forcing clients to special-case each one."),
            ("Unversioned breaking changes", "Changing a field's type or removing it from a response without a new API version, breaking existing consumers silently."),
            ("Leaky internal IDs", "Exposing database auto-increment integers as public identifiers, revealing internal scale and enabling enumeration."),
            ("Offset pagination at scale", "Using page/offset pagination on a frequently-changing large dataset, causing skipped or duplicated rows for clients paging through results."),
            ("200 for everything", "Returning HTTP 200 with an 'error' field in the body instead of proper 4xx/5xx status codes."),
        ],
        verification=[
            "A new endpoint added to the API matches the status code and error shape of existing endpoints without special-casing.",
            "The OpenAPI spec validates against the actual implementation (e.g. via contract tests).",
            "A breaking change was shipped behind a new version with the old version still functioning during the deprecation window.",
            "Pagination behaves correctly under concurrent writes (spot-checked with a test that inserts rows mid-pagination).",
        ],
        references=[
            "Microsoft REST API Guidelines.",
            "RFC 7807 — Problem Details for HTTP APIs.",
            "skills/30-backend/validation-and-error-handling/SKILL.md",
            "skills/20-architecture/api-design-graphql-and-grpc/SKILL.md",
        ],
    ),
    dict(
        dir="20-architecture", slug="api-design-graphql-and-grpc", category="architecture",
        tags=["graphql", "grpc", "api-design"],
        desc="Use when REST does not fit the consumer's needs — either clients need flexible, client-specified queries (GraphQL) or services need low-latency internal calls (gRPC) — and you need to choose and design the right one.",
        purpose=[
            "REST is not always the right fit: client applications needing flexible, nested data fetching "
            "benefit from GraphQL, while internal service-to-service calls needing low latency and strong "
            "typing benefit from gRPC. This skill explains when each is appropriate and the core design "
            "practices for each.",
            "Choosing the wrong protocol for the situation creates either over-fetching/under-fetching pain "
            "(REST/GraphQL mismatch) or unnecessary operational complexity (gRPC for a public-facing API).",
        ],
        when_use=[
            "A client application needs to fetch varying, nested combinations of data efficiently — consider GraphQL.",
            "Multiple frontend teams need different shapes of the same underlying data.",
            "Two internal services need frequent, low-latency, strongly-typed calls — consider gRPC.",
            "You are designing streaming or bidirectional communication between backend services.",
        ],
        when_not=[
            "The API is simple CRUD with a small number of consumers — plain REST (skills/20-architecture/api-design-rest/SKILL.md) is simpler to operate.",
            "The API must be easily callable from arbitrary HTTP clients/browsers without special tooling — avoid gRPC for public-facing APIs.",
        ],
        prereqs=[
            "skills/20-architecture/api-design-rest/SKILL.md read first, to confirm REST does not fit.",
            "Confirmed consumer needs (browser client vs internal service) driving the protocol choice.",
        ],
        workflow=[
            ("Confirm the protocol fits the consumer", "GraphQL for flexible client-driven queries over HTTP/browsers; gRPC for internal, high-throughput, strongly-typed service calls."),
            ("Design the schema/contract first", "Write the GraphQL SDL or protobuf .proto file before implementation, and treat it as the API contract."),
            ("Model GraphQL types around the domain, not the database", "Avoid exposing raw ORM shapes; define types that make sense to API consumers."),
            ("Avoid the N+1 query problem in GraphQL", "Use a batching/dataloader pattern for resolvers that fetch related entities."),
            ("Design gRPC services around use cases", "Define RPC methods as specific operations, not a generic CRUD wrapper around internal storage."),
            ("Version deliberately", "GraphQL evolves via additive schema changes and deprecation directives; gRPC evolves via backward-compatible protobuf field numbering."),
            ("Set explicit query limits for GraphQL", "Apply depth and complexity limits to prevent a single query from causing excessive backend load."),
        ],
        decision=[
            ("Public-facing API for third-party developers", "Prefer REST or GraphQL over gRPC, since gRPC tooling is harder for arbitrary external clients."),
            ("Internal service mesh with polyglot services", "gRPC is a strong fit due to protobuf's cross-language code generation and HTTP/2 performance."),
            ("Mobile client needs to minimize round trips for a complex screen", "GraphQL's single-request nested queries reduce round trips versus multiple REST calls."),
            ("Need for streaming updates between services", "gRPC's native streaming support fits better than polling a REST endpoint."),
            ("A GraphQL resolver is causing N+1 database queries", "Introduce a DataLoader/batching layer rather than accepting the performance hit."),
            ("A protobuf field needs to be removed", "Reserve its field number and name rather than reusing it, to avoid breaking old clients."),
        ],
        code_lang="mermaid",
        code_intro="Choosing between REST, GraphQL, and gRPC based on consumer and use case:",
        code=(
            "flowchart TD\n"
            "    Start{Who is the primary consumer?}\n"
            "    Start -->|Public/third-party, simple resources| REST[REST]\n"
            "    Start -->|Browser/mobile client, flexible nested data| GQL[GraphQL]\n"
            "    Start -->|Internal service-to-service, high throughput| GRPC[gRPC]\n"
            "    GQL --> Batch[Add DataLoader batching for resolvers]\n"
            "    GRPC --> Stream{Needs streaming?}\n"
            "    Stream -->|Yes| BiDi[Bidirectional streaming RPC]\n"
            "    Stream -->|No| Unary[Unary RPC]\n"
        ),
        code_notes=[
            "This decision tree is a starting heuristic, not a rigid rule — some APIs legitimately expose both REST and GraphQL for different consumers.",
            "A gRPC-web gateway can bridge browser clients to gRPC backends if truly needed, but adds operational complexity.",
        ],
        code2_heading="A minimal gRPC service contract (protobuf)",
        code2=("protobuf",
            "A use-case-oriented gRPC service definition, not a generic CRUD wrapper:",
            "syntax = \"proto3\";\n"
            "package orders.v1;\n"
            "\n"
            "service OrderService {\n"
            "  rpc PlaceOrder (PlaceOrderRequest) returns (PlaceOrderResponse);\n"
            "  rpc StreamOrderUpdates (StreamOrderUpdatesRequest) returns (stream OrderUpdate);\n"
            "}\n"
            "\n"
            "message PlaceOrderRequest {\n"
            "  string customer_id = 1;\n"
            "  repeated OrderLine lines = 2;\n"
            "}\n"
            "\n"
            "message OrderLine {\n"
            "  string product_id = 1;\n"
            "  int32 quantity = 2;\n"
            "}\n"
            "\n"
            "message PlaceOrderResponse {\n"
            "  string order_id = 1;\n"
            "  string status = 2;\n"
            "}\n"
        ),
        checklist=[
            "The chosen protocol matches the actual consumer (browser/public vs internal service).",
            "A schema/contract (SDL or .proto) exists and is treated as the source of truth.",
            "GraphQL resolvers avoid N+1 queries via batching/dataloaders.",
            "GraphQL queries have depth/complexity limits to prevent runaway queries.",
            "gRPC services are modeled around use cases, not generic CRUD passthroughs.",
            "Protobuf field numbers are never reused after removal; deprecated fields are reserved.",
            "Versioning strategy (additive GraphQL schema evolution, protobuf compatibility rules) is documented.",
        ],
        antipatterns=[
            ("GraphQL over a raw ORM", "Exposing database entities directly as GraphQL types, leaking internal schema details and coupling the API to storage."),
            ("Unbounded GraphQL queries", "Allowing arbitrarily deep or wide queries with no complexity limit, letting one client request take down the backend."),
            ("gRPC for public APIs", "Exposing gRPC directly to third-party/browser consumers who lack easy tooling to call it, creating adoption friction."),
            ("N+1 resolver chains", "Fetching related entities one at a time per parent in a GraphQL resolver instead of batching."),
            ("Reusing protobuf field numbers", "Assigning a removed field's number to a new field, causing old clients to misinterpret data."),
        ],
        verification=[
            "Load testing a nested GraphQL query confirms resolvers are batched, not causing N+1 queries.",
            "A complexity/depth limit rejects a deliberately excessive test query.",
            "A protobuf schema change passes a backward-compatibility check (e.g. buf breaking) before merge.",
            "Consumers can successfully generate typed clients from the published schema/contract.",
        ],
        references=[
            "GraphQL.org — Official specification and best practices.",
            "gRPC.io — Official documentation.",
            "skills/20-architecture/api-design-rest/SKILL.md",
            "Buf — protobuf schema linting and breaking-change detection.",
        ],
    ),
    dict(
        dir="20-architecture", slug="event-driven-architecture", category="architecture",
        tags=["events", "messaging", "async"],
        desc="Use when services need to react to state changes in other services without tight coupling, and synchronous request/response would create unwanted temporal or availability coupling.",
        purpose=[
            "Synchronous calls between services couple their availability and latency together: if the "
            "downstream service is slow or down, the caller is too. Event-driven architecture decouples "
            "producers and consumers in time by routing state changes through an event bus or broker.",
            "This skill covers designing event schemas, choosing delivery guarantees, and avoiding the "
            "common pitfalls of eventual consistency and duplicate/out-of-order delivery.",
        ],
        when_use=[
            "Multiple services need to react to the same state change without direct coupling.",
            "A downstream operation can tolerate eventual consistency (seconds to minutes, not immediate).",
            "You need to decouple a slow or unreliable downstream integration from the main transaction.",
            "You are building an audit trail or need to replay history of what happened over time.",
        ],
        when_not=[
            "The operation requires an immediate, synchronous response to the caller (e.g. checking real-time inventory before confirming a purchase).",
            "The team has no operational experience with message brokers and the complexity is not yet justified.",
        ],
        prereqs=[
            "A message broker or event bus available (e.g. Kafka, RabbitMQ, Azure Service Bus, SNS/SQS).",
            "skills/30-backend/background-jobs-and-messaging/SKILL.md for the consumer-side implementation.",
            "Agreement on event schema versioning and ownership per bounded context.",
        ],
        workflow=[
            ("Identify the domain events", "List meaningful business state changes (OrderPlaced, PaymentFailed) from the domain model, not just CRUD operations."),
            ("Design the event schema", "Include a stable event type, version, timestamp, and enough context for consumers to act without calling back the producer."),
            ("Choose a delivery guarantee", "Decide between at-least-once (most common, requires idempotent consumers) and at-most-once based on the use case's tolerance for loss vs duplication."),
            ("Use the outbox pattern for reliability", "Persist the event in the same transaction as the state change, then publish asynchronously, to avoid dual-write inconsistency."),
            ("Make consumers idempotent", "Design consumers to safely process the same event twice (e.g. using an event ID for deduplication)."),
            ("Handle ordering explicitly", "Use partition/shard keys (e.g. per-aggregate ID) if relative event order matters, since brokers rarely guarantee global order."),
            ("Version events additively", "Add new optional fields rather than changing/removing existing ones; introduce a new event type for breaking changes."),
            ("Monitor consumer lag and dead-lettering", "Track how far behind consumers are and route unprocessable messages to a dead-letter queue for investigation."),
        ],
        decision=[
            ("Caller needs an immediate answer", "Use a synchronous call, not an event — events are for 'something happened', not 'give me an answer now'."),
            ("Multiple consumers need the same event", "Use a pub/sub topic rather than point-to-point queues so new consumers can subscribe without producer changes."),
            ("Order of events per entity matters", "Partition by the entity's ID (e.g. order ID) so related events land in the same ordered partition."),
            ("A consumer might receive the same event twice", "Design it to be idempotent (e.g. upsert semantics, dedupe by event ID) rather than assuming exactly-once delivery."),
            ("An event fails processing repeatedly", "Route it to a dead-letter queue with alerting rather than retrying forever or silently dropping it."),
            ("Producer and consumer are in the same transaction today", "Consider whether decoupling via an event is actually needed yet, or if it is premature complexity."),
            ("Event schema needs a breaking change", "Publish a new versioned event type alongside the old one during a migration window."),
        ],
        code_lang="mermaid",
        code_intro="Reliable event publication using the outbox pattern, with a downstream consumer:",
        code=(
            "sequenceDiagram\n"
            "    participant O as Orders Service\n"
            "    participant DB as Orders DB\n"
            "    participant Relay as Outbox Relay\n"
            "    participant Bus as Event Bus\n"
            "    participant N as Notification Service\n"
            "    O->>DB: BEGIN TX: save Order + insert OutboxEvent(OrderPlaced)\n"
            "    DB-->>O: COMMIT\n"
            "    Relay->>DB: poll unpublished OutboxEvents\n"
            "    Relay->>Bus: publish OrderPlaced (v1)\n"
            "    Bus->>N: deliver OrderPlaced\n"
            "    N->>N: process idempotently (dedupe by event id)\n"
            "    N-->>Bus: ack\n"
        ),
        code_notes=[
            "The outbox table is written in the same DB transaction as the Order, so the event is never lost even if the relay crashes.",
            "The relay marks the outbox row published only after the broker acknowledges receipt.",
        ],
        code2_heading="A versioned event schema example (JSON)",
        code2=("json",
            "A well-formed domain event with enough context for consumers to act independently:",
            "{\n"
            "  \"eventId\": \"5c1b1e2a-9e3e-4d3a-9b2b-7e6c9c1a2b3c\",\n"
            "  \"eventType\": \"OrderPlaced\",\n"
            "  \"eventVersion\": 1,\n"
            "  \"occurredAt\": \"2026-08-21T01:30:00Z\",\n"
            "  \"orderId\": \"ord_9182\",\n"
            "  \"customerId\": \"cus_4471\",\n"
            "  \"totalAmount\": 129.99,\n"
            "  \"currency\": \"USD\",\n"
            "  \"lines\": [\n"
            "    { \"productId\": \"prod_11\", \"quantity\": 2 }\n"
            "  ]\n"
            "}\n"
        ),
        checklist=[
            "Events represent meaningful domain state changes, not raw CRUD notifications.",
            "Every event has a stable type name, version, and unique ID for deduplication.",
            "Events are published via the outbox pattern (or equivalent) to avoid dual-write loss.",
            "Consumers are idempotent and safely handle duplicate delivery.",
            "Ordering guarantees (if needed) are achieved via partition/shard keys, not assumed globally.",
            "A dead-letter queue and alerting exist for messages that repeatedly fail processing.",
            "Event schema changes are additive; breaking changes introduce a new versioned event type.",
        ],
        antipatterns=[
            ("Dual-write without an outbox", "Writing to the database and publishing to the broker as two separate operations, risking losing the event if the process crashes in between."),
            ("Non-idempotent consumers", "Assuming exactly-once delivery and performing non-idempotent operations (e.g. blind increment) on event receipt."),
            ("CRUD-shaped events", "Publishing generic 'EntityUpdated' events with no semantic meaning, forcing consumers to diff state themselves."),
            ("Silent message drops", "Letting unprocessable messages disappear with no dead-letter queue or alerting."),
            ("Assuming global ordering", "Relying on events arriving in a specific cross-entity order without a partition key guaranteeing it."),
            ("Using events for synchronous needs", "Publishing an event and polling/waiting for a response instead of using a direct synchronous call."),
        ],
        verification=[
            "Killing the process between DB commit and broker publish does not lose the event (outbox relay recovers it).",
            "Replaying the same event twice against a consumer produces the same end state (idempotency check).",
            "Consumer lag and dead-letter queue depth are visible on a dashboard with alerting thresholds.",
            "A schema change was verified to not break existing consumers still on the prior event version.",
        ],
        references=[
            "skills/30-backend/background-jobs-and-messaging/SKILL.md",
            "Chris Richardson, 'Microservices Patterns' — Outbox and Saga patterns.",
            "skills/20-architecture/resilience-patterns/SKILL.md",
        ],
    ),
    dict(
        dir="20-architecture", slug="caching-strategy", category="architecture",
        tags=["caching", "performance", "consistency"],
        desc="Use when a read path is too slow or too expensive at current load and you need to decide what to cache, where, and how to keep it consistent with the source of truth.",
        purpose=[
            "Caching is one of the highest-leverage performance techniques available, but done carelessly it "
            "trades latency problems for consistency and cache-invalidation problems. This skill provides a "
            "framework for choosing what to cache, at which layer, with which invalidation strategy, before "
            "reaching for caching as a default fix for slow reads.",
            "It emphasizes that caching should follow a measured bottleneck, not be applied speculatively "
            "everywhere a read exists.",
        ],
        when_use=[
            "A specific read path has been measured as a latency or database load bottleneck.",
            "Data is read far more often than it changes (high read/write ratio).",
            "An expensive computation or aggregation is repeated for the same inputs frequently.",
            "You need to protect a downstream system (DB, third-party API) from repeated identical requests.",
        ],
        when_not=[
            "The data changes on every read or must always reflect the absolute latest state (e.g. account balance mid-transaction).",
            "No measured performance problem exists yet — do not cache speculatively.",
        ],
        prereqs=[
            "A measured baseline (latency, DB load) showing the bottleneck cache is meant to fix.",
            "A caching layer available (in-process, Redis, or a CDN depending on the layer).",
            "Clarity on the acceptable staleness window for the cached data.",
        ],
        workflow=[
            ("Confirm the bottleneck with data", "Profile or measure the specific read path before deciding to cache it."),
            ("Choose the caching layer", "Client/CDN cache for static/public content; distributed cache (Redis) for shared application data; in-process cache for very hot, small, per-instance data."),
            ("Define the cache key precisely", "Include every parameter that affects the result (tenant ID, locale, filters) to avoid serving wrong data to the wrong request."),
            ("Choose an invalidation strategy", "Time-based expiry (TTL) for tolerable staleness; explicit invalidation on write for strict consistency needs."),
            ("Handle cache misses safely", "Use request coalescing or locking to prevent a 'thundering herd' of duplicate work when a popular key expires."),
            ("Set a sensible TTL", "Base TTL on how stale the data can acceptably be, not an arbitrary default."),
            ("Plan for cache failure", "Ensure the system still functions (slower, not broken) if the cache is unavailable — never make it a single point of failure for correctness."),
            ("Monitor hit rate and staleness", "Track cache hit ratio and, where relevant, how often stale data was actually served."),
        ],
        decision=[
            ("Data changes rarely and staleness of minutes is fine", "Use TTL-based expiry in a distributed cache; simplest and usually sufficient."),
            ("Data must reflect the very latest write immediately after it happens", "Use explicit invalidation on write (cache-aside with delete-on-write) rather than relying on TTL alone."),
            ("A hot key is read by every request (e.g. feature flag config)", "Consider an in-process cache with a short refresh interval to avoid a network hop per request."),
            ("Cache and database can drift under concurrent writes", "Prefer cache-aside with invalidation over write-through if strict consistency during races matters, and accept brief staleness windows."),
            ("A popular cache key just expired under high load", "Use request coalescing (single-flight) so only one request recomputes it while others wait for the result."),
            ("Cached data is user- or tenant-specific", "Always include the user/tenant ID in the cache key — never share cache entries across security boundaries."),
        ],
        code_lang="mermaid",
        code_intro="Cache-aside pattern with explicit invalidation on write:",
        code=(
            "sequenceDiagram\n"
            "    participant App\n"
            "    participant Cache as Redis\n"
            "    participant DB\n"
            "    Note over App,DB: Read path (cache-aside)\n"
            "    App->>Cache: GET product:123\n"
            "    alt cache hit\n"
            "        Cache-->>App: cached value\n"
            "    else cache miss\n"
            "        App->>DB: SELECT * FROM products WHERE id=123\n"
            "        DB-->>App: row\n"
            "        App->>Cache: SET product:123 (TTL 5m)\n"
            "    end\n"
            "    Note over App,DB: Write path (invalidate on write)\n"
            "    App->>DB: UPDATE products SET price=... WHERE id=123\n"
            "    App->>Cache: DEL product:123\n"
        ),
        code_notes=[
            "Delete-on-write rather than update-on-write avoids the cache ever holding a partially-applied or racing write.",
            "A short TTL acts as a safety net in case an invalidation is ever missed.",
        ],
        code2_heading="Cache-aside implementation with request coalescing (C#)",
        code2=("csharp",
            "Using IMemoryCache's GetOrCreateAsync to avoid duplicate work on concurrent misses:",
            "public class ProductCacheService\n"
            "{\n"
            "    private readonly IDistributedCache _cache;\n"
            "    private readonly IProductRepository _repo;\n"
            "\n"
            "    public async Task<ProductDto?> GetProductAsync(Guid id)\n"
            "    {\n"
            "        var key = $\"product:{id}\";\n"
            "        var cached = await _cache.GetStringAsync(key);\n"
            "        if (cached is not null)\n"
            "            return JsonSerializer.Deserialize<ProductDto>(cached);\n"
            "\n"
            "        var product = await _repo.GetByIdAsync(id);\n"
            "        if (product is null) return null;\n"
            "\n"
            "        var dto = ProductDto.FromEntity(product);\n"
            "        await _cache.SetStringAsync(key, JsonSerializer.Serialize(dto),\n"
            "            new DistributedCacheEntryOptions { AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(5) });\n"
            "        return dto;\n"
            "    }\n"
            "\n"
            "    public async Task InvalidateAsync(Guid id) => await _cache.RemoveAsync($\"product:{id}\");\n"
            "}\n"
        ),
        checklist=[
            "The cached read path was measured as an actual bottleneck before adding caching.",
            "Cache keys include every parameter that affects the cached result (tenant, locale, filters).",
            "An explicit invalidation or TTL strategy matches the data's real staleness tolerance.",
            "The system degrades gracefully (slower, not broken/incorrect) if the cache is unavailable.",
            "Thundering-herd protection exists for popular keys that expire under load.",
            "Cache hit rate is monitored, and TTLs are tuned based on observed data.",
            "User/tenant-specific data is never cached under a shared key across security boundaries.",
        ],
        antipatterns=[
            ("Speculative caching", "Adding a cache layer to a read path with no measured performance problem, adding complexity for no benefit."),
            ("Incomplete cache keys", "Omitting a parameter like tenant ID from the cache key, causing one tenant to see another tenant's cached data."),
            ("Cache as source of truth", "Treating the cache as authoritative and losing data if it's evicted, instead of always being able to rebuild from the real source."),
            ("Unbounded TTLs", "Caching data forever with no expiry, leading to permanently stale results after the underlying data changes."),
            ("No thundering-herd protection", "Letting a popular key's expiry cause a stampede of duplicate expensive recomputation."),
            ("Cache failure as total failure", "Building a design where cache unavailability makes the whole feature unusable instead of degrading gracefully."),
        ],
        verification=[
            "A load test confirms the cached path meets its latency target under expected traffic.",
            "Cache invalidation is confirmed to remove stale data within the required window after a write.",
            "A simulated cache outage shows the system still functions, just slower.",
            "Cache hit ratio is visible on a dashboard and matches expectations for the access pattern.",
        ],
        references=[
            "skills/20-architecture/scalability-and-capacity-planning/SKILL.md",
            "Martin Kleppmann, 'Designing Data-Intensive Applications' — caching and consistency trade-offs.",
            "Redis documentation — cache-aside and expiration strategies.",
        ],
    ),
]
