#!/usr/bin/env python3
"""Decode Cortex-M SCB fault registers and print a human-readable diagnosis.

Usage examples:
  # Decode CFSR only
  python3 decode_cortexm_fault.py --cfsr 0x00000200

  # Decode all four fault registers (capture them in HardFault_Handler before reset)
  python3 decode_cortexm_fault.py --cfsr 0x00020000 --hfsr 0x40000000 \\
      --mmfar 0x00000004

  # Read register values in GDB:
  #   (gdb) p/x SCB->CFSR    -> use for --cfsr
  #   (gdb) p/x SCB->HFSR    -> use for --hfsr
  #   (gdb) p/x SCB->MMFAR   -> use for --mmfar
  #   (gdb) p/x SCB->BFAR    -> use for --bfar
  #
  # Read via J-Link Commander:
  #   mem 0xE000ED28 4   (CFSR)
  #   mem 0xE000ED2C 4   (HFSR)
  #   mem 0xE000ED34 4   (MMFAR)
  #   mem 0xE000ED38 4   (BFAR)
"""

from __future__ import annotations

import argparse
import sys
from typing import NamedTuple


class _CfsrBit(NamedTuple):
    bit: int
    name: str
    description: str
    fix_hint: str


_CFSR_BITS: list[_CfsrBit] = [
    # Usage Fault Status Register (UFSR) — bits 31:16
    _CfsrBit(31, "DIVBYZERO",
             "Division by zero (SDIV/UDIV instruction).",
             "Add a zero-check before the division, or clear CCR.DIV_0_TRP to suppress trapping."),
    _CfsrBit(30, "UNALIGNED",
             "Unaligned memory access.",
             "Align the struct/pointer, or add __attribute__((packed)) if intentional; "
             "also check CCR.UNALIGN_TRP."),
    _CfsrBit(19, "NOCP",
             "No co-processor — FPU instruction with FPU disabled.",
             "Enable FPU before any FP instruction: SCB->CPACR |= (0xF << 20); __DSB(); __ISB();"),
    _CfsrBit(18, "INVPC",
             "Invalid PC load — bad EXC_RETURN value on exception return.",
             "Check the stacked LR value and exception-nesting logic; "
             "likely a stack corruption or incorrect exception return."),
    _CfsrBit(17, "INVSTATE",
             "Invalid EPSR state — EPSR.T=0 or illegal EPSR combination.",
             "Ensure all function pointers have bit 0 set (Thumb bit); "
             "a pointer loaded from a table stored in word-aligned flash may have bit 0 cleared."),
    _CfsrBit(16, "UNDEFINSTR",
             "Undefined instruction executed.",
             "Check for Thumb/ARM mode mismatch at the stacked PC, "
             "or memory corruption that overwrote the instruction stream."),
    # Bus Fault Status Register (BFSR) — bits 15:8
    _CfsrBit(15, "BFARVALID",
             "BFAR register holds the valid faulting address.",
             "Inspect --bfar for the exact address that triggered the bus error."),
    _CfsrBit(13, "LSPERR",
             "Lazy FP state preservation bus fault.",
             "FP context save triggered a bus fault; disable lazy stacking "
             "(FPU->FPCCR &= ~FPU_FPCCR_LSPEN_Msk) or fix the FP stack memory region."),
    _CfsrBit(12, "STKERR",
             "Bus fault during exception entry stacking.",
             "Stack pointer is invalid or out of range; "
             "check SP alignment and available SRAM at the top of the stack."),
    _CfsrBit(11, "UNSTKERR",
             "Bus fault during exception return unstacking.",
             "Stack pointer was corrupted during the exception; "
             "check for stack overflow or out-of-bounds write."),
    _CfsrBit(10, "IMPRECISERR",
             "Imprecise data bus error (async — fault address not captured).",
             "Set CCR.DISDEFWBUF=1 to disable write buffering; "
             "the next run will produce PRECISERR with a valid BFAR."),
    _CfsrBit(9, "PRECISERR",
             "Precise data bus error — BFAR is valid when BFARVALID is also set.",
             "Check --bfar for the bad address; "
             "likely a null/unmapped pointer or a clock-gated peripheral access."),
    _CfsrBit(8, "IBUSERR",
             "Instruction bus error.",
             "PC branched to an unmapped or non-executable address; "
             "check function pointers and vtable entries."),
    # MemManage Fault Status Register (MMFSR) — bits 7:0
    _CfsrBit(7, "MMARVALID",
             "MMFAR register holds the valid faulting address.",
             "Inspect --mmfar for the MPU-protected address that was accessed."),
    _CfsrBit(5, "MLSPERR",
             "Lazy FP state preservation MemManage fault.",
             "FP context save tripped an MPU region boundary; "
             "verify MPU configuration covers the FPU stack area."),
    _CfsrBit(4, "MSTKERR",
             "MemManage fault during exception entry stacking.",
             "Stack has grown into an MPU-protected guard region; "
             "increase the task or ISR stack size."),
    _CfsrBit(3, "MUNSTKERR",
             "MemManage fault during exception return unstacking.",
             "Stack pointer corrupted or stack shrank below the MPU guard; "
             "check for stack overflow in the interrupted context."),
    _CfsrBit(1, "DACCVIOL",
             "Data access violation — MMFAR may be valid if MMARVALID is also set.",
             "Access to an MPU-restricted or null-region address; "
             "validate the pointer before dereferencing."),
    _CfsrBit(0, "IACCVIOL",
             "Instruction access violation (MPU or XN execute-never region).",
             "Attempting to execute from a non-executable region; "
             "check function pointer value and MPU XN settings."),
]


class _HfsrBit(NamedTuple):
    bit: int
    name: str
    description: str


_HFSR_BITS: list[_HfsrBit] = [
    _HfsrBit(31, "DEBUGEVT",
             "Debug event escalated to hard fault "
             "(harmless if a debugger is attached; unexpected if not)."),
    _HfsrBit(30, "FORCED",
             "Forced hard fault — a configurable fault (BusFault, MemManage, or UsageFault) "
             "escalated because it was disabled or occurred inside an exception handler."),
    _HfsrBit(1, "VECTTBL",
             "Vector table read fault on exception entry — "
             "SCB->VTOR points to an invalid or misaligned vector table."),
]

_CORTEXM_REGIONS: list[tuple[int, int, str]] = [
    (0x00000000, 0x1FFFFFFF, "Code region (Flash/ROM)"),
    (0x20000000, 0x3FFFFFFF, "SRAM region"),
    (0x40000000, 0x5FFFFFFF, "Peripheral region (APB/AHB bus)"),
    (0x60000000, 0x7FFFFFFF, "External RAM region"),
    (0x80000000, 0x9FFFFFFF, "External device region"),
    (0xA0000000, 0xBFFFFFFF, "External PPB / device region"),
    (0xC0000000, 0xDFFFFFFF, "External device region"),
    (0xE0000000, 0xFFFFFFFF, "System region (PPB / vendor-specific)"),
]


def _address_region(addr: int) -> str:
    for start, end, name in _CORTEXM_REGIONS:
        if start <= addr <= end:
            return name
    return "Unknown region"


def _parse_hex(value: str) -> int:
    return int(value, 0)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Decode Cortex-M SCB fault registers and print a diagnosis.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "GDB commands to capture register values before reset:\n"
            "  (gdb) p/x SCB->CFSR\n"
            "  (gdb) p/x SCB->HFSR\n"
            "  (gdb) p/x SCB->MMFAR\n"
            "  (gdb) p/x SCB->BFAR\n"
            "  (gdb) p/x ((uint32_t *)__get_MSP())[6]  <- stacked PC\n"
            "\n"
            "OpenOCD commands to read without halting (unsafe but quick):\n"
            "  mdw 0xE000ED28   (CFSR)\n"
            "  mdw 0xE000ED2C   (HFSR)\n"
            "  mdw 0xE000ED34   (MMFAR)\n"
            "  mdw 0xE000ED38   (BFAR)\n"
        ),
    )
    parser.add_argument(
        "--cfsr", type=_parse_hex, required=True,
        metavar="0xVALUE",
        help="SCB->CFSR value (required). Captures MemManage, BusFault, and UsageFault bits.",
    )
    parser.add_argument(
        "--hfsr", type=_parse_hex, default=0,
        metavar="0xVALUE",
        help="SCB->HFSR value (optional). Indicates if a configurable fault was escalated.",
    )
    parser.add_argument(
        "--mmfar", type=_parse_hex, default=None,
        metavar="0xVALUE",
        help="SCB->MMFAR value (optional). Valid only when CFSR.MMARVALID is set.",
    )
    parser.add_argument(
        "--bfar", type=_parse_hex, default=None,
        metavar="0xVALUE",
        help="SCB->BFAR value (optional). Valid only when CFSR.BFARVALID is set.",
    )
    return parser


def _decode_cfsr(cfsr: int) -> list[_CfsrBit]:
    return [entry for entry in _CFSR_BITS if cfsr & (1 << entry.bit)]


def _decode_hfsr(hfsr: int) -> list[_HfsrBit]:
    return [entry for entry in _HFSR_BITS if hfsr & (1 << entry.bit)]


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    sep = "=" * 64
    print(f"\n{sep}")
    print("  Cortex-M Fault Register Decoder")
    print(sep)
    print(f"  CFSR  : 0x{args.cfsr:08X}")
    print(f"  HFSR  : 0x{args.hfsr:08X}")
    if args.mmfar is not None:
        print(f"  MMFAR : 0x{args.mmfar:08X}  [{_address_region(args.mmfar)}]")
    if args.bfar is not None:
        print(f"  BFAR  : 0x{args.bfar:08X}  [{_address_region(args.bfar)}]")
    print()

    cfsr_hits = _decode_cfsr(args.cfsr)
    hfsr_hits = _decode_hfsr(args.hfsr)

    if not cfsr_hits and not hfsr_hits:
        print("  No fault bits are set — all registers read as zero.")
        print("  Tip: capture registers BEFORE the system resets or clears them.\n")
        print(sep + "\n")
        return 0

    if hfsr_hits:
        print("HFSR active bits:")
        for h in hfsr_hits:
            print(f"  [{h.name}] {h.description}")
        print()

    if cfsr_hits:
        cfsr_names = {b.name for b in cfsr_hits}
        print("CFSR active bits:")
        for b in cfsr_hits:
            if b.name in ("BFARVALID", "MMARVALID"):
                continue  # report these alongside their address below
            print(f"\n  [{b.name}]")
            print(f"    Meaning  : {b.description}")
            print(f"    Fix hint : {b.fix_hint}")

        print()
        if "BFARVALID" in cfsr_names:
            if args.bfar is not None:
                label = "  ** NULL pointer dereference **" if args.bfar == 0 else ""
                print(f"  Bus fault address (BFAR) = 0x{args.bfar:08X}"
                      f"  [{_address_region(args.bfar)}]{label}")
            else:
                print("  BFARVALID is set but --bfar was not provided; re-run with --bfar.")

        if "MMARVALID" in cfsr_names:
            if args.mmfar is not None:
                label = "  ** NULL pointer dereference **" if args.mmfar == 0 else ""
                print(f"  MemManage fault address (MMFAR) = 0x{args.mmfar:08X}"
                      f"  [{_address_region(args.mmfar)}]{label}")
            else:
                print("  MMARVALID is set but --mmfar was not provided; re-run with --mmfar.")

    print(f"\n{sep}")
    print("  Next steps:")
    print("  1. In GDB, read the stacked PC at fault time:")
    print("       (gdb) p/x ((uint32_t *)__get_MSP())[6]")
    print("  2. Resolve the faulting source line:")
    print("       arm-none-eabi-addr2line -e build/firmware.elf 0x<stacked_pc>")
    print("  3. Apply the fix hint(s) shown above to that source line.")
    print("  4. Clear fault registers after analysis:")
    print("       SCB->CFSR = SCB->CFSR;   // W1C — write 1 to clear")
    print(f"{sep}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
