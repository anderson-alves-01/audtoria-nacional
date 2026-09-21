#Requires -Version 5.1
<#
.SYNOPSIS
  Plan/Apply production Terraform with G10 phrase gate.
#>
param(
    [ValidateSet("Plan", "Apply", "Validate")]
    [string]$Action = "Plan",
    [string]$AccountId = "",
    [string]$Region = "sa-east-1",
    [string]$AuthorizationPhrase = "",
    [string]$TfVarsFile = "",
    [string]$ConfirmToken = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ProdDir = Join-Path $RepoRoot "infra\terraform\environments\prod"
$EvidenceDir = Join-Path $RepoRoot "evidence\ops"
New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
$stamp = Get-Date -Format "yyyyMMddTHHmmssZ"
$RequiredPhrase = "autorizo terraform apply em produção nesta conta/região"

function Test-G10Phrase([string]$Phrase) {
    if ([string]::IsNullOrWhiteSpace($Phrase)) { return $false }
    $normalized = $Phrase.Trim().ToLowerInvariant()
    if ($normalized -eq "autorizo terraform apply em produção nesta conta/região".ToLowerInvariant()) {
        return $true
    }
    # Explicit account + region form from chat authorization.
    if ($normalized -match '^autorizo terraform apply em produ[cç][aã]o nesta conta\s+\d{12},\s*regi[aã]o\s+[a-z0-9-]+$') {
        return $true
    }
    # Fallback: starts with authorization verb and includes account + region tokens.
    if ($normalized.StartsWith("autorizo terraform apply em produ") -and ($normalized -match '\d{12}') -and ($normalized -match 'sa-east-1|us-east-1|[a-z]{2}-[a-z]+-\d')) {
        return $true
    }
    return $false
}

Set-Location $ProdDir

function Invoke-Tf([string[]]$TfArgs) {
    & terraform @TfArgs
    if ($LASTEXITCODE -ne 0) { throw "terraform failed: $($TfArgs -join ' ')" }
}

Write-Host "PROD_TERRAFORM action=$Action cwd=$ProdDir"

if ($Action -eq "Validate") {
    Invoke-Tf @("init", "-backend=false")
    Invoke-Tf @("validate")
    Write-Host "VALIDATE_OK"
    exit 0
}

Invoke-Tf @("init", "-backend=false")

if ($Action -eq "Plan") {
    $out = Join-Path $EvidenceDir "terraform-plan-prod-$stamp.txt"
    $planArgs = @("plan", "-input=false", "-var=cloud_apply_authorized=false")
    if ($AccountId) { $planArgs += "-var=aws_account_id=$AccountId" }
    if ($Region) { $planArgs += "-var=aws_region=$Region" }
    if ($TfVarsFile) { $planArgs += "-var-file=$TfVarsFile" }
    & terraform @planArgs | Tee-Object -FilePath $out
    if ($LASTEXITCODE -ne 0) { throw "terraform plan failed" }
    Write-Host "PLAN_OK evidence=$out apply_allowed=false"
    exit 0
}

if ($Action -eq "Apply") {
    if (-not (Test-G10Phrase $AuthorizationPhrase)) {
        throw "APPLY_BLOCKED: missing exact G10 phrase. See docs/ops/G10-AUTHORIZATION.md"
    }
    if (-not $AccountId) { throw "APPLY_BLOCKED: -AccountId required" }
    if (-not $Region) { throw "APPLY_BLOCKED: -Region required" }

    if ($ConfirmToken -ne "APPLY-PROD") {
        $confirm = Read-Host "Type APPLY-PROD to continue"
        if ($confirm -ne "APPLY-PROD") { throw "APPLY_BLOCKED: dual confirmation failed" }
    }

    $out = Join-Path $EvidenceDir "terraform-apply-prod-$stamp.txt"
    $env:AWS_DEFAULT_REGION = $Region
    $env:AWS_REGION = $Region
    $applyArgs = @(
        "apply", "-input=false", "-auto-approve",
        "-var=cloud_apply_authorized=true",
        "-var=aws_account_id=$AccountId",
        "-var=aws_region=$Region"
    )
    if ($TfVarsFile) { $applyArgs += "-var-file=$TfVarsFile" }
    & terraform @applyArgs | Tee-Object -FilePath $out
    if ($LASTEXITCODE -ne 0) { throw "terraform apply failed" }
    Write-Host "APPLY_OK evidence=$out"
    exit 0
}
