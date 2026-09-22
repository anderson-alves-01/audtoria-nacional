# RELEASE NOTES 0.3.52

## Resumo

Ativação allowlist do CSV mensal Tesouro Transparente para LC 176/2020 (ADO25), reutilizando o conector `tesouro_monthly_csv`.

## Entrega

- `TESOURO-LC176-VALORES` (`transfer_item_allowlist: ["LC 176/2020 (ADO25)"]`).
- Probe 202609: CIDE e FEX **não** constam no CSV mensal municipal; permanecem sem ativação neste conector.
- Dashboard `/transferencias` inclui a nova fonte.
- Migration Alembic `0055_tesouro_lc176_allowlist` → `implementation_version=0.3.52`.

## Restrições

- Sem crédito, cobrança, inscrição ou notificação.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
- Gates humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados.
