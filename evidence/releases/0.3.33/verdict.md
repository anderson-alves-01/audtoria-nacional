# 0.3.33 — BCB SGS allowlist activation (432+433)

## Verdict

TECHNICAL_GO for BCB-SGS-OLINDA activation via official SGS JSON API with
series allowlist Meta Selic (432) and IPCA (433), minimized fixtures (ultimos=3).
Gold remains `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
No human homologation requested.

## Delivered

- Connector `bcb_sgs_olinda` for `BCB-SGS-OLINDA`
- Allowlist-only ingest (432 + 433); secondary series fetched via SGS URL template
- REFERENCE_QUANTITY Gold (macro series points); lineage complete; no tax credit
- Sectoral panel `PARTIAL_TECHNICAL_ACTIVATION` (ANP+ANEEL+BCB); EPE/Anatel/CNES blocked
- Migration `0036_bcb_sgs_activation`

## Evidence

- `tests.txt` — unit + integration
- `angular.txt` — web specs

## Non-goals

- OLINDA OData activation, EPE/Anatel/CNES activation, additional SGS series beyond
  allowlist, UF ICMS/IPVA beyond prior activations, RFB national load, human Gold
  validation, tax credit
