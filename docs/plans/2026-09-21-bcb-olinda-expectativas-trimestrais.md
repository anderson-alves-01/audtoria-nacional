# Plan — BCB OLINDA Expectativas trimestrais (0.3.93)

## Objetivo

Ativar nova fonte `BCB-OLINDA-EXPECTATIVAS-TRIMESTRAIS` (PUBLIC_OPEN) via
entity set `ExpectativasMercadoTrimestrais` com allowlist IPCA + componentes
Focus + Câmbio + PIB Total (`baseCalculo=1`, max_rows=8 por indicador).

## Critérios de aceite

- Nova source TECHNICALLY_APPROVED; connector `bcb_olinda_expectativas`
- Layout `bcb-olinda-expectativas-trimestrais-v1`; silverCount 64
- Unidades `PERCENT_PER_QUARTER` (Câmbio=`BRL_PER_USD`)
- Fixtures oficiais mínimas; medianas IPCA 1.5731 … PIB Total 1.3
- Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Migration `0096_bcb_olinda_trimestrais` → `0.3.93`
- Fora desta fatia: Selic/IGP/IPA/INPC vazios; PIB setoriais congelados 2021

## Rollback

Alembic → `0095_bcb_olinda_mensais_ipa`; remover source TRIMESTRAIS do catálogo.
