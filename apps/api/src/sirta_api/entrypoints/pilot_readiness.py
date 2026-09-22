from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.pilot_readiness import get_pilot_readiness
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/pilot-readiness")
def pilot_readiness_endpoint(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return get_pilot_readiness(session, context=context)
