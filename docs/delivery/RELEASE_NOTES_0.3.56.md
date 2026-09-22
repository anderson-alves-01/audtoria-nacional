# RELEASE NOTES 0.3.56

## Resumo

Ativação de IPI estadual em PE, BA e MG nos mesmos arquivos PUBLIC_OPEN já aprovados para ICMS/IPVA.

## Entrega

- Parsers `state_pe_csv`, `state_ba_csv` e `state_mg_csv` aceitam `tax=IPI`.
- Fontes `ESTADO-PE-IPI-QUOTA`, `ESTADO-BA-IPI-QUOTA` e `ESTADO-MG-IPI-QUOTA`.
- Dashboard `/transferencias` inclui as novas fontes.
- Migration Alembic `0059_state_pe_ba_mg_ipi` → `implementation_version=0.3.56`.

## Restrições

- Sem crédito, cobrança, inscrição ou notificação.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
- Gates humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados.
- MS IPI/CIDE sem `Tipo_Repasse` correspondente no fixture; UFs restantes sem tabular recente.
