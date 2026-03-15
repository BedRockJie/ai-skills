#!/usr/bin/env python3

from __future__ import annotations

import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


PATH_RULES: list[tuple[str, re.Pattern[str], str]] = [
    ("high", re.compile(r"(^|/)(include|public|api)/"), "public header or API surface changed"),
    ("high", re.compile(r"(^|/)(auth|security|crypto|tls|ssl)/"), "security-sensitive path changed"),
    ("high", re.compile(r"(^|/)(build|cmake|toolchain|packaging|scripts)/"), "build or packaging path changed"),
    ("high", re.compile(r"(^|/)(allocator|memory|pool)/"), "memory-management path changed"),
    ("medium", re.compile(r"(^|/)(test|tests|testing|fixtures?)/"), "test path changed"),
]

CONTENT_RULES: list[tuple[str, re.Pattern[str], str]] = [
    ("high", re.compile(r"\bextern\b|\b__attribute__\b|\bvisibility\b"), "symbol visibility or ABI-related code changed"),
    ("high", re.compile(r"\b(pthread_|std::thread|std::mutex|std::atomic|futex)\b"), "concurrency primitive changed"),
    ("high", re.compile(r"\b(malloc|calloc|realloc|free|new|delete)\b"), "ownership or allocation behavior changed"),
    ("high", re.compile(r"\b(exec|system|popen|fork|clone)\b"), "process execution behavior changed"),
    ("medium", re.compile(r"\b(json|yaml|protobuf|serialize|deserialize)\b", re.IGNORECASE), "serialization or wire-format code changed"),
    ("medium", re.compile(r"\berrno\b|\bstrerror\b|\breturn\s+-1\b"), "error propagation logic changed"),
]


def run_git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def main() -> int:
    base_ref = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    repo_root = Path(__file__).resolve().parents[2]

    try:
        merge_base = run_git(repo_root, "merge-base", "HEAD", base_ref)
        changed_names = run_git(repo_root, "diff", "--name-only", merge_base, "HEAD").splitlines()
        diff_text = run_git(repo_root, "diff", merge_base, "HEAD")
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: git command failed: {exc}", file=sys.stderr)
        return 1

    risk_buckets: dict[str, list[str]] = defaultdict(list)

    for name in changed_names:
        for level, pattern, reason in PATH_RULES:
            if pattern.search(name):
                risk_buckets[level].append(f"{reason}: {name}")

    for level, pattern, reason in CONTENT_RULES:
        if pattern.search(diff_text):
            risk_buckets[level].append(reason)

    print("RISK SUMMARY:")
    if not any(risk_buckets.values()):
        print("- low: no predefined high-risk indicators matched")
        return 0

    for level in ("high", "medium", "low"):
        reasons = sorted(set(risk_buckets[level]))
        if not reasons:
            continue
        for reason in reasons:
            print(f"- {level}: {reason}")

    print("AI REVIEW INPUT:")
    print("- focus on the high-risk items above, not on formatting or build failures")
    print("- verify tests and error paths match the changed risk surface")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
