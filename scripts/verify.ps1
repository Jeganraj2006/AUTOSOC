Write-Host "AutoSOC Local Verification Script" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"

Write-Host "`n1. Running Backend Linting (Ruff)..."
cd apps/api
python -m uv run ruff check .
python -m uv run ruff format --check .

Write-Host "`n2. Running Backend Type Checks (mypy)..."
python -m uv run mypy src

Write-Host "`n3. Running Backend Tests (pytest)..."
python -m uv run pytest --cov=src

cd ../..

Write-Host "`n4. Running Frontend Linting..."
cd apps/web
npx pnpm lint

Write-Host "`n5. Running Frontend Type Checks..."
npx pnpm typecheck

cd ../..

Write-Host "`n6. Running Pre-commit checks..."
pre-commit run --all-files

Write-Host "`nAll checks passed successfully!" -ForegroundColor Green
