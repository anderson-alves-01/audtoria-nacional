# Release notes 0.3.44

## Fatia

- Ativação técnica de ICMS e IPVA do Rio Grande do Norte via SEFAZ-RN Nextcloud (`state_rn_xls` / `ESTADO-RN-ICMS-QUOTA` / `ESTADO-RN-IPVA-QUOTA`)
- XLS Repasses Prefeituras (abas ICMS/IPVA), coluna mensal, join IBGE7 por nome+UF, competência `2026-01`
- Fixture mínima + quarentena de território sem IBGE; valores BRL arredondados a 2 casas
- MT Transparency XLSX marcado como série congelada ≤2015 (sem ativação); TO/PA/MA sem tabular estável neste ciclo
- Migration `0047_state_rn_activation`
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`; gates humanos inalterados
