#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


HEADER_PATTERN = re.compile(
    r"^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\([a-z0-9-]+\))?"
    r"!?:"
    r" [^\s].*$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate whether a commit message follows Conventional Commits."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--message", help="Commit message text to validate.")
    group.add_argument("--file", help="Path to a file containing the commit message.")
    group.add_argument(
        "--last-commit",
        action="store_true",
        help="Read the latest commit message from the current Git repository.",
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository path used with --last-commit. Defaults to the current directory.",
    )
    return parser.parse_args()


def read_message(args: argparse.Namespace) -> str:
    if args.message is not None:
        return args.message.strip()

    if args.last_commit:
        result = subprocess.run(
            ["git", "-C", args.repo, "log", "-1", "--pretty=%B"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    return Path(args.file).read_text(encoding="utf-8").strip()


def validate_message(message: str) -> tuple[bool, str]:
    if not message:
        return False, "Commit message must not be empty."

    header = message.splitlines()[0].strip()
    if not HEADER_PATTERN.fullmatch(header):
        return (
            False,
            "Invalid Conventional Commits header. Expected "
            "'type(optional-scope): description' or "
            "'type(optional-scope)!: description'.",
        )

    return True, f"Valid Conventional Commit: {header}"


def main() -> int:
    args = parse_args()

    try:
        message = read_message(args)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Failed to read commit message: {exc}", file=sys.stderr)
        return 1

    is_valid, output = validate_message(message)
    stream = sys.stdout if is_valid else sys.stderr
    print(output, file=stream)
    return 0 if is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
