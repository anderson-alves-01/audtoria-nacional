"""Technical municipal diagnosis shell. Never invents recovery targets."""

from sirta_api.domain.gates import G1_CHECKLIST

DIAGNOSIS_VERSION = "diagnosis-technical-v1"

# Technical checklist mirrored from checklists/MUNICIPAL-DIAGNOSIS.md.
# All items remain unmet until institutional G1 homologation.
DIAGNOSIS_CHECKLIST: tuple[dict, ...] = (
    {"id": "sponsor_governance", "label": "Patrocinador e grupo gestor definidos", "met": False},
    {"id": "tax_inventory", "label": "Tributos e receitas inventariados", "met": False},
    {"id": "systems_map", "label": "Sistemas e fornecedores mapeados", "met": False},
    {"id": "data_stewards", "label": "Responsáveis por cada base identificados", "met": False},
    {
        "id": "formats_volumes",
        "label": "Formatos, volumes, competências e periodicidade registrados",
        "met": False,
    },
    {"id": "quality_sample", "label": "Qualidade e completude amostradas", "met": False},
    {
        "id": "portfolio_quantified",
        "label": "Carteira e dívida ativa quantificadas sem prometer recuperação",
        "met": False,
    },
    {"id": "collection_flows", "label": "Fluxos atuais de cobrança documentados", "met": False},
    {"id": "installments_map", "label": "Parcelamentos e pagamentos mapeados", "met": False},
    {
        "id": "legal_interviews",
        "label": "Procuradoria e controle interno entrevistados",
        "met": False,
    },
    {"id": "transfers_priority", "label": "Transferências prioritárias definidas", "met": False},
    {"id": "ibs_cbs_impacts", "label": "Impactos IBS/CBS levantados", "met": False},
    {"id": "legal_basis", "label": "Base legal, finalidade e retenção avaliadas", "met": False},
    {"id": "security_review", "label": "Infraestrutura e segurança avaliadas", "met": False},
    {"id": "pilot_portfolio", "label": "Carteira piloto aprovada", "met": False},
    {"id": "baseline_homologated", "label": "Baseline de indicadores homologado", "met": False},
)

DISCLAIMER = (
    "Diagnóstico técnico vazio. Sem meta de recuperação, sem percentual prometido "
    "e sem amostra municipal real. G1 permanece BLOCKED até homologação institucional."
)


def build_diagnosis_snapshot() -> dict:
    return {
        "version": DIAGNOSIS_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "createsTaxCredit": False,
        "recoveryMeta": None,
        "g1Status": "BLOCKED",
        "g1Checklist": [dict(row) for row in G1_CHECKLIST],
        "checklist": [dict(row) for row in DIAGNOSIS_CHECKLIST],
        "items": [],
        "disclaimer": DISCLAIMER,
        "homologationStatus": "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION",
    }
