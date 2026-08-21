#!/usr/bin/env python3
"""Temporary generator: renders SKILL.md files from structured data.
Not part of the shipped repo; deleted after use.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"


def render(skill: dict) -> str:
    fm = []
    fm.append("---")
    fm.append(f"name: {skill['slug']}")
    fm.append(f"description: {skill['desc']}")
    fm.append(f"category: {skill['category']}")
    tags = ", ".join(skill["tags"])
    fm.append(f"tags: [{tags}]")
    fm.append(f"maturity: {skill.get('maturity', 'stable')}")
    fm.append(f"updated: {skill.get('updated', '2026-08-21')}")
    fm.append("---")
    fm.append("")

    body = []
    body.append("## Purpose")
    body.append("")
    purpose = skill["purpose"]
    paragraphs = purpose if isinstance(purpose, list) else [purpose]
    for i, para in enumerate(paragraphs):
        body.append(para)
        if i != len(paragraphs) - 1:
            body.append("")
    body.append("")

    body.append("## When to use / When NOT to use")
    body.append("")
    body.append("**Use this skill when:**")
    body.append("")
    for item in skill["when_use"]:
        body.append(f"- {item}")
    body.append("")
    body.append("**Do NOT use this skill when:**")
    body.append("")
    for item in skill["when_not"]:
        body.append(f"- {item}")
    body.append("")

    body.append("## Prerequisites")
    body.append("")
    for item in skill["prereqs"]:
        body.append(f"- {item}")
    body.append("")

    body.append("## Workflow")
    body.append("")
    for i, (name, detail) in enumerate(skill["workflow"], start=1):
        body.append(f"{i}. **{name}** - {detail}")
    body.append("")

    body.append("## Decision guide")
    body.append("")
    body.append("| Situation | Recommended approach |")
    body.append("| --- | --- |")
    for situation, rec in skill["decision"]:
        body.append(f"| {situation} | {rec} |")
    body.append("")

    body.append("## Reference implementation")
    body.append("")
    body.append(skill.get("code_intro", "Example:"))
    body.append("")
    body.append(f"```{skill['code_lang']}")
    body.append(skill["code"].rstrip("\n"))
    body.append("```")
    body.append("")
    if skill.get("code_notes"):
        for note in skill["code_notes"]:
            body.append(f"- {note}")
        body.append("")
    if skill.get("code2"):
        lang2, intro2, code2 = skill["code2"]
        body.append(f"### {skill.get('code2_heading', 'Additional example')}")
        body.append("")
        body.append(intro2)
        body.append("")
        body.append(f"```{lang2}")
        body.append(code2.rstrip("\n"))
        body.append("```")
        body.append("")

    body.append("## Checklist")
    body.append("")
    for item in skill["checklist"]:
        body.append(f"- [ ] {item}")
    body.append("")

    body.append("## Anti-patterns")
    body.append("")
    for name, detail in skill["antipatterns"]:
        body.append(f"- **{name}** - {detail}")
    body.append("")

    body.append("## Verification")
    body.append("")
    for item in skill["verification"]:
        body.append(f"- {item}")
    body.append("")

    body.append("## References")
    body.append("")
    for item in skill["references"]:
        body.append(f"- {item}")
    body.append("")

    return "\n".join(fm + body).rstrip() + "\n"


def write_all(skills: list[dict]):
    for skill in skills:
        d = SKILLS_DIR / skill["dir"] / skill["slug"]
        d.mkdir(parents=True, exist_ok=True)
        f = d / "SKILL.md"
        content = render(skill)
        f.write_text(content, encoding="utf-8")
        n = len(content.splitlines())
        print(f"{skill['dir']}/{skill['slug']}: {n} lines")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import importlib
    mods = sys.argv[1:] if len(sys.argv) > 1 else []
    all_skills = []
    for m in mods:
        mod = importlib.import_module(m)
        all_skills.extend(mod.SKILLS)
    write_all(all_skills)
    print(f"Total: {len(all_skills)} skills written")
