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
- Operação: `tools/ops/prod-sped-ingest.py` (padrão `--dry-run` sem rede; `--execute` exige `--confirm <sha256>` e `--expect-tenant`).
- Achado aberto: a planilha traz volumes implausíveis por UF (AC e RR no lugar de UFs maiores). Conferir com a fonte primária do SPED antes de qualquer uso analítico.
- Rollback: retirar o lote da leitura por operação registrada, preservando os bytes. A tabela é aditiva.
