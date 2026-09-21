# Verdict 0.3.88

## Fatia

BCB OLINDA Expectativas: `Balança comercial` multi-detalhe
(`Saldo` + `Exportações` + `Importações`).

## Evidência técnica

- Fixtures oficiais minimizadas (top=8) para Exportações e Importações
- Probe: Data 2026-09-18; Medianas 372.9 / 294.0198
- Layout `bcb-olinda-expectativas-anuais-v23`; silverCount 280 (33×8 + 16)
- Migration: `0091_bcb_olinda_balanca_exim` → implementation_version `0.3.88`
- Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Sem carga nacional; sem crédito

## Próximo

UF tabular nova quando publicada; ou demais entity sets Focus OLINDA
(mensais/trimestrais) / indicadores ainda fora da allowlist anual.
