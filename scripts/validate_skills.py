#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_SECTIONS = ["## Purpose", "## When to use", "## Instructions", "## References"]

RECOMMENDED_CHECKS = {
    "examples": "Add inline examples or an examples.md file when the skill benefits from concrete walkthroughs.",
    "numbered_instructions": "Prefer numbered instruction subsections such as '### 1. ...' for clarity.",
}

TITLE_PREFIX = "# Skill:"
ALLOWED_FRONT_MATTER_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
}


def find_skill_files(repo_root: Path) -> list[Path]:
    return sorted(repo_root.glob("skills/*/SKILL.md"))


def stripped_lines(lines: list[str]) -> list[str]:
    return [line.strip() for line in lines]


def find_heading_index(lines: list[str], heading: str) -> int | None:
    for index, line in enumerate(lines):
        if line == heading:
            return index
    return None


def paragraph_after(lines: list[str], heading: str) -> str:
    start = find_heading_index(stripped_lines(lines), heading)
    if start is None:
        return ""

    content: list[str] = []
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        if stripped:
            content.append(stripped)
    return " ".join(content)

def _split_front_matter(lines: list[str]) -> tuple[dict[str, str], int]:
    """
    Minimal YAML front matter parser.

    Returns:
      (front_matter_dict, content_start_index)
    If no front matter is present, returns ({}, 0).
    """
    # Skip leading empty lines
    idx = 0
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    if idx >= len(lines) or lines[idx].strip() != "---":
        return {}, 0

    fm: dict[str, str] = {}
    idx += 1
    while idx < len(lines):
        line = lines[idx].rstrip("\n")
        if line.strip() == "---":
            return fm, idx + 1
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in fm:
                fm[key] = value
        idx += 1
    # Unclosed front matter; treat as absent.
    return {}, 0


def _first_h1_title(normalized_lines: list[str]) -> str:
    for line in normalized_lines:
        if line.startswith("# ") and len(line) > 2:
            return line[2:].strip()
    return ""


def _detect_format(lines: list[str]) -> str:
    normalized = stripped_lines(lines)
    if any(line.startswith(TITLE_PREFIX) for line in normalized):
        return "repo"
    fm, start = _split_front_matter(lines)
    if fm and start > 0:
        return "front_matter"
    return "generic"


def validate_skill(skill_file: Path) -> tuple[list[str], list[str]]:
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    normalized_lines = stripped_lines(lines)
    errors: list[str] = []
    warnings: list[str] = []
    skill_dir = skill_file.parent
    skill_name = skill_dir.name

    fm, content_start = _split_front_matter(lines)
    if not fm or content_start <= 0:
        errors.append(f"{skill_name}: missing required YAML front matter header")
        return errors, warnings

    unknown_keys = sorted(set(fm.keys()) - ALLOWED_FRONT_MATTER_KEYS)
    for key in unknown_keys:
        warnings.append(
            f"{skill_name}: unknown front matter field '{key}' will be ignored by OpenCode"
        )

    fm_name = fm.get("name", "").strip()
    fm_desc = fm.get("description", "").strip()
    if not fm_name:
        errors.append(f"{skill_name}: front matter 'name' is required")
    if not fm_desc:
        errors.append(f"{skill_name}: front matter 'description' is required")
    if fm_name and fm_name != skill_name:
        errors.append(
            f"{skill_name}: front matter name '{fm_name}' does not match directory name"
        )

    fmt = _detect_format(lines)

    if fmt == "repo":
        for heading in REQUIRED_SECTIONS:
            if heading not in normalized_lines:
                errors.append(f"{skill_name}: missing required section '{heading}'")

        title_line = next(
            (line for line in normalized_lines if line.startswith(TITLE_PREFIX)),
            "",
        )
        if not title_line:
            errors.append(f"{skill_name}: skill title must not be empty")
        else:
            title_content = title_line[len(TITLE_PREFIX) :].strip()
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
            errors.append(
                f"{skill_name}: references section must include at least one entry"
            )

        has_examples_section = "## Examples" in normalized_lines
        has_examples_file = (skill_dir / "examples.md").exists()
        if not has_examples_section and not has_examples_file:
            warnings.append(f"{skill_name}: {RECOMMENDED_CHECKS['examples']}")

        if not any(line.startswith("### 1.") for line in normalized_lines):
            warnings.append(
                f"{skill_name}: {RECOMMENDED_CHECKS['numbered_instructions']}"
            )

    elif fmt == "front_matter":
        title = _first_h1_title(normalized_lines[content_start:] if content_start else normalized_lines)
        if not title:
            errors.append(f"{skill_name}: missing H1 title (expected a '# ...' heading)")

        # Anthropic skills often don't include our repo-specific sections; treat those as warnings.
        for heading in REQUIRED_SECTIONS:
            if heading not in normalized_lines:
                warnings.append(
                    f"{skill_name}: missing section '{heading}' (allowed for front matter skills)"
                )

        # Require the document to have some real body content beyond headings/front matter.
        body_lines = [
            ln.strip()
            for ln in lines[content_start:]
            if ln.strip() and not ln.strip().startswith("---")
        ]
        if len(body_lines) < 5:
            errors.append(f"{skill_name}: SKILL.md appears to be empty or too short")

        # Recommend adding references, but don't fail Anthropic-format skills.
        references = paragraph_after(lines, "## References")
        if not references:
            warnings.append(
                f"{skill_name}: references section is missing; add a '## References' when adapting upstream skills"
            )

    else:
        # Generic skill format: only require a non-empty H1 and non-trivial content.
        title = _first_h1_title(normalized_lines)
        if not title:
            errors.append(f"{skill_name}: missing H1 title (expected a '# ...' heading)")
        nonempty = [ln for ln in normalized_lines if ln and not ln.startswith("#")]
        if len(nonempty) < 3:
            errors.append(f"{skill_name}: SKILL.md appears to be empty or too short")

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
