# 0.3.35 — Anatel Meu Município UF-scoped activation

## Verdict

TECHNICAL_GO for ANATEL-DADOS-ABERTOS activation via official ZIP
(`meu_municipio.zip` → `Meu_Municipio_Acessos.csv`) with UF=MS,
competence 2025-11, service Banda Larga Fixa, max_rows=8, native IBGE7 and
minimized CSV fixture. Gold remains `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
No human homologation requested.

## Delivered

- Connector `anatel_dados_gov` for `ANATEL-DADOS-ABERTOS`
- UF + month scoped ingest; CSV fixture / ZIP live parser; Gold REFERENCE_QUANTITY
- Sectoral panel ANP+ANEEL+BCB+EPE+Anatel; CNES still blocked
- Migration `0038_anatel_meu_municipio`

## Evidence

- `tests.txt` — unit + integration (39 passed)
- `angular.txt` — web specs

## Non-goals

- CNES activation, additional UFs ICMS/IPVA, RFB national load, human Gold
  validation, tax credit
