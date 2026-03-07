# Skill: Git

## Purpose

Help AI agents follow consistent, clean Git workflows when working with source
code repositories — from branching and committing to resolving conflicts.

## When to use

Use this skill when:

- Creating a new branch for a feature, bug fix, or experiment
- Writing or reviewing commit messages
- Resolving merge conflicts
- Squashing or reorganizing commits before a merge/rebase
- Tagging releases or managing remote refs

## Instructions

### 1. Branching

- Use descriptive branch names: `feature/<short-description>`, `fix/<issue-id>`, `chore/<task>`.
- Branch off `main` (or the designated base branch) unless told otherwise.

```bash
git checkout -b feature/add-login-page
```

### 2. Commits

- Write imperative-mood subject lines under 72 characters:
  - ✅ `Add login endpoint`
  - ❌ `Added login endpoint`
- Separate subject from body with a blank line.
- Reference issue numbers when applicable: `Closes #42`.

```bash
git commit -m "Add login endpoint

Implements POST /auth/login with JWT response.
Closes #42"
```

### 3. Keeping history clean

- Prefer `git rebase` over `git merge` for integrating upstream changes on
  feature branches.
- Squash fixup commits before opening a PR:

```bash
git rebase -i HEAD~<n>
```

### 4. Conflict resolution

1. Run `git status` to identify conflicting files.
2. Open each file and resolve markers (`<<<<<<<`, `=======`, `>>>>>>>`).
3. Stage resolved files with `git add <file>`.
4. Continue the rebase/merge: `git rebase --continue` or `git merge --continue`.

### 5. Tags and releases

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

## Examples

See [examples.md](examples.md).

## References

- Inspired by https://github.com/anthropics/skills
- [Git SCM documentation](https://git-scm.com/doc)
- [Conventional Commits](https://www.conventionalcommits.org/)
