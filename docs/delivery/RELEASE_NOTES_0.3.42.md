# Release notes 0.3.42

## Fatia

AC IPVA PUBLIC_OPEN via Portal da Transparência (POST+CSRF JSON).

## Entregas

- Connector `state_ac_transparencia_json` (CSRF session + JSON export; join IBGE7 nome+UF; competência `2025-01`)
- Fonte `ESTADO-AC-IPVA-QUOTA` `TECHNICALLY_APPROVED`
- Fixture mínima `ac-transparencia-repasses-2025-01.json`
- HTTP client com `fetch_csrf_form_post` / `fetch_post`
- Migration `0045_state_ac_ipva_activation`
- Probes: PB PDF-only e AM HTML-per-município → `PROVENANCE_VERIFIED` (sem ativação)

## Restrições

- Sem crédito/cobrança/inscrição a partir de fonte pública
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`
- Gates humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados
