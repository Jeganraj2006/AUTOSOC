# Contributing to AutoSOC

## Phase Boundary Rules
We are currently operating in **Phase 3 (Repository Setup)**. 
- **DO NOT** submit PRs implementing future phase functionality (e.g., ML models, databases, rules).
- Review the `README.md` to ensure your PR aligns with the current active phase.

## Setup
See `docs/44-local-development-guide.md` for full setup instructions using `pnpm` and `uv`.

## Branch Naming
- `feature/[issue-number]-short-description`
- `fix/[issue-number]-short-description`
- `docs/short-description`
- `experiment/ml-model-name` (For Phase 10+)

## Commit Conventions
We use Conventional Commits:
`feat: add new endpoint`
`fix: correct validation bug`
`chore: update dependencies`

## Testing Requirements
All PRs must include tests. Backend coverage must remain above the established threshold. Run the verification script before pushing.

## Security Restrictions
- **NEVER** commit secrets. `gitleaks` runs on pre-commit.
- **NEVER** use real organizational infrastructure for response playbooks.
- **NEVER** describe anomalies as "confirmed zero-day vulnerabilities". Use "potential zero-day behavior".
