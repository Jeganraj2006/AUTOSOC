# CI and Quality Gates

AutoSOC utilizes GitHub Actions to enforce code quality and security.

## Workflows
1. **Frontend CI**: Runs on PRs to `main`/`develop`. 
   - Installs dependencies.
   - Runs ESLint and tsc.
   - Executes Next.js build.
2. **Backend CI**: Runs on PRs to `main`/`develop`.
   - Uses `uv` for fast environment setup.
   - Runs `ruff` (lint and format check).
   - Runs `mypy`.
   - Runs `pytest` with coverage.
3. **Security Scan**: Runs on PRs and weekly schedule.
   - `gitleaks`: Scans for hardcoded secrets.
   - `trivy`: Scans filesystem for vulnerable dependencies.

## Dependency Updates
Dependabot is configured to check weekly for `npm` and `pip` (via `uv`) updates, and monthly for GitHub Action updates.
