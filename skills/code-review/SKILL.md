# Skill: C/C++ Code Review Gate

## Purpose

Run deterministic review checks before AI review. Use this for C/C++ code in
Linux user-space, libraries, services, tools, and support code.

## When to use

Use this skill when:

- Reviewing a C or C++ change
- Self-reviewing before peer review
- Standardizing review around buildable, scriptable checks first

## Inputs

- A git branch ready for review
- A base branch, default `origin/main`
- A build command, usually passed with `BUILD_COMMAND`

## Instructions

Run the stages in order. Do not use AI review until the gates pass.

### 1. Classify the change

Mark the change type before review:

- `api/abi`
- `memory`
- `concurrency`
- `security`
- `build/tooling`

Mark more than one type if needed.

### 2. Run the style gate

```bash
bash skills/code-review/run_style_checks.sh [BASE_REF]
```

This checks:

- `clang-format` on changed C/C++ files
- `shellcheck` on changed shell files
- diff size limits

Rules:

- Missing required tools are a failure
- Stop if the script prints `RESULT: FAIL`
- Split large diffs before deeper review

### 3. Run the full gate

```bash
bash skills/code-review/run_review_gate.sh [BASE_REF]
```

This runs:

1. Style checks
2. Build validation
3. Optional static analyzers
4. Generic rule scanning
5. Risk summary generation

Environment variables:

- `BUILD_COMMAND`
- `CLANG_TIDY_COMMAND`
- `CPPCHECK_COMMAND`

### 4. Read the risk summary

Use the risk summary to focus the next review pass.

Look for:

- API or ABI changes
- ownership and cleanup changes
- lock or thread behavior changes
- error handling changes
- subprocess or file-handling risks
- build and packaging changes

### 5. Do AI review last

Only ask AI to review what the scripts cannot prove.

Focus on:

- design fit
- concurrency logic
- error recovery
- API clarity
- test coverage versus risk

Keep the AI input small:

- risk summary
- relevant diff
- any intentional warnings with rationale

### 6. Approve or request changes

- Approve when the gates pass and no `blocker:` remains
- Request changes when a gate fails or a `blocker:` remains

Comment format:

```
<tag>: [file:line] <one-sentence description>
  Expected: <correct pattern>
  Actual:   <what the diff shows>
```

Tags: `nit:` | `suggestion:` | `question:` | `blocker:`

## Examples

See [examples.md](examples.md).

## References

- [clang-format documentation](https://clang.llvm.org/docs/ClangFormat.html)
- [clang-tidy documentation](https://clang.llvm.org/extra/clang-tidy/)
- [cppcheck manual](https://cppcheck.sourceforge.io/manual.html)
- [shellcheck wiki](https://www.shellcheck.net/wiki/)
- [SEI CERT C Coding Standard](https://wiki.sei.cmu.edu/confluence/display/c)
