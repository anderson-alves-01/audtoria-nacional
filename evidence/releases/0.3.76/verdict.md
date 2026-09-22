# Verdict 0.3.76

## Fatia

`Investimento direto no país` (USD_BILLION, baseCalculo=1) via
multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Evidência técnica

- Fixture OData mínima (8 linhas Focus)
- Layout `bcb-olinda-expectativas-anuais-v11`; silverCount 144 (18×8)
- Migration: `0079_bcb_olinda_investimento` → implementation_version `0.3.76`
- Unit + integration verdes locais
- UF re-probe: nenhum ACTIVATE_NOW

## Rollback

Reverter migration para `0078_bcb_olinda_taxa_desocup` e restringir
allowlist removendo Investimento direto no país no catálogo/runtime.
