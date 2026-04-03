---
name: codecheckflow
description: Run the standard PixelCore C++ code review workflow for incremental changes. Use this skill whenever the user asks for C++ code review, PR review, pre-commit review, clang-format checking, clang-tidy scanning, or a repository-specific review of changed C++/CUDA files. This skill runs tool checks first, stops immediately on tool failures, and only then invokes the incremental AI review skill.
---

# Code Check Flow

Use this skill for repository-specific C++ and CUDA code review in `PixelCore`.

This is the entry skill. It owns the full review flow:

1. Determine the incremental review scope
2. Run `clang-format` checking
3. Run `clang-tidy` scanning
4. Stop immediately if a tool fails
5. Run the incremental AI review
6. Return one concise Markdown report

Read these references before reviewing:

- `references/review-workflow.md`
- `references/tooling.md`

For the AI review stage, also read:

- `../codereviewcore/SKILL.md`

## Inputs

Prefer this precedence:

1. Explicit file list from the user
2. Explicit git range from the user
3. Current branch incremental diff against the default review base

If the user does not specify a base, use the current branch diff relative to its merge base with the default upstream branch when available. If that cannot be determined safely, fall back to the unstaged and staged working tree diff.

Review only changed C++ and CUDA sources by default:

- `*.c`
- `*.cc`
- `*.cpp`
- `*.cxx`
- `*.h`
- `*.hh`
- `*.hpp`
- `*.hxx`
- `*.cu`
- `*.cuh`

Ignore generated files, third-party code, and unrelated non-source files unless the user explicitly asks for them.

## Workflow

### 1. Establish review scope

Collect the exact changed files and the diff hunks that will be reviewed.

If there are no changed C++/CUDA files, return a short report saying no applicable files were found.

### 2. Run format checking

Use repository-native format checking first:

```bash
cmake --build build --target format-check
```

If the build directory is missing or the target is unavailable, report that as a blocking setup failure instead of guessing.

Do not run formatting that rewrites files unless the user explicitly asks for a fix.

### 3. Run static analysis

Follow `references/tooling.md`.

Default mode is incremental-file scanning. Support an explicit full-scan mode when the user asks.

Use the unified repository entrypoint:

```bash
cmake --build build --target clang-tidy-check
```

If `compile_commands.json` is missing, treat that as a blocking setup issue and stop. Do not silently skip `clang-tidy`.

### 4. Stop on tool failures

If either `clang-format` check or `clang-tidy` reports errors:

- do not run the AI review stage
- output the raw tool errors in the final report
- classify the result as blocked

### 5. Run AI incremental review

Only after both tools pass, invoke the AI review core skill.

At that stage, let the AI review skill load the repository review rules, issue library, and report template from its own references.

Focus on:

- correctness
- behavioral regressions
- hot-path and pipeline risks
- synchronization, queueing, and copy overhead
- forbidden Release-only overhead such as newly added `NVTX` / `NV Event`

### 6. Return one concise report

Let the AI review skill apply its report template after the tool stages pass.

The report must start with a problem summary.

Tool failures:

- include a short summary at the top
- then paste the raw tool output
- stop there

AI findings:

- keep them terse
- state only severity, location, problem, and direct fix suggestion
- do not add long narrative explanations

## Review policy

Severity levels:

- `blocker`: must be fixed before merge; breaks correctness, pipeline semantics, Release constraints, or review preconditions
- `major`: serious regression or high-probability defect
- `minor`: worthwhile correction, but not usually merge-blocking

When reviewing, prioritize findings over summary text.

If no findings are discovered after tools pass, say that explicitly and stop there.
