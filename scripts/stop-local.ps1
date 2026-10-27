[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
docker compose -f (Join-Path $repositoryRoot "infrastructure/docker/compose.yml") stop
Write-Host "AutoSOC Docker services were stopped. Persistent volumes and E: storage were preserved." -ForegroundColor Green
