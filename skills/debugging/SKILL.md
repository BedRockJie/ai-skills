# Skill: Embedded Debugging

## Purpose

Guide AI agents through systematic, hardware-aware debugging of embedded
firmware — from reproducing the fault to root-cause analysis using JTAG/SWD,
UART logging, hard-fault handlers, and logic analyzers.

## When to use

Use this skill when:

- A firmware crash, hard fault, or watchdog reset has occurred
- A peripheral (SPI, I2C, CAN, ADC) behaves unexpectedly or produces wrong data
- A real-time task misses its deadline or an interrupt fails to fire
- A regression appears after a code or hardware change
- Performance or power consumption deviates from specification

## Instructions

### 1. Reproduce the issue and gather evidence

Before touching any code or registers:

- Record the **exact conditions** – firmware version, hardware revision, supply
  voltage, temperature, and sequence of events leading to the fault.
- Capture any available diagnostic output: UART log, semihosting output,
  ITM/SWO trace, LED blink patterns.
- If a hard fault occurred, extract the fault registers immediately
  (see step 3); they are lost on reset unless saved to non-volatile memory.

### 2. Connect a debug probe and inspect state

Set up an OpenOCD + GDB session (or vendor IDE equivalent):

```bash
# Terminal 1 – start OpenOCD with your target config
openocd -f interface/stlink.cfg -f target/stm32h7x.cfg

# Terminal 2 – connect GDB to OpenOCD
arm-none-eabi-gdb build/firmware.elf
(gdb) target remote :3333
(gdb) monitor reset halt
(gdb) load                   # flash the firmware
(gdb) break main
(gdb) continue
```

Useful GDB commands for embedded:

```gdb
info registers              # dump all CPU registers including PC, SP, LR
x/16xw 0x20000000           # hex dump 16 words from SRAM start
p/x USART1->SR              # print peripheral register value (CMSIS struct)
backtrace                   # call stack (may be unwound on Cortex-M with -funwind-tables)
monitor reset halt          # hard reset + halt without reflashing
```

### 3. Analyse a Cortex-M hard fault

A `HardFault_Handler` that dumps the stacked frame is essential for every
Cortex-M project:

```c
/* Place in fault_handler.c */
void HardFault_Handler(void) {
    /* Read the stacked PC from the exception frame */
    volatile uint32_t *sp = (volatile uint32_t *)__get_MSP();
    volatile uint32_t stacked_pc = sp[6];  /* offset 6 in basic frame */
    volatile uint32_t cfsr = SCB->CFSR;    /* Configurable Fault Status */
    volatile uint32_t mmfar = SCB->MMFAR;  /* MemManage Fault Address */
    volatile uint32_t bfar  = SCB->BFAR;   /* Bus Fault Address */
    (void)stacked_pc; (void)cfsr; (void)mmfar; (void)bfar;
    __BKPT(0); /* Break here in GDB; inspect variables above */
    while (1) {}
}
```

Decode `SCB->CFSR` bits to identify the fault type:

| CFSR bit | Fault | Common cause |
|---|---|---|
| IBUSERR | Instruction bus error | Branch to invalid address / bad function pointer |
| PRECISERR | Precise data bus error | Access to non-existent peripheral address |
| STKERR | Stack error | Stack overflow – SP below stack limit |
| UNDEFINSTR | Undefined instruction | Thumb/ARM mode mismatch or corrupted PC |
| NOCP | No co-processor | FPU instruction when FPU not enabled (CPACR) |

### 4. Debug peripheral issues with UART logging

When a JTAG probe is unavailable or halting the CPU disturbs timing:

```c
/* Lightweight debug UART – polling, no DMA, no RTOS */
#define DBG_UART  USART2

void dbg_print(const char *msg) {
    while (*msg) {
        while (!(DBG_UART->SR & USART_SR_TXE)) {}
        DBG_UART->DR = (uint8_t)*msg++;
    }
}

/* Usage */
dbg_print("[INIT] SPI2 configured\r\n");
```

- Use a dedicated low-priority UART that is never shared with application data.
- Prefix messages with a timestamp or tick count for timing analysis.
- Remove or `#ifdef DEBUG` guard all debug prints before production builds.

### 5. Use a logic analyzer for hardware-software interface issues

When the peripheral register values look correct but hardware still misbehaves:

1. Attach a logic analyzer to the suspect bus (SPI CLK/MOSI/MISO/CS,
   I2C SDA/SCL, UART TX/RX, CAN H/L).
2. Decode the protocol in the capture tool and compare byte-by-byte against
   the datasheet timing diagrams.
3. Check:
   - CS de-assert timing between transactions
   - Clock polarity / phase (CPOL/CPHA) matching the peripheral device
   - I2C address byte (7-bit vs 10-bit, read vs write bit)
   - Pull-up resistor value adequate for bus speed

### 6. Narrow the scope with git bisect

For regressions where the bad commit is unknown:

```bash
git bisect start
git bisect bad                     # current HEAD is broken
git bisect good v2.3.0             # last known-good release tag
# Git checks out a midpoint commit; flash it and test
git bisect good                    # or: git bisect bad
# Repeat until Git prints: "abc1234 is the first bad commit"
git bisect reset
```

### 7. Fix and verify

- Make the **smallest** possible change that addresses the root cause.
- Re-flash and reproduce the original test scenario — not just a superficial
  smoke test.
- Run the full build with `-Wall -Wextra` and address any new warnings.
- Verify watchdog still refreshes correctly after the fix.

### 8. Document the fix

Leave a commit message and inline comment explaining:

- What the fault was (fault type, register values, corrupted address)
- Why it happened (root cause)
- How the fix addresses it

```
fix(spi): add timeout to TX-complete poll loop

SCB->CFSR showed PRECISERR with BFAR=0x40013000 (USART1 status reg).
The ISR was calling the SPI wait function from within a higher-priority
ISR context, causing nested SPI access before the bus was idle.
Added a 1000-tick timeout and moved the wait to task context.
Closes #87
```

## Examples

See [examples.md](examples.md).

## References

- [ARM Cortex-M Fault Exceptions (Application Note AN209)](https://developer.arm.com/documentation/kan209/latest/)
- [OpenOCD User Guide](https://openocd.org/doc/html/index.html)
- [GDB User Manual](https://sourceware.org/gdb/current/onlinedocs/gdb/)
- [Debugging Embedded Systems – J. Labrosse (embedded.com)](https://www.embedded.com/)
