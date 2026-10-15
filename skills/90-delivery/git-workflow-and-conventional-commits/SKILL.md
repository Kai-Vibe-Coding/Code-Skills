---
name: git-workflow-and-conventional-commits
description: Use when structuring git branches, commits, and pull requests so history stays readable and changelogs/versioning can be automated from commit messages.
category: delivery
tags: [git, conventional-commits, branching]
maturity: stable
updated: 2026-08-21
---

## Purpose

An inconsistent commit history makes it hard to understand why a change was made, generate changelogs, or automate semantic version bumps. This skill covers a trunk-based branching workflow paired with the Conventional Commits specification, so commit messages carry structured, machine-parseable meaning.

## When to use / When NOT to use

**Use this skill when:**

- You are starting a new repository and need to establish a branching and commit convention.
- You want to automate changelog generation or semantic versioning from commit history.
- A team's commit history is inconsistent and hard to scan or search.

**Do NOT use this skill when:**

- The project has an established, working convention already (e.g. a different but consistent commit style) and switching would cause more churn than value.
- You need broader release process guidance — see skills/60-devops/release-strategies/SKILL.md.

## Prerequisites

- skills/90-delivery/shipping-checklist/SKILL.md for how commits/PRs feed into the release process.
- Team agreement on the branching model (trunk-based vs. Git Flow) before enforcing commit conventions.

## Workflow

1. **Adopt a trunk-based branching model** - Use short-lived feature branches off `main`, merged frequently, avoiding long-lived divergent branches that accumulate conflict risk.
2. **Use Conventional Commits format for every commit** - Structure messages as `type(scope): subject`, e.g. `feat(orders): add discount code support`, using standard types (feat, fix, docs, refactor, test, chore).
3. **Keep commits atomic and focused** - Each commit represents one logical change; avoid bundling unrelated changes into a single commit.
4. **Write descriptive PR titles and descriptions** - A PR title following the same conventional format, with a description explaining what changed and why, not just what.
5. **Squash or rebase merge to keep main history clean** - Choose one merge strategy consistently (squash-merge is common) so `main`'s history remains one entry per logical PR.
6. **Reference related issues/tickets in commits or PRs** - Link commits to their originating requirement or bug ticket for traceability, per skills/00-core/requirements-to-code-traceability/SKILL.md.
7. **Automate changelog and version bumps from commit types** - Use a tool like semantic-release or conventional-changelog to derive the next version and changelog entries from commit history.
8. **Protect the main branch with required reviews and checks** - Require passing CI and at least one review before merge, preventing unreviewed changes from landing on the trunk.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Committing a change that fixes a bug | Use `fix:` as the commit type so automated tooling classifies it correctly for changelog and patch-version bumps. |
| Committing a change that adds a new capability | Use `feat:` so automated tooling can compute a minor version bump. |
| A commit contains a breaking API change | Add a `BREAKING CHANGE:` footer or a `!` after the type/scope (e.g. `feat(api)!:`) so automated tooling computes a major version bump. |
| A change only affects tests or CI configuration, no production code | Use `test:` or `ci:` as the type so it's excluded from user-facing changelog sections by default. |
| Choosing between merge commit, squash, or rebase for a PR | Prefer squash-merge for most teams to keep `main` history as one clean commit per PR, unless the team specifically values preserving full commit-level history. |

## Reference implementation

Example Conventional Commits messages for a typical feature branch history:

```bash
git commit -m "feat(orders): add support for percentage-based discount codes"
git commit -m "fix(orders): correct rounding error in discount calculation"
git commit -m "test(orders): add coverage for discount edge cases"
git commit -m "docs(orders): document discount code API in README"

# A breaking change uses a ! after the type/scope and a footer explaining the break:
git commit -m "feat(api)!: require API key header on all order endpoints

BREAKING CHANGE: requests without an X-Api-Key header now return 401."
```

- The `!` and `BREAKING CHANGE:` footer are what automated semantic-release tooling uses to trigger a major version bump.
- Consistent `type(scope):` prefixes let changelog generators group entries automatically by category.

### A branch protection configuration enforcing review and CI before merge (YAML)

Preventing unreviewed or failing changes from reaching main:

```yaml
# GitHub branch protection rule (illustrative, configured via repo settings or API)
required_status_checks:
  strict: true
  contexts: ["ci/build", "ci/test"]
required_pull_request_reviews:
  required_approving_review_count: 1
enforce_admins: true
```

## Checklist

- [ ] Feature branches are short-lived and merged frequently via a trunk-based model.
- [ ] Every commit follows the Conventional Commits `type(scope): subject` format.
- [ ] Commits are atomic, each representing one logical, reviewable change.
- [ ] Breaking changes are marked with `!` and a `BREAKING CHANGE:` footer.
- [ ] The main branch is protected, requiring passing CI and at least one review before merge.
- [ ] Changelog and version bumps are automated from commit history where feasible.

## Anti-patterns

- **Long-lived divergent branches** - Keeping a feature branch alive for weeks without merging, accumulating conflict risk and drift from main.
- **Inconsistent commit message formats** - Mixing free-form commit messages with no structure, making automated changelog generation impossible.
- **Giant, unfocused commits** - Bundling unrelated changes (a bug fix, a refactor, and a new feature) into a single commit, making review and revert difficult.
- **Force-pushing over shared history** - Rewriting and force-pushing a branch other collaborators have already based work on, silently discarding their changes.
- **Unprotected main branch** - Allowing direct pushes to main with no required review or passing CI check, permitting unreviewed changes to ship.

## Verification

- A commit-lint check in CI confirms all commit messages conform to the Conventional Commits format.
- The main branch's protection settings show required status checks and review count enforced.
- An automated changelog generation run produces a correctly categorized changelog from recent commit history.
- A sample of recent PRs shows atomic, focused commits with clear, structured messages.

## References

- skills/90-delivery/shipping-checklist/SKILL.md
- skills/00-core/requirements-to-code-traceability/SKILL.md
- Conventional Commits specification (conventionalcommits.org).
