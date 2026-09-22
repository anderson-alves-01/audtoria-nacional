# Ciclo 2026-09-20 — PR ICMS/IPVA HTML SEFA

- Fatia: `state_pr_html` + catálogo `ESTADO-PR-ICMS-QUOTA` / `ESTADO-PR-IPVA-QUOTA`
- Fonte: relatório HTML mensal SEFA/PR (`rrepassesmun.jsp`, Param_Tiporelatorio=MENSAL)
- Probe: HTTP 200; colunas ICMS líquido (pós-FUNDEB) e IPVA; join IBGE7 nome+UF
- AP: PROVENANCE_VERIFIED (link sefaz detalhes/17 → 404)
- RR: PROVENANCE_VERIFIED (painel HTML sem split ICMS/IPVA)
- DF: PROVENANCE_VERIFIED (não aplicável — sem municípios)
- Homologação humana Gold: não solicitada
- Resultado: PROGRESSED
