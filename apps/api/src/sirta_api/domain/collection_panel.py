"""Official empty administrative collection panel. Synthetic start remains API-test only."""

COLLECTION_PANEL_VERSION = "collection-panel-technical-v1"

DISCLAIMER = (
    "Painel de cobrança administrativa oficial vazio. Comandos desativados até "
    "validação humana e gates G0/G4/G5. Fluxo sintético permanece somente em testes de API. "
    "Nenhuma cobrança, inscrição ou notificação é iniciada por este shell."
)


def build_collection_panel() -> dict:
    return {
        "version": COLLECTION_PANEL_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "sendEnabled": False,
        "createsTaxCredit": False,
        "legalCommandsEnabled": False,
        "g0Status": "BLOCKED",
        "g4Status": "BLOCKED",
        "g5Status": "BLOCKED",
        "items": [],
        "queue": [],
        "disclaimer": DISCLAIMER,
        "homologationStatus": "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION",
    }
