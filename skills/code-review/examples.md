# Embedded Code Review – Examples

## Example 1: Missing `volatile` on a status register

**Patch under review (custom register struct without `volatile`):**

```c
typedef struct {
    uint32_t SR;   /* Status register – note: NOT volatile */
    uint32_t DR;
    uint32_t BRR;
} USART_TypeDef;

static USART_TypeDef * const USART1 = (USART_TypeDef *)0x40013000;

static void wait_for_tx_complete(void) {
    while (!(USART1->SR & (1u << 6))) {}   /* TC bit */
}
```

**Review comment:**

```
blocker: USART_TypeDef::SR is not declared volatile. At -O1 or higher the
compiler is free to read SR once, cache it in a register, and produce an
infinite loop (or remove the loop entirely). Hardware status registers change
independently of the CPU, so they MUST be volatile:

  typedef struct {
      volatile uint32_t SR;
      volatile uint32_t DR;
      volatile uint32_t BRR;
  } USART_TypeDef;

This is how CMSIS-Device vendor headers define peripheral structs — follow
that convention so the compiler cannot optimise away hardware reads/writes.
```

**Corrected code:**

```c
typedef struct {
    volatile uint32_t SR;
    volatile uint32_t DR;
    volatile uint32_t BRR;
} USART_TypeDef;

static USART_TypeDef * const USART1 = (USART_TypeDef *)0x40013000;

static void wait_for_tx_complete(void) {
    uint32_t timeout = 10000;
    while (!(USART1->SR & (1u << 6)) && timeout--) {}   /* TC bit with timeout */
}
```

---

## Example 2: Blocking RTOS call inside an ISR

**Patch under review:**

```c
void USART1_IRQHandler(void) {
    char ch = USART1->DR;
    xQueueSend(rx_queue, &ch, portMAX_DELAY); /* Wait forever */
}
```

**Review comment:**

```
blocker: `xQueueSend` is not ISR-safe and must never be called with
portMAX_DELAY from an interrupt context — this will corrupt the RTOS scheduler.
Use `xQueueSendFromISR` with a BaseType_t woken variable and request a context
switch if needed.
```

**Corrected code:**

```c
void USART1_IRQHandler(void) {
    char ch = (char)USART1->DR;
    BaseType_t higher_priority_task_woken = pdFALSE;
    xQueueSendFromISR(rx_queue, &ch, &higher_priority_task_woken);
    portYIELD_FROM_ISR(higher_priority_task_woken);
}
```

---

## Example 3: Missing peripheral clock enable

**Patch under review:**

```c
void spi2_init(void) {
    SPI2->CR1 = SPI_CR1_MSTR | SPI_CR1_SPE;
    SPI2->CR2 = SPI_CR2_DS_7; /* 8-bit frames */
}
```

**Review comment:**

```
blocker: SPI2 peripheral clock is not enabled before accessing SPI2->CR1.
On STM32, reading or writing a register on a clock-gated peripheral returns
undefined data and may bus-fault on some silicon revisions.
Add `__HAL_RCC_SPI2_CLK_ENABLE()` (or the bare-metal equivalent
`RCC->APB1ENR |= RCC_APB1ENR_SPI2EN`) as the first line of spi2_init().
```

---

## Example 4: Unbounded buffer copy

**Patch under review:**

```c
void process_command(const char *cmd) {
    char local_buf[32];
    strcpy(local_buf, cmd);   /* cmd length unchecked */
    parse(local_buf);
}
```

**Review comment:**

```
blocker: `strcpy` does not check the source length. If `cmd` exceeds 31 bytes,
this overwrites the stack frame, corrupting the return address — a classic
stack-smash vulnerability on an MCU with no MMU protection.
Replace with a bounded copy:

  strncpy(local_buf, cmd, sizeof(local_buf) - 1);
  local_buf[sizeof(local_buf) - 1] = '\0';
```

---

## Example 5: Constructive suggestion on DMA buffer placement

**Patch under review:**

```c
/* Placed in default SRAM1 */
static uint8_t adc_dma_buf[256];
```

**Review comment (STM32H7 context):**

```
question: On STM32H7, DTCM (0x20000000) is not accessible to BDMA/DMA1/DMA2
without going through the AXI interconnect. Is adc_dma_buf intended for use
with DMA1? If so, consider annotating it with a linker section that places it
in AXI SRAM (D2, 0x30000000) to ensure DMA accessibility:

  __attribute__((section(".dma_buf"))) static uint8_t adc_dma_buf[256];
```
