# RELEASE NOTES 0.3.54

## Resumo

Ativação dos CSV COINT do Tesouro Transparente para CIDE-Combustíveis e FEX por município — fonte alternativa ao CSV mensal constitucional (sem CIDE/FEX).

## Entrega

- Conector `tesouro_coint_municipio_csv` (layout wide anos × mês; join IBGE por nome+UF).
- Fontes `TESOURO-CIDE-VALORES` e `TESOURO-FEX-VALORES` (`max_rows=8`, competência `2025-01`).
- Dashboard `/transferencias` inclui as novas fontes.
- Migration Alembic `0057_tesouro_coint_cide_fex` → `implementation_version=0.3.54`.

## Restrições

- Sem crédito, cobrança, inscrição ou notificação.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
- Gates humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados.
- Sem carga nacional ilimitada dos CSV COINT (~12–14 MiB).
