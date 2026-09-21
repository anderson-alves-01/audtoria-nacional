#Requires -Version 5.1
param(
    [Parameter(Mandatory = $true)]
    [string]$BaseUrl
)

$ErrorActionPreference = "Stop"
$EvidenceDir = Join-Path (Resolve-Path (Join-Path $PSScriptRoot "..\..")) "evidence\ops"
New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
$stamp = Get-Date -Format "yyyyMMddTHHmmssZ"
$out = Join-Path $EvidenceDir "smoke-prod-$stamp.txt"

$base = $BaseUrl.TrimEnd("/")
$lines = @()
$lines += "smoke_started=$(Get-Date -Format o)"
$lines += "base_url=$base"
$lines += "gold_status=PENDING_HUMAN_VALIDATION"
$lines += "note=Smoke does not promote Gold or validate fiscal credit."

function Test-Url([string]$Path) {
    $url = "$base$Path"
    try {
        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 30
        return "OK $Path status=$($resp.StatusCode)"
    }
    catch {
        return "FAIL $Path error=$($_.Exception.Message)"
    }
}

$lines += (Test-Url "/health")
$lines += (Test-Url "/")
$lines += "smoke_finished=$(Get-Date -Format o)"
$lines | Tee-Object -FilePath $out
Write-Host "SMOKE_EVIDENCE=$out"
