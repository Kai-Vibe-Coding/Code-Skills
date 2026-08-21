---
name: technical-documentation
description: Use when writing or maintaining technical documentation such as READMEs, architecture docs, and runbooks so they stay accurate, discoverable, and useful to their intended audience.
category: delivery
tags: [documentation, readme, adr]
maturity: stable
updated: 2026-08-21
---

## Purpose

Documentation that's stale, scattered, or written for the wrong audience is worse than no documentation, since it actively misleads. This skill covers structuring documentation by audience and purpose (README for onboarding, ADRs for decisions, runbooks for operations) and keeping it maintained alongside the code it describes.

## When to use / When NOT to use

**Use this skill when:**

- You are writing a README, architecture overview, API reference, or operational runbook.
- Existing documentation has become stale or contradicts the current system behavior.
- A new team member's onboarding reveals gaps in existing documentation.

**Do NOT use this skill when:**

- You are documenting a specific architectural decision — use skills/10-planning/architecture-decision-records/SKILL.md and templates/adr.template.md instead.
- You are writing an operational incident runbook specifically — see skills/60-devops/incident-response-and-runbooks/SKILL.md.

## Prerequisites

- skills/10-planning/architecture-decision-records/SKILL.md for decision-specific documentation.
- templates/runbook.template.md for operational documentation structure.

## Workflow

1. **Identify the audience and purpose before writing** - A README onboarding a new contributor needs different content than an API reference for an external integrator.
2. **Keep a README focused on getting started quickly** - Cover what the project is, how to install/run it, and where to find deeper documentation, not exhaustive detail.
3. **Push deep detail into linked, purpose-specific documents** - Architecture rationale goes in ADRs, operational procedures go in runbooks, detailed API contracts go in generated API references.
4. **Keep documentation next to the code it describes** - Store docs in the same repository as the code, ideally in a `docs/` folder, so they change together and stay discoverable.
5. **Update documentation as part of the same PR as the code change** - Treat outdated documentation as a defect; require doc updates in the same review as the behavior change that invalidates it.
6. **Use diagrams for structure and flow, prose for rationale** - A Mermaid diagram communicates system structure faster than paragraphs; use prose to explain the 'why' behind decisions.
7. **Review documentation for accuracy periodically** - Schedule a periodic pass (e.g. quarterly) to catch documentation that's silently drifted from actual behavior.
8. **Write for the reader's context, not your own** - Avoid unexplained internal jargon or assumed context the target audience doesn't have.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Documenting why a technology choice was made | Write an ADR, not a README section, so the rationale is preserved as a discrete, dated decision record. |
| Documenting how to operate/troubleshoot a running service | Write a runbook using templates/runbook.template.md, not an ad hoc wiki page. |
| A PR changes observable behavior described in existing docs | Update the relevant documentation in the same PR, not as a follow-up 'someday' task. |
| Choosing what belongs in the top-level README vs. a deeper doc | Keep the README to a fast-onboarding overview; move deep technical detail to a linked doc in `docs/`. |
| Documentation is found to be stale during onboarding | Fix it immediately as a small PR rather than just noting it verbally to the new team member. |

## Reference implementation

A README skeleton structured for fast onboarding with links to deeper docs:

```markdown
# Order Service

Handles order creation, discount application, and fulfillment status for the storefront.

## Quick start
```bash
dotnet restore && dotnet run --project src/OrderService.Api
```

## Documentation
- Architecture overview: docs/architecture.md
- Architecture Decision Records: docs/adr/
- Operational runbook: docs/runbook.md
- API reference: docs/api-reference.md

## Contributing
See CONTRIBUTING.md for branching and commit conventions.
```

- The README stays short and links out to purpose-specific documents rather than embedding everything inline.
- Each linked document has a single clear purpose (architecture, decisions, operations, API), avoiding overlap and duplication.

### A documentation staleness check as a lightweight CI convention (Markdown)

A PR template checklist item enforcing docs-with-code updates:

```markdown
## PR Checklist
- [ ] Tests added/updated for this change
- [ ] Documentation updated to reflect any behavior change (README, ADR, or runbook)
- [ ] No stale references to removed/renamed functionality remain
```

## Checklist

- [ ] Documentation is structured by audience/purpose: README, ADRs, runbooks, API references, kept separate.
- [ ] The README stays focused on fast onboarding, linking out to deeper documents rather than embedding everything.
- [ ] Documentation lives in the same repository as the code it describes, kept in a discoverable location.
- [ ] Documentation updates ship in the same PR as the code change that invalidates prior docs.
- [ ] Diagrams are used for structure/flow; prose is reserved for rationale and context.
- [ ] A periodic review catches documentation that has silently drifted from actual system behavior.

## Anti-patterns

- **One giant README** - Cramming architecture rationale, API reference, and operational procedures all into a single sprawling README instead of purpose-specific documents.
- **Documentation as an afterthought** - Deferring documentation updates to a 'someday' follow-up task instead of the same PR as the invalidating code change.
- **Docs disconnected from code** - Storing documentation in a separate wiki or tool disconnected from the code repository, causing it to drift unnoticed.
- **Writing for yourself, not the reader** - Using unexplained internal jargon or assumed context that a new contributor or external integrator doesn't have.
- **Never revisiting existing docs** - Writing documentation once at project start and never reviewing it again as the system evolves, letting it silently become misleading.

## Verification

- A new team member can get a local environment running using only the README's quick start section.
- A sample of recent PRs that changed observable behavior shows corresponding documentation updates in the same PR.
- A periodic documentation review log exists showing stale content is found and corrected on a cadence.
- Documentation for architecture, decisions, and operations exists in clearly separated, appropriately named locations.

## References

- skills/10-planning/architecture-decision-records/SKILL.md
- skills/60-devops/incident-response-and-runbooks/SKILL.md
- templates/runbook.template.md
