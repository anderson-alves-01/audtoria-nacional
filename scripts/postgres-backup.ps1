# Local PostgreSQL dump with mandatory dry-run safety.
# Default target is the compose Postgres on localhost:55432.
# Never runs against cloud without an explicit DATABASE_URL override.

param(
  [switch]$DryRun,
  [string]$Output = "var/backups/sirta-local.dump",
  [string]$DatabaseUrl = $env:DATABASE_URL
)

$ErrorActionPreference = "Stop"

if (-not $DatabaseUrl -or $DatabaseUrl.Trim() -eq "") {
  $DatabaseUrl = "postgresql://sirta:sirta_local_only@localhost:55432/sirta"
}

if ($DatabaseUrl -notmatch "localhost|127\.0\.0\.1") {
  throw "Refusing backup: DATABASE_URL host is not localhost/127.0.0.1"
}

$resolvedOutput = [System.IO.Path]::GetFullPath($Output)
$pgDump = "pg_dump --format=custom --file=`"$resolvedOutput`" `"$DatabaseUrl`""

Write-Host "SIRTA local postgres backup"
Write-Host "target=$resolvedOutput"
Write-Host "command=$pgDump"

if ($DryRun) {
  Write-Host "DRY-RUN: no dump written"
  exit 0
}

$dir = Split-Path -Parent $resolvedOutput
if ($dir -and -not (Test-Path $dir)) {
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
}
& pg_dump --format=custom --file=$resolvedOutput $DatabaseUrl
if ($LASTEXITCODE -ne 0) {
  throw "pg_dump failed with exit $LASTEXITCODE"
}
Write-Host "backup_written=$resolvedOutput"
