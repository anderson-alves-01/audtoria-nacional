# Release notes 0.3.20

Estado: `OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS`

## Nesta fatia

- `GET/POST /v1/transfer-reconciliation` — conciliação vazia; diferença = ocorrência; POST 409; `createsTaxCredit=false`.
- `GET /v1/pilot-readiness` — checklist técnico em `/prontidao`; `technicalReady` possível; G9 BLOCKED.
- `GET /v1/ops-governance` — inventário de runbooks locais; `canDeploy=false`; G10 BLOCKED.
- Telas `/conciliacao-transferencias`, `/prontidao` (dedicada) e `/operacao-governanca`.
- Runbooks: `incident-response-local.md`, `ingest-ops-local.md`, `gates-governance-local.md`.
- Migration aditiva `0023_f7_f9_f10_shells` (meta 0.3.20).

## Não concluído

Backfill nacional, fontes estaduais, RFB territorial, setoriais, upload municipal, cadastro 360, piloto institucional, produção e homologação humana.
