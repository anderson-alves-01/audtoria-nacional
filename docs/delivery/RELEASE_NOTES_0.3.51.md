# RELEASE NOTES 0.3.51

## Fatia

Ativação allowlist do CSV mensal Tesouro Transparente para ITR, IPI-Exportação e Royalties, reutilizando o conector `tesouro_monthly_csv` já usado pelo FPM.

## Entregas

- `TESOURO-ITR-VALORES` (`transfer_item_allowlist: [ITR]`).
- `TESOURO-IPI-EXP-VALORES` (`transfer_item_allowlist: [IPI-EXP]`; no arquivo 202609 as linhas observadas destinam-se a FUNDEB).
- `TESOURO-ROYALTIES-VALORES` (`transfer_destination_allowlist: [Royalties]`; Item FEP/CFEM/ANP/CFH/PEA/ITA).
- Parser parametrizado; Gold `TRANSFER_AMOUNT_AS_PUBLISHED`; dashboard transferências atualizado.
- Migration Alembic `0054_tesouro_monthly_allowlist` → `implementation_version=0.3.51`.

## Não inclui

- Homologação humana de Gold.
- Carga nacional ilimitada do CSV Tesouro.
- Ativação de UFs restantes sem tabular recente.
- Carga RFB nacional ou Portal da Transparência com credencial.
