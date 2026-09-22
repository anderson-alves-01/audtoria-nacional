# Verdict 0.3.75

## Fatia

`Taxa de desocupação` (PERCENT, baseCalculo=1) via
multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Evidência técnica

- Fixture OData mínima (8 linhas Focus)
- Layout `bcb-olinda-expectativas-anuais-v10`; silverCount 136 (17×8)
- Migration: `0078_bcb_olinda_taxa_desocup` → implementation_version `0.3.75`
- Unit + integration verdes locais
- UF re-probe: nenhum ACTIVATE_NOW

## Rollback

Reverter migration para `0077_bcb_olinda_divida_bruta` e restringir
allowlist removendo Taxa de desocupação no catálogo/runtime.
