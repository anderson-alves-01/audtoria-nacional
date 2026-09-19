# Plan — Ativação ANP revendedores (0.3.31)

- Goal: Ativar ingestão técnica `ANP-REVENDEDORES` (PUBLIC_OPEN, REFERENCE_ENRICHMENT) com escopo UF, fixture mínima, agregação por município+IBGE7, minimização de CNPJ e lineage Gold.
- Phase: F3.2 — `F3-SECTORAL-ANP`
- Spec: ROADMAP 1.2 § fontes setoriais; `contracts/sources/official-catalog.yaml`
- Components:
  - `parsers.py` — `parse_anp_revendedores_api`
  - `official_ingest.py` — registrar conector; remover do bloqueio
  - `gold.py`, `dashboards.py` (economia), `sectoral_enrichment.py`
  - catálogo + snapshot `anp-revendedores-ms-page1.json`
  - migration `0034_anp_revendedores_activation` → 0.3.31
- Data: PUBLIC_OPEN; fixture só em testes; escopo `uf=MS`, `numeropagina=1`; sem carga nacional
- Security: CNPJ/endereço/razão social fora de Silver/Gold; sem crédito
- Acceptance: ingest 200 com lineage; painel setorial parcial; demais setoriais bloqueados; testes verdes
- Human gates: inalterados; Gold `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`
