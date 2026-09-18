from uuid import uuid4

from sirta_api.domain.checklist import CHECKLIST_VERSION, required_item_codes
from sirta_api.domain.credit import Decision


def complete_checklist_items() -> list[dict[str, bool | str]]:
    return [{"code": code, "satisfied": True} for code in required_item_codes()]


def validation_payload(
    *,
    decision: str = Decision.APPROVE.value,
    evidence_ids: list[str],
    complete: bool = True,
) -> dict:
    return {
        "decision": decision,
        "checklistVersion": CHECKLIST_VERSION,
        "evidenceIds": evidence_ids,
        "rationale": "Synthetic validation decision for local tests only.",
        "checklistItems": complete_checklist_items()
        if complete
        else [{"code": "ORIGIN_IDENTIFIED", "satisfied": False}],
    }


def idempotency_headers(base: dict[str, str], key: str | None = None) -> dict[str, str]:
    headers = dict(base)
    headers["Idempotency-Key"] = key or f"idem-{uuid4().hex}"
    return headers
