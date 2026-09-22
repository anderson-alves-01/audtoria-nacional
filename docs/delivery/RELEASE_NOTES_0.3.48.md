# RELEASE NOTES 0.3.48

## Fatia

Ativação técnica do Cadastro Central de Empresas municipal via IBGE/SIDRA tabela 9509
(`IBGE-SIDRA-CEMP` / connector `ibge_sidra_series`), após sondagem das UFs restantes
sem nova fonte estadual estruturada PUBLIC_OPEN.

## O que mudou

- Fonte `IBGE-SIDRA-CEMP`: variáveis 707 (pessoal ocupado), 662 (massa salarial) e 367
  (empresas atuantes), competência 2024, localidades N6.
- Presentation Gold `REFERENCE_QUANTITY` sem crédito; painéis executivo e economia.
- Fixture mínima `ibge-9509.json` e testes unitário/integração.
- Migration Alembic `0051_ibge_sidra_cemp` → `implementation_version=0.3.48`.
- Evidência de sondagem UF (RJ IP-block, GO ZIP 500, PI ICMS vazio, SC ≤2017, RR total).

## Não mudou

- Homologação humana Gold não solicitada.
- Gates G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 bloqueados.
- Sem carga nacional ilimitada, sem terraform apply, sem merge em main.
- UFs restantes sem CSV/API estruturado recente de ICMS/IPVA permanecem bloqueadas
  externamente.
