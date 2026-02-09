# tools

Standalone utilities (CLI/scripts) for maintaining agent workflows.

Available:
- `receipt_lint.py` — validates receipt JSON files against Swarmkit's required fields
- `risk_scan.py` — scans git diffs for high-risk path and line-level changes
- `task_broker.py` — generates agent-ready implementation briefs from GitHub issues

Example:
- `python3 tools/task_broker.py --repo RedLynx101/swarmkit --issue 8 --out docs/briefs/issue-8.md`
- `python3 tools/task_broker.py --issue-url https://github.com/RedLynx101/swarmkit/issues/8`

Tests:
- `python3 -m unittest discover -s tools -p 'test_*.py'`

Planned:
- suspicious-change scanner
