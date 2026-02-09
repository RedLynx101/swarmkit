#!/usr/bin/env python3
"""task_broker.py

Generate an agent-ready implementation brief from a GitHub issue.

Input options:
1) --issue-json <path> (supports "-" for stdin)
2) --repo owner/name --issue <number> (uses gh CLI: gh issue view --json ...)

Output:
- Markdown brief to stdout or --out file.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class IssueData:
    number: int
    title: str
    body: str
    url: str
    labels: list[str]


HEADING_ALIASES: dict[str, list[str]] = {
    "goal": ["goal", "objective", "outcome"],
    "non_goals": ["non-goals", "non goals", "out of scope", "not in scope"],
    "acceptance": ["acceptance criteria", "acceptance", "done when", "definition of done"],
    "files": ["files likely touched", "files", "areas impacted", "paths"],
    "safety": ["safety constraints", "safety", "security constraints", "constraints"],
    "verify": ["how to verify", "verification", "test plan", "validation"],
}


SECTION_ORDER = ["goal", "non_goals", "acceptance", "files", "safety", "verify"]


DEFAULTS = {
    "goal": "- Deliver the requested issue outcome with minimal scope and clear verification.",
    "non_goals": "- Avoid unrelated refactors, style-only edits, or broad architecture changes.",
    "acceptance": "- [ ] The implementation meets issue requirements and is reviewable.",
    "files": "- Identify exact files once implementation starts.",
    "safety": "- Do not introduce secrets, unsafe shell execution, or unnecessary dependency risk.",
    "verify": "- Run relevant checks and include command/output in PR summary.",
}


def _normalize_heading(text: str) -> str:
    t = text.strip().lower().strip(":# ")
    t = re.sub(r"\s+", " ", t)
    for key, aliases in HEADING_ALIASES.items():
        if t in aliases:
            return key
    return ""


def _parse_sections(body: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {k: [] for k in SECTION_ORDER}
    current = ""

    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        m = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", line)
        if m:
            key = _normalize_heading(m.group(1))
            current = key if key else ""
            continue

        bullet = re.match(r"^\s*[-*]\s+(.+?)\s*$", line)
        if bullet and not current:
            maybe_key = _normalize_heading(bullet.group(1))
            if maybe_key:
                current = maybe_key
                continue

        if current:
            sections[current].append(line)

    out: dict[str, str] = {}
    for key in SECTION_ORDER:
        content = "\n".join(sections[key]).strip()
        if content:
            out[key] = content
    return out


def _extract_labels(raw: Any) -> list[str]:
    labels: list[str] = []
    if isinstance(raw, list):
        for l in raw:
            if isinstance(l, dict) and isinstance(l.get("name"), str):
                labels.append(l["name"])
            elif isinstance(l, str):
                labels.append(l)
    return labels


def parse_issue_json(payload: dict[str, Any]) -> IssueData:
    number = payload.get("number")
    title = payload.get("title")
    body = payload.get("body") or ""
    url = payload.get("url") or payload.get("html_url") or ""
    labels = _extract_labels(payload.get("labels", []))

    if not isinstance(number, int):
        raise ValueError("Issue JSON missing integer 'number'.")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Issue JSON missing non-empty 'title'.")
    if not isinstance(body, str):
        raise ValueError("Issue JSON field 'body' must be a string.")
    if not isinstance(url, str):
        raise ValueError("Issue JSON field 'url' must be a string.")

    return IssueData(number=number, title=title.strip(), body=body, url=url.strip(), labels=labels)


def load_issue_from_file(path: str) -> IssueData:
    if path == "-":
        payload = json.load(sys.stdin)
    else:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return parse_issue_json(payload)


def load_issue_from_gh(repo: str, issue_number: int) -> IssueData:
    if not shutil.which("gh"):
        raise RuntimeError("gh CLI not found on PATH.")

    cmd = [
        "gh",
        "issue",
        "view",
        str(issue_number),
        "--repo",
        repo,
        "--json",
        "number,title,body,url,labels",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        msg = res.stderr.strip() or res.stdout.strip() or f"gh failed with code {res.returncode}"
        raise RuntimeError(msg)

    payload = json.loads(res.stdout)
    return parse_issue_json(payload)


def render_markdown(issue: IssueData) -> str:
    sections = _parse_sections(issue.body)

    def section(key: str) -> str:
        return sections.get(key, DEFAULTS[key]).strip()

    labels = ", ".join(issue.labels) if issue.labels else "(none)"

    return f"""# Agent Brief: #{issue.number} {issue.title}

Source issue: {issue.url or '(missing URL)'}
Labels: {labels}

## Goal
{section('goal')}

## Non-goals
{section('non_goals')}

## Acceptance criteria (testable)
{section('acceptance')}

## Files likely touched
{section('files')}

## Safety constraints
{section('safety')}

## How to verify
{section('verify')}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a task brief from a GitHub issue")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--issue-json", help="Path to issue JSON file, or '-' for stdin")
    src.add_argument("--issue", type=int, help="Issue number (requires --repo)")
    parser.add_argument("--repo", help="owner/repo (required with --issue)")
    parser.add_argument("--out", help="Write output markdown to a file")

    args = parser.parse_args()

    try:
        if args.issue_json:
            issue = load_issue_from_file(args.issue_json)
        else:
            if not args.repo:
                parser.error("--repo is required when using --issue")
            issue = load_issue_from_gh(args.repo, args.issue)

        output = render_markdown(issue)
        if args.out:
            out_path = Path(args.out)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)

        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
