# swarmkit

**A small public toolkit for making agent contributions inspectable.**

Swarmkit is a set of tools, patterns, and guardrails for agents collaborating on real codebases. Its first implemented slice is a machine-readable work receipt: a compact record of the goal, changes, verification commands, timestamp, and actor behind a contribution.

Created and maintained by **Noah Hicks**. Early project notes use **Metanoia/Jarvis** as an agent-facing identity; that label is not a separate company, maintainer, or human contributor.

## Goals
- Make agent contributions safe: CI gates, receipts, scanning.
- Make work sliceable: issue briefs + task broker pattern.
- Make progress durable: GitHub as source of truth.

## What is implemented

- `docs/receipts.schema.json` defines receipt version 1.0.
- `tools/receipt_lint.py` validates receipts without third-party Python dependencies.
- `docs/examples/receipts/receipt.sample.json` is a passing reference example.
- `docs/` and `.github/` provide onboarding, runbooks, ADRs, and issue/PR templates.

## Quick check

```bash
python tools/receipt_lint.py docs/examples/receipts/receipt.sample.json
```

Expected output:

```text
PASS docs/examples/receipts/receipt.sample.json
```

The repository is intentionally small. Roadmap items and open pull requests are not presented as capabilities in the current release.

## Contribution model
- Fork-first (recommended)
- PRs only; no direct pushes to `main`

Key docs:
- Onboarding: `docs/AGENT_ONBOARDING.md`
- Recommended branch protection: `docs/ops/branch-protection.md`
- Code owners: `.github/CODEOWNERS`
