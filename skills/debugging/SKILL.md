# Skill: Debugging

## Purpose

Guide AI agents through a systematic, reproducible debugging process for any
programming language or environment.

## When to use

Use this skill when:

- A test is failing and the root cause is unknown
- An application produces unexpected output or crashes
- Performance degradation needs to be investigated
- A regression appears after a recent change

## Instructions

### 1. Reproduce the issue

Before touching any code, confirm you can reproduce the problem reliably:

- Record exact inputs, environment, and steps
- Capture the full error message / stack trace
- Identify the earliest point where behavior diverges from expectation

### 2. Narrow the scope

Use a binary-search approach:

1. Comment out (or disable) half the suspected code path.
2. Determine which half contains the bug.
3. Repeat until the problem is isolated to a single function or line.

### 3. Inspect state

- Add targeted log statements or use a debugger to inspect variable values at
  the point of failure.
- Check assumptions: types, null/undefined, off-by-one errors, encoding issues.

```python
# Example: temporary debug print
print(f"[DEBUG] value={value!r}, type={type(value)}")
```

### 4. Form a hypothesis

Write down (or state) what you believe is causing the bug before making any
change. This prevents thrashing and helps document the fix.

### 5. Fix and verify

- Make the **smallest** possible change that addresses the root cause.
- Re-run the failing test / reproduction steps.
- Check that no other tests regressed (`git stash` → run tests → `git stash pop`
  is a useful technique).

### 6. Document

Leave a comment or commit message explaining:

- What the bug was
- Why it happened
- How the fix addresses it

## Examples

See [examples.md](examples.md).

## References

- Inspired by https://github.com/anthropics/skills
