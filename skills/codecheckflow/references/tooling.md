# Tooling Rules

## clang-format

Use the repository target:

```bash
cmake --build build --target format-check
```

Why:

- `AGENTS.md` states that `format-check` is the authoritative dry-run format gate
- the root `CMakeLists.txt` already wires this target to `.clang-format`

Rules:

- never rewrite files during review unless the user explicitly asks for fixes
- if `build/` or `format-check` is unavailable, treat that as a blocking setup problem

## clang-tidy

The repository exports compile commands through CMake and provides a unified CMake entrypoint for static analysis.

Review behavior:

- require `compile_commands.json`
- default to incremental-file scanning
- support explicit full-scan mode for `common/`, `gpuController/`, and `surfaceKeeper`

Preferred repository entrypoint:

```bash
cmake --build build --target clang-tidy-check
```

The CMake target should use a conservative default check set unless the repository later adds `.clang-tidy`.

The target should run in parallel by default, using the machine's logical core count unless `TIDY_JOBS` is explicitly overridden at configure time.

The default diagnostics scope should include repository-owned headers under `common/`, `gpuController/`, and `surfaceKeeper/`, and exclude diagnostics from `3rdparty/` headers.

For smoke tests or narrower scans, allow directory override at configure time:

```bash
cmake -S . -B build -G Ninja -DTIDY_DIRS=/abs/path/to/smaller/scope
cmake -S . -B build -G Ninja -DTIDY_DIRS=/abs/path/to/smaller/scope -DTIDY_JOBS=8
```

Rules:

- prefer the unified CMake target when available
- do not silently skip files that should be scanned
- if a file is outside the available compile database, report the setup issue
- report tool output directly on failure and stop

## Incremental scope

Default scope is incremental diff only.

Recommended base resolution:

1. user-provided file list
2. user-provided git range
3. merge-base against upstream default branch
4. staged + unstaged working tree diff as fallback

Only review changed source files. Exclude:

- `3rdparty/`
- generated artifacts
- binary files

## Output behavior

Tool failure output should be passed through with minimal wrapping.

Do not summarize away important tool diagnostics.
