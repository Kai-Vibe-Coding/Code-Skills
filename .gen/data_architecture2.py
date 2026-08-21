SKILLS = [
    dict(
        dir="20-architecture", slug="clean-and-onion-architecture", category="architecture",
        tags=["clean-architecture", "onion-architecture", "layering"],
        desc="Use when designing the internal layering of a backend service and you need business logic to stay independent of frameworks, databases, and UI concerns.",
        purpose=[
            "Business logic tightly coupled to a specific database or web framework becomes expensive to "
            "test and impossible to evolve independently. Clean/Onion architecture inverts the traditional "
            "dependency direction so infrastructure depends on the domain, not the other way around.",
            "This skill shows how to structure a .NET solution (or equivalent) into concentric layers with "
            "dependencies pointing strictly inward, and how to enforce that boundary in practice, not just "
            "in a diagram.",
        ],
        when_use=[
            "You are starting a new backend service and choosing its internal layering.",
            "Business logic is currently entangled with Entity Framework, ASP.NET, or another framework.",
            "You need to unit test business rules without spinning up a database or web server.",
            "Multiple infrastructure choices (DB, message broker) may need to change over the service's life.",
        ],
        when_not=[
            "The service is a thin proxy or pass-through with no real business logic to isolate.",
            "The team is a single small script/tool where the layering overhead outweighs the benefit.",
        ],
        prereqs=[
            "skills/20-architecture/domain-driven-design/SKILL.md concepts if the domain is non-trivial.",
            "A dependency injection container available in the chosen framework.",
            "Agreement within the team on where the boundary lines are drawn.",
            "skills/30-backend/dotnet-solution-bootstrap/SKILL.md if starting a new .NET solution.",
        ],
        workflow=[
            ("Define the domain layer first", "Model entities, value objects, and domain services with zero framework references."),
            ("Define application layer use cases", "Express each use case (command/query) as an explicit class or method orchestrating domain objects."),
            ("Define ports as interfaces in the inner layers", "Repository and external-service interfaces live in the domain/application layer, not infrastructure."),
            ("Implement adapters in the outer layer", "EF Core repositories, HTTP clients, and messaging adapters implement the inner-layer interfaces."),
            ("Wire dependencies at the composition root", "Only the outermost startup project references concrete infrastructure implementations."),
            ("Enforce the dependency rule", "Use project references (or architecture tests) so inner layers physically cannot reference outer layers."),
            ("Keep controllers/handlers thin", "API controllers should only translate HTTP to application layer calls, with no business logic inline."),
            ("Test business logic in isolation", "Unit test the domain and application layers without any database, HTTP, or framework dependency."),
        ],
        decision=[
            ("Where to put validation logic", "Structural/format validation in the application layer input model; business rule validation inside domain entities."),
            ("Where to put a repository interface", "In the domain or application layer (the 'port'); its EF Core implementation belongs in infrastructure (the 'adapter')."),
            ("A use case needs data from two aggregates", "Coordinate in the application layer service/handler, not by having one aggregate directly reference another."),
            ("Team is tempted to skip layering for 'a simple CRUD endpoint'", "Still separate a thin application layer if the entity has any real behavior; skip only for pure pass-through data."),
            ("Framework attributes leak into domain classes", "Move framework-specific concerns (e.g. [Column], [JsonProperty]) to separate DTOs/EF configuration classes instead."),
            ("New infrastructure choice replaces an old one", "Only the adapter implementation changes; the domain/application layers and their tests remain untouched — this is the payoff of the pattern."),
        ],
        code_lang="mermaid",
        code_intro="Layer dependency direction — arrows point inward, never outward:",
        code=(
            "flowchart TB\n"
            "    subgraph Outer[\"Infrastructure (adapters)\"]\n"
            "        EF[EF Core Repository]\n"
            "        Http[External API Client]\n"
            "        Api[ASP.NET Controllers]\n"
            "    end\n"
            "    subgraph App[\"Application layer (use cases)\"]\n"
            "        Handlers[Command/Query Handlers]\n"
            "        Ports[[Ports: IOrderRepository]]\n"
            "    end\n"
            "    subgraph Domain[\"Domain layer\"]\n"
            "        Entities[Order, OrderLine]\n"
            "    end\n"
            "    Api --> Handlers\n"
            "    Handlers --> Entities\n"
            "    Handlers --> Ports\n"
            "    EF -.implements.-> Ports\n"
            "    Http -.implements.-> Ports\n"
        ),
        code_notes=[
            "Dotted arrows show 'implements' — the infrastructure depends on the port interface, not vice versa.",
            "Only the composition root (startup project) is allowed to reference both application and infrastructure projects.",
        ],
        code2_heading="Enforcing the dependency rule with a project reference (.csproj layout)",
        code2=("text",
            "A solution layout that makes violating the dependency rule a compile error:",
            "src/\n"
            "  Domain/                 (no project references)\n"
            "  Application/            references: Domain\n"
            "  Infrastructure/         references: Application, Domain\n"
            "  Api/                    references: Application, Infrastructure (composition root)\n"
            "\n"
            "Domain.csproj must NOT reference Infrastructure.csproj or Api.csproj.\n"
            "A CI check (e.g. NetArchTest) can assert this automatically:\n"
            "\n"
            "  Types.InAssembly(typeof(Order).Assembly)\n"
            "      .Should().NotHaveDependencyOn(\"Infrastructure\")\n"
            "      .GetResult().IsSuccessful.Should().BeTrue();\n"
        ),
        checklist=[
            "Domain layer has zero references to web frameworks, ORMs, or infrastructure packages.",
            "Application layer defines use cases and port interfaces, without infrastructure detail.",
            "Infrastructure layer implements ports; no port lives in the infrastructure project.",
            "Controllers/handlers are thin translators, not homes for business logic.",
            "Domain and application layer logic is unit tested without a database or HTTP server.",
            "Project references (or an architecture test) physically enforce the dependency direction.",
            "Swapping an infrastructure implementation does not require changing domain/application code.",
        ],
        antipatterns=[
            ("Anemic layering in name only", "Having Domain/Application/Infrastructure folders that still freely reference each other in any direction, defeating the purpose."),
            ("Fat controllers", "Putting business rule logic directly in API controllers instead of application/domain layers."),
            ("Leaky infrastructure types", "Returning EF Core entities or ORM-tracked types directly from application layer methods, coupling callers to the ORM."),
            ("Framework attributes on domain entities", "Decorating domain classes with ORM or JSON serialization attributes, coupling them to infrastructure concerns."),
            ("Testing only through the API", "Skipping unit tests for domain/application logic and only testing via slow, database-backed integration tests."),
        ],
        verification=[
            "An architecture test (or manual review) confirms Domain has no outward dependencies.",
            "Unit tests for domain/application logic run without a database connection or HTTP server.",
            "A sample infrastructure swap (e.g. mocking a repository) requires no change to application/domain code.",
            "Code review confirms controllers contain no business rule logic.",
        ],
        references=[
            "Robert C. Martin, 'Clean Architecture'.",
            "Jeffrey Palermo, original Onion Architecture articles.",
            "skills/20-architecture/domain-driven-design/SKILL.md",
            "skills/30-backend/dotnet-solution-bootstrap/SKILL.md",
        ],
    ),
    dict(
        dir="20-architecture", slug="modular-monolith-vs-microservices", category="architecture",
        tags=["microservices", "monolith", "service-boundaries"],
        desc="Use when deciding whether a new system or a monolith split should be built as a modular monolith or as independently deployable microservices.",
        purpose=[
            "Choosing microservices before a team needs the operational complexity they bring is one of the "
            "most common architecture mistakes; choosing a tangled monolith when teams genuinely need "
            "independent deployability is the opposite mistake. This skill gives explicit criteria for "
            "choosing between a modular monolith and microservices, and how to keep a monolith modular "
            "enough to split later if needed.",
            "The default recommendation is monolith-first: build a well-modularized monolith, and extract "
            "services only when a concrete, evidenced need appears.",
        ],
        when_use=[
            "You are starting a new system and choosing its deployment topology.",
            "A monolith has grown large enough that team velocity or deploy risk is suffering.",
            "You are evaluating whether to extract a specific module into its own service.",
            "Leadership is pushing for microservices without a concrete driving requirement.",
        ],
        when_not=[
            "The system is small and unlikely to need independent scaling or independent team ownership.",
            "The team lacks the operational maturity (observability, on-call, deployment automation) microservices require.",
        ],
        prereqs=[
            "skills/20-architecture/domain-driven-design/SKILL.md to identify real bounded contexts as split candidates.",
            "Team topology information: how many teams, and do they need to deploy independently.",
            "Current pain points documented (deploy time, coupling, scaling limits) if considering a split.",
        ],
        workflow=[
            ("Start with a modular monolith by default", "Organize code into modules matching bounded contexts, each with a clear internal API, inside one deployable unit."),
            ("Enforce module boundaries in-process", "Prevent modules from reaching into each other's internal types/tables; force communication through defined interfaces or in-process events."),
            ("Track concrete pain signals", "Monitor deploy frequency conflicts, scaling mismatches between modules, and team coordination overhead as objective signals."),
            ("Evaluate extraction only when a signal is real", "Extract a module to its own service when it has a genuinely different scaling profile, release cadence, or ownership need."),
            ("Extract along existing module boundaries", "Only extract a module that is already cleanly bounded internally — extraction does not fix a poorly modularized monolith."),
            ("Define the service contract before extraction", "Design the new service's API/events first, then move code behind that contract."),
            ("Invest in operational readiness before splitting", "Confirm observability, deployment automation, and on-call processes can support an additional independently deployed unit."),
        ],
        decision=[
            ("Small team, unclear domain boundaries", "Stay with a modular monolith; premature service boundaries will be wrong and costly to fix."),
            ("One module needs to scale 100x independently of the rest", "Good candidate for extraction into its own service."),
            ("Two teams keep blocking each other's deploys", "Consider extraction if the blocking module has a clean internal boundary already."),
            ("Team lacks mature CI/CD and observability", "Invest in operational maturity first; do not add service count before you can operate what you already have."),
            ("A module has fundamentally different technology needs", "e.g. a CPU-bound ML component may justify a separate service even at small scale."),
            ("Leadership wants microservices for its own sake", "Push back with the monolith-first default and require a concrete signal before agreeing to split."),
        ],
        code_lang="mermaid",
        code_intro="A modular monolith with clear internal module boundaries, and one already-extracted service:",
        code=(
            "flowchart TB\n"
            "    subgraph Monolith[\"Modular Monolith (single deployable)\"]\n"
            "        Orders[Orders Module]\n"
            "        Catalog[Catalog Module]\n"
            "        Billing[Billing Module]\n"
            "    end\n"
            "    subgraph Extracted[\"Extracted Service\"]\n"
            "        Notifications[Notification Service]\n"
            "    end\n"
            "    Orders -- \"in-process interface\" --> Catalog\n"
            "    Orders -- \"in-process event\" --> Billing\n"
            "    Orders -- \"OrderPlaced (HTTP/event)\" --> Notifications\n"
        ),
        code_notes=[
            "Orders-to-Catalog and Orders-to-Billing stay in-process because they need strong consistency and low latency today.",
            "Notifications was extracted because it has a different scaling profile (bursty, fan-out) and no consistency requirement with Orders.",
        ],
        code2_heading="Enforcing module boundaries inside a monolith (C#)",
        code2=("csharp",
            "A simple internal-visibility pattern that keeps modules honest before any service split:",
            "// Catalog module's public surface — the only thing Orders may reference\n"
            "namespace Catalog.Public;\n"
            "public interface ICatalogQueries\n"
            "{\n"
            "    Task<ProductSummary?> GetProductAsync(Guid productId);\n"
            "}\n"
            "\n"
            "// Internal implementation and EF entities stay non-public to other modules\n"
            "namespace Catalog.Internal;\n"
            "internal class CatalogQueries : ICatalogQueries\n"
            "{\n"
            "    private readonly CatalogDbContext _db; // never referenced outside this module\n"
            "    public CatalogQueries(CatalogDbContext db) => _db = db;\n"
            "\n"
            "    public async Task<ProductSummary?> GetProductAsync(Guid productId) =>\n"
            "        await _db.Products.Where(p => p.Id == productId)\n"
            "            .Select(p => new ProductSummary(p.Id, p.Name, p.Price))\n"
            "            .FirstOrDefaultAsync();\n"
            "}\n"
        ),
        checklist=[
            "The default starting point was a modular monolith unless a concrete signal justified otherwise.",
            "Module boundaries match real bounded contexts, not arbitrary technical layers.",
            "Cross-module access goes through defined public interfaces, never internal types or tables directly.",
            "Any proposed service extraction is backed by a documented, concrete pain signal.",
            "The extracted module was already cleanly bounded before extraction, not entangled.",
            "Operational readiness (observability, deploy automation, on-call) was confirmed before adding a new service.",
        ],
        antipatterns=[
            ("Microservices-first without evidence", "Splitting into services at project kickoff because 'that's how it's done', before any real scaling or team boundary need exists."),
            ("Distributed monolith", "Extracting services that still share a database or require synchronous calls for every operation, getting all the downsides of both models."),
            ("Big ball of mud monolith", "A monolith with no internal module boundaries, making a future split (if ever needed) extremely expensive."),
            ("Splitting along technical layers", "Extracting a 'database service' or 'business logic service' instead of splitting along business capability boundaries."),
            ("Ignoring operational readiness", "Adding services faster than the team's ability to operate, monitor, and deploy them independently."),
        ],
        verification=[
            "A dependency check confirms modules only communicate through defined public interfaces.",
            "Any existing service split can be justified with a documented pain signal that existed before extraction.",
            "The team can deploy, monitor, and support every currently existing service independently.",
            "New module boundaries align with the domain model from skills/20-architecture/domain-driven-design/SKILL.md.",
        ],
        references=[
            "Sam Newman, 'Building Microservices'.",
            "Martin Fowler, 'MonolithFirst'.",
            "skills/20-architecture/domain-driven-design/SKILL.md",
            "skills/60-devops/kubernetes-deployment/SKILL.md",
        ],
    ),
]
