# CGU NF-e (2021 a 2025): pipeline reproduzível e auditável

Fonte: notas fiscais eletrônicas (NF-e) do Portal da Transparência da CGU.
Catálogo: <https://portaldatransparencia.gov.br/download-de-dados/notas-fiscais>.
Dicionário: <https://portaldatransparencia.gov.br/dicionario-de-dados/notas-fiscais>.
ZIP mensal: `https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/nfe/AAAAMM_NFe.zip`.

Código: `apps/api/src/sirta_api/adapters/ingest/cgu_nfe/` e regras puras em
`apps/api/src/sirta_api/domain/cgu_nfe.py`. Versão de processamento: `cgu-nfe-v1`.

O pipeline é local e fora do Postgres: os agregados ficam em SQLite e os ZIPs em arquivos, sob
`var/datalake/cgu-nfe/` (ignorado pelo Git). Nenhum dado é publicado nem enviado a terceiros.

## Estado da execução de 29/10/2026

Veja `evidence/ops/cgu-nfe-*-20261029.*`. O WAF da rodada de 28/10 não se repetiu: os 28 meses
ainda pendentes baixaram com HTTP 200 (`run_id=f1aec0539244`). Resumo honesto:

| Item | Resultado |
| --- | --- |
| Meses pedidos | 60 (2021-01 a 2025-12) |
| Listados no catálogo | 53 |
| Não listados | 7 (jan, fev, mar, mai, jun, jul, ago de 2021; HEAD devolve 403) |
| Baixados, validados e processados | 53 (todos os listados) |
| Bloqueados por verificação humana | 0 nesta rodada |
| Arquivo final | `var/datalake/cgu-nfe/exports/CGU_NFE_2021_2025_PARCIAL.xlsx` (sha256 `2e31b75b02d1f79641688c6e59603946ff1fdd17a132cbf838f9ebbb1330dd9b`) |

O nome permanece `PARCIAL` porque 7 meses não existem no catálogo. Totais locais (53 meses):
7.045.577 notas (R$ 329.592.242.391,61) e 25.261.747 itens (R$ 366.792.907.305,23). A
reconciliação da exportação bateu com o banco. Quarentena: 0 linhas. Alerta recorrente:
`ITEM_UNIDADE_AUSENTE` em 51 meses (itens mantidos com unidade vazia).

Reprodução da extração anterior (`docs/data/CGU_2021_2025_*PARCIAL*`):

- Os 30 meses da referência foram reproduzidos (mesmo SHA-256, mesmas contagens e mesmos
  valores). Totais anuais de 2021, 2022, 2023 e 2024 do CSV de detalhe iguais.
- Consistência interna do pacote anterior: 3.878.534 notas e 13.482.862 itens;
  969.885 combinações ano/UF/NCM/CFOP/unidade; itens R$ 196.845.092.168,69.
- Meses locais sem correspondente na referência: 202402 a 202512 (a referência parava em
  202401).

## Comandos

Tudo roda da raiz do repositório. `--root` muda a pasta de trabalho; `--months AAAAMM ...`,
`--since` e `--until` limitam os meses. Cada execução imprime um `run_id`, gravado no manifesto e
no processamento.

```powershell
$env:PYTHONPATH = "apps/api/src"
$m = "sirta_api.adapters.ingest.cgu_nfe"

python -m $m status                       # estado de cada mês, sem rede
python -m $m inventory --probe --out evidence/ops/inventario.csv   # catálogo + HEAD (só leitura)
python -m $m download --concurrency 2 --pause 10 --retries 3 --backoff 5 --breaker 2
python -m $m import-zip C:\Downloads\202402_NFe.zip                 # ZIP baixado no navegador
python -m $m process                      # processa ZIPs validados (idempotente)
python -m $m audit --out evidence/ops/auditoria.csv
python -m $m export                       # XLSX de seis abas + CSVs completos
python -m $m reconcile-reference --out evidence/ops/referencia.md
python -m $m resume                       # download + processamento dos pendentes
```

Códigos de saída: `0` ok; `1` falha de validação, processamento ou reconciliação; `2` catálogo
indisponível, nada a exportar ou entrada recusada; `3` download com bloqueio ou arquivo inválido.

Retomada: `.part` em `bronze/.partial/` e `Range`. Se o servidor ignora `Range`, o arquivo
recomeça. ZIP recusado vai para `bronze/.rejected/` como evidência, nunca para o bronze.

## Estados do mês

Derivados dos fatos gravados, nunca do nome do arquivo.

| Estado | Significado |
| --- | --- |
| `NAO_LISTADO` | catálogo não lista o mês (ou o catálogo ainda não foi lido) |
| `DOWNLOAD_PENDENTE` | listado, sem arquivo validado |
| `DOWNLOAD_BLOQUEADO` | GET devolveu verificação humana (HTTP 405/HTML) ou limite |
| `ARQUIVO_INVALIDO` | HTML no lugar do ZIP, truncado, CRC ruim, nome inseguro, dados de outro mês |
| `BAIXADO_VALIDADO` | ZIP no bronze com SHA-256 registrado, ainda não processado |
| `PROCESSAMENTO_CONCLUIDO` | processado com o mesmo SHA-256 e a mesma versão |

Um ZIP validado importado à mão encerra o bloqueio do mês.

## Validações de arquivo

Assinatura `PK`, detecção de HTML (página de erro ou de verificação humana), tamanho esperado,
estrutura, CRC de todos os membros, SHA-256, nomes de membro seguros (sem `..`, caminho absoluto
ou `:`), limite de tamanho descomprimido e de razão de compressão. A importação manual usa as
mesmas validações. Se os dados do ZIP não pertencem ao mês informado (menos de 50 % das notas com
data no mês), o processamento é recusado antes de gravar.

## Leitura e armazenamento

- Leitura em streaming dentro do ZIP; nada é extraído em disco.
- Separador `;`, texto entre aspas, Windows-1252 (UTF-8 com ou sem BOM também é aceito e
  reportado quando difere). Vírgula decimal.
- Cabeçalho mapeado por nomes normalizados do dicionário (sem acento, maiúsculas). Coluna
  obrigatória ausente falha fechado. Colunas novas são listadas na auditoria (`INFO`), não
  descartadas em silêncio. Os cabeçalhos reais de 202401 e 202402 conferem com o mapa.
- Dinheiro em centavos inteiros. Valor com mais de duas casas é recusado (quarentena), nunca
  arredondado. Quantidade em `Decimal`, com a precisão da fonte. Campo vazio é ausente, nunca zero.
- Chave de acesso (44 dígitos), NCM, CFOP e unidade ficam como texto. Dígito verificador
  divergente é só reportado.
- Duplicidade: cópia idêntica conta uma vez e é reportada. Cópia conflitante da mesma chave (ou
  chave+item) põe todas as versões em quarentena, fora dos totais, com arquivo e linha. A mesma
  chave em outro mês é só reportada.
- Idempotência: o mês é reprocessado só se o SHA-256 ou a versão mudarem. Um novo arquivo
  substitui os derivados do mês e mantém o histórico do manifesto (`SUPERSEDED`).
- Privacidade: CPF/CNPJ e nomes não entram no SQLite nem nas exportações. Só digests de chave.
  A quarentena mostra o digest da chave e a linha no ZIP.

## Regras de interpretação

- UF e município são os do **emitente** (local do fornecedor). A UF do destinatário é outra
  dimensão. Não se infere município de entrega ou consumo. A grafia é preservada; variantes
  viram linhas separadas.
- Quantidade é a **declarada comercialmente**, por unidade literal. Não é quantidade física
  padronizada, não se soma entre unidades e não se convertem embalagens. O mesmo NCM e unidade
  podem reunir produtos distintos.
- A descrição na planilha é a do NCM/SH informada pela fonte (tipo de produto). A descrição
  comercial do item não é agregada e fica no ZIP.
- CFOP não é usado para classificar compra ou venda. A planilha só o preserva.
- A base NF-e não representa todo o mercado, todas as compras públicas nem NFS-e. Valor de nota
  não é pagamento.
- **Bruto e visões filtradas.** O total bruto inclui todas as notas aceitas, canceladas inclusive
  (mesmo escopo da extração anterior). As colunas de canceladas e de exceto canceladas são
  separadas.
- **Cancelamento.** Cancelada quando o evento mais recente da nota, ou algum evento da tabela de
  eventos, contém `CANCEL` (cancelamento é terminal e a regra é a da extração anterior). Em 202401
  e 202402 a tabela de eventos veio vazia e nenhuma nota saiu cancelada. Em meses posteriores há
  cancelamentos registrados (por exemplo 4.714 em 202111). Nota sem
  evento fica `SEM_EVENTO_INFORMADO` e não é chamada de autorizada. A regra não prova validade
  fiscal.
- **Nota versus itens.** A soma dos itens não é forçada a igualar o valor da nota. Em 202401,
  33.674 de 118.914 notas com itens diferem da soma dos itens; em 202402, 14.642 de 61.640. A
  causa não foi investigada nesta rodada e não se conclui irregularidade. As maiores diferenças
  estão em `notas_diferenca_itens` (200 por mês).
- **Itens sem nota** entram no bruto de itens em `ITEM_SEM_NOTA` ou `NOTA_EM_QUARENTENA` e são
  contados à parte. Nenhum ocorreu em 202401 e 202402.

## Exportação

`CGU_NFE_2021_2025_PARCIAL.xlsx` (ou `COMPLETO` com os 60 meses processados) e CSVs completos
(`;`, UTF-8 com BOM, vírgula decimal, valores exatos):

1. `Consolidado por UF`: ano, UF, meses com dados, notas e valores bruto, cancelado, exceto
   cancelado, itens, itens sem nota aceita, fonte.
2. `Municípios`: idem por município do emitente.
3. `Bens e serviços`: ano, UF, NCM, descrição do NCM, CFOP, unidade, itens, quantidade declarada,
   valores. Se as combinações passarem de 1.000.000 de linhas, a aba omite o CFOP e o CSV
   `bens_servicos_completo` traz tudo. Nada é truncado em silêncio.
4. `Série histórica`: 60 linhas. Mês sem dados mostra `SEM DADOS` e o motivo; zero só para mês
   processado.
5. `Auditoria`: verificações por mês e pendências de cobertura.
6. `Fontes e metodologia`: URLs, versão, regras, limites e manifesto dos arquivos.

CSVs adicionais: `serie_historica`, `auditoria`, `manifesto_arquivos` (URL, data de aquisição,
origem, SHA-256, igualdade com a referência), `quarentena`, `notas_diferenca_itens`,
`reconciliacao_exportacao`. O Excel guarda cerca de 15 dígitos significativos; os CSVs são a cópia
exata. Códigos (NCM, CFOP) são texto no XLSX. Ao abrir o CSV no Excel, importe a coluna como texto.

A exportação recusa rodar sem nenhum mês processado e recompõe os totais a partir dos CSVs e do
XLSX gravados, comparando com o banco (`reconciliacao_exportacao`). Divergência derruba o comando.

## Auditoria

Por mês, na tabela `auditoria`: formato, colunas novas, linhas lidas e aceitas, chaves
inválidas e duplicadas, itens sem nota, notas sem itens, nota diferente da soma dos itens, datas
fora do mês, campos ausentes, cancelamentos, eventos sem nota, chaves em outros meses, linhas em
quarentena e a reconciliação entre leitura e agregados gravados (falha derruba o mês em uma única
transação). O detalhe da quarentena é limitado a 5.000 linhas por motivo e mês; a contagem total
é sempre exata e o corte é declarado na auditoria.

Alerta `ITEM_UNIDADE_AUSENTE` em 51 dos 53 meses processados. Itens mantidos com unidade vazia.

## Testes

`tests/unit/test_cgu_nfe_domain.py`, `test_cgu_nfe_zipcheck_xlsx.py`, `test_cgu_nfe_acquire.py` e
`tests/integration/test_cgu_nfe_pipeline.py`: 104 testes. Usam apenas ZIPs **sintéticos**
identificados (`tests/helpers/cgu_nfe_synthetic.py`, nomes "SINTETICO"), que nunca aparecem em
entregáveis oficiais. Cobrem: página de verificação humana no lugar do ZIP, ZIP truncado, CRC,
nomes inseguros, razão de compressão, download com retomada e sem suporte a `Range`, tentativas
com espera progressiva, disjuntor, importação manual e hash de referência, leitura e valores,
duplicidades, itens sem nota, datas fora do mês, mês trocado, coluna obrigatória ausente,
cancelamento, nova execução idempotente, versão nova e arquivo novo, ausência versus zero,
reconciliação de exportação, limite do Excel e ausência de CPF/CNPJ, nomes e chaves completas nos
arquivos gerados.

Desempenho medido com ZIP sintético de 150 mil notas e 450 mil itens: 40 s por mês no processamento.

## Simulador (base pública local, 29/10/2026)

O Simulador (`/simulador`) lê `GET /v1/cgu-nfe`, que agrega o SQLite local por UF do emitente e
ano. Não é ingestão Gold, não passa pelo Postgres e não lê o bronze (sem CPF/CNPJ/nomes na API).
Quantidade pública = número de itens, visão exceto canceladas. Valor público = soma dos itens em
centavos, mesma visão. Imposto do Simulador continua sendo valor × alíquota (indicador
`simulador_imposto_apurado_dados_publicos` permanece NAO_CONFIAVEL; alíquotas não homologadas).

Indicadores CONFERIDO neste recorte, por decisão do responsável em 29/10/2026:

- `cgu_nfe_itens_uf_ano`
- `cgu_nfe_valor_itens_uf_ano`

O que não está conferido: mercado inteiro, compras públicas totais, NFS-e, município de
consumo/entrega, soma de quantidade entre unidades, valor da nota como pagamento, imposto apurado.
Cobertura PARCIAL 53/60. O painel `/sped-operacoes` não muda e o SPED não alimenta o Simulador.

Se nenhum dos dois SQLite existir, a API devolve `run: null`, `items: []` e `coverage: AUSENTE` —
nunca zero inventado. A API prefere `cgu-nfe-series.sqlite` (UF × ano + metadados de processamento,
sem chave, CPF/CNPJ ou bronze) e só então o `cgu-nfe.sqlite` completo. Exportar o recorte:
`python -m sirta_api.adapters.ingest.cgu_nfe export-series --out apps/api/data/cgu-nfe-series.sqlite`.
O slim versionado tem 32 KiB, sha256
`d1f4ec38ef0dce4689500e2545297c67b63fdb10d9928dcf5ce195594c2dc475`, 135 linhas, 53 meses; SP 2024
bate com o recorte local (1.823.805 itens / R$ 30.362.096.754,69). O arquivo de 1,7 GB e o bronze
não entram na imagem. Publicado na API 0.3.127 (`sirta-prod-api:33`); a web permanece 0.4.25.
Bronze e Postgres não são tocados. Evidência: `evidence/ops/prod-cgu-series-0.3.127-20261029.txt`.

## Limites e dívida técnica

- Os 53 meses listados processaram com o mapa de colunas atual (falha fechada se faltar coluna
  obrigatória). Os 7 meses de 2021 não listados continuam sem fonte.
- O alerta visível nos meses reais é `ITEM_UNIDADE_AUSENTE`. Cancelamentos pelos eventos aparecem
  em vários meses a partir de 202110.
- A diferença entre valor da nota e soma dos itens precisa de análise própria.
- Rollback: apagar `var/datalake/cgu-nfe/` (nada fora dele é alterado) ou `process --force` para
  refazer um mês a partir do bronze.
