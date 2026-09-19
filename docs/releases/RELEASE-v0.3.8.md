# Release v0.3.8 - Alembic hygiene

## Objetivo

Separar schema de seed sintético e tornar `alembic upgrade` reproduzível em banco vazio, em `0004 -> head` válido e após `drop_all` das tabelas de domínio.

`release_stage: ALEMBIC_HYGIENE`  
`spec_version: 0.3.0` (inalterada)

## Escopo entregue

- Migrations `0003`, `0004`, `0005` e `0007` sem carga mutável.
- `seed_synthetic` idempotente via `python -m sirta_api.adapters.db.seed`.
- pytest deixa de usar `Base.metadata.drop_all` no banco compartilhado.
- Serviço Compose `migrate` e seed no start da API.
- CI: migrate → seed → tests.
- Caminhos testados em `sirta_migtest` (isolado): `base -> head`, `0004 -> head`, `0004 -> head` após drop de domínio.

## Fora de escopo

- Novas regras tributárias, conectores oficiais, G0–G1, G9–G10.

## Rollback

```bash
git revert <sha-da-fatia>
```

`0010_alembic_hygiene` é aditiva.

## Evidências

`evidence/releases/0.3.8/`
