---
name: codereviewcore
description: Review incremental PixelCore C++ or CUDA changes after clang-format and clang-tidy have already passed. Use this skill whenever the task is to inspect changed code, identify repository-specific defects, assess pipeline or hot-path risk, and return concise findings with severity and direct fix suggestions.
---

# Code Review Core

Use this skill only after tool checks have passed or when the caller explicitly wants AI-only review.

Read these inputs before reviewing:

- incremental diff hunks
- nearby implementation context as needed
- `references/pixelcore-review-rules.md`
- `references/issue-library.md`
- `references/report-template.md`

## Scope

Review only incremental code by default.

Expand to surrounding context only when needed to answer:

- what consumes this result
- whether pipeline semantics changed
- whether synchronization or copy behavior changed
- whether ownership, lifetime, or validation assumptions still hold

Do not perform broad whole-repository style commentary.

## Output style

Return a concise code-review report.

Each finding must include:

- severity
- file and line
- direct problem statement
- direct modification suggestion

Do not write long explanations unless the risk would be unclear without one extra sentence.

## Review checklist

Inspect changed code for:

- correctness and behavioral regressions
- `ZeroDelayPipeline` / `OneFrameDelayPipeline` semantic damage
- hidden synchronization
- extra copies, conversions, allocations, or serialization
- stream ownership and submit-order ambiguity
- Release-forbidden instrumentation such as new `NVTX` / `NV Event`
- project-standard error handling, logging, and lifetime management issues

## Severity policy

- `blocker`: merge-blocking correctness, pipeline, or Release-rule issue
- `major`: serious defect or high-risk regression
- `minor`: useful corrective change with lower immediate risk

## Review discipline

- findings first
- no praise padding
- no changelog-style recap
- no suggestions that ignore repository constraints

If no findings are present, say so explicitly and stop there.
