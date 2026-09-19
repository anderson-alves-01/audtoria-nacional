# Release notes 0.3.18

Estado: `OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS`

## Nesta fatia

- `GET /v1/findings` — achados técnicos vazios (`createsTaxCredit=false`, `legalCommandsEnabled=false`, G5 BLOCKED).
- `GET /v1/cases` + `POST /v1/cases` — casos de auditoria D5 vazios; POST sempre 409 sem persistência.
- `GET /v1/human-validation` — workflow F5 vazio (`publishesPublicCredit=false`, estados de referência documentais).
- `GET /v1/notifications` + `POST /v1/notifications` — notificações vazias; envio real sempre 409.
- `GET /v1/collection` — painel oficial de cobrança vazio; comandos desativados; fluxo sintético só em testes de API.
- Telas `/achados`, `/casos-auditoria`, `/validacao-humana`, `/notificacoes` e `/cobranca` com loading/empty/erro.
- Migration aditiva `0021_findings_human_validation` (meta 0.3.18).
- Orquestrador: wait de agent com heartbeat e poll de CI sem `--watch`.

## Não concluído

Backfill nacional, fontes estaduais, RFB territorial, pagamentos/dívida ativa F6, piloto, produção e homologação humana.
