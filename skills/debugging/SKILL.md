# Skill: Target Debugging

## Purpose

Follow a structured debug flow for target-side failures. Collect evidence, form a
 root-cause statement, and verify the smallest fix.

## When to use

Use this skill when:

- A target crashes or resets
- A device or bus behaves incorrectly
- A timing or scheduling regression appears
- A recent change introduced a hard-to-reproduce failure

## Inputs

Collect what you already have:

| Item | Example |
|------|---------|
| Logs | serial log, service log, crash log |
| Register dump | debugger output before reset |
| Fault address | stacked PC or faulting address |
| Last known-good version | tag or commit |
| Trace or capture | logic analyzer, scope, or bus trace |

## Instructions

### 1. Connect and halt

Use the debugger or probe for your target. Stop execution close to the failure.

Example:

```bash
openocd -f interface/stlink.cfg -f target/stm32h7x.cfg
arm-none-eabi-gdb build/firmware.elf
```

Useful GDB commands:

```gdb
info registers
backtrace
p/x SCB->CFSR
monitor reset halt
```

### 2. Classify the failure

Start with the simplest label:

- crash
- reset
- bad data
- timeout
- race
- regression

### 3. Decode the fault when needed

If fault registers are available, run the fault-decode skill:

```bash
python3 skills/fault-decode/decode_cortexm_fault.py --cfsr 0x<CFSR>
```

Then resolve the faulting line:

```bash
arm-none-eabi-addr2line -e build/firmware.elf 0x<stacked_pc>
```

### 4. Capture more evidence

Use the least intrusive tool that still answers the question:

- logs for control flow
- debugger for state
- logic analyzer for bus activity
- `git bisect` for regressions

### 5. Write the hypothesis

Write one short statement before editing code:

```text
Fault: <type>
Location: <file>:<line> or <address>
Cause: <why it happened>
Fix: <smallest useful change>
```

### 6. Apply the fix and verify

- Make the smallest change first
- Reproduce the original failure
- Rebuild with warnings enabled
- Confirm the failure is gone
- Check for nearby regressions

## Examples

See [examples.md](examples.md).

## References

- [OpenOCD User Guide](https://openocd.org/doc/html/index.html)
- [GDB User Manual](https://sourceware.org/gdb/current/onlinedocs/gdb/)
- [ARM Cortex-M Fault Exceptions — Application Note AN209](https://developer.arm.com/documentation/kan209/latest/)
