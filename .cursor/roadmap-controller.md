# Controlador de ciclo autônomo — ROADMAP SIRTA 2026

Você executa **exatamente um ciclo** de trabalho. Não encerre o programa porque uma fatia ficou verde. Não solicite validação humana. Não faça merge em `main`. Não execute `terraform apply`, deploy, carga nacional ilimitada nem force-push.

Branch obrigatória: `feat/official-public-ingest`. PR obrigatória: `#2`. Estado: `OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS` até o orquestrador gravar conclusão. Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.

## Leitura obrigatória (completa)

1. `AGENTS.md`
2. `docs/delivery/ROADMAP-SIRTA-2026.md`
3. `docs/delivery/HUMAN-GATES.md`
4. `current-state.yaml`
5. `MANIFEST.md`
6. `docs/autonomous/ROADMAP-WORK-QUEUE.yaml`
7. `docs/autonomous/AUTONOMOUS-EXECUTION.md`
8. evidências mais recentes em `evidence/`
9. `contracts/sources/official-catalog.yaml`
10. `contracts/sources/state-transfers-catalog.yaml`

## Procedimento do ciclo

1. Verificar Git: branch, HEAD, working tree, PR #2 (`gh pr view 2`). Sem nova PR.
2. Reconstruir e corrigir `ROADMAP-WORK-QUEUE.yaml` se estiver incompleta em relação ao roadmap.
3. Selecionar o maior lote seguro de itens relacionados em `PENDING`, `FAILED` ou `IN_PROGRESS`. Volume alto não é bloqueio: pagine, faça checkpoint e deixe o restante para o próximo ciclo.
4. Implementar código funcional (backend, frontend, pipeline, testes). Documentação sozinha não conta como progresso.
5. Dados: somente PUBLIC_OPEN em runtime. Snapshots oficiais minimizados só em testes. Sem sintético em Landing/Bronze/Silver/Gold/API/dashboard.
6. Sem dado oficial autorizado: capacidade técnica + estado vazio + `CREDENTIAL_REQUIRED` / `READY_FOR_TERRITORIAL_SCOPE` / evidência. Prosseguir itens independentes.
7. Toda linha Gold exige lineage até Silver, Bronze, manifesto Landing, checksum SHA-256 e URL oficial.
8. Fonte pública nunca cria crédito, cobrança, inscrição ou notificação.
9. Dashboards: cada rota precisa de backend real, Gold oficial quando aplicável, vazio/loading/erro, fonte, competência, fórmula, qualidade, lineage, homologação pendente, testes.
10. Executar testes aplicáveis. Corrigir falhas. Não enfraquecer testes.
11. Atualizar fila, roadmap, `current-state.yaml`, evidências.
12. Commit convencional (sem `git add .`) e `git push` normal. Atualizar PR #2, sem merge.
13. Verificar CI da PR #2 quando houver push. Se vermelha, o próximo ciclo corrige CI antes de nova funcionalidade.
14. Usar subagentes em paralelo para pesquisa de fontes, dados, backend, frontend, segurança, testes, lineage e docs. Você integra, evita conflitos, faz regressão, commit e push. Subagentes não fazem merge, deploy nem `terraform apply`.
15. `EXTERNAL_BLOCKED` só se: implementação técnica independente pronta; dependência externa comprovada; sem alternativa oficial lícita; APIs/telas vazias funcionais; testes do vazio; evidência registrada. “Volume”, “demora” ou “outra fatia” não são bloqueio.

## Resultado

Grave detalhes no repositório (`docs/autonomous/`, `evidence/`, fila). Não emita relatório longo no terminal.

`COMPLETE_CANDIDATE` somente se a fila não tiver nenhum item técnico em `PENDING`, `IN_PROGRESS` ou `FAILED`.

Última linha do stdout, exatamente uma destas:

CYCLE_RESULT=PROGRESSED

CYCLE_RESULT=NO_PROGRESS

CYCLE_RESULT=COMPLETE_CANDIDATE
