# Skill: Git for Embedded Firmware

## Purpose

Help AI agents follow clean, traceable Git workflows when developing embedded
firmware — covering branch naming, binary artifact handling, hardware-revision
tagging, vendor SDK submodules, and multi-platform release management.

## When to use

Use this skill when:

- Creating a branch for a firmware feature, driver fix, or board bring-up
- Tagging a firmware release that must be tied to a hardware revision
- Managing vendor SDK or HAL source code as a submodule
- Handling binary build artifacts (`.hex`, `.elf`, `.bin`, `.map`)
- Resolving merge conflicts in generated files (linker maps, auto-generated headers)
- Preparing a clean commit history before opening a PR

## Instructions

### 1. Branching

Use descriptive branch names that include the target board or subsystem:

```bash
git checkout -b feature/stm32h7-can-driver
git checkout -b fix/nxp-i2c-timeout-issue-42
git checkout -b bringup/new-rev-c-pcb
git checkout -b chore/update-freertos-10.6
```

- Branch off `main` (or `develop`) unless told otherwise.
- Include the board or SoC family in the name when a branch is hardware-specific.

### 2. Commits

- Write imperative-mood subject lines under 72 characters.
- Reference issue or hardware errata numbers when relevant:

```bash
git commit -m "fix(spi2): add clock enable before register access

RCC->APB1ENR SPI2EN must be set before any SPI2 register access
or the peripheral returns 0xFFFFFFFF. Confirmed on STM32H743 rev V.
Closes #23"
```

- Pair with the conventional-commits skill to format the type and scope.

### 3. Ignore build artifacts — never commit binaries to history

Keep generated files out of the repository. Add them to `.gitignore`:

```
# Build outputs
build/
*.elf
*.hex
*.bin
*.map
*.lst
*.d
*.o
*.a

# IDE project files (vendor-specific)
.settings/
*.uvoptx
*.uvprojx.bak
Debug/
Release/
```

Use **Git LFS** only when binary release artifacts (signed firmware images,
golden `.hex` files) must be stored alongside the source for traceability:

```bash
git lfs track "release/*.hex"
git lfs track "release/*.bin"
git add .gitattributes
```

### 4. Manage vendor SDKs with submodules

Never copy vendor SDK/HAL source directly into the repository — use submodules
to keep the vendor code versioned and auditable:

```bash
# Add STM32 HAL as a submodule at a specific tag
git submodule add https://github.com/STMicroelectronics/stm32h7xx_hal_driver.git \
    lib/stm32h7xx_hal

cd lib/stm32h7xx_hal
git checkout v1.11.3   # pin to a specific release
cd ../..
git add lib/stm32h7xx_hal .gitmodules
git commit -m "chore(hal): pin STM32H7 HAL to v1.11.3"
```

Cloning with submodules:

```bash
git clone --recurse-submodules <repo-url>
# or, after a plain clone:
git submodule update --init --recursive
```

Updating a submodule to a newer release:

```bash
cd lib/stm32h7xx_hal
git fetch && git checkout v1.12.0
cd ../..
git add lib/stm32h7xx_hal
git commit -m "chore(hal): upgrade STM32H7 HAL from v1.11.3 to v1.12.0"
```

### 5. Tagging releases with hardware revision

Firmware releases must record both the software version and the compatible
hardware revision:

```bash
# Format: v<major>.<minor>.<patch>+hw<revision>
git tag -a "v2.1.0+hwC" -m "Release v2.1.0 for PCB rev C

Changelog:
- feat(can): increase TX FIFO depth to 64 frames
- fix(adc): apply errata workaround for STM32H743 rev V silicon
- chore(hal): upgrade STM32H7 HAL to v1.12.0

Compatible hardware: PCB rev C (schematic: SCH-2024-003-C)
Build toolchain: arm-none-eabi-gcc 13.2 + CMake 3.28"
git push origin "v2.1.0+hwC"
```

- Increment hardware revision in the tag whenever the PCB changes in a way
  that requires different firmware behaviour.
- Store the hardware revision in a build-time constant for runtime checks:

```c
#define HW_REVISION_REQUIRED  'C'

void board_check_revision(void) {
    char rev = read_hw_id_pins();
    if (rev != HW_REVISION_REQUIRED) {
        log_error("Firmware built for hw rev %c, running on rev %c",
                  HW_REVISION_REQUIRED, rev);
    }
}
```

### 6. Keep history clean before a PR

- Prefer `git rebase` over `git merge` for integrating upstream changes on
  feature branches.
- Squash fixup commits before opening a PR:

```bash
git rebase -i HEAD~<n>
# In the editor: mark fixup commits as 'fixup' or 'squash'
```

### 7. Conflict resolution in generated files

Linker map files and auto-generated HAL init code often produce conflicts.
Prefer re-generation over manual merging:

```bash
git status                        # identify conflicting generated files
git checkout --theirs path/to/generated_file.c
# Re-run the code generator or CubeMX to produce a clean output
git add path/to/generated_file.c
git rebase --continue
```

## Examples

See [examples.md](examples.md).

## References

- [Git SCM documentation](https://git-scm.com/doc)
- [Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [Git LFS](https://git-lfs.github.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
