# RELEASE NOTES 0.3.62

## Resumo

Ativação allowlist do CSV mensal Tesouro Transparente para complementação
FUNDEB (COUN VAAT/VAAR/VAAF) e AJUSTE FUNDEB VAAT, reutilizando o conector
`tesouro_monthly_csv`.

## Entrega

- `TESOURO-FUNDEB-COMPLEMENT-VALORES` (`transfer_item_allowlist`:
  COUN VAAT, COUN VAAR, COUN VAAF, AJUSTE FUNDEB VAAT).
- Probe 202609: milhares de linhas COUN*/AJUSTE; distinto de retenções
  FPM/IPI-EXP→FUNDEB.
- Dashboard `/transferencias` inclui a nova fonte.
- Migration Alembic `0065_tesouro_fundeb_complement` →
  `implementation_version=0.3.62`.

## Restrições

- Sem crédito, cobrança, inscrição ou notificação.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
- Gates humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados.
- UFs restantes sem tabular recente: RJ (IP block), PI ICMS, SP, SC≤2017,
  RR, PA plena, AP, MT, SE/PB, AM, TO.
