# Skill: Peripheral Initialization Code Generator

## Purpose

Generate correct, complete peripheral initialization code for an embedded MCU
given a hardware specification.  Produce a compilable C function that the
caller can drop into a BSP or HAL source file.

## When to use

Use this skill when:

- Bringing up a new peripheral (UART, SPI, I2C, CAN, ADC, TIM, DMA) on an MCU
- Translating a datasheet or CubeMX/MCUXpresso configuration into hand-written C
- Reviewing generated init code for correctness against the datasheet sequence
- Creating a minimal, dependency-free init for a custom BSP

## Inputs

Collect these before generating:

| Input | Example |
|-------|---------|
| MCU family | STM32H743, NXP i.MX RT1060, nRF5340, GD32F450 |
| Peripheral type | UART / SPI / I2C / CAN-FD / ADC / TIM / DMA |
| Peripheral instance | USART2, SPI1, I2C3, FDCAN1 |
| Bus / clock domain | APB1 @ 120 MHz, APB2 @ 240 MHz |
| Configuration parameters | Baud rate, data bits, CPOL/CPHA, address, bit rate |
| GPIO pins (TX/RX/CLK/etc.) | PA2 AF7 (TX), PA3 AF7 (RX) |
| DMA required? | Yes – DMA1 Stream 6 CH4 / No |
| Interrupt required? | Yes – USART2_IRQn priority 8 / No (polling) |

## Instructions

### 1. Verify the initialization sequence from the datasheet

Every peripheral has a mandatory register-write order.  Before generating code,
confirm the correct sequence for the target family.  The general pattern is:

```
1. Enable peripheral clock in the RCC/CGC/CLOCK_CTRL register
2. Configure GPIO alternate function and drive strength
3. Reset the peripheral (if the family has a software-reset register)
4. Write configuration registers (baud, format, timing)
5. Enable the peripheral (set the EN/UE/TXEN/RXEN bit last)
6. Enable NVIC interrupt (if interrupt-driven)
```

Deviations from this order are a common source of hard faults and bus errors.

### 2. Fill in the clock-enable line

```c
/* STM32 example */
__HAL_RCC_USART2_CLK_ENABLE();          /* or: RCC->APB1ENR |= RCC_APB1ENR_USART2EN; */

/* NXP MCUX example */
CLOCK_EnableClock(kCLOCK_Lpuart2);

/* Nordic nRF example */
NRF_CLOCK->TASKS_HFCLKSTART = 1;
```

Missing this line causes reads of peripheral registers to return 0xFFFFFFFF and
leads to a Bus fault on some Cortex-M implementations.

### 3. Fill in the GPIO configuration

```c
/* STM32 — set alternate function then configure mode/speed */
GPIO_InitTypeDef gpio = {0};
gpio.Pin       = GPIO_PIN_2 | GPIO_PIN_3;
gpio.Mode      = GPIO_MODE_AF_PP;
gpio.Pull      = GPIO_NOPULL;
gpio.Speed     = GPIO_SPEED_FREQ_HIGH;
gpio.Alternate = GPIO_AF7_USART2;
HAL_GPIO_Init(GPIOA, &gpio);
```

### 4. Generate the peripheral configuration block

Fill in this template — one block per register that must be set:

```c
void <peripheral>_init(<config_params>) {
    /* 1. Clock enable */
    <clock_enable_line>;

    /* 2. GPIO */
    <gpio_init_block>;

    /* 3. Reset peripheral */
    <peripheral>->CR1 = 0;   /* or vendor reset API */

    /* 4. Configure */
    <peripheral>->BRR  = <baud_divisor>;   /* baud rate */
    <peripheral>->CR2  = 0;               /* stop bits, clock */
    <peripheral>->CR1  = USART_CR1_RE     /* receive enable  */
                       | USART_CR1_TE;    /* transmit enable */

    /* 5. Enable */
    <peripheral>->CR1 |= USART_CR1_UE;

    /* 6. NVIC (if interrupt-driven) */
    NVIC_SetPriority(<IRQn>, <priority>);
    NVIC_EnableIRQ(<IRQn>);
}
```

### 5. Validate the generated code against this checklist

- [ ] Clock-enable call appears **before** any peripheral register access
- [ ] GPIO alternate-function number matches the datasheet pinout table (not assumed)
- [ ] Configuration registers written **before** the peripheral-enable bit is set
- [ ] Timeout or ready-flag poll present when waiting for PLL/oscillator lock
- [ ] DMA channel/stream matches the request mapping table in the datasheet
- [ ] NVIC priority respects the system's priority band table (see architecture skill)
- [ ] No `volatile` missing on any pointer that accesses a peripheral register directly

## Output

Deliver a single compilable C function:

```c
/**
 * @brief  Initialize <PERIPHERAL> for <purpose>.
 * @note   Clock: <bus> @ <freq> MHz.  GPIO: <pin list>.
 *         Call this function once during system startup before using <peripheral>.
 */
void <peripheral>_init(void) {
    /* generated body */
}
```

Include a header declaration and any required `#include` directives.

## Examples

```c
/* USART2 @ 115200 baud, PA2/PA3, STM32H743, polling */
void usart2_init(void) {
    __HAL_RCC_USART2_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    GPIO_InitTypeDef gpio = {0};
    gpio.Pin       = GPIO_PIN_2 | GPIO_PIN_3;
    gpio.Mode      = GPIO_MODE_AF_PP;
    gpio.Pull      = GPIO_NOPULL;
    gpio.Speed     = GPIO_SPEED_FREQ_VERY_HIGH;
    gpio.Alternate = GPIO_AF7_USART2;
    HAL_GPIO_Init(GPIOA, &gpio);

    USART2->CR1 = 0;
    USART2->BRR = 120000000U / 115200U;   /* APB1 = 120 MHz */
    USART2->CR1 = USART_CR1_TE | USART_CR1_RE | USART_CR1_UE;
}
```

## References

- [STM32 Reference Manual RM0433 (STM32H7)](https://www.st.com/resource/en/reference_manual/rm0433-stm32h742-stm32h743-stm32h753-and-stm32h750-value-line-advanced-armbased-32bit-mcus-stmicroelectronics.pdf)
- [NXP i.MX RT1060 Reference Manual](https://www.nxp.com/docs/en/reference-manual/IMXRT1060RM.pdf)
- [CMSIS-Core Peripheral Access (ARM)](https://arm-software.github.io/CMSIS_5/Core/html/group__peripheral__gr.html)
