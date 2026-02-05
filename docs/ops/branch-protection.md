# Branch protection (recommended)

This repo is designed to be PR-only. The point of this document is to make the *expected* GitHub settings explicit.

## Main branch (`main`)

Recommended settings:
- Require a pull request before merging
  - Require approvals: **1+**
  - Dismiss stale approvals when new commits are pushed
  - Require review from Code Owners (see `.github/CODEOWNERS`)
- Require status checks to pass before merging
  - Require branches to be up to date before merging
  - Suggested required checks:
    - CI / test
    - Lint / format (if present)
    - Security / scan (if present)
- Require conversation resolution before merging
- Require signed commits (optional, but encouraged)
- Do not allow force pushes
- Do not allow deletions

## Tags / releases (optional)

If you publish release artifacts:
- Restrict who can create or delete tags

## Notes

GitHub settings live outside the repo. This document exists so maintainers can quickly verify the repo is configured safely.
