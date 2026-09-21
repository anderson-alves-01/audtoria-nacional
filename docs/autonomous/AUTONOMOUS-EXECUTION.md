# Execução autônoma do ROADMAP SIRTA 2026

Sistema local persistente que abre **sessões novas** do Cursor Agent (`agent`) até a conclusão técnica real. Cada sessão é um ciclo. O repositório e `docs/autonomous/ROADMAP-WORK-QUEUE.yaml` são a memória.

## Estado de partida

| Item | Valor |
|---|---|
| Branch | `feat/official-public-ingest` |
| HEAD inicial | `1d7a601` ou sucessor |
| PR | #2 |
| Versão | 0.3.51 |
| Estado | `OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS` |
| Merge em main | proibido |
| Gold | `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION` |

## Comandos

Preflight (não inicia ciclo):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/autonomous/run-roadmap-autonomous.ps1 -PreflightOnly
```

Verificação determinística:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/autonomous/verify-roadmap.ps1
```

Orquestrador (até 80 ciclos):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/autonomous/run-roadmap-autonomous.ps1 -MaxCycles 80
```

Acompanhamento:

```powershell
Get-Content .cursor-autonomous/orchestrator.log -Wait -Tail 50
```

Parada controlada:

```powershell
New-Item -ItemType File -Force .cursor-autonomous/STOP
```

## Runtime

`.cursor-autonomous/` (gitignored) guarda lock, PID, logs e resultados de ciclo. Proibido: chaves, tokens, payloads grandes, dados brutos oficiais.

## Conclusão

Somente o orquestrador, após fila sem PENDING/IN_PROGRESS/FAILED, `verify-roadmap.ps1` exit 0, CI verde, árvore limpa, push feito e **dois** auditores `VERDICT=COMPLETE`, grava `.cursor-autonomous/COMPLETE` e o estado `TECHNICAL_ROADMAP_COMPLETE_REAL_DATA_AWAITING_HUMAN_VALIDATION`.

80 ciclos sem conclusão: `.cursor-autonomous/MAX_CYCLES_REACHED`. Não declarar sucesso.
