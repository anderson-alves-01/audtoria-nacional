# G8 — calendário IBS/CBS sintético e não vinculante (0.3.7)

## Goal and user outcome

Expor um calendário regulatório versionado, com fontes do catálogo, leiaute placeholder, mapa de impacto ISS e simulação explícita como **não vinculante**. Nenhuma data, alíquota ou obrigação é tratada como operacional.

## Roadmap phase and epic

ROADMAP 2026 Fase 8 (G8) em modo local. Gate oficial “norma homologada” permanece **NO-GO**.

## Approved specification

- `docs/legal/BOUNDARIES.md`: simulações IBS/CBS não vinculantes até homologação.
- Skill `ibs-cbs-readiness`: datas e leiautes configuráveis; nunca inferir obrigação.
- Invariante 9: regra tributária é versionada e homologada.

## Components and files

- `apps/api/src/sirta_api/domain/regulatory.py`
- `apps/api/src/sirta_api/application/regulatory.py`
- `apps/api/src/sirta_api/entrypoints/regulatory.py`
- `apps/api/src/sirta_api/adapters/db/models.py` (`regulatory_items`)
- `alembic/versions/0009_g8_regulatory.py`
- `GET /v1/regulatory/ibs-cbs`
- Angular `/calendario`
- `contracts/openapi/sirta-v1.yaml`

## Consumed / produced interfaces

Consome contexto F0 (OIDC, tenant, território, finalidade). Produz lista de itens `NON_BINDING` com `operational=false` e `homologated=false`.

## Data classification

Somente catálogo sintético e URLs públicas do `BOUNDARIES.md`. Sem dado fiscal real.

## Security

GET exige leitura fiscal. `tech_admin` recebe 403. Evento de auditoria `regulatory.list`.

## Migration and rollback

`0009_g8_regulatory` aditivo (`create_all`). Rollback: `git revert` e `drop table regulatory_items` apenas após depreciação; nesta fatia o downgrade é no-op.

## Acceptance criteria

- Itens do catálogo têm `binding=false` e `status=NON_BINDING`.
- Resposta declara `operational=false` e `homologated=false`.
- Tentativa de uso operacional sem homologação falha no domínio.
- GET é idempotente (não duplica códigos).
- UI mostra aviso de não vinculante e não afirma homologação.
- Spec 0.3.0 permanece.

## Evidence path

`evidence/releases/0.3.7/`

## Human gates

G8 oficial (fontes homologadas para uso operacional), G0 municipal, G1 diagnóstico, G4 especialista, G9 piloto e G10 produção: **BLOQUEADO**.
