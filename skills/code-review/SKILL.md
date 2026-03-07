# Skill: Code Review

## Purpose

Help AI agents perform thorough, constructive, and consistent code reviews that
improve code quality without discouraging contributors.

## When to use

Use this skill when:

- Reviewing a pull request or patch submitted by another developer
- Self-reviewing your own changes before requesting a review
- Establishing or enforcing a team code-review standard

## Instructions

### 1. Understand context before commenting

- Read the PR description and linked issue/ticket first.
- Checkout the branch and run the code if the change is non-trivial.
- Understand *why* the change was made, not just *what* changed.

### 2. Check correctness first

- Does the code actually solve the stated problem?
- Are edge cases handled (null inputs, empty collections, concurrent access)?
- Are errors handled and propagated correctly?

### 3. Check tests

- Is there test coverage for the new behaviour?
- Do existing tests still pass?
- Are tests testing behaviour (not implementation details)?

### 4. Check readability

- Are names (variables, functions, classes) clear and consistent with the
  existing codebase?
- Is the code self-explanatory, or does it need comments?
- Is dead code removed?

### 5. Check security and performance

- Are inputs validated / sanitised?
- Are credentials or secrets kept out of source code?
- Are expensive operations (DB queries, network calls) appropriately cached or
  batched?

### 6. Comment constructively

Use a tiered comment style:

| Prefix | Meaning |
|---|---|
| `nit:` | Minor style preference – author may choose to ignore |
| `suggestion:` | Improvement idea – not blocking |
| `question:` | Seeking understanding – not necessarily a problem |
| `blocker:` | Must be addressed before merge |

Example:

```
suggestion: extracting this into a helper function would make it easier to test.

nit: s/recieve/receive
```

### 7. Approve or request changes clearly

- Approve when correctness, tests, and security are satisfied.
- Request changes when there is at least one blocker.
- Avoid leaving a review in a perpetual "commented" state.

## References

- Inspired by https://github.com/anthropics/skills
- [Google Engineering Practices – Code Review](https://google.github.io/eng-practices/review/)
