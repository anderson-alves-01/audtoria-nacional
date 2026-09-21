# ROADMAP ESTRATÉGICO E TECNOLÓGICO 2026

## Plataforma Auditoria Nacional - SIRTA Municipal

**SIRTA - Sistema Integrado de Recuperação Tributária e Auditoria**  
**Lema:** “Auditar. Acompanhar. Recuperar.”  
**Versão do roadmap:** 1.2  
**Data-base:** setembro de 2026  
**Revisão 1.2:** reconciliação do estado executável 0.3.7, gates locais/oficiais e dívida Alembic  
**Revisão 1.1:** plano explícito de fontes públicas e ingestão do datalake  
**Horizonte:** implantação inicial de 6 a 8 meses e evolução contínua

---

## Estado de execução em 21 de setembro de 2026

| Item | Estado registrado |
|---|---|
| Versão da especificação | `0.3.0` |
| Versão da implementação local | `0.3.70` |
| Linha técnica em progresso | F0/S0-S4, G6–G8 locais, Alembic, F3, onda 1 PUBLIC_OPEN, lineage Gold, 15 dashboards, FPM/ITR/IPI-EXP/Royalties/LC176/IOF-Ouro/FUNDEB-COMPLEMENT/FUNDEB-COINT/LC87-COINT/FPM-COINT/ITR-COINT/IOF-COINT/LC176-COINT/CIDE-COINT/FEX-COINT/RREO/DCA/RGF, observabilidade, LC 214, Portal stub, diagnóstico, regras não vinculantes, calendário catalog-official-docs-v1, shells F5–F10, upload municipal, Cadastro 360, setoriais (ANP+ANEEL+EPE+BCB SGS+BCB OLINDA Expectativas IPCA/Selic/Câmbio/PIB Total/PIB Serviços/PIB Agropecuária/PIB Indústria/IGP-M/IGP-DI/INPC+Anatel+CNES ativados), backfill controlado FPM/RREO/DCA, RFB territorial sem carga nacional, PE+BA+MG+ES+MS+RO+AC+CE+RS+AL+RN+MA+PR ICMS (+IPVA onde publicado) + GO ICMS/IPVA/IPI + ES IPI/CIDE/FRD/Compensação + CE/AL/RN/PE/BA/MG IPI + MA/PR FPEX/IPI-Exportação + MS IPI-Exportação/CIDE + AL/PR royalties + PI IPVA + AC IPVA/ICMS/FUNDEB Transparência + RS Compensação LC194 + PA ICMS Verde + IBGE SIDRA 9509 CEMP TECHNICALLY_APPROVED |
| Dívida Alembic `0004 -> 0005` | `RESOLVED` (`ALEMBIC_HYGIENE`) |
| Próximo passo automático | Preferir UF restante com CSV/API tabular recente; PA cota plena ainda DOE PDF; TO IPM/PDF; AP link SEFAZ 404; RR painel sem split ICMS/IPVA; MT XLSX ≤2015 / corrente PDF; SE/PB PROVENANCE_VERIFIED (PDF); AM HTML-per-município; SP HTML-only; SC PROVENANCE_ONLY ≤2017; PI ICMS quando Repasse WEB publicar linhas; RJ IP-blocked. BCB OLINDA Expectativas IPCA+Selic+Câmbio+PIB Total+PIB Serviços+PIB Agropecuária+PIB Indústria+IGP-M+IGP-DI+INPC ativado. Tesouro COINT municipal completo. RFB sem carga nacional. Sem homologação humana agora. Gates G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 permanecem BLOCKED. |
| Commit de referência local | `feat/official-public-ingest` |
| Nuvem, produção e dados fiscais restritos | Não autorizados |
| Estado composto | `OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS` |

A implementação `0.3.70` expande BCB OLINDA Expectativas Focus
(IPCA+Selic+Câmbio+PIB Total+PIB Serviços+PIB Agropecuária+PIB Indústria+IGP-M+IGP-DI+INPC) além do SGS 432/433;
mantém o pacote COINT municipal do Tesouro completo e as ativações estaduais/setoriais
anteriores. Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
O Programa SIRTA 2026 **não** está concluído. Pacote: `docs/delivery/HUMAN_VALIDATION_PACKAGE.md`.

### Estados compostos dos gates

| Gate | Componente técnico/local | Componente institucional/oficial | Estado consolidado |
|---|---|---|---|
| F0/S0-S4 | Implementado e testado localmente | Não depende de homologação tributária | `LOCAL_GO` |
| G0 - programa municipal | Não substitui decisão administrativa | Município piloto, patrocinador e governança ausentes | `BLOCKED` |
| G1 - diagnóstico | Estrutura técnica disponível | Diagnóstico municipal não realizado/homologado | `BLOCKED` |
| G4 - ISS | Componentes genéricos disponíveis | Regras e amostras não homologadas por especialista | `BLOCKED` |
| G6 - financeiro | Fluxo financeiro local verde | Uso oficial depende dos gates anteriores | `LOCAL_GO/OFFICIAL_BLOCKED` |
| G7 - transferências | Ocorrências locais não criam crédito | Conectores e reconciliação com Tesouro/fontes estaduais não homologados | `LOCAL_GO/OFFICIAL_BLOCKED` |
| G8 - IBS/CBS | Calendário sintético, não vinculante e não operacional | Fontes, regras e datas não homologadas oficialmente | `LOCAL_GO/OFFICIAL_BLOCKED` |
| G9 - piloto | Não iniciado | Município e usuários do piloto ausentes | `BLOCKED` |
| G10 - produção | Não iniciado | Segurança, operação e aceite institucional ausentes | `BLOCKED` |

Os estados `LOCAL_GO` não autorizam carga real, decisão administrativa, cálculo vinculante, cobrança, publicação oficial ou promoção a produção.

### Evidência do G8 local

- `GET /v1/regulatory/ibs-cbs` expõe catálogo versionado com `binding=false`, `operational=false` e `homologated=false`;
- itens permanecem em `NON_BINDING`;
- simulações, leiautes e mapas de impacto não se tornam regras operacionais;
- a interface `/calendario` informa explicitamente a natureza não vinculante;
- execução informada: 75 testes Python, 12 testes Angular e CI verde nos jobs `python`, `web` e `containers`;
- execução de referência: https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35367451209.

O registro dos gates humanos está associado ao commit `86022ad` e à execução https://github.com/anderson-alves-01/audtoria-nacional/actions/runs/35367701439.

### Dívida técnica Alembic

A falha `0004 -> 0005` (`users_tenant_id_fkey` após `drop_all` com `alembic_version` preservado) foi reproduzida em `sirta_migtest` e corrigida na implementação `0.3.8`:

1. migrations de schema separadas do seed sintético;
2. `seed_synthetic` idempotente (`python -m sirta_api.adapters.db.seed`);
3. pytest não executa `drop_all` no banco compartilhado;
4. comprovados `base -> head`, `0004 -> head` válido e `0004 -> head` após drop de domínio;
5. evidência em `evidence/releases/0.3.8/`.

Estado da ocorrência: `RESOLVED`. O G8 local permanece `LOCAL_GO`; a homologação oficial permanece `OFFICIAL_BLOCKED`.

---

## 1. Decisão de produto

A **Auditoria Nacional** será a plataforma tecnológica e de governança comum. O **SIRTA** será sua solução municipal, configurável para municípios pequenos, médios e grandes.

```text
Plataforma Auditoria Nacional
├── SIRTA Municipal
│   ├── Receitas próprias
│   ├── Auditoria e validação
│   ├── Cobrança administrativa
│   ├── Dívida ativa
│   ├── Parcelamentos e pagamentos
│   ├── Transferências intergovernamentais
│   ├── Preparação IBS/CBS
│   └── Gestão, transparência e IA privada
├── Inteligência estadual e distrital
├── Solução para tribunais de contas
└── Inteligência nacional agregada
```

O SIRTA será oferecido como serviço de implantação rápida, reduzindo a necessidade de cada pequeno município manter equipe técnica, infraestrutura analítica e especialistas próprios.

---

## 2. Objetivo estratégico

Implantar uma capacidade municipal permanente para:

1. conhecer a carteira de créditos;
2. consolidar dados dispersos;
3. verificar a qualidade e a legalidade dos créditos;
4. priorizar ações administrativas;
5. acompanhar cobrança, parcelamento e pagamento;
6. melhorar a gestão da dívida ativa;
7. conciliar transferências constitucionais e legais;
8. preparar o município para a transição ao IBS/CBS;
9. medir recuperação efetiva, custo e retorno;
10. produzir transparência agregada sem exposição indevida.

---

## 3. Princípios obrigatórios

### 3.1 Nenhuma cobrança sem validação

O sistema bloqueará o avanço para cobrança enquanto não houver origem, competência, contribuinte, valor, memória de cálculo, exigibilidade, evidências e validação por servidor competente.

### 3.2 Tecnologia como apoio

O SIRTA não cria tributo, crédito ou obrigação; não substitui processo administrativo, contraditório, ampla defesa, Procuradoria ou autoridade competente.

### 3.3 Separação financeira

Nunca somar como se fossem equivalentes:

- potencial econômico;
- indício;
- valor em conferência;
- crédito validado;
- valor elegível;
- crédito constituído;
- dívida ativa;
- valor em cobrança;
- valor parcelado;
- valor efetivamente recuperado.

### 3.4 Evidência sobre afirmação

Indicadores devem informar fonte, competência, atualização, fórmula, exclusões, versão metodológica e nível de confiança.

### 3.5 Segurança por padrão

Acesso condicionado a usuário, órgão, território, finalidade, classificação e vigência. Dados reais são proibidos em desenvolvimento e testes.

### 3.6 Fonte pública não constitui crédito

Dados públicos oficiais podem apoiar diagnóstico, contextualização econômica, enriquecimento cadastral, comparação, cálculo de indicadores e conciliação de transferências. Eles não criam, constituem, validam ou tornam exigível um crédito tributário por si mesmos.

Todo conjunto de dados deverá ser classificado no catálogo segundo seu papel:

- `PRIMARY_FISCAL`: registro fiscal mantido pela autoridade competente;
- `OFFICIAL_TRANSFER`: repasse, coeficiente ou demonstrativo publicado por órgão oficial;
- `REFERENCE_ENRICHMENT`: informação pública usada somente para contexto ou cruzamento;
- `REGULATORY`: norma, leiaute, calendário ou orientação institucional.

Somente registros `PRIMARY_FISCAL`, submetidos às validações administrativa e jurídica aplicáveis, poderão integrar a memória de um crédito. Diferenças encontradas em fontes públicas gerarão indícios ou ocorrências para análise, nunca cobrança automática.

---

## 4. Escopo de receitas

### 4.1 Receitas próprias municipais

- ISS/ISSQN;
- IPTU;
- ITBI;
- taxas municipais;
- contribuições municipais aplicáveis;
- IRRF e demais receitas cuja titularidade ou tratamento municipal seja confirmado;
- multas, juros e acréscimos legalmente aplicáveis;
- créditos inscritos e não inscritos em dívida ativa.

### 4.2 Transferências intergovernamentais

Módulo separado para monitoramento e conciliação de:

- FPM;
- quota-parte municipal do ICMS;
- quota-parte municipal do IPVA;
- ITR;
- IPI-Exportação;
- CIDE-Combustíveis;
- FUNDEB;
- royalties e compensações;
- outras transferências constitucionais ou legais configuradas.

O módulo não classificará automaticamente diferenças como “dívida tributária”. Ele comparará previsão, base, coeficiente, repasse recebido, retenções, bloqueios, ajustes e fonte oficial, gerando ocorrência para análise administrativa.

### 4.3 Transição IBS/CBS

O SIRTA manterá calendário regulatório parametrizado, catálogo de leiautes, integrações e impactos sobre receitas municipais. Não serão codificadas regras temporais diretamente no código quando puderem ser configuradas e versionadas.

---

## 5. Domínios funcionais

### D1 - Organização, identidade e governança

Municípios, órgãos, unidades, territórios, usuários, perfis, segregação de funções, delegações temporárias, finalidade de acesso, aprovações e auditoria.

### D2 - Catálogo e acesso a dados

Fontes públicas e restritas, responsável, base legal, finalidade, autorização, vigência, classificação, layout, retenção e linhagem.

### D3 - Plataforma de dados

Landing, Bronze, Silver, Gold, qualidade, quarentena, idempotência, reconciliação, histórico e rollback lógico.

Nenhuma fonte poderá alimentar diretamente Silver, Gold, regra de auditoria ou indicador. Toda ingestão começará pelo catálogo, passará por Landing/Bronze imutável e conservará origem, versão, competência, checksum, finalidade e linhagem.

### D4 - Cadastro 360

Contribuinte, estabelecimentos, atividades, imóveis, vínculos, débitos, declarações, pagamentos, parcelamentos, notificações e processos.

### D5 - Auditoria tributária

Regras versionadas, cruzamentos, duplicidades, inconsistências, triagem, evidências, parecer, revisão e validação humana.

### D6 - Cobrança administrativa

Carteiras, notificações, canais, prazos configuráveis, respostas, pendências, regularização e histórico.

### D7 - Parcelamentos e pagamentos

Adesão, parcelas, vencimentos, conciliação, atraso, rompimento, renegociação, saldo e baixa.

### D8 - Dívida ativa e jurídico

Checklist de legalidade, elegibilidade, inscrição, certidão, suspensão, baixa, encaminhamento, retorno da Procuradoria e judicialização.

### D9 - Transferências intergovernamentais

Previsão, realizado, coeficientes, base de cálculo, retenções, bloqueios, diferenças, alertas e processo de esclarecimento/contestação.

### D10 - Reforma tributária

Cadastro de normas, calendário IBS/CBS, leiautes, riscos, impactos, capacitação, simulações e prontidão municipal.

### D11 - Gestão e transparência

Painéis executivo, operacional, de dados, segurança e painel público agregado.

### D12 - IA privada

Pesquisa autorizada, organização de evidências, resumo, minutas e explicações com citação. Nenhuma decisão ou cobrança autônoma.

---

## 6. Modelo de estado do crédito

Não utilizar uma única classificação A-G no banco. Separar dimensões:

| Dimensão | Estados principais |
|---|---|
| Validação | identificado, em conferência, validado, rejeitado, cancelado |
| Exigibilidade | exigível, suspenso, extinto, impedido, análise jurídica |
| Cobrança | não iniciada, administrativa, dívida ativa, Procuradoria, judicial, encerrada |
| Pagamento | aberto, parcial, pago, compensado, parcelado regular, parcelado rompido |
| Prioridade | crítica, alta, acompanhamento, regularizada |

Cada transição registra usuário, autoridade, data, estado anterior, estado novo, justificativa, evidência, valor e versão da regra.

---

## 7. Indicadores

### 7.1 Financeiros

- créditos identificados;
- créditos auditados;
- créditos validados;
- valor elegível;
- valores em cobrança;
- dívida ativa;
- parcelamentos ativos;
- recuperação mensal e acumulada;
- custo de recuperação;
- ROI;
- evolução da carteira.

### 7.2 Operacionais

- tempo da identificação à validação;
- tempo da validação à providência;
- casos por responsável e SLA;
- taxa de inconsistência;
- taxa de regularização;
- parcelamentos adimplentes e rompidos;
- créditos próximos de prazos configurados;
- produtividade sem incentivo a cobranças indevidas.

### 7.3 Transferências

- previsto versus realizado;
- variação mensal e anual;
- diferenças por modalidade;
- retenções e bloqueios;
- ocorrências abertas e conciliadas;
- impacto sobre receita corrente.

### 7.4 Prontidão IBS/CBS

- integrações adaptadas;
- leiautes homologados;
- cadastros compatíveis;
- servidores capacitados;
- testes concluídos;
- riscos pendentes;
- conciliação durante a transição.

### 7.5 Índice SIRTA de Recuperação

`ISR = valor efetivamente recuperado / valor elegível para recuperação x 100`

O denominador exclui, conforme política versionada e homologada, créditos suspensos, extintos, cancelados, duplicados, indevidos, impedidos, não validados ou fora do período.

---

## 8. Roadmap de implantação - 6 a 8 meses

> **Nota de nomenclatura:** `F0_FOUNDATION` foi fechado inicialmente na implementação 0.3.1 e a linha local evoluiu até 0.3.7. Esse estágio técnico não equivale ao Gate G0 do programa municipal. O Gate G0 continua dependente de patrocinador, município piloto e governança formal.

## Fase 0 - Mobilização e governança

**Prazo:** semanas 1-2  
**Objetivo:** autorizar e organizar o programa.

Entregas:

- termo de abertura;
- comitê gestor;
- matriz de responsabilidades;
- definição do município piloto;
- política de segurança inicial;
- inventário de responsáveis pelos dados;
- plano de comunicação;
- critérios de sucesso;
- gates jurídicos, técnicos e administrativos.

Gate G0: patrocinador, responsáveis e escopo do diagnóstico formalmente definidos.

## Fase 1 - Diagnóstico municipal acelerado

**Prazo:** semanas 2-6  
**Objetivo:** conhecer sistemas, dados, carteira e processos.

Entregas:

- inventário de tributos e transferências;
- mapa dos sistemas existentes;
- catálogo inicial de bases;
- amostra controlada dos dados;
- avaliação de qualidade;
- mapa atual de cobrança e dívida ativa;
- levantamento de integrações;
- diagnóstico de segurança e LGPD;
- baseline dos indicadores;
- seleção da carteira piloto.

Gate G1: diagnóstico homologado sem promessa prévia de percentual de recuperação.

## Fase 2 - Fundação tecnológica e segurança

**Prazo:** semanas 3-8  
**Objetivo:** disponibilizar núcleo seguro e reutilizável.

Entregas:

- monorepositório e CI/CD;
- ambientes local, desenvolvimento e qualidade;
- identidade, MFA e perfis;
- tenant municipal e territórios;
- auditoria imutável;
- observabilidade;
- gestão de segredos;
- infraestrutura como código;
- dados sintéticos;
- testes de isolamento.

Gate G2: build reproduzível, scans aprovados e isolamento municipal comprovado.

## Fase 3 - Plataforma de dados

**Prazo:** semanas 6-12  
**Objetivo:** receber e publicar dados confiáveis.

### F3.0 - Inventário, classificação e autorização das fontes

Antes de desenvolver conectores, criar o Registro Mestre de Fontes. Cada fonte deverá possuir:

- identificador, nome, órgão mantenedor e URL ou URI oficial;
- papel da fonte (`PRIMARY_FISCAL`, `OFFICIAL_TRANSFER`, `REFERENCE_ENRICHMENT` ou `REGULATORY`);
- classificação de acesso (`PUBLIC_OPEN`, `PUBLIC_CONTROLLED`, `RESTRICTED` ou `CONFIDENTIAL`);
- finalidade, base legal, responsável institucional e aprovador;
- licença ou termos de uso, formato, leiaute, versão e dicionário de dados;
- abrangência territorial, granularidade, competência e periodicidade;
- método de obtenção, autenticação, limites de uso e contato do mantenedor;
- dados pessoais existentes, retenção, minimização e regras de publicação;
- camada de destino, contrato de qualidade, reconciliação e política de descarte;
- datas de homologação, última consulta, próxima revisão e eventual descontinuação.

Estados permitidos: `DISCOVERED`, `UNDER_REVIEW`, `APPROVED`, `ACTIVE`, `SUSPENDED` e `RETIRED`. Somente fontes `APPROVED` ou `ACTIVE` poderão ser ingeridas fora de fixtures sintéticas.

### F3.1 - Framework de ingestão reproduzível

Implementar primeiro com fixtures sintéticas:

- conectores por API, arquivo, upload controlado e banco autorizado;
- manifesto, checksum e preservação do conteúdo bruto;
- paginação, limites, retentativas e retomada;
- idempotência por tenant, fonte, competência, checksum e versão do leiaute;
- detecção de mudança de esquema;
- quarentena e aprovação para publicação;
- métricas, logs sem dados sensíveis, linhagem e rollback lógico.

APIs e arquivos oficiais são preferidos. Coleta automatizada de páginas somente será admitida quando não houver canal estruturado, os termos permitirem, houver aprovação registrada e o conector preservar evidência da origem e da data de consulta.

### F3.2 - Primeira onda de fontes públicas

Após autorização da fase, implementar e homologar nesta ordem:

1. IBGE/SIDRA para PIB de serviços, população e indicadores econômicos territoriais;
2. Tesouro Nacional/SICONFI/FINBRA para demonstrativos fiscais e finanças municipais;
3. Tesouro Transparente e Portal da Transparência para transferências federais;
4. Receita Federal para dados abertos de CNPJ, estabelecimentos e CNAE, com minimização e controles de privacidade;
5. portais oficiais estaduais para quota-parte de ICMS/IPVA e demais repasses disponíveis;
6. Planalto, Receita Federal, CGIBS e legislação oficial local para catálogo regulatório versionado;
7. fontes setoriais oficiais, quando necessárias ao caso de uso: ANP, ANEEL/EPE, Anatel, Banco Central e CNES/DATASUS.

O conector de uma fonte poderá ser catalogado em v0.5 e ativado somente na release funcional correspondente. Fontes de transferências serão catalogadas na Fase 3, mas sua conciliação operacional continuará pertencendo à Fase 7/v0.9.

### F3.3 - Fontes municipais e restritas

Arrecadação, cadastro mobiliário, dívida ativa, pagamentos, parcelamentos, notas fiscais e processos administrativos exigirão Gate G0, diagnóstico G1, autorização do controlador, finalidade registrada, canal seguro e homologação de amostra. Nenhum dado fiscal real será usado em desenvolvimento ou teste automatizado.

### F3.4 - Matriz inicial do datalake

| Grupo | Fontes oficiais iniciais | Uso permitido | Papel | Camada inicial | Release-alvo |
|---|---|---|---|---|---|
| Catálogo nacional | Catálogo Nacional de Dados e dados.gov.br | Descoberta e metadados | `REFERENCE_ENRICHMENT` | Catálogo | v0.5 |
| Indicadores territoriais | IBGE/SIDRA | PIB de serviços, população e contexto econômico | `REFERENCE_ENRICHMENT` | Landing/Bronze | v0.5 |
| Finanças municipais | Tesouro Nacional, SICONFI e FINBRA | Demonstrativos, comparação e reconciliação agregada | `REFERENCE_ENRICHMENT` | Landing/Bronze | v0.5 |
| Transferências federais | Tesouro Transparente e Portal da Transparência | Previsto versus transferido e ocorrências | `OFFICIAL_TRANSFER` | Landing/Bronze | catálogo v0.5; uso v0.9 |
| Transferências estaduais | Fazendas, tesouros e portais estaduais oficiais | Quotas-partes de ICMS/IPVA e outros repasses | `OFFICIAL_TRANSFER` | Landing/Bronze | catálogo v0.5; uso v0.9 |
| Estabelecimentos | Receita Federal - dados abertos de CNPJ/CNAE | Enriquecimento e conferência cadastral | `REFERENCE_ENRICHMENT` | Landing/Bronze | v0.6 |
| Regulação | Planalto, Receita Federal, CGIBS e legislação oficial local | Normas, vigência, leiautes e calendário | `REGULATORY` | Repositório documental/catálogo | v0.5-v0.9 |
| Setores econômicos | ANP, ANEEL/EPE, Anatel, Banco Central e CNES/DATASUS | Referência para combustíveis, energia, telecom, bancos e saúde | `REFERENCE_ENRICHMENT` | Landing/Bronze | por caso de uso, a partir de v0.6 |
| Fiscal municipal | Sistemas de ISS, dívida ativa, cadastro e pagamentos | Constituição, validação e acompanhamento do crédito | `PRIMARY_FISCAL` | Landing/Bronze restrita | após G0/G1 e autorização |

Esta matriz é um plano inicial, não uma autorização de acesso. Durante F3.0, cada entrada será desdobrada em datasets específicos e submetida a validação técnica, jurídica, de privacidade e de titularidade.

Entregas:

- registro mestre, catálogo e solicitações de acesso;
- inventário versionado de datasets públicos, controlados e restritos;
- manifesto de carga;
- conectores de arquivos e bancos;
- Bronze/Silver/Gold;
- qualidade e quarentena;
- idempotência e retomada;
- reconciliação;
- lineage;
- rollback lógico;
- monitoramento de jobs.

Gate G3: 100% das fontes ativadas registradas e aprovadas; reexecução sem duplicidade; conteúdo bruto preservado com checksum; mudança de esquema detectada; lote inválido não publicado; dados pessoais minimizados; totais reconciliados; linhagem demonstrável da fonte ao indicador; e nenhuma fonte pública usada isoladamente para constituir crédito ou iniciar cobrança.

## Fase 4 - MVP de auditoria e potencial do ISS

**Prazo:** semanas 10-16  
**Objetivo:** entregar o primeiro valor mensurável.

Escopo:

- arrecadação histórica;
- cadastro mobiliário;
- dívida ativa selecionada;
- atividades econômicas;
- indicadores econômicos oficiais;
- arrecadação versus potencial;
- cinco regras iniciais;
- triagem e validação;
- painel executivo;
- metodologia e memória de cálculo.

Gate G4: série reconciliada, fórmulas explicáveis e regras homologadas por especialista municipal.

## Fase 5 - Gestão de casos e cobrança administrativa

**Prazo:** semanas 14-20  
**Objetivo:** transformar achados validados em atuação controlada.

Entregas:

- finding, caso e evidências;
- designação e SLA;
- parecer e revisão;
- gate “nenhuma cobrança sem validação”;
- carteiras de cobrança;
- notificações registradas;
- acompanhamento de providências;
- resposta e regularização;
- trilha completa.

Gate G5: nenhum caso avança sem validação e competência do usuário comprovadas.

## Fase 6 - Parcelamento, pagamentos e dívida ativa

**Prazo:** semanas 18-24  
**Objetivo:** acompanhar o ciclo financeiro e jurídico.

Entregas:

- integração de pagamentos;
- parcelamentos e conciliação;
- inadimplência e rompimento;
- checklist de inscrição;
- integração com dívida ativa;
- encaminhamento à Procuradoria;
- baixa, suspensão e encerramento;
- funil financeiro completo.

Gate G6: rastreabilidade do crédito identificado ao valor efetivamente recebido.

## Fase 7 - Transferências intergovernamentais

**Prazo:** semanas 20-26  
**Objetivo:** monitorar receitas transferidas sem confundi-las com dívida tributária.

Entregas:

- conectores do Tesouro Nacional e fontes estaduais;
- FPM e demais transferências federais prioritárias;
- quota-parte de ICMS e IPVA conforme disponibilidade estadual;
- previsto versus recebido;
- coeficientes, retenções e bloqueios;
- ocorrência de divergência;
- processo de conciliação;
- painel de transferências.

Gate G7: diferenças reconciliadas com fontes oficiais e classificadas como ocorrência, não como crédito automaticamente exigível.

## Fase 8 - Prontidão para IBS/CBS

**Prazo:** semanas 22-28  
**Objetivo:** preparar tecnologia, dados e pessoas para a transição.

Entregas:

- monitor regulatório;
- calendário versionado;
- catálogo de leiautes;
- mapa de impacto sobre ISS e receitas municipais;
- prontidão cadastral;
- simulações não vinculantes;
- testes de integração;
- plano de capacitação;
- painel de riscos da transição.

Gate G8: regras e datas confirmadas em fontes oficiais e homologadas antes de uso operacional.

## Fase 9 - Projeto-piloto e operação assistida

**Prazo:** semanas 25-30  
**Objetivo:** validar a solução em carteira real autorizada.

Entregas:

- piloto controlado;
- treinamento por perfil;
- atendimento e suporte;
- medição do tempo e da qualidade;
- correção de regras;
- homologação dos painéis;
- teste de continuidade e restauração;
- relatório de resultados.

Gate G9: aceite técnico, administrativo, jurídico, segurança e proteção de dados.

## Fase 10 - Implantação municipal

**Prazo:** semanas 29-34  
**Objetivo:** ampliar para tributos, carteiras e setores aprovados.

Entregas:

- produção;
- operação monitorada;
- expansão gradual das carteiras;
- painel público agregado;
- metas baseadas no diagnóstico;
- governança mensal;
- suporte e manutenção;
- plano de evolução.

Gate G10: produção autorizada, rollback testado e responsabilidades operacionais formalizadas.

---

## 9. Ondas posteriores

### Onda A - Município piloto do Rio de Janeiro

ISS e carteira selecionada, aproveitando referências de Maricá, São João de Meriti, Teresópolis e Santa Maria Madalena. Valores demonstrativos existentes permanecem como hipóteses até validação das fontes e fórmulas.

### Onda B - Outros tributos municipais

IPTU, ITBI, taxas, demais receitas e dívida ativa, conforme qualidade e autorização.

### Onda C - Municípios do mesmo estado

Template de implantação, conectores reutilizáveis, regras configuráveis e benchmark apenas entre municípios comparáveis.

### Onda D - Expansão regional

Sudeste, Centro-Oeste, Sul, Nordeste e Norte, com adaptações econômicas e institucionais.

### Onda E - Inteligência nacional

Indicadores agregados, tipologias compartilháveis sem dados identificáveis, maturidade, governança federativa e comparação entre pares.

---

## 10. Arquitetura de implementação

Manter os padrões consolidados no projeto CFQ:

- monorepositório;
- ingestão separada de API e frontend;
- Cloud Run Services para API/web;
- Cloud Run Jobs para ingestão;
- Cloud Storage e BigQuery em camadas;
- PostgreSQL para workflow transacional;
- migrations aditivas;
- contratos versionados;
- ingestão idempotente;
- validação de SQL antes da execução;
- rollback lógico;
- releases com evidências.

Para municípios sem infraestrutura, utilizar modelo SaaS governamental multi-tenant com forte isolamento ou instância exclusiva conforme risco e capacidade.

---

## 11. Releases e marcos

As versões de implementação e os marcos do produto são trilhas relacionadas, mas não equivalentes. Uma implementação local pode comprovar comportamento técnico sem concluir o gate institucional correspondente.

### 11.1 Versões executadas

| Versão | Conteúdo | Estado |
|---|---|---|
| Especificação `0.3.0` | Produto SIRTA, domínio, governança, contratos e roadmap | Mantida |
| Implementação `0.3.1` | F0/Sprints 0 e 1, fundação segura, identidade, tenant e auditoria | `LOCAL_GO` |
| Implementações `0.3.2-0.3.7` | Evolução local S0-S4, G6 financeiro, G7 ocorrências e G8 calendário sintético | `LOCAL_GO` nos recortes informados |
| Próxima versão | Saneamento Alembic `0.3.8` concluído; catálogo técnico de fontes sintéticas em seguida | `LOCAL_GO` na higiene; F3 oficial `BLOCKED` |

### 11.2 Marcos futuros do produto

| Marco sugerido | Conteúdo | Dependência |
|---|---|---|
| v0.4 | Marco de fundação segura, já absorvido pela linha de implementação 0.3.x | Evidência local preservada |
| v0.5 | Registro de fontes públicas/restritas, catálogo, conectores públicos prioritários, Bronze/Silver/Gold e qualidade | G0/G1 e autorização explícita da Fase 3 |
| v0.6 | MVP ISS, regras e painel de potencial | G4 homologado |
| v0.7 | Casos e cobrança administrativa | Créditos validados e fluxo autorizado |
| v0.8 | Parcelamentos, pagamentos e dívida ativa | Regras municipais e integrações homologadas |
| v0.9 | Transferências e prontidão IBS/CBS oficiais | G7/G8 oficiais homologados |
| v1.0 | Piloto municipal homologado | G9 |
| v1.1 | Implantação municipal ampliada | Aceite do piloto |
| v2.0 | Plataforma regional/nacional | G10 e governança interfederativa |

---

## 12. Equipe mínima

- patrocinador municipal;
- gestor do programa;
- especialista tributário;
- Procuradoria;
- controle interno;
- encarregado de dados;
- arquiteto de solução;
- engenharia de dados;
- backend;
- frontend;
- DevSecOps;
- QA;
- suporte e treinamento.

Para municípios pequenos, as funções técnicas podem ser providas centralmente pela plataforma, preservando as decisões administrativas e jurídicas no município.

---

## 13. Riscos e respostas

| Risco | Resposta |
|---|---|
| Dados incompletos | Diagnóstico, quarentena e reconciliação |
| Cobrança indevida | Gate obrigatório de validação |
| Percentual de recuperação artificial | Denominador elegível versionado |
| Exposição de dados | Zero Trust, ABAC, DLP e auditoria |
| Dependência de fornecedor | Contratos, exportação e adaptadores |
| Mudança normativa | Regras e calendário parametrizados |
| Baixa capacidade municipal | Serviço gerenciado e implantação por template |
| Falha de integração | Contratos e observabilidade por fronteira |
| Promessa comercial excessiva | Metas somente após diagnóstico |
| Mistura de transferências e créditos | Módulos e conceitos separados |
| Fonte pública tratada como prova de débito | Papel da fonte, validação humana e proibição de cobrança automática |
| Mudança ou indisponibilidade de fonte externa | Contrato versionado, detecção de schema drift, cache bruto e suspensão controlada |
| Coleta pública sem base ou termos compatíveis | Catálogo, revisão de finalidade/licença e preferência por API ou arquivo oficial |
| Migration dependente de seed mutável | Separar schema e seed, tornar carga idempotente e testar todos os caminhos de upgrade |
| Confusão entre gate local e homologação oficial | Estado composto `LOCAL_GO/OFFICIAL_BLOCKED` e evidência separada por fronteira |

---

## 14. Critérios de sucesso do programa

- 100% das bases selecionadas inventariadas;
- 100% das fontes ingeridas com órgão, finalidade, base legal, versão, competência e linhagem registradas;
- cargas rastreáveis e reconciliadas;
- ausência de cobrança sem validação registrada;
- redução de tempo entre identificação e providência;
- aumento do valor efetivamente recuperado;
- melhor acompanhamento de parcelamentos;
- redução de inconsistências;
- visão consolidada da dívida ativa;
- transferências monitoradas e conciliadas;
- prontidão mensurável para IBS/CBS;
- nenhum incidente grave de exposição de dados;
- resultados reconhecidos por usuários e órgãos de controle.

---

## 15. Fontes institucionais e política de ingestão

### 15.1 Diretórios e fontes transversais

- Catálogo Nacional de Dados: https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/catalogo-nacional-de-dados
- Portal Brasileiro de Dados Abertos: https://dados.gov.br/
- IBGE/SIDRA: https://sidra.ibge.gov.br/
- SICONFI/Tesouro Nacional: https://siconfi.tesouro.gov.br/
- Tesouro Transparente - transferências a estados e municípios: https://www.tesourotransparente.gov.br/temas/estados-e-municipios/transferencias-a-estados-e-municipios
- Portal da Transparência da União: https://portaldatransparencia.gov.br/
- Receita Federal: https://www.gov.br/receitafederal/

### 15.2 Fontes regulatórias

- Constituição, Emenda Constitucional nº 132/2023 e legislação complementar aplicável: https://www.planalto.gov.br/
- Comitê Gestor do IBS e documentação técnica: https://www.cgibs.gov.br/
- Receita Federal e cronogramas CBS/IBS: https://www.gov.br/receitafederal/
- legislação tributária e administrativa publicada oficialmente por estado e município.

### 15.3 Fontes setoriais de enriquecimento

- ANP para combustíveis;
- ANEEL e EPE para energia elétrica;
- Anatel para telecomunicações;
- Banco Central para instituições financeiras;
- CNES/DATASUS para estabelecimentos de saúde.

Fontes setoriais são referências de contexto e cruzamento. Elas não demonstram inadimplência nem substituem cadastro, lançamento, processo ou memória de cálculo da autoridade tributária competente.

### 15.4 Regras obrigatórias de consumo

1. Registrar a fonte antes da primeira coleta.
2. Utilizar endpoint, API, arquivo ou publicação do domínio oficial do órgão mantenedor.
3. Preservar na Landing/Bronze o conteúdo recebido, checksum, URL lógica, data/hora, competência e versão do leiaute.
4. Não promover dados para Silver/Gold sem contrato, qualidade e reconciliação aprovados.
5. Não combinar datasets para finalidade incompatível com a registrada.
6. Não publicar CPF, CNPJ completo de empresário individual ou outro dado pessoal sem avaliação de necessidade e base legal.
7. Suspender automaticamente o conector diante de mudança incompatível de esquema, licença, domínio ou integridade.
8. Registrar indisponibilidade, correção, reprocessamento e substituição de versão.
9. Exigir homologação humana para qualquer regra jurídica, tributária, cálculo de potencial ou indicador de recuperação.
10. Manter dados públicos, dados restritos e evidências fiscais separados por classificação e política de acesso.

Nenhuma regra jurídica ou tributária será ativada apenas por inferência da IA. Nenhuma lista pública será apresentada como relação de devedores sem fonte fiscal competente, processo aplicável e validação institucional.

---

## 16. Próxima ação executiva

Não há próximo item técnico automático na implementação local. A linha `0.3.8`–`0.3.13` em `feat/roadmap-technical-completion` está consolidada em `docs/delivery/TECHNICAL_COMPLETION_REPORT.md`.

G0, G1, G4, G7 oficial, G8 oficial, G9 e G10 permanecem bloqueados. Decisões e evidências exigidas: `docs/delivery/HUMAN_DECISIONS_REQUIRED.md`.
