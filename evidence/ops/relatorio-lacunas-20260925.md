# Lacunas para atuar

Consulta pública de referência. Nenhum número deste relatório é crédito tributário, cobrança ou valor a recuperar. Este texto não aprova gate.

## 1. O que ainda está rodando sozinho

A carga pública do DCA 2024 segue ativa, em fatias de 5 entes, sem crédito tributário. Na manhã de 25 de setembro o cursor local estava em 820, com cerca de 4.750 entes ainda por percorrer. Cada fatia leva cerca de 2 a 3 minutos. O restante do DCA leva em torno de dois dias nesse ritmo.

O RREO 2025, 6º bimestre, já fechou: a API recusou nova fatia porque a partição está completa.

O tempo de inatividade do balanceador de produção foi elevado de 60 para 300 segundos. Sem isso a fatia grande era cortada antes de gravar. Evidência da sequência: `evidence/ops/prod-siconfi-finish-20260924.txt`.

## 2. Publicado e utilizável

Já está no datalake e aparece nos painéis de referência:

- IBGE: população, PIB e CEMP. São quantidade de referência. Não são potencial de ISS.
- SICONFI: cadastro de entes, RREO 2025 (6º bimestre, partição completa) e DCA 2024 dos entes já percorridos.
- Tesouro mensal com arquivo completo na carga: FPM, ITR, IPI-exportação, royalties, LC 176, IOF-ouro e complementação do FUNDEB.
- Repasses estaduais publicados, inclusive Bahia, Maranhão, Goiás e as duas fontes do Acre.
- Contexto setorial e Focus já carregados (ANP, ANEEL, EPE, Anatel, CNES, Banco Central).
- Documentos do Planalto, não vinculantes.

A receita da conta-mãe no painel soma só os entes já publicados. Não é o total nacional e não é valor a recuperar. O DCA ainda cresce enquanto a carga automática continua.

## 3. Teto de 8 linhas — resolvido

A publicação substituta v2 entrou em 25 de setembro. A amostra antiga deixou de ser publicada, então o painel não soma as 8 linhas com o arquivo inteiro. Os registros antigos continuam no datalake, só não entram na soma. Sem crédito tributário. Evidência: `evidence/ops/prod-coint-v2-20260925.txt`.

- TESOURO-FUNDEB-VALORES, 2025-01: 5.545 linhas publicadas
- TESOURO-CIDE-VALORES, 2025-01: 5.545 linhas publicadas
- TESOURO-LC87-VALORES, 2018-01: 5.545 linhas publicadas
- TESOURO-FPM-COINT-VALORES, 2025-01: 5.547 linhas publicadas
- TESOURO-ITR-COINT-VALORES, 2025-01: 5.050 linhas publicadas
- TESOURO-IOF-OURO-COINT-VALORES, 2014-07: 40 linhas publicadas (série esparsa)
- TESOURO-LC176-COINT-VALORES, 2025-01: 5.402 linhas publicadas

TESOURO-FEX-VALORES, competência 2025-01, continua de fora: o arquivo veio com células em branco.

## 4. Arquivo oficial vazio — apontar outra publicação

Não repetir a competência que já voltou vazia.

- TESOURO-FEX-VALORES, competência 2025-01: células em branco. Como resolver: indicar outro mês oficial que tenha valores, com a URL.
- Minas Gerais (ICMS, IPVA e IPI): o arquivo veio só com cabeçalho e todas as linhas ficaram em quarentena. Como resolver: apontar um arquivo novo, com municípios e valores.
- SICONFI-RGF, período 3 de 2025: a API devolveu contagem 0. Como resolver: indicar outro período oficial.

## 5. Ato humano — a carga restrita continua recusada

G0, G4, G7 oficial e G10 permanecem NO-GO. A ingestão de dado real permanece bloqueada até DPA e autorização.

- ISS, IPTU e ITBI: DPA assinado, ato de G0 e arquivo municipal apontado.
- Dívida ativa, pagamentos e processos municipais: o mesmo pacote. Os painéis de cobrança, pagamentos e dívida ficam vazios de propósito até esse ato.
- Portal da Transparência: credencial institucional da API.
- Previsto de FPM ou de outro repasse: URL oficial do catálogo e autorização de G7. A diferença, quando os dois lados existirem, é ocorrência, não crédito.
- Funil de recuperação: não há funil de crédito publicado neste território. Não inventar etapas nem valor a recuperar. A correção local da aba ainda não está na imagem web 0.4.7 em produção.
