# AutoSOC local development startup.  Starts only core dependencies; workers are opt-in.
$ErrorActionPreference = "Stop"

$composeFile = "infrastructure/docker/compose.yml"
$composeEnv = "infrastructure/docker/.env"

if (-not (Test-Path $composeEnv)) {
    Copy-Item "infrastructure/docker/.env.example" $composeEnv
    throw "Created $composeEnv. Replace every placeholder before re-running setup."
}

docker compose -f $composeFile config --quiet

Write-Host "Starting core services (PostgreSQL, Redis, Redpanda, OpenSearch, Keycloak)..." -ForegroundColor Cyan
docker compose -f $composeFile up -d postgres redis redpanda opensearch keycloak

$requiredContainers = @("autosoc-postgres", "autosoc-redis", "autosoc-redpanda", "autosoc-opensearch")
$deadline = (Get-Date).AddMinutes(3)
do {
    $states = @{}
    foreach ($container in $requiredContainers) {
        $states[$container] = docker inspect --format '{{.State.Health.Status}}' $container 2>$null
    }
    if (($states.Values | Where-Object { $_ -ne "healthy" }).Count -eq 0) {
        break
    }
    Start-Sleep -Seconds 5
} while ((Get-Date) -lt $deadline)

if (($states.Values | Where-Object { $_ -ne "healthy" }).Count -ne 0) {
    throw "Core services did not become healthy: $($states | ConvertTo-Json -Compress)"
}

$keycloakDeadline = (Get-Date).AddMinutes(2)
do {
    try {
        $keycloakReady = (Invoke-WebRequest -Uri "http://127.0.0.1:8080/realms/master" -TimeoutSec 5).StatusCode -eq 200
    } catch {
        $keycloakReady = $false
    }
    if (-not $keycloakReady) { Start-Sleep -Seconds 5 }
} while (-not $keycloakReady -and (Get-Date) -lt $keycloakDeadline)

if (-not $keycloakReady) {
    throw "Keycloak did not become reachable on http://127.0.0.1:8080."
}

Write-Host "Running database migrations..." -ForegroundColor Cyan
Push-Location "apps/api"
try {
    & ".venv/Scripts/alembic.exe" -c alembic.ini upgrade head
} finally {
    Pop-Location
}

Write-Host "Configuring the local Keycloak realm..." -ForegroundColor Cyan
& "apps/api/.venv/Scripts/python.exe" "scripts/setup_keycloak.py"

Write-Host "Creating Redpanda topics..." -ForegroundColor Cyan
$topics = @(
    "security.events.raw", "security.events.normalized", "security.events.enriched",
    "security.detections", "security.alerts", "security.incidents", "security.predictions",
    "security.agent.tasks", "security.response.tasks", "security.audit.events"
)
foreach ($topic in $topics) {
    docker exec autosoc-redpanda rpk topic create $topic --if-not-exists
}

Write-Host "Core setup is complete. Start the API with 'uv run --offline uvicorn --app-dir src autosoc_api.main:app --host 127.0.0.1 --port 8000' from apps/api, then start the web app with 'pnpm --filter web dev'." -ForegroundColor Green
