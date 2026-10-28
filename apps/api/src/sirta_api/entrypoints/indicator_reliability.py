from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.indicator_reliability import authorize_fiscal_use
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/indicator-reliability/{indicator_id}/fiscal-use")
def get_fiscal_use(
    indicator_id: str,
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    """Authorizes a fiscal calculation on an indicator. 409 unless the indicator is CONFERIDO."""
    context.ensure_fiscal_read()
    return authorize_fiscal_use(session, context=context, indicator_id=indicator_id)
