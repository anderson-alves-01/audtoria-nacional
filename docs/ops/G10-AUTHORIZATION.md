# Autorização G10 — deploy AWS produção

## Ato registrado

| Campo | Valor |
|---|---|
| Timestamp (UTC) | 2026-09-21T23:00:00Z |
| Frase | `autorizo terraform apply em produção nesta conta 332380491162, região sa-east-1` |
| Account ID | `332380491162` |
| Região | `sa-east-1` |
| Principal | `arn:aws:iam::332380491162:user/TerraformUser` |
| Confirmação dual | `APPLY-PROD` via agente após ato na conversa |

## Estado

- `cloud_apply_authorized`: **true** (somente nesta execução autorizada)
- Gold: permanece `PENDING_HUMAN_VALIDATION`
- Merge `main`: não autorizado por este ato

## Texto aceito pelo gate

1. `autorizo terraform apply em produção nesta conta/região`
2. ou `autorizo terraform apply em produção nesta conta <12 dígitos>, região <região>`

## Execução

```powershell
tools/ops/prod-terraform.ps1 -Action Apply `
  -AccountId 332380491162 `
  -Region sa-east-1 `
  -AuthorizationPhrase "autorizo terraform apply em produção nesta conta 332380491162, região sa-east-1" `
  -ConfirmToken APPLY-PROD
```
