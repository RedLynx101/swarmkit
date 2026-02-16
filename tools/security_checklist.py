#!/usr/bin/env python3
"""Local security checklist verifier for swarmkit-like repos."""

from __future__ import annotations

from pathlib import Path
import sys

REQUIRED_FILES = [
    "SECURITY.md",
    "docs/security/hardening.md",
    ".github/CODEOWNERS",
]


def check_required_files(root: Path) -> list[str]:
    return [p for p in REQUIRED_FILES if not (root / p).exists()]


def find_workflows_missing_permissions(root: Path) -> list[str]:
    workflows_dir = root / ".github" / "workflows"
    if not workflows_dir.exists():
        return []

    missing: list[str] = []
    for path in sorted(workflows_dir.glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        if "permissions:" not in text:
            missing.append(str(path.relative_to(root)))
    return missing


def main() -> int:
    root = Path.cwd()

    missing_files = check_required_files(root)
    missing_permissions = find_workflows_missing_permissions(root)

    if missing_files:
        print("FAIL required security files missing:")
        for path in missing_files:
            print(f"- {path}")

    if missing_permissions:
        print("FAIL workflow files missing explicit permissions block:")
        for path in missing_permissions:
            print(f"- {path}")

    if missing_files or missing_permissions:
        return 1

    print("PASS security checklist baseline")
    print("NOTE branch protection + secret scanning should be verified in GitHub settings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
