"""Local ops and governance readiness. G10 remains BLOCKED; no production deploy."""

OPS_GOVERNANCE_VERSION = "ops-governance-technical-v1"

OPS_RUNBOOKS: tuple[dict, ...] = (
    {
        "id": "local_dev",
        "label": "Desenvolvimento local (compose)",
        "path": "docs/operations/local-dev.md",
        "present": True,
    },
    {
        "id": "backup_restore",
        "label": "Backup e restore PostgreSQL local",
        "path": "docs/operations/backup-restore-local.md",
        "present": True,
    },
    {
        "id": "incident_response",
        "label": "Resposta a incidentes locais",
        "path": "docs/operations/incident-response-local.md",
        "present": True,
    },
    {
        "id": "ingest_ops",
        "label": "Operação de ingestão PUBLIC_OPEN",
        "path": "docs/operations/ingest-ops-local.md",
        "present": True,
    },
    {
        "id": "gates_governance",
        "label": "Governança de gates sem fabricar aprovação",
        "path": "docs/operations/gates-governance-local.md",
        "present": True,
    },
)

DISCLAIMER = (
    "Governança operacional técnica local. Runbooks documentados; G10 permanece "
    "BLOCKED. Sem terraform apply, sem deploy em nuvem e sem fabricar aprovação humana."
)


def build_ops_governance_snapshot() -> dict:
    runbooks = [dict(row) for row in OPS_RUNBOOKS]
    return {
        "version": OPS_GOVERNANCE_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "canDeploy": False,
        "canApprove": False,
        "humanApprovalFabricated": False,
        "terraformApplyAuthorized": False,
        "cloudAccess": "BLOCKED_UNTIL_EXPLICIT_AUTHORIZATION",
        "g10Status": "BLOCKED",
        "runbooks": runbooks,
        "runbooksComplete": all(row["present"] for row in runbooks),
        "items": [],
        "disclaimer": DISCLAIMER,
        "homologationStatus": "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION",
    }
