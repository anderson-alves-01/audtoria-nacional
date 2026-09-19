# Release notes 0.3.28

## Fatia

Ativação técnica PUBLIC_OPEN de ICMS/IPVA do Espírito Santo (ES).

## Entregue

- Connector `state_es_csv` + fontes `ESTADO-ES-ICMS-QUOTA` / `ESTADO-ES-IPVA-QUOTA`
- CSV oficial `TransfEstadoMunicipios-2024` (`;`, UTF-8, IBGE7 nativo em `CodMunicipio`)
- ICMS via `IcmsTotal`; IPVA via `Ipva`; territórios sem IBGE7 em quarentena
- Fixture mínima (Afonso Cláudio, Vitória, território inválido)
- ES `TECHNICALLY_APPROVED`; PE/BA/MG intactos; GO permanece DISCOVERED (download CSV 500); RJ IP-blocked
- Migration aditiva `0031_state_es_activation` (meta 0.3.28)

## Não-objetivos

- Ativação GO/RJ, carga nacional RFB, homologação humana Gold, crédito tributário
