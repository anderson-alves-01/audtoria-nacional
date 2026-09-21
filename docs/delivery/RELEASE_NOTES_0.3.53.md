# RELEASE NOTES 0.3.53

## Resumo

Ativação allowlist do CSV mensal Tesouro Transparente para IOF-Ouro, reutilizando o conector `tesouro_monthly_csv`.

## Entrega

- `TESOURO-IOF-OURO-VALORES` (`transfer_item_allowlist: ["IOF Ouro"]`, `transfer_name: IOF-Ouro`).
- Probe 202609: 31 linhas IOF-Ouro; CIDE e FEX permanecem ausentes neste CSV.
- Dashboard `/transferencias` inclui a nova fonte.
- Migration Alembic `0056_tesouro_iof_ouro_allowlist` → `implementation_version=0.3.53`.

## Restrições

- Sem crédito, cobrança, inscrição ou notificação.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
- Gates humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados.
