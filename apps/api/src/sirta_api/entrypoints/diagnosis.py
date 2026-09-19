from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.diagnosis import get_diagnosis
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/diagnosis")
def diagnosis_endpoint(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return get_diagnosis(session, context=context)
