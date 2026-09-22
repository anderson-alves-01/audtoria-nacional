# Plan — BCB OLINDA Expectativas mensais IGP-M + Câmbio (0.3.90)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS-MENSAIS` (PUBLIC_OPEN) de allowlist IPCA
para `IPCA`, `IGP-M` e `Câmbio` (baseCalculo=1, max_rows=8 por indicador).

## Critérios de aceite

- Allowlist multi-fetch; primary permanece IPCA
- Unidades: IPCA/IGP-M `PERCENT_PER_MONTH`; Câmbio `BRL_PER_USD`
- Layout `bcb-olinda-expectativas-mensais-v2`; silverCount 24
- Fixtures oficiais mínimas; medianas 0.4937 / 0.4327 / 5.17
- Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Migration `0093_bcb_olinda_igp_cambio` → `0.3.90`
- Próximo: IPCA Livres/Serviços/Administrados mensais ou trimestrais

## Rollback

Alembic → `0092_bcb_olinda_mensais_ipca`; allowlist volta a `[IPCA]`.
