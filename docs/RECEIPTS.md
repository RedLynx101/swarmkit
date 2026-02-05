# Receipts

A "receipt" is a small, verifiable record of what changed and how to confirm it.

Examples live in: `docs/examples/receipts/`

## In PRs
Include a section:
- What changed
- Why
- How to verify (commands + expected output)

## On disk (future)
We will standardize a `receipts/` schema for automation runs.

## Template (copy/paste)

```md
## Receipt
- Goal: <what you set out to do>
- Changes:
  - <bullet list of concrete edits>
- Verification:
  - <commands + expected output or observable behavior>
```
