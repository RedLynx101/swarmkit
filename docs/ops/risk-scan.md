# High-risk change scan

Swarmkit CI runs `tools/risk_scan.py` on pull requests and fails when high-risk paths are touched.

Current flagged categories:
- GitHub workflow changes (`.github/workflows/**`)
- Tooling changes (`tools/**`)
- Dependency manifests (`requirements*.txt`, `pyproject.toml`, lockfiles)
- Runtime scripts (`Dockerfile`, `docker-compose*.yml`, `Makefile`, `*.sh`, `*.ps1`)

## Why this gate exists

These files can change execution behavior, supply chain posture, or CI policy. A failing risk scan is a review signal, not an accusation.

## Maintainer workflow

When scan fails in CI:
1. Confirm the risky change is expected for the PR scope.
2. Ensure at least one human maintainer review before merge.
3. Require passing checks after revisions.

## Local usage

Scan explicit paths:

```bash
python3 tools/risk_scan.py .github/workflows/ci.yml docs/ROADMAP.md
```

Scan a git diff range:

```bash
python3 tools/risk_scan.py --base <base-sha> --head <head-sha>
```
