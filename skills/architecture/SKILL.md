# Skill: Firmware Architecture Decision Maker

## Purpose

Produce three concrete artifacts — a **component map**, a **memory sketch**,
and one or more **ADRs** — for an embedded firmware project given hardware
constraints and requirements.

## When to use

Use this skill when:

- Starting firmware for a new MCU or SoC board
- Deciding between bare-metal and RTOS execution models
- Documenting a significant firmware design choice for the team
- Reviewing a proposed architecture before implementation begins

## Inputs

Collect these before starting:

| Input | Example |
|-------|---------|
| MCU / SoC | STM32H743, i.MX RT1060, nRF5340 |
| Flash / SRAM sizes | 2 MB Flash, 512 KB SRAM |
| Concurrent workloads | "Motor control 20 kHz + CAN 100 Hz + UART CLI" |
| Hard deadline | "Motor ISR ≤ 50 µs worst-case jitter" |
| Safety standard | None / IEC 61508 SIL-2 / ISO 26262 ASIL-B |
| Memory allocation strategy | "Static only" / "FreeRTOS heap_4" |

## Instructions

### 1. Select the execution model

Answer all four questions; use the **first row that matches**:

| Condition | Model |
|-----------|-------|
| ≤ 2 concurrent workloads, no blocking I/O | Bare-metal super-loop |
| ≥ 1 latency-critical ISR + background loop | Bare-metal + ISR |
| ≥ 3 independent deadlines, or any blocking I/O | RTOS (FreeRTOS / Zephyr / ThreadX) |
| Mixed safety levels or mixed OS on multi-core SoC | AMP (per-core assignment) |

Record the selected model. This becomes the subject of the first ADR.

### 2. Fill in the component map

List every software component — one row per component:

```
Layer         | Component            | Owns
──────────────┼──────────────────────┼────────────────────────────────
Application   | sensor_fusion        | Kalman filter, output queue
Application   | ota_manager          | Image validation, slot swap
Middleware    | freertos_tasks       | Task creation, scheduler config
HAL / Driver  | spi2_driver          | SPI2 peripheral, DMA channel 3
HAL / Driver  | can_driver           | FDCAN1, TX queue, RX ISR
BSP           | board_init           | Clocks, pin mux, vector table
```

Rule: a component may call only components in the same or lower layer.
Flag any component in Application or Middleware that accesses hardware
registers directly — those accesses belong in HAL or BSP.

### 3. Fill in the memory sketch

```
Flash (<SIZE> KB @ <BASE>)
  +0x000  Vector table + startup code
  +0x400  [Bootloader, if present]
  +XXXX   Application (slot A)
  +YYYY   [OTA slot B, if OTA required]
  +ZZZZ   [NVM / config page, if needed]

SRAM (<SIZE> KB @ <BASE>)
  .data   initialised globals      ~X KB
  .bss    zero-initialised globals ~Y KB
  heap    [static pool / none]      Z KB
  stack   grows downward            W KB  ← MPU guard page recommended
  [DTCM/CCM for ISR stacks and timing-critical buffers, if available]
```

Flag if `.data + .bss + heap + stack > available SRAM`.

### 4. Fill in the NVIC priority band table

```
Band 0–1    Safety:    [watchdog refresh, critical-fault handler]
Band 2–4    Hard RT:   [motor PWM, sensor-sampling ISR]
Band 5–8    Soft RT:   [UART RX, CAN RX, SPI complete]
Band 9–12   Comms:     [USB DMA, Ethernet descriptor]
Band 13–15  RTOS:      [SysTick, PendSV — must be lowest preemptible]
```

Fill in actual ISR names from the project.  Flag any ISR that calls a blocking
RTOS API (xQueueSend, osDelay, etc.) from a priority above
`configMAX_SYSCALL_INTERRUPT_PRIORITY`.

### 5. Write an ADR for each significant decision

One ADR per choice (execution model, memory strategy, IPC mechanism).

```markdown
# ADR-NNN: <title>

## Status
Accepted | Proposed | Superseded by ADR-XXX

## Context
<One paragraph: what constraint or requirement forced this decision>

## Decision
<One sentence: the choice made>

## Consequences
+ <benefit 1>
+ <benefit 2>
- <trade-off 1>
- <trade-off 2>
```

## Output

Deliver these three artifacts:

1. **Component map** — filled table from step 2
2. **Memory sketch** — filled template from step 3
3. **ADR(s)** — one file per major decision (step 5)

## Examples

See [examples.md](examples.md).

## References

- [ARM Cortex-M Programming Guide (ARM DDI0403)](https://developer.arm.com/documentation/ddi0403/latest/)
- [FreeRTOS Reference Manual](https://www.freertos.org/Documentation/RTOS_book.html)
- [Zephyr RTOS Architecture Docs](https://docs.zephyrproject.org/latest/kernel/index.html)
- [MISRA-C:2012 Guidelines](https://www.misra.org.uk/)
