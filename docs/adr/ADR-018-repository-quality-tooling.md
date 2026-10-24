# ADR-018: Repository Quality Tooling

## Status
Accepted

## Context
A monorepo containing multiple languages requires standardized, high-performance tooling to ensure code quality and consistency across a distributed team.

## Decision
We will standardize on the following tools:
- **Python**: `ruff` for linting and formatting, `mypy` for static type checking, `pytest` for unit testing.
- **TypeScript**: `eslint` and `prettier` for linting/formatting, `vitest` for unit tests, `playwright` for end-to-end tests.
- **Security**: `gitleaks` (secrets), `semgrep` (SAST), `trivy` (container/fs vulnerabilities).

## Alternatives Considered
- Python `flake8` / `black`: Slower and requires multiple separate tools compared to the unified Rust-based `ruff`.
- TypeScript `jest`: Slower than `vitest` and requires complex configuration to work seamlessly with modern ESM and Vite.

## Positive Consequences
- Faster CI execution times (Ruff is orders of magnitude faster than Black/Flake8).
- Unified configuration in `pyproject.toml` and `package.json`.

## Security Implications
- Automated secret scanning (Gitleaks) prevents accidental exposure of credentials in the open-source repository.
