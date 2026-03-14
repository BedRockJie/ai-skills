# Git for Embedded Firmware – Examples

## Example 1: CAN driver feature branch workflow

```bash
# 1. Start from a clean main
git checkout main && git pull

# 2. Create a hardware-scoped feature branch
git checkout -b feature/stm32h7-can-fd-driver

# 3. Implement the driver, then stage and commit
git add src/drivers/can/
git commit -m "feat(can): add CAN FD driver for STM32H7 FDCAN peripheral

Supports ISO CAN FD at up to 8 Mbit/s data phase.
Interrupt-driven TX/RX with 64-byte payload support.
Closes #55"

# 4. Rebase onto latest main before opening a PR
git fetch origin
git rebase origin/main

# 5. Push
git push -u origin feature/stm32h7-can-fd-driver
```

---

## Example 2: Adding a vendor HAL as a submodule

```bash
# Initial setup
git submodule add \
  https://github.com/STMicroelectronics/stm32h7xx_hal_driver.git \
  lib/stm32h7xx_hal

# Pin to a specific release
cd lib/stm32h7xx_hal
git checkout v1.11.3
cd ../..
git add lib/stm32h7xx_hal .gitmodules
git commit -m "chore(hal): add STM32H7 HAL submodule pinned to v1.11.3"
git push

# Team members clone with submodules
git clone --recurse-submodules git@github.com:org/firmware.git
# Or update submodules after a plain clone
git submodule update --init --recursive
```

---

## Example 3: Tagging a firmware release with hardware revision

```bash
# Firmware v2.1.0 validated on PCB rev C
git tag -a "v2.1.0+hwC" -m "Release v2.1.0 for PCB rev C

Changelog:
- feat(can): CAN FD driver (Closes #55)
- fix(adc): errata workaround for STM32H743 rev V (Closes #61)
- chore(hal): upgrade STM32H7 HAL to v1.12.0

Compatible hardware: PCB rev C (SCH-2024-003-C)
Toolchain: arm-none-eabi-gcc 13.2.1, CMake 3.28"
git push origin "v2.1.0+hwC"
```

---

## Example 4: Squashing fixup commits before a PR

After implementing a driver you have four commits, but only the first is meaningful:

```
a1b2c3d feat(spi): add DMA-driven SPI2 driver
d4e5f67 fix typo in comment
g8h9i0j remove leftover debug print
k1l2m3n add missing volatile qualifier
```

Squash the last three into the first:

```bash
git rebase -i HEAD~4
# In the editor: mark the last three commits as 'fixup'
```

Result: one clean, reviewable commit.

---

## Example 5: Setting up `.gitignore` for an embedded project

```
# Build outputs
build/
*.elf
*.hex
*.bin
*.map
*.lst

# Object and dependency files
*.o
*.d
*.a

# IDE and toolchain artefacts
.settings/
*.uvoptx
*.uvprojx.bak
Debug/
Release/
.vs/
cmake-build-*/

# Semihosting / OpenOCD logs
*.log
openocd.pid
```

Binary release images that must be stored for traceability should use Git LFS:

```bash
git lfs track "release/*.hex"
git lfs track "release/*.bin"
git add .gitattributes
git commit -m "chore: track signed firmware images with Git LFS"
```
