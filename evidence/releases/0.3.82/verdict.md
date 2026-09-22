# Verdict 0.3.82

## Fatia

`PIB Despesa de consumo da administração pública` (PERCENT_PER_YEAR, baseCalculo=1) via
multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Evidência técnica

- Fixture OData mínima (8 linhas Focus; primeira Mediana=2.2)
- Layout `bcb-olinda-expectativas-anuais-v17`; silverCount 208 (26×8)
- Migration: `0085_bcb_olinda_pib_despesa_adm` → implementation_version `0.3.82`
- Parser: rowId >64 chars usa digest SHA-256 estável (evita colisão no nome longo)
- Unit + integration aplicáveis
- UF re-probe: nenhum ACTIVATE_NOW (status herdado de `evidence/releases/0.3.81/uf-reprobe-remaining.txt`)

## Rollback

Reverter migration para `0084_bcb_olinda_pib_despesa_fam` e restringir
allowlist removendo PIB Despesa de consumo da administração pública no catálogo/runtime.
