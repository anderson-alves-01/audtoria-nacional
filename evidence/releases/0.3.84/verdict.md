# Verdict 0.3.84

## Fatia

`PIB Importação de bens e serviços` (PERCENT_PER_YEAR, baseCalculo=1) via
multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Evidência técnica

- Fixture OData mínima (8 linhas Focus; primeira Mediana=3.0)
- Layout `bcb-olinda-expectativas-anuais-v19`; silverCount 224 (28×8)
- Migration: `0087_bcb_olinda_pib_importacao` → implementation_version `0.3.84`
- Unit + integration aplicáveis
- UF re-probe: nenhum ACTIVATE_NOW (status herdado de `evidence/releases/0.3.83/uf-reprobe-remaining.txt`)

## Rollback

Reverter migration para `0086_bcb_olinda_pib_exportacao` e restringir
allowlist removendo PIB Importação de bens e serviços no catálogo/runtime.
