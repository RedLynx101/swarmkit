# tools

Standalone utilities (CLI/scripts) for maintaining agent workflows.

Available:
- `receipt_lint.py` — validates receipt JSON files against Swarmkit's required fields
- `risk_scan.py` — flags potentially risky diff paths (workflows, tooling, deps, runtime scripts)
- `task_broker.py` — converts a GitHub issue into an agent-ready brief template (`--fail-on-missing` for strict mode)
  - accepts `--issue` as: `8`, `#8`, or full URL (`https://github.com/<owner>/<repo>/issues/8`)
