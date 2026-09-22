# Plan — BCB OLINDA Expectativas trimestrais PIB setoriais (0.3.94)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS-TRIMESTRAIS` com PIB Serviços, PIB
Agropecuária e PIB Indústria (`baseCalculo=1`, max_rows=8), série oficial
congelada em 2021-09-13 publicada pela fonte.

## Critérios de aceite

- Allowlist trimestrais sobe de 8 para 11 indicadores
- Layout `bcb-olinda-expectativas-trimestrais-v2`; silverCount 88
- Unidades `PERCENT_PER_QUARTER`; medianas 2.3684 / 2.25 / 1.8281
- Fixtures oficiais mínimas; Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Migration `0097_bcb_olinda_trim_pib_sec` → `0.3.94`
- Documentar série congelada 2021; Selic/IGP/IPA/INPC permanecem vazios

## Rollback

Alembic → `0096_bcb_olinda_trimestrais`; remover os 3 indicadores da allowlist.
