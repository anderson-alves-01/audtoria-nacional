"""Sectoral REFERENCE_ENRICHMENT empty shell. No tax credit; ingest not activated."""

from sirta_api.domain.errors import ConflictError

SECTORAL_ENRICHMENT_VERSION = "sectoral-enrichment-technical-v1"

SECTORAL_SOURCES: tuple[dict, ...] = (
    {
        "sourceId": "ANP-REVENDEDORES",
        "maintainer": "ANP",
        "connector": "anp_revendedores_api",
        "structuredOfficialSource": "rest_api_verified",
        "status": "DISCOVERED",
        "ingestAllowed": False,
        "personalDataRisk": "possible_establishment_cnpj_minimized",
        "activationGate": "TECHNICALLY_APPROVED_WITH_FIXTURE",
    },
    {
        "sourceId": "ANEEL-DADOS-ABERTOS",
        "maintainer": "ANEEL",
        "connector": "aneel_ckan_open",
        "structuredOfficialSource": "ckan_api_verified",
        "status": "DISCOVERED",
        "ingestAllowed": False,
        "personalDataRisk": "none",
        "activationGate": "TECHNICALLY_APPROVED_WITH_FIXTURE",
    },
    {
        "sourceId": "EPE-DADOS-ABERTOS",
        "maintainer": "EPE",
        "connector": "epe_open_files",
        "structuredOfficialSource": "tabular_download_portal",
        "status": "DISCOVERED",
        "ingestAllowed": False,
        "personalDataRisk": "none",
        "activationGate": "STABLE_FILE_URL",
    },
    {
        "sourceId": "ANATEL-DADOS-ABERTOS",
        "maintainer": "Anatel",
        "connector": "anatel_dados_gov",
        "structuredOfficialSource": "dados_gov_zip_odt",
        "status": "DISCOVERED",
        "ingestAllowed": False,
        "personalDataRisk": "none",
        "activationGate": "STRUCTURED_CSV_VERIFIED",
    },
    {
        "sourceId": "BCB-SGS-OLINDA",
        "maintainer": "Banco Central",
        "connector": "bcb_sgs_olinda",
        "structuredOfficialSource": "sgs_json_and_olinda_odata",
        "status": "DISCOVERED",
        "ingestAllowed": False,
        "personalDataRisk": "none",
        "activationGate": "SERIES_ALLOWLIST",
    },
    {
        "sourceId": "CNES-DATASUS",
        "maintainer": "Ministério da Saúde / DATASUS",
        "connector": "cnes_datasus_open",
        "structuredOfficialSource": "open_data_portal_and_competence_files",
        "status": "DISCOVERED",
        "ingestAllowed": False,
        "personalDataRisk": "possible_professional_contact_minimized",
        "activationGate": "TERRITORIAL_SCOPE",
    },
)

DISCLAIMER = (
    "Fontes setoriais oficiais catalogadas (ANP, ANEEL, EPE, Anatel, BCB, CNES). "
    "Estado vazio; ingestAllowed=false; REFERENCE_ENRICHMENT apenas. "
    "Nenhuma carga ativada nesta fatia. Não constitui crédito tributário."
)

BLOCKED_SECTORAL_CONNECTORS = frozenset(
    {
        "anp_revendedores_api",
        "aneel_ckan_open",
        "epe_open_files",
        "anatel_dados_gov",
        "bcb_sgs_olinda",
        "cnes_datasus_open",
    }
)


def build_sectoral_enrichment_panel(*, page: int = 1, size: int = 20) -> dict:
    sources = [dict(row) for row in SECTORAL_SOURCES]
    return {
        "version": SECTORAL_ENRICHMENT_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "createsTaxCredit": False,
        "ingestEnabled": False,
        "sourceRole": "REFERENCE_ENRICHMENT",
        "institutionalStatus": "DISCOVERED",
        "sources": sources,
        "items": [],
        "page": page,
        "size": size,
        "total": 0,
        "disclaimer": DISCLAIMER,
        "homologationStatus": "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION",
    }


def reject_sectoral_enrichment_command() -> None:
    raise ConflictError(
        "Enriquecimento setorial desativado até ativação técnica por fonte. "
        "Shell vazio; sem carga e sem constituição de crédito."
    )
