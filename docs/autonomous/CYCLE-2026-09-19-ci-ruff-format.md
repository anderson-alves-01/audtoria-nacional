# Ciclo — correção CI ruff format (PR #2)

Data: 2026-09-19  
HEAD base: `0978085`  
Branch: `feat/official-public-ingest`  
PR: #2

## Seleção

CI `python` vermelha nos runs `35442958209` / `35442955746`. Regra do controlador: corrigir CI antes de nova funcionalidade. Itens PENDING (RFB, ICMS/IPVA, DOC) adiados.

## Causa

`ruff format --check` falhou em 3 arquivos da fatia 0.3.23 (backfill).

## Correção

`python -m ruff format` em:

- `apps/api/src/sirta_api/config.py`
- `apps/api/src/sirta_api/domain/backfill_controls.py`
- `tests/unit/test_backfill_controls.py`

## Evidência

- `ruff format --check` + `ruff check`: OK
- `pytest tests/unit/test_backfill_controls.py tests/unit/test_ingest_observability.py`: 13 passed
- `evidence/releases/0.3.23/ruff-format-fix-tests.txt`

## Não feito

Nova funcionalidade (RFB territorial, estados, setorial). Homologação humana.
