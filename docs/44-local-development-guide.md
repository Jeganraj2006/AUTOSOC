# Local Development Guide

## Prerequisites
1. **Python 3.12**
2. **Node.js 20** (LTS)

## Initial Setup
Run the setup script from the repository root (PowerShell):
```powershell
.\scripts\setup.ps1
```
Alternatively, manually:
1. Frontend: `cd apps/web && npx pnpm install`
2. Backend: `cd apps/api && python -m uv sync --extra dev`
3. Hooks: `pre-commit install`

## Running the Applications

**Frontend (Next.js)**:
```bash
cd apps/web
npx pnpm dev
```
Accessible at http://localhost:3000

**Backend (FastAPI)**:
```bash
cd apps/api
python -m uv run uvicorn autosoc_api.main:app --reload
```
Accessible at http://localhost:8000/api/v1/health/live

## Quality Checks
Run the verification script to run all linting, formatting, and tests:
```powershell
.\scripts\verify.ps1
```
