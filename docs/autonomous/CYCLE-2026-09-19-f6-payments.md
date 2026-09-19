# Ciclo autônomo — F6 payments / active-debt / Procuradoria

Data: 2026-09-19  
Branch: `feat/official-public-ingest`  
PR: #2  
Versão: 0.3.19

## Seleção

- `F6-PAYMENTS`, `F6-ACTIVE-DEBT`, `F6-PROCURADORIA` (shells vazios relacionados).

## Entrega

- Backend: domain/application/entrypoints para `/v1/payments`, `/v1/active-debt`, `/v1/procuradoria`.
- Frontend: `/pagamentos`, `/divida-ativa`, `/procuradoria`.
- Testes unitários, integração e Angular.
- Fila, `current-state.yaml`, roadmap e evidências atualizados.

## Proibições respeitadas

Sem recuperação inventada, sem inscrição, sem alteração jurídica automática, sem merge em main, sem deploy.
