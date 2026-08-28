# Security Self-Audit Checklist (Maintainers)

Use this before major releases and at least monthly.

## 1) Branch and review controls
- [ ] Default branch is protected.
- [ ] PRs required for merge to default branch.
- [ ] At least one approving review is required.
- [ ] Required status checks are up to date.

## 2) Workflow permissions
- [ ] GitHub Actions workflow permissions are least-privilege.
- [ ] No unnecessary `pull_request_target` workflows.
- [ ] No unreviewed workflow changes merged recently.

## 3) Secrets and credential exposure
- [ ] Secret scanning is enabled.
- [ ] No plaintext tokens/keys in recent commits.
- [ ] Example config files use placeholders only.

## 4) Dependency and supply chain checks
- [ ] Dependency updates are reviewed and intentional.
- [ ] New dependencies are justified in PR descriptions.
- [ ] CI passes on dependency-related changes.

## 5) Agent-specific guardrails
- [ ] PRs include verification commands / receipts.
- [ ] Risk scan findings reviewed for network/exec/deps changes.
- [ ] High-risk diffs have explicit maintainer sign-off.

## Fast command check

```bash
# local test baseline
python3 -m unittest discover -s tools -p 'test_*.py'

# quick risk scan against main
python3 tools/risk_scan.py --diff-ref main..HEAD
```
