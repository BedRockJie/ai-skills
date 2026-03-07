# Git Skill – Examples

## Example 1: Feature branch workflow

```bash
# 1. Start from a clean main
git checkout main && git pull

# 2. Create a feature branch
git checkout -b feature/user-authentication

# 3. Make changes, stage, and commit
git add src/auth/
git commit -m "Add JWT-based user authentication

Implements login/logout endpoints with 24-hour token expiry.
Closes #12"

# 4. Rebase onto latest main before opening a PR
git fetch origin
git rebase origin/main

# 5. Push
git push -u origin feature/user-authentication
```

---

## Example 2: Squashing fixup commits

You made three commits but only the first is meaningful:

```
abc1234 Add search feature
def5678 fix typo
fed9012 remove debug print
```

Squash the last two into the first:

```bash
git rebase -i HEAD~3
# In the editor: mark def5678 and fed9012 as 'fixup'
```

Result: one clean commit ready for review.

---

## Example 3: Resolving a merge conflict

```bash
git rebase origin/main
# CONFLICT (content): Merge conflict in src/config.py

# Inspect
git status

# Edit src/config.py to resolve <<<<<<< / ======= / >>>>>>> markers

git add src/config.py
git rebase --continue
```

---

## Example 4: Tagging a release

```bash
git tag -a v2.0.0 -m "Release v2.0.0: Add payment module"
git push origin v2.0.0
```
