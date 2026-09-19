# Gates humanos bloqueados

Este arquivo registra o que a implementação local **não** pode avançar sem autorização institucional. Não altera a especificação 0.3.0.

Data: 2026-09-18  
Implementação: 0.3.11 (`F3_SOURCE_INGEST_LOCAL`)  
CI G8: https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35367451209

## Concluído localmente (sintético)

| Fatia | Versão | Evidência | Observação |
|---|---|---|---|
| F0 / Sprints 0–1 | 0.3.1 | `evidence/releases/0.3.1/` | Isolamento, OIDC, Compose local |
| Sprint 2 validação | 0.3.2 | `evidence/releases/0.3.2/` | Nenhuma cobrança sem validação (domínio) |
| Sprint 3 cobrança | 0.3.3 | `evidence/releases/0.3.3/` | `StartAdministrativeCollection` |
| Sprint 4 funil ISS | 0.3.4 | `evidence/releases/0.3.4/` | Bronze/Silver/Gold sintético |
| G6 financeiro | 0.3.5 | current-state | Pagamento só após conciliação |
| G7 transferências | 0.3.6 | CI `35366037839` | Ocorrência nunca cria `TaxCredit` |
| G8 calendário IBS/CBS | 0.3.7 | `evidence/releases/0.3.7/` | Catálogo `NON_BINDING`, não operacional |
| Higiene Alembic | 0.3.8 | `evidence/releases/0.3.8/` | Schema separado do seed; caminhos `base/0004 -> head` |
| Catálogo de fontes | 0.3.9 | `evidence/releases/0.3.9/` | Registro mestre sintético; ISS restrito sem ingestão |
| Gates + Terraform docs | 0.3.10 | `evidence/releases/0.3.10/` | Snapshot LOCAL_GO/OFFICIAL_BLOCKED; sem apply |
| Ingestão IBGE sintética | 0.3.11 | `evidence/releases/0.3.11/` | Landing/Gold de enriquecimento; nunca cria crédito |

## Bloqueado até decisão humana

| Gate | Motivo | O que desbloqueia |
|---|---|---|
| **G0** programa municipal | Sem patrocinador, município piloto, DPA nem equipe nomeada | Autorização institucional explícita |
| **G1** diagnóstico | Depende de G0 e de dados/sistemas reais do município | Diagnóstico homologado pelo município |
| **G4** especialista ISS | Regras, fórmulas e potencial em R$ exigem homologação; hipóteses regionais não são KPI | Especialista municipal e jurídico |
| **G7 oficial** Tesouro | Conectores e fontes oficiais exigem credencial, nuvem e dado real | Autorização de ingestão + DPA |
| **G8 oficial** IBS/CBS | Datas, alíquotas e leiautes oficiais não foram homologados; o catálogo local é não vinculante | Fonte oficial versionada + homologação |
| **G9** piloto | Carteira real, treinamento e aceite integrado | Aceites técnico, administrativo, jurídico e LGPD |
| **G10** produção | Deploy, segredos, região e operação 24x7 | Autorização de produção |

## Proibições vigentes

- Dados reais em local, desenvolvimento ou testes.
- `terraform apply`, GCP/AWS, serviços pagos.
- Inferir obrigação legal, alíquota ou prazo a partir do modelo.
- Publicar ISR ou potencial regional em reais como indicador.
- Marcar G8/G9/G10 como concluídos só porque o CI local está verde.

## Próxima ação automática

Após CI verde de `0.3.11`, stub sintético Tesouro (sem conector oficial) e UI de checklists G0/G1 em estado BLOCKED. Gates da tabela acima continuam bloqueados.
