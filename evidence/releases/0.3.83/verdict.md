# Verdict 0.3.83

## Fatia

`PIB Exportação de bens e serviços` (PERCENT_PER_YEAR, baseCalculo=1) via
multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Evidência técnica

- Fixture OData mínima (8 linhas Focus; primeira Mediana=4.2676)
- Layout `bcb-olinda-expectativas-anuais-v18`; silverCount 216 (27×8)
- Migration: `0086_bcb_olinda_pib_exportacao` → implementation_version `0.3.83`
- Unit + integration aplicáveis
- UF re-probe: nenhum ACTIVATE_NOW (status herdado de `evidence/releases/0.3.82/uf-reprobe-remaining.txt`)

## Rollback

Reverter migration para `0085_bcb_olinda_pib_despesa_adm` e restringir
allowlist removendo PIB Exportação de bens e serviços no catálogo/runtime.
