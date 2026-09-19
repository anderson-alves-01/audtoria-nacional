# Governança de gates (local)

## Princípios

- `GET /v1/program-gates` e `/v1/ops-governance` são somente leitura.
- `canApprove=false`, `humanApprovalFabricated=false`, `canDeploy=false`.
- Gates G0/G1/G4/G9/G10 permanecem BLOCKED até decisão institucional.
- G6/G7/G8 locais podem ser `LOCAL_GO` com componente oficial `OFFICIAL_BLOCKED`.

## Operação

1. Consultar `/gates` e `/operacao-governanca` na UI.
2. Não alterar feature flags para simular aprovação.
3. Documentar pendências em `docs/delivery/HUMAN_DECISIONS_REQUIRED.md`.
4. Evidências técnicas em `evidence/releases/<versão>/` não equivalem a homologação humana.

## Proibições

- Fabricar aceite de piloto (G9) ou autorização de produção (G10).
- Publicar indicadores com status `UNVALIDATED`, `QUARANTINED` ou `REJECTED`.
- Merge em `main` pelo orquestrador autônomo.
