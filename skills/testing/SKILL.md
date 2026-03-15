# Skill: C Unit Testing (Minimal)

## Purpose

Write and run small C unit tests with `gcc` and one header-only test helper.
No framework install is required.

## When to use

Use this skill when:

- Adding a new C module and wanting tests first
- Reproducing a bug as a failing test
- Checking that a fix did not break nearby behavior

## Inputs

- A C module: `src/<module>.c` and `src/<module>.h`
- `gcc` on the host, or another compiler via `CC`

The runner writes `test/test_utils.h` automatically.

## Instructions

### 1. Create the test directory

```bash
mkdir -p test/
```

### 2. Write `test/test_<module>.c`

```c
#include "test_utils.h"
#include "../src/<module>.h"

static void test_<module>_<scenario>(void) {
    <set up inputs>
    <result> = <function>(<inputs>);
    TEST_ASSERT(<result> == <expected>, "<what should be true>");
}

int main(void) {
    RUN_TESTS(
        test_<module>_<scenario>,
    );
}
```

Naming rule: `test_<module>_<scenario>`.

Available assertions in `test_utils.h`:

| Macro | Use |
|-------|-----|
| `TEST_ASSERT(cond, msg)` | General condition |
| `TEST_ASSERT_EQ(expected, actual, msg)` | Integer equality |
| `TEST_ASSERT_STR(expected, actual, msg)` | String equality |
| `TEST_ASSERT_NULL(ptr, msg)` | Pointer is NULL |
| `TEST_ASSERT_NOT_NULL(ptr, msg)` | Pointer is not NULL |

### 3. Run the tests

```bash
python3 skills/testing/test_runner.py test/ src/
```

The runner:

1. Writes `test/test_utils.h`
2. Compiles each test with the matching source file when present
3. Runs the test binary
4. Prints PASS or FAIL and exits non-zero on failure

### 4. Handle platform-specific dependencies

If the module touches OS or hardware-specific APIs, stub them behind a compile
flag:

```c
#ifdef UNIT_TEST
static uint8_t _fake_txbuf[256];
static size_t _fake_txlen;

void uart_send_byte(uint8_t b) { _fake_txbuf[_fake_txlen++] = b; }
#else
void uart_send_byte(uint8_t b) {
    platform_uart_write(b);
}
#endif
```

Then compile with `-DUNIT_TEST`:

```bash
CC="gcc" CFLAGS="-DUNIT_TEST" python3 skills/testing/test_runner.py test/ src/
```

### 5. Commit a failing test with the fix

1. Write a test that fails on current code
2. Fix the bug
3. Re-run the tests
4. Commit the test and the fix together

## Examples

See [examples.md](examples.md).

## References

- [`gcc` man page](https://man7.org/linux/man-pages/man1/gcc.1.html)
- [Test Driven Development for Embedded C — James Grenning](https://pragprog.com/titles/jgade/test-driven-development-for-embedded-c/)
