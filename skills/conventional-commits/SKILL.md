# Skill: Conventional Commits

## Purpose

Help AI agents create Git commit messages that follow the
Conventional Commits specification and verify the message before running
`git commit`.

## When to use

Use this skill when:

- Preparing a Git commit for code, docs, tests, or maintenance work
- You want consistent commit history that is easy to read and automate
- You want to validate a commit message before committing

## Instructions

### 1. Pick the correct commit type

- Use a Conventional Commits type such as `feat`, `fix`, `docs`, `test`,
  `refactor`, `chore`, `build`, `ci`, `perf`, `style`, or `revert`.
- Add an optional scope when it helps: `feat(api): add search endpoint`
- Use `!` only for breaking changes: `feat(api)!: remove v1 endpoint`

### 2. Write a valid subject line

- Format the first line as:

```text
type(optional-scope)!: short description
```

- Keep the description short, specific, and lowercase when possible.
- Good examples:
  - `feat: add commit message validator`
  - `fix(git): handle empty commit message`
  - `docs(readme): add conventional commits example`
- Avoid invalid subjects such as:
  - `update readme`
  - `Fix bug`
  - `feat add validator`

### 3. Validate before committing

- Run the validation script before `git commit`.
- Pass the message directly:

```bash
python3 skills/conventional-commits/check_commit_message.py \
  --message "feat: add conventional commits skill"
```

- Or validate a message file before using it with Git:

```bash
python3 skills/conventional-commits/check_commit_message.py \
  --file /tmp/commit-message.txt
git commit -F /tmp/commit-message.txt
```

### 4. Fix invalid messages before commit

- If validation fails, rewrite the first line so it matches the format.
- Do not commit until the script reports success.

## Examples

```bash
# Valid
python3 skills/conventional-commits/check_commit_message.py \
  --message "feat(cli): add commit pre-check"

# Invalid: missing colon
python3 skills/conventional-commits/check_commit_message.py \
  --message "feat(cli) add commit pre-check"
```

## References

- [Conventional Commits](https://www.conventionalcommits.org/)
- Inspired by https://github.com/anthropics/skills
