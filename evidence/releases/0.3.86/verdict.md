# Verdict 0.3.86

## Fatia

`IPCA-15` (PERCENT_PER_YEAR, baseCalculo=0) via multi-fetch
`bcb_olinda_expectativas` (PUBLIC_OPEN). Última publicação Focus Anuais
observada: 2021-02-17 (série congelada na fonte; ainda fetchável).
baseCalculo=1 retorna zero linhas.

## Evidência técnica

- Fixture OData mínima (8 linhas Focus; primeira Mediana=3.79)
- Layout `bcb-olinda-expectativas-anuais-v21`; silverCount 240 (30×8)
- Migration: `0089_bcb_olinda_ipca15` → implementation_version `0.3.86`
- Unit + integration aplicáveis
- UF re-probe: nenhum ACTIVATE_NOW (status herdado de `evidence/releases/0.3.85/uf-reprobe-remaining.txt`)

## Rollback

Reverter migration para `0088_bcb_olinda_prod_ind` e restringir
allowlist removendo IPCA-15 no catálogo/runtime.
