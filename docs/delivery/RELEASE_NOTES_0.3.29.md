# Release notes 0.3.29

## Fatia

Ativação técnica de IPVA estadual de Goiás via dump CKAN DataStore oficial.

## Entregue

- Connector `state_go_csv` + fonte `ESTADO-GO-IPVA-QUOTA`
- Endpoint oficial: datastore dump (CSV upload permanece HTTP 500)
- Schema mensal 2026 publicado contém apenas IPVA (`VALR_IPVA`); ICMS não ativado
- Join IBGE7 por nome+UF; fixture mínima; lineage Gold
- GO `TECHNICALLY_APPROVED` com `ingest_allowed=true` e `taxes: [IPVA]`
- Migration aditiva `0032_state_go_ipva_activation` (meta 0.3.29)

## Não objetivos

- ICMS GO (colunas ausentes no datastore 2026)
- RJ (IP-blocked), carga RFB nacional, homologação humana de Gold
