#!/usr/bin/env python3
"""Run periodic maintenance tasks backed by marker files.

Pattern:
- keep a `*-last-run.json` marker in-repo
- skip expensive work until interval is due
- update marker only on success
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


class MarkerError(RuntimeError):
    pass


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def parse_timestamp(raw: str) -> dt.datetime:
    try:
        return dt.datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.UTC)
    except ValueError as exc:
        raise MarkerError(f"invalid marker timestamp '{raw}' (expected YYYY-MM-DDTHH:MM:SSZ)") from exc


def load_marker(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MarkerError(f"{path}: invalid JSON ({exc})") from exc
    if not isinstance(payload, dict):
        raise MarkerError(f"{path}: marker root must be a JSON object")
    return payload


def is_due(marker: dict[str, Any], every_seconds: int, now: dt.datetime) -> bool:
    last_run = marker.get("last_run_utc")
    if not last_run:
        return True
    if not isinstance(last_run, str):
        raise MarkerError("marker field 'last_run_utc' must be a string")
    elapsed = (now - parse_timestamp(last_run)).total_seconds()
    return elapsed >= every_seconds


def write_marker(path: Path, now: dt.datetime, command: list[str]) -> None:
    payload = {
        "last_run_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_command": command,
        "version": 1,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_command(command: list[str]) -> int:
    proc = subprocess.run(command)
    return proc.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run maintenance command only when marker interval is due")
    parser.add_argument("--marker", required=True, help="Path to marker JSON (example: memory/x-last-run.json)")
    parser.add_argument("--every-hours", type=float, required=True, help="Run interval in hours")
    parser.add_argument("--force", action="store_true", help="Run regardless of marker timestamp")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run (prefix with --)")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.every_hours <= 0:
        raise SystemExit("--every-hours must be > 0")

    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise SystemExit("missing command; pass it after --")

    marker_path = Path(args.marker)
    every_seconds = int(args.every_hours * 3600)
    now = utc_now()

    try:
        marker = load_marker(marker_path)
        due = args.force or is_due(marker, every_seconds, now)
    except MarkerError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2

    if not due:
        print(f"SKIP {marker_path}: not due yet")
        return 0

    print(f"RUN {' '.join(command)}")
    rc = run_command(command)
    if rc != 0:
        print(f"FAIL command exited with {rc}", file=sys.stderr)
        return rc

    write_marker(marker_path, now, command)
    print(f"PASS marker updated: {marker_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
