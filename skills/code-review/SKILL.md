# Skill: Embedded C Code Review

## Purpose

Execute a systematic, ordered checklist against a C firmware diff and produce a
formatted list of findings — each tagged as `nit:`, `suggestion:`, `question:`,
or `blocker:` — ready to post as review comments.

## When to use

Use this skill when:

- Reviewing a pull request or patch for MCU / SoC firmware
- Self-reviewing before requesting a peer review
- Auditing a driver or HAL module for common embedded defects

## Inputs

- The diff or file(s) to review
- MCU family (to interpret register names and peripheral sequences)
- RTOS in use, if any (FreeRTOS, Zephyr, bare-metal)

## Instructions

Work through the checks **in order**.  For each finding emit one comment block
in the format shown at the end of this section.  Stop and emit a `blocker:` as
soon as one is found — do not defer blockers to later checks.

### 1. Scan for missing `volatile` on MMIO and ISR-shared variables

For every struct that maps to a hardware register address, verify:

```c
/* Required */
volatile uint32_t * const SR = (volatile uint32_t *)0x40013000;

/* Flag this — compiler may cache the read at -O2 */
uint32_t * const SR = (uint32_t *)0x40013000;
```

Also flag any variable written in an ISR and read in task context (or vice
versa) that lacks `volatile` or an atomic/critical-section guard.

Emit: `blocker: [file:line] missing volatile — compiler may eliminate …`

### 2. Check W1C register access

Read-modify-write on a status register with write-1-to-clear bits silently
clears other pending flags.  Pattern to flag:

```c
/* Dangerous — clears all W1C bits in the status register */
USART1->SR &= ~USART_SR_ORE;

/* Correct — touch only the target bit */
USART1->SR = USART_SR_ORE;
```

Emit: `blocker: [file:line] RMW on W1C register clears unrelated flag bits`

### 3. Check ISR safety

For each ISR function (identified by NVIC registration or `__attribute__((interrupt))`):

- Flag any call to a blocking API: `printf`, `malloc`, `vTaskDelay`,
  `xQueueSend` (non-ISR variant), `HAL_Delay`, `osDelay`.
- Flag direct RTOS queue/semaphore operations — require `FromISR` variants.
- Flag large local arrays (>= 64 bytes) — each ISR has its own stack frame.

Emit: `blocker: [file:line] blocking call inside ISR — use xQueueSendFromISR`

### 4. Check memory safety

- Flag `strcpy`, `sprintf`, `gets`, `memcpy` without bounded equivalents.
- Flag `malloc`/`free` in bare-metal or MISRA-scoped code unless approved.
- Flag signed/unsigned mismatch in array index arithmetic.

Emit: `blocker: [file:line] unbounded copy — use strncpy(dst, src, sizeof(dst)-1)`

### 5. Check peripheral driver sequence

- Clock-enable call must appear **before** any register access for that
  peripheral (`RCC->APB1ENR |= ...` on STM32; equivalent on other families).
- Configuration registers must be written before the peripheral-enable bit.
- Poll loops must have a timeout:

```c
/* Flag — no timeout */
while (!(USART1->SR & USART_SR_TC)) {}

/* Required */
uint32_t t = 1000;
while (!(USART1->SR & USART_SR_TC) && t--) {}
if (t == 0) { return ERR_TIMEOUT; }
```

Emit: `blocker: [file:line] clock enable missing before peripheral access`
Emit: `blocker: [file:line] unbounded poll — add timeout counter`

### 6. Check RTOS usage

- Task stack sizes: flag if the task's call depth + local variable totals could
  exceed the configured stack words.
- Priority assignment: flag if a higher-priority task performs more work than
  a lower-priority one (likely inversion).
- DMA buffers: flag any buffer in DTCM/CCM when the DMA controller cannot
  reach that memory region.

Emit: `suggestion: [file:line] DMA buffer in CCM — DMA1 cannot access this region`

### 7. Note MISRA-C deviations (where project uses MISRA)

Flag these specific rules with the required deviation comment format:

| Rule | What to flag |
|------|--------------|
| 14.4 | `if`/`while` controlling expression not essentially Boolean |
| 21.3 | `malloc`/`free` after initialisation phase |
| 21.6 | `printf` family in production code |
| 15.5 | Multiple return points in a function |

Emit: `nit: [file:line] MISRA Rule 21.6 deviation — add /* MISRA deviation: … */ comment`

### 8. Approve or request changes

- **Approve** when no `blocker:` findings remain.
- **Request changes** when one or more `blocker:` items exist.
- Every finding must be one of: `nit:` / `suggestion:` / `question:` / `blocker:`

Comment format:

```
<tag>: [file.c:line] <one-sentence description of the problem>
  Expected: <what correct code looks like>
  Actual:   <what the diff shows>
```

## Examples

See [examples.md](examples.md).

## References

- [MISRA-C:2012 Guidelines](https://www.misra.org.uk/)
- [Barr Group Embedded C Coding Standard](https://barrgroup.com/embedded-systems/books/embedded-c-coding-standard)
- [ARM Cortex-M System Design Reference](https://developer.arm.com/documentation/dui0552/latest/)
