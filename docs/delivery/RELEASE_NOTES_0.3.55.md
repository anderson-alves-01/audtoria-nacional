# RELEASE NOTES 0.3.55

## Resumo

Ativação de IPI estadual em CE, AL e RN nos mesmos arquivos PUBLIC_OPEN já aprovados para ICMS/IPVA.

## Entrega

- Parsers `state_ce_xls`, `state_al_xls` e `state_rn_xls` aceitam `tax=IPI`.
- Fontes `ESTADO-CE-IPI-QUOTA`, `ESTADO-AL-IPI-QUOTA` e `ESTADO-RN-IPI-QUOTA`.
- Dashboard `/transferencias` inclui as novas fontes.
- Migration Alembic `0058_state_ce_al_rn_ipi` → `implementation_version=0.3.55`.

## Restrições

- Sem crédito, cobrança, inscrição ou notificação.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
- Gates humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados.
- UFs restantes sem tabular recente permanecem PROVENANCE_VERIFIED / DISCOVERED / IP-blocked.
