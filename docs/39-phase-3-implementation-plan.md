# Phase 3 Implementation Plan

## Current Repository State
The repository currently contains Phase 1 (Requirements and Scope) and Phase 2 (Architecture and Threat Modelling) documentation, along with the main `README.md`. No application code, configuration files, or directory scaffolding exist yet.

## Files and Directories to be Created
- **Root config**: `package.json`, `pnpm-workspace.yaml`, `.python-version`, `.nvmrc`, `.pre-commit-config.yaml`, `.editorconfig`, `.gitignore`, `.dockerignore`, `.env.example`.
- **Apps**: `apps/web/` (Next.js frontend), `apps/api/` (FastAPI backend).
- **Workers (Scaffolding)**: `workers/ingestion`, `workers/normalization`, `workers/detection`, `workers/correlation`, `workers/prediction`, `workers/agents`.
- **Packages (Scaffolding)**: `packages/event-schemas`, `packages/shared-python`, `packages/shared-typescript`.
- **Other Scaffolding**: `ml/`, `rules/`, `infrastructure/`.
- **Governance**: `CONTRIBUTING.md`, `SECURITY.md`, `.github/CODEOWNERS`, `.github/pull_request_template.md`.
- **CI/CD**: `.github/workflows/` (frontend, backend, security, docs).
- **Scripts**: Developer helper scripts in `scripts/`.
- **Documentation**: Phase 3 development, repository, and security documentation in `docs/`.
- **Agent Rules**: `.agents/rules/` directory containing instructions for AI assistants.
- **ADRs**: Four Phase 3 architectural decision records.

## Files to be Modified
- `README.md` (Update status to Phase 3, add quick-start and setup commands).
- `docs/08-requirements-traceability-matrix.md` (Add Phase 3 notes if required).
- `docs/13-assumptions-and-decisions.md` (Append Phase 3 ADRs).
- `docs/14-project-glossary.md` (Append frontend/backend development terminology).

## Dependency Choices
- **Frontend**: Next.js (App Router), React, Tailwind CSS, shadcn/ui, Vitest, Playwright, ESLint, Prettier.
- **Backend**: FastAPI, Pydantic, Pydantic Settings, Uvicorn, Ruff, mypy, Pytest, HTTPX.

## Runtime Choices
- **Node.js**: v20 (LTS for stability with Next.js).
- **Python**: v3.12 (Latest stable version supporting robust typing and performance).
- **Package Managers**: `pnpm` (v9) for fast, disk-efficient JS workspaces; `uv` (v0.4+) for lightning-fast, reproducible Python environments.

## Tooling Choices
- **Linting/Formatting**: Ruff (Python), ESLint + Prettier (TypeScript).
- **Type Checking**: mypy (Python), tsc (TypeScript).
- **Pre-commit**: Managed via the standard `pre-commit` Python tool.
- **Security Scanning**: Gitleaks (secrets), Semgrep (SAST), Trivy (container/fs).

## Risks
- **Monorepo Complexity**: Managing dependencies across JS and Python in the same repo can lead to pathing issues. *Mitigation: Strict workspace boundaries using `pnpm-workspace.yaml` and separate `uv` virtual environments.*
- **Pre-commit Failures**: Overly strict hooks might block legitimate development. *Mitigation: Use standard, well-tested hook versions and document how to bypass them locally in an emergency.*

## Assumptions
- The development machine supports both Node.js and Python.
- Docker is not required to run the Phase 3 tests (only local Node/Python runtimes).
- The user is operating in a Linux, macOS, or WSL2 environment (for shell scripts).

## Validation Commands
- `pnpm install` & `uv sync`
- `pnpm lint` & `uv run ruff check .`
- `pnpm type-check` & `uv run mypy .`
- `pnpm test` & `uv run pytest`
- `pre-commit run --all-files`

## Rollback Approach
If Phase 3 introduces critical issues, the entire phase can be rolled back using standard Git reversion (`git reset --hard HEAD~1` before the Phase 3 commit) since no external databases or cloud resources are affected.

## Features Explicitly Excluded from Phase 3
- User authentication, Keycloak integration, RBAC.
- PostgreSQL models, Alembic migrations, OpenSearch, Redpanda, Redis, MinIO, MLflow.
- Log ingestion, Event normalization, Detection rules, ML models.
- Alert/Incident management, MITRE mapping, Attack graphs.
- Agentic workflows, RAG, Response playbooks.
- Docker Compose infrastructure, Kubernetes manifests, Cloud integrations.
