#!/usr/bin/env python3
"""Minimal C unit test runner.

Discovers all test_*.c files under a directory, compiles each one
against its production source file (if found), runs the resulting
binary, and reports a summary.

Usage:
    python3 skills/testing/test_runner.py [TEST_DIR] [SRC_DIR]

Defaults:
    TEST_DIR  = test/
    SRC_DIR   = src/

File layout convention:
    src/crc16.c        -- production module
    test/test_crc16.c  -- tests for crc16 (includes test_utils.h + crc16.c)

Each test_*.c file must:
  - Include "test_utils.h"  (provides TEST_ASSERT and the test runner macro)
  - Define a main() that calls RUN_TESTS(...)

test_utils.h is embedded inside this script and written to the build
directory automatically — no manual download or install required.

Exit codes:
  0  All tests passed
  1  One or more tests failed or failed to compile

Requirements:
  gcc (or set CC environment variable to an alternative compiler)
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


# ── Embedded test_utils.h ────────────────────────────────────────────────────
# A minimal, zero-dependency C test utility header.
# Copy or symlink this into your project's test/ directory and commit it.
TEST_UTILS_H = r"""
/*
 * test_utils.h — minimal C unit test utilities.
 * No external dependencies; compile as part of each test_*.c file.
 *
 * Usage:
 *   #include "test_utils.h"
 *
 *   static void test_add_positive_numbers(void) {
 *       TEST_ASSERT(add(2, 3) == 5, "2+3 should be 5");
 *   }
 *
 *   int main(void) {
 *       RUN_TESTS(
 *           test_add_positive_numbers,
 *       );
 *   }
 */

#ifndef TEST_UTILS_H
#define TEST_UTILS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Internal state */
static int _tests_run    __attribute__((unused)) = 0;
static int _tests_passed __attribute__((unused)) = 0;
static int _tests_failed __attribute__((unused)) = 0;

/* ── TEST_ASSERT ─────────────────────────────────────────────────────────── */
/* Assert that CONDITION is true; print a FAIL line if not. */
#define TEST_ASSERT(condition, message)                              \
    do {                                                             \
        if (!(condition)) {                                          \
            printf("  FAIL  %s:%d  %s\n",                           \
                   __FILE__, __LINE__, (message));                   \
            _tests_failed++;                                         \
        } else {                                                     \
            printf("  pass  %s\n", (message));                      \
            _tests_passed++;                                         \
        }                                                            \
        _tests_run++;                                                \
    } while (0)

/* ── TEST_ASSERT_EQ / TEST_ASSERT_STR ────────────────────────────────────── */
#define TEST_ASSERT_EQ(expected, actual, message)                    \
    TEST_ASSERT((expected) == (actual), message)

#define TEST_ASSERT_STR(expected, actual, message)                   \
    TEST_ASSERT(strcmp((expected), (actual)) == 0, message)

/* ── TEST_ASSERT_NULL / TEST_ASSERT_NOT_NULL ─────────────────────────────── */
#define TEST_ASSERT_NULL(ptr, message)     TEST_ASSERT((ptr) == NULL, message)
#define TEST_ASSERT_NOT_NULL(ptr, message) TEST_ASSERT((ptr) != NULL, message)

/* ── RUN_TESTS ───────────────────────────────────────────────────────────── */
/*
 * Call each test function in the comma-separated list, then print a summary
 * and exit with code 0 (all passed) or 1 (one or more failed).
 *
 * Example:
 *   RUN_TESTS(test_crc16_known_vector, test_crc16_empty_input);
 */
#define RUN_TESTS(...)                                               \
    do {                                                             \
        void (*_fns[])(void) = { __VA_ARGS__ };                     \
        size_t _n = sizeof(_fns) / sizeof(_fns[0]);                 \
        for (size_t _i = 0; _i < _n; _i++) {                        \
            _fns[_i]();                                              \
        }                                                            \
        printf("\n--- %d tests: %d passed, %d failed ---\n",        \
               _tests_run, _tests_passed, _tests_failed);           \
        exit(_tests_failed > 0 ? 1 : 0);                            \
    } while (0)

#endif /* TEST_UTILS_H */
""".lstrip()


# ── Compilation helpers ───────────────────────────────────────────────────────

def _find_production_source(test_file: Path, src_dir: Path) -> Path | None:
    """Return src/<module>.c for a test file named test_<module>.c, or None."""
    stem = test_file.stem  # e.g. "test_crc16"
    if stem.startswith("test_"):
        module = stem[len("test_"):]  # "crc16"
        candidate = src_dir / f"{module}.c"
        if candidate.exists():
            return candidate
    return None


def _compile_and_run(
    test_file: Path,
    src_file: Path | None,
    include_dir: Path,
    build_dir: Path,
    compiler: str,
    extra_cflags: list[str] | None = None,
) -> tuple[bool, str]:
    """Compile and run one test file.

    Returns:
        (passed, output) where passed is True when the test binary exits 0,
        False when compilation fails or the binary exits with a non-zero code.
        output contains the text printed by the binary, or a COMPILE ERROR
        block describing the failure.
    """
    binary = build_dir / test_file.stem
    sources: list[str] = [str(test_file)]
    if src_file:
        sources.append(str(src_file))

    compile_cmd = [
        compiler,
        "-std=c11",
        "-Wall",
        "-Wextra",
        "-g",
        f"-I{include_dir}",
        *(extra_cflags or []),
        *sources,
        "-o", str(binary),
    ]

    # Compile
    result = subprocess.run(
        compile_cmd,
        capture_output=True,
    )
    if result.returncode != 0:
        stderr_text = result.stderr.decode("utf-8", errors="replace").strip()
        output = (
            f"COMPILE ERROR:\n"
            f"  Command: {' '.join(compile_cmd)}\n"
            f"  stderr: {stderr_text}"
        )
        return False, output

    # Run
    result = subprocess.run(
        [str(binary)],
        capture_output=True,
    )
    output = result.stdout.decode("utf-8", errors="replace")
    if result.returncode != 0:
        return False, output
    return True, output


# ── Main ──────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    test_dir = Path(args[0]) if len(args) > 0 else Path("test")
    src_dir  = Path(args[1]) if len(args) > 1 else Path("src")
    compiler = os.environ.get("CC", "gcc")
    # CFLAGS: space-separated extra compile flags, e.g. CFLAGS="-DUNIT_TEST -DBOARD_STM32"
    raw_cflags = os.environ.get("CFLAGS", "").strip()
    extra_cflags = raw_cflags.split() if raw_cflags else []

    if not test_dir.is_dir():
        print(f"ERROR: test directory '{test_dir}' not found.", file=sys.stderr)
        print(f"Usage: python3 skills/testing/test_runner.py [TEST_DIR] [SRC_DIR]",
              file=sys.stderr)
        return 1

    test_files = sorted(test_dir.glob("test_*.c"))
    if not test_files:
        print(f"No test_*.c files found in '{test_dir}'.")
        return 0

    # Write test_utils.h into the test directory so #include "test_utils.h" works
    utils_path = test_dir / "test_utils.h"
    utils_path.write_text(TEST_UTILS_H, encoding="utf-8")

    sep = "=" * 60
    passed_total = 0
    failed_total = 0

    with tempfile.TemporaryDirectory(prefix="test_runner_") as tmp:
        build_dir = Path(tmp)

        for test_file in test_files:
            src_file = _find_production_source(test_file, src_dir)
            print(f"\n{sep}")
            print(f"TEST: {test_file.name}")
            if src_file:
                print(f"  src: {src_file}")
            else:
                print("  src: (none — test is self-contained)")

            passed, output = _compile_and_run(
                test_file, src_file, test_dir, build_dir, compiler, extra_cflags
            )
            print(output)
            if passed:
                passed_total += 1
                print(f"  RESULT: PASS")
            else:
                failed_total += 1
                print(f"  RESULT: FAIL", file=sys.stderr)

    total = passed_total + failed_total
    print(f"\n{sep}")
    print(f"SUMMARY: {total} test file(s): {passed_total} passed, {failed_total} failed")
    return 0 if failed_total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
