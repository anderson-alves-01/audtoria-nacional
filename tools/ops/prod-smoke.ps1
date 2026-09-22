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
$lines += "gold_status=REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY"
$lines += "note=Smoke checks public shells; does not constitute tax credit."

function Test-Url([string]$Path) {
    $url = "$base$Path"
    try {
        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 45
        return "OK $Path status=$($resp.StatusCode) len=$($resp.RawContentLength)"
    }
    catch {
        return "FAIL $Path error=$($_.Exception.Message)"
    }
}

$lines += (Test-Url "/health")
$lines += (Test-Url "/")
$lines += (Test-Url "/executivo")
$lines += (Test-Url "/financeiro")
$lines += (Test-Url "/transferencias")
$lines += (Test-Url "/cobranca")
$lines += "smoke_finished=$(Get-Date -Format o)"
$lines | Tee-Object -FilePath $out
Write-Host "SMOKE_EVIDENCE=$out"
