# Lacunas para atuar

Consulta pública de referência. Nenhum número deste relatório é crédito tributário, cobrança ou valor a recuperar. Este texto não aprova gate.

## 1. Publicado e utilizável no painel

Já está no datalake e aparece nos painéis de referência:

- IBGE: população, PIB e CEMP. São quantidade de referência. Não são potencial de ISS.
- SICONFI: cadastro de entes, RREO 2025 (6º bimestre) e DCA 2024, só dos entes já percorridos.
- Tesouro mensal com arquivo completo na carga: FPM, ITR, IPI-exportação, royalties, LC 176, IOF-ouro e complementação do FUNDEB.
- Repasses estaduais publicados, inclusive Bahia, Maranhão, Goiás e as duas fontes do Acre conferidas nesta execução.
- Contexto setorial e Focus já carregados (ANP, ANEEL, EPE, Anatel, CNES, Banco Central).
- Documentos do Planalto, não vinculantes.

Receita da conta-mãe, só dos entes já carregados, conferida em `/v1/dashboards/financeiro`:

- RREO, receita corrente até o bimestre, 2025: R$ 28.811.154.367,62
- RREO, previsão atualizada, 2025: R$ 26.264.825.083,13
- DCA, receitas brutas realizadas, 2024: R$ 44.466.645.888,34

A soma não é o total nacional e não é valor a recuperar. Cobertura: 114.454 linhas de RREO e 142.139 de DCA.

Acre, uma chamada cada, HTTP 200, `PUBLISHED`, `replay=true`, 22 registros recebidos, 20 publicados, 2 em quarentena, `taxCreditCreated=false`. Não houve linha nova. Evidência: `evidence/ops/prod-acre-retry-20260923.txt`.

## 2. Continuidade automática, sem ato seu

Próxima carga pública continua em fatias de 5 entes. Um POST nacional continua rejeitado.

- RREO 2025, 6º bimestre: cursor 125, faltam 5.445 entes, `IN_PROGRESS`.
- DCA 2024: cursor 150, faltam 5.420 entes, `IN_PROGRESS`.

## 3. Teto técnico de 8 linhas

Estas fontes COINT publicaram no máximo 8 linhas porque o catálogo tem `max_rows: 8`. Um novo POST do mesmo arquivo não acrescenta linhas: o replay usa o checksum e o leiaute. Publicar o CSV inteiro por cima criaria um segundo Gold da mesma competência, e o painel soma todos os Gold publicados.

Decisão necessária: autorizar uma publicação substituta do arquivo inteiro, com leiaute novo, sem manter as 8 linhas somadas ao total.

- TESOURO-FUNDEB-VALORES
- TESOURO-CIDE-VALORES
- TESOURO-LC87-VALORES
- TESOURO-FPM-COINT-VALORES
- TESOURO-ITR-COINT-VALORES
- TESOURO-IOF-OURO-COINT-VALORES
- TESOURO-LC176-COINT-VALORES

TESOURO-FEX-VALORES também tem esse teto, mas a competência 2025-01 voltou com células vazias. Não repetir essa competência. Se houver outro mês com valor publicado, apontar a URL e a competência.

## 4. Ato humano

Estas fontes não entram sem o ato indicado. G0, G4, G7 oficial e G10 permanecem NO-GO. `real_data_ingestion` permanece `BLOCKED_UNTIL_DPA_AND_AUTHORIZATION`.

- ISS, IPTU e ITBI: DPA assinado, ato de G0 e arquivo municipal apontado. Sem isso a carga restrita continua recusada.
- Dívida ativa, pagamentos e processos municipais: o mesmo pacote. Os painéis de cobrança, pagamentos e dívida ficam vazios de propósito.
- Portal da Transparência: credencial institucional da API. Sem chave a fonte não é consultada.
- Previsto de FPM ou de outro repasse: URL oficial do catálogo e autorização de G7. Sem URL o previsto não é publicado. A diferença, quando os dois lados existirem, é ocorrência, não crédito.
- SICONFI-RGF, período 3 de 2025: a API devolveu contagem 0. Não repetir esse período. Outro período só com a competência oficial indicada.
- Minas Gerais (ICMS, IPVA e IPI): o arquivo oficial veio só com cabeçalho e todas as linhas ficaram em quarentena. Não repetir. Um arquivo novo, com municípios e valores, precisa ser apontado.
- Funil de recuperação: não há funil de crédito publicado neste território. Não inventar etapas nem valor a recuperar.
