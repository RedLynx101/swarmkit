#!/usr/bin/env python3
"""Verify critical repository baseline files exist."""

from __future__ import annotations

from pathlib import Path
import sys

REQUIRED_PATHS = [
    ".github/CODEOWNERS",
    ".github/PULL_REQUEST_TEMPLATE.md",
    "docs/AGENT_ONBOARDING.md",
    "docs/ISSUE_BRIEFS.md",
    ".github/DISCUSSION_TEMPLATE/start-here.yml",
    "docs/community/START_HERE_DISCUSSION.md",
]


def main() -> int:
    root = Path.cwd()
    missing = [p for p in REQUIRED_PATHS if not (root / p).exists()]

    if missing:
        print("FAIL missing required baseline files:")
        for path in missing:
            print(f"- {path}")
        return 1

    print("PASS baseline files present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
