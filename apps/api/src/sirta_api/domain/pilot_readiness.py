"""Technical pilot readiness checklist. G9 remains BLOCKED until institutional accept."""

PILOT_READINESS_VERSION = "pilot-readiness-technical-v1"

# Technical capacity that can be green without a municipality; institutional items stay unmet.
PILOT_TECHNICAL_CHECKLIST: tuple[dict, ...] = (
    {
        "id": "ci_reproducible",
        "label": "CI Python/web/containers reproduzível",
        "met": True,
        "category": "technical",
    },
    {
        "id": "empty_official_shells",
        "label": "Shells oficiais vazios (F5/F6/F7) com comandos desativados",
        "met": True,
        "category": "technical",
    },
    {
        "id": "gold_lineage",
        "label": "Lineage Gold por linha até URL oficial",
        "met": True,
        "category": "technical",
    },
    {
        "id": "backup_restore_local",
        "label": "Backup/restore local documentado e testável",
        "met": True,
        "category": "technical",
    },
    {
        "id": "pilot_municipality",
        "label": "Município piloto formalmente aprovado",
        "met": False,
        "category": "institutional",
    },
    {
        "id": "pilot_users",
        "label": "Usuários do piloto nomeados e treinados",
        "met": False,
        "category": "institutional",
    },
    {
        "id": "restricted_sample",
        "label": "Amostra restrita autorizada (DPA/G0/G1)",
        "met": False,
        "category": "institutional",
    },
    {
        "id": "g9_acceptances",
        "label": "Aceites técnico, administrativo, jurídico e LGPD (G9)",
        "met": False,
        "category": "institutional",
    },
)

DISCLAIMER = (
    "Checklist técnico de prontidão para piloto assistido. Capacidade local pode "
    "estar pronta; G9 permanece BLOCKED sem município, usuários e aceites "
    "institucionais. Sem território piloto inventado e sem dado municipal real."
)


def build_pilot_readiness_snapshot() -> dict:
    checklist = [dict(row) for row in PILOT_TECHNICAL_CHECKLIST]
    technical_met = all(row["met"] for row in checklist if row["category"] == "technical")
    institutional_met = all(row["met"] for row in checklist if row["category"] == "institutional")
    return {
        "version": PILOT_READINESS_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "createsTaxCredit": False,
        "pilotMunicipalityApproved": False,
        "technicalReady": technical_met,
        "institutionalReady": institutional_met,
        "g9Status": "BLOCKED",
        "g10Status": "BLOCKED",
        "checklist": checklist,
        "items": [],
        "disclaimer": DISCLAIMER,
        "homologationStatus": "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION",
    }
