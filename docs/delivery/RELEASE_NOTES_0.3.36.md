# Release notes 0.3.36

## Fatia

Ativação técnica CNES/DATASUS via API DEMAS com escopo UF=MS (`codigo_uf=50`, `limit=8`).

## Entregue

- Connector `cnes_datasus_open` com agregação municipal IBGE7 e minimização de PII
- Painel setorial ANP+ANEEL+BCB+EPE+Anatel+CNES; CNES `ingestAllowed=true`
- Migration aditiva `0039_cnes_demas_uf_activation` (meta 0.3.36)
- Fixture oficial mínima `cnes-estabelecimentos-ms-limit8.json`

## Não-objetivos

- Outras UFs ICMS/IPVA, carga nacional RFB, homologação humana do Gold
- Constituição de crédito a partir de fonte pública
