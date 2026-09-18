# Decisões arquiteturais iniciais

## ADR-001 Monorepositório

Mantém contratos, dados, API, web, infraestrutura e testes sincronizados, como no CFQ.

## ADR-002 Monólito modular primeiro

Reduz complexidade operacional. Serviços só serão extraídos quando carga, segurança ou equipes justificarem.

## ADR-003 Bronze/Silver/Gold

Preserva fonte, separa normalização e estabiliza produtos analíticos.

## ADR-004 PostgreSQL mais BigQuery

PostgreSQL mantém workflow e consistência transacional; BigQuery atende análise histórica e agregações.

## ADR-005 GCP na primeira implantação

Mantém continuidade operacional com o CFQ em `southamerica-east1`; adaptadores evitam dependência irreversível.

## ADR-006 IA através de gateway privado

Centraliza autorização, DLP, auditoria, avaliação e troca de modelo.

## ADR-007 Migrações aditivas

Alterações incompatíveis exigem expandir, migrar, observar, depreciar e somente depois remover.

