---
name: skill-authoring
description: Use when writing or updating a SKILL.md file in this catalog and you need to follow the required structure, frontmatter, and validation rules.
category: core
tags: [meta, documentation, skills-catalog]
maturity: stable
updated: 2026-08-21
---

## Purpose

This is the meta-skill for maintaining the Code-Skills catalog itself: it captures the structural rules that scripts/validate_skills.py enforces so that every skill is consistent, discoverable, and machine-checkable.

Following it consistently keeps the catalog usable both by human engineers browsing docs/INDEX.md and by coding agents parsing frontmatter to select the right skill automatically.

## When to use / When NOT to use

**Use this skill when:**

- You are creating a brand-new skill folder under skills/<category>/<name>/.
- You are updating an existing SKILL.md and need to preserve its required structure.
- You are reviewing a skill-authoring pull request.
- You are deciding whether a new topic deserves its own skill or belongs inside an existing one.

**Do NOT use this skill when:**

- You are writing general project documentation unrelated to the skills catalog — use docs/ conventions instead.

## Prerequisites

- docs/skill-authoring-guide.md read at least once.
- templates/SKILL.template.md as the starting point (via scripts/new_skill.py).
- PyYAML installed locally if you intend to run scripts/validate_skills.py directly.

## Workflow

1. **Scaffold from the template** - Run `python scripts/new_skill.py --category <dir> --name <slug>` to generate correct frontmatter and section order.
2. **Write a single-sentence description** - Start it with the literal words 'Use when' and keep it under 400 characters.
3. **Choose precise tags** - Pick 2-4 lowercase tags that would help someone searching docs/INDEX.md find this skill.
4. **Fill all ten sections in order** - Purpose, When to use/NOT, Prerequisites, Workflow, Decision guide, Reference implementation, Checklist, Anti-patterns, Verification, References.
5. **Add a real code or diagram example** - Use the correct language for the domain, and add a Mermaid diagram for architecture skills.
6. **Keep length in range** - Target 150-400 lines total; the validator hard-fails above 500.
7. **Validate and index** - Run `python scripts/validate_skills.py` and `python scripts/generate_index.py`, fixing any reported issues.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Unsure which category a skill belongs to | Pick the category matching where in the SDLC an engineer would reach for it first; cross-link from others. |
| Skill overlaps heavily with an existing one | Extend the existing skill instead of creating a near-duplicate. |
| Skill needs a diagram | Use a fenced ```mermaid block inside Reference implementation (or Workflow) rather than an external image. |
| Content does not fit in 400 lines | Split into two more focused skills rather than exceeding the limit. |
| Skill is still being drafted/reviewed | Set maturity: draft and only flip to stable after a peer review pass. |

## Reference implementation

The standard commands for authoring and validating a skill:

```bash
# Scaffold a new skill
python scripts/new_skill.py --category 30-backend --name outbox-pattern

# ... fill in skills/30-backend/outbox-pattern/SKILL.md ...

# Validate structure, frontmatter, and links
python scripts/validate_skills.py

# Regenerate the catalog index
python scripts/generate_index.py

# Confirm the index is not stale (used in CI)
python scripts/generate_index.py --check

# Optional: lint markdown locally before opening a PR
npx --yes markdownlint-cli '**/*.md' --ignore node_modules
```

### Example of a correctly filled frontmatter block

A concrete, valid frontmatter block for a hypothetical new skill:

```yaml
---
name: outbox-pattern
description: Use when you need to publish domain events reliably alongside a database transaction.
category: backend
tags: [messaging, reliability, transactions]
maturity: draft
updated: 2026-08-21
---
```

## Checklist

- [ ] Frontmatter has exactly the required keys: name, description, category, tags, maturity, updated.
- [ ] description starts with 'Use when' and is under 400 characters.
- [ ] name matches the folder name exactly and is kebab-case.
- [ ] All ten required H2 sections are present, in order, with no placeholder text.
- [ ] File length is between 150 and 400 lines (never over 500).
- [ ] python scripts/validate_skills.py passes with zero issues.
- [ ] docs/INDEX.md was regenerated and committed alongside the new/changed skill.

## Anti-patterns

- **Renaming section headings** - Using synonyms like 'Overview' instead of 'Purpose' breaks the validator's ordered-section check.
- **Leaving template placeholders** - Shipping text like '<situation 1>' verbatim instead of real content.
- **Overstuffed tags** - Adding a dozen loosely related tags instead of 2-4 precise ones that aid search.
- **Skipping validation before PR** - Opening a PR without having run validate_skills.py and generate_index.py locally first.
- **Duplicate skills** - Creating a near-copy of an existing skill instead of extending it, fragmenting the catalog.

## Verification

- `python scripts/validate_skills.py` exits 0 for the new/changed file.
- `python scripts/generate_index.py --check` reports the index as up to date after regeneration.
- A peer reviewer confirms the description accurately triggers on the intended situation.

## References

- docs/skill-authoring-guide.md
- templates/SKILL.template.md
- scripts/validate_skills.py
- docs/agent-integration.md
