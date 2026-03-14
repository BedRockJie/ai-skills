# Skill: Embedded Code Review

## Purpose

Help AI agents perform thorough, safety-conscious code reviews for embedded
firmware — covering correctness, hardware-software interface integrity,
memory safety, and real-time constraints.

## When to use

Use this skill when:

- Reviewing a pull request or patch for firmware running on MCUs or SoCs
- Self-reviewing changes before requesting a peer review
- Establishing or enforcing a team code-review standard for C/C++ firmware

## Instructions

### 1. Understand the hardware context before commenting

- Read the target MCU/SoC datasheet section relevant to the changed peripheral.
- Check the PR description: which hardware revision, which toolchain, which RTOS
  (or bare-metal) does this change run on?
- Understand *why* the change was made — a register write sequence is often
  dictated by the hardware errata, not developer preference.

### 2. Check volatile and memory-mapped register correctness

- Every memory-mapped register struct must use `volatile`:
  ```c
  /* Correct */
  volatile uint32_t *const SR = (volatile uint32_t *)0x40013000;

  /* Wrong — compiler may cache the read */
  uint32_t *const SR = (uint32_t *)0x40013000;
  ```
- Variables shared between an ISR and non-ISR context must be `volatile`.
- Verify that read-modify-write on status registers does not accidentally
  clear write-1-to-clear (W1C) bits unintentionally.

### 3. Check ISR safety

- ISR functions must not call any blocking or non-reentrant APIs
  (e.g., `printf`, `malloc`, RTOS blocking calls like `xQueueSend` —
  use `xQueueSendFromISR` instead).
- Verify that shared data structures accessed from both ISR and task context
  are protected with critical sections or atomic operations:
  ```c
  /* ARM Cortex-M: disable/enable interrupts around shared data */
  __disable_irq();
  shared_counter++;
  __enable_irq();
  ```
- ISR handlers must be as short as possible — defer work to a task via a
  queue or semaphore; do not process data inside the ISR.

### 4. Check memory safety and stack usage

- Reject dynamic memory allocation (`malloc`/`free`) in bare-metal or
  MISRA-compliant firmware unless explicitly approved and bounded.
- Review stack-allocated arrays in ISRs — each ISR uses its own stack
  frame; large local arrays may cause hard faults.
- Confirm that string / buffer operations are bounded:
  ```c
  /* Unsafe */
  strcpy(dst, src);

  /* Safe */
  strncpy(dst, src, sizeof(dst) - 1);
  dst[sizeof(dst) - 1] = '\0';
  ```
- Check for signed/unsigned mismatch in array index calculations that
  could produce unexpected wrap-around.

### 5. Check peripheral driver correctness

- Register initialisation sequences must match the datasheet order
  (some peripherals require enable → configure → start, not the reverse).
- Verify clock enable calls before any peripheral register access
  (e.g., `__HAL_RCC_USART1_CLK_ENABLE()` on STM32 must precede USART config).
- DMA descriptors and buffers must reside in DMA-accessible memory regions;
  flag any buffers placed in DTCM/CCM if the DMA cannot reach those regions.
- Confirm timeout values in polling loops to prevent CPU lockup:
  ```c
  uint32_t timeout = 1000; /* ticks */
  while (!(USART1->SR & USART_SR_TC) && timeout--) {}
  if (timeout == 0) { return ERROR_TIMEOUT; }
  ```

### 6. Check real-time and RTOS usage

- Task stack sizes must be reviewed against call-tree depth plus local variables.
- RTOS primitive usage must match context: use `FromISR` variants inside ISRs.
- Verify no task calls a driver function that disables interrupts for longer
  than the system's worst-case interrupt latency budget.
- Check that task priorities are assigned intentionally (higher-priority tasks
  should complete faster; avoid priority inversion by using mutexes with
  priority inheritance).

### 7. Check for MISRA-C key rules (where applicable)

| Rule | What to look for |
|---|---|
| Rule 14.4 | Controlling expression of `if`/`while` must be essentially Boolean |
| Rule 15.5 | Return statement at end of function only |
| Rule 17.3 | No implicit function declarations |
| Rule 21.3 | No dynamic memory allocation after initialisation |
| Rule 21.6 | No use of `printf` family in production code |

Flag MISRA deviations with a `/* MISRA deviation: Rule X.Y – reason */` comment.

### 8. Comment constructively

Use a tiered comment style:

| Prefix | Meaning |
|---|---|
| `nit:` | Minor style preference – author may choose to ignore |
| `suggestion:` | Improvement idea – not blocking |
| `question:` | Seeking hardware or design clarification – not necessarily a problem |
| `blocker:` | Must be addressed before merge (safety, correctness, or data corruption) |

Example:

```
blocker: SR is not declared volatile; the compiler may optimise away the
poll loop entirely on -O2. Declare as volatile uint32_t *.

question: The datasheet errata (rev C, §2.1) notes a required delay between
enabling the PLL and selecting it as clock source. Is that handled here?
```

### 9. Approve or request changes clearly

- Approve when correctness, ISR safety, and memory safety are satisfied.
- Request changes when there is at least one `blocker:` comment.
- Do not leave reviews in a perpetual "commented" state — decide.

## Examples

See [examples.md](examples.md).

## References

- [MISRA-C:2012 Guidelines](https://www.misra.org.uk/)
- [ARM Cortex-M System Design Reference](https://developer.arm.com/documentation/dui0552/latest/)
- [Google Engineering Practices – Code Review](https://google.github.io/eng-practices/review/)
- [Barr Group Embedded C Coding Standard](https://barrgroup.com/embedded-systems/books/embedded-c-coding-standard)
