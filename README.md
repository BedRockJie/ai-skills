# AI Skills Library

A curated collection of reusable AI skills for CLI agents and coding assistants.

This repository contains modular **skills** that can be used by AI agents such as:

- [Codex CLI](https://github.com/openai/codex)
- [Claude Code](https://github.com/anthropics/claude-code)
- [OpenCode](https://github.com/opencode-ai/opencode)
- Local Agent frameworks

## Philosophy

Skills should be:

- **Small** – Each skill covers one focused concern
- **Composable** – Skills can be combined together
- **Source-traceable** – All inspiration and references are documented

## Structure

```
skills/
  git/          – Git workflow best practices
  debugging/    – Systematic debugging approaches
  architecture/ – Software design principles
  code-review/  – Code review guidelines
  testing/      – Testing strategies and patterns

references/     – Attribution for external sources
templates/      – Templates for adding new skills
```

## Usage

Skills can be loaded by AI agents through:

- Prompt injection
- Tool loading
- CLI frameworks

To use a skill, point your agent at the relevant `SKILL.md` file, e.g.:

```
@file skills/git/SKILL.md
```

## Adding a New Skill

1. Copy `templates/skill-template.md` into a new folder under `skills/`
2. Fill in the template sections
3. Add an `examples.md` if helpful
4. Open a PR

## References

Some skills are inspired by:

- <https://github.com/anthropics/skills>

See [`references/`](references/) for full attribution.

## License

[MIT](LICENSE)
