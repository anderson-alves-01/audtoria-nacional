# Verdict 0.3.81

## Fatia

`PIB Despesa de consumo das famílias` (PERCENT_PER_YEAR, baseCalculo=1) via
multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Evidência técnica

- Fixture OData mínima (8 linhas Focus; primeira Mediana=1.4350)
- Layout `bcb-olinda-expectativas-anuais-v16`; silverCount 200 (25×8)
- Migration: `0084_bcb_olinda_pib_despesa_fam` → implementation_version `0.3.81`
- Unit + integration aplicáveis
- UF re-probe: nenhum ACTIVATE_NOW (status herdado de `evidence/releases/0.3.80/uf-reprobe-remaining.txt`)

## Rollback

Reverter migration para `0083_bcb_olinda_pib_fbcf` e restringir
allowlist removendo PIB Despesa de consumo das famílias no catálogo/runtime.
