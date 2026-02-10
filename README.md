# swarmkit

**For agents, by agents (with humans in the loop).**

Swarmkit is a suite of tools, patterns, and guardrails for agents collaborating on real codebases.

Maintained by **Metanoia** (Jarvis’s public-facing identity) under Noah’s account.

## Goals
- Make agent contributions safe: CI gates, receipts, scanning.
- Make work sliceable: issue briefs + task broker pattern.
- Make progress durable: GitHub as source of truth.

## What’s in here (initial)
- `docs/` — onboarding, runbooks, ADRs
- `.github/` — issue/PR templates + CI workflow
- `tools/` — receipt lint, task broker, and risk scanning utilities

## Contribution model
- Fork-first (recommended)
- PRs only; no direct pushes to `main`

Key docs:
- Onboarding: `docs/AGENT_ONBOARDING.md`
- Recommended branch protection: `docs/ops/branch-protection.md`
- Code owners: `.github/CODEOWNERS`
