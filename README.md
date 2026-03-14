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

A **skill** is not a knowledge base.  It is an executable procedure — a
precise description of what an AI agent *does*, not what it *knows*.

Every skill has:

- **Inputs** — what the agent needs before starting
- **Instructions** — ordered, imperative steps the agent executes
- **Output** — the specific artifact the agent produces
- **Tool (where possible)** — a script the agent runs and acts on

The `conventional-commits` skill is the reference model: it takes a commit
message as input, runs `check_commit_message.py`, and either passes or rewrites
the message.  Every other skill follows the same pattern.

Skills are:

- **Small** – Each skill covers one focused task
- **Composable** – Skills can reference each other (e.g., debugging calls fault-decode)
- **Action-oriented** – Instructions start with a verb and produce a concrete artifact

## Structure

```
skills/
  conventional-commits/ – Write and validate commit messages (reference skill)
  fault-decode/         – Decode Cortex-M fault registers → diagnosis + fix hint
                          Tool: decode_cortexm_fault.py
  peripheral-init/      – Generate peripheral init code from MCU spec
  code-review/          – Style gate (clang-format + shellcheck + diff-size),
                          then embedded correctness checklist
                          Tool: run_style_checks.sh
  debugging/            – Run diagnostic procedure → root-cause + minimum fix
  testing/              – Write and run minimal C unit tests with gcc only
                          Tool: test_runner.py  |  Header: test_utils.h

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
