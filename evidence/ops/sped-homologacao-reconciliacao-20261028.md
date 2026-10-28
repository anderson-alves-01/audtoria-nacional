# Evidência SPED da homologação do Simulador (28/10/2026)

Gerado em 2026-10-28 14:07 UTC por `tools/ops/sped-homologacao-evidence.py`. Somente leitura sobre os originais. Nenhuma quantidade foi alterada e nada foi carregado no banco.

## Comandos executados

- `python tools/ops/sped-source-verify.py` (código de saída 0)
- `python tools/ops/sped-source-reconcile.py` (código de saída 0)
- `python tools/ops/sped-omission-audit.py` (código de saída 0)

## Saída da verificação de hash

```
OK docs/data/originais/Estat_NFe_CFOP_por_UF_2016_a_2025_v1_formatada.ods sha256=195cabcaa4d242fda0794c817116f216119e958dafea3fd12e4224f9e191685a
OK docs/data/originais/Estat_NFe_CFOP_2025_v1_formatada.ods sha256=4dc50922f7e9f582fc08ded7a3e4442203a1f1be3a60f603e09fd8202dcf292e
OK docs/data/Consolidado_Operacoes_UF_2021_2025_SPED.xlsx sha256=1091967dd768b72152cc4c4a9b01b8637eebe45827c268f658ad462044e02cf3
```

## Verificações

| ID | Verificação | Esperado | Observado | Resultado |
| --- | --- | --- | --- | --- |
| SP-01 | Hash SHA-256 e tamanho dos 2 originais e da planilha consolidada conferem | 0 e 3 OK | 0 e 3 OK | APROVADO |
| SP-02 | Os originais em docs/data/originais não foram alterados | limpo | limpo | APROVADO |
| SP-03 | 46.825 células reproduzidas (planilha) | 46825 | 46825 | APROVADO |
| SP-04 | 46.825 células iguais ao original | 46825 | 46825 | APROVADO |
| SP-05 | Células diferentes ou sem correspondência no original | 0 e 0 | 0 e 0 | APROVADO |
| SP-06 | Ausentes = legítimas + indevidas | 22343 | 22343 | APROVADO |
| SP-07 | Omissões sem regra publicada | 1041 | 1041 | APROVADO |
| SP-08 | Células ausentes no total | 22343 | 22343 | APROVADO |
| SP-09 | 1.041 omissões = recebidas confirmadas + pendentes (células) | 1041 | 1041 | APROVADO |
| SP-10 | 268.317.945 NF-e = recebidas confirmadas + pendentes | 268317945 | 268317945 | APROVADO |
| SP-11 | Recebidas confirmadas (células e NF-e) | 844 e 132237096 | 844 e 132237096 | APROVADO |
| SP-12 | Pendentes de classificação (células e NF-e) | 197 e 136080849 | 197 e 136080849 | APROVADO |
| SP-13 | CFOPs de transferência confirmados (recebidos e remetidos) têm direção própria | True, True, 8, 10 | True, True, 8, 10 | APROVADO |
| SP-14 | CFOPs sem classificação comprovada continuam pendentes | 1159,2159,1190,2170,1155,1156,1157,1158,5154,5157 | 1159,2159,1190,2170,1155,1156,1157,1158,5154,5157 | APROVADO |
| SP-15 | Somar recebidas e remetidas é recusado | recusou a mistura | recusou a mistura | APROVADO |
| SP-16 | Nenhum script saiu com erro | 0, 0, 0 | 0, 0, 0 | APROVADO |

Resultado: 16 de 16 verificações aprovadas.

## Origem dos números

- Reconciliação (46.825 células, 22.343 ausentes): `evidence/ops/sped-reconciliacao-20261028.md`.
- Auditoria das 1.041 omissões e reclassificação por CFOP: `evidence/ops/sped-auditoria-omissoes-20261028.md` e `evidence/ops/sped-omissoes-1041-20261028.csv`.
- Tabela oficial de CFOP (Sefaz-PE, `cfop.htm`, lida em 2026-10-28): só os CFOPs listados ali como transferência são confirmados.

Limites: a definição de `Quantidade NF-e` não existe nas fontes e a planilha não traz as entradas por transferência. Por isso nenhum indicador do SPED é promovido a CONFERIDO.
