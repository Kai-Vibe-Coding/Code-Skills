# Agent Integration Guide

This document explains how to point GitHub Copilot (or another coding
agent) at this repository so it can discover and apply the right skill
automatically.

## Why this repo exists

Coding agents perform best when given a small, targeted set of
instructions for the task at hand rather than an entire company wiki.
Each file in `skills/` is a self-contained, single-purpose playbook: a
description of when to use it, a step-by-step workflow, decision
tables, and a reference implementation. Agents can retrieve exactly the
skill(s) relevant to the current task instead of guessing.

## Recommended repo layout for consumption

Add this repository as a git submodule or a synced folder inside the
target project, for example at `.copilot/skills/` or `docs/skills/`.
Keep the internal `skills/<category>/<name>/SKILL.md` layout intact so
that tooling and links keep working.

```bash
git submodule add https://github.com/<org>/Code-Skills .copilot/skills
```

## Pointing an agent at a skill

Most coding agents (including Copilot CLI and Copilot Chat) accept a
file path or `#file` reference. Instruct the agent explicitly:

```text
Follow the workflow in .copilot/skills/skills/30-backend/cqrs-with-mediatr/SKILL.md
while implementing the OrderPlaced command handler.
```

For agents that support custom instruction files (for example a
`.github/copilot-instructions.md` or an agent-specific skills registry),
reference `docs/INDEX.md` so the agent can look up the right skill by
category or tag before starting work:

```markdown
See docs/INDEX.md in the Code-Skills catalog for a full list of
available skills, grouped by category, with a one-line description of
when to use each one.
```

## Selecting a skill programmatically

`docs/INDEX.md` is generated from the frontmatter of every skill and is
safe to parse as a markdown table. Each row contains the skill name
(linked to its `SKILL.md`), its category, one-sentence description,
tags, and maturity. An agent or script can:

1. Grep `docs/INDEX.md` for tags or keywords relevant to the current
   task.
2. Open the linked `SKILL.md` for the best match.
3. Follow the `## Workflow` section step by step, consulting the
   `## Decision guide` table when a fork in the road appears.
4. Use the `## Checklist` section to self-verify before declaring the
   task complete.

## Composing multiple skills

Real tasks often span categories. For example, adding a new REST
endpoint might combine:

- `skills/20-architecture/api-design-rest/SKILL.md`
- `skills/30-backend/validation-and-error-handling/SKILL.md`
- `skills/70-quality/integration-testing/SKILL.md`

Instruct the agent to read all relevant skills first, then execute the
combined workflow, resolving conflicts by preferring the more specific
skill (e.g. a backend-specific validation rule overrides a generic
architecture guideline).

## Keeping skills in sync

If you fork or vendor this repository, periodically re-run:

```bash
python scripts/validate_skills.py
python scripts/generate_index.py --check
```

to confirm the catalog you are shipping to agents is still internally
consistent after any local edits.

## Versioning

Each skill's `updated` frontmatter field acts as a lightweight version
marker. Pin agent instructions to a specific git tag or commit of this
repository in regulated environments where reproducibility matters.
