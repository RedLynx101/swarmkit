# Receipts

A "receipt" is a small, verifiable record of what changed and how to confirm it.

Examples live in: `docs/examples/receipts/`

## In PRs
Include a section:
- What changed
- Why
- How to verify (commands + expected output)

## On disk (JSON schema)
For automation-friendly workflows, store machine-readable receipts as JSON and validate them in CI.

- Schema: `docs/receipts.schema.json`
- Linter: `tools/receipt_lint.py`
- Example: `docs/examples/receipts/receipt.sample.json`

Recommended location for real run receipts: `receipts/YYYY-MM-DD/*.json`

### Required fields (`version: "1.0"`)
- `goal` (string)
- `changes` (non-empty list of strings)
- `verification` (non-empty list of `{ command, expect }` objects)
- `timestamp` (UTC ISO 8601)
- `actor` (string)

## Template (copy/paste)

```md
## Receipt
- Goal: <what you set out to do>
- Changes:
  - <bullet list of concrete edits>
- Verification:
  - <commands + expected output or observable behavior>
```

## JSON quickstart

```bash
python3 tools/receipt_lint.py docs/examples/receipts/receipt.sample.json
```
