# Release notes 0.3.18

Estado: `OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS`

## Nesta fatia

- CI: correção do assert de checksum no dry-run de `postgres-restore` (Linux CI).
- `GET /v1/findings` — achados técnicos vazios (`createsTaxCredit=false`, `legalCommandsEnabled=false`, G5 BLOCKED).
- `GET /v1/cases` + `POST /v1/cases` — casos de auditoria D5 vazios; POST sempre 409 sem persistência.
- `GET /v1/human-validation` — workflow F5 vazio (`publishesPublicCredit=false`, estados de referência documentais).
- Telas `/achados`, `/casos-auditoria` e `/validacao-humana` com loading/empty/erro.
- Migration aditiva `0021_findings_human_validation` (meta 0.3.18).

## Não concluído

Backfill nacional, fontes estaduais, RFB territorial, notificações/cobrança F5–F6, piloto, produção e homologação humana.
