# ROADMAP ESTRATÉGICO E TECNOLÓGICO 2026

## Plataforma Auditoria Nacional - SIRTA Municipal

**SIRTA - Sistema Integrado de Recuperação Tributária e Auditoria**  
**Lema:** “Auditar. Acompanhar. Recuperar.”  
**Versão do roadmap:** 1.0  
**Data-base:** setembro de 2026  
**Horizonte:** implantação inicial de 6 a 8 meses e evolução contínua

**Estado local (2026-09-18):** fatias sintéticas G2/G3/G5–G8 executáveis até implementação 0.3.7. Gates humanos G0, G1, G4, G7 oficial, G8 oficial, G9 e G10 estão **BLOQUEADOS** — ver `docs/delivery/HUMAN-GATES.md`.

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

Entregas:

- catálogo e solicitações de acesso;
- manifesto de carga;
- conectores de arquivos e bancos;
- Bronze/Silver/Gold;
- qualidade e quarentena;
- idempotência e retomada;
- reconciliação;
- lineage;
- rollback lógico;
- monitoramento de jobs.

Gate G3: reexecução sem duplicidade, lote inválido não publicado e totais reconciliados.

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

## 11. Releases sugeridas

| Release | Conteúdo |
|---|---|
| v0.3 | Produto SIRTA, domínio, governança e diagnóstico |
| v0.4 | Fundação segura, identidade, tenant e auditoria |
| v0.5 | Catálogo, Bronze/Silver/Gold e qualidade |
| v0.6 | MVP ISS, regras e painel de potencial |
| v0.7 | Casos e cobrança administrativa |
| v0.8 | Parcelamentos, pagamentos e dívida ativa |
| v0.9 | Transferências e prontidão IBS/CBS |
| v1.0 | Piloto municipal homologado |
| v1.1 | Implantação municipal ampliada |
| v2.0 | Plataforma regional/nacional |

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

---

## 14. Critérios de sucesso do programa

- 100% das bases selecionadas inventariadas;
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

## 15. Fontes institucionais para implementação

- Emenda Constitucional nº 132/2023 e legislação complementar aplicável: https://www.planalto.gov.br/
- Comitê Gestor do IBS e documentação técnica: https://www.cgibs.gov.br/
- Receita Federal e cronogramas CBS/IBS: https://www.gov.br/receitafederal/
- Tesouro Transparente - transferências a estados e municípios: https://www.tesourotransparente.gov.br/temas/estados-e-municipios/transferencias-a-estados-e-municipios
- Fontes estaduais oficiais para quota-parte de ICMS e IPVA.
- Legislação tributária e administrativa específica de cada município.

As fontes devem ser registradas no catálogo com versão, data de consulta, competência, responsável e finalidade. Nenhuma regra jurídica ou tributária será ativada apenas por inferência da IA.

---

## 16. Próxima ação executiva

Iniciar a Fase 0 com escolha do município piloto, criação do grupo gestor e autorização do diagnóstico. Em paralelo, iniciar a release v0.3 com o domínio SIRTA, modelo de estados, matriz de competências, contratos iniciais e checklist de diagnóstico.

