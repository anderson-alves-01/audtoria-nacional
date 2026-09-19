#!/usr/bin/env bash
# Local PostgreSQL dump with mandatory dry-run safety.
set -euo pipefail

DRY_RUN=0
OUTPUT="var/backups/sirta-local.dump"
DATABASE_URL="${DATABASE_URL:-postgresql://sirta:sirta_local_only@localhost:55432/sirta}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --output) OUTPUT="$2"; shift 2 ;;
    --database-url) DATABASE_URL="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

case "$DATABASE_URL" in
  *localhost*|*127.0.0.1*) ;;
  *) echo "Refusing backup: DATABASE_URL host is not localhost/127.0.0.1" >&2; exit 1 ;;
esac

echo "SIRTA local postgres backup"
echo "target=$OUTPUT"
echo "command=pg_dump --format=custom --file=$OUTPUT $DATABASE_URL"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "DRY-RUN: no dump written"
  exit 0
fi

mkdir -p "$(dirname "$OUTPUT")"
pg_dump --format=custom --file="$OUTPUT" "$DATABASE_URL"
echo "backup_written=$OUTPUT"
