# Contributing to Code-Skills

Thanks for helping grow this catalog of engineering skills for coding
agents and humans alike. This document covers the essentials; see
`docs/skill-authoring-guide.md` for the full authoring reference.

## Adding a new skill

1. Pick the right category folder (see `README.md` for the list of
   ten categories).
2. Scaffold it:

   ```bash
   python scripts/new_skill.py --category 30-backend --name my-new-skill
   ```

3. Fill in every section of the generated `SKILL.md`. Do not leave
   placeholder text, `TODO` markers, or empty sections.
4. Regenerate the index:

   ```bash
   python scripts/generate_index.py
   ```

5. Validate:

   ```bash
   python scripts/validate_skills.py
   ```

6. Open a pull request using the PR template. Set `maturity: draft` for
   brand-new skills; a maintainer will bump it to `stable` after review.

## Editing an existing skill

- Bump the `updated` frontmatter field to today's date whenever you make
  a material change.
- Re-run `python scripts/validate_skills.py` and
  `python scripts/generate_index.py` before committing.

## Style rules

- One sentence per `description`, starting with "Use when".
- Keep code snippets under ~60 lines and use realistic, runnable syntax
  for the relevant stack (C#/.NET 8 for backend, TypeScript for
  frontend, YAML/HCL for infra, SQL for database).
- Never commit real secrets, credentials, or customer data. Use
  placeholders like `<YOUR_CONNECTION_STRING>`.
- Security skills are defensive only — do not include exploit code or
  step-by-step attack instructions.
- Keep `SKILL.md` files between 150 and 400 lines (hard cap: 500).

## Pull request checklist

- [ ] `python scripts/validate_skills.py` passes
- [ ] `python scripts/generate_index.py --check` passes
- [ ] Markdown lints cleanly (`markdownlint` via the CI workflow)
- [ ] No secrets or TODOs left in the diff

## Code of conduct

Be respectful and constructive in reviews. This repository is a shared
knowledge base — assume good faith and prefer clarifying questions over
blocking nitpicks.
