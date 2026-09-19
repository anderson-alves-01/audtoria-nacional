# 0.3.34 — EPE Anuário Dados brutos UF-scoped activation

## Verdict

TECHNICAL_GO for EPE-DADOS-ABERTOS activation via stable official XLSX
(`Dados brutos.xlsx`) with UF=MS, competence_year=2024, max_rows=8 and
minimized CSV fixture. Gold remains `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
No human homologation requested.

## Delivered

- Connector `epe_open_files` for `EPE-DADOS-ABERTOS`
- UF + year scoped ingest; CSV fixture / XLSX live parser; Gold REFERENCE_QUANTITY
- Sectoral panel ANP+ANEEL+BCB+EPE; Anatel/CNES still blocked
- Migration `0037_epe_dados_brutos_activation`

## Evidence

- `tests.txt` — unit + integration
- `angular.txt` — web specs

## Non-goals

- Anatel/CNES activation, additional UFs ICMS/IPVA, RFB national load, human Gold
  validation, tax credit
