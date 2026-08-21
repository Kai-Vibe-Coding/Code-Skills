SKILLS = [
    dict(
        dir="30-backend", slug="dotnet-solution-bootstrap", category="backend",
        tags=["dotnet", "solution-structure", "bootstrap"],
        desc="Use when starting a new .NET 8 backend service and you need a consistent solution layout, project references, and baseline tooling before writing feature code.",
        purpose=[
            "Inconsistent solution structures across services make it harder for engineers to move between "
            "projects and for tooling (CI, analyzers, architecture tests) to apply uniformly. This skill "
            "defines a standard .NET 8 solution layout aligned with Clean/Onion Architecture, plus the "
            "baseline tooling (analyzers, EditorConfig, central package management) every new service should "
            "start with.",
            "Getting this right at bootstrap time avoids expensive structural rework once a service has "
            "significant business logic already in place.",
        ],
        when_use=[
            "You are starting a brand-new .NET 8 backend service from scratch.",
            "An existing service's structure has drifted and needs to be realigned with the team standard.",
            "You are setting up shared tooling (analyzers, formatting) for a new solution.",
        ],
        when_not=[
            "You are adding a feature to an already-bootstrapped, well-structured solution — just follow its existing conventions.",
            "The project is a small throwaway script or prototype with no expectation of long-term maintenance.",
        ],
        prereqs=[
            ".NET 8 SDK installed.",
            "skills/20-architecture/clean-and-onion-architecture/SKILL.md understood, since the layout implements it.",
            "Team agreement on shared analyzer/style rules if this is a multi-service organization.",
        ],
        workflow=[
            ("Create the solution and layered projects", "dotnet new sln, then Domain, Application, Infrastructure, and Api class library/web projects."),
            ("Set project references per the dependency rule", "Application -> Domain; Infrastructure -> Application, Domain; Api -> Application, Infrastructure."),
            ("Add central package management", "Use Directory.Packages.props to pin package versions once across the whole solution."),
            ("Add a Directory.Build.props for shared settings", "Centralize TargetFramework, Nullable, ImplicitUsings, and analyzer settings across all projects."),
            ("Configure nullable reference types and analyzers", "Enable <Nullable>enable</Nullable> and treat key analyzer warnings as errors from day one, not retrofitted later."),
            ("Set up the test project structure", "One test project per layer (Domain.Tests, Application.Tests) plus an Api.IntegrationTests project."),
            ("Add baseline CI", "Wire dotnet build, dotnet test, and dotnet format --verify-no-changes into CI immediately."),
            ("Commit a working 'hello world' vertical slice", "Prove the layering works end-to-end with one trivial endpoint before building real features."),
        ],
        decision=[
            ("Solution will have many similar services (a platform)", "Extract Directory.Build.props/Directory.Packages.props conventions into a shared template repo."),
            ("Team is small and domain is simple", "Still use the layered structure, but keep the Application layer thin rather than skipping layering entirely."),
            ("Service needs both a public API and background workers", "Add a separate Worker project referencing Application/Infrastructure, rather than cramming worker code into the Api project."),
            ("Analyzer warnings are noisy on day one", "Enable them as warnings first, fix or explicitly suppress with justification, then escalate to errors — do not disable them permanently."),
            ("Package versions drift across projects", "Centralize via Directory.Packages.props immediately rather than pinning per-project."),
        ],
        code_lang="text",
        code_intro="Standard .NET 8 solution layout produced by the bootstrap workflow:",
        code=(
            "OrderPlatform.sln\n"
            "Directory.Build.props\n"
            "Directory.Packages.props\n"
            ".editorconfig\n"
            "src/\n"
            "  OrderPlatform.Domain/            (no project references)\n"
            "  OrderPlatform.Application/        -> Domain\n"
            "  OrderPlatform.Infrastructure/     -> Application, Domain\n"
            "  OrderPlatform.Api/                -> Application, Infrastructure (composition root)\n"
            "  OrderPlatform.Worker/             -> Application, Infrastructure\n"
            "tests/\n"
            "  OrderPlatform.Domain.Tests/\n"
            "  OrderPlatform.Application.Tests/\n"
            "  OrderPlatform.Api.IntegrationTests/\n"
            "\n"
            "# Bootstrap commands\n"
            "dotnet new sln -n OrderPlatform\n"
            "dotnet new classlib -n OrderPlatform.Domain -o src/OrderPlatform.Domain\n"
            "dotnet new classlib -n OrderPlatform.Application -o src/OrderPlatform.Application\n"
            "dotnet new classlib -n OrderPlatform.Infrastructure -o src/OrderPlatform.Infrastructure\n"
            "dotnet new webapi -n OrderPlatform.Api -o src/OrderPlatform.Api\n"
            "dotnet sln add src/**/*.csproj tests/**/*.csproj\n"
        ),
        code_notes=[
            "Add project references immediately after creation so the dependency rule is enforced from commit one.",
            "Keep the Api project's Program.cs as the only place concrete infrastructure types are registered (the composition root).",
        ],
        code2_heading="Directory.Build.props baseline settings",
        code2=("xml",
            "Shared settings applied to every project in the solution:",
            "<Project>\n"
            "  <PropertyGroup>\n"
            "    <TargetFramework>net8.0</TargetFramework>\n"
            "    <Nullable>enable</Nullable>\n"
            "    <ImplicitUsings>enable</ImplicitUsings>\n"
            "    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>\n"
            "    <AnalysisLevel>latest</AnalysisLevel>\n"
            "    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>\n"
            "  </PropertyGroup>\n"
            "</Project>\n"
        ),
        checklist=[
            "Projects are split by layer (Domain, Application, Infrastructure, Api) with correct references.",
            "Domain project has zero references to Infrastructure or any framework package.",
            "Directory.Build.props and Directory.Packages.props centralize shared settings and versions.",
            "Nullable reference types are enabled solution-wide from the start.",
            "A test project exists per layer, plus an integration test project for the Api.",
            "CI runs build, test, and format-verification on every push from day one.",
            "A trivial end-to-end vertical slice proves the layering works before real features are built.",
        ],
        antipatterns=[
            ("Single flat project", "Putting controllers, business logic, and EF Core entities all in one project, making later layering a painful retrofit."),
            ("Per-project package versions", "Letting each project pin its own package versions, causing version drift and conflicting transitive dependencies."),
            ("Deferred nullable enablement", "Starting with Nullable disabled 'to move fast' and enabling it later, when it requires touching every file."),
            ("No tests from day one", "Deferring test project setup until 'there's something worth testing', losing the habit of testing as you go."),
            ("CI added as an afterthought", "Writing weeks of code before wiring up any CI pipeline, missing early regressions."),
        ],
        verification=[
            "`dotnet build` succeeds with zero warnings on a fresh clone.",
            "An architecture test (or manual check) confirms Domain has no outward project references.",
            "`dotnet test` runs at least one passing test per layer, including the integration test project.",
            "CI is green on the initial bootstrap commit before any feature work begins.",
        ],
        references=[
            "skills/20-architecture/clean-and-onion-architecture/SKILL.md",
            "Microsoft Learn — .NET solution and project structure guidance.",
            "skills/60-devops/ci-cd-pipelines/SKILL.md",
        ],
    ),
    dict(
        dir="30-backend", slug="cqrs-with-mediatr", category="backend",
        tags=["cqrs", "mediatr", "application-layer"],
        desc="Use when an application's use cases are becoming tangled in large service classes and you need a consistent, discoverable pattern for commands, queries, and their handlers.",
        purpose=[
            "As an application layer grows, large service classes with many methods become hard to navigate "
            "and test in isolation. CQRS (Command Query Responsibility Segregation) with a mediator library "
            "like MediatR gives each use case its own small, independently testable handler, discoverable by "
            "convention rather than buried in a large class.",
            "This skill covers applying CQRS pragmatically within a single data store (not necessarily "
            "separate read/write databases) using MediatR as the in-process mediator.",
        ],
        when_use=[
            "The application layer has many distinct use cases that would benefit from isolation.",
            "You want cross-cutting concerns (logging, validation, transactions) applied consistently via pipeline behaviors.",
            "Multiple engineers work on different use cases concurrently and merge conflicts in large service classes are frequent.",
        ],
        when_not=[
            "The application has only a handful of simple CRUD operations — plain service/repository methods are simpler.",
            "The team is unfamiliar with mediator patterns and the indirection would slow onboarding for a small project.",
        ],
        prereqs=[
            "skills/20-architecture/clean-and-onion-architecture/SKILL.md applied, since commands/queries live in the Application layer.",
            "MediatR (or equivalent) package referenced in the Application layer.",
            "skills/30-backend/validation-and-error-handling/SKILL.md for validation pipeline behavior.",
        ],
        workflow=[
            ("Define a command or query per use case", "One class per use case (PlaceOrderCommand, GetOrderByIdQuery) with only the data it needs."),
            ("Write one handler per command/query", "Each handler implements IRequestHandler<TRequest, TResponse> and contains only that use case's orchestration logic."),
            ("Keep handlers thin and focused", "Handlers orchestrate domain objects and repositories; business rules live in domain entities, not handlers."),
            ("Add pipeline behaviors for cross-cutting concerns", "Validation, logging, and transaction wrapping applied uniformly via IPipelineBehavior, not duplicated per handler."),
            ("Separate commands from queries clearly", "Commands mutate state and return minimal data (e.g. an ID); queries never mutate state."),
            ("Register handlers via assembly scanning", "Use MediatR's service registration to auto-discover handlers instead of manually wiring each one."),
            ("Test handlers in isolation", "Unit test each handler with mocked repositories/dependencies, independent of HTTP or the database."),
        ],
        decision=[
            ("Use case only reads data with no business logic", "Model it as a query handler returning a DTO directly from a read-optimized query, not through domain entities."),
            ("Use case mutates state and enforces business rules", "Model it as a command handler that loads an aggregate, calls domain methods, and persists changes."),
            ("Same validation logic needed across every command", "Implement it once as a MediatR pipeline behavior (e.g. using FluentValidation) rather than per-handler."),
            ("A handler grows to orchestrate many unrelated steps", "Split it into a domain service called by a leaner handler, or reconsider whether it is really one use case."),
            ("Read-heavy reporting query with complex joins", "Consider Dapper (skills/30-backend/dapper-and-raw-sql/SKILL.md) for that specific query handler instead of forcing it through EF Core entities."),
        ],
        code_lang="csharp",
        code_intro="A command and its handler following CQRS conventions:",
        code=(
            "public record PlaceOrderCommand(Guid CustomerId, List<OrderLineDto> Lines)\n"
            "    : IRequest<PlaceOrderResult>;\n"
            "\n"
            "public class PlaceOrderCommandHandler : IRequestHandler<PlaceOrderCommand, PlaceOrderResult>\n"
            "{\n"
            "    private readonly IOrderRepository _orders;\n"
            "    private readonly ICatalogQueries _catalog;\n"
            "\n"
            "    public PlaceOrderCommandHandler(IOrderRepository orders, ICatalogQueries catalog)\n"
            "    {\n"
            "        _orders = orders;\n"
            "        _catalog = catalog;\n"
            "    }\n"
            "\n"
            "    public async Task<PlaceOrderResult> Handle(PlaceOrderCommand request, CancellationToken ct)\n"
            "    {\n"
            "        var order = Order.Create(request.CustomerId);\n"
            "        foreach (var line in request.Lines)\n"
            "        {\n"
            "            var product = await _catalog.GetProductAsync(line.ProductId)\n"
            "                ?? throw new NotFoundException(nameof(Product), line.ProductId);\n"
            "            order.AddLine(product.ToRef(), line.Quantity);\n"
            "        }\n"
            "        order.Submit();\n"
            "        await _orders.AddAsync(order, ct);\n"
            "        return new PlaceOrderResult(order.Id);\n"
            "    }\n"
            "}\n"
        ),
        code_notes=[
            "The handler orchestrates; AddLine and Submit enforce invariants inside the Order aggregate, not here.",
            "Register handlers with services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(typeof(PlaceOrderCommand).Assembly)).",
        ],
        code2_heading="A validation pipeline behavior applied to every command (C#)",
        code2=("csharp",
            "Cross-cutting validation without repeating logic in every handler:",
            "public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>\n"
            "    where TRequest : IRequest<TResponse>\n"
            "{\n"
            "    private readonly IEnumerable<IValidator<TRequest>> _validators;\n"
            "    public ValidationBehavior(IEnumerable<IValidator<TRequest>> validators) => _validators = validators;\n"
            "\n"
            "    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next,\n"
            "        CancellationToken ct)\n"
            "    {\n"
            "        var failures = _validators\n"
            "            .Select(v => v.Validate(request))\n"
            "            .SelectMany(r => r.Errors)\n"
            "            .Where(e => e != null)\n"
            "            .ToList();\n"
            "        if (failures.Count != 0)\n"
            "            throw new ValidationException(failures);\n"
            "        return await next();\n"
            "    }\n"
            "}\n"
        ),
        checklist=[
            "Each use case has its own command/query and handler, not a shared multi-method service class.",
            "Commands mutate state and return minimal data; queries never mutate state.",
            "Business rules live inside domain entities, not scattered across handler logic.",
            "Cross-cutting concerns (validation, logging, transactions) are pipeline behaviors, not duplicated per handler.",
            "Handlers are unit tested in isolation with mocked dependencies.",
            "Handler registration uses assembly scanning rather than manual per-handler wiring.",
        ],
        antipatterns=[
            ("Fat handlers", "Cramming business rules directly into a handler instead of delegating to domain entities, recreating an anemic-model problem inside MediatR."),
            ("CQRS as ceremony", "Introducing MediatR and command/query classes for a trivial CRUD app with no real benefit, adding indirection for its own sake."),
            ("Commands returning full entities", "Returning entire aggregate graphs from a command handler instead of the minimal result the caller actually needs."),
            ("Duplicated cross-cutting logic", "Re-implementing logging or validation inside every handler instead of a shared pipeline behavior."),
            ("Queries that mutate state", "Sneaking a side effect (like an audit log write) into a query handler, blurring the CQRS separation and surprising callers."),
        ],
        verification=[
            "A new engineer can find the handler for any given use case by its command/query name alone.",
            "Unit tests exist for each handler's core logic without requiring a database or HTTP server.",
            "Validation, logging, and transaction behavior are demonstrably applied uniformly across handlers via pipeline tests.",
            "No query handler is found to mutate persisted state during code review.",
        ],
        references=[
            "MediatR documentation (Jimmy Bogard).",
            "skills/20-architecture/clean-and-onion-architecture/SKILL.md",
            "skills/30-backend/validation-and-error-handling/SKILL.md",
            "skills/20-architecture/domain-driven-design/SKILL.md",
        ],
    ),
]
