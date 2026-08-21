---
name: engineering-principles
description: Use when starting any engineering task and you need a shared baseline of quality, simplicity, and safety principles to apply before writing code.
category: core
tags: [principles, fundamentals, agent-behavior]
maturity: stable
updated: 2026-08-21
---

## Purpose

This skill establishes the baseline engineering principles that every other skill in this catalog assumes: favor simplicity, make small reversible changes, write for the next reader, and verify before declaring done.

It exists so that agents and humans do not have to relearn these fundamentals in every task-specific skill, and so that reviewers have a shared vocabulary for pushing back on over-engineered or under-verified changes.

## When to use / When NOT to use

**Use this skill when:**

- You are beginning any coding, design, or review task and want a shared quality bar.
- You are unsure whether a proposed change is 'simple enough' or 'safe enough' to ship.
- You are onboarding a new contributor (human or agent) to how this team works.
- You are reviewing a pull request and need objective criteria beyond personal taste.
- You are deciding between two designs that both technically satisfy the requirements.
- You are tempted to add an abstraction and want to sanity-check whether it is justified.

**Do NOT use this skill when:**

- You need a concrete step-by-step procedure for a specific technology — use the relevant specialized skill instead.
- You are deep in an unrelated domain-specific decision (e.g. choosing an index type) — see the matching skill.
- The team already has a documented, conflicting standard for this specific case — defer to that.
- You are evaluating a purely cosmetic style choice already covered by a linter/formatter config.

## Prerequisites

- None — this is the entry point for the whole catalog.
- Familiarity with the specific language/framework of the task at hand helps but is not required to apply these principles.
- Access to the project's existing tests, linters, and build tooling for the verification step.

## Workflow

1. **Prefer the simplest solution that works** - Before adding an abstraction, ask whether the problem actually requires it today, not hypothetically.
2. **Make changes small and reversible** - Split work into commits/PRs that can be reviewed and rolled back independently.
3. **Write for the next reader** - Optimize for readability over cleverness; a change that saves 2 minutes of typing but costs 20 minutes of comprehension is a net loss.
4. **State assumptions explicitly** - When requirements are ambiguous, write down the assumption you are proceeding with instead of silently guessing.
5. **Match existing conventions first** - Follow the codebase's existing patterns before introducing a personally preferred style.
6. **Verify before declaring done** - Run the tests, linters, or manual checks that prove the change works, not just that it compiles.
7. **Leave the codebase better than you found it** - Fix small, directly related issues you encounter, but do not scope-creep into unrelated refactors.
8. **Communicate trade-offs** - When a shortcut was taken deliberately, say so and explain the trade-off instead of hiding it.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Two designs solve the problem equally well | Choose the one with fewer moving parts and less new vocabulary for the team to learn. |
| Requirements are ambiguous and no one is available to ask | Make the most conservative, reversible assumption and document it prominently. |
| A quick hack would unblock you today | Only take it if it is clearly labeled, tracked, and does not compromise correctness or security. |
| You find an unrelated bug while working | Log it separately; fix it inline only if it is a one-line, low-risk change directly in your path. |
| A new abstraction would remove duplication | Only introduce it once the same logic is needed in three or more places (rule of three). |
| Team convention conflicts with a 'best practice' you know | Follow the team convention and raise the discrepancy separately rather than deviating silently. |
| Deadline pressure tempts skipping verification | Reduce scope instead of skipping verification; an unverified change is not actually finished. |

## Reference implementation

A short principles checklist to paste at the top of a design doc or PR description:

```text
Engineering Principles Checklist
---------------------------------
[ ] Simplicity: could this be solved with less code / fewer moving parts?
[ ] Reversibility: can this change be rolled back safely and quickly?
[ ] Readability: would a new teammate understand this in under 5 minutes?
[ ] Assumptions: are ambiguous requirements documented explicitly?
[ ] Convention: does this match how the rest of the codebase already does it?
[ ] Verification: is there a concrete way to prove this works (test, log, metric)?
[ ] Scope: does this change avoid unrelated, uncoordinated refactors?
[ ] Trade-offs: are any deliberate shortcuts called out explicitly, not hidden?

Example PR description applying the checklist:

  Title: Add retry to payment webhook delivery
  - Simplicity: reused existing Polly retry policy, no new library added.
  - Reversibility: change is feature-flagged behind Payments.WebhookRetry.
  - Assumption: treating HTTP 5xx and timeouts as retryable, 4xx as terminal.
  - Verified: added unit test WebhookSenderTests.RetriesOn5xx, ran dotnet test.
  - Trade-off: fixed 3 retries with exponential backoff chosen over a queue-based
    approach for this iteration; revisit if webhook volume grows 10x.
```

- Use this checklist format verbatim in PR descriptions to make principle application visible to reviewers.
- Keep each checklist line answerable in one sentence; if it needs a paragraph, the change may be too large.

### Recognizing an over-engineered alternative

Contrast the same task solved with unnecessary generality, to make the anti-pattern concrete:

```text
Over-engineered version (avoid):
  - Introduces IWebhookDeliveryStrategy with 3 implementations for 1 real use case.
  - Adds a generic RetryPolicyFactory configurable via 12 new settings.
  - Ships with no test proving the one real retry path actually works.
  - PR description: "Refactored webhook delivery to be more extensible."

Why this fails the checklist:
  - Simplicity: 3x the code for 1 real requirement.
  - Verification: no test asserts the behavior that was actually requested.
  - Scope: 'more extensible' is not a stated requirement — it is speculative.
```

## Checklist

- [ ] The simplest viable design was chosen and the reasoning is recorded.
- [ ] The change can be reverted independently of unrelated work.
- [ ] Any assumption made about ambiguous requirements is written down.
- [ ] The change follows existing codebase conventions rather than introducing a new personal style.
- [ ] A verification step (test, build, manual check) was actually run, not just planned.
- [ ] The change stays within the requested scope, with unrelated fixes called out separately.
- [ ] Deliberate trade-offs or shortcuts are explicitly documented, not hidden.
- [ ] No abstraction was added solely for hypothetical future requirements.
- [ ] A teammate unfamiliar with the change could review it without needing a walkthrough.

## Anti-patterns

- **Speculative generality** - Building configuration, plugin systems, or abstractions for requirements that do not exist yet. Build for today's requirements and refactor when the second real use case appears.
- **Silent assumptions** - Proceeding on an ambiguous requirement without stating the assumption anywhere. Always surface it in the PR description or a comment.
- **Big-bang changes** - Bundling unrelated refactors, dependency upgrades, and features into one giant diff that is impossible to review or revert safely.
- **Declaring done without verification** - Assuming code works because it compiles or 'looks right'. Always run the smallest test that would catch a regression.
- **Style crusades** - Rewriting unrelated code to match a personally preferred style instead of the team's existing convention.
- **Hidden shortcuts** - Taking a deliberate shortcut (e.g. skipping an edge case) without telling anyone, creating a silent landmine for later.

## Verification

- The PR description states what was verified and how (command run, output observed).
- A reviewer can identify the single main change and any explicitly called-out side fixes.
- No TODO, placeholder, or 'figure this out later' text remains in the shipped change.
- Any deliberate trade-off is documented in the PR description or a code comment.
- The diff does not touch files unrelated to the stated task.

## References

- Kent Beck, 'Tidy First?' — on small, reversible, separately-reviewable changes.
- Robert C. Martin, 'Clean Code' — on writing for the next reader.
- skills/00-core/context-gathering/SKILL.md — how to gather the context needed before applying these principles.
- skills/70-quality/code-review/SKILL.md — how these principles are checked in review.
- skills/90-delivery/shipping-checklist/SKILL.md — final gate before release.
