# Verdict 0.3.92

## Fatia

BCB OLINDA Expectativas mensais: expandiu allowlist com `IPA-M`, `IPA-DI`,
`IGP-DI` e `INPC` via `ExpectativaMercadoMensais` (`baseCalculo=0`).

## Evidencia tecnica

- Fixtures oficiais minimizadas (top=8 por indicador)
- Medianas: IPA-M 0.29; IPA-DI 0.33; IGP-DI 0.27; INPC 0.33
  (Data 2021-02-17; series congeladas na fonte)
- Layout `bcb-olinda-expectativas-mensais-v4`; silverCount 96
- Migration: `0095_bcb_olinda_mensais_ipa` -> implementation_version `0.3.92`
- Commit: `eb1dbe7`
- Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Selic mensal nao ativado (congelado 2005-12-14)
- Sem carga nacional; sem credito
- Testes: 11 passed (unit+sectoral+alembic)
- CI verde: https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35642801810

## Proximo

ExpectativasMercadoTrimestrais (entity set verificado com IPCA 2026-09-18);
ou UF tabular nova quando publicada.
