# Skill: Embedded Firmware Test Generator

## Purpose

Generate a Unity test file from a C header, run the tests on the host (no
hardware required), and interpret failures — all without modifying production
firmware code.

## When to use

Use this skill when:

- Writing unit tests for a new driver, state machine, or protocol parser
- Mocking a hardware peripheral so tests run on a PC
- Running static analysis to catch undefined behaviour before hardware testing
- A test is flaky and needs diagnosis

## Inputs

- A `.h` header file with the public function signatures to test
- The RTOS or execution model (affects which types to mock)
- Whether CMock mock generation is available (`ruby` + CMock submodule)

## Instructions

### 1. Decouple hardware behind a HAL interface

If the module under test calls hardware registers directly, extract a HAL
struct before writing tests:

```c
/* hal_spi.h — abstract interface (no registers here) */
typedef struct {
    hal_status_t (*transfer)(const uint8_t *tx, uint8_t *rx, size_t len);
} hal_spi_t;

/* Module under test depends on the interface, not the register */
int16_t sensor_read_temperature(const hal_spi_t *spi);
```

On the target, pass a real `hal_spi_t`.  In tests, pass a mock or fake.

### 2. Generate the test file skeleton

For a header `src/<module>.h`, create `test/test_<module>.c`:

```c
/* test/test_<module>.c — generated skeleton */
#include "unity.h"
#include "<module>.h"
/* #include "mock_hal_<peripheral>.h"  — add if using CMock mocks */

void setUp(void)    { /* reset module state before each test */ }
void tearDown(void) { /* clean up after each test */ }

/* --- Test cases below --- */

void test_<module>_<scenario>_<expected>(void) {
    /* Arrange */

    /* Act */

    /* Assert */
    TEST_ASSERT_<MATCHER>(...);
}

/* Required by Unity standalone runner */
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_<module>_<scenario>_<expected>);
    return UNITY_END();
}
```

Name format: `test_<module>_<scenario>_<expected_outcome>`

```c
/* Good */
void test_crc16_known_vector_matches_spec(void) { ... }
void test_uart_rx_overrun_flag_returns_error(void) { ... }

/* Bad — too vague */
void test_uart(void) { ... }
void test1(void)     { ... }
```

### 3. Generate mocks with CMock (when available)

```bash
# Generate mock from HAL header
ruby tools/cmock/lib/cmock.rb --mock_path=build/mocks src/hal/hal_spi.h

# Use in the test file
#include "mock_hal_spi.h"

void test_sensor_read_calls_spi_transfer(void) {
    uint8_t fake_rx[] = {0x01, 0x90};   /* 40.0 °C in 0.1 °C units */
    hal_spi_transfer_ExpectAnyArgsAndReturn(HAL_OK);
    hal_spi_transfer_ReturnArrayThruPointer_rx(fake_rx, 2);

    TEST_ASSERT_EQUAL_INT16(400, sensor_read_temperature(&mock_spi));
}
```

### 4. Compile and run on the host

```bash
# CMake + host toolchain (no ARM target needed)
cmake -DCMAKE_TOOLCHAIN_FILE=cmake/host-gcc.cmake -B build/test -S .
cmake --build build/test --target run_tests

# Or with Ceedling
ceedling test:all
```

Minimal `cmake/host-gcc.cmake`:

```cmake
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_C_COMPILER gcc)
set(CMAKE_C_FLAGS "-DUNIT_TEST -DUNITY_INCLUDE_CONFIG_H")
```

Passing output:

```
test/test_crc16.c:25:test_crc16_known_vector_returns_0x6131:PASS
test/test_crc16.c:31:test_crc16_empty_buffer_returns_0xFFFF:PASS
-----------------------
2 Tests 0 Failures 0 Ignored
OK
```

### 5. Run static analysis

```bash
cppcheck --enable=all --inconclusive --std=c11 \
         --suppress=missingIncludeSystem \
         -I src/ src/ 2>&1 | tee cppcheck_report.txt
```

Enable compiler warnings in the build system:

```cmake
target_compile_options(firmware PRIVATE
    -Wall -Wextra -Wshadow -Wundef -fstack-usage)
```

For MISRA-C compliance: use PC-lint Plus or Polyspace in CI.

### 6. Diagnose a flaky test

A test that sometimes passes / sometimes fails must be fixed before merging.

Common embedded causes and fixes:

| Cause | Fix |
|-------|-----|
| Uninitialized static state between tests | Call `memset` on module state in `setUp` |
| Real-time dependency in host test | Mock `HAL_GetTick` / `clock_gettime` |
| Missing `setUp` / `tearDown` | Add reset logic for every stateful module |

Never `#if 0` or skip a flaky test — fix or delete it.

## Examples

See [examples.md](examples.md).

## References

- [Unity Test Framework](https://github.com/ThrowTheSwitch/Unity)
- [CMock Mock Generator](https://github.com/ThrowTheSwitch/CMock)
- [Ceedling Build System](https://github.com/ThrowTheSwitch/Ceedling)
- [cppcheck Static Analyser](https://cppcheck.sourceforge.io/)
- [Test Driven Development for Embedded C — James Grenning](https://pragprog.com/titles/jgade/test-driven-development-for-embedded-c/)
