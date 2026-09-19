# Plan — Ativação BCB SGS allowlist (0.3.33)

- `parsers.py` — `parse_bcb_sgs_olinda`
- `official_ingest.py` — PARSERS + `_parse_bcb_sgs_allowlist`
- `gold.py`, `dashboards.py` (economia), `sectoral_enrichment.py`
- catálogo + snapshots `bcb-sgs-432-ultimos3.json` / `bcb-sgs-433-ultimos3.json`
- migration `0036_bcb_sgs_activation` → 0.3.33
