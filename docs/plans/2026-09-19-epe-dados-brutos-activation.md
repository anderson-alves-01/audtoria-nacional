# Plan — Ativação EPE Dados brutos (0.3.34)

- Goal: ativar `EPE-DADOS-ABERTOS` com URL estável do Anuário (`Dados brutos.xlsx`), escopo UF=MS, fixture mínima.
- Phase: F3.2 — `F3-SECTORAL-ANEEL-EPE` (EPE).
- Files: `parsers.py` (`parse_epe_open_files`), `official_ingest.py`, `sectoral_enrichment.py`, `gold.py`, `dashboards.py`, catálogo, snapshot CSV, migration `0037`, testes.
- Data: PUBLIC_OPEN; fixture oficial minimizada; sem crédito.
- Acceptance: ingest 200, Gold `REFERENCE_QUANTITY`, lineage, Anatel/CNES ainda bloqueados.
- Human gates: homologação Gold permanece pendente; não solicitar.
