"""State ICMS/IPVA transfer catalog shell. No tax credit; ingest gated per UF."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from sirta_api.domain.errors import ConflictError

STATE_TRANSFERS_VERSION = "state-transfers-technical-v1"
STATE_CATALOG_RELATIVE = Path("contracts/sources/state-transfers-catalog.yaml")

DISCLAIMER = (
    "Catálogo estadual ICMS/IPVA. Somente UF com fonte PUBLIC_OPEN estruturada "
    "comprovada pode avançar; portais HTML e agregadores privados são recusados. "
    "Estado vazio; ingestAllowed=false; diferença gera ocorrência, nunca crédito."
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
        states.append(
            {
                "uf": row["uf"],
                "name": row["name"],
                "status": row.get("status") or "DISCOVERED",
                "structuredOfficialSource": row.get("structured_official_source"),
                "taxes": list(catalog.get("taxes") or ["ICMS", "IPVA"]),
                "ingestAllowed": False,
                "officialUrl": row.get("official_url"),
                "datasetUrl": row.get("dataset_url"),
                "reason": row.get("reason"),
            }
        )
    verified = [row for row in states if row["status"] == "PROVENANCE_VERIFIED"]
    return {
        "version": STATE_TRANSFERS_VERSION,
        "binding": False,
        "operational": False,
        "homologated": False,
        "commandsDisabled": True,
        "createsTaxCredit": False,
        "ingestEnabled": False,
        "normalize": catalog.get("normalize") or "ibge7",
        "taxes": list(catalog.get("taxes") or ["ICMS", "IPVA"]),
        "institutionalStatus": "DISCOVERED",
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
        "Transferências estaduais ICMS/IPVA desativadas até ativação por UF com "
        "arquivo/API estruturado comprovado e schema verificado. Shell vazio; sem crédito."
    )
