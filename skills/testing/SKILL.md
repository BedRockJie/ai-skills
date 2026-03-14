# Skill: Embedded Firmware Testing

## Purpose

Help AI agents write effective, hardware-decoupled tests for embedded firmware
using the Unity + CMock framework and host-side native compilation — enabling
fast feedback loops without requiring physical hardware for every test run.

## When to use

Use this skill when:

- Writing unit tests for a new driver, state machine, or protocol parser
- Mocking hardware peripherals (SPI, I2C, UART, GPIO) in host-side tests
- Running static analysis to catch MISRA-C violations or undefined behaviour
- Deciding what level of testing to apply to safety-critical firmware code
- Diagnosing a flaky or brittle test in an embedded CI pipeline

## Instructions

### 1. Choose the right test level

| Level | What it tests | Runs on | Speed |
|---|---|---|---|
| Unit (host) | A single function or module with mocked HAL | PC (native GCC) | Very fast |
| Integration (host) | Multiple modules + fake peripheral responses | PC (native GCC) | Fast |
| Hardware-in-the-loop (HIL) | Full firmware on real target + test harness | Target MCU | Slow |
| System / acceptance | End-to-end product behaviour | Target + bench | Slowest |

Use host-side unit and integration tests as the foundation; reserve HIL tests
for timing-critical paths and hardware-dependent behaviour.

### 2. Structure firmware for testability

Decouple hardware access behind a HAL interface so the same logic can be
compiled and tested on a PC:

```c
/* hal_uart.h – abstract interface */
typedef struct {
    void (*send)(const uint8_t *data, size_t len);
    int  (*recv)(uint8_t *buf, size_t max_len, uint32_t timeout_ms);
} hal_uart_t;

/* application code depends on the interface, not the hardware */
void protocol_send_ack(const hal_uart_t *uart);
```

On the target, provide a real `hal_uart_t` backed by peripheral registers.
In tests, provide a mock or fake that records calls and returns controlled data.

### 3. Write unit tests with Unity

[Unity](https://github.com/ThrowTheSwitch/Unity) is a lightweight C unit-test
framework designed for embedded targets and host compilation:

```c
/* test_crc16.c */
#include "unity.h"
#include "crc16.h"

void setUp(void) {}    /* run before each test */
void tearDown(void) {} /* run after each test  */

void test_crc16_known_vector(void) {
    /* Arrange */
    const uint8_t data[] = {0x01, 0x02, 0x03};

    /* Act */
    uint16_t result = crc16_compute(data, sizeof(data));

    /* Assert */
    TEST_ASSERT_EQUAL_HEX16(0x6131, result);
}

void test_crc16_empty_buffer_returns_initial_value(void) {
    TEST_ASSERT_EQUAL_HEX16(0xFFFF, crc16_compute(NULL, 0));
}
```

### 4. Mock hardware with CMock

[CMock](https://github.com/ThrowTheSwitch/CMock) auto-generates mock
implementations from header files:

```bash
# Generate mocks from the HAL header
# (CMock submodule at tools/cmock/ — see https://github.com/ThrowTheSwitch/CMock)
ruby tools/cmock/lib/cmock.rb --mock_path=build/mocks src/hal/hal_spi.h
```

Use the generated mock in a test:

```c
#include "unity.h"
#include "mock_hal_spi.h"   /* CMock-generated */
#include "sensor_driver.h"

void test_sensor_read_returns_temperature(void) {
    /* Arrange: set up mock to return a known SPI response */
    uint8_t fake_response[] = {0x01, 0x90}; /* 400 in 0.1 °C units = 40.0 °C */
    hal_spi_transfer_ExpectAnyArgsAndReturn(HAL_OK);
    hal_spi_transfer_ReturnArrayThruPointer_rx_buf(fake_response, 2);

    /* Act */
    int16_t temp = sensor_read_temperature();

    /* Assert */
    TEST_ASSERT_EQUAL_INT16(400, temp);
}
```

### 5. Run tests on the host

Compile and run without hardware using native GCC:

```bash
# Example CMake target for host tests
cmake -DCMAKE_TOOLCHAIN_FILE=cmake/host-gcc.cmake -B build/test -S .
cmake --build build/test --target run_tests

# Or with Ceedling (Unity + CMock build system)
ceedling test:all
```

A minimal `cmake/host-gcc.cmake` toolchain file:

```cmake
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_C_COMPILER gcc)
set(CMAKE_C_FLAGS "-DUNIT_TEST -DUNITY_INCLUDE_CONFIG_H")
```

### 6. Run static analysis

Use `cppcheck` for fast host-side static analysis (free, no license required):

```bash
cppcheck --enable=all --inconclusive --std=c11 \
         --suppress=missingIncludeSystem \
         -I src/ src/ 2>&1 | tee cppcheck_report.txt
```

For MISRA-C compliance, use PC-lint Plus or Polyspace in CI.
At minimum, enable the compiler's own warnings:

```cmake
target_compile_options(firmware PRIVATE
    -Wall -Wextra -Wshadow -Wundef
    -Wno-unused-parameter   # remove once all stubs are implemented
    -fstack-usage           # generates .su files for stack analysis
)
```

### 7. Name tests descriptively

Format: `test_<module>_<scenario>_<expected_outcome>`

```c
/* Good */
void test_uart_rx_with_overrun_flag_returns_error(void) { ... }
void test_crc16_all_zeros_matches_spec_vector(void)     { ... }

/* Bad */
void test_uart(void) { ... }
void test1(void)     { ... }
```

### 8. Treat flaky tests as bugs

A test that sometimes passes and sometimes fails erodes trust in the suite.

- Common causes in firmware tests: uninitialized static state between tests,
  real-time dependency leaking into host tests, missing `setUp`/`tearDown`.
- Fix: call `memset` on any static module state inside `setUp`; mock all
  time-dependent functions (`HAL_GetTick`, `clock_gettime`).
- Never skip or `#if 0` a flaky test — fix or delete it.

## Examples

See [examples.md](examples.md).

## References

- [Unity Test Framework](https://github.com/ThrowTheSwitch/Unity)
- [CMock Mock Generator](https://github.com/ThrowTheSwitch/CMock)
- [Ceedling Build System](https://github.com/ThrowTheSwitch/Ceedling)
- [cppcheck Static Analyser](https://cppcheck.sourceforge.io/)
- [Test Driven Development for Embedded C – James Grenning](https://pragprog.com/titles/jgade/test-driven-development-for-embedded-c/)
