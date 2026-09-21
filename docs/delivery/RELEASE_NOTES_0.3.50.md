# RELEASE NOTES 0.3.50

## Fatia

Ativação de IPI e CIDE já publicados nos arquivos PUBLIC_OPEN de ES e GO, sem novas UFs.

## Entregas

- `ESTADO-ES-IPI-QUOTA` e `ESTADO-ES-CIDE-QUOTA` via `state_es_csv` (colunas `Ipi` e `CotaParteCide`).
- `ESTADO-GO-IPI-QUOTA` via `state_go_economia_xlsx` (coluna Bruto do grupo IPI-Exportação).
- Modalidades Gold `IPI_QUOTA` e `CIDE_QUOTA`; `createsTaxCredit=false`.
- Migration Alembic `0053_state_es_go_ipi_cide` → `implementation_version=0.3.50`.

## Não inclui

- Homologação humana de Gold.
- Ativação de UFs restantes sem tabular recente (RJ, SP, AM, AP, RR, MT, SC, SE, PB, TO, PI ICMS).
- Carga nacional RFB ou Portal da Transparência com credencial.
