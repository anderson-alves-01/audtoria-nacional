# Plan — BCB OLINDA Expectativas mensais IPA/IGP-DI/INPC (0.3.92)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS-MENSAIS` (PUBLIC_OPEN) com indicadores
Focus que exigem `baseCalculo=0`: `IPA-M`, `IPA-DI`, `IGP-DI` e `INPC`
(max_rows=8 por indicador). Selic mensal permanece fora (série congelada
em 2005-12-14).

## Critérios de aceite

- Allowlist multi-fetch com `indicator_base_calculo` override = 0
- Unidades `PERCENT_PER_MONTH` para os quatro indicadores
- Layout `bcb-olinda-expectativas-mensais-v4`; silverCount 96
- Fixtures oficiais mínimas; medianas 0.29 / 0.33 / 0.27 / 0.33
- Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Migration `0095_bcb_olinda_mensais_ipa` → `0.3.92`
- Próximo: ExpectativasMercadoTrimestrais (entity set verificado)

## Rollback

Alembic → `0094_bcb_olinda_mensais_comp`; allowlist volta a
IPCA+componentes+IGP-M+Câmbio.
