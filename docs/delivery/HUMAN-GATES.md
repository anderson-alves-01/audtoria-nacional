# Gates humanos bloqueados

Este arquivo registra o que a implementação local **não** pode avançar sem autorização institucional. Detalhe operacional: `HUMAN_DECISIONS_REQUIRED.md`.

Data: 2026-09-18  
Implementação: 0.3.13 (`TERRAFORM_MODULES_DOCS`)  
HEAD: `57d4b12`

## Concluído localmente (sintético)

| Fatia | Versão | Commit | CI | Evidência |
|---|---|---|---|---|
| Higiene Alembic | 0.3.8 | `74e7852` | [35378698815](https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35378698815) | `evidence/releases/0.3.8/` |
| Catálogo de fontes | 0.3.9 | `140e24c` | [35379184092](https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35379184092) | `evidence/releases/0.3.9/` |
| Gates + Terraform docs | 0.3.10 | `09ab340` | [35379564590](https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35379564590) | `evidence/releases/0.3.10/` |
| Ingestão IBGE | 0.3.11 | `0a03c3c` | [35409091892](https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35409091892) | `evidence/releases/0.3.11/` |
| Stub Tesouro + `/gates` | 0.3.12 | `cd412dd` | [35409413760](https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35409413760) | `evidence/releases/0.3.12/` |
| Módulos Terraform | 0.3.13 | `2e5dd38` | [35409721281](https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35409721281) | `evidence/releases/0.3.13/` |

IBS/CBS local: `NON_BINDING`, `binding=false`, `operational=false`, `homologated=false`. `/gates` somente leitura; `canApprove=false`.

## Bloqueado até decisão humana

| Gate | Estado | Responsável | Decisão | Evidência |
|---|---|---|---|---|
| **G0** | BLOCKED | Patrocinador + controlador | Autorizar programa, município, DPA | Ato de abertura + DPA |
| **G1** | BLOCKED | Município piloto | Homologar diagnóstico sem meta de recuperação | Relatório G1 assinado |
| **G4** | BLOCKED | Especialista ISS + jurídico | Homologar regras e fórmulas | Memória de cálculo versionada |
| **G7 oficial** | OFFICIAL_BLOCKED | Controlador + órgão fonte | Autorizar conector Tesouro | Credencial + DPA |
| **G8 oficial** | OFFICIAL_BLOCKED | Jurídico + fonte oficial | Homologar norma IBS/CBS | Norma versionada + parecer |
| **G9** | BLOCKED | Patrocinador + usuários | Aceitar piloto | Aceites técnico/jurídico/LGPD |
| **G10** | BLOCKED | Autoridade de produção | Autorizar deploy | Plano de release + IAM |

## Proibições vigentes

- Dados reais em local, desenvolvimento ou testes
- `terraform apply`, GCP/AWS, serviços pagos
- Inferir obrigação legal, alíquota ou prazo
- Publicar ISR ou potencial regional em reais como indicador
- Marcar G8/G9/G10 como concluídos só porque o CI está verde
- Tratar fixture sintético como prova de crédito

## Próxima ação automática

Nenhuma. Ver `HUMAN_DECISIONS_REQUIRED.md`.
