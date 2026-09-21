# Cycle — BCB OLINDA Expectativas trimestrais PIB setoriais (0.3.94)

## Fatia

Expandiu `BCB-OLINDA-EXPECTATIVAS-TRIMESTRAIS` com PIB Serviços,
PIB Agropecuária e PIB Indústria (série oficial congelada 2021-09-13).

## Evidência

- Layout `bcb-olinda-expectativas-trimestrais-v2`; silverCount 88
- Medianas: Serviços 2.3684; Agropecuária 2.25; Indústria 1.8281
- Migration `0097_bcb_olinda_trim_pib_sec` -> `0.3.94`
- Commit: `176eeaf`
- Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Selic/IGP/IPA/INPC trimestrais continuam vazios na fonte

## Próximo

UF tabular PUBLIC_OPEN restante, ou outro indicador trimestral se a fonte
publicar linhas novas. Sem homologação humana agora.
