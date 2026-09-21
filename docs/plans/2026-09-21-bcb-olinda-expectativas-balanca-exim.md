# Plan — BCB OLINDA Balança Exportações / Importações (0.3.88)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS` para buscar os três detalhes Focus
anuais de `Balança comercial`: `Saldo` (já ativo), `Exportações` e
`Importações` (USD_BILLION, baseCalculo=1).

## Critérios de aceite

- `indicator_detalhe` aceita lista por indicador no conector multi-fetch
- catálogo: `Balança comercial: [Saldo, Exportações, Importações]`
- fixtures OData mínimas (8 linhas) para Exportações e Importações
- HTTP helper mapeia URLs com IndicadorDetalhe
- unit parse Medianas 372.9 / 294.0198; silverCount integração=280 (33×8+16)
- layout `bcb-olinda-expectativas-anuais-v23`
- migration `0091_bcb_olinda_balanca_exim` → `0.3.88`
- Gold REFERENCE_QUANTITY; sem crédito
- próximo OLINDA: demais Focus anuais / entity sets restantes fora da allowlist

## Rollback

Downgrade Alembic para `0090_bcb_olinda_ipc_ipa` e restaurar
`indicator_detalhe.Balança comercial: Saldo` (string única).
