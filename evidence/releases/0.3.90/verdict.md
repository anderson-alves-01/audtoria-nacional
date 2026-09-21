# Verdict 0.3.90

## Fatia

BCB OLINDA Expectativas mensais: expandiu allowlist para `IPCA`, `IGP-M` e
`Câmbio` via `ExpectativaMercadoMensais`.

## Evidência técnica

- Fixtures oficiais minimizadas (top=8 por indicador)
- Medianas: IPCA 0.4937; IGP-M 0.4327; Câmbio 5.17 (Data 2026-09-18)
- Layout `bcb-olinda-expectativas-mensais-v2`; silverCount 24
- Migration: `0093_bcb_olinda_igp_cambio` → implementation_version `0.3.90`
- Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Sem carga nacional; sem crédito
- Testes: 17 passed (unit+sectoral integration)

## Próximo

IPCA Livres/Serviços/Administrados/Alimentação/Bens industrializados mensais;
ou entity set trimestral; ou UF tabular nova quando publicada.
