from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.regulatory import list_ibs_cbs_calendar
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/regulatory/ibs-cbs")
def get_ibs_cbs_calendar(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return list_ibs_cbs_calendar(session, context=context)
