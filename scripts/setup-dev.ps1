[CmdletBinding()]
param(
    [switch]$StartApplications
)

$ErrorActionPreference = "Stop"

function Require-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found. See docs/DEPLOYMENT_GUIDE.md."
    }
}

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $repositoryRoot "infrastructure/docker/compose.yml"
$composeEnv = Join-Path $repositoryRoot "infrastructure/docker/.env"

Push-Location $repositoryRoot
try {
    Require-Command docker
    Require-Command uv
    Require-Command pnpm

    if (-not (Test-Path -LiteralPath $composeEnv)) {
        throw "Missing $composeEnv. Run 'pwsh scripts/initialize-local-env.ps1' to generate unique local secrets first."
    }
    if (Select-String -LiteralPath $composeEnv -Pattern '^.+replace-with-.+$' -Quiet) {
        throw "$composeEnv still contains placeholder values. Run 'pwsh scripts/initialize-local-env.ps1'; secret values are never printed."
    }

    docker compose -f $composeFile config --quiet

    Write-Host "Starting core services..." -ForegroundColor Cyan
    docker compose -f $composeFile up -d --build postgres redis redpanda opensearch minio keycloak

    $healthyContainers = @("autosoc-postgres", "autosoc-redis", "autosoc-redpanda", "autosoc-opensearch", "autosoc-minio")
    $deadline = (Get-Date).AddMinutes(5)
    do {
        $unhealthy = @()
        foreach ($container in $healthyContainers) {
            $health = docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' $container 2>$null
            if ($health -ne "healthy") { $unhealthy += "$container=$health" }
        }
        if ($unhealthy.Count -eq 0) { break }
        Start-Sleep -Seconds 5
    } while ((Get-Date) -lt $deadline)
    if ($unhealthy.Count -ne 0) {
        throw "Core services did not become healthy: $($unhealthy -join ', ')"
    }

    $keycloakReady = $false
    $keycloakDeadline = (Get-Date).AddMinutes(3)
    do {
        try {
            $keycloakReady = (Invoke-WebRequest -Uri "http://127.0.0.1:8080/realms/master" -TimeoutSec 5).StatusCode -eq 200
        } catch { $keycloakReady = $false }
        if (-not $keycloakReady) { Start-Sleep -Seconds 5 }
    } while (-not $keycloakReady -and (Get-Date) -lt $keycloakDeadline)
    if (-not $keycloakReady) { throw "Keycloak did not become reachable on http://127.0.0.1:8080." }

    Write-Host "Installing backend development dependencies and applying migrations..." -ForegroundColor Cyan
    Push-Location "apps/api"
    try {
        uv sync --group dev
        uv run --group dev alembic -c alembic.ini upgrade head
    } finally { Pop-Location }

    Write-Host "Reconciling Keycloak realm and identities without rotating existing passwords..." -ForegroundColor Cyan
    & "apps/api/.venv/Scripts/python.exe" "scripts/setup_keycloak.py"

    Write-Host "Creating required Redpanda topics..." -ForegroundColor Cyan
    $topics = @(
        "security.events.raw", "security.events.normalized", "security.events.enriched",
        "security.detections", "security.alerts", "security.incidents", "security.predictions",
        "security.agent.tasks", "security.response.tasks", "security.audit.events", "security.events.failed"
    )
    foreach ($topic in $topics) { docker exec autosoc-redpanda rpk topic create $topic --if-not-exists }

    Write-Host "Starting SOC workers..." -ForegroundColor Cyan
    docker compose -f $composeFile up -d --build ingestion-worker normalization-worker detection-worker correlation-worker prediction-worker agent-worker
    docker compose -f $composeFile ps

    if ($StartApplications) {
        & "$PSScriptRoot/start-local.ps1"
    } else {
        Write-Host "Infrastructure is ready. Run 'pwsh scripts/start-local.ps1' to start the API and web UI." -ForegroundColor Green
    }
} finally {
    Pop-Location
}
