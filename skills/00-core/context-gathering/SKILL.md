---
name: context-gathering
description: Use when starting work in an unfamiliar codebase or module and you need to understand existing conventions before making changes.
category: core
tags: [discovery, codebase-exploration, research]
maturity: stable
updated: 2026-08-21
---

## Purpose

Changes that ignore existing conventions create inconsistency and rework. This skill describes a fast, targeted process for learning enough about a codebase's structure, patterns, and constraints before writing code, without over-investing time in exploration for its own sake.

It balances two failure modes: acting on incomplete understanding and causing rework, versus over-exploring and stalling on a task that could have started sooner.

## When to use / When NOT to use

**Use this skill when:**

- You are making your first change in a repository or module you have not touched before.
- The task description references files, systems, or terms you do not yet understand.
- You suspect there may already be an existing pattern for what you are about to build.
- You are about to introduce a new dependency and want to check if an equivalent already exists.

**Do NOT use this skill when:**

- You already have full, current context on the exact files you need to change.
- The task is isolated to a brand-new file with no existing conventions to follow.

## Prerequisites

- Read access to the repository, its README, and its build/test configuration.

## Workflow

1. **Read the entry points** - Check README, CONTRIBUTING, and top-level docs for stated conventions and architecture.
2. **Find an analogous example** - Search for an existing feature similar to what you are building and study its structure end-to-end.
3. **Identify the test and build commands** - Locate how the project is built, linted, and tested so you can verify your change the same way.
4. **Note naming and layering conventions** - Observe folder structure, naming patterns, and layering (e.g. controller -> service -> repository) actually used.
5. **Check for existing utilities** - Search for helpers, base classes, or shared libraries before writing new one-off logic.
6. **Check version and dependency constraints** - Confirm the language/framework/library versions in use so new code stays compatible.
7. **Scope your exploration** - Stop once you have enough context to proceed confidently; do not read the entire codebase.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| A similar feature already exists | Follow its exact pattern unless there is a documented reason to deviate. |
| No similar feature exists | Follow the closest architectural layer's conventions and note the new pattern in the PR description. |
| Conventions are inconsistent across the codebase | Follow the most recently updated, most-tested example, and flag the inconsistency rather than picking arbitrarily. |
| Time pressure limits exploration | Prioritize reading the file(s) you will directly modify and their immediate dependents/dependencies. |
| Documentation contradicts the actual code | Trust the code and tests over stale docs, and note the discrepancy for a follow-up doc fix. |

## Reference implementation

A quick context-gathering script using common CLI search tools:

```bash
# 1. Understand top-level layout and stated conventions
cat README.md CONTRIBUTING.md 2>/dev/null | head -100

# 2. Find an analogous existing feature (example: another CRUD endpoint)
grep -rl "class .*Controller" src/ | head -5

# 3. Identify build/test/lint commands
cat package.json | grep -A5 '"scripts"' 2>/dev/null
cat *.csproj Directory.Build.props 2>/dev/null | head -30

# 4. Check for existing shared utilities before writing new ones
grep -rl "class .*Validator" src/ | head -5

# 5. Confirm framework / language version constraints
cat global.json .nvmrc go.mod 2>/dev/null

# 6. Look for architectural decision records that explain 'why'
find . -iname 'ADR-*' -o -iname '*decision*record*' 2>/dev/null | head -10
```

### Example exploration summary before starting work

Capture findings briefly so the plan step in agent-build-workflow can reference them:

```text
Context summary: Adding rate limiting to /reset-password
  - Analogous example: LoginController already uses IRateLimiter (src/RateLimiting/).
  - Build/test: dotnet build, dotnet test --filter Auth (see README 'Testing' section).
  - Convention: middleware registered in Program.cs, one line per policy.
  - Existing utility: IRateLimiter.TryAcquire(key, window) — reuse, do not reimplement.
  - Version constraint: net8.0 per global.json; no external packages needed.
```

## Checklist

- [ ] An existing analogous example was found and studied, or its absence was noted explicitly.
- [ ] The project's build, lint, and test commands were identified before making changes.
- [ ] Naming and layering conventions actually observed in the code were followed.
- [ ] Existing utilities were reused instead of duplicated where applicable.
- [ ] Exploration was scoped to what is needed for this task, not the entire repository.
- [ ] Version/dependency constraints were checked before introducing new code.
- [ ] Any conflict between documentation and actual code behavior was flagged explicitly.

## Anti-patterns

- **Cargo-culting from memory** - Applying conventions from a different, unrelated codebase instead of what this repository actually uses.
- **Analysis paralysis** - Spending excessive time reading unrelated modules instead of the smallest set needed to proceed confidently.
- **Ignoring existing utilities** - Writing a new validation/mapping/logging helper when an equivalent already exists in the codebase.
- **Skipping the build/test discovery step** - Guessing at how to verify a change instead of using the project's actual tooling.
- **Trusting stale docs over code** - Following outdated documentation that contradicts what the current code and tests actually do.

## Verification

- You can name the specific file(s) used as the analogous example, if one exists.
- You can state the exact command used to build/test/lint the project.
- The resulting change matches the codebase's existing naming and structural conventions.
- Any discrepancy found between docs and code was flagged, not silently ignored.

## References

- skills/00-core/agent-build-workflow/SKILL.md
- skills/70-quality/refactoring-and-legacy-code/SKILL.md
