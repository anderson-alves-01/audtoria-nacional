"""Cadastro 360 technical empty shell. No real PII and no invented territory."""

from sirta_api.adapters.ingest.catalog_loader import catalog_source
from sirta_api.domain.errors import ConflictError
from sirta_api.domain.rfb_cnpj import build_rfb_readiness

CADASTRO_360_VERSION = "cadastro-360-technical-v1"

MINIMIZATION_POLICY: tuple[dict, ...] = (
    {
        "field": "cpf_cnpj",
        "policy": "MASKED_OR_ABSENT",
        "present": False,
    },
    {
        "field": "nome_razao_social",
        "policy": "ABSENT_UNTIL_AUTHORIZED",
        "present": False,
    },
    {
        "field": "endereco",
        "policy": "ABSENT_UNTIL_AUTHORIZED",
        "present": False,
    },
    {
        "field": "contato",
        "policy": "ABSENT_UNTIL_AUTHORIZED",
        "present": False,
    },
)

DISCLAIMER = (
    "Cadastro 360 técnico vazio. Sem PII real, sem território inventado e sem "
    "cruzamento RFB/municipal até escopo territorial e CREDENTIAL_REQUIRED. "
    "Minimização obrigatória; G0 permanece BLOCKED."
)


def build_cadastro_360_panel(*, page: int = 1, size: int = 20) -> dict:
    rfb_catalog = catalog_source("RFB-DADOS-ABERTOS") or {}
    rfb = build_rfb_readiness(rfb_catalog.get("parameters"))
    return {
        "version": CADASTRO_360_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "createsTaxCredit": False,
        "piiPresent": False,
        "territoryInvented": False,
        "minimizationEnforced": True,
        "rfbScopeReady": bool(rfb.get("scopeReady")),
        "rfbResumeCapable": bool(rfb.get("resumeCapable")),
        "rfbEiPolicy": rfb.get("eiPolicy"),
        "municipalDataLinked": False,
        "g0Status": "BLOCKED",
        "institutionalStatus": "CREDENTIAL_REQUIRED",
        "minimizationPolicy": [dict(row) for row in MINIMIZATION_POLICY],
        "subjects": [],
        "items": [],
        "page": page,
        "size": size,
        "total": 0,
        "disclaimer": DISCLAIMER,
        "homologationStatus": "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION",
    }


def reject_cadastro_360_command() -> None:
    raise ConflictError(
        "Comando de Cadastro 360 desativado até escopo territorial, DPA e G0. "
        "Shell técnico sem PII e sem território inventado."
    )
