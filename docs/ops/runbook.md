# Maintainer Runbook

## Maintainer loop
- Triage issues → label → clarify acceptance criteria.
- Slice tasks into `agent-task` issues.
- Review PRs with CI + receipts.

## Merge policy
- PRs only.
- CI required.
- At least 1 review.
- Risk scan findings (`tools/risk_scan.py`) must be reviewed before merge if CI flags high-risk changes.

## PR preflight (local)
Run these before pushing:

```bash
PYTHONPATH=tools python3 -m unittest tools/test_*.py
python3 tools/risk_scan.py --base origin/main --head HEAD --fail-on high
```

If risk scan fails, include a reviewer note describing why the flagged change is intentional.
