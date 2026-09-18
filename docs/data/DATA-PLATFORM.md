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

