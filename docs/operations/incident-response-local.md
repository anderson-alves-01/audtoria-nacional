# Resposta a incidentes (ambiente local)

Escopo: somente compose/local. Sem nuvem, sem produção e sem dados fiscais reais.

## Classificação

1. Identificar serviço (api, worker, web, postgres, redis, keycloak, minio).
2. Capturar `trace_id` e horário UTC; não copiar tokens nem PII.
3. Verificar logs sem payload sensível.
4. Isolar: reiniciar container afetado; não apagar volumes sem dupla confirmação.

## Contenção

- Preferir `docker compose restart <service>`.
- Backup dry-run antes de restore: `docs/operations/backup-restore-local.md`.
- Jobs de ingestão: falhar fechado; não forçar reprocessamento nacional.

## Comunicação

- Registrar evidência em `evidence/` com run_id.
- Não fabricar status de gate G9/G10.
- Escalation institucional fora do escopo automático deste runbook.
