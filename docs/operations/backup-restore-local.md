# Backup e restauração locais (PostgreSQL compose)

Procedimento exclusivo para o Postgres local (`localhost:55432`). Sem cloud, sem `terraform apply`.

## Backup (dry-run primeiro)

```powershell
powershell -NoProfile -File scripts/postgres-backup.ps1 -DryRun
```

```bash
./scripts/postgres-backup.sh --dry-run
```

Sem `-DryRun` / `--dry-run`, o script grava em `var/backups/` (gitignored).

## Restore (dupla confirmação)

```powershell
powershell -NoProfile -File scripts/postgres-restore.ps1 -DryRun -InputFile var/backups/sirta-local.dump
powershell -NoProfile -File scripts/postgres-restore.ps1 -Confirm -InputFile var/backups/sirta-local.dump
```

Scripts recusam `DATABASE_URL` que não seja `localhost` / `127.0.0.1`.
