from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.human_validation import get_human_validation
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/human-validation")
def human_validation_endpoint(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return get_human_validation(session, context=context)
