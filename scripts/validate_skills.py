#!/usr/bin/env python3
"""Validate every skills/<category>/<skill-name>/SKILL.md file in the repo.

Checks performed:
  - Frontmatter exists, is valid YAML, and has no unknown keys.
  - `name` is kebab-case, matches the parent folder name, and is unique
    across the whole repository.
  - `description` is <= 400 characters and starts with the literal
    string "Use when".
  - `category` is one of the ten allowed category slugs.
  - The ten required H2 sections are present, in the exact required
    order (extra content between sections is allowed).
  - The file is no more than 500 lines long.
  - Any relative markdown links inside the file point at files that
    actually exist on disk.

Exit code is 0 when everything is valid, 1 otherwise. All problems are
printed before exiting so authors can fix everything in one pass.
"""

from __future__ import annotations

import re
import sys
import urllib.parse
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

ALLOWED_CATEGORIES = {
    "core",
    "planning",
    "architecture",
    "backend",
    "frontend",
    "database",
    "devops",
    "quality",
    "security",
    "delivery",
}

REQUIRED_KEYS = {"name", "description", "category", "tags", "maturity", "updated"}
ALLOWED_MATURITY = {"draft", "stable"}

REQUIRED_SECTIONS = [
    "Purpose",
    "When to use / When NOT to use",
    "Prerequisites",
    "Workflow",
    "Decision guide",
    "Reference implementation",
    "Checklist",
    "Anti-patterns",
    "Verification",
    "References",
]

MAX_LINES = 500
MAX_DESCRIPTION_LEN = 400

KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


class ValidationError:
    def __init__(self, path: Path, message: str):
        self.path = path
        self.message = message

    def __str__(self) -> str:
        rel = self.path.relative_to(REPO_ROOT) if self.path.is_absolute() else self.path
        return f"{rel}: {self.message}"


def find_skill_files() -> list[Path]:
    if not SKILLS_DIR.exists():
        return []
    return sorted(SKILLS_DIR.glob("*/*/SKILL.md"))


def validate_file(path: Path, seen_names: dict[str, Path]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    text = path.read_text(encoding="utf-8")

    match = FRONTMATTER_RE.match(text)
    if not match:
        errors.append(ValidationError(path, "missing or malformed YAML frontmatter (must start/end with '---')"))
        return errors

    raw_frontmatter, body = match.group(1), match.group(2)

    try:
        frontmatter = yaml.safe_load(raw_frontmatter)
    except yaml.YAMLError as exc:
        errors.append(ValidationError(path, f"malformed YAML frontmatter: {exc}"))
        return errors

    if not isinstance(frontmatter, dict):
        errors.append(ValidationError(path, "frontmatter must be a YAML mapping"))
        return errors

    keys = set(frontmatter.keys())
    unknown_keys = keys - REQUIRED_KEYS
    missing_keys = REQUIRED_KEYS - keys
    if unknown_keys:
        errors.append(ValidationError(path, f"unknown frontmatter keys: {sorted(unknown_keys)}"))
    if missing_keys:
        errors.append(ValidationError(path, f"missing frontmatter keys: {sorted(missing_keys)}"))

    folder_name = path.parent.name
    name = frontmatter.get("name")
    if name is not None:
        if not isinstance(name, str) or not KEBAB_CASE_RE.match(name):
            errors.append(ValidationError(path, f"name '{name}' is not kebab-case"))
        if name != folder_name:
            errors.append(ValidationError(path, f"name '{name}' does not match folder name '{folder_name}'"))
        if name in seen_names:
            errors.append(
                ValidationError(
                    path,
                    f"duplicate name '{name}' also used by {seen_names[name].relative_to(REPO_ROOT)}",
                )
            )
        else:
            seen_names[name] = path

    description = frontmatter.get("description")
    if description is not None:
        if not isinstance(description, str):
            errors.append(ValidationError(path, "description must be a string"))
        else:
            if len(description) > MAX_DESCRIPTION_LEN:
                errors.append(
                    ValidationError(
                        path,
                        f"description is {len(description)} chars, must be <= {MAX_DESCRIPTION_LEN}",
                    )
                )
            if not description.startswith("Use when"):
                errors.append(ValidationError(path, "description must start with 'Use when'"))

    category = frontmatter.get("category")
    if category is not None and category not in ALLOWED_CATEGORIES:
        errors.append(
            ValidationError(path, f"category '{category}' not in allowed set {sorted(ALLOWED_CATEGORIES)}")
        )

    tags = frontmatter.get("tags")
    if tags is not None and not isinstance(tags, list):
        errors.append(ValidationError(path, "tags must be a YAML list"))

    maturity = frontmatter.get("maturity")
    if maturity is not None and maturity not in ALLOWED_MATURITY:
        errors.append(ValidationError(path, f"maturity '{maturity}' must be one of {sorted(ALLOWED_MATURITY)}"))

    updated = frontmatter.get("updated")
    if updated is not None:
        updated_str = str(updated)
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", updated_str):
            errors.append(ValidationError(path, f"updated '{updated}' must be an ISO date YYYY-MM-DD"))

    # Section presence / ordering.
    found_sections = H2_RE.findall(body)
    normalized_found = [s.strip() for s in found_sections]
    filtered = [s for s in normalized_found if s in REQUIRED_SECTIONS]
    missing_sections = [s for s in REQUIRED_SECTIONS if s not in normalized_found]
    if missing_sections:
        errors.append(ValidationError(path, f"missing required H2 sections: {missing_sections}"))
    elif filtered != REQUIRED_SECTIONS:
        errors.append(
            ValidationError(
                path,
                f"H2 sections out of order. Expected {REQUIRED_SECTIONS}, found {filtered}",
            )
        )

    # Line count.
    line_count = len(text.splitlines())
    if line_count > MAX_LINES:
        errors.append(ValidationError(path, f"file has {line_count} lines, must be <= {MAX_LINES}"))

    # Relative link validation.
    for link in MD_LINK_RE.findall(body):
        link = link.strip()
        if not link or link.startswith("#"):
            continue
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://", link):
            continue  # absolute URL (http, https, mailto, etc.)
        if link.startswith("mailto:"):
            continue
        link_path = link.split("#", 1)[0]
        if not link_path:
            continue
        link_path = urllib.parse.unquote(link_path)
        target = (path.parent / link_path).resolve()
        if not target.exists():
            errors.append(ValidationError(path, f"broken relative link: '{link}'"))

    return errors


def main() -> int:
    skill_files = find_skill_files()
    if not skill_files:
        print("No skill files found under skills/*/*/SKILL.md")
        return 0

    all_errors: list[ValidationError] = []
    seen_names: dict[str, Path] = {}
    for path in skill_files:
        all_errors.extend(validate_file(path, seen_names))

    if all_errors:
        print(f"Found {len(all_errors)} issue(s) across {len(skill_files)} skill file(s):\n")
        for error in all_errors:
            print(f"  - {error}")
        return 1

    print(f"All {len(skill_files)} skill file(s) passed validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
