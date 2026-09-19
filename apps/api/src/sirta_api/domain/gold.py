from sirta_api.domain.catalog import HOMOLOGATION_PENDING

VALUE_KINDS = frozenset(
    {
        "REFERENCE_QUANTITY",
        "CATALOG_METADATA",
        "COVERAGE_REGISTRY",
        "TRANSFER_AMOUNT_AS_PUBLISHED",
        "FISCAL_STATEMENT_LINE",
        "REGULATORY_DOCUMENT",
    }
)

PRESENTATION = {
    "IBGE-SIDRA": {
        "valueKind": "REFERENCE_QUANTITY",
        "label": (
            "População estimada publicada pelo IBGE. Não é crédito tributário nem transferência."
        ),
    },
    "IBGE-SIDRA-PIB": {
        "valueKind": "REFERENCE_QUANTITY",
        "label": (
            "PIB municipal publicado pelo IBGE. Não é crédito tributário nem potencial de ISS."
        ),
    },
    "SICONFI-ENTES": {
        "valueKind": "COVERAGE_REGISTRY",
        "label": "Cadastro de entes do SICONFI. Não é demonstrativo fiscal (RREO/DCA).",
    },
    "TESOURO-TRANSPARENTE": {
        "valueKind": "CATALOG_METADATA",
        "label": "Dicionário de tipos de transferência. FPM código 3 não é valor transferido.",
    },
    "TESOURO-FPM-VALORES": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Valores de FPM publicados pelo Tesouro. "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-ICMS-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de ICMS estadual publicada (PE ativado). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "ESTADO-IPVA-QUOTA": {
        "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
        "label": (
            "Quota-parte de IPVA estadual publicada (PE ativado; zero é valor oficial). "
            "Ocorrência para análise, não crédito nem cobrança."
        ),
    },
    "SICONFI-RREO": {
        "valueKind": "FISCAL_STATEMENT_LINE",
        "label": "Linhas do RREO municipal. Não constituem crédito tributário.",
    },
    "SICONFI-DCA": {
        "valueKind": "FISCAL_STATEMENT_LINE",
        "label": "Linhas do DCA/FINBRA. Não constituem crédito tributário.",
    },
    "SICONFI-RGF": {
        "valueKind": "FISCAL_STATEMENT_LINE",
        "label": "Linhas do RGF municipal. Não constituem crédito tributário.",
    },
    "PLANALTO-LEGISLACAO": {
        "valueKind": "REGULATORY_DOCUMENT",
        "label": "Documento regulatório. binding=false, operational=false, homologated=false.",
    },
    "PLANALTO-LC-214": {
        "valueKind": "REGULATORY_DOCUMENT",
        "label": (
            "Lei Complementar 214/2025 preservada. "
            "binding=false, operational=false, homologated=false."
        ),
    },
}


def presentation_for(source_id: str) -> dict:
    base = PRESENTATION.get(
        source_id,
        {
            "valueKind": "REFERENCE_QUANTITY",
            "label": "Dado oficial de referência. Não é crédito tributário.",
        },
    )
    financial = base["valueKind"] in {"TRANSFER_AMOUNT_AS_PUBLISHED", "FISCAL_STATEMENT_LINE"}
    return {
        **base,
        "createsTaxCredit": False,
        "createsCollection": False,
        "financial": financial,
        "homologationStatus": HOMOLOGATION_PENDING,
        "isFinancialTransferValue": base["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED",
        "isFiscalStatement": base["valueKind"] == "FISCAL_STATEMENT_LINE",
        "isCatalogMetadata": base["valueKind"] == "CATALOG_METADATA",
        "isCoverageRegistry": base["valueKind"] == "COVERAGE_REGISTRY",
    }


def assert_gold_lineage_complete(line: dict) -> None:
    required = (
        "silverRowId",
        "bronzeSha256",
        "landingManifestPath",
        "officialUrl",
        "checksumSha256",
    )
    missing = [key for key in required if not line.get(key)]
    if missing:
        raise ValueError(f"Gold line is missing lineage fields: {missing}")
    if line.get("layer") == "quarantine":
        raise ValueError("Quarantined records cannot be published as Gold")


def coverage_divergence(items: list[dict]) -> dict | None:
    by_source = {item.get("sourceId"): item.get("coverageCount") for item in items}
    ibge = by_source.get("IBGE-SIDRA")
    siconfi = by_source.get("SICONFI-ENTES")
    pib = by_source.get("IBGE-SIDRA-PIB")
    if ibge is None or siconfi is None:
        return None
    if ibge == siconfi and (pib is None or pib == ibge):
        return None
    explanation = (
        "A cobertura municipal difere entre IBGE 6579, SICONFI/entes e IBGE 5938. "
        "A diferença 5.571 versus 5.570 é cobertura pendente de homologação, "
        "não ocorrência administrativa nem crédito tributário."
    )
    return {
        "sourceId": "COVERAGE-DIVERGENCE",
        "indicator": "municipal_coverage_divergence",
        "maintainer": "SIRTA",
        "dataset": "COVERAGE-CHECK",
        "competence": "as_published",
        "lastExtractedAt": "",
        "formula": (
            "Contagem de municípios na série IBGE 6579 versus entes municipais SICONFI "
            "versus municípios da série IBGE 5938."
        ),
        "methodologyVersion": "coverage-divergence-v1",
        "coverageCount": abs(int(ibge or 0) - int(siconfi or 0)),
        "qualityLevel": "COVERAGE_DIVERGENCE_PENDING_HUMAN_VALIDATION",
        "homologationStatus": HOMOLOGATION_PENDING,
        "officialUrl": "https://sidra.ibge.gov.br/tabela/6579",
        "lineage": {"status": "COVERAGE_DIVERGENCE_PENDING_HUMAN_VALIDATION"},
        "quarantinedCount": 0,
        "numericTotal": None,
        "createsTaxCredit": False,
        "valueKind": "COVERAGE_REGISTRY",
        "financial": False,
        "presentation": explanation,
        "ibgePopulationMunicipalities": ibge,
        "siconfiMunicipalEntes": siconfi,
        "ibgePibMunicipalities": pib,
        "status": "COVERAGE_DIVERGENCE_PENDING_HUMAN_VALIDATION",
        "explanation": explanation,
    }
