# Release notes 0.3.37

## Fatia

Ativação técnica ICMS/IPVA de Rondônia (RO) via CSV SEFIN no portal `dados.ro.gov.br`.

## Entregue

- Connector `state_ro_csv` (ICMS wide `MM/YYYY` + join nome+UF; IPVA wide `jan/yy` + IBGE6→7)
- Fontes `ESTADO-RO-ICMS-QUOTA` / `ESTADO-RO-IPVA-QUOTA` `TECHNICALLY_APPROVED`
- Migration aditiva `0040_state_ro_activation` (meta 0.3.37)
- Fixtures oficiais mínimas `ro-icms-repasses-2022.csv` e `ro-ipva-repasses-2022.csv`

## Não-objetivos

- Demais UFs, GO ICMS (colunas ausentes), RJ (IP-blocked), carga nacional RFB
- Homologação humana do Gold; constituição de crédito a partir de fonte pública
