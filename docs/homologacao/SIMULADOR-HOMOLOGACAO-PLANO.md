# Plano de homologação do Simulador SIRTA

Versão: 1.0 (28/10/2026). Ramo: `feat/professional-ui-v1`. Estado de produção inalterado: web 0.4.23 e API 0.3.124.

Este plano descreve como o Simulador foi preparado para homologação. Preparar a homologação não autoriza publicar dados nem fazer deploy em produção, e nenhum indicador recebe CONFERIDO automaticamente.

## 1. Objetivo e escopo

O Simulador permite ao usuário informar manualmente uma hipótese (UF, município, imposto, operação, tipo de bem, quantidade e valor) e ver o imposto estimado. Ele não apura, não cobra e não cria crédito tributário.

Dentro do escopo:

- Interface do Simulador (`apps/web/src/app/simulador/`): seleção de UF, município, impostos, operação e tipo de bem; quantidade e valor; cálculo; gráfico; rótulos de hipótese; comparação com dados públicos (bloqueada).
- Rotas de apoio na API: `GET /v1/sped-operacoes`, `GET /v1/tax-rates`, `GET /v1/indicator-reliability/{id}/fiscal-use`.
- Portão de confiabilidade (NAO_CONFIAVEL, EXPLORATORIO, CONFERIDO) no web e na API.
- Cadastro de alíquotas (`tax_rate_versions`, migrações 0109 a 0111).
- Dados do SPED usados como base pública (46.825 registros, 1.041 omissões) e a classificação de CFOP.
- Lista de municípios do IBGE (referência territorial).

Fora do escopo desta fase:

- Deploy, push, merge e alteração do estado de carga em produção.
- Ingestão de dados reais, carga das transferências recebidas e qualquer carga nova.
- Promoção de indicador a CONFERIDO e homologação de alíquota, que são decisões humanas.
- Criação de crédito tributário.

## 2. Ambientes

| Ambiente | Uso nesta homologação | Observação |
| --- | --- | --- |
| Local (Windows) | Testes automatizados, migrações e scripts | Banco PostgreSQL sintético em `localhost:55432`. Sem dado real. |
| Chrome Headless 156 | Testes de interface (Karma) | Sem leitor de tela e sem dispositivo físico. |
| Produção | Não utilizado | Web 0.4.23 (`sirta-prod-web:31`) e API 0.3.124 (`sirta-prod-api:30`) sem alteração. |

Os ambientes são segregados: nenhuma credencial de outro ambiente é lida ou reutilizada, e os arquivos `.env` ficam fora do controle de versão (verificado por teste, CT-038).

## 3. Responsáveis

Os campos abaixo são preenchidos pela instituição. Nenhum nome foi inventado.

| Papel | Nome | Matrícula ou cargo | Data |
| --- | --- | --- | --- |
| Responsável pela homologação funcional | ________________ | ________________ | ____/____/______ |
| Revisor jurídico das alíquotas | ________________ | ________________ | ____/____/______ |
| Responsável pela conferência dos dados (SPED) | ________________ | ________________ | ____/____/______ |
| Responsável de segurança e privacidade | ________________ | ________________ | ____/____/______ |
| Autoridade que autoriza a publicação | ________________ | ________________ | ____/____/______ |

## 4. Critérios de entrada

1. Código no ramo `feat/professional-ui-v1`, sem alteração não commitada nos arquivos do escopo.
2. Banco local sintético no head `0111_tax_rate_review_fields`.
3. Originais do SPED com hash conferido (`tools/ops/sped-source-verify.py`).
4. Registro de confiabilidade (`config/indicator-reliability.yaml`) válido.

## 5. Critérios de saída

Homologação funcional condicionada (alcançável nesta fase):

- Todos os casos de teste executáveis sem pessoa externa executados e aprovados.
- Nenhum defeito comprovado em aberto dentro do escopo.
- O Simulador não apresenta valor como imposto apurado ou devido.
- Nenhum caminho de publicação ou promoção automática.

Homologação definitiva (depende de decisões humanas, ver bloqueios):

- Indicadores do SPED conferidos e promovidos a CONFERIDO por responsável identificado, com data e evidência.
- Alíquotas revisadas e homologadas por revisor identificado.
- Teste de aceite com usuários e testes de acessibilidade com leitor de tela.
- Autorização expressa para publicar.

## 6. Estratégia de testes

| Camada | Instrumento | Local |
| --- | --- | --- |
| Lógica e interface do web | Karma e Jasmine | `apps/web/src/app/**/*.spec.ts` |
| Domínio e aplicação da API | pytest | `tests/unit/` |
| API, banco, acesso e auditoria | pytest com PostgreSQL sintético | `tests/integration/` |
| Dados do SPED | Scripts somente leitura | `tools/ops/sped-*.py` |
| Alíquotas | Script de auditoria e migração | `tools/ops/tax-rates-audit.py`, `alembic/versions/0111_*.py` |

Cada defeito corrigido nesta fase foi reproduzido antes por um teste que falhava, e depois corrigido em commit pequeno.

## 7. Bloqueios conhecidos

| ID | Bloqueio | Quem resolve |
| --- | --- | --- |
| B-01 | Nenhum indicador do SPED está CONFERIDO. A definição de `Quantidade NF-e` não existe nas fontes e a planilha não traz as entradas por transferência. | Responsável pela conferência dos dados |
| B-02 | Nenhuma alíquota está homologada (31 versões). Falta revisor, revisão registrada e, para 29 versões, fundamento legal. | Revisor jurídico |
| B-03 | CFOPs 1.159, 2.159, 1.190, 2.170, 1.155 a 1.158, 5.154 e 5.157 continuam pendentes por falta de definição oficial. | Responsável pela conferência dos dados |
| B-04 | Carga das transferências recebidas (apenas nas planilhas `.ods`) exige autorização. | Autoridade que autoriza |
| B-05 | Não há alíquota municipal cadastrada. ITBI e ISS usam parâmetro de simulação. | Revisor jurídico |
| B-06 | Publicar a API aplica as migrações 0109, 0110 e 0111 na inicialização. | Autoridade que autoriza |
| B-07 | O requisito de "valor total" não define preço unitário e quantidade. O valor informado é tratado como total. | Responsável funcional |

## 8. Riscos

| Risco | Mitigação |
| --- | --- |
| Usuário tomar a estimativa por imposto devido | Rótulo "estimado" e aviso "não é imposto apurado nem devido" testados (CT-014) |
| Uso de número não conferido como fiscal | Portão fechado por padrão no web e na API (CT-020 a CT-029) |
| Alíquota sem lei ser tratada como oficial | Alíquota PENDENTE rotulada; cadastro sem homologação (CT-050 a CT-053) |
| Erro de ponto flutuante no imposto | Aritmética em centavos testada (CT-007) |
| Soma de transferências recebidas e remetidas | Recusa testada (CT-011, CT-040) |

## 9. Reversão

- Web e API: nenhuma alteração foi publicada. Reverter é descartar os commits locais.
- Migração 0111: aditiva. Reversão por `alembic downgrade 0110_direction_rate_scope`, testada em upgrade, downgrade e upgrade no banco local (CT-056).
- Lista de municípios: arquivo estático versionado. Remover o arquivo e o seletor volta ao comportamento por UF.

## 10. Documentos do pacote

1. `SIMULADOR-HOMOLOGACAO-PLANO.md` (este).
2. `SIMULADOR-CASOS-DE-TESTE.md`.
3. `SIMULADOR-MATRIZ-REQUISITOS.md`.
4. `SIMULADOR-HOMOLOGACAO-DADOS.md`.
5. `SIMULADOR-HOMOLOGACAO-JURIDICA.md`.
6. `SIMULADOR-RELATORIO-FINAL.md`.
7. `SIMULADOR-ATA-HOMOLOGACAO.md` (modelo em branco).

Evidência de comandos: `evidence/ops/simulador-homologacao-20261028.txt`.
