# AI Skills Library

A small library of reusable skills for CLI agents and coding assistants.

This repo includes skills for review, testing, debugging, commit hygiene, and
some hardware-specific tasks.

Works well with:

- [Codex CLI](https://github.com/openai/codex)
- [Claude Code](https://github.com/anthropics/claude-code)
- [OpenCode](https://github.com/opencode-ai/opencode)
- [Cursor CLI]()
- Local agent frameworks

## Philosophy

A skill is not a knowledge base. It is a procedure. It tells an agent what to
do, in what order, and what output to produce.

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
```

Some skills are general. Some are specialized.

## Usage

Point your agent to the relevant `SKILL.md` file.

```text
@file skills/code-review/SKILL.md
```

## Validation

Run:

- `python3 scripts/validate_skills.py`
- `python3 skills/conventional-commits/check_commit_message.py --last-commit`

GitHub Actions runs the same checks on pushes and pull requests.

## Adding a New Skill

1. Copy `templates/skill-template.md` into a new folder under `skills/`
2. Fill in the sections
3. Add `examples.md` if it helps
4. Open a PR

## References

- <https://github.com/anthropics/skills>

See [`references/`](references/) for attribution.

## License

[MIT](LICENSE)
