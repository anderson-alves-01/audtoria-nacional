# Ciclo 2026-09-21 — BCB OLINDA Balança Exportações / Importações

## Fatia

`Balança comercial` Focus anuais: multi-detalhe `Saldo` + `Exportações` +
`Importações` (USD_BILLION, baseCalculo=1) via multi-fetch
`bcb_olinda_expectativas` (PUBLIC_OPEN).

## Alterações

- `indicator_detalhe` aceita lista por indicador
- Allowlist detalhe: `Balança comercial: [Saldo, Exportações, Importações]`
- Layout `bcb-olinda-expectativas-anuais-v23`; silverCount 280
- Medianas de prova: Exportações 372.9 / Importações 294.0198 (Data 2026-09-18)
- Nenhum indicador Focus anual novo fora da allowlist encontrado no probe de nomes
- Próximo: UF tabular nova quando publicada; ou demais entity sets Focus OLINDA

## Rollback

Restaurar `indicator_detalhe.Balança comercial: Saldo`; Alembic → `0090_bcb_olinda_ipc_ipa`.
