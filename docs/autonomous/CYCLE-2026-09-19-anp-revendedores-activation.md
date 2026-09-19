# Ciclo autônomo 0.3.31 — ativação ANP revendedores (escopo UF)

Data: 2026-09-19  
Branch: `feat/official-public-ingest`  
PR: #2  
Commit: `32156ae`  
Estado: `OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS`

## Seleção

`F3-SECTORAL-ANP` — UFs restantes sem CSV/API de quota-parte verificável neste
ciclo (SC arrecadação ≠ transfer; GO ICMS sem colunas; RJ IP-blocked). Setorial
ANP com API REST já verificada.

## Entregas

- Parser `parse_anp_revendedores_api` + ingest; CNPJ fora de Silver/Gold
- Fixture `anp-revendedores-ms-page1.json`; Gold REFERENCE_QUANTITY
- Painel `/v1/sectoral-enrichment` parcial; migration `0034` → 0.3.31
- Evidência: `evidence/releases/0.3.31/`

## Não feito

Outras UFs ICMS/IPVA, demais setoriais, RFB nacional, homologação humana.

## Resultado

CYCLE_RESULT=PROGRESSED
