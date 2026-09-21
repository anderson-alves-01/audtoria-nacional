# Verdict 0.3.91

## Fatia

BCB OLINDA Expectativas mensais: expandiu allowlist com componentes IPCA
Focus (`IPCA Livres`, `IPCA Serviços`, `IPCA Administrados`,
`IPCA Alimentação no domicílio`, `IPCA Bens industrializados`) via
`ExpectativaMercadoMensais`.

## Evidência técnica

- Fixtures oficiais minimizadas (top=8 por indicador)
- Medianas: Livres 0.515; Serviços 0.31; Administrados 0.335;
  Alimentação 1.38; Bens 0.3 (Data 2026-09-18)
- Layout `bcb-olinda-expectativas-mensais-v3`; silverCount 64
- Migration: `0094_bcb_olinda_mensais_comp` → implementation_version `0.3.91`
- Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Sem carga nacional; sem crédito

## Próximo

Selic/IPA-M/IPA-DI mensais se baseCalculo ativo; ou entity set trimestral;
ou UF tabular nova quando publicada.
