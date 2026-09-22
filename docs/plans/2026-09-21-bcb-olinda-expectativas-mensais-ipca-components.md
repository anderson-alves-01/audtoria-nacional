# Plan — BCB OLINDA Expectativas mensais IPCA componentes (0.3.91)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS-MENSAIS` (PUBLIC_OPEN) da allowlist
IPCA/IGP-M/Câmbio para incluir componentes Focus mensais:
`IPCA Livres`, `IPCA Serviços`, `IPCA Administrados`,
`IPCA Alimentação no domicílio` e `IPCA Bens industrializados`
(baseCalculo=1, max_rows=8 por indicador).

## Critérios de aceite

- Allowlist multi-fetch; primary permanece IPCA
- Unidades: novos indicadores `PERCENT_PER_MONTH`
- Layout `bcb-olinda-expectativas-mensais-v3`; silverCount 64
- Fixtures oficiais mínimas; medianas 0.515 / 0.31 / 0.335 / 1.38 / 0.3
- Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Migration `0094_bcb_olinda_mensais_comp` → `0.3.91`
- Próximo: Selic/IPA mensais se ativos, ou ExpectativasMercadoTrimestrais

## Rollback

Alembic → `0093_bcb_olinda_igp_cambio`; allowlist volta a
`[IPCA, IGP-M, Câmbio]`.
