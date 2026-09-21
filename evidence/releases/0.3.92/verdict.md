# Verdict 0.3.92

## Fatia

BCB OLINDA Expectativas mensais: expandiu allowlist com `IPA-M`, `IPA-DI`,
`IGP-DI` e `INPC` via `ExpectativaMercadoMensais` (`baseCalculo=0`).

## Evidência técnica

- Fixtures oficiais minimizadas (top=8 por indicador)
- Medianas: IPA-M 0.29; IPA-DI 0.33; IGP-DI 0.27; INPC 0.33
  (Data 2021-02-17; séries congeladas na fonte)
- Layout `bcb-olinda-expectativas-mensais-v4`; silverCount 96
- Migration: `0095_bcb_olinda_mensais_ipa` → implementation_version `0.3.92`
- Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Selic mensal não ativado (congelado 2005-12-14)
- Sem carga nacional; sem crédito

## Próximo

ExpectativasMercadoTrimestrais (entity set verificado com IPCA 2026-09-18);
ou UF tabular nova quando publicada.
