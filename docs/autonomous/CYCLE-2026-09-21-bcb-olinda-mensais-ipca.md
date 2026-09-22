# Ciclo 2026-09-21 — BCB OLINDA Expectativas mensais IPCA

## Fatia

Nova fonte `BCB-OLINDA-EXPECTATIVAS-MENSAIS` via entity set
`ExpectativaMercadoMensais` (PUBLIC_OPEN), allowlist IPCA baseCalculo=1.

## Alterações

- Conector respeita `parameters.entity_set` e `focus_label`
- Parser `FOCUS_MENSAL` + unidade `PERCENT_PER_MONTH`
- Layout `bcb-olinda-expectativas-mensais-v1`; silverCount 8
- Mediana de prova: 0.4937 (Data 2026-09-18, horizonte 01/2027)
- Migration `0092_bcb_olinda_mensais_ipca` → `0.3.89`
- Próximo: demais mensais ativos (IGP-M, Câmbio, IPCA Livres…) ou trimestrais

## Rollback

Remover fonte mensal; Alembic → `0091_bcb_olinda_balanca_exim`.
