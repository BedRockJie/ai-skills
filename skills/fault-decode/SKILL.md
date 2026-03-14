# Skill: Cortex-M Fault Decode

## Purpose

Run `decode_cortexm_fault.py` against SCB fault register values captured from a
live or post-mortem Cortex-M fault, then translate the decoded output into a
root-cause statement and a minimum fix.

## When to use

Use this skill when:

- A Cortex-M target has entered `HardFault_Handler`, `MemManage_Handler`,
  `BusFault_Handler`, or `UsageFault_Handler`
- A firmware image resets unexpectedly with no UART output
- An RTOS task crashes and `configCHECK_FOR_STACK_OVERFLOW` fires
- You have raw register values from a debugger and need a diagnosis

## Inputs

You need at least the CFSR value.  Collect the others whenever available:

| Register | Address    | GDB command        | Contains |
|----------|------------|--------------------|---------|
| CFSR     | 0xE000ED28 | `p/x SCB->CFSR`   | MemManage + BusFault + UsageFault bits |
| HFSR     | 0xE000ED2C | `p/x SCB->HFSR`   | HardFault cause (forced vs. debug) |
| MMFAR    | 0xE000ED34 | `p/x SCB->MMFAR`  | Faulting address for MemManage faults |
| BFAR     | 0xE000ED38 | `p/x SCB->BFAR`   | Faulting address for Bus faults |

**Capture registers before any reset.** They are lost when the MCU reboots
unless your `HardFault_Handler` saves them to non-volatile memory or via
semihosting.

Minimal fault handler that preserves the values:

```c
void HardFault_Handler(void) {
    volatile uint32_t cfsr  = SCB->CFSR;
    volatile uint32_t hfsr  = SCB->HFSR;
    volatile uint32_t mmfar = SCB->MMFAR;
    volatile uint32_t bfar  = SCB->BFAR;
    (void)cfsr; (void)hfsr; (void)mmfar; (void)bfar;
    __BKPT(0);  /* GDB breaks here; inspect the four variables above */
    while (1) {}
}
```

## Instructions

### 1. Run the decode script

```bash
python3 skills/fault-decode/decode_cortexm_fault.py \
    --cfsr  0x<CFSR_VALUE>  \
    --hfsr  0x<HFSR_VALUE>  \
    --mmfar 0x<MMFAR_VALUE> \
    --bfar  0x<BFAR_VALUE>
```

Omit `--hfsr`, `--mmfar`, `--bfar` if those values were not captured.

### 2. Read the script output and form a diagnosis

The script prints one entry per active fault bit, each with:

- **Meaning** — what hardware event occurred
- **Fix hint** — the standard corrective action for that fault type

Translate the output into a one-sentence root-cause statement:

```
Root cause: [fault bit] at address [BFAR/MMFAR if present] — [what the
code was doing at the stacked PC].
```

### 3. Locate the faulting source line

```bash
# Read the stacked PC from GDB (basic frame offset 6)
(gdb) p/x ((uint32_t *)__get_MSP())[6]

# Resolve to file and line
arm-none-eabi-addr2line -e build/firmware.elf 0x<stacked_pc>
```

If the stacked PC points into a library or the vector table, the fault was
likely triggered by a corrupt function pointer or a stack overflow that
overwrote the return address.

### 4. Apply the fix

Use the fix hint from the script output.  Common patterns:

| Fault bit   | Typical fix |
|-------------|-------------|
| NOCP        | Add `SCB->CPACR \|= (0xF << 20);` before any FP instruction |
| DIVBYZERO   | Guard the divisor: `if (divisor == 0) { return ERROR; }` |
| PRECISERR   | Check the address in `--bfar`; add clock-enable or null-check |
| STKERR      | Increase stack size; add `configCHECK_FOR_STACK_OVERFLOW=2` |
| INVSTATE    | Ensure function-pointer values have bit 0 set (Thumb bit) |
| DACCVIOL    | Null-pointer or MPU region violation; validate pointer before use |

### 5. Write the fix commit

Use the conventional-commits skill:

```
fix(<module>): <one-line description of what was wrong>

SCB->CFSR=0x<VALUE> [FAULTBIT]: <meaning>.
Stacked PC 0x<ADDR> → <file>:<line>.
Fix: <what was changed>.
Closes #<issue>
```

## Examples

```bash
# Scenario: target resets after calling a new sensor driver
# GDB output: SCB->CFSR = 0x00000002, CFSR bit 1 = DACCVIOL
python3 skills/fault-decode/decode_cortexm_fault.py --cfsr 0x00000002 --mmfar 0x00000000

# Scenario: FPU instruction crash at startup
# Symptom: NOCP — FPU not enabled
python3 skills/fault-decode/decode_cortexm_fault.py --cfsr 0x00080000

# Scenario: stack overflow in motor-control ISR
# CFSR STKERR set, HFSR FORCED set
python3 skills/fault-decode/decode_cortexm_fault.py \
    --cfsr 0x00001000 --hfsr 0x40000000
```

## References

- [ARM Cortex-M Fault Exceptions — Application Note AN209](https://developer.arm.com/documentation/kan209/latest/)
- [ARM Cortex-M3/M4 Generic User Guide — SCB registers](https://developer.arm.com/documentation/dui0552/latest/)
- [OpenOCD User Guide](https://openocd.org/doc/html/index.html)
