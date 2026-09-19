#Requires -Version 5.1
<#
.SYNOPSIS
  Deterministic local verification of the SIRTA roadmap (no apply, deploy, merge).
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Continue"
Set-StrictMode -Version Latest

function Get-RepoRoot {
    $dir = (Get-Location).Path
    if (-not (Test-Path (Join-Path $dir "AGENTS.md"))) {
        throw "Execute verify-roadmap.ps1 na raiz do repositório."
    }
    return $dir
}

$script:RepoRoot = Get-RepoRoot
$script:Failures = New-Object System.Collections.Generic.List[string]
$env:PYTHONUTF8 = "1"

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Action,
        [switch]$Optional
    )
    Write-Host "==> $Name"
    try {
        & $Action
        if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
            throw "exit $LASTEXITCODE"
        }
        Write-Host "OK $Name"
    }
    catch {
        $msg = "$Name : $($_.Exception.Message)"
        if ($Optional) {
            Write-Host "SKIP $msg"
        }
        else {
            $script:Failures.Add($msg) | Out-Null
            Write-Host "FAIL $msg"
        }
    }
}

Invoke-Step "ruff format --check" {
    python -m ruff format --check apps tests alembic
}
Invoke-Step "ruff check" {
    python -m ruff check apps tests alembic
}
Invoke-Step "OpenAPI" {
    python -m openapi_spec_validator contracts/openapi/sirta-v1.yaml
}
Invoke-Step "detect-secrets" {
    python -m detect_secrets scan --baseline .secrets.baseline --exclude-files "package-lock.json|.*\.lock"
}
Invoke-Step "migrations base->head, upgrade paths, seed estrutural" {
    python -m pytest tests/integration/test_alembic_paths.py -q
}
Invoke-Step "pytest (unit, contract, integration, lineage, isolation)" {
    python -m pytest tests -q
}
Invoke-Step "npm test" {
    Push-Location (Join-Path $script:RepoRoot "apps/web")
    try { npm test } finally { Pop-Location }
}
Invoke-Step "Angular build" {
    Push-Location (Join-Path $script:RepoRoot "apps/web")
    try { npm run build } finally { Pop-Location }
}
Invoke-Step "Angular e2e (se existir pacote)" {
    $pkg = Get-Content (Join-Path $script:RepoRoot "apps/web/package.json") -Raw
    if ($pkg -notmatch '"e2e"' -or $pkg -match "add a package that implements") {
        throw "e2e não configurado"
    }
    Push-Location (Join-Path $script:RepoRoot "apps/web")
    try { npm run e2e } finally { Pop-Location }
} -Optional
Invoke-Step "docker build api" {
    docker build -f apps/api/Dockerfile -t sirta-api:verify .
}
Invoke-Step "docker build worker" {
    docker build -f apps/workers/Dockerfile -t sirta-worker:verify .
}
Invoke-Step "docker build web" {
    docker build -f apps/web/Dockerfile -t sirta-web:verify .
}
Invoke-Step "terraform fmt -check" {
    terraform fmt -check -recursive infra/terraform
}
Invoke-Step "terraform validate local (backend disabled)" {
    $tfDir = Join-Path $script:RepoRoot "infra/terraform/environments/local"
    Push-Location $tfDir
    try {
        terraform init -backend=false -input=false | Out-Host
        terraform validate
    }
    finally { Pop-Location }
}

if ($script:Failures.Count -gt 0) {
    Write-Host "VERIFY_FAILED count=$($script:Failures.Count)"
    $script:Failures | ForEach-Object { Write-Host $_ }
    exit 1
}
Write-Host "VERIFY_OK"
exit 0
