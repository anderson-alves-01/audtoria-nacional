"""Non-binding audit rule catalog. Potential never becomes tax credit."""

from dataclasses import dataclass

STATUS_NON_BINDING = "NON_BINDING"
AUDIT_RULES_VERSION = "audit-rules-synthetic-v1"

DISCLAIMER = (
    "Catálogo técnico de regras não vinculantes. Nenhuma regra constitui crédito, "
    "potencial em reais ou cobrança. Homologação especialista (G4) ausente."
)


@dataclass(frozen=True)
class AuditRuleItem:
    code: str
    title: str
    domain: str
    notes: str


AUDIT_RULES_CATALOG: tuple[AuditRuleItem, ...] = (
    AuditRuleItem(
        code="ISS-CADASTRO-CROSSCHECK-PLACEHOLDER",
        title="Cruzamento cadastral ISS — placeholder não executável",
        domain="iss",
        notes="Regra técnica vazia. Sem fórmula de potencial e sem execução automática.",
    ),
    AuditRuleItem(
        code="DUPLICATE-CREDIT-DETECT-PLACEHOLDER",
        title="Detecção de duplicidade — placeholder não vinculante",
        domain="credit-quality",
        notes="Não marca crédito como exigível. Requer homologação G4.",
    ),
)


def build_audit_rules_catalog() -> dict:
    return {
        "catalogVersion": AUDIT_RULES_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "createsTaxCredit": False,
        "taxPotentialAsCredit": False,
        "disclaimer": DISCLAIMER,
        "homologationStatus": "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION",
        "items": [
            {
                "code": item.code,
                "title": item.title,
                "domain": item.domain,
                "status": STATUS_NON_BINDING,
                "binding": False,
                "operational": False,
                "createsTaxCredit": False,
                "taxPotentialAsCredit": False,
                "notes": item.notes,
            }
            for item in AUDIT_RULES_CATALOG
        ],
    }
