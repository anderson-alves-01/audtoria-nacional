# RELEASE NOTES 0.3.49

## Fatia

Ativação técnica da quota-parte de ICMS de Goiás via XLSX mensal da Secretaria
da Economia (`ESTADO-GO-ICMS-QUOTA` / connector `state_go_economia_xlsx`),
complementando o IPVA já ativo no DataStore CKAN.

## O que mudou

- Fonte `ESTADO-GO-ICMS-QUOTA`: aba `MM-YYYY`, coluna ICMS `Bruto` (quota antes
  da retenção FUNDEB 20%), join IBGE7 por nome+UF.
- Presentation Gold `TRANSFER_AMOUNT_AS_PUBLISHED` sem crédito; painel
  transferências.
- Fixture mínima `go-economia-repasses-2024-11.xlsx` e testes unitário/integração.
- Migration Alembic `0052_state_go_icms_economia` → `implementation_version=0.3.49`.
- Catálogo estadual GO passa a ICMS+IPVA TECHNICALLY_APPROVED.

## Não mudou

- Homologação humana Gold não solicitada.
- Gates G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 bloqueados.
- Sem carga nacional ilimitada, sem terraform apply, sem merge em main.
- IPVA GO permanece no DataStore; ZIP anual CKAN ainda HTTP 500.
- Demais UFs sem CSV/API estruturado recente permanecem bloqueadas externamente.
