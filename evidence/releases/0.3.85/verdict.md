# Verdict 0.3.85

## Fatia

`Produção industrial` (PERCENT_PER_YEAR, baseCalculo=1) via multi-fetch
`bcb_olinda_expectativas` (PUBLIC_OPEN). Última publicação Focus Anuais
observada: 2021-09-13 (série congelada na fonte; ainda fetchável).

## Evidência técnica

- Fixture OData mínima (8 linhas Focus; primeira Mediana=6.3348)
- Layout `bcb-olinda-expectativas-anuais-v20`; silverCount 232 (29×8)
- Migration: `0088_bcb_olinda_prod_ind` → implementation_version `0.3.85`
- Unit + integration aplicáveis
- UF re-probe: nenhum ACTIVATE_NOW (status herdado de `evidence/releases/0.3.84/uf-reprobe-remaining.txt`)

## Rollback

Reverter migration para `0087_bcb_olinda_pib_importacao` e restringir
allowlist removendo Produção industrial no catálogo/runtime.
