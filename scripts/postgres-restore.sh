#!/usr/bin/env bash
# Local PostgreSQL restore with dry-run and explicit --confirm.
set -euo pipefail

DRY_RUN=0
CONFIRM=0
INPUT=""
DATABASE_URL="${DATABASE_URL:-postgresql://sirta:sirta_local_only@localhost:55432/sirta}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --confirm) CONFIRM=1; shift ;;
    --input) INPUT="$2"; shift 2 ;;
    --database-url) DATABASE_URL="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$INPUT" ]]; then
  echo "--input is required" >&2
  exit 2
fi

case "$DATABASE_URL" in
  *localhost*|*127.0.0.1*) ;;
  *) echo "Refusing restore: DATABASE_URL host is not localhost/127.0.0.1" >&2; exit 1 ;;
esac

if [[ ! -f "$INPUT" ]]; then
  echo "Input dump not found: $INPUT" >&2
  exit 1
fi

BYTES=$(wc -c < "$INPUT" | tr -d ' ')
SHA256=$(sha256sum "$INPUT" | awk '{print $1}')

echo "SIRTA local postgres restore"
echo "input=$INPUT"
echo "bytes=$BYTES"
echo "sha256=$SHA256"
echo "command=pg_restore --clean --if-exists --dbname=$DATABASE_URL $INPUT"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "DRY-RUN: no restore executed"
  exit 0
fi

if [[ "$CONFIRM" -ne 1 ]]; then
  echo "Refusing restore without --confirm (use --dry-run to inspect)" >&2
  exit 1
fi

pg_restore --clean --if-exists --dbname="$DATABASE_URL" "$INPUT"
echo "restore_completed=$INPUT"
