# AI Skills Library

A reusable `skills` integration library for CLI agents and coding assistants.

This repo is not just for writing original skills. Its main job is to collect,
adapt, validate, and document skills that are actually useful across different
projects.

Works well with:

- [Codex CLI](https://github.com/openai/codex)
- [Claude Code](https://github.com/anthropics/claude-code)
- [OpenCode](https://github.com/opencode-ai/opencode)
- [Cursor CLI]()
- Local agent frameworks

## Philosophy

A skill is not a knowledge base. It is a procedure. It tells an agent what to
do, in what order, and what output to produce.

This repository is organized around three practical goals:

- collect high-value skills from different ecosystems
- normalize them so they can be reused in real projects
- document how to install and apply them per project

Each skill should include:

- Inputs
- Instructions
- Examples, when useful
- A tool or script, when possible

The `conventional-commits` skill is the reference model. It takes a commit
message, runs `check_commit_message.py`, and either passes or rewrites it.

Good skills are:

- Small
- Composable
- Action-oriented

Good integrations are:

- Source-aware
- Tool-compatible
- Project-oriented

## Structure

```text
skills/
  conventional-commits/ - Write and validate commit messages
  code-review/          - Run review gates before AI review
  debugging/            - Follow a debug workflow and record a fix
  fault-decode/         - Decode Cortex-M fault registers
  peripheral-init/      - Generate peripheral init code from a spec
  testing/              - Write and run small C unit tests

references/ - Attribution for external sources
templates/  - Templates for new skills
docs/       - Integration notes, workflows, and project usage
```

Some skills are general. Some are specialized.

## Usage

Point your agent to the relevant `SKILL.md` file.

```text
@file skills/code-review/SKILL.md
```

For the bigger picture, see:

- [docs/skill-integration-guide.md](/home/emb/workspces/code-nv/ai-skills/docs/skill-integration-guide.md)
- [docs/skill-import-sop.md](/home/emb/workspces/code-nv/ai-skills/docs/skill-import-sop.md)

## Validation

Run:

- `python3 scripts/validate_skills.py`
- `python3 skills/conventional-commits/check_commit_message.py --last-commit`

GitHub Actions runs the same checks on pushes and pull requests.

## Adding a New Skill

There are two supported paths:

1. Create a native skill in this repo from `templates/skill-template.md`
2. Import an external skill, then adapt and document it for local use

Example external import:

```bash
npx skills add https://github.com/anthropics/skills --skill pptx
```

When importing from another ecosystem:

- keep the upstream source traceable
- add or preserve required front matter
- validate it locally with `python3 scripts/validate_skills.py`
- document how that skill should be used in project contexts

## References

- <https://github.com/anthropics/skills>

See [`references/`](references/) for attribution.

## License

[MIT](LICENSE)
