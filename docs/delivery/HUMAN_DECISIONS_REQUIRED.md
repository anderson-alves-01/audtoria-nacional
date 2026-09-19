# Decisões humanas obrigatórias

Este arquivo não aprova nem desbloqueia gates. Lista responsável, decisão e evidência mínima para cada item BLOCKED após a conclusão técnica local `0.3.13`.

Spec `0.3.0`. Branch `feat/roadmap-technical-completion`. Flags oficiais permanecem `false`.

## Gates bloqueados

| Gate | Estado | Responsável | Decisão necessária | Evidência exigida |
|---|---|---|---|---|
| **G0** programa municipal | BLOCKED | Patrocinador institucional + controlador municipal | Autorizar município piloto, governança, DPA e equipe nomeada | Ato de abertura, matriz RACI, DPA assinado, política de segurança inicial |
| **G1** diagnóstico | BLOCKED | Município piloto (depende de G0) | Homologar diagnóstico de sistemas, dados e processos **sem** promessa de recuperação | Relatório G1 assinado, inventário de sistemas, avaliação LGPD, amostra controlada autorizada |
| **G4** especialista ISS | BLOCKED | Especialista tributário municipal + jurídico | Homologar regras, fórmulas e leiautes ISS reais | Memória de cálculo versionada, amostra mascarada, parecer jurídico |
| **G7 oficial** Tesouro | OFFICIAL_BLOCKED | Controlador + Tesouro/fonte estadual + segurança | Autorizar conector oficial (credencial, volume, finalidade) | DPA, credencial institucional, contrato de fonte, dry-run oficial registrado |
| **G8 oficial** IBS/CBS | OFFICIAL_BLOCKED | Jurídico municipal + fonte oficial versionada | Homologar datas, alíquotas e leiautes; só então `binding/operational/homologated` | Norma oficial versionada, parecer, testes de leiaute. Até lá: `NON_BINDING` |
| **G9** piloto | BLOCKED | Patrocinador + usuários do piloto (depende de G0/G1) | Aceitar carteira, treinamento e operação assistida | Aceites técnico, administrativo, jurídico e LGPD |
| **G10** produção | BLOCKED | Autoridade de produção + segurança | Autorizar deploy, região, segredos e operação 24x7 | Plano de release, rollback testado, IAM real, `terraform apply` autorizado por escrito |

## Proibições até a decisão

- Inferir GO a partir de CI verde ou desta documentação
- Tratar fixture IBGE/Tesouro como prova de dívida ou crédito
- Ligar `official_tesouro_connectors`, `official_ibs_cbs_rules`, `real_data_ingestion`, `cloud_apply` ou `production_deploy`
- Executar `terraform apply`
- Consultar SIDRA, Tesouro Transparente ou outra API oficial sem autorização
- Alterar `canApprove` ou marcar checklist `met=true` sem ato humano

## Ordem

G0 → G1 → (G4 e/ou G7 oficial conforme finalidade) → G8 oficial quando houver norma → G9 → G10.

## Retomada

Após ato explícito, abrir fatia na mesma branch ou em `feat/<gate>` a partir do HEAD desta linha. Dados reais exigem DPA. Relatório técnico: `TECHNICAL_COMPLETION_REPORT.md`.
