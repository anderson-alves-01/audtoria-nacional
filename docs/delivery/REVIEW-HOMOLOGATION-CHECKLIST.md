# Checklist de revisão e homologação — 0.3.13

Uso: revisão técnica da branch `feat/roadmap-technical-completion`. Itens institucionais ficam **não aplicáveis** até o gate humano correspondente.

## Revisão técnica (esta branch)

- [ ] Diff `main...HEAD` revisado (109 arquivos nesta auditoria)
- [ ] Spec `0.3.0` inalterada; implementação `0.3.13`
- [ ] Pytest 99 passed (unitário, contrato, integração, Alembic)
- [ ] Angular 15 SUCCESS + `ng build`
- [ ] OpenAPI `contracts/openapi/sirta-v1.yaml` válida
- [ ] `ruff format --check` e `ruff check` verdes
- [ ] Imagens `apps/api`, `apps/workers`, `apps/web` constroem
- [ ] `terraform fmt -check` e `terraform validate` sem apply
- [ ] Scan de segredos sem achado novo
- [ ] Evidências `evidence/releases/0.3.11/` … `0.3.13/` presentes (pytest, angular, CI, verdict)

## Invariantes de produto (não negociáveis nesta revisão)

- [ ] Ingestão sintética **não** cria `TaxCredit`
- [ ] Nenhuma chamada HTTP a SIDRA/Tesouro/Planalto no runtime de ingestão
- [ ] `/gates` GET-only; `canApprove=false`
- [ ] Checklists G0/G1 com `met=false`
- [ ] IBS/CBS: `NON_BINDING`, `binding=false`, `operational=false`, `homologated=false`
- [ ] G0, G1, G4, G9, G10 = BLOCKED; G7/G8 oficiais = OFFICIAL_BLOCKED
- [ ] Flags em `config/feature-flags.yaml` todas `false`
- [ ] Nenhum `terraform apply` no histórico desta fatia

## Homologação institucional (fora desta PR)

- [ ] G0 — patrocinador, município, DPA
- [ ] G1 — diagnóstico homologado
- [ ] G4 — especialista ISS
- [ ] G7 oficial — conector Tesouro autorizado
- [ ] G8 oficial — norma IBS/CBS homologada
- [ ] G9 — aceite de piloto
- [ ] G10 — autorização de produção

A PR para `main` é revisão técnica. Não é aceite de piloto nem autorização de produção.

## Lentes de review (ROADMAP)

1. Conformidade com spec 0.3.0 e ROADMAP 1.2
2. Arquitetura hexagonal e migrations aditivas
3. Segurança, LGPD, isolamento de tenant, custódia
4. Qualidade de dados sintéticos, linhagem e rollback lógico

O implementador não aprova o próprio gate de segurança crítica, metodologia fiscal ou produção.
