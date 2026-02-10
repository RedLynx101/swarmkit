# Issue Briefs (Task Broker)

To make agent contributions high-quality, issues should read like a work order.

## Template
- Goal
- Non-goals
- Acceptance criteria (testable)
- Files likely touched
- Safety constraints
- How to verify

## Why
Agents can implement quickly, but need tight intent and verification.

## CLI helper
Use the task broker utility to generate a draft brief from an existing issue:

```bash
python3 tools/task_broker.py --repo RedLynx101/swarmkit --issue 8 --out docs/briefs/issue-8.md
```

It reads issue metadata/body and maps common sections into the template above, with sensible defaults when issue text is incomplete.
