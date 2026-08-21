SKILLS = [
    dict(
        dir="70-quality", slug="debugging-methodology", category="quality",
        tags=["debugging", "root-cause-analysis", "troubleshooting"],
        desc="Use when investigating a bug or unexpected behavior and you need a systematic approach rather than guessing at fixes.",
        purpose=[
            "Undisciplined debugging — changing code speculatively and re-running to see if it 'fixes' the "
            "symptom — wastes time and often masks the real problem instead of resolving it. This skill "
            "establishes a systematic debugging method: reproduce reliably, form a hypothesis, gather "
            "evidence, and narrow down the cause via bisection, before making any change.",
            "It applies equally to a local development bug and a production incident, though production "
            "debugging must also respect skills/60-devops/incident-response-and-runbooks/SKILL.md's mitigate-first "
            "priority when user impact is ongoing.",
        ],
        when_use=[
            "You've encountered a bug or unexpected behavior and need to find its root cause.",
            "A bug is intermittent or hard to reproduce and needs a systematic approach rather than guesswork.",
            "You want to verify a fix actually addresses the root cause, not just the visible symptom.",
        ],
        when_not=[
            "The system is actively causing significant user-facing production impact — mitigate first per skills/60-devops/incident-response-and-runbooks/SKILL.md, then debug the root cause.",
            "The cause is already obvious and confirmed (e.g. a clear typo) — apply the fix directly without a lengthy investigation process.",
        ],
        prereqs=[
            "skills/60-devops/observability/SKILL.md for the logs/traces/metrics debugging often depends on.",
            "Access to a debugger and the ability to reproduce the issue in a controlled environment.",
        ],
        workflow=[
            ("Reproduce the issue reliably first", "A bug you can't reliably reproduce can't be reliably confirmed as fixed; invest in finding reliable reproduction steps before anything else."),
            ("Gather all available evidence before theorizing", "Read the actual error message/stack trace fully, check logs/traces, and note exactly what's expected versus observed."),
            ("Form a specific, falsifiable hypothesis", "'I think X causes this because Y' — not a vague 'maybe it's the database' with nothing to test."),
            ("Test the hypothesis with the smallest possible experiment", "Add a targeted log statement, a breakpoint, or a minimal reproduction case to confirm or refute the hypothesis directly."),
            ("Use bisection to narrow down the cause", "Binary search across commits (git bisect), code paths, or input ranges to isolate exactly where behavior diverges from expected."),
            ("Read the code, don't just guess from behavior", "Actually trace through the relevant code path rather than pattern-matching against a similar bug seen before."),
            ("Fix the root cause, not just the symptom", "Confirm the fix addresses why the bug happened, not just makes the specific reproduction case stop failing."),
            ("Add a regression test before considering the bug closed", "A test reproducing the original bug ensures it can't silently reappear later."),
        ],
        decision=[
            ("A bug is intermittent and hard to reproduce", "Invest first in finding a reliable reproduction (specific input, timing, environment) before attempting any fix."),
            ("A bug appeared recently in a codebase with git history", "Use git bisect to find the exact commit that introduced the regression, rather than reading the whole codebase."),
            ("Multiple hypotheses seem equally plausible", "Test the cheapest-to-verify hypothesis first, narrowing the search space quickly rather than deep-diving the first idea."),
            ("The 'fix' makes the specific test case pass but you're unsure why", "Stop and confirm you understand the actual root cause before considering it resolved — an unexplained fix often isn't a real fix."),
            ("The bug is causing active production user impact right now", "Follow skills/60-devops/incident-response-and-runbooks/SKILL.md to mitigate first; do full root-cause debugging in parallel or after."),
        ],
        code_lang="bash",
        code_intro="Using git bisect to systematically find the commit that introduced a regression:",
        code=(
            "git bisect start\n"
            "git bisect bad HEAD                 # current commit exhibits the bug\n"
            "git bisect good v1.4.0               # this known-good tagged release did not\n"
            "\n"
            "# Git checks out a midpoint commit; run the reproduction steps, then mark it:\n"
            "git bisect good   # or: git bisect bad\n"
            "\n"
            "# Repeat until git identifies the exact first bad commit:\n"
            "# \"abc1234 is the first bad commit\"\n"
            "git bisect reset\n"
            "\n"
            "# Automate the whole process with a script that exits 0 (good) or 1 (bad):\n"
            "git bisect run ./scripts/reproduce-bug.sh\n"
        ),
        code_notes=[
            "git bisect run automates the good/bad marking entirely if the reproduction can be scripted, turning a manual hunt into an unattended search.",
            "This finds the exact introducing commit in O(log n) steps rather than reading through the entire commit history linearly.",
        ],
        code2_heading="A minimal, targeted reproduction case isolating the hypothesis (C#)",
        code2=("csharp",
            "Stripping away everything unrelated to confirm a specific suspected cause:",
            "[Fact]\n"
            "public void Repro_DiscountCalculator_ReturnsNegativeForQuantityZero()\n"
            "{\n"
            "    // Hypothesis: division by zero occurs when quantity is 0 in the tiered discount branch.\n"
            "    var result = DiscountCalculator.PercentFor(quantity: 0);\n"
            "    Assert.True(result >= 0, \"Expected non-negative discount, hypothesis confirmed if this fails\");\n"
            "}\n"
        ),
        checklist=[
            "The bug has a reliable, documented reproduction before any fix is attempted.",
            "A specific, falsifiable hypothesis is formed and tested before changing code speculatively.",
            "Bisection (commit history, input range, or code path) is used to systematically narrow down the cause.",
            "The actual code path is read and traced, not just guessed from surface-level behavior.",
            "The applied fix addresses the confirmed root cause, not just the originally observed symptom.",
            "A regression test capturing the original bug is added before considering it closed.",
        ],
        antipatterns=[
            ("Speculative fix-and-pray", "Changing code based on a guess and re-running to see if the symptom disappears, without understanding why it would help."),
            ("Debugging without reliable reproduction", "Attempting to fix an intermittent bug without first establishing steps to reproduce it consistently, making any 'fix' unverifiable."),
            ("Symptom-only fixes", "Patching over a null-reference exception with a null check without investigating why the value was unexpectedly null in the first place."),
            ("Skipping evidence gathering", "Jumping straight to a hypothesis without reading the actual full error message, stack trace, or relevant logs first."),
            ("No regression test after fixing", "Closing a bug ticket without adding a test that would catch the exact issue if it were reintroduced later."),
        ],
        verification=[
            "The bug can be reliably reproduced on demand before and cannot be reproduced after the fix.",
            "A clear, articulated explanation exists for why the identified root cause produced the observed symptom.",
            "A regression test exists that would fail against the pre-fix code and passes against the post-fix code.",
            "git bisect (or equivalent) log/history confirms the exact introducing change when the bug was a regression.",
        ],
        references=[
            "skills/60-devops/incident-response-and-runbooks/SKILL.md",
            "skills/60-devops/observability/SKILL.md",
            "skills/70-quality/unit-testing-dotnet/SKILL.md",
        ],
    ),
]
