---
name: peripheral-init
description: Generate a small C peripheral init function from a hardware spec and constraints.
license: MIT
---

# Skill: Peripheral Initialization Code Generator

## Purpose

Generate a small C init function for a target peripheral from a hardware spec.

## When to use

Use this skill when:

- Bringing up a new peripheral
- Translating a datasheet or tool config into C
- Reviewing init order for a target peripheral
- Writing a small init path without extra framework code

## Inputs

Collect these first:

| Input | Example |
|-------|---------|
| Target family | STM32H743, i.MX RT1060, nRF5340 |
| Peripheral | UART, SPI, I2C, CAN, ADC, TIM, DMA |
| Instance | USART2, SPI1, I2C3 |
| Clock domain | APB1 @ 120 MHz |
| Config | baud rate, mode, timing |
| Pins | PA2 AF7, PA3 AF7 |
| DMA | yes or no |
| IRQ | yes or no |

## Instructions

### 1. Confirm init order

Use the target reference manual. The usual order is:

```text
1. Enable the peripheral clock
2. Configure pins
3. Reset the peripheral if needed
4. Write config registers
5. Enable the peripheral
6. Enable interrupts if used
```

### 2. Fill in the clock step

```c
__HAL_RCC_USART2_CLK_ENABLE();
CLOCK_EnableClock(kCLOCK_Lpuart2);
NRF_CLOCK->TASKS_HFCLKSTART = 1;
```

### 3. Fill in the pin step

```c
GPIO_InitTypeDef gpio = {0};
gpio.Pin = GPIO_PIN_2 | GPIO_PIN_3;
gpio.Mode = GPIO_MODE_AF_PP;
gpio.Pull = GPIO_NOPULL;
gpio.Speed = GPIO_SPEED_FREQ_HIGH;
gpio.Alternate = GPIO_AF7_USART2;
HAL_GPIO_Init(GPIOA, &gpio);
```

### 4. Generate the init function

```c
void <peripheral>_init(void) {
    <clock_enable_line>;
    <gpio_init_block>;
    <peripheral>->CR1 = 0;
    <config_writes>;
    <enable_line>;
    <irq_setup_if_needed>;
}
```

### 5. Validate the result

- Clock enable appears first
- Pin config matches the manual
- Config writes happen before enable
- DMA and IRQ mapping match the target docs
- Poll loops have a timeout when needed

## Output

Deliver one compilable C function and the needed declarations.

## Examples

```c
void usart2_init(void) {
    __HAL_RCC_USART2_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    GPIO_InitTypeDef gpio = {0};
    gpio.Pin = GPIO_PIN_2 | GPIO_PIN_3;
    gpio.Mode = GPIO_MODE_AF_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    gpio.Alternate = GPIO_AF7_USART2;
    HAL_GPIO_Init(GPIOA, &gpio);

    USART2->CR1 = 0;
    USART2->BRR = 120000000U / 115200U;
    USART2->CR1 = USART_CR1_TE | USART_CR1_RE | USART_CR1_UE;
}
```

## References

- [STM32 Reference Manual RM0433 (STM32H7)](https://www.st.com/resource/en/reference_manual/rm0433-stm32h742-stm32h743-stm32h753-and-stm32h750-value-line-advanced-armbased-32bit-mcus-stmicroelectronics.pdf)
- [NXP i.MX RT1060 Reference Manual](https://www.nxp.com/docs/en/reference-manual/IMXRT1060RM.pdf)
- [CMSIS-Core Peripheral Access (ARM)](https://arm-software.github.io/CMSIS_5/Core/html/group__peripheral__gr.html)
