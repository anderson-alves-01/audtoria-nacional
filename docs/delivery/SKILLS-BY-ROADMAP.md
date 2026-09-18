# Skills por fase do roadmap SIRTA

| Fase | Skills específicas | Skills de engenharia | Gate |
|---|---|---|---|
| G0 Mobilização | product-architect | writing-plans, requesting-code-review, verification-before-completion | Programa autorizado |
| G1 Diagnóstico | product-architect, data-engineer | writing-plans, requesting-code-review, verification-before-completion | Diagnóstico homologado |
| G2 Fundação | devops-platform, backend-engineer, security-reviewer | TDD, review, verificação | Build e isolamento |
| G3 Dados | data-engineer | TDD de contrato, review, verificação | Idempotência e reconciliação |
| G4 ISS | sirta-domain, data-engineer | TDD, debugging, review, verificação | Fórmula e regras homologadas |
| G5 Casos/cobrança | sirta-domain, backend/frontend | TDD estrito, review, verificação | Nenhuma cobrança sem validação |
| G6 Dívida/parcelamentos | sirta-domain, security-reviewer | TDD estrito, review, verificação | Rastreabilidade financeira |
| G7 Transferências | transfer-reconciliation, data-engineer | TDD de contrato, review, verificação | Conciliação oficial |
| G8 IBS/CBS | ibs-cbs-readiness, product-architect | Plano, review, verificação | Norma oficial homologada |
| G9 Piloto | qa-release, security-reviewer | Review, debugging, verificação | Aceites integrados |
| G10 Implantação | devops-platform, qa-release | Plano de release, review, verificação | Produção autorizada |

## Compatibilidade com a nomenclatura anterior

| Fase | Obrigatórias | Gates principais |
|---|---|---|
| F0 Fundação | Plano, TDD, review, verificação | Build, testes, segredos, isolamento |
| F1 Dados | Plano, TDD de contrato, review, verificação | SQL, idempotência, quarentena, linhagem |
| F2 ISS/RJ | Plano, TDD, review quádruplo, verificação | Reconciliação, fórmula, homologação |
| F3 Casos | Plano, TDD estrito, review, verificação | Workflow, custódia, auditoria, funil |
| F4 DF | Plano, TDD, review, verificação | Regras, isolamento, filtros e contratos |
| F5 IA privada | Plano, TDD de segurança, review, verificação | RAG, citação, DLP e revisão humana |
| F6 Expansão | Plano, review, verificação; TDD conforme mudança | Templates, conectores, homologação |
| F7 Nacional | Plano, review, verificação; TDD conforme mudança | Metodologia, anonimização e governança |

`systematic-debugging` é ativada sempre que qualquer gate falhar. `receiving-code-review` é ativada sempre que houver retorno de revisão.

## Parâmetros centrais

- Até três hipóteses de correção antes de revisão arquitetural.
- Tarefas planejadas em fatias de 15-45 minutos.
- Trabalho local autônomo permitido.
- Dados reais, nuvem, produção e destruição bloqueados.
- Evidência obrigatória na revisão atual.
- Telemetria externa desabilitada.

O arquivo executável de política é `config/skills-policy.yaml`.
