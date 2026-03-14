# Embedded Firmware Testing – Examples

## Example 1: Unit-testing a CRC-16 module with Unity

**Directory layout:**

```
src/
  crc16.c
  crc16.h
test/
  test_crc16.c
CMakeLists.txt
```

**test/test_crc16.c:**

```c
#include "unity.h"
#include "crc16.h"

void setUp(void) {}
void tearDown(void) {}

/* Known test vector from the CRC-16/CCITT-FALSE spec */
void test_crc16_known_vector_0x313233(void) {
    const uint8_t data[] = {0x31, 0x32, 0x33};
    TEST_ASSERT_EQUAL_HEX16(0x29B1, crc16_compute(data, sizeof(data)));
}

void test_crc16_single_byte_0x00(void) {
    const uint8_t data[] = {0x00};
    /* Verify against software reference, not hardware */
    uint16_t result = crc16_compute(data, 1);
    TEST_ASSERT_NOT_EQUAL(0x0000, result); /* must not be trivially zero */
}

void test_crc16_null_or_zero_length_returns_initial_value(void) {
    TEST_ASSERT_EQUAL_HEX16(0xFFFF, crc16_compute(NULL, 0));
    const uint8_t buf[4] = {0};
    TEST_ASSERT_EQUAL_HEX16(0xFFFF, crc16_compute(buf, 0));
}
```

**Run on host:**

```bash
ceedling test:test_crc16
# or
gcc -DUNIT_TEST -Isrc -Iunity/src \
    unity/src/unity.c src/crc16.c test/test_crc16.c -o test_crc16
./test_crc16
```

---

## Example 2: Mocking a SPI HAL with CMock

**src/hal/hal_spi.h** (the interface to mock):

```c
typedef enum { HAL_OK = 0, HAL_ERROR } hal_status_t;

hal_status_t hal_spi_transfer(uint8_t *tx_buf, uint8_t *rx_buf, size_t len);
```

**Generate the mock:**

> CMock is available at https://github.com/ThrowTheSwitch/CMock.
> Add it to your project as a Git submodule under `tools/cmock/`, then adjust
> the path below accordingly.

```bash
# If CMock is a submodule at tools/cmock/
ruby tools/cmock/lib/cmock.rb --mock_path=build/mocks src/hal/hal_spi.h
# Produces build/mocks/mock_hal_spi.c and mock_hal_spi.h
```

When using Ceedling, mock generation is automatic — just `#include "mock_hal_spi.h"`
and Ceedling discovers and builds the mock for you.

**test/test_bme280_driver.c:**

```c
#include "unity.h"
#include "mock_hal_spi.h"    /* CMock-generated */
#include "bme280_driver.h"

void setUp(void)    { }
void tearDown(void) { }

void test_bme280_read_chip_id_returns_0x60(void) {
    /* Arrange: first byte is dummy (SPI read command), second is chip ID */
    uint8_t fake_rx[] = {0x00, 0x60};
    hal_spi_transfer_ExpectAnyArgsAndReturn(HAL_OK);
    hal_spi_transfer_ReturnArrayThruPointer_rx_buf(fake_rx, 2);

    /* Act */
    uint8_t chip_id = bme280_read_chip_id();

    /* Assert */
    TEST_ASSERT_EQUAL_HEX8(0x60, chip_id);
}

void test_bme280_read_chip_id_returns_error_on_spi_failure(void) {
    hal_spi_transfer_ExpectAnyArgsAndReturn(HAL_ERROR);
    uint8_t chip_id = bme280_read_chip_id();
    TEST_ASSERT_EQUAL_HEX8(0x00, chip_id); /* error sentinel */
}
```

---

## Example 3: State machine unit test (no hardware dependency)

**Scenario:** Test the UART protocol parser state machine in isolation.

```c
#include "unity.h"
#include "protocol_parser.h"

static parser_ctx_t ctx;

void setUp(void)    { parser_init(&ctx); }
void tearDown(void) { }

void test_parser_accepts_valid_frame(void) {
    /* SOF=0xAA, LEN=0x02, DATA=0x01 0x02, CRC=0x03C1 */
    uint8_t frame[] = {0xAA, 0x02, 0x01, 0x02, 0x03, 0xC1};
    for (size_t i = 0; i < sizeof(frame); i++) {
        parser_feed(&ctx, frame[i]);
    }
    TEST_ASSERT_EQUAL(PARSER_STATE_COMPLETE, ctx.state);
    TEST_ASSERT_EQUAL_UINT8(0x01, ctx.payload[0]);
    TEST_ASSERT_EQUAL_UINT8(0x02, ctx.payload[1]);
}

void test_parser_rejects_frame_with_bad_crc(void) {
    uint8_t frame[] = {0xAA, 0x02, 0x01, 0x02, 0xFF, 0xFF}; /* bad CRC */
    for (size_t i = 0; i < sizeof(frame); i++) {
        parser_feed(&ctx, frame[i]);
    }
    TEST_ASSERT_EQUAL(PARSER_STATE_ERROR, ctx.state);
}

void test_parser_resets_on_unexpected_sof(void) {
    /* Mid-frame, inject a new SOF to simulate a framing error */
    parser_feed(&ctx, 0xAA);  /* partial frame */
    parser_feed(&ctx, 0x01);
    parser_feed(&ctx, 0xAA);  /* new SOF mid-frame */
    TEST_ASSERT_EQUAL(PARSER_STATE_SOF, ctx.state);
}
```

---

## Example 4: Static analysis with cppcheck in CI

**Makefile target:**

```makefile
analyze:
	cppcheck --enable=all --inconclusive --std=c11 \
	         --error-exitcode=1 \
	         --suppress=missingIncludeSystem \
	         -I src/ src/ 2>&1 | tee reports/cppcheck.txt
```

**CMake integration:**

```cmake
find_program(CPPCHECK cppcheck)
if(CPPCHECK)
    add_custom_target(static_analysis
        COMMAND ${CPPCHECK}
            --enable=all --inconclusive --std=c11
            --error-exitcode=1
            --suppress=missingIncludeSystem
            -I ${CMAKE_SOURCE_DIR}/src
            ${CMAKE_SOURCE_DIR}/src
        COMMENT "Running cppcheck static analysis"
    )
endif()
```

Run before every PR merge:

```bash
cmake --build build --target static_analysis
```
