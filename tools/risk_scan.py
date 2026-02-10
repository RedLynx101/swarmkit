#!/usr/bin/env python3
"""Scan git diffs for potentially risky changes.

Flags:
- dependency manifest changes
- workflow changes
- added lines that introduce network calls or shell/process execution

Dependency-free by design for CI portability.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass


DEPENDENCY_FILES = {
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "Pipfile",
    "Pipfile.lock",
    "poetry.lock",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "Cargo.lock",
}

WORKFLOW_PREFIXES = (
    ".github/workflows/",
)

CONTENT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("network-call", re.compile(r"\b(requests\.|httpx\.|urllib\.|fetch\(|axios\(|curl\s+https?://|wget\s+https?://)")),
    ("process-exec", re.compile(r"\b(subprocess\.|os\.system\(|exec\(|spawn\(|child_process\.|Runtime\.getRuntime\(\)\.exec)")),
    ("shell-script", re.compile(r"\b(sh\s+-c|bash\s+-c|powershell(\.exe)?\s+-[Cc]ommand)")),
]


@dataclass(frozen=True)
class Finding:
    kind: str
    location: str
    detail: str


def _run_git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout


def scan_paths(diff_ref: str) -> list[Finding]:
    out = _run_git(["diff", "--name-only", diff_ref])
    findings: list[Finding] = []
    for path in [p.strip() for p in out.splitlines() if p.strip()]:
        filename = path.split("/")[-1]
        if filename in DEPENDENCY_FILES:
            findings.append(Finding("dependency-file", path, "Dependency manifest changed"))
        if path.startswith(WORKFLOW_PREFIXES):
            findings.append(Finding("workflow-change", path, "GitHub workflow changed"))
    return findings


def scan_content(diff_ref: str) -> list[Finding]:
    out = _run_git(["diff", "-U0", diff_ref])
    findings: list[Finding] = []
    current_file = "unknown"

    for raw_line in out.splitlines():
        if raw_line.startswith("+++ b/"):
            current_file = raw_line[6:]
            continue
        if not raw_line.startswith("+") or raw_line.startswith("+++"):
            continue

        line = raw_line[1:]
        for kind, pattern in CONTENT_PATTERNS:
            if pattern.search(line):
                findings.append(Finding(kind, current_file, line.strip()))
                break

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan diff for risky changes")
    parser.add_argument("--diff-ref", default="HEAD~1..HEAD", help="Git diff ref/range to scan")
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Return exit code 1 when any findings exist",
    )
    args = parser.parse_args()

    try:
        findings = [*scan_paths(args.diff_ref), *scan_content(args.diff_ref)]
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not findings:
        print(f"PASS no risky changes detected in {args.diff_ref}")
        return 0

    print(f"RISK findings in {args.diff_ref}:")
    for f in findings:
        print(f"- [{f.kind}] {f.location}: {f.detail}")

    return 1 if args.fail_on_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
