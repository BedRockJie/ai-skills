# Skill Creator

Guide for creating effective skills.

## Overview

This skill provides guidance for creating modular, self-contained skills that extend an agent's capabilities.

## When to Use

- Creating a new skill from scratch
- Updating an existing skill
- Adding reusable workflows, domain knowledge, or tool integrations

## Quick Start

1. Run `python -m scripts.init_skill <skill-name>` to initialize
2. Edit `SKILL.md` with your skill content
3. Add `agents/openai.yaml` for UI metadata
4. Test with subagents

## Key Principles

1. **Concise is Key** - Only add context the agent doesn't already have
2. **Set Appropriate Degrees of Freedom** - Match specificity to task fragility
3. **Protect Validation Integrity** - Test independently without leaking answers

## Directory Structure

```
skill-name/
├── SKILL.md           # Required: name, description, instructions
├── agents/            # Optional: UI metadata
├── scripts/           # Optional: executable helpers
├── references/       # Optional: documentation
├── assets/            # Optional: output resources
├── doc/               # Optional: usage documentation
└── template/          # Optional: skill templates
```

## Scripts

- `scripts/init_skill.py` - Initialize a new skill
- `scripts/generate_openai_yaml.py` - Generate UI metadata
- `scripts/quick_validate.py` - Quick validation

## Resources

See `references/openai_yaml.md` for UI metadata generation guidelines.
