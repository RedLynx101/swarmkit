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
# by number
python3 tools/task_broker.py --issue 8 --output docs/briefs/issue-8.md

# by hash reference
python3 tools/task_broker.py --issue '#8' --output docs/briefs/issue-8.md

# by full GitHub URL (repo inferred from URL)
python3 tools/task_broker.py --issue https://github.com/RedLynx101/swarmkit/issues/8 --output docs/briefs/issue-8.md
```

The script infers the repository from `origin` (or from the issue URL), fills missing template sections with `- TODO`, and includes a missing-sections note. It recognizes both Markdown headings (`## Goal`) and common template-style headings (`**Goal**`, `Goal:`/`Goal -`, including bulleted forms like `- **Goal:** ...`), including inline values (`**Goal** Ship parser`, `Goal:Ship parser`) and common aliases (`Out of scope` → `Non-goals`, `Verification`/`Test plan` → `How to verify`). Use `--fail-on-missing` in CI/automation when you want strict failure on incomplete issue specs.
