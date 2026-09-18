# Release v0.3.2 - Sprint 2 credit validation

## Objetivo

Entregar `ValidateCredit` sobre a especificação 0.3.0, sem reescrever `RELEASE-v0.3.0.md` nem `RELEASE-v0.3.1.md`.

`release_stage: S2_CREDIT_VALIDATION`

## Escopo entregue

- Estados ortogonais de validação no domínio.
- Checklist configurável `credit-legality-v1` (não é parecer jurídico).
- Evidências sintéticas com SHA-256.
- `POST /v1/tax-credits/{creditId}/validations` com `Idempotency-Key`.
- Segregação: só validador; criador não valida o próprio crédito.
- Transição inválida → 409 sem alteração parcial.
- Formulário Angular mínimo; autorização permanece na API.
- Cobrança continua 404.

## Fora de escopo

- StartAdministrativeCollection (Sprint 3).
- G0 municipal, dado real, nuvem, ISR, Gold, pipelines.

## Rollback

```bash
docker compose down -v
git revert <sha-da-fatia>
```

## Evidências

`evidence/releases/0.3.2/`

## Revisão

Revisão independente de segurança/fiscal permanece gate humano. O implementador não autoaprova esse gate.
