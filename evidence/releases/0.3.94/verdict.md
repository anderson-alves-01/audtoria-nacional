# Verdict 0.3.94

## Fatia

BCB OLINDA Expectativas trimestrais: expansão PIB Serviços / Agropecuária /
Indústria em `BCB-OLINDA-EXPECTATIVAS-TRIMESTRAIS`
(`ExpectativasMercadoTrimestrais`, `baseCalculo=1`).

## Evidencia tecnica

- Fixtures oficiais minimizadas (top=8 por indicador)
- Medianas: PIB Serviços 2.3684; Agropecuária 2.25; Indústria 1.8281
  (Data 2021-09-13, horizonte 1/2022)
- Layout `bcb-olinda-expectativas-trimestrais-v2`; silverCount 88
- Migration: `0097_bcb_olinda_trim_pib_sec` -> implementation_version `0.3.94`
- Commit: `176eeaf`
- Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Serie setorial congelada na fonte; Selic/IGP/IPA/INPC trimestrais vazios
- Sem carga nacional; sem credito
- Testes: unit trimestrais + sectoral ingest + alembic paths
- CI: https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35648904520

## Proximo

UF tabular PUBLIC_OPEN restante. Sem homologacao humana agora.
