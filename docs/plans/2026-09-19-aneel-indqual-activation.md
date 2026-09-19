# Plan — Ativação ANEEL IndQual Município (0.3.32)

- Goal: Ativar ingestão técnica `ANEEL-DADOS-ABERTOS` (PUBLIC_OPEN, REFERENCE_ENRICHMENT) com escopo UF=MS, fixture mínima IndQual Município (DataStore), agregação por CodMunicipio IBGE7 e lineage Gold.
- Phase: F3.2 — `F3-SECTORAL-ANEEL-EPE`
- Spec: ROADMAP 1.2 § fontes setoriais; `contracts/sources/official-catalog.yaml`
- Components:
  - `parsers.py` — `parse_aneel_ckan_open`
  - `official_ingest.py` — registrar conector; remover do bloqueio
  - `gold.py`, `dashboards.py` (economia), `sectoral_enrichment.py`
  - catálogo + snapshot `aneel-indqual-municipio-ms-limit8.json`
  - migration `0035_aneel_indqual_activation` → 0.3.32
- Data: PUBLIC_OPEN; fixture só em testes; escopo `uf=MS`, `limit=8`; sem carga nacional
- Security: sem PII; sem crédito
- Acceptance: ingest 200 com lineage; painel setorial parcial ANP+ANEEL; demais setoriais bloqueados; testes verdes
- Human gates: inalterados; Gold `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`
