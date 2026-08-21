#!/usr/bin/env python3
"""Scaffold a new skill folder from templates/SKILL.template.md.

Usage:
    python scripts/new_skill.py --category 30-backend --name outbox-pattern

This creates skills/30-backend/outbox-pattern/SKILL.md with the
frontmatter `name` and `category` fields pre-filled based on the
arguments given. All other placeholder text from the template is left
in place for the author to fill in.
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = REPO_ROOT / "templates" / "SKILL.template.md"
SKILLS_DIR = REPO_ROOT / "skills"

KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

CATEGORY_SLUG_BY_DIR = {
    "00-core": "core",
    "10-planning": "planning",
    "20-architecture": "architecture",
    "30-backend": "backend",
    "40-frontend": "frontend",
    "50-database": "database",
    "60-devops": "devops",
    "70-quality": "quality",
    "80-security": "security",
    "90-delivery": "delivery",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--category",
        required=True,
        choices=sorted(CATEGORY_SLUG_BY_DIR.keys()),
        help="Category folder, e.g. 30-backend",
    )
    parser.add_argument("--name", required=True, help="Skill name in kebab-case, e.g. outbox-pattern")
    args = parser.parse_args()

    if not KEBAB_CASE_RE.match(args.name):
        print(f"error: --name '{args.name}' must be kebab-case", file=sys.stderr)
        return 1

    category_slug = CATEGORY_SLUG_BY_DIR[args.category]
    skill_dir = SKILLS_DIR / args.category / args.name
    skill_file = skill_dir / "SKILL.md"

    if skill_file.exists():
        print(f"error: {skill_file} already exists", file=sys.stderr)
        return 1

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    content = (
        template.replace("<skill-name>", args.name)
        .replace("<category-slug>", category_slug)
        .replace("<YYYY-MM-DD>", today)
    )

    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file.write_text(content, encoding="utf-8")
    print(f"Created {skill_file.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
