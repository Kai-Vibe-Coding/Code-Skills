SKILLS = [
    dict(
        dir="20-architecture", slug="system-design-process", category="architecture",
        tags=["system-design", "architecture-process", "diagrams"],
        desc="Use when designing a new system or major subsystem and you need a repeatable process to move from requirements to a reviewable architecture.",
        purpose=[
            "Ad hoc system design produces architectures that are hard to review because the reasoning "
            "behind them is invisible. This skill defines a repeatable process — context, requirements, "
            "constraints, options, decision, diagram — so architecture proposals can be evaluated on their "
            "merits rather than the persuasiveness of whoever presents them.",
            "It is a meta-skill that ties together requirements, ADRs, and the more specific architecture "
            "skills in this category into a single end-to-end workflow.",
        ],
        when_use=[
            "You are designing a new service, subsystem, or major integration.",
            "An existing system needs a significant architectural change (e.g. splitting a monolith).",
            "You need to communicate a design to reviewers who were not part of early discussions.",
            "Multiple teams need to agree on system boundaries and contracts before building.",
        ],
        when_not=[
            "The change is a small, local implementation detail with no architectural impact.",
            "An architecture already exists and is well documented — use it rather than redesigning.",
        ],
        prereqs=[
            "Confirmed requirements (skills/10-planning/prd-and-spec-writing/SKILL.md).",
            "Known non-functional requirements: scale, latency, availability, compliance.",
            "A way to produce diagrams (Mermaid is used throughout this catalog).",
        ],
        workflow=[
            ("Restate the problem and constraints", "Summarize what the system must do and the hard constraints (budget, timeline, team skills, existing systems it must integrate with)."),
            ("Identify quality attributes", "Rank the top 3 non-functional priorities (e.g. availability over latency, or vice versa) — you cannot maximize all of them equally."),
            ("Sketch context and containers", "Draw a system context diagram showing external actors and systems, then a container diagram showing major deployable units."),
            ("Generate at least two real options", "Force yourself to consider a genuinely different approach, not just one design dressed up two ways."),
            ("Evaluate against quality attributes", "Score each option against the ranked priorities from step 2, not just against 'does it work'."),
            ("Record the decision as an ADR", "Use skills/10-planning/architecture-decision-records/SKILL.md for the chosen option and rejected alternatives."),
            ("Define interfaces and contracts explicitly", "Specify APIs, events, or data contracts between components before implementation starts."),
            ("Review with stakeholders", "Walk the diagrams and ADR through a review before committing engineering time to build."),
        ],
        decision=[
            ("Team is small and the domain is well understood", "Prefer skills/20-architecture/modular-monolith-vs-microservices/SKILL.md's monolith-first guidance over premature service decomposition."),
            ("Strong consistency is required across aggregates", "Favor a single transactional boundary over an eventually-consistent distributed design."),
            ("Multiple independent teams need to ship independently", "Favor clear service boundaries with explicit contracts over a shared codebase."),
            ("Non-functional requirements are still fuzzy", "Pause and go back to skills/10-planning/requirements-elicitation/SKILL.md before finalizing the design."),
            ("Two designs score similarly", "Prefer the one with less operational complexity and fewer new technologies for the team."),
            ("Design review surfaces a blocking disagreement", "Record it as an open question in the ADR and escalate rather than silently picking a side."),
        ],
        code_lang="mermaid",
        code_intro="A system context diagram produced during step 3 of the workflow:",
        code=(
            "flowchart TB\n"
            "    subgraph External\n"
            "        Customer[Customer]\n"
            "        PaymentGW[Payment Gateway]\n"
            "    end\n"
            "    subgraph System[\"Order Platform (in scope)\"]\n"
            "        WebApp[Web App]\n"
            "        OrdersAPI[Orders API]\n"
            "        OrdersDB[(Orders DB)]\n"
            "        EventBus[[Event Bus]]\n"
            "        Notifier[Notification Service]\n"
            "    end\n"
            "    Customer --> WebApp --> OrdersAPI\n"
            "    OrdersAPI --> OrdersDB\n"
            "    OrdersAPI --> PaymentGW\n"
            "    OrdersAPI --> EventBus --> Notifier\n"
            "    Notifier --> Customer\n"
        ),
        code_notes=[
            "Keep the context diagram to one page — push implementation detail into container/component diagrams instead.",
            "Label every arrow with the protocol or contract (REST, event type) so reviewers see explicit boundaries.",
        ],
        code2_heading="Option comparison table used before the ADR",
        code2=("text",
            "A structured comparison forces genuine option evaluation instead of confirmation bias:",
            "Priorities (ranked): 1) Availability  2) Cost  3) Latency\n"
            "\n"
            "Option A: Single region, multi-AZ deployment\n"
            "  Availability: Good (survives AZ failure)  Cost: Low   Latency: Best\n"
            "Option B: Active-active multi-region\n"
            "  Availability: Best (survives region failure)  Cost: High  Latency: Good\n"
            "\n"
            "Decision: Option A for launch; revisit Option B if regional outage SLAs tighten.\n"
        ),
        checklist=[
            "Requirements and non-functional priorities are explicitly ranked before comparing options.",
            "At least two genuinely different options were considered and evaluated.",
            "A context diagram and at least one container/component diagram exist.",
            "The chosen option is recorded as an ADR with rejected alternatives documented.",
            "Interfaces/contracts between components are specified, not left implicit.",
            "The design was reviewed with stakeholders before implementation began.",
            "Open questions or disagreements from review are tracked, not silently dropped.",
        ],
        antipatterns=[
            ("Diagram-free architecture", "Describing a system only in prose, making it hard for reviewers to spot missing components or unclear boundaries."),
            ("Single-option design", "Presenting only the chosen design with no real alternative considered, hiding the trade-off reasoning."),
            ("Resume-driven design", "Choosing a technology because it is new or interesting rather than because it best fits the ranked quality attributes."),
            ("Implicit contracts", "Leaving API/event schemas undefined until implementation, causing integration surprises between teams."),
            ("Skipping review", "Starting implementation before stakeholders have seen and agreed to the design."),
            ("Optimizing everything equally", "Trying to maximize availability, cost, and latency simultaneously instead of explicitly ranking trade-offs."),
        ],
        verification=[
            "A reviewer unfamiliar with the discussion can understand the design from the diagrams and ADR alone.",
            "The chosen option's trade-offs are traceable to the ranked quality attributes.",
            "Every component-to-component interaction has a named contract (API spec, event schema).",
            "The ADR documents at least one rejected alternative with reasoning.",
        ],
        references=[
            "skills/10-planning/architecture-decision-records/SKILL.md",
            "skills/10-planning/prd-and-spec-writing/SKILL.md",
            "C4 model (Simon Brown) — context/container/component/code diagram levels.",
            "skills/20-architecture/scalability-and-capacity-planning/SKILL.md",
        ],
    ),
    dict(
        dir="20-architecture", slug="domain-driven-design", category="architecture",
        tags=["ddd", "bounded-context", "domain-model"],
        desc="Use when a business domain is complex enough that a shared, ubiquitous model is needed to keep code aligned with how domain experts actually think and talk about the problem.",
        purpose=[
            "Complex business domains modeled as generic CRUD entities lose meaning: business rules end up "
            "scattered across services with no single place that represents 'what the business actually "
            "means'. Domain-Driven Design (DDD) provides tactical and strategic patterns — bounded contexts, "
            "aggregates, ubiquitous language — to keep the code's model aligned with the business's model.",
            "This skill focuses on applying DDD pragmatically to real projects, not on academic completeness; "
            "not every system needs full DDD rigor.",
        ],
        when_use=[
            "The domain has complex business rules that change based on real-world policy, not just data shape.",
            "Multiple teams have different, sometimes conflicting, meanings for the same term (e.g. 'Customer').",
            "You are decomposing a monolith and need principled boundaries, not arbitrary ones.",
            "Domain experts and engineers currently struggle to communicate using a shared vocabulary.",
        ],
        when_not=[
            "The system is a simple CRUD application with little real business logic.",
            "The team is too small to sustain the discovery and modeling overhead DDD requires.",
        ],
        prereqs=[
            "Access to domain experts for event storming or similar discovery sessions.",
            "skills/20-architecture/system-design-process/SKILL.md applied at the system level first.",
        ],
        workflow=[
            ("Run domain discovery", "Facilitate event storming or similar sessions with domain experts to surface real business events, commands, and rules."),
            ("Identify bounded contexts", "Group related concepts into contexts where a term has one unambiguous meaning (e.g. 'Product' means something different in Catalog vs Shipping)."),
            ("Define the ubiquitous language per context", "Agree on precise terms with domain experts and use them verbatim in code — class names, not synonyms."),
            ("Model aggregates around invariants", "Group entities that must be consistent together into an aggregate with a single root enforcing its invariants."),
            ("Define context boundaries and relationships", "Document how contexts relate: shared kernel, customer-supplier, anti-corruption layer, etc."),
            ("Keep the domain model free of infrastructure", "Domain entities should not know about databases, HTTP, or frameworks — see skills/20-architecture/clean-and-onion-architecture/SKILL.md."),
            ("Validate with domain experts", "Walk real scenarios through the model with domain experts to confirm it matches their mental model."),
        ],
        decision=[
            ("Two teams use the same word differently", "Split into separate bounded contexts rather than forcing one shared meaning."),
            ("An aggregate is growing very large", "Check whether it is enforcing more than one true invariant; split along invariant boundaries."),
            ("Integrating with a legacy or third-party system", "Introduce an anti-corruption layer to translate its model into your bounded context's language."),
            ("Domain has little real complexity", "Skip full DDD tactical patterns; a simpler CRUD/service layer is more appropriate."),
            ("A rule changes based on business policy, not data", "Model it as an explicit domain concept (e.g. a Policy or Specification object), not a scattered if-statement."),
            ("Cross-context consistency seems needed instantly", "Prefer eventual consistency via domain events between contexts over a distributed transaction."),
        ],
        code_lang="mermaid",
        code_intro="Bounded contexts and their relationships for an e-commerce platform:",
        code=(
            "flowchart LR\n"
            "    subgraph Catalog[\"Catalog Context\"]\n"
            "        Product[Product Aggregate]\n"
            "    end\n"
            "    subgraph Ordering[\"Ordering Context\"]\n"
            "        Order[Order Aggregate]\n"
            "        LineItem[OrderLine]\n"
            "    end\n"
            "    subgraph Shipping[\"Shipping Context\"]\n"
            "        Shipment[Shipment Aggregate]\n"
            "    end\n"
            "    Catalog -- \"ACL: ProductRef\" --> Ordering\n"
            "    Ordering -- \"OrderPlaced event\" --> Shipping\n"
            "    Order --> LineItem\n"
        ),
        code_notes=[
            "The 'ACL' label shows Catalog's Product is translated through an anti-corruption layer before Ordering uses it.",
            "OrderPlaced crossing to Shipping via an event, not a direct call, keeps the contexts loosely coupled.",
        ],
        code2_heading="An aggregate enforcing its own invariant (C#)",
        code2=("csharp",
            "A minimal Order aggregate that protects a real business invariant:",
            "public class Order\n"
            "{\n"
            "    private readonly List<OrderLine> _lines = new();\n"
            "    public IReadOnlyList<OrderLine> Lines => _lines;\n"
            "    public OrderStatus Status { get; private set; } = OrderStatus.Draft;\n"
            "\n"
            "    public void AddLine(ProductRef product, int quantity)\n"
            "    {\n"
            "        if (Status != OrderStatus.Draft)\n"
            "            throw new DomainException(\"Cannot modify a submitted order.\");\n"
            "        if (quantity <= 0)\n"
            "            throw new DomainException(\"Quantity must be positive.\");\n"
            "        _lines.Add(new OrderLine(product, quantity));\n"
            "    }\n"
            "\n"
            "    public void Submit()\n"
            "    {\n"
            "        if (_lines.Count == 0)\n"
            "            throw new DomainException(\"Cannot submit an order with no lines.\");\n"
            "        Status = OrderStatus.Submitted;\n"
            "    }\n"
            "}\n"
        ),
        checklist=[
            "Bounded contexts are identified with explicit, non-overlapping meanings for shared terms.",
            "The ubiquitous language is used verbatim in code (class/method names match domain expert vocabulary).",
            "Each aggregate enforces exactly the invariants it needs to, and no more.",
            "Domain entities have no direct dependency on infrastructure (DB, HTTP, frameworks).",
            "Cross-context communication uses events or anti-corruption layers, not shared database access.",
            "The model was validated against real scenarios with domain experts.",
        ],
        antipatterns=[
            ("Anemic domain model", "Entities that are just data bags with all logic living in separate 'service' classes, losing the benefit of DDD."),
            ("God aggregate", "One aggregate root spanning the entire domain, causing contention and unclear consistency boundaries."),
            ("Shared database as integration", "Multiple bounded contexts reading/writing the same tables directly instead of communicating via explicit contracts."),
            ("Vocabulary mismatch", "Code using generic technical names (Manager, Helper, Data) instead of the domain experts' actual terms."),
            ("DDD everywhere", "Applying full tactical DDD patterns to simple CRUD subdomains that do not need the complexity."),
        ],
        verification=[
            "A domain expert can read the aggregate/entity names and recognize their own vocabulary.",
            "Each bounded context's model is internally consistent and does not silently depend on another context's internals.",
            "Invariant-breaking operations are impossible to construct in code (compiler/runtime enforced, not just convention).",
        ],
        references=[
            "Eric Evans, 'Domain-Driven Design'.",
            "Vaughn Vernon, 'Implementing Domain-Driven Design'.",
            "skills/20-architecture/clean-and-onion-architecture/SKILL.md",
            "skills/20-architecture/modular-monolith-vs-microservices/SKILL.md",
        ],
    ),
]
