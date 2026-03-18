# Skill Integration Guide

## 1. Repository Positioning

This repository is a `skills` aggregation and integration library.

Its purpose is not limited to writing original skills from scratch. It is also
used to:

- collect good skills from external ecosystems
- adapt them to local conventions when needed
- document installation and compatibility details
- apply them in concrete projects

The practical unit here is not just a single skill file, but:

1. source skill
2. local compatibility adjustments
3. validation rules
4. project-level usage guidance

---

## 2. What Belongs Here

This repo is a good home for:

- original local skills
- imported upstream skills
- compatibility wrappers and validation rules
- usage notes for different agents or projects

This repo is not primarily for:

- storing all project knowledge
- defining one fixed multi-agent org chart
- building one project-specific prompt stack only

If a skill is broadly reusable across projects, it belongs here.
If it is specific to one product or one team workflow, document it in that
project first and only upstream it here if it generalizes cleanly.

---

## 3. External Skill Import

External skills can be pulled in and then adapted locally.

For the operational checklist, see
[`docs/skill-import-sop.md`](/home/emb/workspces/code-nv/ai-skills/docs/skill-import-sop.md).

Example:

```bash
npx skills add https://github.com/anthropics/skills --skill pptx
```

This is the right pattern when:

- the upstream skill is already strong
- you want to reuse it across multiple projects
- you need a local copy for validation, documentation, or small adaptation

After import, do not stop at copying files. Check:

1. does the skill match local directory conventions
2. does `SKILL.md` include required front matter
3. does the skill need local references or attribution
4. does it require extra scripts, binaries, or node/python packages
5. does it need project-specific usage notes in `docs/`

---

## 4. Front Matter Standard

For OpenCode compatibility, every `SKILL.md` in this repo should start with YAML
front matter.

Supported fields:

- `name` required
- `description` required
- `license` optional
- `compatibility` optional
- `metadata` optional

Minimal example:

```yaml
---
name: testing
description: Write and run minimal C unit tests with gcc and a header-only helper.
license: MIT
---
```

This front matter is used for machine discovery and indexing.
The Markdown body is still where the real workflow lives.

---

## 5. Local Adaptation Rules

When importing a skill, keep the adaptation boundary tight.

Prefer this order:

1. preserve upstream content if it already works
2. add missing front matter or compatibility notes
3. change validation logic only when the format difference is legitimate
4. add local wrapper docs instead of rewriting the upstream skill unnecessarily

Good local changes:

- adding front matter
- adding attribution
- documenting dependencies
- making validators accept legitimate upstream formats

Bad local changes:

- rewriting the whole skill just to match local aesthetics
- hiding the upstream origin
- coupling a generic skill to one project's internals

---

## 6. Project-Level Application

This repository is meant to be applied per project, not just stored centrally.

The usual workflow is:

1. identify the project type
2. select the relevant skills
3. load those skills into the target agent workflow
4. add project-specific context outside this repo

Examples:

- firmware project: `debugging`, `fault-decode`, `peripheral-init`, `testing`
- general coding project: `code-review`, `testing`, `conventional-commits`
- presentation/document project: `pptx`

The reusable skill stays here.
The project context, rules, and business constraints stay in the target project.

---

## 7. Documentation Expectations

When adding or importing a skill, document enough for future reuse:

- source repository
- install command
- compatibility assumptions
- required dependencies
- recommended project scenarios

If a skill came from another ecosystem, leave a clear trail so future updates
can compare local changes against upstream.

---

## 8. Suggested Layout

Use the repository in these layers:

- `skills/`: canonical local skill copies
- `references/`: attribution and upstream context
- `docs/`: integration guides, install flows, project usage
- `.agents/`: optional agent-role templates that compose skills, not replace them

If `.agents/` is added later, it should define how to orchestrate skills for a
role, not become the primary storage location for reusable skill logic.
