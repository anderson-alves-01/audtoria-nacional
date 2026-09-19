# Release notes 0.3.19

Estado: `OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS`

## Nesta fatia

- `GET /v1/payments` + `POST /v1/payments` — painel oficial vazio; `recoveryInvented=false`; POST sempre 409.
- `GET /v1/active-debt` + `POST /v1/active-debt` — painel oficial vazio; `inscriptionEnabled=false`; POST sempre 409.
- `GET /v1/procuradoria` + `POST /v1/procuradoria` — workflow oficial vazio; `altersLegalStatus=false`; POST sempre 409.
- Telas `/pagamentos`, `/divida-ativa` e `/procuradoria` com loading/empty/erro e backend real.
- Migration aditiva `0022_f6_payments_active_debt` (meta 0.3.19).

## Não concluído

Backfill nacional, fontes estaduais, RFB territorial, F7 conciliação operacional, piloto, produção e homologação humana.
