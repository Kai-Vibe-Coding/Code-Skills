SKILLS = [
    dict(
        dir="70-quality", slug="code-review", category="quality",
        tags=["code-review", "pull-requests", "feedback"],
        desc="Use when reviewing a pull request or preparing your own change for review to ensure feedback is focused on real risks and communicated constructively.",
        purpose=[
            "Code review is one of the highest-leverage quality practices available, but it fails when "
            "reviewers nitpick style over substance, or when authors submit unreviewable giant PRs. This "
            "skill establishes what a reviewer should focus on (correctness, security, maintainability) "
            "versus what tooling should catch (formatting, style), and how to give feedback that improves "
            "the code without demoralizing the author.",
            "It also covers the author's responsibility: keeping changes small, providing context, and "
            "responding to feedback professionally, since a good review is a two-way collaboration.",
        ],
        when_use=[
            "You are reviewing a pull request from a teammate.",
            "You are preparing your own pull request and want it to be easy and fast to review.",
            "A review process feels slow, contentious, or is producing low-quality feedback.",
        ],
        when_not=[
            "You need guidance on running an automated code-quality/security tool — that's a complementary but distinct practice from human review.",
            "The change is trivial (a typo fix) where a lightweight or skipped review may be reasonable per team policy.",
        ],
        prereqs=[
            "skills/90-delivery/git-workflow-and-conventional-commits/SKILL.md for how changes should be structured and described.",
            "Automated formatting/linting already enforced in CI so reviewers don't need to manually flag style issues.",
        ],
        workflow=[
            ("Keep changes small and focused", "As an author, submit one logical change per PR; large multi-concern PRs are inherently harder to review well."),
            ("Provide context in the PR description", "Explain what changed and why, link the related issue/spec, and call out anything the reviewer should pay special attention to."),
            ("Let automated tooling catch style and formatting", "Reviewers should not spend review time on things a linter/formatter already enforces in CI."),
            ("Focus review on correctness, security, and maintainability", "Does the logic actually do what's intended? Are there security or data-integrity risks? Will this be understandable in six months?"),
            ("Distinguish blocking issues from suggestions", "Clearly mark must-fix issues versus optional nitpicks/preferences, so the author knows what's required to merge."),
            ("Ask questions instead of asserting when unsure", "'Why was this approach chosen over X?' invites explanation rather than assuming a mistake."),
            ("Respond to feedback promptly and professionally on both sides", "Authors address or discuss every comment; reviewers re-review promptly rather than leaving a PR blocked indefinitely."),
            ("Approve when the change is good enough, not perfect", "Avoid holding a PR hostage to endless polish; file a follow-up ticket for genuinely non-blocking improvement ideas."),
        ],
        decision=[
            ("A PR touches many unrelated files/concerns", "Ask the author to split it into smaller, independently reviewable PRs before doing a deep review."),
            ("A comment is about a formatting/style preference already enforced by the linter", "Skip it — trust the automated tooling and focus review time elsewhere."),
            ("A comment is a genuine correctness or security concern", "Mark it clearly as blocking and require it to be addressed before merge."),
            ("A comment is a nice-to-have improvement with no real risk if deferred", "Mark it as non-blocking/optional, or file a follow-up ticket instead of blocking the merge."),
            ("You disagree with an author's approach but it's not objectively wrong", "Raise it as a question/discussion point, not a demand, and be willing to defer to the author's judgment on subjective choices."),
        ],
        code_lang="markdown",
        code_intro="A well-structured PR description that makes review faster and more focused:",
        code=(
            "## What changed\n"
            "Adds optimistic concurrency to the Order aggregate to prevent lost updates when two\n"
            "users edit the same order simultaneously (see issue #482).\n"
            "\n"
            "## Why\n"
            "Support reported customers occasionally seeing their shipping address changes silently\n"
            "reverted. Root cause: concurrent PUT requests with no conflict detection.\n"
            "\n"
            "## How to review\n"
            "- Focus on `OrderRepository.UpdateAsync` — this is the core fix.\n"
            "- `OrderRepositoryTests.cs` has a new concurrent-update test reproducing the original bug.\n"
            "- Formatting/style changes are auto-generated by `dotnet format`, safe to skim.\n"
            "\n"
            "## Risk\n"
            "Low — additive change (a new RowVersion column), backward compatible with existing rows.\n"
        ),
        code_notes=[
            "Explicitly pointing reviewers at the core logic and away from mechanical formatting changes saves real review time.",
            "Stating the risk level upfront helps the reviewer calibrate how much scrutiny the change actually needs.",
        ],
        code2_heading="Distinguishing blocking from non-blocking review comments (Markdown, PR comment style)",
        code2=("markdown",
            "Making it unambiguous what must change before merge versus what's optional:",
            "**[blocking]** This query doesn't filter by `tenantId`, which would leak cross-tenant data.\n"
            "Please add the tenant filter before merging.\n"
            "\n"
            "**[nit, non-blocking]** Consider renaming `tmp` to `pendingOrder` for clarity — up to you,\n"
            "not required for this PR.\n"
        ),
        checklist=[
            "PRs are kept small and focused on one logical change.",
            "PR descriptions provide context: what changed, why, and where reviewers should focus attention.",
            "Reviewers focus on correctness, security, and maintainability, not style already enforced by tooling.",
            "Comments are clearly marked as blocking versus optional/non-blocking.",
            "Feedback is phrased as questions or specific concerns, not personal criticism.",
            "Both author and reviewer respond promptly, avoiding PRs sitting blocked for extended periods.",
        ],
        antipatterns=[
            ("Giant unreviewable PRs", "Submitting a 2000-line PR touching five unrelated concerns, making a thorough review practically impossible."),
            ("Style nitpicking over substance", "Spending review time debating brace placement instead of checking for correctness or security issues, when a linter already enforces style."),
            ("Vague or absent PR descriptions", "Submitting a PR titled 'fixes' with no description, forcing the reviewer to reverse-engineer intent from the diff alone."),
            ("Ambiguous blocking status", "Leaving comments with no indication of whether they must be addressed before merge, causing confusion and delay."),
            ("Personal or harsh feedback", "Phrasing a comment as 'this is wrong' or targeting the author rather than focusing constructively on the code."),
        ],
        verification=[
            "A sample of recent PRs shows an average size small enough to be reviewed thoroughly in one sitting.",
            "PR descriptions consistently include what/why/how-to-review context, verified by a sample review.",
            "Review comments are consistently marked blocking vs non-blocking, and merges only proceed once blocking comments are resolved.",
            "Time-to-first-review and time-to-merge metrics show reviews aren't a chronic bottleneck.",
        ],
        references=[
            "skills/90-delivery/git-workflow-and-conventional-commits/SKILL.md",
            "Google Engineering Practices — Code Review Developer Guide.",
            ".github/PULL_REQUEST_TEMPLATE.md",
        ],
    ),
    dict(
        dir="70-quality", slug="refactoring-and-legacy-code", category="quality",
        tags=["refactoring", "legacy-code", "technical-debt"],
        desc="Use when you need to safely change behavior or improve the structure of code that has little or no existing test coverage.",
        purpose=[
            "Legacy code — code without adequate tests, not necessarily old code — is risky to change because "
            "there's no safety net to confirm a refactor didn't alter behavior. This skill covers safely "
            "characterizing existing behavior with tests before refactoring, making small reversible steps, "
            "and using established refactoring patterns rather than rewriting from scratch.",
            "It treats 'add tests, then refactor' as the default approach to legacy code, reserving a full "
            "rewrite for the rare cases where the existing code is genuinely beyond safe incremental repair.",
        ],
        when_use=[
            "You need to change or extend a piece of code with little or no existing test coverage.",
            "A codebase area is described as 'nobody wants to touch it' due to fear of breaking something.",
            "You are deciding between refactoring incrementally versus rewriting a component from scratch.",
        ],
        when_not=[
            "The code already has solid test coverage — see skills/70-quality/test-strategy/SKILL.md's normal workflow instead, no special legacy-code caution needed.",
            "The change is a trivial, well-isolated addition with no risk to existing behavior.",
        ],
        prereqs=[
            "skills/70-quality/unit-testing-dotnet/SKILL.md and skills/70-quality/integration-testing/SKILL.md for the testing techniques used to add a safety net.",
            "Version control with the ability to make small, incremental, revertible commits.",
        ],
        workflow=[
            ("Write characterization tests before changing anything", "Capture the code's current actual behavior (bugs and all) in tests, giving a safety net for the refactor."),
            ("Identify seams to break dependencies for testability", "Find a point where a dependency can be substituted (extract an interface, inject a parameter) without a large rewrite."),
            ("Make the smallest possible refactoring steps", "Extract a method, rename a variable, or introduce a parameter object one step at a time, running tests after each."),
            ("Never refactor and change behavior in the same commit", "Separate 'restructure without changing behavior' commits from 'add new behavior' commits, so each is independently reviewable and revertible."),
            ("Apply established refactoring patterns by name", "Extract Method, Extract Class, Replace Conditional with Polymorphism — recognized patterns are safer and more communicable than ad hoc restructuring."),
            ("Improve test coverage incrementally as you touch code", "Add tests for the specific area being modified rather than attempting a big-bang full-codebase test-writing effort."),
            ("Reserve a rewrite for genuinely irreparable code", "Only consider a full rewrite when incremental refactoring is demonstrably infeasible, and even then scope it as narrowly as possible."),
            ("Track and pay down technical debt deliberately", "Log significant known debt as a ticket with context, rather than leaving it as an unspoken, undocumented risk."),
        ],
        decision=[
            ("Code has zero tests and needs a bug fix", "Write characterization tests capturing current behavior first, then fix the bug with tests as a safety net."),
            ("A class has a hard dependency preventing any testing (e.g. static call, `new` in constructor)", "Introduce a seam (extract interface, inject dependency) as the very first small step before attempting further refactoring."),
            ("A large method mixes several responsibilities", "Apply Extract Method repeatedly to separate them, verifying behavior is unchanged after each small step."),
            ("The team is tempted to 'just rewrite it'", "Default to incremental refactoring first; a rewrite carries high risk of losing undocumented business rules embedded in the old code."),
            ("A refactor and a behavior change both seem needed at once", "Split them into separate commits/PRs — refactor first (behavior-preserving), then change behavior as a distinct, reviewable step."),
        ],
        code_lang="csharp",
        code_intro="Introducing a seam to make a previously untestable class testable:",
        code=(
            "// Before: hard dependency on a static call, impossible to unit test\n"
            "public class InvoiceService\n"
            "{\n"
            "    public decimal CalculateTotal(Invoice invoice)\n"
            "    {\n"
            "        var taxRate = TaxRateProvider.GetCurrentRate(); // static call, untestable\n"
            "        return invoice.Subtotal * (1 + taxRate);\n"
            "    }\n"
            "}\n"
            "\n"
            "// After: seam introduced via constructor injection, now testable in isolation\n"
            "public class InvoiceService\n"
            "{\n"
            "    private readonly ITaxRateProvider _taxRateProvider;\n"
            "    public InvoiceService(ITaxRateProvider taxRateProvider) => _taxRateProvider = taxRateProvider;\n"
            "\n"
            "    public decimal CalculateTotal(Invoice invoice)\n"
            "    {\n"
            "        var taxRate = _taxRateProvider.GetCurrentRate();\n"
            "        return invoice.Subtotal * (1 + taxRate);\n"
            "    }\n"
            "}\n"
        ),
        code_notes=[
            "This single small change (extract an interface, inject it) is the entire first commit — no other behavior changes bundled in.",
            "Once this seam exists, a unit test can substitute a fake ITaxRateProvider and safely verify CalculateTotal's logic.",
        ],
        code2_heading="A characterization test capturing existing behavior before refactoring (C#)",
        code2=("csharp",
            "Written to match what the code actually does today, bugs included, as a safety net for the refactor:",
            "[Fact]\n"
            "public void CalculateTotal_MatchesCurrentObservedBehavior()\n"
            "{\n"
            "    var provider = Substitute.For<ITaxRateProvider>();\n"
            "    provider.GetCurrentRate().Returns(0.08m);\n"
            "    var service = new InvoiceService(provider);\n"
            "\n"
            "    var result = service.CalculateTotal(new Invoice { Subtotal = 100m });\n"
            "\n"
            "    Assert.Equal(108m, result); // captures current behavior before any refactor\n"
            "}\n"
        ),
        checklist=[
            "Characterization tests exist for the current behavior before any refactoring begins.",
            "Refactoring commits are kept separate from behavior-changing commits.",
            "Each refactoring step is small enough to verify immediately with a test run.",
            "Seams (interfaces, injected dependencies) are introduced deliberately to make previously untestable code testable.",
            "A full rewrite is only chosen after incremental refactoring is demonstrated to be infeasible.",
            "Known technical debt is tracked in a ticket with context, not left as silent, undocumented risk.",
        ],
        antipatterns=[
            ("Refactoring with no tests as a safety net", "Restructuring code with zero characterization tests first, with no way to confirm behavior wasn't accidentally changed."),
            ("Refactor and feature change bundled together", "Mixing a restructuring with new functionality in one commit, making it impossible to isolate which change caused a regression."),
            ("Big-bang rewrite as a default", "Reaching for a full rewrite as the first response to messy legacy code, discarding undocumented business logic embedded in it."),
            ("Giant refactoring steps", "Attempting to restructure an entire large class in one uninterrupted pass instead of small, independently verifiable steps."),
            ("Silent technical debt", "Leaving known-bad code unaddressed and undocumented, with no ticket or note explaining the risk for future engineers."),
        ],
        verification=[
            "Characterization tests pass both before and immediately after each refactoring step, confirming behavior is unchanged.",
            "Git history shows refactoring commits are separate from behavior-changing commits.",
            "A previously untestable class now has passing unit tests after a seam was introduced.",
            "Any deferred technical debt has a corresponding tracked ticket with enough context to act on later.",
        ],
        references=[
            "skills/70-quality/unit-testing-dotnet/SKILL.md",
            "Michael Feathers — Working Effectively with Legacy Code.",
            "Martin Fowler — Refactoring: Improving the Design of Existing Code.",
        ],
    ),
]
