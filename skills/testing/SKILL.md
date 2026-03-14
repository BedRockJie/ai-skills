# Skill: C Unit Testing (Minimal)

## Purpose

Write and run unit tests for a C firmware module using only `gcc` and a
single-header test utility — no build system, no framework install, no hardware
required.

## When to use

Use this skill when:

- Adding a new C module (driver, parser, state machine, utility) and want tests
  before it goes to hardware
- Reproducing a bug as a failing test before fixing it
- Confirming a fix did not break other behaviour

## Inputs

- A C module: `src/<module>.c` + `src/<module>.h`
- `gcc` available on the host (or set `CC=arm-none-eabi-gcc` for cross-compile)

No other tools are required.  The test runner script writes `test_utils.h` into
your `test/` directory automatically.

## Instructions

### 1. Create the test directory

```bash
mkdir -p test/
```

### 2. Write `test/test_<module>.c`

```c
#include "test_utils.h"         /* written by test_runner.py on first run */
#include "../src/<module>.h"    /* the module under test */

/* One function per test case */
static void test_<module>_<scenario>(void) {
    /* Arrange */
    <set up inputs>

    /* Act */
    <result> = <function>(<inputs>);

    /* Assert */
    TEST_ASSERT(<result> == <expected>, "<description of what should be true>");
}

int main(void) {
    RUN_TESTS(
        test_<module>_<scenario>,
        /* add more test functions here */
    );
}
```

**Naming rule**: `test_<module>_<scenario>` — be specific:

```c
/* Good */
static void test_crc8_known_vector_returns_0xC0(void) { ... }
static void test_ring_buffer_full_returns_error(void) { ... }

/* Bad — too vague to diagnose failures */
static void test_crc(void) { ... }
static void test1(void)    { ... }
```

**Available assertions in `test_utils.h`**:

| Macro | Use |
|-------|-----|
| `TEST_ASSERT(cond, msg)` | General boolean condition |
| `TEST_ASSERT_EQ(expected, actual, msg)` | Integer equality (`==`) |
| `TEST_ASSERT_STR(expected, actual, msg)` | String equality (`strcmp`) |
| `TEST_ASSERT_NULL(ptr, msg)` | Pointer is NULL |
| `TEST_ASSERT_NOT_NULL(ptr, msg)` | Pointer is not NULL |

### 3. Run the tests

```bash
python3 skills/testing/test_runner.py test/ src/
```

The runner:

1. Writes `test/test_utils.h` (single-header utility, overwritten each run)
2. For each `test/test_<module>.c`, locates `src/<module>.c` and compiles both
   with `gcc -std=c11 -Wall -Wextra`
3. Runs the resulting binary and prints PASS / FAIL per assertion
4. Prints a summary and exits 0 (all passed) or 1 (failures)

**Passing output:**

```
============================================================
TEST: test_crc8.c
  src: src/crc8.c
  pass  empty data should return 0x00
  pass  crc8(0x00) should be 0x00
  pass  crc8({0x31,0x32,0x33}) should be 0xC0

--- 3 tests: 3 passed, 0 failed ---

  RESULT: PASS

============================================================
SUMMARY: 1 test file(s): 1 passed, 0 failed
```

### 4. Handle hardware dependencies

If the module under test calls hardware registers directly, stub those calls
out using a compile-time guard:

```c
/* src/uart.c */
#ifdef UNIT_TEST
/* Stub: no real hardware */
static uint8_t _fake_txbuf[256];
static size_t  _fake_txlen;

void uart_send_byte(uint8_t b) { _fake_txbuf[_fake_txlen++] = b; }
#else
void uart_send_byte(uint8_t b) {
    while (!(USART1->SR & USART_SR_TXE)) {}
    USART1->DR = b;
}
#endif
```

Compile the test with `-DUNIT_TEST`:

```bash
CC="gcc" CFLAGS="-DUNIT_TEST" python3 skills/testing/test_runner.py test/ src/
# (test_runner.py passes $CFLAGS automatically when set)
```

### 5. Commit a failing test before a bug fix

```bash
# 1. Write a test that reproduces the bug — it must FAIL on current code
python3 skills/testing/test_runner.py test/ src/
# → FAIL: test_ring_buffer_full_returns_error

# 2. Fix the bug in src/ring_buffer.c
# 3. Re-run — test must now PASS
python3 skills/testing/test_runner.py test/ src/
# → PASS

# 4. Commit both the test and the fix together
```

## Examples

See [examples.md](examples.md).

## References

- [`gcc` man page](https://man7.org/linux/man-pages/man1/gcc.1.html)
- [Test Driven Development for Embedded C — James Grenning](https://pragprog.com/titles/jgade/test-driven-development-for-embedded-c/)
