from fastapi import APIRouter, Depends

from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.indicator_reliability import (
    ensure_fiscal_use,
    indicator_view,
    load_registry,
)
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/indicator-reliability/{indicator_id}/fiscal-use")
def get_fiscal_use(
    indicator_id: str,
    context: AccessContext = Depends(get_access_context),
) -> dict:
    """Authorizes a fiscal calculation on an indicator. 409 unless the indicator is CONFERIDO."""
    context.ensure_fiscal_read()
    registry = load_registry()
    ensure_fiscal_use(indicator_id, registry)
    return indicator_view(indicator_id, registry)
