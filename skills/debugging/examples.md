# Target Debugging - Examples

## Example 1: Stack fault on startup

**Symptom:** The target resets soon after boot.

**Steps:**

1. Capture fault state in the handler.
2. Read `CFSR` and the stacked PC in GDB.
3. Resolve the PC to a source line.
4. Increase stack size or remove large local buffers.

```gdb
(gdb) p/x cfsr
$1 = 0x00000200
(gdb) p/x stacked_pc
$2 = 0x08003f2c
```

---

## Example 2: Peripheral stays silent

**Symptom:** No clock or data on the bus.

**Steps:**

1. Check the clock-enable state.
2. Check init order.
3. Re-test with a logic analyzer.

```c
void spi2_init(void) {
    RCC->APB1ENR |= RCC_APB1ENR_SPI2EN;
    (void)RCC->APB1ENR;
    SPI2->CR1 = SPI_CR1_MSTR | SPI_CR1_BR_2 | SPI_CR1_SPE;
}
```

---

## Example 3: Timing regression

**Symptom:** Throughput drops after a recent merge.

**Steps:**

```bash
git bisect start
git bisect bad
git bisect good v3.1.0
```

Use each midpoint to reproduce the issue. Stop when Git identifies the first bad commit.
