# Release notes 0.3.43

## Entrega

- Ativação técnica de IPVA do Piauí via SEFAZ Repasse WEB (`state_pi_repasseweb_html` / `ESTADO-PI-IPVA-QUOTA`): sessão JSF/PrimeFaces, tabela HTML agregada por município, join IBGE7 nome+UF.
- SE marcado `PROVENANCE_VERIFIED` (demonstrativos mensais PDF no SharePoint; sem CSV/API).
- ICMS-PI permanece sem ativação: o mesmo UI retornou “Nenhum repasse encontrado” nos intervalos sondados.
- Gold continua `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`. Sem crédito, cobrança ou notificação.

## Evidência

- `evidence/releases/0.3.43/`
- Probe: `pi-ipva-probe.txt`

## Não inclui

- Homologação humana Gold
- Gates G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10
- Carga nacional RFB
- `terraform apply` / deploy
