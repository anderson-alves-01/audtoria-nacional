# Release notes 0.3.13 — conclusão técnica local

Spec: `0.3.0` (inalterada)  
Roadmap: `1.2`  
Branch: `feat/roadmap-technical-completion` (sem merge em `main`)  
Implementação: `0.3.13`  
Release stage: `TERRAFORM_MODULES_DOCS`

## Resumo

Esta linha fecha as fatias técnicas locais desbloqueadas do ROADMAP 1.2. Inclui higiene Alembic, catálogo sintético de fontes, ingestão IBGE/Tesouro sem crédito tributário, checklists G0/G1 somente leitura e módulos Terraform documentation-only.

Nenhum gate institucional foi aprovado, contornado ou inferido.

## Versões nesta linha

| Versão | Commit | CI | Evidência |
|---|---|---|---|
| 0.3.8 | `74e7852` | [35378698815](https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35378698815) | `evidence/releases/0.3.8/` |
| 0.3.9 | `140e24c` | [35379184092](https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35379184092) | `evidence/releases/0.3.9/` |
| 0.3.10 | `09ab340` | [35379564590](https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35379564590) | `evidence/releases/0.3.10/` |
| 0.3.11 | `0a03c3c` | [35409091892](https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35409091892) | `evidence/releases/0.3.11/` |
| 0.3.12 | `cd412dd` | [35409413760](https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35409413760) | `evidence/releases/0.3.12/` |
| 0.3.13 | `2e5dd38` | [35409721281](https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35409721281) | `evidence/releases/0.3.13/` |

Registro de CI do closeout: `57d4b12` ([35409814778](https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35409814778)).

## O que entra em 0.3.13

- Módulo `infra/terraform/modules/documentation_stack` (provider `hashicorp/null`, `prevent_destroy`)
- Ambientes `local`, `dev`, `staging` e `prod` apenas como documentação
- `terraform fmt -check` e `terraform validate -backend=false`
- `terraform apply` permanece proibido

## O que já estava na linha e permanece

- Ingestão sintética IBGE e stub Tesouro: `taxCreditCreated=false`, `wouldDownloadFullBase=false`
- `/gates` somente leitura; `canApprove=false`; checklists G0/G1 unmet
- IBS/CBS: `NON_BINDING`, `binding=false`, `operational=false`, `homologated=false`
- Flags oficiais em `config/feature-flags.yaml` todas `false`

## Rollback

`git revert` dos commits da fatia. Migration `0015` é aditiva.

## Fora de escopo

Conectores oficiais, dado fiscal real, DPA, IAM de nuvem, produção, merge em `main`.
