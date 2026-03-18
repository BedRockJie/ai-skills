---
name: fault-decode
description: Decode Cortex-M fault registers into a concise diagnosis and next steps.
license: MIT
---

# Skill: Cortex-M Fault Decode

## Purpose

Decode Cortex-M fault registers and turn them into a short diagnosis and next
step.

## When to use

Use this skill when:

- A Cortex-M target enters a fault handler
- The target resets before normal logs appear
- You captured `CFSR`, `HFSR`, `MMFAR`, or `BFAR`
- You need a fast first diagnosis from raw register values

## Inputs

Collect at least `CFSR`. Collect the others when available:

| Register | GDB command |
|----------|-------------|
| CFSR | `p/x SCB->CFSR` |
| HFSR | `p/x SCB->HFSR` |
| MMFAR | `p/x SCB->MMFAR` |
| BFAR | `p/x SCB->BFAR` |

Capture them before reset.

## Instructions

### 1. Run the decoder

```bash
python3 skills/fault-decode/decode_cortexm_fault.py \
    --cfsr 0x<CFSR> \
    --hfsr 0x<HFSR> \
    --mmfar 0x<MMFAR> \
    --bfar 0x<BFAR>
```

### 2. Read the output

The script prints:

- active fault bits
- a short meaning
- a short fix hint
- fault addresses when available

### 3. Resolve the source line

```bash
arm-none-eabi-addr2line -e build/firmware.elf 0x<stacked_pc>
```

### 4. Write the diagnosis

Use this format:

```text
Fault: <fault bit>
Location: <address> or <file>:<line>
Cause: <what likely happened>
Fix: <next change to try>
```

### 5. Apply the smallest fix

Fix the likely cause first. Then reproduce the original failure.

## Examples

```bash
python3 skills/fault-decode/decode_cortexm_fault.py --cfsr 0x00000002 --mmfar 0x00000000
python3 skills/fault-decode/decode_cortexm_fault.py --cfsr 0x00080000
python3 skills/fault-decode/decode_cortexm_fault.py --cfsr 0x00001000 --hfsr 0x40000000
```

## References

- [ARM Cortex-M Fault Exceptions — Application Note AN209](https://developer.arm.com/documentation/kan209/latest/)
- [ARM Cortex-M3/M4 Generic User Guide — SCB registers](https://developer.arm.com/documentation/dui0552/latest/)
- [OpenOCD User Guide](https://openocd.org/doc/html/index.html)
