# Operação de ingestão PUBLIC_OPEN (local)

## Regras

- Somente fontes `PUBLIC_OPEN` em runtime.
- Snapshots oficiais minimizados apenas em testes.
- Sem sintético em Landing/Bronze/Silver/Gold/API/dashboard.
- Toda linha Gold exige lineage até Silver, Bronze, manifesto, checksum SHA-256 e URL.
- Fonte pública nunca cria crédito, cobrança, inscrição ou notificação.

## Execução controlada

1. Confirmar `source_id` em `contracts/sources/official-catalog.yaml`.
2. Definir competência e `max_entes_per_run` / escopo territorial.
3. Respeitar `official_max_entes_hard_cap` (padrão 25) — valores acima falham fechado.
4. Garantir espaço livre em `datalake_root` ≥ `datalake_min_free_bytes` (padrão 64 MiB).
5. Executar job com `run_id`; registrar manifesto, contagens e métricas de checkpoint.
6. Partições SICONFI usam chave `exercício:período` (ou só exercício no DCA); status `COMPLETE` não reinicia sem `allow_restart`.
7. FPM mensal resolve URL por `resource_url_by_competence` quando presente.
8. Em falha de schema/licença/domínio: suspender conector.

## Proibições

- Carga nacional ilimitada sem autorização.
- Wrap silencioso de checkpoint após `COMPLETE`.
- RFB sem `territorial_scope`.
- Portal da Transparência sem credencial.
- `terraform apply` e deploy.
