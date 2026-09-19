# Release notes 0.3.30

## Fatia

Ativação técnica de ICMS e IPVA estadual de Mato Grosso do Sul via dump CKAN DataStore oficial.

## Entregue

- Connector `state_ms_csv` + fontes `ESTADO-MS-ICMS-QUOTA` / `ESTADO-MS-IPVA-QUOTA`
- Endpoint oficial: datastore dump mensal `repasses-dos-municipios-01_2026`
- Filtro por `Tipo_Repasse` (`REPASSE DE ICMS` / `REPASSE DE IPVA`)
- Join IBGE7 por nome+UF após remover prefixo `PREFEITURA MUNICIPAL DE`
- Fixture mínima; lineage Gold; MS `TECHNICALLY_APPROVED`
- Migration aditiva `0033_state_ms_activation` (meta 0.3.30)

## Não objetivos

- RJ (IP-blocked), GO ICMS, carga RFB nacional, homologação humana de Gold
