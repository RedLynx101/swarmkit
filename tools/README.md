# tools

Standalone utilities (CLI/scripts) for maintaining agent workflows.

Available:
- `receipt_lint.py` — validates receipt JSON files against Swarmkit's required fields
- `risk_scan.py` — scans git diffs for high-risk path and line-level changes
- `task_broker.py` — generates agent-ready implementation briefs from GitHub issues

`risk_scan.py` highlights:
- dependency manifests (`requirements.txt`, `pyproject.toml`, `package.json`, lockfiles, etc.)
- GitHub workflow edits (`.github/workflows/*`)
- added diff lines introducing network calls or process/shell execution

Example:
- `python3 tools/risk_scan.py --diff-ref HEAD~1..HEAD`
- `python3 tools/risk_scan.py --diff-ref origin/main..HEAD --fail-on-findings`

Example:
- `python3 tools/task_broker.py --repo RedLynx101/swarmkit --issue 8 --out docs/briefs/issue-8.md`
- `python3 tools/task_broker.py --issue-url https://github.com/RedLynx101/swarmkit/issues/8`

Tests:
- `python3 -m unittest discover -s tools -p 'test_*.py'`

Planned:
- suspicious-change scanner
