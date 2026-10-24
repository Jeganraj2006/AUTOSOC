Write-Host "AutoSOC Local Setup Script" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"

Write-Host "`n1. Setting up Backend (uv)..."
cd apps/api
python -m uv sync --extra dev
cd ../..

Write-Host "`n2. Setting up Frontend (pnpm)..."
cd apps/web
npx pnpm install
cd ../..

Write-Host "`n3. Installing Pre-commit hooks..."
pre-commit install

Write-Host "`nSetup complete!" -ForegroundColor Green
