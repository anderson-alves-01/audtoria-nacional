"""Official empty transfer reconciliation shell. Differences are never tax credits."""

from sirta_api.domain.errors import ConflictError

TRANSFER_RECONCILIATION_VERSION = "transfer-reconciliation-technical-v1"

DISCLAIMER = (
    "Conciliação técnica de transferências vazia. Compara previsto versus realizado "
    "somente quando ambos existirem em fontes oficiais. Diferença gera ocorrência, "
    "nunca crédito tributário, cobrança ou inscrição. G7 oficial permanece BLOCKED."
)


def build_transfer_reconciliation_panel(*, page: int = 1, size: int = 20) -> dict:
    return {
        "version": TRANSFER_RECONCILIATION_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "autoReconcileEnabled": False,
        "createsTaxCredit": False,
        "differenceIsOccurrenceOnly": True,
        "legalCommandsEnabled": False,
        "g0Status": "BLOCKED",
        "g7Status": "LOCAL_GO_OFFICIAL_BLOCKED",
        "compareOnlyWhenBothExist": True,
        "expectedSources": [],
        "receivedSources": [],
        "items": [],
        "differences": [],
        "page": page,
        "size": size,
        "total": 0,
        "disclaimer": DISCLAIMER,
        "homologationStatus": "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION",
    }


def reject_reconciliation_command() -> None:
    raise ConflictError(
        "Comando de conciliação de transferências desativado até fontes oficiais "
        "homologadas (G7 oficial). Shell técnico vazio; diferença nunca constitui crédito."
    )
