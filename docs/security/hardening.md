# Repo Security Hardening Checklist

This is a practical checklist for maintainers of **agent-facing repos**.

## Baseline (do these first)

- **Protect the default branch**
  - Require PRs (no direct pushes)
  - Require review (at least 1)
  - Require status checks to pass
  - Require linear history (optional but recommended)

- **Secrets + credentials**
  - Enable GitHub secret scanning + push protection (if available)
  - Never commit real tokens/keys in examples
  - Prefer `.env.example` and documented env vars

- **Dependencies**
  - Pin toolchains and lockfiles (npm/pnpm/bun/pip) where relevant
  - Turn on Dependabot (or an equivalent) for critical ecosystems
  - Treat new dependencies as a risk surface: justify and keep minimal

- **CI guardrails**
  - Run CI on PRs (lint/test)
  - For any workflow that uses `pull_request_target`, document why and isolate permissions
  - Set workflow permissions to least-privilege (avoid `write-all`)

## Agent-specific hardening

- **Receipts required**
  - Require PRs to include: what changed, how to verify, and exact commands run
  - Prefer a `receipts/` folder or PR template section

- **Network + execution boundaries**
  - If you run untrusted code (agent tasks / plugins / scripts), sandbox it
  - Avoid running arbitrary community-submitted scripts in privileged environments

- **Supply chain awareness**
  - Assume prompt-injected or malicious contributions will happen
  - Review any changes that touch:
    - CI workflows
    - install scripts
    - package manager configs
    - credential handling

## Incident response (keep it simple)

- If a secret is leaked:
  1) Revoke/rotate immediately
  2) Audit recent commits and CI logs
  3) Document what happened (brief postmortem)
  4) Add a guardrail to prevent repeat

## Quick verification (suggested)

- Branch protection enabled on default branch
- CI required checks configured
- No broad workflow permissions
- Secret scanning enabled
- CONTRIBUTING mentions receipts + verification

### Local helper

Run the local baseline checker before pushing security-oriented changes:

```bash
python3 tools/security_checklist.py
```

This validates required security docs and ensures workflow files declare explicit `permissions` blocks.
