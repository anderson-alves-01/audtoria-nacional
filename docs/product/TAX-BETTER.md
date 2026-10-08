# Tax Better

Estrutura do projeto. Brasília, 2 de outubro de 2026.

Fonte: `TAX BETTER - ESTRUTURA DO PROJETO.docx.pdf`. Este texto é o escopo vigente do produto. O que já está publicado no SIRTA (mapa, SICONFI, Tesouro, IBGE e painéis) permanece como referência e não é o objeto vigente. Gates e a ingestão de dado real restrito continuam sem ato.

A plataforma busca fato gerador tributário não conhecido e não declarado ao fisco estadual e municipal, para evitar a decadência fiscal. A leitura de “omisso”, o prazo de decadência e a base de cálculo pela tabela FIPE ficam pendentes de parecer. Não viram regra operacional neste registro.

## Tributos

Somente estes:

- ICMS
- ISS
- IPTU
- IPVA
- ITBI
- ITCMD

## ICMS — fatos geradores omissos

| Código no PDF | Hipótese |
|---|---|
| 3.2.1a | Venda de carro por pessoa jurídica revendedora, sem pagamento do ICMS |
| 3.2.1b | Venda de carro por pessoa física sócia de revendedora, sem pagamento do ICMS |
| 3.2.1c | Venda de carro por pessoa física com alto volume ou recorrência, sem pagamento do ICMS |
| 3.2.1d | Venda de carro por pessoa jurídica revendedora, com ICMS pago sobre base abaixo da tabela FIPE |
| 3.2.1e | Compra de bens de outro estado para uso, sem pagamento do DIFAL |
| 3.2.1f | Compra e venda de mercadorias, com volume acumulado de compras maior que o de vendas, e ICMS pago a menor |
| 3.2.1g | Compra por construtora ou empresa de reforma, sem recolhimento do ICMS do material fornecido pelo prestador quando produzido fora do local da prestação |
| 3.2.1h | Compra de materiais em outra unidade da federação por construtora ou empresa de reforma, sem recolhimento do ICMS-DIFAL |

### Fontes escritas

- 3.2.1a a 3.2.1d: extrato do DETRAN com as operações de transferência de veículos, e tabela FIPE.
- 3.2.1e a 3.2.1h: o PDF não nomeia a fonte.

CPF de sócio e extrato de transferência são dado pessoal restrito. Não entram sem acordo de proteção, finalidade registrada e ato. Não há conector do DETRAN nem da FIPE neste registro.

### Regras de apuração escritas

Cada regra gera lista, aponta base e pede apuração por malha fiscal. No produto, o resultado é ocorrência para análise humana. Não é crédito, não é cobrança e não dispara notificação sozinha.

- 3.2.1a: lista dos carros transferidos por empresas de revenda; compara com os carros registrados nas vendas dessas empresas; aponta a base mensal pelo valor de cada carro na tabela FIPE; solicita apuração do ICMS por malha fiscal.
- 3.2.1b: lista dos carros transferidos pelo CPF do sócio de empresa de revenda; aponta a base mensal pela FIPE; solicita apuração por malha fiscal.
- 3.2.1c: lista dos carros transferidos por CPF; filtra mais de uma ocorrência em prazo inferior a seis meses; aponta a base mensal pela FIPE; solicita apuração por malha fiscal. O PDF numera esta regra como 3.2.3c e aponta o item 3.2.1b; o caso correspondente no sumário é 3.2.1c.
- 3.2.1d: lista dos carros transferidos por empresas de revenda; compara com os valores registrados nas vendas; aponta a base mensal pela FIPE; solicita apuração por malha fiscal.
- 3.2.3g repete, no PDF, o mesmo texto de 3.2.1d e aponta o item 3.2.1d. Não há regra escrita para 3.2.1e, 3.2.1f, 3.2.1g e 3.2.1h.

## ISS, IPTU, IPVA, ITBI e ITCMD

O PDF só traz os títulos. Fonte e regra de apuração estão em branco, salvo o único caso de ISS nomeado: ISS de prestadores de fora do Distrito Federal, como lista de notas desses prestadores. Sem fonte e sem regra de apuração.

| Tributo | Casos | Fonte | Regra |
|---|---|---|---|
| ISS | Prestadores de fora do DF; demais casos em branco | em branco | em branco |
| IPTU | em branco | em branco | em branco |
| IPVA | em branco | em branco | em branco |
| ITBI | em branco | em branco | em branco |
| ITCMD | em branco | em branco | em branco |

Esses tributos só entram na fila quando o documento ganhar fonte e regra. A seção 3.3, regra de apuração do ganho Tax Better, está em branco. Sem fórmula e sem percentual.

## Processo

1. Alinhamento e recebimento dos dados.
2. Importação e processamento na plataforma, conforme a regra de apuração.
3. Apuração, validação e aprovação dos contribuintes elencados para envio e integração com a saída de notificação.
4. Integração para gerar notificações de malha fiscal aos contribuintes apurados, somente depois da aprovação do passo 3.

## Menu vigente

Integração, visão e administração. A barra abre esses três grupos. A referência já publicada (mapa, SICONFI, Tesouro, IBGE e os demais painéis) fica recolhida no grupo Referência publicada. As URLs antigas continuam.

### Integração — entrada

- Seleção do tipo de arquivo, do imposto, do fato gerador e do período.
- Anexo de arquivo externo ainda não integrado.

### Integração — saída

Exportação ao sistema de malha fiscal, com imposto, cidade, período, contribuinte (CPF ou CNPJ) e tipo de pessoa. A aprovação usa os mesmos critérios. Sem aprovação, não há saída.

### Visão

A visão geral cruza, para cada imposto e cada fato gerador, dois lados:

| | Valor | Base de cálculo | Imposto |
|---|---|---|---|
| Operação | o que o arquivo do órgão trouxe | o que o arquivo do órgão trouxe | o que o arquivo do órgão trouxe |
| Malha | o que a malha trouxe | o que a malha trouxe | o que a malha trouxe |

A linha se abre por todas as variáveis presentes no arquivo (cidade, período e as demais colunas). Medida ausente permanece vazia. A soma de exemplo da planilha não é valor gravado. A saída permanece sem aprovação. `createsTaxCredit` fica falso.

Tabelas de apoio: impostos do escopo, órgão DETRAN (outro órgão entra na linha quando o arquivo o nomear) e os oito fatos geradores de ICMS. ISS, IPTU, IPVA, ITBI e ITCMD estão na tabela de impostos, ainda sem fato gerador. A recepção fica em `tax_better_intake_lines`. Não há carga do DETRAN neste registro.

O operador grava o canal (arquivo ou API) e o mapa de campos na tela de fontes, na fonte `TAX-BETTER-ENTRADA`. O catálogo YAML não é o lugar da coluna nem da URL. A API guarda só o nome do segredo. Arquivo sem leiaute e API sem nome de segredo são recusados. Campo obrigatório vazio vai para quarentena. A busca ao órgão continua bloqueada até o ato.

### Administração

Usuário, acessos e papéis.

## Fora do roadmap de engenharia

O PDF ainda lista plano comercial, investimentos e estrutura empresarial (remuneração, captação, custos, retorno, tipo societário e acordo de sócios). Esses itens não entram na fila técnica.

## Fila curta

1. Entrada de arquivo autorizado, com imposto, fato gerador e período.
2. Primeira regra de ICMS de veículo, quando existirem o extrato do DETRAN e a tabela FIPE autorizados.
3. Visão da ocorrência.
4. Saída aprovada para a malha.

A primeira entrega técnica, quando houver arquivo autorizado, é a regra de ICMS de veículo. A aprovação humana vem antes de qualquer saída.
