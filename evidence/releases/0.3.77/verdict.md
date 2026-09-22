# Verdict 0.3.77

## Fatia

`IPCA Livres` + `IPCA Serviços` (PERCENT_PER_YEAR, baseCalculo=1) via
multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Evidência técnica

- Fixtures OData mínimas (8 linhas Focus cada)
- Layout `bcb-olinda-expectativas-anuais-v12`; silverCount 160 (20×8)
- Migration: `0080_bcb_olinda_ipca_livres` → implementation_version `0.3.77`
- Unit + integration verdes locais
- UF re-probe: nenhum ACTIVATE_NOW

## Rollback

Reverter migration para `0079_bcb_olinda_investimento` e restringir
allowlist removendo IPCA Livres e IPCA Serviços no catálogo/runtime.
