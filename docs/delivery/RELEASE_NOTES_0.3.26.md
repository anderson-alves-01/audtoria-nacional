# Release notes 0.3.26

## Summary

Ativação técnica do CSV oficial de repasses municipais da Bahia (ICMS e IPVA) com cabeçalho multi-coluna, fixture mínima, join IBGE7 e lineage Gold. PE permanece ativo.

## Changes

- Parser `parse_state_ba_csv` (`;`, utf-8/latin-1, número BR, colunas posicionais ICMS=4 / IPVA=13).
- Fontes `ESTADO-BA-ICMS-QUOTA` e `ESTADO-BA-IPVA-QUOTA` em `TECHNICALLY_APPROVED`.
- BA no catálogo estadual com `ingest_allowed=true`; MG/RJ sem ingest.
- Fixture `ba-repasses-municipios-2024.csv` e SICONFI-ENTES ampliado com Abaíra/Alagoinhas.
- Migration aditiva `0029_state_ba_activation` (meta 0.3.26).

## Non-goals

- Carga estadual completa em runtime de CI.
- Homologação humana do Gold.
- Ativação MG/RJ ou RFB nacional.
- Constituição de crédito ou cobrança.
