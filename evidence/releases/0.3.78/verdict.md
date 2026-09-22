# Verdict 0.3.78

## Fatia

`IPCA Administrados` + `IPCA Alimentação no domicílio` (PERCENT_PER_YEAR,
baseCalculo=1) via multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Evidência técnica

- Fixtures OData mínimas (8 linhas Focus cada)
- Layout `bcb-olinda-expectativas-anuais-v13`; silverCount 176 (22×8)
- Migration: `0081_bcb_olinda_ipca_admin` → implementation_version `0.3.78`
- Unit + integration verdes locais
- UF re-probe: nenhum ACTIVATE_NOW

## Rollback

Reverter migration para `0080_bcb_olinda_ipca_livres` e restringir
allowlist removendo IPCA Administrados e IPCA Alimentação no domicílio no
catálogo/runtime.
