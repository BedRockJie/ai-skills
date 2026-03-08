#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "# Skill:",
    "## Purpose",
    "## When to use",
    "## Instructions",
    "## References",
]

RECOMMENDED_CHECKS = {
    "examples": "Add inline examples or an examples.md file when the skill benefits from concrete walkthroughs.",
    "numbered_instructions": "Prefer numbered instruction subsections such as '### 1. ...' for clarity.",
}


def find_skill_files(repo_root: Path) -> list[Path]:
    return sorted(repo_root.glob("skills/*/SKILL.md"))


def paragraph_after(lines: list[str], heading: str) -> str:
    try:
        start = lines.index(heading)
    except ValueError:
        return ""

    content: list[str] = []
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        if stripped:
            content.append(stripped)
    return " ".join(content)


def validate_skill(skill_file: Path) -> tuple[list[str], list[str]]:
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors: list[str] = []
    warnings: list[str] = []
    skill_dir = skill_file.parent
    skill_name = skill_dir.name

    for heading in REQUIRED_SECTIONS:
        if not any(line.strip() == heading for line in lines):
            errors.append(f"{skill_name}: missing required section '{heading}'")

    title_prefix = "# Skill:"
    title_line = next((line for line in lines if line.startswith(title_prefix)), "")
    if not title_line.strip():
        errors.append(f"{skill_name}: skill title must not be empty")
    else:
        title_content = title_line[len(title_prefix) :].strip()
        if not title_content:
            errors.append(f"{skill_name}: skill title must not be empty")

    purpose = paragraph_after(lines, "## Purpose")
    if not purpose:
        errors.append(f"{skill_name}: purpose section must include content")
    elif sum(purpose.count(mark) for mark in ".!?") > 2:
        warnings.append(
            f"{skill_name}: purpose is longer than two sentences; keep it concise if possible"
        )

    references = paragraph_after(lines, "## References")
    if not references:
        errors.append(f"{skill_name}: references section must include at least one entry")

    has_examples_section = "## Examples" in text
    has_examples_file = (skill_dir / "examples.md").exists()
    if not has_examples_section and not has_examples_file:
        warnings.append(f"{skill_name}: {RECOMMENDED_CHECKS['examples']}")

    if "### 1." not in text:
        warnings.append(f"{skill_name}: {RECOMMENDED_CHECKS['numbered_instructions']}")

    return errors, warnings


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    skill_files = find_skill_files(repo_root)

    if not skill_files:
        print("No skill files found under skills/*/SKILL.md", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    all_warnings: list[str] = []
    for skill_file in skill_files:
        errors, warnings = validate_skill(skill_file)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    for warning in all_warnings:
        print(f"WARNING: {warning}")

    if all_errors:
        for error in all_errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        f"Validated {len(skill_files)} skills successfully"
        + (f" with {len(all_warnings)} warning(s)" if all_warnings else "")
        + "."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
