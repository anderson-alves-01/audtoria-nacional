"""RFB CNPJ open-data territorial scope, resume and EI minimization.

No national load. Ingest remains blocked while territorial_scope is none.
Individual entrepreneurs never reach Gold.
"""

from __future__ import annotations

from dataclasses import dataclass

from sirta_api.domain.errors import ForbiddenError

RFB_CONNECTOR = "rfb_cnpj_open"
RFB_SOURCE_ID = "RFB-DADOS-ABERTOS"
RFB_LAYOUT_VERSION = "rfb-cnpj-zip-v1"
RFB_METHODOLOGY = "rfb-cnpj-minimization-v1"

# Natureza jurídica 213-5 — Empresário Individual (layout RFB).
INDIVIDUAL_ENTREPRENEUR_NATURE_CODES = frozenset({"2135", "213-5", "213"})

ESTABELECIMENTO_FILES = tuple(f"Estabelecimentos{index}.zip" for index in range(10))


@dataclass(frozen=True)
class TerritorialScope:
    ufs: frozenset[str]
    ibge_codes: frozenset[str]
    rfb_municipio_codes: frozenset[str]

    @property
    def is_ready(self) -> bool:
        return bool(self.ufs) or bool(self.ibge_codes) or bool(self.rfb_municipio_codes)


@dataclass(frozen=True)
class ResumeCursor:
    file_name: str
    byte_offset: int

    def encode(self) -> str:
        return f"{self.file_name}:{self.byte_offset}"

    @classmethod
    def decode(cls, raw: str | None) -> ResumeCursor | None:
        if not raw or ":" not in raw:
            return None
        name, offset = raw.rsplit(":", 1)
        if not offset.isdigit():
            return None
        return cls(file_name=name, byte_offset=int(offset))


def parse_territorial_scope(parameters: dict | None) -> TerritorialScope | None:
    params = parameters or {}
    raw = params.get("territorial_scope")
    if raw in (None, "", "none", "null"):
        return None
    if isinstance(raw, str):
        raw = {"ufs": [part.strip().upper() for part in raw.split(",") if part.strip()]}
    if not isinstance(raw, dict):
        return None
    ufs = frozenset(
        str(item).strip().upper() for item in (raw.get("ufs") or []) if str(item).strip()
    )
    ibge = frozenset(
        str(item).strip() for item in (raw.get("ibge_codes") or []) if str(item).strip()
    )
    rfb_codes = frozenset(
        str(item).strip() for item in (raw.get("rfb_municipio_codes") or []) if str(item).strip()
    )
    scope = TerritorialScope(ufs=ufs, ibge_codes=ibge, rfb_municipio_codes=rfb_codes)
    return scope if scope.is_ready else None


def assert_territorial_scope_ready(parameters: dict | None) -> TerritorialScope:
    scope = parse_territorial_scope(parameters)
    if scope is None:
        raise ForbiddenError(
            "RFB CNPJ requires territorial_scope (UF and/or municipality codes); "
            "national and arbitrary sample loads are refused"
        )
    return scope


def is_individual_entrepreneur(natureza_codigo: str | None) -> bool:
    if natureza_codigo is None:
        return False
    normalized = str(natureza_codigo).strip().replace(" ", "")
    return normalized in INDIVIDUAL_ENTREPRENEUR_NATURE_CODES


def ei_policy_decision(
    *,
    natureza_codigo: str | None,
    minimize_individual_entrepreneur: bool = True,
) -> str | None:
    """Return quarantine reason when the row must not reach Gold."""
    if not minimize_individual_entrepreneur:
        return None
    if natureza_codigo in (None, ""):
        return "missing_nature_for_ei_policy"
    if is_individual_entrepreneur(natureza_codigo):
        return "individual_entrepreneur_excluded"
    return None


def next_resume_plan(
    *,
    cursor: ResumeCursor | None = None,
    files: tuple[str, ...] = ESTABELECIMENTO_FILES,
) -> ResumeCursor:
    if cursor is None:
        return ResumeCursor(file_name=files[0], byte_offset=0)
    if cursor.file_name not in files:
        return ResumeCursor(file_name=files[0], byte_offset=0)
    return cursor


def build_rfb_landing_manifest(
    *,
    source_id: str,
    official_url: str,
    resolved_url: str,
    checksum: str,
    byte_count: int,
    scope: TerritorialScope,
    resume: ResumeCursor,
    received_count: int,
    silver_count: int,
    quarantined_count: int,
) -> dict:
    return {
        "sourceId": source_id,
        "officialUrl": official_url,
        "resolvedUrl": resolved_url,
        "sha256": checksum,
        "bytes": byte_count,
        "layoutVersion": RFB_LAYOUT_VERSION,
        "methodologyVersion": RFB_METHODOLOGY,
        "territorialScope": {
            "ufs": sorted(scope.ufs),
            "ibgeCodes": sorted(scope.ibge_codes),
            "rfbMunicipioCodes": sorted(scope.rfb_municipio_codes),
        },
        "resumeCursor": resume.encode(),
        "receivedCount": received_count,
        "silverCount": silver_count,
        "quarantinedCount": quarantined_count,
        "createsTaxCredit": False,
        "nationalLoad": False,
        "individualEntrepreneurInGold": False,
    }


def build_rfb_readiness(parameters: dict | None = None) -> dict:
    scope = parse_territorial_scope(parameters)
    return {
        "sourceId": RFB_SOURCE_ID,
        "connector": RFB_CONNECTOR,
        "layoutVersion": RFB_LAYOUT_VERSION,
        "scopeReady": scope is not None,
        "territorialScope": (
            {
                "ufs": sorted(scope.ufs),
                "ibgeCodes": sorted(scope.ibge_codes),
                "rfbMunicipioCodes": sorted(scope.rfb_municipio_codes),
            }
            if scope
            else None
        ),
        "resumeCapable": True,
        "streaming": True,
        "eiPolicy": "exclude_from_gold",
        "ingestAllowed": False,
        "nationalLoadAllowed": False,
        "createsTaxCredit": False,
        "status": "READY_FOR_TERRITORIAL_SCOPE",
    }
