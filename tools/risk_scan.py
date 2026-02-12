#!/usr/bin/env python3
"""Flag high-risk code changes between two git refs.

This scanner is intentionally lightweight and dependency-free so it can run in CI.
It is conservative: findings require human review before merge.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Finding:
    file: str
    line: int | None
    severity: str
    reason: str
    snippet: str | None = None


PATH_RULES: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"^\.github/workflows/.*\.ya?ml$"), "medium", "CI/workflow pipeline changed"),
    (re.compile(r"(^|/)Dockerfile$|(^|/)docker-compose\.ya?ml$"), "high", "Container runtime config changed"),
    (re.compile(r"(^|/)Makefile$"), "medium", "Build orchestration changed"),
    (re.compile(r"(^|/)requirements(\.txt|/.*\.txt)?$"), "high", "Python dependency manifest changed"),
    (re.compile(r"(^|/)pyproject\.toml$|(^|/)poetry\.lock$|(^|/)package(-lock)?\.json$|(^|/)pnpm-lock\.ya?ml$|(^|/)yarn\.lock$"), "high", "Dependency lock/manifest changed"),
    (re.compile(r"(^|/)\.env(\.|$)"), "high", "Environment/secrets-related file changed"),
]

LINE_RULES: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"\b(subprocess\.(Popen|run|call)|os\.system|child_process\.|Runtime\.getRuntime\(\)\.exec)\b"), "high", "Shell command execution added"),
    (re.compile(r"\b(eval|exec)\s*\("), "high", "Dynamic code execution added"),
    (re.compile(r"\b(curl|wget)\b"), "medium", "Network fetch command added"),
    (re.compile(r"\b(requests\.|httpx\.|fetch\(|axios\.|urllib\.)"), "medium", "HTTP client usage added"),
    (re.compile(r"\b(chmod\s+777|setenforce\s+0|--privileged)\b"), "high", "Potentially unsafe privilege/config change"),
]


def run_git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout


def changed_files(base: str, head: str) -> list[str]:
    out = run_git(["diff", "--name-only", f"{base}..{head}"])
    return [line.strip() for line in out.splitlines() if line.strip()]


def is_excluded(path: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(p.search(path) for p in patterns)


def scan_paths(files: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for file in files:
        for pattern, severity, reason in PATH_RULES:
            if pattern.search(file):
                findings.append(Finding(file=file, line=None, severity=severity, reason=reason))
    return findings


def scan_added_lines(base: str, head: str, exclude: list[re.Pattern[str]] | None = None) -> list[Finding]:
    diff = run_git(["diff", "--unified=0", f"{base}..{head}"])
    findings: list[Finding] = []
    exclude = exclude or []

    current_file: str | None = None
    current_line: int | None = None

    hunk_re = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")

    for raw in diff.splitlines():
        line = raw.rstrip("\n")

        if line.startswith("+++ b/"):
            current_file = line[6:]
            current_line = None
            continue

        m = hunk_re.match(line)
        if m:
            current_line = int(m.group(1))
            continue

        if not line.startswith("+") or line.startswith("+++"):
            continue

        if current_file is None:
            continue
        if is_excluded(current_file, exclude):
            continue

        content = line[1:]
        for pattern, severity, reason in LINE_RULES:
            if pattern.search(content):
                findings.append(
                    Finding(
                        file=current_file,
                        line=current_line,
                        severity=severity,
                        reason=reason,
                        snippet=content[:200],
                    )
                )

        if current_line is not None:
            current_line += 1

    return findings


def format_finding(f: Finding) -> str:
    loc = f"{f.file}:{f.line}" if f.line is not None else f.file
    snippet = f"\n    + {f.snippet}" if f.snippet else ""
    return f"[{f.severity.upper()}] {loc} — {f.reason}{snippet}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan git diff for high-risk changes")
    parser.add_argument("--base", required=True, help="Base git ref (e.g., origin/main)")
    parser.add_argument("--head", required=True, help="Head git ref (e.g., HEAD)")
    parser.add_argument("--fail-on", choices=["high", "medium", "all"], default="high")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Regex path to exclude from scanning (repeatable)",
    )
    args = parser.parse_args()

    exclude_patterns = [re.compile(x) for x in args.exclude]

    files = changed_files(args.base, args.head)
    files = [f for f in files if not is_excluded(f, exclude_patterns)]
    if not files:
        print("risk-scan: no changed files")
        return 0

    findings = [*scan_paths(files), *scan_added_lines(args.base, args.head, exclude_patterns)]

    if not findings:
        print("risk-scan: no risky changes detected")
        return 0

    order = {"medium": 1, "high": 2}
    threshold = {"high": 2, "medium": 1, "all": 1}[args.fail_on]

    print("risk-scan: findings")
    for finding in findings:
        print(format_finding(finding))

    should_fail = any(order.get(f.severity, 0) >= threshold for f in findings)
    if should_fail:
        print("risk-scan: FAIL (review required)", file=sys.stderr)
        return 1

    print("risk-scan: PASS (findings below fail threshold)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
