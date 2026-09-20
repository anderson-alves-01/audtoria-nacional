"""State ICMS/IPVA catalog shell. No tax credit; PE/BA/MG/ES/GO/MS/RO/AC/CE/RS gated."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from sirta_api.domain.errors import ConflictError

STATE_TRANSFERS_VERSION = "state-transfers-technical-v1"
STATE_CATALOG_RELATIVE = Path("contracts/sources/state-transfers-catalog.yaml")

DISCLAIMER = (
    "Catálogo estadual ICMS/IPVA. PE, BA, MG, ES, GO, MS, RO, AC, CE, RS, AL, PI, RN e MA "
    "ativados com fonte PUBLIC_OPEN (MG/ES/AL IBGE7 nativo; RO IPVA IBGE6→7; GO/MS DataStore; "
    "RO/AC CSV; CE/RS/AL/RN/MA XLS; PI Repasse WEB HTML). Demais UFs só avançam com fonte "
    "estruturada comprovada; portais HTML e agregadores privados são recusados. Diferença "
    "gera ocorrência, nunca crédito."
)


def _state_catalog_path() -> Path:
    here = Path(__file__).resolve()
    for parent in [Path.cwd(), *here.parents]:
        candidate = parent / STATE_CATALOG_RELATIVE
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("state transfers catalog is missing")


@lru_cache(maxsize=1)
def load_state_transfers_catalog() -> dict:
    return yaml.safe_load(_state_catalog_path().read_text(encoding="utf-8"))


def build_state_transfers_panel(*, page: int = 1, size: int = 30) -> dict:
    catalog = load_state_transfers_catalog()
    states = []
    for row in catalog.get("states") or []:
        status = row.get("status") or "DISCOVERED"
        ingest_allowed = bool(row.get("ingest_allowed")) and status == "TECHNICALLY_APPROVED"
        taxes = list(row.get("taxes") or catalog.get("taxes") or ["ICMS", "IPVA"])
        states.append(
            {
                "uf": row["uf"],
                "name": row["name"],
                "status": status,
                "structuredOfficialSource": row.get("structured_official_source"),
                "taxes": taxes,
                "ingestAllowed": ingest_allowed,
                "officialUrl": row.get("official_url"),
                "datasetUrl": row.get("dataset_url"),
                "reason": row.get("reason"),
            }
        )
    verified = [
        row for row in states if row["status"] in {"PROVENANCE_VERIFIED", "TECHNICALLY_APPROVED"}
    ]
    ingest_enabled = any(row["ingestAllowed"] for row in states)
    return {
        "version": STATE_TRANSFERS_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "createsTaxCredit": False,
        "ingestEnabled": ingest_enabled,
        "normalize": catalog.get("normalize") or "ibge7",
        "taxes": list(catalog.get("taxes") or ["ICMS", "IPVA"]),
        "institutionalStatus": "TECHNICALLY_APPROVED" if ingest_enabled else "DISCOVERED",
        "verifiedCount": len(verified),
        "states": states,
        "items": [],
        "page": page,
        "size": size,
        "total": 0,
        "disclaimer": DISCLAIMER,
        "homologationStatus": "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION",
        "notes": catalog.get("notes"),
    }


def reject_state_transfers_command() -> None:
    raise ConflictError(
        "Comando agregado de transferências estaduais desativado. Use ingestão "
        "catalogada por fonte (PE/BA/MG/ES/GO/MS/RO/AC/CE) quando "
        "TECHNICALLY_APPROVED; sem crédito."
    )
