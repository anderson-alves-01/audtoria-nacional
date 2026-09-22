# Ciclo 2026-09-21 — Tesouro COINT FPM/ITR/IOF-Ouro/LC176

## Seleção

Dataset CKAN Transferências Obrigatórias por Município ainda tinha quatro
CSVs COINT sem ativação (distintos dos allowlists mensais):

- FPM por município (`d69ff32a-6681-4114-81f0-233bb6b17f58`)
- ITR por município (`f6ad4e51-fc7e-40bb-b35a-3686da7fde2d`)
- IOF-Ouro por município (`4248cd95-6d79-4520-9e17-48322eab6259`)
- LC 176/2020 por Município (`c833631a-0933-4e43-a0a5-f77c2fa2267d`)

## Implementação

- Fontes `TESOURO-FPM-COINT-VALORES`, `TESOURO-ITR-COINT-VALORES`,
  `TESOURO-IOF-OURO-COINT-VALORES`, `TESOURO-LC176-COINT-VALORES`.
- Conector existente `tesouro_coint_municipio_csv` (`max_rows=8`).
- Competências: FPM/ITR/LC176 `2025-01`; IOF-Ouro `2014-07` (série esparsa).
- Fixtures mínimas latin-1 + testes unitário/integração.
- Migration `0068_tesouro_coint_remaining` → `0.3.65`.
- Dashboard `/transferencias` inclui as quatro fontes.

## Notas

Pacote COINT municipal do dataset agora completo (CIDE/FEX/FUNDEB/LC87 +
estes quatro). Sem crédito. Sem carga nacional.
