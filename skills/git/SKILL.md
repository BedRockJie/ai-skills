# Skill: Git for Embedded Firmware

## Purpose

Execute the correct Git command sequence for each firmware task — branching,
committing, ignoring build artifacts, managing vendor SDKs, tagging releases
with hardware revision, and cleaning history before a PR.

## When to use

Use this skill when:

- Starting work on a new driver, board bring-up, or firmware fix
- Tagging a release tied to a specific PCB revision
- Adding or updating a vendor SDK / HAL submodule
- Keeping binary build artifacts out of the repository
- Preparing a clean commit history before opening a PR

## Instructions

### 1. Create a branch

```bash
# New peripheral driver
git checkout -b feature/<board>-<peripheral>-driver
# Example: git checkout -b feature/stm32h7-fdcan-driver

# Bug fix (reference issue number)
git checkout -b fix/<subsystem>-issue-<N>
# Example: git checkout -b fix/spi2-clock-enable-issue-42

# New hardware revision bring-up
git checkout -b bringup/hw-rev-<X>
# Example: git checkout -b bringup/hw-rev-d

# Vendor SDK / toolchain update
git checkout -b chore/update-<vendor>-<version>
# Example: git checkout -b chore/update-freertos-10.6
```

Always branch off `main` (or `develop`) unless a long-lived release branch
exists for the target hardware.

### 2. Commit — pair with the conventional-commits skill

```bash
python3 skills/conventional-commits/check_commit_message.py \
    --message "fix(spi2): enable APB1 clock before register access"
git commit -m "fix(spi2): enable APB1 clock before register access

RCC->APB1ENR SPI2EN must be set before any SPI2 register access.
Reading an ungated peripheral returns 0xFFFFFFFF and triggers PRECISERR.
Confirmed on STM32H743 rev V errata §2.3.4.
Closes #42"
```

### 3. Ignore build artifacts — never commit binaries to history

Add to `.gitignore`:

```
# Toolchain outputs
build/
*.elf
*.hex
*.bin
*.map
*.lst
*.d
*.o
*.a
*.su

# IDE / vendor-generated files
.settings/
*.uvoptx
*.uvprojx.bak
Debug/
Release/
```

Use **Git LFS only** for signed release binaries that must be stored alongside
source for traceability (regulatory audit trails, golden images):

```bash
git lfs track "release/*.hex"
git lfs track "release/*.bin"
git add .gitattributes
git commit -m "chore(lfs): track signed release images"
```

### 4. Add or update a vendor SDK submodule

```bash
# Add — pin to a specific release tag
git submodule add https://github.com/STMicroelectronics/stm32h7xx_hal_driver.git \
    lib/stm32h7xx_hal
cd lib/stm32h7xx_hal && git checkout v1.11.3 && cd ../..
git add lib/stm32h7xx_hal .gitmodules
git commit -m "chore(hal): add STM32H7 HAL submodule at v1.11.3"

# Clone a repo that already has submodules
git clone --recurse-submodules <repo-url>
# or, after a plain clone:
git submodule update --init --recursive

# Update to a newer release
cd lib/stm32h7xx_hal && git fetch && git checkout v1.12.0 && cd ../..
git add lib/stm32h7xx_hal
git commit -m "chore(hal): upgrade STM32H7 HAL from v1.11.3 to v1.12.0"
```

### 5. Tag a release with hardware revision

Format: `v<major>.<minor>.<patch>+hw<Revision>`

```bash
git tag -a "v2.1.0+hwC" -m "Release v2.1.0 for PCB rev C

Changelog:
- feat(can): increase TX FIFO depth to 64 frames
- fix(adc): apply errata workaround for STM32H743 rev V
- chore(hal): upgrade STM32H7 HAL to v1.12.0

Compatible hardware: PCB rev C (schematic SCH-2024-003-C)
Toolchain: arm-none-eabi-gcc 13.2 + CMake 3.28"

git push origin "v2.1.0+hwC"
```

Add a compile-time hardware revision check to catch firmware/hardware mismatches:

```c
#define HW_REVISION_REQUIRED 'C'

void board_check_hw_revision(void) {
    char rev = board_read_id_pins();
    if (rev != HW_REVISION_REQUIRED) {
        LOG_ERROR("Firmware built for hw rev %c, running on rev %c",
                  HW_REVISION_REQUIRED, rev);
    }
}
```

### 6. Clean history before a PR

```bash
# Squash fixup commits interactively
git rebase -i HEAD~<N>
# In the editor: change 'pick' to 'fixup' for WIP/typo commits

# Rebase onto updated main instead of merge
git fetch origin
git rebase origin/main
```

### 7. Resolve generated-file conflicts

Linker map files and CubeMX / MCUXpresso-generated files produce conflicts.
Re-generate rather than manually merge:

```bash
git status                             # find conflicting generated file
git checkout --theirs path/to/file.c  # take their version as base
# Re-run the code generator (CubeMX, STM32CubeIDE) to produce clean output
git add path/to/file.c
git rebase --continue
```

## Examples

See [examples.md](examples.md).

## References

- [Git SCM documentation](https://git-scm.com/doc)
- [Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [Git LFS](https://git-lfs.github.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
