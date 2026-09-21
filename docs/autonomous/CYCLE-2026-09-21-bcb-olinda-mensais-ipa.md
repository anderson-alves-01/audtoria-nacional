# Cycle — BCB OLINDA mensais IPA-M/IPA-DI/IGP-DI/INPC (0.3.92)

## Fatia

Expandiu `BCB-OLINDA-EXPECTATIVAS-MENSAIS` com IPA-M, IPA-DI, IGP-DI e INPC
via `ExpectativaMercadoMensais` e `baseCalculo=0`.

## Evidencia

- Fixtures oficiais minimizadas (top=8); medianas 0.29 / 0.33 / 0.27 / 0.33
- Layout `bcb-olinda-expectativas-mensais-v4`; silverCount 96
- Selic mensal nao ativado (congelado 2005-12-14)
- Migration `0095_bcb_olinda_mensais_ipa` -> `0.3.92`
- Commit: `eb1dbe7`
- Gold REFERENCE_QUANTITY; createsTaxCredit=false
- CI verde: https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35642801810

## Proximo

ExpectativasMercadoTrimestrais (entity set ativo com IPCA recente) ou UF tabular.
