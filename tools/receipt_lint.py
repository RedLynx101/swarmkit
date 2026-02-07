#!/usr/bin/env python3
"""Validate Swarmkit receipt JSON files.

Deliberately dependency-free so it can run in minimal CI environments.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

ISO_8601_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class ReceiptError(Exception):
    pass


def _require(condition: bool, msg: str) -> None:
    if not condition:
        raise ReceiptError(msg)


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_receipt(payload: dict[str, Any], source: str) -> None:
    required = ["version", "goal", "changes", "verification", "timestamp", "actor"]
    for key in required:
        _require(key in payload, f"{source}: missing required field '{key}'")

    _require(payload["version"] == "1.0", f"{source}: version must be '1.0'")
    _require(_is_nonempty_string(payload["goal"]), f"{source}: goal must be a non-empty string")
    _require(_is_nonempty_string(payload["actor"]), f"{source}: actor must be a non-empty string")

    changes = payload["changes"]
    _require(isinstance(changes, list) and len(changes) > 0, f"{source}: changes must be a non-empty list")
    for idx, change in enumerate(changes, start=1):
        _require(_is_nonempty_string(change), f"{source}: changes[{idx}] must be a non-empty string")

    verification = payload["verification"]
    _require(
        isinstance(verification, list) and len(verification) > 0,
        f"{source}: verification must be a non-empty list",
    )
    for idx, step in enumerate(verification, start=1):
        _require(isinstance(step, dict), f"{source}: verification[{idx}] must be an object")
        _require(_is_nonempty_string(step.get("command")), f"{source}: verification[{idx}].command required")
        _require(_is_nonempty_string(step.get("expect")), f"{source}: verification[{idx}].expect required")

    timestamp = payload["timestamp"]
    _require(_is_nonempty_string(timestamp), f"{source}: timestamp must be a non-empty string")
    _require(bool(ISO_8601_UTC.match(timestamp)), f"{source}: timestamp must be ISO8601 UTC (YYYY-MM-DDTHH:MM:SSZ)")
    try:
        dt.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ReceiptError(f"{source}: invalid timestamp value: {exc}") from exc



def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReceiptError(f"{path}: invalid JSON ({exc})") from exc
    _require(isinstance(data, dict), f"{path}: root JSON value must be an object")
    return data



def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Swarmkit receipt JSON files")
    parser.add_argument("paths", nargs="+", help="Receipt JSON file(s) to validate")
    args = parser.parse_args()

    failures = 0
    for raw in args.paths:
        path = Path(raw)
        if not path.exists():
            print(f"FAIL {path}: file not found", file=sys.stderr)
            failures += 1
            continue
        try:
            payload = load_json(path)
            validate_receipt(payload, str(path))
            print(f"PASS {path}")
        except ReceiptError as exc:
            print(f"FAIL {exc}", file=sys.stderr)
            failures += 1

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
