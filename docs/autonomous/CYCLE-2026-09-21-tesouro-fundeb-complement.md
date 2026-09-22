# Ciclo autônomo 0.3.62 — Tesouro FUNDEB complement

## Contexto

Branch `feat/official-public-ingest`, PR #2. CI prévia verde.
UFs restantes sem CSV/API recente (RJ IP-blocked, PI ICMS vazio, SP HTML,
SC≤2017, RR/AP/MT/SE/PB/AM/TO). Fatia segura: allowlist COUN VAAT/VAAR/VAAF
e AJUSTE FUNDEB VAAT no CSV mensal Tesouro já aprovado.

## Entrega

- Fonte `TESOURO-FUNDEB-COMPLEMENT-VALORES`.
- Parser/family `FUNDEB_COMPLEMENT` + `AJUSTE_FUNDEB`.
- Fixture mínima no `tesouro-fpm-202608.csv`.
- Testes unitário + integração; migration `0065`.

## Não feito

- Ativação UF tabular nova (nenhuma candidata estável neste runtime).
- Homologação humana Gold.
- Carga nacional ilimitada.
