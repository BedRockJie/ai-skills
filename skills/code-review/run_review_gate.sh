#!/usr/bin/env bash

set -euo pipefail

BASE_REF="${1:-origin/main}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel)"
BUILD_COMMAND="${BUILD_COMMAND:-}"
CLANG_TIDY_COMMAND="${CLANG_TIDY_COMMAND:-}"
CPPCHECK_COMMAND="${CPPCHECK_COMMAND:-}"

overall=0

header() { printf '\n=== %s ===\n' "$*"; }
ok() { printf '  [PASS] %s\n' "$*"; }
info() { printf '  [INFO] %s\n' "$*"; }
err() { printf '  [FAIL] %s\n' "$*" >&2; overall=1; }

run_optional_command() {
    local label="$1"
    local command="$2"
    if [[ -z "$command" ]]; then
        info "${label} not configured - skipping"
        return 0
    fi
    if bash -lc "$command"; then
        ok "${label} passed"
        return 0
    fi
    err "${label} failed"
    return 1
}

detect_build_command() {
    if [[ -n "$BUILD_COMMAND" ]]; then
        printf '%s' "$BUILD_COMMAND"
        return 0
    fi
    if [[ -x "${REPO_ROOT}/build.sh" ]]; then
        printf './build.sh'
        return 0
    fi
    if [[ -f "${REPO_ROOT}/Makefile" || -f "${REPO_ROOT}/makefile" ]]; then
        printf 'make -j$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4)'
        return 0
    fi
    return 1
}

python_cmd=""
if command -v python3 > /dev/null 2>&1; then
    python_cmd="python3"
elif command -v python > /dev/null 2>&1; then
    python_cmd="python"
else
    printf 'ERROR: python3 or python is required for code-review scripts.\n' >&2
    exit 1
fi

header "Stage 1 - style gate"
if ! bash "${SCRIPT_DIR}/run_style_checks.sh" "$BASE_REF"; then
    overall=1
fi

header "Stage 2 - build gate"
if build_command=$(detect_build_command); then
    if bash -lc "$build_command"; then
        ok "Build command passed: ${build_command}"
    else
        err "Build command failed: ${build_command}"
    fi
else
    err "No build command configured. Set BUILD_COMMAND or provide a repo-level build.sh/Makefile."
fi

header "Stage 2 - optional static analyzers"
run_optional_command "clang-tidy" "$CLANG_TIDY_COMMAND" || true
run_optional_command "cppcheck" "$CPPCHECK_COMMAND" || true

header "Stage 2 - generic rule scan"
if "$python_cmd" "${SCRIPT_DIR}/check_code_review_rules.py" "$BASE_REF"; then
    ok "Rule scan completed without blocker findings"
else
    err "Rule scan reported blocker findings"
fi

header "Stage 3 - change risk summary"
"$python_cmd" "${SCRIPT_DIR}/check_change_risk.py" "$BASE_REF" || err "Risk summary generation failed"

printf '\n'
if [[ $overall -eq 0 ]]; then
    printf 'RESULT: PASS - deterministic review gates passed. AI review can focus on residual design risks.\n'
else
    printf 'RESULT: FAIL - deterministic review gates did not pass. Fix these issues before AI review.\n' >&2
fi

exit "$overall"
