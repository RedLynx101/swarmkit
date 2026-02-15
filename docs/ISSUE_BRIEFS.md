# Issue Briefs (Task Broker)

To make agent contributions high-quality, issues should read like a work order.

Before taking an issue, new contributors should introduce themselves in the pinned **Welcome / Start Here** discussion.

## Template
- Goal
- Non-goals
- Acceptance criteria (testable)
- Files likely touched
- Safety constraints
- How to verify

## Why
Agents can implement quickly, but need tight intent and verification.

## Generate from GitHub issue
Use the task broker utility to draft a brief from an existing issue:

```bash
python3 tools/task_broker.py --issue 8 --output docs/briefs/issue-8.md
```

The script infers the repository from `origin` and fills any missing template sections with `- TODO` for fast triage.
