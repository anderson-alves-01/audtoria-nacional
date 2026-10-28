# Plataforma de dados

## Fluxo padrão

`fonte -> landing -> bronze -> validação -> silver -> regras -> gold -> API/painel`

## Manifesto de carga

Cada execução registra: `run_id`, tenant, território, fonte, URI lógica, checksum, tamanho, competência, extração, esquema, finalidade, base legal, contagens, status, erros, versão do código e operador.

## Qualidade

Dimensões: completude, validade, unicidade, consistência, atualidade, integridade referencial e reconciliação financeira.

Status: `RECEIVED`, `VALIDATING`, `QUARANTINED`, `VALIDATED`, `HOMOLOGATED`, `PUBLISHED`, `ROLLED_BACK`.

## Idempotência

A chave combina tenant, fonte, competência, checksum e versão do layout. Reexecução igual retorna a execução anterior; versão nova cria lote novo sem sobrescrever evidência.

## Rollback

Rollback é lógico: retirar o lote da visão publicada, preservar bytes e evidências, recalcular Gold e registrar motivo/aprovador.

## Primeiras fontes do MVP

- Arrecadação municipal de ISS.
- Cadastro mobiliário.
- Dívida ativa.
- PIB de serviços e indicadores oficiais.
- Cadastro de atividades econômicas.


## SPED NF-e por UF e CFOP (SPED-NFE-UF-CFOP)

Fonte pública agregada, carga por upload do xlsx (conector `uploaded_xlsx`, nunca pela ingestão genérica). Contrato em `contracts/sources/official-catalog.yaml` (layout `sped-nfe-uf-cfop-v1`, competência `2021-25`).

- Bronze: o arquivo original fica em `landing/SPED-NFE-UF-CFOP/…/<sha256>/payload.bin` com manifesto.
- Silver/Gold: `sped_operation_facts` (migration aditiva 0108). Nível `SERIE` com 945 linhas (27 UFs × 5 anos × 7 operações) e nível `CFOP` com a base por UF, CFOP e ano.
- Reconciliação que bloqueia o lote inteiro: Série × soma da Base CFOP (quantidade exata, valor com tolerância de centavos) × Consolidado UF. A classificação de CFOP por prefixo gera só aviso.
- Idempotência: tenant + checksum + layout. Repetir o envio devolve `replay=true`.
- Semântica: quantidade é observada. Valor em R$ é rateio estimado (`valueKind=ESTIMATED_ALLOCATION`), não é valor fiscal, não é homologado, não é somado entre operações. Valor ausente fica `null` e aparece como `—`, nunca zero.
- Acesso: envio só do administrador técnico; leitura em `GET /v1/sped-operacoes` com papel fiscal e sessão com tenant, território e finalidade. Todo envio e leitura gera evento de auditoria.
- Painel: `/sped-operacoes` em Referência publicada, com faixa permanente de base exploratória.
- Como o valor estimado é calculado: não é calculado pela plataforma. Vem da planilha como rateio: valor nacional do CFOP no ano × quantidade da UF no CFOP/ano ÷ soma das quantidades de todas as UFs no mesmo CFOP/ano. O total nacional não está no arquivo (só é recuperável somando as UFs), então não há conferência independente. A faixa 0,1x a 10x da planilha é sinalizador, não atestado. Um erro na quantidade de uma UF contamina o valor dela.
- Painel (ajustes de 2026-10-27): UF escolhida isola o hexágono nos dois mapas ("Mostrar todas as UFs" restaura); quantidade e valor estimado ficam no mesmo gráfico, em duas linhas, com modo "Eixos separados" (esquerdo quantidade, direito R$) ou "Índice (ano inicial = 100)".
- Painel (segundo ajuste de 2026-10-27): rótulo único "Valor" (sem selo "Estimado" por painel; o banner "Exploratório · não homologado" e a seção "Como o valor é calculado" permanecem); um único mapa por UF mostra quantidade e valor em cada hexágono, com seletor "Colorir por Quantidade | Valor"; botão "Simular com esta UF e operação" abre `/simulador?uf=..&operacao=..` (parâmetros validados contra lista permitida).
- Simulador, segundo ajuste: dados públicos e imposto apurado vêm primeiro (só com carga validada) e os campos de quantidade e valor vêm logo depois e funcionam sem carga SPED (UF e operação com listas fixas); os textos "Parte A" e "Parte B" e o seletor de Município (sem fonte pública) foram removidos da tela.
- Simulador (`/simulador`, grupo acima de Visão): Parte A mostra quantidade, valor estimado, operação e imposto por ano para uma UF e uma operação; Parte B recebe quantidade e valor desejados e compara com um ano público, com a diferença do imposto. Imposto = valor × alíquota (ITCD 6%, ITBI 3%, ISS 5%, ICMS modal interna por UF do anexo fornecido pelo usuário em 27/10/2026; AC lido como 19%, a confirmar). É simulação aritmética no navegador, não apuração fiscal, não grava nada. Município e tipo de bem/serviço não existem no dado público: município fica desabilitado e o tipo de bem é só rótulo. Imposto e operações nunca são somados entre si.
- Operação: `tools/ops/prod-sped-ingest.py` (padrão `--dry-run` sem rede; `--execute` exige `--confirm <sha256>` e `--expect-tenant`).
- Achado aberto: a planilha traz volumes implausíveis por UF (AC e RR no lugar de UFs maiores). Conferir com a fonte primária do SPED antes de qualquer uso analítico.
- Rollback: retirar o lote da leitura por operação registrada, preservando os bytes. A tabela é aditiva.
