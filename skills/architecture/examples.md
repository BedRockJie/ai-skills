# Embedded Firmware Architecture – Examples

## Example 1: Cortex-M4 bare-metal sensor node

**Platform:** STM32L476 (Cortex-M4 @ 80 MHz, 128 KB SRAM, 1 MB Flash)

**Requirements:**
- Read an accelerometer over SPI at 1 kHz
- Aggregate samples and transmit over UART every 100 ms
- Sleep between samples (LP sleep mode, < 10 µA average)

**Execution model decision:** Bare-metal + ISR (2 concerns, no blocking I/O needed)

**Layer breakdown:**

```
Application: sample_accumulator.c  – ring buffer, UART framer
HAL:         spi_driver.c          – DMA-driven SPI, ISR completion callback
             uart_driver.c         – TX-only, DMA, non-blocking
BSP:         stm32l4xx_init.c      – clock (HSI16, PLL to 80 MHz), pin mux
             startup_stm32l476.s   – vector table, stack pointer
```

**Memory layout (sketch):**

```
Flash 0x08000000  vector table + BSP init + application  (~48 KB)
SRAM  0x20000000  .data + .bss                           (~4 KB)
      0x20008000  sample ring buffer (static, 4 KB)
      0x2001E000  main stack                             (8 KB, grows down)
```

**Key decisions:**
- DMA for SPI and UART frees the CPU during transfers
- `volatile` on the DMA-complete flag shared between ISR and main loop
- Watchdog (IWDG) refreshed in the main loop; never inside the ISR

---

## Example 2: Dual-core AMP on i.MX 8M Plus

**Platform:** i.MX 8M Plus (Cortex-A53 quad @ 1.8 GHz + Cortex-M7 @ 800 MHz)

**Requirements:**
- Linux on A53: camera pipeline, network stack, OTA update agent
- Real-time motor control on M7: FOC loop at 20 kHz, CAN telemetry

**Architecture decision: AMP (Asymmetric Multi-Processing)**

```
Cortex-A53 (Linux 6.x)           Cortex-M7 (FreeRTOS, static alloc only)
─────────────────────────         ──────────────────────────────────────
  OTA update daemon                 FOC ISR (20 kHz, DTCM-resident)
  Camera / ISP pipeline             CAN receive task  (500 kbps)
  Remote Proc Framework (RPMsg)     Telemetry task    (100 Hz)
                   ↕  shared SRAM mailbox (RPMsg)  ↕
```

**ADR excerpt:**

```markdown
# ADR-002: Run motor control on M7 co-processor

## Decision
Isolate the 20 kHz FOC loop on the M7 to guarantee < 5 µs jitter
independent of Linux scheduler activity on the A53 cluster.

## Consequences
+ Deterministic real-time performance unaffected by Linux load
+ M7 can continue operating if the A53 crashes (limp-home mode)
- IPC via RPMsg adds ~2 µs latency for non-critical commands
```

---

## Example 3: RTOS task priority assignment (FreeRTOS)

**Scenario:** Industrial gateway with Ethernet, Modbus RTU, and local UI.

```c
/* Priority definitions — higher number = higher priority in FreeRTOS */
#define PRIO_MODBUS_RX    5   /* Soft real-time: 10 ms deadline      */
#define PRIO_ETHERNET_TX  4   /* Background comms: throughput matters */
#define PRIO_UI_UPDATE    2   /* Human-perceptible: 100 ms is fine    */
#define PRIO_IDLE         0   /* FreeRTOS idle task                   */

/* Static task creation — no heap required */
static StaticTask_t modbus_tcb;
static StackType_t  modbus_stack[512];

void app_start(void) {
    xTaskCreateStatic(modbus_rx_task, "ModbusRX",
                      512, NULL, PRIO_MODBUS_RX,
                      modbus_stack, &modbus_tcb);
    /* ... other tasks ... */
    vTaskStartScheduler();
}
```

**Why static allocation?**
- Eliminates heap fragmentation and malloc failure modes
- Stack sizes are fixed at compile time — easier to audit
- Required for MISRA-C Rule 21.3 compliance (no dynamic memory after init)
