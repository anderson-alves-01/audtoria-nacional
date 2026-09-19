# Release notes 0.3.38

## Fatia

Ativação técnica ICMS do Acre (AC) via CSV SEPLAG no portal `dados.ac.gov.br`.

## Entregue

- Connector `state_ac_csv` (wide anual `Cod IBGE` nativo; competência filtrada)
- Fonte `ESTADO-AC-ICMS-QUOTA` `TECHNICALLY_APPROVED` (IPVA não publicado)
- SC catalogada como arrecadação (`VL_PGTO`), não quota-parte
- Migration aditiva `0041_state_ac_activation` (meta 0.3.38)
- Fixture oficial mínima `ac-icms-repasses-2021.csv`

## Não-objetivos

- Demais UFs, GO ICMS, RJ (IP-blocked), SC como transfer, carga nacional RFB
- Homologação humana do Gold; constituição de crédito a partir de fonte pública
