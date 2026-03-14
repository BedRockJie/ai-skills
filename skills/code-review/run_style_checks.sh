#!/usr/bin/env bash
# run_style_checks.sh — Style gate for C/C++ and shell scripts.
#
# Runs clang-format (C/C++) and shellcheck (Bash) on files changed since the
# merge-base with the target branch, then checks that the diff is small enough
# for a meaningful code review.
#
# Exit codes:
#   0  All checks passed
#   1  One or more checks failed (see printed output)
#
# Usage:
#   bash skills/code-review/run_style_checks.sh [BASE_REF]
#
# BASE_REF defaults to origin/main.  Override for other base branches:
#   bash skills/code-review/run_style_checks.sh origin/develop
#
# Requirements:
#   clang-format >= 10   (for --dry-run --Werror)
#   sc (shellcheck)      (any recent version)
#   git                  (must be run inside a git repo)
#
# Environment variables (all optional):
#   CLANG_FORMAT_STYLE   Style to use with clang-format. Default: file
#                        (reads .clang-format in the repo; falls back to LLVM)
#   MAX_DIFF_LINES       Maximum total lines added+deleted for the whole diff.
#                        Default: 400.
#   MAX_LINES_PER_FILE   Maximum lines added+deleted for a single file.
#                        Default: 200.

set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────────────
BASE_REF="${1:-origin/main}"
CLANG_FORMAT_STYLE="${CLANG_FORMAT_STYLE:-file}"
MAX_DIFF_LINES="${MAX_DIFF_LINES:-400}"
MAX_LINES_PER_FILE="${MAX_LINES_PER_FILE:-200}"

overall=0   # accumulate failures; stays 0 only if everything passes

# ── Helpers ───────────────────────────────────────────────────────────────────
_header() { printf '\n=== %s ===\n' "$*"; }
_ok()     { printf '  [PASS] %s\n' "$*"; }
_err()    { printf '  [FAIL] %s\n' "$*" >&2; overall=1; }
_info()   { printf '  [INFO] %s\n' "$*"; }

# ── Resolve changed files ─────────────────────────────────────────────────────
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "ERROR: must be run inside a git repository." >&2
    exit 1
fi

# Get the common ancestor commit so the diff is always against the branch point,
# not the current HEAD of base (which may have advanced past our branch).
merge_base=$(git merge-base HEAD "${BASE_REF}" 2>/dev/null) || {
    echo "ERROR: cannot find merge-base with '${BASE_REF}'." \
         "Is the remote fetched?" >&2
    exit 1
}

# Lists of changed files by language (only files that still exist in the tree)
c_files=()
sh_files=()
while IFS= read -r f; do
    [[ -f "$f" ]] || continue   # skip deleted files
    case "$f" in
        *.c|*.cc|*.cpp|*.cxx|*.h|*.hh|*.hpp) c_files+=("$f") ;;
        *.sh)                                  sh_files+=("$f") ;;
    esac
done < <(git diff --name-only "${merge_base}" HEAD)

# ── Section 1: clang-format (C / C++) ─────────────────────────────────────────
_header "clang-format — C/C++ style check"

if ! command -v clang-format > /dev/null 2>&1; then
    _info "clang-format not found — skipping (install: apt install clang-format)"
elif [[ ${#c_files[@]} -eq 0 ]]; then
    _info "No C/C++ files changed — skipping"
else
    cf_fail=0
    for f in "${c_files[@]}"; do
        if ! clang-format --dry-run --Werror --style="${CLANG_FORMAT_STYLE}" \
                          "$f" 2>/dev/null; then
            _err "${f} — needs reformatting (run: clang-format -i --style=${CLANG_FORMAT_STYLE} ${f})"
            cf_fail=1
        fi
    done
    if [[ $cf_fail -eq 0 ]]; then
        _ok "${#c_files[@]} file(s) match clang-format style"
    else
        overall=1
    fi
fi

# ── Section 2: shellcheck (Bash / shell scripts) ──────────────────────────────
_header "shellcheck — shell script style check"

if ! command -v shellcheck > /dev/null 2>&1; then
    _info "shellcheck not found — skipping (install: apt install shellcheck)"
elif [[ ${#sh_files[@]} -eq 0 ]]; then
    _info "No shell scripts changed — skipping"
else
    sc_fail=0
    for f in "${sh_files[@]}"; do
        if ! shellcheck "$f"; then
            _err "${f} — shellcheck reported issues (see above)"
            sc_fail=1
        fi
    done
    if [[ $sc_fail -eq 0 ]]; then
        _ok "${#sh_files[@]} script(s) passed shellcheck"
    else
        overall=1
    fi
fi

# ── Section 3: diff-size gate ─────────────────────────────────────────────────
_header "Diff-size gate — reviewability check"

# Count added + deleted lines per file (exclude blank / context lines).
# git diff --stat output looks like: "path/to/file | 42 ++++----"
per_file_fail=0
total_lines=0

while IFS= read -r line; do
    # Extract the filename and the ±number
    # Format: " src/foo.c  |  42 ++-"
    file_part=$(echo "$line" | awk -F'|' '{print $1}' | xargs)
    change_part=$(echo "$line" | awk -F'|' '{print $2}')
    num=$(echo "$change_part" | grep -oE '[0-9]+' | head -1 || true)
    [[ -z "$num" ]] && continue
    total_lines=$(( total_lines + num ))
    if (( num > MAX_LINES_PER_FILE )); then
        _err "${file_part}: ${num} lines changed — exceeds per-file limit of ${MAX_LINES_PER_FILE}." \
             "Split this change into smaller commits."
        per_file_fail=1
    fi
done < <(git diff --stat "${merge_base}" HEAD | grep '|' | grep -v 'changed,')

if [[ $per_file_fail -eq 0 ]]; then
    _ok "All individual files within ${MAX_LINES_PER_FILE}-line per-file limit"
else
    overall=1
fi

if (( total_lines > MAX_DIFF_LINES )); then
    _err "Total diff is ${total_lines} lines — exceeds ${MAX_DIFF_LINES}-line limit." \
         "Large diffs make it impossible to review code quality thoroughly." \
         "Break this PR into smaller, independently-mergeable pieces."
    overall=1
else
    _ok "Total diff ${total_lines} lines — within ${MAX_DIFF_LINES}-line limit"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
if [[ $overall -eq 0 ]]; then
    echo "RESULT: PASS — all style checks passed. Proceed to code review step 2."
else
    echo "RESULT: FAIL — fix the issues above before proceeding to code review." >&2
fi

exit $overall
