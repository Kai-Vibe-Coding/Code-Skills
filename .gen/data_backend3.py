SKILLS = [
    dict(
        dir="30-backend", slug="dapper-and-raw-sql", category="backend",
        tags=["dapper", "sql", "performance"],
        desc="Use when a query is performance-critical or too complex for clean LINQ expression and you need direct, well-parameterized SQL via a micro-ORM like Dapper.",
        purpose=[
            "Some queries — complex reports, bulk operations, or hot paths under heavy load — are clearer and "
            "faster written as raw, hand-tuned SQL than forced through an ORM's query translation. Dapper "
            "gives a thin, fast mapping layer between raw SQL and C# objects while still requiring discipline "
            "around parameterization and connection management.",
            "This skill defines when to reach for Dapper instead of EF Core, and how to do so safely without "
            "reintroducing SQL injection or connection-leak risks.",
        ],
        when_use=[
            "A reporting or analytics query involves multiple joins/aggregations that are unreadable or slow as LINQ.",
            "A hot-path query needs hand-tuned SQL (specific index hints, batched operations) for performance.",
            "Bulk read or write operations need to avoid EF Core's per-entity change tracking overhead.",
        ],
        when_not=[
            "The query is a simple CRUD operation already well served by EF Core — don't bypass the ORM for its own sake.",
            "The team lacks SQL review discipline; raw SQL without careful review reintroduces injection and maintainability risk.",
        ],
        prereqs=[
            "skills/50-database/indexing-and-query-optimization/SKILL.md for tuning the underlying query.",
            "skills/80-security/input-validation-and-output-encoding/SKILL.md for parameterization discipline.",
            "A connection factory or scoped connection lifetime already established in Infrastructure.",
        ],
        workflow=[
            ("Identify the query that needs raw SQL", "Confirm via profiling or readability review that EF Core LINQ is the wrong tool for this specific query, not the whole layer."),
            ("Write parameterized SQL only", "Always use Dapper's parameter objects; never string-concatenate user input into SQL text."),
            ("Map results to purpose-built DTOs", "Query into a flat read-model class, not domain entities — Dapper queries are for reads, not aggregate reconstruction."),
            ("Manage connections explicitly and briefly", "Open a connection per query/operation via a factory, and let `using` dispose it promptly."),
            ("Use QueryMultiple for related result sets", "Fetch a parent and its children in a single round trip when the shape is well known, instead of N+1 separate calls."),
            ("Wrap multi-statement writes in a transaction", "Use IDbTransaction explicitly when a raw-SQL write spans more than one statement that must succeed or fail together."),
            ("Keep Dapper isolated to specific query handlers", "Confine raw-SQL usage to the handlers/repositories that need it; don't let it creep into general-purpose CRUD."),
        ],
        decision=[
            ("Read query is a straightforward filter/sort of one table", "Use EF Core; Dapper adds no benefit here."),
            ("Read query aggregates across 5+ tables for a dashboard", "Use Dapper with hand-written SQL and a flat result DTO."),
            ("Write operation must update thousands of rows efficiently", "Use Dapper with a set-based UPDATE statement instead of loading and saving entities individually."),
            ("Query needs full-text search or database-specific functions", "Use Dapper to call the database-specific SQL feature directly rather than fighting the ORM's LINQ translator."),
            ("Team is unsure whether raw SQL is warranted", "Default to EF Core first; only switch to Dapper once profiling shows a concrete performance or readability problem."),
        ],
        code_lang="csharp",
        code_intro="A parameterized Dapper query returning a flat DTO for a dashboard:",
        code=(
            "public class OrderReportQueries : IOrderReportQueries\n"
            "{\n"
            "    private readonly IDbConnectionFactory _connectionFactory;\n"
            "    public OrderReportQueries(IDbConnectionFactory connectionFactory) =>\n"
            "        _connectionFactory = connectionFactory;\n"
            "\n"
            "    public async Task<IReadOnlyList<CustomerSpendDto>> GetTopSpendersAsync(\n"
            "        DateTime since, int take, CancellationToken ct)\n"
            "    {\n"
            "        const string sql = \"\"\"\n"
            "            SELECT c.Id AS CustomerId, c.Name,\n"
            "                   SUM(ol.UnitPrice * ol.Quantity) AS TotalSpend\n"
            "            FROM Orders o\n"
            "            JOIN OrderLines ol ON ol.OrderId = o.Id\n"
            "            JOIN Customers c ON c.Id = o.CustomerId\n"
            "            WHERE o.SubmittedAt >= @Since\n"
            "            GROUP BY c.Id, c.Name\n"
            "            ORDER BY TotalSpend DESC\n"
            "            LIMIT @Take\n"
            "            \"\"\";\n"
            "\n"
            "        using var conn = _connectionFactory.Create();\n"
            "        var command = new CommandDefinition(sql, new { Since = since, Take = take },\n"
            "            cancellationToken: ct);\n"
            "        var rows = await conn.QueryAsync<CustomerSpendDto>(command);\n"
            "        return rows.AsList();\n"
            "    }\n"
            "}\n"
        ),
        code_notes=[
            "@Since and @Take are bound parameters — never interpolate values directly into the sql string.",
            "CommandDefinition carries the CancellationToken through so long-running reports can be cancelled cleanly.",
        ],
        code2_heading="A multi-statement write wrapped in an explicit transaction (C#)",
        code2=("csharp",
            "Ensuring a batch update and audit insert succeed or fail together:",
            "using var conn = _connectionFactory.Create();\n"
            "conn.Open();\n"
            "using var tx = conn.BeginTransaction();\n"
            "try\n"
            "{\n"
            "    await conn.ExecuteAsync(\n"
            "        \"UPDATE Orders SET Status = @Status WHERE Id = ANY(@Ids)\",\n"
            "        new { Status = \"Archived\", Ids = orderIds }, tx);\n"
            "    await conn.ExecuteAsync(\n"
            "        \"INSERT INTO AuditLog (Action, Payload) VALUES (@Action, @Payload::jsonb)\",\n"
            "        new { Action = \"BulkArchive\", Payload = JsonSerializer.Serialize(orderIds) }, tx);\n"
            "    tx.Commit();\n"
            "}\n"
            "catch { tx.Rollback(); throw; }\n"
        ),
        checklist=[
            "Every Dapper query uses parameter objects; no string concatenation or interpolation of user input into SQL.",
            "Dapper queries return flat DTOs, not domain entities being reconstructed as aggregates.",
            "Connections are opened per operation and disposed promptly via `using`.",
            "Multi-statement writes use an explicit transaction with commit/rollback handling.",
            "Raw SQL usage is confined to specific, justified query handlers, not the default data-access approach.",
            "CancellationToken is passed through CommandDefinition for long-running queries.",
        ],
        antipatterns=[
            ("String-concatenated SQL", "Building SQL text by concatenating user input directly, reintroducing SQL injection risk that parameterized queries prevent."),
            ("Dapper for simple CRUD", "Using Dapper to replace all EF Core access 'for performance' without profiling data justifying the switch."),
            ("Long-lived shared connections", "Holding a single DbConnection open for the app's lifetime instead of opening/closing per operation, causing pool exhaustion."),
            ("Domain entities from raw SQL", "Populating full domain aggregates via Dapper and then calling repository.Add on them, bypassing invariant enforcement in constructors/factories."),
            ("Unversioned ad hoc SQL scattered in handlers", "Copy-pasting similar raw SQL across many handlers instead of centralizing shared report queries."),
        ],
        verification=[
            "A security review or SAST scan confirms no raw string concatenation feeds into executed SQL.",
            "Profiling shows the target query's latency improved measurably versus the ORM-translated equivalent.",
            "Connections opened via Dapper are confirmed closed/disposed under load testing (no pool exhaustion).",
            "Code review confirms Dapper usage is limited to the specific queries that justified it.",
        ],
        references=[
            "Dapper documentation (StackExchange).",
            "skills/50-database/indexing-and-query-optimization/SKILL.md",
            "skills/80-security/input-validation-and-output-encoding/SKILL.md",
            "skills/30-backend/ef-core-data-access/SKILL.md",
        ],
    ),
    dict(
        dir="30-backend", slug="validation-and-error-handling", category="backend",
        tags=["validation", "error-handling", "problem-details"],
        desc="Use when designing how a backend service validates input and reports errors consistently across all endpoints and use cases.",
        purpose=[
            "Inconsistent validation and error responses make an API frustrating to integrate with and hide "
            "real bugs behind generic 500 errors. This skill establishes a layered validation strategy "
            "(input shape, business rule, domain invariant) and a single, consistent error response format "
            "using RFC 7807 Problem Details.",
            "It also defines how exceptions map to HTTP status codes so client applications get predictable, "
            "machine-readable errors rather than parsing free-text messages.",
        ],
        when_use=[
            "You are designing or auditing how a .NET API validates requests and returns error responses.",
            "Client teams report unpredictable or inconsistent error shapes across different endpoints.",
            "You are adding a new command/query and need to know where each kind of validation belongs.",
        ],
        when_not=[
            "The service is a purely internal batch job with no external API surface — simpler logging-based error handling may suffice.",
            "You're deep in a single bug fix; a full validation strategy overhaul isn't warranted for a one-line change.",
        ],
        prereqs=[
            "skills/30-backend/cqrs-with-mediatr/SKILL.md if using pipeline behaviors for validation.",
            "skills/80-security/input-validation-and-output-encoding/SKILL.md for security-relevant input handling.",
            "FluentValidation (or equivalent) package for declarative input validation.",
        ],
        workflow=[
            ("Validate input shape at the API boundary", "Use model binding plus FluentValidation validators to reject malformed requests before they reach the Application layer."),
            ("Validate business rules in Application handlers", "Rules like 'customer must have an active subscription' belong in the handler or a domain service, not the controller."),
            ("Enforce invariants inside domain entities", "Rules intrinsic to the entity (e.g. order total must be positive) throw domain exceptions from within the entity itself."),
            ("Map exceptions to Problem Details centrally", "A single exception-handling middleware converts known exception types to RFC 7807 responses with correct status codes."),
            ("Distinguish validation errors from not-found and conflict errors", "400 for validation, 404 for missing resources, 409 for conflicts — never collapse all failures to 500."),
            ("Never leak internal exception details to clients", "Log full exception details server-side; return a safe, generic message and a correlation ID to the client."),
            ("Return structured field-level errors for validation failures", "Include an 'errors' dictionary keyed by field name so client forms can highlight the exact problem."),
        ],
        decision=[
            ("Request has malformed JSON or missing required fields", "Return 400 with field-level Problem Details errors from the input validator."),
            ("Business rule fails (e.g. insufficient balance)", "Throw a specific domain/application exception and map it to 409 Conflict or 422 Unprocessable Entity."),
            ("Referenced resource doesn't exist", "Throw a NotFoundException mapped to 404, never a generic 400."),
            ("An unexpected, unhandled exception occurs", "Map it to 500 with a generic message and a correlation ID; log the full stack trace server-side only."),
            ("Client needs to distinguish retryable vs non-retryable errors", "Use distinct status codes/error codes (e.g. 429 vs 400) so clients can decide whether to retry."),
        ],
        code_lang="csharp",
        code_intro="Centralized exception-to-Problem-Details mapping middleware:",
        code=(
            "app.UseExceptionHandler(errApp => errApp.Run(async context =>\n"
            "{\n"
            "    var feature = context.Features.Get<IExceptionHandlerFeature>();\n"
            "    var ex = feature?.Error;\n"
            "    var (status, title) = ex switch\n"
            "    {\n"
            "        ValidationException => (StatusCodes.Status400BadRequest, \"Validation failed\"),\n"
            "        NotFoundException => (StatusCodes.Status404NotFound, \"Resource not found\"),\n"
            "        ConflictException => (StatusCodes.Status409Conflict, \"Conflict\"),\n"
            "        _ => (StatusCodes.Status500InternalServerError, \"An unexpected error occurred\")\n"
            "    };\n"
            "\n"
            "    var problem = new ProblemDetails\n"
            "    {\n"
            "        Status = status,\n"
            "        Title = title,\n"
            "        Extensions = { [\"correlationId\"] = context.TraceIdentifier }\n"
            "    };\n"
            "    if (ex is ValidationException ve)\n"
            "        problem.Extensions[\"errors\"] = ve.Errors.GroupBy(e => e.PropertyName)\n"
            "            .ToDictionary(g => g.Key, g => g.Select(e => e.ErrorMessage).ToArray());\n"
            "\n"
            "    context.Response.StatusCode = status;\n"
            "    await context.Response.WriteAsJsonAsync(problem);\n"
            "}));\n"
        ),
        code_notes=[
            "context.TraceIdentifier gives support teams a correlation ID to find the matching server-side log entry.",
            "Only ValidationException field errors are exposed; unhandled exceptions never leak stack traces to the client.",
        ],
        code2_heading="Declarative FluentValidation validator (C#)",
        code2=("csharp",
            "Input-shape validation applied automatically via a MediatR pipeline behavior:",
            "public class PlaceOrderCommandValidator : AbstractValidator<PlaceOrderCommand>\n"
            "{\n"
            "    public PlaceOrderCommandValidator()\n"
            "    {\n"
            "        RuleFor(x => x.CustomerId).NotEmpty();\n"
            "        RuleFor(x => x.Lines).NotEmpty()\n"
            "            .WithMessage(\"Order must contain at least one line item.\");\n"
            "        RuleForEach(x => x.Lines).ChildRules(line =>\n"
            "        {\n"
            "            line.RuleFor(l => l.Quantity).GreaterThan(0);\n"
            "        });\n"
            "    }\n"
            "}\n"
        ),
        checklist=[
            "Input-shape validation happens at the API boundary using declarative validators.",
            "Business rules live in Application handlers or domain services, not controllers.",
            "Entity invariants throw domain exceptions from within the entity, never bypassed.",
            "A single centralized middleware maps exceptions to consistent Problem Details responses.",
            "400/404/409/500 are used distinctly and never collapsed into a generic error shape.",
            "Unhandled exceptions never leak stack traces or internal details to the client.",
        ],
        antipatterns=[
            ("Try/catch in every controller action", "Duplicating exception-to-response mapping logic in each endpoint instead of one centralized middleware."),
            ("Everything returns 400", "Collapsing not-found, conflict, and validation errors all into 400 Bad Request, making client-side error handling impossible."),
            ("Leaking stack traces", "Returning ex.ToString() or ex.StackTrace in the API response body, exposing internal implementation details."),
            ("Validation scattered ad hoc", "Re-implementing the same null/empty checks manually in multiple handlers instead of one declarative validator per command."),
            ("Swallowing exceptions silently", "Catching an exception and returning a generic success response, hiding failures from both the client and logs."),
        ],
        verification=[
            "Every distinct failure mode (validation, not-found, conflict, unexpected) maps to a distinct, correct HTTP status code.",
            "API responses never include a stack trace or exception type name in production.",
            "Field-level validation errors are returned as structured data, not a single free-text message.",
            "A correlation ID in the error response can be matched to a corresponding server-side log entry.",
        ],
        references=[
            "RFC 7807 — Problem Details for HTTP APIs.",
            "FluentValidation documentation.",
            "skills/30-backend/cqrs-with-mediatr/SKILL.md",
            "skills/80-security/input-validation-and-output-encoding/SKILL.md",
        ],
    ),
]
