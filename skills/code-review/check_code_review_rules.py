#!/usr/bin/env python3

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Rule:
    tag: str
    name: str
    pattern: re.Pattern[str]
    message: str


RULES = [
    Rule(
        tag="blocker",
        name="dangerous_c_string_api",
        pattern=re.compile(r"\b(strcpy|strcat|sprintf|vsprintf|gets)\s*\("),
        message="unbounded or legacy string API - use a bounded alternative",
    ),
    Rule(
        tag="blocker",
        name="unsafe_tempfile_api",
        pattern=re.compile(r"\b(tmpnam|mktemp)\s*\("),
        message="unsafe temporary-file API - use mkstemp or a safer wrapper",
    ),
    Rule(
        tag="warning",
        name="process_execution",
        pattern=re.compile(r"\b(system|popen)\s*\("),
        message="process execution requires strict input validation and error handling",
    ),
    Rule(
        tag="warning",
        name="manual_memory_management",
        pattern=re.compile(r"\b(malloc|calloc|realloc|free|new|delete)\b"),
        message="manual memory management changed - verify ownership, failure paths, and cleanup",
    ),
    Rule(
        tag="warning",
        name="raw_threading",
        pattern=re.compile(r"\b(pthread_create|std::thread|std::mutex|pthread_mutex_lock|pthread_rwlock)\b"),
        message="concurrency primitive changed - verify ordering, lifetime, and shutdown behavior",
    ),
    Rule(
        tag="warning",
        name="unchecked_assert_usage",
        pattern=re.compile(r"\bassert\s*\("),
        message="assert usage changed - ensure runtime validation does not disappear in release builds",
    ),
]


def run_git(*args: str, repo_root: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def changed_files(repo_root: Path, base_ref: str) -> list[Path]:
    merge_base = run_git("merge-base", "HEAD", base_ref, repo_root=repo_root)
    names = run_git("diff", "--name-only", merge_base, "HEAD", repo_root=repo_root)
    files: list[Path] = []
    for name in names.splitlines():
        if not name:
            continue
        path = repo_root / name
        if path.is_file():
            files.append(path)
    return files


def relevant_file(path: Path) -> bool:
    return path.suffix.lower() in {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp"}


def changed_line_numbers(repo_root: Path, base_ref: str, rel_path: Path) -> set[int]:
    merge_base = run_git("merge-base", "HEAD", base_ref, repo_root=repo_root)
    diff_text = run_git(
        "diff",
        "--unified=0",
        merge_base,
        "HEAD",
        "--",
        str(rel_path),
        repo_root=repo_root,
    )
    lines: set[int] = set()
    current_line = 0
    for raw_line in diff_text.splitlines():
        if raw_line.startswith("@@"):
            match = re.search(r"\+(\d+)(?:,(\d+))?", raw_line)
            if not match:
                continue
            current_line = int(match.group(1))
            continue
        if raw_line.startswith("+++") or raw_line.startswith("---"):
            continue
        if raw_line.startswith("+"):
            lines.add(current_line)
            current_line += 1
            continue
        if raw_line.startswith(" "):
            current_line += 1
    return lines


def scan_file(path: Path, repo_root: Path, changed_lines: set[int]) -> list[str]:
    findings: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = path.relative_to(repo_root)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if line_no not in changed_lines:
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        for rule in RULES:
            if rule.pattern.search(line):
                findings.append(
                    f"{rule.tag}: [{rel}:{line_no}] {rule.message} ({rule.name})"
                )
    return findings


def main() -> int:
    base_ref = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    repo_root = Path(__file__).resolve().parents[2]

    try:
        files = [path for path in changed_files(repo_root, base_ref) if relevant_file(path)]
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: git command failed: {exc}", file=sys.stderr)
        return 1

    if not files:
        print("INFO: no changed C/C++ files to scan")
        return 0

    findings: list[str] = []
    for path in files:
        rel = path.relative_to(repo_root)
        lines = changed_line_numbers(repo_root, base_ref, rel)
        findings.extend(scan_file(path, repo_root, lines))

    if not findings:
        print("INFO: no regex-detectable review findings in changed C/C++ files")
        return 0

    blocker_count = 0
    for finding in findings:
        print(finding)
        if finding.startswith("blocker:"):
            blocker_count += 1

    if blocker_count:
        print(f"INFO: {blocker_count} blocker finding(s) detected")
        return 1

    print("INFO: warnings/questions detected; continue with targeted review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
