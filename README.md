# AI Skills Library — Embedded Systems Edition

A curated collection of reusable AI skills for embedded firmware development,
targeting CLI agents and coding assistants working with MCUs and SoCs
(ARM Cortex-M/A/R, x86, AMD/Intel embedded, RISC-V).

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
  git/                  – Git workflow for embedded firmware
                          (branching, binary artifacts, hardware-rev tags, submodules)
  conventional-commits/ – Conventional Commits guidance and validation script
  debugging/            – Embedded debugging: JTAG/SWD, GDB, HardFault, UART log
  architecture/         – Embedded firmware architecture: layered design, memory map, RTOS
  code-review/          – Embedded code review: volatile, ISR safety, MISRA-C, memory
  testing/              – Embedded testing: Unity/CMock, host-side, static analysis

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

## Validation

This repository does not need a traditional application build, but lightweight
automation is helpful to keep skills consistent.

- Run `python3 scripts/validate_skills.py` to check required skill structure
- Run `python3 skills/conventional-commits/check_commit_message.py --last-commit`
  to validate the latest local commit message
- GitHub Actions runs the same checks on pushes and pull requests

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
