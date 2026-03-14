# Embedded Debugging – Examples

## Example 1: Diagnosing a Cortex-M HardFault (stack overflow)

**Symptom:** MCU hard-resets repeatedly ~200 ms after boot; no UART output after
initialisation.

**Steps:**

1. Add a minimal hard-fault handler that saves context before the reset:

```c
void HardFault_Handler(void) {
    volatile uint32_t cfsr  = SCB->CFSR;
    volatile uint32_t hfsr  = SCB->HFSR;
    volatile uint32_t *sp   = (volatile uint32_t *)__get_MSP();
    volatile uint32_t stacked_pc = sp[6];
    (void)cfsr; (void)hfsr; (void)stacked_pc;
    __BKPT(0);  /* Halt here when GDB is attached */
    while (1) {}
}
```

2. Attach GDB, reproduce the fault, halt at the breakpoint:

```gdb
(gdb) p/x cfsr
$1 = 0x00000200     /* CFSR bit 9 = STKERR: stacking error */
(gdb) p/x stacked_pc
$2 = 0x08003f2c
(gdb) info line *0x08003f2c
Line 47 of "src/sensor_task.c"
```

3. `STKERR` + stacked PC in `sensor_task.c:47` points to a stack overflow in
   the sensor task. Check task stack size:

```c
/* Before fix: too small for the FFT + local arrays */
#define SENSOR_TASK_STACK  128   /* words — WAY too small */

/* After fix */
#define SENSOR_TASK_STACK  512   /* words — verified with uxTaskGetStackHighWaterMark */
```

4. Enable FreeRTOS stack-overflow checking during development:

```c
/* FreeRTOSConfig.h */
#define configCHECK_FOR_STACK_OVERFLOW  2
```

---

## Example 2: SPI peripheral produces no clock output

**Symptom:** SPI2 MOSI stays low, no CLK pulses visible on oscilloscope.

**Steps:**

1. Check that the peripheral clock is enabled:

```gdb
(gdb) p/x RCC->APB1ENR
$1 = 0x00000000   /* SPI2EN bit (14) is 0 — clock NOT enabled! */
```

2. The root cause: `spi2_init()` accesses SPI2->CR1 before enabling the bus clock.
   Fix — add clock enable as the first line:

```c
void spi2_init(void) {
    RCC->APB1ENR |= RCC_APB1ENR_SPI2EN;   /* Enable SPI2 clock first */
    /* Small delay to let the clock propagate (see errata) */
    (void)RCC->APB1ENR;

    SPI2->CR1 = SPI_CR1_MSTR | SPI_CR1_BR_2 | SPI_CR1_SPE;
}
```

3. Re-attach logic analyser — SCK, MOSI, CS now show correct transactions.

---

## Example 3: Intermittent I2C NACK — logic analyser catches it

**Symptom:** I2C sensor read returns `HAL_ERROR` roughly 1 in 50 transactions.

**Steps:**

1. Attach logic analyser to SDA and SCL, decode I2C at 400 kHz.
2. Capture ~100 transactions. Find the failing one:
   - Address byte `0x4C` (write) — ACK ✓
   - Register byte `0x00` — ACK ✓
   - Repeated Start — *missing* — bus releases to idle instead
3. Hypothesis: CS de-assertion (repeated start) is skipped when another task
   pre-empts between the address write and the register read phases.
4. Fix: wrap the two-phase transaction in a mutex to make it atomic from the
   scheduler's perspective:

```c
xSemaphoreTake(i2c_mutex, portMAX_DELAY);
HAL_I2C_Master_Transmit(&hi2c1, addr_write, &reg, 1, 10);
HAL_I2C_Master_Receive(&hi2c1,  addr_read,  buf,  2, 10);
xSemaphoreGive(i2c_mutex);
```

---

## Example 4: Using `git bisect` to find a timing regression

**Symptom:** CAN telemetry frame rate drops from 100 Hz to ~60 Hz after a recent
merge. The regression was not caught in review.

**Steps:**

```bash
git bisect start
git bisect bad                     # current HEAD – 60 Hz (bad)
git bisect good v3.1.0             # last release – 100 Hz (good)

# Git checks out the midpoint; flash and measure frame rate
git bisect bad                     # still 60 Hz

# ... repeat ~8 times ...

# Git reports:
# 7d3a1c4 is the first bad commit
# Author: dev@example.com
# Date:   Mon Mar 10 09:14:22 2026
#     feat(uart): increase UART TX DMA buffer to 4 KB

git bisect reset
```

**Root cause:** The larger UART DMA buffer raised the DMA transfer completion
interrupt priority above the CAN Tx interrupt, starving it. Fix: lower the
UART DMA IRQ priority below the CAN Tx IRQ in the NVIC configuration.

