# Release v0.3.7 - G8 IBS/CBS synthetic calendar

## Objetivo

Entregar um calendário regulatório local, versionado e **não vinculante**, sobre a especificação 0.3.0. Nenhuma regra, data ou alíquota é tratada como operacional.

`release_stage: G8_IBS_CBS_LOCAL`

## Escopo entregue

- Catálogo sintético com fontes listadas em `docs/legal/BOUNDARIES.md`.
- `GET /v1/regulatory/ibs-cbs` com `binding=false`, `operational=false`, `homologated=false`.
- Leiaute placeholder, mapa de impacto ISS e simulação explícitos como não operacionais.
- Tela Angular `/calendario` com aviso visual de estimativa.
- Migration `0009_g8_regulatory` aditiva.

## Fora de escopo

- Homologação oficial de normas, leiautes ou prazos.
- Inferência de obrigação legal a partir do modelo.
- G0 municipal, G1 diagnóstico, G4 especialista, G9 piloto, G10 produção.
- Conectores oficiais do Tesouro.

## Rollback

```bash
git revert <sha-da-fatia>
```

A migration é aditiva; remoção de `regulatory_items` exige ciclo de depreciação.

## Evidências

`evidence/releases/0.3.7/`

## Revisão

O implementador não autoaprova o gate G8 oficial. Uso operacional permanece bloqueado até homologação municipal e jurídica.
