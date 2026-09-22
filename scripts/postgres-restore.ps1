# Local PostgreSQL restore with dry-run and explicit --Confirm.
param(
  [switch]$DryRun,
  [switch]$Confirm,
  [Parameter(Mandatory = $true)][string]$InputFile,
  [string]$DatabaseUrl = $env:DATABASE_URL
)

$ErrorActionPreference = "Stop"

if (-not $DatabaseUrl -or $DatabaseUrl.Trim() -eq "") {
  $DatabaseUrl = "postgresql://sirta:sirta_local_only@localhost:55432/sirta"
}

if ($DatabaseUrl -notmatch "localhost|127\.0\.0\.1") {
  throw "Refusing restore: DATABASE_URL host is not localhost/127.0.0.1"
}

$resolved = [System.IO.Path]::GetFullPath($InputFile)
if (-not (Test-Path $resolved)) {
  throw "Input dump not found: $resolved"
}

$info = Get-Item $resolved
$hash = (Get-FileHash -Algorithm SHA256 -Path $resolved).Hash
$pgRestore = "pg_restore --clean --if-exists --dbname=`"$DatabaseUrl`" `"$resolved`""

Write-Host "SIRTA local postgres restore"
Write-Host "input=$resolved"
Write-Host "bytes=$($info.Length)"
Write-Host "sha256=$hash"
Write-Host "command=$pgRestore"

if ($DryRun) {
  Write-Host "DRY-RUN: no restore executed"
  exit 0
}

if (-not $Confirm) {
  throw "Refusing restore without -Confirm (use -DryRun to inspect)"
}

& pg_restore --clean --if-exists --dbname=$DatabaseUrl $resolved
if ($LASTEXITCODE -ne 0) {
  throw "pg_restore failed with exit $LASTEXITCODE"
}
Write-Host "restore_completed=$resolved"
