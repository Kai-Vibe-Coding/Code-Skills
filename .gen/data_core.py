SKILLS = [
    dict(
        dir="00-core", slug="engineering-principles", category="core",
        tags=["principles", "fundamentals", "agent-behavior"],
        desc="Use when starting any engineering task and you need a shared baseline of quality, simplicity, and safety principles to apply before writing code.",
        purpose=[
            "This skill establishes the baseline engineering principles that every other skill in this "
            "catalog assumes: favor simplicity, make small reversible changes, write for the next reader, "
            "and verify before declaring done.",
            "It exists so that agents and humans do not have to relearn these fundamentals in every "
            "task-specific skill, and so that reviewers have a shared vocabulary for pushing back on "
            "over-engineered or under-verified changes.",
        ],
        when_use=[
            "You are beginning any coding, design, or review task and want a shared quality bar.",
            "You are unsure whether a proposed change is 'simple enough' or 'safe enough' to ship.",
            "You are onboarding a new contributor (human or agent) to how this team works.",
            "You are reviewing a pull request and need objective criteria beyond personal taste.",
            "You are deciding between two designs that both technically satisfy the requirements.",
            "You are tempted to add an abstraction and want to sanity-check whether it is justified.",
        ],
        when_not=[
            "You need a concrete step-by-step procedure for a specific technology — use the relevant specialized skill instead.",
            "You are deep in an unrelated domain-specific decision (e.g. choosing an index type) — see the matching skill.",
            "The team already has a documented, conflicting standard for this specific case — defer to that.",
            "You are evaluating a purely cosmetic style choice already covered by a linter/formatter config.",
        ],
        prereqs=[
            "None — this is the entry point for the whole catalog.",
            "Familiarity with the specific language/framework of the task at hand helps but is not required to apply these principles.",
            "Access to the project's existing tests, linters, and build tooling for the verification step.",
        ],
        workflow=[
            ("Prefer the simplest solution that works", "Before adding an abstraction, ask whether the problem actually requires it today, not hypothetically."),
            ("Make changes small and reversible", "Split work into commits/PRs that can be reviewed and rolled back independently."),
            ("Write for the next reader", "Optimize for readability over cleverness; a change that saves 2 minutes of typing but costs 20 minutes of comprehension is a net loss."),
            ("State assumptions explicitly", "When requirements are ambiguous, write down the assumption you are proceeding with instead of silently guessing."),
            ("Match existing conventions first", "Follow the codebase's existing patterns before introducing a personally preferred style."),
            ("Verify before declaring done", "Run the tests, linters, or manual checks that prove the change works, not just that it compiles."),
            ("Leave the codebase better than you found it", "Fix small, directly related issues you encounter, but do not scope-creep into unrelated refactors."),
            ("Communicate trade-offs", "When a shortcut was taken deliberately, say so and explain the trade-off instead of hiding it."),
        ],
        decision=[
            ("Two designs solve the problem equally well", "Choose the one with fewer moving parts and less new vocabulary for the team to learn."),
            ("Requirements are ambiguous and no one is available to ask", "Make the most conservative, reversible assumption and document it prominently."),
            ("A quick hack would unblock you today", "Only take it if it is clearly labeled, tracked, and does not compromise correctness or security."),
            ("You find an unrelated bug while working", "Log it separately; fix it inline only if it is a one-line, low-risk change directly in your path."),
            ("A new abstraction would remove duplication", "Only introduce it once the same logic is needed in three or more places (rule of three)."),
            ("Team convention conflicts with a 'best practice' you know", "Follow the team convention and raise the discrepancy separately rather than deviating silently."),
            ("Deadline pressure tempts skipping verification", "Reduce scope instead of skipping verification; an unverified change is not actually finished."),
        ],
        code_lang="text",
        code_intro="A short principles checklist to paste at the top of a design doc or PR description:",
        code=(
            "Engineering Principles Checklist\n"
            "---------------------------------\n"
            "[ ] Simplicity: could this be solved with less code / fewer moving parts?\n"
            "[ ] Reversibility: can this change be rolled back safely and quickly?\n"
            "[ ] Readability: would a new teammate understand this in under 5 minutes?\n"
            "[ ] Assumptions: are ambiguous requirements documented explicitly?\n"
            "[ ] Convention: does this match how the rest of the codebase already does it?\n"
            "[ ] Verification: is there a concrete way to prove this works (test, log, metric)?\n"
            "[ ] Scope: does this change avoid unrelated, uncoordinated refactors?\n"
            "[ ] Trade-offs: are any deliberate shortcuts called out explicitly, not hidden?\n"
            "\n"
            "Example PR description applying the checklist:\n"
            "\n"
            "  Title: Add retry to payment webhook delivery\n"
            "  - Simplicity: reused existing Polly retry policy, no new library added.\n"
            "  - Reversibility: change is feature-flagged behind Payments.WebhookRetry.\n"
            "  - Assumption: treating HTTP 5xx and timeouts as retryable, 4xx as terminal.\n"
            "  - Verified: added unit test WebhookSenderTests.RetriesOn5xx, ran dotnet test.\n"
            "  - Trade-off: fixed 3 retries with exponential backoff chosen over a queue-based\n"
            "    approach for this iteration; revisit if webhook volume grows 10x.\n"
        ),
        code_notes=[
            "Use this checklist format verbatim in PR descriptions to make principle application visible to reviewers.",
            "Keep each checklist line answerable in one sentence; if it needs a paragraph, the change may be too large.",
        ],
        code2_heading="Recognizing an over-engineered alternative",
        code2=("text",
            "Contrast the same task solved with unnecessary generality, to make the anti-pattern concrete:",
            "Over-engineered version (avoid):\n"
            "  - Introduces IWebhookDeliveryStrategy with 3 implementations for 1 real use case.\n"
            "  - Adds a generic RetryPolicyFactory configurable via 12 new settings.\n"
            "  - Ships with no test proving the one real retry path actually works.\n"
            "  - PR description: \"Refactored webhook delivery to be more extensible.\"\n"
            "\n"
            "Why this fails the checklist:\n"
            "  - Simplicity: 3x the code for 1 real requirement.\n"
            "  - Verification: no test asserts the behavior that was actually requested.\n"
            "  - Scope: 'more extensible' is not a stated requirement — it is speculative.\n"
        ),
        checklist=[
            "The simplest viable design was chosen and the reasoning is recorded.",
            "The change can be reverted independently of unrelated work.",
            "Any assumption made about ambiguous requirements is written down.",
            "The change follows existing codebase conventions rather than introducing a new personal style.",
            "A verification step (test, build, manual check) was actually run, not just planned.",
            "The change stays within the requested scope, with unrelated fixes called out separately.",
            "Deliberate trade-offs or shortcuts are explicitly documented, not hidden.",
            "No abstraction was added solely for hypothetical future requirements.",
            "A teammate unfamiliar with the change could review it without needing a walkthrough.",
        ],
        antipatterns=[
            ("Speculative generality", "Building configuration, plugin systems, or abstractions for requirements that do not exist yet. Build for today's requirements and refactor when the second real use case appears."),
            ("Silent assumptions", "Proceeding on an ambiguous requirement without stating the assumption anywhere. Always surface it in the PR description or a comment."),
            ("Big-bang changes", "Bundling unrelated refactors, dependency upgrades, and features into one giant diff that is impossible to review or revert safely."),
            ("Declaring done without verification", "Assuming code works because it compiles or 'looks right'. Always run the smallest test that would catch a regression."),
            ("Style crusades", "Rewriting unrelated code to match a personally preferred style instead of the team's existing convention."),
            ("Hidden shortcuts", "Taking a deliberate shortcut (e.g. skipping an edge case) without telling anyone, creating a silent landmine for later."),
        ],
        verification=[
            "The PR description states what was verified and how (command run, output observed).",
            "A reviewer can identify the single main change and any explicitly called-out side fixes.",
            "No TODO, placeholder, or 'figure this out later' text remains in the shipped change.",
            "Any deliberate trade-off is documented in the PR description or a code comment.",
            "The diff does not touch files unrelated to the stated task.",
        ],
        references=[
            "Kent Beck, 'Tidy First?' — on small, reversible, separately-reviewable changes.",
            "Robert C. Martin, 'Clean Code' — on writing for the next reader.",
            "skills/00-core/context-gathering/SKILL.md — how to gather the context needed before applying these principles.",
            "skills/70-quality/code-review/SKILL.md — how these principles are checked in review.",
            "skills/90-delivery/shipping-checklist/SKILL.md — final gate before release.",
        ],
    ),
    dict(
        dir="00-core", slug="agent-build-workflow", category="core",
        tags=["agent-workflow", "process", "automation"],
        desc="Use when a coding agent is executing a multi-step build, fix, or feature task and needs a repeatable loop for planning, acting, and verifying work.",
        purpose=[
            "Coding agents produce more reliable results when they follow an explicit plan-act-verify loop "
            "instead of free-form editing. This skill defines that loop: understand the task, form a plan, "
            "make the smallest change that satisfies it, run verification, and report progress — repeating "
            "until the task is complete.",
            "It reduces two common agent failure modes: silently drifting from the original request, and "
            "declaring success without actually proving the change works.",
        ],
        when_use=[
            "An agent is given a coding task spanning more than a single trivial edit.",
            "The task requires touching multiple files or coordinating several changes.",
            "You need a consistent way to track partially completed multi-step work.",
            "The task has ambiguous scope and needs to be broken down before execution.",
            "Multiple sub-tasks depend on each other and must be sequenced correctly.",
        ],
        when_not=[
            "The task is a single-line, unambiguous fix — just make the edit and verify directly.",
            "You are only answering a question with no code change involved.",
            "The task is already fully specified as a single atomic step with no sub-decisions.",
        ],
        prereqs=[
            "Read access to the target repository and its existing tests/build tooling.",
            "skills/00-core/context-gathering/SKILL.md applied to understand the codebase first.",
            "A clear statement of the requested outcome, even if some details need clarifying assumptions.",
        ],
        workflow=[
            ("Restate the task", "Summarize the requested outcome in your own words, including explicit and implicit acceptance criteria."),
            ("Gather context", "Locate relevant files, existing conventions, and prior art before writing any code."),
            ("Form a plan", "Break the task into an ordered list of small, independently verifiable steps."),
            ("Track the plan explicitly", "Maintain a visible list of steps with status (pending/in_progress/done/blocked) as work proceeds."),
            ("Execute the smallest next step", "Make one focused change at a time rather than editing many files speculatively."),
            ("Verify immediately", "Run the build, tests, or linter scoped to the change just made, not just at the very end."),
            ("Adjust the plan when reality disagrees", "If a step reveals the plan was wrong, revise it explicitly rather than silently improvising."),
            ("Report and iterate", "Summarize what changed and what remains, then continue to the next step until the plan is complete."),
        ],
        decision=[
            ("Task is a single well-defined bug fix", "Skip formal planning; fix, verify, and report directly."),
            ("Task spans multiple files or subsystems", "Write an explicit step list before editing anything."),
            ("A step reveals the plan was wrong", "Stop, revise the plan, and continue — do not silently improvise around it."),
            ("Verification tooling is missing or broken", "Fix or note the gap explicitly rather than skipping verification silently."),
            ("A step is blocked by an external dependency", "Mark it blocked, explain why, and continue with independent steps if any exist."),
            ("The user's request is ambiguous about scope", "State the assumed scope in the plan before executing, so it can be corrected early."),
        ],
        code_lang="text",
        code_intro="A minimal task-tracking format an agent can maintain across a multi-step task:",
        code=(
            "Task: Add pagination to GET /orders\n"
            "\n"
            "Restated acceptance criteria:\n"
            "  - Endpoint accepts pageNumber/pageSize query params (default 1/20).\n"
            "  - Response includes totalCount and totalPages.\n"
            "  - Existing callers without query params keep working unchanged.\n"
            "\n"
            "Plan:\n"
            "1. [done]        Read existing OrdersController and repository for conventions\n"
            "2. [done]        Add PageNumber/PageSize query params with validation\n"
            "3. [in_progress] Update repository query to apply Skip/Take\n"
            "4. [pending]     Add/adjust integration test for paginated response shape\n"
            "5. [pending]     Run dotnet test --filter Orders and confirm green\n"
            "\n"
            "Verification performed so far:\n"
            "- dotnet build succeeded after step 2\n"
            "- Manual curl against /orders?pageNumber=1&pageSize=5 returned expected shape\n"
            "\n"
            "Next action: implement step 3, then rerun the targeted test in step 5.\n"
        ),
        code_notes=[
            "Persist this plan somewhere durable (PR description, issue comment, or scratch file) so progress survives interruptions.",
            "Update the status markers in real time, not retroactively at the end of the task.",
        ],
        code2_heading="What silent plan drift looks like",
        code2=("text",
            "A red-flag transcript pattern to recognize and avoid in agent output:",
            "Turn 1: \"Plan: 1) add param 2) update query 3) add test\"\n"
            "Turn 2: *edits 6 unrelated files, renames 2 classes, upgrades a NuGet package*\n"
            "Turn 3: \"Done! Also cleaned up some other things while I was in there.\"\n"
            "\n"
            "Why this fails: the plan was abandoned without acknowledgement, unrelated\n"
            "changes were bundled in, and 'cleaned up' hides scope that a reviewer now has\n"
            "to reverse-engineer instead of reviewing intentionally.\n"
            "\n"
            "Corrected behavior: if extra cleanup seems valuable, stop and say so explicitly:\n"
            "\"I also noticed X is duplicated in 3 places — want me to extract it in a\n"
            "follow-up, or is that out of scope for this task?\"\n"
        ),
        checklist=[
            "The task was restated with explicit acceptance criteria before any edit was made.",
            "Work was broken into small, independently verifiable steps.",
            "Each step was verified before moving to the next one.",
            "Any plan revision (due to new information) was made explicit, not silent.",
            "Blocked steps are labeled as such with a stated reason, not silently dropped.",
            "A final summary lists what changed and how it was verified.",
            "Any additional cleanup beyond the stated scope was proposed, not silently applied.",
            "The plan's status markers were kept current throughout, not reconstructed after the fact.",
        ],
        antipatterns=[
            ("Edit-everything-then-test-once", "Making sweeping changes across many files before running any verification, making it hard to isolate what broke."),
            ("Silent plan drift", "Quietly abandoning the stated plan mid-task without acknowledging the change, confusing anyone reviewing progress."),
            ("Verification theater", "Running an unrelated or trivial check and calling it 'verified' instead of the smallest test that would actually catch a regression."),
            ("Unbounded scope creep", "Using a bug fix task as an excuse to refactor unrelated modules without calling it out separately."),
            ("Invisible progress", "Doing multi-step work without ever externalizing the plan, so a reviewer cannot tell what is left."),
        ],
        verification=[
            "A step-by-step log or plan exists showing what was done in what order.",
            "Each completed step has a corresponding verification action (test run, build, manual check).",
            "The final report distinguishes 'done', 'in progress', and 'blocked' items clearly.",
            "Re-reading the original task against the final summary confirms every acceptance criterion was addressed.",
        ],
        references=[
            "skills/00-core/context-gathering/SKILL.md",
            "skills/00-core/requirements-to-code-traceability/SKILL.md",
            "skills/70-quality/debugging-methodology/SKILL.md",
            "skills/10-planning/work-breakdown-and-estimation/SKILL.md",
        ],
    ),
    dict(
        dir="00-core", slug="requirements-to-code-traceability", category="core",
        tags=["traceability", "requirements", "compliance"],
        desc="Use when you need to prove that every requirement, ticket, or acceptance criterion is actually implemented and tested somewhere in the codebase.",
        purpose=[
            "Untraceable requirements silently disappear during implementation, causing missed acceptance "
            "criteria that surface only in production or during an audit.",
            "This skill provides a lightweight way to link requirements to the code and tests that satisfy "
            "them, so gaps are visible before release rather than after, and so audits can be answered with "
            "evidence instead of memory.",
        ],
        when_use=[
            "You are implementing a feature with multiple discrete acceptance criteria.",
            "The project is subject to audit, compliance, or contractual sign-off requirements.",
            "A PR needs to demonstrate which ticket items are actually addressed.",
            "A large feature is being built incrementally across several PRs and coverage must be tracked.",
        ],
        when_not=[
            "The change is a trivial, single-criterion bug fix with no formal requirement document.",
            "The team has no requirement-tracking system at all and adding one is out of scope for this task.",
        ],
        prereqs=[
            "A source of requirements (ticket, PRD, or acceptance criteria list).",
            "skills/10-planning/prd-and-spec-writing/SKILL.md if the PRD itself still needs to be written.",
            "A test framework capable of naming/tagging individual test cases.",
        ],
        workflow=[
            ("List atomic requirements", "Break the PRD or ticket into individually testable statements, each with a stable ID (e.g. REQ-1)."),
            ("Map each requirement to code", "Identify the file(s)/class(es) that implement each requirement as you build it."),
            ("Map each requirement to a test", "Ensure at least one automated test asserts the requirement's observable behavior."),
            ("Maintain a traceability matrix", "Keep a simple table of requirement ID -> code location -> test ID, updated as work progresses."),
            ("Flag orphans", "Any requirement with no code/test mapping, or any test with no requirement mapping, is a gap to resolve before release."),
            ("Review the matrix before sign-off", "Walk the matrix with a reviewer or stakeholder to confirm every row is actually 'Done', not just claimed."),
            ("Attach the matrix to the PR", "Include or link the traceability matrix so reviewers can confirm coverage without re-reading the whole diff."),
        ],
        decision=[
            ("Small bug fix, single criterion", "Use an informal one-line trace in the PR description instead of a full matrix."),
            ("Regulated or contractual feature", "Maintain a persistent traceability matrix file reviewed as part of sign-off."),
            ("Requirement changes mid-implementation", "Update the requirement ID's description and re-verify its code/test mapping, do not silently drop it."),
            ("A requirement has no feasible automated test", "Document the manual verification procedure explicitly in the matrix instead of leaving it blank."),
            ("Feature spans multiple PRs", "Carry the matrix forward in the tracking issue and update it per PR rather than recreating it each time."),
        ],
        code_lang="text",
        code_intro="A minimal traceability matrix that can live in a PR description or a docs file:",
        code=(
            "| Req ID | Requirement                          | Code                         | Test                    | Status |\n"
            "|--------|---------------------------------------|------------------------------|--------------------------|--------|\n"
            "| REQ-1  | User can reset password via email     | AuthController.RequestReset   | AuthControllerTests.T1   | Done   |\n"
            "| REQ-2  | Reset link expires after 30 minutes   | PasswordResetToken.IsExpired  | PasswordResetTokenTests  | Done   |\n"
            "| REQ-3  | Rate limit reset requests per account | ResetRateLimiter              | ResetRateLimiterTests    | Gap    |\n"
            "| REQ-4  | Reset events are audit logged         | AuditLogger.LogPasswordReset  | AuditLoggerTests         | Done   |\n"
            "\n"
            "REQ-3 has code but no automated test yet - blocking release sign-off.\n"
            "\n"
            "Sign-off note (attach to PR):\n"
            "  4 of 4 requirements have code. 3 of 4 have passing automated tests.\n"
            "  REQ-3 tracked as follow-up ticket JIRA-4821 before this feature can be marked done.\n"
        ),
        code_notes=[
            "Store the matrix in the PR description for small features, or a linked docs/traceability/<feature>.md for larger ones.",
            "Treat 'Gap' rows as release blockers unless explicitly and visibly waived by a decision-maker.",
        ],
        code2_heading="Escalating an unresolved gap",
        code2=("text",
            "Example note attached to a release sign-off request when a gap cannot be closed in time:",
            "Release sign-off request for v2.4.0:\n"
            "  Coverage: 12/13 requirements have code + passing tests.\n"
            "  Open gap: REQ-9 (bulk export rate limiting) has code but no automated test;\n"
            "  manual test performed 2026-08-19 by QA, see JIRA-5102 for the automation follow-up.\n"
            "  Requesting explicit waiver from: Release Owner, QA Lead.\n"
            "  Waiver granted by: <name>, <date>. Follow-up ticket due: <sprint>.\n"
        ),
        checklist=[
            "Every acceptance criterion has a stable requirement ID.",
            "Each requirement ID maps to at least one code location and one test.",
            "No requirement is marked 'done' without a corresponding passing test or documented manual check.",
            "The traceability matrix is attached to or linked from the PR.",
            "Any requirement that changed scope mid-implementation is reflected in the matrix.",
            "Gaps are tracked as follow-up tickets, not silently dropped.",
            "Any waived gap names an explicit approver and a due date for the follow-up.",
            "The matrix's requirement IDs match the IDs used in the originating ticket or PRD.",
        ],
        antipatterns=[
            ("Implicit coverage", "Assuming a requirement is covered because 'the tests probably exercise it' without an explicit mapping."),
            ("Matrix drift", "Writing the matrix once at the start and never updating it as implementation details change."),
            ("Test without requirement", "Adding tests for behavior that traces back to no stated requirement, inflating scope silently."),
            ("Requirement without test", "Marking a requirement 'done' purely because code was written, without proving the behavior via a test."),
            ("Silent gap waiving", "Shipping with an unresolved 'Gap' row without any stakeholder sign-off or tracked follow-up."),
        ],
        verification=[
            "Every row in the traceability matrix has a non-empty code and test column, or an explicit documented exception.",
            "Running the mapped tests actually exercises the described requirement (spot-check a sample).",
            "A reviewer can answer 'is REQ-N done?' by reading the matrix alone.",
            "Any waived gap has a linked follow-up ticket and a named approver.",
        ],
        references=[
            "skills/10-planning/prd-and-spec-writing/SKILL.md",
            "skills/70-quality/test-case-design/SKILL.md",
            "ISO/IEC/IEEE 29148 — Requirements engineering traceability practices.",
            "skills/90-delivery/shipping-checklist/SKILL.md",
        ],
    ),
    dict(
        dir="00-core", slug="context-gathering", category="core",
        tags=["discovery", "codebase-exploration", "research"],
        desc="Use when starting work in an unfamiliar codebase or module and you need to understand existing conventions before making changes.",
        purpose=[
            "Changes that ignore existing conventions create inconsistency and rework. This skill describes "
            "a fast, targeted process for learning enough about a codebase's structure, patterns, and "
            "constraints before writing code, without over-investing time in exploration for its own sake.",
            "It balances two failure modes: acting on incomplete understanding and causing rework, versus "
            "over-exploring and stalling on a task that could have started sooner.",
        ],
        when_use=[
            "You are making your first change in a repository or module you have not touched before.",
            "The task description references files, systems, or terms you do not yet understand.",
            "You suspect there may already be an existing pattern for what you are about to build.",
            "You are about to introduce a new dependency and want to check if an equivalent already exists.",
        ],
        when_not=[
            "You already have full, current context on the exact files you need to change.",
            "The task is isolated to a brand-new file with no existing conventions to follow.",
        ],
        prereqs=[
            "Read access to the repository, its README, and its build/test configuration.",
        ],
        workflow=[
            ("Read the entry points", "Check README, CONTRIBUTING, and top-level docs for stated conventions and architecture."),
            ("Find an analogous example", "Search for an existing feature similar to what you are building and study its structure end-to-end."),
            ("Identify the test and build commands", "Locate how the project is built, linted, and tested so you can verify your change the same way."),
            ("Note naming and layering conventions", "Observe folder structure, naming patterns, and layering (e.g. controller -> service -> repository) actually used."),
            ("Check for existing utilities", "Search for helpers, base classes, or shared libraries before writing new one-off logic."),
            ("Check version and dependency constraints", "Confirm the language/framework/library versions in use so new code stays compatible."),
            ("Scope your exploration", "Stop once you have enough context to proceed confidently; do not read the entire codebase."),
        ],
        decision=[
            ("A similar feature already exists", "Follow its exact pattern unless there is a documented reason to deviate."),
            ("No similar feature exists", "Follow the closest architectural layer's conventions and note the new pattern in the PR description."),
            ("Conventions are inconsistent across the codebase", "Follow the most recently updated, most-tested example, and flag the inconsistency rather than picking arbitrarily."),
            ("Time pressure limits exploration", "Prioritize reading the file(s) you will directly modify and their immediate dependents/dependencies."),
            ("Documentation contradicts the actual code", "Trust the code and tests over stale docs, and note the discrepancy for a follow-up doc fix."),
        ],
        code_lang="bash",
        code_intro="A quick context-gathering script using common CLI search tools:",
        code=(
            "# 1. Understand top-level layout and stated conventions\n"
            "cat README.md CONTRIBUTING.md 2>/dev/null | head -100\n"
            "\n"
            "# 2. Find an analogous existing feature (example: another CRUD endpoint)\n"
            "grep -rl \"class .*Controller\" src/ | head -5\n"
            "\n"
            "# 3. Identify build/test/lint commands\n"
            "cat package.json | grep -A5 '\"scripts\"' 2>/dev/null\n"
            "cat *.csproj Directory.Build.props 2>/dev/null | head -30\n"
            "\n"
            "# 4. Check for existing shared utilities before writing new ones\n"
            "grep -rl \"class .*Validator\" src/ | head -5\n"
            "\n"
            "# 5. Confirm framework / language version constraints\n"
            "cat global.json .nvmrc go.mod 2>/dev/null\n"
            "\n"
            "# 6. Look for architectural decision records that explain 'why'\n"
            "find . -iname 'ADR-*' -o -iname '*decision*record*' 2>/dev/null | head -10\n"
        ),
        code2_heading="Example exploration summary before starting work",
        code2=("text",
            "Capture findings briefly so the plan step in agent-build-workflow can reference them:",
            "Context summary: Adding rate limiting to /reset-password\n"
            "  - Analogous example: LoginController already uses IRateLimiter (src/RateLimiting/).\n"
            "  - Build/test: dotnet build, dotnet test --filter Auth (see README 'Testing' section).\n"
            "  - Convention: middleware registered in Program.cs, one line per policy.\n"
            "  - Existing utility: IRateLimiter.TryAcquire(key, window) — reuse, do not reimplement.\n"
            "  - Version constraint: net8.0 per global.json; no external packages needed.\n"
        ),
        checklist=[
            "An existing analogous example was found and studied, or its absence was noted explicitly.",
            "The project's build, lint, and test commands were identified before making changes.",
            "Naming and layering conventions actually observed in the code were followed.",
            "Existing utilities were reused instead of duplicated where applicable.",
            "Exploration was scoped to what is needed for this task, not the entire repository.",
            "Version/dependency constraints were checked before introducing new code.",
            "Any conflict between documentation and actual code behavior was flagged explicitly.",
        ],
        antipatterns=[
            ("Cargo-culting from memory", "Applying conventions from a different, unrelated codebase instead of what this repository actually uses."),
            ("Analysis paralysis", "Spending excessive time reading unrelated modules instead of the smallest set needed to proceed confidently."),
            ("Ignoring existing utilities", "Writing a new validation/mapping/logging helper when an equivalent already exists in the codebase."),
            ("Skipping the build/test discovery step", "Guessing at how to verify a change instead of using the project's actual tooling."),
            ("Trusting stale docs over code", "Following outdated documentation that contradicts what the current code and tests actually do."),
        ],
        verification=[
            "You can name the specific file(s) used as the analogous example, if one exists.",
            "You can state the exact command used to build/test/lint the project.",
            "The resulting change matches the codebase's existing naming and structural conventions.",
            "Any discrepancy found between docs and code was flagged, not silently ignored.",
        ],
        references=[
            "skills/00-core/agent-build-workflow/SKILL.md",
            "skills/70-quality/refactoring-and-legacy-code/SKILL.md",
        ],
    ),
    dict(
        dir="00-core", slug="skill-authoring", category="core",
        tags=["meta", "documentation", "skills-catalog"],
        desc="Use when writing or updating a SKILL.md file in this catalog and you need to follow the required structure, frontmatter, and validation rules.",
        purpose=[
            "This is the meta-skill for maintaining the Code-Skills catalog itself: it captures the "
            "structural rules that scripts/validate_skills.py enforces so that every skill is consistent, "
            "discoverable, and machine-checkable.",
            "Following it consistently keeps the catalog usable both by human engineers browsing docs/INDEX.md "
            "and by coding agents parsing frontmatter to select the right skill automatically.",
        ],
        when_use=[
            "You are creating a brand-new skill folder under skills/<category>/<name>/.",
            "You are updating an existing SKILL.md and need to preserve its required structure.",
            "You are reviewing a skill-authoring pull request.",
            "You are deciding whether a new topic deserves its own skill or belongs inside an existing one.",
        ],
        when_not=[
            "You are writing general project documentation unrelated to the skills catalog — use docs/ conventions instead.",
        ],
        prereqs=[
            "docs/skill-authoring-guide.md read at least once.",
            "templates/SKILL.template.md as the starting point (via scripts/new_skill.py).",
            "PyYAML installed locally if you intend to run scripts/validate_skills.py directly.",
        ],
        workflow=[
            ("Scaffold from the template", "Run `python scripts/new_skill.py --category <dir> --name <slug>` to generate correct frontmatter and section order."),
            ("Write a single-sentence description", "Start it with the literal words 'Use when' and keep it under 400 characters."),
            ("Choose precise tags", "Pick 2-4 lowercase tags that would help someone searching docs/INDEX.md find this skill."),
            ("Fill all ten sections in order", "Purpose, When to use/NOT, Prerequisites, Workflow, Decision guide, Reference implementation, Checklist, Anti-patterns, Verification, References."),
            ("Add a real code or diagram example", "Use the correct language for the domain, and add a Mermaid diagram for architecture skills."),
            ("Keep length in range", "Target 150-400 lines total; the validator hard-fails above 500."),
            ("Validate and index", "Run `python scripts/validate_skills.py` and `python scripts/generate_index.py`, fixing any reported issues."),
        ],
        decision=[
            ("Unsure which category a skill belongs to", "Pick the category matching where in the SDLC an engineer would reach for it first; cross-link from others."),
            ("Skill overlaps heavily with an existing one", "Extend the existing skill instead of creating a near-duplicate."),
            ("Skill needs a diagram", "Use a fenced ```mermaid block inside Reference implementation (or Workflow) rather than an external image."),
            ("Content does not fit in 400 lines", "Split into two more focused skills rather than exceeding the limit."),
            ("Skill is still being drafted/reviewed", "Set maturity: draft and only flip to stable after a peer review pass."),
        ],
        code_lang="bash",
        code_intro="The standard commands for authoring and validating a skill:",
        code=(
            "# Scaffold a new skill\n"
            "python scripts/new_skill.py --category 30-backend --name outbox-pattern\n"
            "\n"
            "# ... fill in skills/30-backend/outbox-pattern/SKILL.md ...\n"
            "\n"
            "# Validate structure, frontmatter, and links\n"
            "python scripts/validate_skills.py\n"
            "\n"
            "# Regenerate the catalog index\n"
            "python scripts/generate_index.py\n"
            "\n"
            "# Confirm the index is not stale (used in CI)\n"
            "python scripts/generate_index.py --check\n"
            "\n"
            "# Optional: lint markdown locally before opening a PR\n"
            "npx --yes markdownlint-cli '**/*.md' --ignore node_modules\n"
        ),
        code2_heading="Example of a correctly filled frontmatter block",
        code2=("yaml",
            "A concrete, valid frontmatter block for a hypothetical new skill:",
            "---\n"
            "name: outbox-pattern\n"
            "description: Use when you need to publish domain events reliably alongside a database transaction.\n"
            "category: backend\n"
            "tags: [messaging, reliability, transactions]\n"
            "maturity: draft\n"
            "updated: 2026-08-21\n"
            "---\n"
        ),
        checklist=[
            "Frontmatter has exactly the required keys: name, description, category, tags, maturity, updated.",
            "description starts with 'Use when' and is under 400 characters.",
            "name matches the folder name exactly and is kebab-case.",
            "All ten required H2 sections are present, in order, with no placeholder text.",
            "File length is between 150 and 400 lines (never over 500).",
            "python scripts/validate_skills.py passes with zero issues.",
            "docs/INDEX.md was regenerated and committed alongside the new/changed skill.",
        ],
        antipatterns=[
            ("Renaming section headings", "Using synonyms like 'Overview' instead of 'Purpose' breaks the validator's ordered-section check."),
            ("Leaving template placeholders", "Shipping text like '<situation 1>' verbatim instead of real content."),
            ("Overstuffed tags", "Adding a dozen loosely related tags instead of 2-4 precise ones that aid search."),
            ("Skipping validation before PR", "Opening a PR without having run validate_skills.py and generate_index.py locally first."),
            ("Duplicate skills", "Creating a near-copy of an existing skill instead of extending it, fragmenting the catalog."),
        ],
        verification=[
            "`python scripts/validate_skills.py` exits 0 for the new/changed file.",
            "`python scripts/generate_index.py --check` reports the index as up to date after regeneration.",
            "A peer reviewer confirms the description accurately triggers on the intended situation.",
        ],
        references=[
            "docs/skill-authoring-guide.md",
            "templates/SKILL.template.md",
            "scripts/validate_skills.py",
            "docs/agent-integration.md",
        ],
    ),
]
