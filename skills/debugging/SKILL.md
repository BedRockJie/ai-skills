# Skill: Embedded Firmware Debugger

## Purpose

Execute a structured, evidence-first debugging procedure for embedded firmware
faults — from capturing diagnostic data to forming a root-cause hypothesis and
a minimum fix.

## When to use

Use this skill when:

- A firmware crash, hard fault, or watchdog reset has occurred
- A peripheral produces wrong data or fails to respond
- An RTOS task misses its deadline or an interrupt does not fire
- A regression appears after a code or hardware change

## Inputs

Start by collecting what is already available:

| Item | How to get it |
|------|---------------|
| Fault register dump | GDB `p/x SCB->CFSR` before reset, or saved by fault handler |
| UART log | Serial terminal output up to the crash |
| Stacked PC | GDB `p/x ((uint32_t *)__get_MSP())[6]` |
| Last known-good tag | `git log --oneline --tags` |
| Logic analyzer capture | Attach to the suspect bus before reproducing |

## Instructions

### 1. Connect the debug probe and halt

```bash
# Terminal 1 — start OpenOCD
openocd -f interface/stlink.cfg -f target/stm32h7x.cfg

# Terminal 2 — connect GDB
arm-none-eabi-gdb build/firmware.elf
(gdb) target remote :3333
(gdb) monitor reset halt
(gdb) load
(gdb) break main
(gdb) continue
```

Key GDB commands:

```gdb
info registers              # CPU registers: PC, SP, LR, xPSR
x/16xw 0x20000000           # hex dump SRAM start (check for corruption)
p/x SCB->CFSR               # fault status — capture BEFORE reset
backtrace                   # call stack (requires -funwind-tables in build)
monitor reset halt          # hard reset + halt without reflashing
```

### 2. Classify the fault

| Symptom | First action |
|---------|-------------|
| Execution in HardFault_Handler | Go to step 3 (fault decode) |
| WDT reset, no fault handler reached | Check for infinite loop or priority starvation |
| Peripheral returns 0xFFFFFFFF | Clock not enabled — add `RCC->APBxENR \|= ...` |
| RTOS task never runs | Priority too low, or blocking call in a higher-priority task |
| Wrong data on bus | Go to step 4 (logic analyzer) |
| Regression after recent commit | Go to step 5 (git bisect) |

### 3. Decode a hard fault

Run the fault-decode skill:

```bash
python3 skills/fault-decode/decode_cortexm_fault.py \
    --cfsr  0x<CFSR>  \
    --hfsr  0x<HFSR>  \
    --mmfar 0x<MMFAR> \
    --bfar  0x<BFAR>
```

Then resolve the faulting source line:

```bash
arm-none-eabi-addr2line -e build/firmware.elf 0x<stacked_pc>
```

### 4. Debug a peripheral with UART polling log

When halting the CPU disturbs timing, use a dedicated polling UART:

```c
#define DBG_UART USART2

static void dbg_print(const char *msg) {
    while (*msg) {
        while (!(DBG_UART->SR & USART_SR_TXE)) {}
        DBG_UART->DR = (uint8_t)*msg++;
    }
}

/* Usage */
dbg_print("[SPI] CS assert\r\n");
```

Add a tick counter prefix (`dbg_printf("[%lu] ...", HAL_GetTick())`) for
timing analysis.  Guard all debug prints with `#ifdef DEBUG`.

For hardware-protocol issues, attach a logic analyzer to the suspect bus
and decode the capture byte-by-byte against the device datasheet.

### 5. Narrow a regression with git bisect

```bash
git bisect start
git bisect bad                   # current HEAD is broken
git bisect good v<last-good-tag> # last confirmed-working release
# Git checks out a midpoint commit; flash it and test
git bisect good                  # or: git bisect bad
# Repeat — Git prints "abc1234 is the first bad commit" when done
git bisect reset
```

### 6. Form and record the hypothesis

Write one statement before touching any code:

```
Fault: [fault type, register values]
Stacked PC: 0x<ADDR> → <file>:<line>
Root cause: <why this code path was reached>
Fix: <minimum change that addresses the root cause>
```

Do not modify any code until this statement is written.

### 7. Apply the fix and verify

- Make the smallest possible change.
- Re-flash and reproduce the original fault scenario — not a smoke test.
- Build with `-Wall -Wextra`; address any new warnings.
- Confirm WDT still refreshes after the fix.

Write the fix commit using the conventional-commits skill:

```
fix(<module>): <description>

SCB->CFSR=0x<VALUE>: <fault type>.
Stacked PC 0x<ADDR> → <file>:<line>.
Root cause: <one sentence>.
Closes #<issue>
```

## Examples

See [examples.md](examples.md).

## References

- [ARM Cortex-M Fault Exceptions — Application Note AN209](https://developer.arm.com/documentation/kan209/latest/)
- [OpenOCD User Guide](https://openocd.org/doc/html/index.html)
- [GDB User Manual](https://sourceware.org/gdb/current/onlinedocs/gdb/)
