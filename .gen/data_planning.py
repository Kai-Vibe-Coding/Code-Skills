SKILLS = [
    dict(
        dir="10-planning", slug="requirements-elicitation", category="planning",
        tags=["requirements", "stakeholders", "discovery"],
        desc="Use when a feature request is vague or comes from a single stakeholder and you need to uncover the real needs, constraints, and edge cases before design begins.",
        purpose=[
            "Vague requirements produce rework, scope disputes, and features that miss the actual user need. "
            "This skill provides a structured way to interview stakeholders, surface hidden assumptions, and "
            "convert ambiguous requests into concrete, testable requirements.",
            "It focuses on asking the right questions early, when changes are cheap, rather than discovering "
            "gaps during implementation or after release when changes are expensive.",
        ],
        when_use=[
            "A stakeholder describes a feature in business terms without technical detail.",
            "A ticket says 'make it faster/better/easier' without a measurable target.",
            "Two stakeholders describe the same feature differently.",
            "You are about to write a PRD or spec and need raw material to work from.",
            "The request conflicts with, or overlaps, an existing feature.",
            "You suspect there are unstated non-functional requirements (performance, security, compliance).",
        ],
        when_not=[
            "The requirement is already fully specified with clear acceptance criteria.",
            "You are fixing a well-understood bug with an obvious, unambiguous correct behavior.",
            "The change is a pure internal refactor with no external behavior change.",
        ],
        prereqs=[
            "Access to the requesting stakeholder(s) or their proxy (product manager, support lead).",
            "Basic understanding of the existing product/system the request relates to.",
            "skills/00-core/context-gathering/SKILL.md applied to the current system first.",
            "A place to record findings (ticket, doc, or PRD draft).",
        ],
        workflow=[
            ("Identify all stakeholders", "List everyone affected: requester, end users, support, compliance, ops — not just the loudest voice."),
            ("Ask 'why' before 'what'", "Uncover the underlying problem or goal before accepting a proposed solution at face value."),
            ("Use concrete scenarios", "Ask for specific examples ('walk me through the last time this went wrong') instead of abstract descriptions."),
            ("Probe edge cases explicitly", "Ask about empty states, error states, concurrent use, and scale — these are rarely volunteered."),
            ("Surface non-functional requirements", "Explicitly ask about performance, availability, security, and compliance constraints."),
            ("Restate and confirm", "Play back your understanding in plain language and get explicit stakeholder confirmation."),
            ("Document open questions separately", "Track unresolved ambiguities visibly instead of quietly picking an answer."),
            ("Hand off to spec writing", "Feed confirmed requirements into skills/10-planning/prd-and-spec-writing/SKILL.md."),
        ],
        decision=[
            ("Stakeholder gives a solution, not a problem", "Ask 'what problem does this solve for you' before accepting the proposed solution."),
            ("Two stakeholders disagree", "Surface the disagreement explicitly and get a decision-maker to resolve it, rather than silently picking one side."),
            ("Stakeholder is unavailable for clarification", "Document your best-effort assumption and flag it as unconfirmed, do not block indefinitely."),
            ("Request implies a large, multi-quarter effort", "Break elicitation into phases: confirm the MVP scope first, defer edge cases to a follow-up round."),
            ("Non-functional requirements are never mentioned", "Proactively ask about scale, latency, and security expectations rather than assuming 'default' is fine."),
            ("Requirement conflicts with a known technical constraint", "Surface the conflict immediately rather than silently designing around it."),
            ("Elicitation reveals the request duplicates an existing feature", "Point this out before further design work is invested."),
        ],
        code_lang="text",
        code_intro="A structured interview script covering the most commonly missed areas:",
        code=(
            "Requirements Elicitation Interview Guide\n"
            "-----------------------------------------\n"
            "1. Problem framing\n"
            "   - What problem are you trying to solve? Who is affected, and how often?\n"
            "   - What happens today without this change? What is the workaround?\n"
            "2. Success criteria\n"
            "   - How will you know this worked? What metric moves, and by how much?\n"
            "3. Scenarios\n"
            "   - Walk me through the last time this went wrong, step by step.\n"
            "   - Who are the different types of users, and does each need something different?\n"
            "4. Edge cases (ask explicitly, do not wait for volunteering)\n"
            "   - What should happen with zero results / the first-ever use / concurrent use?\n"
            "   - What is the expected behavior on error, timeout, or partial failure?\n"
            "5. Non-functional requirements\n"
            "   - Expected volume/scale? Peak load? Response time expectations?\n"
            "   - Any compliance, audit, or data residency constraints?\n"
            "6. Boundaries\n"
            "   - What is explicitly out of scope for this iteration?\n"
            "   - What existing feature might this overlap with or replace?\n"
            "\n"
            "Output: a list of REQ-N statements plus an 'Open Questions' list of anything\n"
            "unresolved, both fed into the PRD.\n"
        ),
        code_notes=[
            "Timebox elicitation sessions (30-45 minutes) and follow up in writing rather than trying to resolve everything live.",
            "Always send a written summary back to stakeholders for explicit confirmation before design starts.",
        ],
        code2_heading="Turning a vague request into confirmed requirements",
        code2=("text",
            "Before-and-after showing how elicitation converts a vague ask into testable requirements:",
            "Before (raw request): \"Can we make the order search better? It's kind of slow\n"
            "and people can't find what they need.\"\n"
            "\n"
            "After elicitation:\n"
            "  REQ-1: Search must return results in under 1s for a 500k-row order table (p95).\n"
            "  REQ-2: Users must be able to filter by date range, status, and customer name.\n"
            "  REQ-3: Empty search results must suggest removing the most restrictive filter.\n"
            "  Open question: should search include archived (soft-deleted) orders? [Owner: PM]\n"
        ),
        checklist=[
            "Every named stakeholder group was consulted or explicitly represented by a proxy.",
            "The underlying problem, not just the proposed solution, was captured.",
            "At least one concrete scenario/example was gathered per major requirement.",
            "Edge cases (empty, error, concurrent, scale) were explicitly asked about.",
            "Non-functional requirements were explicitly discussed, not assumed.",
            "A written summary was played back and confirmed by the stakeholder.",
            "Open questions are tracked visibly rather than silently resolved by guessing.",
            "Overlap with existing features was checked and called out if found.",
        ],
        antipatterns=[
            ("Accepting the first solution offered", "Taking a stakeholder's proposed implementation at face value instead of uncovering the underlying problem it is meant to solve."),
            ("Single-source requirements", "Gathering requirements from only the loudest or most senior stakeholder, missing conflicting needs from other affected groups."),
            ("Silent tie-breaking", "Quietly picking one interpretation when stakeholders disagree instead of escalating for an explicit decision."),
            ("Assuming defaults for non-functional requirements", "Never asking about scale, latency, or compliance and hoping the 'obvious' assumption is correct."),
            ("Skipping written confirmation", "Proceeding to design purely from a verbal conversation with no documented, confirmed summary."),
            ("Elicitation without boundaries", "Gathering an ever-expanding wish list without ever confirming what is explicitly out of scope."),
        ],
        verification=[
            "A written requirements summary exists and was explicitly confirmed by the stakeholder(s).",
            "Each requirement traces back to a stated problem, not just a requested feature.",
            "Edge cases and non-functional requirements appear in the summary, not just happy-path behavior.",
            "Open questions are listed with an owner and are not blocking silently.",
            "The summary was checked against existing features for overlap or duplication.",
        ],
        references=[
            "skills/10-planning/prd-and-spec-writing/SKILL.md",
            "skills/10-planning/risk-and-assumption-log/SKILL.md",
            "Karl Wiegers, 'Software Requirements' — structured elicitation techniques.",
            "skills/00-core/requirements-to-code-traceability/SKILL.md",
        ],
    ),
    dict(
        dir="10-planning", slug="prd-and-spec-writing", category="planning",
        tags=["prd", "specification", "documentation"],
        desc="Use when you have gathered requirements for a feature and need to turn them into a written product requirements document or technical spec before implementation begins.",
        purpose=[
            "A good PRD turns scattered conversations into a single source of truth that engineering, "
            "design, and stakeholders can align on before code is written. This skill defines a lightweight "
            "but complete PRD/spec structure and the process for writing and reviewing one.",
            "It exists to prevent the two common failure modes: PRDs so vague they don't reduce ambiguity, "
            "and PRDs so heavyweight that nobody writes or reads them.",
        ],
        when_use=[
            "A feature is complex enough to involve more than one engineer or more than a few days of work.",
            "Multiple teams or stakeholders need to agree on scope before implementation starts.",
            "The feature has non-trivial non-functional requirements (performance, security, compliance).",
            "You need a durable reference to check the shipped feature against later.",
        ],
        when_not=[
            "The change is a small, single-owner bug fix or minor tweak.",
            "The team has already agreed on scope informally and formal documentation adds no value for a trivial change.",
        ],
        prereqs=[
            "Requirements gathered via skills/10-planning/requirements-elicitation/SKILL.md.",
            "templates/prd.template.md as the starting structure.",
            "Access to whoever needs to approve the PRD before implementation.",
        ],
        workflow=[
            ("Start from the template", "Copy templates/prd.template.md rather than inventing a new structure each time."),
            ("Write the problem statement first", "State the user/business problem in 2-3 sentences before any solution details."),
            ("Define goals and explicit non-goals", "List what this feature will and will not do, to bound scope early."),
            ("Translate requirements into user stories", "Phrase functional needs as 'As a <persona>, I want <capability>, so that <benefit>'."),
            ("Specify non-functional requirements with numbers", "Replace 'fast' and 'secure' with measurable targets like p95 latency or specific compliance standards."),
            ("Define success metrics", "State how success will be measured after launch, with a baseline and target."),
            ("Circulate for review", "Get explicit sign-off from engineering, design, and the requesting stakeholder before implementation starts."),
            ("Keep it living but versioned", "Update the PRD as scope changes during implementation, noting what changed and why."),
        ],
        decision=[
            ("Feature is small and single-owner", "Use a 1-page lightweight spec instead of the full PRD template."),
            ("Requirements are still shifting rapidly", "Delay full PRD sign-off; use a short 'working draft' status until they stabilize."),
            ("Non-functional requirements are unclear", "Escalate to skills/20-architecture/scalability-and-capacity-planning/SKILL.md before finalizing the PRD."),
            ("Stakeholders disagree on scope after the draft is shared", "Resolve via an explicit decision recorded in the PRD, not by silently editing it later."),
            ("Feature touches compliance-sensitive data", "Loop in skills/80-security/privacy-and-compliance-basics/SKILL.md before sign-off."),
            ("PRD keeps growing during review", "Split it: keep the MVP scope in this PRD and move future ideas to a separate backlog doc."),
            ("Engineering feasibility is uncertain", "Run a short technical spike before finalizing effort-sensitive requirements."),
        ],
        code_lang="markdown",
        code_intro="Excerpt from a filled PRD following templates/prd.template.md:",
        code=(
            "# PRD: Bulk Order Export\n"
            "\n"
            "## Problem Statement\n"
            "Finance manually exports orders one page at a time, costing ~4 hours/week and\n"
            "causing errors during month-end close.\n"
            "\n"
            "## Goals\n"
            "- Export up to 100k orders to CSV in a single request.\n"
            "- Reduce manual export time to under 5 minutes.\n"
            "\n"
            "## Non-Goals\n"
            "- Real-time export streaming (out of scope for v1).\n"
            "- Export formats other than CSV.\n"
            "\n"
            "## Requirements\n"
            "### Functional\n"
            "1. User can request an export for a date range and status filter.\n"
            "2. Export runs asynchronously; user is notified via email when ready.\n"
            "\n"
            "### Non-Functional\n"
            "- Performance: export of 100k rows completes within 5 minutes.\n"
            "- Security: only users with Finance.Export role may request exports.\n"
            "\n"
            "## Success Metrics\n"
            "| Metric | Baseline | Target |\n"
            "|---|---|---|\n"
            "| Manual export time | 4 hrs/week | < 30 min/week |\n"
        ),
        code_notes=[
            "Keep the functional requirement list numbered so it can be referenced directly in skills/00-core/requirements-to-code-traceability/SKILL.md.",
            "Non-functional requirements must have a number attached — 'fast' and 'secure' are not requirements.",
        ],
        code2_heading="Lightweight one-page spec for a small feature",
        code2=("markdown",
            "For small, single-owner work, use a trimmed-down alternative instead of the full PRD:",
            "# Spec: Add CSV column for order channel\n"
            "\n"
            "Problem: Finance cannot distinguish web vs phone orders in exports.\n"
            "Change: add an `order_channel` column to the existing CSV export.\n"
            "Non-goals: no new filter UI in this iteration.\n"
            "Acceptance: exported CSV includes `order_channel` with values web|phone|store.\n"
            "Verified by: OrderExportTests.IncludesChannelColumn.\n"
        ),
        checklist=[
            "The problem statement is written before any solution detail.",
            "Explicit non-goals are listed to bound scope.",
            "Every functional requirement is numbered and independently testable.",
            "Non-functional requirements have measurable targets, not vague adjectives.",
            "Success metrics have a stated baseline and target.",
            "The PRD was explicitly reviewed and approved by engineering and the requesting stakeholder.",
            "Open questions are listed rather than silently resolved.",
            "Scope changes during implementation are reflected back into the PRD with a changelog note.",
        ],
        antipatterns=[
            ("Solution-first PRDs", "Jumping straight to UI mockups or technical design without stating the underlying problem first."),
            ("Vague non-functional requirements", "Writing 'the system should be fast and secure' instead of measurable targets and standards."),
            ("Unbounded scope", "Omitting explicit non-goals, letting the feature quietly grow during implementation."),
            ("Write-once documents", "Treating the PRD as immutable after the kickoff meeting, letting it silently diverge from what is actually being built."),
            ("Sign-off theater", "Circulating a PRD for 'review' without any explicit approval step or recorded decision."),
            ("Requirement soup", "Mixing functional requirements, implementation details, and success metrics together with no clear structure."),
        ],
        verification=[
            "A named approver for each key stakeholder group signed off on the PRD before implementation began.",
            "Every requirement can be traced to a code/test pair using skills/00-core/requirements-to-code-traceability/SKILL.md.",
            "Non-functional requirements are measurable and were actually tested against post-launch.",
            "Any scope change during implementation has a corresponding update in the PRD.",
        ],
        references=[
            "templates/prd.template.md",
            "skills/10-planning/requirements-elicitation/SKILL.md",
            "skills/10-planning/definition-of-ready-and-done/SKILL.md",
            "skills/00-core/requirements-to-code-traceability/SKILL.md",
        ],
    ),
    dict(
        dir="10-planning", slug="work-breakdown-and-estimation", category="planning",
        tags=["estimation", "planning", "wbs"],
        desc="Use when a feature or PRD needs to be broken into implementable tasks with size estimates before sprint or milestone planning.",
        purpose=[
            "Large, unestimated units of work hide risk and make progress invisible until it is too late to "
            "adjust. This skill describes how to decompose a feature into small, independently deliverable "
            "tasks and produce estimates that are useful for planning without pretending to be precise.",
            "It emphasizes relative sizing and explicit uncertainty over false-precision, single-number "
            "estimates that create unrealistic commitments.",
        ],
        when_use=[
            "A PRD or epic needs to be turned into a sprint/milestone plan.",
            "Stakeholders are asking 'how long will this take' and a rough but defensible answer is needed.",
            "A task feels too large to safely implement, review, or test as a single unit.",
            "You need to identify which parts of a feature can be built in parallel.",
        ],
        when_not=[
            "The work is a single, well-understood task with no meaningful sub-parts.",
            "Precise time estimates are not needed (e.g. pure exploratory research spikes) — timebox instead.",
        ],
        prereqs=[
            "A reviewed PRD or clear requirement list (skills/10-planning/prd-and-spec-writing/SKILL.md).",
            "Team velocity history or comparable past task data, if available.",
        ],
        workflow=[
            ("Decompose by vertical slice", "Split work into end-to-end slices that each deliver observable value, not by technical layer alone."),
            ("Target 1-2 day tasks", "Break down any task estimated larger than roughly two days of focused work."),
            ("Separate must-have from nice-to-have", "Tag each task against the PRD's goals vs non-goals so scope cuts are easy under pressure."),
            ("Estimate relatively", "Use relative sizing (t-shirt sizes or story points) rather than false-precision hour estimates for uncertain work."),
            ("Call out unknowns explicitly", "Flag tasks with high uncertainty and consider a time-boxed spike before committing an estimate."),
            ("Sequence by dependency", "Identify which tasks block others and which can run in parallel across engineers."),
            ("Review as a team", "Have more than one engineer sanity-check estimates, especially for unfamiliar areas."),
            ("Track actuals vs estimates", "Record actual effort after completion to improve future estimation calibration."),
        ],
        decision=[
            ("Task has high technical uncertainty", "Timebox a short spike first, then re-estimate with that information instead of guessing."),
            ("Task naturally spans multiple layers (API + DB + UI)", "Split by vertical slice per capability rather than by layer, so each slice is independently testable."),
            ("Estimate significantly exceeds available time", "Cut scope (defer nice-to-haves) rather than compressing the estimate artificially."),
            ("Team has little history with the tech stack", "Widen the estimate range and flag it as low-confidence rather than presenting false precision."),
            ("Multiple engineers could work on it", "Break work into parallelizable tasks with clear interface contracts between them."),
            ("A task keeps ballooning during breakdown", "Split it further; if it still cannot go below ~2 days, treat it as its own mini-epic."),
            ("Stakeholders want a single delivery date", "Give a range with a stated confidence level, not a false-precision point estimate."),
        ],
        code_lang="text",
        code_intro="A work breakdown table combining vertical slices, sizing, and dependencies:",
        code=(
            "Feature: Bulk Order Export (from PRD REQ-1..REQ-6)\n"
            "\n"
            "| Task                                        | Slice type | Size | Depends on | Confidence |\n"
            "|----------------------------------------------|-----------|------|------------|------------|\n"
            "| Export request API + validation (REQ-1)       | vertical  | M    | -          | High       |\n"
            "| Async export job + CSV generation (REQ-2)     | vertical  | L    | Task 1     | Medium     |\n"
            "| Email notification on completion (REQ-2)      | vertical  | S    | Task 2     | High       |\n"
            "| Role-based access check (REQ non-func: sec.)  | vertical  | S    | Task 1     | High       |\n"
            "| Load test for 100k row export (REQ non-func)  | spike     | M    | Task 2     | Low        |\n"
            "\n"
            "Sizes: S = <1 day, M = 1-2 days, L = 3-5 days (split further if larger).\n"
            "Load test task is Low confidence -> timebox a 1-day spike before committing a firm size.\n"
        ),
        code_notes=[
            "Keep the breakdown table linked back to the PRD's requirement IDs for traceability.",
            "Re-run this breakdown whenever the PRD's scope changes materially.",
        ],
        code2_heading="Splitting an oversized task",
        code2=("text",
            "Example of decomposing a task that was initially too large to estimate confidently:",
            "Before: \"Build export job\" (estimated L, ~5 days, low confidence)\n"
            "\n"
            "After splitting by vertical concern:\n"
            "  1. CSV generation from an existing in-memory result set (S, high confidence)\n"
            "  2. Chunked/streamed generation for large result sets (M, medium confidence)\n"
            "  3. Background job scheduling + status tracking (M, high confidence)\n"
            "  4. Failure/retry handling for partial export failures (S, medium confidence)\n"
            "\n"
            "Each sub-task is now independently reviewable, testable, and estimable.\n"
        ),
        checklist=[
            "Every task traces back to a specific PRD requirement or explicit technical necessity.",
            "No task is estimated larger than roughly two days without being split further.",
            "High-uncertainty tasks are flagged and have a spike planned before firm estimation.",
            "Dependencies between tasks are identified so parallel work is possible.",
            "Estimates use relative sizing or ranges, not false-precision single numbers for uncertain work.",
            "Must-have vs nice-to-have tasks are explicitly tagged for scope-cut decisions.",
            "A team review (not a single person) validated the breakdown and estimates.",
        ],
        antipatterns=[
            ("Layer-based decomposition", "Splitting tasks purely by technical layer (all backend, then all frontend) so nothing is demoable until the very end."),
            ("False precision", "Giving a single-number hour estimate for a task with significant unknowns instead of a range with a stated confidence level."),
            ("Giant tasks", "Leaving multi-week tasks unbroken, hiding risk and making progress invisible until it's nearly due."),
            ("Estimating in isolation", "One person estimating everything alone without any peer sanity-check, especially for unfamiliar work."),
            ("Ignoring dependencies", "Planning tasks without identifying blocking relationships, causing engineers to be idle or blocked mid-sprint."),
            ("No calibration loop", "Never comparing actual effort against estimates, so estimation accuracy never improves over time."),
        ],
        verification=[
            "Every task in the plan maps to a PRD requirement or a stated technical necessity.",
            "No single task in the current sprint/milestone exceeds the team's agreed size ceiling.",
            "Dependency order was checked so no engineer is blocked without a fallback task.",
            "Post-completion, actual effort was recorded against the original estimate for calibration.",
        ],
        references=[
            "skills/10-planning/prd-and-spec-writing/SKILL.md",
            "skills/10-planning/definition-of-ready-and-done/SKILL.md",
            "Mike Cohn, 'Agile Estimating and Planning'.",
        ],
    ),
    dict(
        dir="10-planning", slug="architecture-decision-records", category="planning",
        tags=["adr", "documentation", "decision-making"],
        desc="Use when making a significant, hard-to-reverse technical decision that future engineers will need context on, such as choosing a database, framework, or integration pattern.",
        purpose=[
            "Significant technical decisions made verbally or in chat are forgotten within months, causing "
            "teams to relitigate the same debate or misunderstand why a system looks the way it does. This "
            "skill defines when and how to write an Architecture Decision Record (ADR) that captures the "
            "context, the decision, and the trade-offs at the time it was made.",
            "ADRs are lightweight by design: they are meant to be written in under an hour and read in under "
            "five minutes, not to be exhaustive design documents.",
        ],
        when_use=[
            "You are choosing between two or more viable technical approaches with real trade-offs.",
            "The decision is expensive or slow to reverse once implemented (e.g. database choice, API contract).",
            "The decision affects multiple teams or will outlive the original author's context.",
            "A past decision is being revisited and its original rationale is unclear or undocumented.",
        ],
        when_not=[
            "The decision is easily reversible and low-impact (e.g. naming a single internal variable).",
            "There is only one reasonable option with no real trade-off to record.",
        ],
        prereqs=[
            "templates/adr.template.md as the starting structure.",
            "A short list of the realistic options actually considered.",
            "Enough context (see skills/00-core/context-gathering/SKILL.md) to describe constraints accurately.",
        ],
        workflow=[
            ("Number and title the ADR", "Use a sequential ID (ADR-0001) and a short, specific title describing the decision, not the problem."),
            ("Write the context section first", "Describe the forces at play (technical, business, team) neutrally, before naming a preferred option."),
            ("List the options genuinely considered", "Include the rejected options with brief reasoning, not just the chosen one."),
            ("State the decision plainly", "Write the decision in one or two sentences in active voice: 'We will use PostgreSQL for...'"),
            ("Document consequences honestly", "List both positive outcomes and real trade-offs/costs accepted by making this choice."),
            ("Set the status", "Mark it Proposed until reviewed, then Accepted; mark old ADRs Superseded rather than deleting them."),
            ("Store it durably and discoverably", "Keep ADRs in a consistent location (e.g. docs/adr/) referenced from related code or READMEs."),
            ("Link forward and backward", "When superseding a decision, link the new ADR to the old one and vice versa."),
        ],
        decision=[
            ("Decision is easily reversible", "Skip the ADR; a code comment or PR description is sufficient."),
            ("Decision is contentious among the team", "Write the ADR to force explicit trade-off comparison rather than resolving it informally in chat."),
            ("A prior ADR's assumptions have changed", "Write a new ADR that explicitly supersedes the old one instead of editing history silently."),
            ("Decision spans multiple related choices", "Write one ADR per independently reversible decision rather than one giant ADR."),
            ("No real alternative was considered", "Skip the ADR, or note explicitly 'no viable alternative existed' rather than inventing false options."),
            ("Decision needs executive/stakeholder sign-off", "Route the ADR through the same approval path as skills/10-planning/prd-and-spec-writing/SKILL.md."),
        ],
        code_lang="markdown",
        code_intro="Filled example following templates/adr.template.md:",
        code=(
            "# ADR-0007: Use PostgreSQL as the primary datastore for the Orders service\n"
            "\n"
            "- Status: Accepted\n"
            "- Date: 2026-08-10\n"
            "- Deciders: Backend Guild\n"
            "\n"
            "## Context\n"
            "Orders service needs strong consistency for inventory decrement and supports\n"
            "up to 5k orders/minute at peak. Team has strong SQL experience; NoSQL options\n"
            "were considered for horizontal write scale that we do not currently need.\n"
            "\n"
            "## Decision\n"
            "We will use PostgreSQL (managed, single primary with read replicas) as the\n"
            "primary datastore for the Orders service.\n"
            "\n"
            "## Considered Options\n"
            "1. PostgreSQL - strong consistency, team familiarity, mature tooling.\n"
            "2. DynamoDB - higher write scale, but eventual consistency complicates inventory.\n"
            "3. MongoDB - flexible schema, but weaker transactional guarantees for this use case.\n"
            "\n"
            "## Consequences\n"
            "Positive: strong consistency simplifies inventory logic; team can move fast.\n"
            "Negative: horizontal write scaling requires future sharding work if volume 10x's.\n"
        ),
        code_notes=[
            "Keep the 'Considered Options' section honest — including the ones rejected is what makes an ADR useful later.",
            "Revisit ADRs during major re-architecture work rather than assuming they are still valid forever.",
        ],
        code2_heading="Superseding an old ADR",
        code2=("markdown",
            "How to link a new decision back to the one it replaces:",
            "# ADR-0014: Migrate Orders service from PostgreSQL to CockroachDB\n"
            "\n"
            "- Status: Accepted\n"
            "- Supersedes: ADR-0007\n"
            "\n"
            "## Context\n"
            "Order volume grew 12x since ADR-0007; single-primary PostgreSQL write\n"
            "throughput is now the top scaling bottleneck.\n"
            "\n"
            "## Decision\n"
            "We will migrate to CockroachDB for horizontally scalable writes.\n"
            "\n"
            "(ADR-0007 updated to add: \"Status: Superseded by ADR-0014\".)\n"
        ),
        checklist=[
            "The ADR has a sequential ID and a decision-focused title.",
            "Context is described neutrally before the decision is stated.",
            "At least one genuinely rejected alternative is documented with reasoning.",
            "The decision itself is a single clear, active-voice statement.",
            "Both positive and negative consequences are documented honestly.",
            "The ADR's status (Proposed/Accepted/Superseded) is current.",
            "Superseding ADRs link to the ADRs they replace, and vice versa.",
        ],
        antipatterns=[
            ("Decision-only ADRs", "Recording only the chosen option with no context or rejected alternatives, making the record useless for future reconsideration."),
            ("Editing history", "Modifying an old ADR to reflect a new decision instead of writing a new one that supersedes it."),
            ("Sales-pitch ADRs", "Listing only positive consequences and omitting real trade-offs or costs accepted."),
            ("ADR sprawl", "Writing an ADR for every trivial, reversible choice, diluting the signal of the ones that actually matter."),
            ("Orphaned ADRs", "Storing ADRs somewhere no one will find them, disconnected from the code or docs they explain."),
        ],
        verification=[
            "A new engineer reading the ADR alone can understand why the decision was made without asking anyone.",
            "The ADR's status reflects reality (not stuck as 'Proposed' long after implementation).",
            "Any decision it supersedes is explicitly linked and marked Superseded.",
        ],
        references=[
            "templates/adr.template.md",
            "Michael Nygard, 'Documenting Architecture Decisions' (original ADR concept).",
            "skills/20-architecture/system-design-process/SKILL.md",
        ],
    ),
    dict(
        dir="10-planning", slug="risk-and-assumption-log", category="planning",
        tags=["risk-management", "assumptions", "planning"],
        desc="Use when a plan or PRD depends on unverified assumptions or carries risks that could derail delivery, and those need to be tracked visibly rather than discovered later.",
        purpose=[
            "Unstated assumptions and untracked risks are a leading cause of late-stage surprises in software "
            "delivery. This skill provides a lightweight log format for recording assumptions, risks, and "
            "their mitigations so they are visible to the whole team and revisited as new information arrives.",
            "It is deliberately simple: a living table, not a heavyweight risk-management process, designed "
            "to be updated in minutes during planning meetings.",
        ],
        when_use=[
            "A plan depends on something outside the team's control (a third-party API, another team's delivery).",
            "You are estimating work with significant technical or requirements uncertainty.",
            "A stakeholder decision is pending and work is proceeding on a best guess in the meantime.",
            "A previous project failed due to an unmanaged risk and you want to avoid repeating it.",
        ],
        when_not=[
            "The task is small, fully understood, and has no external dependencies or open questions.",
        ],
        prereqs=[
            "A draft plan or PRD to anchor the assumptions and risks against.",
            "A shared, visible place to maintain the log (ticket, wiki page, or PRD appendix).",
        ],
        workflow=[
            ("Brainstorm assumptions", "List everything the plan takes for granted: technical, resourcing, third-party, and timing assumptions."),
            ("Brainstorm risks separately", "List things that could go wrong even if assumptions hold, e.g. a dependency being late or scope growing."),
            ("Rate likelihood and impact", "Score each risk on rough likelihood and impact (Low/Medium/High) to prioritize attention."),
            ("Assign a mitigation or contingency", "For medium/high risks, define what you will do if the risk materializes, not just hope it doesn't."),
            ("Assign an owner", "Every open risk and assumption needs a named owner responsible for monitoring and resolving it."),
            ("Review on a cadence", "Revisit the log at each planning checkpoint, closing resolved items and adding new ones."),
            ("Escalate blocking risks early", "If a high-impact risk is close to materializing, raise it to stakeholders before it becomes a crisis."),
        ],
        decision=[
            ("Assumption is easy to verify quickly", "Verify it immediately rather than logging it as an ongoing risk."),
            ("Risk has low likelihood and low impact", "Log it for visibility but do not invest mitigation effort — accept it explicitly."),
            ("Risk has high likelihood or high impact", "Define and, if cheap, implement a concrete mitigation or contingency plan now."),
            ("Risk depends on another team's delivery", "Get an explicit commitment or fallback plan from that team, not just an assumption it will land on time."),
            ("An assumption turns out to be false mid-project", "Update the plan immediately and communicate the impact, rather than continuing silently."),
            ("Risk log grows very long", "Focus active discussion on Medium/High items; keep Low items archived but visible."),
        ],
        code_lang="text",
        code_intro="A lightweight risk and assumption log format:",
        code=(
            "Risk & Assumption Log — Bulk Order Export\n"
            "-------------------------------------------\n"
            "Assumptions:\n"
            "A1: Third-party email service supports attachments up to 25MB. [Owner: BE] [Unverified]\n"
            "A2: Finance team's export volume stays under 100k rows for the next 12 months. [Owner: PM]\n"
            "\n"
            "Risks:\n"
            "| ID | Risk                                   | Likelihood | Impact | Mitigation                          | Owner |\n"
            "|----|-----------------------------------------|-----------|--------|--------------------------------------|-------|\n"
            "| R1 | Export job times out for very large sets| Medium    | High   | Add chunked processing + retry       | BE    |\n"
            "| R2 | Email provider rate-limits large sends   | Low       | Medium | Fallback: in-app download link       | BE    |\n"
            "| R3 | Finance needs Excel not CSV (scope risk) | Medium    | Medium | Confirm format explicitly in PRD     | PM    |\n"
            "\n"
            "Review cadence: revisit at each sprint planning; close items once verified/resolved.\n"
        ),
        code_notes=[
            "Convert 'Unverified' assumptions to either 'Confirmed' or a tracked risk as soon as they are checked.",
            "Do not let the log become a graveyard — actively close items each review cycle.",
        ],
        code2_heading="Escalating a materializing risk",
        code2=("text",
            "Example escalation message when a logged risk is about to become real:",
            "Subject: Risk R1 (export timeout) is materializing - needs a decision\n"
            "\n"
            "Status: Load testing shows the export job times out around 60k rows,\n"
            "below our 100k target (see R1 in the risk log).\n"
            "\n"
            "Options:\n"
            "  1. Ship with a documented 60k row limit for v1, raise it in v1.1 (recommended)\n"
            "  2. Delay launch by 1 week to implement chunked processing now\n"
            "\n"
            "Requesting a decision from: Product Owner, Eng Lead, by EOD Thursday.\n"
        ),
        checklist=[
            "Assumptions and risks are logged separately with distinct handling.",
            "Every Medium/High risk has a named owner and a concrete mitigation or contingency.",
            "Unverified assumptions are flagged as such, not silently treated as fact.",
            "The log is reviewed on a regular cadence, not written once and forgotten.",
            "High-impact risks close to materializing were escalated to stakeholders proactively.",
            "Resolved risks/assumptions are marked closed rather than left stale.",
        ],
        antipatterns=[
            ("Silent assumptions", "Proceeding on unverified assumptions without ever writing them down, so no one notices when they are wrong."),
            ("Risk theater", "Logging risks once during kickoff and never revisiting them for the rest of the project."),
            ("Ownerless risks", "Listing risks with no assigned owner, so nobody actually monitors or mitigates them."),
            ("Hope as a strategy", "Identifying a high-impact risk but defining no mitigation or contingency plan at all."),
            ("Late escalation", "Sitting on a materializing high-impact risk until it becomes an emergency instead of raising it early."),
        ],
        verification=[
            "Every assumption has a status: Confirmed, Unverified, or Invalidated.",
            "Every Medium/High risk has an owner and a stated mitigation.",
            "The log's last-updated date is recent relative to the project timeline, not stale.",
            "At least one planning checkpoint explicitly reviewed the log as an agenda item.",
        ],
        references=[
            "skills/10-planning/prd-and-spec-writing/SKILL.md",
            "skills/10-planning/architecture-decision-records/SKILL.md",
            "PMI, 'Risk Management' guidance adapted for lightweight software delivery.",
        ],
    ),
    dict(
        dir="10-planning", slug="definition-of-ready-and-done", category="planning",
        tags=["dor", "dod", "agile", "quality-gates"],
        desc="Use when a team needs explicit, shared criteria for when a work item is ready to start and when it is truly finished, to avoid starting underspecified work or shipping incomplete features.",
        purpose=[
            "Teams without an explicit Definition of Ready (DoR) start work on underspecified tickets, "
            "causing mid-sprint churn. Teams without an explicit Definition of Done (DoD) ship features that "
            "are 'code complete' but missing tests, docs, or monitoring. This skill defines both gates "
            "concretely and shows how to apply them consistently.",
            "DoR and DoD are team-level contracts: once agreed, they should be enforced the same way for "
            "every ticket, not applied selectively based on deadline pressure.",
        ],
        when_use=[
            "A team is repeatedly starting work that turns out to be underspecified mid-sprint.",
            "Features are marked 'done' but later found missing tests, docs, or monitoring.",
            "A new team is being formed and needs a shared quality bar from day one.",
            "You are reviewing whether a ticket can move into the next stage of a workflow (backlog -> sprint -> done).",
        ],
        when_not=[
            "The team already has a documented, working DoR/DoD and this ticket simply needs to be checked against it.",
            "The work is a single-person spike explicitly exempted from normal DoD (e.g. throwaway prototype).",
        ],
        prereqs=[
            "Team agreement on what belongs in DoR and DoD (this is a one-time setup cost).",
            "A ticketing system or checklist mechanism to attach these criteria to work items.",
        ],
        workflow=[
            ("Draft the Definition of Ready", "List the minimum information a ticket must have before it can be pulled into a sprint (acceptance criteria, estimate, dependencies known)."),
            ("Draft the Definition of Done", "List everything required beyond 'code compiles': tests, docs, code review, monitoring, deployed and verified."),
            ("Socialize and agree as a team", "Review both definitions with the whole team and adjust until everyone will actually honor them."),
            ("Attach the checklist to the workflow", "Add DoR as a gate before 'sprint start' and DoD as a gate before 'done' in the ticketing tool."),
            ("Apply consistently", "Reject tickets that fail DoR back to refinement; reject 'done' claims that fail DoD back to in-progress."),
            ("Revisit periodically", "Update DoR/DoD as the team matures — e.g. adding accessibility checks once that becomes a standing concern."),
        ],
        decision=[
            ("Ticket lacks clear acceptance criteria", "Fails DoR — send back to refinement before it enters a sprint."),
            ("Feature works but has no automated test", "Fails DoD — not shippable as 'done' regardless of deadline pressure."),
            ("A story is an exploratory spike", "Apply a reduced DoD explicitly agreed in advance (e.g. 'no production code required'), not the full checklist."),
            ("Team is under deadline pressure to skip DoD items", "Make the trade-off explicit and get a named approver to accept the risk, rather than silently lowering the bar."),
            ("DoR/DoD items feel irrelevant for a specific ticket type", "Adjust the team-level definition explicitly rather than ignoring it case-by-case."),
        ],
        code_lang="text",
        code_intro="Example Definition of Ready and Definition of Done for a backend team:",
        code=(
            "Definition of Ready (before a ticket enters a sprint)\n"
            "-------------------------------------------------------\n"
            "[ ] Problem/goal stated in one sentence\n"
            "[ ] Acceptance criteria are specific and testable\n"
            "[ ] Dependencies (other teams, external services) identified\n"
            "[ ] Rough size estimate agreed (see work-breakdown-and-estimation)\n"
            "[ ] UX/API contract available if the ticket involves a user-facing or API change\n"
            "\n"
            "Definition of Done (before a ticket is marked done)\n"
            "-------------------------------------------------------\n"
            "[ ] Code implements all stated acceptance criteria\n"
            "[ ] Automated tests cover the acceptance criteria (unit + integration as applicable)\n"
            "[ ] Code reviewed and approved by at least one other engineer\n"
            "[ ] Documentation updated (README, API docs, or runbook as applicable)\n"
            "[ ] Deployed to at least staging and manually verified\n"
            "[ ] Monitoring/alerting in place for new failure modes introduced\n"
            "[ ] No known regressions in existing automated test suite\n"
        ),
        code_notes=[
            "Keep both lists short (5-8 items); a checklist nobody reads provides no value.",
            "Print the DoD on the PR template so it is checked at the natural point of submission.",
        ],
        code2_heading="Handling a DoD exception explicitly",
        code2=("text",
            "Example of an explicit, tracked exception instead of silently lowering the bar:",
            "Ticket: ORD-482 Add order channel column to export\n"
            "\n"
            "DoD exception requested: ship without a staging deploy due to environment outage.\n"
            "Approved by: Eng Lead (2026-08-15).\n"
            "Follow-up: verify in staging within 24h of environment restoration, tracked as\n"
            "ORD-483, blocking the next release until confirmed.\n"
        ),
        checklist=[
            "The team has an explicitly agreed, written DoR and DoD (not tribal knowledge).",
            "Tickets failing DoR are sent back to refinement rather than started anyway.",
            "Work claiming 'done' is checked against every DoD item, not just 'code compiles'.",
            "Any explicit exception (e.g. reduced DoD for a spike) is agreed in advance, not applied retroactively.",
            "DoR/DoD are revisited periodically as the team's standards evolve.",
        ],
        antipatterns=[
            ("Tribal knowledge DoD", "Relying on 'everyone knows what done means' instead of a written, agreed checklist."),
            ("Selective enforcement", "Applying DoD strictly for some tickets but waiving it silently under deadline pressure for others."),
            ("DoR as a formality", "Rubber-stamping tickets into a sprint without actually checking acceptance criteria are testable."),
            ("Done means merged", "Treating a merged PR as 'done' without deployment, verification, or monitoring in place."),
            ("Static definitions", "Never updating DoR/DoD even as the team learns painful lessons that should be codified."),
        ],
        verification=[
            "A sample of recently started tickets shows each passed the team's DoR at start time.",
            "A sample of recently closed tickets shows each satisfies every DoD item.",
            "Any DoD exception applied has a recorded, explicit approval.",
        ],
        references=[
            "skills/10-planning/work-breakdown-and-estimation/SKILL.md",
            "skills/90-delivery/shipping-checklist/SKILL.md",
            "Scrum Guide — Definition of Done concept.",
        ],
    ),
]
