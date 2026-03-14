# Skill: Embedded Firmware Architecture

## Purpose

Help AI agents reason about and design firmware architecture for embedded
systems — covering SoC/MCU platform constraints, layered software structure,
memory layout, execution model selection, and hardware-software partitioning.

## When to use

Use this skill when:

- Starting firmware design for a new SoC or MCU (ARM Cortex-M/A/R, x86, RISC-V,
  AMD/Intel embedded)
- Partitioning responsibilities between BSP, HAL, middleware, and application
- Choosing between bare-metal and RTOS execution models
- Planning flash and RAM memory layout before writing linker scripts
- Writing Architecture Decision Records (ADRs) for significant firmware choices

## Instructions

### 1. Capture platform constraints first

Before proposing any design, gather:

- **Target device** – vendor, family, core (e.g., STM32H743, Cortex-M7 @ 480 MHz)
- **Memory budget** – internal Flash/SRAM sizes; external memory (QSPI Flash,
  SDRAM, EEPROM)
- **Peripherals in use** – UART, SPI, I2C, CAN, USB, DMA, ADC, timers
- **Real-time requirements** – hard/soft deadlines, worst-case interrupt latency
- **Power budget** – active current ceiling, required sleep modes, wake sources
- **Safety or compliance** – IEC 61508, ISO 26262, MISRA-C applicability

### 2. Choose the execution model

| Model | When to use |
|---|---|
| Bare-metal super-loop | ≤ 2 concurrent concerns, no blocking I/O, ≤ 32 KB RAM |
| Bare-metal + ISR | Latency-critical events plus background processing |
| RTOS (FreeRTOS, Zephyr, ThreadX) | ≥ 3 independent tasks, blocking I/O, deadline management |
| Asymmetric multi-core (AMP) | Mixed safety criticality or mixed OS on multi-core SoC |

Document the decision as an ADR (see step 5).

### 3. Define the layered firmware architecture

Organise firmware top-down and enforce strict layer boundaries:

```
┌──────────────────────────────────────────────┐
│  Application Layer                           │
│  (state machines, protocols, business logic) │
├──────────────────────────────────────────────┤
│  Middleware / Services                       │
│  (FatFS, LwIP, MQTT, USB stack, RTOS APIs)   │
├──────────────────────────────────────────────┤
│  HAL / Driver Layer                          │
│  (UART, SPI, DMA, ADC, CAN drivers)          │
├──────────────────────────────────────────────┤
│  BSP / CMSIS / Vendor SDK                   │
│  (clock init, pin mux, startup, vector table)│
├──────────────────────────────────────────────┤
│  Hardware                                    │
│  (registers, on-chip peripherals, board)     │
└──────────────────────────────────────────────┘
```

Rules:
- Upper layers call downward only; hardware registers are never accessed
  above the HAL boundary.
- Each driver owns exactly one peripheral instance.
- HAL functions must be re-entrant, or clearly documented when they are not.
- Keep vendor SDK code in a versioned submodule — never edit it directly.

### 4. Define the memory map

Sketch the linker-script regions before coding:

```
Flash (example: 2 MB @ 0x08000000)
  0x08000000  Interrupt vector table
  0x08000400  Bootloader / secure boot partition
  0x08010000  Application image slot A
  0x08100000  Application image slot B  (OTA update)
  0x081F0000  NVM / configuration page

SRAM (example: 512 KB SRAM1 + 128 KB DTCM)
  0x20000000  .data  (initialised globals)
  0x20010000  .bss   (zero-initialised globals)
  0x20020000  Heap   (keep minimal; prefer static allocation)
  0x2003C000  Stack  (grows downward; add guard page)
  0x20000000  DTCM   (ISR stacks, time-critical buffers — fastest access)
```

- Prefer **static allocation** in safety-critical or memory-constrained targets.
- Place ISR stacks and hot data in DTCM/ITCM (Cortex-M7) for lowest latency.
- Use `__attribute__((section(".dtcm")))` to force placement explicitly.

### 5. Assign NVIC interrupt priority bands

Prevent priority inversion by partitioning Cortex-M NVIC priorities:

| Band | Priority range | Typical users |
|---|---|---|
| Safety / watchdog | 0 – 1 | WDT refresh, hard-fault escalation |
| Hard real-time | 2 – 4 | Motor PWM update, sensor sampling ISR |
| Soft real-time | 5 – 8 | UART RX, CAN receive, SPI completion |
| Background comms | 9 – 12 | USB DMA, Ethernet descriptor handling |
| RTOS kernel | 13 – 15 | SysTick, PendSV (lowest preemptible) |

Never call RTOS blocking APIs from priorities 0–`configMAX_SYSCALL_INTERRUPT_PRIORITY`.

### 6. Write an ADR for significant decisions

```markdown
# ADR-001: Use FreeRTOS with static allocation only

## Status
Accepted

## Context
The product requires concurrent handling of sensor fusion (1 kHz),
CAN telemetry (100 Hz), and async OTA update. Three independent deadlines
make a bare-metal super-loop fragile and difficult to maintain.

## Decision
Use FreeRTOS with configSUPPORT_DYNAMIC_ALLOCATION=0 (static tasks/queues only).

## Consequences
+ Clear task prioritisation; blocking drivers are simplified
+ Static-only allocation → deterministic memory, MISRA-C compliance easier
- ~8 KB Flash overhead for the FreeRTOS kernel
- Team must follow FreeRTOS API rules (no ISR-unsafe calls from tasks)
```

### 7. Review for common embedded architecture pitfalls

- **Missing `volatile`** – memory-mapped registers and ISR-shared variables must
  be declared `volatile`; omitting it allows the compiler to cache stale values.
- **Stack overflow** – calculate worst-case stack depth with a call-tree analysis;
  enable `configCHECK_FOR_STACK_OVERFLOW` in FreeRTOS during development.
- **Forgotten clock gating** – always enable the peripheral clock (e.g., via RCC
  on STM32) before accessing any register; reading an ungated peripheral returns
  undefined data.
- **FPU context in ISRs** – if ISRs use floating-point, save/restore the FPU
  context explicitly or restrict FP to a single protected task.
- **Busy-wait spin loops** – replace `while (!(reg & flag));` with timeout
  counters or event flags to prevent CPU hogging and watchdog starvation.
- **Toolchain-specific behaviour** – document compiler flags (`-O2`, LTO, whole-
  program optimisation) that affect volatile, inlining, and section placement.

## Examples

See [examples.md](examples.md).

## References

- [ARM Cortex-M Programming Guide (ARM DDI0403)](https://developer.arm.com/documentation/ddi0403/latest/)
- [FreeRTOS Reference Manual](https://www.freertos.org/Documentation/RTOS_book.html)
- [Zephyr RTOS Architecture Docs](https://docs.zephyrproject.org/latest/kernel/index.html)
- [MISRA-C:2012 Guidelines](https://www.misra.org.uk/)
- [Embedded Systems Architecture – Daniele Lacamera](https://www.packtpub.com/product/embedded-systems-architecture/9781788832502)
