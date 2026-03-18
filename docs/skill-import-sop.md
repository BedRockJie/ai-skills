# Skill Import SOP

## Purpose

Use this SOP when importing a skill from an external repository into this
library, then preparing it for reuse in concrete projects.

This SOP assumes the target output is:

- a local copy under `skills/<skill-name>/`
- valid `SKILL.md` front matter for OpenCode
- local validation passing
- source traceability preserved
- project usage documented when needed

---

## Standard Flow

### 1. Choose the upstream skill

Before importing, confirm:

- the skill is actually reusable across more than one project
- the upstream workflow is already strong enough to preserve
- local changes are likely to be small and compatibility-focused

If the skill is deeply project-specific, do not add it here first.

---

### 2. Import the skill

Recommended command pattern:

```bash
npx skills add <repo-url> --skill <skill-name>
```

Example:

```bash
npx skills add https://github.com/anthropics/skills --skill pptx
```

Expected result:

- files appear under `skills/<skill-name>/`
- `SKILL.md` is present
- any upstream helper scripts or docs are copied with it

---

### 3. Inspect the imported files

Check the imported directory immediately:

```bash
find skills/<skill-name> -maxdepth 2 -type f | sort
sed -n '1,80p' skills/<skill-name>/SKILL.md
```

Confirm:

- `SKILL.md` exists
- helper docs are included if referenced
- scripts referenced by the skill are actually present
- no upstream files are obviously broken or incomplete

---

### 4. Normalize front matter

Every `SKILL.md` in this repository must start with YAML front matter.

Allowed fields:

- `name` required
- `description` required
- `license` optional
- `compatibility` optional
- `metadata` optional

Minimal template:

```yaml
---
name: <skill-name>
description: <one-line summary>
license: <license if known>
---
```

Rules:

- `name` must match the directory name
- `description` should describe what the skill does, not its entire procedure
- preserve upstream license information when available
- do not invent unsupported fields just because another tool accepts them

---

### 5. Preserve source traceability

Do not import a skill and lose its origin.

Record at least:

- upstream repository
- imported skill path
- import command used
- license source when relevant

Preferred places:

- `references/`
- a local `## References` section if the skill format uses one
- integration notes in `docs/`

---

### 6. Check compatibility gaps

After import, inspect the skill for local compatibility issues.

Typical gaps:

- missing front matter
- different Markdown structure from local templates
- missing dependency notes
- scripts that assume tools not present locally
- links that point to files not copied into the repo

Do not rewrite the whole skill unless necessary.
Prefer the smallest compatibility adjustment that keeps the upstream workflow
usable.

---

### 7. Validate locally

Run the local validator:

```bash
python3 scripts/validate_skills.py
```

Interpretation:

- `ERROR` means the imported skill is not yet acceptable for this repo
- `WARNING` means the skill is usable but should be reviewed for consistency

If the validator is too rigid for a legitimate upstream format, fix the
validator logic instead of forcing a destructive rewrite of the skill.

---

### 8. Document runtime dependencies

If a skill depends on external tooling, document it before treating the import
as complete.

Examples:

- Node packages
- Python packages
- system binaries
- office or media conversion tools

At minimum, note:

- what dependency is required
- what it is used for
- whether it is optional or mandatory

---

### 9. Define project-level usage

This repository stores reusable skills, but the real goal is project
application.

For each imported skill, define where it should be used:

- which project types benefit from it
- what context needs to come from the target project
- what should remain outside this repo

Example:

- `pptx` belongs here as a reusable presentation skill
- brand style, deck narrative, and business content belong in the target project

---

### 10. Mark the import complete

Treat the import as complete only when all of the following are true:

- files are present under `skills/<skill-name>/`
- `SKILL.md` has valid front matter
- source attribution is preserved
- local validation passes
- dependencies are documented
- project usage is clear enough for reuse

---

## Quick Checklist

- imported into `skills/<skill-name>/`
- `SKILL.md` starts with YAML front matter
- `name` matches the directory name
- `description` is present
- source is traceable
- dependencies are documented
- `python3 scripts/validate_skills.py` passes
- project usage is understood

---

## Example: `pptx`

Real command:

```bash
npx skills add https://github.com/anthropics/skills --skill pptx
```

Typical follow-up actions:

1. verify `skills/pptx/SKILL.md`
2. preserve Anthropic attribution
3. ensure required front matter exists
4. validate with `python3 scripts/validate_skills.py`
5. document how `pptx` should be applied in presentation-oriented projects
