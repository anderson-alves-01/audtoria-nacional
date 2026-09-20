# RELEASE NOTES 0.3.46

## Fatia

Ativação técnica de ICMS/IPVA do Paraná via relatório HTML mensal SEFA/Portal da Transparência (`state_pr_html` / `ESTADO-PR-ICMS-QUOTA` / `ESTADO-PR-IPVA-QUOTA`).

## O que mudou

- Parser `parse_state_pr_html`: ICMS líquido (pós-FUNDEB) e IPVA; join IBGE7 por nome+UF; quarentena sem IBGE.
- Catálogo oficial e estadual: PR `TECHNICALLY_APPROVED`, `ingestAllowed=true`.
- Provenance: AP (link SEFAZ 404), RR (painel sem split ICMS/IPVA), DF (não aplicável).
- Migration Alembic `0049_state_pr_activation` → `implementation_version=0.3.46`.
- Fixture mínima e testes unitários/integração sem crédito tributário.

## Não mudou

- Homologação humana Gold não solicitada.
- Gates G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 bloqueados.
- Sem carga nacional ilimitada, sem terraform apply, sem merge em main.
