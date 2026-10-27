[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$logDirectory = "E:\AUTOSOC\runtime-logs\local-app"
New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null

function Test-LocalPort([int]$Port) {
    return [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
}

if (-not (Test-LocalPort 8000)) {
    Start-Process -FilePath "uv" -ArgumentList "run --directory apps/api --group dev uvicorn --app-dir src autosoc_api.main:app --host 127.0.0.1 --port 8000" -WorkingDirectory $repositoryRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDirectory "api.out.log") -RedirectStandardError (Join-Path $logDirectory "api.err.log")
    Write-Host "Started API on http://127.0.0.1:8000." -ForegroundColor Green
} else { Write-Host "API port 8000 is already in use; preserving the existing process." -ForegroundColor Yellow }

if (-not (Test-LocalPort 3000)) {
    Start-Process -FilePath "pnpm" -ArgumentList "--dir apps/web dev" -WorkingDirectory $repositoryRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDirectory "web.out.log") -RedirectStandardError (Join-Path $logDirectory "web.err.log")
    Write-Host "Started web UI on http://127.0.0.1:3000." -ForegroundColor Green
} else { Write-Host "Web port 3000 is already in use; preserving the existing process." -ForegroundColor Yellow }
