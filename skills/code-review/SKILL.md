# Skill: Embedded C Code Review

## Purpose

Gate a firmware pull request through two sequential phases: an automated style
and size check (binary pass/fail, no judgment needed), then a targeted manual
review of embedded-specific correctness issues in the changed lines only.

## When to use

Use this skill when:

- Reviewing a pull request or patch for MCU / SoC firmware (C / C++)
- Self-reviewing before requesting a peer review
- Enforcing a repeatable, tool-backed review standard in a team

## Inputs

- A git branch with commits ready to review
- The base branch to diff against (default: `origin/main`)

## Instructions

Work through the two phases **in order**.  Do not start Phase 2 until Phase 1
produces `RESULT: PASS`.

---

### 1. Phase 1 — Automated style and size gate

#### 1a. Run the style-check script

```bash
bash skills/code-review/run_style_checks.sh [BASE_REF]
# Example: bash skills/code-review/run_style_checks.sh origin/main
```

The script performs three independent checks and prints a single result line:

```
RESULT: PASS — all style checks passed. Proceed to code review step 2.
```
or
```
RESULT: FAIL — fix the issues above before proceeding to code review.
```

**Do not proceed to Phase 2 while the result is FAIL.**

#### 1b. C / C++ style — clang-format

The script runs:

```bash
clang-format --dry-run --Werror --style=file  <every changed .c/.h/.cpp file>
```

- `--dry-run` makes no changes to files — it only checks.
- `--Werror` turns any formatting difference into a non-zero exit code.
- `--style=file` reads the project's `.clang-format`; falls back to LLVM style
  if no config file exists.

**Fix**: Apply the formatter in-place, then commit the result:

```bash
clang-format -i --style=file src/driver/uart.c src/driver/uart.h
git add -p     # review the diff before staging
```

#### 1c. Shell script style — shellcheck

The script runs `shellcheck` on every changed `.sh` file.  shellcheck reports
problems by severity (`error` / `warning` / `info` / `style`).

**Fix**: Resolve each reported issue.  For intentional suppressions, add an
inline directive:

```bash
# shellcheck disable=SC2034  # reason: variable used by caller via eval
MY_VAR="value"
```

#### 1d. Diff-size gate — reviewability limit

| Limit | Default | Override |
|-------|---------|----------|
| Lines changed per file | 200 | `MAX_LINES_PER_FILE=300 bash ...` |
| Total lines in the diff | 400 | `MAX_DIFF_LINES=600 bash ...` |

These limits exist because a reviewer (human or AI) cannot verify correctness
of a 1 000-line diff: important bugs hide in the volume.

**Fix**: Split the branch into smaller, independently-mergeable commits:

```bash
git rebase -i HEAD~<N>
# Mark large commits as 'edit', split with 'git reset HEAD~1', re-stage piece by piece
```

---

### 2. Phase 2 — Embedded correctness review of the diff

Open the diff:

```bash
git diff origin/main HEAD -- '*.c' '*.h'
```

Work through the checks below **in order**.  Emit one comment block per
finding, using the format at the end of this section.

#### 2. Check `volatile` on MMIO and ISR-shared variables

Every memory-mapped register pointer and every variable shared between an ISR
and task context must be `volatile`:

```c
/* Required */
volatile uint32_t * const SR = (volatile uint32_t *)0x40013000;

/* Flag — compiler caches the read at -O2 */
uint32_t * const SR = (uint32_t *)0x40013000;
```

Emit: `blocker: [file:line] missing volatile — compiler may cache this value`

#### 3. Check W1C register access

Read-modify-write on a write-1-to-clear status register clears all pending
flags, not just the intended one:

```c
/* Flag — clears all W1C bits */
USART1->SR &= ~USART_SR_ORE;

/* Correct — write only the target bit */
USART1->SR = USART_SR_ORE;
```

Emit: `blocker: [file:line] RMW on W1C register — use assignment, not &=~`

#### 4. Check ISR safety

For each ISR (identified by NVIC registration or `__attribute__((interrupt))`):

- Flag calls to: `printf`, `malloc`, `vTaskDelay`, `xQueueSend` (non-ISR),
  `HAL_Delay`, `osDelay`, `osMutexAcquire`.
- Flag RTOS operations that lack the `FromISR` suffix.
- Flag local arrays ≥ 64 bytes (risk of ISR stack overflow).

Emit: `blocker: [file:line] blocking call in ISR — use xQueueSendFromISR`

#### 5. Check memory safety

- Flag `strcpy`, `sprintf`, `gets` — require bounded equivalents.
- Flag `malloc`/`free` in bare-metal or MISRA firmware unless approved.
- Flag signed/unsigned mismatch in array-index arithmetic.

Emit: `blocker: [file:line] unbounded copy — use strncpy(dst, src, sizeof(dst)-1)`

#### 6. Check peripheral driver sequence

- Clock-enable must appear **before** any peripheral register access.
- Poll loops must have a timeout counter.

```c
/* Flag — no timeout */
while (!(USART1->SR & USART_SR_TC)) {}

/* Required */
uint32_t t = 1000;
while (!(USART1->SR & USART_SR_TC) && t--) {}
if (t == 0) { return ERR_TIMEOUT; }
```

Emit: `blocker: [file:line] clock enable missing before peripheral register access`
Emit: `blocker: [file:line] unbounded poll — add timeout counter`

#### 7. Approve or request changes

- **Approve** when Phase 1 passed and no `blocker:` findings remain in Phase 2.
- **Request changes** when Phase 1 failed or any `blocker:` exists.

**Comment format** (one block per finding):

```
<tag>: [file.c:line] <one-sentence description>
  Expected: <correct pattern>
  Actual:   <what the diff shows>
```

Tags: `nit:` | `suggestion:` | `question:` | `blocker:`

## Examples

See [examples.md](examples.md).

## References

- [clang-format documentation](https://clang.llvm.org/docs/ClangFormat.html)
- [shellcheck wiki](https://www.shellcheck.net/wiki/)
- [MISRA-C:2012 Guidelines](https://www.misra.org.uk/)
- [Barr Group Embedded C Coding Standard](https://barrgroup.com/embedded-systems/books/embedded-c-coding-standard)
