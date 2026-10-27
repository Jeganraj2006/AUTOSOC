[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$templatePath = Join-Path $repositoryRoot "infrastructure/docker/.env.example"
$environmentPath = Join-Path $repositoryRoot "infrastructure/docker/.env"

function New-Secret([int]$ByteCount = 32) {
    $bytes = [System.Security.Cryptography.RandomNumberGenerator]::GetBytes($ByteCount)
    return [Convert]::ToBase64String($bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
}

if (-not (Test-Path -LiteralPath $environmentPath)) {
    Copy-Item -LiteralPath $templatePath -Destination $environmentPath
}

$replacements = @{
    'AUTOSOC_POSTGRES_USER' = 'autosoc_local'
    'AUTOSOC_POSTGRES_PASSWORD' = New-Secret 32
    'AUTOSOC_POSTGRES_DB' = 'autosoc'
    'AUTOSOC_KEYCLOAK_ADMIN_USER' = 'autosoc_keycloak_admin'
    'AUTOSOC_KEYCLOAK_ADMIN_PASSWORD' = New-Secret 32
    'AUTOSOC_KEYCLOAK_FRONTEND_CLIENT_SECRET' = New-Secret 48
    'AUTOSOC_BOOTSTRAP_USER' = 'autosoc_bootstrap'
    'AUTOSOC_BOOTSTRAP_PASSWORD' = New-Secret 32
    'AUTOSOC_MINIO_ROOT_USER' = 'autosoc_minio_admin'
    'AUTOSOC_MINIO_ROOT_PASSWORD' = New-Secret 32
}

$changed = $false
$lines = Get-Content -LiteralPath $environmentPath | ForEach-Object {
    if ($_ -match '^(?<name>[A-Z0-9_]+)=replace-with-.+$' -and $replacements.ContainsKey($Matches.name)) {
        $changed = $true
        "$($Matches.name)=$($replacements[$Matches.name])"
    } else { $_ }
}

if ($changed) {
    Set-Content -LiteralPath $environmentPath -Value $lines -Encoding utf8
    Write-Host "Generated missing local-development secrets in infrastructure/docker/.env. Values were not printed." -ForegroundColor Green
} else {
    Write-Host "Local environment already has non-placeholder values; nothing was overwritten." -ForegroundColor Green
}
