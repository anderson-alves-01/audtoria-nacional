# Verdict 0.3.80

## Fatia

`PIB Formação Bruta de Capital Fixo` (PERCENT_PER_YEAR, baseCalculo=1) via
multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Evidência técnica

- Fixture OData mínima (8 linhas Focus; primeira Mediana=0.9000)
- Layout `bcb-olinda-expectativas-anuais-v15`; silverCount 192 (24×8)
- Migration: `0083_bcb_olinda_pib_fbcf` → implementation_version `0.3.80`
- Unit + integration aplicáveis
- UF re-probe: nenhum ACTIVATE_NOW (status herdado de `evidence/releases/0.3.79/uf-reprobe-remaining.txt`)

## Rollback

Reverter migration para `0082_bcb_olinda_ipca_bens` e restringir
allowlist removendo PIB Formação Bruta de Capital Fixo no catálogo/runtime.
