# Release notes 0.3.27

## Summary

Ativa ingestão oficial PUBLIC_OPEN de ICMS/IPVA de Minas Gerais via datapackage
Frictionless (CSV.gz) com IBGE7 nativo e dimensões município/tempo.

## Changes

- Connector `state_mg_csv` + fontes `ESTADO-MG-ICMS-QUOTA` / `ESTADO-MG-IPVA-QUOTA`
- Join `ft_repasse_mun` × `dm_municipio` × `dm_tempo_mensal`; quarentena sem IBGE7
- Catálogo estadual MG `TECHNICALLY_APPROVED`; PE/BA intactos; RJ IP-blocked
- Migration aditiva `0030_state_mg_activation` (meta 0.3.27)

## Non-goals

- Homologação humana do Gold, carga nacional RFB, ativação RJ, crédito tributário
