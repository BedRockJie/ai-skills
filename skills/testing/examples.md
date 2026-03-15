# C Unit Testing - Examples

## Example 1: CRC-8 module

**Directory layout:**

```text
src/
  crc8.c
  crc8.h
test/
  test_crc8.c
  test_utils.h
```

**test/test_crc8.c:**

```c
#include "test_utils.h"
#include "../src/crc8.h"

static void test_crc8_empty_returns_zero(void) {
    TEST_ASSERT(crc8_compute(NULL, 0) == 0x00, "empty data should return 0x00");
}

static void test_crc8_known_vector(void) {
    const uint8_t data[] = {0x31, 0x32, 0x33};
    TEST_ASSERT_EQ(0xC0, crc8_compute(data, sizeof(data)), "crc8 vector should match");
}

int main(void) {
    RUN_TESTS(
        test_crc8_empty_returns_zero,
        test_crc8_known_vector,
    );
}
```

**Run:**

```bash
python3 skills/testing/test_runner.py test/ src/
```

---

## Example 2: Platform stub in tests

**src/uart.c:**

```c
#include "uart.h"

#ifdef UNIT_TEST
static uint8_t _tx_buf[256];
static size_t _tx_len;

void uart_stub_reset(void) { _tx_len = 0; }
size_t uart_stub_sent_count(void) { return _tx_len; }
uint8_t uart_stub_sent_byte(size_t i) { return _tx_buf[i]; }

void uart_send_byte(uint8_t b) { _tx_buf[_tx_len++] = b; }
#else
void uart_send_byte(uint8_t b) { platform_uart_write(b); }
#endif
```

**test/test_uart.c:**

```c
#include "test_utils.h"
#include "../src/uart.h"

static void test_uart_send_byte_stores_value(void) {
    uart_stub_reset();
    uart_send_byte(0x42);
    TEST_ASSERT_EQ(1, uart_stub_sent_count(), "one byte should be recorded");
    TEST_ASSERT_EQ(0x42, uart_stub_sent_byte(0), "byte should match");
}

int main(void) {
    RUN_TESTS(
        test_uart_send_byte_stores_value,
    );
}
```

**Run:**

```bash
CFLAGS="-DUNIT_TEST" python3 skills/testing/test_runner.py test/ src/
```

---

## Example 3: Self-contained parser test

```c
#include "test_utils.h"

typedef enum { IDLE, IN_FRAME, DONE } parser_state_t;
static parser_state_t _state = IDLE;

static void parser_reset(void) { _state = IDLE; }

static parser_state_t parser_feed(uint8_t b) {
    switch (_state) {
    case IDLE: if (b == 0xAA) _state = IN_FRAME; break;
    case IN_FRAME: if (b == 0x55) _state = DONE; break;
    default: break;
    }
    return _state;
}

static void test_parser_idle_on_reset(void) {
    parser_reset();
    TEST_ASSERT(_state == IDLE, "state should be IDLE after reset");
}

static void test_parser_transitions_to_done(void) {
    parser_reset();
    parser_feed(0xAA);
    parser_feed(0x55);
    TEST_ASSERT(_state == DONE, "should reach DONE after 0xAA then 0x55");
}

int main(void) {
    RUN_TESTS(
        test_parser_idle_on_reset,
        test_parser_transitions_to_done,
    );
}
```
