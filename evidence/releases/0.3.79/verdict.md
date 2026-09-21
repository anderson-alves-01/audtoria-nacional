# Verdict 0.3.79

## Fatia

`IPCA Bens industrializados` (PERCENT_PER_YEAR, baseCalculo=1) via
multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Evidência técnica

- Fixture OData mínima (8 linhas Focus; primeira Mediana=3.4641)
- Layout `bcb-olinda-expectativas-anuais-v14`; silverCount 184 (23×8)
- Migration: `0082_bcb_olinda_ipca_bens` → implementation_version `0.3.79`
- Unit + integration aplicáveis
- UF re-probe: nenhum ACTIVATE_NOW (status herdado de `evidence/releases/0.3.78/uf-reprobe-remaining.txt`)

## Rollback

Reverter migration para `0081_bcb_olinda_ipca_admin` e restringir
allowlist removendo IPCA Bens industrializados no catálogo/runtime.
