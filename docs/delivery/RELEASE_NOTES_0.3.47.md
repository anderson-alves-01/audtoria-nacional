# RELEASE NOTES 0.3.47

## Fatia

Ativação técnica do componente ecológico ICMS Verde do Pará via planilha mensal SEMAS (`state_pa_icms_verde_xlsx` / `ESTADO-PA-ICMS-VERDE-QUOTA`).

## O que mudou

- Parser `parse_state_pa_icms_verde_xlsx`: colunas mensais, modalidade `ICMS_VERDE_QUOTA`, join IBGE7 por nome+UF, quarentena sem IBGE.
- Catálogo oficial e estadual: PA `TECHNICALLY_APPROVED` apenas para ICMS Verde; cota ICMS/IPVA plena permanece em DOE PDF.
- Migration Alembic `0050_state_pa_icms_verde` → `implementation_version=0.3.47`.
- Fixture mínima e testes unitários/integração sem crédito tributário.
- Fixture SICONFI-ENTES ampliada com Belém/Ananindeua (PA) para join.

## Não mudou

- Homologação humana Gold não solicitada.
- Gates G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 bloqueados.
- Sem carga nacional ilimitada, sem terraform apply, sem merge em main.
- RJ continua IP-blocked; TO/SP/AM/SC/MT/AP/RR sem ativação plena.
