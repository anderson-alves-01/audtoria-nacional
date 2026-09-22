# Ciclo autônomo 0.3.32 — ativação ANEEL IndQual Município (escopo UF)

## Seleção

Item `F3-SECTORAL-ANEEL-EPE` (ANEEL). Dataset IndQual Município com CodMunicipio
IBGE7 e filtro SigUF verificados no DataStore oficial.

## Entrega

- Parser `parse_aneel_ckan_open` + ingest; endpoint scoped UF=MS limit=8
- Gold REFERENCE_QUANTITY com lineage; dashboard economia
- Painel `/v1/sectoral-enrichment` parcial ANP+ANEEL; migration `0035` → 0.3.32
- Evidência: `evidence/releases/0.3.32/`

## Resultado

CYCLE_RESULT=PROGRESSED
