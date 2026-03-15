#!/usr/bin/env bash

set -euo pipefail

BASE_REF="${1:-origin/main}"
CLANG_FORMAT_STYLE="${CLANG_FORMAT_STYLE:-file}"
CLANG_FORMAT_FALLBACK_STYLE="${CLANG_FORMAT_FALLBACK_STYLE:-LLVM}"
MAX_DIFF_LINES="${MAX_DIFF_LINES:-400}"
MAX_LINES_PER_FILE="${MAX_LINES_PER_FILE:-200}"

overall=0

header() { printf '\n=== %s ===\n' "$*"; }
ok() { printf '  [PASS] %s\n' "$*"; }
info() { printf '  [INFO] %s\n' "$*"; }
err() { printf '  [FAIL] %s\n' "$*" >&2; overall=1; }

if ! git rev-parse --git-dir > /dev/null 2>&1; then
    printf 'ERROR: must be run inside a git repository.\n' >&2
    exit 1
fi

merge_base=$(git merge-base HEAD "${BASE_REF}" 2>/dev/null) || {
    printf "ERROR: cannot find merge-base with '%s'.\n" "${BASE_REF}" >&2
    exit 1
}

c_files=()
sh_files=()
while IFS= read -r path; do
    [[ -f "$path" ]] || continue
    case "$path" in
        *.c|*.cc|*.cpp|*.cxx|*.h|*.hh|*.hpp) c_files+=("$path") ;;
        *.sh) sh_files+=("$path") ;;
    esac
done < <(git diff --name-only "${merge_base}" HEAD)

header "clang-format - C/C++ style check"
if [[ ${#c_files[@]} -eq 0 ]]; then
    info "No C/C++ files changed - skipping"
elif ! command -v clang-format > /dev/null 2>&1; then
    err "clang-format not found - install it before review"
else
    clang_fail=0
    for file in "${c_files[@]}"; do
        if ! clang-format --dry-run --Werror --style="${CLANG_FORMAT_STYLE}" \
            --fallback-style="${CLANG_FORMAT_FALLBACK_STYLE}" "$file"; then
            err "${file} - needs reformatting (run: clang-format -i --style=${CLANG_FORMAT_STYLE} --fallback-style=${CLANG_FORMAT_FALLBACK_STYLE} ${file})"
            clang_fail=1
        fi
    done
    if [[ $clang_fail -eq 0 ]]; then
        ok "${#c_files[@]} file(s) match clang-format style"
    fi
fi

header "shellcheck - shell style check"
if [[ ${#sh_files[@]} -eq 0 ]]; then
    info "No shell scripts changed - skipping"
elif ! command -v shellcheck > /dev/null 2>&1; then
    err "shellcheck not found - install it before review"
else
    shell_fail=0
    for file in "${sh_files[@]}"; do
        if ! shellcheck "$file"; then
            err "${file} - shellcheck reported issues"
            shell_fail=1
        fi
    done
    if [[ $shell_fail -eq 0 ]]; then
        ok "${#sh_files[@]} script(s) passed shellcheck"
    fi
fi

header "Diff-size gate - reviewability check"
per_file_fail=0
total_lines=0

while IFS=$'\t' read -r added deleted path; do
    [[ -n "$path" ]] || continue
    if [[ "$added" == "-" || "$deleted" == "-" ]]; then
        info "Skipping diff-size count for renamed binary file ${path}"
        continue
    fi
    file_total=$((added + deleted))
    total_lines=$((total_lines + file_total))
    if (( file_total > MAX_LINES_PER_FILE )); then
        err "${path}: ${file_total} lines changed - exceeds per-file limit of ${MAX_LINES_PER_FILE}. Split this change into smaller commits."
        per_file_fail=1
    fi
done < <(git diff --numstat "${merge_base}" HEAD)

if [[ $per_file_fail -eq 0 ]]; then
    ok "All individual files within ${MAX_LINES_PER_FILE}-line per-file limit"
fi

if (( total_lines > MAX_DIFF_LINES )); then
    err "Total diff is ${total_lines} lines - exceeds ${MAX_DIFF_LINES}-line limit. Break this review into smaller pieces."
else
    ok "Total diff ${total_lines} lines - within ${MAX_DIFF_LINES}-line limit"
fi

printf '\n'
if [[ $overall -eq 0 ]]; then
    printf 'RESULT: PASS - all style checks passed. Proceed to the next review stage.\n'
else
    printf 'RESULT: FAIL - fix the issues above before proceeding.\n' >&2
fi

exit "$overall"
