# Review Workflow

This workflow is the standard `PixelCore` incremental C++ review process.

## Sequence

1. Resolve review scope from explicit files, explicit git range, or current incremental diff
2. Keep only changed C++ / CUDA files
3. Run `clang-format` check using the repository target
4. Run `clang-tidy`
5. If a tool fails, stop immediately
6. If both tools pass, review the incremental diff with repository-specific rules
7. Return one Markdown report with a problem summary first

## Stop Conditions

Stop immediately when any of the following happens:

- `format-check` fails
- `clang-tidy` fails
- `compile_commands.json` is unavailable
- the review scope cannot be determined safely

When stopping, output:

- a short blocked summary
- the raw tool or setup error

Do not continue into AI review after a blocking tool failure.

## AI Review Stage

The AI review is intentionally incremental and terse.

Inspect:

- changed hunks first
- nearby functions, types, and call sites when needed for correctness
- repository rules and issue library before judging findings

Do not turn the report into a tutorial. Prefer direct review comments.
