#!/usr/bin/env python3
"""Flag risky file changes in a diff.

Exit codes:
- 0: no risky paths
- 2: risky paths detected (or 0 with --warn-only)
- 1: usage/runtime error
"""

from __future__ import annotations

import argparse
from pathlib import PurePosixPath
import re
import subprocess
import sys
from typing import Iterable

RISK_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("workflows", re.compile(r"^\.github/workflows/.+")),
    ("tooling", re.compile(r"^tools/.+")),
    ("dependency-manifests", re.compile(r"(^|/)(requirements(-dev)?\.txt|pyproject\.toml|package(-lock)?\.json|pnpm-lock\.yaml|poetry\.lock)$")),
    ("runtime-scripts", re.compile(r"(^|/)(Dockerfile|docker-compose\.ya?ml|Makefile|.*\.sh|.*\.ps1)$")),
]


def _normalize(paths: Iterable[str]) -> list[str]:
    out: list[str] = []
    for p in paths:
        p = p.strip()
        if not p:
            continue
        out.append(PurePosixPath(p).as_posix())
    return out


def _git_diff_names(base: str, head: str) -> list[str]:
    cmd = ["git", "diff", "--name-only", base, head]
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git diff failed")
    return _normalize(proc.stdout.splitlines())


def classify(paths: Iterable[str]) -> dict[str, list[str]]:
    matched: dict[str, list[str]] = {}
    for p in _normalize(paths):
        for label, pattern in RISK_RULES:
            if pattern.search(p):
                matched.setdefault(label, []).append(p)
    return matched


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="git base ref/sha for diff")
    parser.add_argument("--head", help="git head ref/sha for diff")
    parser.add_argument(
        "files",
        nargs="*",
        help="explicit file paths to scan (optional if --base/--head provided)",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="do not fail exit code when risky paths are found",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if bool(args.base) ^ bool(args.head):
        print("error: --base and --head must be provided together", file=sys.stderr)
        return 1

    try:
        files = _git_diff_names(args.base, args.head) if args.base and args.head else _normalize(args.files)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not files:
        print("risk-scan: no files to scan")
        return 0

    matched = classify(files)
    if not matched:
        print("risk-scan: PASS (no risky paths)")
        return 0

    print("risk-scan: FLAGGED risky paths:")
    for label in sorted(matched):
        print(f"- {label}:")
        for p in sorted(set(matched[label])):
            print(f"  - {p}")

    return 0 if args.warn_only else 2


if __name__ == "__main__":
    sys.exit(main())
