# Release notes 0.3.25

## Summary

Ativação técnica do CSV oficial de transferências municipais de Pernambuco (ICMS e IPVA) com lineage Gold, fixture mínima e shell estadual atualizado.

## Changes

- Parser `parse_state_pe_csv` com filtro por imposto e join IBGE7 por nome+UF.
- Fontes `ESTADO-ICMS-QUOTA` e `ESTADO-IPVA-QUOTA` em `TECHNICALLY_APPROVED` (layout distintos para idempotência).
- PE no catálogo estadual com `ingest_allowed=true`; BA/MG/RJ sem ingest.
- IPVA zero publicado como valor oficial.
- Migration aditiva `0028_state_pe_activation` (meta 0.3.25).

## Non-goals

- Carga estadual completa em runtime de CI.
- Homologação humana do Gold.
- Ativação BA/MG/RJ ou RFB nacional.
- Constituição de crédito ou cobrança.
